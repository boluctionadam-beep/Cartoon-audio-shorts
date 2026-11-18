"""Bogis, French foot soldier, 1204 (original design). Pose: head tilted back, looking up, pointing up, spear.
Style: round white head with soft shading, capsule body in a padded gambeson, tapered limbs, thick brows."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../tools"))
from charkit import Canvas, INK, WHITE, ellipse_pts, capsule_pts

BLUE = (46, 82, 160, 255); BLUE_D = (30, 56, 118, 255)
STEEL = (120, 128, 140, 255); WOOD = (138, 96, 58, 255); STEEL_HI = (190, 198, 208, 255)
BELT = (104, 66, 38, 255); GOLD = (236, 188, 58, 255); HAIR = (92, 58, 34, 255); MITT = (70, 48, 34, 255)


def gambeson(draw, c):
    s = c.ss
    for x in range(330, 700, 38):                                   # padded vertical channels
        draw.line([(x * s, 540 * s), ((x + 14) * s, 1160 * s)], fill=BLUE_D, width=int(5 * s))
    for y in range(600, 1150, 62):                                  # stitch dashes
        for x in range(345, 700, 38):
            draw.line([(x * s, y * s), ((x + 10) * s, (y + 4) * s)], fill=BLUE_D, width=int(3 * s))
    draw.polygon([(c.P([(300, 985)])[0]), (c.P([(720, 1005)])[0]), (c.P([(720, 1040)])[0]), (c.P([(300, 1020)])[0])], fill=BELT)


def hair_curls(draw, c):
    import random
    r = random.Random(3); s = c.ss; dark = (58, 34, 18, 255)
    for _ in range(160):
        x = r.uniform(200, 740); y = r.uniform(180, 470); w = r.uniform(14, 30)
        draw.arc([(x - w) * s, (y - w * 0.7) * s, (x + w) * s, (y + w * 0.7) * s], r.uniform(180, 230), r.uniform(320, 360), fill=dark, width=int(4 * s))


def draw(path, expr="curious"):
    c = Canvas(1000, 1800, ss=4, seed=7, light=(-0.75, -0.65))
    # spear behind everything
    c.limb((300, 175), (300, 900), (300, 1660), 15, 14, WOOD, outline=5)
    c.shape([(300, 30), (334, 150), (300, 200), (266, 150)], STEEL_HI, outline=10, var=0.2, shade=0.25, seed=2)
    # legs (one straight, one bent) with small hooked feet
    c.limb((462, 1080), (424, 1330), (446, 1585), 30, 24)
    c.limb((446, 1585), (414, 1600), (382, 1596), 24, 18)
    c.limb((552, 1080), (625, 1320), (574, 1578), 30, 24)
    c.limb((574, 1578), (608, 1594), (640, 1590), 24, 18)
    # left arm to the spear (behind body)
    c.limb((420, 720), (330, 820), (304, 940), 26, 20)
    c.shape(ellipse_pts(300, 950, 34, 30, rot=0.4, seed=21), MITT, outline=7, shade=0.2, seed=21)
    # body: soft capsule, slight lean back
    c.shape(capsule_pts(510, 860, 260, 320, 580, rot=0.10, seed=4), BLUE, outline=15, shade=0.38, shade_col=(20, 26, 60), pattern=gambeson, seed=4)
    c.shape(ellipse_pts(470, 760, 26, 30, wobble=0.06, seed=11), GOLD, outline=7, shade=0.2, seed=11)   # lily patch
    # right arm pointing up at the toilet (in front)
    c.limb((590, 700), (725, 650), (790, 482), 26, 20)
    c.shape(ellipse_pts(796, 462, 33, 35, rot=0.3, seed=22), MITT, outline=7, shade=0.2, seed=22)
    c.limb((806, 432), (812, 400), (820, 368), 20, 16)
    # hair mass behind the head (shows at the sides under the brim)
    c.shape(ellipse_pts(468, 330, 262, 150, wobble=0.07, rot=-0.12, seed=51), HAIR, outline=14, shade=0.3, shade_col=(30, 18, 10), pattern=hair_curls, seed=51)
    # head: near-round white, tilted back
    c.shape(ellipse_pts(468, 445, 228, 222, wobble=0.022, bean=0.03, rot=-0.12, seed=5), WHITE, outline=15, shade=0.42, seed=5)
    # hair tufts under the helmet
    # kettle helmet: brim + dome with highlight
    dome = [p for p in ellipse_pts(462, 236, 205, 150, n=240, rot=-0.12, seed=31)]
    c.shape(ellipse_pts(462, 240, 300, 50, wobble=0.015, rot=-0.12, seed=30), STEEL, outline=13, shade=0.35, shade_col=(30, 34, 44), seed=30, hi=0.25)
    top = [p for i, p in enumerate(dome) if i >= 120] + [dome[0]]
    c.shape(top, STEEL, outline=13, shade=0.4, shade_col=(30, 34, 44), seed=31, hi=0.55)
    # face: looking up and to the right
    if expr == "curious":
        c.eye(392, 398, 31, look=(0.35, -0.6)); c.eye(532, 383, 31, look=(0.35, -0.6))
        c.brow(384, 330, 100, angle=-14, arch=20, w=27)       # raised, arched
        c.brow(536, 330, 96, angle=10, arch=2, w=27)          # lower, flatter: suspicious
        c.shape(ellipse_pts(470, 530, 22, 28, wobble=0.05, seed=41), (120, 44, 52, 255), outline=8, shade=0, seed=41)
    c.save(path)
    return path


if __name__ == "__main__":
    print(draw(sys.argv[1] if len(sys.argv) > 1 else "bogis.png"))
