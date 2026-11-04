"""Save (or compare) the HTML of every Arabic page, to prove the English work leaves Arabic pages unchanged.
usage: snapshot.py save|compare <folder>"""
import difflib, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)
xml = client.get("/sitemap.xml").text
urls = [u.replace("https://wadihguide.com", "") for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
urls = [u for u in urls if not u.startswith("/en")]
urls += ["/my-list", "/my-list?partial=1&ids=mit,harvard-university,stanford-university", "/search", "/search?q=" + "منحة",
         "/search?q=duolingo", "/search?q=zzzzqq", "/nope-404", "/grades/nope",
         "/universities?track=arruaad", "/universities?track=emdad", "/universities?track=waaid", "/universities?track=rnd",
         "/universities?q=" + "هندسة", "/universities?q=computer", "/universities?q=harvard", "/universities?country=US",
         "/universities?country=DE", "/universities?lang=other", "/universities?lang=english", "/universities?q=" + "ألمانيا",
         "/universities?track=emdad&field=" + "1", "/universities?track=arruaad&partial=1", "/universities?q=zzzz",
         "/api/search?q=" + "منحة", "/api/suggestions", "/api/universities", "/robots.txt"]


def clean(t):
    t = re.sub(r"\?v=[0-9a-f]{8}", "?v=X", t)
    # the additions the English feature makes on purpose
    t = re.sub(r'\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+">', "", t)
    t = re.sub(r"\s*<a class=\"lang-toggle\".*?</a>", "", t, flags=re.S)
    return t


def key(u):
    return hashlib.sha1(u.encode()).hexdigest()[:16] + ".txt"


mode, folder = sys.argv[1], Path(sys.argv[2])
folder.mkdir(parents=True, exist_ok=True)
if mode == "save":
    manifest = {}
    for u in urls:
        r = client.get(u)
        (folder / key(u)).write_text(clean(r.text), encoding="utf-8", newline="\n")
        manifest[u] = r.status_code
    (folder / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=0), encoding="utf-8")
    print("saved", len(urls), "pages; statuses:", sorted(set(manifest.values())))
else:
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    diffs = 0
    for u, status in manifest.items():
        r = client.get(u)
        strip = lambda x: "\n".join(l for l in x.splitlines() if l.strip())  # noqa: E731
        old = strip((folder / key(u)).read_text(encoding="utf-8"))
        new = strip(clean(r.text))
        if r.status_code != status or old != new:
            diffs += 1
            if diffs <= 12:
                print("DIFF", u, status, r.status_code)
                for line in list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0))[:14]:
                    print("   ", line[:220])
    print(f"compared {len(manifest)} pages, {diffs} differ")
