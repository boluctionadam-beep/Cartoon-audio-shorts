#!/usr/bin/env python3
"""Local American-English narrator voice (Kokoro, Apache-2.0), runs on CPU, no API, no limits.

Voice blends: --voice "am_michael:0.5,am_adam:0.5" (weights are normalised).
The script is split into sentences; each sentence is generated, its edge silence trimmed,
and sentences are joined with a fixed short pause, so the pace stays tight (Ricks-style).

Outputs:
  <out>.wav            24 kHz mono narration, voice starts at ~0.05 s
  <out>.phrases.json   [{"text","s","e"}] per sentence (exact)
  <out>.words.json     [{"w","s","e"}] per word (estimated inside each sentence by syllable weight)

Usage:
  python3 tools/tts.py "Text here." -o work/voice
  python3 tools/tts.py --file work/script.txt -o work/voice --voice "am_michael:0.5,am_adam:0.5" --speed 1.1
Install once: pip install kokoro-onnx soundfile   (model files ~350 MB are downloaded on first run)
"""
import argparse, json, os, re, sys, urllib.request
import numpy as np

REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = ["kokoro-v1.0.onnx", "voices-v1.0.bin"]


def ensure_models(d):
    os.makedirs(d, exist_ok=True)
    for f in FILES:
        p = os.path.join(d, f)
        if not os.path.exists(p) or os.path.getsize(p) < 1_000_000:
            print("downloading", f, "...", file=sys.stderr)
            urllib.request.urlretrieve(REL + f, p + ".part")
            os.replace(p + ".part", p)
    return [os.path.join(d, f) for f in FILES]


def blend(k, spec):
    parts = []
    for item in spec.split(","):
        name, _, w = item.strip().partition(":")
        parts.append((name, float(w) if w else 1.0))
    tot = sum(w for _, w in parts)
    return sum(k.get_voice_style(n) * (w / tot) for n, w in parts)


def trim(a, sr, thr=0.012, keep=0.03):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(keep * sr)); e = min(len(a), idx[-1] + int(keep * sr))
    return a[s:e]


def syllables(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    return max(1, len(re.findall(r"[aeiouy]+", w)) - (1 if w.endswith("e") and len(w) > 3 else 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("-o", "--out", default="work/voice")
    ap.add_argument("--voice", default="am_michael:0.5,am_adam:0.5")
    ap.add_argument("--speed", type=float, default=1.1)
    ap.add_argument("--pause", type=float, default=0.22, help="silence between sentences, s")
    ap.add_argument("--lead", type=float, default=0.05, help="silence before the first word, s")
    ap.add_argument("--models", default=os.path.expanduser("~/.cache/kokoro"))
    a = ap.parse_args()
    text = open(a.file).read() if a.file else a.text
    if not text:
        ap.error("give text or --file")
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k = Kokoro(*ensure_models(a.models))
    style = blend(k, a.voice)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", " ".join(text.split())) if s.strip()]
    sr = 24000; out = [np.zeros(int(a.lead * sr), np.float32)]; t = a.lead
    phrases, words = [], []
    for i, s in enumerate(sents):
        audio, sr = k.create(s, voice=style, speed=a.speed, lang="en-us")
        audio = trim(audio.astype(np.float32), sr)
        d = len(audio) / sr
        phrases.append({"text": s, "s": round(t, 3), "e": round(t + d, 3)})
        ws = s.split(); wt = [syllables(w) + (0.6 if w[-1] in ",;:" else 0) for w in ws]
        acc = t
        for w, x in zip(ws, wt):
            dd = d * x / sum(wt); words.append({"w": w, "s": round(acc, 3), "e": round(acc + dd, 3)}); acc += dd
        out.append(audio); t += d
        if i < len(sents) - 1:
            out.append(np.zeros(int(a.pause * sr), np.float32)); t += a.pause
    out.append(np.zeros(int(0.3 * sr), np.float32))
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    sf.write(a.out + ".wav", np.concatenate(out), sr)
    json.dump(phrases, open(a.out + ".phrases.json", "w"), indent=1)
    json.dump(words, open(a.out + ".words.json", "w"), indent=1)
    n = len(text.split())
    print(f"{a.out}.wav  {t:.1f}s  {len(sents)} sentences  {n} words  ~{n / t * 60:.0f} wpm  voice={a.voice} speed={a.speed}")


if __name__ == "__main__":
    main()
