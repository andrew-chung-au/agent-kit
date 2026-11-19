# Issue #143: Run the backend and migrations on Postgres, chosen by the database URL (driver, schema, CI job)

**Date:** 2026-11-14T13:24Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

With `SOCBOARD_DATABASE_URL` set to a Postgres URL, `make migrate` and `make seed` run, the backend starts and answers health and login, and a CI job shows it against a Postgres 16.15 service. SQLite stays the default and its output is unchanged.

- `pyproject.toml`, `uv.lock`: `psycopg[binary]>=3.2` (psycopg 3.3.9), added after the human approved the diff.
- `socboard/migrations/versions/0001_initial_schema.py`: the three audit triggers and their drops only on SQLite (`_is_sqlite()`). `sqlite_autoincrement` is not guarded: SQLAlchemy ignores a `sqlite_` table option on other dialects, and a test shows it. On Postgres the audit ids are `BIGSERIAL`. The append-only rule on Postgres is D6a, not here.
- `socboard/database.py`: on a non-SQLite engine a `do_connect` hook replaces a failed connection with `DatabaseConnectError` (a SQLAlchemy error), fixed text plus one reason word from a fixed list (authentication, database-missing, refused, timeout, unknown), no chained driver error. The reason is found by matching the driver's message, which is never printed, because psycopg 3 sets no SQLSTATE while connecting. #104's SQLite-only hook in `socboard/sessions.py` is unchanged.
- `.github/workflows/postgres.yml` (protected, applied by the human): migrate twice, bigint ids and no trigger, seed twice, health and login, and three no-leak steps (refused login user, missing database for the real user, refused connection). Throwaway credentials, no repository secret.
- `scripts/postgres_no_leak.sh`: the shared no-leak check, with optional `EXPECT_REASON`.
- `tests/test_data_migration_dialects.py`, `tests/test_data_server_connect.py` (new), `README.md` (one paragraph), the decision record `_docs/decisions/2026-11-14T1120Z-postgres-driver.md` (status `proposed`) and its index row.

Worked by two sessions of the Postgres lane, Heavy tier, no Engineer launch. Branch `issue-143-postgres-driver`, draft PR #181. Claims: https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6876119906 (first session, released in https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877163861) and https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877302842 (this session). Final head is the commit that adds this file; CI runs on `d599440` (the last code and workflow head, including the merge of `main`): `socboard verify` 43598327348 and 43598333711, `socboard postgres` 43598327413 and 43598333762, all success. The pull_request verify run: 2050 Python tests, 209 frontend tests.

