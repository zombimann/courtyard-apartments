"""
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", ".."))
render_6_hero_shots_v2.py  —  Photorealistic upgrade
Run:  blender.exe -b "Courtyard Apartments 50x100 v3.blend" --python render_6_hero_shots_v2.py
"""
import bpy, math, os
from mathutils import Vector

scene = bpy.context.scene
scene.frame_set(1)
outdir = _os.path.join(_PROJ, r"render/hero")
os.makedirs(outdir, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
#  1.  HIDE ANNOTATION / COMPLIANCE OBJECTS FROM RENDER
# ═══════════════════════════════════════════════════════════════════
annotation_keywords = ['CONFLICT', 'Annotation', 'conflict', 'annotation',
                       'Walkthrough_Path', 'CarDescent_Path',
                       'Camera_Walkthrough', 'Camera_CarDescent',
                       'Camera_01_', 'Camera_02_', 'Camera_03_',
                       'Camera_04_', 'Camera_05_', 'Camera_06_',
                       'Camera_07_', 'Camera_08_']
for obj in bpy.data.objects:
    for kw in annotation_keywords:
        if kw in obj.name:
            obj.hide_render = True
            break

# Also hide the Annotations collection from render
ann_col = bpy.data.collections.get('Annotations')
if ann_col:
    ann_col.hide_render = True

print("Annotation objects hidden from render.")

# ═══════════════════════════════════════════════════════════════════
#  2.  UPGRADE ALL MATERIALS TO PRINCIPLED BSDF
# ═══════════════════════════════════════════════════════════════════
def get_principled(mat):
    """Return (or create) the Principled BSDF node in a material."""
    if not mat.use_nodes:
        mat.use_nodes = True
    nt = mat.node_tree
    for n in nt.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            return n
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    out  = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if out:
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return bsdf

def set_mat(mat, base_color, roughness=0.85, metallic=0.0,
            specular=0.1, ior=1.45, transmission=0.0, alpha=1.0):
    bsdf = get_principled(mat)
    bsdf.inputs['Base Color'].default_value   = (*base_color, 1.0)
    bsdf.inputs['Roughness'].default_value    = roughness
    bsdf.inputs['Metallic'].default_value     = metallic
    # Blender 5.2 uses 'Specular IOR Level' instead of 'Specular'
    spec_input = bsdf.inputs.get('Specular IOR Level') or bsdf.inputs.get('Specular')
    if spec_input:
        spec_input.default_value = specular
    bsdf.inputs['IOR'].default_value          = ior
    trans = bsdf.inputs.get('Transmission Weight') or bsdf.inputs.get('Transmission')
    if trans:
        trans.default_value = transmission
    if transmission > 0:
        mat.blend_method = 'BLEND'
    alpha_in = bsdf.inputs.get('Alpha')
    if alpha_in:
        alpha_in.default_value = alpha

# Palette
CONCRETE      = (0.72, 0.71, 0.68)   # warm grey RC
BRICK_TERRA   = (0.72, 0.42, 0.28)   # terracotta brick
TIMBER_WARM   = (0.62, 0.42, 0.22)   # warm timber fins / pergola
TIMBER_LIGHT  = (0.78, 0.60, 0.35)   # light timber decking
GLASS_TINT    = (0.55, 0.72, 0.82)   # blue-grey glazing
STEEL_DARK    = (0.40, 0.40, 0.42)   # dark galvanised steel railings
STEEL_LIGHT   = (0.70, 0.72, 0.75)   # light aluminium
LAWN_GREEN    = (0.18, 0.42, 0.15)   # courtyard lawn
PLANTER_EARTH = (0.25, 0.18, 0.12)   # planter soil
DARK_GREY     = (0.12, 0.12, 0.14)   # dark soffit / shadow
WHITE_RENDER  = (0.92, 0.92, 0.90)   # rendered concrete floor / soffit
CANOPY_GREEN  = (0.12, 0.35, 0.10)   # tree canopy

# Keyword → (rgb, roughness, metallic, specular, ior, transmission)
MAT_MAP = {
    # Structural RC
    'Concrete':        (CONCRETE,     0.88, 0.0, 0.04, 1.45, 0.0),
    'RC_':             (CONCRETE,     0.88, 0.0, 0.04, 1.45, 0.0),
    'Wall':            (CONCRETE,     0.88, 0.0, 0.04, 1.45, 0.0),
    'Retaining':       (CONCRETE,     0.90, 0.0, 0.03, 1.45, 0.0),
    'Slab':            (WHITE_RENDER, 0.86, 0.0, 0.05, 1.45, 0.0),
    'Column':          (CONCRETE,     0.85, 0.0, 0.05, 1.45, 0.0),
    'Beam':            (CONCRETE,     0.85, 0.0, 0.04, 1.45, 0.0),
    'Foundation':      (CONCRETE,     0.92, 0.0, 0.02, 1.45, 0.0),
    'Floor_Concrete':  (CONCRETE,     0.82, 0.0, 0.08, 1.45, 0.0),
    # Masonry / finish
    'Brick':           (BRICK_TERRA,  0.90, 0.0, 0.03, 1.45, 0.0),
    'Masonry':         (BRICK_TERRA,  0.90, 0.0, 0.03, 1.45, 0.0),
    'Parapet':         (CONCRETE,     0.88, 0.0, 0.04, 1.45, 0.0),
    # Timber
    'Timber':          (TIMBER_WARM,  0.70, 0.0, 0.04, 1.50, 0.0),
    'Fin':             (TIMBER_WARM,  0.68, 0.0, 0.05, 1.50, 0.0),
    'Pergola':         (TIMBER_WARM,  0.72, 0.0, 0.04, 1.50, 0.0),
    'Louvre':          (TIMBER_WARM,  0.70, 0.0, 0.04, 1.50, 0.0),
    'Decking':         (TIMBER_LIGHT, 0.75, 0.0, 0.04, 1.50, 0.0),
    'Roof_Deck':       (TIMBER_LIGHT, 0.75, 0.0, 0.04, 1.50, 0.0),
    # Glazing
    'Glaze':           (GLASS_TINT,   0.05, 0.0, 0.50, 1.52, 0.92),
    'Glass':           (GLASS_TINT,   0.05, 0.0, 0.50, 1.52, 0.92),
    'Window':          (GLASS_TINT,   0.05, 0.0, 0.50, 1.52, 0.92),
    # Metal
    'Balustrade':      (STEEL_DARK,   0.35, 0.85, 0.60, 1.45, 0.0),
    'Railing':         (STEEL_DARK,   0.35, 0.85, 0.60, 1.45, 0.0),
    'Barrier':         (STEEL_DARK,   0.40, 0.80, 0.55, 1.45, 0.0),
    'Guard':           (STEEL_DARK,   0.40, 0.80, 0.55, 1.45, 0.0),
    'Metal':           (STEEL_DARK,   0.38, 0.82, 0.58, 1.45, 0.0),
    'Steel':           (STEEL_LIGHT,  0.30, 0.90, 0.65, 1.45, 0.0),
    'Aluminium':       (STEEL_LIGHT,  0.28, 0.92, 0.70, 1.45, 0.0),
    'Gate':            (STEEL_DARK,   0.45, 0.75, 0.50, 1.45, 0.0),
    'Solar':           (DARK_GREY,    0.20, 0.10, 0.55, 1.45, 0.0),
    # Landscape
    'Lawn':            (LAWN_GREEN,   1.00, 0.0, 0.02, 1.45, 0.0),
    'Grass':           (LAWN_GREEN,   1.00, 0.0, 0.02, 1.45, 0.0),
    'Garden':          (LAWN_GREEN,   1.00, 0.0, 0.02, 1.45, 0.0),
    'Planter':         (PLANTER_EARTH,0.95, 0.0, 0.02, 1.45, 0.0),
    'Tree':            (CANOPY_GREEN, 0.95, 0.0, 0.02, 1.45, 0.0),
    'Stem':            (TIMBER_WARM,  0.80, 0.0, 0.03, 1.50, 0.0),
}

upgraded = 0
for mat in bpy.data.materials:
    for keyword, params in MAT_MAP.items():
        if keyword.lower() in mat.name.lower():
            set_mat(mat, *params)
            upgraded += 1
            break

print(f"Upgraded {upgraded} materials to Principled BSDF.")

# ═══════════════════════════════════════════════════════════════════
#  3.  PHOTOREALISTIC EEVEE SETTINGS
# ═══════════════════════════════════════════════════════════════════
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 64
scene.eevee.use_shadows        = True
scene.eevee.use_raytracing     = True

def safe_set(obj, attr, val):
    try: setattr(obj, attr, val)
    except Exception as e: print(f"  [skip] {attr}: {e}")

safe_set(scene.eevee, 'ray_tracing_method',       'SCREEN')
safe_set(scene.eevee, 'use_fast_gi',              True)
safe_set(scene.eevee, 'fast_gi_method',           'GLOBAL_ILLUMINATION')
safe_set(scene.eevee, 'fast_gi_quality',          1.0)
safe_set(scene.eevee, 'fast_gi_ray_count',        4)
safe_set(scene.eevee, 'fast_gi_resolution',       '4')
safe_set(scene.eevee, 'fast_gi_step_count',       16)
safe_set(scene.eevee, 'fast_gi_bias',             0.03)
safe_set(scene.eevee, 'shadow_resolution_scale',  2.0)
safe_set(scene.eevee, 'shadow_ray_count',         2)
safe_set(scene.eevee, 'shadow_step_count',        8)
safe_set(scene.eevee, 'direct_light_intensity',   1.0)
safe_set(scene.eevee, 'indirect_light_intensity', 1.0)

rt = getattr(scene.eevee, 'ray_tracing_options', None)
if rt:
    safe_set(rt, 'resolution',             'FULL')
    safe_set(rt, 'use_denoise',            True)
    safe_set(rt, 'screen_trace_quality',   0.95)
    safe_set(rt, 'screen_trace_thickness', 0.2)

scene.render.resolution_x               = 1920
scene.render.resolution_y               = 1080
scene.render.resolution_percentage      = 100
scene.render.image_settings.file_format = 'PNG'

print("EEVEE 5.2: FastGI=ON, Raytracing(SCREEN)=ON, 64 samples.")

# ═══════════════════════════════════════════════════════════════════
#  4.  NISHITA ATMOSPHERIC SKY (golden-hour Nairobi ~4 PM)
# ═══════════════════════════════════════════════════════════════════
world = scene.world
if not world:
    world = bpy.data.worlds.new('World')
    scene.world = world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()

try:
    sky_node = nt.nodes.new('ShaderNodeTexSky')
    # Blender 5.2 sky types: SINGLE_SCATTERING, MULTIPLE_SCATTERING, PREETHAM, HOSEK_WILKIE
    # HOSEK_WILKIE is the physically-based Nairobi sky model available in 5.2
    sky_node.sky_type      = 'HOSEK_WILKIE'
    sky_node.sun_elevation = math.radians(28)   # ~4pm afternoon angle
    sky_node.sun_rotation  = math.radians(248)  # from WSW direction
    safe_set(sky_node, 'air_density',   1.0)
    safe_set(sky_node, 'dust_density',  0.6)    # slight afternoon haze
    sky_used = True
    print("Sky: HOSEK_WILKIE atmospheric sky loaded.")
except Exception as e:
    sky_node = None
    sky_used = False
    print(f"Sky node failed ({e}), using flat colour fallback.")

bg_node  = nt.nodes.new('ShaderNodeBackground')
out_node = nt.nodes.new('ShaderNodeOutputWorld')

if sky_node:
    bg_node.inputs['Strength'].default_value = 0.55
    nt.links.new(sky_node.outputs['Color'], bg_node.inputs['Color'])
else:
    # Warm golden-hour flat fallback
    bg_node.inputs['Color'].default_value   = (0.70, 0.78, 1.00, 1.0)
    bg_node.inputs['Strength'].default_value = 1.8

nt.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])
print("World sky configured.")

