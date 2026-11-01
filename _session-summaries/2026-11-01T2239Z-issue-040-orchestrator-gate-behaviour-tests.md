# Issue #40: Behaviour tests for assert-clean.sh and the kit's githooks/pre-push

**Tier:** Standard
**Date:** 2026-11-01T22:39Z (UTC)
**Spec version:** none

## What changed and why

Added behaviour tests for the two gate scripts that had none: `tests/test_gate_assert_clean.py` (9 tests) and `tests/test_gate_pre_push.py` (23 tests), commit 8765f60. Tests only: no script, `tests/kit_repo.py` or protected file changed. `make verify` passed with 316 tests. QA PASS at 8765f60; it ran 13 mutations on scratch copies and the tests caught 12 (the survivor behaves identically with or without the mutated line).

The PM found two fail-open defects while grooming; the human chose option A (keep #40 tests-only, file a follow-up). Follow-up filed as #43, unlabelled, Standard proposed, hash recorded.

**What I learned:** gate scripts that read git output without checking its exit status pass when git fails; the #16 lesson (bad input and failing underlying commands) applies to every script argument.

## Reflection

### Engineer

1. Slowed by: one failed test run (`make test`, 1 of 316) because I guessed the git-lfs stub args; the hook calls `git lfs pre-push origin <url>`, so the record starts `pre-push`, as the failure output showed.
2. Nearly went wrong: the orchestrator's #16 and #39 session summaries were already staged, so a plain `git commit` would have swept them into my commit; I used a pathspec commit (`git commit -- <two paths>`) and checked with `git log --stat`.
3. Proposal: `agent-kit/team/software-engineer.md` (Commits): add "If other paths are already staged, commit with a pathspec (`git commit -- <paths>`) and check `git log --stat -1`." Effect: no unrelated staged files in Engineer commits. Measure: count Engineer commits whose `--stat` lists paths outside the issue's expected paths, over the next ten issues.

### QA

1. Slowed by my first LFS mutation hitting `cd "$root" || exit 1` instead of the LFS line, so it showed a false survivor and needed a second script (`.scratch/qa40-mutate2.sh`); my mutate helper replaces only the first match of a short pattern.
2. Nearly wrong: `make assert-clean` could not serve as proof of "changed nothing", because the tree already holds unrelated uncommitted work (`pm.md`, staged summaries, `proposals/`), so I compared `git status --short` before and after instead.
3. Proposal: add to `agent-kit/team/qa-engineer.md` a line "for a mutation check, match the whole line and assert the mutant differs from the original". Effect: fewer false survivors. Measure: count of QA reruns caused by a bad mutation across the next five QA comments.

### PM

1. Slowed down: rebuilding the case list for #43 from my own `.scratch/pm40-comment.md` and `pm40-probe.sh`, plus reading `.scratch/pm42-body.md` to place the overlap; about 6 reads before writing, because no note links a probe to its follow-up.
2. Nearly went wrong: the hook version line. #42 bumps 2 to 3, so #43 could have bumped it a second time; I wrote one bump per release into #43, but nothing enforces that.
3. Proposed change: `agent-kit/team/pm.md`, add one line: when a groomed issue overlaps an open issue on the same file, name the shared lines and the order in both bodies. Expected effect: fewer double version bumps and merge conflicts. Measure: count issues whose Engineer report mentions an unplanned overlap or second bump, before versus after, over the next five issues.

## Launch usage

- Engineer (implement): active time 159.7 s, 22 tool uses
- QA (check): 120.8 s, 20 tool uses
- PM (file #43): 54.0 s, 15 tool uses
- Engineer (reflection, resumed): 15.5 s, 3 tool uses
- QA (reflection, resumed): 15.8 s, 3 tool uses
- PM (reflection, resumed): 84.2 s, 18 tool uses (as the notification reported it; may include the earlier run)

## Files created or modified

- `tests/test_gate_assert_clean.py` (new)
- `tests/test_gate_pre_push.py` (new)
- This summary.

## Decisions made by the human

- Fail-open defects in `assert-clean.sh` and `githooks/pre-push`: option A (tests-only #40, PM files a follow-up with the fixes). Chosen as recommended.
- Sweep: wait for #32 before proposing the first sweep. Chosen as recommended.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none. `make clean-scratch` was run at the end of the issue.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `make assert-clean` always fails in this tree: `.claude/agents/pm.md` is modified, two session summaries (#16, #39) were staged by an earlier session and not committed, and two `proposals/` files are untracked. QA compared `git status --short` before and after instead.
- The issue's LFS wording is slightly off: the hook runs `git lfs pre-push origin <url>`.

## Follow-ups for the next session

- #43 (unlabelled): fix the two fail-open defects. Recommended order: #42 first, then #43, one version bump.
- The three reflection proposals above are for the human; none applied.
- The #16 and #39 summaries are still staged and uncommitted.
- First sweep waits for #32.
