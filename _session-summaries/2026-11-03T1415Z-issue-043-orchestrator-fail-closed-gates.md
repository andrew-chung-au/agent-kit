# Issue #43: Fix fail-open defects in assert-clean.sh and githooks/pre-push

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-03T14:15Z (UTC)
**Spec version:** none

## What changed and why

Two gates could report success when git itself failed: `assert-clean.sh` printed `ASSERT-CLEAN: PASS` even when `git status` or `git rev-parse --short HEAD` failed (a non-repo, an unreadable HEAD), and the pre-push hook treated a failed git call or a malformed pushed sha as "nothing to verify" and let the push through. Both now fail closed. Built by the Kiro cloud session on branch `issue-043-fail-open-defects`, commit dff2ad1 (one commit on `main` f782a41 after #42; pull request #62; committed with `HUMAN_APPROVED=1` after the human approved the exact diff, per the Engineer's comment). Merged into the sandbox `main` by the human as 03f911f.

Changes: `agent-kit/scripts/assert-clean.sh` captures the exit code of `git status` and fails (exit 1, a reason) when it fails, and when `rev-parse --short HEAD` fails or is empty; a repository with no commits fails closed (the decision the issue asked to be stated, covered by a test). `agent-kit/githooks/pre-push` checks every git call that decides the outcome (`rev-parse --show-toplevel`, `hash-object`, `rev-list`, `diff`, `rev-parse HEAD`, `status`), names the push ref and step on failure, and sets the failure flag; a pushed local sha must be 40 or 64 hex digits and a commit (`git cat-file -e`), checked as plain hex first so `--stat`, `-h` and `--output=...` never reach git as options; "nothing new to push" still passes, and an unknown or option-like remote sha still falls through to a normal verify. Tests: `tests/test_gate_assert_clean.py` (+7), `tests/test_gate_pre_push.py` (+10 methods), and a new shared helper `tests/git_stub.py` (a `git` stub that fails chosen commands by glob; outside the issue's file list, judged justified by QA: test-only, not collected by discovery, and it keeps `tests/kit_repo.py` untouched so there is no conflict with #59).

QA PASS at dff2ad1, comparing the old script (`git show origin/main:<path>`) with the new one: the old `assert-clean.sh` printed PASS and exited 0 for a missing `GIT_DIR`, a non-repo, a failing `git status`, a failing `rev-parse --short HEAD` and an empty repo; the new one exits 1 with `ASSERT-CLEAN: FAIL` and a reason in each, and the clean path still prints PASS with the right HEAD. The old hook exited 0 for `nothex`, forty 1s, short, too-long, 64-hex unknown, tree and blob shas, and `--stat`, `-h` and `--output=<file>` (and the last created the file); the new one exits 1 with a reason and runs no verify, and creates no file. With a stub failing each of `rev-list`, `diff`, `status`, `rev-parse HEAD`, `rev-parse --show-toplevel` and `hash-object`, the new hook exits 1 naming the ref and step; the old exited 0 and even ran verify after a failing `status`. The cases that should still pass do (unknown remote sha verifies, nothing new, empty stdin, branch delete), and #42's NUL-delimited reads are intact (the project `proj b é` still verifies with the right BASE). Mutants (drop any exit-code check, drop `cat-file -e`, treat a failed `rev-list` as nothing new, drop the diff, status, HEAD, toplevel or hash-object checks, don't set the failure flag) were all killed; three survived (the hex check always true, the length check dropped, and the `-z "$head"` half of assert-clean's HEAD check), because `cat-file -e` and the exit-code check overlap them; none changes the verdict.

After merging, in the sandbox: `make verify` with #59, #43 and #44 merged: 580 tests OK, 332 assertion lines added and none removed; the new fail-closed `assert-clean.sh` printed PASS on the real tree (the first real run of it, which is also the script the orchestrator uses to prove QA left the tree unchanged). Earlier, with #59 and #43 merged: 462 tests OK, and QA's two-branch merge of #43 with #59 gave 462 tests.

Live effect: `agent-kit/scripts/assert-clean.sh` runs live from the working tree, so `make assert-clean` and `make verify` use the new script from the merge on. `agent-kit/githooks/pre-push` takes effect only after `make hooks`.

**Hooks version, accepted for now by the human:** `pre-push` stays at version 3 (#42 made it 3), so `install-hooks.sh`, which copies only when the version is greater, will not install #43's fix over a v3 copy. Repos on kit 1.9 are at version 2 and will get both fixes with v3; the sandbox's own `.githooks/pre-push` stays on the old v3 content until the version is bumped, and the human said that is fine for now. A bump to 4 would also need the two tests that pin version 3 edited.

Not verified: a real `git push` through the installed hook, the Docker push check on the human's machine, GitHub CI for the merged result beyond the PR #62 run status. One wording note from QA, no action: assert-clean's "no HEAD commit" message also covers git being unable to read HEAD.

**What I learned:** a gate must treat "the tool failed" as its own outcome; every decisive git call needs its exit status checked, and malformed input must never reach git as an option.

## Reflection

### Engineer

unknown (the Kiro cloud session built this; its role was not asked)

### QA

1. Slowed down: the mutation run executed the two gate test files 15 times in one Python script that printed only at the end, so I polled it about ten times over roughly four minutes, one tool call per poll, because a foreground sleep is blocked and my first Monitor call was rejected (its schema was not loaded). I also spent a round on a flawed check: `.scratch/` sits inside the repository, so my "not a repository" test for assert-clean found the parent repo and printed PASS from both the old and the new script; I redid it with `GIT_CEILING_DIRECTORIES`.
2. Nearly went wrong: I almost reported the non-repo assert-clean case as a failure of the new script (it printed PASS) when the cause was my own setup. I also almost took "mutation killed" as the whole picture: three mutants survived because `cat-file -e` and the exit-code check overlap them; I reported them as gaps. The first two attempts to post my verdict failed on the network; I checked the comment count before retrying, so I did not post twice.
3. Proposal: `agent-kit/team/qa-engineer.md`, add to the checking bullets: "For a 'not a repository' or 'git failed' check, run it under `GIT_CEILING_DIRECTORIES=<scratch dir>`, because `.scratch/` is inside this repository and git finds the parent. For a mutation run, write one line per mutant to a log file as it finishes and wait for the background-task notification instead of polling." Measure: tool calls spent polling a background job (this run about 10, target 0) and non-repo cases that printed PASS from a nested directory (this run 1, target 0).

### PM

unknown (the PM's grooming ran in earlier sessions; role not asked)

## Launch usage

- QA (check #43 at dff2ad1, PASS): 548.5 s, 54 tool uses
- QA (reflection, resumed): 24.9 s, 4 tool uses
- Engineer: the Kiro cloud session (not measured here)
- Also this session: `make verify` and `make assert-clean` by the orchestrator after the merge.

## Files created or modified

- `agent-kit/scripts/assert-clean.sh`, `agent-kit/githooks/pre-push`, `tests/git_stub.py`, `tests/test_gate_assert_clean.py`, `tests/test_gate_pre_push.py` (commit dff2ad1, merged as 03f911f)
- This summary.

## Decisions made by the human

- Labelled #43 `approved`; approved the exact diff on the Kiro side and merged the branch in the sandbox.
- Accepted that the new pre-push content is not installed here until the hooks version is bumped ("this is fine for now").

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
- The three surviving mutants are redundant checks (see above); no action.
- The sandbox's `.githooks/pre-push` is stale against the kit copy until the version is bumped (accepted by the human).

## Follow-ups for the next session

- Bump the pre-push hooks version to 4 when a release is cut, so `make hooks` installs #42 and #43 everywhere; the two tests that pin version 3 need editing with it.
- Push from the clean clone; GitHub CI on `main` and the push check on the human's machine are the remaining checks (PR #62 shows merged after the push).
