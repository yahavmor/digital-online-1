"""Question tag: compact rounded label (black fill, thin gold outline, one gold keyword).

Layout is measured with the real font file (PIL) so the box hugs the text exactly; lines are
balanced (similar lengths) instead of greedy-wrapped. Drawn through ASS so it renders with the
same libass/HarfBuzz shaping as the captions (Hebrew RTL safe).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .language import norm


@dataclass
class TagLayout:
    lines: list[list[str]]      # words per line (logical order)
    font_px: int
    line_h: int
    box_w: int
    box_h: int
    pad_x: int
    pad_y: int
    ass_fs: int                 # libass \fs value that renders glyphs at font_px em size


def _font(font_file: Path, px: int):
    from PIL import ImageFont
    return ImageFont.truetype(str(font_file), px, layout_engine=ImageFont.Layout.RAQM)


def _width(font, text: str) -> float:
    return font.getlength(text, direction="rtl" if any("֐" <= c <= "׿" for c in text) else None)


def _balanced(words: list[str], font, max_w: float) -> list[list[str]]:
    """Fewest lines that fit, then minimise the longest line (balanced rag)."""
    n = len(words)
    for k in range(1, n + 1):
        best = None
        # DP over split points minimising the max line width
        import functools

        @functools.lru_cache(None)
        def solve(i: int, lines_left: int):
            if lines_left == 1:
                w = _width(font, " ".join(words[i:]))
                return (w, [words[i:]]) if w <= max_w else (float("inf"), [])
            out = (float("inf"), [])
            for j in range(i + 1, n - lines_left + 2):
                w = _width(font, " ".join(words[i:j]))
                if w > max_w:
                    break
                rest_w, rest = solve(j, lines_left - 1)
                cand = max(w, rest_w)
                if cand < out[0]:
                    out = (cand, [words[i:j]] + rest)
            return out
        if k <= n:
            best = solve(0, k)
        if best and best[0] < float("inf"):
            return best[1]
    return [words]


def layout(text: str, font_file: Path, W: int, font_frac: float = 0.03, max_w_frac: float = 0.84) -> TagLayout:
    px = max(24, int(round(W * font_frac * 1920 / 1080)))      # font_frac is relative to a 1920 frame height
    font = _font(font_file, px)
    pad_x, pad_y = int(px * 0.70), int(px * 0.40)
    max_text_w = W * max_w_frac - 2 * pad_x
    lines = _balanced(text.split(), font, max_text_w)
    line_h = int(px * 1.24)
    text_w = max(_width(font, " ".join(l)) for l in lines)
    asc, desc = font.getmetrics()
    # libass treats \fs as ascent+descent height (not the em size PIL uses) -> convert
    ass_fs = asc + desc
    return TagLayout(lines, px, line_h, int(text_w + 2 * pad_x), int(line_h * len(lines) + 2 * pad_y),
                     pad_x, pad_y, ass_fs)


def rounded_rect(w: int, h: int, r: int) -> str:
    """ASS vector path for a rounded rectangle with origin at top-left (cubic Bézier corners)."""
    k = 0.4477 * r       # (1 - 0.5523) * r -> control-point offset for a circular arc
    return (f"m {r} 0 l {w - r} 0 b {w - k:.1f} 0 {w} {k:.1f} {w} {r} "
            f"l {w} {h - r} b {w} {h - k:.1f} {w - k:.1f} {h} {w - r} {h} "
            f"l {r} {h} b {k:.1f} {h} 0 {h - k:.1f} 0 {h - r} "
            f"l 0 {r} b 0 {k:.1f} {k:.1f} 0 {r} 0")


def keyword_hit(word: str, keyword: str | None) -> bool:
    if not keyword:
        return False
    k = norm(keyword)
    w = norm(word)
    return bool(k) and (w == k or (len(k) >= 3 and k in w))
