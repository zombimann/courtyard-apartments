# Drawing Set Review

A sheet-by-sheet verification of the Courtyard Apartments drawing set against
the model geometry, the compliance register and the cost plan.

**Method.** Every sheet was inspected at full resolution (4966 × 3507 px, A1 at
150 dpi) and every dimension, area, level and compliance figure on it was
re-derived from `docs/drawings/geometry.json` — the geometry actually exported
from `Courtyard Apartments 50x100 v3.blend`. Nothing below is based on reading
the rendered sheets by eye; each number was recomputed from the model.

---

## 1. Errors found and fixed

### 1.1 Basement plan read "Cut at +-1.20 m"

`make_drawings.py` formatted the cut note as `f"Cut at +{z:.2f} m"`. For the
basement `z` is negative, so the sheet printed a double sign.

| | |
|---|---|
| Was | `Cut at +-1.20 m. Dimensions in metres...` |
| Now | `Cut at -0.90 m (+1.10 m above FFL). Dimensions in metres...` |

The note now also states the height above finished floor level, which is the
convention and removes the ambiguity about whether the figure is absolute.

### 1.2 Plan cuts were below every window sill — windows were missing from all plans

This is the most consequential drafting error found.

The plans were cut 0.30–0.35 m above finished floor level (GF cut at +1.20 on a
+0.90 slab; L1 at +4.55 on +4.20). Standard practice is 1.0–1.2 m. Because
almost every window in the scheme has a sill above 0.35 m, **the windows were
not intersected by the cut and therefore did not appear on any floor plan** —
on a project whose entire premise is daylight into a deep plan.

Verified against the opening geometry:

| Plan | Cut was | Openings shown | Cut now | Openings shown |
|---|---|---|---|---|
| B1 | −1.20 | 0 | −0.90 | 0 *(no basement openings in model)* |
| GF | +1.20 | 7 | +2.00 | 7 |
| L1 | +4.55 | 8 | +5.30 | **10** |
| L2 | +7.55 | 8 | +8.30 | **10** |
| L3 | +10.55 | 8 | +11.30 | **10** |
| L4 | +13.55 | 8 | +14.30 | **10** |

Two additional glazing panels per storey now appear. The cut heights are set
1.10 m above FFL in `scripts/dump_geometry.py`, documented there so the
reasoning travels with the code.

### 1.3 S08 stated a basement area larger than the site

| | |
|---|---|
| Was | `B1 Basement parking — 9 bays + bikes — 620 m2` |
| Now | `B1 Basement parking — 9 bays + bikes — 464.5 m2 gross` |

The plot is 15.24 × 30.48 = **464.5 m²**. A basement cannot exceed the footprint
of the site it sits under, so 620 m² was impossible. The model's raft covers the
full plot, so 464.5 m² gross is the correct figure.

This number had propagated: the Bill of Quantities uses "1,983 m² incl.
basement" = 1,363 + 620, so the basement figure in the cost plan is also wrong.

### 1.4 S08 stated a roof area of ~120 m²

| | |
|---|---|
| Was | `Roof communal garden + PV — ~120 m2` |
| Now | `Roof garden terrace — pergola, planters, seats — 57.0 m2` and `Roof slab (excl. terrace fit-out) — 327.7 m2` |

The roof terrace floor in the model is `Roof_Garden_Terrace_Floor`,
X 0.30–6.00 × Y 8.00–18.00 = 5.70 × 10.00 = **57.0 m²**. The figure of 120 m²
matched neither the terrace nor the 327.7 m² roof slab.

### 1.5 S08 claimed 37.6% window area — the real figure is 7.2%

| | |
|---|---|
| Was | `s.143(1) windows >= 10% floor area — 37.6% (see note) — NOTE` |
| Now | `s.143(1) windows >= 10% floor area — 7.2% modelled − see note — CHECK` |

37.6% is approximately the **total glazing of all five storeys divided by the
area of a single floor plate** (119.5 / 327.73 = 36.5%) — a category error that
inflates the result roughly five-fold.

Recomputed from the model's 28 glazing panels, total glass = **119.5 m²**:

| Storey | Glass | Floor plate | Ratio |
|---|---|---|---|
| GF | 29.4 m² | 359.8 m² | 8.2% |
| L1 | 22.5 m² | 327.7 m² | 6.9% |
| L2 | 22.5 m² | 327.7 m² | 6.9% |
| L3 | 22.5 m² | 327.7 m² | 6.9% |
| L4 | 22.5 m² | 327.7 m² | 6.9% |
| **Total** | **119.5 m²** | **1,670.7 m²** | **7.2%** |

