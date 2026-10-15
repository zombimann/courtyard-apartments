"""
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", ".."))
render_6_hero_shots.py
Run with: blender.exe -b "Courtyard Apartments 50x100 v3.blend" --python render_6_hero_shots.py
Renders 6 production stills to render\hero\ at 1920x1080, EEVEE 32 samples.
"""
import bpy, math
from mathutils import Vector
import os

scene = bpy.context.scene
outdir = _os.path.join(_PROJ, r"render/hero")
os.makedirs(outdir, exist_ok=True)

# ── PRODUCTION RENDER SETTINGS ─────────────────────────────────────────
scene.render.engine = 'BLENDER_EEVEE'
scene.eevee.taa_render_samples = 32
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.frame_set(1)

# ── GOLDEN-HOUR NAIROBI LIGHTING ───────────────────────────────────────
sun = bpy.data.objects.get('Sun_Nairobi')
if sun:
    sun.data.energy = 6.5
    sun.data.color = (1.0, 0.91, 0.78)
    sun.rotation_euler = (math.radians(55), math.radians(15), math.radians(-25))

sky = bpy.data.objects.get('Sky_Fill')
if sky:
    sky.data.energy = 2.2
    sky.data.color = (0.60, 0.76, 1.0)

if scene.world and scene.world.node_tree:
    bg = scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value  = (0.42, 0.60, 0.88, 1.0)
        bg.inputs['Strength'].default_value = 2.4

# ── CAMERA FACTORY ─────────────────────────────────────────────────────
def make_or_get_cam(name, loc, target, lens=35):
    obj = bpy.data.objects.get(name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 0.1
    cam_data.clip_end = 600
    cam_obj = bpy.data.objects.new(name, cam_data)
    col = bpy.data.collections.get('Annotations') or scene.collection
    col.objects.link(cam_obj)
    cam_obj.location = loc
    direction = Vector(target) - Vector(loc)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam_obj

# ── 6 HERO SHOTS ───────────────────────────────────────────────────────
shots = [
    # (name, loc, target, lens)
    # 1. Courtyard garden: eye-level near the feature tree, looking UP through the open void
    #    See: tree canopy, staggered balconies rising on both wings, open sky above
    ("Prod_01_Courtyard_Garden",
        (7.50, 10.50, 2.50), (9.85, 16.00, 10.00), 24),

    # 2. Bird's-eye void: hovering dead-centre of courtyard, looking DOWN
    #    See: full garden, tree, colonnade arcade, ground-floor landscaping, all 4 balcony tiers
    ("Prod_02_Courtyard_BirdsEye",
        (9.85, 14.00, 24.00), (9.85, 14.50, 1.00), 20),

    # 3. Street façade: 3/4 perspective from the road, slight elevation
    #    See: full front elevation - fins, guardhouse, car portal, pedestrian gate, glazing
    ("Prod_03_Street_Facade",
        (-5.00, -14.00, 6.00), (7.62, 2.00, 7.00), 35),

    # 4. Living room interior: inside left-wing L1 living room, looking THROUGH glazing
    #    See: glazed wall, courtyard garden, feature tree, opposite balconies, sunlight
    ("Prod_04_LivingRoom_L1",
        (3.20, 12.00, 5.80), (10.50, 14.50, 4.80), 28),

    # 5. Balcony overlook: standing on a L3 right-wing cantilevered balcony
    #    See: metal balustrade foreground, courtyard void, opposite living-room glazing, garden below
    ("Prod_05_Balcony_L3_Overlook",
        (14.00, 13.00, 11.80), (4.50, 15.00, 5.50), 28),

    # 6. Roof terrace: under the timber pergola, golden-hour sky behind
    #    See: pergola rafters overhead, solar panels, planters, Nairobi sky, roofscape
    ("Prod_06_Roof_Pergola_Sunset",
        (5.00, 9.00, 17.80), (11.00, 22.00, 16.50), 24),
]

# ── RENDER EACH SHOT ───────────────────────────────────────────────────
for name, loc, target, lens in shots:
    print(f"\n=== Rendering: {name} ===")
    cam_obj = make_or_get_cam(name, loc, target, lens)
    scene.camera = cam_obj
    outpath = os.path.join(outdir, f"{name}.png")
    scene.render.filepath = outpath
    bpy.ops.render.render(write_still=True)
    size_kb = os.path.getsize(outpath) / 1024 if os.path.exists(outpath) else 0
    print(f"  -> Saved: {outpath} ({size_kb:.0f} KB)")

print("\n\n=== ALL 6 HERO SHOTS COMPLETE ===")
print(f"Output folder: {outdir}")
for name, *_ in shots:
    p = os.path.join(outdir, f"{name}.png")
    status = f"{os.path.getsize(p)/1024:.0f} KB" if os.path.exists(p) else "MISSING"
    print(f"  {name}: {status}")
