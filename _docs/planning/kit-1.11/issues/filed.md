# Kit 1.11 issues: filed numbers

Filed on 2026-11-20, unlabelled, in the index order (`00-index.md`). Each waits for the human's `approved` label; grooming is one issue at a time until 04c (issue #203) lands.

The filed bodies name other 1.11 issues by draft id (01a, 02, ...). Read each id as the issue number in this table.

| Order | Draft id | Issue | Title |
|---|---|---|---|
| 1 | 01a | issue #196 | Add kit settings, profiles, the grade vocabulary and numbered criteria, documented in customizing.md |
| 2 | 01b | issue #197 | Add per-issue overrides with the overrides label, the bounds no level can cross, and session rulings |
| 3 | 02 | issue #198 | Give role returns, findings, QA comments and messages to the human fixed fields, checked by a script, with a recommendation required |
| 4 | 03a | issue #199 | Route failing QA findings by impact and points, with a fix check, a patchwork guard, RECHECK and STEP_UP |
| 5 | 03b | issue #200 | Log unfixed findings by group, list them with make findings, and sweep them |
| 6 | 04a | issue #201 | Make the numbered criteria the Engineer's and QA's shared checklist |
| 7 | 04b | issue #202 | Add a standards register and a Standards: line to issues |
| 8 | 04c | issue #203 | Groom up to GROOM_AHEAD issues ahead with a [groomed] prefix, each placed in the order |
| 9 | 05 | issue #204 | Weight decision points, keep a ledger of the ones the agent continued past, and answer them per point |
| 10 | 06 | issue #205 | Give human tasks a header, a make human-tasks list, rendered steps and an archive for done one-off tasks |
| 11 | 07a | issue #206 | Write reflections to files and have the sweep read them |
| 12 | 07b | issue #207 | Replace the session summary with make status (including the spec version) and the Close comment |
| 13 | 08a | issue #208 | Add a consult stage and environment map before planning |
| 14 | 08b | issue #209 | Give each planned issue grades, Debt, Runs in and criterion-level Needs lines |
| 15 | 08c | issue #210 | Add reasoning variants of role files and let STEP_UP=auto use them (Claude Code only) |
| 16 | 09a | issue #211 | Ship one short core-rules file loaded by Claude Code and OpenCode in every session |
| 17 | 09b | issue #212 | Add the kit's Kiro layer: the core rules as always-loaded steering |
| 18 | 10 | issue #213 | Make Verify quiet by default, printing the test output only on failure or with V=1 |
| 19 | 11a | issue #214 | Add an optional delivery-lead role for parallel lanes, with the Claude Code channel |
| 20 | 11b | issue #215 | Let the delivery lead and workers talk through Lead: and Status: issue comments (Kiro and cloud) |
| 21 | 12 | issue #216 | Move this repo's docs into one _docs/ tree following socboard's layout, with an index row for each file |

## How they were filed

`make issue-create` could not post from the cloud session (its `gh api` write failed; the script discards gh's error, issue #187). With the human's approval, the orchestrator filed them through the GitHub connector as the owner's account, title and body only, after the PM's pre-filing scan (secret patterns, title line, criteria with `Check:` lines) passed on every file. A read-back compared each filed title and body with its source file: all 21 match, none has a label.

## Notes from the split (for grooming)

1. 03a C1's Check pointed at the parent's C8; it now reads "03b's C1".
2. Drafts 03, 08, 09 and 11 had one Files list for the whole draft; the PM split each list by criterion. Grooming confirms the split.
3. 11a: the split list gave no tier or Needs line; the index values were used (heavy; 01a, 02, 05, 06, 07b, 08b). The shared-machine `.scratch/status/<lane>` channel went to 11a.
4. 09a and 09b: the Kiro parts of the parent's C2 and C6 moved to 09b.
5. One-line reasons for the parts' grades were written by the PM where the draft gave reasons only for the parent.
6. 08b also relies on 01a (the vocabulary); its Needs line says so.

## Grooming notes from the human (2026-11-20)

The PM folds these into the issues named when it grooms each one. Each change still goes through grooming and the human's label.

### A. Amend a criterion: a third answer to "ship or fix?"

A criterion can look right at grooming and prove too strict once the Engineer and QA meet it. Today the only answers are fix (the loop) or ship (accept it as not done). Add **amend**: the criterion is wrong, not the code.

- **The three answers:** fix (the code is wrong; the Engineer fixes it), ship (the criterion is right but not worth finishing now; it is marked not done and a follow-up issue is filed), amend (the criterion is rewritten, re-approved and re-checked).
- **Where amend is offered:**
  1. The patchwork guard's approach review (a finding's second failure): "the criterion is the problem" is one conclusion the Engineer may reach, besides "change approach".
  2. QA's findings: a finding marked `category: criterion` ("stricter than the goal needs") goes to the human, not back to the Engineer for another round.
  3. Before building: if the Engineer sees a criterion can't be met as written, it raises that at once instead of failing through the loop.
