Reviewer: FAIL at 84e99fd
Documents reviewed: `_docs/project-brief.md`, `_docs/rubric.md`, `_docs/planning-process.md`, `_docs/specs.md`, `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/testing.md`, `_docs/tasks.md`, `_docs/plan-summary.md`
Read as context only (not reviewed, not counted): `_docs/roadmap.md`, `_docs/aws-setup.md`, and `_docs/roadmap-showcase.md` (read to understand the showcase split)
Not yet written: none

Reviewer session: Claude Code, model sonnet (claude-sonnet-5-5), a fresh session with no part in writing the plan. The plan was written by OpenCode and mostly Claude Code (claude-opus-5-5). This is a different model but not a different tool, which is a recorded exception (human decision, 2026-10-22, issue #108) to the "different tool" text in `_docs/agent-team.md`.

Scope notes:
- Human-decided items are not reported as gaps: A16-A18, Q8, Q10, roadmap decisions H1-H7. Still open and acceptable because recorded: roadmap D4 and D5, spec Q2-Q4, A41/Q11. The Tier A/B/C and S1-S5/B1-B6/C1-C9 vocabularies are intentional.
- H7 moved the LLM brief, MCP server and n8n out of submission scope. The brief's success criteria on the brief guardrail, GitHub issue and MCP are therefore not met at submission. This is a decided scope change, not a finding.
- `openapi.yaml` was read line by line to line 1349 (all 21 operations, security schemes, parameters, responses and the first schemas). Lines 1350-2309 (schemas) were checked by search only (`signalsChanged`, ownerless, held, `dueAt`). The operation count (21) and the consumer split in `api.md` match the paths in the file.
- The counts in `plan-summary.md` (113 register entries) and the 21-operation figure were recomputed by hand and are consistent.

## Findings

1. [High] `specs.md` E8 and Data flow vs `architecture.md` § Routing and notifications, `tasks.md` tasks 10 and 37, `testing.md` `I-SIGNALS`/`S-SIGNALS`: the E8 "signals changed" notice (a `risk accepted` finding whose signals escalate: "the owner and security lead are notified once") is submission scope. It is not marked Showcase in the spec, and `testing.md` lists `I-SIGNALS` and `S-SIGNALS` as submission cases. No submission component or task sends it. Architecture says the `signals changed` job is delivered by n8n (showcase), and task 37 sends only the `top tier` job. The security-lead contact (`SECURITY_LEAD_NAME`/`SECURITY_LEAD_EMAIL`, A28) is also only in showcase task 35, yet E8 needs it.
   Why it matters: a spec behaviour and two submission tests have no owner, so the plan cannot meet its own acceptance criteria as written.
   Suggested fix: either extend task 37 and the delivery design to send `signals changed` jobs to the owner and the configured security lead (and move the security-lead contact into submission), or have the human move the E8 notice to Showcase in the spec and drop `I-SIGNALS`'s notice assertion and `S-SIGNALS` from submission. (If the human chooses the second option, this finding drops to Low.)

2. [Medium] `tasks.md` § Milestone A, task 15 and § Coverage summary note; `architecture.md` § Rubric enablement (Application row); `roadmap.md` B2 (context): Tier A is stated as 12 points, but Application scores 2 only if the app "runs locally with a single command". The only task that supplies that clause is task 15 (Compose, Tier B). No Tier A task adds a single local start command (the Makefile has `frontend-start` only, and backend start is not specified anywhere).
   Why it matters: the Tier A total is 11 at best until task 15, and the "S1 alone scores 12" claim in the roadmap is not supported by the tasks.
   Suggested fix: add a one-command local run (SQLite, no Docker; for example `make dev` for backend plus frontend) to a Tier A task, or restate Tier A as 11.

3. [Medium] `tasks.md` tasks 11 and 12: no task replaces the frontend mock service with a real HTTP client, or fixes how the SPA reaches the backend (Vite dev proxy or CORS in development, static serving or reverse proxy in Compose). Task 11 says "builds the React screens over the single services layer", but the screens and the mock service already exist (roadmap steps 9, #34, #45).
   Why it matters: the Application criterion needs "frontend talks to backend", and this is the only link between them; today nothing owns it.
   Suggested fix: state in task 11 (or a new Tier A task) that it implements the real `Services` over `fetch` with the cookie and `X-Requested-With` header, removes the mock from production wiring, and says how dev and Compose route `/` to the API.

4. [Medium] `tasks.md` task 13 vs tasks 4-12; `testing.md` § Integration tests (T-A2) and plan-summary `testing.md:T-A2`: the `tests/fixtures/` directory, `make record-fixtures`, the `U-NET`/`I-NET` network guard and the growth of `make test` to include backend tests are all created in task 13, which depends on 10. Tasks 4-12 each name `U-*`/`I-*` checks "in `make test`" and tasks 5 and 6 need stubbed OSV/KEV/EPSS fixtures and the outbound-call guard. T-A2 puts the first fixture capture in task 13.
   Why it matters: tasks 4-12 cannot be handed to someone who has not read task 13, and their checks have no harness.
   Suggested fix: move the test harness, network guard and first fixtures into task 4 or a new task before task 4 (task 1 could carry the harness), and leave task 13 as the CI-facing consolidation.

5. [Medium] `tasks.md` tasks 10, 25, 28, 29 vs `testing.md` § Showcase scope and counts, § Telemetry, § Responder: submission tasks name Showcase test IDs as their checks. Task 10 checks `I-JOBS`, `I-AUTH-N8N` and `I-AUTH-MCP`; task 25 builds `T-JOURNEY` (n8n report call); tasks 28 and 29 check `P-DEMO`. Testing defines the submission versions as `T-JOURNEY-BE` and `P-DEMO-BE`, and says the Showcase cases are not counted. Task 10 also implements 13 operations in one task, including the showcase n8n/MCP/digest endpoints (needed only because the conformance test compares all 21 operations).
   Why it matters: the checks cannot be run as named, the case counts in `testing.md` disagree with the tasks, and task 10 is not one session of work.
   Suggested fix: rename the checks in tasks 25, 28 and 29 to the `-BE` cases; in task 10 name the submission cases only and either split the task or say the showcase operations are contract-only stubs returning the documented responses.

6. [Medium] `tasks.md` task 37 (check) vs `testing.md` `I-OWNER-NOAWS`, `I-OWNER-SEND`: task 37's check is "a `make test` run delivering the notification to MailHog with no AWS credentials". MailHog is a Compose container and the sandbox has no Docker; `testing.md` itself says `make test` uses an in-process fake sink and leaves "whether `make test` uses an in-process SMTP stand-in or the case runs in `postgres-integration`" to task 37.
   Why it matters: the acceptance check is not runnable where `make test` runs, and the open choice sits inside the check.
   Suggested fix: change task 37's check to the in-process sink under `make test` plus the MailHog delivery in `make test-compose`, and close the `VERIFY:` in testing.

7. [Medium] `architecture.md` § Observability (A40, "a job's `traceparent` is never null") vs A40 itself and `testing.md` `I-OWNER-SEND`: A40 makes instrumentation a no-op when no Collector endpoint is set, and `I-OWNER-SEND` runs in `make test` (no Collector) and asserts `notification.deliver` is a child of the job's stored `traceparent`. A no-op tracer produces invalid (all-zero) span contexts, so the stored `traceparent` would be null or invalid.
   Why it matters: two stated invariants conflict in the Tier A/test configuration, and the `Traceparent` pattern in the contract would reject an all-zero value.
   Suggested fix: say that the SDK always creates real span contexts (in-memory exporter when no endpoint is set) and that only export is a no-op.

8. [Medium] `architecture.md` § Deployment (A37 nightly stop, A36) vs task 38, task 21 and `aws-setup.md` step 10 (context): the server is stopped every night. Task 38's scheduler runs at 06:00 UTC inside the backend; if the server is stopped there is no run and no catch-up rule (only KEV has "at backend start if no copy exists"). Task 21's automatic dev deploy runs through SSM on the server, which fails while it is stopped. Graders visiting a stopped server see nothing (the guide only says to keep it running "while graders may visit").
   Why it matters: US-7 "daily refresh without manual action", CD "automatically deploys" and Deployment "reachable at a public URL" can each fail for a reason the plan created.
   Suggested fix: add a catch-up rule (run the refresh and re-scan at start if the last run is over 24 hours old), say what a deploy does when the server is stopped, and state the schedule window or make the nightly stop opt-in during grading.

9. [Medium] `specs.md` E2/US-8 and `api.md`/`openapi.yaml` (no asset update operation): there is no way to set or change an asset's owner, criticality or internet-facing flag after registration, and no rule releases a notification held as `held: ownerless` or `held: owner email missing` once an owner is known. Release is specified only for `held: configuration error` ("sent once the contact is set").
   Why it matters: an ownerless P1 finding can never be delivered, and a misregistered asset can only be fixed by re-registering (which would create a second asset).
   Suggested fix: add an owner/attributes update operation (and its audit entries) or state that assets are immutable in the MVP, and specify when held owner jobs are released.

10. [Medium] `architecture.md` § US-14 alert rule, `testing.md` T-A3 and `A-GAP`: the rule uses `noDataState: Alerting`. The metric `vt_top_tier_notification_overdue{finding_id,tier}` has one series per job, so when no jobs exist (a fresh system, or the backend is down) the query returns nothing and the rule would fire with no `finding_id` label. That contradicts "a successful notification fires none" and would wake the responder with no finding. How long a `sent` job keeps emitting 0 (series cardinality) is also unspecified.
   Why it matters: the alert could fire on a healthy empty system, and "exactly one alert naming the finding" cannot hold.
   Suggested fix: emit a constant series (for example a global `0` gauge) so NoData only means the backend is down, name what that alert says, and set how long a `sent` job's series is kept.

11. [Medium] `architecture.md` § Data model (`NotificationJob`) vs § US-14 alert rule and `testing.md` `A-TIER`: the alert metric's `tier` label is "the tier recorded when the job was created", but `NotificationJob` has no `tier` field. `testing.md` calls it "#56 Spec note 1" and says the test uses it "once the model adds it". Task 3 builds the data model from architecture as written.
   Why it matters: the model built in task 3 will lack a field that tasks 26/27 need.
   Suggested fix: add `tier` to the `NotificationJob` row in the data model.

12. [Medium] `architecture.md` A34 and `roadmap.md` C7/C8 (context) vs `tasks.md` tasks 2, 28, 29: "a recorded alert-to-fix run as the evidence" is how On-Call Agent, Alerting and Observability are shown for submission (the demo runs locally, H6), but no task produces or links the recording, and the roadmap says the final re-audit and README close-out "have no task". Task 28's check runs only with `RESPONDER_MODE=stub`; the responder runtime is unchosen (R3).
   Why it matters: the highest-value criteria (24 points) depend on evidence nobody is assigned to make, and a stub run does not show an agent fixing anything.
   Suggested fix: add a close-out task (recorded drill with the real responder, README public URL/one-command start/rollback sections, rubric re-audit) with yes/no checks, and say which runtime task 28 uses for the recorded run.

13. [Medium] `architecture.md` § Security boundaries (prompt injection, A31) and `testing.md` `S-NOTIFY`: URL defanging is specified as `https://` becoming `hxxps[:]//`. It does not cover `http://`, `ftp://`, `www.` or bare domains, which mail clients also auto-link, nor `mailto:` or similar schemes. The spec says every URL in advisory text is shown as inert text.
   Why it matters: a plain-text owner email can still carry a clickable attacker link, which is exactly the flow the spec table guards.
   Suggested fix: define the rule as "any scheme, `www.` or domain-shaped token is defanged" and add those cases to `S-FIXTURE`.

14. [Medium] `testing.md` `P-DEMO-BE`, § CI jobs (`responder` job), `tasks.md` task 29: `P-DEMO-BE` includes "CI deploys to dev" inside a pull-request Compose job, but architecture says pull-request workflows never receive an AWS role, and the roadmap (C7, context) says the drill has "no dev deploy". Task 29's `P-FLAG-GONE` is described both as a test that blocks promotion until the defect path is gone and as part of a `make test-compose` run that must be green; while the demo defect exists the test would be red (or the test is "gone or refused", which is not one yes/no check).
   Why it matters: the check cannot pass as written, and either the demo or the green CI gate has to give.
   Suggested fix: remove the dev deploy from `P-DEMO-BE` (the local run restarts the stack) and define `P-FLAG-GONE` as a single check that runs only on the production-promotion workflow.

15. [Medium] `architecture.md` A4 (background worker and job table), Security boundaries (operator command to create accounts), A28 (`/health`) vs `tasks.md` and `openapi.yaml`: no task description builds the worker/job table that task 4's asynchronous first scan, task 38's scheduler and task 37's delivery all rely on (the register points A4 at task 10, which does not mention it). No task builds the operator command that creates dashboard users (no sign-up), which the dev, prod and demo environments need. `/health` is used by A28 and by Compose health checks (roadmap B1, context) but is not in `api.md` or `openapi.yaml`, so the conformance test would fail on it.
   Why it matters: three needed components have no owner, and one conflicts with the "every endpoint is in the contract" test.
   Suggested fix: name each in a task (worker in task 4 or 10, user command in task 9, `/health` added to the contract or excluded from the conformance test).

16. [Low] `architecture.md` § Deployment (A36), `aws-setup.md` step 4 (context): HTTPS is a hard dependency, because the session cookie is `Secure`, and the certificates come from Let's Encrypt under the shared `sslip.io` name (rate limits `VERIFY:`). No fallback is named if issuance fails.
   Why it matters: a refused certificate breaks login on dev and prod, and with it the Deployment criterion.
   Suggested fix: name the fallback now (for example an `nip.io` name or a staging-certificate demo path).

17. [Low] `architecture.md` § Security boundaries (owner notification): the email is `text/plain` with labelled fields, but nothing says how the subject and headers are built from OSV-sourced ids and package names (untrusted).
   Why it matters: CRLF in a value placed in a header is a header-injection route.
   Suggested fix: state that header values are built from the finding id and tier only, and that CR/LF is rejected.

18. [Low] `specs.md` US-1 vs `api.md` § Authorization: US-1 says a security lead registers assets, but `POST /assets` and `POST /assets/{id}/rescan` accept any signed-in user; role rules are defined only for risk acceptance.
   Why it matters: any asset owner can register arbitrary repositories (using the backend's repository token) and trigger scans.
   Suggested fix: state the intended role rule for both operations.

19. [Low] `architecture.md` § Prioritisation, worked example: the six findings contain no `P2` case (KEV listed on a non-exposed asset, or EPSS at or above T on an exposed asset), and nothing at exactly T.
   Why it matters: the rule most likely to be implemented wrongly (≥ T, KEV on a non-exposed asset) has no worked check beyond the unit test list.
   Suggested fix: add one `P2` finding and one finding at EPSS exactly 0.10.

20. [Low] `plan-summary.md` § Stage 6 checklist ("Every risk has a mitigation"): says "Top risks has 9 rows", but the table now has R1-R10.
   Why it matters: a stale count in a checklist that claims to be verified.
   Suggested fix: update to 10.

21. [Low] `planning-process.md` Stage 5 ("then the LLM brief, MCP server and n8n, which are committed scope") and § "The Reviewer reads": the first sentence is stale after H7 (those are Showcase), and the Reviewer list omits `_docs/openapi.yaml`.
   Why it matters: the process document contradicts `tasks.md` and the review prompt on what the plan contains.
   Suggested fix: update both lines when the file is next edited.

22. [Low] `_docs/docker-runbook.md` line 5 and `_docs/rubric-evidence.md` lines 29 and 45: stale "roadmap step 16" mentions. Known and accepted by the human; listed only for completeness.
   Why it matters: a dead cross-reference.
   Suggested fix: change to T3/#31 when those files are next touched.

23. [Low] `api.md` § Showcase scope, `openapi.yaml` `startSignalRefresh`/`startScheduledRescan`: the two operations are unmarked (submission) but their only listed credential is `n8nAuth` (Showcase), and no n8n token is provisioned for submission. The backend scheduler calls the code in-process, so in submission scope no caller can use these endpoints.
   Why it matters: they are dead operations that the conformance test and task 10 must still build and secure.
   Suggested fix: note in the contract that they are reachable only in the showcase build, or give them a submission credential.

24. [Low] `testing.md` § CI jobs: the `telemetry`, `alert` and `responder` jobs all run `make test-compose`.
   Why it matters: without a per-job selector each job runs the whole Compose suite three times, which also hides which job covers which case.
   Suggested fix: give `make test-compose` a case selector or use three targets.

## Questions for the human

- E8 (finding 1): do you want the "signals changed" notice and the security-lead contact in submission scope, or should the spec move that clause to Showcase?
- Held ownerless P1 findings (A39): the brief says an alert fires when a top-priority finding does not reach its owner. Under A39 a held (ownerless or name-only owner) P1 finding never fires the alert, and no frontend wire field shows "notification held" (only ownerless can be inferred from null owner fields). Is that intended, given there is also no way to set an owner later (finding 9)?
- Tier A total (finding 2): do you prefer a Tier A single-command local run, or restating Tier A as 11?
- Responder runtime (R3, finding 12): should the runtime be chosen before task 28 is filed, since the rubric evidence depends on a real run, not the stub?
- Plan feasibility: R6 puts the estimate at 26-30 hours against the course's roughly 20 hours. I did not count this as a finding because it is recorded as the human's call, but tasks 9, 10, 28 and 29 look larger than one session (QA noted this in the roadmap, step 11).
