# Roadmap 1: Core

Order and status only. Acceptance criteria live on the issues; open/closed is read from the tracker. Scope and reasons: `_docs/specs.md`. Stack choice (approved): `_docs/decisions/20261105T133030Z-stack-choice.md`.

- **Status:** now
- **Goal:** A full-stack SOCBoard that ingests alerts, scores them by fixed rules, shows a live-updating queue, runs the claim→investigate→close workflow, and records an audit trail — running locally with one command.
- **Tasks, in order** (tracker issues; open or closed is read from the tracker):
  1. #7 Review and record the imported Lovable frontend base.
  2. #27 Make the frontend build static and remove Lovable coupling.
  3. #8 Complete the frontend base: mock rule enforcement, hostile fixtures, frontend tests, `make` targets.
  4. #9 OpenAPI contract (`openapi.yaml`), derived from the service layer and the spec.
  5. #10 Backend skeleton: FastAPI app, health endpoint, error shape.
  6. #11 Data model and migrations, including the one audit-writing function.
  7. #12 Rule-based severity scoring and seeded asset inventory.
  8. #13 Seeded minimal auth: two Analysts and a Lead, bearer token.
  9. #14 Ingest API with an API key.
  10. #15 Queue and case-detail read API.
  11. #16 Claim and single-owner enforcement.
  12. #17 Workflow transitions with a required closing reason.
  13. #18 Notes on a case.
  14. #19 Audit trail read API.
  15. #20 Closed-cases list for Leads.
  16. #21 Connect the frontend to the real API and add the login screen.
  17. #22 Integration tests for both journeys and the one-command `make run`.
