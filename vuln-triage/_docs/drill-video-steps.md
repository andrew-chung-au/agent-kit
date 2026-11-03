# On-call drill video: the one step list

This file supersedes Part 1 step 1 of `_docs/drill-runbook.md` and all of `_docs/drill-runbook-commands.md` for the video, and covers runbook Parts 2 and 3 as well (B29 to B31). Use only this file.

This file lives on branch `claude/260-cli-runtime` until that branch is merged. If step A2 shows a different branch or `ls _docs/drill-video-steps.md` fails, run these (once):
```bash
git remote set-branches --add origin claude/260-cli-runtime
git fetch origin claude/260-cli-runtime
git checkout claude/260-cli-runtime
```
Expect: `branch 'claude/260-cli-runtime' set up to track 'origin/claude/260-cli-runtime'.` (The first line is needed if your clone was made with `--single-branch`; it is harmless otherwise.)
After the branch is merged into `main`, use `git checkout main` instead and `git pull --ff-only`.

Setup: WSL2 Ubuntu bash, repo at `~/clone/vuln-triage`, your own Claude login (Pro plan). Paste one block per step. Stay in `~/clone/vuln-triage` unless a step says otherwise. Part A and steps marked OFF CAMERA are not recorded. If you get stuck, tell the step number (for example "B13") and the last output.

Never show on camera: `.env`, anything in `.scratch/` except `responder.log`, the Grafana password, the GitHub token, the output of `docker compose config`, the output of `env`.

## PREREQUISITES (have these ready before A1)

- A GitHub fine-grained token for the responder: github.com, Settings, Developer settings, Fine-grained personal access tokens, Generate new token. Only select repositories: `andrew-chung-au/vuln-triage`. Contents: Read and write. Pull requests: Read and write. Administration: No access. Everything else: No access. The token is shown once: store it in a password manager. Never put it in `.env` or any file. (Details: `_docs/responder-token-proof.md`.)
- Claude Code logged in with your own account, and a fresh plan allowance: run `claude`, type `/usage`, check you are well below the limit, then `/exit`.
- Docker running (Docker Desktop with WSL integration, or Docker Engine in WSL).
- Installed in WSL: `uv`, `openssl`, `curl`, `node`, `git`, `claude` (A3 checks).
- `clip.exe` (comes with Windows; used to copy a password without showing it).
- A second terminal window for the log, and a screen recorder on Windows (OBS or Game Bar).

---

## PART A: setup (OFF CAMERA, 20 to 40 minutes the first time)

### A1. Open a NEW terminal and go to the repo
```bash
cd ~/clone/vuln-triage
```
Expect: no output.

### A2. Get the latest code and show the branch
```bash
git branch --show-current
git pull --ff-only
git log --oneline -1
[ "$(git branch --show-current)" = "claude/260-cli-runtime" ] && echo "BRANCH OK" || echo "STOP: you are on the wrong branch. Run the three commands at the top of this file, then repeat A2."
ls _docs/drill-video-steps.md
```
Expect: the branch `claude/260-cli-runtime`, `Already up to date.` or a list of updated files, one commit line, `BRANCH OK`, and `_docs/drill-video-steps.md`. A fresh clone starts on `main`, which does NOT have the drill prompt, the commit-rule fix or the logging, so a run from `main` fails for the wrong reasons: never continue past `STOP`. (Once this branch has been merged into `main`, `main` is the right branch and this check can be ignored.) If `git pull` says local changes would be overwritten or cannot fast-forward: `git status --short`, tell the orchestrator the output, and do not continue. If the file is missing, use the three commands at the top of this file, then repeat A2.

### A3. Check the tools are installed
```bash
for t in docker openssl curl uv node git claude; do command -v $t >/dev/null && echo "ok      $t" || echo "MISSING $t"; done
```
Expect: seven `ok` lines, no `MISSING`.

### A4. Check Docker is running
```bash
docker info --format 'docker server {{.ServerVersion}}'
```
Expect: `docker server ` and a version number. An error means start Docker Desktop (or the Docker service) and repeat.

### A5. Check your Claude login
```bash
claude auth status
```
Expect: `"loggedIn": true` and `"authMethod"` `claude.ai` or `oauth_token`. If not: run `claude auth login`, then repeat A5.

### A6. Check the GitHub token can be read (OFF CAMERA; nothing is saved)
Have the token ready in your password manager. Paste it at the hidden prompt and press Enter.
```bash
read -rsp 'GitHub token (hidden): ' T; echo
curl -s -o /dev/null -w '%{http_code}\n' -H "Authorization: Bearer $T" https://api.github.com/repos/andrew-chung-au/vuln-triage
unset T
```
Expect: `200`. This proves only that the token is valid and can READ the repo. It does not prove it can push or open a pull request: that is proven only by the run itself (if B20 shows `push_failed`, see TROUBLESHOOTING). `401` means a wrong or expired token: create a new one and repeat A6; `404` means the token cannot see the repo (wrong repository selected).

