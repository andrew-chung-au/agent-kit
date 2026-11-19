# Epoch batch: exact kit edits, drafted by the PM (proposal only)

Nothing tracked was edited; nothing was commented on or labelled. Every diff is a file in this folder and is also shown inline below, so this README is enough to review the batch. Kit files are protected: an agent commits each diff with `HUMAN_APPROVED=1` only after the human has approved it.

Human rulings of 2026-11-12 (this session) are applied: items 5, 6, 6b and 7 approved; 2a rewritten as the pointer variant; 3 and 4 left as drafted, with the wording marked as the PM's.

- **Base:** `origin/main` = `2c77a6f` (fetched). The working tree is on branch `session-summary-issue-74` at `999a410`, behind `origin/main` by #74's `openapi.yaml` and two test files only. `git diff --stat HEAD origin/main` over `_docs/agent-kit`, `agent-kit.conf`, `AGENTS.md` is empty, so the patches apply the same to the tree and to `origin/main`.
- **Checks run** (`apply-check.sh`, `check-batch.py`, both read-only, in this folder; re-run 2026-11-12 after rewriting 2a): `git status --short` was empty before and after; `git apply --check` on each patch against the tree passed (output below); `check-batch.py` applied each patch in memory to the `origin/main` blob and counted words (`len(text.split())`, equal to `wc -w`).
- **Not checked:** patches that touch the same file (2a and 4 on `process.md`; 2c and 3 on `qa-engineer.md`; 6 and 7 on `agent-kit.conf`) were each checked alone against the original, not applied in sequence. Their hunks are far apart (git handles the line offset), so I expect them to stack, but I did not prove it. I did not run `make contract-check`, `make verify` or the tests (Kiro Web, no package index).

