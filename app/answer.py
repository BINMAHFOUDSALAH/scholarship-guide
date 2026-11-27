"""The answer to a student's question: «أريد دراسة علوم الحاسب في بريطانيا» (redesign v3, 2026-11).

Two steps, both on the data the Finder already publishes:

1. `parse(text, explorer)` reads a typed question into its parts: a major (or a university's name) and a country.
   «علوم الحاسب في بريطانيا» found nothing before (name search, 0 results), so the box now understands the
   sentence a student actually types, in Arabic or English.
2. `build(result, explorer, ...)` turns a search result into an answer a student can act on: the universities that
   fit, grouped by *why* they appear (الرواد takes every major; إمداد lists by field), each with the two gates kept
   apart (scholarship list membership, then university admission: the Saudi certificate, English, the next
   deadline), the country counts to narrow by, and the facts the next step depends on.

The answer is plain data with ids, sources and actions, so the page, /api/answer and وضّاح (next milestone) all
use the same records. Nothing here is typed twice: every fact comes from data/ with its source.
"""

import re
from pathlib import Path
from urllib.parse import urlencode

from app.i18n import tf, tr
from app.universities import (SAT_COUNTRIES, SAT_POLICY_AR, SAT_UNVERIFIED_AR, english_compact, normalize)

# How many cards a group shows before «اعرض الكل»: enough to compare, short enough to scan on a phone.
PREVIEW = 6
PREVIEW_COUNTRY = 12  # with a country chosen the lists are short; show them whole up to this

# Words around the subject of a typed question, as normalize() writes them (أ/إ/آ → ا, ة → ه, ى → ي). Only stripped
# from the edges of the question, so a major's own words are never touched. The question words students type, dialect
# included, are app/question_words.txt (the site search's list, kept outside the formal-Arabic check); these are the
# words of wanting to study.
FILLER = {w for line in (Path(__file__).parent / "question_words.txt").read_text(encoding="utf-8").splitlines()
          if not line.startswith("#") for w in line.split()} | {
    "دراسه", "ادرس", "الدراسه", "اتخصص", "تخصص", "بتخصص", "التخصص", "مجال", "افعل", "انوي", "ارغب", "رغبه", "بعد",
    "جامعات", "الجامعات", "ابحث",
    "i", "want", "to", "study", "would", "like", "in", "the", "where", "do", "start", "how", "can", "major",
    "majoring", "a", "an", "degree", "at", "of", "should", "go", "abroad", "universities", "university",
}
SENTENCE_BREAK = re.compile(r"[.؟?!،,؛;\n]+")


def _country_names(explorer):
    """[(normalized name, code)], longest first, so «كوريا الجنوبية» wins over «كوريا»."""
    names = []
    for code, c in explorer.countries.items():
        for name in [c["name_ar"], tr(c["name_ar"]), *c.get("aliases", [])]:
            n = normalize(name)
            if n:
                names.append((n, code))
    return sorted(set(names), key=lambda x: -len(x[0]))


