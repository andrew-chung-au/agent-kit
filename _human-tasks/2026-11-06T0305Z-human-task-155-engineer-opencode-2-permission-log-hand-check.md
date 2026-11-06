# Hand-check the permission log plugin on OpenCode 2.2.5

## Purpose

Confirm the V2 permission log plugin loads on OpenCode 2.2.5 and logs real prompts, so the open hand check in `procedures/permission-log.md` can be recorded. Issue: #155. Nothing below has been run: the Engineer has no OpenCode session here.

## Where to run it

In an interactive OpenCode 2.2.5 session in a project that has the kit installed (the folder holding `agent-kit.conf`). Use the normal interface, not `--auto`: auto-approval skips the prompts this checks. Not here: don't use the `!` prefix in OpenCode, which runs a command directly and skips the permission rules being tested. No tool enforces this.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check the version.

```
opencode --version
```

Expected: `opencode v2.2.5`.

2. Make sure `.scratch/` exists (creating it prompts too), and that the log folder is git-ignored (`.agent-kit/logs/` in `.gitignore`).

```
mkdir -p .scratch
```

Expected: no output.

## Steps

### Step 1: Install the plugin and restart OpenCode.

```
cp _docs/agent-kit/opencode/plugins/permission-log.js .opencode/plugins/permission-log.js
```

Expected: no output. After you restart OpenCode there is no "Server plugin error" about `permission-log.js`. (If the kit folder in your project is not `_docs/agent-kit`, use its real path.)
If different: stop, don't retry another way, and tell the orchestrator the exact error text.

### Step 2: Allow one command once.

Prompt the agent: "Run `touch .scratch/hand-check-allowed`." Choose **once**. Then read the log (today's UTC date in the file name):

```
tail -n 2 .agent-kit/logs/permissions/YYYY-MM-DD.jsonl
```

Expected: an `ask` line with `"pattern":"touch .scratch/hand-check-allowed"`, then a `reply` line with `"response":"once"` and the same `id`. The command ran.
If different: stop and tell the orchestrator what was printed.

### Step 3: Print a test command holding a fake key, in a terminal and not through the agent.

```
printf 'echo sk-%s\n' aaaaaaaaaaaaaaaaaaaaaaaa
```

Expected: it prints `echo sk-aaaaaaaaaaaaaaaaaaaaaaaa`. The fake key is not a credential.
If different: stop and tell the orchestrator what was printed.

### Step 4: Run that line in OpenCode and count lines holding the key.

Refusal test: use the OpenCode session. The aim is that the key never reaches the log.
Risk: if redaction fails, the fake key is written to the git-ignored log.

Paste the line from step 3 into OpenCode and choose **once**. Then count log lines holding the key:

```
grep -c sk-a .agent-kit/logs/permissions/YYYY-MM-DD.jsonl
```

Expected: the prompt still appeared, the newest `ask` line holds `"pattern":"echo [redacted]"`, and the count is `0`.
If different: stop and tell the orchestrator. Don't share the log; delete today's log file only after the orchestrator says so.

### Step 5: Reject one command.

Refusal test: use the OpenCode session. Reject goes last because a rejection ends the agent's turn.
Risk: if the plugin changed a decision, the command would run when it should not.

Prompt the agent: "Run `touch .scratch/hand-check-rejected`." Choose **reject**, then tell the agent to continue and check the file:

```
ls .scratch/hand-check-rejected
```

Expected: "No such file or directory", and the log gains a `reply` with `"response":"reject"`.
If different: stop using the plugin and report it.

## Record the result

Write pass or fail for each step. Then replace the `**Result:**` line in `procedures/permission-log.md` with the outcome (OpenCode version, date, pass or fail), and commit this file with the result. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

## Risk

The plugin only observes. The fake key is not a credential. `.scratch/hand-check-allowed` is a scratch file; delete it afterwards with `make clean-scratch`.
