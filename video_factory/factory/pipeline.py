"""The production line: one raw video in -> a folder of finished deliverables out."""
from __future__ import annotations

import json
import logging
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from . import analyze, audio, broll as brollmod, captions as capmod, cleanup, color, hooks, motion, \
    project_export, render, sfx
from .config import ROOT, load_config, resolve_path
from .media import MediaInfo, audio_envelope, detect_silence, probe, require_binaries
from .transcribe import extract_audio, is_hebrew, transcribe

log = logging.getLogger("factory")


def slugify(name: str) -> str:
    s = re.sub(r"[^\w֐-׿-]+", "_", name, flags=re.UNICODE).strip("_")
    return s[:60] or "video"


def _dump(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@dataclass
class Context:
    raw: Path
    cfg: dict
    job: str
    work: Path
    out: Path
    info: MediaInfo
    voice: Path
    tr: dict | None
    emphasis: list[float]
    scores: list[dict]
    keep: list[cleanup.Seg]
    face: list
    src_chain: str
    lang: str


# --------------------------------------------------------------------------- analysis stage
def prepare(raw: Path, cfg: dict) -> Context:
    require_binaries()
    job = slugify(raw.stem)
    work = resolve_path(cfg, "processing") / job
    out = resolve_path(cfg, "output") / job
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    cfg["_fonts_dir"] = str(resolve_path(cfg, "fonts"))
    sfx.ensure_kit(resolve_path(cfg, "sfx"))

    info = probe(raw)
    if not info.has_video:
        raise ValueError(f"{raw.name} has no video stream")
    log.info("▶ %s  %dx%d  %.1ffps  %.1fs  audio=%s", raw.name, info.width, info.height, info.fps,
             info.duration, info.has_audio)

    voice = work / "voice_enhanced.wav"
    if not (voice.exists() and cfg["pipeline"]["resume"]):
        log.info("• Audio enhancement")
        audio.enhance_voice(raw, voice, cfg, info.has_audio, info.duration)

    tr_path = work / "transcript.json"
    tr = None
    if tr_path.exists() and cfg["pipeline"]["resume"]:
        tr = json.loads(tr_path.read_text(encoding="utf-8")) or None
    elif info.has_audio:
        log.info("• Transcription")
        a16 = extract_audio(raw, work / "speech16k.wav")
        tr = transcribe(raw, a16, cfg, resolve_path(cfg, "models"))
        _dump(tr_path, tr)
    if tr and not tr.get("words"):
        tr = None

    env = audio_envelope(voice)
    kw = cfg["_keywords"]
    log.info("• Cleanup (silence / fillers / stutters / retakes)")
    if tr:
        removed = cleanup.detect_removals(tr, cfg, kw)
        keep = cleanup.keep_from_words(tr, removed, info.duration, cfg)
        emphasis = analyze.word_emphasis(tr, cfg, kw, env)
        scores = analyze.sentence_scores(tr, kw, emphasis, removed)
    else:
        removed, emphasis, scores = {}, [], []
        c = cfg["cleanup"]
        keep = cleanup.keep_from_silence(detect_silence(voice, c["silence_db"], c["silence_min"]),
                                         info.duration, cfg) if info.has_audio else [cleanup.Seg(0, info.duration)]
    if not keep:
        keep = [cleanup.Seg(0, info.duration)]
    st = cleanup.stats(info.duration, keep, removed)
    log.info("  %.1fs -> %.1fs (%.1f%% tighter, %d cuts)", st["source_duration"], st["edited_duration"],
             st["tightened_pct"], st["cuts"])
    _dump(work / "cleanup.json", {"stats": st, "removed": {str(k): v for k, v in removed.items()},
                                  "keep": [[round(s.s, 3), round(s.e, 3)] for s in keep]})

    face_path = work / "face_track.json"
    if face_path.exists() and cfg["pipeline"]["resume"]:
        face = json.loads(face_path.read_text())
    else:
        log.info("• Face tracking")
        face = analyze.face_track(raw, info, cfg["reframe"]["sample_fps"], cfg["reframe"]["smoothing"]) \
            if cfg["reframe"]["face_tracking"] else []
        _dump(face_path, face)

    log.info("• Picture analysis / colour")
    pstats = analyze.picture_stats(raw, info)
    src_chain = color.source_chain(pstats, cfg, resolve_path(cfg, "luts"), pstats["low_res"])
    _dump(work / "picture.json", {"stats": pstats, "chain": src_chain})

    lang = (tr or {}).get("language") or "en"
    return Context(raw, cfg, job, work, out, info, voice, tr, emphasis, scores, keep, face, src_chain, lang)


# --------------------------------------------------------------------------- one edit -> one file
def map_words(ctx: Context, shots: list[motion.Shot]) -> list[tuple[int, float, float]]:
    """Place every transcript word on the output timeline (handles repeated source ranges)."""
    if not ctx.tr:
        return []
    words = ctx.tr["words"]
    res, off = [], 0.0
    for sh in shots:
        for i, w in enumerate(words):
            if w["e"] <= sh.s or w["s"] >= sh.e:
                continue
            mid = (w["s"] + w["e"]) / 2
            if not (sh.s <= mid < sh.e):
                continue
            a = off + max(w["s"] - sh.s, 0)
            b = off + min(w["e"] - sh.s, sh.d)
            res.append((i, a, max(b, a + 0.06)))
        off += sh.d
    return res


def build_edit(ctx: Context, name: str, kind: str, segs: list[cleanup.Seg], title: str | None,
               dst: Path, is_short: bool = False) -> dict:
    cfg = ctx.cfg
    tg = render.choose_target(kind, ctx.info, cfg)
    words = ctx.tr["words"] if ctx.tr else []
    shots = motion.plan_shots(segs, words, ctx.emphasis, ctx.face, cfg, tg.fps)
    if not shots:
        raise ValueError(f"{name}: nothing left to render after cleanup")
    offsets, acc = [], 0.0
    for sh in shots:
        offsets.append(acc)
        acc += round(sh.d * tg.fps) / tg.fps
    duration = acc
    log.info("• %s: %d shots, %.1fs, %s/%s %dx%d", name, len(shots), duration, kind, tg.mode, tg.W, tg.H)

    ewk = ctx.work / name
    parts = render.render_shots(ctx.raw, ctx.voice, ctx.info, shots, tg, ctx.src_chain, cfg, ewk / "shots")
    cut = render.concat(parts, ewk / "cut.mkv")

    # ---- captions + graphics
    placed = map_words(ctx, shots)
    cap_words = [capmod.CapWord(words[i]["w"], a, b, ctx.emphasis[i] if ctx.emphasis else 0)
                 for i, a, b in placed]
    ass_path = None
    g = cfg["graphics"]
    if cfg["captions"]["burn_in"] or g["hook_title"]:
        ab = capmod.AssBuilder(cfg, tg.W, tg.H, "youtube" if kind == "youtube" else "vertical")
        if cap_words and cfg["captions"]["burn_in"]:
            ab.captions(cap_words, cfg["captions"]["position_youtube" if kind == "youtube" else "position_vertical"])
        if g["hook_title"] and title:
            ab.hook_title(title, 0.0, min(g["hook_title_seconds"], duration * 0.3))
        if g["lower_third"] and not is_short and cfg["brand"]["name"]:
            ab.lower_third(cfg["brand"]["name"], cfg["brand"]["role"], min(g["lower_third_at"], duration * 0.2))
        if g["keyword_popups"] and cap_words:
            last, side = -1e9, 1
            hot = sorted(cap_words, key=lambda w: -w.emphasis)
            picks = []
            for w in hot:
                if w.emphasis < 0.75 or w.s < g["hook_title_seconds"] + 0.5 or w.s > duration - 3:
                    continue
                if all(abs(w.s - p.s) > 7 for p in picks):
                    picks.append(w)
                if len(picks) >= max(1, int(duration // 12)):
                    break
            for w in sorted(picks, key=lambda w: w.s):
                ab.keyword_popup(w.text, w.s, side=side)
                side = -side
        if g["end_card"] and duration > 15:
            cta = g["cta_text"].get(ctx.lang, g["cta_text"]["en"])
            ab.end_card(cta, duration - 2.2, duration)
        ass_path = ab.write(ewk / f"{name}.ass")

    # ---- B-roll (only matched clips are inserted; everything is written to the plan)
    broll_plan = []
    if ctx.tr and cfg["broll"]["enabled"]:
        first_out: dict[int, float] = {}
        for i, a, _ in placed:
            first_out.setdefault(i, a)
        broll_plan = brollmod.plan_broll(ctx.tr, ctx.emphasis, first_out, duration, cfg, cfg["_keywords"],
                                         resolve_path(cfg, "broll"))
    inserts = [b for b in broll_plan if b["file"] and cfg["broll"]["insert_matched"]]

    # ---- audio master
    sfx_ev = audio.place_sfx(motion.sfx_cues(shots, offsets, cfg), cfg["audio"]["sfx"]["min_spacing"])
    for b in inserts:
        sfx_ev.append({"t": b["t"], "kind": "whoosh", "offset": -0.2, "gain": -6})
    mood = cfg["audio"]["music"]["mood"]
    if mood == "auto":
        mood = "energetic" if kind != "youtube" or is_short else "inspiring"
    music = audio.pick_music(resolve_path(cfg, "music"), mood, ctx.job + name) \
        if cfg["audio"]["music"]["enabled"] else None
    master = audio.master_mix(cut, ewk / "master.wav", duration, cfg,
                              cfg["audio"]["loudness"]["youtube" if kind == "youtube" else "vertical"],
                              music, sfx_ev, resolve_path(cfg, "sfx"))

    progress = g["progress_bar"]["youtube" if kind == "youtube" else "vertical"]
    render.final_encode(cut, master, ass_path, tg, duration, inserts, cfg, dst, progress)

    # ---- sidecars
    cap_dir = ctx.out / "captions"
    cap_dir.mkdir(exist_ok=True)
    if cap_words and cfg["deliverables"]["captions"]:
        capmod.write_srt(cap_words, cap_dir / f"{dst.stem}.srt")
        capmod.write_vtt(cap_words, cap_dir / f"{dst.stem}.vtt")
        if ass_path:
            shutil.copy(ass_path, cap_dir / f"{dst.stem}.ass")
    if cfg["deliverables"]["project_files"]:
        pdir = ctx.out / "project"
        pdir.mkdir(exist_ok=True)
        project_export.write_fcpxml(shots, ctx.raw, ctx.info, tg.fps, tg.W, tg.H, dst.stem, pdir / f"{dst.stem}.fcpxml")
        project_export.write_edl(shots, ctx.raw, tg.fps, dst.stem, pdir / f"{dst.stem}.edl")
        _dump(pdir / f"{dst.stem}.timeline.json", {
            "target": tg.__dict__, "duration": duration, "shots": [s.to_dict() for s in shots],
            "offsets": offsets, "sfx": sfx_ev, "music": str(music) if music else None,
            "broll": broll_plan, "color_chain": ctx.src_chain})
    thumbs = []
    if cfg["deliverables"]["thumbnails"] and not is_short:
        times = sorted({round(w.s + 0.15, 2) for w in sorted(cap_words, key=lambda w: -w.emphasis)[:4]}) or [duration * 0.3]
        thumbs = render.thumbnails(dst, times, ctx.out / "thumbnails", dst.stem)
    if not cfg["pipeline"]["keep_intermediates"]:
        shutil.rmtree(ewk / "shots", ignore_errors=True)
        cut.unlink(missing_ok=True)
    return {"name": name, "file": str(dst), "kind": kind, "mode": tg.mode, "resolution": f"{tg.W}x{tg.H}",
            "duration": round(duration, 2), "shots": len(shots), "title": title,
            "broll_opportunities": len(broll_plan), "broll_inserted": len(inserts),
            "music": Path(music).name if music else None, "sfx": len(sfx_ev),
            "thumbnails": [str(t) for t in thumbs]}


def with_cold_open(ctx: Context, segs: list[cleanup.Seg]) -> tuple[list[cleanup.Seg], str | None]:
    sc = ctx.cfg["structure"]
    if not ctx.scores:
        return segs, None
    horizon = ctx.info.duration * sc["cold_open_search_window"]
    best = hooks.best_hook(ctx.scores, within=horizon)
    first = ctx.scores[0]
    if not best or best["index"] == first["index"] or best["e"] - best["s"] > sc["cold_open_max"]:
        return segs, (best or first)["text"]
    teaser = hooks.clip_keep(ctx.keep, best["s"], best["e"])
    if not teaser:
        return segs, first["text"]
    for t in teaser:
        t.tags.append("teaser")
    return teaser + segs, best["text"]


# --------------------------------------------------------------------------- whole job
def process(raw: Path, preset: str | None = None, overrides: list[str] | None = None) -> dict:
    raw = Path(raw).resolve()
    side = raw.with_suffix(".yaml")
    cfg = load_config(preset, side if side.exists() else None, overrides)
    t0 = time.time()
    ctx = prepare(raw, cfg)
    d = cfg["deliverables"]
    results = []
    if d["youtube"]:
        segs, title = (with_cold_open(ctx, list(ctx.keep)) if cfg["structure"]["cold_open_youtube"]
                       else (list(ctx.keep), ctx.scores[0]["text"] if ctx.scores else None))
        results.append(build_edit(ctx, "youtube", "youtube", segs, title, ctx.out / f"{ctx.job}_youtube.mp4"))
    if d["vertical"]:
        segs, title = (with_cold_open(ctx, list(ctx.keep)) if cfg["structure"]["cold_open_vertical"]
                       else (list(ctx.keep), ctx.scores[0]["text"] if ctx.scores else None))
        results.append(build_edit(ctx, "vertical", "vertical", segs, title, ctx.out / f"{ctx.job}_vertical.mp4"))
    shorts_meta = []
    if d["shorts"] and ctx.scores:
        plans = hooks.plan_shorts(ctx.scores, ctx.keep, cfg)
        (ctx.out / "shorts").mkdir(exist_ok=True)
        for p in plans:
            segs = hooks.clip_keep(ctx.keep, p.start, p.end)
            if p.teaser:
                segs = hooks.clip_keep(ctx.keep, *p.teaser) + segs
            slug = slugify(" ".join(p.title.split()[:5]))
            dst = ctx.out / "shorts" / f"{ctx.job}_short{p.index:02d}_{slug}.mp4"
            r = build_edit(ctx, f"short{p.index:02d}", "vertical", segs,
                           p.title if cfg["shorts"]["title_card"] else None, dst, is_short=True)
            r.update({"source_range": [round(p.start, 2), round(p.end, 2)], "score": p.score,
                      "reasons": p.reasons, "cold_open": bool(p.teaser)})
            results.append(r)
            shorts_meta.append(r)
    elif d["shorts"]:
        log.warning("Shorts skipped: they need a transcript to find hooks.")

    report = {
        "job": ctx.job, "source": str(raw), "preset": cfg.get("_preset"), "language": ctx.lang,
        "source_info": {"duration": ctx.info.duration, "resolution": f"{ctx.info.width}x{ctx.info.height}",
                        "fps": ctx.info.fps},
        "cleanup": json.loads((ctx.work / "cleanup.json").read_text())["stats"],
        "top_hooks": sorted(ctx.scores, key=lambda s: -s["score"])[:10],
        "deliverables": results, "elapsed_sec": round(time.time() - t0, 1),
    }
    _dump(ctx.out / "report.json", report)
    write_report_md(report, ctx.out / "REPORT.md")
    if not cfg["pipeline"]["keep_intermediates"]:
        for p in ctx.work.glob("*.wav"):
            p.unlink(missing_ok=True)
    log.info("✔ %s done in %.0fs -> %s", ctx.job, report["elapsed_sec"], ctx.out)
    return report


def write_report_md(r: dict, path: Path) -> None:
    c = r["cleanup"]
    lines = [f"# Edit report — {r['job']}", "",
             f"- Source: `{Path(r['source']).name}` · {r['source_info']['resolution']} · "
             f"{r['source_info']['duration']:.1f}s · language **{r['language']}**",
             f"- Preset: {r['preset'] or 'default'} · processing time {r['elapsed_sec']}s",
             f"- Cleanup: {c['source_duration']}s → **{c['edited_duration']}s** "
             f"({c['tightened_pct']}% tighter, {c['cuts']} cuts) · removed words: {c['removed_words'] or '—'}",
             "", "## Deliverables", "", "| File | Format | Duration | Shots | B-roll (inserted/opportunities) |",
             "|---|---|---|---|---|"]
    for d in r["deliverables"]:
        lines.append(f"| `{Path(d['file']).name}` | {d['kind']} {d['resolution']} ({d['mode']}) | "
                     f"{d['duration']}s | {d['shots']} | {d['broll_inserted']}/{d['broll_opportunities']} |")
    if r["top_hooks"]:
        lines += ["", "## Strongest hook lines", ""]
        for h in r["top_hooks"][:5]:
            lines.append(f"- **{h['score']:.2f}** @ {h['s']:.1f}s — {h['text']}  _({', '.join(h['reasons']) or '—'})_")
    lines += ["", "B-roll search queries for open slots are in `project/*.timeline.json` → `broll`.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def default_cfg() -> dict:
    return load_config()


__all__ = ["process", "prepare", "build_edit", "ROOT", "is_hebrew"]
