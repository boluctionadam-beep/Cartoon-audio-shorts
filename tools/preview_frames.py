#!/usr/bin/env python3
"""Contact sheet of composed frames (background + animated cards + fx) at a fraction u of each shot.
python3 preview_frames.py PROJ SHOT_DIR out.jpg [u=0.5] [ids]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compose import Shot
from PIL import Image, ImageDraw
proj, sd, out = sys.argv[1:4]; u = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5
ids = sys.argv[5].split(",") if len(sys.argv) > 5 else None
os.environ["SHOT_DIR"] = sd
TL = json.load(open(os.path.join(proj, "work/timeline.json")))
tiles = []
for sh in TL:
    if ids and sh["id"] not in ids: continue
    if not os.path.exists(os.path.join(sd, sh["id"] + ".json")): continue
    meta = json.load(open(os.path.join(sd, sh["id"] + ".json"))); W = int(round(meta["size"][0] / meta["overscan"] / 2) * 2); H = int(round(W * 16 / 9 / 2) * 2)
    S = Shot(proj, sh, W, H, 30, None); fr = S.frame(int(u * S.dur * 30))
    tiles.append((sh["id"], Image.fromarray(fr)))
tw, th = 216, 384; cols = min(9, len(tiles)); rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 4), rows * (th + 18)), (255, 255, 255)); d = ImageDraw.Draw(sheet)
for i, (n, im) in enumerate(tiles):
    x, y = (i % cols) * (tw + 4), (i // cols) * (th + 18); sheet.paste(im.resize((tw, th)), (x, y + 16)); d.text((x + 2, y + 2), n, fill=(0, 0, 0))
sheet.save(out); print(out, len(tiles))
