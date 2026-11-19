# Issue #62: Fix future-dated timer alerts and order-dependent root-timer-wiring test

**Date:** 2026-11-12T06:56Z (UTC)
**Spec version:** e68c39e

## What changed and why

Tier: Standard (from the PM proposal; no tier label). A supporting issue (before #21), run while #11 waits for outside answers. Ponytail trial: not a control issue. Epoch: no move.

- `frontend/src/services/mockService.ts`: the new-alert timer's alert has `age: 1` (the human's ruling), so it is no longer dated in the future; `ingest` is unchanged.
- `frontend/src/test/new-alert-timer.test.ts`: two tests: nothing the timer adds is dated after the fake current time, and a claim right after the new alert is dated at or after its `ingested` entry.
- `frontend/src/test/root-timer-wiring.test.tsx`: each test loads the routes with fresh modules, so no test depends on another; a third test runs the mock-on scenario then the mock-off one.
- CI was the test loop: runs 43168798022 (push) and 43168810673 (pull request) on `1ce5cda`, VERIFY: PASS, frontend tests 154 to 157, weakened-test check against `main`: 12 assertions added, 0 removed. The refused case was proved on CI on a throwaway branch (run 43169297079: three tests failed with the guard removed); the branch was deleted.
- The human ran the wiring test under five shuffled seeds in the dev container: all passed, the order varied. That met the shuffled-order criterion without touching the protected `frontend/package.json` or the Vitest config.
- Draft PR #90 (draft so CI's weakened-test check compares with `main` from the first push). QA PASS commit `1ce5cda`.

**What I learned:** a draft PR opened at the first push gives the weakened-test check against `main` for free, closing the trap seen on #51 and #74 until #65 lands.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6816930239, unchanged:

Reflection:
1. Slowed down: Vitest cannot run in this sandbox, so each test check needed a CI round trip; the refusal check took two throwaway branch runs (the first passed because a second guard hid the failure), and the shuffled-order criterion waited on a human run.
2. Nearly went wrong or blocked: the shuffled-seed criterion could only be met by editing protected or out-of-list files (package.json, vitest config, workflow), so I stopped and left it open until the human ran seeds 1 to 5 by hand; I also did not run the new future-date tests without the fix.
3. Proposed change: `_docs/agent-kit/procedures/verify.md`, add a rule that a criterion needing a runner option the sandbox cannot run gets a human-task file at the start; expected effect is no waiting at the end; measure by counting criteria left "not done" at hand-over, per issue, before and after.

### QA

From comment 6816972197, unchanged:

Reflection:
1. The slowest part was reading the log of the failing CI run by hand; the Engineer's `.scratch/ci-log-62.py` was hard-wired to one branch, so I wrote a new script that takes run ids (evidence: `.scratch/qa-62-ci.py`, one run, four runs read).
2. Nothing was blocked; the near-miss was accepting "fails on the old value" without proof, since nobody could run Vitest, so I reasoned it through from the code and labelled it as reasoning.
3. Proposed change: `_docs/agent-kit/team/qa-engineer.md`, add a line that when tests cannot run in the sandbox, QA asks the orchestrator for one throwaway CI run of the reverted fix; expected effect is a proven, not reasoned, answer on whether new tests catch the bug; measured by counting QA comments that say "reasoned, not proven" per issue.

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). Engineer 2. QA 1 (PASS). Handovers: one human run (five shuffled seeds).

## Files created or modified

The three frontend files above. This file.

## Decisions made by the human

- The shuffled-order criterion met by the human's five-seed run (option 2), not by a config change.
- Alongside: #71 and #73 approved as recommended; epoch-batch item 8 narrowed to roadmaps, epoch-batch notes and runbooks; Deploy uses Terraform.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI runs 43168798022 and 43168810673: VERIFY: PASS).

## Proposed AGENTS.md changes

none.

## Temporary changes

- A throwaway branch was pushed for the refused case and deleted, locally and on GitHub.
- `make clean-scratch`: NOT run; housekeeping is on hold.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The new alert now reads "1 min ago" in the UI rather than "just now" (QA's note; a consequence of the human's ruling).
- The two future-date tests were reasoned, not shown, to fail on the old value (no revert run).

## Follow-ups for the next session

- #59 (dev server reachable from the browser) is next among supporting issues; it needs the human's browser check.
- #11 still waits for the outside answers.
- Sweep 4 evidence: the Engineer's and QA's proposals (a human-task file at the start for unrunnable checks; one throwaway CI run of a reverted fix).
