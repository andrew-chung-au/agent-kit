# Planning 2026-10-22: submission and showcase tracks

Tool: Claude Code (cloud session), branch `claude/tender-volta-wiq6xv`.

## What was asked

After the AWS setup guide, the human asked which deployment approach is easiest and fastest for the final project, compared the original plan with a cut-down one, and asked to structure the work as a submission track (meet the criteria for submission) plus a later CV showcase track. The human then chose Terraform, an on-demand demo with about $0 standing cost, and a possible portfolio "Launch demo" button.

## Decisions (human, this session)

H1 two tracks, showcase kept as its own file; H2 Terraform instead of CloudFormation; H3 one server for dev and prod, deploy and roll back by image tag; H4 GHCR instead of ECR; H5 `sslip.io`, no domain; H6 observability, alert and responder in local Compose for submission; H7 n8n and the other committed-scope features move to the showcase track. Full table in `_docs/roadmap-submission-draft.md`.

## What was done

- `_docs/roadmap-submission-draft.md` (temporary): phases S0-S5 with tasks, done-when and score estimates, a cutoff rule, the changes from the Tier B/C draft, and the documents to update before plan review.
- `_docs/roadmap-showcase.md` (kept separate): items X1-X9 with dependencies, rough cost and design notes for the on-demand demo and the Lambda trigger.
- `_docs/aws-setup.md`: status line says it is being revised for H2-H5.
- Filed #93: merge the submission and Tier B/C drafts into `_docs/roadmap.md` (showcase stays separate) and apply H2-H7 to `architecture.md`, `tasks.md`, the protected spec, `aws-setup.md` and `plan-summary.md` before step 14.
- Neither roadmap edited; no README change (the step 13 session edits it).

## Verification

`make verify`: PASS WITH WARNINGS. The one warning is `BASE` equal to `HEAD` (uncommitted, docs-only change); 62 tests passed, type check passed, no test files changed.

## Open

- The submission deadline is the human's to manage, by the human's direction; the drafts record no date and tell agents not to plan against one.
- H7's spec change needs a proposed diff and the human's approval (#93 item 9).

## Permission review

Created #93 through the GitHub MCP tool (issue creation, at the human's request); `git push -u origin claude/tender-volta-wiq6xv` (cloud-session exception). Both are writes to the record (keep asking). Nothing read-only or risky to propose.
