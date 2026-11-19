# Deploy wave 1: full issue drafts (D1 to D5)

Companion to `_docs/planning/deploy-backlog-proposal.md`. **Drafts only: nothing is filed, and none of these is approved.** They assume the proposal's recommendations on its questions 1 to 5 (trigger functions for the Postgres audit rule, in-process rate limits, frontend settings as build arguments, lanes A and C in parallel, D2 Heavy). If the human answers differently, the affected bodies change before filing; each says which question it depends on.

Wave 1 is the work that can start now whichever way #22 and #104 land: the decision record, serving the build, deployed-mode configuration, the container bind rule, and Postgres support. Each body is in the layout the existing issues use (Why, Goal, Acceptance criteria, Out of scope, Design, Constraints). The first line of each block is the title, as `make issue-create` expects (`Title: <text>`, blank line, body). Facts below were read from `main` at `5d0ffa6`.

---

## D1

Title: Record the Deploy decisions (Terraform on AWS, Postgres audit rule, rate limits)

## Why

`_docs/planning/roadmap-3-deploy.md` records seven decisions the human made on 2026-11-12, but no decision record exists in `_docs/decisions/`, so no Deploy issue can cite one. Two further decisions are needed before the Heavy issues that depend on them: how Postgres keeps the audit trail append-only (D6) and how login and ingest limits are counted (D8, D9). Deploy issues are filed against this record.

## Goal

One approved decision record in `_docs/decisions/` states the nine decisions below with reasons, alternatives and trade-offs, and `make decisions` lists it as approved.

## Acceptance criteria
- [ ] A new record `_docs/decisions/<timestamp>-deploy.md` follows the layout of the existing records (Status, Decision, Reason, Alternatives, Trade-offs, Evidence). Its status is `proposed` until the human approves it, then `approved`; `make decisions` shows the word.
- [ ] It records the seven decisions of 2026-11-12 as the roadmap states them: Terraform on AWS with one environment and one server; CI may run `fmt`, `validate` and a read-only `plan`, and `apply` only for the server part, only on `main`, in an `infra` Environment with a named reviewer and administrators not exempt; the container binds a non-loopback address only through an explicit opt-in while `make backend-run` stays loopback-only; Postgres runs as a container beside the app on an encrypted volume with daily snapshots; secrets live in one Secrets Manager secret; the URL is a wildcard-DNS hostname with Caddy certificates; no stop schedule, budget notifications at three thresholds.
- [ ] It records the Postgres audit decision (proposal question 1): the database refuses UPDATE, DELETE and overwrite of `audit_entries` rows by trigger functions in the migration; a role without those rights is recorded as a Phase 3 hardening; the record states what the database owner can still do.
- [ ] It records the limit decision (proposal question 2): login and ingest limits are counted in the process, reset on restart, and are not shared between replicas; the record names the defaults' owner (the D8 and D9 issues) and states this as a known limit.
- [ ] It records the region (human, 2026-11-13): the deployment runs in `us-east-1`. It is the human's own AWS account, whose home region is `ap-southeast-2`; the human has used `us-east-1` before. It says which resources follow the region: every regional resource (server, volume, snapshots, Secrets Manager secret, the Terraform state bucket unless the human picks otherwise) is in `us-east-1`; IAM, the GitHub OIDC provider and roles are global; budget notifications are account-wide. It tells the Terraform and the operator to name `us-east-1` explicitly, never rely on a default region setting.
- [ ] It lists the accepted risks (single server, no high availability, Postgres on the same host, a public URL on a shared wildcard-DNS name, and that reviewers in Australia reach a US-east server, which adds latency but not a correctness risk against the 5 second target; the smoke check measures it).
- [ ] It records the amendment to the 2026-11-12 decision on the CI-applied "server part" (human, 2026-11-13): the instance role and profile, any role the snapshot schedule needs (`VERIFY:`), and the budgets are applied only by the human, together with the CI-access part. The CI apply role may only attach that one role to the instance and has a deny on other IAM writes (exact permission unverified until the first apply). The cost is stated: any later change to the instance's permissions is a manual apply.
- [ ] It pins one Postgres major version, used in the dev container, the CI service and the Compose stack.
- [ ] It states what Terraform state, GitHub secrets and the image must never hold (no long-lived cloud key, no seeded password, no ingest key, no token secret, no database password in state outputs), matching spec §5.
- [ ] `_docs/index.md` lists the record.
- [ ] `make verify` passes.

## Out of scope
- Any code, Terraform or workflow change.
- Choosing the rate-limit numbers (D8 and D9 choose defaults).
- DevOps-phase decisions (dev and prod environments, observability, the on-call agent).

## Design

None.

