"""Bogis, French foot soldier, 1204. Pose: looking up, pointing up, spear in the other hand. Expression: curious."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../tools"))
from charkit import Canvas, INK

SKIN = (246, 240, 228, 255)
STEEL = (150, 160, 172, 255); STEEL_HI = (196, 204, 214, 255)
BLUE = (44, 84, 168, 255); GOLD = (236, 190, 60, 255); BROWN = (120, 78, 44, 255); WOOD = (150, 104, 60, 255)
MAIL = (110, 116, 124, 255)

def draw(path, expr="curious"):
    c = Canvas(1000, 1800, ss=4, seed=7)
    # spear (behind body)
    c.stroke([(236, 190), (236, 1640)], 14, WOOD, 6)
    c.poly([(236, 40), (268, 160), (236, 205), (204, 160)], STEEL_HI, 10)
    # legs + shoes
    c.line([(462, 1150), (448, 1575)], 11); c.line([(540, 1150), (556, 1575)], 11)
    c.blob(430, 1585, 44, 22, INK, outline=0, wobble=0.02, seed=3)
    c.blob(578, 1585, 44, 22, INK, outline=0, wobble=0.02, seed=4)
    # body: mail shirt hem under a blue tabard
    c.poly([(400, 1060), (600, 1060), (622, 1175), (378, 1175)], MAIL, 12)
    c.poly([(418, 770), (582, 770), (628, 1150), (372, 1150)], BLUE, 13)
    c.poly([(388, 1000), (612, 1000), (616, 1030), (384, 1030)], BROWN, 8)          # belt
    c.blob(500, 905, 26, 32, GOLD, outline=7, wobble=0.05, seed=11)                 # simple lily badge
    c.blob(500, 862, 12, 18, GOLD, outline=6, wobble=0.04, seed=12)
    # arms: left holds spear, right points up at the toilet
    c.line([(432, 800), (330, 890), (244, 960)], 10)
    c.blob(240, 962, 24, 22, SKIN, outline=8, seed=21)
    c.line([(572, 800), (735, 735), (835, 610)], 10)
    c.blob(842, 598, 24, 24, SKIN, outline=8, seed=22)
    c.line([(850, 578), (872, 525)], 9)                                              # pointing finger
    # head: pale wavy bean, slightly tilted back (looking up)
    c.blob(505, 535, 232, 262, SKIN, outline=16, wobble=0.045, bean=0.07, rot=-0.06, seed=5)
    # kettle helmet: brim + dome
    c.blob(500, 318, 318, 48, STEEL, outline=14, wobble=0.02, rot=-0.06, seed=31)
    c.blob(500, 266, 214, 118, STEEL, outline=14, wobble=0.03, rot=-0.06, seed=32)
    c.blob(445, 221, 70, 26, STEEL_HI, outline=0, wobble=0.05, rot=-0.3, seed=33)    # highlight
    # face (eyes high = looking up)
    if expr == "curious":
        c.dot(430, 470, 17, 22); c.dot(578, 462, 17, 22)
        c.dot(425, 462, 6, 7, (255, 255, 255, 255)); c.dot(573, 454, 6, 7, (255, 255, 255, 255))
        c.arc([392, 398, 472, 446], 200, 330, 11)          # left brow raised, arched
        c.line([(548, 420), (612, 414)], 11)               # right brow flat
        c.blob(512, 612, 20, 24, (90, 40, 40, 255), outline=9, wobble=0.06, seed=41)  # small "o" mouth
    c.save(path)
    return path

if __name__ == "__main__":
    print(draw(sys.argv[1] if len(sys.argv) > 1 else "bogis.png"))
