# Issue #31: Make lint pass in frontend/ (formatting only)

**Date:** 2026-11-15T04:54Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`make frontend-lint` now exits 0 on `frontend/`. One commit, `1fb014e`, holds the output of `make frontend-format` for the 15 `.ts` and `.tsx` files ESLint reads (`components/soc`, `routes`, `services/mockService.ts`, seven test files); layout only. The three markdown files the format script also rewrites were restored. No rule, config, dependency or protected file changed. One warning remains (`react-refresh/only-export-components`, `src/components/ui/button.tsx` line 49), left as it was because moving the export is not layout.

Before the change, the issue had two regroom edits by the PM at the human's request: the stale baseline (114, then 531 measured on `main`), the make targets from #75, branch plus pull request instead of a commit to `main`, and the sandbox's ability to run lint; then the stale file counts and #8 and #51 wording. The human confirmed both (hashes `ef6451…3539`, then `13bafe9d03602ef349f125014aae68314ffbe979e8bbe6e520e5cbed89846452`).

Branch `issue-31-frontend-lint-format`, draft PR #232. Claim: https://github.com/andrew-chung-au/socboard/issues/31#issuecomment-6889276524. Baseline: https://github.com/andrew-chung-au/socboard/issues/31#issuecomment-6889280959 (531 `prettier/prettier` errors, 1 warning, 16 files, on `7b3c83c`). QA PASS at `1fb014e`, Lows only: https://github.com/andrew-chung-au/socboard/issues/31#issuecomment-6889339262 (AST comparison 0 differences over 15 files, with six mutants caught; build comparison explained; file list clean). Engineer verify comment with the per-file reasons: https://github.com/andrew-chung-au/socboard/issues/31#issuecomment-6889415830. CI on `1fb014e`, all success: `socboard verify` pull_request run 43677928018 (`VERIFY: PASS WITH WARNINGS`, 2389 Python and 237 frontend tests), postgres run 43677927995, image run 43677927977, compose run 43677927934.

**What I learned:** the build comparison cannot be a plain hash comparison: content-hashed file names change in a cascade, so the files are compared after masking the hashes. The one real difference is a JSX `{" "}` that prettier introduced, with the same rendered text.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** the first hash comparison of `frontend/dist` showed 8 changed chunks plus `index.html`, because the output names carry content hashes; masking them took one `.scratch/` script.
**What nearly went wrong or was blocked:** the first run of my dist compare read an empty "before" directory because two tool calls ran in parallel; I caught it from the "files before 0" line.
**One proposed change (file, expected effect, measure):** in the body template for formatting-only issues, say the build comparison masks content hashes in file names (it would save the first false alarm; measured by whether the Engineer needs a second script).

## Launch usage

PM: 2 regroom launches. QA: 1 launch (PASS). Active time and tool uses: unknown.

## Files created or modified

- `frontend/src/components/soc/AppShell.tsx`, `CaseTable.tsx`, `badges.tsx`
- `frontend/src/routes/cases.$id.tsx`, `closed.tsx`, `index.tsx`, `login.tsx`
- `frontend/src/services/mockService.ts`
- `frontend/src/test/contract-paths.test.ts`, `error-page-router.test.tsx`, `guardrails.test.ts`, `http-service.test.ts`, `mock-service.test.ts`, `real-client.test.tsx`, `screen-behaviour.test.tsx`
- `_docs/records/findings/31.json`
- `_session-summaries/2026-11-15T0454Z-issue-31-orchestrator-frontend-lint-format.md` (this file)

## Decisions made by the human

- Said "go #31" after the two regrooms; confirmed the 531 baseline and the stale-text fixes.
- The `approved` label was left as it was.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Lint:** `make frontend-lint` (exit 0, one warning).
- **Format stability:** `make frontend-format`, then restore the three markdown files it rewrites; no `.ts` or `.tsx` change.
- **Frontend test:** `make frontend-test`.
- **Verify:** `make verify` (CI run 43677928018). It does not run lint; `LINT_CMD` is empty until #93.

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-31-1: Prettier split the queue's refresh-failed banner text into two adjacent text nodes with the same visible text, and no test pins that DOM shape.
- F-31-2: make frontend-format rewrites three markdown files that ESLint does not read on every run, so each run needs a git restore of them before a commit.
- F-31-3: The react-refresh/only-export-components warning for buttonVariants in src/components/ui/button.tsx is left in place, since moving the export is not a layout change.

## Follow-ups for the next session

- The human's browser check of the login screen and queue in mock mode (criterion 6) before merging.
- #93 (lint in `make verify`) depends on #31 and is waiting for the human's label.
- The title of #31 still says `bun run lint`.
