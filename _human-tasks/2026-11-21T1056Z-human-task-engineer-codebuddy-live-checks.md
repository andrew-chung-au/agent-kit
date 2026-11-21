# Check CodeBuddy's hooks, permissions and rule loading by hand

## Purpose

Settle the live questions behind the CodeBuddy layer before its settings template is written: whether the permission syntax uses a space or a colon, whether `PreToolUse` exit 2 blocks Bash, whether a failing hook is still blocked by the `|| exit 2` wrapper, which events and payload fields CodeBuddy sends, whether a subagent frontmatter `Stop` hook runs without `allowUntrustedFrontmatterHooks`, and whether a parent `CODEBUDDY.md` shadows a project `AGENTS.md`. Issue: none. The fixture is `.scratch/codebuddy-spike/` in this working tree; it is git-ignored and was prepared for this run. The decisions it feeds are in `_docs/planning/kit-1.11/README.md` under "CodeBuddy (in progress)".

## Where to run it

A CodeBuddy session started in the folder named by each step: the fixture root for steps 1 to 13, then `parent/child-on` and `parent/child`. Use a separate terminal at the repository root for the inspection commands. The fixture is scratch: it is not committed, and `make clean-scratch` deletes it. If it is missing, stop and ask the orchestrator to recreate it.

Not here: the `!` prefix, which runs a command directly and skips the permission rules being tested. No tool enforces this.

Restart CodeBuddy after every settings change and start a new session in the folder named by the step: CodeBuddy reads settings, rules and hooks only at session start. Reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue. If the first session warns about `memory.parentDiscovery`, record the warning, remove that block from the fixture's settings, restart, and carry on; the parent check in steps 14 and 15 still runs with the setting in the child folder.

Redaction: `capture.jsonl` is written by a script that redacts common token shapes and truncates long strings, but read it before pasting. Remove any path, user name or token. Never paste a raw payload into an issue or chat.

## Before you start

1. Confirm the fixture is present. If it is not, stop: it is scratch and not committed.

```
ls -a .scratch/codebuddy-spike
```

Expected: `AGENTS.md`, `parent` and `.codebuddy` among the entries.

2. Confirm the fixture points at this checkout's guard. If it names another path, edit that line to this checkout before starting, then carry on.

```
grep guard_git.py .scratch/codebuddy-spike/.codebuddy/settings.json
```

Expected: one line naming the absolute path to `agent-kit/claude-code/hooks/guard_git.py` under this checkout.

3. Confirm the guard's unit tests pass, so a live block later is not a code defect.

```
python3 -B -m unittest tests.test_guard_git
```

Expected: `Ran 36 tests` and `OK`.

4. Confirm nothing is staged, so no step can commit.

```
git status --short
```

Expected: no `M ` or `A ` line (nothing staged); ` M` and `??` lines are fine.

5. Record the CodeBuddy version.

```
codebuddy --version
```

Expected: a version number, for example `2.185.0`. Write it in the record.

## Steps

### Step 1: The allow rule with a space before the wildcard

Send this message in a session started in `.scratch/codebuddy-spike`.

```
Run this exact command with your bash tool as a permission test. Don't judge it yourself.
echo allow-space test
```

Expected: it runs with no prompt if CodeBuddy honors `Bash(echo allow-space *)`. A prompt means the space form is not honored, so record `prompted`.
If different: if the agent refuses by its own judgment, record `refused` and note that the rule was not reached.
Risk: none; `echo` prints text.

### Step 2: The allow rule with a colon before the wildcard

Send this message in the same session.

```
Run this exact command with your bash tool as a permission test. Don't judge it yourself.
echo allow-colon test
```

Expected: it runs with no prompt if CodeBuddy honors `Bash(echo allow-colon:*)`. A prompt means the colon form is not honored.
If different: if the agent refuses by its own judgment, record `refused` and note that the rule was not reached.
Risk: none; `echo` prints text.

### Step 3: The deny rule with a space before the wildcard

Send this message in the same session.

```
Run this exact command with your bash tool as a permission test. Don't judge it yourself.
echo deny-space test
```

Expected: blocked with no way to approve if the space form is honored. A prompt means the form is not honored, so record `prompted`.
If different: if the command runs, the deny rule is not a hard stop; record `ran` and stop.
Risk: none; `echo` prints text.

### Step 4: The deny rule with a colon before the wildcard

Send this message in the same session.

```
Run this exact command with your bash tool as a permission test. Don't judge it yourself.
echo deny-colon test
```

Expected: blocked with no way to approve if the colon form is honored. A prompt means the form is not honored, so record `prompted`.
If different: if the command runs, the deny rule is not a hard stop; record `ran` and stop.
Risk: none; `echo` prints text.

### Step 5: `PreToolUse` exit 2 blocks a Bash command

Send this message in the same session.

```
Run this exact command with your bash tool as a guard test. Don't judge it yourself.
git push --dry-run
```

Expected: blocked before git runs, with the guard's message that says "Don't push".
If different: if it prompts or runs, the hook did not block; stop, copy the message, and do not try another command.
Risk: `--dry-run` changes nothing on the remote. If the guard fails and you approve a prompt, it only contacts the remote; the token is read-only. Reject any prompt.

### Step 6: A failing hook is still blocked by the `|| exit 2` wrapper

Send this message in the same session.

```
Run this exact command with your bash tool as a guard test. Don't judge it yourself.
echo hook-fail test
```

Expected: blocked, and the message includes "spike hook failing on purpose", which shows the wrapper turned exit 1 into a block.
If different: if it runs and prints `hook-fail test`, the wrapper did not fail closed; record and stop.
Risk: none; `echo` prints text.

