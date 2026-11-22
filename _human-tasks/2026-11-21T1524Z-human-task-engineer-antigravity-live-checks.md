# Check Antigravity CLI's rules, hooks, subagents and skills by hand

## Purpose

**Status (2026-11-21): run, all twenty steps recorded.** Settle the live questions behind a possible Antigravity layer before any of it is written: whether `AGENTS.md` loads and walks parent folders, what a `PreToolUse` hook does on deny, crash, silence and timeout, whether a subagent and a skill are discovered, and whether headless mode soft-denies. Issue: none. The fixture is `.scratch/agy-spike/` in this working tree; it is git-ignored and `make clean-scratch` deletes it. The findings feed `_docs/planning/antigravity-cli.md`.

**No credential is involved.** The CLI runs on the Antigravity starter quota, which needs no key and no sign-in, so there is nothing to set up before the behaviour checks. The API-key and proxy path was measured separately and is recorded in the planning doc.

## Where to run it

A terminal at the repository root, in `.scratch/agy-spike` for step 1, then one interactive `agy --dangerously-skip-permissions` session in the same terminal for steps 2 to 4 and 7 to 18, and a new session in the same terminal in `.scratch/agy-spike/parent/child` for step 5. Steps 6, 8, 10, 12, 14 and 19 change the hook's mode from a second terminal in `.scratch/agy-spike`.

Not here: a CodeBuddy session. The point is `agy`'s own behaviour, and a second agent in the loop would hide what the first one did.

Step 1 is headless and needs no session. Step 20 is headless again and can run in any container terminal.

## Before you start

1. Record the CLI version.

```
agy --version
```

Expected: `1.5.14`, or another version; write it in the record.

2. Confirm the fixture is present. If it is missing, stop: it is scratch and not committed.

```
ls -a .scratch/agy-spike
```

Expected: `AGENTS.md`, `.agents` and `parent` among the entries.

3. Confirm the API-key switch is off, so the CLI uses the starter quota.

```
grep -c modelProvider ~/.gemini/antigravity-cli/settings.json
```

Expected: `0`, and the command exits 1 because nothing matched. If different: `1` means `"modelProvider": "gemini"` is still set and the CLI will insist on `GEMINI_API_KEY`; remove that line before going on.

4. Confirm the hook points at this checkout. If it names another path, edit that line before starting, then carry on.

```
grep agent-kit-sandbox .scratch/agy-spike/.agents/hooks.json
```

Expected: one line with the absolute path to `.scratch/agy-spike/.agents/hook.py` under this checkout.

5. Confirm the hook starts in deny mode.

```
cat .scratch/agy-spike/.agents/mode
```

Expected: `deny`.

6. Confirm nothing is staged, so no step can commit.

```
git status --short
```

Expected: no `M ` or `A ` line; ` M` and `??` lines are fine.

## Steps

### Step 1: One headless request on the starter quota

Run this from `.scratch/agy-spike`.

```
agy -p "Reply with exactly OK" --output-format json
```

Expected: one JSON object with `"status":"SUCCESS"` and `"response"` containing `OK`. Write the model and the token counts in the record.
If different: `429` means the quota, not a broken setup; write `quotaId` or `quotaMetric` and stop. A message naming `GEMINI_API_KEY` means the API-key switch is still on; go back to pre-check 3.

### Step 2: Start the interactive session

```
agy --dangerously-skip-permissions
```

Expected: the banner names `(Antigravity Starter Quota)` and a model, and the session stays open; leave it open for steps 3 to 18. The flag turns the permission prompt off, so from step 7 onward a block can only come from the hook; without it, a permission prompt and a hook deny look the same in the transcript.
If different: if it asks for a key or a sign-in, stop; the starter quota is not available on this machine.

### Step 3: Record the starting quota

Send this in the session from step 2.

```
/usage
```

Expected: weekly limits for the Gemini group and for the Claude and GPT group. Write both percentages and the reset time, so step 20's consumption can be compared against them.
If different: if the command is unknown, record that and carry on; the quota is a measurement here, not a gate.

### Step 4: Does the project file load

Send this message in the session from step 2.

```
Without running any command and without reading any file, name the instruction files you were given when this session started. For each, give its path if you were told one, and quote its first line exactly. If you were given none, say so.
```

Expected: `# Spike instructions`, and the repository's `AGENTS.md` alongside it, because the walk goes up to the checkout root. Record whether the answer names a path.
If different: if it runs a command or opens a file to answer, the probe is inconclusive rather than failed; record that, and the marker it quoted.

