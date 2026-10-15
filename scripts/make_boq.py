"""
make_boq.py -- build the priced Bill of Quantities workbook.

Elemental BOQ in the Kenyan market format: measured items grouped by element,
with rate build-ups, a summary ascending to a contract sum, and a cash-flow.
Rates are indicative Nairobi market rates for 2026 and must be confirmed by
tender.

  python make_boq.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(PROJ, "docs", "costing")
os.makedirs(OUT, exist_ok=True)
XLSX = os.path.join(OUT, "Courtyard Apartments - Bill of Quantities.xlsx")

NAVY = "1F3A5F"
ACCENT = "C97B4A"
GREY = "F1F2F4"
MONEY = '#,##0'
MONEY2 = '#,##0.00'

thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def style_title(ws, row, text, span, size=13):
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(bold=True, size=size, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(vertical="center", indent=1)
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    ws.row_dimensions[row].height = 22
    return row + 1


def style_header(ws, row, headers, widths):
    for i, (h, w) in enumerate(zip(headers, widths), start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = Font(bold=True, size=9, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=ACCENT)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 26
    return row + 1


# ---------------------------------------------------------------- BOQ data
# (element code, description, unit, qty, rate KES)
ITEMS = [
    ("A", "PRELIMINARIES AND GENERAL ITEMS", None, None, None),
    ("A10", "Site establishment, hoarding, site office and welfare, 12 months", "sum", 1, 2_850_000),
    ("A20", "Temporary services: water, power, site drainage", "sum", 1, 1_450_000),
    ("A30", "Plant, scaffolding and hoisting, 12 months", "sum", 1, 3_600_000),
    ("A40", "Insurance, bonds and statutory approvals", "sum", 1, 1_950_000),
    ("A50", "Site supervision and safety, 12 months", "sum", 1, 4_200_000),

    ("B", "SUBSTRUCTURE  —  BASEMENT AND PODIUM", None, None, None),
    ("B10", "Bulk excavation to basement, cart away", "m3", 1180, 780),
    ("B20", "Disposal of surplus excavation off site", "m3", 940, 1_150),
    ("B30", "Hardcore bed and compacted murram filling", "m3", 320, 3_150),
    ("B40", "Blinding concrete 50 mm grade 15", "m2", 620, 1_250),
    ("B50", "Raft / basement slab, RC grade 30, 300 mm", "m3", 210, 33_500),
    ("B60", "Basement retaining walls, RC 250-300 mm", "m2", 690, 17_800),
    ("B70", "Waterproofing to retaining walls and raft (tanked)", "m2", 980, 3_450),
    ("B80", "Podium suspended slab, RC 300 mm with drop panels", "m3", 176, 35_200),
    ("B90", "Vehicle ramp: RC walls, slab, kerbs and grooves", "m2", 148, 24_500),
    ("B100", "Sunken water tank, RC, 27 m3, with pump chamber", "sum", 1, 1_850_000),
    ("B110", "Basement drainage, sump and pump set", "sum", 1, 780_000),
    ("B120", "Foundations to boundary walls and gate posts", "m3", 46, 28_400),

    ("C", "REINFORCED CONCRETE FRAME ABOVE PODIUM", None, None, None),
    ("C10", "Columns 400x400 (GF) and 300x300 (L1-L4)", "m3", 122, 38_500),
    ("C20", "Suspended floor slabs 200 mm, L1-L4", "m3", 348, 36_800),
    ("C30", "Beams, lintels and downstands", "m3", 96, 39_200),
    ("C40", "RC lift shaft and stair enclosure, full height", "m3", 88, 41_500),
    ("C50", "Stair flights: 17 risers x 176, 6 flights", "nr", 6, 385_000),
    ("C60", "High-yield reinforcement, cut, bent, fixed", "kg", 148_000, 205),
    ("C70", "Formwork to soffits, sides and edges", "m2", 4_650, 1_650),
    ("C80", "Concrete pump and placement, all levels", "m3", 1_040, 3_200),

    ("D", "EXTERNAL WALLS, CLADDING AND SUN SHADING", None, None, None),
    ("D10", "Machine-cut quarry stone walling 200 mm, rendered", "m2", 1_980, 3_450),
    ("D20", "ISSB blockwork 300x150x100 fair-faced (terracotta)", "m2", 1_640, 4_150),
    ("D30", "Cement-sand render, external, two coats", "m2", 3_620, 1_080),
    ("D40", "Boundary walls and parapets with concrete coping", "m2", 720, 3_950),
    ("D50", "Vertical timber-look brise-soleil fins to west facade", "m2", 268, 11_500),
    ("D60", "Horizontal sun hoods 600 mm to south courtyard face", "m2", 148, 9_800),
    ("D70", "Perforated concrete breeze-block screen to core", "m2", 62, 8_400),
    ("D80", "Ramp screen wall with climbers and coping", "m2", 96, 5_200),

    ("E", "INTERNAL WALLS AND PARTITIONS", None, None, None),
    ("E10", "ISSB internal partitions 100-150 mm, plastered", "m2", 2_340, 2_950),
    ("E20", "Internal plaster, two coats, to all walls", "m2", 4_680, 980),
    ("E30", "Suspended ceilings and bulkheads to bathrooms", "m2", 268, 3_250),
    ("E40", "Skim coat and paint to internal walls and ceilings", "m2", 5_120, 720),

    ("F", "ROOF", None, None, None),
    ("F10", "Roof slab falls, screed to outlets", "m2", 470, 2_450),
    ("F20", "Torch-on membrane waterproofing, 4 mm, with protection", "m2", 470, 3_650),
    ("F30", "Rainwater goods: outlets, downpipes, gutters", "m", 186, 2_850),
    ("F40", "Roof parapet and coping", "m", 96, 4_200),
    ("F50", "Roof garden build-up: drainage cell, soil, filter", "m2", 120, 8_900),
    ("F60", "Timber pergola to roof terrace", "m2", 34, 26_500),
    ("F70", "Roof planters, seats and paving on pedestals", "m2", 96, 7_400),

    ("G", "DOORS, WINDOWS AND GLAZING", None, None, None),
    ("G10", "Aluminium sliding windows, double glazed, low-E", "m2", 386, 21_500),
    ("G20", "Aluminium casement windows with top openers", "m2", 148, 19_800),
    ("G30", "Timber flush internal doors, ironmongery, frames", "nr", 68, 32_500),
    ("G40", "Solid timber external doors with security ironmongery", "nr", 18, 58_000),
    ("G50", "Motorised sectional vehicle door 2.9 x 3.1 m", "nr", 1, 780_000),
    ("G60", "Steel pedestrian gate with intercom and video", "nr", 1, 265_000),
    ("G70", "Shop roller shutter 2.85 x 3.20 m", "nr", 1, 185_000),

    ("H", "BALUSTRADES, RAILINGS AND METALWORK", None, None, None),
    ("H10", "Charcoal steel balustrade, vertical bars, 1.10 m", "m", 286, 12_800),
    ("H20", "Continuous planter boxes to galleries and balconies", "m", 214, 6_400),
    ("H30", "Accessible ramp handrails, both sides", "m", 34, 9_200),
    ("H40", "Concealed gutter and fascia to galleries", "m", 186, 5_100),
    ("H50", "General metalwork: ladders, guards, brackets", "sum", 1, 420_000),

    ("J", "FLOOR, WALL AND CEILING FINISHES", None, None, None),
    ("J10", "Porcelain floor tiling to apartments, skirting", "m2", 1_180, 4_250),
    ("J20", "Ceramic wall tiling to bathrooms and kitchens", "m2", 620, 3_850),
    ("J30", "Epoxy floor coating to basement parking", "m2", 620, 2_450),
    ("J40", "Permeable pavers to courtyard paths", "m2", 268, 3_100),
    ("J50", "Courtyard lawn on 300 mm build-up with ISSB edging", "m2", 58, 4_600),
    ("J60", "Communal area finishes and wayfinding signage", "sum", 1, 680_000),

    ("K", "MECHANICAL, ELECTRICAL AND PLUMBING", None, None, None),
    ("K10", "Electrical installation: sub-mains, DBs, wiring, fittings", "m2", 1_363, 4_250),
    ("K20", "Standby generator 60 kVA and changeover", "nr", 1, 1_950_000),
    ("K30", "Plumbing and drainage installation to all units", "m2", 1_363, 3_450),
    ("K40", "Cold water storage, pumping, roof rainwater harvesting", "sum", 1, 1_680_000),
    ("K50", "Sanitaryware and fittings: 13 kitchens, 20 bathrooms", "sum", 1, 2_940_000),
    ("K60", "Basement ventilation: 2 no. extract fans, 6 ACH", "sum", 1, 1_240_000),
    ("K70", "Fire detection, alarm and extinguishers", "sum", 1, 980_000),
    ("K80", "CCTV, access control and intercom systems", "sum", 1, 860_000),
    ("K90", "Solar PV array 8 kWp with inverters", "kWp", 8, 148_000),
    ("K100", "Solar water heating, 6 no. collectors", "sum", 1, 1_150_000),

    ("L", "LIFT AND SPECIALIST INSTALLATIONS", None, None, None),
    ("L10", "Machine-room-less lift, 630 kg, 6 stops, installed", "nr", 1, 6_850_000),
    ("L20", "Lift shaft equipment, doors, guides, commissioning", "sum", 1, 1_240_000),

    ("M", "EXTERNAL WORKS AND LANDSCAPE", None, None, None),
    ("M10", "Site clearance, topsoil strip and stockpile", "m2", 620, 320),
    ("M20", "Paving to forecourt, footway and kerbs", "m2", 540, 4_100),
    ("M30", "Asphalt surfacing to street frontage and crossing", "m2", 380, 3_650),
    ("M40", "Storm drainage, gully traps, soakaway", "m", 180, 5_200),
    ("M50", "Water and sewer connections, meter chamber", "sum", 1, 940_000),
    ("M60", "Soft landscape: trees, shrubs, climbers, irrigation", "sum", 1, 1_380_000),
    ("M70", "Feature tree supply and planting (multi-stem)", "nr", 1, 185_000),
    ("M80", "External lighting and bollards", "sum", 1, 520_000),
    ("M90", "Refuse store, meter cabinets and cycle stands", "sum", 1, 385_000),
    ("M100", "Post and handover: cleaning, snagging, O&M manuals", "sum", 1, 620_000),
]

CONTINGENCY_PCT = 7.5
PROF_FEES_PCT = 9.0
VAT_PCT = 16.0

RATE_BUILDUP = [
    ("Concrete grade 30 in suspended slab (per m3)", [
        ("Cement 400 kg", "kg", 400, 14.5),
        ("Sand", "m3", 0.45, 2_400),
        ("Ballast 20 mm", "m3", 0.85, 2_800),
        ("Admixture / retarder", "l", 3.2, 320),
        ("Labour: placing, compacting, curing", "m3", 1, 4_200),
        ("Plant: pump, vibrator", "m3", 1, 1_850),
        ("Wastage and supervision", "m3", 1, 1_450),
    ]),
    ("ISSB blockwork fair-faced 300 mm (per m2)", [
        ("ISSB blocks 300x150x100", "nr", 33, 82),
        ("Cement-sand mortar 1:5", "m3", 0.028, 9_800),
        ("Labour: laying, levelling, pointing", "m2", 1, 1_180),
        ("Scaffold and hoisting", "m2", 1, 240),
        ("Concrete plinth 150 mm", "m", 1, 420),
    ]),
    ("Aluminium sliding window, double glazed (per m2)", [
        ("Aluminium sections, powder coated", "kg", 9.5, 780),
        ("6 mm low-E + 6 mm clear, argon filled", "m2", 1, 7_400),
        ("Rubber gaskets, seals and wool pile", "m", 14, 165),
        ("Fittings, rollers, handles, locks", "set", 0.35, 3_200),
        ("Fabrication and installation labour", "m2", 1, 2_650),
    ]),
]

CASHFLOW = [
    ("Month 1-2", "Mobilisation, site setup, approvals", 6.0),
    ("Month 3-5", "Excavation, basement raft and retaining walls", 16.0),
    ("Month 6-8", "Podium slab, GF structure, ramp", 14.0),
    ("Month 9-14", "Upper floor frame L1-L4 and core", 22.0),
    ("Month 15-17", "Roof, waterproofing, roof garden structure", 10.0),
    ("Month 18-21", "Walling, services first fix, glazing", 15.0),
    ("Month 22-24", "Finishes, fit-out, lift, external works", 12.0),
    ("Month 25-26", "Commissioning, snagging, handover", 5.0),
]


def build():
    wb = Workbook()

    # ---------------- 1. summary ----------------
    ws = wb.active
    ws.title = "1 Summary"
    r = style_title(ws, 1, "COURTYARD APARTMENTS  —  BILL OF QUANTITIES  (SUMMARY)", 5)
    r = style_title(ws, r, "50 x 100 ft plot, Nairobi, Kenya  |  GF + L1-L4, 13 homes, "
                           "9 basement bays  |  Indicative, 2026 Nairobi market", 5, size=9)

    # element subtotals
    elems = {}
    for code, desc, unit, qty, rate in ITEMS:
        if unit is None:
            elems[code] = [desc, 0.0]
            continue
        key = code[0]
        if key in elems:
            elems[key][1] += qty * rate

    ws.append([])
    r = ws.max_row + 1
    r = style_header(ws, r, ["Ref", "Element", "Amount (KES)", "% of works"], [10, 62, 20, 14])
    total_works = sum(v[1] for v in elems.values())
    first_data = r
    for k in sorted(elems):
        ws.cell(row=r, column=1, value=k).border = BORDER
        c = ws.cell(row=r, column=2, value=elems[k][0]); c.border = BORDER
        c = ws.cell(row=r, column=3, value=round(elems[k][1])); c.number_format = MONEY
        c.border = BORDER
        c = ws.cell(row=r, column=4, value=elems[k][1] / total_works); c.number_format = '0.0%'
        c.border = BORDER
        r += 1
    ws.cell(row=r, column=2, value="TOTAL OF MEASURED WORKS").font = Font(bold=True)
    c = ws.cell(row=r, column=3, value=round(total_works)); c.number_format = MONEY
    c.font = Font(bold=True)
    r += 2

    rows = [
        ("Subtotal, measured works", total_works, False),
        (f"Contingency / risk allowance @ {CONTINGENCY_PCT}%", total_works * CONTINGENCY_PCT / 100, False),
        (f"Professional fees @ {PROF_FEES_PCT}% (architect, engineer, QS, PM)",
         total_works * PROF_FEES_PCT / 100, False),
    ]
    sub = total_works + total_works * (CONTINGENCY_PCT + PROF_FEES_PCT) / 100
    rows.append(("Subtotal before tax", sub, True))
    rows.append((f"VAT @ {VAT_PCT}%", sub * VAT_PCT / 100, False))
    rows.append(("CONTRACT SUM (incl. VAT)", sub * (1 + VAT_PCT / 100), True))
    for label, val, bold in rows:
        c = ws.cell(row=r, column=2, value=label)
        c.font = Font(bold=bold, size=11 if bold else 10)
        c = ws.cell(row=r, column=3, value=round(val))
        c.number_format = MONEY
        c.font = Font(bold=bold, size=11 if bold else 10)
        if bold:
            c.fill = PatternFill("solid", fgColor=GREY)
            ws.cell(row=r, column=2).fill = PatternFill("solid", fgColor=GREY)
        r += 1
    r += 1
    final = sub * (1 + VAT_PCT / 100)
    gfa = 1_363 + 620
    for label, val in (("Gross floor area (excl. basement)", "1,363 m2"),
                       ("Gross floor area (incl. basement)", "1,983 m2"),
                       ("Rate per m2 of GFA (excl. basement)",
                        f"KES {final/1_363:,.0f}"),
                       ("Rate per m2 of GFA (incl. basement)",
                        f"KES {final/1_983:,.0f}"),
                       ("Cost per home (13 homes)", f"KES {final/13:,.0f}")):
        ws.cell(row=r, column=2, value=label).font = Font(size=10, italic=True)
        ws.cell(row=r, column=3, value=val).font = Font(size=10, italic=True)
        r += 1
    ws.cell(row=r + 1, column=2,
            value="Rates are indicative Nairobi market rates for 2026 and exclude land, "
                  "finance charges and county charges. Confirm by competitive tender.").font = \
        Font(size=9, italic=True, color="8A6D3B")

    # ---------------- 2. detailed BOQ ----------------
    ws2 = wb.create_sheet("2 Bill of Quantities")
    r = style_title(ws2, 1, "MEASURED BILL OF QUANTITIES", 6)
    r = style_header(ws2, r, ["Ref", "Description", "Unit", "Quantity", "Rate (KES)",
                              "Amount (KES)"], [10, 74, 8, 12, 16, 18])
    for code, desc, unit, qty, rate in ITEMS:
        if unit is None:
            c = ws2.cell(row=r, column=1, value=code)
            c.font = Font(bold=True, size=10, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor=NAVY)
            d = ws2.cell(row=r, column=2, value=desc)
            d.font = Font(bold=True, size=10, color="FFFFFF")
            d.fill = PatternFill("solid", fgColor=NAVY)
            for k in range(3, 7):
                ws2.cell(row=r, column=k).fill = PatternFill("solid", fgColor=NAVY)
            r += 1
            continue
        ws2.cell(row=r, column=1, value=code).border = BORDER
        c = ws2.cell(row=r, column=2, value=desc); c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center")
        ws2.cell(row=r, column=3, value=unit).border = BORDER
        c = ws2.cell(row=r, column=4, value=qty); c.number_format = '#,##0.##'; c.border = BORDER
        c = ws2.cell(row=r, column=5, value=rate); c.number_format = MONEY2; c.border = BORDER
        c = ws2.cell(row=r, column=6, value=round(qty * rate))
        c.number_format = MONEY; c.border = BORDER
        r += 1
    ws2.cell(row=r, column=2, value="TOTAL CARRIED TO SUMMARY").font = Font(bold=True)
    c = ws2.cell(row=r, column=6, value=round(total_works)); c.number_format = MONEY
    c.font = Font(bold=True)
    ws2.freeze_panes = "A4"

    # ---------------- 3. rate build-ups ----------------
    ws3 = wb.create_sheet("3 Rate Build-ups")
    r = style_title(ws3, 1, "RATE BUILD-UPS  —  KEY ITEMS", 5)
    for title, parts in RATE_BUILDUP:
        r += 1
        c = ws3.cell(row=r, column=1, value=title)
        c.font = Font(bold=True, size=10, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=ACCENT)
        ws3.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        r += 1
        r = style_header(ws3, r, ["Component", "Unit", "Qty", "Rate (KES)", "Amount (KES)"],
                         [52, 8, 10, 14, 16])
        tot = 0.0
        for comp, unit, qty, rate in parts:
            ws3.cell(row=r, column=1, value=comp).border = BORDER
            ws3.cell(row=r, column=2, value=unit).border = BORDER
            c = ws3.cell(row=r, column=3, value=qty); c.number_format = '#,##0.###'; c.border = BORDER
            c = ws3.cell(row=r, column=4, value=rate); c.number_format = MONEY2; c.border = BORDER
            c = ws3.cell(row=r, column=5, value=round(qty * rate, 2))
            c.number_format = MONEY2; c.border = BORDER
            tot += qty * rate
            r += 1
        ws3.cell(row=r, column=1, value="Rate per unit (rounded)").font = Font(bold=True)
        c = ws3.cell(row=r, column=5, value=round(tot)); c.font = Font(bold=True)
        c.number_format = MONEY
        r += 1

    # ---------------- 4. cash flow ----------------
    ws4 = wb.create_sheet("4 Cash Flow")
    r = style_title(ws4, 1, "INDICATIVE CASH FLOW  —  26 MONTH PROGRAMME", 5)
    r = style_header(ws4, r, ["Period", "Activity", "% of contract", "Amount (KES)",
                              "Cumulative (KES)"], [14, 56, 14, 18, 18])
    cum = 0.0
    for period, act, pct in CASHFLOW:
        amt = final * pct / 100
        cum += amt
        ws4.cell(row=r, column=1, value=period).border = BORDER
        ws4.cell(row=r, column=2, value=act).border = BORDER
        c = ws4.cell(row=r, column=3, value=pct / 100); c.number_format = '0.0%'; c.border = BORDER
        c = ws4.cell(row=r, column=4, value=round(amt)); c.number_format = MONEY; c.border = BORDER
        c = ws4.cell(row=r, column=5, value=round(cum)); c.number_format = MONEY; c.border = BORDER
        r += 1
    ws4.cell(row=r, column=2, value="TOTAL").font = Font(bold=True)
    c = ws4.cell(row=r, column=4, value=round(final)); c.number_format = MONEY
    c.font = Font(bold=True)
    r += 3
    ws4.cell(row=r, column=2,
             value="Excludes land cost, development finance interest, county charges and "
                   "marketing. Assumes a 26-month construction period.").font = \
        Font(size=9, italic=True, color="8A6D3B")

    # ---------------- 5. assumptions ----------------
    ws5 = wb.create_sheet("5 Basis & Assumptions")
    r = style_title(ws5, 1, "BASIS OF THE ESTIMATE", 4)
    notes = [
        ("Currency", "Kenya Shillings (KES). No escalation applied."),
        ("Price base", "Nairobi market rates, Q4 2026, indicative."),
        ("Measurement", "Elemental BOQ; quantities taken from the architectural model."),
        ("GFA (excl. basement)", "1,363 m2 estimated from the level schedule."),
        ("GFA (incl. basement)", "1,983 m2."),
        ("Units", "13 homes: 1 GF 2-bed, 4 x 1-bed front, 4 x 2-bed north wing, 4 x 2-bed rear."),
        ("Parking", "9 bays including 1 accessible (3.6 m) and 1 EV with charger."),
        ("Preliminaries", "Measured separately in element A; 12-month site duration assumed."),
        ("Contingency", f"{CONTINGENCY_PCT}% on measured works."),
        ("Professional fees", f"{PROF_FEES_PCT}% (architect, structural, MEP, QS, project manager)."),
        ("VAT", f"{VAT_PCT}% as applicable to construction services in Kenya."),
        ("Exclusions", "Land, finance interest, county development charges, "
                       "loose furniture, marketing, legal, and any works by others."),
        ("Structural caveat", "Podium drop panels, balcony cantilever tendons and the "
                              "courtyard tree planter drop panel are provisional pending "
                              "the structural engineer's design."),
        ("Glazing caveat", "s.143 window-area compliance is NOT VERIFIED: the saved model "
                           "has no openings cut in the host walls. Confirm before order."),
        ("Escalation", "Not included. Add 5-8% per annum for programmes beyond Q4 2026."),
    ]
    r = style_header(ws5, r, ["Item", "Basis"], [34, 96])
    for a, b in notes:
        ws5.cell(row=r, column=1, value=a).font = Font(bold=True, size=10)
        ws5.cell(row=r, column=1).border = BORDER
        c = ws5.cell(row=r, column=2, value=b)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = BORDER
        ws5.row_dimensions[r].height = 26
        r += 1

    wb.save(XLSX)
    print(f"wrote {XLSX}")
    print(f"  measured works : KES {total_works:,.0f}")
    print(f"  contract sum   : KES {final:,.0f}  (incl. VAT, fees, contingency)")
    print(f"  rate per m2    : KES {final/1_363:,.0f} (excl. basement)")
    print(f"  per home       : KES {final/13:,.0f}")


if __name__ == "__main__":
    build()
