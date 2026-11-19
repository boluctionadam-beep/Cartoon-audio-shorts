"""Short 09 sets v2: real textures + dense set dressing (CLAUDE.md 5c). Same coordinate conventions as sets09.py."""
import bpy, math, random, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../tools"))
from scene_kit import *
import props as PR
from sets09 import _stain, world_h, WALL_Y, GX, GZ, GY, HERE, TEX

_MAT = {}


def mat(name):
    if name in _MAT and _MAT[name].name in bpy.data.materials: return _MAT[name]
    f = {
        "wall": lambda: pbr("v2_wall", "sandstone_blocks_05", scale=0.40, tint=(1.0, 0.98, 0.94), bump=1.3),
        "wall_far": lambda: pbr("v2_wallf", "sandstone_blocks_05", scale=0.14, tint=(1.0, 0.97, 0.92), bump=0.8),
        "rough": lambda: pbr("v2_rough", "medieval_blocks_05", scale=0.55, tint=(0.95, 0.93, 0.9), bump=1.5),
        "cobble": lambda: pbr("v2_cobble", "cobblestone_floor_04", scale=0.45, bump=1.2),
        "ground": lambda: pbr("v2_ground", "aerial_grass_rock", scale=0.22, tint=(0.95, 1.05, 0.85), bump=0.8),
        "dirt": lambda: pbr("v2_dirt", "brown_mud_leaves_01", scale=0.35, bump=1.0),
        "planks": lambda: pbr("v2_planks", "wood_planks_dirt", scale=0.6, bump=1.0),
        "roof_red": lambda: pbr("v2_roofr", "clay_roof_tiles", scale=0.5, bump=1.2),
        "roof_slate": lambda: pbr("v2_roofs", "roof_slates_02", scale=0.5, bump=1.2),
        "thatch": lambda: pbr("v2_thatch", "thatch_roof_angled", scale=0.5, bump=1.2),
        "plaster": lambda: pbr("v2_plaster", "clay_plaster", scale=0.5, tint=(1.0, 0.95, 0.85), bump=0.8),
        "floor": lambda: pbr("v2_floor", "stone_tiles_02", scale=0.5, bump=1.0),
        "grime": lambda: pbr("v2_grime", "brown_mud_02", scale=0.8, tint=(0.6, 0.5, 0.35), bump=1.0),
        "moss": lambda: pbr("v2_moss", "mossy_rock", scale=0.6, bump=1.0),
    }[name]
    _MAT[name] = f(); return _MAT[name]


def house(x, y, z, w=4, d=3.5, h=3.2, yaw=0, roof="roof_red", windows=True):
    """medieval house: plaster walls, timber posts, gable roof, lit windows"""
    objs = [box((0, 0, h / 2), (w, d, h), mat("plaster"), 0.03)]
    for sx in (-1, 1):
        for sy in (-1, 1): objs.append(box((sx * w / 2, sy * d / 2, h / 2), (0.18, 0.18, h), mat("planks"), 0.01))
    objs.append(box((0, -d / 2 - 0.01, h * 0.55), (w, 0.08, 0.16), mat("planks")))
    o = PR._join(objs, "house"); o.location = (x, y, z); o.rotation_euler.z = math.radians(yaw)
    rl = math.hypot(w / 2, h * 0.45) + 0.4
    for sx in (-1, 1):
        r = box((0, 0, 0), (rl, d + 0.6, 0.12), mat(roof)); r.rotation_euler = (0, sx * math.atan2(h * 0.45, w / 2), math.radians(yaw)) if False else (0, -sx * math.atan2(h * 0.45, w / 2), 0)
        r.location = (sx * w / 4, 0, h + h * 0.22); r.parent = o
    if windows:
        for wx in (-w * 0.25, w * 0.25):
            p = PR.window_lit((0, 0, 0), 0, 0.6, 0.9); p.parent = o; p.location = (wx, -d / 2 - 0.02, h * 0.5)
    return o


def tower_roof(x, y, r, z, mat_name="roof_red", h=None):
    h = h or r * 2.2
    c = cyl((x, y, z + h / 2), r * 1.18, h, mat(mat_name), 40, "troof", r2=0.0)
    cyl((x, y, z + h + 0.6), 0.06, 1.4, PR.M("iron"), 6)
    return c


