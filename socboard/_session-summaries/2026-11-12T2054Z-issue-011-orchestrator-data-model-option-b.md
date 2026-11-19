# Issue #11: Data model and migrations (option B: database-enforced append-only audit)

**Date:** 2026-11-12T20:54Z (UTC)
**Spec version:** 185bb50 on this branch (`main` is at 36d9ad7, a wording change merged after the branch was cut; the branch does not touch the spec)

## What changed and why

Tier: Heavy (from the PM proposal; no tier label). The fifth control issue, so epoch batch 1 lands after this closes. This session picked up from `_session-summaries/2026-11-12T1136Z-planning-orchestrator-handoff.md`.

- **Option B, as the human ruled:** migration `0001` creates three SQLite triggers on `audit_entries` (`audit_entries_no_update`, `audit_entries_no_delete`, `audit_entries_no_reuse_id`), each with fixed text, and the downgrade drops them first. The application guard (`socboard/audit_guard.py`) stays as a second layer and is the only DDL guard. Its DDL check now accepts any object with a string name, which closes M3 (`DropTable(table(...))`), and it refuses `DDL` that names a trigger. Raw-SQL DDL that drops a trigger is a recorded, tested limit.
- **Outside advice (G1 to G5),** tested in the dev container on SQLite 3.46.1 and re-checked here on 3.40.0, changed the body twice with the human's confirmation (hashes `2f7bf5a7…` → `2d161605…`):
  - G1: SQLite gives `NEW.id` the value -1 in a BEFORE INSERT with no id, so trigger (c) is `WHEN EXISTS (…)` and `audit_entries` has `CHECK id >= 1` (`ck_audit_entries_id_positive`).
  - G2: the tests expect `IntegrityError` carrying the fixed message.
  - G3: an Alembic batch rebuild of `audit_entries` drops the triggers and `AUTOINCREMENT`; the decision record says so, and the tests fail with a hint.
  - G4: a test proves the guard-off fixture.
  - G5: the Postgres wording in Out of scope.
- **CI was the test loop.**
  - At `7e5d873`: 4 failed, 527 passed. The causes were a string-built `DROP TRIGGER`, and `prefix_with("REPLACE")` compiling to invalid `INSERT REPLACE INTO`.
  - At `cf172ab`: the pull-request run 43215961360 gave 541 passed, frontend 157 passed, `Assertion lines: 286 added, 0 removed` and `VERIFY: PASS`. The push run 43215950737 gave `PASS WITH WARNINGS`; the three warned lines were rewritten in this round's own new test file, each to an equal or stricter check, with the reasons in the Engineer's comment.
- **QA:**
  - First-launch re-check: PASS at `cf172ab` (comment 6823445361).
  - Fresh second launch: Claude Code in the dev container, PASS at `cf172ab` (comment 6824588180). It ran 51 routes ×2 (guard on and off) and none changed a row; it also ran a real batch rebuild, and `make verify BASE=origin/main` gave PASS.
  - `make assert-clean` passed after each launch.
- **Exception to "existing tests pass unmodified":** commit `37af68a` changed two tests in `tests/test_data_audit.py` (`test_an_id_is_never_reused` and the raw-SQL test). Both asserted that raw SQL could change `audit_entries`, which option B makes false; they now expect the database's refusal, which is stricter. The human chose to record this here and in the Close comment rather than change the body again.

**What I learned:** outside advice that tests a design on the real engine before the Engineer builds it found two defects (the -1 id and the rebuild) that three code reviews had not. Asking for it before the build, not after, would have saved a round.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6823346581, unchanged:

- Slow: no test could run, so each change was checked by reading against SQLite and SQLAlchemy semantics. My first guess about which REPLACE form was invalid came from the CI failure ids, which named the single-prefix route, not the two-prefix one.
- Unclear: "existing tests pass unmodified" against two raw-SQL tests that option B makes false; the issue did not say what to do. The note to compile the two-prefix form assumed a runnable Python.
- Went well: the CI log names each failing test, so each fix could be kept to one small commit. A script comparing the record with the body caught drift in the decision record.

### QA

First-launch re-check: unknown (role not asked; its comment has no Reflection block).

Second launch, from comment 6824588180, unchanged:

