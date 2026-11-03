# Build the push-check image and run the push check with it

## Purpose

Build the reference push-check image, confirm its tool versions, and run the push check with it so a Node plus uv project passes `make install verify`. Issue: #96. The Engineer cannot run Docker here, so nothing below has been run.

## Where to run it

On your machine, in the clean clone (the folder you push from), in the shell you push from. Not here: never run `make` in a clean clone, and build only from the clean clone's copy of the Dockerfile, never one taken from a sandbox. The commands below build with no build context.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check that the clean clone has no local changes and that the Dockerfile is there.

```
git status --short
```

Expected: no output.

2. Read `agent-kit/environments/local-sandbox/push-check.Dockerfile` before building. Its pins are unverified: Node, uv, the Python base and the Node image variant.

## Steps

### Step 1: Build the image from standard input, so docker gets no build context.

```
docker build -t agent-push-check:node24-uv0.13.6 - < agent-kit/environments/local-sandbox/push-check.Dockerfile
```

Expected: the build finishes. Its last step prints the versions of bash, git, make, python3, node, npm and uv.
If different: stop and tell the orchestrator what was printed (a tag in the file may not exist).

### Step 2: Check the Node version.

```
docker run --rm agent-push-check:node24-uv0.13.6 node --version
```

Expected: `v24.22.0`.
If different: stop and tell the orchestrator what was printed.

### Step 3: Check the npm version.

```
docker run --rm agent-push-check:node24-uv0.13.6 npm --version
```

Expected: the npm that ships with that Node (`11.19.1` is expected, unverified).
If different: write what was printed in the table.

### Step 4: Check the uv version.

```
docker run --rm agent-push-check:node24-uv0.13.6 uv --version
```

Expected: `uv 0.13.6`.
If different: stop and tell the orchestrator what was printed.

### Step 5: Check the Python version.

```
docker run --rm agent-push-check:node24-uv0.13.6 python3 --version
```

Expected: a `Python 3.12` version.
If different: stop and tell the orchestrator what was printed.

### Step 6: Point the push check at the image and run the dry run.

Run this in the clean clone, in a project push that changes a project with `agent-kit.conf`. Set the variable in this shell first: `export AGENT_PUSH_CHECK_IMAGE=agent-push-check:node24-uv0.13.6`.

```
AGENT_PUSH_CHECK_PLAN=1 git push
```

Expected: the push check prints what it would check, runs nothing and lets the push go on.
Risk: with the plan variable set the push check passes without checking anything, and the push goes through. Use a branch you are happy to push, or a push that has nothing to send.
If different: stop and tell the orchestrator what was printed.

### Step 7: Do a real push from the clean clone.

```
git push
```

Expected: the push check runs `make -C <project> install verify` in the new image and passes. Without the image, the same push fails with exit 127.
If different: stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either. Also record the date and who confirmed each unverified pin: the Python base tag, the `node:24.22.0-bookworm-slim` image, the `ghcr.io/astral-sh/uv:0.13.6` image, and npm.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |

## Risk

Low. The image holds no credentials or project files. Step 6 lets a push through unchecked on purpose; step 7 pushes for real, so do it only for a push you have reviewed.
