# Issue #111: upgrade Vite past the high-severity advisory

**Date:** 2026-10-24
**Spec version:** 9b04f90

## What changed and why

Prerequisite for #140 (task 20, the light security scan): the unchanged
`frontend/` tree had one high-severity finding, `vite@8.1.5` (GHSA-587h-7wmj-h5pm
/ CVE-2026-112942). The scan would have started red on a known finding. The bump
to the first patched version, `8.1.6`, clears it; `npm audit` now reports zero
high, zero critical and zero total findings. No application code or test changed.

## Files created or modified

- `frontend/package.json`: `vite` exact pin `8.1.5` -> `8.1.6`.
- `frontend/package-lock.json`: npm-generated; only the vite entry and lockfile
  metadata changed (`rolldown` stays `1.2.1`, `lockfileVersion` stays `3`).
- `Makefile`: new `frontend-audit` target (protected, human-approved, committed
  alone with `HUMAN_APPROVED=1`).
- `AGENTS.md`: records `make frontend-audit` (protected, human-approved, committed
  alone; approval record comment 6378131602).
- `_docs/ai-usage-log.md`: the Engineer's entry.

## Decisions made by the human

- Q1/D3: bump to exactly `8.1.6` (first patch on the 8.1 line), not `8.2.4`,
  `8.3.3`, or npm's suggested `8.3.5`.
- D2: add `make frontend-audit` (full `npm audit`) rather than a one-off command.
- Approved the npm network commands, `make install`, and the exact protected
  `Makefile` and `AGENTS.md` diffs.

## Mismatches with the spec or design docs

- The groomed #111 body recommended a one-off audit and refused a `Makefile`
  change; the human chose the reusable target instead. Recorded in the Engineer
  comment and covered by the approval record.
- The Engineer appended `_docs/ai-usage-log.md` at the orchestrator's request; the
  groomed text said the orchestrator would. The human confirmed both deviations
  at the decision point.

## Commands to validate

**Verify:** `make verify` -> PASS (87 frontend, 396 backend, 0 failed; type
check, whitespace and weakened-test checks clean).
**Test (frontend):** `make frontend-test` -> PASS (87).
**Type-check frontend:** `make frontend-typecheck` -> PASS.
**Audit frontend:** `make frontend-audit` -> `found 0 vulnerabilities`.

## Proposed AGENTS.md changes

Applied and committed: `068ce44` adds the **Audit frontend** command line.

## Temporary changes

None. No processes started; no system changes. `.scratch/` cleaned.

## Permission review

- Read-only (propose allowing): `npm audit --json` / `make frontend-audit`
  (network read for triage and verification; merits request and bash `*` ask
  rule); read-only `.scratch/` checks (bash `*` ask rule); `make issue-dump`.
- Writes to the record (keep asking): `make install` twice (network dependency
  install; merits request under the issue's Verification/Approval criteria);
  `npm install --save-dev --save-exact vite@8.1.6` (dependency change and
  network; merits request); editing `Makefile` (protected file; merits request
  and edit ask rule); `HUMAN_APPROVED=1 git commit` (protected commit; bash `*`
  ask rule); `make issue-comment` (issue record; `make *` allow).
- Risky (propose denying): none.

## Interruptions

None. PM, Engineer and QA each completed in one run.

## Unrelated problems noticed but not fixed

- `_docs/testing.md` still says the CI `security-scan` job runs only
  `make security-scan`; #140's groomed body adds `make security-scan-selftest`.
  That is a #140 spec note.
- `npm audit --omit=dev` and the `vite` peer/dev marker need the `VERIFY:` check
  in #140.

## Follow-ups for the next session

- #140 (task 20): implement the light security scan with the human's Q1 (OSV
  post-processing) and Q2 (fail closed) decisions.
