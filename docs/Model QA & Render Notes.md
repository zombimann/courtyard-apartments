# Model QA & Render Notes

**Scope:** review of `Courtyard Apartments 50x100 v3.blend` carried out while
producing the six hero renders, October 2026.
**Pipeline:** `scripts/render_hero_v3.py` (Blender 5.2 EEVEE Next).
**Method:** every finding below was verified by ray-casting through the actual
scene geometry and by mesh statistics, not by eye.

---

## 1. Defect found: every window and door panel is embedded in a solid wall

### What is wrong

In the saved model each glazing panel sits *inside* the wall box it belongs to,
with no opening cut. The wall is a closed six-polygon box that spans the full
extent of the façade; the glass is a thin box buried inside it.

Measured on the L3 north-wing living room:

```
L3_2BedL_Courtyard_Wall   X[6.15, 6.30]  Y[7.30, 23.00]  Z[10.20, 13.00]   6 polys
L3_2BedL_Living_Glaze     X[6.22, 6.30]  Y[ 8.50, 12.00]  Z[10.20, 12.60]   6 polys
```

The glazing occupies `X 6.22–6.30`, entirely inside the wall's `X 6.15–6.30`.
A ray cast from inside the living room along the sight line to the courtyard
stopped on the wall:

```
before fix:  L3_2BedL_Courtyard_Wall (Mat_ISSB_Terracotta) @ 4.38 m   <- view blocked
after  fix:  L3_2BedL_Living_Glaze   (Mat_Glass_Arch)       @ 4.48 m   <- passes through
```

**43 of 43 panels were affected** — every window and door in the building. The
practical consequence is that no habitable room in the model had any daylight
opening at all.

### Why it matters beyond the renders

The v3.1 report records, under the compliance patch summary:

> Living-room glazing widened 3.0 m → 3.5 m (all L1–L4) | s.143(2) | 27.7% → 37.6%
> floor area | **FIXED — now PASS**

The *panel* was widened, but because the panel sits inside a solid wall the
glazing area claim is not represented by the geometry. **s.143(1) and s.143(2)
should be treated as NOT CHECKED until the openings exist in the model**, and the
same caveat applies to the s.137 zone-of-space calculation, which assumes the
window is a real opening.

### What was done

`open_glazed_walls()` in the render pipeline:

1. finds every mesh using the glass material whose name is not a frame, rail or
   sill;
2. determines the panel's thin axis and looks for the smallest structural wall
   (ISSB / stone / concrete / RC slab) whose bounding box contains the panel on
   the other two axes;
3. builds one cutter per wall covering all of its openings, inflated through the
   full wall thickness, and applies a single **exact** boolean difference;
4. stretches the glass itself along the thin axis to fill the reveal, so the
   glazing is flush with both wall faces rather than leaving a slot.

Result: **43 openings cut across 28 wall objects**, 0 panels left embedded. The
key wall goes from 6 to 20 polygons, and sight lines now pass through.

> **Action for the model owner:** this fix is applied at render time only — the
> `.blend` on disk is untouched. The same openings should be built into
> `scripts/build_courtyard_apartments_v3.py` so the saved model, the reports and
> the drawings all agree.

---

## 2. Defect found: all block furniture shares the timber material

The interior furniture is deliberately simple blocking, which is fine, but
46 objects — sofas, beds, dining tables, desks, kitchen counters, bathroom
fittings — all reference `Mat_Warm_Timber`. Rendered, a sofa reads as a log.

**Fix:** `dress_furniture()` re-assigns plausible procedural materials by object
name — upholstery fabric for sofas and chairs, linen for beds, wood for tables,
desks and counters. It matches whole name tokens, not substrings, because unit
descriptors such as `2BedL` contain the substring `Bed`.

**37 objects** re-dressed.

---

## 3. Lighting: why the courtyard needs a high sun

The courtyard is a slot 7.1 m wide (X 6.30–13.44) with roughly 15.3 m of wall
above its floor. Direct sun reaches the floor only when

```
tan(elevation) > 15.3 / 7.1  ->  elevation > ~65 deg
```

so a "golden hour" sun cannot light the courtyard floor — it lights the upper
façades and leaves the floor in shade. That is physically correct, and it is why
the courtyard is comfortable, but it produces a dark, flat render.

The courtyard shots therefore use a **high afternoon sun, bearing 231°,
elevation 73°** (a realistic Nairobi afternoon), which gives:

| Surface | Normal | Lit? |
|---|---|---|
| Courtyard floor | +Z | yes (0.96) |
| North-wing courtyard façade | +X | yes (0.18) |
| Rear block, west courtyard face | −Y | yes (0.21) |
| South gallery | −X | shaded — provides the contrast |
| West street façade | −Y | yes (0.21) |

