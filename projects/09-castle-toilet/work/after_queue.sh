#!/usr/bin/env bash
# wait for make.sh's render loop to pass s35, then re-render the reviewed shots at full quality
cd "$(dirname "$0")/.."
until [ -f renders/shots/s35.png ] && ! pgrep -f "shots09.py render s35" >/dev/null; do sleep 20; done
echo "queue done, rerendering $*"
bash work/rerender.sh "$@"
echo "AFTERQ DONE"
