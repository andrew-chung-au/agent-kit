# Issue #028: Verify gate: treat test-file renames as moves, and allow human-approved test deletions

**Date:** 2026-10-18
**Spec version:** d3a8f11

## What changed and why

The weakened-tests check in `verify.sh` used `--no-renames`, so the #15 move of `frontend-lovable/` to `frontend/` (b566fb6) and the human-approved Bolt deletion (cbe2123) failed `make verify BASE=0dd108a` with "test files deleted". The check now uses `-M`. An unchanged move (R100) between test paths is a move. An edited rename is checked at its new path, diffed old to new. A deletion passes only if its exact path is in the new `APPROVED_TEST_DELETIONS` array in `agent-kit.conf`, and a glob entry fails the gate. Committed alone in 035eafd with `HUMAN_APPROVED=1`. Engineer work only; QA has not run yet.

## Files created or modified

- `_docs/agent-kit/scripts/verify.sh`, `agent-kit.conf` (protected; 035eafd)
- `_docs/ai-usage-log.md` (entry for #28)
- this summary
- `.scratch/issue-28-verify-fixtures.sh` (git-ignored; 24 fixture cases, QA re-runs it)

## Decisions made by the human

- Earlier, in the #15 session: fix the gate rather than work around it; the name `APPROVED_TEST_DELETIONS`, exact paths only and the 100% similarity rule (relayed by the Orchestrator).
- 2026-10-18: approved the exact diff of `verify.sh` and `agent-kit.conf` ("Approve as shown (Recommended)", relayed by the Orchestrator).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify BASE=0dd108a`. After 035eafd, the weakened-tests section lists the four Bolt paths under "Deleted with approval" and does not mention the two moved tests. Result: PASS WITH WARNINGS, the only warning being the no-`TEST_CMD` one.
- Fixtures: `bash .scratch/issue-28-verify-fixtures.sh`. Result: 24 passed, 0 failed, and this repository's HEAD and `git status --short` were unchanged.

## Proposed AGENTS.md changes

none

## Temporary changes

The fixture script creates throwaway repos in `.scratch/issue-28-fixtures/` (git-ignored). They are left in place so QA can inspect them, and `make clean-scratch` at the end of the issue removes them. No system or git config changes, no processes started, no installs.

## Interruptions

The Engineer stopped before the protected commit, as instructed, and returned the diff with an approval request. After the human approved, the Orchestrator checked that the working-tree diff matched and resumed the Engineer.

## Unrelated problems noticed but not fixed

- The skip-marker and assertion greps (`^\+[^+]`, `^-[^-]`) skip added or removed lines whose content itself starts with `+` or `-`. This is existing behaviour and was left unchanged because the issue forbids it.

## Follow-ups for the next session

- QA for #28: re-run the fixture script and quote the weakened-tests section of `make verify BASE=0dd108a`. After that, #15 QA is unblocked.
- For the human, kit upstream (out of scope for #28): document `APPROVED_TEST_DELETIONS` in `_docs/agent-kit/templates/agent-kit.conf.template` and `blueprints.md`, and offer the fix to the agent kit (version 1.9).
