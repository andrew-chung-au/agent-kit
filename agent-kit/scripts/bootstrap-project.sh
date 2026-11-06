#!/usr/bin/env bash
# Set up a repository for the local sandbox profile in one command (issue #150).
#
# The human runs this on their own machine, from a plain folder (one that is not
# inside any git work tree, for example ~/projects), using a clean clone of the kit:
#
#   cd ~/projects
#   bash ~/projects/agent-kit/agent-kit/scripts/bootstrap-project.sh <github-url> [--kit <kit folder>] [--force]
#
# --kit defaults to the kit this script sits in. It:
#
#   - creates <repo> (a clean clone) and <repo>-sandbox in the current folder if
#     absent, and adds the 'sandbox' remote on the clean clone as a file:// path;
#   - installs the push check (environments/local-sandbox/pre-push) to
#     ~/.agent-hooks/pre-push and into the clean clone's .git/hooks/pre-push, and
#     unsets core.hooksPath in the clean clone if it is set;
#   - copies the kit to <repo>/_docs/agent-kit/, devcontainer.json and setup.sh to
#     <repo>/.devcontainer/, and the CI template to <repo>/.github/workflows/verify.yml;
#   - refuses to run inside a git work tree (a sandbox is one), and refuses a kit
#     that is not a git clone, has uncommitted changes under its folder, or whose
#     HEAD is on no reviewed remote branch (unpushed, or only on the 'sandbox'
#     remote or another local working clone, so unreviewed);
#   - refuses up front a non-git folder already holding the clean or sandbox name;
#   - copies only the kit's git-tracked files, so ignored files never ride along;
#   - prints each file it writes and the next step, and changes nothing else.
#
# Re-running changes nothing. Files you edit after the first run (the git identity
# in setup.sh, the CI placeholders, the copied kit) are kept, never overwritten,
# unless --force is given. The push check is the exception: it is always brought
# back in step with the kit, because it must match it exactly.
#
# Not a make target: at bootstrap time there is no Makefile, and `make` in a clean
# clone is forbidden (environments.md). Stops at local files; the human reviews and
# pushes. git and coreutils only; the only network use is `git clone`.
set -euo pipefail

prog="$(basename "$0")"
usage() {
  echo "usage: $prog <github-url> [--kit <kit folder>] [--force]" >&2
  echo "  Run from a plain folder (not inside a git work tree), using a clean clone of the kit." >&2
  exit 2
}
die() { echo "$prog: $*" >&2; exit 1; }

kit="$(cd "$(dirname "$0")/.." && pwd)"
url=""
force=0
resolve_kit() { kit="$(cd "$1" 2>/dev/null && pwd || true)"; [ -n "$kit" ] || die "--kit path does not exist: $1"; }
while [ "$#" -gt 0 ]; do
  case "$1" in
    --kit) [ "$#" -ge 2 ] || usage; resolve_kit "$2"; shift 2 ;;
    --kit=*) resolve_kit "${1#--kit=}"; shift ;;
    --force) force=1; shift ;;
    -h|--help) usage ;;
    -*) echo "$prog: unknown option: $1" >&2; usage ;;
    *) [ -z "$url" ] || usage; url="$1"; shift ;;
  esac
done
[ -n "$url" ] || usage

# 1. Where it runs. A sandbox is an ordinary clone with no marker of its own, so
# the test is the one thing every sandbox shares: it is a git work tree. A plain
# folder such as ~/projects passes; any clone, sandbox or clean, is refused (that
# also stops a clone being nested inside another).
if git -C "$PWD" rev-parse --git-dir >/dev/null 2>&1; then
  die "the current folder is inside a git work tree (a sandbox is one).
  Run it from a plain folder instead, for example: cd ~/projects"
fi

