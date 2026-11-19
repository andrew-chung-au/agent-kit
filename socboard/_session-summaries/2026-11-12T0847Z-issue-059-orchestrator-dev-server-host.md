# Issue #59: Dev server unreachable from the browser in the dev container

**Date:** 2026-11-12T08:47Z (UTC)
**Spec version:** 185bb50

Tier: Standard (from the PM proposal; no tier label).

## What changed and why

`frontend/vite.config.ts` now sets `server.host` to `"127.0.0.1"` (commit a3998e4), so the dev server answers on the IPv4 loopback address that the dev container's forwarded port uses, and still listens on no other interface. The dev URL wording in the `AGENTS.md` Frontend dev server line and the `Makefile` `frontend-start` help text changed from `http://localhost:5173/` to `http://127.0.0.1:5173/` (commit 7cbf7d6, protected files, `HUMAN_APPROVED=1`, after the human approved the two exact one-line diffs). `frontend/README.md` names no URL, so it is unchanged.

**What I learned:** QA noted that a browser's `localhost` may resolve to `[::1]` first, so `http://localhost:5173/` may still fail; the docs now name the IPv4 address.

## Reflection

Not asked in this session.

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer: 181074 ms, 25 tool uses
- QA: 124760 ms, 18 tool uses
- (Same session, not #59: a general-purpose advisory launch for the #11 questions, 244178 ms, 14 tool uses; it changed no project file.)

## Files created or modified

- `frontend/vite.config.ts` (a3998e4)
- `AGENTS.md`, `Makefile` (7cbf7d6)
- `_session-summaries/2026-11-12T0847Z-issue-059-orchestrator-dev-server-host.md`

## Decisions made by the human

- Approved the two protected-file URL edits (`AGENTS.md` Commands line, `Makefile` help text), asked for as exact one-line diffs.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify` (PASS after both commits: 121 Python tests, 157 frontend tests).
**Frontend dev server:** `make frontend-start`, then `curl http://127.0.0.1:5173/` returns 200; `make frontend-stop`.

## Proposed AGENTS.md changes

none (the URL edit above is already applied)

## Temporary changes

No processes left running; the Engineer and QA each started and stopped the frontend dev server. `make clean-scratch` was NOT run: `.scratch/` still holds the F1 to F9 scripts and databases from the #11 advice run, which the human may want to re-run (they were not created for #59).

## Interruptions

none for #59.

## Unrelated problems noticed but not fixed

- `strictPort` is set only by the Makefile's `--strictPort` flag, so a hand-run `vite dev` can move to another port (QA note; follows the issue's design).

## Follow-ups for the next session

- Human: update the runbook's "Traps seen on #51". The human opened the forwarded port and the SOCBoard page loaded (2026-11-12); no agent ran a browser.
- Human: push from the clean clone.
- Human: say when `.scratch/` may be cleaned (`make clean-scratch`), after reading or keeping the #11 advice scripts.
- #59 was closed with `make issue-close` after the human confirmed the browser check.
