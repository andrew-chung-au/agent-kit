# Create the overrides label

## Purpose

Create the `overrides` label, so an `Overrides:` line in an approved issue body can take effect (`agent-kit/customizing.md`, "One issue: overrides and session rulings"). Agents never create labels (`AGENTS.md`, Issues). Issue: #197.

## Where to run it

A terminal on your own machine where `gh` is signed in to the account that owns this repository, or the repository's Labels page in a browser. Not here: an agent session; agents must not create labels.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Confirm the label does not exist yet.

```
gh label list --repo andrew-chung-au/agent-kit --search overrides
```

Expected: no line whose name is exactly `overrides`.

## Steps

### Step 1: Create the label

```
gh label create overrides --repo andrew-chung-au/agent-kit --description "The Overrides: line in this issue's body applies (customizing.md)"
```

Expected: a line saying the label `overrides` was created. In a browser instead: Issues, Labels, New label, name `overrides`, the same description.
If different: it may exist already (then nothing more is needed) or `gh` is signed in to another account. Stop, don't retry another way, and tell the orchestrator what was printed.
Risk: adds a label to the public repository. It changes nothing until you add it to an issue. Undo: `gh label delete overrides --repo andrew-chung-au/agent-kit --yes`.

### Step 2: Check the label is listed

```
gh label list --repo andrew-chung-au/agent-kit --search overrides
```

Expected: one line with the name `overrides` and the description from Step 1.
If different: the label was not created. Stop and tell the orchestrator what was printed.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | pass | Done by the human; reported in session on 2026-11-21 ("the label is already created"). |
| 2 | pass | Not separately recorded; the human confirmed the label exists. |

**Status: done (2026-11-21).**

## Risk

Low. Only the human adds the `overrides` label to an issue; until then no `Overrides:` line takes effect, and `make settings N=<n>` refuses an `Overrides:` line on an issue without it.