# 2. Where it copies from. The kit must be a git work tree with nothing
# uncommitted under its folder, so an agent's unsaved edits are never copied.
# The clean-clone marks (a 'sandbox' remote, the push check) are NOT a reason to
# refuse: the human's own clean clone of the kit has them, and is the right source.
[ -d "$kit/scripts" ] && [ -f "$kit/environments/local-sandbox/pre-push" ] ||
  die "kit path '$kit' is not an agent kit (no scripts/ and environments/local-sandbox/pre-push)."
git -C "$kit" rev-parse --git-dir >/dev/null 2>&1 ||
  die "kit path '$kit' is not a git clone. Use a clean clone of the kit (git clone), not a copy or an unpacked zip."
dirty="$(git -C "$kit" status --porcelain --untracked-files=all -- . 2>/dev/null || true)"
if [ -n "$dirty" ]; then
  die "kit path '$kit' has uncommitted changes, so it is not a clean clone:
$(printf '%s\n' "$dirty" | head -n 5 | sed 's/^/    /')
  Copy the kit only from a clean clone, never a sandbox. See environments.md."
fi
# Committed is not enough: an agent's sandbox commits are committed too. The kit's
# HEAD must be on a branch of a reviewed remote, which in a clean clone means it
# came from (or was pushed to) GitHub after the human's review.
#
# A clean clone normally has a 'sandbox' remote, and `git fetch sandbox` is the
# review flow, so sandbox/* refs carry unreviewed agent commits and never count.
# Neither does any remote whose URL is a local working clone (a folder with a .git
# inside), whatever it is named: that is someone's sandbox, not a review gate. The
# test is a file test only, so git never runs in that folder (environments.md).
#
# This reads the remote-tracking refs from the last fetch, so a stale clone fails
# safe: fetch and retry.
is_working_clone_url() {
  local u="$1"
  case "$u" in file://*) u="${u#file://}" ;; /*|./*|../*) ;; *) return 1 ;; esac
  [ -e "$u/.git" ]
}
reviewed_remotes=()
while IFS= read -r r; do
  [ -n "$r" ] && [ "$r" != "sandbox" ] || continue
  is_working_clone_url "$(git -C "$kit" remote get-url "$r" 2>/dev/null || true)" && continue
  reviewed_remotes+=("refs/remotes/$r")
done < <(git -C "$kit" remote 2>/dev/null)
on_reviewed=""
if [ "${#reviewed_remotes[@]}" -gt 0 ]; then
  on_reviewed="$(git -C "$kit" for-each-ref --contains HEAD --format='%(refname)' "${reviewed_remotes[@]}" 2>/dev/null |
    grep -v '/HEAD$' || true)"
fi
if [ -z "$on_reviewed" ]; then
  die "kit path '$kit' is at a commit that is on no reviewed remote branch: it is unpushed,
  or only on the 'sandbox' remote or another local working clone (unreviewed agent work).
  Copy the kit only from a clean clone of a reviewed, pushed commit (for example: git checkout origin/main).
  If this is your clean clone and the commit is pushed, run 'git -C \"$kit\" fetch' and retry."
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
clean="$PWD/$name"
sandbox="$PWD/$name-sandbox"
# Before cloning anything: an existing folder with either name must be a clone.
for dir in "$clean" "$sandbox"; do
  if [ -e "$dir" ] && [ ! -d "$dir/.git" ]; then
    die "'$dir' exists but is not a git clone. Move it aside or pick another folder, then re-run.
  Nothing was changed."
  fi
done

wrote=0
note() { echo "  wrote $1"; wrote=$((wrote + 1)); }
skip() { echo "  ok    $1"; }
kept() { echo "  kept  $1 (differs from the kit; yours is left alone. Compare: diff -ru '$2' '$1'. Replace with --force)"; }

# install_file SRC DST: copy only when missing; keep a differing file unless --force.
install_file() {
  local src="$1" dst="$2"
  if [ ! -e "$dst" ]; then
    cp "$src" "$dst"; note "$dst"
  elif cmp -s "$src" "$dst"; then
    skip "$dst is up to date"
  elif [ "$force" -eq 1 ]; then
    cp "$src" "$dst"; note "$dst (replaced, --force)"
  else
    kept "$dst" "$src"
  fi
}

