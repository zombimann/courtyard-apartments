"""query3.py - find genuinely free camera positions inside the L3 north wing
and on the L3 courtyard balcony. Prints every object bbox that occupies the
regions of interest so a camera can be placed in real empty space.
"""
import bpy
from mathutils import Vector

def bb(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def dump(label, xr, yr, zr):
    print(f"\n--- {label}  X{xr} Y{yr} Z{zr} ---")
    rows = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        lo, hi = bb(o)
        # overlap test with the region
        if (hi.x < xr[0] or lo.x > xr[1] or hi.y < yr[0] or lo.y > yr[1]
                or hi.z < zr[0] or lo.z > zr[1]):
            continue
        rows.append((o.name, lo, hi))
    for name, lo, hi in sorted(rows):
        print(f"  {name[:46]:46s} X[{lo.x:6.2f},{hi.x:6.2f}] Y[{lo.y:6.2f},{hi.y:6.2f}] Z[{lo.z:6.2f},{hi.z:6.2f}]")
    print(f"  ({len(rows)} objects)")

print("\n" + "=" * 100)
print("  QUERY 3 - INTERIOR CLEARANCES")
print("=" * 100)

# The L3 north-wing living room is the room behind the courtyard glazing
# L3_2BedL_Living_Glaze at X 6.22-6.30, Y 8.50-12.00, Z 10.20-12.60
dump("L3 north wing, around the courtyard living room",
     (0.0, 7.0), (6.5, 14.0), (9.8, 13.2))

dump("L3 courtyard balcony + its immediate surroundings",
     (5.0, 9.0), (7.0, 13.0), (9.8, 13.5))

dump("L3 whole north wing (X<6.4)",
     (0.0, 6.4), (6.0, 24.0), (10.0, 13.2))

dump("Roof deck around the pergola",
     (0.0, 8.0), (8.0, 20.0), (16.0, 20.2))

dump("Street frontage",
     (0.0, 15.24), (-1.0, 6.0), (0.0, 4.5))

# ---- candidate free-space probe: sample a grid and report emptiness -------
print("\n--- FREE-SPACE PROBE (are candidate camera points inside geometry?) ---")
def inside_any(p, margin=0.25):
    hits = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        lo, hi = bb(o)
        if (lo.x - margin <= p[0] <= hi.x + margin and
                lo.y - margin <= p[1] <= hi.y + margin and
                lo.z - margin <= p[2] <= hi.z + margin):
            hits.append(o.name)
    return hits

candidates = {
    'L3 living A (2.6, 9.8, 11.75)': (2.6, 9.8, 11.75),
    'L3 living B (3.6, 9.8, 11.70)': (3.6, 9.8, 11.70),
    'L3 living C (4.4, 9.8, 11.70)': (4.4, 9.8, 11.70),
    'L3 living D (3.6, 10.6, 11.70)': (3.6, 10.6, 11.70),
    'L3 living E (2.2, 10.6, 11.75)': (2.2, 10.6, 11.75),
    'L3 balcony  (6.95, 9.6, 11.75)': (6.95, 9.6, 11.75),
    'L3 balcony  (6.90, 10.8, 11.75)': (6.90, 10.8, 11.75),
    'L3 gallery  (14.3, 12.0, 11.75)': (14.3, 12.0, 11.75),
    'Courtyard   (11.6, 7.6, 2.30)': (11.6, 7.6, 2.30),
    'Courtyard   (12.4, 9.0, 2.30)': (12.4, 9.0, 2.30),
    'Courtyard   (7.0, 8.0, 2.30)': (7.0, 8.0, 2.30),
    'Colonnade   (5.0, 9.0, 2.30)': (5.0, 9.0, 2.30),
    'Roof        (4.6, 17.2, 17.75)': (4.6, 17.2, 17.75),
    'Roof        (3.0, 13.0, 17.75)': (3.0, 13.0, 17.75),
    'Roof        (7.0, 14.0, 17.75)': (7.0, 14.0, 17.75),
    'Street      (13.0, -31.0, 4.0)': (13.0, -31.0, 4.0),
    'Street      (6.0, -26.0, 3.0)': (6.0, -26.0, 3.0),
}
for label, p in candidates.items():
    hits = inside_any(p)
    status = "INSIDE: " + ", ".join(hits[:4]) if hits else "clear"
    print(f"  {label:40s} {status}")
print("=" * 100 + "\n")
