# Current status

**Date:** 2026-11-04T11:35Z (UTC), after #138 merged at 11:27Z.
Built from issue comments and gh output at that time; not re-run since. Rewritten in place on each change; the Date line says how fresh it is.

## Needs you
1. #116 is not on main. PR #138 merged into `issue-114-kit-check-installed-map`, already merged to main by #136. Open a PR from that branch into main and merge. Then I post #116's Close comment.
2. Retarget PR #137 (#115) to main before any merge. It also has a QA FAIL.
3. #18 (ad hoc permission review): defaults stand unless you say otherwise (last 7 days; pointer in `permission-log.md` only). Label `approved` when you want it started.
4. Merge #139, then #140 (both target main), after #139's QA.
5. Optional: #71 closing summary is committed locally on main as `43fdcfb`, not pushed.
6. Later: version bump and changelog lines.

## Issues
| Issue | PR / base | QA | Blocked by | Next |
|---|---|---|---|---|
| #116 | #138 merged to stale base (`7f1c1c1`) | PASS x2, last at `e3c7293` | not on main | you: PR to main; me: Close comment |
| #115 | #137, stale base, head `49f0999` | FAIL 06:56 (Heavy); fix list posted | fixes, retarget | me: Engineer fixes, then QA |
| #117 | #139, main, head `3185893` | PASS 08:07 after FAIL 06:18 (Heavy: two PASSes needed) | QA launch 2 | me: launch QA |
| #118 | #140, main, head `8b9b3c6` | FAIL 03:12 (README points at #139's section) | #139 merge | recheck after #139 |
| #143 | none | not started | #116 on main | me: Engineer after #116 lands |
| #142 | none | not started | none; trim its #18 text | me: PM trim, then Engineer |
| #18 | none | not started | unlabelled | you: label |
| #141 | none | no QA | unlabelled | your call to approve |
| #31 | merged | failed after merge | follow-up is #143 | waits on #143 |

Not tracked here: #91, #90, #56, #20.
