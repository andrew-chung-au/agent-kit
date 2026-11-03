"""assert-clean.sh, QA's proof that it changed nothing (issue #40).

Run with the project folder as the working directory, as `make assert-clean` does.
Any modified, staged or untracked file in the folder (untracked files are listed
one by one, including inside new subfolders) gives FAIL and exit 1. Changes outside
the folder and git-ignored files are not reported.
"""
from __future__ import annotations

import os
import unittest

import git_stub
from kit_repo import KitTestCase, KIT

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


class AssertCleanFailClosedTest(AssertCleanBase):
    """When git itself fails, assert-clean must never print PASS (issue #43).

    Decision recorded here: in a repository with no commits there is no HEAD to compare
    the folder against, so the script fails closed (exit 1, FAIL, a reason) instead of
    passing or printing an empty `HEAD is `.
    """

    def standalone(self, name):
        """An empty folder away from the kit's own repo (the script is run by path)."""
        folder = self.work / name
        folder.mkdir()
        return folder

    def run_there(self, folder, env=None):
        # GIT_CEILING_DIRECTORIES stops git looking above self.work, which sits inside the kit repo.
        e = {"GIT_CEILING_DIRECTORIES": str(self.work)}
        e.update(env or {})
        return self.run_cmd(["bash", KIT / "scripts" / "assert-clean.sh"], cwd=folder, env=e)

    def assert_fails_closed(self, r, reason):
        everything = r.stdout + r.stderr
        self.assertNotEqual(r.returncode, 0, everything)
        self.assertNotIn("PASS", everything)
        self.assertNotIn("HEAD is", everything)
        self.assertTrue(everything.strip(), "a reason is printed")
        self.assertIn("ASSERT-CLEAN: FAIL", r.stdout)
        self.assertIn(reason, r.stdout)

    def test_a_folder_that_is_not_a_git_repository_fails(self):
        r = self.run_there(self.standalone("not-a-repo"))
        self.assert_fails_closed(r, "git status failed")

    def test_a_git_dir_that_does_not_exist_fails(self):
        r = self.run_cmd(["bash", SCRIPT], cwd=self.project,
                         env={"GIT_DIR": str(self.work / "missing.git")})
        self.assert_fails_closed(r, "git status failed")

    def test_a_repository_with_no_commits_fails_closed_and_says_why(self):
        folder = self.standalone("no-commits")
        self.git("init", "-q", "-b", "main", cwd=folder)
        r = self.run_there(folder)
        self.assert_fails_closed(r, "no HEAD commit")
        self.assertEqual(r.returncode, 1)

    def test_a_failing_git_status_fails(self):
        stub, log = git_stub.install(self.work)
        env = {"PATH": stub + os.pathsep + self.env["PATH"], "GIT_STUB_FAIL": "status *"}
        r = self.run_cmd(["bash", SCRIPT], cwd=self.project, env=env)
        self.assert_fails_closed(r, "git status failed")
        self.assertTrue(any(c.startswith("status ") for c in git_stub.calls(log)), "the stub was not reached")

    def test_a_failing_git_rev_parse_fails_even_though_git_status_works(self):
        stub, log = git_stub.install(self.work)
        env = {"PATH": stub + os.pathsep + self.env["PATH"], "GIT_STUB_FAIL": "rev-parse --short HEAD"}
        r = self.run_cmd(["bash", SCRIPT], cwd=self.project, env=env)
        self.assert_fails_closed(r, "no HEAD commit")
        self.assertIn("rev-parse --short HEAD", git_stub.calls(log))

    def test_the_stub_passes_everything_through_when_no_pattern_matches(self):
        stub, log = git_stub.install(self.work)
        r = self.run_cmd(["bash", SCRIPT], cwd=self.project, env={"PATH": stub + os.pathsep + self.env["PATH"]})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ASSERT-CLEAN: PASS", r.stdout)
        self.assertIn(self.base[:7], r.stdout)
        self.assertTrue(git_stub.calls(log))

    def test_a_dirty_tree_still_fails_with_the_changes_listed(self):
        self.write("new.txt", base=self.project)
        self.failed(self.check(), "new.txt")


if __name__ == "__main__":
    unittest.main()
