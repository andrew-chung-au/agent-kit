# Issue #34: frontend SPA shell (document owned by index.html, built stylesheet linked)

**Date:** 2026-10-21
**Spec version:** 97893c1

## What changed and why

- The Start-era `RootShell` (`<html>` rendered inside `#root`) is gone, and the Tailwind stylesheet is now imported by `main.tsx`, so `dist/index.html` links it statically (no FOUC, styled without JS).
- All static meta, including `og:*` and `twitter:card`, now lives in `frontend/index.html`; `head()` was deleted from `__root.tsx`.
- A regression test renders the real `routeTree` at `/` and asserts no `console.error` containing `cannot be a child of`. The Engineer ran it red against the unfixed shell first (1 failed, 61 passed), then green.

## Files created or modified

- Engineer `67419b2`: `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/routes/__root.tsx`, `frontend/src/test/app-routing.test.tsx` (comment only), `frontend/src/test/document-shell.test.tsx` (new).
- `d8c2ffe`: `_docs/ai-usage-log.md` (Engineer entry).
- Orchestrator close-out: `_docs/ai-usage-log.md`, `_docs/roadmap.md`, this summary.
- No protected file changed; `package.json`, the lockfile and the Vite/Vitest configs are untouched.

## Decisions made by the human

- D1 (PM comment 6326704884): all static meta in `index.html`, `head()` deleted (recommended). Recorded in comment 6328636205.
- D2: findings C (`vite-tsconfig-paths`) and D (`package.json` name) move out of #34 to #33 (recommended).
- QA criteria 9 and 10: approved a read-only `.scratch/` script that serves `dist/` on 127.0.0.1 and checks HTTP 200.
- Decision point: QA's outside-criteria risks are noted only, no follow-up issue; the `.scratch/` script is discarded.

## Mismatches with the spec or design docs

- none. The roadmap's "test count updated to 35 at grooming" is superseded: the criteria say "existing tests still pass plus the new regression test", and vitest printed 62.

## Commands to validate

- **Test:** `make test` (62 passed at `d8c2ffe`).
- **Build frontend:** `make frontend-build`; `dist/index.html` has exactly one stylesheet link.
- **Verify:** `make verify`: PASS (also run by the pre-push hook).
- **Assert clean:** `make assert-clean`: PASS at `d8c2ffe` after both QA runs.

## Proposed AGENTS.md changes

- none.

## Temporary changes

- none. QA started `make frontend-start` once (stopped with `make frontend-stop`) and a `.scratch/` static server for `dist/` that stopped itself. `make clean-scratch` ran at the end of the session.

## Permission review

PM and Engineer comments state no command needed approval. QA's first comment states none; its final comment lists the one merits request below. The orchestrator's `make` runs matched no `ask` rule.

- Read-only (propose allowing): `.scratch/check_dist_http.py`, a local-only (127.0.0.1) HTTP GET check of `frontend/dist/` (QA, merits request for local network access). Propose a `make` target if this check is wanted again; no settings change.
- Writes to the record (keep asking): none beyond the `make issue-comment` runs, which are allowed targets.
- Risky (propose denying): none
- Proposed `opencode.json` and `.claude/settings.json` changes: none

## Interruptions

- The session's worker process restarted after the QA re-check. `make assert-clean` had passed at `d8c2ffe` before the restart.

## Unrelated problems noticed but not fixed

- The jsdom tests load neither `index.html` nor the CSS, so nothing would catch the `/src/main.tsx` script tag or the CSS import going missing (QA risk; human chose note only).
- Sign-in reaching findings in a real browser was not machine-verified; criterion 9 passed on the clean dev-server start plus the routeTree tests.
- The `vite-tsconfig-paths` warning still prints in the build log (finding C, #33).

## Follow-ups for the next session

- Step 9 is done once #34 closes. Next: step 8b (#50), then step 10 (Stage 4 `_docs/testing.md`).
- #33 now also carries findings C and D from #34 (no pointer comment posted on #33; add one when it is groomed).
