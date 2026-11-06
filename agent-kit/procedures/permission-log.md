# Permission log

The record format for permission requests an agent tool asks the human to approve. The OpenCode plugin `opencode/plugins/permission-log.js` writes it, and so does the Claude Code hook `claude-code/hooks/log_permission.py` (`tool: "claude-code"`, `ask` records only: its events carry no outcome, so no `id`). `make permission-report` summarises both (`SINCE`: UTC date or `YYYY-MM-DDTHH:MMZ`); `make permission-logs-prune DAYS=<n>` deletes old files (#36). The hook refuses symlinks, like report and prune.

**Where:** `.agent-kit/logs/permissions/YYYY-MM-DD.jsonl` (UTC date), one JSON object per line. It is git-ignored and outside `.scratch/`, so `make clean-scratch` leaves it.

```json
{"event":"ask","tool":"opencode","time":"2026-11-03T09:15:02.114Z","sessionID":"ses_1","id":"per_1","type":"shell","pattern":"git push *","source":"permission.asked"}
{"event":"reply","tool":"opencode","time":"2026-11-03T09:15:09.870Z","sessionID":"ses_1","id":"per_1","response":"once","source":"permission.replied"}
{"event":"unknown","tool":"opencode","time":"2026-11-03T09:16:00.002Z","source":"permission.v2.asked"}
{"event":"truncated","tool":"opencode","time":"2026-11-03T23:59:58.500Z"}
```

**Fields** (the only ones ever written): `event`, `tool`, `time` (ISO-8601 UTC), `sessionID`, `id`, `type` (the action asked about, such as `shell`), `pattern`, `response`, `source` (OpenCode's own event name). A reply's `id` is the id of the ask it answers; `response` is `once`, `always` or `reject`. For the report, `once` is allowed, `always` is always, `reject` is denied.

**Limits:** secrets in `pattern` are replaced by `[redacted]` using `scripts/secret-patterns.txt`, then it is cut to 200 characters (a cut ends in `...`). If the patterns cannot be read it is `[redacted: no patterns]`. The first record that does not fit under 1048576 bytes ends that day's log: one `truncated` record is written, and every later record is dropped, even after a restart.

**Never logged:** commands, titles, tool output, file contents, diffs. An unrecognised permission event becomes an `unknown` record with its name only; other events are ignored.

**Tested against:** OpenCode 2.2.5 and its V2 plugin API (`@opencode/plugin`); not for OpenCode 1.x. V2 gives plugins no log sink, so a logging failure drops the record silently. Open: do subagent prompts appear (extra `sessionID` values)?

**Hand check at each OpenCode upgrade:** the kit has no Node check. Follow the three steps in `opencode/START.md` (step 6): allow one command, reject one, run one holding a fake key. Pass: every prompt appears, decisions are unchanged, and no line holds the key.

**Result:** not yet run on 2.2.5.
