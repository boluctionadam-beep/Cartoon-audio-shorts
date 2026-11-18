"""Cast of short 09 (The Castle That Fell Through Its Toilet). Each character = one spec for tools/cast.py.
Distinctness: unique dominant colour, headwear, hair/facial hair, height class and body shape (see CLAUDE.md).
  python3 cast.py lineup OUT.jpg
  python3 cast.py card NAME EXPR POSE OUT.png [lookx looky]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../tools"))
from cast import draw_full, lineup, pat_lines, pat_mail, pat_emblems, pat_combo, pat_curls
from charkit import ellipse_pts

def band(y_rel, col, h=36):
    """belt-like band across the body, clipped to it (pattern factory piece)"""
    def make(bx, by, wt, wb, bh):
        def f(draw, c):
            y = by + bh * y_rel; s = c.ss
            draw.polygon([((bx - 400) * s, (y - h / 2) * s), ((bx + 400) * s, (y - h / 2 + 30) * s), ((bx + 400) * s, (y + h / 2 + 30) * s), ((bx - 400) * s, (y + h / 2) * s)], fill=col)
        return f
    return make

def P(*factories):
    def make(bx, by, wt, wb, bh):
        return pat_combo(*[fa(bx, by, wt, wb, bh) for fa in factories])
    return make

def quilt(col):
    return lambda bx, by, wt, wb, bh: pat_lines(col, 38, 22, (bx - 260, by - bh / 2, bx + 260, by + bh / 2))

def mail_lower(col, from_rel=0.25):
    return lambda bx, by, wt, wb, bh: pat_mail(col, (bx - 260, by + bh * from_rel, bx + 260, by + bh / 2 + 20))

def emblems(kind, col, rel_pts):
    return lambda bx, by, wt, wb, bh: pat_emblems(kind, col, [(bx + x * wt, by + y * bh) for x, y in rel_pts])

def ermine(y_rel=-0.40):
    def make(bx, by, wt, wb, bh):
        def f(draw, c):
            s = c.ss; y = by + bh * y_rel
            draw.rectangle([(bx - 300) * s, (by - bh) * s, (bx + 300) * s, (y + 40) * s], fill=(248, 248, 244, 255))
            for i, x in enumerate(range(int(bx - 200), int(bx + 220), 60)):
                yy = y - 30 + (i % 2) * 34
                draw.polygon([(x * s, (yy - 10) * s), ((x + 8) * s, (yy + 12) * s), ((x - 8) * s, (yy + 12) * s)], fill=(20, 20, 20, 255))
        return f
    return make

def patch(col, dx=-0.14, dy=-0.18, r=28):
    def ex(c, bx, by, wt, wb, bh):
        c.shape(ellipse_pts(bx + dx * wt, by + dy * bh, r, r * 1.1, wobble=0.06, seed=11), col, outline=7, shade=0.2, seed=11)
    return ex

GOLD = (236, 188, 58, 255)
SPECS = {
 "bogis": dict(name="Bogis", head=dict(r=225, squash=0.97, seed=5), head_offset=55, tilt=-0.10, legs=505,
     hair=dict(type="curly", color=(96, 60, 34, 255)), hat=dict(type="kettle"),
     body=dict(w_top=260, w_bot=320, h=580, color=(46, 82, 160, 255), rot=0.12,
               pattern=P(quilt((30, 56, 118, 255)), band(0.22, (104, 66, 38, 255))), extras=[patch(GOLD, -0.14, -0.16)]),
     prop="spear", default_expr="curious", default_pose="point_up"),
 "richard": dict(name="Richard", head=dict(r=205, squash=1.0, seed=12), head_offset=-38, tilt=0.06, legs=560, limb=32, arm=28,
     hair=dict(type="long", color=(200, 98, 40, 255)), facial_hair=dict(type="beard", color=(190, 90, 36, 255)),
     hat=dict(type="crown", color=(242, 192, 54, 255)),
     body=dict(w_top=300, w_bot=270, h=650, color=(176, 30, 38, 255), rot=-0.06,
               pattern=P(emblems("lion", GOLD, [(0.0, -0.18), (0.0, 0.05)]), band(0.30, (120, 80, 30, 255), 30))),
     prop="sword", default_expr="smug", default_pose="hold_sword"),
 "philip": dict(name="Philip", head=dict(r=245, squash=0.93, seed=21), head_offset=32, tilt=-0.04, legs=360, limb=32,
     hair=dict(type="bowl", color=(64, 42, 30, 255)), facial_hair=dict(type="mustache", color=(52, 34, 24, 255)),
     hat=dict(type="crown", color=(242, 192, 54, 255), lily=True, gem=(40, 90, 200, 255)),
     body=dict(w_top=360, w_bot=400, h=520, color=(86, 62, 156, 255), rot=0.04,
               pattern=P(emblems("lily", GOLD, [(-0.25, 0.0), (0.22, 0.02), (-0.02, 0.22), (-0.28, 0.32), (0.25, 0.30)]), ermine(-0.38))),
     default_expr="determined", default_pose="hips"),
 "roger": dict(name="Roger", head=dict(r=198, squash=1.12, seed=31), head_offset=44, tilt=0.05, legs=560, limb=24, arm=22,
     hair=dict(type="none"), facial_hair=dict(type="droopy", color=(120, 100, 84, 255)), hat=dict(type="coif", color=(150, 156, 166, 255)),
     body=dict(w_top=220, w_bot=250, h=640, color=(56, 120, 72, 255), rot=-0.03,
               pattern=P(mail_lower((90, 96, 106, 255), 0.30), band(0.20, (90, 60, 34, 255), 26), emblems("cross", (232, 232, 226, 255), [(0.0, -0.12)]))),
     default_expr="scared", default_pose="shrug"),
 "gaston": dict(name="Gaston", head=dict(r=232, squash=0.90, seed=41), head_offset=62, tilt=-0.05, legs=410, limb=32,
     hair=dict(type="bald"), facial_hair=dict(type="stubble"), hat=dict(type="cap", color=(122, 78, 44, 255)),
     body=dict(w_top=340, w_bot=390, h=560, color=(204, 112, 40, 255), rot=0.08,
               pattern=P(band(0.18, (90, 56, 30, 255), 40), quilt((168, 86, 28, 255)))),
     default_expr="laughing", default_pose="arms_up"),
 "tibo": dict(name="Tibo", head=dict(r=208, squash=1.05, seed=51), head_offset=-30, tilt=0.07, legs=560, limb=24, arm=22, eye_scale=0.9,
     hair=dict(type="spiky", color=(232, 196, 92, 255)),
     body=dict(w_top=220, w_bot=240, h=600, color=(214, 178, 58, 255), rot=-0.07,
               pattern=P(band(0.24, (110, 70, 36, 255), 28), quilt((176, 140, 40, 255)))),
     default_expr="curious", default_pose="stand"),
}

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "lineup":
        print(lineup(list(SPECS.values()), sys.argv[2], exprs=("neutral", "curious", "smug", "shocked", "disgusted", "laughing", "angry", "scared")))
    elif cmd == "card":
        name, expr, pose, out = sys.argv[2:6]; look = (float(sys.argv[6]), float(sys.argv[7])) if len(sys.argv) > 7 else (0, 0)
        print(draw_full(SPECS[name], out, expr, pose, look))
