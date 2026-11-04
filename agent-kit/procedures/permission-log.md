# Permission log

The record format for permission requests an agent tool asks the human to approve. The OpenCode plugin `opencode/plugins/permission-log.js` writes it, and so does the Claude Code hook `claude-code/hooks/log_permission.py` (`tool: "claude-code"`, `ask` records only: its events carry no outcome, so no `id`). `make permission-report` summarises both (`SINCE`: UTC date or `YYYY-MM-DDTHH:MMZ`); `make permission-logs-prune DAYS=<n>` deletes old files (#36). The hook refuses symlinks, like report and prune.

**Where:** `.agent-kit/logs/permissions/YYYY-MM-DD.jsonl` (UTC date), one JSON object per line. It is git-ignored and outside `.scratch/`, so `make clean-scratch` leaves it.

```json
{"event":"ask","tool":"opencode","time":"2026-11-03T09:15:02.114Z","sessionID":"ses_1","id":"per_1","type":"bash","pattern":"git push *","source":"permission.asked"}
{"event":"reply","tool":"opencode","time":"2026-11-03T09:15:09.870Z","sessionID":"ses_1","id":"per_1","response":"once","source":"permission.replied"}
{"event":"unknown","tool":"opencode","time":"2026-11-03T09:16:00.002Z","source":"permission.v2.asked"}
{"event":"truncated","tool":"opencode","time":"2026-11-03T23:59:58.500Z"}
```

**Fields** (the only ones ever written): `event`, `tool`, `time` (ISO-8601 UTC), `sessionID`, `id`, `type` (what is asked about, such as `bash`), `pattern`, `response`, `source` (OpenCode's own event name). A reply's `id` is the id of the ask it answers. For the report, `once` is allowed, `always` is always, `reject` is denied.

**Limits:** secrets in `pattern` are replaced by `[redacted]` using `scripts/secret-patterns.txt`, then it is cut to 200 characters (a cut ends in `...`). If the patterns cannot be read it is `[redacted: no patterns]`. The first record that does not fit under 1048576 bytes ends that day's log: one `truncated` record is written, and every later record is dropped, even after a restart.

**Never logged:** commands, titles, tool output, file contents, diffs. An unrecognised permission event becomes an `unknown` record with its name only; other events are ignored.

**Tested against:** written from the type declarations of `@opencode-ai/plugin` 1.19.0; no real session has run it yet (the human's OpenCode is 2.2.5). Open: do subagent prompts appear (extra `sessionID` values), and does the log show which session is a subagent? Answer here after the first real session.

**Hand check at each OpenCode upgrade** (the kit has no Node check): allow one command (one `ask`, one `reply` with `once`); reject one (`reject`); run one holding an API-key-shaped string (the line holds none of it). The prompt must still appear, the decision unchanged.
