#!/usr/bin/env python3
"""Print the sha256 of a GitHub issue body, its author and an owner check.

Run through the make target, from the repo root:
    make issue-hash N=<issue number>
or directly:
    python3 -B agent-kit/scripts/issue-hash.py <issue number>

It reads the issue with `gh issue view <N> --json body,author` and the owner
with `gh repo view --json owner`, and prints exactly four lines, in this order:

    Body sha256: <64 lowercase hex characters>
    Author: <login>
    Repository owner: <login>
    Owner-authored: yes|no|unknown

The digest is of the issue BODY only, exactly as received: UTF-8, no newline
added or removed. The title and the comments are not part of the hashed text,
so a title change or a new comment does not change the digest.

Exit codes:
    0  the body, author and owner were all read (Owner-authored is yes or no)
    1  a read failed (gh missing or failing, malformed JSON, a missing or empty
       body, author or owner): each field that could not be read prints
       `unknown`, the hash and Owner-authored lines also say `unknown` (so a
       partial read never looks valid), and a short reason goes to stderr
    2  N is not a positive integer without leading zeros (^[1-9][0-9]*$);
       no gh command is run

It only reads: it never posts, edits or creates anything. Standard library only.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys

NUMBER = re.compile(r"[1-9][0-9]*")
UNKNOWN = "unknown"


def body_digest(body: str) -> str:
    """sha256 of the body text exactly as received (UTF-8, nothing added or removed)."""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def run_gh(args):
    """Run gh and return its parsed JSON, or raise ValueError with a short reason."""
    try:
        done = subprocess.run(["gh", *args], capture_output=True, text=True,
                              encoding="utf-8", timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError(f"cannot run gh: {error}")
    if done.returncode != 0:
        raise ValueError(f"gh {' '.join(args[:2])} failed (exit {done.returncode})")
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise ValueError(f"gh {' '.join(args[:2])} returned malformed JSON")
    if not isinstance(data, dict):
        raise ValueError(f"gh {' '.join(args[:2])} returned unexpected JSON")
    return data


def text_field(value):
    """Return value if it is a non-empty string, else None."""
    return value if isinstance(value, str) and value != "" else None


def read_issue(number: str):
    """Return (body, author, owner, reasons); a field that could not be read is None."""
    reasons = []
    body = author = owner = None
    try:
        issue = run_gh(["issue", "view", number, "--json", "body,author"])
        body = text_field(issue.get("body"))
        if body is None:
            reasons.append("issue body is missing or empty")
        person = issue.get("author")
        author = text_field(person.get("login")) if isinstance(person, dict) else None
        if author is None:
            reasons.append("issue author is missing")
    except ValueError as error:
        reasons.append(str(error))
    try:
        repo = run_gh(["repo", "view", "--json", "owner"])
        person = repo.get("owner")
        owner = text_field(person.get("login")) if isinstance(person, dict) else None
        if owner is None:
            reasons.append("repository owner is missing")
    except ValueError as error:
        reasons.append(str(error))
    return body, author, owner, reasons


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1 or not NUMBER.fullmatch(args[0]):
        print("Usage: issue-hash.py <issue number> (a positive integer without leading zeros)",
              file=sys.stderr)
        return 2
    body, author, owner, reasons = read_issue(args[0])
    if reasons or author is None or owner is None:
        owned = UNKNOWN
    else:
        owned = "yes" if author == owner else "no"
    # Any failed read prints no hash, so a partial read never looks like a valid result.
    print(f"Body sha256: {body_digest(body) if body is not None and not reasons else UNKNOWN}")
    print(f"Author: {author or UNKNOWN}")
    print(f"Repository owner: {owner or UNKNOWN}")
    print(f"Owner-authored: {owned}")
    if reasons:
        print("issue-hash: " + "; ".join(reasons), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
