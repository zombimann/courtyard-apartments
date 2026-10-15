# ANTIGRAVITY PROMPT — Courtyard Apartments on a 50×100 ft plot (v3, 5 storeys, gate faces WEST)

Paste everything below the line into Antigravity (Blender MCP connected, "Use Poly Haven" ticked in the Blender MCP panel). This replaces v2 completely.

---

You are working in Blender 5.2 via the Blender MCP. Open `Basement Parking 50x100 v1.blend` and its script `build_basement_parking.py` in my project folder. Evolve that basement into a complete **5-storey courtyard apartment building (GF + L1–L4)** in Nairobi, Kenya. Write ONE parametric script `build_courtyard_apartments_v3.py` (all dimensions as named constants at the top; re-running it rebuilds the scene from scratch). Save as **`Courtyard Apartments 50x100 v3.blend`**. Do not overwrite v1.

Work in STAGES (plan at the bottom). After each stage: take a viewport screenshot, check it against this brief, fix problems, then continue. If a step fails, simplify — never stop silently.

## 0. Coordinate system, orientation & fixed facts
- Plot 15.24 m (x, the 50 ft street/gate side) × 30.48 m (y, depth). Origin = front-left plot corner at street level (standing on the street looking into the plot). x = 0 left boundary, x = 15.24 right boundary, y = 0 street boundary, y = 30.48 rear boundary. z = 0 = street level.
- **Orientation: the gate/street faces WEST.** So: street (y = 0) = WEST, rear (y = 30.48) = EAST, left boundary (x = 0) = NORTH, right boundary (x = 15.24) = SOUTH. In Blender world space **north = −X**. Set the Sun Position add-on north offset so its north arrow points along −X (check visually; flip the sign if it points +X). Add a small north-arrow object in the `Annotations` collection.
- Walls ON the left, right and rear boundaries (external face on the boundary line, max 0.3 m inside). These building walls ARE the fence. Only the street side has gates.
- **No windows, vents or projections on any boundary wall.** All habitable rooms take light from the courtyard or the street.
- Parameters: `N_UPPER = 4` (fixed: GF + L1–L4 = 5 storeys = 13 homes), `GF_RAISE = 0.90`, `BASEMENT_FFL = -2.00`, `UPPER_FTF = 3.00`, `GF_FTF = 3.30`, `PARAPET = 1.10`, `WING_DEPTH = 6.30`, `BALCONY_PROJ = 1.20`.

## 1. Basement (split-level) — WHY
The v1 ramp profile does not work: 0.20 + 0.16 + 2.50 + 0.15 m = 3.01 m, but the floor is at −3.30, and a full-depth ramp leaves no room to turn. Fix: raise the ground floor 0.90 m (podium) and put the basement floor at **−2.00**.
- Flat-slab podium (no downstand beams over drive aisles). Clear headroom ≥ 2.40 m everywhere, including under ducts and lights.
- **Ramp** on the LEFT (north) strip x 0.3–3.48, one-way, 3.2 m clear, 450 mm kerb. Profile: crest +0.15 at the gate (keeps road stormwater out; trench drains at crest and bottom) → 5.0 m at ≤1:25 → 2.4 m transition ~6% → main ≤12.5% → 2.4 m transition ~6% → touch down by y ≈ 23. **Print the profile table and assert the drops sum exactly to the floor level.** Red/green traffic lights at both ends, convex mirror at the street, amber flasher + buzzer when the door opens.
- **Car portal**: motorised sectional door set back ~1.5–2 m from the street boundary (under the front block), chamfered guard-house corner for visibility.
- **Layout (9 car bays)** — bays now sit on the LEFT of the aisle so the wider upper wing can have columns:
  - **Core** (stair + lift) front-right x 10.49–14.94, y 0.3–5.2, continues to the roof.
  - **Lift lobby** x 8.48–12.0, y 5.2–8.0 (lift door opens into it). **Utility/server room** x 12.0–14.94, y 5.2–8.0, door off the lobby.
  - **Left bay row** x 3.48–8.48 (5.0 m deep, nose-in): **accessible bay 3.6 m wide at y 5.2–8.8, directly beside the lift lobby** (no crossing of traffic), then 4 bays 2.5 m wide to y 19.1.
  - **Aisle** x 8.48–14.94 (≥6.1 m), y 8.0–19.1 (short dead-end aisle; mark a 1.2 m kerbed/painted walkway from lobby to bays, s.201).
  - **Cross aisle / turning zone** x 3.48–14.94, y 19.1–25.2 (6.1 m).
  - **4 bays along the rear wall** x 3.48–14.94, y 25.2–30.18 (~2.85 m wide each), one EV bay with charger (s.38).
  - **Ramp run-out** x 0.3–3.48, y 23.0–30.18: kept clear so a car leaving the ramp foot (heading east) has room to swing right into the cross aisle. Use its far end for motorbikes, bicycles and the sump. Only if the swept path proves a car can still turn, add a 10th bay here and report it.
  - No basement under y 0–5.2 between x 3.48 and 10.49 (solid ground under the street-level shop/guard).
