# Issue #192: Run the backend tests on Postgres in CI: fixtures take the database from a URL

**Date:** 2026-11-14T18:09Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The Python tests now run on SQLite by default and on Postgres 16 in CI, from the same test code. D6a (#193), D7 (#194) and D6b (#195) need tests that run on Postgres.

- `tests/db_target.py`: the one place that builds a test database URL. With `SOCBOARD_TEST_POSTGRES_URL` set to a `postgresql+psycopg://` server URL, each test gets a new database (`socboard_t_` plus 12 hex digits; app fixtures copy a template with `CREATE DATABASE ... TEMPLATE`), dropped when the test ends, pass or fail. A wrong value, or a server that cannot be reached, stops the run before any test without printing the value. It also holds the three shared `sqlite_only` markers, each with its owner issue.
- `tests/conftest.py`: registers `sqlite_only(reason)`, refuses a marker without a one-line reason, deselects marked tests on Postgres (never skips: the verify gate refuses added skip lines), and prints the marked and deselected counts and the test databases before, dropped and left.
- The three support files and 9 modules take their database from the helper. 61 functions marked from the first Postgres run's failures (25 need the SQLite triggers, owner D6a; 30 test the guard's SQLite rules, owner D6b; 6 are SQLite internals with no Postgres equivalent), plus 28 marked earlier for SQLite file and URL forms.
- Made portable instead of marked: the two hide-parameters traceback tests (each database's own missing-table error) and, in the QA fix round, the two migration idempotence and round-trip tests (the helper reads the Postgres schema catalogue).
- New `tests/test_data_postgres_differences.py`: id column types and a 2**62 id round trip, and a NUL in text (refused on Postgres with a `DataError`, kept on SQLite).
- `.github/workflows/postgres.yml` (protected, applied by the human as commit `5264497`): a second job, `tests`, runs `uv run --locked pytest` against the `postgres:16.15` service with only the test variable set.
- `README.md`: one paragraph on running the tests on Postgres; it points at `tests/db_target.py` for the variable name, because the README-names test allows only runtime settings.

Branch `issue-192-postgres-test-fixtures`, draft PR #197. Claim: https://github.com/andrew-chung-au/socboard/issues/192#issuecomment-6878506459. CI on `8e9ae54` (the last code head), all success: `socboard verify` 43624235323 and 43624239515, `socboard postgres` 43624235309 and 43624239557. Postgres `tests` job 132536409319: `1680 passed, 378 deselected in 284.86s`, `0 left on the server`. SQLite on the branch alone: 2058 passed (main's 2050 plus 8 new), 0 skipped.

QA record (Standard tier, one QA plus one re-check):
- QA at `0a2672e`: FAIL, one Medium (two migration tests marked "no owner" though their property matters on Postgres): https://github.com/andrew-chung-au/socboard/issues/192#issuecomment-6881818461. Fixed, not ruled away.
- QA re-check of the fix round at `8e9ae54`: PASS, Low findings only: https://github.com/andrew-chung-au/socboard/issues/192#issuecomment-6881981812.

One fix round used.

**What I learned:** the first Postgres run, not reading the tests, is what finds the SQLite-only set: my reading-based list of 81 items was right for those tests but covered under a fifth of the real 380, and a function-by-function comparison of the run's failures with the markers made the set exact.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** the Postgres run waited on a protected workflow commit while the human was away, roughly two hours between the task file (`183d261`) and the human's commit (`5264497`); no local Postgres was installed to work around it, because I asked rather than read "continue" as approval.
**What nearly went wrong or was blocked:** I first left #192 stopped at the human's merge and protected file without saying clearly enough that QA was waiting on the Postgres run; the human asked why it had stopped.
**One proposed change (file, expected effect, measure):** `_docs/planning/deploy-coordination.md` rule 9: let a lane install a small database server into `.scratch/` (named, size-capped, deleted at the end of the issue) when CI is the only other way to run a database test. Expected effect: one CI round per fix instead of a wait on a protected workflow edit. Measure: hours between an issue's first push and its first database test run.

## Launch usage

PM: 1 launch (grooming #192). QA: 2 launches (FAIL at `0a2672e`, PASS at `8e9ae54`). Active time and tool uses were not given by the launch result: unknown.

## Files created or modified

- `tests/db_target.py` (new), `tests/test_data_postgres_differences.py` (new)
- `tests/conftest.py`, `tests/data_support.py`, `tests/backend_support.py`
- `tests/test_audit_api.py`, `tests/test_auth_follow_ups.py`, `tests/test_auth_seed.py`, `tests/test_backend_server.py`, `tests/test_data_audit.py`, `tests/test_data_audit_ddl.py`, `tests/test_data_audit_guard_gaps.py`, `tests/test_data_audit_triggers.py`, `tests/test_data_engine.py`, `tests/test_data_migration_triggers.py`, `tests/test_data_migrations.py`, `tests/test_data_schema.py`, `tests/test_data_server_connect.py`, `tests/test_inventory.py`, `tests/test_journeys.py`, `tests/test_make_run.py`, `tests/test_set_password.py`
- `.github/workflows/postgres.yml` (protected, applied by the human)
- `README.md`
- `_session-summaries/2026-11-14T1809Z-issue-192-orchestrator-postgres-test-fixtures.md` (this file)
- Added and removed on the branch: `_human-tasks/2026-11-14T1413Z-192-postgres-tests.yml`

## Decisions made by the human

- Filed #192 to #195 unlabelled, to be groomed one or two at a time; labelled #192 `approved`.
- The two PM decision questions on #192 (deselect, not skip; the job goes in the existing `postgres.yml`) were answered by the body as written. The human's "recommendations approved" in the session was read as answering those two only, and the Claim says so.
- Applied the protected workflow copy (`5264497`, `515f5dc`).
- The human's later "approve:" message held only pasted push output; it approved nothing specific and was not applied.
- Open, asked at the decision point and not answered yet: whether the lane may commit protected diffs the human approves in chat, and whether a local Postgres (`pgserver`) may be installed into `.scratch/`.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43624235323 and 43624239515 on `8e9ae54`).
- **Test:** `make test` runs the SQLite default. The Postgres run is `uv run --locked pytest` with the test variable set (README, "Tests on Postgres"); a `make test-postgres` target is proposed in the PR as a diff (the `Makefile` is protected).

## Proposed AGENTS.md changes

- If the human accepts the `make test-postgres` target in the PR: a Commands line for it.

## Temporary changes

- `.venv` and frontend packages installed in the sandbox with the uv Python variables set on single commands; not undone (the sandbox is discarded after the session).
- `.scratch/` holds CI logs, the failure lists and the QA reports (git-ignored); the QA reports are posted on the issue.
- AGENTS.md slips in this session: one shell heredoc edit of `tests/db_target.py` and one heredoc for a PR body (both early, not repeated), and multi-step shell loops for CI polling and parsing.

## Interruptions

- The first PM launch for #195 failed on server load and was relaunched; nothing was left behind.

## Unrelated problems noticed but not fixed

- An INSERT into `audit_entries` with `id` set to `None` works on SQLite and fails on Postgres (`null value in column "id"`); the application never sends one. For D6b (#195), which reviews the guard's id rule.

## Follow-ups for the next session

- QA Lows left: the schema query does not list functions (add `pg_proc` rows when D6a's migration `0002` adds a trigger function), column order, identity settings, comments, grants or views; a killed run can leave `socboard_t_` databases on a long-lived server (the README says so); the 28 functions marked before the Postgres run never ran there; some unmarked tests use SQLite URLs on a Postgres run on purpose, so "1680 ran on Postgres" is slightly high; `migrated_database_url` skips the migration if `db_url` made the database first (one test combines them, unaffected).
- #194 (D7) and #193 (D6a) are groomed and labelled and wait for this merge; #195 (D6b) is groomed, unlabelled, and waits for #193 and #107.
