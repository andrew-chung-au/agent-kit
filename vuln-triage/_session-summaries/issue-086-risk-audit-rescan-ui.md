# Issue #86: Risk acceptance, audit trail and re-scan UI (task 12)

**Date:** 2026-10-23
**Spec version:** (at `main` 84e3d29)

## What changed and why

Task 12 of S1. The dashboard write path: a signed-in human accepts risk with a
reason, sees the audit trail, and requests a manual re-scan. The write views
(accept-risk form, `AuditTrail` component, per-row re-scan button) and the mock
`acceptRisk`/`reScan` service were built by the #34/#45 SPA shell; this task
confirms US-10/US-11 and adds the named `F-STATUS` write-path coverage.

Added `F-STATUS write path` tests that exercise the real UI and service:
- **US-11 accept** — a security lead accepts with a reason through the form;
  the finding becomes `risk accepted` and the audit trail records the signed-in
  user (the "who"), the time, the previous value and the reason.
- **US-11 reason** — an empty or whitespace-only reason is refused on the form
  and the status does not change.
- **US-11 owner-match** — a security lead may accept on any finding; an asset
  owner only where the asset `ownerEmail` matches theirs (trim + case-fold); a
  mismatch is refused on the screen and changes nothing.
- **US-11 non-open** — a non-open finding offers no accept form and the service
  refuses it with `conflict`; no automated path sets `risk accepted` (only
  `acceptRisk` does, via a human; a re-scan never does).
- **US-10 re-scan** — a signed-in user requests a manual re-scan from the
  assets list (`POST /assets/{id}/rescan`); the scan status is unchanged until
  the scan finishes. A rejected write maps to `ServiceError` and shows its
  message.
- The `AuditTrail` component renders who/when/previous/new/reason.

No view or service code changed: the screens already satisfy the criteria.

## Files created or modified

- Modified: `frontend/src/test/vulntriage.test.tsx` (the `F-STATUS write path`
  describe block).
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- The write views were complete from the SPA shell, so #86 is the confirming
  `F-STATUS` write-path coverage; no new view, service field or dependency.
- The custom CSRF header is a concern of the real API-backed `Services`
  implementation (built later); the mock layer has no HTTP, so it enforces the
  error-to-`ServiceError` mapping and the behaviour only. VERIFY for the real
  client.

## ⚠️ Could not run the frontend suite here

The Kiro Web sandbox blocks the npm registry (`registry.npmjs.org` 403), so
`make frontend-test` / `make frontend-typecheck` could NOT run. The new tests
assert via `getByRole`/`getByLabelText` and direct service state (no ambiguous
text matches), checked against the real `accept` route, `AuditTrail.tsx`, the
assets route and `mockService.ts`. **The human must run `make verify` before
merge.** `I-RISK` (the backend half) already passes from #82.

## Commands to validate

- **Verify (human):** `make verify` — NOT run here (npm registry blocked).
