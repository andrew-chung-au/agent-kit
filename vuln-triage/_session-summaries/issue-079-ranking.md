# Issue #79: Deterministic ranking and rank reason

**Date:** 2026-10-23
**Spec version:** (at `main` 041bec0)

## What changed and why

Task 7 of S1. Each finding now gets a deterministic tier, a total order and a
rank reason (US-5). No AI: the tier is one of four fixed rules, and the order is
total, so re-scoring the same inputs always gives the same result.

- **`ranking.py`** (pure functions + one DB writer):
  - `tier_for(inputs)` — the P1-P4 rules from `architecture.md` § Prioritisation,
    applied top to bottom, first match winning: P1 = KEV listed and exposed;
    P2 = KEV listed (not exposed) or EPSS high on an exposed asset; P3 = fix
    available and not P1/P2; P4 = everything else. Returns the tier and a
    plain-language reason naming the rule and the signals.
  - `sort_key` / `order_findings` — the total order: EPSS higher first (`n/a`
    after every scored finding), then criticality `critical` > `high` > `medium`
    > `low`, then older `first_detected_at`, then finding id ascending.
  - `rank_asset(session, asset_id)` — reads each finding's CVE `Signal` and the
    asset's exposure, writes `tier`, `rank_inputs` (JSON) and `rank_reason`
    (A20: scores `open` and `risk accepted` findings).
  - Fixed values only (A16-A18): T = 0.10; "exposed" = internet-facing or
    criticality `critical`; only `critical` counts as critical. No new threshold
    or enum.
- **`scan.py`** — `rank_asset` runs after KEV/EPSS enrichment, replacing the
  placeholder tier/rank fields task 5 created.

## Files created or modified

- New: `backend/vulntriage/ingest/ranking.py`.
- Modified: `backend/vulntriage/ingest/scan.py`.
- Tests: new `tests/test_ranking.py` (U-TIER, U-TIE, the I-RANK worked example,
  and a DB `rank_asset` case); `tests/test_ingest.py` (I-FINDINGS tier asserts).
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- No `rank` column exists on `Finding`; the ranked order is computed from the
  stored tier + `rank_inputs` via `order_findings` (used by `GET /findings` /
  `list_top_exposures`, tasks 9b/11). Task 7 populates the per-finding fields and
  provides the ordering function; `I-RANK` asserts the order.
- The rank reason format follows the architecture example
  ("P2: KEV listed, asset not exposed; KEV: not listed; EPSS 0.42; ...").

## Mismatches / VERIFY

- None new. All tier/tie-break/threshold values come from
  `architecture.md` § Prioritisation.

## Commands to validate

- **Verify:** `make verify BASE=origin/main` — NOT run in this session (Kiro Web
  sandbox has no PyPI access). All files byte-compile under CPython 3.12.13; the
  pure ranking logic and the worked-example order were validated standalone.
  **The human must run `make verify` before merge.**
