# First apply, part A: state, IAM and budgets, CI access and the server

> **Record of a finished run.** The maintainer ran this checklist on 2026-11-15/16; its results are in "Record the result" below and in `_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`. Do not run it again. Its commands are as they were then: since #268, `iam-and-budgets/` also requires `app_prod_secret_arn`, so a new apply follows the steps in `terraform/README.md`, not this file.

## Purpose

Take the AWS account from nothing to the four Terraform parts applied (`state/`, `iam-and-budgets/`, `ci-access/`, `server/`), set the GitHub Environments, the repository secrets and the state bucket variable, and record every `VERIFY:` this apply can settle. Issue: #207 (Deploy item D19a).

**If a row fails:** write in its note what you saw, stop that line of work, and ask for a new issue. Never edit Terraform, a policy or a workflow during the apply to make a check pass; the fix goes through the new issue, and its number goes in the row.

**The repository is public.** Never paste into this file (or into a GitHub log you keep) the AWS account number, any ARN that contains it (role ARNs, the secret's ARN), the notification e-mail address, a token, a key or a secret value. Where a row asks about an ARN, write "ARN set" or "ARN ends in `<role name>/<session>`". The Elastic IP is a public address and may be written.

This file does not copy the apply commands. Each apply step names the section of `terraform/README.md` (or the #156 task file) that holds them, so a later fix there is not left stale here. Commands shown in full below are this checklist's own checks.

## Where to run it

Your own shell in the clean clone, with your own AWS credentials (never in a file in this repository), and a browser for GitHub's settings and the AWS console. Not here: the sandbox where the agents work, which has no AWS access. An agent never runs any step of this file.

## Before you start

1. The clean clone is on an up-to-date `main` with nothing changed.

```
git status --short --branch
```

Expected: `## main...origin/main` and no other line.

2. You have Terraform at the version in `terraform/.terraform-version`, the AWS CLI v2, and an hour for steps 1 to 8. Step 9 is the next day.

## Steps

### Step 1: Checks before any apply

```
terraform version
```

Expected: `Terraform v1.17.2`, the same as `terraform/.terraform-version`.

```
grep -n 'region *=' terraform/state/main.tf terraform/iam-and-budgets/main.tf terraform/ci-access/main.tf terraform/server/main.tf terraform/state/backend.tf.example terraform/iam-and-budgets/backend.tf.example terraform/ci-access/backend.tf.example terraform/server/backend.tf.example
```

Expected: eight lines, each `region = "us-east-1"` (spacing may differ). The account's home region is `ap-southeast-2`, so a default region in your CLI profile or the console can point elsewhere: every regional `aws` command in this file names `--region us-east-1`, and in the console pick "US East (N. Virginia)" before each check.

```
aws sts get-caller-identity --query Account --output text
```

Expected: the number of the account you intend to use. Read it; do not write it anywhere in this file.
If different: stop and switch credentials before anything is created.

### Step 2: Create the application secret, with no value

The proposed name is `socboard/app`. Its value is set by D20, not here.

```
aws secretsmanager create-secret --region us-east-1 --name socboard/app --description "socboard application secret - value set by D20" --tags Key=project,Value=socboard --query ARN --output text
```

Expected: one secret ARN ending in `:secret:socboard/app-` and six random characters. Put it in `app_secret_arn` in `terraform/iam-and-budgets/terraform.tfvars` (git-ignored) at that section's step 1. Do not paste it here.
If different: an error saying a value is required means a secret with no version cannot be created this way (row 2 FAIL); stop and ask for a new issue.
Risk: creates one secret (about 0.40 USD a month). Undo: `aws secretsmanager delete-secret --region us-east-1 --secret-id socboard/app` (deleted after a recovery window).

### Step 3: Apply `state/`, then `iam-and-budgets/`, then `ci-access/`

Budgets go before anything else that costs money, so the notifications exist first.

1. `terraform/README.md`, "Steps for the human (not yet run)" under the state bucket, steps 1 to 6, in `terraform/state/`.
   Expected: each step's own `Expected:` line; at the end `terraform state list` shows six resources and the local state files are deleted.
2. `terraform/README.md`, "The instance's IAM role, the snapshot schedule and the budgets", steps 1 to 6, in `terraform/iam-and-budgets/`. Set `monthly_budget_usd` above the expected spend (see Cost below, about 22 USD), or the 100 percent notice fires every month.
   Expected: each step's own `Expected:` line; the plan's inline policy names exactly the one secret ARN from step 2; the Lifecycle Manager policy is `ENABLED`. Note whether the lifecycle policy needed the second `terraform apply` (row 4).
3. `terraform/README.md`, "CI access (the GitHub OIDC provider and three roles)", steps 1 to 6, in `terraform/ci-access/`. Its step 7 is step 5 of this file.
   Expected: each step's own `Expected:` line, and three role ARNs printed (keep them in your terminal for step 4).

Each section says to commit that folder's `backend.tf` and `.terraform.lock.hcl`; do it as it says (row 29).
If different: stop at the first surprise, as each section says.

### Step 4: GitHub settings

In the repository's settings, in a browser:

1. Environment `infra`: "Required reviewers" on, with you (or the named reviewer) listed; "Allow administrators to bypass configured protection rules" off; "Deployment branches and tags" set to "Selected branches and tags" with one rule, `main`. If you are the only reviewer, leave "Prevent self-review" off, or no deployment can be approved.
2. Environment `deploy`: "Deployment branches and tags" set to "Selected branches and tags" with one rule, `main`.
3. Under "Secrets and variables", "Actions", the "Secrets" tab, as repository secrets (not variables): `AWS_PLAN_ROLE_ARN`, `AWS_APPLY_ROLE_ARN` and `AWS_DEPLOY_ROLE_ARN` from step 3.3's output. A role ARN contains the account number; GitHub Actions logs print variable values in clear text but mask secrets.
4. On the "Variables" tab: the repository variable `TF_STATE_BUCKET`, set to the state bucket name. It stays a variable because a bucket name does not identify the account, provided you chose one without the account number (`terraform/README.md`, state bucket, step 2).

Expected: the two Environments show the rules above, the Secrets tab lists the three role secrets, and the Variables tab lists `TF_STATE_BUCKET`. This covers the #156 task file's "Before you start" items 2 and 3, and the `AWS_PLAN_ROLE_ARN` secret it asks for in its step 1.
Risk: changes who may deploy. Undo: edit or delete the Environment, secret or variable in the same page.

Note: the secret `AWS_PLAN_ROLE_ID` was added later by #209 (set on 2026-11-16); see `terraform/README.md`, Outputs.

### Step 5: The #156 branch check

Do `_human-tasks/2026-11-14T0928Z-human-task-156-engineer-ci-access-apply-and-branch-check.md`, steps 1 to 5. Its "Before you start" is done by steps 3 and 4 above.

Refusal test: steps 2 and 3 of that file, in the GitHub Actions tab and the clean clone: a throwaway branch must not assume the apply role (`infra`) or the deploy role (`deploy`). Risk: if an Environment's branch rule is missing or wrong, the job prints "assumed" and that role's name (no key, no account number); that file says what to do.

Expected: that file's own `Expected:` lines. Record its results in its own table. Its probes print only "assumed" with the role and session name, or the AWS error code, and the role ARNs come from secrets, which Actions masks, so no log holds the account number.

### Step 6: Apply `server/`

#199 is merged to `main` (the server part is in `terraform/server/`). First check that the default zone offers T3:

```
aws ec2 describe-instance-type-offerings --region us-east-1 --location-type availability-zone --filters Name=instance-type,Values=t3.small --query 'InstanceTypeOfferings[].Location' --output text
```

Expected: a list of zones that includes `us-east-1a` (the default in `terraform/server/variables.tf`). Record whether `us-east-1e` is in it (row 12).
If different: if `us-east-1a` is missing, stop and ask for a new issue to change the default zone; do not override it with `-var`, because CI applies with the defaults later.

Then `terraform/README.md`, "The server (instance, network and data volume)", "Steps for the human (not yet run)", steps 1 to 6, in `terraform/server/`.

Expected: each step's own `Expected:` line, the three outputs printed, and the instance online in Systems Manager within about ten minutes.

Then, while the instance is online, open a shell on it from the console (Systems Manager, Session Manager, "Start session") and run:

```
sudo apt-get update
```

Expected: it ends with `Reading package lists... Done` and no `Failed to fetch` line (package mirrors through egress 80 and 443).

```
curl -sS -o /dev/null -w '%{http_code}\n' https://ghcr.io/v2/
```

Expected: `401` (the container registry is reachable; it only asks for a login).

```
lsblk -d -o NAME,SIZE
```

Expected: the root disk and a 10 GiB disk named `nvme1n1` or similar (the data volume, attached as `/dev/sdf`, shows as NVMe). End the session.

Then read the creation calls in the console: CloudTrail, "Event history", filter "Event name" for each of `RunInstances`, `CreateVolume`, `CreateSecurityGroup` and `AllocateAddress`.
Expected: each event's request has a tag specification with `project` = `socboard`. This is what #156's apply role requires (the tag in the create call), so it is evidence for the later CI apply (row 15).

And the security group's outbound rules:

```
aws ec2 describe-security-groups --region us-east-1 --filters Name=group-name,Values=socboard-server --query 'SecurityGroups[].IpPermissionsEgress[].[IpProtocol,FromPort,ToPort]' --output text
```

Expected: exactly two lines, `tcp 80 80` and `tcp 443 443`; no `-1` line (the allow-all rule AWS adds was removed).

Risk: the server costs money from here on and stays running (see Cost). Undo: the server teardown, linked below.

### Step 7: A second plan shows no changes

In each of `terraform/state/`, `terraform/iam-and-budgets/`, `terraform/ci-access/` and `terraform/server/`:

```
terraform plan
```

Expected: `No changes. Your infrastructure matches the configuration.` in all four.
If different: write the planned change in row 23 and ask for a new issue.

### Step 8: Refusal test, the plan role cannot write or read the secret

Refusal test: use the GitHub Actions tab and the clean clone, with a copy of the #156 task's step 1 workflow. Risk: if the plan role's policy is wrong, the tag write would be allowed, but it is a dry run (`--dry-run`), so nothing is changed, and the job prints `DryRunOperation`. If the secret deny is missing, the job prints `ResourceNotFoundException` (the secret has no value yet); it never prints a value, because the command asks only for the name. The log is public and an AWS error message can name the assumed role's full ARN, so the job prints only "assumed" or the AWS error code, never an error message or an ARN.

On a new branch `oidc-probe-plan-refusals`, add `.github/workflows/oidc-probe-plan-refusals.yml`:

```yaml
name: oidc-probe-plan-refusals
on: pull_request
permissions:
  id-token: write
  contents: read
jobs:
  probe:
    runs-on: ubuntu-latest
    steps:
      - name: Try one write and one secret read with the plan role
        env:
          ROLE_ARN: ${{ secrets.AWS_PLAN_ROLE_ARN }}
          AWS_DEFAULT_REGION: us-east-1
        run: |
          # Prints only the AWS error code from "An error occurred (<code>) ...", never the message.
          code() { grep -o -E '\([A-Za-z.]+\)' | head -n 1 | tr -d '()'; }
          TOKEN=$(curl -sS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.amazonaws.com" | jq -r .value)
          echo "::add-mask::$TOKEN"
          if ! CREDS=$(aws sts assume-role-with-web-identity --role-arn "$ROLE_ARN" --role-session-name probe-plan-refusals --web-identity-token "$TOKEN" --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' --output text 2>&1); then
            C=$(code <<< "$CREDS"); echo "assume: ${C:-OTHER}"; exit 1
          fi
          read -r AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN <<< "$CREDS"
          echo "::add-mask::$AWS_ACCESS_KEY_ID"
          echo "::add-mask::$AWS_SECRET_ACCESS_KEY"
          echo "::add-mask::$AWS_SESSION_TOKEN"
          export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
          echo "assume: assumed"
          INSTANCE_ID=$(aws ec2 describe-instances --filters Name=tag:project,Values=socboard Name=instance-state-name,Values=running --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null || true)
          CT=$(aws ec2 create-tags --dry-run --resources "$INSTANCE_ID" --tags Key=probe,Value=refused 2>&1 | code); echo "create-tags (dry run): ${CT:-OTHER}"
          GS=$(aws secretsmanager get-secret-value --secret-id socboard/app --query Name --output text 2>&1 | code); echo "get-secret-value: ${GS:-OTHER}"
```

Push the branch, open a draft pull request, and read the job's log.

Expected: `assume: assumed`, then `create-tags (dry run): UnauthorizedOperation` (EC2's form of access denied) and `get-secret-value: AccessDeniedException` (the explicit deny in `terraform/ci-access/plan.tf`). No other line from the job's commands.
If different: `DryRunOperation` or `ResourceNotFoundException` means the refusal failed (row 24 or 25 FAIL). Any other code (for example `InvalidID` if no running instance was found), or `OTHER`, means the check did not run as meant: re-run the same call by hand with your own credentials only if you understand why, otherwise record NOT SETTLED. Either way, stop and tell the orchestrator.

Clean up: close the draft pull request, delete the branch and the run.

```
git push origin --delete oidc-probe-plan-refusals
```

Expected: the branch is gone; in the Actions tab, delete the run ("Delete workflow run").

### Step 9: The next day, the snapshot

After 04:00 UTC on the day after the apply (the schedule is set for 03:00 UTC, and Data Lifecycle Manager can start up to an hour late):

```
aws ec2 describe-snapshots --region us-east-1 --owner-ids self --filters Name=tag:project,Values=socboard --query 'Snapshots[].[VolumeId,StartTime,State]' --output text
```

Expected: one snapshot per day since the apply, each with the data volume's id (`terraform output data_volume_id` in `terraform/server/`) and state `completed`. Being listed at all shows the tag was copied (`copy_tags`). No snapshot of the root volume.
If different: an empty list can mean no snapshot or a snapshot without the tag. Look in the EC2 console (Snapshots) for a snapshot of the data volume and record which (row 28).

## Record the result

Filled on 2026-11-16 by the planning session from the maintainer's run and outputs (maintainer's run, 2026-11-15/16). "As reported" means the maintainer reported the result and the output was not kept.

Write PASS, FAIL or NOT SETTLED in each row, with a short note. A FAIL note says what you saw and links the new issue. Commit this file with the results. Results contain no account number, no ARN with it, no e-mail address, no token, key or secret value.

| Row | What is checked | Source | Result | Note |
|---|---|---|---|---|
| 1 | Terraform is 1.17.2; every provider and backend example names `us-east-1`; the caller is the intended account | step 1 | PASS | Terraform v1.17.2 installed as the exact release binary (SHA-256 checked against HashiCorp's list) beside an older package copy; the shell's cached path had to be cleared (`hash -r`). Every resource landed in `us-east-1`. Caller: the SSO member account (profile `socboard`), after a first attempt ran in the organisation's main account by mistake (see the evidence timeline). |
| 2 | A secret with no version can be created and its ARN used by `iam-and-budgets/` | step 2; `iam-and-budgets/main.tf` (`read_app_secret`) | PASS | `socboard/app` created empty in the member account and its ARN used by `iam-and-budgets/` (plan named only that secret). |
| 3 | `state/` steps 1 to 6 as expected: 6 resources, provider 6.x and backend argument names accepted, the empty lifecycle `filter {}` gives no warning, the native lock file seen | step 3.1; `state/main.tf`, `state/backend.tf.example` | PASS | 6 resources, `No changes` after the move, state in the bucket under `state/`. Lock file and the lifecycle-filter warning not observed. In the first (main-account) attempt the local state was deleted before the move and the 6 resources were re-adopted with `terraform import`; that bucket was later destroyed. |
| 4 | `iam-and-budgets/` steps 1 to 6 as expected: 8 resources, the inline policy names only the one secret, the lifecycle policy `ENABLED`; whether the second apply was needed | step 3.2; `iam-and-budgets/main.tf` | PASS | 8 resources applied; reported as expected. Whether the second apply was needed: not reported. |
| 5 | The budget notification address is confirmed (or no confirmation mail was sent: say which); the budget was accepted in `us-east-1` | step 3.2; `iam-and-budgets/main.tf` (`aws_budgets_budget`) | NOT SETTLED | Confirmation mail not reported. |
| 6 | Width of `AmazonSSMManagedInstanceCore`, as you read its current document | step 3.2 (README step 6); #162's trade-offs | NOT SETTLED | The managed policy's current document was not read in this run. |
| 7 | Width of `AWSDataLifecycleManagerServiceRole` (account-wide, no tag condition?), as you read its current document | step 3.2 (README step 6); #162's trade-offs | NOT SETTLED | The managed policy's current document was not read in this run. |
| 8 | `ci-access/` steps 1 to 6 as expected: 7 resources (6 if the provider was reused), the provider made without `thumbprint_list` | step 3.3; `ci-access/main.tf` | PASS | No GitHub provider existed in the member account (count 0), so this part created it: 7 resources and three role ARNs. `thumbprint_list` not checked. |
| 9 | The real OIDC subject has the numeric-id form (#156 step 1 passes); if not, the README's "If the subject has no ids" path was followed, never a looser trust | step 5; `ci-access/main.tf`, `ci-access/plan.tf` | PASS | #156 step 1: `assumed socboard-ci-plan/probe-plan` (draft PR #255), so the trust's numeric-id subject matches a real token. |
| 10 | Branch check: see the #156 task file's own table (steps 2 and 3 refused) | step 5 | PASS | #156 steps 2 and 3 refused by GitHub's environment rule; see that file's table. |
| 11 | `infra`: named reviewer, administrators not exempt, `main` only; `deploy`: `main` only; the three role ARNs set as repository secrets (write "ARN set") and `TF_STATE_BUCKET` as a variable | step 4 | PASS | Read back by `gh api`: `infra` with the maintainer as required reviewer, admin bypass off, `main` only; `deploy` with `main` only and admin bypass turned off (it was on); `AWS_PLAN_ROLE_ARN`, `AWS_APPLY_ROLE_ARN`, `AWS_DEPLOY_ROLE_ARN` as secrets (ARN set); `TF_STATE_BUCKET` as a variable. |
| 12 | T3 is offered in the chosen zone (default `us-east-1a`); whether `us-east-1e` is listed | step 6; `server/variables.tf` | PASS | `us-east-1a` offers `t3.small`. Whether `us-east-1e` was listed: not recorded. |
| 13 | The `aws_ami` lookup (owner `099720109477`, the noble 24.04 amd64 name pattern) finds an image, and the default subnet of the zone is found | step 6 (README step 4); `server/main.tf` | PASS | The lookup found a noble 24.04 amd64 image and the default subnet (the apply succeeded). |
| 14 | `server/` steps 1 to 6 as expected: 9 resources, three outputs | step 6; `server/main.tf` | PASS | Applied at `5cc7352`, which already included #233's bootstrap, so the plan was 10 resources (the 9 here plus the Elastic IP association) and four outputs, including `hostname`. |
| 15 | The instance, data volume, security group and Elastic IP each carry `project=socboard` in their create call (CloudTrail) | step 6; `server/main.tf`, `ci-access/apply.tf` | NOT SETTLED | CloudTrail create calls not read in this run. |
| 16 | The root volume is untagged and the data volume tagged `project=socboard`; both encrypted | step 6 (README step 6) | NOT SETTLED | Not checked directly; row 28 (step 9) shows which volume is snapshotted. |
| 17 | Metadata tokens required, hop limit 1 | step 6 (README step 6) | NOT SETTLED | Not checked in this run. |
| 18 | The security group's egress is only TCP 80 and 443 (the allow-all rule was removed) | step 6; `server/main.tf` | PASS | `describe-security-groups` egress: exactly `tcp 80 80` and `tcp 443 443`. |
| 19 | The instance is online in Systems Manager within about ten minutes, with egress limited to TCP 80 and 443 | step 6 (README step 6); `server/main.tf` | PASS | Online in Systems Manager within the wait loop. |
| 20 | `apt-get update` and an HTTPS request to `ghcr.io` work through that egress | step 6; `server/main.tf` (`egress_ports`) | PASS | The bootstrap installed its packages through that egress; `curl https://ghcr.io/v2/` on the server returned `401`. |
| 21 | The data volume shows as an NVMe device | step 6; `server/main.tf` (`aws_volume_attachment`) | PASS | `findmnt` shows the data volume as `/dev/nvme1n1` (D19b, 2026-11-16). |
| 22 | The Elastic IP (write it: it is public, and D17c builds the hostname from it) | step 6 | PASS | 44.216.250.242; hostname `44-216-250-242.sslip.io`. |
| 23 | A second plan shows "No changes." in all four folders | step 7 | PASS | `No changes` in all four folders, as reported. |
| 24 | The plan role's write is refused (`create-tags` dry run: `UnauthorizedOperation`) | step 8; `ci-access/plan.tf` | PASS | `create-tags (dry run): UnauthorizedOperation`. |
| 25 | The plan role's secret read is refused (`AccessDeniedException`) | step 8; `ci-access/plan.tf` (`DenySecretValues`) | PASS | `get-secret-value: AccessDeniedException`. |
| 26 | The plan role is enough for a plan of `server/` (no read denied). Recorded for D18b; this apply used your own credentials, so expect NOT SETTLED unless D18b's first plan has run | `ci-access/plan.tf` | PASS | #209's plan job (`plan: success`) on PR #263, run 43747150371, planned `server/` with the plan role. Its logs were deleted on 2026-11-16 because the credentials action printed the role's unique ID; the run's result remains. |
| 27 | The apply role's EC2 list is enough to apply `server/`. Recorded for D22b; expect NOT SETTLED (row 15 is the evidence so far) | `ci-access/apply.tf` | NOT SETTLED | Waits for an apply from CI (D22b, deferred). |
| 28 | The snapshot schedule took a snapshot of the data volume only, not the root volume, with the tag copied | step 9; `iam-and-budgets/main.tf` (`copy_tags`) | NOT CHECKED | Pending: step 9 on 2026-11-16 after 04:00 UTC. |
| 29 | `backend.tf` and `.terraform.lock.hcl` committed in all four folders | step 3, step 6 | PASS | Committed on `main`: `4073f78` (state), `588028d` (state, iam-and-budgets, ci-access), `4e6c7d1` (server). |
| 30 | Whether Data Lifecycle Manager needs the `socboard-snapshot` role: the lifecycle policy applies with it as its execution role (Lifecycle Manager console, the policy's IAM role) and takes the step 9 snapshot with it | step 3.2, step 9; `iam-and-budgets/main.tf` (`aws_iam_role.snapshot`) | NOT CHECKED | Pending step 9. |

Not settled by this apply, so no row: the deploy role's resource split and its AWS-owned-document deny (`ci-access/deploy.tf`; needs the D20 document), the Environment subject form from a `main` run (`ci-access/apply.tf`, `deploy.tf`; D22, unless the #156 task's optional step 4 shows it), fork pull requests getting no token (D18b), and `stop_instance_before_detaching` (seen only at a detach or teardown).

## Cost

The server part stays running after these checks, through D19b and beyond (your ruling of 2026-11-14: the system goes live soon, and a running server means less development friction). There is no stop step. Rough monthly cost in `us-east-1`, from general knowledge (`VERIFY:` on the AWS pricing pages when you run this): `t3.small` about 15 USD, the Elastic IP's public IPv4 charge about 3.6 USD, 30 GiB of gp3 (20 root and 10 data) about 2.4 USD, snapshots of a near-empty volume a few cents: roughly 21 USD a month, plus about 0.40 USD for the secret. You accepted this cost in that ruling.

## Teardown (not part of this run)

Not repeated here; D23 owns the runbook. Order: `server/` first, then `iam-and-budgets/`, then `ci-access/`, and the state bucket last. Each part's steps are in its own "Teardown (the human's step, destructive)" section of `terraform/README.md`: the server, the instance's IAM role, the snapshot schedule and the budgets, CI access, and the state bucket.

## Risk

Steps 2, 3 and 6 create billed resources in your account, and step 4 changes who may deploy. Steps 5 and 8 run probe workflows that hold short-lived role credentials during the job only; they print only "assumed" (with the role and session name) or an AWS error code, never a key, an ARN or an error message. A FAIL is fixed through a new issue, never by an edit during the apply.
