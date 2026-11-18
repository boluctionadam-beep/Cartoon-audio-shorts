"""Shot: Bogis at the foot of the castle wall, looking up at the garderobe (toilet box) sticking out of the wall.
Low angle, golden hour. 2D character card in a stylised 3D world (Cycles).
Usage: python3 shot_bogis_looks_up.py OUT.png [W H SAMPLES]"""
import bpy, math, sys, os, random
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
OUT = os.path.abspath(args[0]) if args else os.path.join(HERE, "../renders/shot.png")
W, H, SPP = (int(args[1]), int(args[2]), int(args[3])) if len(args) >= 4 else (1440, 2560, 128)
CARD = os.path.join(HERE, "../renders/bogis_card.png")
random.seed(4)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- materials
def nodes(m):
    m.use_nodes = True; return m.node_tree.nodes, m.node_tree.links

def mat_stone(name, base=(0.64, 0.59, 0.50), scale=1.6):
    m = bpy.data.materials.new(name); N, L = nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale); mp.inputs["Rotation"].default_value = (math.radians(90), 0, 0)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    br = N.new("ShaderNodeTexBrick"); br.inputs["Scale"].default_value = 1.0
    br.inputs["Mortar Size"].default_value = 0.018; br.inputs["Mortar Smooth"].default_value = 0.3
    br.inputs["Brick Width"].default_value = 1.1; br.inputs["Row Height"].default_value = 0.55
    br.offset = 0.5; br.squash = 1.0
    br.inputs["Color1"].default_value = (*base, 1); br.inputs["Color2"].default_value = (base[0] * .72, base[1] * .70, base[2] * .68, 1)
    br.inputs["Mortar"].default_value = (base[0] * .55, base[1] * .5, base[2] * .45, 1)
    L.new(mp.outputs["Vector"], br.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.8; nz.inputs["Detail"].default_value = 6; nz.inputs["Roughness"].default_value = 0.6
    L.new(mp.outputs["Vector"], nz.inputs["Vector"])
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"; mix.inputs["Factor"].default_value = 0.55
    L.new(br.outputs["Color"], mix.inputs[6]); L.new(nz.outputs["Color"], mix.inputs[7])
    # dirt toward the ground
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -4; mr.inputs["From Max"].default_value = 3
    mr.inputs["To Min"].default_value = 0.55; mr.inputs["To Max"].default_value = 1.0
    L.new(sep.outputs["Z"], mr.inputs["Value"])
    dm = N.new("ShaderNodeMix"); dm.data_type = "RGBA"; dm.blend_type = "MULTIPLY"; dm.inputs["Factor"].default_value = 1.0
    L.new(mix.outputs[2], dm.inputs[6]); L.new(mr.outputs["Result"], dm.inputs[7])
    L.new(dm.outputs[2], b.inputs["Base Color"])
    bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35
    L.new(br.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.9
    return m

def mat_flat(name, col, rough=0.8, emit=0.0):
    m = bpy.data.materials.new(name); N, L = nodes(m); b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*col, 1); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*col, 1); b.inputs["Emission Strength"].default_value = emit
    return m

