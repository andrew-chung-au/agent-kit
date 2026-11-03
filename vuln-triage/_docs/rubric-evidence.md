# Rubric evidence

Status of each of the 12 criteria (24 points, 10 to pass) in `_docs/rubric.md`,
with links to evidence that exists now. Only the Rubric Evidence Auditor
(`.opencode/agents/rubric-auditor.md` and `.claude/agents/rubric-auditor.md`,
via the `update-rubric-evidence` skill) updates this file. Planned work does
not count, and the log's claims alone are not accepted without opening the
linked evidence.

- Audit date: 2026-10-28 (fourth audit; previous: 2026-10-26 at `20a1fd8`,
  22 of 24).
- Tree audited: `83e0703` (`main`, merge of PR #269), the HEAD of the session
  branch `claude/ecstatic-newton-b7whlf` when this audit started (working tree
  clean). Changes since the last audited tree: 104 files (`git diff --stat
  20a1fd8 83e0703`), mainly the responder runtime and tests, the drill
  screenshots, the drill runbook and README.
- Auditor environment: Claude Code cloud session, no Docker, no AWS credentials,
  no access to `*.sslip.io` or YouTube. Nothing was run live by me and I ran no
  test suite. CI evidence comes from the Actions records and PR records read
  through the GitHub API; every screenshot cited below was opened and looked at
  (the ones I did not open are named).
- **Owner-captured** means the artefact is a committed screenshot or a recorded
  run made on the owner's machine. I can read the screenshot but cannot
  reproduce the run. The recorded video (https://youtu.be/B4OvaHqAeyI) was
  **not** watched by me; nothing below rests on it.
- `_docs/rubric.md` defines 12 criteria (24 points). The auditor role files'
  "14 criteria" wording is stale (tracked in issue #10).
- Status values: MET (top point level), PARTIAL (a lower non-zero level),
  MISSING (0 points).
- **Points currently evidenced: 24 of 24 (pass mark 10), with the caveats
  below.** Sum: criteria 1 to 8 at 2 each (16), CI/CD 3, Observability 2,
  Alerting 1, On-Call 2 = 24. The change from the 2026-10-26 audit (22) is
  On-Call Agent 0 to 2 only. Criteria 9 and 10 stay at their maximum, and the
  evidence for each is stronger than before (see the table), but a limit on each
  is stated and should be read with the score.
- **Independent QA of the final merged runtime code was not completed.** PR #266
  (the `cli` runtime fixes from the live drill) says in its own description that
  "the final combination has not had a clean QA pass": a QA run on `4ae7391` was
  voided when files changed under it, a run on `116850a` was killed by a usage
  limit, and the rule change, the prompt change and the redact-first change were
  not independently reviewed. Earlier QA rounds on #261 passed
  (`_docs/roadmap.md`, 2026-10-27 rows). The score for On-Call Agent rests on
  the recorded run, not on QA of the code that ran. It is not a rubric
  requirement, but it limits how far the code can be trusted.

## Score table

| # | criterion | max | score | status | change since 2026-10-26 (22/24) |
|---|---|---|---|---|---|
| 1 | Problem Description | 2 | 2 | MET | none |
| 2 | Product Specification | 2 | 2 | MET | none |
| 3 | Agent Team Specification | 2 | 2 | MET | none |
| 4 | Context Management | 2 | 2 | MET | none |
| 5 | Application | 2 | 2 | MET | none |
| 6 | Testing | 2 | 2 | MET | none |
| 7 | Containerization | 2 | 2 | MET | none |
| 8 | Deployment | 2 | 2 | MET [URLs owner-confirmed, committed screenshots] | none |
| 9 | CI/CD | 3 | 3 | MET [required checks now visible; one forward-looking risk stated] | none (evidence stronger) |
| 10 | Observability | 2 | 2 | MET [metric leg now shown on screen; limit stated] | none (evidence stronger) |
| 11 | Alerting on User Impact | 1 | 1 | MET | none |
| 12 | On-Call Agent | 2 | 2 | MET [scripted drill, owner-captured; QA of final code incomplete] | **+2** |
| | **Total** | **24** | **24** | | **+2** |

## Evidence by criterion

| criterion | max points | full-marks condition | status | evidence | gap |
|---|---|---|---|---|---|
| 1. Problem Description | 2 | "The README clearly describes the problem, the system functionality, and expected behaviour." | MET (2) | `README.md` at `83e0703`: "The problem", "What it does" and "Expected behaviour" sections; the reviewer table "Where to find each criterion" maps every criterion to evidence. The stale "responder planned / not built" wording found last time is gone: line 7, row 12 and the "Alerting & on-call agent" section now describe the real `cli` responder and say the Compose service is stub-only (line 265). | None for the level. README lines 30 and 257 still say the audit on file is 22 of 24 and predates the drill; this audit supersedes that, so those two sentences are now out of date (the README is not mine to edit). |
| 2. Product Specification | 2 | "A specification exists and there's a publicly accessible task tracker. The tasks define acceptance criteria and there's evidence that the agents used the tracker." | MET (2) | Spec `_docs/specs.md` (US-1 to US-15, each with Acceptance lines). Public tracker https://github.com/andrew-chung-au/vuln-triage/issues; PR #265 and #266 were read through the API in this audit; role-labelled comments and `_session-summaries/` files exist (the 2026-10-27 roadmap rows cite QA comment ids). | None for the level. Individual issue comments were not re-read this time. |
| 3. Agent Team Specification | 2 | "The project defines the agent team and process of how they work together." | MET (2) | `_docs/agent-team.md`; `_docs/agent-kit/process.md`; `_docs/agent-kit/team/` role files; definitions in `.claude/agents/` and `.opencode/agents/`. | None. Stale "14 criteria" wording (issue #10) is cosmetic. |
| 4. Context Management | 2 | "AGENTS.md exists and it also points to modular docs (process, teams, etc.)." | MET (2) | `AGENTS.md` "Where to read more" links the README, brief, spec, rubric, roadmap, reviews, process, team files, agent-team, procedures, environments, usage log and human tasklist; `CLAUDE.md` imports `AGENTS.md`. | None. |
| 5. Application | 2 | "Full-stack application works end to end: frontend talks to backend, data persists in a database. Application runs locally with a single command." | MET (2) | `backend/`, `frontend/`, `Makefile` `dev` and `demo` targets. The `telemetry` job in the `verify` workflow runs the backend journey on Postgres; the `verify` run on `83e0703` is `success` (https://github.com/andrew-chung-au/vuln-triage/actions/runs/40659992968). Committed screenshots of the running app: `docs/images/dashboard.png`, `assets.png`, `g7-vuln-triage-dev-findings.png`, and the drill screenshot `drill-b14-register-the-failing-asset-this-starts-the-scan.png` (registered asset, P1 finding; listed in README, not opened by me). | No recorded run I could re-check of a browser reaching the backend locally; the link rests on the owner-captured screenshots, the typed client, the OpenAPI conformance job and the CI journey. |
| 6. Testing | 2 | "Both unit and integration tests exist, run with a single command, and pass." | MET (2) | `make test` runs vitest, backend pytest and responder pytest. The `verify` workflow (jobs unit, sqlite-integration, postgres-integration, frontend, openapi-validation, telemetry, verify) is `success` on `83e0703` (run 40659992968), on the PR head `3690190` (run 40659731685) and on `103264d` (run 40659233021). PR #266's text gives "frontend 89, backend 561, responder 1638" for its head; I did **not** re-count them and did not run `make verify`. | None for the level. Postgres integration is `make test-integration`; `make test` includes SQLite integration cases. The Compose-based `alert` and `responder` jobs are not on every PR (see criterion 12). |
| 7. Containerization | 2 | "The full system, including the database, runs via Docker or Docker Compose and starts with a single command." | MET (2) | `backend/Dockerfile`, `frontend/Dockerfile`, `compose.yaml` (Postgres 16.4, migrations, backend, frontend, health checks), `make compose-up`. New this time: `docs/images/drill-b5-show-the-containers.png` (listed in README; not opened by me) shows the stack's containers healthy, owner-captured. Earlier: deploy logs and the owner's six-container observability run. | Unchanged limit: no recorded `make compose-up` session for the plain app (issue #137); the server runs the deploy variant (`compose.deploy.yaml`, GHCR images). |
| 8. Deployment | 2 | "The application is deployed and reachable at a public URL, or there's a clear demo with the deployment." | MET (2) [URL reachability owner-confirmed] | Terraform modules `terraform/bootstrap`, `deploy-roles`, `server`; public URLs https://dev.52-206-221-145.sslip.io and https://app.52-206-221-145.sslip.io in `README.md`; committed screenshots `g7-vuln-triage-dev-findings.png` (opened last audit) and `g6-vuln-triage-production-login.png`. The `deploy` workflow on `main` is `success` for the latest four runs (#71 to #74; #74 on `83e0703`: https://github.com/andrew-chung-au/vuln-triage/actions/runs/40659992978). | My sandbox cannot fetch `*.sslip.io`, so reachability stays owner-confirmed. Keep the nightly stop off until after grading. |
| 9. CI/CD | 3 | "CI runs tests, CD deploys to dev, and there's a manual deploy to production." | MET (3) | CI on every PR: `.github/workflows/verify.yml` (`on: [push, pull_request]`), green on the PR head `3690190` (run 40659731685). CD to dev on merge to `main`: `deploy.yml` push runs #71 to #74 all `success`. Manual production deploy: `deploy-prod` only on `workflow_dispatch` in `environment: production` (runs #31 to #33, earlier audit). Screenshots opened: `g5-github-settings-rulesets-protect-main.png` (re-captured in this range; opened) now shows the whole **Required status checks** list: `verify`, `unit`, `frontend`, `sqlite-integration`, `postgres-integration`, `telemetry`, `openapi-validation`, bypass list empty, PR required, force pushes and deletions blocked. That closes last audit's gap (b), which was that the required checks were not visible. `g1` and `g2` (production reviewer, deploy #33 waiting for review) were opened last audit. | (a) "Prevent self-review" is unticked and the only reviewer is the owner, so the production gate is a deliberate pause, not a second person; it still satisfies "manual deploy". (b) **New risk:** `deploy-prod` now runs `P-FLAG-GONE` (`ci/check_flag_gone.py`) before it deploys, and it fails while any tracked code mentions `VT_DEMO_DEFECT`, `demo_defect` or `notify_no_fix`. `backend/vulntriage/ingest/settings.py`, `backend/vulntriage/main.py` and `backend/vulntriage/mail/message.py` still do (grep in this audit), so a production promotion of the current tree would be refused until the cleanup (#161). The last production deploys (#31 to #33) predate the gate, and the README says the gate has not been proven in a real promotion (roadmap 2026-10-27: human B12). I score 3 on the recorded production deploys and the screenshots, but a grader who tries a promotion today would see a red gate. (c) Cosmetic: run #32 shows `cancelled` overall; point graders to attempt 1. |
| 10. Observability | 2 | "A key user journey is instrumented with metrics, traces, and structured logs that share a trace ID; no customer data or credentials are sent to telemetry; and the signals are collected, stored, and viewable in a UI." | MET (2) | Instrumentation, collection and storage: `backend/vulntriage/observability/`, `observability/`; `T-REFUSE` and `T-JOURNEY-BE` in the `telemetry` job (green in every `verify` run listed above), including the exemplar assertion (`tests/test_compose_telemetry.py`). Screenshots opened: `g9-grafana-tempo-trace.png`, `g9-grafana-trace-scan-loki-expandedlog.png` (log event and trace carry `42f5161ee955e543e2f5f355e410c247`), `g9-grafana-dashboard-dev-local.png` (re-captured 2026-10-28, view mode, three populated panes, dropdowns gone), and **new** `drill-b30-metric-to-trace-and-trace-to-logs-prometheus-exemplar.png` (opened): Grafana Explore on Prometheus, an exemplar on `vt_notifications_total` with `trace_id 363bee600baddaaaf2299dac77e1eacf` and `span_id 8325cc5ebb3d1ff4`. The same id appears (as `363bee600baddaaaf22...`, `scan.run`, `vulntriage-backend`) in the Tempo pane of the re-captured dashboard screenshot. So the metric-to-trace leg that last audit could only cite as a CI assertion is now visible on screen. | **What is still not shown:** one single trace id across all three signals in one run. The metric-exemplar and Tempo-pane id (`363bee...`) is from the drill run; the log-and-trace id (`42f516...`) is from the 2026-10-26 run; the dashboard's Loki pane shows event names but I did not see a log line carrying `363bee...`. The trace-to-logs click-through is not shown (the screenshot file name says "trace-to-logs" but it shows only the exemplar and its query view). The observability stack runs in local Compose only, not on the AWS server (README says so). Not shown: that the README's "no customer data" claim holds for the drill run; it rests on `T-REFUSE` (CI) and the field list in the expanded-log screenshot. I count MET because each rubric clause has evidence that exists now. |
| 11. Alerting on User Impact | 1 | "At least one alert exists." | MET (1) | Provisioned Grafana rule `observability/grafana/provisioning/alerting/us14-overdue.yaml`. Fired in real Grafana in the drill: `drill-b18-show-the-grafana-alert.png` (opened) shows "1 rule, 1 firing", `VulnTriage > us14-notification-overdue`, Provisioned; `drill-b19-wait-for-the-alert-email-email.png` (opened) shows the MailHog email `[FIRING:1] 1 (Top-tier owner notification overdue VulnTriage P1)`, label `finding_id=1`, `tier=P1`, summary "A top-tier owner notification is overdue for finding 1 (tier P1)". `drill-b27-show-the-resolved-alert-grafana.png` (opened) shows the same rule "1 normal" afterwards. The `alert` workflow ran nightly (runs #1 to #3, all `success`, latest 2026-10-27: https://github.com/andrew-chung-au/vuln-triage/actions/runs/40584579706). | The email's `environment` and `version` annotations read "[no value]" (cosmetic). The last `alert` run predates PR #265, which removed the planted defect from `main` (see criterion 12); whether the next nightly stays green is not known. |
| 12. On-Call Agent | 2 | "An agent wakes up on an alert and fixes the issue." | MET (2) [scripted drill; owner-captured; QA of final code incomplete] | An agent woke on a real Grafana alert and a fix was merged. Verified in this audit: **PR #265** "Fix undelivered notification for alert f2522d83872e83ce" (read through the GitHub API): `merged: true`, merged by the owner at 2026-10-28T07:24:03Z, branch `responder/f2522d83872e83ce`, one commit, 4 files (`backend/vulntriage/mail/message.py`, `tests/test_demo_defect.py`, `tests/test_notifications.py`, `tests/test_notify_no_fixed_version.py`), +37 -28; its body says the runner checked the commits before pushing and that "the responder never merges". Screenshots opened: `drill-b21-open-the-pull-request.png` (the PR open, 14 checks passed), `drill-b22-merge-the-pull-request.png` (merged, 14 checks passed), `drill-b27-show-the-resolved-alert-terminals.png` (the responder's action log: `webhook_rejected` 401, `run_started` at 07:14:20 UTC with `model claude-sonnet-5-5`, `api_read`, `branch_pushed` 07:15:54, `pull_request_opened` 07:15:55 naming PR 265, `alert_ignored` outcome `resolved` 07:32:16; and the terminal showing `VT_DEMO_DEFECT=[]` after the restart, MailHog total 2, the overdue metric back to 0), `drill-b16` (metric `vt_top_tier_notification_overdue == 1`, `finding_id="1"`, `tier="P1"`), `drill-b18`, `drill-b19`, `drill-b27-...-grafana` (rule back to "1 normal"). The timestamps agree with the PR's creation time (07:15:53Z). The responder code exists and is tested: `responder/vt_responder/` (`real_runner.py`, `cli_session.py`, `publisher.py`, `policy.py`, `cli_rules.py`, ...), the stub-mode `responder` workflow ran `success` on 2026-10-27 (runs #1 manual and #2 scheduled: https://github.com/andrew-chung-au/vuln-triage/actions/runs/40586825318); #222's refused push to `main` is recorded in the roadmap (not re-read). | Limits, in order of weight. (1) **Scripted drill, not a discovery:** the agent's prompt states that the code behind `VT_DEMO_DEFECT` is a deliberately planted defect and fixing it is its task (PR #266 body; README says so). Without that line the live agent escalated twice. (2) **Independent QA of the final runtime code (#266) was not completed** (see the top of this file). (3) **The runner, not the agent, pushes and opens the PR, and a person merges**; the rubric says an agent "fixes the issue", and I read the merged fix as meeting that, but a strict grader could count the human merge as part of the fix. (4) **Not reproducible on `main`:** #265 removed the planted branch (the diff on `message.py` is -8 lines; no backend code raises `DemoDefectError` now, grep in this audit), so `VT_DEMO_DEFECT=notify_no_fix` no longer fails a job on `main`. The Compose cases that depend on it (`tests/test_compose_demo_be.py` sets the flag and expects a failed job; the nightly `responder` and `alert` workflows) last ran green on `fb2e5c2`, before #265 merged, so I cannot say the nightly stays green; it was not checked and I cannot run it. (5) The video was not watched; the screenshots and the PR record carry the evidence. (6) Several `VERIFY:` items in `_docs/responder-cli-runtime.md` are still open, and the demo-defect cleanup (#161) is not done. (7) The `responder` job is nightly and on demand, not per PR. The README states limits (1), (2), (3 partly) and (6) honestly. |

## Observability: what changed since the last audit

The 2026-10-26 audit listed as the one soft spot that the metric-to-trace link was
asserted in CI but not shown on screen. The drill screenshot
`drill-b30-metric-to-trace-and-trace-to-logs-prometheus-exemplar.png` now shows the
exemplar carrying a `trace_id`, and the re-captured dashboard
`g9-grafana-dashboard-dev-local.png` lists a Tempo trace starting with the same
digits (`363bee600baddaaaf22...`). The pre-existing screenshots were not
re-opened beyond the two named in the table; their descriptions from the earlier
audit stand (log event and trace share `42f5161e...`). The dashboard-filter caveat
from before is closed in practice: the re-captured screenshot was taken after the
Environment and Version dropdowns were removed, so the dashboard JSON in the repo
has now been loaded in Grafana (README says it was re-captured 2026-10-28; the
screenshot shows no dropdowns).

## README claims checked against the evidence

Supported by evidence I opened:

- Row 12 and line 7: a real `claude -p` responder fixed the planted defect and the
  runner opened PR #265, which the owner merged (PR API record; screenshots b21,
  b22, b27; action log timestamps).
- "Exactly one alert fires" (b18: one rule, 1 firing) and "the next row's email
  names the finding" (b19: finding 1, tier P1).
- Production reviewer gate, `protect-main` with seven required checks (g1, g2, g5).
- "Metric returns to 0" and "alert resolves" (b27 terminals, b27 Grafana).
- Row 10: the exemplar carries a trace id (b30) and the same id appears in the
  Tempo pane of the dashboard screenshot.
- Line 7: independent QA of the final merged runtime code was not completed
  (matches PR #266's own text).

Claims the evidence does not fully support, or that are out of date:

1. **README lines 30 and 257** say the audit on file is 22 of 24 with On-Call
   Agent missing. That was true until this audit; they are now stale. The
   suggested 24/24 in row "Total" is now consistent with this file's score, but
   see the caveats.
2. **Row 12, "runs green in the nightly/on-demand `alert` and `responder` CI
   workflows"**: true of the runs on record (all `success`, latest 2026-10-27),
   but those runs predate PR #265, which removed the planted defect from `main`.
   The README does not say the nightly P-DEMO-BE stub loop depends on that
   defect, and I have no evidence it still passes. Unverified, at risk.
3. **Row 12, "recorded alert-to-fix drill ... is the video"**: the video is
   unlisted on YouTube and I did not watch it. The screenshots carry the claim.
4. **Row 10 / line 211, "shown live in the on-call drill evidence"**: true for the
   exemplar. It is not shown that one trace id is common to metric, trace and log
   in a single run (two different ids across runs, see criterion 10), and the
   trace-to-logs click-through is not shown although the screenshot file name
   mentions it.
5. **Row 9 and "Deployment & rollback"**: "production is a manual promotion" is
   supported by runs #31 to #33. The README does not say a promotion of the
   current tree is blocked by `P-FLAG-GONE` until #161 removes the demo-defect
   code; line 243 says only "the cleanup of the remaining switch is pending".
6. **Line 215 / row 12, the agent "investigates ... adds a test and fixes"**:
   PR #265 does add `tests/test_notify_no_fixed_version.py` and updates two
   other tests, so this holds; but the PR deleted the defect branch rather than
   reproducing a production failure, and the README's own "scripted drill"
   sentence covers that.

Not checked: the `responder-token-proof` and `responder-security-limits` claims
(README lines 233, 248), the CI-run duration claims, and the 9 other drill
screenshots not named above (b12, b14, b16 graph, b19 inbox, b21 full-screen,
b24, b25, b26, b30 query).

## Items confirmed by the owner (not independently reproduced)

1. **The live URLs load** (criterion 8): committed screenshots g6, g7 plus the
   owner's confirmation; my sandbox cannot fetch the pages.
2. **The live drill of 2026-10-28** (criteria 10, 11, 12): the screenshots and the
   action log are committed and I read them; the run itself, the Claude login and
   the model call on the owner's host cannot be reproduced here.
3. **`make test-compose JOB=responder` green on a Docker host** and the `#233`
   run (roadmap): not re-read. The stub `responder` workflow has green Actions
   runs.
4. **#222 refused push to `main`** with the fine-grained token (roadmap,
   evidence on #160): not re-read.

## Corrections to earlier claims

- 2026-10-26 table: On-Call Agent MISSING (0) is superseded by MET (2). Its gap
  list (a real runner, a real alert-to-PR run, the action log, the `verify.yml`
  responder job) is closed except the last item: the responder job lives in
  `.github/workflows/responder.yml` (nightly and on demand), not in `verify.yml`.
- 2026-10-26 criterion 9 gap (b), "which checks `protect-main` requires is not
  visible": closed by the re-captured `g5-github-settings-rulesets-protect-main.png`.
- 2026-10-26 criterion 10 limit "the metric panel shows no trace id": narrowed;
  the exemplar is now shown (see above).
- 2026-10-26 "Items confirmed by the owner" item 4 (branch protection requires the
  CI checks) is now backed by the visible required-checks list.

## Top three gaps (priority order)

1. **Make the on-call evidence reproducible and honest about the removed defect
   (protects criterion 12 and 11).** #265 deleted the planted branch, so the
   nightly `responder` and `alert` workflows and `tests/test_compose_demo_be.py`
   may now fail. Dispatch the `responder` and `alert` workflows once on `main` and
   record the result; if red, decide whether the drill needs a re-armed defect or
   the tests need updating. This is the claim most likely to be contradicted by a
   grader who runs the project.
2. **Independent QA of the merged runtime code (#266), plus the demo-defect
   cleanup (#161).** Run QA on `main` for the rule change, the prompt change and
   the redact-first change; then remove the `VT_DEMO_DEFECT` machinery so
   `P-FLAG-GONE` passes, and prove it in one real production promotion (human
   B12). Until then a production promotion of the current tree is blocked
   (criterion 9 risk).
3. **Documentation consistency and one tighter observability view (no new
   points).** Update README lines 30 and 257 to point at this audit; say in the
   README that the nightly stub loop and the production gate depend on the demo
   defect; capture one run where the metric exemplar, the Tempo trace and the
   Loki log line for the same trace id are all shown (and the trace-to-logs
   click-through); keep the nightly server stop off until after grading.
