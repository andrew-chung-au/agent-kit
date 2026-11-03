# Issue #76: Asset registration and repository ingestion

**Date:** 2026-10-23
**Spec version:** 9b04f90

## What changed and why

Task 4 of S1. `POST /assets` validates a registration, stores the asset and a `Scan` row, and returns 201 at once. An in-process worker thread then reads `uv.lock`, `requirements.txt` and `package-lock.json` from the repository through a GitHub reader (GET only, `api.github.com` only, no redirects, optional `GITHUB_READ_TOKEN`), parses them with three pure parsers and stores the dependencies and warnings, or records `repository unavailable`, `no dependency files` or `lockfile parse error`. The `Scan` row is the job (no schema change); the status after a successful read follows an interim rule until task 5 adds OSV. `-r` includes outside the repository or remote are refused and never fetched. All tests use project-authored fixtures and stubs; no live GitHub call was made. Backend tests went from 56 to 246.

## Files created or modified

- Dependencies `httpx` 0.28.1 and `packaging` in `backend/pyproject.toml` and `backend/uv.lock` (`fb33f75`).
- `backend/vulntriage/ingest/` (`uv_lock`, `requirements`, `package_lock`, `github`, `scan`, `models`, `settings`), `backend/vulntriage/worker.py`, `backend/vulntriage/api/assets.py`, `backend/vulntriage/main.py`, `.env.example`, `tests/` parser, reader, ingest and API tests, `tests/record_fixtures.py`, `tests/github_stub.py`, `tests/fixtures/github/**` and `tests/fixtures/MANIFEST.md` (`a6a342f`, `6ba1cae`, `1d7c25f`, `c5ef99b`, `7f08719`).
- `Makefile` `record-fixtures` target (`95eb7bf`, protected; approval record 6358822028).
- Include-path fix (`9a7950d`): an include path with unsupported characters now gives `include refused` instead of failing the scan.
- `_docs/testing.md` and `_docs/architecture.md` doc notes (`c3f5a46`, layout corrected in `2f54435`).
- `_docs/ai-usage-log.md`, `_docs/roadmap.md` check-in.

## Decisions made by the human

- D1: `httpx` and `packaging` approved. D2-D6 accepted as the PM recommended (`GITHUB_READ_TOKEN` and `.env.example`; interim scan-status rule; the `Scan` row is the job with one worker; `local_packages` for npm link/workspace entries; `POST /assets` unguarded until tasks 9a/9b).
- D7: the exact Makefile `record-fixtures` diff approved; the AGENTS.md Commands line held on purpose; fixture repositories deferred to the live capture.
- Decision point: fix QA's path-character finding now; apply the doc spec notes now (not the `specs.md` E10 gaps); note the remaining risks only; defer the fixture repository choice.

## Mismatches with the spec or design docs

- `specs.md` E10 gaps are still open: whether a missing in-repository include counts toward `scanned, incomplete` (implemented: yes), and whether an exact pin with an environment marker is "version unknown" (implemented literally, may over-warn). For the next approved spec change.
- `_docs/testing.md` counts test handles; adding `U-GITHUB` may change the case count it records. Not recomputed.
- The architecture's GitHub read shape (endpoints, `X-GitHub-Api-Version`, 409 for an empty repository, directory-as-absent) is still VERIFY until the human runs the live capture.

## Commands to validate

- **Verify:** `make verify` (QA: PASS WITH WARNINGS at `2f54435`; 62 frontend + 246 backend tests; warnings are the new project-authored fixtures and a `tests/test_smoke.py` paths assertion updated for `POST /assets`, judged a legitimate update)
- **Test (backend):** `make backend-test`
- **Record fixtures (human, live GitHub, later):** `make record-fixtures SOURCE=github`

## Proposed AGENTS.md changes

Held, not applied: a `make record-fixtures` Commands line (batch with the next AGENTS.md change).

## Temporary changes

- `backend/.venv` gained httpx, httpcore and certifi (git-ignored, kept).
- `.scratch/` files removed by `make clean-scratch` at the end. No processes started.

## Permission review

- Read-only (propose allowing): `make issue-dump N=76` (orchestrator, Engineer, QA; ask rule).
- Writes to the record (keep asking): `make issue-comment N=76 ...` (PM, Engineer, QA, orchestrator; posts to the tracker); `make backend-lock` and `make backend-install` (orchestrator; network package downloads, new dependencies, merits request); `HUMAN_APPROVED=1 git commit` for `Makefile` (orchestrator; protected file); `make issue-close N=76` (orchestrator; ask rule).
- Risky (propose denying): none.

The PM, Engineer and QA comments state no approvals needed.

## Interruptions

none

## Unrelated problems noticed but not fixed

Risks from QA and the Engineer, carried to the owning tasks (human choice, no follow-up issue):
- `lastScanAt` is set on a failed first scan (decide "last attempt" or "last successful scan" before #82).
- `run_scan` deletes and re-inserts `Dependency` rows; task 8 (#80) must keep rows referenced by `finding_dependencies`.
- An unexpected scan error leaves the scan unfinished and it is re-queued at every start; a repeating error would loop (no error state in the four failure reasons).
- The global 422 handler returns a fixed message for all future routes.
- A legitimate file name with non-ASCII, `$`, `%` or `;` is flagged and keeps the repository at `scanned, incomplete`.
- `scanWarnings` is `[]` on the wire until #82; `POST /assets` needs the 401/403/CSRF criteria in #82.
- The `starlette.testclient` "install httpx2" warning is harmless now.
- #112 (the push-check image) is still open and waits on the human's build and push steps.

## Follow-ups for the next session

- The human confirms three small public fixture repositories, puts them in `tests/fixtures/github/repositories.txt`, runs `make record-fixtures SOURCE=github`, then the Engineer checks the captures for tokens and fixes the MANIFEST rows.
- Close #112 once the human reports the image results.
- Next in S1 per the roadmap: #77 (task 5, OSV matching).
