#!/usr/bin/env bash
# Set up a repository for the local sandbox profile in one command (issue #150).
#
# The human runs this from a clean clone, never a sandbox:
#
#   bash <kit>/scripts/bootstrap-project.sh <github-url> [--kit <clean kit clone>]
#
# <kit> is a clean clone of the agent kit (the folder that holds this script's
# parent, scripts/). <github-url> is the project to set up. It:
#
#   - creates <repo> (a clean clone) and <repo>-sandbox beside it if absent, and
#     adds the 'sandbox' remote on the clean clone as a file:// path to the
#     sandbox clone;
#   - installs the push check (environments/local-sandbox/pre-push) to
#     ~/.agent-hooks/pre-push and into the clean clone's .git/hooks/pre-push,
#     and unsets core.hooksPath in the clean clone if it is set;
#   - copies the kit to <repo>/_docs/agent-kit/, devcontainer.json and setup.sh
#     to <repo>/.devcontainer/, and the CI template to
#     <repo>/.github/workflows/verify.yml;
#   - refuses to run from inside a sandbox, and refuses a kit path that is one
#     (the same two signals as setup.sh and install-hooks.sh);
#   - prints each file it writes and the next step, and changes nothing else.
#
# Re-running it on a set-up machine changes nothing (idempotent). It is not a
# make target: at bootstrap time there is no Makefile, and `make` in a clean
# clone is forbidden (environments.md). It stops at local files; the human
# fills in the git identity in setup.sh, reviews, and pushes. git and coreutils
# only; nothing is installed and nothing touches the network except `git clone`.
set -euo pipefail

prog="$(basename "$0")"
usage() {
  echo "usage: $prog <github-url> [--kit <clean kit clone>]" >&2
  echo "  Run from a clean clone, never a sandbox. See environments.md." >&2
  exit 2
}
die() { echo "$prog: $*" >&2; exit 1; }

# The kit holding this script: scripts/ is one level below the kit root.
kit="$(cd "$(dirname "$0")/.." && pwd)"

url=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --kit) [ "$#" -ge 2 ] || usage; kit="$(cd "$2" 2>/dev/null && pwd || true)"; [ -n "$kit" ] || die "--kit path does not exist"; shift 2 ;;
    --kit=*) kit="$(cd "${1#--kit=}" 2>/dev/null && pwd || true)"; [ -n "$kit" ] || die "--kit path does not exist"; shift ;;
    -h|--help) usage ;;
    -*) echo "$prog: unknown option: $1" >&2; usage ;;
    *) [ -z "$url" ] || usage; url="$1"; shift ;;
  esac
done
[ -n "$url" ] || usage

