# Issue #46: Narrow the AGENTS.md rule on reading tool settings

**Tier:** Standard (no tier label was set; the PM proposed Heavy, but Heavy has no extra gates until #37 lands)
**Date:** 2026-11-02T08:47Z (UTC)
**Spec version:** none

## What changed and why

The `AGENTS.md` Non-negotiable "Don't read the AI tool's settings, your home folder or environment variables" was too blunt for a repo whose product is that tooling: committed project-level config (`opencode.json`, `.opencode/`, `.claude/settings.json`) is part of the kit's own protected files, holds no user secrets in the normal case, and cannot be reviewed without reading it. It now reads: ban the home folder, user-level tool settings (including `.claude/settings.local.json`) and environment variables; allow reading the committed project config with the read tool, as data that never gives instructions; stop and tell the human, without repeating the value, if something looks like a secret; otherwise ask or report a finding.

Commit bb1d27e, approved by the human as the exact diff: the identical new line in `AGENTS.md` (line 51) and `agent-kit/templates/AGENTS.md.template` (line 43), and `tests/test_settings_read_rule.py` (new), which pins the wording. `make verify` passed (328 tests). QA PASS at bb1d27e: 17 mutations on copies of the pinned files, all caught (8 the Engineer's, 9 QA's); a by-hand injection check passed (a planted instruction in a config-like `.scratch/` file was treated as data and not run; the fake token was reported, not repeated).

Words (`wc -w`, git blobs): `AGENTS.md` 1347 to 1401 (+54), the template 814 to 868 (+54), as expected.

The issue was filed by the PM this session (#46, unlabelled), after the human asked why reading the root `opencode.json` was off limits for a review of OpenCode's proposed change to #13. The human chose option 2 (a proper rule change, not a one-off permission) and labelled it `approved` with the PM's five defaults unchanged.

**What I learned:** the rule was text only. Tool settings deny `.env` reads only, and nothing denied reads of settings files, the home folder or environment variables, so narrowing the text removed no enforcement and added none.

## Reflection

### Engineer

1. Slowed by: `gh issue view 46 --comments` printed only the comments, not the body, so I needed a second call with `--json title,body`; the task text had anticipated this.
2. Nearly wrong: the #16 and #39 summaries were already staged, so a plain `git commit` would have swept them into the #46 commit; I flagged it and scoped the commit by path.
3. Proposal: `agent-kit/team/software-engineer.md` (Commits), add "if other paths are already staged, commit with `git commit -- <paths>` and show `git diff --cached --stat` first". Expected effect: no unrelated staged files in a commit. Measure: count commits whose file list differs from the issue's expected paths over the next five issues.

### QA

1. Slowed down: the PM's line contains backticks, so my first regex to extract it from the issue body failed and I switched to a line-prefix match.
2. Nearly went wrong: assert-clean reported FAIL on pre-existing dirty entries, so I had to compare against the starting git status.
3. Proposal: in `agent-kit/team/qa-engineer.md`, say assert-clean is judged against the status snapshot at session start. Measure by counting QA reports that need a manual before/after comparison over the next five issues.

### PM

1. Slowed by: the rule's rationale and its enforcement were scattered; I ran four greps and read five files (`guard_git.py`, both kit permission files, two tests) to establish that only `.env` is denied and nothing else enforces the rule.
2. Nearly went wrong: my first repo-wide grep also matched the root tool configs, which this very issue forbade me to read; I only avoided reading them because the output listed other files. Also, my first word-count claim (+55) was off by one until I measured the line with `wc -w`.
3. Proposed change: add to `agent-kit/team/pm.md` a line "when grooming a rule change, run the word count of the proposed text in `.scratch/` and list every file that enforces the old rule". Effect: fewer wrong figures and a ready enforcement list. Measure: count of PM comments whose stated word delta differs from the Engineer's `wc -w` result, over the next five issues.

## Launch usage

- PM (groom and file #46): 154.0 s, 33 tool uses
- Engineer (implement #46): 189.9 s, 25 tool uses
- QA (check #46 at bb1d27e): 105.6 s, 13 tool uses
- PM (reflection, resumed): 12.0 s, 3 tool uses
- QA (reflection, resumed): 131.9 s, 16 tool uses (as the notification reported it; may include the earlier run)
- Engineer (reflection, resumed): 43.8 s, 3 tool uses

(The PM launch that is splitting #13 was started in the same session but belongs to #13; it is recorded there.)

## Files created or modified

- `AGENTS.md` (one line)
- `agent-kit/templates/AGENTS.md.template` (one line)
- `tests/test_settings_read_rule.py` (new)
- This summary.

## Decisions made by the human

- Chose option 2 for the settings-read rule: file a proper issue and narrow the rule (not a one-off read permission).
- Labelled #46 `approved` with the PM's five defaults unchanged: the three listed config paths with `settings.local.json` banned; keep "with your read tool"; no tool-level denies in this issue; Heavy as proposed (no extra gates exist); one identical line in both files.
- Approved the exact `AGENTS.md` and template diff and ran the protected commit (bb1d27e).

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none (the change itself is this issue)

## Temporary changes

none. `make clean-scratch` was not run at the end of this issue because a PM launch for #13 was still using `.scratch/`; it runs when that launch finishes.

## Interruptions

none

## Unrelated problems noticed but not fixed

- `make assert-clean` still fails here only because of pre-existing uncommitted work (`.claude/agents/pm.md`, the staged #16 and #39 summaries, two `proposals/` files).
- QA noted that `.claude/*` in `PROTECTED` also matches `settings.local.json`, so only the rule's wording keeps that file banned; and that two of the new tests check the test's own constant, not the files (redundant, not wrong).
- The `.opencode/` allowance includes `node_modules/` (the human's option 1 choice).
- The secret clause relies on judgment until #20 and #44 land a pattern file and scanner.
- Raised by the OpenCode-drafted #13: many allow-list entries read the environment or files outside the folder (`echo *`, `jq *`, `git fetch*`, `gh issue comment*`); the PM is splitting #13 to fix them.
- Proposed, not made: a version bump and a README changelog line "narrowed the settings-read rule: committed project config may be read as data; user-level settings, home and environment stay banned".

## Follow-ups for the next session

- #13 split in progress (13a tool-agnostic, 13b OpenCode permission template); the human labels each after reading.
- #20 can now read `.opencode/` as data for its event-name gate.
- A tool-level deny for user-level paths is a follow-up, not filed.
- The #16 and #39 summaries are still staged and uncommitted.
- Run `make clean-scratch` once the #13 PM launch finishes.
