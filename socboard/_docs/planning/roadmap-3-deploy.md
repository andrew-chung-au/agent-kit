# Roadmap 3: Deploy

Order and status only. Acceptance criteria live on the issues; open/closed is read from the tracker. Scope and reasons: `_docs/specs.md` (§3 journey 3, §4 Deploy stories, §5 invariants, §6 Phase 2). Method: `_docs/planning/03_deployment.md` (course material for this project, followed here). Roadmap 1 (Core) is `roadmap-1-core.md`; DevOps becomes roadmap 4.

- **Status:** in progress, near the end. See "Status at 2026-11-16" under Tasks; the tracker wins where they differ.
- **Revision, 2026-11-13 (human-approved recommendations):** the task list below is superseded in detail by `_docs/planning/deploy-backlog-proposal.md` (D1 to D23). Changes: task 4 is split (Postgres support, then the append-only audit rule on Postgres); login and ingest limiting are added; task 3 gains the token secret and treats the poll interval as a build argument; #100 is a prerequisite of the image; the image build joins CI with the Dockerfile. Region: deployment `us-east-1` (the human's own account, home region `ap-southeast-2`). Wave 1 is filed: #139 (decision record), #140 (serve the build), #141 (deployed-mode settings), #142 (container bind opt-in), #143 (Postgres). Later items are filed as wave 1 progresses.
- **Goal:** SOCBoard runs from one container image with Postgres, starts with one Docker Compose command, is covered by integration and end-to-end tests, is reachable at a public HTTPS URL on AWS created by Terraform, and is deployed by CI/CD only when the tests pass.
- **Who:** **CI** = GitHub Actions can run it; **Human** = needs the human (AWS account, `terraform apply`, GitHub settings, secrets); **Eng** = the Engineer in the sandbox (no Docker, Terraform, AWS credentials or push).

## Decisions (human, 2026-11-12; recorded by task 1)

- **Terraform on AWS**, one environment, one server. Infrastructure as code makes the environment repeatable.
- **CI and Terraform.** Pull requests run `fmt`, `validate` and a read-only `plan`. `apply` runs from CI only for the server part, only on `main`, in an `infra` GitHub Environment where a named reviewer must approve and administrators are not exempt. The state bucket and the CI-access part are applied only by the human, so CI cannot widen its own permissions.
- **Bind address.** `make backend-run` stays loopback-only. The image sets an explicit opt-in; without it `SOCBOARD_HOST=0.0.0.0` still exits with an error, and a test covers the refusal. The app port is published on the host's loopback only, behind Caddy.
- **Postgres** runs as a container beside the app, with its files on the encrypted data volume and daily snapshots. A restore note goes in the runbook. A managed database (RDS) is the Phase 3 upgrade.
- **Secrets.** The ingest key, the seeded passwords and the database password live in one Secrets Manager secret the human creates. In deployed mode the app refuses to start if one is missing. The human hands reviewers their credentials out of band, not in the README.
- **URL and TLS.** A hostname derived from the server's Elastic IP through a public wildcard-DNS service, with Caddy issuing the certificate automatically (a real contact address or none). While testing, use the certificate authority's staging endpoint or another wildcard-DNS service to stay under rate limits.
- **Cost.** No stop schedule in this phase. Budget notifications at half, 80 percent and the full limit; `terraform destroy` when idle. Revisit in Phase 3.
- **Roadmap name:** `roadmap-3-deploy.md`, because number 2 is the ponytail trial.

## SOCBoard's Deploy design, and why

- **One small server running Docker Compose.** SOCBoard is one image plus Postgres; one server keeps cost and moving parts low for a single environment.
- **One image.** FastAPI serves the built SPA, so there is no second web server container. Caddy in front only terminates TLS and proxies to the app.
- **Remote state in a private, versioned, encrypted S3 bucket.** State holds resource details and must survive the laptop. The bucket is created first with local state, then state is moved into it.
- **Keyless CI through GitHub OIDC.** Separate roles for plan (read-only), apply and deploy, each trusted only for this repository and a named GitHub Environment. Trust uses the repository's numeric ids so a renamed or recreated repository cannot reuse a role.
- **Access through AWS Systems Manager only.** No SSH key and no port 22; the security group opens 80 and 443. CI deploys by sending a command through Systems Manager.
- **Images in the public GitHub Container Registry**, pushed with the workflow's own token. The repository is public, so the host needs no registry login.
- **Persistent data on its own encrypted EBS volume with scheduled snapshots**, holding the Postgres files.
- **Requirements that follow from SOCBoard itself:**
  - In deployed mode the app refuses to start if any secret is missing; there is no default password.
  - `/api/health` stays database-free (`openapi.yaml`), so start order uses the Postgres health check.
  - Postgres must keep exactly one owner under simultaneous claims (spec §5).
  - The public deployment holds synthetic data only (spec §5, §7).
  - Every cloud resource carries the tag `project=socboard`, and IAM conditions use it.
  - Nothing is proven until a real apply. Eng cannot run `plan` or `apply`, so CI runs `fmt` and `validate` and the human runs the first apply. Mark AWS-specific details unverified (`VERIFY:`) in the Terraform issues.

## Tasks, in order (D-labels; the issue text is in `_docs/planning/deploy-backlog-proposal.md` and the draft files beside it)

**Status at 2026-11-16** (read from `origin/main` and the tracker; it goes stale, the tracker wins)

