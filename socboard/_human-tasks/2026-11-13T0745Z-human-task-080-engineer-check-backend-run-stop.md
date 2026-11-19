# Check the hardened make backend-run and make backend-stop

## Purpose

Run the checks that need a real backend for the #80 change to `backend-run` and `backend-stop` (this checkout only on stop; start-up confirmed by a health request on run), and read the three cases that are checked by reading the diff. Issue: #80.

## Where to run it

The dev container terminal (it has `.venv` with FastAPI and uvicorn), in this checkout on branch `issue-80-backend-run-stop`, with the `Makefile` change and `scripts/backend_probe.py` in the working tree (uncommitted is fine). Not here: the Kiro Web sandbox, which has no packages and no second checkout.

Some steps need two terminals ("A" and "B"). Work from the checkout's root in both. Steps below say `../socboard-other-80`; if your checkout folder is not named `socboard`, adjust the `.venv/bin/python` path in the second-checkout steps.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. The backend needs `SOCBOARD_TOKEN_SECRET`, at least 32 characters, or the server exits 2. Set it in the terminal the way you already do for the dev container; read the value from the place you keep it (your password manager or the dev container's settings). Never type it into this file, and do not print it (no `env`, `printenv`, or `cat` of an env file). This check prints only a verdict:

```
test "${#SOCBOARD_TOKEN_SECRET}" -ge 32 && echo secret-ok || echo secret-missing-or-short
```

Expected: `secret-ok`. Do this in every terminal you use.

2. Nothing of yours is running on ports 8000, 8011 or 8012, and no old pid file is in the way.

```
git status --short
ls .scratch/backend.pid
```

Expected: the status lists `Makefile` (modified), `scripts/backend_probe.py` and this task file (untracked); `ls` says there is no such file. If a pid file exists, run `make backend-stop` first and tell the orchestrator.

3. The dry run expands both targets.

```
make -n backend-run
make -n backend-stop
```

Expected: both print their recipe text and exit 0. Nothing starts.

## Steps

### Step 1: run, normal case

```
make backend-run
```

Expected: within a few seconds, `backend started (pid N); log: .scratch/backend.log`, exit 0.
If different: stop and tell the orchestrator what was printed (and the last lines of `.scratch/backend.log`).
Risk: starts a backend on 127.0.0.1:8000 in the background. Undo: Step 2 (`make backend-stop`).

### Step 2: health answers, and stop in this checkout (normal case)

```
.venv/bin/python scripts/backend_probe.py health
make backend-stop
ls .scratch/backend.pid
```

Expected: the first command prints nothing and exits 0 (`echo $?` right after it prints 0); `make backend-stop` prints `backend stopped`; `ls` says there is no such file.
If different: stop and tell the orchestrator what was printed.
Risk: stops the backend that Step 1 started (only that one).

### Step 3: run twice says "already running"

```
make backend-run
make backend-run
.venv/bin/python scripts/backend_probe.py health
make backend-stop
```

Expected: the first prints `backend started (pid N)`; the second prints `backend is already running (pid N)` with the same N, make reports an error (exit non-zero; `make` shows 2 for a failed recipe, the recipe itself exits 1) and does not start or touch the first process; the probe still exits 0; the stop prints `backend stopped`.
If different: stop and tell the orchestrator what was printed.
Risk: starts and stops one backend on port 8000.

### Step 4: stop refused for a backend of another checkout (refused case 1)

Build a second checkout and start its backend on a different port. The cloned folder has its own copy of the package; it runs with this checkout's Python.

```
git clone --local . ../socboard-other-80
```

Expected: a clone appears next to this folder.

Start its backend in terminal B, from the second checkout (set the secret first, see "Before you start"):

```
cd ../socboard-other-80
SOCBOARD_PORT=8011 ../socboard/.venv/bin/python -m socboard.server
```

