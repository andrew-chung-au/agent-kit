# Check in a browser that `make run` serves the frontend with the mock off

> Written 2026-11-14T04:00Z by the orchestrator for #22. The repository is public: no secrets here. Choose the secret, the passwords and the key yourself, use throwaway values, and keep them out of the issue.

## Purpose

Check the last open acceptance criterion of #22 by hand, because it is a visual check: after `make run`, http://127.0.0.1:5173/ shows the Sign in page without the "Mock mode" box and, after sign-in as `lead`, no `mock` badge in the top bar. Issue: #22. Everything else in #22 passed QA at `2ade537`.

## Where to run it

A clean clone (or the dev container) on branch `claude/blissful-wright-vg0ycj`, with Python, uv, bun and make installed, and a browser that can open http://127.0.0.1:5173/ (forward ports 5173 and 8000 in a dev container). Run every command from the repository root, in ONE terminal: the `export` lines last only for that shell. About 5 minutes.

Do not set `SOCBOARD_PORT` (`make run` accepts only 8000, the frontend proxy's target) and do not export `VITE_USE_MOCK` (`make run` sets it to `false` itself).

## Before you start

1. Nothing of this checkout's stack is running and ports 8000 and 5173 are free.

```
make stop
```

Expected: it says the frontend and the backend are not running (or stops them), and exits 0.

## Steps

### Step 1: get the branch and install

```
git fetch origin claude/blissful-wright-vg0ycj
```

```
git switch claude/blissful-wright-vg0ycj
```

```
make install
```

Expected: the branch is checked out and `make install` ends without an error line.
If different: stop and tell the orchestrator what was printed.

### Step 2: set the five required variables (this shell only)

Pick your own values: the secret needs at least 32 characters (not counting leading and trailing spaces), each seed password at least 12, the ingest key at least 16.

```
export SOCBOARD_TOKEN_SECRET='<a secret of at least 32 characters>'
export SOCBOARD_SEED_PASSWORD_ANALYST_A='<12 or more characters>'
export SOCBOARD_SEED_PASSWORD_ANALYST_B='<12 or more characters>'
export SOCBOARD_SEED_PASSWORD_LEAD='<12 or more characters>'
export SOCBOARD_INGEST_API_KEY='<16 or more characters>'
```

Expected: no output. Remember the `lead` password. `make seed` never changes an existing user: if `socboard.db` (git-ignored) already exists from earlier work, `lead` keeps the password it had then. For a clean start, remove it first: `rm -f socboard.db`.

### Step 3: start the stack

```
make run
```

Expected: the migrate and seed lines, `backend started ...`, `frontend started ...`, then the two lines `run: backend  http://127.0.0.1:8000/ ...` and `run: frontend http://127.0.0.1:5173/ (mock off; ...)`, and `run: make stop stops both`. Exit status 0.
If different: if it names a variable, that variable is missing or too short (nothing was started): fix it and run again. Otherwise stop and tell the orchestrator what was printed (no values).

### Step 4: the Sign in page (browser)

Open http://127.0.0.1:5173/.

Expected: the Sign in page with NO "Mock mode" box (the box that lists test accounts).
If different: stop, run `make stop`, and tell the orchestrator.

### Step 5: sign in as `lead` (browser)

Sign in as `lead` with the password you chose for `SOCBOARD_SEED_PASSWORD_LEAD`.

Expected: you are signed in, and the top bar shows NO `mock` badge.
If different: stop, run `make stop`, and tell the orchestrator.

### Step 6: stop the stack

```
make stop
```

Expected: `frontend stopped`, then `backend stopped`, exit status 0. Optional: `rm -f socboard.db` to drop the test data.

## Record the result

Write pass or fail for each step on #22 (or tell the orchestrator in the session). Do NOT paste passwords, the secret, the key or any token.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 branch, install | pass | `make install`: no changes, no error line |
| 3 `make run` exit 0, both URLs printed | pass | migrate at latest; seed `0 user(s) added, 3 already present` (an existing database, so `lead` kept its earlier password); backend and frontend started; both URLs printed |
| 4 no "Mock mode" box on Sign in | pass | reported by the human |
| 5 signed in as `lead`, no `mock` badge | pass | reported by the human |
| 6 `make stop` stopped both | pass | `frontend stopped`, `backend stopped`; the human then removed `socboard.db` |

Run by the human on 2026-11-14 in the dev container on branch `claude/blissful-wright-vg0ycj` (`bc7d6ba`). Note for next time: the Step 2 placeholders were exported literally; they pass the length checks but are public text, so the step should say plainly to replace them.

## Risk

Two local servers run from Step 3 until Step 6. `socboard.db` (git-ignored) holds the seeded users. Nothing is pushed.
