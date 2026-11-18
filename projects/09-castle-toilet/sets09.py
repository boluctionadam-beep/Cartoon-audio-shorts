"""Sets (3D worlds) for short 09. Each builder creates geometry + lights; shots09.py adds camera + characters.
Coordinates: metres, z up. Characters are ~2.1 m cards."""
import bpy, math, random, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../tools"))
from scene_kit import *

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "renders", "tex"); os.makedirs(TEX, exist_ok=True)

LIME = (0.70, 0.66, 0.58)          # Gaillard limestone
IRON = None; BUTTER = None


def wall_mats(variant):
    if variant == "iron":
        m = stone("iron", base=(0.30, 0.32, 0.36), scale=0.35, row=0.9, width=1.4, var=0.85, mortar=(0.12, 0.12, 0.14), bump=0.8, dirt=False)
        m.node_tree.nodes["Principled BSDF"].inputs["Metallic"].default_value = 0.8
        m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
        return m, m
    if variant == "butter":
        m = stone("butter", base=(1.0, 0.80, 0.18), scale=0.5, row=0.6, width=1.2, var=0.93, mortar=(0.92, 0.70, 0.12), bump=0.25, dirt=False)
        b = m.node_tree.nodes["Principled BSDF"]; b.inputs["Roughness"].default_value = 0.25
        b.inputs["Subsurface Weight"].default_value = 0.3
        return m, m
    return stone("stone", base=LIME, scale=0.6), stone("stone_d", base=(0.60, 0.56, 0.49), scale=0.9)


# ================================================================== WALL (exterior, close)
WALL_Y, GX, GZ = 4.0, 2.2, 8.6
GY = WALL_Y - 0.9


def set_wall(light="golden", breach=False, stain=True, grass=True, rubble=False):
    S, SD = wall_mats("normal")
    box((0, WALL_Y + 1.5, 6), (44, 3, 16), S, 0.05, "wall")
    merlons(-20, 20, WALL_Y + 0.4, 14, S)
    bpy.ops.mesh.primitive_cube_add(location=(0, WALL_Y - 0.2, 0.9)); tb = bpy.context.object; tb.scale = (22, 1.0, 1.4)
    bpy.ops.object.transform_apply(scale=True)
    for v in tb.data.vertices:
        if v.co.z > 1.5 and v.co.y < WALL_Y: v.co.y += 1.4
    tb.data.materials.append(SD)
    # garderobe
    box((GX, GY, GZ), (2.2, 1.8, 2.6), SD, 0.06, "garderobe")
    for dx in (-0.85, 0.85):
        box((GX + dx, GY + 0.25, GZ - 1.5), (0.5, 1.3, 0.4), SD, 0.03); box((GX + dx, GY + 0.55, GZ - 1.85), (0.5, 0.7, 0.32), SD, 0.03)
    r = box((GX, GY - 0.1, GZ + 1.45), (2.5, 2.1, 0.18), flat("slate", (0.16, 0.18, 0.24), 0.6)); r.rotation_euler.x = math.radians(-20)
    box((GX + 0.5, GY - 0.91, GZ + 0.3), (0.16, 0.05, 0.6), flat("dark", (0.02, 0.015, 0.01), 1.0))
    box((GX - 0.2, GY - 0.25, GZ - 1.31), (0.7, 0.6, 0.04), flat("hole", (0.01, 0.008, 0.005), 1.0), name="hole")
    point("hole", (GX - 0.2, GY - 0.25, GZ - 1.35)); point("garderobe", (GX, GY, GZ))
    if stain:
        m = _stain()
        plane((GX - 0.2, WALL_Y - 0.02, (GZ - 1.3) / 2 + 0.6), (0.9, (GZ - 1.3) - 0.8), m, rot=(math.radians(90), 0, 0))
    # banner
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=40, size=1, location=(-3.4, WALL_Y - 0.12, 10.6)); bn = bpy.context.object
    bn.scale = (1.5, 4.6, 1); bn.rotation_euler.x = math.radians(90); bn.data.materials.append(flat("banner", (0.62, 0.05, 0.05), 0.7))
    wv = bn.modifiers.new("w", "WAVE"); wv.height = 0.08; wv.width = 0.9; wv.use_normal = True
    if breach:
        cutter = box((-6, WALL_Y + 1.5, 4), (6, 5, 9), None); cut(bpy.data.objects["wall"], cutter)
    if rubble or breach:
        rg = random.Random(3); RM = SD
        for i in range(70):
            x = rg.uniform(-10, -1.5) if breach else rg.uniform(-8, 8)
            sphere((x, rg.uniform(1.0, WALL_Y + 1), rg.uniform(0, 1.2)), rg.uniform(0.2, 0.7), RM, (1, rg.uniform(.7, 1.3), rg.uniform(.5, .9)), sub=1, smooth=False)
    # ground
    G = noisy("grass", (0.10, 0.30, 0.05), (0.36, 0.55, 0.12), 0.6)
    g = grid_ground(90, 60, G, lambda x, y: 0.08 * math.sin(x * 0.7) * math.cos(y * 0.5))
    RK = flat("rock", (0.55, 0.52, 0.47), 0.9); rg = random.Random(4)
    for i in range(18):
        x = rg.choice([rg.uniform(-9, -1.8), rg.uniform(1.4, 9)]); y = rg.uniform(-5, WALL_Y - 0.5)
        sphere((x, y, 0), rg.uniform(0.12, 0.45), RK, (1, rg.uniform(.7, 1.2), rg.uniform(.4, .7)), sub=2, smooth=False)
    if grass:
        grass_particles(g, blade_mat(), 70000, lambda v: -7.5 < v.y < WALL_Y - 0.6 and abs(v.x) < 14)
    clouds(5, (-60, 60), (70, 90), (24, 40), 0.8)
    if light == "night":
        sky("night"); point_light((-3, -2, 3), 120, (1.0, 0.55, 0.25), 0.3)       # torch glow off-screen
    else:
        sky(light)


