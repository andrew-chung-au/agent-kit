# Issue #131: Frontend follow-ups from #21

**Date:** 2026-11-15T03:29Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

The deferred #21 items, `frontend/` only, no protected file, no new dependency:
- The queue polling test runs through the real client and counts fetch calls to `/api/queue`.
- The case page asks for `/api/users` only when the Reassign control can show.
- `http.ts`: a 2xx body that is not JSON is an `ApiError` (`bad_response`, fixed text); a 401 ends the session only if the request's token is still the current one.
- `session.ts`: `expire(message)` and `endedMessage()`; Sign in shows the server's message after a 401 and nothing after a plain Log out; memory only. The mock ends a session the same way.
- `config.ts`: with the mock off the Reassign control is never shown (`reassignCase` is planned, no backend route); `frontend/README.md` row updated.
- The case page shows Claim, Start investigating and Close case… at all times; one not allowed is disabled with a visible reason (`aria-describedby`), computed from the same rules as before. Back links use the outline button style and stay links.
- The dev-proxy item was already met (`scripts/run_preflight.py`, both READMEs); no change.

Branch `issue-131-frontend-follow-ups`, draft PR #227. Claim: https://github.com/andrew-chung-au/socboard/issues/131#issuecomment-6888398894. CI on `a3f4d92`, all success: `socboard verify` pull_request run 43671872887 (237 frontend tests, `VERIFY: PASS WITH WARNINGS`, each warning given a reason in the PR). QA PASS at `a3f4d92`, Lows only: https://github.com/andrew-chung-au/socboard/issues/131#issuecomment-6888573629.

Order with #31: #31 reformats every file ESLint reads, including the ones changed here, so it starts after this merges.

**What I learned:** two existing tests pinned behaviour the approved criteria change (buttons hidden, Reassign shown with the mock off); changing them, with the reason in the PR, was required, not a weakening.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** nothing notable; the frontend packages were installed and `make frontend-test` runs here in about 35 s.
**What nearly went wrong or was blocked:** none.
**One proposed change (file, expected effect, measure):** none.

## Launch usage

QA: 1 launch (PASS). PM: 3 grooming launches in the same session (#93, #214, #215). Active time and tool uses: unknown.

## Files created or modified

- `frontend/src/services/http.ts`, `frontend/src/services/session.ts`, `frontend/src/services/config.ts`, `frontend/src/services/mockService.ts`
- `frontend/src/routes/cases.$id.tsx`, `frontend/src/routes/login.tsx`
- `frontend/src/test/config.test.ts`, `frontend/src/test/http-service.test.ts`, `frontend/src/test/real-client.test.tsx`, `frontend/src/test/screen-behaviour.test.tsx`
- `frontend/README.md`
- `_session-summaries/2026-11-15T0329Z-issue-131-orchestrator-frontend-follow-ups.md` (this file)

## Decisions made by the human

- Assigned #131, then #31, and the grooming of #93, #214 and #215, on 2026-11-15.
- The PM's question (split the usability items?) was not answered; the body's default (keep them here) stands.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43671872887).
- **Frontend test:** `make frontend-test`.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- `tsc --noEmit` reports errors in test files on `main` (`contract-paths.test.ts`, `guardrails.test.ts`, `screen-behaviour.test.tsx` line 216); not touched here.

## Follow-ups for the next session

- QA Lows: a 2xx body of only whitespace gives `bad_response`; a 401 for a request that sent no token, with no session, still records an ended message (a `sentToken &&` guard would close it); Sign in reads the message at render without subscribing; the Actions block's indentation (fixed by #31's formatting).
- The human's look at the case page in a browser (disabled buttons and reasons, the back link's style).
