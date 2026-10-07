"""Voice enhancement, music bed with ducking, SFX placement and loudness mastering."""
from __future__ import annotations

import logging
import random
from pathlib import Path

from .media import ffmpeg, measure_loudness

log = logging.getLogger("factory")

MOOD_WORDS = {
    "energetic": ["energetic", "upbeat", "hype", "edm", "trap", "fast"],
    "inspiring": ["inspiring", "uplifting", "motivational", "hope", "epic"],
    "dramatic": ["dramatic", "cinematic", "tension", "dark", "trailer"],
    "calm": ["calm", "chill", "lofi", "ambient", "soft", "piano"],
    "corporate": ["corporate", "business", "tech", "clean", "minimal"],
}


def voice_chain(cfg: dict) -> str:
    a = cfg["audio"]
    if not a["enhance"]:
        return "anull"
    f = [f"highpass=f={a['highpass_hz']}", f"lowpass=f={a['lowpass_hz']}"]
    if a["denoise"]:
        f.append(f"afftdn=nr={a['denoise_nr']}:nf=-40:tn=1")
    for freq, q, gain in a["eq"]:
        f.append(f"equalizer=f={freq}:t=q:w={q}:g={gain}")
    if a["deesser"]:
        f.append("deesser=i=0.4:m=0.5:f=0.5")
    c = a["compressor"]
    f.append(f"acompressor=threshold={c['threshold']}dB:ratio={c['ratio']}:attack={c['attack']}:"
             f"release={c['release']}:makeup={c['makeup']}dB")
    f.append("alimiter=limit=0.95:level=disabled")
    return ",".join(f)


def enhance_voice(src: Path, dst: Path, cfg: dict, has_audio: bool, duration: float) -> Path:
    """Full-length enhanced voice track (48 kHz stereo WAV) — cut later with the video."""
    if not has_audio:
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{duration:.3f}", str(dst))
        return dst
    ffmpeg("-i", src, "-vn", "-af", voice_chain(cfg) + ",aresample=48000", "-ac", "2",
           "-c:a", "pcm_s16le", dst)
    return dst


def pick_music(music_dir: Path, mood: str, seed: str) -> Path | None:
    files = [p for p in music_dir.glob("**/*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".flac", ".ogg")]
    if not files:
        return None
    if mood and mood != "auto":
        keys = MOOD_WORDS.get(mood, [mood])
        tagged = [p for p in files if any(k in str(p).lower() for k in keys)]
        files = tagged or files
    random.Random(seed).shuffle(files)
    return files[0]


def pick_sfx(sfx_dir: Path, kind: str) -> Path | None:
    files = sorted(p for p in sfx_dir.glob(f"{kind}*") if p.suffix.lower() in (".wav", ".mp3"))
    return files[0] if files else None


def place_sfx(events: list[dict], min_spacing: float) -> list[dict]:
    """Thin out SFX so they support the edit rather than clutter it."""
    out, last = [], -1e9
    for ev in sorted(events, key=lambda e: (e["t"], -e.get("priority", 0))):
        if ev["t"] - last >= min_spacing:
            out.append(ev)
            last = ev["t"]
    return out


def master_mix(voice: Path, dst: Path, duration: float, cfg: dict, target: dict,
               music: Path | None, sfx_events: list[dict], sfx_dir: Path) -> Path:
    """voice + ducked music + SFX -> two-pass loudnorm master (AAC-ready WAV)."""
    a = cfg["audio"]
    inputs = ["-i", str(voice)]
    graph = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][vsc]"]
    mix = ["[v]"]
    idx = 1
    if music and a["music"]["enabled"]:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        m = a["music"]
        fo = max(duration - m["fade_out"], 0)
        graph.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{duration:.3f},"
                     f"volume={m['volume_db']}dB,afade=t=in:d={m['fade_in']},afade=t=out:st={fo:.3f}:d={m['fade_out']}[mus]")
        if m["duck"]:
            graph.append("[mus][vsc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[musd]")
            mix.append("[musd]")
        else:
            graph.append("[vsc]anullsink")
            mix.append("[mus]")
        idx += 1
    else:
        graph.append("[vsc]anullsink")
    if a["sfx"]["enabled"]:
        for ev in sfx_events:
            f = pick_sfx(sfx_dir, ev["kind"])
            if not f:
                continue
            inputs += ["-i", str(f)]
            delay = int(max(ev["t"] + ev.get("offset", 0), 0) * 1000)
            graph.append(f"[{idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                         f"volume={a['sfx']['volume_db'] + ev.get('gain', 0)}dB,adelay={delay}|{delay}[s{idx}]")
            mix.append(f"[s{idx}]")
            idx += 1
    graph.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{duration:.3f}[mix]")
    pre = dst.with_suffix(".premaster.wav")
    ffmpeg(*inputs, "-filter_complex", ";".join(graph), "-map", "[mix]", "-c:a", "pcm_s16le", pre)

    meas = measure_loudness(pre)
    ln = (f"loudnorm=I={target['I']}:TP={target['TP']}:LRA={target['LRA']}:"
          f"measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:measured_LRA={meas['input_lra']}:"
          f"measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true")
    ffmpeg("-i", pre, "-af", ln + ",aresample=48000", "-c:a", "pcm_s16le", dst)
    pre.unlink(missing_ok=True)
    return dst
