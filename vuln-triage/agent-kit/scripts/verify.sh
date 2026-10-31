#!/usr/bin/env bash
# Verification gate: tests, optional lint and type checks, whitespace, and weakened-test detection.
# Run from the project folder, normally as `make verify [BASE=<commit>]`.
# BASE defaults to the branch's upstream (all unpushed work), falling back to HEAD.
# Exit 0 = PASS (warnings need a stated reason), 1 = FAIL.
set -uo pipefail
. "$(dirname "$0")/lib.sh"
load_conf

BASE="${1:-}"
if [ -z "$BASE" ] || [ "$BASE" = "0000000000000000000000000000000000000000" ]; then
  BASE="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo HEAD)"
fi
fail=0
warn=0

run_gate() { # run_gate LABEL COMMAND
  section "$1 ($2)"
  if bash -c "$2"; then
    echo "PASS: $1"
  else
    echo "FAIL: $1"
    fail=1
  fi
}

section "Changes in this folder since $BASE"
git diff --stat "$BASE" -- .
untracked="$(git ls-files --others --exclude-standard -- .)"
if [ -n "$untracked" ]; then
  echo "Untracked files (not in the diff, but present when tests run):"
  echo "$untracked"
fi

if [ -n "$TEST_CMD" ]; then
  run_gate "Tests" "$TEST_CMD"
else
  section "Tests"
  echo "WARN: no TEST_CMD in agent-kit.conf, so nothing was tested. Fine only before any code exists."
  warn=1
fi
[ -n "$LINT_CMD" ] && run_gate "Lint" "$LINT_CMD"
[ -n "$TYPECHECK_CMD" ] && run_gate "Type check" "$TYPECHECK_CMD"

section "Whitespace (git diff --check)"
if git diff --check "$BASE" -- .; then
  echo "PASS: no whitespace errors"
else
  echo "FAIL: whitespace errors"
  fail=1
fi

section "Weakened tests"
changed_tests=()
deleted_tests=()
while IFS=$'\t' read -r status path; do
  [ -z "$path" ] && continue
  matches_any "$path" "${TEST_FILES[@]}" || continue
  if [ "$status" = "D" ]; then deleted_tests+=("$path"); else changed_tests+=("$path"); fi
done < <(git diff --relative --name-status --no-renames "$BASE")

if [ "${#deleted_tests[@]}" -gt 0 ]; then
  echo "FAIL: test files deleted:"
  printf '  %s\n' "${deleted_tests[@]}"
  fail=1
fi

if [ "${#changed_tests[@]}" -gt 0 ]; then
  test_diff="$(git diff -U0 "$BASE" -- "${changed_tests[@]}")"
  added="$(printf '%s\n' "$test_diff" | grep -E '^\+[^+]' || true)"
  removed="$(printf '%s\n' "$test_diff" | grep -E '^-[^-]' || true)"

  skips="$(printf '%s\n' "$added" | grep -E \
    'pytest\.mark\.(skip|xfail)|pytest\.skip\(|unittest\.skip|\.skip\(|\.only\(|\.todo\(|\bxit\(|\bxdescribe\(|t\.Skip\(|#\[ignore\]' || true)"
  if [ -n "$skips" ]; then
    echo "FAIL: skip, xfail or focus markers added:"
    printf '%s\n' "$skips"
    fail=1
  fi

  n_added="$(printf '%s\n' "$added" | grep -cE 'assert|expect\(' || true)"
  n_removed="$(printf '%s\n' "$removed" | grep -cE 'assert|expect\(' || true)"
  echo "Assertion lines: $n_added added, $n_removed removed"
  if [ "$n_removed" -gt 0 ]; then
    echo "WARN: assertions removed or rewritten; give a reason for each:"
    printf '%s\n' "$removed" | grep -E 'assert|expect\('
    warn=1
  fi

  fixtures="$(printf '%s\n' "${changed_tests[@]}" | grep -E 'conftest|fixture' || true)"
  if [ -n "$fixtures" ]; then
    echo "WARN: test fixtures changed; check they weren't loosened:"
    printf '  %s\n' $fixtures
    warn=1
  fi
else
  echo "No test files changed."
fi

section "Result"
if [ "$fail" -ne 0 ]; then
  echo "VERIFY: FAIL"
  exit 1
elif [ "$warn" -ne 0 ]; then
  echo "VERIFY: PASS WITH WARNINGS (each warning needs a stated reason)"
else
  echo "VERIFY: PASS"
fi
