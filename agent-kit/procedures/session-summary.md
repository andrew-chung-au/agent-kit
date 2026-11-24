# Write the session summary

At the end of every orchestrator session: issue work, planning or a backlog review.

1. Name the file in `_session-summaries/` using the filename convention below (kind `issue` or `planning`, role `orchestrator`). Take the timestamp with `date -u +%Y-%m-%dT%H%MZ`.
2. Get the spec version: `git log -1 --format=%h -- _docs/specs.md`. If there is no spec yet, write "none".
3. Fill in `_docs/agent-kit/templates/session-summary.md`, with the full UTC timestamp on the `**Date:**` line. Keep each section to a few lines, and write "none" rather than leaving a section out.
4. Commit it on its own: `git add _session-summaries/<file>`, with a message like "Add session summary for issue #004".

## Reflection

Reflections are files, not comments, and need no launch after QA PASS: every role writes one at the end of each launch, and the orchestrator appends it to the issue's reflection file (`procedures/formats.md`, Reflection). Under `## Reflection`, write the path of that file, `_docs/records/reflections/<issue>.md`, or `none` when the session has none. Don't copy its sections into the summary. Neither the summary nor this section is needed for a reflection to be written or read. Summaries written before this change keep their Reflection blocks as history.

## Launch usage

Under `## Launch usage`, write one line per subagent launch: role, active time, tool uses, copied from the completion notification, not estimated. A figure the tool doesn't give reads `unknown`. No launches: `none`.

## Filename convention

One convention names every log-style entry, whatever its type: `<timestamp>-<kind>-<id>-<role>-<slug>.md`. This is its only home; other docs link here.

Examples:
- `2026-10-31T0642Z-issue-022-engineer-claims-check.md`
- `2026-10-31T0642Z-decision-cloud-push-allow-path.md`
- `2026-10-31T0642Z-measure-doc-budget-baseline.md`

Rules:
- The timestamp is UTC with no colons (`YYYY-MM-DDTHHMMZ`) and comes first, so `ls` sorts chronologically. The file also records the full timestamp with timezone near the top.
- `<kind>`, `<id>` and `<role>` let a glob such as `*issue-022*` group an issue.
- No sequence numbers: parallel agents would collide. Issue numbers are safe, because GitHub allocates them.
- If the exact name exists, the second writer appends `-2` before `.md`, the third `-3`.
- Names never change after creation. Files named `issue-NNN-<slug>.md` or `planning-<date>-<slug>.md` predate the convention and keep their names; `ls` sorts them after new names, so sort by their `**Date:**` line (date only).
- The last summary is `git log -1 --format=%h -- _session-summaries/`.

| Kind | Entry type | `<id>` | `<role>` |
|---|---|---|---|
| `issue` | log entry (session summary) | required: three-digit issue number | required |
| `planning` | log entry (session summary) | absent | required |
| `decision` | decision record | absent | optional |
| `measure` | measurement | absent | optional |
| `source` | source or input | absent | optional |
| `runbook` | runbook | absent | optional |
| `human-task` | human task file, in `_human-tasks/` (`templates/human-task.md`) | optional: three-digit issue number, absent when the task has no issue | required: the role that wrote it |

Roles: `orchestrator`, `pm`, `engineer`, `qa`. Session summaries use `orchestrator` unless the human says otherwise.

To parse a name, read the timestamp, then the kind (`human-task` contains a hyphen). Only `issue` and `human-task` have an id (digits), and for `human-task` it may be absent. The next token is the role if it is in the role list, otherwise it starts the slug. So a slug must not begin with a role word, and must not be only digits.
