# Proposal: the `responder` CI job and `P-FLAG-GONE` (#161, task 29; protected `.github/` files, needs the owner's approval)

Reading the diffs: blank context lines are written as empty lines (not a single space) so this file passes the whitespace check; `patch` and `git apply` accept that.

Status: **draft, not applied.** Nothing under `.github/`, no `Makefile`, `AGENTS.md`, spec or `agent-kit.conf` is changed by this branch. The two non-protected files the proposal needs (the check script and its tests) are committed on branch `claude/161-responder-job-draft`. Everything protected is written below as an exact diff. Format follows `_docs/make-demo-proposal.md`.

What was validated, and what was not: the proposed YAML was **parsed** (PyYAML, `.scratch/validate_proposal.py`), the `run` block and the proposed `ci/test-compose.sh` were syntax-checked with `bash -n`, and the `P-FLAG-GONE` step's shell text was run locally against this repository with a made-up image tag. **That is all.** GitHub Actions, Docker and the Compose job were not run; the `responder` job has never run in CI, and the new `deploy-prod` step has never run in Actions.

## 0. Findings that shape the proposal

1. **`.github/` is not in `PROTECTED` in `agent-kit.conf`.** The project treats it as protected anyway (`human-tasklist.md` B3 and C2; the #159 precedent `4ba7e52`), but the commit hook will not ask for `HUMAN_APPROVED=1`, and the approval-record rules say "every path matches `PROTECTED`". See open question 4.
2. **A job cannot be nightly inside `verify.yml`.** `on:` is per workflow, and `verify.yml` has `on: [push, pull_request]`. The #159 answer was a separate `alert.yml` (nightly plus `workflow_dispatch`). The same split is proposed here.
3. **The alert job has no teardown or log-upload step.** `ci/test-compose.sh` tears the project down in an `EXIT` trap, so by the time a later `if: failure()` step runs, the containers and their logs are gone. A log upload is only useful with a small change to that script (section 1.4).
4. **The 8 cases from #220 already passed on the owner's host** (`8 passed in 103 s`, comment 6415509715 on #220). What has not run anywhere is #233's `P-DEMO-BE` loop (two takes, about 8 to 10 minutes each, about 20 in all; branch `claude/233-p-demo-be`, not on `origin`).
5. **`P-FLAG-GONE` cannot be "the string is absent" for `VT_FEEDS=fixtures`.** The flag legitimately appears in `compose.telemetry.yaml`, the `Makefile` demo, the tests and the docs, and `feeds.py` ships in every image. Section 2 states the rule used instead.
6. **The demo-defect cleanup is bigger than one source file.** Running the new script on `main` today gives 78 findings in 13 files (section 2.5), including the container-form tests of the `responder` job itself. After the cleanup those cases cannot pass, so the job's contents change then (open question 6).

## 1. The `responder` job

### 1.1 Cadence: nightly plus `workflow_dispatch`, in its own file

Recommended: **nightly (17:30 UTC) and on demand, in a new `.github/workflows/responder.yml`, not on push or pull request.** Both at once is not possible without running the job twice (it would have to be defined in two workflows).

Why not every PR:

- Cost. #233's case runs the full stub loop twice, about 8 to 10 minutes per take and about 20 in all (measured on the owner's host; **not yet measured in CI**). A cold CI run also builds the backend image and waits for the Prometheus heartbeat (up to 300 s in `wait_for_heartbeat`). `verify.yml` runs on `push` and `pull_request`, so one PR commit would pay it twice.
- Flakiness. The alert job ran about 30 minutes and was flaky on Grafana's own timing before it was moved off the PR path (`testing.md`, "Where each case runs"). The responder job reuses the same Grafana path (the real alert fires and Grafana posts to the responder), so it inherits that timing.
- The PR gate is unaffected either way for correctness: the unit and SQLite cases (`I-RESP-*`, the responder pytest suite, `test_demo_defect.py`) already run in `verify.yml` through `make test`.

Cost of nightly: a regression is seen up to a day later, not on the PR. The mitigation is `workflow_dispatch` (Actions, responder, Run workflow) before merging anything that touches `compose*.yaml`, `responder/` or `ci/test-compose.sh`.

The literal alternative (a job in `verify.yml`, every push and PR) is in section 1.5 so the owner can pick it.

### 1.2 `timeout-minutes: 45`

The cases take about 20 minutes (two takes at 8 to 10), plus an uncached image build and the up to 5-minute heartbeat wait: about 30 minutes worst case on the numbers we have. 45 keeps headroom for a slow runner. Without the line GitHub allows 6 hours, so a hung run would hold a runner that long.

**This number is a guess and must be re-sized after the owner's first recorded run in CI:** set it to about twice the observed time, rounded up to 5. A first run that hits 45 is a signal to look at the log, not to raise the limit blindly.

### 1.3 Steps: copied versus new

| Step | Source |
|---|---|
| `actions/checkout@v4` | copied from `alert.yml` (identical) |
| `actions/setup-python@v5`, Python 3.12 | copied (identical) |
| `astral-sh/setup-uv@v5`, uv 0.13.1 | copied (identical) |
| `make backend-install` | copied (identical) |
| `make test-compose JOB=responder` | copied; only the `JOB` value differs |
| `name`, `on:` (`schedule`, `workflow_dispatch`), `permissions: contents: read` | copied from `alert.yml`; the cron is 30 minutes after the alert job's so the two do not start together (they run on separate runners, so this is cosmetic) |
| `timeout-minutes: 45` | **new** (the alert job has none) |
| "Upload the Compose logs of a failed run" (`actions/upload-artifact@v4`, `if: failure()`) | **new** (the alert job has none) |
| Teardown | **not a step**: `ci/test-compose.sh` does it in its `EXIT` trap, as for the alert job |

The upload step uses `if-no-files-found: ignore`, so the workflow is safe to apply before the `ci/test-compose.sh` hunk in 1.4: it uploads nothing. `VERIFY:` that `actions/upload-artifact@v4` is still the current major version.

### 1.4 `ci/test-compose.sh`: keep the logs of a failed CI run (optional, NOT protected)

`ci/` is not protected, but the `responder` branch of this script belongs to #220 (merged) and #233 is editing the same file on `claude/233-p-demo-be`. **Apply this only after #233 merges**, as an ordinary commit, to avoid a conflict. It saves the stack's logs only when the script fails under CI (`CI` is set by Actions), before the `down` that destroys them:

```diff
--- a/ci/test-compose.sh
+++ b/ci/test-compose.sh
@@ -80,6 +80,13 @@ export VT_BACKEND_URL="http://localhost:8000"
 export VT_COMPOSE_POLL_TIMEOUT="${VT_COMPOSE_POLL_TIMEOUT:-150}"

 cleanup() {
+  local rc=$?
+  # In CI, keep the stack's logs from a failed run before the project (and its
+  # logs) is removed; the workflow uploads .scratch/compose-logs-*.txt on failure.
+  if [ "$rc" -ne 0 ] && [ -n "${CI:-}" ]; then
+    mkdir -p .scratch
+    "${COMPOSE[@]}" logs --no-color --timestamps >".scratch/compose-logs-${PROJECT}.txt" 2>&1 || true
+  fi
   "${COMPOSE[@]}" down --volumes --remove-orphans >/dev/null 2>&1 || true
 }
 trap cleanup EXIT
```

The file name uses `PROJECT`, which is `vt-responder` for this job, matching the `path:` in the workflow. Syntax-checked with `bash -n` only; not run.

### 1.5 Diffs

**New file `.github/workflows/responder.yml`** (recommended):

```diff
--- /dev/null
+++ b/.github/workflows/responder.yml
@@ -0,0 +1,49 @@
+name: responder
+# The US-15 responder Compose job (issue #161, task 29): the real Grafana alert
+# reaches the responder (stub mode), and the P-DEMO-BE loop runs twice (the cases
+# in tests/test_compose_responder.py: P-DEMO-BE, P-PROD-REFUSAL, the Grafana body
+# shape, the 401 cases). It takes about 8 to 10 minutes per take and about 20 in
+# all, so it runs nightly and on demand (Actions -> responder -> Run workflow),
+# not on every push/PR, the same split as the alert job (alert.yml, human decision
+# 2026-10-25). The pull-request gate is the unit and SQLite cases in verify.yml.
+on:
+  schedule:
+    - cron: "30 17 * * *" # 17:30 UTC daily, after the alert job (17:00)
+  workflow_dispatch:
+
+# No secret or live feed: the stack is local, with throwaway env set in
+# ci/test-compose.sh (RESPONDER_MODE=stub, no model key, no GitHub token). A
+# read-only token is all CI gets.
+permissions:
+  contents: read
+
+jobs:
+  # The app + observability + responder stack (compose.yaml + compose.telemetry.yaml
+  # + compose.alert.yaml + compose.responder.yaml). ubuntu-latest ships Docker +
+  # Docker Compose.
+  responder:
+    runs-on: ubuntu-latest
+    # About 20 minutes of cases plus the image builds and the heartbeat wait. NOT
+    # yet measured in CI (the 8 to 10 minutes per take were measured on the
+    # owner's host, #233). Re-size after the first recorded run to about twice the
+    # observed time. Without this line a hung run holds a runner for 6 hours.
+    timeout-minutes: 45
+    steps:
+      - uses: actions/checkout@v4
+      - uses: actions/setup-python@v5
+        with: { python-version: "3.12" }
+      - uses: astral-sh/setup-uv@v5
+        with: { version: "0.13.1" }
+      - run: make backend-install
+      - run: make test-compose JOB=responder
+      # ci/test-compose.sh removes the Compose project on exit, so on a failure it
+      # first saves the stack's logs to this file (the ci/test-compose.sh hunk in
+      # the proposal). Without that hunk there is nothing to upload.
+      - name: Upload the Compose logs of a failed run
+        if: failure()
+        uses: actions/upload-artifact@v4
+        with:
+          name: responder-compose-logs
+          path: .scratch/compose-logs-vt-responder.txt
+          if-no-files-found: ignore
+          retention-days: 7
```

**`.github/workflows/verify.yml`** (a pointer comment only, as #159 left for the alert job; the parsed YAML is identical before and after):

```diff
--- a/.github/workflows/verify.yml
+++ b/.github/workflows/verify.yml
@@ -89,6 +89,10 @@ jobs:
   # The alert Compose job (#159) is in alert.yml: it runs nightly and on demand,
   # not on every push/PR (human decision, 2026-10-25).

+  # The responder Compose job (#161) is in responder.yml for the same reason: it
+  # runs the full stub loop twice (about 20 minutes), so it runs nightly and on
+  # demand, not on every push/PR.
+
   # The full gate, kept so PRs still get the whitespace and weakened-test checks
   # that the split test jobs above do not cover; it also runs the suite as a
   # backstop. Needs both toolchains because make verify runs make test (frontend
```

**Alternative, if the owner wants it on every push and PR: instead of the two diffs above, apply only this to `verify.yml`** (the job body is the same steps; the comment is shorter):

```diff
--- a/.github/workflows/verify.yml
+++ b/.github/workflows/verify.yml
@@ -89,6 +89,29 @@ jobs:
   # The alert Compose job (#159) is in alert.yml: it runs nightly and on demand,
   # not on every push/PR (human decision, 2026-10-25).

+  # The responder Compose job (#161): the real Grafana alert reaches the responder
+  # (stub mode) and the P-DEMO-BE loop runs twice, about 20 minutes in all (NOT yet
+  # measured in CI). ubuntu-latest ships Docker + Docker Compose.
+  responder:
+    runs-on: ubuntu-latest
+    timeout-minutes: 45 # re-size after the first recorded run
+    steps:
+      - uses: actions/checkout@v4
+      - uses: actions/setup-python@v5
+        with: { python-version: "3.12" }
+      - uses: astral-sh/setup-uv@v5
+        with: { version: "0.13.1" }
+      - run: make backend-install
+      - run: make test-compose JOB=responder
+      - name: Upload the Compose logs of a failed run
+        if: failure()
+        uses: actions/upload-artifact@v4
+        with:
+          name: responder-compose-logs
+          path: .scratch/compose-logs-vt-responder.txt
+          if-no-files-found: ignore
+          retention-days: 7
+
   # The full gate, kept so PRs still get the whitespace and weakened-test checks
   # that the split test jobs above do not cover; it also runs the suite as a
   # backstop. Needs both toolchains because make verify runs make test (frontend
```

Cost of the alternative: roughly 20 to 30 extra minutes per push and per PR update, on a Grafana-timing-dependent job, and the Actions page would show a red PR whenever Grafana is slow. The `testing.md` job table row for `responder` (currently "`ubuntu-latest` with Compose", no cadence) would then stay as it is; for the recommended option it should gain "nightly and on demand, not on push/PR", as the `alert` row did (a docs edit, not protected).

## 2. `P-FLAG-GONE`

### 2.1 Design, from #161, `testing.md` § Responder and the #172 re-scope

One yes/no check, run **only** in the production promotion, before the deploy. It is not in `make test-compose`, not in any pull-request job, so the PR gate stays green while the demo defect exists. Its own correctness is tested under `make test` against two fixture trees.

Two rules, in `ci/check_flag_gone.py` (standard library only; exit 0 pass, 1 fail, 2 bad usage):

1. **demo-defect.** No tracked non-documentation file, and no file name, anywhere in the tree contains `VT_DEMO_DEFECT`, any `demo_defect` / `DemoDefect` identifier, or the `notify_no_fix` token. The token match does not hit `notify_no_fixed_version` (the responder's intended test file name, a different thing).
2. **fixtures-flag** (re-scoped from #172, note 6410199234). `feeds.py` ships in every image by design, so the rule targets the flag/value and its fail-closed gate, not the module:
   - a. no production artifact (`compose.yaml`, `.env.example`, any `Dockerfile*`, anything under `terraform/`) sets `VT_FEEDS` to `fixtures` on a non-comment line; and
   - b. the gate still exists: `require_feeds_allowed` is defined in `backend/vulntriage/ingest/settings.py` and called in `backend/vulntriage/main.py`.

   `compose.telemetry.yaml` (test-only override), the `Makefile` demo and the tests may set `VT_FEEDS=fixtures`; that is the design. `VERIFY:` this reading is the owner's call in #229 (open question 5).

Not scanned: `*.md`, `_docs/`, `_session-summaries/` (documentation and records), build and dependency folders, and the script and its test (they name the strings by necessity).

### 2.2 Files on the branch (NOT protected: `ci/` and `tests/` are not in `PROTECTED`)

- `ci/check_flag_gone.py`: the script.
- `tests/test_flag_gone.py`: 19 `unit`-marked cases that run it as a child process (as the workflow does) against two kinds of tree built per test: a clean tree (must pass: defect gone, a test-only override still setting the fixtures flag, docs mentioning the strings, the `notify_no_fixed_version` name) and trees with the defect or the flag added (must fail, with the right rule and path). They also cover a missing gate (definition removed, call commented out, `main.py` absent) and bad usage. The trees are built in `tmp_path`, so no committed fixture file carries the forbidden strings.
- They run in `make test` (`make backend-test` collects `tests/`). No Makefile change is needed for that. `make backend-test` passed: 551 passed, 13 deselected.

### 2.3 Where it goes: `deploy.yml`, job `deploy-prod`, one step (protected)

`.github/workflows/deploy.yml` is the production-promotion workflow (task 18, `workflow_dispatch`, job `deploy-prod`, environment `production`). The step goes **after "Resolve the image tag to promote" and before "Resolve image digests for the tag"**, so it runs before "Deploy the prod Compose project" and a failure stops the job before anything reaches the server.

How it finds "the code at the tag being promoted": the image tag is `YYYYMMDD-HHMMSS-shortsha` (`build-and-push`), so its last field is the commit. The step resolves it, extracts that commit's tree with `git archive`, and runs the script from the dispatched ref against it. It then runs the script on the checked-out workspace too, because `compose.yaml` and `terraform/server/deploy-env.sh` sent to the server come from the workspace, not from the tag. A tag whose commit cannot be found fails closed. There is deliberately no override input. The checkout needs `fetch-depth: 0` so the promoted commit is available.

The diff also rewords one comment ("VT_FEEDS=fixtures / VT_DEMO_DEFECT refusals") so that `deploy.yml` does not trip its own check after the cleanup; "demo-defect" with a hyphen is not matched. Without this, the cleanup commit would need a second protected edit.

```diff
--- a/.github/workflows/deploy.yml
+++ b/.github/workflows/deploy.yml
@@ -257,7 +257,10 @@ jobs:
       INPUT_TAG: ${{ inputs.image_tag }}
       REPO: ${{ github.repository }}
     steps:
+      # Full history: P-FLAG-GONE below checks the tree of the promoted commit,
+      # which is not the tip of the ref this run was dispatched from.
       - uses: actions/checkout@v4
+        with: { fetch-depth: 0 }

       # OIDC: assume the PROD deploy role. Its trust policy accepts only tokens
       # from this repo in the `production` environment (not `main`, not PRs), so
@@ -337,6 +340,38 @@ jobs:
           echo "Promoting image tag: $tag"
           echo "tag=$tag" >> "$GITHUB_OUTPUT"

+      # P-FLAG-GONE (#161, task 29): stop the promotion while a test-only switch
+      # is still in the code. It runs only here, in the production promotion, never
+      # in a pull-request job or in make test-compose, so the pull-request gate
+      # stays green while the demo defect exists.
+      #   - The image tag is YYYYMMDD-HHMMSS-shortsha (build-and-push), so its last
+      #     dash-separated field is the commit the images were built from. The tree
+      #     of THAT commit is checked: it is what the images contain. The script
+      #     is the one on the ref this run was dispatched from, so an old tag is
+      #     judged by today's rule.
+      #   - The checked-out workspace is checked too: the compose.yaml and
+      #     deploy-env.sh sent to the server come from it, not from the tag.
+      #   - A failure stops the job before "Deploy the prod Compose project", so
+      #     nothing reaches the server. There is no override input on purpose.
+      - name: P-FLAG-GONE (demo defect and fixtures flag)
+        if: steps.state.outputs.instance_state == 'running'
+        env:
+          TAG: ${{ steps.tag.outputs.tag }}
+        run: |
+          set -euo pipefail
+          sha="${TAG##*-}"
+          commit="$(git rev-parse --verify --quiet "${sha}^{commit}")" || {
+            echo "P-FLAG-GONE: image tag ${TAG} does not end in a commit that exists in this repository, so what it contains cannot be checked" >&2
+            exit 1
+          }
+          promoted="${RUNNER_TEMP}/promoted-tree"
+          mkdir -p "$promoted"
+          git archive "$commit" | tar -x -C "$promoted"
+          echo "== P-FLAG-GONE at the promoted commit ${commit} (tag ${TAG}) =="
+          python3 ci/check_flag_gone.py "$promoted"
+          echo "== P-FLAG-GONE at the deploy files this run sends (${GITHUB_SHA}) =="
+          python3 ci/check_flag_gone.py .
+
       # Resolve the digests for this tag from GHCR, so the deploy log records
       # what was promoted (acceptance: the log holds each tag's digest; rollback
       # reads the previous tag from it).
@@ -360,7 +395,7 @@ jobs:
       # from Secrets Manager using the server's instance role (the prod deploy
       # OIDC role has no secrets access; architecture.md Security boundaries).
       # DEPLOYMENT_ENVIRONMENT=prod is set by deploy-env.sh, which makes the
-      # backend's VT_FEEDS=fixtures / VT_DEMO_DEFECT refusals fail closed.
+      # backend's fixtures-mode and demo-defect refusals fail closed.
       - name: Deploy the prod Compose project (SSM Run Command)
         if: steps.state.outputs.instance_state == 'running'
         id: deploy
```

Checked locally (the step's shell text, `bash -c`, in this repository with `TAG=20261026-120000-<short sha of HEAD>`): exits 1, prints `P-FLAG-GONE: FAIL`, and names the promoted commit; a tag ending in a sha that does not exist exits 1 with the "does not end in a commit" message. Both are as intended on `main` today. The passing path is covered by the unit tests, not by this step in Actions.

Note on the first real run: while the demo defect exists, a `workflow_dispatch` of `deploy` from `main` (after the `production` approval and with the server running) **must go red at this step and deploy nothing**. That is the Check in #161 ("fails the promotion while the defect path exists"), and a safe first exercise of the step. If the server is stopped, the step is skipped, as are the other server steps.

### 2.4 Optional `Makefile` target (protected; recommended against for now)

AGENTS.md prefers `make` targets. The workflow calls `python3` directly so it does not depend on a `Makefile` change, and `make test` already covers the script. If the owner wants a local command to run before promoting, this is the whole diff (append after the `test-compose` target):

```make
# Append to the end of the Makefile, after the test-compose target:

.PHONY: flag-gone

flag-gone: ## P-FLAG-GONE: fail while the demo defect or the fixtures flag is in the tree: make flag-gone [TREE=<dir>]
	@python3 ci/check_flag_gone.py "$(or $(TREE),.)"
```

Not tested (it is a protected file; this was not applied or run). If approved it needs a matching line in `AGENTS.md` Commands (also protected).

### 2.5 What the cleanup commit must remove (the script run on `main`, 2026-10-26)

`python3 ci/check_flag_gone.py .` on `main` today: FAIL, 78 findings, no `fixtures-flag` finding (the gate is present and no production artifact sets the flag). The `demo-defect` findings are in these files; the cleanup (task 29, after the recorded drill #163, as `drill-runbook.md` step 9 says) has to deal with all of them:

- Source: `backend/vulntriage/ingest/settings.py`, `backend/vulntriage/main.py` (import and the `require_demo_defect_allowed()` call), `backend/vulntriage/mail/message.py`, `backend/vulntriage/mail/delivery.py` (`DemoDefectError`).
- Compose and config: `compose.responder.yaml` (the `VT_DEMO_DEFECT` passthrough), `.env.example`, `terraform/server/deploy-env.sh` (a comment), `ci/test-compose.sh` (a comment).
- Tests that exist only for the defect: `tests/test_demo_defect.py` (the whole file), the defect cases in `tests/test_notifications.py`, `tests/test_compose_responder.py` (`P-PROD-REFUSAL` container form) and `tests/test_compose_responder_static.py` (the passthrough check). #233's `P-DEMO-BE` will add more on its branch; this list was taken from `origin/main`, where it does not exist yet.
- `.github/workflows/deploy.yml`: nothing, if the comment reword in 2.3 is approved.

Deleting those tests is a deliberate retirement of the feature they test, not weakening a test to pass; `make verify`'s weakened-test check lists test-file deletions, so `agent-kit.conf` `APPROVED_TEST_DELETIONS` (protected) needs the exact paths with the owner's decision cited. That is a protected edit for the cleanup commit, not for this proposal.

## 3. Protected paths, approvals, order

### 3.1 Paths this proposal touches

| Path | Change | Protected by |
|---|---|---|
| `.github/workflows/responder.yml` | new file (1.5) | project convention (B3/C2); **not** in `agent-kit.conf` `PROTECTED` |
| `.github/workflows/verify.yml` | pointer comment (1.5) | same |
| `.github/workflows/deploy.yml` | checkout depth, one step, one comment (2.3) | same |
| `Makefile` | optional `flag-gone` target (2.4) | `PROTECTED` |
| `AGENTS.md` | optional Commands line for it | `PROTECTED` |
| `agent-kit.conf` | optional: add `.github/*` to `PROTECTED` (question 4) | `PROTECTED` |

Not protected, committed or proposed as ordinary commits: `ci/check_flag_gone.py`, `tests/test_flag_gone.py` (on the branch), `ci/test-compose.sh` (1.4, later), `_docs/testing.md` (job table row, later).

### 3.2 Approval records the owner must give

Each protected commit is its own `HUMAN_APPROVED=1` commit with only its paths, then a record on #161 in the `asking-the-human.md` format. Two commits:

- **Commit A, `deploy.yml` only** (`P-FLAG-GONE`). Paths: `.github/workflows/deploy.yml`. Approved text: the 2.3 diff.
- **Commit B, `responder.yml` and `verify.yml`**. Paths: `.github/workflows/responder.yml`, `.github/workflows/verify.yml`. Approved text: the two 1.5 diffs. (If the owner picks the every-PR alternative: `verify.yml` only, the alternative diff.)

Record skeleton, per commit (fill the SHAs from the commit; copy the diff from the approval, do not regenerate it):

````
Protected-change approval record
- Issue: #161
- Commit: <full 40-character SHA>
- Parent: <full 40-character SHA of the first parent>
- Paths: <paths of that commit>
- Approved: human, <YYYY-MM-DD>, <link to the approval comment>
- Diff command: git show --format= --no-renames --patch <commit> -- <paths>
- Diff: <verbatim output, identical to the approved diff>
- Blob IDs: <path>: <git rev-parse <commit>:<path>> for each path
````

If question 4 is answered yes, the `agent-kit.conf` commit comes first and gets its own record; otherwise a record naming `.github/` paths breaks the "paths match `PROTECTED`" rule and QA would reject it.

### 3.3 Order

1. (If question 4 is yes) `agent-kit.conf` `PROTECTED` gains `.github/*`: own commit, own record.
2. Merge this branch (`ci/check_flag_gone.py`, `tests/test_flag_gone.py`, this proposal) into `main`. The script has to be on `main` before `deploy.yml` calls it, because the step runs the script from the dispatched ref.
3. Commit A (`deploy.yml`). Then, with the production approval and the server running, dispatch `deploy` from `main` once: expect red at "P-FLAG-GONE" and no deploy (2.3). Record the run on #161.
4. Commit B (`responder.yml`, `verify.yml`) after the owner decides question 1. Then dispatch `responder` once from the Actions page and note the wall-clock time; re-size `timeout-minutes` (protected edit, small).
5. After #233 merges: the `ci/test-compose.sh` log hunk (1.4), an ordinary commit; dispatch `responder` again for the full loop's time and re-size again if needed.
6. After the recorded drill (#163): the cleanup commit (2.5) and its protected pieces; `responder.yml` changes with it (question 6). Then the Check: `P-FLAG-GONE` passes (`make flag-gone`, or `python3 ci/check_flag_gone.py .`, or a `deploy` dispatch).

Independent of the CC22 / #67 change to `verify.yml` (`BASE` for `make verify`): the hunks do not overlap (this one is at lines 89 to 92, in the comment between jobs), so either order applies cleanly; the later one rebases.

### 3.4 If the first CI run is red

For the `responder` job (nightly or dispatched; the PR gate is unaffected):

1. Read the run log, and the `responder-compose-logs` artifact if the 1.4 hunk is in. Decide harness bug (port clash, image build, wait too short), CI-only timing (Grafana), or product bug.
2. A harness or timing fault is fixed forward in `ci/test-compose.sh`, `tests/` or `compose*.yaml` (ordinary commits, no approval needed). Re-run with `workflow_dispatch`.
3. Hitting `timeout-minutes` is a measurement: read how far it got, then re-size (protected, small).
4. If it stays red and cannot be fixed that day, **disable the workflow in the Actions page** (no commit, reversible) or remove the `schedule` block (protected, own commit), so a red nightly run does not teach everyone to ignore Actions. A revert of Commit B is the last resort. None of this affects `verify` or `deploy`.
5. #161's Check ("`make test-compose JOB=responder` green") stays unmet until a green recorded run; the issue is not closed on a red one.

For the `deploy-prod` step: red **because the defect exists** is the expected result before the cleanup (see 2.3). Red **for any other reason** (the tag's commit is not found, `git archive` fails, a runner without `python3`) blocks every production promotion until fixed, by design (fail closed, no override). The fix is a protected commit; the rollback of that commit is a revert. Nothing is deployed in either case. `VERIFY:` that a previous prod promotion of a tag from before the cleanup does not exist; a rollback to such a tag would be refused too.

## 4. Open questions for the owner

1. **Does the `responder` job need the first successful host run of #233 (`P-DEMO-BE`) before it goes in CI?** *Recommendation: no, apply it now.* The 8 cases from #220 passed on your host (103 s), and `timeout-minutes: 45` covers both that and #233's 20 minutes. A nightly job costs the PR gate nothing, and a CI run of the 8 cases gives the first CI evidence for #160 (CI differs from your WSL host in Grafana timing and a cold image build). What does need #233's host run: re-sizing the timeout, and closing #161 (its Check needs `P-DEMO-BE` green). If you prefer to wait, the only cost is a later first CI run; the `deploy.yml` step is independent and does not wait.
2. **Cadence: nightly plus on demand in `responder.yml`, or every push and PR in `verify.yml`?** *Recommendation: nightly plus on demand* (section 1.1). Both is not clean (two workflows, double runs).
3. **Should `responder` be a required status check in the `protect-main` ruleset?** *Recommendation: no.* A scheduled workflow does not report on PRs, and requiring a 20-minute Grafana-timed job would block merges on its timing. (Only applies if question 2 is answered "every PR".)
4. **`.github/` is not in `agent-kit.conf` `PROTECTED`.** Add `.github/*` so the hook asks for `HUMAN_APPROVED=1` and approval records are well-formed? *Recommendation: yes*, as its own approved commit before commits A and B. It matches how `human-tasklist.md` already treats these files; without it, the record format cannot name the paths. The alternative is to approve A and B as the #159 change was and record the gap.
5. **`P-FLAG-GONE` wording (the second open box in #229).** Confirm: (a) rule 1 scans the whole tree except documentation and the check itself, so comments, tests and compose files count, and `notify_no_fixed_version` does not; (b) rule 2 means "no production artifact sets `VT_FEEDS=fixtures`, and `require_feeds_allowed` is defined and called", not "the string is absent", and not the existence of `feeds.py`. *Recommendation: approve as drafted.* Whole-tree is the literal reading of "anywhere in the code", and a narrower source-only scope would let the defect survive in a test or compose file. The cost is that the cleanup has to tidy stale comments too (2.5). Nothing is built beyond this wording until you confirm; changing it is a small edit in `ci/check_flag_gone.py` and its test.
6. **What happens to the `responder` job after the cleanup?** `P-DEMO-BE` and the container form of `P-PROD-REFUSAL` need the defect, so they go with it (2.5) and `P-FLAG-GONE` cannot pass with them in the tree. The remaining cases (the Grafana body shape, the 401 cases, the env check, the test notification) still test the wiring. *Recommendation: keep the nightly job for the remaining wiring cases*; the cleanup commit updates the `responder.yml` header comment and the `testing.md` row with it. Retire `responder.yml` instead only if nothing meaningful is left. The recorded drill (#163) must come first, since it needs the defect.
7. **Check the workspace as well as the promoted tree?** The step runs the script twice (2.3) because `compose.yaml` and `deploy-env.sh` come from the dispatched ref. *Recommendation: yes, keep both.* The extra run takes under a second; the cost is that promoting an old tag from a ref that has the defect also fails (which is the safe direction). Drop the last two lines of the step if you want only the literal "at the tag".
8. **Apply the `ci/test-compose.sh` log hunk (1.4)?** *Recommendation: yes, after #233 merges*, so a red CI run leaves something to read. Without it the upload step is a no-op.
9. **Optional `make flag-gone` target (2.4)?** *Recommendation: not now.* `make test` already covers the script and the workflow does not need it; add it if you want a local pre-promotion command.
