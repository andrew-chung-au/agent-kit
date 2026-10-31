# Issue #28: Let the PM role use the Edit tool, limited to .scratch/ (option a only)

**Date:** 2026-10-31T2318Z (UTC)
**Spec version:** none

## What changed and why

The Claude Code PM role definition (`agent-kit/claude-code/agents/pm.md`) now disallows only `NotebookEdit`, and its text says to write and edit only under `.scratch/`. `agent-kit/claude-code/START.md` (lines 12 and 39) and `agent-kit/README.md` (line 111) now say the PM can edit under `.scratch/` by instruction and QA can't edit, and line 39 states plainly that no hook or path rule enforces it. A new test (`tests/test_role_definitions.py`) pins the PM and QA tool lists and the OpenCode PM's `.scratch/`-only grant.

Why: GitHub has no partial issue edit, so `gh issue edit --body-file` always sends the whole body, and the PM drafts it in a local `.scratch/` file. With only Write the PM had to retype the whole draft (about 4,000 words for #23, groomed three times) to change one sentence, which is slow and can silently drop text, and it led to two shell-edit slips on scratch files. The Claude Code PM could already overwrite any file with Write, so allowing Edit adds almost no capability; the OpenCode PM already allowed edits under `.scratch/`.

Option (b), a hook that refuses PM and QA writes outside `.scratch/` in Claude Code, is deferred; it comes up only if a PM overwrites a repo file outside `.scratch/`.

**What I learned:** I first framed #28 around an enforcement gap that the human's plain question ("why can't they edit gh issues? ... am I missing something?") showed was a separate concern; the real reason is the whole-body retype cost.

## Reflection

Copied unchanged from each role's issue comment.

### PM

Reflection:
1. Slowed by: finding the #22 `wc -w` commands. A grep of the repo found only session summaries that mention them, so I read #22's body to get the commands (3 searches).
2. Nearly went wrong: I could not use Edit myself, so I rewrote the whole body with Write. It cost one full retype, the very problem #28 describes. No text was dropped.
3. Proposal: add the two `wc -w` commands to `agent-kit/procedures/verify.md`. Expected effect: grooming and QA find them in one read. Measure: tool calls spent locating them in the next issue with a doc-budget criterion (this one took 3).

### Engineer

Reflection:
1. Slowed: the mutation check needed its own script (`.scratch/mutate28.py`) because the test resolves `agent-kit/` from its own path; I had to copy the test and two agent folders into `.scratch/` to mutate safely. Six runs, one script.
2. Nearly went wrong: the first draft of the START.md line 39 edit would have left a dangling clause; I replaced up to the semicolon so "**Assert clean**" still read correctly.
3. Proposal: add a one-line note in `agent-kit/procedures/verify.md` that tests should take the kit root from a constant, so mutation copies work unchanged. Effect: fewer script lines per mutation check. Measure: lines in the next mutation script.

### QA

Reflection:
1. Slowed down: my first grep used a backtick inside a double-quoted pattern and failed with an eval error (exit 2), and the Edit tool is not available to QA, so a one-line fix to my comment draft needed a script (`.scratch/qa28_fix.py`). Reading #29/#25/#30/#31 returned 46.7KB, so I grepped a saved file.
2. Nearly wrong: the PM definition shown to me still disallowed Edit, so the real grant could not be tested; I reported it as a live check not done.
3. Proposal: `agent-kit/team/qa-engineer.md`, add "write the mutation script to cover the criteria's variants and print exit codes per mutant". Expected: fewer ad hoc reruns; measure by count of QA shell calls per issue in the session summary.

### Orchestrator

Reflection:
1. Slowed down: the human needed three rounds of questions to see why #28 existed, because my first explanation and the issue's own text led with the mechanism, not the reason (evidence: "I'm not seeing the why clearly enough", then "am I missing something?").
2. Nearly went wrong: I tied the Claude Code write gap to #28's goal, which would have turned a small convenience change into a hook project; the human's question caught it before anything was built.
3. Proposal: land #30 (a required `## Why` section in the issue template), so every groomed issue opens with the reason in plain terms; expected effect: fewer clarifying rounds on an issue's purpose; measured by counting human questions about purpose per issue at the next sweep.

## Launch usage

Active time and tool uses per launch, copied from the subagent completion notifications. Tokens are not recorded (see #26).

- PM, grooming #28: 1.0 min, 17 tool uses
- PM, reflection: 0.2 min, 4 tool uses
- Engineer, implementation: 3.9 min, 28 tool uses
- Engineer, post comment after commit: 0.4 min, 4 tool uses
- Engineer, reflection: 0.2 min, 4 tool uses
- QA, check: 1.5 min, 23 tool uses
- QA, reflection: 0.6 min, 4 tool uses (the notification showed running totals of 2.1 min and 27 tool uses; this line is the difference from the earlier figure)

Totals: PM 1.2 min, Engineer 4.5 min, QA 2.1 min, about 7.8 min of agent time. Other launches in this stretch, not part of #28: PM updating #29 1.2 min, 13 tool uses.

## Files created or modified

Commit 53fffc5 (4 files): `agent-kit/claude-code/agents/pm.md`, `agent-kit/claude-code/START.md`, `agent-kit/README.md`, `tests/test_role_definitions.py` (new).
Live code: `tests/test_role_definitions.py` runs live in `make test` and `make verify`. Nothing under `agent-kit/scripts/` or `agent-kit/claude-code/hooks/` changed, and no hook or path rule was added.
Doc budget (the two #22 `wc -w` commands, tracked metric, not a gate): always-loaded 4,571 to 4,571 (no growth); total core Markdown 15,330 to 15,366 (+36).

## Decisions made by the human

- Option (a) only for #28: allow Edit for the Claude Code PM and rely on the role text and the protected-file prompts; option (b), the enforcement hook, is a future idea only if issues arise.
- Labelled #28, then ran the approved commit (53fffc5) themselves.
- At the decision point: accept the minor test gap (an extra `"agent-kit/*": allow` line added to the OpenCode PM definition still passes the fourth test), and start #25 next.

## Mismatches with the spec or design docs

None (there is no `_docs/specs.md`).

## Commands to validate

- **Verify:** `make verify` (passes at 53fffc5: claims OK, 90 tests, 0 failed)
- **Test (all):** `make test`

## Proposed AGENTS.md changes

None.

## Temporary changes

None. `make clean-scratch` ran at the end of the issue. Nothing was started that needs stopping.

## Interruptions

None. `make assert-clean` fails only on the known baseline: ` M .claude/settings.json` (the human's change) and the two untracked `proposals/` files; HEAD did not move during QA.

## Unrelated problems noticed but not fixed

- `.claude/settings.json` is still modified and uncommitted, and the two `proposals/` files are untracked.
- Many commits are unpushed (the human reviews the diff and pushes).
- The PM can now overwrite any repo file with Edit or Write in Claude Code. Only the role text, the protected-file ask rules and the commit gate stop it (accepted as option (a)).

## Follow-ups for the next session

- The benefit isn't live here yet: this repo launches roles from the installed `.claude/agents/`, which still disallows Edit for the PM. The human copies `agent-kit/claude-code/agents/pm.md` to `.claude/agents/pm.md`, restarts Claude Code, launches the PM and asks it to edit an existing `.scratch/` file with Edit (should work); asking QA to use Edit should still be refused.
- Next up: #25 (sweep skill part 1): the PM first refreshes its stale baselines (always-loaded 4,571, `AGENTS.md` 1,658, `pm.md` 623) and its reuse note (the hyphenated `issue-hash.py` name means a copy, not an import), then an Engineer implements it. #30 (required Why section) and #29 (Part 2) wait for the human's label; #31 (kit evolution) waits for a label and its four decisions.
- Reflection proposals for the human to decide later (nobody applies them): the two `wc -w` commands put in `agent-kit/procedures/verify.md` (this PM) or `pm.md` (the #27 PM); tests take the kit root from a constant so mutation copies work unchanged; QA mutation scripts cover the criteria's variants and print exit codes per mutant; land #30 so every issue opens with its reason. These add always-loaded words only if they go in role files, which belongs with Phase 1b.
- Test gaps accepted: an added allow line in the OpenCode PM definition, and widened OpenCode PM body text, aren't pinned by the extra fourth test.
- Still open from #22: the human's live checks with the kit's settings installed in Claude Code and OpenCode (including `gh run view 1 --log` being refused), and the stale `agent-kit/opencode/START.md` wording (small follow-up, not filed).
- Version bump: the human cuts 1.10 when ready; the changelog covers #22, #24, #23, #27, #28 and whatever lands by then (the Engineer's lines for #28: the Claude Code PM can use Edit under `.scratch/` by role text only, the docs say so, and a new test pins the PM and QA tool lists).
- New phase issues still to file, unlabelled: 1b-a, 1b-b, 2b, 3b. Phases 4 and 6 wait until after Phase 3's dry runs. #18 waits for Phase 2.
