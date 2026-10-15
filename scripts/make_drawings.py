"""
make_drawings.py -- produce the architectural drawing set from geometry.json.

Draws A1 sheets (841 x 594 mm at 150 dpi) with Pillow: plans from true section
cuts through the model, sections, projected elevations, schedules and a title
sheet. Outputs individual PNGs plus one multi-page PDF.

  python make_drawings.py [--only S03]
"""
import argparse
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
GEO = os.path.join(PROJ, "docs", "drawings", "geometry.json")
OUT = os.path.join(PROJ, "docs", "drawings")

DPI = 150
MM = DPI / 25.4
SW, SH = int(841 * MM), int(594 * MM)          # A1 landscape
M = 15 * MM                                     # sheet margin

FONT_R = "C:/Windows/Fonts/arial.ttf"
FONT_B = "C:/Windows/Fonts/arialbd.ttf"
FONT_M = "C:/Windows/Fonts/consola.ttf"
_C = {}


def font(path, mm):
    key = (path, round(mm, 2))
    if key not in _C:
        _C[key] = ImageFont.truetype(path, int(mm * MM))
    return _C[key]


def t(pt, sz, text, path=FONT_R, anchor="la", fill=(0, 0, 0)):
    d, xy = pt
    d.text(xy, text, font=font(path, sz), fill=fill, anchor=anchor)


def line(d, a, b, w, fill=(0, 0, 0)):
    d.line([a, b], fill=fill, width=max(1, int(round(w))))


def rect(d, x0, y0, x1, y1, w, fill=None, outline=(0, 0, 0)):
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=outline,
                width=max(1, int(round(w))))


# line weights in mm
LW_CUT, LW_MED, LW_THIN, LW_FINE = 0.70, 0.35, 0.18, 0.10

POCHE = (62, 62, 68)
POCHE_LIGHT = (112, 114, 120)
GRID = (150, 60, 60)


class View:
    """Maps model metres to sheet pixels."""

    def __init__(self, ox, oy, m_per_mm, flip_y=True):
        # m_per_mm is the 1:x denominator: 1 model metre = 1000/x mm on paper
        self.s = MM * 1000.0 / m_per_mm        # px per model metre
        self.ox, self.oy = ox, oy
        self.flip = flip_y

    def p(self, x, y):
        return (self.ox + x * self.s,
                self.oy - (y * self.s if self.flip else -y * self.s))

    def box(self, b, ax=0, ay=1):
        # b = [x0,y0,z0,x1,y1,z1]
        lo = self.p(b[ax], b[ay])
        hi = self.p(b[ax + 3], b[ay + 3])
        return [min(lo[0], hi[0]), min(lo[1], hi[1]),
                max(lo[0], hi[0]), max(lo[1], hi[1])]


# ---------------------------------------------------------------- sheet frame
TITLE_ROWS = [
    ("PROJECT", "COURTYARD APARTMENTS — 50 x 100 ft PLOT, NAIROBI"),
    ("SHEET", ""),
    ("SCALE", ""),
    ("DATE", "OCTOBER 2026"),
    ("STATUS", "FOR DEVELOPMENT CONTROL SUBMISSION"),
    ("DRAWN / CHECKED", "AV / —"),
]


