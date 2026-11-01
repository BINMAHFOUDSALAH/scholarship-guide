"""The site-check issue (scripts/watch_issue.py, decision 064), against a fake GitHub that remembers its
issues between "mornings". The rule under test: a notification (an opened issue or a comment) always
means something new and urgent."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("watch_issue", ROOT / "scripts" / "watch_issue.py")
watch_issue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch_issue)


class FakeGitHub:
    """Enough of GitHub's issues API to keep state across runs, and a log of what notifies the owner."""

    def __init__(self):
        self.issues, self.notifications = [], []

    def __call__(self, method, path, payload=None):
        if method == "GET":
            return [dict(i) for i in reversed(self.issues)] + [{"number": 99, "body": "a PR", "pull_request": {}}]
        if path.endswith("/issues"):
            issue = {"number": len(self.issues) + 1, "state": "open", **payload}
            self.issues.append(issue)
            self.notifications.append(("opened", payload["body"]))
            return issue
        number = int(path.split("/")[5])
        issue = next(i for i in self.issues if i["number"] == number)
        if path.endswith("/comments"):
            self.notifications.append(("comment", payload["body"]))
        else:
            issue.update(payload)
        return {}


def check(today, *findings):
    """findings: (key, urgent) pairs."""
    items = [{"section": "new", "key": k, "text": f"text {k}", "urgent": u} for k, u in findings]
    return {"today": today, "items": items, "report": f"## Site check, {today}"}


def run(gh, today, *findings):
    before = len(gh.notifications)
    result = watch_issue.sync(check(today, *findings), "o/r", gh)
    return result, gh.notifications[before:]


def test_routine_findings_alone_never_open_an_issue():
    gh = FakeGitHub()
    assert run(gh, "2026-11-01", ("sdaia-recheck", False)) == ("nothing to do", [])


def test_an_urgent_finding_opens_one_issue_and_is_announced_once():
    gh = FakeGitHub()
    result, said = run(gh, "2026-11-01", ("waaid:sar", True), ("sdaia-recheck", False))
    assert result == "opened #1" and [kind for kind, _ in said] == ["opened"]
    assert gh.issues[0]["title"] == "Site check: 1 urgent, 1 routine" and watch_issue.MARKER in gh.issues[0]["body"]
    assert run(gh, "2026-11-02", ("waaid:sar", True), ("sdaia-recheck", False)) == ("updated #1 (0 new)", [])
    result, said = run(gh, "2026-11-03", ("waaid:sar", True), ("live:/waaid:500", True))
    assert result == "updated #1 (1 new)" and said == [("comment", "New on 2026-11-03:\n\n- text live:/waaid:500")]
    assert len(gh.issues) == 1


def test_an_ongoing_finding_is_never_announced_again_even_after_skipped_runs():
    gh = FakeGitHub()
    run(gh, "2026-11-01", ("waaid:sar", True))
    assert run(gh, "2026-12-01", ("waaid:sar", True)) == ("updated #1 (0 new)", [])  # a month of missed runs


def test_a_flapping_finding_is_not_announced_again_within_a_week():
    gh = FakeGitHub()
    run(gh, "2026-11-01", ("waaid:sar", True), ("waaid-page", True))
    run(gh, "2026-11-02", ("waaid:sar", True))  # the page opened today
    assert run(gh, "2026-11-03", ("waaid:sar", True), ("waaid-page", True))[1] == []  # failed again: quiet
    assert run(gh, "2026-11-11", ("waaid:sar", True), ("waaid-page", True))[1] == []  # seen on the 3rd: still quiet
    assert run(gh, "2026-11-12", ("waaid:sar", True))[1] == []
    assert [k for k, _ in run(gh, "2026-11-20", ("waaid:sar", True), ("waaid-page", True))[1]] == ["comment"]


def test_it_closes_itself_when_nothing_urgent_is_left():
    gh = FakeGitHub()
    run(gh, "2026-11-01", ("waaid:sar", True), ("sdaia-recheck", False))
    result, said = run(gh, "2026-11-02", ("sdaia-recheck", False))
    assert result == "closed #1" and gh.issues[0]["state"] == "closed" and gh.issues[0]["state_reason"] == "completed"
    assert [k for k, _ in said] == ["comment"] and "routine" in gh.issues[0]["title"]
    assert run(gh, "2026-11-03", ("sdaia-recheck", False)) == ("left #1 closed", [])


def test_closing_it_by_hand_mutes_what_is_in_it_until_something_new():
    gh = FakeGitHub()
    run(gh, "2026-11-01", ("page:kgsp", True))
    gh.issues[0]["state"] = "closed"  # the owner closes it: "I know"
    assert run(gh, "2026-11-02", ("page:kgsp", True)) == ("left #1 closed", [])
    assert run(gh, "2026-11-20", ("page:kgsp", True)) == ("left #1 closed", [])  # muted, not just for a week
    result, said = run(gh, "2026-11-21", ("page:kgsp", True), ("waaid:new", True))
    assert result == "reopened #1 (1 new)" and gh.issues[0]["state"] == "open"
    assert said == [("comment", "New on 2026-11-21:\n\n- text waaid:new")]


def test_after_an_all_clear_the_next_urgent_finding_reopens_the_same_issue():
    gh = FakeGitHub()
    run(gh, "2026-11-01", ("waaid:sar", True))
    run(gh, "2026-11-02")
    result, said = run(gh, "2026-12-01", ("waaid:new", True))
    assert result == "reopened #1 (1 new)" and len(gh.issues) == 1 and [k for k, _ in said] == ["comment"]


def test_old_findings_are_forgotten_so_the_hidden_list_stays_small():
    gh = FakeGitHub()
    run(gh, "2026-11-01", ("waaid:sar", True), ("old", False))
    run(gh, "2026-12-15", ("waaid:sar", True))
    assert watch_issue.state_in(gh.issues[0]) == {"last_run": "2026-12-15", "seen": {"waaid:sar": "2026-12-15"}}