- **Done, applied and checked on the real systems:** D15 state bucket, D16 CI access, D17a instance IAM and budgets, D17b server, D17c bootstrap, #256 hardened bootstrap, D19a first apply (#207), D19b re-apply (#236), #266 prod Caddy site and data folder (applied 2026-11-16, record pending in #266), #268 prod access (code merged; the maintainer's re-apply pending). The results are in `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`.
- **Done in code:** D1 to D14 (app, Postgres, image, Compose, integration and browser tests, image publish), D20 deploy script (#237 stage a), D21 smoke check, D22a deploy to dev (#238, its workflow is a proposal the maintainer applies after the first deploy), D24, #261, #271, #281.
- **Next, in order (each names the event that ends its wait, `.kiro/steering/real-dependencies-only.md`):**
  1. #314 (deploy script points Postgres at `/srv/socboard-data/postgres`): must merge before the first deploy.
  2. **D20 first deploy to dev** (#237 stage b, the maintainer's run): after #314 merges. Unlocks the Deployment criterion.
  3. Apply #238's workflow and set `DEPLOY_INSTANCE_ID` (now `i-071fe10ec49fbbbe5`) and `DEPLOY_URL`: after the first deploy. Unlocks CD to dev.
  4. #268 re-apply of `iam-and-budgets/` and `ci-access/`, with the plan role's `ssm:DescribeDocumentPermission` fix: after that fix merges.
  5. #267 (deploy script `dev`/`prod` parameter) and #269 (manual promote with rollback), then one promote run: unlocks the manual production deploy.
  6. #240 (D23 runbook and teardown): after the first deploy, so its facts are real.
- **Not needed for the rubric, kept at low priority:** #209 (read-only plan on pull requests), #307, #239 (D22b, deferred), #218. Step 9 (the snapshot check) blocks nothing.
- **Lanes:** see the table in `_docs/planning/deploy-coordination.md`. DevOps (Phase 3) runs in parallel from `roadmap-4-devops.md`.

Order and status only. An item with an issue number is filed; open or closed is read from the tracker. The earlier 20-task list is replaced by this one (changes and reasons: the proposal, sections 2 and 9). No item starts before the human approves its issue.

- **Before and beside:** #22 (the last Core task) and #104; #100 (CI Python pin), #144 (NUL-byte password), #107 (audit guard simplification) and #131 (frontend follow-ups) are prerequisites named below.
- **Groomed, waiting for the human's approval (2026-11-13; each carries the `[groomed]` title prefix and a `PM:` comment with its body hash):** #139 (D1), #140 (D2), #142 (D4), #100 (CI Python pin) and #144 (NUL-byte password). #141 (D3) and #143 (D5a) wait for #104 and are not groomed yet.
- **D0** Dev-container Postgres service: a human sitting between issues, before D5a (`_human-tasks/2026-11-13T1500Z-human-task-orchestrator-d0-dev-container-postgres.md`).
- **D1** (#139) Record the Deploy decisions. First; unlocks D5a onward and the Terraform lane.
- **Lane A, application:** **D2** (#140) serve the built frontend; **D3** (#141) deployed-mode settings (after #104 and #22's variable list); **D4** (#142) container bind opt-in; **D5a** (#143) Postgres driver, schema and CI job (needs D0, D1, #104, #100); **D5b** Postgres test fixtures; **D6a** Postgres append-only triggers; **D6b** guard review (after #107; before D20); **D7** single ownership on Postgres; **D10** one container image and a CI build; **D11** Compose stack (needs #22); **D12** integration tests against Compose (needs #22); **D13** end-to-end browser test (needs #131); **D14** CI: build, integration, E2E and image push.
- **Lane B, hardening (after D3 and #144):** **D8** login attempt limiting; **D9** ingest rate limiting.
- **Lane C, infrastructure (the human applies):** **D15** state bucket; **D16** CI access roles; **D17a** (#162) instance IAM, budgets and the daily snapshot schedule; **D17b** instance, network and volume; **D17c** bootstrap and Caddy; **D18a** CI format and validate (after D15 only); **D19** first apply (human); **D18b** CI plan (after D19).
- **Join:** **D21** smoke check (before D20); **D20** deploy script and first deploy (needs D6a, D6b, D7 to D9, #144, D14, D17c, D19, D21, #22); **D22a** deploy from CI; **D22b** Terraform apply from CI; **D23** deploy and teardown runbook; **D24** reset a seeded user's password.
- **Needs #22:** D11, D12, D13 (via D11), D20. Everything else can start without it.
- **Needs the human:** D0, D1 (approve), D4, D10, D11 and D21 (protected files), D15 to D17c (apply), D19, D20 (first run), D22a and D22b (variables, Environment approval), D23 (teardown).
- **Draft bodies:** wave 1 in `deploy-draft/wave-1-issue-drafts.md` (filed); wave 2 (D6a, D6b, D8, D9, D10, D15, D16, D17a to D17c, D18a, D18b, D21, D24) in `deploy-draft/wave-2-issue-drafts.md` (not filed); D11 to D14, D19, D20, D22 and D23 are outlines in the proposal.
- **Spec notes pending the human:** A (token secret in the secrets invariant) and B (poll interval is set at build): `deploy-draft/spec-notes-a-b.patch`.

- **Not in this phase:** separate dev and production environments, promotion and rollback (DevOps, `_docs/planning/04_devops.md`); metrics, tracing, alerting; managed or replicated database, autoscaling, load balancing, high availability; custom domain; scheduled server stop; SSH access; synthetic alert generator and Lead reassignment (Should-haves); Target Enhancements. Login attempt limiting and ingest rate limiting are in this phase (D8 and D9; spec §4 Deploy stories).
- **Archive when:** the public URL serves the app, the Compose `make` target starts the full system, `terraform plan` on `main` shows no changes after the human's apply, and a passing push to `main` deploys without manual steps.
