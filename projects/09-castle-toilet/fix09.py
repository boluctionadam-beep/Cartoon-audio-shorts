"""Per-shot dressing added after review (CLAUDE.md 5c): story props that sit inside the camera frame.
Called from shots09.build() through the shot key  extra="<name>"  ->  dress_<name>(sh)."""
import math, random, os
import bpy
from scene_kit import box, cyl, sphere, plane, flat, text_image, sign, point_light
import props as PR
import sets09b as S2
from sets09 import WALL_Y, TEX


def _cam_frame(sh):
    loc, tgt = sh["cam"]["loc"], sh["cam"]["target"]
    fx, fy = tgt[0] - loc[0], tgt[1] - loc[1]; L = math.hypot(fx, fy); fx, fy = fx / L, fy / L
    rx, ry = fy, -fx
    return lambda u, v: (loc[0] + fx * u + rx * v, loc[1] + fy * u + ry * v)


def _mound(x, y, r, h, m, seed=0):
    rg = random.Random(seed)
    sphere((x, y, 0.0), r, m, (1.0, rg.uniform(0.7, 1.0), h / r), sub=3)
    for i in range(5):                                                         # lumps so the heap is not a perfect dome
        a = rg.uniform(0, 2 * math.pi); d = rg.uniform(0.3, 0.8) * r
        sphere((x + math.cos(a) * d, y + math.sin(a) * d, h * 0.25), r * rg.uniform(0.25, 0.4), m, (1, 1, 0.6), sub=2)


def _pick(loc, yaw, lean):
    """pickaxe leaning against something: handle + curved iron head"""
    x, y, z = loc
    h = cyl((0, 0, 0.5), 0.025, 1.0, PR.M("wood"), 8)
    hd = cyl((0, 0, 1.0), 0.03, 0.6, PR.M("iron"), 8); hd.rotation_euler.x = math.radians(90)
    bpy.ops.object.select_all(action="DESELECT")
    for o in (h, hd): o.select_set(True)
    bpy.context.view_layer.objects.active = h; bpy.ops.object.join(); o = bpy.context.object
    o.location = (x, y, z); o.rotation_euler = (math.radians(lean), 0, math.radians(yaw)); return o


def _shovel(loc, yaw, lean):
    x, y, z = loc
    h = cyl((0, 0, 0.55), 0.022, 1.1, PR.M("wood"), 8)
    b = box((0, 0, 0.05), (0.24, 0.03, 0.3), PR.M("iron"))
    bpy.ops.object.select_all(action="DESELECT")
    for o in (h, b): o.select_set(True)
    bpy.context.view_layer.objects.active = h; bpy.ops.object.join(); o = bpy.context.object
    o.location = (x, y, z); o.rotation_euler = (math.radians(lean), 0, math.radians(yaw)); return o


def _wheelbarrow(loc, yaw):
    x, y, z = loc; W = PR.M("wood")
    tub = cyl((0, 0, 0.55), 0.42, 0.34, W, 12, r2=0.28); tub.scale = (1.3, 0.85, 1)
    dirt = sphere((0, 0, 0.72), 0.36, S2.mat("dirt"), (1.25, 0.8, 0.35), sub=2)
    wh = cyl((0.7, 0, 0.22), 0.22, 0.06, PR.M("darkwood"), 16); wh.rotation_euler.x = math.radians(90)
    arms = [box((-0.55, s * 0.28, 0.5), (1.2, 0.05, 0.05), W) for s in (-1, 1)]
    legs = [box((-0.35, s * 0.28, 0.2), (0.05, 0.05, 0.4), W) for s in (-1, 1)]
    bpy.ops.object.select_all(action="DESELECT")
    for o in [tub, dirt, wh] + arms + legs: o.select_set(True)
    bpy.context.view_layer.objects.active = tub; bpy.ops.object.join(); o = bpy.context.object
    o.location = (x, y, z); o.rotation_euler.z = math.radians(yaw); return o


