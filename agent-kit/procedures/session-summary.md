# Write the session summary

At the end of every orchestrator session: issue work, planning or a backlog review.

1. Name the file in `_session-summaries/` using the filename convention below (kind `issue` or `planning`, role `orchestrator`). Take the timestamp with `date -u +%Y-%m-%dT%H%MZ`.
2. Get the spec version: `git log -1 --format=%h -- _docs/specs.md`. If there is no spec yet, write "none".
3. Fill in `_docs/agent-kit/templates/session-summary.md`, with the full UTC timestamp on the `**Date:**` line. Keep each section to a few lines, and write "none" rather than leaving a section out.
4. Commit it on its own: `git add _session-summaries/<file>`, with a message like "Add session summary for issue #004".

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
- If the exact name exists, the second writer appends `-2` before `.md`.
- Names never change after creation. Files created before this convention (`issue-NNN-...`, `planning-<date>-...`) keep their names; the convention applies to new files only.

| Kind | Entry type | `<id>` | `<role>` |
|---|---|---|---|
| `issue` | log entry (session summary) | required: three-digit issue number | required |
| `planning` | log entry (session summary) | absent | required |
| `decision` | decision record | absent | optional |
| `measure` | measurement | absent | optional |
| `source` | source or input | absent | optional |
| `runbook` | runbook | absent | optional |

Roles: `orchestrator`, `pm`, `engineer`, `qa`. Session summaries use `orchestrator` unless the human says otherwise.

To parse a name, read the timestamp, then the kind. Only `issue` has an id (digits). The next token is the role if it is in the role list, otherwise it starts the slug. So a slug must not begin with a role word.
