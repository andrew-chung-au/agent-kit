# Update the deploy document, put prod's secret and run the first prod deploy

## Purpose

Update the Systems Manager document `socboard-deploy` to its second parameter, `environment`. Put the value of the prod secret `socboard/app-prod`. Deploy the digest dev is running to the prod stack once. Then check that prod answers, that dev did not change, that a repeat changes nothing, and that Systems Manager refuses a bad environment. Issue: #267. Merging #267 deploys nothing to prod, so this file is the first time the prod branch of the script runs for real.

First run: 2026-11-17, recorded in the table at the end. The steps were rewritten after that run (see "What changed after the first run").

## Where to run it

- On your own machine, with your own AWS credentials (SSO, region `us-east-1`).
- In a terminal opened at the **repository root** (`cd ~/projects/socboard`), on `main` after #267 merged. Every `terraform` command below uses `-chdir=terraform/...`, which only works from the root.
- Steps that run on the server say "on the server". They need the Session Manager plugin (`session-manager-plugin` prints "installed successfully"). Without it, use the AWS Console instead: EC2, the instance, Connect, Session Manager.
- Not here: the agent's sandbox, which has no Docker, Terraform or AWS access. The agent never runs `init`, `plan`, `apply` or a deploy.

**How to read the commands.** Copy each block exactly. Step 0 sets two shortcuts, `I` and `D`, that later blocks use. They exist only in the terminal where you set them: in a new terminal, run step 0 again. A send with an empty shortcut fails with `InvalidParameters`.

Destructive steps in this file: none. Step 14 (a reboot) stops both apps for the length of the boot, and it is your choice.

## Before you start

The instance role must be able to read prod's secret. #268 added this to `terraform/iam-and-budgets/`, but it takes effect only once that folder is re-applied with `app_prod_secret_arn` in its variable file. On 2026-11-17 it had not been, and the first prod send exited 3.

```
grep -c '^app_prod_secret_arn' terraform/iam-and-budgets/terraform.tfvars
```

Expected: `1`.
If different: `0` means the line is missing. Do #268's task file, step 1 (`_human-tasks/2026-11-15T2328Z-human-task-268-engineer-prod-access-apply.md`), then continue here.

```
terraform -chdir=terraform/iam-and-budgets plan -out=tfplan
```

Expected: `No changes.` (already applied), or `Plan: 0 to add, 1 to change, 0 to destroy.` with only `aws_iam_role_policy.read_app_secret` updated in place, its `Resource` list showing two secrets, `socboard/app-…` and `socboard/app-prod-…`.
If different: stop and tell the orchestrator the resource lines (not the ARNs).

If the plan showed `1 to change`:

```
terraform -chdir=terraform/iam-and-budgets apply tfplan
```

Expected: `Apply complete! Resources: 0 added, 1 changed, 0 destroyed.`

```
aws iam get-role-policy --role-name socboard-instance --policy-name read-app-secret --query 'length(PolicyDocument.Statement[0].Resource)' --output text
```

Expected: `2`.
If different: `1` means the instance can still read only dev's secret. Stop.

## Steps

### Step 0: set the two shortcuts

```
I=$(terraform -chdir=terraform/server output -raw instance_id)
```

```
echo "I=[$I]"
```

Expected: `I=[i-` followed by hex digits `]`.
If different: empty brackets mean you are not at the repository root, or Terraform has no state here. Stop.

### Step 1: read the hostnames and check dev answers

```
terraform -chdir=terraform/server output -raw hostname; echo
```

Expected: `<four numbers with dashes>.sslip.io`. This is the dev hostname.

```
terraform -chdir=terraform/server output -raw prod_hostname; echo
```

