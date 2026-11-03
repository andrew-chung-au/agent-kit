"""Tests for agent-kit/scripts/secret-patterns.txt (issue #44).

The file is read by grep -E -f (scan-issue-body.sh) now and by a JavaScript
plugin later (#20), so it must hold only the regex subset that Python `re`,
JavaScript `RegExp` and `grep -E` read the same way. The fixtures are in
secret_fixtures.py, the one list shared with #20's plugin test.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import unittest
from pathlib import Path

from kit_repo import new_workdir
from secret_fixtures import MATCH, NON_MATCH, PATTERN_COUNT

REPO = Path(__file__).resolve().parent.parent
PATTERNS_FILE = REPO / "agent-kit" / "scripts" / "secret-patterns.txt"

# Things outside the shared subset: lookaround and groups with `(?`, backreferences,
# class escapes, word-boundary escapes, lazy quantifiers.
NON_PORTABLE = [
    (re.compile(r"\(\?"), "a `(?` group (lookaround, non-capturing or named group)"),
    (re.compile(r"\\[1-9]"), "a backreference"),
    (re.compile(r"\\[A-Za-z]"), "a backslash letter escape (\\d \\w \\s \\b ...)"),
    (re.compile(r"[*+?}]\?"), "a lazy quantifier"),
]


def non_portable(pattern: str) -> list:
    """Why a pattern is outside the shared subset (empty list: it is inside)."""
    return [why for regex, why in NON_PORTABLE if regex.search(pattern)]


def read_patterns() -> list:
    return PATTERNS_FILE.read_text(encoding="utf-8").split("\n")[:-1]


def grep_matches(pattern: str, text: str, work: Path) -> bool:
    """True when `grep -E -f` finds the pattern in text (the pattern goes through a file)."""
    pattern_file = work / "one-pattern.txt"
    pattern_file.write_text(pattern + "\n", encoding="utf-8")
    done = subprocess.run(["grep", "-E", "-f", str(pattern_file)], input=text + "\n",
                          capture_output=True, text=True, env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})
    if done.returncode not in (0, 1):
        raise AssertionError(f"grep could not read pattern {pattern!r}: {done.stderr}")
    return done.returncode == 0


class FileFormatTest(unittest.TestCase):
    def test_one_pattern_per_line_and_nothing_else(self):
        raw = PATTERNS_FILE.read_bytes()
        self.assertTrue(raw.endswith(b"\n"), "the last line needs its newline")
        self.assertNotIn(b"\r", raw)
        lines = read_patterns()
        self.assertEqual(len(lines), PATTERN_COUNT)
        for number, line in enumerate(lines, 1):
            self.assertNotEqual(line, "", f"line {number} is blank")
            self.assertFalse(line.startswith("#"), f"line {number} looks like a comment")
            self.assertEqual(line, line.strip(), f"line {number} has spaces at an end")

    def test_grep_can_read_the_whole_file(self):
        done = subprocess.run(["grep", "-E", "-f", str(PATTERNS_FILE), "/dev/null"],
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 1, done.stderr)

    def test_six_vuln_triage_patterns_are_kept_in_order(self):
        self.assertEqual(read_patterns()[:6], [
            "-----BEGIN [A-Z ]*PRIVATE KEY-----",
            "ghp_[A-Za-z0-9]{36}",
            "github_pat_[A-Za-z0-9_]{22,}",
            "AKIA[0-9A-Z]{16}",
            "xox[baprs]-[A-Za-z0-9-]{10,}",
            "sk-[A-Za-z0-9]{20,}",
        ])


class PortableSubsetTest(unittest.TestCase):
    def test_every_pattern_is_inside_the_shared_subset(self):
        for number, pattern in enumerate(read_patterns(), 1):
            self.assertEqual(non_portable(pattern), [], f"pattern {number}: {pattern}")

    def test_the_checker_refuses_what_is_outside_the_subset(self):
        for pattern in ["(?=x)", "(?!x)", "(?<=x)", "(?<!x)", "(?:x)", "(?P<n>x)", "(?<n>x)",
                        "(a)\\1", "\\d+", "\\w", "\\s", "\\bx", "a+?", "a*?", "a??", "a{2,3}?",
                        "\\D", "\\W", "\\S"]:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(non_portable(pattern), [])

    def test_the_checker_allows_plain_patterns(self):
        for pattern in ["a+", "[A-Za-z0-9_]{22,}", "(^|[^a-z])x", "\\.env", "a|b", "x?y", "(a|b)?c"]:
            with self.subTest(pattern=pattern):
                self.assertEqual(non_portable(pattern), [])


class FixtureTest(unittest.TestCase):
    def setUp(self):
        self.work = new_workdir(prefix="patterns-")
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.patterns = read_patterns()

    def matching_numbers(self, text, matcher):
        return [number for number, pattern in enumerate(self.patterns, 1) if matcher(pattern, text)]

    def test_each_secret_fixture_matches_its_pattern_in_python_and_grep(self):
        for name, text, number, _ in MATCH:
            with self.subTest(name=name):
                by_python = self.matching_numbers(text, lambda p, t: re.search(p, t) is not None)
                by_grep = self.matching_numbers(text, lambda p, t: grep_matches(p, t, self.work))
                self.assertEqual(by_python, [number])
                self.assertEqual(by_grep, [number])

    def test_each_non_secret_fixture_matches_nothing_in_python_and_grep(self):
        for name, text in NON_MATCH:
            with self.subTest(name=name):
                self.assertEqual(self.matching_numbers(text, lambda p, t: re.search(p, t) is not None), [])
                self.assertEqual(self.matching_numbers(text, lambda p, t: grep_matches(p, t, self.work)), [])

    def test_python_and_grep_agree_on_extra_cases(self):
        extra = [
            ".env", "see .env.", "x .env.production.local", "my.env.txt", ".environment",
            "cp .env.example .env", ".env.examples", "authorization: bearer " + "a" * 25,
            "Authorization: Bearer short", "xoxz-" + "1" * 12, "sk-" + "a" * 19, "sk-" + "a" * 20,
            "ghp_" + "a" * 35, "ghp_" + "a" * 36, "AKIA" + "A" * 15, "github_pat_" + "a" * 21,
            # #63: a backslash inside a bracket is literal for grep -E but not for Python or JS.
            "aws_secret_access_key\\=" + "A" * 40, "aws_secret_access_key \\ = " + "B" * 40,
            "ghs_" + "a" * 36 + "\\", "xsk-proj-" + "a" * 25, "AUTHORIZATION: BASIC " + "Q" * 16,
        ]
        for text in extra:
            with self.subTest(text=text):
                for number, pattern in enumerate(self.patterns, 1):
                    self.assertEqual(re.search(pattern, text) is not None,
                                     grep_matches(pattern, text, self.work),
                                     f"pattern {number} on {text!r}")

    def test_fixture_list_covers_the_issue(self):
        names = [name for name, *_ in MATCH]
        for needed in ("PEM private key header", "ghp_ token", "github_pat_ token", "AKIA key",
                       "xoxb- token", "sk- key", "Authorization Bearer header", "cat .env",
                       "config/.env.local"):
            self.assertIn(needed, names)
        # #63 adds rows after these; the five from #44 stay first and unchanged.
        self.assertEqual([text for _, text in NON_MATCH[:5]],
                         ["git status", "make verify", ".env.example", "config/.env.example", "sk-short"])
        self.assertEqual([name for name, *_ in MATCH[:9]],
                         ["PEM private key header", "ghp_ token", "github_pat_ token", "AKIA key", "xoxb- token",
                          "sk- key", "Authorization Bearer header", "cat .env", "config/.env.local"])

    def test_each_added_pattern_has_a_fixture_and_there_are_near_misses(self):
        # #63: one must-refuse fixture per added pattern (9 to 16), and at least as many near misses.
        numbers = {number for _, _, number, _ in MATCH}
        self.assertTrue(set(range(9, PATTERN_COUNT + 1)) <= numbers, set(range(9, PATTERN_COUNT + 1)) - numbers)
        self.assertGreaterEqual(len(MATCH) - 9, 10)
        self.assertGreaterEqual(len(NON_MATCH) - 5, len(MATCH) - 9)

    def test_left_out_on_purpose(self):
        # #63 decisions; the pattern file allows no comment lines, so the reasons live here.
        # - bare 40-character or longer base64 blobs: they match commit hashes and checksums,
        #   which issues quote all the time;
        # - `password=` or `password:` with any value: it matches every discussion of passwords,
        #   and the patterns above already cover real tokens;
        # - a key split across a line break: the scanner reads line by line (see process.md).
        patterns = PATTERNS_FILE.read_text(encoding="utf-8").split("\n")
        texts = dict(NON_MATCH)
        for name in ("a 40-character commit hash", "a password= value (left out on purpose)"):
            with self.subTest(name=name):
                self.assertFalse(any(line and re.search(line, texts[name]) for line in patterns))
        split = "ghp_" + "A1b2" * 4 + "\n" + "A1b2" * 5
        self.assertFalse(any(line and any(re.search(line, part) for part in split.split("\n")) for line in patterns))


class EmptyMatchTest(unittest.TestCase):
    def test_no_pattern_matches_an_empty_string(self):
        work = new_workdir(prefix="patterns-")
        self.addCleanup(shutil.rmtree, work, ignore_errors=True)
        for number, pattern in enumerate(read_patterns(), 1):
            with self.subTest(pattern=number):
                self.assertIsNone(re.search(pattern, ""))
                self.assertFalse(grep_matches(pattern, "", work))

    def test_the_whole_file_does_not_match_an_empty_line(self):
        done = subprocess.run(["grep", "-q", "-E", "-f", str(PATTERNS_FILE)], input="\n",
                              capture_output=True, text=True)
        self.assertEqual(done.returncode, 1)


if __name__ == "__main__":
    unittest.main()
