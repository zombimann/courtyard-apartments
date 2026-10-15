# Concept Design & Architectural Visualization Report: Basement Parking Level
**Location:** Nairobi, Kenya | **Plot Dimensions:** $50\text{ ft} \times 100\text{ ft}$ ($15.24\text{ m} \times 30.48\text{ m}$, $464.52\text{ m}^2$)  
**Governing Standard:** Kenya National Building Code 2024 (LN 47/2024)  
**Deliverable Project File:** [`Basement Parking 50x100 v1.blend`](../../Basement%20Parking%2050x100%20v1.blend)  
**Scripts:** [`build_basement_parking.py`](../../build_basement_parking.py) & [`enhance_and_animate.py`](../../enhance_and_animate.py)

---

## 1. Cinematic Renders (1920 × 1080 EEVEE)

````carousel
![Still 1: Ramp Entrance with Soft Daylight & Hazard Kerbs](still_1_ramp_entrance.png)
<!-- slide -->
![Still 2: Central Aisle Perspective with Overhead LED Lights & Parked Vehicles](still_2_aisle_view.png)
<!-- slide -->
![Still 3: Aerial Structural Cut-Away with Illuminated Garage Interior](still_3_aerial_cutaway.png)
<!-- slide -->
![Basement Level Top Orthographic Floor Plan](basement_top_plan.png)
````

---

## 2. Kenya National Building Code 2024 (LN 47/2024) Compliance Audit

| Requirement & Code Clause | Mandated Standard | Value Designed / Used | Status | Notes & Verification |
| :--- | :--- | :--- | :---: | :--- |
| **Parking Bay Dimensions**<br>*(Second Sched. Fig. 1c)* | Min $2.4\text{ m} \times 4.6\text{ m}$ (head-on 90°) | **$2.50\text{ m} \times 5.00\text{ m}$** | **PASS** | Upgraded to generous $2.5 \times 5.0\text{ m}$ stalls with $100\text{ mm}$ thermoplastic lines and wheel stops. |
| **Driving Aisle Width**<br>*(Second Sched. Fig. 1c)* | Min $6.10\text{ m}$ clear aisle | **$6.10\text{ m}$ clear** | **PASS** | Continuous unobstructed aisle from ramp terminal to rear court. |
| **Ramp Road Approach**<br>*(Section 42(a))* | Slope $\le 1:25$ ($4.0\%$) within $5.0\text{ m}$ of road | **$1:25$ ($4.0\%$)** ($Y = 0 \text{ to } 5.0\text{ m}$) | **PASS** | Drop of $0.20\text{ m}$ over first $5\text{ m}$ prevents vehicle grounding and ensures driver line-of-sight. |
| **Ramp Maximum Slope**<br>*(Section 44)* | Max gradient $12.5\%$ ($1:8$) | **$12.50\%$ ($1:8$)** | **PASS** | Main ramp segment ($Y = 7.5 \text{ to } 27.5\text{ m}$) strictly capped at $12.5\%$. |
| **Ramp Anti-Scrape Transitions**<br>*(Section 44 best practice)* | $2.0 \text{ to } 3.0\text{ m}$ slope transitions (~$6\%$) | **$2.50\text{ m}$ top ($6.4\%$), $2.30\text{ m}$ bottom ($6.5\%$)** | **PASS** | Parabolic / blended grade changes eliminate vehicle front overhang and exhaust scraping. |
| **Ramp Clear Width**<br>*(Section 44)* | One-way width $\ge 3.00\text{ m}$ | **$3.20\text{ m}$ clear** | **PASS** | Width between retaining wall and barrier is $3.20\text{ m}$ (strip is $3.45\text{ m}$ total). |
| **Vehicle Barriers / Kerb**<br>*(Section 41)* | Height $375\text{ mm} \text{ to } 610\text{ mm}$ at any edge | **$450\text{ mm}$ high RC kerb** | **PASS** | Continuous yellow-black hazard chevron barrier along ramp edge ($X = 3.50 \text{ to } 3.75\text{ m}$). |
| **Pedestrian Guardrails**<br>*(Section 39(2))* | Guardrails in parking, none on vehicle-only ramp | **Dedicated barriers & kerbs** | **PASS** | Vehicle-only ramp excluded from pedestrian access; barrier protects parking area. |
| **Means of Escape**<br>*(Section 400)* | 2 escape stairs, OR 1 enclosed stair + vehicle ramp | **1 Enclosed Stair + 1 Ramp** | **PASS** | Enclosed $2.45\text{ m}$ stairwell with $1.20\text{ m}$ flights + vehicle ramp providing redundant escape. |
| **Passenger Lift Shaft**<br>*(Section 400 / KS ISO 21542)* | Sized for building | **$2.00\text{ m} \times 2.00\text{ m}$ internal** | **PASS** | Enclosed RC shaft at front right lobby, continuing up to floors 1–5. |
| **Pedestrian Safety Route**<br>*(Section 201)* | Route from stair/lift must not cross vehicle path unprotected | **$1.20\text{ m}$ painted & kerbed walkway** | **PASS** | Protected walkway connects Core exit door directly to Accessible Bay transfer zone. |
| **Accessible Parking**<br>*(Section 353 / KS ISO 21542)* | $\ge 1$ bay near lift, $3.6\text{ m}$ wide incl. transfer zone | **$3.60\text{ m}$ wide ($2.4\text{ m} + 1.2\text{ m}$)** | **PASS** | Bay 1 located right at lift lobby; blue finish, wheelchair graphics, and hatched transfer zone. |
| **EV Charging Bays**<br>*(Section 38)* | $\ge 5\%$ of bays, minimum 1 bay | **1 dedicated EV Bay ($12.5\%$)** | **PASS** | Bay 2 marked in green epoxy with wall-mounted Level 2 AC charger and signage. |
| **Mechanical Ventilation**<br>*(Section 156)* | Extract $\ge 6\text{ ACH}$ (10 ACH at ramp queue) | **2 Shafts ($0.80\text{ m} \times 0.80\text{ m}$)** | **PASS** | Shaft 1 at ramp entry ($10\text{ ACH}$); Shaft 2 at rear ($6\text{ ACH}$) rising above ground podium. |
| **Floor Drainage & Falls**<br>*(Code drainage provisions)* | Fall $1:100$ to sump pit with pump | **Fall $1:100$, Sump $1.0 \times 1.0 \times 1.2\text{ m}$** | **PASS** | Concrete floor graded towards rear low point with cast iron grating and submersible pump. |
| **Clear Headroom**<br>*(Architectural assumption)* | Clear headroom $\ge 2.40\text{ m}$ under beams | **$2.70\text{ m}$ clear headroom** | **PASS** | FFL at $-3.30\text{ m}$, beam soffit at $-0.60\text{ m}$ $\implies 3.30 - 0.60 = 2.70\text{ m} \ge 2.40\text{ m}$. |
| **Column Setback**<br>*(Architectural assumption)* | Columns setback $0.6\text{ m}$ from aisle edge | **$0.60\text{ m}$ setback into stalls** | **PASS** | Columns set back behind vehicle front door swing, permitting unobstructed car ingress/egress. |

