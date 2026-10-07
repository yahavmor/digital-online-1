"""Environment check — tells you exactly what is missing and how to fix it."""
from __future__ import annotations

import importlib
import shutil
import subprocess

from .config import load_config, resolve_path


def _ok(flag: bool, label: str, hint: str = "", optional: bool = False) -> bool:
    mark = "✔" if flag else ("○" if optional else "✖")
    print(f"  {mark} {label}" + ("" if flag else f"   → {hint}"))
    return flag


def doctor() -> int:
    cfg = load_config()
    good = True
    print("Binaries")
    ff = shutil.which("ffmpeg")
    good &= _ok(bool(ff), "ffmpeg", "install FFmpeg 6+ (scripts/install.sh does it)")
    good &= _ok(bool(shutil.which("ffprobe")), "ffprobe", "comes with FFmpeg")
    if ff:
        conf = subprocess.run(["ffmpeg", "-hide_banner", "-buildconf"], capture_output=True, text=True).stdout
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        for lib in ("libass", "libfribidi", "libx264", "libfreetype"):
            good &= _ok(f"--enable-{lib}" in conf, f"ffmpeg built with {lib}",
                        "use a full FFmpeg build (gyan.dev 'full' on Windows, brew ffmpeg on macOS)")
        for flt in ("subtitles", "loudnorm", "afftdn", "sidechaincompress", "deesser", "lut3d"):
            good &= _ok(f" {flt} " in filters, f"filter {flt}", "full FFmpeg build required")
    print("Python packages")
    for mod, hint in (("yaml", "pip install PyYAML"), ("numpy", "pip install numpy"),
                      ("faster_whisper", "pip install faster-whisper (needed for transcription)"),
                      ("cv2", "pip install opencv-python-headless (face-tracked reframing)")):
        try:
            importlib.import_module(mod)
            _ok(True, mod)
        except ImportError:
            _ok(False, mod, hint, optional=mod in ("faster_whisper", "cv2"))
            good &= mod in ("faster_whisper", "cv2")   # optional: pipeline degrades gracefully
    print("Assets")
    fonts = list(resolve_path(cfg, "fonts").glob("*.ttf"))
    sys_font = subprocess.run(["fc-list"], capture_output=True, text=True).stdout if shutil.which("fc-list") else ""
    _ok(bool(fonts) or cfg["brand"]["font"].lower() in sys_font.lower(),
        f"caption font '{cfg['brand']['font']}'", "run `factory setup` (downloads Rubik/Heebo)")
    _ok(any(resolve_path(cfg, "sfx").glob("whoosh*")), "SFX kit", "auto-built on first run, or `factory setup`", optional=True)
    music = [p for p in resolve_path(cfg, "music").glob("**/*") if p.suffix.lower() in (".mp3", ".wav", ".m4a")]
    _ok(bool(music), f"music library ({len(music)} tracks)", "optional: add licensed tracks to library/music", optional=True)
    broll = [p for p in resolve_path(cfg, "broll").glob("**/*") if p.suffix.lower() in (".mp4", ".mov")]
    _ok(bool(broll), f"B-roll library ({len(broll)} clips)", "optional: add clips to library/broll", optional=True)
    mdir = resolve_path(cfg, "models")
    for lang in ("he", "en"):
        name = cfg["transcription"]["models"][lang]
        local = (mdir / name.replace("/", "__")).exists()
        _ok(local, f"Whisper model [{lang}] {name}", "run `factory setup` (or it downloads on first use)", optional=True)
    print("\nREADY  (○ = optional, improves results)" if good else "\nNOT READY — fix the ✖ items above")
    return 0 if good else 1
