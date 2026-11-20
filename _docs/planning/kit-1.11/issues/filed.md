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

- **Proposal:** a label added before grooming means "go ahead and groom". The human's confirmation of the groomed body, recorded in the orchestrator's Confirm comment, is the approval, with no separate step. The hash rule is unchanged: the Engineer still starts only on a body whose hash the PM recorded.
- **Meanwhile:** the PM grooms first and the human labels after, so each issue needs one approval.
- **Issue:** #203 (04c), which already rewrites Lifecycle step 2 and the Approved text.
