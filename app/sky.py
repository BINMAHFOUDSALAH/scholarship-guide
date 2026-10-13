"""The sky drawings (decision 060): star fields and the الرواد star chart.

Pure layout: positions for decorative SVG, computed once at startup. Nothing here is a fact
shown to students; the chart's universities, ranks and countries come from the Explorer
(the Ministry's guide), and only their places on the drawing are decided here.
"""

import math
import random


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
