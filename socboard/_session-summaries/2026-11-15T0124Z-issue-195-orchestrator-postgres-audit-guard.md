# Issue #195: Review the audit guard for Postgres after its simplification

**Date:** 2026-11-15T01:24Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The audit guard (`socboard/audit_guard.py`), as #107 left it, is reviewed for Postgres: for each Postgres way to defeat the append-only trail, the tests show whether the guard or the database (D6a's triggers and owner rules) refuses it. No guard rule was added or changed.
- `tests/test_data_audit_guard_postgres.py` (new): 31 Design-table statements offline, as `DDL(...)` and as `text()`; live on Postgres, the six `DDL(...)` forms refused on a connection and through `Session.execute` with the triggers and rows unchanged, raw SQL reaching the database, the application role unable to move the id sequence, COPY firing the insert trigger, the planted-id limit, and an ORM flush not reaching the Session hook.
- `socboard/audit_guard.py`: docstring only.
- `tests/db_target.py`, `tests/test_data_audit_guard_gaps.py`: marker reasons only. All 28 guard tests marked with owner D6b still fail on Postgres for SQLite reasons of their own (`sqlite_sequence`, `sqlite_master`, a NULL id, SQLite trigger syntax), so each keeps the marker with a reason naming that part.
- One added line in `_docs/decisions/2026-11-12T0834Z-data-model.md` (the guard's open limits on Postgres); new decision record `_docs/decisions/2026-11-15T0052Z-postgres-audit-guard.md` (proposed) and its index row.

Branch `issue-195-postgres-audit-guard`, draft PR #219. Claim: https://github.com/andrew-chung-au/socboard/issues/195#issuecomment-6886827339 (records the human's ruling: the offline criterion calls `refused_statement(DDL(...))` with no dialect, since #107 removed the parameter). Engineer inventory: https://github.com/andrew-chung-au/socboard/issues/195#issuecomment-6887038420. CI on `f3e4763`, all success: `socboard postgres` push run 43661260096 (tests job 132650872210: 2045 passed, 348 deselected, 0 databases and 0 roles left), `socboard verify` pull_request run 43661328064 (2307 passed).

QA record (Heavy):
- QA 1 at `f3e4763`: PASS, Lows only: https://github.com/andrew-chung-au/socboard/issues/195#issuecomment-6887234151.
- Independent second QA at `f3e4763` (fresh subagent, issue body and diff only): PASS, Lows only: https://github.com/andrew-chung-au/socboard/issues/195#issuecomment-6887265617.

No fix round.

**What I learned:** `ALTER TABLE ... DISABLE TRIGGER ALL` needs a superuser on a table with foreign keys, because it also disables the foreign-key system triggers; the owner can still disable its own triggers with `DISABLE TRIGGER USER`.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** none to speak of; the local Postgres made each check a matter of seconds, and the one probe that switched the markers off answered the "existing tests" criterion in one run.
**What nearly went wrong or was blocked:** the approved body asked for a `dialect` argument that #107 had removed; I asked the human before claiming instead of reading it my own way.
**One proposed change (file, expected effect, measure):** none beyond the one in #193's summary.

## Launch usage

QA: 2 launches (QA 1 PASS, second QA PASS). Active time and tool uses: unknown.

## Files created or modified

- `tests/test_data_audit_guard_postgres.py` (new)
- `socboard/audit_guard.py` (docstring), `tests/db_target.py`, `tests/test_data_audit_guard_gaps.py` (marker lines)
- `_docs/decisions/2026-11-12T0834Z-data-model.md` (one added line), `_docs/decisions/2026-11-15T0052Z-postgres-audit-guard.md` (new), `_docs/index.md` (one row)
- `_session-summaries/2026-11-15T0124Z-issue-195-orchestrator-postgres-audit-guard.md` (this file)

## Decisions made by the human

- Labelled #195 `approved`. #107 merged first (PR #217), so the review is of the simplified guard.
- "recommendation approved" (option A): the offline criterion is read without a dialect argument; the issue body is not edited.
- The PM's two remaining questions defaulted to option 1 (no new Postgres guard rule; a planted future id is a recorded limit).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43661328064).
- **Postgres tests:** the CI `tests` job.

## Proposed AGENTS.md changes

none

## Temporary changes

- `.scratch/pgserver` and `.scratch/pgdata` (the throwaway local Postgres): to be deleted now that the lane's last issue is done.

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- QA Lows: the data-model line's "a later `append_audit` that draws a planted id is refused once" is true (QA probed it) but has no test; replacing a trigger function as the owner is not tested live; `DROP SCHEMA public CASCADE` and `DROP OWNED` are further owner-only routes the guard does not refuse, not listed in the inventory; the `DISABLE TRIGGER ALL` test asserts only a database error; `tests/db_target.py` is outside the Constraints list (marker reasons only).
- #203 (`make test-postgres`) and #205 (migration URL) are filed and unlabelled.
