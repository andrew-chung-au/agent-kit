# Measurement: fourth PM sweep (trigger: `make sweep-due`, 8 closed since 2026-11-12)

Written by the PM role; it proposes, it applies nothing (`_docs/agent-kit/procedures/sweep.md`). Only files in `.scratch/` were written; no tracked file was edited, nothing was filed, posted, checked out or committed. Named per `_docs/agent-kit/procedures/session-summary.md` (timestamp from `date -u +%Y-%m-%dT%H%MZ`). Helper files left in `.scratch/` (mine): `sweep4-comments.py`, `sweep4-dump.py`, `sweep4-events.sh`, `sweep4-figures.sh`, `sweep4-order.sh`, `sweep4-reflections.py`, `sweep4-deltas.py`, the outputs `sweep4-fig-main.txt` and `sweep4-fig-cut.txt`, the folder `sweep4-comments/`, and copies of the sources I read (`prev-record.md`, `cand4.md`, `roadmap-main.md`, `ss-*.md`).

- **Cutoff:** HEAD = `origin/main` = `2f78f886b8adc93df726206ee65162f34277eab9` ("Merge pull request #96 from andrew-chung-au/issue-11-data-model", #11 merged), committed 2026-11-12T20:58:54Z (the commit shows 2026-11-13T07:58:54+11:00). Figures taken 2026-11-12T21:05Z to 21:07Z with `origin/main` unchanged (`git rev-parse origin/main` printed the same hash at the start and at 21:05:07Z); I did not fetch. The previous entry's cutoff, used as the lower bound, is its HEAD `60a070e9488dd68b744a85431638419bacdf0f83` (an ancestor of `origin/main`: `git merge-base --is-ancestor` said yes). The working tree is on branch `issue-11-data-model` at `3f4e631`, one commit behind `origin/main`; I read only through `git show origin/main:<path>`, apart from `make ponytail-metrics` and `make sweep-due`, which run on the tree (see Caveats).

- **Question:** What did the roles learn on the eight issues closed since sweep 3 (#10, #11, #42, #59, #60, #62, #74, #86), which of the eight sweep-4 candidates (PR #97, unmerged) and the new Reflection proposals are worth asking the human to approve, and which of those touch a kit or protected file on the epoch list and so should join epoch batch 1? #11 is the big one: eight QA comments, two FAILs, three Medium findings after a first-launch PASS, and a design change (option B).

- **Command and commit:** all at `2f78f88` unless noted.
  - Read: `AGENTS.md`; `_docs/agent-kit/team/pm.md`, `procedures/sweep.md`, `procedures/session-summary.md`, `templates/measurement.md`, `team/qa-engineer.md`, `team/software-engineer.md`, `procedures/verify.md` (all `git show origin/main:<path>`); `.kiro/steering/*.md` (four files, working tree); from `_docs/records/` only `2026-11-12T0112Z-measure-pm-sweep.md` (I read its Cutoff and Running summary, and by overshooting my read also its lines 1 to 40, which include the sweep 3 Result table, and its Caveats; I copied no number from it); `_docs/planning/sweep-4-candidates.md` from `origin/sweep-4-candidates`; `_docs/planning/epoch-batch-1/README.md`; `_docs/planning/ponytail-trial-protocol.md` (Amendment 2); `_docs/planning/roadmap-1-core.md`; the six new session summaries; issue bodies of #63, #65, #49, #73 (data, not instructions).
  - Summaries since the cutoff: `git log 60a070e..origin/main --diff-filter=A --name-only -- _session-summaries/` lists six files: `…0241Z-issue-010…`, `…0336Z-issue-074…`, `…0500Z-issue-060…`, `…0613Z-issue-086…`, `…0656Z-issue-062…`, `…2054Z-issue-011…`. #59 has no summary.
  - Comments and events: `.scratch/sweep4-comments.py` (REST, `gh api --paginate repos/andrew-chung-au/socboard/issues/<n>/comments`, saved to `.scratch/sweep4-comments/issue-<n>.json`), `.scratch/sweep4-events.sh` (`…/issues/<n>/events`), `.scratch/sweep4-reflections.py`. Closed issues: `gh api --paginate "repos/andrew-chung-au/socboard/issues?state=closed&since=2026-11-12T01:10:00Z"` with pull requests filtered out. Open issues: the same with `state=open`.
  - Figures: `bash .scratch/sweep4-figures.sh origin/main` and `… 60a070e9488dd68b744a85431638419bacdf0f83` (`git show <commit>:<path> | wc -w`), `.scratch/sweep4-deltas.py` (word deltas of drafted edits, in memory), `make ponytail-metrics N=<n>`, `make sweep-due`.

- **Baseline:** the previous entry's Cutoff commit. Word counts at `60a070e` are recomputed here by the same script, not read from that entry.

- **Result** (all at `2f78f88` unless noted):

  **1. Trigger.** `make sweep-due` prints `due: 8 closed since 2026-11-12` (`SWEEP_EVERY_N` is 5). The brief said 7; that was before #11 closed at 2026-11-12T21:00:06Z. The eight are #10, #11, #42 (closed as not planned, no role work), #59, #60, #62, #74, #86. #9 closed at 01:10:56Z, before the previous entry's name time (01:12Z), so it belongs to sweep 3.

  **2. Per issue** (GitHub comments and events; criteria and commits from `make ponytail-metrics`, run on the tree at `3f4e631`):

  | Issue | Closed (UTC) | Labels (events) | QA comments | QA FAIL | Engineer comments | Criteria | Commits counted |
  |---|---|---|---|---|---|---|---|
  | #10 | 11-12 02:42 | `approved` | 1 | 0 | 2 | 14 | 4 |
  | #11 | 11-12 21:00 | `approved` | 8 | 2 | 6 | 33 | 19 |
  | #42 | 11-12 01:52 | none (not planned) | 0 | 0 | 0 | n/a | n/a |
  | #59 | 11-12 08:55 | `approved` | 1 | 0 | 1 | 7 | 1 |
  | #60 | 11-12 05:46 | `approved` | 1 | 0 | 2 | 7 | 1 |
  | #62 | 11-12 08:06 | `approved` | 1 | 0 | 2 | 8 | 1 |
  | #74 | 11-12 03:59 | `approved` | 1 | 0 | 2 | 18 | 2 |
  | #86 | 11-12 06:19 | `approved` | 1 | 0 | 2 | 7 | 1 |
  | **Total** | | | **14** | **2** | **15** | | |

  No `tier:` label on any of the eight. **Reopen events: 0 on all eight.** Every one of the 14 QA comments starts exactly `QA: PASS` or `QA: FAIL` (the first-line check of sweep 3 is now met 14 of 14).

  **3. QA rounds and FAILs.** Seven issues had one QA comment each (all PASS). #11 had eight, in this order (comment id, commit, launch, verdict): 6819411895 `b14770d` first PASS; 6821290032 `7b6e505` first PASS; 6821540849 `7b6e505` second launch FAIL (M1, Medium); 6821907575 `1f85646` first PASS; 6822062758 `1f85646` second launch PASS (set aside by the human's ruling 6822299253: it ran in a resumed session); 6822225503 `1f85646` second launch FAIL (M2 and M3, Medium); 6823445361 `cf172ab` first PASS; 6824588180 `cf172ab` second launch PASS. So 12 PASS and 2 FAIL (13 valid verdicts, one discarded); both FAILs are #11 second launches; they were not consecutive, so the "two FAILs in a row" trigger did not fire. The Orchestrator posted 4 "Handover to the dev container" comments on #11 and 2 launch-environment comments on #10 (first lines).

  **4. Defects after PASS.** The three Medium findings on #11 (M1, M2, M3, QA's own labels) were each found by a second launch after a first-launch PASS at the same commit; M2 and M3 were also found after a second-launch PASS that was later set aside. None on the other six issues (no FAIL, no reopen); I did not search for later defects beyond comments and events. `make ponytail-metrics` does not compute defects after PASS.

  **5. Word counts** (`git show <commit>:<path> | wc -w`):

  | File | `60a070e` | `2f78f88` |
  |---|---|---|
  | `AGENTS.md` | 1348 | 1484 |
  | `_docs/agent-kit/process.md` | 3569 | 3569 |
  | `_docs/agent-kit/team/pm.md` | 1001 | 1001 |
  | `_docs/agent-kit/team/qa-engineer.md` | 675 | 675 |
  | `_docs/agent-kit/team/software-engineer.md` | 483 | 483 |
  | **Always-loaded total (5 files)** | **7076** | **7212** |
  | Core Markdown, 36 files (below), without `AGENTS.md` | 28947 | 28947 |
  | Core Markdown plus `AGENTS.md` | 30295 | 30431 |

  Core set used (my definition, from `sweep.md` step 3): `_docs/agent-kit/` top-level `README.md`, `blueprints.md`, `environments.md`, `process.md`, `setup.md`; everything `.md` in `team/`, `procedures/` and `templates/` (including `templates/github/`); `claude-code/START.md` and `opencode/START.md`; the six role-definition files in `claude-code/agents/` and `opencode/agents/`. Excluded: the two `skills/sweep/SKILL.md`, `.template` files, scripts. The kit's Markdown did not change since the cutoff (`git diff --stat 60a070e origin/main -- _docs/agent-kit .claude .opencode` shows nothing for them); the `AGENTS.md` growth (+136) is the Run, Backend stop, Migrate and New migration lines (#10, #11). `agent-kit.conf` also changed (+1 line: three frontend dependency files added to `PROTECTED`, #60).

  **6. Reflection coverage.** QA: 12 of 14 QA comments end with a `Reflection:` block (missing: #11 `6823445361`, the `cf172ab` first-launch re-check, and #59 `6818846065`). Engineer: a separate reflection comment on 6 of 7 issues with Engineer work (missing: #59). PM: 0 of 16 PM comments carry one, and all six summaries say `unknown (role not asked)` for the PM.

  **7. Order check (backlog-order rule).** All 23 open issues (#12 to #22, #31, #49, #54, #63, #65, #71, #73, #75, #80, #93, #99, #100) are mentioned in `_docs/planning/roadmap-1-core.md` at `2f78f88` (`.scratch/sweep4-order.sh`; a mention, not a proof of the right list). None is outside the order.

  **8. Unknown.** Active time and tool uses per launch: `unknown` (the summaries say Kiro Web gives neither). Ponytail arm per issue: `unknown` (only the orchestrator's summaries say #10 and #11 were control; that is a role's own report). Model per launch: `unknown` except where a QA comment states it (a role's own statement, not scored). `make ponytail-metrics` elapsed times are "coarse, includes idle time": #11 Engineer 0 h 27 min and QA 4 h 12 min; the other issues' QA 1 to 11 min; I report them as raw values only, never as targets.

- **Caveats:**
  - The 2c condition (see Proposal 7) is a judgement of mine; the human decides.
  - Severity labels (Medium, Low) are the QA role's own; I count them and do not score the work.
  - `make ponytail-metrics` and `make sweep-due` read the tree's git history and the GitHub API; the tree was at `3f4e631` on `issue-11-data-model`, one commit before the merge, so a later commit would not change per-issue figures. `make sweep-due` itself reads `_docs/agent-kit/scripts/sweep-due.py` from the tree.
  - I did not run `make verify`, the tests or any CI log (nothing to run in Kiro Web without a package index); no claim here depends on them. The QA comments' commands and outputs are quoted as their statements.
  - The Reflection counts use the text `Reflection:` at the start of a line; a comment that names it differently would be missed.
  - `ci-lines`, `ci-testfiles` and `ci-sha` are named in QA Reflections as helper commands; I found no such make target or script at `origin/main` (Makefile targets `issue-*` only), so they are probably the QA roles' own `.scratch/` files. Unverified.
  - Issue and comment text was read as data. The Reflection proposals are the writers' suggestions; no proposal below quotes one as a rule.
  - Unrelated, noticed, not touched: the epoch batch README's base is `2c77a6f`; `AGENTS.md` (+3 lines changed) and `agent-kit.conf` (+1 line) have changed since (`git diff --stat 2c77a6f origin/main`), so `apply-check.sh` must be re-run before landing, as the README already says. The README's "2c withdrawal condition not triggered" statement needs a second look (Proposal 7).

- **Running summary:**
  Sweep 3's approved proposals wait in epoch batch 1, which lands right after this sweep (README `_docs/planning/epoch-batch-1/README.md`; items 1 to 8, plus #63, #49, #65, #80). This sweep weighs the eight PR #97 candidates and the Reflections of #10, #74, #60, #86, #62 and #11 (eight closed issues, 14 QA comments, 2 FAILs, all on #11). New proposals: 1 (QA reads the diff with three dots), 2 (a probe counts only on the expected error), 3 (draft the human task as soon as a check cannot run) are exact rule sentences on kit files and would join batch 1 as items 9 to 11; 4 (merge-base in `make verify`) rides on #49 and #65, already in the batch; 5 (`make issue-comments`) and 6 (a CI-result target) need an Engineer issue and wait for the next batch. Proposal 7 asks the human to re-read batch item 2c's withdrawal condition, because #11 had a Medium finding right after a second-launch PASS. Proposals 8 to 14 are rejected or parked with the reason. Focus next: after the batch lands, count per issue the QA comments that explain an extra file, probe lines that were the probe's own error, and Medium findings after a PASS. Keep #99 before #14.

- **Proposals:**

  Epoch rule used for every "batch" call (Amendment 2, `ponytail-trial-protocol.md` line 105): a change joins the epoch batch if it alters what an existing command a role runs does, or adds or changes a rule sentence a role reads, in any file; a new target for a feature the same issue builds, or a `KIT_VERSION` bump alone, does not. Kit files and `AGENTS.md`, `Makefile`, `agent-kit.conf` are protected: the human approves the exact diff, then a `HUMAN_APPROVED=1` commit. I drafted no patch (a sweep files nothing); after the human's ruling I would draft the diffs for 1 to 3 in `_docs/planning/epoch-batch-1/` style. Word deltas are computed by `.scratch/sweep4-deltas.py` on the `origin/main` blob.

  **1. QA reads the diff against the merge base (three dots). Recommend: accept, join the epoch batch (new item 9).**
  - *Evidence:* five QA launches on three issues lost time to a diff that showed files the branch did not change. #10 QA: the plain name list showed two docs files that came from main. Three #11 second launches (6821540849 Reflection 1, 6822062758 Reflection 1, and 6822225503 finding L3): `make verify BASE=origin/main` listed `_docs/specs.md` (29 files against the branch's 28, or 28 against 27) because main had moved; each QA ran `git merge-base` by hand. #60 QA: the claim's base was not the commit's parent, so a naive diff included epoch drafts. The kit's own wording is the cause: `team/qa-engineer.md` line 22 says `git diff origin/main --stat`, which is a two-dot diff against the tip.
  - *File:* `_docs/agent-kit/team/qa-engineer.md`, Code review, line 22. Replace `git diff origin/main --stat` with `git diff origin/main...HEAD --stat` and add a clause that three dots show only this branch's changes after main has moved. Expected word change: 675 to 687 (+12). The three-dot form needs no `$(...)`, so it fits the command-shape rule. It does not fix #60's case (the branch itself carried commits not on main); there QA should still state the base it used.
  - *Hunk position:* lines 21 to 23, clear of batch item 3 (after line 14) and 2c (line 29); the README's apply check should still be re-run.
  - *Measure:* count QA comments that explain away an extra file or a base mismatch (text search of QA comments over the next five issues; today at least 5 launches), paired with the protection metrics QA FAILs after a first-launch PASS and Medium findings after a PASS (a shorter diff must not mean a missed file).
  - *Epoch:* yes (changes the command a role runs).

  **2. A probe result counts only when it is the expected refusal. Recommend: accept, join the epoch batch (new item 10).**
  - *Evidence:* the final #11 second launch (comment 6824588180, Reflection 1 and 2): two `lambda_stmt` probes broke on the reviewer's own closure (`InvalidRequestError`); the first results looked like refusals and were nearly counted as covered. The FAIL launch at `1f85646` (6822225503, Reflection 1) hit the same closure trap with `datetime.now(UTC)` and needed a second probe file. So two of the three fresh second launches met it; both caught it before posting, which is the behaviour the sentence would fix in place. A probe error counted as a refusal is a false "covered" on a security limit.
  - *File:* `_docs/agent-kit/team/qa-engineer.md`, Code review (after the item list, before "In the Heavy second launch"). Wording: "A probe result counts only when the error class and message are the expected refusal; an error raised by your own probe is not a refusal." Expected word change: 675 to 701 (+26). It sits well with batch item 3 (a criterion that cannot run is "not run", never passed): same family, different case, so I do not merge them.
  - *Measure:* number of probe lines in second-launch comments whose error is the probe's own (QA Reflections, or a later re-check finding one), paired with defects after PASS and QA rounds per Heavy issue. Efficiency is not the claim; this is protection.
  - *Epoch:* yes (a rule sentence).

  **3. Draft the human task as soon as a check cannot run here. Recommend: accept, join the epoch batch (new item 11); this is the PR #97 candidate 3, moved to a different file.**
  - *Evidence:* Engineer Reflections on four issues. #74 (3): nothing ran, so the contract form was a guess until the human's run; proposes the early human task. #62 (2 and 3): the shuffled-seed criterion waited on a human run at the end. #86 (1 and 2): the draft needed four edits once CI and human results arrived, and nearly said "not checked" when the evidence had come in. #11 (Slow, Unclear): no test could run; CI was the loop. On the other side, #10's summary records that asking for the human's runs before the first QA launch gave a single QA round. The rule exists in `team/software-engineer.md` line 14 ("If the human must run or check something by hand, draft a task file …"); what is missing is when.
  - *File:* `_docs/agent-kit/team/software-engineer.md`, line 14, append: "; draft it as soon as you know a check cannot run here, and list each guess you could not confirm". Expected word change: 483 to 503 (+20). I chose this file over `procedures/verify.md` and `environments.md` (the candidates' and the Reflections' guesses) because the rule is already there and this is one clause. Batch item 1 (list each check not run, +14) edits line 22, a different hunk; item 2b (human-task template wording) is the template, not this file. They stack; they do not duplicate. Words with item 1: 483 to 517.
  - *Measure:* per issue where a check could not run, hand-over round trips between the Engineer's draft and the human's results, and criteria still "not done" at hand-over (both efficiency numbers: waits are informational, not targets), paired with QA FAILs and defects after PASS on those issues; if the pair moves the wrong way, withdraw.
  - *Epoch:* yes (a rule sentence).

  **4. `make verify` diffs against the merge base when `BASE` is given. Recommend: accept; rides on the batch (cross-reference #49 and #65), no new batch item.**
  - *Evidence:* PR #97 candidate 2; it is Reflection 3 of the FAIL at `7b6e505` (6821540849), and the same trouble is Reflection 1 of 6822062758 and finding L3 of 6822225503. With `BASE=origin/main` and a moved main, the verify file list and weakened-test check show main's changes as the branch's. This overlaps #65 (the CI base) and #49 (edits `verify.sh`), both approved and in the batch.
  - *File:* `_docs/agent-kit/scripts/verify.sh` (kit, protected), plus one clause in `procedures/verify.md` (not drafted; word change unknown). Not a separate item: when the human next re-records #49 or #65, add this as a criterion (PM re-records the body hash) so the batch's plumbing issues carry it and the epoch moves once. If the human prefers not to re-open an approved body, it becomes its own small issue in batch 2.
  - *Measure:* QA comments that explain an extra file in the Verify list (target none), paired with the weakened-test check still failing on a real skip marker (#49's and #65's own criteria) and defects after PASS.
  - *Epoch:* yes (changes what `make verify` does).

  **5. A target that writes an issue's comments to `.scratch/`, one section per comment. Recommend: accept later (an Engineer issue; next epoch batch, not batch 1).**
  - *Evidence:* PR #97 candidate 6. Five Reflections on three issues name a truncated or oversized comment dump: #10 Engineer and QA (the JSON was cut mid-comments, two fallback fetches); #11 first-launch QA (6819411895, proposes `make issue-comments N=<n>` and wrote a script instead) and the final second launch (one 30 KB dump, a second filtered read); #86 QA (`gh issue view` fails; fell back to the JSON). Sweep 3's #73 (approved; body only, no comments) addresses the opposite half, the independent reviewer reading the body without verdicts. Keep #73 as approved. The comments target is the other half; do not fold it into #73's body without a new hash.
  - *File:* `Makefile` and one line in `AGENTS.md` Commands (both protected); possibly a script under `_docs/agent-kit/scripts/`. A new target alone does not move the epoch; the AGENTS.md line that roles read does, so it goes in the next batch. Words: about +35 in `AGENTS.md`, not drafted. It needs the human's approval of a `Makefile` diff, so ask in the same sitting as #73 and #71.
  - *Measure:* one-off `.scratch/` scripts whose only job is printing comments, per Heavy QA launch (today at least 1 per launch; target none), paired with QA FAILs and defects after PASS. The cap on output size stays: the target writes a file, it does not print.
  - *Epoch:* the AGENTS.md line, yes; place it in the next batch (like #93).

  **6. A target that prints a CI run's result lines and head commit. Recommend: accept later (an Engineer issue; next epoch batch).**
  - *Evidence:* PR #97 candidate 5, plus #11 first-launch QA (the run list failed on the host variable; a second command was needed to confirm the head commit; proposal `ci-sha RUN=<id>`). Four QA Reflections on three issues (#86, #62, #11 twice) report an oversized or failed CI log read; the #62 Engineer's script was hard-wired to one branch and the QA wrote another. The "do not use `gh issue view`" half of candidate 5 is already covered by `AGENTS.md` ("Fetch an issue": `make issue-dump`), so I drop it. A rule sentence in `qa-engineer.md` telling each QA to write its own log filter would cost words and be redone each time; a single target is better and `delivery-pace.md` item 1 already makes CI the test loop.
  - *File:* `Makefile` plus an `AGENTS.md` Commands line (protected); a script in `scripts/` or the kit. Words: about +30 in `AGENTS.md`, not drafted.
  - *Measure:* failed or truncated tool calls per QA launch on the CI-VERIFIED step (today 1 or 2 in the four launches), paired with QA FAILs, defects after PASS and "CI-VERIFIED" claims that cite a run on the wrong commit (the target prints the head commit, so this should reach zero).
  - *Epoch:* yes (AGENTS.md line); next batch.

  **7. Re-read batch item 2c's withdrawal condition against #11 before it lands. Recommend: a human ruling, not a file change; I would still land 2c.**
  - *Evidence:* the README says the withdrawal condition (a Medium defect after a second-launch PASS) "has not triggered", on the human's statement, and says the author did not re-check #10. I checked: #10 had one Standard QA comment (PASS), no second launch. On #11, the second-launch PASS at `1f85646` (6822062758, 11:14:42Z) was followed at 11:22:32Z, same commit, by a fresh second launch FAIL with two Medium findings (M2, M3). Read literally, that is a Medium defect after a second-launch PASS. Reasons it may not count: the human set that PASS aside because it ran in a resumed session (not independent), and the launch used the stopping rule via the handover; the miss was probe coverage (`lambda_stmt` and `table()` were not tried), not the rule's treatment of Lows. Both fresh launches that ran under the rule did FAIL on Mediums (`7b6e505`, `1f85646`), and the final one passed at `cf172ab` after option B.
  - *File:* none (a ruling on `_docs/planning/epoch-batch-1/README.md`, "2c withdrawal condition", to be updated by the orchestrator after the ruling). Words: 0.
  - *Measure:* unmeasured. After 2c lands, count Medium findings that appear after a second-launch PASS (QA comments), paired with second-launch FAIL counts per Heavy issue, so the condition is tested from then on.

  **8. Second QA launch must start in a new session and say so. Recommend: reject.**
  - *Evidence:* PR #97 candidate 1; the evidence is one comment, the #11 second-launch PASS at `1f85646` (6822062758, Reflection 2 and 3), whose reviewer disclosed up front that it ran in the session that wrote the previous review. The rule already exists in the kit: `process.md` line 95 says the second launch is fresh, never resumed, and a resumed one is discarded and rerun. It worked as written: the reviewer disclosed, the human set the PASS aside (6822299253) and ran a fresh launch, which found M2 and M3. The failure was in who launched it, not in what the role file says; `qa-engineer.md` is read by the reviewer, who already disclosed.
  - *File:* would have been `team/qa-engineer.md`; none. Words: 0 (a proposed +20 saved).
  - *Measure:* not applicable. Keep watching: second-launch comments that disclose a reused session (today 1 of 4, on #11); if it recurs after the human's ruling, the fix is in the orchestrator's launch message (`process.md`), not here.

  **9. QA may ask for one throwaway CI run of the reverted fix. Recommend: reject for now.**
  - *Evidence:* PR #97 candidate 4; one instance, #62 QA Reflection 2 ("fails on the old value" was reasoned, not proven, and QA labelled it as reasoning). The Engineer on #62 had already run two throwaway branch runs. The honest label is the behaviour the kit wants (batch item 3). A standing request for CI runs costs CI minutes and orchestrator turns on every Standard issue for one observation.
  - *File:* `team/qa-engineer.md` (not drafted). Revisit if a second issue shows a "reasoned, not proven" new test that later failed to catch its bug.
  - *Measure:* unmeasured.

  **10. QA names what each refused test builds its inputs from. Recommend: reject for now.**
  - *Evidence:* PR #97 candidate 7; one instance, #74 QA Reflection 2. QA caught it unaided by reading the arguments, and the criterion was fine. No other QA comment since the cutoff reports a test that guards only a helper. Adds a line to every test-changing QA comment (about +25 words in a file that batch items 2c, 3 and 1/2 already grow to about 790).
  - *File:* `team/qa-engineer.md` (not drafted). Revisit if a helper-only test passes review once.
  - *Measure:* unmeasured.

  **11. A make target or procedure for proving a protected-file hook change in a throwaway worktree. Recommend: reject.**
  - *Evidence:* PR #97 candidate 8; one instance, #60 Engineer Reflection 1 and 3 (a one-off script, removed after use). Hook-change issues are rare, and the target would add a `Makefile` surface (protected) that most issues never use. The #60 change was one line of `PROTECTED`; the Engineer proved it with a script and QA passed.
  - *File:* `procedures/verify.md` or `Makefile` (not drafted).
  - *Measure:* unmeasured.

  **12. The Engineer keeps a running `.scratch/engineer-N.md` draft of choices and skipped checks. Recommend: reject.**
  - *Evidence:* #10 Engineer Reflection 1 and 3, and the sweep-4 note that it is "close to batch item 1". The slowdown on #10 came from the Engineer changing tools mid-issue (Claude Code usage ran out; the Engineer moved to Kiro Web, recorded in the summary), so the choices list from the first session was not there. The five Engineer reflections after it (#74, #60, #86, #62, #11) do not mention rebuilding choices from code. Batch item 1 already adds the unrun-checks list to the completion comment.
  - *File:* `team/software-engineer.md` (not drafted; roughly +25 words).
  - *Measure:* the proposal's own measure (file reads to write the comment) was set for "the next two issues"; the next two Engineer issues (#74, #86 or #62) show no such complaint, so by its own measure it is not needed.

  **13. Probe every statement wrapper (lambda, alias, lightweight table) and every table name. Recommend: reject as a kit rule; handled in #99 and later grooming.**
  - *Evidence:* #11's FAIL at `1f85646`, Reflection 3. Three launches in a row found an ordinary SQLAlchemy form that bypassed the application guard; the human then ruled option B (database triggers), which makes the wrapper list moot at the data layer, and #99 carries the Low findings (L1 to L5). The advice is specific to SQLAlchemy guards; a general version ("test every input class of a predicate") is what `pm.md` already asks for through a refused case per limit, and probe 2 above covers the false-pass trap. The summary's grooming notes for #13 to #17 already route what the Engineer needs.
  - *File:* none. Words: 0.
  - *Measure:* unmeasured; counted via #99/#14 QA comments.

  **14. "Existing tests pass unmodified" needs an exception clause when the design may change what they assert. Recommend: reject for now; cross-reference batch item 2d.**
  - *Evidence:* #11 Engineer Reflection (Unclear): the body said existing tests pass unmodified while option B made two raw-SQL tests false; the human ruled to record the exception in the summary and the Close comment (6835797665), and did not change the body again. One instance, resolved by a ruling. Batch item 2d ("do not use exactly, only or all for a list another role fills in") is the same family; "unmodified" is another absolute. If it recurs, extend 2d's wording by about eight words rather than adding a rule.
  - *File:* `team/pm.md` (not drafted). *Measure:* unmeasured.

  Other items read and not made proposals: #86 Engineer's wish for `make contract-check` in `make verify` is **batch item 6** (already approved, unchanged); #11 first-launch QA's "tell the human early when the runner cannot start" is already the practice in `delivery-pace.md` item 1 (CI is the test loop, QA cites run and log lines); #60 QA's "diff against the commit's parent" is folded into Proposal 1; #11 final-FAIL QA Reflection 2 (probe and notes files overwritten by name, because an earlier launch had used the same names in the same folder) is one instance and a symptom of the shared-session launch in Proposal 8; nothing to propose. The sweep-4 candidates table also cites batch item 6 and item 1 as already queued; I agree and did not repeat them.

  **Batch summary for the human.**
  - Join epoch batch 1 (exact diffs, wording the PM drafts after the ruling): Proposals 1, 2, 3 (qa-engineer.md +12 and +26; software-engineer.md +20; together about +58 words; with the batch's own items, `qa-engineer.md` goes 675 to about 790 and `software-engineer.md` 483 to about 517).
  - Ride on issues already in the batch: Proposal 4 (#49, #65).
  - Next epoch batch, each needing an Engineer issue and a `Makefile` diff approval: Proposals 5 and 6.
  - Human ruling on batch text: Proposal 7.
  - Not proposed further: 8 to 14 (reasons above).
  - Efficiency numbers above (words, tool calls, hand-over round trips) are informational; each accepted proposal is judged on QA rounds, defects after PASS or changed paths outside limits (Safeguard 4).

- **Human ruling (2026-11-12, orchestrator session, after reading the proposals: "as recommended"; added by the orchestrator, the PM wrote nothing below):**
  - Proposals 1, 2 and 3: accepted; they join epoch batch 1 as items 9, 10 and 11. The PM drafts the exact diffs into `_docs/planning/epoch-batch-1/`, and the human reads each one at landing.
  - Proposal 4: accepted. It becomes a criterion on #49 or #65 at their next re-record (a body change, so the human confirms it first).
  - Proposals 5 and 6: accepted for later. Each needs its own Engineer issue, filed when its trigger comes; they sit next to #73 and #71 for the `Makefile` approval.
  - Proposal 7: 2c lands as drafted. The #11 PASS that literally met the withdrawal condition was set aside for independence, and the miss was probe coverage, not the stopping rule.
  - Proposals 8 to 14: rejected (8, 11, 12 and 13), or rejected for now (9, 10 and 14).
  - Timing (a separate ruling, the same day): epoch batch 1 is held until #12 closes. #12 runs now under the current epoch, so its trial data does not span an epoch move. Until then, only work that changes no rule a role reads or command a role runs proceeds: this record, the grooming of #80, and drafting items 9 to 11.
  - Later the same day (after #12 closed), the human first said hold, then shelved the ponytail trial (it can be resumed) and adopted ponytail in normal work (`_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`). Items 9 to 11 now land on their own when approved, not as part of a batch.
