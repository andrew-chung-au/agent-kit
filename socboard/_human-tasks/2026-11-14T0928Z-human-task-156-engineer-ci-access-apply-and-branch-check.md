# Check that a non-main branch cannot assume the apply or deploy role

## Purpose

Show that only `main` can use the `infra` and `deploy` GitHub Environments' roles, after the human has applied `terraform/ci-access/`. This is the evidence for the issue's criterion on non-`main` branches, and it belongs in the record of the first apply (Deploy item D19, not filed yet). The Engineer has **not checked** any of it: no Terraform, AWS or GitHub Environment was available. Issue: #156.

## Where to run it

A browser for GitHub's settings, and the clean clone for the git commands. The AWS commands run in the clean clone's shell with your own AWS credentials. Not here: the sandbox where the Engineer worked, which has no AWS access.

## Before you start

1. Apply `terraform/ci-access/` following its section of `terraform/README.md` (steps 1 to 6). Keep the three role ARNs it prints.

```
git branch --show-current
```

Expected: `main`, with a clean `git status --short`.

2. In the repository settings, create the two Environments `infra` and `deploy` if they do not exist. For each, set "Deployment branches and tags" to "Selected branches and tags" and add one rule: `main`. (The reviewer rule for `infra`, "administrators are not exempt", is part of D19 and is not tested here.)
3. In the repository settings, under Actions "Secrets" (not Variables), add `AWS_APPLY_ROLE_ARN` and `AWS_DEPLOY_ROLE_ARN` as repository secrets with the ARNs from the apply output. A role ARN contains the AWS account number, and Actions logs print variable values in clear text but mask secrets.

## Steps

### Step 1: Positive control, the plan role accepts a pull request run

