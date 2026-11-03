# Planning: step 12 Milestone A backlog

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

- Built the step 12 backlog proposal from `_docs/tasks.md` (36 tasks) against the spec and the existing tracker, then filed the human-approved Milestone A set.
- Filed #74 (task 1), #75 (task 2), #76-#80 (tasks 4-8), #81-#84 (tasks 9a/9b and 10a/10b), #85-#88 (tasks 11-14). Rewrote #26 as task 3 (data model and SQLite persistence); closed #24 and #25 as superseded, with comments naming where their scope moved.
- B/C/Committed issues are not filed yet; they file at each milestone boundary, per the human's answer.
- Issue 1's criteria were corrected so `make test` keeps the existing frontend suite and adds the backend smoke test, instead of dropping the frontend from `make verify`. Task 13 still grows `make test` as written.

## Files created or modified

- `_docs/roadmap.md` (step 12 and step 15 rows, check-in), `_docs/ai-usage-log.md`, this summary.
- No application or planning document changed; `_docs/tasks.md` and `README.md` are unchanged in this session.
- GitHub: issues #74-#88 created; #26 edited; #24/#25 closed with comments 6333191444 and 6333194914. Decisions recorded on #72 (6331775484). Follow-ups from the previous session: #73 and `andrew-chung-au/agent-kit` #19.

## Decisions made by the human

- File Milestone A now; file B/C/Committed at each boundary.
- Close #24/#25 as superseded; rewrite #26 as task 3.
- Split task 9 into 9a/9b and task 10 into 10a/10b (38 issues total).
- Accept the four #63 notes before Milestone C (not applied yet).
- Decide the LLM provider/model and responder runtime at Milestone C/Committed start; use stubs for interface tasks now.

## Mismatches with the spec or design docs

- `_docs/tasks.md` task 1 said the frontend suite is not part of the task's pass condition; that would remove the frontend from `make test` and weaken `make verify`. Issue #74 keeps the frontend suite in `make test`, and task 13 still grows it. This is a tasks.md wording inconsistency, reported here rather than edited.
- `_docs/tasks.md` task 2's evidence note says "without changing the record"; the issue clarifies that the GitHub record is unchanged and only the task note is written.

## Commands to validate

- None run for this backlog-only session. No code, test or contract changed; `make verify` was not needed.
- `gh issue list --state all --json ...` was read to check duplicates.

## Proposed AGENTS.md changes

- none

## Temporary changes

- `.scratch/step-12-backlog-proposal.md`, the 16 Milestone A issue bodies and the two closure comments; `make clean-scratch` ran at the end of the session.
- No processes started; no system configuration changed; no installs.

## Permission review

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` for #74-#88 (issue-creation allow rule), `gh issue edit 26` (issue-edit ask rule), `make issue-comment` on #24/#25/#72 (allowed target), `make issue-close` on #24/#25 (issue-close ask rule); `gh issue create -R andrew-chung-au/agent-kit` for #19 in the previous session
- Risky (propose denying): none

## Interruptions

- none

## Unrelated problems noticed but not fixed

- Task 2's "record a note in `_docs/tasks.md`" is a small deviation from the D2 wording "does not rewrite documents"; the issue scopes it to the task 2 note only.
- Tasks 9, 10, 28 and 29 remain the broadest even after the 9/10 split; #87/#88 and the B/C issues will show whether further splits are needed.
- Closing #24/#25 through `make issue-close` records `state_reason: completed`, not `not planned`; the comments explain the supersession.

## Follow-ups for the next session

- Work the Milestone A issues in dependency order, starting with #74 (task 1), after the phase-line change that step 14 still requires.
- File Milestone B issues when step 15's Milestone A work is under way (the human's batching choice).
- Step 13 (`_docs/plan-summary.md`) still needs its own issue.
