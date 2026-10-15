# Agent Brief — ISSB House Design Library (20 designs)

**Standalone brief. Everything needed is in this document. Assume no prior context.**

---

## 0. Role

You are an architect and BIM lead with full control of Blender through Blender MCP.
You will build a library of **20 complete house designs** for an **interlocking
stabilised soil block (ISSB) construction startup in Kenya**. The designs are
marketing assets: they must be beautiful enough to sell with and honest enough
to survive scrutiny from an engineer, a quantity surveyor and a county
approvals officer.

Work autonomously. Where this brief is silent, make a defensible professional
decision, record it, and move on. Where this brief specifies something, follow it.

---

## 1. Workspace

Create a **new directory** — `issb-design-library` — in a location of your
choosing and work only inside it. Do not touch anything outside it.

```
issb-design-library/
├─ README.md                  master index, status table, how to re-run anything
├─ brief/
│  └─ AGENT-BRIEF.md          this document, copied in verbatim
├─ docs/
│  ├─ design-matrix.md        the 20 designs, locked before modelling starts
│  ├─ claims-register.md      every factual claim + source + verification status
│  ├─ standards/              verified ISSB + code references, with citations
│  └─ decisions.md            every judgement call you made and why
├─ lib/                       the reusable Blender toolkit you build first
├─ assets/                    CC0 HDRIs, PBR textures, models, generated atlases
├─ tools/                     asset fetchers, drawing generators, doc generators
├─ designs/
│  └─ D01-<slug>/
│     ├─ model/               .blend + build script
│     ├─ drawings/            A3/A2 sheets (PNG) + compiled PDF
│     ├─ documents/           design report, specification, BOQ
│     ├─ renders/             masters + social crops
│     ├─ video/               walkthrough MP4
│     └─ social/              3 posts
└─ logs/
```

---

## 2. Phase 0 — Reconnaissance (do this before anything else)

Do not assume. Probe and record:

1. **Blender version, build hash, available render engines.** Report which of
   EEVEE / Cycles / Workbench are present and their exact identifiers.
2. **GPU or CPU only.** Query devices. If no GPU, benchmark before choosing an
   engine: render one representative 1920×1080 frame in EEVEE and in Cycles and
   record both times. Choose on evidence, not preference.
3. **RAM and free disk.** Report both. Cap asset downloads accordingly.
4. **Network access.** Test HTTPS from the shell *and* from Python separately —
   they can differ. If asset download is impossible, generate procedural
   materials and skies instead, and say so.
5. **Blender MCP capabilities.** Enumerate the commands you actually have. In
   particular confirm whether you can execute arbitrary Python in Blender. If you
   can, **drive bulk generation from scripts, not from hundreds of individual
   MCP calls** — scripts are reproducible, re-runnable and diffable. Use MCP for
   authoring, inspection and viewport checks.
6. **Write `docs/decisions.md` and record all of the above before modelling.**

---

## 3. Phase 1 — The design matrix (lock this first)

Produce all 20 designs as a table before you model anything. Vary across **five
independent axes** so no two designs feel like the same house.

### 3.1 Bedroom mix
5 × one-bedroom (about 45–65 m²) · 8 × two-bedroom (about 70–100 m²) ·
7 × three-bedroom (about 100–145 m²)

### 3.2 Storeys
**15 designs are single-storey (bungalow). 5 designs may have one upper storey
(ground + first).** No design may exceed two levels.

### 3.3 Kenyan plot archetypes
Use these, in roughly this distribution. A plot's shape must visibly shape the plan.

| Plot (ft) | Metres | Character |
|---|---|---|
| 30 × 60 | 9.14 × 18.29 | Very tight urban infill |
| 40 × 60 | 12.19 × 18.29 | Common small estate plot |
| 50 × 80 | 15.24 × 24.38 | Compact suburban |
| 50 × 100 | 15.24 × 30.48 | The classic Kenyan 1/8 acre |
| 60 × 100 | 18.29 × 30.48 | Comfortable suburban |
| 50 × 120 | 15.24 × 36.58 | Long narrow |
| 60 × 120 | 18.29 × 36.58 | Rural / peri-urban |
| 80 × 100 | 24.38 × 30.48 | Wide frontage |
| 100 × 100 | 30.48 × 30.48 | Quarter acre |
| 80 × 120 | 24.38 × 36.58 | Large rural homestead |

Orientation, road frontage, prevailing wind and solar path must be stated per
plot and must be visible in the design.

