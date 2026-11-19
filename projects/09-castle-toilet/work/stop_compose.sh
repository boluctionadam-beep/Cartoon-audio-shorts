#!/usr/bin/env bash
# when make.sh reaches the compose stage, stop it: the reviewed shots are re-rendered first, then everything is composed once
until pgrep -f "tools/compose.py . --w" >/dev/null; do sleep 5; done
pkill -f "bash make.sh"; pkill -f "tools/compose.py . --w"; echo "make.sh stopped before compose $(date -u +%H:%M)"
