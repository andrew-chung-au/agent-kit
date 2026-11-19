# Check each tool's commits carry the Assisted-by line

## Purpose

Confirm that agent commits from Kiro, OpenCode and Claude Code each end with `Assisted-by: <Tool>`, as the commit-attribution decision requires, and see whether a tool adds a line of its own as well. Issue: none.

## Where to run it

In the project folder, during real Core work, after the first agent commit made by each tool. Not here: don't ask an agent for a throwaway commit just for this check. The Engineer works only on approved issues.

## Before you start

1. Confirm the rule is on main.

```
git log --oneline -1 -- _docs/decisions/2026-11-06T0111Z-commit-attribution.md
```

Expected: one commit line.

## Steps

### Step 1: Kiro

After Kiro's first commit on an approved issue:

```
git log -1 --format='%an%n%B'
```

Expected: the first line is `Kiro Agent` and the last line is `Assisted-by: Kiro`.
If different: stop, don't retry another way, and tell the orchestrator what was printed (a missing line, or a co-author line instead).

### Step 2: OpenCode

After OpenCode's first commit on an approved issue:

```
git log -1 --format='%an%n%B'
```

Expected: the last line is `Assisted-by: OpenCode`. Note whether OpenCode also added a line of its own, such as a "Generated with" line or a co-author line.
If different: stop and tell the orchestrator what was printed.

### Step 3: Claude Code

After Claude Code's first commit on an approved issue:

```
git log -1 --format='%an%n%B'
```

Expected: the last line is `Assisted-by: Claude Code`. The kit's own "Generated with Claude Code" line may also appear; note whether it does.
If different: stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 Kiro | Pass | Read from history on 2026-11-10: Kiro commits on approved issues (#25, #27), for example 9f4993a, are authored `Kiro Agent` and end with `Assisted-by: Kiro`; no co-author line. |
| 2 OpenCode | Not run | No commit in the history was made by OpenCode yet. Run this step at OpenCode's first commit on an approved issue. Reading commit messages does not change agent behaviour, so this does not block the ponytail epoch. |
| 3 Claude Code | Pass, with a caveat | 4f5365e, 58be61b and 818f89b end with `Assisted-by: Claude Code` and have no "Generated with" or co-author line. Caveat: they were orchestrator commits, not commits on an approved issue. |

Note (2026-11-10): 8e514a0 and f34b65e on #27 were committed by the human by hand but carry `Assisted-by: Kiro`, because the orchestrator's instructions said so. That attribution is wrong; a commit the human makes carries no `Assisted-by` line. #27 is excluded from the ponytail trial, so no counted figure is affected.

## Risk

None. The commands only read commit messages.
