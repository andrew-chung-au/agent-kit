# <What the human will do, in a few words>

> Copy to `_human-tasks/`, named as in `procedures/session-summary.md` (kind `human-task`). Write it before asking the human, and link it instead of repeating the steps in chat. The repository is public: no secrets, tokens, private paths, home folders or machine names. If a step needs a value, say where to read it, never print it. No example may print a secret or the environment (`env`, `printenv`, `cat .env`, `gh auth token`, `/proc/self/environ`); use a safe variant such as `head -n 1 /etc/hostname`. A step that tests a refusal on purpose has a `Refusal test:` line saying which window to use and a `Risk:` line saying what would print if the rule fails. A test checks this wording in this file and in `_human-tasks/`; it cannot see what is later written into a copy, so a reviewer checks that.

## Purpose

<One line: what this achieves.> Issue: #<number> or none.

## Where to run it

<The window or tool: this sandbox, the clean clone, an OpenCode session, a browser.> Not here: <what to avoid, for example the `!` prefix in OpenCode, which runs a command directly and skips the permission rules being tested. No tool enforces this.>

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. <A check to make first, in one sentence.>

```
<one command>
```

Expected: <what it prints or shows.>

## Steps

### Step 1: <what this step does, in one sentence>

```
<one command>
```

Expected: <what the output or result looks like.>
If different: <what it means. Stop, don't retry another way, and tell the orchestrator what was printed.>
Risk: <only when the step changes live behaviour (a push, a label, a config edit): what changes, and the undo command or "can't be undone".>

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |

## Risk

<What could go wrong across the whole task, or "none".>
