# Issue #80: Finding lifecycle, re-scan and audit trail

**Date:** 2026-10-23
**Spec version:** (at `main` 2710d12)

## What changed and why

Task 8 of S1. A scan (registration or re-scan) now drives every finding through
its status machine and records every change in the append-only audit trail.

- **`lifecycle.py`** — the status machine and audit writer:
  - `create_finding` — a new vulnerable dependency gets an `open` finding, its
    first `Lifecycle`, dependency links and a creation audit entry.
  - `apply_rescan(finding, state)` — transitions, from the spec's finding-status
    table: all merged advisories withdrawn → `withdrawn` (saving the prior status
    in `status_before_withdrawal`, never `fixed`, E4); reinstated + in range →
    restore `open`/`risk accepted` (a restored acceptance names the earlier audit
    entry via `restores_entry_id`); reinstated + out of range → `fixed`; out of
    every live range → `fixed` (US-10, including from `risk accepted`, E8); a
    `fixed` finding whose vulnerable version returns → `open` + a new lifecycle
    (E7).
  - Every change writes an `AuditEntry` (previous value, actor `re-scan`, source
    `OSV`); creation records actor/timestamp only. No automated path sets
    `risk accepted` — a restore only reinstates a human's earlier acceptance
    (US-11).
- **`matcher.py`** — `match_asset` now reconciles every `(asset, package,
  vulnerability)` on each scan: it groups withdrawn advisories too (to detect
  withdrawal and reinstatement), upserts the vulnerability lazily (a
  withdrawn-at-first-sight advisory with no finding records nothing, E4), and
  closes findings OSV no longer returns (an upgrade that drops a vuln out of the
  answer → `fixed`). Returns whether any finding is `open`/`risk accepted` (the
  `scanned, findings` status).
- **`ranking.py`** — E8: a `risk accepted` finding whose tier rises or whose KEV
  becomes listed keeps its status but is flagged `signals_changed`.

## Files created or modified

- New: `backend/vulntriage/ingest/lifecycle.py`.
- Modified: `backend/vulntriage/ingest/matcher.py`, `backend/vulntriage/ingest/ranking.py`.
- Tests: new `tests/test_lifecycle.py` (US-10, E4 withdraw/restore, E7, E8, audit)
  with a programmable OSV client; `tests/test_ranking.py` E8 flag test. The
  existing `test_matcher.py` first-scan cases are unchanged in intent.
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- `Lifecycle.due_at` is set to the lifecycle start as a placeholder; the real
  US-9 due date is task 10a.
- The risk-accepted E4 restore leaves `AuditEntry.reason` null and sets
  `restores_entry_id`, which the model's CHECK constraint allows (a restore is
  not a new acceptance).
- E8 signals-changed detection lives in `rank_asset` (it needs KEV/EPSS, which
  run before ranking); the range/withdrawal transitions live in the matcher.

## Mismatches / VERIFY

- None new. Status strings, audit fields and transitions come from
  `specs.md` § Finding statuses and `architecture.md` § Data model.

## Commands to validate

- **Verify:** `make verify BASE=origin/main` — NOT run in this session (Kiro Web
  sandbox has no PyPI access). All files byte-compile under CPython 3.12.13; the
  full lifecycle state machine was validated standalone against every transition.
  **The human must run `make verify` before merge.**
