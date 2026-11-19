"""Blender scene kit (bpy 5.x, Cycles CPU) for stylised 3D worlds behind 2D character cards.

Characters are planes with the card image. By default they are SHADOW-ONLY (invisible to the camera, still cast
shadows); the compositor draws them in 2D so they can be animated. `baked=True` renders them in 3D instead
(use when geometry must occlude them). After render, export() writes the projected card corners (pixels) and
named screen points to JSON for the compositor.
"""
import bpy, math, random, json, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view as w2c

OVERSCAN = 1.10
CARDS = []       # (name, obj, image_path, baked)
POINTS = {}      # name -> world Vector


# ------------------------------------------------------------------ basics
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    CARDS.clear(); POINTS.clear()
    return bpy.context.scene


def _nodes(m):
    m.use_nodes = True
    return m.node_tree.nodes, m.node_tree.links


def flat(name, col, rough=0.8, emit=0.0, metal=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col[:3], 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*col[:3], 1); b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    return m


def stone(name="stone", base=(0.58, 0.56, 0.52), scale=0.6, row=0.55, width=1.1, var=0.72, bump=0.5, mortar=(0.30, 0.28, 0.26), rot90=True, dirt=True):
    """Big irregular stone blocks (painted look): brick texture with strong per-block tint, noise mottling, bevel bump."""
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
    if rot90: mp.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    br = N.new("ShaderNodeTexBrick"); br.offset = 0.5
    br.inputs["Mortar Size"].default_value = 0.022; br.inputs["Mortar Smooth"].default_value = 0.45
    br.inputs["Brick Width"].default_value = width; br.inputs["Row Height"].default_value = row; br.inputs["Bias"].default_value = 0.0
    br.inputs["Color1"].default_value = (*base, 1); br.inputs["Color2"].default_value = (base[0] * var, base[1] * var, base[2] * var * 0.98, 1)
    br.inputs["Mortar"].default_value = (*mortar, 1)
    L.new(mp.outputs["Vector"], br.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.2; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.6
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 0.5
    L.new(br.outputs["Color"], mix.inputs[6]); L.new(nz.outputs["Color"], mix.inputs[7])
    out = mix.outputs[2]
    if dirt:
        sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -6; mr.inputs["From Max"].default_value = 2
        mr.inputs["To Min"].default_value = 0.6; mr.inputs["To Max"].default_value = 1.0; L.new(sep.outputs["Z"], mr.inputs["Value"])
        dm = N.new("ShaderNodeMix"); dm.data_type = "RGBA"; dm.blend_type = "MULTIPLY"; dm.inputs["Factor"].default_value = 1.0
        L.new(out, dm.inputs[6]); L.new(mr.outputs["Result"], dm.inputs[7]); out = dm.outputs[2]
    L.new(out, b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; bp.inputs["Distance"].default_value = 0.08
    hm = N.new("ShaderNodeMath"); hm.operation = "MULTIPLY_ADD"; hm.inputs[1].default_value = 0.25
    L.new(nz.outputs["Fac"], hm.inputs[0]); L.new(br.outputs["Fac"], hm.inputs[2])
    L.new(hm.outputs[0], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.88
    return m


def noisy(name, c0, c1, scale=0.5, rough=0.9, bump=0.2, detail=4):
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = detail
    L.new(tc.outputs["Object"], nz.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*c0, 1); cr.color_ramp.elements[1].color = (*c1, 1)
    L.new(nz.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    if bump:
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump; L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = rough
    return m


def terrain(name="terrain", g0=(0.14, 0.34, 0.07), g1=(0.40, 0.58, 0.15), rock=(0.72, 0.68, 0.60), steep=0.75):
    """grass on flats, chalky rock on steep slopes, multi-scale colour variation (fields, patches)"""
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord")
    n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.012; n1.inputs["Detail"].default_value = 4; L.new(tc.outputs["Object"], n1.inputs["Vector"])
    n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 0.25; n2.inputs["Detail"].default_value = 8; L.new(tc.outputs["Object"], n2.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*g0, 1); cr.color_ramp.elements[1].color = (*g1, 1); L.new(n1.outputs["Fac"], cr.inputs["Fac"])
    mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "OVERLAY"; mx.inputs["Factor"].default_value = 0.35
    L.new(cr.outputs["Color"], mx.inputs[6]); L.new(n2.outputs["Color"], mx.inputs[7])
    rk = N.new("ShaderNodeTexNoise"); rk.inputs["Scale"].default_value = 0.5; rk.inputs["Detail"].default_value = 10; L.new(tc.outputs["Object"], rk.inputs["Vector"])
    rc = N.new("ShaderNodeValToRGB"); rc.color_ramp.elements[0].color = (rock[0] * .7, rock[1] * .7, rock[2] * .7, 1); rc.color_ramp.elements[1].color = (*rock, 1); L.new(rk.outputs["Fac"], rc.inputs["Fac"])
    geo = N.new("ShaderNodeNewGeometry"); sp = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sp.inputs[0])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = steep; mr.inputs["From Max"].default_value = steep + 0.08
    mr.inputs["To Min"].default_value = 1.0; mr.inputs["To Max"].default_value = 0.0; L.new(sp.outputs["Z"], mr.inputs["Value"])
    m2 = N.new("ShaderNodeMix"); m2.data_type = "RGBA"; L.new(mr.outputs["Result"], m2.inputs["Factor"]); L.new(mx.outputs[2], m2.inputs[6]); L.new(rc.outputs["Color"], m2.inputs[7])
    L.new(m2.outputs[2], b.inputs["Base Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.3; L.new(rk.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.92
    return m


def wood(name="wood", c0=(0.30, 0.17, 0.08), c1=(0.52, 0.32, 0.16), planks=True):
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 8.0, 1.0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    w = N.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = 3.0; w.inputs["Distortion"].default_value = 6; w.inputs["Detail"].default_value = 3
    L.new(mp.outputs["Vector"], w.inputs["Vector"])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*c0, 1); cr.color_ramp.elements[1].color = (*c1, 1)
    L.new(w.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.7
    return m


def water(name="water", col=(0.04, 0.34, 0.42)):
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = 0.03; b.inputs["IOR"].default_value = 1.33
    tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5
    L.new(tc.outputs["Object"], nz.inputs["Vector"]); bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15
    L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def image_mat(name, path, emit=0.0, alpha=True):
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path); t.interpolation = "Cubic"
    L.new(t.outputs["Color"], b.inputs["Base Color"])
    if alpha: L.new(t.outputs["Alpha"], b.inputs["Alpha"])
    if emit:
        L.new(t.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    b.inputs["Roughness"].default_value = 0.9; b.inputs["Specular IOR Level"].default_value = 0.1
    return m


# ------------------------------------------------------------------ geometry helpers
def box(loc, size, mat, bevel=0.0, name="box", rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # keep the origin at loc
    if bevel:
        bv = o.modifiers.new("bv", "BEVEL"); bv.width = bevel; bv.segments = 2
    if mat: o.data.materials.append(mat)
    return o


def cyl(loc, r, h, mat, verts=48, name="cyl", r2=None):
    if r2 is not None:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=h, location=loc)
    else:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc)
    o = bpy.context.object; o.name = name
    if mat: o.data.materials.append(mat)
    return o


def sphere(loc, r, mat, scale=(1, 1, 1), sub=3, smooth=True):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=loc); o = bpy.context.object
    o.scale = scale
    if smooth: bpy.ops.object.shade_smooth()
    if mat: o.data.materials.append(mat)
    return o


def plane(loc, size, mat, rot=(0, 0, 0), name="plane"):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = (size[0], size[1], 1); bpy.ops.object.transform_apply(scale=True)
    if mat: o.data.materials.append(mat)
    return o


def cut(target, cutter):
    m = target.modifiers.new("cut", "BOOLEAN"); m.object = cutter; m.operation = "DIFFERENCE"
    try: m.solver = "EXACT"
    except Exception: pass
    cutter.hide_render = True; cutter.display_type = "WIRE"
    return target


def merlons(x0, x1, y, z, mat, step=2.0, size=(1.2, 0.9, 1.3)):
    out = []
    x = x0
    while x <= x1 + 1e-6:
        out.append(box((x, y, z + size[2] / 2), size, mat, 0.04, "merlon")); x += step
    return out


def ring_wall(cx, cy, r, h, thick, mat, z0=0.0, towers=6, tower_r=None, tmat=None, crenel=True, gap=None):
    """circular curtain wall made of segments + towers (gap=(a0,a1) radians left open)"""
    n = max(16, int(2 * math.pi * r / 2.2)); seg = 2 * math.pi * r / n
    for i in range(n):
        a = 2 * math.pi * (i + 0.5) / n
        if gap and gap[0] < a < gap[1]: continue
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        o = box((x, y, z0 + h / 2), (seg * 1.16, thick, h), mat, 0.0, "seg"); o.rotation_euler.z = a + math.pi / 2
        if crenel:
            for off in (-0.25, 0.25):
                aa = a + off * seg / r
                m = box((cx + math.cos(aa) * (r - thick * 0.38), cy + math.sin(aa) * (r - thick * 0.38), z0 + h + 0.45), (seg * 0.28, 0.55, 0.9), mat, 0.02, "mer")
                m.rotation_euler.z = aa + math.pi / 2
    tr = tower_r or thick * 1.6
    for k in range(towers):
        a = 2 * math.pi * k / towers + 0.3
        if gap and gap[0] < a < gap[1]: continue
        tower(cx + math.cos(a) * r, cy + math.sin(a) * r, tr, h * 1.3, tmat or mat, z0)


def tower(x, y, r, h, mat, z0=0.0, crenel=True, roof=None):
    t = cyl((x, y, z0 + h / 2), r, h, mat, 40, "tower")
    if crenel:                                                          # corbelled cap ring instead of loose merlons
        cyl((x, y, z0 + h + 0.5), r * 1.10, 1.0, mat, 40, "tcap")
        cyl((x, y, z0 + h - 0.35), r * 1.05, 0.7, mat, 40, "tcap2")
    if roof:
        cyl((x, y, z0 + h + r * 0.9), r * 1.15, r * 1.8, roof, 40, "roof", r2=0.0)
    D = bpy.data.materials.get("slit") or flat("slit", (0.02, 0.015, 0.012), 1.0)
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        for zz in (h * 0.45, h * 0.75):
            o = box((x + math.cos(a) * (r + 0.02), y + math.sin(a) * (r + 0.02), z0 + zz), (0.12, 0.35, 1.2), D); o.rotation_euler.z = a
    return t


def tree(x, y, z, s=1.0, mats=None):
    trunk, leaf = mats
    cyl((x, y, z + 1.2 * s), 0.25 * s, 2.4 * s, trunk, 10)
    for dz, rr in ((2.8, 1.5), (3.8, 1.2), (4.6, 0.8)):
        sphere((x + random.uniform(-.2, .2) * s, y + random.uniform(-.2, .2) * s, z + dz * s), rr * s, leaf, (1, 1, 0.85), sub=2)


def grass_particles(ground, blade_mat, count=40000, region=None, length=0.38):
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.035, depth=length, location=(0, 0, -500)); blade = bpy.context.object
    for v in blade.data.vertices: v.co.z += length / 2
    blade.data.materials.append(blade_mat)
    ps = ground.modifiers.new("grass", "PARTICLE_SYSTEM").particle_system.settings
    ps.type = "HAIR"; ps.count = count; ps.hair_length = 1.0; ps.render_type = "OBJECT"; ps.instance_object = blade
    ps.particle_size = 1.0; ps.size_random = 0.6; ps.use_rotations = True; ps.rotation_mode = "OB_Z"; ps.phase_factor_random = 2.0
    ps.rotation_factor_random = 0.25; ps.use_advanced_hair = True
    if region:
        vg = ground.vertex_groups.new(name="dens")
        for v in ground.data.vertices:
            vg.add([v.index], 1.0 if region(v.co) else 0.0, "REPLACE")
        ground.particle_systems[0].vertex_group_density = "dens"
    return blade


def blade_mat():
    m = bpy.data.materials.new("blade"); N, L = _nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.05, 0.18, 0.03, 1); cr.color_ramp.elements[1].color = (0.46, 0.66, 0.16, 1)
    L.new(sep.outputs["Z"], cr.inputs["Fac"])
    oi = N.new("ShaderNodeObjectInfo"); hv = N.new("ShaderNodeMix"); hv.data_type = "RGBA"; hv.blend_type = "MULTIPLY"   # per-blade tint variation
    L.new(oi.outputs["Random"], hv.inputs["Factor"]); L.new(cr.outputs["Color"], hv.inputs[6]); hv.inputs[7].default_value = (0.75, 0.85, 0.55, 1)
    L.new(hv.outputs[2], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.6
    return m


def grid_ground(size, cuts, mat, height_fn=None, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=cuts, y_subdivisions=cuts, size=size, location=loc); g = bpy.context.object
    if height_fn:
        for v in g.data.vertices:
            wx, wy = v.co.x + loc[0], v.co.y + loc[1]; v.co.z = height_fn(wx, wy)
    g.data.materials.append(mat); bpy.ops.object.shade_smooth()
    return g


def clouds(n=6, area=(-80, 80), y=(120, 160), z=(40, 70), scale=1.0, warm=(1.0, 0.94, 0.86), seed=3):
    r = random.Random(seed); CL = flat("cloud", warm, 1.0, emit=0.3)
    for i in range(n):
        cx, cy, cz = r.uniform(*area), r.uniform(*y), r.uniform(*z)
        for j in range(7):
            sphere((cx + r.uniform(-6, 6) * scale, cy + r.uniform(-2, 2), cz + r.uniform(-1.5, 2) * scale), r.uniform(3, 5.5) * scale, CL, (1, 1, 0.55), sub=2)


def text_image(path, text, size=(1024, 512), bg=(150, 104, 60), fg=(40, 24, 12), font_size=200, border=True):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", size, (*bg, 255)); d = ImageDraw.Draw(im)
    try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception: f = None
    for i in range(0, size[1], 64):                         # plank lines
        d.line([(0, i), (size[0], i + 6)], fill=tuple(int(c * 0.8) for c in bg), width=4)
    tw = d.textlength(text, font=f); d.text(((size[0] - tw) / 2, (size[1] - font_size * 1.15) / 2), text, fill=(*fg, 255), font=f)
    if border: d.rectangle([4, 4, size[0] - 5, size[1] - 5], outline=(30, 18, 8, 255), width=14)
    im.save(path); return path


def sign(path_img, loc, w, h, rot_z=0.0, post=True, mat_post=None):
    m = image_mat("sign", path_img, emit=0.1, alpha=False)
    p = plane((loc[0], loc[1], loc[2]), (w, h), m, rot=(math.radians(90), 0, rot_z))
    if post:
        cyl((loc[0], loc[1] + 0.06, loc[2] / 2), 0.08, loc[2], mat_post or wood("post"), 8)
    return p


# ------------------------------------------------------------------ characters
def card(name, img, x, y, h=2.1, yaw=None, baked=False, feet=210 / 1800, img_wh=(1000, 1800)):
    """character card standing on z=ground at (x,y); faces the camera (set later by face_cards) or yaw (deg)."""
    from PIL import Image
    if isinstance(x, (tuple, list)): x, y, z = x
    else: z = 0.0
    w, hh = img_wh
    if os.path.exists(img):
        w, hh = Image.open(img).size
    width = h * w / hh
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0)); o = bpy.context.object; o.name = "card_" + name
    o.scale = (width, h, 1); bpy.ops.object.transform_apply(scale=True)
    for v in o.data.vertices:                                   # stand the plane up, feet line at local z=0
        v.co = Vector((v.co.x, 0, v.co.y + h / 2 - h * feet))
    o.location = (x, y, z)
    mat = bpy.data.materials.new("cardmat_" + name); N, L = _nodes(mat); b = N["Principled BSDF"]
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(img); t.interpolation = "Cubic"
    L.new(t.outputs["Color"], b.inputs["Base Color"]); L.new(t.outputs["Alpha"], b.inputs["Alpha"])
    L.new(t.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.45
    b.inputs["Roughness"].default_value = 1.0; b.inputs["Specular IOR Level"].default_value = 0.0
    o.data.materials.append(mat)
    if not baked:
        o.visible_camera = False; o.visible_glossy = False; o.visible_diffuse = True
    o["yaw"] = yaw if yaw is not None else -999
    CARDS.append((name, o, img, baked))
    return o


def face_cards(cam):
    for name, o, img, baked in CARDS:
        if o["yaw"] != -999:
            o.rotation_euler.z = math.radians(o["yaw"])
        else:
            d = cam.location - o.location; o.rotation_euler.z = math.atan2(d.x, -d.y)


def point(name, loc):
    POINTS[name] = Vector(loc)


# ------------------------------------------------------------------ camera + light
def camera(loc, target=None, rot=None, lens=24, shift=(0, 0), dof=None, fstop=2.8):
    sc = bpy.context.scene
    bpy.ops.object.camera_add(location=loc); cam = bpy.context.object; sc.camera = cam
    if target is not None:
        cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    if rot is not None:
        cam.rotation_euler = tuple(math.radians(a) for a in rot)
    cam.data.lens = lens; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24 * OVERSCAN
    cam.data.shift_x, cam.data.shift_y = shift
    cam.data.clip_end = 3000
    if dof is not None:
        cam.data.dof.use_dof = True
        if isinstance(dof, (int, float)): cam.data.dof.focus_distance = dof
        else: cam.data.dof.focus_object = dof
        cam.data.dof.aperture_fstop = fstop
    return cam


def sky(preset="golden"):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; WN, WL = w.node_tree.nodes, w.node_tree.links
    bg = WN["Background"]
    P = {
        "day":    dict(el=40, rot=-120, sun=(1.0, 0.96, 0.9), e=3.6, sky=0.22, dir=(0.6, 0.5, -0.62)),
        "golden": dict(el=14, rot=-128, sun=(1.0, 0.80, 0.56), e=4.2, sky=0.16, dir=(0.9, 0.25, -0.36)),
        "dawn":   dict(el=8, rot=-60, sun=(1.0, 0.72, 0.55), e=3.6, sky=0.15, dir=(-0.6, 0.7, -0.3)),
        "dusk":   dict(el=4, rot=-140, sun=(1.0, 0.55, 0.35), e=3.2, sky=0.12, dir=(0.95, 0.1, -0.25)),
    }
    if preset == "night":
        grad = WN.new("ShaderNodeTexGradient"); tc = WN.new("ShaderNodeTexCoord"); mp = WN.new("ShaderNodeMapping")
        mp.inputs["Rotation"].default_value = (0, math.radians(90), 0)
        WL.new(tc.outputs["Generated"], mp.inputs["Vector"]); WL.new(mp.outputs["Vector"], grad.inputs["Vector"])
        cr = WN.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.02, 0.04, 0.12, 1); cr.color_ramp.elements[1].color = (0.10, 0.16, 0.36, 1)
        WL.new(grad.outputs["Fac"], cr.inputs["Fac"]); WL.new(cr.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.7
        bpy.ops.object.light_add(type="SUN"); s = bpy.context.object
        s.rotation_euler = Vector((0.5, 0.6, -0.62)).normalized().to_track_quat("-Z", "Y").to_euler()
        s.data.energy = 1.1; s.data.color = (0.55, 0.68, 1.0); s.data.angle = math.radians(1.5)
        return s
    p = P[preset]
    COLS = {"day": ((0.70, 0.85, 1.0), (0.12, 0.40, 0.95)), "golden": ((0.98, 0.86, 0.70), (0.14, 0.42, 0.95)),
            "dawn": ((1.0, 0.74, 0.58), (0.26, 0.44, 0.88)), "dusk": ((1.0, 0.58, 0.36), (0.28, 0.26, 0.66))}
    hor, zen = COLS[preset]
    tc = WN.new("ShaderNodeTexCoord"); sep = WN.new("ShaderNodeSeparateXYZ"); WL.new(tc.outputs["Generated"], sep.inputs[0])
    nrm = WN.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; WL.new(tc.outputs["Generated"], nrm.inputs[0])
    sz = WN.new("ShaderNodeSeparateXYZ"); WL.new(nrm.outputs[0], sz.inputs[0])
    cr = WN.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[0].color = (*hor, 1)
    cr.color_ramp.elements[0].position = 0.0; cr.color_ramp.elements[1].position = 0.16; cr.color_ramp.elements[1].color = (*zen, 1)
    WL.new(sz.outputs["Z"], cr.inputs["Fac"])
    lp_ = WN.new("ShaderNodeLightPath"); bg2 = WN.new("ShaderNodeBackground"); WL.new(cr.outputs["Color"], bg2.inputs["Color"]); bg2.inputs["Strength"].default_value = 1.6
    bg.inputs["Strength"].default_value = p["sky"] * float(__import__("os").environ.get("AMB", "5.0")); WL.new(cr.outputs["Color"], bg.inputs["Color"])
    mx_ = WN.new("ShaderNodeMath"); mx_.operation = "MAXIMUM"; WL.new(lp_.outputs["Is Camera Ray"], mx_.inputs[0]); WL.new(lp_.outputs["Is Glossy Ray"], mx_.inputs[1])
    mix = WN.new("ShaderNodeMixShader"); WL.new(mx_.outputs[0], mix.inputs[0]); WL.new(bg.outputs[0], mix.inputs[1]); WL.new(bg2.outputs[0], mix.inputs[2])
    WL.new(mix.outputs[0], WN["World Output"].inputs["Surface"])
    bpy.ops.object.light_add(type="SUN"); s = bpy.context.object
    s.rotation_euler = Vector(p["dir"]).normalized().to_track_quat("-Z", "Y").to_euler()
    s.data.energy = p["e"]; s.data.color = p["sun"]; s.data.angle = math.radians(2.5)
    return s


def interior_world(col=(0.05, 0.04, 0.035), strength=1.0):
    sc = bpy.context.scene; w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (*col, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = strength


def point_light(loc, energy=300, col=(1.0, 0.7, 0.4), r=0.1):
    bpy.ops.object.light_add(type="POINT", location=loc); l = bpy.context.object
    l.data.energy = energy; l.data.color = col; l.data.shadow_soft_size = r
    return l


def area_light(loc, target, energy=500, size=2.0, col=(1, 1, 1)):
    bpy.ops.object.light_add(type="AREA", location=loc); l = bpy.context.object
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    l.data.energy = energy; l.data.size = size; l.data.color = col
    return l


# ------------------------------------------------------------------ render + export
def render(out_png, W=1440, H=2560, spp=40, exposure=-0.3, look="AgX - Punchy"):
    sc = bpy.context.scene
    face_cards(sc.camera)
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = spp
    sc.cycles.use_denoising = True; sc.cycles.max_bounces = 5; sc.cycles.transparent_max_bounces = 64
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.02
    sc.render.resolution_x, sc.render.resolution_y = int(W * OVERSCAN), int(H * OVERSCAN); sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = look; sc.view_settings.exposure = exposure
    sc.render.filepath = os.path.abspath(out_png); sc.render.image_settings.file_format = "PNG"
    sc.render.film_transparent = False
    if not os.environ.get("PROBE"):
        bpy.ops.render.render(write_still=True)
    export(out_png.replace(".png", ".json"), sc)


def export(path, sc):
    cam = sc.camera; bpy.context.view_layer.update()
    W, H = sc.render.resolution_x, sc.render.resolution_y
    def px(v):
        p = w2c(sc, cam, v); return [round(p.x * W, 1), round((1 - p.y) * H, 1), round(p.z, 3)]
    data = {"size": [W, H], "overscan": OVERSCAN, "cards": [], "points": {}}
    for name, o, img, baked in CARDS:
        mw = o.matrix_world; vs = [mw @ v.co for v in o.data.vertices]
        # order: bottom-left, bottom-right, top-right, top-left (in card image space)
        loc = [o.matrix_world.inverted() @ v for v in vs]
        order = sorted(range(4), key=lambda i: (round(loc[i].z, 3), loc[i].x))
        bl, br = sorted(order[:2], key=lambda i: loc[i].x); tl, tr = sorted(order[2:], key=lambda i: loc[i].x)
        data["cards"].append({"name": name, "img": img, "baked": baked, "quad": [px(vs[i]) for i in (tl, tr, br, bl)],
                              "dist": round((o.location - cam.location).length, 2)})
    for k, v in POINTS.items():
        data["points"][k] = px(v)
    json.dump(data, open(path, "w"), indent=1)


# ------------------------------------------------------------------ real assets (Poly Haven, CC0)
def pbr(name, aid, scale=1.0, res="2k", tint=None, bump=1.0, rough_mul=1.0, box_blend=0.25, moss=None):
    """Photo-scanned PBR material with box projection (no UVs needed). scale = texture repeats per metre.
    tint multiplies the colour (for warmer limestone etc.), moss = (aid, amount) mixes a second texture by noise."""
    import polyhaven as ph
    t = ph.tex(aid, res)
    m = bpy.data.materials.new(name); N, L = _nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def img(path, color=True):
        n = N.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(path); n.projection = "BOX"; n.projection_blend = box_blend
        if not color: n.image.colorspace_settings.name = "Non-Color"
        L.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    col = img(t["diff"]).outputs["Color"]
    if moss:
        t2 = ph.tex(moss[0], res); c2 = img(t2["diff"]).outputs["Color"]
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.35; nz.inputs["Detail"].default_value = 6
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.55 - moss[1] * 0.2; mr.inputs["From Max"].default_value = 0.62 - moss[1] * 0.2
        L.new(nz.outputs["Fac"], mr.inputs["Value"])
        mx = N.new("ShaderNodeMix"); mx.data_type = "RGBA"; L.new(mr.outputs["Result"], mx.inputs["Factor"]); L.new(col, mx.inputs[6]); L.new(c2, mx.inputs[7]); col = mx.outputs[2]
    if tint:
        tn = N.new("ShaderNodeMix"); tn.data_type = "RGBA"; tn.blend_type = "MULTIPLY"; tn.inputs["Factor"].default_value = 1.0
        tn.inputs[7].default_value = (*tint, 1); L.new(col, tn.inputs[6]); col = tn.outputs[2]
    L.new(col, b.inputs["Base Color"])
    if "rough" in t:
        r = img(t["rough"], False); mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = rough_mul
        L.new(r.outputs["Color"], mm.inputs[0]); L.new(mm.outputs[0], b.inputs["Roughness"])
    if "nor" in t:
        nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = bump
        L.new(img(t["nor"], False).outputs["Color"], nm.inputs["Color"])
        if "disp" in t:
            bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.35 * bump; bp.inputs["Distance"].default_value = 0.05
            L.new(img(t["disp"], False).outputs["Color"], bp.inputs["Height"]); L.new(nm.outputs["Normal"], bp.inputs["Normal"]); L.new(bp.outputs["Normal"], b.inputs["Normal"])
        else:
            L.new(nm.outputs["Normal"], b.inputs["Normal"])
    return m


def hdri_world(aid, strength=1.0, rot=0.0, res="2k", sat=1.15, cam_strength=None):
    """HDRI sky for lighting and background. cam_strength lets the visible sky be brighter/darker than the light it gives."""
    import polyhaven as ph
    p = ph.hdri(aid, res); sc = bpy.context.scene
    w = bpy.data.worlds.new("hdri"); sc.world = w; w.use_nodes = True; N, L = w.node_tree.nodes, w.node_tree.links
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(rot))
    env = N.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(p)
    L.new(tc.outputs["Generated"], mp.inputs["Vector"]); L.new(mp.outputs["Vector"], env.inputs["Vector"])
    hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = sat; L.new(env.outputs["Color"], hs.inputs["Color"])
    bg = N["Background"]; bg.inputs["Strength"].default_value = strength; L.new(hs.outputs["Color"], bg.inputs["Color"])
    if cam_strength is not None:
        bg2 = N.new("ShaderNodeBackground"); bg2.inputs["Strength"].default_value = cam_strength; L.new(hs.outputs["Color"], bg2.inputs["Color"])
        lp = N.new("ShaderNodeLightPath"); mx = N.new("ShaderNodeMixShader")
        L.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); L.new(bg.outputs[0], mx.inputs[1]); L.new(bg2.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], N["World Output"].inputs["Surface"])
    return w


