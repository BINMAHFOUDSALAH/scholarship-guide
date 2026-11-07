"""The sky drawings (decision 060): star fields and the الرواد star chart.

Pure layout: positions for decorative SVG, computed once at startup. Nothing here is a fact
shown to students; the chart's universities, ranks and countries come from the Explorer
(the Ministry's guide), and only their places on the drawing are decided here.
"""

import math
import random
from functools import lru_cache


# Fixed seeds, so the sky is the same on every visit.
def star_field(count, width, height, seed, keep_clear=None):
    """[(x, y, r, tier)]: tier 0 = faint, 1 = medium, 2 = bright. keep_clear = (x, y, radius) to leave empty."""
    rng = random.Random(seed)
    stars = []
    while len(stars) < count:
        x, y = rng.uniform(0, width), height * rng.random() ** 1.4  # thinner towards the horizon
        if keep_clear and math.dist((x, y), keep_clear[:2]) < keep_clear[2]:
            continue
        tier = rng.choices((0, 1, 2), weights=(6, 3, 1))[0]
        stars.append((round(x, 1), round(y, 1), (0.9, 1.3, 1.8)[tier], tier))
    return stars


# ---------- The الرواد chart ----------

# Where each country's constellation sits on the 1000 × 520 chart: a schematic world map (west on the
# left, like any map), so the drawing reads as "where these universities are" at a glance.
# A country missing here (if the lists change) is placed automatically along the bottom.
CHART_W, CHART_H = 1000, 520
CLUSTER_AT = {
    "US": (205, 270), "CA": (250, 92),
    "GB": (468, 150), "FR": (488, 236), "CH": (552, 206),
    "CN": (800, 205), "JP": (905, 178), "SG": (782, 392),
}
HOME = (640, 300)  # Saudi Arabia: where the student starts
LABEL_ABOVE = {"GB"}  # its label would sit on France's stars
GOLDEN = math.pi * (3 - math.sqrt(5))


def _spiral(n, spacing):
    """n points on a sunflower spiral around (0, 0): even spacing with no grid."""
    return [(spacing * math.sqrt(i + 0.6) * math.cos(i * GOLDEN + 0.9),
             spacing * math.sqrt(i + 0.6) * math.sin(i * GOLDEN + 0.9)) for i in range(n)]


def _tree(points):
    """The shortest set of lines joining all points (Prim): looks like a constellation, never crosses itself."""
    if len(points) < 2:
        return []
    inside, lines = {0}, []
    while len(inside) < len(points):
        a, b = min(((i, j) for i in inside for j in range(len(points)) if j not in inside),
                   key=lambda ij: math.dist(points[ij[0]], points[ij[1]]))
        inside.add(b)
        lines.append((points[a], points[b]))
    return lines


def rowwad_chart(explorer):
    """Stars, constellation lines and labels for the الرواد list, grouped by country.

    Returns {"stars": [...], "countries": [...], "home": (x, y), "w": .., "h": ..}. Each star carries its
    university id, Arabic name, rank and country; each country its centre, label place, and the path
    of light from the student's home to it (drawn when that country is chosen).
    """
    rows = explorer.listings("arruaad")
    by_country = {}
    for listing, u in rows:
        by_country.setdefault(u["country"], []).append((listing["rank"], u))

    spare = iter((x, 470) for x in range(120, 1000, 140))
    stars, countries = [], []
    for code, items in sorted(by_country.items(), key=lambda kv: -len(kv[1])):
        cx, cy = CLUSTER_AT.get(code) or next(spare)
        items.sort(key=lambda t: t[0])
        offsets = _spiral(len(items), 23 if len(items) > 6 else 21)
        points = [(round(cx + dx, 1), round(cy + dy, 1)) for dx, dy in offsets]
        for (rank, u), (x, y) in zip(items, points):
            stars.append({"id": u["id"], "name_ar": u["name_ar"] or u["name_en"], "name_en": u["name_en"],
                          "rank": rank, "country": code, "x": x, "y": y})
        reach = max(math.dist((cx, cy), p) for p in points)
        # The path of light: a gentle arc from home, bending upwards, ending at the edge of the cluster.
        (hx, hy), angle = HOME, math.atan2(cy - HOME[1], cx - HOME[0])
        ex, ey = cx - math.cos(angle) * (reach + 14), cy - math.sin(angle) * (reach + 14)
        mx, my = (hx + ex) / 2, min(hy, ey) - 0.18 * math.dist((hx, hy), (ex, ey))
        countries.append({
            "code": code, "name_ar": explorer.countries[code]["name_ar"], "count": len(items),
            "x": cx, "y": cy,
            "label_y": round(cy - reach - 14 if code in LABEL_ABOVE else cy + reach + 26, 1),
            "lines": [(a, b) for a, b in _tree(points)],
            "path": f"M{hx} {hy} Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}",
        })
    stars.sort(key=lambda s: s["rank"])
    return {"stars": stars, "countries": countries, "home": HOME, "w": CHART_W, "h": CHART_H}


