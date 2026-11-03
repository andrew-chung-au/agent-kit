# Issue #50: API contract: responder agent read-only endpoints (US-15)

**Date:** 2026-10-22
**Spec version:** 97893c1

## What changed and why

Roadmap step 8b. #27 left US-15's responder without a documented data path, so `_docs/api.md` and `_docs/openapi.yaml` now cover every call the responder makes, under a fourth bearer scheme `responderAuth` (role `responder-read`, GET only):

- `GET /responder/findings/{id}` (`responderGetFinding`): the `FindingWithAsset` shape without `untrustedAdvisoryData`.
- `GET /responder/notification-jobs` (`responderListNotificationJobs`): a finding's jobs in every state, as the strict `ResponderNotificationJob` schema (no recipient, owner or advisory text; `lastErrorCode` and `traceparent` included).
- Logs are not in the API: the responder reads them from Loki with the Viewer token (`api.md` "Responder (US-15)" section).

After QA PASS, three approved architecture edits (spec notes 1-3) aligned `architecture.md` with the contract.

Also at the human's request this session: filed #56 (Stage 4 test strategy, roadmap step 10) for a parallel agent.

## Files created or modified

- `_docs/openapi.yaml`, `_docs/api.md` (`6ff10d9`, merged in PR #57 as `9a03ba9`)
- `_docs/ai-usage-log.md` (`3188ce7`, Engineer entry)
- `_docs/architecture.md` (protected; `cd870df`, `54bdce3`, `147bd7a`)
- `_docs/roadmap.md` (row 8b, step 10 and check-in line)
- `_session-summaries/issue-050-responder-read-only-contract.md` (this file)

## Decisions made by the human

- Before this session (grooming): D1 Loki only for logs, D2 responder-only job schema, D3 no `untrustedAdvisoryData`, all option 1.
- Contract diff: the human merged PR #57 (`9a03ba9`) after review; no separate approval statement was recorded, and the merge was treated as the approval.
- Decision point: approved all three spec notes (architecture security-boundaries row, refused case, secrets row) and asked to close #50. The QA risks outside the criteria were proposed for #24 notes or the next `api.md` edit; the reply did not change that, so they are recorded under Follow-ups.
- Approval records, one per protected commit: 6329360243 (`cd870df`), 6329361058 (`54bdce3`), 6329361312 (`147bd7a`).

## Mismatches with the spec or design docs

- Fixed by the three approved commits: architecture said "GET findings, jobs and logs" and a "job retry `POST`" refused case that has no matching operation; the secrets row did not name `RESPONDER_API_TOKEN`.
- Open and cosmetic: the CSRF sentence in `api.md` and `info.description` does not name the responder operations.

## Commands to validate

- **Verify:** `make verify` (PASS at `9a03ba9`, 62 tests)
- **Validate OpenAPI:** `make openapi-validate` (exit 0; QA's broken-`$ref` copy exits 2)
- **Assert clean:** `make assert-clean` (PASS at `9a03ba9`)

## Proposed AGENTS.md changes

none

## Temporary changes

none. Nothing was started; `.scratch/` cleaned with `make clean-scratch`. The session branch was restarted from `origin/main` after PR #57 merged, as the cloud-session rule requires.

## Permission review

Engineer comment 6329142996, QA comment 6329301519 and PM comment 6317612610 each report no approvals.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `git commit` with `HUMAN_APPROVED=1` for the three protected `architecture.md` commits (merits: protected-file commit); `make issue-comment` for the three approval records.
- Risky (propose denying): none. `git push origin HEAD:claude/sleepy-euler-bzyy0r` was refused by the `guard_git.py` hook; the allowed form `git push -u origin claude/sleepy-euler-bzyy0r` was then used.
- Proposed `opencode.json` and `.claude/settings.json` changes: none

## Interruptions

none

## Unrelated problems noticed but not fixed

- The `make verify` header compares against a stale base ref (`origin/<session branch>`) in cloud sessions; related to #53.
- Roadmap says #50 is placed "after #45"; the stale line near the end of the roadmap was updated here.

## Follow-ups for the next session

- #56 (step 10, Stage 4 testing): finish its US-15 section against the closed contract.
- #24 (conformance): confirm that `id` descending order matches numeric order for non-padded ids, and that every job state carries a non-null `traceparent`.
- Next `api.md` edit: name the responder operations in the CSRF sentence.
- Spec notes still open from the roadmap's step 10 list (tier label test, alert resolve and re-fire after a metric gap, Grafana "resolved" message).
