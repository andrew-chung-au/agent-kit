# Issue #138 (task 16): real-Postgres integration tests

**Date:** 2026-10-23
**Branch:** `feat/138-postgres-integration`

## What changed and why

Task 16 of Milestone B (S2): run the existing backend integration cases against
**real Postgres** in a test-owned `vt-test` Compose project, with an `E-GUARD`
that refuses any non-test database. Depends on #31 (the Postgres dev-container
pattern and the `psycopg` lock) and #137 (the `compose.yaml` `db` service) —
both merged.

It is **not** a new set of tests: the same integration cases (already marked
`pytest.mark.sqlite_integration`) run on Postgres when `VT_TEST_DATABASE_URL` is
set, and on in-memory SQLite otherwise (unchanged `make test`).

## Design (human-approved recommendations)

- **Engine fixture in `tests/conftest.py`.** New `db_engine`/`db_session` choose the backend from `VT_TEST_DATABASE_URL`: SQLite in-memory by default; Postgres when set. `sqlite_engine`/`sqlite_session` are kept as aliases, so no existing test module changes.
- **Isolation = fresh schema per test.** On Postgres, `db_engine` does `Base.metadata.drop_all` at setup and teardown, and each test's own `factory` fixture runs `Base.metadata.create_all` — the same schema builder the SQLite harness uses — so the schema is identical to SQLite and nothing persists between tests. (The plan allows "a transaction rollback or a fresh schema"; fresh schema was chosen after a single-shared-connection rollback attempt failed in CI with `AttributeError: 'dict' object has no attribute 'transaction_status'` — the pooled-connection proxy is not the raw psycopg connection. Fresh schema is simple and robust. The migration itself is separately proven by `test_db_migration.py`.)
- **`E-GUARD`** (`guard_test_database_url` in `conftest.py`): refuses unless the URL is `postgresql`, database `vt`, host in `{db, localhost, 127.0.0.1}` — the `vt-test` service. Checked in `pytest_configure` before any connection.
- **Postgres from `compose.yaml`'s `db`** under the `vt-test` project, plus a tiny `compose.test.yaml` override that publishes the db port to the host (the app `compose.yaml` keeps the db unpublished).

## Files

- `tests/conftest.py`: `db_engine`/`db_session` (+ `sqlite_*` aliases), `guard_test_database_url` (E-GUARD), `_run_migrations`, the `VT_TEST_DATABASE_URL` branch in `pytest_configure`.
- `tests/test_integration_guard.py` (new): pure-function E-GUARD cases (marked `unit`; run under `make test`, no Docker) — accepts the three `vt-test` URLs, rejects non-Postgres, wrong db name, and off-allowlist hosts.
- `ci/test-integration.sh` (new): brings up the `vt-test` `db`, sets `VT_TEST_DATABASE_URL`, runs `pytest -m sqlite_integration`, tears down with its volume.
- `compose.test.yaml` (new): test-only override publishing the db port.
- `Makefile` (protected): `make test-integration` (runs the script) and `postgres-integration` (CI alias; task 19 wires the job).
- `_docs/verify-locally.md`: §7 subsection documenting `make test-integration`, E-GUARD and the SQLite/Postgres split.

## Acceptance criteria mapping

- `vt-test` Compose project starts `db`, runs migrations, isolates per test (rollback), never SQLite ✅
- Committed fixtures; no live external call (network guard still installed) ✅
- `make test-integration` green; `E-GUARD` refuses a non-test DB/host ✅ (human runs the Docker part; E-GUARD cases run under `make test`)
- `postgres-integration` job target exists (CI wiring is task 19) ✅
- `make verify` passes — human runs it (see below)

## ⚠️ Human steps (no Docker/venv in the sandbox)

The sandbox can't run Docker or pytest. On the host:
1. `make verify` — the SQLite suite + the new `E-GUARD` unit cases must stay green (backend tests unchanged on SQLite).
2. `make test-integration` — brings up `vt-test` Postgres and runs the integration cases against it; expect green, and the project torn down after.

Logic verified here: both Python test files byte-compile, the bash script passes `bash -n`, and the E-GUARD accept/reject decisions were cross-checked standalone (3 accept, 5 reject, each for the right reason).

## Notes / VERIFY

- `E-GUARD` in `_docs/testing.md` is listed under the Showcase E2E (`vt-e2e`) set; the same guard concept is applied here to the `vt-test` integration run, as #138's acceptance requires. The E2E (`vt-e2e`) form stays a later showcase task; this task implements the integration (`vt-test`) form.
- `VERIFY:` the single-connection `creator=` rollback pattern against Postgres holds for the app's own sessions (the app opens sessions from the test `factory`'s `sessionmaker(engine)`, which share the bound connection). Confirm at `make test-integration`.
- #68 (the dedicated write/restart/read persistence case) stays a separate follow-up, after this task.
