#!/usr/bin/env bash
# Video Factory installer — macOS / Linux.
#   ./scripts/install.sh            full install (FFmpeg, Python venv, fonts, SFX, Whisper models)
#   ./scripts/install.sh --no-models  skip the ~3 GB speech models (they download on first use)
set -euo pipefail
cd "$(dirname "$0")/.."
MODELS="he en"; [[ "${1:-}" == "--no-models" ]] && MODELS="none"

echo "▶ 1/4 FFmpeg"
if ! command -v ffmpeg >/dev/null; then
  if [[ "$(uname)" == "Darwin" ]]; then
    command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }
    brew install ffmpeg
  elif command -v apt-get >/dev/null; then
    sudo apt-get update && sudo apt-get install -y ffmpeg fontconfig
  elif command -v dnf >/dev/null; then
    sudo dnf install -y ffmpeg fontconfig
  else
    echo "Please install FFmpeg 6+ manually."; exit 1
  fi
fi
ffmpeg -hide_banner -version | head -1

echo "▶ 2/4 Python environment"
PY=${PYTHON:-python3}
$PY -c 'import sys; assert sys.version_info >= (3, 9), "Python 3.9+ required"'
[[ -d .venv ]] || $PY -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt

echo "▶ 3/4 Assets (fonts, SFX kit, models: $MODELS)"
.venv/bin/python -m factory setup --models $MODELS

echo "▶ 4/4 Check"
.venv/bin/python -m factory doctor || true
chmod +x factory.sh start_watch.command 2>/dev/null || true
echo
echo "Done. Drop videos into workspace/input and run:  ./factory.sh watch"
