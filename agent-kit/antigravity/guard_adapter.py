#!/usr/bin/env python3
"""Antigravity CLI PreToolUse hook adapter on run_command.

Translates Antigravity's `run_command` toolCall payload into the shared git guard's
expected input (from `claude-code/hooks/guard_git.py`) and returns a JSON decision
on stdout.

FACTS THAT SHAPE THIS ADAPTER:
- A hook that prints {"decision": "deny", "reason": ...} blocks the tool call.
- A hook that exits 1 blocks.
- A hook killed at the 30 s timeout blocks.
- A hook that exits 0 with NO output ALLOWS the command (fails open).
- Malformed JSON from a hook blocks (protojson unmarshal error).

Therefore, this adapter must emit an explicit decision JSON on EVERY path,
including its own errors, and must NEVER exit 0 silently.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def emit_decision(decision: str, reason: str | None = None) -> None:
    """Print the decision JSON and exit 0. Never exit silently."""
    out: dict[str, str] = {"decision": decision}
    if reason:
        out["reason"] = reason
    sys.stdout.write(json.dumps(out) + "\n")
    sys.stdout.flush()
    sys.exit(0)


def find_guard_git(cwd_hints: list[str] | None = None) -> Path | None:
    """Find claude-code/hooks/guard_git.py relative to this file or the workspace."""
    here = Path(__file__).resolve().parent
    candidates: list[Path] = [
        here.parent / "claude-code" / "hooks" / "guard_git.py",
        here / "claude-code" / "hooks" / "guard_git.py",
    ]
    for root_str in cwd_hints or []:
        if root_str:
            root = Path(root_str)
            candidates.extend([
                root / "_docs" / "agent-kit" / "claude-code" / "hooks" / "guard_git.py",
                root / "agent-kit" / "claude-code" / "hooks" / "guard_git.py",
                root.parent / "_docs" / "agent-kit" / "claude-code" / "hooks" / "guard_git.py",
                root.parent / "agent-kit" / "claude-code" / "hooks" / "guard_git.py",
            ])
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def workspace_hints(payload: dict, args: dict) -> list[str]:
    """Absolute paths the payload offers, best first.

    The docs list `workspacePaths`; the 2026-11-21 spike payload carried `cwd`;
    `run_command` also takes its own `Cwd` argument. Use whichever are present.
    """
    hints: list[str] = []
    workspace_paths = payload.get("workspacePaths")
    if isinstance(workspace_paths, list):
        hints.extend(p for p in workspace_paths if isinstance(p, str) and p)
    for value in (args.get("Cwd"), payload.get("cwd")):
        if isinstance(value, str) and value:
            hints.append(value)
    return hints


def handle_payload(raw_input: str) -> None:
    if not raw_input or not raw_input.strip():
        emit_decision("deny", "Blocked by the agent kit: hook received empty input.")

    try:
        payload = json.loads(raw_input)
    except Exception as exc:
        emit_decision("deny", f"Blocked by the agent kit: malformed hook payload ({exc}).")

    if not isinstance(payload, dict):
        emit_decision("deny", "Blocked by the agent kit: hook payload is not a JSON object.")

    # Only PreToolUse is handled by this adapter.
    event = payload.get("hookEventName")
    if event and event != "PreToolUse":
        emit_decision("allow")

    tool_call = payload.get("toolCall")
    if tool_call is None or not isinstance(tool_call, dict):
        emit_decision("deny", "Blocked by the agent kit: payload has no toolCall object.")

    tool_name = tool_call.get("name")
    if tool_name != "run_command":
        # Any tool other than run_command is allowed by this hook.
        emit_decision("allow")

    args = tool_call.get("args")
    if args is None or not isinstance(args, dict):
        emit_decision("deny", "Blocked by the agent kit: toolCall has no args object.")

    command = args.get("CommandLine")
    if command is None:
        command = ""
    if not isinstance(command, str):
        emit_decision("deny", "Blocked by the agent kit: CommandLine argument is not text.")

    hints = workspace_hints(payload, args)
    guard_path = find_guard_git(hints + [os.getcwd()])
    if guard_path is None:
        emit_decision("deny", "Blocked by the agent kit: guard_git.py not found in the kit.")

    guard_payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})

    run_cwd = next((hint for hint in hints if os.path.isdir(hint)), None)
    try:
        proc = subprocess.run(
            [sys.executable, str(guard_path)],
            input=guard_payload,
            text=True,
            capture_output=True,
            timeout=25,
            cwd=run_cwd,
        )
    except subprocess.TimeoutExpired:
        emit_decision("deny", "Blocked by the agent kit: git guard timed out.")
    except Exception as exc:
        emit_decision("deny", f"Blocked by the agent kit: failed to run git guard ({exc}).")

    if proc.returncode == 0:
        emit_decision("allow")
    else:
        reason = (proc.stderr or proc.stdout or "").strip()
        if not reason:
            reason = f"Blocked by the agent kit (exit code {proc.returncode})."
        emit_decision("deny", reason)


def main() -> None:
    try:
        raw_input = sys.stdin.read()
        handle_payload(raw_input)
    except SystemExit:
        raise
    except BaseException as exc:
        # Ultimate fallback: ensure a decision is emitted on every unhandled error.
        try:
            emit_decision("deny", f"Blocked by the agent kit: adapter error ({exc}).")
        except Exception:
            sys.exit(1)


if __name__ == "__main__":
    main()
