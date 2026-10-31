# Issue #23: Reflection prompts and launch usage lines in session summaries (re-scoped from "scorecard and reflection prompts")

**Date:** 2026-10-31T1801Z (UTC)
**Spec version:** none

## What changed and why

Session summaries now carry a `## Reflection` section (each role's three-line block, copied unchanged from a new comment that role posts on the issue after QA PASS) and a `## Launch usage` section (one line per launch: role, active time, tool uses). The procedure documents the `-3` collision case and how to read old `issue-NNN-` and `planning-<date>-` names, `process.md` step 2 gives the exact `git log -1 --format=%h -- _session-summaries/` command and says to read the `**Spec version:**` line of the summary it finds, and the third filename test in `tests/test_claims.py` is stronger. A small test (`tests/test_session_summary.py`) checks that the template keeps the two headings and the three prompt labels.

The issue was re-scoped before commit. The per-session scorecard, the `improvement` kind and the safeguards moved to the sweep skill issue (#25), because numbers are better recomputed from git and GitHub at a periodic sweep and only perishable items need capturing during a session. The token figure was dropped from the usage line because its meaning is unverified; it is tracked in #26.

**What I learned:** the first live use of the Reflection step worked: all three roles posted specific, measurable proposals when asked, and the instructions were followable.

## Reflection

Copied unchanged from each role's issue comment. The PM and Engineer comments carry the same labels as the template.

### PM

Reflection:
1. Slowed down: #23 was groomed three times in one day (full scorecard, re-scope, tokens dropped); the first body was about 4,000 words and each re-scope meant rewriting it whole, because my Edit tool is disallowed and only Write was available (comments of 16:45Z, 17:25Z and the token decision).
2. Nearly went wrong: with no Edit tool I made two shell-side rewrites of scratch issue text (a Python replace script for the #25 reference, a heredoc append on #24); neither touched repo files.
3. Proposed change: let the PM role use Edit, limited to `.scratch/` (`agent-kit/claude-code/agents/pm.md`, `agent-kit/opencode/agents/pm.md`); expected effect is no shell edits by the PM; measured by counting shell-edit slips in PM reports over the next five issues (tracked as a new unlabelled issue).

### Engineer

Reflection:
1. Slowed down: I built the full scope first, then reworked it three times (re-scope, tokens dropped, QA's FAIL). The word limit made me trim step 2 twice. My first trim dropped the `**Spec version:**` instruction, which was QA's FAIL.
2. Nearly went wrong: my first edit merged steps 3 and 4 onto one line. Verify did not catch it; the PM found it by reading the diff.
3. Proposal: `agent-kit/procedures/verify.md`. Add a check that numbered steps in edited procedures start on their own lines. Expected effect: no merged-step defects. Measured by: zero such findings from PM or QA over the next 5 issues.

### QA

Reflection:
1. Slowed down: my first mutation (b) on the strengthened test changed nothing and passed; I only noticed by reading the result and redoing it (`.scratch/qa23_mut_b.py`). The first-round FAIL was a criterion the Engineer had disclosed dropping to fit the 1,493-word limit.
2. Nearly went wrong: counting a mutation that did not change behaviour as proof the test fails; the unmutated-copy control caught it.
3. Proposal: in `agent-kit/team/qa-engineer.md`, add "for each mutation, first confirm the mutated copy differs from the original and that an unmutated copy passes". Effect: no false mutation results. Measure: QA comments that report a redone mutation, counted at the next sweep.

### Orchestrator

Reflection:
1. Slowed down: scope changed mid-issue three times (the re-scope after the sweep design, dropping tokens, the QA fix), so the Engineer's staged work was reworked each time; the re-scope came from human design discussion held while implementation was already running.
2. Nearly went wrong: I asked the human to approve a commit command twice that became stale because a later decision changed the staged files; I told them not to run it, but a stale command in an earlier message is a risk.
3. Proposal: when a decision is still open and could change staged files, ask for it before presenting the commit command (`agent-kit/process.md`, step 3 or 7); expected effect: one approval request per commit; measured by counting commit requests withdrawn per issue at the sweep.

## Launch usage

Active time and tool uses per launch, copied from the subagent completion notifications. Tokens are not recorded (see #26).

- PM, first grooming: 3.5 min, 22 tool uses
- PM, re-groom after the re-scope: 1.3 min, 14 tool uses
- PM, add the #25 reference to #23: 1.9 min, 21 tool uses
- PM, file #26 and update #23's body: 1.1 min, 8 tool uses
- PM, reflection and file #28: 0.8 min, 9 tool uses
- Engineer, first implementation: 3.5 min, 48 tool uses
- Engineer, rework to the re-scoped issue: 2.6 min, 20 tool uses
- Engineer, drop tokens: 0.7 min, 8 tool uses
- Engineer, post comment after cf16819: 0.5 min, 5 tool uses
- Engineer, QA FAIL fix: 12.8 min, 15 tool uses
- Engineer, post comment after 75a0d5b: 0.4 min, 4 tool uses
- Engineer, reflection: 0.3 min, 4 tool uses
- QA, first check (FAIL): 1.8 min, 24 tool uses
- QA, re-check (PASS): 1.1 min, 18 tool uses
- QA, reflection: 0.2 min, 4 tool uses

Totals: PM 8.7 min, Engineer 20.8 min, QA 3.1 min, about 32.6 min of agent time. Other launches in this session, not part of #23: backlog review PM 4.7 min, 25 tool uses; PM filing #25 1.1 min, 12 tool uses; PM filing #27 1.5 min, 18 tool uses.

## Files created or modified

Commit cf16819 (5 files): `agent-kit/procedures/session-summary.md`, `agent-kit/process.md`, `agent-kit/templates/session-summary.md`, `tests/test_claims.py`, `tests/test_session_summary.py` (new).
Commit 75a0d5b (3 files): `agent-kit/process.md`, `agent-kit/procedures/session-summary.md`, `agent-kit/templates/session-summary.md`.
Live code: `tests/test_claims.py` and `tests/test_session_summary.py` run live in `make test` and `make verify`. Nothing under `agent-kit/scripts/` or `agent-kit/claude-code/hooks/` changed.
Doc budget (the two #22 `wc -w` commands): always-loaded 4,420 to 4,420; total core Markdown 15,020 to 15,251 (+231). Reported, not enforced, per the human's decision that the cap is a tracked metric.

## Decisions made by the human

- Re-scope of #23 before commit: scorecard, `improvement` kind and safeguards out (moved to #25); reflection prompts, launch usage line and the #24 follow-ups stay.
- Drop the token figure for now and mark it for future review (#26). Ponytail's token reporting is unverified; tokens must come from the host tool.
- Word cap is a performance metric tracked at the sweep, not a hard cap; always-loaded and total words are recomputed from git history there.
- Backlog review: approve Phases 1b, 2 and 3 now, with 4 and 6 after Phase 3's dry runs; rewrite survivor issues in place; version 1.10 when the human is ready.
- Issue approval semantics, option A (#27): agents may edit or comment on owner-authored issues, groom before approval, freeze by body hash; no new label. #27 is split in two (Part 1: author rule, `make issue-hash`, PM-file line and tests; Part 2: lifecycle reorder and freeze checks), and the hash comes from `make issue-hash N=<number>`.
- The PM role gets a small issue to use Edit (#28).
- Ran the approved commits cf16819 and 75a0d5b themselves. Chose to run the new Reflection step now for #23.

## Mismatches with the spec or design docs

None (there is no `_docs/specs.md`).

## Commands to validate

- **Verify:** `make verify` (passes at 75a0d5b: claims OK, 62 tests, 0 failed)
- **Test (all):** `make test`

## Proposed AGENTS.md changes

None for #23. The issue approval change is #27, which touches `AGENTS.md` and waits for the human.

## Temporary changes

None. `make clean-scratch` ran at the end of the issue. Nothing was started that needs stopping.

## Interruptions

QA failed once (the `**Spec version:**` instruction was dropped from `process.md` step 2); fixed in 75a0d5b and re-checked with a PASS. No role stopped early. `make assert-clean` fails only on the known baseline: ` M .claude/settings.json` (the human's change) and the two untracked `proposals/` files; HEAD did not move during QA.

## Unrelated problems noticed but not fixed

- `.claude/settings.json` is still modified and uncommitted, and the two `proposals/` files are untracked.
- The PM role lacks the Edit tool, which led to two shell-side rewrites of git-ignored scratch text (a heredoc on #24, a script on #25). Tracked in #28.
- Step 3 of the session-summary procedure still uses the `_docs/agent-kit/templates/...` path form, which `AGENTS.md` maps to `agent-kit/`.

## Follow-ups for the next session

- Label #27 (the human) and the Orchestrator comment records the split; the PM then grooms Part 1 and files Part 2. Next in the agreed order after that: #27 Part 2, then 1b-a, 1b-b, #1 re-scoped, 2a, 2b, #18 re-groomed, the permission template refresh, 3a, 3b. Phases 4 and 6 wait until after Phase 3's dry runs.
- When the human labels #25, the PM first updates it to match the re-scope: no tokens or token metric, four safeguards, usage lines without tokens.
- New phase issues still to file, unlabelled: 1b-a, 1b-b, 2b, 3b (the human wants the metric approach confirmed first, which is now decided: cap as a metric).
- Reflection proposals for the human to decide later (nobody applies them): the QA mutation-control line in `qa-engineer.md` (belongs with Phase 1b because it adds always-loaded words); a merged-steps check in `verify.md`; the PM Edit tool (#28); ask for open decisions before showing a commit command (`process.md`).
- Still open from #22: the human's live checks with the kit's settings installed in Claude Code and OpenCode (including `gh run view 1 --log` being refused), and the stale `agent-kit/opencode/START.md` wording (small follow-up, not filed).
- Version bump: the human cuts 1.10 when ready; the changelog covers #22, #24, #23 and whatever lands by then.
- #26 (token figures): compare one figure with the tool's usage view once, and decide on a source.
- Part B of #24 (`docs-check`) is filed after the index has been used in a real project; #18 waits for Phase 2.
- Later worth considering: counting scope changes during implementation at the sweep, since two of this issue's three reworks came from them.
