# Issue #232: responder guard forgets a fingerprint on `resolved` (task 28c-A of #160); also the #225 sweep, CC11, the #220 split and wiring, #234, and the live US-13 check (#155, #199)

**Date:** 2026-10-26
**Spec version:** 76c73f7

## What changed and why

The owner asked for the highest-value human verification chunk, then asked why the agent could not do it, then asked for the next task the agent could do alone, then asked to be walked through the Docker-host verification step by step. Pieces of work followed (the last two bullets below are the later ones).

- **#225 close-out sweep, done by the agent.** The Actions record was checked through the GitHub tools (telemetry log "3 passed in 61.07s" in run 40291587781, runs 40188742150, the two T-REFUSE negative checks 40073386642 and 40073409867, alert run 40226288166, dev deploy run 40291937292 for the image digests, and the `skipif` pair in `tests/test_compose_alert.py`). #157, #174 and #141 were closed with the evidence on each. #172 was closed after a QA re-check passed (6411988890). #225 itself is not ticked or closed.
- **CC11.** Juice Shop commits no `package-lock.json`; NodeGoat commits one at `lockfileVersion` 2 with a `packages` key, which the parser accepts. `deploy/pilot-seed.json` now lists NodeGoat only (plus the two `REPLACE_ME` entries that are the owner's). Read from github.com and the first lines of the raw file; the file was not run through the parser.
- **#220 grooming and split.** The PM groomed #220 (comment 6412133802) and recommended three issues; the owner chose that. Created #232 (this issue) and #233 (`P-DEMO-BE`, run twice), both under #160, and narrowed #220 to the Compose wiring.
- **#232.** The repeat-fingerprint guard now forgets a fingerprint when its alert resolves. A `resolved` that arrives while a run is in flight defers the release until the run finishes; a firing that arrives after the deferred resolved cancels the deferred release; a run that errors or raises still releases. QA PASS (6412775111).

- **#234 (follow-up to #232), same session.** QA's risk that no test made the runner raise became #234, narrowed at the owner's request to the raise-path test only; the `_save()` failure modes and restart loss became future-development item X12 in `_docs/roadmap-future.md`. Engineer `6f4792b` added `test_hook_run_that_raises_releases_the_fingerprint_and_clears_in_flight` (the webhook answers 500, the fingerprint is released, in-flight is cleared, a later firing runs). Mutation check done twice (the Engineer in place, QA on a copy): removing the `finally` makes it fail. QA PASS (6413284562), assert clean PASS. Pull request: https://github.com/andrew-chung-au/vuln-triage/pull/235.

- **#220 (Compose wiring), same session.** Engineer commits `d53438f`, `b97f714`, `ea3eee8`, `91b61a4`: `compose.responder.yaml` (no new image: built from `./backend` with the source bind-mounted), the `responder` branch of `ci/test-compose.sh`, a static compose-file test, eight `compose`-marked cases (written, NOT run: no Docker here) and the `tasks.md` 28/29 wording. QA (6413501579): the [V] criteria PASS (static checker mutated on a copy: all 10 mutations caught), the [D] criteria UNVERIFIED. Decision point (owner, 2026-10-26): the real-Grafana-body criterion is amended to a `claimed` backdated job; a one-line comment fix in the protected `Makefile` was approved and committed as `5173c20` (record on #220, comment 6413563367); QA's two test-quality risks parked as X13. **Update:** the owner ran `make test-compose JOB=responder` on a Docker host (WSL on Windows, Docker 29.8.2, Compose v5.6.0): **8 passed in 103 s** (2m28s wall clock, warm cache); recorded and #220 closed (comment 6415509715). The first attempt failed only on a local port clash (VS Code, `Code.exe`, listened on host port 9099); found with `netstat.exe` and `tasklist.exe` from WSL, cleared by closing VS Code, and documented in the README (Option B) and `verify-locally.md` Troubleshooting.
- **The live US-13 stack check (#155, #199), run by the owner on 2026-10-26, walked through step by step.** Results are in #226 (comments 6417013401 and 6417309808): six services healthy, `make demo` with the OTLP and mail settings passed explicitly, data in the metric, trace and log panels, a 7-span `scan.run` trace joined to its `notification.deliver` log line by trace id, one owner email in MailHog, the US-14 rule Provisioned and Normal. An older demo instance in the owner's original checkout (processes on 5173 and 8000) was stopped with `make dev-stop` there, and this folder's own database was reset with `make demo-reset` (the verification clone is throwaway). **A finding the agent got wrong first:** the agent told the owner the Environment and Version filters "work" because the panels stayed populated; reading the dashboard JSON showed the two variables are defined but referenced by no panel query, and the metric has neither label, so they filtered nothing. Corrected on #226, #155 and #199. **Owner decision: drop the variables (option 2)**; making them work is X14. The Engineer removed them (`b574494`, checked statically only; the dashboard has not been loaded live since). QA took five passes on #199: the code and dashboard passed every time, and the failures were record defects (a stale pending note, unsupported claims in the G9 row, a removed section leaving stale pointers), all fixed; PASS on the fifth (6417556909). #155 closed on QA PASS (6417378357).
- **Screenshots (G9).** Three images the owner took (`g9-grafana-dashboard-dev-local.png`, `g9-grafana-trace-scan-loki-expandedlog.png`, `g9-grafana-tempo-trace.png`) were committed by the owner (`b093eb9`) after a mix-up over which checkout held them; the agent read each image, linked them in the README under "Observability evidence" with captions QA checked, and removed the two older placeholders. The agent had the line colours reversed in its first #226 comment (held is green, sent is yellow); corrected in a new comment. `_docs/rubric-evidence.md` was not edited (it belongs to the `rubric-auditor`).

## Files created or modified

- Responder: `responder/vt_responder/guard.py` (`resolve`, `finish`, in-memory in-flight and deferred sets), `responder/vt_responder/app.py` (resolved calls `guard.resolve`; the run is wrapped in try/finally calling `guard.finish`), `responder/tests/test_webhook.py` (new cases).
- Compose wiring (#220): `compose.responder.yaml` (new), `ci/test-compose.sh`, `tests/compose_responder.py` and `tests/test_compose_responder.py` and `tests/test_compose_responder_static.py` (new cases).
- Dashboard: `observability/grafana/dashboards/us13-journey.json` (the two template variables removed), `observability/README.md`, `tests/test_us13_dashboard.py` (a comment only).
- Docs: `_docs/testing.md`, `_docs/tasks.md`, `_docs/pending-verification.md`, `_docs/human-tasklist.md`, `_docs/cloud-tasklist.md`, `_docs/aws-setup.md` (A13 step 2), `_docs/verify-locally.md`, `_docs/roadmap.md`, `_docs/roadmap-future.md` (X12, X13, X14), `README.md` (a Docker port-clash note and "Observability evidence"), `_docs/ai-usage-log.md`, this summary.
- Images: three added, two removed under `docs/images/`.
- Deploy: `deploy/pilot-seed.json`.
- GitHub, outside the diff: comments and closes on #157, #174, #141, #172, #232, #234, #220 and #155; created #232, #233 and #234; rewrote the bodies of #220, #155 and #199; result comments on #226. #199 stays open until the owner or the next step closes it.
- Protected: `Makefile` (a comment only, `5173c20`, with the owner's approval).

## Decisions made by the human

- Asked the agent to run the #225 sweep itself, and to do the #172 QA re-check and the doc tidy (2026-10-26).
- Asked the agent to do the next task without them; accepted both the #220 draft and CC11.
- Chose option 1 of the PM's split question: three issues (#232, a narrowed #220, #233).
- Not asked, and so not decided: the PM's point that a second Compose service built from the existing backend Dockerfile is not a "new image". The PM's default stands unless the owner objects; this was stated in the question and on #220. (The owner's green responder run used that design.)
- At the #220 decision point: amend the real-Grafana-body criterion to a `claimed` backdated job; approve the one-line protected `Makefile` comment change; park QA's two test-quality risks as X13.
- Asked for a step-by-step walkthrough of the Docker-host verification, with the agent doing whatever it could itself; asked whether to document or change the port clash (decided: document, keep the port) and for the note to be more prominent in the README.
- Filters: chose option 2, drop the dashboard's Environment and Version filters; option 1 (make them work) is future development X14.
- Asked the agent to submit the PR, then said they could not see it. **The agent had wrongly reported PR #235 as open and ready for review for several turns: the owner had merged it at 11:05 UTC (head `2a805e0`), and the agent had not re-checked its state.** The agent then found 14 commits on the branch that were not in `main`, merged `main` into the branch (no force-push) and opened PR #236 with only that work; the description of the merged PR #235 was corrected.

## Mismatches with the spec or design docs

none new. Earlier ones still open: `architecture.md` A34 and `roadmap.md` S4/C6 still describe the responder runtime as open (F2 settled it); `_docs/tasks.md` tasks 28/29 both claim the `responder` CI job (#220 is to align the wording).

## Commands to validate

- **Verify:** `make verify` (PASS at the last push, `e0f532c`: frontend 89, backend 532, responder 77).
- **Test (responder):** `make responder-test` (77 passed).
- **Compose responder job (owner's Docker host, not run by an agent):** `make test-compose JOB=responder` (8 passed in 103 s).

## Proposed AGENTS.md changes

none.

## Temporary changes

- `make install` ran in this session (the `responder/.venv` was missing, so `make verify` failed until it was installed). It installs from the lockfiles into git-ignored directories (`frontend/node_modules`, `backend/.venv`, `responder/.venv`); left in place.
- No processes were started by the agent and no system configuration was changed by it. `.scratch/` was emptied with `make clean-scratch` after each issue; the QA runs left files in `.scratch/` that are git-ignored.
- On the owner's machine (not the agent's): a verification clone `~/projects/vuln-triage/vuln-triage-verify`, a throwaway `.env` there, the observability stack and demo (both torn down by the owner at the end of the sitting), and the owner's stopped older demo in the original checkout (`make dev-stop`; its database was kept). The owner closed VS Code to free port 9099 and was advised to untick `remote.autoForwardPorts`; whether they did was not recorded.

## Permission review

- Read-only (propose allowing): none of the role comments reported an approval. The orchestrator's `make install` (network; installs into git-ignored directories; no matched `ask` rule recorded).
- Writes to the record (keep asking): GitHub issue comments, issue creation, the #220 body edit and issue closes through the GitHub tools; `make issue-comment` posts by the PM, Engineer and QA roles; `git push -u origin claude/funny-dijkstra-svm6xw` (cloud session branch, several pushes); `HUMAN_APPROVED=1 git commit` for the protected `Makefile` comment change `5173c20` (matched `ask` rule, owner approved the exact diff; record on #220, comment 6413563367); opening PRs #235 and #236 and editing their descriptions; merging `main` into the session branch (a merge commit, no force-push).
- Risky (propose denying): none. A web-fetch subagent read public GitHub pages for CC11 (no approval requested). The PM's report notes it used `cat backend/Dockerfile` for a file read (a convention slip, no approval needed). One QA subagent ran `git show --output=.scratch/...` twice to try to extract deleted images; the output went to the terminal and nothing changed.
- Role comments without an approvals line: the PM's #220 comment states "none"; the #232 Engineer comment and the #232 and #172 QA comments state "none". The CC11 fetch had no comment. The #234, #220 and #199 Engineer and QA comments all state none needed.

## Interruptions

- The container was restarted mid-session and the GitHub tool server disconnected and reconnected several times. The PM's finished report was recovered from its hand-back message and from `.scratch/pm-220-groomed.md` (still present). The owner also hit a usage limit once, mid-turn. Nothing was left half-done: no commit or issue was in a partial state.
- Pre-push runs of `make verify` were deliberately held a few times while an Engineer had uncommitted edits in the tree (the mutation checks and the dashboard edit), so the hook would not run on a half-edited state; every push went out after the tree was clean.

## Unrelated problems noticed but not fixed

QA's risks on #232, none changing its verdict:
- No test makes `runner.run` raise, so the new try/finally release is untested (removing the `finally` would leave every test green).
- If `_save()` raises inside `claim`, the fingerprint stays in memory as in flight and a later resolved defers forever until a restart.
- If `_save()` raises inside `finish`, the exception replaces the run result.
- The in-flight and deferred state is in memory only, so a restart mid-run drops a pending release (relevant to #221).
- `compose.yaml` does not pass `VT_DEMO_DEFECT` through; #220's criteria add it.
- Flake #185 (Tempo drops leading zeros in trace ids) can fail `T-JOURNEY-BE` about 1 run in 16.

A process lapse by the agent: after PR #235 was merged it kept pushing commits to the branch and told the owner the PR was open and ready, without re-reading the PR's state, so the post-merge work (the dashboard change, the screenshots, the records for #199 and #155, which were already closed on GitHub) was not in `main` until PR #236. Re-read the PR's state before saying it is open.

Noticed later in the session:
- #220: the static compose checker does not parse a list-form `environment:`; the test-notification case snapshots the `no_change` count (both X13).
- The alert annotations in `us14-overdue.yaml` read `deployment_environment` and `service_version` labels, which `vt_notifications_total` does not carry, so they are empty today (X14). The Loki log event does carry both as fields.
- `make demo` alone does not send mail to MailHog: the mail transport and SMTP host had to be passed explicitly. The README's reviewer path does not need it.
- `_docs/rubric-evidence.md` is a dated 2026-10-25 snapshot and does not reflect the new Observability evidence; a rubric re-audit is the way to credit it.
- Minor stale text QA found and left: `tests/test_compose_alert.py` line 34 points at a removed `pending-verification.md` section; the cloud tasklist's "Last updated" and "Suggested order" are old.

## Follow-ups for the next session

- **#233 (`P-DEMO-BE`)** is unblocked: #232 and #220 are green in recorded runs. It needs a Docker host again to prove.
- **#199** is closed on QA PASS (record the close on the issue); confirm on the next live run that the dashboard's two dropdowns are gone and the three panels are unchanged.
- **Rubric re-audit** (`rubric-auditor`) so `_docs/rubric-evidence.md` reflects the Observability screenshots, the responder job run and the closed issues.
- X12 (guard failure modes), X13 (two #220 test-quality risks) and X14 (working dashboard filters, plus the alert annotation labels) are parked in `_docs/roadmap-future.md`.
- #225 is left for the owner to tick and close. #229 (owner decisions) and #222 (token) are unchanged. The optional G10 alert-firing screenshot and the held-job Loki case were skipped.
- The owner reviews and merges PR #236 (PR #235 was already merged at head `2a805e0`).
