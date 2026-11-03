# Issue #85: Frontend dashboard read views (task 11)

**Date:** 2026-10-23
**Spec version:** (at `main` 2ec3d05)

## What changed and why

Task 11 of S1. The dashboard read views for assets and ranked findings. The
views, components and the `frontend/src/services/` layer were already built by
the #34/#45 SPA-shell work; this task confirms they meet the US-1/4/5/6
acceptance criteria and adds the named `F-ASSET` and `F-STATUS` test cases the
Stage 4 strategy calls for.

- **`F-ASSET`** (US-1) — renders `/assets` and asserts each asset shows the
  owner's name and email (or an ownerless marker when both are unset),
  criticality, and the internet-facing flag; and that a partial owner is shown,
  not flagged ownerless.
- **`F-STATUS`** (US-4/5/6) — asserts a finding shows exactly one KEV value
  (`listed` / `not listed` / `n/a (no CVE)`), an EPSS score or `n/a`, a stale
  marker when a signal is stale, and the owning asset's criticality and
  exposure (US-4); the rank reason on every finding and the deterministic order
  the services layer returns, never re-sorted (US-5); and the three brief
  states — available-with-matching-fix, "brief pending", and "brief
  unavailable" (US-6). It also checks every finding status renders.

No view code changed: the existing screens already satisfy the criteria, and
the task's deliverable is the confirming `F-ASSET`/`F-STATUS` coverage.

## Files created or modified

- Modified: `frontend/src/test/vulntriage.test.tsx` (the two describe blocks).
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- The dashboard read views were complete from the SPA shell, so #85 is scoped
  to the named test coverage and a confirmation pass against the US criteria.
  No new view, service field or dependency was added.

## ⚠️ Could not run the frontend suite here

The Kiro Web sandbox blocks the npm registry (`registry.npmjs.org` 403), so
`npm ci`, `make frontend-test` and `make frontend-typecheck` could NOT run. The
new tests use only symbols already imported in the suite and assert against the
existing components' real markup (checked by reading `FindingsTable.tsx`,
`Badges.tsx`, the routes and `mockData.ts`). **The human must run `make verify`
(which runs the frontend suite and the type check) before merge.**

## Mismatches / VERIFY

- None. The screens use the single services layer and add no field beyond the
  contract; briefs are shown as `brief`/`briefStatus` as the contract provides.

## Commands to validate

- **Verify (human):** `make verify` — NOT run here (npm registry blocked).