# ================================================================== WALL exterior (garderobe) — dense
def set_wall3(light="golden", grass=True, rubble=False, breach=False, stain=True, crowd_space=False):
    W, R = mat("wall"), mat("rough")
    w = box((0, WALL_Y + 1.5, 6), (44, 3, 16), W, 0.03, "wall")
    merlons(-20, 20, WALL_Y + 0.4, 14, W)
    bpy.ops.mesh.primitive_cube_add(location=(0, WALL_Y - 0.2, 0.9)); tb = bpy.context.object; tb.scale = (22, 1.0, 1.4)
    bpy.ops.object.transform_apply(scale=True)
    for v in tb.data.vertices:
        if v.co.z > 1.5 and v.co.y < WALL_Y: v.co.y += 1.4
    tb.data.materials.append(R)
    # towers at both ends of the wall + roofs
    for tx in (-11, 12):
        tower(tx, WALL_Y + 1.6, 3.0, 19, W); tower_roof(tx, WALL_Y + 1.6, 3.0, 20, "roof_red")
        PR.window_lit((tx, WALL_Y + 1.6 - 3.02, 12.5), 0, 0.5, 0.9)
    # garderobe
    box((GX, GY, GZ), (2.2, 1.8, 2.6), R, 0.05, "garderobe")
    for dx in (-0.85, 0.85):
        box((GX + dx, GY + 0.25, GZ - 1.5), (0.5, 1.3, 0.4), R, 0.03); box((GX + dx, GY + 0.55, GZ - 1.85), (0.5, 0.7, 0.32), R, 0.03)
    r = box((GX, GY - 0.1, GZ + 1.45), (2.5, 2.1, 0.18), mat("roof_slate")); r.rotation_euler.x = math.radians(-20)
    box((GX + 0.5, GY - 0.91, GZ + 0.3), (0.16, 0.05, 0.6), flat("dark", (0.02, 0.015, 0.01), 1.0))
    box((GX - 0.2, GY - 0.25, GZ - 1.31), (0.7, 0.6, 0.04), flat("hole", (0.01, 0.008, 0.005), 1.0), name="hole")
    point("hole", (GX - 0.2, GY - 0.25, GZ - 1.35)); point("garderobe", (GX, GY, GZ))
    if stain: plane((GX - 0.2, WALL_Y - 0.02, (GZ - 1.3) / 2 + 0.6), (0.9, (GZ - 1.3) - 0.8), _stain(), rot=(math.radians(90), 0, 0))
    # wall dressing: heraldic banners, shields, torches, arrow slits
    PR.banner((-4.0, WALL_Y - 0.1, 10.0), 0, 1.6, 4.4, "lions"); PR.banner((7.2, WALL_Y - 0.1, 10.0), 0, 1.6, 4.4, "lions")
    for sx in (-6.5, -1.4, 5.0, 9.4): PR.shield((sx, WALL_Y - 0.06, 6.2), 0, 0.9, "lions")
    for tx in (-2.6, 5.8): PR.torch((tx, WALL_Y - 0.15, 3.4), 0, True, 160 if light != "night" else 320)
    D = flat("slit", (0.02, 0.015, 0.012), 1.0)
    for sx in range(-16, 17, 4): box((sx + 0.5, WALL_Y - 0.01, 11.6), (0.16, 0.05, 0.9), D)
    # scaffold + ladder on the left, lean-to shed on the right
    for sx in (-8.6, -6.8):
        cyl((sx, 2.2, 3.5), 0.1, 7, PR.M("darkwood"), 6); cyl((sx, 3.0, 3.5), 0.1, 7, PR.M("darkwood"), 6)
    for zz in (2.4, 4.8): box((-7.7, 2.6, zz), (2.2, 1.0, 0.1), mat("planks"))
    place("wooden_ladder", (-5.9, 2.9, 0), 1.0, math.radians(-10))
    box((9.0, 2.2, 1.3), (3.0, 1.8, 0.1), mat("planks")).rotation_euler.x = math.radians(18)
    for sx in (7.6, 10.4): cyl((sx, 1.4, 1.1), 0.08, 2.2, PR.M("darkwood"), 6)
    # yard clutter in front of the wall (keeps the hero spots clear)
    clear = lambda x, y: (abs(x + 0.25) < 1.7 and -7.5 < y < -1.2) or (abs(x - 0.3) < 1.3 and y < -5) or (abs(x - GX) < 1.6 and y > 1.6) or (crowd_space and abs(x) < 6.5 and y > 0.4)
    PR.cart((-5.2, 0.6, 0), 15, "hay"); PR.weapon_rack((4.4, 2.0, 0), 0); PR.cauldron((7.4, 0.3, 0), fire=True)
    PR.barrels((-3.4, 2.1, 0), 2, 0); PR.crate_stack((3.0, 2.3, 0), 10); PR.hay_bale((-6.6, -1.4, 0), 30)
    PR.dress((-12, 12, -3.5, 2.6), 14, ["sack", "barrels", "crates", "bucket", "rope", "hay", "rocks"], clear=clear, seed=7)
    PR.fence((-3.4, -8.6, 0), (-1.0, -9.6, 0), 4, 1.0); PR.fence((1.6, -9.4, 0), (4.0, -8.2, 0), 4, 1.0)   # foreground framing
    lp = cyl((-2.9, -5.5, 1.1), 0.06, 2.2, PR.M("darkwood"), 6); PR.lantern((-2.9, -5.5, 2.15), 40)
    if breach: cut(w, box((-6, WALL_Y + 1.5, 4), (6, 5, 9), None))
    if rubble or breach:
        rg = random.Random(3)
        for i in range(40):
            x = rg.uniform(-10, -1.5) if breach else rg.uniform(-8, 8)
            sphere((x, rg.uniform(1.0, WALL_Y + 1), rg.uniform(0, 1.0)), rg.uniform(0.2, 0.6), R, (1, rg.uniform(.7, 1.3), rg.uniform(.5, .9)), sub=1, smooth=False)
    g = grid_ground(90, 70, mat("ground"), lambda x, y: 0.08 * math.sin(x * 0.7) * math.cos(y * 0.5))
    near = lambda c: -10 < c.y < WALL_Y - 0.6 and abs(c.x) < 15
    if grass: grass_field(g, "grass_medium_01", 50000, near, size=2.6)
    scatter("shrub_02", (-12, 12, 1.0, 2.4), 7, scale=(0.7, 1.2), seed=3, avoid=lambda x, y: clear(x, y) or abs(x - GX) < 1.6)
    # far hills + trees seen above/around the wall ends
    TR, LF = wood("trunk"), noisy("leaf", (0.10, 0.28, 0.06), (0.25, 0.46, 0.10), 0.5, bump=0.3)
    rg = random.Random(12)
    for i in range(10): tree(rg.choice([rg.uniform(-40, -15), rg.uniform(16, 40)]), rg.uniform(-10, 20), 0, rg.uniform(1.4, 2.2), (TR, LF))
    clouds(6, (-60, 60), (70, 90), (24, 40), 0.8)
    sky(light) if light != "night" else sky("night")
    fog(0.006 if light != "night" else 0.01, (0.95, 0.88, 0.78) if light in ("golden", "dusk", "dawn") else (0.75, 0.82, 1.0), 0.45, (120, 90, 40), (0, 0, 18))


