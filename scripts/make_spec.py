"""
make_spec.py -- produce the architectural and engineering specification (DOCX).

  python make_spec.py
"""
import os
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Cm, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(PROJ, "docs", "specification")
os.makedirs(OUT, exist_ok=True)
DOCX = os.path.join(OUT, "Courtyard Apartments - Specification.docx")

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
ACCENT = RGBColor(0xC9, 0x7B, 0x4A)


def h(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    for r in p.runs:
        r.font.color.rgb = NAVY if level <= 2 else ACCENT
    return p


def para(doc, text, style=None, italic=False, bold=False, size=10):
    p = doc.add_paragraph(style=style)
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


def numbered(doc, text):
    p = doc.add_paragraph(text, style="List Number")
    for r in p.runs:
        r.font.size = Pt(10)
    return p


def table(doc, rows, headers, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
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

    # page setup
    for s in doc.sections:
        s.top_margin = Cm(2.2)
        s.bottom_margin = Cm(2.2)
        s.left_margin = Cm(2.4)
        s.right_margin = Cm(2.2)

    st = doc.styles['Normal']
    st.font.name = 'Calibri'
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(6)

    # ---------------- cover ----------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("COURTYARD APARTMENTS")
    r.bold = True
    r.font.size = Pt(28)
    r.font.color.rgb = NAVY
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("50 ft x 100 ft plot  |  15.24 m x 30.48 m  |  Nairobi, Kenya")
    r.font.size = Pt(13)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ARCHITECTURAL AND ENGINEERING SPECIFICATION")
    r.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = ACCENT
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("GF + L1–L4  ·  13 homes  ·  9 basement parking bays  ·  "
                  "single protected stair  ·  8-person lift")
    r.font.size = Pt(11)

    doc.add_paragraph()
    table(doc, [
        ("Project", "Courtyard Apartments, 50 x 100 ft plot, Nairobi"),
        ("Employer", "[To be confirmed]"),
        ("Architect", "[To be confirmed]"),
        ("Structural engineer", "[To be confirmed]"),
        ("Services engineer", "[To be confirmed]"),
        ("Quantity surveyor", "[To be confirmed]"),
        ("Document", "Specification, revision P01"),
        ("Date", "October 2026"),
        ("Status", "For Development Control submission and tender"),
        ("Governing code", "Kenya National Building Code 2024 (Legal Notice 47/2024)"),
    ], ["Item", "Detail"], [4.5, 11.5])

    doc.add_paragraph()
    para(doc, "This specification is to be read with the drawing set "
              "(Courtyard Apartments — Drawing Set, sheets S01–S08), the priced Bill of "
              "Quantities, and the Design Report v3.1. Where documents conflict, the "
              "following order of precedence applies: the Bill of Quantities for measured "
              "quantities; this specification for quality and workmanship; the drawings for "
              "dimensions and layout; the Design Report for design intent.",
         italic=True)

    doc.add_page_break()

    # ---------------- contents ----------------
    h(doc, "Contents", 1)
    sections = [
        ("A", "General requirements and preliminaries"),
        ("B", "Site works, excavation and substructure"),
        ("C", "Concrete — materials, mixing and workmanship"),
        ("D", "Reinforcement and structural steel"),
        ("E", "Masonry — quarry stone and ISSB blockwork"),
        ("F", "Waterproofing, roofing and rainwater disposal"),
        ("G", "Carpentry, joinery and timber"),
        ("H", "Metalwork, balustrades and architectural metal"),
        ("I", "Aluminium glazing, windows, doors and ironmongery"),
        ("J", "Plaster, screeds, tiling and finishes"),
        ("K", "Painting and decoration"),
        ("L", "Plumbing, drainage and water services"),
        ("M", "Electrical installation, ICT and security"),
        ("N", "Fire and life safety"),
        ("O", "Lift installation"),
        ("P", "Renewable energy — solar PV and solar water heating"),
        ("Q", "External works, drainage and landscape"),
        ("R", "Quality assurance, testing, commissioning and handover"),
        ("S", "Schedules — doors, windows and finishes"),
    ]
    for a, b in sections:
        p = doc.add_paragraph()
        r = p.add_run(f"{a}.  ")
        r.bold = True
        r.font.color.rgb = NAVY
        p.add_run(b)

    doc.add_page_break()

    # ---------------- A ----------------
    h(doc, "A.  General requirements and preliminaries", 1)
    h(doc, "A1  Scope", 2)
    para(doc, "The works comprise the construction of a five-storey courtyard apartment "
              "building on a 15.24 m x 30.48 m plot, with a single basement parking level, "
              "thirteen dwellings, a ground-floor commercial unit, a guarded pedestrian and "
              "vehicular entry, a communal roof garden, and all associated external works, "
              "services and landscaping, complete and ready for occupation.")
    h(doc, "A2  Standards", 2)
    para(doc, "Work is to comply with the Kenya National Building Code 2024 (LN 47/2024), "
              "Kenya Bureau of Standards (KEBS) standards where applicable, and with the "
              "British Standards / European Standards and ASTM standards cited in each "
              "section. Where a KEBS standard exists it takes precedence.")
    table(doc, [
        ("Concrete", "KS EN 206-1, BS 8500"),
        ("Reinforcement", "KS EN 10080, BS 4449"),
        ("Masonry units", "KS EN 771, KS 2029 (ISSB)"),
        ("Cement", "KS EN 197-1, KS EAS 18-1"),
        ("Structural design", "Eurocode 2 (BS EN 1992) with Kenya National Annex"),
        ("Timber", "KS EN 14081, KS 1536"),
        ("Water supply", "KS EN 806, KS 1966"),
        ("Electrical", "KS IEC 60364, Kenya Electricity Wiring Regulations 2019"),
    ], ["Element", "Standard"], [5.0, 11.0])
    h(doc, "A3  Programme and sequence", 2)
    para(doc, "The indicated construction period is twenty-six months. The Contractor is to "
              "submit a resource-loaded programme within twenty-one days of award. "
              "Preliminary works for the basement are on the critical path and are to be "
              "supported by a designed dewatering and shoring scheme.")
    h(doc, "A4  Access and working hours", 2)
    bullet(doc, "Vehicular access to the site is from the west street frontage only. The "
                "existing boundary walls form the site perimeter and are to be maintained.")
    bullet(doc, "Working hours 07:00 to 18:00 Monday to Saturday. No noisy work before "
                "08:00 or after 17:00, and none on Sundays or public holidays.")
    bullet(doc, "The public footway and carriageway are to remain unobstructed and clean.")
    h(doc, "A5  Samples, mock-ups and approvals", 2)
    para(doc, "Submit samples of every finish, unit and component for the Architect's "
              "approval before ordering. Construct a full-size mock-up of one typical "
              "bathroom and one balcony balustrade bay, including the sun hood and planter, "
              "and obtain approval before proceeding with repetition.")
    h(doc, "A6  Setting out", 2)
    para(doc, "The Contractor is responsible for setting out and for verifying all "
              "dimensions on site. Grid lines are referenced A–G (X axis, north to south) "
              "and 1–8 (Y axis, west/street to east/rear) as shown on the drawings. "
              "Report any discrepancy before commencing the affected work.")

    # ---------------- B ----------------
    h(doc, "B.  Site works, excavation and substructure", 1)
    bullet(doc, "Site strip and cart away all vegetation, topsoil and obstructions. "
                "Stockpile acceptable topsoil for reuse in the courtyard and roof garden.")
    bullet(doc, "Rock, if encountered, to be removed by controlled means with a written "
                "method statement and prior approval.")
    bullet(doc, "Excavate to the levels shown for the basement, sump and lift pit. Keep "
                "excavations dry by open pumping with settlement monitoring of adjacent "
                "property; provide a designed dewatering scheme.")
    bullet(doc, "Blinding concrete grade 15, 50 mm thick, on compacted formation.")
    bullet(doc, "Raft and basement slab: grade 30 concrete, 300 mm thick, with drop panels "
                "where spans exceed 6.0 m. Provide a continuous tanked waterproofing system.")
    bullet(doc, "Retaining walls: 250–300 mm reinforced concrete, designed for at-rest "
                "earth pressure plus surcharge from the street.")
    bullet(doc, "Backfill in 200 mm layers, each compacted to 95% modified AASHTO density, "
                "using approved granular material free of organic matter.")
    bullet(doc, "Vehicle ramp: 12.5% maximum gradient, 3.18 m clear width, 450 mm kerb to "
                "the open side in accordance with s.41 and s.44, grooved finish, crest and "
                "bottom trench drains, and a convex mirror at the street.")
    para(doc, "The Contractor is to satisfy himself as to ground conditions. The design "
              "assumes Nairobi murram over weathered volcanic tuff; a geotechnical "
              "investigation is required before excavation and the Engineer is to confirm "
              "the founding stratum.", italic=True)

    # ---------------- C ----------------
    h(doc, "C.  Concrete — materials, mixing and workmanship", 1)
    bullet(doc, "Cement: ordinary Portland cement to KS EAS 18-1, from an approved "
                "manufacturer, delivered in sealed bags or bulk, used within three months "
                "of manufacture.")
    bullet(doc, "Aggregates: clean, hard, durable crushed stone or natural gravel to KS EN "
                "12620, graded 20 mm nominal for structural concrete. Sand to be washed "
                "river or pit sand, free of silt and clay; silt content not exceeding 4% by "
                "volume by the field settlement test.")
    bullet(doc, "Water: potable, free of oils, acids, alkalis and organic matter.")
    bullet(doc, "Grades: grade 15 for blinding; grade 25 for non-structural fills and "
                "kerbs; grade 30 for all structural members, raft and retaining walls; "
                "grade 40 only where shown.")
    bullet(doc, "Mix design: designed mixes by weight, with trial mixes approved before "
                "use. Nominal mixes are not permitted for structural concrete.")
    bullet(doc, "Slump: 75–125 mm for pumped concrete; 25–75 mm for hand-placed. "
                "No water to be added on site to restore workability; use a plasticiser.")
    bullet(doc, "Placing: within 30 minutes of mixing; vibrated with needle vibrators of "
                "appropriate diameter, avoiding contact with reinforcement and formwork.")
    bullet(doc, "Curing: keep surfaces continuously moist for at least seven days; "
                "fourteen days for raft and retaining walls. Use polythene sheeting or "
                "ponding in hot weather.")
    bullet(doc, "Formwork: plywood or steel, true to line and level, with tight joints, "
                "release agent, and designed to resist the full hydrostatic pressure of "
                "the wet concrete.")
    bullet(doc, "Tolerances: as BS EN 13670 Class 1 for verticality (±10 mm per storey), "
                "flatness (5 mm under a 3 m straight edge) and cover.")
    bullet(doc, "Cover to reinforcement: 40 mm for foundations in contact with earth, "
                "30 mm for external faces, 20 mm for internal faces, 20 mm for slabs.")

    # ---------------- D ----------------
    h(doc, "D.  Reinforcement and structural steel", 1)
    bullet(doc, "Reinforcement: high-yield deformed bars to BS 4449 grade B500B, with "
                "mill certificates for every consignment. Store clear of the ground and "
                "free of loose rust, scale, oil or paint.")
    bullet(doc, "Cutting and bending to BS 8666. Laps and anchorage as the Engineer's "
                "drawings, minimum lap 40 bar diameters unless shown otherwise.")
    bullet(doc, "Fix with galvanised or plastic-coated tying wire; use approved spacers "
                "and chairs to maintain cover and position. No reinforcement to be fixed "
                "on the ground without a blinding layer.")
    bullet(doc, "Mechanical couplers, where used, to be an approved proprietary system "
                "with type-test certificates.")
    bullet(doc, "Post-tensioning to balcony cantilevers, where designed, to be executed "
                "by a specialist sub-contractor with a chartered engineer's check, "
                "including tendon layout, stressing records and grouting.")
    bullet(doc, "Structural steel to BS EN 10025 S275, galvanised to BS EN ISO 1461 for "
                "external and wet locations, and shop-primed elsewhere.")

    # ---------------- E ----------------
    h(doc, "E.  Masonry — quarry stone and ISSB blockwork", 1)
    h(doc, "E1  Machine-cut quarry stone", 2)
    bullet(doc, "Stone to be sound, durable, free from cracks and weathered faces, "
                "machine cut to approximately 200 x 200 x 400 mm, with a minimum "
                "compressive strength of 5 N/mm².")
    bullet(doc, "External and party walls minimum 200 mm thick in accordance with s.129.")
    bullet(doc, "Mortar 1:4 cement–sand by volume for load-bearing walls, with plasticiser "
                "only where approved. Joints 10–12 mm, flush or slightly recessed on "
                "fair-faced work, and raked on surfaces to be rendered.")
    bullet(doc, "Render: two-coat cement–sand render, 12–15 mm total, off-white, with "
                "expanded metal lath across all dissimilar material junctions and a "
                "proprietary bonding agent as required.")
    h(doc, "E2  Interlocking stabilised soil blocks (ISSB)", 2)
    bullet(doc, "Blocks approximately 300 x 150 x 100 mm, machine-pressed from approved "
                "soil, cement-stabilised, cured a minimum of fourteen days, with a minimum "
                "wet compressive strength of 3.5 N/mm² and absorption below 15%.")
    bullet(doc, "ISSB is used for the guard house, shop and store walls, courtyard "
                "feature walls, raised planters and seat walls, the ramp screen wall "
                "(courtyard face), internal partitions, and parapets with concrete coping.")
    bullet(doc, "Never below ground or as a structural member. Provide a concrete plinth "
                "at least 150 mm high under every ISSB wall.")
    bullet(doc, "Fair-faced work: uniform colour and texture, mortar joints 8–10 mm, "
                "struck flush and finished with a soft brush on setting. No cutting of "
                "blocks on the face of the work.")
    bullet(doc, "Sample panel of 1.5 m x 1.5 m to be approved before general work.")

    # ---------------- F ----------------
    h(doc, "F.  Waterproofing, roofing and rainwater disposal", 1)
    bullet(doc, "Basement: fully tanked system to the raft, retaining walls and lift pit. "
                "Use a bonded elastomeric membrane or a crystalline waterproofing admixture "
                "plus membrane, with protection board. Wet-test each compartment for "
                "72 hours before backfilling and again before handover.")
    bullet(doc, "Roof: screed laid to falls with a minimum 1:80 fall to outlets, 4 mm "
                "torch-on elastomeric membrane with a mineral or screed protection layer, "
                "and 50 mm lap at all upstands. Upstands minimum 150 mm above finished "
                "roof level, 250 mm at door thresholds.")
    bullet(doc, "Waterproofing to balconies, planters and the roof garden, including all "
                "upstands, with a root-resistant membrane beneath all planting.")
    bullet(doc, "Rainwater goods: UPVC or coated aluminium gutters and downpipes, sized "
                "for a 1-in-50-year storm at 150 mm/hour intensity, with leaf guards. "
                "Direct roof runoff to the rainwater harvesting tank or soakaway.")
    bullet(doc, "Provide a rainwater harvesting system with first-flush diversion, "
                "screening and a 15 m³ storage tank for irrigation and WC flushing.")
    bullet(doc, "Concealed gutters to galleries to be formed in the same waterproofing "
                "system, fully lined, with accessible inspection outlets.")

    # ---------------- G ----------------
    h(doc, "G.  Carpentry, joinery and timber", 1)
    bullet(doc, "Timber to be kiln-dried to 12–15% moisture content, graded to KS 1536, "
                "free of knots larger than one third of the face width, shakes, splits "
                "and fungal attack.")
    bullet(doc, "Structural timber to be grade C24 or better. All timber in external "
                "locations to be naturally durable (Class 1 or 2) or pressure-treated "
                "with a copper-based preservative.")
    bullet(doc, "Vertical timber-look brise-soleil fins to the west facade: 50 x 100 mm "
                "section, thermally treated or modified timber, fixed with stainless "
                "steel brackets to the concrete frame, with a 10 mm shadow gap and "
                "adjustable fixing to accommodate movement.")
    bullet(doc, "Roof pergola: 150 x 150 mm posts, 100 x 200 mm beams and 50 x 150 mm "
                "rafters at 600 mm centres, all with a chamfered profile and a penetrating "
                "exterior finish.")
    bullet(doc, "Timber decking and seat slats: 25 mm thick, 8 mm gaps, stainless steel "
                "screws, joists above a drained and ventilated void.")
    bullet(doc, "All exposed timber to receive a factory-applied UV-stable finish and one "
                "site-applied maintenance coat before handover.")

    # ---------------- H ----------------
    h(doc, "H.  Metalwork, balustrades and architectural metal", 1)
    bullet(doc, "Balustrades 1.10 m high to all balconies, galleries and roof terraces in "
                "accordance with s.17, with vertical bars at maximum 95 mm centres to "
                "prevent passage of a 100 mm sphere, and a continuous handrail with no "
                "projecting ends.")
    bullet(doc, "Steel to BS EN 10025 S275, powder-coated to a minimum 60 micron dry film "
                "thickness in a charcoal colour, with galvanising to BS EN ISO 1461 for "
                "all external locations. Colour to be approved from a physical sample.")
    bullet(doc, "All fixings external and in wet areas to be stainless steel grade 316.")
    bullet(doc, "Planter boxes to galleries and balconies: 1.2 mm folded steel or precast "
                "concrete, fully lined, with drainage outlets and a 50 mm drainage layer.")
    bullet(doc, "Accessible ramp handrails both sides at 900 mm and 700 mm above the "
                "ramp surface, with 300 mm extensions beyond the top and bottom.")
    bullet(doc, "Metalwork to receive a zinc-rich primer at all cut edges and welds "
                "before the finishing coat.")

    # ---------------- I ----------------
    h(doc, "I.  Aluminium glazing, windows, doors and ironmongery", 1)
    bullet(doc, "Aluminium: extruded sections to BS EN 755, alloy 6063 T6, powder coated "
                "to a minimum 40 micron dry film thickness, marine-grade finish.")
    bullet(doc, "Glazing: 6 mm low-E toughened glass outer, 12 mm argon-filled cavity, "
                "6 mm clear toughened inner, with warm-edge spacer. U-value not exceeding "
                "1.6 W/m²K and SHGC not exceeding 0.35 to the west and south elevations.")
    bullet(doc, "Living-room glazing 3.5 m wide x 2.4 m high per dwelling, with an "
                "openable top-hung casement giving at least 5% of the floor area openable "
                "above 1.75 m, in accordance with s.143(3).")
    bullet(doc, "Full perimeter gaskets, drained and ventilated sills, and concealed "
                "fixings. Provide a 100 mm minimum reveal and a proprietary cavity closer.")
    bullet(doc, "Watertightness to BS EN 12208 class 9A, air permeability to BS EN 12207 "
                "class 4, wind resistance to BS EN 12210 class C3.")
    bullet(doc, "Integral fly screens to all habitable-room openable windows.")
    bullet(doc, "Ironmongery to be an approved architectural range, satin stainless steel "
                "or powder-coated to match, with a master-keyed suite; provide three keys "
                "per dwelling and a maintenance set.")
    bullet(doc, "Vehicle door: motorised sectional door, 2.9 m x 3.1 m, insulated, with "
                "two remote handsets, safety edge, manual release, and red/green traffic "
                "signals with an amber flasher and audible warning interlocked to the door "
                "position.")
    bullet(doc, "Pedestrian gate: steel door with an electro-mechanical lock, video "
                "intercom and a guard-house release.")

    # ---------------- J ----------------
    h(doc, "J.  Plaster, screeds, tiling and finishes", 1)
    bullet(doc, "Internal plaster: two-coat gypsum or cement–sand plaster, 12 mm, to a "
                "Class B finish, with corner beads, stop beads and a scrim over all joints.")
    bullet(doc, "Floor screed: cement–sand 1:4, 40–65 mm, laid monolithically where "
                "possible, cured and dried to below 75% relative humidity before tiling.")
    bullet(doc, "Floor tiling: 600 x 600 mm porcelain, class 4 abrasion resistance, laid "
                "with a flexible adhesive on a levelling compound, 3 mm joints, grouted "
                "with a stain-resistant epoxy grout, with 100 mm skirting.")
    bullet(doc, "Wall tiling: 300 x 600 mm ceramic to bathrooms and kitchens to a height "
                "of 2.1 m, with a waterproof tanking system to all wet areas before tiling.")
    bullet(doc, "Basement floor: epoxy resin coating, 300 microns, in a light grey, with a "
                "non-slip finish to ramps and bay markings in white and blue.")
    bullet(doc, "Courtyard paving: permeable concrete block paving on a permeable bedding "
                "and sub-base, laid to a 1:80 fall away from the building, with ISSB "
                "seating edging.")
    bullet(doc, "Lawn: 300 mm growing medium on a drainage layer, with a filter geotextile "
                "and a subsurface irrigation system.")
    bullet(doc, "Movement joints to be provided in all screeds and tiling at 6 m centres "
                "and at every change of substrate.")

    # ---------------- K ----------------
    h(doc, "K.  Painting and decoration", 1)
    bullet(doc, "All surfaces to be clean, dry, sound and correctly prepared before "
                "decoration. Fill, rub down and prime as required.")
    bullet(doc, "External: alkali-resistant primer followed by two coats of a 100% acrylic "
                "masonry paint, matt, in an approved colour. Total dry film thickness not "
                "less than 120 microns.")
    bullet(doc, "Internal walls and ceilings: two coats of low-VOC matt emulsion on a "
                "thinned primer; washable finish to kitchens and bathrooms.")
    bullet(doc, "Timber: one coat of knotting and primer, two undercoats and two gloss or "
                "satin topcoats in an approved colour.")
    bullet(doc, "Metal: zinc phosphate primer, two undercoats and two topcoats; "
                "galvanised surfaces to be treated with a mordant solution before priming.")
    bullet(doc, "Provide a paint schedule with manufacturer, product reference, colour and "
                "sheen for approval, and leave 5 litres of each colour for maintenance.")

    # ---------------- L ----------------
    h(doc, "L.  Plumbing, drainage and water services", 1)
    bullet(doc, "Water supply: 25 mm high-density polyethylene service from the meter to a "
                "15 m³ storage tank, then a duplex booster pump set with a pressure vessel "
                "delivering a minimum 1.5 bar at the most remote outlet.")
    bullet(doc, "Distribution: PPR or PEX pipework in conduits or ducts, with isolation "
                "valves at every fixture group and a manifold per dwelling. No pipework "
                "buried in structural concrete without a duct.")
    bullet(doc, "Drainage: 110 mm UPVC soil and waste stacks with access fittings at every "
                "change of direction, vented to above roof level; 160 mm below-ground "
                "drainage to inspection chambers at maximum 15 m spacing.")
    bullet(doc, "All bathroom floors to be tanked and laid to a fall to a trapped gully; "
                "provide a floor waste to every bathroom.")
    bullet(doc, "Hot water: solar pre-heat with an electric backup element in each "
                "dwelling, or a central solar installation with a circulation loop — "
                "confirm the selected option before ordering.")
    bullet(doc, "Sanitaryware: white vitreous china, close-coupled WC suites with dual "
                "flush (maximum 4.5/3 litres), basin with a mixer tap, and a shower mixer "
                "with a low-flow head. One bathroom per dwelling to be accessible.")
    bullet(doc, "Rainwater harvesting: separate pipework to WCs and irrigation, clearly "
                "labelled, with a first-flush diverter and a filtration unit.")
    bullet(doc, "Pressure-test all pipework at 1.5 times working pressure for one hour "
                "with no loss, and record the results.")

    # ---------------- M ----------------
    h(doc, "M.  Electrical installation, ICT and security", 1)
    bullet(doc, "Supply: three-phase 400 V, 50 Hz, from the utility with a main "
                "switchboard, metering per dwelling in a ground-floor cabinet, and a "
                "60 kVA standby generator with automatic changeover.")
    bullet(doc, "Installation to KS IEC 60364 and the Kenya Electricity Wiring "
                "Regulations 2019. All circuits to be protected by RCBOs at 30 mA.")
    bullet(doc, "Containment: PVC conduit concealed in walls and slabs; no surface wiring. "
                "Provide draw wires to all future points.")
    bullet(doc, "Dwellings: a distribution board per unit, a minimum of two socket outlets "
                "per bedroom, four in the living room, dedicated circuits for the cooker, "
                "water heater and air conditioning, and LED lighting throughout.")
    bullet(doc, "Common areas: LED lighting with photocell and time-clock control, "
                "emergency lighting to escape routes with 3-hour battery duration, and a "
                "fire alarm system with a manual call point at each landing.")
    bullet(doc, "External lighting: bollards and wall-mounted fittings to the forecourt, "
                "courtyard, ramp and roof terrace, dark-sky compliant (no upward light).")
    bullet(doc, "Earthing and lightning protection: a ring earth electrode bonded to all "
                "metallic services, with a surge protective device at the main board and "
                "an air termination system to BS EN 62305.")
    bullet(doc, "ICT: fibre entry to a communications cabinet, structured cabling to every "
                "dwelling, and a TV and data outlet in each living room and bedroom.")
    bullet(doc, "Security: CCTV coverage of the gate, ramp, courtyard and all circulation, "
                "with recording for 30 days; access control to the pedestrian gate, lift "
                "lobby and basement; and video intercom to each dwelling.")

    # ---------------- N ----------------
    h(doc, "N.  Fire and life safety", 1)
    bullet(doc, "Single protected stair serving all levels including the basement, with a "
                "60-minute fire-resisting construction, self-closing fire doors at every "
                "landing, and a smoke lobby at the basement and ground floor.")
    bullet(doc, "The stair is one of two escape routes; the vehicle ramp is the second for "
                "the basement only, in accordance with s.400. Stair and ramp head "
                "entrances are separated by approximately 17.8 m, satisfying s.401(2).")
    bullet(doc, "Stair continues to roof level with a roof exit door in accordance with "
                "s.194(2).")
    bullet(doc, "Automatic fire detection to all common areas and the basement, with "
                "sounders audible in every dwelling and a main panel in the guard house.")
    bullet(doc, "Fire extinguishers: CO2 and dry powder at every landing, in the plant "
                "rooms and in the basement at maximum 15 m travel distance.")
    bullet(doc, "Basement ventilation: two extract shafts raising 6 air changes per hour "
                "in normal operation and 10 ACH in fire mode, discharging at least 1 m "
                "above the roof parapet and away from any window, in accordance with "
                "s.156.")
    bullet(doc, "All fire-resisting elements to be supported by test certificates and "
                "marked with a permanent identification plate.")
    para(doc, "Fire strategy, ratings and means of escape must be confirmed by a "
              "specialist fire engineer before construction. Nothing in this "
              "specification constitutes a fire-engineered design.", italic=True)

    # ---------------- O ----------------
    h(doc, "O.  Lift installation", 1)
    bullet(doc, "One machine-room-less traction lift, 630 kg / 8 persons, serving six "
                "stops (B1, GF, L1, L2, L3, L4) at 1.0 m/s, with a car size sufficient "
                "for an ambulance stretcher, in accordance with KS ISO 8100.")
    bullet(doc, "Car and landing finishes to match the approved architectural schedule; "
                "stainless steel car doors, mirror, handrail, and LED lighting.")
    bullet(doc, "Controls: collective selective with a car operating panel, landing call "
                "stations at every level, battery lowering, emergency intercom, and "
                "automatic return to the ground floor on alarm.")
    bullet(doc, "Provide a two-year maintenance contract and the statutory test "
                "certificate on completion.")
    bullet(doc, "Accessibility: lift lobby and car to provide an accessible route to the "
                "accessible parking bay and to every dwelling, in accordance with "
                "KS ISO 21542.")

    # ---------------- P ----------------
    h(doc, "P.  Renewable energy — solar PV and solar water heating", 1)
    bullet(doc, "Roof-mounted photovoltaic array of approximately 8 kWp, with "
                "monocrystalline modules, an aluminium mounting system ballasted or "
                "mechanically fixed to the roof slab without penetrating the "
                "waterproofing, and string inverters in the lift plant room.")
    bullet(doc, "Modules to be rated at least 400 Wp with a 25-year performance warranty "
                "and a 12-year product warranty. Inverters to have a 10-year warranty.")
    bullet(doc, "Generation to serve common-area lighting, pumps and the lift, with "
                "surplus exported or diverted to water heating. Provide metering and a "
                "display in the lobby.")
    bullet(doc, "Solar water heating: evacuated tube or flat-plate collectors serving "
                "communal pre-heat, sized for a minimum 50% annual solar fraction, with "
                "a thermosiphon or pumped circuit, freeze protection, and an electric "
                "backup.")
    bullet(doc, "Structural capacity for the array, tank and plant to be confirmed by the "
                "Engineer. Provide safe access and fall-arrest anchor points for "
                "maintenance.")

    # ---------------- Q ----------------
    h(doc, "Q.  External works, drainage and landscape", 1)
    bullet(doc, "Carriageway and forecourt: 60 mm dense bituminous macadam on a 200 mm "
                "crushed stone base, with kerbs, channel, and thermoplastic road markings "
                "including a zebra crossing at the pedestrian gate.")
    bullet(doc, "Footways: 60 mm permeable concrete block paving on a permeable sub-base, "
                "laid to a 1:60 fall away from the building.")
    bullet(doc, "Surface water: separate system with gullies at maximum 25 m spacing, "
                "inspection chambers, and discharge to a soakaway or the public system as "
                "approved. Provide attenuation for a 1-in-30-year storm.")
    bullet(doc, "Foul drainage: separate system to the public sewer, with inspection "
                "chambers at every change of direction and at maximum 15 m spacing.")
    bullet(doc, "Courtyard: permeable paving to paths, ISSB seating walls, raised planters "
                "with a 600 mm soil depth, a rain garden fed by downpipe overflow, and "
                "one multi-stem feature tree in a 1.2 m deep planter.")
    bullet(doc, "Soft landscape to at least 50% of the open courtyard: trees, shrubs, "
                "climbers on the ramp screen wall and the GF party wall, and ground cover.")
    bullet(doc, "Irrigation: drip or subsurface system with a soil-moisture controller, "
                "fed from harvested rainwater.")
    bullet(doc, "Roof garden: planting to a minimum 300 mm soil depth over a drainage "
                "cell, with wind-resistant species and a protected waterproofing system.")
    bullet(doc, "Reinstate all surfaces disturbed by the works to at least their original "
                "condition, and make good to the satisfaction of the local authority.")

    # ---------------- R ----------------
    h(doc, "R.  Quality assurance, testing, commissioning and handover", 1)
    h(doc, "R1  Testing", 2)
    table(doc, [
        ("Concrete", "Slump and cube tests at every 20 m³ or one per pour, 7 and 28 day"),
        ("Reinforcement", "Mill certificates; visual inspection before every pour"),
        ("Compaction", "Field density test per 200 mm layer of backfill"),
        ("Waterproofing", "72-hour flood test to basement and roof; 24-hour to planters"),
        ("Drainage", "Water test and air test to every stack and run"),
        ("Pressure pipework", "1.5 x working pressure for 1 hour, no loss"),
        ("Electrical", "Insulation resistance, earth loop impedance, RCD trip test"),
        ("Glazing", "Watertightness and air permeability to the specified classes"),
        ("Lift", "Statutory examination and load test before handover"),
    ], ["Element", "Test"], [4.5, 11.5])
    h(doc, "R2  Handover", 2)
    bullet(doc, "Provide a complete set of as-built drawings in PDF and editable format, "
                "and a building information model if produced.")
    bullet(doc, "Provide operation and maintenance manuals for every installed system, "
                "with manufacturer contacts, maintenance schedules and spare parts lists.")
    bullet(doc, "Provide training for the building manager and the residents' committee on "
                "the lift, pump set, generator, fire panel, solar system and irrigation.")
    bullet(doc, "Provide all statutory certificates: occupation certificate, electrical "
                "certificate of compliance, plumbing certificate, lift certificate, and "
                "fire safety certificate.")
    bullet(doc, "Defects liability period: twelve months from practical completion, with a "
                "retention of 5% released in two halves in accordance with the contract.")
    bullet(doc, "Provide a maintenance manual for the soft landscape covering watering, "
                "feeding, pruning and replacement for the first two years.")

    # ---------------- S ----------------
    h(doc, "S.  Schedules — doors, windows and finishes", 1)
    h(doc, "S1  Window schedule", 2)
    table(doc, [
        ("W1", "Living room, courtyard face", "3500 x 2400", "Aluminium sliding, low-E DGU", "37"),
        ("W2", "Bedroom, street or courtyard", "1800 x 1500", "Aluminium sliding, low-E DGU", "26"),
        ("W3", "Bedroom 2, courtyard", "1500 x 1500", "Aluminium sliding, low-E DGU", "13"),
        ("W4", "Kitchen", "1200 x 1200", "Aluminium casement with top opener", "13"),
        ("W5", "Bathroom", "600 x 600", "Aluminium top-hung, obscured glass", "20"),
        ("W6", "Stair and gallery", "1200 x 1500", "Aluminium fixed, low-E DGU", "10"),
    ], ["Ref", "Location", "Size (mm)", "Type", "No."], [1.6, 4.4, 3.0, 5.4, 1.6])
    h(doc, "S2  Door schedule", 2)
    table(doc, [
        ("D1", "Flat entrance", "900 x 2100", "Solid core timber, fire-rated, security lock", "13"),
        ("D2", "Internal room", "800 x 2100", "Flush timber, satin stainless ironmongery", "55"),
        ("D3", "Bathroom", "700 x 2100", "Flush timber, privacy lock", "20"),
        ("D4", "Stair and lobby, fire", "900 x 2100", "Steel, 60 min fire-rated, self-closing", "12"),
        ("D5", "Shop entrance", "2750 x 3000", "Glazed shopfront with roller shutter", "1"),
        ("D6", "Vehicle portal", "2900 x 3100", "Motorised insulated sectional door", "1"),
        ("D7", "Pedestrian gate", "1600 x 2400", "Steel, intercom and electric lock", "1"),
        ("D8", "Store and plant", "900 x 2100", "Steel louvre door", "6"),
    ], ["Ref", "Location", "Size (mm)", "Type", "No."], [1.6, 3.8, 3.0, 6.0, 1.6])
    h(doc, "S3  Finishes schedule (typical dwelling)", 2)
    table(doc, [
        ("Floor", "Living, bedrooms", "600x600 porcelain tile on screed, 100 mm skirting"),
        ("Floor", "Kitchen, bathrooms", "300x300 anti-slip porcelain, tanked substrate"),
        ("Wall", "Living, bedrooms", "Plaster, primer, two coats low-VOC matt emulsion"),
        ("Wall", "Kitchen, bathrooms", "300x600 ceramic to 2.1 m, tanked, remainder emulsion"),
        ("Ceiling", "All rooms", "Plaster on slab soffit, two coats matt emulsion"),
        ("Ceiling", "Bathrooms", "Moisture-resistant plasterboard, washable paint"),
        ("Joinery", "Kitchen", "Moisture-resistant carcasses, quartz worktop, soft-close"),
        ("Joinery", "Wardrobes", "Built-in, timber veneer doors, hanging and shelf"),
    ], ["Element", "Location", "Specification"], [2.2, 4.0, 9.8])

    doc.add_page_break()
    h(doc, "Appendix 1 — Compliance register", 1)
    para(doc, "Refer to the Design Report v3.1 and Drawing S08 for the full compliance "
              "register against the Kenya National Building Code 2024 (LN 47/2024). The "
              "position at the date of this specification is summarised below.")
    table(doc, [
        ("s.17", "Balustrades >= 1.0 m", "1.10 m", "PASS"),
        ("s.18", "6 m open front space", "shop and guard on boundary", "CONFLICT — waiver"),
        ("s.19", "1.5 m open side space", "walls on both boundaries", "CONFLICT — waiver"),
        ("s.20", "Courtyard >= 35 m2, min dim 4.5 m", "112.1 m2, 7.14 m", "PASS"),
        ("s.21", "<= 5 storeys, single stair acceptable", "5 storeys, stair + ramp", "PASS"),
        ("s.38", "EV bays >= 5%", "1 of 9 = 11.1%", "PASS"),
        ("s.44", "Ramp <= 12.5%, width >= 3.0 m", "12.5%, 3.18 m", "PASS"),
        ("s.129", "External walls >= 200 mm", "200 mm stone + 300 RC", "PASS"),
        ("s.137", "Zone of space >= H/3", "7.14 m >= 4.37 m", "PASS"),
        ("s.143(1)", "Windows >= 10% of floor area", "NOT VERIFIED in model", "NOTE"),
        ("s.143(2)", "Glazing + balcony uplift >= 30%", "NOT VERIFIED in model", "NOTE"),
        ("s.156", "Basement extract >= 6 ACH", "2 shafts, MEP to size", "PASS"),
        ("s.194(2)", "Stair continues to roof", "to +19.00 m", "PASS"),
        ("s.205", "Risers 150–180, treads 250–320", "176 / 280 mm", "PASS"),
        ("s.353", "Accessible bay 3.6 m by lift", "Bay 01", "PASS"),
        ("s.400", "Basement 2 escape routes", "stair + ramp", "PASS"),
    ], ["Clause", "Requirement", "Value", "Result"], [2.0, 6.0, 5.0, 3.0])
    para(doc, "s.143(1) and (2) cannot be signed off against the current model: the "
              "glazing panels exist but the saved model has no openings cut in the host "
              "walls, so the window area is not delivered by the geometry. Refer to the "
              "Model QA and Render Notes. This must be resolved before any submission "
              "that relies on the window-area calculation.", italic=True)

    doc.save(DOCX)
    print(f"wrote {DOCX}")
    print(f"  paragraphs: {len(doc.paragraphs)}, tables: {len(doc.tables)}")


if __name__ == "__main__":
    build()
