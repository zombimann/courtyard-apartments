"""
finish.py -- photographic finishing pass and social-media delivery.

Runs OUTSIDE Blender (uses the bundled Python's numpy + Pillow).

What it does to each rendered PNG:
  * highlight bloom / halation (the single biggest "not CG" cue)
  * subtle lateral chromatic aberration
  * unsharp mask to recover the crispness bloom costs
  * filmic S-curve, lift/gain, saturation, split-tone
  * vignette
  * luminance-weighted film grain

Then it writes the aspect ratios the platforms actually want:
  16:9  1920x1080   LinkedIn, X, YouTube, website
  4:5   1080x1350   Instagram feed + carousel
  9:16  1080x1920   Reels, Shorts, Stories, WhatsApp status   (cropped masters)
  1:1   1080x1080   grid / thumbnails

Usage:
  python finish.py --src render/v4 --dst render/delivery [--only 01,03]
"""
import argparse
import glob
import json
import os

import numpy as np
from PIL import Image, ImageFilter

# ---------------------------------------------------------------- recipes
# Per-shot tuning. Warm shots get more bloom, cool interiors less grain.
DEFAULT = dict(bloom=0.30, bthresh=0.70, brad=26.0, btint=(1.00, 0.87, 0.70),
               ca=0.0013, sharpen=0.36, contrast=0.10, sat=1.06,
               lift=0.004, gain=1.020, gamma=0.985, grain=0.0120,
               vignette=0.22, split=(1.010, 0.996, 0.980))

RECIPES = {
    '01': dict(),                                   # courtyard, neutral
    '02': dict(bloom=0.22, grain=0.010),
    '03': dict(bloom=0.46, bthresh=0.62, btint=(1.00, 0.74, 0.44),
               contrast=0.14, sat=1.10, vignette=0.30, split=(1.030, 0.992, 0.968)),
    '04': dict(bloom=0.20, grain=0.014, contrast=0.08, sat=1.03, vignette=0.26),
    '05': dict(bloom=0.24, grain=0.011),
    '06': dict(bloom=0.50, bthresh=0.60, btint=(1.00, 0.72, 0.42),
               contrast=0.15, sat=1.10, vignette=0.30, split=(1.032, 0.990, 0.964)),
    '07': dict(bloom=0.58, bthresh=0.48, btint=(1.00, 0.72, 0.46),
               contrast=0.16, sat=1.08, vignette=0.34, grain=0.016,
               split=(1.020, 0.990, 0.990)),
    '08': dict(bloom=0.30, contrast=0.12, sat=1.05, vignette=0.24),
}

# where to anchor a 4:5 crop (0 = left edge, 1 = right edge) per shot
CROP_ANCHOR = {'01': 0.42, '02': 0.50, '03': 0.46, '04': 0.50,
               '05': 0.50, '06': 0.50, '07': 0.44, '08': 0.50}
VERTICAL_SET = ('01', '03', '06', '07')


def recipe_for(key):
    r = dict(DEFAULT)
    r.update(RECIPES.get(key, {}))
    return r


