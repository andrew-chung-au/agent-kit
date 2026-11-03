# Issue #44: GitHub module, part 1: issue-create and issue-comment wrappers, scan-issue-body.sh and reject-case tests (Phase 4a)

**Tier:** Standard (no tier label was set)
**Date:** 2026-11-03T15:30Z (UTC)
**Spec version:** none

## What changed and why

Agents no longer need raw `gh issue create` or `gh issue comment` to write to this public repository: two `make` targets post a file under `.scratch/` through wrappers that validate the issue number and file name before any shell runs, scan the exact bytes they will post for secrets, and make only fixed `gh` calls. The secret-patterns file and its shared fixtures, which had been planned under #20, moved into this issue (the human's decision of 2026-11-02, body revised and its new hash confirmed by the human in an `Orchestrator:` comment).

Built by the Kiro cloud session on branch `issue-044-github-wrappers`, commit 5ede5fc (one commit on `main` 2c1c2ff; 17 files, +1,867 -4; pull request #60). The human approved the commit so that it could be reviewed; Kiro committed it with `HUMAN_APPROVED=1`; the human then merged it in the sandbox as f36d000, after QA. Files: `agent-kit/scripts/issue-create.sh`, `issue-comment.sh`, `issue-text-lib.sh` (shared helper, a deviation from the file list), `scan-issue-body.sh`, `secret-patterns.txt` (eight patterns); `agent-kit/templates/Makefile.github.mk` and the same two targets in the repo `Makefile`; seven `ask` entries in `agent-kit/claude-code/settings.json` (no allow rule added; `opencode.json` unchanged because #47 already had them); one bullet each in `process.md`, `team/pm.md` and `setup.md` and a `blueprints.md` row; tests `test_issue_wrappers.py`, `test_scan_issue_body.py`, `test_secret_patterns.py`, `test_permissions.py` (extended) and `tests/secret_fixtures.py`.

QA FAIL at 5ede5fc on one criterion only, then PASS on the re-check. About 200 assertions against a fake `gh` that records argv and stdin: every refused N, file name, title and prefix, including make-function injection (`$(shell ...)`, `$(file ...)`, `$(eval ...)`), produced no `gh` call and no marker file; the argv matches the four allowed shapes exactly and no `--label` appears; hostile text is posted byte-identical; the file is read once (a swap during the target check did not change the posted bytes); unreadable or malformed target-issue cases exit 4 and post nothing; a failed `gh` call is made once and exits 1; a secret in the title, body or last line exits 3 and is never printed. All 14 pattern fixtures agree between Python `re` and `grep -E -f`; the patterns are portable, none matches an empty string, and the env-file pattern does not match an example env file. 98 mutants against the shipped tests: 84 killed, 12 survived (redundant inner checks the make layer also covers; the two that mattered, `..` and the character set, were confirmed by running the scripts directly), 2 not applied. After the merge, in the sandbox: `make verify` with #59, #43 and #44 merged: 580 tests OK, 332 assertion lines added and none removed, with one warning (the new file `tests/secret_fixtures.py`, a new fixture file, nothing loosened).

**The by-hand criterion and how it closed.** The issue asked the Engineer to post its report with `make issue-comment`. Kiro could not: `gh issue view` fails in its cloud sandbox, so the wrapper would refuse. QA failed that item. The human chose to supply the report; the orchestrator posted it from the sandbox with `make issue-comment N=44` (comment 6596015478), with a header that says who posted it and why and that env file names were reworded because the scanner refuses text that names them. QA's re-check: PASS, "met in purpose, and only in part in letter"; an Engineer-run wrapper post cannot be done from the cloud sandbox and would have needed a waiver. This was the first real use of `make issue-comment`: QA posted its first verdict with it, and it worked.

Word counts (`wc -w`, before then after): `process.md` 3042 to 3101 (+59, expected +70), `team/pm.md` 764 to 780 (+16, +30), `blueprints.md` 2596 to 2695 (+99, +110), `setup.md` 1258 to 1309 (+51, +50); core Markdown +225 (expected about +260), always-loaded set +75 (expected about +100), `AGENTS.md` +0.

Live effect: `agent-kit/scripts/` runs live from the working tree. All five scripts are new and no existing script changed; `make verify` now syntax-checks them and discovers the new tests.

Not verified: a real `issue-create` (it would file a real issue; checked against the fake `gh` only, as the issue says; the first real use is the next PM-filed issue); OpenCode's real matcher for writes (not exercised, and OpenCode has since been upgraded to 2.2.5); GitHub CI on the merged result (the PR run was green).

**What I learned:** the secret scanner's env-file pattern refuses any comment that names an env file, so QA verdicts and Engineer reports that discuss env files get blocked and must be reworded; and the wrapper accepts only the four role prefixes, so it refuses a comment that starts with `Reflection:`, which is what the process asks roles to post.

## Reflection

### Engineer

unknown (the Kiro cloud session built this; its role was not asked)

### QA

1. Slowed down: the 98-mutant run took about 50 minutes, because each mutant ran four test modules and I could only wait on background events. The env-file path pattern refused my first verdict twice. My clone's remote pointed at a local path, so the first real post failed on `gh issue view`.
2. Nearly went wrong: HEAD moved from 087e945 while I worked, so a "tree unchanged" check would have used the wrong commit; I recorded the commit I tested. I nearly counted redundant-check mutant survivors as test gaps; I confirmed the two that mattered (`..` and the charset check) by running the scripts directly.
3. Proposal: `agent-kit/team/qa-engineer.md`, under the verdict layout: write the verdict without naming env files, and for a mutation run use only the test module that covers the mutated file. Measure: the count of exit-3 refusals in QA sessions and the mutation run's wall-clock in the QA report, both lower over the next two QA launches. For the PM: the wrapper cannot post a `Reflection:` comment (QA posted it as `QA: Reflection on ...`); either allow that prefix in `issue-text-lib.sh` and `process.md`, or ask for `QA: Reflection`.

### PM

unknown (the PM's grooming and revision ran in earlier sessions; role not asked)

## Launch usage

- QA (check #44 at 5ede5fc, FAIL on the by-hand criterion only): 1549.1 s, 61 tool uses (as reported; the harness gave interim usage)
- QA (re-check and reflection, resumed): 53.8 s, 9 tool uses
- Engineer: the Kiro cloud session (not measured here)
- PM (revise #44's body for the secret-patterns move; notes on #20 and #31): 92.5 s and 26.1 s, 19 and 8 tool uses

## Files created or modified

- `Makefile`, `agent-kit/blueprints.md`, `agent-kit/claude-code/settings.json`, `agent-kit/process.md`, `agent-kit/scripts/issue-comment.sh`, `issue-create.sh`, `issue-text-lib.sh`, `scan-issue-body.sh`, `secret-patterns.txt`, `agent-kit/setup.md`, `agent-kit/team/pm.md`, `agent-kit/templates/Makefile.github.mk`, `tests/secret_fixtures.py`, `tests/test_issue_wrappers.py`, `tests/test_permissions.py`, `tests/test_scan_issue_body.py`, `tests/test_secret_patterns.py` (commit 5ede5fc, merged as f36d000)
- This summary.

## Decisions made by the human

- Moved the secret-patterns file and fixtures from #20 into #44, and confirmed #44's new body hash and #20's matching edit.
- Approved the commit of 5ede5fc so that it could be reviewed; merged it after QA; supplied the Engineer's report text for posting.
- Chose that the orchestrator posts the Engineer's report with the wrapper, in place of waiving the by-hand criterion.

## Mismatches with the spec or design docs

none

## Commands to validate

**Verify:** `make verify`

## Proposed AGENTS.md changes

none

## Temporary changes

none

## Interruptions

The cloud session first reported the work staged but not committed, with no branch pushed; it was checked only after it pushed the branch and opened PR #60. Two QA comment posts failed on network errors on other issues; unrelated to this one.

## Unrelated problems noticed but not fixed

- **Secret patterns miss common shapes** (findings, not failures: the issue lists exactly eight patterns): dashed `sk-proj-` and `sk-ant-` keys, `gho_` and `ghs_` tokens, bearer headers in other letter cases and `Authorization: Basic`, a PGP key block header, AWS secret keys, JWTs, `password=` values, Slack webhook URLs, bare base64 blobs, and a key split across a line break.
- **The env-file pattern refuses text that names an env file**, which blocks QA verdicts and Engineer reports that discuss them (workaround: describe them in words).
- **The wrapper refuses a `Reflection:` first line** (only `PM:`, `Engineer:`, `QA:` and `Orchestrator:` are accepted), although `process.md` asks roles to post `Reflection:` comments.
- **The repo's own `.claude/settings.json` lacks the new `ask` rules**; only the kit copy has them. Claude Code still prompts for raw `gh` writes because no allow rule matches.
- A small symlink gap between the symlink check and reading FILE by path (only a local actor could use it).
- `make issue-hash` and `make issue-create` and `issue-comment` do not work in the Kiro cloud sandbox, where `gh issue view` fails (it needs GraphQL).
- #57 should audit the new `issue-file-ok`; #20 must read the shared pattern file and fixtures and not recreate them; #36, #31 and #57 will need to rebase over these files.
- QA's reflection proposal above is for the human; none applied.

## Follow-ups for the next session

- A PM follow-up issue (unlabelled, the human has been asked) for the pattern misses, the repo `.claude/settings.json` sync, the symlink gap, the env-file wording and the `Reflection:` prefix.
- Push from the clean clone; PR #60 shows merged after the push.
- #57 (approved, now unblocked), #20 stage 2 after a working OpenCode, #36, #56.
