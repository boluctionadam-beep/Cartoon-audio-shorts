"""Western music bed + SFX for the Brannan short, mixed under voice.mp3."""
import numpy as np, subprocess, wave

SR = 48000
DUR = 2050 / 30
N = int(DUR * SR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR

def load_voice():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "voice.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    v = np.frombuffer(raw, np.float32).copy()
    out = np.zeros(N, np.float32); out[:min(N, len(v))] = v[:N]; return out

def env(n, a=0.005, r=0.2, sus=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r)
    return e

def lp(x, k):  # one-pole low-pass, k in (0,1)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y

def lp_fast(x, cutoff):
    # FFT brick-ish low-pass (fast, fine for beds)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)

def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x)).astype(np.float32)

def place(buf, sig, t0, gain=1.0):
    i = int(t0 * SR); j = min(N, i + len(sig))
    if i < N and j > i: buf[i:j] += sig[: j - i] * gain

midi = lambda m: 440 * 2 ** ((m - 69) / 12)

# ---------------- sfx ----------------
sfx = np.zeros(N, np.float32)
def noise(d): return rng.standard_normal(int(d * SR)).astype(np.float32)
def thunk(f0=90, d=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f0 * t * (1 + 0.6 * np.exp(-t * 40))) * np.exp(-t * 14) + lp_fast(noise(d), 1200) * np.exp(-t * 30) * 0.5).astype(np.float32)
def rumble(d):
    n = int(d * SR); t = np.arange(n) / SR
    s = lp_fast(noise(d), 160) * 3 * np.minimum(1, t / 0.15) * np.exp(-t / (d * 0.45))
    return s.astype(np.float32)
def crash(d=1.2):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n, np.float32)
    for k in range(14):
        tk = rng.uniform(0, d * 0.6); i = int(tk * SR); g = thunk(rng.uniform(60, 160), 0.35) * rng.uniform(0.3, 0.9)
        s[i:i + len(g)] += g[: n - i]
    s += lp_fast(noise(d), 2500) * np.exp(-t * 3) * 0.25
    return s
def cuckoo():
    out = []
    for f, d in [(740, 0.16), (587, 0.24)]:
        n = int(d * SR); t = np.arange(n) / SR
        out.append(np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.01) * np.exp(-t * 6)); out.append(np.zeros(int(0.06 * SR)))
    return np.concatenate(out).astype(np.float32)
def scrape(d=0.8):
    n = int(d * SR); t = np.arange(n) / SR
    s = noise(d) * (0.5 + 0.5 * np.sin(2 * np.pi * 13 * t)) * np.sin(np.pi * t / d)
    s = hp_fast(lp_fast(s, 5000), 1500)
    ring = np.sin(2 * np.pi * 1870 * t) * np.exp(-t * 3) * 0.2
    return (s * 0.6 + ring).astype(np.float32)
def ting():
    n = int(1.2 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(2093, 4), (3136, 6), (4186, 8)]) * 0.3).astype(np.float32)
def sting():
    n = int(2.0 * SR); t = np.arange(n) / SR
    low = np.sin(2 * np.pi * 41 * t) * np.exp(-t * 1.5) * 1.2
    hit = lp_fast(noise(2.0), 900) * np.exp(-t * 6) * 0.8
    stab = brass([midi(45), midi(48), midi(51)], 1.4); s = low + hit; s[: len(stab)] += stab * 2.2 * np.exp(-np.arange(len(stab)) / SR * 2)
    return s.astype(np.float32)
def creak(d=0.6, f0=140):
    n = int(d * SR); t = np.arange(n) / SR
    rate = f0 * (1 + 0.35 * np.sin(2 * np.pi * 1.3 * t / d))
    ph = np.cumsum(rate) / SR; pulses = (np.mod(ph, 1) < 0.08).astype(np.float32)
    s = lp_fast(pulses * (0.6 + 0.4 * rng.random(n).astype(np.float32)), 2200) * np.sin(np.pi * t / d)
    return hp_fast(s, 200) * 2.5
def snap():
    d = 0.5; n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(noise(d), 800) * np.exp(-t * 18) * 1.4 + np.pad(thunk(120, 0.4), (0, n - int(0.4 * SR))) * 0.6).astype(np.float32)