- **Basement column lines** (x): 3.48 (ramp wall), **6.30** (under the new wing face — columns ONLY on bay-division lines, deduct 0.3 m per column from the bay row), 8.48 (bay fronts, set 0.3 m into the bay row), plus the boundary walls. Right part of the podium spans ~6.5 m from x 8.48 to the right wall — use a 300 mm flat slab with drop panels there and flag it for the engineer.
- **Turning check**: draw the swept path (car 4.8×1.8 m, 5.3 m outer turning radius) from the ramp foot through the cross aisle into every bay. If a move fails, adjust (raise `GF_RAISE` up to 1.05, shorten transitions, or drop one bay) and report. The ramp foot is the critical move — test it first.
- **Utility/server room**: at the HIGH end of the floor falls (1:100 to a sump at the rear), 150 mm upstand threshold, no water pipes overhead, dedicated extract/AC, cable riser in the core, fibre/power duct entry through the front wall.
- **Water**: sunken concrete tank under the ramp (x 0.5–3.2, y 3–13, base ~−3.0) for domestic storage + roof rainwater (irrigation, WC flushing). Pump room beside it.
- 2 extract shafts (s.156: ≥6 ACH, 10 ACH fire mode) rising in the store at x 0–3.0, y 5.8–7.3 on every floor and discharging ≥1 m above the roof parapet, away from windows. Fresh air via the ramp portal.

## 2. Ground floor (podium FFL +0.90; shop & guard at street level 0.00)
- **Street side (y 0–5.2), left (north) to right (south):**
  - x 0–3.48: car portal + ramp.
  - x 3.48–5.68: **guard house** y 0–3.0 (~6.5 m² incl. 1.0×1.4 WC); windows onto the car portal, pedestrian gate and courtyard; gate controls, intercom, CCTV monitor.
  - x 3.48–5.68, y 3.0–5.2: **storage** + bin/meter niche.
  - x 5.68–7.28: **pedestrian gate** (steel door + intercom) into a covered entry; steps + accessible ramp ≤1:12 with landings up 0.90 to the courtyard, running along the courtyard's front edge.
  - x 7.28–10.49: **shop** (~17 m², street level). Roller shutter to the street only; no door into the courtyard.
  - x 10.49–15.24: core; lift stops B1, GF, L1–L4; lobby door faces the courtyard.
- **Car ramp is cordoned off**: full-height screen wall at x ≈ 3.6 (planted courtyard face with climbers). No pedestrian access to the ramp from the courtyard.
- **Colonnade**: the upper wing overhangs the courtyard to x 6.30, so the GF courtyard has a shaded colonnade x 3.6–6.3 with slim columns on the x = 6.30 line (same positions as the basement columns below). Benches and planters between columns.
- **2-bed (GF)**: x 3.6–15.24, y 23.0–30.48 (~86 m²) + laundry/store x 0.3–3.6 behind the ramp head. Front door and all windows face the courtyard.
- **Courtyard**: x 3.6–15.24, y 5.2–23.0 (~205 m² at ground), of which ~110 m² is open to the sky (x 6.3–13.44, y 7.3–23.0).

