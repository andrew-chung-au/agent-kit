# Issue #77: OSV matching and fixed-version resolution

**Date:** 2026-10-23
**Spec version:** (at `main` 9d1f79a)

## What changed and why

Task 5 of S1. After the scan stores the asset's dependencies (#76), the backend
now matches each installed `(ecosystem, name, version)` against OSV, merges the
answers into vulnerabilities and creates findings.

- **Version ordering** (`versions.py`): PyPI via `packaging` (PEP 440, already a
  dependency); npm SemVer 2.0.0 precedence implemented in-house (a SemVer library
  is approval-gated, so none was added). No raw string compare.
- **Fixed version** (`osv_ranges.py`, pure): the five-step rule from
  `architecture.md` § Ingestion and matching. Turns OSV `affected[]` ranges and
  events into intervals (`introduced`/`fixed` exclusive/`last_affected`
  inclusive; `introduced: "0"` = from the start; explicit `versions[]` are
  one-version intervals; `GIT` ranges skipped), finds the intervals containing
  the installed version, and returns the lowest `fixed` candidate that lies
  outside every containing interval. An open-ended or `last_affected`-only
  interval gives no fixed version (E1, A11). Evaluated across all merged
  advisories together (E9).
- **OSV client** (`osv.py`): `POST /v1/querybatch` then `GET /v1/vulns/{id}`,
  `api.osv.dev` only, no redirects, 10 s timeout with two retries, then
  `FeedUnavailable` (E3). The `httpx.Client` is injected, like the GitHub reader.
- **Matcher** (`matcher.py`): batches one query per distinct installed version
  (version-unknown entries skipped, E10); caches advisories by id and `modified`;
  union-find merges advisories whose alias sets intersect into one
  `Vulnerability` keyed by CVE else the primary advisory id (E9), recording every
  id in `VulnerabilityAlias`; drops an advisory already withdrawn at first sight
  (E4, no finding); creates one `open` `Finding` per `(asset, package,
  vulnerability)` with its `FindingDependency` links; A6 merges the same package
  across files (fixed version = highest per-entry value, or none if any entry has
  none).
- **Scan wiring** (`scan.py`, `worker.py`): `run_scan`/`run_pending_scans`/
  `ScanWorker` take an optional OSV client (None = ingest only, so the worker and
  ingestion-only tests need no OSV stub). The interim status rule is replaced by
  `status_for_result`: `scanned, findings` when any finding matched, else the
  warning-based `incomplete`/`clean`. An OSV `FeedUnavailable` rolls back the
  transaction (keeping last-known dependencies) and records `scan failed` /
  `feed unavailable` (E3).

Findings are created with placeholder rank fields (`tier=P4`, `rank_inputs={}`,
`rank_reason=""`) because ranking is task 7.

## Files created or modified

- New: `backend/vulntriage/ingest/versions.py`, `osv_ranges.py`, `osv.py`,
  `matcher.py`.
- Modified: `backend/vulntriage/ingest/scan.py`, `backend/vulntriage/worker.py`.
- Tests: new `tests/test_versions.py`, `test_osv_ranges.py`, `test_osv_client.py`,
  `test_matcher.py`; `tests/osv_stub.py`; edits to `tests/test_ingest.py`
  (the two interim tests updated; `I-FINDINGS` scan-to-findings case added).
- Fixtures: `tests/fixtures/osv/` (querybatch, four advisories, `packages.txt`,
  README); `tests/record_fixtures.py` extended with `SOURCE=osv`;
  `tests/fixtures/MANIFEST.md` rows.
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- npm SemVer implemented in-house rather than adding a dependency (keeps the
  no-new-dependency rule; the architecture named `semver` as "ask before adding").
- `I-FINDINGS` written as an sqlite-integration case (the `GET /findings` API is
  tasks 9b/11; Postgres is #68), so it passes under `make test` as the issue asks.
- OSV fixtures are project-authored for deterministic cases; versions line up with
  the recorded GitHub fixtures (pygoat: urllib3 1.26.9, PyYAML 5.1, Django 4.2,
  requests 2.28.2).

## Mismatches / VERIFY

- `VERIFY:` OSV endpoint shapes, querybatch size/rate limits and the `limit`
  event meaning (marked in `osv.py`/`osv_ranges.py`). Confirm with a live
  `make record-fixtures SOURCE=osv`.
- A10 "range evaluation mismatch" warning (OSV returns an advisory the backend's
  own range check does not match) is not yet recorded; task 5 creates the
  advisory/vulnerability rows but no finding in that case. For a follow-up.

## Commands to validate

- **Install:** `make install` (needs the push-check image for the push).
- **Verify:** `make verify` — NOT run in this session: the Kiro Web sandbox is
  network-mode INTEGRATIONS_ONLY with no PyPI access, so dependencies could not be
  installed. All files byte-compile under CPython 3.12.13; the pure algorithms
  (SemVer precedence, the five-step fixed-version rule loaded from the real
  modules, the alias union-find) were validated standalone. **The human must run
  `make verify` before merge.**
- **Record OSV fixtures (human, live, later):** `make record-fixtures SOURCE=osv`.