def splash(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    s = lp_fast(noise(d), 4000) * (np.exp(-t * 4) * np.minimum(1, t / 0.01)) + lp_fast(noise(d), 400) * np.exp(-t * 7) * 1.5
    return s.astype(np.float32)
def whoosh(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1500) * np.sin(np.pi * t / d) ** 2 * 0.6).astype(np.float32)
def snore(d=1.1):
    n = int(d * SR); t = np.arange(n) / SR
    buzz = (np.mod(np.cumsum(60 + 25 * np.sin(np.pi * t / d)) / SR, 1) < 0.3).astype(np.float32)
    return (lp_fast(buzz * 0.5 + noise(d) * 0.15, 700) * np.sin(np.pi * t / d) ** 2).astype(np.float32)
def leaves(d):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 6000), 2500) * (0.3 + 0.3 * np.sin(2 * np.pi * 0.7 * t) ** 2) * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)).astype(np.float32)
def water(d):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 900) * 0.5 + hp_fast(lp_fast(noise(d), 3000), 1200) * 0.15 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.4 * t))).astype(np.float32)

F = lambda f: f / 30
def breath(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 2500), 300) * np.sin(np.pi * t / d) ** 2 * 0.7).astype(np.float32)
def squish(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 300) * 4 * np.sin(np.pi * t / d) + np.sin(2 * np.pi * (70 + 30 * t / d) * t) * 0.3 * np.sin(np.pi * t / d)).astype(np.float32)
def plink(f=1400, d=0.3):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t * (1 + 0.4 * np.exp(-t * 30))) * np.exp(-t * 14) * 0.5).astype(np.float32)
def pop(f=520):
    n = int(0.18 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (f + 400 * np.exp(-t * 40)) * t) * np.exp(-t * 20)).astype(np.float32)
def tick():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return hp_fast((rng.standard_normal(n) * np.exp(-t * 90)).astype(np.float32), 3000)
def purr(d=3.0):
    n = int(d * SR); t = np.arange(n) / SR
    s = lp_fast(noise(d), 260) * (0.55 + 0.45 * np.sin(2 * np.pi * 26 * t)) * 3.0 * np.minimum(1, t / 0.3) * np.minimum(1, (d - t) / 0.4)
    return (s + np.sin(2 * np.pi * 52 * t) * 0.25 * np.minimum(1, t / 0.3)).astype(np.float32)
def radio(d=0.35):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 4000), 800) * np.exp(-t * 9) * 0.8 + np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 30) * 0.3).astype(np.float32)
def step(): return thunk(130, 0.13)

def beep(f=1500,d=0.12):
    n=int(d*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)*np.exp(-t*25)*0.5).astype(np.float32)
def zap(d=0.25):
    n=int(d*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*(400+2400*t/d)*t)*np.exp(-t*8)*0.4).astype(np.float32)
def heartb():
    return thunk(55,0.25)*0.9
def rustle(d=0.6):
    n=int(d*SR); t=np.arange(n)/SR
    return (hp_fast(lp_fast(noise(d),5000),1200)*(0.4+0.6*np.abs(np.sin(2*np.pi*7*t)))*np.sin(np.pi*t/d)).astype(np.float32)
def hum(d,f=110):
    n=int(d*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)*0.3*np.minimum(1,t/0.4)*np.minimum(1,(d-t)/0.4)).astype(np.float32)
def crackle(d=1.0):
    n=int(d*SR); r=np.zeros(n,np.float32); k=rng.random(int(d*40))*n
    for i in k.astype(int): m=min(n-i,int(0.01*SR)); r[i:i+m]+=rng.standard_normal(m).astype(np.float32)*np.exp(-np.arange(m)/(0.002*SR))*0.6
    return r# ---------------- music: oceanic bed that follows the story ----------------
music = np.zeros(N, np.float32)
def padn(freqs, d, a=0.7, r=0.9):
    n = int(d * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for dt in (-0.4, 0.0, 0.5):
            ff = f * (1 + dt * 0.003)
            s += np.sin(2 * np.pi * ff * t) + 0.35 * np.sin(4 * np.pi * ff * t) + 0.12 * np.sin(6 * np.pi * ff * t)
    s = lp_fast(s.astype(np.float32), 1800)
    return (s * np.minimum(1, t / a) * np.minimum(1, np.maximum(0, (d - t)) / r) / (len(freqs) * 3)).astype(np.float32)
def pluckn(f, dur=0.6, bright=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t) / (k + 1) for k in range(5))
    return (s * np.minimum(1, t / 0.004) * np.exp(-t / (dur * 0.3))).astype(np.float32)
