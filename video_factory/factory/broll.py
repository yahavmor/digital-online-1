"""B-roll preparation: find cutaway opportunities, emit search queries, auto-match a local library.

library/broll/ may contain clips named by keyword (e.g. `money_cash_01.mp4`) and/or an
`index.yaml` mapping `file: [tag, tag]`. Unmatched opportunities are written to broll_plan.json
with stock-search queries so an editor (or a downloader script) can fill them later.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .language import in_lexicon, lexicon, norm, variants

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


def library_index(broll_dir: Path) -> list[tuple[Path, set[str]]]:
    idx: list[tuple[Path, set[str]]] = []
    tags_file = broll_dir / "index.yaml"
    explicit = {}
    if tags_file.exists():
        explicit = yaml.safe_load(tags_file.read_text(encoding="utf-8")) or {}
    for p in broll_dir.glob("**/*"):
        if p.suffix.lower() not in VIDEO_EXT:
            continue
        tags = {norm(t) for t in p.stem.replace("-", "_").split("_") if t and not t.isdigit()}
        tags |= {norm(t) for t in explicit.get(p.name, [])}
        idx.append((p, tags))
    return idx


def plan_broll(tr: dict, emphasis: list[float], word_out: dict[int, float], duration: float,
               cfg: dict, kw: dict, broll_dir: Path) -> list[dict]:
    """word_out maps transcript word index -> output-timeline seconds (first appearance)."""
    bc = cfg["broll"]
    if not bc["enabled"] or not tr:
        return []
    lang = tr["language"]
    hints = {norm(k): v for k, v in (kw.get("broll_hints") or {}).items()}
    emph = lexicon(kw, lang, "emphasis")
    lib = library_index(broll_dir)
    plan, last = [], -1e9
    for i, w in enumerate(tr["words"]):
        key = next((v for v in variants(w["w"]) if v in hints), None)
        if not key and not (in_lexicon(w["w"], emph) and emphasis[i] >= 0.6):
            continue
        t = word_out.get(i)
        if t is None or t < 3.0 or t - last < bc["every"] or t + bc["duration"] > duration - 2:
            continue
        queries = hints.get(key, []) if key else []
        if not queries:
            queries = [norm(w["w"])]
        match = None
        wanted = {v for v in variants(w["w"])} | {norm(x) for q in queries for x in q.split()}
        for p, tags in lib:
            if tags & wanted:
                match = p
                break
        plan.append({"t": round(t, 3), "d": bc["duration"], "word": w["w"], "queries": queries,
                     "file": str(match) if match else None, "layout": bc["layout"]})
        last = t
    return plan
