#!/usr/bin/env bash
# Launcher: ./factory.sh <command> [...]   e.g.  ./factory.sh watch --preset reels
cd "$(dirname "$0")"
PY=.venv/bin/python; [[ -x $PY ]] || PY=python3
exec "$PY" -m factory "$@"
