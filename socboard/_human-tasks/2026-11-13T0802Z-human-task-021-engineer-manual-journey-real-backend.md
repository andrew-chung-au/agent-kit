# Run the frontend against the real backend and walk the journey

> Written 2026-11-13T08:02Z by the Engineer for #21; rewritten with copy-paste commands and checked outputs by the orchestrator. The repository is public: no secrets here. Choose the secret, the passwords and the key yourself, keep them out of the issue, and use throwaway values.

## Purpose

Check the last acceptance criterion of #21 by hand: an Analyst signs in, claims a case, moves it to Investigating, adds a note and closes it with a reason; the Lead reads the audit trail and the closed-cases view; a wrong password and an expired token behave. Issue: #21. Kiro Web could not run this (no database, no browser), so the criterion is NOT CHECKED until you paste the result. The automated version is #22.

## Where to run it

The dev container, or a clean clone with Python, uv, bun and make installed, and a browser that can open http://127.0.0.1:5173/ (forward ports 5173 and 8000 in a dev container). Not in Kiro Web. About 15 minutes.

With the mock off, the sign-in page no longer lists the demo usernames and passwords. The usernames are `analyst-a`, `analyst-b` and `lead`; the passwords are the three values you export in Step 1 (they are stored only as hashes, and `make seed` never changes an existing user, so to change them remove `socboard.db` and repeat Steps 2 and 3). The old mock passwords do not work against the real backend.

Run every command from the repository root, in ONE terminal for Steps 0 to 10: the `export` lines only last for that shell, and the frontend needs `VITE_USE_MOCK` from the same shell.

## Step 0: get the branch and install

```
git fetch origin
git switch issue-21-connect-frontend
git pull
make install
```

Expected: the branch is checked out; `make install` finishes without an error line (`echo $?` prints `0`). If the branch has moved since you read this, `git pull` brings the latest; the journey does not change.

## Step 1: set the environment (this shell only)

Pick your own values. Lengths matter: the secret needs at least 32 characters, each seed password at least 12, the ingest key at least 16.

```
export SOCBOARD_TOKEN_SECRET='<a secret of at least 32 characters>'
export SOCBOARD_SEED_PASSWORD_ANALYST_A='<12 or more characters>'
export SOCBOARD_SEED_PASSWORD_ANALYST_B='<12 or more characters>'
export SOCBOARD_SEED_PASSWORD_LEAD='<12 or more characters>'
export SOCBOARD_INGEST_API_KEY='<16 or more characters>'
export VITE_USE_MOCK=false
```

Expected: no output. Remember the three passwords; you type them into the browser. Set the ingest key before Step 3, because the backend reads it at start.

For a clean start, remove an old local database first (it is git-ignored): `rm -f socboard.db`.

## Step 2: create the tables, then load the users and assets

```
make migrate
```

Expected output: `socboard.migrate: the database is at the latest migration`. Running it again prints the same line and changes nothing.

```
make seed
```

Expected output (first run):

```
socboard.seed: 10 asset(s) added, 0 already present
socboard.seed: 3 user(s) added, 0 already present
```

A second run prints `0 asset(s) added, 10 already present` and `0 user(s) added, 3 already present`. If a password variable is missing or too short, the error names it and nothing is added: fix it and run again.

## Step 3: start the backend

```
make backend-run
```

Expected output: `backend started (pid <number>); log: .scratch/backend.log`. Then:

```
curl -s http://127.0.0.1:8000/api/health
```

Expected output: `{"status":"ok"}`

If it printed "the server exited at once", the last log lines follow; the usual cause is a missing or short `SOCBOARD_TOKEN_SECRET` (the backend exits 2). Stop and report what was printed.

## Step 4: start the frontend with the mock off

```
make frontend-start
```

Expected output: `frontend started (pid <number>); log: .scratch/frontend.log`. Open http://127.0.0.1:5173/ in the browser.

Expected in the browser: the Sign in page with NO "Mock mode — test accounts" box. (If you see it, `VITE_USE_MOCK` was not `false` in this shell: run `make frontend-stop`, export it, start again.) After signing in, the top bar must NOT show a `mock` badge.

## Step 5: post two alerts so the queue has two rows

Copy each command as one block. The timestamp is "now" in UTC.

```
curl -s -w "\nHTTP %{http_code}\n" -X POST http://127.0.0.1:8000/api/alerts -H "X-API-Key: $SOCBOARD_INGEST_API_KEY" -H "Content-Type: application/json" -d "{\"source\":\"EDR\",\"type\":\"malware_detection\",\"asset\":\"dc-01\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"title\":\"Malware on domain controller\",\"description\":\"Manual journey test, expected Critical.\"}"
```

Expected: a JSON object containing `"title":"Malware on domain controller"`, `"severity":"Critical"`, `"status":"New"` and an `"id"`, then `HTTP 201`.

