# Deploy phase: readiness, spec notes and decision questions (v3)

PM proposal only. No issue created, no tracked file edited. Replaces v2. Companion: `.scratch/roadmap-deploy-draft-v3.md`. Sources: `_docs/specs.md`, `_docs/planning/03_deployment.md` (course material), SOCBoard's code, and public documentation of Terraform, AWS, GitHub OIDC, Secrets Manager, Compose and TLS.

## 1. Definition of ready

**NOT READY.** The ruling of 2026-11-12 (Terraform on AWS) picks the method; it adds no journey and no requirements. The Deploy part of the spec has no testable stories, no journey and no stated infrastructure rule. Per `planning.md` and `process.md#backlog`, propose spec changes (section 2) and file no Deploy issues until the human approves them.

## 2. Spec notes (five; the human decides)

```
Spec note: Phase 2 (Deploy) has no user stories to derive acceptance criteria from
- Added: a "Deploy" group in §4 with Must stories, each testable:
  (a) WHEN the single container image runs with a database URL THE SYSTEM SHALL serve the SPA at `/`
      and the API under `/api` from one origin.
  (b) WHEN a browser requests a screen route such as `/cases/1` THE SYSTEM SHALL return the SPA
      entry page; WHEN a request under `/api` matches no route THE SYSTEM SHALL return the JSON
      404 `not_found`, never the SPA page.
  (c) The database is chosen by environment variable; SQLite is the local default, Postgres the deployed one.
  (d) One Docker Compose command starts the app and Postgres, and the app waits for the database and migrations.
  (e) Integration tests run against the Compose stack; an end-to-end test drives both journeys with two analysts and a Lead.
  (f) The application is reachable at a public HTTPS URL on infrastructure that Terraform creates and one documented procedure removes.
  (g) On every push to `main`, CI runs the tests, builds the image and runs integration and E2E tests; CD deploys only if all pass, with a short-lived scoped credential (GitHub OIDC); pull requests never get a deploy credential.
  (h) Infrastructure changes reach the cloud only through Terraform: a pull request shows the plan, and an apply from CI runs only on `main` after the human approves it.
- Changed: none
- Removed: none
- Why: `planning.md` requires requirements that acceptance criteria can be derived from; §6 says Phase 2 is detailed by a spec revision first. (h) follows from the ruling.
```

```
Spec note: no journey covers the deployed system, and the Deploy users are not named
- Added: in §2, an Operator (holds the cloud account and secrets, approves applies, can tear down) and the visitor who opens the public URL. In §3, journey 3 "Deploy -> Public URL": the Operator proposes a change by pull request; CI shows the Terraform plan; the Operator merges; CI passes; CD deploys; a visitor opens the HTTPS URL and logs in as a seeded user; an alert ingested with the key appears in the queue within N = 5 s.
- Changed: none
- Removed: none
- Why: `planning.md` asks for at least one end-to-end journey; the 5 s invariant means more when checked where users are.
```

```
Spec note: Deploy has no scope boundary on environments, hosting or tooling, and no Deploy non-goals
- Added: to §6 Phase 2, "one environment, one server, one Postgres, on AWS, created by Terraform"; to §7 non-goals: second environment and promotion, rollback (Phase 3), autoscaling, load balancing, managed or replicated database, custom domain, high availability, SSH access.
- Changed: none
- Removed: none
- Why: the course brief treats a single-instance deploy as proof of concept and defers the rest to DevOps; without a boundary, Deploy issues can grow into Phase 3.
```

```
Spec note: invariants for a public, Terraform-managed deployment are missing
- Added: to §5: (1) secrets (ingest key, seeded passwords, database password) come from the cloud secret store at deploy time and never appear in the repository, image, frontend bundle or Terraform state outputs; (2) the public deployment holds synthetic data only (restates §7); (3) single ownership under concurrent claims holds on Postgres; (4) no long-lived cloud key exists in the repository or GitHub secrets; (5) CI cannot change its own permissions; the definitions of CI's roles are applied by the human; (6) in deployed mode a missing secret stops the app at start-up.
- Changed: "on any supported database" -> "(SQLite and Postgres)"
- Removed: none
- Why: a public URL with seeded accounts needs a rule for how passwords are set (§2 says seeded and hashed), and the course brief asks for scoped, short-lived credentials.
```

```
Spec note: the spec does not say what the health route proves, and server.py binds localhost only
- Added: one line in §6 Phase 2: container start order uses the Postgres health check in Compose, while `GET /api/health` stays database-free (`openapi.yaml`); and a statement of who may run the backend on a non-loopback address (question 2).
- Changed: none
- Removed: none
- Why: `socboard/server.py` refuses any host except 127.0.0.1, localhost or ::1, so a container cannot be reached without changing a security limit; the human decides.
```

## 3. Decision questions (remaining)

