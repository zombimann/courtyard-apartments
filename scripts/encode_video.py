"""
encode_video.py -- photographic finish + MP4 encode for the render frames.

Two jobs:
  1. apply the same finishing pass as the stills (bloom, grade, grain, vignette)
     to every frame, written to a _graded folder;
  2. encode those frames to H.264 MP4 using Blender's bundled FFmpeg (there is no
     system ffmpeg on this machine).

Also writes a 16:9 centre-crop version for LinkedIn / YouTube / X, since the
primary render is 9:16 for Reels, Shorts and WhatsApp status.

  python encode_video.py --src render/video1/video_fly --fps 24 `
      --out "render/videos/Courtyard Walkthrough.mp4"
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import finish as fin  # noqa: E402

PROJ = os.path.normpath(os.path.join(HERE, ".."))

# No ffmpeg on PATH and Blender 5.2 no longer exposes FFMPEG through
# image_settings.file_format, so a real ffmpeg binary is located on disk instead.
# Search locations are derived from the user profile, never hardcoded.
_HOME = os.path.expanduser("~")
FFMPEG_GLOBS = [
    os.path.join(_HOME, "AppData", "Local", "**", "ffmpeg.exe"),
    os.path.join(_HOME, "scoop", "apps", "**", "ffmpeg.exe"),
    os.path.join(_HOME, "AppData", "Local", "Microsoft", "WinGet", "**", "ffmpeg.exe"),
    r"C:\Program Files\**\ffmpeg.exe",
    r"C:\Program Files (x86)\**\ffmpeg.exe",
    r"C:\ffmpeg\**\ffmpeg.exe",
]


def find_ffmpeg():
    import glob as _g
    import shutil
    onpath = shutil.which("ffmpeg")
    if onpath:
        return onpath
    for pat in FFMPEG_GLOBS:
        hits = _g.glob(pat, recursive=True)
        if hits:
            return hits[0]
    return None



def grade_frames(src, dst, vertical_crop=False):
    os.makedirs(dst, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, '*.png')))
    if not files:
        raise SystemExit(f"no frames in {src}")
    print(f"grading {len(files)} frames -> {dst}", flush=True)
    for i, f in enumerate(files):
        img = Image.open(f).convert('RGB')
        if vertical_crop:
            w, h = img.size
            tw, th = 16, 9
            nw = int(round(h * tw / th))
            if nw <= w:
                x0 = (w - nw) // 2
                img = img.crop((x0, 0, x0 + nw, h))
            else:
                nh = int(round(w * th / tw))
                y0 = max(0, (h - nh) // 2)
                img = img.crop((0, y0, w, y0 + nh))
        arr = np.asarray(img, dtype=np.float32) / 255.0
        h, w = arr.shape[:2]

        r = fin.recipe_for('01')
        r.update(dict(bloom=0.34, ca=0.0011, grain=0.0095, vignette=0.26,
                      contrast=0.12, sat=1.06))
        # bloom
        lum = arr[:, :, 0] * 0.2126 + arr[:, :, 1] * 0.7152 + arr[:, :, 2] * 0.0722
        m = np.clip((lum - r['bthresh']) / max(1e-3, 1.0 - r['bthresh']), 0, 1) ** 1.4
        hi = arr * m[:, :, None]
        glow = fin._blur(hi, r['brad']) * 0.62 + fin._blur(hi, r['brad'] * 2.6) * 0.38
        tint = np.array(r['btint'], dtype=np.float32)
        arr = 1.0 - (1.0 - arr) * (1.0 - np.clip(glow * tint[None, None, :] * r['bloom'], 0, 1))
        arr = fin._chromatic(arr, r['ca'])
        arr = fin._curve(arr, r['contrast'], r['lift'], r['gain'], r['gamma'])
        if r['sat'] != 1.0:
            g = arr @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
            arr = g[:, :, None] + (arr - g[:, :, None]) * r['sat']
        arr = np.clip(arr, 0, 1)
        arr = fin._vignette(arr, r['vignette'])
        b = fin._blur(arr, 1.0)
        arr = np.clip(arr + (arr - b) * 0.30, 0, 1)
        rs = np.random.RandomState(1234 + i)          # vary grain per frame
        n = rs.normal(0, 1, size=(h, w)).astype(np.float32)
        n = fin._blur(n[:, :, None].repeat(3, axis=2), 0.55)[:, :, 0]
        lum = arr[:, :, 0] * 0.2126 + arr[:, :, 1] * 0.7152 + arr[:, :, 2] * 0.0722
        wgt = 0.4 + 0.6 * (1.0 - np.abs(2.0 * lum - 1.0))
        arr = np.clip(arr + (n * wgt)[:, :, None] * r['grain'], 0, 1)

        Image.fromarray((arr * 255 + 0.5).astype(np.uint8)).save(
            os.path.join(dst, os.path.basename(f)), optimize=False)
        if (i + 1) % 40 == 0:
            print(f"  {i+1}/{len(files)}", flush=True)
    return files


def encode(frame_dir, out_mp4, fps):
    files = sorted(glob.glob(os.path.join(frame_dir, '*.png')))
    if not files:
        raise SystemExit(f"no graded frames in {frame_dir}")
    ff = find_ffmpeg()
    if not ff:
        raise SystemExit("no ffmpeg binary found")
    os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
    if not out_mp4.endswith('.mp4'):
        out_mp4 += '.mp4'
    first = os.path.basename(files[0])
    import re
    m = re.match(r'^(.*?)(\d+)(\.png)$', first)
    if not m:
        raise SystemExit(f"cannot infer frame numbering from {first}")
    pattern = m.group(1) + '%0' + str(len(m.group(2))) + 'd.png'
    start = int(m.group(2))
    cmd = [ff, '-y', '-hide_banner', '-loglevel', 'error',
           '-framerate', str(fps), '-start_number', str(start),
           '-i', os.path.join(frame_dir, pattern),
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
           '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out_mp4]
    print(f"encoding {len(files)} frames -> {out_mp4}", flush=True)
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print((p.stderr or '')[-1200:])
        raise SystemExit(f"ffmpeg failed ({p.returncode})")
    print(f"wrote {out_mp4}  ({os.path.getsize(out_mp4)/1e6:.1f} MB)")
    return out_mp4


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--fps', type=int, default=24)
    ap.add_argument('--keep', action='store_true')
    args = ap.parse_args()

    parent = os.path.dirname(os.path.abspath(args.src))
    name = os.path.basename(args.src.rstrip('/\\'))
    graded = os.path.join(parent, name + '_graded')
    graded_wide = os.path.join(parent, name + '_graded_16x9')

    grade_frames(args.src, graded, vertical_crop=False)
    encode(graded, args.out, args.fps)

    base, ext = os.path.splitext(args.out)
    grade_frames(args.src, graded_wide, vertical_crop=True)
    encode(graded_wide, base + '_16x9' + ext, args.fps)

    if not args.keep:
        import shutil
        shutil.rmtree(graded, ignore_errors=True)
        shutil.rmtree(graded_wide, ignore_errors=True)
        print("cleaned intermediate graded frames")


if __name__ == '__main__':
    main()
