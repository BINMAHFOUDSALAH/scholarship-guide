"""«خطتي» (decision 078, Part B; replaces «قائمتي», decision 035).

The plan lives in the student's browser, in localStorage["wadih:plan"]:

    {"v": 1, "items": [{"type": "university", "id": "harvard-university", "status": "applied", "updated": "2026-11-06"},
                       {"type": "program", "id": "arruaad", "status": "thinking", "updated": "2026-11-06"}]}

Ids, statuses and dates only: no names, grades or scores. The page POSTs it, and the server draws the rows
with each item's next step, from data we already publish. Nothing is stored here. Phase 2 stores the same
shape per account.
"""
import re

MAX_ITEMS = 100
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID = re.compile(r"^[a-z0-9-]{1,80}$")

# In the order a student moves through them. The first is what a new item starts with.
STATUSES = {
    "thinking": "أفكّر",
    "preparing": "أستعد",
    "applied": "قدّمت",
    "accepted": "قُبلت",
    "not_accepted": "لم أُقبل",
}
# Statuses whose date is worth showing («قدّمت في 6 نوفمبر 2026»).
DATED = {"applied": "قدّمت في {date}", "accepted": "قُبلت في {date}", "not_accepted": "لم أُقبل، في {date}"}


def program_targets(paths):
    """Every program a student can add to the plan: one per high-school track (its id), or the program's
    id when its single track has none (Aramco). {id: (path, track)}."""
    out = {}
    for path in paths:
        tracks = [t for t in path["tracks"] if t.get("for_high_school") is not False]
        for t in tracks:
            pid = t.get("id") or (path["id"] if len(tracks) == 1 else None)
            if pid:
                out[pid] = (path, t)
    return out


def clean(raw, universities, programs):
    """The plan as the browser sent it, kept only where it's valid: known ids, known statuses, ISO dates,
    no duplicates, at most MAX_ITEMS, in the student's order. Anything else is dropped quietly."""
    items = raw.get("items") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return []
    out, seen = [], set()
    for item in items[:MAX_ITEMS * 2]:
        if len(out) == MAX_ITEMS:
            break
        if not isinstance(item, dict):
            continue
        kind, iid = item.get("type"), item.get("id")
        if not isinstance(iid, str) or not ID.match(iid) or (kind, iid) in seen:
            continue
        if not ((kind == "university" and iid in universities) or (kind == "program" and iid in programs)):
            continue
        status = item.get("status") if item.get("status") in STATUSES else "thinking"
        updated = item.get("updated") if isinstance(item.get("updated"), str) and ISO_DATE.match(item["updated"]) else None
        seen.add((kind, iid))
        out.append({"type": kind, "id": iid, "status": status, "updated": updated})
    return out


def university_step(item, u, explorer):
    """The next step for a university, by status. Links go to pages that hold the sourced facts."""
    page = f"/universities/{u['id']}"
    listed = any(l["track"] in ("arruaad", "emdad") for l in u["listings"])
    status = item["status"]
    if status == "thinking":
        return {"text_ar": "افتح صفحتها: هل تطلب SAT؟ وكم درجة الإنجليزية؟", "href": page, "label_ar": "صفحة الجامعة"}
    if status == "preparing":
        nxt = explorer.next_deadline(u["id"])
        if nxt:
            return {"text_ar": "أقرب موعد لها في بياناتنا:", "date": nxt["date"], "href": page + "#dates", "label_ar": "مواعيدها ومصدرها"}
        return {"text_ar": "لا موعد قادمًا لها في بياناتنا، فراجع موقعها الرسمي.", "href": page, "label_ar": "صفحة الجامعة"}
    if status == "applied":
        if listed:
            return {"text_ar": "حتى يصلك الرد، جهّز مستندات الابتعاث.", "href": "/programs/custodian-scholarship#ready", "label_ar": "خطوات «معي قبول جامعي»"}
        return None
    if status == "accepted":
        if listed:
            return {"text_ar": "إن كان قبولك غير مشروط، فالخطوة التالية التقديم على الابتعاث.", "href": "/programs/custodian-scholarship#ready", "label_ar": "خطوات «معي قبول جامعي»"}
        return None
    return {"text_ar": "ابحث عن جامعات أخرى في المجال نفسه.", "href": "/universities", "label_ar": "ابحث في الجامعات"}


def program_step(item, path, track, status_now, apply_when_ar, has_page):
    """The next step for a program track, by the student's status and the track's status today."""
    page = f"/programs/{path['id']}" if has_page else None
    official = {"href": path["official_url"], "label_ar": "الموقع الرسمي", "external": True}
    status = item["status"]
    if status in ("thinking", "preparing"):
        if status_now == "open" and track.get("apply_url") and track.get("apply_when") == "in_school":
            return {"text_ar": "مفتوح الآن.", "href": track["apply_url"], "label_ar": "تقدم الآن", "external": True}
        step = {"text_ar": apply_when_ar}
        return {**step, "href": page, "label_ar": "الشروط والتفاصيل"} if page else {**step, **official}
    if status == "applied":
        return {"text_ar": "تابع حالة طلبك في الموقع الرسمي.", **official}
    if status == "accepted":
        return {"text_ar": "تابع الخطوات التالية في الموقع الرسمي.", **official}
    return {"text_ar": "انظر البرامج الأخرى، ومتى تتقدم على كل منها.", "href": "/programs", "label_ar": "البرامج"}