echo "Bootstrapping '$name' for the local sandbox profile (kit: $kit)"

# 3. The two clones, side by side in the current folder.
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

# 4. The 'sandbox' remote on the clean clone, pointing at the sandbox clone.
if git -C "$clean" remote get-url sandbox >/dev/null 2>&1; then
  skip "clean clone already has a 'sandbox' remote"
else
  git -C "$clean" remote add sandbox "file://$sandbox"
  echo "  added 'sandbox' remote on the clean clone -> file://$sandbox"
fi

# 5. The push check: ~/.agent-hooks/pre-push, then the clean clone's hook. These
# must equal the kit's copy exactly, so a differing one is updated, not kept.
hooks_dir="$HOME/.agent-hooks"
mkdir -p "$hooks_dir"
for dst in "$hooks_dir/pre-push" "$clean/.git/hooks/pre-push"; do
  if [ -f "$dst" ] && cmp -s "$pre_push_src" "$dst"; then
    skip "$dst is up to date"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$pre_push_src" "$dst"
    chmod +x "$dst"
    note "$dst"
  fi
done
# core.hooksPath would switch off .git/hooks/pre-push, so the push check would never run.
if git -C "$clean" config --local --get core.hooksPath >/dev/null 2>&1; then
  git -C "$clean" config --local --unset core.hooksPath
  echo "  unset core.hooksPath on the clean clone (it would disable the push check)"
fi

# 6. The kit, at _docs/agent-kit/ (never beside it). Only git-tracked files are
# copied, so an ignored file in the kit clone (a stray .env, __pycache__) never
# lands in the project. An existing copy is kept if it differs, because the human
# may have merged a newer kit into it; --force replaces it.
kit_dest="$clean/_docs/agent-kit"
# copy_kit DEST: the kit's tracked files, with modes and symlinks as they are.
copy_kit() {
  local f
  mkdir -p "$1"
  # Portable flags only (no GNU cp --parents), so it also runs on macOS.
  while IFS= read -r -d '' f; do
    mkdir -p "$1/$(dirname "$f")"
    cp -P -p "$kit/$f" "$1/$f"
  done < <(git -C "$kit" ls-files -z -- .)
}
# kit_matches: DEST holds exactly the tracked files, each byte for byte.
kit_matches() {
  local f n=0
  while IFS= read -r -d '' f; do
    cmp -s "$kit/$f" "$kit_dest/$f" || return 1
    n=$((n + 1))
  done < <(git -C "$kit" ls-files -z -- .)
  # Count by NUL terminators (no GNU find -printf), so names with newlines count once.
  local found
  found="$(find "$kit_dest" \( -type f -o -type l \) -print0 | tr -dc '\000' | wc -c)"
  [ "$((found))" -eq "$n" ]
}
mkdir -p "$clean/_docs"
if [ ! -e "$kit_dest" ]; then
  copy_kit "$kit_dest"
  note "$kit_dest/ (the kit)"
elif kit_matches; then
  skip "$kit_dest matches the kit"
elif [ "$force" -eq 1 ]; then
  rm -rf "$kit_dest"
  copy_kit "$kit_dest"
  note "$kit_dest/ (replaced, --force)"
else
  kept "$kit_dest" "$kit"
fi

# 7. The dev container recipe and the CI workflow.
mkdir -p "$clean/.devcontainer" "$clean/.github/workflows"
install_file "$recipe/devcontainer.json" "$clean/.devcontainer/devcontainer.json"
install_file "$recipe/setup.sh" "$clean/.devcontainer/setup.sh"
install_file "$ci_src" "$clean/.github/workflows/verify.yml"

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
Re-running this script keeps the files you edit. See _docs/agent-kit/environments.md.
EOF
