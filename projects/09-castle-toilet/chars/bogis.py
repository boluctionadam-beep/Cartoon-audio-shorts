"""Bogis, French foot soldier, 1204 (original design).
Round-ish white head with small bumps, offset from the body axis; shaggy brown hair; kettle helmet with ridge,
band, rivets and a specular streak; padded blue gambeson on a capsule body; tapered limbs; expression presets.
  python3 bogis.py card.png [expr]      full body (default expr: curious)
  python3 bogis.py --sheet sheet.png    expression sheet (heads)"""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../tools"))
from charkit import Canvas, INK, WHITE, ellipse_pts, capsule_pts, head_pts, shaggy_pts

BLUE = (46, 82, 160, 255); BLUE_D = (30, 56, 118, 255)
STEEL = (126, 135, 150, 255); STEEL_D = (78, 86, 100, 255); WOOD = (138, 96, 58, 255); STEEL_HI = (196, 204, 216, 255)
BELT = (104, 66, 38, 255); GOLD = (236, 188, 58, 255); HAIR = (96, 60, 34, 255); HAIR_D = (52, 30, 16, 255); MITT = (70, 48, 34, 255)


def hair_curls(seed, box):
    def f(draw, c):
        r = random.Random(seed); s = c.ss; x0, y0, x1, y1 = box
        for _ in range(int((x1 - x0) * (y1 - y0) / 900)):
            x = r.uniform(x0, x1); y = r.uniform(y0, y1); w = r.uniform(10, 24)
            draw.arc([(x - w) * s, (y - w * .7) * s, (x + w) * s, (y + w * .7) * s], r.uniform(170, 230), r.uniform(320, 380), fill=HAIR_D, width=int(4 * s))
    return f


def gambeson(draw, c):
    s = c.ss
    for x in range(300, 740, 38):
        draw.line([(x * s, 520 * s), ((x + 22) * s, 1170 * s)], fill=BLUE_D, width=int(5 * s))
    for y in range(600, 1150, 62):
        for x in range(320, 740, 38):
            draw.line([(x * s, y * s), ((x + 10) * s, (y + 4) * s)], fill=BLUE_D, width=int(3 * s))
    draw.polygon([c.P([(290, 978)])[0], c.P([(740, 1010)])[0], c.P([(740, 1046)])[0], c.P([(290, 1014)])[0]], fill=BELT)