### 3.4 Kenyan climate and region
Spread the 20 across: Nairobi highlands · Central highlands / Mt Kenya (cool, wet) ·
Rift Valley (cool, windy) · Coastal (hot humid, salt air, monsoon) · Lake Victoria
basin (hot humid) · Western highlands (wet) · Semi-arid (Machakos, Kitui — hot, dry,
dusty) · Arid (Garissa — very hot, dry).

**ISSB behaves differently in each.** In the coastal belt it needs protection from
driving rain and salt. In semi-arid areas its thermal mass is an asset and it needs
shade and dust control. Say which climate strategy each design uses and why.

### 3.5 Style family and wall finish
Roughly **13 traditional / established** and **7 experimental**.

Traditional: pitched roof, deep verandah, central-spine or courtyard plan, separate
wet and dry kitchens, Swahili coastal (makuti, deep overhangs, coral-stone
detailing), highland stone-and-timber, rural homestead with detached utility block.

Experimental: flat or vaulted roof, **Nubian vault** (no timber formwork, no
roofing sheets), modular cluster, double-skin wall, solar chimney, earth-cooled
supply, ISSB-and-timber hybrid, courtyard-as-cooling-tower.

Wall finishes — mix these, and make the choice climate-justified:
**fair-faced / bare sealed ISSB** · cement-sand render and paint · earth or mud
plaster · lime plaster · bag-wash · textured roughcast · stone-clad feature panels ·
timber-clad or louvred feature panels · micro-cement.

Bare ISSB must be *designed for* — adequate roof overhang, a plinth, a DPC and a
silane/siloxane sealer. Do not show bare blocks where the detail would let them fail.

### 3.6 Deliverable for this phase
`docs/design-matrix.md` with one row per design: ID, slug, bedrooms, storeys, plot
size, region, climate, style family, wall finish, ISSB extent (full / partial, and
where it is not used), and one sentence on the design idea.

---

## 4. ISSB technical basis

> **Resolve this first, before you model anything.** You need the **exact block
> dimensions and profile from the machine the startup actually uses** — Makiga,
> Hydraform or other. Block length plus joint sets the coursing module, and the
> coursing module sets every wall length, every opening position, every floor
> plan and every shop drawing in all 20 designs. If the module is wrong, all 20
> designs are wrong.
>
> If the spec is not supplied, ask for it. Do not guess and do not proceed on an
> assumed block size. If you must proceed, state the assumed module prominently
> in `docs/decisions.md` and flag it as the single largest risk in the library.

### 4.1 What they are
Interlocking stabilised soil blocks are compressed soil-cement units made in a
manual or hydraulic press. Soil (usually lateritic or sandy loam) is mixed with
cement — commonly 5–10% by mass — moistened, pressed, and cured. The blocks
interlock by tongue-and-groove or a shaped profile, which reduces or eliminates
mortar in the bed joints. Kenyan machine makers include **Makiga** and
**Hydraform**; block profiles and dimensions differ between them.

### 4.2 What you must verify, not assume
**Every number in this list is indicative. Verify each one against a citable
source before it goes in a drawing, a document or a social post.**

- Cement content, by mass, for a given strength
- Wet compressive strength (commonly quoted 2–7 N/mm²; higher with more cement)
- Water absorption (commonly required below about 15%)
- Dry density and thermal conductivity
- Block dimensions and the resulting **coursing module**
- Curing duration and method (commonly 14–21 days, moist-cured)
- Suitability of a given soil (plasticity, clay fraction, silt) and the field tests
  used to check it
- Shrinkage and its effect on long walls
- Cost per square metre compared with machine-cut quarry stone and fired brick

**Sources to consult and cite:** the Kenya National Building Code 2024
(LN 47/2024); relevant KEBS standards; published ISSB research (Kenyatta
University, University of Nairobi, Makerere, and peer-reviewed journals);
manufacturer technical data from Makiga and Hydraform. Record each in
`docs/standards/` with a URL or full citation and the date you accessed it.

### 4.3 Design consequences you must honour
These are not optional — they are what makes an ISSB design buildable:

1. **Coursing module — and there is no mortar to absorb error.** The interlock
   sets alignment, so block length alone defines the module. Every wall must be
   set out to it. Openings, corners, returns and wall lengths must land exactly
   on the module, because unlike masonry you cannot take up a few millimetres in
   the bed joint. **Produce a block coursing drawing for at least one wall in
   every design** showing the setting-out.
