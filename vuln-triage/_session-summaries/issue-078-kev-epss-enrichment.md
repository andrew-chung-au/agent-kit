# Issue #78: KEV and EPSS enrichment

**Date:** 2026-10-23
**Spec version:** (at `main` 5eac3bf)

## What changed and why

Task 6 of S1. After OSV matching creates findings (#77), the backend now
enriches each finding's CVE with CISA KEV status and the FIRST EPSS score.

- **`signals.py`** — two injected-`httpx.Client` clients (like the OSV/GitHub
  readers) and `enrich_asset`:
  - `KevClient.fetch_catalogue()` — `GET` the whole CISA KEV JSON, parse
    `vulnerabilities[].{cveID,dateAdded}` into a `KevCatalogue`.
  - `EpssClient.fetch_scores(cves)` — `GET https://api.first.org/data/v1/epss?cve=<list>`
    in batches, parse `data[].{cve,epss,percentile,date}`.
  - `enrich_asset` — for every distinct CVE among the asset's findings'
    vulnerabilities, upsert a per-CVE `Signal`: set `kev_listed`/`kev_date_added`/
    `kev_fetched_at` and clear `kev_stale` on success; set EPSS score/percentile/
    date and clear `epss_stale`. A vulnerability with no CVE (E11) gets no
    `Signal` — the KEV value derives to `KEV: n/a (no CVE)` and EPSS to `n/a`
    from `Vulnerability.cve_id` via `kev_value`.
- **E3 (the key difference from OSV):** a KEV or EPSS failure keeps the
  last-known signal and sets its stale marker; it never raises to the scan and
  never changes the scan status (stays the OSV result). A CVE never successfully
  KEV-fetched keeps `kev_listed` null → derives to `KEV: not listed` + stale
  (US-4, I15).
- **Scan wiring** (`scan.py`, `worker.py`): `run_scan`/`run_pending_scans`/
  `ScanWorker` take optional `kev_client`/`epss_client`; enrichment runs after
  `match_asset` and before commit. None = no enrichment (ingestion-only paths).

## Files created or modified

- New: `backend/vulntriage/ingest/signals.py`.
- Modified: `backend/vulntriage/ingest/scan.py`, `backend/vulntriage/worker.py`.
- Tests: new `tests/test_signals.py` (U-KEV, U-EPSS, U-FEED) and
  `tests/signals_stub.py`; `tests/test_ingest.py` (I-FINDINGS extended);
  `tests/test_github_reader.py` (recorder tests updated).
- Fixtures: `tests/fixtures/kev/known_exploited_vulnerabilities.json`,
  `tests/fixtures/epss/epss.json`, `tests/fixtures/cves.txt`;
  `tests/record_fixtures.py` gains `SOURCE=kev` and `SOURCE=epss`;
  `tests/fixtures/MANIFEST.md` rows.
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- No new dependency (KEV/EPSS parsed from JSON with the standard library +
  `httpx`, already present).
- A CVE absent from the EPSS answer keeps its last-known score (not zeroed); the
  fetch still counts as successful, so the stale marker is cleared.
- Ranking is untouched (task 7): findings keep their placeholder tier/rank from
  task 5; this task only attaches signals.

## Mismatches / VERIFY

- `VERIFY:` the CISA KEV catalogue URL and `cveID`/`dateAdded` fields, and the
  FIRST EPSS `cve=` batch size and `epss`/`percentile`/`date` fields (marked in
  `signals.py`). Confirm with a live `make record-fixtures SOURCE=kev` /
  `SOURCE=epss`.
- `I-FINDINGS` runs as an sqlite-integration case under `make test` (the
  `GET /findings` API is tasks 9b/11; Postgres is #68).

## Commands to validate

- **Verify:** `make verify BASE=origin/main` — NOT run in this session (Kiro Web
  sandbox has no PyPI access). All files byte-compile under CPython 3.12.13; the
  KEV/EPSS fixtures and signal parse helpers were validated standalone. **The
  human must run `make verify` before merge.**
- **Record KEV/EPSS fixtures (human, live, later):**
  `make record-fixtures SOURCE=kev` and `make record-fixtures SOURCE=epss`.
