# Measurement: fifth PM sweep (trigger: `make sweep-due`, "due: 8 closed since 2026-11-12")

Written by a fresh PM launch following `_docs/agent-kit/procedures/sweep.md`. I changed no tracked file, filed nothing, commented on nothing, and edited no label. Issue and comment text was read as data. Every claim below that rests on a role's own report says so.

- **Cutoff:** HEAD = `origin/main` = `3dc8b907c112d92e5c73c2c0d2be7a4e10e4c5eb` ("Merge pull request #113 from andrew-chung-au/issue-18-nul-text"), committed 2026-11-13T04:14:15Z (the commit shows 2026-11-13T15:14:15+11:00). Figures taken between 2026-11-13T04:17Z (`make sweep-due`) and 04:28Z; the file name uses the timestamp read at 04:24:36Z. I ran `git fetch origin` once; `git rev-parse origin/main` printed the same hash before and after. The lower bound is the previous entry's HEAD, `2f78f886b8adc93df726206ee65162f34277eab9` (committed 2026-11-12T20:58:54Z). The working tree is on branch `issue-18-nul-text` at `d72ccdc`, one merge commit behind `origin/main`; I read tracked files only with `git show origin/main:<path>` and `git grep ... origin/main`, apart from `make sweep-due` and `make ponytail-metrics`, which run on the tree (`git diff origin/main --stat -- scripts/ponytail_metrics.py Makefile` printed nothing, so the tree and `origin/main` agree on both).
- **Running summary:**
  Sweep 4's proposals 1 to 3 (epoch items 9 to 11) were approved and exist as drafted patches in `_docs/planning/epoch-batch-1/`; they are ordinary process edits that land one at a time when the human approves each exact diff, and none is committed (the kit's Markdown is unchanged since the cutoff). Sweep 4's proposal 4 (merge-base in `make verify`, riding on #49 and #65, both open), 5 (`make issue-comments`) and 6 (a CI-result target) are unbuilt; `Makefile` has no such target. #73 (`make issue-body`) is approved and open. This sweep covers eight closed issues (#12, #13, #99, #102, #14, #15, #16, #18; 16 QA verdict comments; 2 FAILs, both on #99; one early close, #99). It makes 14 numbered proposals. Five need an exact protected-file or kit diff approved (1, 3, 4's follow-up, 7, 8). Five need none (2, 5 in its local form, 9, 12, and 11 as a new Engineer issue). Four are parked or rejected with reasons (6, 10, 13 as a new proposal, 14 as a file change). Focus next: put #63 and #73 with #71 in one sitting for the human's diff approval before the next Heavy issue; give #107 a tighter trigger before #19; file the contract-sync issue (11) before #21; place #112. Keep the ponytail comparison (separate record, `.scratch/2026-11-13T0424Z-measure-ponytail-review.md`) as the human's evidence; it recommends nothing.

