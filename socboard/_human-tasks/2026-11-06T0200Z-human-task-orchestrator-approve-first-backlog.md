# Approve the first backlog

## Purpose

Turn the Core backlog drafts and the three ponytail plumbing tasks into groomed, approved issues. Issue: none.

## Where to run it

An orchestrator session in any tool for the PM steps; GitHub or a terminal for the labels. Not here: don't let an agent add the `approved` label. Only you change approval labels.

## Before you start

1. Confirm the planning documents are on main.

```
git log --oneline -3 -- _docs/specs.md _docs/planning/core-backlog.md
```

Expected: commits touching both files.

2. Confirm the labels the process needs exist.

```
gh label list
```

Expected: `approved`, `tier:light`, `tier:standard` and `tier:heavy` are listed.
If different: tell the orchestrator which are missing before going further.

## Steps

### Step 1: Ask the PM to propose the backlog

Ask the PM role to compare `_docs/specs.md` with the existing issues and propose issues: titles with a one-line goal, in build order. No issue is created yet.

Expected: a list covering the eleven tasks in `_docs/planning/core-backlog.md`, plus three trial tasks from `_docs/planning/roadmap-2-ponytail-trial.md` (hold the pinned review file, the metrics script, the reviewer role).

### Step 2: Approve, amend or reject the list

Reply in the session. The PM then creates only the approved titles with `make issue-create`.

```
gh issue list --state open
```

Expected: one open issue per approved title.

### Step 3: Read each groomed issue

For each issue in build order, read the PM's grooming comment: the five template sections, the `Proposed tier:` line and the `Body sha256:` line.

Expected: all present.
If different: send it back to the PM.

### Step 4: Approve one issue at a time

```
gh issue edit <number> --add-label approved
```

Expected: `gh issue view <number> --json labels` lists `approved`.
Risk: lets the Engineer start on that text. Undo: `gh issue edit <number> --remove-label approved`.

### Step 5: Override a tier, only if you disagree with the proposal

```
gh issue edit <number> --add-label tier:heavy
```

Expected: the label is listed on the issue. A `tier:` label always wins over the PM's proposal.
Risk: a Heavy issue needs an approved decision record before the Engineer starts.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 to 5 | Pass (done) | Recorded 2026-11-10 from the repo, not at the time. The backlog was proposed, filed and groomed, and issues are approved one at a time (#2 onward; #7, #23, #24, #25 and #27 have been worked). Step-by-step output was not kept. |

## Risk

Adding `approved` before reading the groomed text approves text you haven't seen. An approved issue's body is locked by its hash, so a later change needs re-approval.
