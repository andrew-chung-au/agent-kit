"""The pull request flow in process.md, blueprints.md and the changelog (issue #239).

Opening the session branch's pull request and readying it are mechanical steps (C1); the
`gate` stop kind keeps a merge, a label and a waiver (C1, C6); Commits and pushes says who
pushes (C2), when the draft is readied (C5), what is refused (C6), how a records-only pull
request is readied (C7) and what CI does (C8); blueprints.md and the changelog name the
target (C9). These are reading checks: each pins a phrase a reader relies on.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"


def flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def section(text: str, heading: str) -> str:
    """The text of a `## ` or `### ` section, up to the next heading of any level."""
    match = re.search(r"(?m)^#{2,3} " + re.escape(heading) + r"\n(.*?)(?=^#{1,3} |\Z)", text, re.S)
    if not match:
        raise AssertionError(f"no section {heading!r}")
    return " ".join(match.group(1).split())


PROCESS = (KIT / "process.md").read_text(encoding="utf-8")
DECISION_POINTS = section(PROCESS, "Decision points")
COMMITS = section(PROCESS, "Commits and pushes")
LIFECYCLE = section(PROCESS, "Lifecycle")


class DecisionPointsTest(unittest.TestCase):
    def test_opening_and_readying_are_mechanical_steps(self):  # C1
        mechanical = re.search(r"Mechanical steps \((.*?)\) are not decision points and never ask", DECISION_POINTS)
        self.assertIsNotNone(mechanical)
        for phrase in ("posting a comment", "running a check", "opening the session branch's pull request",
                       "readying it"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, mechanical.group(1))
        self.assertIn("Opening or readying a pull request is never logged in the ledger and never asked.",
                      DECISION_POINTS)

    def test_the_gate_kind_keeps_merge_label_and_waiver(self):  # C1, C6
        self.assertIn("- `gate`: a label, a merge, a push other than the session's own branch under the "
                      "project's push opt-in, a waiver or an override.", DECISION_POINTS)
        self.assertNotIn("`gate`: a label, a merge, a push, a waiver", DECISION_POINTS)


class CommitsAndPushesTest(unittest.TestCase):
    def test_who_pushes(self):  # C2
        for phrase in ("Only the human pushes to `main` and merges.",
                       "the Claude Code cloud push, `AGENT_KIT_CLOUD_PUSH=1`",
                       "the orchestrator pushes that branch with the plain `git push -u origin <branch>`",
                       "first after the Engineer's first commit and before QA is launched, so CI runs alongside QA",
                       "After that it pushes each new commit.",
                       "Without the opt-in (the local sandbox, Codespaces, OpenCode, CodeBuddy, Antigravity, Kiro) "
                       "no agent pushes or opens a pull request",
                       "Lifecycle step 10 is unchanged: the human reviews, pushes and opens any pull request."):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, COMMITS)
        self.assertIn("10. The human reviews the diff, pushes and opens any pull request", LIFECYCLE)

    def test_opening_goes_through_make_pr_open(self):  # C3, C4 as described
        for phrase in ("`make pr-open N=<number> FILE=.scratch/<name>.md`", "`Refs #<number>`",
                       "`templates/github/pull_request_template.md`", "pre-approved wherever `make` is",
                       "a closing keyword before an issue reference", "the default branch, a detached HEAD",
                       "a branch whose `origin` copy is not at HEAD", "it prints that URL and creates nothing"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, COMMITS)

    def test_each_ready_condition(self):  # C5
        for phrase in ("takes the draft out of draft without asking, and records nothing in the ledger for it",
                       "every QA launch the tier requires posted PASS on the current head",
                       "**Assert clean** passed after each",
                       "A head whose only later commits touch `_docs/records/`",
                       "the body hash matches the recorded one (`make issue-hash N=<n>`)",
                       "every commit that touched a protected path was approved by the human",
                       "**Verify**, and CI on the head commit, fail only on pre-existing failures named by finding id",
                       "`make decisions N=<n>` lists no open point and no rework item of the issue",
                       "no ship-or-fix, waiver or amend is waiting",
                       "no role return with `Needs the human: yes` is unanswered",
                       "the GitHub connector's update with `draft: false`",
                       "it leaves the draft and says in the message to the human that it is ready"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, COMMITS)

    def test_refused_steps(self):  # C6
        for phrase in ("Refused: readying while any condition fails. The pull request stays a draft, and the next "
                       "message to the human names each failed condition.",
                       "merging, closing a pull request or an issue through a pull request, adding or removing a "
                       "label, and recording a waiver. Each stays with the human (`gate`) or with `make issue-close`."):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, COMMITS)

    def test_records_only_pull_requests(self):  # C7
        for phrase in ("files under `_docs/records/` and `_session-summaries/`",
                       "the planning roadmap file the docs index names",
                       "readied when CI passes, with no QA condition. It still waits for the human to merge.",
                       "Refused: readying a branch on this path that holds any other file"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, COMMITS)

    def test_ci_and_subscription(self):  # C8
        for phrase in ("Where the tool can subscribe to pull-request activity (Claude Code cloud), the orchestrator "
                       "subscribes after opening.",
                       "A CI failure that isn't a named pre-existing failure keeps the draft and goes to the human "
                       "in the next message; the orchestrator doesn't re-run, merge or push around it.",
                       "Elsewhere, the orchestrator reads the CI result before readying."):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, COMMITS)


class DocsTest(unittest.TestCase):
    def test_blueprints_names_the_target_and_the_template(self):  # C9
        text = flat(KIT / "blueprints.md")
        self.assertIn("GitHub module: `issue-create`, `issue-comment`, `issue-close` and `pr-open` targets", text)
        self.assertIn("`scripts/pr-open.sh`", text)
        self.assertIn("so `make pr-open` takes the body from this template", text)

    def test_changelog_has_the_entry_with_the_upgrade_step(self):  # C9
        text = (KIT / "CHANGELOG.md").read_text(encoding="utf-8")
        release = text.split("## Changes in 1.11", 1)[1].split("\n## ", 1)[0]
        entry = next((line for line in release.splitlines() if "#239)" in line), "")
        self.assertIn("`make pr-open N=<n> FILE=.scratch/<name>.md`", entry)
        self.assertIn("Behaviour change: no question before opening or readying a pull request.", entry)
        self.assertIn("add the `pr-open` target from `templates/Makefile.github.mk` and copy `scripts/pr-open.sh`",
                      entry)
        self.assertLess(release.index("#206)"), release.index("#239)"))

    def test_readme_lists_the_script(self):
        self.assertIn("pr-open.sh", flat(KIT / "README.md"))


if __name__ == "__main__":
    unittest.main()
