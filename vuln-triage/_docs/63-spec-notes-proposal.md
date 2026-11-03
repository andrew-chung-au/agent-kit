# Proposal: the four #63 spec notes (for the owner's approval)

Draft diffs for [#63](https://github.com/andrew-chung-au/vuln-triage/issues/63) and the
third box of [#229](https://github.com/andrew-chung-au/vuln-triage/issues/229)
(D2, cloud task CC5(b)). **Nothing protected is changed here.** `_docs/specs.md` and
`_docs/architecture.md` are protected: each diff below is applied only after you approve
it, as its own `HUMAN_APPROVED=1` commit, with an approval record on #63 (format:
`_docs/agent-kit/procedures/asking-the-human.md`).

Checked against `main` at `9c8216c` on 2026-10-26.

## Summary

| # | Note | State on `main` | File | Proposal |
|---|---|---|---|---|
| 1 | `NotificationJob` has no `tier` | **Already done.** The architecture's `NotificationJob` row has `tier` ("the finding's tier when the job was created; never changes, and is the `tier` label of the US-14 metric"). | none | Record as done on #63 and #229. No edit. |
| 2 | The US-13 metric has no trace-id carrier | Open. The architecture puts the `traceparent` on the job and says the metric, trace and log share one trace ID, but never says what carries it on the metric. | `_docs/architecture.md` | Diff A |
| 3 | US-14 "exactly one alert" wording | Open. US-14's acceptance says "fires exactly one alert" and is silent on the resolved notification. (The architecture already says the alert "resolves when the job is `sent`".) | `_docs/specs.md` | Diff B |
| 4 | Demo-defect removal wording | Open. A35 says the defect is refused in production and does not say it is removed before the first production promotion. | `_docs/architecture.md` | Diff C |

Note 3 assumes your D1 option 1 decision (2026-10-22). If that changes, Diff B changes with it.

## Diff A: note 2, the metric carries the trace ID as an exemplar (`_docs/architecture.md`, line 364)

Appended to the end of the "One trace ID" paragraph, after "A job's `traceparent` is
therefore never null and never changes."

```diff
-... records a `notification.enqueue` span, with its own root span when it is not inside `scan.run`, and stores that span's `traceparent` on the job. A job's `traceparent` is therefore never null and never changes.
+... records a `notification.enqueue` span, with its own root span when it is not inside `scan.run`, and stores that span's `traceparent` on the job. A job's `traceparent` is therefore never null and never changes. The US-13 metric carries the journey's trace ID as an OpenTelemetry exemplar on the sample, not as a label (a label would multiply the series), so the telemetry allowlist needs no `trace_id` attribute. Prometheus stores the exemplar and the CI test T-A4 reads it back through `/api/v1/query_exemplars`; VERIFY: that Grafana shows the exemplar as a link from the metric panel to the trace, which CI does not assert.
```

Basis: `tests/test_compose_telemetry.py` (T-A4) asserts the exemplar carries the journey
trace ID in CI, and `tests/compose_telemetry.py::prometheus_exemplar_trace_ids` reads
`/api/v1/query_exemplars`. The last clause is deliberately a `VERIFY:`: the Grafana UI link
is shown only in the committed screenshots, not asserted (the rubric auditor makes the same
point).

## Diff B: note 3, one alert is one firing episode (`_docs/specs.md`, US-14, line 186)

```diff
 - Acceptance: a top-priority finding whose notification fails or does not
   complete within the agreed window (based on the `notification.deliver`
   outcome) fires exactly one alert naming the finding; a successful
-  notification fires none.
+  notification fires none. One alert means one firing episode for a finding;
+  a resolution notification for the same episode is not a second alert.
```

The sentence is the one #63 proposed, unchanged.

## Diff C: note 4, the demo defect is removed before production (`_docs/architecture.md`, A35, line 517)

```diff
 - (A35) The demo defect is switched by `VT_DEMO_DEFECT`, refused in production. "Production" is `DEPLOYMENT_ENVIRONMENT` not explicitly `dev`/`test` (the same fail-closed test as the `VT_FEEDS=fixtures` refusal, A42; closes T-A8).
+ (A35) The demo defect is switched by `VT_DEMO_DEFECT`, refused in production. "Production" is `DEPLOYMENT_ENVIRONMENT` not explicitly `dev`/`test` (the same fail-closed test as the `VT_FEEDS=fixtures` refusal, A42; closes T-A8). The demo defect is removed in a cleanup commit/PR before the first production promotion; a test proves the production startup refusal while it exists, and a later check (`P-FLAG-GONE`, task 29) proves the code path and variable are gone.
```

The wording is #63's, with one addition: it names `P-FLAG-GONE` as the later check, which
exists as a draft (PR for #161). Delete the parenthesis if you would rather keep the
architecture free of check names.

## How to apply (three commits, each alone)

1. Diff B: `_docs/specs.md` only.
2. Diff A: `_docs/architecture.md` only.
3. Diff C: `_docs/architecture.md` only.

Each: `HUMAN_APPROVED=1 git commit` after you approve that diff, then a "Protected-change
approval record" comment on #63 (issue, commit, parent, paths, date, the
`git show --format= --no-renames --patch <commit> -- <path>` diff, blob IDs). Then tick the
third box on #229 and close #63 with a note for note 1 (already done).

## What this does not decide

- The `P-FLAG-GONE` wording box on #229 is a separate decision (the wording is in
  `_docs/161-responder-job-proposal.md`). It is not approved by this document.