def parse(text, explorer):
    """A typed question → {"q": subject or "", "country": code or None}, or None when there is nothing to read.

    «أريد دراسة علوم الحاسب في بريطانيا. من أين أبدأ؟» → {"q": "علوم الحاسب", "country": "GB"}
    "I want to study computer science in the UK" → {"q": "computer science", "country": "GB"}
    «بريطانيا» → {"q": "", "country": "GB"}
    The subject is kept only when it names a major or a university; otherwise the question isn't ours to guess.
    """
    country = None
    candidates = []
    names = _country_names(explorer)
    for part in SENTENCE_BREAK.split(text or ""):
        # Each word keeps its original spelling beside its normalized form, so the subject comes back as typed
        # («هندسة»), not as the search key («هندسه»).
        pairs = [(w, normalize(w)) for w in part.split()]
        pairs = [(w, n) for w, n in pairs if n]
        if not pairs:
            continue
        norm = [n for _, n in pairs]
        for name, code in names:
            size = len(name.split())
            hit = next((i for i in range(len(norm) - size + 1) if " ".join(norm[i:i + size]) == name), None)
            if hit is not None:
                country = country or code
                pairs = pairs[:hit] + pairs[hit + size:]
                break
        start, end = 0, len(pairs)
        while start < end and pairs[start][1] in FILLER:
            start += 1
        while end > start and pairs[end - 1][1] in FILLER:
            end -= 1
        if start < end:
            candidates.append((" ".join(n for _, n in pairs[start:end]), " ".join(w for w, _ in pairs[start:end])))
    subject = next((typed for key, typed in candidates if explorer.matching_majors(key) or explorer.is_health_search(key)
                    or any(key in u["search_key"] for u in explorer.universities.values())), "")
    if not subject and not country:
        return None
    return {"q": subject.strip(" .،,؟?!\"'«»"), "country": country}


# ---------- the answer ----------

def _cycle_deadlines(explorer, uid):
    """The university's general application deadlines for the current cycle (not a single group's, not a past
    cycle's), oldest first. The same rule as the homepage's nearest deadlines and وضّاح's preview."""
    d = explorer.details.get(uid) or {}
    return sorted((x for x in d.get("dates") or []
                   if x.get("date") and not x.get("reference_only") and x["event_ar"] == "آخر موعد للتقديم"
                   and "فقط" not in (x.get("note_ar") or "")), key=lambda x: x["date"])


def deadline(explorer, uid, today):
    """{"state": "upcoming" | "passed", ...the date record} for the next general deadline, or the last one when the
    cycle's deadlines have all passed (Oxford and Cambridge close in October). None when the file has no date."""
    dates = _cycle_deadlines(explorer, uid)
    upcoming = [x for x in dates if x["date"] >= today]
    if upcoming:
        return {"state": "upcoming", **upcoming[0]}
    if dates:
        return {"state": "passed", **dates[-1]}
    return None


def certificate(explorer, u):
    """The Saudi secondary certificate for year 1, as the university's own page says (decision 054): "yes", "no",
    or "unknown" where it decides the route (the UK, where most universities ask for a foundation year first) and
    we haven't read it. None elsewhere when the file doesn't say."""
    sc = (explorer.details.get(u["id"]) or {}).get("saudi_certificate") or {}
    if sc.get("direct_entry") is not None:
        return {"state": "yes" if sc["direct_entry"] else "no", "note_ar": sc.get("note_ar"),
                "quote": sc.get("quote"), "source_url": sc.get("source_url")}
    if u["country"] == "GB" and u["id"] in explorer.details:
        return {"state": "unknown", "note_ar": None, "quote": None, "source_url": None}
    return None


def card(explorer, u, listing, today):
    """One university in an answer: why it is here (its list and place) and the admission gate at a glance."""
    d = explorer.details.get(u["id"])
    english = ((d or {}).get("english") or {}).get("ielts")
    sat = None
    if u["country"] in SAT_COUNTRIES and d is not None:
        policy = (d.get("sat_act") or {}).get("policy")
        sat = SAT_POLICY_AR.get(policy, SAT_POLICY_AR["unknown"]) if policy else SAT_UNVERIFIED_AR
    return {
        "university": u, "id": u["id"], "rank": listing["rank"], "track": listing["track"], "field": listing.get("field"),
        "masters_only": bool(listing.get("masters_only")), "logo": explorer.logos.get(u["id"]),
        "researched": d is not None,
        "certificate": certificate(explorer, u),
        "english": {"text": english_compact("ielts", english), "varies": bool(english.get("varies")),
                    "source_url": english.get("source_url")} if english else None,
        "sat": sat,
        "deadline": deadline(explorer, u["id"], today) if d else None,
        "admissions_url": (d or {}).get("admissions_url"),
    }


