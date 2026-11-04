"""List every Arabic text still needing English, by group. Writes worklists to the scratchpad."""
import ast, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1])
AR = re.compile(r"[\u0600-\u06FF]")

# 1. templates: _("...") / _f("...")
tpl = set()
CALL = re.compile(r"""\b_f?\(\s*(?:"([^"]*)"|'([^']*)')""", re.S)
for p in (ROOT / "app/templates").rglob("*.html"):
    for a, b in CALL.findall(p.read_text(encoding="utf-8")):
        tpl.add(a or b)
# Arabic string literals inside {{ }} / {% %} (shown through finalize)
EXPR = re.compile(r"\{\{.*?\}\}|\{%.*?%\}", re.S)
LIT = re.compile(r"""(?:"([^"]*[\u0600-\u06FF][^"]*)"|'([^']*[\u0600-\u06FF][^']*)')""")
for p in (ROOT / "app/templates").rglob("*.html"):
    src = re.sub(r"\{#.*?#\}", "", p.read_text(encoding="utf-8"), flags=re.S)
    for e in EXPR.findall(src):
        for a, b in LIT.findall(e):
            tpl.add(a or b)

# 2. python: tr()/tf() literals + the Arabic constants shown on pages
py = set()
SKIP = {"ARABIC_MONTHS", "ARABIC_PREFIXES", "SYNONYMS", "UNIVERSITIES_AR", "PROGRAMS_AR", "FIELDS_AR", "COUNTRIES_AR", "RESULTS_AR"}
for name in ("main.py", "universities.py", "search.py"):
    tree = ast.parse((ROOT / "app" / name).read_text(encoding="utf-8"))
    skip_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in SKIP:
            for sub in ast.walk(node):
                skip_nodes.add(id(sub))
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)) and ast.get_docstring(node):
            skip_nodes.add(id(node.body[0].value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and AR.search(node.value) and id(node) not in skip_nodes:
            py.add(node.value)
py = {s for s in py if s not in ("أ", "إ", "آ", "ة", "ى", "ا", "ه", "ي", "ال")}
py.discard("آخر موعد للتقديم") if False else None


# 3. data
def walk(o, key=None):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, k)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)
    elif isinstance(o, str) and AR.search(o):
        yield key, o


NOT_SHOWN = {"quote", "aliases", "evidence", "note_for_owner"}
top = {}
for p in sorted((ROOT / "data").glob("*.json")):
    if p.name in ("university_names_ar.json", "universities.json"):
        continue
    for k, s in walk(json.loads(p.read_text(encoding="utf-8"))):
        top.setdefault(s, set()).add(f"{p.name}:{k}")

# universities.json: fields and majors have name_en; what else?
guide = json.loads((ROOT / "data/universities.json").read_text(encoding="utf-8"))
names = set()
for f in guide["fields"]:
    names.add(f["name_ar"])
    for m in f["majors"]:
        names.add(m["name_ar"])
for k, s in walk(guide):
    if s not in names:
        top.setdefault(s, set()).add(f"universities.json:{k}")

uni = {}
for p in sorted((ROOT / "data/university_details").glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    for k, s in walk(d):
        uni.setdefault(s, set()).add(k)

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tpl.json").write_text(json.dumps(sorted(tpl), ensure_ascii=False, indent=0), encoding="utf-8")
(OUT / "py.json").write_text(json.dumps(sorted(py - tpl), ensure_ascii=False, indent=0), encoding="utf-8")
(OUT / "top.json").write_text(json.dumps({s: sorted(v) for s, v in top.items()}, ensure_ascii=False, indent=0), encoding="utf-8")
(OUT / "uni.json").write_text(json.dumps({s: sorted(v) for s, v in uni.items()}, ensure_ascii=False, indent=0), encoding="utf-8")
print("templates", len(tpl), "python", len(py - tpl), "top data", len(top), "university", len(uni))
