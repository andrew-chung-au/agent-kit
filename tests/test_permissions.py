"""Configuration tests for the kit's tool permission rules.

These tests read agent-kit/claude-code/settings.json and
agent-kit/opencode/opencode.json and evaluate the rules with a small model of
each tool's matching. They check configuration, not the live tools: QA checks
the behaviour in each tool that is available.

The OpenCode tests check structure and order only, under this file's model of
last-match-wins. They never run OpenCode's real matcher, so they do not show
how OpenCode splits a chain, treats a path argument or applies
`external_directory`; those are by-hand checks (agent-kit/opencode/START.md).

Models used:
- Both tools: in a command rule `*` matches any characters, a trailing ` *`
  also matches the bare command (`git status *` matches `git status`), and a
  rule without `*` matches exactly.
- Claude Code: a deny rule wins over an allow rule, whatever the order.
  An Edit rule without a `/` matches the file name, and `*` there doesn't
  cross `/`.
- OpenCode: the last matching rule wins (agent-kit/opencode/START.md), so the
  general `*` rule comes first and specific rules after it. `*` matches any
  characters.
"""
from __future__ import annotations

import fnmatch
import json
import re
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent / "agent-kit"
CLAUDE = json.loads((KIT / "claude-code" / "settings.json").read_text(encoding="utf-8"))["permissions"]
OPENCODE = json.loads((KIT / "opencode" / "opencode.json").read_text(encoding="utf-8"))["permission"]

ALLOWED_COMMANDS = [
    "git remote", "git remote -v", "git remote show origin", "git remote get-url origin",
    "git cat-file -p HEAD", "gh issue view 22", "gh issue list", "gh run list",
    "gh run view 123", "sha256sum file",
]
REFUSED_COMMANDS = [
    "git remote add origin x", "git remote remove origin", "git remote rename origin up",
    "git remote set-url origin x", "git remote set-head origin -a",
    "git remote set-branches origin main", "git remote prune origin", "git remote update",
    "git remote update origin", "gh run view 123 --log", "gh run view 123 --log-failed",
    "gh run view --log 123",
]
ENV_DENIED = [".env", ".env.local", ".env.production.local"]
EDIT_DENY_RULES = ["Edit(.env)", "Edit(.env.local)", "Edit(.env.*.local)"]


def wildcard(pattern: str, text: str) -> bool:
    """`*` matches any characters; a trailing ` *` also matches the bare command."""
    optional_tail = pattern.endswith(" *")
    if optional_tail:
        pattern = pattern[:-2]
    regex = "".join(".*" if ch == "*" else re.escape(ch) for ch in pattern)
    if optional_tail:
        regex += "(?: .*)?"
    return re.fullmatch(regex, text, flags=re.DOTALL) is not None


def rule_body(rule: str, tool: str):
    prefix = tool + "("
    if rule.startswith(prefix) and rule.endswith(")"):
        return rule[len(prefix):-1]
    return None


def claude_matches(rule: str, tool: str, value: str) -> bool:
    body = rule_body(rule, tool)
    if body is None:
        return False
    if tool == "Bash":
        return wildcard(body, value)
    name = value.rsplit("/", 1)[-1]
    return "/" not in body and fnmatch.fnmatchcase(name, body) and "/" not in name


def claude_decision(tool: str, value: str) -> str:
    """Claude Code: deny wins over ask and allow, whatever the order."""
    for decision in ("deny", "ask", "allow"):
        if any(claude_matches(rule, tool, value) for rule in CLAUDE.get(decision, [])):
            return decision
    return "ask"


def opencode_decision(section: str, value: str) -> str:
    """OpenCode: the last matching rule wins."""
    decision = "ask"
    for pattern, action in OPENCODE[section].items():
        if wildcard(pattern, value):
            decision = action
    return decision


class WildcardModelTest(unittest.TestCase):
    def test_model_matches_exactly_without_star(self):
        self.assertTrue(wildcard("git remote", "git remote"))
        self.assertFalse(wildcard("git remote", "git remote add origin x"))
        self.assertTrue(wildcard("gh run view *--log*", "gh run view 1 --log-failed"))

    def test_model_deny_wins_and_last_match_wins(self):
        self.assertEqual(claude_decision("Bash", "git push origin main"), "deny")
        self.assertEqual(opencode_decision("read", ".env.example"), "allow")
        self.assertEqual(opencode_decision("read", ".env"), "deny")


