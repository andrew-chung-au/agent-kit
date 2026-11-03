# Issue #107: Pre-review clean-up: stale planning wording, plan-summary register, roadmap step 14 dependency

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

Roadmap step 14 (plan review) had no issue. The PM drafted two: #107 (this clean-up, so the Reviewer does not spend findings on known staleness) and #108 (the plan review and phase change, blocked by #107). Both were filed after the human approved the drafts. The Engineer then updated the planning documents to match the decisions H1-H7:

- `planning-process.md`: the Stage 2 Deployment bullet now says Terraform, one server running `dev` and `prod` as two Compose projects, GHCR and `sslip.io`; promotion, rollback, the Docker-capable environment, cost controls and teardown are kept.
- `plan-summary.md`: step numbers replaced with S1-S5 and T1-T3; register rows for roadmap D1, D2, D3, D6, D7 and `architecture.md:Q6` marked resolved (D4 and D5 stay open); the A26, T-A6 and A36 rows corrected; R7 amended so Milestone B/C/Committed filing no longer gates step 14; D6 marked resolved by #73; all counts and line locations recounted at `2285abc`. Two `testing.md` VERIFY items that were missing were added as register rows, so the total is 112 (was 110).
- `roadmap.md`: step 14 "Depends on" is "11, 13 (Milestone A filed)" and "Done when" no longer says "and the spec"; step 12's status cell says B/C/Committed issues are filed at their boundaries and no longer gate step 14; the D2 row no longer says the `architecture.md` edit is not made; a check-in line was added.
- `architecture.md`: `service.version` added to the telemetry allowlist (A32, one line).
- `roadmap-showcase.md` line 3 needed no edit; #93 had already removed the deleted draft's name.

Commits: `17fc6d9`, `061de62`, `af9a5f8` (usage log). QA PASS at `af9a5f8` (comment 6351364903).

## Files created or modified

- `_docs/planning-process.md`, `_docs/architecture.md`, `_docs/roadmap.md` (`17fc6d9`); not protected
- `_docs/plan-summary.md` (`061de62`); not protected
- `_docs/ai-usage-log.md` (`af9a5f8`) and this file (separate commits)

## Decisions made by the human

- 2026-10-22, Q1: proceed with step 14 now and amend the roadmap (step 14 depends on 11 and 13 plus Milestone A filed).
- 2026-10-22, Q2: the Reviewer is a fresh Claude Code session on a model other than claude-opus-5-5, recorded as an exception to the Reviewer text in `agent-team.md`.
- 2026-10-22: one clean-up issue before the review; file both issues as drafted.
- 2026-10-22: A16, A17, A18/Q8 confirmed as written (T = 0.10 is configuration); Q10 accepted and documented; "and the spec" dropped from step 14's Done-when. Applying these to `architecture.md` and `plan-summary.md` is part of #108.
- 2026-10-22, QA risks: accept the two added VERIFY rows, the D2 row edit and the log entry; fold the task 17 OIDC `VERIFY:` register row and the `architecture.md` line 430 step number into #108.

## Mismatches with the spec or design docs

- `tasks.md` line 107 (task 17) has a `VERIFY:` about an existing GitHub OIDC provider that the register lacks; `tasks.md` now has 7 occurrences on 3 lines against the register's 6 on 2, and the register's "tasks.md unchanged since #99" claim is stale. To #108.
- `architecture.md` line 430 still says "#31 (roadmap step 16)". To #108.
- `_docs/prompts/reviewer-plan-review.md` says OpenCode wrote the plan; kept verbatim, with a run note in #108.

## Commands to validate

**Verify:** `make verify` (Engineer and QA: PASS, 62 tests, type check, whitespace, no weakened tests)
**Assert clean:** `make assert-clean` (PASS, HEAD `af9a5f8` unchanged after QA)

## Proposed AGENTS.md changes

none (the phase-line change is #108's)

## Temporary changes

none

## Permission review

The PM and QA comments say no approval was needed on the merits; the Engineer comment says none. The PM's issue creation and comments matched ask rules.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` twice (PM, #107 and #108, ask rule); `make issue-comment` for the PM comments on #107 and #108 and for the Engineer and QA comments; `make issue-close N=107` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none

## Unrelated problems noticed but not fixed

none beyond the two items passed to #108 above.

## Follow-ups for the next session

- #108: apply the A16-A18/Q8/Q10 answers, add the two folded-in items, run the Reviewer (fresh Claude Code session, model other than claude-opus-5-5), then the phase-line commit.
