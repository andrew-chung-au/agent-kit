# Confirm the merged GitHub wrappers write and read against real GitHub, including in Kiro Web

## Purpose

Check that the wrappers merged by #172 work against real GitHub and in Kiro Web. Issue: #172.

## Where to run it

GitHub in a browser, and a Kiro Web session on this repository. Not here: the Kiro Web check cannot run in this sandbox, and its git remote is not the one that fails there.

## Before you start

1. Open issue #172 on GitHub and find the `Orchestrator:` Close comment posted at the end of the 2026-11-07 closing session.

Expected: the comment starts with `Orchestrator:` and has `QA PASS commit:`, `Merge commit:`, `Verify:` and `Summary:` lines, and the issue shows as closed.

## Steps

### Step 1: Confirm the write shapes worked

In a browser, look at issue #172: the Close comment above was posted with `make issue-comment` (a REST POST) and the issue was closed with `make issue-close` (a REST PATCH), both through the merged wrappers.

Expected: the comment exists and the issue is closed. If different: the POST or PATCH shape failed against real GitHub; report what the wrapper printed, and do not close anything by hand.

### Step 2: Check the REST read in Kiro Web

In a Kiro Web session on this repository:

```
make issue-hash N=172
```

Expected: five lines, and `Body sha256:` equals the `Recorded sha256:` in the PM's 2026-11-06 comment on #172 (the record for `d369ddd8...cfa7`). If different: the REST read returns something `gh issue view` did not; report the output.

## Record the result

Write pass or fail for each step, and paste the `make issue-hash` output. Commit this file with the result so a later run can compare. Results contain no secrets either.
