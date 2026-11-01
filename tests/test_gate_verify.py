"""Behaviour tests for agent-kit/scripts/verify.sh.

Run as `bash agent-kit/scripts/verify.sh <BASE>` in a throwaway repo with a base
commit, then a second commit holding the change under test.

The skip and focus markers the script looks for are built from pieces below, so
this file does not itself contain them (verify.sh reads added lines in test
files, this one included).
"""
from __future__ import annotations

import unittest

from kit_repo import KitTestCase

ZERO = "0" * 40
SKIPS = {
    "unittest": "@unittest" + ".sk" + "ip('later')\n",
    "pytest": "@pytest.mark" + ".skip\n",
    "focus": "describe" + ".on" + "ly('a', fn)\n",
    "go": "t" + ".Skip(\"later\")\n",
}
BASE_TEST = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_a(self):\n        assert 1 == 1\n        assert 2 == 2\n"


class VerifyCase(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.write("tests/test_a.py", BASE_TEST)
        self.write("src.txt", "one\n")
        self.base = self.commit_all("base")

    def conf(self, **settings):
        text = "".join('%s="%s"\n' % (k, v) for k, v in settings.items())
        self.write("agent-kit.conf",
                   'KIT_DIR="agent-kit"\nLINT_CMD=""\nTYPECHECK_CMD=""\nTEST_FILES=( \'tests/*\' )\n' + text)
        self.git("add", "agent-kit.conf")
        self.git("commit", "-q", "--no-verify", "-m", "conf")

    def verify(self, base=None):
        args = ["bash", "agent-kit/scripts/verify.sh"]
        if base is not None:
            args.append(base)
        return self.run_cmd(args)

    def change(self, rel, content, message="change"):
        self.write(rel, content)
        self.git("--literal-pathspecs", "add", "--", rel)
        self.git("commit", "-q", "--no-verify", "-m", message)


class OutcomeTest(VerifyCase):
    def test_a_clean_change_passes(self):
        self.change("src.txt", "two\n")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("VERIFY: PASS", r.stdout)
        self.assertNotIn("WARNINGS", r.stdout)

    def test_a_failing_test_command_fails(self):
        self.conf(TEST_CMD="false")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL: Tests", r.stdout)

    def test_a_passing_test_command_is_run(self):
        self.conf(TEST_CMD="echo ran-the-tests")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("ran-the-tests", r.stdout)

    def test_an_empty_test_command_passes_with_a_warning(self):
        self.conf(TEST_CMD="")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("WARN: no TEST_CMD", r.stdout)
        self.assertIn("PASS WITH WARNINGS", r.stdout)

    def test_a_whitespace_error_fails(self):
        self.conf(TEST_CMD="true")
        self.change("src.txt", "trailing space \n")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL: whitespace errors", r.stdout)

    def test_a_deleted_test_file_fails(self):
        self.conf(TEST_CMD="true")
        self.git("rm", "-q", "tests/test_a.py")
        self.git("commit", "-q", "--no-verify", "-m", "delete")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("FAIL: test files deleted", r.stdout)
        self.assertIn("  tests/test_a.py\n", r.stdout)

    def test_each_skip_or_focus_marker_fails(self):
        self.conf(TEST_CMD="true")
        self.slate_ref = self.git("rev-parse", "HEAD").stdout.strip()
        for label, line in SKIPS.items():
            with self.subTest(marker=label):
                self.change("tests/test_a.py", BASE_TEST + line, "add " + label)
                r = self.verify(self.base)
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("FAIL: skip, xfail or focus markers added", r.stdout)

    def test_removed_assert_lines_warn_but_pass(self):
        self.conf(TEST_CMD="true")
        self.change("tests/test_a.py", BASE_TEST.replace("        assert 2 == 2\n", ""))
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("WARN: assertions removed or rewritten", r.stdout)
        self.assertIn("PASS WITH WARNINGS", r.stdout)

    def test_a_changed_test_file_without_weakening_passes(self):
        self.conf(TEST_CMD="true")
        self.change("tests/test_a.py", BASE_TEST + "        assert 3 == 3\n")
        r = self.verify(self.base)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("VERIFY: PASS", r.stdout)


class BaseTest(VerifyCase):
    def test_no_base_no_upstream_and_detached_head_compares_head_with_head(self):
        # Pins the CI problem (a shallow, detached checkout with no BASE): there is
        # nothing to compare, so a deleted test is not seen. If verify.sh ever gets
        # a better fallback, this test is expected to change.
        self.conf(TEST_CMD="true")
        self.git("rm", "-q", "tests/test_a.py")
        self.git("commit", "-q", "--no-verify", "-m", "delete")
        self.git("checkout", "-q", "--detach")
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("Changes in this folder since HEAD", r.stdout)
        self.assertIn("No test files changed.", r.stdout)

    def test_an_all_zero_base_takes_the_same_fallback(self):
        self.conf(TEST_CMD="true")
        self.git("checkout", "-q", "--detach")
        r = self.verify(ZERO)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("Changes in this folder since HEAD", r.stdout)

    def test_a_base_that_is_not_a_commit_never_passes(self):
        self.conf(TEST_CMD="true")
        for bad in ("1" * 40, "no-such-branch"):
            with self.subTest(base=bad):
                r = self.verify(bad)
                self.assertNotEqual(r.returncode, 0, r.stdout)
                self.assertNotIn("VERIFY: PASS", r.stdout)


if __name__ == "__main__":
    unittest.main()
