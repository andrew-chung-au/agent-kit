# AWS setup for the human

The human's how-to for the AWS and GitHub steps behind the deployment work (the deployment tasks 17, 18, 21 and 22 and the email task 37 in `_docs/tasks.md`). It is instructions to follow in order, written from experience hosting earlier apps on EC2. It is not a record of progress.

The agents write the Terraform files and the GitHub Actions workflows. You own the AWS account, its credentials, the secrets, the first `terraform apply` and teardown. Agents never hold AWS credentials, never run `terraform apply` and never see a secret value (`_docs/architecture.md`, Security boundaries). You apply Terraform from your own machine as your admin identity; CI has no AWS key and only assumes the OIDC roles, whose trust policies refuse pull-request and other-branch runs.

Design decisions behind it: Terraform, one server for dev and prod, GHCR, `sslip.io` (`_docs/architecture.md`, Deployment and A36), and the local Compose stack for observability, the alert and the responder during submission (A34). Sources: `_docs/architecture.md` (Deployment, Security boundaries, Routing and notifications, assumptions A26, A36 and A37) and tasks 17, 18, 21 and 37. Where this guide and `architecture.md` differ, `architecture.md` wins and the difference is a defect here. AWS, GHCR, Let's Encrypt and Terraform behaviours, prices and console paths are marked `VERIFY:`: check them in the documentation or console when you do the step.

Everything in "Submission steps" is needed for the submission. "Future-development extra steps" is optional and starts only after the submission is in (`_docs/roadmap-future.md`, Rule).

For a single prioritised view of **all** human action (this AWS runbook plus the per-issue verification runs, merges and sweeps), see `_docs/human-tasklist.md`; it indexes back to the steps here.

## What gets built, and by whom

Three Terraform modules, all in one region, every resource tagged `project=vuln-triage`. Terraform is the tool; OpenTofu runs the same files. Installing it is a new tool the build task asks you about first.

