"""diag_rays.py - what does each hero camera actually hit, and what materials
are the furniture / wall objects using?"""
import bpy, math
from mathutils import Vector

dg = bpy.context.evaluated_depsgraph_get()
scene = bpy.context.scene

SHOTS = {
    '01': ((11.60, 7.45, 2.30), (9.00, 20.00, 5.60)),
    '03': ((13.50, -30.00, 3.60), (7.00, 0.00, 8.80)),
    '04': ((2.85, 8.20, 11.85), (10.50, 14.50, 9.60)),
    '05': ((7.40, 9.80, 11.75), (10.50, 19.00, 4.50)),
    '06': ((4.60, 17.20, 17.75), (1.40, 4.50, 16.40)),
}

print("\n" + "=" * 100)
print("  RAY DIAGNOSTIC")
print("=" * 100)

for tag, (loc, tgt) in SHOTS.items():
    o = Vector(loc)
    d = (Vector(tgt) - o).normalized()
    print(f"\n--- shot {tag}  from {loc} toward {tgt} ---")
    cur = o
    for step in range(6):
        hit, hloc, hnor, idx, obj, mw = scene.ray_cast(dg, cur, d)
        if not hit:
            print(f"   {step}: no hit (sky)")
            break
        dist_total = (hloc - o).length
        mat = obj.data.materials[0].name if (obj.type == 'MESH' and obj.data.materials) else '-'
        print(f"   {step}: {obj.name:44s} mat={mat:22s} at {dist_total:7.2f} m  z={hloc.z:6.2f}")
        cur = hloc + d * 0.02
        if dist_total > 120:
            break

print("\n\n--- MATERIALS ON FURNITURE (are the blocks dressed properly?) ---")
keys = ('Sofa', 'Bed', 'DiningTable', 'Kitchen_Counter', 'Counter', 'Desk', 'Table', 'Chair')
seen = {}
for ob in bpy.data.objects:
    if ob.type != 'MESH':
        continue
    if any(k in ob.name for k in keys):
        mats = tuple(m.name for m in ob.data.materials if m)
        seen.setdefault(mats, []).append(ob.name)
for mats, names in sorted(seen.items(), key=lambda kv: -len(kv[1])):
    print(f"   {str(mats):34s} x{len(names):3d}  e.g. {names[0]}")

print("\n--- MATERIALS ON WINDOW / GLAZING OBJECTS ---")
gseen = {}
for ob in bpy.data.objects:
    if ob.type != 'MESH':
        continue
    if 'Glaz' in ob.name or 'Glass' in ob.name:
        gseen.setdefault(tuple(m.name for m in ob.data.materials if m), []).append(ob.name)
for mats, names in sorted(gseen.items(), key=lambda kv: -len(kv[1])):
    print(f"   {str(mats):34s} x{len(names):3d}  e.g. {names[0]}")

print("\n--- IS THE L3 COURTYARD WALL SOLID? (mesh stats) ---")
for nm in ('L3_2BedL_Courtyard_Wall', 'L3_2BedL_Living_Glaze',
           'L2_2BedL_Courtyard_Wall', 'GF_Colonnade_Floor'):
    ob = bpy.data.objects.get(nm)
    if ob and ob.type == 'MESH':
        me = ob.data
        print(f"   {nm:34s} verts={len(me.vertices):5d} polys={len(me.polygons):5d} "
              f"mats={[m.name for m in me.materials if m]}")

print("\n--- ALL MATERIALS USED BY L3 OBJECTS ---")
mats = {}
for ob in bpy.data.collections['L3_Floor'].objects:
    if ob.type == 'MESH':
        for m in ob.data.materials:
            if m:
                mats[m.name] = mats.get(m.name, 0) + 1
for k, v in sorted(mats.items(), key=lambda kv: -kv[1]):
    print(f"   {k:28s} {v}")
print("=" * 100 + "\n")
