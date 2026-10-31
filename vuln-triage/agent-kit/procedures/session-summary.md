# Write the session summary

At the end of every orchestrator session: issue work, planning or a backlog review.

1. Name the file in `_session-summaries/` using the scheme in the **Session summaries** setting in `AGENTS.md`. If none is set, use:
   - issue work: `issue-<NNN>-<short-name>.md`, with the issue number padded to three digits
   - planning or a backlog review: `planning-<YYYY-MM-DD>-<short-name>.md`
2. Get the spec version: `git log -1 --format=%h -- _docs/specs.md`. If there is no spec yet, write "none".
3. Fill in `_docs/agent-kit/templates/session-summary.md`. Keep each section to a few lines, and write "none" rather than leaving a section out.
   - **Permission review:** collect the "Commands and changes that required approval" line from every role comment of this session, add the orchestrator's own, and group them by proposed disposition: read-only (propose allowing), routine issue writes (already allowed; list only if a role recorded one), protected record writes (keep asking), system and external changes (keep asking), risky (propose denying). Record each action and its basis (a merits request, or the matched `ask` rule), not whether it was granted. Creating and commenting on issues is routine, so it is not an approval and is not recorded; issue edits and closes are. If a role comment has no such line, say so in the section rather than guessing. Don't propose settings changes in the summary and don't edit `opencode.json` or `.claude/settings.json`: the recorded approvals are counted later by `make permission-report` and decided in a permission sweep (`_docs/agent-kit/procedures/permission-sweep.md`). A risky item (for example a refused push or a destructive command) is not parked until a sweep: bring it to the human at the decision point of this issue.
4. Commit it on its own: `git add _session-summaries/<file>`, with a message like "Add session summary for issue #004".
