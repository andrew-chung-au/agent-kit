Reviewer: PASS at 46dd403
Documents reviewed: `_docs/project-brief.md`, `_docs/rubric.md`, `_docs/planning-process.md`, `_docs/specs.md`, `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/testing.md`, `_docs/tasks.md`, `_docs/plan-summary.md`
Read as context only (not reviewed, not counted): `_docs/roadmap.md`, `_docs/aws-setup.md`
Not yet written: none

Reviewer session: OpenCode subagent, model `opencode/deepseek-v4.1-flash-free`, a fresh session with no part in writing the plan. The plan was written by OpenCode and mostly Claude Code (`claude-opus-5-5`). This is a different tool and model, so it meets the different-tool requirement; it is not the Claude Code sonnet session named in the 2026-10-22 handoff (subagents inherit the main session model), and the review does not claim that exception.

Scope notes:
- This review cites the first review, `_docs/reviews/2026-10-22-plan-review.md`, and re-checks its findings by name below. It does not re-report decisions the human settled on 2026-10-22: E8 is Showcase with the `signalsChanged` flag staying in submission; A16-A18, Q8 and Q10; all 14 Mediums fixed; Tier A keeps 12 points and `make dev`; `PATCH /assets/{id}` makes 22 operations; the nightly stop has the 24-hour catch-up and grading switch; the alert uses a constant `0` gauge and `NoData` means the backend is down; `/health` is outside the contract and excluded by name; task 10 is one task with contract-only Showcase stubs; task 39 exists; the responder runtime is chosen before task 28; A39 stays; and R6 is accepted and still to be re-estimated.
- Still open and acceptable because recorded: spec Q2-Q4, A41/Q11, roadmap D4/D5, and the responder runtime itself (A34).
- `openapi.yaml` was read in full this run (2421 lines), including the schemas after line 1350. The 22-operation count in `_docs/api.md` matches the paths and operations I read. The safety rule "Tier A uses no Tier B or C component" in `_docs/architecture.md` § Rubric enablement is treated as a plan invariant.

