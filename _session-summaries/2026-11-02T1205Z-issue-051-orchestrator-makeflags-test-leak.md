# Issue #51: Tests inherit MAKEFLAGS from the push check's make and fail the unreachable-base test

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-02T12:05Z (UTC)
**Spec version:** none

## What changed and why

The human's first `git push` of about 68 commits from the clean clone was blocked by the push check: `make test` failed one of 371 tests in the throwaway container, `tests/test_gate_push_check.py` `ContainerScriptTest.test_an_unreachable_base_is_dropped_not_fatal` (expected `base-is-[]`, got `base-is-[fac22711…]`, the push check's own base). The suite passes in the sandbox (no Docker, and `make verify` runs there without a `BASE`).

Cause (confirmed by the Engineer and by QA on copies, not on the real container): the push check runs `make -C . verify BASE=<sha>`; GNU make passes command-line variables to child makes through the `MAKEFLAGS` environment variable; the test suite runs under that make, so the test's inner `make` inherits the outer `BASE` as a command-line variable, which overrides the container script's dropped `BASE`. In the sandbox nothing leaks.

Fix, commit f39478b (tests only, unprotected, committed by the Engineer; option 1 of the PM's three, assumed from the orchestrator's recommendation after the human labelled the issue; recorded in an `Orchestrator:` comment): `build_env` in `tests/kit_repo.py` and the `env()` helpers in `tests/test_sweep.py` and `tests/test_issue_hash.py` now drop `MAKEFLAGS`, `MFLAGS` and `MAKELEVEL`; one new test in `tests/test_gate_push_check.py`. `make verify` passed (372 tests). QA PASS at f39478b: reproduced the failure on a pre-fix copy with `MAKEFLAGS`, `MFLAGS` and `MAKELEVEL` set in the parent environment; the full suite passes under that stand-in; mutations of `build_env` are caught.

Not verified by automation: the real container run. The human re-runs `git push` from the clean clone as the real check; no Docker here. Not guarded by any test: the scrubs in `test_sweep.py` and `test_issue_hash.py` (QA: reverting them still passes; they are correct by inspection).

**What I learned:** a test suite that runs under the push check's `make` inherits make's state through `MAKEFLAGS`; tests that spawn `make` must clean the environment, and a mismatch between the sandbox and the container shows only at push time.

## Reflection

### Engineer

1. Slowed down: my first diagnosis run failed with "Start directory is not importable" because I guessed `unittest discover -s tests -t .`; the Makefile uses `discover tests`. No documented single-file test command exists (`Test (one file): none`), so I read the Makefile to find the form.
2. Nearly went wrong: the mutation run's failure output printed the whole environment, including a messaging token, because `assertNotIn(name, env)` dumps the dict. I switched to `assertFalse(name in env, ...)` before committing.
3. Proposal: add a `make test-one FILE=tests/test_x.py` target and fill the `Test (one file)` slot in `AGENTS.md`. Effect: no guessing the unittest form. Measure: count first-try failed test invocations per engineer session in the session summaries (here: 1 before, target 0).

### QA

1. Slowed down: the test copies resolve `REPO` from their own file path, so my first copies would have lacked `agent-kit/`; I had to copy the whole tree (about 8 mutation copies, each taking 4-12 s) in `.scratch/qa51-run.py`.
2. Nearly went wrong: a reverted scrub in `test_sweep.py` or `test_issue_hash.py` passes all tests, so a mutation run alone could have read as "covered"; I reported it as unguarded instead.
3. Proposal: add a one-line note to `agent-kit/team/qa-engineer.md` that mutation checks copy the whole repo minus `.git` and `.scratch`, with a helper `.scratch/` script pattern. Expected effect: fewer false starts. Measure: QA sessions needing a re-copy, counted in session summaries.

### PM

1. Slowed down: I wrote the body before the decision options, so its option numbers did not match the comment; fixing it cost an edit and a second hash (fa95c2c8... became 1aaebbe8...).
2. Nearly went wrong: the first draft of this PM comment carried the stale hash; I caught it only because I re-ran `make issue-hash N=51` after the edit.
3. Proposal: in `agent-kit/team/pm.md`, add "draft the decision question before the body, and record the hash only after the body is final". Expected effect: one hash per issue. Measure by counting PM re-hashes in issue comments over the next five groomed issues (target: zero).

## Launch usage

- PM (diagnose and file #51): 95.2 s, 27 tool uses
- Engineer (implement #51): 138.4 s, 31 tool uses
- QA (check #51 at f39478b): 186.1 s, 20 tool uses
- Engineer (reflection, resumed): 21.0 s, 3 tool uses
- QA (reflection, resumed): 220.6 s, 23 tool uses (as reported; may include the earlier run)
- PM (reflection, resumed): 18.7 s, 3 tool uses
- Also this session, not tied to an issue: the stopped #50 Engineer ran for seconds and produced nothing.

## Files created or modified

- `tests/kit_repo.py`, `tests/test_gate_push_check.py`, `tests/test_sweep.py`, `tests/test_issue_hash.py`
- This summary and the handover summary.

## Decisions made by the human

- Labelled #51 `approved` after seeing the options and the orchestrator's recommendation of option 1; option 1 is assumed, not named.
- Ran the push and reported the push check's failure output.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none (the Engineer proposes filling the `Test (one file)` slot with a `make test-one` target, which needs its own issue)

## Temporary changes

none

## Interruptions

The human asked to hand over for Kiro while the #50 Engineer was running; the orchestrator stopped it within seconds (nothing left behind). Then the push check failure interrupted the order: #51 was filed and fixed before #50 started.

## Unrelated problems noticed but not fixed

- **Possible secret exposure:** the Engineer reports that a failing `assertNotIn(name, env)` in a mutation run printed the whole environment, including a messaging token, into its tool output. That output is in the sandbox session transcript only (not committed), but the human may want to rotate that token. The committed test uses `assertFalse(name in env, ...)`, which prints only the variable name.
- A redundant `mock.patch.dict(os.environ, ...)` in the new test has no effect (harmless).
- Reverting the scrubs in `test_sweep.py` and `test_issue_hash.py` is not caught by any test.
- No documented command for running a single test file (`Test (one file): none` in `AGENTS.md`).

## Follow-ups for the next session

- The human re-runs `git push` from the clean clone as the real check of this fix.
- #50 (approved, hash recorded): relaunch the Engineer fresh. #13, #44, #49, #20, #36, #2, #37 as in the handover.
