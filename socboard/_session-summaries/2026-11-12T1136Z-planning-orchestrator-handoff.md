# Planning: hand-off to the next orchestrator session

**Date:** 2026-11-12T11:36Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

A long orchestrator session (2026-11-11 to 2026-11-12) closed #9, #10, #74, #60, #86, #62 and #42 (not planned) and is ending mid-#11 because its context is full. This file is the hand-off: read it first in the next session, with `AGENTS.md`, `.kiro/steering/*.md` and `_docs/planning/roadmap-1-core.md`.

### Where #11 stands (Heavy, the current Core issue)
- Branch `issue-11-data-model` at `1f85646`; draft PR #96 (do not merge until both QA launches pass).
- Body hash `2f7bf5a77a6599944b19146fbc55b285f0e781166bedc1e4ade1e070eb8e902d`, recorded (Confirm and PM re-record posted).
- The human ruled option B (https://github.com/andrew-chung-au/socboard/issues/11#issuecomment-6822299253): SQLite triggers on `audit_entries` enforce append-only (no UPDATE, no DELETE, no INSERT that reuses an id); the application guard stays as a second layer and is the DDL guard (fold in M3: `DropTable(table("audit_entries"))` refused); raw-SQL DDL that drops a trigger is a recorded, tested limit.
- **Waiting on the human:** re-read the changed `## Decision record` on #11 and confirm.
- **Then:** the Engineer implements the triggers and tests (Kiro Web, CI as the loop; push, then read the PR's CI run); a first-launch QA re-check of the change; then a fresh second launch by Claude Code in a NEW session in the dev container (handover comments on #11 show the layout; `.kiro/steering/delivery-pace.md` item 6 once PR #97 merges).
- QA history on #11: first launch PASS at `b14770d`; re-checks PASS at `7b6e505` and `1f85646`; second launches FAIL at `7b6e505` (M1 aliases and case variants), a reused-session PASS at `1f85646` (set aside), FAIL at `1f85646` (M2 `lambda_stmt`, M3 `table()`), which led to option B.
- Low notes to route when the issues are groomed: `allow_schema_changes()` callers and the AST alias gap (#16, #17); engines must come from `create_db_engine` (#16, #17); `render_as_batch` for SQLite (#12 or #13, whichever first changes the schema); the decision record should name `exec_driver_sql` and the DBAPI cursor with `text()` (wording); Postgres CTE DML, READ COMMITTED pinning, the driver-message check (Deploy); the misleading "not a valid URL" text for a missing driver (Deploy task 4).

### After #11 closes
- #11 is the fifth control issue, so **epoch batch 1** lands next, as one batch: #63 first, the kit edits (items 1 to 5, 8), #65 and #49 together, items 6 and 6b (contract-check in verify), #80, then item 7 (`KIT_VERSION` 1.10+socboard.2) and a new epoch-start record. Drafts, rulings and patches: `_docs/planning/epoch-batch-1/README.md`. Each protected diff needs the human's approval at landing.
- Then **#12, #13, #14**, already checked ahead against the contract and #10's code, re-groomed and confirmed (hashes `b06f8f35…`, `a0b0f61c…`, `30807dfb…`); #13 and #14 are Heavy. #86 (ingest limits in the contract) is merged.
- Supporting issues, in order: see `_docs/planning/roadmap-1-core.md`. Next among them: #59 (needs the human's browser check; a good one for Claude in the dev container), #75 then #31, #71 with #73, #54, #93 (next epoch batch).
- **Deploy:** `_docs/planning/roadmap-3-deploy.md` (status next, 20 tasks, the seven decisions written in; the spec's Deploy part passes the definition of ready). Terraform on AWS.

### Rules from this session (in `.kiro/steering/`)
- `delivery-pace.md`: CI is the test loop; one PR per issue (summary on the issue branch); groom the next two or three Core issues ahead; one small supporting issue alongside; the Heavy second QA launch is a new session (item 6, in PR #97).
- `gate-blocks.md`: when a script blocks on mechanics, say the work is done, explain, offer the hand option, wait.
- `backlog-order.md`: every filed issue is placed in the supporting list with a trigger; groomed issues get a `[groomed]` title prefix.
- QA's first line must start `QA: PASS` or `QA: FAIL` (`make issue-close` reads only that line); put it in every QA launch message.
- Run git steps one at a time, never in parallel: parallel git calls in this session put commits on the wrong branch three times.

### How to read CI from Kiro Web
`gh api "repos/andrew-chung-au/socboard/actions/runs?branch=<branch>&per_page=4"`, then `.../actions/runs/<id>/jobs` and `.../actions/jobs/<job id>/logs`; filter the log for `passed`, `Weakened`, `Assertion lines` and `VERIFY:` with a small `.scratch/` script (the log is too long to read whole). `gh issue view` and `gh pr ...` fail in Kiro Web; use `gh api`.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). Per-issue counts are in each issue's session summary.

## Files created or modified

This file.

## Decisions made by the human

Recorded in each issue's comments and session summary, and in the steering files above. Latest: option B for #11's audit trail.

## Mismatches with the spec or design docs

none open.

## Commands to validate

- **Verify:** `make verify` (CI on each push).

## Proposed AGENTS.md changes

none.

## Temporary changes

- `make clean-scratch`: not run; housekeeping was on hold. The Kiro Web checkout's local `main` has two unpushed commits (`30f9024`, `fee11dd`) that are superseded; they are local to that sandbox and can be discarded.

## Interruptions

The session ended for context length, mid-#11, at a clean point: no Engineer or QA launch is running, and #11's branch, body and hash are consistent.

## Unrelated problems noticed but not fixed

none beyond those listed above.

## Follow-ups for the next session

1. Ask the human whether they have re-read #11's decision record; then launch the Engineer for option B.
2. Merge state: PR #97 (sweep 4 candidates, interim rule) and this hand-off PR are open.
3. Sweep 4 is due by count after a few more closes; its candidates are in `_docs/planning/sweep-4-candidates.md` (PR #97).
