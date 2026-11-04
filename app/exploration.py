"""«جرّب قبل أن تقرر» (decision 069): an exploration activity, not a test.

The student answers about concrete activities («أستمتع به»… «لم أجرّبه، وأودّ أن أجرّبه»), and the result
groups the broad fields into three bands, each explained by the student's own answers. Fixed, readable
rules, no scores or percentages shown, no AI: the same answers always give the same result, and a test
can check every rule.

Nothing is stored. The form is posted once (POST, so the answers never appear in a URL or the server's
access log), the result is drawn from it, and the answers are gone. Why: docs/research/career-exploration-
evaluation-2026-11.md.
"""

import json
from pathlib import Path
from urllib.parse import parse_qs

DATA = json.loads((Path(__file__).parent.parent / "data" / "exploration.json").read_text(encoding="utf-8"))

ANSWERS = {a["id"]: a for a in DATA["answers"]}
FIELDS = {f["id"]: f for f in DATA["fields"]}
DIFFICULTIES = {d["id"]: d for d in DATA["difficulties"]}
SUBJECTS = {s["id"]: s for s in DATA["subjects"]}
GRADES = {g["id"]: g for g in DATA["grades"]}

# Fewer tried activities than this and the result leads with «جرّب أولًا»: too little to go on.
THIN_EVIDENCE = 10
# This many fields drawing the student and the result says the answers are close (it's common).
MANY_DRAWS = 6
# The form is small (about 2 KB); anything much bigger isn't ours.
MAX_BODY = 20_000


def is_public(show_drafts):
    """A draft until it's been reviewed and tried with students (decision 069); the owner sees it locally."""
    return show_drafts or not DATA.get("draft")


def activities():
    """The activities in the order asked: one from each field in turn, so no field comes twice in a row."""
    by_field = {}
    for a in DATA["activities"]:
        by_field.setdefault(a["field"], []).append(a)
    rounds = max(len(items) for items in by_field.values())
    return [items[i] for i in range(rounds) for items in by_field.values() if i < len(items)]


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
    return {
        "answers": {k: v for k, v in answers.items() if v},
        "difficulties": many("difficulty", DIFFICULTIES),
        "subjects": many("subject", SUBJECTS),
        "grade": one("grade", GRADES),
        "considered": one("considered", FIELDS),
    }


def band(counts, progress):
    """Which band a field goes in, from its answers. The rules, in words:
    - «تجذبك الآن»: you enjoy at least two of its activities and dislike none.
    - «تستحق التجربة»: you enjoy one, or want to try one, or it's fine for you and you've seen yourself progress
      in a subject close to it.
    - «لا تجذبك الآن»: everything else (for now; it's still shown)."""
    if counts["enjoy"] >= 2 and counts["dislike"] == 0:
        return "draws"
    if counts["enjoy"] >= 1 or counts["curious"] >= 1 or (progress and counts["ok"] >= 1):
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
        mine = [a for a in DATA["activities"] if a["field"] == f["id"]]
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

    # Strongest first inside a band: more enjoyed, then more wanted, then progress; ties keep the data's order.
    def strength(f):
        return (-f["counts"]["enjoy"], -f["counts"]["curious"], -len(f["progress"]), f["order"])

    considered = choices["considered"]
    bands = {name: sorted((f for f in fields if f["band"] == name and f["id"] != considered), key=strength)
             for name in ("draws", "try", "not_now")}
    tried = sum(1 for v in answers.values() if ANSWERS[v]["group"] == "tried")
    untried = len(answers) - tried
    draws = sum(1 for f in fields if f["band"] == "draws")
    return {
        "bands": bands,
        "considered": next((f for f in fields if f["id"] == considered), None),
        "tried": tried,
        "untried": untried,
        "skipped": len(DATA["activities"]) - len(answers),
        "thin": tried < THIN_EVIDENCE,
        "many_draws": draws >= MANY_DRAWS,
        "nothing_yet": not any(f["band"] in ("draws", "try") for f in fields),
        "several_draws": draws >= 2,
        "difficulties": [DIFFICULTIES[d] for d in choices["difficulties"]],
        "grade": choices["grade"],
    }


def field_names(explorer):
    """Each field's name: the Ministry guide's own name where the guide has the field (as in the explorer)."""
    return {f["id"]: explorer.field("emdad", f["guide_field"])["name_ar"] if f.get("guide_field") else f["name_ar"]
            for f in DATA["fields"]}


def field_view(fid, explorer, school_tracks):
    """What the result shows about a field: its name, example majors from the Ministry's guide and a link to
    its universities (or why there are none), and the school tracks whose official summary relates to it."""
    f = FIELDS[fid]
    guide = f.get("guide_field")
    view = {"id": fid, "try_ar": f["try_ar"], "programs": f.get("programs", []), "in_guide": bool(guide)}
    if guide:
        emdad = explorer.field("emdad", guide)
        view["name_ar"] = emdad["name_ar"]
        majors = list(dict.fromkeys(m["name_ar"] for track in ("emdad", "rnd")
                                    for m in (explorer.field(track, guide) or {}).get("majors", [])))
        view["majors"] = majors[:4]
        view["more_majors"] = len(majors) > 4
        view["explorer_url"] = f"/universities?track=emdad&field={guide}"
    else:
        view["name_ar"] = f["name_ar"]
    by_name = {t["name_ar"]: t for t in school_tracks["tracks"]}
    view["tracks"] = [by_name[name] for name in f["tracks"]]
    return view
