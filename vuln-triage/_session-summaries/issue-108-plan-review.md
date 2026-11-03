# Issue #108: plan review and phase change

**Date:** 2026-10-23
**Spec version:** 9b04f90

## What changed and why

Roadmap step 14 is done. The plan passed an independent review, the `AGENTS.md` phase line moved from PLANNING to BUILD, and S1 is unblocked. The work ran in two orchestrator sessions with a mid-issue handoff; this summary covers the whole issue.

- Review 1 (FAIL at `84e99fd`) found 1 High, 14 Medium and 9 Low findings. The High (E8 notice had no submission owner) was fixed by the human-approved spec commit `9b04f90`; the 14 Mediums and the listed Lows were fixed in stage 2 in six commits (WP2 `b9e3c23`, WP3 `2a0e169`, WP4 `ca470b5`, WP5 `5fcfa8f`, WP6 `aa9b93a`, WP8 `971457b`), with the log and check-in in `4a512a2`.
- QA passed stage 2 at `46dd403` (comment 6354307995): `make verify` PASS (62 tests), `make openapi-validate` OK (22 operations).
- Review 2 (`fc89dcf`, `_docs/reviews/2026-10-22-plan-review-2.md`) is `Reviewer: PASS at 46dd403`: 0 High, 2 Medium, 2 Low. All earlier Highs and Mediums were re-checked by name and fixed. The four leftover findings and two questions are in follow-up #109.
- Post-PASS: README line 4 now says the project is in the build phase (`f14ac52`); the `AGENTS.md` phase line was committed alone with `HUMAN_APPROVED=1` (`bbce6fb`, approval record comment 6354792932); the roadmap records step 14 `done` and S1 `todo` (`31d7be9`).

## Files created or modified

- Plan documents in stage 2: `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/testing.md`, `_docs/tasks.md`, `_docs/plan-summary.md`, `_docs/roadmap.md`, `_docs/aws-setup.md`, `_docs/planning-process.md`, `_docs/docker-runbook.md`.
- Protected: `_docs/specs.md` (`9b04f90`, E8 Showcase); `AGENTS.md` (`bbce6fb`, phase line).
- Reviews and record: `_docs/reviews/2026-10-22-plan-review.md` (`d31cb02`), `_docs/reviews/2026-10-22-plan-review-2.md` (`fc89dcf`), `_docs/ai-usage-log.md`, `README.md` (`f14ac52`), `_docs/roadmap.md`, this summary.
- GitHub: follow-up issue #109; approval records and close-out comments on #108.

## Decisions made by the human

- Step 14 proceeds now; it depends on steps 11 and 13 (Milestone A filed), and "and the spec" is dropped from its Done-when.
- Reviewer: a fresh session with a model other than `claude-opus-5-5`; run 1 was Claude Code sonnet. Run 2 was planned as sonnet, but this environment's subagents inherit the main session model; the human accepted the OpenCode `deepseek-v4.1-flash-free` run as the independent run because it is a different tool and model from the plan's authors.
- A16-A18 and Q8 confirmed as written; Q10 accepted and documented (no-CVE vulnerabilities cannot reach P1 or P2).
- E8: the notice moves to Showcase; `signalsChanged` stays in submission.
- All 14 Mediums fixed; Tier A gets `make dev` and stays 12; `PATCH /assets/{id}` makes 22 operations; nightly stop gets a 24-hour catch-up rule and a grading switch; the alert uses a constant 0 gauge with NoData alerting the human only; `/health` is outside the contract and excluded by name; task 10 stays one task with contract-only Showcase stubs; task 39 added; responder runtime chosen before task 28; A39 kept; R6 accepted and to be re-estimated.
- README line 4 is rewritten after PASS; D8 and the Q10 risk row are added to `plan-summary.md`.
- File one follow-up (#109) for the four review-2 findings and two questions; accept the review-2 run and its model.

## Mismatches with the spec or design docs

- The review-2 findings are known and deferred to #109: `I-ASSET-UPDATE` placement in task 9 vs the task 37 delivery worker; the two E8 `signals changed` jobs colliding on the `(lifecycle, kind)` key; the unmarked Showcase `issue close` enum; task 10's traceparent ordering vs task 23.
- Low 19 (worked example needs a P2 finding and one at EPSS exactly 0.10) is deliberately left; the `rubric-evidence.md` lines 29 and 45 stale "roadmap step 16" text is the auditor's file and left alone.
- The spec's criticality assumption wording is left as written (D8) and aligned at the next approved spec change.

## Commands to validate

- **Verify:** `make verify` (PASS at `46dd403` and on the close-out commits; 62 tests, type check, whitespace, no weakened tests).
- **Validate OpenAPI:** `make openapi-validate` (OK, 22 operations).
- **Assert clean:** `make assert-clean` (PASS after QA and after the Reviewer).

## Proposed AGENTS.md changes

- The phase line is already changed. The Commands section still needs lines when the protected Makefile targets land: `make dev`, `make dev-start`, `make dev-stop` (task 11), `make record-fixtures` (task 4), and `make test-compose JOB=<telemetry|alert|responder>` (task 25).

## Temporary changes

None. No system changes, processes or large installs. `.scratch/` was emptied with `make clean-scratch`.

## Permission review

- Read-only (propose allowing): none (the read-only commands used, such as `make issue-dump`, `git status/log/show/diff/rev-parse`, `make verify` and `make openapi-validate`, are auto-allowed and did not require approval).
- Writes to the record (keep asking): `edit` of `_docs/specs.md` and `HUMAN_APPROVED=1 git commit` for `9b04f90` (merits request, protected file, 2026-10-22); `edit` of `AGENTS.md` (matched the `AGENTS.md: ask` rule) and `HUMAN_APPROVED=1 git commit` for `bbce6fb` (merits request, protected file, 2026-10-23); `gh issue create` for #109 (PM, merits request, network write); `make issue-close N=108` (matched the `make issue-close*: ask` rule).
- Risky (propose denying): none.

## Interruptions

The first orchestrator session handed off mid-issue while the Engineer's WP8 edits were uncommitted. The updated handoff records that WP8 was committed (`971457b`) and the log/check-in followed (`4a512a2`); the tree was clean at `46dd403`, so no work was lost. No role stopped early in this session.

## Unrelated problems noticed but not fixed

- Low 19 (worked example) and the `rubric-evidence.md` stale lines 29 and 45 stay as they were.
- The `I-OWNER-HOLD` ownerless-flag question and the E8 two-job design question are in #109.
- The protected Makefile targets and their `AGENTS.md` Commands lines are still to be added at build time.

## Follow-ups for the next session

- Fix #109 before tasks 9, 10, 23, 35 and 37.
- Start S1 with #74, then the Milestone A issues in the roadmap order.
- Ask for the protected Makefile commits when task 4, 11 or 25 needs them; then add the `AGENTS.md` Commands lines.
- Choose the responder runtime before task 28 is filed; re-estimate R6 after the #108 fixes.
