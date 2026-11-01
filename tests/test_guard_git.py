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

    # Issue #39: shell commands naming .env files.

    ENV_REFUSED = [
        "cat .env", "less .env", "grep x .env", "cp .env .scratch/x", "cp .env.example .env",
        "echo x > .env", "cat < .env", "cat <.env",
        "cat ./.env", "cat sub/dir/.env", 'cat "/workspaces/proj/.env"', "cat '.env'",
        "cat .env.local", "cat .env.production.local", "cat .env.example.bak",
        "echo hi && cat .env", "cat .env | head", "echo $(cat .env)", "echo `cat .env`",
        "FOO=1 cat .env", "sudo cat .env",
        "grep -f .env x", "cat --file=.env",
        "ls .env", "git check-ignore .env",
        # option-like and odd shapes
        "cat -- .env", "cat -n .env", "cat .env;", "cat >>.env", "cat 2>.env", "cat --file='.env'",
        "echo ok; cat .env.local", "git add .env", "f=.env", "FILE=.env cat",
    ]
    ENV_ALLOWED = [
        "cat .env.example", "grep x .env.example", "cat ./.env.example", "git add .env.example",
        "cat environment.txt", "ls .envrc.d", "cat my.env.txt", "cat .environment", "cat env",
        "cat .env_notes", "ls .envrc", "cat .ENV", "cat .env/", "cat -- ",
        'git commit -m "document the .env rule"', 'gh issue comment 39 --body "never cat .env"',
        "git status", "git add agent-kit/README.md", "make verify", "gh issue view 39",
        "", "   ", '""', "cat --", "cat -",
    ]

    def test_env_commands_refused(self):
        for command in self.ENV_REFUSED:
            with self.subTest(command=command):
                result = self.run_command(command)
                self.assertEqual(result.returncode, 2, result.stderr)
                for text in ("Blocked by the agent kit", ".env", ".env.example", "ask the human"):
                    self.assertIn(text, result.stderr)

    def test_env_lookalikes_and_ordinary_commands_allowed(self):
        for command in self.ENV_ALLOWED:
            with self.subTest(command=command):
                result = self.run_command(command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")

    def test_env_example_allowed_and_env_local_refused(self):
        self.assertEqual(self.run_command("cat .env.example").returncode, 0)
        self.assertEqual(self.run_command("cat .env.local").returncode, 2)

    def test_env_check_runs_on_non_git_commands_and_before_git_check(self):
        self.assertEqual(self.run_command("git add .env.local").returncode, 2)
        self.assertEqual(self.run_command("cat .env").returncode, 2)

    def test_env_check_fails_open_on_unparseable_or_missing_input(self):
        # Unbalanced quote: the parser can't split it, so it is let through, as today.
        self.assertEqual(self.run_command("cat '.env").returncode, 0)
        self.assertEqual(self.run_guard("{}").returncode, 0)
        self.assertEqual(self.run_guard('{"tool_input": null}').returncode, 0)
        self.assertEqual(self.run_guard('{"tool_input": {"command": null}}').returncode, 0)
        self.assertEqual(self.run_guard("").returncode, 0)

    def test_env_known_gaps_still_pass(self):
        # Documented gaps (decision 1): indirection the parser can't see.
        for command in ('bash -c "cat .env"', "cat .e*","cat $f", "cat *"):
            with self.subTest(command=command):
                self.assertEqual(self.run_command(command).returncode, 0)

    def test_hook_docstring_lists_env_block_and_gaps(self):
        text = GUARD.read_text(encoding="utf-8")
        doc = text.split('"""')[1]
        self.assertIn(".env", doc)
        self.assertIn("Known gaps", doc)
        self.assertIn("bash -c", doc)


if __name__ == "__main__":
    unittest.main()
