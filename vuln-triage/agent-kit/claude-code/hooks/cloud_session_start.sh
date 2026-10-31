#!/usr/bin/env bash
# Claude Code SessionStart hook: print where the session runs.
# Extend this in the project copy, for example to install dependencies and hooks.
set -u

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

printf '%s\n' "Environment: Claude Code cloud session (Docker available; push only this session's branch)"
