"""agent-kit/githooks/pre-push reads changed names NUL-delimited (issue #42).

A name git would quote in plain output (non-ASCII, double quote, backslash) must
still reach find_project as the real path, so the right projects run `make verify`.
The projects are stub Makefiles that record their folder and BASE. Every hook run
uses a PATH with no git-lfs, as in test_gate_pre_push.py.
"""
from __future__ import annotations

import unittest

import test_gate_pre_push as base
from kit_repo import KitTestCase, KIT, DEFAULT_CONF, UNUSUAL_NAMES

HOOK = KIT / "githooks" / "pre-push"


class PrePushNamesTest(KitTestCase):
    no_lfs_path = base.PrePushTest.no_lfs_path

    def setUp(self):
        super().setUp()
        self.record = self.work / "verify-record"
        self.origin = self.work / "origin.git"
        self.run_cmd(["git", "init", "-q", "--bare", str(self.origin)], cwd=self.work)
        self.git("remote", "add", "origin", str(self.origin))
        # No agent-kit.conf at the repo root: only the subfolder is a project.
        self.write("proj/agent-kit.conf", DEFAULT_CONF)
        self.write("proj/Makefile", base.STUB_MAKEFILE)
        self.write("bare/readme.txt", "no project here\n")
        self.base = self.commit_all("base")
        self.slate_ref = self.base
        self.git("push", "-q", "origin", "main")

    def hook(self, new):
        line = "refs/heads/main %s refs/heads/main %s\n" % (new, self.base)
        return self.run_cmd(["bash", HOOK, "origin", str(self.origin)], stdin=line,
                            env={"RECORD": str(self.record), "PATH": self.no_lfs_path()})

    def verified(self):
        if not self.record.exists():
            return []
        return self.record.read_text(encoding="utf-8").splitlines()

    def commit_files(self, *rels):
        for r in rels:
            self.write(r, "changed\n")
        return self.commit_all("change")

    def test_an_unusual_named_file_in_a_subfolder_project_verifies_it_once(self):
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.record.unlink(missing_ok=True)
                new = self.commit_files("proj/%s.txt" % name)
                r = self.hook(new)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(self.verified(), ["proj BASE=" + self.base])

    def test_an_unusual_named_file_with_no_project_above_it_runs_nothing(self):
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.record.unlink(missing_ok=True)
                new = self.commit_files("bare/%s.txt" % name)
                r = self.hook(new)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(self.verified(), [])

    def test_a_root_project_and_a_subfolder_project_both_touched_both_run(self):
        # Give the repo root a project too, committed before the pushed change.
        self.write("agent-kit.conf", DEFAULT_CONF)
        self.write("Makefile", base.STUB_MAKEFILE)
        self.base = self.commit_all("root project")
        self.slate_ref = self.base
        self.git("push", "-q", "origin", "main")
        root_name = self.repo.name
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.record.unlink(missing_ok=True)
                new = self.commit_files("top-%s.txt" % name, "proj/%s.txt" % name)
                r = self.hook(new)
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(sorted(self.verified()),
                                 sorted([root_name + " BASE=" + self.base, "proj BASE=" + self.base]))

    def test_a_failing_verify_for_an_unusual_named_file_still_blocks(self):
        self.write("proj/verify-fails", "x\n")
        self.base = self.commit_all("make verify fail")
        self.slate_ref = self.base
        self.git("push", "-q", "origin", "main")
        for label, name in UNUSUAL_NAMES.items():
            with self.subTest(label):
                self.record.unlink(missing_ok=True)
                new = self.commit_files("proj/%s.txt" % name)
                r = self.hook(new)
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("verify failed, push blocked", r.stderr)
                self.assertEqual(self.verified(), ["proj BASE=" + self.base])


class HookVersionTest(KitTestCase):
    def test_hook_header_is_version_3(self):
        header = HOOK.read_text(encoding="utf-8").splitlines()[1]
        self.assertEqual(header, "# agent-kit-hooks-version: 3")

    def test_install_hooks_upgrades_a_version_2_hook_to_3(self):
        self.add_project()
        self.commit_all()
        installed = self.repo / ".githooks"
        installed.mkdir()
        v2 = HOOK.read_text(encoding="utf-8").replace(
            "# agent-kit-hooks-version: 3", "# agent-kit-hooks-version: 2", 1)
        self.assertIn("version: 2", v2)
        (installed / "pre-push").write_text(v2, encoding="utf-8")
        r = self.run_cmd(["bash", "agent-kit/scripts/install-hooks.sh"])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("updated .githooks/pre-push to version 3", r.stdout)
        self.assertEqual((installed / "pre-push").read_bytes(), HOOK.read_bytes())


if __name__ == "__main__":
    unittest.main()
