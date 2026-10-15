"""
make_board.py -- A1 presentation board compositing the finished renders with the
key drawings. A single shareable image for social and for client presentation.

  python make_board.py
"""
import glob
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
DEL = os.path.join(PROJ, "render", "delivery")
DRW = os.path.join(PROJ, "docs", "drawings")
OUT = os.path.join(PROJ, "docs", "presentation")
os.makedirs(OUT, exist_ok=True)

DPI = 150
MM = DPI / 25.4
SW, SH = int(841 * MM), int(594 * MM)

F_R = "C:/Windows/Fonts/arial.ttf"
F_B = "C:/Windows/Fonts/arialbd.ttf"
NAVY = (31, 58, 95)
ACCENT = (201, 123, 74)
GREY = (105, 105, 110)


def f(path, mm):
    return ImageFont.truetype(path, int(mm * MM))


def fit(img, w, h):
    """Cover-fit an image into a w x h box, centre-cropped."""
    iw, ih = img.size
    s = max(w / iw, h / ih)
    nw, nh = int(iw * s + 0.5), int(ih * s + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return img.crop((x, y, x + w, y + h))


def contain(img, w, h):
    iw, ih = img.size
    s = min(w / iw, h / ih)
    img = img.resize((int(iw * s), int(ih * s)), Image.LANCZOS)
    out = Image.new("RGB", (w, h), (255, 255, 255))
    out.paste(img, ((w - img.size[0]) // 2, (h - img.size[1]) // 2))
    return out


def load(name):
    p = os.path.join(DEL, name)
    return Image.open(p).convert("RGB") if os.path.exists(p) else None


def main():
    board = Image.new("RGB", (SW, SH), (250, 250, 251))
    d = ImageDraw.Draw(board)

    m = 18 * MM
    d.rectangle([m, m, SW - m, SH - m], outline=(210, 210, 214), width=int(0.4 * MM))

    # ---- header --------------------------------------------------------
    d.rectangle([m, m, SW - m, m + 34 * MM], fill=NAVY)
    d.text((m + 10 * MM, m + 6 * MM), "COURTYARD APARTMENTS",
           font=f(F_B, 13), fill=(255, 255, 255))
    d.text((m + 10 * MM, m + 21 * MM),
           "15.24 x 30.48 m  (50 x 100 ft) plot  ·  Nairobi, Kenya  ·  "
           "GF + L1–L4, 13 homes, 9 basement bays",
           font=f(F_R, 5), fill=(214, 224, 238))
    d.text((SW - m - 10 * MM, m + 8 * MM), "ARCHITECTURAL PRESENTATION",
           font=f(F_B, 7), fill=ACCENT, anchor="ra")
    d.text((SW - m - 10 * MM, m + 19 * MM),
           "Issue P01  ·  October 2026  ·  renders: Blender EEVEE Next, CC0 HDRI + PBR",
           font=f(F_R, 4), fill=(200, 212, 228), anchor="ra")

    # ---- render grid ---------------------------------------------------
    top = m + 40 * MM
    gw = (SW - 2 * m - 4 * 6 * MM) / 4.0
    gh = gw * 9 / 16
    shots = ["01_Courtyard_Garden_16x9.jpg", "03_Street_Facade_16x9.jpg",
             "06_Roof_Pergola_Sunset_16x9.jpg", "07_Twilight_Street_16x9.jpg",
             "02_Courtyard_Void_Aerial_16x9.jpg", "04_LivingRoom_L3_16x9.jpg",
             "05_L3_Gallery_Overlook_16x9.jpg", "08_Aerial_Hero_16x9.jpg"]
    labels = ["COURTYARD GARDEN", "STREET ELEVATION — GOLDEN HOUR",
              "ROOF PERGOLA AT SUNSET", "BLUE HOUR",
              "COURTYARD VOID FROM ABOVE", "L3 LIVING ROOM",
              "L3 GALLERY OVERLOOK", "AERIAL THREE-QUARTER"]
    for i, (s, lab) in enumerate(zip(shots, labels)):
        r, c = divmod(i, 4)
        x = m + c * (gw + 6 * MM)
        y = top + r * (gh + 14 * MM)
        im = load(s)
        if im is None:
            continue
        board.paste(fit(im, int(gw), int(gh)), (int(x), int(y)))
        d.rectangle([x, y, x + gw, y + gh], outline=(255, 255, 255), width=int(0.5 * MM))
        d.text((x, y + gh + 1.6 * MM), lab, font=f(F_B, 3.4), fill=NAVY)
    bottom_of_grid = top + 2 * (gh + 14 * MM)

    # ---- drawings strip ------------------------------------------------
    dy = bottom_of_grid + 4 * MM
    dh = SH - m - 12 * MM - dy
    if dh > 40 * MM:
        dw = dh * 1.414
        for i, (sheet, lab) in enumerate([
                ("S03.png", "GROUND FLOOR PLAN"),
                ("S04.png", "TYPICAL UPPER FLOOR PLAN"),
                ("S06.png", "SECTIONS A-A / B-B")]):
            p = os.path.join(DRW, sheet)
            if not os.path.exists(p):
                continue
            x = m + i * (dw + 6 * MM)
            if x + dw > SW - m - 92 * MM:
                break
            board.paste(contain(Image.open(p).convert("RGB"), int(dw), int(dh)),
                        (int(x), int(dy)))
            d.rectangle([x, dy, x + dw, dy + dh], outline=(205, 205, 210),
                        width=int(0.3 * MM))
            d.text((x, dy + dh + 1.4 * MM), lab, font=f(F_B, 3.2), fill=GREY)

    # ---- key data panel ------------------------------------------------
    px = SW - m - 86 * MM
    pw = 86 * MM - 2 * MM
    d.rectangle([px, dy, px + pw, dy + dh], fill=(242, 243, 245),
                outline=(205, 205, 210), width=int(0.3 * MM))
    d.text((px + 4 * MM, dy + 4 * MM), "KEY DATA", font=f(F_B, 4.4), fill=NAVY)
    rows = [
        ("Plot", "15.24 x 30.48 m"),
        ("Storeys", "GF + L1–L4 + roof"),
        ("Dwellings", "13 (1 + 3 per floor)"),
        ("Parking", "9 bays, 1 accessible, 1 EV"),
        ("Courtyard", "112.1 m2 open to sky"),
        ("GFA", "1,363 m2 (1,983 m2 incl. B1)"),
        ("Cost / m2", "KES 241,700 excl. basement"),
        ("Cost / home", "KES 25.3 M"),
        ("Structure", "RC frame, flat slabs"),
        ("External walls", "200 mm quarry stone, ISSB"),
        ("Sun shading", "timber fins W, hoods S"),
        ("Code", "Kenya NBC 2024"),
    ]
    yy = dy + 12 * MM
    for k, v in rows:
        d.text((px + 4 * MM, yy), k, font=f(F_B, 3.2), fill=GREY)
        d.text((px + 4 * MM, yy + 3.8 * MM), v, font=f(F_R, 3.4), fill=(20, 20, 24))
        yy += 9.2 * MM

    out = os.path.join(OUT, "Courtyard Apartments - Presentation Board.jpg")
    board.save(out, quality=92, subsampling=1, optimize=True)
    print(f"wrote {out}  ({os.path.getsize(out)/1e6:.1f} MB)")

    small = os.path.join(OUT, "Courtyard Apartments - Presentation Board (web).jpg")
    board.resize((1920, int(1920 * SH / SW)), Image.LANCZOS).save(
        small, quality=88, optimize=True)
    print(f"wrote {small}  ({os.path.getsize(small)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
