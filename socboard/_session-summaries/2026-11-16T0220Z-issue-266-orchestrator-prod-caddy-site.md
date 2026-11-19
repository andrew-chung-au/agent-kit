# Issue #266: prod's Caddy site and data folder (server side)

**Date:** 2026-11-16T02:20Z (UTC)
**Spec version:** e3461a7

## What changed and why

Prod runs beside dev on the one server (decision 2026-11-15T1840Z). This change, by Terraform lane A, adds the server side and starts nothing for prod.

- `terraform/server/main.tf`: locals `prod_hostname` (`prod-` and the dev hostname) and `prod_app_upstream` (`127.0.0.1:8100`), passed to the bootstrap template. `outputs.tf`: a new output `prod_hostname`.
- `terraform/server/bootstrap.sh.tftpl`: `postgres-prod/` beside `postgres/` (999:999, 0700, top level only), and a second Caddy site for the prod hostname. The dev block, the global block and every other line are unchanged.
- `terraform/server/tests/server.tftest.hcl`: a run `prod_site` that compares the whole Caddyfile, checks two sites with two different loopback upstreams, the prod folder and that the security group still opens only TCP 80 and 443.
- `terraform/README.md` (server and bootstrap sections only): the outputs, the layout, Caddy, a new "The prod stack beside dev" subsection with the values table and the F-256-6 design note (considered, not chosen), and a block at the end of the D19b steps for what changes at this replacement.

Not done here: the apply (the maintainer's, after #237's first deploy), the human-task record and the timeline line (written after that apply).

## Reflection

unknown (role not asked)

## Launch usage

none

## Files created or modified

- `terraform/server/main.tf`, `outputs.tf`, `bootstrap.sh.tftpl`, `tests/server.tftest.hcl`
- `terraform/README.md`
- `_docs/records/findings/266.json` (new), this file

## Decisions made by the human

- 2026-11-16: the ports (8000 and 8100), the `postgres-prod` folder and the names are fine; F-256-6 is recorded as not chosen; the issue is labelled `approved`.
- 2026-11-16: build, QA and merge now. Only the maintainer's apply waits for #237's first deploy, because nothing applies Terraform from CI. First-deploy follow-ups belong to the Application lane.

## Mismatches with the spec or design docs

none

## Commands to validate

**Terraform check:** `make tf-check` (CI's `terraform check` workflow; no Terraform in this sandbox). **Verify:** `make verify` (CI).

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

none

## Unrelated problems noticed but not fixed

- F-266-1: the "no shared upstream" rule is tested on the default values only.
- F-266-2: the `caddy validate` step in the README has not been run on a host.
- F-266-3: the start condition was waived for building and merging on the maintainer's word.

## Follow-ups for the next session

- The maintainer applied this change on 2026-11-16, before #237's first deploy (nothing was running). The record is `_human-tasks/2026-11-16T0259Z-human-task-266-engineer-apply-prod-site.md` and the timeline has its line. The apply settled F-266-2 (`caddy validate` printed `Valid configuration`; the README's `VERIFY:` on it is removed) and corrected the README's claim that the apply waits for #237's first deploy.
