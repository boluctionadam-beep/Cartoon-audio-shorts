#!/usr/bin/env bash
# Full build of short 09 (resumable). Usage: bash make.sh [W H SPP]
set -e
cd "$(dirname "$0")"
W=${1:-1440}; H=${2:-2560}; SPP=${3:-40}
python3 shots09.py plan
python3 shots09.py cards
mkdir -p renders/shots out
for id in $(python3 -c "import shots09; print(' '.join(s['id'] for s in shots09.SHOTS))"); do
  if [ ! -f renders/shots/$id.png ] || [ ! -f renders/shots/$id.json ]; then
    echo "render $id"; python3 shots09.py render $id $W $H $SPP renders/shots/$id.png > renders/shots/$id.log 2>&1
  fi
done
python3 ../../tools/compose.py . --w $W --h $H --fps 60 --jobs 4 --out out/picture.mp4
python3 ../../tools/sound.py .
python3 ../../tools/mix.py audio/voice.wav audio/music.wav audio/sfx.wav -o out/mix.wav
ffmpeg -v error -y -i out/picture.mp4 -i out/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/final.mp4
echo "DONE out/final.mp4"
