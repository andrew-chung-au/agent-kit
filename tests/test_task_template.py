"""Pins the section order of the issue task template (issue #30) and its criteria format (issue #196)."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

TEMPLATE = (
    Path(__file__).resolve().parent.parent
    / "agent-kit"
    / "templates"
    / "task-template.md"
)
EXPECTED = ["Why", "Goal", "Acceptance criteria", "Out of scope", "Design", "Constraints"]

CRITERION = re.compile(r"- \[ \] C([1-9][0-9]*)\. \S.*")
CHECK = re.compile(r"  Check: \S.*")


def headings(text: str) -> list[str]:
    return [line[3:].strip() for line in text.splitlines() if line.startswith("## ")]


def criteria_section(text: str) -> list[str]:
    lines = text.splitlines()
    start = lines.index("## Acceptance criteria") + 1
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start:end]


def criteria_ids(lines: list[str]) -> list[int]:
    """The criterion ids in order; ValueError for a criterion with no id, a repeated id or no Check: line.

    Gaps are allowed (a removed criterion keeps its number free); the template itself
    is checked separately for C1, C2, C3 in order.
    """
    ids = []
    for index, line in enumerate(lines):
        if not line.startswith("- ["):
            continue
        match = CRITERION.fullmatch(line)
        if match is None:
            raise ValueError(f"criterion without an id: {line!r}")
        number = int(match.group(1))
        if number in ids:
            raise ValueError(f"repeated id C{number}")
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if not CHECK.fullmatch(following):
            raise ValueError(f"C{number} has no Check: line")
        ids.append(number)
    return ids


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
        for needle in ("**Design section:**", "optional", "real design choice", "Heavy rule",
                       "`## Decision record`", "process.md` (Tiers)", "link to the record instead of copying it"):
            self.assertIn(needle, pm, needle)
        # The Tiers row is linked, not paraphrased.
        self.assertNotIn("security boundary", pm.split("**Design section:**")[1].split("If something does not belong")[0])


class StandardsLineTest(unittest.TestCase):
    """Issue #202, C1: a column-1 Standards: line in Constraints, with a none form."""

    def constraints(self) -> list[str]:
        lines = TEMPLATE.read_text(encoding="utf-8").splitlines()
        return lines[lines.index("## Constraints") + 1:]

    def test_template_has_the_standards_line_at_column_1_in_constraints(self):
        found = [line for line in self.constraints() if line.startswith("Standards: ")]
        self.assertEqual(len(found), 1)

    def test_template_line_names_files_and_the_none_form(self):
        line = next(line for line in self.constraints() if line.startswith("Standards: "))
        for needle in ("`_docs/standards/`", "`human-steps.md, commit-style.md`", "or `none`"):
            self.assertIn(needle, line, needle)

    def test_an_indented_standards_line_is_not_at_column_1(self):
        self.assertFalse("  Standards: none".startswith("Standards: "))

    def test_the_pm_definition_of_done_returns_a_body_without_the_line(self):
        pm = " ".join((TEMPLATE.parent.parent / "team" / "pm.md").read_text(encoding="utf-8").split())
        done = pm.split("**Definition of done:**")[1].split("**Design section:**")[0]
        for needle in ("`Standards:` line", "or `none`", "returned to you", "no script reads it"):
            self.assertIn(needle, done, needle)


class CriteriaFormatTest(unittest.TestCase):
    """Issue #196, C3: numbered criteria, each with a Check: line."""

    def test_template_criteria_are_c1_c2_c3_each_with_a_check_line(self):
        lines = criteria_section(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(criteria_ids(lines), [1, 2, 3])
        self.assertEqual(sum(1 for line in lines if line.startswith("- [")), 3)

    def test_template_states_the_id_keeps_rule(self):
        text = " ".join(TEMPLATE.read_text(encoding="utf-8").split())
        for needle in ("`C1`, `C2`", "`Check:` line", "keeps its id", "leaves a gap", "next unused number"):
            self.assertIn(needle, text, needle)

    def test_a_criterion_with_no_id_is_refused(self):
        with self.assertRaisesRegex(ValueError, "without an id"):
            criteria_ids(["- [ ] C1. First", "  Check: test_a", "- [ ] Second", "  Check: test_b"])

    def test_a_repeated_id_is_refused(self):
        with self.assertRaisesRegex(ValueError, "repeated id C1"):
            criteria_ids(["- [ ] C1. First", "  Check: test_a", "- [ ] C1. Second", "  Check: test_b"])

    def test_a_criterion_with_no_check_line_is_refused(self):
        with self.assertRaisesRegex(ValueError, "C2 has no Check: line"):
            criteria_ids(["- [ ] C1. First", "  Check: test_a", "- [ ] C2. Second", "", "- [ ] C3. Third",
                          "  Check: test_c"])

    def test_a_gap_after_a_removed_criterion_is_allowed(self):
        self.assertEqual(criteria_ids(["- [ ] C1. First", "  Check: a", "- [ ] C3. Third", "  Check: c"]), [1, 3])

    def test_the_pm_definition_of_done_requires_ids_and_check_lines(self):
        pm = " ".join((TEMPLATE.parent.parent / "team" / "pm.md").read_text(encoding="utf-8").split())
        done = pm.split("**Definition of done:**")[1].split("**Design section:**")[0]
        for needle in ("`- [ ] C<n>. <statement>`", "`Check:` line", "keeps its id",
                       "no id, a repeated id or no `Check:` line", "no script checks issue bodies"):
            self.assertIn(needle, done, needle)


if __name__ == "__main__":
    unittest.main()
