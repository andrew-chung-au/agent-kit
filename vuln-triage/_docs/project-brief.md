VulnTriage ranks vulnerable software dependencies by real-world exploit risk
and routes each fix to the person who owns it.

Problem: new vulnerabilities are published daily; most don't affect us, the few
that do are hard to find; hand-maintained asset lists go stale; severity scores
alone don't show what attackers actually exploit; findings that don't reach an
owner don't get fixed.

Workflow:
1. Inventory: register assets (apps/services) with owner, criticality and
   whether they are internet-facing; read their dependency files
   automatically (uv.lock, requirements.txt, package-lock.json).
2. Match: query OSV.dev for known vulnerabilities per package version, with
   the fixed version.
3. Enrich: add CISA KEV status (known exploited) and FIRST EPSS score
   (probability of exploitation), plus asset context.
4. Prioritise: a deterministic, explainable score. No AI.
5. Brief: an LLM writes a plain-language brief for the asset owner from the
   structured finding. Guardrail: code rejects any brief whose fix version
   differs from OSV's fixed version. Advisory text is untrusted data.
6. Route (n8n): daily refresh of KEV/EPSS and re-score via the API; notify the
   owner and open a GitHub issue for new top-priority findings; overdue
   reminders and escalation; weekly digest to the security lead. Workflows
   exported as JSON into the repo.
7. Re-scan: a finding closes automatically when a re-scan shows the fixed
   version is in place.
8. Watch and respond: one key user journey is instrumented with metrics, traces
   and structured logs sharing a trace ID; an alert fires when a top-priority
   finding does not reach its owner; a responder agent wakes on that alert and
   fixes the cause. No customer data or credentials are sent to telemetry.

Also: a web dashboard of findings per asset with status (open / risk accepted /
fixed) and an audit trail. An MCP server with read-only tools
(list_top_exposures, which_assets_affected, get_finding, get_asset) that calls
the API with its own read-only token. No write tools in the MVP; risk
acceptance is a human decision in the dashboard.

Fixed stack (do not change): React frontend with all backend calls in one
service layer; FastAPI backend (Python, uv for dependencies); SQLAlchemy with
SQLite for development and Postgres for Docker Compose and production; Docker
Compose; GitHub Actions CI/CD: tests on every pull request, automatic deploy to
a dev environment, and a manual promotion of the same image to production; n8n
as a separate Compose service; MCP server in Python; OpenTelemetry
instrumentation through an OpenTelemetry Collector to Prometheus, Loki and
Tempo, with Grafana for dashboards and alerting.

Out of scope for the MVP: servers, network devices and commercial software;
active scanning or penetration testing (the tool only reads inventory);
automatic patching (people approve fixes); write tools in the MCP server.

Pilot data: a few of my own repositories, plus a public deliberately vulnerable
app (OWASP Juice Shop) and/or an open-source repo pinned to older versions, so
there are real findings.

Success criteria: findings appear without manual data entry; each finding shows
why it ranks where it does; no AI brief reaches an owner with a wrong fix
version (tested); a new top-priority finding notifies its owner and opens a
GitHub issue automatically; a re-scan closes fixed findings; an AI assistant can
answer "which assets are affected by this CVE?" through the MCP server.
