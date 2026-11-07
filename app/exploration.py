"""«جرّب قبل أن تقرر» (decision 069): an exploration activity, not a test.

The student answers 14 concrete activities («يعجبني / لا بأس / لا يجذبني», decision 087) and says where they've
seen themselves progress; the result groups the broad fields into three bands, each explained by the student's own
answers. Fixed, readable
rules, no scores or percentages shown, no AI: the same answers always give the same result, and a test
can check every rule.

Nothing is stored. The form is posted once (POST, so the answers never appear in a URL or the server's
access log), the result is drawn from it, and the answers are gone. Why: docs/research/career-exploration-
evaluation-2026-11.md.
"""

import json
from pathlib import Path
from urllib.parse import parse_qs

from app import i18n

DATA = json.loads((Path(__file__).parent.parent / "data" / "exploration.json").read_text(encoding="utf-8"))

ANSWERS = {a["id"]: a for a in DATA["answers"]}
FIELDS = {f["id"]: f for f in DATA["fields"]}
SUBJECTS = {s["id"]: s for s in DATA["subjects"]}

# Fewer answered activities than this (half of them) and the result says to try more first: too little to go on.
THIN_EVIDENCE = 7
# The form is small (about 2 KB); anything much bigger isn't ours.
MAX_BODY = 20_000


def is_public(show_drafts):
    """A draft until it's been reviewed and tried with students (decision 069); the owner sees it locally."""
    return show_drafts or not DATA.get("draft")


def activities():
    """The activities in the order asked: the data's order, which moves round Holland's six types (decision 087)."""
    return DATA["activities"]


def parse(body):
    """The posted form → the student's choices. Anything unknown is dropped, so the rest of the code
    only ever sees our own ids."""
    form = parse_qs(body[:MAX_BODY].decode("utf-8", "replace"), max_num_fields=200)

    def one(name, allowed):
        value = form.get(name, [""])[0]
        return value if value in allowed else None

    def many(name, allowed):
        return [v for v in dict.fromkeys(form.get(name, [])) if v in allowed]

    answers = {a["id"]: one(f"a-{a['id']}", ANSWERS) for a in DATA["activities"]}
    return {"answers": {k: v for k, v in answers.items() if v}, "subjects": many("subject", SUBJECTS)}


def band(counts, progress):
    """Which band a field goes in, from its answers. The rules, in words (decision 087):
    - «تجذبك الآن»: none of its activities fails to draw you, and you like at least two of them, or one and you've
      seen yourself progress in a subject close to it.
    - «تستحق التجربة»: you like one of its activities, or one is «لا بأس» for you.
    - «لا تجذبك الآن»: everything else (for now; it's still shown)."""
    if counts["dislike"] == 0 and (counts["enjoy"] >= 2 or (counts["enjoy"] >= 1 and progress)):
        return "draws"
    if counts["enjoy"] >= 1 or counts["ok"] >= 1:
        return "try"
    return "not_now"


def score(choices):
    """Group every field into a band, with the answers that put it there."""
    answers = choices["answers"]
    progress_by_field = {}
    for sid in choices["subjects"]:
        for fid in SUBJECTS[sid]["fields"]:
            progress_by_field.setdefault(fid, []).append(SUBJECTS[sid]["label_ar"])

    fields = []
    for order, f in enumerate(DATA["fields"]):
        mine = [a for a in DATA["activities"] if f["id"] in a["fields"]]
        counts = {aid: 0 for aid in ANSWERS}
        why = []
        for a in mine:
            if a["id"] in answers:
                counts[answers[a["id"]]] += 1
                why.append({"activity_ar": a["text_ar"], "answer": answers[a["id"]],
                            "answer_ar": ANSWERS[answers[a["id"]]]["label_ar"]})
        progress = progress_by_field.get(f["id"], [])
        fields.append({"id": f["id"], "order": order, "counts": counts, "why": why, "progress": progress,
                       "band": band(counts, bool(progress))})

    # Strongest first inside a band: more liked, then progress, then more «لا بأس»; ties keep the data's order.
    def strength(f):
        return (-f["counts"]["enjoy"], -len(f["progress"]), -f["counts"]["ok"], f["order"])

    bands = {name: sorted((f for f in fields if f["band"] == name), key=strength)
             for name in ("draws", "try", "not_now")}
    return {
        "bands": bands,
        "answered": len(answers),
        "skipped": len(DATA["activities"]) - len(answers),
        "thin": len(answers) < THIN_EVIDENCE,
        "nothing_yet": not any(f["band"] in ("draws", "try") for f in fields),
    }


