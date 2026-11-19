# Issue #215: The audit guard's Session do_orm_execute hook has no test that only it can fail

**Date:** 2026-11-15T11:45Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

A new parametrised test in `tests/test_data_audit_guard_gaps.py` shows what only the `Session` `do_orm_execute` hook does: update, delete, an explicit-id insert and `DROP TABLE audit_entries` through `Session.execute` are refused with no pool checkout, no `begin` and no transaction, with the audit rows (and on SQLite `sqlite_sequence`) unchanged; a control through `session.connection().execute(...)` shows one checkout. With only the hook removed the test fails on its checkout assertion; with only the `Engine` listener removed it passes. One sentence added to item 2 of the module docstring of `socboard/audit_guard.py`. No change to `refused_statement`, the listeners or their registration; tests are additions only; no skip or xfail; no protected file.

Branch `issue-215-session-hook-test`, draft PR #249. Claim: https://github.com/andrew-chung-au/socboard/issues/215#issuecomment-6893642917. Engineer: https://github.com/andrew-chung-au/socboard/issues/215#issuecomment-6893714436. QA PASS at `e086a9c`, Lows only: https://github.com/andrew-chung-au/socboard/issues/215#issuecomment-6893816530. CI on `e086a9c`, all success: `socboard verify` pull_request run 43709753772, `socboard postgres` run 43709753813 (its tests job ran 138 tests of the gaps file on Postgres, which includes the new ones), image 43709753776, compose 43709753733.

**What I learned:** a QA subagent read a steering note meant for the Engineer subagent as its own history and stopped; the relaunch had to say plainly that it was a fresh launch.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** one wasted QA launch that stopped before reviewing because of the steering note.
**What nearly went wrong or was blocked:** the tier: the human first called #215 Heavy, the PM proposed Standard; I asked before claiming and the human approved Standard.
**One proposed change (file, expected effect, measure):** in QA launch messages, add one line saying the subagent is a fresh launch and that steering notes in its context are addressed to other agents (expected: no QA launch stops for independence by mistake; measure: QA launches that stop before reviewing).

## Launch usage

Engineer: 1 launch. QA: 2 launches (the first stopped before reviewing; the relaunch PASS). Active time and tool uses: unknown.

## Files created or modified

- `tests/test_data_audit_guard_gaps.py`
- `socboard/audit_guard.py` (module docstring, item 2)
- `_docs/records/findings/215.json`
- `_session-summaries/2026-11-15T1145Z-issue-215-orchestrator-session-hook-test.md` (this file)

## Decisions made by the human

- Labelled #215 `approved`; approved Standard (the orchestrator's recommendation) over Heavy on 2026-11-15; PM decision question 1 stays at option A (keep the hook).
- Asked the session to continue as far as it could while away; the merge waits for the human.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43709753772).
- **Guard tests:** `make test-one FILE=tests/test_data_audit_guard_gaps.py`.

## Proposed AGENTS.md changes

none

## Temporary changes

none (the rule-removal plugins and runners are under `.scratch/`, not committed)

## Interruptions

- The human went away mid-issue and asked the session to continue.

## Unrelated problems noticed but not fixed

- F-215-1: The new test checks the sequence table through a dialect branch in a helper, not the SQLite-only marker its neighbours use, so the check is missing from the marker count.
- F-215-2: The control test through the session's own connection checks the pool checkout count only, not the begin count.
- F-215-3: An ORM select built from an update or delete statement with returning is refused by neither guard layer, only by the SQLite trigger; the PM noted it while grooming and it is not filed.
- F-215-4: The Session hook alone misses an explicit id passed under a mapper attribute name other than id, so it is not a full second layer; the new docstring sentence stays true because the Engine listener refuses it.

## Follow-ups for the next session

- F-215-3 and F-214-4 (two guard routes, one Postgres-only): the human decides whether to file them; if filed, place them in the supporting list in `_docs/planning/roadmap-1-core.md`.
- #237 (D20): prepare only; groom when the human asks, after #233, #235 and #236 are merged.
