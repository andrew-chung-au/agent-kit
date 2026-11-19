# Issue #15: Queue and case-detail read API

**Date:** 2026-11-13T03:00Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked it by the human's ruling, and Claude Code takes #16 after it merges. Ponytail was on; this is the fourth issue in the ponytail group. Draft PR #109, stacked on #14 until #14 merged, then merged with `main`.

- **Endpoints:** `socboard/cases.py` adds `GET /api/queue` and `GET /api/cases/{id}`, both behind #13's bearer token. They are read-only: no writes and no audit entries.
- **Queue order:** an explicit severity rank (Critical first), then the alert timestamp oldest first, then the case id.
- **Bad ids:** an unknown or invalid id gives 404 `not_found` and never a 500.
- **Schemas:** `Note`, `CaseDetail` (a subclass of #14's `CaseSummary`) and `QueueResponse` are in `socboard/schemas.py`, with the router registered in `socboard/app.py`. Tests are in `tests/test_queue_api.py` and `tests/test_queue_contract.py`.
- **Rounds:** two Engineer rounds. In round 1 at `fa14ac1`, the #11 test flagged `ApiHTTPException` in `cases.py`. By the human's ruling, `cases.py` was added to that test's set of HTTP-layer file names, following #13's `auth.py`. That widens an exemption and removes no assertion.
- **CI at `58669f7`:** pull-request run 43354534335 and push run 43354528112 both show 1284 passed, 157 frontend passed and VERIFY: PASS, with `Assertion lines: 238 added, 0 removed`.
- **QA:** PASS at `58669f7`, with all eight criteria met. A bypass script tried 23 hostile ids, every token kind and a replay of the queue order; all held.
- **Reviewer (ponytail):** "Ship", with six findings and about 25 lines that could go. None was applied; all six move to #110.

**What I learned:** the stacked branch let #15 run through Engineer, CI and QA while #14 waited to merge. Merging `main` in afterwards brought only docs.

## Reflection

### PM

unknown (role not asked)

### Engineer

From the completion comment, unchanged:

- Declaring the 422 on a route whose input cannot fail is a small lie in the generated schema; the choice is the human's.
- I ran two read-only git commands in parallel once (before the first commit), against the instruction; no harm, nothing changed.
- The `ingestedAt < servedAt` assertion relies on a clock that ticks between ingest and read; true on Linux CI.

### QA

unknown (QA's comment has no Reflection block).

### Ponytail

Engineer: "Reused `CaseSummary`, `User.from_row`, `current_user`, `get_session`, `from_public_id`, `ApiHTTPException` and the `create_users_router(prefix)` pattern … Skipped: a pagination or filter option, a shared summary builder with ingest, caching." The Reviewer's top finding was that shared builder (15-1).

## Launch usage

Active time and tool uses are unknown, because Kiro Web reports neither. Tool: Kiro; model: unknown. Launches: Engineer 2, QA 1 (PASS), Reviewer 1.

## Files created or modified

`socboard/cases.py` (new), `socboard/schemas.py`, `socboard/app.py`, `tests/test_queue_api.py` (new), `tests/test_queue_contract.py` (new), `tests/test_data_audit.py` (one file name added, by ruling), `_docs/planning/roadmap-1-core.md` (#110 note), this file.

## Decisions made by the human

- `cases.py` was added to the HTTP-layer set in `tests/test_data_audit.py`. #107 will move that list to one place.
- `getCase` declares the contract's `ApiError` 422 as the one named difference. A later contract issue may add it to `openapi.yaml` (the Engineer's spec note).
- Finding 15-1: useful (smaller). Finding 15-2: correct-minor. Finding 15-3: correct-minor. Finding 15-4: correct-minor. Finding 15-5: correct-minor. Finding 15-6: useful (scope; QA had also raised it). QA had raised none of the others. None was applied; all move to #110.
- Accepted QA risks: an over-long test line; `/api/cases/` with an empty id gets the framework's 404; no #15 HTTP test uses an expired token (#13 covers expiry).
- A case's "age" is the alert's own timestamp.

## Mismatches with the spec or design docs

- `openapi.yaml` `getCase` has no 422, but FastAPI adds one. The contract test names and accepts this one difference. It should be resolved in a later contract issue.

## Commands to validate

- **Verify:** `make verify` (CI runs 43354534335 and 43354528112 at `58669f7`).

## Proposed AGENTS.md changes

none.

## Temporary changes

none. The orchestrator runs `make clean-scratch` at the end of this session.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The queue has no paging (15-6). It is fine at the expected load and is recorded for #110.

## Follow-ups for the next session

- Claude Code takes #16 (claim and single owner), then #17.
- #110 now also holds #15's findings. #107 holds the HTTP-module list.
