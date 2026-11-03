# Issue #42: Read changed names NUL-delimited in githooks/pre-push and verify_on_stop.py (follow-up to #1)

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-03T11:00Z (UTC)
**Spec version:** none

## What changed and why

Two reads of changed file names that #1 had not fixed now use NUL-delimited git output, so a name git would quote (non-ASCII, a double quote, a backslash, a tab) is read as the real path. The defect was real and silent: with a subfolder project, a push whose only change had such a name exited 0 and skipped `make verify`, so the push went through unverified.

Commit 087e945 (committed by the human with `HUMAN_APPROVED=1` after reading the exact diff): `agent-kit/githooks/pre-push` (`git diff --name-only --no-renames -z` with `read -r -d ''`; `agent-kit-hooks-version` 2 to 3, one bump), `agent-kit/claude-code/hooks/verify_on_stop.py` (`-z` on both `git diff --name-only` and `git ls-files --others`, split on NUL), and two new test files, `tests/test_gate_pre_push_names.py` and `tests/test_verify_on_stop_names.py`. A second human commit, 9e760fa, installed `.githooks/pre-push` (version 3) and `.githooks/pre-commit` (version 4) after the Engineer ran `make hooks`; the pre-commit copy had been stale at version 3, which is unrelated drift.

The work was first given to an OpenCode Engineer, which stalled on its usage limit after reading files and changed nothing; a Claude Code Engineer then did it from the same brief. The cloud session's claim on #42 had been released first.

QA PASS at 087e945. QA ran the pre-change hook (`git show 087e945^:agent-kit/githooks/pre-push`) in throwaway repos: for a subfolder project it skipped verify (0 calls, exit 0) for non-ASCII, double quote, backslash, emoji and tab names; the new hook ran verify exactly once for all 11 names tried, including 6 the tests do not list; a root plus subfolder push ran both; a failing verify blocked. For `verify_on_stop.py` with a stub make target: a Markdown-only change with an unusual name gave 0 calls, a non-Markdown change 1, an edit after a pass 2. Seven mutations (drop `-z` in pre-push, drop `-d ''`, version 3 back to 2, drop `-z` from either Stop-hook read, split on newline for both or for untracked only) were each killed by the shipped tests. The installed `.githooks` copies equal the kit copies. `make verify` (sandbox, also before commit): 438 tests OK, no whitespace errors, 27 assertion lines added and none removed. `make assert-clean` passed after QA.

Not verified: a real `git push` (QA fed the refs to the hook on stdin); the Docker push check on the human's machine and `agent-kit/environments/local-sandbox/pre-push`; GitHub CI; the Engineer's claim of 20 failures before the fix was not rerun at the old commit (the old-hook and mutant runs show the same failures).

Live effect: `agent-kit/claude-code/hooks/` runs live from the working tree, so the Stop-hook edit changed Claude Code's Stop hook for this repo as soon as it was saved; `agent-kit/githooks/` takes effect only after `make hooks`.

**What I learned:** a hook that exits 0 with no output looks like a pass when it has skipped its work; count the side effect (the stub's recorded calls), not the exit code. And `make hooks` run by an Engineer to test a hook rewrites tracked, protected `.githooks/` copies, which then need their own approved commit.

## Reflection

### Engineer

1. Slowed down: `tests/kit_repo.py` has no helper for a stub-Makefile project or for running a Stop hook; I wrote both inside the new test files. The pre-push test reuses `no_lfs_path` by assigning a method from another test class.
2. Nearly went wrong: the Stop-hook test would have created `.scratch/` inside the throwaway repo as untracked files, so every run would look like a non-Markdown change and hide the Markdown-skip result; I added a `.gitignore` to the test repo. Also `make hooks` silently updated the tracked `.githooks/pre-commit`, outside the issue's paths.
3. Proposal: add a `stub_verify_project(subdir)` helper and a `run_stop_hook()` helper to `tests/kit_repo.py`, and move `no_lfs_path` into it from `tests/test_gate_pre_push.py`. Effect: new hook tests need no copied setup. Measure: lines of setup in the two new test files (about 40 now), and whether the tests for #43 and #40 add none.

### QA

1. Slowed down: the mutation checks had no shared harness. The tests import `REPO` from their own file location, so each mutant needed a full copy of `tests/` and `agent-kit/`, and I wrote a one-off script to build, mutate and run them. The behaviour script rebuilt isolated git config, identity and a git-lfs-free PATH by hand, although `tests/kit_repo.py` already does this.
2. Nearly went wrong: an unusual-named file that the old hook silently skipped can look like a pass, because the old hook exits 0 with no output. I counted verify calls from a stub record file instead of trusting the exit code, and asserted that each mutation changed its target.
3. Proposal: `agent-kit/team/qa-engineer.md`, add one line under the checks: "For a fix that changes how a script reads input, copy the script's tests and sources under `.scratch/`, apply each mutation to the copy, assert it changed the text, and run the shipped tests against it; reuse `tests/kit_repo.py` for the isolated repo, git config and PATH." Measure: QA scripts written under `.scratch/` per issue with a mutation request (target one reusable script), and whether the QA comment lists each mutant as killed or survived.

### PM

unknown (the PM's grooming ran in earlier sessions; role not asked)

## Launch usage

- Engineer (OpenCode, stalled on its usage limit, changed nothing): not measured
- Engineer (implement #42, Claude Code): 296.8 s, 28 tool uses
- Engineer (reflection, resumed): not reported separately
- QA (check #42 at 087e945, PASS): 155.9 s, 30 tool uses
- QA (reflection, resumed): not reported separately

## Files created or modified

- `agent-kit/githooks/pre-push`, `agent-kit/claude-code/hooks/verify_on_stop.py`, `tests/test_gate_pre_push_names.py`, `tests/test_verify_on_stop_names.py` (commit 087e945)
- `.githooks/pre-commit`, `.githooks/pre-push` (commit 9e760fa, from `make hooks`)
- This summary.

## Decisions made by the human

- Labelled #42 `approved`; released from the cloud claim so it could be worked here.
- Approved and committed both protected commits (087e945 and 9e760fa).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

The OpenCode Engineer stalled on its usage limit; the Claude Code Engineer continued. The human upgraded OpenCode from 1.19.5 to 2.2.5 during this issue; none of #42 depends on it, but the recorded OpenCode results and #20's stage 1 were all for 1.19.x (see the follow-ups).

## Unrelated problems noticed but not fixed

- `agent-kit/scripts/verify.sh:29` still uses a plain `git ls-files --others` (it only prints a warning; the issue lists it as out of scope).
- The tracked `.githooks/pre-commit` had been stale at version 3 until `make hooks` ran (committed as 9e760fa).
- The Engineer's and QA's reflection proposals above are for the human; none applied.

## Follow-ups for the next session

- **#43** (claimed by the cloud session, stacks on this change): it edits the same `agent-kit/githooks/pre-push` and must not bump the hooks version again.
- Push from the clean clone and watch the push check on the human's machine: it is the real test of the pre-push change.
- The human decides the kit version bump and changelog.
- OpenCode 2.2.5: re-run the by-hand task file, re-check #20 stage 1, and have the PM file a check of the kit's OpenCode layer if the human wants it.
