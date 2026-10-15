# Render Toolchain Assessment

What the industry uses, what is free, what was evaluated for this project, and
what was actually used — with the reasons.

---

## 1. The free add-ons worth knowing about

| Add-on | Cost | What it does | Would it help here? |
|---|---|---|---|
| **Poly Haven add-on** | Free (CC0 assets) | Browses and imports Poly Haven HDRIs, PBR textures and models straight into Blender | **Yes — and it was used, indirectly.** The assets were pulled through the same Poly Haven API the add-on calls. See §3. |
| **BlenderKit** | Free tier | Asset library: models, materials, HDRIs, some scanned | Partly. Its free architectural props (furniture, cars, people) would help most. Requires an account and writes a cache to `%APPDATA%`. |
| **Gaffer** | Free (GitHub) | Batch-manages lights, exposure, collections, render settings across shots | Marginal. This pipeline already drives per-shot rigs from a shot table (`SHOTS` in `render_v4.py`), which is the same job. |
| **Photographer** | Free version | Physical camera and light units, real exposure/f-stop/ISO, bokeh | Marginal. Physical exposure and sun angle are already set explicitly; the free version's best feature is the light UI. |
| **Light Wrangler** | Free version | Faster light placement and shaping | Marginal — lighting here is a sun plus an HDRI, not a multi-light rig. |
| **Node Wrangler** | Bundled with Blender | Node graph conveniences (preview, mix, UV) | Convenience only; does not change output. |
| **EasyHDRI / HDRI Maker** | Free | Quick environment switching | Already covered: the pipeline swaps four HDRIs per shot. |
| **Extra Lights / LightLab** | Free | Additional photometric light types | Not needed; area lights cause a renderer hang on this machine (see §4). |

**Assessment.** For photorealism the add-ons that genuinely matter are the
**asset libraries** — Poly Haven and BlenderKit — not the lighting utilities.
Real HDRI skies and real photographed PBR textures are what move an image from
"CG" to "photographic"; every lighting helper is a workflow convenience on top
of that. That is what this project went and got.

---

## 2. The paid tools the top of the industry actually uses

Listed for completeness and future budgeting, not as a recommendation to buy:

| Tool | Typical use |
|---|---|
| **3ds Max + Corona / V-Ray** | Still the commercial archviz standard in most studios |
| **Chaos Vantage / Enscape / D5 Render** | Real-time GPU visualisation, instant client walkthroughs |
| **Unreal Engine 5** | Interactive and cinematic architectural presentation |
| **SpeedTree / GrowFX / Botaniq / Scatter** | Vegetation that reads as real |
| **Quixel Megascans / Poliigon** | Scanned surfaces and props |
| **Forest Pack / RailClone** | Large-scale scattering and parametric detail |
| **Cycles (Blender, free)** | The free path-traced renderer that matches V-Ray closely |

The honest position: the difference between this project's output and a
top-tier studio render is **not the software**. It is (a) a GPU, (b) scanned
vegetation and props, and (c) the time budget to dress every scene. All three
are addressable here without buying anything.

---

## 3. What was actually used

- **Skies:** four CC0 Poly Haven 4K HDRIs — `kloofendal_48d_partly_cloudy_puresky`
  (day), `belfast_sunset_puresky` and `kloppenheim_06_puresky` (golden hour),
  `satara_night` (twilight), `overcast_soil_puresky` (interior light).
- **Surfaces:** eleven CC0 2K PBR sets with diffuse, normal and packed
  AO/roughness/metallic maps — concrete, worn concrete, white plaster, red brick,
  oak veneer, weathered planks, brick paving, pavement, asphalt, leafy grass,
  metal plate. Mapped with true box-projected UVs at real-world scale.
- **Models:** `potted_plant_02` (62 k triangles) for the planters.
- **Foliage:** generated — alpha-cut leaf-cluster cards drawn procedurally
  (see `scripts/assets/make_leaf_atlas.py`) and scattered through the canopy
  volumes. 1,515 cards cost 3,000 triangles and read as a real tree.

### Why the Poly Haven trees were rejected

`jacaranda_tree` (4.0 M triangles) and `tree_small_02` (1.6 M triangles) are
photogrammetry-grade assets. On a CPU-only 2-core machine they are not merely
slow, they are unusable — the depsgraph evaluation and BVH build alone would
exceed the memory and the session budget. Both were downloaded, measured, and
deleted to reclaim 232 MB. The procedural card system replaced them and in
practice looks better at this render scale, because its silhouette is
controllable.

---

## 4. Environment constraints discovered

1. **No GPU.** The machine reports CPU only (AMD Athlon Gold 3150U, no
   CUDA/OptiX/HIP device). Cycles was benchmarked at ~441 s per 1080p frame
   against EEVEE's ~40 s, so EEVEE Next was used throughout. The design brief
   also specifies EEVEE.

2. **HTTPS is unavailable to the shell, but available to Python.** Windows
   `schannel` cannot acquire credentials inside the sandbox
   (`SEC_E_NO_CREDENTIALS`), so `Invoke-WebRequest` and `curl.exe` both fail on
   any HTTPS URL. The bundled Python uses OpenSSL instead and reaches the
   network normally. Every asset download therefore runs through
   `scripts/assets/*.py`, not through PowerShell.

3. **Add-on installation is blocked by the sandbox.** Blender installs add-ons
   by unpacking into `%APPDATA%\Blender Foundation\...`, which is outside the
   writable workspace — the load attempt fails with `PermissionError [WinError 5]`.
   Add-ons can only be enabled in the Blender GUI, or by pointing
   `BLENDER_USER_SCRIPTS` at a workspace folder. Given §1, no add-on was worth
   that workaround for this project.

4. **EEVEE deadlocks on two specific things.** Both were hit and diagnosed:
   - **Area lights with raytracing at high resolution.** The render stalls with
     CPU time crawling at ~1 s per minute, indefinitely. Interior fill now uses
     shadowless point lights with the specular lobe disabled.
   - **Alpha-cut (dithered) geometry casting shadows.** Adding leaf cards
     deadlocked the renderer in exactly the same way. Cards are now excluded
     from the shadow pass; the opaque canopy core underneath still casts.
   - Depth of field was dropped for the same family of reasons.

5. **Disk.** 17 GB free on C:. The available asset store was capped at what the
   project can use; total footprint is ~400 MB including all renders.

---

## 5. What would lift this output further, in priority order

1. **A GPU.** Cycles at 100+ samples with real caustics, real glass refraction
   and physically accurate light transport is the single biggest step. It also
   removes constraint 4 entirely.
2. **Scanned vegetation.** A real jacaranda and a shrub library, with the
   graphics memory to render them.
3. **Scanned props.** Cars, street furniture, people, bicycles. Human-scale
   objects do more for believability than any shader.
4. **Megascans/Poliigon-grade surfaces** at 4K, with displacement rather than
   bump.
5. **Time.** The renders here took about 20 minutes of machine time in total.
   A studio would spend that on one image.