# ================================================================== BATTLEMENTS v2
def set_battlements2(variant="normal", light="golden", knife=False, drips=False):
    from sets09 import wall_mats
    S, SD = (mat("wall"), mat("rough")) if variant == "normal" else wall_mats(variant)
    box((0, 0, -7.5), (30, 5, 15), S, 0.04, "walltop")
    merlons(-14, 14, -2.1, 0, S, step=2.2, size=(1.4, 0.8, 1.5)); box((0, -2.1, 0.35), (30, 0.8, 0.7), S, 0.03)
    box((0, 0.6, 0.02), (30, 3.0, 0.06), mat("planks"))                    # wooden wall-walk
    if variant == "butter":
        if knife:
            k = box((1.6, -2.1, 1.8), (0.08, 0.6, 1.2), flat("blade", (0.85, 0.87, 0.9), 0.2, metal=1.0)); k.rotation_euler.y = math.radians(20)
            box((1.75, -2.1, 2.55), (0.14, 0.18, 0.5), wood("handle"))
        if drips:
            BU = flat("drip", (1.0, 0.80, 0.18), 0.25); rg = random.Random(5)
            for i in range(40): sphere((rg.uniform(-12, 12), -2.55, rg.uniform(-3, 1.3)), rg.uniform(0.12, 0.3), BU, (1, 1, rg.uniform(1.5, 3)), sub=2)
    # dressing: banners on poles, torches, shields on merlons, cauldron of oil, barrels, arrows, weapon rack
    # dressing kept within ~2 m of the hero spot (-0.2, -0.6) so it is actually in the tight frames
    PR.flag_pole((-1.9, -1.55, 0), 4.2, (0.62, 0.06, 0.06), 1.4); PR.flag_pole((2.3, -1.55, 0), 4.2, (0.62, 0.06, 0.06), 1.4)
    for tx in (-1.15, 1.25): PR.torch((tx, -1.72, 1.55), 180, True, 140)
    for sx in (-3.3, 3.3): PR.shield((sx, -1.68, 0.95), 0, 0.75, "lions")
    PR.cauldron((-1.75, 0.5, 0.05), fire=True); PR.barrels((1.45, 0.4, 0.05), 2, 10); PR.weapon_rack((2.6, -0.9, 0.05), 180)
    PR.crate_stack((-2.6, 1.0, 0.05), 20); PR.sack((-1.0, 1.4, 0.05)); PR.rope_coil((0.9, 1.3, 0.05))
    place("wooden_bucket_01", (0.6, 0.9, 0.05), 1.0, 0.2, variant=0)
    # landscape far below: fields, river, village, trees, hills
    G = noisy("fields", (0.20, 0.40, 0.10), (0.48, 0.60, 0.18), 0.02, bump=0)
    grid_ground(900, 80, G, lambda x, y: -40 + 6 * math.sin(x * 0.01) * math.cos(y * 0.013))
    plane((90, -300, -44), (60, 900), water("riv2"), rot=(0, 0, math.radians(20)))
    TR, LF = wood("trunk"), noisy("leaf", (0.10, 0.28, 0.06), (0.25, 0.46, 0.10), 0.5, bump=0.3)
    rg = random.Random(2)
    for i in range(70): tree(rg.uniform(-250, 250), rg.uniform(-420, -60), -40, rg.uniform(2, 3.5), (TR, LF))
    for i in range(14): house(rg.uniform(20, 80), rg.uniform(-200, -120), -40, 6, 5, 4.5, rg.uniform(0, 360), rg.choice(["roof_red", "thatch"]))
    HL = noisy("hills", (0.18, 0.34, 0.12), (0.32, 0.46, 0.18), 0.02, bump=0)
    for i in range(8): sphere((rg.uniform(-600, 600), rg.uniform(-900, -600), -60), rg.uniform(150, 250), HL, (1.6, 1, 0.35), sub=3)
    clouds(8, (-400, 400), (-700, -500), (60, 160), 3.0)
    sky(light)


