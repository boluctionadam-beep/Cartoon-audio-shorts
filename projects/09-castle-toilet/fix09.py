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
