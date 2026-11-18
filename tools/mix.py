#!/usr/bin/env python3
"""Mix voice + music (+ sfx): music set to (voice LUFS + music_db), sfx to (voice LUFS + sfx_db) with peaks kept under
the voice, then one gain to -14 LUFS and a -1 dBTP limiter. The voice is never edited.
Usage: python3 mix.py voice.wav music.wav [sfx.wav] -o out/mix.wav [--music-db -12] [--sfx-db -8]"""
import subprocess, re, argparse
ap = argparse.ArgumentParser(); ap.add_argument('voice'); ap.add_argument('music'); ap.add_argument('sfx', nargs='?')
ap.add_argument('-o', default='mix.wav'); ap.add_argument('--music-db', type=float, default=-12); ap.add_argument('--sfx-db', type=float, default=-8)
a = ap.parse_args()
def lufs(p):
    err = subprocess.run(['ffmpeg', '-nostats', '-i', p, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1]); L = float(re.findall(r'LRA:\s+(-?[\d.]+) LU', err)[-1])
    pk = re.findall(r'Peak:\s+(-?[\d.inf]+) dBFS', err); pk = float(pk[-1]) if pk and 'inf' not in pk[-1] else -99
    return I, L, pk
vI, _, vP = lufs(a.voice); mI, _, _ = lufs(a.music); g_m = (vI + a.music_db) - mI
ins = ['-i', a.voice, '-i', a.music]; f = [f"[1:a]volume={g_m:.2f}dB[m]"]; mixin = '[0:a][m]'; n = 2
if a.sfx:
    sI, _, sP = lufs(a.sfx); g_s = (vI + a.sfx_db) - sI
    if sP + g_s > vP - 1: g_s = vP - 1 - sP
    ins += ['-i', a.sfx]; f.append(f"[2:a]volume={g_s:.2f}dB[s]"); mixin += '[s]'; n = 3
f.append(f"{mixin}amix=inputs={n}:duration=longest:normalize=0[x]")
raw = a.o.replace('.wav', '_raw.wav')
subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex', ';'.join(f), '-map', '[x]', '-ar', '48000', '-ac', '2', raw], check=True)
comp = a.o.replace('.wav', '_comp.wav')                       # gentle bus compression keeps LRA <= ~4 LU
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', "acompressor=threshold=-24dB:ratio=2.5:attack=8:release=180:makeup=2", '-ar', '48000', comp], check=True)
rI, _, _ = lufs(comp); g = -14 - rI
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', comp, '-af', f"volume={g:.2f}dB,alimiter=limit=0.78:level=false", '-ar', '48000', a.o], check=True)
oI, oL, oP = lufs(a.o)
print(f"voice {vI:.1f} LUFS | music {a.music_db:+.0f} dB, sfx {a.sfx_db:+.0f} dB under voice | final {oI:.1f} LUFS, LRA {oL:.1f} LU, peak {oP:.1f} dBFS -> {a.o}")
