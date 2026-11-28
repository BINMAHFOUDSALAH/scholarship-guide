"""Builds وضّاح's homepage animation rig (app/static/img/waddah/hero/) from the existing renders in marketing/assets/waddah.

    python scripts/waddah_rig.py marketing/assets/waddah app/static/img/waddah/hero

The renders are flat images, so the rig keeps them whole: two poses on one 360x340 stage with the same feet (scaled so
the agal ring is the same width in both), the laptop pose's eyes painted out and returned as ellipses (drawn as their
own layer in home.html, so they can squint), and the point pose mirrored so it points toward the search field. Needs
numpy and Pillow (a developer tool, not used by the site). It prints the eyes' positions for home.html.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

src = Path(sys.argv[1])
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
AGAL = 150          # the head ring's width on the stage, px
CW, CH = 360, 340   # the stage
AX, AY = 180, 334   # where the feet touch, on the stage


def load(name, mirror=False):
    im = Image.open(src / f"{name}.webp").convert("RGBA")
    return ImageOps.mirror(im) if mirror else im


def measure(im):
    a = np.array(im).astype(int)
    alpha = a[..., 3]
    ys, xs = np.where(alpha > 40)
    top, bottom = ys.min(), ys.max()
    feet = np.where(alpha[bottom - 4] > 40)[0]
    foot_x = (feet.min() + feet.max()) / 2
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    grey = (abs(r - g) < 12) & (abs(g - b) < 12) & (r < 90) & (r > 25) & (alpha > 200)
    grey[top + 320:] = False   # the agal only, not the laptop's keys
    gx = np.where(grey)[1]
    return {"agal": gx.max() - gx.min(), "foot_x": foot_x, "bottom": bottom}


def place(im, m):
    s = AGAL / m["agal"]
    small = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    stage = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ox = round(AX - m["foot_x"] * s)
    oy = round(AY - m["bottom"] * s)
    stage.alpha_composite(small, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
    return stage, s, ox, oy


def lift_eyes(im):
    """Paint the eyes out with the visor's own colour (a diffusion fill from the visor around them) and return
    the eyes as ellipses."""
    a = np.array(im).astype(float)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    lime = (g > 170) & (r > 140) & (b < 170) & (g > b + 50) & (al > 200)
    face = np.zeros_like(lime)
    face[470:670, 560:870] = True   # the visor, where the laptop pose's eyes are (probe.py)
    lime &= face
    ys, xs = np.where(lime)
    # keep the two blobs on the visor (the largest lime area in the middle of the face)
    mask_img = Image.fromarray((lime * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
    mask = np.array(mask_img) > 0
    colour = np.median(a[lime][:, :3], axis=0)
    eyes = []
    xs_sorted = np.sort(np.unique(xs))
    d = np.diff(xs_sorted)
    split = xs_sorted[int(np.argmax(d))] + 1
    for sel in (xs < split, xs >= split):
        ex, ey = xs[sel], ys[sel]
        eyes.append({"cx": (ex.min() + ex.max()) / 2, "cy": (ey.min() + ey.max()) / 2,
                     "rx": (ex.max() - ex.min() + 1) / 2, "ry": (ey.max() - ey.min() + 1) / 2})
    # diffusion fill inside the mask's bounding box
    y0, y1 = ys.min() - 20, ys.max() + 20
    x0, x1 = xs.min() - 20, xs.max() + 20
    crop = a[y0:y1, x0:x1, :3].copy()
    m = mask[y0:y1, x0:x1]
    crop[m] = np.array([22, 70, 45])
    for _ in range(600):
        p = np.pad(crop, ((1, 1), (1, 1), (0, 0)), mode="edge")
        avg = (p[:-2, 1:-1] + p[2:, 1:-1] + p[1:-1, :-2] + p[1:-1, 2:]) / 4
        crop[m] = avg[m]
    a[y0:y1, x0:x1, :3] = crop
    return Image.fromarray(a.astype(np.uint8), "RGBA"), eyes, colour


laptop = load("laptop")
lm = measure(laptop)
body, eyes, colour = lift_eyes(laptop)
lean, ls, lox, loy = place(body, lm)
point = load("point", mirror=True)
pm = measure(point)
pt, ps, pox, poy = place(point, pm)

lean.save(out / "lean-laptop.webp", quality=90, method=6)
pt.save(out / "point.webp", quality=90, method=6)
# A reference of the untouched laptop pose on the same stage, to check the eyes line up.
# (A check image of the untouched pose on the same stage helps when the renders change: place(laptop, lm)[0].)
meta = {"stage": [CW, CH], "feet": [AX, AY], "eye_colour": "#%02x%02x%02x" % tuple(int(c) for c in colour),
        "eyes": [{k: round((v * ls) + (lox if k == "cx" else loy if k == "cy" else 0), 1) for k, v in e.items()} for e in eyes],
        "scale": {"laptop": ls, "point": ps}}
print(json.dumps(meta, indent=1))

