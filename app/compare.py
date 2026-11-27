"""«قارن» (redesign v3, 2026-11): two to four universities side by side, from the records the Finder already uses.

Like a shop's comparison (Apple's iPhone compare, a phone shop's spec table): the same row for every university, so
a difference is visible at a glance, with «الفروق فقط» to hide the rows where they all agree. The scholarship's lists
and the university's own admission are separate groups (the two gates). An unknown is said, never left blank. The page
is drawn from the address (/compare?u=a,b,c), so a counsellor can send it.

2026-11-27 (owner): a «المصدر» pill in every cell drew more attention than the facts and made short values wrap on a
phone. Each value is now split into what answers the row (`value`: «7.5») and what qualifies it (`note`: «لا تقل أي
مهارة عن 7.0»). Every value still keeps its official source, shown with «عرض المصادر»: once for the row when every
university's value comes from the same document (the Ministry's guide ranks them all), otherwise under each value,
named by the site it comes from, so a source never drifts to the wrong university.
"""

from urllib.parse import urlsplit

from app.i18n import tf, tr
from app.universities import (ENGLISH_TESTS, FIELDS_AR, SAT_COUNTRIES, SAT_POLICY_AR, SAT_UNVERIFIED_AR, WAIVER_AR,
                              count_ar, no_score_ar, score_text)

MAX = 4
UNKNOWN_AR = "لم نتحقق منه"
NO_MIN_AR = "لا يوجد حد أدنى منشور"
NOT_ON_LIST_AR = "ليست في القائمة"
# The Ministry's guide, named as a student would look for it (its full title is long and says the year twice).
GUIDE_LABEL_AR = "دليل الوزارة لقوائم الجامعات"


def ids_from(raw, explorer):
    """The universities named in ?u=a,b,c: known ids only, no repeats, at most MAX, in the given order."""
    out = []
    for uid in (raw or "").split(","):
        uid = uid.strip()
        if uid in explorer.universities and uid not in out:
            out.append(uid)
    return out[:MAX]


# Second-level domains a university's site sits under («ox.ac.uk», «nus.edu.sg»), so its name is the label shown.
_SHARED_SUFFIXES = {"ac", "edu", "co", "gov", "org", "net"}


# File hosts that say nothing about whose document it is (a university's PDF on a content network).
_FILE_HOSTS = {"sitecorecloud.io", "amazonaws.com", "cloudfront.net", "azureedge.net", "googleusercontent.com"}


def site_of(url):
    """The official site a source is on, short enough for a phone: «ox.ac.uk», «harvard.edu», «utoronto.ca».
    A file on a content network is named by what it is («ملف PDF»): its column already says whose it is."""
    split = urlsplit(url)
    host = (split.hostname or "").lower()
    if any(host == h or host.endswith("." + h) for h in _FILE_HOSTS):
        return tr("ملف PDF") if split.path.lower().endswith(".pdf") else host
    parts = host.split(".")
    if parts and parts[0] == "www":
        parts = parts[1:]
    keep = 3 if len(parts) >= 3 and parts[-2] in _SHARED_SUFFIXES and len(parts[-1]) == 2 else 2
    return ".".join(parts[-keep:])


def _cell(value, note=None, sources=(), state=None, plain=False):
    """One university's answer to a row.

    value: what answers the row, set strongest. note: what qualifies it, beside or under it.
    sources: [{"url", "what"}], `what` naming the part a second link supports («الإعفاء»), None for the value itself.
    state: the kind of answer when it is not a fact we read: "unknown" (we haven't checked), "nomin" (the university
    publishes no minimum: a fact), "none" (doesn't apply, or not on the list), "no" (a limit), "passed".
    plain: a sentence rather than a figure (essays), so it reads at body weight.
    """
    return {"value": value, "note": note, "state": state, "plain": plain,
            "sources": [{"url": s["url"], "what": s.get("what"), "site": site_of(s["url"])} for s in sources if s.get("url")]}


def _src(url, what=None):
    return {"url": url, "what": what}


def _split(text, limit=40):
    """A long published value as its answer and its qualification: «UCAS، مع اختبار قبول…» → «UCAS» + «مع اختبار
    قبول…». Applied to the text in the page's language, at its first clause break, only when the answer stays short."""
    best = None
    for mark in ("، ", ", ", " ("):
        i = text.find(mark)
        if 0 < i <= limit and (best is None or i < best[0]):
            best = (i, mark)
    if best is None:
        return text, None
    i, mark = best
    rest = text[i + len(mark):].strip()
    if mark == " (" and rest.endswith(")") and rest.count("(") == 0:
        rest = rest[:-1]
    return text[:i], rest or None


