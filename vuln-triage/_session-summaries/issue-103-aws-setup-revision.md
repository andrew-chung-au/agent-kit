# Issue #103: Revise aws-setup.md: submission steps vs showcase steps, settled email route, derived secrets list

**Date:** 2026-10-22
**Spec version:** 4fa7a55

## What changed and why

#97 rewrote `_docs/aws-setup.md` for Terraform before the email route was decided and before the human's guidance that the guide be a how-to, not a status record. The Engineer rewrote it as a how-to: a Track column and 11 submission steps, then a separate "Showcase extra steps" section (showcase secrets, the AWS-hosted Grafana pointer, the n8n and MCP pointer), with the cost table under "Reference". The only fact stated as true is that root MFA is already enabled. The budget is one short human-owned step with no amount. Server access is Session Manager only, matching `architecture.md`. The submission AWS secrets are the database password and the backend's repository read-only token per environment; the Grafana, observability and responder items stay in the local `.env`; the showcase secrets are the backend LLM key, the n8n, MCP and tracker tokens, and the moves to AWS for the hosted Grafana. The email route is the settled SES API through the instance role with one verified sender, plus the sender and demo-recipient verification steps, and no SMTP credentials. QA failed the first commit (7fa6de1) because the guide cited `roadmap.md` for "Deploy phase S3" and "H2-H5", which exist only in the draft file #93 retires. The fix (9890d28) names the decisions inline, adds the teardown check that nothing tagged `project=vuln-triage` remains, says the human performs the first deploy, and clarifies that hostnames are recorded after the first apply. QA passed the recheck.

## Files created or modified

- `_docs/aws-setup.md` (7fa6de1, 9890d28)
- This file (separate commit)

## Decisions made by the human

- 2026-10-22: the guide is a how-to, not a status record; nothing in it is marked done except that root MFA is enabled; the budget is the human's to manage and carries no amount.
- 2026-10-22: approved the PM's plan to split submission from showcase steps and to apply the settled email route.

## Mismatches with the spec or design docs

- `_docs/architecture.md` line ~311 lists "LLM keys" in the secrets table without a showcase mark: folded into #93's clean-up.
- `_docs/plan-summary.md` A37 says "nightly stop of dev and observability" where the architecture stops the one server: folded into #93's clean-up.
- `_docs/tasks.md` task 17 omits the existing-GitHub-OIDC-provider case that `architecture.md` and the guide cover: folded into #93 (human approved the one-sentence edit).
- For plan review: `architecture.md` does not say which backend the local responder reads. For submission the responder stays in local Compose with its token in the local `.env`; if it ever reads the deployed backend, the AWS secret set grows.

## Commands to validate

**Verify:** `make verify` (QA: PASS, 62 tests passed, type check pass, whitespace pass, no test files changed)
**Assert clean:** `make assert-clean` (PASS after each QA run)

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Permission review

PM, Engineer and QA comments for #103 say none required on the merits. The PM's tracker writes matched ask rules.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create` and `gh issue edit 93` (PM, ask rules in `opencode.json`); `make issue-close N=103` (orchestrator, matches `make issue-close*`)
- Risky (propose denying): none

## Interruptions

none. QA's first run failed #103; the fix and recheck followed the normal loop.

## Unrelated problems noticed but not fixed

- The guide's S1-S3 labels could be confused with the roadmap's S-phases (QA note).

## Follow-ups for the next session

- #93 (roadmap merge, milestones, README links, check-ins, the clean-ups above); then close #92.
- Settle at plan review which backend the local responder reads.
