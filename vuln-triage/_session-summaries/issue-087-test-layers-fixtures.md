# Issue #87: Backend test layers and stored fixtures (task 13)

**Date:** 2026-10-23
**Spec version:** (at `main` 6566690)

## What changed and why

Task 13 of S1. `make test` runs the backend unit and SQLite integration layers
with stubs and committed fixtures. Most of this was built incrementally by
tasks 1-12; this task consolidates it so the two layers are cleanly selectable
by pytest marker (needed for the task-21 CI `unit` / `sqlite-integration`
split) and audits the fixtures and manifest.

Already present (tasks 1-12), confirmed here:
- The network guard with its own `U-NET` and `I-NET` cases
  (`tests/test_network_guard.py`); every external call uses a stub or a
  committed fixture.
- The stubs (`github_stub`, `osv_stub`, `signals_stub`, `conftest`), the
  github/osv/kev/epss fixtures, `tests/record_fixtures.py`
  (`SOURCE=github|osv|kev|epss`, never run in CI), and `tests/fixtures/MANIFEST.md`
  with a source and capture date for every captured fixture.
- `make test` runs the frontend suite then the backend suite; it is unchanged
  as the single local test command.

Added:
- A module-level `pytestmark` (`unit` or `sqlite_integration`) to the 10 test
  files that had none, so every `U-*` / SQLite `I-*` case carries a marker:
  - unit: `test_github_reader`, `test_parser_package_lock`,
    `test_parser_requirements`, `test_parser_uv_lock`.
  - sqlite_integration: `test_api_assets`, `test_api_auth`, `test_api_findings`,
    `test_api_mcp`, `test_api_service`, `test_ingest`.
  Files with existing per-test marks (`test_db_migration`, `test_db_schema`,
  `test_network_guard`, `test_ranking`, `test_smoke`, and the already-marked
  modules) were left as they were.
- `addopts = "--strict-markers"` in `backend/pyproject.toml`: an unknown marker
  is now an error (it catches a typo like `sqlite-integration`); it does not
  require a mark.

## Files created or modified

- Modified: the 10 test files above (one `pytestmark` line each);
  `backend/pyproject.toml` (`--strict-markers`).
- `_docs/ai-usage-log.md` entry.

## Decisions made (pending human confirmation)

- Scope is harness/fixtures consolidation. The `U-*`/SQLite `I-*` cases for
  tasks 1-12 are implemented; checks owned by later tasks (I-CONTRACT task 14,
  I-SCHED task 38, I-OWNER-* task 37, the Showcase I-* cases) stay with those
  tasks. The task's check is "`make test` passes with both layers".
- `--strict-markers` only rejects unknown markers; unmarked tests still run, so
  nothing is skipped or weakened.

## ⚠️ Could not run the suite here

The Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI), so
`make test` / `make verify` could NOT run. All test files byte-compile under
CPython 3.12.13; marker coverage was audited and the MANIFEST confirmed to name
every captured fixture. **The human must run `make verify` before merge.**

## Commands to validate

- **Verify (human):** `make verify` — NOT run here (no PyPI). `make test` runs
  both layers; `make record-fixtures SOURCE=<...>` is the re-capture path and
  never runs in CI.
