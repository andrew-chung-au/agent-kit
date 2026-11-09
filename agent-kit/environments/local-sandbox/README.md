# Local sandbox: setup and reference

One-time setup and reference for the local sandbox profile. Reader: the human, on their own machine. The profiles and the rules for the sandbox are in `environments.md`; the numbered install and upgrade steps are in `install-and-upgrade.md`. The files described here sit beside this page.

## Bootstrap script and recipe files

`install-and-upgrade.md` (situations 1 to 3) gives the full numbered steps around it, including pushing an existing repo first and moving the old folder aside. One script does the local part of the setup for you. Run it on your machine from a plain folder (one that is not inside any git work tree, for example `~/projects`), using a clean clone of the kit:

```
cd ~/projects
bash ~/projects/agent-kit/agent-kit/scripts/bootstrap-project.sh https://github.com/<you>/<your-repo>.git
```

It creates `<repo>` and `<repo>-sandbox` side by side in that folder, adds the `sandbox` remote, installs the push check to `~/.agent-hooks/pre-push` and the clean clone's `.git/hooks/pre-push` (unsetting `core.hooksPath` first if it is set), and copies the kit to `_docs/agent-kit/`, `devcontainer.json` and `setup.sh` to `.devcontainer/`, and the CI template to `.github/workflows/verify.yml`. A sandbox is an ordinary clone with no marker of its own, so the script refuses to run anywhere inside a git work tree, which covers every sandbox and clean clone. It also refuses a kit that is not a git clone, has uncommitted changes, or whose `HEAD` is on no reviewed remote branch, so neither an agent's unsaved edits nor its committed but unpushed sandbox commits are copied. Branches of the `sandbox` remote never count, because `git fetch sandbox` is the review flow and brings unreviewed agent commits into the clean clone; nor does any remote whose URL is a local working clone (a folder with a `.git` inside), whatever its name. The check reads the refs from your last fetch: if your own clean clone is refused, check out the reviewed commit (for example `origin/main`), or run `git fetch` in it and retry. It can't tell a pushed but unreviewed commit from a reviewed one; your review before pushing is that gate. Only the kit's git-tracked files are copied, so an ignored file in the kit clone (a stray `.env`, caches) never lands in the project. A non-git folder that already has the clean or sandbox name is refused before anything is cloned. It prints each file it writes and stops at local files: it never pushes, and it leaves the git identity in `setup.sh` as a placeholder for you to fill in. A re-run changes nothing, and files you edited since (the identity in `setup.sh`, the CI placeholders, the copied kit) are kept, with a `kept` line and a diff hint; `--force` replaces them. The push check is always brought back in step with the kit. It is not a make target: at bootstrap time there is no Makefile, and `make` in a clean clone is forbidden. The rest of this section is what it does and why; to set a repo up by hand, do these steps yourself, always from a clean clone.

The kit supplies reference copies of its files in `environments/local-sandbox/`:

| File | Installed as | Notes |
|---|---|---|
| `pre-push` | `~/.agent-hooks/pre-push`, copied into each clean clone's `.git/hooks/pre-push` | The push check. Monorepo-aware: it finds every project the new commits change, using git only, then runs `make -C <project> install verify` for each in a throwaway container. The container sees only a bundle of the pushed commits: no ignored files, git settings or other branches. It blocks the push if a project's `agent-kit.conf` was removed. Never run it from the repo. |
| `devcontainer.json`, `setup.sh` | `.devcontainer/` at the repo root | The container recipe for Python plus frontend projects: installs Node and uv at pinned versions, names the container after its folder, and `setup.sh` refuses to run in a clean clone. Fill in your name and noreply email in `setup.sh`. |
| `templates/ci-verify.yml.template` | `.github/workflows/` at the repo root | CI with `permissions: contents: read` and no secrets |

