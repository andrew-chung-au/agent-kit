# Issues #60, #37 and #61: permission settings

**Date:** 2026-10-22
**Spec version:** 97893c1

Scheduled outside `_docs/roadmap.md` at the human's direction (2026-10-22), on branch `claude/beautiful-lovelace-la54rn`, so the tooling work stayed apart from the product session working step 10 (#56). Corrected 2026-10-22 after QA: the Engineer's first version of this summary described the work as uncommitted and not applied; this version describes the committed state.

## What changed and why

- #60 and #37 (`a5b21c0`, one protected commit): `.claude/settings.json` no longer allows `Bash(gh api repos/*)`, which let flag-after-path writes (close an issue, post or delete a comment) run without a prompt. It now asks for `Bash(gh api *)`, matching `opencode.json`, and asks before edits to `.devcontainer/`, `.githooks/`, `.github/` and `.vscode/`. The PM found that #60's Option B (ask rules for write flags) is not safe, because `--method=PATCH`, `-XPATCH` and `-fstate=closed` slip past it.
- #61 (`2520c9c`, `4c42cf3`): `make permission-report SINCE=<commit>` (read-only, session summaries only, rejects any `SINCE` that is not 7-40 lowercase hex and a commit) and `_docs/agent-kit/scripts/permission-report.py`; `AGENTS.md`, `process.md`, the session-summary template and procedure no longer ask sessions to propose settings changes; new `_docs/agent-kit/procedures/permission-sweep.md` (allow a read-only pattern after three distinct session summaries, never allow `python3`/`bash .scratch/*`, writes stay on ask, risky items get a deny proposal and go to the human at their own decision point).
- `509215b`: `_docs/cloud-sessions.md` line 46 now matches the settings, new `_docs/permission-sweeps.md` (last-sweep record, placeholder for the first sweep issue), usage log, Engineer summary.

## Files created or modified

- Protected, each committed alone with `HUMAN_APPROVED=1`: `.claude/settings.json` (`a5b21c0`); `Makefile` and `_docs/agent-kit/scripts/permission-report.py` (`2520c9c`); `AGENTS.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/templates/session-summary.md`, `_docs/agent-kit/procedures/session-summary.md`, `_docs/agent-kit/procedures/permission-sweep.md` (`4c42cf3`).
- Unprotected: `_docs/cloud-sessions.md`, `_docs/permission-sweeps.md`, `_docs/ai-usage-log.md`, this summary.
- Approval records: #60 6330381464, #37 6330381694, #61 6330381921 (`2520c9c`) and 6330382170 (`4c42cf3`).
- GitHub comments: PM 6330134485 (#60), 6330134704 (#37), 6330137277 (#61); human's decisions 6330251791 and copies; Engineer 6330334016 (#60), 6330335550 (#37), 6330334233 (#61); QA 6330439958 (#60), 6330440182 (#37), 6330440402 (#61).

## Decisions made by the human

- All six PM decisions as recommended: #60 remove the allow rule and add a `Bash(gh api *)` ask rule; one commit for #60 and #37; #61 limited to the target and the template/rule change, with the first sweep as a new issue after #60 and #37 land; a read-only pattern is proposed for allow after three distinct sessions; the last sweep is recorded in `_docs/permission-sweeps.md`; the report reads session summaries only.
- Approved the three protected diffs as drafted by the Engineer (settings; Makefile and script; rules and procedure).
- Kept this work off `_docs/roadmap.md` and on its own branch.

## Mismatches with the spec or design docs

- none

## Commands to validate

- **Verify:** `make verify` PASS (62/62) on the pre-push run and in QA's run with `BASE=6d6c3ba`; `make assert-clean` PASS at `509215b` after QA.
- `make permission-report SINCE=1b37fd1` on the real tree, and a refused case (`SINCE=main`, exit 2); QA ran 31 bad `SINCE` values with no injected output.
- Not verified: a live Claude Code prompt for the `gh api` and four `Edit` rules. It needs a session started after `a5b21c0`; whether settings load at session start is still a `VERIFY:` item in the sweep procedure.

## Temporary changes

- `.scratch/` scripts and comment files; `make clean-scratch` run at the end of the session.
- No processes started; no system configuration changed.
- The orchestrator applied the human-approved diffs with `git apply` on the Engineer's patch files instead of the editor, so each applied change matched the approved text exactly; each commit's diff is in its approval record.

## Permission review

PM and Engineer comments list no command that required approval. QA lists none known. None of the three can see whether the tool prompted for an `ask`-rule command.

- Read-only (propose allowing): none
- Writes to the record (keep asking): `HUMAN_APPROVED=1 git commit` of `a5b21c0`, `2520c9c`, `4c42cf3`; `git apply` of approved diffs onto protected paths (the `Edit` ask rules on those paths); `git push -u origin claude/beautiful-lovelace-la54rn` (the cloud-session exception); `make issue-comment` on #37, #60 and #61 (allowed target); `make issue-close` on the three issues (ask rule `Bash(make issue-close*)`)
- Risky (propose denying): none

## Interruptions

- The stop hook asked for a commit and then a push while the Engineer and QA were still running. The unprotected files were committed after the Engineer finished and the branch was pushed once, before QA finished.

## Unrelated problems noticed but not fixed

- `Bash(make issue-close*)` only matches commands that start with `make issue-close`. By the rule shapes, `make -s issue-close`, `make N=1 issue-close` and `make -C . issue-close` match the `make *` allow and no ask, which is the same family as the hole #60 closes (QA risk, existed before this branch). The human is asked whether to file a follow-up.
- The report is a heuristic: it counts `.scratch/` in #23's `make openapi-validate` bullet under the `.scratch` pattern, counts `gh issue edit` for #58 where it was only blocked, and shows "none ... `command`" bullets under "read by hand" instead of Risky.
- `HUMAN_APPROVED=1 git commit` counts 6 not 7 because the #21 summary is in the root commit, which `SINCE..HEAD` cannot include.
- The #60 Engineer comment has one stray duplicated output line; comments cannot be edited. The #61 PM comment says `AGENTS.md` lines 73-79 for the Permission review rule, which starts at line 72.
- The four Edit-ask folders are not in `PROTECTED`, and Claude Code `Edit` asks cover its Edit/Write tools, not shell writes.
- Build and QA both ran as claude-sonnet-5-5 in Claude Code; QA ran in a fresh subagent context and no different model was available.

## Follow-ups for the next session

- Human: in a session started after `a5b21c0`, try the six `gh api` commands from #60 against issue `999999999`, declining each prompt, and one harmless file edit under each of the four new ask folders.
- File the first-sweep issue now that #60 and #37 are done, and put its number in `_docs/permission-sweeps.md` (needs the human's go-ahead to file).
- Decide whether to file the `make issue-close` argument-order follow-up.
- Merge note: this branch and the product branch both append to `_docs/ai-usage-log.md`.
