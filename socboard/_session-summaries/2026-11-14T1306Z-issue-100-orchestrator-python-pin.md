# Issue #100: Pin CI's Python version to the project's 3.12

**Date:** 2026-11-14T13:06Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

CI had been running on whatever Python the runner offered (3.14.4 on `main`, run 43577502611) while the project targets 3.12. Now `.python-version` holds `3.12`, so uv picks 3.12 in CI and on a fresh checkout, and a CI step fails when the running major.minor differs from the file.

- `.python-version` (new, exactly `3.12`), `scripts/check_python_version.py` (reads the file, so "3.12" is written once), `tests/test_check_python_version.py` (10 tests: a mismatch names both versions; a missing, empty, blank-line, two-line, `3.12.3`, `3` or `python3.12` file is refused).
- `.github/workflows/verify.yml` (protected): one added `Check Python version` step after `make install`; committed as `bba789d` with `HUMAN_APPROVED=1` after the human approved the exact diff.
- `pyproject.toml`, `uv.lock` and the `Makefile` are unchanged.

Worked by Session A/B (Kiro Web) as Engineer, QA and orchestrator launches; closed out by the Hardening session. Standard tier. Branch `issue-100-python-pin`, PR #173, merge commit `7388d86`, head `bba789d`. Engineer: https://github.com/andrew-chung-au/socboard/issues/100#issuecomment-6875014474. QA PASS at `bba789d`: https://github.com/andrew-chung-au/socboard/issues/100#issuecomment-6875029879. Reviewer report: https://github.com/andrew-chung-au/socboard/issues/100#issuecomment-6875049803.

**What I learned:** the one test that compares the repository file with the running interpreter (`test_repository_file_matches_this_interpreter`) makes `make test` fail on any non-3.12 local Python although `pyproject.toml` allows `>=3.12`; the Reviewer proposed deleting it.

## Reflection

### Engineer

Taken unchanged from its comment (https://github.com/andrew-chung-au/socboard/issues/100#issuecomment-6875014474):

- Slowed: no 3.12 interpreter in the sandbox, so only CI could show the pin working.
- Nearly went wrong: committing `verify.yml` with the unprotected files; staging by explicit path and checking `git diff --cached --name-only` kept it out.
- Proposed change: none.

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked). Closed out by the Hardening session.

## Launch usage

Engineer: 1 launch. QA: 1 launch. Reviewer: 1 launch. Active time and tool uses were not recorded on the issue: unknown.

## Files created or modified

- `.python-version`, `scripts/check_python_version.py`, `tests/test_check_python_version.py` (new)
- `.github/workflows/verify.yml` (protected, one step)
- `_session-summaries/2026-11-14T1306Z-issue-100-orchestrator-python-pin.md` (this file, written at close-out)

## Decisions made by the human

- Approved the exact `verify.yml` diff (Session A, 2026-11-14).
- Merged PR #173. The issue thread records no decision on the three Reviewer findings; none was applied before the merge.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI runs 43578997610 pull_request and 43578993849 push on `bba789d`: `Using CPython 3.12.16`, 1847 Python tests, 208 frontend tests, `VERIFY: PASS`).

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- Reviewer finding 1 (should fix): the repository-file test fails a local run on a non-3.12 interpreter.
- Reviewer finding 2: `.devcontainer/devcontainer.json` names `python:3.12` a second time, so a later bump of `.python-version` leaves the dev container behind silently; the file is protected.

## Follow-ups for the next session

- Decide whether to delete the one repository-file test and whether to tie the dev container image tag to `.python-version`.