def drum(f=62, d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t * (1 + 0.8 * np.exp(-t * 18))) * np.exp(-t * 7) + lp_fast(rng.standard_normal(n).astype(np.float32), 600) * np.exp(-t * 25) * 0.4).astype(np.float32)
def sub(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.minimum(1, t / 0.3) * np.minimum(1, np.maximum(0, d - t) / 0.5)).astype(np.float32)
S = lambda fr: fr / 30# ---------------- whale-specific sounds ----------------
def whalesong(d=2.2, f0=170, rise=1.3):
    n = int(d * SR); t = np.arange(n) / SR
    fr = f0 * (1 + rise * np.sin(np.pi * t / d) ** 1.5) * (1 + 0.025 * np.sin(2 * np.pi * 5.5 * t))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = (np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * np.sin(np.pi * t / d) ** 1.4
    s = lp_fast(s.astype(np.float32), 1600)
    e = np.zeros(n + int(0.6 * SR), np.float32); e[:n] += s; k = int(0.33 * SR); e[k:k + n] += s * 0.4; k2 = int(0.55 * SR); e[k2:k2 + n] += s * 0.2
    return e
def clicks(m=9, gap=0.06, f=3800):
    n = int((m * gap + 0.1) * SR); out = np.zeros(n, np.float32)
    for k in range(m):
        i = int(k * gap * (1 - 0.03 * k) * SR); L = int(0.012 * SR); tt = np.arange(L) / SR
        out[i:i + L] += (np.sin(2 * np.pi * f * tt) + 0.5 * rng.standard_normal(L)) * np.exp(-tt * 380) * 0.7
    return hp_fast(out, 1500)
def whimper(d=0.45, f0=950):
    n = int(d * SR); t = np.arange(n) / SR
    fr = f0 * (1 - 0.35 * t / d) * (1 + 0.04 * np.sin(2 * np.pi * 22 * t))
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / d) ** 0.7 * 0.5).astype(np.float32)
def sparkle(k=5):
    out = np.zeros(int(1.4 * SR), np.float32)
    for j in range(k):
        f = midi(84 + [0, 4, 7, 12, 16, 19][j % 6]); n = int(0.5 * SR); tt = np.arange(n) / SR
        i = int(j * 0.09 * SR); out[i:i + n] += (np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7) * 0.35).astype(np.float32)[: len(out) - i]
    return out
def bigsplash(d=1.4):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 5000) * np.exp(-t * 3) * np.minimum(1, t / 0.006) + lp_fast(noise(d), 300) * np.exp(-t * 5) * 2.0 + np.sin(2 * np.pi * 48 * t) * np.exp(-t * 6) * 1.2).astype(np.float32)
def wash(d=1.8):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 2200) * np.sin(np.pi * t / d) ** 2 * 0.9).astype(np.float32)
# ---------------- western SFX ----------------
def mixs(*a):
    n = max(len(x) for x, g in a); o = np.zeros(n, np.float32)
    for x, g in a: o[:len(x)] += x * g
    return o
def dig():
    return mixs((scrape(0.35), 0.5), (thunk(105, 0.28), 0.9))
def clink(f=None):
    f = f or rng.uniform(2300, 4200); n = int(0.35 * SR); t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.51 * t)) * np.exp(-t * 22) * 0.45).astype(np.float32)
def coins(n=8, d=1.0, g=1.0):
    out = np.zeros(int((d + 0.4) * SR), np.float32)
    for k in range(n): place_loc(out, clink(), rng.uniform(0, d), g * rng.uniform(0.5, 1.0))
    return out
def place_loc(buf, sig, t0, gain=1.0):
    i = int(t0 * SR); j = min(len(buf), i + len(sig))
    if i < len(buf) and j > i: buf[i:j] += sig[: j - i] * gain
def register():
    n = int(1.4 * SR); t = np.arange(n) / SR; out = np.zeros(n, np.float32)
    place_loc(out, (hp_fast(noise(0.12), 1500) * np.exp(-np.arange(int(0.12 * SR)) / SR * 40)).astype(np.float32), 0.0, 0.9)
    place_loc(out, thunk(150, 0.2), 0.03, 0.8)
    bell = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(2349, 3.0), (3520, 4.0), (4698, 6.0)]) * 0.45
    place_loc(out, bell.astype(np.float32), 0.14, 1.0)
    place_loc(out, coins(7, 0.6), 0.2, 0.7)
    return out
