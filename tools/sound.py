#!/usr/bin/env python3
"""Synthesised SFX + music for the shorts (numpy, 48 kHz), vocal reactions from the local Kokoro voice.
  python3 sound.py PROJECT_DIR      -> PROJECT/audio/sfx.wav, PROJECT/audio/music.wav (aligned to work/timeline.json)"""
import json, math, os, random, sys
import numpy as np, soundfile as sf
SR = 48000
R = np.random.default_rng(7)


def env(n, a=0.005, d=0.2, sus=0.0, curve=4.0):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) * curve / max(d, 1e-3))
    return np.maximum(e, sus * (t < n / SR * 0.8))


def lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)


def bp(x, f0, q=4.0):
    from scipy.signal import iirpeak, lfilter
    b, a = iirpeak(min(f0, SR / 2 - 100) / (SR / 2), q); return lfilter(b, a, x)


def hp(x, fc):
    from scipy.signal import butter, lfilter
    b, a = butter(2, fc / (SR / 2), "high"); return lfilter(b, a, x)


def noise(d): return R.standard_normal(int(d * SR))


def sine(f, d, ph=0.0):
    t = np.arange(int(d * SR)) / SR
    f = np.broadcast_to(np.asarray(f, float), t.shape) if np.ndim(f) else np.full(t.shape, float(f))
    return np.sin(2 * math.pi * np.cumsum(f) / SR + ph)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9; return x / m * peak


# ------------------------------------------------------------------ SFX library
def whoosh(d=0.6):
    n = noise(d); t = np.linspace(0, 1, len(n)); f = 300 + 2500 * np.sin(np.pi * t)
    y = np.zeros_like(n)
    for k in range(0, len(n), 2400):
        seg = n[k:k + 2400]; y[k:k + 2400] = bp(seg, f[k], 1.5)
    return norm(y * np.sin(np.pi * t) ** 1.5, 0.6)


def thud(d=0.5, f=70):
    t = np.arange(int(d * SR)) / SR; y = np.sin(2 * math.pi * (f * t - 30 * t * t)) * np.exp(-t * 9) + 0.3 * lp(noise(d), 400) * np.exp(-t * 25)
    return norm(y, 0.9)


def boom(d=1.6):
    t = np.arange(int(d * SR)) / SR
    y = np.sin(2 * math.pi * (55 * t - 12 * t * t)) * np.exp(-t * 3.5) + 0.7 * lp(noise(d), 600) * np.exp(-t * 4) + 0.3 * lp(noise(d), 3000) * np.exp(-t * 12)
    return norm(y, 0.95)


def clang(d=1.2, f=420):
    t = np.arange(int(d * SR)) / SR; y = sum(np.sin(2 * math.pi * f * r * t) * np.exp(-t * (3 + 2 * i)) / (i + 1) for i, r in enumerate((1, 2.76, 5.4, 8.93)))
    return norm(y + 0.2 * hp(noise(d), 3000) * np.exp(-t * 40), 0.7)


def hammer(): return norm(np.concatenate([clang(0.5, 900) * 0.6 + np.pad(thud(0.5, 120), (0, 0))[:int(0.5 * SR)], np.zeros(int(0.05 * SR))]), 0.7)


def creak(d=1.0, f0=90):
    t = np.arange(int(d * SR)) / SR; f = f0 + 25 * np.sin(2 * math.pi * 1.3 * t) + 40 * t
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1; pulses = (np.sin(2 * math.pi * 14 * t) > 0.6) * 1.0
    y = bp(saw * (0.4 + pulses), 700, 3) + bp(saw, 1400, 5) * 0.5
    return norm(y * np.sin(np.pi * t / d) ** 0.5, 0.6)


def scrape(d=0.7):
    t = np.arange(int(d * SR)) / SR; n = bp(noise(d), 1800, 1.2) * (0.5 + 0.5 * np.abs(np.sin(2 * math.pi * 6 * t)))
    return norm(n * np.sin(np.pi * t / d), 0.5)


