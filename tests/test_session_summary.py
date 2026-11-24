"""Checks the session-summary template (issue #23) and its Reflection section (#206).

The check takes text and returns a list of problems, so the same function runs
on the real file (must be empty) and on a mutated copy (must not be).

Since #206 reflections are files (`procedures/formats.md`, Reflection): the
summary's Reflection section only names the issue's reflection file.
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
    "_docs/records/reflections/",
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
        self.assertTrue(check_template(self.text.replace("_docs/records/reflections/", "")))

    def test_the_template_no_longer_asks_for_copied_blocks(self):
        # #206: the three questions live in templates/reflection.md, not in the summary.
        self.assertNotIn("What slowed you down", self.text)
        self.assertNotIn("copied unchanged from its issue comment", self.text)


PROCEDURE = REPO / "agent-kit" / "procedures" / "session-summary.md"


def reflection_wording_problems(text: str) -> list:
    """#206 C5: the Reflection section points at the reflection files and asks for no comment."""
    lines = text.splitlines()
    body = []
    if "## Reflection" in lines:
        for line in lines[lines.index("## Reflection") + 1:]:
            if line.startswith("## "):
                break
            body.append(line)
    flat = " ".join(" ".join(body).split())
    problems = []
    if "`procedures/formats.md`, Reflection" not in flat:
        problems.append("the section does not point at formats.md, Reflection")
    if "`_docs/records/reflections/<issue>.md`" not in flat or "`none`" not in flat:
        problems.append("the section does not ask for the reflection file's path or none")
    if re.search(r"(?i)post a new comment|unknown \(role not asked\)", " ".join(text.split())):
        problems.append("the procedure still asks roles for a reflection comment")
    return problems


class ReflectionWordingTest(unittest.TestCase):
    text = PROCEDURE.read_text(encoding="utf-8")

    def test_the_procedure_points_at_the_reflection_files(self):
        self.assertEqual(reflection_wording_problems(self.text), [])

    def test_asking_for_a_comment_again_fails(self):
        mutated = self.text + "\nAfter QA PASS, ask each role to post a new comment.\n"
        self.assertIn("the procedure still asks roles for a reflection comment", reflection_wording_problems(mutated))

    def test_removing_the_path_fails(self):
        mutated = self.text.replace("`_docs/records/reflections/<issue>.md`", "the file")
        self.assertNotEqual(mutated, self.text)
        self.assertNotEqual(reflection_wording_problems(mutated), [])


if __name__ == "__main__":
    unittest.main()
