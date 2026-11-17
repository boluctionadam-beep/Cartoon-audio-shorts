# ---------------- music: oceanic bed that follows the story ----------------
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
S = lambda fr: fr / 30