2. **Never below ground, and the foundation is quarry stone.** The substructure
   is built in **ordinary machine-cut quarry stone**, not reinforced concrete —
   this is the operator's standard practice and it is the right detail, because
   quarry stone handles ground contact, moisture and bearing that ISSB cannot.
   The typical section is: quarry stone strip foundation → quarry stone or
   concrete plinth with a minimum 150 mm upstand above finished ground level →
   DPC → ISSB wall above. **No ISSB within 150 mm of finished ground level, ever.**
3. **Roof overhang.** Minimum 600 mm, more in driving-rain zones. State it.
4. **Ring beam.** A reinforced concrete ring beam at wall top, tied to the
   foundation, is required for lateral stability unless you can demonstrate
   otherwise.
5. **Movement.** Provide movement joints at spacing you can justify, and control
   cracking at openings with lintels and reinforcement.
6. **Services.** Chase and conduit routes must be planned before construction —
   chasing a cured ISSB wall is difficult and damages it. Show routes on the plan.
7. **Length of unsupported wall.** Check slenderness against the code and state
   the maximum you used.

### 4.4 What real ISSB construction looks like — design to this, not to a brochure

The following is taken from photographs of ISSB walls actually being built in
Kenya. It is the reality the designs must sit inside. Study it before you model
anything, because most ISSB renders fail by looking too clean.

**The wall face.**
- **The running joints are DRY.** There is no mortar between courses. The
  interlocking profile carries alignment, level and shear on its own, and this is
  true for the overwhelming majority of joints in the building. Cement appears
  only at **special junctions** — where ISSB meets a reinforced concrete column,
  a door or window frame, a lintel, the plinth, the ring beam, or any other
  material.
- This is the single most distinctive thing about the product and it must be
  **visible in every render**. A close-up of a dry interlocked joint, with the
  tongue-and-groove register reading clearly and no mortar line, is the strongest
  image the startup has. Do not smear a mortar joint over it.
- **Colour varies block to block**, from pale buff through sandy tan to deep
  terracotta. The same wall will show all of it. This comes from variable soil,
  variable cement content and variable curing, and it is the material's most
  recognisable characteristic.
- The face is **grainy and sandy**, with visible striations from the press.
  Edges are slightly eased, not crisp like a fired brick or a concrete block.
- Coursing is **hand-built**, and with no mortar there is nothing to correct a
  mis-set block. Expect it to read as accurately laid but not machine-perfect.

**The block itself.**
- The top face carries a **shaped register** — a tongue-and-groove or cup-and-cone
  interlock — not a plain rectangle.
- Blocks are **cured stacked in the open**, pyramid-fashion, on sheeting on bare
  ground, typically 14–21 days, before they are laid. Water is applied during
  curing.

**The site.**
- Rural and peri-urban plots: bare earth, a simple wire or block boundary, mature
  trees retained, minimal hard landscaping during construction.
- Construction is **hand-built with string lines**, minimal plant, no
  scaffolding tower.

**Consequence for the renders.** An ISSB wall rendered as a uniform, flat-coloured
surface — one texture tiled evenly, one colour — is the single most common way
these images give themselves away as CG, and it also misrepresents the product.
Build the material with **per-block colour variation** and per-block variation in
joint width, and show the grain at close range in the detail shots.

**Compound realism.** These are self-build budgets. Design compounds that a
Kenyan household can actually deliver: outdoor wash area, clothes line, watertank on a stand, kitchen garden, simple boundary wall and gate, a car port or
hardstanding. Avoid manicured lawns, imported paving and water features — they
undercut the value proposition the designs exist to make.

### 4.5 Soil selection — the operator's field rules

These are the operator's own rules, from production experience. Treat them as
authoritative and build the soil assessment around them.

**Suitable soils — use these:** murram · red soil (laterite) · loam subsoil.

**Clay is not suitable on its own.** It is too fine. It appears to bind well
while wet, which is what misleads people, but it loses too much mass as it dries
and the blocks crack. Clay must be **blended with coarse sand** before pressing.
Budget for the sand (see §4.6) and test the soil before committing to a site.

**Mix designs given by the operator:**

| Soil | Cement | Soil | Yield |
|---|---|---|---|
| Murram | 1 bag (50 kg) | 5 wheelbarrows | 100 blocks |
| Red soil | 1 bag (50 kg) | 4 wheelbarrows | 100 blocks *(confirm)* |

**Crew and output:** 4 people produce **350–500 blocks per day**, so **4 people
produce 350–500 blocks per day** on a hired machine, working a normal day.

