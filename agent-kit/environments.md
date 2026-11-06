# Environments

The kit's rules are the same wherever agents run. What changes is:
- where the agent works;
- where the kit's git hooks are active;
- where you review and push;
- what checks a push before it reaches GitHub.

There are two separate choices:
- **Which agent tool:** the core kit works with any tool that reads `AGENTS.md`. A tool layer adds that tool's own enforcement: `claude-code/` or `opencode/`.
- **Where it runs:** one of the three profiles below. Record it in the **Environment** setting in `AGENTS.md`, so agents know what's available to them.

| | Codespaces | Local sandbox | Local, no sandbox |
|---|---|---|---|
| Agent works in | The codespace | A dev container, in the `<repo>-sandbox` folder | Your own checkout |
| You review and push from | The same codespace | A separate clean clone, `<repo>` | The same checkout |
| Kit's git hooks (`make hooks`) | In the codespace | In the container only | In the checkout |
| What checks a push | The kit's pre-push hook, then CI | Your push check (`environments/local-sandbox/pre-push`) in a throwaway container, then CI | The kit's pre-push hook, then CI |
| Can the agent push? | Yes: the codespace's GitHub token can. Only the rules and hooks stop it | No: its token has read-only code access | Yes: it can use your login |
| Docker | Available | Not available | Available |
| Best for | Projects that need Docker (Compose stacks, databases) | Everything else | Quick experiments only |

## Codespaces

This is the kit as the README describes it. Run `make hooks` once per codespace. The kit's pre-push hook runs `make verify` before you push, and the optional CI workflow runs it again on GitHub.

The codespace's own token can push to the repo, so nothing technical stops an agent pushing; the rules and the Claude Code layer's git guard ask it not to. Your review before pushing is the real control. Codespaces stop after a period of inactivity, even while an agent is working.

## Local sandbox

The agent works in a dev container with a GitHub token that can't push, in its own clone of the repo. You review its commits from a second, clean clone that is never opened in the container, and push from there. The guide that sets this up lives outside the kit.

One script does the local part of the setup for you. Run it on your machine from a plain folder (one that is not inside any git work tree, for example `~/projects`), using a clean clone of the kit:

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

**Copy these files only from a clean clone, never from a sandbox.** An agent can change anything in its sandbox, including the kit.

### The sandbox token

As the human stated it from the token settings (2026-11-02): repository permissions are read access to code and metadata, and read and write access to issues; no user permissions. Whether the token is scoped to a single repository is not verified; scope it to one repository. Git credentials come from a credential helper rather than the remote URL. You set the token in your GitHub account's token settings; agents never print or read it.

**Limit:** with issues write, the token can also edit or close issues and add labels, including `approved`. The `AGENTS.md` rule that agents never add that label is a text rule the token does not enforce. So OpenCode's `gh issue edit*`, `gh issue close*` and `gh api*` stay at ask, and a scanned `make` target is the structured way to write issues.

With no Docker, the sandbox can't run the push check end to end; it runs on your machine.

### The push-check image

The push check runs `make install verify` in a throwaway container. Its image comes from `AGENT_PUSH_CHECK_IMAGE` in the shell you push from, and defaults to `python:3.12`, which has git and make but no Node and no uv. A project whose `make install` runs `npm ci` or `uv sync` fails there with exit 127 before `verify` runs.

`environments/local-sandbox/push-check.Dockerfile` is a reference image with Node and uv at the same pins as the dev container recipe (all unverified until you build it). Build it on your machine from the clean clone's copy, never from a sandbox, with no build context, then point the push check at it:

```
docker build -t agent-push-check:node24-uv0.13.6 - < agent-kit/environments/local-sandbox/push-check.Dockerfile
export AGENT_PUSH_CHECK_IMAGE=agent-push-check:node24-uv0.13.6
AGENT_PUSH_CHECK_PLAN=1 git push
```

With `AGENT_PUSH_CHECK_PLAN=1` the push check prints what it would check, runs nothing and lets the push go on, so run the dry run first and push for real without it. The variable is per shell, so one image serves every project you push from that shell; a monorepo with different stacks needs one image that holds all of them. A project that needs more (Terraform, `pip-audit`, `libpq-dev`) adds it to its own copy of the Dockerfile. The image holds no credentials and no project files. `pre-push` is unchanged: the image is your choice, on your side, and nothing in a pushed commit can pick it. Services such as a database are not available in the push check: the throwaway container has none.

### Rules for the local sandbox

