#!/usr/bin/env bash
# Refuse an issue body that looks like it contains a secret. Prints the pattern
# and line number, never the matching text, so the terminal log stays clean.
# Usage: scan-issue-body.sh FILE
set -u

file="${1:?Usage: scan-issue-body.sh FILE}"
status=0
patterns=(
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'
  'ghp_[A-Za-z0-9]{36}'
  'github_pat_[A-Za-z0-9_]{22,}'
  'AKIA[0-9A-Z]{16}'
  'xox[baprs]-[A-Za-z0-9-]{10,}'
  'sk-[A-Za-z0-9]{20,}'
)
for p in "${patterns[@]}"; do
  if grep -nEI -- "$p" "$file" >/dev/null; then
    echo "possible secret in $file (pattern: $p); redact it or ask the human to post manually" >&2
    status=1
  fi
done
exit "$status"
