"""Synthetic test footage with ground-truth transcripts.

No real footage, no network, no speech model needed: every clip carries a `.words.json`
sidecar whose timings match a synthesized "voice" (pitched, enveloped tones per word), so the
whole line — cleanup, captions, hooks, shorts, mixing, rendering — can be exercised and validated.
"""
from __future__ import annotations

import json
import math
import wave
from pathlib import Path

import numpy as np

from .media import ffmpeg

SR = 48000

# (word, seconds) — "_" = pause. Includes fillers, a stutter, a retake, dead air, hooks, numbers.
SCRIPT_EN = [
    ("Most", .30), ("people", .35), ("never", .35), ("learn", .30), ("this", .30), ("secret.", .55), ("_", .6),
    ("um", .45), ("_", .9),
    ("I", .15), ("I", .15), ("made", .30), ("my", .20), ("first", .30), ("million", .50), ("_", .3),
    ("in", .15), ("3", .30), ("years.", .50), ("_", 2.4),                                   # dead air
    ("Here's", .30), ("the", .15), ("thing", .30), ("you", .2), ("need", .3), ("to", .1), ("_", 1.0),  # retake…
    ("Here's", .30), ("the", .15), ("thing", .30), ("you", .2), ("need", .3), ("to", .1), ("know.", .5), ("_", .4),
    ("uh", .40), ("_", .5),
    ("Your", .25), ("clients", .45), ("don't", .30), ("buy", .30), ("products.", .60), ("_", .35),
    ("They", .25), ("buy", .30), ("results.", .60), ("_", .5),
    ("Why", .30), ("does", .20), ("nobody", .40), ("talk", .30), ("about", .25), ("this?", .55), ("_", .6),
    ("The", .15), ("biggest", .40), ("mistake", .45), ("is", .15), ("chasing", .40), ("money", .45),
    ("instead", .35), ("of", .1), ("solving", .4), ("problems.", .6), ("_", 1.8),
    ("So", .2), ("stop", .35), ("guessing.", .5), ("_", .3), ("Build", .3), ("a", .1), ("system", .45),
    ("that", .15), ("brings", .3), ("you", .15), ("clients", .45), ("every", .3), ("single", .3), ("day.", .5), ("_", .5),
    ("Follow", .35), ("for", .15), ("more.", .5), ("_", .8),
]
SCRIPT_HE = [
    ("רוב", .30), ("האנשים", .45), ("לא", .2), ("יודעים", .4), ("את", .2), ("הסוד", .5), ("הזה.", .4), ("_", .6),
    ("אממ", .5), ("_", .8),
    ("הרווחתי", .5), ("את", .15), ("המיליון", .55), ("הראשון", .45), ("שלי", .3), ("תוך", .25), ("3", .3),
    ("שנים.", .5), ("_", 2.2),
    ("הטעות", .45), ("הכי", .25), ("גדולה", .4), ("היא", .2), ("לרדוף", .4), ("אחרי", .3), ("כסף.", .5), ("_", .4),
    ("אהה", .45), ("_", .6),
    ("לקוחות", .5), ("לא", .2), ("קונים", .4), ("מוצרים.", .55), ("_", .3), ("הם", .2), ("קונים", .4),
    ("תוצאות.", .6), ("_", .6),
    ("למה", .3), ("אף", .2), ("אחד", .3), ("לא", .2), ("מדבר", .35), ("על", .15), ("זה?", .45), ("_", 1.6),
    ("תבנו", .35), ("שיטה", .4), ("שמביאה", .4), ("לקוחות", .5), ("כל", .2), ("יום.", .45), ("_", .5),
    ("עקבו", .35), ("לעוד.", .45), ("_", .8),
]


def _voice(script, seed: int = 1) -> tuple[np.ndarray, list[dict]]:
    rng = np.random.default_rng(seed)
    chunks, words, t = [], [], 0.6
    chunks.append(np.zeros(int(SR * 0.6)))
    for w, d in script:
        n = int(SR * d)
        if w == "_":
            chunks.append(rng.normal(0, 0.0015, n))          # room tone
        else:
            tt = np.arange(n) / SR
            f0 = 130 + 60 * rng.random() + (25 if w.endswith(("?", "!")) else 0)
            vib = 4 * np.sin(2 * math.pi * 5 * tt)
            phase = 2 * math.pi * np.cumsum(f0 + vib) / SR
            sig = sum((0.6 / k) * np.sin(k * phase) for k in range(1, 7))
            env = np.minimum(1, tt / 0.03) * np.minimum(1, (d - tt) / 0.05) * (0.8 + 0.2 * np.sin(2 * math.pi * 3 * tt))
            loud = 1.25 if w.rstrip(".?!").lower() in {"secret", "million", "mistake", "money", "הסוד", "המיליון", "כסף"} else 1.0
            chunks.append(0.22 * loud * sig * env + rng.normal(0, 0.0015, n))
            words.append({"w": w, "s": round(t + 0.01, 3), "e": round(t + d - 0.02, 3), "p": 0.99})
        t += d
    chunks.append(np.zeros(int(SR * 0.5)))
    return np.concatenate(chunks).astype(np.float32), words


