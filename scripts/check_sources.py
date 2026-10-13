"""Is every university fact still on the official page it cites? (decision 059)

For each data/university_details/<id>.json (drafts included), fetches every cited page once and
checks that what the site shows is on it: English scores near the test's name, the application
fee, each date (day + month), and the Saudi-certificate quote. Prints what it couldn't find and
which pages didn't open. A report, never a CI failure: a miss means "open the page and read it",
not "the fact is wrong" (tables, PDFs and pages built with JavaScript often hide the text).

Run from the repo root:

    .venv\\Scripts\\python.exe scripts\\check_sources.py                 (all universities)
    .venv\\Scripts\\python.exe scripts\\check_sources.py stanford-university mit

Uses curl (like scripts/check_quote.py) and pdftotext for PDFs if installed. Reads only; the
pages are cached in your temp folder for a day so a second run is fast.
"""

import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).parent.parent
CACHE = Path(tempfile.gettempdir()) / "wadih-sources"
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august",
          "september", "october", "november", "december"]
LABELS = {"ielts": ["ielts"], "toefl_ibt": ["toefl"], "duolingo": ["duolingo", "det "]}


def page_text(url):
    """The page as lower-case plain text, or None if it didn't open."""
    CACHE.mkdir(exist_ok=True)
    cached = CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".txt")
    if cached.exists() and time.time() - cached.stat().st_mtime < 86400:
        text = cached.read_text(encoding="utf-8")
        return text or None
    try:
        body = subprocess.run(["curl", "-sSL", "--fail", "-m", "40", "-A", "Mozilla/5.0", url],
                              capture_output=True, check=True).stdout
        if body[:5] == b"%PDF-":
            text = subprocess.run(["pdftotext", "-", "-"], input=body, capture_output=True).stdout.decode("utf-8", "ignore")
        else:
            text = re.sub(r"(?s)<(script|style).*?</\1>", " ", body.decode("utf-8", "ignore"))
            text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        text = re.sub(r"\s+", " ", text).replace("’", "'").lower()
    except Exception:  # 403, timeout, DNS, no pdftotext: the page didn't open
        text = ""
    cached.write_text(text, encoding="utf-8")
    return text or None


def forms(value):
    """6 → {"6", "6.0"}; 6.5 → {"6.5"}."""
    v = float(value)
    return {f"{v:g}", str(value)} | ({f"{int(v)}", f"{int(v)}.0"} if v == int(v) else set())


def near(text, labels, value, window=300):
    for m in re.finditer("|".join(map(re.escape, labels)), text):
        part = text[max(0, m.start() - window): m.end() + window]
        if any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d]|\.\d)", part) for f in forms(value)):
            return True
    return False


def has_date(text, iso):
    _, month, day = iso.split("-")
    name, d, m = MONTHS[int(month) - 1][:3], str(int(day)), str(int(month))
    patterns = [rf"{name}[a-z]*\.?\s+{d}(?!\d)", rf"{name}[a-z]*\.?\s+\d{{1,2}}\s*[-–]\s*{d}(?!\d)", rf"(?<!\d){d}(st|nd|rd|th)?\s+(of\s+)?{name}", rf"(?<!\d)0?{m}/0?{d}(?!\d)"]
    return any(re.search(p, text) for p in patterns)


def facts(d):
    """(what, url, check) for everything the university page shows as a number, date or quote."""
    english = d.get("english") or {}
    for test in ("ielts", "toefl_ibt", "duolingo"):
        item = english.get(test) or {}
        for key in ("min", "recommended"):
            if item.get(key) is not None:
                url = item.get(f"{key}_source_url") or item.get("source_url")
                yield f"{test} {key} {item[key]}", url, lambda t, v=item[key], test=test: near(t, LABELS[test], v)
    fee = d.get("application_fee") or {}
    if fee.get("fee_usd"):
        yield f"fee ${fee['fee_usd']}", fee["source_url"], lambda t, v=fee["fee_usd"]: f"${v}" in t or near(t, ["fee"], v, 150)
    for x in d.get("dates") or []:
        if x.get("date") and not x.get("reference_only"):
            yield f"date {x['date']} ({x.get('round_ar') or x['event_ar']})", x["source_url"], lambda t, v=x["date"]: has_date(t, v)
    cert = d.get("saudi_certificate") or {}
    if cert.get("quote"):
        yield "Saudi certificate quote", cert["source_url"], lambda t, q=cert["quote"]: re.sub(r"\s+", " ", q).lower()[:100] in t


def main(ids):
    files = sorted((ROOT / "data" / "university_details").glob("*.json"))
    files = [f for f in files if not ids or f.stem in ids]
    todo = [(f.stem, *fact) for f in files for fact in facts(json.loads(f.read_text(encoding="utf-8")))]
    urls = sorted({url for _, _, url, _ in todo if url})
    with ThreadPoolExecutor(8) as pool:
        pages = dict(zip(urls, pool.map(page_text, urls)))
    missing, closed = [], set()
    for uid, what, url, check in todo:
        text = pages.get(url)
        if text is None:
            closed.add((uid, url))
        elif not check(text):
            missing.append((uid, what, url))
    print(f"{len(files)} universities, {len(todo)} facts, {len(urls)} pages.")
    print(f"Found on the cited page: {len(todo) - len(missing) - sum(1 for t in todo if pages.get(t[2]) is None)}")
    print(f"\nNot found on the page ({len(missing)}): open it and read it.")
    for uid, what, url in missing:
        print(f"  {uid:45} {what}\n      {url}")
    print(f"\nPages that didn't open ({len(closed)}): check them in a browser.")
    for uid, url in sorted(closed):
        print(f"  {uid:45} {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
