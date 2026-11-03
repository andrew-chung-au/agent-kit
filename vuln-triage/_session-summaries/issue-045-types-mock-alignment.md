# Issue #45: align frontend types, mock and screens with the OpenAPI contract (also: #50 groomed and placed)

**Date:** 2026-10-21
**Spec version:** 97893c1

## What changed and why

- #45 (D4 from #23): `types.ts`, `mockData.ts`, `mockService.ts`, the screens and the tests now match `_docs/openapi.yaml` and the D4 table in `_docs/api.md`. This unblocks step 9 (#34) and #25. The frontend still uses the mock only and makes no network request.
- New behaviour: `forbidden` as the fifth error code; `acceptRisk` checks in contract order; `reScan` in `Services` and the mock; a second demo user (`asset owner`); a per-row Re-scan button on the assets list; `validateRepositoryUrl` and `validateOwnerEmail`; an old-shape stored session counts as signed out. The suite went from 35 to 61 tests.
- `make frontend-typecheck` (`tsc --noEmit`) added, because `vite build` does not type-check.
- The hard-coded test count was removed from `AGENTS.md`, `agent-kit.conf` and `frontend/README.md` (the human asked for it not to be maintained by hand).
- #50 (US-15 responder read-only contract) was groomed with the human's decisions and placed in the roadmap as step 8b.

## Files created or modified

- Engineer `72903cc`: `frontend/src/services/types.ts`, `mockData.ts`, `mockService.ts`, `frontend/src/lib/auth.ts`, `validation.ts`, `frontend/src/routes/_authed.tsx`, `_authed.assets.index.tsx`, `_authed.assets.new.tsx`, `_authed.findings.$findingId.tsx`, `_authed.findings.$findingId_.accept.tsx`, `frontend/src/components/vt/AuditTrail.tsx`, `Badges.tsx`, `FindingsTable.tsx`, `frontend/src/test/vulntriage.test.tsx`; `a2d3bd9`: `_docs/ai-usage-log.md`.
- Protected, each committed alone with `HUMAN_APPROVED=1` and an approval record on #45: `Makefile` (`0d5197b`, record 6325795173), `AGENTS.md` (`3f55509`, record 6325796249), `AGENTS.md` (`4e10afe`, record 6326025911), `agent-kit.conf` (`b18157c`, record 6326028192).
- `frontend/README.md` (`6447082`), `_docs/roadmap.md` (`ec7b49c` and the closing check-in), `_docs/ai-usage-log.md`, this summary.

## Decisions made by the human

- #45 D1 a second `asset owner` demo user; D2 a per-row Re-scan button; D3 `AuditEntry.source` values from `api.md`/`architecture.md`; D4 a `frontend-typecheck` target. All were the recommended options.
- #50 D1 logs from Loki only; D2 a responder-only job schema; D3 no `untrustedAdvisoryData`; roadmap row 8b after #45. All recommended.
- Approved the Makefile and AGENTS.md typecheck changes; left the accept screen's client-side reason check as it is.
- Asked for the test count to be dynamic (not hard-coded); approved the three-file rewording.
- Chose to file both QA verify-gate gaps as a follow-up under Later (#53).

## Mismatches with the spec or design docs

- `AuditEntry.source` is an untyped string in `_docs/openapi.yaml`; the PM's grooming assumed an enum. The Engineer used `dashboard` and `OSV`, both named in `_docs/architecture.md` line 113. A tighter contract could be a later change to #23's output.
- `_docs/api.md`'s D4 table does not list the `acceptRisk` check-order change; the PM suggested adding a D4 row.
- #50's spec notes (three proposed `architecture.md` wording changes, including `RESPONDER_API_TOKEN` in the secrets row) are still open and need approval when #50 is worked.

## Commands to validate

- **Test:** `make test` (61 passed at `3f55509`).
- **Type-check frontend:** `make frontend-typecheck` (exit 0).
- **Verify:** `make verify`: PASS WITH WARNINGS before the final push (7 assertion lines rewritten from old wire values to contract values, none deleted); PASS on the last push.
- **Assert clean:** `make assert-clean`: PASS at `3f55509` after QA.

## Proposed AGENTS.md changes

- none new. The Test (all) line and the Type-check line were already approved and committed.

## Temporary changes

- none. The Engineer applied the Makefile patch temporarily to test it and reverted it. `.scratch/` is cleaned with `make clean-scratch` at the end of the session.

## Permission review

PM (#45), PM (#50), PM (#53 draft) and QA comments or reports state no command needed approval. The Engineer's comment states no `ask` rule matched and no merits request was made; the only gate was the protected-file rule.

- Read-only (propose allowing): none
- Writes to the record (keep asking): GitHub MCP `issue_write` create for #53 (merits request); `HUMAN_APPROVED=1 git commit` for `Makefile`, `AGENTS.md` (twice) and `agent-kit.conf` (merits requests: protected commits)
- Risky (propose denying): none
- Proposed `opencode.json` and `.claude/settings.json` changes: none

## Interruptions

- The session's worker process restarted after QA. `make assert-clean` had passed at `3f55509` before the restart, and `git status` and the pushed branch showed nothing lost.

## Unrelated problems noticed but not fixed

- `make verify` run by hand compares against `origin/<branch>`; when that equals HEAD it compares nothing (filed as #53, together with the type check not being in the gate).
- QA noted the owner demo credential is exported from `mockData.ts` and shares the analyst's password. It is mock-only and not shown on the login screen.
- The accept form checks the reason on the client before the service, so an owner mismatch with an empty reason shows the validation message in the UI. The service returns `forbidden` in contract order. Note for #34 and #25.
- `_docs/api.md` line 198 and `_docs/cloud-sessions.md` still say "35 tests" (historical trial results and the D4 follow-up description); they were not changed.

## Follow-ups for the next session

- Step 9 (#34) is unblocked; #50 (step 8b) runs before step 10.
- #53 (verify gate gaps) is under Later and needs grooming and the human's choice between warning, procedure change, or both for gap 2.
- `make clean-scratch` was run at the end of this session.