# ================================================================== CUTAWAY v2
def set_cutaway2(light="night", labels=False):
    from sets09 import set_cutaway
    set_cutaway(light, labels)
    # grime streaks + moss in the chute, cobwebs, bucket and torch upstairs, reeds in the moat, a rat
    plane((0, 1.72, 5.5), (1.25, 9.0), mat("grime"), rot=(math.radians(90), 0, 0))
    for zz in (2.0, 4.5, 7.0):
        sphere((0.55, 1.2, zz), 0.18, mat("moss"), (0.4, 1, 1.4), sub=2)
    place("wooden_bucket_01", (0.95, 1.1, 10.1), 1.0, 0.4, variant=0)
    R = mat("rough")
    for k, zz in enumerate((1.8, 2.9, 4.0, 5.1, 6.2, 7.3, 8.4)):          # protruding stones he climbs on
        box((-0.5 if k % 2 else 0.5, 1.0, zz), (0.32, 0.9, 0.18), R, 0.03)
    PR.torch((0.6, 1.05, 6.0), -90, True, 220)
    for zz in (1.4, 3.6, 5.6, 7.8, 9.2):
        sphere((-0.6, 1.4, zz), 0.16, mat("moss"), (0.35, 0.9, 1.5), sub=2)
    SL = flat("slime", (0.32, 0.36, 0.10), 0.15)
    for zz in (2.4, 4.8, 7.0, 8.8):
        cyl((0.2, 1.68, zz), 0.05, 0.9, SL, 8)
    from PIL import Image as _I, ImageDraw as _D
    wp = os.path.join(TEX, "web.png")
    if not os.path.exists(wp):
        im = _I.new("RGBA", (512, 512), (0, 0, 0, 0)); d = _D.Draw(im)
        for a_ in range(0, 90, 12): d.line([(0, 0), (512 * math.cos(math.radians(a_)), 512 * math.sin(math.radians(a_)))], fill=(230, 230, 235, 200), width=3)
        for r_ in range(60, 520, 60): d.arc([-r_, -r_, r_, r_], 0, 90, fill=(230, 230, 235, 170), width=3)
        im.save(wp)
    for (wx, wz, ry) in ((-0.62, 9.9, 0), (0.62, 9.9, 90)):
        plane((wx, 0.5, wz), (0.7, 0.7), image_mat("web", wp, emit=0.2), rot=(math.radians(90), math.radians(ry + 180), 0))
    PR.torch((-1.0, 1.65, 11.6), 0, True, 0)
    PR.shield((-6.3, 1.95, 9.0), 0, 0.9, "lions"); PR.banner((6.5, 1.95, 9.5), 0, 1.4, 3.6, "lions")
    scatter("shrub_02", (-16, -5, -3, 3), 8, scale=(0.5, 0.9), seed=4)
    for i, x in enumerate((-9.5, -7.0)): place("rock_moss_set_01", (x, -2.0, -0.7), 0.3, i)
    if light != "night":
        PR.barrels((-2.9, -1.6, 0), 2, 20); PR.sack((-1.4, -2.4, 0)); PR.sack((-1.0, -1.9, 0), 40, 0.8)
        place("wooden_bucket_01", (-3.6, -2.8, 0), 1.0, 0.2, variant=0); place("wooden_broom", (-0.6, -0.5, 0), 1.0, 0.3)
        place("wooden_ladder", (1.6, -0.4, 0), 1.0, math.radians(15)); PR.hay_bale((2.6, -2.2, 0), 15)
        PR.torch((-4.6, -0.2, 3.0), 0, True, 120)
        for i in range(6): sphere((-7.5 + i * 0.7, -1.4 + (i % 2) * 0.5, -0.4), 0.18, flat("reed", (0.25, 0.42, 0.12), 0.8), (0.3, 0.3, 2.2), sub=1)


