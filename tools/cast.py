"""Character system: every character is a SPEC (dict) drawn by the same code, so all characters share
one quality level and style, and differ by design. See CLAUDE.md -> "Characters".

draw_full(spec, path, expr, pose, look)   full body card (RGBA PNG, 1000x1800)
draw_head(c, spec, hx, hy, k, expr, tilt, look)   head only (for sheets / close-ups)
lineup(specs, path, exprs)                 cast lineup + silhouette check + expression rows

Expressions: neutral curious smug shocked disgusted laughing angry scared sad determined
Poses: stand point_up hips arms_up hold_spear hold_sword shrug
"""
import math, random
from PIL import Image, ImageDraw
from charkit import Canvas, INK, WHITE, ellipse_pts, capsule_pts, head_pts, shaggy_pts

EXPRS = ["neutral", "curious", "smug", "shocked", "disgusted", "laughing", "angry", "scared", "sad", "determined"]
_HI = (238, 242, 248, 255)


def _darker(c, f=0.55):
    return tuple(int(v * f) for v in c[:3]) + (255,)


def _lighter(c, f=0.45):
    return tuple(int(v + (255 - v) * f) for v in c[:3]) + (255,)


# ------------------------------------------------------------------ patterns
def pat_lines(col, step=38, tilt=22, box=(0, 0, 1000, 1800), stitches=True):
    def f(draw, c):
        s = c.ss; x0, y0, x1, y1 = box
        for x in range(int(x0), int(x1), step):
            draw.line([(x * s, y0 * s), ((x + tilt) * s, y1 * s)], fill=col, width=int(5 * s))
        if stitches:
            for y in range(int(y0) + 40, int(y1), 62):
                for x in range(int(x0) + 15, int(x1), step):
                    draw.line([(x * s, y * s), ((x + 10) * s, (y + 4) * s)], fill=col, width=int(3 * s))
    return f


def pat_mail(col, box):
    def f(draw, c):
        s = c.ss; x0, y0, x1, y1 = box; row = 0
        for y in range(int(y0), int(y1), 16):
            off = 9 if row % 2 else 0; row += 1
            for x in range(int(x0) + off, int(x1), 18):
                draw.arc([(x - 9) * s, (y - 7) * s, (x + 9) * s, (y + 7) * s], 0, 180, fill=col, width=int(3 * s))
    return f


def pat_curls(col, box, seed=5, density=900):
    def f(draw, c):
        r = random.Random(seed); s = c.ss; x0, y0, x1, y1 = box
        for _ in range(int((x1 - x0) * (y1 - y0) / density)):
            x = r.uniform(x0, x1); y = r.uniform(y0, y1); w = r.uniform(10, 24)
            draw.arc([(x - w) * s, (y - w * .7) * s, (x + w) * s, (y + w * .7) * s], r.uniform(170, 230), r.uniform(320, 380), fill=col, width=int(4 * s))
    return f


def pat_strands(col, box, seed=5, step=22):
    def f(draw, c):
        r = random.Random(seed); s = c.ss; x0, y0, x1, y1 = box
        for x in range(int(x0), int(x1), step):
            xx = x + r.uniform(-6, 6)
            draw.line([(xx * s, y0 * s), ((xx + r.uniform(-14, 14)) * s, y1 * s)], fill=col, width=int(4 * s))
    return f


def pat_combo(*fs):
    def f(draw, c):
        for g in fs:
            if g: g(draw, c)
    return f


