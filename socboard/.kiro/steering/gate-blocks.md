---
inclusion: always
---

# When a script blocks on mechanics, not substance

Applies to the orchestrator in this repository.

When a script or gate (for example `make issue-close`, a hook, a format check) refuses because of how something was recorded rather than because the work is missing or wrong:

1. Say plainly that the work itself is done, and name the evidence (the comment links, the commit). Do not word it as if the work is missing.
2. Explain the mechanical cause in one or two sentences (for example "the script reads only the comment's first line, which must start `QA: PASS`").
3. Give the human the options before acting, including closing or proceeding by hand with an explanatory comment, and a recommendation.
4. Wait for the human's choice. Do not launch an extra role round just to satisfy the script unless the human picks that option.

Reason: on #9 two valid QA PASS comments had the wrong first line, and an extra QA round was launched without asking; the human could have closed the issue by hand with an explanation.

Also: in launch messages, keep each role's required output format (for QA, a first line starting exactly `QA: PASS` or `QA: FAIL`); do not ask a role for a heading that replaces it.

Also: before `make clean-scratch`, list `.scratch/` and copy or commit anything a person has still to see (a PM draft, a sweep entry, a task file). The command deletes everything in it, including drafts that exist nowhere else (sweep 6, proposal 7; the PM's grooming drafts for #115, #112 and #122 were nearly lost on 2026-11-13).
