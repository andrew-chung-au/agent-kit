# Issue #31 (T3): Compose dev container so Postgres can run

**Date:** 2026-10-23
**Branch:** `feat/31-compose-postgres-devcontainer`

## What changed and why

T3 on the parallel tooling track: give the local sandbox a Compose-based dev
container so Postgres runs as a **sibling service** the agent reaches by hostname
but cannot control. This unblocks Milestone B issues #137 (task 15) and #138
(task 16), which need Postgres, and later #68 (the write/restart/read
persistence test against Postgres). #26 (the SQLAlchemy persistence work) has
landed, so #31's dependency is satisfied.

The former recipe used a single `image:`; it is converted to a Compose dev
container (`dockerComposeFile` + `service: app` + `runServices: [app, db]`).

## Files

- **`.devcontainer/compose.yaml`** (new): `app` (built from `./Dockerfile`) and `db` (`postgres:16.4`, pinned). `db` has a `pg_isready` healthcheck, a `pgdata` named volume, and is **not** published to the host — only `app` reaches it on the Compose network as `db`. `app` mounts **only** the workspace (`..`), attaches to `db` with `depends_on: service_healthy`.
- **`.devcontainer/Dockerfile`** (new): `FROM mcr.microsoft.com/devcontainers/python:3.12` (same base as the former `image:` line). The toolchain install stays in `setup.sh` (`postCreateCommand`).
- **`.devcontainer/devcontainer.json`**: Compose form; `workspaceFolder: /workspaces/vuln-triage-sandbox`; `DATABASE_URL=postgresql+psycopg://vt:vt@db:5432/vt` in `containerEnv`; features (github-cli, node 24.22.0) and the claude-config volume mount kept.
- **`backend/pyproject.toml`**: adds `psycopg[binary]>=3.2,<4` (human-approved). The backend's `create_db_engine` already passes any non-SQLite URL straight to SQLAlchemy, so no code change.
- **`AGENTS.md`** (protected, human-approved): the Environment line and the Docker gotcha updated to describe the Compose recipe, the `db` sibling and the no-socket boundary.

## Acceptance criteria mapping

- Environment route chosen and recorded in AGENTS.md: **done** (Compose recipe; protected commit with `HUMAN_APPROVED=1` after approval).
- Postgres reachable at `DATABASE_URL`, image pinned (not `latest`): **done** (`postgres:16.4`, `postgresql+psycopg://vt:vt@db:5432/vt`).
- `make backend-test` passes against Postgres: **human step** — see below; the dedicated persistence test is #68.
- No SQLite-only code; new driver listed+approved: **done** (`psycopg[binary]` approved; no code change).
- Agent reaches the DB but cannot control the daemon: **done** — no `/var/run/docker.sock` mount.
- No host-executing hook, no host-path mount beyond the workspace: **done** — no `initializeCommand`; only `..` is a host path; `pgdata` is a named volume.
- Reversible: **done** — revert the three `.devcontainer/` files + the AGENTS.md line and rebuild; `docker volume rm` the `pgdata` volume for a clean slate.

## ⚠️ Human steps required (cannot run here)

The Kiro Web sandbox is read-only for uv's Python dir and has no PyPI/Docker, so
`uv lock`, `make backend-test` and the rebuild could not run. During the
rebuild the human must, in order:

1. **`make backend-lock`** — `psycopg[binary]` is a new dependency, so
   `backend/uv.lock` must be regenerated before `uv sync --locked`
   (`make install`) will succeed. This is a `Makefile`-documented target; it
   edits `backend/uv.lock` only.
2. **Rebuild the dev container** from the new recipe (the human's step; the
   agent cannot run Docker).
3. **`make backend-test`** with `DATABASE_URL` set to the `db` service, and
   quote the command and result on #31.

## Notes / risks

- The `db` credentials are a literal `vt/vt` in `compose.yaml`. Acceptable: this is a **local-only dev-container** Postgres, never published to the host or network, and not the application's own Compose stack (task 15, which uses `.env`). Not a secret.
- `VERIFY:` the `postgres:16.4` tag and that `psycopg[binary]` resolves on the pinned uv (the human sees this at `make backend-lock`).
- The undo is recorded above (revert + rebuild).
