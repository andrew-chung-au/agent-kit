# Issue #81: Session authentication and CSRF guard (task 9a)

**Date:** 2026-10-23
**Spec version:** (at `main` c6aad6b)

## What changed and why

Task 9a of S1. The frontend now authenticates with the `vt_session` cookie and a
CSRF header; the session guard is enforced. Resource endpoints and the
risk-acceptance payload are task 9b (#82).

- **`api/security.py`**
  - Argon2id `hash_password` / `verify_password` (`argon2-cffi`, human-approved).
  - Sessions: the cookie carries a random 256-bit id; only its SHA-256 hash is
    stored as the `sessions` PK. 30-minute idle + 8-hour absolute lifetime;
    each authenticated request bumps `last_seen_at`; an expired session row is
    deleted on the failing request.
  - `vt_session` cookie flags `HttpOnly; Secure; SameSite=Strict`.
  - `LoginThrottle`: 5 failed logins per username in 15 minutes → locked 15
    minutes; a locked username returns the same `401` as a wrong password, so the
    response never reveals whether the username exists. In-process (one backend;
    the spec needs no table).
  - `require_session` guard: `401` for no/expired/invalid session, then `403`
    for a wrong-consumer bearer credential or a missing/wrong
    `X-Requested-With: XMLHttpRequest` on a non-GET request (login/logout exempt).
  - `may_accept_risk` (A30): security lead anywhere; asset owner only where the
    asset's owner email matches theirs after trim + case-fold.
- **`api/auth.py`** — `POST /auth/login` (strict `{username, password}` → `User`
  + cookie, no bearer), `POST /auth/logout` (`204`, idempotent, no session/CSRF),
  `GET /auth/me` (`User` or `401`).
- **`main.py`** — registers the auth router and the login-throttle app state, and
  adds an HTTPException handler that renders the contract `{code, message}`
  Error shape.

## Files created or modified

- New: `backend/vulntriage/api/security.py`, `backend/vulntriage/api/auth.py`.
- Modified: `backend/vulntriage/main.py`, `backend/pyproject.toml` (`argon2-cffi`).
- Tests: new `tests/test_api_auth.py` (I-AUTH-SESSION + guard/lockout/owner-match).
- `_docs/ai-usage-log.md` entry.

## ⚠️ Human step required before verify

`backend/pyproject.toml` gained `argon2-cffi` (approved), but `backend/uv.lock`
is NOT updated — this sandbox has no PyPI access. Run **`make backend-lock`**
(then `make backend-install`) before `make verify`, or install fails on the
missing lock entry.

## Decisions made (pending human confirmation)

- `argon2-cffi` approved by the human (Option A).
- The login lockout counter is in-process (A30 names no persistence; one backend
  for submission).
- `.env.example` is unchanged: 9a introduces no new secret (sessions are
  DB-backed, no cookie-signing key).

## Mismatches / VERIFY

- `I-CONTRACT` (OpenAPI conformance) is task 14 (#24); this task implements the
  `/auth/*` operations the contract already defines.

## Commands to validate

- **Lock + verify (human):** `make backend-lock && make backend-install && make verify BASE=origin/main`
  — NOT run here (no PyPI). All files byte-compile under CPython 3.12.13; the
  dependency-free auth logic was validated standalone.
