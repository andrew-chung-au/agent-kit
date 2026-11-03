# Issue #26: Backend data model and SQLite persistence

**Date:** 2026-10-23
**Spec version:** 9b04f90

## What changed and why

Task 3 of S1: the backend data model and its persistence. SQLAlchemy models for 14 tables (User, Session, Asset, Scan, Dependency, Vulnerability, Advisory, VulnerabilityAlias, Signal, Finding, Lifecycle, NotificationJob, AuditEntry, and the finding-dependency link table), enums stored as strings with a CHECK per column, a hand-written Alembic migration (`0001_initial_schema`), the finding uniqueness on `(asset_id, ecosystem, package, vulnerability_id)`, the E9 `identity_key()` rule, an append-only `AuditEntry` guard in the ORM, and one `DATABASE_URL` setting defaulting to `sqlite:///./.scratch/vulntriage.db`. No Brief table (task 30) and no KEV column (the KEV value is derived). No API, UI, seed data or committed database file. Backend tests went from 3 to 56.

## Files created or modified

- `backend/vulntriage/db/{__init__,enums,identity,models,session}.py`, `backend/alembic.ini`, `backend/migrations/{env.py,script.py.mako,versions/0001_initial_schema.py}`, `backend/pyproject.toml` (alembic), `backend/uv.lock`, `tests/conftest.py`, `tests/test_db_schema.py`, `tests/test_db_migration.py`, `_docs/testing.md` (U-SCHEMA, U-ENUM, U-CONSTRAINT, U-AUDIT) (`8ec6313`)
- `Makefile` (`d811e9b`, protected; approval record 6356828269): `backend-lock`
- `_docs/architecture.md` (`b3e08a7`): KEV value marked "derived, not stored"
- `AGENTS.md` (`b6086fa`, protected; approval record 6356930604): `make backend-lock` Commands line and the New migration note
- `_docs/ai-usage-log.md`, `_docs/roadmap.md` check-in

## Decisions made by the human

- Approved adding Alembic (`alembic>=1.16,<2`; locked 1.20.1 with mako 1.4.3, markupsafe 3.0.4).
- Makefile: add `backend-lock` only (no `db-upgrade`/`db-revision`); approved the exact diff, and the `make backend-lock` / `make backend-install` network steps.
- No `Brief` table; KEV value derived, not stored.
- PM defaults 4-6: store all NotificationJob kind/state values; ORM append-only guard on AuditEntry; single `DATABASE_URL`.
- Decision point: approved both `AGENTS.md` lines; reworded `architecture.md` now; QA's risks noted only.
- Outside #26: asked for a follow-up for the push-check image (uv missing). Chose a custom image, Python baked in, Dockerfile in the repo, scheduled right after #26, and all four extra tools now (`openapi-spec-validator`, `libpq-dev`, `pip-audit`, Terraform fmt/validate). Filed as #112.

## Mismatches with the spec or design docs

- The issue body lists `Brief` and a stored KEV value; `_docs/tasks.md` and `_docs/architecture.md` say otherwise. Followed the human's decision; the issue body was not edited, the PM comment supersedes it. `architecture.md` fixed in `b3e08a7`.
- The issue says SQLAlchemy needs approval; it was already in `backend/pyproject.toml` from #74.

## Commands to validate

- **Verify:** `make verify` (QA: PASS WITH WARNINGS; 62 frontend + 56 backend tests; the only warning is "test fixtures changed": `tests/conftest.py` now sets `PRAGMA foreign_keys=ON` (a tightening) and `tests/fixtures/MANIFEST.md` is flagged only because the diff base is origin/main)
- **Test (backend):** `make backend-test`
- **Lock backend:** `make backend-lock`

## Proposed AGENTS.md changes

Applied at the decision point and committed as `b6086fa`. None outstanding.

## Temporary changes

- `backend/.venv` gained alembic, mako and markupsafe (git-ignored, kept as the working environment).
- QA left `.scratch/qa26_check.py`, `.scratch/qa26_run2.py` and `.scratch/qa-26-comment.md`; removed by `make clean-scratch` at the end.
- No processes started.

## Permission review

- Read-only (propose allowing): WebFetch of `https://pypi.org/pypi/alembic/json` (Engineer; network read). `make issue-dump N=26` and `N=32` (orchestrator, QA; network read, ask rule). `gh issue view 32 --json body --jq .body` and `gh issue list --search ...` (orchestrator; network read).
- Writes to the record (keep asking):
  - `make issue-comment N=26 ...` (PM, Engineer, QA, orchestrator; posts to the tracker).
  - `gh issue create` for #112 and `make issue-comment N=112` (PM; merits request, filing approved by the human).
  - `HUMAN_APPROVED=1 git commit` for `Makefile` and `AGENTS.md` (orchestrator; protected files).
  - `make backend-lock` and `make backend-install` (orchestrator; network package downloads, new dependency, merits request).
  - `make issue-close N=26` (orchestrator; ask rule).
- Risky (propose denying): none.

The PM comment on #26 (6356748748) records "none so far (reads only)" with the Alembic and Makefile requests as asks; the PM's #112 commands are the orchestrator's account of the PM task, and the PM's own comment on #112 was not re-read for a permission line. The QA comment (6356915049) states none.

## Interruptions

none

## Unrelated problems noticed but not fixed

- The push check fails before `verify` because the image has no uv (since #74). Filed as #112, scheduled right after #26.
- QA risks outside the criteria, noted only (human choice): the `risk accepted` reason CHECK trims spaces only, so a tab- or newline-only reason passes the database (task 8's API must refuse it); the `AuditEntry` append-only guard is ORM-only (bulk delete and raw SQL bypass it); Python-side-only defaults (booleans, `attempts`, `state`, `scan_status`) mean raw-SQL writers must supply them; `findings.current_lifecycle_id` has no foreign key; the migration is untested on Postgres until #68.
- The PM's first-pass `Brief`/KEV mismatches were resolved by the human's decision.

## Follow-ups for the next session

- #112: the push-check image (`ci/push-check/Dockerfile`); the human builds the image and sets `AGENT_PUSH_CHECK_IMAGE`.
- Task 8 (API): refuse tab/newline-only `risk accepted` reasons.
- #68: run #26's persistence test against Postgres.
- Next in S1 per the roadmap: #76 (task 4), after #112.
