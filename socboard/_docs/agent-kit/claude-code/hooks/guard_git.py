#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Bash): block shell commands the kit's rules forbid (see "Enforced by hooks" in AGENTS.md).

Blocks, with the reason and the allowed alternative:
- any command with an argument naming a `.env` file (`.env`, or `.env.*` other than
  exactly `.env.example`), whatever the command: `cat .env`, `ls .env`, `cp .env.example .env`.
  Use `.env.example`, or ask the human.
- broad staging: `git add .`, `-A`, `--all`, `-u`, `--update`, `:/`, `*`
- `git commit -a` / `--all` (also in clusters such as `-am`)
- skipping hooks: `--no-verify`, and `git commit -n` (also in clusters such as `-nm`)
- `git push` (only the human pushes)
- changing `core.hooksPath` (would switch off the kit's git hooks)

`HUMAN_APPROVED=1 git commit ...` is allowed: Claude Code asks the human before
any command with an environment prefix, and that prompt is the approval check.

Exit 2 blocks the tool call and shows the message to Claude. Anything this
script can't parse is let through: Claude Code's own permission checks and the
git hooks still apply. This is a guard against habits, not a security boundary.

Known gaps in the `.env` block (documented, not fixed): indirection the parser can't
see (globs such as `cat .e*`, variables such as `f=.env; cat $f`, `bash -c "cat .env"`
and `sh -c` where the name sits inside one quoted token, `python3 -c "open('.env')"`,
`xargs`, `find -exec`, reading the file through any other tool), and a command that
never names the file but reads it (`cat *` in a folder that has `.env`). OpenCode's
template denies `.env` shell commands by a text pattern instead (not a boundary).
"""
from __future__ import annotations

import json
import re
import shlex
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


def names_env_file(tokens) -> bool:
    """True if any token names a forbidden `.env` file.

    Source: `agent-kit.conf` (FORBIDDEN `.env`, `.env.*`; ALLOWED `.env.example`).
    A token matches when its last path component, after stripping a leading `<`/`>`
    redirect (`<`, `>`, `>>`, `2>`) and quotes or backticks, and also for the value of `--opt=value`, is
    exactly `.env` or starts with `.env.` and is not exactly `.env.example`.
    Whole-name, case-sensitive.
    """
    for token in tokens:
        token = re.sub(r"^[0-9]*[<>]+", "", token).strip("`'\"")
        candidates = [token]
        if "=" in token:
            candidates.append(token.split("=", 1)[1].strip("`'\""))
        for candidate in candidates:
            name = candidate.rsplit("/", 1)[-1]
            if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
                return True
    return False


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


def check(sub: str, args) -> str | None:
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
        return "Don't push. The human reviews the diff and pushes; the pre-push hook runs make verify."
    if sub == "config" and any(a.lower() == "core.hookspath" for a in args) and "--get" not in args:
        return "Don't change core.hooksPath: it switches off the kit's git hooks. Ask the human."
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        sys.exit(0)
    command = (payload.get("tool_input") or {}).get("command") or ""
    for tokens in segments(command) or []:
        if names_env_file(tokens):
            print("Blocked by the agent kit: don't open, print or copy `.env` files from the shell. "
                  "Use `.env.example`, or ask the human.", file=sys.stderr)
            sys.exit(2)
        parts = git_parts(tokens)
        if not parts:
            continue
        reason = check(*parts)
        if reason:
            print(f"Blocked by the agent kit: {reason}", file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
