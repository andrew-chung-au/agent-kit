# Issue #244: pre-drill hardening of the real runner (follow-up to #221)

**Date:** 2026-10-27
**Spec version:** not changed (no protected file touched)

## What changed and why

Engineer subagent on `claude/244-hardening`, branched from `origin/main` (#221 and #241 are merged). Fake session and fake clients only; no key, no network, no live SDK call.

- **B1 env scrub** (`envscrub.py`, `sdk_session.build_options`): confirmed in the installed `subprocess_cli.py` (lines 819-825) that the CLI environment is `{**os.environ, **options.env}`, which can override but not remove a variable. `options.env` now blanks every inherited variable that is not on a short allowlist (so all `RESPONDER_*`, database, mail, cloud credentials), then sets `ANTHROPIC_API_KEY`, `GH_TOKEN`, the git identity and credential, and the run marker. The runner's own `SubprocessGit` call also gets only allowlisted names plus the git credential.
- **B1 limit not removable:** `GH_TOKEN` and `GIT_CONFIG_VALUE_0` (the token) stay in the agent's environment because the policy lets the agent run `git push` and `gh pr create` through Bash and the SDK gives all Bash children the CLI's environment. Documented plainly and tested as a known limit. The narrowest fix (the runner pushes and opens the PR; the agent only commits) changes the agent contract: put to the owner as a question.
- **`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`:** the string exists in the bundled CLI binary, and its messages say it needs bubblewrap and a sandbox. Not tried, not relied on.
- **B1 honesty:** `_docs/responder-security-limits.md` (policy is a guardrail, not a sandbox; what bounds a hostile agent; owner decision B13 recorded: accept the residual risk for the supervised recorded drill on a throwaway demo defect, 2026-10-27, to be revisited with a container and limited egress before unattended or production use). There is no `responder/README`, so the pointer is in the `sdk_session.py` and `real_runner.py` module docstrings.
- **S1:** the runner records `responder/<fp>`'s head SHA before the session (`get_branch_sha`) and deletes only if it was absent or its SHA changed; otherwise `branch_preserved` is logged. A branch that cannot be inspected beforehand is never deleted.
- **S4:** `parse_result` anchors the URL (`(?=\s|$)`, matched at the start of the text after `PULL_REQUEST`). With a repo configured, the runner reads the PR (`get_pull_request`) and requires `head.ref == responder/<fp>` and `head.repo.full_name` equal to the configured repo; failures are `pull_request_unreadable` or `pull_request_not_this_runs`, with S1 cleanup.
- **S3:** each run gets a marker (`VT_RUN_MARKER`) in `options.env`; `procs.kill_marked_processes` SIGKILLs every process carrying it (found through `/proc/<pid>/environ`), in a `finally` before the checkout is removed and the branch deleted. Reason for the marker: the SDK starts the CLI without its own process group, so `killpg` would hit the responder. `max_budget_usd` (confirmed: the SDK passes `--max-budget-usd`) comes from `RESPONDER_MAX_BUDGET_USD`, default 3.0. The worker is a daemon thread, so an abandoned session cannot keep the interpreter alive (test runs a real subprocess).
- **S2:** `installer.SubprocessInstaller` runs `make install` in the fresh checkout before the session, with only allowlisted environment names, in its own process group, output discarded, within the run's time limit (the session gets the remaining time). A failed or overlong install is `error` (`install_failed`), no session, no branch. The policy still denies `make install`, `uv`, `npm`, `pytest` (new tests).
- **S5/S6:** `GitHubRestBranches` re-checks `responder/` plus `SAFE_ID` and quotes the fingerprint with `safe=""`; secrets (and their base64 forms, including the `x-access-token:` form) are redacted from `explanation` and `pull_request` before logging; `_run_session` logs `agent_session_failed:<ExceptionType>`.

## Findings: reproduced or not

Reproduced red first (27 new tests failing on the unchanged code): B1 (the three `RESPONDER_*` secrets and other credentials non-empty in the agent env), S1 (a pre-existing branch deleted on a failed or no-change run), S4 (`/pull/12abc`-style and prefixed text accepted; a PR number of any branch accepted), S5 (`../main` reached a URL).

Not run red first (written with their fix, because they need the new seams): S2 order, S3 ordering, kill and daemon-worker hang, S6. The hang test passes now; it was not shown to hang on the old code.

Did not reproduce as stated: none outright. Two caveats: the reviewer's S3 claim that the CLI survives cancellation is `VERIFY:` (not checkable without a live SDK; the SDK source's `close()` does terminate/kill the process on a normal context exit, but an abandoned worker thread was real). S2 "invisible to fake-SDK tests" is true, and still cannot be shown without a live run.

## Files created or modified

`responder/vt_responder/{real_runner,sdk_session,github_client,checkout,config,fakes,app}.py`; new `responder/vt_responder/{envscrub,procs,installer}.py`; new `responder/tests/{test_hardening_244,test_hardening_244_runner}.py`; adapted `responder/tests/{test_real_runner_isolation,test_background}.py`; `.env.example` (name only); `_docs/responder-security-limits.md` (new); `_docs/ai-usage-log.md`; `_docs/roadmap.md`; this summary.

## Existing tests changed (not weakened)

Tests that encoded the S1 bug (a branch that already existed before the run is deleted after a failure) now start with the branch absent and have the fake session "push" it, which is the case S1 still deletes. The `Broken` cleanup test gained `get_branch_sha`. The accepted-PR test and the background rig give the fake branch client a matching pull request, because a reported PR is now read back. `make verify` reports 0 assertion lines removed.

## Decisions made by the human

Owner decision B13 (relayed by the orchestrator, 2026-10-27): accept the residual risk for the drill; no container or egress control.

## Mismatches with the spec or design docs

none.

## Commands to validate

- **Verify:** `make verify BASE=origin/main` PASS (frontend 89, backend 561, responder 314).
- **Test (responder):** `make responder-test`.

## Proposed AGENTS.md changes

none. (Real mode needs `make` and `uv`/`npm` on the responder host for the install; `RESPONDER_MAX_BUDGET_USD` is a new optional name in `.env.example`.)

## Temporary changes

`make responder-install` and `make install` ran (git-ignored venvs and `node_modules` in this worktree). No processes left running; no system configuration changed.

## Permission review

- Read-only (propose allowing): `make issue-dump`, `git fetch`, `grep` over the installed SDK package and the bundled CLI (to read `subprocess_cli.py` and the scrub variable).
- Writes to the record (keep asking): `make responder-install` and `make install` (network, git-ignored folders); `make issue-comment` for the Engineer comment.
- Risky (propose denying): none.

## Interruptions

The orchestrator relayed the B13 decision mid-task; it was recorded in the limits note.

## Unrelated problems noticed but not fixed

- Reviewer items C1 to C9 (out of scope).
- The kill only finds processes that kept the marker; `env -i` children escape it (stated in the limits note).
- `make install` as the installer needs `uv`, `node` and `npm` on the responder host and network to PyPI and npm; its duration is unknown until the first live run.
- Allowlisted proxy variables may carry credentials.

## Follow-ups for the next session

- Owner question: have the runner (not the agent) do `git push` and open the PR, so the git token is hidden from the agent's children? Otherwise accept it as the documented limit.
- QA on #244; then the live run and the recorded drill (task 39). At the first live run, check: the marker reaches the CLI children, `--max-budget-usd` ends a run, cancellation ends the CLI, install time.
