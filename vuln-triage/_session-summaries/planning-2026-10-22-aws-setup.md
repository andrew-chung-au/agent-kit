# Planning 2026-10-22: parallel-work analysis and AWS setup guide

Tool: Claude Code (cloud session), branch `claude/tender-volta-wiq6xv`.

## What was asked

1. Another session started roadmap step 13 (`_docs/plan-summary.md`). The human asked which work in `_docs/roadmap.md` and `_docs/roadmap-tiers-b-c.md` can run independently without conflict, without editing either roadmap.
2. The human set #48 aside (cloud Docker depends on remaining credits), said they already have an AWS account with credits and EC2 experience, and asked for documentation in `_docs/` of what else is needed and the steps.

## What was done

- Analysis (chat only, no file): safe beside step 13 are #73 and the human-side prerequisites; #75, #63 and applying Tier B/C decisions D1/D2/D6/D7 need coordination (they change step 13's inputs; land them after `plan-summary.md` and before step 14); not now: roadmap merge, #31, Milestone A code issues, a rubric re-audit, and the "Later" list without the human's go-ahead.
- Added `_docs/aws-setup.md`: who deploys each stack, a 12-step checklist (account hygiene, region, credits, a budget that excludes credits, domain and TLS, instance access, GitHub `production` environment and variables, bootstrapping `vt-ci-iam`/`vt-ecr` with a review checklist, secrets, SES, nightly stop and tags, teardown), a rough cost table, and seven decisions for the human. All AWS details carry `VERIFY:`.
- Appended an entry to `_docs/ai-usage-log.md`.

## Not done, on purpose

- No README index link to the new guide: the step 13 session edits the README's planning document list. Add the link after step 13 merges.
- Neither roadmap changed. The Tier B/C roadmap's "AWS account" prerequisite can point to `_docs/aws-setup.md` when it is merged into `_docs/roadmap.md`.

## Found, not changed

- `_docs/roadmap.md` line 137 is a leftover `=======` conflict marker (also noted in the Tier B/C session summary). The step 13 session can remove it with its check-in.
- `_docs/architecture.md` Deployment does not say who first deploys `vt-ci-iam` and `vt-ecr` (CI can't create the roles it logs in with), or that an account may already hold a GitHub OIDC provider. The guide covers both as human steps; task 17 should reflect them.

## Verification

`make verify` (frontend tests, type check, whitespace, weakened tests): PASS WITH WARNINGS. The one warning is `BASE` equal to `HEAD` (uncommitted, docs-only change); no test files changed.

No QA or rubric-auditor review; the guide is for the human, and nothing in it was run against AWS.

## Permission review

No approval requests in this session.