# ================================================================== TOILET ROOM v2
def set_toilet2():
    from sets09 import set_toilet_room
    set_toilet_room()
    place("wooden_bucket_01", (-1.2, 2.2, 1.21), 1.0, 0.3, variant=0)
    PR.candle((1.9, 2.6, 1.21), 0.22, light=60); PR.candle((2.1, 2.5, 1.21), 0.15)
    box((-2.7, 0.6, 1.8), (0.08, 2.4, 3.4), mat("planks"))                    # wooden door
    cyl((-2.6, 1.4, 1.6), 0.05, 0.05, PR.M("iron"), 8)
    shelf = box((2.65, 0.8, 2.3), (0.3, 1.6, 0.06), mat("planks"))
    for i in range(3): cyl((2.65, 0.3 + i * 0.4, 2.45), 0.09, 0.26, flat("jar", (0.55, 0.32, 0.18), 0.4), 12)
    plane((2.75, -0.6, 2.4), (0.02, 1.0), PR.M("rope"), rot=(0, math.radians(90), 0))
    PR.rope_coil((-1.9, -0.4, 0)); PR.sack((1.8, -1.2, 0), 20, 0.8)
    import fix09; fix09.dress_privy()


# ================================================================== CHAPEL v2
def set_chapel2():
    from sets09 import set_chapel
    set_chapel()
    PR.carpet((0.6, 3.0, 0.01), 0, 1.6, 5.0)
    for x in (-3.5, 3.8): PR.pillar((x, 3, 0), 0.45, 8.0)
    PR.tapestry((-5.68, 3.5, 3.0), 90, 1.8, 3.0); PR.tapestry((5.68, 4.5, 3.0), -90, 1.8, 3.0, (60, 20, 30))
    PR.chandelier((0.8, 3.5, 5.2)); PR.banner((-2.2, 6.6, 4.2), 0, 1.0, 2.6, "lions"); PR.banner((3.6, 6.6, 4.2), 0, 1.0, 2.6, "lions")
    for i in range(6): PR.candle((-0.6 + i * 0.3, 5.9, 0.0), 0.5 + 0.15 * (i % 2), light=30 if i % 2 else 0)
    PR.sack((-4.2, 1.0, 0)); PR.barrels((4.6, 0.8, 0), 1, 0)
    import fix09; fix09.dress_chapel()