def list_text(titles):
    """Field titles in a sentence: «أ، وب، وج» / "A; B; C" (an English title holds its own "and")."""
    return ("; " if i18n.is_english() else "، و").join(i18n.tr(t) for t in titles)


def why_text(f):
    """Why a field was suggested, in one short sentence from the student's own answers (decisions 073, 087): what
    they like, else what is «لا بأس» for them, and where they've seen themselves progress. At most two activities are
    named; every answer stays listed in the card's details. Built when shown, so it follows the page's language."""
    def said(answer):
        names = [i18n.tr(w["activity_ar"]) for w in f["why"] if w["answer"] == answer]
        return [n[:1].lower() + n[1:] for n in names] if i18n.is_english() else names  # mid-sentence in English

    enjoy, ok = said("enjoy"), said("ok")
    progress = [i18n.tr(p) for p in f["progress"]]
    parts = []
    if enjoy:
        pattern = {1: "لأنك تحب {a}", 2: "لأنك تحب {a}، و{b}"}.get(len(enjoy), "لأنك تحب {a}، و{b}، ونشاطًا آخر منه")
        parts.append(i18n.tf(pattern, a=enjoy[0], b=enjoy[1] if len(enjoy) > 1 else ""))
    elif ok:
        pattern = {1: "لأنك قلت «لا بأس» عن {a}", 2: "لأنك قلت «لا بأس» عن {a}، و{b}"}.get(len(ok), "لأنك قلت «لا بأس» عن {a}، و{b}، ونشاط آخر منه")
        parts.append(i18n.tf(pattern, a=ok[0], b=ok[1] if len(ok) > 1 else ""))
    if progress:
        pattern = "ولاحظت تقدمك في {p}" if parts else "لأنك لاحظت تقدمك في {p}"
        parts.append(i18n.tf(pattern, p=(", " if i18n.is_english() else " و").join(progress)))
    if not parts:
        return ""
    return (". " if i18n.is_english() else "، ").join(parts) + "."


def field_view(fid, explorer, school_tracks):
    """What a result card shows about a field: its plain title, real example majors with where they come from, a
    link to its universities (or why there are none), and the school tracks whose official summary relates to it."""
    f = FIELDS[fid]
    guide = f.get("guide_field")
    sources = {s.get("id"): s for s in DATA["sources"]}
    view = {"id": fid, "title_ar": f["title_ar"], "try_ar": f["try_ar"], "programs": f.get("programs", []),
            "in_guide": bool(guide), "majors": f["majors_ar"],
            "majors_source": {"title": "التصنيف السعودي الموحد للتخصصات", "url": sources["classification"]["url"]}
            if f["majors_from"] == "classification"
            else {"title": "دليل الوزارة لقوائم الجامعات", "url": explorer.source["url"]}}
    if guide:
        view["guide_name_ar"] = explorer.field("emdad", guide)["name_ar"]
        listed = guide_majors(explorer, guide)
        view["guide_only_major"] = listed[0] if len(listed) == 1 else None  # the card's examples go beyond the guide
        view["explorer_url"] = f"/universities?track=emdad&field={guide}"
    by_name = {t["name_ar"]: t for t in school_tracks["tracks"]}
    view["tracks"] = [by_name[name] for name in f["tracks"]]
    return view


def guide_majors(explorer, guide):
    """Every major the Ministry's guide lists under a field, in both of its lists."""
    return list(dict.fromkeys(m["name_ar"] for track in ("emdad", "rnd")
                              for m in (explorer.field(track, guide) or {}).get("majors", [])))
