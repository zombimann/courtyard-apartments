"""query2.py - remaining facts: annotations, lights, key livable-space objects."""
import bpy, math
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

def show(label, objs):
    b = bounds(objs)
    if not b:
        print(f"  {label:34s} -- none --")
        return
    lo, hi = b
    print(f"  {label:34s} X[{lo.x:6.2f},{hi.x:6.2f}] Y[{lo.y:6.2f},{hi.y:6.2f}] Z[{lo.z:6.2f},{hi.z:6.2f}]"
          f"  ctr=({(lo.x+hi.x)/2:5.2f},{(lo.y+hi.y)/2:5.2f},{(lo.z+hi.z)/2:5.2f})")

def pref(p):
    return [o for o in bpy.data.objects if o.name.startswith(p)]

print("\n" + "=" * 100)
print("  QUERY 2")
print("=" * 100)

print("\n--- ANNOTATION OBJECTS ---")
for o in sorted(bpy.data.collections['Annotations'].objects, key=lambda o: o.name):
    print(f"  {o.name:46s} {o.type:8s} hide_render={o.hide_render} hide_viewport={o.hide_viewport}")

print("\n--- LIGHTS ---")
for o in bpy.data.objects:
    if o.type == 'LIGHT':
        d = o.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        print(f"  {o.name}: {o.data.type} energy={o.data.energy} color={tuple(round(c,3) for c in o.data.color)} angle={o.data.angle:.4f}")
        print(f"      travels->({d.x:6.3f},{d.y:6.3f},{d.z:6.3f}) elevation={math.degrees(math.asin(max(-1,min(1,-d.z)))):6.1f}deg azimuth={math.degrees(math.atan2(d.y,d.x)):6.1f}deg")

print("\n--- VIEW / COLOR MANAGEMENT ---")
sc = bpy.context.scene
print("  view_transform:", sc.view_settings.view_transform)
print("  look:", sc.view_settings.look, " exposure:", sc.view_settings.exposure, " gamma:", sc.view_settings.gamma)
print("  world:", sc.world.name if sc.world else None, "use_nodes:", sc.world.use_nodes if sc.world else None)
if sc.world and sc.world.use_nodes:
    for n in sc.world.node_tree.nodes:
        print("    world node:", n.type, n.name)
print("  engine:", sc.render.engine, " res:", sc.render.resolution_x, "x", sc.render.resolution_y, "@", sc.render.resolution_percentage)
print("  film_transparent:", sc.render.film_transparent)
try:
    print("  eevee.taa_render_samples:", sc.eevee.taa_render_samples)
    print("  eevee.use_raytracing:", sc.eevee.use_raytracing)
    print("  eevee.use_shadows:", sc.eevee.use_shadows)
except Exception as e:
    print("  eevee attrs:", e)

print("\n--- ROOF SUB-PARTS ---")
for p in ('Roof_Pergola', 'Roof_Solar', 'Roof_Deck', 'Roof_Para', 'Roof_Garden', 'Roof_Planter',
          'Roof_Stair', 'Roof_Lift', 'Roof_Water', 'Roof_Tank', 'Roof_Seat', 'Roof_Lawn', 'Roof_Paver',
          'Roof_Soil', 'Roof_Rail', 'Roof_Screen', 'Roof_Planter'):
    r = pref(p)
    if r:
        show(p + '*', r)

print("\n--- RESIDENTIAL / LIVING SPACES per level (sample) ---")
for lvl in ('L1', 'L2', 'L3', 'L4'):
    for kind in ('Living', 'Bed', 'Kitchen', 'Sofa', 'Dining'):
        r = [o for o in bpy.data.objects if o.name.startswith(lvl) and kind in o.name]
        if r:
            show(f'{lvl} *{kind}*', r)

print("\n--- BALCONY objects L3 (detail) ---")
for o in sorted(pref('L3_'), key=lambda o: o.name):
    if 'Balc' in o.name or 'Glaz' in o.name or 'Court' in o.name:
        b = bounds([o])
        if b:
            lo, hi = b
            print(f"  {o.name:44s} X[{lo.x:6.2f},{hi.x:6.2f}] Y[{lo.y:6.2f},{hi.y:6.2f}] Z[{lo.z:6.2f},{hi.z:6.2f}]")

print("\n--- GF COURTYARD-FACING GLAZING (ground floor) ---")
for o in sorted([o for o in bpy.data.collections['GF_Ground'].objects if 'Glaz' in o.name], key=lambda o: o.name):
    b = bounds([o])
    lo, hi = b
    print(f"  {o.name:44s} X[{lo.x:6.2f},{hi.x:6.2f}] Y[{lo.y:6.2f},{hi.y:6.2f}] Z[{lo.z:6.2f},{hi.z:6.2f}]")

print("\n--- L1 EAST-WING (x>12) objects, to find what faces the courtyard ---")
e = [o for o in bpy.data.collections['L1_Floor'].objects if o.matrix_world.translation.x > 12]
show('L1 east-wing cluster', e)
print("=" * 100 + "\n")
