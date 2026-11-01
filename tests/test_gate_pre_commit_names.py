"""The pre-commit dispatcher and unusual file names (issue #1).

The dispatcher must read the staged list NUL-delimited (-z): git quotes a name
with a double quote or a backslash even with core.quotePath=false, so a quoted
path inside a subfolder project was not assigned to that project and the
project's checks never ran. Also pins hook version 4 and the upgrade from 3.
"""
from __future__ import annotations

import unittest

from kit_repo import KIT, KitTestCase, UNUSUAL_NAMES

HOOK = KIT / "githooks" / "pre-commit"


class PreCommitNamesTest(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.add_project("proj")
        self.write("README.md")
        self.commit_all()
        self.install_precommit()

    def assert_refused(self, path, shown=None):
        """Refused, with the real name on stderr (check-staged.sh names paths relative to its project)."""
        r = self.try_commit()
        self.assertNotEqual(r.returncode, 0, "committed %r" % path)
        self.assertIn("  " + (shown or path) + "\n", r.stderr)

    def test_repo_root_protected_names_are_refused_and_approvable(self):
        for label, base in UNUSUAL_NAMES.items():
            for folder in (".github/", ".vscode/", ".githooks/", ".devcontainer/"):
                path = folder + base + ".yml"
                with self.subTest(name=label, folder=folder):
                    self.write(path)
                    self.stage(path)
                    self.assert_refused(path)
                    self.assertEqual(self.try_commit(approved="1").returncode, 0)

    def test_forbidden_names_in_a_subfolder_project_are_refused(self):
        for label, base in UNUSUAL_NAMES.items():
            path = "proj/" + base + ".pem"
            with self.subTest(name=label):
                self.write(path)
                self.stage(path)
                self.assert_refused(path, shown=base + ".pem")
                self.unstage_all()

    def test_protected_names_in_a_subfolder_project_need_approval(self):
        for label, base in UNUSUAL_NAMES.items():
            path = "proj/docs/" + base + ".md"
            with self.subTest(name=label):
                self.write(path)
                self.stage(path)
                self.assert_refused(path, shown="docs/" + base + ".md")
                self.assertEqual(self.try_commit(approved="1").returncode, 0)

    def test_a_quoted_name_in_a_subfolder_still_runs_that_projects_checks(self):
        # A whitespace error is only found by that project's check-staged.sh run.
        self.write('proj/a"b.txt', "trailing \n")
        self.stage('proj/a"b.txt')
        r = self.try_commit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("whitespace", r.stderr)


class HookVersionTest(KitTestCase):
    def test_hook_header_is_version_4(self):
        header = HOOK.read_text(encoding="utf-8").splitlines()[1]
        self.assertEqual(header, "# agent-kit-hooks-version: 4")

    def test_install_hooks_upgrades_a_version_3_hook_to_4(self):
        self.add_project()
        self.commit_all()
        installed = self.repo / ".githooks"
        installed.mkdir()
        v3 = HOOK.read_text(encoding="utf-8").replace(
            "# agent-kit-hooks-version: 4", "# agent-kit-hooks-version: 3", 1)
        self.assertIn("version: 3", v3)
        (installed / "pre-commit").write_text(v3, encoding="utf-8")
        r = self.run_cmd(["bash", "agent-kit/scripts/install-hooks.sh"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("updated .githooks/pre-commit to version 4", r.stdout)
        self.assertEqual((installed / "pre-commit").read_bytes(), HOOK.read_bytes())


if __name__ == "__main__":
    unittest.main()
