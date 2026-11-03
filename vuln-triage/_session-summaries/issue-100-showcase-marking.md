# Issue #100: Mark showcase features in api.md, openapi.yaml, testing.md and README

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

H7 moved n8n routing, the LLM brief, the MCP server, reminders and the digest to the showcase (#98), but the API and test documents still presented them as submission scope. The Engineer marked them. `openapi.yaml` changed only description text and `x-showcase: true` flags: 7 operations (the notification-job operations, the weekly digest, the three MCP operations), the `n8n` and `mcp` tags, the `n8nAuth` and `mcpAuth` schemes and 8 schemas. No path, parameter, schema shape, response or security change. `api.md` has a Showcase scope paragraph and marked rows. `testing.md` has a "Showcase scope and counts" section: 53 submission and 18 showcase case IDs, 9 submission and 2 showcase CI jobs, recounted by script and by QA. README marks steps 5 and 6 and the MCP bullet and links the spec's Showcase section. QA passed it at 3c13321.

## Files created or modified

- `README.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/testing.md` (3c13321); none protected
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: the human reviewed the contract diff (`git show 3c13321 -- _docs/openapi.yaml _docs/api.md`) and replied "approved 3c13321"; recorded on #100.
- The backend scheduler (task 38) calls refresh and re-scan in-process, so `POST /signals/refresh` and `POST /scans` keep n8n's credential and the contract is unchanged.
- Process gap: the commit was made before the human reviewed the contract diff, though the issue asks for the review first. QA noted it; the human then approved the commit as made.

## Mismatches with the spec or design docs

- Submission rows in `testing.md` still described the n8n claim/report path (`I-JOBS`, `I-LIFECYCLE`, `I-IDEMPOTENCY`, `I-HOLD`, `T-JOURNEY`, `P-DEMO`, US-8 rows): #102.
- `ResponderNotificationJob.lastErrorCode` still worded as the n8n `errorCode`, and `testing.md` `T-A6`/E2E paragraph said Mailpit where the decision is MailHog: #102.
- The README does not link `roadmap-showcase.md`; that belongs to #93.
- US-15 (responder) operations and cases are left unmarked because the spec's Showcase section does not include US-15; `I-CONFIG` is counted as showcase because US-9 moved.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Validate OpenAPI:** `make openapi-validate` (OK)
**Assert clean:** `make assert-clean` (PASS after QA)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

Engineer and QA comments say none required.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `make issue-close N=100` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- #102 and #101; #93 last, after #92.
