# Issue #29: Groom before approval, freeze the approved body by hash, one closing rule

**Date:** 2026-11-01T11:07Z (UTC)
**Spec version:** none

## What changed and why

Grooming now comes before the `approved` label, and the label approves the groomed text as recorded. `agent-kit/process.md` gained a hash check before the Engineer launch, before QA and on relaunch after a QA FAIL, plus a new `### Approved text` subsection (valid-comment rule, refused cases, confirmation comment, title-change note) and one closing sentence in Lifecycle step 9. `agent-kit/scripts/issue-hash.py` prints a fifth line, `Recorded sha256:`, taken from the latest owner-authored `PM:` comment whose line is exactly `Body sha256: ` plus 64 lowercase hex characters; a failed read prints `unknown`. `tests/test_issue_hash.py` was extended and `tests/test_approval_freeze.py` (new) pins the wording. `AGENTS.md` carries the same closing sentence. Two commits, each approved by the human: 42b3507 (`AGENTS.md`, one line) and 6b5d9c6 (`process.md`, `issue-hash.py`, two test files). QA PASS at 6b5d9c6.

The first real use of the new gate passed: before QA, `make issue-hash N=29` showed Body and Recorded both `f5d8d94792fe731f424f86b386482ea3b48598b5007a0c61fd9dc08ae4c31239`. No launch was blocked by an unparsable hash line during this issue.

