# Issue #10: Backend skeleton: FastAPI app, health endpoint and error shape

**Date:** 2026-11-12T02:41Z (UTC)
**Spec version:** d913e19

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Ponytail trial arm: control (no treatment marker; the human ruled #9 counts as control, and #10 was launched the same way). Epoch: unchanged under protocol Amendment 2 (new run and stop targets for the feature this issue builds).

- `socboard/app.py`, `socboard/errors.py`, `socboard/server.py`: a FastAPI app with `GET /api/health`, the contract's `ApiError { code, message }` for every failure through three handlers (HTTP errors, validation, unexpected), and a server entry point that binds to localhost only.
- `tests/`: error shape, no-echo markers, the contract's shared error responses, the order of checks for `GET /cases` and `POST /cases/{id}/transition` on test-only routes (the repository's proof of #9's tested order), the structural schema comparison with normaliser tests, the server entry point. 68 new Python tests.
- Protected, each an exact diff the human approved: `make backend-run` and `make backend-stop`, the AGENTS.md Run and Backend stop lines, the dependencies (fastapi 0.162.5, uvicorn 0.54.0; dev: httpx2 2.16.0), the last committed by the human.
- Branch `issue-10-backend-skeleton`, PR #78, merge commit `d9a1516`. QA PASS commit `bef1022`, one QA launch, no FAIL.
- Before the Engineer started, in the same session: #10 re-groomed with the #9 follow-ups (Confirm and PM re-record); #71, #73, #74 and #75 filed; #42 closed as superseded; a prioritization review placed twelve side issues in "Supporting issues, in order" (`_docs/planning/roadmap-1-core.md`, PR #76); steering rules `.kiro/steering/backlog-order.md` (every issue gets a place in the order; `[groomed]` title prefix, PR #77) and `.kiro/steering/gate-blocks.md`.
- Environment: the dev container's Claude Code usage ran out, so the Engineer wrote all code in Kiro Web, which has no package index. The human ran `uv add`, `make test`, `make verify`, the run and stop checks and the push from the dev container terminal and the clean clone.

**What I learned:** asking for the human's runs before the first QA launch (the run and stop checks here) gave a single QA round; and output-only commands (`ok` / `FAIL` per check) work when raw HTTP output cannot be pasted.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6812557164, unchanged:

Reflection:
(1) Slowed down: the notes on my first-pass choices were not in this session and no engineer-10 notes file existed in `.scratch/`, so I rebuilt the choices list by reading five source files and a test helper; `gh issue view` also failed on a host mismatch and the saved issue JSON was cut off partway through its comments.
(2) Nearly went wrong: the run and stop criterion could have been written as done because the Makefile targets and the bind tests exist, but nothing ran them, so I marked it not checked; the fastapi version resolved is one patch above the one the issue names, which I stated instead of folding into "matched".
(3) Proposed change: in `_docs/agent-kit/team/software-engineer.md`, add a line to keep a running `.scratch/engineer-N.md` draft (choices made and checks skipped, added as they happen); expected effect is that the completion comment is assembled from the draft rather than from re-reading code; measure by counting the file reads needed to write the comment (this time about ten) on the next two issues, aiming at three or fewer.

### QA

From comment 6812733808, unchanged:

Reflection:
(1) Slowed me down: `gh issue view` failed on a host mismatch and the saved issue JSON was cut off partway through the comment list at the read limit, so I re-read the later comments with a `gh api` jq slice; that was two extra calls before I could read the Engineer's comment.
(2) Nearly went wrong: the raw `git diff --name-only` lists two docs files outside the issue's Files, which could read as out-of-scope edits; only the log and a second diff against the docs commit showed they came from main. I also had no way to run the run and stop targets, so I marked that criterion on the human's results and said so.
(3) Proposed change: in the `issue-dump` target of `Makefile`, also write `.scratch/issue-N-comments.md` with one section per comment; expected effect: a QA launch reads every comment with no truncation and no fallback fetch; measure by counting the fallback fetch commands per QA launch (this one needed two) on the next two issues.

## Launch usage

Active time and tool uses: unknown for every launch (Kiro Web gives neither).
- PM: #10 re-groom (1), filing #71, #73, #74, #75 (4), prioritization review (1). 6 launches.
- Engineer: 2 (first pass with code, tests and protected diffs; completion and Reflection comments).
- QA: 1 (PASS).
- Handovers: the dependency install, tests and verify (human, dev container terminal); the run and stop checks (human); the push (human, clean clone). Two push-check retries: the image variable was not set in a new shell.

## Files created or modified

On `main` through PR #78: `socboard/app.py`, `socboard/errors.py`, `socboard/server.py`, `tests/backend_support.py`, `tests/conftest.py`, `tests/openapi_compare.py`, `tests/test_backend_components.py`, `tests/test_backend_errors.py`, `tests/test_backend_health.py`, `tests/test_backend_openapi.py`, `tests/test_backend_order.py`, `tests/test_backend_server.py`, `Makefile`, `AGENTS.md`, `pyproject.toml`, `uv.lock`. Through PRs #72, #76 and #77: the sweep 3 record, the roadmap supporting list, the two steering files. This file.

## Decisions made by the human

- Sweep 3: proposals 1 to 4 approved and queued for the epoch batch; 5 deferred; 6 filed as #73.
- Prioritization review: the supporting list and its triggers; #42 closed; #75 filed; #9 counts as control, so the epoch batch lands after #11; #71 and #73 in one sitting.
- `/health` added to the contract by #74, after #10.
- #10: the dependency list, the `Makefile` and `AGENTS.md` diffs; the Engineer's choices accepted (unexpected statuses become 500 `internal_error`; `SOCBOARD_HOST` limited to localhost; test-only routes under `tests/`).
- Follow-ups from QA: 1, 2 and 7 folded into later grooming; 3 left; 4 for the human to read; 5 and 6 one small issue.
- The `[groomed]` title prefix marks issues ready to label.

## Mismatches with the spec or design docs

- `openapi.yaml` has no `/health` path (#74 adds it; a test asserting its absence must flip then).

## Commands to validate

- **Test (all):** `make test` (dev container: 115 Python, 154 frontend tests at `bef1022`).
- **Verify:** `make verify` (PASS with the stated `tests/conftest.py` warning).
- **Run:** `make backend-run`, then `make backend-stop`.

## Proposed AGENTS.md changes

none pending (the approved lines are on `main`).

## Temporary changes

- `make clean-scratch`: NOT run; housekeeping is on hold at the human's request.
- Two unpushed local commits on `main` in the Kiro Web checkout (`30f9024`, `fee11dd`) still wait for the human's word.
- The backend was started and stopped by the human; check 14 confirmed no pid file was left.

## Interruptions

- The dev container's Claude Code usage ran out before the Engineer launch; the Engineer moved to Kiro Web (recorded on #10 in an `Orchestrator:` comment).

## Unrelated problems noticed but not fixed

- `gh issue view` fails in Kiro Web on a host mismatch, and `make issue-dump` output is cut off at the read limit for long issues (both QA and the Engineer named it; #73 covers part of it).
- The frontend tests print many `act(...)` warnings (pre-existing).

## Follow-ups for the next session

- #74 (`/health` in the contract): trigger reached; groom it, including flipping `test_health_is_not_in_the_contract`.
- #11 (data model): the next Core issue; check its approved body against `openapi.yaml` before the Engineer.
- #13 to #20: when each is groomed, require domain refusals to use the app's error class that carries a code (otherwise an unexpected status becomes 500).
- #14: the schema comparison ignores `default` and `minLength`; check them when the length limits arrive.
- A small issue for `backend-stop` matching any `-m socboard.server` process and `backend-run`'s two-second start check, placed before #22.
- Sweep 4 evidence: the Engineer's and QA's Reflections both name the truncated issue dump; the Engineer proposes a running notes draft.
