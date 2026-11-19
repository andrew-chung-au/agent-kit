# Issue #75: Add make frontend-lint and make frontend-format

**Date:** 2026-11-13T10:00Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #75 as the last of four issues in one `Makefile` sitting (#73, #71, #80, #75; the human's order). Ponytail was on. PR: #130 (merged by the human at 09:59 UTC at `1bebb8e`), then a small follow-up PR for the warning clause and this summary. The branch started from `main` at `49969d5`, which already held #73, #71, #80 and #21 (#128).

- **Claim-time check:** the five decision records dated after grooming say nothing about the lint or format targets, `LINT_CMD` or the epoch batch. A search found no existing caller of either name. No conflict.
- **Change:** two standalone targets in `Makefile`, after `frontend-test`, in its style: `frontend-lint` (`cd frontend && bun run lint`) and `frontend-format` (`cd frontend && bun run format`), each after a missing-tool check with the issue's fixed message. They take no variable, so `ARGS=--fix` is ignored. Two `AGENTS.md` Commands lines after **Frontend test**. Nothing else calls the targets; `make verify` and CI are unchanged.
- **Approvals:** the human approved the exact `Makefile` and `AGENTS.md` diff, then approved applying Reviewer finding 1 with the wording the orchestrator proposed. Both protected commits used `HUMAN_APPROVED=1`.
- **CI:** green on the first push (runs 43400371780 and 43400354852). QA PASS at `1bebb8e` with no finding at Medium or higher. The Reviewer said "Ship".
- **Reviewer finding 1 (applied):** `bun run format` is `prettier --write .`, and `.prettierignore` skips only lockfiles and build output, so the target can rewrite protected files (`frontend/package.json`, in `PROTECTED`) and files the weakened-test guard watches. The **Frontend format** line now says so and tells the reader to check `git status --short` and commit only what the task needs. Not applied, by the human's decision: finding 2 (the help text copies the script body, "(prettier --write .)"; it is the issue's approved wording) and finding 3 (only `eslint` is checked before the lint run; the issue fixes that check). Finding 4, a typo in the task file, was fixed by the orchestrator.
- **Merge timing:** the human merged PR #130 while the clause was still uncommitted, so the clause, the task-file fixes and this summary went in a second branch (`issue-75-format-warning`) from the new `main`. An earlier local merge of `main` into the first branch (made by the Engineer after the human's steering message) was left unpushed and unused.
- **Not verified:** the refused case with the probe file, the pass-through comparison, the format run on a throwaway branch (which also reports whether it touches `frontend/package.json` or test files), the missing-tool message in a clean clone and the `make verify` step list are the human's, in `_human-tasks/2026-11-13T0845Z-human-task-075-engineer-check-frontend-lint-format.md` (Steps 1 to 7). `make frontend-lint` fails on `main` until #31.
- **#31:** its body still needs the edit (Depends on #75; use the make targets; link #75). That needs the human's confirmation in an `Orchestrator:` comment and a new `PM:` hash; the orchestrator did not touch it. A short notice that #75 landed is posted on #31.

**What I learned:** when the human has approved the exact wording of a protected change, committing it does not need a second approval request. Asking again cost a round and let the human merge first.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer (first launch): active time unknown, tool uses unknown (Kiro Web gives neither).
- QA: active time unknown, tool uses unknown.
- Reviewer: active time unknown, tool uses unknown.
- Engineer (second, Reviewer finding 1): active time unknown, tool uses unknown.
- QA (re-check of the warning clause): see the follow-up PR comment.

## Files created or modified

- `Makefile`, `AGENTS.md` (protected; approved diffs).
- `_human-tasks/2026-11-13T0845Z-human-task-075-engineer-check-frontend-lint-format.md`
- This file.

## Decisions made by the human

- Approved the exact diff of `Makefile` and `AGENTS.md` as shown.
- Decision point: apply Reviewer finding 1 (the warning clause); do not apply findings 2 and 3.
- Merged PR #130 at `1bebb8e`, before the clause was committed; expected the orchestrator to commit everything.
- The sweep stays set for after #75.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI; green on `1bebb8e`).
- **Frontend lint / Frontend format:** `make frontend-lint` and `make frontend-format`; the by-hand cases are in the human-task file above.

## Proposed AGENTS.md changes

none (the two Commands lines and the warning clause were approved and committed).

## Temporary changes

none. `make clean-scratch` ran.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- #31's body still needs the edit that depends on #75 (human confirmation and a new `PM:` hash).
- The lint target checks only for `eslint` before running; a partial install with `eslint` but no `prettier` gives bun's own error (Reviewer 3; the issue fixes the check).

## Follow-ups for the next session

1. Run the sweep now that #75 has merged (the human's choice; `make sweep-due` said due after #71).
2. The human's run checks for #73, #71, #80 and #75 are open.
3. #31 can start once the human has confirmed its body edit and the PM has recorded the new hash.