The recipe's Node, nvm, uv and OpenCode versions are pins nobody has verified against the release pages yet (Node `24.22.0`, nvm `0.40.8`, uv `0.13.6`, OpenCode `2.2.5`, and the setup actions in the CI template). Keep uv at 0.13.4 or later: earlier versions bundle a TLS root that was withdrawn (GHSA-hq85-5cpj-mr62). OpenCode is pinned to the `2.x` version this project's sessions use. It installs from the v2 endpoint (`https://opencode.ai/v2/install`, which takes `--version`); the v1 installer at `https://opencode.ai/install` refuses 2.x. The OpenCode pin stays unverified until the first rebuild reports `opencode v2.2.5`. To bump any of these pins, edit the value in `setup.sh` next to the others (OpenCode in `opencode_version`); the recipe re-installs only when the running version differs. Your first rebuild creates `.devcontainer/devcontainer-lock.json` with an entry for the Node feature; you commit that file in the project. An agent never writes it. A project with no frontend deletes the Node feature and the Node lines in `setup.sh`.

## Setting up by hand (without the script)

The bootstrap script does all of this; use these steps only if you cannot run it. Put the kit in the project first (situation 7 of `install-and-upgrade.md`, steps 1 to 4). Then, from the clean clone:

1. Copy `environments/local-sandbox/devcontainer.json` and `setup.sh` to the project's `.devcontainer/`, and `templates/ci-verify.yml.template` to `.github/workflows/verify.yml`. Put your git name and noreply email in `setup.sh`.
2. Open only the project's `<repo>-sandbox` folder in the container. `setup.sh` runs `make hooks` on the first build. Commit the `.devcontainer/devcontainer-lock.json` that the first rebuild creates.
3. Copy `environments/local-sandbox/pre-push` to `~/.agent-hooks/pre-push` and into each clean clone's `.git/hooks/pre-push`, and make it executable. This is the push check; it needs git, Docker and coreutils on your machine.
4. If the project's `make install` needs Node or uv, build the image from `environments/local-sandbox/push-check.Dockerfile` and set `AGENT_PUSH_CHECK_IMAGE` to it; otherwise the push check uses `python:3.12`. Dry-run it with `AGENT_PUSH_CHECK_PLAN=1 git push`.
5. If the project's checks need a database, use the files in `environments/local-sandbox/compose/`: copy its three files into `.devcontainer/`, next to the standard `setup.sh`.

## The sandbox token

As the human stated it from the token settings (2026-11-02): repository permissions are read access to code and metadata, and read and write access to issues; no user permissions. Whether the token is scoped to a single repository is not verified; scope it to one repository. Git credentials come from a credential helper rather than the remote URL. You set the token in your GitHub account's token settings; agents never print or read it.

**Limit:** with issues write, the token can also edit or close issues and add labels, including `approved`. The `AGENTS.md` rule that agents never add that label is a text rule the token does not enforce. So OpenCode's `gh issue edit*`, `gh issue close*` and `gh api*` stay at ask, and a scanned `make` target is the structured way to write issues.

With no Docker, the sandbox can't run the push check end to end; it runs on your machine.

## The push-check image

The push check runs `make install verify` in a throwaway container. Its image comes from `AGENT_PUSH_CHECK_IMAGE` in the shell you push from, and defaults to `python:3.12`, which has git and make but no Node and no uv. A project whose `make install` runs `npm ci` or `uv sync` fails there with exit 127 before `verify` runs.

`environments/local-sandbox/push-check.Dockerfile` is a reference image with Node and uv at the same pins as the dev container recipe (all unverified until you build it). Build it on your machine from the clean clone's copy, never from a sandbox, with no build context, then point the push check at it:

```
docker build -t agent-push-check:node24-uv0.13.6 - < agent-kit/environments/local-sandbox/push-check.Dockerfile
export AGENT_PUSH_CHECK_IMAGE=agent-push-check:node24-uv0.13.6
AGENT_PUSH_CHECK_PLAN=1 git push
```

With `AGENT_PUSH_CHECK_PLAN=1` the push check prints what it would check, runs nothing and lets the push go on, so run the dry run first and push for real without it. The variable is per shell, so one image serves every project you push from that shell; a monorepo with different stacks needs one image that holds all of them. A project that needs more (Terraform, `pip-audit`, `libpq-dev`) adds it to its own copy of the Dockerfile. The image holds no credentials and no project files. `pre-push` is unchanged: the image is your choice, on your side, and nothing in a pushed commit can pick it. Services such as a database are not available in the push check: the throwaway container has none.

## The Compose variant (an app plus a database)