## 3. Typical upper floor (L1–L4) — 2× 2-bed + 1× 1-bed, deeper overhangs
- **1-bed (front, street aspect)**: x 0–10.49, y 0–5.8 (~55 m² net). Living room + bedroom face the street with a RECESSED balcony (nothing projects past the street boundary).
- **Store / shaft zone**: x 0–3.0, y 5.8–7.3 (1-bed store + the basement extract shafts).
- **Front gallery**: x 3.0–15.24, y 5.8–7.3 (1.5 m), from the lift lobby.
- **2-bed (left/north wing, THICKER)**: x 0–6.30, y 7.3–23.0 (~99 m² gross, ~88 m² net). Front door off the front gallery. Two-zone plan: habitable rooms along the courtyard face (living/dining, master, bedroom 2), with kitchen, bathrooms, wardrobes and corridor against the boundary wall. Structure: wall/columns at x 0, 3.48 and 6.30 — no cantilever.
- **Right (south) gallery**: x 13.44–15.24 (1.8 m), y 7.3–23.0, solid wall on the boundary side, 1.1 m balustrade (vertical bars, gaps <100 mm) with continuous planter boxes on the courtyard side.
- **2-bed (rear/east block, premium)**: x 0–15.24, y 23.0–30.48 (~100 m² net incl. a recessed loggia). Door at the end of the right gallery; windows on the courtyard face only.
- **Balconies cantilever into the courtyard** (`BALCONY_PROJ = 1.20`): left wing — two balconies per flat in front of living room and master bedroom, x 6.3–7.5, ~3.0 m long each, **staggered floor to floor** so no balcony sits directly over another's living-room window; rear block — one living-room balcony y 21.8–23.0. Planters on every balcony edge.
- **Courtyard void** (open to sky): x 6.3–13.44, y 7.3–23.0 (≈ 7.1 × 15.7 m ≈ 112 m²; ≥ 5.9 m clear between balcony edge and gallery).
- **Room schedule (realistic Nairobi sizes)**:
  - 2-bed: living/dining 20–26 m², kitchen 7–9 m² (+ drying yard/balcony), master ≥3.3×3.6 + en-suite ~1.8×2.4, bedroom 2 ≥3.0×3.3, common bath ~1.8×2.2, linen/store.
  - 1-bed: living/kitchenette 20–24 m², bedroom ≥3.0×3.6, bath ~1.8×2.2.
  - Partitions 100–150 mm; doors 0.9 m entry / 0.8 m rooms.
  - Windows: ≥10% of floor area per habitable room, ≥5% openable with part ≥1.75 m above floor (s.143(1),(3)); **+5% window area per 300 mm of balcony projecting over a window (s.143(2)) → +20% under a 1.2 m balcony.** Internal bathrooms get mechanical extract to roof.

## 4. Roof (flat)
1.1 m parapet. **Main stair continues to the roof (s.194(2) — building is over 4 storeys).** Lift overrun ~3.6 m above the top stop (L4), stair headroom, elevated water tanks on a stand, solar PV + solar water heaters, communal roof garden (planters, pergola, seating), covered drying area, roof falls to outlets with downpipes to the rainwater tank.

## 5. Structure, levels & materials
- **Levels**: street 0.00; basement FFL −2.00; GF +0.90; L1 +4.20; L2 +7.20; L3 +10.20; L4 +13.20; roof slab top +16.20; parapet top +17.30. Show a level table.
- **Structure**: RC frame. x lines 0, 3.48, 6.30, 8.48 (basement/GF only), 10.49, 15.24; y lines 0, 5.2/5.8, 7.3, ~11, ~15, 19.1, 23.0, 30.48 (adjust to bay divisions). Columns 400×400 B1–GF, 300×300 above. Flat slabs 250–300 mm podium (drop panels where spans exceed 6 m), 200 mm upper floors. RC lift shaft. Basement retaining walls + raft 300 mm, waterproofed. Every upper column lands on a basement column; flag any transfer beam.
- **Lift**: small 8-person (630 kg) machine-room-less lift, 6 stops (B1, GF, L1–L4). Build the RC shaft now; the car can be installed later.
- **Materials** (realistic, correct scale, procedural or Poly Haven):
  - Concrete: raft, retaining walls, frame, slabs, core, ramp.
  - Machine-cut quarry stone 200 mm (≈200×200×400), rendered off-white: all boundary/party walls and external walls (s.129 ≥200 mm).
  - Interlocking stabilised soil blocks (ISSB, warm terracotta, fair-faced, ≈300×150×100 as a parameter): guard house, shop and store walls, courtyard feature walls, raised planters and seat walls, ramp screen wall (courtyard face), internal partitions, parapets with concrete coping. Never below ground or structural; concrete plinth ≥150 mm under every ISSB wall.
  - Visible mortar joints on ISSB/stone.
  - Accents: charcoal steel balustrades and sectional door; warm timber-look vertical fins; perforated concrete breeze-block panel on the core's courtyard face.
- **Sun response (gate faces west)**: west street façade and the rear block's west-facing courtyard façade get deep vertical timber fins + recessed glazing (hot afternoon sun); the left wing's south-facing courtyard façade gets 600 mm horizontal hoods; the front block's east-facing courtyard side is shaded by the gallery.
- **Style**: contemporary Kenyan / tropical-modern; calm, grounded, realistic proportions; plants everywhere.