### A7. Check no old exported values are left in this terminal
```bash
compgen -e | grep -E '^(POSTGRES_PASSWORD|GRAFANA_ADMIN_PASSWORD|RESPONDER_[A-Z_]+|VT_[A-Z_]+|COMPOSE_[A-Z_]+|DEPLOYMENT_ENVIRONMENT|MAIL_[A-Z_]+|LLM_MODE|ANTHROPIC_[A-Z_]+|CI|GITHUB_ACTIONS)$' || echo none
```
Expect: `none`. If names are listed: close the terminal, open a new one, repeat from A1.

### A8. Install the responder
```bash
make responder-install
```
Expect: it ends without an error line. Wait: 1 to 3 minutes.

### A9. Write `.env` (any old `.env` is moved aside, not overwritten)
```bash
mkdir -p .scratch
if [ -f .env ]; then mv .env ".env.bak-$(date +%Y%m%d-%H%M%S)"; echo "old .env moved aside"; fi
PG=$(openssl rand -hex 24)
GF=$(openssl rand -hex 24)
API=$(openssl rand -hex 24)
WH=$(openssl rand -hex 24)
cat > .env <<EOF
POSTGRES_PASSWORD=$PG
GRAFANA_ADMIN_PASSWORD=$GF
RESPONDER_API_TOKEN=$API
VT_RESPONDER_WEBHOOK_TOKEN=$WH
VT_ALERT_HUMAN_EMAIL=oncall@drill.test
MAIL_SENDER=vulntriage@sender.example
VT_RESPONDER_WEBHOOK_URL=http://host.docker.internal:9100/webhook/grafana
VT_DEMO_DEFECT=notify_no_fix
LLM_MODE=stub
RESPONDER_MODE=stub
COMPOSE_PROJECT_NAME=vt-drill
COMPOSE_FILE=compose.yaml:compose.telemetry.yaml:compose.alert.yaml:.scratch/compose.drill-defect.yaml
EOF
chmod 600 .env
unset PG GF API WH
echo ".env written"
```
Expect: `.env written` (and `old .env moved aside` if you had one).

### A10. Check `.env` has 12 lines
```bash
grep -c '=' .env
```
Expect: `12`.

### A11. Write the Compose override file
```bash
cat > .scratch/compose.drill-defect.yaml <<'YAML'
services:
  backend:
    environment:
      VT_DEMO_DEFECT: ${VT_DEMO_DEFECT:-}
  grafana:
    extra_hosts:
      - "host.docker.internal:host-gateway"
YAML
echo override written
```
Expect: `override written`.

### A12. Check Compose accepts the files and `.env`
```bash
docker compose config --quiet && echo "compose config OK"
```
Expect: `compose config OK` and no message about a missing or required variable. (Never run `docker compose config` without `--quiet`: it prints secrets.)

### A13. Write the responder start script
```bash
cat > .scratch/start-responder.sh <<'SH'
#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
if [ -f .scratch/responder.pid ] && kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null; then
  echo "responder already running (pid $(cat .scratch/responder.pid)); stop it first (C1)"; exit 1
fi
set -a; source ./.env; set +a
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN ANTHROPIC_BASE_URL DEPLOYMENT_ENVIRONMENT CI GITHUB_ACTIONS
unset POSTGRES_PASSWORD GRAFANA_ADMIN_PASSWORD COMPOSE_FILE COMPOSE_PROJECT_NAME VT_DEMO_DEFECT LLM_MODE MAIL_SENDER VT_ALERT_HUMAN_EMAIL
export RESPONDER_WEBHOOK_SECRET="$VT_RESPONDER_WEBHOOK_TOKEN"
export RESPONDER_MODE=real
export RESPONDER_RUNTIME=cli
export RESPONDER_MODEL=claude-sonnet-5-5
export RESPONDER_API_URL=http://127.0.0.1:8000
export RESPONDER_GITHUB_REPO=andrew-chung-au/vuln-triage
export RESPONDER_STATE_FILE="$PWD/.scratch/responder-state/handled-fingerprints.json"
mkdir -p .scratch/responder-state
read -rsp 'GitHub token for the responder (hidden, not saved): ' RESPONDER_GITHUB_TOKEN
echo
export RESPONDER_GITHUB_TOKEN
nohup responder/.venv/bin/python -m uvicorn --app-dir responder \
  vt_responder.app:create_app_from_env --factory --host 0.0.0.0 --port 9100 \
  > .scratch/responder.log 2>&1 &
echo $! > .scratch/responder.pid
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:9100/webhook/grafana \
    -H 'Authorization: Bearer wrong' -H 'Content-Type: application/json' -d '{}' || true)
  [ "$code" = "401" ] && { echo "responder up (pid $(cat .scratch/responder.pid)); wrong bearer correctly refused with 401"; exit 0; }
  kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null || break
  sleep 2
done
echo "responder did NOT start; last log lines:"; tail -n 15 .scratch/responder.log; exit 1
SH
chmod +x .scratch/start-responder.sh
echo written
```
Expect: `written`.

