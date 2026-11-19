# Open-issue review against main and the 1.11 proposal (2026-11-19)

26 open issues, checked against `main` at `5fcddf7` and `_docs/planning/kit-1.11/workflow-review.md`. Nothing has been changed on GitHub. Closing as not planned needs the human's approval (backlog review); closing after QA PASS is the orchestrator's.

**Status at end of 2026-11-19:** sections A and B are done (issue #91, issue #31, issue #181 and issue #182 closed after QA PASS; issue #171 waits for the human to confirm the 1.10 zip). Sections C and D wait for the human's approval. Follow-ups filed: issue #192, issue #193.

## A. Done: close

| Issue | State | Action |
|---|---|---|
| issue #91 installed-file map (design) | QA PASS at `83a88e0` (PR #185), on main | Orchestrator closes as completed |
| issue #31 hash manifest and import review | QA PASS at `7c53c54`, on main | Orchestrator closes as completed |
| issue #171 cut 1.10 | Tag `v1.10` exists; README says 1.10 (2026-11-09) | Close as completed after the human confirms the release zip with the manifest was published (no QA comment found) |

## B. Merged without a final QA PASS: re-check, then close

| Issue | State | Action |
|---|---|---|
| issue #181 install and upgrade steps | Last QA: FAIL at `bb0e125`. Fix `fcf5198` merged via PR #189, not re-checked | One QA re-check of `fcf5198` on main (Changed only), then close |
| issue #182 docs structure | Last QA: FAIL at `3240a2b`. Fix `cbf4428` merged via PR #190, not re-checked | One QA re-check of `cbf4428` on main, then close |

## C. Superseded or made obsolete by 1.11

| Issue | Why | Recommendation |
|---|---|---|
| issue #142 session-summary Date line | 1.11 issue 7 replaces session summaries with `make status` (proposal 7.2) | Close as not planned once 1.11 issue 7 is approved. Its one live need, a start time for `make permission-report SINCE=`, moves to issue #18 (see D) |
| issue #26 token figures in the launch-usage line | The launch-usage line goes with the session summary; the open question (what the usage figure means, from which source) is the same investigation as issue #191 | Close as not planned and add one line to issue #191: "also record what the per-launch token figure means" |
| issue #17 parallel issues in worktrees | Replaced by 1.11 issue 11 (delivery lead) and proposal section 10 (Claude Code worktree subagents first, dmux trial later). Its 2026-11-02 direction (cloud sessions) is also stale | Close as superseded by 1.11 issue 11; carry its parallel-safety rules (no dependency link, no shared files, no two protected changes) into issue 11 |
| issue #9 tagged releases with a zip | `agent-kit/releasing.md` (from issue #182) now documents tag, `git archive`, manifest and zip. Two differences: the zip's top folder is `agent-kit`, not `_docs/agent-kit/`, and there's no `gh release create` step | Close as superseded by `releasing.md`, or narrow to "attach the zip to a GitHub release". The prefix question was settled by issue #181/#182 |

## D. Overlap: fold into a 1.11 issue or tie together

| Issue | Overlaps | Recommendation |
|---|---|---|
| issue #15 three Conventions rules (web fetch, `make tool-versions`, say if a scratch script changes anything) | 1.11 issue 9, the core-rules file | Fold the three rules into issue 9's criteria, then close issue #15 |
| issue #33 measure always-loaded context | 1.11 issue 9 changes exactly what is always loaded | Keep, and run it after issue 9 so it measures the new set. Or make its measurement issue 9's acceptance evidence |
| issue #141 filesystem-failure audit | Its third question ("should the process say fix the class, not the spot?") is answered by the 1.11 patchwork guard (issue 3) | Keep the audit; remove the process question from its scope and point to issue 3 |
| issue #56 tier timings and prompt counts | 1.11 adds effort grades and points, which give better data than two dry runs | Regroom after 1.11 issues 1 and 3: measure points and QA rounds per grade instead of tier wall-clock. Low priority |
| issue #18 permission review | Needs a session start time for `SINCE`, which issue #142 was going to provide | Keep; let the human give the range as a date (already its default), with no dependence on the summary |
| issue #52 Kiro Web cloud profile | 1.11 issue 8 adds the environment map and `Runs in:` | Keep; issue 8 should name it as the profile that adds the cloud-agent row |

## E. Independent: keep as they are

- Security: issue #66 (`make --eval` escape), issue #58 (merge commits skip the gate). Both stay high priority; 1.11 doesn't touch them.
- Bugs: issue #188 (uv stub), issue #187 (`issue-comment.sh` loses gh's stderr). Small, worth doing before 1.11.
- Human-only or environment: issue #154 (this repo's `.devcontainer/` sync), issue #90 (merge checklist, now mostly a human tracking issue), issue #10 (Codespaces, needs human testing), issue #12 (the "Where am I?" table is still not in the kit), issue #8 (misplaced kit detection, deferred), issue #6 and issue #3 (reviews of `proposals/helpers.sh` and `proposals/pre-push-v3`).
- Investigation: issue #191.

## F. Housekeeping

- Several issues carry "PM: Planned for release 1.10/1.11" notes that are now wrong (issue #12, issue #9, issue #8). Correct them during the 1.11 filing.
- After C and D, the open backlog goes from 26 to about 17 before the 1.11 issues are added.
