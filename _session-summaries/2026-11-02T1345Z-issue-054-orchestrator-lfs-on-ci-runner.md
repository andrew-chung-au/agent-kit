# Issue #54: Pre-push hook tests find a real git-lfs on the CI runner and fail the root-commit test

**Tier:** Standard (proposed by the PM; no tier label was set)
**Date:** 2026-11-02T13:45Z (UTC)
**Spec version:** none

## What changed and why

After the human's push went through (`origin/main` at f4621a4), GitHub CI (`make verify`) failed on `main` (run 41442100861) and on the cloud session's #50 branch (run 41451507615) with one test: `tests/test_gate_pre_push.py` `PrePushTest.test_a_root_commit_takes_the_empty_tree_as_base` ("Invalid remote name "origin""). Cause (diagnosed by the orchestrator, verified by the PM, the Engineer and QA): the hook's last step runs `git lfs pre-push "$@"` when git-lfs is on PATH. The GitHub runner has git-lfs; this sandbox does not, so the suite passed here. The test's `fresh` repo has no `origin` remote, so git-lfs rejects the name. Every other test uses the setUp repo, which has an `origin`. Same class as #51: the sandbox and the CI environment differ.

The failure is not caused by #50; it was already on `main`.

Fix, commit 82c0523 (one file, `tests/test_gate_pre_push.py`, unprotected, committed by the Engineer; option 3 of the PM's three, assumed from the PM's stated default after the human labelled the issue, recorded in the Engineer comment): `hook()` now defaults `PATH` to `self.no_lfs_path()` (tests that pass their own PATH still override it), the direct `run_cmd` call in the root-commit test passes `no_lfs_path()`, and the file docstring was updated. `make verify` passed (372 tests).

QA PASS at 82c0523, on tree copies under `.scratch/` with a stub `git-lfs` that fails on an unknown remote placed first on the PATH of `make test`:
- fixed tree: exit 0, 372 tests OK, stub called 0 times;
- root-commit PATH reverted: exit 2, only that test fails, stub called once (the CI failure);
- `hook()` default removed: suite stays green but the stub is called 10 times, so the default is what closes the other exposed calls;
- default forced over a test's own PATH: the two lfs-stub tests fail, so overrides work and are tested.
`make assert-clean` passed afterwards (HEAD 82c0523).

Not verified: CI on GitHub (the human confirms after pushing from the clean clone). The stub models CI's remote-name failure, not real git-lfs.

Found outside the criteria: the Engineer's audit named only `agent-kit/githooks/pre-push`; `agent-kit/githooks/lfs-passthrough` also calls `git lfs`. No test executes it today, so it is harmless, but a future test of the post-* hooks would need the same git-lfs-free PATH.

