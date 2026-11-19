# Issue #185: Reset an existing user's password without deleting the user

**Date:** 2026-11-14T12:34Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`python -m socboard.set_password <username>` sets a new password for one existing user, so the deploy runbook (D23) has a rotation step; `make seed` still never changes an existing user. The password comes from `SOCBOARD_NEW_PASSWORD`, never the command line.

- `socboard/set_password.py` (new): refuses, with exit 2 and fixed text before any write, a username that is missing, blank, padded, differently cased, or holds a NUL or a lone surrogate, and a password under 12 characters or holding a NUL; checks the URL and then that the database is migrated (exit 1); then one `UPDATE` of `password_hash` on one exactly matched row. It prints and logs no password, hash or username, creates no user, issues no DDL and writes no audit entry.
- `socboard/settings.py` (`SOCBOARD_NEW_PASSWORD`, secret, not required in deployed mode), README (a row and a "Resetting a user's password" paragraph with the token, secret-rotation and counter limits), the example env file.

Worked by the Hardening session, Standard tier, no Engineer launch. Branch `issue-185-set-password`, PR #186, merge commit `a7ace99`, head `d6efe30`. Claim: https://github.com/andrew-chung-au/socboard/issues/185#issuecomment-6877210322. QA PASS at `d6efe30`: https://github.com/andrew-chung-au/socboard/issues/185#issuecomment-6877291445.

**What I learned:** the Deploy draft's `make set-password USER=<username>` would silently target the shell's own `USER` when the argument is left out, so the make variable is `ACCOUNT`; and any new `SOCBOARD_` name has to enter the settings list, README table and example env file together or the agreement tests fail.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

What slowed me down: nothing in CI (one push, green). What nearly went wrong: I started this issue's edits on the `issue-183-ingest-limit` branch before cutting `issue-185-set-password`; I moved them with a stash before the first commit, so nothing reached the wrong branch. Proposed change: none.

## Launch usage

QA: 1 launch (pass at `d6efe30`). Active time and tool uses were not given: unknown.

## Files created or modified

- `socboard/set_password.py` (new), `socboard/settings.py`
- `README.md`, `.env.example`
- `tests/test_set_password.py` (new), `tests/test_settings.py`
- `_session-summaries/2026-11-14T1234Z-issue-185-orchestrator-set-password.md` (this file)
- Protected, not in the branch: `Makefile` and `AGENTS.md` (see below).

## Decisions made by the human

- The `ACCOUNT` make variable, confirmed ("confirm account is ine", read as "fine").
- Applied the `approved` label.
- Merged PR #186.

## Mismatches with the spec or design docs

PR #186 merged without the proposed `Makefile` target and `AGENTS.md` Commands line, so `make set-password` does not exist on `main` yet (`git show origin/main:Makefile` has no `set-password` target). The command runs as `python -m socboard.set_password <username>` meanwhile.

## Commands to validate

- **Verify:** `make verify` (CI runs 43594641879 and 43594648283 on `d6efe30`: 2028 Python tests, 209 frontend tests).

## Proposed AGENTS.md changes

The exact diff for `Makefile` and `AGENTS.md` was given to the human in the decision-point message and kept as `.scratch/set-password-protected.diff` (it applies cleanly with `git apply --check`). It adds a `set-password` target before `migration-new:` (validated like `migration-new`, running `uv run --locked python -m socboard.set_password "$$ACCOUNT"`) and a **Set password** line before **New migration** in the Commands list. Not applied; it needs the human's approval and a `HUMAN_APPROVED=1` commit.

## Temporary changes

none (the stash used to move the edits was popped and dropped).

## Interruptions

none

## Unrelated problems noticed but not fixed

- The repository has no Postgres CI job, so the `VERIFY:` in #185 about running the test on Postgres had nothing to run; the Postgres path (rowcount, UPDATE privilege) is untested.

## Follow-ups for the next session

- Apply the `Makefile` and `AGENTS.md` diff above, with the human's approval, then D23 can cite `make set-password`.
- Low findings left: the log-capture test covers a success and three refusals only; the login test does not exercise the failed-login counters.
