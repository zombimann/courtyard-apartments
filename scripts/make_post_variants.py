"""
make_post_variants.py -- three ready-to-post variants per platform, written
against the delivered assets.

Emits both a Markdown file (easy to copy from) and a DOCX (to match the rest of
the documentation set) from one source of truth.

  python make_post_variants.py
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(PROJ, "docs", "social")
os.makedirs(OUT, exist_ok=True)

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0xC9, 0x7B, 0x4A)

# ══════════════════════════════════════════════════════════════════════════
#  SOURCE OF TRUTH
#  Each platform -> list of variants. A variant is a dict:
#    name, format, assets, hook, copy (the post body), notes (list)
# ══════════════════════════════════════════════════════════════════════════
PLATFORMS = []

# ─────────────────────────────────────────────────────────── INSTAGRAM
PLATFORMS.append(("Instagram", [
    dict(
        name="A — The constraint, then the answer",
        fmt="Carousel, 6 slides, 4:5 (1080 × 1350)",
        assets=[
            "03_Street_Facade_4x5.jpg      (slide 1 — the hook)",
            "01_Courtyard_Garden_4x5.jpg   (slide 2 — the turn)",
            "02_Courtyard_Void_Aerial_4x5.jpg (slide 3 — the proof)",
            "06_Roof_Pergola_Sunset_4x5.jpg   (slide 4 — aspiration)",
            "04_LivingRoom_L3_4x5.jpg     (slide 5 — life inside)",
            "08_Aerial_Hero_4x5.jpg       (slide 6 — the whole thing)",
        ],
        hook="15 metres wide. Walls on three sides. Nowhere to put a window.",
        copy="""15 metres wide. Walls on three sides. Nowhere to put a window.

That is the whole brief on a 50 x 100 ft Nairobi plot.

When three of your four elevations are party walls, the plan stops being
a layout problem and becomes a light problem. So the middle of the
building became the point of it.

A 112 m2 courtyard, open to the sky, running the length of the plot.
Every home faces it. Living rooms open onto it through 3.5 metre
glazed walls. Balconies step across it so no balcony sits directly
above another home's window.

Five storeys. Thirteen homes. Nine parking bays under the podium.
A roof garden with a pergola and 8 kWp of solar.

Renders, not photographs — nothing is built yet. Swipe through and
tell me what you would change.

#architecture #archviz #nairobi #courtyardhouse #tropicalmodern
#architecturekenya #apartmentdesign #urbaninfill #sustainablearchitecture
#blender #architecturerender #design""",
        notes=["First line is 72 characters, so it never truncates in the feed.",
               "Slide 1 must work as a still on its own — the sunlit street elevation does.",
               "Packaging: slides 2→3 are the 'wait, there's a garden inside' moment."],
    ),
    dict(
        name="B — Living well in a small footprint",
        fmt="Carousel, 5 slides, 4:5",
        assets=[
            "01_Courtyard_Garden_4x5.jpg      (slide 1)",
            "06_Roof_Pergola_Sunset_4x5.jpg   (slide 2)",
            "04_LivingRoom_L3_4x5.jpg         (slide 3)",
            "05_L3_Gallery_Overlook_4x5.jpg   (slide 4)",
            "02_Courtyard_Void_Aerial_4x5.jpg (slide 5)",
        ],
        hook="Thirteen homes around one tree.",
        copy="""Thirteen homes around one tree.

Density gets a bad reputation because it is usually built badly — a
corridor, a lift core, and a view of the neighbour's wall. It does not
have to be.

On this plot the shared space is the good space: a planted courtyard
with a multi-stem tree at the centre, a shaded colonnade along its
north side, benches between the columns, a rain garden fed by the
downpipes. Every home looks onto it rather than onto a boundary wall.

Up top, a communal roof garden — pergola, planters, seating, the
water tanks, and solar.

Planting on every balcony and every gallery. Climbers on the ramp
screen wall. Soft landscape over half the open courtyard.

Thirteen homes, and every one of them gets the garden.

#architecture #courtyard #urbanliving #nairobi #archviz #greenbuilding
#apartmentliving #tropicalmodern #landscapearchitecture #blender
#designinspiration #home""",
        notes=["Emotional angle; leads with the garden rather than the building.",
               "Carousels are re-served to people who didn't swipe, so the last slide matters too."],
    ),
    dict(
        name="C — Reel: 12 seconds through the building",
        fmt="Reel, 9:16 (1080 × 1920)",
        assets=["Courtyard Walkthrough.mp4 (or its 9:16 cut)",
                "Optional cover frame: 03_Street_Facade_9x16.jpg"],
        hook="On-screen text, not a spoken hook — 0.5s: “15 m × 30 m. Almost no light.”",
        copy="""A narrow plot, a deep plan, and one idea: put the garden in the
middle and make every home face it.

12 seconds from the street to the roof.

Renders — nothing built yet.

#architecture #archviz #courtyard #nairobi #reels #architecturelovers
#blender #3dvisualization #apartmentliving #design""",
        notes=["Watch completion is the ranking signal, so 12 s and a clean loop beat 30 s.",
               "On-screen text beats a voiceover: most people watch muted.",
               "End on the same frame it opened on so the loop is invisible."],
    ),
]))

