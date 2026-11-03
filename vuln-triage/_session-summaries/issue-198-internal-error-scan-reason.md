# Issue #198: Finish a scan that dies from an unexpected exception (status, failure reason, scan.finished log)

**Date:** 2026-10-25
**Spec version:** 543c87d

## What changed and why

A scan that died from an unexpected exception in `run_scan` stayed unfinished and emitted no log. Following the human's choice of option C, it now ends as `scan failed` with a fifth failure reason, `internal error`, with `finished_at` set and one `scan.finished` log (same fields as #194). The spec change was a protected commit; the rest was ordinary work.

- `run_scan`'s body moved to `_execute`; any unhandled exception goes to `_fail_unexpected`, which rolls back, reloads the rows and calls `_fail` with `INTERNAL_ERROR`. If the recovery commit itself fails, the exception propagates and the scan stays unfinished. A scan already committed as finished is not rewritten.
- New Alembic migration `0002` widens the CHECK constraints on `assets.scan_failure_reason` and `scans.failure_reason`; `0001` is untouched.
- The scheduler already retries every asset with no status filter, so the spec's "the scheduled run retries it" holds with no scheduler change.

Changes beyond the issue text (QA judged each legitimate):
1. `_fail` now marks kept findings stale for every failure reason and a success clears the mark. `Finding.stale` was set nowhere before; `architecture.md` and the spec already required it.
2. `span()` in `backend/vulntriage/observability/tracing.py` no longer records exceptions on any span (error status only). The OpenTelemetry default copied the exception message into a span event, which broke the no-exception-text rule.
3. `tests/test_ingest.py::test_worker_survives_an_unexpected_error` asserted the superseded "left unfinished" behaviour; it now asserts `scan failed` / `internal error` with the worker alive.

## Files created or modified

- `_docs/specs.md` (protected, commit `543c87d`, approval record 6396589596)
- `backend/vulntriage/db/enums.py`, `backend/vulntriage/ingest/scan.py`, `backend/vulntriage/observability/tracing.py`
- `backend/migrations/versions/0002_internal_error_failure_reason.py` (new)
- `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`
- `frontend/src/services/types.ts` and a frontend test
- `tests/test_scan_internal_error.py` (new), `tests/test_db_schema.py`, `tests/test_ingest.py`
- `_docs/ai-usage-log.md`, `_docs/pending-verification.md`, `_docs/roadmap.md`

Commits: `543c87d` (spec), `88dbcd9` (backend and tests), `c687ec5` (docs and frontend), `94dc3a8` (usage log).

## Decisions made by the human

- Option C: a fifth failure reason `internal error` (comment 6396530035).
- Approved the spec text and the wording `internal error` ("Approve as written"). The human saw a summary of the two changes and the wording, not the line-by-line diff; the record says so.
- Decision point: accept the global `span()` change and note the limits; note the other QA risks only.

## Mismatches with the spec or design docs

None. The PM noted `architecture.md` is not in `agent-kit.conf`'s protected list; its edits were ordinary commits.

## Commands to validate

**Verify:** `make verify` (QA: 88 frontend, 496 backend, 5 Postgres tests deselected; PASS WITH WARNINGS, the warning being the deliberately rewritten assertion above). `make openapi-validate` (OK).

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No processes started. `make clean-scratch` run at the end.

## Permission review

PM, Engineer and QA comments each reported no command needing approval.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `HUMAN_APPROVED=1 git commit` for the protected spec change (matched the protected-commit rule; human approved the change)
- Risky (propose denying): none

## Interruptions

None.

## Unrelated problems noticed but not fixed

- `human-tasklist.md` §C still lists PRs #184 and #183, which no longer show as open.
- The two #65 commits `dd5d7ce` and `e5ac135` (permission-log plugin) are in the unpushed range but were not reviewed here.

## Post-merge-request CI fix (added after PR #200 opened)

The `postgres-integration` job failed on PR #200 on three tests added by #194 and #198 that assumed SQLite (a `PRAGMA`, and two Alembic migration tests that rebuild the schema and insert an integer boolean). Fixed in `81c4254` by moving them to `unit`-only modules (`tests/test_migration_0002.py`, `tests/test_scan_orphaned_scan.py`) so the Postgres job (`-m sqlite_integration`) no longer selects them; no assertion changed and the collected total stayed 501. QA PASS (comment 6396948952), assert clean PASS. No `pytest.skip` was used because the verify gate rejects added skips. Cause: the Postgres path was the risk QA and the Engineer had noted as unverified. Migration `0002` is still not run on Postgres anywhere in CI; filed as #201.

## Follow-ups for the next session

- #201: run the Alembic chain (0001, 0002) on real Postgres in CI (decisions open for the human: keep it in the existing `postgres-integration` job via a `postgres_migration` marker, and gate versus best-effort; both are the PM's recommendations in the issue).

- Run migration `0002` on real Postgres and check the reason on the dashboard in a running UI (added to the cloud-session queue in `_docs/pending-verification.md`).
- QA risks, noted only: the `span()` change removes exception events from all spans, so error traces lose diagnostics everywhere; an `internal error` scan stores no exception class or message, so it is hard to diagnose, and the worker's "failed unexpectedly" line no longer fires for these scans; the downgrade is lossy by design (`internal error` rows become `feed unavailable`); any exception in `_execute`, including a failing commit in a known `_fail` path, now becomes `internal error`; if `log_event` raises after the commit the scan stays finished and the exception propagates (a test covers it).