def drip():
    d = 0.25; t = np.arange(int(d * SR)) / SR; f = 900 + 1800 * np.exp(-t * 30)
    return norm(sine(f, d) * np.exp(-t * 22), 0.5)


def pop():
    d = 0.18; t = np.arange(int(d * SR)) / SR; f = 300 + 900 * t / d
    return norm(sine(f, d) * np.exp(-t * 25) + 0.4 * hp(noise(d), 2000) * np.exp(-t * 80), 0.8)


def splash(d=0.9):
    t = np.arange(int(d * SR)) / SR; y = hp(noise(d), 800) * np.exp(-t * 5) * (1 + 0.5 * np.sin(2 * math.pi * 23 * t))
    return norm(y + 0.5 * lp(noise(d), 500) * np.exp(-t * 8), 0.7)


def flies(d=1.6):
    t = np.arange(int(d * SR)) / SR; y = np.zeros_like(t)
    for k in range(3):
        f = 190 + 25 * k + 18 * np.sin(2 * math.pi * (0.7 + 0.3 * k) * t + k)
        saw = 2 * ((np.cumsum(f) / SR) % 1) - 1; y += bp(saw, 1100 + 200 * k, 2) * (0.6 + 0.4 * np.sin(2 * math.pi * (1.1 + k * 0.4) * t + k))
    return norm(y * np.minimum(1, np.minimum(t / 0.2, (d - t) / 0.3)), 0.35)


def birds(d=1.6):
    y = np.zeros(int(d * SR))
    for k in range(5):
        s = int(R.uniform(0, d - 0.3) * SR); dd = 0.12; t = np.arange(int(dd * SR)) / SR
        f = 3200 + 1500 * np.sin(2 * math.pi * 18 * t); y[s:s + len(t)] += sine(f, dd) * np.sin(np.pi * t / dd)
    return norm(y, 0.3)


def wind(d=2.5):
    t = np.arange(int(d * SR)) / SR; y = lp(noise(d), 500) * (0.6 + 0.4 * np.sin(2 * math.pi * 0.4 * t))
    return norm(y * np.minimum(1, np.minimum(t / 0.5, (d - t) / 0.5)), 0.4)


def drums(d=2.2, bpm=120):
    y = np.zeros(int(d * SR)); beat = 60 / bpm
    for i in range(int(d / beat)):
        s = int(i * beat * SR); k = thud(0.3, 90) if i % 2 == 0 else norm(hp(noise(0.2), 1200) * np.exp(-np.arange(int(0.2 * SR)) / SR * 30), 0.5)
        y[s:s + len(k)] += k[:len(y) - s]
    return norm(y, 0.8)


def march(d=2.2):
    y = np.zeros(int(d * SR))
    for i in range(int(d / 0.25)):
        s = int((i * 0.25 + R.uniform(0, 0.04)) * SR); k = lp(noise(0.12), 900) * np.exp(-np.arange(int(0.12 * SR)) / SR * 40)
        y[s:s + len(k)] += k[:len(y) - s]
    return norm(y, 0.5)


def catapult(): return norm(np.concatenate([creak(0.5, 70), whoosh(0.7)]), 0.7)


def collapse(d=2.2):
    t = np.arange(int(d * SR)) / SR; y = lp(noise(d), 900) * np.exp(-t * 1.8) + 0.6 * boom(d)
    for k in range(25):
        s = int(R.uniform(0.1, d - 0.3) * SR); c = thud(0.25, R.uniform(80, 200)) * R.uniform(0.2, 0.5); y[s:s + len(c)] += c[:len(y) - s]
    return norm(y, 0.95)


def boing(d=0.6):
    t = np.arange(int(d * SR)) / SR; f = 180 + 120 * np.sin(2 * math.pi * 9 * t) * np.exp(-t * 4)
    return norm(sine(f, d) * np.exp(-t * 4), 0.6)


def ding(f=1320):
    d = 0.7; t = np.arange(int(d * SR)) / SR
    return norm((np.sin(2 * math.pi * f * t) + 0.3 * np.sin(2 * math.pi * f * 2.01 * t)) * np.exp(-t * 6), 0.5)


