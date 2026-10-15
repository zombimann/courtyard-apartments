"""query_geometry.py - report exact world positions of the elements that matter
for camera composition: courtyard, tree, wings, colonnade, balconies, roof.
"""
import bpy
from mathutils import Vector

def bounds(objs):
    pts = []
    for o in objs:
        if o.type != 'MESH':
            continue
        for c in o.bound_box:
            pts.append(o.matrix_world @ Vector(c))
    if not pts:
        return None
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def show(label, objs_or_names):
    if isinstance(objs_or_names[0], str):
        objs = [bpy.data.objects[n] for n in objs_or_names if n in bpy.data.objects]
    else:
        objs = objs_or_names
    b = bounds(objs)
    if not b:
        print(f"  {label:36s} -- none --")
        return
    lo, hi = b
    print(f"  {label:36s} X[{lo.x:6.2f},{hi.x:6.2f}] Y[{lo.y:6.2f},{hi.y:6.2f}] Z[{lo.z:6.2f},{hi.z:6.2f}]"
          f"  ctr=({(lo.x+hi.x)/2:5.2f},{(lo.y+hi.y)/2:5.2f},{(lo.z+hi.z)/2:5.2f})")

def pref(prefix, coll=None):
    src = coll.objects if coll else bpy.data.objects
    return [o for o in src if o.name.startswith(prefix)]

print("\n" + "=" * 100)
print("  GEOMETRY QUERY")
print("=" * 100)

print("\n--- COLLECTION ENVELOPES ---")
for c in bpy.context.scene.collection.children:
    show(c.name, list(c.objects))

print("\n--- COURTYARD / GARDEN ---")
for p in ('GF_Courtyard', 'GF_Lawn_', 'GF_Tree_', 'GF_Path_', 'GF_Colonnade'):
    show(p + '*', pref(p))

print("\n--- CIRCULATION CORE ---")
for p in ('Core_',):
    show(p + '*', pref(p))

print("\n--- STREET FRONTAGE (Y min) ---")
for p in ('GF_Guard', 'GF_Gate', 'GF_Portal', 'GF_Pedestrian', 'GF_Entry', 'GF_Shop', 'GF_Access_Ramp', 'GF_Ramp'):
    show(p + '*', pref(p))

print("\n--- WINGS: sample L1 objects by X side ---")
l1 = [o for o in bpy.data.collections['L1_Floor'].objects if o.type == 'MESH']
left = [o for o in l1 if (o.matrix_world.translation.x) < 7.62]
right = [o for o in l1 if (o.matrix_world.translation.x) >= 7.62]
show('L1 left of x=7.62', left)
show('L1 right of x=7.62', right)
show('L1 ALL', l1)

print("\n--- BALCONIES (all levels) ---")
for lvl in ('L1', 'L2', 'L3', 'L4'):
    show(lvl + '_*Balc*', [o for o in bpy.data.objects if o.name.startswith(lvl) and 'Balc' in o.name])

print("\n--- GLAZING (all) ---")
show('*Glaz*/*Glass*/*Win*', [o for o in bpy.data.objects if any(k in o.name for k in ('Glaz', 'Glass')) ])

print("\n--- ROOF ---")
show('Roof ALL', list(bpy.data.collections['Roof'].objects))
for p in ('Roof_Pergola', 'Roof_Solar', 'Roof_Deck', 'Roof_Para', 'Roof_Garden', 'Roof_Planter', 'Roof_Stair'):
    show(p + '*', pref(p))

print("\n--- TIMBER FINS / BRISE-SOLEIL ---")
for p in ('GF_Fin', 'Fin_', 'L1_Fin', 'L2_Fin', 'L3_Fin', 'L4_Fin', 'Brise'):
    r = pref(p)
    if r:
        show(p + '*', r)

print("\n--- BASEMENT ---")
show('B1 ALL', list(bpy.data.collections['B1_Basement'].objects))

print("\n--- ANNOTATIONS (to hide) ---")
show('Annotations ALL', list(bpy.data.collections['Annotations'].objects))
for o in sorted(bpy.data.collections['Annotations'].objects, key=lambda o: o.name):
    print(f"    {o.name:44s} type={o.type} hide_render={o.hide_render}")

print("\n--- LIGHTS IN DETAIL ---")
for o in bpy.data.objects:
    if o.type == 'LIGHT':
        loc = o.matrix_world.translation
        e = o.rotation_euler
        print(f"  {o.name}: type={o.data.type} energy={o.data.energy} color={tuple(round(c,3) for c in o.data.color)}")
        print(f"      loc=({loc.x:.2f},{loc.y:.2f},{loc.z:.2f}) rot=({e.x:.3f},{e.y:.3f},{e.z:.3f}) rad")
        # sun direction
        d = o.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        print(f"      light travels toward ({d.x:.3f},{d.y:.3f},{d.z:.3f})  elevation={__import__('math').degrees(__import__('math').asin(max(-1,min(1,-d.z)))):.1f} deg")

print("\n--- SCENE ---")
sc = bpy.context.scene
print("  engine:", sc.render.engine)
print("  view_transform:", sc.view_settings.view_transform, "look:", sc.view_settings.look, "exposure:", sc.view_settings.exposure)
print("  world:", sc.world.name if sc.world else None, "use_nodes:", sc.world.use_nodes if sc.world else None)
print("  fps:", sc.render.fps, " frame range:", sc.frame_start, "-", sc.frame_end)
print("  units:", sc.unit_settings.system, "scale_length:", sc.unit_settings.scale_length)
bb = bpy.data.collections['B1_Basement'].objects
print("=" * 100 + "\n")
