#!/usr/bin/env bash
# Open one draft pull request from the current branch to the default branch, after
# checking every input. Run through the make target, from the project folder:
#     make pr-open N=<issue number> FILE=.scratch/<name>.md
# or directly: bash _docs/agent-kit/scripts/pr-open.sh <number> .scratch/<name>.md
#
# FILE is read as `make issue-create` reads it: first line `Title: <text>`, a blank
# line, then the body, written from templates/github/pull_request_template.md. On
# success it prints the pull request's URL and nothing else on standard output.
#
# Refused, with the reason and no GitHub write call (process.md, Commits and pushes):
#   - a bad N or FILE (the issue-comment rules, issue-text-lib.sh), or a bad Title: line;
#   - a body without the line `Refs #<N>` for this N;
#   - a closing keyword (close, closes, closed, fix, fixes, fixed, resolve, resolves,
#     resolved, any case) before an issue reference: only the orchestrator closes issues;
#   - text the secret scan (scan-issue-body.sh) refuses;
#   - a detached HEAD, the default branch, or a branch whose origin copy is not at HEAD
#     (not yet pushed). The origin copy is the local remote-tracking ref; nothing is fetched.
# When an open pull request for the branch already exists, it prints that URL, creates
# nothing and exits 0. A closed or merged one does not count: a session branch name can
# be reused after its pull request merges.
#
# The repository is the GITHUB_REPO line of agent-kit.conf (github_api.py validates it).
# The only gh calls it makes are these three shapes, built from the validated repository,
# branch names and the title, never passed to a shell:
#     gh api repos/<repo>
#     gh api "repos/<repo>/pulls?state=open&head=<owner>:<branch>&per_page=100"
#     gh api repos/<repo>/pulls --method POST -f title=<title> -f head=<branch>
#            -f base=<default branch> -F draft=true -F body=@-
# (the last is the only write; the body goes on standard input). It never readies,
# merges, closes, labels or pushes. The bytes scanned are the bytes posted.
#
# Exit codes: 0 opened, or an open pull request already exists; 1 gh failed or printed
# no URL (no retry); 2 bad N, FILE, title or body (no gh command ran); 3 the secret scan
# refused (no gh command ran); 4 the branch is refused (detached, default, not pushed,
# or a name outside letters, digits and . _ / -).
set -u
set -o pipefail
export LC_ALL=C

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 2
die() {
  echo "pr-open: $2" >&2
  exit "$1"
}
# shellcheck source=issue-text-lib.sh
. "$here/issue-text-lib.sh"

[ "$#" -eq 2 ] || die 2 "Usage: pr-open.sh N FILE (N is the issue number; FILE is under .scratch/: first line Title: <text>, a blank line, then the body with a Refs #N line)"
number="$1"
file="$2"
check_number "$number"
check_file_arg "$file"
load_issue_file "$file"

first="${CONTENT%%$'\n'*}"
case "$CONTENT" in
  *$'\n'*) rest="${CONTENT#*$'\n'}" ;;
  *) die 2 "FILE needs a Title: line, a blank line, then a body; nothing was opened" ;;
esac
case "$first" in
  "Title: "*) raw_title="${first#"Title: "}" ;;
  *) die 2 "the first line of FILE must start with: Title: ; nothing was opened" ;;
esac
case "$rest" in
  $'\n'*) body="${rest#?}" ;;
  *) die 2 "the line after the Title: line must be blank; nothing was opened" ;;
esac
[ -n "${body//[[:space:]]/}" ] || die 2 "the body after the blank line is empty; nothing was opened"

title=$(printf '%s' "$raw_title" | python3 -B -c '
import sys, unicodedata
text = sys.stdin.buffer.read().decode("utf-8").strip(" ")
bad = not 1 <= len(text) <= 200 or text.startswith("-")
bad = bad or any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in text)
if bad:
    sys.exit(1)
sys.stdout.write(text)
') || die 2 "the title must be 1 to 200 characters, with no control characters, and must not start with -; nothing was opened"

# The body rules, on the exact text: the Refs line, then the closing keywords (in the
# title too, to be safe). Exit 3: no Refs line; 4: a closing keyword; other: cannot check.
printf '%s' "$CONTENT" | python3 -B -c '
import re, sys
number = sys.argv[1]
try:
    text = sys.stdin.buffer.read().decode("utf-8")
except UnicodeDecodeError:
    sys.exit(2)
body = text.split("\n", 2)[2] if text.count("\n") >= 2 else ""
if not any(line.rstrip(" \t\r") == "Refs #" + number for line in body.split("\n")):
    sys.exit(3)