def fog(density=0.004, color=(0.85, 0.88, 0.95), anisotropy=0.35, size=(160, 160, 70), center=(0, 0, 25)):
    """thin fog in a bounded volume box around the scene: aerial perspective + light shafts.
    (A world volume would absorb the sun and the HDRI, which sit at infinity.)"""
    m = bpy.data.materials.new("fog"); m.use_nodes = True; N, L = m.node_tree.nodes, m.node_tree.links
    N.remove(N["Principled BSDF"])
    v = N.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = density; v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Anisotropy"].default_value = anisotropy
    L.new(v.outputs[0], N["Material Output"].inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(location=center); o = bpy.context.object; o.name = "fog_domain"
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); o.data.materials.append(m)
    o.visible_shadow = False
    return o


_MODEL_CACHE = {}


def model(aid, res="1k"):
    """import a Poly Haven glTF once; returns a list of hidden template objects (one per variant node)"""
    import polyhaven as ph
    if aid in _MODEL_CACHE: return _MODEL_CACHE[aid]
    path = ph.model(aid, res)
    before = set(o.name for o in bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o.name for o in bpy.data.objects if o.name not in before]
    meshes = [bpy.data.objects[n] for n in new if bpy.data.objects[n].type == "MESH"]
    for m in meshes:
        mw = m.matrix_world.copy(); m.parent = None; m.matrix_world = mw
    for n in new:
        o = bpy.data.objects.get(n)
        if o is not None and o.type != "MESH": bpy.data.objects.remove(o)
    out = []
    for m in meshes:                                   # recentre each variant on its footprint, base at z=0
        bpy.ops.object.select_all(action="DESELECT"); m.select_set(True); bpy.context.view_layer.objects.active = m
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        vs = [v.co for v in m.data.vertices]
        cx = sum(v.x for v in vs) / len(vs); cy = sum(v.y for v in vs) / len(vs); z0 = min(v.z for v in vs)
        for v in m.data.vertices: v.co.x -= cx; v.co.y -= cy; v.co.z -= z0
        m.location = (0, 0, 0); m.name = f"tmpl_{aid}_{len(out)}"; out.append(m)
    lib = bpy.data.collections.new("lib_" + aid)                       # library collection, NOT linked to the scene
    for m in out:
        for c in list(m.users_collection): c.objects.unlink(m)
        lib.objects.link(m)
    _MODEL_CACHE[aid] = out
    return out