### A14. Write the value-check script
```bash
cat > .scratch/check-values.sh <<'SH'
#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
set -a; source ./.env; set +a
BAD=0
h() { if [ -z "$1" ]; then echo "EMPTY"; else printf %s "$1" | sha256sum | cut -c1-6; fi; }
same() {
  if [ "$2" = "$3" ] && [ "$2" != "EMPTY" ]; then echo "OK        $1 ($2)"; else echo "MISMATCH  $1 (A=$2 B=$3)"; BAD=1; fi
}
cenv() { docker compose exec -T "$1" sh -c "printf %s \"\$$2\""; }
penv() { tr '\0' '\n' < "/proc/$1/environ" | grep "^$2=" | cut -d= -f2-; }
A=$(h "$VT_RESPONDER_WEBHOOK_TOKEN")
B=$(h "$RESPONDER_API_TOKEN")
same "grafana container VT_RESPONDER_WEBHOOK_TOKEN vs .env" "$A" "$(h "$(cenv grafana VT_RESPONDER_WEBHOOK_TOKEN)")"
same "backend container RESPONDER_API_TOKEN vs .env" "$B" "$(h "$(cenv backend RESPONDER_API_TOKEN)")"
PID=$(cat .scratch/responder.pid 2>/dev/null || true)
if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
  same "responder process RESPONDER_WEBHOOK_SECRET vs .env webhook token" "$A" "$(h "$(penv "$PID" RESPONDER_WEBHOOK_SECRET)")"
  same "responder process RESPONDER_API_TOKEN vs .env" "$B" "$(h "$(penv "$PID" RESPONDER_API_TOKEN)")"
  echo "responder: MODE=$(penv "$PID" RESPONDER_MODE) MODEL=$(penv "$PID" RESPONDER_MODEL) RUNTIME=$(penv "$PID" RESPONDER_RUNTIME) API_URL=$(penv "$PID" RESPONDER_API_URL)"
  echo "responder ANTHROPIC_API_KEY: $(penv "$PID" ANTHROPIC_API_KEY | wc -c | tr -d ' ') chars (expect 0)"
else
  echo "MISMATCH  responder is not running"; BAD=1
fi
echo "backend: VT_DEMO_DEFECT=$(cenv backend VT_DEMO_DEFECT) RESPONDER_MODE=$(cenv backend RESPONDER_MODE) VT_FEEDS=$(cenv backend VT_FEEDS) DEPLOYMENT_ENVIRONMENT=$(cenv backend DEPLOYMENT_ENVIRONMENT)"
echo "grafana to responder (wrong bearer, expect 401):"
docker compose exec -T grafana sh -c 'wget -S -O /dev/null --header="Authorization: Bearer wrong" --post-data="{}" "$VT_RESPONDER_WEBHOOK_URL"' 2>&1 | grep -E 'HTTP/|can.t connect|bad address|refused|timed out' || echo "no answer line"
claude auth status | grep -E 'loggedIn|authMethod'
[ "$BAD" = "0" ] && echo "ALL VALUE CHECKS PASSED" || echo "SOMETHING DOES NOT MATCH: see TROUBLESHOOTING"
SH
chmod +x .scratch/check-values.sh
echo written
```
Expect: `written`.

### A15. Stop any old drill responder, remove old drill containers, volumes and files
```bash
if [ -f .scratch/responder.pid ] && kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null; then kill "$(cat .scratch/responder.pid)"; for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null || break; sleep 1; done; fi
docker compose -p vt-drill down --volumes --remove-orphans
rm -rf .scratch/responder-state .scratch/responder.pid .scratch/responder.log .scratch/cookie.txt .scratch/login.hdr .scratch/findings.json .scratch/events.base
echo clean
```
Expect: `clean` (earlier lines may say nothing to remove).

### A16. Check no other program holds a drill port
```bash
docker ps --format '{{.Names}}  {{.Ports}}' | grep -E ':(3000|8000|8025|9090|9099|1025|4317|3100|3200)->' || echo "no port conflicts"
ss -ltn | grep -E ':(3000|8000|9090|9100|8025) ' || echo "no listeners"
```
Expect: `no port conflicts` and `no listeners`. A listed container: `docker stop <name>`; a listed listener: `ss -ltnp | grep <port>` and stop that program; then repeat A16.

### A17. Download the images
```bash
docker compose pull db otel-collector prometheus tempo loki grafana mailhog
```
Expect: ends without an error. Wait: 2 to 10 minutes.

### A18. Build the app images
```bash
docker compose build backend migrations webhook-sink
```
Expect: ends without an error. Wait: 3 to 10 minutes the first time.

---

## PART B: the recording

### B1. Go to the repo in Terminal 1
```bash
cd ~/clone/vuln-triage
```
Expect: no output. (Part B may be a new terminal; Terminal 1 stays the main one.)

### B2. Arrange the screen and start recording (Windows side: OBS or Game Bar)
Terminal 1 (this one), a second terminal for the log (B10), and browser tabs open to: `http://localhost:3000`, `http://localhost:8025`, `http://localhost:9090`, and your GitHub repo pull requests.
Expect: all visible; recording running.

