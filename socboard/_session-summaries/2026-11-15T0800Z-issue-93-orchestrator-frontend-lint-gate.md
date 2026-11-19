# Issue #93: Run the frontend lint in make verify and CI

**Date:** 2026-11-15T08:00Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`make verify`, and so CI and the push check, now runs the OpenAPI contract check and the frontend lint in its one Lint gate: `agent-kit.conf` line 25 is `LINT_CMD="make contract-check && make frontend-lint"`, and the `AGENTS.md` Verify line names both. Both are protected; the agent wrote the exact diff and a human task (`_human-tasks/2026-11-15T0627Z-human-task-093-engineer-apply-lint-gate.md`), and the human read, applied and committed it with `HUMAN_APPROVED=1` (`db1a6a6`). Epoch-batch item 6 had not landed (`LINT_CMD=""` at claim), so this line is the whole change. No `Makefile`, `verify.sh`, `.github/*`, `frontend/` or `openapi.yaml` change.

Branch `issue-93-frontend-lint-gate`, draft PR #242. Claim: https://github.com/andrew-chung-au/socboard/issues/93#issuecomment-6890301254. Engineer evidence (both failure probes through the real `make verify`): https://github.com/andrew-chung-au/socboard/issues/93#issuecomment-6891238058. QA PASS at `db1a6a6`, Lows only: https://github.com/andrew-chung-au/socboard/issues/93#issuecomment-6891397785. CI on `db1a6a6`, all success: `socboard verify` pull_request run 43690150701 (`== Lint (make contract-check && make frontend-lint) ==`, `PASS: Lint`, `VERIFY: PASS`), postgres 43690150664, image 43690150684, compose 43690150703.

**What I learned:** an empty `LINT_CMD` is silent in `verify.sh` (no section, no warning), so a protected commit that missed its apply step still passed every check; the line itself has to be read after the human's commit.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** two hand-overs for the protected commit: the branch was not yet in the human's clone (`invalid reference`), then the first commit `e1c8ab6` held only the proposal deletion.
**What nearly went wrong or was blocked:** `e1c8ab6` passed the push check with no Lint gate; I caught it only by reading `agent-kit.conf` on the fetched head.
**One proposed change (file, expected effect, measure):** in the human-task template for protected diffs, put a `grep` of the changed line straight after the `git add` and before the commit, with the exact expected line (it would stop an empty commit; measured by protected commits that need a second round).

## Launch usage

QA: 1 launch (PASS). Active time and tool uses: unknown.

## Files created or modified

- `agent-kit.conf`, `AGENTS.md` (by the human, `db1a6a6`)
- `_human-tasks/2026-11-15T0627Z-human-task-093-engineer-apply-lint-gate.md`; `_human-tasks/093-proposed/lint-gate.diff` (added, then removed by the human)
- `_docs/records/findings/93.json`
- `_session-summaries/2026-11-15T0800Z-issue-93-orchestrator-frontend-lint-gate.md` (this file)

## Decisions made by the human

- Labelled #93 `approved`; approved the plan, then the exact two-line diff, and committed it.
- Not answered, so the stated defaults stand: the session summary and findings file are kept in this pull request (option a); the epoch-batch README items 6 and 6b are left for the human to mark as folded into #93.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43690150701): look for `== Lint (make contract-check && make frontend-lint) ==` and `PASS: Lint`.
- **Lint value:** `grep -n '^LINT_CMD=' agent-kit.conf`.

## Proposed AGENTS.md changes

none beyond the approved Verify line

## Temporary changes

- `frontend/src/lint-probe.ts` and an `openapi.yaml` edit, for the failure probes: removed and restored; `git status --short` empty after each.

## Interruptions

- A steering message mid-session renamed the lane to the application and tests lane (`[App]`) and set the queue: #31, #93, then #214 and #215 (Heavy, one at a time), #237 prepared only.

## Unrelated problems noticed but not fixed

- F-93-1: The branch holds a human task file and, before the merge, the session summary and findings file, which are paths beyond the two the criterion lists; the human decides whether docs paths count.
- F-93-2: The human task file still describes a removal step an earlier commit already did, and its result table is empty.
- F-93-3: The push check's Lint section was not seen: the human's pasted push output showed only the final verify line.
- F-93-4: The first protected commit held only the removal of the proposal file because the apply step was missed, and the checks still passed, since an empty LINT_CMD runs no gate.

## Follow-ups for the next session

- The epoch-batch README (`_docs/planning/epoch-batch-1/README.md`, items 6 and 6b): mark them folded into #93 (the human's call).
- Next in the queue: #214 (Heavy), then #215 (Heavy); never both at once.