Reflection:
1. What slowed me: the Orchestrator comments came back as one 30 KB dump, so I needed a second filtered read; and two of my `lambda_stmt` probes broke on my own closure (an `InvalidRequestError` in the first log), so I had to rerun them.
2. What nearly went wrong: the first `lambda_stmt` insert results looked like refusals but were my probe's own error; I almost counted them as covered before checking the error class.
3. Proposed change: in `_docs/agent-kit/team/qa-engineer.md`, under Code review, add "a probe result counts only when the error class and message are the expected refusal". Expected effect: probe-construction errors are no longer counted as refusals. Measure: how often a later QA re-check or orchestrator query finds a probe line whose error was the probe's own.

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). This session ran Engineer ×2, PM ×3 (body draft, hash re-record, follow-up filing) and QA ×1 (first-launch re-check). The second QA launch was run by the human in Claude Code in the dev container. The outside advice (G1 to G5) was run by the human in a separate dev-container session.

## Files created or modified

- **On `issue-11-data-model` this session:**
  - `socboard/migrations/versions/0001_initial_schema.py`, `socboard/models.py`, `socboard/audit_guard.py`
  - `tests/test_data_audit.py`, `tests/test_data_audit_triggers.py`, `tests/test_data_audit_ddl.py`, `tests/test_data_migration_triggers.py`
  - `_docs/decisions/2026-11-12T0834Z-data-model.md`, `_docs/index.md`
  - `_docs/planning/roadmap-1-core.md` (#99 and #100 placed)
  - This file.
- **Issue #11:** body updated (hash `2d161605…`), with Claim, Confirm, Engineer, QA and handover comments.
- **Filed:** #99 and #100.

## Decisions made by the human

- The human confirmed re-reading option B's decision record, then confirmed the body change adopting G1 to G5 (2026-11-12).
- At the decision point, "as recommended":
  - The five Low second-launch findings (L1 explicit max id, L2 templated `DDL`, L3 `DropIndex` on `table()`, L4 `PRAGMA ignore_check_constraints`/`writable_schema`, L5 docstring) go to follow-up #99, before #14; #11 closes as is.
  - The two adapted tests are recorded in the summary and the Close comment, with no further body change.
  - Sweep 4 runs after #11 closes, before epoch batch 1.
  - CI's unpinned Python (3.14 vs the project's 3.12) is filed as #100.

## Mismatches with the spec or design docs

- The decision record's "what can still bypass it" does not list L1 to L4; #99 adds them.
- The body's "existing tests pass unmodified" has the recorded exception above.

## Commands to validate

- **Verify:** `make verify` (CI run 43215961360: VERIFY: PASS; the second QA launch ran `make verify BASE=origin/main`: VERIFY: PASS).
- **Contract check:** `make contract-check` (second QA launch: `openapi.yaml: OK`).

## Proposed AGENTS.md changes

none (the Migrate and New migration lines were approved and committed in the earlier round).

## Temporary changes

- No processes started and no system changes.
- `make clean-scratch`: run at the end of this session, after the follow-up drafts were filed and the comments posted.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- In Kiro Web, `uv` cannot create its Python folder (read-only file system), so no Python test can run here; CI and the dev container are the only test loops.

## Follow-ups for the next session

1. The human merges PR #96 (mark it ready for review first; it is a draft). Then the orchestrator posts the Close comment (with `QA PASS commit: cf172ab`, the merge commit, the Verify line, this file's path and the adapted-tests note) and runs `make issue-close N=11`.
2. Sweep 4 (due: 7 closed since 2026-11-12; candidates in `_docs/planning/sweep-4-candidates.md`, PR #97), then epoch batch 1 (`_docs/planning/epoch-batch-1/README.md`).
3. Then #12, #13 and #14 (already re-groomed); #99 lands before #14. Notes to route when they are next groomed:
   - routes must not map every `IntegrityError` to 409 (#13 on);
   - a refused flush poisons the session, but a refused `session.execute` does not, so #16 and #17 roll back rather than commit after a refusal;
   - #14 never uses `INSERT OR IGNORE`/`ON CONFLICT DO NOTHING` on `audit_entries`;
   - a migration that rebuilds `audit_entries` re-creates the triggers and `AUTOINCREMENT`;
   - the earlier notes in the hand-off summary still stand (`render_as_batch`, `create_db_engine`, `allow_schema_changes()` callers, the Deploy items).
4. Sweep evidence: the second QA's proposal (a probe counts only with the expected error class and message).