```
curl -s -w "\nHTTP %{http_code}\n" -X POST http://127.0.0.1:8000/api/alerts -H "X-API-Key: $SOCBOARD_INGEST_API_KEY" -H "Content-Type: application/json" -d "{\"source\":\"Auth\",\"type\":\"failed_login\",\"asset\":\"kiosk-02\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"title\":\"Failed logins on kiosk\",\"description\":\"Manual journey test, expected Low.\"}"
```

Expected: `"severity":"Low"`, `"status":"New"`, then `HTTP 201`. If you get `HTTP 401`, the ingest key was not exported before Step 3: stop the backend, export it, start again.

## Step 6: the Analyst journey (browser)

Sign in as `analyst-a` with the password you chose for `SOCBOARD_SEED_PASSWORD_ANALYST_A`.

1. The queue shows "Malware on domain controller" (Critical) first, then "Failed logins on kiosk" (Low). That is the server's order; nothing re-sorts it. Now test polling: with the queue still open, post a third alert in the terminal and do not reload.

```
curl -s -w "\nHTTP %{http_code}\n" -X POST http://127.0.0.1:8000/api/alerts -H "X-API-Key: $SOCBOARD_INGEST_API_KEY" -H "Content-Type: application/json" -d "{\"source\":\"NDR\",\"type\":\"unusual_network_traffic\",\"asset\":\"web-prod-01\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"title\":\"Unusual traffic on web server\",\"description\":\"Manual journey test, expected High.\"}"
```

   Expected: `"severity":"High"`, `HTTP 201`, and within about 3 seconds a High row appears between the Critical and the Low, without a reload. Then open the Critical case.
2. Click **Claim case**. Expected: the owner shows `Ana Alvarez`.
3. Click **Start investigating**. Expected: the status shows Investigating.
4. Type a note such as `<b>plain</b> text` and click **Add note**. Expected: it appears in the Notes list as the literal characters `<b>plain</b> text`, not bold.
5. Click **Close case…**, pick a reason, click **Close case** in the dialog. Expected: the status shows Closed with the reason you picked, and the case is gone from the queue.
6. Check the page: no **Audit trail** panel, and no **Closed** link in the top bar. Look at the link at the top of the closed case and write down what it says. (If it says "Closed cases", it leads to a page that says only a Lead can see it; Reviewer finding 1 on #21. After the fix it says "Queue".)
7. Check the session. Open the browser developer tools, Application tab. Under Session storage for http://127.0.0.1:5173 the key `socboard.session` exists. Under Local storage that key does NOT exist.

## Step 7: the Lead journey (browser)

Click **Log out**, then sign in as `lead` with the password you chose for `SOCBOARD_SEED_PASSWORD_LEAD`.

1. The **Closed** link is now in the top bar. Open it. Expected: the case you closed is listed, with its reason.
2. Open that case. Expected: the **Audit trail** panel lists the raw action codes in time order. For the steps above it reads: `ingested` (actor: system), `claimed` (Ana Alvarez), `status_changed` (to Investigating), `note_added`, `status_changed` (to Closed). The note sits between the two status changes.

## Step 8: the wrong-password check (browser)

Click **Log out**. Sign in as `analyst-a` with a wrong password.

Expected: the page shows `Invalid username or password.`, stays on the Sign in page, and does not crash.

## Step 9: the 401 check

Sign in as `analyst-a` with the right password and leave the queue open. Then, in the terminal:

```
make backend-stop
```

Expected: `backend stopped`.

```
export SOCBOARD_TOKEN_SECRET='<a different secret of at least 32 characters>'
```

```
make backend-run
```

Expected: `backend started (pid <number>); log: .scratch/backend.log`. Go back to the browser and wait up to 3 seconds for the next poll.

Expected: you are returned to the Sign in page, and `socboard.session` is gone from Session storage. (No "session expired" message is shown on the Sign in page; that is known and not part of #21.)

## Step 10: stop what you started

```
make frontend-stop
```

Expected: `frontend stopped`.

```
make backend-stop
```

Expected: `backend stopped`. Optional: `unset VITE_USE_MOCK`, and `rm -f socboard.db` to drop the test data.

## Record the result

Paste on #21 a pass or fail for each row, and anything unexpected. Do NOT paste passwords, the secret, the key or any token. Then tell the orchestrator, who records it and closes the issue after the merge.

| Step | Pass or fail | Output or note |
|---|---|---|
| 0 branch, install | | |
| 2 migrate, seed output as shown | | |
| 3 backend-run, health `{"status":"ok"}` | | |
| 4 frontend-start, no mock box, no mock badge | | |
| 5 both alerts HTTP 201, Critical and Low | | |
| 6.1 queue: Critical first; the third (High) alert appears by polling, no reload | | |
| 6.2 to 6.5 claim, Investigating, literal note, close with reason | | |
| 6.6 Analyst: no Audit panel, no Closed link; back link text: | | |
| 6.7 token in Session storage only | | |
| 7 Lead: Closed list, audit trail entries and order | | |
| 8 wrong password message | | |
| 9 401 returns to Sign in, session key gone | | |
| 10 both stopped | | |

## Risk

Two local servers run until Step 10. The database file `socboard.db` (git-ignored) holds the test data. Nothing is pushed.
