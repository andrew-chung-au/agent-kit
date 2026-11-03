# Issue #195: US-13 dashboard: align panel queries with exported metric labels (static check and test)

**Date:** 2026-10-25
**Spec version:** 9b04f90

## What changed and why

Panel 1 of the US-13 dashboard grouped `vt_notifications_total` by `kind, outcome`, but the backend emits `vt.notification.kind` and `vt.outcome`, which the Collector's Prometheus exporter writes as `vt_notification_kind` and `vt_outcome`. The panel therefore almost certainly matched no series. Panel 1 now groups by the exported names, and a new stdlib-only test (`tests/test_us13_dashboard.py`) parses the committed dashboard and checks every Prometheus query against an allowed metric and label set derived from `metrics.py` and `delivery.py`. Refusal cases show the old query, an unknown metric and an unknown label are rejected. The `environment` and `version` template variables are listed as unverified, live check pending (#199). `testing.md` and `architecture.md` each gained a one-line "exported as" note.

The issue was narrowed at the start: the live Grafana check was split out to #199 (cloud session), and #195's title and body were rewritten after PM grooming.

## Files created or modified

- `observability/grafana/dashboards/us13-journey.json`
- `tests/test_us13_dashboard.py` (new)
- `_docs/testing.md`, `_docs/architecture.md` (one line each)
- `_docs/ai-usage-log.md`
- `_docs/pending-verification.md` (queue now points at #199; commit `3737d39`)
- `_docs/roadmap.md` (check-in row)

Implementation commits: `e072634`, `0b30652`.

## Decisions made by the human

- File #199 for the live check and narrow #195 to the static fix.
- Mark the `environment` and `version` variables unverified in the test, not asserted valid.
- Add the "exported as" doc notes now.
- Decision point: note the QA risks only, then close.

## Mismatches with the spec or design docs

None. The doc lines `testing.md` and `architecture.md` used the logical names `{kind,outcome}`; they stay correct as design text and now carry the exported-as note.

## Commands to validate

**Verify:** `make verify` (QA: 487 backend, 87 frontend; PASS)

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No processes started. `make clean-scratch` run at the end.

## Permission review

PM, Engineer and QA comments each reported no command needing approval. The orchestrator ran `gh issue create` (to file #199) and `gh issue edit` (to replace #195's title and body); there is no make target for either.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `gh issue create --body-file` (filing #199); `gh issue edit --title --body-file` (rewriting #195). Basis: no make target; the human approved the split.
- Risky (propose denying): none

## Interruptions

None.

## Unrelated problems noticed but not fixed

- `human-tasklist.md` §C still lists PRs #184 and #183, which no longer show as open.
- No `make issue-create` / `make issue-edit` targets exist; worth proposing at the next permission sweep (also noted in the #194 summary).

## Follow-ups for the next session

- #199: live Grafana check (cloud session, sequenced with #181). It confirms the `vt_notification_kind` spelling, that panel 1 shows data, and whether `deployment_environment` and `service_version` exist as labels.
- #181: moved to a cloud session; its PM decisions Q1-Q3 are still open.
- QA risks, noted only: the test is regex-based, not a PromQL parser (a new panel could trip a false "unknown metric"; `on(...)` and `group_left(...)` clauses are not checked), and it skips Prometheus panels nested in a row or with the datasource set only on the target. The current dashboard has neither.