def _stain():
    m = bpy.data.materials.new("stain"); m.use_nodes = True; N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.20, 0.13, 0.05, 1); b.inputs["Roughness"].default_value = 0.4
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sep.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4; L.new(tc.outputs["UV"], nz.inputs["Vector"])
    gx = N.new("ShaderNodeMath"); gx.operation = "SUBTRACT"; gx.inputs[1].default_value = 0.5; L.new(sep.outputs["X"], gx.inputs[0])
    ax = N.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"; L.new(gx.outputs[0], ax.inputs[0])
    wv = N.new("ShaderNodeMath"); wv.operation = "MULTIPLY_ADD"; wv.inputs[1].default_value = 0.25; L.new(nz.outputs["Fac"], wv.inputs[0]); L.new(ax.outputs[0], wv.inputs[2])
    ex = N.new("ShaderNodeMapRange"); ex.inputs["From Min"].default_value = 0.30; ex.inputs["From Max"].default_value = 0.42
    ex.inputs["To Min"].default_value = 1; ex.inputs["To Max"].default_value = 0; L.new(wv.outputs[0], ex.inputs["Value"])
    ey = N.new("ShaderNodeMapRange"); ey.inputs["To Max"].default_value = 0.85; L.new(sep.outputs["Y"], ey.inputs["Value"])
    a = N.new("ShaderNodeMath"); a.operation = "MULTIPLY"; L.new(ex.outputs["Result"], a.inputs[0]); L.new(ey.outputs["Result"], a.inputs[1])
    L.new(a.outputs[0], b.inputs["Alpha"])
    return m


# ================================================================== WORLD (castle on the cliff, river, camp)
def world_h(x, y):
    r = math.hypot(x, y)
    z = 0.0
    if r > 52: z = -9 * min(1, (r - 52) / 60)
    if 29.5 < r < 33.5: z = min(z, -2.2)                                   # moat channel
    if x > 50:
        t = min(1, (x - 50) / 22); z = min(z, -52 * (t * t * (3 - 2 * t)))  # cliff to the river
    z += 0.6 * math.sin(x * 0.05) * math.cos(y * 0.04) + 0.25 * math.sin(x * 0.21 + y * 0.17)
    return z


