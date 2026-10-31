"""Behaviour tests for agent-kit/claude-code/hooks/guard_git.py.

Each case pipes a PreToolUse payload to the hook, as Claude Code does, from
inside a throwaway git repo under .scratch/ whose current branch is set with a
real checkout. Cloud env vars inherited from the session are removed first.

Phase 1 locks in the core denial: the hook has no cloud-session allow path,
so every push is blocked, even with AGENT_KIT_CLOUD_PUSH=1 and
CLAUDE_CODE_REMOTE=true on a claude/ branch. Phase 6 changes these tests when
it adds the cloud-session module.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD = REPO / "agent-kit" / "claude-code" / "hooks" / "guard_git.py"
SCRATCH = REPO / ".scratch"
CLOUD_VARS = ("AGENT_KIT_CLOUD_PUSH", "CLAUDE_CODE_REMOTE")
BOTH = {"AGENT_KIT_CLOUD_PUSH": "1", "CLAUDE_CODE_REMOTE": "true"}
GIT_TEST_CONFIG = [
    "-c", "user.name=Guard Test", "-c", "user.email=guard-test@example.invalid",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=.git/no-hooks",
]


class GuardGitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SCRATCH.mkdir(exist_ok=True)
        cls.workdir = Path(tempfile.mkdtemp(prefix="guard-git-", dir=SCRATCH))
        cls.repo = cls.workdir / "repo"
        cls.repo.mkdir()
        cls.git("init", "-q", "-b", "main")
        (cls.repo / "README.md").write_text("guard test\n", encoding="utf-8")
        cls.git("add", "README.md")
        cls.git("commit", "-q", "-m", "initial")
        for branch in ("feature/x", "claude/x"):
            cls.git("branch", branch)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.workdir, ignore_errors=True)

    @classmethod
    def git(cls, *args):
        subprocess.run(["git", *GIT_TEST_CONFIG, *args], cwd=cls.repo, check=True,
                       capture_output=True, text=True)

    def checkout(self, branch):
        self.git("checkout", "-q", branch)
        current = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=self.repo,
                                 check=True, capture_output=True, text=True).stdout.strip()
        self.assertEqual(current, branch)

    def run_guard(self, stdin, extra_env=None):
        env = {k: v for k, v in os.environ.items() if k not in CLOUD_VARS}
        env.update(extra_env or {})
        return subprocess.run([sys.executable, "-B", str(GUARD)], input=stdin, cwd=self.repo,
                              env=env, capture_output=True, text=True, timeout=30)

    def run_command(self, command, extra_env=None):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
        return self.run_guard(payload, extra_env)

    def assert_push_blocked(self, result):
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Blocked by the agent kit", result.stderr)
        self.assertIn("Don't push", result.stderr)

    # Push cases: all blocked.

    def test_push_blocked_without_cloud_env(self):
        self.checkout("claude/x")
        self.assert_push_blocked(self.run_command("git push -u origin claude/x"))

    def test_push_blocked_with_cloud_push_but_not_remote(self):
        self.checkout("claude/x")
        result = self.run_command("git push -u origin claude/x", {"AGENT_KIT_CLOUD_PUSH": "1"})
        self.assert_push_blocked(result)

    def test_push_blocked_with_both_vars_on_main(self):
        self.checkout("main")
        self.assert_push_blocked(self.run_command("git push origin main", BOTH))

    def test_push_blocked_with_both_vars_on_feature_branch(self):
        self.checkout("feature/x")
        self.assert_push_blocked(self.run_command("git push -u origin feature/x", BOTH))

    def test_force_push_blocked_with_both_vars_on_claude_branch(self):
        self.checkout("claude/x")
        self.assert_push_blocked(self.run_command("git push --force origin claude/x", BOTH))

    def test_push_of_main_blocked_with_both_vars_on_claude_branch(self):
        self.checkout("claude/x")
        self.assert_push_blocked(self.run_command("git push origin main", BOTH))

    # Happy path and unparseable input: let through.

    def test_git_status_allowed(self):
        self.checkout("main")
        for env in (None, BOTH):
            result = self.run_command("git status", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")

    def test_explicit_git_add_allowed(self):
        self.checkout("main")
        for env in (None, BOTH):
            result = self.run_command("git add agent-kit/README.md", env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")

    def test_malformed_json_allowed(self):
        result = self.run_guard('{"tool_name": "Bash", "tool_input": ')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_broad_add_still_blocked(self):
        result = self.run_command("git add .")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Stage explicit paths only", result.stderr)


if __name__ == "__main__":
    unittest.main()