# ═══════════════════════════════════════════════════════════════════
#  5.  SUN LIGHT — warm golden afternoon
# ═══════════════════════════════════════════════════════════════════
sun = bpy.data.objects.get('Sun_Nairobi')
if sun:
    sun.data.energy       = 8.0
    sun.data.color        = (1.0, 0.90, 0.72)   # warm golden afternoon
    sun.data.angle        = math.radians(0.53)   # realistic solar disc size
    sun.rotation_euler    = (math.radians(62), 0, math.radians(-248 + 90))

sky_fill = bpy.data.objects.get('Sky_Fill')
if sky_fill:
    sky_fill.data.energy  = 0.0   # Let Nishita sky handle ambient

print("Sun: 8W, golden warm, aligned with Nishita sky direction.")

# ═══════════════════════════════════════════════════════════════════
#  6.  CAMERA FACTORY
# ═══════════════════════════════════════════════════════════════════
def make_cam(name, loc, target, lens=35, clip_end=500, sensor=36):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
    cd = bpy.data.cameras.new(name)
    cd.lens          = lens
    cd.sensor_width  = sensor
    cd.clip_start    = 0.1
    cd.clip_end      = clip_end
    cam_obj = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = loc
    cam_obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z','Y').to_euler()
    return cam_obj