- **Never run `make` in a clean clone.** That includes `make hooks`, `make verify` and `make test`. The Makefile is repo code that an agent may have changed, and in a clean clone it would run on your machine with your login. `make hooks` refuses in a clean clone (it spots the `sandbox` remote or the push check), but that's only a convenience: by the time it refuses, `make` has already run.
- **Never open a clean clone in a container.** A container gets write access to the folder it opens, including its `.git/hooks/pre-push`, which is your push check. Its `setup.sh` and `make hooks` would also run against the clean clone, so repo code runs against the clean clone. Open only the `<repo>-sandbox` folder in the container.
- **Run `make hooks` in the container only.** `setup.sh` does it on the first build. Run it again in the container after a kit upgrade.
- **The kit's pre-push hook never fires here.** The agent can't push, and the clean clone doesn't use the kit's hooks. Your push check and CI do that job.
- **Protected changes are committed in the container,** with `HUMAN_APPROVED=1`, after your approval. Never commit in the sandbox folder from Ubuntu.
- **The kit's pre-commit hook asks for approval on repo-root `.github/` and `.devcontainer/` changes**, as well as `.githooks/`. An agent can set `HUMAN_APPROVED=1` itself, so your review of the diff is still the real check.
- **Pushing:** instead of the README's "read the diff, then push", fetch the sandbox's commits into the clean clone, read the full diff, merge and push from there. The push check runs automatically. The commands, step by step, are in `_human-tasks/2026-11-02T1220Z-human-task-engineer-push-review-from-clean-clone.md`; this file keeps the reasons.
- **The push check is a quality gate, not a security gate.** Whoever controls a project's Makefile controls what `verify` does, so an agent could make it pass. It proves the tests pass; your review of the diff is what proves the change is safe.
- **From Ubuntu, touch the sandbox folder only with `git fetch sandbox`, run from the clean clone.** The sandbox folder is shared with the container, so the agent can change files there without committing them:
  - `.devcontainer/`: an `initializeCommand` runs on your machine at the next rebuild, and extra mounts can expose your files to the container. Compare the recipe with the clean clone's before every open or rebuild.
  - `.git/config`: some settings run commands whenever git works in that folder.

  Keep git on your machine up to date, because fetching from a local folder has had security fixes.