| Module | Contents | First applied by | Changed by |
|---|---|---|---|
| State bucket | One S3 bucket holding Terraform state (VERIFY: S3-native state locking, so no lock table) | You, once, from your machine | You |
| Deploy role | GitHub OIDC provider (or the account's existing one) and the dev and prod deploy roles | You, once, from your machine | You (CI never changes IAM) |
| Server | One EC2 instance running the `dev` and `prod` Compose projects behind a TLS reverse proxy, with an Elastic IP, a data volume, snapshots and a nightly stop | You, once, from your machine | You for infrastructure; CI only deploys images onto it |

Images live in GHCR (GitHub's container registry), public, so the server pulls them without a credential (VERIFY). Hostnames come from the server's IP through `sslip.io`, so there is no domain to buy. Dev deploys automatically on a push to `main` when tests pass; production deploys only from a manual workflow you approve.

Not used, on purpose (cost): load balancers, NAT gateways, RDS, ECS/EKS, CloudFront, an AWS container registry. No IAM user or long-lived access key for CI: GitHub Actions assumes the roles through OIDC.

## Checklist

| # | Step | Track | When | Time (rough) |
|---|---|---|---|---|
| 1 | Account hygiene | Submission | Before anything else | 10 min |
| 2 | Pick the region | Submission | Before the bootstrap | 5 min |
| 3 | Budget alert | Submission | Before anything is applied | 10 min |
| 4 | Hostnames and TLS | Submission | Decide the name form before the server is applied; record the hostnames after the first apply | 10 min |
| 5 | How you reach the server | Submission | Before the server is applied | 5 min |
| 6 | GitHub settings | Submission | Environment before task 21; variables after step 7 | 15 min |
| 7 | Bootstrap: state bucket, deploy role, server | Submission | Start of task 17, after review | 45 min |
| 8 | Submission secrets | Submission | Before the first dev deploy; prod ones before the first production deploy | 20 min |
| 9 | Email sending route | Submission | Before task 37 runs on AWS | 15 min plus the verification wait |
| 10 | Nightly stop and cost tag | Submission | With the server | 10 min |
| 11 | Teardown | Submission | When you decide to end the deployment | 30 min |
| S1 | Future-development extra secrets | Future development | After the submission is in | 20 min |
| S2 | Grafana and responder on AWS (X3) | Future development | After the submission is in | see `roadmap-future.md` |
| S3 | On-demand demo and Launch button (X1, X9) | Future development | After the submission is in | see `roadmap-future.md` |

Steps 1-4 need no repository code. Steps 4 and 5 are decisions (for step 4, the name form; the hostnames themselves exist only after the first apply creates the Elastic IP); record them in the issue for task 17. You, not an agent, perform the first deploy (task 17).

# Submission steps

## 1. Account hygiene

- Root MFA: already enabled. Confirm the root user has no access keys (IAM → Security credentials) and don't use root for anything below except billing settings that need it.
- Sign in day to day as an admin identity with MFA: an IAM Identity Center user (preferred) or an IAM user. VERIFY: Identity Center is free and available in your chosen region.
- If you use the AWS CLI on your machine, it uses that admin identity (for example `aws configure sso`), not root keys. Terraform uses the same identity when you run it.
- List old resources from earlier EC2 projects before starting (EC2 → Instances, Elastic IPs, Volumes, Snapshots; or Resource Explorer, VERIFY). A forgotten Elastic IP or volume is easy to mistake for this project's. This project creates its own VPC resources or uses the default VPC (decided in task 17); it does not reuse old security groups or key pairs.

## 2. Pick the region

One region for the state bucket, the server and the secrets. Options:
- `ap-southeast-2` (Sydney): lowest latency if you and the reviewers are in Australia.
- `us-east-1` (N. Virginia): usually the lowest prices and the most services; some account-wide settings live there anyway (billing alerts, VERIFY).

Check that Amazon SES is available in the region (step 9; VERIFY) and whether the region can hold the verified sender identity if it differs from the server's. Record the region as the repository variable `AWS_REGION` (step 6).

## 3. Budget alert

Create a monthly AWS Budgets cost budget with email alerts at 50 %, 80 % and 100 %, before any stack is applied (`_docs/architecture.md`, Cost controls). The amount and its upkeep are yours (A37). VERIFY: Budgets console path and pricing.

## 4. Hostnames and TLS (`sslip.io`)

The dashboard uses session cookies marked `Secure`, so it needs HTTPS. There is no load balancer or CloudFront, so no AWS Certificate Manager certificate (VERIFY). The certificate comes from Let's Encrypt, obtained by the reverse proxy on the server.

You do not buy or configure a domain. The server has an Elastic IP, and `sslip.io` resolves a hostname containing that IP back to it, for example `dev.203-0-113-10.sslip.io` for dev and `app.203-0-113-10.sslip.io` for prod (VERIFY: the exact `sslip.io` name forms). Ports 80 and 443 are open to the internet (80 only for the certificate challenge and the redirect to 443).

Points to know:
- Keep the Elastic IP. If it is released, the hostnames change, and every URL in the README with it. It is kept across the nightly stop.
- Let's Encrypt limits how many certificates it issues per name (VERIFY: rate limits). Every `sslip.io` user shares the `sslip.io` name, so you may hit a limit you did not cause (VERIFY: whether `sslip.io` is treated as its own registered domain). If issuance fails, the fallback is named in `_docs/architecture.md` (A36): first the Let's Encrypt staging certificate for the demo (the browser shows a warning you accept once; the `Secure` cookie still works), then another hostname service such as `nip.io` with the same issuance path.
- The proxy (Caddy, Traefik or nginx with certbot) is chosen in task 17 and needs your approval as a new image.

Record in the task 17 issue: the two hostnames once the Elastic IP exists.

## 5. How you reach the server

AWS Systems Manager Session Manager only; there is no SSH port and no key pair (`_docs/architecture.md`, Deployment; VERIFY). The instance role gets the `AmazonSSMManagedInstanceCore` policy. You connect from the console or with the Session Manager plugin for the CLI (VERIFY). The deploy workflow may also use SSM Run Command to run the deploy on the server (VERIFY). Sessions are logged.

SSH would be an architecture change (CI would need it too); propose that in the plan review first, not here.

You rarely need a session: deploys run from the workflow, and logs are in the local stack's Loki.

## 6. GitHub settings

Repository Settings, in `andrew-chung-au/vuln-triage`:
1. **Environments → New environment `production`.** Add yourself as a required reviewer, and restrict deployments to the `main` branch. VERIFY: environment protection rules are available for this repository's plan. The prod role's trust policy only accepts tokens from this environment, so no workflow can deploy to prod without your approval.
2. **Secrets and variables → Actions → Variables** (variables, not secrets: none of these is a secret): `AWS_REGION`, and after step 7 `AWS_DEV_ROLE_ARN` and `AWS_PROD_ROLE_ARN` (the role ARNs from the deploy role module's outputs). Nothing AWS goes in the repository files; the account ID only appears in these variables.
3. **Packages:** after the first image push, set each GHCR package (backend, frontend, responder) to public so the server can pull it without a credential (VERIFY: where the visibility setting lives and that a repository workflow can keep pushing to a package).
4. **Rulesets:** the `main` ruleset from `_docs/cloud-sessions.md` section 4.2 refuses direct pushes and needs a pull request. The responder relies on that (it may open pull requests, never push to `main`). Check it is Active.

## 7. Bootstrap: state bucket, deploy role, server

CI can't create the roles it uses to log in, and Terraform needs somewhere to keep its state, so you do this once by hand, from your machine, as your admin identity. The agent writes the Terraform in task 17; you apply it after reviewing the diff.

1. Install Terraform on your machine. VERIFY: the version the files require.
2. Create the state bucket: apply the bootstrap files with local state, then move the state into the bucket as the runbook instructs (VERIFY: the exact `init` step).
3. Before applying the deploy role, check for an existing GitHub OIDC provider: IAM → Identity providers → `token.actions.githubusercontent.com`. An account can have only one provider per URL (VERIFY). Tell the agent whether one exists, so the files reuse it (a variable) instead of failing to create a second.
4. Review the deploy role module before you apply it:
   - Trust policy: audience `sts.amazonaws.com`; subject limited to this repository, with `environment:dev` for the dev role (limit that GitHub environment's deployment branches to `main`) and `environment:production` for the prod role (the `sub` claim carries GitHub's immutable ids, `repo:<owner>@<owner id>/<repo>@<repo id>:environment:<name>`, confirmed from CloudTrail on 2026-10-25; the ids are the `github_owner_id` and `github_repo_id` variables). No wildcard over other repositories or pull requests.
   - Dev role: run the dev deploy on the server only. Prod role: run the production deploy only. Neither can change IAM, Terraform state or the server's configuration, or read secrets.
   - Every resource tagged `project=vuln-triage`.
5. Run `terraform plan`, read it, then `terraform apply` for the deploy role and then the server. Copy the two role ARNs from the outputs into the GitHub variables (step 6), and note the Elastic IP for step 4.

## 8. Submission secrets

Runtime secrets live in AWS Secrets Manager, read at container start by the instance role (`_docs/architecture.md`, Security boundaries, secrets table; VERIFY). You create the values; agents see only the secret names, which the Terraform files and `.env.example` list.

Derivation: the secrets table (Security boundaries) lists what exists; the credentials table says who holds each; submission keeps only what the deployed backend needs. Per environment (`dev` and `prod`):

| Secret | Holder | Source row |
|---|---|---|
| Database password | The backend only | Credentials: "Database credential" |
| Repository read-only token | The backend only | Credentials: "Repository read-only token (backend)". GitHub fine-grained token, `contents: read` on the pilot repositories (VERIFY) |

Not in AWS for submission:
- No email credential exists: SES uses the instance role (step 9). Do not create SMTP credentials.
- The Grafana admin password, the observability stack's tokens (including the Grafana Viewer token), the responder's `RESPONDER_API_TOKEN`, and the responder's LLM key and GitHub token belong to the local Compose stack for submission (A34). They go in the local git-ignored `.env`, which agents never read.
- The backend LLM key, the n8n, MCP and tracker tokens and SMTP credentials are future development (S1).

Rules:
- Generate passwords and tokens with a password manager or `openssl rand -base64 32` on your machine. Never paste a value into an issue, a chat with an agent or a file in the repository.
- Cost: Secrets Manager charges per secret per month (about $0.40, VERIFY). One JSON secret per environment keeps that low.
- Alternative: SSM Parameter Store `SecureString` parameters have no per-parameter charge at the standard tier (VERIFY). Using it instead is an `architecture.md` change: propose it at task 17.

Create the dev secrets before the first dev deploy and the prod ones before the first production deploy.

## 9. Email sending route

The route is settled (`_docs/architecture.md`, Routing and notifications; task 37; A26): the backend sends the top-tier owner notification by calling the Amazon SES API with the server's instance role, from one verified sender address. `sslip.io` names cannot carry the DNS records SES domain DKIM needs, so you verify an address, not a domain. No SMTP credentials are created or stored. Development and tests send to MailHog and need nothing from you.

Your actions:
1. In the chosen region (step 2), SES → Identities → Create identity → Email address, for the sender address. Open the verification email and click the link (VERIFY: console path).
2. New accounts start in the SES sandbox, which allows mail only to verified addresses (VERIFY). Create an identity for each demo recipient address the same way and click each verification link.
3. Tell the agent the sender address and the recipient addresses. They are not secrets. Give it nothing else: no key, profile or credential.

The instance role's SES permission is send-only, limited to the one verified sender identity and conditioned on the sender address. A send from any other address is refused by SES. VERIFY: the IAM action (`ses:SendEmail`, and whether `ses:SendRawEmail` is also needed), the resource form (the verified identity ARN), the `ses:FromAddress` condition key, the free allowance and sending limits, and the SES region that holds the identity.

## 10. Nightly stop and cost tags

- **Nightly stop.** The server is stopped each night (Cost controls); the schedule is in the Terraform (VERIFY: EventBridge Scheduler). Start the server from the console (EC2 → Instances → Start) before working or demoing. Both environments stop together, so switch the nightly stop off (the Terraform variable, apply, or disable the schedule in the console) while graders may visit, and switch it back on afterwards. A stopped server has three effects: the backend runs a catch-up refresh and re-scan at start if the last run is over 24 hours old; an automatic dev deploy to a stopped server is skipped and reported in the workflow summary, so re-run the skipped workflow after you start the server; and anyone visiting the URL sees nothing. The Elastic IP is kept, so the hostnames do not change (VERIFY: an Elastic IP stays associated with a stopped instance).
- **Cost allocation tag.** After the first apply, activate the `project` tag in Billing → Cost allocation tags (VERIFY), so Cost Explorer can show this project's spend alone. Tags take about a day to appear.

## Production promotion and rollback (task 18)

Production is **never** deployed automatically. A merge to `main` deploys only the `dev` project (task 21); you promote a tested image to production by hand, and only you can (the `production` GitHub environment has you as the required reviewer). Both environments run on the one server as two Compose projects behind one Caddy: `dev` at `dev.<eip>.sslip.io`, `prod` at `app.<eip>.sslip.io` (A36). Nothing is rebuilt during a promotion — it deploys an image tag that already exists in GHCR.

Prerequisites (once):
- The `production` environment exists with you as the required reviewer (step 6.1) and the `AWS_PROD_ROLE_ARN` variable is set (step 7).
- The production secret `vuln-triage/prod` exists in Secrets Manager with at least `POSTGRES_PASSWORD` (step 8). The deploy reads it on the server with the instance role; the workflow carries no secret.
- The server is running (promotion to a stopped server is skipped and reported, like the dev deploy; start it first).

**Promote a release:**
1. GitHub → Actions → **deploy** → **Run workflow** (this is the `workflow_dispatch` trigger).
2. Leave **"Image tag to promote"** blank to promote the tag currently running in dev (the default — the image that has been serving dev), or paste a specific `YYYYMMDD-HHMMSS-shortsha` tag from an earlier deploy-log entry.
3. The run pauses for your review on the `production` environment. Approve it. The `deploy-prod` job then deploys the `prod` project with that tag and records the promoted tag and each image's digest in the run summary (the deploy log).
4. Confirm `https://app.<eip>.sslip.io` answers and shows the promoted build. The run summary (and the earlier build run for that tag) names the digest; `dev` and `prod` run the same digest when you promote dev's current tag.

**Roll back:** re-run the same workflow and paste the **previous** tag — read it from an earlier "prod promotion" entry in the deploy log (each entry names its tag and digests). The promotion is the rollback; there is no separate path. A deploy that fails to pull leaves the running containers in place, so a bad tag does not take production down (`_docs/architecture.md` Deployment → Rollback). Alembic migrations are backward compatible for one release, so the previous image runs on the current schema.

Notes:
- The deploy log is the workflow run summary; keep the tag and digest from each promotion so a rollback has a previous tag to use.
- The demo-defect gate `P-FLAG-GONE` (task 29) runs in this same production workflow; its step is added by task 29, not here.

## Pilot seed data (task 22)

Once the dev environment answers, register the pilot assets so real findings appear. They are registered **through the API** (`POST /assets`, US-1), never written to the database — so the dashboard, scan worker and audit trail all run as in production.

1. **Fill in the seed list.** Edit `deploy/pilot-seed.json`: replace the `REPLACE_ME` entries with a few of your own GitHub repositories (set each `ownerName`/`ownerEmail`/`criticality`/`internetFacing`), keep the OWASP NodeGoat entry. `repositoryUrl` must be exactly `https://github.com/<owner>/<repo>`.
2. **Juice Shop's lockfile (A41), checked 2026-10-26.** `juice-shop/juice-shop` commits no `package-lock.json` (no yarn, pnpm or shrinkwrap lock at the root either), so its entry was dropped and the NodeGoat fallback is now the entry to use. NodeGoat's `package-lock.json` has `lockfileVersion` 2 and a `packages` key, which the parser accepts; this was read from the GitHub page and the first lines of the raw file, not run through the parser, so the first registration is the real test (`VERIFY:`). The script still skips any entry carrying a `_use_only_if_juice_shop_has_no_package_lock` flag, but the seed file no longer has one.
3. **Run the seed script** against the dev URL, signed in as a `security lead` (only a security lead may register; the password is prompted or read from `VT_SEED_PASSWORD`, never passed on the command line):

   ```
   python deploy/seed-pilot.py --base-url https://dev.<eip>.sslip.io/api --username <security-lead>
   ```

   The base URL **ends in `/api`**: the dashboard host serves the single-page app, and only `/api/` is forwarded to the backend (with the prefix stripped). Without `/api` the script's login gets a 404 or 405 and says so.

   It is stdlib-only (no dependency to install) and prints each registered asset with its id and scan status. Re-running it registers the assets again, so run it once (or clear the earlier assets first).
4. **Check (the acceptance):** on the dev dashboard each asset shows a scan status and, once its first scan finishes, at least one finding. The repository URLs stay out of telemetry (A38) — the seed script is a plain API client and emits no spans, metrics or logs.

## Public reviewer account (A14)

Peer reviewers are anonymous and cannot be contacted, so the README publishes one shared login for the **dev** URL (`reviewer` / `vt-reviewer-demo`, a `security lead`). That is a decision the human made on 2026-10-25: a public password is accepted so reviewers can use the live app at all. Create it once the dev environment answers (after step A9), from a Session Manager session on the server (no SSH). `VERIFY:` the command; it has not been run on the server.

```
sudo -i
cd /opt/vuln-triage/dev
printf '%s\n' 'vt-reviewer-demo' | docker compose -f /opt/vuln-triage/app/compose.yaml -f compose.deploy.yaml --project-name dev --env-file .env exec -T backend python -m vulntriage.manage create-user --username reviewer --display-name "Public reviewer (demo)" --email reviewer@example.com --role "security lead"
```

Change the username or password in the README and in this command together. Do **not** create this account on production.

What a public `security lead` login allows, and what keeps it acceptable:

- **Anyone can register an asset.** The URL must be `https://github.com/<owner>/<repo>`, so it cannot reach an internal address, but each registration starts a scan that uses the server's read-only GitHub token and its rate limit. Accepted: the token is read-only and public-repo only.
- **Anyone can send mail to any address if mail is on.** An asset's `ownerEmail` is where a top-priority finding is emailed. While this account is public, keep mail off on dev (leave `MAIL_TRANSPORT` unset) **or** keep the SES account in the sandbox (never request production access), so only your verified demo recipient can ever receive anything. Do not enable real delivery on dev while the account is public.
- **Anyone can lock the account.** Five failed sign-ins in 15 minutes lock a username for 15 minutes, so a stranger can keep `reviewer` locked out. Accepted; the local demo in the README is the fallback.
- **The data can be changed or filled with junk.** Keep nothing real on dev: only public repositories and fictional owners. The pilot seed (A13) can be re-run after clearing the dev database if it is vandalised.
- **Rotate or remove after grading:** delete the account, or tear down (step 11). The password is unique to this project; do not reuse it anywhere.

## 11. Teardown

Human-only. Follow `_docs/architecture.md` Deployment → Teardown, in this order:
1. Export anything to keep (a prod database dump).
2. Run `terraform destroy` for the server module, then the deploy role module (VERIFY: destroy order and that the Elastic IP is released).
3. Delete the EBS snapshots, the Secrets Manager secrets without a recovery window (VERIFY) and the budget. Delete the GHCR images in the GitHub package settings if wanted.
4. Last, empty and delete the state bucket (VERIFY: a versioned bucket needs all versions removed).

5. Check that no resource tagged `project=vuln-triage` remains (VERIFY: Tag Editor or Resource Groups search) and that the next bill shows no running charges.

Then release any Elastic IP left, and check Cost Explorer filtered by `project=vuln-triage` a few days later.

# Future-development extra steps

Nothing in this section is needed for the submission. Start it only after the submission is in. Items are described in `_docs/roadmap-future.md`.

## S1. Future-development extra secrets

Each is future development and `VERIFY:` for the exact name, which `architecture.md` does not fix:
- LLM API key for the backend brief (X4), in AWS with the backend's other secrets. The architecture's secrets table lists "LLM keys" without a future-development mark; the credentials table (backend key is future development, responder key is local) is followed here.
- `N8N_API_TOKEN`, `MCP_API_TOKEN` and the tracker token (X5, X6).
- SMTP credentials, only if n8n sends mail (X6).
- For Grafana and the responder on AWS (S2): the Grafana admin password, the responder's LLM key and GitHub token, `RESPONDER_API_TOKEN` and the Grafana Viewer token, moved from the local `.env` into AWS secrets.

The step 8 rules apply.

## S2. Grafana and responder on AWS (X3)

Observability and the responder run on AWS only as future-development item X3 (a separate observability server). Grafana would then need a public hostname and TLS as in step 4. Details and cost: `_docs/roadmap-future.md`.

## S3. On-demand demo and Launch button (X1, X9)

See X1, X9 and their design notes in `_docs/roadmap-future.md`. Nothing is set up from this guide.

# Reference

## Rough monthly cost of the submission server

On-demand prices in `us-east-1`, orders of magnitude only (VERIFY in the AWS Pricing Calculator for your region; Sydney is typically 10-25 % higher).

| Item | Count | Approx. per month |
|---|---|---|
| `t3.medium` server running 24/7 (VERIFY: size) | 1 | about $30 |
| EBS gp3 root and data volumes, 20-30 GB | 2 | about $2-3 each |
| Public IPv4 address (Elastic IP; charged whether or not the server runs) | 1 | about $3.60 |
| Secrets (one JSON secret per environment) | 2 | about $0.40 each |
| State bucket, snapshots, data transfer, email, GHCR (public images, VERIFY) | | a few dollars |

Running all the time: roughly $40 a month. With the nightly stop (about 12 hours a day): roughly $25 a month, because the volumes, snapshots and the Elastic IP are still charged while the server is stopped. After teardown (step 11) the standing cost is about $0: only the state bucket, a few cents, stays until you delete it.

Future-development additions (VERIFY: all prices):
- A second server for X2: VERIFY its price.
- A separate observability server for X3: VERIFY its price.
- LLM API usage for X4: VERIFY the provider's price.
- A Lambda and its function URL for X9: within the free tier (VERIFY).
- X1 on-demand demo: about $0 standing cost while the demo is down (`roadmap-future.md`).

## Decisions for the human

Record each answer in the task 17 issue before it starts:

| # | Decision | Recommendation |
|---|---|---|
| 1 | Region | **Decided 2026-10-25: `us-east-1`** (lowest prices; reviewers are in the US and EU). The Terraform defaults and examples now say so |
| 2 | Existing GitHub OIDC provider in the account | Tell the agent; reuse it if present |
| 3 | Secrets store | Secrets Manager with one JSON secret per environment, as planned |
| 4 | Verified sender address and demo recipient addresses (step 9) | One sender address you control; the route itself is settled |
| 5 | Where to apply Terraform | Your machine, as your admin identity; never CI |
