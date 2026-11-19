# Planning: Lovable starting prompt and post-import frontend work

**Date:** 2026-11-09T12:45Z (UTC)
**Spec version:** d913e19

## What changed and why

- The human asked whether Bolt (more tokens) or Lovable (better design, limited usage) should build the frontend. Kept Lovable, but cut its job to the design, screens, service-layer contract and a basic mock, so a complex build doesn't stall for days waiting for credits. Fallback if usage runs out: import Lovable's repo into Bolt, or finish it here. No change to the stack decision record.
- Reviewed the starting prompt against the spec and backlog, then rewrote it (`8d201d8`). It now covers two Analysts and a Lead, the full alert fields, the severity rule shown, the sort tie-break, `servedAt`/`ingestedAt` for latency, an `/api` prefix (avoids route clashes when FastAPI serves the SPA in Phase 2), a closed-cases view and Lead reassign. It also asks for a single fetch wrapper so a trace header can be added in Phase 3.
- New backlog item 1b and a roadmap entry hand the routine work to a coding agent after import: mock rule enforcement and error codes, hostile fixtures, the mock new-alert timer, the reassign flag, frontend tests, `make` targets and a README section.
- Spec (`d913e19`): Leads can claim; anyone can add notes to an open case (common SOC practice: ownership controls status, not comments); only the owner or a Lead changes status; Leads can list closed cases to reach their audit trails.

**What I learned:** the usage limit is managed best by narrowing what the generator does, not by choosing the tool with more tokens; the routine code is cheaper for a coding agent in the repo.

## Reflection

### Orchestrator

**What slowed you down (evidence):** the first optimised prompt asked Lovable for tests, fixtures and full mock rules; the human's point about credit refresh times led to the split, so the prompt was written twice.
**What nearly went wrong or was blocked:** nothing blocked. The spec edit waited for the human's approval of the exact diff before the protected commit.
**One proposed change (file, expected effect, measure):** `_docs/planning/02_development.md` step 2: say the generator gets the design and contract only, and a coding agent adds tests and mock rules after import. Expected effect: less generator usage per frontend. Measure: Lovable prompts used before import.

### PM

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `_docs/specs.md`
- `_docs/planning/lovable-guidance.md`
- `_docs/planning/core-backlog.md`
- `_docs/planning/roadmap-1-core.md`
- `_session-summaries/2026-11-09T1245Z-planning-orchestrator-frontend-prompt.md`

## Decisions made by the human

- Keep Lovable for the frontend base, with the trimmed prompt and the Bolt fallback.
- Add a closed-cases list so a Lead can read closed audit trails (decision 1).
- Include Lead reassignment in the frontend now, behind a flag (decision 2).
- Notes open to anyone on an open case; Leads can claim; status changes by the owner or a Lead (decision 3).
- Approved the spec diff committed as `d913e19`.

## Mismatches with the spec or design docs

- Backlog drafts lag the spec and the new frontend contract: #3 seeds one Analyst (spec: two); #2 and #4 lack title, description, `severity_rule` and `ingested_at`; #7 to #9 don't reflect Lead claims, open notes and owner-or-Lead status changes; #6 to #10 use paths without the `/api` prefix and lack the closed-cases (`GET /cases?status=Closed`), reassign and users endpoints.
- The prompt's reassign picks "another user"; the spec's Should-have says "another analyst". Settle when reassignment is groomed.

## Commands to validate

**Verify:** `make verify`
**Decisions:** `make decisions`

## Proposed AGENTS.md changes

none (backlog 1b will need new Commands for frontend run and test, with approval)

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

none new (see the previous summary's list)

## Follow-ups for the next session

- Human: run the starting prompt in Lovable, iterate on design only, connect it to GitHub and clone it into `.scratch/` for review.
- PM: in the backlog review, fix the mismatches above and groom item 1b with the scaffold.
- Engineer: after import, work backlog 1b (`_docs/planning/core-backlog.md`).
