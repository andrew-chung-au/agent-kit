"""Phrase tests for issue #29: groom before approval, freeze the approved body by hash.

These pin the wording of the freeze rules in agent-kit/process.md, the one closing
rule in process.md and AGENTS.md, and the script docstring, so they cannot drift
out of the text. Whitespace is normalised, so line wrapping does not matter.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CLOSING = ("Only the orchestrator closes issues: after QA posts PASS on an `approved` issue, "
           "or as not planned after the human approves that closure in a backlog review, "
           "whatever the label.")


def flat(path: Path) -> str:
    return " ".join(path.read_text().split())


def section(text: str, start: str, end: str) -> str:
    """The part of flattened text from the start marker up to the end marker."""
    begin = text.index(start)
    return text[begin:text.index(end, begin)]


class ProcessFreezeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = flat(REPO / "agent-kit" / "process.md")

    def lifecycle_step(self, number: int) -> str:
        lifecycle = section(self.text, "## Lifecycle", "## Commits and pushes")
        match = re.search(rf"(?:^| ){number}\. (.*?)(?= {number + 1}\. |$)", lifecycle)
        self.assertIsNotNone(match, f"step {number} not found")
        return match.group(1)

    def test_step_1_agreed_order(self):
        self.assertIn("Pick the next open issue in the agreed order.", self.lifecycle_step(1))

    def test_step_2_groom_before_label(self):
        step = self.lifecycle_step(2)
        for phrase in ["The PM grooms it, even if it is not yet labelled, when it is owner-authored",
                       "Then the human reads the groomed text and adds `approved`",
                       "the Engineer starts only after that",
                       "only the next issue in the agreed order",
                       "not a second unlabelled issue while the first waits for the label",
                       "record the new hash in a new `PM:` comment before the label is added",
                       "Never skip this step."]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, step)

    def test_backlog_says_the_same(self):
        backlog = section(self.text, "## Backlog", "## Issue comments")
        self.assertIn("Grooming comes before the label, and the label approves the groomed text", backlog)
        self.assertIn("The human's approval of a backlog proposal still comes before any issue is created, "
                      "edited or closed", backlog)

    def test_hash_comparison_at_the_three_launches(self):
        self.assertIn("run `make issue-hash N=<number>` and compare `Body sha256:` with `Recorded sha256:`",
                      self.text)
        self.assertIn("Before launching the Engineer, and before relaunching it after a QA FAIL, "
                      "run the hash check", self.lifecycle_step(3))
        self.assertIn("Before launching QA, the orchestrator runs the hash check", self.lifecycle_step(4))
        self.assertIn("the hash check runs again", self.lifecycle_step(6))

    def test_refused_cases_of_the_check(self):
        for phrase in ["don't launch the role",
                       "`Recorded sha256:` is `none` or `unknown`",
                       "the command exits non-zero or prints `unknown`",
                       "show the human the diff of the body, not a paraphrase"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_valid_comment_rule(self):
        for phrase in ["only from a comment that starts with `PM:`",
                       "authored by the repository owner's account",
                       "`comments[].author.login`",
                       "`Repository owner:`",
                       "the latest valid line wins",
                       "A `Body sha256:` line anywhere else is ignored"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_confirmation_comment(self):
        for phrase in ["the human confirms it in this session",
                       "an `Orchestrator:` comment naming the new hash",
                       "the PM then records that hash in a `PM:` comment",
                       "Without that `PM:` line the launch stays blocked",
                       "edits an approved body and carries on without the confirmation comment",
                       "A title change is reported to the human as a note, not a freeze failure"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.text)

    def test_closing_sentence_in_step_9(self):
        step = self.lifecycle_step(9)
        self.assertIn("Close the issue. " + CLOSING, step)

    def test_closing_sentence_in_agents_md(self):
        text = flat(REPO / "AGENTS.md")
        self.assertIn("Closing is not covered by the author rule. " + CLOSING, text)
        self.assertNotIn("don't close an issue without the label", text)


class ScriptDocstringTest(unittest.TestCase):
    def test_docstring_says_five_lines(self):
        text = (REPO / "agent-kit" / "scripts" / "issue-hash.py").read_text()
        self.assertIn("exactly five lines", text)
        self.assertNotIn("exactly four lines", text)
        self.assertIn("Recorded sha256: <64 lowercase hex characters|none|unknown>", text)


if __name__ == "__main__":
    unittest.main()
