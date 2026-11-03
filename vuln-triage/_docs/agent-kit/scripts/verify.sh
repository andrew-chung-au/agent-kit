#!/usr/bin/env bash
# Verification gate: tests, optional lint and type checks, whitespace, and weakened-test detection.
# Run from the project folder, normally as `make verify [BASE=<commit>]`.
# BASE defaults to the branch's upstream (all unpushed work), falling back to HEAD.
# Exit 0 = PASS (warnings need a stated reason), 1 = FAIL.
set -uo pipefail
. "$(dirname "$0")/lib.sh"
# Optional in agent-kit.conf; reset here so a missing array means "none approved"
# and nothing from the environment can add an approval.
APPROVED_TEST_DELETIONS=()
load_conf

BASE="${1:-}"
if [ -z "$BASE" ] || [ "$BASE" = "0000000000000000000000000000000000000000" ]; then
  BASE="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo HEAD)"
fi
fail=0
warn=0

# BASE may be a commit or a tree: the pre-push hook passes the empty tree for a new
# branch with no parent, so resolve with ^{tree} (a commit resolves to its tree too).
# An unresolvable BASE would make every git diff below print an error and compare
# nothing, so refuse it before any check runs.
if ! git rev-parse --verify -q "$BASE^{tree}" >/dev/null; then
  echo "FAIL: BASE '$BASE' does not resolve to a commit or tree"
  echo "VERIFY: FAIL"
  exit 1
fi
base_commit="$(git rev-parse --verify -q "$BASE^{commit}" 2>/dev/null || true)"

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
# Skipped when BASE is a tree (base_commit is empty): the empty-tree case.
if [ -n "$base_commit" ] && [ "$base_commit" = "$(git rev-parse --verify -q HEAD || true)" ]; then
  echo "WARN: BASE ($BASE) is the same commit as HEAD, so only uncommitted changes were compared; pass BASE=<commit>"
  warn=1
fi
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
# Renames are detected with -M (git's default similarity threshold, 50%). A rename
# line is "R<score><TAB>old<TAB>new":
#   - R100 from a test path to a test path is a move: not a deletion, not a change.
#   - R<100 to a test path is a changed test, diffed from the old to the new contents.
#   - a rename whose new path no longer matches TEST_FILES deletes the old test file.
#   - a move edited so much that git doesn't pair the two paths shows as D + A, so it
#     counts as a deletion. This is deliberate: when in doubt, fail.
# A deletion passes only if its exact path is in APPROVED_TEST_DELETIONS.
changed_tests=()   # new paths of changed test files
diff_paths=()      # pathspecs for the content diff (includes the old side of renames)
deleted_tests=()
while IFS=$'\t' read -r status path newpath; do
  [ -z "$path" ] && continue
  if [ "${status:0:1}" = "R" ] && [ -n "$newpath" ]; then
    old_is_test=0
    matches_any "$path" "${TEST_FILES[@]}" && old_is_test=1
    if matches_any "$newpath" "${TEST_FILES[@]}"; then
      if [ "$old_is_test" -eq 1 ] && [ "$status" = "R100" ]; then
        continue
      fi
      changed_tests+=("$newpath")
      diff_paths+=("$newpath")
      # Only pair with the old contents if the old file was a test file too;
      # otherwise the new test file is checked as an addition, as before.
      [ "$old_is_test" -eq 1 ] && diff_paths+=("$path")
    elif [ "$old_is_test" -eq 1 ]; then
      deleted_tests+=("$path")
    fi
    continue
  fi
  matches_any "$path" "${TEST_FILES[@]}" || continue
  if [ "$status" = "D" ]; then
    deleted_tests+=("$path")
  else
    changed_tests+=("$path")
    diff_paths+=("$path")
  fi
done < <(git diff --relative --name-status -M "$BASE")

# Approved deletions: exact paths only. A glob entry is a config error and is never matched.
approved=()
for entry in "${APPROVED_TEST_DELETIONS[@]}"; do
  case "$entry" in
    *[\*\?\[]*)
      echo "FAIL: APPROVED_TEST_DELETIONS entry '$entry' contains a glob character; only exact paths are allowed"
      fail=1
      ;;
    *) approved+=("$entry") ;;
  esac
done
unapproved_deletions=()
approved_deletions=()
for path in "${deleted_tests[@]}"; do
  ok=0
  for entry in "${approved[@]}"; do
    if [ "$path" = "$entry" ]; then ok=1; break; fi
  done
  if [ "$ok" -eq 1 ]; then approved_deletions+=("$path"); else unapproved_deletions+=("$path"); fi
done

if [ "${#approved_deletions[@]}" -gt 0 ]; then
  echo "Deleted with approval (APPROVED_TEST_DELETIONS in agent-kit.conf):"
  printf '  %s\n' "${approved_deletions[@]}"
fi

if [ "${#unapproved_deletions[@]}" -gt 0 ]; then
  echo "FAIL: test files deleted:"
  printf '  %s\n' "${unapproved_deletions[@]}"
  fail=1
fi

if [ "${#changed_tests[@]}" -gt 0 ]; then
  test_diff="$(git diff -U0 -M "$BASE" -- "${diff_paths[@]}")"
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
