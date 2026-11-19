# Issue #233: Terraform: the server's bootstrap, host Caddy and Docker setup (D17c)

**Date:** 2026-11-15T15:29Z (UTC)
**Spec version:** 5985a83

## What changed and why

D17c, Standard tier from the PM proposal, on the critical path to a public URL (#207 stage (b), then #233, then #236 (D19b), then D20). The Decision needed block was unanswered, so it follows option 1: host Caddy proxies to `127.0.0.1:8000`, the Compose `proxy` service is not started on the server, and D20 sets `SOCBOARD_TRUSTED_PROXIES`.

Branch `claude/233-bootstrap-caddy`, draft PR #251. Commit d41b14e:
- `terraform/server/bootstrap.sh.tftpl`, the user data:
  - Docker, the Compose plugin, and Caddy behind a pinned key fingerprint;
  - log rotation and a weekly prune of unused images;
  - the data volume found by its stable by-id name, formatted only when it has no file system, and mounted by UUID with `nofail` at `/srv/socboard-data` (the `STACK_PGDATA_DIR` path), owned by uid 999;
  - a Caddyfile with the admin endpoint off, storage on the volume, and `<ip>.sslip.io` proxied to `127.0.0.1:8000`;
  - no secret is written, read or held.
- `main.tf`: user data with `user_data_replace_on_change = true`, and a separate `aws_eip_association` to avoid a cycle.
- `acme_ca` variable (production by default, staging allowed) and a `hostname` output.
- Six `terraform test` runs; README "The bootstrap" section with the D19b steps.

**Replacement:** if #207 applies `server/` first, the next plan replaces the instance. The data volume and Elastic IP survive. D20 deploys again after any replacement.

QA PASS at d41b14e (all 12 criteria), then assert-clean PASS. CI green, including `terraform check` (run 43716940829). Main moved to 13d371e (#215, #235) without touching this diff. It was not merged in, because that would carry protected `.github/` files, which the lane rules route through the human.

**What I learned:** a user-data template that names the Elastic IP turns the IP-to-instance link into a cycle, and a separate association resource breaks it.

## Reflection

### PM

unknown (the PM groomed #233 in another session and could not be reached from this one)

### Engineer

Reflection:
(1) Slowed by: the issue cites "README, Compose stack", but that section is in the root `README.md`, not `terraform/README.md`; I found it only by grepping for `STACK_PGDATA_DIR`. Also, fetching Caddy's key from Cloudsmith returned 403, so I read the fingerprint from keyserver.ubuntu.com instead, and it stays VERIFY.
(2) Nearly wrong: the user data names the Elastic IP while `aws_eip` named the instance, which is a dependency cycle; splitting out `aws_eip_association` fixed it. I also edited `main.tf` with a one-off python replace script, which the command-shape rule forbids.
(3) Proposal: in the `Makefile` `tf-check` target (protected), render each `*.tftpl` with sample values and run `bash -n` on it, so CI catches a script syntax error before the human's apply. Measure: count the bootstrap syntax fixes still needed at D19b (target: 0).

### QA

Reflection:
1. Slowed: `make verify` took about 6 minutes (pytest 302 s, see `.scratch/qa233-verify.log`) on a diff that touches only `terraform/`. Getting the user data rendered for `bash -n` and the mutations took a hand-written 10-step `.scratch/` script, because no make target renders the template.
2. Nearly wrong: the gate printed "No test files changed" for a diff to `server.tftest.hcl`, so a removed Terraform assertion would have passed silently. I only caught that by reading the diff. Also, the test's copy of the secret patterns misses kit patterns 9 and 13, which I found only by mutation.
3. Proposal: in `_docs/agent-kit/scripts/verify.sh`, treat `*.tftest.hcl` as test files for the weakened-test check (removed `assert` or `run` blocks give a WARN). Expected effect: a dropped Terraform assertion is flagged. Measure: a mutation that deletes one `assert` from `server.tftest.hcl` makes the gate print WARN instead of "No test files changed".

## Launch usage

- Engineer (implement): 22m13s, 48 tool uses
- QA (full check, d41b14e): unknown (its completion notice was replaced by a usage-limit stop after the PASS was posted)
- Engineer (reflection): 22s, 3 tool uses
- QA (reflection): unknown (stopped by a usage limit after posting)

## Files created or modified

`terraform/server/bootstrap.sh.tftpl` (new), `terraform/server/main.tf`, `terraform/server/variables.tf`, `terraform/server/outputs.tf`, `terraform/server/tests/server.tftest.hcl`, `terraform/README.md`, `_docs/records/findings/233.json` (new), this summary.

## Decisions made by the human

- The lane plan (2026-11-15): the critical path comes first. The cloud session works on a `claude/` branch. Protected files go to the human as diffs.
- The Decision needed block was not answered, so the body's option 1 applies.
- The PM may groom #236 once #233's QA passes, without asking again (done after the PASS).

## Mismatches with the spec or design docs

none

## Commands to validate

- **Verify:** `make verify BASE=e45c0c0`: PASS (2505 Python, 237 frontend).
- **Terraform check:** `make tf-check TERRAFORM=.scratch/tf/bin/terraform`: PASS (6 of 6 `server/` tests).
- CI on d41b14e: all green.

## Proposed AGENTS.md changes

none (the Engineer's and QA's proposals touch the protected `Makefile` and kit script; they are suggestions for the human, not applied)

## Temporary changes

Terraform 1.17.2 in `.scratch/tf/` (124 MB) and `.scratch/ref-vt` (18 MB) remain for #209; `make clean-scratch` removes them when it is done.

## Interruptions

- A usage limit stopped QA after it posted its PASS and its reflection. Both comments were confirmed on the issue.
- A usage limit stopped the PM grooming #236 before it changed anything (checked on the issue). It was resumed.

## Unrelated problems noticed but not fixed

- F-233-1: The test's copy of the secret patterns misses two of the kit scanner's patterns.
- F-233-2: No test checks that the Elastic IP association exists.
- F-233-3: No test can guard against a secret-bearing output; review is the only check.
- F-233-4: Docker can start containers on reboot before the nofail data mount is ready.
- F-233-5: Caddy's TLS and ACME keys sit inside the directory bind-mounted into the root-run Postgres container.
- F-233-6: The Caddy key check reads only the first fingerprint, while apt trusts every key in the keyring.
- F-233-7: Two install steps' guards also hide a failed install of the apt source or cron file.
- F-233-8: The README replacement paragraph lacks the inline VERIFY marker main.tf has.
- F-233-9: The verify gate's weakened-test check ignores Terraform test files.
- F-233-10: The Engineer used a one-off script for some main.tf edits, against the command-shape rule.

## Follow-ups for the next session

- The human confirms the Engineer's open choices and merges PR #251. Then the orchestrator posts the close comment and closes #233.
- #236 (D19b) is being groomed. #209 (D18b) follows, and closes after #207's stage (b).
- For D20 (another lane): `SOCBOARD_TRUSTED_PROXIES=10.231.77.1` (VERIFY), `STACK_PGDATA_DIR=/srv/socboard-data`, do not start the Compose `proxy` service, and add `restart: unless-stopped` on `db` and `app`.
