"""List every checked fact on واضح by the date we last read its official source, oldest first.

A report, not a test: it never fails CI, so an aging fact can't block a deploy.
Run from the repo root:

    .venv\\Scripts\\python.exe scripts\\stale_facts.py                       # as of today, flag > 90 days
    .venv\\Scripts\\python.exe scripts\\stale_facts.py --as-of 2026-12-09    # as of launch day
    .venv\\Scripts\\python.exe scripts\\stale_facts.py --days 30 --all       # also list the fresh ones

Re-check a flagged fact against its source, update its date in data/ or content/, and run it again.
The data names its check date in four ways (last_checked, read_on, checked, retrieved); all are read here.
Logos aren't facts, so their dates are left out.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import frontmatter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def collect():
    """Every checked item as a dict: where it lives, what it is, when it was checked, and its source."""
    items = []

    def add(where, label, checked, url=None, reviewed=None):
        items.append({"where": where, "label": label, "checked": checked, "url": url, "reviewed": reviewed})

    for path in load("paths.json"):
        where = f"data/paths.json › {path['id']}"
        for track in path["tracks"]:
            add(where, f"track status: {track.get('id') or track['name_ar']}", track["last_checked"],
                track.get("status_source"))
            for fact in track.get("facts", []):
                add(where, f"fact: {fact['id']}", fact["last_checked"],
                    (fact["sources"] or [{}])[0].get("url"), fact["owner_reviewed"])
        for fact in path.get("facts", []):
            add(where, f"fact: {fact['id']}", fact["last_checked"],
                (fact["sources"] or [{}])[0].get("url"), fact["owner_reviewed"])
        if "targets_source" in path:
            source = path["targets_source"]
            add(where, "target universities list", source["retrieved"], source["url"])

    quote = load("featured_quote.json")
    add("data/featured_quote.json", "featured quote", quote["last_checked"], quote.get("source_url"))

    guide = load("universities.json")["source"]
    add("data/universities.json", "universities guide (PDF)", guide["retrieved"], guide["url"])

    waaid = load("waaid_programs.json")
    add("data/waaid_programs.json", "latest واعد programs", waaid["checked"], waaid["source_url"])

    tracks = load("school_tracks.json")["source"]
    add("data/school_tracks.json", "school tracks", tracks["read_on"], tracks["url"])

    for row in load("test_needs.json")["rows"]:
        if "read_on" in row:  # the computed row has no date of its own
            add("data/test_needs.json", f"row: {row['id']}", row["read_on"], row["source"]["url"])

    apply_year = load("apply_year.json")
    for row in apply_year["rows"]:
        for i, fact in enumerate(row.get("facts", []), 1):
            if "read_on" in fact:
                add("data/apply_year.json", f"{row['id']} fact {i}", fact["read_on"],
                    (fact.get("sources") or [{}])[0].get("url"))
    scholarship = apply_year["scholarship"]
    add("data/apply_year.json", "scholarship rule", scholarship["read_on"], scholarship["rule_source"])

    for file in sorted((DATA / "university_details").glob("*.json")):
        detail = json.loads(file.read_text(encoding="utf-8"))
        add("data/university_details", detail["id"], detail["checked"], detail.get("admissions_url"))

    for file in sorted((ROOT / "content").glob("*/*.md")):
        meta = frontmatter.load(file).metadata
        if "last_checked" in meta:
            add(f"content/{file.parent.name}/{file.name}", "page", str(meta["last_checked"]),
                None, meta.get("owner_reviewed"))

    for item in items:
        item["checked"] = date.fromisoformat(item["checked"])
    return sorted(items, key=lambda i: (i["checked"], i["where"], i["label"]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(),
                        help="count ages as of this date (YYYY-MM-DD), e.g. launch day; default today")
    parser.add_argument("--days", type=int, default=90, help="flag items older than this; default 90")
    parser.add_argument("--all", action="store_true", help="also list the items that aren't stale")
    args = parser.parse_args(argv)

    items = collect()
    stale = [i for i in items if (args.as_of - i["checked"]).days > args.days]
    shown = items if args.all else stale

    print(f"As of {args.as_of}: {len(stale)} of {len(items)} checked items are over {args.days} days old.")
    if items:
        print(f"Oldest check: {items[0]['checked']}  ·  newest: {items[-1]['checked']}")
    for item in shown:
        age = (args.as_of - item["checked"]).days
        flag = "STALE" if item in stale else "     "
        review = "  [not owner-reviewed]" if item["reviewed"] is False else ""
        print(f"{flag} {item['checked']} ({age:>3}d)  {item['where']} · {item['label']}{review}")
        if item["url"] and item in stale:
            print(f"{'':28}{item['url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
