# Issue #17: Workflow transitions with required closing reason

**Date:** 2026-11-13T05:09Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox on `main` from `aee867a` (which held #16 and #18). Ponytail was on; sixth issue in the ponytail group.

- **Endpoint:** `socboard/cases.py` adds `POST /api/cases/{id}/transition`. The move is one conditional UPDATE that checks the target's one allowed source status and, for an Analyst, ownership. Only a refused move reads the case to choose 404, 403, 409 `invalid_transition` or 422 `reason_required` in the contract's order, then rolls back. A success writes `status_changed` (from, to, reason) through `append_audit` in the same transaction; the response is built before commit.
- **Supporting:** `errors.py` adds `invalid_transition` and `reason_required`; `schemas.py` adds `TransitionRequest`. Tests in `tests/test_transition_api.py`. The real route made the test-only transition route in `tests/backend_support.py` unreachable, so it was removed and `tests/test_backend_order.py`'s 200 call now targets a real case (QA confirmed no assertion lost).
- **Round 2 (Reviewer findings, approved):** 17-1 fixes race 18-3: `add_note` now starts with the claim's no-op conditional UPDATE, so a note can't land on a case closed in between (on SQLite and Postgres); a note-vs-close race test fails against the old `add_note`. 17-2: `reason_required` only when no reason was sent.
- **Round 3:** merged `origin/main` (`3dc8b90`, PR #113 NUL refusal and #18's summary) into `main` as `28bc7c8`; QA confirmed the merge changed no #17 code.
- **QA:** PASS at `f0d5911`, `7e84cd4` and `28bc7c8`; `make assert-clean` passed after each.
- **#16 note:** #16 was closed by hand by the human because `make issue-close` refused under #63 (the Engineer's Reflection named commit hashes). This session's #17 Reflection requests banned hashes.

**What I learned:** a hand-over comment posted after the Engineer's issue dump was missed; re-dump the issue before each launch.

## Reflection

### PM

unknown (role not asked; the PM had no part in #17 this session)

### Engineer

Reflection:
1. Slowed: round 1 missed the orchestrator's note about race 18-3, so QA and the Reviewer raised it and round 2 was needed. Round 2's prompt was the first time the request reached me.
2. Nearly wrong: the new race test could have passed without the fix. I checked it against the old `add_note`: it failed 13 of 15 runs, and passed 15 of 15 with the fix.
3. Proposal: in `_docs/agent-kit/procedures/orchestrator-comments.md`, have each Engineer launch list every orchestrator comment that asks something of the issue. Expected effect: no hand-off requests are missed in round 1. Measure: Reviewer findings that repeat an earlier orchestrator request, per issue.

### QA

Reflection:
1. Slowed: my first merge check compared the raw diffs with `cmp`, and both sides reported "NO" only because of hunk-header line offsets in the shared `socboard/schemas.py`. It took a second script (`git merge-tree --write-tree` plus a header-stripped compare) to prove the merge had no resolution edits. Setting up the probe also meant copying the conftest shim from the earlier `.scratch/qa17r/` run.
2. Nearly wrong: I could have read that first "NO" as a FAIL (the merge changed #17's code) if I hadn't looked into it further. Nothing was blocked.
3. Proposal: add a merge-recheck step to `_docs/agent-kit/team/qa-engineer.md` saying "compare `git merge-tree --write-tree <ours> <theirs>` with `<merge>^{tree}`; equal trees mean no resolution edits". Expected effect: one command instead of two scripts on merge re-checks. Measured by the number of `.scratch/` scripts per merge re-check in the next merge QA.

### Ponytail

Engineer: "reused the claim's no-op conditional UPDATE and the two-closes test's Barrier setup; skipped a Postgres run and any new helper or locking abstraction."

## Launch usage

Tool: Claude Code. Figures copied from the completion notifications.

- Engineer round 1: 539 s, 46 tool uses.
- QA round 1 (PASS at `f0d5911`): 259 s, 42 tool uses.
- Reviewer: 92 s, 16 tool uses.
- Engineer round 2: 491 s, 39 tool uses; merge (round 3): 281 s, 9 tool uses; reflection: 19 s, 4 tool uses.
- QA round 2 (PASS at `7e84cd4`): 223 s, 38 tool uses.
- QA merge check (PASS at `28bc7c8`): 262 s, 26 tool uses; after the reflection resume the notification read 292 s, 29 tool uses (cumulative or per-resume: unknown).

## Files created or modified

`socboard/cases.py`, `socboard/errors.py`, `socboard/schemas.py`, `tests/test_transition_api.py` (new), `tests/backend_support.py`, `tests/test_backend_order.py`, plus the merge of `origin/main` (#113, #18's summary), this file.

## Decisions made by the human

- Criteria 2 and 4 contradict `openapi.yaml`: the contract wins (a valid `closingReason` on a non-close move is ignored; order 401, 404, 403, 409, 422). Issue text unchanged; recorded in an `Orchestrator:` comment.
- Finding 17-1: useful (QA had raised it as 18-3). Finding 17-2: useful (QA had not raised it). Both applied.
- Accepted QA risks: explicit `"closingReason": null` gets a schema 422 (matches the contract); a note holds the write lock until it commits; the race test's comment mentions SQLite; a note made only of NULs gets `validation_error`, not `empty_note` (contract order).
- QA's stray private artifact deleted at the human's request.
- Merge `origin/main` into `main` before closing, with a QA check on the merge commit.

## Mismatches with the spec or design docs

- #17's criteria 2 and 4 contradict `openapi.yaml`; ruled above, text not edited.

## Commands to validate

- **Verify:** `make verify` (PASS at `28bc7c8`: 1441 Python, 157 frontend, no weakened tests).

## Proposed AGENTS.md changes

none. (Reflection proposals touch `_docs/agent-kit/` files; they are for the sweep.)

## Temporary changes

none. No processes started. The Engineer used `git stash` briefly in round 2 to test the race test against the old code and restored it; `git stash list` was empty and the tree clean afterwards. The orchestrator runs `make clean-scratch` at the end of this session.

## Interruptions

none.

## Unrelated problems noticed but not fixed

none.

## Follow-ups for the next session

- Kiro runs the sweep and ponytail comparison (`sweep-5-record` branch exists); the #16 and #17 Reflection proposals go to it.
- #112 needs grooming. #19 is next in order.