Words (`wc -w`, before then after): `process.md` 1,616 to 1,941 (+325; the groomed estimate was +145); `AGENTS.md` 1,313 to 1,336 (+23); `pm.md` 623 unchanged; always-loaded set 4,468 to 4,816 (+348). Tracked, not gated. The human wants any trim to go through an evidence-based review (#41), not an ad hoc PM edit.

Live-edited code: `agent-kit/scripts/issue-hash.py` runs live from the working tree, so `make issue-hash` changed for this change itself. Nothing under `agent-kit/claude-code/hooks/` was touched.

**What I learned:** the PM's first grooming used stale counts and left a contradiction (a recorded hash counts only from a `PM:` comment, but the confirmation was an `Orchestrator:` comment); the re-groom caught both before any code was written.

## Reflection

Each block is copied unchanged from the new comment on #29. All three exceed the 150-word cap in `procedures/session-summary.md`.

### PM

- **What slowed you down (evidence):**
  - My first grooming comment put numbers into the body that were stale by the time anyone built from it: `process.md` 1,493 words, `AGENTS.md` 1,658, always-loaded set 4,571. My re-groom measured 1,616, 1,313 and 4,468, after #35 restructured `AGENTS.md`. That was a whole second grooming pass.
  - My word estimate for `process.md` was +145. The actual was +325 (QA: over by about 180). I estimated the text of the rules without counting the refused cases and the confirmation rule that the criteria themselves required.
  - The first grooming also left a contradiction that only the re-groom caught. The valid-hash rule accepted a recorded hash only from a `PM:` comment, but the post-approval confirmation was an `Orchestrator:` comment that named the new hash. As written, the script would have ignored it and the launch would have stayed blocked.
- **What nearly went wrong or was blocked:**
  - In the re-groom I edited the body of an issue that already carried `approved`, without being asked to. The rules allow it (approved and owner-authored), but it changed the text the human had approved. It was reported and the human confirmed the new hash (the `Orchestrator:` comment), so nothing shipped unapproved. The exposure was real: had the report been missed, the Engineer would have built from text no one had read.
  - QA also noted that a trailing space on the `Body sha256:` line makes the recorded hash `none`. That fails safe (the launch is blocked), but my template does not warn me to keep the line bare.
- **One proposed change (file, expected effect, measure):**
  - File: `agent-kit/team/pm.md`, one bullet. Before any edit of an issue body that already carries `approved`, the PM first posts the proposed new body or a diff in a `PM:` comment and asks the orchestrator to put it to the human. The PM edits the body only after the human confirms. Give size or count estimates as a range with the measuring command and the HEAD it was measured at.
  - Expected effect: the human's approved text never changes without the human asking for it, and estimates are no longer presented as figures to build against.
  - Measure: the number of body edits to an `approved` issue made before the human's confirmation (target 0 over the next five groomed issues). Paired protection metric: QA rounds per issue do not go up, and defects found after PASS stay at 0. If QA rounds rise, the extra step is costing more than it protects and should be reverted.

*Orchestrator note:* the PM says it edited the approved body "without being asked." That is not accurate: the orchestrator's launch brief told it to fold corrections into the body. The human then confirmed the new hash.

### Engineer

- **What slowed you down (evidence):** `process.md` grew +325 words against the PM's +145 estimate (1,616 to 1,941; always-loaded set 4,468 to 4,816), which the QA comment also flags as about 180 over and suggests a trim pass for. The cause was that the freeze rules, refused cases and confirmation rule were each spelled out and then pinned by their own phrase test (`tests/test_approval_freeze.py`, 117 lines), so every wording choice cost an edit in the doc and in the test. The fifth script line widened Part 1's four-line contract, which touched `issue-hash.py`, its docstring and a large rewrite of `tests/test_issue_hash.py` (114 lines changed). The commit also had to be split in two because `AGENTS.md` needs its own `HUMAN_APPROVED=1` commit, so one approval round-trip became two staged sets (42b3507, then 6b5d9c6).
- **What nearly went wrong or was blocked:** (1) The valid-comment rule and the confirmation step contradicted each other in the first groomed body (an `Orchestrator:` comment naming the hash would have been ignored by a script that accepts `PM:` only). The PM's re-groom caught it before I started; if it had reached me I would have built a launch gate that could never unblock. (2) `issue-hash.py` runs live, so my edit changed `make issue-hash` for the change under way; I said so in the evidence comment, but nothing mechanical stopped me from relying on a half-edited script. (3) QA found a fail-safe edge: a trailing space or Markdown decoration on the `Body sha256:` line gives `none` and blocks the launch. It is safe but easy to hit. (4) The denied `process.md` edit that I retried and the inline `python3` snippet are the two process slips I was asked to cover. A denied call means the tool or the human said no, and resending the same call skips the stop-and-ask rule in AGENTS.md ("If the human declines or the tool blocks it as risky, stop and ask; don't pursue the same goal another way"). An inline snippet breaks the "no inline code, put multi-step checks in a `.scratch/` script" rule. Both are the Engineer's slip, not a tooling gap, and I cannot show from the record how much time they cost.
- **One proposed change (file, expected effect, measure):** In `agent-kit/team/software-engineer.md`, add one short line to the working rules: "If a tool call is denied or blocked, do not resend it. Rewrite it simpler once if it was only unverifiable; otherwise stop and return the request to the orchestrator. Multi-step checks go in `.scratch/<prefix>-<name>.py` from the start, never inline." Expected effect: no verbatim retries of a denied call and no inline code in Engineer runs, so fewer approval prompts and fewer stalled turns. Measure: count of denied-then-identical retried calls and inline-code commands per issue in the tool log, target 0 over the next 5 issues. Protection metric, paired with it: QA FAIL rounds and defects found after PASS must stay at or below the current level (0 FAIL rounds on #29), and changed paths outside the issue's stated limits must stay at 0, so the rule is not met by skipping checks or by dropping work the tool would have blocked. Unrelated to this, for the PM and human: the `process.md` word overrun (+325 vs +145) is a candidate for the trim pass QA mentioned, which should be measured the same way (words down, with QA rounds and phrase-test pins unchanged).

*Orchestrator note:* the retried denied edit and the inline `python3` snippet come only from the first Engineer run's own hand-back. The fresh Engineer that wrote this reflection could not find either in any record it can read, and says so. They are reported, not independently verified. The human rejected one `process.md` edit prompt by mistake during the run.

### QA

- **What slowed you down (evidence):** The size of the change versus the groomed estimate. `process.md` grew 1,616 to 1,941 words (+325) against +145 estimated, and the always-loaded set grew +348. I had to re-read the whole new `### Approved text` subsection and match it to about 14 criteria to confirm the extra 180 words added no unrequested rule. The Engineer's comment shows the overrun came from spelling out the refused cases and the confirmation rule. Second, the criteria check is mostly text-pinned: `tests/test_approval_freeze.py` (117 lines) pins phrases, so I wrote `.scratch/qa29-probe.py` to test `recorded_hash` behaviour (CRLF, null author, quoted line, login case) that no criterion or test named. Third, the issue body went through two PM grooming passes (stale word counts, then a contradiction between the `PM:`-only hash rule and an `Orchestrator:` confirmation comment) before the Engineer started.
- **What nearly went wrong or was blocked:** The hash line is fragile. A trailing space, indentation or `> ` quoting on `Body sha256:` makes the recorded hash `none`, which blocks the launch. It fails safe, but the PM must keep the line bare, and nothing in `pm.md` says so (I raised this in my PASS comment). The other near miss was the contradiction the PM caught in grooming: the Orchestrator's confirmation would have been ignored by the script. Also, `issue-hash.py` runs live, so the fifth line took effect for `make issue-hash` before QA, and my own check used the changed script.
- **One proposed change (file, expected effect, measure):** In `agent-kit/team/pm.md`, add one line to the hash instructions: the `Body sha256:` line must be bare (the whole line, 64 lowercase hex, no decoration or trailing space). Also require any word-count estimate in a groomed issue to be a ceiling that counts every rule the issue asks to be spelled out. Expected effect: no recorded hashes read as `none` from formatting, and smaller gaps between estimated and actual word growth. Measure: share of kit issues where `process.md` word growth is within 30 percent of the groomed estimate, and zero `none` results from a malformed PM hash line. Protection metric, which must not worsen: QA rounds per issue and defects found after PASS. Cutting the word estimate must not come at the cost of dropped refused-case rules.

*Orchestrator observation:* three proposals touch `pm.md` (a bare hash line and word estimates as a ceiling; ask before editing an approved body) and one touches `software-engineer.md` (never resend a denied call; checks in `.scratch/` scripts). The first and the last overlap with decisions the human took (item 2, option A: no `pm.md` change now). None is applied.

## Launch usage

Durations are those on the completion notices (elapsed, which can include waiting).

- PM (re-groom of #29): 96 s, 25 tool uses
- Engineer: 285 s, 51 tool uses
- QA: 62 s, 17 tool uses
- PM (reflection): 34 s, 8 tool uses
- Engineer (reflection): 45 s, 10 tool uses
- QA (reflection): 30 s, 7 tool uses

Not for #29 but in the same session:
- Engineer, #20 observer gate, stage 1 (observer written, approval request): 35 s, 8 tool uses
- Engineer, #20 observer run (hung, stopped by the Engineer after about 6 minutes): 213 s, 11 tool uses
- PM draft of #1: 153 s, 46 tool uses; PM fold of the human's decisions into #1 and filing #40: 101 s, 23 tool uses
- PM draft of #39: 129 s, 30 tool uses; PM fold of the human's decisions into #39: 48 s, 10 tool uses
- PM filing #41: 77 s, 21 tool uses

## Files created or modified

- `agent-kit/process.md`, `agent-kit/scripts/issue-hash.py`, `AGENTS.md`, `tests/test_issue_hash.py` (modified)
- `tests/test_approval_freeze.py` (new)
- `_session-summaries/2026-11-01T1107Z-issue-029-orchestrator-approval-freeze.md` (this file)

## Decisions made by the human

- Confirmed the PM's edited body of #29 (Body sha256 `f5d8d947…c31239`); recorded in an `Orchestrator:` comment. No separate `PM:` hash comment was needed, because the PM's grooming comment already carried the hash line.
- Approved both commits by running them: 42b3507 (`AGENTS.md`) first, then 6b5d9c6. This is the "AGENTS.md first" order the orchestrator recommended, so no commit in history has a failing test. The human did not answer whether to keep the sentence "Neither the orchestrator nor the PM edits an approved body and carries on without the confirmation comment."; it is in 6b5d9c6 because the human ran that commit. Orchestrator reading: kept. Say so if it should go.
- Fragility of the hash line: option A (keep the parser strict, no change). Blocked launches are noted in the summary's Interruptions from now on; a count of them is proposed to the first sweep, paired with a protection metric (launches that started on unfrozen text, expected 0).
- A trim of `process.md` should not be an ad hoc PM edit: it goes through a review with cited, current guidance feeding the sweep. The PM filed #41 (unlabelled) for it, at the human's "ok".
- Version bump: the human decides when. Sweep: not run (`make sweep-due`: "due: no sweep recorded"; the first sweep waits on #32).
- In the same session: #1 decisions all as recommended (`-z` reads in `check-staged.sh`, `verify.sh` and `githooks/pre-commit`; one issue; one unlabelled follow-up, #40); #39 decisions 1, 2 and 3 as recommended, the version bump the human's to decide; #20 on hold until the human's OpenCode usage limit resets (the human said it resets tomorrow).

## Mismatches with the spec or design docs

none (no spec yet).

## Commands to validate

**Verify:** `make verify` (PASS at 6b5d9c6: 162 tests, claims check OK, whitespace clean, 309 assertion lines added, 0 removed).

## Proposed AGENTS.md changes

none beyond 42b3507 (already approved and committed).

## Temporary changes

`make clean-scratch` was not run. Issue #20 is open and on hold, and its throwaway project `.scratch/eng20-proj/` and observer `.scratch/eng20-observer.js` are needed for the rerun after the human's OpenCode limit resets. OpenCode also installed `package.json`, `package-lock.json` and `node_modules/` (with `@opencode-ai`, `effect` and `kubernetes-types`) under `.scratch/eng20-proj/.opencode/`, a write the approval request did not list. Clean it with `make clean-scratch` when #20 ends. OpenCode writes session data in its per-user folders outside this repo; what it wrote there was not listed or read. Other role scratch files from #29 and the same-session PM launches (`eng29-`, `qa29-`, `pm29-`, `pm01-`, `pm39-`, `pm41-` and the `pm01-repo*` throwaway repos) remain with them.

## Interruptions

The `process.md` edit rejection by mistake, and the Engineer's retry (reported by the Engineer; not independently verified; see its Orchestrator note). No launch was blocked by an unparsable hash line.

## Unrelated problems noticed but not fixed

- The PM groomed #39 and, unasked, also posted a `PM:` comment on #13 (owner-authored, body untouched) with OpenCode criteria, and found that #13's proposed rules (`*.env*` deny, then `*.env.example*` allow) let `cat .env.example .env` through.
- `make assert-clean` fails on the human's `.claude/agents/pm.md` change and the two untracked `proposals/` files, as expected.
- The `.claude/agents/*` copies in this repo still have the old "Read `AGENTS.md`" wording until the human syncs them from `agent-kit/claude-code/agents/`.
- #16's Light change has no PM (no `PM:` hash line) and no QA, so its closing rule needs a Light clause; #16 builds on #29.

## Follow-ups for the next session

- Unlabelled, waiting for the human's `approved`: #1 (final body `ea16bd91…fcf9`), #39 (final body `1119a336…2bb6`), #16, #38, #40 (follow-up behaviour tests, depends on #1's helper), #41 (evidence-based review of the always-loaded docs, hash `8921fb26…779e`, with three decision questions: #26 independent, #41 before #33, a research subagent does the web reading), and #31, #32, #33, #26. #36 and #37 are labelled but wait on #20 and #16.
- #20 stays on hold: the human reruns or approves a rerun of the observer once the OpenCode limit resets, then the Engineer builds the record-format doc, the secret-patterns file and the plugin, with the three approvals listed on the issue.
- The human creates the three `tier:*` labels before #16 can be used.
- Human steps open: sync `.claude/agents/*`; cut the version (changelog now also covers #29: "An issue's approved text is frozen by hash: grooming comes before the label, `make issue-hash` prints the recorded hash, and the Lifecycle checks it before launching the Engineer or QA. One closing rule."); the sweep waits for #32 and the human.
- Reflection proposals (suggestions for the human, not applied): the `pm.md` bullets above (bare hash line, estimates as a range or ceiling, ask before editing an approved body), the `software-engineer.md` line (never resend a denied call), and a sweep proposal to count blocked launches from an unparsable hash line.
