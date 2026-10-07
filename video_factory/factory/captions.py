"""Animated word-by-word captions + motion graphics, all rendered through ASS/libass.

One .ass file per deliverable carries:
  * captions        — grouped words, active word pops + colours, emphasis words colour-coded
  * hook title      — kinetic title card over the first seconds
  * lower third     — animated name/role card
  * keyword popups  — cards + animated arrow on the strongest moments
  * end card / CTA
libass + fribidi handle Hebrew right-to-left shaping automatically (Encoding -1).
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import resolve_color
from .language import norm
from .transcribe import is_hebrew


# --------------------------------------------------------------------------- helpers
def ass_color(hex_rgb: str, alpha: float = 0.0) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{int(alpha * 255):02X}{b}{g}{r}&".upper()


def ts(t: float) -> str:
    t = max(t, 0.0)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


@dataclass
class CapWord:
    text: str
    s: float          # output-timeline seconds
    e: float
    emphasis: float = 0.0


def group_words(words: list[CapWord], per_line: int, max_chars: int, max_gap: float = 0.6) -> list[list[CapWord]]:
    groups, cur = [], []
    for w in words:
        chars = sum(len(x.text) + 1 for x in cur) + len(w.text)
        brk = cur and (len(cur) >= per_line or chars > max_chars or w.s - cur[-1].e > max_gap
                       or cur[-1].text.endswith((".", "?", "!", ",")))
        if brk:
            groups.append(cur)
            cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


# --------------------------------------------------------------------------- builder
class AssBuilder:
    def __init__(self, cfg: dict, width: int, height: int, kind: str):
        self.cfg, self.W, self.H, self.kind = cfg, width, height, kind
        self.events: list[str] = []
        st = cfg["_caption_styles"][cfg["captions"]["style"]]
        self.st = st
        self.font = resolve_color(cfg, st["font"])
        self.size = int(height * st["size_youtube" if kind == "youtube" else "size_vertical"])
        self.c_base = ass_color(resolve_color(cfg, st["base_color"]))
        self.c_active = ass_color(resolve_color(cfg, st["active_color"]))
        self.c_emph = ass_color(resolve_color(cfg, st["emphasis_color"]))
        self.c_out = ass_color(cfg["brand"]["outline"])
        self.c_primary = ass_color(cfg["brand"]["primary"])
        self.c_accent = ass_color(cfg["brand"]["accent"])
        self.c_text = ass_color(cfg["brand"]["text"])

    def header(self) -> str:
        st = self.st
        box = st.get("box")
        border = 3 if box else 1
        back = ass_color(st.get("box_color", "#000000"), 1 - st.get("box_alpha", 0.5)) if box else "&H80000000&"
        outline = 18 if box else st["outline"]
        f = self.font
        lt = int(self.H * (0.034 if self.kind != "youtube" else 0.04))
        return "\n".join([
            "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {self.W}", f"PlayResY: {self.H}",
            "WrapStyle: 2", "ScaledBorderAndShadow: yes", "YCbCr Matrix: TV.709", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
            "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            f"Style: Cap,{f},{self.size},{self.c_base},{self.c_base},{self.c_out if not box else back},"
            f"{back},{-1 if st['bold'] else 0},0,0,0,100,100,0,0,{border},{outline},{st['shadow']},5,40,40,40,-1",
            f"Style: Title,{f},{int(self.size*1.25)},{self.c_text},{self.c_text},{self.c_out},&H64000000&,"
            f"-1,0,0,0,100,100,0,0,1,{max(6, st['outline'])},4,5,60,60,40,-1",
            f"Style: Hook,{f},{int(self.size*1.05)},&H00000000&,&H00000000&,{self.c_primary},{self.c_primary},"
            f"-1,0,0,0,100,100,0,0,3,{max(10, int(self.size*0.28))},0,8,{int(self.W*0.08)},{int(self.W*0.08)},40,-1",
            f"Style: Pop,{f},{int(self.size*1.0)},{self.c_text},{self.c_text},{self.c_accent},{self.c_accent},"
            f"-1,0,0,0,100,100,0,0,3,{max(8, int(self.size*0.22))},0,5,40,40,40,-1",
            f"Style: Card,{f},{lt},{self.c_text},{self.c_text},&H00000000&,&H00000000&,-1,0,0,0,100,100,0,0,1,0,0,5,20,20,20,-1",
            f"Style: Shape,{f},20,{self.c_primary},{self.c_primary},&H00000000&,&H00000000&,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,-1",
            "", "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]) + "\n"

    def add(self, layer: int, s: float, e: float, style: str, text: str):
        if e - s < 0.02:
            return
        self.events.append(f"Dialogue: {layer},{ts(s)},{ts(e)},{style},,0,0,0,,{text}")

    # ----------------------------------------------------------------- captions
    def captions(self, words: list[CapWord], y_frac: float):
        st = self.st
        per = st["words_per_line"] if self.cfg["captions"]["words_per_line"] == "auto" \
            else int(self.cfg["captions"]["words_per_line"])
        groups = group_words(words, per, self.cfg["captions"]["max_chars"])
        x, y = self.W // 2, int(self.H * y_frac)
        upper = st.get("uppercase") and self.cfg["captions"]["uppercase_latin"]
        pop, pop_ms = st["pop_scale"], st["pop_ms"]
        for gi, g in enumerate(groups):
            g_end = g[-1].e + 0.12
            if gi + 1 < len(groups):
                g_end = min(g_end, groups[gi + 1][0].s)
            for k, w in enumerate(g):
                s = w.s
                e = g[k + 1].s if k + 1 < len(g) else g_end
                parts = []
                for j, o in enumerate(g):
                    raw = o.text.rstrip(".,;:…") or o.text
                    txt = esc(raw.upper() if upper and not is_hebrew(raw) else raw)
                    col = self.c_emph if o.emphasis >= 0.6 else self.c_base
                    if j == k:
                        col = self.c_emph if o.emphasis >= 0.6 else self.c_active
                        big = pop + (12 if o.emphasis >= 0.6 else 0)
                        parts.append(f"{{\\c{col}\\fscx{big}\\fscy{big}\\t(0,{pop_ms},\\fscx{100 + (8 if o.emphasis >= .6 else 0)}"
                                     f"\\fscy{100 + (8 if o.emphasis >= .6 else 0)})}}{txt}{{\\fscx100\\fscy100\\c{self.c_base}}}")
                    elif j > k and st.get("entry") == "pop" and per <= 3:
                        parts.append(f"{{\\c{col}\\alpha&H60&}}{txt}{{\\alpha&H00&\\c{self.c_base}}}")
                    else:
                        parts.append(f"{{\\c{col}}}{txt}{{\\c{self.c_base}}}")
                intro = ""
                if k == 0:
                    if st.get("entry") == "slide":
                        intro = f"\\move({x},{y + 30},{x},{y},0,120)"
                    elif st.get("entry") == "fade":
                        intro = "\\fad(120,0)"
                pos = f"\\pos({x},{y})" if "\\move" not in intro else ""
                self.add(10, s, e, "Cap", f"{{{pos}{intro}}}" + " ".join(parts))

    # ----------------------------------------------------------------- graphics
    def hook_title(self, text: str, s: float, e: float):
        """Kinetic title: brand-colour box hugging the text, scale-pop in, wraps inside safe margins."""
        words = text.split()
        if len(words) > 9:
            text = " ".join(words[:9]) + "…"
        text = text.rstrip(".,;:")
        t = esc(text if is_hebrew(text) else text.upper())
        y = int(self.H * (0.12 if self.kind != "youtube" else 0.08))
        x = self.W // 2
        self.add(21, s, e, "Hook", f"{{\\an8\\q0\\pos({x},{y})\\frz-2\\fscx40\\fscy40"
                                   f"\\t(0,140,\\fscx108\\fscy108)\\t(140,240,\\fscx100\\fscy100)\\fad(40,200)}}{t}")

    def lower_third(self, name: str, role: str, s: float, dur: float = 3.6):
        if not name:
            return
        e = s + dur
        rtl = is_hebrew(name + role)
        h = int(self.H * (0.10 if self.kind == "youtube" else 0.068))
        fs1, fs2 = int(h * 0.44), int(h * 0.28)
        w = int(max(len(name) * fs1 * 0.62, len(role) * fs2 * 0.6) + 70)
        y = int(self.H * (0.74 if self.kind == "youtube" else 0.53))
        x0 = int(self.W * 0.05) if not rtl else int(self.W * 0.95) - w
        bar = f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"
        acc = f"m 0 0 l 10 0 l 10 {h} l 0 {h}"
        slide_from = -w if not rtl else self.W
        self.add(30, s, e, "Shape", f"{{\\an7\\move({slide_from},{y},{x0},{y},0,260)\\1c&H00101010&\\1a&H30&\\fad(0,250)\\p1}}{bar}{{\\p0}}")
        ax = x0 if not rtl else x0 + w - 10
        self.add(31, s + 0.12, e, "Shape", f"{{\\an7\\pos({ax},{y})\\1c{self.c_primary}\\fscy0\\t(0,200,\\fscy100)\\fad(0,250)\\p1}}{acc}{{\\p0}}")
        tx = x0 + (30 if not rtl else w - 30)
        an = 4 if not rtl else 6
        self.add(32, s + 0.2, e, "Card", f"{{\\an{an}\\pos({tx},{y + int(h*0.36)})\\fs{fs1}\\fad(200,250)}}{esc(name)}")
        if role:
            self.add(32, s + 0.3, e, "Card", f"{{\\an{an}\\pos({tx},{y + int(h*0.74)})\\fs{fs2}\\1c{self.c_primary}\\fad(200,250)}}{esc(role)}")

    def keyword_popup(self, word: str, s: float, dur: float = 1.3, side: int = 1):
        """Keyword card (accent box hugging the word) that pops in, with an arrow springing up at it."""
        e = s + dur
        word = word.rstrip(".,;:!?…") or word
        txt = esc(word if is_hebrew(word) else word.upper())
        y = int(self.H * (0.36 if self.kind != "youtube" else 0.34))
        x = int(self.W * (0.5 + 0.2 * side)) if self.kind == "youtube" else self.W // 2
        self.add(41, s, e, "Pop", f"{{\\an5\\pos({x},{y})\\frz{3 * side}\\fscx20\\fscy20"
                                  f"\\t(0,140,\\fscx110\\fscy110)\\t(140,230,\\fscx100\\fscy100)\\fad(0,160)}}{txt}")
        if self.cfg["graphics"]["arrows"]:
            a = int(self.size * 0.5)
            arrow = (f"m 0 0 l {a} {a} l {a // 3} {a} l {a // 3} {int(a * 2.2)} "
                     f"l {-a // 3} {int(a * 2.2)} l {-a // 3} {a} l {-a} {a}")
            top = y + int(self.size * 0.95)
            self.add(42, s + 0.08, e, "Shape", f"{{\\an8\\move({x},{top + a},{x},{top},0,180)\\1c{self.c_primary}"
                                              f"\\bord3\\3c&H00000000&\\fad(80,160)\\p1}}{arrow}{{\\p0}}")

    def end_card(self, text: str, s: float, e: float):
        x, y = self.W // 2, int(self.H * 0.5)
        self.add(50, s, e, "Shape", f"{{\\an7\\pos(0,0)\\1c&H00000000&\\1a&HFF&\\t(0,300,\\1a&H60&)\\p1}}"
                                    f"m 0 0 l {self.W} 0 l {self.W} {self.H} l 0 {self.H}{{\\p0}}")
        self.add(51, s + 0.1, e, "Hook", f"{{\\an5\\pos({x},{y})\\fscx60\\fscy60\\t(0,220,\\fscx110\\fscy110)"
                                         f"\\t(220,320,\\fscx100\\fscy100)\\fad(150,0)}}{esc(text)}")

    def write(self, path):
        path.write_text(self.header() + "\n".join(self.events) + "\n", encoding="utf-8")
        return path


# --------------------------------------------------------------------------- sidecars
def _srt_ts(t: float) -> str:
    ms = int(round(max(t, 0) * 1000))
    return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"


def write_srt(words: list[CapWord], path, per_line: int = 7, max_chars: int = 42):
    lines = []
    for i, g in enumerate(group_words(words, per_line, max_chars, max_gap=0.9), 1):
        lines += [str(i), f"{_srt_ts(g[0].s)} --> {_srt_ts(g[-1].e + 0.1)}", " ".join(w.text for w in g), ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_vtt(words: list[CapWord], path, per_line: int = 7, max_chars: int = 42):
    lines = ["WEBVTT", ""]
    for g in group_words(words, per_line, max_chars, max_gap=0.9):
        lines += [f"{_srt_ts(g[0].s).replace(',', '.')} --> {_srt_ts(g[-1].e + 0.1).replace(',', '.')}",
                  " ".join(w.text for w in g), ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
