"""
make_social_pack.py -- social media strategy, captions and asset mapping.

  python make_social_pack.py
"""
import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(PROJ, "docs", "social")
os.makedirs(OUT, exist_ok=True)
DOCX = os.path.join(OUT, "Courtyard Apartments - Social Media Pack.docx")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0xC9, 0x7B, 0x4A)


def h(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = NAVY if level <= 2 else ACCENT
    return p


def para(doc, text, italic=False, bold=False, size=10.5, space=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space)
    r = p.add_run(text)
    r.italic = italic
    r.bold = bold
    r.font.size = Pt(size)
    return p


def bullet(doc, text):
    p = doc.add_paragraph(text, style="List Bullet")
    for r in p.runs:
        r.font.size = Pt(10)
    return p


def copy_block(doc, text):
    """Monospace block for text the user will copy and paste."""
    for line in text.strip("\n").split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.5)
        r = p.add_run(line if line else " ")
        r.font.name = 'Consolas'
        r.font.size = Pt(9.5)
    doc.add_paragraph()


def table(doc, rows, headers, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    for i, hd in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(hd)
        r.bold = True
        r.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(9)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Cm(w)
    return t


def build():
    doc = Document()
    for s in doc.sections:
        s.top_margin = Cm(2.0)
        s.bottom_margin = Cm(2.0)
        s.left_margin = Cm(2.2)
        s.right_margin = Cm(2.0)
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(10.5)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("COURTYARD APARTMENTS")
    r.bold = True
    r.font.size = Pt(26)
    r.font.color.rgb = NAVY
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("SOCIAL MEDIA PACK")
    r.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = ACCENT
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Instagram  ·  WhatsApp Status  ·  X  ·  LinkedIn  ·  YouTube")
    r.font.size = Pt(11)
    para(doc, "Prepared October 2026. Strategy, ready-to-post copy, asset mapping, "
              "hashtags, alt text and posting cadence.", italic=True)

    # ------------------------------------------------------------------ 1
    h(doc, "1.  What the research says drives engagement", 1)
    para(doc, "Findings from current platform-behaviour sources, applied directly to this "
              "project's assets.")
    table(doc, [
        ("Instagram Reels",
         "The only format that reliably reaches non-followers. The algorithm ranks on "
         "watch completion, so clips under 15 s that loop get pushed hardest.",
         "Two 12 s vertical films, cut to loop, no long intro."),
        ("Instagram carousels",
         "Up to 20 slides, viewed at the user's pace; the platform re-serves the post to "
         "people who did not swipe, showing slide 2 or 3 as the hook.",
         "A 7-slide 4:5 carousel: wide exterior → courtyard → roof → interior → plan."),
        ("Instagram single image",
         "Reach is mostly existing followers; Instagram shows a post to roughly 10% of "
         "followers. Portfolio anchor, not a discovery tool.",
         "Use sparingly — one strong twilight image, not the whole set."),
        ("Stories / WhatsApp status",
         "24 hours, followers only, no discovery. Builds trust and personality.",
         "Vertical crops of the making-of: the model, the drawings, the overnight render."),
        ("LinkedIn",
         "Document (PDF) carousels and native video outperform link posts; the first two "
         "or three lines are all that show before 'see more'.",
         "Use the 8-sheet drawing set as a native PDF document post."),
        ("X",
         "A single high-impact image with a short technical thread performs best; the "
         "first post must stand alone without the thread.",
         "Twilight image + a 5-post thread on the design and the cost per home."),
        ("YouTube",
         "Shorts reward a hook in the first 1–2 seconds and a loop; long-form rewards "
         "chapters and a strong thumbnail.",
         "Shorts = the same vertical films. Long-form = a chaptered walkthrough."),
    ], ["Platform", "What actually drives reach", "How we use it here"],
        [3.2, 7.0, 6.6])

    # ------------------------------------------------------------------ 2
    h(doc, "2.  Asset map — what to post where", 1)
    para(doc, "All final assets are in render/delivery. Masters are 1920 x 1080; "
              "Instagram crops are 1080 x 1350; verticals are 1080 x 1920.")
    table(doc, [
        ("01", "01_Courtyard_Garden", "16:9 + 4:5 + 9:16", "Carousel slide 2, Reel opener"),
        ("02", "02_Courtyard_Void_Aerial", "16:9 + 4:5", "Carousel slide 4, X thread"),
        ("03", "03_Street_Facade", "16:9 + 4:5 + 9:16", "Carousel slide 1 (the hook), LinkedIn"),
        ("04", "04_LivingRoom_L3", "16:9 + 4:5", "Carousel slide 5 — the human scale"),
        ("05", "05_L3_Gallery_Overlook", "16:9 + 4:5", "Carousel slide 6"),
        ("06", "06_Roof_Pergola_Sunset", "16:9 + 4:5 + 9:16", "Carousel slide 3, Reel closer"),
        ("07", "07_Twilight_Street", "16:9 + 4:5 + 9:16", "Single-image post, X hero, cover"),
        ("08", "08_Aerial_Hero", "16:9 + 4:5", "Carousel slide 7, YouTube thumbnail"),
        ("V1", "video_fly (12 s)", "9:16 + 16:9", "Reels, Shorts, WhatsApp status, LinkedIn"),
        ("V2", "video_orbit (12 s)", "9:16 + 16:9", "Reels, Shorts, X, YouTube"),
        ("D1", "Drawing set PDF (8 sheets)", "document", "LinkedIn document post — top performer"),
    ], ["Ref", "Asset", "Formats", "Best use"], [1.4, 4.6, 3.6, 7.2])

    # ------------------------------------------------------------------ 3
    h(doc, "3.  Instagram — carousel (post this first)", 1)
    para(doc, "Seven slides at 4:5. Slide 1 is the hook and must work as a still: the "
              "sunlit street elevation with the timber fins.")
    copy_block(doc, """
SLIDE ORDER
  1  03_Street_Facade_4x5          (hook — sunlit west elevation)
  2  01_Courtyard_Garden_4x5       (the surprise — there is a garden inside)
  3  06_Roof_Pergola_Sunset_4x5    (aspiration — rooftop living)
  4  02_Courtyard_Void_Aerial_4x5  (proof — look at the plan)
  5  04_LivingRoom_L3_4x5          (human scale — life inside)
  6  05_L3_Gallery_Overlook_4x5    (detail — the shading strategy)
  7  08_Aerial_Hero_4x5            (whole building, context)

CAPTION
  A 15 x 30 metre plot in Nairobi. One boundary to the street, three
  walls shared with neighbours, and almost no way to get light or air
  into the middle of the building.

  So the middle became the point.

  A 112 m2 courtyard open to the sky runs the length of the plot.
  Every home faces it. The living rooms open onto it through 3.5 metre
  glazed walls, and the balconies step across it so no balcony sits
  above another home's window.

  The rest is climate:
  · vertical timber fins on the west facade for the afternoon sun
  · 600 mm horizontal hoods to the south courtyard face
  · a colonnade along the north side, shaded by the wing above
  · a multi-stem tree at the centre, and planting on every balcony

  Five storeys. Thirteen homes. Nine parking bays below ground.
  A rooftop garden with a pergola and solar.

  Swipe through. Then tell me what you would change.

  #architecture #archviz #nairobi #courtyardhouse #tropicalmodern
  #architecturekenya #apartmentdesign #sustainablearchitecture
  #urbaninfill #blender3d #architecturerender #designinspiration

ALT TEXT (put this on the post, not the caption)
  Rendered view of a five-storey apartment building on a narrow
  Nairobi plot: a pale rendered facade with vertical timber sun
  screens, a car portal and pedestrian gate at street level, and a
  planted courtyard visible through the centre of the building.
""")

    # ------------------------------------------------------------------ 4
    h(doc, "4.  Instagram Reel / YouTube Short", 1)
    para(doc, "12 seconds, 9:16, no intro, loopable. The hook is the first frame — the "
              "street elevation at golden hour — because a viewer decides in about one "
              "second.")
    copy_block(doc, """
STRUCTURE  (video_fly, 12 s, loops seamlessly ending on the courtyard)
  0.0-1.5s   street level, camera moving toward the pedestrian gate
  1.5-4.0s   through the gate, up the steps, courtyard opening up
  4.0-7.0s   rising through the courtyard past the tree
  7.0-10.0s  over the balconies to the roof garden
  10.0-12.0s pergola and skyline; cut back to the street frame to loop

ON-SCREEN TEXT (keep to 4 lines, large, lower third)
  0.5s   "15 m x 30 m. Almost no light."
  3.0s   "So we turned the middle into a courtyard."
  7.0s   "13 homes. Every one faces the garden."
  10.5s  "Five storeys. One tree at the centre."

CAPTION
  A narrow plot, a deep plan, and one idea: put the garden in the
  middle and let every home face it. 12 seconds through the building.

  #architecture #archviz #courtyard #nairobi #reels #architecturelovers
  #blender #3dvisualization #apartmentliving #design

MUSIC
  Calm minimal piano or lo-fi, 90-100 bpm, no vocal. Must be licensed
  for commercial use on Meta and YouTube.
""")

    # ------------------------------------------------------------------ 5
    h(doc, "5.  WhatsApp Status", 1)
    para(doc, "Two or three vertical frames, 9:16, no more than a few seconds each. "
              "Status is casual and personal — it should feel like a peek behind the "
              "scenes, not a campaign.")
    copy_block(doc, """
STATUS 1  (image)  07_Twilight_Street_9x16
  Caption: "Rendered this at 2am. Five storeys on a 15 x 30 m plot."

STATUS 2  (video)  video_fly, first 8 seconds, 9:16
  Caption: "Walking through it before it's built."

STATUS 3  (image)  S03.png (ground floor plan), cropped to 9:16 on the plan
  Caption: "The drawing behind the render."

Keep each status to one image or one short clip. Reply to every
response — status replies are the highest-intent messages you will get.
""")

    # ------------------------------------------------------------------ 6
    h(doc, "6.  X (Twitter)", 1)
    para(doc, "One image plus a short thread. The first post has to work on its own, "
              "because most people never expand it.")
    copy_block(doc, """
POST 1  (attach 07_Twilight_Street at 16:9)
  A 15 x 30 m plot in Nairobi with walls on three sides.
  We put a 112 m2 courtyard in the middle and made all 13 homes
  face it.

  8 renders and a full drawing set in the thread. 🧵

POST 2  (attach 02_Courtyard_Void_Aerial)
  The plan does the work. Every habitable room takes light and air
  from the courtyard, because the boundary walls cannot have windows.
  The courtyard is 112 m2 with a minimum dimension of 7.14 m —
  the code asks for 35 m2 and 4.5 m.

POST 3  (attach 05_L3_Gallery_Overlook)
  Climate response, not decoration:
  · vertical timber fins to the west facade for the 4pm sun
  · 600 mm horizontal hoods to the south courtyard face
  · a colonnade along the north side, shaded by the wing above
  · balconies staggered so none sits over another home's window

POST 4  (attach 08_Aerial_Hero)
  5 storeys, 13 homes, 9 parking bays below ground, a rooftop
  garden with a pergola and 8 kWp of solar.

  Costed at roughly KES 25 M per home including the basement,
  services and professional fees.

POST 5  (attach S06.png — the long section)
  Full set: 8 sheets — plans, sections, elevations, schedules —
  plus a priced bill of quantities.

  Modelled and rendered in Blender. Questions welcome.
""")

    # ------------------------------------------------------------------ 7
    h(doc, "7.  LinkedIn", 1)
    para(doc, "LinkedIn rewards documents and native video over links. Post the drawing "
              "set as a native PDF document, and keep any link out of the post body — put "
              "it in the first comment if you need it at all. Only the first two or three "
              "lines show before 'see more', so the hook is everything.")
    copy_block(doc, """
DOCUMENT POST  (upload the 8-sheet drawing set PDF as a document)

  Hook — first 3 lines, these are all that show:
    "A 15 x 30 m infill plot in Nairobi, walls on three sides, and a
     building that has to light and ventilate itself from the inside."

  Body:
    In a plot like this the code forces the plan. s.129 requires
    200 mm external walls; s.18 and s.19 want open space at the front
    and side that simply does not exist on a 50 x 100 ft site. Both
    are flagged as CONFLICTS requiring county relaxation rather than
    quietly designed around.

    What we could control is the section and the middle:
      · a 112 m2 courtyard open to the sky, every home facing it
      · living rooms opening through 3.5 m glazed walls
      · stacked balconies staggered so daylight reaches the floor below
      · 12.5% basement ramp at 3.18 m clear width, with the second
        escape route through the ramp in lieu of a second stair

    The set attached is the full issue: basement to roof plans,
    two sections, four elevations, door and window schedules, and a
    priced bill of quantities.

    The most useful thing I learned doing it: the glazing panels were
    modelled inside solid walls with no openings cut, so the s.143
    window-area calculation could not actually be verified against the
    geometry. Worth checking on your own projects.

  First comment (not the post body):
    Model, drawings and renders produced in Blender. Schedules and
    cost plan available on request.

  Hashtags: #architecture #construction #quantitysurveying #Nairobi
            #Kenya #design #builtenvironment
""")

    # ------------------------------------------------------------------ 8
    h(doc, "8.  YouTube", 1)
    copy_block(doc, """
SHORT (60 s limit, use the 12 s vertical cut)
  Title:  "13 homes around one courtyard — 15 x 30 m plot"
  Hook:   first 1.5 s is the street elevation; no title card, no logo.
  Loop:   end on the same street frame so the Short restarts cleanly.

LONG FORM (3-4 minutes, 16:9)
  Chapters:
    00:00  The constraint — 15 x 30 m, walls on three sides
    00:25  The courtyard idea, from above
    00:55  The street elevation and the timber fins
    01:30  Inside a home — the 3.5 m glazed wall
    02:10  The roof garden and the solar array
    02:40  The drawings and the cost plan
    03:10  What I would do differently

  Thumbnail: 08_Aerial_Hero, with three words maximum in the overlay.
  Description: include the drawing register and the cost summary, and
  put any external link in the description, never in the first line.
""")

    # ------------------------------------------------------------------ 9
    h(doc, "9.  Cadence and timing", 1)
    table(doc, [
        ("Day 1", "Instagram carousel + LinkedIn document post", "Post the carousel mid-morning; LinkedIn on a weekday morning"),
        ("Day 1", "X thread", "Same day, a few hours later, so the audiences do not overlap"),
        ("Day 2", "Instagram Reel + YouTube Short", "Same 12 s vertical cut, both platforms"),
        ("Day 3", "WhatsApp status sequence", "Three frames across one day; reply to every response"),
        ("Day 5", "Second Reel (orbit cut)", "Different edit and music from the first"),
        ("Day 7", "LinkedIn follow-up", "The cost plan and what the numbers mean"),
        ("Day 10", "Single twilight image on Instagram", "Portfolio anchor, no carousel"),
    ], ["When", "What", "Note"], [1.8, 6.0, 8.4])

    # ------------------------------------------------------------------ 10
    h(doc, "10.  Practical notes", 1)
    bullet(doc, "Never post the same edit twice on the same platform in one week; "
                "Instagram suppresses repeat content.")
    bullet(doc, "Alt text is written for every image and is included on the post, not in "
                "the caption — it is read by screen readers and is a small ranking signal.")
    bullet(doc, "Keep the first line of every caption under 125 characters so it is not "
                "truncated in the feed.")
    bullet(doc, "Reply to every comment in the first hour; early engagement is what "
                "extends reach.")
    bullet(doc, "Put links in the first comment on LinkedIn and X, never in the post body.")
    bullet(doc, "Music must be licensed for commercial use. Use the platform's own "
                "commercial library rather than a personal streaming account.")
    bullet(doc, "Export images at the platform's native size (1080 x 1350 for feed, "
                "1080 x 1920 for Reels and Shorts). Re-uploading a downscaled asset is "
                "the most common cause of a soft-looking post.")
    bullet(doc, "Be accurate about what is built and what is proposed. Nothing here is "
                "constructed; label renders as renders.")

    # ------------------------------------------------------------------ 11
    h(doc, "11.  Sources consulted", 1)
    for t in [
        "Instagram format behaviour for visual work — carousels, Reels and the "
        "re-serve mechanic: https://www.arthelper.com/community/artbusiness/post/"
        "breaking-down-instagram-format-types-for-visual-work",
        "Instagram benchmarks 2025 (Socialinsider): "
        "https://www.socialinsider.io/data-geeks/instagram_benchmarks_2025.pdf",
        "LinkedIn algorithm behaviour for architects and studios: "
        "https://www.thefoundgen.com/architecture-firms-on-linkedin-what-works-what-"
        "wastes-your-morning-and-what-to-post-this-week/",
        "LinkedIn playbook for architecture firms: "
        "https://easymarketingschool.org/the-linkedin-marketing-playbook-for-"
        "architecture-firms-and-studio-owners/",
        "Shorts retention behaviour: https://github.com/aiskillstore/marketplace/blob/"
        "36e07d5e13068e5be64447e8f20b427cf2cbd21a/skills/vyralcontent/viral-youtube-"
        "shorts/references/shorts-retention.md",
        "Hook formulas for short-form video: https://github.com/sergebulaev/"
        "youtube-skills/blob/main/references/hook-formulas.md",
        "X timeline ranking behaviour: https://nibzard.github.io/twitter-algorithm-"
        "tufte/index.html",
    ]:
        bullet(doc, t)

    doc.save(DOCX)
    print(f"wrote {DOCX}")


if __name__ == "__main__":
    build()
