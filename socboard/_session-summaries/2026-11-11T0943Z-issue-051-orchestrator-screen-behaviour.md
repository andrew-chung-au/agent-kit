# Issue #51: Frontend behaviour: new-alert timer, reassign flag and component tests

**Date:** 2026-11-11T09:43Z (UTC)
**Spec version:** d913e19

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Ponytail trial arm: control (no `ponytail: on` line); Phase 1, shadow review after QA PASS.

- The mock adds one fixed Medium alert ("Unusual outbound DNS volume from build server") every 20 000 ms in mock mode only, through the same `ingest` path as the seeds; started once from a `useEffect` in `routes/__root.tsx`, never on import.
- `VITE_FEATURE_REASSIGN` (`true` / `false` / unset follows the mock) hides the Lead's Reassign control; declared in `vite-env.d.ts`, read in `config.ts`.
- Status buttons are no longer rendered (were rendered disabled) for a user who is neither owner nor Lead (criterion 6).
- Four new test files (21 tests: timer, root wiring, queue order, close dialog, 409, Lead-only hiding, flag, 401, error page through the router); `frontend/README.md` section on variables, service functions, tests and the limits of the bundle check.
- Worked with the #57 runbook recipe: Engineer in Kiro Web with CI as the feedback loop, QA in Kiro Web with CI as the runner (one-time exception), the human ran the build, the `dist` search, `make verify BASE=origin/main` and the browser checks in the dev container.
- Branch `issue-51-screen-behaviour`, PR #58, merge commit `ee4f6c6`; CI on main green (run 42997270910). Runbook traps PR #61 (`8e74bee`, merged `f6d83ab`).

**What I learned:** CI's `VERIFY: PASS` on a branch says nothing about weakened tests; only `make verify BASE=origin/main` does.

## Reflection

### Engineer

Engineer: reflection on issue #51 (commits aadb64a..c8f4282, 9 commits, written in Kiro Web with no way to run tests).

Reflection:
1. Slowed down: I had no feedback loop. Evidence: Kiro Web had no npm registry (403) and no usable `uv`, so I spent effort on a long "Prediction" section and on checking each text matcher against component source by hand, and I still needed a ninth commit (c8f4282) for a timer-test teardown order error.
2. Nearly went wrong: the guardrail and build checks could have failed unseen. `__root.tsx` importing `mockService` could have kept a demo credential in `frontend/dist`, and a setup edit might have been needed for Radix. Neither could be tested here; CI passing first time was partly luck.
3. Proposed change: `_docs/agent-kit/team/software-engineer.md`, under Verify: "If tests cannot run in this environment, list each unrun check and name the one most likely to fail." Effect: less prediction prose and the same risk list in a fixed place. Measure: count of engineer reports with unrun checks that include that list, and CI first-run failures against it, over the next five issues.

### QA

QA: reflection on issue #51, checked at `c8f4282` (verdict PASS, in `.scratch/qa-51.md`). Kiro Web, CI as the test runner under a one-time exception. 26 mutations in 4 CI runs: 21 caught, 5 survived (2.6, 4.2, 4.3a, 4.3b, 4.3c).

Reflection:
1. Slowed: no local runner (npm 403, `uv` could not write), so every result needed a CI round trip: 4 mutation runs plus reading 6 run logs. CI's "Weakened tests" line said "No test files changed" even in batch 4, where I had added skip and focus markers to four test files, so I wrote `.scratch/qa51-limits.sh` to check by hand.
2. Nearly wrong: CI's `VERIFY: PASS` looked like proof of no weakened tests, but `verify.yml` compares against the branch's own upstream. Mutations 4.3a-c (skips) passed CI. Also the mutation branches were pushed and had to be deleted, with the cleanup verified.
3. Change: `.github/workflows/verify.yml` (protected, human approval needed): pass `origin/main` as the weakened-test BASE. Expected: a branch with `.skip(` fails CI. Measured by re-pushing the 4.3c mutation: CI must fail instead of pass.

### PM

unknown (role not asked)

### Ponytail

The reviewer's report is on #51 (comment 6792371537); the reviewer writes no reflection block. Six findings; QA did not raise 1, 4 and 6.

## Launch usage

All launches in Kiro Web (author `Kiro Agent`, attribution `Assisted-by: Kiro`), model auto. The tool's completion notices give no active time or tool-use figures.

