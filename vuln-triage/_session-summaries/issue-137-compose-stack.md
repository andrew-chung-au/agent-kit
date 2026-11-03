# Issue #137 (task 15): one-command Compose stack

**Date:** 2026-10-23
**Branch:** `feat/137-compose-stack`

## What changed and why

Task 15 of Milestone B (S2): `docker compose up` starts the frontend, backend
and Postgres with one command, on one origin. Builds on #31 (the dev-container
Postgres pattern) and #133 (the real `Services` over fetch).

### The /api move (Option B, human-approved)

The SPA's client routes (`/`, `/findings`, `/assets`) collided with the API's
root-level paths on one origin. Resolved by moving the API under `/api`: the
frontend calls `/api/...`, the reverse proxy strips `/api`, and the backend
still mounts the bare paths. Analysis and decisions are in
`planning-2026-10-23-api-prefix-proposal.md`. Because the proxy strips the
prefix, the 58 backend endpoint tests and the conformance test are unchanged.

- `frontend/src/services/httpService.ts`: `const API_BASE = "/api"`, applied once in `request()`.
- `frontend/src/test/http-service.test.ts`: two URL assertions updated to `/api/...`.
- `frontend/vite.config.ts`: dev proxy is a single `/api` with `rewrite` stripping the prefix.
- `backend/vulntriage/main.py`: `/health` route; routes stay at `/findings` etc. (D1's `root_path="/api"` was dropped — deprecated in the pinned FastAPI and only cosmetic; the proxy strips `/api` regardless. Caught by `make verify`.)
- `_docs/openapi.yaml`: `servers.url: /` → `/api`. `_docs/api.md`: base-path note + `/health` note (D2: reached at `/api/health` through the proxy; backend path stays `/health`).

### The Compose stack

- `backend/Dockerfile`: multi-stage, non-root (uid 10001), uvicorn on `0.0.0.0:8000`, built with uv from the locked file.
- `frontend/Dockerfile`: multi-stage Node build → unprivileged nginx (listens 8080) serving `dist/`.
- `frontend/nginx.conf`: SPA fallback (`try_files ... /index.html`) + single `location /api/` proxy to `backend:8000` (strips the prefix); own liveness at `/healthz`.
- `compose.yaml` (repo root): `db` (postgres:16.4, `pgdata` named volume, `pg_isready` healthcheck) → `migrations` (`alembic upgrade head`, runs once, `service_completed_successfully`) → `backend` (healthcheck on `:8000/health`) → `frontend` (healthcheck on `/healthz`). Only the frontend publishes a port (8080).
- `backend/.dockerignore`, `frontend/.dockerignore`: keep `.venv`/`node_modules`/`dist`/`.env` out of the build contexts.
- `.env.example`: names only — `POSTGRES_PASSWORD`, `GITHUB_READ_TOKEN`, `RESPONDER_API_TOKEN`, `GRAFANA_ADMIN_PASSWORD`, `RESPONDER_LLM_KEY`, and `LLM_MODE=stub` / `RESPONDER_MODE=stub`. No showcase settings.
- `GET /health` added to the backend (task 14 deferred it; the conformance test already excludes `/health` by name, so this is expected and safe).
- `Makefile` (protected): `make compose-up` (`docker compose up --build -d --wait`, requires `.env`) and `make compose-down` (`CLEAN=1` also removes the volume).

## Acceptance criteria mapping

- Multi-stage Dockerfiles, non-root, backend on 0.0.0.0, health checks ✅
- Compose file with frontend/backend/Postgres `db` + migrations, named volume, health checks, `depends_on: healthy`/`completed_successfully` ✅
- One `make` target brings the stack up; frontend reads the API on one origin ✅
- Data survives a restart (named `pgdata` volume) ✅ (human verifies at `compose-up`)
- `.env.example` names-only, listed settings, no showcase ✅
- No image pushed; no Collector/MailHog/n8n ✅

## ⚠️ Human steps (cannot run Docker here)

The sandbox has no Docker/PyPI, so `make compose-up` and `make verify` could not run. The human runs, on the host:
1. `cp .env.example .env` and fill `POSTGRES_PASSWORD` (others can stay blank for the app to start; `GITHUB_READ_TOKEN` only needed to register assets).
2. `make compose-up` → stack comes up healthy; open `http://localhost:8080`.
3. `make verify` → frontend suite (incl. the updated http-service URL assertions) + backend conformance test must stay green (expected; backend/tests unchanged by the /api move).
4. **Acceptance for the /api move:** hard-refresh `http://localhost:8080/findings` → the SPA loads (not API JSON).

## Notes / VERIFY

- `VERIFY:` `proxy_pass http://backend:8000/;` (trailing slash) strips the `/api/` prefix (nginx) and the Vite `rewrite` does the same in dev.
- `VERIFY:` the `nginxinc/nginx-unprivileged:1.27-alpine` and `node:24.22.0-bookworm-slim` tags resolve at build.
- Backend container health check uses `python -c urllib.request` against `:8000/health` (no curl in the slim image).
- The `uv.lock` already includes `psycopg` (from #31), which the backend image installs.
