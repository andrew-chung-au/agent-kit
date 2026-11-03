# Issue #53: verify gate gaps (type check, BASE)

**Date:** 2026-10-22
**Spec version:** 97893c1

Worked on branch `claude/start-53-7oaxg3` as roadmap track T1 (parallel tooling track), after the PM grooming (6331077862, corrected by 6331105969) and the human's decisions D1 and D2 (6331160446).

## What changed and why

- `make verify` now runs the frontend type check: `agent-kit.conf` sets `TYPECHECK_CMD="make frontend-typecheck"` (`e0cf368`), and `AGENTS.md` line 35 and `_docs/testing.md` line 20 list it. Before, vitest and `vite build` did not type-check, so a type error passed the gate.
- The weakened-test check can no longer silently compare nothing (`bdda483`, `3d978fe`): `verify.sh` fails with `FAIL: BASE '<value>' does not resolve to a commit or tree` when BASE is unresolvable (checked with `^{tree}`, so the pre-push empty-tree base still works), and warns when BASE is the same commit as HEAD. `verify.md` tells runners to pass `BASE=<commit before the issue's first commit>`, record it in the hand-over comment and report "base used".
- `3d978fe` (one line) silences a stray `error:` line the empty-tree base printed; QA found it, the human chose to fix it.

## Files created or modified

- Protected, each committed alone with `HUMAN_APPROVED=1`: `_docs/agent-kit/scripts/verify.sh` and `_docs/agent-kit/procedures/verify.md` (`bdda483`); `agent-kit.conf` (`e0cf368`); `AGENTS.md` (`1d869a5`); `_docs/agent-kit/scripts/verify.sh` (`3d978fe`).
- Unprotected: `_docs/testing.md` (`291b4bc`), `_docs/roadmap.md` (check-in), `_docs/ai-usage-log.md`, this summary.
- Not edited, as the grooming required: `githooks/pre-push`, `team/*.md`, `Makefile`, `.github/`, the root `agent-kit/` copy.
- GitHub comments on #53: Engineer 6331467458; QA 6331468388; approval records 6331468586 (`bdda483`), 6331468781 (`e0cf368`), 6331469012 (`1d869a5`), 6331469216 (`3d978fe`).

## Decisions made by the human

- D1 (#53): both a) the script warning/failure and b) the procedure change; D2: file the CI follow-up (#67). Both as recommended, before this session.
- Approved all three protected diffs as the Engineer drafted them.
- At the decision point: fix the stray stderr line now (a fourth protected commit); no action on the other QA notes (already tracked).

## Mismatches with the spec or design docs

- none. The issue names `githooks/pre-push`; the hook lives at `.githooks/pre-push` and `_docs/agent-kit/githooks/pre-push`. Both are untouched.

## Commands to validate

- **Verify:** `make verify BASE=6ed87ed` PASS (62 tests, `PASS: Type check`). A plain `make verify` now warns in this branch, as designed.
- Cases, all re-run by QA: `BASE=HEAD` warns, `BASE=nosuchref` fails, `BASE=72903cc^` lists the changed test file, `BASE=3d38e34` is clean, the empty-tree base passes with no stray error, a deliberate type error gives `FAIL: Type check` while `Tests` still passes (reverted).
- `make assert-clean` PASS at `3d978fe` after QA.
- Not verified: the sandbox push check was read, not run (no Docker). By reading it runs `make install verify`, and #32's image has Node.

## Proposed AGENTS.md changes

- none beyond the approved line 35 change (`1d869a5`).

## Temporary changes

- `.scratch/` scripts and comment files; `make clean-scratch` run at the end of the session.
- The Engineer and QA made a deliberate type error in `frontend/src/lib/utils.ts`, uncommitted, and reverted it; `git status --short` was empty afterwards.
- No processes started; no system configuration changed.

## Permission review

The Engineer's comment lists the protected-file commits as merits requests. QA lists none. Neither can see whether the tool prompted for an `ask`-rule command.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `HUMAN_APPROVED=1 git commit` of `bdda483`, `e0cf368`, `1d869a5`, `3d978fe` (protected files, merits request); `git push -u origin claude/start-53-7oaxg3` (cloud-session exception, twice); `make issue-comment` on #53 (allowed target, six comments); `make issue-close N=53` (ask rule `Bash(make issue-close*)`)
- Risky (propose denying): none

## Interruptions

- The stop hook asked for a push twice while QA was running; the branch was pushed after the protected commits and again after the stderr fix. Nothing was lost.

## Unrelated problems noticed but not fixed

- `make verify BASE=nosuchref` exits 2 seen from `make` (the script exits 1). The pre-push hook only tests non-zero.
- The push-check script's default image is `python:3.12`, which has no Node; it relies on `AGENT_PUSH_CHECK_IMAGE` (#32, already an AGENTS.md gotcha).
- The stale root copy `agent-kit/scripts/verify.sh` lacks the fix (#38). CI (`verify.yml`) still has the BASE gap (#67).
- Build and QA both ran as claude-sonnet-5-5 in Claude Code; QA ran in a fresh subagent context and no different model was available.

## Follow-ups for the next session

- #67 (CI passes a real BASE) stays Later.
- Cloud sessions: run `make verify BASE=<commit before the issue's first commit>`, per the updated procedure.
- T1 is done, so step 15 and #24 are no longer blocked on `agent-kit.conf`; next is step 11.
- Merge note: this branch and the other tooling branch both append to `_docs/ai-usage-log.md` and `_docs/roadmap.md`; keep both on conflict.
