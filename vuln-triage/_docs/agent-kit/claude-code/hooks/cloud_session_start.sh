#!/usr/bin/env bash
# Claude Code SessionStart hook: prepare a cloud session, do nothing locally.
#
# Local sessions must see no output and no change. In a Claude Code cloud
# session, install dependencies unless the frontend lockfile is current, install
# the repo's git hooks, then print the banner agents use to tell where they are.
set -u

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 1
repo_root="$(cd "${script_dir}/../../../.." && pwd)" || exit 1
cd "${repo_root}" || exit 1

node_lock="frontend/node_modules/.package-lock.json"
package_lock="frontend/package-lock.json"
if [ ! -f "${node_lock}" ] || { [ -f "${package_lock}" ] && [ "${package_lock}" -nt "${node_lock}" ]; }; then
  make install || exit 1
fi

make hooks || exit 1

printf '%s\n' "Environment: Claude Code cloud session (Docker available; push only this session's branch)"
