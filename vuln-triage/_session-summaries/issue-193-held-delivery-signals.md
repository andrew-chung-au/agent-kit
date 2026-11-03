# Issue #193: Delivery worker emits the outcome span/log/counter on every held branch (folds #177)

**Date:** 2026-10-25
**Spec version:** 9b04f90

## What changed and why

All eight delivery outcomes (`sent`, `failed` and the six holds) now emit the `notification.deliver` span, a structured log and exactly one `vt_notifications_total` increment. Before, the ownerless, owner-email-missing and `no_target` holds returned before the span opened, and `mail_config` and `header_injection` skipped the counter. All six held branches now go through one helper, `_emit_held`. Telemetry `vt.error.code` is snake_case; `last_error_code` and job state are unchanged. `vt.finding.id` is omitted for `no_target`. Counter labels are `vt.notification.kind` and `vt.outcome` only.

Also: the roadmap statuses were refreshed from the tracker first (`144c5b0`), at the human's request.

## Files created or modified

- `backend/vulntriage/mail/delivery.py`
- `tests/test_notifications.py` (one test parametrised over all eight outcomes, idempotence and `traceparent=""` cases)
- `_docs/pending-verification.md`, `_docs/human-tasklist.md` (pending Loki leg for #177 / #193)
- `_docs/ai-usage-log.md`
- `_docs/roadmap.md` (separate commit `144c5b0`)

Implementation commit: `d3dc2af`.

## Decisions made by the human

- Q1 (`no_target` telemetry): omit `vt.finding.id` (option A).
- Q2 (Loki leg): best-effort, not a gate (option 1, after an explanation). The human runs it with Docker later; closing #193 does not wait on it.
- Decision point: note the QA risks only, then close.

## Mismatches with the spec or design docs

None found.

## Commands to validate

**Verify:** `make verify` (QA: 87 frontend, 471 backend, 5 Compose tests deselected; PASS)

## Proposed AGENTS.md changes

None.

## Temporary changes

None. No processes started.

## Permission review

PM, Engineer and QA comments each reported no command needing approval. The orchestrator's own: none beyond the `make` targets already allowed.

- Read-only (propose allowing): none
- Writes to the record (keep asking): none
- Risky (propose denying): none

## Interruptions

None.

## Unrelated problems noticed but not fixed

- QA noted `make verify` lists changes from other commits since origin/main (a permission-log plugin, a planning summary). Not examined.
- `human-tasklist.md` §C still lists PRs #184 and #183, which no longer show as open.

## Follow-ups for the next session

- Held-job Loki proof is unrun: the `T-JOURNEY-BE` journey needs a second ownerless fixture asset and a trace lookup that tells the two assets apart. Recorded in `_docs/pending-verification.md`.
- QA risk (noted only): the new tests replace `metrics.notifications_total` with a throwaway in-memory counter, so they prove the call site and labels, not the production instrument from `setup_metrics()`.
- Next: #194 (`scan.finished` on failed scans), then #181, then #195's static part.