- **Question:** What did the roles learn on the eight issues closed since sweep 4, what do the figures say about cost and protection, and which changes are worth the human's time?
- **Command and commit:** `make sweep-due` (printed "due: 8 closed since 2026-11-12"); `git log 2f78f886..origin/main --diff-filter=A --name-only -- _session-summaries/`; `gh api` REST reads (`.scratch/sweep5-comments.py` for the comment census); `.scratch/sweep5-words.py` for word counts; `make ponytail-metrics N=<n>` (separate record). All at `3dc8b90` unless a line says otherwise.
- **Baseline:** the previous entry's cutoff `2f78f88`. Its word counts are recomputed here with the same script, not read from that entry.
- **Result:** (all at `3dc8b90`; the `2f78f88` column is recomputed by `.scratch/sweep5-words.py`)

  **Summaries added since the cutoff** (ten files; read for Reflection and Launch usage): `…2026-11-12T0847Z-issue-059…`, `…1136Z-planning-orchestrator-handoff`, `…2128Z-issue-012…`, `…2317Z-issue-013-engineer…`, `…2026-11-13T0149Z-issue-099…`, `…0149Z-issue-102…`, `…0249Z-issue-014…`, `…0300Z-issue-015…`, `…0343Z-issue-016…`, `…0410Z-issue-018…`. (#59 and the handoff were added to `origin/main` after the cutoff commit but describe work before it; #59 closed 2026-11-12T08:55Z, so it is not in this sweep's eight.) Closed issues since the sweep-4 entry's time (21:07Z): #12, #13, #99, #102, #14, #15, #16, #18 = 8 by `closed_at` (this is how `sweep-due.py` counts: closed at or after the entry's file-name time; #11 closed 21:00:06Z and belongs to sweep 4).

  **Word counts** (`git show <commit>:<path> | wc -w` equivalent; definition of "core" is sweep 4's, restated: kit top-level `README.md`, `blueprints.md`, `environments.md`, `process.md`, `setup.md`; every `.md` in `team/`, `procedures/`, `templates/`; the two `START.md`; the six role-definition files under `claude-code/agents/` and `opencode/agents/`; 36 files; not counted: the two `skills/sweep/SKILL.md`, `.template` files, scripts):

  | File | `2f78f88` | `3dc8b90` |
  |---|---|---|
  | `AGENTS.md` | 1484 | 1664 |
  | `_docs/agent-kit/process.md` | 3569 | 3569 |
  | `team/pm.md` | 1001 | 1001 |
  | `team/qa-engineer.md` | 675 | 675 |
  | `team/software-engineer.md` | 483 | 483 |
  | Always-loaded total | 7212 | 7392 |
  | Core Markdown (36 files) | 28947 | 28947 |

  The kit did not change. `AGENTS.md` grew by 180 words: `git diff 2f78f886 origin/main -- AGENTS.md Makefile` shows the Seed line and the Ponytail line added, and the Run and Frontend dev server lines reworded (http://127.0.0.1 in place of localhost); `Makefile` gained `seed` and the same URL change. Word counts are tracked, never a gate.

  **QA verdict comments per issue** (owner comments whose first line starts `QA:`, from the census; a Reflection-only `QA: reflection…` comment is not a verdict):

  | Issue | Tier | QA verdict comments | `QA: FAIL` | QA PASS | Notes |
  |---|---|---|---|---|---|
  | #12 | Standard | 1 | 0 | 1 | |
  | #13 | Heavy | 3 | 0 | 3 | first, re-check, second launch |
  | #102 | Standard | 1 | 0 | 1 | |
  | #99 | Heavy | 4 | 2 | 2 | FAIL at `70ad969`, FAIL at `45eca31`, PASS at `805b344`, second launch PASS |
  | #14 | Heavy | 2 | 0 | 2 | first and second launch |
  | #15 | Standard | 1 | 0 | 1 | |
  | #16 | Standard | 2 | 0 | 2 | round 1 and the round-2 re-check |
  | #18 | Standard | 2 | 0 | 2 | first, and the re-check after PR #113 |
  | Total | | 16 | 2 | 14 | |

  Tier for #12 to #18 is from the summaries and claim comments (the PM's proposal; no `tier:` label was on any). **Early close:** #99 `closed_at` 2026-11-13T01:57:37Z, its `Orchestrator: Close` comment 02:15:28Z (17 min 51 s later). The other seven closed 3 s to 12 s after their Close comment, except #16: its Close comment is 03:44:28Z and it closed at 03:47:05Z (2 min 37 s) because the human closed it by hand (comment 03:46:56Z).

  **Launches per issue** (from each summary's Launch usage; Kiro Web gives no time or tool-use figures, so those read `unknown`):

  | Issue | Launches | Detail |
  |---|---|---|
  | #12 | unknown | "Engineer: unknown (figures not available to this launch)" |
  | #13 | unknown | the summary says it launched no subagents (it is the Engineer's own session); the QA launches are not counted there |
  | #102 | 4 | PM 1, Engineer 1, QA 1, Reviewer 1 |
  | #99 | 11 | PM 2, Engineer 4, QA 3 + second 1, Reviewer 1 |
  | #14 | 6 | PM 1, Engineer 2, QA 2, Reviewer 1 |
  | #15 | 4 | Engineer 2, QA 1, Reviewer 1 |
  | #16 | 6 (+3 resumes for Reflections) | Claude Code: Engineer 469 s/34 tool uses and 310 s/26; QA 254 s/24 and 227 s/23; Reviewer 112 s/17; PM 41 s/9. Resume figures: PM 27 s/4, Engineer 32 s/6; the QA resume "264 s, 26 tool uses" may be cumulative or per-resume: unknown. Model unknown to the orchestrator |
  | #18 | 7 | Engineer 3, QA 2, Reviewer 2 (one discarded) |

  **Reflection coverage** (blocks in the summaries): PM 1 of 8 (#16; the other summaries read "unknown (role not asked)"). Engineer 6 of 8 (#102, #99, #14, #15, #16, #18; #12 and #13 read "unknown"). QA 3 of 8 (#99 and #14 second launches, #16; #102, #15 and #18 say QA's comment has no block; #12 and #13 unknown).

  **Protection side of the efficiency figures (Safeguard 4):**
  - QA FAILs: 2 in 16 verdict comments, both on #99 (the two-in-a-row evidence). One early close (#99).
  - Reviewer findings labelled by the human (33 findings on six issues; the labels are in the ponytail record): 13 `useful`, 19 `correct-minor`, 1 `wrong`, 0 `harmful if followed`; QA had already raised 2 of the 33. Five were applied (16-1, 16-2, 16-3, 16-5 and 18-2). Where the Reviewer found a real gap after a QA PASS: #16 (no test that the owner and the `claimed` entry are saved together; detail read after commit) and #18 (a NUL character gave a 500, finding 18-2). I do not score these as "defects after PASS" in the ponytail record's sense; they are listed so the protection side is visible.
  - Medium-or-higher findings after a PASS: `unknown`. A text search for the words in QA comments matched lines I could not tell apart from restated criteria, so I did not count them.
  - Files changed outside the issue's limits: `unknown` (not computed; the metrics script says it does not compute it).
  - Reviewer-prefix problem: found on the first Reviewer comment (`make issue-comment` refuses `Reviewer:`), fixed by one human-approved `AGENTS.md` line on #102's branch.

  **Open issues in neither the Core task list nor the supporting list** (`.kiro/steering/backlog-order.md`; `git show origin/main:_docs/planning/roadmap-1-core.md`, 21 open issues read from `gh api`): **#112** (filed 2026-11-13 after #16; not mentioned in the file). Every other open issue appears in the Core list (#17, #19 to #22) or the supporting list.

  **`.kiro/steering` check:** I read all four files. `delivery-pace.md` item 6 (the interim Heavy second-launch text) is the place proposal 5 touches. `gate-blocks.md` applies to #16's close (below).

- **Caveats:**
  - The eight issues differ in size and tier (Standard 5, Heavy 3), and a Heavy issue carries more launches by design; the tier column keeps the launch table honest. Launch counts include PM follow-up launches (filing #107, #110, #112).
  - #102, #99, #14, #15 and #18 ran in Kiro Web with no tool-use figures; #16 ran in Claude Code; the tool for #12 and #13 is not stated in what I read. The tools differ, so "QA rounds" compare poorly across them.
  - Round counts come from comment census (GitHub) and Launch usage lines (the orchestrator's copy of completion notices). A role did not score its own work, but the Launch usage lines are the orchestrator's report; where a figure's only source is a role's own text I mark it so.
  - `make ponytail-metrics` ran on the tree; it left out #99's commit `45eca31` ("Fix #99 test: …", counted as "mention only") and #14's, #99's and #102's roadmap commits as "shared" or "mention only" (see proposal 7). So #99's test lines may be understated.
  - I did not read every role comment in full. I read the first line of each owner comment on the thirteen issues, the Reflection blocks in the summaries, #16's close and hand-close comments, #63, #73 and #112's presence, and chose by relevance. A detail inside a comment I did not open could change a proposal.

- **Proposals:**

  Epoch rule (sweep 4's "batch" call) no longer applies: the ponytail trial is shelved and `epoch-batch-1` is no longer a batch (`_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`; roadmap 1). Kit files, `AGENTS.md`, `Makefile`, `agent-kit.conf` and `.github/*` are protected (`agent-kit.conf` `PROTECTED`, line 48): each change needs the exact diff approved by the human, then a `HUMAN_APPROVED=1` commit. I drafted no diff. Word changes are my estimates (a sentence of about the stated length), not computed from a blob.

  **1. `pm.md`: re-check criteria against decision records approved after grooming. Recommend: accept, with a second, small check at claim time.**
  - *Evidence:* #16's PM Reflection 2. The groomed criteria said "assignment row"; the approved data-model record (`_docs/decisions/2026-11-12T0834Z-data-model.md`) had dropped that table, and QA had to reinterpret two criteria. The human ruled: the text stays, met as the record reads it. #16 was groomed on 2026-11-09 (comment `6741989528`), the record is dated 2026-11-12, and `delivery-pace.md` item 3 grooms two or three Core issues ahead, so a gap of days is normal.
  - *Why a `pm.md` sentence alone will not fire:* the PM is launched at grooming and at re-record, not at claim. An issue groomed on 11-09 and claimed on 11-13 is not seen by the PM in between. So the cheapest working form is two edits: `_docs/agent-kit/team/pm.md` ("before asking for the label, list the decision records dated after the issue's last grooming and check the criteria against them"; about +30 words, 1001 now) and the claim step in `procedures/orchestrator-comments.md` (run `make decisions` and name any record newer than the `Body sha256` comment; about +20 words). Either alone is weaker. A quick search of the other open groomed issues (#17, #19 to #22, #112) for "assignment" found only #17's out-of-scope line "Reassignment: Should-have", so I found no second instance now; this is one search, not a full check.
  - *Measure:* count of QA "criterion wording" notes per issue (today at least 1: #16). Protection pair: QA FAILs and criteria the human has to rule on after the claim.

  **2. Engineer (#16): a `real_crash_client` fixture in `tests/conftest.py`. Recommend: accept as a small supporting issue; do not fold it into #110.**
  - *Evidence:* #16 Engineer Reflection 3 and Ponytail note ("missed one reuse": `crash_client` already existed). At `origin/main`, `git grep -c raise_server_exceptions=False tests` gives 1 in `conftest.py` and 7 outside it (`test_auth_api.py` 2, `test_claim_api.py` 1, `test_ingest_api.py` 3, `test_notes_api.py` 1). The Engineer counted 6 on the `5985a83` branch; #18's notes test is the seventh, so the number is still growing.
  - *File:* `tests/conftest.py` (a test file under `TEST_FILES`, not protected). *Effect:* new 500-path tests reuse one fixture. No word change in the kit. *Why not #110:* #110 is the ingest-route simplification; its intent is one sentence and this is a different one. A move of the seven existing sites edits test lines; keep it to new tests first, and move the old ones only in an issue that already edits those files.
  - *Measure:* number of inline `raise_server_exceptions=False` outside `conftest.py` (7 now) should stop growing. Protection pair: the verify output line `Assertion lines: N added, 0 removed` stays `0 removed`, and QA FAILs.
  - *Placement:* supporting list, trigger "before #17" (the next Core issue with refusal paths).

  **3. QA (#16): add `make issue-comment` to Commands in `AGENTS.md`. Recommend: accept, one line (about +35 words).**
  - *Evidence:* #16 QA Reflection 1: QA grepped the `Makefile` to find the usage. The command is already described at `_docs/agent-kit/process.md` line 37 (Issue comments) and `AGENTS.md` "Read when" line 73 points to `process.md#issue-comments` for commenting on issues; so the fact exists, QA did not follow the pointer. The Commands list is the place a role looks first. Mis-formed first lines have cost extra rounds before (`.kiro/steering/gate-blocks.md`: #9's two PASS comments), so a visible usage line has protection value, not only speed.
  - *File:* `AGENTS.md` (Commands). *Measure:* `Makefile` greps for `issue-comment` in QA and Engineer transcripts over the next three issues (efficiency, role-reported so only indicative), paired with the count of comments refused or re-posted for a wrong first line (protection; from the `make issue-comment` refusals in the session summaries).

  **4. #99 second QA (`make issue-body`). Recommend: do not open a new proposal; put the existing #73 (and #71) before the next Heavy issue's second launch.**
  - *Evidence:* #99 second-launch QA Reflection 1: a read of `.scratch/issue-99.json` ran into the start of an Engineer comment; the QA disclosed it. #73 already asks for exactly this target: "approved", open, groomed; the supporting list says "before the next Heavy issue's second QA launch if it can". #99 and #14 were the next two Heavy second launches; #73 did not land. So the existing issue needed the human's `Makefile`, `AGENTS.md` and `Makefile.mk` diff approval (with #71), and that did not happen.
  - *Action:* the human reads the #73 and #71 diffs in one sitting (both are in the supporting list as items 11 and 12). Once #73 lands, a QA role sentence ("the Heavy second launch reads `make issue-body`'s file, not `issue-dump`'s") is an ordinary edit (the epoch reason in #73's out-of-scope list is gone); epoch item 2a's launch-message checklist (`_docs/planning/epoch-batch-1/2a-launch-message-checklist.patch`) is the nearest place. Until then, proposal 5's local launch text can carry the instruction.
  - *Measure:* number of second launches whose own comment discloses reading a comment (1 known: #99; I did not read #13's or #14's second-launch comments for this, and #14's disclosed a search leak instead, proposal 5). Protection pair: Heavy second-launch FAILs after a first-launch PASS (none among #13, #99 and #14 since the cutoff: all three second launches passed).

  **5. #14 second QA: blind second launches exclude `.scratch/qa-*`, `.scratch/engineer-*` and `.scratch/issue-*.json` from searches. Recommend: accept in its local form now (add to `.kiro/steering/delivery-pace.md` item 6); fold into epoch item 2a later. Option for the human: run the second launch from a fresh clone, where git-ignored `.scratch/` does not exist.**
  - *Evidence:* #14 second-launch QA Reflection: one broad `grep_search` for a settings name returned lines from files it was told to avoid, so it wrote a disclosure instead of a blind review. The search tool reads the whole tree, including the git-ignored `.scratch/` files of the first QA and the Engineer.
  - *File:* `.kiro/steering/delivery-pace.md` item 6 (not protected; the orchestrator's launch text), about +30 words. Kit form later: `team/qa-engineer.md`, Heavy second launch (675 words now, so about +30). A fresh clone is stronger than an exclude list (the leak cannot happen), but it is an environment change; it is the human's to choose.
  - *Measure:* "forbidden-file lines in search output (target 0)" is QA's own count, so under Safeguard 3 it is role-reported and I mark this proposal **unmeasured** apart from the disclosure line in each second-launch comment. Protection pair: Heavy second-launch FAILs and Medium-or-higher findings after a second-launch PASS.

  **6. #102 Engineer: a `make src-of PKG= FILE=` target to read a locked dependency's source. Recommend: park; one instance, and it would not work where the need arose.**
  - *Evidence:* #102 Engineer Reflection 3. FastAPI was not installed in that Kiro Web session and `uv` could not run; the Engineer read `routing.py` at the locked tag through `gh api`. A `make` target that reads an installed package cannot work in an environment that has none installed, so it would help only where the source is already on disk and `grep`/`read` already work. The human already ruled "kept as evidence; no action now".
  - *Condition to revisit:* a second instance, or a form that fetches the source at the locked tag. *Measure:* number of commands used to read dependency source in an issue (role-reported; unmeasured until a protection pair exists). No file change proposed.

  **7. Commit subjects with "Fix #N" auto-close issues on merge. Recommend: accept a one-sentence rule now; defer the automatic check until a second instance.**
  - *Evidence:* #99 closed 17 min 51 s before its Close comment (comment census above). The cause per the #14 summary: a commit subject began "Fix #99". `git log origin/main -i -E --grep='\b(fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved)\b[: ]+#[0-9]+'` finds exactly one commit in the whole history: `45eca31` "Fix #99 test: a comment naming the table is refused, not a near miss". The launch messages now forbid it, which lives nowhere durable (`git grep` of `_docs/agent-kit`, `AGENTS.md` and `.kiro` for "closing keyword" finds nothing).
  - *Second effect, same cause:* `scripts/ponytail_metrics.py` counts a commit for issue N only when its subject ends `(#N)` and its docstring says no written role rule requires that ending. `45eca31` has no such ending, so the script lists it as "mention only" and leaves its lines out of #99's figures (this is a visible understatement in the ponytail record).
  - *File and sentence:* `_docs/agent-kit/team/software-engineer.md#commits` (483 words now): "End a commit subject with `(#N)`; never write Fix, Fixes, Close, Closes, Resolve or Resolves before an issue number in a subject, a body or a pull-request description; GitHub closes the issue on merge." About +40 words. One sentence covers both the early close and the metric.
  - *Check, deferred:* a script run by `make verify` that scans `git log <merge-base>..HEAD` subjects and bodies for the keyword list. It needs `agent-kit.conf` or `Makefile` and `.github/*` diffs (protected). With one instance in the whole history and a cost of one 18-minute early close that the human caught, I would wait for a second instance.
  - *Measure:* count of commits matching the grep above (1 now; the number should stay 1), and issues closed earlier than their Close comment (1 of 8 now). Protection pair: the Close comment is still posted after QA PASS; QA FAILs.

  **8. #63 (open bug): should it be next in the supporting list? Recommend: yes, #63 first, then #73 and #71 together.**
  - *Evidence:* `make issue-close N=16` refused with "needs 1 owner QA PASS comment(s) at or after the last Engineer commit comment; found 0" because the Engineer's Reflection comment (`6843134115`) names commit hashes; the human closed #16 by hand (comment `6843201264`: "This is the known #63 bug"). The first case was #51. That is two refused closes in two issues that posted such a Reflection (#51 and #16); I did not check whether other issues' Reflection comments named hashes and were still closed by the script. The roadmap's line 54 says "Reflection comments may carry commit hashes again", which #16 shows is wrong while #63 is open.
  - *Weighing:* for #63: it is the only bug in the supporting list that blocks the normal closing path for a correct close; the fix is described in the issue with an evasion refusal criterion (a work comment with a Reflection appended still moves the floor), so it protects the re-check rule rather than loosening it. Against: it is Heavy (it changes the rule that gates every close) and touches `_docs/agent-kit/scripts/issue-close.sh` (protected), so it costs a decision-record approval and a diff read; the hand-close path exists and `.kiro/steering/gate-blocks.md` already covers how to use it. The human's wait is informational (Safeguard 4), so I do not count it as the reason.
  - *Smaller step the human can take now:* correct the roadmap sentence (the orchestrator's file, not protected) so it says that a Reflection naming hashes still refuses a close until #63 lands, or tell roles to put hashes in the summary instead. *Measure:* number of closes done by hand because of #63 (2 known). Protection pair: the evasion case in #63's criteria (a work comment plus a Reflection is still refused).

  **9. The HTTP-layer file-name list in `tests/test_data_audit.py` (#13, #15, future route modules). Recommend: no new proposal; cross-reference #107 and tighten its trigger.**
  - *Evidence:* `tests/test_data_audit.py` lines 513 to 519 at `origin/main`: the allowed set is `{app.py, auth.py, cases.py, errors.py, server.py, __init__.py}`. #13 added `auth.py`; #14 avoided a new name by moving the key dependency into `auth.py`; #15 added `cases.py` by the human's ruling; #16 and #18 added no module. The next likely new module is #19's audit read API (#20 and #17 may reuse `cases.py`). #107's entry in the supporting list already carries "keep the HTTP-layer module list in `tests/test_data_audit.py` in one place" and its trigger is "any time after #99 closes; before Deploy".
  - *Change:* none to #107's content. The human can tighten the trigger to "before the first new route module after #15, which is #19, if #19 adds one", so the #19 Engineer does not need a fourth ruling. No kit or protected file is touched (the roadmap is the orchestrator's). *Measure:* number of rulings on that list per route issue (3 so far: #13, #14, #15). Protection pair: the list stays an exclusion list for a test that fails when data-layer code raises an API HTTP exception, so a wider list is a wider exemption: track its length (6 names now).

  **10. Two QA FAILs in a row on #99: an application guard that lists constructs leaks at the edges. Recommend: no new rule; give #107 the Engineer's guard test; record the lesson.**
  - *Evidence:* #99 FAIL at `70ad969` (an id through a named `bindparam`; a PRAGMA with comments between words) and FAIL at `45eca31` (an id under a compiled bind name; a quoted schema alias before a pragma). #11 (before the cutoff) had the same shape. The orchestrator's stop-listing instruction ended it: ask SQLAlchemy's compiled statement which value goes into `id`, and match pragma names as words. The Reviewer then judged the result over-built (about 60 to 80 lines), so the better design costs code that #107 now removes.
  - *Why no rule:* `team/pm.md` already says to state how a limit is enforced and add a refused case; the failing step was the Engineer's choice of enumeration, on one component, in two issues. A kit rule would be generic advice drawn from one SQLAlchemy guard.
  - *Do instead:* in #107's grooming, add the #99 Engineer's own proposal (a test comparing the hand model of crud names, `id` and `id_m<n>`, with SQLAlchemy's `bind_names` for new forms, as the guard against an upgrade) and the second-launch QA's suggestion to look for forms where the compile path differs from execution (ORM bulk, custom dialects). *Measure:* QA FAILs per Heavy issue on guard criteria (2 on #99, 2 on #11 by first-line count). Protection pair: Reviewer findings labelled `useful` on later guard issues.

  **11. A contract-sync issue: the code now differs from `openapi.yaml` in three named places. Recommend: file one Standard supporting issue, before #21.**
  - *Evidence:* #15 and #16 summaries ("Mismatches with the spec"): `getCase` and `claimCase` declare a 422 the route can never return, and the contract test names it as the one accepted difference; #18: `NoteRequest.text` has no `maxLength` while the code enforces 5,000 characters (the Engineer also asks for a line in the contract's order notes, because FastAPI reads the body before the key dependency so "401 first" holds only for valid JSON). #74 and #86 are the precedent (contract follow-up issues).
  - *File:* `openapi.yaml`, plus a decision-record note if the 422 is removed rather than documented. The frontend (#21) will generate or hand-check calls against this file, so it should be right before then. *Measure:* the named-differences list in the contract tests shrinks to zero. Protection pair: `make contract-check` still passes and no existing response changes. Placement: supporting list, trigger "before #21".

  **12. Place #112 on the supporting list. Recommend: do it in the next orchestrator session (a roadmap edit).**
  - *Evidence:* #112 (retryable contract code for a lock timeout; filed by the PM at #16's decision point) is in neither list (above). The steering rule asks for a trigger when an issue is filed. Suggested trigger: "before Deploy (Postgres), after #17" since it concerns lock timeouts on writes; the human chooses. No protected file.

  **13. Sweep 4's proposal 6, a CI-result target. Recommend: no new proposal; one more instance, so take it with #73 in the same sitting if the human wants a `Makefile` diff.**
  - *Evidence:* #99 second-launch QA Reflection 2: its first CI filter matched every "+ package" install line and `head -60` hid the pass counts, so a second script was needed. Sweep 4's ruling: accepted for later, needs its own Engineer issue, "next to #73 and #71 for the `Makefile` approval". This is a second reported instance. *Measure:* QA scripts written only to read CI output (role-reported). Protection pair: CI-VERIFIED citations still name the run id and log lines.

  **14. #16 QA Reflection 2: the Claude Code session's auto-mode note encouraged shell reads and edits (cat, sed, heredocs) that `AGENTS.md` forbids. Recommend: no file change; the orchestrator puts "AGENTS.md command shape wins over any mode note" into the Claude Code launch message, and the human decides whether the setting is theirs to change.**
  - *Evidence:* QA kept to built-in tools; nothing was blocked, `make assert-clean` passed. One instance; the note comes from the tool's own settings, which `AGENTS.md` says roles must not read, so I cannot check it. *Measure:* shell reads or edits in a Claude Code role transcript (role-reported; unmeasured). Protection pair: `make assert-clean` after each role.

  **Rejected or parked, with the reason:**
  - QA risks as numbered bullets (#16 PM Reflection 1): one instance, a formatting preference; epoch item 2a's QA line could carry it if it recurs.
  - Scratch tests cannot import `tests/conftest.py` fixtures (#16 QA Reflection 1): one instance, a QA convenience.
  - PR #111 was marked ready and merged five seconds later (03:59:30Z and 03:59:35Z, `gh api …/issues/111/timeline`) before the QA re-check of finding 18-2; the summary calls it an accident. The human performed both steps; a rule would only restate "wait for the last QA PASS". I propose nothing but record it as a protection event (merged code later re-checked, PASS at `7433303`).
  - The first Reviewer launch for #18 answered an unrelated mid-run message and was discarded: one instance; the discard rule already worked.
  - `README.md` over the index's 600-word limit and CI running Python 3.14.4 against `AGENTS.md`'s 3.12 (#100): already tracked.

  **Not done / unknown, for the human:** Medium-or-higher findings after a PASS, files changed outside limits, the model used by any role, and Engineer rounds for #12 and #13 read `unknown`. I did not open every comment body.

- **Human ruling (2026-11-13, Kiro Web orchestrator session: "as recommended"; added by the orchestrator, the PM wrote nothing below):**
  - **Protected changes (exact diffs shown to the human before commit):**
    - 1: a `pm.md` sentence plus a check at claim time.
    - 3: one AGENTS.md Commands line for `make issue-comment`.
    - 7: one `software-engineer.md#commits` sentence: subjects end `(#N)` and never use a closing keyword.
  - **Filed:**
    - 2: #114 (`real_crash_client`, after #17).
    - 11: #115 (contract sync, before #21).
  - **Applied now (not protected):**
    - 5: a line in `.kiro/steering/delivery-pace.md` item 6 on what blind second launches exclude.
    - 8: #63 goes first among supporting issues, then #73 and #71 together. The roadmap no longer says Reflection comments may carry commit hashes while #63 is open.
    - 9: #107's trigger moves to before #19.
    - 12: #112 is placed in the supporting list.
  - **Folded into other work:**
    - 4 and 13: covered by #73 and #71, in one sitting.
    - 10: lessons go to #107.
    - 14: a launch-message line only.
  - **Parked:** 6.
- **Carried to sweep 6** (from #17's session summary, which arrived after this sweep's cutoff; not weighed here):
  - Three of #16 and #17's four Reflection proposals are already decided above: items 1, 2 (#114) and 3.
  - **New, for sweep 6:**
    - A one-command check for QA's merge re-checks, so a branch merged after QA is checked the same way each time.
    - Each Engineer launch reads the issue's comments that ask something of the issue. In round 1, #17's Engineer missed the 18-3 request posted on #17.
