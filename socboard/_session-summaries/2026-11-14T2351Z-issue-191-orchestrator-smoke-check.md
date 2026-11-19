# Issue #191: A post-deploy smoke check that runs on the server and, for the health route, from outside

**Date:** 2026-11-14T23:51Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`python -m socboard.smoke <url> [--health-only]` (and `make smoke URL=<url> [HEALTH_ONLY=1]`) checks a running app so a deploy can tell it works: the health route answers, the Lead can log in, one synthetic alert is ingested, its case is in the queue within 5 seconds, and the Lead can read its `ingested` audit entry. `--health-only` runs the first step only and needs no credential, so CI can run it against the public URL. The module lives in `socboard/` so it ships in the image of #190.

- `socboard/smoke.py` (standard library for the checks): URL rules refused with exit 2 before any request (no credentials in the URL, `http` only for loopback, no query or fragment, no space or control character); no redirect followed; the password and the key come from the environment only; no secret, token or response body is ever printed, and a refusal's `code` only when it is a short lower-case word; one request stops after 10 seconds and the whole run after 60, counted from when the connection starts, by a watchdog that shuts the socket (name lookup time is not counted, by the human's ruling); a 429 is reported and not retried.
- `tests/test_smoke.py` (stub servers on loopback, including servers that send one byte at a time) and `tests/test_smoke_make.py` (the target's argument rules and one run through make).
- `socboard/settings.py`, the README rows and the example env file say the Lead's seed password and the ingest key are also read by the smoke check; the README has its own section.
- Protected, committed with `HUMAN_APPROVED=1` after the human approved the exact diffs: the `Makefile` `smoke` target (with `--` before the URL, so `URL=-h` is refused) and the `AGENTS.md` Commands line (worded so that any failure is non-zero and the module's 1 and 2 are explained, because make reports both as 2).

Worked by the Hardening session, Standard tier, no Engineer launch. Branch `issue-191-smoke-check`, PR #200, merge commit `612e1cf`, head `7a09fbe`. Claim: https://github.com/andrew-chung-au/socboard/issues/191#issuecomment-6881448092. QA PASS at `7a09fbe` (fourth launch): https://github.com/andrew-chung-au/socboard/issues/191#issuecomment-6883665279.

**What I learned:** a limit written as "stops after N seconds" invites every network shape. The criterion was reworded once ("counted from when the connection starts; name lookup is not counted") and the code passed on the fourth launch without further changes.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: 2 launches (grooming, comments 6878161142 and 6878175000; sweep entry); QA: 4 launches (FAIL at `6ad48ce`, FAIL at `0793c5f`, FAIL at `2f573c7`, PASS at `7a09fbe`). Active time and tool uses were not given: unknown.

## Files created or modified

- `socboard/smoke.py`, `tests/test_smoke.py`, `tests/test_smoke_make.py` (new)
- `socboard/settings.py`, `README.md`, `.env.example` (rule text and one section)
- `Makefile`, `AGENTS.md` (protected, approved)
- `_session-summaries/2026-11-14T2351Z-issue-191-orchestrator-smoke-check.md` (this file)

## Decisions made by the human

- Labelled `approved`; applied the grooming corrections to the body (comment 6878175000); approved three sets of exact diffs for the `Makefile` and `AGENTS.md`.
- After the third QA FAIL: reworded the time-limit criterion (Confirm comment 6883478255, hash 5e03db69...), shipped with the Low findings noted, and asked for one follow-up (issue 212).
- Merged PR #200.

## Mismatches with the spec or design docs

Deploy decision record `_docs/decisions/2026-11-13T2156Z-deploy.md`, line 32, says the smoke check measures the latency Australian reviewers see. A check run on the server's loopback cannot; it measures ingest to queue only. Proposed in the grooming comment: reword it, and leave a real latency measurement to an observability alert. Not applied.

## Commands to validate

- **Verify:** `make verify` (CI runs 43635813292 (push) and 43635817191 (pull_request) on `7a09fbe`; local Python tests 2182 passed; the frontend tests did not run locally, bun is not installed in this sandbox).
- **Test (one file):** `make test-one FILE=tests/test_smoke.py`, `make test-one FILE=tests/test_smoke_make.py`.
- **Smoke check:** run against the real app in a `.scratch/` script: two full runs and a health-only run passed, and a wrong password failed at step 2 with HTTP 401.

## Proposed AGENTS.md changes

none (the approved Commands line is committed).

## Temporary changes

- Python environment in `.scratch/venv` and `.scratch/uv-cache` and the `.venv` symlink (about 125 MB with other scratch files, approved); to be deleted when the Hardening work ends.
- Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

Low findings of the third and fourth QA, outside the criteria as worded:
- A truncated body counts as a whole answer, and a non-ASCII URL path exits 1 not 2: follow-up issue 212.
- A name that resolves to several unreachable addresses takes one connect timeout per address (excluded by the reworded criterion).
- A full run imports `socboard.ingest` and `socboard.seed` for two length constants, so it needs the app's packages installed.
- IPv6 loopback could not be tested live (the sandbox cannot bind `::1`).
- `tests/test_smoke_make.py` is not named in the issue's Constraints.

## Follow-ups for the next session

- Label and work #212 if wanted.
- D20 and D22a (wiring the check into the deploy command and CI) are not filed yet.
- On the first real run on the server, check which client address the app sees (the login counters use it); the README marks it `VERIFY:`.
- The sweep entry (`2026-11-14T2005Z-measure-pm-sweep.md`) is waiting for the human's ruling.
