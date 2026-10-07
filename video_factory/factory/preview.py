"""Instant style preview: renders captions + graphics on a backdrop to a PNG contact sheet."""
from __future__ import annotations

from pathlib import Path

from .captions import AssBuilder, CapWord
from .config import load_config, resolve_path
from .media import escape_filter_path, ffmpeg

SAMPLES = {
    "en": "Most people never learn this secret. I made my first million in 3 years!",
    "he": "רוב האנשים לא יודעים את הסוד הזה. הרווחתי את המיליון הראשון שלי תוך 3 שנים!",
}


def preview(style: str | None, lang: str, kind: str, out: Path, preset: str | None = None,
            background: Path | None = None) -> Path:
    sets = [f"captions.style={style}"] if style else []
    cfg = load_config(preset, None, sets)
    if not cfg["brand"]["name"]:
        cfg["brand"]["name"], cfg["brand"]["role"] = ("Your Name", "Your Title") if lang == "en" else ("השם שלך", "התפקיד שלך")
    W, H = (cfg["export"]["youtube"]["width"], cfg["export"]["youtube"]["height"]) if kind == "youtube" \
        else (cfg["export"]["vertical"]["width"], cfg["export"]["vertical"]["height"])
    words, t = [], 0.4
    hot = {"secret.", "million", "3", "הסוד", "המיליון"}
    for w in SAMPLES[lang].split():
        d = 0.22 + 0.04 * len(w)
        words.append(CapWord(w, t, t + d, 0.9 if w in hot else 0.1))
        t += d + 0.05
    dur = t + 3.0
    ab = AssBuilder(cfg, W, H, kind)
    ab.captions(words, cfg["captions"]["position_youtube" if kind == "youtube" else "position_vertical"])
    ab.hook_title(" ".join(w.text for w in words[:6]), 0.0, 2.6)
    ab.lower_third(cfg["brand"]["name"], cfg["brand"]["role"], 1.0)
    ab.keyword_popup(words[3].text if lang == "en" else words[5].text, 3.0)
    ab.end_card(cfg["graphics"]["cta_text"][lang], t, dur)
    out.parent.mkdir(parents=True, exist_ok=True)
    ass = ab.write(out.with_suffix(".ass"))
    times = [0.35, 1.6, 2.4, 3.3, words[9].s + 0.05, t + 0.6]
    src = (["-stream_loop", "-1", "-i", str(background)] if background else
           ["-f", "lavfi", "-i", f"gradients=s={W}x{H}:c0=0x2a3a4a:c1=0x9a7a5a:d={dur}:speed=0.02"])
    fonts = escape_filter_path(resolve_path(cfg, "fonts"))
    sel = "+".join(f"eq(n\\,{int(x * 30)})" for x in times)
    tile_w = W // 3 if kind == "youtube" else W // 4
    ffmpeg(*src, "-t", f"{dur:.2f}", "-vf",
           f"fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
           f"subtitles=filename='{escape_filter_path(ass)}':fontsdir='{fonts}',select='{sel}',"
           f"scale={tile_w}:-2,tile={'3x2' if kind == 'youtube' else '6x1'}",
           "-frames:v", "1", "-update", "1", out)
    return out
