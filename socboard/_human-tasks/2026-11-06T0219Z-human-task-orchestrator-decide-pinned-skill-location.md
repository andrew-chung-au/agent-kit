# Decide: where to hold the pinned ponytail-review file

## Purpose

Choose where the pinned `ponytail-review` file lives so that no tool auto-discovers it during the baseline. Blocks: roadmap task 3 and the reviewer role. Issue: none.

## Where to decide

In the orchestrator session, in any tool. Nothing to run.

## Options

1. A new folder `_docs/vendor/ponytail/`, with one row added to `_docs/index.md`. It can later hold the pinned core skill too, and the Phase 2 install copies from it.
2. `_docs/records/`, as a source-kind file next to the source record. No new folder or index row, but a vendored file does not fit the record format.

Not options: any tool's skills folder, or `.agents/skills/`. They are auto-discovered, and OpenCode reads `.claude/skills/` and `.agents/skills/` as well.

## Recommendation

Option 1. One pinned original means a later check can compare each installed copy against it.

## Record the result

Write Pass once decided, and name the option in the note.

| Step | Pass or fail | Output or note |
|---|---|---|
| Decide | Pass | Option 1: `_docs/vendor/ponytail/`, with one row added to `_docs/index.md` when the file is vendored. Human approved the recommendation 2026-11-09. |

## Risk

A wrong choice costs moving one file and one index row.