**No longer a batch (human ruling, 2026-11-12, after #12 closed):** the ponytail trial is shelved (`_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`), so the epoch reasons for landing these together no longer apply. Each patch is an ordinary process edit and lands on its own when the human approves its exact diff. The "Epoch?" column and the "Epoch effect" section below are historical. Nothing here is committed yet.

Items 9 to 11 were added the same day, from sweep 4's proposals 1, 2 and 3 (accepted in the Human ruling at the end of `_docs/records/2026-11-12T2107Z-measure-pm-sweep.md`). Their checks (`.scratch/epoch9-11-check.py`, run from the working tree on `sweep-4-record`, base `origin/main` = `2f78f88`): each patch passes `git apply --check` alone; applied for real to a copy under `.scratch/`, 2c, 3, 9, 10 stack on `qa-engineer.md` (675, 724, 752, 764, 791 words) and 1, 11 stack on `software-engineer.md` (483, 497, 517). No stack failed, so no patch was regenerated.

## Table

Words are `wc -w` of the whole file, before (`origin/main`) and after. "Epoch" is the Amendment 2 test (`_docs/planning/ponytail-trial-protocol.md`, line 105): the change alters what an existing command a role runs does, or adds or changes a rule sentence a role reads. `KIT_VERSION` alone does not.

| n | File (kind) | Change in one line | Words before to after | Approved? Source | Epoch? | Apply check |
|---|---|---|---|---|---|---|
| 1 | `_docs/agent-kit/team/software-engineer.md` (kit) | Completion comment also lists each check not run, with the reason | 483 to 497 (+14; budget about +15) | **Yes**, deferred to the batch. Sweep 2 record, Human ruling, line 112; proposal at lines 82 to 88 | Yes (rule sentence) | OK |
| 2a | `_docs/agent-kit/process.md` (kit) | Launch-message checklist per role (QA, Engineer, PM); the Reflection line points to `procedures/session-summary.md` (Reflection) for the three questions instead of quoting them. **Rewritten 2026-11-12** | 3569 to 3624 (+55; target about +50) | **Yes, pointer variant** (human, 2026-11-12). Earlier: sweep 3 record, Human ruling, line 136; proposal 1 at line 84 | Yes | OK |
| 2b | `_docs/agent-kit/templates/human-task.md` (kit) | A step never asks the human to edit a tracked file by hand; give a command that writes a copy; done banner | 378 to 435 (+57; budget about +55) | **Yes**. Same sweep 3 ruling; proposal 2 at line 91 | Yes (template a role reads) | OK |
| 2c | `_docs/agent-kit/team/qa-engineer.md` (kit) | Heavy second launch fails only on a Medium or higher finding that needs a change in the issue; Lows and later-issue notes are follow-ups | 675 to 724 (+49; budget about +45) | **Yes**, with the withdrawal condition (Medium defect after a second-launch PASS). Same ruling; proposal 3 at line 98. **Condition not triggered** (see below) | Yes | OK |
| 2d | `_docs/agent-kit/team/pm.md` (kit) | Grooming rule: no "exactly", "only", "all" for a list another role fills in | 1001 to 1038 (+37; budget about +40) | **Yes**. Same ruling; proposal 4 at line 105 | Yes | OK |
| 3 | `_docs/agent-kit/team/qa-engineer.md` (kit) | One bullet: a criterion that cannot run is reported "not run" with the reason, never as passed | 675 to 703 (+28) | Approved to queue (#42 Close comment 6812033545, PR #76 body, `roadmap-1-core.md` line 39). **Wording chosen by the PM; the human reads the exact diff at landing** | Yes | OK |
| 4 | `_docs/agent-kit/process.md` (kit) | Lifecycle step 1: every issue gets a place in the order, with a trigger, when filed; an issue outside it is never groomed | 3569 to 3604 (+35) | Approved to queue (`.kiro/steering/backlog-order.md`, PR #76 body). **Wording chosen by the PM; the human reads the exact diff at landing** | Yes | OK |
| 5 | `_docs/agent-kit/procedures/orchestrator-comments.md` (kit) | Claim: fixed-format `Launch environment:` line; Close: `Feedback rounds:` line | 319 to 377 (+58) | **Yes, as drafted** (human, 2026-11-12) | Yes | OK |
| 6 | `agent-kit.conf` (project, protected) | `LINT_CMD="make contract-check"`, so `make verify` and CI run it | 356 to 357 (+1) | **Yes, via `LINT_CMD` for now** (human, 2026-11-12); to be moved when #75's lint target arrives (see below) | Yes (changes what `make verify` runs) | OK |
| 6b | `AGENTS.md` (project, protected) | Verify line says it includes the OpenAPI contract check | 1403 to 1407 (+4) | **Yes**, goes with 6 (human, 2026-11-12) | With 6 | OK |
| 7 | `agent-kit.conf` (project, protected) | `KIT_VERSION` `1.10+socboard.1` to `1.10+socboard.2` (local counter only) | 356 to 356 (0) | **Yes** (human, 2026-11-12). The base `1.10` names the parent agent kit and stays; only `<n>` moves; `<base>+<repo>.<n>` kept as `kit-check.py` requires | No (Amendment 2, "a `KIT_VERSION` bump on its own") | OK |
| 9 | `_docs/agent-kit/team/qa-engineer.md` (kit) | Code review reads the diff with three dots (`git diff origin/main...HEAD --stat`, full diff the same way), so files main changed since the branch started do not show | 675 to 687 (+12; about +12). In order 2c, 3, 9: 764 | **Yes, sweep 4**, `_docs/records/2026-11-12T2107Z-measure-pm-sweep.md`, Human ruling; wording chosen by the PM, the human reads the exact diff at landing | Yes (rule sentence) | OK alone; OK stacked in order 2c, 3, 9, 10 |
| 10 | `_docs/agent-kit/team/qa-engineer.md` (kit) | A probe or bypass attempt counts as refused only when the error class and message are the expected refusal; a probe's own error counts as not run | 675 to 702 (+27; about +26). In order 2c, 3, 9, 10: 791 | **Yes, sweep 4**, `_docs/records/2026-11-12T2107Z-measure-pm-sweep.md`, Human ruling; wording chosen by the PM, the human reads the exact diff at landing | Yes (rule sentence) | OK alone; OK stacked in order 2c, 3, 9, 10 |
| 11 | `_docs/agent-kit/team/software-engineer.md` (kit) | Human-task bullet: when a check cannot run here, the Engineer drafts the human-task file as soon as it knows, listing each unconfirmed guess, not at hand-over | 483 to 503 (+20; about +20). In order 1, 11: 517 | **Yes, sweep 4**, `_docs/records/2026-11-12T2107Z-measure-pm-sweep.md`, Human ruling; wording chosen by the PM, the human reads the exact diff at landing | Yes (rule sentence) | OK alone; OK stacked in order 1, 11 |

### Apply-check output (`bash .scratch/epoch-batch/apply-check.sh`, 2026-11-12, after the 2a rewrite)

```
status before:
(end)
OK   .scratch/epoch-batch/1-unrun-checks-clause.patch
OK   .scratch/epoch-batch/2a-launch-message-checklist.patch
OK   .scratch/epoch-batch/2b-human-task-wording.patch
OK   .scratch/epoch-batch/2c-heavy-stopping-rule.patch
OK   .scratch/epoch-batch/2d-grooming-counting-words.patch
OK   .scratch/epoch-batch/3-qa-not-run.patch
OK   .scratch/epoch-batch/4-backlog-order.patch
OK   .scratch/epoch-batch/5-launch-environment-line.patch
OK   .scratch/epoch-batch/6b-agents-verify-line.patch
OK   .scratch/epoch-batch/6-contract-check-in-verify.patch
OK   .scratch/epoch-batch/7-kit-version.patch
status after:
(end)
HEAD vs origin/main on the files the patches touch:
(end)
```

`git status --short` printed nothing before and after. (The 2a word count was +68 on my first rewrite and +55 on the final one; the table shows the final.)

## Notes for the human

- **#75 and `LINT_CMD` (item 6).** Wiring `make contract-check` into `LINT_CMD` is the approved interim. When #75's lint target arrives, move the contract check out of `LINT_CMD` (or fold it into that target) and regenerate patch 6 and the 6b wording if needed. Cost of the interim: the gate is labelled "Lint" in `make verify` output and in QA's "lint / type check" line.
- **Roadmap line is out of date.** `_docs/planning/roadmap-1-core.md` line 39 says only #63, #49 and #65 move the epoch. #80 also moves it (it changes what `make backend-run` and `make backend-stop` do). The orchestrator fixes the roadmap; I did not touch it.
- **2c withdrawal condition has not triggered.** The condition is a Medium defect after a second-launch PASS. The only second-launch PASS so far is #9's, and no Medium defect has been found since (human statement, 2026-11-12; I did not re-check #10's QA comments myself).
- **Items 3 and 4:** wording chosen by the PM; the human reads the exact diff at landing. Item 3 does not say what "not run" does to the verdict, because #42 does not say. Item 4 uses the generic "agreed order", not the roadmap path, and leaves out the steering file's check at each decision point and the `[groomed]` title prefix.

## Changes, each with its exact diff

### 1. Engineer: list the checks not run (`1-unrun-checks-clause.patch`)

```diff
diff --git a/_docs/agent-kit/team/software-engineer.md b/_docs/agent-kit/team/software-engineer.md
--- a/_docs/agent-kit/team/software-engineer.md
+++ b/_docs/agent-kit/team/software-engineer.md
@@ -22,3 +22,3 @@
 - The issue is still open, with a comment containing:
-  - the verify result and what you did, with one line per acceptance criterion saying done, not done or not checked, and where
+  - the verify result and what you did, with one line per acceptance criterion saying done, not done or not checked, and where, and a list of each check you could not run here, with the reason
   - choices you made that the issue doesn't cover
```

### 2a. Launch-message checklist, pointer variant (`2a-launch-message-checklist.patch`)

Rewritten per the ruling: no word-for-word Reflection quote; it points to `_docs/agent-kit/procedures/session-summary.md` (Reflection), line 12, which holds the three questions (what slowed you down; what nearly went wrong or was blocked; one proposed change). The proposal's "never ask for a heading that replaces the required line" and "label after it" clauses stay dropped; QA's file already says the comment starts with the verdict.

```diff
diff --git a/_docs/agent-kit/process.md b/_docs/agent-kit/process.md
--- a/_docs/agent-kit/process.md
+++ b/_docs/agent-kit/process.md
@@ -51,2 +51,8 @@
 
+Launch messages keep each role's required output:
+- **QA:** the comment starts with `QA: PASS` or `QA: FAIL`, also in re-checks and Code review.
+- **Engineer:** the verify result and one line per criterion.
+- **PM:** the `Body sha256:` and `Proposed tier:` lines.
+- **Reflection,** once after QA PASS: the three questions in `_docs/agent-kit/procedures/session-summary.md` (Reflection).
+
 ## Orchestrator
```

### 2b. Human-task template (`2b-human-task-wording.patch`)

The banner is `Status: done <date>, do not run again` at the top of the file; "record the result the same day" is already covered by the template's "Record the result" section.

```diff
diff --git a/_docs/agent-kit/templates/human-task.md b/_docs/agent-kit/templates/human-task.md
--- a/_docs/agent-kit/templates/human-task.md
+++ b/_docs/agent-kit/templates/human-task.md
@@ -25,3 +25,5 @@
 ## Steps
 
+A step never asks the human to edit a tracked file by hand; if it needs a changed copy, give a command that writes the copy under `.scratch/` and name that copy as the file to test. When a task's steps have run, put `Status: done <date>, do not run again` at the top of this file.
+
 ### Step 1: <what this step does, in one sentence>
```

### 2c. Heavy second-launch stopping rule (`2c-heavy-stopping-rule.patch`)

Includes the one-phrase definition of Medium that the proposal offered as optional ("a defect a builder or user would hit"), because QA's file has no severity scale otherwise (-8 words if removed). Withdrawal condition: a Medium defect after a second-launch PASS (not triggered, see above).

```diff
diff --git a/_docs/agent-kit/team/qa-engineer.md b/_docs/agent-kit/team/qa-engineer.md
--- a/_docs/agent-kit/team/qa-engineer.md
+++ b/_docs/agent-kit/team/qa-engineer.md
@@ -28,3 +28,3 @@
 
-In the Heavy second launch any problem is a FAIL. In a Standard launch a problem fails the verdict only if it breaks a criterion; otherwise list it under Outside the criteria. You change nothing in either launch.
+In the Heavy second launch, only a finding of Medium or higher (a defect a builder or user would hit) that needs a change in this issue is a FAIL. Mark each finding with its severity and `Change in this issue: yes` or `no`. Low findings and notes for later issues are follow-ups and do not fail the verdict. In a Standard launch a problem fails the verdict only if it breaks a criterion; otherwise list it under Outside the criteria. You change nothing in either launch.
 
```

### 2d. Grooming: counting words (`2d-grooming-counting-words.patch`)

```diff
diff --git a/_docs/agent-kit/team/pm.md b/_docs/agent-kit/team/pm.md
--- a/_docs/agent-kit/team/pm.md
+++ b/_docs/agent-kit/team/pm.md
@@ -10,3 +10,4 @@
 - Make the acceptance criteria checkable: someone should be able to look at the UI, an API response or a test result and say yes or no
+- Do not use "exactly", "only" or "all" for a list another role fills in (flagged differences, error codes). Write "at least these, more allowed", and name the classes of choice to sweep (names, formats, statuses, messages)
 - Think about the edge cases the person who filed it did not consider
 - When the task limits what something may do (its tools, network access, files or permissions), say how each limit is enforced, and add a criterion with a case that must be refused. A limit nobody can enforce is a question for the human, not a criterion
```

### 3. QA: "not run" (`3-qa-not-run.patch`) — wording chosen by the PM; the human reads the exact diff at landing

Built from #42's acceptance criterion 1(3) ("QA reports it as 'not run' with the reason and does not count it as passed"), as a bullet in QA's list so the verdict rules are untouched.

```diff
diff --git a/_docs/agent-kit/team/qa-engineer.md b/_docs/agent-kit/team/qa-engineer.md
--- a/_docs/agent-kit/team/qa-engineer.md
+++ b/_docs/agent-kit/team/qa-engineer.md
@@ -14,3 +14,4 @@
 - Stop anything you started before you finish
+- If a criterion needs a tool or step that cannot run in your environment, report it as "not run" with the reason; never count it as passed
 
 Your output is a verdict: PASS or FAIL. It is FAIL if a single acceptance criterion fails, if **Verify** reports FAIL, or if a warning has no convincing reason.
```

### 4. Backlog order (`4-backlog-order.patch`) — wording chosen by the PM; the human reads the exact diff at landing

```diff
diff --git a/_docs/agent-kit/process.md b/_docs/agent-kit/process.md
--- a/_docs/agent-kit/process.md
+++ b/_docs/agent-kit/process.md
@@ -103,2 +103,2 @@
-1. Pick the next open issue in the agreed order. If there are none, build the backlog (see Backlog).
+1. Pick the next open issue in the agreed order. If there are none, build the backlog (see Backlog). Every issue is placed in that order when it is filed, with a trigger (the issue it must land before, or the event that brings it up); an issue outside the order is never groomed.
 2. The PM grooms it, even if it is not yet labelled, when it is owner-authored (`AGENTS.md`, Issues). Groom only the next issue in the agreed order, not a second unlabelled issue while the first waits for the label. The PM's comment records the body hash. Then the human reads the groomed text and adds `approved`; the Engineer starts only after that. If the human changes the text, the orchestrator has the PM record the new hash in a new `PM:` comment before the label is added. Never skip this step. By default (no tier label and no raising proposal is Standard) the PM grooms in full, and the grooming comment carries the `Proposed tier:` line. Only when the human has said the issue is meant to be Light does the PM do the short launch instead (hash record and proposal, no rewrite of the body; see Tiers). The orchestrator reads the effective tier but never decides one.
```

### 5. Launch-environment and feedback-rounds lines (`5-launch-environment-line.patch`) — approved as drafted

The claim line is the template verbatim. The Close line's field names are mine. `make issue-close` matches only the lines listed in `scripts/issue-close.sh`, so the extra line is harmless (read, not run).

```diff
diff --git a/_docs/agent-kit/procedures/orchestrator-comments.md b/_docs/agent-kit/procedures/orchestrator-comments.md
--- a/_docs/agent-kit/procedures/orchestrator-comments.md
+++ b/_docs/agent-kit/procedures/orchestrator-comments.md
@@ -10,2 +10,3 @@
 **Fact:** issue, branch, hash, expected paths, protected files needing approval, and the environment the next role will run in with its missing tools (for example no bun, so the tests step of `make verify` cannot run).
+Also one line, alone and in this form: `Launch environment: <...>; tool: <...>; model: <model or unknown>; tests runnable here: <yes | no: reason>; feedback loop: <local | CI | human-run>`.
 Never name an env file in a claim.
@@ -26,2 +27,3 @@
 **Fact:** every value in those lines.
+When the issue had CI feedback rounds or hand-overs, also one line, alone: `Feedback rounds: CI <n>; human-run <n>; hand-overs <n>` (`make issue-close` does not match it).
 Never close without QA PASS. Post after the last PASS (Light: after `tier-check: PASS`), then `make issue-close N=<n>`. Close as not planned only after the human approved that closure: `Orchestrator: Close as not planned` with `Human approved closure: <YYYY-MM-DD>` and `Backlog review: <path or comment URL>`, then add `REASON=not-planned`.
```

### 6. Contract check in verify (`6-contract-check-in-verify.patch`) — approved via `LINT_CMD` for now

`make verify` runs `_docs/agent-kit/scripts/verify.sh`, which runs `TEST_CMD`, then `LINT_CMD`, then `TYPECHECK_CMD` from `agent-kit.conf`, so this needs no change to the kit script, the `Makefile` or `verify.sh`. Rejected alternatives: `TEST_CMD="make test && make contract-check"` (hides it in the test line); a `Makefile` dependency on `verify` (edits a second protected file); editing `verify.sh` (a kit file, so a local deviation). To be moved when #75's lint target arrives.

```diff
diff --git a/agent-kit.conf b/agent-kit.conf
--- a/agent-kit.conf
+++ b/agent-kit.conf
@@ -24,3 +24,3 @@
 TEST_CMD="make test"
-LINT_CMD=""
+LINT_CMD="make contract-check"
 TYPECHECK_CMD=""
```

CI needs nothing else: `.github/workflows/verify.yml` runs `make install` (`uv sync --locked --all-groups`, which installs the dev group holding `openapi-spec-validator`) and then `make verify`, which will now run `make contract-check` (`uv run --locked openapi-spec-validator openapi.yaml`). The pre-push hook and push check also run `make verify` (not run here). Before landing, the human runs `make contract-check` and `make verify BASE=origin/main` once in the dev container (#74's summary records a passing `make contract-check` there, but not at the batch commit).

### 6b. AGENTS.md Verify line (`6b-agents-verify-line.patch`) — approved, goes with 6

```diff
diff --git a/AGENTS.md b/AGENTS.md
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -20,3 +20,3 @@
 - **Test (one file):** `make test-one FILE=tests/test_socboard.py`
-- **Verify:** `make verify`: tests (Python and frontend), whitespace and weakened-test checks. How to use it: `_docs/agent-kit/procedures/verify.md`.
+- **Verify:** `make verify`: tests (Python and frontend), the OpenAPI contract check, whitespace and weakened-test checks. How to use it: `_docs/agent-kit/procedures/verify.md`.
 - **Assert clean:** `make assert-clean`: confirms nothing in this folder changed (used after QA).
```

### 7. KIT_VERSION (`7-kit-version.patch`) — approved

The base `1.10` names the parent agent kit and stays; only the local counter `<n>` moves, keeping the `<base>+<repo>.<n>` notation that `kit-check.py` requires. `make kit-check` (run earlier, exit 1 as expected for a derivative) accepts any `+socboard.<n>` whose base is right, so the bump is for the record, not for the check; the kit README (line 106) and `procedures/kit-import.md` (line 29) say `<n>` rises with each local change on the same base. Land it last, after all kit edits and the kit-script issues, so it is written once; then run `make kit-check` and expect the same "claim is correct" line with a longer modified list. I did not check whether earlier local changes (for example `17e725e`) already bumped it.

```diff
diff --git a/agent-kit.conf b/agent-kit.conf
--- a/agent-kit.conf
+++ b/agent-kit.conf
@@ -12,3 +12,3 @@
 # pristine kit, <base>+<repo>.<n> (1.9+myrepo.2) once its files are changed here.
-KIT_VERSION="1.10+socboard.1"
+KIT_VERSION="1.10+socboard.2"
 
```

### 8. Light tier for docs-only changes (`8-light-allowed.patch`) — human ruling of 2026-11-12: option 1, the narrow list

Sets `LIGHT_ALLOWED` in `agent-kit.conf` (protected) to `_docs/planning/roadmap-*.md`, `_docs/planning/epoch-batch-*/*.md` and `_docs/runbooks/*.md`, so a small edit to a roadmap, an epoch-batch note or a runbook can pass `make tier-check TIER=light`. The trial protocol, `rubric.md`, `task.md`, records, session summaries and the spec stay outside the list. Source: the delivery-pace ruling (`.kiro/steering/delivery-pace.md`, item 5) and the human's choice of option 1. Words 359 to 363 (+4).

```diff
diff --git a/agent-kit.conf b/agent-kit.conf
--- a/agent-kit.conf
+++ b/agent-kit.conf
@@ -40,7 +40,7 @@
 # check's fixed escalation list (scripts, hooks, tool settings, Makefile, this file,
 # CI, test files, FORBIDDEN) is ignored. Example, Markdown docs only:
 # LIGHT_ALLOWED=( 'README.md' 'docs/*.md' )
-LIGHT_ALLOWED=()
+LIGHT_ALLOWED=( '_docs/planning/roadmap-*.md' '_docs/planning/epoch-batch-*/*.md' '_docs/runbooks/*.md' )
 # Most changed lines a Light change may have (default 20).
 # LIGHT_MAX_LINES=20
 
```

- **Pattern syntax:** a bash glob tested with `[[ "$path" == $pattern ]]` (`_docs/agent-kit/scripts/lib.sh`); `*` crosses `/`. A `.patch` or `.gitattributes` in an epoch-batch folder does not match `*.md`. `_docs/planning/deploy-draft/*` does not match either.
- **Limits:** `LIGHT_MAX_LINES` stays 20 and counts untracked files, so Light fits small edits to existing files, not new documents. The escalation list (`Makefile`, `agent-kit.conf`, CI, hooks, scripts, test files) always wins.
- **Checks (PM, 2026-11-12):** the patch applies alone and after items 6 and 7 in the order 6, 7, 8 on a copy of `origin/main`'s `agent-kit.conf`; a pattern check passes the four example roadmap, epoch-batch and runbook files and leaves the protocol, rubric, task, a patch file, a summary, a record and the spec outside.
- **Epoch (Amendment 2):** not a move: it changes `make tier-check TIER=light`'s result only for those paths, and roles run it only on Light issues, which are not control issues. A strict reading could count it; it lands in the batch either way, so the cost is nil.
- Light still needs its own `approved` issue and the human's `tier:light` label (`process.md`, Tiers).

### 9. QA: three-dot diff (`9-qa-three-dot-diff.patch`) — wording chosen by the PM; the human reads the exact diff at landing

Source: sweep 4, proposal 1. A two-dot diff against the tip of `origin/main` shows files main changed after the branch started; five QA launches on three issues lost time to that.

```diff
diff --git a/_docs/agent-kit/team/qa-engineer.md b/_docs/agent-kit/team/qa-engineer.md
--- a/_docs/agent-kit/team/qa-engineer.md
+++ b/_docs/agent-kit/team/qa-engineer.md
@@ -21,3 +21,3 @@
 
-The orchestrator asks for this in every Standard QA launch. For Heavy issues, a second, fresh launch does only this. Read the diff (`git diff origin/main --stat`, then the full diff) and answer each item, with the file and line for any problem:
+The orchestrator asks for this in every Standard QA launch. For Heavy issues, a second, fresh launch does only this. Read the diff (`git diff origin/main...HEAD --stat`, then the full diff the same way; three dots leave out what main has changed since) and answer each item, with the file and line for any problem:
 - Bugs: logic errors, unhandled bad input, failing underlying commands
```

### 10. QA: a probe counts only on the expected refusal (`10-probe-counts-only-expected-refusal.patch`) — wording chosen by the PM; the human reads the exact diff at landing

Source: sweep 4, proposal 2. On #11, probes that broke on the reviewer's own closure looked like refusals and were nearly counted as covered. Same family as item 3, a different case, so it stays a separate sentence. It sits after the Code review item list, in its own paragraph, clear of 2c's hunk on the next paragraph.

```diff
diff --git a/_docs/agent-kit/team/qa-engineer.md b/_docs/agent-kit/team/qa-engineer.md
--- a/_docs/agent-kit/team/qa-engineer.md
+++ b/_docs/agent-kit/team/qa-engineer.md
@@ -27,2 +27,4 @@
 - Docs the change made out of date
+
+A probe or bypass attempt counts as refused only when the error class and message are the expected refusal; a probe's own error counts as not run.
 
```

### 11. Engineer: draft the human task early (`11-engineer-human-task-early.patch`) — wording chosen by the PM; the human reads the exact diff at landing

Source: sweep 4, proposal 3. The rule to draft a human-task file already exists on this line; this adds when. It does not overlap item 1, which edits the completion-comment bullet further down.

```diff
diff --git a/_docs/agent-kit/team/software-engineer.md b/_docs/agent-kit/team/software-engineer.md
--- a/_docs/agent-kit/team/software-engineer.md
+++ b/_docs/agent-kit/team/software-engineer.md
@@ -13,3 +13,3 @@
 - Do not close the issue, and do not push
-- If the human must run or check something by hand, draft a task file from `_docs/agent-kit/templates/human-task.md` and return it to the orchestrator instead of listing the steps in a comment
+- If the human must run or check something by hand, draft a task file from `_docs/agent-kit/templates/human-task.md` and return it to the orchestrator instead of listing the steps in a comment. When a check cannot run here, draft it as soon as you know, listing each unconfirmed guess, not at hand-over
 - Do not edit protected files (listed in `agent-kit.conf`). If your change affects how the project is installed, run, tested or configured, put the exact proposed change under "Proposed AGENTS.md changes" in your issue comment
```

## Epoch effect

Under Amendment 2 every item above except 7 (and 6b on its own) moves the epoch, and so do #63, #49, #65 and #80. The epoch moves once if all of them are on `main`, with the epoch-start record written, before the first counted issue launches. Nothing here moves it by itself while the batch is held back.

## Proposed landing order

Precondition: #11 is closed and its session summary is merged (the fifth qualifying control issue; `_docs/planning/roadmap-1-core.md`, line 39). No counted issue is claimed until step 6. Re-run `bash .scratch/epoch-batch/apply-check.sh` before each protected commit: #63, #49 and #65 edit kit scripts and `agent-kit.conf`, and may shift lines.

1. **#63** (Engineer, QA): `make issue-close` ignores reflection-only Engineer comments. First, because the roadmap holds Reflection hashes back until it lands, and patch 2a asks for Reflections on every issue. It edits a kit script, so it is protected.
2. **Doc edits 1, 2a, 2b, 2c, 2d, 3, 4, 5, 9, 10, 11** (apply `qa-engineer.md` edits in the order 2c, 3, 9, 10 and `software-engineer.md` edits in the order 1, 11; no Engineer or QA work; the human approves each exact diff; one `HUMAN_APPROVED=1` commit each, or one commit for the lot if the human prefers). Landing them before #65, #49 and #80 means those issues run under the new launch checklist, the stopping rule and the unrun-checks list. If the human wants the plumbing issues run under the old text instead, move this step after step 5; the epoch still moves once.
3. **#65 then #49** (Engineer, QA, both Heavy, together as the roadmap says): the CI base in `.github/workflows/verify.yml` first, then the markers in `verify.sh`, `verify.md` and `agent-kit.conf` (`TEST_FILES`). #65 first so that #49's own `make verify` in CI compares against the merge base.
4. **Patches 6 and 6b (contract-check in verify)**, after #49. Both #49 and patch 6 edit `agent-kit.conf` (lines 25 and 29 are four lines apart, so the contexts may touch): re-run the apply check after #49 and regenerate patch 6 if it fails. If #75's lint target has landed by then, wire the check there instead of `LINT_CMD`.
5. **#80** (Engineer, QA): harden `make backend-run` and `make backend-stop` (a `Makefile` change). It moves the epoch (roadmap line 39 is out of date, see Notes). It must land before #22.
6. **Patch 7 (`KIT_VERSION` to `1.10+socboard.2`)**, then `make kit-check`, then the epoch-start record (new record after `_docs/records/2026-11-10T1506Z-measure-ponytail-epoch-1-start.md`, naming the base commit and the items above). Then claim the next counted issue (#12).

Why this gives one move: steps 1 to 5 each change what a role runs or reads, but no counted issue runs between step 1 and step 6, and the new epoch is recorded once, at step 6, with the final commit as its base.

Not drafted here: #63, #49, #65 and #80 are Engineer issues; their texts are not part of this batch.

## Still open for the human

1. Read the exact diffs of items 3 and 4 at landing (wording is the PM's).
2. Say whether the doc edits (step 2) go before or after #65, #49 and #80.
3. Before landing 6: run `make contract-check` and `make verify BASE=origin/main` in the dev container.
4. Items 9 to 11: read the exact wording at landing (the PM chose it).

## Files in this folder

`1-unrun-checks-clause.patch`, `2a-launch-message-checklist.patch`, `2b-human-task-wording.patch`, `2c-heavy-stopping-rule.patch`, `2d-grooming-counting-words.patch`, `3-qa-not-run.patch`, `4-backlog-order.patch`, `5-launch-environment-line.patch`, `6-contract-check-in-verify.patch`, `6b-agents-verify-line.patch`, `7-kit-version.patch`, `9-qa-three-dot-diff.patch`, `10-probe-counts-only-expected-refusal.patch`, `11-engineer-human-task-early.patch`. Helper scripts: `apply-check.sh`, `check-batch.py` (read-only). Apply one with `git apply <file>` from the project folder.