def pat_emblems(kind, col, pts):
    """small heraldic charges on a surcoat: 'lily' (fleur-de-lis-ish), 'lion' (simplified gold beast), 'cross'"""
    def f(draw, c):
        s = c.ss
        for (x, y) in pts:
            if kind == "lily":
                for dx, dy, rx, ry in ((0, -14, 7, 16), (-12, -2, 9, 6), (12, -2, 9, 6), (0, 12, 4, 10)):
                    draw.ellipse([(x + dx - rx) * s, (y + dy - ry) * s, (x + dx + rx) * s, (y + dy + ry) * s], fill=col)
                draw.rectangle([(x - 12) * s, (y + 2) * s, (x + 12) * s, (y + 7) * s], fill=col)
            elif kind == "lion":
                draw.ellipse([(x - 26) * s, (y - 8) * s, (x + 18) * s, (y + 10) * s], fill=col)        # body
                draw.ellipse([(x + 10) * s, (y - 20) * s, (x + 30) * s, (y + 0) * s], fill=col)        # head
                for lx in (-20, -6, 6, 14):
                    draw.rectangle([(x + lx) * s, (y + 6) * s, (x + lx + 5) * s, (y + 20) * s], fill=col)
                draw.line([((x - 26) * s, y * s), ((x - 40) * s, (y - 18) * s)], fill=col, width=int(5 * s))
            elif kind == "cross":
                draw.rectangle([(x - 8) * s, (y - 40) * s, (x + 8) * s, (y + 40) * s], fill=col)
                draw.rectangle([(x - 30) * s, (y - 12) * s, (x + 30) * s, (y + 4) * s], fill=col)
    return f