class EnvEditDenyTest(unittest.TestCase):
    def test_claude_code_has_exact_env_edit_denies(self):
        for rule in EDIT_DENY_RULES:
            self.assertIn(rule, CLAUDE["deny"])
        self.assertNotIn("Edit(.env*)", CLAUDE["deny"])
        for rule in CLAUDE["deny"]:
            if rule.startswith("Edit("):
                self.assertFalse(rule.startswith("Edit(/"), rule)

    def test_claude_code_env_edit_mirrors_read_deny(self):
        reads = sorted(r[len("Read("):] for r in CLAUDE["deny"] if r.startswith("Read(.env"))
        edits = sorted(r[len("Edit("):] for r in CLAUDE["deny"] if r.startswith("Edit(.env"))
        self.assertEqual(reads, edits)

    def test_claude_code_denies_env_edits(self):
        for name in ENV_DENIED:
            self.assertEqual(claude_decision("Edit", name), "deny", name)
            self.assertEqual(claude_decision("Edit", "config/" + name), "deny", name)

    def test_claude_code_keeps_env_example_editable(self):
        for rule in EDIT_DENY_RULES:
            self.assertFalse(claude_matches(rule, "Edit", ".env.example"), rule)
        self.assertNotEqual(claude_decision("Edit", ".env.example"), "deny")

    def test_opencode_has_exact_env_edit_rules_in_order(self):
        edit = list(OPENCODE["edit"].items())
        self.assertEqual(edit[0], ("*", "allow"))
        self.assertIn(("*.env", "deny"), edit)
        self.assertIn(("*.env.*", "deny"), edit)
        self.assertIn(("*.env.example", "allow"), edit)
        self.assertNotIn("*.env*", OPENCODE["edit"])
        keys = [k for k, _ in edit]
        self.assertLess(keys.index("*.env.*"), keys.index("*.env.example"))

    def test_opencode_denies_env_edits(self):
        for name in ENV_DENIED:
            self.assertEqual(opencode_decision("edit", name), "deny", name)

    def test_opencode_keeps_env_example_editable(self):
        self.assertEqual(opencode_decision("edit", ".env.example"), "allow")


class ReadOnlyAllowTest(unittest.TestCase):
    def test_claude_code_allows_read_only_commands(self):
        for command in ALLOWED_COMMANDS:
            self.assertEqual(claude_decision("Bash", command), "allow", command)

    def test_claude_code_refuses_mutating_and_log_commands(self):
        for command in REFUSED_COMMANDS:
            self.assertEqual(claude_decision("Bash", command), "deny", command)

    def test_opencode_allows_read_only_commands(self):
        for command in ALLOWED_COMMANDS:
            self.assertEqual(opencode_decision("bash", command), "allow", command)

    def test_opencode_refuses_mutating_and_log_commands(self):
        for command in REFUSED_COMMANDS:
            self.assertEqual(opencode_decision("bash", command), "deny", command)

    def test_no_broad_git_remote_allow(self):
        self.assertNotIn("Bash(git remote *)", CLAUDE["allow"])
        self.assertNotIn("git remote*", OPENCODE["bash"])
        self.assertNotIn("git remote *", OPENCODE["bash"])

    def test_no_allow_rule_matches_a_mutating_git_remote(self):
        # The required `gh run view` allows do match `--log` forms; the denies
        # above refuse those (deny wins / last match wins), as the refused
        # command tests show.
        for command in REFUSED_COMMANDS:
            for rule in CLAUDE["allow"]:
                if command.startswith("git remote"):
                    self.assertFalse(claude_matches(rule, "Bash", command), (rule, command))
            allows = [p for p, a in OPENCODE["bash"].items() if a == "allow" and p != "*"]
            if command.startswith("git remote"):
                for pattern in allows:
                    self.assertFalse(wildcard(pattern, command), (pattern, command))

    def test_opencode_denies_come_after_their_allows(self):
        keys = list(OPENCODE["bash"])
        for deny in ("git remote add *", "git remote set-head *", "git remote set-branches *",
                     "gh run view *--log*", "gh run view *--log-failed*"):
            self.assertEqual(OPENCODE["bash"][deny], "deny")
            self.assertGreater(keys.index(deny), keys.index("gh run view*"), deny)

    def test_claude_code_has_every_listed_rule(self):
        for rule in ("Bash(git cat-file *)", "Bash(git remote)", "Bash(git remote -v)",
                     "Bash(git remote show *)", "Bash(git remote get-url *)", "Bash(gh issue view *)",
                     "Bash(gh issue list *)", "Bash(gh run list *)", "Bash(gh run view *)",
                     "Bash(sha256sum *)"):
            self.assertIn(rule, CLAUDE["allow"])
        for rule in ("Bash(git remote add *)", "Bash(git remote remove *)", "Bash(git remote rename *)",
                     "Bash(git remote set-head *)", "Bash(git remote set-branches *)",
                     "Bash(git remote set-url *)", "Bash(git remote prune *)",
                     "Bash(git remote update *)", "Bash(gh run view *--log*)",
                     "Bash(gh run view *--log-failed*)"):
            self.assertIn(rule, CLAUDE["deny"])


