"""
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
dump_geometry.py -- extract 2-D geometry from the Blender model for drawing
production (plans, sections, elevations, schedules).

Run inside Blender:
  blender.exe -b "Courtyard Apartments 50x100 v3.blend" --python scripts\\dump_geometry.py

Writes docs/drawings/geometry.json containing:
  cuts     - horizontal and vertical section polylines
  boxes    - object bounding boxes with a category, for elevation projection
  openings - window / door panels, for plan symbols and schedules
"""
import bpy, json, os, sys
from mathutils import Vector

PROJ = _PROJ
OUT = os.path.join(PROJ, "docs", "drawings")
os.makedirs(OUT, exist_ok=True)

# Plan cut heights: 1.10 m above the finished floor level of each storey.
# The previous values were only 0.30-0.35 m above FFL, which is below every
# window sill, so the windows -- the whole point of the scheme -- were not cut
# and did not appear on any floor plan.
#   B1 floor -2.00 -> -0.90    GF floor +0.90 -> +2.00
#   L1 +4.20 -> +5.30   L2 +7.20 -> +8.30   L3 +10.20 -> +11.30
#   L4 +13.20 -> +14.30   roof slab +16.20 -> +17.30
PLAN_Z = {
    'B1': -0.90, 'GF': 2.00, 'L1': 5.30, 'L2': 8.30,
    'L3': 11.30, 'L4': 14.30, 'ROOF': 17.30,
}
SEC_X = {'LONG_A': 7.62}
SEC_Y = {'CROSS_B': 14.00}

HIDE = ('CONFLICT', 'Annotation', 'Label_', 'North_Arrow', 'Camera_', 'Prod_',
        'Walkthrough', 'Car_Descent', 'Swept_', 'V4_', 'Site_', 'Hero')

def hidden(o):
    if o.hide_render or o.type != 'MESH':
        return True
    return any(h in o.name for h in HIDE)

def tri_iter(me):
    me.calc_loop_triangles()
    vs = me.vertices
    for t in me.loop_triangles:
        yield (vs[t.vertices[0]].co, vs[t.vertices[1]].co, vs[t.vertices[2]].co)

def cut_plane(objs, axis, value, key_a, key_b):
    """Intersect every mesh with a plane; group segments by source object so the
    drawing pass can poché walls."""
    out = {}
    for o in objs:
        mw = o.matrix_world
        segs = []
        try:
            for a, b, c in tri_iter(o.data):
                pa, pb, pc = mw @ a, mw @ b, mw @ c
                pts = []
                for p, q in ((pa, pb), (pb, pc), (pc, pa)):
                    da = p[axis] - value
                    db = q[axis] - value
                    if (da <= 0 < db) or (db <= 0 < da):
                        t = da / (da - db)
                        pts.append(p.lerp(q, t))
                if len(pts) >= 2:
                    segs.append([
                        round(pts[0][key_a], 4), round(pts[0][key_b], 4),
                        round(pts[1][key_a], 4), round(pts[1][key_b], 4),
                    ])
        except Exception:
            continue
        if segs:
            out[o.name] = segs
    return out

def bbox(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [round(min(p.x for p in pts), 3), round(min(p.y for p in pts), 3),
            round(min(p.z for p in pts), 3), round(max(p.x for p in pts), 3),
            round(max(p.y for p in pts), 3), round(max(p.z for p in pts), 3)]

def category(name):
    if name.startswith('Col_'): return 'column'
    if name.startswith('Beam'): return 'beam'
    if name.startswith('Slab_'): return 'slab'
    if name.startswith('GF_Tree'): return 'tree'
    if 'Glaz' in name or 'Glass' in name or 'Win_' in name: return 'glazing'
    if 'Door' in name: return 'door'
    if 'Stair' in name or 'Flight' in name: return 'stair'
    if 'Balustrade' in name or 'Rail' in name: return 'railing'
    if 'Planter' in name or 'Bed_Plants' in name or 'Foliage' in name: return 'planting'
    if 'Boundary' in name or 'Parapet' in name or 'Retaining' in name: return 'structure'
    if 'Floor' in name or 'Finish' in name or 'Paver' in name: return 'floor'
    if 'Wall' in name or 'Part_' in name: return 'wall'
    if 'Ramp' in name or 'Bay' in name or 'Line' in name: return 'parking'
    return 'other'

def main():
    objs = [o for o in bpy.data.objects if not hidden(o)]
    print(f"visible meshes: {len(objs)}")

    data = {'units': 'metres', 'plans': {}, 'sections': {}, 'boxes': [],
            'openings': [], 'meta': {}}

    for name, z in PLAN_Z.items():
        segs = cut_plane(objs, 2, z, 0, 1)
        data['plans'][name] = {'z': z, 'segs': segs}
        print(f"  plan {name} z={z}: {len(segs)} objs / {sum(len(v) for v in segs.values())} segs")

    for name, x in SEC_X.items():
        segs = cut_plane(objs, 0, x, 1, 2)
        data['sections'][name] = {'axis': 'X', 'value': x, 'segs': segs}
        print(f"  section {name} x={x}: {len(segs)} objs / {sum(len(v) for v in segs.values())} segs")
    for name, y in SEC_Y.items():
        segs = cut_plane(objs, 1, y, 0, 2)
        data['sections'][name] = {'axis': 'Y', 'value': y, 'segs': segs}
        print(f"  section {name} y={y}: {len(segs)} objs / {sum(len(v) for v in segs.values())} segs")

    for o in objs:
        bb = bbox(o)
        cat = category(o.name)
        data['boxes'].append({'n': o.name, 'b': bb, 'c': cat,
                              'm': o.data.materials[0].name if o.data.materials else ''})
        if cat in ('glazing', 'door'):
            data['openings'].append({'n': o.name, 'b': bb, 'c': cat,
                                     'w': round(bb[3] - bb[0], 3),
                                     'd': round(bb[4] - bb[1], 3),
                                     'h': round(bb[5] - bb[2], 3)})
    print(f"  boxes: {len(data['boxes'])}, openings: {len(data['openings'])}")

    # collection extents, useful for sheet framing
    for c in bpy.context.scene.collection.children:
        pts = []
        for o in c.objects:
            if hidden(o):
                continue
            bb = bbox(o)
            pts += [(bb[0], bb[1], bb[2]), (bb[3], bb[4], bb[5])]
        if pts:
            data['meta'][c.name] = [
                min(p[0] for p in pts), min(p[1] for p in pts), min(p[2] for p in pts),
                max(p[0] for p in pts), max(p[1] for p in pts), max(p[2] for p in pts)]

    p = os.path.join(OUT, 'geometry.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(f"wrote {p}  ({os.path.getsize(p)/1024:.0f} KB)")

main()