Expected: the same with `prod-` in front. This is the prod hostname.

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$(terraform -chdir=terraform/server output -raw hostname)/api/health"
```

Expected: `200`.
If different: stop. Dev is not healthy, so step 10's before-and-after check would prove nothing.

### Step 2: check prod's data folder (on the server)

```
aws ssm start-session --region us-east-1 --target $I
```

Expected: a `$` prompt on the server. The next two commands run there.
If different: "SessionManagerPlugin is not found" means the plugin is missing (see "Where to run it").

```
sudo stat -c '%u %a %n' /srv/socboard-data/postgres-prod
```

Expected: `999 700 /srv/socboard-data/postgres-prod`.
If different: stop. A folder Docker created itself is owned by root, and prod's database would not start.

### Step 3: record dev's container before anything runs (still on the server)

```
sudo docker inspect --format '{{.Id}} {{.State.StartedAt}} {{.Config.Image}}' socboard-app-1
```

Expected: one line with a container id, a start time and `ghcr.io/andrew-chung-au/socboard@sha256:` followed by 64 hex digits. Copy the whole line into the table as the "before" value. The part after `@` is the digest to send in step 8.
If different: `no such object` means dev is not running, or the command ran on your own machine (check that the prompt is the server's `$`).

```
exit
```

Back on your machine, set the digest shortcut. Paste the part after `@` in place of `PASTE-DIGEST`, so the line reads `D=sha256:` and 64 hex digits:

```
D=PASTE-DIGEST
```

```
echo "D=[$D]"
```

Expected: `D=[sha256:` and 64 hex digits `]`.

CI deploys every green push to `main` to dev. If one lands while you work, dev's container changes and step 10 compares against the wrong line. Check https://github.com/andrew-chung-au/socboard/actions/workflows/deploy-dev.yml before step 8, and redo step 3 if a deploy is running.

### Step 4: plan the document change

```
terraform -chdir=terraform/server plan
```

Expected: `Plan: 0 to add, 1 to change, 0 to destroy.` with only `aws_ssm_document.deploy` updated in place, or `No changes.` if the document is already updated.
If different: stop, don't apply, and tell the orchestrator the resource lines. If the instance is listed, the plan is not this change.

### Step 5: apply the document change (skip the apply if step 4 said `No changes.`)

```
terraform -chdir=terraform/server apply
```

Type `yes`. Expected: `Apply complete! Resources: 0 added, 1 changed, 0 destroyed.`
Risk: updates one Systems Manager document in place. A deploy that is running keeps the script it started with.

```
aws ssm describe-document --region us-east-1 --name socboard-deploy --query 'Document.Parameters[].[Name,DefaultValue]' --output text
```

Expected: `digest  None` and `environment  dev`.

```
aws ssm describe-document --region us-east-1 --name socboard-deploy --query 'Document.[DocumentVersion,LatestVersion,DefaultVersion]' --output text
```

Expected: three equal numbers. A send uses the default version.

### Step 6: make prod's secret value on your own machine

The file has one fixed path, so every command below can be copied exactly.

```
rm -f /tmp/socboard-prod-secret.json
```

```
install -m 600 /dev/null /tmp/socboard-prod-secret.json
```

Expected: no output. The file exists, is empty, and has mode 600.

The next command writes the eight values, random and different from dev's, and prints nothing. The three seed passwords become prod's users' passwords; the `lead` one is the smoke check's login.

```
python3 -c "import json, secrets, sys; names = ['SOCBOARD_TOKEN_SECRET', 'SOCBOARD_INGEST_API_KEY', 'SOCBOARD_SEED_PASSWORD_ANALYST_A', 'SOCBOARD_SEED_PASSWORD_ANALYST_B', 'SOCBOARD_SEED_PASSWORD_LEAD', 'STACK_PG_SUPERUSER_PASSWORD', 'STACK_PG_OWNER_PASSWORD', 'STACK_PG_APP_PASSWORD']; json.dump({n: secrets.token_hex(24) for n in names}, open(sys.argv[1], 'w'))" /tmp/socboard-prod-secret.json
```

```
ls -l /tmp/socboard-prod-secret.json
```

Expected: `-rw-------` and a size around 650 bytes. Never print the file.
If different: a size of `0` means the values were not written. Run the `python3` line again.

### Step 7: put the value, and delete the file

`file://` is followed by the path, which starts with `/`, so there are three slashes in a row.

