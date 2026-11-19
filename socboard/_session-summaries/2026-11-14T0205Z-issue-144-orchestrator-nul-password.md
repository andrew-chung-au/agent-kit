# Issue #144: A login password with trailing NUL bytes is accepted as the correct password

**Date:** 2026-11-14T02:05Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`hashlib.scrypt` gives one key for `"pw"`, `"pw\x00"` and `"pw\x00\x00"`, so a password with trailing NUL bytes verified as correct. Option A of the issue's Design was built: `hash_password` raises `ValueError` (fixed message, no password) for a password containing a NUL, and `verify_password` treats such a password as wrong after one scrypt run against the dummy hash, so it costs what any wrong password costs. No hash format change and no contract change; `socboard/auth.py` was not edited. Tests were added in `tests/test_auth_passwords.py` (the NUL cases, the old-hash fixture, the one-scrypt counter, the no-echo `ValueError`) and `tests/test_auth_api.py` (the same 401 for a NUL password as for a wrong one, for a real and an unknown username; no password in the body or any log record).

Worked by Session A (Kiro Web) in a git worktree on branch `issue-144-nul-password`, draft PR #149, alongside #139 in a second worktree. Standard tier, one QA launch. QA PASS at `7371424`; CI run 43515196432 (1520 Python tests, 1508 before; 208 frontend; `Assertion lines: 18 added, 0 removed`; `VERIFY: PASS`). The human merged PR #149 on 2026-11-14 (merge commit `9d3537d`, on `origin/main`). This summary is committed after the merge, on its own pull request, because the session did not write it on the issue branch before the human merged (`.kiro/steering/delivery-pace.md` item 2 asks for that); see Interruptions.

**What I learned:** a fix that lives entirely in `verify_password` keeps the timing parity of the unknown-user path for free; the counter test makes that parity checkable.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

The Engineer and QA ran as subagents that ended when they returned; no Reflection was asked for before they ended, and a new launch would not be the role that did the work.

## Launch usage

- Engineer: one launch (subagent); active time not recorded; it ran a stdlib-only sanity script on Python 3.11 and relied on CI for the test run.
- QA: one launch (subagent, fresh); active time not recorded.
- Reviewer: one launch (subagent, read-only, fresh); active time not recorded.

## Files created or modified

- `socboard/passwords.py`
- `tests/test_auth_passwords.py`
- `tests/test_auth_api.py`
- `_session-summaries/2026-11-14T0205Z-issue-144-orchestrator-nul-password.md` (this file)

## Decisions made by the human

- Option A (refuse a password containing a NUL, 401, no hash format change), by approving the groomed body (hash `57a1ac8a...c95588`).
- Reviewer findings: the human approved the orchestrator's recommendations on 2026-11-13: no action on finding 1 (a NUL in the login username may give a 500 on Postgres) and no action on finding 2 (an optional readability refactor of `verify_password`). Finding 1 is in any case fixed on `main` by #104 item 6: `_find_user` in `socboard/auth.py` now returns no user for a username containing a NUL, before any lookup.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Test (one file):** `make test-one FILE=tests/test_auth_passwords.py` and `make test-one FILE=tests/test_auth_api.py`
- **Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

A git worktree at `.scratch/wt/144` (git-ignored), used for the issue branch; removed when this session cleans up. No system changes, no processes started, no installs.

## Interruptions

The issue merged before its session summary was written: the session was waiting at the decision point for the human's labels on the Reviewer findings when the human merged. No work was lost; this summary is written from the issue's comments, the pull request and CI.

## Unrelated problems noticed but not fixed

- QA's Low risk: if the scrypt parameters are raised later, a NUL password and a wrong password could differ in timing for a user whose stored hash uses old parameters (the NUL path runs against the dummy hash's parameters). Recorded in the QA comment; no issue filed.
- `make issue-close` checks only that a Close comment names a merge commit, not that the commit is on `origin`; #104, #114 and #120 were closed with merge commits that were then only in the human's local sandbox (since pushed). Recorded in `_docs/planning/deploy-coordination.md` (PR #157).

## Follow-ups for the next session

- After this summary merges, the orchestrator posts the Close comment and runs `make issue-close N=144`.