WORLD_CACHE = os.path.join(HERE, "work", "world_base.blend")


def _tag(before, key):
    for o in bpy.data.objects:
        if o.name not in before: o[key] = 1


def _world_base():
    S, SD = wall_mats("normal")
    grid_ground(520, 220, terrain("terrain_w"), world_h)
    plane((150, 0, -49), (120, 600), water("river"))                      # the Seine
    mo = cyl((0, 0, -1.5), 33.6, 0.2, water("moat", (0.10, 0.28, 0.30)), 128, "moat")
    cut(mo, cyl((0, 0, -1.5), 29.4, 2.0, None, 128, "moatcut"))
    before = set(o.name for o in bpy.data.objects)
    tower(0, 4, 6.5, 26, S, 0)
    ring_wall(0, 0, 14, 13, 3, S, towers=5, tmat=SD)
    ring_wall(0, 0, 26, 11, 3, S, towers=8, tmat=SD)
    _tag(before, "castle"); before = set(o.name for o in bpy.data.objects)
    ring_wall(-6, 0, 40, 9, 3, S, towers=7, tmat=SD, gap=(5.6, 6.8))
    _tag(before, "castle"); _tag(before, "outer")
    cyl((0, 4, 31), 0.25, 9, wood("pole"), 8)
    TR, LF = wood("trunk"), noisy("leaf", (0.10, 0.28, 0.06), (0.25, 0.46, 0.10), 0.5, bump=0.3)
    rg = random.Random(9); before = set(o.name for o in bpy.data.objects)
    for i in range(110):
        a = rg.uniform(0, 2 * math.pi); r = rg.uniform(62, 220); x, y = math.cos(a) * r, math.sin(a) * r
        if 45 < x < 120: continue
        tree(x, y, world_h(x, y), rg.uniform(1.2, 2.0), (TR, LF))
    for i in range(30):
        x = rg.uniform(200, 320); y = rg.uniform(-250, 250); tree(x, y, -48, rg.uniform(1.4, 2.2), (TR, LF))
    _tag(before, "tree")
    HL = noisy("hills", (0.18, 0.34, 0.12), (0.32, 0.46, 0.18), 0.02, bump=0)
    for i in range(10):
        sphere((rg.uniform(-500, 500), rg.uniform(400, 600), -60), rg.uniform(120, 220), HL, (1.6, 1, 0.35), sub=3)
    clouds(9, (-300, 300), (300, 420), (90, 160), 3.0)


