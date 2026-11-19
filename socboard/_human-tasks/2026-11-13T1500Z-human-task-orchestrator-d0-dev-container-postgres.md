# Add a Postgres service to the dev container (Deploy item D0)

## Purpose

Give the dev container a throwaway Postgres service named `db`, so the Postgres work (D5a onward) can be tried quickly while CI stays the evidence of record. Issue: none yet (D0 is a sitting, not an Engineer issue; see `_docs/planning/deploy-backlog-proposal.md`, D0). Do it between issues, after the D4 issue (#142) and before D5a (#143); do not do it while an Engineer launch is in progress.

## Where to run it

Your machine, in the clean clone for the edit and the push, and in VS Code (Dev Containers) for the rebuild. Not here: the Kiro Web sandbox, which has no Docker. Follow `_docs/agent-kit/environments.md` ("Rules for the local sandbox" and "The Compose variant") where this file is shorter than it.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Confirm no Engineer launch is in progress and `main` is current. Nothing on `main` should depend on a database service; the default test run must still pass without Postgres, because the push check container has no `db`.

```
git status --short --branch
```

Expected: your clean clone on `main`, no other lines.

2. Confirm which Postgres major version the Deploy decision record pins (issue #139). If it is not approved yet, use 16, the version the recipe assumes, and change it later if the record says otherwise.

## Steps

### Step 1: copy the recipe over the dev container files, on a branch

Do this in the clean clone, on a new branch (for example `d0-dev-container-postgres`). Copy `devcontainer.json`, `compose.yaml` and `Dockerfile` from `_docs/agent-kit/environments/local-sandbox/compose/` into `.devcontainer/`. Keep the existing `setup.sh` and `devcontainer-lock.json`.

Then compare the new `devcontainer.json` with the old one:

```
git diff .devcontainer/devcontainer.json
```

Expected: only five kinds of change: `image` replaced by `dockerComposeFile`, `service`, `runServices` and `workspaceFolder`, and one new `DATABASE_URL` line under `containerEnv`. Anything else in the old file (the Node feature, the mounts, the settings) is unchanged.
If different: stop and tell the orchestrator what differs. Do not merge by hand.

### Step 2: replace the four placeholders, in both files, identically

Replace `<folder>` (the sandbox folder's name), `<db_name>`, `<db_user>` and `<db_password>` in `compose.yaml` and `devcontainer.json`. Use plain names for the first three, for example `socboard_dev`. For the password choose a throwaway value used nowhere else. It will be committed to a public repository, so it must never be reused for the deployment, a cloud account or anything real.

```
grep -n -E "<folder>|<db_name>|<db_user>|<db_password>" .devcontainer/compose.yaml .devcontainer/devcontainer.json
```

Expected: no lines.

### Step 3: check the recipe's limits and the image tag

```
grep -n -E "ports|privileged|network_mode|docker.sock" .devcontainer/compose.yaml
```

Expected: no lines (the database is not published to the host, has no host path, no Docker socket and nothing is privileged).
If different: stop; do not add any of those.

```
docker manifest inspect postgres:16.15
```

Expected: JSON output and exit 0. The recipe says its tag is unverified. If it fails, pick the newest `16.x` tag that exists on Docker Hub, put it in `compose.yaml`, and note it in the result table.

### Step 4: note the driver assumption

The recipe's `DATABASE_URL` uses the driver name `psycopg`. D5a chooses and adds the real driver after your approval. If D5a picks a different one, change the scheme in `devcontainer.json` in D5a's sitting. No action now.

### Step 5: commit, push and let CI run

`.devcontainer/*` is a protected path, so the commit needs your approval of this exact diff:

```
git diff --stat
```

Expected: `compose.yaml` and `Dockerfile` added, `devcontainer.json` changed, nothing else.

Commit with your approval flag as the kit describes, push the branch and open a pull request. CI runs `make verify`; it does not use the dev container, so it should pass unchanged.

### Step 6: rebuild the container and reach the database

Open the sandbox folder (never the clean clone) in the dev container and rebuild it. Then, inside the container:

```
timeout 3 bash -c '</dev/tcp/db/5432' && echo open
```

Expected: `open`.
If different: the `db` service is not up or not healthy; check `docker ps` on the host for the `db` container and tell the orchestrator what you see. Do not retry another way.

### Step 7: confirm nothing else changed

Inside the container, run the default checks.

```
make test
```

Expected: the same pass counts as CI on `main`. The test run does not use the database yet.

## Record the result

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 (limits) | | |
| 3 (image tag used) | | |
| 5 (CI run) | | |
| 6 | | |
| 7 | | |

## Risk

Rebuilding the container discards tool installs inside it; `setup.sh` reinstalls them. The recipe's own notes say it is untested until its first rebuild. To reverse it, revert the three files and rebuild. Removing the database volume (`pgdata`) is a step for you on the host; an agent never does it. The dev-container database is for iteration speed only: CI stays the evidence of record, and its password is never used anywhere else.