# ---- Issue #47: the OpenCode bash template refresh ----------------------------
# Every check below is structure and order under this file's model of
# last-match-wins (see the module docstring). None of it runs OpenCode's real
# matcher, so it cannot show how OpenCode treats a path argument, a chain or
# `external_directory`: those are three by-hand checks for the human (START.md).

BASH = OPENCODE["bash"]
KEYS = list(BASH)
FIRST_DENY = next(i for i, k in enumerate(KEYS) if BASH[k] == "deny")
ALLOW_KEYS = [k for k in KEYS if BASH[k] == "allow"]
META_ASKS = ["*$*", "*`*", "*;*", "*&*", "*|*", "*>*", "*<*", "*\n*"]
PATH_ASKS = ["* /*", "*../*", "* ..", "* ~*", "grep -r*", "grep -R*", "grep * -r*",
             "grep * -R*", "grep *--recursive*"]

NEW_ALLOWED = [
    "make test", "git status", "git status -s", "git diff HEAD", "git log -1", "git show HEAD",
    "git rev-parse HEAD", "git rev-list HEAD", "git ls-files", "git blame x", "git describe",
    "git cat-file -p HEAD", "git worktree list", "git remote", "git remote -v",
    "git remote show origin", "git remote get-url origin", "git fetch", "git fetch origin",
    "git branch --show-current", "git branch -vv", "git config --get user.name",
    "gh issue list", "gh issue view 47", "gh run list", "gh run view 1", "gh pr list",
    "gh pr view 3", "gh label list", "gh repo view", "command -v make", "id", "pwd", "ls x",
    "date", "date -u", "realpath x", "basename x", "dirname x", "wc -w x", "grep x y",
    "head -n 1 x", "tail x", "diff a b", "stat x", "file x", "sha256sum x",
    "git commit -m x", "git diff --output-indicator-new=x", "git log main..HEAD",
    "git diff HEAD~1",
]
NOT_ALLOWED_PATTERNS = [
    "echo *", "jq *", "rg *", "date*", "git branch -vv*", "git branch --show-current*",
    "git add *", "git fetch*", "git push*", "gh run watch*", "gh issue comment*", "pgrep *",
    "python3 *", "python *", "node *", "bash *", "sh *",
]
NOT_ALLOWED_COMMANDS = [
    "echo $GITHUB_TOKEN", "echo x", "jq -n env", "jq . x", "rg --pre x y", "rg x", "date -s x",
    "date -d x", "git branch -D x", "git branch -vv -D x", "git branch --show-current -D x",
    "git add x", "git add src", "git push", "gh run watch 1", "gh issue comment 5 --body x",
    "pgrep -a x", "pgrep -f x", "python3 x.py", "node x.js", "bash x.sh", "sh x.sh",
    "gh auth status", "git config --get-regexp .", "git config --list",
]
FETCH_ASK = [
    "git fetch --upload-pack=touch origin", "git fetch --upload-pack touch", "git fetch -u x",
    "git fetch origin main", "git fetch --all", "git fetch origin; ls",
]
GH_WRITE_ASK = [
    "gh issue comment 5 --body x", "gh issue create", "gh issue edit 5", "gh issue close 5",
    "gh issue reopen 5", "gh issue delete 5", "gh api repos/x/y",
]
NOT_ALLOW_COMMIT = [
    "git commit --amend -m x", "git commit -m x --amend", "git commit -n -m x",
    "git commit -m x -n", "git commit -nm x", "git commit -am x", "git commit -m x -a",
]
COMMIT_DENY = [
    "git commit -n -m x", "git commit -m x -n", "git commit -nm x", "git commit -am x",
    "git commit -m x -a", "git commit --all -m x", "git commit -m x --all",
    "git commit -m x --no-verify",
]
CREDENTIAL_DENY = [
    "gh auth token", "gh auth status --show-token", "gh auth status -t",
    "gh auth git-credential get", "git credential fill", "git credential approve",
    "git credential reject", "git config --get credential.helper",
    "git config --get-all credential.helper",
]
PATH_ASK = [
    "head -n 1 /proc/self/environ", "tail /proc/self/environ", "grep -r x /etc",
    "diff /etc/passwd x", "stat /etc/hostname", "file /bin/ls",
    "sha256sum /proc/self/environ", "head ../../x", "head ~/.bashrc", "ls /proc/self",
]
RECURSIVE_ASK = [
    "grep -r x .", "grep -R x .", "grep -rn x .", "grep --recursive x .", "grep x -r .",
]
CHAIN_ASK = [
    "ls ; touch x", "ls && touch x", "ls | head", "ls $(touch x)", "ls `touch x`",
    "ls > x", "ls >x", "ls<x", "ls\ntouch x", "make test; touch x", "git status; git push",
]
ENV_SHELL_DENY = [
    "cat .env", "cat .env.local", "cp .env x", "cat .env.example .env",
    "cat .env .env.example", "head .env", "grep x .env.production", "cat .env.example",
]
EDIT_ASKS = ["AGENTS.md", "CLAUDE.md", "Makefile", "agent-kit.conf", "_docs/specs.md",
             "_docs/agent-kit/*", "opencode.json", ".opencode/*", ".claude/*"]


