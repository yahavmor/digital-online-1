"""One-time asset setup: caption fonts, Whisper models, procedural SFX kit."""
from __future__ import annotations

import logging
import re
import urllib.request
from pathlib import Path

from .config import load_config, resolve_path
from .sfx import ensure_kit

log = logging.getLogger("factory")

FONTS = {  # family -> weights to fetch (Hebrew + Latin coverage)
    "Rubik": [900, 700],
    "Heebo": [900, 800],
    "Assistant": [800],
}


def fetch_fonts(dst: Path) -> list[Path]:
    dst.mkdir(parents=True, exist_ok=True)
    got = []
    for fam, weights in FONTS.items():
        for wgt in weights:
            out = dst / f"{fam}-{wgt}.ttf"
            if out.exists():
                got.append(out)
                continue
            url = f"https://fonts.googleapis.com/css2?family={fam}:wght@{wgt}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/4.0"})  # old UA -> TTF urls
                css = urllib.request.urlopen(req, timeout=30).read().decode()
                ttf = re.search(r"url\((https://[^)]+\.ttf)\)", css)
                if not ttf:
                    raise RuntimeError("no ttf url in css")
                out.write_bytes(urllib.request.urlopen(ttf.group(1), timeout=60).read())
                got.append(out)
                log.info("  font %s", out.name)
            except Exception as exc:
                log.warning("  could not fetch %s %s (%s)", fam, wgt, exc)
    return got


def fetch_models(cfg: dict, langs: list[str]) -> None:
    try:
        from faster_whisper import download_model
    except ImportError:
        log.error("faster-whisper not installed; run the installer first.")
        return
    mdir = resolve_path(cfg, "models")
    mdir.mkdir(parents=True, exist_ok=True)
    names = {cfg["transcription"]["models"][k] for k in langs + ["detect"] if k in cfg["transcription"]["models"]}
    for name in names:
        target = mdir / name.replace("/", "__")
        if target.exists():
            log.info("  model %s ✓", name)
            continue
        log.info("  downloading model %s (one-time, may take a while)…", name)
        try:
            download_model(name, output_dir=str(target))
        except Exception as exc:
            log.error("  model %s failed: %s", name, exc)


def setup(models: list[str] | None = None, fonts: bool = True) -> int:
    cfg = load_config()
    log.info("• SFX kit")
    ensure_kit(resolve_path(cfg, "sfx"))
    if fonts:
        log.info("• Fonts")
        fetch_fonts(resolve_path(cfg, "fonts"))
    langs = ["he", "en"] if models is None else [m for m in models if m != "none"]
    if langs:
        log.info("• Whisper models: %s", ", ".join(langs))
        fetch_models(cfg, langs)
    log.info("Setup complete. Run `factory doctor` to verify.")
    return 0
