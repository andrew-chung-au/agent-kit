# Measurement: sixth PM sweep (trigger: the human asked; `make sweep-due` printed "due: 10 closed since 2026-11-13" when I ran it)

Written by a fresh PM launch following `_docs/agent-kit/procedures/sweep.md`. I wrote only this file (and read-only helper scripts `sweep6-*.py` and data dumps `sweep6-*.json/.txt` in `.scratch/`). I changed no tracked file, filed nothing, posted nothing and changed no label. Issue and comment text was read as data. Where a claim rests only on a role's own words, it says so.

- **Cutoff:** HEAD of record = `origin/main` as my clone holds it = `a63ef30fce89d4ac89d9587466274b9ab8c8d387` ("Merge pull request #129 from andrew-chung-au/issue-21-summary"), committed 2026-11-13T09:56:48Z (the commit shows 20:56:48+11:00). The working tree is branch `groom-handover-roadmap` at `41de5c6` (committed 2026-11-13T10:01:09Z), which is `a63ef30` plus one docs commit (the `_human-tasks/` hand-over files and a roadmap edit). I ran no `git fetch`, so the local `origin/main` ref is not refreshed: GitHub's `main` has since moved to `8bb6886` (PR #130, "Add make frontend-lint and make frontend-format (#75)", merged 09:59:15Z, push run 43405604764 success). It is outside this sweep's range by the human's instruction; #75 still read open when I listed issues. The previous entry's cutoff was `3dc8b907c112d92e5c73c2c0d2be7a4e10e4c5eb` (committed 2026-11-13T04:14:15Z, `git log -1 --format=%cI` shows 15:14:15+11:00). Figures were taken between 10:00Z and 10:09Z; the file name uses the clock read at 10:08:51Z.
- **Running summary:**
  Sweep 5's rulings have mostly landed. Its proposals 1, 3 and 7 are applied as four protected commits (`3a08673`, `007a072`, `4c78a30`, `84b1ba6`). Proposals 2 and 11 became #114 and #115, both still open. Proposals 5, 9 and 12 were done in the steering files and the roadmap. Proposal 8 is done (#63 closed). #73 and #71 landed. Still unbuilt: a CI-result target and `make issue-comments`; the merge-base check for `make verify` (sweep 4) now has a second reporter. Ten issues closed since: four Core (#17, #19, #20, #21), five supporting (#54, #63, #71, #73, #80) and one tracker closed as not planned (#125). QA gave 19 verdicts with 2 FAILs, both on #63. Reviewers raised 41 findings; the records show 19 applied. This sweep makes 11 proposals and one question. Six touch a protected kit file and need an exact diff approved (1, 2, 5, 7, 8, 9). Five are local steering or roadmap edits (3, 4, 6, 10, 11). Focus next: rule on #63's stopping rule and #19's close (question 12), decide whether #122's design replaces the marker list, and place the roadmap triggers that #21's closing made stale. Reflection coverage fell: five of nine issues carry no role reflection, so the next sweep leans on the Reviewers and the orchestrator's own notes.

