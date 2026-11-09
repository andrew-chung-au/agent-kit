#!/usr/bin/env python3
"""The kit's GitHub reads: name the repository and use `gh api` (REST).

Shared by issue-hash.py and sweep-due.py (imported) and by the shell wrappers and the
issue-dump target (run as a command). Standard library only; it only reads.

Why: `gh issue ...` and `gh repo view` find the repository from the folder's git
remote. Where the remote is not github.com (Kiro Web points it at a gateway) they
fail, while `gh api repos/<owner>/<name>/...` works everywhere.

The repository comes from ONE place: the line `GITHUB_REPO="<owner>/<name>"` in
./agent-kit.conf (protected, so an agent cannot retarget the wrappers). The file is
read as text and never sourced or run. The value must match
`^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` with no `..` and no `.` part, and exactly one such
line must exist. With no valid value nothing runs `gh`.

Only these gh shapes are ever used for reading, built from the validated repository and
numbers, never from issue text:
    gh api repos/<repo>
    gh api repos/<repo>/issues/<N>
    gh api "repos/<repo>/issues/<N>/comments?per_page=100&page=<P>"   (every page)
    gh api "repos/<repo>/issues?state=closed&since=<time>&per_page=100&page=<P>"

Command line (used by the wrappers; the JSON has the field names `gh issue view --json`
used to give, so the checks that read it did not change):
    github_api.py repo                 print the validated repository
    github_api.py dump N               the issue with its comments, from the repository in the conf
    github_api.py issue REPO N         the issue with every comment (state, labels, author, comments ...)
    github_api.py head REPO N          the same without the comments
    github_api.py owner REPO           {"owner": {"login": ...}}
Exit 0 with JSON on standard output; 1 with a reason on standard error and nothing on
standard output; 2 for a bad command line.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

CONF = "agent-kit.conf"
REPO_NAME = re.compile(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+")
CONF_LINE = re.compile(r"GITHUB_REPO=(?:\"([^\"]*)\"|'([^']*)')[ \t]*")
NUMBER = re.compile(r"[1-9][0-9]*")
PAGE_SIZE = 100
MAX_PAGES = 100


def valid_repo(value) -> bool:
    """True for `<owner>/<name>` with only letters, digits . _ - and no `..` or `.` part."""
    if not isinstance(value, str) or not REPO_NAME.fullmatch(value) or ".." in value:
        return False
    return all(part != "." for part in value.split("/"))


def conf_repo(conf: str = CONF) -> str:
    """The repository named in the conf, read as text; ValueError (a reason) if none is valid."""
    try:
        text = Path(conf).read_bytes().decode("utf-8")
    except (OSError, ValueError):
        raise ValueError(f"cannot read {conf}: no repository to use")
    found = []
    for line in text.split("\n"):
        if line.startswith("GITHUB_REPO="):
            match = CONF_LINE.fullmatch(line)
            found.append(None if match is None else (match.group(1) if match.group(1) is not None
                                                     else match.group(2)))
    if len(found) != 1:
        raise ValueError(f'{conf} needs exactly one GITHUB_REPO="<owner>/<name>" line')
    if not valid_repo(found[0]):
        raise ValueError(f"the GITHUB_REPO value in {conf} is not a valid <owner>/<name>")
    return found[0]


def check_repo(repo) -> str:
    if not valid_repo(repo):
        raise ValueError("the repository is not a valid <owner>/<name>")
    return repo


def check_number(value) -> str:
    if not isinstance(value, str) or not NUMBER.fullmatch(value):
        raise ValueError("the issue number is not valid")
    return value


def gh_api(path: str):
    """Run `gh api <path>` and return its parsed JSON; ValueError with a short reason."""
    try:
        done = subprocess.run(["gh", "api", path], capture_output=True, text=True, encoding="utf-8",
                              stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.SubprocessError) as error:
        raise ValueError(f"cannot run gh: {error}")
    if done.returncode != 0:
        raise ValueError(f"gh api failed (exit {done.returncode})")
    try:
        return json.loads(done.stdout)
    except ValueError:
        raise ValueError("gh api returned malformed JSON")


def gh_api_object(path: str) -> dict:
    data = gh_api(path)
    if not isinstance(data, dict):
        raise ValueError("gh api returned unexpected JSON")
    return data


def gh_api_pages(path: str, limit: int = MAX_PAGES * PAGE_SIZE) -> list:
    """Every item of a paged list: pages of PAGE_SIZE until a short page. ValueError if over limit."""
    joiner = "&" if "?" in path else "?"
    items: list = []
    for page in range(1, MAX_PAGES + 1):
        data = gh_api(f"{path}{joiner}per_page={PAGE_SIZE}&page={page}")
        if not isinstance(data, list):
            raise ValueError("gh api returned unexpected JSON")
        items.extend(data)
        if len(data) < PAGE_SIZE:
            return items
        if len(items) >= limit:
            break
    raise ValueError("too many items to read safely")


def login_of(person):
    """{"login": ...} for a REST user object, None for a null user, the key left out otherwise."""
    return {"login": person.get("login")} if isinstance(person, dict) else None


def head(repo: str, number: str) -> dict:
    """The issue without its comments, with the field names `gh issue view --json` used."""
    repo, number = check_repo(repo), check_number(number)
    issue = gh_api_object(f"repos/{repo}/issues/{number}")
    out: dict = {}
    for key in ("number", "title", "labels"):
        if key in issue:
            out[key] = issue[key]
    if "body" in issue:
        out["body"] = "" if issue["body"] is None else issue["body"]
    if isinstance(issue.get("state"), str):
        out["state"] = issue["state"].upper()
    if "user" in issue:
        out["author"] = login_of(issue["user"])
    return out


def comments(repo: str, number: str) -> list:
    """Every comment, every page, as {"author": {"login"}, "body", "createdAt"}."""
    repo, number = check_repo(repo), check_number(number)
    out = []
    for item in gh_api_pages(f"repos/{repo}/issues/{number}/comments"):
        if not isinstance(item, dict):
            raise ValueError("a comment is malformed")
        comment: dict = {}
        if "user" in item:
            comment["author"] = login_of(item["user"])
        for source, target in (("body", "body"), ("created_at", "createdAt")):
            if source in item:
                comment[target] = item[source]
        out.append(comment)
    return out


def issue(repo: str, number: str) -> dict:
    """The issue with every comment."""
    data = head(repo, number)
    data["comments"] = comments(repo, number)
    return data


def owner(repo: str) -> dict:
    """{"owner": {"login": ...}} for the repository (the key is left out if unreadable)."""
    data = gh_api_object(f"repos/{check_repo(repo)}")
    return {"owner": login_of(data["owner"])} if "owner" in data else {}


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    try:
        if args == ["repo"]:
            print(conf_repo())
            return 0
        if len(args) == 2 and args[0] == "dump":
            print(json.dumps(issue(conf_repo(), args[1])))
            return 0
        if len(args) == 3 and args[0] in ("issue", "head"):
            print(json.dumps((issue if args[0] == "issue" else head)(args[1], args[2])))
            return 0
        if len(args) == 2 and args[0] == "owner":
            print(json.dumps(owner(args[1])))
            return 0
    except ValueError as error:
        print(f"github_api: {error}", file=sys.stderr)
        return 1
    print("Usage: github_api.py repo | dump N | issue REPO N | head REPO N | owner REPO", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