def set_world(variant="normal", light="golden", camp=False, flags="english", scaffold=False, trebuchet=False, breach=False, smoke=False):
    if os.path.exists(WORLD_CACHE):
        bpy.ops.wm.open_mainfile(filepath=WORLD_CACHE)
    else:
        _world_base(); os.makedirs(os.path.dirname(WORLD_CACHE), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=WORLD_CACHE)
    S, SD = wall_mats(variant if variant in ("iron", "butter") else "normal")
    if variant in ("iron", "butter"):
        for o in bpy.data.objects:
            if o.get("castle") and o.type == "MESH" and o.data.materials and o.data.materials[0].name.startswith("stone"):
                o.data.materials[0] = S
    if breach:                                                             # knock a hole in the outer ring (facing the camp)
        for o in list(bpy.data.objects):
            if o.get("outer"):
                a = math.atan2(o.location.y, o.location.x + 6) % (2 * math.pi)
                if 2.5 < a < 3.25 and o.location.z > -1: bpy.data.objects.remove(o)
        rg = random.Random(3)
        for i in range(60):
            a = rg.uniform(2.5, 3.25); r = 40 + rg.uniform(-3, 4); x, y = -6 + math.cos(a) * r, math.sin(a) * r
            sphere((x, y, world_h(x, y) + rg.uniform(0, 1.5)), rg.uniform(0.5, 1.5), SD, (1, rg.uniform(.7, 1.3), rg.uniform(.5, .9)), sub=1, smooth=False)
    point("castle", (-38, 6, 6) if breach else (-30, 10, 8)); point("keep_top", (0, 4, 27))
    if flags:
        fcol = (0.62, 0.06, 0.06) if flags == "english" else (0.12, 0.22, 0.62)
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=12, size=1, location=(3.2, 4, 33.5)); fl = bpy.context.object
        fl.scale = (6, 3.6, 1); fl.rotation_euler.x = math.radians(90); fl.data.materials.append(flat("flag", fcol, 0.7))
        wv = fl.modifiers.new("w", "WAVE"); wv.height = 0.5; wv.width = 2.5; wv.use_normal = True; wv.time_offset = 3
        if flags == "french":
            for dx, dz in ((-1.5, 0.8), (1.5, 0.8), (0, -0.8)):
                sphere((3.2 + dx, 3.85, 33.5 + dz), 0.45, flat("lilyg", (0.95, 0.75, 0.15), 0.5, emit=0.2), (1, 0.3, 1.2), sub=2)
    if scaffold:
        W = wood("scaf")
        for i in range(10):
            a = 3.6 + i * 0.1; x, y = math.cos(a) * 28, math.sin(a) * 28
            cyl((x, y, 7), 0.15, 14, W, 6); cyl((x + 1.2, y + 0.4, 7), 0.15, 14, W, 6)
            for z in (4, 8, 12):
                box((x + 0.6, y + 0.2, z), (2.2, 0.8, 0.15), W)
        for i in range(24):
            rg = random.Random(i); x, y = rg.uniform(-50, -36), rg.uniform(-40, -20); box((x, y, world_h(x, y) + 0.35), (1.2, 0.8, 0.7), SD, 0.05)
    if camp:
        _camp(trebuchet)
    if smoke:
        SM = flat("smoke", (0.55, 0.52, 0.50), 1.0, emit=0.15); rg = random.Random(11)
        for i in range(14):
            sphere((rg.uniform(-48, -40), rg.uniform(-2, 12), 4 + i * 1.3), rg.uniform(2, 4), SM, (1, 1, 0.8), sub=2)
    sky(light)


def _camp(trebuchet):
    rg = random.Random(21); cx, cy = -112, -88
    T1, T2 = flat("tent", (0.92, 0.90, 0.84), 0.9), flat("tentb", (0.14, 0.24, 0.62), 0.8)
    for i in range(16):
        x, y = cx + rg.uniform(-24, 24), cy + rg.uniform(-16, 16); z = world_h(x, y)
        cyl((x, y, z + 2.2), 3.0, 4.4, T1 if i % 3 else T2, 20, "tent", r2=0.0)
        cyl((x, y, z + 0.6), 3.05, 1.2, T2 if i % 3 else T1, 20, "tentb")
        cyl((x, y, z + 5), 0.08, 2, wood("tp"), 6)
    for i in range(6):                                                     # banners with lilies
        x, y = cx + rg.uniform(-25, 25), cy + rg.uniform(-20, 20); z = world_h(x, y)
        cyl((x, y, z + 4), 0.12, 8, wood("bp"), 6)
        box((x + 1.2, y, z + 6.6), (2.4, 0.05, 1.5), T2)
    fire = flat("fire", (1.0, 0.45, 0.1), 0.9, emit=8)
    for i in range(3):
        x, y = cx + rg.uniform(-15, 15), cy + rg.uniform(-10, 10); sphere((x, y, world_h(x, y) + 0.5), 0.8, fire, (1, 1, 1.4), sub=2)
        point_light((x, y, world_h(x, y) + 2), 800, (1, 0.5, 0.2), 0.5)
    if trebuchet:
        x, y = -62, -38; z = world_h(x, y); W = wood("treb")
        box((x, y, z + 0.5), (6, 4, 1), W); box((x - 1.5, y, z + 4), (0.6, 0.6, 7), W); box((x + 1.5, y, z + 4), (0.6, 0.6, 7), W)
        arm = box((x, y, z + 7.5), (0.5, 0.5, 13), W); arm.rotation_euler.y = math.radians(-55)
        box((x - 4, y, z + 4.5), (2.2, 2.2, 2.2), flat("cw", (0.3, 0.3, 0.32), 0.8))
        point("treb_tip", (x + 5.4, y, z + 11.3))


