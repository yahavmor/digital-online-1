# Workflow

## 1. One-time setup
1. Run `scripts/install.sh` (macOS/Linux) or `scripts\install.ps1` (Windows).
2. Copy `config/local.example.yaml` to `config/local.yaml` and set your name, title, brand colours and CTA.
3. Optional: add licensed music to `library/music` (with mood words in the names), B-roll to
   `library/broll`, premium SFX to `library/sfx`, `.cube` LUTs to `library/luts`.
4. Run `factory doctor`, then `factory selftest`.
5. Pick a caption style with `factory preview --style hormozi|mrbeast|clean|karaoke --lang he`.

## 2. Daily use
* **Watch mode:** start `factory watch` (or `START_WATCH.bat` / `start_watch.command`) and drop
  videos into `workspace/input`. Files are picked up once they stop growing, so large copies are safe.
* **One-shot:** run `factory process path/to/video.mp4 --preset reels`, or drag files onto
  `DROP_VIDEOS_HERE.bat`.
* **Batch:** run `factory process` with no files to process everything in `workspace/input` once.

Sources move to `workspace/archive` after success. After a failure they move to `workspace/failed`,
with a full `*.error.log`.

## 3. Per-video direction (sidecar `video.yaml`)
```yaml
preset: sales
brand: {name: "Guest Name", role: "CEO, Company"}
structure: {cold_open_youtube: false}    # e.g. a VSL that must start from the top
cleanup: {max_gap: 0.4}                  # looser pacing for an emotional story
color: {look: moody}
shorts: {count: 10, max_duration: 45}
transcription: {language: en}
```

## 4. Review and finish
* Read `REPORT.md` for the cut summary, top hook lines, and B-roll fill rate.
* To fine-tune in an NLE, import `project/<name>.fcpxml` into Final Cut, Premiere (via FCPXML) or
  DaVinci Resolve. It contains the exact cuts and zoom keyframes, linked to the original media.
  Add the `.srt`/`.ass` captions as a track.
* To re-render after changing settings, run `factory process video.mp4 --set ...`. Cached analysis
  makes this fast. Delete `workspace/processing/<job>` to force a fresh analysis.

## 5. Tuning cheatsheet
| Want | Setting |
|---|---|
| Tighter / looser pacing | `cleanup.max_gap` (0.18 aggressive … 0.45 relaxed) |
| Keep "like / כאילו" | `cleanup.remove_soft_fillers: false` |
| More / less zoom energy | `motion.zoom_levels`, `motion.emphasis_zoom`, `motion.shot_max` |
| Caption look | `captions.style`, `brand.primary/secondary`, `config/caption_styles.yaml` |
| Words to highlight | `config/keywords.yaml → emphasis` |
| Hook detection | `config/keywords.yaml → hook_phrases` |
| Grade | `color.look` or `color.lut` |
| Music level | `audio.music.volume_db` (−22 present … −30 subtle) |
| Faster drafts | `--preset fast` |