# ------------------------------------------------------------------ face
def face(c, spec, fx, fy, r, k, expr, look):
    sk = spec.get("skin", WHITE)
    ex, es = r * 0.33, 30 * k * spec.get("eye_scale", 1.0)
    L, R = (fx - ex, fy - r * 0.0), (fx + ex, fy - r * 0.05)
    by_ = fy - r * 0.25; bw = 26 * k * spec.get("brow_scale", 1.0); bl = 92 * k * spec.get("brow_len", 1.0)
    my = fy + r * 0.40 * spec.get("mouth_drop", 1.0); glasses = spec.get("glasses")
    def eyes_dot(lk=look, sc=1.0):
        c.eye_dot(*L, es * sc, lk); c.eye_dot(*R, es * sc, lk)
    if expr == "neutral":
        eyes_dot()
        c.brow2(L[0], by_, bl, angle=-4, arch=8 * k, w=bw); c.brow2(R[0], by_ - 4 * k, bl, angle=4, arch=8 * k, w=bw)
        c.mouth_line(fx + 6 * k, my, 60 * k, curve=2 * k, thick=12 * k)
    elif expr == "curious":
        c.eye_white(*L, es * 1.05, look); c.eye_lid(*R, es, lid=0.42, tilt=-8, look=look, skin=sk)
        c.brow2(L[0], by_ - 26 * k, bl * 1.04, angle=-12, arch=26 * k, w=bw * 1.04)
        c.brow2(R[0], by_ + 8 * k, bl, angle=12, arch=4 * k, w=bw * 1.04, hook=10 * k)
        c.mouth_o(fx + 10 * k, my + 4 * k, 22 * k)
    elif expr == "smug":
        c.eye_lid(*L, es, lid=0.5, tilt=6, look=(0.6, 0), skin=sk); c.eye_lid(*R, es, lid=0.5, tilt=-6, look=(0.6, 0), skin=sk)
        c.brow2(L[0], by_ + 2 * k, bl, angle=-10, arch=10 * k, w=bw); c.brow2(R[0], by_ - 14 * k, bl, angle=-8, arch=18 * k, w=bw)
        c.mouth_line(fx + 14 * k, my, 74 * k, curve=-10 * k, tilt=10 * k, thick=12 * k)
    elif expr == "shocked":
        c.eye_white(*L, es * 1.25, (0, 0), pupil=0.26); c.eye_white(*R, es * 1.25, (0, 0), pupil=0.26)
        c.brow2(L[0], by_ - 34 * k, bl, angle=-14, arch=24 * k, w=bw * 0.92); c.brow2(R[0], by_ - 38 * k, bl, angle=14, arch=24 * k, w=bw * 0.92)
        c.mouth_open(fx + 6 * k, my - r * 0.04, 90 * k, 80 * k, teeth=False, smile=-0.2)
        c.sweat(fx + r * 0.66, fy - r * 0.28, 22 * k)
    elif expr == "disgusted":
        c.eye_lid(*L, es * 0.9, lid=0.6, tilt=-10, look=(0, 0.3), skin=sk); c.eye_lid(*R, es * 0.9, lid=0.6, tilt=10, look=(0, 0.3), skin=sk)
        c.brow2(L[0] + 6 * k, by_ + 14 * k, bl, angle=16, arch=6 * k, w=bw * 1.04); c.brow2(R[0] - 6 * k, by_ + 14 * k, bl, angle=-16, arch=6 * k, w=bw * 1.04)
        c.mouth_squiggle(fx + 8 * k, my + 2 * k, 96 * k, amp=5 * k, waves=3, thick=11 * k)
    elif expr == "laughing":
        c.eye_arc(*L, es, up=True); c.eye_arc(*R, es, up=True)
        c.brow2(L[0], by_ - 18 * k, bl, angle=-8, arch=18 * k, w=bw * 0.96); c.brow2(R[0], by_ - 22 * k, bl, angle=8, arch=18 * k, w=bw * 0.96)
        c.mouth_open(fx + 6 * k, my - r * 0.10, 130 * k, 92 * k, teeth=True, smile=0.35)
    elif expr == "angry":
        eyes_dot((0.0, 0.25), 0.85)
        c.brow2(L[0] + 4 * k, by_ + 18 * k, bl * 1.08, angle=24, arch=4 * k, w=bw * 1.15); c.brow2(R[0] - 4 * k, by_ + 18 * k, bl * 1.08, angle=-24, arch=4 * k, w=bw * 1.15)
        c.mouth_open(fx + 6 * k, my - r * 0.02, 84 * k, 46 * k, teeth=True, smile=-0.5)
    elif expr == "scared":
        c.eye_white(*L, es * 1.1, (0.5, 0.2), pupil=0.22); c.eye_white(*R, es * 1.1, (0.5, 0.2), pupil=0.22)
        c.brow2(L[0] + 4 * k, by_ - 20 * k, bl, angle=-22, arch=10 * k, w=bw * 0.9); c.brow2(R[0] - 4 * k, by_ - 20 * k, bl, angle=22, arch=10 * k, w=bw * 0.9)
        c.mouth_squiggle(fx + 6 * k, my, 80 * k, amp=7 * k, waves=4, thick=10 * k)
        c.sweat(fx - r * 0.70, fy - r * 0.30, 20 * k); c.sweat(fx + r * 0.68, fy - r * 0.20, 16 * k)
    elif expr == "sad":
        eyes_dot((0, 0.5), 0.9)
        c.brow2(L[0] + 4 * k, by_ - 6 * k, bl, angle=-20, arch=6 * k, w=bw); c.brow2(R[0] - 4 * k, by_ - 6 * k, bl, angle=20, arch=6 * k, w=bw)
        c.mouth_line(fx + 6 * k, my + 6 * k, 64 * k, curve=12 * k, thick=11 * k)
    elif expr == "determined":
        c.eye_lid(*L, es, lid=0.32, tilt=-12, look=(0.4, 0), skin=sk); c.eye_lid(*R, es, lid=0.32, tilt=12, look=(0.4, 0), skin=sk)
        c.brow2(L[0] + 4 * k, by_ + 12 * k, bl, angle=14, arch=6 * k, w=bw * 1.1); c.brow2(R[0] - 4 * k, by_ + 12 * k, bl, angle=-14, arch=6 * k, w=bw * 1.1)
        c.mouth_line(fx + 8 * k, my, 70 * k, curve=-2 * k, tilt=-4 * k, thick=13 * k)
    if glasses:
        for (x, y) in (L, R):
            c.d.ellipse([(x - es * 1.35) * c.ss, (y - es * 1.35) * c.ss, (x + es * 1.35) * c.ss, (y + es * 1.35) * c.ss], outline=INK, width=int(8 * k * c.ss))
        c.limb((L[0] + es * 1.35, L[1]), ((L[0] + R[0]) / 2, L[1] - 8 * k), (R[0] - es * 1.35, R[1]), 8 * k, 8 * k)


