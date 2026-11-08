# Rebuild check for the Python plus frontend dev container recipe

## Purpose

Check the reference recipe's Node, npm and uv pins, the `PATH` entry, the per-folder container name and the early clean-clone refusal in a throwaway dev container. Issue: #95. The Engineer cannot run Docker here, so nothing below has been run.

## Where to run it

On your machine, in a throwaway folder that is not this repo's `.devcontainer/` (which stays unchanged), opened in VS Code as a dev container. Use a small test project with a frontend (`package-lock.json`), a backend (`uv.lock`) and a `make install` target. Not here: never run `make` in a clean clone.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. In the throwaway folder, copy `devcontainer.json` and `setup.sh` from the clean clone's `agent-kit/environments/local-sandbox/` into `.devcontainer/`, and fill in your name and noreply email in `setup.sh`. Don't commit or push them.

```
ls .devcontainer
```

Expected: `devcontainer.json` and `setup.sh`.

2. Run "Dev Containers: Rebuild and Reopen in Container" and open a terminal in the container. The rebuild log should end with "Setup complete", and the container's name should be the throwaway folder's name, not a fixed name. If the log shows an error, stop and tell the orchestrator its last lines.

## Steps

### Step 1: Check the Node version.

```
node --version
```

Expected: `v24.22.0`.
If different: stop and tell the orchestrator what was printed (the pin is unverified).

### Step 2: Check the npm version.

```
npm --version
```

Expected: `11.19.1` (unverified: the npm that ships with that Node).
If different: write what was printed in the table; the expected value is only a guess.

### Step 3: Check the uv version.

```
uv --version
```

Expected: `uv 0.13.6`.
If different: stop and tell the orchestrator what was printed.

### Step 4: Check the nvm version.

```
nvm --version
```

Expected: `0.40.8`.
If different: stop and tell the orchestrator what was printed.

### Step 5: Check that no yarn shim resolves.

```
command -v yarn
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

### Step 6: Check that no pnpm shim resolves.

```
command -v pnpm
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

### Step 7: Check that `claude` resolves in a new terminal.

Open a new terminal in the container first.

```
command -v claude
```

Expected: a path under the container user's `.local/bin`.
If different: stop and tell the orchestrator what was printed.

### Step 8: Check that `opencode` resolves in a new terminal.

```
command -v opencode
```

Expected: a path under the container user's `.opencode/bin`.
If different: stop and tell the orchestrator what was printed.

### Step 9: Install the project's dependencies.

```
make install
```

Expected: the frontend and backend dependencies install without error.
If different: stop and tell the orchestrator what was printed.

### Step 10: Check the tool list.

```
make tool-versions
```

Expected: one line per tool (git, gh, node, npm, python3, uv, docker), and `docker: missing`.
If different: stop and tell the orchestrator what was printed.

### Step 11: Check the lock file the rebuild created.

```
git status --short
```

Expected: `.devcontainer/devcontainer-lock.json` is new and has an entry for the Node feature. Commit it in the throwaway project; the Engineer never writes it.
If different: stop and tell the orchestrator what was printed.

### Step 12: Open a clean clone on purpose and see the early refusal.

Refusal test: use a throwaway clean clone (a folder with a remote named `sandbox`) with the same `.devcontainer/` files, never your real clean clone. First check the remote in that folder's terminal on the host, then rebuild and reopen it in the container.
Risk: if the check fails, the setup step would install tools and write the global git config inside that throwaway container only; nothing is pushed. Close and delete the container afterwards.

```
git remote
```

Expected: `sandbox` is listed. After the rebuild, the setup step fails at once with a message that this is a clean clone, to close the container and reopen the `<repo>-sandbox` folder, and to see `environments.md`. No install lines appear before it.
If different: stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either. Also record the date and who confirmed each unverified pin: Node, nvm, npm, uv, the Node feature options (`nvmVersion`, `pnpmVersion`), `pipx` in the base image, the nvm Node path in `setup.sh`, and the CI template's action majors (the first CI run confirms those).

