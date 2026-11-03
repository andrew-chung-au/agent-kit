# Issue #104: Consistency fixes before plan review (testing.md line 175, roadmap-showcase.md line 3, brief content in architecture.md)

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

After #98 moved the AI brief (US-6) to Showcase and #101 reconciled n8n and MCP, three inconsistencies were left. `_docs/testing.md` line 175 said `I-OWNER-SEND` uses MailHog, but its table row says an in-process fake mail sink in the `sqlite-integration` job (`make test`, no Docker); it now says the sink. `_docs/roadmap-showcase.md` line 3 cited the deleted `roadmap-submission-draft.md`; it now points to `_docs/roadmap.md`. `_docs/architecture.md` still described the brief as part of the submission system, because #101's grep and scope covered n8n and MCP only; the Engineer marked about 20 places as showcase in the #101 forms (the backend and LLM rows, workflow step 5, the "LLM brief" section with a banner, the LLM-keys credentials row, Open question 9, A22-A24 and others), deleting nothing and leaving the 1.2.5 / 1.2.6 refused case intact. The submission notification is documented as carrying the structured finding and no brief, matching the spec. The LLM-keys row now matches the secrets table: the backend key is showcase (X4), the responder key is local. At the human's request Open question 9 gained a note: candidate provider (not decided), the Gemini free tier, with `VERIFY:` marks on rate limits, free-tier data use, model names and the SDK being a dependency. QA passed it at f6c0efc.

## Files created or modified

- `_docs/testing.md` (1 line), `_docs/roadmap-showcase.md` (1 line), `_docs/architecture.md` (f6c0efc); none protected
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: approved items 2 and 3 (the testing.md and roadmap-showcase.md lines) and "the bigger gap" (marking the brief in architecture.md); asked what `.env.example` means for the LLM-key fix and was told it is a names-only template (see #105).
- 2026-10-22: "add a note" for the Gemini free-tier candidate in Open question 9 (a note only, nothing decided).

## Mismatches with the spec or design docs

- The responder's GitHub token and the Grafana Viewer token appear in `aws-setup.md` and the credentials table but not in the `architecture.md` secrets table (~line 315); left for plan review.
- Some marks are a bare `(showcase)` tag, a small variant of the #101 forms (QA accepted).
- The sentence "The guardrail never blocks or delays a notification beyond the timeout" is unmarked inside a paragraph that opens "(showcase)" (QA accepted).

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #104 say none required on the merits. The PM's issue creation matched an ask rule.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` (PM, ask rule in `opencode.json`); `make issue-close N=104` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none. The Gemini note reached the Engineer by a mid-run message; the Engineer amended its own unpushed commit to include it, and QA verified it appears in one file only.

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- Plan review (roadmap step 14). Settle the secrets-table gap above, which backend the local responder reads, and the LLM provider (Open question 9).