def head(c, hx, hy, k=1.0, expr="curious", tilt=-0.10, look=(0.5, -0.6)):
    r = 225 * k
    # --- hair mass behind the head (only the messy back/sides peek out)
    hb = (hx - r * 1.2, hy - r * 1.1, hx + r * 1.2, hy + r * 0.1)
    c.shape(shaggy_pts(hx, hy - r * 0.50, r * 1.06, r * 0.50, curls=26, depth=0.12, rot=tilt, seed=51), HAIR,
            outline=11 * k, shade=0.35, shade_col=(30, 16, 8), pattern=hair_curls(5, hb), seed=51)
    # --- head with slight hand-drawn bumps
    c.shape(head_pts(hx, hy, r, squash=0.97, bumps=0.032, rot=tilt, seed=5), WHITE, outline=15 * k, var=0.4, shade=0.45, seed=5)
    # --- curly fringe in front: hairline across the upper forehead
    c.shape(shaggy_pts(hx - r * 0.02, hy - r * 0.66, r * 0.90, r * 0.26, curls=22, depth=0.22, rot=tilt, seed=52), HAIR,
            outline=10 * k, shade=0.3, shade_col=(30, 16, 8), pattern=hair_curls(6, hb), seed=52)
    # --- kettle helmet, sitting high and tipped back
    by = hy - r * 0.80
    brim = ellipse_pts(hx - r * 0.02, by, r * 1.22, r * 0.20, wobble=0.012, rot=tilt, seed=30)
    c.shape(brim, STEEL, outline=12 * k, shade=0.55, shade_col=(30, 34, 46), light=(0.15, -1), shade_dist=0.05, seed=30)
    dome_full = ellipse_pts(hx - r * 0.04, by - r * 0.02, r * 0.80, r * 0.58, n=240, rot=tilt, seed=31)
    dome = dome_full[120:] + [dome_full[0]]
    c.shape(dome, STEEL, outline=12 * k, shade=0.45, shade_col=(30, 34, 46), seed=31, hi=0.35)
    band = ellipse_pts(hx - r * 0.04, by - r * 0.02, r * 0.80, r * 0.17, n=120, rot=tilt, seed=32)
    c.limb(band[66], band[90], band[114], 20 * k, 20 * k, STEEL_D, outline=5 * k)
    for i in (70, 80, 90, 100, 110):
        c.dot(band[i][0], band[i][1], 4.5 * k, fill=STEEL_HI)
    top = dome_full[180]
    c.limb((top[0] - r * 0.02, top[1] + r * 0.02), (top[0] + r * 0.02, top[1] + r * 0.26), (top[0] + r * 0.05, by - r * 0.11), 9 * k, 6 * k)
    c.limb((hx - r * 0.56, by - r * 0.18), (hx - r * 0.50, by - r * 0.48), (hx - r * 0.22, by - r * 0.54), 12 * k, 5 * k, (238, 242, 248, 255))
    # --- face (shifted toward the look direction)
    fx, fy = hx + look[0] * r * 0.16, hy + r * 0.14 + look[1] * r * 0.06
    ex, ey, es = r * 0.33, fy - r * 0.02, 30 * k
    L, R = (fx - ex, ey + r * 0.02), (fx + ex, ey - r * 0.03)
    by_ = ey - r * 0.27
    if expr == "neutral":
        c.eye_dot(*L, es, look); c.eye_dot(*R, es, look)
        c.brow2(L[0], by_, 90 * k, angle=-4, arch=8 * k, w=26 * k); c.brow2(R[0], by_ - 4 * k, 90 * k, angle=4, arch=8 * k, w=26 * k)
        c.mouth_line(fx + 6 * k, fy + r * 0.40, 60 * k, curve=2 * k, thick=12 * k)
    elif expr == "curious":          # spotting the toilet: one wide eye, one suspicious squint
        c.eye_white(*L, es * 1.05, look); c.eye_lid(*R, es, lid=0.42, tilt=-8, look=look)
        c.brow2(L[0], by_ - 26 * k, 96 * k, angle=-12, arch=26 * k, w=27 * k)
        c.brow2(R[0], by_ + 8 * k, 92 * k, angle=12, arch=4 * k, w=27 * k, hook=10 * k)
        c.mouth_o(fx + 10 * k, fy + r * 0.42, 22 * k)
    elif expr == "smug":
        c.eye_lid(*L, es, lid=0.5, tilt=6, look=(0.6, 0)); c.eye_lid(*R, es, lid=0.5, tilt=-6, look=(0.6, 0))
        c.brow2(L[0], by_ + 2 * k, 92 * k, angle=-10, arch=10 * k, w=26 * k); c.brow2(R[0], by_ - 14 * k, 92 * k, angle=-8, arch=18 * k, w=26 * k)
        c.mouth_line(fx + 14 * k, fy + r * 0.40, 74 * k, curve=-10 * k, tilt=10 * k, thick=12 * k)
    elif expr == "shocked":
        c.eye_white(*L, es * 1.25, (0, 0), pupil=0.26); c.eye_white(*R, es * 1.25, (0, 0), pupil=0.26)
        c.brow2(L[0], by_ - 34 * k, 90 * k, angle=-14, arch=24 * k, w=24 * k); c.brow2(R[0], by_ - 38 * k, 90 * k, angle=14, arch=24 * k, w=24 * k)
        c.mouth_open(fx + 6 * k, fy + r * 0.36, 90 * k, 80 * k, teeth=False, smile=-0.2)
        c.sweat(hx + r * 0.82, hy - r * 0.15, 22 * k)
    elif expr == "disgusted":
        c.eye_lid(*L, es * 0.9, lid=0.6, tilt=-10, look=(0, 0.3)); c.eye_lid(*R, es * 0.9, lid=0.6, tilt=10, look=(0, 0.3))
        c.brow2(L[0] + 6 * k, by_ + 14 * k, 92 * k, angle=16, arch=6 * k, w=27 * k); c.brow2(R[0] - 6 * k, by_ + 14 * k, 92 * k, angle=-16, arch=6 * k, w=27 * k)
        c.mouth_squiggle(fx + 8 * k, fy + r * 0.42, 96 * k, amp=5 * k, waves=3, thick=11 * k)
    elif expr == "laughing":
        c.eye_arc(*L, es * 1.0, up=True); c.eye_arc(*R, es * 1.0, up=True)
        c.brow2(L[0], by_ - 18 * k, 90 * k, angle=-8, arch=18 * k, w=25 * k); c.brow2(R[0], by_ - 22 * k, 90 * k, angle=8, arch=18 * k, w=25 * k)
        c.mouth_open(fx + 6 * k, fy + r * 0.30, 130 * k, 92 * k, teeth=True, smile=0.35)
    elif expr == "angry":
        c.eye_dot(*L, es * 0.85, (0.3, 0.2)); c.eye_dot(*R, es * 0.85, (-0.3, 0.2))
        c.brow2(L[0] + 4 * k, by_ + 16 * k, 100 * k, angle=24, arch=4 * k, w=30 * k); c.brow2(R[0] - 4 * k, by_ + 16 * k, 100 * k, angle=-24, arch=4 * k, w=30 * k)
        c.mouth_line(fx + 6 * k, fy + r * 0.44, 74 * k, curve=14 * k, thick=13 * k)


