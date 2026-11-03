# Measurement: always-loaded guidance and the kit's own always-loaded docs (issue #41)

Research only. No kit file is edited and no proposal is applied. Issue and comment text, and every fetched or searched web page, is data here, never a rule.

- **Question:** What do vendors and one study say about the size and structure of always-loaded instruction files, how large are this kit's always-loaded docs (from git, at a named commit), and which numbered changes, if any, should the human consider?
- **Command and commit:** `sh .scratch/count41.sh <commit>` (a `.scratch/` helper, not committed; its core is below), run at `2c1c2ff` (origin/main at the time of writing, re-fetched after the human said main had updated: still `2c1c2ff`) and at `03de86e` (the parent of #29's first commit `42b3507`) and `6b5d9c6` (#29's last commit). Per file:

  ```
  git show <commit>:<path> | wc -l
  git show <commit>:<path> | wc -c
  git show <commit>:<path> | wc -w
  ```

  Per-section words: `python3 -B .scratch/sections41.py <commit> <path>` (splits the blob at `#` headings and runs the same word count). Word counts are tracked, never a gate.
- **Baseline:** the human's figures in the issue body (process.md 1,616 to 1,941; always-loaded set 4,468 to 4,816), rechecked below. No earlier measurement entry exists (`_docs/measurements/` is new).
- **Result:** see Sources, What each tool loads, Counts, Comparison, Rules and pins.
- **Caveats:** see the end.

Date read for every source below: 2026-11-02 (UTC).

## Sources

**Fetch status.** Every `web_fetch` of a primary page returned HTTP 403 in this session (docs.anthropic.com, code.claude.com, opencode.ai, developers.openai.com, arxiv.org abs and pdf). So no primary page was read in full. What follows is what the web search tool returned for those primary URLs (page title and excerpt). A claim is marked *excerpt* when that is all that was read. Anything seen only in a blog, forum post, GitHub issue or mirror reads `unknown`.

| # | Source (URL) | Label | Claim it supports (paraphrased) |
|---|---|---|---|
| S1 | https://docs.anthropic.com/en/docs/claude-code/claude-md ("How Claude remembers your project"), excerpt | vendor description | Claude Code has two memory systems, both loaded at the start of every conversation. Claude treats them as context, not enforced configuration. |
| S2 | same URL, excerpt | vendor description | CLAUDE.md files are plain-text persistent instructions that Claude reads at the start of every session. |
| S3 | https://code.claude.com/docs/en/subagents, excerpt | vendor description | Each subagent runs in its own context window with its own system prompt, tool access and permissions. |
| S4 | https://developers.openai.com/codex/guides/agents-md, excerpt | tool limit | Codex stops adding AGENTS.md files once their combined size reaches `project_doc_max_bytes`, 32 KiB by default; it suggests raising the limit or splitting across nested directories. |
| S5 | https://developers.openai.com/codex/concepts/customization, excerpt | vendor recommendation | AGENTS.md is durable project guidance applied before work starts, and it should be kept small. |
| S6 | https://opencode.ai/docs/rules (excerpt seen via https://docs.dev.opencode.ai/docs/rules and the docs source https://github.com/anomalyco/opencode/blob/dev/packages/web/src/content/docs/rules.mdx) | vendor description | OpenCode takes custom instructions from an AGENTS.md file; its contents are included in the model's context. |
| S7 | https://arxiv.org/abs/2602.11988 (Gloaguen et al., "Are Repository-Level Context Files Helpful for Coding Agents?"), abstract excerpt | research finding | In their experiments context files did not generally improve task success and raised inference cost by over 20% on average, for both generated and developer-written files, across the models and agents they tested. |
| S8 | https://arxiv.org/pdf/2602.11988, excerpt | research finding | The authors conclude context files help mainly to specify non-standard practices, and that any attempt to improve performance should be evaluated before deployment. |

Not verified from a primary page (all `unknown` here):
- **Claude Code's "under 200 lines per CLAUDE.md" target and its stated reason (longer files cost context and reduce adherence).** Many third-party posts attribute it to the Claude Code memory docs (for example https://getunblocked.com/blog/audit-fix-bloated-claude-md/ and posts on dev.to), but no primary excerpt containing it was returned. Used below only as "reported, `unknown`".
- That `@AGENTS.md` imports save no context (secondary posts only). `unknown`.
- Whether Claude Code subagents receive CLAUDE.md. GitHub issues on anthropics/claude-code report both outcomes and conflict with each other; they are user reports, not documentation. `unknown`.
- Whether OpenCode falls back to CLAUDE.md. A third-party docs mirror says older docs had a fallback and a later version does not. `unknown` for the version in use.
- Any token figure. `unknown` (#26 owns it).
- S7 wording differs between copies (OpenReview and ResearchGate excerpts say "no improvement" or "tend to reduce"), so the result depends on the paper version. The benchmarks and agents are `unknown` to me beyond the abstract.

No instruction aimed at an agent (run, install, add to AGENTS.md) was found in any search excerpt. Nothing was acted on.

## What each tool loads at session start for this repo

- **Claude Code, main session.** `CLAUDE.md` (2 lines, 15 words: `@AGENTS.md` plus a scratch note). Per S1/S2 CLAUDE.md files load at the start of every session. That the `@AGENTS.md` import is expanded at launch: `unknown` (primary page not read). `AGENTS.md` therefore arrives through the import. `agent-kit/process.md` and `team/*.md` are not loaded at session start: `AGENTS.md` "Read when" tells the agent to read them, so they are read only if the agent follows that line.
- **Claude Code, subagents (`.claude/agents/*.md`).** The definition body is the subagent's own prompt (S3, excerpt). Whether CLAUDE.md/AGENTS.md also reaches a subagent: `unknown`. The kit's generic launch message, and this task's, tell the role to read `AGENTS.md` and then its `team/` file; neither names `process.md`. `AGENTS.md` "Read when" line 1 does name `process.md` for "before working an issue". Whether a role follows that line is not observable from git (the tool's session log is outside the project and was not read): `unknown`.
- **OpenCode.** `AGENTS.md` is read as instructions (S6). Whether `CLAUDE.md` is also read by the version in use: `unknown`. `.opencode/agents/*.md`: the docs page was not read: `unknown`.
- **Codex.** Not used by this repo's setup; S4 limit recorded for comparison only.

Consequence for what "always-loaded" means: it differs by role. The orchestrator meets `AGENTS.md` and `process.md`; a launched role meets `AGENTS.md`, its `team/` file and its definition, and `process.md` only if it follows the Read-when line.

## Counts

Command per file as above; `wc -w` counts whitespace-separated words, `wc -c` bytes. Commit `2c1c2ff` (HEAD, origin/main) unless stated.

| File | Lines | Bytes | Words |
|---|---|---|---|
| `AGENTS.md` | 83 | 9,711 | 1,473 |
| `agent-kit/process.md` | 149 | 18,582 | 3,042 |
| `agent-kit/team/pm.md` | 39 | 4,382 | 764 |
| `agent-kit/team/qa-engineer.md` | 74 | 3,977 | 675 |
| `agent-kit/team/software-engineer.md` | 37 | 2,674 | 442 |
| **Total (the 5 files)** | **382** | **39,326** | **6,396** |
| `CLAUDE.md` | 2 | 97 | 15 |
| `.claude/agents/pm.md` / `qa-engineer.md` / `software-engineer.md` | 6 / 6 / 11 | 590 / 505 / 759 | 87 / 72 / 99 |

Rechecking the issue's claims from git:

| Commit | AGENTS.md | process.md | pm | qa | engineer | Total words |
|---|---|---|---|---|---|---|
| `03de86e` (before #29) | 1,313 | 1,616 | 623 | 505 | 411 | **4,468** |
| `6b5d9c6` (#29 last commit) | 1,336 | 1,941 | 623 | 505 | 411 | **4,816** |
| `2c1c2ff` (HEAD) | 1,473 | 3,042 | 764 | 675 | 442 | **6,396** |

- The human's figures check out exactly: process.md 1,616 to 1,941 and the set 4,468 to 4,816 (#29 added +325 and +348). Bytes of the set: 27,663, 29,736, 39,326; lines: 328, 336, 382.
- The numbers have moved on: from `6b5d9c6` to HEAD the set grew by 1,580 words (+33%): process.md +1,101, AGENTS.md +137, pm +141, qa +170, engineer +31. Over the whole range it is +1,928 words (+43%). This includes #50, #13, #37 and #54 and other issues merged since. I did not split the +1,580 by issue.
- process.md at HEAD, words per section: Tiers 838, Lifecycle 660 plus Approved text 176, Orchestrator 224, blocked 156, stops early 114, Planning 109, Backlog 113, Start 81, Roles 180, Commits 120, Definition of done 128, Issue comments 54, Keeping the setup current 53, title 36. AGENTS.md: Non-negotiables 446, Issues 327, Project gotchas 225, Commands 134, Read when 96, Project settings 104, Enforced by hooks 62, intro 79.
- Per role at HEAD, words if the role reads each named file: orchestrator `CLAUDE.md` + `AGENTS.md` + `process.md` = 4,530; Engineer `AGENTS.md` + engineer file + definition = 2,014 (5,056 with `process.md`); PM 2,324 (5,366 with); QA 2,220 (5,262 with).
- Tokens: `unknown`.

## Comparison with the guidance

Applying a target is not evidence that a file performs better or worse; S7 is the only performance evidence found and it concerns whether context files help at all.

- **Claude Code 200-line target (reported, `unknown`).** `AGENTS.md` 83 lines and `process.md` 149 lines are each below 200; the five-file set (382 lines) is above it if it were treated as one file, which the target does not say. Lines are a weak measure here: average 17.7 words per line in `AGENTS.md` and 20.4 in `process.md`, so the line count understates the words.
- **Codex 32 KiB (S4, tool limit).** Only the `AGENTS.md` chain counts toward it: 9,711 bytes, about 30% of 32,768. The five-file set is 39,326 bytes (38.4 KiB) but Codex would not load `process.md` or `team/*` automatically, so the limit is not exceeded and does not apply to the set.
- **"Keep it small" (S5, vendor recommendation).** No number given, so no above/below judgement is possible.
- **OpenCode (S6).** No size guidance found: `unknown`.
- **S7/S8.** Context files are most useful for non-standard practices, and cost over 20% more inference in the tested settings. This kit's files are process rules, much of it non-standard by design, but I cannot say how their cost or benefit compares to the tested files: `unknown`. The finding supports the rule test used below (keep non-standard rules and known pitfalls; treat discoverable content as a candidate) and supports a protection metric before any cut (S8: evaluate before deployment).

## Proposals

Nothing below is applied. Each needs the human's ruling one by one. Words are measured with `git show <commit>:<path> | wc -w` before and after, per file and for the set. Protection metric for all of them (the efficiency metric alone is "unmeasured", `procedures/sweep.md` Safeguard 4): over the next 5 closed issues compared with the 5 before, QA rounds per issue, defects found after PASS, and changed paths outside the issue's Constraints; plus, for P1 and P2, any Heavy gate or incident step that is skipped (the orchestrator's check and the human's reading are the only enforcement). Baselines would be taken by the sweep from session summaries and `QA:` comments, not by the proposal's author.

All "expected word change" figures are counted on the blob at `2c1c2ff` by `.scratch/deltas41.py`; the new text is my draft.

**P1. Move the Light details and the Heavy gates out of `process.md` behind a trigger.**
- Evidence: the Tiers section is 838 words, 28% of `process.md`. A Standard issue (the default, per the label rule in the same section) needs none of the Light bullets or Heavy gates. S7 gives the general case for carrying less; S5 for keeping the always-read file small.
- File: `agent-kit/process.md`, new file `agent-kit/procedures/tiers.md`, a blueprints row.
- Change: move to `procedures/tiers.md` the bullets "Light issues get a short PM launch" (122 words), "When Light stops being Light" (53), "Every Light change has its own `approved` issue" (28), "Review of Light" (37), and the "Heavy gates" bullet with its three sub-bullets (245 words). Keep in `process.md` the table, "The human's label sets the tier", "Proposals", "Raise, never lower" and "What enforces this", and add one pointer bullet (29 words) naming the new file and when to read it.
- Expected effect: `process.md` −456 words net (3,042 to about 2,586); the new file about +485 words, so the kit as a whole grows about 30 words, and only sessions that handle a Light or Heavy issue read it. Effect on actual reading is `unknown` (see Caveats).
- Measure: set total and `process.md` words from git; paired with the protection metric above.
- Rule judgement: Light/Heavy rules are non-standard process practice (keep, move). Pinned by: `tests/test_heavy_gates.py` (reads `process.md` between `## Tiers` and `## Lifecycle` for the ADR, second-QA and lowering phrases: its `tiers` slice must read the new file, and "Lowering needs the human to change the label" stays in the kept "Raise, never lower" bullet); the claims check (new `procedures/tiers.md` and `_docs/agent-kit/...` code spans must resolve, and `blueprints.md` must name the new file or its directory); `tests/test_tier_check.py` exercises `check-tier.sh`, not these words (I could not run it here, #52). Light behaviour is otherwise enforced only by `make tier-check` and the orchestrator.
- Touches protected paths: `agent-kit/*`; test change in `tests/` goes in with it. `HUMAN_APPROVED=1` commit.

**P2. Move the two incident sections to a procedure.**
- Evidence: "When a role's actions are blocked" (156 words) and "When a role stops early" (114) apply only after something goes wrong and only to the orchestrator.
- File: `agent-kit/process.md`, new `agent-kit/procedures/role-incidents.md`.
- Change: replace both sections (270 words) with one heading and the sentence "When a role's actions are blocked, or a role stops early, read `_docs/agent-kit/procedures/role-incidents.md` before relaunching it." (25 words total with heading).
- Expected effect: `process.md` −245 words; new file about +270; kit about +25.
- Measure: `process.md` words; protection metric above, plus count of incidents where the orchestrator relaunched a role without checking `git status` (from summaries).
- Rule judgement: both are known-pitfall rules (keep, move): the checks before relaunch (git status, half-edited issue) are not discoverable from the repo. Pins: no phrase test found for these sections (grep of `tests/` and `agent-kit/scripts/` for their headings returned nothing); the claims check covers the new path and the blueprints row. The "never copy the tool's session log into the project" sentence is also a settings-read boundary in `AGENTS.md`'s Non-negotiables; keep that sentence intact in the new file.
- Protected: `agent-kit/*`.

**P3. Remove the duplicated tier text from Lifecycle step 2.**
- Evidence: step 2 repeats what the Tiers bullets say about the default tier, the short Light launch and "the orchestrator never decides a tier" (59 words).
- File: `agent-kit/process.md`, Lifecycle step 2, from "By default (no tier label is Standard)" to the end of the step.
- Change: replace with "The PM's grooming comment carries the `Proposed tier:` line (see Tiers)." (11 words). The sentences `tests/test_approval_freeze.py::test_step_2_groom_before_label` pins are earlier in the step and stay.
- Expected effect: −48 words. Measure: `process.md` words; protection metric above. Do after or with P1 (the short-launch detail then lives only in `tiers.md`).
- Rule judgement: duplicated text; the rule stays once, in Tiers (or `procedures/tiers.md` under P1). Pin: none on the removed tail (checked in `test_approval_freeze.py`).
- Protected: `agent-kit/*`.

**P4. Move the "Review of Light" bullet to an issue.**
- Evidence: the bullet (37 words) is a one-time review after ten Light uses, not a rule an agent follows each session.
- File: `agent-kit/process.md` (or `procedures/tiers.md` if P1 is accepted; then it moves instead of being deleted and this proposal is subsumed).
- Change: delete the bullet; the PM files an unlabelled follow-up issue "Review Light after ten uses" for the human to label.
- Expected effect: −37 words. Measure: `process.md` words; protection: whether the review happens (follow-up issue closed), plus the metric above.
- Rule judgement: not a rule; a reminder. Candidate for removal. No pin found.
- Protected: `agent-kit/*`.

**P5. Say who reads `process.md`.**
- Evidence: `AGENTS.md` "Read when" line 1 sends every role to `process.md` (3,042 words, much of it orchestrator-only: Orchestrator, blocked, stops early, Backlog, Planning, Start of every session, Tiers), while the generic launch message in `process.md` sends launched roles only to `AGENTS.md` and their `team/` file. The two disagree, and what a role really reads is `unknown`. The rules a role needs from `process.md` already have their own triggers (issue comments, commits, Definition of done).
- File: `AGENTS.md` (shared block) and `agent-kit/templates/AGENTS.md.template`, changed in the template first as the file's own marker says.
- Change: old: "Before working an issue -> `_docs/agent-kit/process.md`, then your role file in `_docs/agent-kit/team/`." New: "Orchestrator, before working an issue -> `_docs/agent-kit/process.md`. Every role, before starting -> your role file in `_docs/agent-kit/team/`." (13 to 18 words, +5.)
- Expected effect: +5 words in `AGENTS.md`. Words saved per launched role: up to 3,042 if roles now read the whole file, 0 if they do not: `unknown`. This is why it is not a word-count proposal; it removes a contradiction.
- Measure: unmeasured as a size change. Paired metric: comments without a role prefix (`PM:`/`Engineer:`/`QA:`), commits not following `#commits`, QA rounds; and the `Launch usage` lines in session summaries once #26 gives a token source.
- Rule judgement: the line is process wiring (keep, clarify). Pins: `tests/test_kit_env_and_launch.py` pins the launch-message regex only, not this line; the template and `AGENTS.md` shared block must stay identical (no test found that diffs them beyond the Fetch-an-issue slot line in `tests/test_issue_dump.py`, which this does not touch).
- Protected: `AGENTS.md`, `agent-kit/*`.

**P6. Add a make target that prints these counts.**
- Evidence: the issue says counts come from `git show | wc` and a script should be a separate proposal. Every sweep (`procedures/sweep.md` step 2) repeats the same recipe by hand.
- File: `Makefile`, a new `agent-kit/scripts/` script (live-running path), a Commands line in `AGENTS.md`.
- Change: `make always-loaded COMMIT=<hash>` prints lines/bytes/words per file and the total from git blobs (my `.scratch/count41.sh` is a draft).
- Expected effect: +about 25 words in `AGENTS.md`; no reduction. Measure: sweep entries reuse it; unmeasured as an efficiency change since it only measures.
- Pins/enforcement: a new script needs a test; `make test` syntax-checks scripts; the claims check requires any new kit path in blueprints. It would be a live-running path: say so in the issue.
- Protected: `Makefile`, `agent-kit/*`, `AGENTS.md`. Needs a new dependency? No (coreutils and git).

**No change proposed** for these, with the evidence:
- `AGENTS.md` Non-negotiables (446 words) and "Enforced by hooks": each rule is a known pitfall or non-standard practice, several pinned (env rule and hook line by `tests/test_kit_env_and_launch.py`; the settings-read slot by `tests/test_settings_read_rule.py`; closing sentence by `tests/test_approval_freeze.py`). S8 favours keeping such rules.
- `AGENTS.md` Issues (327) and Project gotchas (225): non-standard to this repo (public repo, `agent-kit/` path, pre-push on the human's machine). Not discoverable from the repo.
- `team/*.md` (1,881 words together) and `.claude/agents/*` (258): already short; only the engineer and QA files are partly pinned by tests (`test_heavy_gates.py` for QA).
- Keeping the setup current (53 words): the trigger is not stated elsewhere; keep.
- Do not trim by lines or words as a goal. Words are tracked, never a gate.

**Totals.** P4's bullet is one of the four Light bullets P1 moves, so P4 only counts if P1 is declined. If P1, P2 and P3 are accepted: `process.md` 3,042 to about 2,293 (−749); the five-file set 6,396 to about 5,647 (−749, −12%); the two new files add about 755 words that are read only on trigger, so the kit as a whole is roughly unchanged. If only P2, P3 and P4 are accepted: −330. These are expected values; the actual is reported after it ships.

## Caveats

- **No primary page was fetched** (HTTP 403 for all). Every vendor claim is an excerpt from the search tool's result for the primary URL, not a read of the page. QA should re-fetch each URL in S1 to S8 from a session with web access and check the claim; the 200-line target and the import and subagent behaviours are the open items.
- The Claude Code 200-line target and its reason are `unknown` here, although the issue and #33 name them. Do not cite them as verified in #33 until a primary page is read.
- What roles actually read (`process.md` especially), and any token cost, are `unknown`; word counts say how big the files are, not what a session loads.
- The set of "always-loaded" files follows the issue (five files). `CLAUDE.md` and `.claude/agents/*` are given separately; `agent-kit/claude-code/agents/*` copies differ by a few words from `.claude/agents/*`.
- Counts are from git blobs at the commits named; the working tree was not used. `origin/main` was fetched twice (before the work and after the human's note that main had updated) and was `2c1c2ff` both times. If main moves again the figures need a rerun with the same script.
- `tests/test_tier_check.py` was not run (hangs here, #52). Test pin statements come from reading the test files, not from running them with the proposed changes.
- Word deltas for P1 to P4 use my draft replacement text; the real text may differ by a few words.
- No proposal edits a protected path now. Any later issue from P1 to P6 touches protected paths (`agent-kit/*`, possibly `AGENTS.md`, `Makefile`) and needs `HUMAN_APPROVED=1` after the human approves the diff.
- Untrusted text: no search excerpt carried an instruction to an agent. None was followed.
- Decisions assumed from the PM's defaults: 1(a) tokens independent and `unknown`; 2(a) #41 runs before #33 so #33 can cite verified sources (and this entry says the 200-line figure is not yet verified); 3(a) web reading by the engineer role, with the research notes in `.scratch/pm41-research.md` (not committed).
