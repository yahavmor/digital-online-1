# 🎬 Video Factory

**Drop raw footage in → get finished edits out.** A drag-and-drop production line for talking-head,
educational, and sales content in **Hebrew and English**:

| You drop | You get (in `workspace/output/<video>/`) |
|---|---|
| `my_video.mp4` | `my_video_youtube.mp4` — 16:9 master, cleaned, graded, punched-in, captioned, mixed |
| | `my_video_vertical.mp4` — 9:16 full-length version (face-tracked or premium blur-fill) |
| | `shorts/…_short01_<hook>.mp4` … — 3–10 viral clips, each opening on a hook |
| | `captions/*.srt · *.vtt · *.ass` — sidecar captions for every deliverable |
| | `project/*.fcpxml · *.edl · *.timeline.json` — open the edit in Premiere / Resolve / Final Cut |
| | `thumbnails/*.jpg` — candidate frames at the most emphatic moments |
| | `REPORT.md` — what was cut, the strongest hooks, B-roll opportunities |

---

## Quick start

```bash
# macOS / Linux
./scripts/install.sh            # FFmpeg + Python env + fonts + SFX + Hebrew/English speech models
./factory.sh watch              # then drop videos into workspace/input/
```
```powershell
# Windows
.\scripts\install.ps1           # then either:
#   • drag videos onto DROP_VIDEOS_HERE.bat
#   • or double-click START_WATCH.bat and drop files into workspace\input
```
macOS: double-click `start_watch.command`. Docker: see `Dockerfile`.

Verify everything with `./factory.sh doctor` and `./factory.sh selftest`. The self-test generates
synthetic footage, runs the full line on it, and checks every output.

---

## What happens to every video

```
 RAW ─► probe ─► voice enhancement ─► transcription (word-level, he/en) ─► cleanup
        (HPF/LPF, FFT denoise, EQ, de-ess,   ivrit-ai Whisper for Hebrew     silences, dead air, fillers
         compression, limiter)                                               (אממ/um), stutters, retakes
                                                                                  │
   ┌──────────────────────────────────────────────────────────────────────────────┘
   ▼
 analysis ─► emphasis words · hook score per sentence · face track · exposure/white-balance stats
   │
   ├─► YouTube 16:9 ┐
   ├─► Vertical 9:16 ├─► shot plan: beats every 2–5 s, alternating punch-ins, snap-zoom on key
   └─► Shorts ×N    ┘    words, forced re-framing on every jump cut, face-anchored, cold-open teaser
                          │
                          ▼
               per-shot render (colour correction → look/LUT → reframe → zoom → sharpen → vignette)
                          │  frame-quantised cuts, PCM audio → zero A/V drift
                          ▼
               master audio: voice + mood-matched music (side-chain ducked) + whoosh/impact SFX
                          → two-pass EBU R128 loudness (−14 LUFS, −1 dBTP)
                          ▼
               final encode: animated captions, hook title, lower third, keyword pop-ups +
               arrows, progress bar, end-card CTA, B-roll cutaways → H.264 High / AAC, +faststart
```

Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) · Day-to-day use: [docs/WORKFLOW.md](docs/WORKFLOW.md)

---

## Controls

**Presets** set the platform style in one word: `youtube`, `tiktok`, `reels`, `shorts`, `linkedin`, `facebook`, `sales`, `fast` (draft renders).

```bash
./factory.sh process my_video.mp4 --preset reels
./factory.sh watch --preset sales
```

**Per-video sidecar.** Put `my_video.yaml` next to the video to override anything for that video only:
```yaml
preset: tiktok
captions: {style: mrbeast}
shorts: {count: 8}
brand: {name: "דנה כהן", role: "מאמנת עסקית"}
```

**One-off overrides** work on any command: `--set captions.style=clean --set motion.emphasis_zoom=1.4`

**Brand defaults:** copy `config/local.example.yaml` to `config/local.yaml`.

**Style previews in seconds.** No footage needed:
```bash
./factory.sh preview --style hormozi --lang he --kind vertical
```

**Bring your own transcript.** A `my_video.srt` or `my_video.words.json` next to the video skips transcription.

| Folder | Purpose |
|---|---|
| `workspace/input` | drop zone (watched) |
| `workspace/processing` | per-job working files and caches (transcript, face track, cleanup decisions) |
| `workspace/output` | deliverables |
| `workspace/archive` / `failed` | processed sources / failed sources + `*.error.log` |
| `library/music` `broll` `sfx` `luts` `fonts` | your creative assets, matched automatically |
| `config/` | `default.yaml` (every knob, documented), `presets.yaml`, `caption_styles.yaml`, `keywords.yaml` |

---

## Honest limits

* **B-roll:** the factory finds cutaway moments and writes stock-search queries for them. It only
  *inserts* clips that exist in `library/broll`. It does not download stock footage.
* **Music:** it only uses tracks you put in `library/music` (licensing stays in your hands). The
  built-in SFX kit is procedural and royalty-free.
* **Upscaling:** low-res sources get Lanczos scaling, denoise, and sharpening. AI upscalers
  (Real-ESRGAN, Topaz) are not bundled.
* **Speed:** on a 4-core CPU, plan for about 1–2 minutes of processing per minute of footage *per
  deliverable*. Transcription is about 10× faster with an NVIDIA GPU (`transcription.device: cuda`).
* The face tracker is OpenCV Haar, which is robust for single-speaker talking heads. With multiple
  speakers it follows the largest face.
