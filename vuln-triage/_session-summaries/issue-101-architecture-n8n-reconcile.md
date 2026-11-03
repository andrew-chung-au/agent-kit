# Issue #101: Reconcile remaining n8n-as-built mentions in architecture.md with the Showcase spec

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

After #97 and #98, `_docs/architecture.md` still described n8n and the MCP token as part of the submission in many places. The Engineer marked every n8n hit as showcase or rewrote it as a submission fact without n8n. The owner-notification journey now runs scan, match, score, notification job, backend delivery, with `notification.enqueue` then `notification.deliver`; the n8n round trip sits under a "Showcase:" clause. The email route is now the human's decision, not an options list: SES API through the instance role, one verified sender, MailHog for development and tests (no Mailpit left), with `VERIFY:` marks on sandbox recipients, free allowance and limits, IAM action and condition keys, SES region and the MailHog image and ports. QA failed the first commit (c098669) because the submission 403 case named the MCP token, which is showcase; the fix commit 86d3978 names the responder token (`I-RESP-WRITE`) and marks the MCP and n8n token rows and the claim/reminder/digest paths as showcase. QA passed the recheck at 86d3978.

## Files created or modified

- `_docs/architecture.md` (c098669, 86d3978)
- `_docs/ai-usage-log.md` and this file (separate commits)

## Decisions made by the human

- 2026-10-22: the email route (SES API via the instance role, one verified sender, MailHog for development and tests), recorded on #99 and #101.
- Approved folding two small follow-ups into #93's clean-up: an in-process fake mail sink for `I-OWNER-SEND` and `I-OWNER-HOLD`, and rewording task 37's stale "option (b)" reference.

## Mismatches with the spec or design docs

- The "## MCP server" section (lines about 290-301) has no showcase marker and states `MCP_API_TOKEN` as plain fact, though the MCP server is showcase (QA, outside the criteria). Not fixed.
- Line 271, "A second claim of a claimed job is refused", is unmarked but sits inside the showcase n8n design (cosmetic).
- Task 37 in `_docs/tasks.md` cites "option (b), which #101 settles" though the option list is gone: folded into #93.
- Line 260 was edited in c098669 against the issue's constraint; reverted in 86d3978.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS after each QA run)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #101 each say none required on the merits. The PM's issue creation and edits matched ask rules.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` and `gh issue edit 99` (PM, ask rules in `opencode.json`); `make issue-close N=101` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none. QA's first run failed #101; the fix and recheck followed the normal loop.

## Unrelated problems noticed but not fixed

- The MCP server section and line 271 above.

## Follow-ups for the next session

- Mark the MCP server section as showcase (small; could join #93's clean-up or a later pass).
- #93 (roadmap merge, milestones, two small clean-up edits) after #92.