- **Pace (human ruling, 2026-11-12):** CI is the test loop; one pull request per issue; the next two or three Core issues may be groomed ahead and approved together; one small supporting issue may run alongside the main issue while it waits. Details: `.kiro/steering/delivery-pace.md`.
- **Supporting issues, in order** (tracker issues outside the task list; each lands at its trigger, the Core issue it goes before or the event that brings it up; open or closed is read from the tracker; none changes the Core order). Every new issue is placed in this list, with a trigger, when it is filed, so that it is groomed when its trigger comes and does not wait unseen (added after the 2026-11-12 prioritization review found twelve issues outside any order):
  1. #74 Add the health route to the OpenAPI contract. After #10 closes, before #13. (Done.)
  - #86 Add the ingest field limits to the OpenAPI contract. Before #14 (#14 depends on it).
  2. #63 Make `make issue-close` ignore reflection-only Engineer comments. (Done, 2026-11-13: PR #119; Reflection comments may name commit hashes again. The Reviewer's findings are deferred to #122.) Then #73 and #71 together, in one `Makefile` sitting; sweep proposals 4 and 13 ride on it.
  3. #49 Close the weakened-test gaps for Vitest markers and test support files. Epoch batch, together with #65.
  4. #65 Make the CI weakened-test check compare a branch with its merge base. Epoch batch, together with #49. Second report of the stale-base failure (sweep 6, item 10): #54's QA saw `make verify` fail on "test files deleted" only because local `main` was behind `origin/main`, and a `git fetch` during a QA run can do the same; first raised in sweep 4, proposal 4.
  5. #62 Fix future-dated timer alerts and the order-dependent timer test. Before #21.
  6. #59 Make the dev server reachable from the browser in the dev container. Before #21.
  7. #54 Close the cheap gaps in the frontend guardrail scan. Before #21, after #62 and #59.
  8. #75 Add `make frontend-lint` and `make frontend-format`. Before #31.
  9. #31 Make `bun run lint` pass in `frontend/`. After #75 (its body gains "Depends on #75" when it is next groomed); before #21 if ready by then, otherwise after #22.
  10. #60 Protect the frontend dependency files. Any time, and before #21 at the latest.
  11. #73 Add `make issue-body`. Any time; before the next Heavy issue's second QA launch if it can.
  12. #71 Fix the `make contract-check` help and usage text. In the same sitting as #73 (both need the human's approval of a `Makefile` diff).
  13. #80 Harden `make backend-run` and `make backend-stop`. In the epoch batch (it changes what two existing commands do), so before #22.
  14. #93 Run the frontend lint in `make verify` and CI. After #75 and #31; it moves the epoch, so it joins the next epoch batch after the current one.
  15. #99 Harden the audit guard's remaining DDL and id gaps (#11's Low QA findings L1 to L5). After #11 closes, before #14 (the first issue that writes audit entries in use); proposed Heavy.
  - #102 A request body that cannot be parsed gets 500 instead of 422 (#13 follow-up). Before #14, which takes the first JSON body from outside.
  - #107 Simplify the audit guard (from #99's Reviewer and QA findings; proposed Heavy). Before Deploy (human ruling, 2026-11-13, on #19: #19 puts its route in `socboard/cases.py`, so no new route module needs a list ruling; it was "before #19", from sweep 5, because the HTTP-layer list has needed three rulings). Also feed it #99's `bind_names` test idea and QA's "compile path differs from execution" probe (sweep 5, item 10). At grooming, also add: keep the HTTP-layer module list in `tests/test_data_audit.py` in one place, because #13, #15 and later route issues each add a name (human ruling, #15). Also add #19's QA Low risk (human ruling, #19): the code search in `tests/test_audit_api.py` that no code path updates or deletes an audit entry misses aliased imports, SQL built in pieces and plain attribute assignment (the guard and triggers cover them at run time).
  - #110 Simplify the ingest route (from #14's Reviewer and QA findings; proposed Standard). Any time after #14 closes; before Deploy. At grooming, also add #18's Reviewer findings 18-1, 18-4, 18-5 and 18-7 (human ruling, #18): the redundant rollback in `add_note`, the large 401 test grid, the duplicated note reply builder, and the "read-only" docstrings. Also add #19's Reviewer finding 19-1 (human ruling, #19): the `ingested` audit entry copies the untrusted `source` field into the append-only trail, so a secret in a feed name stays there for good; write the entry without the source (the alert row keeps it). Also add #15's Reviewer findings (human ruling, #15):
    - one shared `CaseSummary` builder for ingest and the queue (15-1);
    - the repeated contract and hostile-text tests (15-2, 15-3);
    - the single-use not-found message (15-4);
    - the triple 422 explanation (15-5);
    - "no queue paging", recorded as a known limit (15-6).
  - #103 A deleted user's id can be reused, so their old token is accepted as the new user (#13 follow-up, low). Before any issue that deletes users, and before Deploy.
  - #104 Small follow-ups from #13 (missing database, seed variables, seed help text, hash bounds, secret check; low). Any time before #22; needs the human's approval of a `Makefile` and `AGENTS.md` diff. Candidate addition from #18's QA: login fields do not go through `_storable`, so a NUL may give a 500 on Postgres. (Done, 2026-11-13: worked in Claude Code on `main`; the NUL in the login username is included.)
  - #144 A login password with trailing NUL bytes is accepted as the correct password (found by #104's Engineer; low). After #104; any time before Deploy, not before #22. The human chose option A (refuse a password holding a NUL: 401, no contract or hash-format change, a one-line note on `LoginRequest.password` in `openapi.yaml`); needs grooming with that choice. It touches `socboard/passwords.py`, which #104 changed.
  - #153 Make two wall-clock-dependent tests deterministic (the mock audit order in `frontend/src/test/mock-service.test.ts` and `test_the_login_token_lasts_eight_hours`; each failed once in #104's QA runs; low). Before #22, so its `make verify` and `make run` tests do not meet a flaky test. Needs grooming.
  - #112 A retryable contract code for a claim's lock timeout (#16 follow-up). After #115 (landed), before #22 (re-timed in sweep 6, item 11: #21 closed on 2026-11-13 with both open). Groomed drafts are in `_human-tasks/groom-handover-2026-11-13/`; not applied.
  - #114 Add a `real_crash_client` test fixture (sweep 5, item 2). After #17 closes; before #22. (Done, 2026-11-13.)
  - #115 Bring `openapi.yaml` in line with the code: the 422s on `getCase` and `claimCase`, the note limit, the order notes (sweep 5, item 11). After #17, before #22 (re-timed in sweep 6, item 11: #21 closed on 2026-11-13 with it open). (Done, 2026-11-13: PR #134; closed before #112, as sweep 6 asked.)
  - #120 Remove the dead test-only `GET /api/cases` route from `tests/backend_support.py` (found by #20's QA and Engineer; the real closed-cases list shadows it). After #20 closes; before #22. Standard, small, `tests/` only; at grooming, the PM re-checks its mutation-check step (it must not edit `socboard/` in the committed change) and confirms it is independent of #114 and #110. (Done, 2026-11-13.)
  16. #100 Pin CI's Python version to the project's 3.12 (CI ran 3.14 on #11). Any time, before #22; needs the human's approval of the workflow diff.
  - #122 Make the close floor test the shape of a reflection, not a marker list (the Reviewer's findings on #63; proposed Heavy). After #63 (landed); any time before the next epoch or kit sitting, and before many more Standard or Heavy closures rely on the marker rule. Needs grooming and the human's approval of its decision record first. It touches only protected kit files, so it can share a sitting with #73 and #71. The regression test needs a separate approval of a place in `tests/`.
  - #125 Write the session summary for #20. Closed as not planned on 2026-11-13 (human approved): the Claude Code session wrote the summary itself after its usage limit reset.
  - #131 Frontend follow-ups from #21 (the real-client polling test, the unused `/users` request, QA's Low hardening items, and clearer action buttons from the human's manual run; proposed Standard). After #22; before Deploy. Any item can be dropped at grooming. Needs grooming and the human's approval first.
  - #203 Add `make test-postgres` to run the Python tests on a Postgres server (#192 follow-up, filed 2026-11-14; protected `Makefile` and `AGENTS.md`). Any time after #192 (landed); before the Postgres lane closes, so the Postgres test run has a `make` target.
  - #205 Let migrations connect with their own database URL (#193 follow-up, filed 2026-11-14; groomed 2026-11-15, unlabelled). Trigger: D20's grooming. The PM found no planned path that runs `make migrate` with the app's environment (Compose's `migrate` service gets the owner role's URL, #221), so the human ruled on 2026-11-15 to keep it open and decide then: close it as not planned if D20 migrates only through Compose's `migrate` service, otherwise build it before D20.
  - #258 Make the publish workflow test follow GitHub's trigger rules, so a workflow that cannot run on main is not forced into the gate list (#235 follow-up, filed 2026-11-16; groomed 2026-11-16, unlabelled). Trigger: the next throwaway probe branch, or the human's label. The maintainer's #156 and #207 probes could not pass the push check; the human decides how probes are handled (decision question in the PM comment).
  - #261 Pin the stack network's gateway to `10.231.77.1` in `compose.yaml`, because Docker chose `10.231.77.128` (#221 follow-up, found by the maintainer on the server on 2026-11-16; groomed 2026-11-16, unlabelled). Trigger: before #237's first run (the trusted proxy address and the Terraform README assume `10.231.77.1`). The human decides the label.
  - #271 Make the stack's project name, network prefix and trusted proxy variables in `compose.yaml` (`STACK_PROJECT`, `STACK_NET`, `STACK_TRUSTED_PROXIES`), with the defaults unchanged (#261 follow-up, asked for by the maintainer on 2026-11-16; groomed 2026-11-16, approved). After #261; before any prod issue starts (#266, #267 and #269 reuse `compose.yaml` with other values).
  - #349 Make the dev deploy's `find` end green, not red, when a second merge lands before the first commit's publish run (#238 follow-up, found on the first CI deploy, filed 2026-11-16). Trigger: before #269's first promote run, so the promote's dev records are not interleaved with red runs; any time otherwise.
  - #350 Make `scripts/ci_deploy.py check` refuse a `DEPLOY_URL` that is not the `sslip.io` form `terraform/server/` produces (#238 follow-up: a mistyped `.sslip.ioa` passed the check, filed 2026-11-16). Trigger: before `deploy-prod`'s variables are first used by #269's promote.
  - The PM's grooming drafts for #115, #112 and #122 are committed in `_human-tasks/groom-handover-2026-11-13/`, with the instructions in `_human-tasks/2026-11-13T1000Z-human-task-orchestrator-groom-handover-115-112-122.md`; nothing in them is applied yet.
  - The epoch batch (#63, #49, #65, #80, and the approved kit edits waiting for it, including #42's item 3; drafts and rulings in `_docs/planning/epoch-batch-1/README.md`) lands once, after the fifth qualifying control issue closes. #9 counts as a control issue (human ruling, 2026-11-12), so the fifth is #11 (closed 2026-11-12). Sweep 4 added items 9 to 11 (`_docs/records/2026-11-12T2107Z-measure-pm-sweep.md`). **The ponytail trial was shelved on 2026-11-12 (human ruling, after #12 closed; it can be resumed: `_docs/planning/roadmap-2-ponytail-trial.md`; `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`), so for now there are no epochs and no batch landing point. Work focuses on the Core task list.** #63, #49, #65 and #80 are ordinary supporting issues now, picked up when useful. The drafted patches in `_docs/planning/epoch-batch-1/` are ordinary process edits, each landing when the human approves its exact diff, with no need to land together. Reflection comments carried no commit hashes until #63 landed (sweep 5); they may now.

- **Not in this phase:** synthetic alert generator and Lead reassignment (Should-haves). Deploy, then DevOps (observability, alerting, on-call agent) are the next two phases, outlined in `_docs/specs.md` §6 and given their own roadmaps when Core is done. Target Enhancements (LangGraph advisory triage, n8n, MCP server) — future roadmap. See `_docs/specs.md` §6–7.
- **Archive when:** every Core issue is closed and `make run` brings up the full stack.
