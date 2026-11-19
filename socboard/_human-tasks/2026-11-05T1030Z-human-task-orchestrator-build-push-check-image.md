# Build the push-check image with uv

## Purpose

Let the push check run `make install` (uv) in its throwaway container. Issue: none.

## Where to run it

On your machine, from the clean clone. Not here: the dev container (it has no Docker) and the sandbox folder.

## Before you start

1. Confirm Docker is available.

```
docker version --format '{{.Server.Version}}'
```

Expected: a version number.

## Steps

### Step 1: Build the image

```
docker build -t agent-push-check:node24-uv0.13.6 - < _docs/agent-kit/environments/local-sandbox/push-check.Dockerfile
```

Expected: a successful build.
Risk: none; the image holds no credentials or project files.

### Step 2: Point the push check at it

```
export AGENT_PUSH_CHECK_IMAGE=agent-push-check:node24-uv0.13.6
```

Expected: no output.

### Step 3: Dry-run the next push

```
AGENT_PUSH_CHECK_PLAN=1 git push
```

Expected: the push check prints what it would check and runs nothing.

## Record the result (Recorded: 05/11/2026)

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | Pass | 29.9.2 |
| 2 | Pass | |
| 3 | Pass | |

## Risk

The image is built from the clean clone's kit copy; don't build from the sandbox.