**Consequence for the designs.** Because ISSB is pressed from soil won in the
foundation and landscaping excavation, the block-making is coupled to the
earthworks. Show this in the drawings and the buildability note: the soil is won
in a single operation that also digs the trenches and shapes the compound, and it
is stockpiled and covered before pressing. That is the cost model, not a detail.

### 4.6 Production economics — the numbers the marketing must respect

A runnable model is supplied alongside this brief as `issb_cost_model.py`. Copy
it into `tools/` and re-run it against confirmed local prices before quoting any
cost figure anywhere.

**Base case** — 100-block batch, soil won on site, 4 crew, 425 blocks/day:

| Line | KES per 100 | Share |
|---|---|---|
| Cement, 1 bag @ 750 | 750 | 26.6% |
| Cement transport @ 60/bag | 60 | 2.1% |
| Labour, 100 × 12 | 1,200 | 42.6% |
| Machine hire, 3,000/day | 706 | 25.1% |
| Consumables | 100 | 3.6% |
| **Total** | **2,816** | **100%** |
| **Per block** | **28.16** | |

**Four findings that must shape how these designs are presented:**

1. **This is a labour-and-machine business, not a materials business.** Labour
   plus machine hire is **68%** of the block cost. Cement is under 30%. Any
   marketing that leads on material cheapness is arguing the wrong case.

2. **Cement transport is a rounding error — 2.1%.** Even at KES 120 per bag
   delivered it is KES 1.20 per block. Do not build a cost story on transport.

3. **Site-won soil is the entire business model.** Importing soil takes the block
   from KES 28 to KES 43 — **+53%** at 50 km. And site-won soil avoids spoil
   removal, turning a disposal cost into a resource. **Never show a design whose
   economics depend on trucked-in soil.**

4. **The economics depend on the wall being left fair-faced — and the wall
   carries no jointing cement at all.** Per m² of finished wall face:

   | Wall | Units | Laying | Joints / finish | Total |
   |---|---|---|---|---|
   | ISSB 140 mm, dry-jointed, fair-faced | 728 | 89 | 25 | **KES 842** |
   | Quarry stone 200 mm, fair-faced | 364 | 500 | 180 | KES 1,044 |
   | Quarry stone 200 mm, rendered | 364 | 500 | 1,080 | **KES 1,944** |

   A **57% saving** against rendered quarry stone. Two things make it up, and
   both are structural to the product rather than cosmetic:

   - **No jointing cement.** Quarry stone masonry carries a full 1:4 mortar bed.
     The ISSB wall carries none at all — the only cement in the wall is the
     stabiliser inside the blocks.
   - **It is designed to be left bare.** Render the ISSB and most of the
     advantage disappears.

   **This is why §4.4 and §9.1 matter so much.** The design language must make
   exposed ISSB desirable rather than something you would want to cover up. A
   design that only works when rendered is a design that fails commercially.

**The KES 12 per block labour rate is sound.** At 425 blocks/day across 4 people
it pays **KES 1,275 per person per day**; at 350 it pays 1,050 and at 500 it pays
1,500. That is a fair semi-skilled rate for Kenya. Note the consequence, and
design the buildability note around it: **paying per block puts the output risk
on the crew.** If the machine breaks, the soil is wrong or it rains, they earn
nothing. Say so, and offer a guaranteed day rate as the alternative.

---

## 5. Phase 2 — Build the toolkit first

**Do not model 20 houses one at a time by hand.** Build a reusable library in
`lib/`, then drive all 20 from data files. Design 01 is your pilot; designs
02–20 must be substantially faster to produce than 01.

The toolkit should generate, from a small per-design parameter file:

- **Sitework** — levels, cut and fill, topsoil strip, access, boundary wall, gate,
  driveway, turning, parking, soakpit/septic, storm drainage, landscaping zones
- **Substructure** — strip or pad foundations, plinth, hardcore, blinding, DPM/DPC,
  foundation depth driven by the region's soil and climate
- **ISSB walling** — module-aware wall generator that takes a wall run, a height
  and a list of openings and emits correct coursing, lintels and returns
- **Superstructure** — ring beam, roof structure (pitched timber, flat slab,
  Nubian vault), roof covering
- **Openings** — doors, windows, sills, reveals, lintels, burglar-proofing
  (standard in Kenya — steel grilles or bars are the norm, not an exception)
