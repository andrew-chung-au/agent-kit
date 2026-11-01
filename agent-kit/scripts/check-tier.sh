#!/usr/bin/env bash
# Escalation check for the tiers (process.md, Tiers). Run from the project folder,
# normally as `make tier-check TIER=<light|standard|heavy> [BASE=<commit>]`.
# TIER=light passes only when every changed path matches LIGHT_ALLOWED (agent-kit.conf;
# unset or empty means nothing qualifies), no changed path is on the fixed escalation
# list, and the changed lines total at most LIGHT_MAX_LINES (default 20).
# Standard and heavy have no path limit. Exit 0 = allowed, 1 = needs a higher tier,
# 2 = bad usage. Nothing here sets a tier: only the human's label does.
set -uo pipefail

usage() {
  echo "Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]" >&2
  exit 2
}

TIER="${1-}"
case "$TIER" in
  light | standard | heavy) ;;
  *) usage ;;
esac

if [ "$TIER" != "light" ]; then
  echo "tier-check: TIER=$TIER has no path limit; nothing to check."
  exit 0
fi

. "$(dirname "$0")/lib.sh"
LIGHT_ALLOWED=()
LIGHT_MAX_LINES=20
load_conf

case "$LIGHT_MAX_LINES" in
  '' | *[!0-9]*)
    echo "tier-check: LIGHT_MAX_LINES in agent-kit.conf must be a whole number." >&2
    exit 2
    ;;
esac

BASE="${2-}"
if [ -z "$BASE" ] || [ "$BASE" = "0000000000000000000000000000000000000000" ]; then
  BASE="$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' 2>/dev/null || echo HEAD)"
fi

# Always at least Standard, even when LIGHT_ALLOWED matches.
ESCALATE=(
  "$KIT_DIR/scripts/*" "$KIT_DIR/githooks/*" "$KIT_DIR/claude-code/hooks/*"
  "$KIT_DIR/claude-code/settings.json" "$KIT_DIR/opencode/opencode.json"
  '.claude/*' '.opencode/*' 'opencode.json' '.githooks/*' '.github/*' '.devcontainer/*'
  'Makefile' 'agent-kit.conf'
)
ESCALATE+=("${TEST_FILES[@]}" "${FORBIDDEN[@]}")

escalating=()
outside=()
lines=0
binary=()

classify() { # classify PATH
  if matches_any "$1" "${ESCALATE[@]}"; then
    escalating+=("$1")
  elif [ "${#LIGHT_ALLOWED[@]}" -eq 0 ] || ! matches_any "$1" "${LIGHT_ALLOWED[@]}"; then
    outside+=("$1")
  fi
}

# Tracked changes since BASE (committed, staged and unstaged). -z: NUL-delimited
# "added<TAB>deleted<TAB>path<NUL>", and core.quotePath=false, so git never quotes a name.
while IFS= read -r -d '' rec; do
  added="${rec%%$'\t'*}"
  rest="${rec#*$'\t'}"
  deleted="${rest%%$'\t'*}"
  path="${rest#*$'\t'}"
  [ -z "$path" ] && continue
  classify "$path"
  if [ "$added" = "-" ]; then
    binary+=("$path")
  else
    lines=$((lines + added + deleted))
  fi
done < <(git -c core.quotePath=false diff --relative --numstat --no-renames -z "$BASE" -- .)

# Untracked files count too: they are present when the human reviews.
while IFS= read -r -d '' path; do
  [ -z "$path" ] && continue
  classify "$path"
  n="$(grep -c '' -- "$path" 2>/dev/null || true)"
  lines=$((lines + ${n:-0}))
done < <(git -c core.quotePath=false ls-files --others --exclude-standard -z -- .)

fail=0
if [ "${#escalating[@]}" -gt 0 ]; then
  echo "tier-check: these paths are always at least Standard:"
  printf '  %s\n' "${escalating[@]}"
  fail=1
fi
if [ "${#outside[@]}" -gt 0 ]; then
  echo "tier-check: these paths are not in LIGHT_ALLOWED (agent-kit.conf):"
  printf '  %s\n' "${outside[@]}"
  fail=1
fi
if [ "${#binary[@]}" -gt 0 ]; then
  echo "tier-check: binary files cannot be counted, so they are not Light:"
  printf '  %s\n' "${binary[@]}"
  fail=1
fi
if [ "$lines" -gt "$LIGHT_MAX_LINES" ]; then
  echo "tier-check: $lines changed lines; Light allows at most $LIGHT_MAX_LINES."
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  echo "tier-check: FAIL. This change needs at least Standard; the human must set the tier label."
  exit 1
fi
echo "tier-check: PASS for light ($lines changed lines since $BASE)."
