# Reviewer brief: SOCBoard Deploy plan

You are reviewing a plan, not code. Read-only: change no file and post nothing to the tracker. Reply in the format at the end.

## The project in three lines

SOCBoard is an alert triage case manager for a security operations centre (synthetic data only): FastAPI and SQLAlchemy backend, React and TypeScript frontend, SQLite locally. Core (ingest, scoring, queue, claim, workflow, notes, audit trail) is built; one task, #22 (integration tests and a one-command local run), remains. The Deploy phase puts it on a public HTTPS URL: one container image, Postgres, Docker Compose, Terraform on AWS (`us-east-1`, the owner's own account), and CI/CD with keyless GitHub OIDC credentials. The work is graded against `_docs/planning/rubric.md` (12 criteria, 24 points, 10 to pass).

## Where to read (branch `deploy-backlog-proposal`, not yet merged to `main`)

In this order:
1. `_docs/planning/deploy-backlog-proposal.md`: the plan. Read all of it: the review of the old roadmap (section 2), the effect of #22 (3), order and lanes (4), the 23 issue drafts D1 to D23 (5), the human's decisions (6) and two spec notes (7).
2. `_docs/planning/roadmap-3-deploy.md`: the earlier roadmap, with the seven human decisions and the design reasons. Superseded in its task list by the proposal.
3. `_docs/specs.md` sections 3 to 7: the Deploy stories, the invariants (section 5) and the non-goals (section 7).
4. `_docs/planning/deploy-draft/wave-1-issue-drafts.md`: full bodies for D1 to D5. These are filed as issues #139 to #143.
5. `_docs/planning/03_deployment.md`: the course process the plan follows.

Code to check claims against (on the same branch): `socboard/app.py`, `socboard/server.py`, `socboard/database.py`, `socboard/migrations/versions/0001_initial_schema.py`, `socboard/audit_guard.py`, `tests/conftest.py`, `.github/workflows/verify.yml`, `Makefile`.

## What to judge

1. **Soundness of the risky choices.** For each, say agree, disagree or unsure, with a reason:
   - Postgres keeps the audit trail append-only with trigger functions in the migration (D6); a restricted database role is deferred.
   - Login and ingest limits are counted in the process (D8, D9), reset on restart, and are a known limit.
   - Frontend settings are image build arguments, not runtime settings (D3, D10).
   - FastAPI serves the built frontend; no separate web server (D2).
   - CI deploys over AWS Systems Manager with three OIDC roles (plan, apply, deploy); Terraform apply from CI only for the server part, only on `main`, after a named reviewer approves; the CI-access part is applied by hand (D16, D18, D22).
2. **Order and dependencies.** Is anything in the wrong order, missing a dependency, or blocked on something not listed? Are the two lanes (application and Terraform) really independent?
3. **Missing work.** Anything a public deployment of this app needs that no item covers (examples to consider: backups and restore, secret rotation, image pull failure, log handling, a crash loop, TLS renewal failure).
4. **Security model.** Weak points in the secret handling (one cloud secret, no long-lived cloud key), the OIDC trust, the single public server, and seeded accounts on a public URL.
5. **Rubric fit.** Does completing D1 to D23 plausibly earn the Containerization, Deployment and CI/CD criteria? What would fall short?
6. **Sizing.** Items that are too large to be one issue, or too small to be worth one. Tier (Standard or Heavy) that looks wrong.

## Known gaps: do not report these

- D6 to D23 are outlines (goal and headline criteria), not full bodies. They are written after wave 1 is under way. Judge their scope, not their wording.
- `roadmap-3-deploy.md` has a revision note but its task list is not rewritten; the proposal is the current plan.
- The AWS and Terraform details are unverified until the owner's first apply; they are marked `VERIFY:` for that reason. No one has run Terraform, Docker or Postgres in this environment (the planning sandbox has none of them).
- Phase 3 (separate dev and prod, observability, alerting, the on-call agent) has no plan yet by design: the spec says to detail it when Deploy is done.
- Spec notes A and B (section 7 of the proposal) are not yet applied; `_docs/specs.md` is a protected file the owner commits.
- Issue bodies refer to items as D1 to D23; the roadmap will map them to issue numbers. Issues #139 to #143 are filed but not groomed or approved.
- #139's body says "account and organisation" in one place; the account is the owner's own and its home region is `ap-southeast-2`. The deployment region `us-east-1` is decided.
- Several choices are already decided by the owner and are listed in section 6 of the proposal and in `roadmap-3-deploy.md` ("Decisions"). You may disagree with them, but say so as a disagreement, not a missed item.

## How the project works (so findings fit)

Agents (PM, Engineer, QA, Reviewer) work issues one at a time under the rules in `AGENTS.md` and `_docs/agent-kit/process.md`. Protected files (`Makefile`, `AGENTS.md`, `agent-kit.conf`, `pyproject.toml`, `_docs/specs.md`, CI workflows) change only with the owner's approval of the exact diff. No agent can push to `main`, run Terraform, or reach AWS; the owner runs the first apply and approves each issue.

## Reply format

1. **Verdict:** ready to groom, ready after changes, or not ready, in one sentence.
2. **Findings:** a numbered list. For each: the item (D-number or section), the problem in one or two sentences, severity (Must fix, Should fix, Nice to have), and a proposed change.
3. **Answers** to the five judgements in "What to judge", one short paragraph each.
4. **Anything you could not check** and why.

Keep it under two pages.