def dress_mine(sh):
    """s13 'They dug': a mine tunnel into the wall foot, timber frame, spoil heaps, tools, buckets, lantern, foreground dirt."""
    D, R = S2.mat("dirt"), S2.mat("rough")
    ty = WALL_Y - 1.25                                                           # front face of the talus at ground level
    # dark tunnel mouth (half-disc) with a timber frame
    bpy.ops.mesh.primitive_circle_add(vertices=32, radius=0.85, fill_type="NGON", location=(0.1, ty - 0.02, 0.0), rotation=(math.radians(90), 0, 0))
    m = bpy.context.object; m.data.materials.append(flat("tunnel", (0.006, 0.004, 0.003), 1.0)); m.scale = (1.0, 1.25, 1.0)
    for sx in (-0.72, 0.92): box((sx, ty - 0.12, 0.6), (0.16, 0.16, 1.25), PR.M("darkwood"))
    box((0.1, ty - 0.12, 1.27), (1.95, 0.2, 0.18), PR.M("darkwood"))
    for i, sx in enumerate((-0.45, 0.65)): box((sx, ty - 0.2, 1.0 - i * 0.1), (0.05, 0.04, 0.6), PR.M("wood"), rot=(0, math.radians(20 - 40 * i), 0))
    PR.lantern((1.05, ty - 0.3, 1.25), 50)
    # spoil heaps of fresh dirt around the tunnel and a dirt apron on the ground
    cyl((0.1, 0.4, 0.09), 3.4, 0.04, D, 48)
    for i, (x, y, r, h) in enumerate(((-2.3, 1.7, 1.1, 0.7), (2.4, 1.9, 1.0, 0.6), (-0.4, -0.6, 0.5, 0.22), (3.1, 0.3, 0.7, 0.35), (-3.0, 0.2, 0.8, 0.4))):
        _mound(x, y, r, h, D, seed=i)
    # tools and work clutter (kept off the hero spots at x=-1.05 / 1.15, y~1)
    _wheelbarrow((2.25, -0.2, 0.1), 200)
    _pick((-1.75, 2.2, 0.0), 20, -14); _pick((1.75, 2.35, 0.0), -30, 12)
    _shovel((-0.45, 2.45, 0.0), 10, 8)
    for (x, y) in ((0.55, 0.25), (-2.0, 0.6)): S2.place("wooden_bucket_01", (x, y, 0.1), 1.0, random.uniform(0, 6))
    PR.rope_coil((1.6, 1.6, 0.1)); PR.sack((-2.7, -0.3, 0.1), 30, 0.9)
    for (x, y, s) in ((-3.3, 1.2, 0.5), (3.4, 1.5, 0.6)):
        box((x, y, 0.35 * s), (1.6 * s, 0.25, 0.25), PR.M("darkwood"), rot=(0, 0, math.radians(15)))   # spare props/timbers
    # foreground: dirt clods + a rock cropped by the lower frame edge, blurred by DoF
    side = _cam_frame(sh)
    for i, (u, v, r) in enumerate(((1.6, -0.75, 0.42), (1.8, 0.85, 0.5), (2.6, -1.1, 0.35))):
        x, y = side(u, v); _mound(x, y, r, r * 0.55, D, seed=10 + i)
    x, y = side(2.2, 0.55); S2.place("rock_moss_set_01", (x, y, 0.05), 0.22, 1.0)


