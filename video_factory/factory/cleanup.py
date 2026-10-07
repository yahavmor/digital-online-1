"""Filler / stutter / retake detection and the keep-list (cut list) builder.

Output of this stage is a list of `Seg(src_s, src_e)` in SOURCE time — everything else
(captions, motion, graphics) is re-timed through `Timeline.to_out()`.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field

from .language import in_lexicon, lexicon, norm, phrases

log = logging.getLogger("factory")


@dataclass
class Seg:
    s: float
    e: float
    tags: list[str] = field(default_factory=list)

    @property
    def d(self) -> float:
        return self.e - self.s


class Timeline:
    """Maps source time <-> output time for an ordered list of kept segments."""

    def __init__(self, segs: list[Seg]):
        self.segs = segs
        self.offsets = []
        acc = 0.0
        for sg in segs:
            self.offsets.append(acc)
            acc += sg.d
        self.duration = acc

    def to_out(self, t: float) -> float | None:
        for sg, off in zip(self.segs, self.offsets):
            if sg.s - 1e-6 <= t <= sg.e + 1e-6:
                return off + min(max(t - sg.s, 0.0), sg.d)
        return None

    def span_to_out(self, s: float, e: float) -> tuple[float, float] | None:
        a, b = self.to_out(s), self.to_out(e)
        if a is None and b is None:
            return None
        if a is None:
            a = b - min(e - s, 0.3)
        if b is None:
            b = a + min(e - s, 0.3)
        return (a, max(b, a + 0.05))

    def cut_points(self) -> list[float]:
        return self.offsets[1:]

    def to_dict(self) -> list[dict]:
        return [{"src_s": round(s.s, 3), "src_e": round(s.e, 3), "out_s": round(o, 3), "tags": s.tags}
                for s, o in zip(self.segs, self.offsets)]


# ---------------------------------------------------------------------------
def detect_removals(tr: dict, cfg: dict, kw: dict) -> dict[int, str]:
    """Return {word_index: reason} for words that should be cut."""
    c = cfg["cleanup"]
    lang = tr["language"]
    words = tr["words"]
    hard = lexicon(kw, lang, "fillers_hard")
    soft = lexicon(kw, lang, "fillers_soft")
    soft_multi = [p for p in phrases(kw, lang, "fillers_soft") if len(p) > 1]
    toks = [norm(w["w"]) for w in words]
    removed: dict[int, str] = {}

    for i, w in enumerate(words):
        t = toks[i]
        if not t:
            continue
        if c["remove_fillers"] and (t in hard or (t.strip("ה") == "" and len(t) > 1)):
            removed[i] = "filler"
        elif c["remove_soft_fillers"] and in_lexicon(w["w"], soft):
            gap_b = w["s"] - words[i - 1]["e"] if i else 1
            gap_a = words[i + 1]["s"] - w["e"] if i + 1 < len(words) else 1
            if gap_b > 0.12 or gap_a > 0.12:          # isolated by pauses = verbal tic
                removed[i] = "soft_filler"
    if c["remove_soft_fillers"]:
        for p in soft_multi:
            n = len(p)
            for i in range(len(toks) - n + 1):
                if toks[i:i + n] == p:
                    for j in range(i, i + n):
                        removed[j] = "soft_filler"

    if c["remove_stutters"]:
        for n in (3, 2, 1):
            for i in range(len(toks) - 2 * n + 1):
                a, b = toks[i:i + n], toks[i + n:i + 2 * n]
                if a == b and all(a) and words[i + 2 * n - 1]["e"] - words[i]["s"] < 2.5 * n:
                    for j in range(i, i + n):
                        removed.setdefault(j, "stutter")

    if c["remove_retakes"]:
        k = c["retake_ngram"]
        sents = tr["sentences"]
        for a, b in zip(sents, sents[1:]):
            ta = [x for x in toks[a["i0"]:a["i1"]] if x]
            tb = [x for x in toks[b["i0"]:b["i1"]] if x]
            n = min(k, len(ta), len(tb))
            if n >= 2 and ta[:n] == tb[:n] and b["s"] - a["e"] < 6:
                for j in range(a["i0"], a["i1"]):
                    removed[j] = "retake"
    return removed


def keep_from_words(tr: dict, removed: dict[int, str], duration: float, cfg: dict) -> list[Seg]:
    c = cfg["cleanup"]
    words = tr["words"]
    segs: list[Seg] = []
    cur: list[int] = []

    def flush():
        if not cur:
            return
        first, last = words[cur[0]], words[cur[-1]]
        s = first["s"] - c["pad_before"]
        e = last["e"] + c["pad_after"]
        # never let padding re-introduce a removed word
        if cur[0] - 1 >= 0 and (cur[0] - 1) in removed:
            s = max(s, words[cur[0] - 1]["e"])
        if cur[-1] + 1 < len(words) and (cur[-1] + 1) in removed:
            e = min(e, words[cur[-1] + 1]["s"])
        if cur[0] - 1 >= 0:
            s = max(s, (words[cur[0] - 1]["e"] + first["s"]) / 2 if (cur[0] - 1) not in removed else s)
        if cur[-1] + 1 < len(words):
            e = min(e, (last["e"] + words[cur[-1] + 1]["s"]) / 2 if (cur[-1] + 1) not in removed else e)
        segs.append(Seg(max(0.0, s), min(duration, e)))
        cur.clear()

    prev = None
    for i, w in enumerate(words):
        if i in removed:
            flush()
            prev = None
            continue
        if prev is not None and w["s"] - words[prev]["e"] > c["max_gap"]:
            flush()
        cur.append(i)
        prev = i
    flush()
    return _merge(segs, c["min_segment"])


def keep_from_silence(silences: list[tuple[float, float]], duration: float, cfg: dict) -> list[Seg]:
    c = cfg["cleanup"]
    segs, t = [], 0.0
    for s, e in silences:
        if s > t:
            segs.append(Seg(max(0.0, t - c["pad_before"]), min(duration, s + c["pad_after"])))
        t = e
    if t < duration:
        segs.append(Seg(max(0.0, t - c["pad_before"]), duration))
    return _merge(segs, c["min_segment"])


def _merge(segs: list[Seg], min_len: float) -> list[Seg]:
    segs = sorted(segs, key=lambda x: x.s)
    out: list[Seg] = []
    for sg in segs:
        if out and sg.s <= out[-1].e + 0.02:
            out[-1].e = max(out[-1].e, sg.e)
        else:
            out.append(Seg(sg.s, sg.e))
    return [s for s in out if s.d >= min_len]


def split_long(segs: list[Seg], max_len: float) -> list[Seg]:
    """Split long takes into beats so motion can change inside a continuous shot."""
    out = []
    for sg in segs:
        n = max(1, math.ceil(sg.d / max_len - 1e-9))
        if n == 1:
            out.append(sg)
            continue
        step = sg.d / n
        for k in range(n):
            out.append(Seg(sg.s + k * step, sg.s + (k + 1) * step, ["beat"] if k else []))
    return out


def stats(original: float, segs: list[Seg], removed: dict[int, str]) -> dict:
    kept = sum(s.d for s in segs)
    reasons: dict[str, int] = {}
    for r in removed.values():
        reasons[r] = reasons.get(r, 0) + 1
    return {"source_duration": round(original, 2), "edited_duration": round(kept, 2),
            "removed_seconds": round(original - kept, 2),
            "tightened_pct": round(100 * (1 - kept / original), 1) if original else 0,
            "cuts": max(0, len(segs) - 1), "removed_words": reasons}
