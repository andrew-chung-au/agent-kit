# Issue #84: MCP and responder read APIs (task 10b)

**Date:** 2026-10-23
**Spec version:** (at `main` 5642a56)

## What changed and why

Task 10b of S1. The three MCP read operations (stubs from #83) are now real, and
`GET /assets/{id}` accepts the MCP token as well as a session cookie. The two
responder read operations were built in #83 (task 10a) and are re-covered here.

- **`GET /mcp/top-exposures`** — `RankedFinding[]`, open findings only, in server
  rank order; `limit` 1-50 (default 10); `assetId` optionally filters, and an
  unknown `assetId` is `404`.
- **`GET /mcp/vulnerabilities/{alias}/assets`** — `AffectedAssets`: resolves any
  alias (CVE/GHSA/PYSEC) to its vulnerability and lists every finding in any
  status with its asset. Unknown alias → `known: false`,
  `untrustedAdvisoryData: null`, `assets: []` (never `404`); known with no
  finding → `known: true`, empty assets. The two are distinguishable by `known`.
- **`GET /mcp/findings/{id}`** — `McpFinding` = `FindingWithAsset` plus the
  labelled `untrustedAdvisoryData` (US-12 boundary): every advisory's summary,
  details and references as JSON strings, under the fixed label. No advisory
  text appears anywhere else or as instructions.
- **`GET /assets/{id}`** — now guarded by `require_session_or_mcp`: a valid
  session cookie or the MCP token; the n8n/responder token is `403`. It is the
  only operation two consumers share.

The MCP token is GET-only: every write with it is `403` and changes no state;
there are no write tools.

## Files created or modified

- Modified: `backend/vulntriage/api/service.py` (real MCP reads),
  `backend/vulntriage/api/serializers.py` (`untrusted_advisory_data`,
  `ranked_finding_to_wire`, `UNTRUSTED_LABEL`),
  `backend/vulntriage/api/service_auth.py` (`require_session_or_mcp`),
  `backend/vulntriage/api/assets.py` (`getAsset` dual consumer).
- Tests: new `tests/test_api_mcp.py` (I-MCP, I-AUTH-MCP; responder I-RESP-*
  already in `tests/test_api_service.py`).
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- The MCP operations are Showcase; the MCP server with its four tools is task
  32. This task builds the read API behind them so task-14 conformance and the
  US-12 untrusted-data boundary hold.
- `untrustedAdvisoryData` uses the exact fixed label from architecture § MCP
  server; references are returned as plain strings, never auto-linked.

## Mismatches / VERIFY

- `I-CONTRACT` (task 14/#24) compares all operations. `S-MCP` output tests
  belong to task 32. No route paths changed from #83, so `test_smoke` is
  unchanged.

## Commands to validate

- **Verify (human):** `make verify BASE=origin/main` — NOT run here (no PyPI).
  All files byte-compile under CPython 3.12.13. **The human must run `make
  verify` before merge.**
