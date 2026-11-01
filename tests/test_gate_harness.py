"""Tests for the throwaway-repo helper itself (tests/kit_repo.py).

They pin the fresh-checkout independence the gate tests rely on: nothing from
the machine's git config, a scratch folder that may not exist yet, the
HUMAN_APPROVED variable never inherited, and a docker stub that no test may
reach by accident.
"""
from __future__ import annotations

import os
import shutil
import unittest
from unittest import mock

from kit_repo import KitTestCase, SCRATCH, build_env, new_workdir


class HarnessTest(KitTestCase):
    def test_identity_is_fixed_and_hooks_path_unset(self):
        self.assertEqual(self.git("config", "--get", "user.email").stdout.strip(), "kit-test@example.invalid")
        self.assertNotEqual(self.git("config", "--get", "core.hooksPath", check=False).returncode, 0)

    def test_no_git_config_from_outside_the_throwaway_repo(self):
        listing = self.git("config", "--list", "--show-origin").stdout.splitlines()
        self.assertTrue(listing)
        for line in listing:
            origin = line.split("\t", 1)[0]
            if origin.startswith("file:"):
                # git prints the repo's own config relative to the repo (file:.git/config)
                inside = origin.startswith("file:.git/") or str(self.work) in origin
                self.assertTrue(inside, "config read from outside the throwaway folder: " + line)

    def test_global_and_system_config_are_empty(self):
        for scope in ("--global", "--system"):
            self.assertEqual(self.git("config", scope, "--list", check=False).stdout.strip(), "", scope)

    def test_tmpdir_is_under_the_work_folder(self):
        self.assertTrue(self.env["TMPDIR"].startswith(str(self.work)))

    def test_inherited_approval_and_kit_variables_are_dropped(self):
        with mock.patch.dict(os.environ, {"HUMAN_APPROVED": "1", "FORCE": "1", "GIT_DIR": "/nowhere",
                                          "AGENT_PUSH_CHECK_PLAN": "1"}):
            env = build_env(self.work)
        for name in ("HUMAN_APPROVED", "FORCE", "GIT_DIR", "AGENT_PUSH_CHECK_PLAN"):
            self.assertNotIn(name, env)

    def test_scratch_folder_is_created_when_missing(self):
        parent = new_workdir(SCRATCH, "kit-gate-harness-")
        self.addCleanup(shutil.rmtree, parent, ignore_errors=True)
        missing = parent / "not" / "yet" / ".scratch"
        self.assertFalse(missing.exists())
        made = new_workdir(missing)
        self.assertTrue(made.is_dir())
        self.assertEqual(made.parent, missing)

    def test_docker_stub_exits_99_and_leaves_a_marker(self):
        self.docker_expected = True
        r = self.run_cmd(["docker", "run", "x"])
        self.assertEqual(r.returncode, 99)
        self.assertIn("DOCKER-STUB-CALLED", r.stderr)
        self.assertTrue((self.work / "docker-called").exists())
        self.clear_docker_marker()
        self.assertFalse((self.work / "docker-called").exists())


if __name__ == "__main__":
    unittest.main()