# ---------- Any set of universities on the map (decisions 083, 084) ----------

# Every country in the lists, on the same schematic map as the الرواد chart (west on the left). These are where each
# constellation would like to be; world_chart() moves them apart when a big list makes them meet.
WORLD_AT = {
    "US": (190, 260), "CA": (215, 92),
    "GB": (420, 118), "NL": (500, 92), "DE": (566, 138), "FR": (444, 222), "CH": (530, 222),
    "ES": (372, 300), "IT": (520, 318),
    "IN": (760, 352), "CN": (800, 200), "KR": (888, 120), "JP": (930, 236), "SG": (812, 452), "AU": (912, 430),
}
HOME_BOX = (HOME[0] - 34, HOME[1] - 26, HOME[0] + 34, HOME[1] + 44)  # the home star and «المملكة» under it
FRAME = (26, 26, CHART_W - 26, CHART_H - 26)
LABEL_GAP, LABEL_H, CHAR_W = 12, 22, 6.6  # the country's name under its stars; CHAR_W ≈ one Arabic letter at 16px


def _star_d(x, y, s):
    """One four-point star (the shape of the الرواد chart's stars) as a relative sub-path, so a whole constellation
    is one <path>: 290 stars on the homepage stay small in the page."""
    k = round(s * 0.16, 2)
    return (f"M{x:.1f} {y - s:.1f}q{k} {s - k:.2f} {s} {s}q{k - s:.2f} {k} {-s} {s}"
            f"q{-k} {k - s:.2f} {-s} {-s}q{s - k:.2f} {-k} {s} {-s}z")


def _spread(boxes, fixed):
    """Moves the constellations apart until none overlaps another, the home star or the frame. boxes are dicts with
    x, y (the centre) and the box's reach around it (left, top, right, bottom); each is pulled gently back to where
    it wants to be, so the map keeps its shape. Deterministic: the same list always gives the same map."""
    def rect(b):
        return (b["x"] - b["l"], b["y"] - b["t"], b["x"] + b["r"], b["y"] + b["b"])

    for _ in range(240):
        moved = False
        for i, a in enumerate(boxes):
            for other in boxes[i + 1:] + fixed:
                ax0, ay0, ax1, ay1 = rect(a)
                bx0, by0, bx1, by1 = other if isinstance(other, tuple) else rect(other)
                ox = min(ax1, bx1) - max(ax0, bx0) + 10
                oy = min(ay1, by1) - max(ay0, by0) + 10
                if ox <= 0 or oy <= 0:
                    continue
                moved = True
                share = 1.0 if isinstance(other, tuple) else 0.5
                if ox < oy:
                    d = ox * (1 if (ax0 + ax1) >= (bx0 + bx1) else -1)
                    a["x"] += d * share
                    if share < 1:
                        other["x"] -= d * share
                else:
                    d = oy * (1 if (ay0 + ay1) >= (by0 + by1) else -1)
                    a["y"] += d * share
                    if share < 1:
                        other["y"] -= d * share
        for b in boxes:
            b["x"] += (b["ax"] - b["x"]) * 0.04
            b["y"] += (b["ay"] - b["y"]) * 0.04
            x0, y0, x1, y1 = FRAME
            b["x"] = min(max(b["x"], x0 + b["l"]), x1 - b["r"])
            b["y"] = min(max(b["y"], y0 + b["t"]), y1 - b["b"])
        if not moved:
            break