# ================================================================== BATTLEMENTS (wall-walk on top)
def set_battlements(variant="normal", light="golden", knife=False, drips=False):
    S, SD = wall_mats(variant)
    box((0, 0, -7.5), (30, 5, 15), S, 0.04, "walltop")                    # top at z=0
    merlons(-14, 14, -2.1, 0, S, step=2.2, size=(1.4, 0.8, 1.5))
    box((0, -2.1, 0.35), (30, 0.8, 0.7), S, 0.03)                          # parapet base
    if variant == "butter":
        if knife:
            k = box((1.6, -2.1, 1.8), (0.08, 0.6, 1.2), flat("blade", (0.85, 0.87, 0.9), 0.2, metal=1.0)); k.rotation_euler.y = math.radians(20)
            box((1.75, -2.1, 2.55), (0.14, 0.18, 0.5), wood("handle"))
        if drips:
            BU = flat("drip", (0.98, 0.84, 0.36), 0.25)
            rg = random.Random(5)
            for i in range(30):
                sphere((rg.uniform(-12, 12), -2.55, rg.uniform(-3, 1.3)), rg.uniform(0.12, 0.3), BU, (1, 1, rg.uniform(1.5, 3)), sub=2)
    # landscape far below (outside)
    G = noisy("grass_b", (0.16, 0.36, 0.08), (0.42, 0.58, 0.16), 0.05, bump=0)
    grid_ground(900, 80, G, lambda x, y: -40 + 6 * math.sin(x * 0.01) * math.cos(y * 0.013))
    plane((90, -300, -44), (60, 900), water("riv2"), rot=(0, 0, math.radians(20)))
    TR, LF = wood("trunk"), noisy("leaf", (0.10, 0.28, 0.06), (0.25, 0.46, 0.10), 0.5, bump=0.3)
    rg = random.Random(2)
    for i in range(90):
        x, y = rg.uniform(-250, 250), rg.uniform(-420, -40); tree(x, y, -40, rg.uniform(2, 3.5), (TR, LF))
    HL = noisy("hills", (0.18, 0.34, 0.12), (0.32, 0.46, 0.18), 0.02, bump=0)
    for i in range(8):
        sphere((rg.uniform(-600, 600), rg.uniform(-900, -600), -60), rg.uniform(150, 250), HL, (1.6, 1, 0.35), sub=3)
    clouds(8, (-400, 400), (-700, -500), (60, 160), 3.0)
    sky(light)


