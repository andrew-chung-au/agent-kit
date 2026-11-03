# VulnTriage plan summary (Stage 6)

Status: Stage 6 deliverable, draft for review; the register, completeness counts and line locations were refreshed in the #108 stage 2 commits (plan review 1 fixes; stage 1 was `8bdb0fc`)

Sources: [`_docs/rubric.md`](rubric.md), [`_docs/project-brief.md`](project-brief.md), [`_docs/specs.md`](specs.md), [`_docs/architecture.md`](architecture.md), [`_docs/api.md`](api.md), [`_docs/testing.md`](testing.md), [`_docs/tasks.md`](tasks.md), [`_docs/roadmap.md`](roadmap.md) and [`_docs/reviews/2026-10-16-final-rubric-impact.md`](reviews/2026-10-16-final-rubric-impact.md).

## How to read

- This is **planned coverage, not evidence**. [`_docs/rubric-evidence.md`](rubric-evidence.md) is the only record of what is currently MET, PARTIAL or MISSING; no row here awards points or claims a status.
- Criterion names, order and maximum points are copied verbatim from [`_docs/rubric.md`](rubric.md) (12 criteria, 24 points, 10 to pass).
- `task N` means the `## N.` heading in [`_docs/tasks.md`](tasks.md); it is not a GitHub issue number. Issue numbers, where they exist, are cross-references only.
- Milestones A, B and C and their targets (A 12, B 19, C 24 points) are the targets in [`_docs/reviews/2026-10-16-final-rubric-impact.md`](reviews/2026-10-16-final-rubric-impact.md) §5 and [`_docs/roadmap.md`](roadmap.md) §Tier B and Tier C milestones. They are targets, not current evidence.
- Submission and future development: the submission scope is tasks 1-29, 37, 38 and 39 (decisions H2-H7: Terraform, one server for dev and prod, GHCR, `sslip.io`, observability and the responder in local Compose, the backend delivering the top-tier notification and running the schedule). Tasks 30-36 (LLM brief, MCP server, n8n) are in the "Future development (after submission)" section of [`_docs/tasks.md`](tasks.md) and are not in the rubric map. A register entry whose owner is a task numbered 30-36 is future-development scope, and no submission task depends on one.
- Duplicate coverage is explicit and allowed: a task may serve several criteria, and a criterion may need several tasks.
- In the register, keys are `file:tag` because tags repeat across files (for example `architecture.md:A1` and `api.md:A1 (#27)` are different entries). Status values are `open`, `proposed answer`, `resolved`, `deferred` and `VERIFY`. Line numbers were read after the #108 stage 2 edits and may move.

## Rubric map

