# Issue #102: Split notification tests into Showcase and submission versions

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

After the spec moved n8n routing to the showcase (#98), the submission notification tests still assumed n8n claimed and reported jobs. The Engineer kept the six n8n cases (`I-JOBS`, `I-LIFECYCLE`, `I-IDEMPOTENCY`, `I-HOLD`, `T-JOURNEY`, `P-DEMO`) verbatim with IDs unchanged and marked them showcase, and wrote eight new submission cases for what the backend does alone: `I-OWNER-SEND`, `I-OWNER-NOAWS`, `I-OWNER-SENDER`, `I-OWNER-ONCE`, `I-OWNER-HOLD`, `I-SCHED`, `T-JOURNEY-BE`, `P-DEMO-BE`. Matrix rows US-7, US-8a-d, US-13, US-15 and edge rows E2, E4, E7, E9 point at them. Counts moved from 53 submission / 18 showcase case IDs to 55 / 24; CI jobs stay 9 / 2 (QA's own recount agrees). Mailpit became MailHog, and the `lastErrorCode` description now reads as the backend's last failed delivery attempt code, keeping the n8n meaning for the showcase path (description text only in `api.md` and `openapi.yaml`). QA passed it at 5573e03.

## Files created or modified

- `_docs/testing.md`, `_docs/api.md`, `_docs/openapi.yaml` (5573e03); none protected
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: preferred keeping the old n8n tests renamed to showcase and writing pared-down submission ones, to avoid rewriting later.
- Reviewed the `api.md`/`openapi.yaml` diff before the commit and replied "approve" (recorded on #102 before the commit, so no process gap this time).
- Approved an in-process fake mail sink for `I-OWNER-SEND` and `I-OWNER-HOLD` (folded into #93's clean-up).

## Mismatches with the spec or design docs

- `I-OWNER-SEND` and `I-OWNER-HOLD` sit in `sqlite-integration` (`make test`, no Docker) but assert via MailHog, a Compose container. Fix folded into #93's clean-up.
- The counts method cites `.scratch/count_cases.py`, which is git-ignored, so the counts cannot be rerun from a clean clone.
- The unmarked paragraph after `T-JOURNEY` still describes the n8n traceparent round trip; the US-5 row cites `E-DELIVER` without a Showcase mark (pre-existing).
- `POST /signals/refresh` and `POST /scans` keep the n8n credential; the human decided the backend scheduler calls them in-process, so the contract is unchanged.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Validate OpenAPI:** `make openapi-validate` (OK)
**Assert clean:** `make assert-clean` (PASS after QA)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #102 each say none required on the merits. The PM's issue creation matched an ask rule.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` (PM, ask rule in `opencode.json`); `make issue-close N=102` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none

## Unrelated problems noticed but not fixed

- The stray, redundant "E-DELIVER ... Mailpit text" bullet in #102's body was deliberately ignored (the MailHog criterion covers it).
- A stray placeholder `qa-102-fix.txt` was left in `.scratch/` by QA; `make clean-scratch` removes it.

## Follow-ups for the next session

- #93 carries the in-process sink edit for `I-OWNER-SEND`/`I-OWNER-HOLD`; consider committing the case-count script as a make target.
