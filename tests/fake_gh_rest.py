"""A fake `gh` for the `gh api` (REST) calls the kit's GitHub wrappers make.

Import it with `from fake_gh_rest import FAKE_GH, rest_config`. Write FAKE_GH to a file named
`gh` in a folder first on PATH, with a `config.json` beside it. The fake logs every call as one
JSON line in `calls.log` (the argument list), records standard input of create and comment calls
in `stdin.bin`, and answers by kind of call:

    issue_view   GET  repos/<o>/<n>/issues/<N>
    comments     GET  repos/<o>/<n>/issues/<N>/comments?per_page=<S>&page=<P>
    repo_view    GET  repos/<o>/<n>
    issues_list  GET  repos/<o>/<n>/issues?state=closed&since=...&per_page=<S>&page=<P>
    create       POST repos/<o>/<n>/issues
    comment      POST repos/<o>/<n>/issues/<N>/comments
    close        PATCH repos/<o>/<n>/issues/<N>

`config.json` maps a kind to {"stdout": text, "exit": code}; for `comments` and `issues_list`
{"list": [...]} serves that list in pages of the requested size, like GitHub does.
"""
from __future__ import annotations

import json

FAKE_GH = """\
#!/usr/bin/env python3
import json, os, re, sys
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
with open(os.path.join(here, "calls.log"), "a") as log:
    log.write(json.dumps(args) + "\\n")
config = json.load(open(os.path.join(here, "config.json")))
target = args[1] if args[:1] == ["api"] and len(args) > 1 else ""
path = target.split("?")[0]
query = dict(p.split("=", 1) for p in target.split("?", 1)[1].split("&")) if "?" in target else {}
method = args[args.index("--method") + 1] if "--method" in args else "GET"
kind = "other"
R = r"repos/[^/]+/[^/]+"
if method == "POST" and re.fullmatch(R + r"/issues/[0-9]+/comments", path):
    kind = "comment"
elif method == "POST" and re.fullmatch(R + r"/issues", path):
    kind = "create"
elif method == "PATCH" and re.fullmatch(R + r"/issues/[0-9]+", path):
    kind = "close"
elif method == "GET" and re.fullmatch(R + r"/issues/[0-9]+/comments", path):
    kind = "comments"
elif method == "GET" and re.fullmatch(R + r"/issues/[0-9]+", path):
    kind = "issue_view"
elif method == "GET" and re.fullmatch(R + r"/issues", path):
    kind = "issues_list"
elif method == "GET" and re.fullmatch(R, path):
    kind = "repo_view"
if kind in ("create", "comment"):
    with open(os.path.join(here, "stdin.bin"), "ab") as out:
        out.write(sys.stdin.buffer.read())
entry = config.get(kind, {})
if kind in ("comments", "issues_list") and "list" in entry:
    size, page = int(query.get("per_page", "30")), int(query.get("page", "1"))
    sys.stdout.write(json.dumps(entry["list"][(page - 1) * size:page * size]))
else:
    sys.stdout.write(entry.get("stdout", "[]" if kind in ("comments", "issues_list") else ""))
sys.exit(entry.get("exit", 0))
"""


def rest_config(view: str) -> dict:
    """Config entries that make the fake answer like GitHub for an issue written in the
    shape `gh issue view --json state,labels,author,comments` printed (a JSON text). Anything
    that is not a JSON object is served as it is, as the issue's own reply."""
    try:
        data = json.loads(view)
    except ValueError:
        return {"issue_view": {"stdout": view}}
    if not isinstance(data, dict):
        return {"issue_view": {"stdout": view}}
    issue = {key: data[key] for key in ("number", "title", "body", "labels") if key in data}
    if "state" in data:
        issue["state"] = str(data["state"]).lower()
    if "author" in data:
        issue["user"] = data["author"]
    config = {"issue_view": {"stdout": json.dumps(issue)}}
    if "comments" in data:
        config["comments"] = {"list": [rest_comment(c) for c in data["comments"]]}
    return config


def rest_comment(item):
    """One comment in the REST shape, from one in the `gh issue view` shape."""
    if not isinstance(item, dict):
        return item
    out = {}
    if "author" in item:
        out["user"] = item["author"]
    if "body" in item:
        out["body"] = item["body"]
    if "createdAt" in item:
        out["created_at"] = item["createdAt"]
    return out
