# Decision: Self-hosted observability stack, a GitHub Action as the on-call runner, and a script that reads Alertmanager as the alert path

One file per choice that may be revisited. **Status: approved** (the human, 2026-11-16, in the planning session; issue #287 records it). Phase 3 needs a telemetry backend, a runner for the on-call agent and a way for an alert to start that agent. The human chose all three on 2026-11-16 so that later issues link this record instead of re-arguing them.

- **Decision:**
  1. **Backend:** self-hosted in `compose.observability.yaml`, layered on `compose.yaml` (which is never edited): OpenTelemetry Collector, Tempo, Loki, Prometheus, Alertmanager and Grafana, each pinned by digest. It needs no account and runs in CI.
  2. **Runner:** `anthropics/claude-code-action` in a workflow, with `ANTHROPIC_API_KEY` held only in a GitHub Environment named `oncall`. For the drill the pull request is opened with the workflow's own `GITHUB_TOKEN`, so it gets no automatic CI; the run log shows the tests the agent ran.
  3. **Alert path:** a script in the drill workflow reads Alertmanager's API and starts the agent when `QueueLatencyOverSLO` is firing.
- **Reason:** The rubric scores Observability (signals that share a trace id, no customer data, stored and viewable in a UI), Alerting on User Impact and the On-Call Agent. A reviewer has to be able to reproduce all three from the repository alone. A stack in Compose starts with one command, needs no account or secret, and runs in a CI job, so the drill can run on an ephemeral stack that lives only in that job. The Action runs the agent inside GitHub, where its key sits in one Environment and the run log is public evidence. Reading Alertmanager's API from the drill workflow works against a stack that exists only in that run.
- **Alternatives:**
  1. Backend: the all-in-one `grafana/otel-lgtm` image (the fallback if the six-service configuration grows too large; the human is asked before switching); a managed service (needs an account and secrets, and cannot run offline in CI).
  2. Runner: OpenCode; Kiro CLI headless (its login and headless terms are not confirmed); a GitHub App or fine-grained token for the pull request (it would give the pull request its CI, but adds a credential).
  3. Alert path: a webhook to `repository_dispatch` (the dev path later; it needs a dispatch token and a public receiver); a scheduled poll (it cannot reach a stack that lives only in CI).
- **Trade-offs:**
  - A pull request opened with `GITHUB_TOKEN` gets no automatic CI, so the evidence of passing tests is the run log, not a CI run on the pull request.
  - Five more containers do not fit the server's 2 GiB (`t3.small`, `_docs/decisions/2026-11-15T1840Z-dev-prod-one-server.md`) beside two app stacks, so showing the stack on dev waits on the server size.
  - The poller does not prove the webhook path; the webhook stays a later dev path that reuses the script's parsing.
  - Six pinned images are six digests to keep current, and the configuration is larger than the single-image fallback.
- **Evidence:** the human's ruling in the planning session, 2026-11-16, recorded in the Decisions section of `_docs/planning/roadmap-4-devops.md` (added by https://github.com/andrew-chung-au/socboard/pull/302) and in the PM's grooming comment on https://github.com/andrew-chung-au/socboard/issues/287#issuecomment-6903452715; issue #287; the rubric criteria Observability, Alerting on User Impact and On-Call Agent in `_docs/planning/rubric.md`; `_docs/planning/04_devops.md` (steps 7 and 8, alerting and on-call response); `_docs/decisions/2026-11-15T1840Z-dev-prod-one-server.md` (server size); built by #292 (stack) and #297 to #299 (alert path and agent).
