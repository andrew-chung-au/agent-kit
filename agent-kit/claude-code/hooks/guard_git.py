#!/usr/bin/env python3
"""Claude Code PreToolUse hook (Bash): block shell commands the kit's rules forbid (see "Enforced by hooks" in AGENTS.md).

Blocks, with the reason and the allowed alternative:
- any command with an argument naming a `.env` file (`.env`, or `.env.*` other than
  exactly `.env.example`), whatever the command: `cat .env`, `ls .env`, `cp .env.example .env`.
  Use `.env.example`, or ask the human.
- broad staging: `git add .`, `-A`, `--all`, `-u`, `--update`, `:/`, `*`, and
  unambiguous prefixes such as `--al`; short clusters such as `-Av` and `-uA`
- `git commit -a` / `--all` (also in clusters such as `-am`, and prefixes such as `--al`)
- skipping hooks: `--no-verify` and unambiguous prefixes such as `--no-ver`, and
  `git commit -n` (also in clusters such as `-nm`)
- `git push` (only the human pushes), with one opt-in exception for Claude Code cloud
  sessions (below)
- changing `core.hooksPath`, including `git -c core.hooksPath=...`,
  `git -c core.hooksPath ...` and `git --config-env=core.hooksPath=...`, in any case

Fails closed: invalid JSON, an unexpected payload, or an internal error exits 2 with a
message. `claude-code/settings.json` registers the hook as
`python3 .../guard_git.py || exit 2`, so a crash blocks instead of letting the command run.
When the command cannot be parsed, a raw scan still blocks the high-risk patterns (`git
push`, `--no-ver`, `core.hooksPath`, broad `git add`, `.env`).

Cloud-session push (opt-in): a push is let through only when all of these hold:
`AGENT_KIT_CLOUD_PUSH=1` (the project opts in, for example in `.claude/settings.json` `env`),
`CLAUDE_CODE_REMOTE=true` (set by Claude Code in its cloud sessions, so a local session
stays blocked), the command is exactly `git push origin <branch>` or
`git push -u|--set-upstream origin <branch>` with nothing before `git` and no other option,
and `<branch>` is the current branch and starts with `claude/`. Force, delete, other refs,
`main` and every other form stay blocked.

`HUMAN_APPROVED=1 git commit ...` is allowed: Claude Code asks the human before
any command with an environment prefix, and that prompt is the approval check.

Exit 2 blocks the tool call and shows the message to Claude. Invalid input or an
internal error also exits 2, so a crash blocks rather than lets the command run.
Claude Code's own permission checks and the git hooks still apply. This is a guard
against habits, not a security boundary.

Known gaps (documented, not fixed): wrappers and indirection the parser can't see
(`bash -c "git push"`, `xargs git push`, `eval`, scripts, `GIT_CONFIG_*` variables,
globs such as `cat .e*`, variables such as `f=.env; cat $f`, and a command that never
names `.env` but reads it, such as `cat *` in a folder that has one). This is a habit
guard, not a security boundary: the read-only token, the git hooks and the human's
review are the boundary. A wrapper can skip the pre-commit hook, so the `--no-verify`
catch matters; a breach is a visible rule violation, not an accident. OpenCode's
template denies `.env` shell commands by a text pattern instead (also not a boundary).
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
# Long options this guard checks. Git accepts any unambiguous prefix of a long option,
# so `--no-ver` and `--al` must be read as `--no-verify` and `--all`.
FORBIDDEN_LONG = ("--no-verify", "--all", "--update")
# Options whose next token is a value, not a flag. A commit message may name `--no-verify`
# without running it.
MESSAGE_OPTS = ("-m", "--message", "-F", "--file")
# When the command cannot be parsed, these patterns are still checked in the raw text.
RAW_RISK = (
    (re.compile(r"(?:^|[;&|()\s])git\s+push(?:[\s;&|()]|$)", re.IGNORECASE),
     "Don't push. The human reviews the diff and pushes; the pre-push hook runs make verify."),
    (re.compile(r"--no-ver", re.IGNORECASE),
     "Never skip git hooks (--no-verify). If a hook blocks you, fix the cause or ask the human."),
    (re.compile(r"core\.hookspath", re.IGNORECASE),
     "Don't change core.hooksPath: it switches off the kit's git hooks. Ask the human."),
    (re.compile(r"(?:^|[;&|()\s])git\s+add\s+(?:\.|-A(?=[\s;&|()]|$)|-u(?=[\s;&|()]|$)|"
                r"--all(?=[\s;&|()]|$)|--al(?=[\s;&|()]|$))", re.IGNORECASE),
     "Stage explicit paths only (git add path/to/file), never everything at once."),
    (re.compile(r"\.env(?!\.example)(?:$|[\s;&|)'\"])", re.IGNORECASE),
     "don't open, print or copy `.env` files from the shell. Use `.env.example`, or ask the human."),
)


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


CLOUD_PUSH_PREFIXES = (["origin"], ["-u", "origin"], ["--set-upstream", "origin"])
CLOUD_BRANCH = re.compile(r"claude/[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*")


def current_branch() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def cloud_push_allowed(tokens) -> bool:
    """True only for the exact opt-in cloud-session push (see the module docstring)."""
    if os.environ.get("AGENT_KIT_CLOUD_PUSH") != "1" or os.environ.get("CLAUDE_CODE_REMOTE") != "true":
        return False
    if len(tokens) < 4 or tokens[0] != "git" or tokens[1] != "push":
        return False
    args = tokens[2:]
    branch = args[-1]
    if args[:-1] not in CLOUD_PUSH_PREFIXES:
        return False
    if not CLOUD_BRANCH.fullmatch(branch) or ".." in branch:
        return False
    return branch == current_branch()


def canonical_long(arg: str) -> str:
    """The forbidden long option this is an unambiguous prefix of, or the arg itself."""
    if not arg.startswith("--") or "=" in arg:
        return arg
    matches = [full for full in FORBIDDEN_LONG if full.startswith(arg)]
    return matches[0] if len(matches) == 1 else arg


def value_indices(args) -> set:
    """Indices of tokens that are values of a message or file option, not flags.

    `git commit -m "--no-verify"` mentions the flag in its message; it must not be read
    as the flag. Handles separate and attached forms.
    """
    values = set()
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in MESSAGE_OPTS:
            if i + 1 < len(args):
                values.add(i + 1)
            i += 2
            continue
        if arg.startswith(("--message=", "--file=")):
            i += 1
            continue
        if (arg.startswith("-m") and arg != "-m") or (arg.startswith("-F") and arg != "-F"):
            i += 1
            continue
        i += 1
    return values


def hooks_path_override(tokens) -> bool:
    """True if a git global option sets core.hooksPath, in any case or form.

    Catches `git -c core.hooksPath=...`, `git -c core.hooksPath ...`,
    `git -c CORE.HOOKSPATH=...` and `git --config-env=core.hooksPath=...`, including
    after another global option such as `-C <dir>`.
    """
    i = 1
    while i < len(tokens):
        arg = tokens[i]
        if arg in ("-c", "--config-env"):
            value = tokens[i + 1] if i + 1 < len(tokens) else ""
            if value.lower().startswith("core.hookspath"):
                return True
            i += 2
            continue
        if arg.startswith("--config-env="):
            if arg.split("=", 1)[1].lower().startswith("core.hookspath"):
                return True
            i += 1
            continue
        if arg.startswith("-c") and arg != "-c":
            if arg[2:].lower().startswith("core.hookspath"):
                return True
            i += 1
            continue
        if arg in GIT_GLOBAL_OPTS_WITH_VALUE:
            i += 2
            continue
        if not arg.startswith("-"):
            break
        i += 1
    return False


def check(sub: str, args) -> str | None:
    values = value_indices(args)
    flags = [canonical_long(a) for i, a in enumerate(args) if i not in values]
    if "--no-verify" in flags:
        return "Never skip git hooks (--no-verify). If a hook blocks you, fix the cause or ask the human."
    if sub == "add":
        if any(a in BROAD_ADD for a in flags) or short_cluster_has(flags, "A") or short_cluster_has(flags, "u"):
            return "Stage explicit paths only (git add path/to/file), never everything at once."
    if sub == "commit":
        if "--all" in flags or short_cluster_has(flags, "a"):
            return "Don't use git commit -a. Stage explicit paths with git add, then commit."
        if short_cluster_has(flags, "n"):
            return "Never skip git hooks (git commit -n). If a hook blocks you, fix the cause or ask the human."
    if sub == "push":
        return "Don't push. The human reviews the diff and pushes; the pre-push hook runs make verify."
    if (sub == "config" and any(a.lower() == "core.hookspath" for a in flags)
            and not any(a.startswith("--get") for a in flags)):
        return "Don't change core.hooksPath: it switches off the kit's git hooks. Ask the human."
    return None


def run_checks(command: str) -> None:
    parsed = segments(command)
    if parsed is None:
        for pattern, reason in RAW_RISK:
            if pattern.search(command):
                print(f"Blocked by the agent kit: {reason} The command could not be parsed, so it "
                      "was checked for high-risk patterns; simplify it and try again.", file=sys.stderr)
                sys.exit(2)
        sys.exit(0)
    for tokens in parsed:
        if names_env_file(tokens):
            print("Blocked by the agent kit: don't open, print or copy `.env` files from the shell. "
                  "Use `.env.example`, or ask the human.", file=sys.stderr)
            sys.exit(2)
        if hooks_path_override(tokens):
            print("Blocked by the agent kit: Don't change core.hooksPath: it switches off the kit's "
                  "git hooks. Ask the human.", file=sys.stderr)
            sys.exit(2)
        parts = git_parts(tokens)
        if not parts:
            continue
        if parts[0] == "push" and cloud_push_allowed(tokens):
            continue
        reason = check(*parts)
        if reason:
            print(f"Blocked by the agent kit: {reason}", file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("the hook payload is not an object")
        tool = payload.get("tool_name")
        if tool is not None and not isinstance(tool, str):
            raise ValueError("tool_name is not text")
        if tool and tool != "Bash":
            sys.exit(0)
        tool_input = payload.get("tool_input")
        if tool_input is not None and not isinstance(tool_input, dict):
            raise ValueError("tool_input is not an object")
        command = (tool_input or {}).get("command")
        if command is None:
            command = ""
        if not isinstance(command, str):
            raise ValueError("the command is not text")
        run_checks(command)
    except SystemExit:
        raise
    except Exception as exc:
        print("Blocked by the agent kit: the git guard could not check this command "
              f"({type(exc).__name__}). Ask the human to check the hook.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
