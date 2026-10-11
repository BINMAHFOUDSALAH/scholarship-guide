"""The universities explorer: data loading and search.

Data comes from data/universities.json (extracted from the Ministry's official guide by
scripts/extract_universities.py), data/university_names_ar.json (our Arabic translations of the
names), data/countries.json, and data/university_details/<id>.json (requirements researched from
each university's own official pages).
"""

import json
import re
import unicodedata
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

TRACKS = {
    "arruaad": {"name_ar": "مسار الرواد", "short_ar": "الرواد"},
    "emdad": {"name_ar": "مسار إمداد", "short_ar": "إمداد"},
    "rnd": {"name_ar": "مسار البحث والتطوير", "short_ar": "البحث والتطوير"},
}
SAT_POLICY_AR = {
    "required": "مطلوب",
    "optional": "اختياري",
    "not_considered": "لا يُنظر فيه",
    "not_applicable": "لا ينطبق",
    "unknown": "غير منشور",
}

ARABIC_DIACRITICS = re.compile(r"[ً-ْـ]")


def normalize(text):
    """Make search forgiving: case, accents, Arabic letter variants (أ/إ/آ → ا, ة → ه, ى → ي)."""
    # Letter variants first: decomposing «أ» would otherwise leave a separate hamza mark behind.
    text = (text or "").translate(str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}))
    # Then drop accents (é → e) and Arabic short vowels, which are all combining marks.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = ARABIC_DIACRITICS.sub("", text)
    text = re.sub(r"[^\w؀-ۿ]+", " ", text.casefold())
    return re.sub(r"\s+", " ", text).strip()


def _load(name, default=None):
    path = DATA_DIR / name
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


