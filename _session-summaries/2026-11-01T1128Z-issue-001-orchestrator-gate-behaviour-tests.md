# Issue #1: Behaviour tests for the kit's commit and push gates, and make CI's weakened-test check work

**Date:** 2026-11-01T11:28Z (UTC)
**Spec version:** none

## What changed and why

The kit's commit and push gates now have behaviour tests, and three scripts read changed file names NUL-delimited (`-z`), so non-ASCII names, names with a double quote or backslash, and a repo root containing a space are no longer missed. Before the fix, a forbidden `café.pem` or a protected non-ASCII path passed pre-commit; deleting a non-ASCII test file or adding `@unittest.skip` to it gave `VERIFY: PASS`; and a quoted name in a subfolder project made `githooks/pre-commit` skip that project's checks entirely. Four commits, each approved and run by the human, in this order: ffa5c7b (shared helper `tests/kit_repo.py` and six gate test files, no protected path), 9e86ec2 (`agent-kit/scripts/check-staged.sh`), ddf1f96 (`agent-kit/scripts/verify.sh`), 48c63fe (`agent-kit/githooks/pre-commit`, hook version 3 to 4). Each fix commit carries its own names tests, so every commit passes `make verify` alone (the Engineer's claim; QA checked each fix against its parent). QA PASS at 48c63fe.

QA's fail-then-pass evidence, taken per fix commit against its parent's scripts: `check-staged.sh` 15 failures then 6 tests OK, `verify.sh` 8 then 3 OK, `pre-commit` 18 then 6 OK; plain-name controls pass both ways. `make verify`: 254 tests, 515 assertion lines added, 0 removed.

Live-edited code: `agent-kit/scripts/check-staged.sh` and `agent-kit/scripts/verify.sh` run live from the working tree, so the fix changed this repo's own pre-commit checks and `make verify` while the change was being made. `agent-kit/githooks/pre-commit` takes effect only after `make hooks`: this repo's own `.githooks/pre-commit` is still version 3 until the human runs it. Nothing under `agent-kit/claude-code/hooks/` was touched.

Not verified: the proposed `.github/workflows/verify.yml` diff (adds `fetch-depth: 0` and the template's `BASE` expression, plus one for a push that creates a branch). It is for the human to apply and is unverified until the first Actions run shows "Changes in this folder since <a commit>", not `HEAD`.

**What I learned:** a one-line fix per script would have shipped with the gap open: `core.quotePath=false` covers non-ASCII names but git still quotes a name containing a double quote; only a NUL-delimited read closes both. The same read pattern survives in two more places, now #42 (see below).

## Reflection

Each block is copied unchanged from the new comment on #1. All three exceed the 150-word cap in `procedures/session-summary.md`.

### PM

- **What slowed you down (evidence):** I groomed #1 three times in about 1h45 (comments at 09:03, 10:44, 10:48 UTC). The first pass found the `check-staged.sh` defect, said `verify.sh` "has the same defect (not probed)" and proposed a one-line `core.quotePath=false` fix. The second pass probed `verify.sh`, found it was broken the same way, and found that `core.quotePath=false` is not enough (a name with a double quote is still quoted, and a subfolder project's checks are skipped). That rewrote the Goal, the criteria and the Constraints. The third pass only recorded the human's three decisions. I probed the defect where I first saw it and did not probe the other places that read git file lists in the same way until a re-groom.
- **What nearly went wrong or was blocked:** The first-pass recommendation (one line per script) would have shipped a fix that still let `a"b.pem` and `proj/a"b.pem` through, and the Engineer would have built tests to match it. The `-z` approach was only reached because I probed again. The same gap is still visible after PASS: the Engineer found unquoted-name reads in `agent-kit/githooks/pre-push` (line 41) and `agent-kit/claude-code/hooks/verify_on_stop.py` (line 63), and QA repeated it. Neither is in #1's criteria, #40 covers only behaviour tests for `githooks/pre-push`, and `verify_on_stop.py` has no issue. Nothing was blocked: no QA FAIL, no changed paths outside the 13 listed files, and the human's decision on scope (fix all three scripts) was clear.
- **One proposed change (file, expected effect, measure):** In `agent-kit/team/pm.md`, add to the grooming list: when an issue is about a defect class (for example unquoted file names, a missing check), search the kit case-insensitively for every site of the pattern, probe each in a throwaway repo before writing the criteria, and list each site as either a criterion or an out-of-scope item with an issue link. Expected effect: the right fix is chosen at the first groom (fewer re-grooms) and sibling sites are found by the PM, not by the Engineer or QA after the work. Measure: sibling sites of the defect class found by Engineer or QA outside the criteria, per issue (target 0), plus re-groom comments per issue (baseline for #1: 2 re-grooms; a lower count alone does not count as success). Paired protection metric: defects found after QA PASS and QA FAIL rounds must not rise, and changed paths outside the issue's listed limits must stay 0; an issue that grows in scope because of the extra search must still be one deliverable (the PM asks about splitting rather than absorbing it).

*Orchestrator note:* the PM's "no issue exists" for the `pre-push` and `verify_on_stop.py` reads was true when it wrote this; #42 was filed at the human's decision a few minutes later and now covers both.

### Engineer

- **What slowed you down (evidence):** The size of the change. The four commits touch 13 files, 1370 insertions and 14 deletions, 1075 of them in the first tests-only commit (seven files, a shared helper `tests/kit_repo.py`, then six test files). The PM comment of 2026-11-01 already called the issue large and offered a split; the human kept it as one. Two further costs are visible in the comments. First, a tests-first run needed an explicit failing record (43 failures across three name files, kept only in a local `.scratch/eng01-failing.txt`), and QA had to rebuild the same before/after evidence from `git archive` copies (15 + 8 + 18 failures) because the failing run lives in a comment, not in the history. Second, the tests had to avoid tripping the very checks they exercise: the skip markers are built from string pieces so `verify.sh` does not flag the test files, and the helper overrides `subTest` to reset the throwaway repo so one failure cannot cascade. Both were found by running, not by reading.
- **What nearly went wrong or was blocked:** (1) Live scripts: `check-staged.sh` and `verify.sh` run from the working tree, so the fix changed this repo's own gate while I was working; the commit order (tests only, `check-staged.sh`, `verify.sh`, hook) was chosen so each commit passes `make verify` alone, and commit 4's subfolder cases depend on commit 2. (2) The same defect class remains unfixed outside the criteria: `agent-kit/githooks/pre-push` line 41 (`git diff --name-only`, decides which projects the pre-push runs) and `agent-kit/claude-code/hooks/verify_on_stop.py` line 63. I found them by a case-insensitive re-grep after the fix, and QA confirmed them; the PM's earlier probes covered only the three scripts the issue named. (3) `verify.sh` with no `BASE` on a detached HEAD compares nothing ("No test files changed."); I pinned that as current behaviour with a comment rather than fixing it, and the CI first-run check is still UNVERIFIED (human action). (4) Until the human runs `make hooks`, this repo's own `.githooks/pre-commit` is still version 3, so the repaired hook is not yet the one guarding commits here.
- **One proposed change (file, expected effect, measure):** File: `agent-kit/team/software-engineer.md`, in the bullet list before the Definition of done. Add one line: "When the task fixes a defect in how a command reads input (quoting, delimiters, encodings), grep the whole repo for the same read before the first fix commit, and list every other site in your first comment, fixed or not, with the reason." Expected effect: sibling sites such as `pre-push` line 41 and `verify_on_stop.py` line 63 are known and decided (fix here, or follow-up issue filed by the PM) while the issue is still being scoped, instead of found after the fix and left as notes for QA. Measure: the number of same-class sites reported by QA or later work that the Engineer's first comment did not list (target 0 on defect-class issues), paired with protection metrics: QA rounds on those issues must not rise above the current count (1 for #1), defects found after PASS must stay at 0, and changed paths outside the issue's Files list must stay at 0 (so the grep produces a listing and a follow-up, not scope creep). Review it after the next two defect-class issues.

*Orchestrator note:* the Engineer's first comment on the issue did list its findings after the fix (the same-defect sites are in its evidence comment), but not before the first fix commit, as the proposal asks. The Engineer's "43 failures" is its pre-split run; QA's per-commit counts (41 = 15 + 8 + 18) are the evidence of record.

### QA

- **What slowed you down (evidence):**
  - Tests-first evidence was not reproducible from the issue. The Engineer's 43 failures came from uncommitted files and a local `.scratch/eng01-failing.txt`, taken before the work was split into four commits. To confirm each fix commit I had to `git archive` each parent and fix commit and run the fix commit's tests against the parent scripts (`.scratch/qa01-prepost.sh`). I then had to reconcile my 15 + 8 + 18 = 41 failures with their 43 (the 2 non-ASCII subfolder cases were already fixed by the earlier `check-staged.sh` commit). The split into four commits was good; the per-commit failing counts were not in the Engineer's comment.
  - The verdict comment is long (13 criteria lines plus per-file failure counts and an edge-probe list) because the issue has about 17 criteria and a 13-file diff. Reading the criteria against 1370 added lines was the bulk of the work. `make verify` itself took 13 s.
- **What nearly went wrong or was blocked:**
  - I edited my own scratch script with `sed -i`, which breaks the command-shape rule (scratch only, but a slip). I should have rewritten the file with the Write tool.
  - Two of my edge probes (`x\n.env`, `trail.pem\n`) were first read as bypasses. They were accepted correctly because those names do not match the patterns. I had to check the pattern semantics before concluding.
  - The same defect class survives outside the criteria: `agent-kit/githooks/pre-push` line 41 and `agent-kit/claude-code/hooks/verify_on_stop.py` line 63 still read names without `-z`. No criterion covered them, so nothing blocked the PASS. They are listed in my "Outside the criteria" section for the human.
  - Nothing was blocked. The CI first-run check could not be run in the sandbox and stayed UNVERIFIED.
- **One proposed change (file, expected effect, measure):**
  - File: `agent-kit/team/software-engineer.md`. When an issue says tests first and the work is committed as several commits, the evidence comment gives, for each fix commit, the failing test names and count of that commit's tests run against the parent commit's scripts (taken per commit, not once before the work was split).
  - Expected effect: QA compares its own pre/post run to the posted counts and does not have to rebuild and reconcile the baseline, so a mismatch such as 43 versus 41 is explained up front.
  - Measure: QA minutes spent reproducing tests-first evidence on issues that use the tests-first rule go down over the next three such issues (efficiency). The protection metrics: QA rounds stay at 1 per issue or lower, defects found after PASS stay at 0, and changed paths outside the issue's limits stay at 0. If any protection metric gets worse, the change is not working, whatever the time saved.

*Orchestrator observation:* the Engineer's and QA's proposals both edit `software-engineer.md`, and the PM's edits `pm.md`; the PM's and the Engineer's both say to grep the whole kit for every site of a defect class before the fix. With the proposals from #29, four `pm.md` and two `software-engineer.md` suggestions are now pending. None is applied.

## Launch usage

Durations are those on the completion notices (elapsed, which can include waiting).

- PM (first re-groom of #1, with probes): 153 s, 46 tool uses
- PM (fold the human's decisions into #1, file #40): 101 s, 23 tool uses
- Engineer: 615 s, 74 tool uses
- QA: 195 s, 33 tool uses
- PM (reflection): 36 s, 8 tool uses
- Engineer (reflection): 54 s, 10 tool uses
- QA (reflection): 35 s, 6 tool uses

Not for #1 but in the same session:
- PM drafting the #16 refresh: 120 s, 21 tool uses; PM revising it: 96 s, 18 tool uses; PM applying the confirmed body and recording the hash: 34 s, 10 tool uses
- PM filing #42: 111 s, 24 tool uses

## Files created or modified

- `agent-kit/scripts/check-staged.sh`, `agent-kit/scripts/verify.sh`, `agent-kit/githooks/pre-commit` (modified)
- `tests/kit_repo.py` (new helper), `tests/test_gate_harness.py`, `tests/test_gate_pre_commit.py`, `tests/test_gate_install_hooks.py`, `tests/test_gate_push_check.py`, `tests/test_gate_ci_template.py`, `tests/test_gate_verify.py`, `tests/test_gate_check_staged_names.py`, `tests/test_gate_verify_names.py`, `tests/test_gate_pre_commit_names.py` (new)
- `_session-summaries/2026-11-01T1128Z-issue-001-orchestrator-gate-behaviour-tests.md` (this file)

## Decisions made by the human

- Re-scoped decisions on #1, all as recommended: fix option 1 (`-z` reads in the three scripts), keep it as one issue, one unlabelled follow-up for the out-of-scope items (#40, behaviour tests for `assert-clean.sh` and the kit's `githooks/pre-push`; `sweep-due.py` already has tests in `tests/test_sweep.py`, so it is not in #40).
- Approved and ran all four commits: ffa5c7b, 9e86ec2, ddf1f96, 48c63fe, in the order the Engineer proposed.
- Option 1 on the follow-up for the `githooks/pre-push` and `verify_on_stop.py` name reads: the PM filed #42 (unlabelled).
- In the same session, on #16: confirmed the revised body (hash `156976334852…2ded`, recorded in a `PM:` comment by the PM after an `Orchestrator:` confirmation comment), no bypass for Light (a short PM launch records the hash and proposes the tier), the PM's grooming comment must carry `Proposed tier:`, #16's own tier is Heavy. Renamed the three labels to `tier:light`, `tier:standard` and `tier:heavy` (verified with `gh label list`).
- Version bump: the human cuts it when ready; sweep skipped (`make sweep-due`: "due: no sweep recorded").

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (PASS at 48c63fe: 254 tests, whitespace clean, 515 assertion lines added, 0 removed).

## Proposed AGENTS.md changes

none.

## Temporary changes

`make clean-scratch` was not run: issue #20 is open and on hold, and its throwaway project `.scratch/eng20-proj/` and observer `.scratch/eng20-observer.js` are needed for the rerun after the human's OpenCode limit resets (see the #29 summary; OpenCode's `node_modules` install sits in that folder). Scratch files from this issue remain: `eng01-*`, `qa01-*` (including `qa01-work/`), `pm01-*`, `pm01b-*`, `pm01r-*`, `eng01r-*`, `qa01r-*`, `pm16*-*`, `pm42-*`.

## Interruptions

none.

## Unrelated problems noticed but not fixed

- The same unquoted-name read in `agent-kit/githooks/pre-push` (a push whose only change is `café.txt`, `café.md` or `a"b.txt` in a subfolder project exits 0 and runs no `make verify`) and in `agent-kit/claude-code/hooks/verify_on_stop.py` (a stale passing stop can be reused after editing an untracked non-ASCII or quoted file). Now #42, unlabelled. `environments/local-sandbox/pre-push` already reads with `-z`.
- `verify.sh` with no `BASE` on a detached HEAD compares nothing ("No test files changed."); pinned as current behaviour in a test comment.
- `verify.sh` lists untracked files with plain `git ls-files --others`; only a warning, cosmetic.
- `make assert-clean` fails on the human's `.claude/agents/pm.md` change and two untracked `proposals/` files, as expected.
- The `.claude/agents/*` copies in this repo still carry the old "Read `AGENTS.md`" wording until the human syncs them.
- QA edited one of its own scratch scripts with `sed -i` (scratch only), and the new tests use `--no-verify` only on setup commits inside throwaway repos; no change to kit rules proposed.

## Follow-ups for the next session

- The human's to apply: the `.github/workflows/verify.yml` diff in the Engineer's final comment on #1 (https://github.com/andrew-chung-au/agent-kit/issues/1#issuecomment-6557244848), and `make hooks` in the clean clone for pre-commit version 4. The first Actions run is the check.
- Unlabelled, waiting for the human: #42 (hash `36f6222a…5ee6`; the more serious half of the defect), #38, #41 (three decision questions), #31, #32, #33, #26. #40 is approved but its hash is not recorded (`make issue-hash N=40` prints `Recorded sha256: none`); a short PM launch records it when #40 is worked. #36 and #37 are approved and wait on #20 and #16.
- #16 (Phase 3a, body now includes the mandatory `Proposed tier:` line and is Heavy) is next after #39 in the suggested order; it was waiting on #1 and #29, both done.
- #20 stays on hold until the human's OpenCode limit resets.
- Changelog line for #1 (human decides when to cut a version): "check-staged.sh, verify.sh and the pre-commit hook read file names NUL-delimited, so non-ASCII and quoted names are no longer missed; pre-commit hook version 4". Existing installs need `make hooks`.
- Reflection proposals (suggestions for the human, not applied): `pm.md` (grep the whole kit for every site of a defect class and probe each before writing criteria; plus the three from #29), `software-engineer.md` (list every same-class site in the first comment before the first fix commit; give per-fix-commit failing counts against the parent; plus the one from #29).