def mat_grass():
    m = bpy.data.materials.new("grass"); N, L = nodes(m); b = N["Principled BSDF"]
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.6
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.10, 0.30, 0.05, 1); cr.color_ramp.elements[1].color = (0.36, 0.55, 0.12, 1)
    L.new(nz.outputs["Fac"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    return m

def mat_blade():
    m = bpy.data.materials.new("blade"); N, L = nodes(m); b = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.06, 0.22, 0.04, 1); cr.color_ramp.elements[1].color = (0.50, 0.70, 0.18, 1)
    L.new(sep.outputs["Z"], cr.inputs["Fac"]); L.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.6; b.inputs["Subsurface Weight"].default_value = 0.0
    return m

def mat_stain():
    """brown streak running down the wall under the toilet (the joke)"""
    m = bpy.data.materials.new("stain"); N, L = nodes(m); b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.20, 0.13, 0.05, 1); b.inputs["Roughness"].default_value = 0.4
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sep.inputs[0])
    # alpha: strong at top, fading down, soft edges left/right, wavy
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 4; L.new(tc.outputs["UV"], nz.inputs["Vector"])
    gx = N.new("ShaderNodeMath"); gx.operation = "SUBTRACT"; gx.inputs[1].default_value = 0.5; L.new(sep.outputs["X"], gx.inputs[0])
    ax = N.new("ShaderNodeMath"); ax.operation = "ABSOLUTE"; L.new(gx.outputs[0], ax.inputs[0])
    wv = N.new("ShaderNodeMath"); wv.operation = "MULTIPLY_ADD"; wv.inputs[1].default_value = 0.25; L.new(nz.outputs["Fac"], wv.inputs[0]); L.new(ax.outputs[0], wv.inputs[2])
    ex = N.new("ShaderNodeMapRange"); ex.inputs["From Min"].default_value = 0.30; ex.inputs["From Max"].default_value = 0.42
    ex.inputs["To Min"].default_value = 1; ex.inputs["To Max"].default_value = 0; L.new(wv.outputs[0], ex.inputs["Value"])
    ey = N.new("ShaderNodeMapRange"); ey.inputs["From Min"].default_value = 0.0; ey.inputs["From Max"].default_value = 1.0
    ey.inputs["To Min"].default_value = 0.0; ey.inputs["To Max"].default_value = 0.85; L.new(sep.outputs["Y"], ey.inputs["Value"])
    a = N.new("ShaderNodeMath"); a.operation = "MULTIPLY"; L.new(ex.outputs["Result"], a.inputs[0]); L.new(ey.outputs["Result"], a.inputs[1])
    L.new(a.outputs[0], b.inputs["Alpha"])
    return m

def mat_card(path):
    m = bpy.data.materials.new("card"); N, L = nodes(m); b = N["Principled BSDF"]
    tex = N.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(path); tex.interpolation = "Cubic"
    L.new(tex.outputs["Color"], b.inputs["Base Color"]); L.new(tex.outputs["Alpha"], b.inputs["Alpha"])
    L.new(tex.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 0.45
    b.inputs["Roughness"].default_value = 1.0; b.inputs["Specular IOR Level"].default_value = 0.0
    return m

def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); bpy.ops.object.transform_apply(scale=True)
    if bevel:
        bv = o.modifiers.new("bv", "BEVEL"); bv.width = bevel; bv.segments = 2
    o.data.materials.append(mat); return o

STONE = mat_stone("stone", scale=0.62); STONE_D = mat_stone("stone_dark", base=(0.56, 0.49, 0.39), scale=1.5)
DARK = mat_flat("hole", (0.02, 0.015, 0.01), 1.0)
RED = mat_flat("banner", (0.62, 0.05, 0.05), 0.7); GOLDM = mat_flat("gold", (0.85, 0.62, 0.12), 0.4)
WOODM = mat_flat("roofslate", (0.16, 0.18, 0.24), 0.6)

# ---------------------------------------------------------------- world geometry (y+ = away from camera)
WALL_Y = 4.0
box("wall", (0, WALL_Y + 1.5, 6), (40, 3, 16), STONE, 0.05)
for i in range(-10, 11):                                                     # merlons
    box(f"merlon{i}", (i * 2.0, WALL_Y + 0.4, 14.6), (1.2, 0.9, 1.3), STONE, 0.04)
# battered (sloped) base of the wall, like Gaillard's talus
bpy.ops.mesh.primitive_cube_add(location=(0, WALL_Y - 0.2, 0.9)); tb = bpy.context.object; tb.scale = (20, 1.0, 1.4)
bpy.ops.object.transform_apply(scale=True)
for v in tb.data.vertices:
    if v.co.z > 1.5 and v.co.y < WALL_Y: v.co.y += 1.4
tb.data.materials.append(STONE_D)

