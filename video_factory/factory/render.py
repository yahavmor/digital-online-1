"""Frame-accurate segment renderer + final assembly (captions, graphics, B-roll, master audio).

Flow for one deliverable:
  shots ──► per-shot intermediates (colour, reframe, zoom, voice slice)  [parallel]
        ──► lossless concat (MKV, PCM audio — no AAC priming drift)
        ──► master audio (voice + ducked music + SFX, two-pass loudnorm)
        ──► final encode: B-roll overlays + ASS captions/graphics + progress bar
"""
from __future__ import annotations

import hashlib
import logging
import math
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from . import color as colormod
from .media import MediaInfo, escape_filter_path, ffmpeg
from .motion import Shot

log = logging.getLogger("factory")


@dataclass
class Target:
    kind: str        # youtube | vertical
    W: int
    H: int
    fps: int
    mode: str        # crop | fill

    @property
    def aspect(self) -> float:
        return self.W / self.H


def choose_target(kind: str, info: MediaInfo, cfg: dict) -> Target:
    ex = cfg["export"][kind]
    W, H, fps = ex["width"], ex["height"], ex["fps"]
    at = W / H
    mode = "crop"
    if kind == "vertical":
        vm = cfg["reframe"]["vertical_mode"]
        crop_w = min(info.width, info.height * at)
        if vm == "auto":
            mode = "crop" if (info.is_vertical or crop_w >= cfg["reframe"]["min_crop_width"]) else "fill"
        else:
            mode = "fill" if vm in ("blur_fill", "split") else "crop"
    elif info.aspect < at * 0.8:      # vertical source -> landscape master
        mode = "fill"
    return Target(kind, W, H, fps, mode)


# --------------------------------------------------------------------------- zoom expressions
def zoom_expr(sh: Shot) -> str:
    d = max(sh.d, 0.04)
    if sh.emphasis or sh.punch:
        # fast settle from z0 to z1 (snap zoom), then hold with tiny drift
        return f"({sh.z1:.4f}+({sh.z0 - sh.z1:.4f})*exp(-t*14))"
    if abs(sh.z1 - sh.z0) < 1e-4:
        return f"{sh.z0:.4f}"
    return f"({sh.z0:.4f}+({sh.z1 - sh.z0:.4f})*(1-cos(PI*min(t/{d:.4f},1)))/2)"


def window_chain(info: MediaInfo, sh: Shot, out_w: int, out_h: int, face_y: float = 0.40) -> str:
    """Scale-by-zoom then crop an out_w x out_h window anchored on the face."""
    a = out_w / out_h
    base_w = min(info.width, info.height * a)          # widest window of this aspect at zoom 1
    k = out_w / base_w
    z = zoom_expr(sh)
    sw, shh = info.width, info.height
    scale = (f"scale=w='2*trunc({sw}*{k:.6f}*{z}/2+1)':h='2*trunc({shh}*{k:.6f}*{z}/2+1)':"
             f"eval=frame:flags=lanczos")
    cx, cy = sh.cx, sh.cy
    crop = (f"crop={out_w}:{out_h}:x='max(0,min(iw-{out_w},{cx:.4f}*iw-{out_w}/2))':"
            f"y='max(0,min(ih-{out_h},{cy:.4f}*ih-{face_y}*{out_h}))'")
    return f"{scale},{crop}"


def video_graph(info: MediaInfo, sh: Shot, tg: Target, src_chain: str, cfg: dict) -> str:
    base_w = min(info.width, info.height * tg.aspect)
    upscale = tg.W / base_w
    finish = colormod.finish_chain(cfg, upscale)
    blur = ",gblur=sigma=10:steps=2:enable='lt(t,0.07)'" if sh.punch and sh.jump else ""
    head = f"[0:v]setpts=PTS-STARTPTS,fps={tg.fps},{src_chain},format=yuv420p"
    if tg.mode == "crop":
        return f"{head},{window_chain(info, sh, tg.W, tg.H)}{blur},{finish},setsar=1[v]"
    # fill: blurred, darkened cover background + framed foreground
    if tg.kind == "vertical":
        fg_w, fg_h = tg.W, int(round(tg.W / 0.8 / 2) * 2)          # 4:5 foreground
        fg_y = (tg.H - fg_h) // 2 - int(tg.H * 0.06)
        if info.is_vertical:
            fg_w, fg_h, fg_y = tg.W, tg.H, 0
    else:
        fg_h = tg.H
        fg_w = int(round(tg.H * info.aspect / 2) * 2)
        fg_y = 0
    fg_x = (tg.W - fg_w) // 2
    bg = (f"scale={tg.W}:{tg.H}:force_original_aspect_ratio=increase,crop={tg.W}:{tg.H},"
          f"boxblur=luma_radius=40:luma_power=2,eq=brightness=-0.12:saturation=1.2")
    return (f"{head},split=2[a][b];[a]{bg}[bg];"
            f"[b]{window_chain(info, sh, fg_w, fg_h, face_y=0.45)}{blur},{finish}[fg];"
            f"[bg][fg]overlay={fg_x}:{fg_y},setsar=1[v]")