# is_sandbox DIR: the two signals setup.sh and install-hooks.sh use for a clean
# clone, read the other way round here. A folder is a sandbox (or any working
# tree an agent commits in) when it has a 'sandbox' remote, or the clean-clone
# push check in its .git/hooks/pre-push. Git and coreutils only; no repo there
# means neither signal is present.
is_sandbox() {
  local dir="$1" common
  common="$(git -C "$dir" rev-parse --git-common-dir 2>/dev/null || true)"
  [ -n "$common" ] || return 1
  case "$common" in /*) ;; *) common="$dir/$common" ;; esac
  git -C "$dir" remote get-url sandbox >/dev/null 2>&1 && return 0
  grep -qs '^# agent-kit-push-check' "$common/hooks/pre-push" && return 0
  return 1
}

# Refuse the two places that must never be a sandbox: the folder the human ran
# this from, and the kit it copies out of. Copying from a sandbox would carry an
# agent's changes into a fresh project.
if is_sandbox "$PWD"; then
  die "this looks like a sandbox (it has a 'sandbox' remote or the clean-clone push check).
  Run it from a clean clone instead. See environments.md."
fi
[ -d "$kit/scripts" ] && [ -f "$kit/environments/local-sandbox/pre-push" ] ||
  die "kit path '$kit' is not an agent kit (no scripts/ and environments/local-sandbox/pre-push).
  Pass a clean clone of the kit with --kit <path>."
if is_sandbox "$kit"; then
  die "kit path '$kit' looks like a sandbox (it has a 'sandbox' remote or the clean-clone push check).
  Copy the kit only from a clean clone, never a sandbox. See environments.md."
fi

recipe="$kit/environments/local-sandbox"
pre_push_src="$recipe/pre-push"
ci_src="$kit/templates/ci-verify.yml.template"
[ -f "$ci_src" ] || die "CI template missing: $ci_src"
for f in devcontainer.json setup.sh; do
  [ -f "$recipe/$f" ] || die "recipe file missing: $recipe/$f"
done

name="$(basename "$url")"; name="${name%.git}"
[ -n "$name" ] && [ "$name" != "/" ] || die "cannot derive a repo name from '$url'"
# The two clones are created under the folder the script is run from, as
# siblings: <cwd>/<repo> (the clean clone) and <cwd>/<repo>-sandbox.
clean="$PWD/$name"
sandbox="$PWD/$name-sandbox"

wrote=0
note() { echo "  wrote $1"; wrote=$((wrote + 1)); }
skip() { echo "  ok    $1"; }

echo "Bootstrapping '$name' for the local sandbox profile (kit: $kit)"

# 1. The two clones, created under the folder this was run from.
if [ -d "$clean" ]; then
  skip "clean clone exists: $clean"
else
  git clone "$url" "$clean"
  echo "  cloned clean clone: $clean"
fi
if [ -d "$sandbox" ]; then
  skip "sandbox clone exists: $sandbox"
else
  git clone "$url" "$sandbox"
  echo "  cloned sandbox clone: $sandbox"
fi

# 2. The 'sandbox' remote on the clean clone, pointing at the sandbox clone.
if git -C "$clean" remote get-url sandbox >/dev/null 2>&1; then
  skip "clean clone already has a 'sandbox' remote"
else
  git -C "$clean" remote add sandbox "file://$sandbox"
  echo "  added 'sandbox' remote on the clean clone -> file://$sandbox"
fi

# 3. The push check: ~/.agent-hooks/pre-push, then the clean clone's hook.
hooks_dir="$HOME/.agent-hooks"
installed_hook="$hooks_dir/pre-push"
mkdir -p "$hooks_dir"
if [ -f "$installed_hook" ] && cmp -s "$pre_push_src" "$installed_hook"; then
  skip "$installed_hook is up to date"
else
  cp "$pre_push_src" "$installed_hook"
  chmod +x "$installed_hook"
  note "$installed_hook"
fi

# core.hooksPath would switch off .git/hooks/pre-push, so the push check would
# never run. Unset it on the clean clone before installing the hook.
if git -C "$clean" config --local --get core.hooksPath >/dev/null 2>&1; then
  git -C "$clean" config --local --unset core.hooksPath
  echo "  unset core.hooksPath on the clean clone (it would disable the push check)"
fi
clean_hook="$clean/.git/hooks/pre-push"
if [ -f "$clean_hook" ] && cmp -s "$pre_push_src" "$clean_hook"; then
  skip "$clean_hook is up to date"
else
  cp "$pre_push_src" "$clean_hook"
  chmod +x "$clean_hook"
  note "$clean_hook"
fi

# 4. The kit, at _docs/agent-kit/ (never beside it). Copy fresh each run so the
#    files match the kit this script came from; nothing else under _docs/ moves.
kit_dest="$clean/_docs/agent-kit"
mkdir -p "$clean/_docs"
if [ -d "$kit_dest" ] && diff -rq "$kit" "$kit_dest" >/dev/null 2>&1; then
  skip "$kit_dest matches the kit"
else
  rm -rf "$kit_dest"
  cp -a "$kit" "$kit_dest"
  note "$kit_dest/ (the kit)"
fi

# 5. The dev container recipe at .devcontainer/, and CI at .github/workflows/.
mkdir -p "$clean/.devcontainer" "$clean/.github/workflows"
for f in devcontainer.json setup.sh; do
  dst="$clean/.devcontainer/$f"
  if [ -f "$dst" ] && cmp -s "$recipe/$f" "$dst"; then
    skip ".devcontainer/$f is up to date"
  else
    cp "$recipe/$f" "$dst"
    note ".devcontainer/$f"
  fi
done
ci_dst="$clean/.github/workflows/verify.yml"
if [ -f "$ci_dst" ] && cmp -s "$ci_src" "$ci_dst"; then
  skip ".github/workflows/verify.yml is up to date"
else
  cp "$ci_src" "$ci_dst"
  note ".github/workflows/verify.yml (fill in its standalone placeholders)"
fi

echo
if [ "$wrote" -eq 0 ]; then
  echo "Nothing changed: '$name' is already set up."
else
  echo "Wrote $wrote item(s). Nothing was pushed and nothing else changed."
fi
cat <<EOF

Next, from the clean clone ($clean):
  1. Fill in your git name and noreply email in .devcontainer/setup.sh.
  2. Edit .github/workflows/verify.yml: for a standalone repo, delete the two
     'paths:' filters and set working-directory to "." (see the file's header).
  3. In your tool, run: "Set up this project using _docs/agent-kit/setup.md."
  4. Review the diff, commit and push from this clean clone. Never run 'make'
     here. Open only the '$name-sandbox' folder in the container.
See _docs/agent-kit/environments.md for the whole picture.
EOF
