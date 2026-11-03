#!/usr/bin/env python3
"""Claude Code Stop hook for the Engineer subagent: don't finish while `make verify` fails.

Defined in the Engineer's role definition, so it runs only for that subagent
(Claude Code turns a subagent's Stop hook into SubagentStop). PM and QA aren't
blocked: reporting a failure is their job.

- Runs from the project folder ($CLAUDE_PROJECT_DIR) and looks only at that folder.
- Skips when nothing changed since the upstream branch, or only Markdown changed.
- Skips when the folder is identical to the last state that passed.
- Exit 2 blocks the stop and shows the Engineer the failure, so it fixes it.
- After MAX_BLOCKS failed attempts it lets the Engineer stop and warns the human,
  so an unfixable failure can't loop forever.

State and the full log of the last run: .scratch/verify-on-stop/ (git-ignored;
`make clean-scratch` removes it).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MAX_BLOCKS = 3
STATE = Path(".scratch") / "verify-on-stop"


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, errors="replace"
    ).stdout


def base() -> str:
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}").strip()
    return upstream or "HEAD"


def fingerprint(untracked: list[str]) -> str:
    h = hashlib.sha256()
    h.update(git("rev-parse", "HEAD").encode())
    h.update(git("diff", "HEAD", "--binary", "--", ".").encode())
    for path in sorted(untracked):
        h.update(path.encode())
        try:
            h.update(Path(path).read_bytes())
        except OSError:
            pass
    return h.hexdigest()


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    os.chdir(os.environ.get("CLAUDE_PROJECT_DIR", "."))

    untracked = [p for p in git("ls-files", "--others", "--exclude-standard", "--", ".").splitlines() if p]
    changed = [p for p in git("diff", "--name-only", "--relative", base(), "--", ".").splitlines() if p] + untracked
    if not changed or all(p.endswith(".md") for p in changed):
        sys.exit(0)

    STATE.mkdir(parents=True, exist_ok=True)
    run_id = payload.get("agent_id") or payload.get("session_id") or "unknown"
    blocks_file = STATE / f"blocks-{run_id}"
    last_pass = STATE / "last-pass"
    fp = fingerprint(untracked)
    if last_pass.exists() and last_pass.read_text() == fp:
        blocks_file.unlink(missing_ok=True)
        sys.exit(0)

    result = subprocess.run(
        ["make", "verify"], capture_output=True, text=True, errors="replace", stdin=subprocess.DEVNULL
    )
    log = result.stdout + result.stderr
    (STATE / "last-run.log").write_text(log)

    if result.returncode == 0:
        last_pass.write_text(fp)
        blocks_file.unlink(missing_ok=True)
        sys.exit(0)

    blocks = int(blocks_file.read_text()) if blocks_file.exists() else 0
    if blocks >= MAX_BLOCKS:
        print(json.dumps({
            "systemMessage": f"make verify is still failing after {MAX_BLOCKS} fix attempts. "
                             "The Engineer was allowed to stop; see .scratch/verify-on-stop/last-run.log."
        }))
        sys.exit(0)

    blocks_file.write_text(str(blocks + 1))
    tail = "\n".join(log.splitlines()[-60:])
    print(
        "make verify failed, so this work isn't done. Fix the failures below, then finish. "
        "Never weaken or skip a test to make it pass. If you can't fix it, say so in your issue comment. "
        "Full log: .scratch/verify-on-stop/last-run.log\n\n" + tail,
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
