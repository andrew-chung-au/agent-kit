# Issue #298: O13 On-call agent: mandate, guard and two jobs (handed over, not closed)

**Date:** 2026-11-17T04:04Z (UTC)
**Spec version:** 9cf7ed3

Tier: Heavy (from the PM proposal; no tier label). Session: Rubric2, which releases the issue to another agent at the maintainer's request. Rubric: On-Call Agent, toward 2 points (`.kiro/steering/rubric-priority.md`). Track C of the lane split.

This is a handover summary. The issue is open, the pull request is a draft, and no findings file is written yet: `_docs/records/findings/298.json` is written once, by whoever closes the issue.

## State at handover

- **Branch:** `claude/298-oncall-guard`, head `4fa5f51` (pushed), base `b63a91f`. Draft PR #367.
- **Body hash:** `5ac039b2fdff3ddcf654f22ddbab1291a29da9ca2c6706b2adfdd991f04b5ebc`, matches the PM's record. The maintainer approved the `## Decision record` section by name on 2026-11-17 (recorded in the claim, https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6936715594).
- **Files (6, +897 lines):** `_docs/decisions/2026-11-17T0301Z-oncall-agent-limits.md` and its `_docs/index.md` row; `observability/oncall/MANDATE.md`; `observability/oncall/guard.py` (standard library only); `tests/test_oncall_guard.py`; `_human-tasks/2026-11-17T0307Z-human-task-298-engineer-oncall-environment-and-ruleset.md`.
- **CI on 4fa5f51:** verify run 44011543391 (`VERIFY: PASS`, 3894 passed), image 44011543429, compose 44011543416, postgres 44011543495, observability 44011543389, all success.
- **QA:** two FAILs in a row on the agent tools criterion. The next QA run needs the maintainer's ruling first (`.kiro/steering/delivery-pace.md` item 9).

## Commits

