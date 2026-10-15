# Courtyard Apartments — 50 × 100 ft plot, Nairobi

A five-storey courtyard apartment building (GF + L1–L4, 13 homes, 9 basement
parking bays) on a 15.24 m × 30.48 m plot, modelled in Blender 5.2, rendered
photorealistically, and documented to construction-issue standard.

---

## Deliverables

| What | Where |
|---|---|
| **8 photoreal renders, all social formats** | [`render/delivery/`](render/delivery) |
| **2 short films** | [`render/videos/`](render/videos) |
| **Drawing set, 8 sheets** | [`docs/drawings/`](docs/drawings) · [Drawing Set Review](<docs/drawings/Drawing Set Review.md>) |
| **Priced bill of quantities** | [`docs/costing/`](docs/costing) |
| **Specification** | [`docs/specification/`](docs/specification) |
| **Social media pack** | [`docs/social/`](docs/social) |
| **Post copy — 3 variants per platform** | [Post Variants](<docs/social/Post Variants - 3 per platform.md>) · [DOCX](<docs/social/Post Variants - 3 per platform.docx>) |
| **A1 presentation board** | [`docs/presentation/`](docs/presentation) |
| Model QA and render notes | [Model QA & Render Notes](<docs/Model QA & Render Notes.md>) |
| Toolchain assessment (add-ons, constraints) | [Render Toolchain Assessment](<docs/Render Toolchain Assessment.md>) |
| 3-D model | [`Courtyard Apartments 50x100 v3.blend`](<Courtyard Apartments 50x100 v3.blend>) |

### The eight renders

| # | Shot | Rig | Subject |
|---|---|---|---|
| 01 | Courtyard Garden | high afternoon, 231°/73° | Eye level on the podium — feature tree, lawn, colonnade, stacked balconies |
| 02 | Courtyard Void Aerial | high afternoon | Above the void — the whole garden and all four balcony tiers |
| 03 | Street Facade | golden hour, 214°/11° | The west elevation, timber fins, portal, guardhouse, gate |
| 04 | Living Room L3 | south-south-east, 168°/64° | Inside a home, looking through the 3.5 m glazed wall |
| 05 | L3 Gallery Overlook | high afternoon | Over the balustrade into the courtyard |
| 06 | Roof Pergola Sunset | golden hour, 262°/11° | The roof garden, planters and tanks against the sunset |
| 07 | **Twilight Street** *(new)* | blue hour, night HDRI | The building lit from within — the highest-engagement frame |
| 08 | **Aerial Hero** *(new)* | high sun, 248°/44° | The whole building and its courtyard in context |

Every shot is exported as **16:9 (1920×1080)**, **4:5 (1080×1350)** for the
Instagram feed and carousels, **1:1 (1080×1080)**, and — for shots 01, 03, 06
and 07 — **9:16 (1080×1920)** for Reels, Shorts and WhatsApp status.

### The two films

Both are 10 seconds at 24 fps, rendered natively vertical (810 × 1440) for the
platforms that reward it, with a 16:9 centre-crop for LinkedIn and YouTube.

| File | Content |
|---|---|
| `Courtyard Walkthrough.mp4` / `_16x9.mp4` | Street → gate → up through the courtyard → roof garden; loops back to the opening frame |
| `Courtyard Orbit.mp4` / `_16x9.mp4` | A rising arc around the building, settling on the courtyard and roof garden |

Both are cut for the platforms that actually reward video: Instagram Reels and
YouTube Shorts rank on watch completion, so they are short, hook in the first
frame and loop cleanly. See the [social pack](docs/social) for the shot-by-shot
structure and on-screen captions.

---

## Re-running anything

Blender is at `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
Run from the project root. **Assets must be present first** — see §Assets below.

```powershell
$B = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
$PY = "C:\Users\Admin\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
$M = "Courtyard Apartments 50x100 v3.blend"

# 1. the eight stills  (1920x1080, ~20 min)
& $B -b $M --python scripts\render_v4.py -- mode=stills resx=1920 resy=1080 `
      samples=80 quality=final out=render\v4

# 2. photographic finishing + every social crop   (~1 min)
& $PY scripts\finish.py --src render\v4 --dst render\delivery

# 3. a film   (240 frames, 810x1440, ~1.5-2 h) -- paced in bursts of 20
& $B -b $M --python scripts\render_v4.py -- mode=video video=fly resx=810 resy=1440 `
      samples=20 quality=draft frames=240 batch=20 cooldown=15 out=render\video_frames
& $PY scripts\encode_video.py --src render\video_frames\video_fly --fps 24 `
      --out "render\videos\Courtyard Walkthrough.mp4"

# 4. drawings, costing, specification, social pack
& $B -b $M --python scripts\dump_geometry.py
& $PY scripts\make_drawings.py
& $PY scripts\make_boq.py
& $PY scripts\make_spec.py
& $PY scripts\make_social_pack.py
```