# ────────────────────────────────────────────────────── WHATSAPP STATUS
PLATFORMS.append(("WhatsApp Status", [
    dict(
        name="A — The reveal (three frames, one day)",
        fmt="3 × 9:16, posted across one day",
        assets=[
            "03_Street_Facade_9x16.jpg   (morning)",
            "01_Courtyard_Garden_9x16.jpg (midday)",
            "Courtyard Walkthrough.mp4, first 8 seconds (evening)",
        ],
        hook="One line each. Nothing more.",
        copy="""FRAME 1  (image)
  "Five storeys on a 15 x 30 m plot. Walls on three sides."

FRAME 2  (image)
  "So the middle became a courtyard. Every home faces it."

FRAME 3  (video, 8 s)
  "Walking through it before it's built." """,
        notes=["Status is personal, not a campaign — one line per frame.",
               "Reply to every response; status replies are the highest-intent messages you get."],
    ),
    dict(
        name="B — Behind the scenes (the honest one)",
        fmt="3 × 9:16 or 3 × 4:5, one day",
        assets=[
            "07_Twilight_Street_9x16.jpg",
            "S06.png cropped to 9:16 on the long section",
            "Presentation Board (web).jpg cropped to 9:16",
        ],
        hook="Builds trust by showing the work, not the render.",
        copy="""FRAME 1  (image — twilight render)
  "Rendered this at 2am. The machine took an hour and a half."

FRAME 2  (image — the section drawing)
  "This is what it actually is. 26 sheets of drawings and a cost plan."

FRAME 3  (image — the board)
  "Whole project in one board. Ask me anything about it." """,
        notes=["Showing the drawing behind the render performs well because it signals substance.",
               "This is the variant to use if your status audience is mostly work contacts."],
    ),
    dict(
        name="C — The numbers (30 seconds of value)",
        fmt="3 × 9:16, one day",
        assets=[
            "08_Aerial_Hero_4x5.jpg (crop to 9:16)",
            "S03.png cropped to 9:16 on the ground floor plan",
            "06_Roof_Pergola_Sunset_9x16.jpg",
        ],
        hook="Facts only. Fast to read, easy to reply to.",
        copy="""FRAME 1  (image)
  "13 homes. 9 parking bays. 1 tree at the centre."

FRAME 2  (image)
  "112 m2 of courtyard, open to the sky. The code asks for 35."

FRAME 3  (image)
  "KES 25.3 M per home, all in. Built in your head, not yet on site." """,
        notes=["Numbers invite questions, and questions are what keep a status thread alive."],
    ),
]))

