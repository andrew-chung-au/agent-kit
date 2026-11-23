# Backlog review, 2026-11-23

All open issues checked against `main` at `6831f69` and the 1.11 draft list (`_docs/planning/kit-1.11/issues/filed.md`). Nothing has been closed: closing as not planned needs the human's approval, and this review is the record for it.

## Where things stand since the 2026-11-19 review

- **Closed after QA:** #196 to #201. Issue #193 and #188 are closed too.
- **1.11 draft list, filed and unlabelled:** #202 to #216, worked in filing order. #221 (Antigravity layer) is approved.
- **Implemented on `main`, awaiting QA and a close comment:** #187 (`issue-comment.sh` shows gh's reason, two commits at `ddbd979`) and #221 (the Antigravity layer at `d79b954`, no comments yet).
- **Filed since the review:** #218 and #219 (approved, 1.11 follow-ups), #223 (approved), #226, #228 (approved), #229.

## A. Superseded by 1.11: close as not planned once the named issue is approved

| Issue | Superseded by | Why |
|---|---|---|
| #142 session-summary Date line | #207 (07b) | 07b replaces session summaries with `make status`; its one live need, a start time for `make permission-report SINCE=`, is already #18's default |
| #26 token figures in launch usage | #207 (07b) | The launch-usage line goes with the session summary; the open question folds into #191 |
| #17 parallel issues in worktrees | #214 (11a) | 11a adds the delivery-lead role and the parallel-lane rules; its 2026-11-02 cloud direction is stale |
| #15 three Conventions rules | #211 (09a) | 09a's core-rules file is the home for the web-fetch, tool-check and scratch-script rules |

## B. Superseded by shipped docs: narrow, or close

| Issue | State | Recommendation |
|---|---|---|
| #9 tagged releases with a zip | `agent-kit/releasing.md` (#182) now documents the tag, the `git archive` zip, the manifest and the test. Two differences: the zip's top folder is `agent-kit`, not `_docs/agent-kit/`, and there is no `gh release create` step | Narrow to "attach the zip to a GitHub release" (the release page and its notes), or close if the human does not want release pages |

## C. Keep, linked to the 1.11 issue that changes its fate

| Issue | Link | What the link means |
|---|---|---|
| #33 always-loaded context measurement | #211, #212 | Run it after the core-rules file lands, so it measures the new always-loaded set |
| #141 filesystem-failure audit | #199 | 03a's patchwork guard answers its "fix the class, not the spot" question; the audit keeps the rest |
| #56 tier dry runs and measurements | #199, #201 | The routing and checklist change what a run records; regroom after those, measuring points and QA rounds per grade |
| #18 ad hoc permission review procedure | #226 | #226 decides which rules may be relaxed; #18 is the procedure that applies the decision |
| #52 cloud-agent profile (Kiro Web) | #208 (08a) | 08a's environment map takes the cloud-agent row; #52 supplies its content |
| #12 "Where am I?" table | #208 (08a) | Both edit `environments.md`; land #208 first or fold the table into it |
| #10 Codespaces profile | #208 (08a) | Same environment map; needs a human run in a real codespace |
| #8 misplaced kit detection | #211 (09a) | 09a edits `setup.md`, where #8's review mode lives; keep deferred |
| #6 helpers.sh review | #216 (12) | 12 decides where `proposals/` lives, then #6 reviews the helpers |
| #3 push-check v3 review | #216 (12) | Same `proposals/` placement; the push check itself stays human-only |
| #191 usage-limit visibility | #26, #207 | Absorbs #26's token question; 07b removes the launch-usage line it would otherwise change |
| #192 install-guide wording | #211 (09a) | Both edit `install-and-upgrade.md` and `README.md`; do #192 before #211 |
| #226 which role edits prompt | #66, #18 | #66 first (same settings files), then #226's inventory; #18 applies the result |
| #219 issue-close reads the tier | #207, #214 | 07b keeps `make issue-close` accepting the Close comment; 11a may add comment prefixes. Land #219 before both |
| #218 issue-close accepts a waiver | #219, #207 | Same script and files as #219; do it second |
| #223 verify's default BASE | #213 (10) | 10 rewrites `verify.sh` output; land #223 first and 10 inherits the fix |
| #228 rewritten assertions vs weakened | #223, #213 | 11.1 follow-up on the same weakened-tests check; sequence after #223 and before or with #213 |
| #229 reference designs | #208, #211 | Its consult trigger is 08a and its size cap depends on the core-rules file |
| #90 dev-container merge checklist | #56 | Its checklist could supply #56's Light dry run |
| #154 devcontainer sync | #211 (09a) | 09a edits `installed-files.txt`, which #154's constraint depends on; the work itself is the human's |

## D. Independent: keep as they are

| Issue | Note |
|---|---|
| #66 `make` allow rule runs any command | High priority; no 1.11 issue touches the permission files |
| #58 merge commits skip the approval gate | High priority; no 1.11 issue touches `githooks/` |
| #171 cut kit 1.10 | The cut exists (tag `v1.10`, 2026-11-09); see below |
| #187 and #221 | On `main`; need one QA launch and a Close comment each |

## E. The 1.11 draft list

#202 to #216 and #221 are the upgrade another session is working through. This review does not touch them.

## #171: the 1.10 cut is already in the history

- Annotated tag `v1.10` at `7c53c54` (2026-11-09), pushed: `refs/tags/v1.10` on `origin`.
- The tag's `README.md` reads "Version 1.10 (2026-11-09)" and holds the full "Changes in 1.10" section and the release steps.
- #182 moved the changelog into `CHANGELOG.md` after the tag. The 1.10 section is the same text, with two later corrections: the `AGENTS.md` line now names CodeBuddy's hook, and one README pointer was renamed.
- No `MANIFEST.sha256` is committed, by design (`agent-kit/releasing.md`): the human generates it from the tag.
- Checked here: `git archive v1.10 agent-kit`, then `kit-manifest.py` wrote a manifest of 89 files for version 1.10, and `kit-check` reported `pristine; claim 1.10 is correct`.
- Every issue with a kit commit between 1.9 (`bbd25dc`) and the tag (82 issues, 139 commits) maps to a 1.10 changelog bullet. The ones not described are test-only or repo-only: #2, #28, #51, #54, #59, #72, #109.

What remains is the human's own step: confirm the release zip and its manifest were built from the tag and published. The GitHub release page is out of #171's scope (#9).

## Decisions (human, 2026-11-23)

- Every affected issue is linked to its 1.11 issue with an `Orchestrator:` comment pointing here.
- 1.10 is not packaged or published as a GitHub release; it was used personally in socboard. The cut is recorded above and on #171. A release page stays with #9 and is not planned for 1.10; 1.11 is the next cut.
- #142, #26, #17 and #15 close as not planned once #207, #214 and #211 are approved, not before.
- #9 is narrowed to the GitHub release page, or closed if release pages are not wanted.
- #187 and #221 each need one QA launch and a Close comment.