class BashTemplateOrderTest(unittest.TestCase):
    def test_bash_object_is_ordered(self):
        self.assertEqual(KEYS[0], "*")
        self.assertEqual(BASH["*"], "ask")
        self.assertEqual(KEYS[-1], "*.env*")
        self.assertEqual(BASH["*.env*"], "deny")
        last_allow = max(KEYS.index(k) for k in ALLOW_KEYS)
        for key in META_ASKS + PATH_ASKS:
            self.assertEqual(BASH[key], "ask", key)
            self.assertGreater(KEYS.index(key), last_allow, key)
            self.assertLess(KEYS.index(key), FIRST_DENY, key)

    def test_no_ask_comes_after_a_deny(self):
        # An ask after a deny would downgrade it (`git push $X`).
        for key in KEYS[FIRST_DENY:]:
            self.assertEqual(BASH[key], "deny", key)

    def test_no_env_example_allow_in_bash(self):
        for key in KEYS:
            self.assertNotIn("example", key)

    def test_credential_denies_sit_after_the_allows_they_would_lose_to(self):
        self.assertLess(KEYS.index("git config --get *"), KEYS.index("git config *credential*"))
        for key in ("gh auth token*", "gh auth status*--show-token*", "gh auth status*-t*",
                    "gh auth git-credential*", "git credential*", "git config *credential*"):
            self.assertEqual(BASH[key], "deny", key)
            self.assertGreater(KEYS.index(key), max(KEYS.index(a) for a in ALLOW_KEYS), key)
            self.assertGreater(KEYS.index(key), max(KEYS.index(m) for m in META_ASKS), key)

    def test_amend_ask_is_before_the_denies(self):
        self.assertEqual(BASH["git commit *--amend*"], "ask")
        self.assertGreater(KEYS.index("git commit *--amend*"), KEYS.index("git commit *"))

    def test_template_edit_asks_follow_the_env_rules(self):
        edit = OPENCODE["edit"]
        keys = list(edit)
        for key in EDIT_ASKS:
            self.assertEqual(edit[key], "ask", key)
            self.assertGreater(keys.index(key), keys.index("*.env.example"), key)


