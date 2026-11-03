# Verifying the end-to-end flow locally

A step-by-step guide for independently checking the VulnTriage build on your own
machine: install the dependencies, run the test suites (`make test`), and bring
the application up locally (frontend + backend) for a manual end-to-end check.

It covers two ways to run the app:

- **Tier A (phase S1), §1-§6:** the FastAPI backend on SQLite + the React/Vite
  frontend via `make dev`, with the unit + SQLite-integration tests. No Docker.
- **The Compose stack (phase S2), §7:** the full stack (frontend, backend and
  Postgres) in Docker Compose via `make compose-up` (issue #137). Needs Docker.

Deployment and observability are later phases (S3+) and are out of scope here.

> Status note (2026-10-23): `make test` runs both test suites; `make dev` starts
> the backend and frontend together on SQLite (issue #133); and `make compose-up`
> starts the full stack with Postgres in Docker (issue #137). In every case the
> frontend talks to the real backend over one origin — the API is served under
> `/api` and the proxy (Vite in dev, nginx in Compose) strips the prefix — so
> the SPA owns `/`, `/findings` and `/assets`.

## 1. Prerequisites

You need a machine with real network access to PyPI and the npm registry (the
install step downloads packages). Install these tool versions, which match the
dev-container recipe in `_docs/agent-kit/environments.md`:

| Tool | Version | Check |
|---|---|---|
| Python | 3.12.x | `python3 --version` |
| uv | 0.13.1 (or newer) | `uv --version` |
| Node.js | 24.22.0 | `node --version` |
| npm | 11.x | `npm --version` |
| GNU Make | any recent | `make --version` |

A quick way to see them all at once:

```sh
make tool-versions
```

Docker is **not** required for the Tier A guide (§1-§6). It is required for the
Compose stack in §7, which also needs `docker compose`.

## 2. Get the code

```sh
git clone https://github.com/andrew-chung-au/vuln-triage.git
cd vuln-triage
```

Everything below is run from the repository root.

## 3. Install dependencies

One command installs both halves — the frontend via `npm ci` (from
`frontend/package-lock.json`) and the backend via `uv sync --locked` (from
`backend/uv.lock`):

```sh
make install
```

If you want to do them separately:

```sh
make frontend-install   # npm ci in frontend/
make backend-install    # uv sync --locked in backend/
```

`make install` must finish cleanly before the test or run steps; the test
targets fail early with a clear message if `frontend/node_modules` or
`backend/.venv` is missing.

## 4. Run the tests (`make test`)

This is the single command that runs the frontend unit tests (vitest) and then
the backend unit + SQLite-integration tests (pytest):

```sh
make test
```

What it does, in order:

1. `make frontend-test` — `npm --prefix frontend test` (vitest, the cases in
   `frontend/src/test/`).
2. `make backend-test` — `backend/.venv/bin/pytest -c backend/pyproject.toml tests`
   (the backend unit and SQLite-integration cases in `tests/`, starting with the
   smoke test and the network-guard cases `U-NET` / `I-NET`).

Expected result: both runners report all tests passing. The exact case counts are
whatever each runner prints (they are intentionally not pinned in the docs).

### Network guard

The test harness forbids outbound HTTP: any live network call made during a test
**fails** that test (cases `U-NET` and `I-NET`). The only accepted modes are the
stubs `LLM_MODE=stub` and `RESPONDER_MODE=stub`. If you see `U-NET`/`I-NET`
failing, something is trying to reach the network during tests — that is the
guard working, not a flaky test.

### Run one layer at a time (optional)

```sh
make frontend-test       # frontend vitest only
make backend-test        # backend pytest only
make frontend-typecheck  # tsc --noEmit (vite build does not type-check)
```

## 5. Full verification gate (optional but recommended)

To run exactly what CI runs — both test suites plus the frontend type check,
whitespace and weakened-test checks:

```sh
make verify
```

`make verify` needs `make install` to have run first. The procedure behind it is
`_docs/agent-kit/procedures/verify.md`. A green `make verify` is the project's
definition of "done" for a task.

You can also validate the API contract on its own:

```sh
make openapi-validate
```

## 6. Run the application end to end (manual check)

The goal of the manual check is to confirm the stack runs end to end: the
frontend talks to the backend over one origin, the backend persists to SQLite,
and you can sign in and see assets and ranked findings.

### Start everything with one command

```sh
cp .env.example .env    # fill in GITHUB_READ_TOKEN if you will register assets
make dev
```

`make dev` first applies the SQLite migrations (`alembic upgrade head`, so the
schema exists on a fresh checkout), then starts:

- the backend (FastAPI on SQLite) on `http://127.0.0.1:8000`, and
- the frontend Vite dev server on `http://127.0.0.1:5173`.

They share one origin: the API is served under `/api`, and the Vite dev server
proxies `/api/*` to the backend (stripping the `/api` prefix), so the SPA owns
`/`, `/findings` and `/assets` for client-side routing, there is no CORS, and
the `vt_session` cookie is first-party. The frontend calls the real backend —
the in-memory mock is no longer used at runtime (it remains only as a vitest
fixture).

Press `Ctrl-C` to stop both. The schema is created by the `dev-migrate` step
(`alembic upgrade head`, migrations in `backend/migrations/`, config
`backend/alembic.ini`); run `make dev-migrate` on its own to apply migrations
without starting the servers.

> `VERIFY:` if your backend ASGI entry point or port differs from
> `vulntriage.main:app` on `127.0.0.1:8000`, set `VITE_API_TARGET` for the proxy
> and adjust the Makefile target. The defaults match `backend/vulntriage/main.py`
> and `frontend/vite.config.ts`.

### Background form

To run both in the background (for scripted checks) instead of the foreground:

```sh
make dev-start   # logs: .scratch/dev-backend.log, .scratch/dev-frontend.log
make dev-stop    # stops only the processes dev-start recorded
```

### Create a sign-in user

There is no sign-up. Create a dashboard user with the backend's operator command
(task 9); it reads the password from a prompt, never the command line. Check
`backend/vulntriage/` for the exact command name (`VERIFY:` the invocation), then
run it to create a user with a role of `security lead` so you can register assets.

### What to look for (end-to-end acceptance)

1. Open `http://127.0.0.1:5173` — the sign-in page loads.
2. Sign in with the user you created; the login call reaches `POST /auth/login`
   on the backend and the session cookie is set.
3. As a `security lead`, register an asset (`POST /assets`); the first scan reads
   its lockfiles and creates findings.
4. The dashboard lists assets and ranked findings with status, KEV/EPSS values,
   dependencies and the rank reason — all served by the real backend, not the
   mock (the mock remains only as a vitest fixture).
5. Accept risk on a finding with a reason, request a re-scan, and confirm the
   audit trail shows who, when and the previous value.

This exercises the full Tier A path: frontend → backend → SQLite, with the
session cookie and CSRF header, matching the Application and Testing criteria for
phase S1.

## 7. Run the full Compose stack (phase S2)

This runs the whole application — frontend, backend and **Postgres** — in Docker
Compose with one command (issue #137). It is the container form of §6: the same
one-origin app, but on Postgres instead of SQLite, and served by nginx instead
of the Vite dev server.

Needs Docker and `docker compose`. Run it on a Docker-capable host (your machine
or CI), not in the agent sandbox.

### Start the stack

```sh
cp .env.example .env    # then set POSTGRES_PASSWORD (others may stay blank to start)
make compose-up
```

`make compose-up` runs `docker compose up --build -d --wait`, which builds the
images and starts the services in dependency order, waiting until each is
healthy:

1. `db` — Postgres 16.4, on a named volume (`pgdata`) so data survives a restart.
2. `migrations` — runs `alembic upgrade head` once, then exits.
3. `backend` — FastAPI (uvicorn on `0.0.0.0:8000`); health-checked at `/health`.
4. `frontend` — nginx serving the built SPA on port `8080`; health-checked at
   `/healthz`. This is the only service published to the host.

The app is then at **`http://localhost:8080`**.

### `.env` for the stack

Copy `.env.example` to a git-ignored `.env`. For the stack to start you only need
`POSTGRES_PASSWORD`; `GITHUB_READ_TOKEN` is needed only to register assets, and
the stub switches (`LLM_MODE=stub`, `RESPONDER_MODE=stub`) keep their defaults.
The file lists names only; no values are committed.

### One origin and the `/api` prefix

The API is served under `/api`: the browser calls `/api/...`, and the frontend's
nginx routes `/api/*` to the backend (stripping the prefix), while every other
path serves the SPA. This is what lets the SPA own `/`, `/findings` and
`/assets` as client-side routes without colliding with the API.

### What to check (acceptance)

1. Open `http://localhost:8080` — the sign-in page loads.
2. Create a sign-in user and sign in (see §6 "Create a sign-in user"; run the
   operator command inside the backend container, e.g.
   `docker compose exec backend <command>`).
3. Register an asset and confirm findings appear — same end-to-end path as §6,
   now on Postgres.
4. **The `/api` acceptance check:** navigate to a page such as
   `http://localhost:8080/findings`, then **hard-refresh** (Ctrl/Cmd-Shift-R).
   The SPA must load the findings page — **not** raw API JSON. (If you get JSON,
   the proxy prefix-strip or the SPA fallback is misconfigured.)
5. **Data survives a restart:** `make compose-down` then `make compose-up` again
   (without `CLEAN=1`); the data registered in step 3 is still there.

### Stop the stack

```sh
make compose-down            # stop the stack, keep the Postgres volume
make compose-down CLEAN=1    # also remove the Postgres volume (fresh slate)
```

### Run the integration tests on Postgres (issue #138)

The backend integration cases also run against **real Postgres** (not just the
in-memory SQLite of `make test`), in a test-owned `vt-test` Compose project:

```sh
make test-integration
```

This (via `ci/test-integration.sh`) starts only the `db` service under the
`vt-test` project with its port published to the host, builds the schema with
Alembic, runs the integration-marked cases against Postgres (each test isolated
by a transaction rollback), then tears the project down with its volume. It
needs Docker; it runs in CI (the `postgres-integration` job, wired in task 19)
or on your host, not in the agent sandbox.

Two safety points:

- **`E-GUARD`** refuses to run unless the target is the `vt-test` database
  (`postgresql` driver, database `vt`, host `db`/`localhost`/`127.0.0.1`), so the
  suite can never touch a real or dev database. `E-GUARD`'s own cases run under
  `make test` (they are pure checks, no Docker).
- The `make test` SQLite run is unchanged — the same cases run on SQLite by
  default and on Postgres only when `VT_TEST_DATABASE_URL` is set, which
  `make test-integration` does for you.

## 7b. Run the Compose test jobs (`make test-compose`, phases S2-S4)

Separate from the §7 app stack, `make test-compose` runs the **observability /
alerting / responder** test jobs — the ones the agent sandbox cannot run because
they need Docker (no socket in the sandbox). They are authored in the repo and
verified here or in CI. A `JOB` selector picks one job; with no `JOB` it runs all
three in turn (for your host).

Needs Docker and `docker compose`. Run on a Docker-capable host or in CI, not in
the agent sandbox. No live feed and no secret: each job sets throwaway test-only
env in `ci/test-compose.sh` and runs the backend on `VT_FEEDS=fixtures`.

```sh
make test-compose JOB=telemetry   # US-13: T-REFUSE, T-JOURNEY-BE, I-OWNER-* (MailHog)
make test-compose JOB=alert       # US-14: A-FIRE and its rule-absent negative
make test-compose JOB=responder   # US-15: P-PROD-REFUSAL and the wiring cases (#220); P-DEMO-BE is #233
make test-compose                 # all three in turn
```

What each job brings up and asserts:

- **`telemetry`** (issue #157 + #172): the app stack (`compose.yaml`) and the
  `observability/` stack under one project, with the backend exporting OTLP to
  the Collector. It confirms the Collector drops the A32-excluded attributes
  (`T-REFUSE`) and that one scan→notification journey shares a single trace id
  across metric, trace and log with the owner email reaching MailHog
  (`T-JOURNEY-BE`).
- **`alert`** (issue #159, task 27): the app + observability + a **stub webhook
  sink** under the `vt-alert` project. An in-container seam
  (`manage.py alert-seed`/`alert-set`/`alert-rescore`/`alert-clear`) puts a
  top-tier `NotificationJob` into a chosen state (and backdates `created_at`), so
  the task-26 Grafana rule fires from **stored job state** — not a simulation —
  to the human email (MailHog) and the stub responder sink. It covers `A-FIRE`
  and its rule-removed negative. `A-HELD`, `A-TIER`, `A-GAP` part 1 and the
  `sent` → 0 half of `A-RESOLVE` are unit/SQLite cases under `make test`; see
  `_docs/testing.md`, "Where each case runs". CI runs this job nightly and on
  demand (Actions → verify → Run workflow), not on every push or PR.

  **Manual alert checks** (no automated test covers these; run them before a
  release or after changing the rule, on the stack `make test-compose JOB=alert`
  brings up, or the dev stack):
  1. `A-GAP` part 2: with one finding alert firing, stop the Collector
     (`docker compose -p vt-alert stop otel-collector`) for about 3 minutes, then
     start it. MailHog gets one NoData email with no `finding_id`; the webhook
     sink (`http://localhost:9099/__recorded`) gets no new request.
  2. `A-RESOLVE`, Grafana half: drive the job to `sent`
     (`manage.py alert-set --finding-id <id> --state sent`). Within a few minutes
     the webhook sink records one `status: resolved` request for that finding
     and no second `firing` request.
- **`responder`** (issue #220, task 28c): the app + observability + alert +
  responder under the `vt-responder` project; the responder is built from
  `./backend` with its source bind-mounted (no new image). Needs no `.env`:
  `ci/test-compose.sh` exports throwaway values. It covers the container
  `P-PROD-REFUSAL`, the real Grafana body reaching the responder, a Grafana test
  notification ending `no_change`, a bad bearer getting 401, and the container env
  check. The owner ran the job on a Docker host on 2026-10-26: 8 passed in 103 s
  (#220 comment 6415509715). `P-DEMO-BE` (the full loop) is #233 and is not in
  this job yet. The two stacks publish the same
  host ports, so take the observability stack down before running it.

These cases are `compose`-marked and **deselected** by `make test` / `make verify`
(the default `-m "not compose"`), so a no-Docker `make verify` never runs them and
never *skips* them; `tests/test_marker_hygiene.py` guards against an ordinary test
being silently tagged `compose`.

> **Port already taken?** If a job stops with `ports are not available ... /forwards/expose ... 500` (Docker Desktop on Windows with WSL), see the Troubleshooting table below: on 2026-10-26 the process holding port 9099 was VS Code (`Code.exe`; why it held it was not confirmed). Check a port before you start; it costs a minute.
>
> **First-run `VERIFY:` items.** Each Compose job pins external images (Grafana,
> Tempo, Loki, Prometheus, the Collector, MailHog) whose exact query shapes and
> behaviours are marked `VERIFY:` in the code until a human confirms them on the
> running stack. The **single consolidated checklist of every open
> human/CI verification action**, per issue with the exact commands, is
> `_docs/pending-verification.md` — work from there when you run these jobs, and
> tick items off as they pass. Expect a `VERIFY:` shape to need a small fix on
> the first real run; that is normal, not a defect.

## 8. Clean up

```sh
make frontend-stop     # if the dev server is still running
make dev-stop          # if make dev-start is still running
make compose-down      # if the Compose stack is still up
make clean-scratch     # remove .scratch/ working files
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `backend/.venv is missing: run make install first` | deps not installed | `make install` |
| `frontend/node_modules is missing: run make install first` | deps not installed | `make install` |
| `U-NET` / `I-NET` tests fail | a test tried to reach the network | that is the guard; find and stub the outbound call |
| Install step fails to download | no network / restricted registry access | run on a machine with real PyPI + npm access |
| Dashboard shows no data after `make dev` | backend not reached (proxy target or port) | check `.scratch/dev-backend.log`; set `VITE_API_TARGET` if the backend is not on `127.0.0.1:8000` |
| `make dev-start` says "already running" | a previous run is still up | `make dev-stop` first |
| `make compose-up`: `.env is missing` | no `.env` for the stack | `cp .env.example .env` and set `POSTGRES_PASSWORD` |
| `http://localhost:8080/findings` returns JSON on refresh | nginx `/api` prefix-strip or the SPA fallback is misconfigured | check `frontend/nginx.conf` (`location /api/` and `try_files ... /index.html`) |
| Compose data gone after a restart | the stack was brought down with `CLEAN=1` (volume removed) | use plain `make compose-down`; `CLEAN=1` is a deliberate fresh slate |
| a service never becomes healthy | a dependency failed its health check | `docker compose ps` and `docker compose logs <service>` to see which |
| `make test-compose` stops with `ports are not available: exposing port TCP 127.0.0.1:9099 ... /forwards/expose returned unexpected status: 500` (Docker Desktop on Windows with WSL) | something on Windows already listens on that host port; seen 2026-10-26: **VS Code** (`Code.exe`) auto-forwarding the port it spotted in terminal output | find the owner: `netstat.exe -ano \| grep :9099`, then `tasklist.exe /FI "PID eq <pid>"` (from WSL). For VS Code: Ports panel, right-click the port, **Stop Forwarding Port**, and untick the setting `remote.autoForwardPorts`. The stub webhook sink's 9099 is fixed in `ci/test-compose.sh`, `compose.alert.yaml` and the alert tests, so free the port rather than changing it. Other ports the jobs publish (3000, 4317, 8025, 9090, 9100) can clash the same way. Check a port with `docker run --rm -p 127.0.0.1:<port>:<port> alpine true` |

## Related docs

- `README.md` — the project in one page, planning-document index
- `_docs/tasks.md` — the numbered build tasks (task 11 defines `make dev`)
- `_docs/roadmap.md` — phases S1..S5 and what each banks
- `_docs/testing.md` — the full test strategy, case names and fixtures
- `_docs/agent-kit/environments.md` — which environment runs where
- `_docs/agent-kit/procedures/verify.md` — the `make verify` gate