def sting():
    d = 1.0; t = np.arange(int(d * SR)) / SR; y = np.zeros_like(t)
    for f in (146.8, 174.6, 220.0, 293.7):
        saw = 2 * ((f * t) % 1) - 1; y += lp(saw, 1800)
    return norm(y * np.exp(-t * 2.5) * np.minimum(1, t / 0.02), 0.6)


def fanfare():
    notes = [(392, 0.12), (392, 0.12), (392, 0.12), (523.3, 0.5)]; out = []
    for f, d in notes:
        t = np.arange(int(d * SR)) / SR; saw = sum(2 * ((f * h * t) % 1) - 1 for h in (1, 1.003)) / 2
        y = lp(saw, 2200) * np.minimum(1, t / 0.015) * np.exp(-t * (1.5 if d > 0.3 else 8)); out.append(y); out.append(np.zeros(int(0.02 * SR)))
    return norm(np.concatenate(out), 0.6)


def stomach(d=1.0):
    t = np.arange(int(d * SR)) / SR; f = 60 + 40 * np.sin(2 * math.pi * 3 * t)
    return norm(bp(sine(f, d) + 0.4 * noise(d), 180, 2) * np.sin(np.pi * t / d), 0.5)


def squish(d=0.5):
    t = np.arange(int(d * SR)) / SR; f = 400 - 300 * t / d
    return norm((sine(f, d) * 0.5 + bp(noise(d), 600, 3)) * np.exp(-t * 6), 0.6)


def melt(d=1.6):
    y = np.zeros(int(d * SR))
    for k in range(6):
        s = int(k * d / 6 * SR); c = squish(0.4) * 0.7; y[s:s + len(c)] += c[:len(y) - s]
    return norm(y, 0.6)


def dig():
    return norm(np.concatenate([scrape(0.25) * 0.6 + thud(0.25, 150)[:int(0.25 * SR)] * 0.5]), 0.6)


def choir(d=1.4):
    t = np.arange(int(d * SR)) / SR; y = np.zeros_like(t)
    for f in (261.6, 329.6, 392.0, 523.3):
        saw = 2 * (((f + 1.5 * np.sin(2 * math.pi * 5 * t)) * t) % 1) - 1; y += bp(saw, 700, 2) + 0.6 * bp(saw, 1150, 3)
    return norm(y * np.minimum(1, np.minimum(t / 0.15, (d - t) / 0.4)), 0.4)


_K = None


def voice(text, voices, speed=1.15, gain=0.6):
    """crowd/vocal reactions with the local Kokoro voice, several voices layered with small offsets"""
    global _K
    try:
        from kokoro_onnx import Kokoro
        d = os.path.expanduser("~/.cache/kokoro")
        if _K is None: _K = Kokoro(f"{d}/kokoro-v1.0.onnx", f"{d}/voices-v1.0.bin")
    except Exception:
        return np.zeros(int(0.5 * SR))
    from scipy.signal import resample_poly
    out = None
    for i, v in enumerate(voices):
        a, sr = _K.create(text if isinstance(text, str) else text[i % len(text)], voice=v, speed=speed * R.uniform(0.95, 1.08), lang="en-us")
        a = resample_poly(a, SR, sr); off = int(R.uniform(0, 0.12) * SR); a = np.concatenate([np.zeros(off), a])
        out = a if out is None else (np.pad(out, (0, max(0, len(a) - len(out)))) + np.pad(a, (0, max(0, len(out) - len(a)))) * 0.8)
    return norm(out, gain)


