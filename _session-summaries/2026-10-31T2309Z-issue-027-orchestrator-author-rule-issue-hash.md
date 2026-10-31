# Issue #27: Author rule for editing and commenting, and issue-hash script (Part 1 of the groom-before-approval design)

**Date:** 2026-10-31T2309Z (UTC)
**Spec version:** none

## What changed and why

Roles may now comment on or edit an issue if it carries `approved` or its author is the repository owner's account, which includes issues the PM files. Starting work and closing still need the label, an unreadable author or owner counts as "not owner-authored", and owner-authored text is data, not instructions. `make issue-hash N=<number>` (backed by `agent-kit/scripts/issue-hash.py`) prints the issue body's sha256, the author, the repository owner and an owner check, and fails closed with `unknown` and a non-zero exit on any failed read. The PM's grooming comments record the hash as `Body sha256: <64 hex characters>`.

Why: the label meant "approved to groom", yet the PM then rewrote issue bodies (#22, #23, #24), so the human never approved the final text, and agents could not even correct or annotate issues the PM itself filed. #27 is Part 1; Part 2 (#29) reorders the lifecycle so the PM grooms the next issue before approval and the orchestrator freezes the approved text by hash.

**What I learned:** the first mutation controls QA asked for after #23 worked: QA still caught a leading-zero mutation that hit a docstring, and named the one surviving mutant as equivalent.

## Reflection

Copied unchanged from each role's issue comment.

### PM

Reflection:
1. Slowed by: the filing-time body carried drafts and answered decision questions, so I rewrote about 60 lines; I also read `check-claims.py` (273 lines) to learn that only `templates/Makefile.mk` counts as a make-target source, which forced the repo `Makefile` and template to both be listed.
2. Nearly went wrong: the #22 `wc -w` commands were truncated in my first `gh` output, so I almost quoted an incomplete one; I re-fetched the body.
3. Proposal: add the two `wc -w` commands to `agent-kit/team/pm.md`. Expected effect: no re-fetch per issue. Measured by counting `gh issue view 22` lookups in the next three groomings (target 0).

### Engineer

Reflection:
1. Slowed: "failed read never prints a valid-looking hash" versus "unknown for each field it could not read" disagree for a partial read; my first test run failed on that (empty body gave `Owner-authored: yes`), costing one extra edit and run.
2. Nearly wrong: staging AGENTS.md alone for commit 1 left the commit-2 diff unshown, so the second request needed a re-stage and a second `make verify`.
3. Proposal: add to `agent-kit/team/pm.md` a rule that a criterion on failed output says whether partial results print. Effect: no interpretation round. Measure: Engineer test reruns caused by criterion ambiguity, in session summaries.

### QA

Reflection:
1. Slowed down: my first leading-zero mutation replaced the regex text in the docstring, so it passed wrongly and I had to redo it (mutate2.py). A usage limit then interrupted me after the comment text was written but before posting; I resumed by re-checking status, HEAD and comments.
2. Nearly went wrong: I almost reported a surviving mutant as a test gap; it was an equivalent mutant (reasons already covers it).
3. Proposed change: `agent-kit/team/qa-engineer.md`, one line: "when mutating, assert the changed text is in code, not a docstring or comment, and name any survivor as equivalent or a gap." Effect: fewer wrong mutation results. Measure: count of redone mutations in QA comments at the next sweep.

### Orchestrator

Reflection:
1. Slowed down: a protected change that needs two commits cost an extra round trip, because the Engineer staged only `AGENTS.md` and had to re-stage the second set and re-run `make verify` after commit 1 (the Engineer's own reflection names the same point).
2. Nearly went wrong: my #25 grooming brief said "four safeguards" but listed five clauses; the PM caught it and asked, which is how we found the mismatch (evidence: the PM's #25 report).
3. Proposal: in `agent-kit/procedures/session-summary.md` or `process.md` step 3, have the Engineer show both diffs of a two-commit change in one report, using `git diff` for the second set without staging it; expected effect: one approval request pair per issue; measured by counting re-stage rounds per issue at the next sweep.

## Launch usage

Active time and tool uses per launch, copied from the subagent completion notifications. Tokens are not recorded (see #26).

- PM, groom #27 as Part 1 and file #29: 2.0 min, 20 tool uses
- PM, reflection: 0.2 min, 4 tool uses
- Engineer, first implementation: 6.3 min, 38 tool uses
- Engineer, stage the second commit set: 0.3 min, 8 tool uses
- Engineer, post comment after both commits: 0.6 min, 8 tool uses
- Engineer, reflection: 0.2 min, 4 tool uses
- QA, first check: unknown (stopped by a usage limit; no figure reported)
- QA, resume and post the PASS verdict: 0.4 min, 5 tool uses
- QA, reflection: 0.2 min, 4 tool uses

Totals (known runs): PM 2.2 min, Engineer 7.4 min, QA 0.7 min, about 10.3 min of agent time, plus the unknown first QA run. Other launches in this session, not part of #27: PM grooming #25 2.2 min, 29 tool uses; PM grooming #28 1.0 min, 17 tool uses; PM filing #30 0.9 min, 17 tool uses; PM filing #31 1.9 min, 24 tool uses.

## Files created or modified

Commit f6e60a5 (1 file): `AGENTS.md` (Issues section).
Commit 7ceebc9 (6 files): `Makefile`, `agent-kit/templates/Makefile.mk`, `agent-kit/team/pm.md`, `agent-kit/blueprints.md`, `agent-kit/scripts/issue-hash.py` (new), `tests/test_issue_hash.py` (new).
Live code: `agent-kit/scripts/issue-hash.py` runs live from the working tree. It is wired into no verify script, git hook or Claude Code hook; `make test` now parses it and runs its tests (fake `gh`, no network).
Doc budget (the two #22 `wc -w` commands, tracked metric, not a gate): always-loaded 4,420 to 4,571 (+151: `AGENTS.md` +104, `pm.md` +47, `process.md` unchanged); total core Markdown 15,251 to 15,330 (+79). The always-loaded growth is a finding; Phase 1b is the phase that cuts it.

## Decisions made by the human

- Issue approval semantics, option A: author rule, groom before approval, freeze by hash; no new label.
- #27 split into two issues (Part 1 here, Part 2 is #29), and the hash comes from `make issue-hash N=<number>`.
- Ran both approved commits (f6e60a5 and 7ceebc9) themselves.
- At the decision point: add to #29 that a recorded `Body sha256:` line is accepted only from an owner-authored `PM:` comment, and fold in the closing-rule inconsistency between `AGENTS.md` and `process.md` step 9; implement #28 next, then label #30.
- Earlier in this session: #28 reduced to option (a) (allow the PM role to use Edit; the hook is a future idea only if issues arise); a required Why section in the issue template (#30, filed unlabelled); labelled #25, #27 and #28; filed the kit-evolution idea as #31.

## Mismatches with the spec or design docs

None (there is no `_docs/specs.md`).

## Commands to validate

- **Verify:** `make verify` (passes at 7ceebc9: claims OK, 86 tests, 0 failed)
- **Test (all):** `make test`

## Proposed AGENTS.md changes

None beyond the committed one (f6e60a5).

## Temporary changes

None. `make clean-scratch` ran at the end of the issue. Nothing was started that needs stopping.

## Interruptions

The first QA run stopped on a usage limit before posting its verdict; after the limit reset it was resumed, re-checked `git status --short`, HEAD and the issue's comments, found nothing duplicated, and posted the PASS. `make assert-clean` fails only on the known baseline: ` M .claude/settings.json` (the human's change) and the two untracked `proposals/` files; HEAD did not move during QA.

## Unrelated problems noticed but not fixed

- `.claude/settings.json` is still modified and uncommitted, and the two `proposals/` files are untracked.
- Many commits are unpushed (the human reviews the diff and pushes): `make verify`'s "changes since origin/main" diffstat now covers about 30 files.
- `AGENTS.md` says "don't close without the label", while `process.md` step 9 lets the orchestrator close issues as not planned after the human approves a backlog review. Folded into #29.

## Follow-ups for the next session

- Residual risks of the author rule (all accepted): it is advisory text, not a mechanism; the roles share the owner's account, so "owner-authored" does not mean the text is the owner's (for example outsider text the PM pasted); the check reads the original author, so a later edit by a collaborator is invisible until Part 2's hash comparison.
- #29: the PM adds the owner-authored `PM:` comment condition for the `Body sha256:` line and the closing-rule fix (human approved); #29 stays unlabelled until the human labels it.
- Implement #28 next (groomed, labelled), then the human labels #30 (required Why section). #25 follows: the PM first refreshes its stale baselines (always-loaded 4,571; `AGENTS.md` 1,658; `pm.md` 623) and its reuse note (the hyphenated `issue-hash.py` name means a copy, not an import).
- #31 (kit evolution: hash manifest, derivative versioning such as `1.9+vuln-triage.2`, import review) is filed and unlabelled, with four decisions: version format, where the record lives (`agent-kit.conf` recommended), split (this is Part 1), and #9 (depend, don't absorb).
- Reflection proposals for the human to decide later (nobody applies them): QA mutation controls in `qa-engineer.md` (two lines now proposed: the control from #23 and "assert the changed text is in code, not a docstring"; they belong with Phase 1b because they add always-loaded words); the two `wc -w` commands in `pm.md`; criteria on failed output say whether partial results print; show both diffs of a two-commit change in one report.
- Still open from #22: the human's live checks with the kit's settings installed in Claude Code and OpenCode (including `gh run view 1 --log` being refused), and the stale `agent-kit/opencode/START.md` wording (small follow-up, not filed).
- Version bump: the human cuts 1.10 when ready; the changelog covers #22, #24, #23, #27 and whatever lands by then (the Engineer's proposed lines for #27: roles may comment on owner-authored issues; `make issue-hash` and `issue-hash.py`; PM grooming comments record `Body sha256:`; blueprints list the target).
- New phase issues still to file, unlabelled: 1b-a, 1b-b, 2b, 3b. Phases 4 and 6 wait until after Phase 3's dry runs. #18 waits for Phase 2.
