# Rebuild the push-check image with bun

## Purpose

Let the push check run the frontend tests (`make install` installs the frontend packages). Issue: #46.

## Where to run it

On your machine, from the clean clone, after the #46 commits are merged there. Not in the dev container (no Docker) and not in the sandbox folder.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check that the #46 commits, including the Dockerfile change (P5), are in the clean clone and that Docker runs.

```
docker version
```

Expected: client and server versions print without an error.

## Steps

### Step 1: Build the image from standard input (no build context)

```
docker build -t agent-push-check:node24-uv0.13.6-bun1.4.2 - < _docs/agent-kit/environments/local-sandbox/push-check.Dockerfile
```

Expected: a successful build ending with the version check.
If different: if bun is not found or the version differs, stop, don't retry another way, and tell the orchestrator what was printed.
Risk: replaces the image with this tag if it exists. Undo: `docker image rm agent-push-check:node24-uv0.13.6-bun1.4.2`.

### Step 2: Point the push check at the new image

```
export AGENT_PUSH_CHECK_IMAGE=agent-push-check:node24-uv0.13.6-bun1.4.2
```

Expected: no output. The variable lasts for this shell only.
Risk: changes which image the push check uses in this shell. Undo: `unset AGENT_PUSH_CHECK_IMAGE` (back to the default image, which fails at `make install`).

### Step 3: Dry run the push check

```
AGENT_PUSH_CHECK_PLAN=1 git push
```

Expected: it prints what it would check and runs nothing; the push goes on, so use a branch you are happy to push.
If different: stop and tell the orchestrator what was printed.

### Step 4: Push for real

```
git push
```

Expected: the push check shows `make -C . install verify`, a bun install and Vitest's passed count. With `AGENT_PUSH_CHECK_NETWORK=none` it fails at install; that is expected.
If different: stop and tell the orchestrator what was printed.
Risk: publishes the commits. Can't be undone by this task.

### Step 5: Read the CI run

Open the GitHub Actions run for the push.

Expected: green, with the same bun install and Vitest lines in its log.
If different: stop and tell the orchestrator which step failed; do not push a fix yourself.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

## Risk

The image holds no credentials or project files. Undo for the whole task: `unset AGENT_PUSH_CHECK_IMAGE`, remove the image with `docker image rm agent-push-check:node24-uv0.13.6-bun1.4.2`, and revert the #46 commits.
