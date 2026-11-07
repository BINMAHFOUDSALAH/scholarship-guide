"""Small copies of the university logos, for the rows that show a few of them (decision 084).

The logos (decision 049) are up to 128px tall and 52KB; «الآن» shows a handful at 26px. This writes
app/static/img/universities/small/<id>.png at 52px tall (sharp on 2x screens), pixels only, no metadata.
Run it again after adding logos to data/university_logos.json:

    python scripts/logo_thumbs.py
"""

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "app" / "static"
OUT = STATIC / "img" / "universities" / "small"
HEIGHT = 52


def main():
    logos = json.loads((ROOT / "data" / "university_logos.json").read_text(encoding="utf-8"))["logos"]
    OUT.mkdir(parents=True, exist_ok=True)
    for uid, logo in sorted(logos.items()):
        src = STATIC / logo["file"]
        if not src.is_file():
            continue
        im = Image.open(src).convert("RGBA")
        if im.height > HEIGHT:
            im = im.resize((max(1, round(im.width * HEIGHT / im.height)), HEIGHT), Image.LANCZOS)
        # A 128-colour palette (logos are flat colour) and pixels only: no text chunks or profiles carried over.
        small = im.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
        small.info.clear()
        small.save(OUT / f"{uid}.png", optimize=True)
    sizes = [p.stat().st_size for p in OUT.glob("*.png")]
    print(f"{len(sizes)} small logos, {sum(sizes) // 1024} KB in all, largest {max(sizes) // 1024} KB")


if __name__ == "__main__":
    main()
