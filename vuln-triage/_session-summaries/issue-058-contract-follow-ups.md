# Issue #58: Contract follow-ups from #50 QA (job ordering, traceparent, CSRF wording)

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

Settled three contract details QA found outside #50's criteria, so #24's conformance test, the responder build and #56's responder tests compare against one rule. Descriptions only; no schema change.

- Job ids are opaque strings. The job lists order by `createdAt` and then `id` as a stable tie-break by Unicode code point (n8n list ascending, responder list descending).
- `traceparent` is set when a job is created, from `notification.enqueue`, and is never null, in every state.
- The "no CSRF header" sentence now names n8n, MCP and responder.
- `architecture.md` now says `traceparent` is set at creation and never null, and that every job-creating path records a `notification.enqueue` span.

The session ran alongside another session working #56 (`_docs/testing.md`, roadmap step 10); #58 was chosen because it touches neither `testing.md` nor step 10.

## Files created or modified

- `2e9a4dd`: `_docs/openapi.yaml`, `_docs/api.md` (descriptions)
- `4cebbd2`: `_docs/architecture.md` (NotificationJob row; Observability "One trace ID" paragraph)
- `b7b4d36`: `_docs/api.md` (every-job `traceparent` sentence)
- `_docs/roadmap.md` (step 8b row, one check-in line), `_docs/ai-usage-log.md` (one entry), this summary

## Decisions made by the human

- D1: option 1, opaque string ids. D2: option 1, `traceparent` always set (comment 6329573230).
- Spec notes 1 and 3 approved, and the exact `architecture.md` diff approved. Spec note 2 (finding tie-break compares ids as strings) not taken now.
- The contract approved at `2e9a4dd`.
- After QA's FAIL on the approval record: option 2, `architecture.md` is gated by convention only; `PROTECTED` unchanged.

## Mismatches with the spec or design docs

- The issue, the PM comment and the orchestrator all called `_docs/architecture.md` "protected", but it is not in `PROTECTED` (`agent-kit.conf` line 42). The orchestrator posted a protected-change record for `4cebbd2`; QA FAILed it; the correction note is 6329737124. The label may recur in later issues.
- The acceptance criterion "no change to `architecture.md`" did not hold, by the human's approval of spec notes 1 and 3.
- Spec note 2 is deferred, so the finding order (architecture rule 4) and the job-list order state different tie-break rules until the next spec change.
- Roadmap step 8b said `todo` although #50 was closed; corrected.

## Commands to validate

- **Verify:** `make verify` (PASS, 62 tests, at `2e9a4dd` and on both pushes)
- **Validate OpenAPI:** `make openapi-validate` (exit 0)
- **Assert clean:** `make assert-clean` (PASS after both QA runs, HEAD `b7b4d36`)

## Proposed AGENTS.md changes

none

## Temporary changes

none. No processes were started. `.scratch/` cleaned with `make clean-scratch` at the end.

## Permission review

All role comments (PM 6329518860, Engineer 6329595990, QA 6329697265 and 6329743761, orchestrator notes) state "none" for approvals.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `git push -u origin claude/vigilant-heisenberg-qtr2f3` (the cloud-session exception; no merits request). The groomed body was applied to #58 with the GitHub issue tool, because `gh issue edit` (GraphQL) is blocked in cloud sessions; there is no `make` target for editing an issue body.
- Risky (propose denying): none
- Proposed `opencode.json` and `.claude/settings.json` changes: none

## Interruptions

none. The PM could not edit the issue body (HTTP 403 from `gh issue edit`); it stopped, reported, and the orchestrator applied the body.

## Unrelated problems noticed but not fixed

- `make issue-edit` (a REST body-edit target) does not exist; the PM role file implies `gh issue edit`, which fails in cloud sessions. Worth a small tooling issue under "Later".
- The PM comment's closing note names `gh issue edit` as the way to apply the body; wrong in cloud sessions (comments cannot be edited; corrected in 6329573230).

## Follow-ups for the next session

- Spec note 2 (finding tie-break wording) waits for the next spec change.
- #56 (the other session) should check its responder section against `2e9a4dd`: ids opaque, order by `createdAt` then `id` code point, `traceparent` present in all four states.
- Step 11 (`tasks.md`) waits for #56.
- Ask whether `architecture.md` should join `PROTECTED`; the human chose convention only on 2026-10-22.