### Step 5: Does a parent folder's file load

Start a new `agy --dangerously-skip-permissions` session in `.scratch/agy-spike/parent/child`, then send the same message.

```
Without running any command and without reading any file, name the instruction files you were given when this session started. For each, give its path if you were told one, and quote its first line exactly. If you were given none, say so.
```

Expected: `# Child instructions`, `# Parent instructions`, `# Spike instructions` and `# AGENTS.md`, so every level up to the checkout root is in context.
If different: if only the child marker appears, parent walking is off or bounded; record which markers appear. If it reads files to answer, record that instead, because the probe then says nothing about walking.

### Step 6: Put the hook in deny mode

Run this in the second terminal, from `.scratch/agy-spike`.

```
echo deny > .agents/mode
```

Expected: no output.
If different: if the shell refuses the write, the fixture is not where the task says; stop.

### Step 7: A deny decision blocks a command

Send this message in the `agy` session from step 4.

```
Run this exact command with your shell tool, as a hook test. Do not judge it yourself, do not retry, do not substitute another command, and do not ask for approval first: echo hook-deny test
Then quote verbatim what came back, whether that is an error or the command's output.
```

Expected: blocked before it runs, with `spike deny` in the message.
If different: if it runs and prints `hook-deny test`, a deny decision does not block; record and stop. If it does not block, repeat this step once in a session started without the flag before concluding anything, so that a flag which bypasses hooks is not mistaken for a hook that is absent.

### Step 8: Put the hook in crash mode

Run this in the second terminal.

```
echo fail > .agents/mode
```

Expected: no output.
If different: stop; the mode file did not change.

### Step 9: A crashing hook

Send this message in the same session.

```
Run this exact command with your shell tool, as a hook test. Do not judge it yourself, do not retry, do not substitute another command, and do not ask for approval first: echo hook-fail test
Then quote verbatim what came back, whether that is an error or the command's output.
```

Expected: record one of two outcomes. `blocked` means a crash fails closed; `ran` means it fails open, which the adapter must never rely on.
If different: if the agent refuses on its own, record `refused`; the hook was not reached.

### Step 10: Put the hook in silent mode

Run this in the second terminal.

```
echo empty > .agents/mode
```

Expected: no output.
If different: stop; the mode file did not change.

### Step 11: A hook that prints nothing

Send this message in the same session.

```
Run this exact command with your shell tool, as a hook test. Do not judge it yourself, do not retry, do not substitute another command, and do not ask for approval first: echo hook-empty test
Then quote verbatim what came back, whether that is an error or the command's output.
```

Expected: record `blocked` or `ran`. A silent hook has no decision, so this is the second fail-open case to check.
If different: if the agent refuses on its own, record `refused`.

### Step 12: Put the hook in slow mode

Run this in the second terminal.

```
echo slow > .agents/mode
```

Expected: no output.
If different: stop; the mode file did not change.

### Step 13: A hook that outlives the timeout

Send this message in the same session, then wait about 40 seconds.

```
Run this exact command with your shell tool, as a hook test. Do not judge it yourself, do not retry, do not substitute another command, and do not ask for approval first: echo hook-slow test
Then quote verbatim what came back, whether that is an error or the command's output.
```

Expected: record when it returns and whether the command `blocked` or `ran`. The documented default timeout is 30 seconds.
If different: if it hangs beyond a minute, record that and stop the session; the timeout did not apply.

### Step 14: Put the hook in allow mode

Run this in the second terminal.

```
echo allow > .agents/mode
```

Expected: no output.
If different: stop; the mode file did not change.

### Step 15: An allow decision

Send this message in the same session.

```
Run this exact command with your shell tool, as a hook test. Do not judge it yourself, do not retry, do not substitute another command, and do not ask for approval first: echo hook-allow test
Then quote verbatim what came back, whether that is an error or the command's output.
```

Expected: it runs and prints `hook-allow test`. A prompt cannot appear here, because the session started with `--dangerously-skip-permissions`, so this step tests only whether an allow decision is honoured.
If different: if it is blocked, an allow decision does not override the hook; record the exact message.

### Step 16: What the hook receives

Run this in the second terminal, from `.scratch/agy-spike`.

```
head -c 600 .agents/hook-input.json
```

Expected: JSON with a `toolCall` object holding a `name` and `args`. Write the tool name and the args keys in the record. Check the text before pasting it anywhere.
If different: if the file is missing, the hook did not run; record that.

