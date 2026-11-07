# Confirm the merged GitHub wrappers write and read against real GitHub, including in Kiro Web

## Purpose

Check that the wrappers merged by #172 work against real GitHub and in Kiro Web. Issue: #172.

## Where to run it

A local checkout for Step 1, and a Kiro Web session on this repository for Step 2. Not here: Step 2 cannot run in a local checkout, because its git remote is not Kiro's gateway, so the failure #172 fixed would not reproduce there.

## Before you start

1. In the local checkout, confirm it is at or after the commit that closed #172.

```
git log --oneline -1
```

Expected: a line at or after `04d9bfb Add session summaries for #143, #170 and #172`.

## Steps

### Step 1: Confirm the PATCH close reached GitHub

```
gh api repos/andrew-chung-au/agent-kit/issues/172 --jq .state
```

Expected: `closed`. In a browser, the issue's last comment also starts with `Orchestrator: Close` (the POST shape) and has the `QA PASS commit:` and `Merge commit:` lines.

If different: the close or the comment did not reach GitHub; report what the wrapper printed, and do not close anything by hand.

### Step 2: Check the REST read in Kiro Web

In a Kiro Web session on this repository:

```
make issue-hash N=172
```

Expected: five lines, and `Body sha256:` equals the `Recorded sha256:` in the PM's 2026-11-06 comment on #172 (the record for `d369ddd8...cfa7`).

If different: the REST read returns something `gh issue view` did not; report the output.

## Record the result

Result recorded on 2026-11-07 by the orchestrator from the output below. Both steps passed: the REST close and comment reached GitHub, and the Kiro Web read returned the recorded hash.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | pass | `gh api repos/andrew-chung-au/agent-kit/issues/172 --jq .state` printed `closed`. The `Orchestrator: Close` comment was posted at https://github.com/andrew-chung-au/agent-kit/issues/172#issuecomment-6708521027. |
| 2 | pass | Kiro Web on `andrew-chung-au/agent-kit`; `make issue-hash N=172` exited 0. Output pasted below; `Body sha256:` equals `Recorded sha256:`. |

Step 2 output:

```
Body sha256: d369ddd89f0e29722f00ce7bdfac2284a3a97045c2e0a171803cd029fecdcfa7
Author: andrew-chung-au
Repository owner: andrew-chung-au
Owner-authored: yes
Recorded sha256: d369ddd89f0e29722f00ce7bdfac2284a3a97045c2e0a171803cd029fecdcfa7
```

Results contain no secrets.

## Risk

None: both steps only read. Step 1 reads the issue state with `gh api`; Step 2 reads a body hash.