def english_cell(test, item):
    """An English test as a figure and its conditions, keeping the distinctions english_compact keeps: a hard minimum,
    a recommended score (never shown as a minimum), a level that depends on the program, a per-skill minimum."""
    if not item:
        return _cell(tr(UNKNOWN_AR), state="unknown")
    sources = [_src(item.get("source_url"))]
    if item.get("recommended_source_url") and item["recommended_source_url"] != item.get("source_url"):
        sources.append(_src(item["recommended_source_url"], "الموصى به"))
    if item.get("accepted") is False:
        return _cell(tr("لا يُقبل"), tr("لإثبات اللغة"), sources, "no")
    if item.get("listed") is False:
        return _cell(tr("ليس ضمن اختباراتها"), tr("لا تذكره الجامعة بين الاختبارات المقبولة"), sources, "none")
    low, rec, each = item.get("min"), item.get("recommended"), item.get("each_min")
    if low is not None:
        notes = []
        if item.get("varies"):
            value = tf("من {score}", score=score_text(test, low))
            notes.append(tr("حسب التخصص"))
        else:
            value = score_text(test, low)
        if rec is not None:
            notes.append(tf("الموصى به {score}", score=score_text(test, rec)))
        elif each is not None and not item.get("varies"):
            notes.append(tf("لا تقل أي مهارة عن {score}", score=score_text(test, each)))
        return _cell(value, tr("، ").join(notes) or None, sources)
    if rec is not None:
        return _cell(tr(NO_MIN_AR), tf("الموصى به {score}", score=score_text(test, rec)), sources, "nomin")
    if item.get("varies"):
        return _cell(tr("يختلف حسب التخصص"), None, sources)
    said = no_score_ar(item)
    return _cell(tr(said), None, sources if said == NO_MIN_AR else [], "nomin" if said == NO_MIN_AR else "unknown")


def _lists(explorer, unis):
    """The scholarship's lists, one row per list, so a rank is read as the rank it is («المرتبة في قائمة الرواد»)."""
    guide = explorer.source["url"]
    rows = []
    ar = [[l for l in u["listings"] if l["track"] == "arruaad"] for u in unis]
    if any(ar):
        rows.append(("المرتبة في قائمة الرواد", [
            _cell(str(a[0]["rank"]), None, [_src(guide)]) if a else _cell(tr(NOT_ON_LIST_AR), None, [_src(guide)], "none")
            for a in ar]))
    em = [[l for l in u["listings"] if l["track"] == "emdad"] for u in unis]
    if any(em):
        cells = []
        for e in em:
            if not e:
                cells.append(_cell(tr(NOT_ON_LIST_AR), None, [_src(guide)], "none"))
                continue
            names = list(dict.fromkeys(tr(explorer.fields[("emdad", l["field"])]["name_ar"]) for l in e
                                       if ("emdad", l["field"]) in explorer.fields))
            cells.append(_cell(count_ar(len(e), FIELDS_AR), tr("، ").join(names) if len(names) <= 3 else None, [_src(guide)]))
        rows.append(("مجالاتها في قائمة إمداد", cells))
    rnd = [any(l["track"] == "rnd" for l in u["listings"]) for u in unis]
    if any(rnd):
        rows.append(("في قائمة البحث والتطوير (دكتوراه فقط)",
                     [_cell(tr("نعم"), None, [_src(guide)]) if r else _cell(tr("لا"), None, [_src(guide)], "none")
                      for r in rnd]))
    return rows


def _row(label, cells, explorer):
    """A row: its label, its cells, whether they all agree (for «الفروق فقط»), and its one source when every value
    comes from the same document (shown once for the row instead of under each value)."""
    texts = [(c["value"], c["note"]) for c in cells]
    urls = [tuple(s["url"] for s in c["sources"]) for c in cells]
    shared = None
    if len(cells) > 1 and all(len(u) == 1 for u in urls) and len(set(urls)) == 1:
        url = urls[0][0]
        shared = {"url": url, "label": tr(GUIDE_LABEL_AR) if url == explorer.source["url"] else site_of(url)}
    return {"label_ar": label, "cells": cells, "same": len(set(texts)) == 1, "source": shared}


