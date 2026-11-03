# Issue #241: real agent in the background, with a retry cap (follow-up to #221)

**Date:** 2026-10-26
**Spec version:** not changed (no protected file touched)

## What changed and why

Engineer subagent on `claude/241-background-run`, branched from `origin/claude/f4-real-runner-followup` (the #221 runner is not in `main` yet). Tested with a fake session only; no key, no network, no live SDK call.

- **Background run** (`app.py`, `_BackgroundRuns`): in real mode the webhook claims the fingerprint through `FingerprintGuard` and submits the run to a bounded `ThreadPoolExecutor` (standard library); the answer is `accepted` straight away. Stub mode keeps the synchronous path and its tests unchanged.
- **Guard reused, extended** (`guard.py`): the claim also marks the run in flight, as before. `finish(failed=...)` now also counts consecutive failures per fingerprint (a success or a `resolved` clears the count); new `failed_runs`, `abandon` (a claimed run that never started: released, not counted) and `lost_on_restart`.
- **Failures:** `_job` catches every exception, including cancellation, logs `run_failed` with `reason` `run_raised` or `run_cancelled`, and always ends the claim in `finally`. A queued run cancelled at shutdown is released by the future's done-callback.
- **Retry cap:** `RESPONDER_MAX_FAILED_RUNS`, default 3. After N consecutive failed runs a firing logs `retry_cap_reached`, is not claimed and starts no run, until a `resolved` arrives. The count is in memory, so a restart clears it.
- **Concurrency choice:** `RESPONDER_MAX_CONCURRENT_RUNS` (default 1). A second alert is queued and accepted (`RESPONDER_MAX_QUEUED_RUNS`, default 10); only past the queue is it refused: claim released, `run_refused` logged, HTTP 503. Reason: Grafana retries a non-2xx, but a refused alert that stayed claimed would be "repeat_ignored" forever, and a queued alert needs no retry at all; the 503 backstop releases the claim, so the retry runs.
- **Run lost on restart:** the handled record alone cannot tell "done" from "claimed by a run that died". The guard now mirrors the in-flight set to `<state file>.inflight` (written before the handled record on claim). At the next start every fingerprint in it is released, `run_lost_on_restart` is logged, and the alert's next firing runs again: released, not stuck. A run that finished stays handled. An unreadable in-flight record refuses to start, like the handled record.
- **Config:** three new settings in `config.py` with safe defaults; `.env.example` lists the three names with no value.

## Files created or modified

`responder/vt_responder/{app,guard,config}.py`, `responder/tests/test_background.py` (new, 26 cases), `.env.example`, `_docs/ai-usage-log.md`, `_docs/roadmap.md`, this summary.

## Decisions made by the human

none in this session.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify BASE=origin/claude/f4-real-runner-followup` PASS (frontend 89, backend 532, responder 257).
- **Test (responder):** `make responder-test`.

## Proposed AGENTS.md changes

none. (The `RESPONDER_MAX_*` names are in `.env.example`; `compose.responder.yaml` does not pass them, and real mode is not run in Compose.)

## Temporary changes

`make responder-install` and `make install` ran (git-ignored `responder/.venv`, `backend/.venv`, `frontend/node_modules` in this worktree). No processes started; no system configuration changed.

## Permission review

- Read-only (propose allowing): none beyond `make issue-dump` and `git fetch`.
- Writes to the record (keep asking): `make responder-install` and `make install` (network, install into git-ignored folders); `make issue-comment` for the Engineer comment.
- Risky (propose denying): none.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- A timed-out session thread is abandoned, not killed (as in #221); the worker pool slot is held until the SDK's own timeout stops it, so a stuck session can delay the queue.
- The failure count is in memory, so a restart resets the retry cap.
- Graceful shutdown does not wait for a running agent; the process exit ends it, and the next start releases its claim.

## Follow-ups for the next session

- QA on #241; then #222, #233 and the recorded drill (task 39).
- Pass the new `RESPONDER_MAX_*` names through `compose.responder.yaml` if real mode is ever run in Compose.
