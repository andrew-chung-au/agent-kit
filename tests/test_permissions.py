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


# ---- Issue #47, revision: sibling subcommands, option abbreviations, chain wording ----
# Every `git <sub>` name from `git help -a` (git 2.5x, the sandbox's version).
GIT_SUBCOMMANDS = """
add am archive backfill bisect branch bundle checkout cherry-pick citool clean clone commit
describe diff fetch format-patch gc gitk grep gui history init log maintenance merge mv notes
pull push range-diff rebase reset restore revert rm scalar shortlog show sparse-checkout stash
status submodule switch tag worktree config fast-export fast-import filter-branch mergetool
pack-refs prune reflog refs remote repack replace annotate blame bugreport count-objects
diagnose difftool fsck gitweb help instaweb merge-tree rerere show-branch verify-commit
verify-tag version whatchanged apply checkout-index commit-graph commit-tree hash-object
index-pack merge-file merge-index mktag mktree multi-pack-index pack-objects prune-packed
read-tree replay symbolic-ref unpack-objects update-index update-ref write-tree cat-file
cherry diff-files diff-index diff-pairs diff-tree for-each-ref for-each-repo format-rev
get-tar-commit-id last-modified ls-files ls-remote ls-tree merge-base name-rev pack-redundant
repo rev-list rev-parse show-index show-ref unpack-file var verify-pack check-attr
check-ignore check-mailmap check-ref-format column credential credential-cache
credential-store fmt-merge-msg hook interpret-trailers mailinfo mailsplit merge-one-file
patch-id stripspace url-parse
""".split()
SIBLING_REFUSED = [
    "git difftool", "git difftool --extcmd=touch HEAD~1", "git difftool -x touch",
    "git show-ref", "git diff-tree HEAD",
]
ABBREV_DENY = ["git commit -m x --no-veri", "git commit -m x --no-verif", "git commit --no-v -m x"]
ABBREV_ASK = ["git commit --amen -m x", "git commit -m x --am"]
ABBREV_ALLOW = [
    "git commit --dry-run -m x", "git commit -m x --no-edit",
    "git commit --allow-empty-message -m x", 'git commit -m "fix the amendment text"',
]


def trailing_star_git_allows(bash):
    return [k for k, v in bash.items() if v == "allow" and k.startswith("git ") and k.endswith("*")]


def sibling_matches(bash):
    """(allow pattern, command) pairs where a trailing-star git allow matches a refused sibling."""
    hits = []
    for pattern in trailing_star_git_allows(bash):
        own = pattern[len("git "):-1].rstrip()
        for name in GIT_SUBCOMMANDS:
            if name != own and wildcard(pattern, "git " + name):
                hits.append((pattern, "git " + name))
        for command in SIBLING_REFUSED:
            if wildcard(pattern, command):
                hits.append((pattern, command))
    return hits


class SiblingAndAbbreviationTest(unittest.TestCase):
    def decide(self, command):
        return opencode_decision("bash", command)

    def test_no_trailing_star_git_allow_matches_a_sibling_subcommand(self):
        self.assertEqual(sibling_matches(BASH), [])

    def test_diff_and_show_are_paired_not_trailing_star(self):
        for key in ("git diff", "git diff *", "git show", "git show *"):
            self.assertEqual(BASH.get(key), "allow", key)
        for key in ("git diff*", "git show*"):
            self.assertNotIn(key, BASH)

    def test_refused_siblings(self):
        for command in SIBLING_REFUSED:
            self.assertNotEqual(self.decide(command), "allow", command)

    def test_allowed_diff_and_show(self):
        for command in ("git diff", "git diff --stat HEAD~1", "git show HEAD", "git show"):
            self.assertEqual(self.decide(command), "allow", command)

    def test_abbreviated_no_verify_denied(self):
        for command in ABBREV_DENY:
            self.assertEqual(self.decide(command), "deny", command)

    def test_abbreviated_amend_asks(self):
        for command in ABBREV_ASK:
            self.assertEqual(self.decide(command), "ask", command)

    def test_ordinary_commits_stay_allowed(self):
        for command in ABBREV_ALLOW:
            self.assertEqual(self.decide(command), "allow", command)

    def test_abbreviation_rules_sit_in_the_right_group(self):
        last_allow = max(KEYS.index(k) for k in ALLOW_KEYS)
        self.assertEqual(BASH["git commit *--am*"], "ask")
        self.assertGreater(KEYS.index("git commit *--am*"), last_allow)
        self.assertLess(KEYS.index("git commit *--am*"), FIRST_DENY)
        self.assertEqual(BASH["git commit *--no-v*"], "deny")
        self.assertGreater(KEYS.index("git commit *--no-v*"), last_allow)


START = (KIT / "opencode" / "START.md").read_text(encoding="utf-8")


