# Runbook: deploy and tear down the dev server

Issue: #240 (Deploy item D23). This file follows `_docs/agent-kit/templates/runbook.md` for each recurring problem (Symptom, Check, Fix, Undo) and `.kiro/steering/evidence-and-steps.md`, rule 3 (one command per block, what to see, what to do if it differs). Since 2026-11-17 every command block can be copied exactly (see "What changed in these steps (2026-11-17)").

**Status: written before the first dev deploy; nothing here has been run, except where a line says "seen" (section 3.1, seen at the first dev deploy on 2026-11-16).** Every `Expected:` line is what the author expects, not something seen, as `terraform/README.md` says of its own steps (`terraform/README.md`, "Steps for the human (not yet run)"). A line that was seen says "seen" and the date. `VERIFY:` marks a fact only the first dev deploy settles; it names who settles it. The first dev deploy is stage (b) of #237 (`_human-tasks/2026-11-15T1822Z-human-task-237-engineer-first-deploy.md`). The CI deploy path runs since #238 (PR #343; the first deploy from CI is [run 43979237337](https://github.com/andrew-chung-au/socboard/actions/runs/43979237337), 2026-11-16, `README.md`, "Deploy to dev").

**Prod has its own steps, not in this file.** Prod exists since #267: its first deploy by hand is in `_human-tasks/2026-11-17T0030Z-human-task-267-engineer-first-prod-deploy.md`, and a promotion or rollback of prod is the workflow of #269 (`.github/workflows/promote-prod.yml`; `_human-tasks/2026-11-16T0332Z-human-task-269-engineer-promote-and-rollback.md`; `README.md`, "Promote to prod"). This runbook's steps are for dev. The Systems Manager document has two parameters, `digest` and `environment` (`dev` or `prod`, default `dev`; #267), so a send for dev may leave `environment` out, and every send below does. Where the prod pieces are torn down: the secret `socboard/app-prod` (section 9, the secrets Decision), the GitHub Environment `deploy-prod` (section 9, the GitHub settings Decision), prod's Caddy site and its data folder `/srv/socboard-data/postgres-prod` (they go with the server and its data volume, `terraform/README.md`, "The prod stack beside dev (issue #266)"). Follow-up: not filed yet (the Planning lane files it; the number goes here).

## What changed in these steps (2026-11-17)

The steps were rewritten for copy and paste after the #267 run (`_human-tasks/2026-11-17T0030Z-human-task-267-engineer-first-prod-deploy.md`, "What changed after the first run"), with no change to what they do, their order or their risks. The old text wrote values as `<instance id>`, `<hostname>`, `<digest>` and `<secret file>`; a person typed those literally and the shell read `<` as a redirect.

- **Before any command** (below) sets four shortcuts once, each read by a command and echoed: `I` (instance id), `H` (dev hostname), `PH` (prod hostname) and `V` (data volume id). Later sections say "with the shortcuts from Before any command".
- A value the runbook cannot read by a command is a placeholder in capitals, such as `PASTE-DIGEST-HERE`. Each one is announced in the sentence before its block, which says what to paste and where it comes from, and the block's `Expected:` line says what the line must look like once it is replaced. Each is echoed before it is used.
- Every `terraform` command uses `-chdir=terraform/...` and is run from the repository root. Sends use JSON parameters, in single quotes: `--parameters '{"digest":["'"$D"'"]}'`.
- The secret file has one fixed path, `/tmp/socboard-dev-secret.json`; its size and mode are checked, and it is deleted after.
- Commands for the server run in a Session Manager session. A shortcut set on your machine does not exist there, so those blocks either need no value or set one inside the session first.
- Stale facts corrected: the CI deploy runs since #238 (PR #343); the Systems Manager document has the `environment` parameter since #267; prod exists since #267 and its promotion is #269's workflow; exit 5 prints the failing step's name and its last 20 redacted lines since #324 (PR #327).

## Contents