## Run 1 findings re-checked
1. [High] E8 "signals changed" notice — fixed in scope. `_docs/specs.md` E8 now says the notice and the security-lead contact are Showcase, `_docs/testing.md` keeps `I-SIGNALS` as the submission flag and moves the notice to Showcase `I-SIGNALS-NOTICE`, and `_docs/tasks.md` gives the notice to task 35. The residual two-job design defect is current finding 2.
2. [Medium] Tier A single command — fixed: task 11 adds `make dev`; architecture § Rubric enablement and the coverage note record it.
3. [Medium] real frontend services and API routing — fixed in task 11 (real `Services` over `fetch`, mock removed from production, Vite proxy, Compose proxy, AWS proxy).
4. [Medium] test harness and fixture ordering — fixed: task 1 has the harness, network guard and empty fixtures; task 4 has the first fixtures and `make record-fixtures`; task 13 consolidates.
5. [Medium] submission tasks naming Showcase checks — fixed: task 10 uses contract-only stubs and names submission checks; tasks 25, 28 and 29 use `T-JOURNEY-BE`/`P-DEMO-BE`; task 29 uses `P-FLAG-GONE`.
6. [Medium] task 37 check runnable under `make test` — fixed: task 37 uses the in-process sink in `make test` and MailHog only in `make test-compose`.
7. [Medium] no-op tracer invalid traceparent — fixed by A40 (only export is a no-op; the SDK always creates real contexts).
8. [Medium] nightly stop, catch-up and stopped-server deploy — fixed by A37, task 38's catch-up, task 21's skipped-and-reported deploy and the grading switch.
9. [Medium] no way to set an owner or release a held job — fixed by `PATCH /assets/{id}`, the release rule, task 9 and `I-ASSET-UPDATE`; the new test-placement problem is current finding 1.
10. [Medium] alert firing on an empty system — fixed by the constant global `0` heartbeat series and the `NoData`/human-email rule.
11. [Medium] `NotificationJob.tier` absent — fixed in architecture § Data model and task 3.
12. [Medium] no close-out task or recorded drill — fixed by task 39; the runtime is chosen before task 28 (still open and acceptable).
13. [Medium] URL defanging too narrow — fixed in architecture § Security boundaries (any scheme, `www.`, domain-shaped tokens) and `S-FIXTURE`.
14. [Medium] `P-DEMO-BE` dev deploy and `P-FLAG-GONE` conflicting roles — fixed: no dev deploy in the drill; `P-FLAG-GONE` runs only in the production-promotion workflow.
15. [Medium] worker/job table, user command and `/health` — fixed: worker in task 4, user command in task 9, `/health` outside the contract with the exclusion in task 14.
- Low 17, 20, 21, 23 and 24 are fixed; Low 18 is fixed under finding 9; Low 22 is fixed in `_docs/docker-runbook.md` and deliberately left in `_docs/rubric-evidence.md` (the auditor's file); Low 19 is deliberately left.

## Findings

1. [Medium] `_docs/testing.md` § Integration cases (`I-ASSET-UPDATE`), `_docs/tasks.md` task 9 (check) vs tasks 10 and 37, and `_docs/architecture.md` § Rubric enablement: task 9's check names `I-ASSET-UPDATE`, but that case requires "the backend delivery worker, in-process fake mail sink" (testing line 123) and asserts that a released held job's "delivery sends exactly one email". Task 9 depends on task 8; no NotificationJob exists until task 10, and the delivery worker is task 37 (Tier C, after task 24). Task 9's own description says "the delivery of task 37 then sends them". Task 37's check does not include `I-ASSET-UPDATE`, so the case never runs after the delivery exists.
   Why it matters: a Tier A task's acceptance criterion cannot pass as written, and the plan's invariant that Tier A uses no Tier B or C component no longer holds for task 9.
   Suggested fix: split `I-ASSET-UPDATE` — keep the role, audit, re-score and release-state assertions in task 9, and move the "delivery sends exactly one email" assertions (ownerless and name-only release) to task 37's check, or add `I-ASSET-UPDATE` to task 37 after the delivery exists.

2. [Medium] `_docs/architecture.md` § Routing and notifications (idempotency) and § Data model (`NotificationJob`), `_docs/specs.md` E8, `_docs/testing.md` `I-SIGNALS-NOTICE`, `_docs/tasks.md` task 35, and `_docs/api.md`/`_docs/openapi.yaml` `NotificationJob.recipient`: E8 promises one notice to the owner and one to the security lead, and testing/task 35 implement that as two `signals changed` jobs in one lifecycle. But the idempotency key is `(lifecycle id, kind)`, unique, for `signals changed`, so the two jobs of the same kind collide; and the contract says the `signals changed` recipient is the owner, not the security lead.
   Why it matters: the Showcase E8 notice that was moved out of submission still cannot be created or represented as written, and `I-SIGNALS-NOTICE` cannot pass.
   Suggested fix: make the `signals changed` key `(lifecycle id, kind, recipient)` (or otherwise include the recipient), and update the `NotificationJob.recipient` descriptions in `_docs/api.md` and `_docs/openapi.yaml` to allow the security lead for `signals changed`.

3. [Low] `_docs/api.md` § Enums (`NotificationJobKind`) and `_docs/openapi.yaml` `NotificationJobKind`: `issue close` is unmarked, and the Showcase content lists omit it, although architecture § Routing and notifications and task 34 build it only as the Showcase `close-tracker-issue` workflow.
   Why it matters: a contract reader can mistake a Showcase-only job kind for submission scope; the Showcase marking is inconsistent with the data model.
   Suggested fix: mark `issue close` as Showcase in both descriptions and add it to the Showcase content list.

4. [Low] `_docs/tasks.md` task 10 (description) vs task 23 and the dependency chain: task 10 says it creates "a `traceparent` from the `notification.enqueue` span", but task 23, which depends on task 10, is the task that "instruments ... the `notification.enqueue` span"; task 10's check does not verify the traceparent.
   Why it matters: the task that must store the span's traceparent is ordered before the task that adds the instrumentation, so task 23 has to retrofit task 10's job creation or task 10 has to add tracing early.
   Suggested fix: say task 10 creates the `notification.enqueue` span with the SDK (or move the traceparent requirement and its test to task 23, leaving task 10 with job creation only).

## Questions for the human
- `_docs/testing.md` `I-OWNER-HOLD` says for "Ownerless (E2) and name-only owner (A21): the notification is held, the ownerless flag is set". The spec defines ownerless as both owner name and email unset, so should the ownerless flag be set only for the ownerless case and not for a name-only owner?
- Is the E8 two-job design intended to use one `signals changed` job per recipient (which needs the key change in finding 2), or is one job with a combined recipient intended?