```
aws secretsmanager put-secret-value --region us-east-1 --secret-id socboard/app-prod --secret-string file:///tmp/socboard-prod-secret.json
```

Expected: JSON with `ARN`, `Name` (`socboard/app-prod`) and `VersionId`, and no secret value.
If different: `Invalid length for parameter SecretString, value: 0` means the file is empty; go back to step 6. Nothing was stored.
Risk: sets prod's application secret. A later value can be put the same way. Dev's secret `socboard/app` is a different secret and is not touched.

```
rm /tmp/socboard-prod-secret.json
```

```
aws secretsmanager list-secret-version-ids --region us-east-1 --secret-id socboard/app-prod --query 'Versions[].VersionStages[0]' --output text
```

Expected: a list that includes `AWSCURRENT`.

### Step 8: send the first prod deploy

The parameters are JSON. The short form `digest=...,environment=prod` can be split wrongly by the AWS CLI.

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"],"environment":["prod"]}' --instance-ids $I --query Command.CommandId --output text); echo "C=[$C]"
```

Expected: `C=[` and a command id `]`.
If different: `InvalidParameters` usually means `D` or `I` is empty (`echo "D=[$D] I=[$I]"`), or the document has no `environment` parameter (step 5).
Risk: deploys prod on the server: pulls the images, migrates and seeds prod's empty database, starts prod's app. It touches nothing of dev's. A failure after the swap leaves prod's app stopped and prod's database running; dev keeps answering.

Wait one to three minutes, then:

```
aws ssm get-command-invocation --region us-east-1 --command-id $C --instance-id $I --query '[Status,ResponseCode,StandardOutputContent]' --output text
```

Expected: `Success  0  socboard-deploy: deployed.` (run it again while it says `InProgress`).
If different: record the code and the line, stop, and tell the orchestrator. Exit 3 means the secret could not be read or is not usable: check "Before you start" (the policy count `2`) and step 7 (`AWSCURRENT`). Exit 8 means a dev deploy holds the lock: send again in a minute. Exit 10 means prod's network gateway is not `10.231.78.1`.

### Step 9: check prod from your machine

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$(terraform -chdir=terraform/server output -raw prod_hostname)/api/health"
```

Expected: `200`. The certificate is issued on the first request, so try once more after ten seconds before you call it a failure.

### Step 10: check dev did not change (on the server)

```
aws ssm start-session --region us-east-1 --target $I
```

```
sudo docker inspect --format '{{.Id}} {{.State.StartedAt}} {{.Config.Image}}' socboard-app-1
```

Expected: the same line as step 3's "before" value.
If different: check whether CI deployed dev in between (the deploy-dev runs page). A deploy-dev run whose `deploy-record-dev` digest matches the new image explains the change. Otherwise the prod run touched dev: record both lines and stop.

```
sudo docker ps --format '{{.Names}}'
```

Expected: `socboard-app-1`, `socboard-db-1`, `socboard-prod-app-1` and `socboard-prod-db-1`, in any order.

```
sudo ss -ltn
```

Expected: the apps listen only on `127.0.0.1:8000` (dev) and `127.0.0.1:8100` (prod); neither port is on `0.0.0.0` or `*`.

```
exit
```

