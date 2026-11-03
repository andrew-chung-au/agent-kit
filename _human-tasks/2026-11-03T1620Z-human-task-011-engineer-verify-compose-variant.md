# Verify the optional Compose variant of the dev container

## Purpose

Check that the Compose variant (an `app` service plus a Postgres `db` service) builds, that the database becomes healthy and is reachable only by name, and that the container has no Docker access. Issue: #11. The Engineer cannot run Docker here, so nothing below has been run.

## Where to run it

On your machine, in a throwaway folder that is not this repo's `.devcontainer/`. Copy `devcontainer.json`, `compose.yaml` and `Dockerfile` from the clean clone's `agent-kit/environments/local-sandbox/compose/`, and `setup.sh` from `agent-kit/environments/local-sandbox/`, into the throwaway folder's `.devcontainer/`. Replace the placeholders `<folder>`, `<db_name>`, `<db_user>` and `<db_password>` identically in `devcontainer.json` and `compose.yaml` (the password is a dev-only value). Read both files before the first command. Not here: never run `make` in a clean clone.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check that the throwaway folder holds the four files.

```
ls .devcontainer
```

Expected: `Dockerfile`, `compose.yaml`, `devcontainer.json` and `setup.sh`.

## Steps

### Step 1: Check the merged Compose configuration.

This is read-only. Run it from the throwaway folder's root on the host.

```
docker compose -f .devcontainer/compose.yaml config
```

Expected: the merged config prints with no error, shows `postgres:16.15` for `db`, a `pgdata` volume, and no `ports` under `db`.
If different: stop and tell the orchestrator what was printed (the Postgres tag is unverified).

### Step 2: Rebuild the dev container and check the database is healthy.

Run "Dev Containers: Rebuild and Reopen in Container". When it finishes, run this on the host.

```
docker compose -f .devcontainer/compose.yaml ps
```

Expected: `db` shows as healthy and `app` is running.
If different: stop and tell the orchestrator what was printed, and the rebuild log's last lines.

### Step 3: Check the app reaches the database by name.

Run this in a terminal inside the dev container.

```
pg_isready -h db -p 5432
```

Expected: `db:5432 - accepting connections`. If `pg_isready` is not installed in the app container, tell the orchestrator.
If different: stop and tell the orchestrator what was printed.

### Step 4: Check that Docker is unavailable inside the container.

```
command -v docker
```

Expected: no output.
If different: stop and tell the orchestrator what was printed.

### Step 5: Check that there is no Docker socket inside the container.

```
ls /var/run/docker.sock
```

Expected: an error saying the file does not exist.
If different: stop and tell the orchestrator at once, and close the container.

### Step 6: Check that the Node and tool pins still hold in the Compose container.

```
node --version
```

Expected: `v24.22.0`, and the features (Node, GitHub CLI) are present in a container built from the `Dockerfile`.
If different: stop and tell the orchestrator what was printed.

### Step 7: Check the data volume is named for this project only.

Run this on the host.

```
docker volume ls
```

Expected: a `pgdata` volume whose name starts with this project's Compose project name, not a bare `pgdata` shared with another project. If it is shared, tell the orchestrator: the Engineer adds a top-level `name:` placeholder to `compose.yaml` and a test.
If different: write what was printed in the table.

### Step 8: Remove the data volume to start clean (optional, destructive).

Only when you want a clean database. Removing the volume deletes the database's data; no agent does this.
Risk: the data in that volume is lost and can't be recovered. Close the dev container and stop the services first.

```
docker volume rm <the pgdata volume name from step 7>
```

Expected: the volume name is printed back.
If different: stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either. Also record whether the Postgres tag `16.15` exists on Docker Hub (the release was published 2026-08-13; the image tag is unverified) and whether a newer 16.x patch is available, whether `mounts` and `features` applied on the Compose service, and whether `workspaceFolder` plus the `..` mount produced the expected path.

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

## Risk

Low, apart from step 8, which deletes the database volume on purpose. Everything else runs in a throwaway folder.
