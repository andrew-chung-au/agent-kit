"""Phrase tests for issue #161: the Spec note layout.

No script is behind this: the roles follow the layout and the human approves every spec change, so the
wording is what has to stay. The refused case (an edit that goes straight into the spec) is enforced by the
existing protected-file rule and commit approval, which these tests only point at. Whitespace is normalised.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
LINK = "Spec note layout of `_docs/agent-kit/procedures/asking-the-human.md`"


def flat(path: Path) -> str:
    return " ".join(path.read_text().split())


class SpecNoteLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = flat(KIT / "procedures" / "asking-the-human.md")
        cls.section = text[text.index("## Spec note"):text.index("If your tool offers multiple-choice")]

    def test_the_layout_has_added_changed_removed_and_why(self):
        for needle in ("Spec note: <what is wrong or missing, in one line>", "- Added: <requirement>",
                       "- Changed: <new text> (was: <old text>)", "- Removed: <requirement>: <reason>",
                       "- Why: <one line"):
            self.assertIn(needle, self.section, needle)

    def test_it_is_optional_for_a_one_line_note_and_never_merges_automatically(self):
        self.assertIn("A one-line note may skip the layout", self.section)
        self.assertIn("Nothing is merged into the spec automatically", self.section)
        self.assertIn("the human decides, and only then is `_docs/specs.md` changed", self.section)

    def test_the_layout_is_defined_once_and_the_role_files_link_to_it(self):
        for rel in ("team/pm.md", "team/software-engineer.md", "process.md"):
            with self.subTest(file=rel):
                text = flat(KIT / rel)
                self.assertIn(LINK, text)
                self.assertNotIn("- Removed: <requirement>", text)
                self.assertNotIn("(was: <old text>)", text)

    def test_planning_says_nothing_is_merged_automatically(self):
        process = flat(KIT / "process.md")
        planning = process[process.index("## Planning"):process.index("## Backlog")]
        self.assertIn("Nothing is merged into the spec automatically", planning)
        self.assertIn("approved by the human first", planning)

    def test_the_spec_stays_protected(self):
        self.assertIn("'_docs/specs.md'", (REPO / "agent-kit.conf").read_text())

    def test_the_decision_record_and_index_row_exist(self):
        self.assertTrue((REPO / "_docs" / "decisions" / "161-spec-note-layout.md").exists())
        self.assertIn("_docs/decisions/161-spec-note-layout.md", flat(REPO / "_docs" / "index.md"))


if __name__ == "__main__":
    unittest.main()
