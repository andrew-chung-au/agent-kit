# Docs index

No front matter; metadata lives here.

| Detail | Goes in | Not here |
|---|---|---|
| Session narrative and what was learned | a log entry | the README |
| A choice that may be revisited, with reasons and alternatives | a decision record | a record, a plan |
| Exact commands, numbers, full tables and caveats | a record | the README |
| One headline result and its limit, owned by the owner | the README, linking to the record | run tables |
| Proof for a decision (results, review, discussion) | where it was first recorded (issue, pull request or a record), linked from the decision | a copy in the decision record |
| Anything stable and long-lived | a canonical doc | a log entry |

Write once, link elsewhere: log entries link to stable decisions. The README holds one headline result and its limit, no run tables.

A copy is allowed only if the reader would otherwise have to follow a link before acting, and the copy names its source and has a check or a named sync step. Otherwise, link.

Word limits are defaults a project may change: README 300 words; this index 200 words plus one row per entry type.

## Entry types

By folder: "no doc without an index entry" can't work for hundreds of entries. This table is the only place that defines the folders; every other doc says "the folder the index names". Names: `procedures/session-summary.md`.

| Type | Folder | Template | Filename pattern | Not here |
|---|---|---|---|---|
| Plan: what we intend to do and in what order (roadmap files, requirements-like files) | `_docs/planning/` | `templates/roadmap.md` for roadmaps | `roadmap-<n>-<slug>.md`, or `<slug>.md` | measurements, decisions |
| Decision | `_docs/decisions/` | `templates/adr.md` | `<timestamp>-<slug>.md` | plans, measurements |
| Record: what was measured, found or read, with method and caveats (flat; the filename kind, such as `measure` or `source`, tells them apart) | `_docs/records/` | `templates/measurement.md`, `templates/source.md` | `<timestamp>-<kind>-<slug>.md` | decisions, plans |
| Runbook (added when the first repeatable operation appears) | `_docs/runbooks/` | `templates/runbook.md` | `<slug>.md` | one-off fixes, decisions |
| Session summary | `_session-summaries/` | `templates/session-summary.md` | see `procedures/session-summary.md` | decisions, plans |
| Human task | `_human-tasks/` | `templates/human-task.md` | `<timestamp>-human-task-<id>-<role>-<slug>.md` | decisions, records |

## Canonical docs

By file. Add project manifests here.

| Path | Canonical for | Status |
|---|---|---|
