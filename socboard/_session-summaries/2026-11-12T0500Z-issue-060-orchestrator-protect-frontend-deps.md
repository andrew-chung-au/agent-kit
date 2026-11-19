# Issue #60: Protect the frontend dependency files

**Date:** 2026-11-12T05:00Z (UTC)
**Spec version:** d913e19

## What changed and why

Tier: Standard (from the PM proposal; no tier label). A supporting issue run alongside #11 while #11 waits for outside answers (delivery-pace ruling, 2026-11-12). Ponytail trial: not a control issue. Epoch: the human's call (see Decisions); the orchestrator recommends no move.

- `agent-kit.conf`: `frontend/package.json`, `frontend/bun.lock` and `frontend/bunfig.toml` added to `PROTECTED`, so a commit that changes them is refused without `HUMAN_APPROVED=1`. Committed by the orchestrator with `HUMAN_APPROVED=1` after the human approved the exact diff in this session.
- First issue under the delivery-pace rules: CI was the test loop (run 43161409665: `bun install --frozen-lockfile`, 121 Python and 154 frontend tests, VERIFY: PASS), and the refused and allowed cases were proved in throwaway worktrees under `.scratch/` by running `.githooks/pre-commit` directly (hooks are not installed in Kiro Web). No human hand-over.
- One PR for the issue: this summary is on the issue branch.
- Alongside, in the same session: #12, #13 and #14 checked ahead and re-groomed with the human's rulings (Confirms and PM re-records posted); #86 filed and groomed (the ingest limits in the contract, before #14); the spec's Phase 2 outline gains login attempt limiting and ingest rate limiting (PR #87); the Deploy roadmap drafted (provisional, PR #87); the epoch batch drafts recorded (PR #84, merged) with item 8 added; the delivery-pace rulings (PR #85).

**What I learned:** CI as the test loop and a throwaway worktree for hook checks took this issue from claim to QA PASS with no human run.

## Reflection

### PM

unknown (role not asked)

### Engineer

From comment 6815583961, unchanged:

Reflection:
(1) Slowed down: proving the hook without installed hooks. I had to write a throwaway-worktree script that runs the pre-commit file directly, with baseline, refused, allowed and unprotected passes (see the prove script in the scratch folder), and the draft had to be rewritten after the approval and CI results arrived.
(2) Nearly went wrong or was blocked: the protected-file rule meant I could not edit the config myself, and the hooks do not run here, so the real hook path was never exercised. I only avoided touching the branch by using a worktree that I removed afterwards.
(3) Proposed change: `_docs/agent-kit/procedures/verify.md` should say that a protected-file hook change is proved by running the pre-commit file in a throwaway worktree, with a ready-made make target for it. Expected effect: no custom proof script per issue. Measured by counting scratch scripts written and turns spent proving hook changes on the next two such issues.

### QA

From comment 6815614727, unchanged:

Reflection:
(1) Slowed down: the second amendment's text was not in the protocol file on this branch, so my first two searches found nothing; I only found it by listing branches and reading the amendment branch's copy. Also the diff against the claim's base printed far more than the real change.
(2) Nearly went wrong: the base in the claim comment was not the commit's parent, so a naive review of the base-to-head diff would have treated the epoch drafts as part of this change; and the human-commit criterion cannot be verified from git alone.
(3) Proposed change: `_docs/agent-kit/team/qa-engineer.md` should say to diff against the commit's parent (`git diff <head>^ <head>`) and to state the parent when it differs from the claimed base. Expected effect: fewer reads of unrelated diffs. Measured by counting QA diff reads that print files outside the Constraints over the next few issues.

Orchestrator's note on QA's point (1): Amendment 2 is in `_docs/planning/ponytail-trial-protocol.md` on this branch and on `main` (its commit is an ancestor of the branch); QA's search missed it. Its epoch answer still stands on the amendment's text.

## Launch usage

Active time and tool uses: unknown (Kiro Web gives neither). Engineer 2 (diff and proof; comments). QA 1 (PASS). Handovers: none.

## Files created or modified

`agent-kit.conf` (one line). This file.

## Decisions made by the human

- The exact `PROTECTED` diff, committed by the orchestrator with `HUMAN_APPROVED=1` (the issue said the human commits it; the human approved this route with "recommendations approved").
- Epoch effect: pending. QA called it borderline: an Engineer on an unrelated issue who changes a frontend dependency file is now refused without approval. The orchestrator's view: no move, because `AGENTS.md` already required asking before adding a dependency; this enforces an existing rule rather than adding one.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify` (CI run 43161409665: VERIFY: PASS).

## Proposed AGENTS.md changes

none.

## Temporary changes

- Two throwaway worktrees under `.scratch/` (the Engineer's and QA's), each removed with its branch; `git worktree list` shows only the main checkout.
- `make clean-scratch`: NOT run; housekeeping is on hold.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The orchestrator's claim comment named the branch base as `2c77a6f`; the branch was cut after PR #84 merged, so the base is `bdc8f7e`. QA found it; the diff of the issue itself is one line.

## Follow-ups for the next session

- #11 waits for the outside answers on its data-model rules; #12 to #14 and #86 are ready (approved or groomed).
- Decide the epoch question for #60.