def rows(items, explorer, programs, track_status, apply_when, program_pages):
    """What the «خطتي» page draws for each item: its name, link, status, date and next step."""
    out = []
    for item in items:
        row = {**item, "status_ar": STATUSES[item["status"]],
               "dated_ar": DATED.get(item["status"]) if item["updated"] else None}
        if item["type"] == "university":
            u = explorer.universities[item["id"]]
            row.update(university=u, step=university_step(item, u, explorer))
        else:
            path, track = programs[item["id"]]
            confirmed = track.get("status_source") or track.get("owner_confirmed") or track.get("latest_programs")
            now = track_status(track) if confirmed else None
            several = len([t for t in path["tracks"] if t.get("for_high_school") is not False]) > 1
            row.update(path=path, track=track, track_now=now,
                       name_ar=track["name_ar"] if several else path["name_ar"],
                       program_ar=path["name_ar"] if several else path["provider_ar"],
                       step=program_step(item, path, track, now, apply_when.get(track.get("apply_when"), ""),
                                         path["id"] in program_pages))
        out.append(row)
    return out



# ---------- the hub (decision 083): what's coming, progress, and the calendar file ----------

SOON_DAYS = 30  # «قريبًا»: the dates in the next month
# The route a plan item walks; «لم أُقبل» is a turn, not a step.
ROUTE = ("thinking", "preparing", "applied", "accepted")


def dates(items, explorer, programs, track_status, today):
    """Every upcoming date in the plan, soonest first, each with where it comes from:
    - a university's own dates (its requirement file; each date has its official source);
    - an open program track's deadline (status_until, shown only with its status_source).
    Items the student has finished with («قُبلت», «لم أُقبل») add no dates, and a date without its official source is
    never shown (trust rule). Each date has its own uid, so two rounds on one day stay two calendar events."""
    out = []
    for item in items:
        if item["status"] in ("accepted", "not_accepted"):
            continue
        if item["type"] == "university":
            u = explorer.universities[item["id"]]
            for n, d in enumerate((explorer.details.get(u["id"]) or {}).get("dates") or []):
                if d.get("date") and d["date"] >= today and not d.get("reference_only") and d.get("source_url"):
                    out.append({"date": d["date"], "kind": "university", "university": u, "what": d,
                                "name_ar": u["name_ar"] or u["name_en"], "href": f"/universities/{u['id']}#dates",
                                "source_url": d["source_url"], "uid": f"{u['id']}-{d['date']}-{n}"})
        else:
            path, track = programs[item["id"]]
            until = track.get("status_until")
            if until and until >= today and track.get("status_source") and track_status(track) == "open":
                several = len([t for t in path["tracks"] if t.get("for_high_school") is not False]) > 1
                out.append({"date": until, "kind": "program", "name_ar": track["name_ar"] if several else path["name_ar"],
                            "what_ar": "آخر موعد للتقديم", "href": f"/programs/{path['id']}",
                            "source_url": track["status_source"], "uid": f"{item['id']}-{until}"})
    return sorted(out, key=lambda x: (x["date"], x["name_ar"]))


def progress(items):
    """How many items stand at each step of the route, and the furthest step reached (for the hub's route)."""
    counts = {s: sum(1 for i in items if i["status"] == s) for s in STATUSES}
    reached = max((ROUTE.index(i["status"]) for i in items if i["status"] in ROUTE), default=-1)
    return {"counts": counts, "reached": reached, "total": len(items)}


def _ics_text(text):
    """iCalendar text: escape \\ ; , and newlines (RFC 5545, 3.3.11)."""
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line):
    """Lines over 75 octets are folded with CRLF + space (RFC 5545, 3.1), never inside a UTF-8 character."""
    out, cur = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(cur) + len(b) > 74:
            out.append(cur.decode("utf-8"))
            cur = b" "
        cur += b
    out.append(cur.decode("utf-8"))
    return "\r\n".join(out)


def ics(events, base_url, stamp, title_ar):
    """The plan's dates as a calendar file the student adds to their own phone (decision 083): one all-day event per
    date, with a reminder three days before, its page and its official source. Built from the posted plan; nothing
    is stored, and no address or name is in it."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//wadihguide.com//khutati//AR", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH", f"X-WR-CALNAME:{_ics_text(title_ar)}"]
    for e in events:
        day = e["date"].replace("-", "")
        summary = e["summary"]
        lines += ["BEGIN:VEVENT", f"UID:{e['uid']}@wadihguide.com", f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{day}", f"SUMMARY:{_ics_text(summary)}",
                  f"DESCRIPTION:{_ics_text(e['description'])}", f"URL:{base_url}{e['href']}",
                  "BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_ics_text(summary)}", "TRIGGER:-P3D", "END:VALARM",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(line) for line in lines) + "\r\n"
