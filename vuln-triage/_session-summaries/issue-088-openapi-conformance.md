# Issue #88: OpenAPI conformance and validation (task 14)

**Date:** 2026-10-23
**Spec version:** (at `main` 72158d0)

## What changed and why

Task 14 of S1. A backend test (`I-CONTRACT`) fails when FastAPI's generated
document diverges from `_docs/openapi.yaml`, and `make openapi-validate` still
validates the contract.

**Design decision (human-approved, Option A, 2026-10-23).** The routes are
hand-built (raw-body parsing, `dict` returns, `Depends` auth guards), so
`app.openapi()` carries no declared query/header parameters, no request or
response body schemas (except the `login` body), and no `security` block —
authentication is via `Depends`, which emits nothing. A deep schema compare is
therefore impossible against the generated document, and making the routes emit
a conforming document is tasks 9b/10a/10b, explicitly out of scope here. The
test compares the dimensions the routes actually express:

- the **path set**, with template variables normalised (`{finding_id}` ↔ the
  contract's `{id}`), excluding `GET /health` by name;
- the **method set** per path;
- the **success status code** per operation (201/202/204/200);
- the **security requirement** per operation, checked against the `Depends`
  guard on the route (`require_session`→cookieAuth,
  `require_session_or_mcp`→cookieAuth+mcpAuth, `require_n8n`→n8nAuth,
  `require_mcp`→mcpAuth, `require_responder`→responderAuth, none→public).

Ignored fields (named per the issue): `title`, `description`, `summary`,
`operationId`, `examples`; and — because the current routes do not declare them
— query/header parameters, request/response body schemas and the non-2xx
responses. `VERIFY:` a full schema/response/declared-`security` compare needs
`response_model` and declared parameters/security on every route (a task-9b/10
change).

The contract's `paths` block is parsed by a small, strict reader (no YAML
dependency added); any unexpected shape raises, so it cannot pass by
mis-parsing.

## Tests

- operation-set equality (generated == contract, normalised, /health excluded);
- method + success status per operation;
- security requirement per operation (via the guard);
- `/health` served-but-excluded still matches; a route not in the contract
  fails the comparison;
- a deliberate `.scratch/` contract mismatch (login's 2xx flipped to 299) fails.

## Files created or modified

- New: `tests/test_openapi_conformance.py`.
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- Option A granularity (above), human-approved.
- No YAML dependency: the contract paths block is read by a strict scoped parser.
- `_docs/openapi.yaml` not changed (read-only here); `make openapi-validate`
  unchanged.

## ⚠️ Could not run the suite here

The Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI), so
`make test` / `make verify` could NOT run. The test byte-compiles under CPython
3.12.13, and the strict contract parser was validated standalone against the
real `_docs/openapi.yaml` (22 operations; 16×200/3×202/2×204/1×201; cookieAuth
9, mcpAuth 4, n8nAuth 6, responderAuth 2; login/logout public). **The human must
run `make verify` before merge.**

## Commands to validate

- **Verify (human):** `make verify` — NOT run here (no PyPI).
