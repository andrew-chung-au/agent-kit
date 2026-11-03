# Issue #021: Frontend clean-up — remove Lovable coupling and unused code

**Date:** 2026-10-19
**Spec version:** d3a8f11

## What changed and why

- The frontend no longer depends on the app-builder platform: `frontend/src/lib/lovable-error-reporting.ts` and its call site are gone, along with `frontend/AGENTS.md`, `frontend/.lovable/`, the `twitter:site` meta and the two Google Fonts links (replaced by system font stacks).
- `frontend/vite.config.ts` is an explicit config (tailwindcss, vite-tsconfig-paths, `tanstackRouter`, react; `VITE_*` injection, `@` alias, dedupe, `lightningcss`); the shared preset import is gone. Render mode is plain TanStack Router + Vite (client-only SPA), built to `frontend/dist/`.
- 42 unused `src/components/ui/*.tsx` files and the packages only they used are removed; `frontend/bun.lock` and `frontend/bunfig.toml` are gone, and `frontend/.npmrc` carries `min-release-age=1` (review item E).
- The three server-only files (`src/server.ts`, `src/lib/error-capture.ts`, `src/lib/error-page.ts`) and `src/start.ts` are removed; `frontend/index.html` and `frontend/src/main.tsx` mount the plain router. `@tanstack/react-start` and `nitro` are removed and the lockfile pruned.
- `frontend/README.md` is rewritten (what the app is, make targets, render mode and `frontend/dist/` output, provenance, architecture notes, the services methods list unchanged from #15).
- Protected commit `682c69f` (human-approved, committed alone) adds the `frontend-build` target and its `.PHONY` entry to `Makefile` and the one Build line to `AGENTS.md`.
- QA PASS at `682c69f`: all acceptance criteria and refused cases; `make verify` PASS; `make frontend-build` writes `frontend/dist/index.html`; the built output serves HTTP 200; the source app renders in jsdom from login through demo sign-in to findings.

## Files created or modified

- Commits `c816d51` (clean-up), `e65448e` (refused-case grep fixes), `e367e49` (render mode: plain TanStack Router + Vite), `682c69f` (protected Makefile/AGENTS.md, `HUMAN_APPROVED=1`); logs/summaries in `31af1a2`, `25c9b68`, `41c42ca`.
- Removed: `frontend/bun.lock`, `frontend/bunfig.toml`, `frontend/AGENTS.md`, `frontend/.lovable/project.json`, `frontend/src/lib/lovable-error-reporting.ts`, 42 `frontend/src/components/ui/*.tsx`, `frontend/src/server.ts`, `frontend/src/lib/error-capture.ts`, `frontend/src/lib/error-page.ts`, `frontend/src/start.ts`.
- Added: `frontend/.npmrc`, `frontend/index.html`, `frontend/src/main.tsx`. Modified: `frontend/README.md`, `frontend/vite.config.ts`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/src/routes/__root.tsx` (Lovable coupling only), `frontend/src/styles.css` (fonts), `frontend/src/routeTree.gen.ts` (regenerated, Start augmentation dropped), `Makefile`, `AGENTS.md`.
- `agent-kit.conf` unchanged; no test file deleted or changed.

## Decisions made by the human

- `frontend/.npmrc` ownership (2026-10-19, option 1): #21 adds `min-release-age=1`; #33 hardening D later appends `ignore-scripts=true`.
- Render mode (2026-10-19, Orchestrator comment 6276301196): **option 3, plain TanStack Router + Vite**, production output `frontend/dist/` with `frontend/dist/index.html`. This ends the `src/server.ts` network-grep exception.
- Protected `Makefile` `frontend-build` target approved as proposed; protected `AGENTS.md` gets one Build line. Applied and committed alone in `682c69f`.
- End this session after #21; do not start #22.
- Do not run `uptime` or similar nonessential system probes unless a task requires it.

## Mismatches with the spec or design docs

None. `_docs/specs.md` covers product behaviour; render mode, npm configuration and frontend tooling are not in it, and no spec change is proposed.

## Commands to validate

- **Install:** `make install` / `make frontend-install`: `npm ci`, 351 packages, lockfile stable. `npm --prefix frontend config get min-release-age` prints `1`.
- **Test:** `make test` and `make frontend-test`: 2 files, 10 tests passed (baseline unchanged).
- **Verify:** `make verify`: PASS (tests 10/10, whitespace PASS, weakened tests none).
- **Build frontend:** `make frontend-build`: exit 0, writes `frontend/dist/index.html` (963 bytes) plus `frontend/dist/assets/` (main bundle 305233 bytes); output is git-ignored.
- **Serve:** QA served `frontend/dist/` with `python3 -m http.server`; `GET /` and the main asset returned HTTP 200.
- **Run:** `make frontend-start` then `/` and `/login` HTTP 200; QA rendered the source app in jsdom from login through demo sign-in to findings (8 rows); `make frontend-stop` stops only the recorded PID.
- Refused-case greps: `grep -rni lovable frontend --exclude=package-lock.json` → one hit (README provenance); no `@lovable.dev`; no `npm i`/`npm install` in the README; network grep → `src/services/mockData.ts` only (the `src/server.ts` exception has ended).

## Proposed AGENTS.md changes

Applied in `682c69f` with human approval. No pending changes.

## Temporary changes

- Render-mode spike configs `frontend/vite.spa-evidence.config.ts`, `frontend/vite.node-evidence.config.ts`, `frontend/vite.router-evidence.config.ts` and the build outputs `frontend/.output`, `frontend/node_modules/.nitro` were created for evidence and deleted.
- `.scratch/` servers (`node-build-start.sh`/`node-build-stop.sh` on `127.0.0.1:3100`, `serve_check.py` on `127.0.0.1:8137`, and the QA dev check) were started and stopped by their own scripts; `make clean-scratch` ran at close-out.
- No system configuration changed; nothing installed outside `frontend/node_modules` and `frontend/dist`.

## Interruptions

None. QA ran at `682c69f` and posted PASS (comment 6277400761).

## Unrelated problems noticed but not fixed

- `frontend/src/routes/__root.tsx`'s root `shellComponent` now renders `<html>` inside `#root`; React warns "In HTML, `<html>` cannot be a child of `<div>`. This will cause a hydration error." Content still rendered in jsdom. QA reported this outside the criteria; a follow-up issue is proposed.
- The built `frontend/dist/index.html` has no stylesheet `<link>`; CSS is injected at runtime by `HeadContent`, so a JS-less or slow load is unstyled (FOUC). QA reported this outside the criteria; a follow-up issue is proposed.
- `vite-tsconfig-paths` logs a Vite 8 native-resolution warning on every build; `frontend/package.json` still carries the leftover name `tanstack_start_ts`.
- `682c69f` bundles the `Makefile` and `AGENTS.md` changes in one protected commit; the human approved both together, but the process text prefers separate protected commits.

## Follow-ups for the next session

- Human decision pending: file follow-up issue(s) for the `shellComponent` DOM-nesting/hydration risk and the missing stylesheet link, and decide whether to fold in the `vite-tsconfig-paths` warning and the `package.json` name.
- #22 (services interface and README methods list) and #23 (API contract) remain; #33 is deferred.
- #21 is closed; nothing was started for #22 in this session.

## Permission review

- Read-only commands (propose allowing): none stopped for approval.
- Writes to the record (keep asking): `HUMAN_APPROVED=1 git commit` for the protected `Makefile`/`AGENTS.md` change (human-approved in this session); `gh issue close` for #32 and #21 (currently `ask` in `opencode.json`).
- Risky (propose denying): none.
- No system configuration change, install or network command was requested in the sandbox.
