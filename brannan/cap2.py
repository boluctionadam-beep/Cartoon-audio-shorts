#!/usr/bin/env python3
"""Burn word-by-word captions (1–2 words, bold white, black outline, lower third, pop-in) onto frames.
usage: captions.py words.json in_dir out_dir [fps]   words.json = [[start_s, end_s, "TEXT"], ...]"""
import sys, json, os, glob
from PIL import Image, ImageDraw, ImageFont
words = json.load(open(sys.argv[1])); src, dst = sys.argv[2], sys.argv[3]; fps = float(sys.argv[4]) if len(sys.argv) > 4 else 30
os.makedirs(dst, exist_ok=True)
FONT = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
HOT = {'GOLD', 'MILLIONAIRE', '1848', 'SHOVELS', 'MILLIONS', 'FORTUNE', '$150,000', 'BRANNAN', 'PICKAXES', 'TREASURE'}
MAXW = 930
def isHot(w): return w.upper().strip('.,!?:;"').replace('P.S.','PS') in HOT
def render(text, size, hot=False):
    words = text.split(' ')
    while True:
        f = ImageFont.truetype(FONT, size); st = max(8, size // 8)
        d = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        sp = d.textlength(' ', font=f)
        ws = [d.textlength(w, font=f) for w in words]; tot = sum(ws) + sp * (len(words) - 1) + 2 * st
        if tot <= MAXW or size <= 56: break
        size -= 4
    asc, desc = f.getmetrics(); h = asc + desc
    im = Image.new('RGBA', (int(tot) + 2 * st + 12, h + 2 * st + 24), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    x = st + 6
    for w, wd in zip(words, ws):
        col = (255, 216, 58, 255) if isHot(w) else (255, 255, 255, 255)
        dr.text((x, st + 14), w, font=f, fill=(0, 0, 0, 140), stroke_width=st + 2, stroke_fill=(0, 0, 0, 140))
        dr.text((x, st + 8), w, font=f, fill=col, stroke_width=st, stroke_fill=(10, 8, 12, 255))
        x += wd + sp
    return im
for fp in sorted(glob.glob(os.path.join(src, '*.jpg')) + glob.glob(os.path.join(src, '*.png'))):
    n = int(''.join(c for c in os.path.basename(fp) if c.isdigit())); t = n / fps
    if not (int(os.environ.get('LO', 0)) <= n < int(os.environ.get('HI', 10**9))): continue
    img = Image.open(fp).convert('RGBA'); W, H = img.size
    for a, b, txt in words:
        if a <= t < b:
            im = render(txt.upper(), 96); k = min(1.0, (t - a) * fps / 4.0); sc = 0.72 + 0.28 * (1 - (1 - k) ** 3) + (0.08 * __import__('math').sin(k * 3.14159))
            im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
            img.alpha_composite(im, ((W - im.width) // 2, int(H * 0.70) - im.height // 2)); break
    img.convert('RGB').save(os.path.join(dst, os.path.basename(fp)), quality=94)
