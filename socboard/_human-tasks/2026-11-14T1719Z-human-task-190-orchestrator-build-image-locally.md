# Build the container image once on your machine and report the result

## Purpose

Build the image from the `Dockerfile`, run it, and report what the sandbox could not check: that the base image tags and digests resolve, that the locked dependencies (including the Postgres driver) install, and whether `bun run build` needs Node as well as bun. CI builds the image on every push; this is the one local check by a person. Issue: #190.

## Where to run it

Your machine, in a clean clone of the branch for #190 (or of `main` once it is merged), with Docker running. Not here: the Kiro Web sandbox, which has no Docker.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Confirm the clone is clean and on the right commit.

```
git status --short --branch
```

Expected: no changed files, on the branch or on `main`.

## Steps

### Step 1: build the image

```
docker build --tag socboard-image:local .
```

Expected: the build finishes. The three stages are the frontend build (Node with bun), the dependency install (`uv sync --locked --no-dev`) and the final image.
If different: stop and tell the orchestrator which stage failed and the last lines printed. Do not edit the `Dockerfile`.

### Step 2: report the base images and the Node question

```
docker image inspect socboard-image:local --format '{{.Architecture}} {{.Size}}'
```

Expected: one line with the architecture and a size in bytes.

Then write down, in the table below: (a) whether the four base image tags (`oven/bun`, `node`, `python`, the uv image) pulled without an error and whether each digest in the `Dockerfile` was accepted; (b) whether the frontend stage worked with Node 24.22.0 and bun 1.4.2 together, or whether it needed a change (for example, whether `bun run build` still ran `vite` through Node).

### Step 3: the image runs as a numeric non-root user with one worker

```
docker run --rm --entrypoint id socboard-image:local
```

Expected: `uid=10001` and `gid=10001`, not `uid=0`.
If different: stop and tell the orchestrator what was printed.

### Step 4: deployed mode with no settings refuses to start

Refusal test: use a normal terminal on your machine. Risk: none; the container holds no secret and the command passes none, so nothing secret can print. If the rule fails, the container starts and keeps running: stop it with `docker ps` and `docker stop`.

```
docker run --rm --env SOCBOARD_MODE=deployed socboard-image:local
```

Expected: a short refusal naming the missing settings, no value, and exit code 2 (`echo $?` right after).
If different: stop and tell the orchestrator what was printed.

### Step 5: run it with throwaway settings and open it in a browser

Make the values in your shell without printing them (a token secret, an ingest key, and one password for all three seed users), then start the container with a SQLite file under `/tmp`, migrate and seed in it, and open http://127.0.0.1:8000/.

```
docker run --detach --name socboard-local --publish 127.0.0.1:8000:8000 --env SOCBOARD_MODE=deployed --env SOCBOARD_TOKEN_SECRET --env SOCBOARD_INGEST_API_KEY --env SOCBOARD_DATABASE_URL=sqlite:////tmp/local.db socboard-image:local
docker exec socboard-local python -m socboard.migrate
docker exec --env SOCBOARD_SEED_PASSWORD_ANALYST_A --env SOCBOARD_SEED_PASSWORD_ANALYST_B --env SOCBOARD_SEED_PASSWORD_LEAD socboard-local python -m socboard.seed
```

(The three `--env NAME` forms read the value from your shell, where you set them beforehand with a random value each; none is typed into the command line.)

Expected: http://127.0.0.1:8000/api/health answers 200; the page at http://127.0.0.1:8000/ loads the sign-in screen from the same origin, and signing in as `lead` with the seed password works.
If different: stop and tell the orchestrator what the page or `docker logs socboard-local` shows.
Risk: the container keeps running until you stop it. Undo: `docker stop socboard-local` then `docker rm socboard-local`.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 (tags, digests, Node and bun) | | |
| 3 | | |
| 4 | | |
| 5 | | |

## Risk

Low. The image holds no secret; step 5 starts a container bound to 127.0.0.1 only, and the undo is in the step.