def sheet(title, number, scale, rev="P01"):
    img = Image.new("RGB", (SW, SH), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # border
    rect(d, M, M, SW - M, SH - M, 0.5 * MM)
    rect(d, M + 2 * MM, M + 2 * MM, SW - M - 2 * MM, SH - M - 2 * MM, 0.18 * MM)

    # ---- title block, bottom right ----
    tw, th = 190 * MM, 62 * MM
    x0, y0 = SW - M - 4 * MM - tw, SH - M - 4 * MM - th
    rect(d, x0, y0, x0 + tw, y0 + th, 0.5 * MM)
    rh = th / 6.0
    for i, (k, v) in enumerate(TITLE_ROWS):
        yy = y0 + i * rh
        if i:
            line(d, (x0, yy), (x0 + tw, yy), LW_FINE)
        line(d, (x0 + 38 * MM, yy), (x0 + 38 * MM, y0 + th), LW_FINE)
        t((d, (x0 + 2 * MM, yy + rh * 0.5)), 2.6, k, FONT_B, anchor="lm")
        val = v
        if k == "SHEET":
            val = title
        elif k == "SCALE":
            val = scale
        t((d, (x0 + 40 * MM, yy + rh * 0.5)), 3.0 if k in ("SHEET", "PROJECT") else 2.6,
          val, FONT_B if k in ("SHEET", "PROJECT") else FONT_R, anchor="lm")
    t((d, (x0 + tw - 2 * MM, y0 - 7 * MM)), 7.0, number, FONT_B, anchor="ra")
    t((d, (x0 + tw - 2 * MM, y0 - 14 * MM)), 2.4, f"REV {rev}", FONT_R, anchor="ra")

    # ---- north point ----
    nx, ny = x0 - 26 * MM, y0 + th - 20 * MM
    d.ellipse([nx - 11 * MM, ny - 11 * MM, nx + 11 * MM, ny + 11 * MM],
              outline=(0, 0, 0), width=int(0.35 * MM))
    d.polygon([(nx, ny - 9 * MM), (nx - 3.6 * MM, ny + 4 * MM),
               (nx, ny + 1.2 * MM), (nx + 3.6 * MM, ny + 4 * MM)], fill=(0, 0, 0))
    t((d, (nx, ny + 13 * MM)), 3.0, "N", FONT_B, anchor="ma")
    return img, d


def scale_bar(d, pt, m_per_mm, total_m=10):
    x, y = pt
    seg = total_m / 5
    for i in range(5):
        w = seg * MM * 1000.0 / m_per_mm
        x0 = x + i * w
        fill = (0, 0, 0) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([x0, y, x0 + w, y + 3 * MM], fill=fill, outline=(0, 0, 0),
                    width=int(0.25 * MM))
        t((d, (x0, y + 4.2 * MM)), 2.2, f"{int(i*seg)}", FONT_R, anchor="ma")
    t((d, (x + 5 * seg * MM * 1000.0 / m_per_mm, y + 4.2 * MM)), 2.2, f"{int(total_m)} m",
      FONT_R, anchor="ma")
    t((d, (x, y - 4 * MM)), 2.6, f"SCALE 1:{int(round(m_per_mm))}", FONT_B)


def grid(d, view, xlines, ylines, xbub="ABCDEFG", ybub="12345678"):
    for i, gx in enumerate(xlines):
        p0 = view.p(gx, -2.5)
        p1 = view.p(gx, 33.0)
        dash(d, p0, p1, LW_FINE, GRID, 3 * MM, 2 * MM)
        bx = view.p(gx, -5.0)
        d.ellipse([bx[0] - 5 * MM, bx[1] - 5 * MM, bx[0] + 5 * MM, bx[1] + 5 * MM],
                  outline=GRID, width=int(0.25 * MM))
        t((d, bx), 3.2, xbub[i], FONT_B, anchor="mm", fill=GRID)
    for i, gy in enumerate(ylines):
        p0 = view.p(-3.0, gy)
        p1 = view.p(18.5, gy)
        dash(d, p0, p1, LW_FINE, GRID, 3 * MM, 2 * MM)
        by = view.p(-5.2, gy)
        d.ellipse([by[0] - 5 * MM, by[1] - 5 * MM, by[0] + 5 * MM, by[1] + 5 * MM],
                  outline=GRID, width=int(0.25 * MM))
        t((d, by), 3.2, ybub[i], FONT_B, anchor="mm", fill=GRID)


def dash(d, a, b, w, fill, on, off):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L < 1:
        return
    ux, uy = dx / L, dy / L
    pos = 0.0
    while pos < L:
        e = min(pos + on, L)
        d.line([(a[0] + ux * pos, a[1] + uy * pos),
                (a[0] + ux * e, a[1] + uy * e)], fill=fill,
               width=max(1, int(round(w))))
        pos = e + off


def dim_h(d, view, y_model, x0, x1, label=None, off=0):
    a = view.p(x0, y_model)
    b = view.p(x1, y_model)
    yy = a[1] + off
    line(d, (a[0], yy), (b[0], yy), LW_THIN)
    for px in (a[0], b[0]):
        d.line([(px, yy - 2.2 * MM), (px, yy + 2.2 * MM)], fill=(0, 0, 0),
               width=int(round(LW_THIN)))
    lab = label if label else f"{(x1-x0):.2f}"
    t((d, ((a[0] + b[0]) / 2, yy - 3.4 * MM)), 2.3, lab, FONT_R, anchor="ms")


# ---------------------------------------------------------------- plan drawing
def draw_plan(d, view, plan, boxes, openings, labels, furniture_ok=True):
    segs = plan['segs']
    bmap = {b['n']: b for b in boxes}

    # 1. poché: fill cut structural objects
    for name in segs:
        b = bmap.get(name)
        if not b:
            continue
        cat = b['c']
        r = view.box(b['b'], 0, 1)
        if r[2] - r[0] < 2 or r[3] - r[1] < 2:
            continue
        if cat in ('wall', 'structure', 'slab', 'floor'):
            d.rectangle(r, fill=POCHE_LIGHT)
        elif cat in ('column', 'stair'):
            d.rectangle(r, fill=POCHE)

    # 2. cut linework
    for name, ss in segs.items():
        cat = bmap.get(name, {}).get('c', 'other')
        w = LW_CUT if cat in ('wall', 'structure', 'column', 'stair') else LW_THIN
        for x1, y1, x2, y2 in ss:
            line(d, view.p(x1, y1), view.p(x2, y2), w)

    # 3. openings at this level -> window / door symbols
    z = plan['z']
    for op in openings:
        b = op['b']
        if not (b[2] <= z <= b[5]):
            continue
        r = view.box(b, 0, 1)
        d.rectangle(r, outline=(0, 0, 0), width=int(round(LW_MED)))
        if op['c'] == 'glazing':
            line(d, (r[0], (r[1] + r[3]) / 2), (r[2], (r[1] + r[3]) / 2), LW_THIN)

    # 4. room labels
    for lx, ly, code, nm, area in labels:
        p = view.p(lx, ly)
        t((d, p), 2.9, code, FONT_B, anchor="mm")
        t((d, (p[0], p[1] + 4.0 * MM)), 2.4, nm, FONT_R, anchor="mm")
        if area:
            t((d, (p[0], p[1] + 7.4 * MM)), 2.2, area, FONT_R, anchor="mm",
              fill=(90, 90, 90))


def view_plan(d, plan, boxes, openings, labels, ox, oy, m_per_mm=100):
    v = View(ox, oy, m_per_mm)
    draw_plan(d, v, plan, boxes, openings, labels)
    grid(d, v, [0, 3.48, 6.30, 8.48, 10.49, 13.44, 15.24],
         [0, 5.2, 7.3, 11.0, 15.0, 19.1, 23.0, 30.48],
         "ABCDEFG", "12345678")
    # overall dimensions
    base = v.p(0, 0)
    yb = SH - M - 78 * MM
    v2 = View(ox, yb + 30.48 * v.s, m_per_mm)
    dim_h(d, v2, 0, 0, 3.48, off=0)
    dim_h(d, v2, 0, 3.48, 6.30, off=0)
    dim_h(d, v2, 0, 6.30, 8.48, off=0)
    dim_h(d, v2, 0, 8.48, 10.49, off=0)
    dim_h(d, v2, 0, 10.49, 13.44, off=0)
    dim_h(d, v2, 0, 13.44, 15.24, off=0)
    dim_h(d, v2, 0, 0, 15.24, label="15.24 m  (50 ft)", off=11 * MM)
    # left-hand vertical dimensions
    xl = ox - 14 * MM
    v3 = View(xl, oy, m_per_mm)
    for a, b in ((0, 5.2), (5.2, 7.3), (7.3, 11.0), (11.0, 15.0),
                 (15.0, 19.1), (19.1, 23.0), (23.0, 30.48)):
        p0, p1 = v3.p(0, a), v3.p(0, b)
        line(d, (xl, p0[1]), (xl, p1[1]), LW_THIN)
        d.line([(xl - 2.2 * MM, p0[1]), (xl + 2.2 * MM, p0[1])], fill=(0, 0, 0), width=int(LW_THIN))
        d.line([(xl - 2.2 * MM, p1[1]), (xl + 2.2 * MM, p1[1])], fill=(0, 0, 0), width=int(LW_THIN))
        t((d, (xl - 3.2 * MM, (p0[1] + p1[1]) / 2)), 2.2, f"{b-a:.2f}", FONT_R,
          anchor="rm", )
    p0, p1 = v3.p(0, 0), v3.p(0, 30.48)
    line(d, (xl - 9 * MM, p0[1]), (xl - 9 * MM, p1[1]), LW_THIN)
    t((d, (xl - 11 * MM, (p0[1] + p1[1]) / 2)), 2.4, "30.48 m  (100 ft)", FONT_R,
      anchor="rm")
    return v


# ---------------------------------------------------------------- sections
def draw_section(d, view, sec, boxes, ox, oy):
    bmap = {b['n']: b for b in boxes}
    axis = sec['axis']
    val = sec['value']
    ai, bi = (1, 2) if axis == 'X' else (0, 2)

    # light projection of everything behind the cut, far to near
    def depth(b):
        return -(b['b'][1] if axis == 'X' else b['b'][0])
    behind = [b for b in boxes
              if (b['b'][1] > val if axis == 'X' else b['b'][0] > val)
              and b['c'] in ('wall', 'structure', 'slab', 'column', 'floor')]
    for b in sorted(behind, key=depth):
        r = view.box(b['b'], ai, bi)
        if (r[2] - r[0]) < 2 and (r[3] - r[1]) < 2:
            continue
        d.rectangle(r, outline=(178, 178, 182), width=1)

    # cut poché
    for name in sec['segs']:
        b = bmap.get(name)
        if not b or b['c'] not in ('wall', 'structure', 'slab', 'column', 'floor', 'floor'):
            continue
        r = view.box(b['b'], ai, bi)
        if (r[2] - r[0]) < 2 or (r[3] - r[1]) < 2:
            continue
        d.rectangle(r, fill=POCHE if b['c'] != 'floor' else POCHE_LIGHT)

    for name, ss in sec['segs'].items():
        cat = bmap.get(name, {}).get('c', 'other')
        w = LW_CUT if cat in ('wall', 'structure', 'slab', 'column', 'floor') else LW_THIN
        for x1, y1, x2, y2 in ss:
            line(d, view.p(x1, y1), view.p(x2, y2), w)

    # level datum lines
    levels = [(-2.00, "B1 FFL -2.00"), (0.90, "GF FFL +0.90"), (4.20, "L1 +4.20"),
              (7.20, "L2 +7.20"), (10.20, "L3 +10.20"), (13.20, "L4 +13.20"),
              (16.20, "ROOF +16.20"), (17.30, "PARAPET +17.30")]
    for lv, nm in levels:
        p = view.p(-3.2, lv)
        d.line([(p[0] - 3 * MM, p[1]), (view.p(18.6, lv)[0] + 3 * MM, p[1])],
               fill=(120, 150, 200), width=max(1, int(LW_FINE)))
        t((d, (p[0] - 4 * MM, p[1])), 2.1, nm, FONT_R, anchor="rm",
          fill=(70, 100, 150))


# ---------------------------------------------------------------- elevations
def draw_elevation(d, view, boxes, view_axis, flip):
    """Painter's algorithm over axis-aligned boxes -> a readable elevation."""
    def key(b):
        if view_axis == 'Y':
            return b['b'][4] if not flip else -b['b'][1]
        return b['b'][3] if not flip else -b['b'][0]

    order = sorted(boxes, key=key, reverse=True)
    ai, bi = (0, 2) if view_axis == 'Y' else (1, 2)
    drawn = skipped_cat = skipped_size = 0
    for b in order:
        cat = b['c']
        if cat not in ('wall', 'structure', 'slab', 'column', 'railing', 'glazing',
                       'door', 'stair', 'floor', 'tree'):
            skipped_cat += 1
            continue
        r = view.box(b['b'], ai, bi)
        if (r[2] - r[0]) < 1.5 and (r[3] - r[1]) < 1.5:
            skipped_size += 1
            continue
        drawn += 1
        if cat in ('glazing',):
            d.rectangle(r, outline=(0, 0, 0), width=int(LW_MED))
            line(d, (r[0], (r[1] + r[3]) / 2), (r[2], (r[1] + r[3]) / 2), LW_FINE)
        elif cat in ('door',):
            d.rectangle(r, fill=(196, 196, 200), outline=(0, 0, 0),
                        width=int(LW_MED))
        elif cat == 'tree':
            d.rectangle(r, outline=(150, 150, 150), width=int(LW_THIN))
        else:
            # Tonal mass, not white-on-white: white fills cancelled each other
            # out and the elevation read as an empty sheet.
            tone = {'wall': 222, 'structure': 208, 'slab': 238,
                    'floor': 245, 'column': 168, 'railing': 198,
                    'stair': 200}.get(cat, 240)
            d.rectangle(r, fill=(tone, tone, tone), outline=(38, 38, 44),
                        width=int(LW_MED if cat in ('wall', 'structure', 'column')
                                  else LW_THIN))
    print(f"    elev {view_axis} flip={flip}: drawn={drawn} "
          f"skip_cat={skipped_cat} skip_size={skipped_size}")


# ---------------------------------------------------------------- content
ROOMS = {
    'GF': [
        (8.9, 2.6, "SHOP", "retail ~17 m2", ""),
        (4.6, 1.5, "GUARD", "guard house + WC", ""),
        (4.6, 4.1, "STORE", "store / meters", ""),
        (6.5, 2.6, "PED", "pedestrian gate", ""),
        (12.7, 2.7, "CORE", "lift + stair", ""),
        (1.9, 11.0, "RAMP", "vehicle ramp down", ""),
        (5.1, 14.0, "COLONNADE", "shaded arcade", ""),
        (9.85, 14.0, "COURTYARD", "open to sky", "112.1 m2"),
        (2.0, 26.0, "LAUNDRY", "laundry / store", ""),
        (9.5, 26.5, "2-BED", "ground floor flat", "87.1 m2"),
    ],
    'B1': [
        (5.2, 6.6, "BAY 01", "accessible 3.6 m", ""),
        (5.2, 10.6, "BAYS 02-05", "4 bays 2.57 m", ""),
        (9.0, 27.5, "BAYS 06-09", "rear bays incl. EV", ""),
        (11.7, 13.5, "AISLE", "6.46 m", ""),
        (9.2, 22.0, "CROSS AISLE", "turning 6.1 m", ""),
        (1.9, 11.5, "RAMP", "1:8 down", ""),
        (2.1, 8.0, "WATER TANK", "sunken", ""),
        (10.2, 6.6, "LIFT LOBBY", "3.52 x 2.80", ""),
        (12.7, 2.7, "CORE", "stair + lift", ""),
        (2.4, 26.5, "RUN-OUT", "m/bikes, sump", ""),
    ],
}
TYPICAL = [
    (5.2, 2.9, "1-BED", "55 m2 net, street aspect", "~63 m2 gross"),
    (1.6, 6.5, "STORE", "store + shafts", ""),
    (9.0, 6.55, "GALLERY", "1.5 m front gallery", ""),
    (3.15, 15.0, "2-BED", "north wing, 99 m2 gross", "~88 m2 net"),
    (9.85, 14.0, "COURTYARD", "void, open to sky", "112.1 m2"),
    (14.3, 15.0, "GALLERY", "1.8 m + planters", ""),
    (7.6, 26.7, "2-BED", "rear block, 100 m2 net", "~107 m2 gross"),
    (12.7, 2.75, "CORE", "lift + stair", ""),
]
ROOF = [
    (3.1, 13.0, "ROOF GARDEN", "planters, pergola, seats", "~48 m2"),
    (6.6, 2.7, "SOLAR PV", "array", ""),
    (2.1, 3.2, "WATER", "tanks on stand", ""),
    (13.8, 2.8, "STAIR", "head + exit", ""),
    (11.6, 1.4, "LIFT", "overrun", ""),
    (8.0, 20.0, "ROOF", "flat, falls to outlets", ""),
]


# ---------------------------------------------------------------- sheet maker
def make_plan_sheet(geo, plan_key, labels, title, number, m_per_mm=75,
                    ox_mm=250, oy_mm=490):
    img, d = sheet(title, number, f"1:{m_per_mm}")
    plan = geo['plans'][plan_key]
    v = view_plan(d, plan, geo['boxes'], geo['openings'], labels,
                  ox_mm * MM, oy_mm * MM, m_per_mm)
    scale_bar(d, (SW - M - 90 * MM, SH - M - 150 * MM), m_per_mm)
    t((d, (M + 6 * MM, M + 8 * MM)), 4.2, title, FONT_B)
    _z = plan['z']
    _zl = f"{_z:+.2f}" if _z else "0.00"
    t((d, (M + 6 * MM, M + 15 * MM)), 2.6,
      f"Cut at {_zl} m ({_z - FLOOR_FFL.get(plan_key, _z):+.2f} m above FFL). "
      f"Dimensions in metres. Do not scale from this drawing.",
      FONT_R, fill=(90, 90, 90))
    return img


def make_section_sheet(geo, title, number):
    img, d = sheet(title, number, "1:100")
    m = 100
    # stacked: long section in the upper band, cross section below it
    v1 = View(70 * MM, 243 * MM, m)
    draw_section(d, v1, geo['sections']['LONG_A'], geo['boxes'], 0, 0)
    t((d, (70 * MM, 243 * MM + 10 * MM)), 3.4,
      "SECTION A-A  —  LONG SECTION ON GRID LINE C", FONT_B)
    v2 = View(70 * MM, 489 * MM, m)
    draw_section(d, v2, geo['sections']['CROSS_B'], geo['boxes'], 0, 0)
    t((d, (70 * MM, 489 * MM + 10 * MM)), 3.4,
      "SECTION B-B  —  CROSS SECTION THROUGH COURTYARD", FONT_B)
    scale_bar(d, (SW - M - 130 * MM, SH - M - 150 * MM), m)
    return img


def make_elevation_sheet(geo, title, number):
    img, d = sheet(title, number, "1:125")
    m = 125
    spots = [(70, 470, 'Y', False, "WEST ELEVATION  —  STREET / GATE"),
             (70, 300, 'Y', True, "EAST ELEVATION  —  REAR"),
             (470, 470, 'X', True, "NORTH ELEVATION"),
             (470, 300, 'X', False, "SOUTH ELEVATION")]
    for ox_mm, oy_mm, ax, flip, lab in spots:
        v = View(ox_mm * MM, oy_mm * MM, m)
        draw_elevation(d, v, geo['boxes'], ax, flip)
        t((d, (ox_mm * MM, oy_mm * MM + 8 * MM)), 3.2, lab, FONT_B)
        # ground line
        p0, p1 = v.p(-4, 0), v.p(20, 0)
        line(d, p0, p1, LW_CUT)
        # datum levels
        for lv, nm in ((0.0, "+0.00"), (16.20, "ROOF +16.20"), (17.30, "PARAPET +17.30")):
            p = v.p(-4, lv)
            t((d, (p[0] - 2 * MM, p[1])), 2.1, nm, FONT_R, anchor="rm",
              fill=(110, 110, 110))
    scale_bar(d, (SW - M - 120 * MM, SH - M - 150 * MM), m)
    t((d, (M + 6 * MM, M + 8 * MM)), 2.5,
      "Side elevations abut the boundary walls and carry no windows (design brief); "
      "they are shown for completeness.", FONT_R, fill=(90, 90, 90))
    return img


# Finished floor levels, used to report how far above FFL each plan is cut.
FLOOR_FFL = {'B1': -2.00, 'GF': 0.90, 'L1': 4.20, 'L2': 7.20,
             'L3': 10.20, 'L4': 13.20, 'ROOF': 16.20}

AREA_SCHEDULE = [
    # B1: the plot is 15.24 x 30.48 = 464.5 m2, so the basement cannot exceed
    # that. The previous figure of 620 m2 was larger than the entire site.
    ("B1  Basement parking", "9 bays + bikes", "464.5 m2 gross"),
    ("GF  Commercial shop", "1 unit", "16.7 m2"),
    ("GF  Guard house + WC", "1", "6.6 m2"),
    ("GF  Shaded colonnade", "-", "48.1 m2"),
    ("GF  2-bed flat", "1 unit", "87.1 m2"),
    ("GF  Courtyard, open to sky", "-", "112.1 m2"),
    ("L1-L4  1-bed (front)", "4 units", "~63 m2 each"),
    ("L1-L4  2-bed (north wing)", "4 units", "~99 m2 each"),
    ("L1-L4  2-bed (rear, premium)", "4 units", "~107 m2 each"),
    # roof terrace in the model is 5.70 x 10.00 m, not the ~120 m2 previously shown
    ("Roof  garden terrace", "pergola, planters, seats", "57.0 m2"),
    ("Roof  slab (excl. terrace fit-out)", "-", "327.7 m2"),
]
UNIT_SCHEDULE = [
    ("Type A 1-bed", "living/kitchenette", "20-24 m2"),
    ("Type A 1-bed", "bedroom", ">=3.0 x 3.6 m"),
    ("Type A 1-bed", "bathroom", "~1.8 x 2.2 m"),
    ("Type B 2-bed", "living / dining", "20-26 m2"),
    ("Type B 2-bed", "kitchen + drying", "7-9 m2"),
    ("Type B 2-bed", "master + en-suite", ">=3.3 x 3.6 + 1.8 x 2.4 m"),
    ("Type B 2-bed", "bedroom 2", ">=3.0 x 3.3 m"),
    ("Type B 2-bed", "common bath / linen", "1.8 x 2.2 m / store"),
]


def table(d, x, y, w, rows, headers, widths, title):
    t((d, (x, y - 6 * MM)), 3.2, title, FONT_B)
    rh = 6.4 * MM
    y0 = y
    d.rectangle([x, y0, x + w, y0 + rh], fill=(38, 38, 42))
    cx = x + 2 * MM
    for h, ww in zip(headers, widths):
        t((d, (cx, y0 + rh / 2)), 2.5, h, FONT_B, anchor="lm", fill=(255, 255, 255))
        cx += ww * MM
    for i, row in enumerate(rows):
        yy = y0 + rh * (i + 1)
        if i % 2 == 0:
            d.rectangle([x, yy, x + w, yy + rh], fill=(242, 242, 244))
        d.rectangle([x, yy, x + w, yy + rh], outline=(190, 190, 195), width=1)
        cx = x + 2 * MM
        for cell, ww in zip(row, widths):
            t((d, (cx, yy + rh / 2)), 2.4, str(cell), FONT_R, anchor="lm")
            cx += ww * MM
    return y0 + rh * (len(rows) + 1)


def make_schedule_sheet(geo, title, number):
    img, d = sheet(title, number, "NTS")
    table(d, M + 14 * MM, M + 22 * MM, 250 * MM, AREA_SCHEDULE,
          ["ELEMENT / LEVEL", "QUANTITY", "AREA"], [95, 60, 45],
          "AREA SCHEDULE")
    table(d, M + 14 * MM, M + 120 * MM, 250 * MM, UNIT_SCHEDULE,
          ["UNIT", "ROOM", "SIZE"], [55, 85, 60],
          "ROOM SCHEDULE — TYPICAL")
    t((d, (M + 300 * MM, M + 22 * MM)), 3.2, "COMPLIANCE SUMMARY", FONT_B)
    rows = [
        ("s.17  balustrades >= 1.0 m", "1.10 m", "PASS"),
        ("s.20  courtyard >= 35 m2, min dim 4.5 m", "112.1 m2 / 7.14 m", "PASS"),
        ("s.21  <= 5 storeys, single stair + ramp", "5 storeys", "PASS"),
        ("s.38  EV bays >= 5%", "1 of 9 = 11.1%", "PASS"),
        ("s.41  vehicle barriers 375-610 mm", "450 mm kerb", "PASS"),
        ("s.42  <= 1:25 within 5 m of road", "4.0%", "PASS"),
        ("s.44  ramp <= 12.5%, width >= 3.0 m", "12.5%, 3.18 m", "PASS"),
        ("s.129 external walls >= 200 mm", "200 mm stone + 300 RC", "PASS"),
        ("s.137 zone of space >= H/3", "7.14 m >= 4.40 m", "PASS"),
        # The model contains 28 glazing panels = 119.5 m2 of glass. Against the
        # 1,670.7 m2 of floor plate that is 7.2% (6.9-8.2% per storey), below
        # the 10% threshold. The 37.6% previously printed here compared the
        # glazing of ALL floors against the area of ONE floor.
        ("s.143(1) windows >= 10% floor area", "7.2% modelled - see note", "CHECK"),
        ("s.143(2) glazing + balcony uplift >= 30%", "not verified", "CHECK"),
        ("s.194(2) stair continues to roof", "to +19.00 m", "PASS"),
        ("s.205 risers 150-180, treads 250-320", "176 / 280 mm", "PASS"),
        ("s.353 accessible bay 3.6 m by lift", "Bay 01", "PASS"),
        ("s.400 basement 2 escape routes", "stair + ramp", "PASS"),
        ("s.18  6 m open front space", "shop on boundary", "CONFLICT"),
        ("s.19  1.5 m open side space", "walls both sides", "CONFLICT"),
    ]
    y = M + 28 * MM
    for a, b, c in rows:
        col = (0, 0, 0)
        if c == "CONFLICT":
            col = (170, 30, 30)
        elif c in ("NOTE", "CHECK"):
            col = (170, 110, 0)
        t((d, (M + 300 * MM, y)), 2.5, a, FONT_R)
        t((d, (M + 445 * MM, y)), 2.5, b, FONT_R)
        t((d, (M + 520 * MM, y)), 2.5, c, FONT_B, fill=col)
        y += 7.0 * MM
    notes = [
        "NOTES",
        "1. GFA: 1,357 m2 on the basis of enclosed floor area, excluding the courtyard",
        "   void, the open colonnade and the open access galleries. Including every slab",
        "   plate the measured figure is 1,670.7 m2 above ground (2,135 m2 with B1).",
        "2. s.143(1): the model contains 28 glazing panels totalling 119.5 m2, which is",
        "   7.2% of the floor plate - below the 10% required. The spec's window schedule",
        "   lists 119 windows, so the model is probably incomplete rather than the",
        "   design failing. Both must be reconciled before submission.",
        "3. The saved model has no openings cut in the host walls; the drawings cut them",
        "   at render time. See Model QA & Render Notes.",
    ]
    for i, ln in enumerate(notes):
        t((d, (M + 300 * MM, y + 4 * MM + i * 4 * MM)), 2.3, ln, FONT_R,
          fill=(70, 70, 70) if i == 0 else (120, 80, 0))
    return img


def make_cover(geo, title, number):
    img, d = sheet(title, number, "1:200")
    t((d, (M + 8 * MM, M + 16 * MM)), 7.0, "COURTYARD APARTMENTS", FONT_B)
    t((d, (M + 8 * MM, M + 26 * MM)), 3.6,
      "50 ft x 100 ft (15.24 m x 30.48 m) plot  |  Nairobi, Kenya  |  "
      "GF + L1-L4, 13 homes, 9 basement bays", FONT_R, fill=(80, 80, 80))

    # schematic site key plan
    m = 200
    v = View(120 * MM, 430 * MM, m)
    p0, p1 = v.p(0, 0), v.p(15.24, 30.48)
    d.rectangle([p0[0], p0[1], p1[0], p1[1]], outline=(0, 0, 0),
                width=int(LW_CUT))
    # street -- kept inside the sheet frame; the previous extents (-40 m to
    # +60 m) ran the band off the left edge of the page.
    sp0, sp1 = v.p(-4, -12), v.p(19.24, 0)
    d.rectangle([min(sp0[0], sp1[0]), min(sp0[1], sp1[1]),
                 max(sp0[0], sp1[0]), max(sp0[1], sp1[1])],
                fill=(228, 228, 230), outline=(150, 150, 150), width=1)
    t((d, ((sp0[0] + sp1[0]) / 2, (sp0[1] + sp1[1]) / 2)), 3.0, "STREET", FONT_B,
      anchor="mm", fill=(90, 90, 90))
    # building footprint
    fp0, fp1 = v.p(0, 0), v.p(15.24, 30.48)
    d.rectangle([min(fp0[0], fp1[0]) + 2, min(fp0[1], fp1[1]) + 2,
                 max(fp0[0], fp1[0]) - 2, max(fp0[1], fp1[1]) - 2],
                outline=(90, 90, 90), width=2)
    cp0, cp1 = v.p(6.30, 7.30), v.p(13.44, 23.00)
    d.rectangle([min(cp0[0], cp1[0]), min(cp0[1], cp1[1]),
                 max(cp0[0], cp1[0]), max(cp0[1], cp1[1])],
                fill=(206, 226, 200), outline=(90, 130, 90), width=2)
    t((d, ((cp0[0] + cp1[0]) / 2, (cp0[1] + cp1[1]) / 2)), 2.8, "COURTYARD",
      FONT_B, anchor="mm", fill=(60, 110, 60))
    t((d, (fp0[0], fp0[1] + 6 * MM)), 3.0, "BUILDING FOOTPRINT — COVERS PLOT", FONT_R)
    t((d, (v.p(0, -16)[0], v.p(0, -16)[1])), 3.0,
      "GATE FACES WEST", FONT_B, fill=(90, 90, 90))
    scale_bar(d, (SW - M - 110 * MM, SH - M - 150 * MM), m)

    # key data table
    table(d, M + 210 * MM, M + 34 * MM, 200 * MM,
          [("Plot", "15.24 m x 30.48 m (50 x 100 ft)"),
           ("Levels", "B1, GF, L1, L2, L3, L4, roof"),
           ("Homes", "13 (1 GF + 3 per upper floor)"),
           ("Parking", "9 bays incl. 1 accessible, 1 EV"),
           ("Courtyard", "112.1 m2 open to sky"),
           ("GF FFL", "+0.90 m podium"),
           ("Roof slab", "+16.20 m; parapet +17.30 m"),
           ("Code", "Kenya National Building Code 2024 (LN 47/2024)")],
          ["ITEM", "VALUE"], [55, 145], "KEY DATA")
    t((d, (M + 210 * MM, M + 118 * MM)), 3.2, "DRAWING REGISTER", FONT_B)
    reg = [("S01", "Cover, key plan, drawing register"),
           ("S02", "Basement floor plan  B1  -2.00"),
           ("S03", "Ground floor plan  GF  +0.90"),
           ("S04", "Typical upper floor plan  L1-L4"),
           ("S05", "Roof plan  +16.20"),
           ("S06", "Sections A-A and B-B"),
           ("S07", "Elevations"),
           ("S08", "Schedules and compliance summary")]
    y = M + 124 * MM
    for a, b in reg:
        t((d, (M + 210 * MM, y)), 2.5, a, FONT_B)
        t((d, (M + 224 * MM, y)), 2.5, b, FONT_R)
        y += 6.2 * MM
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    args = ap.parse_args()
    only = [s.strip() for s in args.only.split(',') if s.strip()]

    with open(GEO, encoding='utf-8') as f:
        geo = json.load(f)
    os.makedirs(OUT, exist_ok=True)

    jobs = [
        ('S01', lambda: make_cover(geo, "COVER / KEY PLAN",
                                   "S01")),
        ('S02', lambda: make_plan_sheet(geo, 'B1', ROOMS['B1'],
                                        "BASEMENT FLOOR PLAN  —  B1  (-2.00)",
                                        "S02")),
        ('S03', lambda: make_plan_sheet(geo, 'GF', ROOMS['GF'],
                                        "GROUND FLOOR PLAN  —  GF  (+0.90)",
                                        "S03")),
        ('S04', lambda: make_plan_sheet(geo, 'L1', TYPICAL,
                                        "TYPICAL UPPER FLOOR PLAN  —  L1-L4",
                                        "S04")),
        ('S05', lambda: make_plan_sheet(geo, 'ROOF', ROOF,
                                        "ROOF PLAN  —  +16.20", "S05")),
        ('S06', lambda: make_section_sheet(geo, "SECTIONS", "S06")),
        ('S07', lambda: make_elevation_sheet(geo, "ELEVATIONS", "S07")),
        ('S08', lambda: make_schedule_sheet(geo, "SCHEDULES & COMPLIANCE", "S08")),
    ]

    built = []
    for code, fn in jobs:
        if only and code not in only:
            continue
        try:
            img = fn()
        except Exception as e:
            import traceback
            print(f"{code} FAILED: {e}")
            traceback.print_exc()
            continue
        png = os.path.join(OUT, f"{code}.png")
        img.save(png, optimize=True)
        built.append(code)
        print(f"{code}: {png}  ({os.path.getsize(png)/1e6:.1f} MB)")

    # The PDF is always assembled from EVERY sheet present on disk, in order --
    # an earlier version built it only from the sheets generated in that run, so
    # a `--only S07` re-run silently replaced the 8-page set with a 1-page one.
    codes = [c for c, _ in jobs]
    present = [c for c in codes if os.path.exists(os.path.join(OUT, f"{c}.png"))]
    missing = [c for c in codes if c not in present]
    if present:
        pages = [Image.open(os.path.join(OUT, f"{c}.png")).convert('RGB') for c in present]
        pdf = os.path.join(OUT, 'Courtyard Apartments - Drawing Set.pdf')
        pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=DPI)
        print(f"PDF: {pdf}  ({os.path.getsize(pdf)/1e6:.1f} MB, {len(pages)} sheets: "
              f"{', '.join(present)})")
        if missing:
            print(f"  !! MISSING from the set: {', '.join(missing)}")
        if only and len(built) != len(codes):
            print(f"  (regenerated {', '.join(built)}; the PDF still contains all "
                  f"{len(present)} sheets on disk)")


if __name__ == '__main__':
    main()

