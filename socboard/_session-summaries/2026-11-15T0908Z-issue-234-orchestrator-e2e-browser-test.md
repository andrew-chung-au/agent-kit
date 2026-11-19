# Issue #234: End-to-end browser test against the Compose stack (D13)

**Date:** 2026-11-15T09:08Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

`make e2e` drives the built site in a real browser against a running Compose stack, with two Analysts and a Lead, and CI runs it after the stack tests. Before this, every test ran the backend alone or the frontend against an in-memory mock; nothing drove the site through the real proxy, app and Postgres roles. This is D13 of the Deploy phase.

- `e2e/` holds Playwright 1.65.1 (the human approved the dependency), its own `package.json`, `bun.lock` and `bunfig.toml` (the frontend's 24-hour release-age guard copied), and three test groups: a journey (three alerts ingested through the API out of queue order; `analyst-a` sees them most severe first with the older of two High alerts first, claims and starts one; `analyst-b`, whose page was opened before the claim, gets the server's 409 and the owner stays `analyst-a`; closing without a reason is not possible; `analyst-a` closes with a reason; the Lead reads exactly four audit rows, with the start and the close told apart), a hostile-text test (a script tag and an image tag in an alert show as text and run nothing) and a wrong-password test, plus 25 browser-free tests of the loopback-only address rule.
- A run makes 4 ingest requests and 5 sign-ins (1 failed). Cases are found by a unique marker, never by counts, so a second run works.
- `e2e/redact_traces.py` (tested in `tests/test_e2e_redact.py`): Playwright has no option to hide typed values, and a trace records the password typed and the bearer token the page sends, so CI replaces every value of the run's secrets file (plain, JSON-escaped, URL-encoded), every bearer token and the login token before the artifact is uploaded, refuses a value under 8 characters, and does not upload if it fails.
- Protected, applied by the human in `30c68d9` on the PR branch: `.PHONY: e2e` and the targets `e2e-install` and `e2e` in `Makefile`, the `E2E:` and Layout lines of `AGENTS.md`, the browser steps and the artifact upload in `.github/workflows/compose.yml`, and `tests/test_e2e_make.py`.

Worked by the Compose and CI lane session, Standard tier, no separate Engineer launch. Branch `issue-234-e2e-browser-test`, PR #243, merge commit `075df21`, head before merge `51f5d1d`. Claim: https://github.com/andrew-chung-au/socboard/issues/234#issuecomment-6890357814. QA PASS at `51f5d1d`: https://github.com/andrew-chung-au/socboard/issues/234#issuecomment-6891852328 (third launch). CI on the merge commit: compose run 43697244031 passed with 66 stack tests and 28 Playwright tests, and `users before 3, after 3`. The deliberate failure on branch `scratch-234-broken-lead`, run 43690380922, failed at the Lead's sign-in, ran the redaction step and uploaded the artifact `e2e-test-results` (three screenshots and a trace, expires 2026-11-22). I downloaded the artifacts of two failed runs and found no bearer token, token field or typed password in them.

**What I learned:** a test of an ordering has to be shown to fail for each wrong ordering, and I did not do that until the third QA launch. Two QA rounds failed on one check: first because the alerts were ingested in queue order and the titles held the severity word the check looked for, then because the Critical alert was also the oldest, so sorting by time alone gave the same queue. Running the three alerts through the real app and comparing the queue with seven wrong sorts took minutes and closed it. Even that table had one wrong row (title order: I sorted the internal keys, not the titles), which the third QA found.

## Reflection

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Orchestrator

unknown (role not asked)

## Launch usage

PM: none (the issue came groomed). QA: 3 launches (FAIL at `3a3e9c2`, FAIL at `3a5fddc`, PASS at `51f5d1d`). Active time and tool uses were not given: unknown.

## Files created or modified

- `e2e/package.json`, `e2e/bun.lock`, `e2e/bunfig.toml`, `e2e/playwright.config.ts`, `e2e/lib/stack.ts`, `e2e/tests/address.spec.ts`, `e2e/tests/journey.spec.ts`, `e2e/redact_traces.py` (new)
- `tests/test_e2e_redact.py` (new); `tests/test_e2e_make.py` (new, moved in by the human)
- `README.md` (a "Browser test" section), `.gitignore`, `.dockerignore` (one block each)
- `Makefile`, `AGENTS.md`, `.github/workflows/compose.yml` (protected, applied by the human)
- `_human-tasks/2026-11-15T0637Z-human-task-234-engineer-apply-e2e-changes-and-show-a-failure.md`
- `_docs/records/findings/234.json`, `_session-summaries/2026-11-15T0908Z-issue-234-orchestrator-e2e-browser-test.md` (this file)

## Decisions made by the human

- Labelled #234 `approved`; approved the Playwright dependency (pinned `1.65.1`, in `e2e/`).
- Applied the three protected diffs on the PR branch (`30c68d9`), after the first attempt of #229's equivalent step had been blocked by the weakened-test check; this time the make-target test was a text file, so moving it was not read as a deleted test.
- After two QA FAILs on the same criterion, chose option A: one more QA launch, limited to the last change.
- Merged PR #243.

## Mismatches with the spec or design docs

The issue body says #229's protected diffs are not applied. They were applied on `main` before this issue started (`e4b6e5a`); the claim comment says so.

## Commands to validate

- **Verify:** `make verify`. CI run 43697244125 on the merge commit passed; locally the whole Python suite passed on SQLite (2446 passed, 90 deselected) and the redaction, settings and Dockerfile tests passed after the last fix round (120).
- **E2E:** `make e2e-install` once, `cd e2e && bunx playwright install chromium` once, then `make e2e` with the stack up, its address, the ingest key and the three seed passwords in the environment (needs Docker and a browser; never run in the agent's sandbox). CI's compose job runs it.
- **Test (one file):** `make test-one FILE=tests/test_e2e_redact.py`, `make test-one FILE=tests/test_e2e_make.py`.

## Proposed AGENTS.md changes

none (the approved E2E and Layout lines are committed).

## Temporary changes

- `e2e/node_modules` was installed here to make the lockfile and to list the tests, and deleted each time. The branch `scratch-234-broken-lead` is still on the remote; the human deletes it.
- Nothing is running.

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-234-1: the wait for the ingest key's allowance has not run in CI.
- F-234-2: the loopback address rule is written twice, with no test keeping the two in step.
- F-234-3: the redactor's JSON form misses an escaped slash and raw non-ASCII text.
- F-234-4: the README's figure for failed logins before the browser test is an estimate.
- F-234-5: the queue-order check would pass for a sort by title, or by severity then asset or type, and a comment in the test says otherwise.
- F-234-6: proposal for the Engineer role file: show a must-fail test fails for each wrong implementation before handover.

## Follow-ups for the next session

- The human deletes the remote branch `scratch-234-broken-lead` (`git push origin --delete scratch-234-broken-lead`).
- D14 (#235, push the tested image): approved with its Decision record and gate; its `compose.yml` diff builds on the browser steps now on `main`.
- `_human-tasks/229-proposed/test_stack_make.py` is still a leftover copy (F-229-4).
- Still unverified: the browser test in a second run on the same stack; the bind mount with a `lost+found` folder (D17c).
