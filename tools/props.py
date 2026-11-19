"""Medieval prop library for set dressing (bpy). Procedural props + Poly Haven models + heraldry textures.
All functions take a world location, optional yaw (degrees) and scale; they return the created object(s).
Use dress() to scatter themed props around a set while keeping character areas clear."""
import bpy, math, os, random
from mathutils import Vector
import scene_kit as K
from PIL import Image, ImageDraw

TEX = os.path.expanduser("~/.cache/props_tex"); os.makedirs(TEX, exist_ok=True)
_M = {}


def M(name):
    """shared materials"""
    if name in _M and _M[name].name in bpy.data.materials: return _M[name]
    f = {
        "wood": lambda: K.pbr("p_wood", "brown_planks_03", scale=1.2, bump=0.8),
        "darkwood": lambda: K.pbr("p_dwood", "dark_wooden_planks", scale=1.5, bump=0.8),
        "iron": lambda: K.flat("p_iron", (0.10, 0.10, 0.11), 0.45, metal=0.9),
        "gold": lambda: K.flat("p_gold", (0.95, 0.70, 0.22), 0.25, metal=1.0),
        "rope": lambda: K.noisy("p_rope", (0.55, 0.45, 0.28), (0.72, 0.62, 0.40), 8.0, bump=0.6),
        "burlap": lambda: K.pbr("p_burlap", "rough_linen", scale=3.0, tint=(0.75, 0.6, 0.42), bump=1.0),
        "hay": lambda: _hay(),
        "stone": lambda: K.pbr("p_stone", "medieval_blocks_05", scale=1.0, bump=1.2),
        "flame": lambda: K.flat("p_flame", (1.0, 0.42, 0.06), 0.9, emit=7),
        "ember": lambda: K.flat("p_ember", (1.0, 0.3, 0.05), 0.9, emit=12),
        "bread": lambda: K.noisy("p_bread", (0.55, 0.30, 0.10), (0.78, 0.52, 0.22), 6.0, bump=0.5),
        "apple": lambda: K.flat("p_apple", (0.70, 0.06, 0.05), 0.35),
        "candle": lambda: K.flat("p_candle", (0.95, 0.92, 0.82), 0.6),
        "cloth_red": lambda: K.flat("p_red", (0.55, 0.05, 0.06), 0.8),
        "cloth_blue": lambda: K.flat("p_blue", (0.08, 0.16, 0.50), 0.8),
        "paper": lambda: K.flat("p_paper", (0.90, 0.84, 0.66), 0.8),
        "glow": lambda: K.flat("p_glow", (1.0, 0.72, 0.38), 0.9, emit=6),
    }[name]
    _M[name] = f(); return _M[name]