## Constraints
- Files: one new file under `_docs/decisions/`, and `_docs/index.md`. Nothing protected.
- Sources: `_docs/planning/roadmap-3-deploy.md` (decisions), `_docs/specs.md` §5 to §7, `_docs/decisions/2026-11-12T0834Z-data-model.md` (what the audit rule protects today), `_docs/planning/deploy-draft/readiness-and-questions.md` (the options and recommendations).
- The human approves the record before D5 to D9 are groomed against it.
- Proposed tier: heavy (it fixes the rules the whole phase follows). Expected paths: `_docs/decisions/<new record>.md`, `_docs/index.md`.

---

## D2

Title: Serve the built frontend from the FastAPI app

## Why

The spec's Deploy stories require one container image that serves the web app at `/` and the API under `/api` from one origin, with a screen route such as `/cases/1` returning the web app's entry page and an unmatched `/api` path returning the JSON 404. Today the backend serves no static files (`socboard/app.py` includes only the health, login, ingest, users and cases routers), and the README says the `/api` proxy is for the dev server only. #22 deliberately did not do this (the human chose the Vite dev server for `make run`, 2026-11-13). The built site is produced by `make frontend-build` into `frontend/dist`.

## Goal

When `frontend/dist` is present, the app serves the built site and falls back to its entry page for screen routes; every `/api` behaviour is unchanged.

## Acceptance criteria
- [ ] With a `dist` folder (the test builds a small one in a temporary folder with `index.html` and one asset): `GET /` returns `index.html`; `GET /cases/1` returns `index.html` with status 200; an asset path returns that file with its content type.
- [ ] A request under `/api` that matches no route returns the existing JSON 404 `not_found` with the contract's `ApiError` body, never the entry page. A wrong method on an existing `/api` route still gets the existing 405. One test for each.
- [ ] No `/api` route changes status, body or order of checks: the existing contract and order tests pass unchanged, and `create_app().openapi()` is identical to before (the comparison test passes).
- [ ] Traversal is refused: requests such as `/..%2f..%2fsocboard.db`, `/%2e%2e/pyproject.toml` and an absolute path return the entry page or 404, never a file outside `dist`. A test for each.
- [ ] A missing path that looks like a file (its last segment has an extension, for example `/assets/missing.js`) returns 404, not the entry page; only extension-less screen routes fall back to the entry page (a test for each).
- [ ] Without a `dist` folder the app starts and behaves exactly as before (`make backend-run` is unchanged and `GET /` is the existing 404); the folder is read from a setting with a documented default, and a missing folder is not an error.
- [ ] The site is served without interpreting alert text and adds no cookie; response headers for the entry page and assets are listed in the issue comment (the Engineer chooses cache headers and says why).
- [ ] `make verify` passes; no test is weakened or deleted.

## Out of scope
- The Dockerfile, Compose and Caddy (D10, D11, D17c).
- Any change to `openapi.yaml` or to the frontend.
- Server-side rendering, and serving the Vite dev server (the dev proxy stays as is).

## Design

None to decide here, except the rule that the fallback is registered after every API router so it can never shadow one. The Engineer proposes the mechanism (a static-files mount plus a fallback route, or a small catch-all) in the issue comment before implementing, since this adds a public interface.

## Constraints
- Files: `socboard/app.py` and, if needed, one new module under `socboard/`; `tests/` (a new test file); `README.md`. Nothing protected.
- No new dependency if the framework's static-file support can do it. If a dependency is needed, ask first.
- Guardrails from `_docs/planning/lovable-guidance.md` and `AGENTS.md` stay: alert text is never treated as instructions.
- Depends on: #21 (closed). The built output is checked by `make frontend-build`.
- Proposed tier: heavy (a new public interface on the app that fronts the audit and case data; proposal question 5). Expected paths: `socboard/app.py`, one new `socboard/` module, `tests/test_spa_serving.py`, `README.md`.

---

## D3

Title: Read all runtime settings from one list and refuse a missing or weak secret in deployed mode

## Why

