"""Pins the "Report by reference" rule in agent-kit/process.md (issue #55).

rule_problems takes the text of process.md and returns a list of problems, so the same
function runs on the real file (must be empty) and on mutated copies (must not be).

Limit: this checks wording, not behaviour. Whether a message actually restates a file is
counted by hand in the session summaries (the measure in #55).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PROCESS = REPO / "agent-kit" / "process.md"
HEADING = "**Report by reference.**"
MAX_WORDS = 90

# What the rule must say, as (name, regex over the rule's paragraph with whitespace collapsed).
REQUIRED = [
    ("the file kinds", r"session summary, issue comment, `\.scratch/` file, task file"),
    ("both directions", r"a message to the human or a role's return"),
    ("path, outcome and decisions", r"path or link, a one-line size or outcome, and the decisions or exceptions"),
    ("never restates", r"never its contents"),
    ("exception 1: protected-commit approval", r"protected-commit approval request \(its diff and `git diff --cached --stat`\)"),
    ("exception 2: security finding", r"security finding \(never the secret\)"),
    ("exception 3: blocking question", r"a blocking question"),
    ("clean-scratch sentence", r"`make clean-scratch` deletes untracked `\.scratch/`, so post or commit anything lasting; "
                               r"clean up after the human has read it"),
]


def rule_paragraph(text: str):
    for paragraph in text.split("\n\n"):
        if paragraph.startswith(HEADING):
            return " ".join(paragraph.split())
    return None


def rule_problems(text: str) -> list:
    rule = rule_paragraph(text)
    if rule is None:
        return ["no paragraph starts with " + HEADING]
    problems = [name for name, regex in REQUIRED if not re.search(regex, rule)]
    exceptions = rule.split("Exceptions, kept in full:", 1)
    if len(exceptions) != 2:
        problems.append("the exceptions are not introduced")
    else:
        listed = exceptions[1].split("`make clean-scratch`", 1)[0].strip().rstrip(".").split(";")
        if len(listed) != 3:
            problems.append(f"{len(listed)} exceptions instead of exactly three")
    if len(rule.split()) > MAX_WORDS:
        problems.append(f"{len(rule.split())} words, over the {MAX_WORDS}-word cap")
    if text.count(HEADING) != 1:
        problems.append("the heading appears more than once")
    section = text[text.index("## Orchestrator"):text.index("## When a role's actions are blocked")]
    if HEADING not in section or section.index(HEADING) < section.index("**Human tasks.**"):
        problems.append("the rule is not in the Orchestrator section after Human tasks")
    return problems


class ReportByReferenceTest(unittest.TestCase):
    text = PROCESS.read_text(encoding="utf-8")

    def test_the_rule_is_present_and_complete(self):
        self.assertEqual(rule_problems(self.text), [])

    def test_removing_the_heading_fails(self):
        self.assertNotEqual(rule_problems(self.text.replace(HEADING, "**Reporting.**")), [])

    def test_removing_any_one_exception_fails(self):
        rule = rule_paragraph(self.text)
        for part in ("a protected-commit approval request (its diff and `git diff --cached --stat`); ",
                     "a security finding (never the secret); ", "; a blocking question"):
            with self.subTest(part=part):
                raw = next(p for p in self.text.split("\n\n") if p.startswith(HEADING))
                self.assertIn(part, rule)
                self.assertNotEqual(rule_problems(self.text.replace(raw, raw.replace(part, "", 1))), [])

    def test_a_fourth_exception_fails(self):
        mutated = self.text.replace("; a blocking question.", "; a blocking question; a long log.")
        self.assertIn("4 exceptions instead of exactly three", rule_problems(mutated))

    def test_removing_the_clean_scratch_sentence_fails(self):
        raw = next(p for p in self.text.split("\n\n") if p.startswith(HEADING))
        sentence = raw[raw.index("`make clean-scratch`"):]
        self.assertNotEqual(rule_problems(self.text.replace(sentence, "")), [])

    def test_dropping_never_restates_or_the_return_clause_fails(self):
        for old, new in (("never its contents", "with a summary"),
                         ("a message to the human or a role's return", "a message to the human")):
            with self.subTest(old=old):
                self.assertNotEqual(rule_problems(self.text.replace(old, new)), [])

    def test_going_over_the_word_cap_fails(self):
        raw = next(p for p in self.text.split("\n\n") if p.startswith(HEADING))
        self.assertIn("over the 90-word cap", " ".join(rule_problems(self.text.replace(raw, raw + " One more word."))))

    def test_moving_the_rule_out_of_the_orchestrator_section_fails(self):
        raw = next(p for p in self.text.split("\n\n") if p.startswith(HEADING))
        moved = self.text.replace("\n\n" + raw, "", 1).rstrip("\n") + "\n\n" + raw + "\n"
        self.assertIn("the rule is not in the Orchestrator section after Human tasks", rule_problems(moved))


if __name__ == "__main__":
    unittest.main()
