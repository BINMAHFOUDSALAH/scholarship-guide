"""Check that an official page really contains the quotes a research agent gave us.

Fetches the page, strips the HTML (or reads the PDF text), and looks for each quote,
ignoring case and whitespace. Use it before saving any researched fact (decision 054).
Run from the repo root:

    .venv\\Scripts\\python.exe scripts\\check_quote.py URL "exact quote" ["another quote" ...]

Prints FOUND or MISSING per quote; exits 1 if any is missing or the page won't open.
Reads only: nothing is written to disk.
"""

import html
import re
import subprocess
import sys


def page_text(url):
    """Fetch with curl (some university sites reset Python's own HTTP client)."""
    body = subprocess.run(["curl", "-sSL", "--fail", "-m", "40", "-A", "Mozilla/5.0", url],
                          capture_output=True, check=True).stdout
    if body[:5] == b"%PDF-":  # needs pdftotext (poppler)
        return subprocess.run(["pdftotext", "-", "-"], input=body, capture_output=True).stdout.decode("utf-8", "ignore")
    text = body.decode("utf-8", "ignore")
    text = re.sub(r"(?s)<(script|style).*?</\1>", " ", text)
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def normalize(text):
    return re.sub(r"\s+", " ", text).replace("\u2019", "'").strip().lower()


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    url, quotes = argv[0], argv[1:]
    try:
        text = normalize(page_text(url))
    except Exception as error:  # 403, timeout, DNS: the fact can't be confirmed
        print(f"PAGE FAILED | {url} | {error}")
        return 1
    missing = 0
    for quote in quotes:
        found = normalize(quote) in text
        missing += not found
        print(f"{'FOUND  ' if found else 'MISSING'} | {quote[:80]}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