---

## 3. Layout Options & Capacity Comparison

The clear interior width of the plot is $14.64\text{ m}$ ($15.24\text{ m} - 2 \times 0.30\text{ m}$). A double row of 90° bays requires $4.6 + 6.1 + 4.6 = 15.30\text{ m} > 14.64\text{ m}$ and cannot fit.

1. **Option A (Constructed Model):**
   - **8 bays total** (1 Accessible, 1 EV Charging, 6 Standard).
   - Layout: $3.5\text{ m}$ ramp strip on left + $6.1\text{ m}$ clear aisle in center + $5.0\text{ m}$ 90° stalls on right + rear maneuvering court ($14.6\text{ m} \times 3.8\text{ m}$).
   - **Verdict:** Recommended and built.

2. **Option B (45° Angled Bays per LN 47/2024 Fig. 1b):**
   - **6 bays total** (1 Accessible, 1 EV, 4 Standard).
   - Due to $14.64\text{ m}$ width, only ONE row of 45° bays fits alongside the ramp strip ($3.5 + 3.8 + 4.95 = 12.25\text{ m}$).
   - Stall curb pitch $= 2.4 / \sin(45^\circ) = 3.39\text{ m}$.
   - Interlocking diagonal dead corners consume linear wall space, yielding 2 fewer bays (-25%) than Option A.

3. **Option C (Option A + 2-Level Car Stackers):**
   - **15 bays total** (1 Accessible on grade + 14 Stacked).
   - *Headroom Constraint:* Double stackers require **$3.60\text{ m} \text{ to } 4.00\text{ m}$** clear height. To build Option C, the basement excavation must be deepened to $\approx 4.30\text{ m}$ floor-to-floor, requiring an L-shaped ramp or vehicle lift.