def stamp():
    return mixs((thunk(70, 0.4), 1.1), (snap(), 0.5), (rustle(0.3), 0.2))
def murmur(d):
    n = int(d * SR); t = np.arange(n) / SR
    s = hp_fast(lp_fast(noise(d), 1900), 220) * (0.45 + 0.35 * np.sin(2 * np.pi * 2.3 * t + 1) ** 2 + 0.2 * np.sin(2 * np.pi * 0.9 * t) ** 2)
    return (s * np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.5) * 0.8).astype(np.float32)
def gasp(d=0.5):
    n = int(d * SR); t = np.arange(n) / SR
    return (hp_fast(lp_fast(noise(d), 3500), 500) * np.sin(np.pi * t / d) ** 1.5 * 0.9).astype(np.float32)
def shop_bell():
    n = int(1.3 * SR); t = np.arange(n) / SR
    return (sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(1568, 3.5), (2093, 4.5), (3136, 7)]) * 0.4).astype(np.float32)
def sad_bone(f0=233, d=1.3):
    n = int(d * SR); t = np.arange(n) / SR; segs = [(0, 0.38, 1.0), (0.42, 0.78, 0.944), (0.84, d, 0.89)]
    out = np.zeros(n, np.float32)
    for a, b, r in segs:
        i, j = int(a * SR), int(b * SR); tt = np.arange(j - i) / SR; ph = 2 * np.pi * f0 * r * np.cumsum(1 - 0.06 * tt / max(tt[-1], 1e-3)) / SR
        out[i:j] += lp_fast(((np.mod(ph / (2 * np.pi), 1) * 2 - 1) * 0.5).astype(np.float32), 1100) * np.minimum(1, tt / 0.03) * np.exp(-tt * 3)
    return out * 1.2
def whistle_tone(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    fr = (1700 + 700 * np.sin(np.pi * t / d) + 40 * np.sin(2 * np.pi * 6 * t)); ph = 2 * np.pi * np.cumsum(fr) / SR
    return (np.sin(ph) * 0.5 * np.sin(np.pi * t / d) ** 0.6).astype(np.float32)
def gallop_loop(t0, t1, g=1.0, bpm=150):
    b = 60 / bpm; k = 0; tt = t0
    while tt < t1:
        for off, gg in ((0, 1.0), (0.5, 0.6), (0.75, 0.8)): place(sfx, thunk(78 + 10 * (k % 2), 0.16), tt + off * b, 0.35 * g * gg)
        place(sfx, hp_fast(lp_fast(noise(0.09), 4500), 1800) * 0.0 + dustpuff(), tt + 0.1 * b, 0.1 * g) if False else None
        tt += b; k += 1
def dustpuff(d=0.25):
    n = int(d * SR); t = np.arange(n) / SR
    return (lp_fast(noise(d), 1200) * np.exp(-t * 14) * 0.4).astype(np.float32)

# ---------------- music: synthesized western bed locked to the narration ----------------
music = np.zeros(N, np.float32)
def twang(f, dur=0.5, bright=0.55):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t * (1 + 0.003 * np.exp(-t * 30))) / (k + 1) for k in range(6))
    return (s * np.minimum(1, t / 0.003) * np.exp(-t / (dur * 0.35))).astype(np.float32)
def kick(): return drum(58, 0.35)
def snare():
    n = int(0.22 * SR); t = np.arange(n) / SR
    return (hp_fast(noise(0.22), 900) * np.exp(-t * 22) * 0.9 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.4).astype(np.float32)
def hat():
    n = int(0.06 * SR); t = np.arange(n) / SR
    return (hp_fast(noise(0.06), 6000) * np.exp(-t * 60) * 0.5).astype(np.float32)
