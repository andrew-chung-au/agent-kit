"""Doc test for issue #202: the standard template, the docs index row and the role files' pointers to
the `Standards:` line. No script reads the line, so the wording is what has to stay.
Whitespace is normalised.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"
TEMPLATE = KIT / "templates" / "standard.md"

WORD_CAP = 120
LABELS = ["Rule", "Why", "When it applies", "Check", "Added by"]


def flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def labels(text: str) -> list[str]:
    return re.findall(r"(?m)^- \*\*([^*]+):\*\*", text)


def within_cap(text: str, cap: int = WORD_CAP) -> bool:
    return len(text.split()) <= cap


class StandardTemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = TEMPLATE.read_text(encoding="utf-8")

    def test_title_and_headings_in_order(self):
        self.assertTrue(self.text.startswith("# Standard: "))
        self.assertEqual(labels(self.text), LABELS)

    def test_template_states_the_cap_the_test_pins(self):
        self.assertIn(f"at most {WORD_CAP} words", " ".join(self.text.split()))

    def test_template_itself_is_within_the_cap(self):
        self.assertTrue(within_cap(self.text), len(self.text.split()))

    def test_check_is_a_make_target_or_read(self):
        check = next(line for line in self.text.splitlines() if line.startswith("- **Check:**"))
        for needle in ("`make` target", "`read <file>`", "not mechanical"):
            self.assertIn(needle, check, needle)

    def test_a_standard_over_the_cap_is_refused(self):
        self.assertTrue(within_cap("word " * WORD_CAP))
        self.assertFalse(within_cap("word " * (WORD_CAP + 1)))

    def test_template_points_to_the_standards_line(self):
        self.assertIn("`Standards:` line", " ".join(self.text.split()))


class RegisterTest(unittest.TestCase):
    def test_docs_index_template_has_the_standard_row(self):
        rows = [line for line in (KIT / "templates" / "docs-index.md").read_text(encoding="utf-8").splitlines()
                if line.startswith("| Standard ")]
        self.assertEqual(len(rows), 1)
        cells = [cell.strip() for cell in rows[0].strip("|").split("|")]
        self.assertIn("added when the first standard exists", cells[0])
        self.assertEqual(cells[1:4], ["`_docs/standards/`", "`templates/standard.md`", "`<slug>.md`"])

    def test_this_repos_index_has_no_standard_row_until_its_first_standard(self):
        standards = REPO / "_docs" / "standards"
        has_row = any(line.startswith("| Standard ")
                      for line in (REPO / "_docs" / "index.md").read_text(encoding="utf-8").splitlines())
        self.assertEqual(has_row, standards.is_dir())


class RolePointersTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.formats = flat(KIT / "procedures" / "formats.md")
        cls.engineer = flat(KIT / "team" / "software-engineer.md")
        cls.qa = flat(KIT / "team" / "qa-engineer.md")
        cls.pm = flat(KIT / "team" / "pm.md")

    def test_each_points_to_the_standards_line(self):
        for name, text in (("formats", self.formats), ("engineer", self.engineer), ("qa", self.qa),
                           ("pm", self.pm)):
            with self.subTest(file=name):
                self.assertIn("`Standards:` line", text)

    def test_formats_scope_says_what_lists_means(self):
        self.assertIn("a standard on its `Standards:` line", self.formats)

    def test_engineer_reads_each_listed_standard_before_building(self):
        for needle in ("Read each standard on the issue's `Standards:` line", "before building"):
            self.assertIn(needle, self.engineer, needle)

    def test_qa_runs_checks_and_grades_breaches(self):
        for needle in ("Run the check of each standard on the issue's `Standards:` line",
                       "read the file where its check is `read`", "in every launch and re-check",
                       "`Category: standard` and `Scope: in`", "doesn't list is `Scope: out`"):
            self.assertIn(needle, self.qa, needle)

    def test_pm_lists_matching_standards_and_handles_a_mid_project_one(self):
        for needle in ("whose \"when it applies\" matches the issue, or `none`",
                       "applies to issues groomed after it", "only by Confirm",
                       "one unlabelled audit issue"):
            self.assertIn(needle, self.pm, needle)


if __name__ == "__main__":
    unittest.main()
