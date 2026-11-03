#!/usr/bin/env bash
# Fails if this project folder has uncommitted or untracked changes.
# Used to confirm a review-only role (QA) changed nothing. Run as `make assert-clean`.
set -uo pipefail
changes="$(git status --porcelain --untracked-files=all -- .)"
if [ -n "$changes" ]; then
  echo "ASSERT-CLEAN: FAIL. Uncommitted or untracked changes in $(pwd):"
  echo "$changes"
  exit 1
fi
echo "ASSERT-CLEAN: PASS (no changes in this folder; HEAD is $(git rev-parse --short HEAD))"