### Step 17: The subagent

Send this message in the same session.

```
Delegate this to the subagent named spike and report its reply word for word. If there is no subagent named spike, say exactly that and do nothing else.
```

Expected: `spike subagent ran`. Also open `/agents` and record whether `spike` is listed.
If different: if it answers that there is no such subagent, record that; the fixture's `.agents/agents/spike.md` was not discovered. If it hangs, the `tools` list names a tool this build does not know; record the hang and stop.

### Step 18: The skill

Start a new `agy --dangerously-skip-permissions` session in `.scratch/agy-spike`, then send this message without naming the skill as a command.

```
I need help with SPIKE-SKILL. If you use a skill to answer, name the skill you used. If you use none, say so.
```

Expected: record whether the agent says `spike skill ran` on its own, and whether it names the skill. That tells us whether a skill can be kept out of the model's reach.
If different: if it says it used no skill, record that; the skill's description did not match. If it treats the name as a command, the probe is about invocation rather than discovery; record that instead.

### Step 19: Put the hook back in deny mode

Run this in the second terminal.

```
echo deny > .agents/mode
```

Expected: no output.
If different: stop; the mode file did not change.

### Step 20: Headless mode with a blocked command

Run this in any container terminal, from `.scratch/agy-spike`.

```
agy -p "Run echo headless test with your shell tool. Do not ask for approval and do not substitute another command." --output-format json
```

Expected: write `status` and whether the response mentions a denial. The documentation says an unapprovable action is soft-denied and the run still exits 0.
If different: if the run fails, record the error; that is also a usable answer.

## Record the result

**Status (2026-11-21): run, all twenty steps recorded.** Run by the repository owner in this dev container on `agy` 1.5.14. Results contain no secrets.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | pass | `status: SUCCESS`, response `OK`, model `gemini-3.8-flash`, 12,200 tokens (12,131 in) |
| 2 | pass | banner `(Antigravity Starter Quota)`, `Gemini 3.8 Flash (High)`; `/usage` names the account |
| 3 | pass | Gemini 97.76%, resets in 167h 42m; it read 99.26% before the session started |
| 4 | pass | `/workspaces/agent-kit-sandbox/AGENTS.md` and `.scratch/agy-spike/AGENTS.md` (`# Spike instructions`), with no command run |
| 5 | pass | four files: repo `AGENTS.md`, spike `AGENTS.md`, `parent/AGENTS.md` (`# Parent instructions`), `AGENTS.md` (`# Child instructions`) |
| 6 | pass | mode `deny` |
| 7 | pass | blocked: `tool call denied by pre-tool hook: spike deny: deny` |
| 8 | pass | mode `fail` |
| 9 | pass | blocked: `JSON hook ... failed: command failed: exit status 1`; a crash fails closed |
| 10 | pass | mode `empty` |
| 11 | pass | ran: `hook-empty test`, exit 0; a hook that prints nothing **fails open** |
| 12 | pass | mode `slow` |
| 13 | pass | blocked: `command failed: signal: killed`; the 30 s timeout fails closed |
| 14 | pass | mode `allow` |
| 15 | pass | ran: `hook-allow test` |
| 16 | pass | keys `artifactDirectoryPath`, `conversationId`, `cwd`, `hookEventName`, `lastUserInput`, `modelName`, `stepIdx`, `toolCall` |
| 17 | pass | `spike subagent ran`, one subagent spawned |
| 18 | pass | `spike skill ran`, `Skill used: spike-skill`; it also read `SKILL.md` and ran 4 shell commands |
| 19 | pass | mode `deny` again, inferred from step 20's message |
| 20 | pass | `status: SUCCESS`, the response names the denial, exit 0; headless soft-denies |

The one result that changes a design: an empty hook allows the command, while a crash and a timeout both block. A guard adapter must therefore always print an explicit decision and never exit 0 silently.

## Risk

No credential is involved: the CLI uses the starter quota, so no key is exported, stored or read anywhere in this task. Every command the agent is asked to run is `echo`, so nothing changes on disk except `.agents/mode` and `.agents/hook-input.json`. The slow step waits about 40 seconds. `hook-input.json` holds the last tool call, which contains no secret, but read it before pasting it into the record. The fixture is scratch and is deleted by `make clean-scratch`. No global setting is edited, so this task does not test `command(...)` permission rules; that is a separate question.
