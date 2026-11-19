# Issue #290: O5 Instrument alert ingest

**Date:** 2026-11-17T01:49Z (UTC)
**Spec version:** 9cf7ed3

Tier: Standard (from the PM proposal; no tier label). Rubric: Observability, critical path to 2 points (`.kiro/steering/rubric-priority.md`). Track A of the lane split.

## What changed and why

`socboard/telemetry.py` adds a pure ASGI middleware that opens the server span for `POST /api/alerts` only (named from FastAPI's matched route, `traceparent` read with the SDK's propagator, status from a wrapped `send`, exception type only, lifespan and websocket passed through) and counts and logs refused ingests (401, 422, 429) as `outcome="refused"` with the fixed event `alert.refused`. `socboard/ingest.py` wraps the route body in the `ingest.alert` span with the two contract attributes, counts `accepted` with an exemplar and logs `alert.ingested`; responses, status codes, the audit entry and `openapi.yaml` are unchanged. `socboard/app.py` adds the middleware. `tests/test_telemetry_ingest.py` covers the trace id join, refusals, the thread pool, forced database and route errors and the canary test. Commits 8a1f8b8, a96a478, cdd765a (a test looked for the route at the top level of `app.routes`; FastAPI keeps included routers as one wrapper, found by CI before QA). PR #358.

QA PASS on the first check, Low findings only.

**What I learned:** CI catches structural test assumptions (route registration, SDK abstract methods) before QA; pushing the first commit pair early would save a launch.

## Reflection

### Engineer

**What slowed you down (evidence):** nothing could run here; FastAPI and SDK sources were read from the locked wheels.
**What nearly went wrong or was blocked:** the route-lookup test assumed a top-level route; CI caught it.
**One proposed change (file, expected effect, measure):** ask for a CI run on the first commit pair before writing further tests.

### QA

**What slowed you down (evidence):** mutation checks could only be read, not run.
**What nearly went wrong or was blocked:** grading `alert.refused`: the criterion names no event and the contract says names go there first.
**One proposed change (file, expected effect, measure):** in real-app tests, make route-derived values differ from their fallbacks so a test can tell them apart; measured by test gaps of this kind. The session's one proposal.

## Launch usage

- Engineer (build, CI fix): unknown (the tool did not report time or tool uses).
- QA: unknown.

## Files created or modified

- `socboard/telemetry.py`
- `socboard/ingest.py`
- `socboard/app.py`
- `tests/test_telemetry_ingest.py`
- `_docs/records/findings/290.json`
- this file

## Decisions made by the human

- none in this issue (the lane split and rubric priority are recorded in #289's summary and `.kiro/steering/rubric-priority.md`).

## Mismatches with the spec or design docs

- The contract's event table has no event for a refused ingest; the code uses `alert.refused` (F-290-1). A contract row needs its own pull request.

## Commands to validate

- **Verify:** CI-VERIFIED on cdd765a: verify run 43996874808 (`VERIFY: PASS`, 3621 passed; ingest telemetry tests 29 passed), image 43996874859, compose 43996874869, postgres 43996874804, all success.
- **Assert clean:** passed after QA at cdd765a.

## Proposed AGENTS.md changes

none

## Temporary changes

none (wheels downloaded to `.scratch/` for reading were deleted).

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-290-1: alert.refused is not in the contract's event table (Low).
- F-290-2: The caller's tracestate reaches the exported span (Low).
- F-290-3: Real-app tests cannot tell the route-derived span name from its fallback (Low).
- F-290-4: The refused count's exemplar, duplicate traceparent headers and a root path are untested (Low).
- F-290-5: The middleware docstring omits tracestate (Low).

## Follow-ups for the next session

- After the merge of #358: check the merged head, post the Close comment, run `make issue-close N=290`, and tell lane A #290 has merged (#295 needs it).
- The human decides whether `alert.refused` gets a contract row (its own small pull request) and whether to copy only `traceparent` (F-290-2, F-289-1).
- Next in track A: #291 (needs #289, #290, #338), then #312.