LIB = {
    "whoosh": lambda: whoosh(), "thud": lambda: thud(), "boom": lambda: boom(), "clang": lambda: clang(), "hammer": hammer,
    "gate_creak": lambda: creak(1.3, 70), "scrape": lambda: scrape(), "drip": drip, "pop": pop, "splash": lambda: splash(), "flies": lambda: flies(),
    "birds": lambda: birds(), "wind": lambda: wind(), "drums": lambda: drums(), "march": lambda: march(), "catapult": catapult,
    "collapse": lambda: collapse(), "boing": lambda: boing(), "ding": lambda: ding(), "sting": sting, "fanfare": fanfare, "stomach": lambda: stomach(),
    "squish": lambda: squish(), "melt": lambda: melt(), "dig": dig, "choir": lambda: choir(), "drop": lambda: whoosh(0.4) * 0.6,
    "laugh": lambda: voice("Ha ha ha ha!", ["am_michael", "am_adam"], 1.1, 0.55),
    "cheer": lambda: voice(["Hooray!", "Yeah!", "Hooray!"], ["am_puck", "am_fenrir", "am_adam", "am_echo", "am_eric", "am_liam"], 1.1, 0.6),
    "charge": lambda: voice(["Charge!", "Go go go!", "Aaah!"], ["am_fenrir", "am_puck", "am_onyx", "am_eric", "am_liam"], 1.15, 0.6),
    "panic": lambda: voice(["Run!", "Help!", "They're inside!"], ["am_adam", "am_echo", "am_michael"], 1.2, 0.55),
    "scream": lambda: voice("Aaaaah!", ["am_eric", "am_puck"], 1.0, 0.5),
    "grunt": lambda: voice("Hnngh!", ["am_fenrir"], 1.0, 0.5),
    "bleh": lambda: voice("Eww.", ["am_puck"], 1.0, 0.5),
    "crowd_murmur": lambda: lp(noise(2.0), 700) * 0.15,
}
VOCAL = {"laugh", "cheer", "charge", "panic", "scream", "grunt", "bleh"}


def place(track, clip, t, gain=1.0):
    s = int(max(0, t) * SR); e = min(len(track), s + len(clip))
    if e > s: track[s:e] += clip[:e - s] * gain


# ------------------------------------------------------------------ music (Karplus-Strong lute + bass + percussion)
def pluck(f, d=0.6, bright=0.5):
    n = int(SR / f); buf = R.uniform(-1, 1, n); out = np.zeros(int(d * SR)); i = 0
    for k in range(len(out)):
        out[k] = buf[i]; nxt = (i + 1) % n; buf[i] = 0.996 * (bright * buf[i] + (1 - bright) * buf[nxt]) if False else 0.4985 * (buf[i] + buf[nxt]); i = nxt
    return out


def pluck_fast(f, d=0.6):
    """vectorised KS approximation: decaying harmonic series (much faster)"""
    t = np.arange(int(d * SR)) / SR; y = np.zeros_like(t)
    for h in range(1, 9):
        y += np.sin(2 * math.pi * f * h * t + R.uniform(0, 6)) * np.exp(-t * (2.5 + 1.4 * h)) / h ** 1.1
    return y * np.minimum(1, t / 0.003)


NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)