class BashTemplateDecisionTest(unittest.TestCase):
    def decide(self, command):
        return opencode_decision("bash", command)

    def test_allowed_commands(self):
        for command in NEW_ALLOWED:
            self.assertEqual(self.decide(command), "allow", command)

    def test_every_listed_allow_exists(self):
        for key in ("make *", "git status*", "git rev-parse*", "git worktree list*", "git fetch",
                    "git fetch origin", "git branch --show-current", "git branch -vv",
                    "git config --get *", "git commit *", "gh pr view*", "gh repo view*",
                    "command -v *", "id", "pwd", "ls *", "date", "date -u", "wc *", "grep *",
                    "head *", "tail *", "diff *", "stat *", "file *", "sha256sum *"):
            self.assertEqual(BASH.get(key), "allow", key)

    def test_not_allowed_patterns_are_absent_from_the_allows(self):
        for pattern in NOT_ALLOWED_PATTERNS:
            self.assertNotEqual(BASH.get(pattern), "allow", pattern)

    def test_not_allowed_commands_are_refused(self):
        for command in NOT_ALLOWED_COMMANDS:
            self.assertIn(self.decide(command), ("ask", "deny"), command)

    def test_git_fetch_only_in_two_exact_forms(self):
        for command in FETCH_ASK:
            self.assertEqual(self.decide(command), "ask", command)

    def test_raw_gh_writes_ask(self):
        for command in GH_WRITE_ASK:
            self.assertEqual(self.decide(command), "ask", command)
        for pattern in ("gh issue comment*", "gh issue create*", "gh issue edit*",
                        "gh issue close*", "gh issue reopen*", "gh issue delete*", "gh api*"):
            self.assertEqual(BASH[pattern], "ask", pattern)
        self.assertEqual(BASH["make *"], "allow")
        self.assertEqual(self.decide("make issue-comment N=5"), "allow")

    def test_commit_rules(self):
        for command in NOT_ALLOW_COMMIT:
            self.assertNotEqual(self.decide(command), "allow", command)
        self.assertEqual(self.decide("git commit --amend -m x"), "ask")
        self.assertEqual(self.decide("git commit -m x --amend"), "ask")
        for command in COMMIT_DENY:
            self.assertEqual(self.decide(command), "deny", command)

    def test_human_approved_commit_prompts(self):
        self.assertEqual(self.decide("HUMAN_APPROVED=1 git commit -m x"), "ask")

    def test_credential_commands_denied(self):
        for command in CREDENTIAL_DENY:
            self.assertEqual(self.decide(command), "deny", command)

    def test_config_listing_asks(self):
        self.assertEqual(self.decide("git config --get-regexp ."), "ask")
        self.assertEqual(self.decide("git config --list"), "ask")
        self.assertEqual(self.decide("gh auth status"), "ask")

    def test_path_arguments_ask(self):
        for command in PATH_ASK:
            self.assertEqual(self.decide(command), "ask", command)

    def test_recursive_grep_asks(self):
        for command in RECURSIVE_ASK:
            self.assertEqual(self.decide(command), "ask", command)

    def test_chains_and_substitution_ask(self):
        for command in CHAIN_ASK:
            self.assertEqual(self.decide(command), "ask", command)

    def test_chain_after_a_denied_command_stays_denied(self):
        self.assertEqual(self.decide("git push $X"), "deny")
        self.assertEqual(self.decide("git push; ls"), "deny")

    def test_env_in_shell_commands_denied(self):
        for command in ENV_SHELL_DENY:
            self.assertEqual(self.decide(command), "deny", command)

    def test_documented_env_false_positives_are_denied(self):
        for command in ("cat my.env.txt", "ls .envrc", "cat .environment",
                        'git commit -m "document the .env rule"'):
            self.assertEqual(self.decide(command), "deny", command)

    def test_output_flag_narrowed(self):
        self.assertNotIn("*--output*", BASH)
        for command in ("git diff --output=x", "git log --output x"):
            self.assertEqual(self.decide(command), "deny", command)
        self.assertEqual(self.decide("git diff --output-indicator-new=x"), "allow")


if __name__ == "__main__":
    unittest.main()
