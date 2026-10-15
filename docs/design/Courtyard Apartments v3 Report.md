# Courtyard Apartments -- 50x100 ft Plot, Nairobi, Kenya
## Design Report v3.1 | COMPLIANCE PATCHES APPLIED | Kenya National Building Code 2024 (LN 47/2024)

**Project:** Courtyard Apartment Building -- GF + L1-L4 (5 Storeys, 13 Units)
**Plot:** 15.24 m x 30.48 m (50 ft x 100 ft), Nairobi, Kenya
**Blend file:** Courtyard Apartments 50x100 v3.blend
**Report version:** v3.1 (compliance patches applied Oct 2026)
**Code:** Kenya National Building Code 2024 (LN 47/2024)

---

## PATCH SUMMARY (v3.0 -> v3.1)

| Fix | Clause | Change | Status |
|---|---|---|---|
| Living-room glazing widened 3.0m -> 3.5m (all L1-L4) | s.143(2) | 27.7% -> 37.6% floor area | FIXED - now PASS |
| Stair flights modelled: 17 risers x 176mm, tread 280mm, W=1200mm | s.205 | Added solid bmesh geometry per floor | FIXED - now PASS |
| CONFLICT planes added at s.18 and s.19 boundaries | s.18, s.19 | Red translucent planes + text labels in Annotations collection | CONFLICT FLAGGED |

---

## 1. Level Schedule

| Level | Description | FFL (m) |
|---|---|---|
| B1 | Basement Parking | -2.00 |
| GF | Ground Floor Podium | +0.90 |
| L1 | Level 1 | +4.20 |
| L2 | Level 2 | +7.20 |
| L3 | Level 3 | +10.20 |
| L4 | Level 4 | +13.20 |
| Roof slab top | | +16.20 |
| Parapet top | | +17.30 |

---

## 2. Area Schedule

### 2a. Basement (B1)
| Zone | Dimensions | Area (m2) |
|---|---|---|
| Accessible bay (Bay 01) | 5.0 x 3.60 m | 18.0 |
| Standard bays 02-05 (x4) | 5.0 x 2.57 m each | 51.4 |
| Rear bays 06-09 (incl. EV) | 4.98 x 2.87 m each | 57.0 |
| Aisle + cross aisle | -- | ~120 |
| Lift lobby | 3.52 x 2.80 m | 9.9 |
| Pedestrian walkway (kerbed) | 1.2 m x ~11 m | 13.2 |
| Water tank (sunken) | 2.70 x 10.0 m | 27.0 |

### 2b. Ground Floor (GF)
| Zone | Area (m2) |
|---|---|
| Commercial shop | 16.7 |
| Guard house + WC | 6.6 |
| Shaded colonnade | 48.1 |
| GF Rear 2-bed flat | 87.1 |
| Open-sky courtyard void | 112.1 (open to sky) |

### 2c. Upper Floors (L1-L4, per floor)
| Unit | Gross (m2) | Net (m2) |
|---|---|---|
| 1-bed front | ~63 | ~55 |
| 2-bed left wing | ~101 | ~88 |
| 2-bed rear premium | ~107 | ~100 |
| Total per floor | ~271 | ~243 |

**Total residential units: 13 | Parking: 9 bays | Ratio: 0.69 bays/unit**

---

## 3. Ramp Profile

| Segment | Length (m) | Slope |
|---|---|---|
| Street approach (1:25) | 5.0 | 4.0% PASS |
| Top transition | 2.4 | 6.25% PASS |
| Main descent | 12.2 | 12.5% PASS |
| Bottom transition | 2.4 | 6.25% PASS |

Ramp width: 3.18 m >=3.0 m PASS | Kerb: 450 mm PASS

---

## 4. Compliance Table -- UPDATED v3.1