# ------------------------------------------------------------------ head
def draw_head(c, spec, hx, hy, k=1.0, expr="neutral", tilt=0.0, look=(0, 0)):
    H = spec["head"]; r = H.get("r", 225) * k; sk = spec.get("skin", WHITE)
    hair = spec.get("hair", {}); hat = spec.get("hat", {}); fh = spec.get("facial_hair", {})
    hcol = hair.get("color", (96, 60, 34, 255)); hdark = _darker(hcol, 0.55)
    box = (hx - r * 1.3, hy - r * 1.3, hx + r * 1.3, hy + r * 1.4)
    ht = hair.get("type", "none")
    # hair behind the head
    if ht == "curly":
        c.shape(shaggy_pts(hx, hy - r * 0.50, r * 1.06, r * 0.50, curls=26, depth=0.12, rot=tilt, seed=51), hcol, outline=11 * k, shade=0.35, shade_col=hdark[:3], pattern=pat_curls(hdark, box, 5), seed=51)
    elif ht == "long":
        pts = capsule_pts(hx, hy + r * 0.05, r * 2.3, r * 2.25, r * 2.05, rot=tilt, wobble=0.03, seed=53)
        c.shape(pts, hcol, outline=11 * k, shade=0.3, shade_col=hdark[:3], pattern=pat_strands(hdark, box, 7), seed=53)
    elif ht in ("bowl", "spiky"):
        c.shape(shaggy_pts(hx, hy - r * 0.38, r * 1.05, r * 0.64, curls=34 if ht == "spiky" else 60, depth=0.16 if ht == "spiky" else 0.03, rot=tilt, seed=54), hcol, outline=11 * k, shade=0.3, shade_col=hdark[:3], pattern=pat_strands(hdark, box, 9, 18), seed=54)
    # coif (mail hood) sits behind and around the head
    if hat.get("type") == "coif":
        mcol = hat.get("color", (150, 156, 166, 255))
        c.shape(head_pts(hx, hy + r * 0.04, r * 1.20, squash=1.05, bumps=0.02, rot=tilt, seed=70), mcol, outline=13 * k, shade=0.45, shade_col=(40, 44, 54), pattern=pat_mail(_darker(mcol, 0.6), box), seed=70)
    # the head itself: near-round with small hand-drawn bumps
    c.shape(head_pts(hx, hy, r, squash=H.get("squash", 0.97), bumps=H.get("bumps", 0.032), rot=tilt, seed=H.get("seed", 5)), sk, outline=15 * k, var=0.4, shade=0.45, seed=H.get("seed", 5))
    # fringe / front hair
    if ht == "curly":
        c.shape(shaggy_pts(hx - r * 0.02, hy - r * 0.66, r * 0.90, r * 0.26, curls=22, depth=0.22, rot=tilt, seed=52), hcol, outline=10 * k, shade=0.3, shade_col=hdark[:3], pattern=pat_curls(hdark, box, 6), seed=52)
    elif ht == "long":
        c.shape(shaggy_pts(hx - r * 0.05, hy - r * 0.70, r * 0.92, r * 0.30, curls=9, depth=0.14, rot=tilt + 0.08, seed=55), hcol, outline=10 * k, shade=0.3, shade_col=hdark[:3], pattern=pat_strands(hdark, box, 8), seed=55)
    elif ht == "bowl":
        pts = ellipse_pts(hx, hy - r * 0.52, r * 0.98, r * 0.40, rot=tilt, seed=56)
        pts = [(x, min(y, hy - r * 0.40 + 6 * math.sin(x * 0.2))) for x, y in pts]
        c.shape(pts, hcol, outline=10 * k, shade=0.3, shade_col=hdark[:3], pattern=pat_strands(hdark, box, 10, 16), seed=56)
    elif ht == "spiky":
        c.shape(shaggy_pts(hx, hy - r * 0.70, r * 0.86, r * 0.26, curls=12, depth=0.35, rot=tilt, seed=57), hcol, outline=10 * k, shade=0.3, shade_col=hdark[:3], seed=57)
    elif ht == "bald":
        c.limb((hx - r * 0.35, hy - r * 0.62), (hx - r * 0.2, hy - r * 0.78), (hx - r * 0.02, hy - r * 0.80), 10 * k, 4 * k, _HI)
    # facial hair under the features
    ft = fh.get("type", "none"); fcol = fh.get("color", hcol); fd = _darker(fcol, 0.55)
    fx, fy = hx + look[0] * r * 0.16, hy + r * 0.14 + look[1] * r * 0.06
    if ft == "beard":
        pts = [p for p in head_pts(hx, hy + r * 0.06, r * 1.0, squash=1.0, bumps=0.05, rot=tilt, seed=81)]
        cut = fy + r * 0.18
        pts = [p for p in pts if p[1] > cut]
        pts = pts + [(fx + r * 0.30, cut + r * 0.02), (fx, cut + r * 0.14), (fx - r * 0.30, cut + r * 0.02)]
        c.shape(pts, fcol, outline=11 * k, shade=0.35, shade_col=fd[:3], pattern=pat_strands(fd, box, 12, 20), seed=81)
    elif ft == "stubble":
        g = random.Random(4)
        for _ in range(60):
            a = g.uniform(0.15, math.pi - 0.15); rr = g.uniform(0.62, 0.9) * r
            c.dot(hx + math.cos(a) * rr * 0.95, hy + math.sin(a) * rr * 0.9, 2.6 * k, fill=(120, 110, 110, 255))
    # hats on top
    tt = hat.get("type", "none")
    if tt == "kettle":
        _kettle(c, hat, hx, hy, r, k, tilt)
    elif tt == "crown":
        _crown(c, hat, hx, hy, r, k, tilt)
    elif tt == "cap":
        col = hat.get("color", (120, 80, 50, 255))
        c.shape(ellipse_pts(hx - r * 0.02, hy - r * 0.62, r * 0.96, r * 0.50, rot=tilt, seed=90)[120:] + [(hx + r * 0.94, hy - r * 0.60)], col, outline=12 * k, shade=0.45, shade_col=_darker(col, 0.4)[:3], seed=90, hi=0.25)
        c.limb((hx - r * 0.96, hy - r * 0.60), (hx, hy - r * 0.54), (hx + r * 0.96, hy - r * 0.62), 26 * k, 26 * k, _darker(col, 0.7), outline=5 * k)
    if ft == "mustache" or ft == "droopy":
        for sgn in (-1, 1):
            a = (fx + sgn * 6 * k, fy + r * 0.26); end = (fx + sgn * r * 0.34, fy + r * (0.42 if ft == "droopy" else 0.24))
            mid = (fx + sgn * r * 0.18, fy + r * (0.20 if ft == "mustache" else 0.24))
            c.limb(a, mid, end, 30 * k, 10 * k, fcol, outline=5 * k)
    face(c, spec, fx, fy - r * 0.0, r, k, expr, look)
    if ft == "mustache" or ft == "droopy":       # redraw over the mouth top edge
        pass