def _blur(arr, radius):
    im = Image.fromarray(np.clip(arr * 255.0, 0, 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im, dtype=np.float32) / 255.0


def _chromatic(img, amount):
    if amount <= 0:
        return img
    h, w = img.shape[:2]
    out = img.copy()
    for ch, k in ((0, 1.0 + amount), (2, 1.0 - amount)):
        scale = 1.0 + (k - 1.0) * 2.0
        nw, nh = max(2, int(round(w * scale))), max(2, int(round(h * scale)))
        ch_im = Image.fromarray(np.clip(img[:, :, ch] * 255, 0, 255).astype(np.uint8))
        big = ch_im.resize((nw, nh), Image.BICUBIC)
        left, top = (nw - w) // 2, (nh - h) // 2
        out[:, :, ch] = np.asarray(big.crop((left, top, left + w, top + h)),
                                   dtype=np.float32) / 255.0
    return out


def _vignette(img, strength):
    if strength <= 0:
        return img
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / 1.4142
    m = 1.0 - strength * np.clip(r, 0, 1) ** 2.1
    return img * m[:, :, None]


def _curve(x, contrast, lift, gain, gamma):
    y = np.clip(x, 0, 1) ** gamma
    # smooth S-curve around mid grey
    y = y + contrast * (y - 0.5) * (1.0 - abs(2.0 * y - 1.0)) * 2.0
    y = y * gain + lift
    return np.clip(y, 0, 1)


def finish_image(path, out_dir, key, sizes=True):
    r = recipe_for(key)
    im = Image.open(path).convert('RGB')
    img = np.asarray(im, dtype=np.float32) / 255.0
    h, w = img.shape[:2]

    # ---- bloom / halation ------------------------------------------------
    if r['bloom'] > 0:
        lum = img[:, :, 0] * 0.2126 + img[:, :, 1] * 0.7152 + img[:, :, 2] * 0.0722
        m = np.clip((lum - r['bthresh']) / max(1e-3, 1.0 - r['bthresh']), 0, 1)
        m = m ** 1.4
        hi = img * m[:, :, None]
        glow = _blur(hi, r['brad'])
        glow2 = _blur(hi, r['brad'] * 2.6)
        glow = glow * 0.62 + glow2 * 0.38
        tint = np.array(r['btint'], dtype=np.float32)
        img = 1.0 - (1.0 - img) * (1.0 - np.clip(glow * tint[None, None, :] * r['bloom'], 0, 1))

    # ---- lens ------------------------------------------------------------
    img = _chromatic(img, r['ca'])

    # ---- grade -----------------------------------------------------------
    img = _curve(img, r['contrast'], r['lift'], r['gain'], r['gamma'])
    sp = np.array(r['split'], dtype=np.float32)
    lum = img[:, :, 0] * 0.2126 + img[:, :, 1] * 0.7152 + img[:, :, 2] * 0.0722
    img = img * (1.0 + (sp[None, None, :] - 1.0) * lum[:, :, None] * 1.6)
    if r['sat'] != 1.0:
        g = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        img = g[:, :, None] + (img - g[:, :, None]) * r['sat']
    img = np.clip(img, 0, 1)

    # ---- vignette --------------------------------------------------------
    img = _vignette(img, r['vignette'])

    # ---- sharpen ---------------------------------------------------------
    if r['sharpen'] > 0:
        b = _blur(img, 1.1)
        img = np.clip(img + (img - b) * r['sharpen'], 0, 1)

    # ---- grain -----------------------------------------------------------
    if r['grain'] > 0:
        rs = np.random.RandomState(abs(hash(key)) % (2 ** 31))
        n = rs.normal(0.0, 1.0, size=(h, w)).astype(np.float32)
        n = _blur(n[:, :, None].repeat(3, axis=2), 0.55)[:, :, 0]
        lum = img[:, :, 0] * 0.2126 + img[:, :, 1] * 0.7152 + img[:, :, 2] * 0.0722
        wgt = 0.35 + 0.65 * (1.0 - np.abs(2.0 * lum - 1.0))
        img = np.clip(img + (n * wgt)[:, :, None] * r['grain'], 0, 1)

    base = os.path.splitext(os.path.basename(path))[0]
    os.makedirs(out_dir, exist_ok=True)
    master = os.path.join(out_dir, base + '_16x9.jpg')
    Image.fromarray((img * 255.0 + 0.5).astype(np.uint8)).save(master, quality=94,
                                                               subsampling=1, optimize=True)
    out = {'master': master}

    if not sizes:
        return out

    src = Image.fromarray((img * 255.0 + 0.5).astype(np.uint8))

    # 4:5 Instagram crop
    tw, th = 1080, 1350
    ratio = tw / th
    ch = h
    cw = int(round(ch * ratio))
    if cw <= w:
        a = CROP_ANCHOR.get(key, 0.5)
        x0 = int(round((w - cw) * a))
        crop = src.crop((x0, 0, x0 + cw, ch)).resize((tw, th), Image.LANCZOS)
    else:
        cwid = w
        chi = int(round(cwid / ratio))
        y0 = max(0, (h - chi) // 2)
        crop = src.crop((0, y0, cwid, y0 + chi)).resize((tw, th), Image.LANCZOS)
    p45 = os.path.join(out_dir, base + '_4x5.jpg')
    crop.save(p45, quality=94, subsampling=1, optimize=True)
    out['ig_4x5'] = p45

    # 1:1
    s = min(w, h)
    x0 = (w - s) // 2
    y0 = (h - s) // 2
    p11 = os.path.join(out_dir, base + '_1x1.jpg')
    src.crop((x0, y0, x0 + s, y0 + s)).resize((1080, 1080), Image.LANCZOS).save(
        p11, quality=94, subsampling=1, optimize=True)
    out['sq_1x1'] = p11

    # 9:16 vertical from the FINISHED image, not the raw render -- the earlier
    # version cropped the ungraded master and the verticals looked flat.
    if key in VERTICAL_SET:
        tw, th = 1080, 1920
        target = tw / th
        cw = int(round(h * target))
        if cw <= w:
            a = CROP_ANCHOR.get(key, 0.5)
            vx = int(round((w - cw) * a))
            crop_v = src.crop((vx, 0, vx + cw, h))
        else:
            chi = int(round(w / target))
            vy = max(0, int((h - chi) * 0.5))
            crop_v = src.crop((0, vy, w, vy + chi))
        vdir = os.path.join(out_dir, 'vertical')
        os.makedirs(vdir, exist_ok=True)
        pv = os.path.join(vdir, base + '_9x16.jpg')
        crop_v.resize((tw, th), Image.LANCZOS).save(pv, quality=94, subsampling=1,
                                                    optimize=True)
        out['vertical_9x16'] = pv

    return out


def crop_vertical(src_path, out_dir, key):
    """Centre-crop a 16:9 master to 9:16 for Reels / Shorts / status."""
    im = Image.open(src_path).convert('RGB')
    w, h = im.size
    tw, th = 1080, 1920
    target = tw / th
    cw = int(round(h * target))
    if cw <= w:
        a = CROP_ANCHOR.get(key, 0.5)
        x0 = int(round((w - cw) * a))
        im = im.crop((x0, 0, x0 + cw, h))
    else:
        chi = int(round(w / target))
        y0 = max(0, int((h - chi) * 0.5))
        im = im.crop((0, y0, w, y0 + chi))
    im = im.resize((tw, th), Image.LANCZOS)
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, os.path.splitext(os.path.basename(src_path))[0] + '_9x16.jpg')
    im.save(p, quality=94, subsampling=1, optimize=True)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=os.path.join('render', 'v4'))
    ap.add_argument('--dst', default=os.path.join('render', 'delivery'))
    ap.add_argument('--only', default='')
    ap.add_argument('--nosizes', action='store_true')
    args = ap.parse_args()

    only = [x.strip() for x in args.only.split(',') if x.strip()]
    pngs = sorted(glob.glob(os.path.join(args.src, '*.png')))
    manifest = {}
    for p in pngs:
        base = os.path.splitext(os.path.basename(p))[0]
        key = base.split('_')[0]
        if only and key not in only:
            continue
        if base.startswith('video'):
            continue
        info = finish_image(p, args.dst, key, sizes=not args.nosizes)
        manifest[key] = info
        print('finished', base, '->', os.path.basename(info['master']), flush=True)

    # 9:16 verticals are written inside finish_image(), from the graded image.

    with open(os.path.join(args.dst, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=1)
    print(f"\n{len(manifest)} shot(s) finished into {args.dst}")


if __name__ == '__main__':
    main()