def chain_claim_problems(text: str) -> list:
    """Why START.md misstates how OpenCode 1.19.5 treats chains (it checks each command)."""
    problems = []
    if "checks each command of a chain on its own" not in text:
        problems.append("missing the per-command statement")
    if "1.19.5" not in text or "one model" not in text:
        problems.append("missing the one-version, one-model evidence")
    for needle in (r"(?:chain|operator)s?\s+(?:always\s+)?prompts?\b",
                   r"slipped chain", r"splits a (?:command|chain)", r"because it is a chain"):
        if re.search(needle, text, re.I):
            problems.append("claims operators prompt: " + needle)
    return problems


class StartMdChainWordingTest(unittest.TestCase):
    def test_start_md_states_per_command_checking_and_makes_no_operator_claim(self):
        self.assertEqual(chain_claim_problems(START), [])

    def test_check_refuses_the_old_claims(self):
        self.assertNotEqual(chain_claim_problems(START + " A slipped chain is not cheap."), [])
        self.assertNotEqual(chain_claim_problems(START + " Chains prompt."), [])
        self.assertNotEqual(chain_claim_problems(START.replace("checks each command of a chain on its own", "x")), [])


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


# ---- Issue #44: the issue-create and issue-comment wrappers -------------------
# No new allow rule is added: `make *` already covers the wrappers, which is why
# the validation lives in the make targets and scripts. Raw `gh` writes stay
# approval-gated in both tools, and an explicit `ask` entry keeps them so after a
# later broad allow. These are configuration checks under this file's models.

WRAPPER_COMMANDS = [
    "make issue-create FILE=.scratch/x.md",
    "make issue-comment N=1 FILE=.scratch/x.md",
]
RAW_ISSUE_WRITES = [
    "gh issue create", "gh issue create --title x --body-file -", "gh issue comment 5",
    "gh issue comment 5 --body-file -", "gh issue edit 5 --title x", "gh issue close 5",
    "gh issue close 5 --reason completed", "gh issue reopen 5", "gh issue delete 5 --yes",
    "gh api repos/o/r/issues/5/labels", "gh api -X POST repos/o/r/issues", "gh api graphql",
]
CLAUDE_GH_ASKS = [
    "Bash(gh issue create *)", "Bash(gh issue comment *)", "Bash(gh issue edit *)",
    "Bash(gh issue close *)", "Bash(gh issue reopen *)", "Bash(gh issue delete *)", "Bash(gh api *)",
]
OPENCODE_GH_ASKS = [
    "gh issue create*", "gh issue comment*", "gh issue edit*", "gh issue close*",
    "gh issue reopen*", "gh issue delete*", "gh api*",
]


def claude_decision_with(extra_allow: list, tool: str, value: str) -> str:
    """The Claude Code model with extra allow rules added (a later broad allow)."""
    for decision, rules in (("deny", CLAUDE.get("deny", [])), ("ask", CLAUDE.get("ask", [])),
                            ("allow", CLAUDE.get("allow", []) + extra_allow)):
        if any(claude_matches(rule, tool, value) for rule in rules):
            return decision
    return "ask"


def opencode_decision_with(broad_allow: str, value: str) -> str:
    """The OpenCode model with a broad allow inserted right after the general `*` rule."""
    rules = list(BASH.items())
    rules.insert(1, (broad_allow, "allow"))
    decision = "ask"
    for pattern, action in rules:
        if wildcard(pattern, value):
            decision = action
    return decision


