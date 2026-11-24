"""Reflections written to files (issue #206).

The template `agent-kit/templates/reflection.md` holds one reflection: a heading
`### <role>, <UTC time YYYY-MM-DDTHH:MMZ>`, then the lines `Slowed:`, `Nearly:` and
`Change:`, or the single line `Nothing to report.`. Every role writes one to
`.scratch/reflection-<issue>-<role>.md` before its role return (`procedures/formats.md`,
Reflection), and the orchestrator appends it unchanged to `_docs/records/reflections/<issue>.md`
(`process.md`, Reading a return).

The checks take text and return a list of problems, so the same function runs on the
real file (must be empty) and on a mutated copy (must not be). The refused case that a
script enforces, QA writing to `_docs/records/reflections/`, is shown on a fixture repo:
`assert-clean.sh` exits 1.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from kit_repo import KitTestCase

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
TEMPLATE = KIT / "templates" / "reflection.md"
FORMATS = KIT / "procedures" / "formats.md"
PROCESS = KIT / "process.md"

TEMPLATE_HEADING = "### <role>, <UTC time YYYY-MM-DDTHH:MMZ>"
LABELS = ("Slowed: ", "Nearly: ", "Change: ")
NOTHING = "Nothing to report."
HEADING = re.compile(r"^### (pm|engineer|qa), \d{4}-\d\d-\d\dT\d\d:\d\dZ$")


def flat(text: str) -> str:
    return " ".join(text.split())


def section(text: str, heading: str) -> str:
    """The body of a `## ` section of a Markdown doc, up to the next `## ` heading."""
    lines = text.splitlines()
    if heading not in lines:
        return ""
    body = []
    for line in lines[lines.index(heading) + 1:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def check_template(text: str) -> list[str]:
    """The template's heading form, its three labels in order right after it, and the
    nothing-to-report line."""
    lines = text.splitlines()
    if TEMPLATE_HEADING not in lines:
        return [f"missing heading {TEMPLATE_HEADING!r}"]
    after = [line for line in lines[lines.index(TEMPLATE_HEADING) + 1:] if line.strip()]
    problems = []
    for i, label in enumerate(LABELS):
        if i >= len(after) or not after[i].startswith(label):
            problems.append(f"line {i + 1} after the heading does not start {label!r}")
    if len(after) > len(LABELS):
        problems.append("text after the three lines")
    if f"`{NOTHING}`" not in text:
        problems.append(f"the template does not name the line {NOTHING!r}")
    return problems


def check_reflection(text: str) -> list[str]:
    """One written reflection: a heading with a role and a UTC time, then either the three
    labelled lines (line rule: label from column 1, one space, a value) or `Nothing to report.`."""
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines or not HEADING.match(lines[0]):
        return ["the first line is not `### <pm|engineer|qa>, <YYYY-MM-DDTHH:MMZ>`"]
    body = lines[1:]
    if body == [NOTHING]:
        return []
    if len(body) != len(LABELS):
        return [f"expected three lines or {NOTHING!r}, got {len(body)} lines"]
    return [f"line {i + 2} is not {label!r} with a value" for i, (label, line) in enumerate(zip(LABELS, body))
            if not line.startswith(label) or not line[len(label):].strip() or line[len(label)] == " "]


def formats_example() -> str:
    for block in re.findall(r"```\n(.*?)```", FORMATS.read_text(encoding="utf-8"), re.S):
        if block.startswith("### "):
            return block
    raise AssertionError("formats.md has no reflection example")


class TemplateTest(unittest.TestCase):
    text = TEMPLATE.read_text(encoding="utf-8")

    def test_real_template_passes(self):
        self.assertEqual(check_template(self.text), [])

    def test_removing_the_heading_or_a_label_fails(self):
        for old in (TEMPLATE_HEADING, "Slowed: ", "Nearly: ", "Change: ", f"`{NOTHING}`"):
            with self.subTest(removed=old):
                mutated = self.text.replace(old, "")
                self.assertNotEqual(mutated, self.text)
                self.assertTrue(check_template(mutated))

    def test_a_changed_heading_form_fails(self):
        mutated = self.text.replace(TEMPLATE_HEADING, "### <Role> (<date>)")
        self.assertTrue(check_template(mutated))

    def test_labels_out_of_order_fail(self):
        mutated = self.text.replace("Slowed: ", "@@").replace("Nearly: ", "Slowed: ").replace("@@", "Nearly: ")
        self.assertTrue(check_template(mutated))


class WrittenReflectionTest(unittest.TestCase):
    good = "### engineer, 2026-11-24T01:04Z\n\nSlowed: a.\nNearly: b.\nChange: c.\n"

    def test_the_formats_example_and_a_filled_template_pass(self):
        self.assertEqual(check_reflection(formats_example()), [])
        self.assertEqual(check_reflection(self.good), [])

    def test_nothing_to_report_passes(self):
        self.assertEqual(check_reflection(f"### pm, 2026-11-24T01:04Z\n\n{NOTHING}\n"), [])

    def test_refused_shapes(self):
        cases = {
            "unknown role": self.good.replace("engineer", "orchestrator"),
            "date without time": self.good.replace("2026-11-24T01:04Z", "2026-11-24"),
            "missing label": self.good.replace("Nearly: b.\n", ""),
            "empty value": self.good.replace("Change: c.", "Change:"),
            "indented label": self.good.replace("Slowed: ", " Slowed: "),
            "two spaces": self.good.replace("Slowed: ", "Slowed:  "),
            "nothing plus lines": self.good + NOTHING + "\n",
            "no heading": "Slowed: a.\nNearly: b.\nChange: c.\n",
        }
        for name, text in cases.items():
            with self.subTest(case=name):
                self.assertTrue(check_reflection(text), text)


class FormatsDocTest(unittest.TestCase):
    text = FORMATS.read_text(encoding="utf-8")

    def test_reflection_section_is_defined_once_in_formats(self):
        self.assertEqual(self.text.splitlines().count("## Reflection"), 1)
        body = flat(section(self.text, "## Reflection"))
        for phrase in ("`.scratch/reflection-<issue>-<role>.md`", "`_docs/agent-kit/templates/reflection.md`",
                       "`### <role>, <UTC time YYYY-MM-DDTHH:MMZ>`", "`Slowed:`", "`Nearly:`", "`Change:`",
                       f"`{NOTHING}`", "`_docs/records/reflections/<issue>.md`", "append-only",
                       "an earlier section is never edited or removed",
                       "the orchestrator writes no reflection text of its own",
                       "A reflection posted as an issue comment",
                       "QA writing to `_docs/records/reflections/` itself: **Assert clean** fails",
                       "`procedures/sweep.md`, step 2"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_role_return_section_asks_every_role_for_the_file(self):
        body = flat(section(self.text, "## Role return"))
        self.assertIn("Before that message, every role (PM, Engineer, QA) writes its reflection for the launch to "
                      "`.scratch/reflection-<issue>-<role>.md`", body)
        self.assertIn("the ten lines don't change", body)
        self.assertIn("A launch that stops early may leave none.", body)

    def test_the_labels_live_only_in_formats_and_the_template(self):
        # CHANGELOG.md names the labels as history, not as a definition.
        holders = sorted(str(p.relative_to(KIT)) for p in KIT.rglob("*.md") if p.name != "CHANGELOG.md"
                         if "`Slowed:`" in p.read_text(encoding="utf-8", errors="ignore")
                         or "\nSlowed: " in p.read_text(encoding="utf-8", errors="ignore"))
        self.assertEqual(holders, ["procedures/formats.md", "templates/reflection.md"])

    def test_role_files_are_unchanged_by_the_rule(self):
        # The rule lives in formats.md only (D-206-1 q3); no team/ file repeats it.
        for path in (KIT / "team").glob("*.md"):
            with self.subTest(path=path.name):
                self.assertNotIn("reflection-<issue>", path.read_text(encoding="utf-8"))


class ProcessDocTest(unittest.TestCase):
    def paragraph(self, text):
        return next(line for line in text.splitlines() if line.startswith("**Reading a return.**"))

    def test_reading_a_return_says_what_happens_to_the_file(self):
        para = self.paragraph(PROCESS.read_text(encoding="utf-8"))
        for phrase in ("append that launch's `.scratch/reflection-<issue>-<role>.md` unchanged to "
                       "`_docs/records/reflections/<issue>.md`",
                       "commit that file on its own, naming its explicit path",
                       "before you launch the next role, so **Assert clean** still sees a clean tree",
                       "After a QA launch, do this only after **Assert clean** and the HEAD check of Lifecycle step 5",
                       "The file is append-only: never edit or remove an earlier section",
                       "never write reflection text of your own",
                       "When the launch left no reflection file", "append nothing"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, para)

    def test_the_paragraph_does_not_name_the_periodic_review(self):
        # tests/test_sweep.py allows one process.md line with that word, in step 7.
        self.assertNotIn("sweep", self.paragraph(PROCESS.read_text(encoding="utf-8")))


class AssertCleanRefusesQaReflectionTest(KitTestCase):
    """C4: QA writing to `_docs/records/reflections/` fails Assert clean, while its own
    `.scratch/` reflection file (git-ignored) does not."""

    SCRIPT = "agent-kit/scripts/assert-clean.sh"

    def setUp(self):
        super().setUp()
        self.add_project()
        self.write(".gitignore", ".scratch/\n")
        self.write("README.md", "fixture\n")
        self.commit_all("base")

    def check(self):
        return self.run_cmd(["bash", self.SCRIPT])

    def test_an_untracked_reflection_file_fails(self):
        self.write("_docs/records/reflections/1.md", "### qa, 2026-11-24T01:04Z\n\nNothing to report.\n")
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: FAIL", r.stdout)
        self.assertIn("_docs/records/reflections/1.md", r.stdout)

    def test_appending_to_a_committed_reflection_file_fails(self):
        path = self.write("_docs/records/reflections/1.md", "### engineer, 2026-11-24T01:00Z\n\nNothing to report.\n")
        self.commit_all("orchestrator appends the engineer's reflection")
        path.write_text(path.read_text() + "\n### qa, 2026-11-24T01:04Z\n\nNothing to report.\n")
        r = self.check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("_docs/records/reflections/1.md", r.stdout)

    def test_the_scratch_reflection_file_passes(self):
        self.write(".scratch/reflection-1-qa.md", "### qa, 2026-11-24T01:04Z\n\nNothing to report.\n")
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
