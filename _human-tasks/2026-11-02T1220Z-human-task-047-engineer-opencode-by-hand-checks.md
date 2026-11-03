# Check OpenCode's permission rules by hand

## Purpose

**Status (2026-11-03): only steps 10 and 11 are outstanding.** The human already ran steps 1 to 9 on 2026-11-02 (OpenCode 1.19.5); their results are in the "Recorded" lines below and on #47. Do not run them again unless OpenCode has been upgraded since 1.19.5. Steps 10 and 11 have never been run in a real session.

Repeat the by-hand permission checks recorded for #47, plus the two spot-checks that only tests have covered, so a later OpenCode upgrade can be compared with the 2026-11-02 results. Issue: #47 (closed); written under #50. The evidence is in the `Orchestrator:` comments on #47 and `agent-kit/opencode/START.md` ("Permission rules"); this file holds only the steps.

## Where to run it

An OpenCode session started in this repo's folder (not the repository root), restarted after the last change to `opencode.json`. Send each command as its own message, and say: "Run this exact command with your bash tool as a permission-rule test. Don't judge it yourself." OpenCode agents often refuse by judgment before a rule is reached. Not here: the `!` prefix in OpenCode, which runs a command directly and skips the permission rules being tested. No tool enforces this.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue. In every step below, reject the prompt; approving is not part of the check.

## Before you start

1. Check the OpenCode version, in a separate terminal. The recorded results are for 1.19.5; another version means the results are not directly comparable.

```
opencode --version
```

Expected: `1.19.5`.
If different: note the version in the record, then carry on; compare with care.

2. Check which commit last changed the permission rules.

```
git log -1 --format=%h -- opencode.json
```

Expected: `38f04f4` or a later commit.
If different: stop, and tell the orchestrator what was printed.

3. Check nothing is staged, so the commit steps cannot commit anything.

```
git status --short
```

Expected: nothing printed, or only files you expect to be unstaged.
If different: stop, and tell the orchestrator what was printed.

## Steps

Each step lists what was recorded on 2026-11-02 (OpenCode 1.19.5, DeepSeek V4.1 Flash Free, one session) so you can compare.

### Step 1: Chain with an unallowed command

```
ls ; touch .scratch/marker1
```

Expected: a prompt for the `touch` command alone; `ls` runs without one. Recorded: prompted.
If different: stop, and tell the orchestrator what was printed.
Refusal test: yes, in the OpenCode session, without the `!` prefix.
Risk: if you approve the prompt, an empty file `.scratch/marker1` is created. Undo: delete that file.

### Step 2: Command substitution

```
ls $(pwd)
```

Expected: a prompt. Recorded: prompted (the exact command text was not recorded; this is the same kind).
If different: stop, and tell the orchestrator what was printed.
Refusal test: yes, in the OpenCode session, without the `!` prefix.
Risk: harmless if approved; it lists the folder.

### Step 3: Redirect

```
ls > .scratch/redirect-test
```

Expected: a prompt. Recorded: prompted (the exact command text was not recorded; this is the same kind).
If different: stop, and tell the orchestrator what was printed.
Refusal test: yes, in the OpenCode session, without the `!` prefix.
Risk: if you approve the prompt, a file `.scratch/redirect-test` is created. Undo: delete that file.

### Step 4: Absolute path

```
head -n 1 /etc/hostname
```

Expected: a prompt. Recorded: prompted. It is not known whether the path ask or `external_directory` caused it.
If different: stop, and tell the orchestrator what was printed.

### Step 5: Parent folder

```
ls ..
```

Expected: a prompt. Recorded: prompted.
If different: stop, and tell the orchestrator what was printed.

### Step 6: Amend a commit

```
git commit --amend --dry-run -m x
```

Expected: a prompt. Recorded: prompted.
If different: stop, and tell the orchestrator what was printed. The command is a dry run and changes nothing.

### Step 7: Skip the hooks with the short option

```
git commit -n -m x
```

Expected: denied, naming the rule `git commit -n*`. Recorded: denied.
If different: stop, and tell the orchestrator what was printed.
Risk: if the rule fails and you approve, a commit named `x` is made with the hooks skipped (nothing is committed when nothing is staged). Undo: `git reset --soft HEAD~1`.

### Step 8: Name an env file

```
ls .env
```

Expected: denied, naming the rule `*.env*`. Recorded: denied.
If different: stop, and tell the orchestrator what was printed.
Refusal test: yes, in the OpenCode session, without the `!` prefix.
Risk: this safe variant lists a name and prints no content. The real check is `cat .env`, which would print secrets if the rule failed; it is not used here.

### Step 9: Print a token

```
gh auth token --help
```

Expected: denied by the permission rule. Recorded: denied.
If different: stop, and tell the orchestrator what was printed.
Refusal test: yes, in the OpenCode session, without the `!` prefix.
Risk: this safe variant prints help text only. The real command `gh auth token` would print the token if the rule failed; it is not used here.

### Step 10: Skip the hooks with an abbreviated long option

```
git commit --no-veri -m x
```

Expected: denied (covered by tests only; never run in a real session). Recorded: none yet.
If different: stop, and tell the orchestrator what was printed.
Risk: if the rule fails and you approve, a commit named `x` is made with the hooks skipped (nothing is committed when nothing is staged). Undo: `git reset --soft HEAD~1`.

### Step 11: A sibling of `git diff`

```
git difftool
```

Expected: a prompt (covered by tests only; never run in a real session). Recorded: none yet.
If different: stop, and tell the orchestrator what was printed.
Risk: if you approve the prompt, git may start a configured diff tool. Reject it.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Recorded 2026-11-02 | This run (pass or fail, note) |
|---|---|---|
| Before 1 | | |
| Before 2 | | |
| Before 3 | | |
| 1 | prompted | |
| 2 | prompted | |
| 3 | prompted | |
| 4 | prompted | |
| 5 | prompted | |
| 6 | prompted | |
| 7 | denied | |
| 8 | denied | |
| 9 | denied | |
| 10 | none yet | |
| 11 | none yet | |

## Risk

Only steps 1, 3, 7 and 10 could change anything, and only if you approve a prompt instead of rejecting it. Steps 8 and 9 use safe variants; no step prints a secret unless a rule fails on a real secret-printing command, and none is used.
