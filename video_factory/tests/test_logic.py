"""Fast unit tests for the editorial logic (no rendering)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factory import analyze, captions, cleanup, hooks, motion  # noqa: E402
from factory.config import apply_set, deep_merge, load_config  # noqa: E402
from factory.language import in_lexicon, is_number, variants  # noqa: E402
from factory.transcribe import finalize, words_from_srt  # noqa: E402


def W(*items, start=0.0, gap=0.1):
    """Build words: W(("hello", .3), ("world", .3)) — ("_", d) inserts a pause."""
    out, t = [], start
    for w, d in items:
        if w != "_":
            out.append({"w": w, "s": t, "e": t + d})
        t += d + (0 if w == "_" else gap)
    return out


CFG = load_config()
KW = CFG["_keywords"]


def tr_of(words, lang="en"):
    return finalize(words, lang)


# ---------------------------------------------------------------- config
def test_deep_merge_and_set():
    a = {"x": {"y": 1, "z": 2}, "k": 1}
    assert deep_merge(a, {"x": {"y": 5}}) == {"x": {"y": 5, "z": 2}, "k": 1}
    assert apply_set(a, ["x.z=7", "n.m=[1,2]"])["n"]["m"] == [1, 2]


def test_presets_load():
    for p in ("youtube", "tiktok", "reels", "shorts", "linkedin", "facebook", "sales", "fast"):
        cfg = load_config(p)
        assert cfg["_preset"] == p
        assert cfg["captions"]["style"] in cfg["_caption_styles"]


# ---------------------------------------------------------------- language
def test_hebrew_prefix_variants():
    assert "סוד" in variants("והסוד")
    assert in_lexicon("וכסף", {"כסף"})
    assert is_number("3") and is_number("מיליון") and is_number("million")


# ---------------------------------------------------------------- cleanup
def test_fillers_and_stutter_removed():
    tr = tr_of(W(("um", .3), ("I", .1), ("I", .1), ("think", .3), ("so.", .3)))
    rm = cleanup.detect_removals(tr, CFG, KW)
    assert rm[0] == "filler"
    assert rm[1] == "stutter" and 2 not in rm


def test_hebrew_fillers():
    tr = tr_of(W(("אממ", .3), ("זה", .2), ("עובד", .3)), "he")
    assert cleanup.detect_removals(tr, CFG, KW) == {0: "filler"}


def test_retake_keeps_last_take():
    words = W(("Here's", .3), ("the", .1), ("thing", .3), ("you", .1), ("_", 1.0),
              ("Here's", .3), ("the", .1), ("thing", .3), ("you", .1), ("know.", .3))
    tr = tr_of(words)
    rm = cleanup.detect_removals(tr, CFG, KW)
    assert {0, 1, 2, 3} <= set(rm) and 5 not in rm


def test_keep_segments_cut_dead_air():
    words = W(("one", .3), ("two", .3), ("_", 2.0), ("three", .3))
    tr = tr_of(words)
    keep = cleanup.keep_from_words(tr, {}, 10.0, CFG)
    assert len(keep) == 2
    assert sum(k.d for k in keep) < 2.0


def test_padding_never_reintroduces_filler():
    words = W(("hello", .3), ("um", .3), ("world", .3), gap=0.02)
    tr = tr_of(words)
    rm = cleanup.detect_removals(tr, CFG, KW)
    keep = cleanup.keep_from_words(tr, rm, 5.0, CFG)
    um = tr["words"][1]
    assert all(not (k.s < um["e"] - 0.01 and k.e > um["s"] + 0.01) for k in keep)


def test_timeline_mapping():
    tl = cleanup.Timeline([cleanup.Seg(1, 2), cleanup.Seg(5, 7)])
    assert tl.duration == 3
    assert tl.to_out(1.5) == 0.5 and tl.to_out(6) == 2.0 and tl.to_out(3) is None


def test_silence_fallback():
    keep = cleanup.keep_from_silence([(2.0, 4.0), (6.0, 6.5)], 8.0, CFG)
    assert keep[0].s == 0 and abs(keep[0].e - 2.1) < 1e-6 and len(keep) == 3
    assert all(not (k.s < 3.9 and k.e > 2.2) for k in keep)   # 2.0–4.0 silence is gone


# ---------------------------------------------------------------- motion
def test_shots_are_frame_quantised_and_vary():
    keep = [cleanup.Seg(0.013, 9.71), cleanup.Seg(12.0, 15.0)]
    shots = motion.plan_shots(keep, [], [], [], CFG, 30)
    for sh in shots:
        assert abs(sh.s * 30 - round(sh.s * 30)) < 1e-6 and abs(sh.e * 30 - round(sh.e * 30)) < 1e-6
        assert sh.d <= CFG["motion"]["shot_max"] + 1e-6
    # consecutive shots across a jump cut never share the same framing
    for a, b in zip(shots, shots[1:]):
        if b.jump:
            assert abs(a.z1 - b.z0) >= 0.04


def test_emphasis_snap_zoom():
    words = W(("this", .3), ("is", .2), ("the", .2), ("secret", .4), ("today", .4), start=0.2)
    emph = [0, 0, 0, 0.9, 0]
    shots = motion.plan_shots([cleanup.Seg(0, 3.0)], words, emph, [], CFG, 30)
    assert any(s.emphasis and s.z1 == CFG["motion"]["emphasis_zoom"] for s in shots)


# ---------------------------------------------------------------- analysis / hooks
def test_hook_scoring_prefers_hooks():
    words = W(("The", .1), ("weather", .3), ("is", .1), ("fine.", .3), ("_", .9),
              ("Why", .2), ("does", .2), ("nobody", .3), ("know", .2), ("this", .2), ("secret?", .4))
    tr = tr_of(words)
    emph = analyze.word_emphasis(tr, CFG, KW, [])
    sc = analyze.sentence_scores(tr, KW, emph)
    assert sc[1]["score"] > sc[0]["score"]
    assert "question" in sc[1]["reasons"]


def test_titles_are_cleaned():
    tr = tr_of(W(("I", .1), ("I", .1), ("made", .3), ("a", .1), ("million.", .4)))
    rm = cleanup.detect_removals(tr, CFG, KW)
    sc = analyze.sentence_scores(tr, KW, [0] * 5, rm)
    assert sc[0]["text"] == "I made a million."


def test_shorts_non_overlapping():
    scores = [{"index": i, "score": 3.0 if i % 4 == 0 else 1.0, "reasons": [], "s": i * 5.0,
               "e": i * 5.0 + 4.5, "text": f"Sentence {i}."} for i in range(30)]
    keep = [cleanup.Seg(0, 150)]
    cfg = dict(CFG, shorts=dict(CFG["shorts"], count=4, min_duration=15, max_duration=40, target_duration=25))
    plans = hooks.plan_shorts(scores, keep, cfg)
    assert 1 <= len(plans) <= 4
    for a, b in zip(plans, plans[1:]):
        assert a.end <= b.start
    for p in plans:
        assert 15 <= hooks.kept_duration(keep, p.start, p.end) <= 40


# ---------------------------------------------------------------- captions
def test_caption_groups_and_no_overlap(tmp_path):
    ws = [captions.CapWord(f"w{i}", i * 0.3, i * 0.3 + 0.25) for i in range(10)]
    ab = captions.AssBuilder(CFG, 1080, 1920, "vertical")
    ab.captions(ws, 0.7)
    out = ab.write(tmp_path / "c.ass").read_text(encoding="utf-8")
    assert "[Events]" in out and out.count("Dialogue:") == 10

    def t(s):
        h, m, x = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(x)
    ev = [(t(l.split(",")[1]), t(l.split(",")[2])) for l in out.splitlines() if l.startswith("Dialogue")]
    for (a0, a1), (b0, _) in zip(ev, ev[1:]):
        assert a1 <= b0 + 1e-6


def test_ass_color():
    assert captions.ass_color("#FFD400") == "&H0000D4FF&"


def test_srt_roundtrip(tmp_path):
    ws = [captions.CapWord("שלום", 0.5, 0.9), captions.CapWord("עולם", 1.0, 1.4)]
    p = captions.write_srt(ws, tmp_path / "a.srt")
    back = words_from_srt(p)
    assert [w["w"] for w in back] == ["שלום", "עולם"]
    assert abs(back[0]["s"] - 0.5) < 1e-6