Use `environments/local-sandbox/compose/` when the project's checks need a database. Copy its `devcontainer.json`, `compose.yaml` and `Dockerfile` into `.devcontainer/` from a clean clone, next to the standard `setup.sh`, and replace the placeholders for the sandbox folder, database name, user and password. The agent reaches the Postgres service `db` by name and cannot control Docker: the recipe has no Docker socket and no privileged mode, ever, and the database is not published to the host. The data volume persists on the host until you remove it; you run `docker compose` from the host, after reading the files, never the agent. The Postgres tag and the Compose behaviour are unverified until your first rebuild (the steps are in `_human-tasks/`).

In the push check, the throwaway container has no `db`. Tests that need the database must skip when `DATABASE_URL` is unset, or run in CI against a Postgres service. The trade-off: a skipped test proves nothing locally.

## Reopening fails with a `vscode-wayland` mount error (WSL 2 + Docker Desktop)

`docker start` fails before any build with `error mounting ... /tmp/vscode-wayland-<id>.sock ... no such file or directory`. Dev Containers baked a mount of the Wayland socket into the container, and that socket no longer exists (WSLg isn't running, or WSL restarted), so every reopen fails. This is VS Code and Docker Desktop behaviour, not a recipe defect, so the recipe is unchanged. Check, then fix, in the WSL shell:

  ```
  ls -l /run/user/$(id -u)/wayland-0              # "No such file or directory" confirms it
  unset WAYLAND_DISPLAY && code --quit
  docker ps -a --filter label=devcontainer.local_folder --format '{{.ID}}  {{.Label "devcontainer.local_folder"}}'
  docker rm -f <ID>                               # the ID whose folder ends in <repo>-sandbox
  ```

  Docker names the container itself, so find it by the folder label rather than by name. Remove only the dev container, not a Compose service such as `db`. Nothing of yours is lost: the repo is a bind mount and the named volumes (the Claude login, and a Compose project's database volume) are separate and unaffected. Only tool installs inside the container go, and `setup.sh` reinstalls them when you reopen the sandbox. To stop it recurring, add `unset WAYLAND_DISPLAY` to `~/.bashrc`, or turn off `Dev > Containers: Mount Wayland Socket` where your VS Code version offers it; undo by removing the line or turning the setting back on. First reported 2026-11-05 (Docker Desktop 29.8.2, Dev Containers 0.469.0).

## Comparing the installed push check (human only)

The push check is installed on your machine, outside the sandbox: once at `~/.agent-hooks/pre-push`, and once in each clean clone's `.git/hooks/pre-push`. These are the two `human-machine` rows in `installed-files.txt`, whose source is `environments/local-sandbox/pre-push`. A sandbox tool never opens a `human-machine` install path, so `make kit-check` lists these two as "not checked here" and a sandbox check can never prove the installed push check is current. Only you can compare them, from the clean clone.

Do it with git and coreutils only, never `make`, and never by running or sourcing a repo file (the kit folder is untrusted until you have read its diff). The recipe runs in one clone at a time: repeat it in each clean clone, because `.git/hooks/pre-push` belongs to that clone while `~/.agent-hooks/pre-push` is shared. From the clean clone, with `<ref>` the reviewed commit:

```
p=~/.agent-hooks/pre-push; if test -h "$p"; then echo "symlink: $p, resolve it by hand"; elif test -f "$p"; then git show <ref>:agent-kit/environments/local-sandbox/pre-push | git diff --no-index -- - "$p"; else echo "missing: $p"; fi
p=.git/hooks/pre-push; if test -h "$p"; then echo "symlink: $p, resolve it by hand"; elif test -f "$p"; then git show <ref>:agent-kit/environments/local-sandbox/pre-push | git diff --no-index -- - "$p"; else echo "missing: $p"; fi
```

Each line checks one install path and stops at the first answer. A symlink is tested first and reported, never followed (`cmp` follows symlinks, so it is not an alternative). A missing path, or one that is not a regular file, prints `missing:` and nothing is compared. A match prints nothing and exits 0. A mismatch prints the diff and exits 1. The kit text goes to `git diff --no-index` on standard input, so no temp file is written and nothing is written to an install path. Reinstall by copying from the clean clone, as above; never from the container's `.scratch/` copy. The install paths here come from the map's rows, so they are not hard-coded in a second place.