# ================================================================== CUTAWAY (cross-section of the wall + chute)
def set_cutaway(light="night", labels=False):
    S, SD = wall_mats("normal")
    CUTF = stone("cutface", base=(0.74, 0.70, 0.62), scale=0.75, row=0.5, width=1.0, var=0.8, mortar=(0.35, 0.32, 0.28), bump=0.6)
    w = box((0, 2.0, 7), (10, 4, 14), CUTF, 0.0, "wall")                   # front face y=0 is the cut
    shaft = box((0, 0.6, 5.5), (1.3, 2.2, 9.2), None)                      # chute: z 0.9..10.1
    cut(w, shaft)
    room = box((0, 0.6, 11.4), (2.6, 2.2, 2.6), None); cut(w, room)        # toilet room on top
    out = box((-0.9, 0.6, 0.9), (2.4, 2.2, 1.4), None); out.rotation_euler.y = math.radians(30); cut(w, out)
    GR = noisy("grime", (0.10, 0.07, 0.04), (0.22, 0.15, 0.08), 2.0, bump=0.4)
    box((0, 1.75, 5.5), (1.3, 0.02, 9.2), GR)                              # dark back of the chute
    box((0, 1.75, 11.4), (2.6, 0.02, 2.6), S)                              # room back wall (stone)
    seat = box((0.35, 0.9, 10.35), (1.9, 1.5, 0.5), wood("seat"))          # wooden bench over the chute
    hole = box((-0.05, 0.9, 10.35), (0.75, 1.0, 0.6), None); cut(seat, hole)
    box((0, 1.0, 12.85), (2.8, 1.8, 0.1), SD)
    point("seat", (-0.05, 0.9, 10.6)); point("chute_bottom", (0, 0.9, 1.0)); point("chute_top", (0, 0.9, 10.0))
    # outside: moat on the left, ground
    plane((-12, 0, -0.6), (16, 30), water("moat2", (0.10, 0.28, 0.30)))
    G = noisy("grass_c", (0.14, 0.34, 0.08), (0.40, 0.56, 0.14), 0.3)
    box((-14, 4, -1.5), (14, 30, 1.6), G); box((14, 6, -0.5), (18, 26, 1.0), noisy("earth", (0.22, 0.18, 0.10), (0.32, 0.26, 0.15), 0.6))
    box((-20, 2.0, 7), (0.1, 0.1, 0.1), None)
    point("moat", (-5.5, 0, -0.5))
    # torch in the room (warm) + night
    if light == "night":
        sky("night"); point_light((0.9, 0.6, 11.6), 420, (1.0, 0.55, 0.25), 0.2); point_light((0, 0.9, 9.4), 160, (1.0, 0.6, 0.3), 0.3)
        point_light((0, -3, 4), 220, (0.45, 0.55, 1.0), 2.0); point_light((-2, 0.9, 1.5), 60, (0.4, 0.6, 1.0), 0.5)
        f = flat("flame", (1.0, 0.6, 0.2), 0.9, emit=20); sphere((1.1, 1.6, 11.8), 0.12, f, (1, 1, 1.6), sub=2)
    else:
        sky("day"); area_light((0, -8, 8), (0, 1, 6), 450, 8, (1, 0.98, 0.95))
    S2 = stone("stone2", base=LIME, scale=0.6)
    box((-6.5, 3.5, 7), (3, 3, 14), S2, 0.04); box((6.5, 3.5, 7), (3, 3, 14), S2, 0.04)   # wall continues behind the slice
    merlons(-8, 8, 2.5, 14, S2, 2.0)


# ================================================================== TOILET ROOM (inside the garderobe)
def set_toilet_room():
    S = stone("stone_r", base=(0.62, 0.58, 0.52), scale=0.9)
    box((0, 0, -0.1), (6, 6, 0.2), noisy("floor", (0.35, 0.32, 0.28), (0.5, 0.46, 0.4), 1.5, bump=0.3))
    back = box((0, 3, 2), (6, 0.4, 4.2), S); box((-3, 0, 2), (0.4, 6, 4.2), S); box((3, 0, 2), (0.4, 6, 4.2), S)
    cut(back, box((0.8, 3, 2.6), (0.25, 0.6, 1.2), None))
    seat = box((0, 1.9, 0.55), (2.8, 1.8, 1.1), S)                          # stone bench
    top = box((0, 1.9, 1.15), (2.9, 1.9, 0.12), wood("seatw", (0.40, 0.24, 0.12), (0.62, 0.40, 0.20)), 0.03)
    h1 = cyl((0, 1.7, 1.1), 0.36, 0.6, None, 40); cut(top, h1); h2 = cyl((0, 1.7, 0.6), 0.34, 1.2, None, 40); cut(seat, h2)
    cyl((0, 1.7, 0.55), 0.33, 1.0, flat("abyss", (0.005, 0.004, 0.003), 1.0), 32)
    point("seat_hole", (0, 1.7, 1.21)); point("seat_back", (0, 1.7 + 0.36, 1.21))
    hay = noisy("hay", (0.55, 0.42, 0.15), (0.80, 0.66, 0.28), 3.0, bump=0.5)
    sphere((1.3, 2.3, 1.35), 0.35, hay, (1.2, 1, 0.5), sub=2)              # bundle of hay/moss (medieval paper)
    interior_world((0.03, 0.025, 0.02), 1.0)
    area_light((0.8, 4.5, 3.0), (0, 1.5, 1.0), 900, 0.6, (1.0, 0.86, 0.66))  # daylight through the slit
    point_light((-1.8, 0.5, 2.6), 60, (1.0, 0.6, 0.3), 0.4)
    beam = flat("beam", (1.0, 0.9, 0.7), 1.0, emit=1.2, alpha=0.12)
    p = plane((0.6, 2.2, 2.0), (0.6, 2.6), beam, rot=(math.radians(60), 0, 0))


