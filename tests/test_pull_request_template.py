"""Wording checks for the kit's pull request template (issue #21).

It checks the template's text only: that it says `Refs #N`, forbids the words that make GitHub close
an issue, has the five parts and stays short. It does not check what an agent writes in a pull
request, or whether the cloud tool applies the template: GitHub applies
`.github/pull_request_template.md` only to pull requests opened in the web UI.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "agent-kit" / "templates" / "github" / "pull_request_template.md"
BLUEPRINTS = ROOT / "agent-kit" / "blueprints.md"

MAX_WORDS = 70
PROHIBITION = "Never write Closes, Fixes or Resolves: only the orchestrator closes issues, after QA PASS."
PARTS = ("Refs #N", "## What changed", "## Verify", "`make verify`", "## Protected paths",
         "the human approved the commit", "## Not verified")
# Every keyword GitHub reads as "close this issue" when a pull request with it merges.
CLOSE_KEYWORD = re.compile(r"\b(close[sd]?|fix(es|ed)?|resolve[sd]?)\b", re.IGNORECASE)


def check(text: str) -> list[str]:
    """The problems found in the template text; empty means it passes."""
    problems = []
    if not text.isascii():
        problems.append("non-ASCII character (a look-alike or zero-width letter could hide a close keyword)")
    if text.count(PROHIBITION) > 1:
        problems.append("the forbidding sentence appears more than once")
    words = len(text.split())
    if words > MAX_WORDS:
        problems.append("%d words, over the cap of %d" % (words, MAX_WORDS))
    if not re.search(r"\bRefs #N\b", text):
        problems.append("no `Refs #N` line")
    if PROHIBITION not in text:
        problems.append("the sentence that forbids Closes, Fixes and Resolves is missing or changed")
    leftover = CLOSE_KEYWORD.findall(text.replace(PROHIBITION, ""))
    if leftover:
        problems.append("a close keyword appears outside the forbidding sentence")
    for part in PARTS:
        if part not in text:
            problems.append("part missing: " + part)
    return problems


class PullRequestTemplateTest(unittest.TestCase):
    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_the_template_passes(self):
        self.assertEqual(check(self.text), [])

    def test_it_is_at_most_70_words_as_wc_counts_them(self):
        self.assertLessEqual(len(self.text.split()), MAX_WORDS)

    def test_it_names_refs_and_forbids_the_three_words_with_the_reason(self):
        self.assertIn("Refs", self.text)
        for word in ("Closes", "Fixes", "Resolves"):
            self.assertIn(word, PROHIBITION)
        self.assertIn(PROHIBITION, self.text)
        self.assertIn("only the orchestrator closes issues, after QA PASS", PROHIBITION)

    def test_the_forbidding_sentence_is_the_only_place_a_close_keyword_appears(self):
        self.assertEqual(self.text.count(PROHIBITION), 1)
        self.assertEqual(CLOSE_KEYWORD.findall(self.text.replace(PROHIBITION, "")), [])

    def test_the_template_holds_no_personal_data_or_comment_markup(self):
        self.assertNotIn("<!--", self.text)
        self.assertNotRegex(self.text, r"@[A-Za-z0-9]")

    def test_blueprints_lists_it_with_its_source_and_install_path(self):
        row = next(l for l in BLUEPRINTS.read_text(encoding="utf-8").splitlines() if l.startswith("| Pull request template"))
        self.assertIn("`templates/github/pull_request_template.md`", row)
        self.assertIn("`.github/pull_request_template.md`", row)

    def test_the_github_copy_matches_the_kit_copy_once_the_human_has_made_it(self):
        copy = ROOT / ".github" / "pull_request_template.md"
        # Absent until the human copies it from a clean clone: nothing to compare yet.
        if copy.exists():
            self.assertEqual(copy.read_bytes(), TEMPLATE.read_bytes())


class MustBeRefusedTest(unittest.TestCase):
    """Each broken copy of the template makes check() report a problem."""

    def setUp(self):
        self.text = TEMPLATE.read_text(encoding="utf-8")

    def test_removing_refs_is_refused(self):
        self.assertTrue(check(self.text.replace("Refs #N", "See issue")))

    def test_removing_the_prohibition_is_refused(self):
        self.assertTrue(check(self.text.replace(PROHIBITION, "")))

    def test_weakening_the_prohibition_is_refused(self):
        self.assertTrue(check(self.text.replace("Never write", "Prefer not to write")))
        self.assertTrue(check(self.text.replace(", after QA PASS", "")))

    def test_padding_past_the_cap_is_refused(self):
        self.assertTrue(check(self.text + "word " * (MAX_WORDS + 1)))

    def test_a_close_keyword_outside_the_sentence_is_refused(self):
        for line in ("Closes #N", "fixes #N", "RESOLVES #N", "Closed #N", "Fix #N"):
            with self.subTest(line=line):
                self.assertTrue(check(self.text + "\n" + line + "\n"))

    def test_look_alike_and_zero_width_letters_are_refused(self):
        for line in ("Clo\u200bses #N", "Cl\u043eses #N", "Fix\u0435s #N", "\uff23loses #N"):
            with self.subTest(line=ascii(line)):
                self.assertTrue(check(self.text + "\n" + line + "\n"))

    def test_a_second_copy_of_the_forbidding_sentence_is_refused(self):
        self.assertTrue(check(self.text + "\n" + PROHIBITION + "\n"))

    def test_a_missing_part_is_refused(self):
        for part in ("## What changed", "## Verify", "## Protected paths", "## Not verified"):
            with self.subTest(part=part):
                self.assertTrue(check(self.text.replace(part, "## Other")))


if __name__ == "__main__":
    unittest.main()