1. [Before you start and where things are](#1-before-you-start-and-where-things-are)
2. [Routine deploy](#2-routine-deploy)
3. [Reading a failed run](#3-reading-a-failed-run)
4. [Roll back](#4-roll-back)
5. [Hand reviewers their credentials](#5-hand-reviewers-their-credentials)
6. [Rotate a secret](#6-rotate-a-secret)
7. [Restore from a snapshot](#7-restore-from-a-snapshot)
8. [Certificate failure](#8-certificate-failure)
9. [Teardown](#9-teardown)
10. [What to keep before teardown](#10-what-to-keep-before-teardown)

## Before any command

Do this once in every terminal you open for this runbook. A later section that says "with the shortcuts from Before any command" means these.

- **Where:** a terminal on your own machine, opened at the repository root: `cd ~/projects/socboard`. Every `terraform` command in this file uses `-chdir=terraform/...`, which only works from the root.
- **AWS sign-in:** no command here names a profile; each uses the credentials your shell has (SSO is fine). If you use a named profile, add `--profile NAME` to every `aws` command, or run `export AWS_PROFILE=NAME` once in the terminal. All `aws` commands name the region `us-east-1`.
- **Session Manager:** the steps that run on the server need the Session Manager plugin on your machine (`session-manager-plugin` prints "installed successfully"). Without it, use the AWS Console instead: EC2, select the instance, Connect, Session Manager, Connect. The server has no `aws` command: run `aws` commands on your own machine only.
- **Shortcuts live only in the terminal that set them.** In a new terminal, run this section again. They do not exist inside a Session Manager session on the server; a block for the server either needs no value or sets one in the session first. A send with an empty shortcut fails with `InvalidParameters`, so each shortcut is echoed before it is used. None of them holds a secret, and echoing them is allowed (see "Never do").

Check the repository root first.

```
git rev-parse --show-toplevel
```

Expected: a path that ends in `socboard`, the folder you opened.
If different: any other folder means you are not in the clone. Run `cd ~/projects/socboard` and this block again.

The instance id (it changes when the instance is replaced):

```
I=$(terraform -chdir=terraform/server output -raw instance_id)
```

```
echo "I=[$I]"
```

Expected: `I=[i-` followed by hex digits `]`.
If different: empty brackets mean you are not at the repository root, or Terraform has no state here (not signed in, or the server part is destroyed). Stop.

The dev hostname:

```
H=$(terraform -chdir=terraform/server output -raw hostname)
```

```
echo "H=[$H]"
```

Expected: `H=[` four numbers with dashes, then `.sslip.io]`.
If different: empty brackets: as for `I`.

The prod hostname:

```
PH=$(terraform -chdir=terraform/server output -raw prod_hostname)
```

```
echo "PH=[$PH]"
```

Expected: `PH=[prod-` four numbers with dashes, then `.sslip.io]`.
If different: empty brackets: as for `I`.

The data volume id:

```
V=$(terraform -chdir=terraform/server output -raw data_volume_id)
```

```
echo "V=[$V]"
```

Expected: `V=[vol-` followed by hex digits `]`.
If different: empty brackets: as for `I`.

## Never do

The runbook refuses these commands. Each one prints a secret into a place that outlives the step: the terminal's scroll-back, a Session Manager log (Systems Manager keeps the output of every command sent through it, `README.md`, "Deploy to dev"), or an issue or pull request comment.

- A read of the secret `socboard/app` whose output goes to the terminal. The only allowed form sends it to a file made under `umask 077` outside the repository (`/tmp/socboard-dev-secret.json`), or to the memory-backed folder `/run/socboard-deploy` (mode 0600, `terraform/server/socboard-deploy.sh`, `RUN_DIR` and `umask 077`).
- The command that prints every variable of the shell's environment, and any command that prints the content of an env file or of the file in `/run/socboard-deploy` or of `/tmp/socboard-dev-secret.json`.
- A command that echoes a shell variable holding a secret value. The shortcuts of Before any command and the ones set later (a digest, a command id, a volume id) hold no secret and are echoed on purpose. The one variable this runbook uses that does hold a secret value holds it only inside a single command's own environment (sections 5 and 6.8), is never exported, and is never printed.
- A secret value on a command line (it is visible in the process list and in the shell history), in a file on the data volume or on the root disk (a snapshot of the data volume would back it up, `terraform/README.md`, "The server (instance, network and data volume)", "Rules for later changes"), or in an issue, a pull request, a README or a chat message.
- The command that prints the GitHub CLI's token, and the file of a process's environment under `/proc`.
- The account number, an ARN or a secret value in any record, issue, comment or chat message. No step here prints one, and a result file never holds one.

## 1. Before you start and where things are

You need, on your own machine: the AWS CLI v2 with the Session Manager plugin, `gh` signed in as the repository's admin, `git`, `jq` and a clone of this repository on `main`. Terraform at the version in `terraform/.terraform-version` is needed only for the outputs and for section 9 (`terraform/README.md`, "Terraform version"). Everything runs in `us-east-1` (`_docs/decisions/2026-11-13T2156Z-deploy.md`, part C).

Sign in the way `terraform/README.md`, "Steps for the human in D19b", "Step 1: sign in, and check the account" does, and stop if it does not print the sub-account line. That step uses the profile `socboard` and does not print the account number. The commands below name no profile: they use the one your shell has set (see Before any command).

Where things are. Real values are never written in this file: read them from the outputs, as the table says. `VERIFY:` the human reads them at the first deploy (#237 stage (b)).

| What | Where it is | Source |
|---|---|---|
| The URL, shortcut `H` | output `hostname` of `terraform/server/`: the Elastic IP with dots as dashes, then `.sslip.io`. Prod's is output `prod_hostname`, the same with `prod-` in front, shortcut `PH` | `terraform/README.md`, "What it creates"; `terraform/server/socboard-deploy.sh`, `public_hostname` |
| The instance id, shortcut `I` | output `instance_id` of `terraform/server/`; **changes when the instance is replaced** | `terraform/README.md`, "What it creates" and "Changed user data replaces the instance" |
| The data volume id, shortcut `V` | output `data_volume_id` of `terraform/server/` | `terraform/README.md`, "What it creates" |
| The secret | `socboard/app` in Secrets Manager, `us-east-1`, created by hand with eight keys (prod's is `socboard/app-prod`) | `terraform/server/socboard-deploy.sh`, `SECRET_ID`, `SECRET_REGION`, `NAMES` |
| The deploy document | `socboard-deploy`, two parameters: `digest` matching `^sha256:[0-9a-f]{64}$`, and `environment` (`dev` or `prod`, default `dev`, #267) | `terraform/server/deploy_document.tf` |
| The data folders | `/srv/socboard-data/postgres` (dev), `/srv/socboard-data/postgres-prod` (prod, running since #267), `/srv/socboard-data/caddy` | `terraform/README.md`, "The layout on the volume" (in "What it does"); `terraform/server/socboard-deploy.sh`, `DATA_DIR` |
| The deployed releases | `/opt/socboard/releases/REVISION-12HEX`, and the symlink `/opt/socboard/current` (prod's are under `/opt/socboard/prod`) | `terraform/server/socboard-deploy.sh`, `OPT_DIR`, `ENV_DIR`, `REL`, `link_current` |
| The memory-backed folder | `/run/socboard-deploy`; holds the lock, and the variable file only during a run | `terraform/server/socboard-deploy.sh`, `RUN_DIR`, `VARS`, `cleanup` |

The GitHub Environment variables and secrets, and where each is read:

| Name | Where it lives | Read by | Source |
|---|---|---|---|
| `DEPLOY_INSTANCE_ID` | variable of the `deploy` Environment (and of `deploy-prod`, #269) | the deploy job's send step; refused before any role is assumed if missing or not `i-` and 8 to 17 lower-case hex digits | `README.md`, "Deploy to dev"; `scripts/ci_deploy.py`, `check_environment` |
| `DEPLOY_URL` | variable of the `deploy` Environment (and of `deploy-prod`, #269) | the job's health check; `https://` and a host name only | `README.md`, "Deploy to dev"; `scripts/ci_deploy.py`, `check_environment` |
| `AWS_DEPLOY_ROLE_ARN` | repository secret | the deploy job's role assumption | `README.md`, "Deploy to dev"; `terraform/README.md`, "Outputs" (of "CI access") |
| `AWS_PLAN_ROLE_ARN`, `AWS_APPLY_ROLE_ARN` | repository secrets | the Terraform plan and apply workflows | `terraform/README.md`, "Outputs" (of "CI access") |
| `AWS_DEPLOY_ROLE_ID`, `AWS_PLAN_ROLE_ID` | repository secrets, so GitHub masks the roles' unique ids | the credentials step | `terraform/README.md`, "Prod access"; `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md` |

The eight keys of the secret and where the app reads each (`terraform/server/socboard-deploy.sh`, `NAMES`; `README.md`, "Runtime variables"; `compose.yaml`):

| Key | Used by |
|---|---|
| `SOCBOARD_TOKEN_SECRET` | the app (signs tokens; at least 32 characters) |
| `SOCBOARD_INGEST_API_KEY` | the app (alert ingest; at least 16 characters) and the smoke check |
| `SOCBOARD_SEED_PASSWORD_ANALYST_A`, `SOCBOARD_SEED_PASSWORD_ANALYST_B`, `SOCBOARD_SEED_PASSWORD_LEAD` | `seed` (at least 12 characters; creates a missing user and never changes an existing one); `lead`'s also the smoke check |
| `STACK_PG_SUPERUSER_PASSWORD` | `db` and `db-init` only (`compose.yaml`) |
| `STACK_PG_OWNER_PASSWORD` | `db-init` sets the owner role's password; `migrate` connects with it |
| `STACK_PG_APP_PASSWORD` | `db-init` sets the application role's password; `seed` and `app` connect with it |

### Step 1.1: read the instance id and check it matches the CI variable

With the shortcuts from Before any command. Read the running instance from AWS, as a second source next to Terraform's output:

```
aws ec2 describe-instances --region us-east-1 --filters Name=tag:project,Values=socboard Name=instance-state-name,Values=running --query 'Reservations[].Instances[].InstanceId' --output text
```

Expected: one instance id, `i-` and hex digits, equal to the `I=[...]` you echoed in Before any command. The tag `project=socboard` is on the instance (`terraform/README.md`, "Rules for later changes", "The tag is a contract").
If different: no output means no running instance (it was torn down, stopped or never applied); stop. Two ids mean a second instance exists; stop and find out why. One id that differs from `I` means `I` is stale: run the `I=` block of Before any command again.

```
gh variable list --env deploy --repo andrew-chung-au/socboard
```

Expected: a list with `DEPLOY_INSTANCE_ID` and `DEPLOY_URL`, and the id in `DEPLOY_INSTANCE_ID` equal to the one above (`terraform/README.md`, "Steps for the human in D19b", Step 10). The variables exist: CI has deployed with them since 2026-11-16 (`README.md`, "Deploy to dev").
If different: a different id means it is stale after an instance replacement. Update it with the next block, because every CI deploy fails at the send step until then (`README.md`, "Deploy to dev").
Risk: none, it only reads.

```
gh variable set DEPLOY_INSTANCE_ID --env deploy --repo andrew-chung-au/socboard --body "$I"
```

Expected: `✓ Created variable DEPLOY_INSTANCE_ID for andrew-chung-au/socboard` (or "Updated"). Run this block only when the list above showed a different id.
If different: an empty `I` sets an empty value: run the `I=` and `echo` blocks of Before any command and this block again.
Risk: changes where CI deploys go. Undo: set the old id the same way.


## 2. Routine deploy

Two paths. Both send the document `socboard-deploy` with an image digest; the script does the rest (`terraform/server/deploy_document.tf`; `terraform/README.md`, "The deploy document (`socboard-deploy`)", "What the script does, in order"). The swap is not zero downtime: the app is down from the old container's stop to the new one's first healthy check, usually well under a minute and at most 90 seconds (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 3; `terraform/server/socboard-deploy.sh`, `WAIT=90`). A send that leaves `environment` out deploys dev (the document's default, #267).

### 2.1 By CI

A push to `main` that passes every check and is published deploys that digest to dev, in the `deploy` Environment, and only the newest commit deploys (`_docs/decisions/2026-11-15T2100Z-deploy-dev-from-ci.md`, decisions 1 and 3; `README.md`, "Deploy to dev"). The two Environment variables must be set (Section 1) and `DEPLOY_INSTANCE_ID` is stale after an instance replacement (`terraform/README.md`, "Steps for the human in D19b", Step 10). The workflow `.github/workflows/deploy-dev.yml` is installed and running since #238 (PR #343, `README.md`, "Deploy to dev"), so this path runs on its own.

#### Step 2.1.1: read the result of the newest deploy run

```
gh run list --workflow deploy-dev.yml --repo andrew-chung-au/socboard --limit 5
```

Expected: rows of the workflow `socboard deploy dev` (`.github/workflows/deploy-dev.yml`, `name`); the newest one is `completed` and `success` after a published push to `main`. A run that ended green saying "this publish run published nothing" or "superseded: main has moved on" deployed nothing (`README.md`, "Deploy to dev", "When").
If different: a `failure` row means open the run: the job summary names the script's fixed line (`scripts/ci_deploy.py`, the summary rows "Result" and "Script's line"), which section 3 explains. No row means no deploy has run: check the Actions tab for a disabled workflow (Step 4.4 disables it on purpose).
Risk: none, it only reads.

#### Step 2.1.2: find the record of the last good deploy

```
gh api "repos/andrew-chung-au/socboard/actions/artifacts?name=deploy-record-dev&per_page=3" --jq '.artifacts[] | [.id, .created_at, .workflow_run.id] | @tsv'
```

Expected: up to three lines, newest first: the artifact `deploy-record-dev` of a passing deploy, kept 90 days; a failed deploy writes none, so the newest line is the last good deploy (`README.md`, "Deploy to dev", "The record"). The third column is the run id that Step 4.1 uses.
If different: no line means no deploy has passed in the last 90 days (re-running the last deploy run writes a fresh record, `README.md`, "Deploy to dev", "The record"). `VERIFY:` the `.workflow_run.id` field name in the artifacts reply (Step 4.1 uses it).
Risk: none, it only reads.

### 2.2 By hand

#### Step 2.2.1: read the newest published digest

With the shortcuts from Before any command. Read the id of the newest successful publish run into the shortcut `R`:

```
R=$(gh run list --workflow publish.yml --repo andrew-chung-au/socboard --branch main --status success --limit 1 --json databaseId --jq '.[0].databaseId')
```

```
echo "R=[$R]"
```

Expected: `R=[` and a number `]`. That run is `socboard publish`.
If different: empty brackets mean no run, so no image is published yet; stop.

Open the run's page; the job summary holds the digest:

```
gh run view "$R" --repo andrew-chung-au/socboard --web
```

Expected: your browser opens the run. In the job summary, read the digest: `sha256:` and 64 lower-case hex digits (`README.md`, "Published image", "Name and tag"; `_human-tasks/2026-11-15T1822Z-human-task-237-engineer-first-deploy.md`, Step 4). There is no `latest` tag: deploy by digest only. Keep it: you paste it in place of `PASTE-DIGEST-HERE` in the `D` block below.
If different: no browser on this machine means print the page's address with `gh run view "$R" --repo andrew-chung-au/socboard --json url --jq .url` and open it elsewhere.
Risk: none, it only reads.

Now set the shortcut `D`. The next block holds the placeholder `PASTE-DIGEST-HERE`: replace it with the digest you just read in the job summary, so the line reads `D=sha256:` and 64 hex digits.

```
D=PASTE-DIGEST-HERE
```

```
echo "D=[$D]"
```

Expected: `D=[sha256:` and 64 hex digits `]`.
If different: the text `PASTE-DIGEST-HERE` is still there, or the digits are fewer than 64: copy the digest again from the job summary.

#### Step 2.2.2: send the digest

With `D` and `I` set and echoed. The parameters are JSON, in single quotes, because the short form `digest=...` can be split wrongly by the AWS CLI. `environment` is left out, so this is a dev run.

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"]}' --instance-ids "$I" --query Command.CommandId --output text); echo "C=[$C]"
```

Expected: `C=[` and a command id `]`.
If different: `InvalidParameters` usually means `D` or `I` is empty: run `echo "D=[$D] I=[$I]"`. An error that the parameter does not match the pattern means the digest is malformed (Step 2.3.1 shows it). An error about an unknown or stopped instance means `I` is stale (Step 1.1).
Risk: runs the deploy as root on the server: pulls the image and the pinned Postgres image, migrates the database, swaps the app (a short outage). A failed step leaves the current release serving, or restores it (section 3). The migration is not undone by a restore (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 3). Undo: section 4 (the previous release comes back; the database does not).

#### Step 2.2.3: read the result

Wait one to three minutes, then:

```
aws ssm get-command-invocation --region us-east-1 --command-id "$C" --instance-id "$I" --query '{Status:Status,Code:ResponseCode,Output:StandardOutputContent}' --output json
```

Expected: `Status` `Success`, `Code` 0 and `Output` holding `socboard-deploy: deployed.` and nothing else (`terraform/server/socboard-deploy.sh`, end of section 10). `InProgress` for a minute is normal: run it again. `VERIFY:` the first deploy settles what is seen (#237 stage (b)); the human replaces this line with what was seen.
If different: read the exit code and the output in section 3.
Risk: none, it only reads.

#### Step 2.2.4: send the same digest again

With `D` and `I` still set (echo them if the terminal is new).

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"]}' --instance-ids "$I" --query Command.CommandId --output text); echo "C=[$C]"
```

Expected: `C=[` and a new command id `]`.
If different: as Step 2.2.2.

Wait a minute, then:

```
aws ssm get-command-invocation --region us-east-1 --command-id "$C" --instance-id "$I" --query '{Status:Status,Code:ResponseCode,Output:StandardOutputContent}' --output json
```

Expected: `Code` 0 and `Output` `socboard-deploy: already deployed. Nothing was changed.` (`terraform/server/socboard-deploy.sh`, section 3). The run ends before it reads the secret, so a rotated value does not reach the app this way (section 6).
If different: `deployed.` means the app was not healthy, so the run deployed it again (the "already deployed" check needs the image to be running and healthy, `terraform/server/socboard-deploy.sh`, section 3). That is not a fault.
Risk: none, nothing changes when the app is healthy.

### 2.3 Refused cases, on purpose

A digest that is not `sha256:` and 64 lower-case hex digits is refused twice: by the document's pattern before it runs, and by the script with exit 2 (`terraform/server/deploy_document.tf`, `allowedPattern`; `terraform/server/socboard-deploy.sh`, section 2). The environment is checked the same way: only `dev` and `prod` pass (#267).

#### Step 2.3.1: send a value that is not a digest

Refusal test: run it in your own machine's terminal, not in an agent session. The aim is to see that Systems Manager refuses a value that is not a digest (`_human-tasks/2026-11-15T1822Z-human-task-237-engineer-first-deploy.md`, Step 8).
Risk: if the pattern did not hold, the script's own check refuses it with exit 2 and the text in section 3; nothing changes and no secret is printed either way.

```
aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["latest"]}' --instance-ids "$I"
```

Expected: an error from AWS that the parameter does not match the pattern (`InvalidParameters`), and no command id.
If different: if a command id is returned, read its result as Step 2.2.3 does: exit 2 with the refusal text is the script's own check; record both. An `InvalidParameters` error is also what an empty `I` gives: echo `I` first.

#### Step 2.3.2: send a well-formed digest that names no image

Refusal test: your own machine's terminal. The aim is to see exit 4 for a digest of the right shape that no image has.
Risk: none to the running release: the script stops after the failed pull (`terraform/server/socboard-deploy.sh`, section 4) and the app keeps answering.

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["sha256:0000000000000000000000000000000000000000000000000000000000000000"]}' --instance-ids "$I" --query Command.CommandId --output text); echo "C=[$C]"
```

Expected: `C=[` and a command id `]`.
If different: `C=[]` with an error means `I` is empty or stale: echo it (Step 1.1).

Wait a minute, then:

```
aws ssm get-command-invocation --region us-east-1 --command-id "$C" --instance-id "$I" --query '{Status:Status,Code:ResponseCode,Output:StandardOutputContent}' --output json
```

Expected: `Code` 4 and the text for exit 4 in section 3 (`_human-tasks/2026-11-15T1822Z-human-task-237-engineer-first-deploy.md`, Step 9). `VERIFY:` seen by the human at stage (b).
If different: record the output and stop.

## 3. Reading a failed run

Symptom: the CI job failed, or `Status` is not `Success`, or `Code` is not 0.
Check: read the result as Step 2.2.3 does (with `C` and `I` set). For a CI run, the public log shows only the status, the response code and the script's fixed `socboard-deploy:` lines; the rest stays in Systems Manager (`README.md`, "Deploy to dev", "How"). `VERIFY:` whether the failed job prints the command id; if not, list the recent commands:

```
aws ssm list-commands --region us-east-1 --filters key=DocumentName,value=socboard-deploy --max-results 5 --query 'Commands[].[CommandId,Status,RequestedDateTime]' --output text
```

Expected: up to five lines, newest first. To read one of them, copy its command id into `C` as the next block says.
If different: no line means no deploy was sent. `VERIFY:` the filter key name, which the human confirms at the first deploy.
Risk: none, it only reads.

To read a command from that list, replace `PASTE-COMMAND-ID-HERE` with the first column of its line (a command id), then run the echo:

```
C=PASTE-COMMAND-ID-HERE
```

```
echo "C=[$C]"
```

Expected: `C=[` and a command id (letters, digits and dashes) `]`.
If different: the text `PASTE-COMMAND-ID-HERE` still showing means nothing was pasted. Then run Step 2.2.3's block.

The script prints only the fixed lines below and, after exits 6, 7 and 9, at most the last 20 log lines of the app with the secret's eight values replaced by `[redacted]`; after exit 5 it prints the failing step's name and the last 20 lines of that step's output, redacted the same way (since #324, PR #327). Systems Manager keeps that output (`terraform/server/socboard-deploy.sh`, header comment, `logs_of`, `die_step`, `die_logs`). The texts are copied from `text_for` in that file.

| Exit | Fixed text (`terraform/server/socboard-deploy.sh`, `text_for`) | State the server is left in | Next step |
|---|---|---|---|
| 2 | `socboard-deploy: refused: the digest must be sha256: followed by 64 lower-case hex digits. Nothing was changed.` (for a bad environment: `socboard-deploy: refused: the environment must be dev or prod. Nothing was changed.`) | Nothing changed. | Send a real digest (Step 2.2.1). |
| 3 | `socboard-deploy: the application secret could not be read or is not usable. The current release was not changed.` | Current release still serving. | Check the secret `socboard/app`: exactly the eight keys, string values with only the characters the script allows, the three `STACK_PG_` values letters and digits only (`terraform/server/socboard-deploy.sh`, section 6, `PYCODE`); the instance's role may read it (`terraform/README.md`, "What it creates" under "The instance's IAM role, the snapshot schedule and the budgets"). The first run installs `python3-boto3`, which needs the package mirrors (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 5). Then send again. |
| 4 | `socboard-deploy: the image, the database image or the Compose files could not be fetched, or are not this repository's. The current release was not changed.` | Current release still serving. | The pull of the image or of the database image failed, the image's source label is not `https://github.com/andrew-chung-au/socboard`, its revision label is not 40 hex digits, or `compose.yaml` or `compose/db_init.py` could not be fetched from `raw.githubusercontent.com` at that revision (`terraform/server/socboard-deploy.sh`, sections 4 and 5). Check the digest names a published image and the package is public (`README.md`, "Published image", "By hand, once"). Send again. |
| 5 | `socboard-deploy: db-init, migrate or seed failed. The current release was not changed.` Then `socboard-deploy: failed step: NAME` and at most 20 redacted lines of that step's output (since #324). | Current release still serving, **but a migration that failed halfway can leave a partial change** (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 2). The usual cause of a `db-init` failure is a superuser password that no longer matches the data directory (`compose/db_init.py`, `LOGIN_FAILED`). | Read the failing step's name first. For `db-init`, start with section 3.1: it tells a superuser password mismatch from the other causes and fixes it. For a failed migration, do not send again until the migration is read; send the previous digest only if section 4's check passes. |
| 6 | `socboard-deploy: the new app container did not become healthy. The current release was not changed.` Then at most 20 log lines of the candidate. | Current release still serving; the candidate container is removed. | Read the log lines; fix the cause in the code and publish a new digest. |
| 7 | `socboard-deploy: the new release failed after the swap; the previous release was restored.` Then at most 20 log lines. | The previous release is serving again, running against the **new** schema (no migration is undone). | Read the log lines. Do not send the failed digest again. Section 4's check says whether the previous release is safe. |
| 7 | `socboard-deploy: the new release failed after the swap; there was no previous release to restore.` Then at most 20 log lines. | **Not restored: the app is stopped** (`docker stop` of the app container; the database keeps running). | First action: the app is down, so tell the users and send the last good digest (section 4) or fix and publish a new one. This happens on a first deploy. |
| 8 | `socboard-deploy: another run is in progress. Nothing was changed.` | Nothing changed. | Wait and read the other run's result with the `list-commands` command above; send again afterwards. Dev and prod share one lock on the server, so a prod promote in progress gives this too. |
| 9 | `socboard-deploy: the new release failed after the swap and the previous release could not be restored.` Then at most 20 log lines. | **Not restored: the app is not serving a healthy release.** `VERIFY:` the container's state in this case (the script runs no `docker stop` here); the human reads it at the first failure. | First action: the app is down. Read the log lines, then send the last good digest (section 4). If the migration list changed, go to section 7. |
| 10 | `socboard-deploy: the stack network's gateway is not the configured proxy address. The current release was not changed.` | Current release still serving. | The check compares the gateway of the stack's network with `10.231.77.1` (dev; prod's is `10.231.78.1`). Read `terraform/README.md`, "The bootstrap", "The forwarded address", and `compose.yaml` (the pinned `gateway`). Nothing is fixed by sending again. |

The line the script prints on success is `socboard-deploy: deployed.` (exit 0), and on a repeat `socboard-deploy: already deployed. Nothing was changed.` (exit 0) (`terraform/server/socboard-deploy.sh`, sections 3 and 10). A signal (a timeout, a reboot, a lost agent) ends the run with no fixed line; the next run starts from what Docker shows (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 6).

Fix: the Next step column. Undo: none needed for exits 2 to 6, 8 and 10; for exits 7 and 9 see section 4.

### 3.1 Exit 5: the superuser password does not match the data folder

Seen on 2026-11-16 at the first dev deploy (#237 stage (b)): the first two sends exited 5, and the fix below (case A) made the third print `socboard-deploy: deployed.`

**Why it happens.** Postgres sets the superuser's password once, when it first creates its data folder (`/srv/socboard-data/postgres`). It never reads `STACK_PG_SUPERUSER_PASSWORD` again. If the secret's value changes after that, `db-init` logs in with the new value, Postgres refuses it, and every deploy exits 5. Sending again does not help. Ways it happens: a new value put into `socboard/app` after a deploy already ran (for example Steps 2 and 3 of the first deploy done twice), or a data folder that survived from an earlier instance or attempt. To change the password on purpose, use section 6.7, never a new value in the secret alone.

**Symptom:** exit 5 with `socboard-deploy: db-init, migrate or seed failed. The current release was not changed.` On the first dev deploy (2026-11-16) nothing else was printed, because the script threw away `db-init`'s own message. Since #324 (PR #327) it prints `socboard-deploy: failed step: db-init` and the last 20 redacted lines of the step, so the cause is usually visible in the result itself. On a first deploy, the site answers `502` because no app was started.

Every command below runs in a session on the server unless it says "on your own machine". Start the session with the shortcuts from Before any command:

```
aws ssm start-session --region us-east-1 --target "$I"
```

Expected: a shell prompt on the server (not your machine's prompt).
If different: `SessionManagerPlugin is not found` means the plugin is missing: use the AWS Console instead (EC2, select the instance, **Connect**, **Session Manager**, **Connect**). The server has no `aws` command. Run `aws` commands on your own machine only.

#### Step 3.1.1: read the database's log

```
sudo docker logs --tail 40 socboard-db-1 2>&1 | cut -c1-200
```

Expected for this problem: a line `FATAL:  password authentication failed for user "postgres"` a few seconds after `database system is ready to accept connections`. `Skipping initialization` near the top means Postgres found an existing data folder.
If different: no `FATAL` line for `postgres` means this is not the cause. A `FATAL` for `socboard_owner` or `socboard_app` points at `migrate` or `seed`. Read section 3's exit 5 row.
Risk: none, it only reads. The log holds no password.

#### Step 3.1.2: check whether the database holds data

```
sudo docker exec socboard-db-1 psql -U postgres -c '\l'
```

Expected: a table of databases. It connects over the container's local socket, which needs no password (seen 2026-11-16).
- Only `postgres`, `template0` and `template1`: no `socboard` database, so there is no data. Go to case A.
- A `socboard` row: the database may hold cases and the audit trail. Go to case B. Never use case A here.
If different: `No such container` means the database is not running. List names with the next block.
Risk: none, it only reads.

```
sudo docker ps -a --format '{{.Names}}  {{.Status}}'
```

Expected: one line per container, including `socboard-db-1`.
If different: no `socboard-db-1` means the stack is not on this server; stop.

#### Case A: no `socboard` database: set the empty data folder aside

```
sudo docker rm -f socboard-db-1
```

Expected: `socboard-db-1`.
Risk: stops and removes the database container. The data folder stays on the volume.

```
sudo mv /srv/socboard-data/postgres /srv/socboard-data/postgres.old
```

Expected: no output.
If different: an error that `postgres` does not exist means the move already happened or this is the wrong machine: check the prompt.
Risk: none to data; the folder is kept under a new name. Undo: `sudo mv /srv/socboard-data/postgres.old /srv/socboard-data/postgres` (with the database container removed first).

```
sudo ls -l /srv/socboard-data
```

Expected: `postgres.old` and no `postgres`. Leave `caddy`, `lost+found` and `postgres-prod` alone.
If different: a `postgres` entry still there means the move ran somewhere else (check the prompt: your own machine's prompt is not the server's). Run the two commands above again on the server.

Leave the session and go back to your own machine's terminal:

```
exit
```

Expected: your own machine's prompt returns.

Then send the same digest again from your own machine (Step 2.2.2, with `D` still set; if the terminal is new, set `D` again as Step 2.2.1 says) and read the result (Step 2.2.3). Expected: `socboard-deploy: deployed.` The new folder's first start runs `initdb`; its log says `init process complete` and no `Skipping initialization`.
Once the deploy has passed, delete the old folder when you no longer want it (human only), in a server session:

```
sudo rm -rf /srv/socboard-data/postgres.old
```

Expected: no output; `sudo ls /srv/socboard-data` no longer lists `postgres.old`.
Risk: deletes the old, empty data folder; can't be undone. Run it only when the deploy has passed.

#### Case B: a `socboard` database exists: set the password inside the database to the secret's value

Keep the data: change the password inside Postgres to match the secret, as section 6.7 step (3) does, but with the secret's current value instead of a new one. `VERIFY:` case B has not been run; the human settles it the first time it is needed.

1. Leave the session (`exit`). On your own machine, copy the current value to the clipboard: run Step 5.1's first block (the file), then its fourth block (the key `STACK_PG_SUPERUSER_PASSWORD`). On WSL, use `clip.exe` in place of `pbcopy` (seen 2026-11-16).
2. Start a session again (the `aws ssm start-session` block above), then on the server:

```
sudo docker exec -it socboard-db-1 psql -U postgres
```

Expected: a `psql` prompt. Type `\password postgres`, paste the value at both prompts (nothing is shown), then `\q`. `psql` encrypts the password before it is sent, so it is not in any log.
If different: a refused connection means stop; nothing was changed.
Risk: changes the superuser's password to the secret's. Nothing else changes.

3. Leave the session (`exit`). Remove the file with Step 5.3 and copy something else to clear the clipboard.
4. Send the same digest again (Steps 2.2.2 and 2.2.3). Expected: `socboard-deploy: deployed.`

## 4. Roll back

Symptom: the new release is bad and the previous one is wanted back (after exit 7 or 9, or after a deploy that passed).
Check: the three steps below. Fix: send the previous digest with the same command as section 2. Undo: send the newer digest again.

This section is for dev. Prod is rolled back with the promote workflow, which takes an earlier dev digest as its input (`_human-tasks/2026-11-16T0332Z-human-task-269-engineer-promote-and-rollback.md`, step 5).

A rollback holds only until the next green push to `main`, which deploys the newest commit again (`_docs/decisions/2026-11-15T2100Z-deploy-dev-from-ci.md`, decision 3). Hold the push (Step 4.4) as soon as the rollback has passed, unless that push is the fix you want deployed.

### Step 4.1: find the previous digest

Use the first of these that works. The artifact `deploy-record-dev` of the last good run: with the shortcuts from Before any command, read the run id of the second-newest record into the shortcut `R` (Step 2.1.2 lists the same records; a failed deploy writes none, so if the bad release failed and was restored, the newest record, `[0]`, is the one you want: change `[1]` to `[0]` in this block).

```
R=$(gh api 'repos/andrew-chung-au/socboard/actions/artifacts?name=deploy-record-dev&per_page=2' --jq '.artifacts[1].workflow_run.id')
```

```
echo "R=[$R]"
```

Expected: `R=[` and a number `]`.
If different: empty brackets mean there is only one record: let a second push deploy to dev first, or use the server's own list below.

Download the record to a fixed folder outside the repository:

```
gh run download "$R" --repo andrew-chung-au/socboard --name deploy-record-dev --dir /tmp/socboard-dev-record
```

Expected: no output, and one JSON file `/tmp/socboard-dev-record/deploy-record-dev.json` with the fields `digest` and `revision` among others (`README.md`, "Deploy to dev", "The record"). `VERIFY:` the file's name, seen at the first passing deploy.
If different: an error that the artifact is not found means it expired after 90 days; use the older publish run's job summary (`README.md`, "Published image"; open the run with `gh run view "$R" --repo andrew-chung-au/socboard --web`, after setting `R` to a publish run as Step 2.2.1 does) or the server's own list below. A message that the folder exists means an earlier try left it: run `rm -r /tmp/socboard-dev-record` and this block again.
Risk: none, it downloads a file with no secret in it (the fields are listed in `README.md`, "Deploy to dev", "The record").

Read the old digest into the shortcut `D` (this replaces any digest `D` held before):

```
D=$(jq -r .digest /tmp/socboard-dev-record/deploy-record-dev.json)
```

```
echo "D=[$D]"
```

Expected: `D=[sha256:` and 64 hex digits `]`.
If different: empty brackets mean the download failed (see above). If you took the digest from a publish run's job summary or from the server's list below, set it by hand: replace `PASTE-DIGEST-HERE` with that digest (`sha256:` and 64 hex digits), then run the echo block again:

```
D=PASTE-DIGEST-HERE
```

Read the old revision into the shortcut `OLDREV` (Step 4.2 needs it):

```
OLDREV=$(jq -r .revision /tmp/socboard-dev-record/deploy-record-dev.json)
```

```
echo "OLDREV=[$OLDREV]"
```

Expected: `OLDREV=[` and 40 hex digits `]`.
If different: empty brackets: as for `D`. If you have no record, Step 4.2 shows how to read the revision from the server instead.

```
rm -r /tmp/socboard-dev-record
```

Expected: no output.
If different: `No such file or directory` means it is already gone; carry on.

The server's own list is the other way to find a previous digest. Start a session:

```
aws ssm start-session --region us-east-1 --target "$I"
```

Expected: a shell prompt on the server (Systems Manager only; the server has no SSH, `terraform/README.md`, "What it creates"). The next block runs there.
If different: `SessionManagerPlugin is not found` means the plugin is missing: use the AWS Console instead (see Before any command).

```
sudo docker image ls --digests ghcr.io/andrew-chung-au/socboard
```

Expected: one row per image still on the host, with its digest. The weekly prune removes images no container uses and older than 168 hours, so the previous image may be gone; the script pulls any digest anyway (`terraform/README.md`, "What it does", "Docker"; `terraform/server/socboard-deploy.sh`, section 4).
If different: no row means the image was pruned or never pulled; use the record or the publish summary.
Risk: none, it only reads. Leave the session with `exit` when you are done with it.

```
exit
```

Expected: your own machine's prompt returns.

### Step 4.2: check that no migration changed between the two releases

The revision of an image is its label `org.opencontainers.image.revision` (`terraform/server/socboard-deploy.sh`, section 4). The old one is `OLDREV` from Step 4.1. The one now running is read on the server. Start a session:

```
aws ssm start-session --region us-east-1 --target "$I"
```

Expected: a shell prompt on the server.
If different: as in Step 4.1.

```
sudo docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$(sudo docker inspect --format '{{.Config.Image}}' socboard-app-1)"
```

Expected: 40 hex digits: the revision of the image the app is running now. Keep it: you paste it in place of `PASTE-NEW-REVISION-HERE` in the `NEWREV` block below.
If different: an error means the app container is not running or its image is gone; read `sudo docker ps -a --format '{{.Names}}  {{.Status}}'` and stop.

```
exit
```

Expected: your own machine's prompt returns.

If Step 4.1 gave you no `OLDREV` (no record), read it on the server instead: in a session, replace `PASTE-OLD-DIGEST-HERE` in the next block with the old digest from Step 4.1's server list (`sha256:` and 64 hex digits), and run it; it prints that image's 40-digit revision, which you then paste into the `OLDREV` block further down in place of `PASTE-OLD-REVISION-HERE`.

```
sudo docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' ghcr.io/andrew-chung-au/socboard@PASTE-OLD-DIGEST-HERE
```

Expected: 40 hex digits, after you replaced the text `PASTE-OLD-DIGEST-HERE`. Keep it: you paste it in place of `PASTE-OLD-REVISION-HERE` in the `OLDREV` block below.
If different: an error means the image is not on the host: pull it first with `sudo docker pull ghcr.io/andrew-chung-au/socboard@` followed by the same digest.

Back on your own machine, set the shortcut `NEWREV`. Replace `PASTE-NEW-REVISION-HERE` with the 40 hex digits the server printed for the running image:

```
NEWREV=PASTE-NEW-REVISION-HERE
```

```
echo "NEWREV=[$NEWREV]"
```

Expected: `NEWREV=[` and 40 hex digits `]`.
If different: the text `PASTE-NEW-REVISION-HERE` is still there: paste the revision.

Only if you had no record: set `OLDREV` the same way. Replace `PASTE-OLD-REVISION-HERE` with the 40 hex digits the server printed for the old image:

```
OLDREV=PASTE-OLD-REVISION-HERE
```

Expected: after the echo from Step 4.1 (`echo "OLDREV=[$OLDREV]"`), `OLDREV=[` and 40 hex digits `]`.

On your own machine, in the clone:

```
git fetch origin
```

Expected: no error; new commits may be listed.
If different: a network error means the diff below cannot see both revisions; stop.

```
git diff --stat "$OLDREV" "$NEWREV" -- socboard/migrations/versions
```

Expected: no output, which means no changed migration file.
If different: stop. No migration is undone by a restore, so the old release may fail its health check (exit 9) or misbehave (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 3). The next step is the restore in section 7, not a rollback. An error that a revision is unknown means `git fetch origin` did not bring it: run it again.
Risk: none, it only reads.

### Step 4.3: send the previous digest

With `D` set to the old digest (Step 4.1; echo it first) and `I` set.

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"]}' --instance-ids "$I" --query Command.CommandId --output text); echo "C=[$C]"
```

Expected: `C=[` and a command id `]`.
If different: as Step 2.2.2.
Risk: swaps the app for the old release (a short outage). Undo: send the newer digest.

Wait a minute, then:

```
aws ssm get-command-invocation --region us-east-1 --command-id "$C" --instance-id "$I" --query '{Status:Status,Code:ResponseCode,Output:StandardOutputContent}' --output json
```

Expected: `Success`, code 0 and `socboard-deploy: deployed.`. A failure is read in section 3.
If different: read the exit code and the output in section 3.

### Step 4.4: hold the next push

```
gh workflow disable deploy-dev.yml --repo andrew-chung-au/socboard
```

Expected: no error; the workflow shows as disabled in `gh workflow list`. A second way that needs no command: do not merge to `main` until the fix is ready.
If different: an error that the workflow is not found means the workflow file is not on `main`; there is nothing to hold.
Risk: no CI deploy runs until it is enabled again, including a push that fixes the bad release. Undo: `gh workflow enable deploy-dev.yml --repo andrew-chung-au/socboard`.

## 5. Hand reviewers their credentials

Reviewers receive their sign-in out of band and never in the README, an issue or a comment (`_docs/decisions/2026-11-13T2156Z-deploy.md`, decision 5). The three users are `analyst-a`, `analyst-b` and `lead` (`README.md`, "Runtime variables"); their first passwords are the secret's three seed values (`README.md`, "Runtime variables"; `terraform/server/socboard-deploy.sh`, `NAMES`).

### Step 5.1: read one value into your clipboard, never to the terminal

The secret goes first to a file made under `umask 077` at one fixed path outside the repository, `/tmp/socboard-dev-secret.json` (the allowed form of "Never do", first bullet). Remove any older file first:

```
rm -f /tmp/socboard-dev-secret.json
```

Expected: no output.

```
( umask 077; aws secretsmanager get-secret-value --region us-east-1 --secret-id socboard/app --query SecretString --output text > /tmp/socboard-dev-secret.json )
```

Expected: no output; the file exists.
If different: an error means no access or the secret is missing; stop. Never run it without the redirect.
Risk: a copy of all eight values is on your disk until Step 5.3. Undo: Step 5.3.

```
ls -l /tmp/socboard-dev-secret.json
```

Expected: `-rw-------` and a size that is not 0 (eight 48-character values come to around 650 bytes). Never print the file.
If different: a size of `0` means nothing was written: run the previous block again. A mode other than `-rw-------` means the `umask` did not apply: run `rm -f /tmp/socboard-dev-secret.json` and start again.

The next three blocks copy one user's password to the clipboard, one block per user; run only the block you need. `pbcopy` is macOS; use `wl-copy` or `clip.exe` in its place where that is what your machine has (`VERIFY:` on your machine). Paste the value into your password manager.

For `lead`:

```
python3 -c "import json, sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])" /tmp/socboard-dev-secret.json SOCBOARD_SEED_PASSWORD_LEAD | pbcopy
```

Expected: no output; the clipboard holds the value of `SOCBOARD_SEED_PASSWORD_LEAD`.
If different: a `KeyError` means the key is not in the file; a clipboard command not found means use your machine's. The value is printed to the terminal only if the pipe is left off: never leave it off.
Risk: the value sits on the clipboard; copy something else afterwards.

For `analyst-a`:

```
python3 -c "import json, sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])" /tmp/socboard-dev-secret.json SOCBOARD_SEED_PASSWORD_ANALYST_A | pbcopy
```

Expected and If different: as for `lead`, with `SOCBOARD_SEED_PASSWORD_ANALYST_A`.

For `analyst-b`:

```
python3 -c "import json, sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])" /tmp/socboard-dev-secret.json SOCBOARD_SEED_PASSWORD_ANALYST_B | pbcopy
```

Expected and If different: as for `lead`, with `SOCBOARD_SEED_PASSWORD_ANALYST_B`.

For the database superuser's password (used only by section 3.1 case B and section 6.7, never handed to a reviewer):

```
python3 -c "import json, sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])" /tmp/socboard-dev-secret.json STACK_PG_SUPERUSER_PASSWORD | pbcopy
```

Expected and If different: as for `lead`, with `STACK_PG_SUPERUSER_PASSWORD`.

### Step 5.2: hand it over

Send each reviewer their own username and password through your own out-of-band channel. This is not a command. The README, an issue and a comment never hold it.

### Step 5.3: remove the file

```
rm -f /tmp/socboard-dev-secret.json
```

Expected: no output; the file is gone.
If different: if the file is missing already, there is nothing to remove.

### 5.4 Give a user a new password

`make seed` never changes an existing user, so a new password for one user is set with `make set-password ACCOUNT=USERNAME`, which reads the password from `SOCBOARD_NEW_PASSWORD`, never from the command line (`README.md`, "Resetting a user's password"). A token issued before the change stays valid until it expires, 8 hours (`README.md`, "Resetting a user's password"). The deployed database is not reachable from your machine (`db` publishes no port, `README.md`, "Compose stack", "Ports"), so the command runs on the server, in the app's image, with the value read from the memory-backed file of section 6.8. Do 6.8's Steps 6.8.0 to 6.8.3 first (a session, a root shell, the file written), then, in that root shell, set two shortcuts for the user. The pairs are: `analyst-a` with `SOCBOARD_SEED_PASSWORD_ANALYST_A`, `analyst-b` with `SOCBOARD_SEED_PASSWORD_ANALYST_B`, `lead` with `SOCBOARD_SEED_PASSWORD_LEAD`. The next two blocks use the first pair; change both words for another user.

```
U=analyst-a
```

```
UK=SOCBOARD_SEED_PASSWORD_ANALYST_A
```

```
echo "U=[$U] UK=[$UK]"
```

Expected: `U=[analyst-a] UK=[SOCBOARD_SEED_PASSWORD_ANALYST_A]` (or the pair you chose). These are a username and a key name, not secrets.
If different: a pair that does not match means the wrong password would be set: set both again.

```
SOCBOARD_NEW_PASSWORD="$(sed -n "s/^$UK=//p" /run/socboard-deploy/stack-vars)" docker compose --project-directory /opt/socboard/current --env-file /run/socboard-deploy/stack-vars -f /opt/socboard/current/compose.yaml -f /opt/socboard/current/deploy.override.yaml run --rm --no-deps -e SOCBOARD_NEW_PASSWORD app python -m socboard.set_password "$U"
```

Expected: a fixed success line from `socboard.set_password` that names no password or hash, exit 0. `VERIFY:` the exact line; the human settles it at stage (b). Then do Step 6.8.6 (delete the file). The new value is read from the key of the same user in the memory-backed file, so the secret (updated first, section 6.3 to 6.5) and the database end equal, which the smoke check needs for `lead` (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 7).
If different: exit 2 means a missing user or a bad password and nothing changed (`README.md`, "Resetting a user's password"). Do not retype the value on a command line.
Risk: changes one user's password in the live database; can be set again the same way. The value is in the environment of that one process only, never exported in the shell and never in the process list. Undo: set the old value again.

## 6. Rotate a secret

Symptom: a value is known or suspected to be seen by someone who should not have it, or it is due.
Fix: the subsection of the value. Undo: put the old secret version back (`aws secretsmanager put-secret-value` of the old file) and apply it the same way; the old value is not kept by this runbook, so make a copy of the whole secret first (Step 6.0.1) and keep it until the check passes. The copy is the file `/tmp/socboard-dev-secret.json` before Step 6.0.2 changes it, so to keep the old values copy it to `/tmp/socboard-dev-secret-old.json` (same mode) between Steps 6.0.1 and 6.0.2, and delete both in Step 6.0.4.

**How a rotated value reaches the app.** A deploy of the digest already running ends with "already deployed" before the secret is read (`terraform/server/socboard-deploy.sh`, section 3), so a changed secret reaches the app only at the next deploy of a different digest or through the by-hand procedure of section 6.8 (Decision question 4 of #240, recommendation taken). Until then the secret and the running app differ.

**What the script requires of every value** (`terraform/server/socboard-deploy.sh`, section 6, `PYCODE`): a string of the characters `A-Za-z0-9._~+/=@%:,-`, and for the three `STACK_PG_` values letters and digits only. The values below are made with `secrets.token_hex(24)`, 48 hex characters, which pass both rules and the app's minimum lengths (`README.md`, "Runtime variables").

### 6.0 How every rotation starts and ends

**Warning for `STACK_PG_SUPERUSER_PASSWORD`:** never put a new value for this key with these steps alone, and never put a whole new secret (all eight keys) once a deploy has run. Postgres keeps the password it was first created with, so the next deploy exits 5 (section 3.1). Change it only with section 6.7.

#### Step 6.0.1: copy the secret to a file

Run Step 5.1's three blocks that make the file: the `rm -f`, the `get-secret-value` into `/tmp/socboard-dev-secret.json`, and the `ls -l` check. Expected and Risk are as there: `-rw-------` and a size above 0.

To keep the old values for the undo, copy the file now:

```
cp -p /tmp/socboard-dev-secret.json /tmp/socboard-dev-secret-old.json
```

Expected: no output. `ls -l /tmp/socboard-dev-secret-old.json` shows `-rw-------`.
If different: a mode other than `-rw-------` means `cp -p` did not keep it: run `chmod 600 /tmp/socboard-dev-secret-old.json`.
Risk: a second copy of all eight values on your disk until Step 6.0.4.

#### Step 6.0.2: replace one key in the file with a new random value

Set the shortcut `K` to the key you are rotating. The block holds `SOCBOARD_INGEST_API_KEY`, the key the stage (b) rotation run uses; replace it with another of the eight names in section 1's table if you rotate another. The subsections 6.1 to 6.7 say which name each uses.

```
K=SOCBOARD_INGEST_API_KEY
```

```
echo "K=[$K]"
```

Expected: `K=[` and one of the eight key names `]`. A key name is not a secret.
If different: any other text means a mistyped name: set `K` again. A mistyped name would add a ninth key to the file and the next deploy would exit 3 (section 3).

```
python3 -c "import json, secrets, sys; d = json.load(open(sys.argv[1])); d[sys.argv[2]] = secrets.token_hex(24); json.dump(d, open(sys.argv[1], 'w'))" /tmp/socboard-dev-secret.json "$K"
```

Expected: no output; the file keeps mode 600 (it is rewritten in place).
If different: a `KeyError` or `JSONDecodeError` means the file is missing, empty or not the secret: go back to Step 6.0.1. Never print the file.
Risk: none outside the file.

```
python3 -c "import json, sys; print(sorted(json.load(open(sys.argv[1]))))" /tmp/socboard-dev-secret.json
```

Expected: a list of exactly the eight key names (names only, never values).
If different: nine names, or a name that is not in section 1's table, means `K` was mistyped: run Step 6.0.1 again to start over from the stored secret.

#### Step 6.0.3: put the new version

```
ls -l /tmp/socboard-dev-secret.json
```

Expected: `-rw-------` and a size above 0, about the size Step 6.0.1 showed. An empty file gives `Invalid length for parameter SecretString` below.
If different: a size of `0` means the file is empty: go back to Step 6.0.1. Put nothing.

`file://` is followed by the path, which starts with `/`, so there are three slashes in a row.

```
aws secretsmanager put-secret-value --region us-east-1 --secret-id socboard/app --secret-string file:///tmp/socboard-dev-secret.json
```

Expected: a JSON reply with the secret's name and a version id, and no secret value (`_human-tasks/2026-11-15T1822Z-human-task-237-engineer-first-deploy.md`, Step 3).
If different: an access error names the missing action; the secret is unchanged. `Invalid length for parameter SecretString, value: 0` means the file is empty; nothing was stored.
Risk: sets the application secret. From now on the next deploy of a different digest, and every by-hand read, uses the new value. Undo: put the previous file's content the same way (`file:///tmp/socboard-dev-secret-old.json`).

#### Step 6.0.4: remove the file

```
rm -f /tmp/socboard-dev-secret.json /tmp/socboard-dev-secret-old.json
```

Expected: no output. Keep the old copy until the check of the subsection has passed, if you may need the undo; then run this block.
If different: nothing to remove if the files are gone already.

```
ls /tmp/socboard-dev-secret.json /tmp/socboard-dev-secret-old.json
```

Expected: two `No such file or directory` messages.
If different: a listed file is still there: run the block above again.

### 6.1 `SOCBOARD_TOKEN_SECRET`

- **Used where:** the app, to sign and check login tokens (`README.md`, "Runtime variables").
- **What applies a change:** a start of the app with the new value: the next deploy of a different digest, or 6.8.
- **Order:** Steps 6.0.1 to 6.0.4 with `K` set to `SOCBOARD_TOKEN_SECRET`; then deploy (section 2, a different digest) or 6.8.
- **What breaks while the two sides differ:** nothing; the running app keeps the old value. After the change every user is signed out (`README.md`, "Resetting a user's password", Limits).
- **Check afterwards:** the deploy ends with `socboard-deploy: deployed.`, whose checks include the smoke check's login (`terraform/server/socboard-deploy.sh`, `check_release`). Sign in once in a browser.

### 6.2 `SOCBOARD_INGEST_API_KEY`

- **Used where:** the app's alert ingest, and the smoke check (`README.md`, "Runtime variables").
- **What applies a change:** a start of the app, as 6.1.
- **Order:** Steps 6.0.1 to 6.0.4 with `K` set to `SOCBOARD_INGEST_API_KEY` (the value Step 6.0.2 starts with); then deploy or 6.8; then give the new key to every sender of alerts.
- **What breaks while the two sides differ:** a sender with the new key gets 401 until the app restarts; a sender with the old key gets 401 after (`README.md`, "Ingest rate limit": a missing or wrong key is 401).
- **Check afterwards:** the deploy's own smoke check ingests one synthetic alert with the new key (`terraform/server/socboard-deploy.sh`, `check_release`; `README.md`, "Runtime variables"). Each full smoke run adds one New case (`README.md`, "Smoke check"). This key is the value the stage (b) rotation run uses.

### 6.3 `SOCBOARD_SEED_PASSWORD_ANALYST_A`, 6.4 `SOCBOARD_SEED_PASSWORD_ANALYST_B`, 6.5 `SOCBOARD_SEED_PASSWORD_LEAD`

One rule for the three. A seed password in the secret does not change an existing user (`README.md`, "Runtime variables"; "Seed" in `AGENTS.md`'s Commands, `make seed`). A user's password changes with `make set-password` (section 5.4), and then the secret's value is updated, or the smoke check's login as `lead` fails and the deploy restores (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 7).

- **Used where:** `seed` at each deploy (creates a user only if missing); `lead`'s also the smoke check.
- **What applies a change:** `make set-password` changes the database; the secret's value only has to match it.
- **Order:** (1) Steps 6.0.1 to 6.0.4 with `K` set to the key (the secret first, so section 5.4 reads the new value from it). (2) Section 6.8 steps 1 to 4, then section 5.4's command for that user. (3) Clean up as 6.8 says.
- **What breaks while the two sides differ:** for `lead`, a deploy between the secret change and `set-password` fails its smoke check's login and restores the previous release (exit 7); for the other two nothing is checked, so nothing fails, and the user's old password still works until `set-password` runs.
- **Check afterwards:** a deploy of a different digest ends with `socboard-deploy: deployed.` (for `lead`); sign in as the user with the new password.

### 6.6 `STACK_PG_OWNER_PASSWORD` and `STACK_PG_APP_PASSWORD`

- **Used where:** `db-init` sets the owner and application roles' passwords on every start (`compose/db_init.py`, `set_up_roles`); `migrate` connects as the owner, `seed` and `app` as the application role (`compose.yaml`).
- **What applies a change:** the next deploy that runs `db-init`, so these two take effect at the next deploy of a different digest, or at 6.8 with `db-init` run by hand.
- **Order:** Steps 6.0.1 to 6.0.4 with `K` set to the key, then the deploy or 6.8 (which runs `db-init`, then recreates `app`).
- **What breaks while the two sides differ:** nothing before the deploy. During it, once `db-init` has set the new password, the still-running old app cannot open a new database connection with its old one until the swap; connections already open stay valid (`VERIFY:` PostgreSQL behaviour, not a file of this repository; the human watches the app during the first rotation).
- **Check afterwards:** the deploy ends with `socboard-deploy: deployed.`; a failed `db-init`, `migrate` or `seed` is exit 5 (section 3).

### 6.7 `STACK_PG_SUPERUSER_PASSWORD`

`VERIFY:` this whole subsection is unverified until the human has run it (stage (b) of #240); the command is settled then.

- **Used where:** `db` (the password set at first start) and `db-init`, which connects with it on every start (`compose.yaml`; `compose/db_init.py`, `connect`).
- **What applies a change:** Postgres set this password only when the data directory was first made, so changing the secret alone makes every later deploy exit 5 (`compose/db_init.py`, `LOGIN_FAILED`; section 3). The role is changed inside the database first, then the secret.
- **Order:** (1) copy the secret (Step 6.0.1) and make the new value in the file (Step 6.0.2 with `K` set to `STACK_PG_SUPERUSER_PASSWORD`); do not put it yet. (2) Copy the new value to the clipboard as Step 5.1's fourth block does (the key `STACK_PG_SUPERUSER_PASSWORD`). (3) Change the role in the database, in a session on the server (start it with the `aws ssm start-session` block of section 3.1):

```
sudo docker exec -it socboard-db-1 psql -U postgres
```

Expected: a `psql` prompt. At it type `\password postgres`, paste the value at each prompt (nothing is shown), then `\q`. `psql` encrypts the password before it is sent. `VERIFY:` the container name (`socboard-db-1`, from the project name and the service `db`, the same way the script names the app container, `terraform/server/socboard-deploy.sh`, `APP`), and that the local socket accepts the connection.
If different: an error that the container does not exist means list names with `sudo docker ps --format '{{.Names}}'`. A failed login means stop: the secret was not changed, so nothing differs yet.
Risk: changes the database superuser's password. From now until step (4) a deploy exits 5. Undo: set the old value the same way.

(4) Leave the session (`exit`) and put the new secret now (Steps 6.0.3 and 6.0.4). (5) Check by a run of `db-init`, by the next deploy of a different digest or by 6.8.

- **What breaks while the two sides differ:** between (3) and (4), every deploy exits 5 (`compose/db_init.py`, `LOGIN_FAILED`).
- **Check afterwards:** the deploy ends with `socboard-deploy: deployed.`, or by hand `db-init` prints `db-init: roles, database and privileges are in place` (`compose/db_init.py`, `main`).

### 6.8 Operating by hand

No variable file stays on the host, so `docker compose` cannot be run by hand without the script (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 4). This procedure reads the secret again through the instance's role into a mode-0600 file in the memory-backed folder, runs `docker compose` with the two files of the current release, and deletes the file in the last step. It never prints the file. It puts no value on a command line, none in an exported shell variable and none in a file on the data volume or the root disk (a snapshot would back it up); `/run/socboard-deploy` is a memory file system (`terraform/server/socboard-deploy.sh`, `RUN_DIR`, section 7 header). `VERIFY:` the whole procedure is unrun; the human settles it at stage (b).

Do it in a session on the server. Do not do it while a deploy runs. Start the session, with the shortcuts from Before any command:

```
aws ssm start-session --region us-east-1 --target "$I"
```

Expected: a shell prompt on the server.
If different: `SessionManagerPlugin is not found` means the plugin is missing: use the AWS Console instead (see Before any command).

#### Step 6.8.0: become root for the length of the procedure

```
sudo -s
```

Expected: a root shell prompt. Every command of Steps 6.8.1 to 6.8.6 runs in it, because the file is readable by root only. Type `exit` after Step 6.8.6. `VERIFY:` the session's user may use `sudo` without a password.
If different: a refusal means the session's user has no sudo; stop.
Risk: every command you type is now root's. Undo: `exit`.

#### Step 6.8.1: check that no deploy is running

```
flock -n /run/socboard-deploy/lock true && echo free
```

Expected: `free`. The script's lock is this file (`terraform/server/socboard-deploy.sh`, section 1). `VERIFY:` the folder exists before the first deploy; the check is not a lock, so a deploy that starts after it can still run.
If different: no output means a deploy holds the lock; wait (exit 8, section 3).
Risk: none, it takes the lock for an instant.

#### Step 6.8.2: write the variable file

```
python3 -c "import boto3, json, os; names = ['SOCBOARD_TOKEN_SECRET','SOCBOARD_INGEST_API_KEY','SOCBOARD_SEED_PASSWORD_ANALYST_A','SOCBOARD_SEED_PASSWORD_ANALYST_B','SOCBOARD_SEED_PASSWORD_LEAD','STACK_PG_SUPERUSER_PASSWORD','STACK_PG_OWNER_PASSWORD','STACK_PG_APP_PASSWORD']; d = json.loads(boto3.client('secretsmanager', region_name='us-east-1').get_secret_value(SecretId='socboard/app')['SecretString']); os.umask(0o077); f = open('/run/socboard-deploy/stack-vars', 'w'); [f.write(n + '=' + d[n] + chr(10)) for n in names]; f.close()"
```

Expected: no output; the file `/run/socboard-deploy/stack-vars` exists with mode 600 (`ls -l /run/socboard-deploy/stack-vars`). The instance's role may read the secret (`terraform/README.md`, "What it creates" under "The instance's IAM role, the snapshot schedule and the budgets"); `python3-boto3` is there after the first deploy (`_docs/decisions/2026-11-15T1822Z-deploy-script.md`, trade-off 5). `VERIFY:` that boto3 finds the instance's credentials in this session.
If different: an error before the file exists changes nothing. Never print the file.
Risk: the secret's eight values are on the memory file system until Step 6.8.6. The folder is not on the data volume or the root disk. Undo: Step 6.8.6.

#### Step 6.8.3: add the two names that are not secrets

```
printf '%s\n' "STACK_IMAGE=$(docker inspect --format '{{.Config.Image}}' socboard-app-1)" STACK_PGDATA_DIR=/srv/socboard-data/postgres >> /run/socboard-deploy/stack-vars
```

Expected: no output. The two lines are the image the app runs (a digest reference) and the data folder (`terraform/server/socboard-deploy.sh`, section 7; `terraform/README.md`, "The layout on the volume"). `VERIFY:` the container name `socboard-app-1` (`terraform/server/socboard-deploy.sh`, `APP`, itself marked `VERIFY:`).
If different: an empty image (the first line reads `STACK_IMAGE=` with nothing after it) means the app container is not running. Use the digest you want: replace `PASTE-DIGEST-HERE` in the next block with that digest (`sha256:` and 64 hex digits, from Step 4.1 or the publish run's job summary) and run it in place of the block above. Do not run both.

```
printf '%s\n' "STACK_IMAGE=ghcr.io/andrew-chung-au/socboard@PASTE-DIGEST-HERE" STACK_PGDATA_DIR=/srv/socboard-data/postgres >> /run/socboard-deploy/stack-vars
```

Expected: no output, after you replaced the text `PASTE-DIGEST-HERE`. Use this block only if the one above gave an empty image.

#### Step 6.8.4: apply a rotation: run `db-init`, then recreate the app

```
docker compose --project-directory /opt/socboard/current --env-file /run/socboard-deploy/stack-vars -f /opt/socboard/current/compose.yaml -f /opt/socboard/current/deploy.override.yaml run --rm --no-deps db-init
```

Expected: the last line `db-init: roles, database and privileges are in place` (`compose/db_init.py`, `main`). The compose files are the current release's (`terraform/server/socboard-deploy.sh`, `compose()`, `link_current`). The database container must be running (`docker ps`).
If different: `db-init: could not connect to Postgres as its superuser...` means the superuser value and the data directory differ (6.7). Stop.
Risk: sets the owner and application roles' passwords to the file's values. Undo: put the old secret and run it again.

```
docker compose --project-directory /opt/socboard/current --env-file /run/socboard-deploy/stack-vars -f /opt/socboard/current/compose.yaml -f /opt/socboard/current/deploy.override.yaml up -d --no-deps --force-recreate --pull never --no-build app
```

Expected: the `app` container is recreated and becomes healthy within about 90 seconds (`docker ps` shows `(healthy)`). The app is down for the length of the restart (as in section 2). `VERIFY:` seen at stage (b).
If different: read `docker logs --tail 20 socboard-app-1` on the server only. The script redacts the eight values from the same 20 lines before it prints them (`terraform/server/socboard-deploy.sh`, `logs_of`) and this command does not, so do not paste the lines anywhere. If the app does not become healthy, send the last good digest (section 4).
Risk: restarts the live app. Undo: section 4.

#### Step 6.8.5: check with the smoke check

```
SOCBOARD_SEED_PASSWORD_LEAD="$(sed -n 's/^SOCBOARD_SEED_PASSWORD_LEAD=//p' /run/socboard-deploy/stack-vars)" SOCBOARD_INGEST_API_KEY="$(sed -n 's/^SOCBOARD_INGEST_API_KEY=//p' /run/socboard-deploy/stack-vars)" docker run --rm --pull never --network host -e SOCBOARD_SEED_PASSWORD_LEAD -e SOCBOARD_INGEST_API_KEY "$(docker inspect --format '{{.Config.Image}}' socboard-app-1)" python -m socboard.smoke http://127.0.0.1:8000
```

Expected: the five steps named in the output pass and the exit code is 0; it never prints a password, key or token (`README.md`, "Smoke check"). The two values are in the environment of that one `docker` process only, the way the script passes them (`terraform/server/socboard-deploy.sh`, `check_release`); they are not exported in the shell and not in the process list. `VERIFY:` seen at stage (b). Each full run adds one New case (`README.md`, "Smoke check").
If different: the output names the failing step; a login failure means the `lead` password in the database differs from the secret (section 5.4).
Risk: adds one case to the queue; deletes nothing.

#### Step 6.8.6: delete the file and check the folder is empty of it

```
rm -f /run/socboard-deploy/stack-vars
```

Expected: no output.
If different: an error means the folder is read-only or missing; stop and send what was printed.

```
ls -A /run/socboard-deploy
```

Expected: no `stack-vars` entry and no other file with values. The only entry may be `lock`, an empty file the script and Step 6.8.1 create (`terraform/server/socboard-deploy.sh`, section 1: the one file an "already deployed" run may create).
If different: a `stack-vars` entry means the first block did not run; run it again before you leave.
Risk: none.

Leave the root shell, then the session:

```
exit
```

```
exit
```

Expected: the first `exit` returns to the session's own shell, the second returns to your own machine's prompt.

## 7. Restore from a snapshot

Symptom: the database is lost, corrupted, or the previous release cannot run on the new schema (section 4's check, Step 4.2).
Check: the snapshot list (Step 7.1).
Fix: the restore, 7.2, from a scratch volume made from a snapshot of the data volume. It does not delete or detach the live volume, needs no Terraform change and no state change (Decision question 2 of #240, option A). The Terraform `prevent_destroy` on the data volume stays (`terraform/README.md`, "The server (instance, network and data volume)", "Teardown"). Undo: stop the stack, rename the aside folder back (Step 7.2.6).

This section uses the shortcuts from Before any command (`I`, `H`, `V`). It sets more as it goes: `SNAP` (the snapshot), `Z` (the zone), `S` (the scratch volume), and on the server `SN` and `DBI`. Each is echoed before it is used. If you open a new terminal in the middle of this section, run Before any command again and set the later ones again with the "lost the shortcut" blocks in the steps.

Facts. One snapshot a day at 03:00 UTC, the seven newest kept (`terraform/iam-and-budgets/main.tf`, `retain_rule`; `terraform/README.md`, "What it creates" under "The instance's IAM role, the snapshot schedule and the budgets"). A snapshot of a running Postgres is crash-consistent, so Postgres replays its log at start (issue #240, section "Restore (section 7)"; `VERIFY:` seen at the rehearsal). Data written after the snapshot is lost. Space: the live data volume is 10 GiB by default (`terraform/README.md`, "What it creates" under "The server"), and the restore keeps the old and the restored folders side by side, so check free space (Step 7.2.2). The data folder is `/srv/socboard-data/postgres` since #314 (`terraform/server/socboard-deploy.sh`, `DATA_DIR`; `terraform/README.md`, "The layout on the volume"). Prod's data folder, `postgres-prod`, is on the same volume and is not touched by anything here.

A scratch volume must not carry the tag `project=socboard`: the daily schedule snapshots every volume with it (`terraform/README.md`, "Rules for later changes", "The tag is a contract"). The commands below tag it `purpose=restore-scratch`.

Do not reboot the server while the scratch volume is attached: it holds a copy of the live volume's file system with the same UUID, and the server mounts its data volume by UUID (`terraform/README.md`, "What it does", "The data volume"), so a boot could mount the wrong one. `VERIFY:` this risk is the author's reading of the fstab-by-UUID rule, not seen.

### 7.1 Rehearse once on a scratch volume (nothing live changes)

The rehearsal is also the first half of the restore. It starts a throwaway `postgres:16` container with no network and no published port, on the scratch volume's own copy of the `postgres/` folder, counts the rows in `cases`, then removes everything. The live volume and the running stack are not touched and no snapshot is deleted. Choice the issue does not cover: the scratch volume is itself the copy, so the container runs on it directly and no second copy of the folder is made.

#### Step 7.1.1: list the snapshots

```
aws ec2 describe-snapshots --region us-east-1 --owner-ids self --filters Name=tag:project,Values=socboard --query 'sort_by(Snapshots,&StartTime)[].[SnapshotId,StartTime,VolumeId,State]' --output text
```

Expected: up to seven lines, oldest first, one a day at about 03:00 UTC, each `completed`. Note the newest one's age. `VERIFY:` the schedule copies the volume's tags to its snapshots (`terraform/README.md`, "What it creates" under the IAM part, "VERIFY:" on `copy_tags`; #207 stage (b) row 28 is still pending, `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`).
If different: no line may mean the tag was not copied: list by volume instead with the next block. No snapshot at all means the first run at 03:00 UTC has not happened yet; stop.
Risk: none, it only reads.

```
aws ec2 describe-snapshots --region us-east-1 --owner-ids self --filters Name=volume-id,Values="$V" --query 'sort_by(Snapshots,&StartTime)[].[SnapshotId,StartTime,VolumeId,State]' --output text
```

Expected: the same kind of list, found by volume. Run this block only when the one above printed nothing.
If different: nothing again means no snapshot exists; stop. An empty `V` gives an error: run the `V=` block of Before any command.

Read the newest snapshot's id into the shortcut `SNAP`:

```
SNAP=$(aws ec2 describe-snapshots --region us-east-1 --owner-ids self --filters Name=volume-id,Values="$V" --query 'sort_by(Snapshots,&StartTime)[-1].SnapshotId' --output text)
```

```
echo "SNAP=[$SNAP]"
```

Expected: `SNAP=[snap-` followed by hex digits `]`.
If different: `SNAP=[None]` or empty brackets mean no snapshot is listed for the volume; stop.

#### Step 7.1.2: read the zone of the data volume

```
Z=$(aws ec2 describe-volumes --region us-east-1 --volume-ids "$V" --query 'Volumes[0].AvailabilityZone' --output text)
```

```
echo "Z=[$Z]"
```

Expected: `Z=[us-east-1a]`, the default (`terraform/server/variables.tf`, `availability_zone`).
If different: use the zone printed; the scratch volume must be in the instance's zone. Empty brackets mean `V` is empty: run the `V=` block of Before any command.
Risk: none, it only reads.

#### Step 7.1.3: make the scratch volume from the snapshot

```
S=$(aws ec2 create-volume --region us-east-1 --availability-zone "$Z" --snapshot-id "$SNAP" --volume-type gp3 --tag-specifications 'ResourceType=volume,Tags=[{Key=purpose,Value=restore-scratch}]' --query VolumeId --output text); echo "S=[$S]"
```

Expected: `S=[vol-` followed by hex digits `]`. The volume is encrypted like its snapshot (`VERIFY:` AWS behaviour).
If different: an error names the cause (an unfinished snapshot, a wrong zone, an empty `Z` or `SNAP`).
Risk: a new volume that bills until deleted (Step 7.1.12). Undo: delete it.

Lost the shortcut `S` (a new terminal)? List the scratch volume by its tag:

```
aws ec2 describe-volumes --region us-east-1 --filters Name=tag:purpose,Values=restore-scratch --query 'Volumes[].[VolumeId,State]' --output text
```

Expected: one line, the scratch volume's id and state. In the next block, replace `PASTE-SCRATCH-VOLUME-ID-HERE` with that id (`vol-` and hex digits); run it only if you lost `S`.

```
S=PASTE-SCRATCH-VOLUME-ID-HERE
```

Expected: after the echo `echo "S=[$S]"`, `S=[vol-` and hex digits `]`.
If different: the text `PASTE-SCRATCH-VOLUME-ID-HERE` still showing means nothing was pasted. Two lines mean an older scratch volume exists: delete it first as Step 7.1.12 says.

```
aws ec2 wait volume-available --region us-east-1 --volume-ids "$S"
```

Expected: returns with no output once the volume is available.
If different: a timeout means it is not ready; run it again.

#### Step 7.1.4: attach it as a second device

```
aws ec2 attach-volume --region us-east-1 --volume-id "$S" --instance-id "$I" --device /dev/sdg
```

Expected: JSON with `State` `attaching`. `VERIFY:` the device name is free (the data volume's name is not written in this repository; `terraform/README.md` says only that it appears as an NVMe device).
If different: an error that the device is in use means use another letter in the block: `--device /dev/sdh`.
Risk: attaches a second volume to the live instance; the running stack does not use it. Undo: Step 7.1.11.

#### Step 7.1.5: mount it at a scratch folder

Start a session on the server. It stays open until Step 7.1.10; the shortcuts from your machine do not exist in it.

```
aws ssm start-session --region us-east-1 --target "$I"
```

Expected: a shell prompt on the server.
If different: `SessionManagerPlugin is not found` means the plugin is missing: use the AWS Console instead (see Before any command).

```
sudo mkdir -p /mnt/socboard-scratch
```

Expected: no output.

Set `S` inside the session. In the next block, replace `PASTE-SCRATCH-VOLUME-ID-HERE` with the scratch volume's id, which is the value you echoed as `S=[...]` on your own machine in Step 7.1.3 (`vol-` and hex digits):

```
S=PASTE-SCRATCH-VOLUME-ID-HERE
```

```
SN=${S//-/}
```

```
echo "S=[$S] SN=[$SN]"
```

Expected: `S=[vol-` and hex digits `] SN=[vol` and the same hex digits without the dash `]`.
If different: the text `PASTE-SCRATCH-VOLUME-ID-HERE` still showing means nothing was pasted. Anything but `SN=[vol...` with no dash means retype the `SN=` block.

```
sudo mount "/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_$SN" /mnt/socboard-scratch
```

Expected: no output. The device link has this shape on the host (`terraform/README.md`, "What it does", "The data volume", which names `/dev/disk/by-id/nvme-Amazon_Elastic_Block_Store_vol...`). It is mounted by path, never by UUID.
If different: `ls /dev/disk/by-id/` shows the names; a missing link means the attach is not finished (wait a minute). Do not mount `/srv/socboard-data` again.
Risk: none to the live volume.

#### Step 7.1.6: read the Postgres version file and the layout

```
sudo cat /mnt/socboard-scratch/postgres/pgdata/PG_VERSION
```

Expected: `16`, the major version of the image (`compose.yaml`, `db`: `postgres:16.15`). Record it. The `pgdata` folder is the stack's `PGDATA` (`compose.yaml`, `db`).
If different: another number means the data was not made by this stack's Postgres 16; stop. An error that the folder is missing means the layout differs from #314's; stop and run `sudo ls /mnt/socboard-scratch`.

#### Step 7.1.7: start a throwaway Postgres on the scratch copy

Read the database image the stack uses into the shortcut `DBI` (inside the session):

```
DBI=$(sudo docker inspect --format '{{.Config.Image}}' socboard-db-1)
```

```
echo "DBI=[$DBI]"
```

Expected: `DBI=[` and an image name with its digest, from `compose.yaml` (`db`, `image`) `]`. `VERIFY:` the container name (project `socboard`, service `db`).
If different: empty brackets mean the stack's `db` is not running: use the image line of `compose.yaml` at the revision deployed, and set `DBI` to it by hand.

```
sudo docker run -d --name socboard-restore-rehearsal --network none -v /mnt/socboard-scratch/postgres:/var/lib/postgresql/data -e PGDATA=/var/lib/postgresql/data/pgdata "$DBI"
```

Expected: one container id. It is not the stack's container, has no network and publishes no port. No password is given: the folder is already initialised, so the image does not need one (`VERIFY:` the image's start-up behaviour).
If different: a message that the database is uninitialised and no password is set means the folder is empty or is the wrong one; remove the container (Step 7.1.9) and stop.
Risk: starts a container on the scratch volume only; it writes to the scratch volume's files. Undo: Step 7.1.9.

```
sudo docker logs --tail 5 socboard-restore-rehearsal
```

Expected: lines that include `database system is ready to accept connections`; before them, after a snapshot of a running database, `automatic recovery in progress` (crash recovery). `VERIFY:` seen at the rehearsal. The log holds no secret.
If different: a repeated error line means the data is not usable; record it; the snapshot is not a good restore source.

#### Step 7.1.8: count the rows

```
sudo docker exec socboard-restore-rehearsal psql -U postgres -d socboard -tAc "select count(*) from cases"
```

Expected: one whole number, the number of cases at the time of the snapshot (`socboard/models.py`, table `cases`). `VERIFY:` the local socket needs no password in the official image.
If different: `relation "cases" does not exist` means the snapshot is from before the first migration. A login failure means record it and continue to clean up.
Risk: none, it only reads.

#### Step 7.1.9: remove the container

```
sudo docker rm -f socboard-restore-rehearsal
```

Expected: the container name. `sudo docker ps -a` no longer lists it.
If different: an error that it does not exist is fine.

#### Step 7.1.10: unmount

```
sudo umount /mnt/socboard-scratch
```

Expected: no output.
If different: `target is busy` means a container or shell still uses it; leave the shell's folder and check Step 7.1.9.

Leave the session; the next steps run on your own machine, where `S` and `V` are set:

```
exit
```

Expected: your own machine's prompt returns.

#### Step 7.1.11: detach the scratch volume

Check the id is the scratch one, not the live data volume:

```
echo "S=[$S] V=[$V]"
```

Expected: two different volume ids.
If different: the same id twice, or an empty one, means stop: do not detach anything.

```
aws ec2 detach-volume --region us-east-1 --volume-id "$S"
```

Expected: JSON with `State` `detaching`.
If different: a refusal that the volume is in use means Step 7.1.10 did not finish.
Risk: none to the live volume, it is another volume.

```
aws ec2 wait volume-available --region us-east-1 --volume-ids "$S"
```

Expected: returns with no output.
If different: a timeout means it is still detaching; run it again.

#### Step 7.1.12: delete the scratch volume (human only)

```
aws ec2 describe-volumes --region us-east-1 --volume-ids "$S" --query 'Volumes[0].Tags' --output text
```

Expected: only `purpose` and `restore-scratch`, no `project`. This is the check that the id is not the live volume.
If different: if a `project` tag is shown, stop: this may be the live data volume. Delete nothing.

```
aws ec2 delete-volume --region us-east-1 --volume-id "$S"
```

Expected: no output; the volume no longer shows in the next block.
If different: an error that the volume is in use means Step 7.1.11 did not finish.
Risk: deletes the scratch volume and its copy of the data; the snapshot stays. This command is run by the human only and can't be undone. The live data volume and the live data were not touched: the human writes that in the result file.

```
aws ec2 describe-volumes --region us-east-1 --filters Name=tag:purpose,Values=restore-scratch --query 'Volumes[].VolumeId' --output text
```

Expected: no output.
If different: an id means a scratch volume remains: set `S` to it and delete it as above.

### 7.2 The restore

The live `postgres/` folder is renamed aside, never deleted, and the restored one is copied in from a scratch volume. Do Steps 7.1.1 to 7.1.5 (list, zone, make, attach, mount; the session of Step 7.1.5 is the one the next steps use), then:

#### Step 7.2.1: check the scratch copy first

Run Steps 7.1.6 to 7.1.9 (the version file, the throwaway container, the row count, the removal). Expected: as there. If different: choose another snapshot; do not go on.

#### Step 7.2.2: check the free space on the live volume

In the server session:

```
sudo df -h /srv/socboard-data
```

Expected: free space at least the size of the `postgres/` folder, shown by the next command.
If different: not enough space means stop; copying would fill the volume and stop Postgres.

```
sudo du -sh /mnt/socboard-scratch/postgres
```

Expected: a size smaller than the free space above.

#### Step 7.2.3: stop the stack

Before you stop it, read the image dev runs, because Step 7.2.7 sends it again:

```
sudo docker inspect --format '{{.Config.Image}}' socboard-app-1
```

Expected: `ghcr.io/andrew-chung-au/socboard@sha256:` followed by 64 hex digits. The part after `@` is the digest for Step 7.2.7: keep it (write it down or leave this window open). You paste it there in place of `PASTE-DIGEST-HERE`.
If different: `no such object` means the app is not running: use the digest of the last good deploy (Step 2.1.2 or 4.1).

```
sudo docker stop socboard-app-1 socboard-db-1
```

Expected: the two names. `sudo docker ps` shows neither. A container stopped by hand with `restart: unless-stopped` stays stopped until started (`terraform/server/socboard-deploy.sh`, the override file, section 5). `VERIFY:` both names.
If different: a name that does not exist means check `sudo docker ps --format '{{.Names}}'` and stop the right ones.
Risk: the app is down until Step 7.2.7. Undo: `sudo docker start socboard-db-1 socboard-app-1`, only before Step 7.2.5.

#### Step 7.2.4: keep the old folder aside

```
sudo mv /srv/socboard-data/postgres /srv/socboard-data/postgres.aside
```

Expected: no output; the folder now has another name on the same volume. The old folder is **renamed, not deleted**, and is kept until the restored stack has passed the smoke check (Step 7.2.7).
If different: an error that the target exists means an earlier restore left one; choose a different name, never overwrite.
Risk: the stack has no database until Step 7.2.5. Undo: Step 7.2.6.

#### Step 7.2.5: copy the snapshot's folder in

```
sudo cp -a /mnt/socboard-scratch/postgres /srv/socboard-data/postgres
```

Expected: no output.
If different: an error about space or a missing source means stop and run Step 7.2.6.
Risk: writes the restored data into the live folder. Data written after the snapshot is lost.

```
sudo stat -c '%U:%u:%a' /srv/socboard-data/postgres
```

Expected: uid 999 and mode 700 as in `terraform/README.md`, "The layout on the volume" (`cp -a` keeps owner and mode).
If different: a different owner or mode means the Postgres container cannot start; stop and run Step 7.2.6.

#### Step 7.2.6: undo (only if the restore must be abandoned)

The restored `postgres/` must be moved out of the way first; no step in this runbook deletes it, so rename it:

```
sudo mv /srv/socboard-data/postgres /srv/socboard-data/postgres.restored-failed
```

Expected: no output.
If different: an error that `postgres` does not exist means there is nothing to move: carry on.

```
sudo mv /srv/socboard-data/postgres.aside /srv/socboard-data/postgres
```

Expected: no output; the old folder is back.
If different: if the target exists, rename it, as above.
Risk: none to data beyond the rename.

#### Step 7.2.7: start the stack by sending the digest that was running

Leave the session first (the next commands run on your own machine):

```
exit
```

Expected: your own machine's prompt returns.

The app is stopped, so the script's "already deployed" check does not stop the run (it needs the app running and healthy, `terraform/server/socboard-deploy.sh`, section 3), and a full deploy runs: `db` starts on the restored folder, `db-init` sets the owner and application passwords, `migrate` and `seed` run, and the checks include the smoke check. Send the digest the stack ran before. Set `D` to the digest you kept at Step 7.2.3: in the next block, replace `PASTE-DIGEST-HERE` with the part after `@` (`sha256:` and 64 hex digits):

```
D=PASTE-DIGEST-HERE
```

```
echo "D=[$D]"
```

Expected: `D=[sha256:` and 64 hex digits `]`.
If different: the text `PASTE-DIGEST-HERE` is still there: paste the digest.

Now send it and read the result as Steps 2.2.2 and 2.2.3 do:

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"]}' --instance-ids "$I" --query Command.CommandId --output text); echo "C=[$C]"
```

Expected: `C=[` and a command id `]`.
If different: as Step 2.2.2.

```
aws ssm get-command-invocation --region us-east-1 --command-id "$C" --instance-id "$I" --query '{Status:Status,Code:ResponseCode,Output:StandardOutputContent}' --output json
```

Expected: `socboard-deploy: deployed.` with code 0 (wait and run again while `InProgress`). If the secret's superuser value was changed after the snapshot, `db-init` fails (exit 5, section 3): the restored data holds the old value (`compose/db_init.py`, `LOGIN_FAILED`).
If different: read the exit code in section 3.

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$H/api/health"
```

Expected: `200`.
If different: another code means the app is not serving: read section 3.

#### Step 7.2.8: clean up

Do Steps 7.1.10 to 7.1.12 (start a session, unmount, leave, detach, delete the scratch volume). Leave `/srv/socboard-data/postgres.aside` in place. No step of this runbook deletes it, the live data folder or the data volume; deleting the aside folder is a separate decision for the human, after the restored stack has been used for as long as you choose, and it is not given here.

## 8. Certificate failure

Symptom: `https://HOSTNAME/` (the value of `H`) shows a certificate warning or a timeout, while the app is healthy on the server.
Check: the three checks below tell the causes apart. Fix: the cause's row. Undo: set `acme_ca` back (Step 8.4).

What the repository supports today: `acme_ca` accepts only the Let's Encrypt production or staging address; changing it replaces the instance and keeps the certificate data on the data volume (`terraform/server/variables.tf`, `acme_ca`; `terraform/README.md`, "Changed user data replaces the instance"). A staging certificate is not trusted by browsers: it is a test only (`terraform/README.md`, "Steps for the human in D19b", Step 4 and Step 8). There is no other certificate authority and no second DNS name (Decision question 3 of #240, option 2: diagnose and wait, staging only for tests, and a follow-up issue for another DNS name; follow-up not filed yet).

Limits Let's Encrypt applies: 5 duplicate certificates for the same names in 7 days, and a weekly limit per registered domain that every sslip.io user shares unless sslip.io is on the Public Suffix List (`terraform/README.md`, "Changed user data replaces the instance"). `VERIFY:` the current figures at Let's Encrypt's own documentation; they are not a file of this repository.

### Step 8.1: read what the world sees

With the shortcuts from Before any command (`H` for dev, `PH` for prod, which has its own certificate, `terraform/README.md`, "The prod stack beside dev (issue #266)").

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$H/api/health"
```

Expected: `200` with no certificate warning. A certificate error or a timeout is the symptom (`terraform/README.md`, "Steps for the human in D19b", Step 8).
If different: note the error text (`curl` prints it); go to Step 8.2. An empty `H` gives an error about the URL: run the `H=` block of Before any command.
Risk: none, it only reads.

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$PH/api/health"
```

Expected: `200` with no certificate warning. Run it to see whether prod has the same fault.
If different: as above.
Risk: none, it only reads.

```
echo | openssl s_client -connect "$H:443" -servername "$H" 2>/dev/null | openssl x509 -noout -serial -issuer -dates
```

Expected: a `serial=`, an issuer that names Let's Encrypt, and two dates that include today. An issuer that names a staging authority means `acme_ca` is staging. No output means no certificate is served (`terraform/README.md`, "Steps for the human in D19b", Step 2).
If different: expired dates mean renewal failed; go to Step 8.2.
Risk: none, it only reads.

### Step 8.2: read Caddy's log on the server

In a session:

```
aws ssm start-session --region us-east-1 --target "$I"
```

Expected: a shell prompt on the server.
If different: `SessionManagerPlugin is not found`: use the AWS Console instead (see Before any command).

```
sudo journalctl -u caddy --no-pager -n 50
```

Expected: no error lines about the ACME order. The log holds no secret (`terraform/README.md`, "What it does", "Caddy": the Caddyfile holds none; `VERIFY:` the first real log). Read the cause: a rate-limit message names the limit hit; a message about the challenge failing points to DNS (Step 8.3) or to the ports; the next block says whether Caddy runs at all (it does not start without the data volume, `terraform/README.md`, "What it does", "The data volume").
If different: do not paste the log into an issue before reading it for anything that looks like a value.
Risk: none, it only reads.

```
sudo systemctl is-active caddy docker
```

Expected: `active` twice.
If different: `inactive` or `failed` on the first line means Caddy is not running: read the journal above.

```
exit
```

Expected: your own machine's prompt returns.

### Step 8.3: check the name resolves to the server

```
getent hosts "$H"
```

Expected: one line with the server's address; sslip.io resolves the dashed name to it (`terraform/README.md`, "The prod stack beside dev (issue #266)", "Why the hostnames differ by a prefix": read with `getent hosts` on 2026-11-16). The security group allows TCP 80 and 443 in from anywhere and nothing else (`terraform/README.md`, "What it creates" under "The server").
If different: no line means the DNS service or your resolver is the cause: wait and try again.
Risk: none, it only reads.

### Step 8.4: the fallback, test with staging

Only to find out whether the cause is the rate limit, with the human's decision, because it replaces the instance. Follow `terraform/README.md`, "Steps for the human in D19b", Step 4's staging command (it is a Terraform apply there; this file does not repeat it); it replaces the instance and leaves the stack down until the next deploy. After the test, set `acme_ca` back, which is another replacement, so do both only when you mean it. The limit means avoiding repeated replacements in one week (`terraform/README.md`, "Changed user data replaces the instance"). A browser trusts a staging certificate nowhere.

Expected: a staging certificate issued, which proves the path works and that the rate limit was the cause.
If different: if staging also fails, the cause is not the limit: read Step 8.2 again.
Risk: replaces the instance; the old root disk is deleted; both stacks are down until the next deploy; `DEPLOY_INSTANCE_ID` becomes stale (Section 1, Step 1.1), and so does `I`: run the `I=` block of Before any command again after the replacement. Undo: none, it replaces again.

## 9. Teardown

Order: the server (`terraform/server/`), then `terraform/iam-and-budgets/`, then `terraform/ci-access/`, then `terraform/state/` last (`terraform/README.md`, "Teardown" of each part, "Deploy item D23"). Each step links the README's own "Teardown" section and does not copy its steps, so a change to a part's teardown changes one place. Everything here is the human's step and destructive; nothing is run by default, and no step deletes the state bucket, a secret, a snapshot or the image package unless its own `Decision:` step is chosen.

Run each part's README steps with your credentials in your shell, from the repository root (every command here uses `-chdir`). Read section 10 first: the evidence has to outlive the server.

### Step 9.0: take a last snapshot, only if the data should be kept

With `V` set (Before any command):

```
aws ec2 create-snapshot --region us-east-1 --volume-id "$V" --description "socboard last snapshot" --tag-specifications 'ResourceType=snapshot,Tags=[{Key=project,Value=socboard}]' --query SnapshotId --output text
```

Expected: one snapshot id. It is billed until deleted by hand (Decision 9.D2 below), because destroying `iam-and-budgets/` stops the expiry (`terraform/README.md`, "Teardown (the human's step, destructive)" of the IAM part).
If different: skip this step if the data is not needed. An error about an empty volume id means `V` is empty: run the `V=` block of Before any command.
Risk: a billed snapshot. Undo: Decision 9.D2.

### Step 9.1: the server

Follow `terraform/README.md`, "The server (instance, network and data volume)", "Teardown (the human's step, destructive)": remove the `prevent_destroy` block of `aws_ebs_volume.data` by hand (the only manual edit), then `terraform destroy`. Check, before `destroy`:

```
terraform -chdir=terraform/server plan -destroy
```

Expected: `Plan: 10 to destroy.` (`terraform/README.md`, "Teardown (the human's step, destructive)" of the server part). No "Instance cannot be destroyed" line once the block is removed. Terraform's own check refuses a plan that would destroy the data volume while the block is in place: that is the refusal, not a fault.
If different: any other count means stop and read the plan.
Risk: none, it only reads.

After `destroy`:

```
terraform -chdir=terraform/server state list
```

Expected: no output (`Destroy complete! Resources: 10 destroyed.`, same section).
If different: a listed resource means it still exists; read the destroy output.
Risk: none. Restore the `prevent_destroy` block, or do not commit its removal, unless the deployment is gone for good (same section, step 4).

### Step 9.2: `iam-and-budgets/`

Follow `terraform/README.md`, "The instance's IAM role, the snapshot schedule and the budgets", "Teardown (the human's step, destructive)": move its state back to a local file, then `terraform destroy`. Snapshots outlive it and are billed until deleted (Decision 9.D2). After the state is local:

```
terraform -chdir=terraform/iam-and-budgets plan -destroy
```

Expected: `Plan: 8 to destroy.` (same section). Destroying it also removes the budget notifications, so do the snapshot Decision (9.D2) in the same sitting.
If different: stop and read the plan.
Risk: none, it only reads.

### Step 9.3: `ci-access/`

Follow `terraform/README.md`, "CI access (the GitHub OIDC provider and three roles)", "Teardown (the human's step, destructive)": state back to local, `terraform destroy`.

```
terraform -chdir=terraform/ci-access plan -destroy
```

Expected: `Plan: 7 to destroy.`, or 6 if the account's own OIDC provider was reused (same section).
If different: stop and read the plan.
Risk: none, it only reads. After the destroy, CI cannot assume any role.

### Step 9.4: confirm the other parts' state is local before the bucket is touched

Each part's state must be a local file, not the bucket, before the bucket is emptied (`terraform/README.md`, "Teardown (the human's step, destructive)" of the state part). A step that empties the bucket before `terraform destroy` of the three other parts has run is not in this file. Run the three blocks:

```
terraform -chdir=terraform/iam-and-budgets state list
```

Expected: no output, because the part was destroyed (the commands above).
If different: a listed resource means it was not destroyed; stop; do not go to Decision 9.D5.

```
terraform -chdir=terraform/ci-access state list
```

Expected: no output.
If different: as above.

```
terraform -chdir=terraform/server state list
```

Expected: no output.
If different: as above.

### The leftovers: what Terraform does not delete and what it costs

Terraform does not delete these. Each is a `Decision:` step with "keep" and "delete" and a command for each; none runs by default (Decision question 5 of #240, option 1).

| Leftover | Why it stays | Cost | Source |
|---|---|---|---|
| The state bucket | `force_destroy = false`; it holds every state version | storage only; noncurrent versions expire after 90 days | `terraform/README.md`, "Teardown (the human's step, destructive)", "What is deliberately not here" |
| The secrets `socboard/app` and `socboard/app-prod` | created by hand, outside Terraform | per secret per month while they exist; `VERIFY:` whether one scheduled for deletion bills during its recovery window | `terraform/README.md`, "Steps for the human (not yet run)" of the IAM part, "Prod secret (issue #268)" |
| The snapshots | destroying `iam-and-budgets/` stops their expiry | billed until deleted | `terraform/README.md`, "Teardown (the human's step, destructive)" of the IAM part |
| The package `ghcr.io/andrew-chung-au/socboard` | not an AWS resource | none known; `VERIFY:` GitHub's current terms for public packages | `README.md`, "Published image" |
| The GitHub Environments `infra`, `deploy`, `deploy-prod`, their variables, and the repository secrets that name the roles | GitHub settings, not Terraform | none | `terraform/README.md`, "CI access", "Prod access" |

#### Decision 9.D1: the secrets `socboard/app` and `socboard/app-prod` (keep or delete)

Keep: do nothing. They hold random values and stay billed. Delete (human only), dev's secret first:

```
aws secretsmanager delete-secret --region us-east-1 --secret-id socboard/app --recovery-window-in-days 7
```

Expected: JSON with a `DeletionDate` seven days ahead.
If different: an error that the secret is not found means it is already gone.
Risk: the secret is scheduled for deletion and unusable; recoverable until the date with `aws secretsmanager restore-secret --region us-east-1 --secret-id socboard/app`. After the date it can't be undone.

Then prod's secret:

```
aws secretsmanager delete-secret --region us-east-1 --secret-id socboard/app-prod --recovery-window-in-days 7
```

Expected: JSON with a `DeletionDate` seven days ahead.
If different: as above.
Risk: as above; recoverable with `aws secretsmanager restore-secret --region us-east-1 --secret-id socboard/app-prod` until the date.

#### Decision 9.D2: the snapshots (keep or delete)

Keep: do nothing; they bill until you delete them. Delete (human only), one command per snapshot id from the list:

```
aws ec2 describe-snapshots --region us-east-1 --owner-ids self --filters Name=tag:project,Values=socboard --query 'Snapshots[].SnapshotId' --output text
```

Expected: the ids of the snapshots that remain, up to seven plus Step 9.0's. Keep this list: you paste each id, one at a time, in place of `PASTE-SNAPSHOT-ID-HERE` below.
If different: no output means none remain.
Risk: none, it only reads.

For each id, set the shortcut `SNAP` first. In the next block, replace `PASTE-SNAPSHOT-ID-HERE` with one id from the list above (`snap-` and hex digits), then echo it:

```
SNAP=PASTE-SNAPSHOT-ID-HERE
```

```
echo "SNAP=[$SNAP]"
```

Expected: `SNAP=[snap-` followed by hex digits `]`.
If different: the text `PASTE-SNAPSHOT-ID-HERE` still showing means nothing was pasted.

```
aws ec2 delete-snapshot --region us-east-1 --snapshot-id "$SNAP"
```

Expected: no output; the id no longer shows in the list above. Repeat the three blocks once per id.
If different: an access error means your credentials may not delete snapshots (CI's apply role cannot, by design, `terraform/README.md`, "CI access", "CI makes no IAM change").
Risk: deletes a backup. This can't be undone. Do it only when the data is not needed.

#### Decision 9.D3: the published image package (keep or delete)

Keep: reviewers can still pull the image by digest. Delete (human only):

```
gh api -X DELETE /user/packages/container/socboard
```

Expected: no output, status 204. `VERIFY:` the token needs the `delete:packages` scope, and the package may belong to an organisation endpoint instead.
If different: a 403 or 404 means the scope or the endpoint is wrong; use the package's settings page in the browser.
Risk: the image and every digest links to it are gone; can't be undone. The README's digest links stop working (section 10).

#### Decision 9.D4: the GitHub Environments, variables and secrets (keep or delete)

Keep: they name roles that no longer exist and do nothing. Delete (human only), one Environment each. The first:

```
gh api -X DELETE repos/andrew-chung-au/socboard/environments/deploy
```

Expected: no output, status 204.
If different: a 404 means it does not exist.
Risk: removes the Environment, its variables and its protection rules, which can be made again by hand.

```
gh api -X DELETE repos/andrew-chung-au/socboard/environments/infra
```

Expected: no output, status 204.
If different: a 404 means it does not exist.
Risk: as above.

```
gh api -X DELETE repos/andrew-chung-au/socboard/environments/deploy-prod
```

Expected: no output, status 204.
If different: a 404 means it does not exist.
Risk: as above.

The repository secrets that name the roles, one block each:

```
gh secret delete AWS_DEPLOY_ROLE_ARN --repo andrew-chung-au/socboard
```

Expected: a line saying the secret was deleted.
If different: an error that it is not found is fine.
Risk: the CI workflows that use it fail; it can be set again by hand.

```
gh secret delete AWS_PLAN_ROLE_ARN --repo andrew-chung-au/socboard
```

Expected: as above.
If different: as above.
Risk: as above.

```
gh secret delete AWS_APPLY_ROLE_ARN --repo andrew-chung-au/socboard
```

Expected: as above.
If different: as above.
Risk: as above.

```
gh secret delete AWS_DEPLOY_ROLE_ID --repo andrew-chung-au/socboard
```

Expected: as above.
If different: as above.
Risk: as above.

```
gh secret delete AWS_PLAN_ROLE_ID --repo andrew-chung-au/socboard
```

Expected: as above.
If different: as above.
Risk: as above.

#### Step 9.5: the gate before the last Decision

Run Step 9.4's three blocks again. Expected: as there. This is a gate for 9.D5.

#### Decision 9.D5: the state bucket (keep or delete)

Keep: do nothing. Delete (human only): follow `terraform/README.md`, "Teardown (the human's step, destructive)" of the state part, steps 1 to 4: remove `backend.tf`, move the state to local, empty the bucket of all object versions and delete markers, `terraform destroy`. Only after Step 9.5 passes. Check the plan first:

```
terraform -chdir=terraform/state plan -destroy
```

Expected: `Plan: 6 to destroy.` and, after the bucket is emptied and `terraform destroy` ran, `Destroy complete! Resources: 6 destroyed.` (same section).
If different: a non-empty bucket makes `destroy` fail (`force_destroy = false`): that is the refusal, not a fault.
Risk: deletes every Terraform state; can't be undone. Do not do it before the parts above are destroyed.

### Confirm nothing still bills

Read-only. Region `us-east-1`, filter `project=socboard`. Run each; each expected result is stated.

```
aws ec2 describe-instances --region us-east-1 --filters Name=tag:project,Values=socboard Name=instance-state-name,Values=pending,running,stopping,stopped --query 'Reservations[].Instances[].InstanceId' --output text
```

Expected: no output (no instance).
If different: an id means the server still exists; go back to Step 9.1.

```
aws ec2 describe-volumes --region us-east-1 --filters Name=tag:project,Values=socboard --query 'Volumes[].VolumeId' --output text
```

Expected: no output. The root volume is untagged and was deleted with the instance (`terraform/README.md`, "What it creates" under "The server").
If different: an id means the data volume or a stray volume remains.

```
aws ec2 describe-volumes --region us-east-1 --filters Name=tag:purpose,Values=restore-scratch --query 'Volumes[].VolumeId' --output text
```

Expected: no output (no scratch volume of section 7 left).
If different: delete it as Step 7.1.12 says.

```
aws ec2 describe-snapshots --region us-east-1 --owner-ids self --filters Name=tag:project,Values=socboard --query 'Snapshots[].SnapshotId' --output text
```

Expected: no output, unless Decision 9.D2 chose to keep them.
If different: ids mean snapshots that bill.

```
aws ec2 describe-addresses --region us-east-1 --filters Name=tag:project,Values=socboard --query 'Addresses[].AllocationId' --output text
```

Expected: no output (no Elastic IP address; an unattached one bills).
If different: an id means it remains; the server part was not fully destroyed.

```
aws secretsmanager list-secrets --region us-east-1 --query 'SecretList[].Name' --output text
```

Expected: no output, unless Decision 9.D1 chose to keep them.
If different: a name means a secret that bills.

```
aws secretsmanager list-secrets --region us-east-1 --include-planned-deletion --query 'SecretList[].[Name,DeletedDate]' --output text
```

Expected: a secret scheduled for deletion shows its date. `VERIFY:` whether a secret in its recovery window is billed; the human reads AWS's pricing page.
If different: no output means none is scheduled.

The bucket's name is in your own `terraform/state/terraform.tfvars` (git-ignored; the line `bucket_name`). Read it into the shortcut `B`:

```
B=$(sed -n 's/^bucket_name *= *"\(.*\)"/\1/p' terraform/state/terraform.tfvars)
```

```
echo "B=[$B]"
```

Expected: `B=[` and the bucket name you chose `]`. A bucket name is not a secret, but keep any account number out of anything you record.
If different: empty brackets mean the file is gone or the line is written another way: replace `PASTE-BUCKET-NAME-HERE` in the next block with the name you chose when you made the bucket, then echo again.

```
B=PASTE-BUCKET-NAME-HERE
```

```
aws s3api head-bucket --bucket "$B"
```

Expected: an error (`Not Found`, 404), meaning the bucket is gone. A reply with no error means it exists.
If different: no error is expected only when Decision 9.D5 chose keep.

One look at the billing console's cost for the next day: open the Billing console's Cost Explorer, choose the day after the teardown, group by service. Expected: no EC2, EBS or Secrets Manager charge for that day, apart from what Decisions 9.D1 and 9.D2 kept. Cost data lags by a day or more, so look again. `VERIFY:` the cost of each leftover is not known here.

## 10. What to keep before teardown

Peer reviewers cannot open the maintainer's AWS account or terminal; they read the README and follow links. The server runs for about a week, so before teardown every link the README relies on must work without the live server, and the README must say the URLs are no longer live (`.kiro/steering/evidence-and-steps.md`, rules 1, 4 and 5). Keep, as committed files or stable links:

- The URL as it was: the dev address, the value of `H` echoed in Before any command, written in the README as a past address, not as a link to follow. The same for prod's `PH`.
- A passing CI run link, from the next block (`VERIFY:` the field name).
- The deploy record: the artifact `deploy-record-dev` expires after 90 days (`README.md`, "Deploy to dev", "The record"), so copy its JSON (Step 4.1's download) into a committed record. It holds the digest, tag, revision and run, no secret.
- The restore rehearsal's result file, `_human-tasks/*-human-task-240-engineer-*.md`, linked from `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`.
- Screenshots of the live app and its certificate, committed as files.
- A recording is optional and never the only evidence (`.kiro/steering/evidence-and-steps.md`, rule 4).

```
gh run list --workflow verify.yml --repo andrew-chung-au/socboard --branch main --status success --limit 1 --json url
```

Expected: one JSON object with a `url` of a passing `socboard verify` run on `main`.
If different: an empty list means no passing run is listed; open the Actions tab and pick one by hand.
Risk: none, it only reads.

```
git status --short
```

Expected: no output after you commit what you kept.
If different: a listed file is not committed, so a reviewer cannot open it.
Risk: none, it only reads.