def _hay():
    """straw: streaky wave texture, golden"""
    m = bpy.data.materials.new("p_hay"); m.use_nodes = True; N, L = m.node_tree.nodes, m.node_tree.links; b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); w = N.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"
    w.inputs["Scale"].default_value = 18; w.inputs["Distortion"].default_value = 14; w.inputs["Detail"].default_value = 6
    L.new(tc.outputs["Object"], w.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.42, 0.28, 0.08, 1); cr.color_ramp.elements[1].color = (0.86, 0.66, 0.24, 1)
    L.new(w.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; L.new(w.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.85
    return m


def _yaw(o, yaw):
    o.rotation_euler.z = math.radians(yaw); return o


def _join(objs, name):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = bpy.context.object; o.name = name
    return o


# ------------------------------------------------------------------ heraldry & painted textures
def heraldry(kind="lions", bg=(150, 20, 24), fg=(240, 190, 50), w=512, h=768, shape="banner"):
    path = os.path.join(TEX, f"{shape}_{kind}_{bg}_{fg}.png")
    if os.path.exists(path): return path
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shape == "banner":
        d.polygon([(0, 0), (w, 0), (w, h * 0.86), (w / 2, h), (0, h * 0.86)], fill=(*bg, 255))
        d.line([(14, 14), (w - 14, 14), (w - 14, h * 0.85), (w / 2, h - 16), (14, h * 0.85), (14, 14)], fill=(*fg, 255), width=12)
    else:   # heater shield
        pts = [(0, 0), (w, 0), (w, h * 0.45)] + [(w / 2 + (w / 2) * math.cos(a), h * 0.45 + (h * 0.55) * math.sin(a)) for a in [i / 20 * math.pi for i in range(21)]] + [(0, h * 0.45)]
        d.polygon(pts, fill=(*bg, 255)); d.line(pts + [pts[0]], fill=(40, 30, 20, 255), width=16)
    cx = w / 2
    if kind == "lions":
        for k in range(3 if shape == "banner" else 2):
            y = h * (0.2 + k * 0.24); s = w / 300
            d.ellipse([cx - 70 * s, y - 20 * s, cx + 50 * s, y + 25 * s], fill=(*fg, 255)); d.ellipse([cx + 30 * s, y - 45 * s, cx + 85 * s, y + 5 * s], fill=(*fg, 255))
            for lx in (-55, -25, 5, 30): d.rectangle([cx + lx * s, y + 15 * s, cx + (lx + 12) * s, y + 50 * s], fill=(*fg, 255))
            d.line([(cx - 70 * s, y), (cx - 105 * s, y - 40 * s)], fill=(*fg, 255), width=int(10 * s))
    elif kind == "lilies":
        for gy in range(3):
            for gx in range(2 + gy % 2):
                x = w * ((gx + 0.5) / (2 + gy % 2)); y = h * (0.2 + gy * 0.25); s = w / 260
                for dx, dy, rx, ry in ((0, -24, 12, 30), (-22, -2, 16, 10), (22, -2, 16, 10), (0, 20, 7, 16)):
                    d.ellipse([x + (dx - rx) * s, y + (dy - ry) * s, x + (dx + rx) * s, y + (dy + ry) * s], fill=(*fg, 255))
                d.rectangle([x - 22 * s, y + 2 * s, x + 22 * s, y + 10 * s], fill=(*fg, 255))
    elif kind == "cross":
        d.rectangle([cx - w * 0.07, h * 0.08, cx + w * 0.07, h * 0.8], fill=(*fg, 255)); d.rectangle([w * 0.15, h * 0.3, w * 0.85, h * 0.42], fill=(*fg, 255))
    elif kind == "chevron":
        d.polygon([(0, h * 0.55), (cx, h * 0.25), (w, h * 0.55), (w, h * 0.7), (cx, h * 0.4), (0, h * 0.7)], fill=(*fg, 255))
    im.save(path); return path


def pattern_tex(kind="carpet", c0=(130, 18, 24), c1=(230, 180, 60), c2=(20, 30, 90), w=512, h=1024):
    path = os.path.join(TEX, f"{kind}_{c0}_{c1}_{c2}.png")
    if os.path.exists(path): return path
    im = Image.new("RGB", (w, h), c0); d = ImageDraw.Draw(im)
    if kind == "carpet":
        d.rectangle([0, 0, w - 1, h - 1], outline=c1, width=26); d.rectangle([40, 40, w - 41, h - 41], outline=c2, width=14)
        for y in range(120, h - 100, 130):
            d.polygon([(w / 2, y - 50), (w / 2 + 70, y), (w / 2, y + 50), (w / 2 - 70, y)], fill=c1); d.ellipse([w / 2 - 18, y - 18, w / 2 + 18, y + 18], fill=c2)
            for x in (90, w - 90): d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=c1)
    elif kind == "tapestry":
        d.rectangle([0, 0, w - 1, h - 1], outline=c1, width=30)
        for y in range(80, h, 60): d.line([(40, y), (w - 40, y + 10)], fill=tuple(int(c * 0.85) for c in c0), width=6)
        d.ellipse([w / 2 - 120, h * 0.3, w / 2 + 120, h * 0.3 + 240], fill=c2); d.ellipse([w / 2 - 80, h * 0.3 + 40, w / 2 + 80, h * 0.3 + 200], fill=c1)
        for x in range(60, w - 40, 60): d.polygon([(x, h - 40), (x + 30, h - 90), (x + 60, h - 40)], fill=c1)
    im.save(path); return path


def window_tex(w=256, h=512, glow=(255, 190, 90)):
    path = os.path.join(TEX, f"window_{glow}.png")
    if os.path.exists(path): return path
    im = Image.new("RGB", (w, h), glow); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(40, 26, 14), width=22); d.line([(w / 2, 0), (w / 2, h)], fill=(40, 26, 14), width=14)
    d.line([(0, h * 0.45), (w, h * 0.45)], fill=(40, 26, 14), width=14)
    for y in range(30, h, 70):
        d.line([(30, y), (w / 2 - 20, y + 20)], fill=tuple(int(c * 0.85) for c in glow), width=3)
    im.save(path); return path


