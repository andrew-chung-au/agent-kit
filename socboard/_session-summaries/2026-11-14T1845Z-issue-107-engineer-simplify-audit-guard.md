# Issue #107: Simplify the audit guard (from #99's review)

**Date:** 2026-11-14T18:45Z (UTC)
**Spec version:** f0d5911

## What changed and why

The Engineer (cloud session, branch `claude/zen-ritchie-oks73l` from `13b8362`) made the audit guard smaller while keeping #99's refusals, except decision 1.

- `socboard/audit_guard.py` (367 to 334 lines): no compile in the id rule (no `statement.compile`, `bind_names`, `construct_params`, no `dialect` parameter, no `sqlalchemy.dialects.sqlite` import, no `except Exception: return True`). The id rule now refuses anything in the `id` slot of `values()` other than None or NULL (so any caller `bindparam`, even executed with None), the `id` of `from_select`, and an execute key `id` or `id_m<n>` (any case) with a non-None value. A column key alias (`Column("id", key="xid")`) counts as `id`. `_ATTACH`, `_COMMENT` and `_strip_comments` are gone; an unrenderable `DDL(...)` is matched on its template alone. The table, trigger and `sqlite_sequence` patterns treat `$` as part of a word.
- `tests/test_data_audit_guard_gaps.py` (893 to 891 lines): tests for the removed rules deleted, the decision-1 tests rewritten to expect a refusal, new tests for the key alias, `$`, the unrenderable `DDL`, the mistyped execute key and the comment/string-literal open limit.
- `_docs/decisions/2026-11-12T0834Z-data-model.md`: a #107 note beside #99's, and the Trade-offs bullet keeps only the open limits and the new id rule with its cost.

Every kept rule was removed one at a time in a scratch copy (`.scratch/mutate107.py`); each removal fails at least one named test, listed in the `Engineer:` comment on #107, except the `Session` `do_orm_execute` hook: every Session route also reaches the `Engine` listener, so no test fails without it. Three #11/#99 rules (REPLACE prefix, on-conflict-do-update, `DropIndex` by the columns' table) had no test of their own until #107 added one, because the id rule or the index-name rule caught every existing case first.

After QA (comment 6882824631): `_PARAMETER_KEY` lacked `re.DOTALL`, so an execute key containing a newline crashed the guard with `TypeError`; fixed in `f5e4298`, with a test (`test_the_guard_function_reads_the_values_bound_for_id_in_every_parameter_row`) that fails without it. Test file now 892 lines, guard 334.

After the second QA FAIL (comment 6883108572): the execute-key check tested only the key with an `_m<n>` suffix stripped, so a column key alias ending in `_m<n>` (`x_m1`) let any id through. Fixed in `d290568` (the raw key is tested too); `test_an_id_under_a_column_key_alias_is_refused` is now parametrized over `xid`, `x_m1`, `id_x_m0`, `rowid_m12`. Test file 892 lines, guard 336.

**What I learned:** in SQLAlchemy 2.1 `values(id=None)` stores a `BindParameter`, not `Null`, so a plain None and a caller's `bindparam` differ only by `BindParameter._is_crud`.

## Reflection

### Engineer

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `socboard/audit_guard.py`
- `tests/test_data_audit_guard_gaps.py`
- `_docs/decisions/2026-11-12T0834Z-data-model.md`
- `_session-summaries/2026-11-14T1845Z-issue-107-engineer-simplify-audit-guard.md`

## Decisions made by the human

The four grooming decisions in #107's body, approved with the `approved` label (body hash `fe4502a23033ccf2109601ea5a2b7d4f4e9cbd10b19c3deb1bc315c5741d15eb`). None asked during implementation.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify BASE=13b8362`
**Test (one file):** `make test-one FILE=tests/test_data_audit_guard_gaps.py`

## Proposed AGENTS.md changes

none

## Temporary changes

`make install` created `.venv` and `frontend/node_modules` (needed by the task; left in place, git-ignored). Scratch files in `.scratch/` (`probe107.py`, `mutate107.py`, `mutate107.out`, the issue dump and comment draft); the mutant copies under `.scratch/mutants/` were deleted by the script. No system changes, no servers started.

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- The `Session` hook in `socboard/audit_guard.py` makes no test fail when removed (the `Engine` listener catches the same routes). Removing it or adding a test that only it can pass is a decision for the human; not done here (out of scope: #107 removes only the listed rules).
- #195 (Postgres review of the guard) can start: the guard no longer compiles and names no dialect.
- The guard now reads one more private SQLAlchemy attribute, `BindParameter._is_crud` (fail closed if it disappears: `values(id=None)` would then be refused and `test_an_insert_with_no_id_or_a_none_id_is_not_refused` would fail).