def _full_href(track, field=None, country=None):
    params = {k: v for k, v in (("track", track), ("field", field), ("country", country)) if v}
    return "/universities?" + urlencode(params)


def _facets(explorer, q):
    """How many universities fit the same major in each country (unique across lists), most first: the country
    chips that narrow an answer in one tap, like a shop's filter counts."""
    r = explorer.search(q=q)
    seen = {}
    for s in r["sections"]:
        for _, u in s.get("rows", []):
            seen[u["id"]] = u["country"]
    counts = {}
    for code in seen.values():
        counts[code] = counts.get(code, 0) + 1
    return [{"code": c, "name_ar": explorer.countries[c]["name_ar"], "count": n}
            for c, n in sorted(counts.items(), key=lambda kv: (-kv[1], tr(explorer.countries[kv[0]]["name_ar"])))]


def build(result, explorer, scholarship_tracks, prep_fact=None, today=None):
    """The answer for a search result, or None when the result isn't a question about a major or a country
    (a university's name, a whole track list, واعد: those keep their own views).

    scholarship_tracks: the King scholarship's tracks by id (paths.json), for each group's sourced rule.
    """
    from app.clock import date
    today = today or date.today().isoformat()
    mode, country = result["mode"], result["country"]
    if result["language"]:
        # The country-language filter is an advanced refinement with its own explanations (a conflict with the
        # country, the language exception): the classic lists say them, so the answer steps aside.
        return None
    if mode == "major":
        kind = "major"
    elif mode == "browse" and country and not result["track"]:
        kind = "country"
    else:
        return None

    def rule_source(track_id):
        t = scholarship_tracks.get(track_id) or {}
        facts = t.get("facts") or []
        src = facts[0]["sources"][0] if facts and facts[0].get("sources") else None
        return {"title_ar": src["title"], "url": src["url"]} if src else None

    guide = {"title_ar": explorer.source["title_ar"], "url": explorer.source["url"]}
    preview = PREVIEW_COUNTRY if country else PREVIEW
    groups, placed, empty = [], set(), []
    for s in result["sections"]:
        if "rows" not in s or s["track"] not in ("arruaad", "emdad"):
            continue
        rows = [(l, u) for l, u in s["rows"] if u["id"] not in placed]
        placed.update(u["id"] for _, u in rows)
        if not rows:
            # Said in one line («لا جامعة في ألمانيا في قائمة الرواد»), never an empty group.
            empty.append({"track": s["track"], "field": s.get("field")})
            continue
        if s["track"] == "arruaad":
            why = "يقبل كل التخصصات في جامعاته الثلاثين."
            source = rule_source("arruaad")
        else:
            names = list(dict.fromkeys(m["name_ar"] for m in s.get("matched_majors", [])))
            why = (tf("«{major}» من مجال «{field}»، والترتيب للمجال كله، فتأكد أن الجامعة تدرّس التخصص.",
                      major=names[0], field=s["field"]["name_ar"]) if names else
                   tf("الترتيب لمجال «{field}» كله.", field=s["field"]["name_ar"]))
            source = guide
        groups.append({
            "track": s["track"], "field": s.get("field"), "why_ar": why, "source": source, "rule": rule_source(s["track"]),
            "count": len(rows), "items": [card(explorer, u, l, today) for l, u in rows[:preview]],
            "more_href": _full_href(s["track"], (s.get("field") or {}).get("id"), country) if len(rows) > preview else None,
        })

    fields = []
    if kind == "country":
        # A country without a major: الرواد's universities there (every major), then إمداد's fields with their
        # counts, so the next tap is a field (a list is ranked per field).
        for (t, fid), f in sorted(explorer.fields.items(), key=lambda kv: min(kv[1]["list_pages"])):
            if t != "emdad":
                continue
            n = sum(1 for _, u in explorer.listings("emdad", fid) if u["country"] == country)
            if n:
                fields.append({"field": f, "count": n, "href": _full_href("emdad", fid, country)})

    items = [i for g in groups for i in g["items"]]
    total = sum(g["count"] for g in groups)
    upcoming = sorted((i for i in items if i["deadline"] and i["deadline"]["state"] == "upcoming"),
                      key=lambda i: i["deadline"]["date"])
    ielts = sorted(e for e in ((((explorer.details.get(i["id"]) or {}).get("english") or {}).get("ielts") or {}).get("min")
                               for i in items) if e is not None)
    major_names = result.get("major_names") or []
    return {
        "kind": kind, "q": result["q"], "country": country,
        "country_ar": explorer.countries[country]["name_ar"] if country else None,
        "major_ar": major_names[0] if len(major_names) == 1 else None,
        "major_fields": result.get("major_fields") or [],
        "total": total, "groups": groups, "fields": fields, "empty": empty,
        "facets": _facets(explorer, result["q"]) if kind == "major" else [],
        "soonest": upcoming[0] if upcoming else None,
        "ielts_low": ielts[0] if ielts else None,
        # The UK's usual route: a foundation year first. The scholarship's own conditions for it, sourced.
        "foundation": any((i["certificate"] or {}).get("state") == "no" for i in items),
        "prep_fact": prep_fact,
        "unresearched": sum(1 for i in items if not i["researched"]),
        "health": result.get("health"),
    }