# ═══════════════════════════════════════════════════════════════════
#  7.  6 HERO CAMERA COMPOSITIONS
# ═══════════════════════════════════════════════════════════════════
shots = [

    # ── SHOT 1: COURTYARD GARDEN ─────────────────────────────────
    # Camera is at the colonnade edge, looking diagonally ACROSS the courtyard.
    # Tree is a framing element on the right; left wing balconies recede into depth;
    # open sky fills the upper frame. Classic "living room to courtyard" drama.
    ("Prod_01_Courtyard_Garden",
     (5.20, 9.00, 2.50),    # On colonnade edge, GF eye height
     (12.50, 20.00, 7.00),  # Looking diagonally across to far upper balconies
     24),

    # ── SHOT 2: COURTYARD BIRD'S EYE ─────────────────────────────
    # Directly above the courtyard centre, angled 10° from vertical so the
    # balcony depth reads. Shows full 4-storey void, garden, tree shadow.
    ("Prod_02_Courtyard_BirdsEye",
     (7.00, 11.00, 23.00),  # High and slightly to the left/south of centre
     (10.50, 15.50, 0.90),  # Looking toward garden centre at podium level
     20),

    # ── SHOT 3: STREET FACADE ────────────────────────────────────
    # Wide 3/4 exterior: full building height visible, car portal & pedestrian
    # gate at base, timber brise-soleil fins in strong afternoon raking light.
    ("Prod_03_Street_Facade",
     (-8.00, -15.00, 8.50),  # Across the road, 8.5m height (~2nd floor level of adjacent)
     (7.62, 1.00, 8.00),     # Aimed at mid-height of the facade, centred
     35),

    # ── SHOT 4: LIVING ROOM INTERIOR ─────────────────────────────
    # Inside the left-wing L1 living room, standing at rear wall looking toward
    # the 3.5m courtyard glazing. Courtyard garden & opposite wing glow through.
    ("Prod_04_LivingRoom_L1",
     (2.80, 14.00, 5.80),    # Back of left-wing living room at L1 (FFL=4.20+1.60 eye)
     (8.50, 13.00, 5.20),    # Looking through the glazed wall to courtyard
     28),

    # ── SHOT 5: BALCONY OVERLOOK (L3) ────────────────────────────
    # Standing at the far edge of a cantilevered L3 right-wing balcony.
    # Balustrade in the foreground, courtyard void opens up below and across.
    # Opposite wing glazing and planters visible.
    ("Prod_05_Balcony_L3_Overlook",
     (13.60, 16.00, 11.80),  # Right-wing L3 balcony tip
     (4.50, 13.00, 4.00),    # Down and across to garden level on left wing
     24),

    # ── SHOT 6: ROOF TERRACE — GOLDEN HOUR ───────────────────────
    # Standing under the timber pergola looking south across the roof garden.
    # Solar panels glint in low sun. Nairobi skyline beyond the parapet.
    # Pergola rafters frame the top, planters and seats visible.
    ("Prod_06_Roof_Pergola_Sunset",
     (4.00, 8.00, 17.80),    # Under pergola, north side of roof
     (12.00, 26.00, 16.80),  # Looking south-east across roof to horizon
     24),
]

# ═══════════════════════════════════════════════════════════════════
#  8.  RENDER ALL 6 SHOTS
# ═══════════════════════════════════════════════════════════════════
for name, loc, target, lens in shots:
    print(f"\n{'='*60}")
    print(f"  Rendering: {name}")
    print(f"  Camera: loc={[round(v,2) for v in loc]}, target={[round(v,2) for v in target]}, lens={lens}mm")
    print(f"{'='*60}")
    cam_obj = make_cam(name, loc, target, lens)
    scene.camera = cam_obj
    outpath = os.path.join(outdir, f"{name}.png")
    scene.render.filepath = outpath
    bpy.ops.render.render(write_still=True)
    size_kb = os.path.getsize(outpath) / 1024 if os.path.exists(outpath) else 0
    print(f"  -> {outpath}  ({size_kb:.0f} KB)")

print("\n\n=== ALL 6 HERO SHOTS COMPLETE ===")
for name, *_ in shots:
    p = os.path.join(outdir, f"{name}.png")
    status = f"{os.path.getsize(p)/1024:.0f} KB" if os.path.exists(p) else "MISSING"
    print(f"  {name}: {status}")
