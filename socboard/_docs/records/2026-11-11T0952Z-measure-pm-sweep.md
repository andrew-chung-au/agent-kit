# Measurement: second PM sweep (seven issues closed since sweep 1)

Written by the PM role; it proposes, it applies nothing (`_docs/agent-kit/procedures/sweep.md`). Only this file was written, in `.scratch/`; no tracked file was edited, nothing was filed or posted. Named per `_docs/agent-kit/procedures/session-summary.md`.

- **Cutoff:** HEAD `8989fbbb3cfdc2f80f4eac0397831191a87b0f08` (merge of PR #64, "Add session summary for issue #51"), committed 2026-11-11T09:47:48Z (`git show -s` gives 2026-11-11T20:47:48+11:00). Figures were taken from 2026-11-11T09:47Z to 09:52:36Z UTC with HEAD unchanged; `git status --short` was empty before this file was written. The previous entry's cutoff, used as the lower bound, is `f41d503`.

- **Question:** What did the roles learn across the issues closed since sweep 1 (#36, #39, #40, #46, #50, #8, #51), which changes are worth asking the human to approve, and which figures are sound and which are `unknown`? Two proposals the human named (Engineer "unrun checks" list; `origin/main` as the CI weakened-test BASE) are tested against the Reflection blocks.

- **Command and commit:** all at `8989fbb` unless noted.
  - Read: `AGENTS.md`, `_docs/agent-kit/team/pm.md`, `procedures/sweep.md`, `procedures/session-summary.md`, `templates/measurement.md`, and from `_docs/records/` only `2026-11-10T1518Z-measure-pm-sweep.md` (Human ruling and Running summary; no number is copied from it). Also `_docs/agent-kit/team/software-engineer.md`, `.github/workflows/verify.yml`, `_docs/agent-kit/scripts/verify.sh` (BASE handling, lines 3 to 12 and 27 to 71), `agent-kit.conf`, and issues #49, #42 (body and comments).
  - Closed-issue list: `gh api "repos/andrew-chung-au/socboard/issues?state=closed&per_page=100&sort=updated"` (pull requests excluded). Closed after the previous entry: #36 (2026-11-10T16:20Z), #39 (2026-11-11T02:36Z), #40 (02:49Z), #46 (04:17Z), #50 (06:42Z), #8 (08:08Z), #51 (09:46Z). That is 7, matching `make sweep-due` ("due: 7 closed since 2026-11-10"). #27, #7, #25, #24 and #23 were closed before the cutoff and are not in scope. #51 was closed by the human by hand on GitHub.
  - Summaries: `git log f41d503..HEAD --diff-filter=A --name-only -- _session-summaries/ _docs/records/ _human-tasks/`, `git log --all --since=2026-11-10T15:00:00Z --diff-filter=A --name-only -- _session-summaries/`, and `ls _session-summaries/` directly. Scripts: `.scratch/sweep2-comments.sh` (comments and events for the seven issues and #49, output in `.scratch/sweep2-comments.txt`) and `.scratch/sweep2-figures.py` (words, trailers, protected paths, QA verdicts). Also `make sweep-due`, `make kit-check`, `gh api repos/andrew-chung-au/socboard/issues/comments?since=2026-11-10T15:18:00Z` filtered for "Reflection".

- **Baseline:** the previous entry's Running summary and Human ruling. Word counts are compared with the cutoff `f41d503`, recomputed here with the same file groups and not copied.

- **Result** (all numbers at `8989fbb` unless a commit is named):

  **1. Sweep trigger.** `make sweep-due`: `due: 7 closed since 2026-11-10`; `SWEEP_EVERY_N` = 5. The sweep ran after #51, as the human asked. Non-merge commits since `f41d503`: 39; merge commits: 16.

  **2. Session summaries since the cutoff.** One: `_session-summaries/2026-11-11T0943Z-issue-051-orchestrator-screen-behaviour.md` (added in `b0915f5`; found by the git command and by listing the folder; no other file in the folder is dated after 2026-11-10T15:18Z, and `git log --all` shows no other). **The other six closed issues (#36, #39, #40, #46, #50, #8) have no session summary**, so they have no Reflection block and no Launch usage line. Whether their orchestrator sessions happened elsewhere is `unknown`. Their only source here is the role comments on GitHub.

  **3. Reflection blocks.** Only #51 has any: an Engineer comment (6792494473) and a QA comment (posted 2026-11-11T09:43:08Z and 09:43:14Z). The PM block reads `unknown (role not asked)`. The Ponytail reviewer wrote none (by its rules). Across the other six issues, a search of every comment since 2026-11-10T15:18Z for "Reflection" finds nothing but those two. So the evidence for every proposal below comes from one issue.

  **4. QA verdicts posted on GitHub** (comments starting `QA: PASS` or `QA: FAIL`; tooling-derived from comment text and events):

  | Issue | Tier (PM proposal; no `tier:` label) | QA verdicts, in order | Notes |
  |---|---|---|---|---|
  | #36 | Standard | PASS, PASS | Both at `d8901b1`; the second added a `make verify` run the first could not do |
  | #39 | Standard | PASS | The comment says criterion 7 (`make verify`) was NOT RUN, so "the overall result is not confirmed" |
  | #40 | Standard | PASS | none |
  | #46 | Heavy | PASS, PASS, PASS | `b9ba353` (the comment says the second Heavy launch "will fail" a README item), re-check at `8bc759e`, and a fresh Code review launch at `8bc759e`; criteria needing `make test`, Vitest, Docker and CI are marked HUMAN-VERIFIED / NOT RUN |
  | #50 | Standard | PASS | none |
  | #8 | Standard | PASS | One criterion (build and bundle search) HUMAN-VERIFIED / NOT RUN |
  | #51 | Standard | PASS | 26 mutations, 21 caught, 5 survived, all reported; CI used as the runner under a one-time exception |

  Posted: 0 FAIL, 10 PASS verdict comments over 7 issues. Issues needing more than one QA launch: 2 (#36 re-check, #46). **Reopen events: 0** on all seven (`gh api .../issues/<n>/events`). A QA comment headed PASS that also lists NOT RUN criteria appears on #39, #46, #8 and #51; I note it and score nothing. Open issue #42 (item 3) already asks how QA should report such a criterion.

  Post-PASS findings by another route (protection figure): the #51 shadow review (Ponytail, Phase 1) gave 6 findings after QA PASS, 3 of which QA had not raised (1, 4, 6); the summary records the human's labels (51-1, 51-4, 51-6 "useful correctness-risk"; 51-3 "correct-minor correctness-risk"; 51-2, 51-5 "correct-minor scope"). Follow-ups #62 and #60 exist. Those labels come from the orchestrator's own summary, so they are reported, not independently verified. Defects after PASS for the other six issues: `unknown` (reopen events are the only source checked).

  **5. Post-approval body changes.** Only #46 had `Orchestrator: confirm` comments with a PM re-record (2 rounds: after the first QA launch and after the human's decision of 2026-11-11). #8 was re-groomed and relabelled after the human split it (#51 is the other half); #36, #39, #40 and #50 show approve/unapprove/approve label events but no Confirm comment. Count with Confirm plus re-record: 1 of 7.

  **6. Word counts** (`git show <commit>:<path> | wc -w`; tracked, never a gate):

  | Group | At `f41d503` | At `8989fbb` | Change |
  |---|---|---|---|
  | `AGENTS.md` | 1231 | 1329 | +98 |
  | `process.md` | 3569 | 3569 | 0 |
  | `team/pm.md` | 966 | 1001 | +35 |
  | `team/qa-engineer.md` | 675 | 675 | 0 |
  | `team/software-engineer.md` | 468 | 483 | +15 |
  | **Always-loaded total** | **6909** | **7057** | **+148** |
  | Core Markdown (kit top level, `team/`, `procedures/`, `templates/*.md`, both `START.md`, six tool role files; 35 files at both commits) | 28794 | 28893 | +99 |
  | Project-side role files (`_docs/team/reviewer.md`, four `.claude/agents/`, four `.opencode/agents/`) | 1363 | 1363 | 0 |

  The kit-side +99 includes `team/pm.md` +35 and `team/software-engineer.md` +15 (sweep 1 proposals 1 and 3, `17e725e`) and the rest in `procedures/orchestrator-comments.md` and `environments.md`; the split of the remaining +49 was not counted. `AGENTS.md` +98 is from #46 (`ec82ccf`, `6206210`); split not counted. Efficiency metric with protection pairing: none; no proposal below is justified by words.

  **7. Kit state.** `make kit-check`: derivative of 1.10, claim `1.10+socboard.1` is correct. Modified: `blueprints.md`, `claude-code/settings.json`, `environments.md`, `environments/local-sandbox/push-check.Dockerfile`, `procedures/orchestrator-comments.md`, `process.md`, `team/pm.md`, `team/software-engineer.md`. Drift: `.devcontainer/setup.sh`, `.github/workflows/verify.yml`. Two hook files "not checked here (human compares from the clean clone)". Exit status 1 (`make: Error 1`) is expected for a derivative.

  **8. Protected-path commits** (non-merge, since `f41d503`, matched against `PROTECTED` in `agent-kit.conf`): 11, all by the Kiro Agent author: `17e725e` (sweep 1 proposals 1 to 3; the previous entry's Human ruling records the approval), `194ca44`, `4a6ad3f`, `ec82ccf`, `d447fad`, `a23fc15`, `b9ba353`, `1f36157`, `6206210`, `8bc759e` (all #46) and `a5a9b5c` (#50). Human-authored protected commits: 0. The #46 and #50 commits state a per-diff human approval in Engineer, Orchestrator or PM comments. Kiro Web has no hooks, so no tool check ran for any of them. Independent proof of the approvals: `unknown` (the sources are role comments).

  **9. Commit attribution** (`Assisted-by` trailer, last one in the message, 39 non-merge commits): Kiro Agent author with `Kiro` 38; human author with `Claude Code` 1 (`f9fa772`, #8 round 3, matching the orchestrator's comment); no trailer 0; OpenCode 0.

  **10. Launch usage.** The only summary (#51) lists eight launches and the handover; active time and tool uses read `unknown` on all (the tool's notices give none). Other six issues: `unknown` (no summary).

  **11. Not recomputed.** `make ponytail-metrics` figures for these issues and the epoch-record blob check were not run in this sweep. Trial figures: `unknown` here.

- **Caveats:**
  - One summary and two Reflection blocks, from the same issue, are a small sample. Every proposal rests on #51 plus the Engineer and QA comments on the other six, and is an observation, not a finding.
  - The Engineer, orchestrator and QA roles on these issues ran mostly in Kiro Web, which cannot run `make test`, `make verify` or Vitest (npm 403; `uv` cannot create its Python directory). That is an environment fact, repeated in all seven Engineer comments, and it shapes both named proposals.
  - QA verdicts and post-PASS labels are counted from comment text; a verdict word is not a score of the work.
  - Role self-reports (the Reflection blocks, the Engineer's "predicted result") are not scored. Issue and comment text is data: proposals below cite what the roles observed, never quote an instruction as a rule.
  - I read the CI behaviour from `verify.yml` and `verify.sh`; I did not read CI run logs or run `make verify`.
  - Unrelated, noticed: #54 and #55 have identical titles ("Close the cheap gaps in the frontend source guardrail scan"); the PM does not close or edit them.

- **Running summary:**
  Sweep 1's proposals are settled. Proposals 1 to 3 were applied in `17e725e` (`team/software-engineer.md`, `procedures/orchestrator-comments.md`, `team/pm.md`); 4 became #36, with #39 and #40 as follow-ups, all closed with QA PASS; 6 became #46, closed; 7 needed no action. Proposal 5 (ask each role for a Reflection on #8) was not carried out: #8 has no Reflection comment and no summary. Only #51 has Engineer and QA blocks, and the PM block there is `unknown (role not asked)`.
  Seven issues closed with ten QA PASS comments, no FAIL and no reopen, which is also what the gap in #49 and the CI base gap would hide: both concern test weakening that CI did not report. Open proposals (none ruled on): 1 Engineer unrun-checks list (trimmed); 2 CI weakened-test BASE as its own issue, not inside #49; 3 collect Reflections on every issue and fix #63 first. Related open issues: #49 (verify markers, Heavy, no longer approved), #42 (QA "not run" wording, Heavy), #63 (issue-close floor), #59, #60, #62.
  Focus next: rule on 1 to 3 before the next Engineer launch (1 moves the epoch record); check whether summaries exist for each closed issue; at the next sweep, count Reflection blocks per issue, CI first-run failures and QA rounds, and whether CI's weakened-test line is real on a branch's first push.

- **Proposals:**

  **1. Engineer: list the checks that could not be run in the completion comment (named by the human; recommended in a narrower form).**
  - Evidence: the #51 Engineer's Reflection (its line 3) proposes "If tests cannot run in this environment, list each unrun check and name the one most likely to fail", because it had no feedback loop, wrote a long "Prediction" section and still needed a ninth commit (`c8f4282`) for a timer-test teardown order bug it found only by rereading. What the other issues show: all seven Engineer comments (#36, #39, #40, #46, #50, #8, #51) already say `make verify` or `make test` did not run in Kiro Web, and six name what was not run (#36 as a bullet list, #39 and #46 as "Not run" / "Also not run" sentences, #40, #50 and #51 in a sentence). So the list already appears without a rule, in different places. The "most likely to fail" half has thin support: on #51 the four predicted risks (router error boundary, Radix polyfills, duplicate 409 text, build tree-shaking) did not occur, and the actual defect was not predicted; on #8 the first CI run failed because `guardrails.test.ts` threw at load under jsdom (`new URL("..", import.meta.url)`), and whether the Engineer had flagged that file as the risk is `unknown`. Evidence is one issue's Reflection plus comment reading.
  - File: `_docs/agent-kit/team/software-engineer.md`. The Reflection names a "Verify" section; the file has none (Verify is a bullet and the procedure `procedures/verify.md`). The place is the Definition of done bullet that already asks for "the verify result and what you did, with one line per acceptance criterion". Suggested addition to that bullet: ", and a list of each check you could not run here, with the reason". Protected kit file; the human applies it. It is on the epoch list, so it moves the epoch start.
  - Expected effect: the list is in a fixed place the QA and orchestrator can find, in every tool. Drop "name the one most likely to fail" until a sweep shows a predicted risk that came true. Word change: about +15 (483 to about 498); the full wording would be about +30.
  - Measure: share of Engineer comments with a list of unrun checks in the fixed place (baseline: 7 of 7 say verify did not run, 6 of 7 name what; placement varies). Protection metrics: CI first-run failures (baseline: #8 round 1 failed, #51 none; the other five `unknown`), QA rounds per issue, and defects after PASS. Words are not a target.
  - Overlap: #42 item 3 asks that QA report a criterion that cannot run as "not run" and not as passed (the same unrun-check idea on the QA side). They touch different files (`qa-engineer.md`); they can proceed separately.

  **2. CI weakened-test BASE: make the push run compare with `origin/main` (named by the human); a separate issue is recommended, not #49.**
  - Evidence: the #51 QA Reflection (its lines 1 and 2): CI's "Weakened tests" line said "No test files changed" even in mutation batch 4, where QA had added skip and focus markers to four test files; mutations 4.3a to 4.3c (skips) passed CI and QA had to write `.scratch/qa51-limits.sh` to check by hand. The code agrees with this reading: `.github/workflows/verify.yml` passes BASE = `origin/<base_ref>` on `pull_request`, but `github.event.before` on `push`; on a branch's first push `before` is all zeros, and `_docs/agent-kit/scripts/verify.sh` (lines 11 to 12) turns that into the branch's upstream or `HEAD`, so the diff is empty. Later pushes compare only with the previous tip, not with `main`. The human ran `make verify BASE=origin/main` for #51 (51 assertion lines added, 0 removed), which the summary says is what actually tested it. What I did not check: whether the CI run of PR #58 (a `pull_request` event, base `origin/main`) reported its weakened-test line correctly; that is a different event from the mutation pushes.
  - A caveat on the exact text: a literal `origin/main` on every push would make a push to `main` compare `main` with itself (empty diff) and lose the check there. The fix needs a branch test, for example `origin/main` when the ref is not `main` and `github.event.before` when it is, or the merge-base. The Engineer and the human pick the form.
  - File: `.github/workflows/verify.yml` (protected; it already shows as drift in `make kit-check`). A YAML change, so no word-count effect.
  - Expected effect: a pushed branch with `.skip(` in a test file makes CI fail instead of printing "No test files changed".
  - Measure: re-push QA's mutation 4.3c on a throwaway branch; CI must fail where it passed before (QA's own measure). Protection metrics: the CI run on `main` after the next merge must stay green and report the true diff (no false fail), and changed paths outside limits (`.github/workflows/verify.yml` only).
  - **How it overlaps #49 and where it belongs.** #49 is about *what the check matches*: the six Vitest markers, the Vitest config files and the `"test"` script, in `verify.sh`, `verify.md` and `agent-kit.conf`, as a Heavy issue with an open "kit upstream or local deviation" decision and no drafted design. This proposal is about *what the check compares against* in CI. Both end in "CI says PASS and a weakened test slipped through", and #51's missed mutations (`.skip(`) were markers the current list already matches, so they were missed because of the base, not the marker list. The two are independent: fixing the base does not need the new markers, and the new markers do not help while the base is empty. PM already added the CI-base scope to #49 in a comment on 2026-11-11T09:35Z, and the human's session note says to fold it in. My recommendation is a separate small issue, for four reasons: different file (`.github/workflows/verify.yml`, which #49's Files list does not include, so folding in would change an approved scope and need a new hash and Confirm), different layer (project CI wiring rather than the kit's `verify.sh`), no upstream-kit question to wait on (#49's fifth criterion), and an own checkable criterion (the 4.3c re-push). #49 should link to it. Tier: Heavy by the "higher tier in doubt" rule (it changes the gate every issue passes through; #46 changed the same file as Heavy), human may set a lower one. If the human keeps it inside #49, the issue body needs the file and the criterion added before the label. Note that #49's `approved` label was removed on 2026-11-11T05:23:37Z and has not been restored.

  **3. Collect Reflection blocks on every closed Standard or Heavy issue, after #63 is fixed (supported by the sweep's own gaps; no kit text).**
  - Evidence: of the seven closed issues, one has a session summary and Reflection blocks (2 role blocks: Engineer and QA, and the PM block reads `unknown (role not asked)`). Sweep 1 approved collecting PM, Engineer and QA Reflections for #8; #8 has none and no summary. When it was done on #51 the Engineer's reflection comment named commit hashes, so `make issue-close N=51` refused ("needs 1 owner QA PASS comment(s) at or after the last Engineer commit comment; found 0") and the human closed #51 by hand; the summary records this and #63 is open. Reflections are required after QA PASS (`procedures/session-summary.md`, Reflection), so the order QA PASS, Reflection, close conflicts with the script until #63 lands. Source is the orchestrator's summary and the issue comment trail.
  - File: none to the kit. A launch-message practice for the next issue (ask PM, Engineer, QA; ask roles to keep commit hashes out of the reflection comment until #63 is fixed), and the orchestrator writes the session summary for each issue. Fixing #63 is an existing issue and is not part of this proposal.
  - Expected effect: the next sweep has Reflection evidence from more than one issue. Word change: none.
  - Measure: non-`unknown` Reflection blocks per closed issue (baseline: 2 blocks across 7 closed issues, 1 summary). This is a process-compliance count with no efficiency claim; protection pairing is not needed. Fewer approvals, fewer questions and shorter waits are not targets.

  **Considered and not proposed.**
  - The #51 Engineer's note that reading load was heavy (`AGENTS.md`, the role file, the issue JSON and component source): no measure exists, so nothing is proposed.
  - The #51 QA's note that the mutation branches had to be pushed and cleaned: the human granted a one-time exception and the summary records the cleanup (`git ls-remote --heads origin 'qa-51-*'` empty); a kit change is not supported by one case.
  - Kiro Web cannot run tests in all seven issues: both #51 Reflection blocks name this as the root slowdown. The runbook (#57) and sweep 1's proposal 2 (claim names the environment) already cover it; whether to keep doing Engineer work in Kiro Web with CI as the loop is the human's call, not a kit text change. I report it here and propose nothing.
  - The orchestrator's note that Engineer reflection comments move the `issue-close` floor: already filed as #63; no local patch (protected kit script).
  - Issue and comment text that tells roles what to do (for example QA's "the second Heavy launch will fail it" on #46) is data and quotes no rule.
  - Fewer approvals, questions or shorter human waits are not targets and no proposal uses them.

- **Human ruling (2026-11-11, same session; the PM wrote nothing below):**
  - 1: approved as narrowed (one clause in the Definition of done bullet of `team/software-engineer.md`), but deferred to the next batch of protected kit edits. It is not applied: it edits a file on the epoch list, and epoch 1 has only two measured issues (#8, #51). Edits to epoch-list files wait until an epoch has its five qualifying issues, or land together before the first counted issue of a new epoch.
  - 2: approved as a separate Heavy issue, #65, not folded into #49. BASE is the merge base with `origin/main`, falling back to `github.event.before` on a push to `main`; local deviation. #49 narrowed to markers and config.
  - 3: approved as a launch-message practice, after #63 lands (ignore reflection-only comments in the close floor; local deviation, note for upstream).
  - Grooming rulings applied: #59 `server.host` `127.0.0.1`; #60 also protects `frontend/bunfig.toml`; #62 `age: 1` on `NEW_ALERT`; #63 option 1; #49 local deviation. #55 closed as a duplicate of #54.