# A closing keyword, then spaces, a colon or emphasis marks, then an issue reference:
# #12, owner/name#12, or a URL ending in /issues/12 or /pull/12.
keyword = r"(?<![A-Za-z0-9_])(?:close[sd]?|fix(?:es|ed)?|resolve[sd]?)(?![A-Za-z0-9_])"
reference = r"(?:#[0-9]+|[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[0-9]+|https?://[^\s)>\]]*/(?:issues|pull)/[0-9]+)"
if re.search(keyword + r"[\s:*_`]*" + reference, text, re.IGNORECASE):
    sys.exit(4)
sys.exit(0)
' "$number"
case "$?" in
  0) ;;
  3) die 2 "the body has no line Refs #$number; nothing was opened" ;;
  4) die 2 "the text has a closing keyword (close, fix or resolve, any form) before an issue reference; only the orchestrator closes issues (write Refs #$number); nothing was opened" ;;
  *) die 2 "cannot check the body's Refs line and closing keywords; nothing was opened" ;;
esac

scan_content "$file"

# The branch: named (not detached), letters digits . _ / - only, and pushed (origin's copy
# is at HEAD). Read from git only; nothing is fetched or pushed.
branch=$(git symbolic-ref --quiet --short HEAD 2> /dev/null) || die 4 "HEAD is detached; check out the session branch; nothing was opened"
case "$branch" in
  "" | -* | *[!A-Za-z0-9._/-]* | *..*) die 4 "the branch name must use only letters, digits and . _ / -; nothing was opened" ;;
esac
head_sha=$(git rev-parse --verify --quiet "HEAD^{commit}" 2> /dev/null) || die 4 "cannot read HEAD; nothing was opened"
origin_sha=$(git rev-parse --verify --quiet "refs/remotes/origin/$branch^{commit}" 2> /dev/null) \
  || die 4 "origin has no copy of branch $branch: push it first (git push -u origin $branch); nothing was opened"
[ "$head_sha" = "$origin_sha" ] || die 4 "origin/$branch is not at HEAD: push the branch first; nothing was opened"

command -v gh > /dev/null 2>&1 || die 1 "gh was not found; nothing was opened"
github_repo || die 1 "no valid GITHUB_REPO=\"<owner>/<name>\" line in agent-kit.conf; nothing was opened"
owner="${REPO%%/*}"

repo_json=$(gh api "repos/$REPO" 2> /dev/null) || die 1 "cannot read the repository with gh; nothing was opened"
base=$(printf '%s' "$repo_json" | python3 -B -c '
import json, re, sys
try:
    name = json.loads(sys.stdin.read())["default_branch"]
except Exception:
    sys.exit(1)
if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9._/-]+", name) or name.startswith("-") or ".." in name:
    sys.exit(1)
sys.stdout.write(name)
') || die 1 "cannot read the default branch from gh; nothing was opened"
[ "$branch" != "$base" ] || die 4 "the current branch is the default branch ($base); open a pull request only from the session branch; nothing was opened"

list_json=$(gh api "repos/$REPO/pulls?state=open&head=$owner:$branch&per_page=100" 2> /dev/null) \
  || die 1 "cannot list the open pull requests for $branch with gh; nothing was opened"
existing=$(printf '%s' "$list_json" | python3 -B -c '
import json, sys
# Exit 0 printing the URL: one exists. 3: none. 1: unreadable.
try:
    items = json.loads(sys.stdin.read())
except Exception:
    sys.exit(1)
if not isinstance(items, list):
    sys.exit(1)
if not items:
    sys.exit(3)
url = items[0].get("html_url") if isinstance(items[0], dict) else None
if not isinstance(url, str) or not url.startswith("https://") or any(c.isspace() for c in url):
    sys.exit(1)
sys.stdout.write(url)
')
case "$?" in
  0)
    echo "pr-open: an open pull request for $branch already exists; nothing was created" >&2
    printf '%s\n' "$existing"
    exit 0
    ;;
  3) ;;
  *) die 1 "gh returned an unreadable list of pull requests for $branch; nothing was opened" ;;
esac

out=$(gh api "repos/$REPO/pulls" --method POST -f "title=$title" -f "head=$branch" -f "base=$base" \
  -F draft=true -F body=@- 2> /dev/null < <(printf '%s' "$body"))
code=$?
[ "$code" -eq 0 ] || die 1 "gh pull request create failed (exit $code); nothing was retried, so check GitHub before opening again"
print_url "$out"
