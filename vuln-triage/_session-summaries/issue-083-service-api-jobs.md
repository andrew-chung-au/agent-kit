# Issue #83: Service API and notification jobs (task 10a)

**Date:** 2026-10-23
**Spec version:** (at `main` 35b6979)

## What changed and why

Task 10a of S1. The service-token operations are allowlisted and the backend
creates one top-tier notification job per finding lifecycle. The n8n
claim/report/digest behaviour and the MCP tools are Showcase, present here only
as contract-only stubs.

- **`api/service_settings.py`** — `get_n8n_api_token`/`get_mcp_api_token`/
  `get_responder_api_token`, read from the environment at call time (same
  pattern as `ingest/settings.py`).
- **`api/service_auth.py`** — bearer guards `require_n8n` / `require_mcp` /
  `require_responder`: `401` for a missing or invalid credential, `403` for a
  valid credential the operation does not list (another service token, or a
  session cookie). Constant-time token compare; no CSRF for bearer ops.
- **`api/service.py`**
  - Submission: `POST /signals/refresh` (re-score every asset, create top-tier
    jobs, idempotent; `202`), `POST /scans` (re-scan every asset; `202`),
    `GET /responder/findings/{id}` and `GET /responder/notification-jobs`
    (the US-15 responder's two reads; `ResponderNotificationJob` carries no
    recipient/advisory text).
  - Showcase stubs (contract-only, documented statuses): the three
    `/notification-jobs` ops, `GET /reports/weekly-digest`, and the three
    `/mcp/` ops. They enforce the allowlist and validate params, but run no
    claim/report/digest/MCP logic (tasks 32-35).
- **`ingest/notifications.py`** — A27 due windows (P1 7d / P2 14d / P3 30d /
  P4 90d), the `(lifecycle id, kind)` idempotency key, and `create_top_tier_jobs`:
  one `top tier` job per P1 `open` finding's lifecycle, with `entered_p1_at`,
  the real `due_at`, and a valid synthesised `traceparent` (real spans arrive
  with task 23). Idempotent via the `idempotency_key` unique constraint.
- **`ingest/scan.py`** — creates top-tier jobs after ranking.

## Files created or modified

- New: `backend/vulntriage/api/{service_settings,service_auth,service}.py`,
  `backend/vulntriage/ingest/notifications.py`.
- Modified: `backend/vulntriage/ingest/scan.py`, `backend/vulntriage/main.py`.
- Tests: new `tests/test_api_service.py` (n8n/responder allowlists, top-tier
  job + idempotency, stubs); `tests/test_smoke.py` route set.
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- Only the `top tier` job kind is created for submission; everything else is
  Showcase. The delivery worker (claim/email/`sent`/`failed`/ownerless hold) is
  task 37; the daily scheduler is task 38.
- `/signals/refresh` re-scores and creates jobs synchronously at pilot scale and
  returns `202`; if KEV/EPSS clients are on `app.state` it re-enriches first
  (the scheduler wiring is task 38).
- `traceparent` is synthesised as a valid, non-zero W3C value until task 23
  provides real `notification.enqueue` span contexts.
- `.env.example` left unchanged: the n8n/MCP tokens are Showcase and the
  responder token arrives with task 28 (`tasks.md`).

## Mismatches / VERIFY

- `I-CONTRACT` (task 14/#24) compares all operations; the showcase stubs exist
  for that. `I-JOBS`/`I-AUTH-N8N`/`I-LIFECYCLE`/`I-IDEMPOTENCY` are Showcase; the
  submission proof here is `I-RESP-*`, `I-SIGNALS` (the `signalsChanged` flag,
  from #80), and `I-OWNER-ONCE`'s job half (a second refresh makes no second job).

## Commands to validate

- **Verify (human):** `make verify BASE=origin/main` — NOT run here (no PyPI).
  All files byte-compile under CPython 3.12.13; the service-auth decision table,
  A27 due dates, the idempotency key and the traceparent format were validated
  standalone. **The human must run `make verify` before merge.**