# ────────────────────────────────────────────────────────────────────── X
PLATFORMS.append(("X  (Twitter)", [
    dict(
        name="A — Design breakdown thread (5 posts)",
        fmt="Thread, 16:9 images + one drawing sheet",
        assets=[
            "1: 03_Street_Facade_16x9.jpg",
            "2: 02_Courtyard_Void_Aerial_16x9.jpg",
            "3: 05_L3_Gallery_Overlook_16x9.jpg",
            "4: S06.png (the long section)",
            "5: 08_Aerial_Hero_16x9.jpg",
        ],
        hook="Post 1 must stand alone — most people never expand the thread.",
        copy="""POST 1
  A 50 x 100 ft plot in Nairobi. Walls on three sides, so three of the
  four elevations can never have a window.

  We put a 112 m2 courtyard in the middle and made all 13 homes
  face it.

  Renders and drawings in the thread. 🧵

POST 2  (attach 02_Courtyard_Void_Aerial_16x9.jpg)
  The plan does the work. Every habitable room takes light and air
  from the courtyard, because the boundary walls are shared.

  Courtyard is 112 m2 with a minimum dimension of 7.14 m. The code
  asks for 35 m2 and 4.5 m.

POST 3  (attach 05_L3_Gallery_Overlook_16x9.jpg)
  Climate response, not decoration:
  · vertical timber fins to the west facade for the 4pm sun
  · 600 mm horizontal hoods to the south courtyard face
  · a colonnade along the north side, shaded by the wing above
  · balconies staggered so none sits over another home's window

POST 4  (attach S06.png)
  One thing that surprised me: the courtyard is 7.1 m wide with 15 m
  of wall above it, so direct sun only reaches the floor when the sun
  is above about 65 degrees.

  Below that it lights the upper facades and leaves the floor in
  shade. That is why courtyards are comfortable — and why the render
  is lit at 73 degrees.

POST 5  (attach 08_Aerial_Hero_16x9.jpg)
  5 storeys, 13 homes, 9 parking bays below ground, 8 kWp of solar,
  a roof garden with a pergola.

  Renders only — nothing is built. Questions welcome.""",
        notes=["Never attach more than one image to post 1; it changes the crop in the timeline.",
               "Post 4 is the one people quote back at you — a non-obvious technical fact."],
    ),
    dict(
        name="B — The cost thread (4 posts)",
        fmt="Thread, one image + text-led",
        assets=[
            "1: 08_Aerial_Hero_16x9.jpg",
            "2: S08.png (schedules and compliance sheet)",
            "3: 04_LivingRoom_L3_16x9.jpg",
            "4: Presentation Board (web).jpg",
        ],
        hook="Money is the most-shared angle on X in the built-environment space.",
        copy="""POST 1
  Costed a 13-home courtyard apartment building on a 50 x 100 ft
  Nairobi plot.

  KES 329 M all in. KES 241,700 per m2. KES 25.3 M per home.

  Where it goes, thread: 🧵

POST 2  (attach S08.png)
  Measured works: KES 244 M. The five biggest elements:
  · RC frame, slabs and stairs — 21%
  · MEP — 16%
  · external walls and cladding — 11%
  · substructure and basement — 10%
  · doors, windows and glazing — 8%

  Basement parking is the single most expensive square metre on the
  site and it earns nothing.

POST 3  (attach 04_LivingRoom_L3_16x9.jpg)
  Then contingency 7.5%, professional fees 9%, VAT 16%. That is the
  jump from KES 244 M to KES 329 M, and it is where most first
  estimates fall over.

  Rates are Q4 2026 Nairobi market, indicative, to be tendered.

POST 4  (attach Presentation Board (web).jpg)
  Full set: 8 drawing sheets, a priced bill of quantities, and the
  specification.

  Excludes land, finance and county charges. Not built — this is a
  cost plan, not a contract.""",
        notes=["Post the numbers in post 1, not at the end. The number IS the hook.",
               "Expect the replies to be about construction cost generally — that is the point."],
    ),
    dict(
        name="C — The mistake thread (3 posts)",
        fmt="Thread, drawing-led",
        assets=[
            "1: S03.png (ground floor plan)",
            "2: 02_Courtyard_Void_Aerial_16x9.jpg",
            "3: 05_L3_Gallery_Overlook_16x9.jpg",
        ],
        hook="Admitting a specific error outperforms any self-promotion on X.",
        copy="""POST 1
  I checked my own building model and every window in it was fake.

  All 43 glazing panels were modelled *inside* solid walls, with no
  opening cut. A ray cast from inside the living room hit the wall at
  4.38 m.

  Two minutes of ray casting found it. Six months of drawing had not.

POST 2  (attach 02_Courtyard_Void_Aerial_16x9.jpg)
  Why it matters beyond the render: the compliance report claimed the
  living-room glazing met the 10% window-to-floor-area rule.

  A panel inside a solid wall delivers no window area. The claim was
  never true of the geometry.

POST 3  (attach 05_L3_Gallery_Overlook_16x9.jpg)
  Fixed it by booleaning the openings out of the host walls and
  stretching the glass to fill the reveal.

  Lesson for anyone modelling buildings: ray cast your own model
  before you trust your schedule.""",
        notes=["Both images are the same building — this is not a teardown, it is a process note.",
               "High save/quote rate; the lesson is portable to other people's projects."],
    ),
]))

