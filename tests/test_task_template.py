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
EXPECTED = ["Why", "Goal", "Acceptance criteria", "Out of scope", "Constraints"]


def headings(text: str) -> list[str]:
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


class TaskTemplateTest(unittest.TestCase):
    def test_sections_in_order_with_why_first(self):
        self.assertEqual(headings(TEMPLATE.read_text(encoding="utf-8")), EXPECTED)

    def test_missing_why_is_refused(self):
        self.assertNotEqual(headings("## Goal\n\n## Constraints\n"), EXPECTED)

    def test_why_below_goal_is_refused(self):
        moved = ["Goal", "Why", "Acceptance criteria", "Out of scope", "Constraints"]
        self.assertNotEqual(moved, EXPECTED)
        text = "".join(f"## {h}\n\n" for h in moved)
        self.assertNotEqual(headings(text), EXPECTED)


if __name__ == "__main__":
    unittest.main()
