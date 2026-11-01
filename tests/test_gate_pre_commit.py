"""Behaviour tests for agent-kit/githooks/pre-commit and scripts/check-staged.sh.

The hook is installed in a throwaway repo and run the way `git commit` runs it.
Plain names only here; names git quotes are in test_gate_check_staged_names.py
and test_gate_pre_commit_names.py.
"""
from __future__ import annotations

import unittest

from kit_repo import KitTestCase

ROOT_PROTECTED = (
    ".githooks/pre-commit",
    ".github/workflows/ci.yml",
    ".devcontainer/devcontainer.json",
    ".devcontainer.json",
    ".vscode/settings.json",
    ".envrc",
    ".gitmodules",
)


class RootProjectCase(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.write("README.md")
        self.commit_all()
        self.install_precommit()

    def refused(self, r, *names):
        self.assertNotEqual(r.returncode, 0, r.stderr)
        for name in names:
            self.assertIn(name, r.stderr)

    def accepted(self, r):
        self.assertEqual(r.returncode, 0, r.stderr)


class ForbiddenTest(RootProjectCase):
    def test_forbidden_files_are_refused_with_the_path_named(self):
        for name in (".env", "config/.env.local", "data.db", "a.pem"):
            with self.subTest(name=name):
                self.write(name)
                self.stage(name)
                self.refused(self.try_commit(), name)
                self.unstage_all()

    def test_forbidden_is_refused_even_with_approval(self):
        self.write("a.pem")
        self.stage("a.pem")
        self.refused(self.try_commit(approved="1"), "a.pem")

    def test_env_example_is_allowed(self):
        for name in (".env.example", "config/.env.example"):
            with self.subTest(name=name):
                self.write(name)
                self.stage(name)
                self.accepted(self.try_commit())

    def test_deleting_a_committed_forbidden_file_is_accepted(self):
        self.write("data.db")
        self.git("add", "--force", "data.db")
        self.git("commit", "-q", "--no-verify", "-m", "committed before the hook existed")
        self.git("rm", "-q", "data.db")
        self.accepted(self.try_commit())


class ProtectedTest(RootProjectCase):
    def test_protected_change_is_refused_without_approval(self):
        self.write("docs/guide.md")
        self.stage("docs/guide.md")
        self.refused(self.try_commit(), "docs/guide.md")

    def test_protected_change_is_accepted_with_approval(self):
        self.write("docs/guide.md")
        self.stage("docs/guide.md")
        self.accepted(self.try_commit(approved="1"))

    def test_only_the_exact_value_1_approves(self):
        for value in ("0", "yes", "true", "11", ""):
            with self.subTest(value=value):
                self.write("docs/guide.md")
                self.stage("docs/guide.md")
                self.refused(self.try_commit(approved=value), "docs/guide.md")
                self.unstage_all()

    def test_a_rename_of_a_protected_file_is_refused_without_approval(self):
        self.write("docs/guide.md")
        self.commit_all("add protected file")
        self.git("mv", "docs/guide.md", "notes.md")
        self.refused(self.try_commit(), "docs/guide.md")
        self.accepted(self.try_commit(approved="1"))

    def test_a_rename_into_a_protected_path_is_refused_without_approval(self):
        self.write("notes.md")
        self.commit_all("add file")
        (self.repo / "docs").mkdir()
        self.git("mv", "notes.md", "docs/notes.md")
        self.refused(self.try_commit(), "docs/notes.md")


class RepoRootProtectionTest(RootProjectCase):
    def test_each_root_path_is_refused_without_approval_and_accepted_with_it(self):
        for name in ROOT_PROTECTED:
            with self.subTest(name=name):
                self.write(name)
                self.stage(name)
                self.refused(self.try_commit(), name)
                self.accepted(self.try_commit(approved="1"))

    def test_root_protection_needs_the_exact_value_1(self):
        for value in ("0", "yes", ""):
            with self.subTest(value=value):
                self.write(".github/workflows/ci.yml")
                self.stage(".github/workflows/ci.yml")
                self.refused(self.try_commit(approved=value), ".github/workflows/ci.yml")

    def test_a_lookalike_root_path_is_not_protected(self):
        for name in (".githubx/a.yml", ".envrc.bak", ".vscodex/a.json", "sub/.github/a.yml"):
            with self.subTest(name=name):
                self.write(name)
                self.stage(name)
                self.accepted(self.try_commit())


class OtherChecksTest(RootProjectCase):
    def test_whitespace_error_in_staged_content_is_refused(self):
        self.write("notes.txt", "trailing space \n")
        self.stage("notes.txt")
        r = self.try_commit()
        self.refused(r)
        self.assertIn("whitespace", r.stderr)

    def test_clean_change_is_accepted(self):
        self.write("notes.txt", "clean\n")
        self.stage("notes.txt")
        self.accepted(self.try_commit())


class ProjectsTest(KitTestCase):
    def setUp(self):
        super().setUp()
        self.write("README.md")

    def test_folder_without_agent_kit_conf_is_left_alone(self):
        self.add_project("proj")
        self.commit_all()
        self.install_precommit()
        self.write("other/a.pem")
        self.write("other/docs/a.md")
        self.stage("other/a.pem", "other/docs/a.md")
        self.assertEqual(self.try_commit().returncode, 0)

    def test_conf_without_check_staged_script_is_refused(self):
        self.add_project("proj", with_scripts=False)
        self.commit_all()
        self.install_precommit()
        self.write("proj/notes.txt")
        self.stage("proj/notes.txt")
        r = self.try_commit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("has agent-kit.conf but no agent-kit/scripts/check-staged.sh", r.stderr)

    def test_only_the_touched_projects_patterns_apply(self):
        conf_a = 'KIT_DIR="agent-kit"\nFORBIDDEN=( \'*.aaa\' )\nPROTECTED=( )\n'
        conf_b = 'KIT_DIR="agent-kit"\nFORBIDDEN=( \'*.bbb\' )\nPROTECTED=( )\n'
        self.add_project("a", conf=conf_a)
        self.add_project("b", conf=conf_b)
        self.commit_all()
        self.install_precommit()
        cases = (("a/x.aaa", False), ("a/x.bbb", True), ("b/x.bbb", False), ("b/x.aaa", True))
        for name, ok in cases:
            with self.subTest(name=name):
                self.write(name)
                self.stage(name)
                r = self.try_commit()
                if ok:
                    self.assertEqual(r.returncode, 0, r.stderr)
                else:
                    self.assertNotEqual(r.returncode, 0)
                    self.assertIn("x.", r.stderr)
                    self.unstage_all()

    def test_nearest_project_wins_for_a_nested_project(self):
        self.add_project(".", conf='KIT_DIR="agent-kit"\nFORBIDDEN=( \'*.rootonly\' )\nPROTECTED=( )\n')
        self.add_project("proj", conf='KIT_DIR="agent-kit"\nFORBIDDEN=( \'*.projonly\' )\nPROTECTED=( )\n')
        self.commit_all()
        self.install_precommit()
        self.write("proj/a.rootonly")
        self.stage("proj/a.rootonly")
        self.assertEqual(self.try_commit().returncode, 0)
        self.write("proj/a.projonly")
        self.stage("proj/a.projonly")
        self.assertNotEqual(self.try_commit().returncode, 0)


if __name__ == "__main__":
    unittest.main()