---

## 4. Materials, Lighting & Animation Architecture

### Material Specifications
- **Exposed Grey Concrete (`Mat_Concrete_Structure`):** Procedural noise-driven tone variation (0.48 to 0.64 luminance), pore bump mapping (0.004 m distance), and 0.72 roughness for cast-in-place retaining walls, beams, and soffits.
- **Epoxy Grey Floor (`Mat_Concrete_Floor`):** Smooth dark slate grey (0.24, 0.26, 0.28) with high specular clarity and low roughness (0.24), creating realistic reflections of overhead lighting.
- **Hazard Warning Stripes (`Mat_Column_Hazard_Concrete` & `Mat_Barrier_Hazard`):** Procedural 45° alternating safety yellow (0.96, 0.82, 0.04) and charcoal black (0.04, 0.04, 0.04) stripes on the bottom $0.90\text{ m}$ of all column bases and the full profile of the ramp kerb barrier.
- **Galvanised Steel (`Mat_Galvanised_Steel`):** Metallic 0.94, roughness 0.28 on drainage gratings, pump housing, and elevator sliding doors.

### Lighting Setup
- **Aisle Lighting:** 5 linear LED batten fixtures suspended along the central $6.1\text{ m}$ aisle ($X = 6.85\text{ m}, Z = -0.55\text{ m}$) at $Y = 3.5, 9.5, 15.5, 21.5, 27.5\text{ m}$. Each fixture combines an emissive daylight diffuser bar with a downward-facing $220\text{ W}$ rectangular Area Light.
- **Emergency Exit Signage:** Internally illuminated green emergency exit signs with white lettering and emission (strength 10.0) positioned over the stair fire exit door and lift lobby.
- **Ramp Portal Daylight:** $850\text{ W}$ soft daylight area light ($3.6\text{ m} \times 2.5\text{ m}$, 5000K warm daylight) mounted at $Y = -0.5\text{ m}$ angled down at 50° into the ramp portal.

### 20-Second Camera Walkthrough Animation
- **Path:** 3D Bezier curve with 13 key control points starting at the road ($Y = -4\text{ m}$), descending the ramp at $1.6\text{ m}$ eye height, curving smoothly into the rear turning court, driving forward down the central aisle, and walking into the lift lobby.
- **Timing:** 480 frames at $24\text{ fps}$ (20.0 seconds).
- **Constraints:** `FOLLOW_PATH` constraint with fixed location evaluation and clamped Bezier ease-in / ease-out curves; `TRACK_TO` constraint targeting an offset Empty leading ahead on the trajectory.

---

## 5. How to Export the Animation as an MP4 Video

The scene is configured in EEVEE at $1920 \times 1080$, $24\text{ fps}$, outputting to `//render/`.

### Method A: Direct Video Render in Blender (Fastest GUI Method)
1. Open [`Basement Parking 50x100 v1.blend`](../../Basement%20Parking%2050x100%20v1.blend) in Blender.
2. In the **Output Properties** tab (printer icon on the right):
   - Under **Output** $\rightarrow$ **File Format**, change `PNG` to **`FFmpeg Video`**.
   - Under the **Encoding** dropdown:
     - **Container:** `MPEG-4`
     - **Video Codec:** `H.264`
     - **Output Quality:** `Perceptually Lossless` or `High Quality`
     - **Encoding Speed:** `Good`
3. Press **`Ctrl + F12`** (or go to **Render** $\rightarrow$ **Render Animation**).
4. Blender will render all 480 frames directly into a single MP4 file in your `render/` folder in ~3–5 minutes.

### Method B: Render PNG Sequence + Compile with FFmpeg (Industry Standard)
1. In Blender, with file format set to `PNG`, press **`Ctrl + F12`** to render frames `0001.png` to `0480.png` into `//render/`.
2. Open PowerShell or Command Prompt in the `render` directory and run:
   ```powershell
   ffmpeg -framerate 24 -i %04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 "Basement_Walkthrough_20s.mp4"
   ```
   *Explanation of flags:*
   - `-framerate 24`: Matches the 24 fps project timeline.
   - `-i %04d.png`: Reads 4-digit zero-padded PNG sequence.
   - `-c:v libx264`: High-efficiency H.264 video compression.
   - `-pix_fmt yuv420p`: Ensures 100% playback compatibility on Windows, Mac, iOS, Android, and web browsers.
   - `-crf 18`: Visually lossless compression quality.
