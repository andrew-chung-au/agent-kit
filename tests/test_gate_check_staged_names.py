"""check-staged.sh and unusual file names (issue #1).

A name with a space, a non-ASCII character, a double quote or a backslash must
be refused exactly like its plain equivalent, with the real name (not git's
quoted form) on stderr. Git quotes the last three in its default output, so the
script must read the staged list NUL-delimited (-z). The "plain" name is the
control and passes with or without that fix.
"""
from __future__ import annotations

import unittest

from kit_repo import KitTestCase, UNUSUAL_NAMES


class CheckStagedNamesTest(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.write("README.md")
        self.commit_all()
        self.install_precommit()

    def check_direct(self):
        return self.run_cmd(["bash", "agent-kit/scripts/check-staged.sh"])

    def test_forbidden_names_are_refused_by_the_hook_and_the_script(self):
        for label, base in UNUSUAL_NAMES.items():
            path = base + ".pem"
            with self.subTest(name=label, via="hook"):
                self.write(path)
                self.stage(path)
                r = self.try_commit()
                self.assertNotEqual(r.returncode, 0, "committed %r" % path)
                self.assertIn("  " + path + "\n", r.stderr)
                self.unstage_all()
            with self.subTest(name=label, via="script"):
                self.write(path)
                self.stage(path)
                r = self.check_direct()
                self.assertNotEqual(r.returncode, 0, "accepted %r" % path)
                self.assertIn("  " + path + "\n", r.stderr)
                self.unstage_all()

    def test_protected_names_are_refused_without_approval(self):
        for label, base in UNUSUAL_NAMES.items():
            path = "docs/" + base + ".md"
            with self.subTest(name=label, via="hook"):
                self.write(path)
                self.stage(path)
                r = self.try_commit()
                self.assertNotEqual(r.returncode, 0, "committed %r" % path)
                self.assertIn("  " + path + "\n", r.stderr)
                self.unstage_all()
            with self.subTest(name=label, via="script"):
                self.write(path)
                self.stage(path)
                r = self.check_direct()
                self.assertNotEqual(r.returncode, 0, "accepted %r" % path)
                self.assertIn("  " + path + "\n", r.stderr)
                self.unstage_all()

    def test_protected_names_are_accepted_with_approval(self):
        for label, base in UNUSUAL_NAMES.items():
            path = "docs/" + base + ".md"
            with self.subTest(name=label):
                self.write(path)
                self.stage(path)
                r = self.try_commit(approved="1")
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_rename_of_a_protected_file_to_an_unusual_name_is_refused(self):
        for label, base in UNUSUAL_NAMES.items():
            with self.subTest(name=label):
                self.write("docs/old.md", "old " + label + "\n")
                self.commit_all("add protected file")
                self.git("mv", "docs/old.md", base + ".txt")
                r = self.try_commit()
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("  docs/old.md\n", r.stderr)
                self.git("reset", "-q", "--hard")

    def test_a_rename_into_an_unusual_forbidden_name_is_refused(self):
        for label, base in UNUSUAL_NAMES.items():
            with self.subTest(name=label):
                self.write("note.txt", "x " + label + "\n")
                self.commit_all("add file")
                self.git("mv", "note.txt", base + ".pem")
                r = self.try_commit()
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("  " + base + ".pem\n", r.stderr)
                self.git("reset", "-q", "--hard")

    def test_deleting_a_committed_forbidden_unusual_name_is_accepted(self):
        for label, base in UNUSUAL_NAMES.items():
            path = base + ".pem"
            with self.subTest(name=label):
                self.write(path)
                self.git("--literal-pathspecs", "add", "--force", "--", path)
                self.git("commit", "-q", "--no-verify", "-m", "committed before the hook existed")
                self.git("--literal-pathspecs", "rm", "-q", "--", path)
                r = self.try_commit()
                self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == "__main__":
    unittest.main()
