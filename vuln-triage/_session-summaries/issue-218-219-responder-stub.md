# Issues #218 and #219: demo defect and responder in stub mode (task 28a and 28b of #160)

**Date:** 2026-10-26
**Spec version:** 76c73f7

## What changed and why

PR 217 (the D4 false-positive rule and decisions F1-F3) was merged, so the PM groomed #160 (task 28) and split it into five pieces, all approved by the owner: #218 (28a), #219 (28b), #220 (28c), #221 (28d), #222 (28e). #160 stays open as the parent. The split comment is on #160 (6404873337).

Two pieces were built in parallel worktrees and merged:

- **#218:** `VT_DEMO_DEFECT=notify_no_fix`. The owner-notification formatter fails for a finding with no fixed version; the job ends `failed` with `format_failed`, nothing is sent. Startup refuses the variable unless `DEPLOYMENT_ENVIRONMENT` is dev or test (the same fail-closed helper as `VT_FEEDS`); an unknown value is refused everywhere. QA PASS (6406748025).
- **#219:** a new top-level `responder/` project (stub mode only, no SDK): webhook receiver with bearer secret, repeat-fingerprint guard that survives restart, structured action log, and the false-positive "no change" path. QA PASS (6406748685). 51 tests.
- A protected commit (`5ab7b7b`) adds `responder-install` and `responder-test` to the `Makefile` and records them in `AGENTS.md`, so `make install`, `make test` and `make verify` now cover the responder tests.

## Files created or modified

- Backend: `backend/vulntriage/ingest/settings.py`, `backend/vulntriage/mail/message.py`, `backend/vulntriage/mail/delivery.py`, `backend/vulntriage/main.py`.
- Tests: `tests/test_demo_defect.py`, `tests/test_compose_responder.py` (compose-marked), `tests/test_notifications.py`, `tests/test_marker_hygiene.py`.
- New `responder/` project: `pyproject.toml`, `uv.lock`, `vt_responder/` (config, guard, action log, API client, fakes, stub runner, app), `tests/`.
- Docs: `_docs/testing.md` (`DEPLOYMENT_ENVIRONMENT` wording; nine `I-RESP-HOOK-*` rows), `_docs/ai-usage-log.md`, `_docs/roadmap.md` (check-in row), this summary.
- Protected: `Makefile`, `AGENTS.md` (own commit `5ab7b7b`).

## Decisions made by the human

- Split of #160 into five pieces, and all seven PM recommendations: separate `responder/` project; 28c owns the `ci/test-compose.sh` branch and #161 owns the `verify.yml` job; #182 stays separate and depends on #218; close #172 and #157 before #220; the 28e check is a `.scratch/` script plus a runbook.
- Start #218 and #219 in parallel.
- Asked whether adding the responder to `make test` would make GitHub CI onerous: I checked the workflow (only the final `verify` job runs `make install` and `make verify`) and timed the suite (51 tests in about 1 s); the owner then approved the exact `Makefile`/`AGENTS.md` diff. Protected-change approval record: #219 comment 6409216064.

## Mismatches with the spec or design docs

- `architecture.md` A34 and `roadmap.md` S4/C6 still describe the responder runtime as open; F2 settled it. Not edited yet.
- `_docs/tasks.md` tasks 28 and 29 both claim the `responder` CI job. Not edited yet; the split assigns the cases to #220 and the workflow job to #161.
- `testing.md` ~line 434 still has older `ASSUMPTION: T-A8` wording (left alone).

## Commands to validate

- **Verify:** `make verify` (passed at the end of this session: frontend 89, backend 515, responder 51).
- **Test (responder):** `make responder-test`.

## Proposed AGENTS.md changes

None open. The `responder/` Layout line and the responder Commands lines were approved and committed in `5ab7b7b`.

## Temporary changes

- Two worktrees under `.claude/worktrees/` for the parallel Engineers: removed (`git worktree remove --force`). The two local `worktree-agent-*` branches are merged and still exist locally; they were never pushed.
- `responder/.venv` created by `uv sync` (git-ignored); left in place.
- `.scratch/` cleaned with `make clean-scratch` at the end of the session (see the commit that adds this file).

## Permission review

- Read-only (propose allowing): QA #219 ran `uv sync --project responder --locked` (installs into git-ignored `responder/.venv`; network; merits request). Orchestrator ran `make responder-install` (same, via the new target).
- Writes to the record (keep asking): `make issue-comment N=219 FILE=.scratch/approval-219.md` (approval record); `HUMAN_APPROVED=1 git commit` for the protected `Makefile`/`AGENTS.md` change (matched `ask` rule, owner approved the exact diff); `git push -u origin claude/ecstatic-cannon-2i1taq` (cloud session branch). GitHub issue creation (#218-#222) and comments through the GitHub tools.
- Risky (propose denying): `git worktree remove --force` for the two Engineer worktrees (destructive, but both were created by this session and were merged first). The #219 Engineer's comment says it ran `uv lock --project responder` and `make install` (network or install) and did not know whether approval was asked. The #218 Engineer, the #218 and #219 QA comments and the PM report list no other approvals.

## Interruptions

none. The GitHub tool server disconnected and reconnected several times; the one affected write (the approval record) went through `make issue-comment` instead.

## Unrelated problems noticed but not fixed

- A failed defect job retries on every poll, so the log repeats while `VT_DEMO_DEFECT` is on.
- `compose.yaml` sets no `DEPLOYMENT_ENVIRONMENT`; #220 must set `dev` explicitly to turn the defect on.
- The responder logs job `state` strings unfiltered (field allowlisted, value not); they come from the backend's own enum.
- No test covers concurrent delivery or a run that raises in the responder.

## Follow-ups for the next session

- #220 (28c): needs the owner to close #172 and #157 first; add `--build` to the container `P-PROD-REFUSAL` run; confirm the real Grafana webhook body and whether a test alert carries a `fingerprint` (the responder returns 400 without one).
- #221 (28d): needs the model name pinned by the owner; must run the agent in a background task (real runs outlast Grafana's webhook timeout); a run that raises should release its fingerprint, with a retry cap.
- #222 (28e): owner-run (fine-grained token and the refused-push proof).
- Align `tasks.md` 28/29, `architecture.md` A34 and the roadmap S4/C6 wording with F2.
- The container form of `P-PROD-REFUSAL` and the new `make install`/`make verify` path in the GitHub `verify` job have not been run in CI yet.
