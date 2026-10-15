"""inspect_scene.py - dump a factual inventory of the courtyard apartment scene.
Run: blender.exe -b "Courtyard Apartments 50x100 v3.blend" --python inspect_scene.py
"""
import bpy, sys
from mathutils import Vector

print("\n" + "=" * 78)
print("  BLENDER:", bpy.app.version_string)
print("  FILE   :", bpy.data.filepath)
print("  ENGINE :", bpy.context.scene.render.engine)
print("=" * 78)

# ---- Cycles / GPU devices ------------------------------------------------
try:
    addon = bpy.context.preferences.addons.get('cycles')
    if addon:
        prefs = addon.preferences
        prefs.get_devices()
        print("\n--- COMPUTE DEVICES ---")
        for d in prefs.devices:
            print(f"  [{d.type}] {d.name}  use={d.use}")
        print("  cycles.device =", prefs.compute_device_type)
except Exception as e:
    print("cycles prefs:", e)

# ---- Collections --------------------------------------------------------
print("\n--- COLLECTIONS ---")
def walk(coll, depth=0):
    print("  " * depth + f"* {coll.name}  (objs={len(coll.objects)}, hide_render={coll.hide_render})")
    for c in coll.children:
        walk(c, depth + 1)
walk(bpy.context.scene.collection)

# ---- Object inventory ---------------------------------------------------
objs = [o for o in bpy.data.objects]
print(f"\n--- OBJECTS: {len(objs)} total ---")
by_type = {}
for o in objs:
    by_type.setdefault(o.type, []).append(o)
for t, lst in sorted(by_type.items()):
    print(f"  {t:10s}: {len(lst)}")

# ---- World bounding box of all MESH objects ----------------------------
pts = []
for o in objs:
    if o.type != 'MESH':
        continue
    for c in o.bound_box:
        pts.append(o.matrix_world @ Vector(c))
if pts:
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    print("\n--- SCENE BOUNDS (all meshes, world space, metres) ---")
    print(f"  min = ({lo.x:8.3f}, {lo.y:8.3f}, {lo.z:8.3f})")
    print(f"  max = ({hi.x:8.3f}, {hi.y:8.3f}, {hi.z:8.3f})")
    print(f"  size= ({hi.x-lo.x:8.3f}, {hi.y-lo.y:8.3f}, {hi.z-lo.z:8.3f})")
    print(f"  centre = ({(lo.x+hi.x)/2:.3f}, {(lo.y+hi.y)/2:.3f}, {(lo.z+hi.z)/2:.3f})")

# ---- Named objects with location + bbox --------------------------------
print("\n--- NAMED OBJECTS (non-mesh + key meshes) ---")
for o in sorted(objs, key=lambda o: o.name):
    if o.type in ('LIGHT', 'CAMERA', 'EMPTY'):
        loc = o.matrix_world.translation
        extra = ""
        if o.type == 'LIGHT':
            extra = f" type={o.data.type} energy={o.data.energy:.2f}"
        if o.type == 'CAMERA':
            extra = f" lens={o.data.lens:.1f}mm"
        print(f"  {o.name:34s} loc=({loc.x:7.2f},{loc.y:7.2f},{loc.z:7.2f}){extra}")

# ---- Materials ----------------------------------------------------------
print(f"\n--- MATERIALS ({len(bpy.data.materials)}) ---")
for m in sorted(bpy.data.materials, key=lambda m: m.name):
    users = m.users
    print(f"  {m.name:44s} users={users}")

# ---- Mesh object detail (first 120, with bbox) -------------------------
print("\n--- MESH DETAIL ---")
print(f"  {'name':40s} {'minZ':>8s} {'maxZ':>8s} {'sizeX':>7s} {'sizeY':>7s}")
for o in sorted([o for o in objs if o.type == 'MESH'], key=lambda o: o.name):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    zmin = min(p.z for p in bb); zmax = max(p.z for p in bb)
    xs = max(p.x for p in bb) - min(p.x for p in bb)
    ys = max(p.y for p in bb) - min(p.y for p in bb)
    print(f"  {o.name[:40]:40s} {zmin:8.2f} {zmax:8.2f} {xs:7.2f} {ys:7.2f}")

print("\n--- RENDER SETTINGS ---")
r = bpy.context.scene.render
print(f"  res={r.resolution_x}x{r.resolution_y} @{r.resolution_percentage}%  view_transform={bpy.context.scene.view_settings.view_transform}")
print(f"  exposure={bpy.context.scene.view_settings.exposure}  look={bpy.context.scene.view_settings.look}")
print("=" * 78 + "\n")
