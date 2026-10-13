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
from urllib.parse import parse_qsl, urlencode

DATA_DIR = Path(__file__).parent.parent / "data"
STATIC_DIR = Path(__file__).parent / "static"

# In the order a high-school student needs them: the doctorate-only track comes last (decision 038).
TRACKS = {
    "arruaad": {"name_ar": "مسار الرواد", "short_ar": "الرواد"},
    "emdad": {"name_ar": "مسار إمداد", "short_ar": "إمداد"},
    # واعد has no ranked lists: each program names its own institution (data/waaid_programs.json).
    "waaid": {"name_ar": "مسار واعد", "short_ar": "واعد"},
    "rnd": {"name_ar": "مسار البحث والتطوير", "short_ar": "البحث والتطوير"},
}
SAT_POLICY_AR = {
    "required": "مطلوب",
    "optional": "اختياري",
    "not_considered": "لا يُنظر فيه",
    "not_applicable": "لا ينطبق",
    "unknown": "غير منشور",
}
# Application-fee waivers (decision 050): what the university's own page says about waiving its fee.
WAIVER_AR = {
    "accepts_common_app": "تقبل إعفاء Common App",
    "own_waiver": "لها طلب إعفاء خاص بها",
    "domestic_only": "الإعفاء للطلاب الأمريكيين فقط",
    "none": "لا تمنح إعفاءً من الرسوم",
    "not_stated": None,
}
# The country's official language, used by the scholarship's rule on conditional offers. It is not
# the language a program is taught in: many universities in other countries teach in English.
LANGUAGE_AR = {"english": "الإنجليزية", "other": "غير الإنجليزية"}

# The search parameters a results link may carry back from a university page (decision 035).
SEARCH_PARAMS = ("q", "track", "field", "country", "lang")
# What الرواد's list means for a major: it names universities, not majors. Not "available to you":
# admission is still the university's decision (decision 041).
ARRUAAD_NOTE = "قائمة الرواد لا تحدد تخصصات: أي تخصص في هذه الجامعات يدخل في المسار، والقبول تقرره الجامعة."


def count_ar(n, forms):
    """An Arabic count, with the noun in the form Arabic grammar asks for.

    forms = (one, two, 3–10, 11–99, 100s), e.g. ("برنامج واحد", "برنامجان", "برامج", "برنامجًا", "برنامج"):
    1 → «برنامج واحد», 2 → «برنامجان», 5 → «5 برامج», 30 → «30 برنامجًا», 200 → «200 برنامج».
    """
    one, two, few, many, hundreds = forms
    if n == 1:
        return one
    if n == 2:
        return two
    if 3 <= n % 100 <= 10:
        return f"{n} {few}"
    if 11 <= n % 100 <= 99:
        return f"{n} {many}"
    return f"{n} {hundreds}"


UNIVERSITIES_AR = ("جامعة واحدة", "جامعتان", "جامعات", "جامعة", "جامعة")
PROGRAMS_AR = ("برنامج واحد", "برنامجان", "برامج", "برنامجًا", "برنامج")
FIELDS_AR = ("مجال واحد", "مجالان", "مجالات", "مجالًا", "مجال")
COUNTRIES_AR = ("دولة واحدة", "دولتان", "دول", "دولة", "دولة")
RESULTS_AR = ("نتيجة واحدة", "نتيجتان", "نتائج", "نتيجة", "نتيجة")
COUNT_FORMS = {"universities": UNIVERSITIES_AR, "programs": PROGRAMS_AR, "fields": FIELDS_AR,
               "countries": COUNTRIES_AR, "results": RESULTS_AR}