`render_v4.py` rebuilds the whole presentation scene from the saved model on
every run — materials, HDRI lighting, site context, planting, window openings
and cameras. **The `.blend` on disk is never modified.**

Useful options: `shots=01,03` to render a subset, `quality=fast|draft|final`,
`skymul` / `sunmul` / `expadd` / `baseexp` for lighting sweeps, `batch` and
`cooldown` to pace the machine.

---

## Assets

> **Cloning this repository?** The `assets/` folder is **not** committed — it is
> 227 MB of CC0 material that any script can re-download. Fetch it before running
> anything that renders:
>
> ```powershell
> & $PY scripts\assets\fetch_assets.py --all
> & $PY scripts\assets\fetch_model_textures.py potted_plant_02
> & $PY scripts\assets\make_leaf_atlas.py
> ```
>
> Everything else needed — the model, the scripts, the drawings, the documents
> and the finished renders in every social format — is in the repository.

All assets are **CC0 (public domain)** from [Poly Haven](https://polyhaven.com/license),
fetched by script. Re-fetch with:

```powershell
& $PY scripts\assets\fetch_assets.py --all
& $PY scripts\assets\fetch_model_textures.py potted_plant_02
& $PY scripts\assets\make_leaf_atlas.py
```

| Folder | Contents |
|---|---|
| `assets/hdri/` | 5 × 4K HDRI skies — day, two golden hours, twilight, overcast |
| `assets/textures/` | 11 × 2K PBR sets (diffuse + normal + packed AO/rough/metal) |
| `assets/models/` | `potted_plant_02` and its 15 texture maps |
| `assets/generated/` | Procedurally drawn alpha leaf-cluster atlases |

**Note for re-running:** HTTPS is unavailable to PowerShell in this environment
(Windows `schannel` cannot acquire credentials inside the sandbox), but works
normally from the bundled Python. All downloads therefore go through
`scripts/assets/*.py`. See the [toolchain assessment](<docs/Render Toolchain Assessment.md>) §4.

---

## How the render pipeline works

`scripts/render_v4.py` runs in stages:

1. **Hide annotations** — compliance planes, text labels, north arrows and working
   cameras are excluded from render.
2. **Materials** — every surface is rebuilt on a real CC0 PBR texture set
   (diffuse + normal + packed AO/roughness/metallic), tinted to the design palette,
   with a large-scale noise break-up so tiling never reads as wallpaper.
3. **Box-projected UVs** — per-face projection in object-space metres. This
   replaced 3-D object coordinates, which collapse to a line on any axis-aligned
   wall and produced vertical smearing stripes.
4. **Open the glazed walls** — see the QA note below. 43 glazing and door panels
   are booleaned out of the walls they sit in (the geometry export records 48
   openings in total — see [Drawing Set Review](<docs/drawings/Drawing Set Review.md>) §2.4).
5. **Dress the furniture** — 37 block furniture objects get plausible fabric,
   linen and wood materials; internal ISSB partitions get a plaster finish.
6. **Site context** — carriageway, kerbs, footways, lane markings, a zebra
   crossing and neighbouring massing, so the building sits in a street.
7. **Planting** — procedural alpha leaf cards scattered through the canopy volumes
   (1,515 cards, ~3,000 triangles) replace the low-poly blobs, plus a real
   `potted_plant_02` model in the planters.
8. **Detail** — bevelled structural arrises, glazing reveal frames, vertical-bar
   balustrade infill to s.17, downpipes, AC condensers and three street cars. All
   detail is joined down to 6 objects so the depsgraph stays cheap.
9. **Lighting** — a real HDRI sky per shot, with a Sun lamp matched to the
   chosen bearing and elevation to cast the shadows.
10. **Cameras** — composed from the measured model, not estimated.

Then `scripts/finish.py` applies the photographic pass: highlight bloom and
halation, lateral chromatic aberration, an unsharp mask, a filmic S-curve with
split toning, a vignette and luminance-weighted film grain — and writes every
social aspect ratio.

### Lighting rigs

| Rig | Sun | Used by |
|---|---|---|
| `courtyard` | 231° / 73° — high afternoon from the SSW | 01, 02, 05 |
| `golden` | 214–262° / 11° — low WSW sun | 03, 06 |
| `interior` | 168° / 64° — south-south-east | 04 |
| `twilight` | 250° / 4° with practicals only | 07 |
| `aerial` | 248° / 44° | 08 |

The courtyard elevation is not arbitrary. The courtyard is a 7.1 m wide, 15 m
deep slot, so direct sun reaches its floor only above about 65°
(`tan 65° ≈ 15.3 / 7.1`). At 73° the floor is lit except for the shadow band
under the south gallery — which is also why the courtyard is comfortable.

### Coordinate convention

```
X:   0 = NORTH boundary ......... 15.24 = SOUTH boundary
Y:   0 = WEST street / gate ..... 30.48 = EAST rear
Z:   0 = street, 0.90 = GF podium, 4.20/7.20/10.20/13.20 = L1–L4, 16.20 = roof

Courtyard void   X 6.30–13.44, Y 7.30–23.00    Lawn  X 7.20–12.50, Y 8.50–19.50
Feature tree      X 7.76–11.94, Y 12.30–16.70  Canopy top Z 8.10
Colonnade         X 3.60–6.58,  Y 5.20–23.00   Floor Z 0.91
L3 living room    X 2.55–6.15,  Y 7.30–13.50   Glazing X 6.22–6.30, Y 8.50–12.00, Z 10.20–12.60
Roof pergola      X 0.80–5.60,  Y 10.10–15.88  Z 16.20–19.10
```

`scripts/diagnostics/` holds the probes these numbers came from: `query3.py`
reports interior clearances, `diag_rays.py` reports what each camera actually
hits, `bench.py` benchmarks the engine.

---

## Documentation produced

**Drawing set** — `docs/drawings/`, A1 landscape, 150 dpi, 8 sheets plus a
multi-page PDF. Cover and key plan with a drawing register; basement, ground,
typical upper and roof plans drawn from **true section cuts through the model**
(with poché, grid lines A–G / 1–8, dimension chains, room labels and areas);
two sections with level datums; four elevations; schedules and a compliance
summary.

**Costing** — `docs/costing/`, a five-sheet workbook: elemental summary ascending
to a contract sum, ~90 measured items with quantities and rates, rate build-ups
for four key items, a 26-month cash flow, and a basis-of-estimate sheet.

> **Known defect.** The cost plan applies a gross floor area of 1,363 m², which
> is an unstated measurement basis (enclosed area excluding the courtyard void,
> colonnade and open galleries). The model's slab plates total **1,670.7 m²**
> above ground. At that figure the works rate is **KES 197,200/m²**, not the
> KES 241,700/m² quoted below. The basement figure of 620 m² is also wrong — the
> plot is 464.5 m², so the basement cannot exceed that. See
> [Drawing Set Review](<docs/drawings/Drawing Set Review.md>) §2.1 and §1.3.

**Specification** — `docs/specification/`, 19 sections from preliminaries through
substructure, concrete, reinforcement, masonry, waterproofing, joinery, metalwork,
glazing, finishes, MEP, fire, lift, renewables, external works and handover, with
test schedules, door/window/finishes schedules and the compliance register.

**Social pack** — `docs/social/`, the engagement research, an asset map, and
ready-to-post copy for a 7-slide Instagram carousel, a Reel/Short, WhatsApp
status, an X thread, a LinkedIn document post and YouTube, with hashtags, alt
text and a posting cadence.

All three Office documents were generated with `python-docx` / `openpyxl` and
passed the structural checker.

---

## Key findings

### Machine time used

| Stage | Cost |
|---|---|
| 8 stills, 1920 × 1080, 80 samples | 20 min |
| Video 1, 240 frames at 810 × 1440 | 83 min |
| Video 2, 240 frames at 810 × 1440 | 60 min |
| Finishing, encoding, drawings, documents | ~10 min |
| **Total** | **~2 h 55 min** |

All rendering ran in paced bursts (20 frames, then a 15 s rest) to keep this
2-core CPU from overheating. No render was lost to a thermal or memory failure.

### 1. The model has no window openings

Every glazing panel in the saved model sits **inside** a solid wall box. A ray
cast from inside the L3 living room stopped on the wall at 4.38 m. All 43 glazing
and door panels were affected, so no room had a daylight opening at all.

This matters beyond the renders: the v3.1 report records s.143(2) as
"FIXED — now PASS" on the strength of widening the glazing from 3.0 m to 3.5 m,
but a panel inside a solid wall delivers no window area. **s.143(1), s.143(2) and
the s.137 zone-of-space calculation should be treated as NOT CHECKED** until the
openings exist in the model. The render pipeline cuts them at runtime; the fix
still needs to go into `scripts/build_courtyard_apartments_v3.py`.

Full write-up in the [QA notes](<docs/Model QA & Render Notes.md>) §1.

### 2. The 1.10 m balustrade hides the courtyard floor

s.17 requires ≥ 1.00 m and the model uses 1.10 m. With an eye at 1.6 m, a person
standing normally behind the balustrade can see below it only at angles shallower
than `atan(0.5 / d)` — about 30° at 0.85 m back. The galleries therefore give
**no visual surveillance of the courtyard floor**, which is worth knowing for the
passive-security and child-safety argument for a shared courtyard. Full note in
the QA document §5.

### 3. This machine cannot use photogrammetry-grade vegetation

`jacaranda_tree` (4.0 M triangles) and `tree_small_02` (1.6 M triangles) were
downloaded, measured and rejected. A procedural alpha-card canopy replaced them at
~3,000 triangles and looks better at this scale. Both models were deleted to
reclaim 232 MB.

### 4. Two EEVEE deadlocks, both diagnosed and worked around

- **Area lights with raytracing at high resolution** stall the renderer
  indefinitely (CPU crawls at ~1 s per minute). Interior fill now uses shadowless
  point lights with the specular lobe off.
- **Alpha-cut geometry casting shadows** deadlocks identically. The leaf cards are
  excluded from the shadow pass; the opaque canopy core still casts.

Depth of field was dropped for the same family of reasons. Details in the
[toolchain assessment](<docs/Render Toolchain Assessment.md>) §4.

---

## Project layout

```
.
├─ Courtyard Apartments 50x100 v3.blend     primary model (unmodified)
├─ Basement Parking 50x100 v1.blend
├─ assets/                                  CC0 HDRIs, PBR textures, models, atlases
├─ docs/
│  ├─ drawings/                             S01-S08 sheets + PDF + geometry.json
│  ├─ costing/                              priced bill of quantities
│  ├─ specification/                        specification
│  ├─ social/                               social media pack
│  ├─ design/                               original reports and design brief
│  ├─ Model QA & Render Notes.md
│  └─ Render Toolchain Assessment.md
├─ reference/                               concept zoning diagram
├─ render/
│  ├─ delivery/                             ← the assets to post
│  ├─ v4/                                   1920x1080 PNG masters
│  ├─ video_frames/                         (transient) PNG sequences, deleted after encoding
│  ├─ videos/                               encoded MP4s
│  ├─ basement/, walkthrough/               earlier basement and walkthrough work
│  ├─ archive/                              superseded renders (v2 and v3 passes)
│  └─ logs/                                 every render and diagnostic log
└─ scripts/
   ├─ render_v4.py, finish.py               stills pipeline + finishing
   ├─ encode_video.py                       video post and encoding
   ├─ dump_geometry.py, make_drawings.py    drawing production
   ├─ make_boq.py, make_spec.py, make_social_pack.py
   ├─ render_elevations.py                  orthographic clay elevations
   ├─ assets/                               asset fetchers, leaf atlas generator
   ├─ diagnostics/                          scene probes and benchmarks
   └─ archive/                              superseded render scripts
```

The `.blend` files stay at the root because several scripts reference that path.

---

## Open items

1. **Cut the window openings into the model** — highest priority, see finding 1.
2. **Fix the gross floor area basis.** The drawings, cost plan and specification
   quote 1,363 m²; the model measures 1,670.7 m² of slab plate. A 23% swing in
   the works rate. Decide the definition, state it, apply it everywhere.
3. **Reconcile the specification schedules with the model.** The spec lists 119
   windows and 109 doors; the model contains 28 glazing panels and 20 door
   openings. See [Drawing Set Review](<docs/drawings/Drawing Set Review.md>) §2.2.
4. **Resolve s.143(1).** Modelled glazing is 7.2% of floor area against a 10%
   requirement. Either the model is missing most of its glazing or the scheme
   fails the clause. §2.3.
5. **Finish the roof plan** — falls, outlets, downpipe positions and the
   courtyard void are not yet shown on S05. §2.5.
6. **s.18 and s.19 conflicts** — shop and guard house on the street boundary and
   walls on both side boundaries need a county relaxation. Unchanged.
7. **Fire strategy** — the single protected stair, ramp as second basement escape
   and the 60-minute ratings must be confirmed by a fire engineer. Nothing here is
   a fire-engineered design.
8. **Structural items** — podium drop panels, balcony cantilever tendons, the
   courtyard tree planter and the roof-planted areas are all provisional pending
   the structural engineer.
9. **Walkthrough** — 42 frames of the earlier 720-frame walkthrough remain in
   `render/walkthrough/`; the two new films supersede it.
10. **Elevations are schematic.** The painter's-algorithm elevations on sheet S07
    are tonal massing, not hidden-line drawings. `scripts/render_elevations.py`
    will produce proper orthographic clay elevations in Blender, but it was not run
   because it competes with the video render for this 2-core CPU.
11. **Costs are indicative.** Nairobi market rates for Q4 2026, to be confirmed by
    competitive tender. Land, finance and county charges are excluded.