# the garderobe: a stone box corbelled out of the wall, high up, right of frame
GX, GZ = 2.2, 8.6
gy = WALL_Y - 0.9
box("garderobe", (GX, gy, GZ), (2.2, 1.8, 2.6), STONE_D, 0.06)
for dx in (-0.85, 0.85):                                                     # two stepped corbels
    box(f"corbel{dx}", (GX + dx, gy + 0.25, GZ - 1.5), (0.5, 1.3, 0.4), STONE_D, 0.03)
    box(f"corbel2{dx}", (GX + dx, gy + 0.55, GZ - 1.85), (0.5, 0.7, 0.32), STONE_D, 0.03)
# little slate/wood pent roof
bpy.ops.mesh.primitive_cube_add(location=(GX, gy - 0.1, GZ + 1.55)); r = bpy.context.object
r.scale = (1.25, 1.05, 0.09); r.rotation_euler.x = math.radians(-20); r.location.z += 0.1; r.data.materials.append(WOODM)
# tiny window slit
box("slit", (GX + 0.5, gy - 0.91, GZ + 0.3), (0.16, 0.05, 0.6), DARK)
# the hole in the bottom (dark opening) - visible from below
box("hole", (GX - 0.2, gy - 0.25, GZ - 1.31), (0.7, 0.6, 0.04), DARK)
# brown streak down the wall
bpy.ops.mesh.primitive_plane_add(size=1, location=(GX - 0.2, WALL_Y - 0.02, (GZ - 1.3) / 2 + 0.6)); s = bpy.context.object
s.scale = (0.9, (GZ - 1.3) - 0.8, 1); s.rotation_euler.x = math.radians(90); s.data.materials.append(mat_stain())

# banner hanging from the wall top (left of the toilet)
bpy.ops.mesh.primitive_grid_add(x_subdivisions=20, y_subdivisions=40, size=1, location=(-3.4, WALL_Y - 0.12, 10.6)); bn = bpy.context.object
bn.scale = (1.5, 4.6, 1); bn.rotation_euler.x = math.radians(90); bn.data.materials.append(RED)
wave = bn.modifiers.new("w", "WAVE"); wave.height = 0.08; wave.width = 0.9; wave.use_y = False; wave.use_normal = True
bpy.ops.mesh.primitive_plane_add(size=1, location=(-3.4, WALL_Y - 0.2, 11.2)); g = bpy.context.object
g.scale = (0.6, 0.6, 1); g.rotation_euler = (math.radians(90), 0, math.radians(45)); g.data.materials.append(GOLDM)

# ground: grassy slope dropping toward the camera, with rocks
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0)); gr = bpy.context.object
gr.data.materials.append(mat_grass())
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.subdivide(number_cuts=40); bpy.ops.object.mode_set(mode="OBJECT")
for v in gr.data.vertices:
    v.co.z = 0.08 * math.sin(v.co.x * 0.7) * math.cos(v.co.y * 0.5)
RM = mat_flat("rock", (0.55, 0.52, 0.47), 0.9)
for i in range(18):
    x = random.choice([random.uniform(-7, -1.6), random.uniform(1.2, 7)]); y = random.uniform(-5, WALL_Y - 0.5)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.12, 0.45), location=(x, y, 0.0))
    rk = bpy.context.object; rk.scale = (1, random.uniform(.7, 1.2), random.uniform(.4, .7)); rk.data.materials.append(RM)

# grass clumps instanced by a particle system
bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.035, depth=0.38, location=(0, 0, -50)); blade = bpy.context.object
bpy.ops.object.transform_apply(location=False)
for v in blade.data.vertices: v.co.z += 0.19
blade.data.materials.append(mat_blade())
ps = gr.modifiers.new("grass", "PARTICLE_SYSTEM").particle_system.settings
ps.type = "HAIR"; ps.count = 60000; ps.hair_length = 1.0; ps.render_type = "OBJECT"; ps.instance_object = blade
ps.particle_size = 1.0; ps.size_random = 0.6; ps.use_rotations = True; ps.rotation_mode = "OB_Z"; ps.phase_factor_random = 2.0
ps.rotation_factor_random = 0.25; ps.use_advanced_hair = True
vg = gr.vertex_groups.new(name="dens")
for v in gr.data.vertices:
    w = 1.0 if (-6.6 < v.co.y < WALL_Y - 0.6 and abs(v.co.x) < 12) else 0.0
    vg.add([v.index], w, "REPLACE")