def dress_hunger(sh):
    """s15 'they starved the place for months': empty bowls on a bare table, empty sacks, upturned barrels, a tally board."""
    side = _cam_frame(sh)
    W = PR.M("wood")
    # bare trestle table right of Roger with empty bowls, a cup and a candle
    tx, ty = side(6.4, 0.95)
    box((tx, ty, 0.78), (1.5, 0.7, 0.07), S2.mat("planks"))
    for sx in (-0.6, 0.6): box((tx + sx, ty, 0.39), (0.08, 0.6, 0.78), W)
    for i, (dx, dy) in enumerate(((-0.45, -0.1), (0.05, 0.12), (0.45, -0.12))):
        cyl((tx + dx, ty + dy, 0.85), 0.13, 0.08, W, 16, r2=0.09)
        cyl((tx + dx, ty + dy, 0.885), 0.1, 0.01, flat("bowl_in", (0.16, 0.09, 0.04), 0.7), 16)
    cyl((tx + 0.25, ty + 0.25, 0.9), 0.04, 0.16, PR.M("iron"), 10, r2=0.035)
    PR.candle((tx - 0.62, ty + 0.2, 0.815), 0.12, light=25)
    # an empty sack slumped on the bench, flat sacks and upturned barrels on the left
    for i, (u, v) in enumerate(((5.0, -1.45), (7.4, -1.3), (6.9, 1.7))):
        x, y = side(u, v); s = sphere((x, y, 0.12), 0.38, PR.M("burlap"), (1.2, 0.9, 0.28), sub=3); s.rotation_euler.z = i
    x, y = side(7.8, -1.75); PR.barrels((x, y, 0), 2, 30)
    x, y = side(8.2, 1.9); PR.crate_stack((x, y, 0), 25)
    # tally board on the left tower: months of siege
    img = text_image(os.path.join(TEX, "sign_s15_month.png"), "MONTH 6", font_size=150)
    sign(img, (-2.0, 5.78, 3.25), 1.2, 0.6, 0.0, post=False)                 # notice nailed to the gate
    # foreground cropped: an empty barrel bottom-left, a sack bottom-right (blurred by DoF)
    x, y = side(1.7, -0.62); PR.barrels((x, y, 0), 1, 0)
    x, y = side(1.9, 0.72); PR.sack((x, y, 0), 40, 0.9)


def apply(sh):
    if sh.get("extra"): globals()["dress_" + sh["extra"]](sh)


def _dust_mat(dens=0.8, col=(0.82, 0.72, 0.58), glow=0.75):
    m = bpy.data.materials.new("dustvol"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N): N.remove(n)
    out = N.new("ShaderNodeOutputMaterial"); pv = N.new("ShaderNodeVolumePrincipled"); tc = N.new("ShaderNodeTexCoord")
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.6; nz.inputs["Detail"].default_value = 8.0; nz.inputs["Roughness"].default_value = 0.62
    ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(tc.outputs["Object"], ln.inputs[0])
    fall = N.new("ShaderNodeMapRange"); fall.inputs["From Min"].default_value = 0.35; fall.inputs["From Max"].default_value = 1.0
    fall.inputs["To Min"].default_value = 1.0; fall.inputs["To Max"].default_value = 0.0; L.new(ln.outputs["Value"], fall.inputs["Value"])
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = N.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.46; cr.inputs["From Max"].default_value = 0.60; L.new(nz.outputs["Fac"], cr.inputs["Value"])
    m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; L.new(cr.outputs["Result"], m1.inputs[0]); L.new(fall.outputs["Result"], m1.inputs[1])
    m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; m2.inputs[1].default_value = dens; L.new(m1.outputs[0], m2.inputs[0])
    L.new(m2.outputs[0], pv.inputs["Density"]); pv.inputs["Color"].default_value = (*col, 1.0); pv.inputs["Anisotropy"].default_value = 0.0
    em = N.new("ShaderNodeMath"); em.operation = "MULTIPLY"; em.inputs[1].default_value = glow; L.new(m2.outputs[0], em.inputs[0])
    L.new(em.outputs[0], pv.inputs["Emission Strength"]); pv.inputs["Emission Color"].default_value = (*col, 1.0)   # self-lit dust (no dark core)
    L.new(pv.outputs["Volume"], out.inputs["Volume"]); return m


