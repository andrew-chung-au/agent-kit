"""Checks the session-summary template (issue #23).

The check takes text and returns a list of problems, so the same function runs
on the real file (must be empty) and on a mutated copy (must not be).
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

TEMPLATE = Path(__file__).resolve().parent.parent / "agent-kit" / "templates" / "session-summary.md"
HEADINGS = ["## Reflection", "## Launch usage"]
PROMPTS = [
    "What slowed you down",
    "What nearly went wrong or was blocked",
    "One proposed change",
]


def check_template(text: str) -> list[str]:
    lines = text.splitlines()
    problems = [f"missing heading {h}" for h in HEADINGS if h not in lines]
    if "## Reflection" in lines:
        body = []
        for line in lines[lines.index("## Reflection") + 1:]:
            if line.startswith("## "):
                break
            body.append(line)
        reflection = "\n".join(body)
        problems += [f"missing prompt {p!r}" for p in PROMPTS if p not in reflection]
    return problems


class TemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_real_template_passes(self):
        self.assertEqual(check_template(self.text), [])

    def test_deleted_heading_or_label_fails(self):
        self.assertTrue(check_template(self.text.replace("## Launch usage", "")))
        self.assertTrue(check_template(self.text.replace("## Reflection", "")))
        self.assertTrue(check_template(self.text.replace("One proposed change", "")))


if __name__ == "__main__":
    unittest.main()
