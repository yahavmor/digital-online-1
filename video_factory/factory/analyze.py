"""Content + picture analysis: emphasis words, hook scores, exposure stats, face track."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from .language import contains_phrase, in_lexicon, is_number, lexicon, norm, phrases
from .media import MediaInfo, run

log = logging.getLogger("factory")


# --------------------------------------------------------------------------- words
def word_emphasis(tr: dict, cfg: dict, kw: dict, envelope: list[float], hop: float = 0.05) -> list[float]:
    """0..1 emphasis per word: keyword, number, loudness peak, long word, pre-pause."""
    lang = tr["language"]
    emph = lexicon(kw, lang, "emphasis")
    ecfg = cfg["captions"]["emphasis"]
    words = tr["words"]
    out = []
    for i, w in enumerate(words):
        score = 0.0
        if ecfg["keywords"] and in_lexicon(w["w"], emph):
            score += 0.55
        if ecfg["numbers"] and is_number(w["w"]):
            score += 0.6
        if len(norm(w["w"])) >= ecfg["long_words"]:
            score += 0.15
        if envelope:
            a, b = int(w["s"] / hop), max(int(w["e"] / hop), int(w["s"] / hop) + 1)
            seg = envelope[a:b] or [0]
            loud = max(seg)
            score += 0.35 * max(0.0, (loud - 0.6) / 0.4)
        if i and w["s"] - words[i - 1]["e"] > 0.35:
            score += 0.1
        if w["w"].endswith("!"):
            score += 0.25
        out.append(round(min(score, 1.0), 3))
    return out


# --------------------------------------------------------------------------- sentences
def sentence_scores(tr: dict, kw: dict, emphasis: list[float], removed: dict | None = None) -> list[dict]:
    """Hook / retention value per sentence (used for shorts + hook selection).

    `text` is the CLEANED sentence (fillers / stutters removed) so titles never show mistakes.
    """
    removed = removed or {}
    lang = tr["language"]
    hooks = phrases(kw, lang, "hook_phrases")
    ctas = phrases(kw, lang, "cta_phrases")
    words = tr["words"]
    res = []
    for k, s in enumerate(tr["sentences"]):
        toks = [norm(w["w"]) for w in words[s["i0"]:s["i1"]]]
        dur = max(s["e"] - s["s"], 0.1)
        sc = 0.0
        reasons = []
        if any(contains_phrase(toks, p) for p in hooks):
            sc += 2.0; reasons.append("hook-phrase")
        if s["text"].rstrip().endswith("?"):
            sc += 1.2; reasons.append("question")
        if any(is_number(w["w"]) for w in words[s["i0"]:s["i1"]]):
            sc += 0.8; reasons.append("number")
        if any(contains_phrase(toks, p) for p in ctas):
            sc -= 1.5; reasons.append("cta")
        em = emphasis[s["i0"]:s["i1"]] or [0]
        sc += 1.5 * (sum(em) / len(em))
        rate = len(toks) / dur
        if 2.2 <= rate <= 4.5:
            sc += 0.5; reasons.append("good-pace")
        if len(toks) < 4:
            sc -= 0.6
        if k < 3:
            sc += 0.3
        clean = " ".join(words[i]["w"] for i in range(s["i0"], s["i1"]) if i not in removed)
        if not clean:
            sc -= 5   # sentence fully cut (e.g. an abandoned retake)
        res.append({"index": k, "score": round(sc, 3), "reasons": reasons, "s": s["s"], "e": s["e"],
                    "text": clean or s["text"]})
    return res


# --------------------------------------------------------------------------- picture
def picture_stats(src: Path, info: MediaInfo, samples: int = 24) -> dict:
    """Average luma, contrast and chroma balance across sampled frames (signalstats)."""
    step = max(info.duration / (samples + 1), 0.5)
    proc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(src), "-vf",
                f"fps=1/{step:.3f},scale=320:-2,signalstats,metadata=print:file=-",
                "-an", "-f", "null", "-"], check=False)
    vals: dict[str, list[float]] = {}
    for key in ("YAVG", "YLOW", "YHIGH", "UAVG", "VAVG", "SATAVG"):
        vals[key] = [float(x) for x in re.findall(rf"lavfi\.signalstats\.{key}=([\d.]+)", proc.stdout)]
    avg = {k: (sum(v) / len(v) if v else None) for k, v in vals.items()}
    noisy = info.height <= 540
    return {"y_avg": avg["YAVG"], "y_low": avg["YLOW"], "y_high": avg["YHIGH"],
            "u_avg": avg["UAVG"], "v_avg": avg["VAVG"], "sat": avg["SATAVG"], "low_res": noisy}


def face_track(src: Path, info: MediaInfo, sample_fps: float, smoothing: float) -> list[tuple[float, float, float, float]]:
    """Return [(t, cx, cy, size)] normalised 0..1 face centre track (largest face), smoothed.

    Falls back to frame centre when OpenCV is missing or no faces are found.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        log.warning("OpenCV not installed — reframe uses frame centre.")
        return []
    if not hasattr(cv2, "CascadeClassifier"):
        log.warning("This OpenCV build has no Haar cascades (OpenCV 5?) — install opencv-python-headless<5. "
                    "Reframe uses frame centre.")
        return []
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    w = 480
    h = int(round(info.height * w / info.width / 2) * 2)
    import subprocess
    proc = subprocess.Popen(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-i", str(src),
                             "-vf", f"fps={sample_fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                            stdout=subprocess.PIPE)
    track, i, frame_bytes = [], 0, w * h
    last = (0.5, 0.42, 0.25)
    while True:
        buf = proc.stdout.read(frame_bytes)
        if len(buf) < frame_bytes:
            break
        img = np.frombuffer(buf, np.uint8).reshape(h, w)
        faces = cascade.detectMultiScale(img, scaleFactor=1.15, minNeighbors=5, minSize=(w // 20, w // 20))
        if len(faces):
            x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            last = ((x + fw / 2) / w, (y + fh / 2) / h, fh / h)
        track.append((i / sample_fps, *last))
        i += 1
    proc.wait()
    if not track:
        return []
    # exponential smoothing = steady virtual camera operator
    out, sx, sy, ss = [], track[0][1], track[0][2], track[0][3]
    for t, x, y, s in track:
        sx = smoothing * sx + (1 - smoothing) * x
        sy = smoothing * sy + (1 - smoothing) * y
        ss = smoothing * ss + (1 - smoothing) * s
        out.append((round(t, 3), round(sx, 4), round(sy, 4), round(ss, 4)))
    return out


def face_at(track: list, t0: float, t1: float) -> tuple[float, float, float]:
    """Average face position over a source-time window."""
    if not track:
        return (0.5, 0.42, 0.25)
    pts = [p for p in track if t0 <= p[0] <= t1] or [min(track, key=lambda p: abs(p[0] - t0))]
    n = len(pts)
    return (sum(p[1] for p in pts) / n, sum(p[2] for p in pts) / n, sum(p[3] for p in pts) / n)