# ================================================================== GATE v2 (courtyard)
def set_gate2(light="dawn", open_=True):
    from sets09 import set_gate
    set_gate(light, open_)
    plane((0, -5, 0.08), (40, 30), mat("cobble"))                       # above the bumpy dirt grid (was poking through)
    for o in bpy.data.objects:                                           # real planks on the gate leaves
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith("door"):
            o.data.materials[0] = mat("planks")
        elif o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith("stone"):
            o.data.materials[0] = mat("wall")                            # real sandstone blocks instead of flat procedural bricks
    for tx in (-3.4, 3.4): PR.torch((tx, 5.85, 4.2), 0, True, 200)
    PR.banner((-6.0, 5.85, 8.5), 0, 1.6, 4.0, "lions"); PR.banner((6.0, 5.85, 8.5), 0, 1.6, 4.0, "lions")
    PR.cart((-6.6, 0.6, 0), 80, "sacks"); PR.weapon_rack((6.8, 3.6, 0), 180); PR.cauldron((-9.0, -3.0, 0), fire=True)
    PR.dress((-11, 11, -6, 4.5), 12, ["sack", "barrels", "crates", "bucket", "hay", "rope"], clear=lambda x, y: abs(x) < 3.4 or (y < -5 and abs(x) < 6), seed=11)
    for i, x in enumerate((-12.0, 12.0)):
        for z in (3.0, 6.5):
            PR.window_lit((x * 0.98 + (0.95 if x < 0 else -0.95), -6 + i * 3, z), 90 if x < 0 else -90, 0.7, 1.1)
    PR.lantern((2.6, 4.9, 2.4), 60)


# ================================================================== WORLD v2 (castle with roofs, inner houses, village, richer camp)
WORLD2_CACHE = os.path.join(HERE, "work", "world2_base.blend")


def _world2_base():
    from sets09 import _world_base
    _world_base()
    # PBR walls for the castle (big scale), conical roofs, inner houses, village by the river
    WF = mat("wall_far")
    for o in bpy.data.objects:
        if o.get("castle") and o.type == "MESH" and o.data.materials and o.data.materials[0].name.startswith("stone"):
            o.data.materials[0] = WF
    for (x, y, r, h) in ((0, 4, 6.5, 26),):
        tower_roof(x, y, r, h + 1.0, "roof_red", r * 1.6)
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.3
        if k % 2 == 0: tower_roof(math.cos(a) * 26, math.sin(a) * 26, 4.8, 11 * 1.3 + 1.0, "roof_slate", 8)
    rg = random.Random(31)
    for i in range(14):
        a = rg.uniform(0, 2 * math.pi); rr = rg.uniform(16, 23)
        house(math.cos(a) * rr, math.sin(a) * rr, 0, 4, 3.5, 3.4, math.degrees(a) + 90, rg.choice(["roof_red", "roof_slate"]))
    for i in range(18):                                                   # village on the far bank
        x, y = rg.uniform(216, 250), rg.uniform(-110, 70)
        house(x, y, world_h(x, y), 5, 4, 3.6, rg.uniform(0, 360), rg.choice(["thatch", "roof_red"]))
    for i in range(10):                                                   # houses at the cliff foot (near bank)
        x, y = rg.uniform(74, 86), rg.uniform(-80, 40)
        house(x, y, world_h(x, y), 4.5, 3.6, 3.4, rg.uniform(70, 110), "thatch")
    for i, (bx, by) in enumerate(((140, -40), (165, 10), (128, 30), (175, -75))):   # boats on the Seine
        hull = box((bx, by, -48.7), (5.0, 1.8, 0.8), PR.M("wood"), 0.15); hull.rotation_euler.z = math.radians(15 + i * 40)
        cyl((bx, by, -46.0), 0.08, 5.0, PR.M("darkwood"), 6)
        sl = plane((bx + 0.6, by, -45.6), (1.6, 2.8), flat("sail", (0.92, 0.88, 0.78), 0.9), rot=(math.radians(90), 0, math.radians(15 + i * 40)))
    for (r0, r1) in ((0, 13), (15, 25)):                                  # paved / dirt courtyards inside the rings
        cyl((0, 0, 0.06 + r0 * 0.001), r1, 0.1, mat("cobble") if r0 == 0 else mat("dirt"), 96)
    for i in range(10):
        a = rg.uniform(0, 2 * math.pi); rr = rg.uniform(16, 23)
        house(math.cos(a) * rr, math.sin(a) * rr, 0, 3.6, 3.2, 3.0, math.degrees(a) + 90, rg.choice(["roof_red", "thatch"]))
    for i in range(6):
        PR.flag_pole((math.cos(i) * 26, math.sin(i) * 26, 14.5), 4, (0.62, 0.06, 0.06), 2.0)


