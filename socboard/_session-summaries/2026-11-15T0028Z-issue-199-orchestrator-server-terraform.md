# Issue #199: Terraform: the server instance, network and encrypted data volume

**Date:** 2026-11-15T00:28Z (UTC)
**Spec version:** 5985a83

## What changed and why

D17b, Heavy tier from the PM proposal. The PM filed and groomed #199 from the unfiled wave-2 draft and reconciled it with #156 and #162 as merged. The human labelled it `approved` and approved its `## Decision record` section by name. Branch `claude/199-server-terraform`, draft PR #202.

- `terraform/server/`: one Ubuntu 24.04 instance from an `aws_ami` lookup, with image changes ignored. Default VPC, no key pair. Metadata tokens are required with a hop limit of 1, and the instance profile is the fixed `socboard-instance`. An Elastic IP. A security group allowing TCP 80/443 in and 80/443 out, from one list each way. A separate encrypted gp3 data volume with `prevent_destroy`. `project=socboard` is set in each create call; the root volume is untagged (#162). Validated cost variables, and the state key is under `server/` (#156).
- `terraform/server/tests/server.tftest.hcl`: offline `terraform test` with a mock provider, covering the ports, metadata, tags, encryption, no key name, and three refused values.
- CI: a `terraform test` step in `terraform-check.yml`. `make tf-check` and its AGENTS.md line. All three are protected; the human approved them, and they were committed in 0a6b971.
- The decision record `2026-11-14T1742Z-server-instance-network-volume.md` (approved), its index row and a README section.
- The CI demo the issue asked for: 96c7679 added port 22 and the test step failed (run 43626561872); a8d978e reverted it and the run passed (43626918606).
- 758acbe: wording only. It explains the record's approved status, names D20 as the owner of the deploy document, and fixes the stale D17b notes in the README.
- QA: full PASS at a8d978e, a full re-check PASS at 758acbe, and a second (Code review) PASS at 758acbe. Assert-clean passed after each.

**What I learned:** a hook allows only one plain `git push origin claude/<name>` per command; chaining it after a commit is blocked.

## Reflection

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- PM (file and groom D17b): 6m15s active, 28 tool uses
- Engineer (implement): 24m11s, 77 tool uses
- QA (full, a8d978e): unknown (the completion notice was lost in a container restart)
- Engineer (wording fixes): 7m48s, 29 tool uses
- QA (full re-check, 758acbe): 17m47s, 36 tool uses
- QA (second launch, first try): unknown (stopped by a usage limit before posting; discarded)
- QA (second launch, fresh): 9m44s, 24 tool uses

## Files created or modified

`terraform/server/{main,variables,outputs}.tf`, `terraform/server/backend.tf.example`, `terraform/server/tests/server.tftest.hcl`, `terraform/README.md`, `terraform/ci-access/apply.tf` (comment only), `.github/workflows/terraform-check.yml`, `Makefile`, `AGENTS.md`, `_docs/decisions/2026-11-14T1742Z-server-instance-network-volume.md`, `_docs/index.md`, this summary.

## Decisions made by the human

- They approved the Decision record section as written, keeping the Heavy tier.
- They approved downloading Terraform into `.scratch/` for offline checks.
- They approved committing all three protected changes: the workflow step, `make tf-check` and the AGENTS.md line.
- They approved opening draft PR #202 and running the port-22 CI demo.
- The decision record keeps `approved`, although the Constraints line said `proposed`.
- The `socboard-deploy` document is created by D20.

## Mismatches with the spec or design docs

The issue's Constraints line said the record would be added as `proposed`; it was added as `approved` by the human's ruling, and the record says why. The criterion "the Engineer cannot run Terraform here" no longer held once the download was approved; QA judged the intent met.

## Commands to validate

- **Verify:** `make verify BASE=361c58a`: PASS (2065 Python, 209 frontend).
- **Terraform check:** `make tf-check TERRAFORM=.scratch/tf/bin/terraform`: PASS (4 folders valid, `terraform test` 4 passed).
- CI on 758acbe: terraform check, verify, postgres, tests and image all succeeded.

## Proposed AGENTS.md changes

The **Terraform check** Commands line, which the human approved and which is committed in 0a6b971.

## Temporary changes

- Terraform 1.17.2 (124 MB) is in `.scratch/tf/`, kept for D17c and D19a. It has not been deleted yet; `make clean-scratch` removes it.
- The Engineer stopped one provider plugin process that its own test run had started.
- A read-only reference clone (`.scratch/ref-vt`, 18 MB, made for #209's question about logs) could not be deleted: a safety check refused because the shell was inside it. `make clean-scratch` removes it.

## Interruptions

- A container restart lost the first QA's completion notice. Its PASS comment was read from the issue, and assert-clean was run again by the orchestrator: PASS.
- The first second-QA launch hit a usage limit before posting anything. It was discarded and started fresh, as the process requires.

## Unrelated problems noticed but not fixed

- `_docs/decisions/2026-11-13T2156Z-deploy.md` lines 19 and 56 still call D17b "not filed yet". This is a candidate for #208.
- `make tf-check` does not check the binary against `terraform/.terraform-version`.
- `terraform check` and `make tf-check` need registry.terraform.io. An outage shows as an `init` failure.

## Follow-ups for the next session

- Test gaps QA demonstrated, outside the criteria:
  - a second security group rule resource under another name;
  - a provider `default_tags` block;
  - `user_data`;
  - `http_endpoint = "disabled"`;
  - a looser instance-type rule;
  - `us-east-1e` may not offer T3 (`VERIFY:` at D19a).
- After the human merges #202: post the close comment and run `make clean-scratch` (or keep `.scratch/tf/` for D19a).
- D17c waits for D11. D19a (#207), the docs follow-up (#208) and D18b (#209) are groomed and wait for the human's label; #209's tier is still open.
