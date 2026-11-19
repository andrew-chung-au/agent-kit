# Issue #194: Prove single ownership on Postgres under simultaneous claims

**Date:** 2026-11-14T19:12Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Spec §5: one owner under simultaneous claims, on any supported database. New `tests/test_claim_concurrency.py` (tests only, no application change):
- 8 claims of one case, 50 rounds on fresh cases: one 200, seven 409 `already_claimed`, the owner is the 200's user, the status unchanged, one `claimed` entry; later claims by both users still 409 with the state unchanged.
- A claim racing a close, 20 rounds: either claim-first (owner set, Closed, `claimed` then `status_changed`) or close-first (claim 409 `case_closed`, no owner, `status_changed` only); anything else fails.
- Every round blocks the requests behind a held row lock. On Postgres it fails unless every request is seen waiting on a lock before the release; SQLite has no such view, so it waits 0.3 s.
- One line in `_docs/planning/roadmap-1-core.md` places the follow-up #203 in the supporting list.

Branch `issue-194-claim-race`, draft PR #204. Claim: https://github.com/andrew-chung-au/socboard/issues/194#issuecomment-6882247645 (it says the branch was cut at `361c58a`; it was cut at `13b8362`, the #192 merge, which is the `origin/main` head that contains `361c58a`). CI on `4c481cd`, all success: Postgres `tests` job 132549685387 (both tests ran, `1697 passed, 378 deselected`), verify pull_request run 43628518879 (`VERIFY: PASS`, 18 assertion lines added, 0 removed). QA PASS at `4c481cd`, Lows only: https://github.com/andrew-chung-au/socboard/issues/194#issuecomment-6882805675. No race found.

**What I learned:** inside one transaction Postgres returns the same `pg_stat_activity` snapshot, so a poll loop must run in autocommit. It cost two CI rounds (`e0a6216`, `f8e7cd4`) to find.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

**What slowed you down (evidence):** three 6-minute CI rounds for a test bug a local Postgres would have shown in one run; one QA launch cancelled and relaunched.
**What nearly went wrong or was blocked:** nothing blocked; the overlap check correctly failed instead of passing a race that did not happen.
**One proposed change (file, expected effect, measure):** see #192's summary (a local database server in `.scratch/`); the human asked for it at the end of this issue.

## Launch usage

QA: 2 launches (one cancelled with no result, one PASS). Active time and tool uses: unknown.

## Files created or modified

- `tests/test_claim_concurrency.py` (new)
- `_docs/planning/roadmap-1-core.md` (one line)
- `_session-summaries/2026-11-14T1912Z-issue-194-orchestrator-claim-race.md` (this file)

## Decisions made by the human

- Labelled #194 `approved`; the PM's two questions followed as the body is written (same sizes on both databases; start after #192 merged).
- Asked for #203 to be filed as a follow-up.
- Asked for a local Postgres in this sandbox to shorten the work (applied from #193 on).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify` (CI run 43628518879). Adds about 36 s on SQLite.
- **Test (one file):** `make test-one FILE=tests/test_claim_concurrency.py`; on Postgres, the CI `tests` job.

## Proposed AGENTS.md changes

none

## Temporary changes

- The relaunched QA saved CI logs under `/tmp` (outside the folder, against AGENTS.md).

## Interruptions

- The first QA launch was cancelled with no result; it was relaunched.

## Unrelated problems noticed but not fixed

none

## Follow-ups for the next session

- QA Lows: the lock count is not limited to the round's own requests; on SQLite nothing checks the requests were waiting before release; `assert seen` cannot fail; the roadmap line is outside the `tests/`-only constraint.