def chord(m): return [midi(x) for x in m]
G_ = [55, 59, 62]; C_ = [60, 64, 67]; D_ = [62, 66, 69]; A_ = [57, 61, 64]; Em_ = [52, 55, 59]; Am_ = [57, 60, 64]; B_ = [59, 63, 66]; E_ = [52, 56, 59]; Dm_ = [50, 53, 57]; F_ = [53, 57, 60]
def section(t0, t1, style, prog, bpm, lev=1.0):
    b = 60 / bpm; bar = 4 * b; i = 0; tt = t0
    while tt < t1 - 0.05:
        ch = prog[i % len(prog)]; root = ch[0] - 12; fifth = ch[0] - 5
        d = min(bar, t1 - tt) + 0.3
        if style in ('gallop', 'rag', 'cash', 'oompah', 'plink'):
            place(music, padn(chord(ch), d + 0.2, 0.15, 0.4), tt, 0.16 * lev)
        for k in range(8):                             # 8th-note grid
            tk = tt + k * b / 2
            if tk >= t1: break
            if style == 'gallop':
                place(music, kick(), tk, 0.6 * lev) if k in (0, 4) else None
                place(music, snare(), tk, 0.5 * lev) if k in (2, 6) else None
                place(music, twang(midi(ch[k % 3] + 12), 0.28, 0.6), tk, 0.34 * lev)
                place(music, twang(midi(root if k % 4 == 0 else fifth), 0.35, 0.3), tk, 0.45 * lev) if k % 2 == 0 else None
                if k % 2 == 1: place(music, hat(), tk, 0.5 * lev)
            elif style == 'plink':
                place(music, twang(midi(ch[(k * 2) % 3] + 12 + 12 * (k % 2)), 0.32, 0.7), tk, 0.34 * lev)
                place(music, twang(midi(root), 0.4, 0.3), tk, 0.4 * lev) if k in (0, 4) else None
                place(music, hat(), tk, 0.35 * lev) if k % 2 == 1 else None
            elif style == 'sly':
                if k in (0, 3, 4, 7): place(music, twang(midi(root + (0, 3, 7, 5)[[0, 3, 4, 7].index(k)]), 0.55, 0.3), tk, 0.55 * lev)
                if k in (2, 6): place(music, twang(midi(ch[2] + 24), 0.9, 0.35), tk, 0.22 * lev)
                place(music, hat(), tk, 0.25 * lev) if k % 2 == 1 else None
            elif style == 'oompah':
                if k in (0, 4): place(music, twang(midi(root), 0.35, 0.3), tk, 0.7 * lev)
                if k in (2, 6):
                    for m in ch: place(music, twang(midi(m + 12), 0.25, 0.6), tk, 0.22 * lev)
                place(music, hat(), tk, 0.3 * lev) if k % 2 == 1 else None
            elif style == 'rag':
                pat = (0, 2, 3, 5, 6) ; 
                if k in pat: place(music, twang(midi(ch[(k) % 3] + 12), 0.3, 0.7), tk, 0.34 * lev)
                if k in (0, 4): place(music, twang(midi(root), 0.35, 0.3), tk, 0.6 * lev)
                place(music, snare(), tk, 0.3 * lev) if k in (2, 6) else None
                place(music, hat(), tk, 0.3 * lev) if k % 2 == 1 else None
            elif style == 'cash':
                place(music, twang(midi(ch[(k * 2 + 1) % 3] + 12 + 12 * ((k // 2) % 2)), 0.18, 0.8), tk, 0.34 * lev)
                place(music, twang(midi(root), 0.3, 0.3), tk, 0.5 * lev) if k in (0, 3, 4) else None
                place(music, kick(), tk, 0.45 * lev) if k in (0, 4) else None
                place(music, hat(), tk, 0.4 * lev) if k % 2 == 1 else None
            elif style == 'groove':
                if k in (0, 4): place(music, twang(midi(root), 0.6, 0.3), tk, 0.6 * lev)
                if k in (2, 3, 6): place(music, twang(midi(ch[(k) % 3] + 12), 0.6, 0.4), tk, 0.3 * lev)
                place(music, kick(), tk, 0.3 * lev) if k == 0 else None
                place(music, hat(), tk, 0.2 * lev) if k % 2 == 1 else None
        if style == 'groove': place(music, padn(chord(ch), d + 0.4, 0.6, 0.9), tt, 0.22 * lev)
        tt += bar; i += 1
section(0.0, 8.1, 'gallop', [Em_, Am_, Em_, B_], 150, 1.0)
section(8.1, 14.0, 'plink', [G_, C_, G_, D_], 112, 0.85)
section(14.0, 20.3, 'sly', [Am_, E_, Am_, Dm_], 84, 0.9)
section(20.3, 28.5, 'oompah', [C_, G_, C_, F_], 122, 0.9)
section(28.5, 37.0, 'rag', [D_, A_, D_, G_], 132, 0.95)
section(37.0, 47.0, 'gallop', [Em_, Am_, B_, Em_], 156, 1.05)
section(47.0, 53.1, 'cash', [C_, F_, G_, C_], 128, 0.95)
section(53.1, 63.8, 'groove', [Am_, F_, C_, G_], 88, 0.9)
# final resolve
place(music, padn(chord(C_), 5.2, 0.4, 2.4), 63.8, 0.45); place(music, sub(midi(36), 4.8), 63.9, 0.5)
for k, m in enumerate([72, 76, 79, 84]): place(music, twang(midi(m), 1.2, 0.4), 64.1 + k * 0.18, 0.4)
place(music, twang(midi(72), 2.4, 0.4), 65.6, 0.35); place(music, twang(midi(60), 2.6, 0.3), 65.6, 0.5)
place(music, kick(), 64.1, 0.7)
fi = int(0.5 * SR); music[:fi] *= np.linspace(0, 1, fi); fo = int(2.4 * SR); music[-fo:] *= np.linspace(1, 0, fo)

# ---------------- cue table (seconds locked to the shots / narration) ----------------
import re as _re, json as _json
_story = open('web/story.js').read()
SA = {m[0]: int(m[1]) for m in _re.findall(r"SH\('(\w+)', (\d+), \d+", _story)}
_rs = _re.search(r"const RS = \{(.*?)\};", _story, _re.S).group(1)
RS = {k: int(v) for k, v in _re.findall(r"(\w+): (\d+)", _rs)}
def RT(shot, sbf): return (RS[shot] + (sbf - SA[shot])) / 30       # storyboard frame inside a shot -> real seconds
cuts = [RS[k] / 30 for k in RS if RS[k] > 0]
for c_ in cuts: place(sfx, whoosh(0.3), c_ - 0.06, 0.28)
# 0-8: the rush: stampede of boots + crowd, dust
gallop_loop(0.2, 8.0, 0.8, 150); place(sfx, murmur(8.0), 0.1, 0.5); place(sfx, wash(1.6), 0.0, 0.25)
for t_ in (2.0, 3.1, 4.7): place(sfx, whoosh(0.5), t_, 0.3)
place(sfx, plink(1800, 0.4), 4.8, 0.45); place(sfx, sparkle(5), 4.9, 0.5)        # "gold"
place(sfx, sparkle(6), 6.5, 0.45); place(sfx, ting(), 7.1, 0.35)                 # millionaire dream
# 8-14: digging, panning, nugget
for k, t_ in enumerate([8.6, 9.5, 10.3, 11.2]): place(sfx, dig(), t_, 0.7)
place(sfx, water(3.0), 10.8, 0.5); place(sfx, splash(0.8), 11.5, 0.4)
place(sfx, ting(), 12.7, 0.6); place(sfx, sparkle(6), 12.75, 0.7); place(sfx, murmur(1.5), 12.9, 0.25)
place(sfx, pop(700), RT('nugget', 330), 0.7); place(sfx, coins(6, 0.6), RT('nugget', 330), 0.5)   # "GOLD!" bang
# 14-20: Brannan watches
place(sfx, rumble(1.0), 14.15, 0.35)
place(sfx, pop(520), RT('brFace', 436), 0.5); place(sfx, plink(1300, 0.3), RT('brFace', 456), 0.45); place(sfx, ting(), RT('brFace', 468), 0.45)
place(sfx, stamp(), RT('brWatch', 497), 0.7); place(sfx, ting(), RT('brWatch', 500), 0.5); place(sfx, sparkle(4), RT('brWatch', 500), 0.4)
# 20-29: the warehouse: steps on planks, clatter of tools, SOLD
for k in range(8): place(sfx, step(), 20.9 + k * 0.27, 0.4)
place(sfx, creak(0.5, 120), 20.6, 0.35)
place(sfx, coins(5, 0.5), 22.2, 0.5)
place(sfx, stamp(), RT('whDeal', 612), 1.0); place(sfx, register(), RT('whDeal', 616), 0.6)
for k, t_ in enumerate([24.2, 24.9, 25.6, 26.3]): place(sfx, sparkle(3), t_, 0.35); place(sfx, plink(2400 + 200 * k, 0.2), t_, 0.3)
place(sfx, whoosh(0.5), RT('whHero', 712) - 0.05, 0.5); place(sfx, ting(), RT('whHero', 714), 0.55); place(sfx, sparkle(5), RT('whHero', 716), 0.45)
# 29-37: spreading the news
for k in range(3): place(sfx, pop(560 + 80 * k), RT('shout', 750 + 20 * k), 0.6); place(sfx, gasp(0.5), RT('shout', 750 + 20 * k) + 0.2, 0.3)
place(sfx, murmur(4.0), 31.3, 0.55)
for k in range(4): place(sfx, plink(1700 + 150 * k, 0.2), RT('listen', 818 + 9 * k), 0.5)
place(sfx, whoosh(0.6), RT('paperCU', 870), 0.8); place(sfx, rustle(0.7), RT('paperCU', 872), 0.6)
place(sfx, stamp(), RT('paperCU', 884), 0.9); place(sfx, pop(480), RT('paperCU', 884), 0.5)
gallop_loop(35.8, 37.2, 1.0, 156); place(sfx, whoosh(0.9), 36.0, 0.5)
# 37-47: stampede to the store, bell, coins, bustle
gallop_loop(37.2, 41.0, 1.2, 156); place(sfx, murmur(5.0), 37.2, 0.5); place(sfx, rumble(2.5), 37.3, 0.5)
place(sfx, wash(2.0), 37.2, 0.25)
for k in range(5): place(sfx, coins(4, 0.4), 39.8 + k * 0.6, 0.35)
place(sfx, shop_bell(), RT('shopIn', 1080) + 0.1, 0.55); place(sfx, murmur(5.0), RT('shopIn', 1080), 0.45)
for k in range(8): place(sfx, coins(3, 0.3), 42.4 + k * 0.55, 0.35)
place(sfx, register(), 46.2, 0.7)
# 47-53: counting, cash flood
for k in range(14): place(sfx, clink(), 47.2 + k * 0.42, 0.45)
place(sfx, shop_bell(), 48.9, 0.4); place(sfx, murmur(4.0), 47.2, 0.4)
place(sfx, register(), RT('bags', 1340), 0.8); place(sfx, coins(12, 1.4), RT('bags', 1344), 0.8)
place(sfx, stamp(), RT('bags', 1352), 0.7); place(sfx, register(), RT('bags', 1354), 0.9)
place(sfx, whistle_tone(1.0), 52.3, 0.5); place(sfx, ting(), RT('whistle', 1403), 0.5)
# 53-64: contrast: tired digging vs calm counting, womp-womp
for k, t_ in enumerate([53.6, 54.5, 55.3, 56.2]): place(sfx, dig(), t_, 0.45)
place(sfx, wash(2.5), 53.3, 0.2)
for k in range(5): place(sfx, clink(), 57.0 + k * 0.5, 0.4)
place(sfx, sad_bone(233, 1.4), 59.6, 0.7)
place(sfx, breath(1.0), 60.5, 0.25)
place(sfx, coins(5, 0.6), 62.0, 0.4)
# 64-68: the lesson plate
place(sfx, whoosh(0.5), RT('final', 1730) - 0.1, 0.55); place(sfx, stamp(), RT('final', 1730), 1.0)
place(sfx, ting(), RT('final', 1732), 0.7); place(sfx, sparkle(6), RT('final', 1734), 0.6)

voice = load_voice()
def grms(x, win=0.4):  # gated RMS over blocks above -50 dB of peak
    k = int(win * SR); b = x[: len(x) // k * k].reshape(-1, k); r = np.sqrt((b ** 2).mean(1)); g = r > r.max() * 0.05
    return float(np.sqrt((r[g] ** 2).mean())) if g.any() else 1e-6
vr, vp = grms(voice), float(np.abs(voice).max())
music *= (vr * 0.5) / max(grms(music), 1e-6)                       # music = -6 dB vs voice
sfx *= (vr * 0.5) / max(grms(sfx), 1e-6) if sfx.any() else 1
sp = float(np.abs(sfx).max()); sfx *= min(1, 0.7 * vp / sp) if sp > 0 else 1   # peak cap 0.7x voice peak
print("voice rms %.4f | music %.1f dB | sfx %.1f dB vs voice" % (vr, 20 * np.log10(grms(music) / vr), 20 * np.log10(max(grms(sfx), 1e-9) / vr)))
for nm, x in (("music.wav", music), ("sfx.wav", sfx)):
    with wave.open(nm, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
mix = voice + music + sfx
pk = float(np.abs(mix).max()); mix *= min(1, 0.95 / pk)
fade = int(0.04 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
with wave.open("mix_raw.wav", "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
print("ok", len(mix) / SR)
