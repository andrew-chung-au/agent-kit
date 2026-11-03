# Pending verification (cloud / host steps)

One place for every build step that the **agent sandbox cannot run** — because
it needs Docker, real network, AWS, or a `terraform apply` — and so is left for a
**GitHub Codespace, a Claude Code cloud session, CI, or the human's host**.

Each item says where to run it, the exact commands, and when it is done. Tick
items off as they pass. When an issue's items are all done, close the issue and
remove its section here.

Why this exists: the Kiro Web agent sandbox has no shell network and no Docker
socket (`AGENTS.md` Project gotchas), so Compose stacks, live dependency scans,
and AWS applies are authored by the agent and **verified by the human**. This
file collects those hand-offs so a cloud session has one checklist.

Who does each item: `_docs/cloud-tasklist.md` lists the verification runs a
Claude Code cloud session can do (CC IDs, with the human step each needs), and
`_docs/human-tasklist.md` lists what only the human can do (AWS, approvals,
decisions, merges). This file is the detailed per-issue checklist both link to;
the cloud-session queue below is superseded by the cloud list, which is the
source for order and dependencies.

Last updated: 2026-10-26, evening (the owner's responder-job run (#220 comment 6415509715) and live US-13 stack check (#226 comment 6417013401) are recorded; the closed #158 section is removed; the #220 section is gone and the #155 and "#210 and #211" sections are reduced to leftovers; the #199 result is in the queue above). Earlier, 2026-10-26, later (owner-run items regrouped into one ticket per sitting: #225 close-out sweep, #226 live observability stack, #227 AWS console, #228 unblock cloud sessions, #229 decisions; #223 closed as replaced by #225; the #159 section removed, its issue closed and its last items green). Earlier: 2026-10-26 (QA unverified items for #157, #172, #218 and #219 collected in #223). Earlier: 2026-10-25 (#193: held-delivery signals, Loki leg recorded; #180: #177 folded into #193; #159 alert job: CI job committed; cross-ref to verify-locally.md §7b)

## Cloud-session queue (Docker work to hand to Claude Code cloud sessions)

Added 2026-10-25 at the human's direction: work the local sandbox can't do for
lack of Docker goes to a Claude Code cloud session (`_docs/cloud-sessions.md`;
one session per issue, credit is limited). Each line is a candidate, not a
started job.

- **#181** (T-E6, telemetry backend down): groomed; the human answered PM decisions Q1-Q3 on 2026-10-25 (comment 6396530230: best-effort close, narrow "alerts unaffected", add Collector self-metrics). Author and run it in the cloud.
- **#182** (`I-OWNER-SENDER` MailHog form): follows #160 (task 28).
- **#198** (`internal error` scan reason): look at the failure reason on the dashboard in a running UI. Running migration `0002` on real Postgres is now **#201** (a `postgres_migration` check in the `postgres-integration` job; Docker-only, verified in CI).
- **#199** (US-13 dashboard live Grafana check, split from #195 on 2026-10-25): **run live by the owner on 2026-10-26** (results in #226, comment 6417013401). The real labels are `vt_notification_kind` and `vt_outcome`; `deployment_environment` and `service_version` are not labels on `vt_notifications_total`, and the dashboard's Environment and Version variables filtered nothing, so the owner chose to drop them (X14 is the future work). The dashboard change was checked statically only; the next live run confirms the dropdowns are gone.
- **#172**, **#174** and **#157** (`T-JOURNEY-BE`, the Loki leg, `T-REFUSE`): done in CI (run 40291587781) and closed (2026-10-26). The optional #193 held-job case is in #226.
- **#155** (dashboard and MailHog check): run live by the owner on 2026-10-26 (results in #226). The optional US-14 rule spot checks (#158 is closed) and the optional held-job Loki case remain in #226; on 2026-10-26 only the rule's presence was seen (`us14-notification-overdue`, Provisioned, Normal; its contact points and policy were not checked).
- **#140** (security scan, PR #167): needs network to generate the fixture lockfiles.
- **Human machine, not cloud:** AWS applies and secrets (#141, `human-tasklist.md` §A).

## #140 — light security scan (task 20)

PR: #167. Run in a **Codespace / Claude Code cloud / CI** (needs network for the
advisory services and to generate the fixture lockfiles). Full checklist on the
#140 issue comment; summary:

- [ ] Generate the fixture lockfiles per each `tests/fixtures/security/*/SPEC.md` (`uv lock`, `npm install --package-lock-only`); record each advisory ID/severity. `VERIFY:` the advisory is still reported that day.
- [ ] `make security-scan-selftest` — all five fixtures hit their expected outcome.
- [ ] `make security-scan` — the real tree exits 0 (after #111). Report any high/critical; no ignore list.
- [ ] Commit the generated lockfiles to `feat/140-security-scan`; the `security-scan` CI job then goes green.
- [ ] `make verify` stays green (the scan is not part of it).
- [ ] Close #140 when the CI `security-scan` job is green on the PR.

## #155 — observability stack + US-13 dashboard (task 24): leftovers

The live check was run by the owner on 2026-10-26 (results in #226, comment 6417013401): the six services started healthy, the metric, trace and log panels show data, a `scan.run` trace of 7 spans joins to its `notification.deliver` log line by trace id, MailHog received the owner email (with the mail settings passed explicitly), and all six containers started healthy. Open:

- [ ] `VERIFY:` the Grafana trace-to-logs link from a trace (`observability/grafana/provisioning/datasources/datasources.yaml`, `tracesToLogsV2`) was not tried. It is optional ("where available" in #155).

## #156 — backend owner notification + delivery (task 37)

PR: (this change). The core `I-OWNER-*` / `S-NOTIFY` cases run under
`make test` (SQLite + the in-process recording sink, no Docker/AWS/network), so
**the human only needs `make verify`** to land this. The items below are the
Compose and AWS variants the sandbox cannot run.

- [ ] (Codespace / cloud / Docker host) With the `observability/` stack up and the backend run with `MAIL_TRANSPORT=mailhog MAIL_SENDER=<a verified-looking address>`, trigger a P1 finding; confirm one owner email lands in MailHog (`http://localhost:8025`, or `GET /api/v2/messages`). This is `I-OWNER-NOAWS` / `I-OWNER-SENDER` under `make test-compose` and feeds `T-JOURNEY-BE` (task 25 / #157).
- [ ] `VERIFY:` MailHog's SMTP port and HTTP read API (1025 / `GET /api/v2/messages` assumed; `observability/compose.yaml`).
- [ ] (Human, AWS step — deferred, task 37 SES) Add `boto3` to `backend/pyproject.toml` and run `make backend-lock`; settle the SES `VERIFY:` items (IAM action `ses:SendEmail`/`ses:SendRawEmail`, verified-identity ARN, `ses:FromAddress` condition, region, sandbox verified-recipient rule, free allowance) and the exact `boto3` SES client call in `mail/transport.py` `SesTransport.send`. The code ships MailHog-proven with the SES path `VERIFY:`-marked until then.
- [ ] Note: the ownerless-release path (`held: ownerless` / `held: owner email missing` → released by setting an owner email) is `I-ASSET-UPDATE`, owned by the asset-update task, not this one.

## #177 / #193 — delivery outcome signals on every branch (Loki leg)

Commit: see the Engineer comment on #193. The span/log/counter for all eight
outcomes (`sent`, `failed`, and `held` with `sender_not_verified`,
`header_injection`, `mail_config`, `ownerless`, `owner_email_missing`,
`no_target`) is covered under `make test` (`tests/test_notifications.py`,
SQLite + in-memory exporters): the log and span trace ids equal the job's stored
`traceparent` trace id and the counter increments once. The end-to-end Loki leg
is **best-effort, not a gate** (human decision, 2026-10-25); closing #193 does
not wait on it.

- [ ] (CI telemetry job, or a Codespace / cloud / Docker host) The #172
  `T-JOURNEY-BE` Loki assertion (see #172 above) covers the `sent` log. It also
  remains the only end-to-end proof of #177's `sent` log leg.
- [ ] Held-job Loki case is **not** in `T-JOURNEY-BE`: not added blind. It needs a
  second asset with no owner registered through the container backend (a distinct
  repository URL the `VT_FEEDS=fixtures` mode can scan, which the fixtures do not
  have yet), and `wait_for_trace_with_span("notification.enqueue")` then matches
  either journey's trace, so the test needs a per-asset trace lookup. Neither can
  be checked without Docker. Optional manual check: with the stack up, register an
  ownerless asset whose scan yields a P1 finding, wait one delivery poll (~30s),
  then confirm a Loki `notification.deliver` log with `vt.outcome="held"` and
  `vt.error.code="ownerless"` carries the trace id of that job's
  `notification.enqueue` span in Tempo. Post the result on #193.

## #210 and #211 — Grafana start-up and the US-13 metric panel (observability): leftovers

PRs: #211 (stack starts without an override file) and #210 (metric panel plots a running total), both merged 2026-10-25. **Checked live by the owner on 2026-10-26** (results in #226, comment 6417013401): the stack started with no override file, all six containers healthy and no "could not find addresses" error (#211); after a fresh demo run with the stack up, the metric panel showed `top tier/sent` and `top tier/held` lines that step up on Last 1 hour, and Prometheus had `vt_notifications_total` (#210). Open:

- [ ] **#211:** `make test-compose JOB=alert` still passes (the alert test's real `VT_ALERT_HUMAN_EMAIL` / `VT_RESPONDER_WEBHOOK_URL` must override the new defaults; checked statically only; the nightly `alert` workflow also runs it).

## #271 — permission tooling (one local live check)

All checks ran in the local sandbox: `make verify BASE=51bcf57`, `make check-scripts`, the guard's four scratch-repo cases, the read-only `make permission-report`, QA PASS at `5f9cd61` (comment 6495904527), the post-QA fixes `5a0f256`, `4a27b30`, `b50207f` and `d9986ef`, and re-QA PASS at `b50207f` (comment 6497370140) and `d9986ef` (comment 6498104690). See `_docs/permission-tooling-verification.md`. The human restarts OpenCode so `opencode.json` reloads and reads the settings diff before merging. No Docker, network or AWS step.

- [ ] (Human, Claude Code) Confirm `make issue-close` asks even though `make *` is allowed (ask-over-allow precedence; #66). The QA verdict did not verify this live.

---

## Convention

- This file is the **single consolidated checklist** of every open human/CI
  verification action, grouped by issue. For *how to run* the app and the
  Compose test jobs (`make dev`, `make compose-up`, `make test-compose`), see
  the step-by-step guide in `_docs/verify-locally.md` (§6 app, §7 Compose stack,
  §7b the Compose test jobs); this file holds the per-issue items you tick off
  while you run them.
- An item here is the agent saying "I wrote and offline-checked this; it needs a real run I can't do." The agent records the same steps in the issue's session summary; this file is the cross-issue index.
- Prefer the smallest capable environment: CI for anything a workflow already runs; a Codespace/cloud session for Docker/network; the human's machine only for AWS applies and secrets.
- After a run, paste the result on the issue (and tick here). Keep this file to **open** items only.