class Explorer:
    def __init__(self):
        guide = _load("universities.json")
        self.source = guide["source"]
        names_ar = _load("university_names_ar.json", {})
        self.countries = {k: v for k, v in _load("countries.json").items() if not k.startswith("_")}

        self.fields = {(f["track"], f["id"]): f for f in guide["fields"]}
        self.universities = {}
        for u in guide["universities"]:
            u = dict(u)
            u["name_ar"] = names_ar.get(u["id"])
            u["country_info"] = self.countries[u["country"]]
            u["search_key"] = normalize(f"{u['name_en']} {u['name_ar'] or ''}")
            self.universities[u["id"]] = u

        self.details = {}
        for path in sorted((DATA_DIR / "university_details").glob("*.json")):
            d = json.loads(path.read_text(encoding="utf-8"))
            if d.get("id") in self.universities:
                self.details[d["id"]] = d

        # Programs with their own list of target universities (e.g. SDAIA's AI scholarship), for the filter.
        self.target_programs = {}
        self.targets_of = {}
        for path in _load("paths.json", []):
            ids = {t["id"] for t in path.get("target_universities", []) if t.get("id")}
            if ids:
                self.target_programs[path["id"]] = {"label_ar": path.get("target_label_ar") or path["name_ar"], "ids": ids}
                for uid in ids:
                    self.targets_of.setdefault(uid, []).append(path["id"])

        # Every major once per (track, field), with a search key in both languages.
        self.majors = []
        for (track, fid), f in self.fields.items():
            for m in f["majors"]:
                self.majors.append({**m, "track": track, "field": fid,
                                    "key": normalize(f"{m['name_ar']} {m['name_en']}")})

    # ---------- lookups ----------

    def listings(self, track, field=None):
        """[(listing, university)] for one list, by rank."""
        rows = [(l, u) for u in self.universities.values() for l in u["listings"]
                if l["track"] == track and l["field"] == field]
        return sorted(rows, key=lambda r: r[0]["rank"])

    def field(self, track, fid):
        return self.fields.get((track, fid))

    def major_options(self):
        """Unique major names for the search suggestions (Arabic first)."""
        seen, out = set(), []
        for m in sorted(self.majors, key=lambda m: m["name_ar"]):
            if m["name_ar"] not in seen:
                seen.add(m["name_ar"])
                out.append(m)
        return out

    def field_options(self, track):
        return sorted((f for (t, _), f in self.fields.items() if t == track), key=lambda f: f["name_ar"])

    def country_options(self):
        used = {u["country"] for u in self.universities.values()}
        return sorted(((c, self.countries[c]) for c in used), key=lambda kv: kv[1]["name_ar"])

    # ---------- search ----------

    def matching_majors(self, q):
        nq = normalize(q)
        if not nq:
            return []
        exact = [m for m in self.majors if nq in (normalize(m["name_ar"]), normalize(m["name_en"]))]
        return exact or [m for m in self.majors if nq in m["key"]]

    def _keep(self, u, country, language, target=""):
        if target and u["id"] not in self.target_programs[target]["ids"]:
            return False
        if country and u["country"] != country:
            return False
        if language == "english" and not u["country_info"]["english"]:
            return False
        if language == "other" and u["country_info"]["english"]:
            return False
        return True

    def search(self, q="", track="", field="", country="", language="", target=""):
        """Return a dict describing what to show: a mode and sections of rows.

        - major mode: q names a major → الرواد (all majors) + the ranked list of the major's field
          in إمداد (and البحث والتطوير when asked for).
        - name mode: q matches university names → those universities with all their listings.
        - browse mode: no q → one list (الرواد, or a field in إمداد / البحث والتطوير).
        """
        q = (q or "").strip()
        track = track if track in TRACKS else ""
        target = target if target in self.target_programs else ""
        keep = lambda u: self._keep(u, country, language, target)  # noqa: E731
        result = {"q": q, "track": track, "field": field, "country": country, "language": language,
                  "target": target, "mode": "browse", "sections": [], "majors": []}

        majors = self.matching_majors(q) if q else []
        name_hits = [u for u in self.universities.values() if q and normalize(q) in u["search_key"]]

        if majors and (not name_hits or any(normalize(q) in (normalize(m["name_ar"]), normalize(m["name_en"])) for m in majors)):
            result["mode"] = "major"
            result["majors"] = majors
            if track in ("", "arruaad"):
                rows = [(l, u) for l, u in self.listings("arruaad") if keep(u)]
                result["sections"].append({"track": "arruaad", "field": None, "rows": rows,
                                           "note_ar": "الرواد يشمل كل التخصصات، فهذه الجامعات الثلاثون كلها متاحة لتخصصك."})
            for t in ("emdad", "rnd"):
                if track not in ("", t) or (t == "rnd" and track != "rnd"):
                    continue
                for fid in dict.fromkeys(m["field"] for m in majors if m["track"] == t):
                    names = [m for m in majors if m["track"] == t and m["field"] == fid]
                    rows = [(l, u) for l, u in self.listings(t, fid) if keep(u)]
                    result["sections"].append({"track": t, "field": self.field(t, fid), "rows": rows,
                                               "matched_majors": names})
            return result

        if q:
            result["mode"] = "name"
            rows = [u for u in sorted(name_hits, key=lambda u: u["name_en"].lower()) if keep(u)
                    and (not track or any(l["track"] == track for l in u["listings"]))]
            result["sections"].append({"track": None, "field": None, "universities": rows})
            if not rows and majors:
                result["majors"] = majors
            return result

        # Browse.
        if track in ("emdad", "rnd") and self.field(track, field):
            rows = [(l, u) for l, u in self.listings(track, field) if keep(u)]
            result["sections"].append({"track": track, "field": self.field(track, field), "rows": rows})
        elif track in ("emdad", "rnd"):
            rows = [u for u in sorted(self.universities.values(), key=lambda u: u["name_en"].lower())
                    if keep(u) and any(l["track"] == track for l in u["listings"])]
            result["sections"].append({"track": track, "field": None, "universities": rows})
        else:
            rows = [(l, u) for l, u in self.listings("arruaad") if keep(u)]
            result["sections"].append({"track": "arruaad", "field": None, "rows": rows,
                                       "note_ar": "الرواد يشمل كل التخصصات."})
        return result

    # ---------- one university ----------

    def next_deadline(self, uid, today=None):
        """The next upcoming dated item for a university (from its researched requirements), or None."""
        from datetime import date as _date
        today = today or _date.today().isoformat()
        dates = [d for d in (self.details.get(uid) or {}).get("dates") or [] if d.get("date") and d["date"] >= today]
        return min(dates, key=lambda d: d["date"]) if dates else None

    def profile(self, uid):
        u = self.universities.get(uid)
        if u is None:
            return None
        by_track = {}
        for l in sorted(u["listings"], key=lambda l: l["rank"]):
            by_track.setdefault(l["track"], []).append({**l, "field_info": self.field(l["track"], l["field"])})
        details = self.details.get(uid)
        # Dated items in order; items the university hasn't dated yet go last.
        dates = sorted((details or {}).get("dates") or [], key=lambda d: (d.get("date") is None, d.get("date") or ""))
        return {"university": u, "by_track": by_track, "details": details, "dates": dates}

    def api(self):
        """Everything as plain data, for /api/universities."""
        return {
            "source": self.source,
            "fields": list(self.fields.values()),
            "universities": [
                {k: v for k, v in u.items() if k not in ("search_key", "country_info")}
                for u in self.universities.values()
            ],
        }