def body(c, expr):
    # spear behind everything
    c.limb((262, 175), (262, 900), (262, 1660), 15, 14, WOOD, outline=5)
    c.shape([(262, 30), (296, 150), (262, 200), (228, 150)], STEEL_HI, outline=10, var=0.2, shade=0.25, seed=2)
    # legs: one straight, one bent, hooked feet
    c.limb((452, 1080), (414, 1330), (436, 1585), 30, 24); c.limb((436, 1585), (404, 1600), (372, 1596), 24, 18)
    c.limb((548, 1080), (622, 1320), (570, 1578), 30, 24); c.limb((570, 1578), (604, 1594), (636, 1590), 24, 18)
    c.limb((410, 720), (310, 820), (268, 940), 26, 20)
    c.shape(ellipse_pts(264, 950, 34, 30, rot=0.4, seed=21), MITT, outline=7, shade=0.2, seed=21)
    c.shape(capsule_pts(505, 860, 260, 320, 580, rot=0.12, seed=4), BLUE, outline=15, shade=0.38, shade_col=(20, 26, 60), pattern=gambeson, seed=4)
    c.shape(ellipse_pts(470, 770, 26, 30, wobble=0.06, seed=11), GOLD, outline=7, shade=0.2, seed=11)
    c.limb((600, 700), (735, 655), (800, 487), 26, 20)
    c.shape(ellipse_pts(806, 467, 33, 35, rot=0.3, seed=22), MITT, outline=7, shade=0.2, seed=22)
    c.limb((816, 437), (822, 405), (830, 373), 20, 16)


def draw(path, expr="curious"):
    c = Canvas(1000, 1800, ss=4, seed=7, light=(-0.75, -0.65))
    body(c, expr)
    head(c, 560, 430, 1.0, expr, tilt=-0.10, look=(0.5, -0.6))     # head offset to the right of the body axis
    return c.save(path)


def sheet(path):
    exprs = ["neutral", "curious", "smug", "shocked", "disgusted", "laughing", "angry"]
    exprs = exprs[:6]
    c = Canvas(1500, 1080, ss=3, seed=9, light=(-0.75, -0.65))
    for i, e in enumerate(exprs):
        cx = 250 + (i % 3) * 500; cy = 300 + (i // 3) * 520
        look = {"curious": (0.5, -0.6), "smug": (0.6, 0), "disgusted": (0, 0.3)}.get(e, (0, 0))
        head(c, cx, cy, 0.78, e, tilt=-0.06 if i % 2 else 0.05, look=look)
    return c.save(path)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--sheet":
        print(sheet(sys.argv[2]))
    else:
        print(draw(sys.argv[1] if len(sys.argv) > 1 else "bogis.png", sys.argv[2] if len(sys.argv) > 2 else "curious"))
