# Runbook: a step needs tools that Kiro Web does not have

Written 2026-11-11 at `26bb7d8`. Read it before launching a role on a frontend or backend issue, and when a QA or Engineer comment says "not run". It does not copy commands from `AGENTS.md`; it says where each step can run.

- **Symptom:** an Engineer or QA comment says `make test`, `make verify`, Vitest, a dev server or a package install "did not run", or a criterion reads "not checked".
- **Check:** the table below. Every row was observed in a Kiro Web session on 2026-11-10 and 2026-11-11 unless it says unverified.
- **Fix:** hand the branch to the dev container, following "The handover" below. Kiro Web does everything that does not need the missing tools.
- **Undo:** none needed; a handover changes no files. If a handover step is skipped, the criterion stays "not checked" and the issue is not closed on it.

## What each place can do

| Capability | Kiro Web | CI (GitHub Actions, on every push) | Dev container (local sandbox) | Your machine |
|---|---|---|---|---|
| Read, edit, commit, push a branch, open a PR, post issue comments | Yes | n/a | Commit yes; push no (read-only token) | Yes (review and push) |
| `python3 -m pytest` on the Python tests | Yes, on Python 3.11 (the project needs 3.12). 47 tests passed on 2026-11-11. `fastapi` and `sqlalchemy` are NOT importable | Yes | Yes | Yes |
| `make test`, `make verify` | No: `uv` cannot create its Python directory (read-only file system), and Python is 3.11 | Yes: runs `make install` then `make verify` with bun 1.4.2 and Node 24.22.0; verified on PR #47 | Yes (needs `make install` once) | Yes |
| `make install`, `make frontend-install` | No: the npm registry returned HTTP 403 (#27, #46). The Python package index is unverified from here | Yes | Yes (registry access is the reason to use it) | Yes |
| Vitest, `make frontend-test`, `make frontend-build`, `bun run lint` | No: `frontend/node_modules` cannot be installed. bun 1.2.14 exists there; the lockfile was written by 1.4.2 | Yes (`frontend-test` via `make verify`; build and lint are not in CI) | Yes | Yes |
| A real dev server (`make frontend-start`), a browser | No | No | Server yes; browser depends on your port forwarding | Yes |
| Claude Code, OpenCode (the other agent tools) | No | No | Yes, installed by `.devcontainer/setup.sh` | Whatever you install |
| Docker (push-check image build, Compose) | No | n/a | No | Yes |
| Read a CI log | Yes: `gh api repos/<owner>/<repo>/actions/jobs/<id>/logs` worked on 2026-11-11 | n/a | Yes | Yes |

## What this means

1. **CI is the verification that does not need a handover.** Pushing a branch from Kiro Web runs `make install` and `make verify` with registry access. Read the log and cite the run id as evidence. This covers: the full gate, the Python and frontend test counts, and the whitespace and weakened-test checks.
2. **CI is not QA.** QA's own mutations, attack scripts and refused-case checks need a working tree with the tools. A QA launch in Kiro Web on a frontend or backend issue can read code and CI logs but cannot run or mutate the tests. Run those QA launches in the dev container.
3. **Backend issues cannot be run in Kiro Web at all** (`fastapi` and `sqlalchemy` are missing, Python is 3.11). Writing and review can be done there; any run needs CI or the dev container.
4. **Handover waits inflate the time metrics.** The trial's elapsed-time figures come from GitHub timestamps and "include idle time". Post a handover comment with a timestamp at each hand-off and hand-back (see below), so a later reader can separate working time from waiting.

## Per-issue map (at `26bb7d8`; revisit when an issue is groomed)

| Issue | Kiro Web | Hand to the dev container | Why |
|---|---|---|---|
| #8 (mock and service-layer rules, tests only) | Engineer writes the tests and commits; push, then read the CI run | Run `make install`, `make frontend-test`, `make verify`; QA fresh launch with mutations (for example reintroducing `dangerouslySetInnerHTML` in a copy) | The criteria are test results; nothing in Kiro Web can run Vitest |
| #51 (timer, reassign flag, component tests, README) | Engineer writes code and tests; CI run as evidence | The same as #8, plus `make frontend-start` and a look at the timer in a browser (you) | Real timing and the page are visible only with a running server |
| #9 (OpenAPI contract) | Write and review the YAML; read-only checks | Any validator run (none is installed in Kiro Web: `yaml` and `jsonschema` are not importable) | A validator criterion cannot be checked in Kiro Web |
| #10 to #14 (FastAPI skeleton, data model, scoring, auth, ingest) | Write and review code | Everything that runs: `make install`, `make test`, `make verify`, the app | `fastapi`, `sqlalchemy` missing and Python 3.11 in Kiro Web; CI can run the tests but not QA's attacks |
| #31 (`bun run lint` passes) | Edit the code | Run the linter | Needs `node_modules`; CI does not run lint |
| #21 (connect frontend to the real API) | Write code | Run both servers and the journeys | Needs the backend and the frontend running together |
| #22 (integration tests, one-command run) | Write code | Run it on your machine if it uses Docker | Docker is available only on your machine |
| Trial: reviewer reads the pinned file in OpenCode and Claude Code (#23 recorded "not tested") | Kiro's own pointer can be tested here | Test the other two tools in the dev container | Only the dev container has those tools |
| Trial: cross-tool calibration (same diff, two tools) | One of the two tools | The other tool | The protocol needs two tools on the same diff |

## The handover

When a role in Kiro Web reaches a step it cannot run, it stops there. The orchestrator then does the following, in this order.

1. **Push the branch** (`issue-<n>-<slug>`), so CI runs. Record the commit and the CI run id in an `Orchestrator:` comment on the issue.
2. **Leave a handover comment** on the issue, headed "Handover to the dev container", with:
   - the branch and the exact commit;
   - what ran in Kiro Web and what did not, with the reason (use the table above);
   - the commands to run, as `make` targets in order, for example `git fetch`, `git checkout <branch>`, `make install`, `make verify`, and the criteria each one settles;
   - what to report back: the command output (counts, `VERIFY:` line), the commit hash tested, and the tool and model used;
   - what the receiving role must not do: change files, push, close or relabel; QA changes nothing outside `.scratch/`;
   - the time the handover was posted.
3. **The dev-container side** runs the commands, then posts a hand-back comment with the output and its own time. A QA launch there follows `qa-engineer.md` as usual, including `make assert-clean`.
4. **The orchestrator continues** from the hand-back: the hash check, the next role, or a QA FAIL back to the Engineer.
5. **Record it.** The session summary gets one line per handover (issue, step, who ran it, tool and model, wait time), so the trial can annotate or exclude the waiting time.

## What stays the same everywhere

- Only the human labels, merges, rebuilds the image and pushes the clean clone.
- A criterion that no one has run reads "not checked" or "human-verified", never PASS.
- The tool and the model are recorded at launch, not afterwards, for every role.
- A QA launch is fresh and independent. A hand-back from the dev container is evidence for the criteria it names, not a replacement for QA's own checks.

## When the dev container is not available (worked example: #8)

Use this when no dev container session can run: the agent tool's usage is exhausted, the container is down, or nobody is at the keyboard. It does not replace the dev container for anything that needs a browser, a real dev server, Docker, or the other agent tools. It was used to finish #8 on 2026-11-11 and is written down so the next agent knows it exists.

### What happened on #8

1. **Engineer in Kiro Web, tests it could not run.** The npm registry returns 403 there, so Vitest could not run. The Engineer wrote about 130 tests by reading the code, the orchestrator pushed the branch, and CI ran `make install` and `make verify`. First run: 112 tests passed and one file failed to load (`import.meta.url` is not a `file:` URL under jsdom). Second run: 132 of 133 (a regex expectation ignored case). Third run: 133 of 133. Each failed run was handed back to the Engineer with the CI log as a **CI feedback round**. A CI feedback round is not a QA FAIL; record the count separately.
2. **QA in the dev container was stopped** by a usage limit before it wrote a verdict. Its partial results were treated as unverified. One real defect it had found (a test row named "second claim by another analyst" signed in as the case's own owner) was fixed by an Engineer round in Claude Code, pushed by the human.
3. **A fresh QA ran in Kiro Web with CI as the test runner**, under an exception the human granted for #8 only (see "The QA exception").
4. **The human ran the plain commands** that CI does not cover (`make install`, `make verify BASE=origin/main`, `make frontend-build` and a search of `frontend/dist`) and pasted the output. No agent usage was needed for this.
5. The orchestrator recorded the results on the issue; the human merged the pull request.

Evidence on #8: CI runs 42967613566 and 42967972731 (failed, fixed), 42968336588 and 42975627247 (passed); the orchestrator record (comment 6789257456), the QA verdict (6789559879) and the human-verified results (6790628287); pull request #56.

### The recipe

**A. Engineer in Kiro Web with CI as the feedback loop**
1. The Engineer writes and commits; it cannot run the tests and says so for each criterion ("not run here; CI or the dev container must run it").
2. The orchestrator pushes the branch and reads the CI log with `gh api repos/<owner>/<repo>/actions/runs/<id>/jobs` and then `.../actions/jobs/<job id>/logs`.
3. On a red run, relaunch the Engineer with the log path and the failing lines. Ask it to re-read the whole file for the same class of mistake and to predict what the next run will report. Post a handover timestamp each time.

**B. QA in Kiro Web with CI as the runner (needs the human's explicit approval each time)**
1. The QA role does not commit. For this recipe the human grants a one-time exception: QA may create throwaway branches named `qa-<issue>-mut-<n>` from the commit under test (`git worktree add .scratch/qa<issue>-wt/<n> -b qa-<issue>-mut-<n> <commit>`), commit a mutation there (subject starting `QA mutation (not for merge): `, trailer `Assisted-by: Kiro`), push only those branches, read the CI result, and delete the remote branch, the worktree and the local branch.
2. QA never touches the issue branch, protected paths, or the main working tree outside `.scratch/`, and never posts to GitHub. The orchestrator runs `make assert-clean` afterwards and checks that `git ls-remote --heads origin` shows no leftover `qa-<issue>-mut-*` branch.
3. **Batch the mutations.** Vitest lists every failing test, so put 5 to 20 mutations in one branch, each in a different place, and read which test failed. #8 used eight CI runs for about 45 mutations. A mutation that breaks an import crashes a whole test file; do not count that as "caught by a specific test". Record each mutation as caught (with the test names) or SURVIVED.
4. QA must write its own mutations and must not rely on the Engineer's report or on an earlier, stopped QA launch.

**C. Close the gap CI leaves, by hand**
CI runs `make verify` but not `make frontend-build` or lint. Ask the human to run the plain commands in the dev container at the exact commit and paste the output; record them on the issue as human-verified, with the reason for any warning. Give the commands as copy-paste steps with the expected output for each.

**D. Records**
- Record tool and model for every launch, including each CI feedback round and any launch that was stopped. An issue that mixes tools (#8: Kiro Web, then Claude Code, then Kiro Web) is recorded as mixed.
- Do not post partial QA findings to the issue before the next QA verdict: a fresh QA reads every comment and would lose its independence.
- Only one orchestrator writes to GitHub. If another session produces a file, it hands the file back and the orchestrator posts it.

### What this does not give you
- QA never sees the code run itself, and each mutation round costs a push and about a minute of CI.
- No browser and no real dev server: the timer, the page and anything visual stay with the human.
- `make frontend-build` and lint are not in CI. Until they are, the human runs them (step C).
- The exception in B is not a standing rule. If it becomes routine, propose a change to `qa-engineer.md` (a protected file on the epoch list) instead of asking again.

### Traps seen on #8
- `verify.sh` warns "test fixtures changed" for any new or changed test file whose path contains "fixture" or "conftest". A new `hostile-fixtures.test.tsx` triggers it; state the reason on the issue (the file is new, the mock's fixtures are untouched).
- A local branch that was cut before another pull request merged shows that pull request's changes as a reverse diff against `origin/main`. Check the pull request's file list, not the local diff.
- A test that waits as long as the test runner's own timeout fails as "timed out", not as an assertion. Keep the wait well below the timeout.
- Tests written blind pass or fail for reasons visible only in CI (jsdom limits, case-sensitive patterns). Budget two or three CI rounds for a large blind test file.

### Traps seen on #51
- **CI's weakened-test line proves nothing on a branch.** `verify.yml` passes the push's previous commit as BASE, so on a branch's first push the check compares the branch with itself and prints "No test files changed", even when test files changed or gained skip markers (QA saw this in a mutation run). Have the human run `make verify BASE=origin/main` in the dev container at the commit under test, and record its "Assertion lines" figure on the issue. Tracked in #49.
- **Fixed in #59: the browser could not reach `make frontend-start` in the dev container.** The server started and `curl http://localhost:5173/` inside the container returned 200, but the browser got `ERR_CONNECTION_REFUSED`, though VS Code listed 5173 as forwarded. Vite listened on IPv6 loopback only (`[::1]:5173` returned 200, `127.0.0.1:5173` was refused), and the port forward connects over IPv4. Since #59, `frontend/vite.config.ts` binds the dev server to `127.0.0.1`: `make frontend-start`, then open http://127.0.0.1:5173/ (the human confirmed the page loads, 2026-11-12). Use that address, not `localhost`: a browser may resolve `localhost` to `[::1]` first, where nothing listens now. The server is not reachable from other machines. To change a variable, run Vite in the foreground from `frontend/` (`make frontend-stop` first, then `node_modules/.bin/vite dev --strictPort` with the variable in front, for example `VITE_FEATURE_REASSIGN=false`), press Ctrl+C to restart it in the same terminal; a second server in a new terminal fails with "Port 5173 is in use".
- **The mock lives in the tab.** The mock's cases are in browser memory: a page reload or a restarted dev server starts again from the seeds and restarts the 20-second new-alert timer. Stay on the page while waiting for a timer alert.
- **Pasting a long log may be rejected.** Pasting long terminal output (logs, full command lines) into the Kiro Web chat was rejected by the chat backend. Send short plain results (yes/no per check, counts, the final line) instead.
