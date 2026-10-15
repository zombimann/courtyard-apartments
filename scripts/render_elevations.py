"""
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
render_elevations.py -- orthographic clay elevations for the drawing set.

Box projection could not do hidden-line removal, so the elevations are rendered
properly instead: Workbench engine, flat single-colour shading with an object
outline. Fast (seconds per view) and honest about what the model contains.

  blender.exe -b "<model>.blend" --python scripts\\render_elevations.py
"""
import bpy, math, os, sys
from mathutils import Vector

PROJ = _PROJ
OUT = os.path.join(PROJ, "docs", "drawings", "elevations")
os.makedirs(OUT, exist_ok=True)
SC = bpy.context.scene

HIDE = ('CONFLICT', 'Annotation', 'Label_', 'North_Arrow', 'Camera_', 'Prod_',
        'Walkthrough', 'Car_Descent', 'Swept_')

def log(m):
    print(f"[elev] {m}", flush=True)

# ---------------------------------------------------------------- scene prep
for o in bpy.data.objects:
    if any(h in o.name for h in HIDE) or o.type in ('FONT', 'CURVE', 'EMPTY'):
        o.hide_render = True
c = bpy.data.collections.get('Annotations')
if c:
    c.hide_render = True

r = SC.render
r.engine = 'BLENDER_WORKBENCH'
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGB'
r.film_transparent = False
SC.view_settings.view_transform = 'Standard'
SC.view_settings.look = 'None'
SC.view_settings.exposure = 0.0

sh = SC.display.shading
try:
    sh.light = 'FLAT'
    sh.color_type = 'SINGLE'
    sh.single_color = (1.0, 1.0, 1.0)
    sh.show_object_outline = True
    sh.object_outline_color = (0.06, 0.06, 0.07)
    sh.show_specular_highlight = False
    sh.show_cavity = False
    sh.show_shadows = False
    SC.display.render_aa = '8'
except Exception as e:
    log(f"shading setup issue: {e}")
try:
    SC.world.color = (1.0, 1.0, 1.0)
except Exception:
    pass

# ---------------------------------------------------------------- cameras
# view name -> (direction the camera looks along, up is +Z, ortho scale, aspect)
CX, CY = 7.62, 15.24
VIEWS = {
    'WEST':  ((CX, -60.0, 9.0), (CX, CY, 9.0), 36.0, (2600, 1500)),
    'EAST':  ((CX, 90.0, 9.0), (CX, CY, 9.0), 36.0, (2600, 1500)),
    'NORTH': ((CX - 60.0, CY, 9.0), (CX, CY, 9.0), 40.0, (2600, 1500)),
    'SOUTH': ((CX + 60.0, CY, 9.0), (CX, CY, 9.0), 40.0, (2600, 1500)),
}

for name, (loc, tgt, oscale, (rx, ry)) in VIEWS.items():
    old = bpy.data.objects.get('ElevCam_' + name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    cd = bpy.data.cameras.new('ElevCam_' + name)
    cd.type = 'ORTHO'
    cd.ortho_scale = oscale
    cd.clip_start = 0.05
    cd.clip_end = 400.0
    cam = bpy.data.objects.new('ElevCam_' + name, cd)
    SC.collection.objects.link(cam)
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    SC.camera = cam
    r.resolution_x, r.resolution_y = rx, ry
    p = os.path.join(OUT, f'elev_{name.lower()}.png')
    r.filepath = p
    bpy.ops.render.render(write_still=True)
    log(f"{name}: {p}  ({os.path.getsize(p)/1024:.0f} KB)")

log("done")
