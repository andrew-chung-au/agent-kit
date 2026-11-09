# Run the permission-log real-session checks in OpenCode and Claude Code

> Written before asking the human, per `agent-kit/templates/human-task.md`. The repository is public: no secrets, tokens, private paths or machine names appear here. The fake key is built by a command and is never written whole in this file.

## Purpose

Turn on both permission loggers in this repo, run the real-session checks that no agent can run, and record the real outcome: OpenCode 2.2.5 (allow once, a fake key, reject), Claude Code (allow once, deny), subagent prompts in both tools, and the report. Issue: #168. It replaces `_human-tasks/2026-11-03T1435Z-human-task-orchestrator-permission-logs-real-session-checks.md` and `_human-tasks/2026-11-06T0305Z-human-task-155-engineer-opencode-2-permission-log-hand-check.md`; do not run those.

The OpenCode part already passed once on 2026-11-07, in a sandbox project and not in this repo (see the [Orchestrator comment on #168](https://github.com/andrew-chung-au/agent-kit/issues/168#issuecomment-6711870205)). This run repeats it here, with the kit in `agent-kit/`, and adds Claude Code, subagents and the report. The record format and limits are in `agent-kit/procedures/permission-log.md`; the install steps are in `agent-kit/opencode/START.md` and `agent-kit/claude-code/START.md`. The steps below match them.

Parts A to D are required. Part E (steps 19 to 30) is optional: #71's cap check, the 200-character cut and fail-closed, in a throwaway project. If you skip it, write "Part E skipped" in the record.

## Where to run it

In the local sandbox VS Code window opened on this repo, with a terminal for the commands, and OpenCode and Claude Code sessions started in this folder (the folder that holds `agent-kit.conf`). Use the normal interactive interface in both tools, not auto-approve: auto-approval skips the prompts this checks. Not here: don't use the `!` prefix in OpenCode, which runs a command directly and skips the permission rules being tested. No tool enforces this. Part E runs in a second, empty folder outside this repo, with its own terminal and OpenCode session.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue. In each tool the reject step comes last for that reason. In steps that say "once" or "allow", approve exactly that prompt and no other.

When you ask an agent to run a command, write it as a request: Run `the command`. A bare command pasted on its own can be treated as text and never run.

The log files are in `.agent-kit/logs/permissions/`, one per UTC day, and both tools write to the same file. The steps read them with `*.jsonl`, which matches today's file when it is the only one. If `ls` in "Before you start" shows older files, read the newest one by its date.

## Before you start

1. Check the OpenCode version, in the terminal.

```
opencode --version
```

Expected: a version line that contains `2.2.5`. Write it in the record.

2. Check the Claude Code version.

```
claude --version
```

Expected: a version line. Write it in the record.

3. Print the current UTC time. Write it down; it is the `SINCE` value for the report if old records exist.

```
date -u +%Y-%m-%dT%H:%MZ
```

Expected: a time like `2026-11-07T10:30Z`.

4. Check that the plugin will find the kit.

```
grep KIT_DIR agent-kit.conf
```

Expected: `KIT_DIR="agent-kit"`.

5. Check this repo's last commit touching the Claude Code settings is the one that registers the hook.

```
git log -1 --format=%h -- .claude/settings.json
```

Expected: `aa5f7c4` or a later commit.
If different: stop, run `git pull`, and tell the orchestrator what was printed.

6. List the existing logs.

```
ls .agent-kit/logs/permissions
```

Expected: "No such file or directory", or only files with older dates.

## Steps

**Part A: turn the logging on** (steps 1 to 7)

### Step 1: Create the plugin folder

```
mkdir -p .opencode/plugins
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.

### Step 2: Copy the OpenCode plugin into place

```
cp agent-kit/opencode/plugins/permission-log.js .opencode/plugins/permission-log.js
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.
Risk: adds a plugin that OpenCode loads at its next start, under a protected path. It only observes and changes no decision. Undo: delete `.opencode/plugins/permission-log.js` before the commit, or revert the commit after it.

### Step 3: Stage it

```
git add .opencode/plugins/permission-log.js
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.

### Step 4: Commit it with your approval

```
HUMAN_APPROVED=1 git commit -m "Install the OpenCode permission log plugin (#168)"
```

Expected: one file changed, created, mode 100644.
If different: stop, and tell the orchestrator what was printed.
Risk: this is the protected-file commit; you are the approver. The plugin is not active until OpenCode restarts.

### Step 5: Check the log folder is git-ignored

```
git check-ignore .agent-kit/logs/
```

Expected: `.agent-kit/logs/` is printed.
If different: stop. The log would show up as untracked. Tell the orchestrator.

### Step 6: Check the Claude Code hook is registered

This repo's `.claude/settings.json` already registers `log_permission.py` under `PermissionRequest`. Nothing to install.

```
grep -c log_permission.py .claude/settings.json
```

Expected: `1`.
If different: stop, and tell the orchestrator what was printed.

### Step 7: Restart OpenCode and start a fresh Claude Code session

Close OpenCode and open it again in this folder. Plugins load at start. Start a new Claude Code session in this folder (the hook loads from the settings at start) and accept the workspace trust prompt. In Claude Code run `/hooks`. Then confirm the plugin commit exists:

```
git log -1 --format=%h -- .opencode/plugins/permission-log.js
```

Expected: a commit hash. OpenCode shows no "Server plugin error" about `permission-log.js`, and `/hooks` lists the permission logger under `PermissionRequest`.
If different: stop, don't retry another way, and tell the orchestrator the exact error text. Don't use the plugin until it is fixed.

**Part B: OpenCode 2.2.5** (steps 8 to 14)

### Step 8: Allow one command once

Tell the OpenCode agent: "Run `touch .scratch/permlog-allowed`." The prompt should look as it did before the plugin. Choose **once**. Then read the log:

```
tail -n 2 .agent-kit/logs/permissions/*.jsonl
```

Expected: an `ask` line with `"tool":"opencode"`, `"type":"shell"` and `"pattern":"touch .scratch/permlog-allowed"`, then a `reply` line with `"response":"once"` and the same `id`. The command ran. Write down the `sessionID` of the `ask` line; call it session A.
If different: stop and tell the orchestrator what was printed.

### Step 9: Print a test command holding a fake key, in the terminal and not through the agent

```
printf 'echo sk-%s\n' aaaaaaaaaaaaaaaaaaaaaaaa
```

Expected: it prints one line: `echo sk-` followed by 24 letters `a`. The fake key is not a credential.
If different: stop and tell the orchestrator what was printed.

### Step 10: Send the printed line to OpenCode

Send the line `printf` printed, not the `printf` command above (sending that tests nothing, because it holds no key). Write it as a request, with the printed line inside backticks: Run `<the printed line>`. Check that the OpenCode prompt shows the `echo` command; if it only answers in text, no command ran, so ask again. Choose **once**. Then read the log:

```
tail -n 2 .agent-kit/logs/permissions/*.jsonl
```

Expected: the prompt appeared and the command ran. The newest `ask` line holds `"pattern":"echo [redacted]"`, followed by a `reply` with `"response":"once"`.
If different: stop and tell the orchestrator. Don't share the log; delete today's log file only after the orchestrator says so.

### Step 11: Count log lines holding the fake key

Refusal test: use the OpenCode session without the `!` prefix. The aim is that the key never reaches the log. This step only reads the log.
Risk: if redaction failed, the fake key is in the git-ignored log. Don't paste it anywhere.

```
grep -c sk-a ".agent-kit/logs/permissions/$(date -u +%F).jsonl"
```

Expected: `0`.
If different: stop and tell the orchestrator that the count was not `0`. Don't print the lines.

### Step 12: OpenCode subagent

Tell the OpenCode agent: "Use the software-engineer agent to run `touch .scratch/permlog-subagent-opencode`." Choose **once** for the subagent's prompt for that command. If the subagent asks about other commands, choose once too. Then read the log:

```
grep -h permlog-subagent-opencode .agent-kit/logs/permissions/*.jsonl
```

Expected: an `ask` line for that command, or no line at all. Compare its `sessionID` with session A from step 8. A different value means the subagent's session can be told apart; the same value means it cannot. Write both answers in the record.
If different: this step records an answer and has no wrong result. If the command was never asked about, say so.

### Step 13: Reject one command (last in OpenCode)

Refusal test: use the OpenCode session without the `!` prefix. Reject goes last because a rejection ends the agent's turn.
Risk: if the plugin changed a decision, the command would run when it should not.

Tell the agent: "Run `touch .scratch/permlog-rejected`." Choose **reject**, then tell the agent to continue and check the file:

```
ls .scratch/permlog-rejected
```

Expected: "No such file or directory".
If different: stop using the plugin and report it to the orchestrator.

### Step 14: Read the reject record

```
grep -h '"response":"reject"' .agent-kit/logs/permissions/*.jsonl
```

Expected: one `reply` line with `"response":"reject"`. Its `id` is the id of the `ask` line for `touch .scratch/permlog-rejected`.
If different: stop and tell the orchestrator what was printed.

**Part C: Claude Code** (steps 15 to 17)

Use the fresh Claude Code session from step 7. The hook writes `ask` records only: no `id` and no reply, because the event carries no outcome (`agent-kit/procedures/permission-log.md`). The prompts should look as they did before the hook.

### Step 15: Allow one command once

Tell Claude Code: "Run `touch .scratch/permlog-claude-allowed`." Allow it once. Then read the log:

```
grep -h permlog-claude-allowed .agent-kit/logs/permissions/*.jsonl
```

Expected: one `ask` line with `"tool":"claude-code"`, `"type":"bash"` and `"pattern":"touch .scratch/permlog-claude-allowed"`, with no `id` field. The file was created. Write down its `sessionID`; call it session B.
If different: stop. A changed or missing prompt is a finding for #36; tell the orchestrator what you saw.

### Step 16: Claude Code subagent

Tell Claude Code: "Use the software-engineer subagent to run `touch .scratch/permlog-subagent-claude`." Allow it once. Then read the log:

```
grep -h permlog-subagent-claude .agent-kit/logs/permissions/*.jsonl
```

Expected: an `ask` line for that command, or no line at all. Compare its `sessionID` with session B from step 15. A different value means the subagent's session can be told apart; the same value means it cannot. Write both answers in the record.
If different: this step records an answer and has no wrong result. If the command was never asked about, say so.

### Step 17: Deny one command (last in Claude Code)

Refusal test: use the Claude Code session without the `!` prefix. Deny goes last because a denial ends the agent's turn.
Risk: if the hook changed a decision, the command would run when it should not.

Tell Claude Code: "Run `touch .scratch/permlog-claude-denied`." Deny it, then tell it to continue and check the file:

```
ls .scratch/permlog-claude-denied
```

Expected: "No such file or directory". The hook cannot record the denial, so nothing is logged about the outcome; the `ask` line is checked in step 18.
If different: stop using the hook and report it to the orchestrator.

**Part D: read the result** (step 18)

### Step 18: Read the report for both tools

```
make permission-report
```

Expected: if old records exist, add `SINCE=` and the time from "Before you start" item 3. A header line `Permission report (1 log file, <date> to <date>)`, then a table with the columns TOOL, TYPE, ASKED, ALLOWED, ALWAYS, DENIED, SESSIONS, FIRST, LAST and PATTERN. Rows for `opencode` (type `shell`): `touch .scratch/permlog-allowed` asked 1 and allowed 1; `echo [redacted]` asked 1 and allowed 1; `touch .scratch/permlog-rejected` asked 1, allowed 0 and denied 1; the OpenCode subagent row asked 1 if it was asked about. Rows for `claude-code` (type `bash`): `touch .scratch/permlog-claude-allowed`, `touch .scratch/permlog-claude-denied` and the Claude Code subagent command, each asked 1, with `-` in ALLOWED, ALWAYS and DENIED. Each row shows SESSIONS 1. Below the table: a line "Outcomes not recorded for: claude-code", "Skipped lines (not JSON objects): 0" and "Unknown or unrecognised records: 0". No row shows key text. Other rows may appear for other commands the agents ran.
If different: stop, and tell the orchestrator which rows or counts are wrong. Do not paste a real secret into a message.

**Part E (optional): #71's cap check, the 200-character cut and fail-closed** (steps 19 to 30)

Skip this part if you want. It runs in a throwaway project: a new empty folder outside this repo, with its own terminal and OpenCode session started in it. In steps 21 and 24 write the path to this repo where `<this-repo>` stands. Keep the throwaway's OpenCode open from step 22 to step 29, and restart it only in step 30.

### Step 19: Make the throwaway a git project

Run this in the empty folder, so OpenCode treats it as its own project.

```
git init
```

Expected: "Initialized empty Git repository".
If different: stop, and tell the orchestrator what was printed.

### Step 20: Create the plugin folder

```
mkdir -p .opencode/plugins
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.

### Step 21: Copy the plugin

```
cp <this-repo>/agent-kit/opencode/plugins/permission-log.js .opencode/plugins/permission-log.js
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.

### Step 22: Fail closed with no patterns file

Start OpenCode in the throwaway. This folder has no `agent-kit.conf` and no secret-patterns file, so the plugin cannot read the patterns, the same case as an unreadable file. Tell the agent: "Run `echo failclosed-check`." Choose **once**, then read the log:

```
tail -n 2 .agent-kit/logs/permissions/*.jsonl
```

Expected: the prompt appeared and the command ran. The `ask` line holds `"pattern":"[redacted: no patterns]"`, not the command.
If different: stop and tell the orchestrator what was printed.

### Step 23: Create the patterns folder

```
mkdir -p _docs/agent-kit/scripts
```

Expected: nothing printed.
If different: stop, and tell the orchestrator what was printed.

### Step 24: Copy the patterns file

```
cp <this-repo>/agent-kit/scripts/secret-patterns.txt _docs/agent-kit/scripts/secret-patterns.txt
```

Expected: nothing printed. The plugin reads the file on each record, so no restart is needed.
If different: stop, and tell the orchestrator what was printed.

### Step 25: Print a long test command, in the terminal and not through the agent

```
printf 'echo %0300d\n' 0
```

Expected: one line: `echo ` and 300 zeros.
If different: stop and tell the orchestrator what was printed.

### Step 26: Check the 200-character cut

Send the printed line as a request: Run `<the printed line>`. Check that the prompt shows the command. Choose **once**. Then count the cut record:

```
grep -c -E '"pattern":"echo 0{192}\.\.\.","source"' .agent-kit/logs/permissions/*.jsonl
```

Expected: `1`. The pattern is `echo `, 192 zeros and `...`, 200 characters in all.
If different: stop and tell the orchestrator what was printed.

### Step 27: Fill the day's log to just under the cap

Leave OpenCode open. This overwrites the log with 1048226 bytes of filler, which is 350 bytes under the cap of 1048576. The long ask from step 26 is 407 bytes, so it will not fit. The marker and a short record will.

```
head -c 1048226 /dev/zero > .agent-kit/logs/permissions/*.jsonl
```

Expected: nothing printed. If the shell says "ambiguous redirect", more than one log file exists; stop and tell the orchestrator.
If different: stop, and tell the orchestrator what was printed.
Risk: this empties the throwaway's log. It is a throwaway; it can't be undone.

### Step 28: Hit the cap

Send the same long line as in step 26, as a request, and choose **once**. Then count the `truncated` records:

```
grep -a -c '"event":"truncated"' .agent-kit/logs/permissions/*.jsonl
```

Expected: `1`. The filler holds no newline, so the marker is on its line.
If different: stop and tell the orchestrator what was printed. A `0` means the ask fitted, so the cap was not reached; say so.

### Step 29: Check nothing follows the marker in the same session

The reply to step 28's prompt is a smaller record that would fit under the cap. Count all records:

```
grep -a -c '"event"' .agent-kit/logs/permissions/*.jsonl
```

Expected: `1`. The one line is the filler with the marker, and the reply was dropped.
If different: stop and tell the orchestrator the count. A larger count is the #71 gap.

### Step 30: Check nothing follows the marker after a restart

Close OpenCode in the throwaway and open it again. Tell the agent: "Run `echo cap-check`." Choose **once**. This ask is 221 bytes and would fit under the cap if the marker were ignored. Then count all records:

```
grep -a -c '"event"' .agent-kit/logs/permissions/*.jsonl
```

Expected: `1`. The command ran, and no record was added after the marker.
If different: stop and tell the orchestrator the count. A `2` means the plugin ignored the marker after a restart (#71).

## Record the result

Write the OpenCode and Claude Code versions, today's date, and pass or fail for each step. Write the answers to the subagent questions (steps 12 and 16): whether the prompts appear in each tool's log, and whether the subagent's session can be told apart. If you skipped Part E, write "Part E skipped". Then the orchestrator records the outcome in `agent-kit/procedures/permission-log.md` and `agent-kit/opencode/START.md`. Commit this file with the result so a later run can compare. Results contain no secrets either.

Result recorded on 2026-11-08 by andrew. OpenCode `v2.2.5`; Claude Code `2.1.319`. Part E (steps 19 to 30) was skipped, as allowed above. The plugin was already installed and loaded before this run, so step 7 needed no OpenCode restart; the record below says so rather than claiming one.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | pass | `mkdir -p .opencode/plugins` printed nothing. The folder and plugin already existed from the earlier install. |
| 2 | pass | `cp` printed nothing. `cmp` against `agent-kit/opencode/plugins/permission-log.js` printed nothing, so the copy is byte-identical. |
| 3 | pass | `git add .opencode/plugins/permission-log.js` printed nothing. |
| 4 | pass | `HUMAN_APPROVED=1 git commit` made `99bf7c2`: `1 file changed, 148 insertions(+)`, `create mode 100644 .opencode/plugins/permission-log.js`. |
| 5 | pass | `git check-ignore .agent-kit/logs/` printed `.agent-kit/logs/`. |
| 6 | pass | `grep -c log_permission.py .claude/settings.json` printed `1`. |
| 7 | pass | No OpenCode restart: the plugin was already loaded in this session and wrote the records below; `git log -1 --format=%h -- .opencode/plugins/permission-log.js` printed `99bf7c2`. A fresh Claude Code session was started, and `/hooks` listed the `PermissionRequest` hook (`python3 "$CLAUDE_PROJECT_DIR"/agent-kit/claude-code/…`). No "Server plugin error" was seen. |
| 8 | pass | Prompt appeared and the command ran. `ask` for `touch .scratch/permlog-allowed`, `"tool":"opencode"`, `"type":"shell"`, id `per_1b8af220a001gi0AKwjwFii0D7`, session A `ses_e48bfacc1ffeolJ6E9vlFxVqiN`; `reply` with the same id and `"response":"once"`. |
| 9 | pass | `printf` printed `echo sk-` followed by 24 letters, as expected. The key text is not repeated here. |
| 10 | pass | Prompt appeared and the command ran. Newest `ask` had `"pattern":"echo [redacted]"`, id `per_1b8b0bbd7001y0nlNbc6OLdA6x`, followed by a `reply` with the same id and `"response":"once"`. |
| 11 | pass | `grep -c sk-a` printed `0`: the key never reached the log. |
| 12 | pass | The OpenCode subagent's `touch .scratch/permlog-subagent-opencode` produced an `ask`, id `per_1b8b15848001aYFTTo4bk7Ieaj`, session `ses_e474eb29fffeFEtjO1lXDMvwt4`. That differs from session A, so the OpenCode subagent's session can be told apart. |
| 13 | pass | Chose **reject** for `touch .scratch/permlog-rejected`. `ls .scratch/permlog-rejected` printed `No such file or directory`. |
| 14 | pass | `reply` with `"response":"reject"` and id `per_1b8b2573b0011DEPgZBiZNB9Nx`, the same as its `ask`. |
| 15 | pass | First attempt ran in Claude Code's **auto** mode: no dialog appeared and nothing was logged (auto mode emits no `PermissionRequest`). Repeated in manual mode (`--permission-mode manual`, Shift+Tab to manual) and the dialog appeared; chose **1. Yes** (allow once). `ask` for `touch .scratch/permlog-claude-allowed`, `"tool":"claude-code"`, `"type":"bash"`, no `id`, session B `5393bbd7-d747-416e-8547-1fdf7f4a455f`. The file was created. |
| 16 | pass | The subagent's `touch .scratch/permlog-subagent-claude` produced an `ask` with the same `sessionID` as session B (`5393bbd7-…`). So in Claude Code the subagent's session **cannot** be told apart. The command ran. |
| 17 | pass | Chose **No** (deny) for `touch .scratch/permlog-claude-denied`. The file was not created. The hook cannot record the outcome, so only the `ask` line exists. |
| 18 | pass | `make permission-report SINCE=2026-11-08T00:58Z` reported 5 log files (older days exist) and the expected rows: `claude-code` / `bash`, the three commands, each asked 1 with `-` outcomes; `opencode` / `shell`, `touch .scratch/permlog-allowed` asked 1 allowed 1, `echo [redacted]` asked 1 allowed 1, `touch .scratch/permlog-subagent-opencode` asked 1 allowed 1, `touch .scratch/permlog-rejected` asked 1 denied 1. `Outcomes not recorded for: claude-code`, `Skipped lines (not JSON objects): 0`, `Unknown or unrecognised records: 0`. One extra row, `claude --help`, came from a diagnostic probe run by the assistant; other rows are allowed. |
| 19 | skipped | Part E skipped by choice. |
| 20 | skipped | Part E skipped. |
| 21 | skipped | Part E skipped. |
| 22 | skipped | Part E skipped. |
| 23 | skipped | Part E skipped. |
| 24 | skipped | Part E skipped. |
| 25 | skipped | Part E skipped. |
| 26 | skipped | Part E skipped. |
| 27 | skipped | Part E skipped. |
| 28 | skipped | Part E skipped. |
| 29 | skipped | Part E skipped. |
| 30 | skipped | Part E skipped. |

Note for the docs: Claude Code in **auto** mode (now a permission mode) shows no dialog for commands it considers safe, so the hook logs nothing even though it is registered. The manual-mode run above is what the check records. The `claude --help` row in step 18 is a probe, not one of the checked commands.

## Risk

Low. Steps 2 and 4 add a plugin under a protected path that only observes. The `touch` commands create empty files in `.scratch/`; delete them afterwards with `make clean-scratch`. The fake key is made up and is not a credential; if redaction fails it sits in a git-ignored log, so don't paste it anywhere. If a step shows a real secret anywhere, stop and tell the orchestrator without repeating it. Part E overwrites a log in a throwaway folder and touches nothing in this repo.
