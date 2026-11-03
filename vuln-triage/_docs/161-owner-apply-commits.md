# #161 — owner apply runbook: the two protected `.github/` commits

Everything non-protected for #161 is on PR #250 (the check script, its 19 tests,
the proposal, the session summary). PR #249 adds the `ci/test-compose.sh` log
hunk. **Merge #250 (and #249) first**, then run the two commits below on a clone
where you are the committer. Each is its own `HUMAN_APPROVED=1` commit touching
only its own paths, followed by an approval record on #161 (the
`asking-the-human.md` format).

The exact diffs are in `_docs/161-responder-job-proposal.md` (§2.3 for Commit A,
§1.5 for Commit B). Apply them to the files named, then:

## Commit A — `P-FLAG-GONE` step into `deploy.yml`

Paths: `.github/workflows/deploy.yml` only. (Proposal §2.3: checkout `fetch-depth: 0`,
the `P-FLAG-GONE` step before "Resolve image digests", and the one comment reword.)

```sh
git add .github/workflows/deploy.yml
HUMAN_APPROVED=1 git commit -m "ci(deploy): add P-FLAG-GONE gate before prod promotion (#161)

Stops the production promotion while the demo-defect / fixtures switch is still
in the promoted tree (and in the deploy files this run sends). No override, by
design. Diff approved in _docs/161-responder-job-proposal.md section 2.3.
HUMAN_APPROVED: owner, #161 open-questions pass 2026-10-26 (Q5, Q7)."
```

Then post an approval record on #161 naming `.github/workflows/deploy.yml` and the
§2.3 diff.

> Expected on the first real `deploy` dispatch from `main` while the defect
> exists: this step goes **red and deploys nothing**. That is the #161 Check.

## Commit B — `responder.yml` + `verify.yml` pointer

Paths: `.github/workflows/responder.yml` (new) and `.github/workflows/verify.yml`
(pointer comment). (Proposal §1.5, the **recommended** variant — nightly + on
demand, Q1/Q2. Do NOT also apply the "every-PR alternative" diff.)

```sh
git add .github/workflows/responder.yml .github/workflows/verify.yml
HUMAN_APPROVED=1 git commit -m "ci(responder): nightly + on-demand responder Compose job (#161)

New responder.yml (schedule 17:30 UTC + workflow_dispatch) running
make test-compose JOB=responder; verify.yml gets a pointer comment only (parsed
YAML unchanged). Diffs approved in _docs/161-responder-job-proposal.md section 1.5.
HUMAN_APPROVED: owner, #161 open-questions pass 2026-10-26 (Q1, Q2)."
```

Then post an approval record on #161 naming both paths and the §1.5 diffs.

## After Commit B

- Actions → `responder` → Run workflow. Note the wall-clock time; re-size
  `timeout-minutes` to about twice it (a small protected edit, its own
  `HUMAN_APPROVED=1` commit).
- Close the second open box on #229 (the `P-FLAG-GONE` wording, Q5).
- Docs (not protected): add the cadence to the `responder` row in `_docs/testing.md`
  ("nightly and on demand, not on push/PR"), as the `alert` row has.

## Not now (sequenced later)

- The demo-defect cleanup (proposal §2.5) and its protected pieces come **after**
  the recorded drill #163 (it needs the defect present). `responder.yml` changes
  with that cleanup (Q6).
- `make flag-gone` target (Q9): skipped for now.

## Note: `.github/` protection

`.github/` is already enforced by the repo-root hook dispatcher
(`.githooks/pre-commit`), so these commits WILL be blocked without
`HUMAN_APPROVED=1`. There is no need to add `.github/*` to `agent-kit.conf`
`PROTECTED` (Q4, withdrawn as stale). The hooks must be installed in the clone
you commit from (`make hooks`); they are not installed in a clean review clone.
