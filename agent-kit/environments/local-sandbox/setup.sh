#!/usr/bin/env bash
# Dev container setup for the local sandbox profile (see environments.md).
# Runs inside the container on first build. Copy it to .devcontainer/setup.sh
# from a clean clone, and fill in the git identity below.
set -euo pipefail
export PATH="$HOME/.local/bin:$HOME/.opencode/bin:$PATH"

# Refuse early in a clean clone. This check comes before anything is installed or
# configured, so a mistaken open of the clean clone in the container changes nothing.
# Same two signals as agent-kit/scripts/install-hooks.sh (keep the two in step): a
# remote named 'sandbox', or the push check in .git/hooks/pre-push. Git and
# coreutils only.
common_dir="$(git rev-parse --git-common-dir 2>/dev/null || true)"
if git remote get-url sandbox >/dev/null 2>&1 || grep -qs '^# agent-kit-push-check' "$common_dir/hooks/pre-push"; then
  echo "setup.sh: this is a clean clone (it has a 'sandbox' remote or the clean-clone push check)." >&2
  echo "  Close this container and reopen the <repo>-sandbox folder in it instead." >&2
  echo "  A clean clone is never opened in a container. See environments.md." >&2
  exit 1
fi

# The Claude volume starts out owned by root; hand it to the container user.
if [ -d "$HOME/.claude" ]; then
  sudo chown -R "$(id -u):$(id -g)" "$HOME/.claude"
fi

if ! command -v make >/dev/null; then
  sudo apt-get update && sudo apt-get install -y make
fi
# OpenCode 2 at a pinned version (unverified pin, like Node and uv). The v1
# installer at /install refuses 2.x; v2 lives at /v2/install and takes --version.
# `opencode --version` prints `opencode v2.2.5`, so match on `v<version>` (a
# 2.2.50 release would not match). The v2 installer has no "already installed"
# shortcut, so this guard is what stops a re-download on a rebuilt container.
opencode_version="2.2.5"
case "$(opencode --version 2>/dev/null || true)" in
  *"v${opencode_version}") ;;
  *) curl -fsSL https://opencode.ai/v2/install | bash -s -- --version "$opencode_version" ;;
esac
command -v claude >/dev/null || curl -fsSL https://claude.ai/install.sh | bash

# uv at a pinned version (unverified pin). Not older than 0.13.4: earlier versions bundle
# a TLS root that was withdrawn (GHSA-hq85-5cpj-mr62). Safe to re-run on a rebuilt container:
# the install runs only when uv is missing or is another version.
case "$(uv --version 2>/dev/null || true)" in
  "uv 0.13.6"*) ;;
  *) pipx install --force uv==0.13.6 ;;
esac

# Node at a pinned version. The Node feature installs it under nvm; put its bin
# directory on PATH for the rest of this script. The version here must equal the
# feature's "version" in devcontainer.json (a test fails when they differ).
node_version="24.22.0"
export PATH="/usr/local/share/nvm/versions/node/v${node_version}/bin:$PATH"

# No yarn or pnpm shims: the project's lockfile tool is npm.
corepack disable

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