def _kettle(c, hat, hx, hy, r, k, tilt):
    col = hat.get("color", (126, 135, 150, 255)); dk = _darker(col, 0.62)
    by = hy - r * 0.80
    c.shape(ellipse_pts(hx - r * 0.02, by, r * 1.22, r * 0.20, wobble=0.012, rot=tilt, seed=30), col, outline=12 * k, shade=0.55, shade_col=(30, 34, 46), light=(0.15, -1), shade_dist=0.05, seed=30)
    df = ellipse_pts(hx - r * 0.04, by - r * 0.02, r * 0.80, r * 0.58, n=240, rot=tilt, seed=31)
    c.shape(df[120:] + [df[0]], col, outline=12 * k, shade=0.45, shade_col=(30, 34, 46), seed=31, hi=0.35)
    band = ellipse_pts(hx - r * 0.04, by - r * 0.02, r * 0.80, r * 0.17, n=120, rot=tilt, seed=32)
    c.limb(band[66], band[90], band[114], 20 * k, 20 * k, dk, outline=5 * k)
    for i in (70, 80, 90, 100, 110):
        c.dot(band[i][0], band[i][1], 4.5 * k, fill=_lighter(col, 0.6))
    top = df[180]
    c.limb((top[0] - r * 0.02, top[1] + r * 0.02), (top[0] + r * 0.02, top[1] + r * 0.26), (top[0] + r * 0.05, by - r * 0.11), 9 * k, 6 * k)
    c.limb((hx - r * 0.56, by - r * 0.18), (hx - r * 0.50, by - r * 0.48), (hx - r * 0.22, by - r * 0.54), 12 * k, 5 * k, _HI)


