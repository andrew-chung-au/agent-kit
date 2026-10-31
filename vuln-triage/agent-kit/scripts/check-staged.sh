#!/usr/bin/env bash
# Pre-commit checks for one project: forbidden files, protected files, whitespace.
# Called by the repo's pre-commit hook from the project folder. Fast: no tests here.
set -uo pipefail
. "$(dirname "$0")/lib.sh"
load_conf

fail=0
forbidden=()
protected=()
while IFS=$'\t' read -r status path; do
  [ -z "$path" ] && continue
  if [ "$status" != "D" ] && matches_any "$path" "${FORBIDDEN[@]}" && ! matches_any "$path" "${ALLOWED[@]}"; then
    forbidden+=("$path")
  fi
  if matches_any "$path" "${PROTECTED[@]}"; then
    protected+=("$path")
  fi
done < <(git diff --cached --relative --name-status --no-renames)

project="$(basename "$(pwd)")"

if [ "${#forbidden[@]}" -gt 0 ]; then
  echo "agent-kit [$project]: these files must never be committed:" >&2
  printf '  %s\n' "${forbidden[@]}" >&2
  echo "  Unstage them with: git restore --staged <path>" >&2
  fail=1
fi

if [ "${#protected[@]}" -gt 0 ] && [ "${HUMAN_APPROVED:-}" != "1" ]; then
  echo "agent-kit [$project]: this commit changes protected files:" >&2
  printf '  %s\n' "${protected[@]}" >&2
  echo "  Protected files change only with human approval. If the human has approved" >&2
  echo "  this specific change, commit with: HUMAN_APPROVED=1 git commit ..." >&2
  fail=1
fi

if ! git diff --cached --check -- . >&2; then
  echo "agent-kit [$project]: whitespace errors in staged changes (see above)." >&2
  fail=1
fi

exit "$fail"
