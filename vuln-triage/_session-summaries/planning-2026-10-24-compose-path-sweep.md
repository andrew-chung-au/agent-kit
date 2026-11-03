# Compose-only path sweep (first step of #172)

**Date:** 2026-10-24
**Why:** The first real Compose run of the #157 `telemetry` job surfaced three gaps that `make verify` (no Docker, no network) could never catch. Before building #172, enumerate every Docker-only / "planned" / never-actually-run path and, for each, record: (a) is it wired in CI? (b) has it ever run green? (c) does its test assert the signal **reaches the backend/leaves the process**, or only that an in-code helper behaves? Findings become explicit tasks instead of being discovered one CI round-trip at a time.

## The pattern to catch

All three #157-era gaps share one shape: a telemetry/Compose path whose only executed test ran in the no-Docker gate, so "it compiles / the helper filters / the unit asserts" passed green while the **end-to-end path had never executed**.
- **Feed wiring** (#172): `create_app` injects no OSV/KEV/EPSS clients → a deployed scan matches nothing. No test ever ran a scan through the running app.
- **Delivery harness** (#172): delivery must happen in the backend *container* for `I-OWNER-*` to mean anything; a host-process delivery tests the wrong layer.
- **OTLP log export** (#174, fixed): `log_event` wrote stdout only, never exported; task-23 QA unit-tested the allowlist *helper*, never that a record leaves the process.

## Inventory

Source: `.github/workflows/verify.yml` (jobs actually wired), `_docs/testing.md` § CI jobs (the intended table), `Makefile` (targets that exist vs. "planned").

| Path / job | Wired in CI? | Ever run green? | Does a test assert end-to-end (reaches backend/leaves process)? | Sweep finding |
|---|---|---|---|---|
| `unit`, `frontend`, `openapi-validation` | yes | yes | n/a (no-Docker by design) | OK — in-process by design. |
| `sqlite-integration` | yes | yes | API+DB through the app (TestClient), SQLite | OK — exercises the app, in-process. |
| `postgres-integration` (`make test-integration`) | yes | **yes** (green on #157 runs) | Runs the integration suite against real Postgres in Compose | OK — genuinely runs; the one Compose job that was already proven before #157. |
| `telemetry` (`make test-compose JOB=telemetry`) | yes | **yes, as of #157** (`T-REFUSE`, 1 passed) | `T-REFUSE` asserts spans/logs **reach** Tempo/Loki via the Collector (raw-API span + raw OTLP log) | OK for `T-REFUSE`. The journey/delivery cases are #172 (below). |
| `telemetry` → `T-JOURNEY-BE` | not yet | **never** | would assert the full scan→notification journey across metric/trace/log | **#172 (this issue).** Needs feed wiring to produce a P1. |
| `telemetry` → MailHog `I-OWNER-NOAWS`/`I-OWNER-SENDER`, `T-E6`, `T-DELIVER-TRACE` | not yet | **never** | must assert the **container** delivers (not a host process) | **#172 (this issue).** Containerized-backend-delivers harness. |
| `alert` (`make test-compose JOB=alert`) | **not wired** (selector exits 3) | **never** | `A-FIRE/TIER/GAP/RESOLVE/HELD` must assert the alert fires from stored job state through Grafana | **Task 27 / #159.** Depends on #172's harness (needs a real/seeded firing finding). Flag: #159 should reuse #172's containerized harness, not invent its own. |
| `responder` (`make test-compose JOB=responder`) | **not wired** (selector exits 3) | **never** | `P-DEMO-BE/P-PROD-REFUSAL/I-RESP-*` must assert the responder wakes on a real alert and the container refuses prod config | **Task 28 / #160.** `P-DEMO-BE` explicitly needs #172's feed fixtures + a real Compose scan. |
| `security-scan` (`make security-scan`) | **not wired**; target absent | n/a | `C-SCAN/C-FIXTURE-*` audit the app's own lockfiles | **Task 20 / #140** (open PR #167). Not telemetry; needs its own CI wiring + fixture lockfiles. Already tracked; note it is still unwired. |
| `e2e` (`make test-e2e`) | not wired; target absent | n/a | Showcase full-stack journey | Showcase (post-submission). Not a submission blocker. |
| `workflow-export` (`make test-workflows`) | not wired; target absent | n/a | Showcase n8n export | Showcase. Not a submission blocker. |
| `make test-brief-eval` | not wired (manual) | n/a | Showcase LLM eval | Showcase, manual by design. |
| `P-FLAG-GONE` | not in `make test-compose` | n/a | prod-promotion check (task 18 workflow) | Task 29 / #161 wires it into the promotion workflow; its own correctness is a `make test` fixture-tree check. #172 adds a `VT_FEEDS=fixtures` rule to it. |
| `deploy.yml build-and-push` (GHCR) | yes (push) | **yes** — green on every push to `main` (5/5 recent, incl. the #157 merge) | builds + pushes the backend/frontend images | OK — the Dockerfiles genuinely build; not a gap (Finding A, resolved). |

## Findings / actions

- **#172 (this issue):** the feed wiring + `VT_FEEDS=fixtures` + the containerized-backend-delivers harness, carrying `T-JOURNEY-BE`, the MailHog `I-OWNER-*` forms, `T-E6`, `T-DELIVER-TRACE`. This is the main build.
- **Finding A — RESOLVED.** `deploy.yml`'s `build-and-push` (GHCR) has run green on every push to `main` (5/5 recent, including the #157 merge `ab15b3d` at 07:09). The backend/frontend Dockerfiles genuinely build; not a hidden gap.
- **Flag for #159 (task 27):** the `alert` job must reuse #172's containerized-backend-delivers harness to get a real firing finding — it must not seed a host-process shortcut (the same mistake #157's first draft made). Note this on #159 so the design is set before it starts.
- **Flag for #160 (task 28):** `P-DEMO-BE` depends on #172's fixture mode (a real Compose scan producing the no-fixed-version finding). Confirmed in #172's own "blocks" list.
- **General verification lesson (carry into every telemetry/Compose task):** a task's check must assert the signal **leaves the process / reaches the backend**, not just that an in-code helper filters or a unit asserts. Task 23's QA missed the log-export gap precisely because it stopped at the helper. Apply this lens to task 37 (delivery), #159 (alert fires from stored state), #160 (responder wakes).

## Conclusion

Three Compose/Docker paths were proven green: `postgres-integration` (long-standing), `telemetry`/`T-REFUSE` (as of #157), and the GHCR image build in `deploy.yml` (Finding A, resolved). Everything else Docker-only is either **this issue (#172)**, a **later task that should build on #172's harness** (#159, #160), **already-tracked** (#140 security scan), or **showcase**. No new hidden submission path was found beyond what #172/#159/#160 already own — the sweep's value is the explicit "build on #172's harness" constraint for #159/#160 and the end-to-end verification lesson (assert the signal reaches the backend, not just that the in-code helper behaves).