def place(aid, loc, scale=1.0, rot_z=0.0, res="1k", variant=None, seed=None):
    """linked copy (shares mesh data = cheap) of one variant of a model"""
    vs = model(aid, res); r = random.Random(seed if seed is not None else (loc[0] * 7.3 + loc[1] * 3.1))
    t = vs[variant % len(vs)] if variant is not None else r.choice(vs)
    o = t.copy(); bpy.context.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (0, 0, rot_z); o.scale = (scale,) * 3; o.hide_render = False
    return o


def scatter(aid, region, n, zfn=lambda x, y: 0.0, scale=(0.8, 1.3), seed=1, avoid=None, res="1k"):
    """scatter n linked copies over region=(x0,x1,y0,y1); avoid(x,y)->True skips"""
    r = random.Random(seed); out = []
    for i in range(n * 3):
        if len(out) >= n: break
        x, y = r.uniform(region[0], region[1]), r.uniform(region[2], region[3])
        if avoid and avoid(x, y): continue
        out.append(place(aid, (x, y, zfn(x, y)), r.uniform(*scale), r.uniform(0, 6.283), res))
    return out


def brighten(objs, value=1.6, sat=1.15, hue=0.5, translucent=0.25):
    """lift dark scanned foliage materials: HSV on the colour texture + a bit of translucency"""
    seen = set()
    for o in objs:
        for m in o.data.materials:
            if m is None or m.name in seen or not m.use_nodes: continue
            seen.add(m.name); N, L = m.node_tree.nodes, m.node_tree.links
            b = next((n for n in N if n.type == "BSDF_PRINCIPLED"), None)
            if b is None: continue
            src = b.inputs["Base Color"].links[0].from_socket if b.inputs["Base Color"].links else None
            hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Value"].default_value = value; hs.inputs["Saturation"].default_value = sat; hs.inputs["Hue"].default_value = hue
            if src: L.new(src, hs.inputs["Color"])
            else: hs.inputs["Color"].default_value = b.inputs["Base Color"].default_value
            L.new(hs.outputs["Color"], b.inputs["Base Color"])
            for ln in list(b.inputs["Metallic"].links): L.remove(ln)       # scanned foliage is never metal
            b.inputs["Metallic"].default_value = 0.0
            try: b.inputs["Transmission Weight"].default_value = translucent * 0.0; b.inputs["Subsurface Weight"].default_value = translucent
            except Exception: pass


def grass_field(ground, aid="grass_medium_01", count=6000, region=None, size=1.0, res="1k"):
    """real grass clumps (all variants) instanced by a hair particle system on `ground`"""
    vs = model(aid, res); brighten(vs, 2.6, 1.45, 0.47)
    coll = bpy.data.collections["lib_" + aid]
    ps = ground.modifiers.new("grass3d", "PARTICLE_SYSTEM").particle_system.settings
    ps.type = "HAIR"; ps.count = count; ps.hair_length = 1.0; ps.render_type = "COLLECTION"; ps.instance_collection = coll; ps.use_collection_pick_random = True
    ps.particle_size = size; ps.size_random = 0.5; ps.use_rotations = True; ps.rotation_mode = "NOR"; ps.phase_factor_random = 2.0
    ps.use_advanced_hair = True
    if region:
        vg = ground.vertex_groups.new(name="g3d")
        for v in ground.data.vertices: vg.add([v.index], 1.0 if region(v.co) else 0.0, "REPLACE")
        ground.particle_systems[-1].vertex_group_density = "g3d"