- **Open the clean clone in VS Code's Restricted Mode,** and don't let direnv or mise load settings there. `.vscode/tasks.json`, `.envrc` and `mise.toml` can run commands when a folder opens. The pre-commit hook asks for approval when an agent changes `.vscode/`, `.envrc` or `.gitmodules` at the repo root, but your review is what catches them.
- **One Claude login volume per repo is safer.** The reference recipe shares one `claude-config` volume across all sandboxes, so an agent in one sandbox could change Claude settings that every other sandbox uses. Naming the volume `claude-config-${devcontainerId}` gives each repo its own; you then log in once per repo.
- **Docker isn't available in the container.** A project whose checks need Docker can't run them there, and running them from Ubuntu would run agent code outside the sandbox. Either put that project in a codespace, or give it a Compose-based container recipe, so its services run as separate containers that the agent can reach but can't control (see "The Compose variant" below).
- **Reopening fails with a `vscode-wayland` mount error (WSL 2 + Docker Desktop).** `docker start` fails before any build with `error mounting ... /tmp/vscode-wayland-<id>.sock ... no such file or directory`. Dev Containers baked a mount of the Wayland socket into the container, and that socket no longer exists (WSLg isn't running, or WSL restarted), so every reopen fails. This is VS Code and Docker Desktop behaviour, not a recipe defect, so the recipe is unchanged. Check, then fix, in the WSL shell:

  ```
  ls -l /run/user/$(id -u)/wayland-0              # "No such file or directory" confirms it
  unset WAYLAND_DISPLAY && code --quit
  docker ps -a --filter label=devcontainer.local_folder --format '{{.ID}}  {{.Label "devcontainer.local_folder"}}'
  docker rm -f <ID>                               # the ID whose folder ends in <repo>-sandbox
  ```

  Docker names the container itself, so find it by the folder label rather than by name. Remove only the dev container, not a Compose service such as `db`. Nothing of yours is lost: the repo is a bind mount and the named volumes (the Claude login, and a Compose project's database volume) are separate and unaffected. Only tool installs inside the container go, and `setup.sh` reinstalls them when you reopen the sandbox. To stop it recurring, add `unset WAYLAND_DISPLAY` to `~/.bashrc`, or turn off `Dev > Containers: Mount Wayland Socket` where your VS Code version offers it; undo by removing the line or turning the setting back on. First reported 2026-11-05 (Docker Desktop 29.8.2, Dev Containers 0.469.0).

### The Compose variant (an app plus a database)

Use `environments/local-sandbox/compose/` when the project's checks need a database. Copy its `devcontainer.json`, `compose.yaml` and `Dockerfile` into `.devcontainer/` from a clean clone, next to the standard `setup.sh`, and replace the placeholders for the sandbox folder, database name, user and password. The agent reaches the Postgres service `db` by name and cannot control Docker: the recipe has no Docker socket and no privileged mode, ever, and the database is not published to the host. The data volume persists on the host until you remove it; you run `docker compose` from the host, after reading the files, never the agent. The Postgres tag and the Compose behaviour are unverified until your first rebuild (the steps are in `_human-tasks/`).

In the push check, the throwaway container has no `db`. Tests that need the database must skip when `DATABASE_URL` is unset, or run in CI against a Postgres service. The trade-off: a skipped test proves nothing locally.

### Upgrading the kit in the local sandbox

The container reviews and commits the new kit; you fetch the result and push, as in `procedures/kit-import.md`. The new kit is untrusted data until you have read its diff.

1. **Drop the zip into the container.** In the dev container's VS Code window, drop the new kit zip into the workspace's `.scratch/`. Don't copy it in from Ubuntu's file manager or a terminal on your machine: that would break the rule above about touching the sandbox folder from Ubuntu.
2. **The agent unpacks and reviews it in the container.** It unpacks the zip into a new, empty folder under `.scratch/`, never over the kit folder or into the clean clone, and follows `procedures/kit-import.md`. `make kit-check` and `make kit-compare` run in the container. Read the agent's list of every file and its outcome before anything is staged.
3. **The agent commits in the container, after your approval.** It stages explicit paths and sends you the approval request with `git diff --cached --stat`. The kit folder is protected, so it commits with `HUMAN_APPROVED=1` only after you approve. Then the agent runs `make hooks` in the container.
4. **Give the agent the README's upgrade prompt** for the `AGENTS.md` and blueprint changes. Its commits wait for your approval in the same way.
5. **Fetch and push from the clean clone.** Run `git fetch sandbox`, read the full diff, then merge and push, as in "Pushing" above. Don't run `make` in the clean clone.

If the new kit changes `environments/local-sandbox/pre-push`, copy it from the clean clone, after the fetch and merge, to `~/.agent-hooks/pre-push` and refresh each clean clone's copy. Never copy it from the container's `.scratch/` copy. These steps don't touch `.devcontainer/` or the CI template.

### Comparing the installed push check (human only)

The push check is installed on your machine, outside the sandbox: once at `~/.agent-hooks/pre-push`, and once in each clean clone's `.git/hooks/pre-push`. These are the two `human-machine` rows in `installed-files.txt`, whose source is `environments/local-sandbox/pre-push`. A sandbox tool never opens a `human-machine` install path, so `make kit-check` lists these two as "not checked here" and a sandbox check can never prove the installed push check is current. Only you can compare them, from the clean clone.

Do it with git and coreutils only, never `make`, and never by running or sourcing a repo file (the kit folder is untrusted until you have read its diff). The recipe runs in one clone at a time: repeat it in each clean clone, because `.git/hooks/pre-push` belongs to that clone while `~/.agent-hooks/pre-push` is shared. From the clean clone, with `<ref>` the reviewed commit:

```
p=~/.agent-hooks/pre-push; if test -h "$p"; then echo "symlink: $p, resolve it by hand"; elif test -f "$p"; then git show <ref>:agent-kit/environments/local-sandbox/pre-push | git diff --no-index -- - "$p"; else echo "missing: $p"; fi
p=.git/hooks/pre-push; if test -h "$p"; then echo "symlink: $p, resolve it by hand"; elif test -f "$p"; then git show <ref>:agent-kit/environments/local-sandbox/pre-push | git diff --no-index -- - "$p"; else echo "missing: $p"; fi
```

Each line checks one install path and stops at the first answer. A symlink is tested first and reported, never followed (`cmp` follows symlinks, so it is not an alternative). A missing path, or one that is not a regular file, prints `missing:` and nothing is compared. A match prints nothing and exits 0. A mismatch prints the diff and exits 1. The kit text goes to `git diff --no-index` on standard input, so no temp file is written and nothing is written to an install path. Reinstall by copying from the clean clone, as above; never from the container's `.scratch/` copy. The install paths here come from the map's rows, so they are not hard-coded in a second place.

## Local, no sandbox

The agent runs in your own checkout, with your login and files within its reach. The kit works exactly as in Codespaces: run `make hooks` once, and the kit's pre-push hook checks your pushes. Use this profile only for quick experiments. For real work, use the local sandbox.
