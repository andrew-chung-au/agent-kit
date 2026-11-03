# Proposal: `make demo` (protected files; needs the human's approval)

Status: **approved by the human and applied, 2026-10-25.** The human approved this diff in the session ("approve make demo"). Applied as two separate `HUMAN_APPROVED=1` commits: `Makefile` `7beafd9` and the `AGENTS.md` line `936ca53`. Tested before the commit: `make demo-reset`, then `make demo` from an empty database registered 4 assets and produced 2 findings (P1 `urllib3` CVE-2023-43804, P2 `pyyaml` CVE-2020-14343). There is no issue for this change, so the protected-change approval record lives here and in the session summary; if you want one on a GitHub issue, say so and I will file it.

(The text below is the proposal as approved; the "not applied" wording in the Approval section is superseded by this status.)

## Why

A peer reviewer clones the repo and has an empty app. The README's local demo is five commands. One target would make it `make demo`, which is easier to get right. The recipe was run from an empty database on 2026-10-25 and produced 4 assets and 2 findings (P1 `urllib3` CVE-2023-43804, P2 `pyyaml` CVE-2020-14343); this target is that recipe in one place.

## Makefile (append after `dev-stop`)

```make
# --- Local reviewer demo ----------------------------------------------------
# One command: migrate, create a demo security lead, start the app on the
# recorded fixtures (no Docker, no network) and register four demo repositories
# through the API. The demo password is public by design and works only on this
# local database. VT_FEEDS=fixtures is refused unless DEPLOYMENT_ENVIRONMENT is
# dev or test, so it cannot run in production.
DEMO_USER = lead
DEMO_PASSWORD = demo-password-local

demo: dev-migrate ## Start the app on recorded fixtures with a demo login and four demo repositories (local, no Docker, no network)
	@printf '%s\n' '$(DEMO_PASSWORD)' | uv run --directory backend python -m vulntriage.manage create-user --username $(DEMO_USER) --display-name "Security Lead" --email lead@example.com --role "security lead" || echo "note: the demo user was not created (it may already exist)"
	@$(MAKE) dev-start VT_FEEDS=fixtures DEPLOYMENT_ENVIRONMENT=dev
	@VT_SEED_PASSWORD='$(DEMO_PASSWORD)' python3 deploy/seed-pilot.py --base-url http://127.0.0.1:8000 --username $(DEMO_USER) --seed-file deploy/demo-seed.json --wait 60
	@echo "Open http://127.0.0.1:5173 and sign in as $(DEMO_USER) / $(DEMO_PASSWORD). Stop with: make dev-stop"

demo-reset: ## Stop the app and delete the local dev database, so make demo starts clean
	@$(MAKE) dev-stop
	@rm -f backend/.scratch/vulntriage.db
	@echo "dev database removed"

.PHONY: demo demo-reset
```

Add `demo demo-reset` to the existing `.PHONY` list if you prefer a single list.

Known limits, so the diff is not oversold:

- The `|| echo` after `create-user` means a second `make demo` carries on when the user already exists, but it also hides any other `create-user` failure. A re-run registers the four assets again, so run `make demo-reset` first for a clean demo.
- It uses `python3` for the seed script (stdlib only, no new dependency), so `python3` must be on the PATH.
- `demo-reset` deletes `backend/.scratch/vulntriage.db`, the default dev database; it does nothing to a `DATABASE_URL` pointing elsewhere.

## AGENTS.md (Commands list, one line after "Dev (all)")

```
- **Demo:** `make demo`: migrates, creates a demo security lead, starts the backend and frontend on the recorded fixtures (`VT_FEEDS=fixtures`, no Docker, no network) and registers four demo repositories; sign in as `lead` / `demo-password-local` at `127.0.0.1:5173`. `make demo-reset` stops the app and deletes the dev database. Details: the README's "Try it as a reviewer".
```

## Approval

Per `AGENTS.md`: commit with `HUMAN_APPROVED=1` as its own commit after you approve this diff in a session, then post the approval record on the issue. There is no issue yet; I would file one only with your say-so.
