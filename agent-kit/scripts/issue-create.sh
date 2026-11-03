#!/usr/bin/env bash
# File one GitHub issue from a text file, after checking every input.
# Run through the make target, from the project folder:
#     make issue-create FILE=.scratch/<name>.md
# or directly: bash _docs/agent-kit/scripts/issue-create.sh .scratch/<name>.md
#
# FILE's first line is `Title: <text>`, then one blank line, then the body.
# On success it prints the new issue's URL and nothing else.
#
# This script can do ONE thing to GitHub: `gh issue create --title <t> --body-file -`.
# It never adds a label, assignee, project or milestone, and never edits, closes
# or deletes anything. The gh arguments are fixed; FILE's text only goes to the
# scanner and to gh on standard input, never to a shell.
#
# Exit codes: 0 filed; 1 gh missing or failed, or printed no URL (no retry: a
# retried create could file a duplicate); 2 bad FILE or title (no gh command
# ran); 3 the secret scan refused (no gh command ran).
# The bytes scanned are the bytes posted: FILE is read once (issue-text-lib.sh).
set -u
set -o pipefail
export LC_ALL=C

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 2
die() {
  echo "issue-create: $2" >&2
  exit "$1"
}
# shellcheck source=issue-text-lib.sh
. "$here/issue-text-lib.sh"

[ "$#" -eq 1 ] || die 2 "Usage: issue-create.sh FILE (FILE is under .scratch/; first line Title: <text>, then a blank line, then the body)"
file="$1"
check_file_arg "$file"
load_issue_file "$file"

# The first line must be `Title: <text>`, the second must be empty, the body follows.
first="${CONTENT%%$'\n'*}"
case "$CONTENT" in
  *$'\n'*) rest="${CONTENT#*$'\n'}" ;;
  *) die 2 "FILE needs a Title: line, a blank line, then a body" ;;
esac
case "$first" in
  "Title: "*) raw_title="${first#"Title: "}" ;;
  *) die 2 "the first line of FILE must start with: Title: " ;;
esac
case "$rest" in
  $'\n'*) body="${rest#?}" ;;
  *) die 2 "the line after the Title: line must be blank" ;;
esac
[ -n "${body//[[:space:]]/}" ] || die 2 "the body after the blank line is empty"

# 1 to 200 characters after trimming spaces, no control characters, not starting with -.
title=$(printf '%s' "$raw_title" | python3 -B -c '
import sys, unicodedata
text = sys.stdin.buffer.read().decode("utf-8").strip(" ")
bad = not 1 <= len(text) <= 200 or text.startswith("-")
bad = bad or any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in text)
if bad:
    sys.exit(1)
sys.stdout.write(text)
') || die 2 "the title must be 1 to 200 characters, with no control characters, and must not start with -"

scan_content "$file"

command -v gh > /dev/null 2>&1 || die 1 "gh was not found; nothing was filed"
out=$(gh issue create --title "$title" --body-file - 2> /dev/null < <(printf '%s' "$body"))
code=$?
[ "$code" -eq 0 ] || die 1 "gh issue create failed (exit $code); nothing was retried, so check GitHub before filing again"
print_url "$out"