def dress_breach(sh):
    """s16 'The first wall collapsed': volumetric dust instead of grey balls, masonry blocks instead of crystal rubble, French banners."""
    from sets09 import world_h
    rubble, smoke = [], []
    for o in list(bpy.data.objects):
        mn = o.data.materials[0].name if o.type == "MESH" and o.data.materials and o.data.materials[0] else ""
        if mn.startswith("smoke"): smoke.append(o.location.copy()); bpy.data.objects.remove(o)
        elif mn.startswith("stone_d") and o.name.startswith("Ico"): rubble.append((o.location.copy(), max(o.dimensions) / 2)); bpy.data.objects.remove(o)
    R, D = S2.mat("rough"), S2.mat("dirt"); rg = random.Random(5)
    bx, by = -6 + math.cos(2.88) * 40, math.sin(2.88) * 40                     # breach centre
    sphere((bx, by, world_h(bx, by) - 0.6), 7.0, D, (1.0, 1.4, 0.32), sub=3)    # spill of earth and mortar under the stones
    for (p, r) in rubble:                                                        # fallen wall blocks, tumbled
        s = r * rg.uniform(0.7, 1.0)
        b = box((p.x, p.y, world_h(p.x, p.y) + s * 0.35), (s * 1.6, s * 1.0, s * 0.8), R, 0.06)
        b.rotation_euler = (rg.uniform(-0.5, 0.5), rg.uniform(-0.5, 0.5), rg.uniform(0, 3.1))
    for i in range(40):                                                          # small chips
        a = rg.uniform(2.5, 3.25); rr = 40 + rg.uniform(-6, 7); x, y = -6 + math.cos(a) * rr, math.sin(a) * rr
        b = box((x, y, world_h(x, y) + 0.1), (rg.uniform(0.2, 0.5),) * 3, R, 0.03); b.rotation_euler = (rg.uniform(0, 3), rg.uniform(0, 3), rg.uniform(0, 3))
    DM = _dust_mat()
    for i in range(10):                                                          # billowing dust cloud rising from the breach
        h = i / 9.0
        x, y = bx + rg.uniform(-4, 4) - h * 3, by + rg.uniform(-6, 6)
        r = rg.uniform(2.8, 4.2) * (1 + h * 0.5)
        sphere((x, y, world_h(x, y) + 1.5 + h * 14), 1.0, DM, (r, r, r * 0.75), sub=3)
    # French side: lily banners on poles and spears stuck in the ground near the cheering crowd
    side = _cam_frame(sh); W = PR.M("darkwood")
    for (u, v) in ((9.0, -2.6), (12.5, 2.4)):
        x, y = side(u, v); z = world_h(x, y)
        cyl((x, y, z + 2.6), 0.05, 5.2, W, 8); PR.banner((x, y + 0.05, z + 4.0), 0, 1.0, 1.8, "lilies", (30, 50, 150), (240, 200, 60))
    for i in range(6):
        x, y = side(rg.uniform(5, 14), rg.uniform(-3.5, 3.5)); z = world_h(x, y)
        sp = cyl((x, y, z + 1.2), 0.025, 2.4, PR.M("wood"), 6); sp.rotation_euler = (rg.uniform(-0.25, 0.25), rg.uniform(-0.25, 0.25), 0)
    for i in range(3):
        x, y = side(rg.uniform(4, 8), rg.uniform(-2, 2)); z = world_h(x, y)
        img = PR.heraldry("lilies", (30, 50, 150), (240, 200, 60), 384, 448, "shield")     # shield lying flat in the grass
        plane((x, y, z + 0.1), (0.6, 0.7), PR.K.image_mat("shield_lilies", img, emit=0.05), rot=(0.0, 0.0, rg.uniform(0, 6.2)))


