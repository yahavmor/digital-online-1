"""Shot planning: turns the keep-list into visual beats with punch-ins, snap zooms and SFX cues."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .analyze import face_at
from .cleanup import Seg, split_long


@dataclass
class Shot:
    s: float                 # source in
    e: float                 # source out
    z0: float = 1.0          # zoom at shot start
    z1: float = 1.0          # zoom at shot end
    cx: float = 0.5          # face anchor (normalised)
    cy: float = 0.42
    punch: bool = False      # hard punch-in / out at entry -> motion blur + whoosh
    emphasis: bool = False   # snap zoom on an emphasised word -> impact
    jump: bool = False       # a real jump cut (source discontinuity) precedes this shot
    tags: list[str] = field(default_factory=list)

    @property
    def d(self) -> float:
        return self.e - self.s

    def to_dict(self):
        return asdict(self)


def quantize(segs: list[Seg], fps: float) -> list[Seg]:
    """Snap all cut points to the output frame grid -> zero A/V drift over hundreds of cuts."""
    out = []
    for sg in segs:
        s = round(sg.s * fps) / fps
        e = round(sg.e * fps) / fps
        if e - s >= 1 / fps * 3:
            out.append(Seg(s, e, list(sg.tags)))
    return out


def plan_shots(keep: list[Seg], words: list[dict], emphasis: list[float], face: list,
               cfg: dict, fps: float) -> list[Shot]:
    m = cfg["motion"]
    beats = split_long(keep, m["shot_max"])

    # split a beat right before a strongly emphasised word -> snap-zoom lands on the word
    hot = [(w["s"], i) for i, w in enumerate(words) if emphasis and emphasis[i] >= 0.7]
    pieces: list[Seg] = []
    for b in beats:
        cut = next((t for t, _ in hot if b.s + 0.7 < t < b.e - 0.6), None)
        if cut is not None:
            pieces += [Seg(b.s, cut - 0.04, list(b.tags)), Seg(cut - 0.04, b.e, ["emphasis"])]
        else:
            pieces.append(b)
    pieces = quantize(pieces, fps)

    levels = m["zoom_levels"] or [1.0]
    shots: list[Shot] = []
    li = 0
    prev_z = None
    prev_e = None
    for p in pieces:
        jump = prev_e is not None and abs(p.s - prev_e) > 1.5 / fps
        cx, cy, _ = face_at(face, p.s, p.e) if m.get("face_anchor", True) else (0.5, 0.42, 0.25)
        if not m["enabled"]:
            shots.append(Shot(p.s, p.e, 1.0, 1.0, cx, cy, jump=jump, tags=p.tags))
            prev_e = p.e
            continue
        if "emphasis" in p.tags:
            z = m["emphasis_zoom"]
            sh = Shot(p.s, p.e, z + 0.06, z, cx, cy, punch=True, emphasis=True, jump=jump, tags=p.tags)
        else:
            z = levels[li % len(levels)]
            li += 1
            # a jump cut at the same framing reads as a mistake -> force a framing change
            if jump and prev_z is not None and abs(z - prev_z) < 0.05:
                z = levels[li % len(levels)]
                li += 1
                if abs(z - prev_z) < 0.05:
                    z = prev_z + 0.1 if prev_z < 1.15 else 1.0
            push = m["slow_push"] if p.d > 1.4 else 0.0
            punch = prev_z is not None and abs(z - prev_z) >= 0.08
            sh = Shot(p.s, p.e, z, z + push, cx, cy, punch=punch, jump=jump, tags=p.tags)
        shots.append(sh)
        prev_z = sh.z1
        prev_e = p.e
    return shots


def sfx_cues(shots: list[Shot], offsets: list[float], cfg: dict) -> list[dict]:
    a = cfg["audio"]["sfx"]
    ev = []
    for sh, t in zip(shots, offsets):
        if sh.emphasis and a["impact_on_emphasis"]:
            ev.append({"t": t, "kind": "impact", "priority": 2, "gain": -2})
        elif sh.punch and a["whoosh_on_zoom"] and t > 0:
            ev.append({"t": t, "kind": "whoosh", "offset": -0.18, "priority": 1, "gain": -4})
    return ev