# ------------------------------------------------------------------ lights
def torch(loc, yaw=0, wall=True, light=180, s=1.0):
    x, y, z = loc
    stick = K.cyl((0, 0, 0), 0.04 * s, 0.6 * s, M("darkwood"), 8)
    cup = K.cyl((0, 0, 0.33 * s), 0.09 * s, 0.14 * s, M("iron"), 12, r2=0.06 * s)
    f1 = K.sphere((0, 0, 0.48 * s), 0.09 * s, M("flame"), (1, 1, 1.9), sub=2); f2 = K.sphere((0.02, 0.01, 0.58 * s), 0.05 * s, M("flame"), (1, 1, 2.2), sub=2)
    o = _join([stick, cup, f1, f2], "torch"); o.location = loc
    if wall: o.rotation_euler = (math.radians(-25), 0, math.radians(yaw)); K.box((x, y, z - 0.05), (0.06, 0.18, 0.08), M("iron"))
    l = K.point_light((x, y, z + 0.55 * s), light, (1.0, 0.55, 0.22), 0.15); return o


def candle(loc, h=0.25, light=0):
    x, y, z = loc
    c = K.cyl((x, y, z + h / 2), 0.03, h, M("candle"), 10)
    K.sphere((x, y, z + h + 0.03), 0.022, M("flame"), (1, 1, 1.8), sub=2)
    if light: K.point_light((x, y, z + h + 0.1), light, (1.0, 0.62, 0.3), 0.05)
    return c


def lantern(loc, light=60):
    o = K.place("wooden_lantern_01", loc, 1.0, 0, variant=0)
    K.point_light((loc[0], loc[1], loc[2] + 0.2), light, (1.0, 0.62, 0.3), 0.05)
    K.sphere((loc[0], loc[1], loc[2] + 0.18), 0.05, M("glow"), sub=2)
    return o


def campfire(loc, light=600):
    x, y, z = loc
    for i in range(6):
        a = i * math.pi / 3; lg = K.cyl((x + 0.25 * math.cos(a), y + 0.25 * math.sin(a), z + 0.12), 0.06, 0.7, M("darkwood"), 8)
        lg.rotation_euler = (math.radians(70), 0, a + math.pi / 2)
    for i in range(10):
        a = i * math.pi / 5; K.sphere((x + 0.6 * math.cos(a), y + 0.6 * math.sin(a), z + 0.06), 0.12, M("stone"), (1, 1, 0.6), sub=1, smooth=False)
    for i, (dx, dy, h) in enumerate(((0, 0, 0.6), (0.1, 0.05, 0.4), (-0.1, -0.05, 0.45))):
        K.sphere((x + dx, y + dy, z + 0.25 + h / 2), 0.16, M("flame"), (1, 1, h * 3), sub=2)
    K.point_light((x, y, z + 0.8), light, (1.0, 0.5, 0.18), 0.3)


def window_lit(loc, yaw=0, w=0.8, h=1.3, light=0):
    p = K.plane(loc, (w, h), K.image_mat("window", window_tex(), emit=4.0, alpha=False), rot=(math.radians(90), 0, math.radians(yaw)))
    if light: K.point_light((loc[0] - 0.4 * math.sin(math.radians(yaw)), loc[1] + 0.4 * math.cos(math.radians(yaw)), loc[2]), light, (1.0, 0.65, 0.35), 0.3)
    return p


