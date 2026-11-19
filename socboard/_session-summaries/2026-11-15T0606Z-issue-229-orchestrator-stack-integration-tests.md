# Issue #229: Integration tests against the Compose stack: the journeys over HTTP through the proxy, the forwarded-address rule, and the schema check inside the built image (D12)

**Date:** 2026-11-15T06:06Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`make test-stack` runs the journeys, the refusals and the hostile-text test over HTTP against a running Compose stack, and four live checks that only the real proxy, image and database can show. `make test` still runs the same journeys in process on SQLite. This is D12 of the Deploy phase.

- `tests/test_journeys.py` takes its client from one fixture: in process as before, or an HTTP client to the stack address in `tests/stack_support.py` (plain `http` on the loopback only, because the tests ingest alerts and claim cases). Two assertions that assumed an empty database (journey 1's queue, journey 2's closed list) look only at the cases the test made in live mode; the exact ones stay in process. The ingest helper waits once for `Retry-After`.
- `tests/test_stack.py`: the address rule, the schema-file loader and its refusals, the marker, a syntax-tree test that the journeys use the database helpers only inside the two fixtures, and four `stack_only` live tests: six failed logins with forged `X-Forwarded-For` values are limited on the sixth through the proxy and on the app's own port, a valid ingest key is limited with a different forged address each time and the refused alerts store nothing, and the operations of the built image's own schema equal those of `openapi.yaml`.
- `tests/conftest.py` gained the `stack_only` marker: deselected and counted in the run header without a stack, never skipped.
- Protected, applied by the human: the `make test-stack` target, its `AGENTS.md` line, three steps in `.github/workflows/compose.yml`, and `tests/test_stack_make.py` (the target refuses without an address).

Worked by the Compose lane session, Standard tier, no separate Engineer launch. Branch `issue-229-stack-integration-tests`, PR #231, merge commit `5bf6f5f`, head before merge `e4c3e5c`. The protected changes went to `main` as one commit by the human, `e4b6e5a`, after the PR merged. Claim: https://github.com/andrew-chung-au/socboard/issues/229#issuecomment-6888948556. QA PASS at `e4c3e5c`: https://github.com/andrew-chung-au/socboard/issues/229#issuecomment-6889283410. CI on `e4b6e5a`: the compose run 43683332541 ran the new steps and `66 passed` with `stack_only: 4 marked, 0 deselected (live stack)`, so the forged-header tests held through the real Caddy.

**What I learned:** a deliverable that a protected file has to complete is not finished at merge. PR #231 merged without the Makefile, workflow and make test, and the live tests ran nowhere until the human applied them 25 minutes later. I should have said "not done until applied" in the decision-point message, not only in the task file.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (I groomed in this session). QA: 2 launches (FAIL at `9d32ce1` with two Mediums, PASS at `e4c3e5c` on the changed lines only). Active time and tool uses were not given: unknown.

## Files created or modified

- `tests/stack_support.py`, `tests/test_stack.py` (new); `tests/test_journeys.py`, `tests/conftest.py` (edited)
- `README.md` (a "Tests against the stack" section)
- `Makefile`, `AGENTS.md`, `.github/workflows/compose.yml`, `tests/test_stack_make.py` (protected, applied by the human in `e4b6e5a`)
- `_human-tasks/2026-11-15T0412Z-human-task-229-engineer-apply-stack-test-changes-and-run-them.md`
- `_docs/records/findings/229.json`, `_session-summaries/2026-11-15T0606Z-issue-229-orchestrator-stack-integration-tests.md` (this file)

## Decisions made by the human

- Labelled #229 `approved`, which accepted the recommendation: one fixture with two modes and two relaxed live-only assertions.
- Merged PR #231, then applied the protected changes to `main` in one commit. The first attempt of that commit was blocked by the push check (`make verify`): moving `test_stack_make.py` out of the proposals folder read as a deleted test file. The human amended the commit to leave the proposal copy in place.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify`. CI run 43683332554 (verify) and 43683332541 (compose) on `e4b6e5a` passed. Locally the whole Python suite passed before the fix round (2383 passed, 90 deselected).
- **Test (live stack):** `make test-stack` with the stack address, the ingest key and the seed passwords in the environment (needs Docker; never run in the agent's sandbox). The agent also ran the live-mode tests against a local server on SQLite: 66 passed.
- **Test (one file):** `make test-one FILE=tests/test_stack.py`, `make test-one FILE=tests/test_stack_make.py`.

## Proposed AGENTS.md changes

none (the approved Commands line is committed).

## Temporary changes

- Python environment in `.venv` (kept from #221). A throwaway worktree under `.scratch/` was removed. The local live-check server was stopped after each run.
- Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-229-1: the test that keeps the journeys off the database misses async tests, other database names and attribute access after a bare import.
- F-229-2: the README's rerun arithmetic assumes one gateway address for both paths.
- F-229-3: a second live run within five minutes breaks the app-port login test.
- F-229-4: a proposed test file under the human-task folder cannot be removed past the weakened-test check.
- F-229-5: the stack's start prints a pull-access-denied error for the local image three times before the build.

## Follow-ups for the next session

- `_human-tasks/229-proposed/test_stack_make.py` is a leftover copy of `tests/test_stack_make.py`. Removing it needs the human's approval, because the weakened-test check reads it as a deleted test file (F-229-4).
- D13 (end-to-end browser test) needs a dependency approval for the browser tool; D14 (CI pipeline and image push) follows it.
- Still unverified: the bind mount with a `lost+found` folder (D17c) and a browser sign-in on the proxy port (the D11 human task, step 3).