### Step 11: send the same digest to prod again

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"],"environment":["prod"]}' --instance-ids $I --query Command.CommandId --output text); echo "C=[$C]"
```

Wait a minute, then:

```
aws ssm get-command-invocation --region us-east-1 --command-id $C --instance-id $I --query '[Status,ResponseCode,StandardOutputContent]' --output text
```

Expected: `Success  0  socboard-deploy: already deployed. Nothing was changed.`
If different: `deployed.` means prod was running another digest (a promote from CI ran in between); record it.

### Step 12: send a bad environment, twice

Systems Manager should refuse each value before the script starts. If it did not, the script's own check refuses it with exit 2 and `socboard-deploy: refused: the environment must be dev or prod. Nothing was changed.`

```
aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"],"environment":["Prod"]}' --instance-ids $I
```

Expected: an `InvalidParameters` error, and no command id.

```
aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"],"environment":["staging"]}' --instance-ids $I
```

Expected: the same error.
If different (a command id comes back): read its result as in step 8 and record both.

### Step 13: send with no environment

This is a dev run, because the document's default is `dev`. Use dev's current digest: redo step 3's `docker inspect` if CI deployed dev since.

```
C=$(aws ssm send-command --region us-east-1 --document-name socboard-deploy --parameters '{"digest":["'"$D"'"]}' --instance-ids $I --query Command.CommandId --output text); echo "C=[$C]"
```

```
aws ssm get-command-invocation --region us-east-1 --command-id $C --instance-id $I --query '[Status,ResponseCode,StandardOutputContent]' --output text
```

Expected: `Success  0  socboard-deploy: already deployed. Nothing was changed.`
If different: `deployed.` means dev was not running that digest; a refusal means the default did not apply.

### Step 14: reboot the server (your choice; write SKIPPED in the table if you skip it)

```
aws ec2 reboot-instances --region us-east-1 --instance-ids $I
```

Risk: both apps are down until the stacks restart on their own (`restart: unless-stopped`).

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$(terraform -chdir=terraform/server output -raw prod_hostname)/api/health"
```

```
curl -sS -o /dev/null -w '%{http_code}\n' "https://$(terraform -chdir=terraform/server output -raw hostname)/api/health"
```

Expected: `200` from each within ten minutes.

## What changed after the first run

The first run (2026-11-17) hit each of these. The steps above now avoid them.
- The terraform commands used `-chdir=terraform/server`, but a sentence said to run in `terraform/server/`. They now say to run from the repository root.
- Placeholders such as `<secret file>` and `<digest>` were typed literally. The secret step now has one fixed path, and the instance id and digest are shortcuts set once in step 0 and step 3.
- `put-secret-value` read an empty `mktemp` file (`length 0`). The file is now made and filled at one path and its size checked.
- Sends with empty shortcuts in a new terminal gave `InvalidParameters`. The steps now echo each shortcut before use, and the sends use JSON parameters.
- The first send exited 3: the instance role could read only dev's secret, because `iam-and-budgets` had not been re-applied after #268. "Before you start" now checks the policy.
- Session Manager needed its plugin on the person's machine.

## Record the result

First run: 2026-11-17, by the maintainer, reported in the Kiro Web session and recorded by the agent. Commit this file with the result so a later run can compare (`.kiro/steering/evidence-and-steps.md`, rule 2). Results hold no secrets and no account number. After a teardown the hostnames are no longer live; this table, the CI runs and the pull requests stay readable.

