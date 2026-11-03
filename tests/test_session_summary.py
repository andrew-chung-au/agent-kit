"""Checks the session-summary template (issue #23).

The check takes text and returns a list of problems, so the same function runs
on the real file (must be empty) and on a mutated copy (must not be).
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parent.parent
TEMPLATE = REPO / "agent-kit" / "templates" / "session-summary.md"
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


PROCEDURE = REPO / "agent-kit" / "procedures" / "session-summary.md"
ROLE_PREFIX = re.compile(r"starting with its role prefix \(such as `QA:`\) and ending in a `Reflection:` block")


def reflection_wording_problems(text: str) -> list:
    """#63 C: the reflection comment keeps the role prefix the wrapper needs; Reflection: is a block."""
    flat = " ".join(text.split())
    problems = []
    if not ROLE_PREFIX.search(flat):
        problems.append("the reflection comment does not say it starts with the role prefix")
    if re.search(r"starting with `Reflection:`|`Reflection:` prefix", flat):
        problems.append("Reflection: is described as a first-line prefix")
    return problems


class ReflectionWordingTest(unittest.TestCase):
    text = PROCEDURE.read_text(encoding="utf-8")

    def test_the_procedure_names_the_role_prefix_and_the_reflection_block(self):
        self.assertEqual(reflection_wording_problems(self.text), [])

    def test_removing_the_prefix_sentence_fails(self):
        mutated = self.text.replace("starting with its role prefix (such as `QA:`) and ", "")
        self.assertNotEqual(mutated, self.text)
        self.assertIn("the reflection comment does not say it starts with the role prefix",
                      reflection_wording_problems(mutated))

    def test_describing_reflection_as_the_prefix_fails(self):
        mutated = self.text.replace("starting with its role prefix (such as `QA:`)", "starting with `Reflection:`")
        self.assertNotEqual(reflection_wording_problems(mutated), [])


if __name__ == "__main__":
    unittest.main()