Result recorded on 2026-11-07 by andrew, from a run on the host in a throwaway dev container (`~/clone/recipe-check`, container user `vscode`, host container `24ef0e4909b8`) built from the clean clone's recipe. The rebuild log ended with `Setup complete`.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | pass | `node --version` printed `v24.22.0`. Confirms the Node pin. |
| 2 | pass | `npm --version` printed `11.19.1`, matching the guessed value. |
| 3 | pass | `uv --version` printed `uv 0.13.6 (x86_64-unknown-linux-gnu)`. The first attempt, made while setup was still running, printed `bash: uv: command not found`; it passed after `Setup complete`. |
| 4 | pass | `nvm --version` printed `0.40.8`. Confirms the Node feature's `nvmVersion`. |
| 5 | pass | `command -v yarn` printed nothing after `Setup complete`. An earlier run mid-setup printed `/usr/local/share/nvm/versions/node/v24.22.0/bin/yarn`, before the `corepack disable` line; that was timing, not a failure. |
| 6 | pass | `command -v pnpm` printed nothing after `Setup complete`; mid-setup it printed a path under the same nvm directory. `pnpmVersion: "none"` confirmed. |
| 7 | pass | `command -v claude` printed `~/.local/bin/claude`. Confirms the `PATH` entry. |
| 8 | pass | `command -v opencode` printed `~/.opencode/bin/opencode`. Confirms the `PATH` entry. |
| 9 | pass | `make install` installed both sides. Frontend: `up to date, audited 1 package`, `found 0 vulnerabilities`. Backend: uv warned that the bind-mounted `.venv` was linked to a non-existent host interpreter (a `cpython-3.14` path), removed it and recreated it with `CPython 3.12.16` at `/usr/local/bin/python3`, then resolved and checked. Warning is expected when a host-made venv is mounted; not a failure. |
| 10 | pass | `make tool-versions` printed `git: git version 2.56.0`, `gh: gh version 2.103.3 (2026-10-26)`, `node: v24.22.0`, `npm: 11.19.1`, `python3: Python 3.12.16`, `uv: uv 0.13.6 (x86_64-unknown-linux-gnu)`, `docker: missing`. |
| 11 | pass | `git status --short` showed only `?? .devcontainer/devcontainer-lock.json`. Its Node entry is `"ghcr.io/devcontainers/features/node:2"`, resolved to `ghcr.io/devcontainers/features/node@sha256:2a19d3b0b3879437637cfd292eb29fee0afcfbe6364e33db9afc4f80c5c1f956`. Committed in the throwaway as `f8cd6d0`. |
| 12 | pass | `git remote` listed `origin` and `sandbox`. Rebuilding that throwaway clean clone failed at once: `setup.sh: this is a clean clone (it has a 'sandbox' remote or the clean-clone push check).` with the two advice lines, `postCreateCommand ... failed with exit code 1`, and no install lines before it. |

Pin notes:
- **Node** `24.22.0`: confirmed by step 1.
- **nvm** `0.40.8`: confirmed by step 4.
- **npm** `11.19.1`: confirmed by step 2 (not a separate pin; it ships with Node).
- **uv** `0.13.6`: confirmed by step 3.
- **Node feature options** `nvmVersion: "0.40.8"` and `pnpmVersion: "none"`: confirmed by steps 4 and 6.
- **`pipx` in the base image**: not run directly (`command -v pipx` was skipped). Indirectly confirmed, because `setup.sh` installs uv with `pipx install --force uv==0.13.6` and step 3 found that exact uv.
- **nvm Node path** in `setup.sh`: not printed by `command -v node`. Indirectly confirmed by the mid-setup `yarn` and `pnpm` paths, both under `/usr/local/share/nvm/versions/node/v24.22.0/bin/`.
- **CI template action majors**: not confirmed by this run; the first CI run confirms them.

The clean-clone container from step 12 was left to the human to remove with `docker rm -f`.

## Risk

Low. Everything runs in throwaway containers; step 12 starts and closes one. If a pin fails, tell the orchestrator: the Engineer changes it in the recipe, `setup.sh`, the CI template and this file together.