# ─────────────────────────────────────────────────────────────── LINKEDIN
PLATFORMS.append(("LinkedIn", [
    dict(
        name="A — The verification post (document carousel)",
        fmt="Native PDF document post — upload the 8-sheet drawing set",
        assets=[
            "Upload: Courtyard Apartments - Drawing Set.pdf  (8 sheets)",
            "Cover slide will be S01",
            "Optional second image if you post as text instead: 08_Aerial_Hero_16x9.jpg",
        ],
        hook="First 3 lines — this is all that shows before “see more” (about 200 chars)",
        copy="""I re-derived every figure on my own drawing set from the model.

Nine things were wrong. Five of them mattered.

The project is a 13-home courtyard apartment block on a 15.24 x 30.48 m
plot in Nairobi. The set is eight A1 sheets: plans, sections, elevations,
door and window schedules, and a compliance register.

Instead of proofreading the sheets, I wrote a script that exports the model
geometry and recomputes every dimension, area and compliance figure from
scratch, then diffed the two. It found:

The floor plans were cut 0.30 m above floor level. Almost every window sill
is higher than that, so the cut passed underneath the windows and they were
not drawn at all. On a scheme whose entire premise is getting daylight into
a deep plan.

The basement was scheduled at 620 m2. The plot is 464.5 m2. The basement
was larger than the site it sits under.

The roof garden was scheduled at 120 m2. It is 57 m2.

The window area was stated as 37.6% of floor area. It measures 7.2%, against
a clause that requires 10%.

And underneath that: the model contains 28 glazing panels for 13 dwellings,
roughly two windows per home, against a design that puts a 3.5 m glazed wall
in every living room. So either the model is missing most of its glazing, or
the scheme does not meet the clause. The numbers cannot tell me which, and I
am not claiming a pass on a model I do not trust.

None of these were careless. They all came from the same habit: typing a
schedule from intent instead of measuring it from the model. A window object
is not a window. A scheduled area is not an area until something measured it.

The set attached is the corrected issue. The compliance register now shows
what is verified and what is not, which is more useful than a column of
ticks.

If you produce drawings, this check is cheap. Export the geometry, recompute
the numbers, diff them. A day of scripting against a week of proofreading.

What is the last thing you found by measuring rather than reading?

#architecture #BIM #quantitysurveying #construction #design""",
        notes=[
            "Hook is 84 characters, so both lines survive the 'see more' truncation.",
            "Document posts are LinkedIn's strongest format — the PDF renders as a swipeable carousel.",
            "The 'what is not verified' paragraph is the credibility play. Do not cut it.",
            "No links anywhere in the body. Put the geometry-review note in the first comment.",
        ],
    ),
    dict(
        name="B — The window-area post",
        fmt="Text + 1 image, 16:9",
        assets=[
            "S04.png (typical upper floor plan — now shows the windows)",
            "or 05_L3_Gallery_Overlook_16x9.jpg if a render reads better for your audience",
        ],
        hook="Three short lines. The number does the work.",
        copy="""My compliance register said the windows were 37.6% of floor area.

The model measures 7.2%.

The clause requires 10%.

Here is how a number like that gets onto a drawing.

The register was filled in by hand. Someone took the glazing area of all
five storeys and divided it by the area of one floor. 119.5 m2 over
327.7 m2 gives 36.5%, rounded to 37.6% somewhere along the way. The correct
calculation is that same glazing against all five floors: 119.5 m2 over
1,670.7 m2, which is 7.2%.

A five-fold error, and it turned an uncomfortable number into a comfortable
pass.

What the geometry actually says:

GF       8.2%
L1       6.9%
L2       6.9%
L3       6.9%
L4       6.9%
Overall  7.2%

Whether the clause passes depends on whether it is applied room by room or
across a floor. A building at 7.2% cannot be passing it comfortably either
way.

There is a second problem underneath this one. The model contains 28 glazing
panels for 13 dwellings — about two windows per home — against a design that
specifies a 3.5 m glazed wall in every living room. So either the model is
missing most of its glazing, or the scheme genuinely fails the clause. Those
are very different problems and the area figures cannot distinguish them.

The rule I have taken from it: never compute a compliance figure from a
schedule. Compute it from the geometry, every time, and print the workings
beside the result so the next person can check your arithmetic rather than
trust it.

Has anyone else found a compliance number that did not survive being
recalculated?

#architecture #BIM #buildingcodes #compliance #design""",
        notes=[
            "The three-line hook is under 150 characters and reads as a complete thought.",
            "The per-floor table is what makes it credible — it shows the working, not just the verdict.",
            "Naming the second problem (28 panels for 13 homes) is what stops this reading as a teardown.",
            "This is the variant most likely to be quoted; keep the 37.6 / 7.2 / 10 numbers intact.",
        ],
    ),
    dict(
        name="C — The gross-floor-area post (developer-facing)",
        fmt="Text + 1 image, 16:9",
        assets=[
            "08_Aerial_Hero_16x9.jpg",
            "or Presentation Board (web).jpg for a wider audience",
        ],
        hook="Leads with a contradiction. Developers read contradictions.",
        copy="""The same building costs KES 241,700 per square metre.

Or KES 197,200.

The difference is one term nobody defined: gross floor area.

The project is a 13-home courtyard apartment block on a 15.24 x 30.48 m
plot in Nairobi, with a single basement level. The costed works total
KES 329 M including fees, contingency and VAT.

Divide that by the floor area and you get the rate everyone quotes. So the
rate depends entirely on what goes in the denominator — and the drawings
never said.

Measured from the model, the slab plates are:

Basement          464.5 m2
Ground floor      359.8 m2
L1 to L4        1,310.9 m2
Total           2,135.2 m2

The figure used throughout the cost plan was 1,363 m2. That is reproducible,
if you exclude the courtyard void, the open colonnade and the open access
galleries. Which is a perfectly defensible definition of gross floor area.

It is also 23% smaller than the number a contractor will measure.

So the headline rate is either KES 241,700 per m2 on an enclosed-area basis,
or KES 197,200 per m2 across all slab plates. Both are honest. Only one of
them was ever written down.

There was a second one of these. The basement was scheduled at 620 m2 on a
plot of 464.5 m2. A basement cannot be larger than the site it sits under,
which tells you the figure was never checked against anything at all.

If you are pricing, lending against, or buying a building, this is the
cheapest question available to you: what exactly is inside your area figure,
and what is outside it?

#propertydevelopment #construction #realestate #Nairobi #quantitysurveying""",
        notes=[
            "The two-rate contradiction in the first two lines is the whole post. Do not soften it.",
            "Two numbers, both defensible, is far more persuasive than one number called wrong.",
            "Ends on a question the reader can use on their own project, which drives comments.",
            "Excludes land, finance and county charges — say so if anyone asks in the comments.",
        ],
    ),
]))

