#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Bash): block git commands the kit's Conventions forbid.

Blocks, with the reason and the allowed alternative:
- broad staging: `git add .`, `-A`, `--all`, `-u`, `--update`, `:/`, `*`
- `git commit -a` / `--all` (also in clusters such as `-am`)
- skipping hooks: `--no-verify`, and `git commit -n` (also in clusters such as `-nm`)
- `git push`, except `git push -u origin <current branch>` when the optional
  cloud-session module is enabled (`AGENT_KIT_CLOUD_PUSH=1`) in a Claude Code
  cloud session (`CLAUDE_CODE_REMOTE=true`) on a `claude/*` branch other than
  `main`
- changing `core.hooksPath` (would switch off the kit's git hooks)

`HUMAN_APPROVED=1 git commit ...` is allowed: Claude Code asks the human before
any command with an environment prefix, and that prompt is the approval check.

Exit 2 blocks the tool call and shows the message to Claude. Anything this
script can't parse is let through: Claude Code's own permission checks and the
git hooks still apply. This is a guard against habits, not a security boundary.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys

OPERATOR_CHARS = ";&|\n()"
GIT_GLOBAL_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}
BROAD_ADD = {".", "./", "-A", "--all", "-u", "--update", ":/", "*", "--no-ignore-removal"}


def segments(command: str):
    """Split a shell command into simple commands, respecting quotes.

    Returns a list of token lists, or None if the command can't be parsed.
    """
    lexer = shlex.shlex(command, posix=True, punctuation_chars=OPERATOR_CHARS)
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    lexer.commenters = ""
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    result, current = [], []
    for token in tokens:
        if token and all(ch in OPERATOR_CHARS for ch in token):
            if current:
                result.append(current)
            current = []
        else:
            current.append(token)
    if current:
        result.append(current)
    return result


def git_parts(tokens):
    """Return (subcommand, args) if the simple command runs git, else None."""
    # Skip environment assignments (VAR=value) and simple wrappers.
    while tokens and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[0]) or tokens[0] in {"command", "env", "sudo"}):
        tokens = tokens[1:]
    if not tokens or tokens[0].rsplit("/", 1)[-1] != "git":
        return None
    rest = tokens[1:]
    while rest and rest[0].startswith("-"):
        opt = rest.pop(0)
        if opt in GIT_GLOBAL_OPTS_WITH_VALUE and rest:
            rest.pop(0)
    if not rest:
        return None
    return rest[0], rest[1:]


def short_cluster_has(args, letter: str) -> bool:
    return any(a.startswith("-") and not a.startswith("--") and letter in a[1:] for a in args)


def current_branch(cwd):
    """Return the checked-out branch, or None for a detached HEAD or no repo."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def push_reason(args, cwd) -> str:
    """Allow only the cloud session pushing its own claude/* branch.

    The exact form `git push -u origin <current branch>` is required, so force,
    delete, refspec and extra-argument variants all fall through to a refusal.
    """
    if os.environ.get("AGENT_KIT_CLOUD_PUSH") != "1":
        return (
            "Don't push: pushing is off unless the project enables the optional "
            "cloud-session module (AGENT_KIT_CLOUD_PUSH=1). The human reviews and pushes."
        )
    if os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        return "Don't push outside a Claude Code cloud session. The human reviews and pushes locally."
    branch = current_branch(cwd)
    if branch is None:
        return "Don't push from a detached HEAD. Check out the session's claude/* branch first."
    if branch == "main" or not branch.startswith("claude/"):
        return f"Only the session's claude/* branch may be pushed, never '{branch}'."
    if args != ["-u", "origin", branch]:
        return (
            f"Only `git push -u origin {branch}` (the current branch) is allowed; "
            "never force, delete, or push another ref."
        )
    return None


def check(sub: str, args, cwd=None) -> str | None:
    if "--no-verify" in args:
        return "Never skip git hooks (--no-verify). If a hook blocks you, fix the cause or ask the human."
    if sub == "add" and any(a in BROAD_ADD for a in args):
        return "Stage explicit paths only (git add path/to/file), never everything at once."
    if sub == "commit":
        if "--all" in args or short_cluster_has(args, "a"):
            return "Don't use git commit -a. Stage explicit paths with git add, then commit."
        if short_cluster_has(args, "n"):
            return "Never skip git hooks (git commit -n). If a hook blocks you, fix the cause or ask the human."
    if sub == "push":
        return push_reason(args, cwd)
    if sub == "config" and any(a.lower() == "core.hookspath" for a in args) and "--get" not in args:
        return "Don't change core.hooksPath: it switches off the kit's git hooks. Ask the human."
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or None
    for tokens in segments(command) or []:
        parts = git_parts(tokens)
        if not parts:
            continue
        reason = check(*parts, cwd=cwd)
        if reason:
            print(f"Blocked by the agent kit: {reason}", file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