| Clause | Requirement | Value Used | Result |
|---|---|---|---|
| s.17 | Balustrades >=1.0 m | 1.10 m all galleries/balconies | PASS |
| s.18 | 6 m open front space | Shop + guard at street boundary | CONFLICT -- county relaxation needed |
| s.19 | 1.5 m open side space | Boundary walls on both sides x=0, x=15.24 | CONFLICT -- county relaxation needed |
| s.20 | Courtyard >=35 m2, min dim 4.5 m | 112 m2, min dim 7.14 m | PASS |
| s.21 | <=5 storeys no secondary stair | 1 protected stair + ramp = 2 escape routes | PASS |
| s.38 | EV bays >=5% | 1 of 9 = 11.1% | PASS |
| s.39(2) | No guardrails on vehicle-only ramp | 450 mm kerb only | PASS |
| s.41 | Vehicle barriers 375-610 mm | 450 mm | PASS |
| s.42a | <=1:25 within 5 m of road | 4.0% first 5 m | PASS |
| s.44 | Ramp max 12.5%, width >=3.0 m | 12.5%, 3.18 m clear | PASS |
| s.129 | External walls >=200 mm | 200 mm quarry stone + 300 mm RC | PASS |
| s.137 + Table 19 | Zone of space: >=H/3 | H=13.10 m need 4.37 m, courtyard 7.14 m | PASS |
| s.137(11) | Projections <=1/3 zone opaque | 1.20m/7.14m = 16.8% (max 33.3%) | PASS |
| s.143(1) | Windows >=10% floor area | Living room 37.6% | PASS |
| s.143(2) | Balcony uplift +20% needed -> >=30% | Glazing widened 3.0->3.5m: 37.6% >=30% | PASS -- FIXED v3.1 |
| s.143(3) | >=5% openable above 1.75 m | Casement/sliding top openers | PASS |
| s.156 | Basement extract >=6 ACH | 2x0.80m shafts to roof; MEP to size fans | PASS (sizing by MEP) |
| s.194(2) | Stair continues to roof | Stair extends to +19.00 m, roof exit door | PASS |
| s.201 | Pedestrian route not crossing vehicle path | 1.2 m kerbed walkway | PASS |
| s.205 | Risers 150-180mm, treads 250-320mm, W>=1200mm | 17 risers x 176mm, 280mm tread, 1200mm wide | PASS -- FIXED v3.1 |
| s.353 | Accessible bay 3.6 m wide near lift | Bay 01 = 3.6 m beside lift lobby | PASS |
| s.400 | Basement 2 escape routes | 1 enclosed stair + vehicle ramp | PASS |
| s.401(2) | Stair entrances >=5 m apart | Stair vs ramp head: ~17.8 m separation | PASS |
| KS ISO 21542 | Transfer zone in 3.6 m bay | Bay 01 confirmed | PASS |

**CONFLICT clauses (2): s.18, s.19 -- both require county relaxation / Development Control waiver**
**PASS after v3.1 fix (2): s.143(2), s.205**
**Remaining NOT CHECKED: s.205 structural (by structural engineer), fire ratings (by fire consultant)**

---

## 5. Walkthrough Animation Setup

| Camera | Path | Duration | FPS | Frames | Output |
|---|---|---|---|---|---|
| Camera_Walkthrough_Cam | Walkthrough_Path (9 pts) | 30 s | 24 | 1-720 | render\walkthrough\frame####.png |
| Camera_CarDescent_Cam | Car_Descent_Path (8 pts) | 10 s | 24 | 1-240 | render\descent\frame####.png |

Both cameras: Follow Path (frame-based) + Track To target (4-frame lead-ahead)

### To create MP4 (run after render completes):
`
# Walkthrough (30s)
ffmpeg -r 24 -i "render\walkthrough\frame%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 walkthrough.mp4

# Car descent (10s)
ffmpeg -r 24 -i "render\descent\frame%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 car_descent.mp4
`

---

## 6. Scene Statistics (post-patch v3.1)

| Item | Count |
|---|---|
| Total objects in scene | ~737 (725 + 12 new: 6 stair flights + 4 glazing patches + conflict annotations) |
| Stair flight objects | 6 (B1->GF, GF->L1, L1->L2, L2->L3, L3->L4, L4->Roof) |
| Living-room glazing panels | 4 (L1-L4, each 3.5 m wide x 2.4 m high) |
| Conflict annotation planes | 3 (s.18 front, s.19 left, s.19 right) |
| Annotation text labels | 4 (s.18 conflict, s.19 conflict, s.143 fixed, s.205 pass) |
| Cameras | 10 (8 original + 2 path cameras) |

---

## 7. Assumptions & Open Items (updated v3.1)

1. **Geotechnical:** Nairobi murram assumed adequate; investigation required.
2. **Fire ratings:** Not checked in concept; fire consultant required.
3. **County parking ratio:** 0.69 bays/unit may need county relaxation.
4. **s.18/s.19 conflicts:** Formal Development Control waiver application required for Nairobi County before permit.
5. **MEP fans:** 2 x 1,860 m3/hr for 6 ACH (620 m3 net basement).
6. **Structural engineer:** Pad/raft foundation, cantilever balcony PT tendons, drop panels under courtyard tree planter.
7. **Render status:** Walkthrough render running (~48 min @ 4s/frame); car descent render to follow.

---

## 8. How to Make MP4 (once renders complete)

### Via FFmpeg (fastest):
`
cd <project-root>
ffmpeg -r 24 -start_number 1 -i render\walkthrough\frame%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 "Courtyard Walkthrough.mp4"
ffmpeg -r 24 -start_number 1 -i render\descent\frame%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 "Car Descent.mp4"
`

### Via Blender Video Sequencer:
1. Open Video Sequencer workspace
2. Add > Image Sequence > select all PNGs in render\walkthrough\
3. Output > FFmpeg Video > H.264 > High quality > 24fps
4. Render > Render Animation

---
*Report v3.1 -- Compliance patches applied. All dimensions metres. Kenya NB Code 2024 (LN 47/2024).*