# ──────────────────────────────────────────────────────────────── YOUTUBE
PLATFORMS.append(("YouTube", [
    dict(
        name="A — Short: the courtyard reveal",
        fmt="Short, 9:16, 12 s, from Courtyard Walkthrough.mp4",
        assets=["Courtyard Walkthrough.mp4 (9:16)",
                "Thumbnail: 03_Street_Facade_9x16.jpg"],
        hook="First 1.5 seconds are the street elevation. No logo, no title card.",
        copy="""TITLE (pick one, keep under 60 characters)
  · 13 homes around one courtyard — 15 x 30 m plot
  · A courtyard in the middle of a 15 m wide plot
  · 15 x 30 m. Walls on three sides. One courtyard.

DESCRIPTION
  A 50 x 100 ft plot in Nairobi with walls on three sides. The
  building has to light and ventilate itself from the middle.

  A 112 m2 courtyard, open to the sky, with every home facing it.
  Five storeys, 13 homes, 9 parking bays below ground.

  12 seconds from the street to the roof garden.

  Renders only — nothing is built yet.

  #architecture #archviz #courtyard #nairobi #shorts

ON-SCREEN TEXT
  0.5s   "15 m x 30 m. Almost no light."
  3.0s   "So we turned the middle into a courtyard."
  7.0s   "13 homes. Every one faces the garden."
  10.5s  "Five storeys. One tree at the centre."

PINNED COMMENT
  Full drawing set and the cost plan are on the channel — happy to
  answer anything about how it was modelled.""",
        notes=["Loop it: end on the opening frame so the Short restarts seamlessly.",
               "Do not add a title card; retention in the first 2 seconds decides everything."],
    ),
    dict(
        name="B — Long form: the design breakdown",
        fmt="16:9, 4–5 minutes, chaptered",
        assets=[
            "Courtyard Walkthrough_16x9.mp4 (b-roll)",
            "Stills 01, 02, 03, 05, 06, 08 as cutaways",
            "S03.png, S06.png as on-screen graphics",
        ],
        hook="Answer the constraint in the first 15 seconds. No intro sequence.",
        copy="""TITLE
  13 Homes Around One Courtyard — Designing a 15 x 30 m Infill Plot

DESCRIPTION
  A 50 x 100 ft plot in Nairobi: 15.24 m wide, 30.48 m deep, with
  boundary walls on three sides. Three of the four elevations can
  never have a window.

  This is how the plan, the section and the sun shading respond to
  that — with the drawings, the renders and the cost.

  CHAPTERS
  00:00  The constraint — 15 x 30 m, walls on three sides
  00:45  Why the middle became the courtyard
  01:50  The street elevation and the timber fins
  02:40  Inside a home — the 3.5 m glazed wall
  03:30  The roof garden and the solar array
  04:10  What it costs
  04:50  What I would do differently

  Nothing here is built. Renders, drawings and a cost plan.

  #architecture #archviz #courtyard #nairobi #design

THUMBNAIL
  08_Aerial_Hero_16x9.jpg, three words maximum: "13 HOMES, 1 COURTYARD" """,
        notes=["Chapters get the video surfaced in search; write them before you publish, not after.",
               "The 'what I would do differently' chapter is the retention hook at the end."],
    ),
    dict(
        name="C — Long form: how it was made",
        fmt="16:9, 6–8 minutes, process",
        assets=[
            "Presentation Board (web).jpg",
            "S03.png, S06.png, S07.png, S08.png",
            "Before/after: render/archive/hero_v3 vs the new renders",
            "Courtyard Orbit_16x9.mp4 as b-roll",
        ],
        hook="Process videos hold a technical audience far longer than portfolio videos.",
        copy="""TITLE
  Modelling, Rendering and Costing a Building in Blender — Full Process

DESCRIPTION
  Everything behind the Courtyard Apartments set: how the model was
  built, how the renders were lit, how the drawings and the bill of
  quantities were produced, and the mistakes found along the way.

  CHAPTERS
  00:00  What we are making
  00:40  The model and its coordinate system
  01:50  Lighting: real HDRI skies, and why the courtyard needs a
         73-degree sun
  03:10  Materials: PBR textures and box-projected UVs
  04:20  Foliage without a scanned tree
  05:20  The photographic pass — bloom, grain, grade
  06:20  Drawings from true section cuts
  07:10  The bill of quantities
  08:00  Three mistakes worth avoiding

  Assets are CC0 from Poly Haven. Rendered in Blender 5.2 with EEVEE
  Next on a 2-core CPU with no GPU.

  #blender #archviz #3dmodelling #architecture #tutorial""",
        notes=["Before/after is the single most-watched segment in process videos — cut it early.",
               "The 'three mistakes' chapter is where the window-opening defect goes."],
    ),
]))

