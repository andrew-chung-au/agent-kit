# Issue #82: Findings, assets, re-scan and risk-acceptance API (task 9b)

**Date:** 2026-10-23
**Spec version:** (at `main` c824e98)

## What changed and why

Task 9b of S1. The frontend resource endpoints now work behind the session
guard and owner-match rule from task 9a (#81).

- **`api/findings.py`**
  - `GET /findings` — every finding joined with its asset, in the server's
    deterministic rank order (`ranked_findings`).
  - `GET /findings/{id}` — one finding with its asset; `401` then `404`.
  - `POST /findings/{id}/risk-acceptance` — accepts risk for the signed-in user.
    Error order exactly per the contract: `401` → CSRF `403` (guard) → `404` →
    owner-mismatch `403` → `422` (empty/whitespace/extra-field) → `409`
    (not `open`). Writes an audit entry (user, time, previous value, reason).
    No automated path sets `risk accepted` (US-11).
- **`api/serializers.py`** — the `Finding`/`FindingWithAsset` wire shape:
  aliases, `cveId`, derived `kev`/`kevStale`/`epss`/`epssStale`, dependency
  entries, a read-only `affectedRanges` projection of the merged advisories,
  the audit trail, and the joined asset. Briefs are Showcase, so `briefStatus`
  is always `pending` and `brief` is `null`.
- **`api/assets.py`**
  - `POST /assets` now requires a session and the `security lead` role (role
    `403` before body `422`); `GET /assets`, `GET /assets/{id}`,
    `PATCH /assets/{id}` (per-field audit, re-score via `rank_asset`, held-job
    release point), `POST /assets/{id}/rescan` (`202`; owner-match).
  - `asset_to_wire` now returns the latest finished scan's warnings.

The three write routes that need `404`/role/owner checks *before* body
validation read the raw body and validate it by hand (a pydantic body param
would `422` first).

## Files created or modified

- New: `backend/vulntriage/api/findings.py`, `backend/vulntriage/api/serializers.py`.
- Modified: `backend/vulntriage/api/assets.py`, `backend/vulntriage/ingest/ranking.py`,
  `backend/vulntriage/main.py`.
- Tests: new `tests/auth_helpers.py`, `tests/test_api_findings.py` (I-RISK +
  reads + error-order + owner-match + patch/rescan); updated
  `tests/test_api_assets.py` (authenticate as a security lead) and
  `tests/test_smoke.py` (route set).
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- The rescan owner-match reuses `may_accept_risk` (security lead → any; owner →
  match), which is exactly the reScan rule; the helper is not risk-specific.
- `_release_held_jobs` is a documented no-op placeholder: notification jobs are
  tasks 10a/37, so there is nothing to release yet. The release point is in the
  update path so the later work has an obvious home.
- Asset audit entries are stored (not part of the Asset response), per the
  contract.

## Mismatches / VERIFY

- `I-CONTRACT` (OpenAPI conformance) is task 14 (#24); this task implements the
  operations the contract already defines. The `getAsset` `mcpAuth` path is
  task 10b.

## Commands to validate

- **Verify (human):** `make verify BASE=origin/main` — NOT run here (no PyPI).
  All files byte-compile under CPython 3.12.13; the affected-range projection
  was validated standalone. **The human must run `make verify` before merge.**
