# Issue #80: Harden make backend-run and backend-stop

**Date:** 2026-11-13T08:32Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Kiro Web worked #80 as the third of four issues in one `Makefile` sitting (#73, #71, #80, #75; the human's order). Ponytail was on. PR: #127 (draft). The branch started from `main` at `16c2a6f`, which already held #73 and #71.

- **Claim-time check:** the four decision records dated after grooming (auth tokens, ponytail adopt, ingest API key, close floor) say nothing about the two targets, the health route, the host and port settings or `/proc`. No conflict. The epoch hold in the body ("held until #12 closes") no longer applies: #12 is closed and the ponytail trial was shelved (human ruling, in the roadmap).
- **Facts from the current code for the checks:** `/api/health` is unchanged (open without a token, `{"status": "ok"}`). Since #13 the server exits 2 without `SOCBOARD_TOKEN_SECRET` (32 characters or more), so the human's run checks need it set.
- **`backend-stop`:** also requires `readlink -f /proc/<pid>/cwd` to equal this checkout's root. It refuses, killing nothing, on a mismatch (pid file kept) or when the cwd cannot be read; no fallback to the command line.
- **`backend-run`:**
  - Refuses to start if anything already listens on the port.
  - Polls `/api/health` once a second on a 30-second clock. It says "started" only after a 200 with `{"status": "ok"}` while the pid is alive (zombies count as dead).
  - A late failure or a timeout prints the last 20 log lines and removes the pid file. A timed-out start is stopped (10-second wait, zombie-aware).
- **Helper:** `scripts/backend_probe.py` (standard library only) takes the host and port from the server's own `resolve_bind`, so a value the server rejects never reaches a socket or URL. Only `backend-run` calls it.
- **Stale-pid rule (outside the issue's wording, approved by the human):** a pid is stale only when `kill -0` fails and `/proc/<pid>` is gone. Another user's live process is refused and its pid file kept; before, it was called stale and its file deleted. This makes the issue's own "a process the user may not inspect" case reachable. Cost: a stale file whose pid was reused by another user's process now gives exit 1 and a manual removal.
- **Approvals:** the human approved the exact `Makefile` diff twice, in this session: the first version, then the two Reviewer fixes. Both commits used `HUMAN_APPROVED=1`.
- **CI:** green on every push (last: runs 43393176567 and 43393171543 on `07e0fa1`). QA PASS at `4c71b0e`; after the decision point a fresh QA re-check of only the changed parts passed at `07e0fa1`.
- **Reviewer:** applied findings 1 (the wait could take about 90 s, now a clock loop with a 1-second probe timeout; the timeout message comes at 30 to 32 s), 2 (the timeout path's wait uses `alive`) and 3 (task-file Step 8a for `::1` and `localhost`). Not applied, by the human's decision: 4 (the `ps` fallback is dead code; non-Linux is out of scope in the issue) and 5 (the `AGENTS.md` Run and Backend stop lines are still true).
- **Not verified:** every run check is the human's, in the dev container: `_human-tasks/2026-11-13T0745Z-human-task-080-engineer-check-backend-run-stop.md` (Steps 1 to 12, including 8a). `make test` and `make verify` are in Step 10. #10's record names 10 distinct outcomes, not 14; the task file says so.

**What I learned:** the Engineer called the stale-pid rule "outside the criteria", but the issue's own refused case 2 needs it; asking for the trade-offs showed that and gave the human a real choice. Also, QA's first comment post was refused by the secret scan because it named an env file; reword and post again.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- Engineer (first launch): active time unknown, tool uses unknown (Kiro Web gives neither).
- QA (first): active time unknown, tool uses unknown.
- Reviewer: active time unknown, tool uses unknown.
- Engineer (second, Reviewer fixes): active time unknown, tool uses unknown.
- QA (re-check, fresh launch): active time unknown, tool uses unknown.

## Files created or modified

- `Makefile` (protected; `backend-run` and `backend-stop` only; approved diffs).
- `scripts/backend_probe.py` (new).
- `_human-tasks/2026-11-13T0745Z-human-task-080-engineer-check-backend-run-stop.md`
- This file.

## Decisions made by the human

- Approved the first `Makefile` diff and the stale-pid rule (Option A, after the trade-offs were explained).
- Decision point: apply Reviewer findings 1, 2 (new path only) and 3; do not apply 4 or 5; do not change `backend-stop`'s own wait. Then approved the second `Makefile` diff.
- The sweep stays set for after #75.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI on the branch; green on `07e0fa1`).
- **Run / Backend stop:** `make backend-run` and `make backend-stop`; the by-hand cases are in the human-task file above.

## Proposed AGENTS.md changes

none. The Run and Backend stop lines stay true; they do not mention the new refusals (port in use, not this checkout). The human decided to leave them.

## Temporary changes

none. No server was started in this session. `make clean-scratch` ran.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `backend-stop`'s own 10-second wait still uses `kill -0`, so an unreaped zombie would read as "did not stop" (QA Low; no failing case seen).
- `backend-run` still treats another user's live pid in a stale pid file as not running (the PM left it out of scope).
- The 1-second request timeout is per socket read, so a listener that sends bytes slowly could stretch one probe (QA Low).

## Follow-ups for the next session

1. After the human merges #80 and the Close is posted, start #75 from the latest `main`, with a hash check first, and then post the notice on #31 when #75 merges.
2. Run the sweep after #75 (the human's choice).
3. The human's run checks for #73, #71 and #80 are open.