gr.particle_systems[0].vertex_group_density = "dens"


# stylised clouds far behind the wall
CL = mat_flat("cloud", (1.0, 0.93, 0.85), 1.0, emit=0.25)
for cx, cz, sc_ in ((-14, 34, 1.0), (6, 40, 1.4), (22, 31, 0.9), (-2, 28, 0.7)):
    for j in range(7):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=random.uniform(2.2, 3.6) * sc_,
            location=(cx + random.uniform(-5, 5) * sc_, 70 + random.uniform(-2, 2), cz + random.uniform(-1, 1.5) * sc_))
        o = bpy.context.object; o.scale.z = 0.6; o.data.materials.append(CL); bpy.ops.object.shade_smooth()
# two birds
for bx, bz in ((-3.5, 19.5), (-2.4, 20.6)):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(bx, 25, bz)); o = bpy.context.object
    o.scale = (0.5, 0.09, 1); o.rotation_euler = (math.radians(90), math.radians(18), 0); o.data.materials.append(DARK)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(bx + 0.45, 25, bz)); o = bpy.context.object
    o.scale = (0.5, 0.09, 1); o.rotation_euler = (math.radians(90), math.radians(-18), 0); o.data.materials.append(DARK)

# ---------------------------------------------------------------- character card
img = bpy.data.images.load(CARD); aspect = img.size[0] / img.size[1]
CH = 2.1                                                     # card height in metres
bpy.ops.mesh.primitive_plane_add(size=1, location=(-0.25, -4.5, CH / 2 - 0.1)); card = bpy.context.object
card.scale = (CH * aspect, CH, 1); card.rotation_euler.x = math.radians(90)
card.data.materials.append(mat_card(CARD))
bpy.ops.object.transform_apply(scale=True)

# ---------------------------------------------------------------- camera (low angle, looking up)
bpy.ops.object.camera_add(location=(0.05, -6.5, 0.8)); cam = bpy.context.object; sc.camera = cam
cam.rotation_euler = (math.radians(90 + 16), 0, math.radians(-3))
cam.data.lens = 15; cam.data.shift_y = 0.0; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 24
cam.data.dof.use_dof = True; cam.data.dof.focus_object = card; cam.data.dof.aperture_fstop = 1.0

# ---------------------------------------------------------------- light: golden hour from front-left
bpy.ops.object.light_add(type="SUN"); sun = bpy.context.object
sun.rotation_euler = Vector((0.92, 0.2, -0.36)).normalized().to_track_quat("-Z", "Y").to_euler()
sun.data.energy = 5.0; sun.data.color = (1.0, 0.80, 0.56); sun.data.angle = math.radians(2.5)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; WN, WL = w.node_tree.nodes, w.node_tree.links
sky = WN.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"
try:
    sky.sun_elevation = math.radians(14); sky.sun_rotation = math.radians(-128); sky.air_density = 1.4
except Exception as e:
    print("sky", e)
WL.new(sky.outputs["Color"], WN["Background"].inputs["Color"]); WN["Background"].inputs["Strength"].default_value = 0.16

# ---------------------------------------------------------------- render settings
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SPP
sc.cycles.use_denoising = True; sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.resolution_percentage = 100
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"; sc.view_settings.exposure = -0.3
sc.render.filepath = OUT; sc.render.image_settings.file_format = "PNG"
if not os.environ.get("PROBE"):
    bpy.ops.render.render(write_still=True)
    print("WROTE", OUT)
