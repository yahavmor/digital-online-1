#!/usr/bin/env bash
# macOS: double-click to start the drop-folder watcher.
cd "$(dirname "$0")"
open workspace/input 2>/dev/null || true
./factory.sh watch
