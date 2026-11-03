# Session summary: cloud tasklist, re-audit, Terraform review (2026-10-25)

Claude Code cloud session on `claude/quirky-brahmagupta-uisrck` (PR 202). Planning and review work; no application code changed.

## What was done

- Surveyed the roadmap, human tasklist, pending-verification list and open issues for work a cloud session can do. Split the human tasklist into a human-only list and a new `_docs/cloud-tasklist.md` (CC1-CC29), cross-referenced both ways.
- `make install` and `make verify` baseline: PASS (88 frontend, 496 backend tests, type check).
- Rubric re-audit by the `rubric-auditor` at `fb24904`: 17/24 (commit `be9f8bf`). Found the README overclaim of the responder (tracked as CC24, not fixed).
- Started `dockerd` for the session (B1, manual route) and ran the Terraform static check with the pinned image (B2). `fmt -check` passes; `init` and `validate` are blocked by the network policy.
- Pre-apply review of `terraform/` (CC10): `_docs/reviews/2026-10-25-terraform-pre-apply-review.md`, posted on #141 (comment 6397164959). Two High findings: the dev trust policy's `sub` claim cannot match the `environment: dev` deploy job, and the server module needs both secrets to exist at plan time.

## Approvals asked for (permission review)

| Action | Basis | Group | Outcome |
|---|---|---|---|
| Start `dockerd` in the background (`.scratch/docker_start.sh`) | System change in a cloud session; the user approved B1 | writes to the environment (keep asking) | Approved. **Not undone**: the daemon is still running, pid in `.scratch/dockerd.pid`. Undo: `bash .scratch/docker_stop.sh` |
| `docker pull hashicorp/terraform:1.17.0` | Install of a large tool; the user approved B2 | writes to the environment (keep asking) | Approved. Image stays in the session's Docker; remove with `docker rmi hashicorp/terraform:1.17.0` |
| `make issue-comment N=141 FILE=.scratch/issue-141-review.md` | Posts to an external service (GitHub issue) | writes to the record (keep asking) | Posted |

Not done: #48's protected `Makefile` and `AGENTS.md` change (no exact diff was shown for approval).

## Findings and risks for the human

- **Network policy** refuses `registry.terraform.io` and `checkpoint-api.hashicorp.com` (human B6). `releases.hashicorp.com`, `ghcr.io`, the advisory sources and GitHub raw were not tested. npm, PyPI and Docker Hub image pulls work.
- Containers cannot reach the session proxy by default. Use `--network host`, pass `HTTPS_PROXY`, and mount `/root/.ccr/ca-bundle.crt` as `SSL_CERT_FILE`.
- The pre-apply review's F5 (shared deploy policy) needs a human decision (tasklist F0).
- Tool versions in the cloud image (Node 22.22, uv 0.11.32, Python 3.13) differ from the pins in `AGENTS.md`; `make verify` passed regardless.
- The re-audit's CI evidence (runs 40188742150, 40188742170, 40160976080) was taken from the auditor's report and not re-checked here.

## Later in the session (human away; consecutive work)

- PR 202 merged before the CC29 commit was pushed, so the Terraform fixes went into PR 203 (merge of `main` into the session branch, no force push).
- **CC29 done** (PR 203): F1-F4 fixed, `fmt` and `validate` pass; nothing planned or applied.
- **CC24 done:** the README no longer claims the responder is built, no longer links images that did not exist, and no longer claims the 3-point CI/CD level.
- **CC25 done:** the auditor's CI evidence was checked against the Actions records (run 40188742150, `telemetry` job: 3 passed); comments posted on #172 and #157 (6397420046, 6397420242); the matching `pending-verification.md` boxes ticked.
- **CC19 partly done:** `make test-integration` against real Postgres 16.4: 232 passed. It does not run the Alembic chain, so #201 stays open. #68's "write, restart, read" persistence test was not found by searching the backend tests for `persist`/`restart`, so #68 should stay open.
- **CC27 done:** the app ran on `make dev-start` (SQLite, fixtures, no Docker), signed in through the real form, and the screenshots are committed under `docs/images/` and linked in the README.
- **Blocked:** `make test-compose JOB=telemetry` (CC14) failed at the backend image build: `ghcr.io/astral-sh/uv:0.13.1` could not be fetched because the proxy refused `pkg-containers.githubusercontent.com` (Forbidden). Docker Hub pulls work. `make compose-up` (CC26) and the observability stack check (CC15) also need a `.env`, and writing `.env` is denied by the permission settings; I did not work around it. Human rows B6 (hosts) and B7 (`.env`) added.
- **Finding:** the real login page still shows the mock service's "Demo credentials" (`analyst@example.com` / `triage-demo`), which the real backend refuses (CC30, proposed, not changed).

### Additional approvals and actions (permission review)

| Action | Basis | Group | Outcome |
|---|---|---|---|
| `make test-compose JOB=telemetry` (background, Docker) | Builds images, pulls from registries | writes to the environment (keep asking) | Ran; failed at the `ghcr.io` build step; no leftover containers |
| `make test-integration` (Docker, Postgres) | Starts a Postgres container | writes to the environment (keep asking) | Passed; the project's own script tears the `vt-test` project down |
| `make dev-start VT_FEEDS=fixtures DEPLOYMENT_ENVIRONMENT=dev`, `make dev-stop` | Starts and stops local processes this session started | writes to the environment (keep asking) | Started, used, stopped |
| `uv run --directory backend python -m vulntriage.manage create-user ... < .scratch/pw.txt` | Writes a user to the local dev SQLite database | writes to the record (keep asking) | Created user `lead`; the DB file is git-ignored |
| `python3 .scratch/demo_seed.py`, `node .scratch/shot.js` | Agent-written scripts, local only (127.0.0.1) | `.scratch` scripts: never allow as a standing rule | Ran once each; `shot.js` wrote two PNGs to `docs/images/` |
| `make issue-comment N=172` and `N=157` | Posts to GitHub | writes to the record (keep asking) | Posted |
| Write to `.env` | Denied by the permission settings | risky: respect the deny | Not done, not worked around |

`dockerd` (pid in `.scratch/dockerd.pid`) is still running and has not been undone. `.scratch/` holds a throwaway demo password and cookie, git-ignored.

## Next

The remaining cloud work needs you: B6 (`ghcr.io`, `pkg-containers.githubusercontent.com`) for CC14/CC17/CC18/CC26, B7 (`.env`) for CC15/CC26, and the #48 diff approval so sessions start Docker themselves. Agent-only items left: CC30 (needs a go-ahead), CC3 and CC4 (low value), CC2 (close-out doc drafts), CC7 (needs your agreement; gated on F1-F3).