def build(uids, explorer, answer, today):
    """{"universities": [...], "groups": [{"title_ar", "rows": [{"label_ar", "cells": [...], "same", "source"}]}]}"""
    unis = [explorer.universities[uid] for uid in uids]
    details = [explorer.details.get(uid) or {} for uid in uids]
    groups = []

    def row(label, cells):
        return _row(label, cells, explorer)

    groups.append({"id": "lists", "gate": 1, "title_ar": "الابتعاث",
                   "rows": [row(label, cells) for label, cells in _lists(explorer, unis)]})

    rows = []
    certs = [answer.certificate(explorer, u) for u in unis]
    if any(certs):
        words = {"yes": "تقبلها", "no": "لا تكفي وحدها", "unknown": UNKNOWN_AR}
        rows.append(row("الثانوية السعودية للسنة الأولى", [
            _cell(tr(words[c["state"]]), None, [_src(c.get("source_url"))], c["state"] if c["state"] != "yes" else None)
            if c else _cell(tr("لم تذكر صفحاتها"), None, [], "unknown")
            for c in certs]))
    for test, label in ENGLISH_TESTS:
        rows.append(row(label, [english_cell(test, (d.get("english") or {}).get(test) if d else None) for d in details]))
    if any(u["country"] in SAT_COUNTRIES for u in unis):
        cells = []
        for u, d in zip(unis, details):
            if u["country"] not in SAT_COUNTRIES:
                cells.append(_cell(tr("لا ينطبق"), tr("ليس من شروط القبول في بلدها"), [], "none"))
                continue
            sat = d.get("sat_act") or {}
            policy = sat.get("policy")
            if not policy:
                cells.append(_cell(tr(SAT_UNVERIFIED_AR), None, [], "unknown"))
            else:
                cells.append(_cell(tr(SAT_POLICY_AR.get(policy, SAT_POLICY_AR["unknown"])), None, [_src(sat.get("source_url"))],
                                   "unknown" if policy not in SAT_POLICY_AR or policy == "unknown" else None))
        rows.append(row("SAT/ACT", cells))
    cells = []
    for d in details:
        p = d.get("platform")
        if not p:
            cells.append(_cell(tr(UNKNOWN_AR), None, [], "unknown"))
            continue
        value, note = _split(tr(p["value_ar"]))
        cells.append(_cell(value, note, [_src(p.get("source_url"))]))
    rows.append(row("منصة التقديم", cells))
    groups.append({"id": "admission", "gate": 2, "title_ar": "القبول في الجامعة", "rows": rows})

    rows = []
    cells = []
    for u in unis:
        dl = answer.deadline(explorer, u["id"], today) if u["id"] in explorer.details else None
        if not dl:
            cells.append(_cell(tr("لا يوجد لدينا موعد مؤكد"), None, [], "unknown"))
            continue
        c = _cell(dl["date"], None, [_src(dl.get("source_url"))], None if dl["state"] == "upcoming" else "passed")
        c["deadline"] = dl
        cells.append(c)
    rows.append(row("آخر موعد للتقديم", cells))
    fees = []
    for d in details:
        f = d.get("application_fee")
        if not f:
            fees.append(_cell(tr(UNKNOWN_AR) if d else tr("لم نجمعها بعد"), None, [], "unknown"))
            continue
        if f.get("fee_usd") == 0:
            value = tr("بلا رسوم")
        elif f.get("fee_usd"):
            value = f"${f['fee_usd']}"
        else:
            value = tr("الرسوم غير منشورة")
        waiver = WAIVER_AR.get(f.get("waiver"))
        sources = [_src(f.get("source_url"))]
        if waiver and f.get("waiver_source_url") and f["waiver_source_url"] != f.get("source_url"):
            sources.append(_src(f["waiver_source_url"], "الإعفاء"))
        fees.append(_cell(value, tr(waiver) if waiver else None, sources, None if f.get("fee_usd") is not None else "nomin"))
    if any(c["state"] != "unknown" for c in fees):
        rows.append(row("رسوم التقديم", fees))
    essays = [_cell(tr(d["essays"]["summary_ar"]), None, [_src(d["essays"].get("source_url"))], plain=True) if d.get("essays")
              else _cell(tr(UNKNOWN_AR), None, [], "unknown") for d in details]
    if any(c["state"] != "unknown" for c in essays):
        rows.append(row("المقالات", essays))
    groups.append({"id": "apply", "title_ar": "المواعيد والطلب", "rows": rows})

    groups.append({"id": "place", "title_ar": "المكان", "rows": [
        row("الدولة", [_cell(tr(u["country_info"]["name_ar"])) for u in unis]),
        row("لغة الدولة الرسمية", [_cell(tr("الإنجليزية") if u["country_info"]["english"] else tr(u["country_info"]["language_ar"]))
                                   for u in unis]),
    ]})
    return {"universities": unis, "groups": groups, "researched": [bool(d) for d in details]}
