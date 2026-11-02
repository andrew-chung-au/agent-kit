# Issue #37: Tiers, part 2: Heavy tier gates, QA code-review checklist and dry runs (Phase 3b)

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-02T15:20Z (UTC)
**Spec version:** none

## What changed and why

The Heavy tier now has its gates, and QA has a code-review checklist. Built by the Kiro cloud session on branch `issue-037-heavy-tier`, commit 590833a (one commit on f4621a4; committed with `HUMAN_APPROVED=1` after the human approved the exact diff). Merged into the sandbox `main` by the human as a merge commit. Files: `agent-kit/process.md` (a "Heavy gates" block: an ADR in a `## Decision record` section of the issue body, approved by the human before the Engineer starts and covered by the recorded body hash; a second, fresh QA launch limited to the code-review checklist, with Assert clean after it; Heavy is done only when both launches PASS; no agent lowers the tier), `agent-kit/team/qa-engineer.md` (a `## Code review` section and a verdict-layout block), `agent-kit/team/pm.md` (the ADR drafting line), `agent-kit/blueprints.md`, `tests/test_heavy_gates.py` (new).

QA PASS at 590833a on a copy merged with `main`: every gate and checklist criterion met with evidence; 12 mutations of the pinned wording in `process.md`, `qa-engineer.md`, `pm.md` and `blueprints.md` each made a test in `tests/test_heavy_gates.py` fail (24 tests OK unmutated, including `test_approval_freeze`); changed paths are the five expected ones; no script, hook or tool-setting change; the Engineer applied exactly the PM's stated defaults. After the merge, `make verify` in the sandbox: 427 tests OK, claims check OK, no whitespace errors, 83 assertion lines added across the merged work and none removed.

**Closed for the gates only.** The four criteria under "Dry runs and measurements" are not done: the Light and Standard dry runs, the comparison with #25 and #27, the always-loaded and total word report against the 15% growth metric, and the dry-run "never skip labelling" refused case (untested because no dry run happened). The issue's own default was to wait for Phase 2 (#20 and #36) for the permission-log prompt counts, so they were deliberately left out and QA did not fail the issue. The human decided on 2026-11-02 to split: those four criteria moved to **#56** (unlabelled, Standard, depends on #20 and #36). #37's body is unchanged (it is approved and frozen).

Word counts (`wc -w`, branch against f4621a4): `process.md` 2706 to 2954 (+248, the issue expected about +250), `qa-engineer.md` 505 to 675, `pm.md` 734 to 764, `blueprints.md` 2493 to 2507. On the merged copy `process.md` is 3042 and `blueprints.md` 2538 because `main` moved since. The always-loaded total and the 15% growth figure were not computed (that is #56).

Not verified: the second-launch and ADR-hash rules are process text only (the tests pin wording, not behaviour); GitHub CI for the merged result.

**What I learned:** an approved issue with measurement criteria that depend on a later phase should be split when it is groomed, not at close time; the gates were done and checked while four criteria could not be met until #36.

## Reflection

### Engineer

unknown (the Kiro cloud session built this; its role was not asked)

### QA

1. Slowed down: the issue is a 31 KB pile (body plus three long PM and Orchestrator comments that correct the body), so working out which criteria were still live took longer than the checks. Merging a branch cut before `main` moved meant word counts differed between the Engineer's figures and the merged copy, and I had to compute both.
2. Nearly went wrong: I wrote my verdict comment with an abbreviated body hash that I had mistyped (ended b736 instead of b717). I caught it by re-reading before posting and fixed it with a one-off script. Also a "restored" sanity run failed on `python -m unittest tests.test_tier_check` alone (an import error when run by name); the full `make verify` had passed, so it was not a real failure.
3. Proposal: `agent-kit/team/qa-engineer.md`, add one line to the verdict layout instructions: "Quote hashes in full or copy them from the command output; never retype them." Measure: at each sweep, compare every hash in QA comments against `make issue-hash` output (target zero mismatches across the next ten verdicts).

### PM

unknown (the PM's grooming ran in earlier sessions; role not asked)

## Launch usage

- QA (check #37 at 590833a, PASS): 102.0 s, 21 tool uses
- QA (reflection, resumed): not reported separately
- PM (file the #56 follow-up): 46.5 s, 12 tool uses
- Engineer: the Kiro cloud session (not measured here)
- Also this session: trial merge and full `make verify` on the branch by the orchestrator before QA (407 tests, PASS), and again after the merge (427 tests).

## Files created or modified

- `agent-kit/process.md`, `agent-kit/team/qa-engineer.md`, `agent-kit/team/pm.md`, `agent-kit/blueprints.md`, `tests/test_heavy_gates.py` (commit 590833a, merged)
- This summary.

## Decisions made by the human

- Handed #37 to the cloud session and approved the exact diff there; merged the branch themselves.
- Split #37: close it for the gates and move the four dry-run criteria to #56.
- Confirmed #37's body stays as it is (no new hash).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- QA's reflection proposal above is for the human; none applied.
- If #44 or other issues that edit `process.md` and `blueprints.md` land later, they need a rebase over these changes.

## Follow-ups for the next session

- **#56** (unlabelled): the dry runs and word report, after #20 and #36.
- Push from the clean clone; GitHub CI on `main` is the remaining check of the #13 and #37 merges.
- The cloud branches for #42, #43, #41 and #31, and #44 once its revised body hash is confirmed; #2 waits for #9.