- **Services** — water, drainage, electrical runs, solar, rainwater harvesting
- **Finishes** — floor, wall, ceiling per the design's schedule
- **Compound** — boundary wall, gate, hard and soft landscape, clothes-line,
  water tank on a stand, refuse, kitchen garden, outdoor wash area and outdoor
  kitchen (both very common in Kenyan compounds), car port or hardstanding,
  security light. Keep it deliverable at a self-build budget — see §4.4.
- **Cameras, lighting and render automation**

Every generator takes parameters and is idempotent. **The `.blend` is a build
artefact — it must be reconstructible from the script at any time.** Never make a
change in the file that is not in the script.

---

## 6. Per-design deliverables

### 6.1 Model
A complete Blender model, built from the toolkit, containing the house and the
compound, organised into named collections, with a stated coordinate convention
in metres anchored at a plot corner.

### 6.2 Drawings — one compiled PDF per design, plus the sheets
A3 landscape at 150 dpi. Minimum sheets:

| Sheet | Content |
|---|---|
| A01 | Cover, location and site key plan, drawing register, design data |
| A02 | Site plan / compound layout at 1:200 with levels, drainage and landscape |
| A03 | Foundation and plinth plan with details |
| A04 | Floor plan(s) with room names, areas, dimensions, grid, door and window tags |
| A05 | Roof plan with falls, outlets, downpipes and overhangs |
| A06 | Four elevations |
| A07 | Two sections (one long, one cross) with level datums |
| A08 | ISSB setting-out: block coursing, module diagram, opening alignment |
| A09 | Schedules: doors, windows, finishes, sanitary |
| A10 | Services: water and drainage layout; electrical layout |
| A11 | Details: foundation, plinth, DPC, ring beam, window and door reveals, roof edge, movement joint, wall junction |

### 6.3 Documents
- **Design report** — brief, site and climate analysis, design response, ISSB
  strategy, areas, compliance register against the Kenya National Building Code 2024
- **Specification** — preliminaries, sitework, foundations, ISSB walling
  (materials, mix, curing, workmanship, testing), roof, openings, finishes,
  services, external works, QA and handover
- **Bill of quantities** — measured items with quantities from the model and
  Kenyan market rates, elemental summary, contingency, professional fees, VAT
- **Buildability note** — how a small contractor actually builds this, in sequence,
  with the ISSB-specific risks called out

### 6.4 Visuals
Per design, minimum:

- 1 × exterior hero, 16:9
- 1 × exterior at a different time of day or angle
- 2 × interiors (living and a bedroom, or living and kitchen)
- 1 × compound or aerial showing the plot in context
- 2 × detail shots (ISSB texture and coursing; a junction or the plinth).
  **The ISSB detail shot is the most important image in the set** — it is what
  proves the product. Shoot it close, raking light, showing the grain, the thin
  joint and the block-to-block colour variation. See §4.4.
- Optional: 1 × construction-sequence or exploded image

Export every image at 16:9 (1920×1080), 4:5 (1080×1350), 1:1 (1080×1080), and
9:16 (1080×1920) for the hero and the compound shot.

### 6.5 Walkthrough
One clip per design, 10–15 seconds, 24 fps, vertical (1080×1920) plus a 16:9 crop.
Hook in the first frame, loop cleanly, on-screen captions, no voiceover.

### 6.6 Social
**Three posts per design — 60 in total.** One each for a different audience:

1. **Homeowner-facing** — the house as a home. Warmth, space, cost, lifestyle.
2. **Technical / professional** — ISSB performance, the coursing strategy, the
   climate response, a specific number.
3. **Brand / startup** — the mission, why soil instead of fired brick, the
   environmental case, the local labour and materials story.

Each post: platform (choose the best fit), the exact asset files to attach, the
copy ready to paste, hashtags, alt text, and a one-line note on why it works.
Write for Instagram, WhatsApp status, X, LinkedIn or YouTube as the design suits.

---

## 7. Verification protocol — non-negotiable

Everything ships only after these pass. Record results in `docs/decisions.md`.

### 7.1 Geometry truth
- **A window object is not a window.** After generating openings, **ray-cast from
  inside every habitable room** and confirm the ray reaches outside through an
  opening rather than stopping on a wall. Log any room that fails.
- Confirm every wall has a plinth under it, a DPC, and a ring beam over it.
- Confirm no ISSB is below ground or within 150 mm of finished ground level.
- Confirm roof overhangs meet the stated minimum and that no opening is exposed
  to driving rain without protection.

### 7.2 Numeric truth
- **Compute every area, dimension and compliance figure from the exported
  geometry — never from a typed schedule.** Schedules must be generated, not
  written.