# ══════════════════════════════════════════════════════════════════════════
#  SCHEDULE
# ══════════════════════════════════════════════════════════════════════════
SCHEDULE = [
    ("Day 1 (Mon)", "LinkedIn — A: drawing set document", "Weekday morning, ~08:30 local"),
    ("Day 1", "Instagram — A: the constraint carousel", "Same day, mid-morning"),
    ("Day 2", "X — A: design breakdown thread", "Mid-morning; threads do best Tue–Thu"),
    ("Day 3", "Instagram — C: the Reel", "Evening, 18:00–20:00"),
    ("Day 3", "YouTube — A: the Short", "Same clip, same day as the Reel"),
    ("Day 4", "WhatsApp Status — A: the reveal", "Three frames across one day"),
    ("Day 6", "LinkedIn — B: the lesson post", "Weekday morning"),
    ("Day 8", "X — C: the mistake thread", "Different audience from LinkedIn — not a repost"),
    ("Day 9", "WhatsApp Status — B: behind the scenes", "After the LinkedIn lesson post lands"),
    ("Day 11", "LinkedIn — C: the numbers post", "Weekday morning"),
    ("Day 11", "X — B: the cost thread", "Different framing from the LinkedIn version"),
    ("Day 13", "Instagram — B: living well carousel", "Weekend, mid-morning"),
    ("Day 14", "YouTube — B or C: long form", "Publish with chapters and a thumbnail"),
    ("Day 16", "WhatsApp Status — C: the numbers", "Closing frame of the sequence"),
]

