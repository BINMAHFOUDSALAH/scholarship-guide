"""List Arabic text still showing on English pages (decision 066), with the pages it appears on.

usage: python scripts/english_leaks.py [--limit N]
Arabic inside an element marked lang="ar" is allowed (official Arabic names, the language switch).
tests/test_english.py runs the same check on every page; this script is for finding what's left.
"""
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

AR = re.compile(r"[؀-ۿ]")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class ArabicFinder(HTMLParser):
    """Collects text (and visible attributes) with Arabic letters that isn't inside lang="ar"."""

    ATTRS = ("aria-label", "title", "alt", "placeholder", "content", "data-summary", "data-default", "label",
             "data-save-name", "value")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # (tag, is_arabic)
        self.found = []
        self.in_script = False

    def arabic_zone(self):
        return any(a for _, a in self.stack)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        is_ar = attrs.get("lang") == "ar"
        if tag == "script":
            self.in_script = True
        inside = self.arabic_zone() or is_ar
        if not inside:
            for name in self.ATTRS:
                value = attrs.get(name) or ""
                if AR.search(value):
                    self.found.append(f"[{tag} {name}] {value.strip()}")
        if tag not in VOID:
            self.stack.append((tag, is_ar))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1][0] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.in_script or self.arabic_zone():
            return
        text = " ".join(data.split())
        if AR.search(text):
            self.found.append(text)


def arabic_outside_lang_ar(html):
    finder = ArabicFinder()
    finder.feed(html)
    return finder.found


def english_urls(client):
    xml = client.get("/sitemap.xml").text
    urls = [u.replace("https://wadihguide.com", "") for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
    urls = [u for u in urls if u.startswith("/en")]
    extra = ["/my-list", "/my-list?partial=1&ids=mit,harvard-university,stanford-university,technical-university-of-munich",
             "/search", "/search?q=ielts", "/search?q=conditional", "/search?q=zzzzqq", "/nope-404", "/grades/nope",
             "/universities?track=arruaad", "/universities?track=emdad", "/universities?track=waaid",
             "/universities?track=rnd", "/universities?q=computer", "/universities?q=harvard",
             "/universities?q=Computer%20Science", "/universities?country=US", "/universities?country=DE",
             "/universities?lang=other", "/universities?lang=english", "/universities?q=germany",
             "/universities?track=emdad&field=1", "/universities?track=rnd&field=1", "/universities?track=arruaad&partial=1",
             "/universities?q=zzzz", "/universities?country=DE&lang=english", "/universities?track=emdad&country=US",
             "/universities?q=harvard&track=rnd"]
    return urls + ["/en" + u for u in extra]


def main():
    from fastapi.testclient import TestClient
    from app.main import app

    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 400
    client = TestClient(app)
    where = defaultdict(set)
    for url in english_urls(client):
        response = client.get(url)
        for text in arabic_outside_lang_ar(response.text):
            where[text].add(url)
    for text, urls in sorted(where.items(), key=lambda kv: -len(kv[1]))[:limit]:
        print(f"{len(urls):4}  {text[:300]}    <- {sorted(urls)[0]}")
    print(f"\n{len(where)} Arabic texts on English pages")


if __name__ == "__main__":
    main()
