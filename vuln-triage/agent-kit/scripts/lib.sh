# Shared helpers for the agent kit scripts. Sourced, not run.
# Every script runs from the project folder (the one containing agent-kit.conf).

load_conf() {
  if [ ! -f agent-kit.conf ]; then
    echo "agent-kit: no agent-kit.conf in $(pwd). Run the kit setup first (_docs/agent-kit/setup.md)." >&2
    exit 2
  fi
  KIT_DIR="_docs/agent-kit"
  TEST_CMD="make test"
  LINT_CMD=""
  TYPECHECK_CMD=""
  TEST_FILES=()
  FORBIDDEN=()
  ALLOWED=()
  PROTECTED=()
  # shellcheck disable=SC1091
  . ./agent-kit.conf
}

# matches_any PATH PATTERN... : true if PATH matches any pattern ("*" crosses "/").
matches_any() {
  local path="$1"
  shift
  local pat
  for pat in "$@"; do
    # shellcheck disable=SC2053
    [[ "$path" == $pat ]] && return 0
  done
  return 1
}

section() { printf '\n== %s ==\n' "$1"; }