RULES = [
    "Never post the same edit on the same platform twice in one week — Instagram suppresses repeats.",
    "Keep the first line of every Instagram caption under 125 characters so it is not truncated.",
    "LinkedIn shows roughly the first 3 lines (about 200 characters) before “see more”. Write for that.",
    "No external links in a LinkedIn or X post body. Put them in the first comment.",
    "Reply to every comment in the first hour; early engagement is what extends reach.",
    "Add alt text to every image at upload time. It is read by screen readers and is a small ranking signal.",
    "Export at the platform's native size — 1080 x 1350 for feed, 1080 x 1920 for Reels and Shorts. Re-uploading a downscaled file is the most common cause of a soft-looking post.",
    "Use music from the platform's own commercial library, not a personal streaming account.",
    "Say that these are renders and that nothing is built. Every time. It is both true and, in this sector, a credibility signal.",
    "Do not repeat the same opening line across platforms in the same week — the audiences overlap more than you think.",
]


# ══════════════════════════════════════════════════════════════════════════
#  MARKDOWN
# ══════════════════════════════════════════════════════════════════════════
def write_md(path):
    L = []
    L.append("# Post Variants — 3 per platform\n")
    L.append("Written against the delivered assets in `render/delivery/` and "
             "`render/videos/`. Every figure quoted here comes from the drawings and "
             "the bill of quantities, so the copy and the documentation agree.\n")
    L.append("**Nothing in this project is built.** Every variant says so. Keep it that way.\n")
    L.append("---\n")

    for platform, variants in PLATFORMS:
        L.append(f"## {platform}\n")
        for i, v in enumerate(variants, 1):
            L.append(f"### Variant {v['name']}\n")
            L.append(f"**Format:** {v['fmt']}  ")
            L.append(f"**Hook:** {v['hook']}\n")
            L.append("**Assets**\n")
            for a in v['assets']:
                L.append(f"- `{a}`")
            L.append("\n**Copy — paste as is**\n")
            L.append("```")
            L.append(v['copy'])
            L.append("```\n")
            L.append("**Why this variant works**\n")
            for n in v['notes']:
                L.append(f"- {n}")
            L.append("")
        L.append("---\n")

    L.append("## Suggested running order\n")
    L.append("Sequenced so that no two posts in the same week use the same asset or "
             "the same opening line, and so each platform gets a different angle on "
             "the same project.\n")
    L.append("| When | Post | Note |")
    L.append("|---|---|---|")
    for a, b, c in SCHEDULE:
        L.append(f"| {a} | {b} | {c} |")
    L.append("")
    L.append("## Rules that apply to all of them\n")
    for r in RULES:
        L.append(f"- {r}")
    L.append("")
    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(L))
    print(f"wrote {path}")


