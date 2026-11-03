#!/usr/bin/env bash
# Refuse issue text that looks like it contains a secret.
# Run from the project folder (the one containing agent-kit.conf):
#     bash _docs/agent-kit/scripts/scan-issue-body.sh FILE
# FILE is a readable file, or "-" to read standard input (how the wrappers
# issue-create.sh and issue-comment.sh pass the exact bytes they will post).
#
# The patterns are the lines of <KIT_DIR>/scripts/secret-patterns.txt, read
# through `grep -E -f`; KIT_DIR comes from agent-kit.conf. There is no second
# copy of the patterns.
#
# Exit codes:
#   0  no pattern matched
#   1  at least one matched; prints `FILE:LINE: matches pattern <number>` for
#      each (the number is the pattern's line in the patterns file). The
#      matching text is never printed.
#   2  usage error, FILE missing/unreadable/too large, FILE holds a NUL byte or
#      invalid UTF-8, or the patterns file is missing, empty, unreadable or holds
#      a line grep cannot read (or a pattern that matches an empty line).
# Anything that stops the scan from finishing is exit 2, never exit 0: a secret
# must not be reported as clean because something failed. Unlike vuln-triage's
# scanner this does not use `grep -I`, which skips binary files.
set -u
set -o pipefail
export LC_ALL=C

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 2
# shellcheck source=lib.sh
. "$here/lib.sh"
# shellcheck source=issue-text-lib.sh
. "$here/issue-text-lib.sh"

MAX_SCAN_BYTES=1048576

refuse() {
  echo "scan-issue-body: $1" >&2
  exit 2
}

if [ "$#" -ne 1 ]; then
  echo "Usage: scan-issue-body.sh FILE (or - for standard input)" >&2
  exit 2
fi
file="$1"

load_conf
[ -n "${KIT_DIR:-}" ] || refuse "KIT_DIR is empty in agent-kit.conf"
patterns="$KIT_DIR/scripts/secret-patterns.txt"
[ -f "$patterns" ] && [ -r "$patterns" ] || refuse "patterns file $patterns is missing or unreadable"
[ -s "$patterns" ] || refuse "patterns file $patterns is empty"
grep -E -f "$patterns" /dev/null 2>/dev/null
[ "$?" -le 1 ] || refuse "patterns file $patterns holds a line grep cannot read"
# A pattern that matches an empty line would refuse every file.
if printf '\n' | grep -q -E -f "$patterns" 2>/dev/null; then
  refuse "patterns file $patterns holds a pattern that matches an empty line"
fi

if [ "$file" != "-" ]; then
  [ -f "$file" ] && [ -r "$file" ] || refuse "$file is missing, not a regular file or unreadable"
fi
read_b64 "$file" "$MAX_SCAN_BYTES" || refuse "cannot read $file"
size=$(b64_size) || refuse "cannot measure $file"
[ "$size" -le "$MAX_SCAN_BYTES" ] || refuse "$file is larger than $MAX_SCAN_BYTES bytes"
if b64_has_nul; then refuse "$file holds a NUL byte (or cannot be checked for one)"; fi
b64_is_utf8 || refuse "$file is not valid UTF-8"

status=0
number=0
env_hint=0
# A shell command naming an env file, built from pieces so this script keeps no copy of
# any pattern. A matched pattern that also refuses this probe is the env-file pattern.
env_probe="cat .e""nv"
while IFS= read -r pattern || [ -n "$pattern" ]; do
  number=$((number + 1))
  hits=$(b64_decode | grep -a -n -E -f <(printf '%s\n' "$pattern") 2>/dev/null)
  code=$?
  if [ "$code" -eq 1 ]; then
    continue
  fi
  [ "$code" -eq 0 ] || refuse "grep failed on pattern $number"
  while IFS=: read -r line _; do
    echo "$file:$line: matches pattern $number"
  done <<< "$hits"
  if printf '%s\n' "$env_probe" | grep -q -E -f <(printf '%s\n' "$pattern") 2>/dev/null; then
    env_hint=1
  fi
  status=1
done < "$patterns"
if [ "$env_hint" -eq 1 ]; then
  echo "scan-issue-body: the text names an env file; describe it in words instead, for example \"the example env file\", and post again." >&2
fi
exit "$status"
