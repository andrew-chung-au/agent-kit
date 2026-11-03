# Issue #99: Reshape tasks.md and plan-summary.md for the submission/showcase split

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

After the spec moved the showcase features out (#98), the Engineer reshaped `_docs/tasks.md` and `_docs/plan-summary.md`. Tasks 17 and 18 are now Terraform, a GHCR build, one server with two Compose projects behind `sslip.io` hostnames, and the manual production workflow with rollback. Task 21 is the dev auto-deploy only; the production promotion is in task 18. Task 24 is the local Compose observability stack plus MailHog. Task 29 is the local-run demo. New task 37 is the backend owner notification (SES API through the instance role, one verified sender, MailHog for development and tests, four `VERIFY:` marks). New task 38 is the backend scheduler for the daily refresh and scheduled re-scan. Tasks 30-36 are under "Showcase (post-submission)". The plan summary's rubric map, risks R2-R7 and register were updated; the register went from 106 to 110 rows. Tasks 1-36 were not renumbered (0 task numbers changed). QA passed it at 70a0f82.

## Files created or modified

- `_docs/tasks.md`, `_docs/plan-summary.md` (70a0f82)
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22, accepting the PM's recommendations for the #93 split: the new notification task is appended after 36; the backend email route is SES through the AWS API with the instance role plus MailHog for development.
- On QA's open items: keep the "Build order" note (build task 37 after 24 and before 25; no forward `Depends on:` on tasks 25 and 28); accept task 21 as the dev deploy with the production promotion in task 18; the backend scheduler calls refresh and re-scan in-process. Recorded on #99 and #100.

## Mismatches with the spec or design docs

- Build order lives in a note, not in `Depends on:` lines; anything scheduling from `Depends on:` alone could build tasks 25 or 28 before 37 (accepted by the human).
- `roadmap.md` B4, B5 and C3 still cite `vt-ci-iam`, `vt-ecr`, `vt-dev` and ECR, and D3, D6, D7 are still marked open: #93.
- `architecture.md` and `testing.md` still named Mailpit and the n8n path when #99 closed: #101 and #102.
- Task 10's title and description still say "n8n" operations; the API operations are valid, so they were left.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS after QA)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #99 each say none required on the merits. The PM's body edit matched an ask rule.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue edit 99 --body-file ...` (PM, matches the `gh issue edit*` ask rule); `make issue-close N=99` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- #101 (architecture.md), #102 (testing.md and the `lastErrorCode` wording) and #93 (roadmap merge, milestones; waits for #92).
- MailHog and the AWS SDK client are recorded as "ask before adding"; neither is added.