Expected: uvicorn logs `Uvicorn running on http://127.0.0.1:8011`. Leave it running. In terminal A, find its pid and write it into this checkout's pid file (replace PID with the number printed by `pgrep`; it must be the one whose folder is the second checkout):

```
pgrep -f "socboard.server"
echo PID > .scratch/backend.pid
make backend-stop
```

Expected: `make backend-stop` prints a message that names the pid and says its working directory is not this checkout (`the working directory of pid PID is not this checkout; nothing killed; pid file kept`), exits non-zero, and the pid file is still there:

```
cat .scratch/backend.pid
SOCBOARD_PORT=8011 .venv/bin/python scripts/backend_probe.py health
```

Expected: the pid file holds PID; the probe exits 0 (the other backend still answers `/api/health`).
If different: if the backend was stopped, tell the orchestrator at once; stop here.
Refusal test: run the `make backend-stop` in terminal A, this checkout; if the rule fails it kills the process in terminal B (which is the second checkout's own test backend, yours).
Risk: `echo PID > .scratch/backend.pid` replaces this checkout's pid file; do not use a pid that is not the test backend. Undo for the step: `rm .scratch/backend.pid` and Ctrl-C in terminal B.

Clean up (terminal B: Ctrl-C; terminal A):

```
rm .scratch/backend.pid
```

Keep `../socboard-other-80` for Step 7, or remove it at the end with `rm -r ../socboard-other-80`.

### Step 5: stop works through a symlink spelling of the checkout

```
ln -s "$(pwd)" ../socboard-link-80
cd ../socboard-link-80
make backend-run
make backend-stop
ls .scratch/backend.pid
cd ../socboard
rm ../socboard-link-80
```

Expected: `backend started (pid N)`, then `backend stopped`, `ls` says no such file. (`rm` of the link removes the link only.)
If different: stop and tell the orchestrator what was printed.
Risk: starts and stops one backend through the link.

### Step 6: the existing refusals still hold

```
echo abc > .scratch/backend.pid
make backend-stop
echo $$ > .scratch/backend.pid
make backend-stop
rm .scratch/backend.pid
```

Expected: the first says `does not hold a plain pid; nothing killed`; the second says `pid N does not look like the backend ... nothing killed` (N is your shell, still alive afterwards); both exit non-zero.
If different: stop and tell the orchestrator what was printed.
Refusal test: use terminal A only.
Risk: if the rule failed, the second command would kill your own shell (this terminal closes). Nothing else is affected.

Also check a stale pid:

```
echo 999999 > .scratch/backend.pid
make backend-stop
ls .scratch/backend.pid
```

Expected: `backend was not running (stale pid file removed)`, exit 0, no pid file. (If pid 999999 exists on your machine, choose a pid that does not.)

Also check a live process that belongs to another user (the stale test must not call it stale). Pid 1 is owned by root in the dev container; run this as your normal user, not as root:

```
echo 1 > .scratch/backend.pid
make backend-stop
cat .scratch/backend.pid
rm .scratch/backend.pid
```

Expected: `backend-stop: pid 1 does not look like the backend ... nothing killed`, a non-zero exit, and the pid file still holds `1` before you remove it. Before the #80 change the same commands printed `backend was not running (stale pid file removed)` and exited 0; that is the wrong answer for a live process.
If different: stop and tell the orchestrator what was printed.
Refusal test: terminal A. If the rule fails, `make backend-stop` would try to signal pid 1; as a normal user the signal is refused by the system, and as root the command-line check refuses it first.
Risk: none beyond replacing `.scratch/backend.pid`, which the last command removes.

### Step 7: run refused when something already listens on the port (refused case 1)

Foreign listener 1: a plain HTTP server. In terminal B:

```
.venv/bin/python -m http.server 8000 --bind 127.0.0.1
```

Terminal A:

```
make backend-run
ls .scratch/backend.pid
```

Expected: `backend-run: port 8000 on 127.0.0.1 is already in use; nothing started`, non-zero exit, no pid file, and no new process (terminal B is untouched and keeps serving). Stop terminal B with Ctrl-C.

Foreign listener 2: a backend of another checkout on port 8000 (it answers `/api/health` with 200). Terminal B (set the secret first):

```
cd ../socboard-other-80
../socboard/.venv/bin/python -m socboard.server
```

Terminal A:

```
make backend-run
ls .scratch/backend.pid
```

Expected: the same message and result as above; no pid file; terminal B's backend keeps running. Stop terminal B with Ctrl-C.
If different: stop and tell the orchestrator what was printed.
Refusal test: terminal A, this checkout. If the rule fails it prints `backend started` or starts a second process that dies on the busy port.
Risk: none beyond the two listeners you start yourself; stop both with Ctrl-C.

### Step 8: settings the server refuses are still refused at once

```
make backend-run SOCBOARD_HOST=0.0.0.0
ls .scratch/backend.pid
make backend-run SOCBOARD_PORT=abc
ls .scratch/backend.pid
```

Expected for each: within about two seconds, `backend-run: the server exited before it answered /api/health; last lines of .scratch/backend.log:` followed by the server's own message (`socboard.server: SOCBOARD_HOST must be localhost: 127.0.0.1, localhost or ::1`, and `socboard.server: SOCBOARD_PORT must be a whole number from 1 to 65535`), a non-zero exit, no pid file, and no Python traceback from `scripts/backend_probe.py` (the helper exits quietly for these values and builds no URL or socket).
If different: stop and tell the orchestrator what was printed.
Refusal test: terminal A. If the rule fails the backend would be reachable on every address or the target would print `backend started`.
Risk: if `SOCBOARD_HOST=0.0.0.0` were accepted, a backend would listen on all addresses; run `make backend-stop` at once.

### Step 8a: the other allowed hosts, `::1` and `localhost`

The health URL puts an IPv6 host in brackets, and `localhost` can resolve to more than one address. Run each host on its own, stopping the backend in between:

```
make backend-run SOCBOARD_HOST=::1
curl -s http://[::1]:8000/api/health
make backend-stop
make backend-run SOCBOARD_HOST=localhost
curl -s http://localhost:8000/api/health
make backend-stop
```

Expected for each host: `backend started (pid N); log: .scratch/backend.log` within a few seconds, the `curl` prints `{"status":"ok"}`, and `backend stopped`. If the dev container has no IPv6 loopback, the `::1` run fails at start-up with the server's own error and the log tail; write that down as "no IPv6 here" instead of a fail.
If different: stop and tell the orchestrator what was printed.
Risk: starts and stops one backend on port 8000 per host.

### Step 9: the 14 backend-target checks from #10

Repeat the human run from #10 and compare with the results recorded there: the QA comment on #10 (https://github.com/andrew-chung-au/socboard/issues/10#issuecomment-6812733808, section "HUMAN-VERIFIED backend targets (14 checks)"), #10's Close comment, and `_session-summaries/2026-11-12T0241Z-issue-010-orchestrator-backend-skeleton.md` (Commands to validate: run, then stop). Read those first; the results named there are:

1. `make backend-run`: start ok.
2. `GET /api/health`: 200, body status ok.
3. Second `make backend-run`: refused ("already running").
4. `DELETE /api/health`: 405, an `Allow` header listing GET, code `method_not_allowed`.
5. `GET /api/zzmarker`: 404, code `not_found`, the marker not in the body.
6. `make backend-stop`: stop ok.
7. Second `make backend-stop`: "not running".
8. `make backend-run SOCBOARD_HOST=0.0.0.0`: refused.
9. No pid file left after the stop.
10. Pid file pointing at your own shell: `make backend-stop` refused, nothing killed.

(The recorded list names fewer than 14 separate outcomes; the rest are the same commands' exit codes. Run all of the above and compare each with #10's record.) Commands for the two HTTP checks, with the backend started by `make backend-run` (curl is in the dev container; any HTTP client will do):

```
curl -s -i -X DELETE http://127.0.0.1:8000/api/health
curl -s -i http://127.0.0.1:8000/api/zzmarker
```

Expected: as listed above.
Risk: starts and stops one backend on port 8000 (`make backend-stop` at the end).

### Step 10: tests and verify

```
make test
make verify
```

Expected: `make test` passes (the Python tests, then the frontend tests); `make verify` prints `VERIFY: PASS`, with any warning explained. No test file is changed in this issue.
If different: stop and tell the orchestrator what was printed.

### Step 11: read the diff for the cases that need no run

Read `git diff Makefile` and `scripts/backend_probe.py` and confirm each:

1. Late failure (refused case 2): in the `backend-run` wait loop, the `alive` check runs at the top of every one of up to 30 rounds. A process that dies after the first second prints the log tail (20 lines), removes `.scratch/backend.pid`, and exits 1; `backend started` is printed only when the health probe succeeds and `alive` is still true. A 404 on `/api/health` is not healthy (the helper returns true only for status 200 and the JSON body `{"status": "ok"}`).
2. Timeout (refused case 3): after 30 rounds with no healthy answer the target prints the log tail, sends `kill` to the pid it started, waits up to 10 seconds, and then either says it did not stop and keeps the pid file (exit 1) or removes the pid file (exit 1).
3. Unreadable cwd (refused case 2 of the stop): `backend-stop` reads `readlink /proc/PID/cwd` (plain, so an unreadable link gives an empty value), and also the `readlink -f` form and the checkout root; if any is empty it refuses with `could not be read`, exits 1 and kills nothing. There is no fallback to the command line alone. A live pid that this user cannot signal (`kill -0` fails, but `/proc/PID` exists) is not treated as stale; it goes on to the command-line and working-directory checks and is refused there.
4. The probe never builds a socket or URL from a rejected value: it calls the server's own `resolve_bind`, and exits 3 for a rejected host or port. `backend-run` then starts the server as before so the server prints its own message.

Optional, to run them: back up the file, make a temporary edit, run, then restore from the backup (do not use `git checkout Makefile`: it would discard the uncommitted change).

```
cp Makefile .scratch/Makefile.80.bak
```

Late failure: in the `backend-run` recipe replace `exec .venv/bin/python -m socboard.server` with `sleep 5; exit 1`. Run `make backend-run`. Expected: after about 5 seconds, `the server exited before it answered /api/health`, the log tail (empty log is fine), exit non-zero, no pid file.

Timeout: replace the same text with `sleep 600`. Run `make backend-run`. Expected: after 30 to 32 seconds (the wait runs on a clock; the last round can add up to about 2 seconds), `no healthy answer from /api/health within 30 s`, then the target stops that `sleep` (about a second), exit non-zero, no pid file. (Your own `sleep 600` is the process being killed.)

Restore:

```
cp .scratch/Makefile.80.bak Makefile
git diff --stat
```

Expected: the stat shows the same `Makefile` change as before the edit. Remove the backup with `rm .scratch/Makefile.80.bak`.
Risk: starts one `sleep` process each time; the second case kills it. Undo: `kill` its pid if it is left over.

Unreadable cwd, optional: if the dev container has a second user, start a backend as that user (from this checkout, port 8012), write its pid into `.scratch/backend.pid`, and run `make backend-stop`. Expected: a refusal (`could not be read`, or `not this checkout`), exit non-zero, nothing killed. Not required.

### Step 12: clean up

```
rm -r ../socboard-other-80
git status --short
```

Expected: no backend of yours still running (`pgrep -f socboard.server` prints nothing), no `.scratch/backend.pid`; the status shows the `Makefile` change, the helper and this file.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets either.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 run, normal | Pass | Run 2026-11-13 in a separate clone at `main` `5d0ffa6`, with a throwaway signing secret set for the terminal only. `backend started (pid N); log: .scratch/backend.log`, exit 0. |
| 2 health and stop | Pass | The probe exited 0, `curl` printed `{"status":"ok"}`, `backend stopped`, and no pid file was left. |
| 3 run twice | Pass | The second `make backend-run` printed `backend is already running (pid N)` with the same pid and exited 2 (make's code); the probe still exited 0; `backend stopped`. |
| 4 stop refused, other checkout | Pass | `make backend-stop` against a backend of a second checkout (port 8011) printed `the working directory of pid N is not this checkout; nothing killed; pid file kept` and exited 2. A later single-command rerun (`S4`) confirmed the same refusal and that the other backend still answered `/api/health`. |
| 5 symlink | Pass | Started and stopped through a symlink spelling of the checkout; no pid file left. |
| 6 existing refusals, stale pid | Pass | `abc` in the pid file: "does not hold a plain pid; nothing killed", exit 2. The pid of the human's own shell: "does not look like the backend; nothing killed", exit 2, and the shell stayed open. A stale pid (999999): "stale pid file removed", exit 0. Pid 1 (owned by root): refused with "nothing killed", exit 2, file kept (the old code called it stale). |
| 7 port in use (two listeners) | Pass | With a plain `http.server` on port 8000, and again with another checkout's backend answering on port 8000, `make backend-run` printed `port 8000 on 127.0.0.1 is already in use; nothing started`, exited non-zero, left no pid file, and the other backend still answered. |
| 8 settings refused | Pass | `SOCBOARD_HOST=0.0.0.0` and `SOCBOARD_PORT=abc` were each refused with the server's own message and the log tail, exit 2, no pid file and no traceback. |
| 8a hosts `::1` and `localhost` | Pass | Both started, answered `{"status":"ok"}` and stopped (this machine has an IPv6 loopback). |
| 9 the 14 checks from #10 | Pass | #10's record names 10 distinct outcomes, not 14. All 10 matched: start, health 200, second start refused, `DELETE /api/health` gave 405 with `allow: GET` and `method_not_allowed`, an unknown path gave 404 `not_found` without the path in the body, stop, second stop "not running", `0.0.0.0` refused, no pid file left, own-shell pid refused. |
| 10 make test, make verify | Pass | `make verify` ended `PASS: Tests`, `PASS: no whitespace errors`, `No test files changed.`, `VERIFY: PASS`. |
| 11 diff read; optional edits | Pass | Late failure (the server dies after 5 s): `the server exited before it answered /api/health`, non-zero, no pid file. No health answer (a `sleep 600` in place of the server): `no healthy answer from /api/health within 30 s` within the allowed 29 to 36 s window (the check asserts the window, not the exact figure), the `sleep` was stopped, non-zero, no pid file. `Makefile` was restored and the tree was clean afterwards. The unreadable-cwd case was read in the diff, not run. |
| 12 clean up | Pass | No server of the human's was left running, no pid file, and `git status` was clean. |

On the first pass the one-line checks R1, R5 and R6 reported FAIL, and the cause was not captured (a server left running in the second terminal is the likely one). R5 was rerun and passed; R1 was replaced by the single-command check S4, which passed; R6 was rerun and passed. Another attempt at S4 failed once because the walkthrough had already deleted the second checkout, and was rerun after rebuilding it.

## Risk

Steps start backends on ports 8000, 8011 and 8012 and write pid files in `.scratch/`; Steps 4, 6 and 11 write a chosen pid into `.scratch/backend.pid` on purpose. A process is killed only by `make backend-stop` on this checkout's own backend, by Ctrl-C in your own terminal, or in Step 11 by the target killing the `sleep` it started. Nothing is pushed or changed in git. Delete the extra folders `../socboard-other-80` and `../socboard-link-80` when done.
