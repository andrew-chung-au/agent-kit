# Impact of the final project criteria on the VulnTriage plan (2026-10-16)

Author: Software Engineer, for issue #11. Sources read for this report:
`_docs/rubric.md` (replaced in this issue, from the criteria pasted in #11),
`_docs/project-brief.md`, `_docs/specs.md`, `_docs/planning-process.md`,
`_docs/rubric-evidence.md`, `_docs/ai-usage-report.md`,
`_docs/reviews/2026-10-16-plan-review.md`, `README.md`, `AGENTS.md`,
`agent-kit.conf`, `Makefile`, `.github/workflows/verify.yml`,
`.opencode/agents/`, `.claude/agents/`, and issues
[#1](https://github.com/andrew-chung-au/vuln-triage/issues/1) to
[#11](https://github.com/andrew-chung-au/vuln-triage/issues/11)
(`make issue-dump`, dumped to `.scratch/issue-<n>.json`).

Labels used: **ASSUMPTION** for a judgement, **VERIFY:** for an external fact I
could not confirm from this repo. No application code, config, telemetry or
issue edits are made by this report; everything below is a proposal.

## 0. What changed, in one paragraph

The pasted criteria replace a 14-criterion draft with **12 criteria worth 24
points, 10 to pass**. I counted them from the pasted text, now in
`_docs/rubric.md`: twelve `######` criterion headings, whose maximum points sum
to 24 (10 of them worth 2, CI/CD worth 3, Alerting on User Impact worth 1),
which matches the page's own line "There are 12 criteria worth 24 points. You
need 10 points to pass." Four
things follow. (1) Four of the 12 criteria are documentation- or
process-shaped (Problem Description, Product Specification, Agent Team
Specification, Context Management = 8 points) and are the cheapest points in
the rubric; the plan already has most of the material. (2) Three criteria are
new and have **no** counterpart anywhere in the current plan: Observability,
Alerting on User Impact, On-Call Agent (5 points). (3) The rubric no longer
scores an OpenAPI contract, an MCP server, n8n, security-hardening artefacts or
an AI-usage report — five things the current plan spends effort on. (4) The
hardest criteria (Application, Containerization, Deployment, CI/CD = 9 points)
all need a working application and a Docker-capable environment, which this
container does not have (`AGENTS.md` § Project gotchas).

**VERIFY:** the page's own "finalised 2026-10-17" date is one day *after*
today (2026-10-16) and the paste carries no URL, so the date and the whole
pasted text are unconfirmed against the live page. Everything below assumes
the paste is accurate. VERIFY: whether an anonymous reviewer can read the repo
and its issues — my visibility check ran as an authenticated `gh` user.

## 1. Criteria table (one row per final criterion)

Effort key (ASSUMPTION): S = under ~2 hours, M = ~2 to ~6 hours, L = more than
~6 hours, for one developer, excluding review time. Effort is my judgement, not
a measurement.

| Criterion | Max | Where the plan covers it today | Gap to full marks | Proposed change | Effort |
|---|---|---|---|---|---|
| Problem Description | 2 | `README.md` (2 lines of description) and `_docs/project-brief.md` lines 1-7 (problem statement, workflow) | README says what the project is but not the system functionality or expected behaviour; the criterion is about the README | Add to `README.md`: problem, functionality, expected behaviour, one-command run, status, links to the spec | S (ASSUMPTION) |
| Product Specification | 2 | `_docs/specs.md` (132 lines, 12 user stories, US-1..US-12, edge cases E1-E5); repo and issues are public (verified, §9) | `specs.md` is a draft (decision in #3); its acceptance criteria live in prose, not as tracker tasks; agent use of the tracker is visible on only 3 of 11 issues (#1, #2, #11) | Resolve #3-#9, then treat `specs.md` as approved; for each user story add one tracker issue whose body carries its acceptance criteria, and link issue → story | S (ASSUMPTION) |
| Agent Team Specification | 2 | Role files exist in both layers: `.opencode/agents/{pm,qa-engineer,rubric-auditor,software-engineer}.md` and `.claude/agents/{...}.md`; the process is in `_docs/agent-kit/process.md` and `_docs/agent-kit/team/` | No single document names the team and how the roles hand work over; role files still contradict each other on who writes the usage log (#10, open) | Write `_docs/agent-team.md` (roles, handover, who may write what) and link it from `README.md`; fix #10 first so the doc describes one rule | S (ASSUMPTION) |
| Context Management | 2 | `AGENTS.md` (81 lines) points at `_docs/agent-kit/` (line 6, line 81) and `_docs/project-brief.md` (line 39) | `AGENTS.md` names the kit as a folder but not its modular pages (process, team files, procedures); it also does not link `README.md` or the review history | Add an index section to `AGENTS.md` listing each modular doc and its purpose (protected file: BEFORE/AFTER in §7) | S (ASSUMPTION) |
| Application | 2 | Nothing. No code exists: `AGENTS.md` line 8 ("no application code"), `agent-kit.conf` `TEST_CMD=""`, `Makefile` has no `install`/`run` target. The shape is fixed in `_docs/project-brief.md` lines 34-38 (React, FastAPI, SQLAlchemy, Compose, GH Actions) | The whole application: frontend, backend, database, connected, running locally with a single command | Scope the MVP to the smallest slice that is real: register asset → dependencies read → findings ranked → dashboard list. `docker compose up` as the single command | L (ASSUMPTION); blocked by Docker, §8 |
| Testing | 2 | Strategy only, in `_docs/planning-process.md` § Stage 4 (unit, integration, e2e, LLM evaluation, security fixtures); `agent-kit.conf` `TEST_FILES` already names the test patterns | No tests exist and no test command is configured; integration tests are specified against "real Postgres via Docker Compose" | Write `_docs/testing.md` (Stage 4), set `TEST_CMD` to a `make test`, keep unit tests runnable without Docker, run integration tests on CI | M (ASSUMPTION) |
| Containerization | 2 | Compose is in the fixed stack (`_docs/project-brief.md` lines 36-37) and required by Stage 4's integration tests; nothing else | No Dockerfile, no Compose file; cannot be built or shown here | Author `Dockerfile` + `compose.yaml` for app, Postgres, n8n; prove "single command" on a Docker-capable machine or CI | M (ASSUMPTION); blocked by Docker, §8 |
| Deployment | 2 | Nothing. `_docs/project-brief.md` line 36 names "production" as an environment but no host; the hosting decision is open in #9 | No host chosen, no deployed URL, no demo | Answer #9 (its recommendation: one VM running the same Compose file), then deploy dev and prod from it | M (ASSUMPTION); depends on #9 and Docker, §8 |
| CI/CD | 3 | `.github/workflows/verify.yml` runs `make verify` on every push and pull request (a real CI job, but it runs no tests because `TEST_CMD` is empty) | Only the 1-point rung ("CI runs the tests automatically on every pull request") is in reach; nothing deploys anywhere, no dev environment, no manual production deploy | See §4: add a test job to CI, auto-deploy to dev on `main`, manual `workflow_dispatch` deploy to production behind an environment protection | M (ASSUMPTION) |
| Observability | 2 | Nothing. No stage, document or task mentions metrics, traces or a telemetry store | No instrumentation, no shared trace ID, no UI to view signals, no rule about what must stay out of telemetry | New stage after Testing; see §3.1 proposals | L (ASSUMPTION) |
| Alerting on User Impact | 1 | Nothing. The plan has notifications to humans (US-8, US-9) and a weekly digest, but no monitoring or alerting | No alert rule, no alert destination | One candidate alert in §3.2 | S (ASSUMPTION) once Observability exists |
| On-Call Agent | 2 | Nothing. The repo has agent *roles* for building the project, which is a different thing from a responder agent | No agent that wakes on an alert and fixes something; no reproducible failure to point it at | One candidate failure in §3.3; reuse the project's own agent kit (`_docs/agent-kit/`) as the responder's toolset | M (ASSUMPTION) |

Totals: 24 points available, 10 needed. The four documentation criteria are
worth 8 points; the three observability/alerting/on-call criteria are worth 5;
of the remaining 11 points, Application, Containerization, Deployment and CI/CD
(9 points) need a built and deployed application, while Testing (2 points)
needs built code and tests but no deployment.

## 2. No longer scored

Each of these is in the current plan and earned points under the 14-criterion
draft in the previous `_docs/rubric.md`. None appears in the 12 final
criteria.

### 2.1 OpenAPI contract (`_docs/openapi.yaml`, Stage 3)

- **Keep in MVP:** the contract is the shared truth for the frontend, the
  backend and any automation, which is what keeps Application (2 points) and
  Testing (2 points) cheap to get right. Cost: one planning stage plus keeping
  it in step with the code.
- **Later phase:** generate it from the FastAPI app once the endpoints exist;
  loses the "contract first" benefit, costs less total time.
- **Drop:** describe endpoints in `_docs/specs.md` and let the code be the
  contract. Cheapest, but frontend and backend drift is found by tests rather
  than by reading, and no criterion pays for that either way.

### 2.2 MCP server (`_docs/project-brief.md` lines 28-32, 37; `_docs/specs.md` US-12)

- **Keep in MVP:** serves the brief's success criterion "an AI assistant can
  answer 'which assets are affected by this CVE?'". Cost: a separate Python
  service, its own read-only token, its own security boundary, tests
  (`_docs/reviews/2026-10-16-plan-review.md` findings 11 and 14, issue #8).
- **Later phase:** the read-only tools can be added on top of a finished API
  without touching the app; the boundary is easier to design once the API is
  real.
- **Drop from the MVP:** no criterion mentions an assistant integration. The
  same information is available through the dashboard and the API.

### 2.3 n8n (`_docs/project-brief.md` step 6 and line 37; `_docs/specs.md` US-7, US-8, US-9)

- **Keep in MVP:** daily KEV/EPSS refresh, owner notification and the GitHub
  issue for a new top-priority finding are the events that Alerting on User
  Impact (1 point) and, indirectly, the on-call agent (2 points) hang off.
  Cost: a third service in Compose and a second write token (open decision 1
  in #7, and #8 depends on it).
- **Later phase:** a scheduled job inside the backend covers the refresh and
  the notifications for the demo; n8n workflows (and the "exported as JSON
  into the repo" requirement in #7) wait.
- **Drop:** automatic refresh and notification disappear, which removes the
  event an alert would fire on. Not recommended.

### 2.4 Security-hardening artefacts (previous draft criterion 13: PR audit output, deterministic security-scan findings, agent/extension security notes, operational diagnosis output, AI tool/data policy)

- **Keep in MVP:** produces the artefacts, none of which is scored now.
- **Later phase:** the artefacts can be generated near the end from logs that
  already exist.
- **Drop the artefacts, keep two behaviours:** the fix-version guardrail and
  "advisory text is untrusted data" (`_docs/project-brief.md` lines 19-20,
  `planning-process.md` § Stage 2) are already in the plan and are cheap; the
  new rule that no customer data or credentials go to telemetry is required by
  Observability (2 points), so it is behaviour, not an artefact, and should
  stay in the MVP.

### 2.5 AI usage report (`_docs/ai-usage-report.md`, 7 TODO sections)

- **Keep in MVP:** a short, filled-in report is cheap evidence of the AI
  workflow, and the skeleton already exists. But note its header says
  "rubric criterion 2", and criterion 2 is now Product Specification — the
  file as written points at the wrong criterion (§7).
- **Later phase:** fill it in at the end.
- **Drop:** rely on `_docs/ai-usage-log.md` (236 lines, append-only, already
  maintained), the role files, `_docs/prompts/` and the issue history. Nothing
  in the 12 criteria asks for the report.

### Decision needed (no longer scored)

1. OpenAPI contract: keep in MVP / generate later / drop?
2. MCP server: keep in MVP / later phase / drop from the MVP?
3. n8n: keep as a service / replace with an in-backend scheduler / drop?
4. Security artefacts: drop the artefacts, keep the telemetry-data rule and
   the guardrail?
5. AI usage report: fill in the skeleton / later phase / delete the file?

**Recommendation.** Take 1 = generate later (Stage 3 stays in the plan as a
short stage, not a frozen contract), 2 = drop from the MVP, 3 = keep n8n but
with one workflow only (daily refresh + notify), 4 = yes, drop the artefacts
and keep the behaviours, 5 = delete the skeleton and keep `_docs/ai-usage-log.md`
plus `_docs/prompts/`. That frees roughly the time Observability, Alerting and
the On-Call Agent need (5 points) without giving up any point the rubric pays
for. Decisions 2 and 3 change `_docs/project-brief.md` and `_docs/specs.md`,
which are protected: the BEFORE/AFTER text is in §7.

## 3. New requirements in the plan

The final criteria add three things the plan does not mention at all. All of
this section is proposals only; nothing here is implemented, configured or
instrumented.

### 3.1 Observability (2 points)

The criterion needs: one key user journey instrumented with metrics, traces and
structured logs that **share a trace ID**; no customer data or credentials in
telemetry; signals collected, stored and **viewable in a UI**.

- **Proposed key user journey (PROPOSAL):** "a new top-priority finding reaches
  its owner". It is the journey the product exists for
  (`_docs/project-brief.md` workflow steps 2-6), it crosses every component
  (backend match and rank → n8n → notification → dashboard status), and it has
  an outcome a human cares about. Alternative considered: the dashboard load;
  rejected as it touches one component and misses the alert trigger.
- **Proposed signals (PROPOSAL):** a metric for findings entering the top tier,
  a metric for notification delivery success and latency, a trace per scan
  request carrying a trace ID through the backend call, the n8n webhook and the
  notification, and a structured log line per state change. ASSUMPTION: a
  single open standard (OpenTelemetry-compatible) can cover all three without
  a second dependency; VERIFY: which collector and UI are actually available
  and their licensing and cost.
- **What must stay out of telemetry (PROPOSAL):** advisory free text and
  advisory links; the LLM brief body (it quotes advisory text); asset
  repository URLs for private repos; owner e-mail addresses and chat handles;
  GitHub, OSV and LLM tokens; lockfile content; anything from
  `FORBIDDEN` in `agent-kit.conf` line 23-24. Permitted: package names and
  versions, vulnerability ids, tiers and scores, counts, timings, trace and
  span ids, asset ids and criticality flags. This list needs a human decision;
  it is the rule the criterion is graded on.

### 3.2 Alerting on User Impact (1 point)

- **Candidate alert (PROPOSAL):** "a top-priority finding was detected and the
  owner was not notified". Fires when the notification step for a finding that
  enters the top tier fails or does not complete within a window
  (ASSUMPTION: 30 minutes). It is user impact, not CPU: the thing a user
  cares about — the owner receiving the fix — silently did not happen. It
  reuses the US-8 idempotency rule so one alert per finding.
- **Alternatives considered:** feed staleness (an internal data condition, not
  user impact) and "assets scanned per day" (a volume metric, not impact).

### 3.3 On-Call Agent (2 points)

- **Candidate reproducible failure (PROPOSAL):** the daily refresh runs while
  the EPSS feed is unavailable or returns malformed data, so findings keep
  stale ranks, the new top-priority finding is never notified, and §3.2's
  alert fires. Reproducible from a stored fixture: the E3 case already in
  `_docs/specs.md` ("a feed is unavailable") plus a malformed-response
  fixture in `_docs/planning-process.md` § Stage 4 ("external APIs replaced by
  stored response fixtures"). The responder agent then re-runs the refresh
  against the last-known-good feed data, verifies the finding re-enters the top
  tier, confirms the notification, and writes what it did to the run log.
  This is reproducible, safe, and has a checkable end state.
- **Alternatives considered:** an OSV outage (E3 covers the behaviour but the
  fix is "wait", which is a weaker story for an agent) and a rank inversion
  after a tie-break change (real, but harder to reproduce on demand).

### 3.4 What this costs in the plan

A new planning stage between Testing and Containerization ("Telemetry and
alerting"), plus one more stage or task for the responder agent, and a rule in
`_docs/specs.md` for the telemetry data boundary. None of this can be written
before the Decisions in §2 and §5, because the alert fires on the notification
path, which §2.3 decides.

## 4. CI/CD

Current state: `.github/workflows/verify.yml` is one job on `ubuntu-latest`
that runs `make verify` on every push and pull request, with
`permissions: contents: read`. Because `agent-kit.conf` sets `TEST_CMD=""`, it
runs no tests yet (1-point rung at best, once `TEST_CMD` is set).

To reach the 3-point rung the pipeline needs two deploy targets and a
rollback path:

- **Dev environment (automatic):** a target that is safe to overwrite on every
  merge to `main`. Cheapest shape: one VM running the same
  `docker compose` file used for integration tests (the option #9 recommends),
  reached over SSH from the workflow, plus a Compose-based dev Postgres.
  Deployment = pull the image, `docker compose up -d`, run a smoke check
  against the health endpoint. ASSUMPTION: a single VM is enough for the demo
  load; VERIFY: provider, price and whether a public hostname and TLS
  certificate are available without extra accounts.
- **Production environment (manual deploy):** the same Compose file, a second
  host, deployed only by `workflow_dispatch` with an `environment: production`
  protection so a human approves each run, and with the production secrets
  (`POSTGRES_PASSWORD`, `LLM_API_KEY`, `GITHUB_TOKEN`, `OSV`/KEV keys) in the
  environment, never in the repo. The manual gate is what the criterion's
  third rung asks for.
- **Rollback path:** pin image tags per release (never `latest`); the deploy
  workflow records the previous tag in the deployment summary; a
  `workflow_dispatch` input `REF=<previous tag>` redeploys the previous image;
  database changes must be backwards compatible for one release so a rollback
  does not need a data restore; the runbook lives in `README.md` (criterion 8,
  Deployment, wants a reachable URL or a clear demo). ASSUMPTION: image-based
  deploys with
  a tag pin are enough; VERIFY: whether the chosen host supports pulling
  images or needs an SSH transfer.
- **Consequence for criterion 6 (Testing):** CI must run the unit tests on
  every pull request and the integration tests (Compose, Postgres) before the
  deploy steps, which means CI is also where the Docker-dependent checks run,
  because this container has no Docker (§8).

## 5. Scope options

Effort is my judgement against the page's "Roughly 20 hours of work" (VERIFY:
that figure is the page's own text; the paste gives no breakdown). Hours below
are rough and exclude review and waiting.

### Tier A — "Everything that is not infrastructure" (targets 1, 2, 3, 4, 5, 6)

- Criteria: Problem Description (2), Product Specification (2), Agent Team
  Specification (2), Context Management (2), Application (2), Testing (2).
- Expected points: **12 of 24** (pass at 10) — or 10 if the agent-team and
  context-management docs are thin.
- Effort: M for the four documentation criteria (they are near-done) + L for
  the application and its tests. Roughly 12-16h ASSUMPTION.
- Costs: no deployed URL, no containers, no telemetry, no alert, no responder.
- Risk: the page says "One application, taken all the way... It is one app
  that you specify, build, run locally, deploy, and make production ready"
  (paste, § What You Can Submit). A submission at this tier contradicts that
  sentence even though it passes on points.

### Tier B — Tier A + the deployment path (targets 1-9)

- Adds: Containerization (2), Deployment (2), CI/CD up to 3.
- Expected points: **19 of 24**.
- Effort: + M for Compose, + M for deploy and CI/CD. Roughly 18-20h total,
  which uses the whole budget. ASSUMPTION.
- Costs: no telemetry, no alerting, no on-call agent (the 5 points the rubric
  added most visibly), and no slack for the review findings in
  `_docs/reviews/2026-10-16-plan-review.md`.

### Tier C — Tier B + the three new criteria (targets all 12)

- Adds: Observability (2), Alerting on User Impact (1), On-Call Agent (2).
- Expected points: **24 of 24**, and the only tier that reaches the full set.
- Effort: + L for instrumentation and a UI to view signals, + S for one alert,
  + M for the responder agent. Roughly 26-30h total. ASSUMPTION: this is over
  the stated 20 hours, so Tier C needs either a smaller Application slice or an
  acceptance that it overruns.
- Costs: the smallest possible application (fewest user stories), and the
  OpenAPI/MCP decisions from §2 cut early.

### Decision needed (scope)

1. Tier A, B or C?
2. If B or C: how much of the 12 user stories in `_docs/specs.md` fits beside
   the infrastructure and telemetry work?
3. If C: is going over ~20 hours acceptable, or does the application shrink?

**Recommendation: Tier C, with the application cut to a narrow slice.** The
four documentation criteria (8 points) are nearly free, and the three new
criteria are 5 points that no existing plan work competes for once the
Decisions in §2 are taken. Tier B looks safer on hours but spends the whole
budget on 2 points each for containers and deployment and leaves the three
criteria the final page is named for. Tier A passes on points and contradicts
the page's "taken all the way" wording, so it is not worth the risk.

## 6. Open issues #3-#10

| Issue | Verdict | One-line reason |
|---|---|---|
| [#3](https://github.com/andrew-chung-au/vuln-triage/issues/3) define which "fixed version" applies | still valid | The spec is ambiguous about fixed versions regardless of the rubric, and the guardrail and auto-close both depend on it |
| [#4](https://github.com/andrew-chung-au/vuln-triage/issues/4) CVE lookup through advisory aliases | still valid | Rubric-independent correctness of US-3/US-12; if the MCP server leaves the MVP, only the US-3 part remains |
| [#5](https://github.com/andrew-chung-au/vuln-triage/issues/5) feeds, matching and ingestion gaps | still valid | Feed and ingestion edge cases are unaffected by the criteria; needed before any scan can produce real findings |
| [#6](https://github.com/andrew-chung-au/vuln-triage/issues/6) status model, brief display, audit trail | still valid | The status model and audit trail are what the dashboard (Application) shows; rubric-neutral |
| [#7](https://github.com/andrew-chung-au/vuln-triage/issues/7) notifications, due dates, routing | still valid | Still the right questions, and its Decision 1 now also protects criterion 2's "agents used the tracker" evidence if finding issues land in this repo |
| [#8](https://github.com/andrew-chung-au/vuln-triage/issues/8) security boundaries for advisory text and the MCP token | needs change | The advisory-text criteria stay and gain a telemetry rule; the three criteria concerning US-12 (MCP output marks advisory text as untrusted, finding 11; a write with the MCP token is rejected, and one acceptance line per tool, finding 14) are moot if §2.2 drops the MCP server, and the dependency on #7 weakens |
| [#9](https://github.com/andrew-chung-au/vuln-triage/issues/9) carry into later stages | needs change | Its rows are still valid, but it cites old rubric numbers ("criterion 10", "rubric 11", "rubric 14") that must be renumbered, its hosting decision is now on the critical path for Deployment and CI/CD, and the Docker row (finding 12) now blocks three criteria, not one |
| [#10](https://github.com/andrew-chung-au/vuln-triage/issues/10) same-shape log contradiction in role files | still valid | Criterion 3 is graded on the agent team being described consistently, and the contradiction is exactly what a reviewer would see |

Notes on the issue data, not acted on: #3-#10 have no comments yet, so none of
them shows agent use of the tracker; and #10's body contains literal `\n`
sequences where newlines were intended (seen in the `make issue-dump` output),
which makes it hard to read.

## 7. Documents that need to change

Nothing below is changed by this issue; these are proposals. The protected
files (`AGENTS.md`, `_docs/project-brief.md`, `_docs/specs.md`) are given as
before/after text only.

### 7.0 `AGENTS.md` (PROTECTED — before/after text only; proposed separately for the handover)

Criterion Context Management (2 points) is graded on `AGENTS.md` pointing to
modular docs. Today it names `_docs/agent-kit/` as a folder but never links its
pages, nor `README.md`, nor the agent-team document proposed in §1.

- **BEFORE** (line 6, the Layout paragraph):
  > Layout: `AGENTS.md`, `agent-kit.conf`, `Makefile`, `opencode.json`, `.opencode/agents/` (OpenCode role definitions), `_docs/agent-kit/` (agent kit, version 1.9), `_docs/project-brief.md` (project brief, to be written in planning).

- **AFTER** (same paragraph, plus a following "Where to read more" list):
  > Layout: `AGENTS.md`, `agent-kit.conf`, `Makefile`, `opencode.json`, `.opencode/agents/` (OpenCode role definitions), `_docs/agent-kit/` (agent kit, version 1.9), `_docs/project-brief.md` (project brief, to be written in planning).
  >
  > Where to read more:
  > - `README.md` — the project in one page and the planning document index
  > - `_docs/rubric.md` — the final project criteria this project is graded against
  > - `_docs/reviews/` — plan reviews and rubric-impact reviews
  > - `_docs/agent-kit/process.md` — how one issue is worked end to end
  > - `_docs/agent-kit/team/` — one file per working role (`pm.md`, `software-engineer.md`, `qa-engineer.md`; the rubric auditor is `.opencode/agents/rubric-auditor.md`)
  > - `_docs/agent-kit/procedures/` — how to verify, how to ask the human
  > - `_docs/agent-kit/environments.md` — which environment runs where, and what each has
  > - `_docs/agent-team.md` — this project's agent team and handover rules (once written)

### 7.1 `_docs/project-brief.md` (PROTECTED — before/after text only)

Two changes: state the telemetry/alerting/responder requirement (it is absent
today, and 5 of 24 points depend on it), and record the §2 decisions about the
MCP server.

- **BEFORE** (`_docs/project-brief.md` lines 28-32):
  > Also: a web dashboard of findings per asset with status (open / risk accepted /
  > fixed) and an audit trail. An MCP server with read-only tools
  > (list_top_exposures, which_assets_affected, get_finding, get_asset) that calls
  > the API with its own read-only token. No write tools in the MVP; risk
  > acceptance is a human decision in the dashboard.

- **AFTER** (if Decision 2 = drop from the MVP):
  > Also: a web dashboard of findings per asset with status (open / risk accepted /
  > fixed) and an audit trail. No MCP server in the MVP: the same read-only tools
  > (list_top_exposures, which_assets_affected, get_finding, get_asset) are added in
  > a later phase, on top of the finished API, with their own read-only token. No
  > write tools in any phase; risk acceptance is a human decision in the dashboard.

- **BEFORE** (after workflow step 7, line 26, before line 28):
  > 7. Re-scan: a finding closes automatically when a re-scan shows the fixed
  >    version is in place.

- **AFTER** (adds step 8):
  > 8. Watch and respond: one key user journey is instrumented with metrics, traces
  >    and structured logs sharing a trace ID; an alert fires when a top-priority
  >    finding does not reach its owner; a responder agent wakes on that alert and
  >    fixes the cause. No customer data or credentials are sent to telemetry.

### 7.2 `_docs/specs.md` (PROTECTED — before/after text only)

Add three stories and one edge case; US-12 changes or goes if the MCP server
is dropped.

- **BEFORE** (`_docs/specs.md` lines 90-96, US-12, the whole story):
  > ### US-12: Read-only assistant answers exposure questions
  > As a developer using an AI assistant, I can ask "which assets are affected by
  > this CVE?" through the read-only MCP server (tools: `list_top_exposures`,
  > `which_assets_affected`, `get_finding`, `get_asset`).
  > - Acceptance: asking for a known CVE returns the affected assets; asking for
  >   an unknown CVE returns an empty result, not an error; the MCP server offers
  >   no write operations.

- **AFTER** (if the MCP server leaves the MVP; replaces lines 90-96):
  > ### US-12: Read-only assistant answers exposure questions (later phase)
  > Not in the MVP. In a later phase, as a developer using an AI assistant, I can
  > ask "which assets are affected by this CVE?" through the read-only MCP server
  > (tools: `list_top_exposures`, `which_assets_affected`, `get_finding`,
  > `get_asset`); each tool gets its own checkable acceptance line at that point.
  > - Acceptance: asking for a known CVE returns the affected assets; asking for
  >   an unknown CVE returns an empty result, not an error; the MCP server offers
  >   no write operations.

- **AFTER** (append after US-12, before `## Non-goals`):
  > ### US-13: The notification journey is instrumented
  > As a security lead, I can see whether a top-priority finding reached its owner,
  > as metrics, traces and structured logs that share one trace ID, viewable in a UI.
  > - Acceptance: one scan-to-notification journey emits a metric, a trace and a
  >   structured log line carrying the same trace ID; the UI shows them side by side.
  >   No telemetry payload contains advisory text, owner contact details, repository
  >   URLs, lockfile content or any credential.
  >
  > ### US-14: An alert fires when a top-priority finding is not notified
  > As an asset owner, if my finding is never delivered to me, an alert fires so
  > someone looks at it.
  > - Acceptance: a top-priority finding whose notification fails or does not
  >   complete within the agreed window fires exactly one alert naming the finding;
  >   a successful notification fires none.
  >
  > ### US-15: A responder agent wakes on the alert and fixes it
  > As a security lead, an agent reacts to the US-14 alert and restores the journey.
  > - Acceptance: from a stored fixture in which the feed is unavailable, the alert
  >   fires, the agent re-runs the refresh against last-known-good data, the finding
  >   reaches the owner, and the agent's actions are written to the run log; the
  >   same fixture run without the agent leaves the finding undelivered.

- **AFTER** (append a row to `## Edge cases`):
  > | E6 | A telemetry backend is unavailable | Buffer in-process and retry; findings, notifications and alerts are unaffected; the gap is visible in the UI |

### 7.3 `_docs/planning-process.md` (not protected, propose only)

- § Stage list: add a stage after Stage 4 for telemetry and alerting, and name
  the responder agent as a task rather than a stage; add dev/prod deploy and
  rollback to Stage 5 (tasks) or the new stage.
- § Stage 6, line 113: "all 14 criteria appear" → "all 12 criteria appear"
  (and the rubric sum is 24 points, 10 to pass); the stray "Also update the
  Reviewer prompt's reading list..." text at the end of that checklist
  (review finding 18, issue #9) should move to its own line.
- § Inputs, line 7-8: unchanged, but `README.md` should link
  `_docs/reviews/2026-10-16-final-rubric-impact.md` (the planning process
  asks for links to every planning file it creates).
- § How to work, line 22 ("For each planning file you create, add a link to it
  in README.md"): the agent-team document (`_docs/agent-team.md`, proposed in
  §1) needs a stage or a task of its own, so it does not fall between the
  files.

### 7.4 `_docs/rubric-evidence.md` (not protected, propose only)

The table has 14 rows matching the old draft (lines 11-24), all `MISSING` with
the gap "no audit run yet". It must be regenerated for the 12 final criteria
by the Rubric Evidence Auditor (`.opencode/agents/rubric-auditor.md`, via the
`update-rubric-evidence` skill) after this rubric swap, not by hand: the file
says only that auditor updates it. Row mapping for review: 1 Problem
Description → 1; 2 AI-assisted development workflow → dropped (evidence now
lives in `_docs/ai-usage-log.md`); 3 Technologies and architecture → split into
Application and Containerization; 4 Frontend implementation and 6 Backend
implementation → Application; 5 API contract and 12 Agent extension pack →
dropped; 7 Database integration → Application; 9 Integration testing → Testing;
8 Containerisation → Containerization; 10 Deployment → Deployment;
11 CI/CD pipeline → CI/CD; 13 Security/audit/DevOps hardening → dropped;
14 Reproducibility → split across Containerization, Deployment and CI/CD.
Five rows are new with no old equivalent: Agent Team Specification, Context
Management, Observability, Alerting on User Impact, On-Call Agent.

### 7.5 `_docs/ai-usage-report.md` (not protected, propose only)

If §2.5 recommendation 5 is taken, the file is deleted and `README.md` line 17
is removed with it. If it is kept, its header is now wrong and must change:

- **BEFORE** (line 3): "Skeleton for the AI-assisted workflow report (rubric criterion 2)."
- **AFTER**: "AI-assisted workflow notes. Not a scored criterion in the final rubric
  (see `_docs/rubric.md`); kept as supporting evidence for Product Specification and
  Agent Team Specification. The append-only record is `_docs/ai-usage-log.md`."

## 8. Blockers: no Docker in this container

`AGENTS.md` § Project gotchas states Docker is unavailable here, and
`_docs/agent-kit/environments.md` line 20 lists "Docker: Not available" for
the local-sandbox profile. That blocks, directly:

- **Containerization (2 points)** — the criterion is "runs via Docker or Docker
  Compose and starts with a single command"; nothing can be shown.
- **Application (2 points), the second clause** — "runs locally with a single
  command" is the Compose path here.
- **Testing (2 points), the integration half** — `_docs/planning-process.md`
  § Stage 4 specifies integration tests against real Postgres via Compose.
- **Deployment (2 points) and CI/CD (3 points)** — building the image and
  running Compose is the deploy mechanism proposed in §4, and the deploy
  itself needs a Docker-capable host either way.

Not blocked: the four documentation criteria, Alerting's rule design, and the
unit-test half of Testing.

Options, from `_docs/agent-kit/environments.md`:

1. **Move the project to a Codespaces profile** (`environments.md` § Codespaces,
   line 23; the profile table line 13-21 lists Docker as available there, and
   line 27 notes the codespace token can push). Changes the Environment setting
   in `AGENTS.md`.
2. **Add Docker to the devcontainer recipe** (`.devcontainer/devcontainer.json`
   and `setup.sh`, called the container recipe in environments.md line 36;
   `setup.sh` runs from `postCreateCommand` in `devcontainer.json` line 26).
   A DinD or socket-mounting feature; needs the human, and it changes
   what "the sandbox" means.
3. **Keep this sandbox for docs and unit tests, and run every Compose-dependent
   check on GitHub Actions** — CI already exists (`.github/workflows/verify.yml`)
   and runners have Docker (VERIFY: Docker and Compose preinstalled on the
   `ubuntu-latest` runner image); `.github/` and `.devcontainer/` changes at the repo
   root ask for human approval per environments.md line 47.
4. **A dedicated Compose-based container recipe** for the services (environments.md
   line 57) so the agent can reach them without controlling Docker.

**Recommendation: option 3 now, option 1 for the build phase.** It costs nothing
today, keeps the protected AGENTS.md out of the diff, and it also matches §4:
the dev environment is a Compose host anyway. Option 1 is the better fit once
Application and Containerization are being built, because the reviewer will want
to run `docker compose up` locally.

## 9. Tracker evidence (Product Specification, 2 points)

Counts and visibility in this section were refreshed on 2026-10-17 with `gh`
(`gh repo view --json ...` and `gh issue list --state all --json
number,body,comments --jq ...`), before the Engineer's 2026-10-17 follow-up
comment on #11 was posted. They are a snapshot and will change as issues are
worked.

- **Is the repo public?** Yes (checked 2026-10-17). Check run:
  `gh repo view --json nameWithOwner,visibility,isPrivate,url` →
  `andrew-chung-au/vuln-triage`, `PUBLIC`, `isPrivate: false`,
  <https://github.com/andrew-chung-au/vuln-triage>.
  VERIFY: my check ran as an authenticated user; anonymous read access is
  implied, not demonstrated.
- **Are its issues public?** Issues are in the same public repository and are
  listed and readable by `gh issue list` /
  <https://github.com/andrew-chung-au/vuln-triage/issues>, which is what the
  criterion means by "publicly accessible task tracker". VERIFY: as above.
- **Do the tasks define acceptance criteria?** Yes: every issue except #10 has
  an `## Acceptance criteria` section with `- [ ]` items (11 boxes in #1, 7 in
  #2, 8 in #3, 6 in #4, 10 in #5, 8 in #6, 7 in #7, 6 in #8, 9 in #9, 14 in
  #11; counted on 2026-10-17 with `gh issue list --json body --jq`, lines
  matching `- [ ]` or `- [x]`). #10 has none — its body was
  filed with literal `\n` sequences instead of newlines, so its `## Goal` and
  `## Constraints` headings are not even parseable as headings.
- **Is there evidence that agents used the tracker?** Partly, and it is thin.
  Comment counts (2026-10-17, `gh issue list --json comments --jq`): #1 has 6
  role-prefixed comments (`PM:`/`Engineer:`/`QA:` x3/`Orchestrator:`), #2 has 4
  (`PM:`/`Engineer:`/`QA:`/`Orchestrator:`), #11 has 3 (`PM:` grooming,
  `Engineer:` handover, `QA:` PASS), #3-#10 have 0. So 3 of 11 issues show agent
  activity, and none of the open review issues #3-#10 has been worked at all.
- **Consequence:** criterion 2 is worth 2 points and is within reach: keep
  public issues, keep the `- [ ]` acceptance criteria in the bodies, and post
  the role-prefixed handover comments (the pattern already in `AGENTS.md`
  § Conventions). Note the risk in #7 Decision 1: n8n's *finding* issues would
  land in the same tracker, which is an argument for its recommended option C,
  a separate tracker repository.

## 10. Proposed new or changed issues (not created here)

1. Change `_docs/planning-process.md`: add the telemetry/alerting stage, the
   deploy and rollback work, and renumber Stage 6's "14 criteria" to 12.
2. Change `_docs/specs.md` (protected, needs approval): add US-13..US-15 and
   edge case E6; retitle or defer US-12 (BEFORE/AFTER in §7.2).
3. Change `_docs/project-brief.md` (protected, needs approval): add workflow
   step 8 and record the MCP decision (BEFORE/AFTER in §7.1).
4. Change issue #8: drop its three criteria concerning US-12 (MCP output
   marking, MCP-token write rejection, one line per tool) if the MCP server
   leaves the MVP; add the telemetry data rule to the advisory-text list.
5. Change issue #9: renumber the rubric references, make the hosting decision
   blocking for Deployment and CI/CD, and extend the Docker row.
6. New: answer the five Decisions in §2 and the scope Decision in §5 (one
   issue, human-owned).
7. New: expand `README.md` to the Problem Description wording, and add
   `_docs/agent-team.md` for Agent Team Specification.
8. New: the CI/CD work of §4 — CI test job, dev auto-deploy, manual production
   deploy, rollback runbook.
9. New: telemetry boundary list (§3.1) as its own decision issue.
10. New: re-run the rubric evidence auditor after this rubric swap (§7.4).