def _write_wav(x: np.ndarray, path: Path) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def _video(path: Path, wav: Path | None, dur: float, w: int, h: int, label: str, noisy: bool = False) -> None:
    # moving "subject" (bright disc) over a gradient set with a test pattern inset, so zooms,
    # reframes and colour changes are visible in the result
    vf = (f"[0:v]format=yuv420p,eq=brightness=-0.08:saturation=0.7[bg];"
          f"[1:v]scale={w // 4}:{h // 4}[ins];[bg][ins]overlay=W-w-20:20[b2];"
          f"[b2]drawbox=x='{w}*0.5-{h}*0.14+{w}*0.08*sin(t/2)':y={h}*0.22:w={h}*0.28:h={h}*0.36:color=0xE0B090@1:t=fill,"
          f"drawtext=text='{label}':x=20:y=h-th-20:fontsize={h // 18}:fontcolor=white:box=1:boxcolor=black@0.5"
          + (",noise=alls=18:allf=t" if noisy else "") + "[v]")
    args = ["-f", "lavfi", "-i", f"gradients=s={w}x{h}:c0=0x203040:c1=0x806040:d={dur}:speed=0.01",
            "-f", "lavfi", "-i", f"testsrc2=s=320x180:d={dur}"]
    if wav:
        args += ["-i", str(wav)]
    args += ["-filter_complex", vf, "-map", "[v]"]
    if wav:
        args += ["-map", "2:a", "-c:a", "aac", "-b:a", "128k"]
    args += ["-t", f"{dur:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
             "-pix_fmt", "yuv420p", str(path)]
    ffmpeg(*args)


def make_test_inputs(dst: Path, library: Path | None = None) -> list[Path]:
    """Create the validation suite in `dst` (+ optional demo B-roll / music in `library`)."""
    dst.mkdir(parents=True, exist_ok=True)
    tmp = dst / "_gen"
    tmp.mkdir(exist_ok=True)
    made = []
    cases = [
        ("t01_talk_en_landscape", SCRIPT_EN, 1280, 720, "en", False, True),
        ("t02_talk_he_lowres", SCRIPT_HE, 640, 360, "he", True, True),
        ("t03_talk_en_vertical", SCRIPT_EN[:40], 720, 1280, "en", False, True),
        ("t04_no_transcript", SCRIPT_EN[:30], 1280, 720, None, False, False),
    ]
    for name, script, w, h, lang, noisy, with_words in cases:
        x, words = _voice(script, seed=len(name))
        wav = tmp / f"{name}.wav"
        _write_wav(x, wav)
        dur = len(x) / SR
        p = dst / f"{name}.mp4"
        _video(p, wav, dur, w, h, name, noisy)
        if with_words:
            (dst / f"{name}.words.json").write_text(json.dumps({"language": lang, "words": words},
                                                               ensure_ascii=False, indent=1), encoding="utf-8")
        else:
            (dst / f"{name}.yaml").write_text("transcription:\n  backend: none\n", encoding="utf-8")
        made.append(p)
    # silent video edge case
    p = dst / "t05_no_audio.mp4"
    _video(p, None, 6.0, 1280, 720, "t05_no_audio")
    (dst / "t05_no_audio.yaml").write_text("transcription:\n  backend: none\n", encoding="utf-8")
    made.append(p)

    if library:
        (library / "broll").mkdir(parents=True, exist_ok=True)
        (library / "music").mkdir(parents=True, exist_ok=True)
        ffmpeg("-f", "lavfi", "-i", "mandelbrot=s=640x360:r=30", "-t", "4", "-c:v", "libx264",
               "-preset", "veryfast", "-pix_fmt", "yuv420p", library / "broll" / "money_cash_demo.mp4")
        ffmpeg("-f", "lavfi", "-i", "life=s=640x360:r=30:mold=10:ratio=0.1:death_color=#203040:life_color=#FFD400",
               "-t", "4", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
               library / "broll" / "clients_handshake_demo.mp4")
        # simple synthetic pad as a placeholder music bed
        ffmpeg("-f", "lavfi", "-i",
               "aevalsrc='0.2*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.25*t))+0.15*sin(2*PI*277.2*t)+0.12*sin(2*PI*329.6*t)"
               "+0.1*sin(2*PI*110*t)*(0.5+0.5*sin(2*PI*2*t))':s=48000:d=20",
               "-ac", "2", library / "music" / "energetic_demo_pad.wav")
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return made
