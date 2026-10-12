#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$PATH"

# The Claude volume starts out owned by root; hand it to the container user
if [ -d "$HOME/.claude" ]; then
  sudo chown -R "$(id -u):$(id -g)" "$HOME/.claude"
fi

if ! command -v make >/dev/null; then
  sudo apt-get update && sudo apt-get install -y make
fi
command -v opencode >/dev/null || curl -fsSL https://opencode.ai/install | bash
command -v claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash

git config --global user.name "Andrew Chung"
git config --global user.email "177896104+andrew-chung-au@users.noreply.github.com"

# Let git use the read-only agent token, so fetch and pull work on private repos.
# Pushes are still refused, because the token has no write access.
git config --global credential.https://github.com.helper ""
git config --global --add credential.https://github.com.helper '!gh auth git-credential'

if [ -f Makefile ] && grep -q '^hooks:' Makefile; then make hooks; fi
echo "Setup complete"