def music(dur, sections, bpm=112, seed=3):
    """sections: list of (t_start, t_end, mood) with mood in mystery|bouncy|tiptoe|action|ironic|build"""
    rg = random.Random(seed); y = np.zeros(int((dur + 2) * SR)); beat = 60 / bpm; eighth = beat / 2
    D = 62                                                         # D4-ish root (D dorian)
    scale = [0, 2, 3, 5, 7, 9, 10, 12]
    prog = [0, 0, 5, 3, 0, 0, 7, 5]                                # i i IV iii-ish
    for t0, t1, mood in sections:
        t = t0; k = 0
        while t < t1 - 0.05:
            bar = int((t - t0) / (beat * 4)); root = D + prog[bar % len(prog)] - 12
            if mood == "mystery":
                if k % 4 == 0: place(y, pluck_fast(NOTE(root - 12), 1.8) * 0.5, t)
                if k % 2 == 1: place(y, pluck_fast(NOTE(D + rg.choice([0, 3, 7, 10])), 0.8) * 0.25, t)
                step = eighth * 2
            elif mood == "tiptoe":
                if k % 2 == 0: place(y, pluck_fast(NOTE(D + 12 + rg.choice(scale[:5])), 0.25) * 0.35, t)
                if k % 4 == 0: place(y, pluck_fast(NOTE(root - 12), 0.6) * 0.4, t)
                step = eighth
            else:
                vel = {"bouncy": 0.4, "action": 0.5, "ironic": 0.33, "build": 0.45}[mood]
                if k % 2 == 0: place(y, pluck_fast(NOTE(root - 12), 0.5) * 0.55, t)                       # bass
                note = D + rg.choice(scale) + (12 if mood in ("action", "build") and k % 3 == 0 else 0)
                if rg.random() < (0.85 if mood != "ironic" else 0.6): place(y, pluck_fast(NOTE(note), 0.45) * vel, t)
                if k % 4 == 2: place(y, pluck_fast(NOTE(note + rg.choice([3, 4, 7])), 0.4) * vel * 0.6, t)
                # percussion: tambourine-ish shaker + soft kick
                sh = hp(R.standard_normal(int(0.06 * SR)), 5000) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70)
                place(y, sh * (0.18 if k % 2 else 0.1), t)
                if mood in ("action", "build") and k % 2 == 0: place(y, thud(0.25, 65) * 0.5, t)
                if mood == "bouncy" and k % 4 == 0: place(y, thud(0.25, 65) * 0.35, t)
                step = eighth if mood != "build" else eighth * (1 - 0.4 * (t - t0) / max(0.1, t1 - t0))
            t += step; k += 1
    # gentle room reverb
    from scipy.signal import fftconvolve
    ir = R.standard_normal(int(0.8 * SR)) * np.exp(-np.arange(int(0.8 * SR)) / SR * 6) * 0.08
    y = y + fftconvolve(y, ir)[:len(y)] * 0.6
    return norm(y[:int(dur * SR)], 0.8)


def build(proj):
    TL = json.load(open(os.path.join(proj, "work/timeline.json"))); W = json.load(open(os.path.join(proj, "work/words.json")))
    total = TL[-1]["t1"] + 0.3
    sfx = np.zeros(int(total * SR) + SR)
    for sh in TL:
        t0, t1 = sh["t0"], sh["t1"]; dur = t1 - t0 - 0.25; names = sh["sfx"]
        for i, nm in enumerate(names):
            if nm not in LIB: continue
            t = t0 + 0.05 + (i / max(1, len(names))) * dur
            for f in sh["fx"]:
                if nm == "boom" and f["t"] == "boulder": t = t0 + 0.57 * (t1 - t0)
                if nm == "boom" and f.get("time"): t = f["time"] - 0.02
                if nm == "splash" and f["t"] == "splash": t = t0 + f.get("at", 0.8) * (t1 - t0)
            g = 0.45 if nm in VOCAL else 1.0
            place(sfx, LIB[nm](), t, g)
        place(sfx, whoosh(0.5) * 0.35, t0 - 0.2)                     # soft whoosh on every transition
    sf.write(os.path.join(proj, "audio/sfx.wav"), np.clip(sfx[:int(total * SR)], -1, 1), SR)
    # music sections from story beats
    def at(snip):
        q = snip.lower().split(); toks = [x["w"].lower().strip(".,!?") for x in W]
        for i in range(len(toks)):
            if toks[i:i + len(q)] == q: return W[i]["s"]
    last = W[-1]["s"]
    secs = [(0, at("this was"), "mystery"), (at("this was"), at("then, the") or at("then"), "bouncy"),
            (at("then"), at("he and a"), "tiptoe"), (at("he and a"), at("you see"), "action"),
            (at("you see"), at("the castle that"), "ironic"), (at("the castle that"), last - 0.15, "build")]
    m = music(total, [(a, b, c) for a, b, c in secs if a is not None and b is not None])
    m[int((last - 0.1) * SR):] *= np.exp(-np.arange(len(m) - int((last - 0.1) * SR)) / SR * 30)   # stop before the final word
    sf.write(os.path.join(proj, "audio/music.wav"), m, SR)
    print("sfx + music written", f"{total:.2f}s", "sections:", [(round(a, 2), round(b, 2), c) for a, b, c in secs if a and b])


if __name__ == "__main__":
    build(sys.argv[1])
