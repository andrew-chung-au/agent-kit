#!/usr/bin/env bash
# Fails if this project folder has uncommitted or untracked changes.
# Used to confirm a review-only role (QA) changed nothing. Run as `make assert-clean`.
# Fails closed: if git itself fails, or there is no HEAD commit to compare against
# (a repository with no commits), it says why and exits 1. It never prints PASS then.
set -uo pipefail
changes="$(git status --porcelain --untracked-files=all -- .)"
status=$?
if [ "$status" -ne 0 ]; then
  echo "ASSERT-CLEAN: FAIL. git status failed (exit $status) in $(pwd), so nothing was checked."
  exit 1
fi
if [ -n "$changes" ]; then
  echo "ASSERT-CLEAN: FAIL. Uncommitted or untracked changes in $(pwd):"
  echo "$changes"
  exit 1
fi
head="$(git rev-parse --short HEAD 2>/dev/null)"
if [ "$?" -ne 0 ] || [ -z "$head" ]; then
  echo "ASSERT-CLEAN: FAIL. There is no HEAD commit to compare against in $(pwd) (a repository with no commits, or git could not read HEAD)."
  exit 1
fi
echo "ASSERT-CLEAN: PASS (no changes in this folder; HEAD is $head)"
