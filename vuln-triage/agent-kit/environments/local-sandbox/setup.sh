#!/usr/bin/env bash
# Dev container setup for the local sandbox profile (see environments.md).
# Runs inside the container on first build. Copy it to .devcontainer/setup.sh
# from a clean clone, and fill in the git identity below.
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$PATH"

# The Claude volume starts out owned by root; hand it to the container user.
if [ -d "$HOME/.claude" ]; then
  sudo chown -R "$(id -u):$(id -g)" "$HOME/.claude"
fi

if ! command -v make >/dev/null; then
  sudo apt-get update && sudo apt-get install -y make
fi
command -v opencode >/dev/null || curl -fsSL https://opencode.ai/install | bash
command -v claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash

git config --global user.name "<Your Name>"
git config --global user.email "<id+username@users.noreply.github.com>"

# Let git use the read-only agent token, so fetch and pull work on private repos.
# Pushes are still refused, because the token has no write access.
git config --global credential.https://github.com.helper ""
git config --global --add credential.https://github.com.helper '!gh auth git-credential'

# Install the agent kit's git hooks, here in the container only. They are
# repo-wide, so one project's `make hooks` covers a whole monorepo.
kit_project=""
if [ -f agent-kit.conf ]; then
  kit_project="."
else
  conf="$(find . -maxdepth 3 -name agent-kit.conf -not -path './.git/*' | sort | head -n 1)"
  [ -n "$conf" ] && kit_project="$(dirname "$conf")"
fi
if [ -n "$kit_project" ] && grep -q '^hooks:' "$kit_project/Makefile" 2>/dev/null; then
  make -C "$kit_project" hooks
fi
echo "Setup complete"