def render_shot(src: Path, voice: Path, info: MediaInfo, sh: Shot, tg: Target, src_chain: str,
                cfg: dict, dst: Path) -> Path:
    if dst.exists() and cfg["pipeline"]["resume"]:
        return dst
    n = max(1, round(sh.d * tg.fps))
    d = n / tg.fps
    cf = min(cfg["audio"]["click_fade"], d / 4)
    ex = cfg["export"]["intermediate"]
    graph = video_graph(info, sh, tg, src_chain, cfg)
    graph += (f";[1:a]asetpts=PTS-STARTPTS,atrim=0:{d:.6f},apad=whole_dur={d:.6f},"
              f"afade=t=in:d={cf:.3f},afade=t=out:st={d - cf:.6f}:d={cf:.3f}[a]")
    tmp = dst.with_suffix(".tmp.mkv")
    ffmpeg("-ss", f"{sh.s:.6f}", "-t", f"{d + 0.5:.6f}", "-i", src,
           "-ss", f"{sh.s:.6f}", "-t", f"{d + 0.5:.6f}", "-i", voice,
           "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-frames:v", str(n),
           "-c:v", "libx264", "-crf", str(ex["crf"]), "-preset", ex["preset"], "-pix_fmt", "yuv420p",
           "-g", str(tg.fps), "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", "-t", f"{d:.6f}", tmp)
    tmp.rename(dst)
    return dst


def render_shots(src: Path, voice: Path, info: MediaInfo, shots: list[Shot], tg: Target,
                 src_chain: str, cfg: dict, work: Path) -> list[Path]:
    work.mkdir(parents=True, exist_ok=True)
    def key(sh: Shot) -> str:   # cache key = everything that affects the pixels/samples of a shot
        raw = f"{sh.s:.4f}|{sh.e:.4f}|{sh.z0:.4f}|{sh.z1:.4f}|{sh.cx:.3f}|{sh.cy:.3f}|{sh.punch}|{sh.jump}|" \
              f"{sh.emphasis}|{tg}|{src_chain}|{cfg['color']}|{cfg['export']['intermediate']}"
        return hashlib.sha1(raw.encode()).hexdigest()[:12]
    jobs = [(i, sh, work / f"shot_{i:04d}_{key(sh)}.mkv") for i, sh in enumerate(shots)]
    par = max(1, int(cfg["export"]["parallel_segments"]))
    done = 0
    results: dict[int, Path] = {}

    def one(job):
        i, sh, dst = job
        return i, render_shot(src, voice, info, sh, tg, src_chain, cfg, dst)

    with ThreadPoolExecutor(max_workers=par) as pool:
        for i, p in pool.map(one, jobs):
            results[i] = p
            done += 1
            if done % 20 == 0 or done == len(jobs):
                log.info("  [%s] rendered %d/%d shots", tg.kind, done, len(jobs))
    return [results[i] for i in range(len(jobs))]


def concat(parts: list[Path], dst: Path) -> Path:
    lst = dst.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve().as_posix()}'\n" for p in parts), encoding="utf-8")
    ffmpeg("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst)
    return dst


# --------------------------------------------------------------------------- final assembly
def final_encode(cut: Path, master_audio: Path, ass: Path | None, tg: Target, duration: float,
                 broll: list[dict], cfg: dict, dst: Path, progress_bar: bool) -> Path:
    ex = cfg["export"][tg.kind]
    inputs = ["-i", str(cut), "-i", str(master_audio)]
    chain = ["[0:v]setpts=PTS-STARTPTS[v0]"]
    last = "v0"
    for k, b in enumerate(broll):
        idx = 2 + k
        inputs += ["-i", str(b["file"])]
        a, d = b["t"], b["d"]
        f = 0.18
        chain.append(
            f"[{idx}:v]trim=0:{d:.3f},setpts=PTS-STARTPTS,fps={tg.fps},"
            f"scale={tg.W}:{tg.H}:force_original_aspect_ratio=increase,crop={tg.W}:{tg.H},"
            f"zoompan=z='min(1+0.0015*on,1.12)':d=1:s={tg.W}x{tg.H}:fps={tg.fps},"
            f"format=yuva420p,fade=t=in:st=0:d={f}:alpha=1,fade=t=out:st={d - f:.3f}:d={f}:alpha=1,"
            f"setpts=PTS+{a:.3f}/TB[b{k}]")
        chain.append(f"[{last}][b{k}]overlay=0:0:eof_action=pass:enable='between(t,{a:.3f},{a + d:.3f})'[v{k + 1}]")
        last = f"v{k + 1}"
    post = []
    if ass is not None:
        fonts = escape_filter_path(Path(cfg["_fonts_dir"]))
        post.append(f"subtitles=filename='{escape_filter_path(ass)}':fontsdir='{fonts}'")
    if progress_bar:
        bh = max(8, tg.H // 160)
        col = cfg["brand"]["primary"].lstrip("#")
        post.append(f"drawbox=x=0:y=ih-{bh}:w='max(2,iw*t/{max(duration, 0.1):.3f})':h={bh}:color=0x{col}@0.95:t=fill")
    post.append(f"format={cfg['export']['pixel_format']}")
    chain.append(f"[{last}]{','.join(post)}[vout]")
    args = [*inputs, "-filter_complex", ";".join(chain), "-map", "[vout]", "-map", "1:a",
            "-c:v", "libx264", "-crf", str(ex["crf"]), "-preset", ex["preset"], "-profile:v", "high",
            "-r", str(tg.fps), "-g", str(tg.fps * 2), "-bf", "2",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-c:a", "aac", "-b:a", ex["audio_bitrate"], "-ar", "48000",
            "-t", f"{duration:.3f}", "-threads", str(cfg["export"]["threads"])]
    if cfg["export"]["faststart"]:
        args += ["-movflags", "+faststart"]
    ffmpeg(*args, dst)
    return dst


def thumbnails(video: Path, times: list[float], out_dir: Path, prefix: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    res = []
    for i, t in enumerate(times, 1):
        p = out_dir / f"{prefix}_thumb_{i:02d}.jpg"
        ffmpeg("-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-q:v", "2", p, check=False)
        if p.exists():
            res.append(p)
    return res


def frames_for(seconds: float, fps: int) -> int:
    return int(math.floor(seconds * fps + 1e-6))