def set_world2(variant="normal", light="golden", camp=False, flags="english", scaffold=False, trebuchet=False, breach=False, smoke=False):
    import sets09 as S0
    if os.path.exists(WORLD2_CACHE):
        bpy.ops.wm.open_mainfile(filepath=WORLD2_CACHE)
    else:
        _world2_base(); bpy.ops.wm.save_as_mainfile(filepath=WORLD2_CACHE)
    # reuse the variant logic of v1 on top of the cached v2 base (it handles iron/butter/breach/flags/scaffold/camp/smoke + sky)
    _orig = S0.WORLD_CACHE
    S0.WORLD_CACHE = WORLD2_CACHE
    try:
        S0.set_world.__wrapped__ if hasattr(S0.set_world, "__wrapped__") else None
        _apply_variants(S0, variant, light, camp, flags, scaffold, trebuchet, breach, smoke)
    finally:
        S0.WORLD_CACHE = _orig
    if camp: _camp_dressing()
    fog(0.0006, (0.95, 0.88, 0.78) if light in ("golden", "dusk", "dawn") else (0.85, 0.9, 1.0), 0.4, (700, 700, 200), (0, 0, 40))


def _apply_variants(S0, variant, light, camp, flags, scaffold, trebuchet, breach, smoke):
    import inspect
    src = inspect.getsource(S0.set_world)
    body = src.split('        bpy.ops.wm.save_as_mainfile(filepath=WORLD_CACHE)\n', 1)[1]          # everything after the cache load
    code = "def _v(variant, light, camp, flags, scaffold, trebuchet, breach, smoke):\n" + body
    ns = dict(S0.__dict__); exec(code, ns); ns["_v"](variant, light, camp, flags, scaffold, trebuchet, breach, smoke)


def _camp_dressing():
    rg = random.Random(44); cx, cy = -112, -88
    for i in range(5):
        x, y = cx + rg.uniform(-20, 20), cy + rg.uniform(-14, 14); z = world_h(x, y)
        PR.weapon_rack((x, y, z), rg.uniform(0, 360))
    for i in range(4):
        x, y = cx + rg.uniform(-18, 18), cy + rg.uniform(-12, 12); z = world_h(x, y)
        PR.cart((x, y, z), rg.uniform(0, 360), rg.choice(["hay", "sacks"]))
    for i in range(6):
        x, y = cx + 26 + rg.uniform(-4, 8), cy + 18 + rg.uniform(-6, 6); z = world_h(x, y)
        PR.banner((x, y, z + 3.2), rg.uniform(-60, -20), 1.4, 3.0, "lilies", (20, 40, 130), (240, 190, 50), 0.1)
        cyl((x, y, z + 2.4), 0.06, 4.8, PR.M("darkwood"), 6)
    PR.dress((cx + 10, cx + 30, cy + 8, cy + 28), 14, ["sack", "barrels", "crates", "hay", "bucket"], z=world_h, seed=45)
