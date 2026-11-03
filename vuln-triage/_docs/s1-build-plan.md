# S1 build plan (Tier A)

Status: 2026-10-23. This is the context-efficient runbook for phase S1. The
source of truth for order and scope stays `_docs/roadmap.md` (S1) and
`_docs/tasks.md` (tasks 1-14); update this file only when a decision changes.

## Locked decisions

- `#109`: option 1 for the ownerless flag (only an asset with both owner fields
  unset is ownerless) and option 2 for E8 (one `signals changed` job per
  recipient, key includes the recipient).
- Dependencies: the Python runtime/test set is approved as a batch. Versions are
  pinned in `backend/uv.lock`; a new package outside the batch still needs
  approval.
- Fixtures: public repositories only, no token. `make record-fixtures
  SOURCE=<github|osv|kev|epss|all>` validates the value inside make before any
  shell runs, is never called by `make test`, `make verify` or CI, and writes
  `MANIFEST.md` rows with source URL, capture date and (GitHub) commit SHA. The
  Engineer checks captured files for tokens/private data before committing and
  records that check in the issue comment.
- `#74` CI decision D1: option A. `.github/workflows/verify.yml` installs uv
  0.13.1 with `astral-sh/setup-uv@v5` before `make install`.
- Environment: local sandbox, SQLite only, no Docker in S1. Commit on `main`,
  never push.

## Issue order

| Order | Issue | Task | Exit gate |
|---|---|---|---|
| 0a | #74 | 1 | Skeleton, smoke test, network guard, SQLite fixture, manifest shell; `make test` runs frontend + backend |
| 0b | #75 | 2 | Evidence note with one source for each of the four documentation criteria |
| 1 | #26 | 3 | Full data model, enums, constraints, migration, audit-entry test |
| 2 | #76 | 4 | `POST /assets`, GitHub reader, three parsers, worker/job table; fixture capture checkpoint |
| 3 | #77 | 5 | OSV matching, aliases/E9, fixed version, withdrawal |
| 4 | #78 | 6 | KEV/EPSS, `Signal`, stale markers |
| 5 | #79 | 7 | P1-P4 ranking, tie-breaks, rank reason, worked example |
| 6 | #80 | 8 | Status transitions, re-scan, audit, E4/E7/E8 |
| 7 | #109 | - | Four review-2 plan fixes; must precede #81-#84 |
| 8 | #81 | 9a | Session cookie, CSRF, lockout, user CLI, role guard |
| 9 | #82 | 9b | Findings/assets/re-scan/risk/PATCH endpoints, error order |
| 10 | #83 | 10a | Signals/scans, jobs/idempotency/traceparent, future-development stubs |
| 11 | #84 | 10b | MCP and responder read operations, GET-only allowlists |
| 12 | #85 | 11 | Real `Services`, Vite proxy, dashboard views, `make dev` |
| 13 | #86 | 12 | Risk acceptance, audit, re-scan and asset-edit UI |
| 14 | #87 | 13 | Single `make test`, malicious fixture, complete manifest |
| 15 | #88 | 14 | OpenAPI conformance over 22 operations, `/health` excluded |
| 16 | - | - | Auditor: Application 2 and Testing 2; roadmap S1 done |

## Per-issue gate

1. PM grooming comment on the issue (`PM:`).
2. Engineer implements, tests, commits explicit paths, runs `make verify
   BASE=<first-commit-parent>`.
3. QA checks independently and posts `QA: PASS/FAIL`.
4. Orchestrator runs `make assert-clean` and checks HEAD is unchanged.
5. Decision point: protected files, dependencies, spec notes, outside-criteria
   risks. Apply approved protected changes in their own `HUMAN_APPROVED=1`
   commit and post the approval record.
6. Session summary, `_docs/ai-usage-log.md`, roadmap check-in line,
   `make clean-scratch`, close the issue.

## Approval checkpoints

- `#74`: `Makefile` (`install`, `test`, `backend-test`) and `AGENTS.md`
  Commands lines. The Engineer leaves the `Makefile` edit uncommitted for the
  approval; the orchestrator commits it with `HUMAN_APPROVED=1`.
- `#76`: `Makefile` `record-fixtures` (protected), plus the human-run capture.
- `#85`: `Makefile` `dev`/`dev-start`/`dev-stop` (protected) and `AGENTS.md`
  Commands lines.
- `#109`: planning documents only; `_docs/specs.md` only with explicit approval.
- Dependencies: only the approved batch; anything else stops and asks.

## Fixture checkpoint

- `#76` builds `make record-fixtures`. After it lands, the human runs
  `make record-fixtures SOURCE=all` once. Public repositories only.
- `#77` and `#78` consume the captured files; the Engineer records the
  token/private-data check before committing.
- `#87` adds the project-authored malicious advisory fixture and completes the
  manifest.

## S1 done

- `make install`, `make test`, `make verify` and `make openapi-validate` pass.
- `make dev` starts the backend and frontend together on SQLite; a manual
  start/stop smoke test passes.
- The rubric auditor re-audits the final commit and marks Application 2 and
  Testing 2 in `_docs/rubric-evidence.md`.
- `_docs/roadmap.md` marks S1 `done` with a check-in line; the session summary
  is committed.

## Session and context protocol

- Start each issue in a fresh session. Read `AGENTS.md`, this file, the issue
  and the latest PM comment only.
- Point PM/Engineer/QA subagents at the exact document sections; they read in
  their own context. Do not read whole planning documents in the main session.
- Keep durable state in issue comments, session summaries and this file, not in
  chat history.
- Use targeted reads (`grep`, offsets, `gh ... --jq`) and avoid dumping large
  files.
- If a session passes roughly 60% context, stop at the next clean hand-over
  point, write the session summary or a short handoff note, and continue in a
  fresh session.

## Current state

- `#74`: PM groomed at comment 6355211703; D1 = A. The Engineer run was
  cancelled before making changes; the tree is clean.
- Next: start a fresh session for `#74` from the PM comment. The Engineer
  leaves the `Makefile` edit uncommitted and returns its exact diff for
  approval.
