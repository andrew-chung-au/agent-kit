# Current status

**Date:** 2026-11-04T13:35Z (UTC), after #115 and #118 close records and PR #146 merged (13:20Z).
Built from issue comments and gh output at that time; not re-run since. Rewritten in place on each change; the Date line says how fresh it is.

## Needs you
1. PR #147 (#145, README rewrite) is in QA. When it passes, merge it. Cutting 1.10 (fold "Unreleased" into "Changes in 1.10", bump the version, approve the changelog) is a separate step after it.
2. Decide the open items: #18 (label `approved` when you want it started; defaults stand), #143 (approved, not started: start the Engineer?), #142 (approved, not started), #141 (unlabelled).
3. Local `main` here holds docs commits not pushed (the #115 and #118 summaries and this update, on top of the last push `06ce9a9`). Bring them over from the clean clone when convenient; local `main` is also behind `origin/main` (PR #146 and later).
4. Later: version bump and changelog lines.

## Issues
| Issue | PR / base | QA | Blocked by | Next |
|---|---|---|---|---|
| #145 | #147, main, head `2b73ff5` | running | QA | you: merge after PASS; me: summary and Close comment |
| #143 | none | not started | none | on your word: Engineer starts |
| #142 | none | not started | trim its #18 text | PM trim, then Engineer |
| #18 | none | not started | unlabelled | you: label |
| #141 | none | no QA | unlabelled | your call to approve |
| #31 | merged | failed after merge | follow-up is #143 | waits on #143 |

Done today: #71, #116, #117 (auto-closed), #118 (auto-closed, close record posted), #115 closed (on main via PR #146, merge `109dc22`).
Not tracked here: #91, #90, #56, #20.
