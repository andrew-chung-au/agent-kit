# Issue #74: Backend skeleton with one passing test

**Date:** 2026-10-23
**Spec version:** 9b04f90

## What changed and why

Task 1 of S1: a runnable backend skeleton (`backend/` uv project, `app = FastAPI()`, no routes, tables or logic) plus the shared test harness later tasks reuse: the network guard (`U-NET`, `I-NET`), the `LLM_MODE`/`RESPONDER_MODE` stub validator, in-memory SQLite fixtures and `tests/fixtures/MANIFEST.md`. `make install` and `make test` now cover both frontend and backend, so `make verify` runs both suites. The CI workflow installs uv 0.13.1 (D1 option A) so `make install` keeps working there.

## Files created or modified

- `backend/pyproject.toml`, `backend/uv.lock`, `backend/vulntriage/__init__.py`, `backend/vulntriage/main.py` (`e673df2`)
- `tests/conftest.py`, `tests/network_guard.py`, `tests/test_smoke.py`, `tests/test_network_guard.py`, `tests/fixtures/MANIFEST.md` (`e673df2`)
- `.github/workflows/verify.yml` (`961f322`)
- `Makefile` (`f2afe1e`, protected; approval record 6355572492)
- `AGENTS.md` Commands lines (`4952e6b`, protected; approval record 6356140221)
- `_docs/ai-usage-log.md` (`469da6a`, plus the orchestrator entry in the close-out commit)
- `_docs/roadmap.md` check-in

## Decisions made by the human

- D1: install uv in the existing CI workflow in this issue (option A, recommended).
- The dependency batch `fastapi`, `uvicorn`, `sqlalchemy`, `pytest` (dev) and the `uv lock`/`make install` downloads.
- The exact Makefile diff, committed with `HUMAN_APPROVED=1`.
- The exact `AGENTS.md` Commands diff, committed with `HUMAN_APPROVED=1`.
- The npm-vulnerability follow-up: filing #111 (Not in S1).

## Mismatches with the spec or design docs

- `_docs/testing.md` § Test levels still says `make test` "today ... runs the frontend suite". The PM placed the wording fix in task 13 (#87); no edit in #74.
- The Engineer's usage-log entry says the Makefile and CI were left uncommitted; true at hand-over, since committed (`961f322`, `f2afe1e`). The orchestrator entry records the final state.

## Commands to validate

- **Verify:** `make verify BASE=8910c8a` (QA: PASS WITH WARNINGS; 62 frontend + 3 backend tests; the only warning is "test fixtures changed" for the new `tests/conftest.py` and `tests/fixtures/MANIFEST.md`, additions with 0 assertion lines removed)
- **Test (all):** `make test`
- **Test (backend):** `make backend-test`
- **Install:** `make install`

## Proposed AGENTS.md changes

Applied at the decision point and committed as `4952e6b` (Install, Test (all), new Test (backend), Verify lines). None outstanding.

## Temporary changes

- Engineer's red run: the `install_network_guard()` call was removed temporarily and restored; not committed.
- Engineer's `chmod -x`/`chmod +x` on `backend/.venv/bin/pytest` to check the missing-venv message; restored.
- `backend/.venv` and `frontend/node_modules` installs are git-ignored and kept, as they are the working environment.
- `.scratch/` files are removed by `make clean-scratch` at the end.

## Permission review

- Read-only (propose allowing): none recorded beyond `make issue-dump N=74` (QA, network read of the issue record; ask rule).
- Writes to the record (keep asking):
  - `make install` and `make backend-install` (QA; network package downloads, merits request).
  - `uv lock` and `make install` (Engineer; network package downloads for the approved batch, merits request).
  - `.scratch/qa74_guard_checks.py` (QA; a deliberate non-loopback attempt for the red run, merits request).
  - `make issue-comment N=74 ...` (PM, Engineer, QA, orchestrator; posts to the tracker).
  - `gh issue create` for #111 (PM; merits request).
  - `HUMAN_APPROVED=1 git commit` for `Makefile` and `AGENTS.md` (orchestrator; protected files).
  - `git commit` of `.github/workflows/verify.yml` (Engineer; the kit pre-commit hook required `HUMAN_APPROVED=1`, returned to the orchestrator).
  - `make issue-close N=74` (orchestrator; ask rule).
- Risky (propose denying): none. The Engineer's `chmod` toggle on a file created in this task was reversible and restored.

The PM comment states none for the PM's own reading commands. The PM's #111 filing command is the orchestrator's account of the PM Task; the PM's own comment on #111 was not re-read here.

## Interruptions

The previous orchestrator session stopped for usage limits after posting the AGENTS.md approval record and filing #111. This session resumed from the pasted transcript, re-read the issue comments (PM, Engineer, QA, both approval records) and the tracker, and found the tree clean at `4952e6b`.

## Unrelated problems noticed but not fixed

- `npm ci` reports one high-severity vulnerability in the unchanged frontend tree; filed as #111 (Not in S1).
- QA's one early `make frontend-test` overlapped with `make install` and failed on missing `node_modules`; a QA ordering artifact, not a code failure.
- The CI workflow was checked by inspection only; the first real CI run happens after the human pushes.

## Follow-ups for the next session

- #111: upgrade Vite past the advisory (not in S1).
- `_docs/testing.md` § Test levels wording: task 13 (#87).
- Next in S1 per the roadmap: #26 (task 3), then #76.
