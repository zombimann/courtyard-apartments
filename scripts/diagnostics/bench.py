"""bench.py - measure render speed for Cycles CPU vs EEVEE on this machine.
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", ".."))
Uses one representative courtyard camera and the existing lighting.
"""
import bpy, time, math, os
from mathutils import Vector

sc = bpy.context.scene
out = _os.path.join(_PROJ, r"render/_bench")
os.makedirs(out, exist_ok=True)

# representative camera: courtyard, eye level, looking at the tree + east wing
cd = bpy.data.cameras.new("BenchCam")
cd.lens = 24
cam = bpy.data.objects.new("BenchCam", cd)
sc.collection.objects.link(cam)
cam.location = (8.2, 6.5, 2.5)
cam.rotation_euler = (Vector((11.0, 17.0, 6.0)) - Vector((8.2, 6.5, 2.5))).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam

# hide annotations from render
for o in bpy.data.collections['Annotations'].objects:
    o.hide_render = True

sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'AgX'

def run(label, setup, res, samples_key):
    setup()
    sc.render.resolution_x, sc.render.resolution_y = res
    p = os.path.join(out, label + ".png")
    sc.render.filepath = p
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    print(f"BENCH {label}: {res[0]}x{res[1]} {dt:.1f}s  -> {p}")
    return dt

def eevee():
    sc.render.engine = 'BLENDER_EEVEE'
    sc.eevee.taa_render_samples = 64
    try:
        sc.eevee.use_raytracing = True
        sc.eevee.use_shadows = True
    except Exception as e:
        print("eevee opt:", e)

def cycles():
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 4
    try:
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.05
    except Exception as e:
        print("cycles opt:", e)

print("\n>>> BENCHSTART")
t_ee = run("eevee_1080p_64", eevee, (1920, 1080), 'taa_render_samples')
t_cy = run("cycles_720p_48", cycles, (1280, 720), 'samples')
print(f"\n>>> RESULT eevee1920x1080x64 = {t_ee:.1f}s  -> per-frame x6 = {t_ee*6/60:.1f} min")
print(f">>> RESULT cycles1280x720x48 = {t_cy:.1f}s  -> per-frame x6 = {t_cy*6/60:.1f} min")
print(f">>> RESULT cycles scaled to 1920x1080 = {t_cy*(1920*1080)/(1280*720):.1f}s -> x6 = {t_cy*(1920*1080)/(1280*720)*6/60:.1f} min")
print(">>> BENCHEND")
