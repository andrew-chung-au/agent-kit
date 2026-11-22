#!/usr/bin/env bash
# Post one comment on a GitHub issue from a text file, after checking every input.
# Run through the make target, from the project folder:
#     make issue-comment N=<issue number> FILE=.scratch/<name>.md
# or directly: bash _docs/agent-kit/scripts/issue-comment.sh <number> .scratch/<name>.md
#
# The whole of FILE is the comment. Its first line starts at column 1 with a role:
# PM:, Engineer:, QA: or Orchestrator: (process.md, Issue comments). On success it
# prints the comment's URL and nothing else.
#
# The target-issue rule (AGENTS.md, Issues): comment only on an issue that carries
# `approved` or whose author is the repository owner. The script reads both and
# fails closed: if gh is missing, fails, prints nothing or malformed JSON, or a
# field is missing, it refuses and posts nothing.
#
# The repository is the GITHUB_REPO line of agent-kit.conf (github_api.py validates
# it), and the REST API is used because `gh issue` cannot find the repository from the
# git remote everywhere (Kiro Web). The only gh calls it makes are these three shapes:
#     gh api repos/<repo>/issues/<N>
#     gh api repos/<repo>
#     gh api repos/<repo>/issues/<N>/comments --method POST -F body=@-
# (the last is the only write; the first two are made by github_api.py). No label,
# edit, close, reopen or delete call. The gh arguments are fixed; FILE's text only goes
# to the scanner and to gh on standard input, never to a shell. The bytes scanned are
# the bytes posted.
#
# When gh fails, this script's one-line reason is printed first, then gh's own
# standard error, each line prefixed `issue-comment: gh: `, so the cause is not lost.
# The text is redacted with the lines of scripts/secret-patterns.txt (the one copy,
# read next to this script): every match becomes `[redacted]`. At most 20 lines and
# 4000 bytes of it are printed. If the redaction cannot run (the patterns file is
# missing, empty or unreadable, gh's standard error is not valid UTF-8, or it holds a
# NUL byte), gh's text is withheld and one line says so. The same applies to the reason
# github_api.py gives when one of the two reads fails. A successful post prints the URL
# alone; gh's standard error is discarded then, as it always was.
#
# Exit codes: 0 posted; 1 gh failed or printed no URL after the target check (no
# retry); 2 bad N, FILE or prefix (no gh command ran); 3 the secret scan refused
# (no gh command ran); 4 the target issue is not allowed or could not be checked.
set -u
set -o pipefail
export LC_ALL=C

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 2
die() {
  echo "issue-comment: $2" >&2
  exit "$1"
}
# show_gh_text FILE: print FILE's text, redacted and capped, one `issue-comment: gh: `
# line each. The patterns are the lines of secret-patterns.txt next to this script. If
# the redaction cannot run, print one notice and no text at all (fail closed).
show_gh_text() {
  local file="$1" text code line
  text=$(python3 -B -c '
import re, sys
MAX_LINES = 20
MAX_BYTES = 4000
try:
    data = sys.stdin.buffer.read().decode("utf-8")
except UnicodeDecodeError:
    sys.exit(2)
if "\x00" in data:
    sys.exit(2)
try:
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        patterns = [p.rstrip("\r") for p in fh.read().split("\n")]
    patterns = [p for p in patterns if p != ""]
    if not patterns:
        sys.exit(2)
    regexes = [re.compile(p, re.MULTILINE) for p in patterns]
except (OSError, UnicodeDecodeError, re.error):
    sys.exit(2)
if any(regex.search("") for regex in regexes):
    sys.exit(2)
for regex in regexes:
    data = regex.sub("[redacted]", data)
text = "\n".join(data.splitlines()[:MAX_LINES])
out = text.encode("utf-8")[:MAX_BYTES].decode("utf-8", "ignore").encode("utf-8")
sys.stdout.buffer.write(out)
' "$here/secret-patterns.txt" < "$file")
  code=$?
  if [ "$code" -ne 0 ]; then
    printf '%s\n' "issue-comment: withheld gh's error text because the redaction could not run" >&2
    return 0
  fi
  [ -n "$text" ] || return 0
  while IFS= read -r line; do
    printf '%s\n' "issue-comment: gh: $line" >&2
  done <<< "$text"
}
# die_gh CODE REASON FILE: the one-line reason first, then FILE's gh text, then exit.
die_gh() {
  echo "issue-comment: $2" >&2
  show_gh_text "$3"
  exit "$1"
}
# shellcheck source=issue-text-lib.sh
. "$here/issue-text-lib.sh"

[ "$#" -eq 2 ] || die 2 "Usage: issue-comment.sh N FILE (N is an issue number; FILE is under .scratch/ and starts with PM:, Engineer:, QA: or Orchestrator:)"
number="$1"
file="$2"
check_number "$number"
check_file_arg "$file"
load_issue_file "$file"

case "$CONTENT" in
  "PM:"* | "Engineer:"* | "QA:"* | "Orchestrator:"*) ;;
  *) die 2 "the first line of FILE must start at column 1 with PM:, Engineer:, QA: or Orchestrator:" ;;
esac

scan_content "$file"

# Target-issue rule. Every failure to find out is a refusal.
command -v gh > /dev/null 2>&1 || die 4 "cannot check issue $number: gh was not found; nothing was posted"
github_repo || die 4 "cannot check issue $number: no valid GITHUB_REPO=\"<owner>/<name>\" line in agent-kit.conf; nothing was posted"
errfile=$(mktemp "${TMPDIR:-/tmp}/issue-comment.XXXXXX") || die 4 "cannot check issue $number: cannot create a temporary file; nothing was posted"
trap 'rm -f -- "$errfile"' EXIT
issue_json=$(python3 -B "$here/github_api.py" head "$REPO" "$number" 2> "$errfile") || die_gh 4 "cannot read issue $number with gh; nothing was posted" "$errfile"
repo_json=$(python3 -B "$here/github_api.py" owner "$REPO" 2> "$errfile") || die_gh 4 "cannot read the repository owner with gh; nothing was posted" "$errfile"
python3 -B -c '
import json, sys
# Exit 0: the issue is "approved" or owner-authored. 1: readable but neither. 2: unreadable.
try:
    issue = json.loads(sys.argv[1])
    repo = json.loads(sys.argv[2])
    labels = issue["labels"]
    author = issue["author"]["login"]
    owner = repo["owner"]["login"]
    names = [label["name"] for label in labels]
    if not isinstance(labels, list) or not all(isinstance(n, str) for n in names):
        sys.exit(2)
    if not (isinstance(author, str) and author and isinstance(owner, str) and owner):
        sys.exit(2)
except Exception:
    sys.exit(2)
sys.exit(0 if ("approved" in names or author == owner) else 1)
' "$issue_json" "$repo_json"
case "$?" in
  0) ;;
  1) die 4 "issue $number has no approved label and its author is not the repository owner; nothing was posted" ;;
  *) die 4 "cannot tell whether issue $number is approved or owner-authored; nothing was posted" ;;
esac

out=$(gh api "repos/$REPO/issues/$number/comments" --method POST -F body=@- 2> "$errfile" < <(printf '%s' "$CONTENT"))
code=$?
[ "$code" -eq 0 ] || die_gh 1 "gh issue comment failed (exit $code); nothing was retried, so check GitHub before posting again" "$errfile"
print_url "$out"