def _ram(loc, yaw):
    """wheeled battering ram: log on ropes under an A-frame, iron head pointing along local +x"""
    from scene_kit import wood
    LOG, W, IR, RP = wood("ram", (0.32, 0.20, 0.10), (0.5, 0.34, 0.18)), PR.M("wood"), PR.M("iron"), PR.M("rope")
    parts = []
    lg = cyl((0, 0, 1.0), 0.28, 5.0, LOG, 20); lg.rotation_euler.y = math.radians(90); parts.append(lg)
    hd = cyl((2.75, 0, 1.0), 0.36, 0.55, IR, 20, r2=0.14); hd.rotation_euler.y = math.radians(90); parts.append(hd)
    for x in (-1.8, 0.0, 1.8, 2.35):
        b = cyl((x, 0, 1.0), 0.305, 0.09, IR, 20); b.rotation_euler.y = math.radians(90); parts.append(b)
    for sx in (-1.4, 1.4):
        for sy in (-0.75, 0.75):
            parts.append(box((sx, sy, 1.25), (0.14, 0.14, 1.9), W))
        parts.append(box((sx, 0, 2.2), (0.14, 1.64, 0.14), W))
    for sy in (-0.75, 0.75):
        parts.append(box((0, sy, 2.2), (3.1, 0.14, 0.14), W)); parts.append(box((0, sy, 0.42), (3.4, 0.16, 0.16), W))
    for sx in (-0.9, 0.9): parts.append(cyl((sx, 0, 1.75), 0.03, 0.9, RP, 6)); parts.append(cyl((sx, 0, 2.2), 0.06, 0.16, RP, 10))
    for sx in (-1.2, 1.2):
        for sy in (-0.9, 0.9):
            w = cyl((sx, sy, 0.42), 0.42, 0.1, W, 20); w.rotation_euler.x = math.radians(90); parts.append(w)
            h = cyl((sx, sy * 1.06, 0.42), 0.09, 0.06, IR, 12); h.rotation_euler.x = math.radians(90); parts.append(h)
    bpy.ops.object.select_all(action="DESELECT")
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); o = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)     # bake the log's own rotation, origin -> (0,0,0)
    o.location = loc; o.rotation_euler = (0, 0, math.radians(yaw)); return o


def dress_ram(sh):
    """s17 'The second wouldn't budge': a proper battering ram against the wall, banners and ladder on the wall, battle litter."""
    _ram((-0.25, 0.6, 0.02), 70)
    sphere((0.85, 3.25, 1.0), 1.0, _dust_mat(0.6, (0.80, 0.72, 0.60), 0.8), (0.9, 0.6, 0.8), sub=3)      # puff of mortar dust at the impact
    for x in (-1.3, 2.4): PR.banner((x, WALL_Y - 0.1, 5.6), 0, 1.3, 3.4, "lions")
    S2.place("wooden_ladder", (-2.6, 2.6, 0), 1.0, math.radians(-8))
    side = _cam_frame(sh); rg = random.Random(17)
    for i in range(7):                                                            # stone chips knocked off the talus
        x, y = rg.uniform(-0.5, 1.8), rg.uniform(2.0, 2.8)
        b = box((x, y, 0.1), (rg.uniform(0.12, 0.3),) * 3, S2.mat("rough"), 0.02); b.rotation_euler = (rg.uniform(0, 3), rg.uniform(0, 3), rg.uniform(0, 3))
    PR.rope_coil((1.0, 1.2, 0.05)); S2.place("wooden_bucket_01", (2.3, 1.7, 0.02), 1.0, 0.4)
    PR.sack((-2.2, 0.4, 0.0), 20, 0.9); PR.crate_stack((2.9, 2.3, 0), 30)
    for (u, v, k) in ((1.6, -0.8, "rocks"), (1.8, 0.95, "rocks"), (2.4, -1.05, "sack")):   # foreground, cropped and blurred
        x, y = side(u, v); PR.dress((x - 0.05, x + 0.05, y - 0.05, y + 0.05), 1, [k], seed=int(u * 10))


def _swap(prefix, m):
    for o in bpy.data.objects:
        if o.type == "MESH":
            for i, mm in enumerate(o.data.materials):
                if mm and mm.name.startswith(prefix): o.data.materials[i] = m