# ------------------------------------------------------------------ cloth, heraldry
def banner(loc, yaw=0, w=1.2, h=2.4, kind="lions", bg=(150, 20, 24), fg=(240, 190, 50), wave=0.06):
    img = heraldry(kind, bg, fg)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=14, y_subdivisions=24, size=1, location=loc); b = bpy.context.object
    b.scale = (w, h, 1); b.rotation_euler = (math.radians(90), 0, math.radians(yaw)); b.data.materials.append(K.image_mat("banner_" + kind, img, emit=0.05))
    if wave:
        wv = b.modifiers.new("w", "WAVE"); wv.height = wave; wv.width = 0.8; wv.use_normal = True
    rod = K.cyl((loc[0], loc[1], loc[2] + h / 2 + 0.03), 0.03, w * 1.15, M("darkwood"), 8); rod.rotation_euler = (0, math.radians(90), math.radians(yaw))
    return b


def shield(loc, yaw=0, s=0.7, kind="lions", bg=(150, 20, 24), fg=(240, 190, 50)):
    img = heraldry(kind, bg, fg, 384, 448, "shield")
    return K.plane(loc, (s, s * 448 / 384), K.image_mat("shield_" + kind, img, emit=0.05), rot=(math.radians(90), 0, math.radians(yaw)))


def carpet(loc, yaw=0, w=2.0, l=5.0, c0=(130, 18, 24)):
    return K.plane(loc, (w, l), K.image_mat("carpet", pattern_tex("carpet", c0), alpha=False), rot=(0, 0, math.radians(yaw)))


def tapestry(loc, yaw=0, w=1.6, h=2.6, c0=(30, 60, 40)):
    return K.plane(loc, (w, h), K.image_mat("tapestry", pattern_tex("tapestry", c0, (220, 170, 60), (140, 20, 30)), alpha=False), rot=(math.radians(90), 0, math.radians(yaw)))


def flag_pole(loc, h=6, color=(0.12, 0.22, 0.62), w=2.0):
    x, y, z = loc; K.cyl((x, y, z + h / 2), 0.06, h, M("darkwood"), 8)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=8, size=1, location=(x + w / 2, y, z + h - 0.6)); f = bpy.context.object
    f.scale = (w, 1.2, 1); f.rotation_euler.x = math.radians(90); f.data.materials.append(K.flat("flagc", color, 0.8))
    wv = f.modifiers.new("w", "WAVE"); wv.height = 0.15; wv.width = 1.0; wv.use_normal = True
    return f


# ------------------------------------------------------------------ furniture & clutter
def sack(loc, yaw=0, s=1.0):
    o = K.sphere(loc, 0.32 * s, M("burlap"), (1, 0.8, 1.15), sub=3); o.location.z += 0.3 * s
    K.cyl((loc[0], loc[1], loc[2] + 0.68 * s), 0.07 * s, 0.12 * s, M("rope"), 8); return _yaw(o, yaw)


def hay_bale(loc, yaw=0, s=1.0):
    return _yaw(K.box((loc[0], loc[1], loc[2] + 0.3 * s), (1.0 * s, 0.6 * s, 0.6 * s), M("hay"), 0.08), yaw)


def rope_coil(loc, s=1.0):
    out = []
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.22 * s - i * 0.01, minor_radius=0.025 * s, location=(loc[0], loc[1], loc[2] + 0.025 * s + i * 0.045 * s))
        t = bpy.context.object; t.data.materials.append(M("rope")); out.append(t)
    return out


def cauldron(loc, fire=True):
    x, y, z = loc
    b = K.sphere((x, y, z + 0.5), 0.4, M("iron"), (1, 1, 0.85), sub=3)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.36, minor_radius=0.04, location=(x, y, z + 0.78)); bpy.context.object.data.materials.append(M("iron"))
    K.cyl((x, y, z + 0.76), 0.33, 0.02, K.flat("stew", (0.45, 0.25, 0.08), 0.3), 24)
    if fire: campfire((x, y, z), 300)
    return b