def _crown(c, hat, hx, hy, r, k, tilt):
    col = hat.get("color", (240, 190, 50, 255)); gem = hat.get("gem", (200, 30, 40, 255)); lily = hat.get("lily", False)
    base_y = hy - r * 0.70; w = r * 0.78; h = r * 0.30; n = 5
    pts = [(hx - w, base_y)]
    for i in range(n):
        x0 = hx - w + 2 * w * i / n; x1 = hx - w + 2 * w * (i + 1) / n; xm = (x0 + x1) / 2
        pts += [(x0 + (x1 - x0) * 0.15, base_y - h), (xm, base_y - h * (1.9 if i % 2 == 0 else 1.55)), (x1 - (x1 - x0) * 0.15, base_y - h)]
    pts += [(hx + w, base_y), (hx + w * 0.98, base_y + h * 0.55), (hx - w * 0.98, base_y + h * 0.55)]
    ang = tilt; pts = [(hx + (x - hx) * math.cos(ang) - (y - hy) * math.sin(ang), hy + (x - hx) * math.sin(ang) + (y - hy) * math.cos(ang)) for x, y in pts]
    c.shape(pts, col, outline=11 * k, shade=0.45, shade_col=(110, 70, 10), seed=33, hi=0.45, var=0.25)
    for i in range(n):
        xm = hx - w + 2 * w * (i + 0.5) / n
        if lily and i % 2 == 0:
            c.dot(xm, base_y - h * 1.85, 12 * k, 16 * k, col)
        c.dot(xm, base_y + h * 0.12, 11 * k, 11 * k, INK); c.dot(xm, base_y + h * 0.12, 8 * k, 8 * k, gem if i % 2 == 0 else (40, 90, 200, 255))