def dress_privy():
    """toilet room (s23, s35): real stone, a PRIVY plaque, moss basket, candles, jug, rag on a hook, rushes on the floor."""
    _swap("stone_r", S2.mat("rough")); _swap("floor", S2.mat("floor")); _swap("seatw", S2.mat("planks"))
    for o in list(bpy.data.objects):                                                     # the fake light-shaft plane read as a glass sheet
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith("beam"): bpy.data.objects.remove(o)
    img = text_image(os.path.join(TEX, "sign_privy.png"), "PRIVY", font_size=230)
    sign(img, (-0.62, 2.78, 2.1), 0.8, 0.4, 0.0, post=False)
    W = PR.M("wood")
    cyl((0.98, 1.35, 1.33), 0.2, 0.24, W, 16, r2=0.24)                                   # basket of moss (medieval paper)
    sphere((0.98, 1.35, 1.45), 0.19, S2.mat("moss"), (1, 1, 0.45), sub=2)
    PR.candle((-1.0, 2.5, 1.21), 0.2, light=45); PR.candle((-0.82, 2.6, 1.21), 0.12)
    cyl((-0.95, 1.3, 1.36), 0.11, 0.3, flat("jug", (0.55, 0.30, 0.16), 0.5), 16, r2=0.07)
    box((0.95, 2.76, 2.25), (0.05, 0.06, 0.06), PR.M("iron"))
    plane((0.95, 2.74, 1.95), (0.28, 0.55), PR.M("burlap"), rot=(math.radians(90), 0, math.radians(4)))
    rg = random.Random(23)
    for i in range(6):
        x, y = rg.uniform(-1.6, 1.6), rg.uniform(-1.0, 0.9)
        sphere((x, y, 0.0), rg.uniform(0.18, 0.32), PR.M("hay"), (1.5, 1.0, 0.18), sub=2)
    box((0.0, 0.62, 0.16), (0.62, 0.34, 0.32), S2.mat("planks"), 0.02)                 # foot stool
    point_light((0.0, 0.2, 2.4), 40, (1.0, 0.7, 0.45), 0.4)


def dress_chapel():
    """chapel (s25): stone tiles + sandstone walls, a pew, candelabrum, lectern with an open book, broken flags round the hole."""
    _swap("floor_ch", S2.mat("floor")); _swap("stone_ch", S2.mat("wall"))
    W = PR.M("wood")
    for y in (2.0, 3.2):                                                                  # pews behind-right of the hole
        box((0.3, y, 0.45), (2.2, 0.45, 0.08), W); box((0.3, y + 0.22, 0.85), (2.2, 0.06, 0.6), W)
        for sx in (-1.05, 1.05): box((0.3 + sx, y + 0.05, 0.45), (0.08, 0.55, 0.9), W)
    cyl((-0.25, 2.6, 0.7), 0.035, 1.4, PR.M("iron"), 8); cyl((-0.25, 2.6, 0.04), 0.22, 0.08, PR.M("iron"), 16, r2=0.1)
    box((-0.25, 2.6, 1.42), (0.6, 0.06, 0.04), PR.M("gold"))
    for dx in (-0.28, 0.0, 0.28): PR.candle((-0.25 + dx, 2.6, 1.44), 0.2, light=25 if dx == 0 else 0)
    cyl((0.45, 3.6, 0.55), 0.05, 1.1, W, 8); lt = box((0.45, 3.6, 1.12), (0.6, 0.45, 0.04), W, rot=(math.radians(-25), 0, 0))
    for dx in (-0.13, 0.13):
        plane((0.45 + dx, 3.58, 1.16), (0.24, 0.32), flat("page", (0.92, 0.88, 0.76), 0.8), rot=(math.radians(-25), math.radians(6 if dx < 0 else -6), 0))
    rg = random.Random(25); R = S2.mat("floor")
    for i in range(9):                                                                    # cracked flagstones round the latrine hole
        a = rg.uniform(0, 2 * math.pi); d = rg.uniform(0.6, 0.95)
        b = box((-1.6 + math.cos(a) * d, 0.6 + math.sin(a) * d, 0.02), (rg.uniform(0.15, 0.3), rg.uniform(0.12, 0.25), 0.06), R, 0.01)
        b.rotation_euler = (rg.uniform(-0.2, 0.2), rg.uniform(-0.2, 0.2), rg.uniform(0, 3))