# ================================================================== CHAPEL
def stained_glass(path):
    from PIL import Image, ImageDraw
    r = random.Random(7); W, H = 512, 1024; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([0, 0, W, W], fill=(20, 20, 24, 255)); d.rectangle([0, W // 2, W, H], fill=(20, 20, 24, 255))
    cols = [(220, 40, 50), (40, 90, 210), (240, 200, 60), (60, 170, 90), (150, 60, 190)]
    for y in range(20, H, 70):
        for x in range(10, W, 80):
            pts = [(x + r.randint(0, 20), y + r.randint(0, 20)), (x + 70 + r.randint(-10, 10), y + r.randint(0, 20)), (x + 70, y + 64), (x, y + 64)]
            d.polygon(pts, fill=(*r.choice(cols), 255))
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).ellipse([8, 8, W - 8, W - 8], fill=255); ImageDraw.Draw(mask).rectangle([8, W // 2, W - 8, H - 8], fill=255)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.paste(im, (0, 0), mask)
    d2 = ImageDraw.Draw(out)
    for x in range(0, W, 80): d2.line([(x, 0), (x, H)], fill=(15, 15, 15, 255), width=8)
    for y in range(0, H, 70): d2.line([(0, y), (W, y)], fill=(15, 15, 15, 255), width=8)
    d2.ellipse([0, 0, W - 1, W - 1], outline=(15, 15, 15, 255), width=14)
    out.save(path); return path


def set_chapel():
    S = stone("stone_ch", base=(0.66, 0.62, 0.55), scale=0.7)
    FL = noisy("floor_ch", (0.36, 0.33, 0.30), (0.52, 0.48, 0.43), 1.0, bump=0.3)
    fl = box((0, 4, -0.1), (12, 12, 0.2), FL)
    hole = box((-1.6, 0.6, -0.1), (1.1, 1.1, 0.6), None); cut(fl, hole)
    box((-1.6, 0.6, -0.8), (1.1, 1.1, 0.05), flat("abyss2", (0.004, 0.003, 0.002), 1.0))
    point("floor_hole", (-1.6, 0.6, 0.0)); point("floor_hole_back", (-1.6, 1.15, 0.0))
    box((0, 7, 4), (12, 0.6, 8.2), S); box((-6, 4, 4), (0.6, 12, 8.2), S); box((6, 4, 4), (0.6, 12, 8.2), S)
    sg = image_mat("glass", stained_glass(os.path.join(TEX, "glass.png")), emit=3.0)
    plane((0, 6.68, 4.6), (1.8, 3.6), sg, rot=(math.radians(90), 0, 0))
    altar = box((1.8, 5.6, 0.6), (2.6, 1.2, 1.2), S, 0.04)
    box((1.8, 5.6, 1.25), (2.9, 1.4, 0.1), flat("cloth", (0.85, 0.82, 0.75), 0.9))
    box((1.8, 5.0, 1.0), (1.2, 0.05, 0.9), flat("clothr", (0.6, 0.08, 0.1), 0.9))
    CA = flat("candle", (0.95, 0.92, 0.82), 0.6); FLM = flat("flame2", (1.0, 0.65, 0.25), 0.9, emit=25)
    for x in (0.9, 1.4, 2.2, 2.7):
        cyl((x, 5.7, 1.55), 0.06, 0.5, CA, 12); sphere((x, 5.7, 1.86), 0.05, FLM, (1, 1, 1.8), sub=2)
    point_light((1.8, 5.2, 2.2), 160, (1.0, 0.6, 0.3), 0.3)
    cyl((1.8, 5.75, 2.4), 0.04, 1.6, flat("gold", (0.9, 0.7, 0.2), 0.3, metal=1)); box((1.8, 5.75, 2.9), (0.6, 0.05, 0.08), flat("gold2", (0.9, 0.7, 0.2), 0.3, metal=1))
    for x in (-3.5, 3.8):
        cyl((x, 3, 4), 0.45, 8, S, 24)                                      # pillars
    BN = wood("bench")
    for y in (2.6, 3.8):
        box((3.6, y, 0.45), (3.4, 0.5, 0.12), BN); box((3.6, y + 0.2, 0.8), (3.4, 0.08, 0.6), BN)
    interior_world((0.04, 0.03, 0.05), 1.0)
    area_light((0, 6.2, 4.6), (-1, 0, 0.5), 300, 1.6, (0.7, 0.75, 1.0))
    point_light((-3, -2, 4), 80, (0.5, 0.55, 0.9), 1.0)


# ================================================================== GATE (courtyard side of the gatehouse)
def set_gate(light="dawn", open_=True):
    S, SD = wall_mats("normal")
    box((-8.5, 8, 6), (11, 4, 12), S, 0.04); box((8.5, 8, 6), (11, 4, 12), S, 0.04); box((0, 8, 10), (6, 4, 4), S, 0.04)
    merlons(-13, 13, 6.2, 12, S)
    tower(-6, 8.5, 3.2, 16, SD); tower(6, 8.5, 3.2, 16, SD)
    W = wood("door", (0.28, 0.16, 0.08), (0.48, 0.30, 0.14))
    ang = 75 if open_ else 0
    for sgn in (-1, 1):
        d = box((0, 0, 0), (2.9, 0.3, 7.6), W, 0.02)
        d.location = (sgn * 2.9 + (-sgn) * 1.45 * math.cos(math.radians(ang)), 6.0 - 1.45 * math.sin(math.radians(ang)), 3.8)
        d.rotation_euler.z = math.radians(-sgn * ang)
        for z in (1.5, 3.8, 6.1):
            b = box((0, 0, 0), (2.9, 0.34, 0.25), flat("iron_b", (0.12, 0.12, 0.13), 0.5, metal=0.8)); b.location = (d.location.x, d.location.y, z); b.rotation_euler.z = d.rotation_euler.z
    box((0, 8.2, 11.0), (5.6, 0.25, 2.2), flat("portc", (0.15, 0.15, 0.16), 0.5, metal=0.7))   # raised portcullis
    # outside visible through the gate: bright meadow
    G = noisy("grass_g", (0.18, 0.40, 0.10), (0.45, 0.62, 0.18), 0.1, bump=0)
    grid_ground(200, 60, G, lambda x, y: 0.0 if y < 10 else -0.3, loc=(0, 105, 0))
    D = noisy("dirt", (0.36, 0.28, 0.18), (0.52, 0.42, 0.28), 0.4, bump=0.3)
    grid_ground(60, 40, D, lambda x, y: 0.05 * math.sin(x) * math.cos(y), loc=(0, -20, 0))
    BR = wood("barrel"); HY = noisy("hay2", (0.55, 0.42, 0.15), (0.80, 0.66, 0.28), 3.0, bump=0.5)
    for x, y in ((-7, 2), (-6.2, 3), (7.5, 1.5)):
        cyl((x, y, 0.7), 0.6, 1.4, BR, 20)
    sphere((6.5, 3.5, 0.6), 1.0, HY, (1.4, 1, 0.6), sub=2)
    box((-14, -10, 6), (4, 40, 12), S); box((14, -10, 6), (4, 40, 12), S)
    point("gate", (0, 6.2, 3.5))
    sky(light)
    area_light((0, 14, 4), (0, 0, 1), 1500, 6, (1.0, 0.8, 0.6)); area_light((2, -10, 6), (0, 2, 1), 1200, 8, (1.0, 0.92, 0.85))
