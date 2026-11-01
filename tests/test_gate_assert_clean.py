"""assert-clean.sh, QA's proof that it changed nothing (issue #40).

Run with the project folder as the working directory, as `make assert-clean` does.
Any modified, staged or untracked file in the folder (untracked files are listed
one by one, including inside new subfolders) gives FAIL and exit 1. Changes outside
the folder and git-ignored files are not reported.
"""
from __future__ import annotations

import unittest

from kit_repo import KitTestCase

SCRIPT = "agent-kit/scripts/assert-clean.sh"


class AssertCleanBase(KitTestCase):
    subdir = "."

    def setUp(self):
        super().setUp()
        self.project = self.add_project(self.subdir)
        self.write("tracked.txt", "one\n", base=self.project)
        self.write(".gitignore", "ignored.log\nbuild/\n", base=self.project)
        self.write("outside.txt", "o\n")
        self.base = self.commit_all("base")
        self.slate_ref = self.base

    def check(self):
        return self.run_cmd(["bash", SCRIPT], cwd=self.project)

    def failed(self, r, *paths, absent=()):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: FAIL", r.stdout)
        for p in paths:
            self.assertIn(p, r.stdout)
        for p in absent:
            self.assertNotIn(p, r.stdout)


class AssertCleanTest(AssertCleanBase):
    def test_a_clean_tree_passes(self):
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: PASS", r.stdout)
        self.assertIn(self.base[:7], r.stdout)

    def test_a_modified_tracked_file_fails(self):
        self.write("tracked.txt", "two\n", base=self.project)
        self.failed(self.check(), "tracked.txt")

    def test_a_new_untracked_file_fails(self):
        self.write("new.txt", base=self.project)
        self.failed(self.check(), "new.txt")

    def test_an_untracked_file_in_a_new_subfolder_is_listed_by_path(self):
        self.write("newdir/deeper/file.txt", base=self.project)
        r = self.check()
        self.failed(r, "newdir/deeper/file.txt")

    def test_a_staged_only_change_fails(self):
        self.write("staged.txt", base=self.project)
        self.git("add", "--", "staged.txt", cwd=self.project)
        self.failed(self.check(), "staged.txt")

    def test_a_staged_modification_fails(self):
        self.write("tracked.txt", "two\n", base=self.project)
        self.git("add", "--", "tracked.txt", cwd=self.project)
        self.failed(self.check(), "tracked.txt")

    def test_a_git_ignored_file_is_not_reported(self):
        self.write("ignored.log", base=self.project)
        self.write("build/out.bin", base=self.project)
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: PASS", r.stdout)
        self.assertNotIn("ignored.log", r.stdout)
        self.assertNotIn("out.bin", r.stdout)


class AssertCleanSubfolderTest(AssertCleanBase):
    subdir = "proj"

    def test_a_change_outside_the_project_folder_is_not_reported(self):
        self.write("outside.txt", "changed\n")
        self.write("untracked-outside.txt")
        r = self.check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: PASS", r.stdout)

    def test_a_change_inside_the_project_folder_is_reported_next_to_an_outside_one(self):
        self.write("outside.txt", "changed\n")
        self.write("inside.txt", base=self.project)
        self.failed(self.check(), "inside.txt", absent=("outside.txt",))


if __name__ == "__main__":
    unittest.main()