### B3. Show the date and commit
```bash
date
git log --oneline -1
```
Expect: today's date and the latest commit line.

### B4. Start everything except Grafana
```bash
docker compose up -d --wait --wait-timeout 300 db migrations otel-collector prometheus tempo loki mailhog webhook-sink backend
```
Expect: it returns to the prompt with no error. Wait: up to 2 minutes (the command itself waits and stops with an error after 5).

### B5. Show the containers
```bash
docker compose ps -a
```
Expect: `db` and `backend` `healthy`; `migrations` `Exited (0)`; the others `running` (Grafana and the frontend are not listed yet or not started). Evidence: screenshot.

### B6. Wait for the metric to exist in Prometheus
```bash
for i in $(seq 1 60); do curl -fsS 'http://localhost:9090/api/v1/query?query=vt_top_tier_notification_overdue' | grep -q '"result":\[{' && { echo "metric present after about $(((i-1)*5))s"; break; }; sleep 5; done
```
Expect: `metric present after about 0s` to `75s`. Wait: up to 75 seconds (metric export every 60 s plus a 15 s scrape; gives up after 300 s).

### B7. Start Grafana (last, so no "no data" alert fires)
```bash
docker compose up -d --wait --wait-timeout 300 grafana
```
Expect: returns to the prompt with no error. Wait: under 1 minute.

### B8. Show the planted defect is ON
```bash
docker compose exec -T backend sh -c 'echo "VT_DEMO_DEFECT=$VT_DEMO_DEFECT VT_FEEDS=$VT_FEEDS RESPONDER_MODE=$RESPONDER_MODE"'
```
Expect: `VT_DEMO_DEFECT=notify_no_fix VT_FEEDS=fixtures RESPONDER_MODE=stub`. Evidence: screenshot.

### B9. Start the real responder in the background (before the asset; Grafana sends the alert only once)
Have the GitHub token ready to paste from your password manager (the same token as A6).
```bash
bash .scratch/start-responder.sh
```
Expect: a prompt `GitHub token for the responder (hidden, not saved):`. Paste the token (nothing appears) and press Enter. Then: `responder up (pid NNNN); wrong bearer correctly refused with 401`. Wait: up to 60 seconds.

### B10. Second terminal: follow the responder log
Open a second terminal and paste:
```bash
cd ~/clone/vuln-triage
tail -n 20 -f .scratch/responder.log
```
Expect: a few log lines, no `Traceback`. Leave it on screen. Go back to Terminal 1.

### B11. OFF CAMERA (pause recording): check all values match
```bash
bash .scratch/check-values.sh
```
Expect: four `OK` lines; `responder: MODE=real MODEL=claude-sonnet-5-5 RUNTIME=cli API_URL=http://127.0.0.1:8000`; `ANTHROPIC_API_KEY: 0 chars`; `backend: VT_DEMO_DEFECT=notify_no_fix RESPONDER_MODE=stub VT_FEEDS=fixtures DEPLOYMENT_ENVIRONMENT=test`; a line containing `HTTP/1.1 401`; `loggedIn` true; last line `ALL VALUE CHECKS PASSED`. Any `MISMATCH` or a line without 401: go to TROUBLESHOOTING, do not continue. Resume recording.

### B12. Create the dashboard user
```bash
printf '%s\n' 'drill-not-a-secret' | docker compose exec -T backend python -m vulntriage.manage create-user --username drill-lead --display-name "Drill Lead" --email lead@drill.test --role "security lead"
```
Expect: `created user 'drill-lead' (id 1, role 'security lead')`.

### B13. Log in through the API
```bash
curl -sS -D .scratch/login.hdr -o /dev/null -X POST http://127.0.0.1:8000/auth/login -H 'Content-Type: application/json' -d '{"username":"drill-lead","password":"drill-not-a-secret"}'
grep -i '^set-cookie: vt_session=' .scratch/login.hdr | sed -E 's/^[Ss]et-[Cc]ookie: (vt_session=[^;]+).*/\1/' | tr -d '\r\n' > .scratch/cookie.txt
test -s .scratch/cookie.txt && echo "logged in, cookie saved" || echo "LOGIN FAILED"
```
Expect: `logged in, cookie saved`.

### B14. Register the failing asset (this starts the scan)
```bash
curl -sS -w '\nHTTP %{http_code}\n' -X POST http://127.0.0.1:8000/assets -H 'Content-Type: application/json' -H 'X-Requested-With: XMLHttpRequest' -H "Cookie: $(cat .scratch/cookie.txt)" -d '{"name":"pip-app","ownerName":"Owner","ownerEmail":"pip-owner@team.example","criticality":"high","internetFacing":true,"repositoryUrl":"https://github.com/fixture-owner/pip-app"}'
```
Expect: JSON with `"id":"1"` and `"name":"pip-app"`, then `HTTP 201`. Evidence: screenshot.

