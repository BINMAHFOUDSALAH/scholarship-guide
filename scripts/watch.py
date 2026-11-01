"""What needs updating on the site? Step 1 of the /update-site skill (decision 064).

A report, never a failing check: it lists what to act on and changes nothing in the site or its data.
The skill (.claude/skills/update-site/SKILL.md) then reads each official page and makes the changes,
because facts are published only after reading their official source.

Run from the repo root:

    .venv\\Scripts\\python.exe scripts\\watch.py                     # everything, as of today
    .venv\\Scripts\\python.exe scripts\\watch.py --offline           # only the checks that need no internet
    .venv\\Scripts\\python.exe scripts\\watch.py --as-of 2026-11-16  # as if it were that day

What it checks:
1. New on official pages: واعد announcements on the Ministry's page that aren't in data/waaid_programs.json,
   and the pages in scripts/watch_pages.json whose watched phrase disappeared (or whose alert phrase appeared).
2. Past: open tracks past their `status_until`, open tracks with no deadline not re-checked in 14 days,
   universities whose every date has passed, واعد programs closed long enough to remove.
3. Bugs: every page in the live sitemap, the live /waaid page showing every program in the data
   (a failed deploy), and official links that answer 404 or 410.
4. Old facts: anything scripts/stale_facts.py finds older than 90 days.
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import frontmatter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stale_facts  # noqa: E402  (same folder)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RECHECK_OPEN_DAYS = 14  # an open track with no deadline: re-check it this often
STALE_DAYS = 90  # same threshold as scripts/stale_facts.py
CLOSING_SOON_DAYS = 3
# A closed واعد program leaves the homepage board after RECENT_DAYS in app/main.py (a test keeps them equal);
# from then on it's only history, so the skill removes it from the data.
REMOVE_WAAID_AFTER_DAYS = 120
SKIP_LINK_HOSTS = ("x.com", "twitter.com")  # refuse every script; their posts are checked by hand

SECTIONS = {
    "new": "New on official pages",
    "past": "Past or due for a re-check",
    "bug": "Bugs",
    "stale": f"Old facts (last read {STALE_DAYS}+ days ago)",
}

# Arabic text on the Ministry's pages has invisible characters inside words and numbers («202​6م»),
# and sometimes Arabic-Indic digits, so text is cleaned before any matching.
INVISIBLE = dict.fromkeys(map(ord, "​‌‍‎‏⁠﻿\xad"), None)
DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
MONTHS_AR = {"يناير": 1, "فبراير": 2, "مارس": 3, "أبريل": 4, "ابريل": 4, "إبريل": 4, "مايو": 5, "يونيو": 6,
             "يونيه": 6, "يوليو": 7, "يوليه": 7, "أغسطس": 8, "اغسطس": 8, "سبتمبر": 9, "أكتوبر": 10,
             "اكتوبر": 10, "نوفمبر": 11, "ديسمبر": 12}
_MONTH = "|".join(MONTHS_AR)
# «من 1 نوفمبر 2026م إلى 10 نوفمبر 2026م», «من 3 أغسطس إلى 17 أغسطس 2026», «من 30 أغسطس 2026م وحتى 3 سبتمبر 2026م»,
# and once without «من» («25 أكتوبر 2026م إلى 5 نوفمبر 2026م»). A month name on both sides keeps «3.5 من 4» out.
WINDOW = re.compile(rf"(?:من\s*)?(\d{{1,2}})\s*({_MONTH})\s*(\d{{4}})?\s*م?\s*(?:إلى|وحتى|حتى)\s*"
                    rf"(\d{{1,2}})\s*({_MONTH})\s*(\d{{4}})")
ANNOUNCEMENT = "بدء التقديم على برنامج"  # each واعد program on the official page starts with this line
COMPANY = re.compile(r"بالتوظيف\s+(?:في\s+)?(.+?)\s+ضمن\s+مسار\s+واعد")


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def clean(text):
    return text.translate(INVISIBLE).translate(DIGITS)


def page_lines(raw_html):
    """An HTML page as its visible lines of text, cleaned."""
    text = re.sub(r"(?s)<(script|style).*?</\1>", " ", raw_html)
    text = clean(html.unescape(re.sub(r"<[^>]+>", "\n", text)))
    return [line for line in (re.sub(r"\s+", " ", x).strip() for x in text.split("\n")) if line]


def short_date(iso):
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"  # «1 Nov 2026» (no %-d: it doesn't work on Windows)


# ---------------------------------------------------------------- fetching

def fetch(url, read=True, timeout=40, tries=2):
    """(HTTP status or None, the page's text or None). Never raises: a page that doesn't open is a result.
    A page that gives no answer or a server error is tried once more, so one slow moment isn't a to-do."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (wadihguide.com site check)"})
    for attempt in range(tries):
        if attempt:
            time.sleep(5)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                body = response.read().decode("utf-8", "replace") if read else None
                return response.status, body
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:  # timeout, DNS, refused, TLS: it didn't open
            status = None
        if status is not None and status < 500:
            break  # 403, 404…: asking again won't change the answer
    return status, None


def fetch_many(urls, read=False):
    with ThreadPoolExecutor(max_workers=6) as pool:
        return dict(zip(urls, pool.map(lambda u: fetch(u, read=read), urls)))


# ---------------------------------------------------------------- واعد

def parse_window(text):
    """«من 1 نوفمبر 2026م إلى 10 نوفمبر 2026م» → ("2026-11-01", "2026-11-10"), or None."""
    m = WINDOW.search(clean(text))
    if not m:
        return None
    d1, m1, y1, d2, m2, y2 = m.groups()
    m1, m2, y2 = MONTHS_AR[m1], MONTHS_AR[m2], int(y2)
    y1 = int(y1) if y1 else (y2 if m1 <= m2 else y2 - 1)  # «من 3 أغسطس إلى 17 أغسطس 2026»: the year is said once
    try:
        return date(y1, m1, int(d1)).isoformat(), date(y2, m2, int(d2)).isoformat()
    except ValueError:  # «31 نوفمبر»: a typo on the page
        return None


def waaid_announcements(lines):
    """Every program on the official واعد page, in page order (newest first), as
    {"title", "company", "window"}; window is None when the dates couldn't be read."""
    starts = [i for i, line in enumerate(lines) if ANNOUNCEMENT in line]
    found = []
    for n, start in enumerate(starts):
        end = starts[n + 1] - 1 if n + 1 < len(starts) else len(lines)  # the next block's title line is its own
        block = " ".join(lines[start:end])
        company = COMPANY.search(block)
        found.append({"title": lines[start - 1] if start else "", "company": company and company.group(1),
                      "window": parse_window(block)})
    return found


def waaid_items(announcements, programs, today, source_url):
    """Compare the official page with data/waaid_programs.json, window by window (an announcement's dates),
    for windows still open or not open yet. Counting per window survives small wording differences in
    company names; two companies sharing a window still show up as one more program than we have."""
    items = []
    link = f"[official page]({source_url})"
    if not announcements:
        return [item("new", "waaid-page", f"Couldn't read any واعد announcement on the {link}: it may be down, "
                     "blocking scripts, or redesigned. Check it in a browser.")]
    live = [a for a in announcements if a["window"] and a["window"][1] >= today]
    page = Counter(a["window"] for a in live)
    ours = Counter((p["apply_from"], p["apply_to"]) for p in programs if p["apply_to"] >= today)
    for window, count in page.items():
        have = ours.get(window, 0)
        if count > have:
            on_page = [a for a in live if a["window"] == window]
            names = "، ".join(sorted({a["company"] or "?" for a in on_page}))
            titles = "؛ ".join(f"«{a['title']}»" for a in on_page[:12])
            what = (f"a new announcement ({count} program{'s' * (count > 1)})" if not have
                    else f"{count} programs where our data has {have}")
            items.append(item("new", f"waaid:{window[0]}:{window[1]}:{count}",
                              f"واعد, {short_date(window[0])} to {short_date(window[1])}: the {link} lists {what} "
                              f"from {names}: {titles}. Add the missing ones at the top of `data/waaid_programs.json` "
                              f"from the page (requirements, who it's for)."))
    for window, have in ours.items():
        if page.get(window, 0) < have:
            items.append(item("new", f"waaid-gone:{window[0]}:{window[1]}:{page.get(window, 0)}",
                              f"واعد, {short_date(window[0])} to {short_date(window[1])}: our data has {have} "
                              f"program(s) but the {link} now lists {page.get(window, 0)}. Removed, or dates changed? "
                              "Read the page and fix `data/waaid_programs.json`."))
    # A block at the top whose dates couldn't be read (a new wording) would otherwise go unnoticed.
    for a in announcements:
        if a["window"] and a["window"][1] < today:
            break  # from here down, the page lists closed announcements
        if not a["window"]:
            items.append(item("new", f"waaid-unread:{a['title']}",
                              f"واعد: couldn't read the dates of «{a['title']}» ({a['company'] or '?'}) near the top "
                              f"of the {link}. Read it and add it to `data/waaid_programs.json` if it's new."))
    return items


def waaid_closing_soon(programs, today):
    """FYI lines: announcements that close within CLOSING_SOON_DAYS (a reminder worth posting)."""
    soon = date.fromisoformat(today) + timedelta(days=CLOSING_SOON_DAYS)
    windows = {}
    for p in programs:
        if p["apply_from"] <= today <= p["apply_to"] <= soon.isoformat():
            windows.setdefault((p["company_ar"], p["apply_to"]), []).append(p)
    return [f"واعد closes {short_date(end)}: {company} ({len(ps)} program{'s' * (len(ps) > 1)}, "
            f"{sum(p['for_high_school'] for p in ps)} for high school graduates)"
            for (company, end), ps in sorted(windows.items(), key=lambda kv: kv[0][1])]


def waaid_old_items(programs, today):
    """واعد programs whose window closed more than REMOVE_WAAID_AFTER_DAYS ago, one item per announcement."""
    cutoff = (date.fromisoformat(today) - timedelta(days=REMOVE_WAAID_AFTER_DAYS)).isoformat()
    old = {}
    for p in programs:
        if p["apply_to"] < cutoff:
            old.setdefault((p["company_ar"], p["apply_to"]), []).append(p["id"])
    return [item("past", f"waaid-old:{','.join(ids)}",
                 f"واعد: {company} closed {short_date(end)}, over {REMOVE_WAAID_AFTER_DAYS} days ago. Remove its "
                 f"{len(ids)} program(s) from `data/waaid_programs.json` ({', '.join(ids)}).")
            for (company, end), ids in old.items()]


# ---------------------------------------------------------------- deadlines in the data

def deadline_items(paths, details, today):
    items = []
    for path in paths:
        for track in path["tracks"]:
            if track.get("latest_programs"):  # واعد: open/closed comes from its programs' dates
                continue
            tid = track.get("id") or path["id"]
            name = track.get("name_ar") or path["name_ar"]
            until = track.get("status_until")
            if track.get("status") == "open" and until and until < today:
                items.append(item("past", f"track-closed:{tid}:{until}",
                                  f"«{name}» closed on its deadline ({short_date(until)}); the site already shows "
                                  "«أُغلق» with that date, so leave its `status` as it is. Look for the next round on "
                                  f"its official page; when one is announced, update it in `data/paths.json` › "
                                  f"{path['id']}."))
            elif track.get("status") == "open" and not until:
                age = (date.fromisoformat(today) - date.fromisoformat(track["last_checked"])).days
                if age > RECHECK_OPEN_DAYS:
                    source = track.get("status_source")
                    items.append(item("past", f"track-open:{tid}:{track['last_checked']}",
                                      f"«{name}» shows «مفتوح الآن» with no published deadline, last checked "
                                      f"{short_date(track['last_checked'])} ({age} days ago). Still open? Re-check"
                                      f"{f' [its source]({source})' if source else ''} and update `last_checked` "
                                      f"in `data/paths.json` › {path['id']}."))
    for d in details:
        dated = [x["date"] for x in d.get("dates") or [] if x.get("date") and not x.get("reference_only")]
        if dated and max(dated) < today:
            items.append(item("past", f"uni-dates:{d['id']}:{max(dated)}",
                              f"{d['name_en']}: every date has passed (the last was {short_date(max(dated))}). "
                              f"Add the next round's dates to `data/university_details/{d['id']}.json` once the "
                              f"university publishes them ([admissions]({d.get('admissions_url')}))."))
    return items


def stale_items(today):
    as_of = date.fromisoformat(today)
    items = []
    for i in stale_facts.collect():
        if (as_of - i["checked"]).days > STALE_DAYS:
            source = f" ([source]({i['url']}))" if i["url"] else ""
            items.append(item("stale", f"stale:{i['where']}|{i['label']}",
                              f"{i['where']} · {i['label']}: last read {short_date(i['checked'].isoformat())}"
                              f"{source}. Re-read it and update its date."))
    return items


# ---------------------------------------------------------------- watched pages, links, the live site

def matches(phrase, haystack):
    return re.sub(r"\s+", " ", clean(phrase)).lower() in haystack


def page_watch_items(entries, fetcher=fetch):
    """(items, fyi) for scripts/watch_pages.json."""
    items, fyi = [], []
    for e in entries:
        status, body = fetcher(e["url"])
        if body is None:
            line = f"{e['name']}: [the page]({e['url']}) didn't open ({status or 'no answer'})"
            if e.get("often_blocked"):
                fyi.append(line + "; this site often refuses scripts, so check it in a browser now and then.")
            else:
                items.append(item("new", f"page-unread:{e['id']}", line + ". Check it in a browser."))
            continue
        haystack = re.sub(r"\s+", " ", clean(html.unescape(body)) + " " + " ".join(page_lines(body))).lower()
        gone = [p for p in e.get("expect", []) if not matches(p, haystack)]
        new = [p for p in e.get("alert_if", []) if matches(p, haystack)]
        if gone or new:
            why = "; ".join([f"«{p}» is no longer on it" for p in gone] + [f"«{p}» appeared" for p in new])
            items.append(item("new", f"page:{e['id']}:{'|'.join(gone + new)}",
                              f"{e['name']}: [the page]({e['url']}) changed ({why}). {e['then']} Then update the "
                              "phrase in `scripts/watch_pages.json`."))
    return items, fyi


def program_links():
    """Every official link on the site outside the universities explorer (scripts/check_sources.py covers
    that), with where it's cited."""
    found = {}

    def walk(node, where):
        if isinstance(node, dict):
            for value in node.values():
                walk(value, where)
        elif isinstance(node, list):
            for value in node:
                walk(value, where)
        elif isinstance(node, str) and node.startswith(("http://", "https://")):
            found.setdefault(node, where)

    for name in ("paths.json", "waaid_programs.json", "news.json", "featured_quote.json", "test_needs.json",
                 "apply_year.json", "school_tracks.json", "home.json"):
        walk(load(name), f"data/{name}")
    for file in sorted((ROOT / "content").glob("*/*.md")):
        where = f"content/{file.parent.name}/{file.name}"
        page = frontmatter.load(file)
        walk(page.metadata, where)
        for url in re.findall(r"\]\((https?://[^)\s]+)\)", page.content):
            found.setdefault(url, where)
    base = load("site.json")["base_url"].rstrip("/")
    return {u: w for u, w in found.items()
            if not u.split("/")[2].endswith(SKIP_LINK_HOSTS) and not u.startswith(base)}


def link_items(links, results):
    items, other = [], 0
    for url, where in links.items():
        status = results[url][0]
        if status in (404, 410):
            items.append(item("bug", f"link:{url}:{status}",
                              f"Broken official link ({status}): {url}, cited in `{where}`. Find the page's new "
                              "address on the official site and update it."))
        elif status is None or status >= 400:
            other += 1
    return items, other


def live_items(base_url, programs, fetcher=fetch, fetch_all=fetch_many):
    """(items, checked count): every sitemap page answers 200; /waaid shows every program in the data."""
    items = []
    status, sitemap = fetcher(f"{base_url}/sitemap.xml")
    if sitemap is None:
        return [item("bug", "live-down", f"The live site didn't answer: {base_url}/sitemap.xml gave "
                     f"{status or 'no answer'}. Check Render's dashboard (Events, Logs).")], 0
    pages = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    for url, (code, _) in sorted(fetch_all(pages).items()):
        if code != 200:
            items.append(item("bug", f"live:{url}:{code}", f"Live page {url} answered {code or 'nothing'} "
                              "instead of 200."))
    status, page = fetcher(f"{base_url}/waaid")
    missing = [p["id"] for p in programs if page is not None and f'id="{p["id"]}"' not in page]
    if missing:
        items.append(item("bug", f"live-behind:{','.join(missing)}",
                          f"The live /waaid page is missing {len(missing)} program(s) that are in the repo "
                          f"({', '.join(missing)}): the change isn't merged to `main` yet, or the last deploy "
                          "failed (Render → Events)."))
    return items, len(pages)


# ---------------------------------------------------------------- the report

def item(section, key, text):
    return {"section": section, "key": key, "text": text}


def run(today, offline=False):
    """Everything to act on, plus FYI lines and a summary of what was checked."""
    programs = load("waaid_programs.json")
    items, fyi, checked = [], [], []

    details = [json.loads(f.read_text(encoding="utf-8"))
               for f in sorted((DATA / "university_details").glob("*.json"))]
    items += deadline_items(load("paths.json"), details, today)
    items += waaid_old_items(programs["programs"], today)
    items += stale_items(today)
    fyi += waaid_closing_soon(programs["programs"], today)
    checked.append(f"dates in data/paths.json, data/waaid_programs.json and {len(details)} university files")

    if not offline:
        status, page = fetch(programs["source_url"])
        announcements = waaid_announcements(page_lines(page)) if page else []
        items += waaid_items(announcements, programs["programs"], today, programs["source_url"])
        checked.append(f"the واعد page ({len(announcements)} programs listed)")

        entries = json.loads((ROOT / "scripts" / "watch_pages.json").read_text(encoding="utf-8"))["pages"]
        page_items, page_fyi = page_watch_items(entries)
        items += page_items
        fyi += page_fyi
        checked.append(f"{len(entries)} watched official pages")

        links = program_links()
        found, other = link_items(links, fetch_many(list(links)))
        items += found
        checked.append(f"{len(links)} official links")
        if other:
            fyi.append(f"{other} official link(s) didn't open for a script (403, timeout…). Many official sites "
                       "refuse scripts; only 404/410 counts as broken.")

        base = load("site.json")["base_url"].rstrip("/")
        found, count = live_items(base, programs["programs"])
        items += found
        checked.append(f"{count} live pages on {base}")
    return items, fyi, checked


def render(items, fyi, checked, today):
    lines = [f"## Site check, {short_date(today)}", ""]
    if items:
        lines += [f"**To act on: {len(items)}.** Read the official page before changing a fact (CLAUDE.md).", ""]
    else:
        lines += ["**Nothing to act on.**", ""]
    for section, title in SECTIONS.items():
        found = [i for i in items if i["section"] == section]
        if found:
            lines += [f"### {title}", ""] + [f"- {i['text']}" for i in found] + [""]
    if fyi:
        lines += ["### FYI", ""] + [f"- {x}" for x in fyi] + [""]
    lines += [f"Checked: {'; '.join(checked)}."]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(),
                        help="check as if today were this date (YYYY-MM-DD)")
    parser.add_argument("--offline", action="store_true", help="skip the checks that need the internet")
    args = parser.parse_args(argv)

    today = args.as_of.isoformat()
    items, fyi, checked = run(today, offline=args.offline)
    print(render(items, fyi, checked, today))
    return 0


if __name__ == "__main__":
    sys.exit(main())
