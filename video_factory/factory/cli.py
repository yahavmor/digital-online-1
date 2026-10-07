"""Command line entry point:  python -m factory <command>   (or ./factory.sh / factory.bat)."""
from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

from .config import CONFIG_DIR, ROOT, load_config, resolve_path


def _setup_logging(verbose: bool, logfile: Path | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if logfile:
        logfile.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(logfile, encoding="utf-8"))
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO,
                        format="%(asctime)s %(message)s", datefmt="%H:%M:%S", handlers=handlers, force=True)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def cmd_process(a):
    from .pipeline import process
    from .watch import handle
    files = [Path(f) for f in a.files] or None
    if files is None:
        from .watch import run_once
        reps = run_once(a.preset, a.set)
        print(f"Processed {len(reps)} file(s) from the input folder.")
        return 0 if all("error" not in r for r in reps) else 1
    rc = 0
    for f in files:
        if a.archive:
            r = handle(f.resolve(), load_config(a.preset, None, a.set), a.preset, a.set)
            rc |= int("error" in r)
        else:
            process(f, a.preset, a.set)
    return rc


def cmd_watch(a):
    from .watch import watch
    watch(a.preset, a.set)


def cmd_doctor(a):
    from .doctor import doctor
    return doctor()


def cmd_setup(a):
    from .setup_assets import setup
    return setup(models=a.models, fonts=not a.no_fonts)


def cmd_test_inputs(a):
    from .testgen import make_test_inputs
    dst = Path(a.dest) if a.dest else resolve_path(load_config(), "input")
    lib = Path(a.library) if a.library else None
    for p in make_test_inputs(dst, lib):
        print("created", p)


def cmd_validate(a):
    from .validate import validate_job
    cfg = load_config()
    dirs = [Path(d) for d in a.jobs] or sorted(p for p in resolve_path(cfg, "output").iterdir() if p.is_dir())
    rc = 0
    for d in dirs:
        qc = validate_job(d, deep=not a.quick)
        print(f"\n■ {d.name}\n{qc.table()}")
        rc |= 0 if qc.ok else 1
    return rc


def cmd_selftest(a):
    """End-to-end: generate synthetic footage, run the full line on it, QC every output."""
    from .testgen import make_test_inputs
    from .validate import validate_job
    from .watch import run_once
    run_dir = ROOT / "test_run"
    if run_dir.exists() and not a.keep:
        shutil.rmtree(run_dir)
    sets = [f"paths.input={run_dir / 'input'}", f"paths.output={run_dir / 'output'}",
            f"paths.processing={run_dir / 'processing'}", f"paths.archive={run_dir / 'archive'}",
            f"paths.failed={run_dir / 'failed'}", f"paths.broll={run_dir / 'library/broll'}",
            f"paths.music={run_dir / 'library/music'}", f"paths.sfx={run_dir / 'library/sfx'}",
            "shorts.count=2", "shorts.min_duration=8", "shorts.max_duration=30", "shorts.target_duration=15",
            "brand.name=Test Presenter", "brand.role=Video Factory QA"] + (a.set or [])
    if not (run_dir / "input").exists() or not a.keep:
        make_test_inputs(run_dir / "input", run_dir / "library")
    reps = run_once(a.preset or "fast", sets)
    failed = [r for r in reps if "error" in r]
    rc = 0
    for r in reps:
        if "error" in r:
            print(f"\n✖ {r['job']}: {r['error']}")
            continue
        qc = validate_job(run_dir / "output" / r["job"], deep=True)
        print(f"\n■ {r['job']}\n{qc.table()}")
        rc |= 0 if qc.ok else 1
    print(f"\nSELFTEST {'PASSED' if rc == 0 and not failed else 'FAILED'} — outputs in {run_dir / 'output'}")
    return 1 if failed else rc


def cmd_preview(a):
    from .preview import preview
    out = Path(a.out or ROOT / "workspace" / "previews" / f"{a.style or 'default'}_{a.lang}_{a.kind}.png")
    print(preview(a.style, a.lang, a.kind, out, a.preset, Path(a.background) if a.background else None))


def cmd_presets(a):
    import yaml
    presets = yaml.safe_load((CONFIG_DIR / "presets.yaml").read_text(encoding="utf-8"))
    styles = yaml.safe_load((CONFIG_DIR / "caption_styles.yaml").read_text(encoding="utf-8"))
    print("Presets:        ", ", ".join(presets))
    print("Caption styles: ", ", ".join(styles))
    from .color import LOOKS
    print("Colour looks:   ", ", ".join(LOOKS))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="factory", description="Automated video editing factory")
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp):
        sp.add_argument("--preset", help="youtube | tiktok | reels | shorts | linkedin | facebook | sales | fast")
        sp.add_argument("--set", action="append", metavar="KEY=VALUE",
                        help="override any config value, e.g. --set captions.style=mrbeast")

    sp = sub.add_parser("process", help="process given files (or everything in the input folder)")
    sp.add_argument("files", nargs="*")
    sp.add_argument("--archive", action="store_true", help="move sources to archive/failed afterwards")
    common(sp)
    sp.set_defaults(fn=cmd_process)

    sp = sub.add_parser("watch", help="watch the input folder and process new drops forever")
    common(sp)
    sp.set_defaults(fn=cmd_watch)

    sub.add_parser("doctor", help="check dependencies, fonts, models").set_defaults(fn=cmd_doctor)

    sp = sub.add_parser("setup", help="download fonts / models, build the SFX kit")
    sp.add_argument("--models", nargs="*", default=None, help="he en | none (default: he en)")
    sp.add_argument("--no-fonts", action="store_true")
    sp.set_defaults(fn=cmd_setup)

    sp = sub.add_parser("test-inputs", help="generate synthetic test footage with ground-truth transcripts")
    sp.add_argument("--dest")
    sp.add_argument("--library", help="also create demo B-roll + music here")
    sp.set_defaults(fn=cmd_test_inputs)

    sp = sub.add_parser("validate", help="QC finished jobs in the output folder")
    sp.add_argument("jobs", nargs="*")
    sp.add_argument("--quick", action="store_true", help="skip loudness / black-frame scans")
    sp.set_defaults(fn=cmd_validate)

    sp = sub.add_parser("selftest", help="end-to-end run on synthetic footage + QC")
    sp.add_argument("--keep", action="store_true", help="reuse existing test_run folder")
    common(sp)
    sp.set_defaults(fn=cmd_selftest)

    sp = sub.add_parser("preview", help="render a caption/graphics style contact sheet (PNG) in seconds")
    sp.add_argument("--style", help="hormozi | mrbeast | clean | karaoke")
    sp.add_argument("--lang", default="he", choices=["he", "en"])
    sp.add_argument("--kind", default="vertical", choices=["vertical", "youtube"])
    sp.add_argument("--background", help="optional video/image to preview over")
    sp.add_argument("--out")
    sp.add_argument("--preset")
    sp.set_defaults(fn=cmd_preview)

    sub.add_parser("presets", help="list presets / caption styles / looks").set_defaults(fn=cmd_presets)

    a = p.parse_args(argv)
    log_file = ROOT / "workspace" / "factory.log" if a.cmd in ("process", "watch") else None
    _setup_logging(a.verbose, log_file)
    return int(a.fn(a) or 0)


if __name__ == "__main__":
    sys.exit(main())
