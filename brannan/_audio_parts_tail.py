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
