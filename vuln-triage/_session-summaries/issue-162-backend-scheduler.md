# Issue #162 (task 38): backend scheduler for the daily refresh and re-scan

**Date:** 2026-10-24
**Branch:** `feat/162-backend-scheduler`

## What changed and why

Task 38 (Milestone C / C9): a scheduler inside the backend that runs the daily
KEV/EPSS refresh and a re-scan of every asset at 06:00 UTC, with a catch-up rule
for the server's nightly stop — replacing the n8n schedule for submission.
Covers US-7 and the scheduled-re-scan clause of US-10. Independent of the rest
of Tier C (depends only on tasks 8 and 10, both merged), and it verifies fully
in `make verify` (fake-clock + stubs, no Docker, no network).

## Design (human decision: no new dependency)

A clock-driven loop, no library scheduler (the issue's dependency note offered
either; a loop needs none).

- `backend/vulntriage/ingest/refresh.py` (new) — `refresh_all(session, kev, epss)` extracts the per-asset `enrich_asset` → `rank_asset` → `create_top_tier_jobs` loop that `POST /signals/refresh` inlined, so the API handler and the scheduler run identical code. The handler now calls it (no behaviour change).
- `backend/vulntriage/scheduler.py` (new) — `class Scheduler`, a sibling to `ScanWorker`:
  - `run_once()` — refresh all, then enqueue a `ScanTrigger.SCHEDULE` scan per asset (same as `POST /scans`); hands ids to the worker when present.
  - `catch_up()` — at start, if the newest finished `schedule` scan is >24h old (or none), run once immediately (A37).
  - `tick()` — run once per UTC day once 06:00 has passed; safe to call repeatedly.
  - `start()/stop()` — a daemon thread that runs `catch_up()` then ticks every 5 min. The time source is an injected `now` callable, so tests drive `run_once`/`tick`/`catch_up` directly with a fake clock — no thread, no sleep.
  - Last-run source: `last_scheduled_run()` queries `max(Scan.finished_at)` where `trigger = "schedule"` (no new table; the `Scan` row is the record).
- `backend/vulntriage/main.py` — the lifespan starts the Scheduler behind the same `run_worker` flag as the ScanWorker (so `run_worker=False` tests start no thread), passing `app.state.kev_client`/`epss_client`; `app.state.scheduler` exposed; stopped on shutdown.

## Tests (`tests/test_scheduler.py`, I-SCHED, `sqlite_integration`)

- `run_once` re-scans **every** asset (one `schedule` Scan each) and the refresh is idempotent — a second same-day run makes no second notification job (US-8).
- `catch_up` runs immediately when the last scheduled run is 30h old (and when none exists).
- `catch_up` skips, and a same-day `tick` skips, when the last run is 10h old.
- `tick` does nothing at 05:59 with no prior run, runs once at 06:00, and does not re-run later the same day.

## Verified here (offline)

All files byte-compile. The time-boundary logic (06:00 gate, 24h catch-up,
once-per-day, no-prior-run) was validated with a standalone simulation of
`run_once`/`catch_up`/`tick` — all paths pass. The DB-backed assertions run in
`make verify` on the host.

## ⚠️ Verification

The sandbox cannot `uv sync`/run pytest (no PyPI). The human runs `make verify`;
I-SCHED is a `make test` case (SQLite + stubs, no Docker/network), so unlike the
Compose tasks it needs no cloud session — a normal `make verify` covers it.

## Out of scope (unchanged)

The n8n variant of the schedule (showcase task 33). A setting that turns the
backend scheduler off while n8n drives the schedule is part of the showcase n8n
task, not here.
