# Architecture

## Modules (`factory/`)

| Stage | Module | What it does |
|---|---|---|
| Config | `config.py` | Layered config: `default.yaml` < `local.yaml` < preset < sidecar `.yaml` < `--set` |
| I/O | `media.py` | ffmpeg/ffprobe wrappers, loudness measurement, silence detection, energy envelope |
| Audio | `audio.py` | Voice chain (HPF/LPF → afftdn → 4-band EQ → de-esser → compressor → limiter); music pick by mood, side-chain ducking; SFX placement; two-pass `loudnorm` master |
| Speech | `transcribe.py` | faster-whisper with word timestamps (ivrit-ai model for Hebrew), language auto-detect, sidecar `.srt`/`.words.json` import |
| Editorial | `cleanup.py` | Filler / soft-filler / stutter / retake detection → keep-list; silence fallback without a transcript; `Timeline` source↔output mapping |
| Analysis | `analyze.py` | Word emphasis (keywords, numbers, loudness peaks, pauses); sentence hook score; picture stats (`signalstats`); smoothed face track (OpenCV) |
| Language | `language.py` | Normalisation, Hebrew prefix stripping (ו/ה/ב/ל/ש/מ/כ), lexicon & phrase matching |
| Motion | `motion.py` | Beats every 2–5 s, punch-in pattern, snap-zoom on emphasis, forced reframe on jump cuts, frame-grid quantisation, SFX cues |
| Colour | `color.py` | Auto levels / exposure / white balance from stats → skin-protect → look or `.cube` LUT → sharpen/vignette; denoise for low-res |
| Render | `render.py` | Per-shot intermediates (parallel), crop or blur-fill framing, zoom expressions, motion-blur punch, concat, final encode with B-roll overlays, ASS, progress bar |
| Graphics | `captions.py` | ASS generator: word-by-word captions (pop, colour, emphasis), hook title, lower third, keyword pop-up + arrow, end card; SRT/VTT export |
| Hooks | `hooks.py` | Cold-open teaser selection; short-clip window search (hook-first, duration fit, non-overlapping) |
| B-roll | `broll.py` | Cutaway opportunities + search queries; library matching by filename/tags |
| Hand-off | `project_export.py` | FCPXML 1.9 (with zoom keyframes) and CMX3600 EDL |
| Orchestration | `pipeline.py` | `prepare()` (analysis, cached), `build_edit()` (one deliverable), `process()` (whole job + report) |
| Automation | `watch.py` | Drop-folder watcher with file-stability detection, archive/failed routing |
| QA | `validate.py`, `testgen.py`, `tests/` | Delivery QC, synthetic footage with ground truth, unit tests |
| Tools | `doctor.py`, `setup_assets.py`, `preview.py`, `sfx.py`, `cli.py` | Environment check, asset setup, style previews, procedural SFX kit, CLI |

## Key design decisions

* **Frame-quantised cuts and PCM intermediates.** Every cut point is snapped to the output frame
  grid. Shots are rendered to MKV with PCM audio, then stream-copied together. Audio and video stay
  in sync to the sample across hundreds of jump cuts. The validator checks the A/V length delta,
  which is 0 ms in the self-test.
* **Every graphic is ASS/libass.** Captions and motion graphics share one renderer that handles
  Hebrew RTL via fribidi, animates (`\t`, `\move`, `\fad`), and exports as a reusable `.ass` sidecar.
  No browser, After Effects, or GPU is required.
* **Cache-and-resume.** Transcript, face track, cleanup decisions and per-shot renders are cached in
  `workspace/processing/<job>/`. Re-running with another preset re-uses the expensive analysis.
* **Graceful degradation.** No transcript means energy-based cutting without captions or shorts.
  Without OpenCV, framing is centred. No audio gets a silent bed. Without music or B-roll, those are
  skipped and reported.
* **Low-res awareness.** If a 9:16 crop would keep fewer than `reframe.min_crop_width` source pixels,
  the vertical edit switches to a 4:5 foreground over a blurred, darkened background. A 360p crop
  upscaled 5× would look worse than that.

## Caches / artifacts per job (`workspace/processing/<job>/`)

`transcript.json` · `cleanup.json` (kept ranges + removed words with reasons) · `face_track.json` ·
`picture.json` (stats + colour chain) · `<deliverable>/<name>.ass` · `master.wav`.
Set `pipeline.keep_intermediates: true` to keep per-shot renders for debugging.
