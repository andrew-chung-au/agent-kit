# Write the session summary

At the end of every orchestrator session: issue work, planning or a backlog review.

1. Name the file in `_session-summaries/` using the scheme in the **Session summaries** setting in `AGENTS.md`. If none is set, use:
   - issue work: `issue-<NNN>-<short-name>.md`, with the issue number padded to three digits
   - planning or a backlog review: `planning-<YYYY-MM-DD>-<short-name>.md`
2. Get the spec version: `git log -1 --format=%h -- _docs/specs.md`. If there is no spec yet, write "none".
3. Fill in `_docs/agent-kit/templates/session-summary.md`. Keep each section to a few lines, and write "none" rather than leaving a section out.
4. Commit it on its own: `git add _session-summaries/<file>`, with a message like "Add session summary for issue #004".
