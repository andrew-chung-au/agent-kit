# Issue #39: Block shell reads of .env files in the Claude Code Bash hook (follow-up to #35)

**Date:** 2026-11-01T11:57Z (UTC)
**Spec version:** none

## What changed and why

The Claude Code Bash hook (`guard_git.py`) now blocks any shell command that names a `.env` file, other than `.env.example`, so `cat .env` and its relatives no longer rely on the tool settings alone. A match is the last path component of an argument, or the value of `--opt=value`, with a leading redirect (`<`, `>`, `>>`, `2>`) and quotes or backticks stripped. Assignments whose value names `.env` (`f=.env`, `FILE=.env cat`) are refused too, which is stricter than the issue wording. Malformed input fails open, as before. `bash -c`, globs, `$f` and `cat *` stay documented gaps, pinned by a test. `AGENTS.md`, its template, the README, both START.md settings rows and the pinning test now say that Claude Code's hook blocks shell commands naming `.env` files and OpenCode does not (#13).

Commit: ece19f0. QA: PASS at ece19f0 (about 100 payloads probed; `make verify` 285 tests). Issue closed by the orchestrator.

**What I learned:** a leading-redirect strip needs the digit-prefixed forms (`2>`); only the Engineer's own odd-shape tests caught it, because the issue listed just `<` and `>`.

## Reflection

### Engineer

Reflection:
1. Slowed down: two Edit calls to `guard_git.py` were denied mid-task after three had succeeded, which left `test_env_commands_refused` failing on `cat 2>.env` until the human allowed the edit (one extra handback round trip).
2. Nearly went wrong: my first redirect strip (`lstrip("<>")`) missed `2>.env`; only my own odd-shape test cases caught it, since the issue's criteria listed just `<` and `>`.
3. Proposed change: in `agent-kit/team/software-engineer.md`, add under "Stay inside the files and constraints the issue names" that when an issue lists protected files, the Engineer asks for edit approval for all of them in one request before the first edit. Expected effect: no mid-task denial and no half-finished state. Measure: count of denied edits per issue in session summaries (target 0 across the next five protected-file issues).

### QA

Reflection:
1. Slowed by: `make verify` prints a 82-file "changes since origin/main" diffstat that buries the 8-file #39 commit, so I needed a separate `git show --stat` to size the work.
2. Nearly wrong: the hook's non-dict JSON and non-string `command` inputs crash with exit 1 instead of failing open; the body's "fail open, as today" was ambiguous, so I judged it outside the criteria and reported it as a risk.
3. Proposed change: `agent-kit/team/qa-engineer.md` (or the issue template) should say which malformed inputs count as "malformed" for a hook criterion. Effect: fewer judgment calls on edge inputs. Measure: count QA comments whose "Outside the criteria" lists a fail-open ambiguity, over the next five hook issues.

### PM

unknown (role not asked)

## Launch usage

- Engineer, implement #39 (stopped on a denied edit): 3m02s active, 22 tool uses.
- Engineer, resumed after the human allowed the edit: 1m00s active, 12 tool uses.
- QA, check (PASS): 1m15s active, 13 tool uses.
- Engineer, resumed to post its comment: 1m54s active, 19 tool uses.
- Engineer, resumed for its reflection: 14s active, 3 tool uses.
- QA, resumed for its reflection: 1m43s active, 16 tool uses.

The two PM grooming launches for #37 and #40 in the same session are not counted here; they belong with those issues.

## Files created or modified

- Modified: `agent-kit/claude-code/hooks/guard_git.py`, `AGENTS.md`, `agent-kit/templates/AGENTS.md.template`, `agent-kit/README.md`, `agent-kit/claude-code/START.md`, `agent-kit/opencode/START.md`, `tests/test_guard_git.py`, `tests/test_kit_env_and_launch.py` (the pinning test is renamed `test_hook_line_says_claude_code_blocks_shell_env_and_opencode_does_not`).
- 8 files, +112/−8.

## Decisions made by the human

- Earlier, in the issue: `bash -c` and indirection stay a documented gap; any command naming `.env` is blocked, including `cp .env.example .env`, `ls .env` and `git check-ignore .env`; docs and the pinning test are updated inside this issue.
- Mid-issue: allowed the Engineer's two denied edits to `guard_git.py`.
- Approved the commit as staged and ran it themselves with `HUMAN_APPROVED=1`, listing the eight paths so the staged session summary stayed out.

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (285 tests OK, claims check OK, whitespace clean, no weakened tests at ece19f0).

## Proposed AGENTS.md changes

none beyond the committed hook-line wording.

## Temporary changes

none. The Engineer and QA left only `.scratch/` files (`eng39-*`, `qa39-*`); QA created no `.env` file.

## Interruptions

The Engineer stopped after two Edit calls to `guard_git.py` were denied, with the hook partly edited and `make test` failing on `cat 2>.env`. Nothing else was left behind. I surfaced it, the human allowed the edit, and I resumed the Engineer; the final `make verify` passed and QA re-probed the hook.

## Unrelated problems noticed but not fixed

- Non-dict JSON on stdin (`[]`, `null`, `"x"`) and a non-string `command` crash the hook with exit 1, which Claude Code treats as non-blocking. Unchanged from before; not real payload shapes.
- The `agent-kit/claude-code/START.md` row for `hooks/guard_git.py` lists only the git blocks.
- The README line for the `.env` shell block sits inside the 1.8 changelog bullet, the only README mention of `.env` enforcement, an odd place for current behaviour.
- `make verify` prints an 82-file diffstat against the far-behind `origin/main`.
- `.claude/agents/pm.md` is modified and the `proposals/` files are untracked, so `make assert-clean` fails on them.

## Follow-ups for the next session

- Sweep: three proposals for the human, none applied: the Engineer's "request edit approval for all protected files up front" (`software-engineer.md`), QA's "say what counts as malformed input for a hook criterion" (`qa-engineer.md`), and the earlier bad-input-testing line from #16.
- Changelog line for the next version: "Claude Code's Bash guard now blocks shell commands that name `.env` files (other than `.env.example`)."
- Open and waiting for the human: #40 (decision on two script defects), #37 (three questions), #20 (observer run).
