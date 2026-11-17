#!/usr/bin/env python3
"""Burn word-by-word captions (1–2 words, bold white, black outline, lower third, pop-in) onto frames.
usage: captions.py words.json in_dir out_dir [fps]   words.json = [[start_s, end_s, "TEXT"], ...]"""
import sys, json, os, glob
from PIL import Image, ImageDraw, ImageFont
words = json.load(open(sys.argv[1])); src, dst = sys.argv[2], sys.argv[3]; fps = float(sys.argv[4]) if len(sys.argv) > 4 else 30
os.makedirs(dst, exist_ok=True)
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
HOT = {'GOLD', 'GOLD.', 'MILLIONAIRE.', 'MILLIONAIRE', '1848,', '1848', 'SHOVELS', 'MILLIONS'}
def render(text, size, hot):
    f = ImageFont.truetype(FONT, size); st = max(8, size // 8)
    d = Image.new('RGBA', (1, 1)); w, h = ImageDraw.Draw(d).textbbox((0, 0), text, font=f, stroke_width=st)[2:]
    im = Image.new('RGBA', (w + 2 * st + 12, h + 2 * st + 24), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.text((st + 6, st + 14), text, font=f, fill=(0, 0, 0, 140), stroke_width=st + 2, stroke_fill=(0, 0, 0, 140))   # soft shadow
    dr.text((st + 6, st + 8), text, font=f, fill=(255, 216, 58, 255) if hot else (255, 255, 255, 255), stroke_width=st, stroke_fill=(10, 8, 12, 255))
    return im
for fp in sorted(glob.glob(os.path.join(src, '*.jpg')) + glob.glob(os.path.join(src, '*.png'))):
    n = int(''.join(c for c in os.path.basename(fp) if c.isdigit())); t = n / fps
    img = Image.open(fp).convert('RGBA'); W, H = img.size
    for a, b, txt in words:
        if a <= t < b:
            hot = txt.upper().strip('!?') in HOT or txt.upper() in HOT
            im = render(txt.upper(), 96, hot); k = min(1.0, (t - a) * fps / 4.0); sc = 0.72 + 0.28 * (1 - (1 - k) ** 3) + (0.08 * __import__('math').sin(k * 3.14159))
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
            img.alpha_composite(im, ((W - im.width) // 2, int(H * 0.70) - im.height // 2)); break
    img.convert('RGB').save(os.path.join(dst, os.path.basename(fp)), quality=94)
