# Issue #16: Claim a case: single owner

**Date:** 2026-11-13T03:43Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox after Kiro's hand-over, committing directly on `main` from `dbea8ae`. Ponytail was on; this is the fifth issue in the ponytail group.

- **Endpoint:** `socboard/cases.py` adds `POST /api/cases/{id}/claim` (`claimCase`) on the existing cases router. The claim is the data-model record's single conditional UPDATE (`owner_id IS NULL AND status <> 'Closed'`); only a lost claim reads the case, to choose 404, 409 `case_closed` or 409 `already_claimed`, then rolls back. A win appends the `claimed` entry through `append_audit` in the same transaction.
- **Supporting:** `socboard/errors.py` adds `case_closed` and `already_claimed`; `socboard/domain.py` adds `ACTION_CLAIMED`; `getCase` and the claim share `_case_detail`. Tests are in `tests/test_claim_api.py` (18), including a two-session race on a real database file held behind a third connection's row lock, which uses nothing SQLite-only.
- **Rounds:** Engineer round 1 at `5985a83`, QA PASS. The Reviewer said "Ship" with five findings; the human approved applying 16-1, 16-2, 16-3 and 16-5, done in round 2 at `f7e6062`; QA re-checked only that change and passed.
- **Hand-over rules kept:** no new route file (HTTP-layer list in `tests/test_data_audit.py` unchanged), audit only via `append_audit`, explicit rollback after a refusal, no closing keyword in commit subjects.
- **Follow-up filed:** #112 (retryable contract code for a lock timeout), unlabelled and ungroomed.

**What I learned:** the Reviewer found two gaps (no atomicity test, detail read after commit) that a full QA PASS had not; both guard the ownership invariant that #17 and #18 will edit around.

## Reflection

### PM

Reflection:
1. Slowed: QA's risks are unnumbered prose bullets, so "risk 2" had to be matched by hand to "Lock timeout answers 500 `internal_error`" in the PASS comment.
2. Nearly wrong: #16's groomed criteria said "assignment row" although the approved data-model record (`_docs/decisions/2026-11-12T0834Z-data-model.md`) had dropped that table; QA had to reinterpret two criteria. Grooming did not re-read the record after approval.
3. Proposal: `_docs/agent-kit/team/pm.md`, add "re-check criteria against decision records approved after grooming"; effect: no reinterpreted criteria; measure: count of QA "Criterion wording" notes per issue.

### Engineer

Reflection:
1. Slowed: one Edit in round 2 failed because I anchored it on a guessed line, not one I had read ("String to replace not found"). Each `make verify` run took about 110 s (74 s Python, 36 s frontend).
2. Nearly wrong: round 1 shipped with no test that the owner and the `claimed` entry are saved together, and it read the detail after commit (Reviewer 16-1, 16-2). QA passed both. Nothing was blocked.
3. Proposal: add a `real_crash_client` fixture (real app, `raise_server_exceptions=False`) to `tests/conftest.py`, next to `crash_client`. Effect: 500-path tests reuse one fixture, so it's easier to write a failure test like 16-1. Measure: count inline `raise_server_exceptions=False` in `tests/` outside conftest (6 today); it should stop growing.

### QA

Reflection:
1. Slowed: scratch tests can't use `tests/conftest.py` fixtures directly. I had to list `.scratch/qa16/` and read its `conftest.py` before copying it into `.scratch/qa16r2/` (two extra steps). Also, `make issue-comment` isn't under Commands in `AGENTS.md`, so I grepped the `Makefile` to find its usage.
2. Nearly went wrong: the session's auto-mode note encouraged shell reads and edits (cat, sed, heredocs), which `AGENTS.md` forbids. I kept to the built-in tools. Nothing was blocked, and `make assert-clean` passed.
3. Proposal: add a Commands line to `AGENTS.md` for `make issue-comment N=<n> FILE=.scratch/<name>.md` (first line `PM:`, `Engineer:`, `QA:` or `Orchestrator:`). Expected effect: no Makefile lookup before posting. Measure: the number of `Makefile` greps for `issue-comment` in QA and Engineer transcripts over the next 3 issues, against 1 this session.

### Ponytail

Engineer: "Reused `append_audit`, `add_case`/`run` from the queue tests, the existing cases router and the shared `_case_detail` helper. Skipped a new route module and an assignment table (round 1), and finding 16-4 (round 2, as the human decided). Missed one reuse: `tests/conftest.py` already has `crash_client` … and I built an inline `TestClient(real_app, raise_server_exceptions=False)` instead of looking first."

## Launch usage

Tool: Claude Code; model: unknown to the orchestrator for subagents. Figures copied from the completion notifications.

- Engineer round 1: 469 s, 34 tool uses.
- QA round 1 (PASS at `5985a83`): 254 s, 24 tool uses.
- Reviewer: 112 s, 17 tool uses.
- PM (file #112): 41 s, 9 tool uses; resumed for reflection: 27 s, 4 tool uses.
- Engineer round 2: 310 s, 26 tool uses; resumed for reflection: 32 s, 6 tool uses.
- QA round 2 (PASS at `f7e6062`): 227 s, 23 tool uses; after the reflection resume the notification read 264 s, 26 tool uses (cumulative or per-resume: unknown).

## Files created or modified

`socboard/cases.py`, `socboard/errors.py`, `socboard/domain.py`, `tests/test_claim_api.py` (new), this file.

## Decisions made by the human

- "Assignment row" criteria: the issue text stays; they are met as the data-model record reads them (owner set once to the winner; exactly one `claimed` entry).
- Lock timeout: keep the 500 `internal_error` for Core; the PM filed #112 for a retryable contract code.
- Finding 16-1: useful. Finding 16-2: useful. Finding 16-3: useful. Finding 16-4: correct-minor. Finding 16-5: correct-minor. QA had raised none of them. Applied 16-1, 16-2, 16-3, 16-5; 16-4 not applied (the explicit rollback stays).
- Accepted QA risks: the concurrency test's 0.5 s sleep assumption; Postgres run not done (Deploy phase); merge overlap with #18 in `cases.py`/`errors.py`.
- Sweep (due: 6 closed since 2026-11-12) and the ponytail comparison against #8–#12: a fresh PM runs both after #16 closes.

## Mismatches with the spec or design docs

- #16's criteria say "assignment row"; the approved data-model record dropped the assignment table. Ruled above; not edited.
- The claim route documents a 422 it can never return, as `getCase` does; the contract test names this difference.

## Commands to validate

- **Verify:** `make verify` (PASS at `f7e6062`: 1302 Python, 157 frontend, no weakened tests).
- **Test (one file):** `make test-one FILE=tests/test_claim_api.py` (18 passed).

## Proposed AGENTS.md changes

- From QA's reflection (not applied, for the human): add `make issue-comment N=<n> FILE=.scratch/<name>.md` to Commands.

## Temporary changes

none. No processes started. The orchestrator runs `make clean-scratch` at the end of this session.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- `tests/` has six inline `raise_server_exceptions=False` clients outside `conftest.py` (Engineer's reflection).

## Follow-ups for the next session

- Launch the PM for the sweep, including the ponytail comparison record.
- #112 needs grooming before it is approved. #17 is next in order.
