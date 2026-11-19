# Issue #175: Keep make run and make backend-run out of deployed mode

**Date:** 2026-11-14T14:24Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

A development run no longer starts the backend in deployed mode. `make run` refuses `SOCBOARD_MODE=deployed` in its preflight (exit 2, before `make migrate` and `make seed` write anything), and `make backend-run` removes the variable from the backend's environment and prints one line saying it was ignored. `python -m socboard.server` run directly still honours deployed mode.

- `scripts/run_preflight.py`: one more problem entry for `SOCBOARD_MODE`, decided by `settings.is_deployed` (exact match) and named by `settings.MODE_VAR`; the value is never printed.
- `tests/test_make_run.py`: the refusal, the values that leave deployed mode off (unset, empty, `Deployed`, `DEPLOYED`, trailing and leading space, `development`), `make run` end to end for the database-URL-unset case, the repeated-character ingest key case and an otherwise valid environment, and `make backend-run` starting with the variable set and no database URL.
- `README.md`: one sentence on the `SOCBOARD_MODE` row.
- Protected, committed with `HUMAN_APPROVED=1` after the human approved the exact diff: `Makefile` (the `backend-run` server line and one message line) and `AGENTS.md` (the `Run` and `Run (full stack)` lines).

Worked by the Hardening session, Standard tier (from the PM proposal), no Engineer launch. Branch `issue-175-keep-run-out-of-deployed`, PR #196, commits `409078d` (preflight, tests, README) and `7d2c593` (Makefile, AGENTS.md, backend-run test). Claim: https://github.com/andrew-chung-au/socboard/issues/175#issuecomment-6877994405. QA PASS at `7d2c593`: https://github.com/andrew-chung-au/socboard/issues/175#issuecomment-6878742569.

**What I learned:** a test that needs the protected `Makefile` change cannot go into the first commit without a red CI run, so the `backend-run` test went in with the approved protected commit.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

QA: 1 launch (pass at `7d2c593`). Active time and tool uses were not given: unknown.

## Files created or modified

- `scripts/run_preflight.py`, `tests/test_make_run.py`, `README.md`
- `Makefile`, `AGENTS.md` (protected, approved)
- `_session-summaries/2026-11-14T1424Z-issue-175-orchestrator-deployed-mode.md` (this file)

## Decisions made by the human

- Options A (the preflight refuses deployed mode) and C (`make backend-run` clears the variable and prints one line); labelled `approved`.
- Approved the exact `Makefile` and `AGENTS.md` diffs.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43603786905 and 43603791700 on `7d2c593`; the postgres job 43603791719 also passed). Locally only the Python suite ran (2043 passed); the frontend tests did not, because bun and its packages are not installed in this sandbox.
- **Test (one file):** `make test-one FILE=tests/test_make_run.py` (103 passed).

## Proposed AGENTS.md changes

none (the approved ones are committed).

## Temporary changes

- Python environment in `.scratch/venv` and `.scratch/uv-cache` (94 MB, approved), linked as `.venv` (untracked symlink, so `make assert-clean` reports it). Still in place for the next issues; to be deleted when the Hardening work ends.
- Nothing is running (`make backend-stop` reports not running).

## Interruptions

none

## Unrelated problems noticed but not fixed

- `ruff check scripts tests` reports 119 findings on main; no ruff step is configured in `make verify`, so I did not touch them.
- The "ignored" line also prints for harmless values such as an empty value or `development`, which matches "when the variable was set".

## Follow-ups for the next session

- After the human merges PR #196: confirm the merge commit is on `origin/main`, then post the Close comment for #175 and run `make issue-close N=175`.