class IssueWrapperPermissionTest(unittest.TestCase):
    def test_wrapper_commands_are_allowed_in_claude_code(self):
        for command in WRAPPER_COMMANDS:
            self.assertEqual(claude_decision("Bash", command), "allow", command)

    def test_wrapper_commands_are_allowed_in_opencode(self):
        for command in WRAPPER_COMMANDS:
            self.assertEqual(opencode_decision("bash", command), "allow", command)

    def test_the_wrappers_are_covered_by_the_existing_make_rule_not_a_new_one(self):
        self.assertIn("Bash(make *)", CLAUDE["allow"])
        self.assertEqual(BASH["make *"], "allow")
        for command in WRAPPER_COMMANDS:
            self.assertEqual([r for r in CLAUDE["allow"] if claude_matches(r, "Bash", command)], ["Bash(make *)"])
            self.assertEqual([p for p, a in BASH.items() if a == "allow" and wildcard(p, command)], ["make *"])
        for rule in CLAUDE["allow"] + list(BASH):
            self.assertNotIn("issue-create", rule)
            self.assertNotIn("issue-comment", rule)

    def test_no_allow_rule_matches_a_raw_issue_write_in_claude_code(self):
        for command in RAW_ISSUE_WRITES:
            self.assertEqual([r for r in CLAUDE["allow"] if claude_matches(r, "Bash", command)], [], command)
            self.assertEqual(claude_decision("Bash", command), "ask", command)

    def test_no_allow_rule_matches_a_raw_issue_write_in_opencode(self):
        for command in RAW_ISSUE_WRITES:
            self.assertEqual([p for p, a in BASH.items() if a == "allow" and wildcard(p, command)], [], command)
            self.assertEqual(opencode_decision("bash", command), "ask", command)

    def test_claude_code_lists_the_raw_writes_under_ask(self):
        for rule in CLAUDE_GH_ASKS:
            self.assertIn(rule, CLAUDE["ask"])
            self.assertNotIn(rule, CLAUDE["allow"])
            self.assertNotIn(rule, CLAUDE["deny"])

    def test_opencode_lists_the_raw_writes_under_ask_after_the_general_rule_and_every_allow(self):
        last_allow = max(KEYS.index(k) for k in ALLOW_KEYS)
        for pattern in OPENCODE_GH_ASKS:
            self.assertEqual(BASH[pattern], "ask", pattern)
            self.assertGreater(KEYS.index(pattern), KEYS.index("*"), pattern)
            self.assertGreater(KEYS.index(pattern), last_allow, pattern)

    def test_the_asks_survive_a_later_broad_allow(self):
        for command in RAW_ISSUE_WRITES:
            for broad in ("Bash(gh *)", "Bash(gh issue *)", "Bash(*)"):
                self.assertEqual(claude_decision_with([broad], "Bash", command), "ask", (broad, command))
            for broad in ("gh *", "gh issue*", "*"):
                self.assertEqual(opencode_decision_with(broad, command), "ask", (broad, command))

    def test_the_wrappers_themselves_are_not_caught_by_those_asks(self):
        for command in WRAPPER_COMMANDS:
            self.assertEqual(claude_decision_with([], "Bash", command), "allow")
            for rule in CLAUDE["ask"]:
                self.assertFalse(claude_matches(rule, "Bash", command), (rule, command))
            for pattern in OPENCODE_GH_ASKS:
                self.assertFalse(wildcard(pattern, command), (pattern, command))

    def test_editing_and_closing_an_issue_have_no_allow_rule_in_either_tool(self):
        words = ("issue create", "issue comment", "issue edit", "issue close", "issue reopen",
                 "issue delete", "gh api", "gh *", "gh issue *", "gh issue*")
        allows = list(CLAUDE["allow"]) + [k for k in ALLOW_KEYS]
        for rule in allows:
            for word in words:
                self.assertNotIn(word, rule, rule)
        self.assertEqual(sorted(r for r in CLAUDE["allow"] if "gh issue" in r),
                         ["Bash(gh issue list *)", "Bash(gh issue view *)"])
        self.assertEqual(sorted(k for k in ALLOW_KEYS if k.startswith("gh issue")),
                         ["gh issue list*", "gh issue view*"])


# ---- Issue #63 D: this repo's own .claude/settings.json carries the kit's gh asks ----

REPO_CLAUDE = json.loads((KIT.parent / ".claude" / "settings.json").read_text(encoding="utf-8"))["permissions"]


def kit_gh_asks() -> list:
    return [rule for rule in CLAUDE["ask"] if rule.startswith("Bash(gh ")]


def missing_gh_asks(repo_permissions: dict) -> list:
    """The kit's `gh` ask rules that the repo copy lacks (empty list: parity)."""
    return [rule for rule in kit_gh_asks() if rule not in repo_permissions.get("ask", [])]


def repo_decision(command: str, permissions: dict) -> str:
    for decision in ("deny", "ask", "allow"):
        if any(claude_matches(rule, "Bash", command) for rule in permissions.get(decision, [])):
            return decision
    return "ask"


class RepoClaudeGhAskTest(unittest.TestCase):
    def test_the_kit_has_the_seven_gh_asks(self):
        self.assertEqual(sorted(kit_gh_asks()), sorted(CLAUDE_GH_ASKS))

    def test_every_kit_gh_ask_is_in_the_repo_copy(self):
        self.assertEqual(missing_gh_asks(REPO_CLAUDE), [])

    def test_deleting_one_entry_is_named(self):
        for rule in CLAUDE_GH_ASKS:
            with self.subTest(rule=rule):
                trimmed = dict(REPO_CLAUDE, ask=[r for r in REPO_CLAUDE["ask"] if r != rule])
                self.assertEqual(missing_gh_asks(trimmed), [rule])

    def test_no_repo_allow_rule_matches_a_raw_gh_write(self):
        for command in RAW_ISSUE_WRITES:
            with self.subTest(command=command):
                self.assertEqual([r for r in REPO_CLAUDE["allow"] if claude_matches(r, "Bash", command)], [])

    def test_a_raw_gh_issue_comment_asks_under_both_files(self):
        command = "gh issue comment 5 --body-file -"
        self.assertEqual(claude_decision("Bash", command), "ask")
        self.assertEqual(repo_decision(command, REPO_CLAUDE), "ask")
        self.assertTrue(any(claude_matches(r, "Bash", command) for r in REPO_CLAUDE["ask"]),
                        "the repo copy asks only by default, not because a rule asks")


if __name__ == "__main__":
    unittest.main()
