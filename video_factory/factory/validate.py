"""Delivery QC: verifies every output of a job against spec. Non-zero exit on any failure."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import load_config
from .media import integrated_loudness, probe, run


class QC:
    def __init__(self):
        self.rows: list[tuple[str, str, bool, str]] = []

    def check(self, item: str, name: str, ok: bool, detail: str = ""):
        self.rows.append((item, name, bool(ok), detail))

    @property
    def ok(self) -> bool:
        return all(r[2] for r in self.rows)

    def table(self) -> str:
        w = max((len(r[0]) for r in self.rows), default=10)
        lines = []
        for item, name, ok, detail in self.rows:
            lines.append(f"  {'PASS' if ok else 'FAIL'}  {item:<{w}}  {name:<22} {detail}")
        passed = sum(r[2] for r in self.rows)
        lines.append(f"\n  {passed}/{len(self.rows)} checks passed")
        return "\n".join(lines)


def _black_frames(path: Path) -> float:
    proc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-vf",
                "blackdetect=d=0.4:pix_th=0.06", "-an", "-f", "null", "-"], check=False)
    return sum(float(x) for x in re.findall(r"black_duration:([\d.]+)", proc.stderr))


def _srt_ok(path: Path) -> tuple[bool, str]:
    txt = path.read_text(encoding="utf-8")
    times = re.findall(r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})", txt)
    prev = -1.0
    for t in times:
        a = int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2]) + int(t[3]) / 1000
        b = int(t[4]) * 3600 + int(t[5]) * 60 + int(t[6]) + int(t[7]) / 1000
        if b <= a or a + 1e-3 < prev:
            return False, f"non-monotonic cue at {a:.2f}s"
        prev = a
    return bool(times), f"{len(times)} cues"


def validate_job(out_dir: Path, deep: bool = True) -> QC:
    cfg = load_config()
    qc = QC()
    rep_path = out_dir / "report.json"
    qc.check(out_dir.name, "report.json", rep_path.exists())
    if not rep_path.exists():
        return qc
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    src_dur = rep["source_info"]["duration"]
    c = rep["cleanup"]
    qc.check(out_dir.name, "cleanup sane", 0 < c["edited_duration"] <= src_dur + 0.05,
             f"{c['source_duration']}s -> {c['edited_duration']}s")
    for d in rep["deliverables"]:
        f = Path(d["file"])
        item = f.name
        qc.check(item, "file exists", f.exists() and f.stat().st_size > 10_000)
        if not f.exists():
            continue
        info = probe(f)
        W, H = map(int, d["resolution"].split("x"))
        qc.check(item, "resolution", (info.width, info.height) == (W, H), f"{info.width}x{info.height}")
        exp_fps = cfg["export"][d["kind"]]["fps"]
        qc.check(item, "fps", abs(info.fps - exp_fps) < 0.05, f"{info.fps:.2f}")
        qc.check(item, "audio stream", info.has_audio)
        qc.check(item, "duration", abs(info.duration - d["duration"]) < 0.25,
                 f"{info.duration:.2f}s vs plan {d['duration']}s")
        # A/V sync: per-stream durations must agree
        streams = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json",
                       str(f)]).stdout
        durs = {s["codec_type"]: float(s.get("duration", 0)) for s in json.loads(streams)["streams"]}
        if "audio" in durs and "video" in durs:
            qc.check(item, "A/V length match", abs(durs["audio"] - durs["video"]) < 0.1,
                     f"Δ={abs(durs['audio'] - durs['video']) * 1000:.0f}ms")
        if d["kind"] == "vertical":
            qc.check(item, "short length", d["duration"] <= 60.5 or not d["name"].startswith("short"),
                     f"{d['duration']}s")
        if deep:
            target = cfg["audio"]["loudness"]["youtube" if d["kind"] == "youtube" else "vertical"]["I"]
            lufs = integrated_loudness(f)
            qc.check(item, "loudness", abs(lufs - target) <= 1.5, f"{lufs:.1f} LUFS (target {target})")
            black = _black_frames(f)
            qc.check(item, "no black gaps", black < 0.5, f"{black:.2f}s black")
        srt = out_dir / "captions" / f"{f.stem}.srt"
        if srt.exists():
            ok, det = _srt_ok(srt)
            qc.check(item, "captions .srt", ok, det)
    proj = list((out_dir / "project").glob("*.fcpxml")) if (out_dir / "project").exists() else []
    for p in proj:
        try:
            import xml.etree.ElementTree as ET
            ET.parse(p)
            qc.check(p.name, "fcpxml well-formed", True)
        except Exception as exc:
            qc.check(p.name, "fcpxml well-formed", False, str(exc))
    return qc
