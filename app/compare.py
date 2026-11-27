"""«قارن» (redesign v3, 2026-11): two to four universities side by side, from the records the Finder already uses.

Like a shop's comparison (Apple's iPhone compare, a phone shop's spec table): the same row for every university, so
a difference is visible at a glance, with «الفروق فقط» to hide the rows where they all agree. The scholarship's lists
and the university's own admission are separate groups (the two gates). Each value keeps its official source; an
unknown is said, never left blank. The page is drawn from the address (/compare?u=a,b,c), so a counsellor can send it.
"""

from app.i18n import tf, tr
from app.universities import (ENGLISH_TESTS, SAT_COUNTRIES, SAT_POLICY_AR, SAT_UNVERIFIED_AR, TRACKS, WAIVER_AR,
                              count_ar, english_compact, FIELDS_AR)

MAX = 4
UNKNOWN_AR = "لم نتحقق منه"


def ids_from(raw, explorer):
    """The universities named in ?u=a,b,c: known ids only, no repeats, at most MAX, in the given order."""
    out = []
    for uid in (raw or "").split(","):
        uid = uid.strip()
        if uid in explorer.universities and uid not in out:
            out.append(uid)
    return out[:MAX]


def _cell(text, source=None, state=None):
    return {"text": text, "source": source, "state": state}


def _lists(u):
    """The scholarship's lists the university is on, said the same way for every column."""
    parts = []
    ar = [l for l in u["listings"] if l["track"] == "arruaad"]
    em = [l for l in u["listings"] if l["track"] == "emdad"]
    if ar:
        parts.append(tf("الرواد: المرتبة {n}", n=ar[0]["rank"]))
    if em:
        parts.append(tf("إمداد: {fields}", fields=count_ar(len(em), FIELDS_AR)))
    return tr("، ").join(parts) if parts else tr("ليست في الرواد ولا إمداد")


def build(uids, explorer, answer, today):
    """{"universities": [...], "groups": [{"title_ar", "rows": [{"label_ar", "cells": [...], "same": bool}]}]}"""
    unis = [explorer.universities[uid] for uid in uids]
    details = [explorer.details.get(uid) or {} for uid in uids]
    groups = []

    def row(label, cells):
        texts = [c["text"] for c in cells]
        return {"label_ar": label, "cells": cells, "same": len(set(texts)) == 1}

    rows = [row("قوائم الابتعاث", [_cell(_lists(u), explorer.source["url"]) for u in unis])]
    rnd = [any(l["track"] == "rnd" for l in u["listings"]) for u in unis]
    if any(rnd):
        rows.append(row("البحث والتطوير (دكتوراه فقط)",
                        [_cell(tr("نعم") if r else tr("لا"), explorer.source["url"] if r else None) for r in rnd]))
    groups.append({"id": "lists", "gate": 1, "title_ar": "الابتعاث", "rows": rows})

    rows = []
    certs = [answer.certificate(explorer, u) for u in unis]
    if any(certs):
        rows.append(row("الثانوية السعودية للسنة الأولى", [
            _cell({"yes": tr("تقبلها"), "no": tr("لا تكفي وحدها"), "unknown": tr(UNKNOWN_AR)}[c["state"]],
                  c.get("source_url"), c["state"]) if c else _cell(tr("لم تذكر صفحاتها"), None, "unknown")
            for c in certs]))
    for test, label in ENGLISH_TESTS:
        cells = []
        for d in details:
            item = (d.get("english") or {}).get(test)
            if d and item:
                cells.append(_cell(english_compact(test, item), item.get("source_url")))
            else:
                cells.append(_cell(tr(UNKNOWN_AR), None, "unknown"))
        rows.append(row(label, cells))
    if any(u["country"] in SAT_COUNTRIES for u in unis):
        cells = []
        for u, d in zip(unis, details):
            if u["country"] not in SAT_COUNTRIES:
                cells.append(_cell(tr("لا ينطبق"), None, "none"))
                continue
            policy = (d.get("sat_act") or {}).get("policy")
            cells.append(_cell(tr(SAT_POLICY_AR.get(policy, SAT_POLICY_AR["unknown"])) if policy else tr(SAT_UNVERIFIED_AR),
                               (d.get("sat_act") or {}).get("source_url")))
        rows.append(row("SAT/ACT", cells))
    rows.append(row("منصة التقديم", [
        _cell(d["platform"]["value_ar"], d["platform"].get("source_url")) if d.get("platform") else _cell(tr(UNKNOWN_AR), None, "unknown")
        for d in details]))
    groups.append({"id": "admission", "gate": 2, "title_ar": "القبول في الجامعة", "rows": rows})

    rows = []
    cells = []
    for u in unis:
        dl = answer.deadline(explorer, u["id"], today) if u["id"] in explorer.details else None
        cells.append({"text": dl["date"] if dl else tr("لا يوجد لدينا موعد مؤكد"), "deadline": dl,
                      "source": dl.get("source_url") if dl else None, "state": dl["state"] if dl else "unknown"})
    rows.append(row("آخر موعد للتقديم", cells))
    fees = []
    for d in details:
        f = d.get("application_fee")
        if not f:
            fees.append(_cell(tr(UNKNOWN_AR) if d else tr("لم نجمعها بعد"), None, "unknown"))
            continue
        text = tr("بلا رسوم تقديم") if f.get("fee_usd") == 0 else (f"${f['fee_usd']}" if f.get("fee_usd") else tr("الرسوم غير منشورة"))
        if WAIVER_AR.get(f.get("waiver")):
            text += tr("، ") + tr(WAIVER_AR[f["waiver"]])
        fees.append(_cell(text, f.get("source_url")))
    if any(c["state"] != "unknown" for c in fees):
        rows.append(row("رسوم التقديم", fees))
    essays = [_cell(d["essays"]["summary_ar"], d["essays"].get("source_url")) if d.get("essays") else _cell(tr(UNKNOWN_AR), None, "unknown")
              for d in details]
    if any(c["state"] != "unknown" for c in essays):
        rows.append(row("المقالات", essays))
    groups.append({"id": "apply", "title_ar": "المواعيد والطلب", "rows": rows})

    groups.append({"id": "place", "title_ar": "المكان", "rows": [
        row("الدولة", [_cell(u["country_info"]["name_ar"]) for u in unis]),
        row("لغة الدولة الرسمية", [_cell(tr("الإنجليزية") if u["country_info"]["english"] else u["country_info"]["language_ar"]) for u in unis]),
    ]})
    return {"universities": unis, "groups": groups, "researched": [bool(d) for d in details]}
