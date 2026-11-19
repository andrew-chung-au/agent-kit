# Add the three OpenTelemetry packages for #288

## Purpose

Add `opentelemetry-api`, `opentelemetry-sdk` and `opentelemetry-exporter-otlp-proto-http` to the runtime dependencies, with a lower bound each, and commit the changed `pyproject.toml` and `uv.lock`. The agent never runs `uv add` or edits those two files (they are protected). Issue: #288.

Versions chosen (PyPI, checked 2026-11-16 at https://pypi.org/pypi/opentelemetry-api/json and the same path for the other two names): all three are 1.45.2, released 2026-10-29, each declaring `requires_python >=3.10`, so Python 3.12 (the project's `>=3.12`) is supported. The bounds are `>=1.45.2`. No instrumentation package is added: those record URLs and SQL that can carry alert text.

## Where to run it

Your own machine, in a clean clone of the repository (or the clone you already use, with no uncommitted changes). Not here: the agent's sandbox, which cannot edit protected files.

If a tool shows a permission prompt, reject one prompt at a time; rejecting ends the agent's turn, so tell it to continue.

## Before you start

1. Check that the tree is clean.

```
git status --short
```

Expected: prints nothing.
If different: commit or stash your changes first, then start again.

2. Check that `uv` and `bun` are installed (`make verify` needs both).

```
uv --version
```

Expected: one line such as `uv 0.x.y`.
If different: install `uv`, then start again.

```
bun --version
```

Expected: one line with a version number.
If different: install `bun`, then start again.

## Steps

### Step 1: fetch the branch

The branch must already be pushed (the orchestrator pushes it with this file on it).

```
git fetch origin
```

Expected: no error. It may print the new branch `claude/288-otel-deps`.
If different: stop and tell the orchestrator what was printed.

### Step 2: switch to the branch

```
git switch claude/288-otel-deps
```

Expected: `Switched to a new branch 'claude/288-otel-deps'` (or `Switched to branch ...`), tracking `origin/claude/288-otel-deps`.
If different: if git says no such branch, the branch is not pushed yet; stop and tell the orchestrator.

### Step 3: check you are on the right commit

```
git log --oneline -3
```

Expected: the top commit has a subject ending `(#288)` and adds this file; the one below it is `5181065 Merge pull request #319 ...`.
If different: stop and tell the orchestrator what was printed.

### Step 4: install the current packages

```
make install
```

Expected: ends without an error (it runs `uv sync --locked --all-groups` and the frontend install).
If different: stop and tell the orchestrator what was printed.

### Step 5: add the first package

```
uv add "opentelemetry-api>=1.45.2"
```

Expected: `Resolved N packages`, then `Prepared`/`Installed` lines naming `opentelemetry-api==1.45.2` (or a later patch version if PyPI has moved on), and no error.
If different: stop and tell the orchestrator what was printed. Do not retry with another version.

### Step 6: add the second package

```
uv add "opentelemetry-sdk>=1.45.2"
```

Expected: the same shape of output, naming `opentelemetry-sdk` and `opentelemetry-semantic-conventions`.
If different: stop and tell the orchestrator what was printed.

### Step 7: add the third package

```
uv add "opentelemetry-exporter-otlp-proto-http>=1.45.2"
```

Expected: the same shape of output, naming `opentelemetry-exporter-otlp-proto-http` and its dependencies (such as `opentelemetry-proto`, `protobuf` and `googleapis-common-protos`).
If different: stop and tell the orchestrator what was printed.

### Step 8: check the `pyproject.toml` diff adds only the three lines

```
git diff -U0 pyproject.toml
```

Expected: after the `---`/`+++`/`@@` header lines, exactly three lines starting with `+`, in the `dependencies` list (not in the `dev` group):

```
+    "opentelemetry-api>=1.45.2",
+    "opentelemetry-exporter-otlp-proto-http>=1.45.2",
+    "opentelemetry-sdk>=1.45.2",
```

and no line starting with a single `-` (the `---` header line is not a change).If different: any other `+` or `-` line means something else changed. Stop and tell the orchestrator what was printed; do not commit.

### Step 9: check `uv.lock` changes no existing pin

```
git diff --stat uv.lock
```

Expected: `1 file changed, N insertions(+)` with no `deletions(-)` part. A deletion means an existing line (a pin, a hash or a dependency entry) was changed.
If different: if `deletions(-)` appears, run `git diff -U0 uv.lock` and look at each line starting with a single `-` (not the `---` header line). A `version = ` line for a package that was already in the file means an existing pin moved. Stop, don't commit, and tell the orchestrator which package and the old and new versions.

### Step 10: list the packages the lock file gained

```
git diff -U0 uv.lock
```

Expected: the added `[[package]]` blocks (look for `+name = "..."`) are the three packages above plus their dependencies, such as `opentelemetry-proto`, `opentelemetry-semantic-conventions`, `opentelemetry-exporter-otlp-proto-common`, `protobuf`, `googleapis-common-protos`, `requests` and what it needs (`certifi`, `charset-normalizer`, `idna`, `urllib3`), `importlib-metadata` or `zipp` only if the resolver needs them. No FastAPI, SQLAlchemy or HTTP instrumentation package (`opentelemetry-instrumentation-*`) appears.
If different: a name starting `opentelemetry-instrumentation` means the wrong package was added. Stop, don't commit, and tell the orchestrator.

### Step 11: check the lock file matches `pyproject.toml`

```
uv sync --locked --all-groups
```

Expected: no error, and no message that the lock file needs updating.
If different: stop and tell the orchestrator what was printed.

### Step 12: run the checks

```
make verify
```

Expected: ends with `PASS` for every section (Tests, Lint and the others) and exit code 0.
If different: stop and tell the orchestrator which section failed and the last lines printed. Do not commit.

### Step 13: commit the two files

Check which files changed, then stage the two by name.

```
git status --short
```

Expected: exactly ` M pyproject.toml` and ` M uv.lock`.
If different: stop and tell the orchestrator what was printed.

```
git add pyproject.toml uv.lock
```

Expected: prints nothing.

Write your own commit message: it is yours, and it needs no `Assisted-by` line. The subject must end `(#288)` and must not put a closing keyword before the number. A suggested subject: `Add the OpenTelemetry API, SDK and OTLP HTTP exporter packages (#288)`.

```
HUMAN_APPROVED=1 git commit -m "Add the OpenTelemetry API, SDK and OTLP HTTP exporter packages (#288)"
```

Expected: the commit succeeds and lists two files changed.
If different: a hook message names the cause. Stop and tell the orchestrator what was printed; do not use `--no-verify`.
Risk: the packages enter the lock file for every later build. Undo before pushing: `git reset --hard HEAD~1` (it discards the commit; run it only if you are sure).

### Step 14: push

```
git push origin claude/288-otel-deps
```

Expected: the push succeeds. The pre-push hook may run the push check; it prints `PASS`.
If different: stop and tell the orchestrator what was printed.

### Step 15: read the CI run

Tell the orchestrator the push is done. CI runs `make install` and `make verify` and builds the image on the pushed head. To read the runs yourself:

```
gh run list --branch claude/288-otel-deps --limit 5
```

Expected: the `verify` and `image` runs for the new head finish with `success`.
If different: stop and tell the orchestrator which run failed.

## Record the result

Paste the output or write pass or fail for each step. Results contain no secrets. Commit this file with the result so a later run can compare (a plain `git add` of this file and `git commit`, then `git push origin claude/288-otel-deps`).

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 fetch | Not reported |  |
| 2 switch | PASS (as reported) | `git log --oneline -3` showed `HEAD -> claude/288-otel-deps` at 467e6d2 with `origin/claude/288-otel-deps`, above 5181065. |
| 3 log | PASS (as reported) | As step 2. |
| 4 make install | Not reported |  |
| 5 uv add opentelemetry-api | PASS (as reported) | `pyproject.toml` line 10: `"opentelemetry-api>=1.45.2"`. |
| 6 uv add opentelemetry-sdk | PASS (as reported) | `pyproject.toml` line 12: `"opentelemetry-sdk>=1.45.2"`. |
| 7 uv add opentelemetry-exporter-otlp-proto-http | PASS (as reported) | `pyproject.toml` line 11: `"opentelemetry-exporter-otlp-proto-http>=1.45.2"`. |
| 8 pyproject.toml diff: three added lines only | PASS | Read by the orchestrator session on `origin/main...origin/issue-288-otel-deps`: exactly the three `+` lines, no `-` line. |
| 9 uv.lock: no deletions | PASS | Read by the orchestrator session: 297 insertions, no removed line. |
| 10 uv.lock: packages gained, no instrumentation package | PASS | Added: certifi, charset-normalizer, googleapis-common-protos, opentelemetry-exporter-http-transport (0.66b2), opentelemetry-exporter-otlp-common (0.66b2), opentelemetry-exporter-otlp-proto-common, opentelemetry-exporter-otlp-proto-http, opentelemetry-proto, opentelemetry-sdk, opentelemetry-semantic-conventions, protobuf, requests, urllib3. `opentelemetry-api` was already in the lock. The two `0.66b2` packages are dependencies of the 1.45.2 exporter that this file's list predates. No `opentelemetry-instrumentation-*`. |
| 11 uv sync --locked | Not reported | CI's `socboard verify` and `image` runs on a63c813 use the lock (both success). |
| 12 make verify | PASS (as reported) | `VERIFY: PASS` on the maintainer's machine. CI: `socboard verify` run on a63c813, success. |
| 13 commit (hash) | PASS | a63c813, `Add the OpenTelemetry API, SDK and OTLP HTTP exporter packages (#288)`. |
| 14 push | PASS (as reported) | `467e6d2..a63c813  claude/288-otel-deps -> claude/288-otel-deps`. |
| 15 CI runs (links) | PASS | On a63c813: `socboard verify`, `compose`, `image` and `postgres` all success (branch `claude/288-otel-deps`). |

Filled on 2026-11-16 by the orchestrator session from the maintainer's pasted output and from the pushed commit. "As reported" means the maintainer pasted it or said so; "Not reported" means nothing was said about it.

## Risk

The new packages enter the lock file, so every later install and the Docker image carry them. Nothing here changes live behaviour: no code uses the packages until #289. Undo after pushing: revert the commit.