This shows the subject format in the trust is right, so a later refusal means something. Add `AWS_PLAN_ROLE_ARN` as a repository secret first (note: `AWS_PLAN_ROLE_ID` was added later by #209, set on 2026-11-16; see `terraform/README.md`, Outputs). The log is public and an AWS error message can name the role's full ARN, which contains the account number, so every probe below prints only "assumed" with the role and session name (the text after `assumed-role/`), or the AWS error code. On a new branch `oidc-probe-plan`, add `.github/workflows/oidc-probe-plan.yml`:

```yaml
name: oidc-probe-plan
on: pull_request
permissions:
  id-token: write
  contents: read
jobs:
  probe:
    runs-on: ubuntu-latest
    steps:
      - name: Try to assume the plan role
        env:
          ROLE_ARN: ${{ secrets.AWS_PLAN_ROLE_ARN }}
        run: |
          TOKEN=$(curl -sS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.amazonaws.com" | jq -r .value)
          echo "::add-mask::$TOKEN"
          if OUT=$(aws sts assume-role-with-web-identity --role-arn "$ROLE_ARN" --role-session-name probe-plan --web-identity-token "$TOKEN" --query 'AssumedRoleUser.Arn' --output text 2>&1); then
            echo "assumed ${OUT#*assumed-role/}"
          else
            C=$(grep -o -E '\([A-Za-z.]+\)' <<< "$OUT" | head -n 1 | tr -d '()'); echo "refused: ${C:-OTHER}"; exit 1
          fi
```

Push the branch and open a draft pull request, then read the job's log in the Actions tab.

Expected: the job passes and prints `assumed socboard-ci-plan/probe-plan`. The step prints no token, no key and no ARN.
If different: `refused: AccessDenied` means the trust's subject does not match the token's. Stop, don't loosen the trust, and tell the orchestrator the error code. Then read `terraform/README.md`, "If the subject has no ids".

### Step 2: Refusal test, a throwaway branch cannot assume the apply role

Refusal test: use the GitHub Actions tab and the clean clone. Risk: if the Environment's branch rule is missing or wrong, the job succeeds and prints `assumed socboard-ci-apply/probe-apply`. It prints no key and no ARN, but it shows a non-`main` branch holds apply rights: stop, fix the rule, and treat `infra` as open until it refuses.

On a new branch `oidc-probe-apply`, add `.github/workflows/oidc-probe-apply.yml`:

```yaml
name: oidc-probe-apply
on:
  push:
    branches: ["oidc-probe-apply"]
permissions:
  id-token: write
  contents: read
jobs:
  probe:
    runs-on: ubuntu-latest
    environment: infra
    steps:
      - name: Try to assume the apply role
        env:
          ROLE_ARN: ${{ secrets.AWS_APPLY_ROLE_ARN }}
        run: |
          TOKEN=$(curl -sS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.amazonaws.com" | jq -r .value)
          echo "::add-mask::$TOKEN"
          if OUT=$(aws sts assume-role-with-web-identity --role-arn "$ROLE_ARN" --role-session-name probe-apply --web-identity-token "$TOKEN" --query 'AssumedRoleUser.Arn' --output text 2>&1); then
            echo "assumed ${OUT#*assumed-role/}"
          else
            C=$(grep -o -E '\([A-Za-z.]+\)' <<< "$OUT" | head -n 1 | tr -d '()'); echo "refused: ${C:-OTHER}"; exit 1
          fi
```

Push the branch and read the run in the Actions tab.

Expected: the run does not succeed. Either the job never starts and says the branch is not allowed to deploy to `infra`, or it starts and prints `refused: AccessDenied`. Record which one. No `assumed` line is printed.
If different: `assumed socboard-ci-apply/probe-apply` means the refusal test failed (see Risk above).

### Step 3: Refusal test, a throwaway branch cannot assume the deploy role

Same as step 2 on a branch `oidc-probe-deploy`, with `environment: deploy`, `secrets.AWS_DEPLOY_ROLE_ARN`, session name `probe-deploy` and the file `.github/workflows/oidc-probe-deploy.yml`. Refusal test and Risk: as in step 2, for the `deploy` Environment.

Expected: the run does not succeed, and no `assumed` line is printed.

### Step 4 (optional): Control that the Environment rule is what refuses

If step 2 or 3 ended in `refused: AccessDenied` rather than GitHub's branch message, the refusal may come from a wrong trust and not from the rule. To tell, add the throwaway branch name to that Environment's allowed branches, push an empty commit to re-run, and expect the `assumed` line to print; then remove the branch name again and re-run, expecting a refusal. Do this only for a few minutes.
Risk: while the branch name is allowed, that throwaway branch can assume the role. Undo: delete the branch rule in the Environment's settings.

### Step 5: Clean up

Delete the throwaway branches and the probe workflow files (they were only on those branches), close the draft pull request, and keep the secrets.

```
git push origin --delete oidc-probe-plan oidc-probe-apply oidc-probe-deploy
```

Expected: the three branches are gone.

## Record the result

Paste the output or write pass or fail for each step, with the run links. Commit this file with the result. Results contain no secrets and no account number: do not paste a token, a key or any ARN; the `assumed` or `refused` line the probe prints is enough.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | PASS | `assumed socboard-ci-plan/probe-plan` (draft PR #255, 2026-11-16). |
| 2 | PASS | Refused before AWS: "Branch "oidc-probe-apply" is not allowed to deploy to infra due to environment protection rules." |
| 3 | PASS | Refused before AWS: "Branch "oidc-probe-deploy" is not allowed to deploy to deploy due to environment protection rules." |
| 4 | SKIPPED | Not needed: GitHub refused both before any AWS call, so the refusal is the branch rule; skipping avoids opening the role. |
| 5 | PASS | Throwaway branches deleted and PR #255 closed, not merged. The probes were pushed with `--no-verify` because the publish workflow's test refused extra workflow files (since fixed in #258). |

## Risk

The probe workflows run with `id-token: write` and the AWS CLI on a GitHub runner, so a run that succeeds holds short-lived credentials for that role during the job only. The steps print only "assumed" with the role and session name, or an AWS error code, never a key, an ARN or an error message. Apart from the optional step 4, nothing here widens any permission.
