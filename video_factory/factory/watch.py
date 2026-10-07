"""Drop-folder automation: watch workspace/input, process each finished upload, archive it."""
from __future__ import annotations

import logging
import shutil
import time
import traceback
from pathlib import Path

from .config import load_config, resolve_path
from .pipeline import process

log = logging.getLogger("factory")
SIDECAR_SUFFIXES = (".yaml", ".srt", ".words.json")


def _sidecars(video: Path) -> list[Path]:
    return [video.with_suffix(suf) for suf in SIDECAR_SUFFIXES if video.with_suffix(suf).exists()]


def _move(paths: list[Path], dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for p in paths:
        target = dest / p.name
        if target.exists():
            target = dest / f"{p.stem}_{int(time.time())}{p.suffix}"
        shutil.move(str(p), str(target))


def pending(input_dir: Path, exts: list[str]) -> list[Path]:
    return sorted(p for p in input_dir.iterdir()
                  if p.is_file() and p.suffix.lower() in exts and not p.name.startswith("."))


def run_once(preset: str | None = None, overrides: list[str] | None = None) -> list[dict]:
    cfg = load_config(preset, None, overrides)
    inp = resolve_path(cfg, "input")
    reports = []
    for video in pending(inp, cfg["pipeline"]["video_extensions"]):
        reports.append(handle(video, cfg, preset, overrides))
    return reports


def handle(video: Path, cfg: dict, preset, overrides) -> dict:
    side = _sidecars(video)
    try:
        report = process(video, preset, overrides)
        _move([video, *side], resolve_path(cfg, "archive"))
        return report
    except Exception as exc:
        log.error("✖ %s failed: %s", video.name, exc)
        fail = resolve_path(cfg, "failed")
        _move([video, *side], fail)
        (fail / f"{video.stem}.error.log").write_text(traceback.format_exc(), encoding="utf-8")
        return {"job": video.stem, "error": str(exc)}


def watch(preset: str | None = None, overrides: list[str] | None = None) -> None:
    cfg = load_config(preset, None, overrides)
    inp = resolve_path(cfg, "input")
    interval = cfg["pipeline"]["watch_interval"]
    stable_for = cfg["pipeline"]["stable_seconds"]
    sizes: dict[Path, tuple[int, float]] = {}
    log.info("👀 Watching %s  (drop videos here — Ctrl+C to stop)", inp)
    while True:
        now = time.time()
        for v in pending(inp, cfg["pipeline"]["video_extensions"]):
            size = v.stat().st_size
            prev = sizes.get(v)
            if prev is None or prev[0] != size:
                sizes[v] = (size, now)          # still copying
                continue
            if now - prev[1] >= stable_for:
                sizes.pop(v, None)
                handle(v, cfg, preset, overrides)
        time.sleep(interval)
