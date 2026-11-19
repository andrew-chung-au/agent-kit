# Measurement: ponytail review, baseline (no ponytail) against the ponytail group

Written by a fresh PM launch following "Measurement for review" in `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`, in the same session as the fifth sweep (`.scratch/2026-11-13T0424Z-measure-pm-sweep.md`). I changed no tracked file and filed nothing. This record **recommends nothing**: the decision record leaves Keep or Drop to the human. Raw values come first; the summary statistics come after them.

- **Question:** For the six Core issues worked without ponytail (#8, #51, #9, #10, #11, #12) and the six worked with it (#102, #99, #14, #15, #16, #18), how do non-test lines per acceptance criterion, tests added per criterion and QA FAIL rounds compare, and what did the human's labels say about the Reviewer's findings?
- **Command and commit:** `make ponytail-metrics N=<n>`, run one issue at a time for #8, #51, #9, #10, #11, #12, #102, #99, #14, #15, #16 and #18, between 2026-11-13T04:17Z and 04:28Z (the file name uses the timestamp read at 04:24:36Z), after `git fetch origin`. The tree is on `issue-18-nul-text` at `d72ccdc`, one merge commit behind `origin/main` = `3dc8b907c112d92e5c73c2c0d2be7a4e10e4c5eb` (committed 2026-11-13T04:14:15Z); `scripts/ponytail_metrics.py` and `Makefile` are identical in both (`git diff origin/main --stat` over them printed nothing). QA FAIL rounds and Engineer comments: `.scratch/sweep5-comments.py` (GitHub REST, owner comments only). Launch counts and labels: the session summaries at `origin/main`. Medians: `.scratch/sweep5-stats.py`. The switch-on commit is `72d383b` ("Switch ponytail on: Engineer skill and Reviewer after QA PASS (AGENTS.md)"), committed 2026-11-12T23:16:51Z.
- **Baseline:** the six control issues named in the decision record (#8, #51, #9, #10, #11, #12), all claimed before the switch-on commit (the latest, #12, was claimed 2026-11-12T21:01Z). **Comparison group:** the Core issues claimed after the switch-on: #102 (claimed 2026-11-13T00:26Z), #99 (00:36Z), #14 (01:57Z), #15 (02:33Z), #16 (03:13Z) and **#18 (03:18Z)**. #18 was also claimed after the switch-on, so it is in the group; it ran in Kiro Web in parallel with #16, which ran in Claude Code (a one-time human exception to `delivery-pace.md` item 4). **#13 is in neither group**: it was claimed at 2026-11-12T22:52Z, before the switch-on.
- **Result:**

  ### Raw per-issue values

  Lines are added plus deleted in non-test, non-generated files over the commits the script counted (a commit counts for issue N when its subject ends `(#N)` and names no other issue). "Tests added" counts added lines that start a test function or case. QA FAIL is the number of owner comments whose first line starts `QA: FAIL`. Tier is from the claim comments or summaries.

  | Issue | Group | Tier | Criteria | Non-test lines | Lines per criterion | Test lines | Tests added | Tests per criterion | QA FAIL (first line) | Engineer rounds | Defects found after PASS |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | #8 | baseline | Standard | 10 | unknown | unknown | unknown | unknown | unknown | 0 | unknown | unknown |
  | #51 | baseline | Standard | 11 | 118 | 10.73 | 501 | 10 | 0.91 | 0 | 1 | unknown |
  | #9 | baseline | Heavy | 29 | 1079 | 37.21 | 0 | 0 | 0.00 | 2 | 8 | unknown |
  | #10 | baseline | Standard | 14 | 250 | 17.86 | 1022 | 56 | 4.00 | 0 | 2 | unknown |
  | #11 | baseline | Heavy | 33 | 1238 | 37.52 | 3412 | 175 | 5.30 | 2 | unknown | unknown |
  | #12 | baseline | Standard | 14 | 176 | 12.57 | 215 | 18 | 1.29 | 0 | unknown | unknown |
  | #102 | ponytail | Standard | 9 | 8 | 0.89 | 71 | 3 | 0.33 | 0 | 1 | unknown |
  | #99 | ponytail | Heavy | 18 | 364 | 20.22 | 871 | 43 | 2.39 | 2 | 4 | unknown |
  | #14 | ponytail | Heavy | 17 | 367 | 21.59 | 717 | 45 | 2.65 | 0 | 2 | unknown |
  | #15 | ponytail | Standard | 8 | 143 | 17.88 | 424 | 24 | 3.00 | 0 | 2 | unknown |
  | #16 | ponytail | Standard | 7 | 130 | 18.57 | 243 | 13 | 1.86 | 0 | 2 | unknown |
  | #18 | ponytail (claimed after switch-on) | Standard | 7 | 95 | 13.57 | 375 | 25 | 3.57 | 0 | 3 | unknown |

  Each cell is a value `make ponytail-metrics` printed, except QA FAIL (the comment census) and Engineer rounds (the session summaries' Launch usage). I recomputed the two ratios from the raw counts (`.scratch/sweep5-stats.py`); they match the script's rounding.

  **Where the script printed an error (read as `unknown`):**
  - **#8:** `git figures: unavailable (no owner Orchestrator comment has a 'QA PASS commit:' line)`, then `make: *** [Makefile:42: ponytail-metrics] Error 1` (the tool reported exit code 2). Criteria (10) and the elapsed times still printed. #8's PASS is the one at `QA: PASS` comment `6789559879`; the script needs the `QA PASS commit:` line in an `Orchestrator:` comment, which #8 does not have.
  - **#16:** no error. The task note expected one because #16 was closed by hand, but its `Orchestrator: Close` comment (`6843156903`) carries `QA PASS commit: f7e6062`, and the script printed every figure with exit code 0.
  - **Understatement risk, no error:** the script lists commits it left out. #99: "mention only" `45eca31` ("Fix #99 test: a comment naming the table is refused, not a near miss", a real #99 commit with no `(#99)` ending) and "shared" `3997c2f` (a roadmap placement). #14: mention only `da43b33`, `3997c2f`, `59c9f33`, shared `e2aa91f` (docs and roadmap commits). #102: shared `59c9f33` (roadmap). #9: five docs commits, #11: one. For #99, `45eca31` changes a test, so #99's test lines are probably understated; I did not diff it. The other excluded commits are docs or roadmap edits.

  **Other raw values:**
  - **QA FAIL at verdict level, where the first line hides it.** #9: the first-line count is 2, but three more QA comments begin `QA: Code review (second launch)` and carry `Verdict: FAIL` (comments `6801543440`, `6807839186`, `6807946770`), so verdict-level FAIL rounds are 5. #11: both FAILs begin `QA: FAIL`, so 2 either way. No comment in the ponytail group hides a FAIL behind another first line. I used the first-line count in the table because that was the task's definition.
  - **Engineer rounds.** #8: unknown (no session summary for #8 at `origin/main`; the issue has 2 owner `Engineer:` comments). #51: 1, plus a reflection relaunch. #9: 8 (summary). #10: 2 (first pass; completion and Reflection comments). #11: unknown for the issue (the summary covers only the option-B session, "Engineer ×2"; the issue has 6 `Engineer:` comments). #12: unknown (summary: "figures not available to this launch"). #102: 1. #99: 4 (the issue has 3 `Engineer:` comments; one covers rounds 2 and 3). #14: 2. #15: 2. #16: 2 (Claude Code: 469 s and 34 tool uses, then 310 s and 26 tool uses). #18: 3 (implementation, merge resolution, finding 18-2). Kiro Web gives no time or tool-use figures.
  - **Reviewer launches (ponytail group only):** #102 1, #99 1, #14 1, #15 1, #16 1 (112 s, 17 tool uses), #18 2 (the first answered an unrelated message and was discarded). That is 7 launches for 6 issues.
  - **Defects found after PASS:** `unknown` for every issue. No later issue or comment I read names a defect in an earlier one as such. For context only, not counted: the Reviewer found gaps after a QA PASS on #16 (findings 16-1 and 16-2, both labelled `useful` and applied) and #18 (finding 18-2, a NUL character giving a 500, labelled `useful` and applied; the fix also covers ingest text from #14, but the summary does not call that a #14 defect). In the baseline, second-launch QA comments failed #9 and #11 after earlier PASSes inside the issue; those were found before the issues closed, so they are QA rounds, not defects after close.

  ### The human's finding labels (ponytail group only)

  From each summary's "Finding <issue>-<n>: <label>" lines and "Decisions made by the human". "QA had raised" is the summary's statement.

  | Issue | Findings | useful | correct-minor | wrong | harmful if followed | QA had already raised | Applied |
  |---|---|---|---|---|---|---|---|
  | #102 | 4 | 0 | 4 | 0 | 0 | 0 | 0 |
  | #99 | 6 | 3 (99-1, 99-2, 99-3) | 3 (99-4, 99-5, 99-6) | 0 | 0 | 0 | 0 (all to #107) |
  | #14 | 5 | 2 (14-1, 14-2) | 2 (14-3, 14-5) | 1 (14-4) | 0 | 0 | 0 (all to #110) |
  | #15 | 6 | 2 (15-1, 15-6) | 4 (15-2, 15-3, 15-4, 15-5) | 0 | 0 | 1 (15-6) | 0 (all to #110) |
  | #16 | 5 | 3 (16-1, 16-2, 16-3) | 2 (16-4, 16-5) | 0 | 0 | 0 | 4 (16-1, 16-2, 16-3, 16-5) |
  | #18 | 7 | 3 (18-2, 18-3, 18-5) | 4 (18-1, 18-4, 18-6, 18-7) | 0 | 0 | 1 (18-3) | 1 (18-2) |
  | **Total** | **33** | **13** | **19** | **1** | **0** | **2** | **5** |

  Label counts across the 33 findings: `useful` 13, `correct-minor` 19, `wrong` 1, `harmful if followed` 0. QA had already raised 2 of the 33 (15-6 and 18-3, both `useful`). Of the 13 `useful`, 4 were applied in the issue (16-1, 16-2, 16-3 and 18-2), and the rest went to #107, #110 or the #17 notice. The one applied `correct-minor` was 16-5. The one `wrong` finding (14-4, a 16-character minimum that the approved decision record fixes) was not applied.

  The baseline group has no labels in this scheme. One discrepancy to flag: the decision record's Reason says none of #8, #51, #9, #10, #11 or #12 has a reviewer comment, but #51 has an `Orchestrator: shadow review (ponytail trial, Phase 1) of #51` comment (`6792371537`), and its summary lists a Reviewer launch with 6 findings. The review was not applied to the code and the #51 Engineer did not use ponytail, so #51 stays in the baseline; the "Reviewer runs only in the ponytail group" limit below is therefore true of the Engineer-side skill and of every issue but #51.

  ### Summary statistics (each group has 5 or more issues)

  | Measure | Baseline (n = 5; #8 `unknown`) | Ponytail (n = 6) |
  |---|---|---|
  | Lines per criterion, median | 17.86 | 18.23 |
  | Lines per criterion, min to max | 10.73 to 37.52 | 0.89 to 21.59 |
  | Tests per criterion, median | 1.29 | 2.52 |
  | Tests per criterion, min to max | 0.00 to 5.30 | 0.33 to 3.57 |

  Medians: baseline lines `17.86` is #10's value; ponytail lines is the mean of #15's 17.88 and #16's 18.57 (18.225). Baseline tests `1.29` is #12's value; ponytail tests is the mean of #99's 2.39 and #14's 2.65 (2.52).

  Sensitivity, each a choice of mine and shown only because one value in each group is unusual:
  - Baseline without #9 (the contract file; no code and no test lines): n = 4, below the 5-issue rule, so only for orientation. Lines per criterion median 15.22, band 10.73 to 37.52; tests per criterion median 2.65, band 0.91 to 5.30.
  - Ponytail without #102 (8 non-test lines for 9 criteria): n = 5. Lines per criterion median 18.57, band 13.57 to 21.59; tests per criterion median 2.65, band 1.86 to 3.57.

  QA FAIL rounds by the first-line definition: baseline 4 across six issues (#9: 2, #11: 2), ponytail 2 across six (#99: 2). At verdict level the baseline total is 7 (#9: 5). Heavy issues: baseline #9 and #11; ponytail #99 and #14.

  ### What the figures and labels show (no recommendation)

  - The medians for lines per criterion are close (17.86 and 18.23) and the bands overlap. The baseline band is wider on the high side because #9 and #11, both Heavy, are near 37; no ponytail issue is above 21.6. The ponytail group's lowest value, #102 at 0.89, is a one-handler change against nine criteria.
  - Tests per criterion have a higher median in the ponytail group (2.52 against 1.29) and the bands overlap (0.00 to 5.30 and 0.33 to 3.57). The decision record keeps the role file's "tests for what you built" rule over the skill's "one small test", which is consistent with the ponytail group not writing fewer tests; I did not check why.
  - QA FAIL rounds: fewer in the ponytail group by the first-line definition (2 against 4), all on one issue. The baseline's FAILs came on two Heavy issues (#9, #11) whose second launches ran before the human's stopping-rule ruling on #13 (Medium or higher fails; the role file `team/qa-engineer.md` still says any problem is a FAIL, 675 words, unchanged, so the rule is applied by ruling, not by the file).
  - The Reviewer's labels: 32 of 33 findings were `useful` or `correct-minor`, 1 `wrong`, 0 `harmful if followed`. QA had raised 2 of the 33. 5 were applied; 28 were not applied in their issue (most went to #107 and #110). The summaries report the Reviewer's size estimates: "Ship" with findings on #102, #15 and #16; the final guard "over-built" on #99 (60 to 80 lines); about 55 code lines and 150 test lines that could go on #14; about 30 lines on #18. Whether that is a benefit, or advice the human mostly set aside, is for the human.
  - The Reviewer found two post-PASS gaps that were applied (16-1, 16-2) and one defect (18-2) that was applied. Those three are the only evidence in the group of the Reviewer catching something QA passed; they are three of 33.

- **Caveats:** (the limits the decision record requires, and others I found)
  - **Different issues, sizes and tiers.** The issues are not matched. Criteria range from 7 to 33; Heavy issues are 2 of 5 (with figures) in the baseline and 2 of 6 in the ponytail group. #9 is a contract file and #51 a frontend screen-behaviour issue, so the baseline mixes kinds of work; the ponytail group is all backend routes and guards. Lines per criterion depends on how many criteria the PM wrote; #102 has 9 criteria for an 8-line change.
  - **Different tools and models.** The baseline ran in Kiro Web. The ponytail group ran in Kiro Web (#102, #99, #14, #15, #18) and Claude Code (#16). The model is `unknown` for most launches (Kiro: "model unknown" or "auto"; Claude Code: "unknown to the orchestrator for subagents"). A difference could come from the tool or the model instead of ponytail.
  - **Process edits between the groups.** #102's change to the shared error handler, #99's guard hardening and the Reviewer step itself came with or after the switch-on; the Heavy second-launch stopping rule was applied from #13 on by the human's ruling (Medium or higher fails; the role file was not changed); `delivery-pace.md` items 1 to 4 (CI as the test loop, one PR per issue, grooming ahead, one extra issue in flight) were ruled on 2026-11-12 and apply to both groups only partly; the `AGENTS.md` Ponytail line also changed the Reviewer comment prefix to `Orchestrator: Reviewer report` after #102's first use.
  - **The Reviewer runs only in the ponytail group**, and its findings are advice. QA FAIL rounds in the two groups are not like for like: the ponytail group has one more detector (the Reviewer) after the last QA PASS, and the Heavy second-launch rule was applied differently (see the next bullet). Apart from #51's shadow review (see above), no baseline issue had a Reviewer.
  - **Group sizes.** Baseline has 5 issues with figures (#8 `unknown`); ponytail has 6. Medians of five or six values move by a single issue: replacing #102 or #9 changes a median (sensitivity above). The ratios are not rates with errors.
  - **The metric's own limits.** It counts lines of every non-test, non-generated file in commits whose subject ends `(#N)`, so Markdown, YAML and decision records count as lines (the script's file split is by name only; I did not split by type). "Tests added" counts test-function starts, so a parametrised test counts once: #102's summary lists 13 login bodies and the script counts 3 test starts (I did not open the file to confirm parametrisation). A commit without the `(#N)` ending is not counted (`45eca31`). The script can only read a close that has a `QA PASS commit:` line (#8 has none). Criteria are the checkbox lines under "Acceptance criteria" in the issue body as it stands now.
  - **Engineer rounds** come from each summary's Launch usage, where given; #8, #11 and #12 are `unknown` for the whole issue. They are the orchestrator's counts of launches, not the tool's.
  - **Defects after PASS are `unknown` for every issue**, because nothing I read names one in a later issue. This is the protection metric the lines-per-criterion figure must be read against: a smaller diff with no measured defect count is an efficiency figure only (Safeguard 4).
  - **Directional only.** The comparison is directional and nothing is "proven". If it shows a promising difference, the shelved trial (`_docs/planning/roadmap-2-ponytail-trial.md`) is the way to confirm it. I recommend neither Keep nor Drop.
  - **What I did not check:** the Reviewer comments on the issues (I used the summaries' labels), the test files, the diffs behind the counts, and whether any later issue calls an earlier one's code defective beyond the summaries and comment first lines I read.

- **Human (2026-11-13):** the human has read this record. They judge the benefit over the development cycle, so this record makes no Keep or Drop decision. Ponytail stays on, as `AGENTS.md` says. Correction to the decision record it reviews: #51 does have a shadow-review comment (6 findings, none applied). The sentence in `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md` that said no baseline issue had one is corrected in the same commit.
