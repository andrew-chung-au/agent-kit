# Current status

**Date:** 2026-11-04T11:59Z (UTC), after QA PASS on #117 and #145 filed.
Built from issue comments and gh output at that time; not re-run since. Rewritten in place on each change; the Date line says how fresh it is.

## Needs you
1. Merge PR #139 (#117): QA PASS at head `3185893`. It is behind `main` (main has #138 and #144), so merge `main` into the branch or let GitHub do it; QA found no conflict in the files touched.
2. #117 has no tier label, so the close gate needs 1 PASS (met). The body says proposed Heavy; add `tier:heavy` only if you want two PASSes required (also met: 08:07 and the new one, both at `3185893`).
3. After #139 merges: I run one recheck on #140 (#118), which will need a rebase onto the new `main`.
4. Retarget PR #137 (#115) to main before any merge. It has a QA FAIL; hand the Engineer fixes to Kiro if wanted.
5. README issue #145 (unlabelled): decide scope, install path and sequencing (recommended: both READMEs, two install paths, work it after #115/#117/#118 merge). Version cut stays a separate step.
6. #18: defaults stand unless you say otherwise; label `approved` when you want it started.
7. Local `main` here holds docs commits not pushed (`43fdcfb`, `ab50008`, `2c16478`, `daf635e`, `54b41a3`, plus this update) and is behind `origin/main`. Bring them over from the clean clone when convenient.
8. Later: version bump and changelog lines.

## Issues
| Issue | PR / base | QA | Blocked by | Next |
|---|---|---|---|---|
| #117 | #139, main, head `3185893` | PASS 08:07 and PASS 11:5x (both at head) | merge | you: merge; me: Close comment after |
| #118 | #140, main, head `8b9b3c6` | FAIL 03:12 (README points at #139's section) | #139 merge | me: recheck after #139 |
| #115 | #137, stale base, head `49f0999` | FAIL 06:56 (Heavy); fix list posted | fixes, retarget | Kiro fixes, then QA |
| #145 | none | not started | unlabelled; sequencing | you: decisions, label |
| #143 | none | not started | none | me: Engineer starts (on your word) |
| #142 | none | not started | trim its #18 text | PM trim, then Engineer |
| #18 | none | not started | unlabelled | you: label |
| #141 | none | no QA | unlabelled | your call to approve |
| #31 | merged | failed after merge | follow-up is #143 | waits on #143 |

Done today: #71 closed, #116 closed (on main via #144, merge `0e74efe`).
Not tracked here: #91, #90, #56, #20.