QA record:
- QA 1 at `d9e61f1`: FAIL (M1 and L1 to L4): https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6876535198. The human ruled M1 option A and asked for L2 to L4: https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6876830476.
- QA re-check of round 1 at `f23366f`: FAIL, one new Medium (the SQLSTATE is always "none", so the message could not tell a bad password from a missing database): https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877371892. The human approved option A: https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877479335.
- QA re-check of round 2 at `d273ced`: PASS, Low findings only: https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877582965.
- Independent second QA (fresh subagent, issue body and diff only) at `d599440`: FAIL, one Medium (the no-leak script is outside the issue's Constraints file list): https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877841908. The human ruled option B: https://github.com/andrew-chung-au/socboard/issues/143#issuecomment-6877933159. No QA run followed the ruling, because the ruling changes no code; the second QA's Medium ships under the human's ruling (delivery-pace item 7).

Two fix rounds were used; no third round was started.

**What I learned:** the Postgres driver sets no SQLSTATE and always raises `OperationalError` when a connection fails, so the first fix for "name the error class and SQLSTATE" gave the same text for every cause. Only the real Postgres job showed it (`SQLSTATE none` in both no-leak steps); the unit test had built an error by hand that the driver never raises. A test that builds the driver's error is not evidence of what the driver does.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** the task-file route for a protected workflow change cost three CI rounds in this session: a patch file with a blank context line failed the whitespace check on `0035028` (verify run 43596553982) and had to be replaced by a full copy.
**What nearly went wrong or was blocked:** `make install` failed at first because uv tried to download Python into a read-only directory; it worked with `UV_PYTHON`, `UV_PYTHON_PREFERENCE=only-system` and `UV_PYTHON_DOWNLOADS=never` set on the command line.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/templates/human-task.md`: say that a protected-file change is given as a full copy of the file, never a patch, because `git diff --check` rejects the blank context lines of a patch. It would remove one CI round per protected workflow change; measure it by counting verify failures on whitespace in task-file commits.

## Launch usage

QA: 3 launches (round-1 re-check FAIL, round-2 re-check PASS, independent second QA FAIL). Active time and tool uses were not given by the launch result: unknown.

## Files created or modified

- `pyproject.toml`, `uv.lock` (protected, human-approved)
- `.github/workflows/postgres.yml` (protected, applied by the human)
- `socboard/database.py`, `socboard/migrations/versions/0001_initial_schema.py`
- `scripts/postgres_no_leak.sh`
- `tests/test_data_migration_dialects.py` (new), `tests/test_data_server_connect.py` (new)
- `README.md`, `_docs/decisions/2026-11-14T1120Z-postgres-driver.md`, `_docs/index.md`
- `_session-summaries/2026-11-14T1324Z-issue-143-orchestrator-postgres-driver.md` (this file)
- Added and removed on the branch: the `_human-tasks/` copies of the workflow (two files; both deleted).

## Decisions made by the human

- 2026-11-13/14: applied the `approved` label; waived the D0 dependency (the dev-container sitting) for this issue; approved the exact `pyproject.toml` and `uv.lock` diff.
- M1 of QA 1: option A. The "no connect hook" in criterion 4 means #104's hook; the new `do_connect` hook on non-SQLite engines is allowed. The issue body was not edited. L1: no change. L2 to L4: fix.
- Re-check Medium (SQLSTATE always "none"): option A, the fixed reason list.
- Second QA's Medium (the script outside Constraints): option B. The script is in scope, and the human adds `scripts/postgres_no_leak.sh` to `PROTECTED` in `agent-kit.conf`.
- Applied the workflow change of round 2 (the `EXPECT_REASON` lines and the refused step).

## Mismatches with the spec or design docs

- Criterion 4 says "no connect hook is attached" on Postgres; a `do_connect` hook is attached on every non-SQLite engine. Ruled by the human (M1, option A); the issue body is unchanged.
- The issue's Decision record says the SQLite-only parts are "guarded by dialect"; `sqlite_autoincrement` is not, because SQLAlchemy ignores it outside SQLite. Disclosed in the decision record; QA 1 L1, no change.

## Commands to validate

- **Verify:** `make verify` (CI runs 43598327348 and 43598333711 on `d599440`).
- **Test:** in this sandbox `make test` passed on the branch with no Postgres: Python 1918 on the branch alone before the merge of `main` and 2050 after it, frontend 208. The 20 runs of `tests/test_journeys.py::test_journey_two_triage_to_audit` all passed here.
- **Migrate and Seed on Postgres:** run by the `socboard postgres` job (twice each, nothing changes the second time). Not run on a local Postgres: the final local test with the D0 dev-container database (PR #179) is still to do.

## Proposed AGENTS.md changes

none

## Temporary changes

- `.venv` and the frontend packages installed in the sandbox with `make install`; the uv Python variables were set on single commands only. Not undone: the sandbox is discarded after the session.
- `.scratch/` holds QA reports, CI logs and the new workflow copy (git-ignored). Not cleaned: `make clean-scratch` deletes everything in it, and the QA reports are posted on the issue.
- Twenty log files in `/tmp` from the 20-run loop (outside the folder, against AGENTS.md); deleted at once.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `tests/test_journeys.py::test_journey_two_triage_to_audit` failed once on the human's machine with a 401 and never in 20 runs here or in CI. The earlier guess (a clock jump against the token's expiry check at `socboard/tokens.py` line 103) is not reproduced and not confirmed. No issue filed.
- `scripts/postgres_no_leak.sh` passes with an empty word list. Both workflow steps pass words.

## Follow-ups for the next session

- Low findings left, none fixed: the `timeout` phrases and `no password supplied` are tested only with made-up messages (an unmatched message gives `unknown`); the schema match with SQLite is shown by constraint and index names plus a repeatable migration, with no comparison of column types on a real Postgres; two new tests make real connection attempts and depend on the resolver; the decision record carries claims from the first session (the push-check image, `docker manifest inspect` at the D0 sitting) that the second QA could not verify; `str(error)` is called inside the `except` block of the hook (no psycopg error raises from it).
- The human adds `scripts/postgres_no_leak.sh` to `PROTECTED` in `agent-kit.conf` (ruling B).
- The decision record is `proposed`; only the human sets `approved`.
- D5b to D7 drafts (branch `postgres-lane-drafts`): the D5b test run keeps the autouse `login_limits_raised` fixture in `tests/conftest.py` (from #178 and #183); D6a's note that D0 is merged is now true; `DatabaseConnectError` is now a SQLAlchemy error, which #112's lock-timeout mapping will see.
- Final local test with the D0 dev-container Postgres (PR #179).
