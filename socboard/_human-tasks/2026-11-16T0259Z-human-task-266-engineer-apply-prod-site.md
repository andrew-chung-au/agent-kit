# Apply of the prod site on the server (record of the run)

> **Record of a finished run.** The maintainer applied #266's change on 2026-11-16. Do not run it again; a new replacement follows "Steps for the human in D19b" in `terraform/README.md`, with its block for the prod change. Each check is recorded once, here; the evidence timeline (`_docs/records/2026-11-16T0000Z-measure-planning-deploy-evidence-timeline.md`) holds a one-line summary that links this file.

## Purpose

Record the apply of the prod Caddy site and the prod data folder (`postgres-prod/`) to the one server, and the checks that followed. Issue: #266.

## Where it was run

Not reported where; the maintainer's usual setup is described in the D19b record (`_human-tasks/2026-11-16T0033Z-human-task-236-engineer-first-apply-part-b.md`). "As reported" means the maintainer reported the result in the session and the raw output was not kept.

## What the apply did

- Date: 2026-11-16. It ran before #237's first deploy. Nothing was running on the server, so no stack was restarted. `DEPLOY_INSTANCE_ID` was not set yet, so there was no instance id to update; #238's steps will set it to the new instance, `i-071fe10ec49fbbbe5`.
- The plan read `Plan: 3 to add, 0 to change, 3 to destroy.` (the instance, the volume attachment and the Elastic IP association replaced).
- New output: `prod_hostname = prod-44-216-250-242.sslip.io`. The dev hostname `44-216-250-242.sslip.io` did not change. The data volume and the Elastic IP were untouched.

## Record the result

Rows are PASS, FAIL, NOT CHECKED or "Not reported". "Not reported" means the maintainer reported nothing on it: it may have been looked at or not, and this file claims neither. No account number, ARN, e-mail address or secret is in this file.

| Row | What is checked | Result | Note |
|---|---|---|---|
| 1 | Plan counts and resources | PASS | `3 to add, 0 to change, 3 to destroy`: instance, volume attachment and EIP association replaced. Data volume and Elastic IP untouched. |
| 2 | The new output and the dev hostname | PASS | `prod_hostname = prod-44-216-250-242.sslip.io`; dev hostname unchanged. |
| 3 | The new instance is online | PASS | `i-071fe10ec49fbbbe5`, Online on the first poll. The old instance's id was not reported. |
| 4 | cloud-init and the bootstrap finished | PASS | cloud-init done; `socboard-bootstrap: done`. |
| 5 | Owners and modes on the volume | PASS | `/srv/socboard-data` root 755; `postgres/` uid 999, 700; `postgres-prod/` uid 999, 700 (both shown as `dnsmasq`, the host's name for uid 999); `caddy/` 700. |
| 6 | The Caddyfile has two sites, and Caddy reads it as valid | PASS | Two `reverse_proxy` sites; `caddy validate` printed `Valid configuration`. |
| 7 | `https://<dev host>/` and `https://<prod host>/` | PASS | Both answer 502 with valid certificates. Prod's certificate was newly issued. Nothing was deployed, so no app was behind either site. |
| 8 | Dev's certificate serial unchanged (storage reused) | Not reported | Dev's certificate was valid afterwards; its serial was not compared. |
| 9 | `postgres/` untouched | Not reported | Its owner and mode are as expected (row 5); an inode or content comparison was not reported. |
| 10 | `systemctl is-active docker caddy` | Not reported | Nothing was reported on it. |
| 11 | A second run of the bootstrap changes nothing | PASS | It wrote nothing. |
| 12 | A second `terraform plan` | PASS | `No changes`. |
| 13 | Reboot | NOT CHECKED | Not re-tested: D19b proved it, and this change does not touch the mount or Docker. |
| 14 | `DEPLOY_INSTANCE_ID` updated | NOT CHECKED | The variable was not set yet, so there was nothing to update. #238's steps set it from the current `terraform output instance_id`. |
| 15 | The peer address of the prod app behind Caddy (`10.231.78.1`) | NOT CHECKED | No prod stack runs yet, so there was no peer to measure. |

## Risk

None for this file: it records a run that has finished. The apply replaced the instance, which deleted the old root disk and kept the data volume and the Elastic IP; nothing was deployed on it.