At 73° the shadow cast by the south gallery covers roughly the southern 5 m of
the lawn and the rest is sunlit — visible in shot 1.

The street and roof shots use a separate low `golden` rig (236° / 13°), with
per-shot overrides so the sun rakes across the west elevation in shot 3
(214° / 11°) and sits near the view axis for the backlit pergola in shot 6
(262° / 11°).

---

## 4. Render approach

**Engine: EEVEE Next, not Cycles.** Benchmarked on this machine
(`scripts/diagnostics/bench.py`):

| Engine | Resolution | Samples | Time |
|---|---|---|---|
| EEVEE | 1920 × 1080 | 64 | 39.6 s |
| Cycles (CPU) | 1280 × 720 | 48 | 196.2 s |
| Cycles (CPU) | 1920 × 1080 | 48 | ~441 s (extrapolated) |

Cycles is ~11× slower and there is no GPU (CPU-only AMD Athlon Gold 3150U, no
CUDA/OptiX device). The design brief also specifies EEVEE at 1920 × 1080.

**Why the first-pass renders failed.** The saved scene had a flat blue world
background at strength 2.2 — a uniform ambient dome whose irradiance was
comparable to or greater than the sun lamp's, which flattened every shadow and
washed the image out. The replacement uses a Nishita multiple-scattering sky at
strength ~0.25 with the sun as the dominant source, so shadows and form return.

**Other changes made at render time:**

- all 20 architectural materials rebuilt as procedural Principled setups
  (mottled concrete, coursed stone render, ISSB block pattern with mortar,
  timber grain along the member, blended glass with raytraced reflection);
- `Khronos PBR Neutral` view transform instead of AgX, which preserved far more
  colour on the warm terracotta and timber palette;
- site context added (carriageway, kerbs, footways, lane markings, neighbouring
  massing) so the building sits in a street;
- existing foliage subdivided, noise-displaced, and dressed with ~3,200 scattered
  leaf clusters to break up the low-poly silhouettes;
- annotations, compliance planes and text labels hidden from render;
- the planting palette (turf, leaf, foliage core) kept deliberately desaturated —
  a vivid green reads as astroturf under a strong sun, and the courtyard lawn is
  a large flat surface where that reads immediately;
- camera positions derived from measured geometry (`scripts/diagnostics/query3.py`)
  rather than estimated — the previous camera set pointed at empty air or solid
  walls because the courtyard, balcony and living-room positions had been guessed.

---

## 5. Design observation: the 1.10 m balustrade hides the courtyard floor

While placing the L3 viewpoint, a geometric consequence of the compliant
balustrade height became clear. s.17 requires ≥ 1.00 m; the model uses 1.10 m.
With an adult eye at about 1.6 m above the floor, a viewer standing `d` metres
back from the rail can see below it only at angles shallower than

```
atan((1.6 - 1.10) / d)   ->   at 0.85 m back:  atan(0.5 / 0.85) = 30 deg
                              at 0.30 m back:  atan(0.5 / 0.30) = 59 deg
```

Because the courtyard is only ~7.1 m wide and the galleries are 1.8 m deep, a
person standing normally behind the balustrade cannot see the courtyard floor at
all — only the opposite façade. The floor becomes visible only when leaning over
the rail or holding a camera above it.

This is not a compliance failure and it is normal for courtyard buildings, but
it is worth knowing during detailed design: the galleries give **no visual
surveillance of the courtyard floor**, which matters for the passive-security and
child-safety argument for a shared courtyard. Options are a lower rail with a
compliant infill, a section of railing replaced by a planter at seat height, or
accepting that the courtyard is overlooked from the units' glazing rather than
from the access galleries.

The L3 viewpoint for shot 5 was placed at 0.31 m from the rail and 0.8 m above
its top, which is the only position from which the courtyard reads.

---

## 6. Superseded first-pass renders

The six `Prod_*.png` images originally in `render/hero/` are kept in
`render/archive/`. They were unusable: the camera coordinates did not match the
model (shot 3 was a close-up of a fin wall, shot 5 was inside the opposite wing),
shot 1 was blocked by the tree trunk, red compliance planes bled onto the façade,
and a flat ambient world left everything shadowless and washed out.

---

## 7. Open items

1. **Openings not yet in the model** — see §1. Highest priority.
2. **s.18 / s.19 conflicts** unchanged: shop and guard house on the street
   boundary, walls on both side boundaries; county relaxation required.
3. **Walkthrough incomplete** — 42 of 720 frames rendered.
4. **Structural items** (drop panel under the courtyard tree, balcony cantilever
   tendons, transfer beams) remain flagged for the engineer; not checked here.
5. Neighbouring massing, road markings and the sun disc are **scene context added
   for presentation** and are not part of the design.
