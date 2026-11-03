# Issue #98: Move showcase stories in specs.md to a Showcase section

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

H7 moved n8n routing, the LLM brief, the MCP server, reminders and the digest out of the submission. `_docs/specs.md` (protected) now holds US-6, US-9, US-12 and US-16 verbatim in a "Showcase (post-submission)" section, each old place keeping a pointer. US-7 and US-8 are rewritten so the backend does the daily refresh, re-scan and owner notification, recording `notification.enqueue` and `notification.deliver`; the removed GitHub tracker text is kept in the Showcase section. US-14 gained "(based on the `notification.deliver` outcome)". The US-15 false-positive rule (D4) was deliberately not added. Commit 4fa7a55, made by the orchestrator with `HUMAN_APPROVED=1`.

## Files created or modified

- `_docs/specs.md` (4fa7a55, alone in its commit)
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- Approved the PM's recommendations: stories moved whole and verbatim, owner notification and daily refresh stay in submission, D4 kept out.
- Replied "ok" to a summary of the proposal (the full diff was not shown first), then "I checked #98", then commented "Diff approved" on #98 (https://github.com/andrew-chung-au/vuln-triage/issues/98#issuecomment-6340367654, 2026-10-22T12:08:56Z).

## Mismatches with the spec or design docs

- Process deviation: the protected commit was made on the human's reply to a summary, not on the full diff. QA failed the approval criterion twice, then passed it as a ratification after the human's "Diff approved" comment. The approval record's Approved line still says the commit followed a summary, and its Diff was regenerated from the commit. Comments are not edited, so the later ratification is linked in orchestrator comment 6340374798. Lesson for the next protected change: show the full diff in the decision question before committing.
- US-7 and US-10 both name the scheduled re-scan; the scheduler name and interval are left to #99.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

Engineer and QA comments say none required.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `HUMAN_APPROVED=1 git commit` of `_docs/specs.md` (protected commit; merits basis); `make issue-close N=98` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none. The first `git commit` without `HUMAN_APPROVED=1` was blocked by the protected-file hook, as designed.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `_docs/specs.md` line 6 lists "LLM guardrails" under deferred without a showcase mark; harmless.

## Follow-ups for the next session

- #99 (tasks.md, plan-summary.md), #100 (api.md, openapi.yaml, testing.md, README) and #93 (roadmap merge, milestones) are unblocked.
- Read `git show 4fa7a55` before pushing, as for any protected change.