def dress_flag(sh):
    """s28 'the whole castle surrendered': lift the French flag above the keep roof, French colours on every pole, no blob trees in view."""
    from sets09 import world_h
    for o in bpy.data.objects:
        if o.type == "MESH" and o.data.materials and o.data.materials[0] and o.data.materials[0].name.startswith(("flag", "lilyg")) \
                and not o.data.materials[0].name.startswith("flagc") and o.location.z > 30:
            o.location.z += 8.5
    cyl((0.2, 4.0, 40.0), 0.15, 9.0, PR.M("darkwood"), 8)
    for m in bpy.data.materials:
        if m.name.startswith("flagc") and m.node_tree and "Principled BSDF" in m.node_tree.nodes:
            m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.12, 0.22, 0.62, 1)
    loc = sh["cam"]["loc"]; tg = sh["cam"]["target"]; a0 = math.atan2(tg[1] - loc[1], tg[0] - loc[0])
    for ob in list(bpy.data.objects):
        if ob.get("tree"):
            dx, dy = ob.location.x - loc[0], ob.location.y - loc[1]
            if math.hypot(dx, dy) < 90 and abs((math.atan2(dy, dx) - a0 + math.pi) % (2 * math.pi) - math.pi) < math.radians(30):
                bpy.data.objects.remove(ob)


def dress_gate_open(sh):
    """s26/s27: the French camp seen through the open gate, a road, and panic litter in the courtyard foreground."""
    from scene_kit import tree, wood, noisy
    plane((0, 42, 0.0), (90, 70), S2.mat("ground")); plane((0, 40, 0.02), (6, 64), S2.mat("dirt"))
    T1, T2 = flat("tentw3", (0.92, 0.90, 0.84), 0.9), flat("tentb3", (0.14, 0.24, 0.62), 0.8)
    rg = random.Random(26)
    for i, (x, y) in enumerate(((-9, 38), (8, 42), (-15, 55), (14, 58), (-5, 62), (4, 70), (-12, 72), (18, 75))):
        cyl((x, y, 1.8), 2.4, 3.6, T1 if i % 2 else T2, 20, "tent", r2=0.0); cyl((x, y, 0.5), 2.45, 1.0, T2 if i % 2 else T1, 20, "tentb")
    for (x, y) in ((-4.0, 30), (4.0, 33), (-7, 48), (9, 52)):
        cyl((x, y, 2.5), 0.06, 5.0, PR.M("darkwood"), 8); PR.banner((x, y, 4.2), 0, 1.0, 1.8, "lilies", (30, 50, 150), (240, 200, 60))
    TR, LF = wood("trunk"), noisy("leaf", (0.10, 0.28, 0.06), (0.25, 0.46, 0.10), 0.5, bump=0.3)
    for i in range(10): tree(rg.choice([rg.uniform(-40, -20), rg.uniform(20, 40)]), rg.uniform(60, 100), 0, rg.uniform(1.6, 2.4), (TR, LF))
    PR.campfire((10, 46, 0), 300); PR.cart((-6, 26, 0), 100, "sacks")
    side = _cam_frame(sh)
    for i, (u, v) in enumerate(((2.2, -0.9), (2.6, 0.95), (3.8, -1.4))):            # spilled sacks / dropped shield at the frame edges
        x, y = side(u, v); s = sphere((x, y, 0.15), 0.4, PR.M("burlap"), (1.2, 0.9, 0.35), sub=3); s.rotation_euler.z = i
    for i in range(5):                                                                # spears dropped by the fleeing defenders
        x, y = side(rg.uniform(3.0, 6.5), rg.uniform(-1.6, 1.6))
        sp = cyl((x, y, 0.08), 0.025, 2.4, PR.M("wood"), 6); sp.rotation_euler = (math.radians(90), 0, rg.uniform(0, 3.1))
    x, y = side(4.5, 1.3); S2.place("wooden_bucket_01", (x, y, 0.05), 1.0, 1.0)
    x, y = side(2.8, -1.35); PR.barrels((x, y, 0), 1, 0)