# ══════════════════════════════════════════════════════════════════════════
#  DOCX
# ══════════════════════════════════════════════════════════════════════════
def write_docx(path):
    doc = Document()
    for s in doc.sections:
        s.top_margin = Cm(1.9); s.bottom_margin = Cm(1.9)
        s.left_margin = Cm(2.1); s.right_margin = Cm(1.9)
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(10)

    def H(text, level=1):
        p = doc.add_heading(text, level=level)
        for r in p.runs:
            r.font.color.rgb = NAVY if level <= 2 else ACCENT
        return p

    def body(text, size=10, italic=False):
        p = doc.add_paragraph()
        r = p.add_run(text); r.font.size = Pt(size); r.italic = italic
        return p

    def bullet(text):
        p = doc.add_paragraph(text, style="List Bullet")
        for r in p.runs:
            r.font.size = Pt(9.5)

    def block(text):
        for line in text.strip("\n").split("\n"):
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.left_indent = Cm(0.5)
            r = p.add_run(line if line else " ")
            r.font.name = 'Consolas'; r.font.size = Pt(9)
        doc.add_paragraph()

    p = doc.add_paragraph(); p.alignment = 1
    r = p.add_run("COURTYARD APARTMENTS"); r.bold = True
    r.font.size = Pt(24); r.font.color.rgb = NAVY
    p = doc.add_paragraph(); p.alignment = 1
    r = p.add_run("POST VARIANTS — 3 PER PLATFORM"); r.bold = True
    r.font.size = Pt(14); r.font.color.rgb = ACCENT
    p = doc.add_paragraph(); p.alignment = 1
    r = p.add_run("Instagram · WhatsApp Status · X · LinkedIn · YouTube"); r.font.size = Pt(11)
    body("Written against the delivered assets in render/delivery and render/videos. "
         "Every figure quoted comes from the drawings and the bill of quantities, so "
         "the copy and the documentation agree.", italic=True)
    body("Nothing in this project is built. Every variant says so. Keep it that way.",
         italic=True)

    for platform, variants in PLATFORMS:
        doc.add_page_break()
        H(platform, 1)
        for v in variants:
            H(v['name'], 2)
            body(f"Format: {v['fmt']}", 9.5)
            body(f"Hook: {v['hook']}", 9.5, italic=True)
            body("Assets", 10)
            for a in v['assets']:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(a); r.font.name = 'Consolas'; r.font.size = Pt(9)
            doc.add_paragraph()
            body("Copy — paste as is", 10)
            block(v['copy'])
            body("Why this variant works", 10)
            for n in v['notes']:
                bullet(n)

    doc.add_page_break()
    H("Suggested running order", 1)
    body("Sequenced so that no two posts in the same week use the same asset or the "
         "same opening line, and so each platform gets a different angle on the same "
         "project.", italic=True)
    t = doc.add_table(rows=1, cols=3)
    t.style = "Light Grid Accent 1"
    for i, hd in enumerate(["When", "Post", "Note"]):
        c = t.rows[0].cells[i]; c.text = ""
        rr = c.paragraphs[0].add_run(hd); rr.bold = True; rr.font.size = Pt(9)
    for a, b, c in SCHEDULE:
        cells = t.add_row().cells
        for i, v in enumerate((a, b, c)):
            cells[i].text = ""
            rr = cells[i].paragraphs[0].add_run(v); rr.font.size = Pt(9)
    for i, w in enumerate((2.4, 7.4, 6.2)):
        for row in t.rows:
            row.cells[i].width = Cm(w)

    doc.add_paragraph()
    H("Rules that apply to all of them", 1)
    for r in RULES:
        bullet(r)

    doc.save(path)
    print(f"wrote {path}")


def main():
    write_md(os.path.join(OUT, "Post Variants - 3 per platform.md"))
    write_docx(os.path.join(OUT, "Post Variants - 3 per platform.docx"))


if __name__ == "__main__":
    main()