- **Check every dimension chain closes** on the plot boundary, in both directions.
- Diff the drawings against the geometry and report every mismatch.
- The gross floor area definition must be **stated explicitly** on the drawing,
  and the same definition used in the report, the specification and the BOQ.

### 7.3 Documentation integrity
- After compiling any multi-page PDF, **verify the page count from the file**,
  not from the generator's log.
- Confirm no partial regeneration can overwrite a complete deliverable.
- Open every generated DOCX/XLSX/PDF and confirm it is structurally valid.

### 7.4 Claims
`docs/claims-register.md` lists **every factual claim** made in any drawing,
document or social post, with:

| Claim | Value | Source | Verified? | Notes |
|---|---|---|---|---|

Anything unverifiable is either removed or explicitly labelled as indicative.
**No performance claim ships without a source.**

### 7.5 Honesty
These are **proposed designs, not built houses.** Never present a render as a
photograph, never imply a client or a completed build, and never state a
performance figure the design has not demonstrated.

---

## 8. Performance and pacing

- Benchmark before committing to an engine. Record the numbers.
- **If a render ever stalls** — CPU time crawling, no progress — stop, diagnose,
  and record the cause. Known triggers in EEVEE: area lights combined with
  raytracing at high resolution, and alpha-cut (dithered) geometry casting
  shadows. Work around them rather than retrying.
- Render in paced batches with a cooldown between batches. This machine may be
  thermally limited.
- **Before committing to any downloaded model, check its polygon count.** A
  photogrammetry tree can carry millions of triangles and will not render in a
  reasonable time. Prefer procedural foliage (alpha-cut cards) at this scale.
- Delete intermediate frame sequences after encoding video. Keep the MP4.

---

## 9. Assets

Prefer CC0 sources (Poly Haven for HDRIs and PBR textures). Fetch by script into
`assets/`, never by hand. Record what was downloaded and its licence. If the
network is unavailable, generate procedurally and say so in the README.

Map PBR textures with **true-scale box-projected UVs**, not 3D object coordinates
— axis-aligned walls collapse 3D coordinates to a line and produce vertical
smearing.

### 9.1 The ISSB material

Do not use a single tiled texture for ISSB walling. Build a material that varies
**per block**: colour drawn from a controlled palette (buff → tan → terracotta),
a grainy, sandy surface with press striations, and — critically — **a dry
interlocked joint, not a mortar line**. Model the tongue-and-groove register so
it reads at close range. Drive the variation from an object- or UV-space random
so it survives changing the camera. This is a deliverable in its own right — it
will be reused across all 20 designs, so build it once, in `lib/`, and tune it
against the photographs before mass-producing renders.

A flat, uniformly coloured ISSB wall is a failed render. An ISSB wall with a
mortar joint drawn over the interlock is a worse one — it hides the product's
only real differentiator. See §4.4.

---

## 10. Housekeeping

- No scratch directories, no iteration logs left behind, no orphaned assets.
- One status table in `README.md`: design ID, modelled, drawn, documented,
  rendered, video, social, verified — with a tick or a dash.
- The repository must be reproducible from scripts alone. A reader should be able
  to regenerate any deliverable from the README.
- Delete superseded work or move it to an explicit `archive/`.

---

## 11. Definition of done

The library is complete when:

1. 20 designs exist, all rows of `docs/design-matrix.md` filled, no two alike
   across bedrooms, plot, climate, style and finish.
2. Every design has model, drawings, documents, renders, walkthrough and 3 social
   posts — the full §6 list.
3. Every technical claim is in the claims register with a source, or is labelled
   indicative.
4. Every design passes the §7 verification protocol, with results recorded.
5. `README.md` status table is complete and the repository is reproducible from
   scripts.
6. A single master pitch document exists: one presentation introducing the startup
   and the 20 designs, drawing on the best material from all of them.

---

## 12. Working order

1. Phase 0 reconnaissance → `docs/decisions.md`
2. ISSB research → `docs/standards/` (verified, cited)
3. Design matrix → `docs/design-matrix.md` (locked)
4. Toolkit → `lib/`
5. **Design 01 end to end** — full deliverables, full verification. This is the
   template. Review your own output critically before scaling.
6. Designs 02–20, in batches of 3–4, running the verification protocol on each
   batch before starting the next.
7. Master pitch document.
8. Final housekeeping and README.

Report progress at the end of each batch. If a design fails verification, fix it
before moving on — do not accumulate defects.