- Engineer, #51 round 1 (arm: control, tier: standard, 11 criteria): active time unknown, tool uses unknown. 9 commits, aadb64a..c8f4282. CI feedback rounds: 0 (CI run 42986999808 green on first push).
- QA, #51 first launch (fresh), CI as runner under the one-time exception: active time unknown, tool uses unknown. 4 mutation CI runs (42988246026, 42988245654, 42988245589, 42988246439). Verdict PASS at `c8f4282`.
- Reviewer (ponytail-review, shadow), #51: active time unknown, tool uses unknown. 6 findings; diff and criteria given as `.scratch/` files, not pasted (noted on the issue).
- PM, follow-ups #59, #60 and the #49 scope comment: active time unknown, tool uses unknown.
- PM, follow-up #62 (reviewer findings 1 and 4): active time unknown, tool uses unknown.
- PM, follow-up #63 (issue-close floor): active time unknown, tool uses unknown.
- Engineer, reflection relaunch: active time unknown, tool uses unknown.
- QA, reflection relaunch: active time unknown, tool uses unknown.
- Handover: one, Kiro Web to the dev container for the human's checks (build, `dist` search, `make verify BASE=origin/main`, browser). Engineer push 2026-11-11T08:26Z; human results reported about 09:05Z to 09:35Z, including time lost to the dev server bind problem. Wait time includes idle time; annotate or exclude it in the trial.

## Files created or modified

- `frontend/README.md`, `frontend/src/routes/__root.tsx`, `frontend/src/routes/cases.$id.tsx`, `frontend/src/services/config.ts`, `frontend/src/services/mockService.ts`, `frontend/src/vite-env.d.ts`
- New: `frontend/src/test/error-page-router.test.tsx`, `new-alert-timer.test.ts`, `root-timer-wiring.test.tsx`, `screen-behaviour.test.tsx`
- `_docs/runbooks/kiro-web-to-dev-container-handover.md` ("Traps seen on #51", PR #61)
- This summary.

## Decisions made by the human

- Work #51 in Kiro Web following the #57 runbook recipe ("ok lets do it").
- One-time QA exception for CI-run mutation branches on #51 ("ok qa").
- Follow-ups: file the dev server bind issue (#59) and the frontend dependency protection (#60); fold the CI weakened-test base gap into #49; skip the two small test gaps (401 on writes, single interval literal).
- Runbook traps update: yes (PR #61, merged).
- Sweep: after #51 closes.
- Shadow review: yes; follow-up for findings 1 and 4 (#62).
- Closing: `make issue-close N=51` refused because the Engineer's reflection comment (posted after QA PASS, naming commit hashes) moved the script's floor. The human chose to close #51 by hand on GitHub (option 1 of 3); the orchestrator posted the cause (comment 6792560921) and the PM filed #63.
- Accepted the Engineer's choice to hide, not disable, the status buttons for non-owner Analysts (verified in the browser).
- Finding 51-1: useful correctness-risk
- Finding 51-2: correct-minor scope
- Finding 51-3: correct-minor correctness-risk
- Finding 51-4: useful correctness-risk
- Finding 51-5: correct-minor scope
- Finding 51-6: useful correctness-risk

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify BASE=origin/main` (human, dev container, at c8f4282: 154 Vitest, 51 assertion lines added, 0 removed, `VERIFY: PASS`)
- **Frontend build:** `make frontend-build`, then a search of `frontend/dist` for the alert text (human: passed; no match)
- CI: runs 42986999808 (branch) and 42997270910 (main after merge), both green.

## Proposed AGENTS.md changes

none

## Temporary changes

- Four throwaway branches `qa-51-mut-1` to `qa-51-mut-4` (remote and local) and their worktrees: deleted; `git ls-remote --heads origin 'qa-51-*'` empty.
- The human's dev servers in the dev container (make-started and a foreground one bound to 127.0.0.1): stopped by the human.
- No system configuration changed. `make clean-scratch` ran after this summary was written.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `issue-close.sh` counts a post-PASS Engineer reflection that names a commit as new Engineer work (#63). Until fixed, ask roles to keep commit hashes out of reflection comments, or post reflections before the Close step expects them.

- `make install` cannot run in Kiro Web (`uv` cannot create its Python directory; npm registry 403); known, in the runbook.
- Long pastes into the Kiro Web chat were rejected by the chat backend (recorded in the runbook).

## Follow-ups for the next session

- Sweep is due (`make sweep-due`: 6 closed since 2026-11-10); run it now that #51 is closed.
- Confirm #51 is closed (by the human, by hand).
- Follow-up issues to groom: #59 (dev server IPv4 bind), #60 (protect frontend dependency files), #62 (future-dated timer alerts, order-dependent wiring test), #63 (issue-close floor); #49 has the added CI scope.
- Reflection proposals to bring to the human: Engineer (unrun-checks list in `software-engineer.md`), QA (`verify.yml` BASE `origin/main`, overlaps #49).
- Next issue in order after #51.
