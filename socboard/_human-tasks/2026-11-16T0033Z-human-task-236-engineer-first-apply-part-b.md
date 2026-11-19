# First apply, part B: the bootstrapped server replaced (record of the run)

> **Record of a finished run.** The maintainer ran D19b on 2026-11-16 from the planning session's steps, not from a checklist written for this issue, so this file is written afterwards from the results the maintainer reported. Do not run it again. A new replacement of the instance follows "Steps for the human in D19b" in `terraform/README.md`. Each check is recorded once, here; the evidence timeline (`_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`) holds a one-line summary that links this file.

## Purpose

Record the apply of #256's hardened bootstrap over the server that #207 had applied with #233's bootstrap (a replacement of the instance), and the host checks that followed. Issue: #236 (Deploy item D19b).

## Where it was run

The maintainer's own machine (WSL, Terraform 1.17.2, AWS CLI v2, SSO profile `socboard`) for Terraform and for the host checks, which were sent to the instance with `aws ssm send-command` (`AWS-RunShellScript`), not typed in a session. "As reported" means the maintainer reported the result in the planning session (the evidence timeline says the raw output was not kept).

## What was run, in order

As the maintainer listed it on 2026-11-16 (the evidence timeline says the raw output was not kept):

1. `export AWS_PROFILE=socboard`; `aws sso login --profile socboard --use-device-code`; a check that the current account is the `socboard` profile's, printing neither.
2. In `terraform/server/`: `terraform plan -out=d19b.plan -no-color > /tmp/d19b-plan.txt`; a grep of it for `must be replaced|will be destroyed|will be created|^Plan:`; a grep of it for `aws_ebs_volume.data` and `aws_eip.server` with destroy or replace, which printed nothing.
3. `terraform apply d19b.plan`.
4. A loop on `aws ssm describe-instance-information` until `PingStatus` was `Online`.
5. Through `aws ssm send-command`: `cloud-init status --wait` and the bootstrap's last line; `findmnt` and `stat -c '%U %a %n'` of the three folders; `systemctl is-active docker caddy`; `docker compose version --short`; `caddy version`.
6. `curl -sS -o /dev/null -w '%{http_code}' https://<hostname>/`, which printed 502.
7. A re-run of `/var/lib/cloud/instance/scripts/part-001`, counting ` wrote ` lines: 0.
8. `aws ec2 reboot-instances`, then `Online` again, the volume mounted and the services active.
9. A second `terraform plan`: `No changes`. Then `rm -f d19b.plan`.

## What the apply did

