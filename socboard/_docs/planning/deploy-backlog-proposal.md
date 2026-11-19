# Deploy phase: backlog proposal (draft, for the human's approval)

**Human ruling, 2026-11-13:** the recommendations in section 6 (questions 1 to 5) are approved: trigger functions for the Postgres audit rule, in-process login and ingest limits, frontend settings as build arguments, lanes A and C may run in parallel, D2 is Heavy. Region: the deployment runs in `us-east-1`; it is the human's own AWS account (home region `ap-southeast-2`) and the human has used `us-east-1` before, so no organisation policy is expected to block it. Wave 1 is filed from this list: D1 is #139, D2 is #140, D3 is #141, D4 is #142, D5 is #143 (no label added; the human approves each after grooming); D6 onward is written in full after wave 1 is under way. Questions 6 to 8 are approved with conditions (section 6). Spec notes A and B (section 7) are read as approved; `_docs/specs.md` is protected, so the exact diff is for the human to commit.

PM-style proposal. **No issue is filed and no roadmap, spec or decision file is changed by this document.** It reviews `roadmap-3-deploy.md` against `main` at `5d0ffa6` (Core #7 to #21 closed; #22 re-groomed but its new body not yet confirmed), proposes changes to that roadmap, drafts the issues, and states what #22 means for them. Issue bodies are written in full only after the human approves the list and answers the questions in section 6. Numbers are `D1` to `D23` until the tracker gives them real ones.

## 1. Definition of ready (`procedures/planning.md#definition-of-ready`)

The draft of 2026-11-12 (`deploy-draft/readiness-and-questions.md`) said NOT READY. The spec changes it asked for are now in `_docs/specs.md` (commit 185bb50). Item by item:

| Item | Where | Ready? |
|---|---|---|
| Problem and core assumption | spec §1 (unchanged) | Yes |
| Named users | spec §2: Operator and Visitor added | Yes |
| At least one end-to-end journey | spec §3 journey 3, "Deploy to Public URL" | Yes |
| Requirements acceptance criteria can come from | spec §4 "Deploy (Phase 2)": ten Must stories, including login and ingest limiting | Yes |
| Explicit scope boundary | spec §6 Phase 2: one environment, one server, one Postgres, AWS, Terraform | Yes |
| Non-goals (not an empty heading) | spec §7, with Deploy non-goals | Yes |
| Listed invariants | spec §5, including secrets, one owner on both databases, no long-lived cloud key | Yes, with one gap (spec note A) |

This is the PM's reading; the confirmation that counts is the PM's in the backlog-proposal comment, which the human reads before approving.

## 2. Review of `roadmap-3-deploy.md`: what is still right and what must change

Still right: the seven human decisions (2026-11-12), the one-image design, Caddy for TLS, SSM instead of SSH, OIDC with separate roles, human-only first apply, the Core-then-Deploy order, and the two-lane shape (app work and Terraform do not share files).

Must change before issues are filed:

1. **Roadmap task 4 ("Run on Postgres") is several issues, not one.**
   - The audit trail's append-only rule is three SQLite triggers (`RAISE(ABORT, ...)`) in migration `0001`; Postgres needs different trigger code. Spec §5 says the trail is append-only on any supported database.
   - `audit_entries` uses `sqlite_autoincrement`; `socboard/audit_guard.py` is written around SQLite names (`sqlite_sequence`, PRAGMAs, the SQLite dialect for its compile step).
   - `pyproject.toml` has no Postgres driver, and every test file runs on SQLite.
   - Proposed split: D5 (driver, portable migration, Postgres in CI, tests choose the database by URL) and D6 (append-only on Postgres; Heavy, security boundary, updates `_docs/decisions/2026-11-12T0834Z-data-model.md`). Roadmap task 5 (single ownership on Postgres) becomes D7.
2. **Two Must stories have no task: login attempt limiting and ingest rate limiting** (spec §4). The roadmap says no Deploy story exists for them; it does now. They are D8 and D9.
3. **Roadmap task 3 (configuration) is incomplete.**
   - It omits `SOCBOARD_TOKEN_SECRET` (the backend exits 2 without it), so it must be in the cloud secret and the Compose env file. Spec §5 lists the secrets without it (spec note A).
   - It lists "poll interval" as a runtime variable. It is `VITE_POLL_INTERVAL_MS`, fixed when the frontend is built (so are `VITE_USE_MOCK` and `VITE_FEATURE_REASSIGN`). In a one-image design they are build arguments, or the spec line "configurable via env var" must say "at build" (spec note B).
   - Fold in #104 item 5 (a 32-space secret is accepted): a public deployment should refuse a blank-looking secret.
4. **Task 7 (image) needs #100** (pin Python 3.12). The base image and CI must agree, and CI ran 3.14.
5. **Image build feedback comes too late.** The sandbox runs no Docker, so CI is the only place the image is built until the human runs it. Put a `docker build` job in CI with the Dockerfile issue (D10), not with roadmap task 11.
6. **`AGENTS.md` Layout lines** for `Dockerfile`, `docker-compose.yaml`, `terraform/` and `e2e/` are protected edits. Batch them with the Makefile approvals each issue already needs.
7. **The decision record (roadmap task 1) does not exist** in `_docs/decisions/`. It is D1, and it should also record the two new decisions in section 6 (Postgres audit approach, rate-limit design) so Heavy issues D6 and D8 have an approved record to cite.

Not changed: the Terraform tasks, the deploy script, the smoke check, CD and the runbook keep their roadmap content (renumbered D15 to D23). AWS-specific details stay marked `VERIFY:` until the human's first apply.

## 3. What #22 means for Deploy

**Short answer: it blocks little, and it should be given two small changes before its new body is confirmed.**

What the human has already decided for #22 (comment of 2026-11-13, "human decisions for the #22 re-groom"): `make run` is the Vite dev server with the mock off and `/api` proxied (option A), started in the background with pid files, `make stop` stops only what it started, `SOCBOARD_INGEST_API_KEY` is required, and the order is #120 (now closed), #114, #104, then #22. Option C (the backend serves the built frontend) was not chosen, so **#22 does not do D2**. `make run` stays a dev-mode command on SQLite, loopback only. It is not the deployed shape.

| Deploy item | Needs #22? | Why |
|---|---|---|
| D1 to D11, D15 to D19 | No | Different files (`socboard/`, `terraform/`, Dockerfile). They can start now. |
| D12 (integration tests against Compose), D13 (E2E) | Yes | They reuse #22's journeys and schema check. |
| D11 (Compose), D20 (first deploy) | Yes, loosely | The one-shot migrate and seed step mirrors `make run`'s migrate, seed and preflight. |

Changes to ask for in #22's body before the human confirms it (it is not yet confirmed, so this costs nothing):

1. **Make the journey tests portable.** `tests/test_journeys.py` should take its client from one fixture that is in-process by default and can point at a live base URL when `SOCBOARD_BASE_URL` is set. Without that, D12 rewrites the journeys. The fixture is a few lines; the journeys must then avoid touching the database directly.
2. **Keep one list of environment variable names.** #22's `scripts/run_preflight.py` lists five required names, README repeats them, and D3, the Compose env file and the cloud secret will need the same list. Name the list once (the preflight's list is fine) and have the README test check it, as #22 already proposes. D3 reuses it.
3. **Say in the README that `make run` is the development command.** Name the Compose target differently (`make compose-up`, in D11) so the two cannot be confused.

Things that are fine as written: the schema check (`create_app().openapi()` against `openapi.yaml`, by method, path and `operationId`) is exactly what CI should keep running against the built image; the refusal tests and hostile-text tests carry over unchanged.

Effects of later Deploy work on #22's tests: login limiting (D8) can answer 429 to repeated wrong passwords in tests. The spec says limits are set by configuration, so the test settings raise them; D8 must provide that.

Related, not blocking: #104 (before #22, by the human's order) touches `make seed` and the `seed` help line; it also helps D11's one-shot seed step. #131 (frontend follow-ups from #21, after #22, before Deploy) includes the case-page action buttons; do it **before D13**, so the browser test does not pin a screen that is about to change. #110 changes what the `ingested` audit entry stores; D12 and D13 must not pin that text either.

## 4. Order and lanes

```
Human sitting:       D0 (dev-container Postgres) between issues, after D4, before D5a
Lane A (app):        D2  D3  D4 -> D0 -> D5a -> D5b -> D6a -> D7 -> D10 -> D11 -> D12 -> D13 -> D14
Guard review:        #107 -> D6b (before D20; run against the current guard if #107 is not approved when D6a merges)
Lane B (hardening):  D8, D9, #144 (after D3; touch auth.py and ingest.py)
Lane C (infra):      D1 -> D15 -> D18a (format and validate, as soon as D15 exists)
                     D1 -> D15 -> D17a -> D17b -> D17c (also needs D11)    D16 (after D15)
                     D16 + D17a + D17b + D17c -> D19 (human) -> D18b
Join:       D6a, D6b, D7, D8, D9, #144, D14, D17c, D19, D21 -> D20 -> D22a -> D22b -> D23 (also D24)
```

- Lane C touches `terraform/` only, apart from three shared files: the `AGENTS.md` Layout line (D15), and the workflows (D18a, D18b, D22a, D22b). Give each lane its own workflow file so they do not collide. Start D1 first because AWS account and budget setup depend on the human, and that has the longest wait.
- `delivery-pace.md` says never two Engineer launches on Core issues at once. Lanes A and C use disjoint files; the human decides whether to relax the rule for Deploy (question 4).
- Do D5a and D5b before D6a and D7. D5 and D8 and D9 do not overlap in files, except `socboard/auth.py` between D3, D8 and #104; serialize those.
- Human needed: D0 (the dev-container sitting), D1 (approve), D4 and D10 to D11 (protected files; one local Docker check), D15 to D17c (apply), D19, D20 (first run), D22a and D22b (variables, environment approval), D23 (teardown). Each issue still ends with the human's push; the dev-container database (D0) only speeds iteration within it.

## 5. Issue drafts

Full bodies for wave 1 (D1 to D5) are in `_docs/planning/deploy-draft/wave-1-issue-drafts.md` and are filed as #139 to #143. Full draft bodies for wave 2 (D6a, D6b, D8, D9, D10, D15, D16, D17a to D17c, D18a, D18b, D21, D24; not filed) are in `_docs/planning/deploy-draft/wave-2-issue-drafts.md`. D11 to D14, D19, D20, D22 and D23 stay outlines until #22 and the Terraform text exist.

Tier is proposed, not final. Model: **S** stronger, **M** middle, **W** weaker (suitability, as in the earlier plan). "Roadmap" is the old task number in `roadmap-3-deploy.md`.

### Lane A: the application

**D1 Record the deploy decision (Heavy, docs; roadmap 1).** Who: PM drafts, human approves. Model S.
- A record in `_docs/decisions/` holds the seven decisions of 2026-11-12 with reasons, the region (deployment `us-east-1`; the human's own account, home region `ap-southeast-2`), and the accepted risks, plus the two decisions of section 6 (Postgres audit approach, rate-limit design). Status line `approved` only after the human says so; `make decisions` lists it.
- It states what Terraform state and Secrets Manager hold and what they must never hold.
- It records the amendment to the 2026-11-12 decision on the CI-applied "server part" (question 6) and pins one Postgres major version for the dev container, the CI service and the Compose stack (question 7).

**D2 Serve the built frontend from FastAPI (Heavy: a new interface; roadmap 2).** Model M.
- Depends on: nothing open (#21 closed). `make frontend-build` output is the source.
- With `frontend/dist` present, `GET /` and a screen route such as `/cases/1` return the entry page; a path under `/api` that matches no route still returns the JSON 404 `not_found`, never the entry page (a test for each).
- Without `frontend/dist`, the app starts and every API route behaves as before; `make backend-run` is unchanged.
- No change to `openapi.yaml`, and the generated schema is the same (the existing comparison test passes).
- Static files cannot be used to read outside `dist` (a traversal test). A missing path that looks like a file (it has an extension) returns 404; only extension-less screen routes fall back to the entry page.

**D3 Deployed-mode configuration (Standard; roadmap 3).** Model M. Depends on: the variable list from #22, #104.
- One place lists every runtime variable (database URL, token secret, ingest key, three seed passwords, host and port); the README and a test read it.
- A single explicit setting turns on deployed mode (name chosen at grooming). In deployed mode a missing or blank token secret, ingest key or database URL stops app start-up with a message naming the variable, never its value, exit 2 (one test per variable). The three seed passwords are required by the one-shot seed step only, because the app never reads them.
- The token secret and the ingest key are refused when they are all spaces or too short (folds in #104 item 5).
- `.env.example` lists names only. Build-time settings (`VITE_*`) are documented as build arguments.

**D4 Let the container bind a non-loopback address, safely (Heavy: a security limit; roadmap 6).** Model M. Protected: `AGENTS.md` line.
- `make backend-run` still refuses any host except loopback (existing test stays).
- The opt-in is a command-line flag of `python -m socboard.server`, passed only by the image's start command; no environment variable can enable it. `make backend-run` and its probe (`scripts/backend_probe.py` reads the inherited environment) therefore stay loopback-only with no Makefile change. A test shows `SOCBOARD_HOST=0.0.0.0` without the flag exits 2 even with every `SOCBOARD_*` variable set.
- The refusal message and the `AGENTS.md` gotcha are updated to say who may opt in.

**D0 Dev-container Postgres service (a human sitting, not an Engineer issue; new).** Do it between issues, after D4 and before D5a, never during one.
- The human copies the recipe from `_docs/agent-kit/environments/local-sandbox/compose/` into `.devcontainer/` from a clean clone, as `environments.md` says; the agent does not. `.devcontainer/*` is protected, so the human approves the exact diff.
- One Postgres major version, chosen in D1, is used in the dev container, the CI service and the Compose stack (D11).
- The database password in the dev container is a throwaway and is never reused in the deployment.
- CI stays the evidence of record; the sandbox database is for iteration speed. The push check has no `db`, so the default test run must still pass without Postgres.
- It does not give the sandbox Docker, so D10 to D13 still need the human or CI.

**D5a Run on Postgres: driver and portable schema (Heavy: data model; roadmap 4, first part).** Model S. Depends on: D0, D1, #104, #100. **D5b Postgres test fixtures and CI job (Standard; split from D5 by the outside review).** Model M. D5a is the driver, the dialect guards in migration `0001`, `make migrate` and `make seed` on Postgres, and a CI Postgres service job that runs migrate, seed and a health and login smoke; D5b is the fixtures across the test files (about 42, copied from one migrated SQLite file today) with the SQLite-only tests marked. D5b depends on D5a.
- A dependency approval for the driver comes first (`uv add`, lockfile committed).
- `SOCBOARD_DATABASE_URL` chooses the database; SQLite stays the local default; `make migrate` and `make seed` work on both.
- Migration `0001` runs on Postgres with the same tables, constraints and ids (`audit_entries` ids keep ascending, with no gaps promised).
- CI runs a Postgres service container (D5a: migrate, seed, smoke; D5b: the backend tests, with fixtures taking the database from the URL). Evidence of record is CI; the dev-container `db` (D0) is for iteration speed.
- Known failing SQLite-only tests (trigger tests) are named and handled by D6a, not skipped silently: `make verify` reports no new skips.

**D6a Append-only audit trail on Postgres: triggers and tests (Heavy: security boundary; roadmap 4, second part).** Model S. Depends on: D5a, D5b, D1 (approved record). Does not wait for #107.
- On Postgres an UPDATE, DELETE or overwrite of an `audit_entries` row is refused by the database (one test per case, mirroring `tests/test_data_audit_triggers.py`), and `append_audit` still works.
- Postgres `TRUNCATE` does not fire row triggers, so a `BEFORE TRUNCATE` statement trigger refuses it (a test).
- The current `socboard/audit_guard.py` lets a normal audit insert through on Postgres (a test). The guard refuses a statement it cannot compile, and that path has never run on Postgres, so this is shown, not assumed.
- The official Postgres image's default user is a superuser who can disable triggers, so D11 creates a non-superuser application role and the app connects as it; the record states what the owner and superusers can still do.
- The SQLite behaviour and its tests are unchanged.

**D6b Audit guard review for Postgres (Heavy; split from D6).** Model S. Depends on: D6a, #107 (see below). Before D20.
- `socboard/audit_guard.py` is reviewed for SQLite-only parts (`sqlite_sequence`, the pragma words, the SQLite dialect compile); each stays, is made dialect-aware, or is recorded as an open limit, and the data-model record states the Postgres limits. The guard is the only layer that refuses DDL on the table, so this is not optional.
- Order: #107 (simplify the audit guard) comes first, because it rewrites the code this issue reviews. #107 gains a constraint: it introduces no new SQLite-only assumptions, or D6b redoes the work. If #107 is not approved by the time D6a merges, D6b runs against the current guard and #107 follows.

**D7 Prove single ownership on Postgres (Standard; roadmap 5).** Model M. Depends on: D5a, D5b.
- Two simultaneous claims of one case leave exactly one owner and one `claimed` audit entry on Postgres (a test using real concurrent connections, repeated enough to catch a race).
- The loser gets the contract's 409; nothing about the winner's state changes.

**D8 Login attempt limiting (Heavy: authentication; new, spec §4).** Model S. Depends on: D3, D1. Open decision: section 6, question 2.
- Repeated failed logins are slowed or refused for a time with the fixed answer the spec names, and the answer does not reveal whether the username exists (a test comparing a real and a made-up username). The three seeded usernames are public (`socboard/seed.py`), so the limit is keyed on username plus client address, or slows rather than locks per username, so an outsider cannot lock out every reviewer or fail the deploy smoke check (a test). The limit is checked before the password hash work, and the counter table is bounded.
- A correct login still works for another user while one is limited; the limits and window come from configuration, with defaults chosen in the issue and stated in README.
- The limit works behind a reverse proxy: how the client address is read is stated, and a forged forwarding header from outside cannot choose another client's bucket.
- `openapi.yaml` documents the new response; `make contract-check` passes.

**D9 Ingest rate limiting (Standard; new, spec §4).** Model M. Depends on: D3.
- Requests above the configured rate for the holder of the ingest key get 429; the excess alerts are not stored (a test counts rows). The limit is keyed on the ingest key, not the `source` field, because `source` is untrusted text in the body that a caller can change on every request. Requests within the rate are unaffected.
- The refusal order of `openapi.yaml` is kept (401 for a wrong key stays first); the response is documented and `make contract-check` passes.

**D10 One container image, and a CI build job (Standard; roadmap 7).** Model M. Depends on: D2, D3, D4, #100. Protected: `Dockerfile` Layout line in `AGENTS.md`.
- A multi-stage `Dockerfile` builds the frontend (`VITE_USE_MOCK` false, build arguments for the `VITE_*` settings), then copies `dist` into a non-root Python 3.12 image; `.dockerignore` keeps env files, `.scratch/` and `node_modules` out.
- CI builds the image on every pull request and fails on a build error; the human runs it once locally and reports the result.
- No secret, env file or demo credential is in the image or the bundle (a check lists the image's files, as `frontend-build` does for the bundle).
- The start command runs one worker (the in-process limits of D8 and D9 assume it) and passes D4's flag. `VITE_API_BASE_URL` stays unset in the build, so the client uses `/api`.

**D11 Compose stack (Standard; roadmap 8).** Model M. Depends on: D5a, D6a, D10, #22. Protected: `Makefile`. Owns the Compose file in the repository.
- `make compose-up` and `make compose-down` start and stop the app and Postgres; Postgres has a health check; its data directory is a configurable host path (so D17c can mount the encrypted volume there) and defaults to a named volume locally; a one-shot step migrates and seeds before the app starts; the app waits for it. It creates a non-superuser application role (D6).
- Required variables come from the single list (D3). On a fresh clone the first `make compose-up` generates random local secrets into a git-ignored file (values never printed), so the single command works; in deployed mode a missing one fails naming it.
- The app port is published on the host's loopback only. The stack includes a reverse proxy in front of the app (plain HTTP, local configuration only; the deployed Caddy configuration is D17c's), so D12 can test the forwarded-address rule of D8 with a proxy in the path. Postgres major version is the one D1 pins.

**D12 Integration tests against the Compose stack (Standard; roadmap 9).** Model M. Depends on: D11, #22.
- #22's journeys run against `SOCBOARD_BASE_URL` unchanged: ingest to queue, login, claim, move, note, close, audit read, and the refusals.
- The schema check cannot run over HTTP (the app serves no schema, `openapi_url=None`), so it runs inside the built image (`create_app().openapi()` against `openapi.yaml`, by method, path and `operationId`).
- The forwarded-address rule of D8 is exercised with the proxy in the stack.
- Nothing is pinned that #110 may change (the `ingested` audit text).

**D13 End-to-end browser test (Standard; roadmap 10).** Model S. Depends on: D11, #131 (case-page buttons). Dependency approval for the browser tool.
- A browser test with two Analysts and a Lead: ingest, claim, a refused second claim, close with a reason, the Lead reads the audit trail.
- Runs in CI against the Compose stack with no real credentials; failure leaves a screenshot or trace as an artifact.

**D14 CI: build, integration and E2E jobs (Standard; roadmap 11).** Model M. Protected: `.github/workflows/verify.yml`.
- On every push to `main`: unit tests in parallel, then image build, then integration and E2E; a failure at any step stops the later ones.
- Pull requests run the same checks and never receive a deploy credential. `make verify` is unchanged.
- On `main` only, the tested image is pushed to the container registry with the workflow's own token (`packages: write` on that job only) and its digest is an output; the package is public (checked in D19, `VERIFY:`). Actions in jobs that hold a cloud role are pinned by commit, not tag.

### Lane C: infrastructure (Eng writes; the human applies)

All use `VERIFY:` markers for unverified AWS details; CI runs `fmt` and `validate`; the sandbox cannot run `plan`. A new top-level `terraform/` folder and its `AGENTS.md` Layout line need the human's approval.

**D15 Terraform: state bucket (Standard; roadmap 12).** Model W-M. Depends on: D1.
- A private, versioned, encrypted bucket; `.gitignore` covers state and real variable files; an example variable file is tracked; the steps to move state into the bucket are written down.

**D16 Terraform: CI access (Heavy: IAM; roadmap 13).** Model S. Depends on: D1, D15.
- OIDC provider and three roles (plan read-only, apply, deploy), the apply and deploy roles each trusted for this repository and a named GitHub Environment, the plan role for the repository's pull-request subject; no stored keys. A job that names an Environment gets an OIDC subject with the Environment name, not the branch, so any branch's workflow could assume the role unless the Environment restricts deployment branches (D19): a test or manual check shows a non-`main` branch cannot assume either role. Whether the trust policy can also check the numeric repository ids is `VERIFY:` (it may need the subject claim customised). The deploy role may only run one custom Systems Manager document with a fixed script and one validated parameter (the image digest), and read that command's result; a generic shell document would make the role root on the server. The plan role is denied the secret's value. The human applies it; CI cannot change its own roles.

**D17a Terraform: instance IAM and budgets, human-applied (Heavy: IAM; roadmap 14, first part).** Model S. Depends on: D1, D15.
- Every IAM resource of the server lives here with the CI-access part, applied only by the human: the instance role and profile (Systems Manager plus read of the one named secret), and the daily snapshot schedule of the data volume with any execution role it needs (`VERIFY:` whether one is needed) (option A, the human's choice of 2026-11-14 on #139). Budget notifications at three thresholds are also here (account-level, human-applied).
- Recorded in D1 as an amendment to the 2026-11-12 decision. Cost: any later change to the instance's permissions is a manual apply by the human.

**D17b Terraform: instance, network and volume, CI-applied server part (Standard; second part).** Model M. Depends on: D17a.
- One instance with no key pair, an Elastic IP, a security group for 80 and 443 only, an encrypted data volume holding the Postgres data and the env file (it carries the tag the snapshot schedule in D17a selects; the schedule itself is not here), the `project=socboard` tag on every resource, and the metadata service set to require tokens with a hop limit of 1 (so a container cannot read the instance's credentials).
- The apply role may attach only the one instance role to the instance and has an explicit deny on other IAM writes; it passes no snapshot role (option A, the human's choice of 2026-11-14 on #139) (`VERIFY:` the exact permission and its conditions until the first apply).

**D17c Terraform: bootstrap and Caddy (Standard; third part).** Model M. Depends on: D17b, D11 (the Postgres data-directory setting).
- A bootstrap that installs Docker, Compose and Caddy and mounts the encrypted volume at the data directory the Compose stack uses; the deployed Caddy configuration with certificate storage on the data volume; containers restart after a reboot; log rotation; old images pruned.
- It does not deliver the Compose file: D20 owns delivering the file at the deployed commit.

**D18a CI: Terraform format and validate (Standard; roadmap 15, first part).** Model M. Depends on: D15 only, so every later Terraform issue gets format and validate feedback from CI as it is written. Protected: workflow (its own file).
- Pull requests that touch `terraform/` run `fmt -check`, `init -backend=false` and `validate` without credentials. The Terraform version is pinned.

**D18b CI: read-only plan on pull requests (Standard; second part).** Model M. Depends on: D19 (the plan role exists only after the first apply), D16.
- A read-only `plan` is shown on the pull request; forks get no role; state locking and what the plan role may read are `VERIFY:`.

**D19 First apply, by the human (checklist; roadmap 16).** Who: human; Eng drafts the checklist. Depends on: D16, D17a to D17c.
- Before any apply: check that the provider and the state backend both name `us-east-1` (the account's home region is `ap-southeast-2`, so a default region setting in the AWS CLI or console can point elsewhere). Then account and budget notifications, GitHub Environments (`infra` needs a named reviewer and administrators not exempt; both `infra` and `deploy` allow deployment only from `main`), the three applies in order, the secret created, the container registry package confirmed public (`VERIFY:`: new packages may default to private), the IP and hostname noted, and a second `plan` shows no changes.

### Join

**D20 Deploy script and first deploy (Heavy: a root script that holds every secret; roadmap 17).** Model S. Depends on: D6a, D6b, D7, D8, D9, #144, D10, D11, D14, D17c, D19, D21, #22.
- The fixed script behind the Systems Manager document (D16) pulls the image by digest, reads the secret with the instance role, writes the env file with restrictive permissions, migrates before stopping the old container, runs Compose and reloads Caddy. If the image cannot be fetched, or the new one starts and exits, or the migration fails, the current release keeps serving. The human runs it once and the HTTPS URL loads.
- It owns delivering the Compose file: the file at the deployed commit is fetched with the script (D17c does not deliver it). A certificate failure on the shared DNS name has a fallback in the runbook (D23).

**D21 Post-deploy smoke check (Standard; roadmap 18).** Model W-M. Depends on: D3.
- `make smoke URL=<url>` checks `/api/health`, a login, one ingest, and that the alert is in the queue within 5 seconds; it exits non-zero with a message naming the failed step. It reads credentials from the environment only. In CD the authenticated steps run on the server inside the deploy command, and CI checks that result and the public `/api/health`, so no seeded password or ingest key is stored as a GitHub secret. Done before D20.

**D22a Deploy from CI on a green push to `main` (Heavy: deploy credentials; roadmap 19, first part).** Model S. Depends on: D14, D18a, D20, D21.
- Deploy runs only after every test passes, with the OIDC deploy role; the job summary records the image digest; the smoke result is checked after; a failed smoke check fails the job.

**D22b Terraform apply from CI (Heavy; second part).** Model S. Depends on: D18b, D22a.
- Apply covers only the server part, only on `main`, applies the reviewed plan file, and runs after the named reviewer approves in the `infra` Environment.

**D23 Deploy and teardown runbook (Standard, docs; roadmap 20).** Model W-M. Depends on: D19, D22a, D22b, D24.
- How to deploy, where the URL is, how reviewers get credentials (not in the README), how to restore Postgres from a snapshot (rehearsed once, result recorded), how to rotate each secret (seeding never changes an existing user and the Postgres password is set only at first start, so each needs its own steps), the certificate-failure fallback, and the ordered deletion of every cloud resource (server, then CI access, then snapshots and secrets, state bucket last).
- Because idle teardown can leave no URL at grading, it records the URL, a passing CI run and a short demo recording.

**D24 Reset a seeded user's password (Standard; new from the outside review).** Model M. Depends on: #144.
- A documented, tested way to set a new password for an existing seeded user without deleting the user, used by D23's rotation steps.

## 6. Open questions for the human (each with a recommendation)

1. **How does Postgres keep the audit trail append-only?** (a) Trigger functions in the migration, the same rule as SQLite triggers. (b) A database role that has no UPDATE or DELETE right on `audit_entries`. (c) Both. Recommendation: (a) now, record (b) as a Phase 3 hardening; either way the record states what the database owner can still do. Heavy; goes in D1 and D6.
2. **Rate-limit design (D8, D9).** (a) In-process counters: one server and one container make this enough, and it is the smallest change; limits reset on restart and do not work across replicas. (b) Counters in the database: survives restarts, more code and writes. Defaults to choose in the issues (attempts, window, ingest rate). Recommendation: (a), with the limits recorded as a known limit; how to read the client address behind Caddy decided in D8.
3. **Frontend settings at build time.** Pass `VITE_POLL_INTERVAL_MS`, `VITE_FEATURE_REASSIGN` and `VITE_USE_MOCK` as image build arguments, or make the app serve a small runtime settings file? Recommendation: build arguments (no new interface), and change the spec line to say "configurable at build".
4. **May lanes A and C run in parallel,** relaxing the "never two Engineer launches on Core issues at once" rule for Deploy? Recommendation: yes; their files are disjoint (`socboard/`, `tests/` and `Dockerfile` versus `terraform/`).
5. **Where does D2 sit on the tier scale?** #22's PM treated "the backend serves the build" as a new interface, which would make it Heavy. Recommendation: Heavy, as above.

6. **Outside review, round 1: three decisions it raised. All approved by the human on 2026-11-13, with conditions.**
   - **Question 6, instance role: yes.** A CI apply role that can write IAM for the instance role can widen its own reach, which breaks spec §5. The change narrows the "server part" but keeps the purpose of the 2026-11-12 decision, so D1 records it as an amendment. Condition: every other IAM resource of the server part moves with it (the daily snapshot schedule may need its own role, `VERIFY:`). The apply role keeps only the right to attach that one role to the instance, plus a deny on other IAM writes (exact permission unverified until the first apply). Cost: any later change to the instance's permissions is a manual apply by the human. See D17a and D17b.
   - **Question 7, dev-container Postgres: yes, before D5a.** Condition: done between issues, not during one (D0). CI stays the evidence of record; the default test run must still pass without Postgres because the push check has no `db`. One Postgres major version is pinned across the dev container, the CI service and the Compose stack. The human copies the recipe from a clean clone; its password is a throwaway never reused in the deployment. It does not give the sandbox Docker, so D10 to D13 still need the human or CI.
   - **Question 8, #107 first: yes, and D6 is split.** D6a (triggers and tests on Postgres, and a test that the current guard lets a normal audit insert through) starts after D5a and D5b and does not wait for #107. D6b (guard review) waits for #107, which gets a constraint: no new SQLite-only assumptions. #107 had no approved label when the issues were listed; if it is not approved by the time D6a merges, D6b runs against the current guard and #107 follows. D6a and D6b both come before D20, because the guard is the only layer that refuses DDL on the table.

## 7. Spec notes to propose (the human decides; `_docs/specs.md` is protected)

```
Spec note A: the secrets invariant omits the token signing secret
- Added: in §5 "Secrets come only from the environment", add "the token signing secret" to the list (ingest key, seeded passwords, database password).
- Why: SOCBOARD_TOKEN_SECRET is required at start-up (#13); on a public deployment it must come from the cloud secret store like the others.
```

```
Spec note B: the poll interval is set when the frontend is built
- Changed: §5 "(configurable via env var)" to "(configurable when the frontend is built)", unless question 3 chooses a runtime settings file.
- Why: the interval is VITE_POLL_INTERVAL_MS, read at build time, so a single image carries one value.
```

## 8. What this proposal does not cover

Phase 3 (DevOps: separate dev and prod, observability, alerting, the on-call agent) is outlined in the spec and given its own roadmap when Deploy is done. The Terraform and AWS details here follow the roadmap and have not been verified against AWS; the human's first apply is the first real check.

## 9. Outside review, round 1: what was done with each finding

An independent reviewer read this branch at `86e8240` (verdict: ready after changes). Each claim that could be checked against the repository was; all that were checkable held. The plan above was changed as follows.

| Finding | Result |
|---|---|
| D20 does not depend on D6 to D9 or #144 | Accepted: D20 dependencies now list them. #144 (a login password with trailing NUL bytes is accepted) is open and unapproved, and is added to lane B. |
| No item pushes the image to a registry | Accepted: D14 pushes the tested image on `main`; D20 pulls by digest; D19 confirms the package is public (`VERIFY:`). |
| OIDC subject carries the Environment name, not the branch | Accepted: D19 limits both Environments to `main`; D16 adds a check that a non-`main` branch cannot assume either role. |
| Instance role in the CI-applied part lets the apply role widen permissions | Accepted (D17a, D17b); it amends a 2026-11-12 decision, approved as question 6. |
| D4's env opt-in cannot be refused under `make backend-run` | Confirmed (`Makefile` recipe and `scripts/backend_probe.py` read the inherited environment). D4 now uses a command-line flag; no Makefile change. |
| Smoke check needs secrets CI should not hold | Accepted: authenticated steps run on the server inside the deploy command (D21). |
| "The one Systems Manager command" names no mechanism | Accepted: a custom document with a fixed script and one validated parameter (D16). |
| Unowned deployed pieces (Caddy config, Compose file delivery, Postgres volume mapping, reboot, log rotation, pruning) | Accepted: assigned to D11, D17c and D20 (the Compose file is owned by D11 and delivered by D20; Caddy and the host setup by D17c). |
| D8 per-username lockout lets anyone lock out the public seeded users | Confirmed (`socboard/seed.py` lists the three usernames). D8 revised. |
| D6: `TRUNCATE` bypasses row triggers; superuser can disable triggers; #107 rewrites the guard | Accepted (D6, D11, question 8). |
| D5 to D7 "CI is the only evidence" ignores the kit's Compose variant | Confirmed (`_docs/agent-kit/environments.md`). Question 7. |
| D18 plan role exists only after D19; lanes not fully disjoint | Accepted: D18 split; shared files named in section 4. |
| D12 schema check cannot run over HTTP | Confirmed (`openapi_url=None`). Runs in the image. |
| No rotation path | Accepted: D23 steps and new D24. |
| D3 requires seed passwords the app never reads | Confirmed. D3 corrected. |
| Fresh clone has no env file; teardown can leave no URL at grading | Accepted: D11 generates local secrets on first run; D23 records URL, CI run and demo. |
| Sizing (D17, D22, D20, D5) | Accepted: D17a to c, D22a and b, D20 Heavy, D5a and b. Filed issue #143 is D5 as one issue; it needs editing to D5a (see round 2). |
| Metadata service tokens and hop limit | Accepted (D17b). |
| Pin actions by commit; missing asset returns 404; smoke before deploy | Accepted (D14, D2, D21). |
| Missing: restore rehearsal, migrate before stopping old container, container that exits, certificate failure | Accepted (D20, D23). |
| `socboard/migrate.py` "assumes SQLite" | Confirmed wrong: it already branches by dialect. Corrected in the wave 1 drafts. |

Left as `VERIFY:` (not checkable here, as the reviewer said): whether the trust policy can use numeric repository ids; what a read-only plan policy may read; document-level limits on the send-command permission; state locking under a read-only role; the registry package's default visibility; which peer address the app sees behind Caddy. A first apply and one failed assume-role from a branch settle most of them.

### Round 2: the reviewer's check of the revised plan (commit `9b73286`)

The reviewer answered yes to questions 6 to 8 (conditions in section 6) and listed what the revision still got wrong. Dispositions:

| Finding | Result |
|---|---|
| The filed issues #141, #142, #143 still carry the old criteria | Confirmed. The drafts (`wave-1-issue-drafts.md`) are corrected; the filed bodies still need editing before grooming (the human or a PATCH; the kit has no script that edits an issue). |
| D6 half-waits and cannot pass QA | Fixed: D6a and D6b. |
| No item adds the proxy to the Compose stack | Fixed: D11 includes it. |
| Compose file delivery has two owners | Fixed: D11 owns the file, D20 delivers it, D17c does not. |
| D17 split in name only; D17b not parallel; budgets not human-applied | Fixed: three issues with their own tier, model and dependencies; budgets in D17a, human-applied; D17c depends on D17b and D11. |
| D18a waits too long | Fixed: depends on D15 only. |
| Stale references to D5, D22 | Fixed: D5a and D5b, D22a and D22b; D23 depends on D24. |

New: D0, the dev-container sitting (question 7), and the #107 constraint and fallback (question 8). The constraint on #107 is an edit to that issue, which the human or the PM makes.