Runtime settings are read in separate places: the token secret (`socboard/auth.py`, at least 32 characters, no default), the ingest key (`socboard/ingest.py`, at least 16 characters; if unset or short the app starts, logs one warning and closes ingest), the database URL (`socboard/database.py`), the three seed passwords (`socboard/seed.py`, at least 12 characters, checked only when seeding), and host and port (`socboard/server.py`). Spec §5 says that in deployed mode a missing secret stops the app at start-up. Today a missing ingest key does not, so a public deployment could start with ingest silently closed, and a blank-looking secret (32 spaces) is accepted (#104, item 5). #22 adds a `make run` preflight with its own list of five names; the cloud secret, the Compose env file and the README need the same names.

## Goal

A single list names every runtime variable, deployed mode refuses to start with any required secret missing or unusable, and the names appear in one place that the README, the Compose file and the cloud secret copy from.

## Acceptance criteria
- [ ] One module lists each runtime variable: its name, whether it is a secret, whether deployed mode requires it, and its minimum rule. The list is the source for the README's variable table; a test fails if a name in the list is missing from `README.md` or a documented name is not in the list. If #22 has landed, its preflight list is reused, not copied.
- [ ] A single explicit setting turns on deployed mode (the Engineer proposes its name in the issue comment; it defaults to off, so `make run`, tests and `make backend-run` behave as before).
- [ ] In deployed mode, a missing, empty or too-short value for each of: the token secret, the ingest key and the database URL stops the app at start-up, exit code 2, with a message that names the variable and never prints its value. One test per variable. The three seed passwords are required by the one-shot seed step only (the app never reads them); `make seed` already refuses a missing or short one.
- [ ] A secret that is only whitespace, or one repeated character, is refused in every mode for the token secret and in deployed mode for the others (#104 item 5). The rule is stated in the README. A test covers 32 spaces and 32 of one character.
- [ ] Outside deployed mode nothing changes: the ingest key stays optional with its single warning, and the existing tests pass unchanged.
- [ ] No value appears in a log line, error message or the README. A test sets distinctive values and fails if any is found in captured output.
- [ ] A `.env.example` lists names only, with the rule for each; `.gitignore` already allows it. Settings that are fixed when the frontend is built (`VITE_API_BASE_URL`, `VITE_FEATURE_REASSIGN`, `VITE_POLL_INTERVAL_MS`, `VITE_USE_MOCK`) are listed in the README as build arguments, not runtime variables.
- [ ] `make verify` passes.

## Out of scope
- Reading secrets from Secrets Manager (the deploy script does that, D20).
- The Compose file and Dockerfile (D10, D11).
- Login and ingest limits (D8, D9), which read their own settings through this list once it exists.
- #104 items 1 to 4.

## Design

The Engineer proposes the module name and the deployed-mode variable in the issue comment; the human confirms them before the code is written, because they become part of the operator's contract.

## Constraints
- Files: `socboard/` (the settings module, `app.py`, `server.py`, `auth.py`, `ingest.py`, `seed.py` only where they read a setting), `tests/`, `README.md`, `.env.example`. `AGENTS.md` and `Makefile` are not edited here (protected); anything they need is listed in the comment for a later sitting.
- Never open or print a real env file (the kind that holds values); the example env file holds names only.
- Depends on: #104 (it may change what `make seed` requires) and #22's preflight list, if #22 has landed; otherwise this issue defines the list and #22 reads it.
- Proposed tier: standard (no new boundary, but it changes start-up for every deployment). Expected paths: `socboard/settings.py` (or similar), `socboard/app.py`, `socboard/server.py`, `socboard/auth.py`, `socboard/ingest.py`, `socboard/seed.py`, `tests/test_settings.py`, `README.md`, `.env.example`.

---

## D4

Title: Let the container image bind a non-loopback address through an explicit opt-in

## Why

`socboard/server.py` refuses any host except `127.0.0.1`, `localhost` and `::1`, and `AGENTS.md` documents `make backend-run` as loopback-only. Inside a container, the app must listen on an address Caddy and Docker can reach, or nothing can connect. The human decided (2026-11-12) that `make backend-run` stays loopback-only and only the image opts in, with the app port published on the host's loopback behind Caddy.

## Goal

The server binds a non-loopback address only when an explicit opt-in is set, which only the image sets; with no opt-in, the loopback rule and its refusal are exactly as before.

## Acceptance criteria
- [ ] With no opt-in, `SOCBOARD_HOST=0.0.0.0` (and `::`, and a real interface address) still exits 2 with the existing message, and the existing server tests pass unchanged.
- [ ] The opt-in is a command-line flag of `python -m socboard.server`, not an environment variable. With the flag, `SOCBOARD_HOST=0.0.0.0` is accepted by `resolve_bind`; a value that is not an address (a name, an empty string, whitespace, a URL) is still refused. A test for each.
- [ ] The flag is off by default and takes no value. No environment variable can enable it: `SOCBOARD_HOST=0.0.0.0` without the flag exits 2 even with every `SOCBOARD_*` variable set (a test). `make backend-run` and `scripts/backend_probe.py` read the inherited environment, so they stay loopback-only with no Makefile change; the Engineer reads the recipe and the probe in the issue comment to show it.
- [ ] The refusal message names the setting to change, but not any value, and the server prints no secret.
- [ ] The README states who may set the opt-in (the image only) and why.
- [ ] `make verify` passes.

## Out of scope
- The Dockerfile that sets the opt-in (D10) and Compose's loopback port publishing (D11).
- Changing the default host or port.

## Design

None.

## Constraints
- Files: `socboard/server.py`, `tests/test_backend_server.py`, `README.md`. `scripts/backend_probe.py` is read, not changed. `AGENTS.md` holds the rule that `make backend-run` is loopback-only; if its wording needs a change, list the exact diff in the comment for the human (protected).
- Depends on: #80 (closed), which hardened `backend-run` and `backend-stop`.
- Proposed tier: heavy (it relaxes a security limit). Expected paths: `socboard/server.py`, `tests/test_backend_server.py`, `README.md`, possibly `AGENTS.md`.

---

## D5

Title: Run the backend and migrations on Postgres, chosen by the database URL (driver, schema, CI job)

## Why

The spec says the database is chosen by environment variable: SQLite locally, Postgres when deployed. `socboard/database.py` already branches on the dialect for the engine, but nothing else is ready: `pyproject.toml` has no Postgres driver; migration `0001` creates the audit triggers in SQLite syntax and sets `sqlite_autoincrement` on `audit_entries`; `socboard/migrate.py` already branches by dialect (it switches the SQLite foreign-key pragma off and checks it afterwards only on SQLite), but the test fixtures assume a SQLite file (the `template_database` fixture copies a migrated SQLite file per test). The append-only rule itself is D6 and is not in this issue; this issue gets everything else to run, and keeps the rest of the schema identical.

## Goal

With `SOCBOARD_DATABASE_URL` set to a Postgres URL, `make migrate` and `make seed` succeed, the backend starts and answers health and login, and CI runs those steps against a Postgres service; SQLite stays the default and its behaviour is unchanged. Making the whole test suite run on Postgres is D5b, a separate issue.

## Acceptance criteria
- [ ] The Postgres driver is added with `uv add` after the human's approval (the dependency is the first step; `pyproject.toml` and `uv.lock` are committed).
- [ ] Migration `0001` runs on Postgres and creates the same tables, columns, constraints and indexes as on SQLite. The SQLite-only parts (the three triggers, `sqlite_autoincrement`) are guarded by the dialect, so the SQLite result is byte-identical to today (the existing migration tests pass unchanged). On Postgres, `audit_entries` ids are 64-bit and ascending; the append-only rule is not added here (D6) and the issue comment says so.
- [ ] `make migrate` twice changes nothing on Postgres; `make seed` inserts only missing rows and a second run changes nothing.
- [ ] Time values keep their meaning: a stored timestamp reads back as an aware UTC datetime on Postgres as on SQLite (`socboard/db_types.py` is checked, with a round-trip test on both).
- [ ] Ordering is the same: the queue and closed list order rows alike on both databases (the code comments say NULLs are ordered explicitly; a test with a NULL-bearing case shows it on Postgres).
- [ ] The default run (no Postgres URL) is unchanged and still passes without Postgres: the push check has no database service.
- [ ] CI starts a Postgres service container (the major version pinned in D1) as a second job alongside `make verify` and runs `make migrate`, `make seed`, and a start, health and login smoke against it. CI's result is the evidence of record; if the dev-container database (D0) exists, the Engineer uses it for iteration.
- [ ] `make verify` passes; no test is weakened or deleted. The pull request's CI run (id and log lines in the comment) is the evidence.

## Out of scope
- The Postgres append-only rule for the audit trail, and review of `socboard/audit_guard.py` (D6a and D6b).
- The concurrency test for claims (D7).
- The fixtures across the test files, the SQLite-only test markers and the NUL-in-text check on Postgres (D5b).
- Mapping a lock timeout to a retryable response (#112).
- Docker, Compose and Terraform.

## Design

None here. How Postgres test isolation works is D5b's design question.

## Constraints
- Files: `pyproject.toml` and `uv.lock` (protected: the human approves the exact diff and commits with `HUMAN_APPROVED=1`), `socboard/migrations/versions/0001_initial_schema.py` (only guards, no change to its SQLite output), `socboard/migrate.py`, `socboard/database.py`, `socboard/db_types.py` if needed, `tests/conftest.py`, `tests/data_support.py`, the migration and engine tests, `.github/workflows/verify.yml` (protected: the human approves the diff), and `README.md`.
- An existing migration is edited here only to branch on the dialect; its SQLite behaviour must not change. If an edit to `0001` is judged unsafe, add migration `0002` instead and say why in the comment.
- Ask before installing anything large.
- Depends on: #104 (it touches `seed.py` and the missing-database behaviour), D1 (approved record, which pins the Postgres version), #100 (the CI job should run the pinned Python), and D0, the dev-container sitting (done between issues).
- Proposed tier: heavy (it changes the data layer and the migration that every database starts from). Expected paths: as listed above.

---

## What these five leave for later (D5 above is D5a)

D5b (Postgres test fixtures) follows D5a. D6a (Postgres append-only triggers and tests) starts when D5a and D5b are merged and D1 is approved; D6b (guard review) waits for #107. D8 and D9 start after D3. D10 starts after D2, D3 and D4. The full list and the order are in `_docs/planning/deploy-backlog-proposal.md`.
