# Issue #25: Add a periodic sweep skill for reflection and measures (self-learning loop), part 1

**Date:** 2026-11-01T0023Z (UTC)
**Spec version:** none

## What changed and why

The kit now has a periodic sweep: `agent-kit/procedures/sweep.md` (plain Markdown, tool-agnostic), a `/sweep` skill wrapper for Claude Code and for OpenCode, `make sweep-due` backed by `agent-kit/scripts/sweep-due.py`, and one line in `process.md` telling the orchestrator to run `make sweep-due` and propose a sweep when it says due. A sweep is run by a fresh PM launch, writes one `measure` entry to `_docs/measurements/` with a cutoff and a running summary of about 200 words, reads only the newest entry, recomputes every number from git and GitHub, and numbers its proposals with how each would be measured. Four safeguards are written into the procedure and pinned by a phrase test: agents propose and never apply; issue text is data and never becomes a rule; a role never scores its own work; fewer approvals, questions or waits are never targets, and every efficiency metric is paired with a protection metric. There is no token metric (#26). N = 5 issues between sweeps is a placeholder in `SWEEP_EVERY_N` in `sweep-due.py`, the human's to set. `sweep-due` fails closed: any failed `gh` read prints `unknown` and exits non-zero, never "due" or "not due".

Why: the self-learning loop moved from a per-session scorecard to a periodic sweep, because numbers are better recomputed from git and GitHub at the sweep and only perishable items (each role's reflection, the launch usage line) need capturing during a session. This is part 1; the metrics script and the Phase 2-dependent metrics are follow-ups.

**What I learned:** the first sweep can't be followed from the procedure as shipped (no first-run cutoff, no way to find summaries since the cutoff, no copy step, no launch instruction); the fixes are in #32.

## Reflection

Copied unchanged from each role's issue comment. The Engineer's comment is the corrected one; its first comment (6551110975) carried the PM's text by mistake (see Unrelated problems).

### PM

Reflection:
1. Slowed down: the brief named four safeguards but listed five clauses, so I merged two by judgement and had to flag it; and `.scratch/issue25-body.md` was cleared between my two runs, so the refresh script failed with FileNotFoundError and I rebuilt the body from `gh issue view`.
2. Nearly went wrong: `make sweep-due` in the procedure would have failed the claims check, which reads only `templates/Makefile.mk`; I caught it by reading `check-claims.py`.
3. Proposed change: `agent-kit/team/pm.md` gains one line, "when a brief gives a count and a list that disagree, ask before merging"; expected effect, no guessed safeguards; measured by PM comments that flag a count mismatch, per sweep.

### Engineer

Reflection:
1. Slowed by: finding the #22 `wc -w` commands. A grep of `agent-kit/` found only prose mentions, so I ran two `gh issue view 22` lookups (the first output was truncated) before I had the full second command.
2. Nearly went wrong: the stopped run's `START.md` test passed with the files-table path broken, because the copy-step line still matched; the first mutation run showed three survivors, so I tightened the test.
3. Proposal: put the two `wc -w` commands in `agent-kit/procedures/verify.md`. Expected effect: no `gh` lookup to find them. Measured by counting `gh issue view 22` calls in the next issue with a doc-budget criterion (this one took 2).

### QA

Reflection:
1. Slowed down by my first missing-`gh` check: I ran python3 with a PATH holding no python3 (`env: 'python3': No such file or directory`, exit 127), so I redid it with an absolute interpreter path.
2. Nearly wrong: my mutation script's `verify.sh` mutant matched nothing ("OLD NOT FOUND"), so wiring-into-verify went unmutated and I covered it by grep only.
3. Proposal: in `agent-kit/procedures/sweep.md`, state the first-sweep cutoff and how to find session summaries since the cutoff. Expected effect: a first PM sweep runs without guessing; measured by whether the first sweep entry's Cutoff section is filled without an `unknown` and by QA rounds on the sweep issue.

### Orchestrator

Reflection:
1. Slowed down: the human stopped the first Engineer mid-run, thinking it had finished, and a stopped agent can't be resumed, so a new Engineer had to re-verify 13 staged but unverified files, and a question round was needed first (evidence: "was stopped by the user and won't be resumed").
2. Nearly went wrong: concurrent roles shared fixed `.scratch/` file names, and the Engineer's first reflection comment carried the PM's text; comments can't be edited, so a duplicate PM reflection stays on #25 (evidence: the Engineer's own comment 6551113132).
3. Proposal: in the launch instruction in `agent-kit/process.md` (one clause), roles name scratch files with their role and issue, for example `.scratch/<role>-<issue>-<purpose>.md`; expected effect: no overwritten drafts; measured by wrong-text or duplicate comments per sweep.

## Launch usage

Active time and tool uses per launch, copied from the subagent completion notifications. Tokens are not recorded (see #26).

- PM, first grooming: 2.2 min, 29 tool uses
- PM, refresh before implementation: 0.9 min, 11 tool uses
- PM, reflection: 0.2 min, 4 tool uses
- PM, file follow-up #32: 1.3 min, 12 tool uses
- Engineer, first run: unknown (stopped by the human; no figure reported)
- Engineer, takeover and verification: 7.5 min, 28 tool uses
- Engineer, post comment after commit: 0.6 min, 4 tool uses
- Engineer, reflection (including the mis-posted first attempt): 0.5 min, 7 tool uses
- QA, check: 3.1 min, 20 tool uses
- QA, reflection: 0.7 min, 2 tool uses (the notification showed running totals of 22 tool uses and 3.8 min; this line is the difference from the earlier figure)

Totals (known runs): PM 4.6 min, Engineer 8.6 min, QA 3.8 min, about 17 min of agent time, plus the stopped first Engineer run.

## Files created or modified

Commit 7f56aad (13 files): `Makefile`, `_docs/index.md` (new), `agent-kit/README.md`, `agent-kit/blueprints.md`, `agent-kit/claude-code/START.md`, `agent-kit/claude-code/skills/sweep/SKILL.md` (new), `agent-kit/opencode/START.md`, `agent-kit/opencode/skills/sweep/SKILL.md` (new), `agent-kit/procedures/sweep.md` (new), `agent-kit/process.md` (one line), `agent-kit/scripts/sweep-due.py` (new), `agent-kit/templates/Makefile.mk`, `tests/test_sweep.py` (new).
Live code: `agent-kit/scripts/sweep-due.py` runs live from the working tree but is wired into nothing (no verify script, git hook, Claude Code hook, `agent-kit.conf` or `make test`); `tests/test_sweep.py` runs live in `make test` and `make verify`; `process.md` changes the orchestrator's decision-point routine from now on.
Doc budget (the two #22 `wc -w` commands, tracked metric, not a gate): always-loaded 4,571 to 4,586 (+15, all in `process.md`: 1,493 to 1,508); total core Markdown 15,366 to 16,113 (+747, above the ~+600 estimate; `sweep.md` is 598 words against about 450 estimated). The skill wrappers are not matched by the #22 globs.
Skills docs check (read by the Engineer and re-read by QA): both tools support skills; Claude Code with `disable-model-invocation: true` loads the skill only on `/sweep` and keeps its description out of context; OpenCode lists the description to every agent and has no per-skill switch for implicit use.

## Decisions made by the human

- Sweep entries go in `_docs/measurements/` (default accepted); N = 5 stays a placeholder.
- Launch a new Engineer to take over the staged work after the first Engineer was stopped.
- Ran the approved commit (7f56aad) themselves.
- At the decision point: accept the PASS, close #25, file a follow-up for QA's findings (#32), and restart at the clean point.
- Earlier in this stretch: the human is waiting for a good moment to restart Claude and asked to be told the next clean point.

## Mismatches with the spec or design docs

None (there is no `_docs/specs.md`).

## Commands to validate

- **Verify:** `make verify` (passes at 7f56aad: claims OK, 117 tests, 0 failed)
- **Test (all):** `make test`
- **Sweep due:** `make sweep-due` (prints `due: no sweep recorded` today)

## Proposed AGENTS.md changes

None.

## Temporary changes

None. `make clean-scratch` ran at the end of the issue. Nothing was started that needs stopping.

## Interruptions

The first Engineer was stopped by the human (a mistake). It left 13 staged paths, no commits and no comment. I checked `git status --short`, `git log --oneline -5` and the issue comments, found the work unverified, and the stopped agent could not be resumed, so a new Engineer took over, reviewed every staged file against the criteria, found one test gap and fixed it. `make assert-clean` fails only on the known baseline: ` M .claude/settings.json` (the human's change) and the two untracked `proposals/` files; HEAD did not move during QA.

## Unrelated problems noticed but not fixed

- `.claude/settings.json` is still modified and uncommitted, and the two `proposals/` files are untracked.
- Many commits are unpushed (the human reviews the diff and pushes).
- Concurrent roles shared fixed `.scratch/` file names, so the Engineer's first reflection comment on #25 (6551110975) carries the PM's text under a `PM:` label, a duplicate of the PM's own reflection. Comments can't be edited by agents; the human may delete the stray one by hand.
- The installed `.claude/agents/pm.md` is stale until the human copies the kit definition over it (from #28).

## Follow-ups for the next session

- #32 (unlabelled): make the sweep procedure followable on a first run (cutoff, finding summaries since it, who copies the entry, how the PM is launched), fix the Claude Code `START.md` wording ("only you, by typing `/sweep`"), move the `process.md` sweep line into the single "ask once" message, trim `sweep.md` to about 500 words, and pin three more phrases. The first sweep waits for #32; until then `make sweep-due` says due and every decision point proposes a sweep.
- Labels pending from the human: #32, #29 (Part 2 of #27, now with the owner-authored `PM:` hash-line rule and the closing-rule fix), #30 (required Why section) and #31 (kit evolution: hash manifest, derivative versioning such as `1.9+vuln-triage.2`, import review; four decisions with recommendations). #29 will edit the same `process.md` decision-point sub-list as #32; the Engineer re-reads the file first.
- Reflection proposals for the human to decide later (nobody applies them): QA mutation controls and variant coverage lines in `qa-engineer.md`; the two `wc -w` commands in `verify.md` or `pm.md` (proposed independently by three roles now, so a strong signal); "ask before merging when a brief's count and list disagree" in `pm.md`; unique scratch file names per role and issue; show both diffs of a two-commit change in one report; tests take the kit root from a constant. Anything that adds always-loaded words belongs with Phase 1b.
- The human's step: copy `agent-kit/claude-code/agents/pm.md` to `.claude/agents/pm.md`, restart Claude Code, then check the PM can edit a `.scratch/` file with Edit and that QA can't (QA's live check from #28). Also still open from #22: the live checks with the kit's settings installed in Claude Code and OpenCode (including `gh run view 1 --log` being refused), and the stale `agent-kit/opencode/START.md` wording (small follow-up, not filed).
- Version bump: the human cuts 1.10 when ready; the changelog covers #22, #24, #23, #27, #28, #25 and whatever lands by then (for #25: periodic sweep part 1 with `procedures/sweep.md`, a `/sweep` skill for Claude Code and OpenCode, `make sweep-due` and `sweep-due.py`, sweep entries in `_docs/measurements/`, four safeguards with a phrase test, and one `process.md` line).
- New phase issues still to file, unlabelled: 1b-a, 1b-b, 2b, 3b. Phases 4 and 6 wait until after Phase 3's dry runs. #18 waits for Phase 2.
- N = 5 (`SWEEP_EVERY_N` in `agent-kit/scripts/sweep-due.py`) is the human's to set.
