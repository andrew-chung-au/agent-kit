# Issue #97: architecture.md and aws-setup.md for the submission decisions

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

#97 came out of splitting #93 (PM grooming, human-approved choices). The Engineer rewrote Deployment in `_docs/architecture.md` for Terraform (three modules), one server with two Compose projects behind `sslip.io` hostnames, GHCR, deploy and rollback by tag, and updated the CI/CD row, security boundaries, responder placement, and closed Open questions 6 and 7. `_docs/aws-setup.md` was rewritten for the same decisions. The email route for the backend is a `VERIFY:` with three options. QA passed it at d5f6508. A follow-up commit d520876 fixed four stale n8n/Grafana mentions that QA noted; QA rechecked it and passed.

## Files created or modified

- `_docs/architecture.md`, `_docs/aws-setup.md` (d5f6508, d520876)
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: accepted all PM recommendations for the #93 split (Terraform named, new notification task appended after 36, extra issue for other documents, milestones created in part A).
- Replied "ok" to fixing the stale mentions now and to the #98 plan.
- Not yet decided: the backend email route (recommended SES through the AWS API with the instance role); server size and hostname form are Engineer assumptions marked `VERIFY:`.

## Mismatches with the spec or design docs

- `architecture.md` still has about 25 n8n-as-built mentions not marked showcase (QA listed the line numbers on #97). Lines 344 and 352 describe the owner-notification journey through n8n, which contradicts US-8 as committed in #98. Not covered by any #97 criterion.
- Both documents cite roadmap items (H2-H6, S3, D2) that live in `_docs/roadmap-submission-draft.md` until #93 merges them.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS after each QA run)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #97 each say none required. The PM that filed #97 listed its commands without a merits request.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue edit 93` (PM, matches the `gh issue edit*` ask rule in `opencode.json`); `make issue-close N=97` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none

## Unrelated problems noticed but not fixed

- `_docs/specs.md` line 6 still lists "LLM guardrails" under deferred without a showcase mark; harmless.

## Follow-ups for the next session

- File an issue to reconcile the remaining n8n mentions in `architecture.md` before plan review (recommended to the human; not yet approved).
- Decide the backend email route before the notification-email task starts.
