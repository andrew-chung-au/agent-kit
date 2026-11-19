#!/usr/bin/env python3
"""Claude Code PermissionRequest hook: record what Claude Code asked the human to approve.

Observe-only. It never prints anything and always exits 0, so Claude Code shows its normal
prompt and the decision is the human's. It is registered for PermissionRequest only, never
as a decision hook, and it writes nothing except the log file.

Appends one JSON line to <project>/.agent-kit/logs/permissions/YYYY-MM-DD.jsonl (UTC date).
Record format, limits and what is never logged: procedures/permission-log.md. Secrets are
removed from `pattern` with scripts/secret-patterns.txt (see scripts/permission_log_lib.py).

What the event carries, and what it does not (hooks reference, PermissionRequest):
- carried: session_id, tool_name, tool_input (so a type, a pattern and a session);
- not carried: the outcome (allowed or denied) and a tool_use_id to pair it with PostToolUse.
So the log holds `ask` records only, with no `id`; the report says so.

It refuses a symlink: nothing is written when `.agent-kit`, `logs`, `permissions` or the day's
file is a symlink (the project root itself may be reached through one). A refusal is silent.

The log is capped at 1 MiB a day. The first record that does not fit ends that day's log:
one `truncated` record is written and nothing is appended after it, in any later run.
"""
from __future__ import annotations

import errno
import json
import os
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent.parent / "scripts"
TOOL = "claude-code"
CAP = 1048576  # bytes per daily file
MARKER = '"event":"truncated"'
# Which tool_input field is the pattern. Only these are read; contents and diffs never are.
PATTERN_FIELD = {
    "Bash": "command", "PowerShell": "command",
    "Read": "file_path", "Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path",
    "NotebookEdit": "notebook_path", "WebFetch": "url",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def record_for(payload, lib) -> dict:
    """Only whitelisted fields are ever copied. Anything unrecognised becomes an unknown record."""
    base = {"tool": TOOL, "time": now()}
    name = payload.get("hook_event_name") if isinstance(payload, dict) else None
    if name == "PermissionRequest":
        session, kind = payload.get("session_id"), payload.get("tool_name")
        if isinstance(session, str) and session and isinstance(kind, str) and kind:
            field = PATTERN_FIELD.get(kind)
            tool_input = payload.get("tool_input")
            value = tool_input.get(field) if field and isinstance(tool_input, dict) else None
            first = value[:4000].split("\n", 1)[0] if isinstance(value, str) else ""
            return {"event": "ask", **base, "sessionID": lib.plain(session), "type": lib.plain(kind.lower()),
                    "pattern": lib.redact(first), "source": name}
    # The event name only, never the payload.
    source = lib.plain(name, 100) if isinstance(name, str) and name else "unparsed"
    return {"event": "unknown", **base, "source": source}


def has_marker(path: Path) -> bool:
    with open(path, "rb") as handle:
        size = handle.seek(0, os.SEEK_END)
        handle.seek(max(0, size - 1000))
        return MARKER in handle.read().decode("utf-8", "replace")


def is_symlink(path: Path) -> bool:
    """True if the path itself is a symlink (dangling or not). Never follows it."""
    try:
        return stat.S_ISLNK(os.lstat(path).st_mode)
    except FileNotFoundError:
        return False


def write(path: Path, line: bytes) -> None:
    # O_NOFOLLOW: a symlink swapped in after the lstat check is refused by the kernel (ELOOP).
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        os.write(fd, line)
    finally:
        os.close(fd)


def append(root: Path, record: dict) -> None:
    agent_kit = root / ".agent-kit"
    folder = agent_kit / "logs" / "permissions"
    # lstat each level, parent first, before any mkdir: nothing is created through a symlink.
    if any(is_symlink(level) for level in (agent_kit, agent_kit / "logs", folder)):
        return
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (record["time"][:10] + ".jsonl")
    if is_symlink(path):
        return
    line = (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")
    size = path.stat().st_size if path.exists() else 0
    # The marker check comes before any append of a normal record. Each run is a new process,
    # so the file is always the source of truth: nothing follows a marker, even after a restart.
    if size > 0 and has_marker(path):
        return
    if size + len(line) <= CAP:
        write(path, line)
        return
    marker = {"event": "truncated", "tool": TOOL, "time": record["time"]}
    write(path, (json.dumps(marker, separators=(",", ":")) + "\n").encode("utf-8"))


def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except (ValueError, RecursionError):
            payload = None
        sys.path.insert(0, str(SCRIPTS))
        import permission_log_lib as lib  # noqa: E402  (after the path is set; failure is caught below)
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
        append(root, record_for(payload, lib))
    except OSError as error:
        if error.errno != errno.ELOOP:  # ELOOP: O_NOFOLLOW refused a symlink; a refusal is silent
            sys.stderr.write("log_permission: not logged (%s)\n" % type(error).__name__)
    except Exception as error:  # observe-only: never let a logging problem change the prompt
        sys.stderr.write("log_permission: not logged (%s)\n" % type(error).__name__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