**The modelled glazing is below the 10% the clause requires.** See §2.3 — this
is as likely to be an incomplete model as a design failure, but either way the
previous sheet asserted a pass that the geometry does not support.

### 1.6 S08 s.143(2) asserted a figure it could not support

| | |
|---|---|
| Was | `s.143(2) glazing + balcony uplift >= 30% — 68.4% (see note) — NOTE` |
| Now | `s.143(2) glazing + balcony uplift >= 30% — not verified — CHECK` |

The glazing half of that calculation is 7.2%, not the assumed figure, so the
68.4% has no basis. Marked as unverified rather than guessed.

### 1.7 S08 s.137 stated the wrong divisor

`7.14 m >= 4.37 m` → `7.14 m >= 4.40 m`. With H = 13.20 m, H/3 = 4.40 m. The
4.37 came from a 13.10 m wall height that is not in the model. The result
(PASS, by a wide margin) is unchanged.

### 1.8 S01 street band ran off the page

The street rectangle was drawn from model x = −40 m to +60 m, which projects to
x = −472 px on a sheet whose frame begins at x = 106 px. The band bled off the
left edge of the paper. Now drawn from −4 m to +19.24 m, inside the frame.

### 1.9 The compiled PDF contained only one sheet

Reported separately and already fixed: the PDF was assembled from only the
sheets drawn in that run, so a `--only S07` re-run replaced the 8-page set with a
1-page one. The PDF is now always built from every sheet present on disk. Sheet
S08 now also carries a NOTES block recording the basis of the GFA and the s.143
position, so the sheet is self-explaining.

---

## 2. Found, not fixed — these need a decision

### 2.1 The gross floor area is undefined

The README, the Bill of Quantities and the specification all use **GFA =
1,363 m²** (1,983 m² including the basement). That figure cannot be derived from
the model.

Measured floor plates (union of every slab and floor box, 5 cm raster):

| Storey | Plate |
|---|---|
| B1 | 464.5 m² |
| GF (podium) | 359.8 m² |
| L1 | 327.7 m² |
| L2 | 327.7 m² |
| L3 | 327.7 m² |
| L4 | 327.7 m² |
| **Above ground** | **1,670.7 m²** |
| **Including B1** | **2,135.2 m²** |

1,363 m² *is* reproducible if open areas are excluded — GF minus the courtyard
void (112.1) and colonnade (48.1), plus four floors minus the open access
galleries (28.26 + 9.98 each) = **1,357.5 m²**, within 0.4% of 1,363. So the
number is probably not an arithmetic error; it is an unstated measurement basis.

That matters because the cost plan applies it as gross floor area:

- at 1,363 m² → **KES 241,700/m²**
- at 1,670.7 m² → **KES 197,200/m²** *(including all slab plates)*

A 23% swing in the headline rate. **Recommendation:** adopt one definition, state
it on S01 and S08, and use the same one in the BOQ and the specification. S08 now
records both figures and names the basis; the README, BOQ and spec still quote
1,363 m² without qualification.

### 2.2 The specification schedules do not reconcile with the model

| Schedule | Spec implies | Model contains |
|---|---|---|
| Windows (spec §S1) | 119 windows | **28 glazing panels** |
| Doors (spec §S2) | 109 doors | **20 door openings** |

The quantities in the specification's schedules were written as plausible
estimates when the document was drafted, not measured from the model. They are
not defensible in a tender document and should either be measured from the model
or the model completed until it contains the glazing the design intends.

### 2.3 s.143(1) may fail, or the model may be incomplete

The model has 28 glazing panels for 13 dwellings — about two windows per home —
against a design that specifies a 3.5 m × 2.4 m glazed wall to every living room
alone. Either:

- the model is missing most of its glazing, in which case the 7.2% is meaningless
  and the model must be completed before any window-area claim is made; or
- the model is complete, in which case the scheme is at 7.2% and **does not meet
  s.143(1)**.

The figures cannot distinguish these. This needs resolving before submission,
and it is the same root cause as the missing wall openings already recorded in
the QA notes — the model's envelope is not fully built.

### 2.4 Opening count is reported inconsistently

| Source | Count |
|---|---|
| Geometry export | 48 (28 glazing + 20 door) |
| Render pipeline log | 43 panels across 28 walls |
| README / QA notes | 43 |

