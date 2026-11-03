# Issue #139 (task 19): CI test pipeline

**Date:** 2026-10-23
**Branch:** `feat/139-ci-pipeline`

## What changed and why

Task 19 of Milestone B (S2): every pull request runs the test jobs before any
deploy. The single `verify` job is split into the named jobs from
`_docs/testing.md` § CI jobs, so each test area fails a PR independently and the
job list shows which area is red. Depends on #88 (task 14) and #138 (task 16),
both merged.

## Design (human chose Option B)

The backend jobs are split by the existing pytest markers (`unit`,
`sqlite_integration`) via thin `make` targets, so every job runs through `make`
(the project convention) rather than raw `pytest` in CI.

New Makefile targets (protected, human-approved):
- `test-unit` — `pytest -m unit`
- `test-sqlite-integration` — `pytest -m sqlite_integration`
- `test-conformance` — `pytest tests/test_openapi_conformance.py` (the I-CONTRACT case)

`.github/workflows/verify.yml` now has six jobs on `push` + `pull_request`:

| Job | Target(s) | Toolchain |
|---|---|---|
| `unit` | `make backend-install`, `make test-unit` | python + uv |
| `sqlite-integration` | `make backend-install`, `make test-sqlite-integration` | python + uv |
| `frontend` | `make frontend-install`, `make frontend-test`, `make frontend-typecheck` | node |
| `openapi-validation` | `make backend-install`, `make openapi-validate`, `make test-conformance` | python + uv |
| `postgres-integration` | `make backend-install`, `make test-integration` | python + uv + Docker (on `ubuntu-latest`) |
| `verify` | `make install`, `make verify` | python + uv + node |

Each job installs only the toolchain it needs (backend jobs do `backend-install`,
not the full `install`).

## Why the `verify` job is kept

The five split jobs cover the tests, but not the whitespace check and the
weakened-test detection that `make verify` does. Keeping a `verify` job preserves
those gates on every PR (and runs the suite as a backstop). The weakened-test
check needs a real `BASE` to diff against, which is #67 (a separate follow-up);
until then it runs with the default BASE, as the old single job did.

## Acceptance criteria mapping

- Jobs `unit`, `sqlite-integration`, `frontend`, `openapi-validation`, `postgres-integration` added, matching the testing.md table ✅ (plus the retained `verify` gate)
- Every job runs on PR and on push; a push to `main` re-runs the set ✅ (`on: [push, pull_request]`)
- A broken test fails the matching job; clean `main` passes all ✅ (human confirms on the first PR run)
- No job needs a live feed or a secret ✅ (`permissions: contents: read`; the network guard blocks outbound HTTP)

## Out of scope (unchanged)

- `security-scan` job — task 20.
- Deploy jobs — tasks 17, 21.
- Compose `telemetry`/`alert`/`responder` jobs — Tier C.
- #67 (CI passes a real `BASE`) — separate follow-up.

## ⚠️ Verification

The real proof is the first CI run on the PR (the sandbox cannot run GitHub
Actions). Checked here: every `- run: make …` command maps to a real Makefile
target; the marker split covers the whole backend suite (every test module is
module-marked or has all tests function-marked `unit`/`sqlite_integration`), so
`test-unit` + `test-sqlite-integration` leave no backend test unrun.

`VERIFY:` on the first PR run, confirm (a) each job appears and can fail
independently, (b) `postgres-integration` brings up the `vt-test` db on the
runner, and (c) no backend test is collected by neither `-m unit` nor
`-m sqlite_integration` (i.e. the two backend jobs' combined count equals the
full `backend-test` count).