ARABIC_DIACRITICS = re.compile(r"[\u064b-\u0652\u0640]")  # short vowels + tatweel, as escapes (the marks are invisible)


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

        # Official logos (decision 049): only for universities we know, only when the file exists.
        logos = (_load("university_logos.json", {}) or {}).get("logos", {})
        self.logos = {uid: logo for uid, logo in logos.items()
                      if uid in self.universities and (STATIC_DIR / logo["file"]).is_file()}

        self.details = {}
        for path in sorted((DATA_DIR / "university_details").glob("*.json")):
            d = json.loads(path.read_text(encoding="utf-8"))
            if d.get("id") in self.universities:
                self.details[d["id"]] = d

        # main.py plugs in its waaid() here: the latest واعد programs, each marked open or closed today.
        self.waaid = lambda: {"programs": [], "source_url": None}
        self.by_name = {normalize(u["name_en"]): uid for uid, u in self.universities.items()}

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

    def _keep(self, u, country, language):
        if country and u["country"] != country:
            return False
        if language == "english" and not u["country_info"]["english"]:
            return False
        if language == "other" and u["country_info"]["english"]:
            return False
        return True

    def search(self, q="", track="", field="", country="", language=""):
        """Return a dict describing what to show: a mode and sections of rows.

        - major mode: q names a major → الرواد (all majors) + the ranked list of the major's field
          in إمداد (and البحث والتطوير when asked for).
        - name mode: q matches university names → those universities with all their listings.
        - browse mode: no q → one list (الرواد, or a field in إمداد / البحث والتطوير).
        """
        q = (q or "").strip()
        track = track if track in TRACKS else ""
        # A field picked without a track (possible without JavaScript) belongs to إمداد's lists,
        # the ones high-school graduates can use.
        if field and not track and self.field("emdad", field):
            track = "emdad"
        keep = lambda u: self._keep(u, country, language)  # noqa: E731
        result = {"q": q, "track": track, "field": field, "country": country, "language": language,
                  "mode": "browse", "sections": [], "majors": []}

        if track == "waaid":
            result["mode"] = "waaid"
            result["sections"].append({"track": "waaid", "field": None, "waaid": self.waaid_matches(q)})
            return result

        majors = self.matching_majors(q) if q else []
        name_hits = [u for u in self.universities.values() if q and normalize(q) in u["search_key"]]

        if majors and (not name_hits or any(normalize(q) in (normalize(m["name_ar"]), normalize(m["name_en"])) for m in majors)):
            result["mode"] = "major"
            result["majors"] = majors
            if track in ("", "arruaad"):
                rows = [(l, u) for l, u in self.listings("arruaad") if keep(u)]
                # The same 30 for every major, so a compact ranked list here; the field list below is the
                # answer that's specific to this major (decision 041).
                full = urlencode({k: v for k, v in (("track", "arruaad"), ("country", country), ("lang", language)) if v})
                result["sections"].append({"track": "arruaad", "field": None, "rows": rows, "compact": True,
                                           "full_href": "/universities?" + full, "note_ar": ARRUAAD_NOTE})
            for t in ("emdad", "rnd"):
                if track not in ("", t) or (t == "rnd" and track != "rnd"):
                    continue
                for fid in dict.fromkeys(m["field"] for m in majors if m["track"] == t):
                    names = [m for m in majors if m["track"] == t and m["field"] == fid]
                    rows = [(l, u) for l, u in self.listings(t, fid) if keep(u)]
                    field = self.field(t, fid)
                    result["sections"].append({"track": t, "field": field, "rows": rows, "matched_majors": names,
                                               # The guide ranks universities by field, not by major (decision 041).
                                               "note_ar": f"هذا ترتيب مجال «{field['name_ar']}» كله في الدليل، وليس قائمة بتخصص "
                                                          f"«{names[0]['name_ar']}» وحده. تأكد أن الجامعة تدرّس التخصص من موقعها."})
            self._add_waaid(result, q)
            return result

        if q:
            result["mode"] = "name"
            result["country_match"] = self.country_named(q)
            hits = sorted(name_hits, key=lambda u: u["name_en"].lower())
            rows = [u for u in hits if keep(u) and (not track or any(l["track"] == track for l in u["listings"]))]
            section = {"track": None, "field": None, "universities": rows}
            if not rows and hits:
                # The university is on the lists, just not under these filters: say so, never "not found"
                # (decision 041).
                section = {"track": None, "field": None, "universities": hits, "outside_filters": True}
            # A country typed in the box: the country link answers it; no "no university by this name".
            if hits or not result["country_match"]:
                result["sections"].append(section)
            if not rows and majors:
                result["majors"] = majors
            self._add_waaid(result, q)
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
            result["sections"].append({"track": "arruaad", "field": None, "rows": rows, "note_ar": ARRUAAD_NOTE})
            if country or language:
                # A country without a track: every list with matches, not only الرواد (decision 041).
                emdad = [u for u in sorted(self.universities.values(), key=lambda u: u["name_en"].lower())
                         if keep(u) and any(l["track"] == "emdad" for l in u["listings"])]
                if emdad:
                    if not rows:
                        result["sections"].pop()
                    result["sections"].append({"track": "emdad", "field": None, "universities": emdad,
                                               "note_ar": "مرتبة حسب الاسم. اختر مجالًا من «المجال» لترى ترتيبها فيه."})
        return result

    def country_named(self, q):
        """The country code if the search text is a country's name (Arabic or an alias), else None."""
        nq = normalize(q)
        for code, c in self.countries.items():
            if nq in {normalize(n) for n in [c["name_ar"], *c.get("aliases", [])]}:
                return code
        return None

    # ---------- describing a search (decision 035) ----------

    def clean_params(self, params):
        """Keep only search parameters we understand, with values we know. Used for links back to results."""
        out = {}
        q = (params.get("q") or "").strip()[:100]
        if q:
            out["q"] = q
        track = params.get("track") or ""
        if track in TRACKS:
            out["track"] = track
        field = params.get("field") or ""
        if field and track in ("emdad", "rnd") and self.field(track, field):
            out["field"] = field
        if (params.get("country") or "") in self.countries:
            out["country"] = params["country"]
        if (params.get("lang") or "") in LANGUAGE_AR:
            out["lang"] = params["lang"]
        return out

    def result_params(self, result):
        """The parameters that produced a search result, cleaned."""
        return self.clean_params({"q": result["q"], "track": result["track"], "field": result["field"],
                                  "country": result["country"], "lang": result["language"]})

    def back_url(self, raw):
        """The explorer URL a university page should link back to, from its `from` parameter.

        `raw` is the query string the results page put in the link (e.g. "q=AI&track=emdad").
        Only known parameters and values survive, and the path is always /universities,
        so the link can never point anywhere else. None when there's no `from`.
        """
        if raw is None:
            return None
        params = self.clean_params(dict(parse_qsl(raw[:400])))
        return "/universities" + ("?" + urlencode(params) if params else "")

    def describe(self, result):
        """What the student is looking at, in words.

        Returns {"applied": [{label_ar, value_ar, href, remove}], "summary_ar": str, "query": str, "non_english": bool}:
        - applied: one entry per active filter, each with a link to the same search without it
          (removing the track also removes its field). `remove` names the parameters it clears, so
          universities.js can clear just those in the live form (a link's href is a snapshot, and a
          stale one would bring back a filter removed a moment earlier).
        - summary_ar: one line for the screen-reader status message, e.g. «مسار الرواد: 30 جامعة»
        - query: the cleaned query string, carried on result links as `from`
        - non_english: a ranked list shows a university in a non-English-speaking country
          (so the page explains the language exception once)
        """
        params = self.result_params(result)

        def without(*names):
            rest = {k: v for k, v in params.items() if k not in names}
            return "/universities" + ("?" + urlencode(rest) if rest else "")

        def chip(label_ar, value_ar, *names):
            return {"label_ar": label_ar, "value_ar": value_ar, "href": without(*names), "remove": list(names)}

        applied = []
        if "q" in params:
            is_major = result["mode"] == "major" and any(
                normalize(params["q"]) in (normalize(m["name_ar"]), normalize(m["name_en"])) for m in result["majors"])
            applied.append(chip("التخصص" if is_major else "البحث", params["q"], "q"))
        if "track" in params:
            applied.append(chip("المسار", TRACKS[params["track"]]["short_ar"], "track", "field"))
        if "field" in params:
            applied.append(chip("المجال", self.field(params["track"], params["field"])["name_ar"], "field"))
        if "country" in params:
            applied.append(chip("الدولة", self.countries[params["country"]]["name_ar"], "country"))
        if "lang" in params:
            applied.append(chip("لغة الدولة", LANGUAGE_AR[params["lang"]], "lang"))

        parts = []
        for s in result["sections"]:
            if "waaid" in s:
                parts.append(f"{count_ar(len(s['waaid']), PROGRAMS_AR)} في مسار واعد")
                continue
            n = len(s["rows"]) if "rows" in s else len(s["universities"])
            where = TRACKS[s["track"]]["name_ar"] if s["track"] else "نتائج البحث"
            if s.get("field"):
                where += f" ({s['field']['name_ar']})"
            parts.append(f"{where}: {count_ar(n, UNIVERSITIES_AR)}" if n else f"{where}: لا توجد نتائج")
        non_english = any(not u["country_info"]["english"]
                          for s in result["sections"] for _, u in s.get("rows", []))
        return {"applied": applied, "summary_ar": "، ".join(parts), "query": urlencode(params),
                "non_english": non_english}

    # ---------- واعد ----------

    def waaid_matches(self, q=""):
        """واعد programs whose program, company, institution, or level matches q (all of them if q is empty).
        Each gets `university_id` when its institution is in the guide's lists, so we can link to it."""
        nq = normalize(q)
        out = []
        for p in self.waaid()["programs"]:
            key = normalize(f"{p['program_ar']} {p['company_ar']} {p['institution']} {p['level_ar']}")
            if not nq or nq in key:
                out.append({**p, "university_id": self.by_name.get(normalize(p["institution"]))})
        return out

    def _add_waaid(self, result, q):
        matches = self.waaid_matches(q) if q else []
        if matches and result["track"] in ("", "waaid"):
            result["sections"].append({"track": "waaid", "field": None, "waaid": matches})

    # ---------- search suggestions ----------

    def suggestions(self):
        """For the search box: majors grouped by their إمداد field (as in the guide), doctorate-only
        majors in their own group, and every university name in both languages."""
        groups, seen = [], set()
        emdad = sorted((f for (t, _), f in self.fields.items() if t == "emdad"), key=lambda f: min(f["list_pages"]))
        for f in emdad:
            majors = []
            for m in f["majors"]:
                if m["name_ar"] not in seen:
                    seen.add(m["name_ar"])
                    majors.append({"name_ar": m["name_ar"], "name_en": m["name_en"], "masters_only": m["masters_only"]})
            groups.append({"title_ar": f["name_ar"], "title_en": f["name_en"], "majors": majors})
        doctorate = []
        for (t, _), f in self.fields.items():
            if t != "rnd":
                continue
            for m in f["majors"]:
                if m["name_ar"] not in seen:
                    seen.add(m["name_ar"])
                    doctorate.append({"name_ar": m["name_ar"], "name_en": m["name_en"], "masters_only": False})
        if doctorate:
            groups.append({"title_ar": "تخصصات الدكتوراه فقط (البحث والتطوير)", "title_en": "Doctorate only", "majors": doctorate})
        unis = [{"id": u["id"], "name_ar": u["name_ar"], "name_en": u["name_en"],
                 "country_ar": u["country_info"]["name_ar"]}
                for u in sorted(self.universities.values(), key=lambda u: u["name_en"].lower())]
        return {"fields": groups, "universities": unis}

    # ---------- one university ----------

    def next_deadline(self, uid, today=None):
        """The university's next upcoming dated item for the current cycle, or None.
        Dates kept only for reference (a past cycle) never count."""
        from datetime import date as _date
        today = today or _date.today().isoformat()
        dates = [d for d in (self.details.get(uid) or {}).get("dates") or []
                 if d.get("date") and d["date"] >= today and not d.get("reference_only")]
        return min(dates, key=lambda d: d["date"]) if dates else None

    def key_facts(self, uid, today=None):
        """What a result row shows at a glance (decision 038). Unknowns are said, never left blank.

        Returns {"researched": bool, "sat_ar", "ielts_ar", "next", "admissions_url"}; without
        researched requirements, only researched=False.
        """
        d = self.details.get(uid)
        if not d:
            return {"researched": False}
        sat = (d.get("sat_act") or {}).get("policy") or "unknown"
        ielts = (d.get("english") or {}).get("ielts") or {}
        if ielts.get("min") is not None:
            ielts_ar = str(ielts["min"])
        elif ielts.get("note_ar"):
            ielts_ar = "الجامعة لا تنشر حدًا أدنى"
        else:
            ielts_ar = "لم نتحقق منه"
        return {"researched": True, "sat_ar": SAT_POLICY_AR.get(sat, SAT_POLICY_AR["unknown"]),
                "ielts_ar": ielts_ar, "next": self.next_deadline(uid, today),
                "admissions_url": d.get("admissions_url")}

    def sat_summary(self, track="arruaad"):
        """How many researched universities of a track require SAT/ACT, make it optional, etc.

        Returns {"total": n, "researched": n, "counts": {policy: n}} for the grade pages' test table
        (decision 038). Computed from the requirement files, so it can't drift from them.
        """
        on_track = [uid for uid, u in self.universities.items() if any(l["track"] == track for l in u["listings"])]
        researched = [uid for uid in on_track if uid in self.details]
        counts = {}
        for uid in researched:
            policy = (self.details[uid].get("sat_act") or {}).get("policy") or "unknown"
            counts[policy] = counts.get(policy, 0) + 1
        return {"total": len(on_track), "researched": len(researched), "counts": counts}

    def upcoming_deadlines(self, limit=6, today=None):
        """The next application deadlines across researched universities, soonest first (grade 12 page).
        Only «آخر موعد للتقديم» items of the current cycle."""
        from datetime import date as _date
        today = today or _date.today().isoformat()
        rows = []
        for uid, d in self.details.items():
            for x in d.get("dates") or []:
                if (x.get("date") and x["date"] >= today and not x.get("reference_only")
                        and x["event_ar"] == "آخر موعد للتقديم"):
                    rows.append({**x, "university": self.universities[uid]})
        rows.sort(key=lambda r: (r["date"], r["university"]["name_en"]))
        return rows[:limit]

    def timeline_stats(self):
        """Deadline patterns for the grade-page timeline (decision 039), counted from the researched files.

        Only «آخر موعد للتقديم» items of the current cycle (no reference_only). Returns
        {"with_deadlines": n, "early": n (a deadline in October or November), "january": n}.
        """
        early = january = total = 0
        for d in self.details.values():
            months = {x["date"][5:7] for x in d.get("dates") or []
                      if x.get("date") and not x.get("reference_only") and x["event_ar"] == "آخر موعد للتقديم"}
            if not months:
                continue
            total += 1
            early += bool(months & {"10", "11"})
            january += "01" in months
        return {"with_deadlines": total, "early": early, "january": january}

    def fee_groups(self):
        """US universities with a researched application fee, grouped by what their own page says about
        fee waivers (decision 050), for the guide «التقديم على الجامعات الأمريكية». Names in Arabic order."""
        groups = [
            ("accepts_common_app", "تقبل إعفاء Common App"),
            ("own_waiver", "لها إعفاء خاص بها"),
            ("not_stated", "لم تذكر صفحتها إعفاءً للطلاب الدوليين"),
            ("closed", "لا إعفاء للطلاب الدوليين"),
        ]
        rows = {key: [] for key, _ in groups}
        for uid, d in self.details.items():
            fee = d.get("application_fee")
            u = self.universities[uid]
            if not fee or u["country"] != "US":
                continue
            key = "closed" if fee["waiver"] in ("domestic_only", "none") else fee["waiver"]
            rows[key].append({"id": uid, "name_ar": u["name_ar"] or u["name_en"], "fee_usd": fee["fee_usd"]})
        return [{"key": key, "title_ar": title, "rows": sorted(rows[key], key=lambda r: r["name_ar"])}
                for key, title in groups if rows[key]]

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
        return {"university": u, "by_track": by_track, "details": details, "dates": dates,
                "logo": self.logos.get(uid)}

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
