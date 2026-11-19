# Decide: whether to create a trial label

## Purpose

Decide whether to create a `trial:ponytail` label for filtering trial issues on GitHub. Optional. Issue: none.

## Where to decide

In the orchestrator session. Creating the label is a single command that you run.

## Options

1. Create it and apply it to the plumbing issues and the treated issues only. Protocol amendment 1 forbids putting it on control issues, because the Engineer can see labels and it would prime them.
2. Skip it. The trial is still findable through `ponytail` in file names, the `ponytail: on` line, and the session summaries.

## Recommendation

Option 1 is useful for the write-up, but it leaves control issues unlabelled by design. Choose option 2 if that asymmetry bothers you.

## Record the result

Write Pass once decided, and name the option in the note. If you choose option 1, create it with `gh label create trial:ponytail`.

| Step | Pass or fail | Output or note |
|---|---|---|
| Decide | Pass | Option 2: no label. Human decided 2026-11-09: simpler, and control issues stay unprimed. |

## Risk

Applying the label to a control issue by mistake would prime the Engineer. If that happens, remove it and tell the orchestrator.
