"""Thin, logged wrappers around ffmpeg / ffprobe."""
from __future__ import annotations

import json
import logging
import re
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("factory")


class FFmpegError(RuntimeError):
    pass


def require_binaries() -> None:
    for b in ("ffmpeg", "ffprobe"):
        if not shutil.which(b):
            raise SystemExit(f"'{b}' not found on PATH. Run scripts/install.sh (or install FFmpeg).")


def run(cmd: list[str], *, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    log.debug("$ %s", " ".join(shlex.quote(str(c)) for c in cmd))
    proc = subprocess.run([str(c) for c in cmd], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-25:])
        raise FFmpegError(f"Command failed ({proc.returncode}): {cmd[0]} ...\n{tail}")
    return proc


def ffmpeg(*args: str | Path, check: bool = True) -> subprocess.CompletedProcess:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error", *args], check=check)


@dataclass
class MediaInfo:
    path: Path
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool
    has_video: bool
    rotation: int = 0
    sample_rate: int = 48000

    @property
    def aspect(self) -> float:
        return self.width / self.height if self.height else 16 / 9

    @property
    def is_vertical(self) -> bool:
        return self.aspect < 0.9


def _fps(rate: str) -> float:
    try:
        n, d = rate.split("/")
        return float(n) / float(d) if float(d) else 30.0
    except Exception:
        return 30.0


def probe(path: Path) -> MediaInfo:
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format",
               "-show_streams", str(path)]).stdout
    data = json.loads(out)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    dur = float(data["format"].get("duration") or (v or a or {}).get("duration") or 0)
    rot = 0
    if v:
        rot = int(v.get("tags", {}).get("rotate", 0) or 0)
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(sd["rotation"])
    w, h = (int(v["width"]), int(v["height"])) if v else (0, 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    return MediaInfo(
        path=Path(path), duration=dur, width=w, height=h,
        fps=_fps(v.get("avg_frame_rate") or v.get("r_frame_rate", "30/1")) if v else 30.0,
        has_audio=a is not None, has_video=v is not None, rotation=rot,
        sample_rate=int(a.get("sample_rate", 48000)) if a else 48000,
    )


def measure_loudness(path: Path, af_prefix: str = "") -> dict:
    """First pass of loudnorm — returns measured values for two-pass normalisation."""
    chain = (af_prefix + "," if af_prefix else "") + "loudnorm=I=-14:TP=-1:LRA=9:print_format=json"
    proc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af", chain,
                "-vn", "-f", "null", "-"], check=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.S)
    if not m:
        raise FFmpegError("loudnorm analysis produced no JSON")
    return json.loads(m.group(0))


def integrated_loudness(path: Path) -> float:
    proc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af",
                "ebur128=framelog=quiet", "-vn", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", proc.stderr)
    return float(m[-1]) if m else float("nan")


def detect_silence(path: Path, noise_db: float, min_dur: float) -> list[tuple[float, float]]:
    proc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af",
                f"silencedetect=noise={noise_db}dB:d={min_dur}", "-vn", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: (-?[\d.]+)", proc.stderr)]
    out = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        out.append((max(0.0, s), e if e is not None else float("inf")))
    return out


def audio_envelope(path: Path, hop: float = 0.05, normalize: bool = True) -> list[float]:
    """RMS energy per `hop` seconds — normalised 0..1 (hook/energy scoring) or absolute linear RMS."""
    import numpy as np
    sr = 8000
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-i", str(path),
                           "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                          capture_output=True)
    if proc.returncode != 0 or not proc.stdout:
        return []
    x = np.frombuffer(proc.stdout, dtype=np.int16).astype(np.float32) / 32768.0
    n = int(sr * hop)
    if len(x) < n:
        return []
    frames = x[: len(x) // n * n].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    if not normalize:
        return [float(v) for v in rms]
    peak = float(np.percentile(rms, 99)) or 1.0
    return [float(v) for v in np.clip(rms / peak, 0, 1).round(4)]


def escape_filter_path(p: Path) -> str:
    """Escape a path for use inside an ffmpeg filter argument (subtitles=, movie=...)."""
    s = str(Path(p).resolve()).replace("\\", "/")
    return s.replace(":", r"\:").replace("'", r"\'").replace(",", r"\,").replace("[", r"\[").replace("]", r"\]")
