"""Colour correction + grading filter chains (pure ffmpeg, optional .cube LUTs)."""
from __future__ import annotations

from pathlib import Path

from .media import escape_filter_path

LOOKS = {
    "none": "",
    # warm highlights, slightly cool shadows, soft filmic roll-off
    "cinematic_warm": "colorbalance=rs=-0.03:bs=0.04:rm=0.03:bm=-0.02:rh=0.05:gh=0.01:bh=-0.04,"
                      "curves=all='0/0.02 0.25/0.22 0.5/0.5 0.75/0.79 1/0.97'",
    "teal_orange": "colorbalance=rs=-0.08:gs=0.0:bs=0.08:rm=0.05:bm=-0.04:rh=0.07:bh=-0.07,"
                   "curves=all='0/0.03 0.3/0.26 0.7/0.74 1/0.97'",
    "clean_bright": "colorbalance=rh=0.02:bh=0.0,curves=all='0/0 0.4/0.43 0.8/0.84 1/1'",
    "moody": "colorbalance=bs=0.06:rh=0.03,curves=all='0/0.04 0.3/0.22 0.6/0.58 1/0.92',eq=saturation=0.85",
}


def correction(stats: dict, cfg: dict) -> list[str]:
    """Technical correction derived from measured picture statistics."""
    c = cfg["color"]
    f: list[str] = []
    y = stats.get("y_avg")
    if c["auto_levels"] and y is not None:
        lo, hi = stats.get("y_low") or 16, stats.get("y_high") or 235
        # stretch a flat / washed-out range toward broadcast black/white
        span = max(hi - lo, 40)
        if span < 190:
            lo_n, hi_n = lo / 255 * 0.8, min(1.0, hi / 255 * 1.02)
            f.append(f"colorlevels=rimin={lo_n:.3f}:gimin={lo_n:.3f}:bimin={lo_n:.3f}:"
                     f"rimax={hi_n:.3f}:gimax={hi_n:.3f}:bimax={hi_n:.3f}")
        # exposure: aim mid-grey ~ 118 for faces on a talking head
        bright = 0.0
        if y < 95:
            bright = min((118 - y) / 255, 0.10)
        elif y > 150:
            bright = -min((y - 135) / 255, 0.08)
        gamma = 1.0 + (0.12 if y < 85 else 0.0)
        f.append(f"eq=brightness={bright:.3f}:gamma={gamma * c['gamma']:.3f}")
        # white balance: neutralise chroma cast (U/V centred on 128)
        u, v = stats.get("u_avg"), stats.get("v_avg")
        if u is not None and v is not None:
            du, dv = (u - 128) / 128, (v - 128) / 128
            if abs(du) > 0.02 or abs(dv) > 0.02:
                f.append(f"colorbalance=bm={-du*0.6:.3f}:rm={-dv*0.6:.3f}:bs={-du*0.4:.3f}:rs={-dv*0.4:.3f}")
    f.append(f"eq=contrast={c['contrast']:.3f}:saturation={c['saturation']:.3f}")
    if c.get("skin_protect"):
        # gentle midtone warmth = healthier skin without pushing whole frame orange
        f.append("colorbalance=rm=0.02:gm=0.0:bm=-0.015")
    return f


def grade(cfg: dict, luts_dir: Path) -> list[str]:
    c = cfg["color"]
    if c.get("lut"):
        p = luts_dir / c["lut"]
        if p.exists():
            return [f"lut3d=file='{escape_filter_path(p)}':interp=tetrahedral"]
    look = LOOKS.get(c.get("look") or "none", "")
    return [look] if look else []


def source_chain(stats: dict, cfg: dict, luts_dir: Path, low_res: bool) -> str:
    """Filters applied to the source picture before any reframing."""
    c = cfg["color"]
    if not c["enabled"]:
        return "null"
    f: list[str] = []
    dn = c["denoise"]
    if dn is True or (dn == "auto" and low_res):
        s = c["denoise_strength"]
        f.append(f"hqdn3d={s}:{s*0.75}:{s*1.5}:{s*1.2}")
    f += correction(stats, cfg)
    f += grade(cfg, luts_dir)
    return ",".join(x for x in f if x)


def finish_chain(cfg: dict, upscale_factor: float) -> str:
    """Filters applied after scaling to the delivery resolution."""
    c = cfg["color"]
    f: list[str] = []
    sh = c["sharpen"]
    if c["enabled"] and (sh is True or (sh == "auto" and upscale_factor > 1.2)):
        amt = 0.6 if upscale_factor < 2 else 0.9
        f.append(f"unsharp=5:5:{amt}:5:5:0.0")
    if c["enabled"] and c.get("vignette", 0) > 0:
        f.append(f"vignette=angle={0.35 + c['vignette']:.2f}:mode=forward")
    return ",".join(f) or "null"