def overview(explorer):
    """Every university in the lists, counted by country, most first: what the homepage shows before the student
    asks (2026-11-27: an example answer opened on «في بريطانيا» and read as a filter, so the page now starts open)."""
    counts = {}
    for u in explorer.universities.values():
        counts[u["country"]] = counts.get(u["country"], 0) + 1
    return [{"code": c, "name_ar": explorer.countries[c]["name_ar"], "count": n}
            for c, n in sorted(counts.items(), key=lambda kv: (-kv[1], tr(explorer.countries[kv[0]]["name_ar"])))]


def as_data(answer, prefix=""):
    """The answer as plain JSON for /api/answer and وضّاح: ids, facts with their sources, and the actions a student
    can take on each university. No HTML, no translated layout."""
    if not answer:
        return None

    def item(i):
        u = i["university"]
        return {
            "id": i["id"], "name_ar": u["name_ar"], "name_en": u["name_en"], "country": u["country"],
            "list": {"track": i["track"], "field": i["field"], "rank": i["rank"], "masters_only": i["masters_only"]},
            "certificate": {k: v for k, v in (i["certificate"] or {}).items() if v is not None} or None,
            "english_ielts": i["english"], "sat_act": i["sat"],
            "deadline": {k: i["deadline"].get(k) for k in ("state", "date", "event_ar", "round_ar", "cycle_ar", "source_url")}
            if i["deadline"] else None,
            "admissions_url": i["admissions_url"],
            "actions": [
                {"type": "open", "href": f"{prefix}/universities/{i['id']}"},
                {"type": "save", "item": {"type": "university", "id": i["id"]}},
                {"type": "compare", "id": i["id"]},
            ],
        }

    return {
        "kind": answer["kind"], "q": answer["q"], "country": answer["country"], "total": answer["total"],
        "groups": [{"track": g["track"], "field": (g["field"] or {}).get("id"), "why_ar": g["why_ar"],
                    "source": g["source"], "rule_source": g["rule"], "count": g["count"],
                    "items": [item(i) for i in g["items"]],
                    "more_href": prefix + g["more_href"] if g["more_href"] else None} for g in answer["groups"]],
        "countries": answer["facets"],
        "fields": [{"field": f["field"]["id"], "name_ar": f["field"]["name_ar"], "count": f["count"],
                    "href": prefix + f["href"]} for f in answer["fields"]],
        "foundation_rule": ({"text_ar": answer["prep_fact"]["text_ar"], "sources": answer["prep_fact"]["sources"]}
                            if answer["foundation"] and answer["prep_fact"] else None),
    }
