# Sweep 4 candidates

Proposals collected from role Reflections and QA findings since sweep 3, waiting for the next sweep (`_docs/agent-kit/procedures/sweep.md`). Nothing here is approved: the sweep's PM weighs each against the evidence and the human rules. Kit files are protected and on the ponytail epoch list, so an approved change joins an epoch batch.

| # | Proposal | File it would touch | Source (evidence) |
|---|---|---|---|
| 1 | The Heavy second QA launch must start in a new session, and its comment states that it did (a resumed or reused session is not independent and is discarded). | `_docs/agent-kit/team/qa-engineer.md` (Code review) | #11: the second launch re-run in the same Claude Code session that wrote the previous review; disclosed in https://github.com/andrew-chung-au/socboard/issues/11#issuecomment-6822062758 (its Reflection, item 3) |
| 2 | Diff the file list and the weakened-test check against `git merge-base BASE HEAD`, not `BASE`, so the list shows only the branch's own changes after `main` moves. | `_docs/agent-kit/scripts/verify.sh` | #11 second-launch Reflections (both); overlaps #65 |
| 3 | When a check cannot run in the role's environment, the Engineer drafts the human-task file for it at the start, listing each unconfirmed guess. | `_docs/agent-kit/procedures/verify.md` or `environments.md` | #62 and #74 Engineer Reflections |
| 4 | When tests cannot run in the sandbox, QA may ask for one throwaway CI run of the reverted fix, so "the new test catches the bug" is proven, not reasoned. | `_docs/agent-kit/team/qa-engineer.md` | #62 QA Reflection |
| 5 | QA reads CI logs through a script that prints only the result lines, and reads the issue from the dumped JSON, not `gh issue view` (which fails in Kiro Web). | `_docs/agent-kit/team/qa-engineer.md` | #86 QA Reflection |
| 6 | A make target that writes an issue's comments to `.scratch/`, one section per comment, so long issues are not truncated. | `Makefile`, kit template | #10 and #11 QA Reflections; related to #73 |
| 7 | For each refused test, QA names what it builds its inputs from (contract, app or hand-made), so tests that guard only a helper are labelled. | `_docs/agent-kit/team/qa-engineer.md` | #74 QA Reflection |
| 8 | A make target or procedure for proving a protected-file hook change in a throwaway worktree. | `_docs/agent-kit/procedures/verify.md` | #60 Engineer Reflection |

Already queued elsewhere (not repeated here): wiring `make contract-check` into verify (epoch batch 1, item 6); the Engineer's running notes draft (#10 Engineer Reflection) is close to batch item 1.
