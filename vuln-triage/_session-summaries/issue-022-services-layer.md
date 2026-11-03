# Issue #022: Frontend services layer ready for a real API

**Date:** 2026-10-19
**Spec version:** 9f742d2

## What changed and why

- The `Services` interface is now the final frontend contract: `acceptRisk(id, reason)` takes the actor from the service session, and `getAsset`, `logout` and `currentUser` were added. The mock owns a persisted session (`sessionStorage`, key `vulntriage-services-user`); `logout` is idempotent.
- Typed `ServiceError` with `validation`, `not_found`, `conflict` and `unauthenticated`; every protected method rejects `unauthenticated` without a session; unknown ids now reject `not_found` instead of returning `null`.
- Assets use `ownerName`/`ownerEmail` (blank → `null`, ownerless only when both are null); the register form has two optional fields. Audit entries have unique `id`s used as React keys and store wire values (`open`, `risk_accepted`), with screens rendering through `STATUS_LABEL`.
- Screens import services only from `@/services`; demo credentials are exported there, not from `mockData`. `frontend/README.md` lists all nine methods, their errors and proposed HTTP calls.
- Protected docs were brought up to date: `AGENTS.md` and `agent-kit.conf` now record 35 tests; the spec states the partial-owner rule and US-1's two-field owner display.

## Files created or modified

- `759735a` implementation (14 files): `frontend/src/services/{types,index,mockService,mockData}.ts`; `frontend/src/components/vt/AuditTrail.tsx` (new) and `Badges.tsx`; seven route files; `frontend/src/test/vulntriage.test.tsx`; `frontend/README.md`.
- `f790ddc` Engineer's `_docs/ai-usage-log.md` entry.
- `9f742d2` protected spec change (human-approved, committed alone); `c85c6e8` protected `AGENTS.md`/`agent-kit.conf` test-count change (human-approved, committed alone).
- This summary and the orchestrator's usage-log entry.

## Decisions made by the human

- Mock session: services own it and persist it in `sessionStorage`; `lib/auth` stays in sync until #25 replaces it (option 1).
- `logout()` resolves idempotently; it is the only exception besides `login` to the unauthenticated rule.
- Owner fields: two optional trimmed fields; blank → `null`; partial owner allowed and not ownerless; no email validation this issue.
- Approved both spec notes (partial-owner rule, US-1 owner wording) in one spec commit, and the 10 → 35 test-count updates in `AGENTS.md` and `agent-kit.conf`.
- Accepted without a follow-up: no direct render test for partial-owner display (service/helper tests cover it). Keep the service session when a login attempt fails while signed in.

## Mismatches with the spec or design docs

None after the approved spec notes. QA's report that `_docs/ai-usage-log.md` was outside the issue is incorrect: the issue's Constraints list it.

## Commands to validate

- **Test:** `make frontend-test`: 2 files, 35 tests passed (baseline 10; floor 17).
- **Verify:** `make verify`: PASS WITH WARNINGS at `759735a`; 7 rewritten assertions, each stronger for the changed contract and individually justified.
- **Type check:** `frontend/node_modules/.bin/tsc --noEmit -p frontend/tsconfig.json`: exit 0 (not a configured project check).
- **Build frontend:** `make frontend-build`: exit 0.
- **Assert clean:** `make assert-clean`: PASS at `f790ddc`, HEAD unchanged after QA.

## Proposed AGENTS.md changes

Applied in `c85c6e8` with human approval. No pending changes.

## Temporary changes

- None. No process or server was started, nothing was installed, and no system configuration changed. `make clean-scratch` ran at close-out.

## Permission review

- Read-only (propose allowing): none.
- Writes to the record (keep asking): none; `gh issue edit`/`gh issue comment` and `make assert-clean` ran without stopping.
- Risky (propose denying): none.
- Proposed `opencode.json` and `.claude/settings.json` changes: none.

## Interruptions

None. PM, Engineer and QA each completed in one run; QA posted PASS (comment 6279190817) at `f790ddc`.

## Unrelated problems noticed but not fixed

- The Engineer added `public`/`ownerless` display code without a direct render test for the partial-owner case; the human accepted the service/helper coverage without a follow-up.
- A failed login while already signed in leaves the existing service session intact; the human chose to keep that behaviour.

## Follow-ups for the next session

- #23 (API contract: `_docs/api.md` and `_docs/openapi.yaml`) is next; #25 (connect the frontend) remains blocked by the planning phase line.
- No new follow-up issues were filed.
