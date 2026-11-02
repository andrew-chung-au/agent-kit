"""Phrase tests for issue #37: the Heavy tier's gates and QA's code-review checklist.

These pin the wording in agent-kit/process.md, team/qa-engineer.md, team/pm.md and
blueprints.md. There is no script behind the gates: the orchestrator's hash check and
the human's reading enforce them, so the wording is what has to stay. Whitespace is
normalised, so line wrapping does not matter.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"


def flat(path: Path) -> str:
    return " ".join(path.read_text().split())


class ProcessHeavyGatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = flat(KIT / "process.md")
        cls.tiers = cls.text[cls.text.index("## Tiers"):cls.text.index("## Lifecycle")]

    def test_placeholders_are_gone(self):
        self.assertNotIn("Heavy before its gates exist", self.text)
        self.assertNotIn("Extra gates: none yet", self.text)
        self.assertNotIn("Heavy currently adds no gate", self.text)

    def test_adr_before_the_engineer(self):
        for phrase in ["adds a `## Decision record` section to the issue body",
                       "`_docs/agent-kit/templates/adr.md`",
                       "the human's `approved` message names that section",
                       "If the human rejects or changes the ADR, the issue returns to the PM "
                       "and the Engineer does not start",
                       "an edit after approval follows Approved text"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.tiers)

    def test_changed_adr_is_refused(self):
        for phrase in ["The orchestrator's hash check before the Engineer launches is the only "
                       "enforcement (no script)",
                       "an ADR that differs from the approved hash does not count"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.tiers)

    def test_second_qa_launch_is_fresh(self):
        for phrase in ["After the first QA PASS",
                       "launches QA again as a fresh launch, never a resumed one",
                       "shared context defeats an independent review",
                       "limits it to the Code review checklist",
                       "A resumed second launch is discarded and run again",
                       "If it posts FAIL, the issue goes back to the Engineer like any QA FAIL"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.tiers)

    def test_done_only_after_both_pass(self):
        self.assertIn("The issue is done only when both launches have posted PASS", self.tiers)
        self.assertIn("QA has posted PASS (for Heavy, both launches)", self.text)

    def test_tier_is_never_lowered_by_an_agent(self):
        self.assertIn("An agent never lowers a Heavy issue to Standard or Light; "
                      "only the human's changed label does", self.tiers)
        self.assertIn("Lowering needs the human to change the label", self.tiers)

    def test_heavy_row_names_the_gates(self):
        self.assertIn("| Heavy | The Standard path | An approved ADR before the Engineer starts; "
                      "a second QA launch", self.tiers)


class QaCodeReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = flat(KIT / "team" / "qa-engineer.md")

    def test_checklist_items(self):
        review = self.text[self.text.index("## Code review"):self.text.index("Post the verdict")]
        for item in ["Bugs:", "Security:", "Tests weakened, skipped or deleted",
                     "Changes outside the issue's Constraints", "Docs the change made out of date"]:
            with self.subTest(item=item):
                self.assertIn(item, review)
        self.assertLess(len(review.split()), 150)

    def test_used_by_standard_and_heavy_second_launch(self):
        self.assertIn("every Standard QA launch", self.text)
        self.assertIn("a second, fresh launch does only this", self.text)
        self.assertIn("You change nothing in either launch", self.text)

    def test_layout_has_a_code_review_block(self):
        layout = self.text[self.text.index("Post the verdict"):self.text.index("Definition of done")]
        self.assertIn("Code review - Bugs / Security", layout)
        self.assertIn('or "not requested"', layout)
        self.assertLess(layout.index("Code review"), layout.index("Outside the criteria"))

    def test_nothing_changed_rule_kept(self):
        self.assertIn("Nothing in the repository was changed", self.text)


class OtherFilesTest(unittest.TestCase):
    def test_pm_drafts_the_adr_in_the_body(self):
        text = flat(KIT / "team" / "pm.md")
        self.assertIn("add a `## Decision record` section to the body", text)
        self.assertIn("the Engineer does not start until the human has approved it", text)

    def test_blueprints_says_when_and_where(self):
        text = flat(KIT / "blueprints.md")
        self.assertIn("every `tier:heavy` issue (its ADR; one row per ADR in the docs index)", text)

    def test_no_new_role_file(self):
        for folder in ("team", "claude-code/agents", "opencode/agents"):
            names = sorted(p.name for p in (KIT / folder).glob("*.md"))
            with self.subTest(folder=folder):
                self.assertFalse(any(n.startswith(("architect", "reviewer")) for n in names), names)


if __name__ == "__main__":
    unittest.main()
