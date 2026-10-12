# --- Agent sandbox helpers ---
# Set up a repo: clean clone + sandbox, linked, with the push check installed.
# Safe to re-run: it skips anything that already exists.
agent-clone() {
  local url="${1:?usage: agent-clone <github-url> [name]}"
  local name="${2:-$(basename "$url" .git)}"
  local clean="$HOME/projects/$name" sb="$HOME/projects/$name-sandbox"
  [ -d "$clean" ] || git clone "$url" "$clean" || return
  [ -d "$sb" ] || git clone "$url" "$sb" || return
  git -C "$clean" remote get-url sandbox >/dev/null 2>&1 ||
    git -C "$clean" remote add sandbox "file://$sb"
  clean-hook "$name"
  echo "Clean:   $clean"
  echo "Sandbox: $sb"
}

# Install the push check in a clean clone
clean-hook() {
  local clean="$HOME/projects/${1:?usage: clean-hook <repo-name>}"
  if git -C "$clean" config --get core.hooksPath >/dev/null; then
    echo "WARNING: core.hooksPath was set in $clean; removing it so the push check runs"
    git -C "$clean" config --unset core.hooksPath
  fi
  cp ~/.agent-hooks/pre-push "$clean/.git/hooks/pre-push" &&
  chmod +x "$clean/.git/hooks/pre-push" &&
  echo "Push check installed in $clean"
}

# Before opening a sandbox: compare its recipe with the clean clone's
sandbox-check() {
  local name="${1:?usage: sandbox-check <repo-name>}"
  local clean="$HOME/projects/$name" sb="$HOME/projects/$name-sandbox"
  [ -e "$sb/.devcontainer.json" ] && echo "WARNING: unexpected $sb/.devcontainer.json"
  if diff -r "$clean/.devcontainer" "$sb/.devcontainer"; then
    echo "Recipe matches the clean clone: OK to open"
  else
    echo "STOP: the sandbox recipe differs (see above). Don't open it yet."
  fi
}

# Inside the clean clone: fetch the agent's work and show what changed
agent-review() {
  local b="${1:-main}"
  git fetch origin && git fetch sandbox || return
  echo "== Commits =="
  git --no-pager log --oneline "origin/main..sandbox/$b"
  echo "== Sensitive files touched (check these closely) =="
  git --no-pager diff --stat "origin/main...sandbox/$b" -- \
    .github .devcontainer .vscode .claude .githooks Makefile AGENTS.md CLAUDE.md _docs/agent-kit
  echo "== Full diff (q to quit) =="
  git diff "origin/main...sandbox/$b"
}

# Inside a clean clone: add the recipe and CI workflow from your template repo
dc-init() {
  local t=~/projects/devcontainer-test
  cp -r "$t/.devcontainer" . && mkdir -p .github/workflows || return
  [ -e .github/workflows/verify.yml ] || cp "$t/.github/workflows/verify.yml" .github/workflows/
  echo "Recipe and CI workflow added: review, commit and push them"
}
