"""verify.sh and unusual test file names (issue #1).

A test file deleted, or given a skip marker, under a non-ASCII name, a name with
a double quote or a name with a backslash must fail the gate like a plain name.
Git quotes those names in its default output, so verify.sh reads its
--name-status list NUL-delimited (-z) and passes names to git literally. The
"plain" name is the control. The skip marker is built from pieces so this file
does not contain it.
"""
from __future__ import annotations

import unittest

from kit_repo import KitTestCase, UNUSUAL_NAMES

SKIP = "@unittest" + ".sk" + "ip('later')\n"
BODY = "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_a(self):\n        assert 1 == 1\n"


class VerifyNamesTest(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.paths = {label: "tests/" + base + ".py" for label, base in UNUSUAL_NAMES.items()}
        self.paths["umlauts"] = "tests/ünï.py"
        for path in self.paths.values():
            self.write(path, BODY)
        self.base = self.commit_all("base")
        self.slate_ref = self.base

    def verify(self):
        return self.run_cmd(["bash", "agent-kit/scripts/verify.sh", self.base])

    def test_a_deleted_test_file_fails_for_every_name(self):
        for label, path in self.paths.items():
            with self.subTest(name=label):
                self.git("--literal-pathspecs", "rm", "-q", "--", path)
                self.git("commit", "-q", "--no-verify", "-m", "delete " + label)
                r = self.verify()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("FAIL: test files deleted", r.stdout)
                self.assertIn("  " + path + "\n", r.stdout)
                self.git("reset", "-q", "--hard", self.base)

    def test_a_skip_marker_fails_for_every_name(self):
        for label, path in self.paths.items():
            with self.subTest(name=label):
                self.write(path, BODY + SKIP)
                self.git("--literal-pathspecs", "add", "--", path)
                self.git("commit", "-q", "--no-verify", "-m", "skip " + label)
                r = self.verify()
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("FAIL: skip, xfail or focus markers added", r.stdout)
                self.git("reset", "-q", "--hard", self.base)

    def test_a_clean_change_to_every_name_passes(self):
        for label, path in self.paths.items():
            with self.subTest(name=label):
                self.write(path, BODY + "        assert 2 == 2\n")
                self.git("--literal-pathspecs", "add", "--", path)
                self.git("commit", "-q", "--no-verify", "-m", "extend " + label)
                r = self.verify()
                self.assertEqual(r.returncode, 0, r.stdout)
                self.assertIn("VERIFY: PASS", r.stdout)
                self.git("reset", "-q", "--hard", self.base)


if __name__ == "__main__":
    unittest.main()
