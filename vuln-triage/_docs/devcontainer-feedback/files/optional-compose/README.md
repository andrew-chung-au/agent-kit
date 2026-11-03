# Optional Compose variant

This is an example, not the default recipe. It adds a sibling Postgres service
to the dev container without giving the agent Docker control.

## What it changes

- `.devcontainer/devcontainer.json` switches from `image:` to `dockerComposeFile`,
  runs the `app` and `db` services, and sets `workspaceFolder`.
- `.devcontainer/compose.yaml` defines `app` (built from `Dockerfile`) and `db`
  (`postgres:16.4`, healthchecked, not published to the host).
- `.devcontainer/Dockerfile` uses the same Python 3.12 base as the single-image
  recipe.

The generic `setup.sh` and `devcontainer-lock.json` apply unchanged: the feature
set is the same as the single-image recipe.

## What it deliberately does not do

- No Docker socket and no Docker-in-Docker feature. The agent can reach `db`
  by hostname but cannot start, stop or build containers.
- No host paths beyond the workspace.
- No production database settings.

## Before using it

1. Replace `<repo>` in `devcontainer.json` and `compose.yaml` with the repository
   folder name.
2. Change the database name and credentials in both files; the `app` / `app` /
   `app` values are dev-only placeholders.
3. Keep the `DATABASE_URL` driver in step with the project's Python driver.
4. Rebuild the dev container; the human runs `docker compose` from the host when
   needed.

## Verification

- `docker compose config` passes on the host.
- After rebuild, the `db` healthcheck is healthy.
- From the `app` service, the database is reachable at `db:5432`.
- Inside the container, `docker` is still unavailable to the agent.
