# Issue #41: Evidence-based review of the always-loaded docs (research only)

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-03T09:30Z (UTC)
**Spec version:** none

## What changed and why

A research report on how much the always-loaded kit documents cost and what to cut, with cited vendor guidance, word counts taken from git blobs, and six numbered proposals (P1 to P6) for the human to accept or reject one by one. Built by the Kiro cloud session on branch `issue-041-doc-review`, commit 46b170f (one commit on current `main`, committed by the Engineer; unprotected path, so no approval gate). Merged into the sandbox `main` as 17e271c. The only file is `_docs/measurements/2026-11-02T1447Z-measure-always-loaded-guidance.md`: no kit file, test or script changed, and no proposal is applied. The report itself holds the counts, the proposals and their deltas; read it there.

QA PASS at 46b170f: every word count reproduced with `git show <commit>:<file> | wc` at 03de86e, 6b5d9c6 and 2c1c2ff (totals and the `process.md` figures match); the file set matches the issue; each proposal's quoted old text matches `main` and its delta recomputes (P1+P2+P3 is 749 words, 11.7% of 6,396); the test pins named are right; a public-repo scan found no secrets, private paths, names or contact details. After the merge, `make verify` in the sandbox: 427 tests OK, no test files changed. The branch's own CI was green.

Findings from QA that the human should know before accepting proposals (none fail a criterion):
- The report says the vendor pages could not be fetched (HTTP 403 from the cloud sandbox), but QA fetched them and found several items the report calls `unknown` are documented: the 200-line target and its reason, "imports don't reduce context cost", and OpenCode's CLAUDE.md fallback. Claude Code subagents do receive CLAUDE.md and AGENTS.md (Explore and Plan skip them). That weakens the report's "launched roles don't automatically see AGENTS.md" framing and the premise of **P5**.
- Citations: S1 to S6 confirmed; S7 (arXiv) confirmed, but its current title differs from the one quoted; S8 only at abstract level; two URLs now redirect (docs.anthropic.com 301, developers.openai.com 308).
- Nits: the Result line points to a "Rules and pins" part with no such heading; P5's old line is 12 words, not 13 (the +5 delta is right); the helper scripts the report cites (`.scratch/count41.sh`, `sections41.py`, `deltas41.py`) are not committed, so QA rewrote them.
- The test pins come from reading the tests, not running them with the proposed changes; each follow-up issue must run them.

Not verified: GitHub CI on the merged result (after the human pushes), the arXiv PDF itself, what roles actually read of `process.md`, and any token figure.

**What I learned:** a report that says "could not fetch, unknown" is a prompt for QA to try the fetch from a better-connected sandbox; the cloud sandbox's network limits can leave true statements marked unknown, and one of them changed a proposal's premise.

## Reflection

### Engineer

unknown (the Kiro cloud session built this; its role was not asked)

### QA

1. Slowed down: the report's section counts and proposal deltas had no rerunnable script in the commit, so I rewrote the counting and the P1 to P3 delta checks from scratch. The cited pages were slow to confirm: two URLs now redirect and one fetch returned a 54 KB page that I had to read in a saved file to find the 200-line sentence.
2. Nearly went wrong: the report says the primary pages could not be fetched and leaves several claims `unknown`. I could have copied that as the baseline and checked only the quoted excerpts. Fetching the pages showed some `unknown` items are documented, and one (subagents load CLAUDE.md and AGENTS.md) changes P5's premise. I also nearly treated my own drafted pointer wording as the report's (-758 against the report's -749), so I stated that the difference comes from draft text.
3. Proposal: `agent-kit/templates/measurement.md`, add one required line under "Command and commit": "Helper scripts: committed path, or `none` (then the commands are inline)". Effect: a QA or sweep reader can rerun every count and delta without rewriting scripts. Measure: in the next five measurement entries, count entries whose figures QA reproduced with no rewritten script (target 5 of 5, against 0 of 1 now).

### PM

unknown (the PM's grooming ran in earlier sessions; role not asked)

## Launch usage

- QA (check #41 at 46b170f, PASS): 142.0 s, 39 tool uses
- QA (reflection, resumed): 174.6 s, 43 tool uses (as reported; may include the earlier run)
- Engineer: the Kiro cloud session (not measured here)
- Also this session: a trial merge and full `make verify` by the orchestrator before QA (427 tests, PASS), and again after the merge.

## Files created or modified

- `_docs/measurements/2026-11-02T1447Z-measure-always-loaded-guidance.md` (commit 46b170f, merged as 17e271c)
- This summary.

## Decisions made by the human

- Handed #41 to the cloud session; said the orchestrator could merge a ready branch here instead of opening a pull request (a pull request is not possible with the sandbox token, which has no pull-request permission).
- The six proposals are not yet decided.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- QA's reflection proposal above is for the human; none applied.
- The report's nits (the "Rules and pins" heading, the S7 title, the uncommitted helper scripts) are not fixed; the report is a record, and the follow-up issues will cite the checked sources.

## Follow-ups for the next session

- The human decides P1 to P6 one by one; accepted ones become issues (P1 and P2 each add a procedure file and move a pinned test, P6 adds a `make` target). Do not accept P5 as framed: QA found that subagents do receive `AGENTS.md`.
- #33 can cite the sources QA confirmed instead of waiting.
- Push from the clean clone; GitHub CI on `main` is the remaining check.
