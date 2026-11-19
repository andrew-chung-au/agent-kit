# Issue #13: Seeded minimal auth: login, bearer token and role checks

**Date:** 2026-11-12T23:17Z (UTC)
**Spec version:** 36d9ad7

Tier: Heavy (from the PM proposal). Engineer session, launched by the orchestrator; QA (two launches) has not run yet.

## What changed and why

Two Analysts and one Lead can now log in and get a bearer token, and every protected route knows who is calling and in what role (spec section 2). Tokens are HMAC-SHA256 signed `<payload>.<signature>` with a fixed 8-hour lifetime. Passwords are scrypt hashes (N=2^17, r=8, p=1). The role is read from the database on every request. `create_app()` requires `SOCBOARD_TOKEN_SECRET` and wires #11's engine with one session per request. `make seed` adds the three users from three password variables. The decision record is `_docs/decisions/2026-11-12T2255Z-auth-tokens.md`. Engineer comment: https://github.com/andrew-chung-au/socboard/issues/13#issuecomment-6838721775

**What I learned:** FastAPI 0.162 keeps an included router as one `_IncludedRouter` entry in `app.routes`; a route walk needs `fastapi.routing.iter_route_contexts`.

## Reflection

### Engineer

unknown (role not asked; reflection is collected after QA PASS)

## Launch usage

none (this session launched no subagents)

## Files created or modified

- New: `socboard/auth.py`, `socboard/passwords.py`, `socboard/tokens.py`, `socboard/schemas.py`, `socboard/sessions.py`, `tests/test_auth_api.py`, `tests/test_auth_config.py`, `tests/test_auth_passwords.py`, `tests/test_auth_seed.py`, `tests/test_auth_tokens.py`, `_docs/decisions/2026-11-12T2255Z-auth-tokens.md`
- Modified: `socboard/app.py`, `socboard/server.py`, `socboard/seed.py`, `socboard/errors.py`, `tests/backend_support.py`, `tests/conftest.py`, `tests/data_support.py`, `tests/test_data_audit.py`, `tests/test_inventory.py`, `README.md`, `_docs/index.md`
- Staged, not committed (waiting for approval): `AGENTS.md` (one clause on the Run line)
- Unchanged: `tests/test_backend_order.py`, `Makefile`, `pyproject.toml`, `uv.lock`

## Decisions made by the human

From before this session (issue comments): the 8-hour token lifetime; seed passwords from environment variables; `get_session` stays in #13; login attempt limiting is out of scope. Pending: approval of the staged `AGENTS.md` diff.

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (PASS with one warning: `tests/conftest.py` fixtures changed, as the issue requires)
- **Contract check:** `make contract-check` (`openapi.yaml: OK`)
- **Test (one file):** `make test-one FILE=tests/test_auth_api.py`

## Proposed AGENTS.md changes

1. Run line: "the backend needs `SOCBOARD_TOKEN_SECRET`, at least 32 characters, or exits 2" (staged; needs the human's approval).
2. Seed line: name the three users and the three password variables (proposal only; outside the issue's approved scope). The exact text is in the Engineer comment.

## Temporary changes

none. No server started, no system change, no install. Probe scripts in `.scratch/` (scrypt timing, route listing, surrogate login, dummy-hash generation, the comment file) are left for `make clean-scratch`.

## Interruptions

none

## Unrelated problems noticed but not fixed

- The `Makefile` `seed` help text describes only the asset inventory (the issue keeps `Makefile` untouched).

## Follow-ups for the next session

- The human approves or declines the staged `AGENTS.md` diff, and decides on the Seed-line proposal.
- First QA launch, then the second, independent QA launch (Heavy).

## Addendum: upper bound on `exp` (2026-11-12)

- **Why:** the first QA launch (PASS at `c11a755`) found that `read_token` accepted a correctly signed token with a 500-digit `exp`, so the 8-hour lifetime held only when a token was made. The human approved fixing it in #13 in this session.
- **Change:** `socboard/tokens.py` `read_token` now also refuses a token whose `exp` is greater than `math.floor(now) + TOKEN_LIFETIME_SECONDS` (integers only, so a huge `exp` never overflows). The "at or past `exp`" check is unchanged; `socboard/auth.py` is unchanged, so the refusal is the same 401 `unauthorized` with `WWW-Authenticate: Bearer`. The decision record's "As built" lifetime line says so.
- **Tests:** `tests/test_auth_tokens.py` (exactly the lifetime ahead accepted, one second more refused, with an integer and a float `now`; `10**500` and `-(10**500)` refused without raising); `tests/test_auth_api.py` (both huge values refused with 401 through the real app; lifetime + 60 s refused and exactly the lifetime accepted, built when the test runs). No existing assertion changed.
- **Verify:** `make verify BASE=1fe0300`: PASS with warnings; 183 assertion lines added, 2 removed (the two `seed.main` calls that now pass the seed passwords, from the earlier #13 commits), and `tests/conftest.py` fixtures changed as the issue requires. The earlier Engineer comment's figures (218 added, 0 removed) were measured from `origin/main`, not from `1fe0300`.
- **Choice:** the API refusal test uses lifetime + 60 s rather than + 1 s, so a slow clock tick between building the token and the request cannot make it pass by accident; the + 1 s edge is covered in the unit test with a fixed `now`.

## Addendum: orchestrator (2026-11-12)

- **QA:** first launch PASS at `c11a755`, re-check of the `exp` fix PASS at `c67e613`, second independent launch PASS at `c67e613` under the human-approved stopping rule (Medium or higher fails; eight Low findings). Assert clean passed after each.
- **Second launch as a subagent:** the human ruled that the second launch for #13 runs as a fresh `qa-engineer` subagent from the orchestrator session rather than a new Claude Code session (https://github.com/andrew-chung-au/socboard/issues/13#issuecomment-6839289641). A data point for sweep 4, item 1.
- **Protected files:** the human approved both `AGENTS.md` commits (`c8e85bd`, and `c11a755` beyond the issue's scope). The orchestrator did not record the second approval on the issue when it committed it; the second QA launch caught this (F8), and the record was posted afterwards (https://github.com/andrew-chung-au/socboard/issues/13#issuecomment-6839478237).
- **Merge attribution:** the orchestrator's two merges of `origin/main` into `main` (`bc6668f` and `1fe0300`, during #12) used `git merge --no-edit`, so they lack the `Assisted-by: Claude Code` line. They were not rewritten, because later commits sit on top; future merges pass `-m` with the line.
- **Decision point:** the human accepted the Engineer's uncovered choices and approved three follow-up issues (filed by the PM): unparseable bodies give 500 instead of 422 (before #14), a deleted user's id can be reused (low), and one low-priority issue for the smaller items. A sweep is due (`make sweep-due`: 9 closed since 2026-11-12); it runs after #13 closes and before #14.
