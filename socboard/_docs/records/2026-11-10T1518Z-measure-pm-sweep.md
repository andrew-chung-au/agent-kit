# Measurement: first PM sweep (ponytail epoch 1, before the first counted issue)

One file per repeatable check of quality or cost. This is the first sweep: no earlier sweep entry exists, so nothing here is carried over from one. Written by the PM role; it proposes, it applies nothing (`_docs/agent-kit/procedures/sweep.md`).

- **Cutoff:** HEAD `f41d503fc937de67f436f8492c0e28a77e4b902d` (merge of PR #34), committed 2026-11-10T15:09:58Z (`git show -s --format=%cI` gives 2026-11-11T02:09:58+11:00). Figures were taken from the sweep start, 2026-11-10T15:11Z, to 15:18:15Z, with HEAD unchanged.

- **Question:** What did the roles learn across the five issues closed so far (#7, #23, #24, #25, #27) and the planning sessions, and which changes, if any, are worth asking the human to approve before the first counted issue (#8)? Which figures are sound and which are `unknown`?

- **Command and commit:** all at `f41d503` unless noted.
  - Read: `AGENTS.md`, `_docs/agent-kit/team/pm.md`, `procedures/sweep.md`, `procedures/session-summary.md`, `templates/measurement.md`; the six files in `_session-summaries/`; `_docs/records/2026-11-10T1506Z-measure-ponytail-epoch-1-start.md`; the "Handoff for the next session" in the #27 summary; two human tasks (pinned-file location; which findings to raise upstream). The other 11 files in `_human-tasks/` were listed, not read.
  - Role comments: `gh api --paginate repos/andrew-chung-au/socboard/issues/<n>/comments` for #7 (12 comments), #23 (6), #24 (6), #25 (13), #27 (6), and PR-issue #2 (1, an owner note, not a role comment). Events: `gh api .../issues/<n>/events` (`.scratch/sweep-events.sh`). Open issues #8 to #22 and #31 were not read: the procedure asks only for closed issues.
  - Git history: `git log` over all 84 commits; `.scratch/sweep-trailers.sh`, `.scratch/sweep-protected.sh`.
  - Words: `git show <commit>:<path> | wc -w` (`.scratch/sweep-words.sh f41d503` and `... 6211f95`).
  - Trial figures: `make ponytail-metrics N=7`, `N=23`, `N=24`, `N=25`, `N=27`. Also `make sweep-due`, `make kit-check`, `git ls-tree --abbrev=7 f41d503 <paths>`.

- **Baseline:** none. This is the first sweep. The comparison point for words is the kit import commit `6211f95` (kit 1.10+socboard.1), recomputed here, not copied.

- **Result** (all numbers at `f41d503` unless a commit is named):

  **1. Sweep trigger.** `make sweep-due` prints `due: no sweep recorded`. Closed issues: 5 (#7, #23, #24, #25, #27), equal to `SWEEP_EVERY_N` = 5. Session summaries: 6 (4 planning, 2 issue). Commits: 84, of which 48 non-merge since `6211f95`.

  **2. Word counts** (always-loaded files, then core Markdown; tracked, never a gate):

  | Group | At `6211f95` | At `f41d503` | Change |
  |---|---|---|---|
  | `AGENTS.md` | 1139 | 1231 | +92 |
  | `process.md` | 3569 | 3569 | 0 |
  | `team/pm.md` | 966 | 966 | 0 |
  | `team/qa-engineer.md` | 675 | 675 | 0 |
  | `team/software-engineer.md` | 468 | 468 | 0 |
  | **Always-loaded total** | **6817** | **6909** | **+92** |
  | Core Markdown (kit top level, `team/`, `procedures/`, `templates/*.md`, both `START.md`, the six tool role files; includes the always-loaded kit files) | 28794 | 28794 | 0 |
  | Project-side role files (`_docs/team/reviewer.md` 744; `.claude/agents/` pm 85, qa 70, engineer 97, reviewer 75; `.opencode/agents/` pm 79, qa 66, engineer 69, reviewer 78) | 466 | 1363 | +897 |

  The +92 in `AGENTS.md` comes from four commits (`2587282` planning repoint, `7f5411e` Trial-metrics line, `4f0792f` Layout line, `66eab17` two frontend Commands lines); the split between them was not counted. The +897 is the Reviewer role (744 words) and its two pointers (153). No kit file changed after the import. Per-file counts are in `.scratch/sweep-words.sh` output; efficiency metric with protection pairing: none (words are tracked only; no proposal below is justified by words).

  **3. QA verdicts posted on GitHub** (protection figures; tooling-derived from comment text and events):

  | Issue | Tier (PM proposal; no `tier:` label exists) | QA verdicts, in order | FAIL causes |
  |---|---|---|---|
  | #7 | Standard | PASS | none |
  | #23 | Standard | PASS | none |
  | #24 | Standard | FAIL, PASS | a criterion (the "Generated" constant) not implemented and not mentioned in the Engineer comment |
  | #25 | Heavy | FAIL, PASS, FAIL, PASS, PASS | first launch: a criterion (Kiro answer) recorded "not checked yet"; second launch: shell allow-patterns, a file outside Constraints, out-of-date docs, an unverified format |
  | #27 | Standard | PASS | none posted. The close comment and the #27 summary also record one earlier FAIL (QA's environment had no bun, no defect); that FAIL has no GitHub comment, so it is orchestrator-reported only |

  Posted: 3 FAIL, 7 PASS. Issues needing more than one QA round: 2 of 5 on GitHub (#24, #25), 3 of 5 counting the #27 environment FAIL. **Reopen events: 0** on all five issues. Defects found after PASS by any other route: `unknown` (no source other than reopen events was checked).

  **4. Body edits after approval** (from `Orchestrator: confirm` and `PM: re-recording` comments): #7 (re-scope after the Lovable template change), #23 (path spelling), #25 (Files line). 3 of 5 closed issues, each with a Confirm comment and a PM re-record. #27's body changed before the label, so it needed only a PM re-record.

  **5. Trial figures** from `make ponytail-metrics` (raw values; `engineer`/`qa` elapsed include idle time):

  | Issue | Criteria | QA PASS commit | Counted commits | Non-test lines | Lines per criterion | Tests added | Engineer elapsed | QA elapsed |
  |---|---|---|---|---|---|---|---|---|
  | #7 | 8 | `4f0792f` | 3 | 28 | 3.50 | 0 | 1 h 6 min | 0 h 50 min |
  | #23 | 8 | `72e35df` | 2 | 126 | 15.75 | 0 | unavailable | 1 h 45 min |
  | #24 | 8 | `8330f05` | 3 | 304 | 38.00 | 15 | unavailable | 2 h 22 min |
  | #25 | 9 | `4f33407` | 9 | 106 | 11.78 | 0 | unavailable | 2 h 33 min |
  | #27 | 13 | `ecf7965` | 11 | 4919 | 378.38 | 2 | 0 h 26 min | 0 h 55 min |

  #7 and #27 are outside the trial (Lovable scaffold exclusion); #23, #24 and #25 are trial plumbing. None is a counted issue, so none is a baseline. Reliability: the #7 row counts `d15ba98` (a 2026-11-09 commit whose message says "#7" about the old draft backlog), and the #27 row counts `35eb30b` and `1562ee9` (a planning commit and the #7 session summary). Both rows are therefore overstated and are `unknown` as measures of those issues. #27's figure also includes the 4798 lines deleted with the removed shadcn files. Not computed by the script: reviewer time, files outside Constraints, defects after PASS, invariant violations.

  **6. Commit attribution** (`Assisted-by` trailer, 48 non-merge commits since `6211f95`): Kiro Agent author with `Assisted-by: Kiro` 30; human author with `Claude Code` 12; human author with `Kiro` 2 (`8e514a0`, `f34b65e`; the human made these on the orchestrator's instruction, so the trailer is wrong, as the #27 summary admits); human author with no trailer 4 (`7f5411e`, `f6fb87e`, `fab3dd3`, `90638ad`). OpenCode commits: 0, so the OpenCode commit-line check has not run.

  **7. Protected-path commits.** Six non-merge commits by the Kiro Agent author touch protected paths since `6211f95`: `ecf7965` (`.devcontainer/setup.sh`), `66eab17` (`AGENTS.md`), `f1c36ab` (`Makefile`), `4f0792f` (`AGENTS.md`), `dbde225` and `3d459e2` (`.claude/agents/reviewer.md`, `.opencode/agents/reviewer.md`). Each has an approval statement in an Engineer, Orchestrator or summary text. Kiro Web has no hooks, so no tool check ran for any of the six. Independent proof of the approvals: `unknown` (the only sources are role reports). Human-authored protected commits: `7f5411e`, `4f5365e`, `d913e19`, `2394da6`, `2587282`, `90638ad`.

  **8. Epoch record check.** The blobs listed in `_docs/records/2026-11-10T1506Z-measure-ponytail-epoch-1-start.md` for `AGENTS.md`, `process.md`, the three `team/` files, `_docs/team/reviewer.md`, the three `.claude/agents/` role files, both reviewer pointers, `.kiro/agents/reviewer.json`, `scripts/ponytail_metrics.py`, the pinned file and the protocol all match `f41d503` (`git ls-tree --abbrev=7`). `git diff --stat a1d37ba f41d503` shows 3 files, 65 lines, all docs. So the provisional epoch start `a1d37ba` still holds. **Accepting proposal 1, 3 or 4 below would change a listed file (or the metrics script) and move the start to the commit that lands it.** That costs no data yet.

  **9. Kit state.** `make kit-check`: derivative of 1.10, claim `1.10+socboard.1` correct; modified kit files `blueprints.md`, `process.md`, `team/software-engineer.md`, `claude-code/settings.json`; drift `.devcontainer/setup.sh` (bun pin, #27) and `.github/workflows/verify.yml`. Exit status 1 is expected for a derivative.

  **10. Upstream.** `agent-kit#187` (`issue-comment.sh` discards gh's stderr) is open (`gh api repos/andrew-chung-au/agent-kit/issues/187`). The attribution/Kiro-layer finding is still held.

  **11. Launch usage and reflections.** Every Launch usage line across the six summaries gives active time and tool uses as `unknown`; all PM, Engineer and QA Reflection blocks read `unknown (role not asked)`; the only filled Reflection blocks are the orchestrator's (five of six summaries; the kit-import summary says `unknown (role not asked)` for the orchestrator too). Non-orchestrator blocks: 11, all `unknown`. Time per role therefore comes only from the coarse script figures above.

- **Caveats:**
  - First sweep: no trend exists, and five issues (three of them plumbing for the trial itself) is a small sample. Every correlation below is an observation, not a finding.
  - Many facts about how work went (breaches of the clean-clone rule, a pasted diff run as commands, an inline `python3 -c`, parallel tool calls) appear only in the orchestrator's own summaries. They are role self-reports and are not scored or counted here.
  - "Engineer" on #7, #23, #24, #25 and #27 was the orchestrator working in Kiro Web, and QA ran as general sub-agents (Kiro Web) or in Claude Code; the roles are not independent launches, so Reflection "role not asked" often has no separate role to ask.
  - Elapsed times come from comment timestamps of one GitHub login and include idle time. Time, words and tool uses are efficiency figures and appear here only as information; each is paired with a protection figure (QA rounds, reopen events, changed paths outside limits) where a proposal relies on them.
  - Changed paths outside limits are not computed by any tool. The only sources are QA comments: #25 (the Kiro agent file and the decision record file were outside the Files list; fixed by an approved amendment before PASS) and #27 (`.devcontainer/setup.sh` and `AGENTS.md`; QA could not verify a separate approval for `setup.sh`).
  - Process note: the first fetch of issue comments ran as a single inline loop with `$` variables, which the command-shape rule forbids; every later multi-step check is a script in `.scratch/`. Nothing outside `.scratch/` was written.

- **Running summary:**
  The first sweep reads the project's first week: planning and kit import (6 summaries), trial plumbing (#23 to #25), the frontend review (#7) and the static build (#27). The trial's first counted issue is #8, not yet started. Epoch 1 is provisional at `a1d37ba`, and the record's blobs still match `f41d503`.
  Open proposals (none ruled on): 1 per-criterion status in the Engineer comment; 2 environment and tools in the claim comment; 3 PM checks for existing decisions and the decision-record path; 4 fix the metrics script's commit matching before #8; 5 collect role reflections on #8; 6 decide where frontend tests run in CI and the push check; 7 whether to file the held attribution finding.
  Focus next: rule on proposals before #8's Engineer launch, since 1, 3 and 4 move the epoch start; re-groom #8 per the handoff; confirm each reviewer tool can read the pinned file. At the next sweep, check #8's QA rounds, whether the Engineer comment listed every criterion, and whether any protected commit lacks a recorded approval. Defects after PASS and independent approval proof stay `unknown` until a source is named.

- **Proposals:**

  **1. List every acceptance criterion's status in the Engineer's completion comment.**
  - Evidence: on #24 the first QA FAIL was a criterion (the Lovable "Generated" constant) the Engineer comment never mentioned; on #25 a criterion (record whether Kiro has an agent file) was "not checked yet" in the Engineer's comments yet the work went to QA. The Engineer comments on #7, #23 and #27 gave per-criterion status or said what was not shown, and none of those three had a QA FAIL caused by an unmentioned criterion. Five issues, one Engineer (the orchestrator) throughout: weak evidence.
  - File: `_docs/agent-kit/team/software-engineer.md`, Definition of done, one bullet: "each acceptance criterion marked met, not met or not checked, with a pointer to the evidence". Protected kit file; the human applies it. It is on the epoch list.
  - Expected effect: a criterion that is unfinished or unchecked is seen by the Engineer and the orchestrator before QA. Word change: about +20 (468 to about 488).
  - Measure: QA FAILs whose cause is a criterion absent from the Engineer's comment (count per issue; baseline 2 of 3 posted FAILs on #24 and #25 first launches). Protection metrics: QA rounds per issue, reopen events, and defects after PASS. Words are not a target.

  **2. Name the tools and the environment for the Engineer's and QA's checks in the claim comment.**
  - Evidence: #27's first QA run failed because the dev container had no bun although `bun.lock` was the lockfile and the PM had flagged bun in grooming; the orchestrator's Reflection says reading `.devcontainer/` first would have saved the round. QA comments on #23, #24 and #25 each report the tests step of `make verify` could not run in Kiro Web (`uv` cannot create its Python directory) and was "not independently verified", while #7 and #27 QA ran `make verify` in the container and reported a pass. 3 of 5 issues had an unverified tests step at QA.
  - File: `_docs/agent-kit/procedures/orchestrator-comments.md`, Claim: add to the **Fact** line "the environment QA will run in and the tools its checks need (for example bun, uv Python, Docker), each confirmed present". Protected kit file; not on the epoch list.
  - Expected effect: fewer QA launches wasted on a missing tool and QA launched where `make verify` can run. Word change: about +25 (293 to about 318).
  - Measure: count of QA comments that say the tests step was not run or a tool was missing (baseline 4 of 5 issues: #23, #24, #25 and #27's unposted FAIL). Protection metrics: defects after PASS and reopen events, so that a launch moved to a better environment is not credited for skipping a check.

  **3. PM checks existing decisions and names the Heavy decision-record file in Expected paths.**
  - Evidence: #23's grooming comment asked for the pinned file's path and offered `_docs/vendored/ponytail/`, while the human task `decide-pinned-skill-location` (written 2026-11-06) already named `_docs/vendor/ponytail/`; the issue body then needed a Confirm comment and a PM re-record after approval. #25's `Expected paths` omitted the decision-record file `_docs/decisions/2026-11-10T0822Z-reviewer-role.md` that `process.md` (Heavy gates) says the Engineer commits; the second QA launch flagged files outside Constraints and the Files line was amended after approval (new hash, Confirm and re-record). Whether the PM read the task file is `unknown` (the comment does not say).
  - File: `_docs/agent-kit/team/pm.md`: one line before "What to decide yourself": "before asking a decision question, search `_human-tasks/` and `_docs/decisions/` for it; for a Heavy issue, list the decision record's file path in the expected paths." Protected kit file; on the epoch list.
  - Expected effect: fewer post-approval body amendments caused by an omitted path or an already-decided choice. Word change: about +35 (966 to about 1001).
  - Measure: post-approval Confirm comments whose cause is a PM-omitted path or already-decided option (baseline 2 of 5 issues). Protection metrics: changed paths outside limits (QA-reported) and QA rounds. A single sweep cannot show the effect; check at the next sweep.

  **4. Fix commit matching in `scripts/ponytail_metrics.py` before #8's Engineer launch.**
  - Evidence: `make ponytail-metrics N=7` counts `d15ba98`, whose message uses "#7" for the old draft backlog item; `N=27` counts `35eb30b` and `1562ee9`, a planning commit and a session summary. Two commits that name "#8" already exist, `a951ae9` (about 81 non-test lines) and `83c1dcf` (about 65 lines), written before #8 starts. The script counts commits that name the issue and are reachable from the QA PASS commit, so #8's first figures would carry about 146 lines of handoff and record text that the Engineer did not write. The script also exits 1 (make: Error) whenever Engineer elapsed is unavailable.
  - File: `scripts/ponytail_metrics.py` and `tests/test_ponytail_metrics.py`; new issue, Standard. Not protected, but a changed metrics script is in the epoch record. Likely fix: count only commits after the claim comment, or exclude paths under `_docs/records/`, `_human-tasks/` and `_session-summaries/`. The human or PM picks the rule.
  - Expected effect: line and test counts reflect Engineer work only. No word effect.
  - Measure: listed commits for #7, #27 and the first run for #8 compared with a hand check (a correctness check, not an efficiency one). Protection: the existing 23 tests stay green and the "no judgement words" test still passes.

  **5. Ask each role for a Reflection block on #8.**
  - Evidence: all PM, Engineer and QA blocks in the six summaries read `unknown (role not asked)`; every proposal in this sweep from a role's own words is the orchestrator's. `procedures/session-summary.md` (Reflection) already says to ask each role after QA PASS. This is a practice, not a kit change.
  - File: none to the kit. The next issue summary in `_session-summaries/` (for #8). If the Engineer work is again done by the orchestrator, the summary says the Engineer block is the orchestrator's.
  - Expected effect: the next sweep has PM, Engineer and QA evidence in their own words.
  - Measure: number of non-`unknown` role blocks per issue summary (baseline 0 of 11 non-orchestrator blocks). This is a process-compliance count with no efficiency claim; protection pairing is not needed.

  **6. Decide where frontend tests run: CI and the push check have no bun.**
  - Evidence: `.github/workflows/verify.yml` and the push-check image (Node 24 and npm, no bun) cannot run `make frontend-install`; the #27 summary and handoff say #8 will break CI and the push check if frontend tests join `make test`. The decision is with the human (`.github/` and the image are protected or the human's).
  - Files: `.github/workflows/verify.yml` (protected) and the push-check image the human builds; or keep frontend tests out of `make verify` and say so in #8. Decision request, not a text change.
  - Expected effect: #8's QA and the human's push check run the frontend tests.
  - Measure: whether the CI run and the push check execute the frontend test step (yes or no, per push). Protection: weakened-test check and Verify stay as they are.

  **7. Review of the held attribution finding (no change proposed).**
  - Evidence: 44 of 48 non-merge commits since `6211f95` carry an `Assisted-by` trailer; the 4 without are human commits; 2 human commits carry a wrong `Kiro` trailer (see Result 6); OpenCode has produced no commit, so one of the three tools in the rule has never been exercised.
  - File: `_human-tasks/2026-11-06T0219Z-human-task-orchestrator-decide-upstream-kit-issues.md` (record only). Proposal: keep holding option 2 until an OpenCode commit exists, then re-read. Human's call.
  - Measure: unmeasured; no efficiency metric is claimed.

  **Considered and not proposed.**
  - The orchestrator's #25 Reflection (say the Engineer commits the decision record before the first QA launch, `process.md` Lifecycle step 3): `process.md` Heavy gates already say the Engineer commits the ADR as a file, and the file was committed (`72e35df`) before the first QA check; no QA FAIL on #25 cites it. No evidence of harm.
  - The orchestrator's spec-review Reflection (say in `procedures/planning.md` that later phases are outlines): its line 3 already says "Not up-front design"; the only evidence is the orchestrator's own over-planning, corrected by the human in session. Unmeasured, so left out.
  - The orchestrator's #7 Reflection (`issue-comment.sh` should print gh's stderr): already filed as `agent-kit#187`; no local patch (protected kit file).
  - The orchestrator's frontend-prompt Reflection (`_docs/planning/02_development.md` step 2): that file is course material; "Lovable prompts used" has no source. `unknown`, left out.
  - The orchestrator's #27 Reflection (list tools per environment): merged into proposal 2.
  - Fewer approvals, questions or shorter human waits are not targets and no proposal uses them.

- **Human ruling (2026-11-10, same session; the PM wrote nothing below):**
  - 1, 2, 3: approved as drafted and applied in `17e725e` (software-engineer.md, orchestrator-comments.md, pm.md). `make kit-check` still reports claim `1.10+socboard.1` correct.
  - 4: approved; a Standard issue is filed for the orchestrator to groom. It must land before #8's Engineer launch.
  - 5: approved as a launch-message practice for #8 (PM, Engineer, QA each asked for a Reflection block).
  - 6: option (a): bun in CI and the push-check image, frontend tests in `make verify`. Folded into #8's re-grooming; touches protected files, each needing separate approval.
  - 7: no action.
  - Epoch 1 start moved from `a1d37ba` to `17e725e`; see the epoch record. Proposal 4 may move it again.