```
Decision needed: what may CI do with Terraform, and who applies the CI-access part?
- Context: the ruling asks for CI plan and apply. An apply role can create IAM and EC2, so a mistake or a hijacked workflow run is costly. Trust policies for jobs using a GitHub Environment use the environment form of the OIDC subject; GitHub documents a form with immutable owner and repository ids. SOCBoard's ids are 177896104 (owner) and 1446634348 (repository); not secrets, repository is public.
- Options:
  1. CI runs `fmt`, `validate` and a read-only `plan` on pull requests, and `apply` only for the server part, only on `main`, in an `infra` Environment where a named reviewer must approve and administrators are not exempt. State bucket and CI-access parts are human-applied.
  2. As 1, but CI also applies the CI-access part (CI could widen its own permissions; not recommended).
  3. CI only checks and plans; the human runs every apply.
- Recommendation: 1. It meets the ruling, keeps human approval on every apply and stops CI editing its own roles. Fall back to 3 if the apply role looks too broad.
- If you don't answer: the roadmap assumes 1.
```

```
Decision needed: may the backend bind a non-loopback address inside the container?
- Context: `socboard/server.py` refuses any host except 127.0.0.1, localhost and ::1, and `AGENTS.md` documents that as a project rule. A protected file and a security limit are involved.
- Options:
  1. `make backend-run` stays loopback-only; the image sets an explicit opt-in. Without it, `SOCBOARD_HOST=0.0.0.0` still exits with an error. The app port is published on the host's loopback only, behind Caddy.
  2. Remove the restriction.
  3. Defer (nothing can be reached).
- Recommendation: 1, with a test for the refusal.
- If you don't answer: the Dockerfile task is not proposed.
```

```
Decision needed: where does Postgres run and where do its files live?
- Context: the spec says "Postgres in place of SQLite"; the course brief prefers a managed database for real production but accepts a single instance for a proof of concept.
- Options:
  1. Postgres container beside the app, data directory on the encrypted data volume, daily snapshots.
  2. Amazon RDS: sturdier, more cost and Terraform.
  3. Defer.
- Recommendation: 1, with a restore note in the runbook; record RDS as the Phase 3 upgrade.
- If you don't answer: assume 1.
```

```
Decision needed: how are the seeded passwords and the ingest key set on a public URL?
- Context: the spec says accounts are seeded and hashed. The app must not run with weak defaults on the internet.
- Options:
  1. All three secrets (including the database password) live in one Secrets Manager secret the human creates; the app refuses to start if one is missing in deployed mode; the human hands reviewers credentials out of band.
  2. Fixed demo passwords in the README: easy for markers, but anyone can log in as a Lead and the invariant (1) no longer holds.
  3. Defer.
- Recommendation: 1.
- If you don't answer: the config task assumes 1.
```

```
Decision needed: public URL and TLS
- Context: the brief allows a reverse proxy such as Caddy for TLS. A purchased domain costs money; a hostname built from the Elastic IP through a public wildcard-DNS service costs nothing. Certificate authorities rate-limit shared names and reject placeholder contact addresses.
- Options:
  1. Wildcard-DNS hostname plus Caddy automatic certificates, with a real contact address or none; fall back to the CA's staging endpoint or another wildcard-DNS service while testing.
  2. A domain the human owns, DNS pointing at the Elastic IP.
  3. Defer.
- Recommendation: 1.
- If you don't answer: assume 1.
```

```
Decision needed: stopping the server at night to save cost
- Context: the server is one instance (about $25 to $40 a month for a medium size; a smaller size may fit, unverified). A stop schedule adds a "server stopped" branch to deploys and can break a demo URL.
- Options:
  1. No schedule in this phase; budget notifications at three thresholds (half, 80 percent and the full limit); `terraform destroy` when idle.
  2. A stop schedule switched by a variable.
- Recommendation: 1. Revisit in Phase 3.
- If you don't answer: assume 1.
```

```
Decision needed: the roadmap file name
- Context: `_docs/planning/roadmap-2-ponytail-trial.md` already uses number 2.
- Options: 1. `roadmap-2-deploy.md`; 2. `roadmap-3-deploy.md`, DevOps becoming 4; 3. slug-only `deploy.md`.
- Recommendation: 2.
- If you don't answer: the draft keeps the requested name and the conflict stays.
```

## 4. Checked facts that affect the draft
- Docker, Terraform and AWS are unavailable in the Engineer's sandbox (`AGENTS.md`, Environment): the Engineer writes `.tf` files; CI validates; the human applies first.
- A new top-level `terraform/` folder needs the human's approval and a Layout line in `AGENTS.md`; a pinned Terraform version in CI is a new tool.
- `pyproject.toml` has no SQLAlchemy or Postgres driver yet; the Postgres task carries a dependency approval. A browser-test tool is also a new dependency.
- `openapi.yaml` `servers: - url: /api` and `app.py` `API_PREFIX = "/api"` agree, so same-origin serving needs no contract change; the SPA fallback must not catch `/api/*`.
- The repository is public, so image packages can be public and the server pulls with no registry credential.
- AWS-specific details are unverified until the human's first apply; mark them `VERIFY:` in the Terraform issues.