### B15. Confirm the scan found a top-tier finding with no fix
```bash
for i in $(seq 1 30); do curl -sS http://127.0.0.1:8000/findings -H "Cookie: $(cat .scratch/cookie.txt)" > .scratch/findings.json; grep -q '"package":"flask"' .scratch/findings.json && { grep -o '"id":"[0-9]*"\|"tier":"[^"]*"\|"fixedVersion":[^,}]*' .scratch/findings.json | head -n 6; break; }; sleep 4; done
```
Expect: lines including `"tier":"P1"` and `"fixedVersion":null`. Wait: a few seconds (gives up after 120 s).

### B16. Watch the metric reach 1
```bash
for i in $(seq 1 60); do out=$(curl -sS --get 'http://localhost:9090/api/v1/query' --data-urlencode 'query=vt_top_tier_notification_overdue == 1'); echo "$out" | grep -q '"result":\[{' && { echo "$out" | grep -o '"metric":{[^}]*}\|"value":\[[^]]*\]'; echo "metric = 1 after about $(((i-1)*10))s"; break; }; sleep 10; done
```
Expect: a `"metric"` with `finding_id` and `"tier":"P1"`, a `"value"` ending `"1"`, then `metric = 1 after about ...s`. Wait: about 1 to 2 minutes (delivery job fails within 30 s, metric export up to 60 s, scrape 15 s; gives up after 10 minutes).
Evidence (runbook step 2): in the browser open `http://localhost:9090`, query `vt_top_tier_notification_overdue == 1`, Table tab, screenshot showing value 1.

### B17. Copy the Grafana password to the Windows clipboard (without showing it)
```bash
grep '^GRAFANA_ADMIN_PASSWORD=' .env | cut -d= -f2- | tr -d '\n' | clip.exe && echo copied
```
Expect: `copied`. If `clip.exe` is not found: pause recording, open `.env` in an editor, copy the value after `GRAFANA_ADMIN_PASSWORD=`, close the editor, resume. Do not copy anything else before B18. After the recording, clear the Windows clipboard history (Win+V, then "Clear all"), because it keeps the GitHub token from B9 and this password.

### B18. Show the Grafana alert
Browser: `http://localhost:3000`, user `admin`, paste the password (Ctrl+V), then menu Alerting, Alert rules.
Expect: rule "Top-tier owner notification overdue" in state Firing with one instance showing the `finding_id`. Wait: up to 2 minutes after B16 (rule checks every 1 minute). Evidence (runbook step 3): screenshot.

### B19. Wait for the alert email
```bash
for i in $(seq 1 60); do n=$(curl -sS http://localhost:8025/api/v2/messages | grep -o '"total":[0-9]*' | head -n 1); echo "mailhog $n"; [ "$n" = '"total":1' ] && break; sleep 10; done
```
Expect: `mailhog "total":1` at the end. Wait: up to 2 minutes (gives up after 10 minutes).
Then browser `http://localhost:8025`: one email to `oncall@drill.test`, subject starting `[FIRING:1]`. Evidence (runbook step 3): screenshot the inbox and the open email. Do not expect an email to `pip-owner@team.example` yet.

### B20. Wait for the responder to open the pull request
```bash
B=$(cat .scratch/events.base 2>/dev/null || echo 0)
for i in $(seq 1 80); do n=$(grep -cE '"event": ?"(pull_request_opened|run_failed|no_change|retry_cap_reached)"' .scratch/responder.log); [ "$n" -gt "$B" ] && { grep -E '"event": ?"(pull_request_opened|run_failed|no_change|retry_cap_reached)"' .scratch/responder.log | tail -n 1 | grep -oE '"(event|reason|pull_request|explanation)": ?"[^"]*"'; break; }; sleep 10; done
```
(This waits for a NEW result line, so it also works after a replay; it prints only the event, and the reason, explanation or PR URL.) Expect: `"event": "pull_request_opened"` and a `"pull_request"` URL. Wait: starts within seconds of the alert; the run is limited to 10 minutes plus checkout and push: allow up to 13 minutes (the Pro-plan duration is unverified). A `run_failed` or `no_change` line: see TROUBLESHOOTING. No line after 13 minutes: look at Terminal 2.
Evidence (runbook step 4): screenshot Terminal 2 showing `run_started` (with `model`), `branch_pushed`, `pull_request_opened`.

### B21. Open the pull request
Browser: open the `pull_request` URL from B20.
Expect: a PR from branch `responder/...` with a code fix and a new test in "Files changed". Evidence: screenshot.

### B22. Merge the pull request
Browser: click "Merge pull request", then confirm.
Wait: until the PR checks are green (several minutes); the Merge button stays disabled until then. If Merge stays blocked or a check is red: open the PR's Checks tab and tell the orchestrator the name of the failing check. Merging triggers the project's auto-deploy to dev (README CI/CD row): this is expected.
Expect: "Pull request successfully merged and closed". Evidence (runbook step 5): screenshot.

### B23. Turn the defect off in `.env`
```bash
sed -i 's/^VT_DEMO_DEFECT=.*/VT_DEMO_DEFECT=/' .env
grep '^VT_DEMO_DEFECT=' .env
```
Expect: `VT_DEMO_DEFECT=` (nothing after the equals sign).

