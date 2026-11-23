"""Doc test for issue #203: the PM grooms up to GROOM_AHEAD issues ahead, each in the agreed order.

The rules are enforced by the orchestrator reading them, with no script, so the wording is what
has to stay. Whitespace is normalised, so line wrapping does not matter.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"


def flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def between(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    return text[begin:text.index(end, begin)]


class GroomAheadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.process = flat(KIT / "process.md")
        lifecycle = between(cls.process, "## Lifecycle", "## Commits and pushes")
        cls.step2 = re.search(r"(?:^| )2\. (.*?)(?= 3\. )", lifecycle).group(1)
        cls.backlog = between(cls.process, "## Backlog", "## Issue comments")
        cls.approved = between(cls.process, "### Approved text", "### Session rulings")
        cls.pm = flat(KIT / "team" / "pm.md")
        cls.comments = flat(KIT / "procedures" / "orchestrator-comments.md")
        cls.roadmap = flat(KIT / "templates" / "roadmap.md")
        cls.customizing = flat(KIT / "customizing.md")
        cls.changelog = flat(KIT / "CHANGELOG.md")

    def test_c1_groom_ahead_replaces_the_one_at_a_time_rule(self):
        for needle in ("The PM may groom up to `GROOM_AHEAD` issues ahead of the one in progress, "
                       "in the agreed order",
                       "counts as groomed ahead when a valid `PM:` comment's `Body sha256:` matches "
                       "its current body and it hasn't started",
                       "`GROOM_AHEAD=0` is one at a time",
                       "The PM's comment records the body hash"):
            self.assertIn(needle, self.step2, needle)
        for gone in ("only the next issue in the agreed order", "not a second unlabelled issue"):
            self.assertNotIn(gone, self.process, gone)

    def test_c2_refusals_and_enforcement_sentence(self):
        for needle in ("Refused: grooming beyond `GROOM_AHEAD`, and grooming an issue that has no place "
                       "in the order",
                       "The orchestrator enforces both by reading the order and counting groomed-ahead "
                       "issues before launching the PM; no script does"):
            self.assertIn(needle, self.step2, needle)

    def test_c3_the_order_is_the_roadmap_list_with_a_trigger_per_entry(self):
        for needle in ("ordered list of the planning roadmap file the docs index names",
                       "`templates/roadmap.md`", "\"Issues or tasks, in order\"",
                       "each entry with its trigger: the issue it must land before, or the event that "
                       "brings it up",
                       "Every filed issue, follow-ups and periodic-review proposals included, is added to that list "
                       "in the same session it is filed, and the human is told where",
                       "An issue outside the list is never groomed"):
            self.assertIn(needle, self.backlog, needle)
        self.assertIn("trigger: <the issue it must land before, or the event that brings it up>", self.roadmap)
        self.assertIn("give its roadmap entry and trigger", self.pm)

    def test_c4_prefix_is_set_by_the_orchestrator_and_never_counted(self):
        for needle in ("It sets a `[groomed]` title prefix once a valid `PM:` hash record matches the body",
                       "removes it when the body changes without a matching record",
                       "counting uses the hash match, never the title, so a stale prefix can't count"):
            self.assertIn(needle, self.step2, needle)
        self.assertIn("the hash covers the body only", self.approved)
        self.assertIn("A title change is reported to the human as a note, not a freeze failure",
                      self.approved)

    def test_c5_groom_first_lines_are_documented(self):
        self.assertIn("Groom first: the PM's comment records `Grooming authorised by: human in session, "
                      "<date>, \"<the request>\"`", self.approved)
        self.assertIn("`Approved by: approved label, seen <date>` and the body hash the label covers",
                      self.approved)
        self.assertIn("`Grooming authorised by: human in session, <date>, \"<the request>\"`", self.pm)
        claim = between(self.comments, "## Claim", "## Release")
        self.assertIn("`Approved by: approved label, seen <date>`, naming the body hash the label covers",
                      claim)

    def test_c6_label_first_means_you_may_groom(self):
        for needle in ("Label first: `approved` on an issue with no matching `PM:` hash record means "
                       "only \"you may groom\"",
                       "`Grooming authorised by: approved label (seen <date>)`",
                       "the orchestrator asks the human to review the groomed body",
                       "`Approved by: human confirmation in session, <date>` and the new hash; "
                       "the label stays",
                       "A label alone never approves a body it was added before (a token can add labels, "
                       "`environments/local-sandbox/README.md`)"):
            self.assertIn(needle, self.approved, needle)
        self.assertIn("`Grooming authorised by: approved label (seen <date>)`", self.pm)
        confirm = between(self.comments, "## Confirm", "## Ruling")
        self.assertIn("`Approved by: human confirmation in session, <date>` and the new hash; "
                      "the label stays", confirm)
        self.assertTrue((KIT / "environments" / "local-sandbox" / "README.md").exists())

    def test_c7_a_groomed_ahead_issue_is_rechecked_before_its_claim(self):
        for needle in ("is re-checked before its Claim",
                       "reads `git diff --stat <sha>..HEAD`",
                       "the `Groomed at:` line of the PM's comment",
                       "for the paths in the issue's Files list",
                       "the PM re-checks the body in a short launch",
                       "`PM: re-check at <sha>: unchanged`",
                       "or a revised body that goes through Confirm"):
            self.assertIn(needle, self.step2, needle)
        self.assertIn("`Groomed at: <short sha of main>`", self.pm)
        self.assertIn("post `PM: re-check at <sha>: unchanged`, or a revised body for Confirm", self.pm)

    def test_c8_changelog_entry_and_customizing(self):
        entry = between(self.changelog, "- **Grooming ahead", "- **Numbered acceptance criteria**")
        for needle in ("`GROOM_AHEAD=0`", "Existing projects:", "Expected word change"):
            self.assertIn(needle, entry, needle)
        self.assertEqual(self.changelog.count("#203"), 1)
        self.assertIn("the setting acts now, and `GROOM_AHEAD=0` keeps that rule", self.customizing)

    def test_decision_record_and_index_row(self):
        record = REPO / "_docs" / "decisions" / "203-groom-ahead.md"
        self.assertTrue(record.exists())
        self.assertIn("_docs/decisions/203-groom-ahead.md", flat(REPO / "_docs" / "index.md"))


if __name__ == "__main__":
    unittest.main()
