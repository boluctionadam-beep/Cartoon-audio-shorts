#!/usr/bin/env python3
"""QA of a finished short against the reference targets. Usage: python3 qa.py final.mp4 [voice.wav] [sheet.jpg]"""
import sys, subprocess, re, json
f = sys.argv[1]; voice = sys.argv[2] if len(sys.argv) > 2 else None; sheet = sys.argv[3] if len(sys.argv) > 3 else None
pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", f], capture_output=True, text=True).stdout)
dur = float(pr["format"]["duration"]); v = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
err = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]); LRA = float(re.findall(r"LRA:\s+(-?[\d.]+) LU", err)[-1])
pk = re.findall(r"Peak:\s+(-?[\d.inf]+) dBFS", err)
bl = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-vf", "blackdetect=d=0.1:pix_th=0.06", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
blacks = re.findall(r"black_start:([\d.]+)", bl)
onset = None
if voice:
    s = subprocess.run(["ffmpeg", "-nostats", "-i", voice, "-af", "silencedetect=noise=-40dB:d=0.02", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"silence_end: ([\d.]+)", s); st = re.findall(r"silence_start: ([\d.]+)", s)
    onset = 0.0 if not st or float(st[0]) > 0.01 else float(m[0])
print(f"duration {dur:.2f}s | {v['width']}x{v['height']} @ {v['r_frame_rate']} | loudness {I:.1f} LUFS, LRA {LRA:.1f} LU, true peak {pk[-1] if pk else '?'} dBTP"
      f" | black spans {len(blacks)} {blacks[:5]} | voice onset {onset}")
if sheet:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-vf", "fps=1,scale=180:-1,tile=10x7", "-frames:v", "1", sheet], check=True)
    print("sheet ->", sheet)
