#!/usr/bin/env python3
"""Word timestamps for a voiceover whose script is known: offline ASR (sherpa-onnx zipformer, token timestamps)
then map recognised words onto the script words (difflib), interpolating any the ASR missed.
Usage: python3 align.py voice.wav script.txt out_words.json   -> [{"w","s","e"}], also out_phrases.json"""
import sys, json, re, difflib, subprocess, tempfile, os, numpy as np, soundfile as sf
import sherpa_onnx
M = os.path.expanduser("~/.cache/asr/sherpa-onnx-zipformer-en-2023-06-26")
voice, script, out = sys.argv[1:4]
tmp = os.path.join(tempfile.mkdtemp(), "a.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", voice, "-ac", "1", "-ar", "16000", tmp], check=True)
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{M}/encoder-epoch-99-avg-1.onnx", decoder=f"{M}/decoder-epoch-99-avg-1.onnx",
                                                    joiner=f"{M}/joiner-epoch-99-avg-1.onnx", tokens=f"{M}/tokens.txt", num_threads=4)
x, sr = sf.read(tmp, dtype="float32")
words = []
CH = 12 * sr; pos = 0
while pos < len(x):                                    # chunk at quiet points ~20 s
    end = min(len(x), pos + CH)
    if len(x) - end < 3 * sr: end = len(x)
    if end < len(x):
        w = x[end - sr:end + sr]; e = np.convolve(w ** 2, np.ones(800) / 800, "same"); end = end - sr + int(np.argmin(e))
    st = rec.create_stream(); st.accept_waveform(sr, x[pos:end]); rec.decode_stream(st)
    toks, ts = st.result.tokens, st.result.timestamps
    for t, s in zip(toks, ts):
        s += pos / sr
        if t.startswith(("▁", " ")) or not words:
            words.append({"w": t.replace("▁", "").strip(), "s": s})
        else:
            words[-1]["w"] += t
    pos = end
for i, w in enumerate(words):
    w["e"] = words[i + 1]["s"] if i + 1 < len(words) else w["s"] + 0.35
    w["e"] = min(w["e"], w["s"] + 0.9)
asr = [re.sub(r"[^a-z0-9']", "", w["w"].lower()) for w in words]
text = open(script).read()
sw = text.split(); norm = [re.sub(r"[^a-z0-9']", "", w.lower()) for w in sw]
sm = difflib.SequenceMatcher(None, norm, asr, autojunk=False)
res = [None] * len(sw)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): res[a + k] = (words[b + k]["s"], words[b + k]["e"])
known = [i for i, r in enumerate(res) if r]
print(f"script words {len(sw)}, asr words {len(words)}, matched {len(known)}")
for i in range(len(sw)):                               # interpolate gaps
    if res[i] is None:
        p = max([k for k in known if k < i], default=None); q = min([k for k in known if k > i], default=None)
        t0 = res[p][1] if p is not None else 0.05; t1 = res[q][0] if q is not None else t0 + 0.4
        cnt = (q if q is not None else len(sw)) - (p if p is not None else -1) - 1; idx = i - (p if p is not None else -1)
        d = (t1 - t0) / max(1, cnt); res[i] = (t0 + d * (idx - 1), t0 + d * idx)
W = [{"w": w, "s": round(s, 3), "e": round(e, 3)} for w, (s, e) in zip(sw, res)]
json.dump(W, open(out, "w"), indent=0)
ph = []; cur = []
for w in W:
    cur.append(w)
    if re.search(r"[.!?,]$", w["w"]):
        ph.append({"text": " ".join(c["w"] for c in cur), "s": cur[0]["s"], "e": cur[-1]["e"]}); cur = []
if cur: ph.append({"text": " ".join(c["w"] for c in cur), "s": cur[0]["s"], "e": cur[-1]["e"]})
json.dump(ph, open(out.replace("words", "phrases"), "w"), indent=1)

