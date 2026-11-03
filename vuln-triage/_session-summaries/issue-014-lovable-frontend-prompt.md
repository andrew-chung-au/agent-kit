# Issue #14: Frontend prototype via Lovable (stages A to C: process change and approved prompt)

**Date:** 2026-10-17
**Spec version:** 16e1ec0
**Status:** closed after QA PASS on stages A to C. Build and import split to #15. Nothing pushed.

## What changed and why

The human chose #14 as the next issue. The PM groomed it into five stages (comment 6231923268); the human split it (Decision 2), so #14 covers A to C and #15 covers the Lovable build (D) and import (E).

- Stage A: `_docs/planning-process.md` § Stage 3 now derives `_docs/api.md` from the frontend's services layer (`7c12cd4`).
- Stage B: Lovable prompt drafted (`6327f01`), revised for Decision 3 (fixed versions per affected range, full status list with withdrawn, discovery-build note; `2cbffa9`) and for the human's three edits (services-layer order, React with TypeScript, npm test, demo credentials; `67322c9`). 774 words; the 700-word limit was waived by the human.
- Decision 1: one line allowing a mocked frontend prototype in `frontend/` during planning, in `AGENTS.md` (`f6add8a`, HUMAN_APPROVED) and `_docs/planning-process.md` (`79b43e4`).
- Stage C: prompt marked `Status: APPROVED (human, 2026-10-17)` and indexed (`efa250d`).
- All roles ran as Claude Code subagents (claude-opus-5-5): PM, Engineer, QA.

## Files created or modified

- `_docs/planning-process.md`: § Stage 3 sentence (`7c12cd4`); Decision 1 line (`79b43e4`).
- `_docs/prompts/lovable-frontend.md`: new (`6327f01`, `2cbffa9`, `67322c9`, `efa250d`).
- `_docs/prompts/README.md`: index row (`efa250d`).
- `AGENTS.md` (protected): Decision 1 line (`f6add8a`).
- `_docs/ai-usage-log.md`: entries `123e37a`, `1257808`, `a6a14bf`, `50fa747`, `c801ca5` (correction), `ad1a3f0`.
- GitHub: comments on #14, #6 (6232771639), #5 (6233019628) and #15 (6233059654, 6233158527); filed #15; #15 body gained the generated-code scan criterion.

## Decisions made by the human

- Next issue: #14 (not #12 as recommended).
- Decision 1: a one-line clarification in AGENTS.md and planning-process.md, not a complex exception; diffs reviewed, then applied.
- Decision 2: split; #14 closes once the prompt is approved; #15 for build and import, with one make target running all tests including the frontend's.
- Decision 3: don't wait for #3 and #4; labelled assumptions using the richer model; v1 is discovery; later changes by coding agents, not Lovable rebuilds.
- Notes: "no fixed version" wording; login and risk-acceptance reason added to #6; PM's choices (700 words, example.* domains, no Lovable history, target names) accepted.
- Accepted the Engineer's choices: no "stale" status, dashboard status filter, a mock finding with no aliases.
- Three prompt edits (screen 2 order, React/TypeScript and npm test, demo credentials). Kept both ordering assumptions (criticality higher first, EPSS n/a after scored); note posted on #5.
- QA FAIL on word attribution: accepted the Engineer's extra sentence as part of edit 3 and waived the 700-word limit (comment 6233052344); QA risk 1 (scan generated code) added to #15's body.
- QA tool: OpenCode would not start; QA ran as fresh Claude Code subagents, a recorded exception to the #11 rule.
- Approved the prompt: "I looked at the prompt and approve it, date approval today." Quoted in closing comment 6233899240.
- Decision point: post the approval on #14 only. The README row wording and a scan make target were not chosen, so neither was done.

## Mismatches with the spec or design docs

- `specs.md` has no login screen and no risk-acceptance reason; proposed on #6 (6232771639).
- `_docs/planning-process.md` Stage 2 doesn't give the criticality sort direction or where missing EPSS goes; assumptions in the prompt, noted on #5.
- § Stage 3 now points to `frontend/README.md`, which won't exist until #15.

## Commands to validate

- **Verify:** `make verify BASE=ee0fcfe` → PASS WITH WARNINGS (no TEST_CMD: no code exists yet), last run by QA at `ad1a3f0`.
- **Assert clean:** `make assert-clean` → PASS after each QA run (`50fa747`, `c801ca5`, `ad1a3f0`).
- `make clean-scratch` → ran at close-out.

## Proposed AGENTS.md changes

- none outstanding (Decision 1 line applied as `f6add8a`). When #15 lands, the Commands section changes (protected), as #15's criteria say.

## Temporary changes

- none. No processes started, no system changes, no installs.

## Interruptions

- none. The Engineer amended its own unpushed commit `7ba1140` into `efa250d` (README row wording); recorded in the log and checked by QA.

## Unrelated problems noticed but not fixed

- The prompts index row says "the Lovable build task for issue #14"; the build is in #15. Left for #15 to reword when it records the run date.
- The Engineer ran one stray `gh issue comment` with an invalid flag; gh rejected it, and no comment was posted (checked).
- Carried from #11: #10's body still has literal `\n` and no criteria; repo-root `agent-kit/` duplicate remains.

## Follow-ups for the next session

1. Human: review and push `ee0fcfe..HEAD` (#14 commits plus this summary).
2. #15: human runs the approved prompt in Lovable (one build, at most two follow-ups), connects GitHub and gives the repo URL; then the import.
3. What v1 reveals goes into #3, #4 and `api.md`; settle the two tie-break directions in Stage 2 (#5).
4. #12, #13 and #10 remain, as listed in the #11 summary.
