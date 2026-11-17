# ---------------- whale-specific sounds ----------------
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
