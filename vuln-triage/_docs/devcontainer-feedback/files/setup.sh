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

# uv for Python projects (pinned). pipx ships in the base image and installs
# into a directory already on the image PATH.
pipx install uv==0.13.1

# Pin the node bin dir so corepack resolves in this non-interactive script,
# even if nvm's PATH update (from /etc/bash.bashrc) has not run here.
export PATH="/usr/local/share/nvm/versions/node/v24.22.0/bin:$PATH"

# Remove the corepack yarn/pnpm shims. The node feature runs `corepack enable`,
# so a rebuild recreates them. The node bin directory is group-writable by the
# `nvm` group, so no sudo is needed; a second run is a no-op.
corepack disable

git config --global user.name "Andrew Chung"
git config --global user.email "177896104+andrew-chung-au@users.noreply.github.com"

# Let git use the read-only agent token, so fetch and pull work on private repos.
# Pushes are still refused, because the token has no write access.
git config --global credential.https://github.com.helper ""
git config --global --add credential.https://github.com.helper '!gh auth git-credential'

if [ -f Makefile ] && grep -q '^hooks:' Makefile; then make hooks; fi
echo "Setup complete"
