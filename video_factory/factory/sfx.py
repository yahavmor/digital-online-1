"""Procedural, royalty-free SFX kit (whoosh / impact / riser / pop / tick).

Generated once into library/sfx by `factory setup-sfx`. Drop your own premium SFX into
library/sfx with the same name prefixes (whoosh*, impact*, riser*, pop*, tick*) to override.
"""
from __future__ import annotations

from pathlib import Path

from .media import ffmpeg

KIT = {
    # band-passed noise with a frequency sweep + fast attack/slow release
    "whoosh_01.wav": ("anoisesrc=d=0.55:c=pink:a=0.9,"
                      "bandpass=f=1800:w=1.6,"
                      "afade=t=in:d=0.22:curve=exp,afade=t=out:st=0.22:d=0.33:curve=exp,"
                      "aphaser=type=t:speed=2,highpass=f=300,volume=2.2"),
    # sub drop + noise transient
    "impact_01.wav": ("aevalsrc='0.9*sin(2*PI*(55+90*exp(-14*t))*t)*exp(-5*t)+0.35*(random(0)-0.5)*exp(-40*t)':d=0.9,"
                      "lowpass=f=4000,volume=1.6"),
    # rising filtered noise for builds into hooks
    "riser_01.wav": ("aevalsrc='0.4*sin(2*PI*(200+1600*t*t)*t)*(t/1.5)':d=1.5,"
                     "afade=t=out:st=1.4:d=0.1,volume=1.4"),
    # bubbly UI pop for captions / popups
    "pop_01.wav": ("aevalsrc='0.8*sin(2*PI*(900-500*t*10)*t)*exp(-30*t)':d=0.12,volume=1.5"),
    "tick_01.wav": ("aevalsrc='0.7*sin(2*PI*2400*t)*exp(-90*t)':d=0.05"),
}


def ensure_kit(sfx_dir: Path, force: bool = False) -> list[Path]:
    sfx_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for name, expr in KIT.items():
        prefix = name.split("_")[0]
        if not force and any(sfx_dir.glob(f"{prefix}*")):
            continue
        dst = sfx_dir / name
        ffmpeg("-f", "lavfi", "-i", expr, "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", dst)
        made.append(dst)
    return made
