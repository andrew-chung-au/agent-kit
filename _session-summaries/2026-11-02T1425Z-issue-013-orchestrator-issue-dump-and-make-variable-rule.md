# Issue #13: Issue-dump make target, make-variable validation rule and the AGENTS.md Commands slot

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-02T14:25Z (UTC)
**Spec version:** none

## What changed and why

`make issue-dump N=<number>` now writes an issue as JSON to `.scratch/issue-<N>.json`, so agents read an issue with the read tool instead of piping `gh` output through ad hoc scripts. The kit also states a rule for every `make` target that takes a variable: validate it with make functions before it reaches the shell (make pastes variables into shell commands unquoted, and `make *` is allowed without approval). `issue-dump` is the worked example. This is 13a of the issue split; the OpenCode template half became #47.

Built by the Kiro cloud session on branch `issue-013-issue-dump`, commit 802c135 (one commit on f4621a4; committed with `HUMAN_APPROVED=1` after the human approved the exact diff). Merged into the sandbox `main` by the human as f126d39. Files: `Makefile`, `AGENTS.md` (the "Fetch an issue" Commands slot), `agent-kit/templates/Makefile.mk` (target, the rule text, an empty "Project targets" section), `agent-kit/templates/AGENTS.md.template`, `agent-kit/templates/agent-kit.conf.template` (`Makefile` in the `PROTECTED` default), `agent-kit/blueprints.md`, and `tests/test_issue_dump.py` (new).

QA PASS at 802c135 on a copy merged with `main`: the target's behaviour with a stub `gh` for both the repo `Makefile` and the template (valid N writes valid JSON and prints the path; about 26 refused values and a missing N fail with the Usage message before any shell runs; a failing `gh` leaves no file and an existing dump untouched); the rule text, both slots, the blueprints row and the `PROTECTED` default match the issue; the shipped tests killed all 7 mutations (including `$(value N)` to `$(N)`, no whitespace check, no leading-zero check, no length check, no JSON-parse check, no temp-file cleanup). `make verify` after the merge at f126d39: 413 tests OK, claims check OK, no whitespace errors, 59 assertion lines added and none removed. `make assert-clean` passed after QA.

Not verified: `make issue-dump` against the real `gh` and GitHub (QA used a stub); GitHub CI for the merged result (the branch's own CI run failed only on the git-lfs test fixed by #54 after the branch was cut).

Word counts (`wc -w`, before then after): `Makefile.mk` 604 to 823 (+219, about double the +110 expected), `AGENTS.md.template` 904 to 949 (+45), `blueprints.md` 2524 to 2582 (+58), `AGENTS.md` 1428 to 1473 (+45), `agent-kit.conf.template` +1.

Spec note: the criterion that refuses `N=" 1"` cannot hold, because make strips the leading space and `N=" 1"` is exactly `N=1`. It is safe, and the test asserts it.

**What I learned:** a clean merge commit does not run the pre-commit hook, so the `HUMAN_APPROVED=1` gate stayed silent when the human merged this branch's protected files (`Makefile`, `AGENTS.md`, `agent-kit/*`). The merge was legitimate (the diffs were reviewed), but the gate would be just as silent for an unreviewed merge.

## Reflection

### Engineer

unknown (the Kiro cloud session built this; its role was not asked)

### QA

1. Slowed down: my first mutation script used my own refused-value list, and two mutations (`$(value N)` to `$(N)`, dropping the whitespace check) survived it. I wrote a second script that runs the shipped tests against each mutant to learn whether the gap was in my list or in the tests. It was my list. One tool call was wasted on a malformed Write.
2. Nearly went wrong: I could have reported those two survivors as test gaps. A value like `$(touch marker)` expands to nothing under `$(N)` and is refused anyway; only a `$(shell ...)` value or trailing whitespace tells the mutants apart. The side-effect assertions (gh log, file, marker) made the second pass trustworthy.
3. Proposal: `agent-kit/team/qa-engineer.md`, in the line about trying to get around each limit, add: "For a mutation check, run the shipped tests against each mutant first, and use your own script only to probe values the tests do not list; a mutant that survives your script but not the tests is not a test gap." Measure: QA runs where a survivor is later retracted, and QA scripts per issue, over the next five issues that add validation (targets zero and one).

### PM

unknown (the PM's grooming ran in earlier sessions; role not asked)

## Launch usage

- QA (check #13 at 802c135, PASS): 112.4 s, 20 tool uses
- QA (reflection, resumed): 19.2 s, 4 tool uses
- Engineer: the Kiro cloud session (not measured here)
- Also this session, not tied to this issue: the orchestrator ran `make verify` on the branch merged onto `main` in a trial merge before QA (413 tests, PASS), and again at f126d39 after the merge.

## Files created or modified

- `Makefile`, `AGENTS.md`, `agent-kit/templates/Makefile.mk`, `agent-kit/templates/AGENTS.md.template`, `agent-kit/templates/agent-kit.conf.template`, `agent-kit/blueprints.md`, `tests/test_issue_dump.py` (commit 802c135, merged as f126d39)
- This summary.

## Decisions made by the human

- Handed #13 to the cloud session and approved the exact diff there; merged the branch into the sandbox `main` themselves.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none. The "Fetch an issue" slot was added by this issue. `AGENTS.md` still says "your GitHub token is read-only", which no longer matches the stated scopes (issues are writable); a possible small follow-up.

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- **`make issue-hash` still expands `$(shell ...)` in `N`:** its validation uses `$(N)` unquoted, so make expands a crafted value before the check runs. The #13 issue said not to change it here; `issue-dump` uses the safe `$(value N)` form. A follow-up should switch `issue-hash` to the same validation (needs a PM issue and the human's approval).
- **Merge commits bypass the `HUMAN_APPROVED=1` gate:** a clean merge does not run the pre-commit hook. A follow-up should check whether the kit needs a `pre-merge-commit` hook (needs a PM issue).
- `Makefile.mk` grew about twice the expected words.
- QA's reflection proposal above is for the human; none applied.

## Follow-ups for the next session

- Merge `origin/issue-037-heavy-tier` (QA PASS, the human's decision on closing it pending); #44 (stacks on #13, which has now landed); #2 stays unmerged until #9.
- The `issue-hash` validation follow-up and the merge-hook follow-up above, if the human approves filing them.
- Push from the clean clone; GitHub CI on `main` is the remaining check of this merge.