def weapon_rack(loc, yaw=0):
    x, y, z = loc; objs = []
    for dx in (-0.8, 0.8): objs.append(K.cyl((dx, 0, 0.6), 0.05, 1.2, M("darkwood"), 8))
    bar = K.cyl((0, 0, 1.05), 0.04, 1.8, M("darkwood"), 8); bar.rotation_euler.y = math.radians(90); objs.append(bar)
    for i, dx in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):
        sp = K.cyl((dx, 0.12, 1.0), 0.022, 2.0, M("wood"), 6); sp.rotation_euler.x = math.radians(-8); objs.append(sp)
        tip = K.cyl((dx, 0.0, 2.05), 0.05, 0.22, M("iron"), 6, r2=0.0); objs.append(tip)
    o = _join(objs, "rack"); o.location = loc; return _yaw(o, yaw)


def cart(loc, yaw=0, load="hay"):
    objs = []
    objs.append(K.box((0, 0, 0.75), (2.2, 1.2, 0.12), M("wood"), 0.02))
    for sx in (-1, 1): objs.append(K.box((0, sx * 0.58, 0.95), (2.2, 0.06, 0.35), M("wood"), 0.01))
    for sx in (-1, 1): objs.append(K.box((sx * 1.08, 0, 0.95), (0.06, 1.2, 0.35), M("wood"), 0.01))
    for sy in (-1, 1):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.05, location=(0, sy * 0.68, 0.5), rotation=(math.radians(90), 0, 0)); w = bpy.context.object
        w.data.materials.append(M("darkwood")); objs.append(w)
        for k in range(6):
            sp = K.cyl((0, sy * 0.68, 0.5), 0.022, 0.92, M("darkwood"), 6); sp.rotation_euler = (0, k * math.pi / 6, 0); objs.append(sp)
    for sy in (-0.45, 0.45):
        sh = K.cyl((1.9, sy, 0.65), 0.04, 1.8, M("darkwood"), 6); sh.rotation_euler = (0, math.radians(80), 0); objs.append(sh)
    if load == "hay": objs.append(K.sphere((0, 0, 1.05), 0.9, M("hay"), (1.15, 0.6, 0.45), sub=2))
    o = _join(objs, "cart"); o.location = loc
    if load == "sacks":
        for i in range(4): sack((loc[0] - 0.6 + i * 0.4, loc[1], loc[2] + 0.8), i * 30, 0.8)
    return _yaw(o, yaw)


def fence(a, b, posts=6, h=1.0):
    ax, ay, az = a; bx, by, bz = b; objs = []
    for i in range(posts):
        t = i / (posts - 1); objs.append(K.box((ax + (bx - ax) * t, ay + (by - ay) * t, az + h / 2), (0.1, 0.1, h), M("darkwood"), 0.01))
    L = math.hypot(bx - ax, by - ay); ang = math.atan2(by - ay, bx - ax)
    for zz in (0.35, 0.8):
        r = K.box(((ax + bx) / 2, (ay + by) / 2, az + zz * h), (L, 0.06, 0.08), M("wood"), 0.01); r.rotation_euler.z = ang; objs.append(r)
    return objs


def table_feast(loc, yaw=0):
    t = K.place("WoodenTable_01", loc, 1.0, math.radians(yaw), variant=0)
    top = loc[2] + max(0.7, t.dimensions.z)
    x, y = loc[0], loc[1]; r = random.Random(int(x * 10 + y))
    for i in range(3): K.sphere((x - 0.4 + i * 0.35, y + r.uniform(-0.15, 0.15), top + 0.06), 0.12, M("bread"), (1.4, 0.8, 0.6), sub=2)
    for i in range(5): K.sphere((x + 0.5 + r.uniform(-0.2, 0.2), y + r.uniform(-0.2, 0.2), top + 0.05), 0.05, M("apple"), sub=2)
    g = K.cyl((x + 0.1, y - 0.25, top + 0.1), 0.05, 0.18, M("gold"), 12, r2=0.03)
    candle((x - 0.6, y + 0.2, top), 0.2, light=40)
    return t


