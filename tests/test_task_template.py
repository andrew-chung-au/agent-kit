"""Pins the section order of the issue task template (issue #30)."""
from __future__ import annotations

import unittest
from pathlib import Path

TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "agent-kit"
    / "templates"
    / "task-template.md"
)
EXPECTED = ["Why", "Goal", "Acceptance criteria", "Out of scope", "Design", "Constraints"]


def headings(text: str) -> list[str]:
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


class TaskTemplateTest(unittest.TestCase):
    def test_sections_in_order_with_why_first(self):
        self.assertEqual(headings(TEMPLATE.read_text(encoding="utf-8")), EXPECTED)

    def test_missing_why_is_refused(self):
        self.assertNotEqual(headings("## Goal\n\n## Constraints\n"), EXPECTED)

    def test_why_below_goal_is_refused(self):
        moved = ["Goal", "Why", "Acceptance criteria", "Out of scope", "Design", "Constraints"]
        self.assertNotEqual(moved, EXPECTED)
        text = "".join(f"## {h}\n\n" for h in moved)
        self.assertNotEqual(headings(text), EXPECTED)

    def test_design_is_optional_between_out_of_scope_and_constraints(self):
        """Issue #160."""
        text = " ".join(TEMPLATE.read_text(encoding="utf-8").split())
        section = text[text.index("## Design"):text.index("## Constraints")]
        for needle in ("Optional", "real design choice", "one line of reason", "linking to an ADR",
                       "None", "Light issue", "typo fix", "also needs a `## Decision record`",
                       "alone does not satisfy that gate"):
            self.assertIn(needle, section, needle)

    def test_the_pm_role_file_explains_when_and_links_to_tiers(self):
        pm = " ".join((TEMPLATE.parent.parent / "team" / "pm.md").read_text(encoding="utf-8").split())
        for needle in ("**Design section:**", "optional", "real design choice", "Heavy",
                       "`## Decision record`", "process.md`, Tiers", "link to the record instead of copying it"):
            self.assertIn(needle, pm, needle)


if __name__ == "__main__":
    unittest.main()