| # | Criterion | Max | Tasks (`_docs/tasks.md`) | Documents (section) | Earliest milestone |
|---|---|---|---|---|---|
| 1 | Problem Description | 2 | task 2 | [`README.md`](../README.md) §The problem, §What VulnTriage does, §Expected behaviour | A |
| 2 | Product Specification | 2 | task 2 | [`_docs/specs.md`](specs.md) §User stories (acceptance line per story); [`_docs/tasks.md`](tasks.md) §Coverage summary; public [issue tracker](https://github.com/andrew-chung-au/vuln-triage/issues) | A |
| 3 | Agent Team Specification | 2 | task 2 | [`_docs/agent-team.md`](agent-team.md) §Roles and handover; [`_docs/agent-kit/process.md`](agent-kit/process.md) §Roles and §Lifecycle | A |
| 4 | Context Management | 2 | task 2 | [`AGENTS.md`](../AGENTS.md) §Where to read more; [`_docs/agent-kit/process.md`](agent-kit/process.md); [`_docs/agent-kit/team/software-engineer.md`](agent-kit/team/software-engineer.md) | A |
| 5 | Application | 2 | task 1, task 3, task 4, task 5, task 6, task 7, task 8, task 9, task 10, task 11, task 12, task 14, task 37, task 38; task 15¹ | [`_docs/architecture.md`](architecture.md) §Components, §Data model, §Rubric enablement; [`_docs/api.md`](api.md) §Endpoint table; [`_docs/tasks.md`](tasks.md) task 15 (Compose) | A |
| 6 | Testing | 2 | task 1, task 13, task 14, task 16, task 20 | [`_docs/testing.md`](testing.md) §Test levels and where they run, §CI jobs and triggers, §Traceability matrix | A |
| 7 | Containerization | 2 | task 15 | [`_docs/tasks.md`](tasks.md) task 15; [`_docs/architecture.md`](architecture.md) §Development environment, §Rubric enablement; [`_docs/testing.md`](testing.md) §Integration tests (T-A1) | B |
| 8 | Deployment | 2 | task 17, task 18, task 39 | [`_docs/architecture.md`](architecture.md) §Deployment (Terraform, one AWS server running the `dev` and `prod` Compose projects, images in GHCR, `sslip.io` HTTPS hostnames); [`_docs/roadmap.md`](roadmap.md) §Tier B (B4-B6) | B |
| 9 | CI/CD | 3 | task 18, task 19, task 20, task 21 | [`_docs/architecture.md`](architecture.md) §Deployment (Pipeline: tests on pull requests, automatic dev deploy in task 21, manual production workflow in task 18); [`_docs/testing.md`](testing.md) §CI jobs and triggers | B |
| 10 | Observability | 2 | task 23, task 24, task 25, task 39 | [`_docs/architecture.md`](architecture.md) §Observability (local Compose for submission; task 37 emits `notification.deliver`); [`_docs/testing.md`](testing.md) §Telemetry: US-13 | C |
| 11 | Alerting on User Impact | 1 | task 26, task 27, task 39 | [`_docs/architecture.md`](architecture.md) §Observability (US-14 alert rule); [`_docs/testing.md`](testing.md) §Alerting: US-14 | C |
| 12 | On-Call Agent | 2 | task 28, task 29, task 39 | [`_docs/architecture.md`](architecture.md) §Responder agent; [`_docs/testing.md`](testing.md) §Responder: US-15 | C |

**Total: 24 points; pass mark 10** ([`_docs/rubric.md`](rubric.md) line 4). The 12 rows above are in rubric order. Future-development tasks 30-36 add no mapped row; tasks 31 and 36 add Testing evidence after submission, and the Testing row does not depend on them.

¹ `_docs/tasks.md` §Coverage summary assigns the end-to-end application to tasks 1, 3-12 and 14, and notes that the criterion's "runs locally with a single command" clause is supplied in Tier A by `make dev` (task 11, backend on SQLite and frontend together, no Docker; #108 stage 2), with task 15 (the Compose stack) as the container variant that [`_docs/roadmap.md`](roadmap.md) B2 assigns to Application. Task 15's own `Covers:` line names only Containerization. See Source discrepancies D1 (resolved). The caveat does not unmask the row: tasks 1, 3-12 and 14 already cover the end-to-end application, and Tier A no longer waits for task 15 for the single-command clause.

## Source discrepancies

| # | Sources | Difference | Handling |
|---|---|---|---|
| D1 | [`_docs/tasks.md`](tasks.md) §Coverage summary vs [`_docs/roadmap.md`](roadmap.md) B2 | tasks.md lists Application tasks as 1, 3-12 and 14; roadmap B2 assigns Application to task 15 (Compose stack, the "single command" clause), but task 15's `Covers:` line names only Containerization | **Resolved in #95:** [`_docs/tasks.md`](tasks.md) §Coverage summary now separates the two Application clauses: the row lists tasks 1, 3-12 and 14 for the end-to-end application, and a note records the criterion's "runs locally with a single command" clause (in #108 stage 2 the Tier A supplier became `make dev` in task 11, and task 15, the Compose stack, is the container variant). [`_docs/roadmap.md`](roadmap.md) B2 assigns Application to task 15 for the container variant. Task 15's own `Covers:` line still names only Containerization, and no task was renumbered, added or removed. Cross-referenced from the Application row's footnote ¹. |
| D2 | [`_docs/specs.md`](specs.md) line 3 vs §Open questions | The status line says "reviewed", but Open questions 2-4 remain open while architecture proposes answers | Register keeps Q2-Q4 as `proposed answer`; spec wording change is a proposed follow-up, not applied. |
| D3 | [`_docs/specs.md`](specs.md) Open question 2 vs [`_docs/architecture.md`](architecture.md) A27 | Q2 is open; A27 proposes P1 7 / P2 14 / P3 30 / P4 90 days | Both kept; A27 is a proposed answer pending human confirmation. |
| D4 | [`_docs/specs.md`](specs.md) Open questions 3-4 vs [`_docs/architecture.md`](architecture.md) A26, A33 | Q3 (channel) and Q4 (US-14 window) are open; A26 proposes email (the backend sends it: MailHog in development and tests, Amazon SES in AWS) and A33 proposes 30 minutes | Both kept; no answer is treated as resolved. |
| D5 | [`_docs/roadmap.md`](roadmap.md) D1 vs [`_docs/architecture.md`](architecture.md) Open question 6 | D1 proposed closing Q6 with the Module 4 pattern; Q6 was listed as open | **Resolved (checked in #107):** roadmap D1 is resolved (H3, as adapted by H2-H4) and `architecture.md` Open question 6 is closed; the register rows match. |
| D6 | [`README.md`](../README.md) line 27 vs [`_docs/specs.md`](specs.md) §Finding statuses | README listed dashboard statuses as `open`, `risk accepted`, `fixed`; the spec's complete list adds `withdrawn` | **Resolved by #73 (checked in #107):** `README.md` line 27 now lists `open`, `risk accepted`, `fixed`, `withdrawn`, matching the spec. |
| D7 | [`_docs/roadmap.md`](roadmap.md) §Open decisions | The table numbers 18 rows: rows 1-4 are resolved/withdrawn, rows 5-11 carry the labels D1-D7, and rows 12-18 are the decisions H1-H7 (all resolved) | Register keys the decisions `roadmap.md:D1`-`roadmap.md:D7`; D1, D2, D3, D6 and D7 are resolved, D4 and D5 stay open. H1-H7 are not register entries; they are recorded in the roadmap and applied to the documents. |
| D8 | [`_docs/specs.md`](specs.md) §Assumptions bullet 1 (line 436) vs [`_docs/architecture.md`](architecture.md) A16, A17 | The spec's assumption wording about asset criticality values ("small fixed set; final values in Stage 2") predates the values the human confirmed on 2026-10-22 | The spec wording is left as written (the spec is human-owned) and aligned at the next approved spec change; architecture A16 and A17 are the confirmed text. |

## Top risks

Every mitigation has an owner. A mitigation labelled `human` is a human-only action (account, domain, dev-container rebuild, production approval, teardown); no destructive or account-creating step is assigned to the Engineer.

| # | Risk (coverage area) | Source | Trigger / impact | Mitigation | Owner | Step / milestone | Residual risk |
|---|---|---|---|---|---|---|---|
| R1 | No Docker in the local sandbox; Docker/Compose environment is human-dependent (a) | [`AGENTS.md`](../AGENTS.md) §Project gotchas; [`_docs/roadmap.md`](roadmap.md) T2, T3, prerequisites; #31/#48 | `docker compose up`, Postgres integration and the Compose telemetry/alert jobs cannot run in the sandbox; Containerization, the Application single-command clause and Compose Testing wait | Compose dev-container recipe (#31), cloud `docker-start` (#48), Compose jobs in CI; Tier A uses only the local no-Docker rows ([`_docs/architecture.md`](architecture.md) §Development environment) | `human` for the dev-container rebuild; agents for the CI jobs | T2, T3; B2, C3 | Rebuild or cloud route can slip; Tier A is unaffected |
| R2 | AWS account, budget, Terraform, `sslip.io` HTTPS and the GitHub `production` environment (b) | [`_docs/roadmap.md`](roadmap.md) prerequisites, B4-B6; [`_docs/architecture.md`](architecture.md) §Deployment, Open question 7 (closed: no domain, `sslip.io`) | Tasks 17, 18 and 21 cannot deploy; Deployment and the CD half of CI/CD stay at 0-1 points | Budget alert before any stack (A37); the human installs Terraform and runs the bootstrap and every apply; check Let's Encrypt limits for shared `sslip.io` names and the `production` protection rules at build time (both carry `VERIFY:` in the architecture); use the "If AWS is slow" order if it delays; the HTTPS fallback (staging certificate, then `nip.io`) and the nightly-stop rules (24-hour catch-up, a deploy to a stopped server skipped and reported, the stop switched off while graders may visit) are named in `architecture.md` Deployment | `human` for the account, budget, Terraform apply and production approval; agents write the Terraform and runbook | B4-B6; S3 | Schedule risk; D5 fallback (Compose/kind demo) is named but not chosen |
| R3 | Unresolved responder runtime (submission) and LLM provider/model (future development) (c) | [`_docs/architecture.md`](architecture.md) A23, Open question 9, §Responder agent; [`_docs/roadmap.md`](roadmap.md) prerequisites | Task 28 and C6 cannot pin a runtime, and future-development task 30 cannot pin a model; tests and CI must not call a paid provider | Choose the responder runtime with the human before task 28 is filed (human decision, 2026-10-22; it is still open and recorded in A34), because the recorded run of task 39 needs the real runtime and a stub run shows no agent fixing anything; choose the LLM provider when future development starts, before task 30; `RESPONDER_MODE=stub` and `LLM_MODE=stub` in tests; the 20 s timeout and the "brief unavailable" path keep the product working once the brief is built | `human` chooses; agents implement the stubs | Task 28, C6; task 30 (future development) | Provider capabilities, pricing and retention remain `VERIFY:` |
| R4 | External API unknowns, fixture capture and no live feeds in CI (d) | [`_docs/architecture.md`](architecture.md) §External data sources; `VERIFY:` items in [`_docs/api.md`](api.md) and [`_docs/testing.md`](testing.md) | OSV/KEV/EPSS/GitHub/SES/LLM/Grafana details may differ; live feeds would make tests flaky or need secrets | Committed fixtures plus `U-NET`/`I-NET` network guards; deliberate `make record-fixtures` capture; resolve each `VERIFY:` at its build task. Email route (human decision, 2026-10-22, task 37): the backend sends through the Amazon SES API using the server's instance role, with one verified sender address because `sslip.io` hostnames cannot carry SES domain DKIM records; development and tests send to MailHog in the Compose stack (task 24; MailHog is a dependency, ask before adding). `VERIFY:` SES sandbox recipients (the demo recipient must be verified too). `VERIFY:` the current free allowance and sending limits. `VERIFY:` the instance-role permission, action and resource form. `VERIFY:` the SES region | Agents; `human` approves dependency additions (MailHog, the AWS SDK client) and deliberate captures | Tasks 5, 6, 13, 16, 37; B2/B3 | Fixtures drift from live feeds until re-captured; an unverified demo recipient blocks a real send |
| R5 | Telemetry exclusions and advisory prompt injection (e) | [`_docs/specs.md`](specs.md) US-13, US-15; [`_docs/architecture.md`](architecture.md) §Security boundaries, §Observability | Excluded data (advisory text, owner contact, repository URL, lockfile content, credentials) could reach telemetry; advisory text could steer the responder or a notification (and, in future development, the brief) | Allowlist helper in code plus a Collector processor; `T-REFUSE`; `S-*` per flow; responder read-only tokens and "untrusted data" instructions; alert labels carry finding id and tier only | Agents | Tasks 23-25, 28-29; C2-C6 | Auto-instrumented attributes can leak if the allowlist misses a key |
| R6 | Scope and schedule: Tier C estimate above the course's ~20 hours; tasks 37 and 38 added to the submission scope; the LLM/MCP/n8n work moved to future development (f) | [`_docs/reviews/2026-10-16-final-rubric-impact.md`](reviews/2026-10-16-final-rubric-impact.md) §5; [`_docs/tasks.md`](tasks.md) Submission additions and Future development (after submission) | 26-30 h estimate exceeds ~20 h; tasks 37, 38 and 39 add backend and close-out work to the scoring path; the #108 stage 2 fixes add work to tasks 1, 4, 9, 11, 12 and 14 (the test harness, the worker, `PATCH /assets/{id}`, `make dev`, the real `Services`, `/health`) and add task 39 | Scoring path first (Milestones A-B-C with tasks 37 and 38); Future-development tasks 30-36 only after submission; Tier A passes at 12 points; shrink the application slice or accept the overrun at the human's decision. The estimate was accepted by the human (2026-10-22) and is to be re-estimated after the #108 fixes; no new figure is recorded here | `human` owns scope/time; orchestrator/PM own sequence | S1-S5; all milestones | Tier C overrun is accepted or the application shrinks |
| R7 | Step 12 backlog filing is `doing`; step 14 depends on steps 11 and 13 and "Milestone A filed" (g) | [`_docs/roadmap.md`](roadmap.md) steps 12-14 and check-in 2026-10-22; human decision Q1 option 1, 2026-10-22 | The Milestone B, C and Committed issues, including the submission tasks 37, 38 and 39, are not all filed; the plan review sees Milestone A issues only | This summary maps task numbers, not issue numbers; the Milestone B, C and Committed issues are filed at their boundaries after S1 starts and no longer gate step 14; the summary does not claim those issues exist | Orchestrator/PM; `human` approves filing | Steps 12-14 | A later-filed issue can differ from the task it maps; the map is re-checked at each filing (R9) |
| R8 | The demo defect must be removed before production (h) | [`_docs/tasks.md`](tasks.md) task 29; [`_docs/testing.md`](testing.md) §Responder (`P-FLAG-GONE`); [`_docs/architecture.md`](architecture.md) A35 | `VT_DEMO_DEFECT=notify_no_fix` could remain in production code, leaving a deliberate failure path | Production startup refuses the flag (`P-PROD-REFUSAL`); `P-FLAG-GONE` is one check that runs only in the production-promotion workflow and blocks promotion until the path is gone (the pull-request gate stays green meanwhile); cleanup commit/PR; promotion stays manual | Agents write and remove the path; `human` merges and promotes | Task 29; C6-C7 | A bypass of the manual gate could still promote the flag, so the test is the guard |
| R9 | Mapping and points drift as stage documents change (i) | [`_docs/rubric.md`](rubric.md); [`_docs/tasks.md`](tasks.md); any later stage edit | A later edit can add/remove a task or change a `Covers:` line, invalidating a row; scores could be read as current | Task numbers are canonical; re-check this map after any stage-document change; the auditor alone updates [`_docs/rubric-evidence.md`](rubric-evidence.md); this document records conflicts instead of editing sources | Orchestrator/PM; reviewer at step 14 | Steps 12-14 and after any stage change | A stale row can survive until the next check |
| R10 | An exploited vulnerability with no CVE cannot reach `P1` or `P2` | [`_docs/architecture.md`](architecture.md) § Prioritisation, Open question 10 (closed); [`_docs/specs.md`](specs.md) E11 | The KEV and EPSS inputs both key on a CVE id, so an exploited finding with no CVE is ranked by the lower tiers only | Accepted as documented; the sentence in architecture § Prioritisation states it, and the tier tests (task 7) follow the rules as written | `human` accepted, 2026-10-22 | Task 7 | An exploited no-CVE finding can sit below `P2`; accepted, not a defect. Check: the sentence exists in architecture § Prioritisation |

## Open questions and assumptions

Scope per source follows the Stage 6 issue: `specs.md` open questions 1-5 and every `ASSUMPTION:` (including inline ones); `architecture.md` open questions 1-11 and A1-A41; `api.md` `ASSUMPTION:` items and unresolved `VERIFY:` items; `testing.md` `T-A1`-`T-A8` and `VERIFY:` rows; `tasks.md` `ASSUMPTION:` and `VERIFY:` lines; `roadmap.md` live decisions D1-D7 as a separate group. The brief has no labelled items. No item is renumbered or deleted; resolved items keep their entry.

### `_docs/specs.md`

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `specs.md:Q1` | What counts as "top-priority" for the US-8 notification (which tier)? | resolved | [`_docs/architecture.md`](architecture.md) §Prioritisation: `P1`; task 7 |
| `specs.md:Q2` | What are the US-9 overdue and escalation windows? | proposed answer | A27 (7/14/30/90 days); `human` confirms; tasks 35 |
| `specs.md:Q3` | Which notification channel (email or chat) does the pilot use? | proposed answer | A26: email; route in risk R4 (SES API, one verified sender, MailHog in Compose); `human` confirms; task 37 |
| `specs.md:Q4` | What is the US-14 notification window? | proposed answer | A33: 30 minutes; `human` confirms; task 26 |
| `specs.md:Q5` | What credential does the responder use and how is it scoped; does a human or automation merge? | resolved | [`_docs/architecture.md`](architecture.md) §Responder agent (D2: human merges); task 28 |
| `specs.md:Assumptions bullet 1` | "Asset criticality" is a small fixed set; final values in Stage 2 | proposed answer | A16 final values, confirmed by the human 2026-10-22 (spec wording left as written, see D8); task 3 |
| `specs.md:Assumptions bullet 2` | Pilot repos plus OWASP Juice Shop give real findings; pilot list in a later stage | proposed answer | Task 22; `human` supplies repository URLs; A41 fallback |
| `specs.md:Assumptions bullet 3` | An asset owner has a name and contact email; ownerless only when both are unset; partial-owner notification decided in Stage 2 | proposed answer | A21: email-only owner notified, name-only held; tasks 9, 10 |
| `specs.md:withdrawn status ASSUMPTION` | `withdrawn` is an addition to the brief's three finding statuses (also stated in the status table and E4) | proposed answer | Tasks 8, 12; spec status table, E4 |

### `_docs/architecture.md`: open questions

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `architecture.md:Q1` | Spec Q1 (top tier) | resolved | §Prioritisation: `P1`; task 7 |
| `architecture.md:Q2` | Spec Q2 (US-9 windows) | proposed answer | A27; `human` confirms; task 35 |
| `architecture.md:Q3` | Spec Q3 (channel) | proposed answer | A26: email; route in risk R4; `human` confirms; task 37 |
| `architecture.md:Q4` | Spec Q4 (US-14 window) | proposed answer | A33: 30 minutes; `human` confirms; task 26 |
| `architecture.md:Q5` | Spec Q5 (responder credential and merge) | resolved | §Responder agent; D2; task 28 |
| `architecture.md:Q6` | What exactly is the "Module 3/4 pattern" the human referred to? | resolved | Closed in `architecture.md` Open question 6: the pattern is followed as adapted by H2-H4 (Terraform, one server for both environments, GHCR); roadmap D1 |
| `architecture.md:Q7` | Which domain name and TLS approach does the public URL use? | resolved | Closed in `architecture.md` Open question 7: no domain, `sslip.io` hostnames (H5) with Let's Encrypt HTTPS; the rate-limit `VERIFY:` stays; roadmap D3 |
| `architecture.md:Q8` | Confirm EPSS threshold T = 0.10 and the "exposed asset" definition | resolved | Closed 2026-10-22 (human decision): T = 0.10 (A18, configuration) and the exposed-asset definition (A17) confirmed as written; A17/A18; task 7 |
| `architecture.md:Q9` | Which LLM provider and model? | open | A23; `human` before task 30; risks R3 |
| `architecture.md:Q10` | An exploited vulnerability with no CVE can never reach P1/P2: accept, or add a rule? | resolved | Closed 2026-10-22 (human decision): accepted as documented in architecture § Prioritisation (risk R10); task 7 |
| `architecture.md:Q11` | Does Juice Shop commit a supported lockfile? | open | A41 fallback; `human` confirms before task 22 |

### `_docs/architecture.md`: assumptions

All entries are listed under §Assumptions. A7, A12 and A14 were retired into spec rules in the second #43 spec commit; their numbers are not reused, so active IDs are A1-A6, A8-A11, A13, A15-A41.

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `architecture.md:A1` | Tiers: Postgres and n8n are Tier B; the MCP server is Tier A on the developer's machine | proposed answer | Engineer, tasks 1/15/32; step 14 |
| `architecture.md:A2` | n8n and Grafana use their default embedded stores on their own volumes | proposed answer | Engineer, task 15 |
| `architecture.md:A3` | Re-scans: daily schedule after refresh (the backend's own scheduler for submission; the n8n schedule is future development) plus a person's on-demand action; registration starts the first scan | proposed answer | Engineer, tasks 8/38 (n8n variant: future-development task 33) |
| `architecture.md:A4` | Scans and briefs run as background jobs in the backend with a job table and one worker | proposed answer | Engineer, task 4 (the worker and job table; reused by tasks 37 and 38) |
| `architecture.md:A5` | Lockfiles are looked for at the repository root only | proposed answer | Engineer, task 4 |
| `architecture.md:A6` | One finding per package across several files; highest per-entry fixed version; `fixed` only when every entry is clear | proposed answer | Engineer, task 5 |
| `architecture.md:A8` | `uv.lock` and `package-lock.json` entry handling, including lockfileVersion 1 as a parse error | proposed answer | Engineer, task 4 |
| `architecture.md:A9` | `requirements.txt` handling for `-c`, `-e`, VCS/URL requirements and index options | proposed answer | Engineer, task 4 |
| `architecture.md:A10` | OSV's match is the candidate set; a range disagreement keeps the finding with a warning | proposed answer | Engineer, task 5 |
| `architecture.md:A11` | `last_affected`-only or open-ended intervals give no fixed version | proposed answer | Engineer, task 5 |
| `architecture.md:A13` | Enum values are stored and sent exactly as the spec writes them | proposed answer | Engineer, task 3 |
| `architecture.md:A15` | Alias-joined vulnerabilities merge; the earlier finding keeps its id and lifecycle | proposed answer | Engineer, task 5 |
| `architecture.md:A16` | Criticality values are final as `low`, `medium`, `high`, `critical` | resolved | Confirmed by the human, 2026-10-22; task 3 |
| `architecture.md:A17` | Only criticality `critical` counts as "critical" in the tier rules | resolved | Confirmed by the human, 2026-10-22; task 7 |
| `architecture.md:A18` | The EPSS threshold T is 0.10 | resolved | Confirmed by the human, 2026-10-22; task 7 |
| `architecture.md:A19` | "Oldest finding" uses first detection time; the final tie-break is finding id | proposed answer | Engineer, task 7 |
| `architecture.md:A20` | Tiers cover `open` and `risk accepted`; the ranked list is `open` only; E8 escalation means a tier rise or becoming `KEV: listed` | proposed answer | Engineer, task 7 |
| `architecture.md:A21` | An email-only owner is notified; a name-only owner's notification is held | proposed answer | Engineer, task 10 |
| `architecture.md:A22` | The brief prompt includes the advisory summary, truncated to 500 characters | proposed answer | Engineer, task 30 |
| `architecture.md:A23` | LLM provider chosen with the human; 20 s timeout; brief cached per lifecycle, fixed version, prompt version and model | open | `human` chooses; Engineer task 30; R3 |
| `architecture.md:A24` | The brief output check rejects other version tokens and any URL in text fields | proposed answer | Engineer, task 30 |
| `architecture.md:A25` | n8n polls every 5 minutes; refresh 06:00 UTC; digest Monday 08:00 UTC | proposed answer | Engineer, tasks 33/35 (future development); the 06:00 UTC refresh also times task 38 |
| `architecture.md:A26` | Email; a mail catcher in development and Amazon SES in AWS | proposed answer | `human` confirms spec Q3; task 37 (the architecture, testing and tasks documents name MailHog; #100 and #101 reconciled them) |
| `architecture.md:A27` | US-9 windows P1 7, P2 14, P3 30, P4 90 days; reminders and escalation at due and weekly after | proposed answer | `human` confirms spec Q2; task 35 |
| `architecture.md:A28` | A missing security-lead contact shows on `/health` and a dashboard banner, and holds escalation and digest jobs (future development, with the E8 notice, human decision 2026-10-22) | proposed answer | Engineer, task 35 (future development) |
| `architecture.md:A29` | The MCP server runs over stdio on the developer's machine; `get_asset` includes owner contact | proposed answer | Engineer, task 32 |
| `architecture.md:A30` | Dashboard authentication values (Argon2id, session lifetimes, lockout, CSRF header), the owner-match rule and the role rules for registering, updating and re-scanning an asset | proposed answer | Engineer, task 9 |
| `architecture.md:A31` | URL defanging (any scheme, `www.` or domain-shaped token), email header values from finding id and tier only, and `@` mention handling in emails and issue bodies | proposed answer | Engineer, task 37 (owner email); tasks 34/35 (future development) |
| `architecture.md:A32` | The telemetry attribute allowlist, including `service.version` (roadmap D2, added in #107) | proposed answer | Engineer, task 23; R5 |
| `architecture.md:A33` | US-14 window 30 minutes, 1-minute evaluation; no-repeat was the human's 2026-10-20 decision | proposed answer | `human` confirms spec Q4; task 26 |
| `architecture.md:A34` | The responder runs as a container in the observability stack; a recorded alert-to-fix run with the real responder runtime is the evidence (task 39); the runtime itself is open for the human and is chosen before task 28 is filed; branch `responder/<fingerprint>`; failed jobs retried each poll for up to 7 days | open | `human` chooses the runtime; Engineer tasks 28, 39; R3 |
| `architecture.md:A35` | The demo defect is switched by `VT_DEMO_DEFECT` and refused in production | proposed answer | Engineer, tasks 28/29; R8 |
| `architecture.md:A36` | One server runs `dev` and `prod` as two Compose projects behind one reverse proxy on two `sslip.io` hostnames; one `t3.medium` class instance (`t3.small` only if both projects fit); Postgres in a container per project on EBS | proposed answer | `human` approved the one-server shape via H3 (roadmap D1); Engineer task 17 |
| `architecture.md:A37` | Budget amount set by the human; nightly stop of the server with an off switch; 24-hour catch-up at backend start; 7-day telemetry retention | proposed answer | `human` sets the budget amount and switches the stop off for graders; Engineer tasks 17, 21, 38 |
| `architecture.md:A38` | The pilot seed list lives in the repository as a data file, registered through the API | proposed answer | Engineer, task 22 |
| `architecture.md:A39` | Held notification jobs never fire the US-14 alert; accepted by the human, 2026-10-22, with the release of held owner jobs when an owner email is set (`PATCH /assets/{id}`) | resolved | `human` accepted; Engineer tasks 26, 9 |
| `architecture.md:A40` | Only export is a no-op without a Collector endpoint; the SDK always creates real span contexts, so a job's `traceparent` is always valid | proposed answer | Engineer, task 23 |
| `architecture.md:A41` | If Juice Shop has no supported lockfile, an open-source repository pinned to older versions replaces it | open | `human` confirms Q11; task 22 |

### `_docs/api.md`

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `api.md:A1 (#27)` | The n8n and MCP tokens are static opaque bearer tokens from environment variables and AWS Secrets Manager; no refresh or rotation in the MVP | proposed answer | `human` provisions the tokens; Engineer task 10 |
| `api.md:A1 (#50)` | The responder token follows A1: static opaque bearer from `RESPONDER_API_TOKEN` and Secrets Manager; no refresh or rotation | proposed answer | `human` provisions the token; Engineer task 10 |
| `api.md:VERIFY FastAPI 422 header` | FastAPI returns 422 for a missing required `Header()` on the pinned version; #24 maps it to 403 forbidden | VERIFY | Engineer, task 10/24 |
| `api.md:VERIFY query validation order` | FastAPI validates query parameters before the handler runs | VERIFY | Engineer, task 10 |
| `api.md:VERIFY GitHub naming` | GitHub owner and repository naming rules match the `repositoryUrl` pattern | VERIFY | Engineer, task 4 |
| `api.md:VERIFY OpenAPI 3.1 generation` | The pinned FastAPI version generates OpenAPI 3.1.0 | VERIFY | Engineer, task 14 |
| `api.md:VERIFY validator 3.1` | `uvx openapi-spec-validator` validates OpenAPI 3.1 | VERIFY | Engineer, task 14; `make openapi-validate` |
| `api.md:VERIFY n8n headers` | n8n's HTTP Request node sends a custom `traceparent` and bearer `Authorization` header | VERIFY | Engineer, tasks 23/34 |
| `api.md:VERIFY MCP SDK` | The Python MCP SDK and stdio transport work as assumed | VERIFY | Engineer, task 32 |
| `api.md:VERIFY traceparent` | The W3C Trace Context `traceparent` format matches the contract pattern | VERIFY | Engineer, task 23 |
| `api.md:VERIFY tracker issue numbers` | GitHub tracker issue numbers are positive integers | VERIFY | Engineer, task 34 |
| `api.md:VERIFY Secrets Manager injection` | AWS Secrets Manager injects `N8N_API_TOKEN`, `MCP_API_TOKEN` and `RESPONDER_API_TOKEN` at container start (lines 82, 83 and 354) | VERIFY | `human`/Engineer, tasks 10/17 |
| `api.md:VERIFY Loki scope` | The Grafana/Loki viewer token and its Loki access scope | VERIFY | Engineer, task 28 |

### `_docs/testing.md`

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `testing.md:T-A1` | Compose service `db`; test projects `vt-test`/`vt-e2e`; fixture asset/repo names; 120 s E2E timeout | proposed answer | Engineer, tasks 15/16; final names at Compose work |
| `testing.md:T-A2` | Fixture capture baseline is 2026-10-22; the recorder writes the actual date | proposed answer | Engineer, tasks 1 (harness), 4-6 (captures), 13 (manifest) |
| `testing.md:T-A3` | The Grafana rule uses `noDataState: Alerting` and `execErrState: Alerting`; with the constant global `0` series, `NoData` means the backend or metric is down and alerts the human email only | proposed answer | Engineer, task 26 |
| `testing.md:T-A4` | The US-13 metric carries the trace id as an OTel exemplar; otherwise a trace/log join by trace id | proposed answer | Engineer, tasks 23/25 |
| `testing.md:T-A5` | `make test` grows to include backend unit and SQLite integration and stays the single local command | proposed answer | Engineer, tasks 1 and 13 |
| `testing.md:T-A6` | MailHog is the local mail catcher (dependency, ask before adding) | proposed answer | `human` approves the dependency; tasks 24/37 |
| `testing.md:T-A7` | `pip-audit` and `npm audit --omit=dev` are the light-scan tools; adding them needs approval | proposed answer | `human` approves; Engineer task 20 |
| `testing.md:T-A8` | Production configuration is selected with `ENVIRONMENT=production`; the final name is a build detail | proposed answer | Engineer, task 28 |
| `testing.md:VERIFY OSV` | OSV endpoints, batch limit, fields and fixture shape | VERIFY | Engineer, task 5; architecture §External data sources |
| `testing.md:VERIFY KEV` | CISA KEV URL and fields | VERIFY | Engineer, task 6 |
| `testing.md:VERIFY EPSS` | FIRST EPSS URL and fields | VERIFY | Engineer, task 6 |
| `testing.md:VERIFY mail sink form` | The form of the in-process fake mail sink for the owner-notification tests (for example an in-process SMTP server or an injected transport) | resolved | Closed in #108 stage 2: an injected mail transport that records messages; `make test` uses it and `make test-compose` uses MailHog; task 37 |
| `testing.md:VERIFY MailHog read` | How the Compose test reads received mail (MailHog's HTTP API) | VERIFY | Engineer, tasks 24/37 |
| `testing.md:VERIFY GitHub contents` | The GitHub contents API endpoint and fixture shape | VERIFY | Engineer, task 4 |
| `testing.md:VERIFY version libraries` | PEP 440 and SemVer library behaviour, including leading `v` and pre-releases | VERIFY | Engineer, tasks 4/5 |
| `testing.md:VERIFY OTel exemplar` | OTel Prometheus exemplar support | VERIFY | Engineer, task 25 |
| `testing.md:VERIFY Tempo-Loki link` | Tempo-to-Loki/Grafana data-source links | VERIFY | Engineer, task 24 |
| `testing.md:VERIFY Collector processor` | Collector processor names (`transform` / `attributes`) and `keep_keys` behaviour | VERIFY | Engineer, task 24 |
| `testing.md:VERIFY OTel batch/queue` | SDK batch buffering, Collector queue behaviour and self-metric names | VERIFY | Engineer, task 24 |
| `testing.md:VERIFY Grafana no-data` | Grafana no-data/error semantics and whether NoData keeps an instance active | VERIFY | Engineer, task 26 |
| `testing.md:VERIFY Grafana instances` | Grafana alert-instance and notification-policy behaviour and repeat-interval limit | VERIFY | Engineer, task 26 |
| `testing.md:VERIFY Markdown fence` | GitHub Markdown fence rules and whether mentions inside code blocks notify | VERIFY | Engineer, task 34 |
| `testing.md:VERIFY GitHub scope` | GitHub App/token scope and branch-protection details | VERIFY | `human`/Engineer, task 28 |
| `testing.md:VERIFY Loki viewer` | The Loki viewer token scope | VERIFY | Engineer, task 28 |
| `testing.md:VERIFY LLM` | LLM provider, endpoint, schema-constrained output, retention and pricing | VERIFY | `human`/Engineer, task 30; R3 |
| `testing.md:VERIFY audit tools` | `pip-audit` / `npm audit` licence and behaviour | VERIFY | `human`/Engineer, task 20 |

### `_docs/tasks.md`

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `tasks.md:ASSUMPTION` | `ASSUMPTION:` Task 15's Compose file and service names follow testing T-A1; task 17's Terraform resource names and AWS region follow architecture §Deployment and carry its `VERIFY:` tags | proposed answer | Engineer, tasks 15/17 |
| `tasks.md:VERIFY SES sandbox` | The SES sandbox allows only verified recipient addresses, so the demo recipient must be verified too (task 37) | VERIFY | `human`/Engineer, task 37 |
| `tasks.md:VERIFY SES allowance` | The current SES free allowance and sending limits (task 37) | VERIFY | `human`/Engineer, task 37 |
| `tasks.md:VERIFY SES role permission` | The instance-role permission, the `ses:SendEmail` action and the resource form (task 37) | VERIFY | Engineer, task 37; the role itself is Terraform in task 17 |
| `tasks.md:VERIFY SES region` | The SES region that holds the verified sender identity (task 37) | VERIFY | `human`/Engineer, task 37 |
| `tasks.md:VERIFY Juice Shop lockfile` | The exact Juice Shop lockfile in task 22 is confirmed by the human before the first registration | VERIFY | `human`, task 22 |
| `tasks.md:VERIFY OIDC provider` | The deploy-role Terraform accepts an already-existing GitHub OIDC provider in the account instead of failing to create a second one; one provider per URL per account (task 17) | VERIFY | Engineer/`human`, task 17 |

### `_docs/roadmap.md`: live decisions D1-D7

Rows 1-4 of the roadmap's decision table are resolved or withdrawn and are not live; D1-D7 are table rows 5-11.

| Key | Item | Status | Owner / next step |
|---|---|---|---|
| `roadmap.md:D1` | Close architecture Open question 6 with the Module 4 description (the roadmap's original wording: one EC2 instance per environment, Compose, ECR, CloudFormation; adapted by H2-H4: Terraform, one server for both environments, GHCR, as `architecture.md` Open question 6 records) | resolved | Resolved in the roadmap's Open decisions (human, 2026-10-22): yes, with one server for both environments (H3); architecture Q6 |
| `roadmap.md:D2` | Adopt the course image tag `YYYYMMDD-HHMMSS-shortsha` and add `service.version` (the tag) to the telemetry allowlist (A32) | resolved | Resolved in the roadmap (kept; the tag works with GHCR); `service.version` added to `architecture.md` A32 in #107; tasks 17/21 |
| `roadmap.md:D3` | Domain name and TLS approach for the public URL | resolved | Resolved in the roadmap, decided by H5 (`sslip.io`, no domain; `architecture.md` Open question 7 closed) |
| `roadmap.md:D4` | Add to US-15 that a false positive or test alert makes the responder explain and change nothing | open | `human`; `specs.md` is protected; C6 |
| `roadmap.md:D5` | Fallback if AWS is not available in time (kind cluster or local Compose demo) | open | `human` names the fallback date at B4 |
| `roadmap.md:D6` | Move n8n tasks 33 and 34 ahead of task 25 and add task 34 to tasks 25 and 28's `Depends on:` | resolved | Resolved in the roadmap (moot): H7 made n8n future development and the backend delivers (task 37); the new build-order dependency is task 37's, in `tasks.md` Build order |
| `roadmap.md:D7` | At filing, split task 21 (dev vs prod) and task 24 (Compose vs `vt-observability`) | resolved | Resolved in the roadmap; applied in `tasks.md` by #99: task 21 is the dev deploy (17, 19), the production workflow is in task 18, task 24 is Compose only (23) |

### `_docs/project-brief.md`

No labelled items: 0 open questions, 0 `ASSUMPTION:` and 0 `VERIFY:` (read-only `.scratch/` extraction). It is the fixed input, not a source of open items.

### `_docs/plan-summary.md` (self-assumptions)

| Key | Item | Status | Owner / where resolved |
|---|---|---|---|
| `plan-summary.md:P-A1` | `ASSUMPTION:` The earliest milestone in a rubric row is the earliest milestone among the `tasks.md` tasks that §Coverage summary assigns to that criterion; the Application/task 15 caveat does not move its milestone | proposed answer | PM/orchestrator at step 14 |
| `plan-summary.md:P-A2` | `ASSUMPTION:` `_docs/specs.md`'s `VERIFY:` markers are external-detail checks, outside the Stage 1 register scope; they are tracked in architecture §External data sources and risk R4 | proposed answer | PM/orchestrator at step 14 |

## Completeness check

Counts come from the read-only label-only `.scratch/` extraction (`count_labels.py`), which matches only the literal tags `ASSUMPTION:` and `VERIFY:`. Prose, headings, `make verify` and the unlabelled word "assumption" are not counted. An unexplained difference would be a FAIL; every difference below is explained, and the exact line locations follow the table.

| Source | Open questions / decisions | `ASSUMPTION:` labels (occurrences / lines) | `VERIFY:` labels (occurrences / lines) | Captured | Difference and explanation |
|---|---|---|---|---|---|
| `_docs/project-brief.md` | 0 | 0 / 0 | 0 / 0 | 0 | No labelled items |
| `_docs/specs.md` | 5 | 6 / 6 | 14 / 13 (out of scope) | 9 | The 6 assumption labels are 5 distinct meanings: line 226 is the US-9 windows assumption and is recorded in `specs.md:Q2`; lines 319 and 410 are the same `withdrawn` addition (one row); lines 436, 438 and 440 are the three §Assumptions rows. Spec `VERIFY:` labels are external-detail checks outside the Stage 1 register scope (P-A2) |
| `_docs/architecture.md` | 11 | 38 / 29 | 72 / 55 (out of scope) | 49 | The 38 labelled tags are exactly A1-A6, A8-A11, A13 and A15-A41; A7/A12/A14 are retired and not reused, so there is no assumption difference. `VERIFY:` labels are tracked per §External data sources and risk R4, not as separate register rows |
| `_docs/api.md` | 0 | 2 / 2 | 13 / 12 | 13 | Both A1 labels (#27 at line 82, #50 at line 83) are separate rows. The 13 VERIFY occurrences are 11 distinct items: line 346 carries two labels (OpenAPI generation and the validator), and the Secrets Manager item occurs on lines 82, 83 and 354 and is one row listing all three |
| `_docs/testing.md` | 0 | 15 / 15 (14 tagged; 8 distinct T-A) | 22 / 22 | 26 | Line 5 is the conventions definition, so the 14 tagged occurrences are the 8 T-A rows. The 22 VERIFY labels are 21 item mentions (line 5 is a definition) and 18 distinct rows (three labels were closed in #108 stage 2, and their register row stays as `resolved`): the fake mail sink's form is the former #107 row and is now decided (an injected transport that records messages), how the Compose test reads MailHog (line 130) is the other row added in #107, line 131 is the SES sandbox item already in the `tasks.md` rows, line 278 supplies the Grafana instance row, and the table at lines 419-427 repeats items already named inline |
| `_docs/tasks.md` | 0 | 2 / 2 | 7 / 3 | 7 | Lines 95 and 301 are one assumption row (task 15/17 follow T-A1 and architecture §Deployment). Line 107 (task 17) carries one VERIFY label, the existing-OIDC-provider row added in #108. Line 191 (task 37) carries four VERIFY labels, the SES sandbox recipients, the free allowance and limits, the instance-role permission and the SES region, each its own row. Line 301 carries two: one is a cross-reference to architecture's existing tags, the other is the Juice Shop lockfile row. Recounted after #108 stage 2 |
| `_docs/roadmap.md` | 7 live decisions (D1-D7) | 0 / 0 | 6 / 6 (out of scope) | 7 | The decision table has 18 rows; rows 1-4 are resolved/withdrawn and rows 12-18 are the resolved H1-H7, so the 7 D-rows (rows 5-11) are captured. The 6 VERIFY labels (69, 70, 125, 126, 139, 217) are step and milestone external details outside the decision register; the mention of the literal tag at line 291 is prose in a check-in row, not a label |
| `_docs/plan-summary.md` | 0 | 2 / 2 (self) | 4 / 1 (restated) | 2 | P-A1 and P-A2 are labelled `ASSUMPTION:` and added here. Risk R4 restates task 37's four SES `VERIFY:` labels once; they are the four `tasks.md` rows above and add no new row |

Register total: 9 + 49 + 13 + 26 + 7 + 7 + 2 = **113 entries** (112 before #108, which included the 2 self-assumptions and the two `testing.md` mail VERIFY rows added in #107, plus the `tasks.md` OIDC provider VERIFY row added in #108).

All counts and locations in this section were recounted after the #108 stage 2 edits with a read-only `.scratch/` script that matches the literal tags `ASSUMPTION:` and `VERIFY:`. `tasks.md` was recounted at the same time. Stage 1 of #108 added one `tasks.md` register row for a label that was already in the file (line 107). Stage 2 added no tagged label and closed three `testing.md` `VERIFY:` labels (the fake mail sink's form and the `make test` versus Compose question), whose register rows stay as `resolved`; this file's own edits add no tagged label.

Label locations (1-based line numbers, read after the #108 stage 2 edits):

- `_docs/specs.md` — `ASSUMPTION:` 226, 319, 410, 436, 438, 440. `VERIFY:` 36, 39, 78, 90, 294, 299, 319, 381, 390, 410, 415, 416, 417 (14 occurrences on 13 lines; line 410 carries two).
- `_docs/architecture.md` — `ASSUMPTION:` 25, 29, 44, 45, 51, 53, 72, 83, 92, 115, 132, 179, 198, 225, 231, 246, 254, 279, 281, 300, 313, 350, 367, 370, 379, 393, 409, 424, 449 (38 occurrences on 29 lines). `VERIFY:` 5, 14, 29, 49, 59, 60, 61, 62, 63, 80, 81, 86, 87, 94, 104, 244, 246, 262, 277, 279, 287, 288, 289, 290, 291, 292, 293, 294, 300, 313, 329, 332, 344, 346, 362, 366, 369, 374, 385, 399, 403, 409, 413, 414, 419, 420, 421, 428, 430, 431, 433, 449, 473, 474, 476 (72 occurrences on 55 lines; lines 29, 80, 81, 87, 262, 287, 332, 344, 362, 369, 374, 409 and 421 carry two or more).
- `_docs/api.md` — `ASSUMPTION:` 82, 83. `VERIFY:` 54, 79, 82, 83, 169, 216, 346, 350, 351, 352, 353, 354 (13 occurrences; line 346 carries two).
- `_docs/testing.md` — `ASSUMPTION:` 5, 100, 114, 171, 256, 286, 404, 411, 412, 413, 414, 415, 416, 417, 418. `VERIFY:` 5, 130, 131, 198, 252, 258, 262, 264, 274, 278, 294, 296, 300, 419, 420, 421, 422, 423, 424, 425, 426, 427 (22 occurrences on 22 lines; the fake mail sink's form, formerly at lines 128 and 132, and the `make test` versus Compose question, formerly on line 129, were closed in #108 stage 2).
- `_docs/tasks.md` — `ASSUMPTION:` 95, 301. `VERIFY:` 107, 191 (four labels, task 37), 301 (two labels on the line).
- `_docs/roadmap.md` — `ASSUMPTION:` none as a label (line 291 mentions the tag in prose). `VERIFY:` 69, 70, 125, 126, 139, 217.
- `_docs/project-brief.md` — none.

## Stage 6 checklist

| Item | Result | How checked |
|---|---|---|
| All 12 criteria appear | PASS | [`_docs/rubric.md`](rubric.md) has 12 `######` criterion headings; the map has exactly 12 data rows in the same order with the same names (`.scratch/check_map.py`) |
| Max points total 24 and the pass mark is 10 | PASS | [`_docs/rubric.md`](rubric.md) line 4 and the per-criterion headings; the map's Max column is 2+2+2+2+2+2+2+2+3+2+1+2 = 24, and the total line states 24/10 |
| Nothing is unmapped | PASS | Every map row has at least one `task N` and at least one resolving document link; the Gaps table is empty. The Application/task 15 difference is recorded as D1, and the row is still covered by tasks 1, 3-12 and 14 (and 37, 38). Rerun after #99: 12 rows, each with at least one existing task |
| Every task number exists | PASS | `.scratch/check_map.py` matched every `task N` to a `## N.` heading in [`_docs/tasks.md`](tasks.md) and found no number outside 1-38 (rerun after #99 with `.scratch/check_plan99.py`; the headings were 1-38). Task 39 was added in #108 stage 2 and its heading exists, so the headings are 1-39 and every `task N` in this file is within them |
| Every risk has a mitigation | PASS | Top risks has 10 rows (R1-R10, more than 8); every row has a non-empty mitigation, owner and residual risk. Human-only actions are labelled `human` |
| All open questions and assumptions are collected | PASS | Corrected label-only recount: 6 specs assumption labels (5 meanings; `specs.md:Q2` covers line 152), 38 architecture A tags, 2 api A1 entries, 14 tagged testing T-A occurrences (8 items), 7 tasks entries (1 assumption row from 2 labels, task 17's OIDC provider `VERIFY:` row, task 37's four SES `VERIFY:` rows and the Juice Shop lockfile row, recounted after #108 stage 2), 0 roadmap labels, plus 2 self-assumptions = 113 register entries after the #108 stage 2 recount (the `tasks.md` OIDC provider VERIFY row added in stage 1; the two `testing.md` mail VERIFY rows were added in #107, and one of them is now resolved); every difference is explained and the locations are listed above |
| Links resolve | PASS | `.scratch/check_links.py` checked every relative Markdown link in this file and the new README line; all resolve |
| File limit | PASS | For #99, `git status --short` before the commit lists only `_docs/tasks.md` and `_docs/plan-summary.md` as this issue's changes. (At the first Stage 6 commit the limit was `_docs/plan-summary.md` and `README.md`.) |

## Gaps

None. Every criterion has at least one `_docs/tasks.md` task and at least one existing repository document. The Application/task 15 difference is a source discrepancy (D1), not an unmapped criterion.