def scroll(loc, yaw=0):
    p = K.plane((loc[0], loc[1], loc[2] + 0.005), (0.6, 0.4), M("paper"), rot=(0, 0, math.radians(yaw)))
    for sx in (-0.3, 0.3):
        r = K.cyl((loc[0] + sx * math.cos(math.radians(yaw)), loc[1] + sx * math.sin(math.radians(yaw)), loc[2] + 0.03), 0.03, 0.44, M("paper"), 10)
        r.rotation_euler = (math.radians(90), 0, math.radians(yaw))
    return p


def pillar(loc, r=0.45, h=6.0, mat=None):
    x, y, z = loc; mat = mat or M("stone")
    K.box((x, y, z + 0.2), (r * 2.6, r * 2.6, 0.4), mat, 0.03); K.cyl((x, y, z + h / 2), r, h, mat, 24)
    K.box((x, y, z + h - 0.2), (r * 2.6, r * 2.6, 0.4), mat, 0.03)


def chandelier(loc, n=8, r=0.7):
    x, y, z = loc
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.03, location=loc); bpy.context.object.data.materials.append(M("iron"))
    for i in range(n):
        a = 2 * math.pi * i / n; candle((x + r * math.cos(a), y + r * math.sin(a), z), 0.14)
    for i in range(3):
        a = 2 * math.pi * i / 3; c = K.cyl((x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a), z + 1.0), 0.008, 2.0, M("iron"), 4)
    K.point_light((x, y, z + 0.2), 220, (1.0, 0.62, 0.3), 0.5)


def barrels(loc, n=2, yaw=0):
    out = []
    for i in range(n):
        out.append(K.place("wooden_barrels_01", (loc[0] + i * 0.8 * math.cos(math.radians(yaw)), loc[1] + i * 0.8 * math.sin(math.radians(yaw)), loc[2]), 1.0, i * 0.7, variant=i % 2))
    return out


def crate_stack(loc, yaw=0):
    a = K.place("wooden_crate_01", loc, 1.2, math.radians(yaw), variant=0)
    b = K.place("wooden_crate_01", (loc[0] + 0.1, loc[1] + 0.05, loc[2] + a.dimensions.z), 1.1, math.radians(yaw + 15), variant=0)
    return [a, b]


# ------------------------------------------------------------------ scattering
CLUTTER = ["sack", "hay", "barrels", "crates", "bucket", "rope", "stump", "rocks"]


def dress(region, n, kinds=CLUTTER, z=lambda x, y: 0.0, clear=None, seed=1):
    """scatter n themed clutter props over region=(x0,x1,y0,y1); clear(x,y)->True keeps that spot empty"""
    r = random.Random(seed); placed = []
    for i in range(n * 4):
        if len(placed) >= n: break
        x, y = r.uniform(region[0], region[1]), r.uniform(region[2], region[3])
        if clear and clear(x, y): continue
        if any(math.hypot(x - px, y - py) < 0.9 for px, py in placed): continue
        k = r.choice(kinds); zz = z(x, y); yaw = r.uniform(0, 360)
        if k == "sack": sack((x, y, zz), yaw, r.uniform(0.8, 1.1))
        elif k == "hay": hay_bale((x, y, zz), yaw)
        elif k == "barrels": barrels((x, y, zz), r.choice((1, 2)), yaw)
        elif k == "crates": crate_stack((x, y, zz), yaw)
        elif k == "bucket": K.place("wooden_bucket_01", (x, y, zz), 1.0, math.radians(yaw), variant=0)
        elif k == "rope": rope_coil((x, y, zz))
        elif k == "stump": K.place("tree_stump_01", (x, y, zz), r.uniform(0.7, 1.0), math.radians(yaw))
        elif k == "rocks": K.place("rock_moss_set_01", (x, y, zz), r.uniform(0.15, 0.3), math.radians(yaw))
        elif k == "shrub": K.place("shrub_02", (x, y, zz), r.uniform(0.6, 1.0), math.radians(yaw))
        elif k == "candle": candle((x, y, zz), r.uniform(0.15, 0.3), light=20)
        placed.append((x, y))
    return placed