@lru_cache(maxsize=256)
def _world_chart(items):
    counts = dict((code, n) for code, n, _ in items)
    names = {code: name for code, _, name in items}
    total = sum(counts.values())
    # One star per university, as on the الرواد chart. The more stars, the closer they sit, so the homepage's 290
    # fit; a short list (a plan) is drawn at the الرواد chart's own spacing.
    gap = min(23.0, max(9.5, 23 * math.sqrt(30 / total)))
    size = round(min(8.0, max(3.6, gap * 0.36)), 2)
    spare = iter((x, 470) for x in range(120, 1000, 110))
    boxes = []
    for code, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        rng = random.Random(f"{code}{n}")
        # A sunflower spiral, shaken a little so a big cluster doesn't show the spiral's pattern, and a little wider
        # than tall, like the map itself.
        offsets = [(dx * 1.12 + rng.uniform(-0.28, 0.28) * gap, dy * 0.88 + rng.uniform(-0.28, 0.28) * gap)
                   for dx, dy in _spiral(n, gap)] if n > 1 else [(0.0, 0.0)]
        reach = max([math.hypot(dx, dy) for dx, dy in offsets] + [0]) + size
        half_label = len(names[code]) * CHAR_W / 2
        ax, ay = WORLD_AT.get(code) or next(spare)
        boxes.append({"code": code, "n": n, "offsets": offsets, "reach": reach, "ax": ax, "ay": ay, "x": ax, "y": ay,
                      "l": max(reach, half_label), "r": max(reach, half_label), "t": reach,
                      "b": reach + LABEL_GAP + LABEL_H})
    _spread(boxes, [HOME_BOX])

    countries = []
    for b in boxes:
        cx, cy = round(b["x"], 1), round(b["y"], 1)
        points = [(cx + dx, cy + dy) for dx, dy in b["offsets"]]
        (hx, hy), angle = HOME, math.atan2(cy - HOME[1], cx - HOME[0])
        ex, ey = cx - math.cos(angle) * (b["reach"] + 8), cy - math.sin(angle) * (b["reach"] + 8)
        mx, my = (hx + ex) / 2, min(hy, ey) - 0.18 * math.dist((hx, hy), (ex, ey))
        countries.append({
            "code": b["code"], "name_ar": names[b["code"]], "count": b["n"], "x": cx, "y": cy,
            "stars": [(round(x, 1), round(y, 1)) for x, y in points],
            "stars_d": "".join(_star_d(x, y, size) for x, y in points),
            "lines_d": "".join(f"M{a[0]:.1f} {a[1]:.1f}L{c[0]:.1f} {c[1]:.1f}" for a, c in _tree(points)),
            "label_y": round(cy + b["reach"] + LABEL_GAP + 14, 1),
            "path": f"M{hx} {hy} Q{mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}",
        })
    return {"countries": countries, "home": HOME, "w": CHART_W, "h": CHART_H, "star": size}


def world_chart(counts, names):
    """The map for any set of universities (the homepage's «إلى أين؟», the explorer's map view, «خطتي»): drawn like
    the الرواد chart (decision 084), one four-point star per university, one constellation per country under its
    name, and a path of light from home to the country in focus. counts = {code: n}; names = {code: Arabic name}."""
    if not counts:
        return None
    return _world_chart(tuple(sorted((code, n, names[code]) for code, n in counts.items())))
