# Issue #183: Refuse ingest above a configured rate and store none of the excess

**Date:** 2026-11-14T12:34Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`POST /api/alerts` now accepts at most `SOCBOARD_INGEST_MAX_REQUESTS` requests with a valid ingest key per `SOCBOARD_INGEST_WINDOW_SECONDS` (default 60 per 60 seconds). Above that it answers 429 `rate_limited` with `Retry-After` and stores nothing. The limit is on the ingest key, not the `source` field, which a caller can change on every request.

- `socboard/ratelimit.py`: `IngestLimiter`, one deque of at most N timestamps, check and count in one step under a lock; a refused request is not counted.
- `socboard/auth.py`: `limit_ingest_rate`, the second route dependency after `require_api_key`, so the order is 401, 429, then the schema 422. A request with the key counts even if its body is then refused with 422; a wrong or missing key counts for nothing.
- `socboard/ingest.py` (`resolve_ingest_limiter`, the dependency list), `socboard/app.py`, `socboard/settings.py` (two entries), `openapi.yaml` (429 on `ingestAlert`), README, the example env file.

Worked by the Hardening session, Standard tier, no Engineer launch. Branch `issue-183-ingest-limit`, PR #184, merge commit `9ff7ce6`, head `64def37`. Claim: https://github.com/andrew-chung-au/socboard/issues/183#issuecomment-6876811905. QA PASS at `64def37`: https://github.com/andrew-chung-au/socboard/issues/183#issuecomment-6876917692.

**What I learned:** `tests/test_data_audit.py` forbids the string `ApiHTTPException` in any module outside a short list of HTTP-layer files, so the 429 dependency belongs in `auth.py`. The first push failed on it (run 43591865756); I should have read the architecture tests before choosing where the dependency lived.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

What slowed me down: one CI round for the architecture test above. What nearly went wrong: nothing blocked. Proposed change: none (one finding from this session is already recorded in #178's summary).

## Launch usage

QA: 1 launch (pass at `64def37`). Active time and tool uses were not given: unknown.

## Files created or modified

- `socboard/ratelimit.py`, `socboard/auth.py`, `socboard/ingest.py`, `socboard/app.py`, `socboard/settings.py`
- `openapi.yaml`, `README.md`, `.env.example`
- `tests/test_ingest_limit.py` (new), `tests/test_ingest_contract.py` (expects the 429), `tests/test_settings.py`, `tests/conftest.py` (one line)
- `_session-summaries/2026-11-14T1234Z-issue-183-orchestrator-ingest-limit.md` (this file)

## Decisions made by the human

- The ingest defaults (60 per 60 seconds) were approved with the D8 recommendations.
- Applied the `approved` label ("approved labelled").
- Merged PR #184.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43592155829 and 43592159986 on `64def37`: 1999 Python tests, 209 frontend tests).
- **Contract check:** not run on its own in the sandbox; the ingest contract tests passed in CI.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- Low findings left: a valid-key request whose body is not parseable JSON gets 422 before any dependency runs and is not counted (documented order, nothing stored; no test pins it); the concurrency test exercises the limiter, not the route; the README does not cite decision 9 by name.
