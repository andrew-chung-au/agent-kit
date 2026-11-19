# Issue #298: O13 On-call agent: its mandate and the guards that keep it from merging or pushing to main

**Date:** 2026-11-17T06:53Z (UTC)
**Spec version:** 9cf7ed3

Tier: Heavy (from the PM proposal; no tier label). This session took the issue over from the Rubric2 handover (`_session-summaries/2026-11-17T0404Z-issue-298-orchestrator-oncall-guard-handover.md`) in a Claude Code cloud session, claim https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6938015770. Rubric: On-Call Agent, toward 2 points.

## What changed and why

- Fix round 2 (`bf9ba09`): the mandate's quoted `claude_args` gain `--setting-sources user`, so the drill branch's project and local settings, hooks and `.mcp.json` are not loaded; quoted from a git checkout of the pinned action commit. Closes the re-check's Medium. QA re-check PASS: https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6940274872
- Heavy second QA launch (fresh, code review only) on `bf9ba09`: FAIL, one Medium. `make test` and `git diff` run code the agent can write, the pinned action's secret scrub was off by default, and the mandate said no other command was available. https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6940450859
- Fix round 3 (`2063b9a`): the agent job sets `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB: 1`. The patch step pins git's config (system and global off, `.git/config` hash checked, `-c core.fsmonitor=false -c core.hooksPath=/dev/null`, `add -N` before `diff --no-ext-diff --no-textconv`). The false sentence is replaced by an honest residual-risk statement naming the publish job's guard as the boundary. QA re-check PASS: https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6941017637
- `_docs/records/findings/298.json` written (21 findings, all Low).

**What I learned:** a public repository outside the session's GitHub scope can still be read with plain git through the proxy; a pinned shallow checkout in `.scratch/` gave every role first-hand quotes.

## Reflection

The roles returned these blocks in their final reports rather than as issue comments; copied unchanged in substance.

### Engineer

**What slowed you down (evidence):** the session could not read `anthropics/claude-code-action` (`gh api` refused, `add_repo` denied by the classifier), costing one handback before a pinned checkout was provided.
**What nearly went wrong or was blocked:** quoting QA's reading of the source as its own (held back); in round 3, stating `-c core.fsmonitor=false` as enough, when a planted filter driver still runs, so the hash check was added.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/team/software-engineer.md`: require a small `.scratch/` repro of any security claim the mandate makes about a tool before handover; fewer QA Mediums on wording that overstates a limit; measured as Medium findings per Heavy issue whose evidence is a QA repro.

### QA

**What slowed you down (evidence):** CI has two verify runs per head (push and pull_request merge) with different test counts, so the run on the head itself had to be picked before citing it.
**What nearly went wrong or was blocked:** a draft cleanup line in a check script would have deleted `.scratch/fix.patch`, a path the run did not create; removed before running.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/team/qa-engineer.md`: a check script cleans up only the paths it records creating, never fixed names in shared folders; no deletions of other roles' files; measured by scratch files lost per issue.

## Launch usage

Figures as each completion notification gave them; the Engineer was resumed, so its figures are cumulative.
- Engineer, fix round 2 (first stop, blocked on access): 3410191 ms, 17 tool uses
- Engineer, fix round 2 (resumed, done): 549581 ms, 23 tool uses
- QA re-check of fix round 2: 1797660 ms, 27 tool uses
- QA Heavy second launch (code review): 595149 ms, 32 tool uses
- Engineer, fix round 3 (resumed): 695581 ms, 34 tool uses
- QA re-check of fix round 3: 1061790 ms, 26 tool uses

## Files created or modified

- `observability/oncall/MANDATE.md`, `tests/test_oncall_guard.py` (fix rounds 2 and 3)
- `_docs/records/findings/298.json`
- this summary

## Decisions made by the human

- Open Medium after two QA FAILs: chose A, fix round 2 adding `--setting-sources user` (https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6938144503).
- Access to the action's source: asked to retry; the public repository was read with plain git into `.scratch/claude-code-action/` at the pinned commit, with nothing attached to the session.
- Ship or fix after the Heavy second QA FAIL: chose fix round 3, limited to MANDATE.md and its test, with the decision record and issue body unchanged (https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6940499727).
- The maintainer said to continue on the recommended path while away; no Medium was shipped unfixed.

## Mismatches with the spec or design docs

- The decision record says the agent has no network tools besides the model; true of tools, not of the code the agent runs through tests or git (F-298-21). Left unchanged by ruling.

## Commands to validate

- **Verify:** `make verify` (passed locally for each fix round; CI verify run 44032142738 on `2063b9a`, `VERIFY: PASS`).
- **Assert clean:** `make assert-clean` passed after each of the three QA launches.

## Proposed AGENTS.md changes

- The environment line could note that a Claude Code cloud session runs `uv` and `bun` (unlike Kiro Web), so `make verify` runs locally there. Not applied; for the maintainer.

## Temporary changes

- `.scratch/claude-code-action/`: a shallow git checkout of the pinned action commit, read-only; removed by `make clean-scratch`.
- `.venv/` and `frontend/node_modules/` from `make install` (git-ignored, the normal install).
- No process started; no system change.

## Interruptions

- The session's worker restarted once after the claim was posted; the claim was confirmed on the issue and work continued.
- The Engineer's first fix-round-2 run returned BLOCKED on repository access with nothing committed; it was resumed with the pinned checkout.

## Unrelated problems noticed but not fixed

- F-298-1: The check-pr HTTP path is untested and a failed close is logged as closed.
- F-298-2: The test-file rule is broad and its pattern matches a non-test module.
- F-298-3: Several build and config files beside the deny list pass the guard.
- F-298-4: The publish job's permissions and the guard-from-main form are in no delivered file.
- F-298-5: Human task step 6 relies on a community discussion.
- F-298-6: Glob, Grep and WebFetch are not listed in the action's docs.
- F-298-7: Write can write outside the workspace, unseen by the patch.
- F-298-8: Three mandate statements about the action's docs are inexact.
- F-298-9: The make test-one Bash pattern matches trailing text.
- F-298-10: Loose backslash skip, optional run id for library callers, dead run-id test.
- F-298-11: Nothing scans the patch or notes for runner secrets.
- F-298-12: The mandate credits the wrong function for settingSources.
- F-298-13: The .mcp.json claim depends on the CLI, not the action's code.
- F-298-14: The user setting source stays on; its effect on agent writes is for #299.
- F-298-15: The deny-list test checks one direction only.
- F-298-16: check_pull_request does not check base or head ref.
- F-298-17: The guard refuses edits to existing executable files even without a mode change.
- F-298-18: A security.md quote is attributed to the scrub variable rather than its bullet.
- F-298-19: Actions cache writes are not named in the residual risk.
- F-298-20: An ignore rule can keep a new file out of add -N.
- F-298-21: The decision record's "no network tools" wording.

## Follow-ups for the next session

- The maintainer merges PR #367 (and marks it ready for review). After the merge: check the merged head is `2063b9a` or this summary's commit, post the Close comment naming `QA PASS commit: 2063b9a`, then `make issue-close N=298`.
- A sweep is due (`make sweep-due`: 48 closed since 2026-11-14).
- #299 picks up F-298-4, -7, -11, -13, -14, -19 and the job contract in MANDATE.md.
