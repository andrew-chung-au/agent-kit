"""Structural checks for the kit's GitHub issue intake form (issue #45).

The Python standard library has no YAML parser, so this checks the form as
text, line by line. It proves the structure the issue pins and that the form
cannot apply a label (only the human labels issues). That GitHub accepts the
form is not checked here: it is seen by hand on a repository's "New issue" page.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORM = ROOT / "agent-kit" / "templates" / "github" / "ISSUE_TEMPLATE" / "intake.yml"
TASK_TEMPLATE = ROOT / "agent-kit" / "templates" / "task-template.md"

MAX_LINES = 60
MAX_WORDS = 250
FORBIDDEN_KEYS = ("labels", "assignees", "projects", "title")
EXPECTED_TYPES = ["markdown", "textarea", "textarea", "textarea"]
EXPECTED_IDS = ["problem", "expected", "evidence"]
EXPECTED_LABELS = [
    "What is wrong or missing",
    "What you expected",
    "Evidence: commands, output, links",
]
EXPECTED_REQUIRED = [True, True, False]
WARNING_WORDS = ["public", "tokens", "passwords", "keys", "env", "redact"]


def groomed_sections(text: str) -> list[str]:
    return [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]


def check(text: str, groomed: list[str]) -> list[str]:
    """Return the problems found in the form text; empty means it passes."""
    errors: list[str] = []
    lines = text.splitlines()
    if "\t" in text:
        errors.append("tab character")
    top = [m.group(1) for l in lines if (m := re.match(r"^([A-Za-z_]\w*):", l))]
    if top != ["name", "description", "body"]:
        errors.append("top-level keys are %r" % top)
    for l in lines:
        m = re.match(r"^\s*(?:-\s+)?([A-Za-z_]\w*):", l)
        if m and m.group(1) in FORBIDDEN_KEYS:
            errors.append("forbidden key %s" % m.group(1))
    if re.search(r"approved", text, re.IGNORECASE):
        errors.append("the word approved appears")
    # Split the body into elements at each "  - type:" line.
    elements: list[list[str]] = []
    for l in lines:
        if re.match(r"^  - type:", l):
            elements.append([l])
        elif elements:
            elements[-1].append(l)
    types = [re.sub(r"^  - type:\s*", "", e[0]).strip() for e in elements]
    for t in types:
        if t not in ("markdown", "textarea"):
            errors.append("unknown element type %s" % t)
    if types != EXPECTED_TYPES:
        errors.append("element types are %r" % types)
        return errors
    ids = [m.group(1) for e in elements for l in e if (m := re.match(r"^    id:\s*(\S+)\s*$", l))]
    if len(set(ids)) != len(ids):
        errors.append("duplicate id")
    if ids != EXPECTED_IDS:
        errors.append("ids are %r" % ids)
    warning = "\n".join(elements[0]).lower()
    for w in WARNING_WORDS:
        if w not in warning:
            errors.append("warning lacks %r" % w)
    labels, required = [], []
    for e in elements[1:]:
        body = "\n".join(e)
        m = re.search(r'^      label:\s*"?(.*?)"?\s*$', body, re.MULTILINE)
        labels.append(m.group(1) if m else None)
        required.append(bool(re.search(r"^      required:\s*true\s*$", body, re.MULTILINE)))
    if labels != EXPECTED_LABELS:
        errors.append("labels are %r" % labels)
    if required != EXPECTED_REQUIRED:
        errors.append("required flags are %r" % required)
    for lab in labels:
        for section in groomed:
            if lab and section.lower() in lab.lower():
                errors.append("label copies groomed section %s" % section)
    return errors


class IntakeFormTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = FORM.read_text(encoding="utf-8")
        cls.groomed = groomed_sections(TASK_TEMPLATE.read_text(encoding="utf-8"))

    def test_groomed_sections_are_read(self):
        self.assertEqual(
            self.groomed, ["Why", "Goal", "Acceptance criteria", "Out of scope", "Design", "Constraints"]
        )

    def test_form_passes(self):
        self.assertEqual(check(self.text, self.groomed), [])

    def test_form_is_small(self):
        self.assertLessEqual(len(self.text.splitlines()), MAX_LINES)
        self.assertLessEqual(len(self.text.split()), MAX_WORDS)

    def test_installed_form_equals_template(self):
        installed = ROOT / ".github" / "ISSUE_TEMPLATE" / "intake.yml"
        self.assertEqual(installed.read_bytes(), FORM.read_bytes())

    def test_bad_copies_each_fail(self):
        good = self.text
        bad = {
            "labels approved": good.replace("body:\n", "labels: [approved]\nbody:\n", 1),
            "assignees key": good.replace("body:\n", "assignees: [someone]\nbody:\n", 1),
            "duplicate id": good.replace("id: expected", "id: problem"),
            "tab character": good.replace("    id: problem", "\tid: problem"),
            "no body key": good.replace("body:\n", "", 1),
            "required made optional": good.replace("required: true", "required: false", 1),
            "unknown element type": good.replace("type: textarea", "type: dropdown", 1),
            "title key": good.replace("body:\n", "title: x\nbody:\n", 1),
            "copies a groomed label": good.replace("What you expected", "Goal"),
            "no public warning": good.replace("This issue is public", "Hello"),
        }
        for name, text in bad.items():
            with self.subTest(name):
                self.assertNotEqual(text, good, "fixture did not change the form")
                self.assertNotEqual(check(text, self.groomed), [])


if __name__ == "__main__":
    unittest.main()
