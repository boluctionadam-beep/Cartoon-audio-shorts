#!/usr/bin/env python3
"""Ricks-like colour grade for rendered frames: contrast S-curve, saturation, warm highlights / cool shadows,
soft bloom, vignette. Usage: python3 grade.py in.png out.png [--warm 1.0] [--sat 1.25]"""
import argparse, numpy as np
from PIL import Image, ImageFilter
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--warm", type=float, default=1.0); ap.add_argument("--sat", type=float, default=1.25)
ap.add_argument("--contrast", type=float, default=0.22); ap.add_argument("--vignette", type=float, default=0.35)
ap.add_argument("--bloom", type=float, default=0.18)
a = ap.parse_args()
im = Image.open(a.inp).convert("RGB"); x = np.asarray(im).astype(np.float32) / 255
lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
x = lum + (x - lum) * a.sat                                                # saturation
x = np.clip(x, 0, 1); x = x + a.contrast * (x - 0.5) * (1 - np.abs(2 * x - 1))   # S-curve
lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
tint_hi = np.array([1.05, 1.0, 0.90], np.float32); tint_lo = np.array([0.93, 0.97, 1.06], np.float32)
t = (tint_lo + (tint_hi - tint_lo) * lum) ** a.warm
x = np.clip(x * t, 0, 1)
bright = np.clip((x - 0.72) / 0.28, 0, 1) * x                             # bloom
b = np.asarray(Image.fromarray((bright * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(x.shape[1] / 60))).astype(np.float32) / 255
x = 1 - (1 - x) * (1 - b * a.bloom * 2)
h, w = x.shape[:2]; yy, xx = np.mgrid[0:h, 0:w]
r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / np.sqrt(2)
x = x * (1 - a.vignette * np.clip(r - 0.35, 0, 1) ** 1.5 / 0.65 ** 1.5)[..., None]
Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)).save(a.out)
print("graded ->", a.out)
