#!/usr/bin/env python3
"""Project-owned Claude Code PreToolUse hook (Bash) that wraps the kit's guard_git.py.

It runs the kit's guard unchanged, with one exception the human approved
(`_docs/decisions/2026-11-14T0420Z-agent-push-claude-branches.md`): a command that is
exactly one plain push of a `claude/` branch to `origin` is let through, so an agent in a
cloud session can publish its work branch for the human's review. Everything else the kit
blocks stays blocked, including any push of another branch, a force push, a delete, a
refspec with `:` or `+`, `--all`, `--mirror`, `--tags` and `--no-verify`.

Allowed shape, and nothing else: `git push [-u|--set-upstream] origin claude/<name>`,
where `<name>` is letters, digits, `.`, `_`, `-` and `/`, with no `..`. The command must
be that push alone (no `;`, `&&`, `|` or other commands around it).

The kit file stays pristine (`make kit-check`); this wrapper lives outside `_docs/agent-kit/`.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

KIT_GUARD = Path(__file__).resolve().parents[2] / "_docs" / "agent-kit" / "claude-code" / "hooks" / "guard_git.py"
BRANCH = re.compile(r"^claude/[A-Za-z0-9._/-]+$")


def load_kit_guard():
    spec = importlib.util.spec_from_file_location("kit_guard_git", KIT_GUARD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def is_allowed_push(kit, command: str) -> bool:
    """True only for one plain push of a claude/ branch to origin, alone in the command."""
    parsed = kit.segments(command)
    if not parsed or len(parsed) != 1:
        return False
    tokens = parsed[0]
    if not tokens or tokens[0] != "git":
        return False
    args = tokens[1:]
    if not args or args[0] != "push":
        return False
    args = args[1:]
    if args and args[0] in {"-u", "--set-upstream"}:
        args = args[1:]
    if len(args) != 2 or args[0] != "origin":
        return False
    branch = args[1]
    return bool(BRANCH.match(branch)) and ".." not in branch and not branch.endswith("/")


def main() -> None:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except ValueError:
        sys.exit(0)
    kit = load_kit_guard()
    command = (payload.get("tool_input") or {}).get("command") or ""
    if is_allowed_push(kit, command):
        sys.exit(0)
    sys.stdin = __import__("io").StringIO(raw)
    kit.main()


if __name__ == "__main__":
    main()