The README and QA notes quote 43; the export records 48. Most likely the render
pipeline excludes five items it does not treat as wall openings (the sectional
vehicle door, the roof stair door and the store louvre doors). Not yet traced.

### 2.5 S05 roof plan is thin

It shows the outline, pergola, planters, tanks, stair and PV locations, but no
roof falls, no rainwater outlets, no downpipe positions and no parapet line, and
the courtyard opening in the roof is not clearly identified as a void. A roof
plan is where the waterproofing and drainage strategy is communicated; this one
does not yet do that.

### 2.6 S07 elevations are massing, not drawings

The elevations are painter's-algorithm box projections. They read as tonal
masses: the west elevation is legible, the other three are near-blank because
they abut boundary walls. This is a known limitation, stated on the sheet.
`scripts/render_elevations.py` will produce proper orthographic clay elevations
with hidden-line removal in Blender and has not yet been run — it needs the CPU
free of a render.

### 2.7 S01 is largely empty

The cover sheet carries a small key plan, a key-data table and the drawing
register, and roughly two-thirds of an A1 sheet is blank. It should carry a
location plan, a site plan at 1:200 with the street and neighbouring plots, and
a small perspective.

---

## 3. Verified correct

These were checked and found sound. Listing them matters as much as the errors —
it bounds where the problems are.

**Dimensions**
- Horizontal grid chain: 3.48 + 2.82 + 2.18 + 2.01 + 2.95 + 1.80 = **15.24 m** ✓
- Vertical grid chain: 5.20 + 2.10 + 3.70 + 4.00 + 4.10 + 3.90 + 7.48 = **30.48 m** ✓
- Both chains close exactly on the plot boundary; every sheet carries the same
  grids (A–G across X, 1–8 along Y).
- All 713 exported boxes lie within X 0–15.24 (one exception at Y = −0.30, the
  gate post, which projects 0.30 m into the street — intentional).

**Courtyard**
- Void X 6.30–13.44 × Y 7.30–23.00 = **7.14 × 15.70 = 112.1 m²** ✓ matches the
  112.1 m² stated on S01, S03, S04 and S08.
- s.20 requires ≥ 35 m² with no dimension under 4.5 m → 112.1 m² / 7.14 m ✓
- s.137 requires the zone of space ≥ H/3 = 4.40 m → 7.14 m ✓

**Levels** — GF +0.90, L1 +4.20, L2 +7.20, L3 +10.20, L4 +13.20, roof slab
+16.20, parapet +17.30. Every slab box sits 0.20 m below its stated floor level,
consistent with a 200 mm slab. ✓

**Unit areas reconcile with the plates**
- North wing per floor: X 0–6.30 × Y 7.30–23.00 = 6.30 × 15.70 = **98.9 m²**,
  against the stated "~99 m² gross" ✓
- Rear block per floor: X 0–15.24 × Y 23.00–30.48 = 15.24 × 7.48 = **114.0 m²**
  against the stated "~107 m² net / ~107 m²" plus walls ✓
- Front block per floor: X 0–10.49 × Y 0–7.30 = **76.6 m²**, against "~63 m²
  gross" for the 1-bed plus entry and stair landing ✓

**Parking**
- Nine bays confirmed in the geometry: Bay_01 accessible plus bays 02–09.
- Standard bays **2.57 × 5.00 m** ✓
- Accessible bay **3.60 × 5.00 m** ✓ meets the 3.6 m requirement, and it is
  adjacent to the lift lobby.
- s.38: 1 EV bay of 9 = 11.1% ≥ 5% ✓

**Doors** — entry doors are 0.90 × 2.10 m, the vehicle portal 2.88 × 2.90 m, the
roof stair exit door 1.00 × 2.10 m. All plausible. ✓

**Sheet production**
- All eight sheets present, correct sheet numbers and titles in the title block.
- Page size is exactly **841 × 594 mm**, A1 landscape. ✓
- Compiled PDF is 8 pages, valid PDF-1.4, `/Count 8`. ✓
- Scale bars match the stated scales.

---

## 4. Residual honesty note

The set is now internally consistent and every figure on it can be traced to the
model or is explicitly labelled as unverified. What it is **not** is finished:

- the roof plan does not yet communicate drainage;
- the elevations are massing, not drawings;
- the model's envelope is incomplete (no wall openings; probably missing
  glazing), so any window-area compliance statement remains provisional;
- the GFA basis must be fixed once and applied consistently across the drawings,
  the cost plan and the specification.

Nothing in this set should be issued for construction until §2.3 is resolved.