- `e004f17` the decision record (first Engineer launch)
- `a7454f9` the mandate, the guard and its tests (first Engineer launch)
- `04cda94` the human task (first Engineer launch)
- `d5dd058` the mandate now names the hand-off's `--environment` and `--version`; the task checks the ruleset's approval count (second Engineer launch, after checking the first launch's commits)
- `4fa5f51` fix round 1: the guard accepts git's hunk context and no-newline lines; `--run-id` required; the action pinned and its tool options quoted

## What went wrong, in order

1. **The first Engineer launch stopped on a load error** after three commits and before its comment. The orchestrator treated the output as unverified and relaunched; the second launch re-checked every criterion and found the mandate did not mention the hand-off's `--environment` and `--version`.
2. **First QA FAIL** (https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6937293566):
   - **High:** the guard refused every real `git diff`. Its hunk-header pattern rejected the function-context text git writes after the second `@@`. The unit tests used hand-written patches with bare headers, so they passed; 60 of 60 real commits were refused. It failed closed, so nothing unsafe would pass, but the publish job could never open a pull request.
   - **Medium:** the agent tools criterion asks for option names taken from the action's README at the pinned commit. The mandate deferred them all to #299 under a `VERIFY:` note.
3. **Fix round 1** (`4fa5f51`): the parser accepts text after `@@` and `\ No newline at end of file`; 76 of 77 real in-limit commits now pass (the one refused sets an executable mode, correctly). The action is pinned to `cc98b3ae241b0fcfb6a42a2690751afffecb4452` (tag `v1.0.278`), with `--permission-mode default`, `--allowedTools` and `--disallowedTools` quoted from its docs at that commit.
4. **Re-check: QA FAIL** (https://github.com/andrew-chung-au/socboard/issues/298#issuecomment-6937776626), one Medium on the same criterion: `claude_args` sets no `--setting-sources`, so the pinned action loads the checkout's `.claude/settings.json`, any `.mcp.json`, and a `.claude/settings.local.json` the agent could write. The three flags alone therefore do not enforce "no other tool is available". Found in the action's source (`parse-sdk-options.ts`, lines 357 to 363), not by running it.

## Decision waiting for the maintainer

- **A. Fix round 2** (recommended): add `--setting-sources user` to the quoted `claude_args`, say in `MANDATE.md` that project and local settings and `.mcp.json` are not loaded, and have #299 confirm it in its run log; then one fresh QA re-check of the changed lines only.
- **B. Ship** with the Medium accepted by the maintainer's ruling, recorded here and on the issue; #299 adds the flag.
- After a second fix round, `delivery-pace.md` item 13 requires asking "ship or fix?" before any third.

## After QA PASS (Heavy gates still to run)

1. `make assert-clean`, and confirm HEAD has not moved.
2. A **second, fresh QA launch**, code review only (`process.md`, Tiers, Heavy gates; `delivery-pace.md` item 6). Its launch message says: "If this session has already reviewed, implemented or discussed this issue, stop before reviewing and say so." Under item 7 a Medium-or-higher finding fails it; Lows go in the report.
3. `make assert-clean` again.
4. Write `_docs/records/findings/298.json` (all findings below) and the closing session summary on this branch, push, and ask the maintainer to merge PR #367.
5. After the merge, check the merged head is the branch's last commit, post the Close comment (`QA PASS commit` must name the latest PASS and both launches must have passed), then `make issue-close N=298`.

## Open findings for the findings file (all Low unless stated)

From the first QA: `\ No newline` was refused (fixed in 4fa5f51); `--run-id` optional (fixed); the `check-pr` HTTP path untested and a failed close not detected; the test-file rule is broad (any file under `tests/`, a one-line change to an existing test); names beside the deny list pass (`GNUmakefile`, `pytest.ini`, `tox.ini`, `setup.cfg`, `CLAUDE.md`, `.opencode/`, `agent-kit.conf`, `.gitattributes`, `.gitmodules`); the publish job's permissions and the `git show origin/main:` form appear in no delivered file; human-task step 6 cites a community discussion.
From the re-check: the settings-sources gap (Medium, open); `Glob`, `Grep` and `WebFetch` are Claude Code names not listed in the action's docs (fail closed if wrong); `Write` can write outside the workspace; three inexact quotes in `MANDATE.md` (`WebFetch` does appear in `docs/configuration.md`; one quote is link text; the "strict list" sentence is in `docs/security.md`); the `FILE=tests/*` pattern matches trailing text and a test runs arbitrary Python with network access; the `\` skip accepts any backslash line; `check_patch(run_id=None)` still allows a missing run id for library callers; `git diff` omits untracked files, so #299 must stage before diffing; nothing scans the patch or `notes.md` for text copied from the runner's environment.

## Traps for the next agent in this environment (Kiro Web)

- `uv` cannot write its home folder, so `make test` and `make verify` cannot run Tests or Lint here. CI is the test loop (`delivery-pace.md` item 1): push, then read `gh api repos/andrew-chung-au/socboard/actions/runs?branch=claude/298-oncall-guard&event=pull_request` and the job log. Do not run `uv` with a Python from outside the project folder; an earlier Engineer asked, and it was declined.
- `guard.py` is standard library only, so a `.scratch/` script can import it with the sandbox's `python3`. Real `git diff` output from this repository's commits found the High finding; hand-written patches did not.
- `gh pr` and GraphQL calls fail here; use `gh api` REST. The draft PR cannot be marked ready from here; the maintainer clicks "Ready for review".
- Human messages are relayed to every subagent. A QA launch once stopped because it read one as its own prior work; QA launch messages now say relayed messages are not evidence of the subagent's own work.
- Write a comment file and post it in separate tool calls; a parallel write and post can race.
- Importing the guard leaves a git-ignored `observability/oncall/__pycache__/`; delete it after a check.
- Lane split: Rubric1 has #291 and #339, Rubric3 has #340, #292 and #293. `observability/oncall/` is track C. `observability/CONTRACT.md` is shared.

## Downstream

- #299 (the drill, Heavy, not labelled) pins the same action commit, writes the agent and publish jobs this issue's mandate describes, passes `--environment` and `--version` to `observability/oncall/handoff.py` (#297), and stages the agent's new files before `git diff`.

## Launch usage

- Engineer (first launch stopped on a load error; second launch; fix round 1): unknown (the tool did not report time or tool uses).
- QA (first check; re-check): unknown.

## Temporary changes

none (the git-ignored `observability/oncall/__pycache__/` left by a QA script was deleted).