| Step | Pass or fail | Output or note |
|---|---|---|
| Before 1 to 3: dev is deployed and healthy (`200` on the dev hostname) | PASS | Dev was deployed and healthy: CI deploy-dev run 44000643102 at 02:08 UTC printed `socboard-deploy: deployed.` and health `200` through Caddy. The maintainer's own `curl` of the dev URL was not reported. |
| 2: `stat` shows `/srv/socboard-data/postgres-prod` owned by 999 with mode 700 (from #266's apply) | PASS | `999 700 /srv/socboard-data/postgres-prod` |
| 3: dev's app container id, start time and image, before (copy the line) | PASS | `509629b710ee67321dbea294861bf6d58f005575f94f6a003c622ae77351e1c9 2026-11-17T01:28:17.370811137Z ghcr.io/andrew-chung-au/socboard@sha256:d9941ab8671de50823d6cd5e7a456fbcaf639a555082682356687a928b548023` (CI's deploy of `91d985f`) |
| 4: the document's plan shows only `aws_ssm_document.deploy` changed in place (`0 to add, 1 to change, 0 to destroy`) | PASS (already applied) | `No changes. Your infrastructure matches the configuration.` The document was already updated before this run (an earlier apply whose output was not recorded); the checkout was `91d985f`. |
| 5: apply of the document; `describe-document` lists `digest` and `environment` with default `dev` | PASS | `digest None` and `environment dev`; versions `5 5 5` (document, latest, default). |
| 6 and 7: the prod secret's value made from a file on your own machine (random values, different from dev's), put into `socboard/app-prod`, the file deleted, no value printed | PASS | One version with `AWSCURRENT`; no value printed. Two false starts first: the placeholder `<secret file>` was typed literally, so the values went into a file of that name in the repository folder (mode 600, never committed, then removed), and one `put-secret-value` read the empty `mktemp` file and was refused locally (`length 0`). The file deletion was reported by the maintainer, not checked by the agent. |
| 8: the first send with dev's running digest and `environment=prod` prints `socboard-deploy: deployed.` | PASS (second send) | Digest `sha256:d9941ab8…548023`. Two sends were refused by AWS with `InvalidParameters` because the shell shortcuts were empty. The first real send (command `15045c22-ab74-45e1-8fa1-902c28b0a0e9`) ended `Failed 3`: the instance role's `read-app-secret` policy listed only dev's secret. After the maintainer re-applied `terraform/iam-and-budgets` (`Apply complete! Resources: 0 added, 1 changed, 0 destroyed.`), the next send ended `Success 0 socboard-deploy: deployed.` |
| 9: the prod hostname's `/api/health` answers 200 with a valid certificate | PASS | The maintainer reported prod working. The promote run 44001761105 (02:18 UTC) checked `https://prod-44-216-250-242.sslip.io/api/health` through Caddy with certificate checks: `200`. |
| 10: dev's app container id, start time and image are the same as before, and the dev URL still answers 200 | PASS (explained change) | After: `673f085618d2260cba64fe31d2efcedbb44ac6d93e7f7ce2976dc2d04dcab5be 2026-11-17T02:08:17.1449338Z ghcr.io/andrew-chung-au/socboard@sha256:25446a296fa32d3320c88e862c073729e2de33204ccee8a4946093a346981d57`. The container changed because CI deployed `4d7abe0` to dev (run 44000643102, its `deploy-record-dev` digest is `sha256:25446a29…981d57`, sent 02:07 to 02:08 UTC), not because of the prod run. That run's health check answered `200`. |
| 10: `docker ps` shows `socboard-app-1` and `socboard-prod-app-1`; `ss -ltn` shows the apps only on 127.0.0.1:8000 and 127.0.0.1:8100 | PASS (`docker ps`); `ss` NOT CHECKED | `socboard-app-1`, `socboard-prod-app-1`, `socboard-prod-db-1`, `socboard-db-1`. `ss -ltn` was not run. |
| 11: the same send again says `socboard-deploy: already deployed. Nothing was changed.` | NOT CHECKED | Not run. Prod's next change was the promote run 44001761105, which deployed dev's newer digest (`deployed.`), so a repeat now needs that digest. |
| 12: a send with `environment=Prod` and one with `environment=staging` are refused by Systems Manager and change nothing | NOT CHECKED | Not run. The document's pattern, which allows only `dev` and `prod`, is asserted by `terraform test` in CI. |
| 13: a send with no environment is a dev run and says already deployed | NOT CHECKED | Not run. Every CI deploy-dev run sends `digest` only and deploys dev (for example run 44000643102), which shows the default applies. |
| 14: after a reboot both stacks come back (or SKIPPED) | NOT CHECKED | Not run. |

## Risk

Step 8 deploys prod for the first time: a failure after the swap leaves prod's app stopped (there is no previous prod release), and dev keeps running. Step 7 sets the prod secret, which cannot be undone for a first value. Nothing here destroys data or touches dev's secret, data folder or containers. The reboot in step 14 is your choice.
