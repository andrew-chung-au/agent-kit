# Current status

**Date:** 2026-11-04T13:50Z (UTC), after #145 closed and the README wording fix committed.
Built from issue comments and gh output at that time; not re-run since. Rewritten in place on each change; the Date line says how fresh it is.

## Needs you
1. Cut 1.10: fold "Unreleased" into "Changes in 1.10" (add a line for the README rewrite), bump the version line and `KIT_VERSION`, approve the changelog. I can draft the lines without an agent launch.
2. Push from the clean clone: local `main` here is ahead of `origin/main` by the README wording fix (`72747a1`), the #115, #118 and #145 summaries and status updates, plus the merge commits. Bring them over as before.
3. Decide the open items: #18 (label `approved` when you want it started; defaults stand), #143 (approved, not started: start the Engineer?), #142 (approved, not started), #141 (unlabelled).

## Issues
| Issue | PR / base | QA | Blocked by | Next |
|---|---|---|---|---|
| #143 | none | not started | none | on your word: Engineer starts |
| #142 | none | not started | trim its #18 text | PM trim, then Engineer |
| #18 | none | not started | unlabelled | you: label |
| #141 | none | no QA | unlabelled | your call to approve |
| #31 | merged | failed after merge | follow-up is #143 | waits on #143 |

Done today: #71, #116, #117 (auto-closed), #118 (auto-closed, close record posted), #115 (PR #146, merge `109dc22`), #145 (PR #147, merge `7532746`; wording fix `72747a1` unpushed).
No open PRs.
Not tracked here: #91, #90, #56, #20.