- **Question:** What did the roles learn on the ten issues closed since sweep 5, what do the figures say about cost and protection, and which changes are worth the human's time?
- **Command and commit:** `make sweep-due` (printed "due: 10 closed since 2026-11-13"); `git log 3dc8b90..origin/main --diff-filter=A --name-only -- _session-summaries/`; `gh api` GET reads for issues, comments, pulls, events and runs (`.scratch/sweep6-census.py` for the comment census, `.scratch/sweep6-extract.py` for the summary extracts, `.scratch/sweep6-order.py` for the backlog-order check); `.scratch/sweep6-words.py` for word counts (`git show <commit>:<path>`, split on whitespace, equal to `wc -w`). All at `a63ef30` unless a line says otherwise.
- **Baseline:** the previous cutoff `3dc8b90`. Its word counts are recomputed here by the same script; I did not read them from the previous entry.
- **Result:** (all at `a63ef30`; the `3dc8b90` column is recomputed)

  **History in range.** `git log 3dc8b90..origin/main` has 71 commits. `git diff --shortstat 3dc8b90 a63ef30`: 49 files changed, 3986 insertions, 71 deletions (9 of those files are under `socboard/` or `tests/`: 1339 insertions, 36 deletions). Pull requests merged after the cutoff (GitHub, `merged_at` after 04:14:15Z): #116, #117, #118, #119, #121, #123, #124, #126, #127, #128, #129 (and #130 after the head of record). Push run 43405313174 on `main` at `a63ef30`: success.

  **Summaries added since the cutoff** (ten files, all read for Reflection and Launch usage): `…0509Z-issue-017…`, `…0520Z-planning-orchestrator-handoff`, `…0555Z-issue-019…`, `…0622Z-issue-054…`, `…0643Z-issue-063…`, `…0648Z-issue-073…`, `…0727Z-issue-071…`, `…0811Z-issue-020…`, `…0832Z-issue-080…`, `…0914Z-issue-021…` (all dated 2026-11-13). #17's summary arrived after sweep 5's cutoff, as sweep 5 said. There is no summary for #125 (a tracker, closed as not planned).

  **Issues closed since the previous entry's file-name time (04:24Z), by `closed_at`:**

  | Issue | Closed at (UTC) | Tier | Where worked | Close comment before close |
  |---|---|---|---|---|
  | #17 | 05:10:27 | Standard | Claude Code | 05:10:17, 10 s |
  | #19 | 05:59:33 | Standard | Kiro Web | **none**: closed by GitHub at merge, from the PR body (see Q12 and Rulings) |
  | #54 | 06:22:58 | Standard | Claude Code | 06:22:53, 5 s |
  | #63 | 06:50:27 | Heavy | Kiro Web | 06:50:18, 9 s |
  | #73 | 07:00:28 | Standard | Kiro Web | 07:00:18, 10 s |
  | #71 | 07:35:17 | Standard | Kiro Web | 07:35:09, 8 s |
  | #20 | 07:39:37 | Standard | Claude Code | 07:39:19, 18 s (a second Close comment followed at 08:12:25) |
  | #80 | 09:11:43 | Standard | Kiro Web | 09:11:34, 9 s |
  | #21 | 09:59:03 | Standard | Kiro Web | 09:58:53, 10 s |
  | #125 | 09:59:39 | not planned | n/a | 09:59:30, 9 s ("Close as not planned") |

  Tier is from each summary (the PM's proposal; no `tier:` label was recorded) and from #63's claim comment. #18 closed at 04:16:28Z, before the 04:24Z stamp, and belongs to sweep 5.

  **`make sweep-due` count (question 6).** Counting `closed_at` at or after 2026-11-13T04:24:00Z (what `sweep-due.py` does, pull requests left out): the 5th close was #73 at 07:00:28Z (the point `SWEEP_EVERY_N = 5` was reached; #71's summary, written at 07:27Z, says `make sweep-due` said due and the human chose to run the sweep later), the 7th was #20 at 07:39:37Z, and the 10th was #125 at 09:59:39Z. So a count of 7 was right for the window 07:39:37Z to 09:11:42Z, and the run I did printed 10, which matches the table (10 rows). The count includes #125 (closed as not planned, a tracker, no delivered code) and, once, an issue closed with no Close comment (#19). It leaves out #18 correctly. No mismatch found.

  **QA verdict comments per issue** (owner comments starting `QA: PASS` or `QA: FAIL`, from the census; the three `QA: Reflection` comments on #17, #54 and #20 are not verdicts):

  | Issue | Verdicts | FAIL | PASS | Note |
  |---|---|---|---|---|
  | #17 | 3 | 0 | 3 | round 1, round 2, merge re-check |
  | #19 | 2 | 0 | 2 | |
  | #54 | 2 | 0 | 2 | |
  | #63 | 4 | 2 | 2 | FAIL at `54be201`, FAIL at `c869592`, PASS at `8fbb56b`, second Heavy launch PASS |
  | #73 | 1 | 0 | 1 | |
  | #71 | 1 | 0 | 1 | |
  | #20 | 2 | 0 | 2 | |
  | #80 | 2 | 0 | 2 | |
  | #21 | 2 | 0 | 2 | |
  | Total | 19 | 2 | 17 | #125: none |

  **Launches per issue** (from each summary's Launch usage; the counts for #17, #54 and #20 also come from Claude Code completion notices; Kiro Web gives neither time nor tool uses, so those read `unknown`; a resumed launch's figure may be cumulative, so I add none up):

  | Issue | Launches | Detail |
  |---|---|---|
  | #17 | 7 (+2 resumes) | Engineer 3, QA 3, Reviewer 1; Claude Code |
  | #19 | 5 | Engineer 2, QA 2, Reviewer 1; Kiro |
  | #54 | 6 (+3 resumes) | PM 1, Engineer 2, QA 2, Reviewer 1; Claude Code |
  | #63 | 9 | PM 1, Engineer 3, QA 4, Reviewer 1; Kiro |
  | #73 | 3 | Engineer 1, QA 1, Reviewer 1; Kiro |
  | #71 | 3 | Engineer 1, QA 1, Reviewer 1; Kiro |
  | #20 | 7 (+2 resumes) | Engineer 3, QA 2, Reviewer 1, PM 1; Claude Code |
  | #80 | 5 | Engineer 2, QA 2, Reviewer 1; Kiro |
  | #21 | 6 | Engineer 2, QA 2, Reviewer 1, PM 1; Kiro |
  | Total | 51 | active time and tool uses for the Kiro issues: `unknown`; model: `unknown` everywhere |

  The QA launch counts match the verdict counts in the table above for all nine issues.

  **Reflection coverage** (blocks in the summaries). PM: 1 of 9 (#54; #20's PM summary line reads "role not asked"). Engineer: 3 of 9 in the three-part form (#17, #54, #20); #19 carries copied comment notes with no proposal. QA: 3 of 9 (#17, #54, #20). #63, #73, #71, #80 and #21 read "unknown (role not asked)" for all three roles. So #63's and #21's reflections made no proposals; what they left is the orchestrator's "What I learned" and "Unrelated problems" lines, used below.

  **Protection side of the efficiency figures (Safeguard 4):**
  - QA FAILs: 2 of 19 verdicts, both on #63 and both on one criterion (evasion of the floor). Early or missing Close comment: 1 (#19). Closing-keyword commits in the history: `git log origin/main -i -E --grep='...'` (same pattern as sweep 5) prints `84b1ba6` (the rule commit itself, whose subject contains the words "closing keyword") and `45eca31` (the #99 commit); no new real instance since the rule landed.
  - Reviewer findings, counted from the nine reports: #17 2, #19 5, #54 6, #63 7, #73 4, #71 2, #20 5, #80 5, #21 5 = 41. Applied, from the "Decisions made by the human" blocks: #17 2, #19 2 applied and 1 moved to #110, #54 5 (two as comment lines), #63 0, #73 0, #71 0, #20 4, #80 3, #21 3 = 19 applied. I did not read the human's useful/minor/wrong labels (they are not in these summaries), so I give no label counts.
  - Real defects the Reviewer found after a QA PASS and the human had applied: #17 finding 17-2; #19 findings 19-2 and 19-3; #21 finding 1 (a dead-end back link). I list them as evidence of the protection side; I do not score them as "defects after PASS" in a formal sense.
  - Claim-time check (sweep 5's proposal 1, now in `pm.md` and `orchestrator-comments.md`): it ran on #63 (found no contradiction) and on #19, where it found that the contract record contradicted the Lead-only criterion before any code was written (#19 summary). One catch in two recorded uses.
  - Medium-or-higher findings after a PASS: `unknown` (not counted; text search cannot tell them from restated criteria). Files changed outside the issue's limits: `unknown` (not computed). Human waits: informational, not counted.

  **Protected-file commits in range** (`git log 3dc8b90..origin/main -- _docs/agent-kit AGENTS.md Makefile .github agent-kit.conf`): 12 commits: sweep 5's four (`3a08673`, `007a072`, `4c78a30`, `84b1ba6`), #63's three (`54be201`, `c869592`, `8fbb56b`), #73's one (`1b712cc`), #71's one (`d192b13`) and #80's two (`4c71b0e`, `07e0fa1`) and the #73 merge. That the human approved each exact diff first rests on the summaries, not on git; I could not verify it from git.

  **Word counts** (`git show <commit>:<path> | wc -w` equivalent; the core set is the 36 files `sweep.md` step 3 lists: kit top-level `README.md`, `blueprints.md`, `environments.md`, `process.md`, `setup.md`; every `.md` in `team/`, `procedures/`, `templates/` (including `templates/github/`); the two `START.md`; the six role-definition files; not counted: `skills/*/SKILL.md`, `.template` files, scripts):

  | File | `3dc8b90` | `a63ef30` |
  |---|---|---|
  | `AGENTS.md` | 1664 | 1735 |
  | `_docs/agent-kit/process.md` | 3569 | 3569 |
  | `team/pm.md` | 1001 | 1037 |
  | `team/qa-engineer.md` | 675 | 675 |
  | `team/software-engineer.md` | 483 | 522 |
  | Always-loaded total | 7392 | 7538 |
  | Core Markdown (36 files) | 28947 | 29046 |

  The same figures at `41de5c6` (my branch) are unchanged (7538 and 29046): the hand-over commit touches no counted file. Per file, the core set changed in three files: `team/pm.md` +36, `team/software-engineer.md` +39, `procedures/orchestrator-comments.md` 319 to 343 (+24); `AGENTS.md` +71 (two new Commands lines: `make issue-body`, and `make issue-comment` with `make issue-create`). Those match sweep 5's proposals 1, 3 and 7. Word counts are tracked, never a gate.

  **Open issues in neither the Core task list nor the supporting list** (`.kiro/steering/backlog-order.md`; roadmap read from `origin/main` plus the new lines on my branch; 17 open issues from `gh api`, pull requests left out). Checked by reading the line that mentions each number, not only by searching the number:
  - On `origin/main` (`a63ef30`): **#131** only (filed 2026-11-13T10:00:02Z, "Frontend follow-ups from #21…").
  - On my branch (`41de5c6`): none. The new line in `_docs/planning/roadmap-1-core.md` places #131 "After #22; before Deploy" and records the PM drafts for #115, #112 and #122. Every other open issue (#22, #31, #49, #65, #75, #93, #100, #103, #104, #107, #110, #112, #114, #115, #120, #122) has its own line.
  - Staleness, not absence: #112 and #115 are placed "before #21", and #21 closed on 2026-11-13 with both still open (the human chose to start #21 once its listed dependencies were closed). Their trigger no longer names a future event (proposal 11).

- **Caveats:**
  - The ten issues differ: one Heavy, nine Standard or tracker, and two tools (Claude Code for #17, #20, #54; Kiro Web for the rest). Kiro Web gives no times or tool uses, so I compare nothing on time.
  - Counts of QA runs and Reviewer findings come from GitHub comments (the owner account posts all of them, so a role's prefix is its only mark). "Applied" counts come from the orchestrator's summaries.
  - The 51 launches are the orchestrator's counts in the Launch usage lines, not the tool's. I did not check them against any tool log.
  - I read the #63 comments in full (all eleven, QA FAIL 1 and 2 and both PASS in large part), the Reviewer report on every closed issue, and each summary's Reflection, Launch usage, Decisions, Unrelated problems and Follow-ups. I read the first lines of all other comments and some bodies. A detail in a comment I did not open could change a proposal.
  - I ran `make issue-body N=63` once to read #63's body; it wrote `.scratch/issue-63-body.json`. Nothing else was fetched by `make`.
  - The word-change estimates below are my guesses at a sentence of the stated length, not computed from a blob.

- **Proposals:**

  Protected files for this project (`agent-kit.conf` `PROTECTED`): `AGENTS.md`, `Makefile`, `_docs/agent-kit/*`, `.github/*` and others. Each change to one needs its exact diff approved by the human and a `HUMAN_APPROVED=1` commit. `.kiro/steering/*` and `_docs/planning/*` are not protected. I drafted no diff.

  **Two questions you asked, answered first.**

  *(1) Could #63's Heavy process have caught the fail-open marker list sooner, and was the stopping rule agreed with the human before the third run?*
  - What happened (comments `6845337811`, `6845523068`, `6845882757`, `6845965864` and the summary): FAIL 1 at `54be201` found that real comments from #99, #17 and #18, with a Reflection appended, slipped past because the code needed both markers (a Verify line and a numbered criterion line) while the issue's Design said either one. FAIL 2 at `c869592` found real #13 comment `6839188081` slipped past because the pattern allowed 20 characters between the word Verify and the colon. Run 3 passed at `8fbb56b`; the second Heavy launch passed at the same commit. The Reviewer then said the design itself fails open (findings 1 to 3); the human deferred all seven findings to #122. Three protected diffs (`54be201`, `c869592`, `8fbb56b`) were approved on the way.
  - Why the two FAILs were findable earlier: the body had two readings of one sentence ("no verify-result line and no per-criterion lines" in Design, "lacks the markers (a verify result and per-criterion lines)" in the Decision); its test criterion asked for "sample comment JSON", and the Engineer's own check script covered only the one layout that worked (QA's FAIL 1 says so). QA FAIL 1 replayed real comments, but only "the latest 100"; the second FAIL needed the whole history (330 comments) to find the #13 comment. A replay over the whole history in the Engineer's first round, with the let-through count reported, would have shown both failures before the first protected diff was approved, and the 12-of-50 let-through figure (QA run 3) before the decision record was written.
  - The stopping rule: QA run 3's PASS comment (`6845882757`) says that none of its Outside-the-criteria items needs a change "under the agreed stopping rule". I found no comment, claim line or summary entry that records the human agreeing a stopping rule for #63 before run 3. The kit does not carry the rule either (`team/qa-engineer.md` still says that any problem in the Heavy second launch is a FAIL; the drafted patch `2c-heavy-stopping-rule.patch` is not applied). Whether the human agreed it in conversation: **unknown** to me (not in the record). It is a question for you (Q12).

  **1. `team/pm.md`: a rule that reads text states "any" or "all", gives one real example per branch, and carries a replay criterion. Recommend: accept (protected).**
  - *Evidence:* the #63 thread above. The wording gap ("and" read as both, or as either) sat in the groomed body for two days before any code. The criterion asked for a script check on sample JSON, which gave the Engineer no reason to look at real comments. The Design also chose to decide "reflection" by the absence of known markers, which is the fail-open shape the Reviewer named; sweep 5 recorded two earlier guard issues with the same shape (#11 and #99; I took that from sweep 5's text and did not re-check it), so this is the third issue where a list of known forms leaked.
  - *File and sentence:* `_docs/agent-kit/team/pm.md`. About +55 words, for example: "When a check decides from the text of a comment, a file or an input, say whether any one marker or all of them count, and say what the check does with a form nobody listed; prefer a rule that accepts one known good shape over a list of bad forms. Add a criterion that replays the rule over every existing item (paginated read-only GETs) with the expected count of items let through."
  - *Expected effect:* QA FAILs on a text-matching rule fall from two (#63) toward zero, because the first Engineer round meets the real inputs. *Measure:* QA FAILs per Heavy or text-rule issue (2 on #63). *Protection pair:* Reviewer findings of "fails open" on later text rules, and the let-through count the Engineer reports.

  **2. `team/software-engineer.md`: before the first QA, replay a text-matching rule over the full history and put the let-through count in the comment. Recommend: accept with 1; it needs 1's wording (protected).**
  - *Evidence:* QA's FAIL 1 low-severity note that `.scratch/check-63.py` "never saw the real-comment failure", and FAIL 2's whole-repo run. The replay is read-only (`gh api` GETs) and each of QA's runs did it by hand with a new script (`qa-63-*`, `qa-63b-*`, `qa-63c-*`).
  - *File:* `_docs/agent-kit/team/software-engineer.md` (522 words now), about +30 words. *Effect:* the corpus script is written once, by the role that builds the rule, not three times by QA. *Measure:* QA scripts per text-rule issue (at least 12 on #63 across three runs, from the "Commands run" lines; QA-reported). *Protection pair:* QA FAILs, as in 1. Efficiency alone would be unmeasured; this one is paired.

  **3. A stopping rule is agreed with the human before a third run on the same criterion. Recommend: accept in local form now (not protected).**
  - *Evidence:* #63 above: three protected diffs, four QA runs, and no record of when a stopping rule was agreed. Sweep 2's proposal 3 and the epoch patch 2c are the written source for a rule, and 2c is not applied. `sweep.md` already lists "after two QA FAILs in a row" as a trigger for a sweep, but nothing tells the orchestrator to talk to the human at that point.
  - *File:* `.kiro/steering/delivery-pace.md`, item 6, about +45 words: "After two QA FAILs in a row on one criterion, the orchestrator asks the human before the third run: which gaps are accepted, which kinds of finding still fail, and what the decision record will say; the third QA launch is given that list." The kit form is the already-drafted 2c patch (`team/qa-engineer.md`, about +60 words), which the human can approve on its own.
  - *Measure:* number of Heavy issues with a third QA run on one criterion and a recorded agreement before it (0 of 1 on #63 as far as the record shows). *Protection pair:* Medium-or-higher findings after a PASS (`unknown` today) and Reviewer design findings on the same criterion (3 on #63).

  **4. Kiro Web Reviewer and QA are held read-only by the launch message and a check that cannot see ignored paths. Recommend: accept a launch line and an extra check now; ask the human about the listed sub-agent (not protected).**
  - *Evidence (question 2):*
    - In Claude Code the Reviewer is an agent file with `tools: Read, Grep, Glob`, so the tool itself refuses a write (`.claude/agents/reviewer.md`). In Kiro Web, `.kiro/agents/reviewer.json` limits tools to `fs_read` (the file is in the repository), but it is not a listed sub-agent, so the Reviewer runs as a general task. #63's summary says "held read-only by its launch message"; #73, #71 and #80 say "a fresh read-only subagent with the diff pasted in". The only mechanism is the instruction.
    - The check after the fact is `make assert-clean`, which runs `git status --porcelain --untracked-files=all`. It passed after the Reviewer on #19, #54, #63, #73, #71, #20, #80 and #21 (each Reviewer report says so; #17's does not mention it). It cannot see a git-ignored file, and `.scratch/` is git-ignored (`git check-ignore .scratch` prints it). `team/qa-engineer.md` already says the check cannot see ignored files.
    - Did any report write a file? None of the nine Reviewer reports says it did, and #21's says it ran nothing. QA reports list their own `.scratch/` scripts openly (for example `qa-63-probes.py`, `qa-63b-*`, `qa-63c-*` on #63), which the role allows. #17's summary records that "QA's stray private artifact" was deleted at the human's request; what it was and where it sat is **not in the record: unknown**. I found no evidence that a Reviewer wrote anything, and no way to prove it did not for an ignored path.
  - *File:* `.kiro/steering/delivery-pace.md`, about +45 words: the Reviewer launch says "write nothing, not even under `.scratch/`"; the orchestrator lists `.scratch/` file names (a `.scratch/` script, no new make target) before and after a Reviewer launch and reports any change. Whether Kiro Web can list `.kiro/agents/reviewer.json` as a sub-agent is a setting I cannot read; I ask in Q12.
  - *Measure:* Reviewer launches after which the `.scratch/` listing changed (0 known; unmeasured until the listing is taken). *Protection pair:* `make assert-clean` PASS after each Reviewer (8 of 9 reports state it).

  **5. Launch text for QA and Engineer: name no env file in a comment (verdict text is scanned). Recommend: accept; local launch text now, one kit line later (protected).**
  - *Evidence (question 3):* two refusals in this window. #80: QA's first comment post was refused by the secret scan for naming an env file (summary, "What I learned"). #21: the scan refused the text of an env-file name in a QA verdict that said the task file names none; one phrase was reworded and the verdict posted (summary, "Unrelated problems"). Both cost one repost and no lost content. The scanner is working as intended (`secret-patterns.txt` has a pattern for an env-file name); the fix is to avoid the word, not to loosen the scanner. The rule exists only for the orchestrator (`procedures/orchestrator-comments.md`, "Name no env file"); the QA and Engineer role files do not carry it, and the epoch patch 5 that would add a launch line is not applied.
  - *File:* `_docs/agent-kit/team/qa-engineer.md` (675 words now), about +22 words: "Name no env file in a comment; write 'the env file' instead, because the comment scanner refuses the name." Until it is approved, the orchestrator puts that sentence in every QA and Engineer launch message (steering `delivery-pace.md`, item 6, +20 words).
  - *Measure:* scanner refusals of a QA or Engineer comment per issue (2 of 9 issues, both QA, Kiro Web). *Protection pair:* the scanner file unchanged (`git log -- _docs/agent-kit/scripts/secret-patterns.txt` empty in range) and zero secrets found in posted comments.

  **6. The search tool does not index `_docs/`: launch messages and claim-time checks name the shell search. Recommend: accept (not protected).**
  - *Evidence (question 4):* #63's summary records that roles used `grep` through the shell for `_docs/`. That is the only place it is recorded: **per-launch count: unknown**. #63 had up to 9 launches (Engineer 3, QA 4, Reviewer 1, PM 1); I do not know which hit it. The other Kiro issues' summaries and comments do not mention it. Risk I can see: the claim-time check from sweep 5 (an `Orchestrator: Claim` line like "a search of `_docs/decisions/` … found no match", on #63) is only as good as the tool that ran it. If a built-in search ran over an unindexed folder, "no match" means nothing. The comment does not name the tool (I cannot tell which it was).
  - *File:* `.kiro/steering/delivery-pace.md`, about +35 words: "In Kiro Web the search tool does not index `_docs/`: search it with `grep -rn` through the shell, and a claim-time or grooming check of `_docs/` names the command it used."
  - *Measure:* Claim comments that name the search command (unmeasured today). *Protection pair:* criteria found contradicted by a decision record after the claim (0 recorded in this window; 1 caught at the claim on #19).

  **7. Move PM drafts and sweep entries out of `.scratch/` before `make clean-scratch`. Recommend: accept (protected `process.md`, with a local line now).**
  - *Evidence (question 5):* #21's summary: "`make clean-scratch` has not yet run for this issue; it waits for the PM's grooming drafts to be handed over." The PM wrote its drafts for #115, #112 and #122 to `.scratch/` (the PM's output rule; the files are git-ignored), and the orchestrator held the clean-up. They were committed to `_human-tasks/groom-handover-2026-11-13/` on my branch (`41de5c6`) at 10:01Z. The kit's own order is: step 8 of `process.md` runs `make clean-scratch` at the end of an issue, and `sweep.md` has the PM write the sweep entry to `.scratch/` for the orchestrator to copy. So any clean-up run before the copy loses the entry or the draft. #20's summary says its clean-up "covers the `.scratch/` files of #20 and #54", so one run empties the files of more than one issue.
  - *File:* `_docs/agent-kit/process.md` step 8 (3569 words now, always loaded), about +30 words: "Before `make clean-scratch`, list `.scratch/`; copy or commit any PM draft, sweep entry or task file a person has still to see; the command deletes everything." The local line in `.kiro/steering/gate-blocks.md` costs no kit words and can go now.
  - *Measure:* PM drafts or sweep entries lost before hand-over (0 known; 1 close call in 9 issues, which the record shows only as a hold). *Protection pair:* `make clean-scratch` still runs on every issue (summaries state it ran on #63, #73, #71, #80, #20; #19 and #54 planned it), so scratch tokens and logs are still removed.

  **8. Each round-2 or later Engineer launch lists the earlier comments that ask something of the issue and the previous round's comment ids. Recommend: accept, three instances (protected).**
  - *Evidence:* #17 Engineer Reflection 1 and 3 (round 1 missed the orchestrator's note about race 18-3, so QA and the Reviewer raised it and round 2 was needed; the proposal was carried from sweep 5); #54 (round 2's Engineer "had no memory of round 1" and used the issue history); #20 (the final reflection Engineer had "no first-hand record of the earlier rounds"). Different roles, same cause: a resumed or fresh launch does not carry what was asked earlier. This is the same proposal in three issues' words.
  - *File:* `_docs/agent-kit/procedures/orchestrator-comments.md` (343 words now), about +40 words: "Every Engineer launch after the first lists the ids of the earlier Engineer and QA comments and every orchestrator comment that asks something of the issue; re-run `make issue-dump` before the launch."
  - *Measure:* Reviewer or QA findings that repeat an earlier orchestrator request, per issue (1 on #17). *Protection pair:* QA FAILs and rounds per issue.

  **9. `team/qa-engineer.md`: a merge re-check is one command, not two scripts. Recommend: accept (protected; same file as 5).**
  - *Evidence:* #17 QA Reflection: comparing raw diffs after the merge reported a false difference because of hunk offsets, which took a second script (`git merge-tree --write-tree`, compare the tree). #54's QA hit a related trap: `make verify` failed on "test files deleted" only because local `main` was behind `origin/main`, and #54's summary adds that a `git fetch` during a QA run can do the same. Sweep 4's proposal 4 (a merge-base in `make verify`) is that second fix, still unbuilt, and now reported a second time.
  - *File:* `_docs/agent-kit/team/qa-engineer.md`, about +35 words: "To re-check a merge, compare `git merge-tree --write-tree <ours> <theirs>` with `<merge>^{tree}`; equal trees mean the merge added no edits. Do not fetch while a launch runs." *Measure:* `.scratch/` scripts per merge re-check (2 on #17), QA-reported, so indicative only. *Protection pair:* wrongly passed or failed merge re-checks (0 known).
  - The `make verify` merge-base change (`verify.sh`, `verify.md`) stays with sweep 4's proposal 4 and #65/#49; I add this as a second instance in the roadmap line (proposal 10).

  **10. Roadmap: add the second instance to #65/#49's line. Recommend: accept (roadmap, not protected).**
  - *Evidence:* #54's QA found the stale-base verify FAIL (above); #65 is "CI weakened-test check compares a branch's first push with itself" and #49 closes weakened-test gaps. Sweep 4 asked for the merge-base idea for `make verify`; it is not built.
  - *File:* `_docs/planning/roadmap-1-core.md` (supporting list, the #49/#65 entry): one clause naming #54 as the second report and #17's merge re-check. No kit words. *Measure:* QA comments that explain a stale-base FAIL (1 on #54). *Protection pair:* weakened-test check still catches a real deleted test.

  **11. Roadmap: re-time #112 and #115 now that #21 is closed. Recommend: accept (roadmap, not protected).**
  - *Evidence:* both are placed "before #21"; #21 closed at 09:59:03Z with both open; and the long "epoch batch" paragraph in the supporting list still names #63 and #80 as part of a batch that the trial shelving made ordinary. The #131 line and the hand-over line are already on my branch.
  - *File:* `_docs/planning/roadmap-1-core.md`. The new trigger for #112 and #115 is the human's call (suggestion: "before #22"; both touch the contract the integration tests will exercise). No kit words. *Measure:* open issues whose trigger names an event that has already happened (2 now). *Protection pair:* open issues in neither list (0 on my branch).

  **12. Questions for the human, not proposals.**
  - *#19 closed with no Close comment.* **Answered after this entry was drafted (see Rulings, at the end).** The PM could not tell who closed it: #19's thread has 7 comments and none is a Close, and the `closed` event (05:59:34Z) has no commit id. The cause, found by the #19 session and confirmed by the orchestrator reading the whole PR body: PR #118 merged at 05:59:31Z and its body contains the text "the orchestrator closes #19", which GitHub reads as a closing keyword, so GitHub closed the issue at merge. No script or agent bypassed the Close gate; the gate never ran. (The PM's draft said the body "says do not use a closing keyword". That was wrong: the full body, 683 characters, contains "closes #19". A first check by the orchestrator read only the first 600 characters and missed it.)
  - *#63's stopping rule:* was one agreed with you before QA run 3? (See the answer above; the record does not show it.)
  - *`reviewer.json` as a listed sub-agent in Kiro Web:* can you list it? A tool-level restriction beats a launch-message one (proposal 4).
  - *#20's two Close comments:* the first (07:39:19Z) closed it with "Summary: deferred", the second (08:12:25Z) was posted after the summary landed. Fine as a recorded exception; I note it so it is not a surprise in the metrics.
  - *Sweep timing:* "due" was reached at #73 (5th close, 07:00:28Z) and the sweep ran at the 10th. Not a finding; it is the human's choice (`SWEEP_EVERY_N` is a draft value).

  **What the Reflection blocks proposed, and what repeats (question 7).**

  | Issue | Role | Proposal | Where it ends up |
  |---|---|---|---|
  | #17 | Engineer | each launch lists orchestrator asks | proposal 8 |
  | #17 | QA | merge re-check by tree compare | proposal 9 |
  | #54 | PM | `planning.md`: name a gate by the command that runs it | parked (below) |
  | #54 | Engineer | `software-engineer.md`: read `git diff --cached` before committing for unrelated edits | parked (below) |
  | #54 | QA | verify script: show the stale base | proposal 10 (sweep 4's item, second report) |
  | #20 | Engineer | `verify.md`: allow `make test-one` and skip the frontend step for a backend-only change | sent back (below) |
  | #20 | QA | `qa-engineer.md`: a mutation check needs a clean run and a mutated run | parked (below) |
  | #63, #21, #19, #73, #71, #80 | all | none (role not asked) | see "What I learned" lines: #63 gave #122 (shape test, fail closed), #21 none beyond follow-ups |

  Same across issues: (a) the resumed or fresh Engineer without earlier context: #17, #54, #20 (proposal 8); (b) the base moving under a QA run: #54 and #17, plus sweep 4's item (proposals 9 and 10); (c) QA writing a throwaway script because no make target does the job: #17 (merge compare), #20 (mutation run through `make test-one`, whose output hides the result), #63 (corpus and CI-log scripts), the same shape as sweep 5's CI-result target; (d) a long `make verify` for a narrow change: #54 (about 35 s of frontend tests twice and about 93 s of Python for a test-only change) and #20 (about 107 s Python and 37 s frontend for an 18-line change), one proposal only. No two issues proposed the same edit.

  **Parked or sent back, with the reason:**
  - *#20 Engineer, `verify.md` partial run:* the only effect named is time, and it touches the gate. Sent back under Safeguard 4: it returns when it names a protection metric (for example defects that QA's full `make verify` finds after an Engineer partial run).
  - *#54 Engineer, read `git diff --cached` for unrelated line changes:* one instance, cosmetic (a lost space); QA would see it. Park until a second.
  - *#54 PM, `planning.md` "name the gate by the command that runs it":* one instance; the brief's wrong premise was the orchestrator's. The PM caught it in the first read of the Makefile.
  - *#20 QA, mutation check with a clean run:* one instance; sits with theme (c) if it recurs.
  - *#21 follow-ups (UI action buttons, back link style, Reviewer findings 4 and 5, QA Low items):* already in #131, which is placed.
  - *`make issue-comments` (sweep 4/5) and the CI-result target:* still unbuilt; no new evidence this window beyond theme (c); no new proposal.

  **Not done or unknown, for the human:** Medium-or-higher findings after a PASS; files changed outside limits; the model used by any role; active time and tool uses for the Kiro Web issues; the per-launch count of search workarounds; who closed #19; what the "stray private artifact" in #17 was; whether the stopping rule on #63 was agreed before run 3; the human's labels on Reviewer findings (not read). I did not open every comment body.

- **Rulings (added by the orchestrator on 2026-11-13, after the human read the proposals; not written by the PM):**
  - *Q12, #19:* GitHub closed it at merge because PR #118's body contained "the orchestrator closes #19". The human could not recall closing it by hand. The #19 session's decision D5 (post the Close comment with `QA PASS commit: b117d52` and `Merge commit: fbc3950`, leave it closed, no reopening) was approved. Decision D6 was approved as: a steering rule now (`.kiro/steering/delivery-pace.md`, item 8) and a kit proposal at this sweep (proposal 13, below).
  - *Q12, #63's stopping rule:* none had been agreed with the human before QA run 3. The orchestrator's launch message called a rule "agreed with the human": it had taken a Medium-or-higher stopping rule from the previous hand-off summary (stated there for blind second launches), applied it to the first launches as well, and added a clause that gaps a decision record already names do not fail a verdict. The human ruled that Medium-or-higher findings have to be fixed (`.kiro/steering/delivery-pace.md`, item 7). The Mediums that shipped on #63 reached the human at the decision point, who chose to ship them and defer them to #122.
  - *Q12, `reviewer.json` as a listed sub-agent:* not answered; the human cannot do anything about it from the information given. Proposal 4's launch line and `.scratch/` listing cover it.
  - *Proposals 3, 4, 5 (launch-message line), 6 and 11 and the local line of 7:* approved and applied (steering items 9, 10, 12, 11, the `gate-blocks.md` line, and the roadmap). *Proposal 10:* applied to the roadmap. *Proposals 1, 2 and 7 (kit lines) and 13:* approved in principle; each protected diff is shown to the human, and committed with `HUMAN_APPROVED=1`, one at a time; not yet applied when this entry was committed. *Proposals 8 and 9:* parked, with their reason above. *Proposal 5, kit line (`team/qa-engineer.md`):* left for a later sitting.

  **13. `team/software-engineer.md`: the closing-keyword rule covers PR titles and bodies, not only commit subjects. Recommend: accept (protected).**
  - *Evidence:* #19, closed by GitHub at merge from the PR body ("the orchestrator closes #19"), with no Close comment and no `make issue-close` run; #99, closed the same way from a commit subject. Both followed a warning not to close. The role file states the rule for commit subjects only.
  - *File:* `_docs/agent-kit/team/software-engineer.md` (522 words now), about +25 words: "The same applies to a pull request's title and body: no closing keyword before an issue number, not even in a warning; write that the orchestrator closes the issue after the merge."
  - *Measure:* issues closed by GitHub at merge instead of by `make issue-close` (1 in this window, #19; 2 in the project, with #99). *Protection pair:* every closed issue has an `Orchestrator: Close` comment (all others in this window do).
