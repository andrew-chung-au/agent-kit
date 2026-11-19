# Issue #214: The audit guard does not refuse a lambda_stmt INSERT with an explicit id

**Date:** 2026-11-15T09:25Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The audit guard (`socboard/audit_guard.py`) now sees through SQLAlchemy lambda statements: `refused_statement` first replaces a lambda (`LambdaElement`, which covers `StatementLambdaElement`, `LinkedLambdaElement` and `DeferredLambdaElement`, and `NullLambdaStatement`, which `.spoil()` returns) by the statement it builds, through the private `_resolved`, in a bounded loop, and then applies every existing rule. A lambda it cannot read is refused (a private sentinel marks it, so `refused_statement(None)` is unchanged). A closure-captured `None` id is refused like a caller's `bindparam`; a literal `id=None` and an omitted id pass. Tests in a new #214 section of `tests/test_data_audit_guard_gaps.py`, including a canary for the private attribute; no existing test or assertion changed, no skip or xfail. The approved Decision record is committed as `_docs/decisions/2026-11-15T0846Z-audit-guard-lambda-stmt.md` with its index row, and the data-model record has one added note. No protected file.

Branch `issue-214-lambda-stmt-guard`, draft PR #245. Claim: https://github.com/andrew-chung-au/socboard/issues/214#issuecomment-6891877840 (records the human's approval of the Decision record and of PM questions 1 and 2 through it). Engineer: https://github.com/andrew-chung-au/socboard/issues/214#issuecomment-6891969468; fix round: https://github.com/andrew-chung-au/socboard/issues/214#issuecomment-6892169524. CI on `89d7653`, all success: `socboard verify` pull_request run 43698190437, `socboard postgres` run 43698190397 (Postgres 16 tests job: 2198 passed), image 43698190399, compose 43698190398.

QA record (Heavy):
- QA 1 at `5f56554`: FAIL, one High (a `.spoil()` lambda got an explicit id and a `sqlite_sequence` write past the guard) and one Low: https://github.com/andrew-chung-au/socboard/issues/214#issuecomment-6892088913.
- Fix round (one Engineer round), re-check of the changed lines at `89d7653` by one fresh QA: PASS, Lows only: https://github.com/andrew-chung-au/socboard/issues/214#issuecomment-6892206926.
- Independent second QA at `89d7653` (fresh subagent, issue body and diff only): PASS, Lows only: https://github.com/andrew-chung-au/socboard/issues/214#issuecomment-6892306954.

**What I learned:** `lambda_stmt(...).spoil()` returns a `NullLambdaStatement`, which is not a `LambdaElement`; a type check against one SQLAlchemy class missed it, and only an adversarial QA probe found it.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** one fix round for the spoiled lambda (QA 1 FAIL at `5f56554`).
**What nearly went wrong or was blocked:** the first Engineer report said no other lambda wrapper exists; trusting it would have shipped a High bypass.
**One proposed change (file, expected effect, measure):** in the Engineer launch for guard issues, require listing every subclass of the type the guard checks in the installed library and one test per subclass (expected: the class of miss in F-214-1 is found before QA; measure: guard issues that need a fix round for a missed subclass).

## Launch usage

Engineer: 2 launches (implementation, fix round). QA: 3 launches (QA 1 FAIL, fix re-check PASS, independent second QA PASS). Active time and tool uses: unknown.

## Files created or modified

- `socboard/audit_guard.py`
- `tests/test_data_audit_guard_gaps.py`
- `_docs/decisions/2026-11-12T0834Z-data-model.md` (one added note), `_docs/decisions/2026-11-15T0846Z-audit-guard-lambda-stmt.md` (new), `_docs/index.md` (one row)
- `_docs/records/findings/214.json`
- `_session-summaries/2026-11-15T0925Z-issue-214-orchestrator-lambda-stmt-guard.md` (this file)

## Decisions made by the human

- Labelled #214 `approved`; approved its `## Decision record` by name in this session ("approve descion record"), which settles PM questions 1 (unwrap and refuse) and 2 (refuse a closure-captured `None` id); question 3 follows the human's queue (#214 before #215).
- The committed record's Decision line names the lambda classes covered (added in the fix round); its meaning is the approved one. Flagged to the human at the decision point.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43698190437).
- **Guard tests:** `make test-one FILE=tests/test_data_audit_guard_gaps.py`.
- **Postgres:** the CI `socboard postgres` run 43698190397.

## Proposed AGENTS.md changes

none

## Temporary changes

none (QA's and the Engineer's temporary rule removals were restored with `git restore`; `make assert-clean` passed after each)

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-214-1: A spoiled lambda statement is a different class from the one the first unwrap checked, so it reached SQLite with an explicit id or a sequence write; fixed in 89d7653 and listed so the class of miss is on record.
- F-214-2: A null lambda whose private resolved attribute is overwritten by hand with None is not refused; it cannot be built through the public API and cannot execute.
- F-214-3: The new lambda bullet in the audit guard's module docstring sits before the existing Not covered paragraph, so that paragraph now reads as part of the lambda bullet.
- F-214-4: An insert into the audit table with an explicit id nested inside a CTE is not refused by the guard; SQLite does not accept DML in a CTE, so it matters on Postgres only, and it predates lambdas.
- F-214-5: Over-refusal of harmless lambda statements was probed by both QA launches but only some of those cases are pinned by tests in the repository.

## Follow-ups for the next session

- F-214-4 (CTE-nested audit INSERT on Postgres): the human decides whether to file it as an issue; if filed, add it to the supporting list in `_docs/planning/roadmap-1-core.md`.
- #215 (Heavy, approved) is next and touches the same files; it starts only after #214 merges.