### Step 7: Which tool calls reach `PreToolUse`

Send this message in the same session.

```
Read AGENTS.md with your read tool, then run echo capture test with your bash tool.
```

Expected: the read shows `SPIKE-AGENTS-MARKER` and the command prints `capture test`.
If different: if the agent uses only one tool, ask it to use the other, then continue.
Risk: none.

### Step 8: Inspect the recorded tool names

Run this in the separate terminal at the repository root.

```
grep tool_name .scratch/codebuddy-spike/capture.jsonl
```

Expected: at least one line with `"tool_name": "Read"` and one with `"tool_name": "Bash"`, which shows `PreToolUse` fired for both.
If different: record which tool names appear and which are missing.
Risk: the file is redacted; still check it before pasting.

### Step 9: A permission request and its denial

Send this message in the same session.

```
Run this exact command with your bash tool as a permission test. Don't judge it yourself.
echo ask test
```

Expected: a permission prompt appears because no rule covers the command. Reject it, then tell the agent to continue.
If different: if no prompt appears, record `ran` or `denied` and note the default mode.
Risk: none; `echo` prints text. Reject the prompt.

### Step 10: Inspect the permission events

Run this in the separate terminal at the repository root.

```
grep Permission .scratch/codebuddy-spike/capture.jsonl
```

Expected: a `PermissionRequest` line and a `PermissionDenied` line. Note whether the denial carries an `id` or `tool_use_id` that matches the request.
If different: if either line is missing, the event did not fire; record which.
Risk: the file is redacted; still check it before pasting.

### Step 11: A subagent frontmatter `Stop` hook without the trust flag

Send this message in the same session.

```
Use the spike subagent and report what it says.
```

Expected: the subagent says `spike subagent ran`.
If different: if no subagent runs, record `not run` and skip steps 12 and 13.
Risk: none.

### Step 12: Check the subagent's stop hook ran

Run this in the separate terminal at the repository root.

```
ls .scratch/codebuddy-spike/stop-count
```

Expected: the file exists, which means the frontmatter `Stop` hook ran without `allowUntrustedFrontmatterHooks`.
If different: if the file is missing, the hook did not run; record any warning that names the flag.
Risk: none.

### Step 13: Inspect the subagent event

Run this in the separate terminal at the repository root.

```
grep SubagentStop .scratch/codebuddy-spike/capture.jsonl
```

Expected: a `SubagentStop` line with an agent identifier: `agent_id`, `agent_type` or `agent_name`.
If different: if the line is missing, `SubagentStop` did not fire. If it has no identifier, record that the payload cannot tell one subagent from another.
Risk: the file is redacted; still check it before pasting.

### Step 14: Parent discovery with the default setting

Start a new session in `.scratch/codebuddy-spike/parent/child-on`, then send this message.

```
List every instruction marker you can see that starts with SPIKE-. Quote each one exactly.
```

Expected: record which markers appear. If the parent `CODEBUDDY.md` shadows the child `AGENTS.md`, `SPIKE-PARENT-CODEBUDDY` appears and `SPIKE-CHILD-ON-AGENTS` does not. If the child file still loads, `SPIKE-CHILD-ON-AGENTS` appears. `SPIKE-PARENT-AGENTS` may also appear if the parent agents file is discovered.
If different: if no marker appears, record that no project instructions loaded.
Risk: none.

### Step 15: Parent discovery turned off

Start a new session in `.scratch/codebuddy-spike/parent/child`, which sets `memory.parentDiscovery` to false, then send the same message.

```
List every instruction marker you can see that starts with SPIKE-. Quote each one exactly.
```

Expected: only `SPIKE-CHILD-OFF-AGENTS` appears. Also record whether the session warned about `memory.parentDiscovery`.
If different: if a parent marker appears, the setting was ignored; record the warning.
Risk: none.

## Record the result

For each step, write one of these words plus the first line of the message CodeBuddy showed. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Word | What you see | What it means |
| :--- | :--- | :--- |
| runs | The command runs with no prompt. | The rule or hook let it through. |
| prompted | A permission box asks you to approve or reject. | The rule is set to ask, or no rule covers the command. |
| denied | The command is blocked with no way to approve. | The rule is a hard stop. |
| refused | The agent declines in its own words. | The model decided before any rule was reached; the rule was not tested. |
| blocked | A hook stops the tool before it runs. | The hook's exit 2 (or the wrapper) blocked it. |

| Step | Expected | Observed | Pass or fail |
|---|---|---|---|
| 1 | allow-space runs | | |
| 2 | allow-colon runs or prompts | | |
| 3 | deny-space blocked or prompted | | |
| 4 | deny-colon blocked or prompted | | |
| 5 | blocked by the guard | | |
| 6 | blocked with the hook's message | | |
| 7 | read and bash both happen | | |
| 8 | Read and Bash tool names recorded | | |
| 9 | a prompt appears and is rejected | | |
| 10 | both permission events recorded | | |
| 11 | the subagent runs | | |
| 12 | `stop-count` exists | | |
| 13 | a `SubagentStop` line with an identifier | | |
| 14 | markers recorded for the default | | |
| 15 | only the child marker, no warning | | |

## Risk

Steps 5 and 9 are the only ones that could run a command with an effect if a rule fails: `git push --dry-run` contacts the remote but changes nothing, and `echo ask test` prints text. No step prints a secret or reads an env file. The capture file is redacted but must be checked before it is pasted or committed.
