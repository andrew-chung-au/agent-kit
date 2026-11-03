# Turn on the permission logs, run the real-session checks, and label the dry-run issues

> Written before asking the human, per `agent-kit/templates/human-task.md`. The repository is public: no secrets, tokens, private paths or machine names appear here. The one key-shaped string below is a made-up value.

## Purpose

**Status (2026-11-03): not yet run.** Turn on both permission loggers in the local sandbox, run the real-session checks that no agent can run (no OpenCode or live Claude Code session is available to the agents), and set the labels #56's dry runs need. Issues: #20 and #71 (OpenCode plugin), #36 (Claude Code logger), #56 (dry runs and measurements, which count prompts from these logs). The format and limits are in `agent-kit/procedures/permission-log.md`; the install steps are in `agent-kit/opencode/START.md` and `agent-kit/claude-code/START.md`.

Not covered here: #49's by-hand matcher checks (the existing task for #47 holds them), and #71's by-hand cap check in a throwaway project (a prefilled 1 MiB log, then a smaller record, then a restart). Kiro ran the cap rule under Node and the unit tests cover it; do the by-hand cap check only if you want it, and add it here as a step first.

## Where to run it

Parts A and B: the VS Code window opened on the `<repo>-sandbox` folder in its container, with a terminal for the commands and OpenCode and Claude Code sessions started in that folder. Part C: any terminal on your own machine where you are logged in to GitHub. Not here: the `!` prefix in OpenCode, which runs a command directly and skips the permission rules being tested. No tool enforces this. Never run `make` in a clean clone.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue. In steps that say "approve once", approve exactly that prompt and no other.

## Before you start

1. Check that this repo's last commit touching the Claude Code settings is the one that registers the hook, in the container terminal.

```
git log -1 --format=%h -- .claude/settings.json
```

Expected: `aa5f7c4` or a later commit.
If different: stop, run `git pull` in the container, and tell the orchestrator what was printed.

## Steps

**Part A: turn the logging on** (steps 1 to 4)

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
HUMAN_APPROVED=1 git commit -m "Install the OpenCode permission log plugin (#20)"
```

Expected: one file changed, created, mode 100644.
If different: stop, and tell the orchestrator what was printed.
Risk: this is the protected-file commit; you are the approver. The plugin is not active until OpenCode restarts.

**Part B: run the real-session checks** (steps 5 to 13)

Start a new OpenCode session (the plugin loads at start) and a new Claude Code session (the hook loads from the settings at start), both in the sandbox folder, before step 5.

### Step 5: OpenCode, allow one prompt

Send the agent this command and say: "Run this exact command with your bash tool as a permission-rule test. Don't judge it yourself." Approve it once.

```
touch .scratch/log-check-1
```

Expected: a permission prompt, then the file is created. The prompt looks as it did before the plugin.
If different: stop. A missing prompt or a changed prompt is a finding for #20; tell the orchestrator what you saw.
Refusal test: no. This step approves one prompt.
Risk: creates an empty file in `.scratch/`. Undo: delete it.

### Step 6: OpenCode, reject one prompt

Send the same kind of message with this command, and reject the prompt.

```
touch .scratch/log-check-2
```

Expected: a permission prompt, then the command does not run.
If different: stop, and tell the orchestrator what you saw.

### Step 7: OpenCode, a command holding a key-shaped string

Send this command the same way and reject the prompt. The string is made up and is not a real key.

```
echo sk-AAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

Expected: a permission prompt, and nothing runs.
If different: stop, and tell the orchestrator what you saw.
Refusal test: yes, in the OpenCode session, without the `!` prefix. It checks that the key-shaped text is redacted in the log.
Risk: if redaction fails, the made-up string appears in the log file and in the report in step 8. The log is git-ignored and local; delete that day's file from `.agent-kit/logs/permissions/` by hand to undo.

### Step 8: OpenCode, read the report

```
make permission-report
```

Expected: rows for `opencode`: `touch .scratch/log-check-1` asked 1 and allowed 1; `touch .scratch/log-check-2` asked 1 and denied 1; the `echo` row shows `[redacted]` and no key text.
If different: stop, and tell the orchestrator what the report shows, which rows or counts are wrong, and whether the key text appeared. Do not paste a real secret into a message.

### Step 9: Claude Code, allow one prompt and deny another

In the new Claude Code session, ask it to run this command and approve it once.

```
touch .scratch/log-check-3
```

Expected: a permission prompt that looks as it did before the hook, then the file is created.
If different: stop. A changed or missing prompt is a finding for #36.
Risk: creates an empty file in `.scratch/`. Undo: delete it.

### Step 10: Claude Code, deny one prompt

Ask it to run this command and deny the prompt.

```
touch .scratch/log-check-4
```

Expected: a permission prompt, then the command does not run.
If different: stop, and tell the orchestrator what you saw.

### Step 11: Claude Code, read the report

```
make permission-report
```

Expected: rows for `claude-code` with the two `touch` commands, each asked 1; the allowed and denied columns show `-` (the hook's events carry no outcome).
If different: stop, and tell the orchestrator what the report shows.

### Step 12: Both tools, subagent prompts

Ask each tool to start a subagent that runs this command, and approve or reject as you like, once per tool.

```
touch .scratch/log-check-5
```

Expected: a prompt from the subagent in each tool.
If different: note what you saw. This step records an answer; it has no wrong result.

### Step 13: Read the report for the subagent answer

```
make permission-report
```

Expected: this answers two open questions from #20 and #36: whether the subagent prompts appear at all, and whether they show as a separate session (the report counts distinct sessions per row). Write the answer for each tool in the record below.
If different: any result is recorded. If a tool shows no row for the subagent prompt, that is the answer.

**Part C: label the dry-run issues for #56** (steps 14 and 15)

The short PM launch comment is already on #94 (hash, `Proposed tier: light`, the expected path); read it before you label. #94 is the Light candidate: it says why a clean clone is never opened in a container, carved out of #12, which was too big for Light (more than 20 changed lines). It edits only `agent-kit/environments.md`, one of the Light allowed paths. #77 is the Standard one. Both edit `environments.md`, so they run one after the other, not together: #94 first.

### Step 14: Label #94 approved and Light

```
gh issue edit 94 --add-label approved --add-label tier:light
```

Expected: the issue URL is printed.
If different: stop, and tell the orchestrator what was printed.
Risk: lets the dry run start. Undo: `gh issue edit 94 --remove-label approved --remove-label tier:light`.

### Step 15: Label #77 Standard

```
gh issue edit 77 --add-label tier:standard
```

Expected: the issue URL is printed.
If different: stop, and tell the orchestrator what was printed.
Risk: records the tier for the dry run. Undo: `gh issue edit 77 --remove-label tier:standard`.

## Record the result

Paste the output or write pass or fail for each step. Write the OpenCode and Claude Code versions, and the answers to the subagent questions, here. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| 6 | | |
| 7 | | |
| 8 | | |
| 9 | | |
| 10 | | |
| 11 | | |
| 12 | | |
| 13 | | |
| 14 | | |
| 15 | | |

## Risk

Low. Step 2 and 4 add a plugin under a protected path that only observes. The `touch` commands create empty files in `.scratch/`. Steps 14 and 15 change labels and have an undo command each. The key-shaped string is made up. If a step shows a real secret anywhere, stop and tell the orchestrator without repeating it.