### B24. Restart the backend with the defect off
```bash
docker compose up -d --force-recreate --no-deps --wait --wait-timeout 300 backend
docker compose exec -T backend sh -c 'echo "VT_DEMO_DEFECT=[$VT_DEMO_DEFECT]"'
```
Expect: `VT_DEMO_DEFECT=[]`. Wait: 30 to 60 seconds. Evidence: screenshot.

### B25. Wait for the owner email
```bash
for i in $(seq 1 40); do n=$(curl -sS http://localhost:8025/api/v2/messages | grep -o '"total":[0-9]*' | head -n 1); echo "mailhog $n"; [ "$n" = '"total":2' ] && break; sleep 10; done
```
Expect: `mailhog "total":2` at the end. Wait: 30 to 90 seconds (the failed job is retried at the delivery worker's next 30-second poll; gives up after 400 s).
Then browser `http://localhost:8025`: open the new email to `pip-owner@team.example`. Evidence (runbook step 6): screenshot.

### B26. Wait for the metric to return to 0
```bash
for i in $(seq 1 60); do out=$(curl -sS --get 'http://localhost:9090/api/v1/query' --data-urlencode 'query=vt_top_tier_notification_overdue == 1'); echo "$out" | grep -q '"result":\[\]' && { echo "no series at 1 after about $(((i-1)*10))s"; break; }; sleep 10; done
curl -sS --get 'http://localhost:9090/api/v1/query' --data-urlencode 'query=vt_top_tier_notification_overdue' | grep -o '"value":\[[^]]*\]'
```
Expect: `no series at 1 after about ...s`, then `"value"` lines ending in `"0"`. Wait: about 75 seconds (gives up after 10 minutes). Evidence: screenshot of the Prometheus web page (browser, `http://localhost:9090`, not Grafana and not the terminal): enter the query `vt_top_tier_notification_overdue` (without `== 1`), click Execute, open the Table tab, and capture the value `0`.

### B27. Show the resolved alert
Browser: Grafana, Alerting, Alert rules, refresh.
Expect: the rule state is Normal. Terminal 2 shows `alert_ignored` with `"outcome": "resolved"` and no new `run_started`. Wait: up to 5 minutes after B25 (rule check 1 minute, then notification at the 1-minute group interval). Evidence (runbook step 7): screenshot Grafana and Terminal 2.

### B28. Stop the recording and save the file
Expect: the video file exists. Upload it and add the link to the README placeholders and #163 (runbook step 8). Keep the stack running for B29 and B30.

### B29. Dashboard re-capture (runbook Part 2; stack must still be up; screenshots only)
Browser: `http://localhost:3000/d/us13-journey/us-13-journey` (already loaded by Grafana). Set the time range to "Last 1 hour". Use the viewing mode (the dashboard is not in edit mode). Take a screenshot of the whole dashboard and save it as a PNG (for example in your Windows Downloads folder).
Expect: three panes visible (metric, Tempo traces, Loki logs) with no stale Environment or Version dropdowns. Then copy the PNG over the committed screenshot (replace `YOUR_WINDOWS_USER` and `YOUR_FILE.png`, and keep the double quotes because Windows screenshot names contain spaces; the block refuses to run until you do):
```bash
SHOT="/mnt/c/Users/YOUR_WINDOWS_USER/Downloads/YOUR_FILE.png"
if [ -f "$SHOT" ]; then cp "$SHOT" docs/images/g9-grafana-dashboard-dev-local.png && echo "screenshot copied"; else echo "EDIT SHOT FIRST: file not found"; fi
```
Expect: `screenshot copied`. (Committing it is a separate task for the orchestrator.)

### B30. Metric to trace and trace to logs (runbook Part 2; stack still up)
Browser, Grafana: Explore, data source Prometheus, query `vt_notifications_total`, switch "Exemplars" on, hover a dot and click the trace link. Then in the Tempo trace click a span and "Logs for this span".
Expect: the Tempo trace opens and the span links to the matching Loki log line. If the exemplar dot or the link does not appear, take one screenshot of what you see and move on (the README already says the metric-to-trace leg is checked in CI). Evidence: screenshot of whatever appears.

### B31. Ruleset screenshot (runbook Part 3; GitHub only)
Browser: github.com, the repo, Settings, Rules, Rulesets, `protect-main`. Expand "Require status checks to pass" so the check names are visible.
Expect: the required check names are visible. Evidence: screenshot to replace `docs/images/g5-github-settings-rulesets-protect-main.png`.

---

## PART C: cleanup (OFF CAMERA)

### C1. Stop the responder
```bash
cd ~/clone/vuln-triage
if [ -f .scratch/responder.pid ] && kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null; then kill "$(cat .scratch/responder.pid)"; for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null || break; sleep 1; done; fi
sleep 3
kill -0 "$(cat .scratch/responder.pid)" 2>/dev/null && echo "STILL RUNNING" || echo "responder stopped"
```
Expect: `responder stopped`.

### C2. Stop the stack and delete its data
```bash
docker compose -p vt-drill down --volumes --remove-orphans
```
Expect: containers, network and volumes reported `Removed`.

### C3. Empty `.scratch`
```bash
make clean-scratch
```
Expect: `.scratch/ is now empty`.

### C4. Remove the drill `.env`
```bash
rm -f .env
test ! -e .env && echo "no .env left"
ls -a | grep -E '^\.env\.bak' || true
```
Expect: `no .env left`, then either nothing or a `.env.bak-<date>` file (your old `.env`; restore it with `mv .env.bak-<date> .env`).

### C5. Log out of Claude (only if this login was only for the drill)
```bash
claude auth logout
```
Expect: a logged-out message.

---

## TROUBLESHOOTING (find the exact text)

| You see | Do |
|---|---|
| `RESPONDER_WEBHOOK_SECRET is required` | `grep -c '^VT_RESPONDER_WEBHOOK_TOKEN=' .env` must print 1; start the responder only with `bash .scratch/start-responder.sh` |
| `RESPONDER_API_TOKEN is required` | `grep -c '^RESPONDER_API_TOKEN=' .env` must print 1; same script |
| `RESPONDER_MODE must be 'stub' in test and CI` | a `CI`, `GITHUB_ACTIONS` or `DEPLOYMENT_ENVIRONMENT=test` value reached the script; do not add them to `.env`; open a new terminal and repeat from A1 |
| `RESPONDER_GITHUB_TOKEN is required in real mode` | you pressed Enter on an empty token; run C1 then B9 again |
| `RESPONDER_GITHUB_REPO must be 'owner/name'` | re-run A13 |
| a line starting `the 'claude' CLI` | `claude auth login` with your Claude account, then `claude auth status` (A5); `ANTHROPIC_API_KEY` must not be set; then B9 |
| `required variable ... is missing a value` or `set VT_RESPONDER_WEBHOOK_URL` | you are not in `~/clone/vuln-triage`, or `.env` is missing: `cd ~/clone/vuln-triage`, redo A9 |
| `compose.drill-defect.yaml: no such file` | redo A11 |
| `password authentication failed` | old database volume: `docker compose -p vt-drill down --volumes`, then redo B4 |
| backend exits with `VT_DEMO_DEFECT=notify_no_fix is refused unless DEPLOYMENT_ENVIRONMENT` | `grep '^COMPOSE_FILE=' .env` must match A9 exactly |
| B11 `MISMATCH grafana container` | `docker compose up -d --force-recreate --no-deps grafana`, repeat B11 |
| B11 `MISMATCH responder process` or `responder is not running` | C1, then B9, then B11 |
| B11 grafana line `can't connect to remote host` or `refused` or `timed out` | responder not running or Windows/host firewall blocks port 9100: allow it, `ss -ltn | grep 9100` must show `0.0.0.0:9100`, repeat B11 |
| B11 grafana line `bad address 'host.docker.internal'` | redo A11, then `docker compose up -d --force-recreate --no-deps grafana`, repeat B11 |
| B11 grafana line `HTTP/1.1 404` or `403` | another program uses port 9100: `ss -ltnp | grep 9100`, stop it, C1, B9 |
| B11 grafana line `no answer line` | run `curl -s -o /dev/null -w '%{http_code}\n' -X POST http://127.0.0.1:9100/webhook/grafana -H 'Authorization: Bearer wrong' -d '{}'`: `401` means the responder is fine; report the Grafana line to the orchestrator |
| Grafana contact point error `401` or `Unauthorized` | repeat B11 and fix the `MISMATCH` line |
| Grafana contact point error `connection refused` or `no such host` | see the B11 grafana-line rows above |
| B15 prints nothing | `curl -sS -o /dev/null -w 'rescan HTTP %{http_code}\n' -X POST http://127.0.0.1:8000/assets/1/rescan -H 'X-Requested-With: XMLHttpRequest' -H "Cookie: $(cat .scratch/cookie.txt)"` must print `rescan HTTP 202`, then repeat B15 |
| B16 never reaches 1 | repeat B8 (must be `notify_no_fix`) and B15 (must show `"fixedVersion":null`); `docker compose logs --tail 50 backend` |
| B19 stays at `"total":0` while the metric is 1 | `docker compose logs --tail 50 grafana`; Alerting, Contact points in Grafana |
| `plan_usage_limit` (in `run_failed`) | Pro allowance used up: wait for the reset (`/usage` in `claude`), then use the replay block below |
| `max_turns` | C1; `echo 'RESPONDER_MAX_TURNS=40' >> .env`; B9; replay |
| `agent_timeout` | C1; `echo 'RESPONDER_RUN_TIMEOUT_SECONDS=900' >> .env`; B9; replay |
| `push_failed` or `pull_request_create_failed` | the GitHub token lacks push or pull-request rights (A6 only proved read): create a token with the PREREQUISITES settings, C1, B9 with the new token, replay |
| `no_change` | the alert reached the responder without a usable finding, or the run decided there was nothing to fix. The alert fires only once: check B8 (defect ON) and B15 (finding present), then replay once |
| `agent_escalated` | the agent decided not to fix. The agent is told that code gated by `VT_DEMO_DEFECT` is a deliberately planted defect for this drill, so it should fix that one and escalate only for a failure that does not trace to it. Look at the `explanation` text in the log line. Replay once; if it escalates again, paste the whole `run_failed` line, including `explanation` and `denied_calls`, to the orchestrator |
| `denied_calls` shows the plain `git commit -m "..."` | a deny rule over-matches in the real CLI (the tab/VT/FF/CR patterns did this until 2026-10-28). Pull the latest, re-run B9, then `responder/.venv/bin/python .scratch/rule_probe.py --only V0 --extra V0` and send the table |
| any `run_failed` line with a non-empty `denied_calls` | `denied_calls` lists the tool calls the safety rules refused (for example a `git commit` message with a forbidden character). Paste that field, with the `reason`, to the orchestrator; do not change any rule yourself |
| other `run_failed` `reason` (`diff_path_*`, `no_commits`, `too_many_commits`, `output_unparseable`, `result_line_missing`, `agent_cli_error`, `cli_exit_nonzero`, `checkout_failed`, `install_failed`) | replay once; if it fails again, stop and send the `reason` (meanings: `_docs/responder-cli-runtime.md`) |
| `retry_cap_reached` or `alert_ignored` with `"outcome": "repeat"` | C1; `rm -rf .scratch/responder-state`; B9; replay |

Replay the alert to the responder (Grafana does not resend it). Copy `fingerprint` and `finding_id` from the `run_failed` or `no_change` line in `.scratch/responder.log`, replace the two `PASTE_...` values, then paste. It refuses to run until both are replaced (unverified; body shape from `tests/compose_responder.py`):
```bash
FP=PASTE_FINGERPRINT_HERE
FID=PASTE_FINDING_ID_HERE
if [ "${FP#PASTE_}" != "$FP" ] || [ "${FID#PASTE_}" != "$FID" ]; then
  echo "STOPPED: replace PASTE_FINGERPRINT_HERE and PASTE_FINDING_ID_HERE first"
else
  grep -cE '"event": ?"(pull_request_opened|run_failed|no_change|retry_cap_reached)"' .scratch/responder.log > .scratch/events.base || true
  WH=$(grep '^VT_RESPONDER_WEBHOOK_TOKEN=' .env | cut -d= -f2-)
  curl -sS -X POST http://127.0.0.1:9100/webhook/grafana -H "Authorization: Bearer $WH" -H 'Content-Type: application/json' -d "{\"status\":\"firing\",\"alerts\":[{\"status\":\"firing\",\"fingerprint\":\"$FP\",\"labels\":{\"finding_id\":\"$FID\",\"tier\":\"P1\"}}]}"
  unset WH
fi
```
Expect: `{"results":[{"fingerprint":"...","outcome":"accepted"}]}` and a new `run_started` in Terminal 2.

## Value map (reference)

| Variable | Where it is set | Who reads it |
|---|---|---|
| `POSTGRES_PASSWORD` | `.env` | `compose.yaml` db, migrations, backend |
| `GRAFANA_ADMIN_PASSWORD` | `.env` | Grafana (required by `observability/compose.yaml` and `compose.alert.yaml`); copied to the clipboard in B17 |
| `RESPONDER_API_TOKEN` | `.env` | backend; the responder script uses the same value |
| `VT_RESPONDER_WEBHOOK_TOKEN` | `.env` | Grafana; the script copies it to `RESPONDER_WEBHOOK_SECRET` |
| `VT_RESPONDER_WEBHOOK_URL`, `VT_ALERT_HUMAN_EMAIL` | `.env` | `compose.alert.yaml` (required) |
| `MAIL_SENDER` | `.env` | Grafana SMTP sender |
| `VT_DEMO_DEFECT` | `.env` | backend, through `.scratch/compose.drill-defect.yaml` |
| `LLM_MODE`, `RESPONDER_MODE` (`stub`) | `.env` | `compose.yaml` backend only |
| `COMPOSE_PROJECT_NAME`, `COMPOSE_FILE` | `.env` | Docker Compose |
| `VT_FEEDS=fixtures`, `DEPLOYMENT_ENVIRONMENT=test` | `compose.telemetry.yaml` (fixed) | backend; not in `.env` on purpose (the responder refuses real mode when `DEPLOYMENT_ENVIRONMENT=test`) |
| `RESPONDER_MODE=real`, `RESPONDER_RUNTIME`, `RESPONDER_MODEL`, `RESPONDER_API_URL`, `RESPONDER_GITHUB_REPO`, `RESPONDER_STATE_FILE` | `.scratch/start-responder.sh` | the responder only |
| `RESPONDER_MAX_TURNS`, `RESPONDER_RUN_TIMEOUT_SECONDS` (optional) | appended to `.env` only when TROUBLESHOOTING says so | the responder (the script sources `.env`) |
| `RESPONDER_GITHUB_TOKEN` | typed at the hidden prompt in B9 (A6 only tests it) | the responder only; never written to a file |
