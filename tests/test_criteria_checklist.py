"""Doc test for issue #201: the Engineer's criteria list is defined once in formats.md and the
role files point to it. No script reads the list, so the wording is what has to stay.
Whitespace is normalised.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KIT = REPO / "agent-kit"

FORMS = ("C<n>: done (<evidence>)", "C<n>: not done", "C<n>: not checked (<reason>)",
         "C<n>: challenged (<reason>)")


def flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class CriteriaChecklistTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.formats = flat(KIT / "procedures" / "formats.md")
        cls.section = cls.formats[cls.formats.index("## Criteria list"):cls.formats.index("## Finding")]
        cls.engineer = flat(KIT / "team" / "software-engineer.md")
        cls.qa = flat(KIT / "team" / "qa-engineer.md")
        cls.pm = flat(KIT / "team" / "pm.md")
        cls.planning = flat(KIT / "procedures" / "planning.md")

    def test_formats_names_each_form_once(self):
        for form in FORMS:
            with self.subTest(form=form):
                self.assertEqual(self.formats.count(form), 1)
                self.assertIn(form, self.section)

    def test_formats_says_evidence_and_that_no_script_reads_it(self):
        for needle in ("Evidence names a test, a command and its result, or a file",
                       "No script reads the list"):
            self.assertIn(needle, self.section)

    def test_role_files_do_not_restate_the_forms(self):
        for name, text in (("engineer", self.engineer), ("qa", self.qa), ("pm", self.pm)):
            for form in FORMS:
                with self.subTest(role=name, form=form):
                    self.assertNotIn(form, text)

    def test_engineer_points_to_the_list_and_requires_it(self):
        for needle in ("`Criteria list`", "procedures/formats.md", "`done` with no evidence",
                       "your omission", "`challenged`"):
            self.assertIn(needle, self.engineer, needle)
        done = self.engineer[self.engineer.index("**Definition of done:**"):self.engineer.index("## Fix rounds")]
        self.assertIn("`Criteria list`", done)

    def test_qa_reads_the_list_first_and_names_disagreement(self):
        for needle in ("then the Engineer's `Criteria list`", "whatever the list says",
                       "keeps the ids and order of the Engineer's list", "that you fail",
                       "wording is `Category: criterion`", "`not done` or `not checked`",
                       "no amend or ruling on the issue", "`Criterion: none`"):
            self.assertIn(needle, self.qa, needle)

    def test_pm_check_line_and_plan_review_item(self):
        self.assertIn("so QA can run or read it without asking the PM", self.pm)
        review = self.planning[self.planning.index("## Plan review"):]
        self.assertIn("can be run or read without asking the PM", review)


if __name__ == "__main__":
    unittest.main()