- **Safeguards:**
  - Only the human chooses amend; an agent proposes new wording but never rewrites an approved criterion. It is a stop decision point.
  - It uses the existing approved-text steps: the PM drafts the new criterion, the human confirms, the orchestrator posts a Confirm comment naming the new hash, the PM records it, and QA re-checks only the amended criterion.
  - It can't cross the bounds no level can cross (#197): an amend that would drop QA, lower a tier or weaken a security rule is refused, as an override would be.
  - Every amend is logged, and the sweep counts amended criteria per issue as a signal that grooming writes criteria too strict.
- **Issues:** #199 (03a): a new criterion with the three answers and the three places amend is offered (most of the change). #204 (05): "amend an approved criterion" in the stop-point list. #201 (04a): a fourth checklist form, `C<n>: challenged (<reason>)`. #200 (03b): the ship path files its follow-up issue, and the sweep counts amends.

### B. A label added before grooming means "go ahead and groom"

On issue #196 the human added `approved` before grooming, so the groomed body needed a second confirmation (Approved text). That is friction: the label is meant to be the one approval.

- **Proposal (the human's design):** every grooming records where its authority came from, and the approval is whichever human act comes after the groomed body. Two paths:
  1. **Label first.** The orchestrator sees `approved` on an issue that isn't groomed (no `PM:` comment records a hash that matches the body). The label means "you may groom", so the PM grooms without asking. The `PM:` grooming comment records `Grooming authorised by: approved label (seen <date>)`. The orchestrator then asks the human to review the groomed body. The human's reply in the session is noted in the orchestrator's Confirm comment, with the new hash, and that confirmation is the approval. The label stays; nothing else is asked.
  2. **Groom first.** There is no label. Grooming starts because the human asked (directly, or by asking "what's next?"), or because the orchestrator asked "groom the next issue?" and the human said yes. The `PM:` comment records that source, for example `Grooming authorised by: human in session, <date>, "<the request>"`. When the human later adds `approved`, the label is the approval of the groomed body, as today.
- **The approval's source is recorded on the issue too,** so the issue shows both who authorised grooming and who approved the result:
  - Path 1: the orchestrator's Confirm comment carries `Approved by: human confirmation in session, <date>`, with the confirmed body hash.
  - Path 2: when the orchestrator first sees the label on a groomed issue, it posts an `Orchestrator:` comment with `Approved by: approved label, seen <date>`, naming the body hash the label covers (the hash the PM recorded).
- **What doesn't change:** the hash rule. The Engineer starts only on a body whose hash the PM recorded and the approval covers; a later edit needs a new confirmation. "Groomed" is checked mechanically: a recorded hash that matches the current body.
- **Why it's safe:** the confirmation in path 1 comes from the human in the session, never from comment text. The sandbox token can add labels (`environments/local-sandbox/README.md`), so a label alone never approves a body that it was added before.
- **Meanwhile:** until #203 lands, the PM grooms first and the human labels after (path 2), so each issue needs one approval.
- **Issue:** #203 (04c), which already rewrites Lifecycle step 2 and the Approved text.

### C. Other tool layers: check each issue's per-tool files (2026-11-22)

The kit stays tool-agnostic: any tool that reads `AGENTS.md` can run the core. The confirmed, supported tools are Claude Code, OpenCode, CodeBuddy, Kiro and Antigravity (the human, 2026-11-22). New tool layers are joining 1.11 alongside the core changes: CodeBuddy (`agent-kit/codebuddy/`) and Antigravity (`agent-kit/antigravity/`, #221), both on main and built in other sessions. Kiro has no kit layer until #212.

Rules reach every layer through `AGENTS.md`: OpenCode, CodeBuddy and Antigravity read it directly (Antigravity walks up to the repository root), and Claude Code reads it through `CLAUDE.md`. So a rule an issue puts in `AGENTS.md` or the core kit docs needs no per-tool work. Only a layer's own files need a line: role prompts (`<tool>/agents/*.md`), skills, settings and hooks. Kiro is the exception: it loads steering files, not `AGENTS.md`, so once #212 lands an always-loaded rule also needs its Kiro steering copy. When grooming, the PM lists every layer whose own files change, or says why one is left out.

- **#200 (03b), #206 (07a):** the sweep skill copies: Claude Code, OpenCode and CodeBuddy. Antigravity has no sweep skill on purpose (its skills are model-invocable; `antigravity/START.md`), so it runs the sweep by hand.
- **#199 (03a), #210 (08c):** `STEP_UP` and reasoning variants stay Claude Code only; CodeBuddy and Antigravity have no model swapping.
- **#211 (09a), #212 (09b):** the core rules: `AGENTS.md` covers OpenCode, CodeBuddy and Antigravity with no pointer file (CodeBuddy gets no `CODEBUDDY.md`; comments on #211 and #212); Kiro needs the steering copy #212 adds. The hand load check (a fresh session quotes the first core rule without reading any file) covers every supported tool: Claude Code and OpenCode in #211, CodeBuddy and Antigravity too (their 2026-11-21 spikes showed `AGENTS.md` loads, not that the core rules are followed from it), and Kiro in #212.
- **Role prompts in step (see also note D):** from #198, `tests/test_role_definitions.py` checks that every layer with role prompts points each role at the same `team/` file. An issue that adds or changes a role prompt (for example #214's delivery-lead agent) adds it to every such layer, and adds Kiro once its layer has role definitions.
- **#214 (11a), #215 (11b):** a delivery-lead agent per tool with role prompts (Claude Code, OpenCode, CodeBuddy, Antigravity) and the channel each one can use.
- **#198 (02):** groomed before CodeBuddy and Antigravity landed; session rulings (2026-11-22) give `codebuddy/agents/*.md` and `antigravity/agents/*.md` the same change as the Claude Code and OpenCode role prompts. Nothing changes for Kiro.

### D. Grades, model level and splitting (2026-11-22)

Every groomed issue carries Effort, Reasoning and Impact, but in prose and as one grade for the whole issue. Nothing says how the parts combine, which level each role runs at, or how the grades choose a model.

- **Two meanings of "effort".** The kit's Effort (S/R/E) is the size of the work in agent minutes; it feeds points routing and lane planning. A model's effort setting (low, medium, high) follows the kit's Reasoning grade (B/N/D), not its Effort. Docs must not read `Effort: E` as "run the model at high effort".
- **How parts combine.** Issue Reasoning is the hardest criterion's level, not the average: a D criterion run at N fails however easy the rest is. Issue Effort is the total of the parts (time). A criterion carries its own `Reasoning:` only where it differs from the issue's.
- **Level per launch, not per issue.** The model and its effort setting are chosen at each launch from that task's Reasoning and the role: the fix check runs basic (#199 C10); a QA re-check of a small fix may run at or below the issue level; the Engineer and the Heavy second QA launch run at the issue level, or the criterion's where graded.
- **What the kit sets up per tool** (the human, 2026-11-22; the tool situation in general, as the human described it, not researched fact, and likely to change with plans): the grades are useful with any tool and stay tool-neutral. Today only Claude Code is set up to choose a subagent's model level per task. Elsewhere the kit doesn't select levels: OpenCode, Antigravity and CodeBuddy run on free models with little or no stronger choice (CodeBuddy's effort setting can be set), and Kiro can switch models but its auto selection is much cheaper. So in Claude Code an issue can stay whole with subagents at different levels; elsewhere the issue runs at one level, set by its hardest part, or the PM splits it at grooming. A tool's own option may be used where the human chooses to.
- **Splitting.** The PM proposes a split at grooming when one criterion is D and the rest are B and the project's tools can't mix levels. The delivery lead (#214) assigns issues, or separately graded criteria in Claude Code; it never splits an issue itself.
- **Issues:** #209 (08b): the `Effort:`/`Reasoning:` lines become template fields, the max/total rule, optional criterion grades and the Effort-is-size note. #210 (08c): level chosen per launch from task and role, set up for Claude Code only; the other tools are documented as not selecting levels, without fixed claims about their models. Which tools select levels is a project setting, not kit text (the human, 2026-11-22): a new setting in #196's table (working name `LEVEL_SELECT_TOOLS`), a comma-separated list of tool layers or `none`, default `claude-code`, project line only. The models each level maps to stay in the role definitions (#210 C1). `STEP_UP` then acts for exactly the tools in that setting, replacing #199's "Claude Code only" wording, so a plan change is one `agent-kit.conf` line. #214 (11a): the lead assigns issues or graded criteria; splitting stays with the PM.
