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
# The only gh calls it makes are these three shapes:
#     gh issue view <N> --json labels,author
#     gh repo view --json owner
#     gh issue comment <N> --body-file -
# (the last is the only write). No label, edit, close, reopen, delete or API call.
# The gh arguments are fixed; FILE's text only goes to the scanner and to gh on
# standard input, never to a shell. The bytes scanned are the bytes posted.
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
issue_json=$(gh issue view "$number" --json labels,author 2> /dev/null) || die 4 "cannot read issue $number with gh; nothing was posted"
repo_json=$(gh repo view --json owner 2> /dev/null) || die 4 "cannot read the repository owner with gh; nothing was posted"
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

out=$(gh issue comment "$number" --body-file - 2> /dev/null < <(printf '%s' "$CONTENT"))
code=$?
[ "$code" -eq 0 ] || die 1 "gh issue comment failed (exit $code); nothing was retried, so check GitHub before posting again"
print_url "$out"
