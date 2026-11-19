# Deploy wave 2: full issue drafts (not filed)

Companion to `_docs/planning/deploy-backlog-proposal.md`. **Drafts only: nothing here is filed, groomed or approved.** They were written while the human was away, from the plan as approved on 2026-11-13 (questions 1 to 8 with conditions) and the two outside reviews. They cover the items that do not depend on #22: D6a, D6b, D8, D9, D10, D15, D16, D17a, D17b, D17c, D18a, D18b, D21, D24. D11 to D14, D19, D20, D22 and D23 wait for #22 or for the Terraform text and stay as outlines in the proposal.

Each block starts with the title line `make issue-create` expects, then the body. File one only when its dependencies are close and its turn in the order comes (the PM grooms only a few ahead: `.kiro/steering/delivery-pace.md`, item 3). Before filing, re-read each body against the wave 1 issues as they stand then (#139 to #143), and against any decision the human has made since.

AWS and Terraform details are written from the roadmap and general knowledge, and are marked `VERIFY:` where nothing here can check them. The first apply by the human is the first real check. Facts about the code were read from `main` on 2026-11-13.

---

## D6a

Title: Make the audit trail append-only on Postgres: triggers and tests

## Why

Spec §5 says the audit trail is append-only on any supported database. On SQLite three triggers in migration `0001` enforce it (`audit_entries_no_update`, `audit_entries_no_delete`, `audit_entries_no_reuse_id`, `RAISE(ABORT, ...)`, which Postgres does not have). D5a gets the schema onto Postgres without them. Postgres `TRUNCATE` does not fire row triggers, so a truncate empties the trail unless a statement trigger refuses it. The official Postgres image's default user is a superuser, who can disable triggers.

## Goal

On Postgres, an UPDATE, DELETE, overwrite or TRUNCATE of `audit_entries` is refused by the database for the application's role, `append_audit` still works, and the SQLite behaviour is unchanged.

## Acceptance criteria
- [ ] On Postgres, an UPDATE and a DELETE of an `audit_entries` row are each refused with a fixed message, and an INSERT with an id that already exists is refused (the three kinds the SQLite triggers cover). One test per kind, written to mirror `tests/test_data_audit_triggers.py` and run on Postgres.
- [ ] `TRUNCATE audit_entries` is refused by a statement-level trigger (a test). A `TRUNCATE` that also names other tables is refused too.
- [ ] `append_audit` (`socboard/audit.py`) still appends on Postgres, ids ascend, and a plain insert with a new id succeeds.
- [ ] The application connects as a role that does not own `audit_entries` and cannot disable triggers or run DDL; the migration runs as the owner role. A test connects as the application role and shows `ALTER TABLE audit_entries DISABLE TRIGGER ALL` and `DROP TRIGGER` are refused, and that a normal request path still works. The Compose and CI setups create the two roles (the Compose part is D11; here a test fixture or the CI service setup does it).
- [ ] The current `socboard/audit_guard.py` lets a normal audit insert through on Postgres: a test appends through the app's own session on Postgres with the guard installed, and the entry is written. The guard refuses a statement it cannot compile, and that path has never run on Postgres, so this is shown, not assumed.
- [ ] The SQLite triggers and every SQLite test pass unchanged. Tests that are SQLite-only by nature carry the visible marker D5b added, with a reason.
- [ ] Refused case, recorded as a limit and not fixed here: a superuser or the table owner can still disable the trigger. The data-model record gets a line saying so, and what the database owner can still do.
- [ ] `make verify` passes; the Postgres tests run in CI against the pinned Postgres version.

## Out of scope
- The review of `socboard/audit_guard.py` for SQLite-only assumptions (D6b, after #107).
- A role with no UPDATE or DELETE privilege, as a second layer (Phase 3 hardening, recorded in the decision record).
- Compose and production role creation beyond a test fixture (D11).

## Design

The triggers go in migration `0001`'s Postgres branch, next to the SQLite ones, so a fresh database of either kind has the same shape. If editing `0001` is judged unsafe, a migration `0002` that does nothing on SQLite is the alternative; the Engineer says which and why before starting.

## Constraints
- Files: `socboard/migrations/versions/0001_initial_schema.py` (the Postgres branch only; its SQLite output must not change), `socboard/migrate.py` if needed, `tests/` (new Postgres trigger tests), `_docs/decisions/2026-11-12T0834Z-data-model.md` (the Postgres limits line). Nothing protected.
- Depends on: D5a and D5b (merged), D1 (approved record, with the audit decision), the dev-container sitting D0 for iteration speed (CI stays the evidence).
- Fixed value: the refusal messages mirror the SQLite ones where the database allows it. Source: `socboard/migrations/versions/0001_initial_schema.py`.
- Proposed tier: heavy (a security boundary, spec §5). Expected paths: as above, plus the decision record the Engineer commits from the issue's Decision record section.

## Decision record

PM's draft, to be copied here at grooming from #139's Decision 1 (row and truncate triggers, application role that does not own the table, role-only privileges deferred to Phase 3). Not repeated in full in this draft.

---

## D6b

Title: Review the audit guard for Postgres after its simplification

## Why

`socboard/audit_guard.py` refuses DDL aimed at `audit_entries` and its triggers, and it is the only layer that does. It is written around SQLite: the `sqlite_sequence` table, the two pragma names, an `ATTACH` rule, and a compile step that falls back to the SQLite dialect. Postgres has none of those, and its own ways to defeat the trail (a trigger disabled by `ALTER TABLE`, a `DROP TRIGGER`, a `TRUNCATE`) are not what the guard looks for. Open issue #107 simplifies the guard, so this review waits for it, so the work is not done twice.

## Goal

The guard, as simplified by #107, is reviewed for Postgres: each SQLite-only part is kept, made dialect-aware or recorded as an open limit, and the Postgres ways to defeat the trail are either refused by the guard or recorded as limits the database layer (D6a) covers.

## Acceptance criteria
- [ ] Each SQLite-only part of the guard is listed in the issue comment with a decision: stays (SQLite only), made dialect-aware, or recorded as an open limit with the reason.
- [ ] On Postgres, `DDL("ALTER TABLE audit_entries DISABLE TRIGGER ALL")`, `DROP TRIGGER`, `DROP TABLE audit_entries` and `TRUNCATE audit_entries` sent through the ORM or Core are each either refused by the guard or covered by D6a's database-level refusal; a test per statement shows which, and the guard does not rely on a refusal it cannot produce.
- [ ] A normal audit insert passes the guard on Postgres (restated from D6a, kept as a regression test).
- [ ] The SQLite behaviour and its tests are unchanged, and #107's tests still pass.
- [ ] The data-model record's list of open limits is updated for Postgres, naming raw SQL sent through `exec_driver_sql` or a DBAPI cursor as still outside the guard.

## Out of scope
- Simplifying the guard (#107).
- New database roles or privileges (D6a, Phase 3).

## Design

None.

## Constraints
- Files: `socboard/audit_guard.py`, `tests/` (guard tests on Postgres), `_docs/decisions/2026-11-12T0834Z-data-model.md`. Nothing protected.
- Depends on: D6a (merged) and #107. If #107 is not approved when D6a merges, this issue runs against the current guard and #107 follows, as the human ruled on 2026-11-13. Both D6a and D6b come before the first deploy (D20).
- Proposed tier: heavy (the guard is the only layer that refuses DDL on the table). Expected paths: as above, and a decision record only if the review changes a rule.

---

## D8

Title: Slow repeated failed logins without letting anyone lock out a user

## Why

The spec requires that repeated failed logins for one username, or from one client, are slowed or refused for a time, with a fixed answer that does not reveal whether the username exists. The three seeded usernames are public (`socboard/seed.py`), so a plain "lock after N failures" would let anyone lock out every reviewer and make the post-deploy smoke check fail. Today nothing limits attempts; `POST /api/login` strips the username, looks it up, and verifies the password against a dummy hash for an unknown user so timing does not reveal it (`socboard/auth.py`).

## Goal

Repeated failed logins are slowed or refused for a configured time, keyed so one outsider cannot lock out a real user, with an answer that is the same for a real and a made-up username.

## Acceptance criteria
- [ ] After a configured number of failures within a configured window for the same client and username, further attempts are refused with a fixed answer (429 with a `Retry-After` header) until the window passes. The defaults are chosen in the issue and stated in the README; both come from configuration (the settings list from #141), and tests raise them.
- [ ] The answer and the timing do not reveal whether the username exists: a test compares a real and a made-up username across the limit and finds the same status, body and headers.
- [ ] The key is the username (stripped and lower-cased the same way login looks it up) together with the client address, not the username alone. A test shows a client at one address hitting the limit cannot stop the same username logging in from another address, and a correct password at the first address is refused only while limited, never after the window passes.
- [ ] The limit is checked before the password hash work, so a flood of attempts costs little. A test shows no hash is computed for a refused attempt.
- [ ] The counter table is bounded (a maximum number of tracked keys, oldest dropped), so a flood of distinct made-up usernames cannot grow memory without limit. A test fills it past the bound.
- [ ] A successful login does not count and does not reset another client's count.
- [ ] The client address is read in one place. Behind the reverse proxy, the address is the one the proxy reports for the connection, not a value the caller can set: a request with a forged `X-Forwarded-For` from outside the trusted proxy cannot choose another client's bucket (a test with the proxy's address configured as the only trusted one). `VERIFY:` the exact uvicorn setting for trusting only the proxy's address.
- [ ] `openapi.yaml` documents the 429 response on `POST /api/login` with the `ApiError` body and the header; `make contract-check` passes and the generated schema matches.
- [ ] The frontend shows the server's message for a 429 on the sign-in screen without a crash (a test with a stubbed `fetch`, beside the existing 401, 403, 409 and 422 tests).
- [ ] Limits are in the process, with one worker, and reset on restart (the human's decision of 2026-11-13). The README says so.
- [ ] Existing login tests pass unchanged.

## Out of scope
- Shared counters across workers or replicas (the decision record's known limit).
- A lockout that persists across restarts, CAPTCHA, or notifying the user.
- Ingest limiting (D9).

## Design

None beyond the Decision record (limits are counted in the process).

## Constraints
- Files: `socboard/auth.py`, one new `socboard/` module for the limiter, `socboard/app.py`, `openapi.yaml`, `frontend/src/` (the 429 message and its test), `tests/`, `README.md`. Nothing protected.
- Depends on: #141 (the settings list), D1 (approved record), #144 (the trailing-NUL fix, which also touches `auth.py`; do #144 first).
- Fixed values: the 429 status and header are a grooming proposal; the spec allows 429 or 401 (`_docs/specs.md` §4).
- Proposed tier: heavy (authentication, and an `openapi.yaml` interface the frontend uses). Expected paths: as above, plus a decision record only if the key or the status choice needs one.

---

## D9

Title: Refuse ingest above a configured rate and store none of the excess

## Why

The spec requires that a source system exceeding a fixed ingest rate is refused with 429 and the excess alerts are not stored. Ingest uses one shared API key (`socboard/ingest.py`), and `source` is a field in the request body that the caller sets freely, so a limit keyed on `source` could be dodged by renaming the source on every request.

## Goal

Ingest requests above a configured rate for the holder of the ingest key get 429, store nothing, and leave requests within the rate unaffected.

## Acceptance criteria
- [ ] Above the configured rate (requests per window), `POST /api/alerts` with a valid key gets 429 with a `Retry-After` header and the `ApiError` body, and no alert, case or audit entry is written (a test counts rows before and after).
- [ ] The key for the limit is the ingest key, not the `source` field: a test sends over the limit with a different `source` value on every request and is still refused.
- [ ] A request with a wrong or missing key still gets 401 first, as `openapi.yaml` orders it, and does not use up the budget of the key holder (a test).
- [ ] The rate and window come from configuration (the settings list from #141), with defaults chosen in the issue and stated in the README; tests raise them. The limit is checked before the body is validated or stored.
- [ ] Within the rate, behaviour is unchanged: the existing ingest tests pass unchanged. After the window passes, requests are accepted again.
- [ ] The tracked state is bounded and in the process, with one worker, and resets on restart; the README says so.
- [ ] `openapi.yaml` documents the 429 on `ingestAlert`; `make contract-check` passes and the generated schema matches.

## Out of scope
- Per-source limits (the source name is untrusted text).
- Shared counters across workers or replicas.
- Login limiting (D8).

## Design

None.

## Constraints
- Files: `socboard/ingest.py`, the limiter module D8 adds if it is already merged (share it), `socboard/app.py`, `openapi.yaml`, `tests/`, `README.md`. Nothing protected.
- Depends on: #141, D1.
- Proposed tier: standard (no new boundary beyond D8's, same contract style). Expected paths: as above.

---

## D10

Title: Build one container image of the app and the built frontend, and build it in CI

## Why

The spec's Deploy stories need one container image that serves the web app and the API from one origin. Nothing builds one: there is no `Dockerfile`, and CI only runs `make verify`. The sandbox has no Docker, so CI is where the image gets built until the human tries it once.

## Goal

A `Dockerfile` builds the image from the repository, CI builds it on every pull request, and the image runs the app as a non-root user with nothing secret or demo-related in it.

## Acceptance criteria
- [ ] A multi-stage `Dockerfile`: a first stage builds the frontend with the mock off and the `VITE_*` settings passed as build arguments (`VITE_API_BASE_URL` stays unset so the client uses `/api`); a second stage, based on Python 3.12 (the version #100 pins), installs the locked runtime dependencies only, copies `socboard/` (with its migrations) and the built `dist`, and runs as a non-root user.
- [ ] The start command is `python -m socboard.server` with #142's flag, `SOCBOARD_HOST` set to all addresses, and one worker. The image also runs `python -m socboard.migrate` and `python -m socboard.seed` (used by D11 and D20's one-shot step).
- [ ] A `.dockerignore` keeps `.git`, `.scratch/`, `node_modules`, env files, `socboard.db`, `tests/` and the planning docs out of the build context.
- [ ] CI builds the image on every pull request and push, and fails on a build error. The step lists the image's files and fails if it finds an env file, a database file, `.git`, a demo credential or a hostile test string (the same patterns `make frontend-build` checks), a test file, or a secret pattern from `_docs/agent-kit/scripts/secret-patterns.txt`. A case that must be refused: a deliberately added env file in the build context makes that check fail (shown once on a throwaway branch, by the human).
- [ ] The built image starts with no `dist` problem: `GET /` returns the entry page and `GET /api/health` returns 200 (checked in CI by running the container, once D2 and #142 are merged).
- [ ] The image's Python major and minor version equals the contents of `.python-version` (added by #100): a CI step runs the image's interpreter and compares, and fails on a mismatch. A case that must be refused: a base image tag of another minor version makes the step fail.
- [ ] The image carries no cloud credential and no seeded password; the start command refuses to start in deployed mode without the settings from #141 (a CI step runs the container without them and expects exit 2).
- [ ] The human runs the build once locally and reports the result in a task file (`_human-tasks/`), because the sandbox cannot.
- [ ] `make verify` is unchanged and passes.

## Out of scope
- Pushing the image to a registry (D14).
- Compose, Postgres and Caddy (D11, D17c).
- Multi-architecture builds.

## Design

None.

## Constraints
- Files: `Dockerfile`, `.dockerignore`, `.github/workflows/` (a new workflow file for the image job; protected path, the human approves the diff), `README.md`; `AGENTS.md` gets a Layout line for the `Dockerfile` (protected, the human approves the exact diff).
- Fixed values and their sources: tool versions from `.github/workflows/verify.yml` (uv 0.13.6, Node 24.22.0, bun 1.4.2) and Python 3.12 from `AGENTS.md`; pin base images by digest where the tag exists (`VERIFY:` tags and digests on the first build).
- Depends on: D2 (#140), #141, #142, #100.
- Proposed tier: standard (a new file set and a CI job, no new boundary; the start flag is #142's decision). Expected paths: as above.

---

## D15

Title: Terraform: the state bucket

## Why

Terraform state holds resource details and must outlive a laptop. The Deploy decisions (`_docs/planning/roadmap-3-deploy.md`) call for a private, versioned, encrypted S3 bucket in `us-east-1`, created first with local state and then used as the backend. No `terraform/` folder exists yet.

## Goal

A `terraform/` folder holds the state bucket's definition and the steps to move state into it, formatted and valid, ready for the human to apply once.

## Acceptance criteria
- [ ] `terraform/state/` defines one bucket: private (public access blocked), versioned, encrypted at rest, with a policy that refuses non-TLS access, in `us-east-1` named explicitly in the provider (never from a default region setting), tagged `project=socboard`. `VERIFY:` each argument name against the pinned provider version.
- [ ] The state backend uses the bucket's native lock file (`VERIFY:` that the pinned Terraform version supports it) so no other service is needed.
- [ ] `terraform fmt -check` and `terraform validate` pass (CI runs them through D18a; the Engineer cannot run Terraform here and says so).
- [ ] `.gitignore` covers state files, plan files, `.terraform/` and real variable files; an example variable file is tracked and holds names and placeholder values only. A case that must be refused: committing a real variable file or a state file is blocked by `.gitignore` (shown with `git check-ignore` on both paths).
- [ ] The migration steps (create with local state, then configure the backend and move state) are written in `terraform/README.md` as numbered steps for the human, each with the expected output; they are marked as not yet run.
- [ ] No access key, secret, account number or password appears in any file (the kit's secret scan reports none).
- [ ] The never-hold rule for Terraform state and its outputs (decision record of #139, section F): no `output` block exposes a secret value, any output that could hold one is marked sensitive, and no variable declares a secret. Also, no `data` source or resource reads a secret value into state (for example `aws_secretsmanager_secret_version`). A case that must be refused: a throwaway `output` that prints a variable named like a secret makes the check (a search of the folder in the review, until a CI check exists) fail.
- [ ] The new folder and its `AGENTS.md` Layout line are approved by the human (protected).

## Out of scope
- The CI-access roles (D16), the server (D17a to D17c), the workflows (D18a, D18b).
- Applying anything (D19, the human).

## Design

None.

## Constraints
- Files: `terraform/state/*`, `terraform/README.md`, `terraform/*.example` (names only), `.gitignore`, `AGENTS.md` (Layout line, protected).
- New tool: Terraform. The human approves it and the version pin; the version is recorded in one file and the CI job (D18a) reads it.
- Depends on: D1 (approved record: region, the tag, what state must never hold).
- Proposed tier: standard (infrastructure as code, applied only by the human). Expected paths: as above.

---

## D16

Title: Terraform: GitHub OIDC access for CI, with separate plan, apply and deploy roles

## Why

The spec requires CD with a short-lived scoped credential (GitHub OIDC), pull requests that never get a deploy credential, and no long-lived cloud key in the repository or in GitHub secrets. When a GitHub job names an Environment, the token's subject carries the Environment name and not the branch, so a workflow on any branch that names that Environment could assume the role unless the Environment restricts which branches may deploy. CI also must not be able to change its own permissions.

## Goal

Terraform defines the OIDC provider and three roles (plan, apply, deploy) with trust limited to this repository and the right Environment or pull-request subject, applied only by the human.

## Acceptance criteria
- [ ] One OIDC provider for GitHub Actions and three roles: a plan role (read-only, including the state bucket), an apply role, and a deploy role. Each role's trust names the audience and a subject: the plan role trusts the repository's pull-request subject; the apply role trusts the `infra` Environment; the deploy role trusts the `deploy` Environment. `VERIFY:` the exact subject strings and whether a numeric repository id can also be required in the trust policy (it may need the subject claim customised).
- [ ] The apply role covers only the CI-applied server part (D17b): it may attach only the one instance role to the instance and has an explicit deny on every other IAM write; it passes no snapshot role (option A, the human's choice of 2026-11-14 on #139). A case that must be refused: a plan or test shows the apply role cannot create or modify any IAM role or policy, including its own.
- [ ] The deploy role may only run one custom Systems Manager document (fixed script, one parameter, the image digest, validated by a pattern) on instances tagged `project=socboard`, and read that command's result; it cannot run a generic shell document and cannot read any secret. A refused case: the policy names no generic run-command document.
- [ ] The plan role is denied the value of the application secret.
- [ ] The never-hold rule for Terraform state and its outputs (decision record of #139, section F): no `output` block exposes a secret value, any output that could hold one is marked sensitive, and no variable declares a secret. Also, no `data` source or resource reads a secret value into state (for example `aws_secretsmanager_secret_version`).
- [ ] No access key exists for any role, user or workflow; the Terraform creates none, and the secret scan on the folder reports nothing.
- [ ] A non-`main` branch cannot assume the apply or deploy role: the Environments' deployment-branch rule (D19) is checked by the human, and a failed assume-role attempt from a throwaway branch is recorded in D19's task file.
- [ ] The whole file set is human-applied only (the decision record's amendment): the apply role cannot change any of it.
- [ ] `terraform fmt -check` and `validate` pass.

## Out of scope
- The instance role and profile, the snapshot schedule and its role, and budgets (D17a), the server (D17b).
- The workflows that use the roles (D18b, D22a, D22b).

## Design

None beyond the Decision record (D1, Decision 3).

## Constraints
- Files: `terraform/ci-access/*` and its README section. The `AGENTS.md` Layout line comes with D15.
- Depends on: D1 (approved, with the amendment), D15 (state bucket).
- Proposed tier: heavy (it defines what CI may do in the cloud). Expected paths: as above and the decision record the Engineer commits from the issue's Decision record section.

## Decision record

PM's draft, to be copied here at grooming from #139's Decision 3 and the OIDC design in `_docs/planning/roadmap-3-deploy.md` (separate roles, trust by Environment, human applies CI access). Not repeated in full in this draft.

---

## D17a

(Filed as #162 on 2026-11-14, groomed; the text below is the earlier draft and is kept for history. #154 is D15, #155 is D18a, #156 is D16.)

Title: Terraform: the instance's IAM role and the budgets, applied by the human

## Why

The human ruled on 2026-11-13 that an apply role able to write IAM could widen its own reach (spec §5), so every IAM resource of the server and the budgets are applied only by the human, with the CI-access part. The instance needs a role to talk to Systems Manager and to read one secret; the daily snapshots may need a role of their own.

## Goal

Terraform defines the instance role and profile, the daily snapshot schedule and any role it needs, and the budget notifications, as a part only the human applies.

## Acceptance criteria
- [ ] The instance role allows Systems Manager's agent operations and reading exactly one named secret (by ARN); it allows nothing else. A refused case: the policy grants no wildcard resource on secrets and no other service.
- [ ] The daily snapshot schedule and any execution role it needs are defined here (option A, the human's choice of 2026-11-14 on #139); D17b creates the volume only.
- [ ] Budget notifications at three thresholds (half, 80 percent and the full limit of a monthly amount the human sets) go to an address the human sets in the variable file, not in the repository. `VERIFY:` the budget's region and API behaviour.
- [ ] The never-hold rule for Terraform state and its outputs (decision record of #139, section F): no `output` block exposes a secret value, any output that could hold one is marked sensitive, and no variable declares a secret. Also, no `data` source or resource reads a secret value into state (for example `aws_secretsmanager_secret_version`).
- [ ] Every resource is tagged `project=socboard`; the trust policy of each role names only the service that assumes it.
- [ ] The README states the cost: a later change to the instance's permissions is a manual apply by the human.
- [ ] `terraform fmt -check` and `validate` pass; the secret scan reports nothing.

## Out of scope
- The instance, network and volume (D17b), the bootstrap (D17c).
- The CI roles (D16).

## Design

None.

## Constraints
- Files: `terraform/iam-and-budgets/*`. Depends on: D1, D15.
- Proposed tier: heavy (IAM). Expected paths: as above.

---

## D17b

Title: Terraform: the server instance, network and encrypted data volume

## Why

The deployment is one small server running Compose. It is reached through Systems Manager only, with no SSH key and no port 22, and its data (Postgres files and the env file) sits on its own encrypted volume with daily snapshots. Containers on the host must not be able to read the instance's credentials.

## Goal

Terraform defines the instance, Elastic IP, security group and encrypted data volume, as the part CI may apply on `main` after approval. The daily snapshot schedule is in #162 (D17a), applied by the human.

## Acceptance criteria
- [ ] One instance with no key pair, an Elastic IP, and the instance profile from D17a. The security group opens 80 and 443 to the world and nothing else; no rule opens 22 or the app port. A refused case: a test or a plan check fails if a rule opens any other port (`terraform validate` plus a policy check script in CI, `VERIFY:` the approach).
- [ ] The metadata service requires session tokens with a hop limit of 1, so a container cannot read the instance's credentials. `VERIFY:` the argument names.
- [ ] An encrypted data volume, attached to the instance, holds the Postgres data and the env file; it carries the tag that the snapshot schedule in #162 (D17a) selects, and that tag is a contract with #162: removing or renaming it would stop the backups with no error, so a change to it needs #162 changed in the same sitting. This part creates no snapshot schedule and no IAM resource (option A, the human's choice of 2026-11-14 on #139).
- [ ] The root volume is encrypted.
- [ ] Every resource is tagged `project=socboard`.
- [ ] The never-hold rule for Terraform state and its outputs (decision record of #139, section F): no `output` block exposes a secret value, any output that could hold one is marked sensitive, and no variable declares a secret. Also, no `data` source or resource reads a secret value into state (for example `aws_secretsmanager_secret_version`).
- [ ] The apply role (D16) can create these resources and attach the one instance role, and nothing in this folder creates IAM resources (a search of the folder finds none).
- [ ] `terraform fmt -check` and `validate` pass; the secret scan reports nothing.

## Out of scope
- IAM and budgets (D17a), bootstrap and Caddy (D17c).
- A stop schedule, a second environment, a managed database.

## Design

None.

## Constraints
- Files: `terraform/server/*`. Depends on: D17a, D15. Region: `us-east-1`, named in the provider.
- Proposed tier: standard (infrastructure as code, applied by the human first). Expected paths: as above.

---

## D17c

Title: Terraform: server bootstrap, Caddy and the host's Docker setup

## Why

The server must run Compose with Postgres on the encrypted volume, serve HTTPS with an automatic certificate, survive a reboot and not fill its disk. Docker, Compose and Caddy have to be installed, and the data volume mounted where the Compose stack expects it.

## Goal

The instance boots into a host that has Docker, Compose and Caddy, the data volume mounted at the data directory the stack uses, and a Caddy configuration for the public hostname.

## Acceptance criteria
- [ ] The bootstrap installs Docker, the Compose plugin and Caddy, and mounts the encrypted volume at the data directory D11's Compose file takes as its Postgres path. The mount survives a reboot and does not block boot if the volume is missing. `VERIFY:` device naming on this instance type (use a stable identifier, not a guessed device name).
- [ ] Caddy proxies to the app on the host's loopback only, and its certificate and account data live on the data volume. The hostname is derived from the Elastic IP through a public wildcard-DNS service (the decision of 2026-11-12). The certificate authority's staging endpoint is a variable for testing. `VERIFY:` the service's name format and the contact address rule.
- [ ] Containers restart after a reboot; container logs are rotated with a stated size limit; unused images are pruned on a schedule.
- [ ] The never-hold rule for Terraform state and its outputs (decision record of #139, section F): no `output` block exposes a secret value, any output that could hold one is marked sensitive, and no variable declares a secret; the user data and the Caddy file contain no secret; and no `data` source or resource reads a secret value into state (for example `aws_secretsmanager_secret_version`).
- [ ] The bootstrap writes no secret, and does not deliver the Compose file (D20 delivers it at the deployed commit).
- [ ] The bootstrap is idempotent on a re-run (a second boot changes nothing) (`VERIFY:` by the human's first apply).
- [ ] `terraform fmt -check` and `validate` pass; the secret scan reports nothing.

## Out of scope
- The Compose file (D11), the deploy script (D20), the certificate-failure runbook (D23).

## Design

None.

## Constraints
- Files: `terraform/server/*` (user data and the Caddy file). Depends on: D17b and D11 (the Postgres data-directory setting).
- Proposed tier: standard. Expected paths: as above.

---

## D18a

Title: CI: format and validate the Terraform on every pull request

## Why

The Engineer cannot run Terraform in the sandbox, so CI is the only feedback for the Terraform issues. It should be available as soon as the first Terraform files exist, not after all of them.

## Goal

A workflow runs `terraform fmt -check`, `init -backend=false` and `validate` for every Terraform folder, without any cloud credential, on pull requests that touch `terraform/`.

## Acceptance criteria
- [ ] A new workflow file runs on pull requests (and pushes to `main`) that change `terraform/**`, with the Terraform version read from the one file D15 records, and the action pinned by commit.
- [ ] Each folder under `terraform/` is checked: `fmt -check -recursive`, `init -backend=false`, `validate`. The job has no `id-token` permission and no secret, so it works for forks.
- [ ] A bad format or an invalid file fails the job (shown once on a throwaway branch, by the human).
- [ ] The job does not run when no Terraform file changed, and `make verify` is unchanged.
- [ ] The workflow has its own file, so the other CI changes in the Deploy phase do not collide with it.

## Out of scope
- `plan` (D18b), apply (D22b).

## Design

None.

## Constraints
- Files: `.github/workflows/terraform-check.yml` (protected path; the human approves the diff). Depends on: D15 only (the version file and the first folder).
- New tool: the Terraform setup action and its pin, approved with D15.
- Proposed tier: standard. Expected paths: as above.

---

## D18b

Title: CI: a read-only Terraform plan shown on pull requests

## Why

A reviewer should see what a Terraform change would do before merging it. The plan role exists only after the human's first apply (D19), so this waits for it.

## Goal

Pull requests that change `terraform/` show a read-only plan, produced with the plan role, with no way to apply anything.

## Acceptance criteria
- [ ] A job runs `plan` with the plan role (OIDC, pull-request subject) and posts or uploads the plan output; it has no apply step and the role cannot apply.
- [ ] Fork pull requests get no role (the job is skipped or fails closed). A refused case: a fork run shows no token and does not attempt the role.
- [ ] The plan output hides sensitive values (`VERIFY:` how), and the plan role cannot read the application secret. This plan is the place a reviewer reads Terraform outputs for the never-hold rule of the decision record of #139 (section F): an output holding a secret value, or one that is not marked sensitive, is a refusal reason.
- [ ] State locking works under the read-only role, or the job runs with locking off and says why (`VERIFY:` against the first plan).
- [ ] A change with no effect shows "no changes".

## Out of scope
- Apply from CI (D22b).

## Design

None.

## Constraints
- Files: `.github/workflows/terraform-plan.yml` (protected path). Depends on: D19, D16, D18a.
- Proposed tier: standard. Expected paths: as above.

---

## D21

Title: A post-deploy smoke check that runs on the server and from outside

## Why

After a deploy, CI must know the app works: the health route answers, a seeded user can log in, an alert can be ingested, and it reaches the queue within the 5 second target. The check needs a seeded password and the ingest key, which should not be stored as GitHub secrets, so its authenticated steps run on the server inside the deploy command.

## Goal

`make smoke URL=<url>` checks the live app and exits non-zero naming the failed step; the same script runs on the server against loopback, and from CI against the public URL for the health route only.

## Acceptance criteria
- [ ] The steps are, in order: `GET /api/health` returns 200; a login as the Lead succeeds; one synthetic alert is ingested with the key and the call returns 201; the alert appears in the queue within 5 seconds of the ingest response (polling every half second); the case's audit trail can be read by the Lead.
- [ ] The alert is clearly synthetic (a fixed title and `source` such as `smoke-check`) and the script does not delete anything.
- [ ] Credentials come from the environment only, never from an argument or the URL; the script never prints a password, a key or a token, including in failure output. A refused case: a URL with embedded credentials is refused before any request.
- [ ] A non-HTTPS URL is refused unless the host is loopback.
- [ ] Each step failing is shown on a stub server: the output names the step and the exit code is 1; a total timeout stops it.
- [ ] `make verify` passes; the script uses the standard library only.

## Out of scope
- Running it from CI with secrets (the deploy command runs the authenticated steps on the server, D20 and D22a).
- Load or latency measurement beyond the 5 second check.

## Design

None.

## Constraints
- Files: `scripts/smoke.py`, `tests/test_smoke.py`, `Makefile` (a `smoke` target; protected), `AGENTS.md` Commands line (protected). Depends on: #141 (names for the variables).
- Proposed tier: standard. Expected paths: as above.

---

## D24

Title: Reset a seeded user's password without deleting the user

## Why

`make seed` never changes an existing user (its design, `socboard/seed.py`), and the database password is set only at first start. After a deployment, a reviewer's password may need to change, and there is no way to do it short of editing the database by hand. A token carries only the user id and expiry (see #103), so an old token stays valid after a password change until it expires; that is stated as a limit.

## Goal

A tested command sets a new password for an existing user, without printing it, and the old password stops working.

## Acceptance criteria
- [ ] `make set-password USER=<username>` reads the new password from one environment variable, hashes it with the same parameters login uses, and updates that user only. The old password then fails login and the new one succeeds.
- [ ] The password rules are the seed's (`MIN_PASSWORD_LENGTH`, and the NUL-byte rule from #144); a short or blank password is refused and nothing changes. A made-up username is refused and nothing changes.
- [ ] The command never prints the password or its hash, and a failure message names the variable, not the value.
- [ ] It works on SQLite and Postgres, and runs as the application role (it needs no table ownership).
- [ ] The README states the limit: old tokens stay valid until their expiry; rotating the token secret (restart with a new `SOCBOARD_TOKEN_SECRET`) signs everyone out.
- [ ] Existing seed and login tests pass unchanged.

## Out of scope
- Token revocation (#103), a password-reset page, any new route.

## Design

None.

## Constraints
- Files: one new `socboard/` module, `tests/`, `Makefile` (a target; protected), `AGENTS.md` Commands line (protected), `README.md`. Depends on: #144.
- Proposed tier: standard (a new command that writes credentials, no new route). Expected paths: as above.
