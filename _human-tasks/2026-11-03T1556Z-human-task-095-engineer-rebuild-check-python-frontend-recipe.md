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

Expected: `uv 0.13.1`.
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

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| 9 | | |
| 10 | | |
| 11 | | |
| 12 | | |

## Risk

Low. Everything runs in throwaway containers; step 12 starts and closes one. If a pin fails, tell the orchestrator: the Engineer changes it in the recipe, `setup.sh`, the CI template and this file together.