# ------------------------------------------------------------------ body + pose
def draw_full(spec, path, expr="neutral", pose="stand", look=(0, 0), tilt=None, w=1000, h=1800):
    low = spec.get("detail") == "low"
    c = Canvas(w, h, ss=2 if low else 4, seed=7, light=(-0.75, -0.65))
    c.no_pattern = low                       # crowd/extras: flat clothes and hair, no textures
    B = spec["body"]; bw_t, bw_b, bh = B["w_top"], B["w_bot"], B["h"]; legs = spec.get("legs", 500)
    r = spec["head"].get("r", 225); off = spec.get("head_offset", 50)
    ground = h - 210; feet_y = ground
    by = feet_y - legs - bh * 0.40 + 30; bx = 500 + spec.get("body_x", 0)
    hx, hy = bx + off, by - bh / 2 - r * 0.62
    lim = spec.get("limb", 30); arm = spec.get("arm", 26)
    col = B["color"]; brot = B.get("rot", 0.10)
    sL, sR = (bx - bw_t * 0.38, by - bh * 0.30), (bx + bw_t * 0.40, by - bh * 0.28)
    hipL, hipR = (bx - bw_b * 0.17, by + bh * 0.38), (bx + bw_b * 0.19, by + bh * 0.38)
    mitt = spec.get("hands", (70, 48, 34, 255))

    def hand(p, rot=0.3):
        c.shape(ellipse_pts(p[0], p[1], 33, 35, rot=rot, seed=int(p[0])), mitt, outline=7, shade=0.2, seed=int(p[0]))

    # props behind
    prop = spec.get("prop")
    if pose == "hold_spear" or prop == "spear":
        px = sL[0] - 150
        c.limb((px, 175), (px, 900), (px, feet_y + 60), 15, 14, (138, 96, 58, 255), outline=5)
        c.shape([(px, 30), (px + 34, 150), (px, 200), (px - 34, 150)], (196, 204, 216, 255), outline=10, var=0.2, shade=0.25, seed=2)
    # legs
    c.limb(hipL, (hipL[0] - 38, (hipL[1] + feet_y) / 2), (hipL[0] - 16, feet_y), lim, lim * 0.8)
    c.limb((hipL[0] - 16, feet_y), (hipL[0] - 48, feet_y + 15), (hipL[0] - 80, feet_y + 11), lim * 0.8, lim * 0.6)
    c.limb(hipR, (hipR[0] + 70, (hipR[1] + feet_y) / 2 - 20), (hipR[0] + 20, feet_y - 7), lim, lim * 0.8)
    c.limb((hipR[0] + 20, feet_y - 7), (hipR[0] + 54, feet_y + 9), (hipR[0] + 86, feet_y + 5), lim * 0.8, lim * 0.6)
    # back arm (left)
    def arm_to(s, elbow, handp, front=False):
        c.limb(s, elbow, handp, arm, arm * 0.77); hand(handp)
    if pose in ("hold_spear",) or prop == "spear":
        arm_to(sL, (sL[0] - 95, sL[1] + 100), (sL[0] - 150, sL[1] + 215))
    elif pose == "hips":
        arm_to(sL, (sL[0] - 120, sL[1] + 110), (bx - bw_b * 0.48, by + bh * 0.08))
    elif pose == "arms_up":
        arm_to(sL, (sL[0] - 120, sL[1] - 80), (sL[0] - 170, sL[1] - 260))
    elif pose == "shrug":
        arm_to(sL, (sL[0] - 120, sL[1] + 90), (sL[0] - 200, sL[1] - 10))
    else:
        arm_to(sL, (sL[0] - 70, sL[1] + 160), (sL[0] - 60, sL[1] + 330))
    # body
    pattern = B.get("pattern"); pattern = pattern(bx, by, bw_t, bw_b, bh) if pattern else None
    c.shape(capsule_pts(bx, by, bw_t, bw_b, bh, rot=brot, seed=4), col, outline=15, shade=0.38, shade_col=_darker(col, 0.35)[:3], pattern=pattern, seed=4)
    for extra in B.get("extras", []):
        extra(c, bx, by, bw_t, bw_b, bh)
    # front arm (right)
    if pose == "point_up":
        arm_to(sR, (sR[0] + 135, sR[1] - 45), (sR[0] + 200, sR[1] - 213)); c.limb((sR[0] + 216, sR[1] - 243), (sR[0] + 222, sR[1] - 275), (sR[0] + 230, sR[1] - 307), 20, 16)
    elif pose == "hips":
        arm_to(sR, (sR[0] + 120, sR[1] + 110), (bx + bw_b * 0.48, by + bh * 0.08))
    elif pose == "arms_up":
        arm_to(sR, (sR[0] + 120, sR[1] - 80), (sR[0] + 170, sR[1] - 260))
    elif pose == "shrug":
        arm_to(sR, (sR[0] + 120, sR[1] + 90), (sR[0] + 200, sR[1] - 10))
    elif pose == "hold_sword" or prop == "sword":
        hp = (sR[0] + 110, sR[1] + 250)
        c.limb((hp[0] + 20, hp[1] + 10), (hp[0] + 120, hp[1] - 150), (hp[0] + 210, hp[1] - 330), 22, 10, (205, 212, 222, 255), outline=6)
        c.limb((hp[0] - 30, hp[1] + 34), (hp[0] + 20, hp[1] + 10), (hp[0] + 70, hp[1] - 14), 14, 14, (180, 140, 40, 255), outline=5)
        arm_to(sR, (sR[0] + 80, sR[1] + 140), hp)
    else:
        arm_to(sR, (sR[0] + 70, sR[1] + 160), (sR[0] + 60, sR[1] + 330))
    draw_head(c, spec, hx, hy, 1.0, expr, tilt if tilt is not None else spec.get("tilt", -0.08), look)
    if low:                                  # small card is enough for the background
        c.im.resize((w // 2, h // 2), Image.LANCZOS).save(path); return path
    return c.save(path)


# ------------------------------------------------------------------ crowds / extras (simplified on purpose)
def extra_spec(seed, colors, hats=("kettle", "cap", "none", "coif"), hair_cols=((96, 60, 34, 255), (60, 40, 28, 255), (210, 170, 90, 255), (140, 70, 30, 255))):
    """Background extra: same style grammar, low detail. Built from a few templates with random swaps so
    a crowd never looks like clones. colors = the faction's muted palette (never a hero's unique colour)."""
    g = random.Random(seed)
    hat = g.choice(hats); hair = g.choice(("curly", "bowl", "spiky", "bald"))
    if hat == "coif": hair = "none"            # mail hood covers the hair
    build = g.choice(((240, 280, 540, 470), (300, 340, 520, 420), (210, 230, 600, 540), (330, 370, 500, 380)))
    return dict(name=f"extra{seed}", detail="low", head=dict(r=g.uniform(200, 235), squash=g.uniform(0.92, 1.08), seed=seed),
                head_offset=g.choice((-45, -30, 30, 50)), tilt=g.uniform(-0.1, 0.1), legs=build[3], limb=28, arm=24,
                hair=dict(type=hair, color=g.choice(hair_cols)), hat=dict(type=hat),
                facial_hair=dict(type=g.choice(("none", "none", "mustache", "stubble")), color=(70, 46, 30, 255)),
                body=dict(w_top=build[0], w_bot=build[1], h=build[2], color=g.choice(colors), rot=g.uniform(-0.1, 0.1)))


def crowd_cards(n, out_dir, colors, expr_mix=("laughing", "smug", "laughing", "neutral"), pose_mix=("stand", "arms_up", "hips", "stand"), seed0=100, **kw):
    """Render n extra cards (one shared crowd emotion with small variations). Returns the file list."""
    import os
    os.makedirs(out_dir, exist_ok=True); g = random.Random(seed0); files = []
    for i in range(n):
        sp = extra_spec(seed0 + i, colors, **kw)
        p = os.path.join(out_dir, f"extra_{seed0 + i:03d}.png")
        draw_full(sp, p, g.choice(expr_mix), g.choice(pose_mix), look=(g.uniform(-0.5, 0.5), 0)); files.append(p)
    return files


# ------------------------------------------------------------------ lineup
def lineup(specs, path, exprs=("neutral", "smug", "shocked", "laughing", "angry"), poses=None):
    """row 1: full bodies; row 2: silhouettes (distinctness check); rows 3+: expressions per character"""
    import os, tempfile
    n = len(specs); cw = 360; W = cw * n
    tmp = tempfile.mkdtemp()
    fulls = []
    for i, sp in enumerate(specs):
        p = os.path.join(tmp, f"{i}.png")
        draw_full(sp, p, sp.get("default_expr", "neutral"), (poses or {}).get(sp["name"], sp.get("default_pose", "stand")))
        fulls.append(Image.open(p).resize((cw, int(cw * 1.8)), Image.LANCZOS))
    hh = int(cw * 1.8); eh = 300
    sheet = Image.new("RGBA", (W, hh * 2 + eh * len(exprs) + 60), (214, 224, 236, 255))
    d = ImageDraw.Draw(sheet)
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    except Exception:
        font = None
    for i, f in enumerate(fulls):
        sheet.alpha_composite(f, (i * cw, 0))
        sil = Image.new("RGBA", f.size, (20, 20, 24, 255)); sil.putalpha(f.getchannel("A"))
        sheet.alpha_composite(sil, (i * cw, hh))
        d.text((i * cw + 14, hh * 2 - 48), specs[i]["name"], fill=(30, 30, 30, 255), font=font)
    for j, e in enumerate(exprs):
        c = Canvas(W, eh, ss=3, light=(-0.75, -0.65))
        for i, sp in enumerate(specs):
            draw_head(c, sp, i * cw + cw / 2, eh * 0.58, 0.5, e, 0.04 * (1 if i % 2 else -1), (0.4, 0) if e == "smug" else (0, 0))
        img = c.im.resize((W, eh), Image.LANCZOS)
        sheet.alpha_composite(img, (0, hh * 2 + 60 + j * eh))
        d.text((10, hh * 2 + 64 + j * eh), e, fill=(30, 30, 30, 255), font=font)
    sheet.convert("RGB").save(path, quality=92)
    return path