## 6. Green (as much as possible)
- **Courtyard on the podium** (model soil depths visibly): lawn on a 300 mm build-up with ISSB edging that doubles as seating; shrub beds in 600 mm raised planters; one multi-stem feature tree (~5 m) in a 1.2 m-deep raised planter near the centre of the open-sky zone (≈ x 10, y 15) with a local podium drop panel under it (flag for engineer); permeable pavers on paths; rain garden fed by downpipe overflow; small children's corner and benches; planters between colonnade columns.
- Climbers on the ramp screen wall and the GF part of the right party wall.
- Planter boxes with trailing plants on every gallery and balcony.
- Rooftop planters/green roof.
- Poly Haven plant models where available, else simple low-poly plants. Soft landscape ≥50% of the open courtyard.

## 7. Scene, cameras & output
- **Annotations**: ALL text, grid bubbles, dimensions and the north arrow in an `Annotations` collection — hidden in perspective renders, shown only in plan renders. (v1 had floating unreadable 3D text.)
- **Lighting**: Sun Position add-on, Nairobi lat −1.29, long 36.82, UTC+3, north = −X. Sky texture or Poly Haven daytime HDRI. No grey void. Times: street views 16:30 (west façade lit), courtyard and aerial 10:30.
- **Collections per level** (B1, GF, L1–L4, Roof) so plans can be cut.
- **Renders** (EEVEE 1920×1080; Cycles if the GPU allows):
  1. Street view of the west façade and gates.
  2. Aerial ¾ view from the street-left (north-west).
  3. Courtyard at eye level (1.6 m) looking east to the rear block.
  4. L3 gallery view down into the courtyard (shows the overhangs and colonnade).
  5. Roof garden.
  6. Sectional cutaway through courtyard, ramp and basement.
  7. Orthographic labelled plans: B1, GF, typical floor, roof.
  8. Long section through the ramp.
- **Walkthrough** (30 s, 24 fps): street → pedestrian gate → up to the courtyard → colonnade → lift lobby → L2 gallery → look into the courtyard → roof. Second clip (10 s): car from the street down the ramp into the basement. Output MP4 (H.264) directly.
- Simple furniture blocks in the left-wing 2-bed and the 1-bed so views read as homes.

## 8. Report (save `Courtyard Apartments v3 Report.md` + screenshots)
1. **Area schedule**: every unit and room (m²); courtyard area; total GFA; site coverage.
2. **Unit & parking count**: 13 homes (1 GF + 3 × L1–L4) vs 9 bays (+ motorbikes) and ratio.
3. **Ramp table** + swept-path result.
4. **Compliance table** — one row per clause: PASS, CONFLICT or NOT CHECKED. Never write PASS for something you did not compute. Kenya National Building Code 2024 (LN 47/2024):
   - s.20 courtyard: ≥35 m² unobstructed, min dimension 4.5 m.
   - s.137 + Table 19 zone of space outside each habitable window: length ≥ H/3, where H = height from window head to top of the wall containing it (the 71.5° plane in Fig. 10), ≥1 m to any obstruction. Compute for the L1 left-wing living room (worst case: H ≈ 17.3 − 6.3 = 11.0 → ≥3.67 m).
   - s.137(11) projections over windows: ≥2/3 of the zone of space must stay open to the sky; opaque projection must stop ≥1 m short of any obstruction. Check every balcony.
   - s.143 window areas incl. the balcony uplift in s.143(2).
   - s.17 balustrades ≥1 m. s.38 EV bays. s.41 vehicle barriers. s.42 ramp approach. s.44 ramp slope and width. s.156 basement ventilation. s.194(2) stair to roof. s.205 risers 150–180 mm, treads 250–320 mm. s.353 accessible bay. s.400 basement escape. s.401(2) stair entrances ≥5 m apart. s.21 (≤5 storeys: no secondary access needed).
   - **Mark as CONFLICT, needs county relaxation:** s.18 (6 m open front space for residential buildings — shop and guard house are on the street boundary) and s.19 (1.5 m open side space on at least one side — walls are on both side boundaries).
5. **Assumptions & open items**: structure sizes and podium soil/tree loads (engineer to confirm), fire ratings not checked, county parking ratio unknown.

---

## Stage plan (do in order, screenshot after each)
1. Basement + ramp rework; levels table; swept path.
2. Structure frame and core through all 5 storeys + roof.
3. Ground floor: utility house, entry, colonnade, courtyard, GF 2-bed.
4. Typical floor units, galleries and staggered balconies, repeated for L1–L4.
5. Roof.
6. Materials, sun shading and landscape.
7. Sun/north check, cameras, renders, walkthrough MP4s.
8. Report.
