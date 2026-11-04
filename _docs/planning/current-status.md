# Current status

**Date:** 2026-11-04T11:48Z (UTC), after PR #144 merged at 11:46Z and #116 closed.
Built from issue comments and gh output at that time; not re-run since. Rewritten in place on each change; the Date line says how fresh it is.

## Needs you
1. Retarget PR #137 (#115) to main before any merge. It also has a QA FAIL, so it waits for fixes anyway.
2. #18 (ad hoc permission review): defaults stand unless you say otherwise (last 7 days; pointer in `permission-log.md` only). Label `approved` when you want it started.
3. Merge #139, then #140 (both target main), after #139's QA launch 2.
4. Local `main` here holds docs commits not pushed (`43fdcfb` #71 summary, `ab50008` first status, `2c16478` #116 summary, `daf635e` index row, plus this status update) and is behind `origin/main`. Bring them over from the clean clone when convenient.
5. Later: version bump and changelog lines.

## Issues
| Issue | PR / base | QA | Blocked by | Next |
|---|---|---|---|---|
| #115 | #137, stale base, head `49f0999` | FAIL 06:56 (Heavy); fix list posted | fixes, retarget | me: Engineer fixes, then QA |
| #117 | #139, main, head `3185893` | PASS 08:07 after FAIL 06:18 (Heavy: two PASSes needed) | QA launch 2 | me: launch QA |
| #118 | #140, main, head `8b9b3c6` | FAIL 03:12 (README points at #139's section) | #139 merge | recheck after #139 |
| #143 | none | not started | none now (#116 is on main) | me: Engineer starts |
| #142 | none | not started | trim its #18 text | me: PM trim, then Engineer |
| #18 | none | not started | unlabelled | you: label |
| #141 | none | no QA | unlabelled | your call to approve |
| #31 | merged | failed after merge | follow-up is #143 | waits on #143 |

Done today: #71 closed, #116 closed (on main via #144, merge `0e74efe`).
Not tracked here: #91, #90, #56, #20.
