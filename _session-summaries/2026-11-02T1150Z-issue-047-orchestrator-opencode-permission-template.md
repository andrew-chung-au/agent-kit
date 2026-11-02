# Issue #47: OpenCode permission template refresh (split from #13)

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-02T11:50Z (UTC)
**Spec version:** none

## What changed and why

The OpenCode permission template (`agent-kit/opencode/opencode.json`) and this repo's live `opencode.json` were refreshed so routine read-only commands stop prompting while commits, protected files, secrets, broad staging and pushes stay gated. It started as OpenCode's rewrite of #13 for the vuln-triage `opencode.json`; the PM split #13 into 13a (`issue-dump` and the make-variable rule, still #13) and this issue, and fixed eight problems the human and orchestrator found in the draft (`echo *`, `jq *`, `git fetch*`, a raw `gh issue comment*` allow, chain handling, silent `--amend`, remote URLs, `*--output*`) plus token-printing denies.

Four protected commits, each approved by the human as an exact diff and committed by them with `HUMAN_APPROVED=1` and a pathspec:
- A = 0ab8586 (kit files and tests) and B = 0601022 (this repo's live `opencode.json`, a one-line `AGENTS.md` change, `tests/test_repo_opencode.py`).
- QA FAILED at 0601022 (one stale README line: "OpenCode has no shell guard until #13"; plus gaps in the rule list). The human chose option B: the PM revised the body, filed #49 for the rest, and the human confirmed the new body hash (`cd4e6f2f490e90b848b437448e44dc80cf16a38fb53686d3a22c1c04750242a3`).
- A2 = 1ac8f64 (README line; `git diff*` and `git show*` replaced by exact and ` *` forms so `git difftool` and `git show-ref` no longer match; `git commit *--no-v*` deny and `*--am*` ask for option abbreviations; chain wording corrected to per-command checking; new tests) and B2 = 38f04f4 (this repo's `opencode.json` again equal to the template).
- QA PASS at 38f04f4: 18 of 19 mutations caught (one redundant rule, one pre-existing test gap), `make verify` 371 tests, no new gap from this change.

Words (`wc -w`): first round `START.md` 543 to 1053 (estimate +360, overshot by about 150), `environments.md` 1217 to 1378 (+161); revision `START.md` +13 to 1066 (cap 1070), README +11. Total across the five files in the revision +24.

**By-hand OpenCode 1.19.5 results (human, one model, one session; recorded on #47):** `ls | head`, `ls ; pwd` and `ls && pwd` ran silently; `ls ; touch…`, `ls && touch…`, `ls $(pwd)`, `ls > .scratch/out1`, `head -n 1 /etc/hostname`, `ls /`, `ls ..` and `git commit --amend --dry-run -m x` prompted; `git commit -n -m x`, `ls .env` and `gh auth token --help` were denied by the named rules; `git commit --dry-run -m x` ran silently. Conclusion: OpenCode checks each command of a chain on its own, so the whole-line asks for `;`, `&` and `|` are inert (kept, harmless) while the asks for `$(...)`, backticks, redirects and paths fire. The commit abbreviations (`--no-v*`, `--am*`) were not tried in a real session.

**What I learned:** an agent will refuse a command on its own judgment before a permission rule is reached, so refusals prove nothing about the rules; a rule is only tested when the agent is told to make the tool call and the tool decides. And the human's `!` shell prefix bypasses permission rules.

## Reflection

### Engineer

1. What slowed me down: START.md overshot its word cap twice (first round 543 to 1053 against +360; the revision first came out at 1219 against a cap of 1070), so I trimmed in about six passes with a `wc -w` after each; the estimates were set before the text existed.
2. What nearly went wrong: the body required `--allow-empty-message` to stay allowed while an existing deny `git commit *--all*` matched it; only the test run exposed the conflict, so I narrowed that deny beyond the stated scope and reported it.
3. Proposed change: `agent-kit/team/software-engineer.md`, add "when an issue states a word cap, draft the doc text first, run `wc -w`, and cut before writing tests". Expected effect: no trim passes after the tests are written. Measure: count of `wc -w` trim passes per issue in the Engineer comment, from about six to at most two.

### QA

1. Slowed down: I had no Edit tool, so fixing my own mutation script meant writing wrapper scripts (`qa47-mutate2.py`, `qa47b-run2.py`); the first runs of each failed on test-copy setup (unittest import, missing `process.md`).
2. Nearly went wrong: my first mutation `x5` was a silent no-op that would have reported a false "survived"; I only saw it on reading the code, and the `qa47b` script now asserts each mutation changed its target.
3. Proposal: add a short "mutation check" recipe to `agent-kit/team/qa-engineer.md` (copy `agent-kit/` and `tests/` to `.scratch/`, run the unmutated copy first, assert each mutation changed something). Effect: fewer failed setup runs; measure by counting setup-failed script runs per QA pass.

### PM

1. Slowed down: #47 was groomed three times (draft rewrite, human answers, option B), and the pattern list needed 8 findings, then 7 QA gaps, because no one had stated git's option abbreviations or sibling subcommands up front; `.scratch/` was also emptied between my runs, so I rewrote the body file from context.
2. Nearly went wrong: placing the metacharacter `ask` rules after the denies would have downgraded `git push $X` to ask; the body's "chains prompt" claim was wrong until the by-hand run showed OpenCode 1.19.5 splits chains.
3. Proposal: add to `agent-kit/team/pm.md` one line, "For allow/deny pattern lists, list the tool's option-abbreviation, sibling-subcommand and chain behaviour, verified or marked unverified"; expected effect: fewer QA gaps per list; measure by counting pattern-list gaps in QA comments on the next two permission issues (this one had 7).

## Launch usage

- PM (split #13, file #47): 400.3 s, 56 tool uses
- PM (order notes on #13 and #44): 31.7 s, 9 tool uses
- PM (settle the decisions, add token scopes): 95.8 s, 16 tool uses
- PM (revise for option B, file #49): 243.0 s, 18 tool uses
- PM (reflection, resumed): 20.1 s, 3 tool uses
- Engineer (round 1, commit A request): 2859.0 s, 49 tool uses (includes waiting for approvals)
- Engineer (stage B, resumed): 80.8 s, 7 tool uses
- Engineer (revision, A2): 273.7 s, 52 tool uses
- Engineer (stage B2, resumed): 355.0 s, 59 tool uses (as reported; may include earlier resumed runs)
- Engineer (comments and reflection, resumed): 435.9 s, 64 tool uses (as reported; may include earlier runs)
- QA (check at 0601022, FAIL): 259.4 s, 27 tool uses
- QA (re-check at 38f04f4, PASS): 131.4 s, 12 tool uses
- QA (reflection, resumed): 154.6 s, 15 tool uses (as reported; may include the earlier run)

## Files created or modified

- `agent-kit/opencode/opencode.json`, `agent-kit/opencode/START.md`, `agent-kit/environments.md`, `agent-kit/README.md`, `agent-kit/templates/AGENTS.md.template`
- `opencode.json`, `AGENTS.md` (one line)
- `tests/test_permissions.py`, `tests/test_kit_env_and_launch.py`, `tests/test_repo_opencode.py` (new)
- This summary.

## Decisions made by the human

- Order: #47, then #13, then #44; content readers allowed with asks; strict `*.env*` deny with no `.env.example` allow in bash; token scopes (code read, issues read and write, no user permissions; single-repository scope not verified) with the stated limit that the token can add the `approved` label; silent plain commits (`--amend` prompted).
- Option B after QA FAIL; the revised body hash confirmed; the inert `;`, `&`, `|` asks kept.
- Approved the four exact diffs and made the commits; ran the by-hand OpenCode checks.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none this round. `AGENTS.md` still says "your GitHub token is read-only", which no longer matches the stated scopes (issues are writable); a possible small follow-up.

## Temporary changes

none

## Interruptions

none. The orchestrator's usage limit forced a handover to OpenCode, which hit its own limit quickly; the work resumed here.

## Unrelated problems noticed but not fixed

- Test gap: no test pins this repo's `AGENTS.md` "Enforced by hooks" line (only the template's); #49 may take it.
- The redundant `git commit *--all` rule and the redundant `*--amend*` rule are kept for existing tests.
- The Engineer's estimates for word counts were set before the text existed and overshot twice.

## Follow-ups for the next session

- #49 (unlabelled): path forms, recursive grep, `git config --get`, `make *`, the stale `guard_git.py` docstring; two PM decisions with defaults.
- #13 (approved, next), then #44 (approved, also waits for #20), #20's stage 1 gate (OpenCode runs now).
- The human's by-hand check of the commit abbreviations (`git commit --no-veri -m x` denied, `git difftool` prompted) in a restarted OpenCode.
- The human's request for a folder of reviewable human-task instructions (a PM issue is being filed).
- Push from the clean clone: about 66 commits; the push check needs Docker.
