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

