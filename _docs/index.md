# Docs index

No front matter; metadata lives here.

| Detail | Goes in |
|---|---|
| Session narrative and what was learned | a log entry |
| A choice that may be revisited, with reasons and alternatives | a decision record |
| Exact commands, numbers, full tables and caveats | a measurement |
| One headline result plus its limitation | README, linking to the measurement |
| Anything stable and long-lived | a canonical doc |

Write once, link elsewhere: log entries link to stable decisions. README: one headline result and its limitation, no run tables.

## Entry types

By folder: "no doc without an index entry" can't work for hundreds of entries. Names: `agent-kit/procedures/session-summary.md`.

| Type | Folder | Template | Filename pattern |
|---|---|---|---|
| Record: what was measured, found or read, with method and caveats (flat; the filename kind, such as `measure` or `source`, tells them apart; a sweep entry is `measure-pm-sweep`) | `_docs/records/` | `agent-kit/templates/measurement.md` (plus the sections in `agent-kit/procedures/sweep.md` for a sweep), `agent-kit/templates/source.md` | `<timestamp>-<kind>-<slug>.md`; a sweep entry is `<timestamp>-measure-pm-sweep.md` |
| Plan: what we intend to do and in what order, such as the current status (rewritten in place, its Date line says how fresh it is) | `_docs/planning/` | none | `current-status.md`, or `<slug>.md` |
| Decision | `_docs/decisions/` | `agent-kit/templates/adr.md` | `<issue>-<slug>.md` |
| Human task | `_human-tasks/` | `agent-kit/templates/human-task.md` | `<timestamp>-human-task-<id>-<role>-<slug>.md` |

## Canonical docs

By file. Add project manifests here.

| Path | Canonical for | Status |
|---|---|---|
| `_docs/decisions/119-issue-close.md` | Decision to add `make issue-close` (#119) | Approved |
| `_docs/decisions/156-planning-gate.md` | Decision to add `procedures/planning.md` and a spec definition of ready (#156) | Approved |
| `_docs/decisions/159-planning-guidance.md` | Decision to add a testable example, a plan-review checklist and a one-intent rule to the planning guidance (#159) | Approved |
