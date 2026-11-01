"""Behaviour tests for agent-kit/scripts/install-hooks.sh.

Run in a throwaway repo; the script only changes that repo's own core.hooksPath.
"""
from __future__ import annotations

import re
import unittest

from kit_repo import KIT, KitTestCase

HOOKS = ("pre-commit", "pre-push", "post-checkout", "post-commit", "post-merge")
LFS_HOOKS = ("pre-push", "post-checkout", "post-commit", "post-merge")


def lfs_text(name, extra=""):
    """The exact text `git lfs install` writes for a hook."""
    return (
        "#!/bin/sh\n"
        "command -v git-lfs >/dev/null 2>&1 || { echo >&2 \"\\nThis repository is configured for Git LFS "
        "but 'git-lfs' was not found on your path. If you no longer wish to use Git LFS, remove this hook "
        "by deleting the '.git/hooks/%s' file in the repo.\\n\"; exit 2; }\n"
        "git lfs %s \"$@\"\n" % (name, name)
    ) + extra


def kit_version(name):
    src = "lfs-passthrough" if name.startswith("post-") else name
    text = (KIT / "githooks" / src).read_text(encoding="utf-8")
    return int(re.search(r"^# agent-kit-hooks-version: *(\d+)", text, re.M).group(1))


class InstallHooksCase(KitTestCase):
    def setUp(self):
        super().setUp()
        self.add_project()
        self.write("README.md")
        self.commit_all()
        self.githooks = self.repo / ".githooks"

    def install(self, **env):
        return self.run_cmd(["bash", "agent-kit/scripts/install-hooks.sh"], env=env)

    def hooks_path(self):
        r = self.git("config", "--get", "core.hooksPath", check=False)
        return r.stdout.strip() if r.returncode == 0 else None

    def git_hook(self, name, text):
        p = self.repo / ".git" / "hooks" / name
        p.write_text(text, encoding="utf-8")
        p.chmod(0o755)
        return p

    def assert_nothing_installed(self):
        self.assertFalse(self.githooks.exists())
        self.assertNotEqual(self.hooks_path(), ".githooks")


class RefusedTest(InstallHooksCase):
    def test_a_sandbox_remote_is_refused(self):
        self.git("remote", "add", "sandbox", "../sandbox-repo")
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("clean clone", r.stderr)
        self.assert_nothing_installed()

    def test_the_clean_clone_push_check_is_refused(self):
        self.git_hook("pre-push", "#!/bin/sh\n# agent-kit-push-check v2\nexit 0\n")
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("clean clone", r.stderr)
        self.assert_nothing_installed()

    def test_another_hooks_path_is_refused_without_force_and_replaced_with_it(self):
        self.git("config", "core.hooksPath", "other-hooks")
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("other-hooks", r.stderr)
        self.assertEqual(self.hooks_path(), "other-hooks")
        self.assertFalse(self.githooks.exists())
        r = self.install(FORCE="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.hooks_path(), ".githooks")
        for hook in HOOKS:
            self.assertTrue((self.githooks / hook).is_file(), hook)

    def test_a_foreign_hook_in_git_hooks_is_refused_without_force_and_replaced_with_it(self):
        self.git_hook("commit-msg", "#!/bin/sh\necho custom\n")
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("commit-msg", r.stderr)
        self.assert_nothing_installed()
        r = self.install(FORCE="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.hooks_path(), ".githooks")

    def test_a_foreign_hook_already_in_githooks_is_refused_without_force_and_replaced_with_it(self):
        self.githooks.mkdir()
        mine = self.githooks / "pre-commit"
        mine.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("isn't a kit or Git LFS hook", r.stderr)
        self.assertEqual(mine.read_text(encoding="utf-8"), "#!/bin/sh\necho mine\n")
        self.assertNotEqual(self.hooks_path(), ".githooks")
        r = self.install(FORCE="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(mine.read_bytes(), (KIT / "githooks" / "pre-commit").read_bytes())

    def test_an_lfs_looking_hook_with_an_extra_command_is_not_recognised(self):
        self.git_hook("pre-push", lfs_text("pre-push", "echo extra\n"))
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("pre-push", r.stderr)
        self.assert_nothing_installed()

    def test_an_lfs_looking_hook_with_an_extra_command_in_githooks_is_refused(self):
        self.githooks.mkdir()
        (self.githooks / "post-commit").write_text(lfs_text("post-commit", "echo extra\n"), encoding="utf-8")
        r = self.install()
        self.assertEqual(r.returncode, 1)
        self.assertIn("isn't a kit or Git LFS hook", r.stderr)


class InstalledTest(InstallHooksCase):
    def test_a_clean_repo_gets_the_five_hooks(self):
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.hooks_path(), ".githooks")
        self.assertEqual(sorted(p.name for p in self.githooks.iterdir()), sorted(HOOKS))
        for hook in HOOKS:
            self.assertTrue((self.githooks / hook).stat().st_mode & 0o100, hook + " is not executable")
        self.assertEqual((self.githooks / "pre-commit").read_bytes(), (KIT / "githooks" / "pre-commit").read_bytes())

    def test_running_it_again_changes_nothing(self):
        self.install()
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count("is up to date"), 5)

    def test_an_older_version_is_upgraded(self):
        self.githooks.mkdir()
        old = self.githooks / "pre-commit"
        old.write_text("#!/bin/sh\n# agent-kit-hooks-version: 1\necho old\n", encoding="utf-8")
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("updated .githooks/pre-commit to version %d" % kit_version("pre-commit"), r.stdout)
        self.assertEqual(old.read_bytes(), (KIT / "githooks" / "pre-commit").read_bytes())

    def test_an_equal_or_newer_version_is_left_alone(self):
        self.githooks.mkdir()
        for hook, delta in (("pre-commit", 0), ("pre-push", 5)):
            text = "#!/bin/sh\n# agent-kit-hooks-version: %d\necho mine\n" % (kit_version(hook) + delta)
            (self.githooks / hook).write_text(text, encoding="utf-8")
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.count("same or a newer kit version; left as is"), 2)
        for hook in ("pre-commit", "pre-push"):
            self.assertIn("echo mine", (self.githooks / hook).read_text(encoding="utf-8"))

    def test_standard_lfs_hooks_in_git_hooks_are_reported_and_replaced_by_the_kits(self):
        for name in LFS_HOOKS:
            self.git_hook(name, lfs_text(name))
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Found standard Git LFS hooks", r.stdout)
        self.assertEqual(self.hooks_path(), ".githooks")
        self.assertEqual((self.githooks / "pre-push").read_bytes(), (KIT / "githooks" / "pre-push").read_bytes())

    def test_standard_lfs_hooks_already_in_githooks_are_replaced_and_reported(self):
        self.githooks.mkdir()
        for name in LFS_HOOKS:
            (self.githooks / name).write_text(lfs_text(name), encoding="utf-8")
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        for name in LFS_HOOKS:
            self.assertIn("replaced the Git LFS .githooks/%s" % name, r.stdout)
        self.assertEqual((self.githooks / "post-merge").read_bytes(),
                         (KIT / "githooks" / "lfs-passthrough").read_bytes())


if __name__ == "__main__":
    unittest.main()
