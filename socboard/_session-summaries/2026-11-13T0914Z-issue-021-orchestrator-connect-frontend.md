# Issue #21: Connect the frontend to the real API and add the login screen

**Date:** 2026-11-13T09:14Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (no tier label; the PM's proposal). Kiro Web worked #21 on branch `issue-21-connect-frontend` (PR #128, merged at head 203f4e3, merge commit 9356ee3). Ponytail was on for the Engineer. The human chose to start #21 as soon as every issue named in its "Depends on" line was closed; #115 and #112, which the roadmap placed before it, were left for after. This summary is on its own branch because the human merged #128 before it could be added to that branch.

- **What already existed:** the Lovable import had the HTTP client (`httpService.ts`, `http.ts`), the session store (memory plus session storage), a login screen and a config with `VITE_USE_MOCK`, `VITE_API_BASE_URL`, `VITE_POLL_INTERVAL_MS` and `VITE_FEATURE_REASSIGN`. The work was closing gaps and proving them.
- **Added:**
  - the dev proxy of `/api` to 127.0.0.1:8000 in `frontend/vite.config.ts`;
  - `frontend/src/test/contract-paths.test.ts`, which fails if a service call is not in `openapi.yaml` (it reads the contract as text, because no YAML parser is installed and dependencies need approval);
  - `frontend/src/test/real-client.test.tsx` (14 tests): 401, wrong password, good login, 403/409/422 each followed by a case re-read, polling, and role hiding;
  - the Closed link, the closed view and the audit trail are Lead-only and are never requested for an Analyst (before this, an Analyst would have hit 403s);
  - README notes on the proxy, the command form for the real backend, and where the token is kept (memory plus session storage, never local storage, never logged).
- **Reviewer findings applied (as the human approved):**
  - finding 1: an Analyst's back link on a closed case goes to the queue, not the Lead-only page;
  - finding 2: no "Only a Lead" flash while the session loads (`closed.tsx` waits for `hydrated`; the case page waits too);
  - finding 3: the query cache is cleared when the session ends (`clearCacheOnLogout` in `router.tsx`);
  - plus the README command line. Findings 4 (the polling test skips the real client) and 5 (a Lead's case page requests `/users` while reassign is hidden) were deferred.
- **CI:** PR run 43390363913 at 9e2af7e (first) and 43394132363 at 203f4e3 (after the fixes): both success. At 203f4e3: 1508 Python tests, 208 frontend tests (`real-client.test.tsx` 14), `VERIFY: PASS`. The frontend packages could not be installed in Kiro Web (the npm registry answered 403), so CI was the first run of every new test, and it passed first time.
- **QA:** PASS at 9e2af7e (criteria 1 to 7), then PASS at 203f4e3 for the fix round. QA reproduced the contract-paths logic in bun and mutated it six ways; each was caught. Criterion 8 was NOT CHECKED in both runs.
- **Criterion 8, the manual journey against the real backend:** not run in Kiro Web (no database, no browser). The orchestrator rewrote the Engineer's task file with copy-paste commands and expected output, each checked against the code. QA found three wording slips in it (ingest-key timing, the polling step not exercising polling, the audit order), which are corrected in this change. The human ran the journey in the dev container at 203f4e3 (confirmed with `git log`), against the real backend with the mock off. Results: Analyst steps 6.1 to 6.5 pass (queue order, claim to Ana Alvarez, Investigating, a note, close with a reason); 6.6 passes (no Closed item in the top bar, no Audit panel, and the back link on the closed case reads "← Queue"); 6.7 passes (the token is in Session storage); Step 7 passes (the Lead sees the Closed link and the closed case with its reason "False positive", and the Audit trail in time order: ingested, claimed, note_added, status_changed to Investigating, status_changed to Closed (false_positive)); Step 9 passes (restarting the backend with a different secret returned the browser to Sign in); Step 10 passes. Step 8 passes (the human confirmed the wrong-password message, that it stays on Sign in, and that nothing crashes). The Local storage and polling-by-third-alert checks were not reported. The note typed in Step 6 was "this is mine", not the hostile text, so literal rendering was covered by the automated hostile-text tests and QA's probes, not by hand.

**What I learned:** an issue groomed before its backend existed is mostly verification. Reading each criterion against the code first showed that most were already met, so the Engineer's job was to find the real gaps (the Lead-only views, the proxy, the contract-path test) instead of rebuilding. A merge before the summary and the manual result cost a second small PR.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

### Ponytail

The Engineer kept to existing files and added no dependency or helper beyond one small function in `router.tsx`. The Reviewer found no Must fix and one real defect the change itself caused (the dead-end back link), which was applied.

## Launch usage

Active time and tool uses: unknown, because Kiro Web reports neither. Launches: Engineer 2 (implementation, then the approved fixes); QA 2 (PASS, then a PASS on the changed parts); Reviewer 1; PM 1 (grooming #115, #112 and #122 ahead, parked).

## Files created or modified

- `frontend/vite.config.ts`, `frontend/src/components/soc/AppShell.tsx`, `frontend/src/routes/closed.tsx`, `frontend/src/routes/cases.$id.tsx`, `frontend/src/router.tsx`
- `frontend/src/test/contract-paths.test.ts` (new), `frontend/src/test/real-client.test.tsx` (new)
- `README.md`, `frontend/README.md`
- `_human-tasks/2026-11-13T0802Z-human-task-021-engineer-manual-journey-real-backend.md` (new, then rewritten and corrected)
- this file

No protected file, `Makefile`, `AGENTS.md`, `openapi.yaml`, `socboard/` or `tests/` file was touched, and no dependency was added.

## Decisions made by the human

- Start #21 now, with only its listed dependencies as blockers; groom #115, #112 and #122 elsewhere without blocking it.
- At the decision point: apply Reviewer findings 1, 2 and 3 and the README line; defer 4 and 5.
- Run the manual journey in the dev container against the current head.
- Merged #128 at head 203f4e3.

## Mismatches with the spec or design docs

- The Engineer's report said the contract's "Differences from the mock" list omits the Analyst-audit difference. QA found it is covered (`openapi.yaml`, item 14). The mock still lets an Analyst read the audit trail and a Lead be a reassign target; the contract does not. The mock was not aligned.
- `make frontend-start` help text and `AGENTS.md` say "mock on", which is now only the default. Both are protected and need a `Makefile` and `AGENTS.md` sitting.

## Commands to validate

- **Verify:** `make verify` (CI on PR #128: pass at 203f4e3).
- **Frontend test:** `make frontend-test`.
- **Manual journey:** `_human-tasks/2026-11-13T0802Z-human-task-021-engineer-manual-journey-real-backend.md`.

## Proposed AGENTS.md changes

The "mock on" wording in the **Frontend dev server** line, with the matching `Makefile` help text, once the human wants a protected-file sitting. No other change.

## Temporary changes

none. `make clean-scratch` has not yet run for this issue; it waits for the PM's grooming drafts to be handed over.

## Interruptions

none. One Engineer run used two parallel git calls and amended its own unpushed commit; the history was checked and CI passed.

## Unrelated problems noticed but not fixed

- QA Low items: a non-JSON 200 becomes `null`; a late 401 from an old request can clear a newer session; the proxy port is fixed at 8000; no "session expired" message on the sign-in page; `VITE_FEATURE_REASSIGN=true` with the mock off would show a Reassign control with no backend route.
- The reassign route does not exist in the backend yet.
- The secret scanner refuses the text of an env-file name in an issue comment, even when a QA verdict says the task file names none; one phrase was reworded to post the verdict.

## Follow-ups for the next session

1. Close #21 with `make issue-close N=21` once this summary is merged (the manual journey is recorded above and passes).
1a. UI feedback from the manual run, for a later UI issue (not part of the Core submission): show every action button on a case (Claim, Start investigating, Close case…) with the unavailable ones greyed out, instead of revealing Close case only after Start investigating, so a new user can see the whole flow. This sits close to the Lovable guardrail that the client does not decide what is allowed, so the server stays the authority. The "← Queue" back link also reads as a button to a user; it could look more like a link or a button, consistently.
2. Reviewer findings 4 and 5 and the QA Low items: one small follow-up issue if the human wants it.
3. #115 and #112 (contract sync and lock-timeout code): PM drafts exist in this sandbox; hand them over or groom them in another session.
4. #125 may be redundant now that the Claude Code session wrote #20's summary; ask the human whether to close it as not planned.
5. A sweep is due (`make sweep-due`).
