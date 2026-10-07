"""Hook finding + viral short extraction.

Each short = a window of consecutive sentences that
  * opens on a hook-scored sentence (curiosity gap in the first second),
  * fits the platform duration window after cleanup,
  * maximises average sentence value,
  * optionally gets a "cold open": its single strongest line played first as a teaser.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .cleanup import Seg


@dataclass
class ShortPlan:
    index: int
    start: float
    end: float
    score: float
    title: str
    sentences: list[int]
    teaser: tuple[float, float] | None = None
    reasons: list[str] = field(default_factory=list)


def kept_duration(keep: list[Seg], s: float, e: float) -> float:
    return sum(max(0.0, min(k.e, e) - max(k.s, s)) for k in keep)


def clip_keep(keep: list[Seg], s: float, e: float) -> list[Seg]:
    out = []
    for k in keep:
        a, b = max(k.s, s), min(k.e, e)
        if b - a > 0.15:
            out.append(Seg(a, b, list(k.tags)))
    return out


def best_hook(scores: list[dict], within: float | None = None) -> dict | None:
    cands = [s for s in scores if within is None or s["s"] <= within]
    cands = [s for s in cands if 1.2 <= s["e"] - s["s"] <= 9.0]
    return max(cands, key=lambda s: s["score"], default=None)


def plan_shorts(scores: list[dict], keep: list[Seg], cfg: dict) -> list[ShortPlan]:
    sc = cfg["shorts"]
    if not scores:
        return []
    mean = sum(s["score"] for s in scores) / len(scores)
    cands: list[ShortPlan] = []
    for i, first in enumerate(scores):
        if sc["require_hook"] and first["score"] < mean + 0.3:
            continue
        for j in range(i, len(scores)):
            dur = kept_duration(keep, first["s"], scores[j]["e"])
            if dur > sc["max_duration"]:
                break
            if dur < sc["min_duration"]:
                continue
            window = scores[i:j + 1]
            avg = sum(w["score"] for w in window) / len(window)
            closeness = 1 - min(abs(dur - sc["target_duration"]) / sc["target_duration"], 1)
            ending = 0.4 if window[-1]["text"].rstrip().endswith((".", "!", "?")) else 0
            total = first["score"] * 1.6 + avg + closeness * 1.2 + ending
            cands.append(ShortPlan(0, first["s"], scores[j]["e"], round(total, 3), first["text"],
                                   [w["index"] for w in window], reasons=list(first["reasons"])))
    cands.sort(key=lambda c: -c.score)
    chosen: list[ShortPlan] = []
    gap = sc["min_gap_between"]
    for c in cands:
        if all(c.end + gap <= o.start or c.start >= o.end + gap for o in chosen):
            chosen.append(c)
        if len(chosen) >= sc["count"]:
            break
    chosen.sort(key=lambda c: c.start)
    by_idx = {s["index"]: s for s in scores}
    for n, c in enumerate(chosen, 1):
        c.index = n
        if cfg["structure"]["cold_open_shorts"] and len(c.sentences) > 2:
            top = max((by_idx[k] for k in c.sentences[1:]), key=lambda s: s["score"])
            if top["score"] > by_idx[c.sentences[0]]["score"] and top["e"] - top["s"] <= 6:
                c.teaser = (top["s"], top["e"])
                c.title = top["text"]
    return chosen