- Date: 2026-11-16.
- The plan read `Plan: 4 to add, 0 to change, 3 to destroy.` The body of #236 expected `3 to add, 0 to change, 3 to destroy`; the difference is the one resource that is new and unrelated to the replacement: `aws_ssm_document.deploy`, the `socboard-deploy` document from #237, which lives in `terraform/server/`. Replaced: `aws_instance.server` (its user data changed), `aws_volume_attachment.data` and `aws_eip_association.server` (both name the instance). The data volume and the Elastic IP were untouched; the maintainer checked that in the plan before applying.
- New instance: `i-0a09e0f4996d70859`. The old instance's id is not recorded. The hostname `44-216-250-242.sslip.io` did not change.
- A replacement changes the instance id, so `DEPLOY_INSTANCE_ID` on the `deploy` Environment (#238) must hold the new id. Whether the variable was already set when this run was made was not reported; if it was, it needs updating, and if not, #238's steps read the current `terraform output instance_id`.

## Record the result

Rows are PASS, FAIL, NOT CHECKED or "Not reported". NOT CHECKED (rows 12 to 14) means the check needed a reading before the replacement that nobody took, so it cannot be made now. "Not reported" (rows 15 to 21) means the maintainer reported nothing on it: it may have been looked at or not, and this file claims neither. Neither is a failure. Results contain no account number, no ARN with it, no e-mail address, no token, key or secret value.

| Row | What is checked | Result | Note |
|---|---|---|---|
| 1 | The plan before the apply: counts and resources | PASS | `Plan: 4 to add, 0 to change, 3 to destroy.` `aws_instance.server`, `aws_volume_attachment.data` and `aws_eip_association.server` replaced; `aws_ssm_document.deploy` created (from #237, so the count is one higher than the 3/0/3 the body expected). Data volume and Elastic IP untouched, checked before applying. |
| 2 | After the apply: new instance id, hostname unchanged | PASS | New instance `i-0a09e0f4996d70859`; hostname `44-216-250-242.sslip.io` unchanged, as expected (the hostname is built from the Elastic IP). |
| 3 | The new instance is online in Systems Manager | PASS | Online on the first poll. |
| 4 | cloud-init finished and the bootstrap ended | PASS | `cloud-init status` printed `status: done`; the bootstrap log ended `socboard-bootstrap: done`. |
| 5 | The data volume is mounted at `/srv/socboard-data` | PASS | `findmnt` shows `/dev/nvme1n1`; the fstab line is by UUID. |
| 6 | Owners and modes on the volume | PASS | `/srv/socboard-data`: root, 755. `postgres/`: uid 999, 700 (the host names uid 999 `dnsmasq`; checked: nothing on the host runs as uid 999, so the name is harmless). `caddy/`: the `caddy` user, 700. |
| 7 | Docker and Caddy are active, with versions | PASS | Both active. Docker Compose 2.40.3, Caddy v2.11.9. |
| 8 | `https://<hostname>/` answers 502 with a valid certificate (Caddy up, no app yet) | PASS | 502, certificate valid. |
| 9 | A second run of the bootstrap changes nothing | PASS | It wrote nothing and ended `socboard-bootstrap: done`. |
| 10 | Reboot | PASS (as reported) | Back online, volume mounted, Docker and Caddy active. |
| 11 | A second `terraform plan` | PASS (as reported) | `No changes`. |
| 12 | The first run's facts, taken before the replacement (cloud-init lines, package versions, `caddy` uid, owners) | NOT CHECKED | A reading before the replacement was needed and was not taken; the old root disk and its log are gone. |
| 13 | The replacement formatted nothing (no `formatting` line in the new instance's cloud-init log) and re-used the same file-system UUID | NOT CHECKED | The new instance's log line could still be read, but the UUID comparison needed a reading of the old instance before the replacement, which was not taken. The mount shows the volume by UUID and the plan left the data volume untouched. |
| 14 | The certificate's serial before and after (same serial: Caddy re-used the kept storage) | NOT CHECKED | A reading before the replacement was needed and was not taken, so the serial cannot be compared. The certificate was valid afterwards (row 8). |
| 15 | The new instance's image name against the old instance's | Not reported | Not reported. |
| 16 | Caddy's keyring holds exactly one primary key with fingerprint `65760C51EDEA2017CEA2CA15155B6D79CA56EA34` (#256) | Not reported | Not reported. The script stops on any other key, and it ended `done`, but the key itself was not reported. |
| 17 | Docker's log rotation (10 MB, 3 files), the weekly prune file, unattended upgrades, `docker.service` ordered after the data mount | Not reported | Not reported. |
| 18 | Outside checks: `http://` redirects to HTTPS, TCP 8000 and 22 refused, Caddy's admin endpoint refused on the host, a forged `X-Forwarded-For` replaced | Not reported | Not reported for the new instance. The forged header was measured once earlier the same day against the old instance (evidence timeline, the peer-address row, #261). |
| 19 | The peer address the app sees, with the pinned gateway (`10.231.77.1`) | Not reported | Not reported for the new instance. Measured before the pin on 2026-11-16: `10.231.77.128` (evidence timeline, #261). The deploy script (#237) stops with exit 10 if the stack network's gateway is not `10.231.77.1`, so the first deploy checks it on the server. |
| 20 | The published image pulls on the server with no login | Not reported | `curl https://ghcr.io/v2/` returned `401` earlier (#207 row 20), and the package is public (evidence timeline); a pull on the new instance was not reported. |
| 21 | Whether `sslip.io` is on the Public Suffix List | Not reported | Not reported. |

## Why some rows are NOT CHECKED or not reported

The planning session's steps covered the replacement, the host's basic state, the re-run, the reboot and the second plan, not the full body of #236. Rows 15 to 21 would each need the maintainer to run something that the maintainer has said not to run (2026-11-16: "run nothing"). Under the project's rule (`.kiro/steering/evidence-and-steps.md`, rule 2) a check is not repeated only to produce a record, except when the thing it checked has changed, so they stay as they are unless the maintainer decides one is worth running. Rows 12 to 14 cannot be recovered at all: they needed a reading before the replacement. The next replacement's steps (`terraform/README.md`, "Steps for the human in D19b") take those readings.

## Risk

None for this file: it records a run that has finished. The apply replaced the instance; it deleted the old root disk and every file on it, and kept the data volume and the Elastic IP.
