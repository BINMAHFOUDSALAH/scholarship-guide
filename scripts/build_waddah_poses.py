"""Cut وضّاح's original renders (marketing/assets/waddah/) into the homepage hero's poses (2026-11-27).

Every pose comes out on the same canvas at the same scale, his agal centred at the same x and his hem at the same y,
so swapping one pose for another never makes him jump, grow or shrink. The scale is set by the head: the agal's
width, found as the widest band of near-black pixels at the top of the render.

Run from the repo root: python scripts/build_waddah_poses.py
Writes app/static/img/waddah/poses/<pose>.webp (each a few KB).
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "marketing" / "assets" / "waddah"
OUT = ROOT / "app" / "static" / "img" / "waddah" / "poses"

# The poses the hero uses (waddah-hero.js names them); point is mirrored there when the field is on the other side.
POSES = ["logo", "unsure", "cheer", "point", "wave", "search", "read"]

CANVAS = (344, 300)   # about 2.5× the size it's shown at on a laptop (136 × 118)
HEIGHT = 250          # agal top to hem on the canvas: sets every pose's scale
AGAL_X = 166          # the agal's centre on the canvas
HEM_Y = 296           # the lowest point of his hem on the canvas


def black(p):
    """The agal's near-black, not the visor's dark green (whose green runs well above its red)."""
    return p[3] > 200 and max(p[:3]) < 75 and p[1] - p[0] < 14


def agal(im):
    """The agal's centre x and top y: the widest run of near-black, opaque pixels in the top third of the render,
    and the first row that holds any of it."""
    w, h = im.size
    px = im.load()
    best = (0, 0, 0)
    for y in range(h // 3):
        xs = [x for x in range(w) if black(px[x, y])]
        if xs and xs[-1] - xs[0] > best[0] and len(xs) > (xs[-1] - xs[0]) * 0.6:
            best = (xs[-1] - xs[0], (xs[0] + xs[-1]) / 2, y)
    if not best[0]:
        raise SystemExit("no agal found")
    top = next(y for y in range(h // 3) if sum(black(px[x, y]) for x in range(w)) > best[0] * 0.15)
    return best[1], top


def hem(im):
    """The lowest row with a solid pixel (his feet; nothing he holds hangs lower in these poses)."""
    alpha = im.getchannel("A").point(lambda a: 255 if a > 128 else 0)
    return alpha.getbbox()[3]


def build(name):
    im = Image.open(SOURCE / f"{name}.webp").convert("RGBA")
    small = im.copy()
    small.thumbnail((400, 400))   # find the agal on a small copy, for speed
    k = im.width / small.width
    cx, top = agal(small)
    cx, top = cx * k, top * k
    scale = HEIGHT / (hem(im) - top)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = round(AGAL_X - cx * scale)
    top = round(HEM_Y - hem(im))
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.alpha_composite(im, (max(left, 0), max(top, 0)), (max(-left, 0), max(-top, 0)))
    OUT.mkdir(parents=True, exist_ok=True)
    canvas.save(OUT / f"{name}.webp", "WEBP", quality=88, method=6)
    box = canvas.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()
    clipped = box[0] == 0 or box[1] == 0 or box[2] == CANVAS[0]
    print(f"{name}: scale {scale:.3f}{'  (cut at the canvas edge)' if clipped else ''}")


if __name__ == "__main__":
    for pose in POSES:
        build(pose)
