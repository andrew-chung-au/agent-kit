#!/usr/bin/env python3
"""Print the sha256 of a GitHub issue body, its author and an owner check.

Run through the make target, from the repo root:
    make issue-hash N=<issue number>
or directly:
    python3 -B agent-kit/scripts/issue-hash.py <issue number>

It reads the issue (`gh api repos/<repo>/issues/<N>`), the owner (`gh api repos/<repo>`)
and every page of the comments (`gh api "repos/<repo>/issues/<N>/comments?per_page=100&page=<P>"`),
where <repo> is the GITHUB_REPO line of agent-kit.conf (github_api.py), and prints
exactly five lines, in this order:

    Body sha256: <64 lowercase hex characters>
    Author: <login>
    Repository owner: <login>
    Owner-authored: yes|no|unknown
    Recorded sha256: <64 lowercase hex characters|none|unknown>

The digest is of the issue BODY only, exactly as received: UTF-8, no newline
added or removed. The title and the comments are not part of the hashed text,
so a title change or a new comment does not change the digest.

The recorded hash is the one on a `Body sha256: <64 lowercase hex characters>`
line (the whole line, nothing else on it) in the LATEST comment that starts
with `PM:` and whose author login is the repository owner. A line in any other
comment, or with fewer or more than 64 hex characters, does not count. `none`
means no valid line exists; `unknown` means a read failed.

Exit codes:
    0  the body, author, owner and comments were all read (Owner-authored is
       yes or no)
    1  a read failed (gh missing or failing, malformed JSON, a missing or empty
       body, author or owner, or an unreadable comments list): each field that
       could not be read prints `unknown`, the hash, Owner-authored and
       Recorded lines also say `unknown` (so a partial read never looks
       valid), and a short reason goes to stderr
    2  N is not a positive integer without leading zeros (^[1-9][0-9]*$);
       no gh command is run

It only reads: it never posts, edits or creates anything. Standard library only.
"""
from __future__ import annotations

import hashlib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import github_api  # noqa: E402  (the repository and the gh api reads, shared with sweep-due.py)

NUMBER = re.compile(r"[1-9][0-9]*")
HASH_LINE = re.compile(r"Body sha256: ([0-9a-f]{64})")
UNKNOWN = "unknown"


def body_digest(body: str) -> str:
    """sha256 of the body text exactly as received (UTF-8, nothing added or removed)."""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def text_field(value):
    """Return value if it is a non-empty string, else None."""
    return value if isinstance(value, str) and value != "" else None


def recorded_hash(comments, owner):
    """The hash on the last valid `Body sha256:` line, or None.

    Valid: the comment starts with `PM:`, its author login is the owner, and a
    whole line is `Body sha256: ` plus exactly 64 lowercase hex characters.
    Raises ValueError if the comments list is malformed.
    """
    if not isinstance(comments, list):
        raise ValueError("comments are missing or malformed")
    found = None
    for item in comments:
        if not isinstance(item, dict):
            raise ValueError("a comment is malformed")
        person = item.get("author")
        login = text_field(person.get("login")) if isinstance(person, dict) else None
        text = item.get("body")
        if not isinstance(text, str):
            raise ValueError("a comment has no body text")
        if login != owner or not text.startswith("PM:"):
            continue
        for line in text.splitlines():
            match = HASH_LINE.fullmatch(line)
            if match:
                found = match.group(1)
    return found


def read_recorded(repo, number: str, owner, reasons):
    """Return the recorded hash, 'none' or 'unknown'; a failed read adds a reason."""
    try:
        if repo is None:
            return UNKNOWN
        comments = github_api.comments(repo, number)
        if owner is None:
            return UNKNOWN
        return recorded_hash(comments, owner) or "none"
    except ValueError as error:
        reasons.append(str(error))
        return UNKNOWN


def read_issue(repo, number: str):
    """Return (body, author, owner, reasons); a field that could not be read is None."""
    reasons = []
    body = author = owner = None
    if repo is None:
        return body, author, owner, reasons
    try:
        issue = github_api.head(repo, number)
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
        person = github_api.owner(repo).get("owner")
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
    try:
        repo = github_api.conf_repo()
        reasons = []
    except ValueError as error:
        repo = None
        reasons = [str(error)]
    body, author, owner, more = read_issue(repo, args[0])
    reasons += more
    recorded = read_recorded(repo, args[0], owner, reasons)
    if reasons or author is None or owner is None:
        owned = UNKNOWN
        recorded = UNKNOWN
    else:
        owned = "yes" if author == owner else "no"
    # Any failed read prints no hash, so a partial read never looks like a valid result.
    print(f"Body sha256: {body_digest(body) if body is not None and not reasons else UNKNOWN}")
    print(f"Author: {author or UNKNOWN}")
    print(f"Repository owner: {owner or UNKNOWN}")
    print(f"Owner-authored: {owned}")
    print(f"Recorded sha256: {recorded}")
    if reasons:
        print("issue-hash: " + "; ".join(reasons), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
