#!/usr/bin/env python3
"""Tighten a voiceover: shorten pauses longer than --max to --keep seconds, remove leading silence (voice from ~0.05 s),
then time-stretch by --tempo (pitch preserved, rubberband if available else atempo). Usage:
python3 tighten.py in.(mp3|wav) out.wav [--tempo 1.1] [--max 0.22] [--keep 0.17] [--db -40]"""
import argparse, subprocess, numpy as np, soundfile as sf, tempfile, os
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--tempo", type=float, default=1.1); ap.add_argument("--max", type=float, default=0.22)
ap.add_argument("--keep", type=float, default=0.17); ap.add_argument("--db", type=float, default=-40)
a = ap.parse_args()
tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "in.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.inp, "-ac", "1", "-ar", "48000", wav], check=True)
x, sr = sf.read(wav); hop = int(0.01 * sr)
env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x), hop)])
db = 20 * np.log10(env / env.max()); silent = db < a.db
out = []; i = 0; n = len(silent)
first = int(np.argmax(~silent)); start = max(0, first * hop - int(0.05 * sr)) if first else 0
out.append(np.zeros(int(0.05 * sr)))
i = first
while i < n:
    if silent[i]:
        j = i
        while j < n and silent[j]: j += 1
        dur = (j - i) * 0.01
        seg = x[i * hop:j * hop]
        if j >= n:                                          # trailing silence: keep 0.3 s
            out.append(seg[:int(0.3 * sr)])
        elif dur > a.max:
            k = int(a.keep / 2 * sr); out.append(np.concatenate([seg[:k], seg[-k:]]))
        else:
            out.append(seg)
        i = j
    else:
        j = i
        while j < n and not silent[j]: j += 1
        out.append(x[i * hop:j * hop]); i = j
y = np.concatenate(out); mid = os.path.join(tmp, "tight.wav"); sf.write(mid, y, sr)
filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
af = f"rubberband=tempo={a.tempo}:pitchq=quality:formant=preserved" if "rubberband" in filters else f"atempo={a.tempo}"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mid, "-af", af, "-ar", "48000", a.out], check=True)
d0 = len(x) / sr; d1 = len(y) / sr; d2 = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.out], capture_output=True, text=True).stdout)
print(f"orig {d0:.2f}s -> pauses tightened {d1:.2f}s -> tempo x{a.tempo} {d2:.2f}s  ({af.split('=')[0]})")
