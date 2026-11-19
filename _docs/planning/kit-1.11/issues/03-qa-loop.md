Title: Grade QA findings by impact, effort and scope and route them by points, with a bounded fix check, a patchwork guard and a findings log

**What is wrong or missing**

QA rounds are the largest cost in the process. In socboard, 57 of 146 issues (39%) had at least one QA FAIL; issue #139 there took eight Engineer rounds and issue #63 four QA runs, with no stopping rule until the human wrote one. Today any failing criterion sends the issue back for a full new QA launch, every re-check re-runs everything, there is no grade that says how bad a finding is or how costly its fix, and nothing stops a fix-the-spot loop. Findings that don't fail have no home except the decision point at the end of the issue, so small related problems are either lost or each get an issue.

**What you expected**

The QA loop of proposal 3.5 with the points routing of 4.4, using the vocabulary of 4.0 (in `customizing.md` from issue 01a), all controlled by the settings from issue 01a.

Filed as two issues (split approved by the human on 2026-11-19): 03a (C1 to C7) and 03b (C8 to C11), see the end of this section.

Plan fields:

- Proposed tier: heavy. It changes the lifecycle and when work ships with a known failure.
- Effort: E. The whole loop, two new scripts and changes across QA, Engineer, process and sweep docs; more than one session (split below).
- Reasoning: D. The rules interact (points, related findings, patchwork guard, step-ups of the re-check, the ship rule).
- Impact: C. A routing error could ship a Critical finding without the human.
- Needs: issue 01a and 01b (merged): reads `QA_FAIL_AT`, `QA_SCOPE_STRICT`, `RECHECK`, `FIX_CHECK_LOOPS`, `ASK_AT`, `SHIP_RULE`, `STEP_UP`, `FINDINGS_TO_ISSUE_AT`, `FINDINGS_GROUP_AT`, `FINDINGS_KEEP_SWEEPS`. Issue 02 (merged): the finding and QA comment formats.
- Runs in: sandbox.
- Debt: `STEP_UP=auto` can't switch a variant until issue 08c defines reasoning variants of the role files; until 08c lands, `auto` acts as `ask` and says so (see C7; approved by the human on 2026-11-19).
- Touches protected `agent-kit/` files: yes.
- Files: `agent-kit/customizing.md` (section 4.4 points routing; the vocabulary is already there from issue 01a), `agent-kit/team/qa-engineer.md`, `agent-kit/team/software-engineer.md` (fix check, patchwork guard, `shortcut:` debt), `agent-kit/process.md` (Lifecycle steps 4 to 7: the loop, re-check scope, ship-or-fix), `agent-kit/procedures/sweep.md` and both `skills/sweep/SKILL.md` copies (read the findings log, draft one issue per group), `agent-kit/scripts/findings.py` (new: list, group, age), `agent-kit/scripts/route-finding.py` or a function in it (points and route), `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (`findings` target), `agent-kit/installed-files.txt`, `agent-kit/CHANGELOG.md`, `tests/test_findings.py` (new). `agent-kit/scripts/` runs live.

Acceptance criteria:

- [ ] C1. PASS or FAIL is decided by impact only: a finding fails when its impact is at or above `QA_FAIL_AT` (default `M`). With `QA_SCOPE_STRICT=yes`, an out-of-scope finding, or a breach of a standard the issue doesn't list, never fails.
  Check: `tests/test_findings.py` cases: `L/in` logs, `M/in` fails, `C/out` logs (and goes to an issue, C8) with the defaults.
- [ ] C2. Points (4.4): effort (S=1, R=2, E=3) plus 1 for each failed QA re-check on the finding or a `related:` one. Fix checks add no points. Below `ASK_AT` (default 4) the Engineer fixes; at or above, "ship or fix?" goes to the human in the 5.4 form.
  Check: `tests/test_findings.py` reproduces the 4.4 table: E asked after one failed re-check, R after two, S after three.
- [ ] C3. Ship rule: with `SHIP_RULE=none` (default) no failing finding ships without the human. A rule such as `impact:M,effort:E,rounds:1` lets only matching findings ship, logged.
  Check: `tests/test_findings.py`: default never ships; the example rule ships an M/E finding after one round and refuses a C/E one.
- [ ] C4. Fix check (inner loop): after a fix and before QA re-checks, a basic-reasoning check runs on the fix's diff, the tests around it and the standards' scripts; it is not a QA round and adds no points. It stops when clean or after `FIX_CHECK_LOOPS` tries (default 2).
  Check: read `agent-kit/process.md` and `software-engineer.md`; the loop limit is the setting, named once.
- [ ] C5. Patchwork guard: when a finding or a related one fails a second time, the Engineer writes an approach review (root cause, why earlier fixes missed, whether to change approach) in its comment before the next fix. A change of approach is a stop decision point (issue 05 adds it to the stop list; until 05 lands, it is a question at the existing decision point).
  Check: read `software-engineer.md`; QA's checklist in `qa-engineer.md` checks that a second-failure fix has the review.
- [ ] C6. `RECHECK=changed` (default) re-checks the failed criteria, every criterion whose files the fix touched, and the standards' scripts; Verify always runs in full. It becomes a full re-check by itself when the fix touched files outside the failed criteria or the patchwork guard fired. `RECHECK=full` always re-runs everything. The Heavy second launch is always full and runs once.
  Check: read `qa-engineer.md` and `process.md` Tiers (Heavy gates).
- [ ] C7. `STEP_UP` (Claude Code only): at a finding's second failure, `ask` (default) puts the step up into the next message to the human as a note with a recommendation, `auto` launches the next reasoning variant up where it exists, `off` never steps up. Where no stronger variant is defined it is skipped and noted. In OpenCode and Kiro the setting is ignored and the approach review is the only step up. Until issue 08c lands and defines the variants, `auto` acts as `ask` and says so in the note.
  Check: read `process.md` and `customizing.md`; both name Claude Code only.
- [ ] C8. Findings not fixed: impact at or above `FINDINGS_TO_ISSUE_AT` (default `C`) gets an unlabelled PM draft issue; the rest go to `_docs/records/findings/<issue>.json` with a `group`. Debt (a deliberate `shortcut:` or debt QA notices) is a finding with `category: debt`.
  Check: `tests/test_findings.py` writes and reads a findings file; read `qa-engineer.md`.
- [ ] C9. `make findings` lists open log entries by group with age (in sweeps), totals debt by group, and flags groups at or above `FINDINGS_GROUP_AT` (default 5) and entries open for `FINDINGS_KEEP_SWEEPS` sweeps (default 5) as needing keep or drop.
  Check: `tests/test_findings.py` with a fixture folder; run `make findings` on an empty folder (prints none).
- [ ] C10. Refused: a findings file that is not valid JSON or has an entry missing `group` or `impact` makes `make findings` exit non-zero and name the file; it never skips it silently.
  Check: `tests/test_findings.py` refusal case.
- [ ] C11. The sweep (`procedures/sweep.md`) reads the findings log and drafts one issue per group at the threshold, and brings keep-or-drop entries to the human.
  Check: read `agent-kit/procedures/sweep.md`; `tests/test_sweep.py` updated if it asserts the steps.

Out of scope: reasoning variants of role files (issue 08c); decision-point weights and the ledger (issue 05); the vocabulary and numbered criteria (already in place from issue 01a).

Split (approved by the human on 2026-11-19; the criteria above are numbered for the whole, and each filed issue renumbers its own from C1):
- 03a: PASS/FAIL by impact, points routing, ship rule, fix check, patchwork guard, `RECHECK`, `STEP_UP` (C1 to C7). Tier heavy. Effort E, Reasoning D, Impact C. Needs: issue 01a, 01b (merged: `make settings` and the bounds), issue 02 (merged).
- 03b: findings log, `make findings`, age rule, debt category, sweep reads the log (C8 to C11). Tier heavy. Effort R, Reasoning N, Impact M. Needs: issue 03a (merged).

Existing issues affected: the patchwork guard (C5) answers issue #141's third question ("should the process say fix the class, not the spot?"). Issue #141 keeps only its filesystem-failure audit.

**Evidence**

- Proposal sections 3.5, 4.0, 4.4, 4.2 (settings), 12 (decided: vocabulary, thresholds, `ASK_AT=4`, step up Claude Code only, findings thresholds).
- Proposal section 1: socboard 57 of 146 issues with at least one QA FAIL; socboard issue #139 (eight Engineer rounds) and socboard issue #63 (four QA runs). socboard rulings: Medium-or-higher fails; "ship or fix?" after repeated rounds; a fix round re-checks only the changed lines; findings in a file per issue (`socboard/_docs/records/`, group `checker-looser-than-intent`).
- Ponytail's `shortcut:` comment as the source of the debt category (proposal 3.5, section 13).