**What I learned:** twice in one session (#51, #54) the suite passed in the sandbox and failed in the push check or CI, because the sandbox has no Docker and no git-lfs. A test that runs a hook or script reaching an optional external tool must give itself a PATH that cannot find the tool.

## Reflection

### Engineer

1. Slowed down: the audit of other tests. I grepped each hook test by hand to learn which hooks call git-lfs, because nothing in the kit lists which hooks reach external tools. The stub reproduction needed a `.scratch/` script (the command-shape rules rule out inline code), run twice.
2. Nearly went wrong: the negative check had to revert only one line. Reverting the `hook()` default as well would have failed for the wrong reason. I also nearly missed that the `run_cmd` call bypasses `hook()`, so the default alone would not have fixed the failing test.
3. Proposal: `agent-kit/team/software-engineer.md`, under "Write tests": when a test runs a hook or script that calls an optional external tool, give the test a PATH that cannot find it by default, and add a stubbed-tool run as the check. Effect: fewer "passes in the sandbox, fails in CI" issues. Measure: count such issues over the next ten (target zero).

### QA

1. Slowed down: the stub check needed a script that copies the tree, applies four mutations, asserts each changed its target and runs `make test` four times (about 18 s each); the Engineer's script covered only the unmutated run. Finding every `git lfs` call took several greps because the Engineer's audit missed `lfs-passthrough`.
2. Nearly went wrong: the "revert the `hook()` default" mutation passed the whole suite, which could have been read as "not needed". Only the stub call count (10 against 0) showed the exposure was real; I almost judged by exit code alone.
3. Proposal: `agent-kit/team/qa-engineer.md`, add a bullet: when a criterion is an environment-difference reproduction (stub, missing tool, different PATH), also assert a side-effect counter (calls to the stub), not only the exit code, for both the fixed and the mutated copy. Measure: later QA comments for such issues state a call count (target: every one).

### PM

1. Slowed down: working out which tests share the exposure meant reading the whole test file and `kit_repo.py`'s `run_cmd`, since nothing says which helpers build the environment. `make issue-hash` printed "Recorded sha256: none", which looked like a failure until I read the first line.
2. Nearly went wrong: I fixed a sentence in the body file with Edit in the same tool block as `gh issue create`; in the other order the issue would have been filed with the unfixed text and a hash for a different body. I only knew it was right because I re-read the live body.
3. Proposal: `agent-kit/team/pm.md`, under the line about recording the body hash: "Finish the body file before `gh issue create`, never in the same batch of calls; after filing, confirm the live body is the intended text, then run `make issue-hash` and record that value." Measure: over the next 10 groomed issues compare each grooming comment's hash with `make issue-hash` at approval time (target zero mismatches caused by filing order).

## Launch usage

- PM (file and groom #54): 50.1 s, 16 tool uses
- Engineer (implement #54): 132.1 s, 25 tool uses
- QA (check #54 at 82c0523, PASS): 147.7 s, 19 tool uses
- Engineer (reflection, resumed): 14.5 s, 3 tool uses
- QA (reflection, resumed): 169.9 s, 22 tool uses (as reported; may include the earlier run)
- PM (reflection, resumed): not reported separately
- Also this session, not tied to an issue: an Engineer launched on #50 stopped after 37.0 s, 8 tool uses, and changed nothing, because #50 had already been built and QA'd by the cloud session on `origin/issue-050-human-task-files` (a branch this checkout did not have).

## Files created or modified

- `tests/test_gate_pre_push.py`
- This summary.

## Decisions made by the human

- Labelled #54 `approved` after seeing the PM's three options and its recommended default (option 3); option 3 is assumed, not named.
- Asked for as many issues as possible to be handed to the cloud agent on branches (claims posted on #13, #44, #37 and #2; see the follow-ups).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

The CI failure interrupted the order (#50 first): #54 was filed and fixed before #50 and #13. #50 turned out to have been built by the cloud session; the sandbox Engineer launched on it stopped at once and changed nothing.

## Unrelated problems noticed but not fixed

- `agent-kit/githooks/lfs-passthrough` calls `git lfs` and is not covered by the no-git-lfs PATH default; harmless until a test runs the post-* hooks.
- `tests/test_tier_check.py` hangs in the cloud sandbox (reported by the cloud session's QA on #50), so `make verify` was never run end to end there.
- Reflection proposals from #54 (above) are for the human; none applied.
- Handover note and my memory note are slightly stale: they say #50 is waiting for an Engineer, but the cloud session built it.

## Follow-ups for the next session

- **Push:** from the clean clone, `git fetch sandbox`, review, `git merge --ff-only sandbox/main`, `git push`, and watch CI (verify must go green; this is the real check of #54). If it fails, send the output.
- **#50:** built and QA-passed by the cloud session on `origin/issue-050-human-task-files` (9d3c07f, summary 5090ea4). Fast-forward it into the sandbox `main` (the human's decision), re-run `make verify` here (the cloud could not), check its summary, ask for reflections if missing, then close #50.
- **Cloud handover (claims posted):** #13 on `issue-013-issue-dump`, #44 on `issue-044-github-wrappers` (after #13), #37 on `issue-037-heavy-tier`, #2 on `issue-002-root-readme` (assumed "start now with clone-and-copy"; the human to confirm). The orchestrator does not start sandbox Engineers on them while the claims stand; fetch finished branches, re-run `make verify`, QA, reflections, summary, close.
- **Parked as human tasks:** #20 and #36 (need a live OpenCode), the two unrun #47 spot checks, the possible token rotation from #51.
- Backlog-review decisions still unanswered (see the handover).
