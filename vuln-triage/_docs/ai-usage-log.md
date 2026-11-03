# AI usage log

Append-only record of AI-assisted work, kept for rubric criteria 2
(AI-assisted development workflow) and 13 (security, audit, and DevOps
hardening). Append one entry per task; facts only — never record a review
or verification that did not happen. Where the prompt, model, or
verification is not recorded in the repo, write literally `not recorded`
(for prompt/model) or `none` (for verification/human review) rather than
guessing. Key prompts that define a role, stage, or task are saved verbatim
in `_docs/prompts/` and linked from the entry.

## Entry template

Copy this template for each new entry:

- date:
- task/issue:
- agent role:
- model:
- prompt or instruction given (or link to a file in `_docs/prompts/`):
- files changed:
- verification (tests run, reviewer verdict):
- human review (what I checked or corrected, or `none`):

## Entries

### 2026-10-12 — project setup (commit f2735e9)

- date: 2026-10-12
- task/issue: project setup — instructions, settings, hooks, OpenCode layer
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `AGENTS.md`, `agent-kit.conf`, `Makefile`, `opencode.json`, `.opencode/agents/pm.md`, `.opencode/agents/qa-engineer.md`, `.opencode/agents/software-engineer.md`, `README.md`, `.gitignore`, `.githooks/` (verified via `git show f2735e9 --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — project brief Stage 0 (commit 269d30d)

- date: 2026-10-12
- task/issue: add project brief for VulnTriage (Stage 0)
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `_docs/project-brief.md` (verified via `git show 269d30d --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — independent plan review (commit c631603)

- date: 2026-10-12
- task/issue: independent plan review (verdict FAIL: plan docs missing)
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `_docs/plan-review.md` (verified via `git show c631603 --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — final project rubric (commit 235b9f4)

- date: 2026-10-12
- task/issue: add final project rubric (planning reference, 14 criteria)
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `_docs/rubric.md` (verified via `git show 235b9f4 --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — planning process stages 0-6 (commit 88858aa)

- date: 2026-10-12
- task/issue: add VulnTriage planning process (stages 0-6)
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `_docs/planning-process.md` (verified via `git show 88858aa --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — product spec Stage 1 (commit dafd91e)

- date: 2026-10-12
- task/issue: add VulnTriage product spec (Stage 1: users, stories, non-goals, edge cases)
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `_docs/specs.md` (verified via `git show dafd91e --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — README planning-doc links Stage 1 (commit 59bb33a)

- date: 2026-10-12
- task/issue: link planning docs from README (Stage 1)
- agent role: not recorded
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): not recorded
- files changed: `README.md` (verified via `git show 59bb33a --stat`)
- verification (tests run, reviewer verdict): none
- human review (what I checked or corrected, or `none`): none

### 2026-10-12 — implement groomed issue #1 (evidence logging + rubric evidence auditor)

- date: 2026-10-12
- task/issue: implement groomed issue #1 per `.scratch/issue-1-groomed.md` with human overrides (A) prompts README notes no prompts yet, (B) out-of-scope unlinked
- agent role: Software Engineer
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to implement `.scratch/issue-1-groomed.md` (12 criteria) with overrides; no key prompt file in `_docs/prompts/` (only `README.md`, zero entries)
- files changed: `_docs/ai-usage-log.md`, `_docs/rubric-evidence.md`, `_docs/ai-usage-report.md`, `_docs/prompts/README.md`, `README.md` (link lines only), `AGENTS.md` (two rule sentences only, uncommitted pending approval), `.opencode/agents/pm.md`, `.opencode/agents/software-engineer.md`, `.opencode/agents/qa-engineer.md` (DoD line only, uncommitted pending approval), `.opencode/agents/rubric-auditor.md` (new, uncommitted pending approval), `.agents/skills/update-rubric-evidence/SKILL.md` (new)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD as no code exists; whitespace PASS; no test files changed); `.scratch/check_issue1.py` run — all substantive checks pass (two check-script strictness notes: C8 counts 8 TODOs including intro line; C11 lists untracked dirs `.agents/` and `_docs/prompts/` instead of expanded files)
- human review (what I checked or corrected, or `none`): none

### 2026-10-13 — update token permissions and post issue #1 comments

- date: 2026-10-13
- task/issue: apply human-approved protected changes for new GitHub token permissions; post PM/Engineer/QA comments on issue #1
- agent role: Orchestrator
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): human instruction in-session (new token: read-only code, read/write issues; three AGENTS.md/opencode.json edits enumerated verbatim; post the four drafted comments; ask before closing #1); no key prompt file in `_docs/prompts/`
- files changed: `AGENTS.md` (Environment line rewritten; untrusted-issue-text rule added), `opencode.json` (gh issue comment allow; close/create/edit ask; delete deny; api ask) — committed as c22a657 with HUMAN_APPROVED=1 after human approval of the exact diff
- verification (tests run, reviewer verdict): `git diff --check` clean; exact diff shown to human before commit; four comments posted (ids 6136675116, 6136679351, 6136682287, 6136689656)
- human review (what I checked or corrected, or `none`): human authored and approved the changes; flagged pre-existing working-tree extras in the same diff (one-command bullet in AGENTS.md, tool-added opencode.json allow rules) as included-but-not-new

### 2026-10-16 — install Claude Code layer alongside OpenCode

- date: 2026-10-16
- task/issue: install the agent kit's Claude Code layer (`_docs/agent-kit/claude-code/START.md`, steps 2-5) without clashing with the OpenCode layer; Claude Code is to supervise/review OpenCode's work
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): human instruction in-session ("help me set up the claude code layer. make sure it does not clash with opencode. I will use claude code to supervise/review the work opencode has done."); no key prompt file in `_docs/prompts/`
- files changed: `CLAUDE.md` (new, from template), `.claude/agents/pm.md`, `.claude/agents/software-engineer.md`, `.claude/agents/qa-engineer.md` (new, from kit plus the project's ai-usage-log DoD line), `.claude/agents/rubric-auditor.md` (new, port of `.opencode/agents/rubric-auditor.md`), `.claude/settings.json` (new, kit settings; ask list matched to PROTECTED plus Makefile; gh issue view/list allowed; gh issue delete denied), `agent-kit.conf` (PROTECTED adds `CLAUDE.md`, `.claude/*`), `opencode.json` (edit ask for `CLAUDE.md`, `.claude/*`; also commits the human's pending `gh issue create*` ask→allow change), `_session-summaries/planning-2026-10-16-claude-code-layer.md`
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: no code exists; whitespace PASS; no test files changed). START.md step 6 checks (`/agents`, `/hooks`, `/permissions`, guard test) not yet run: they need a Claude Code restart
- human review (what I checked or corrected, or `none`): human approved the protected edits to `agent-kit.conf` and `opencode.json` and chose to include the pending opencode.json change in this commit

### 2026-10-16 — independent plan review of Stage 1 (at 27d4760)

- date: 2026-10-16
- task/issue: independent review of the planning documents written so far (brief, rubric, planning process, `_docs/specs.md`); Stages 2-6 not yet written
- agent role: Reviewer (Claude Code, independent of the OpenCode planning agent)
- model: claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): human-pasted reviewer prompt in-session (find errors, gaps, scope, checkability, unmarked external API facts, feasibility, security; write only the review and this log entry); not saved to `_docs/prompts/` because the instruction limited the files written (raised as a question in the review)
- files changed: `_docs/reviews/2026-10-16-plan-review.md` (new), `_docs/ai-usage-log.md` (this entry)
- verification (tests run, reviewer verdict): reviewer verdict FAIL (2 High, 10 Medium, 6 Low findings; 6 questions for the human); `make verify` run before commit
- human review (what I checked or corrected, or `none`): none

### 2026-10-16 — turn plan review findings into GitHub issues

- date: 2026-10-16
- task/issue: convert `_docs/reviews/2026-10-16-plan-review.md` (ba39c5c) into GitHub issues #3-#9; record the human's decisions on the review questions
- agent role: Reviewer (Claude Code)
- model: claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): human-pasted instruction in-session (one issue per High finding, Medium/Low grouped by topic in at most 5 issues, a carry-forward issue for later stages, task-template bodies, VERIFY: on feed assumptions, show titles before creating), then approval with changes (coverage check, Depends-on lines, recorded decisions); not saved as a key prompt (task instruction, not a role or stage definition)
- files changed: `_docs/plan-review.md` renamed to `_docs/plan-review-2026-10-12-superseded.md` with a superseded first line (human decision); `_docs/prompts/reviewer-plan-review.md` (new, Reviewer prompt verbatim, human decision); `_docs/prompts/README.md` (index row); `_docs/ai-usage-log.md` (this entry)
- GitHub issues created: #3 finding 1 (fixed version), #4 finding 2 (CVE aliases), #5 findings 4/7/8/9 (feeds and ingestion), #6 findings 3/10/13/16/17 (status and audit; depends on #3), #7 findings 5/6/15 (notifications; decisions on issue destination and issue-close sync), #8 findings 11/14 (security boundaries; depends on #7), #9 carry into later stages (findings 1, 2, 4, 11, 12, 15, 18 by stage; cloud hosting decision open). Coverage checked: findings 1-18 each appear in at least one issue; split findings (1, 2, 4, 11, 15) say which part each issue handles
- human decisions recorded: specs.md is a draft until the review issues are resolved (in #3); cloud hosting target left open (in #9)
- verification (tests run, reviewer verdict): issue numbers checked against each `gh issue create` result before cross-references were written; `make verify` run before commit; issue links point at ba39c5c, which resolve only after the human pushes
- human review (what I checked or corrected, or `none`): human approved the issue titles and grouping and asked for the coverage check, Depends-on lines and recorded decisions before creation

### 2026-10-16 — QA re-check of issue #1 at ba39c5c (fresh PASS)

- date: 2026-10-16
- task/issue: issue #1 — fresh full QA check at current HEAD ba39c5c (prior PASS at 0b2a18f was stale after e496aa5, c22a657, 3f6a919, 27d4760, ba39c5c)
- agent role: QA Engineer (subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to perform a fresh full QA check at current HEAD per `_docs/agent-kit/team/qa-engineer.md`; no key prompt file in `_docs/prompts/`
- files changed: none (QA changed nothing; `.scratch/` left empty)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed); verdict QA PASS — all 11 criteria PASS at ba39c5c; E2E not applicable (`none` in AGENTS.md, docs-only change); `make assert-clean` PASS and HEAD unmoved (ba39c5c) confirmed by Orchestrator; verdict posted as issue comment 6217664490
- human review (what I checked or corrected, or `none`): none

### 2026-10-16 — PM files follow-up issue #2 (role log-entry contradiction)

- date: 2026-10-16
- task/issue: file approved follow-up for the QA-flagged risk that PM/QA role files contradict themselves (write-only-.scratch/ vs append to `_docs/ai-usage-log.md`); the 3 earlier-drafted follow-ups (prompts index, first audit, report content) stay deferred per human decision
- agent role: PM (Product Manager subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction citing the human's decision-point approval to file exactly one follow-up; no key prompt file in `_docs/prompts/`
- files changed: none in working tree (body drafted in `.scratch/followup-pm-qa-log-body.md`, removed by `make clean-scratch`)
- verification (tests run, reviewer verdict): none (no code changed; new issue #2 returned with URL https://github.com/andrew-chung-au/vuln-triage/issues/2)
- human review (what I checked or corrected, or `none`): human approved filing this follow-up and deferring the other three at the issue #1 decision point

### 2026-10-16 — PM grooms issue #2 (orchestrator-appends rule)

- date: 2026-10-16
- task/issue: issue #2 — groom to task template (Goal + 7 checkable criteria + Out of scope + Constraints); recommend single rule (roles write only to `.scratch/`, orchestrator appends log entry after assert-clean)
- agent role: PM (Product Manager subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to groom #2 per `_docs/agent-kit/team/pm.md` using `_docs/agent-kit/templates/task-template.md`; no key prompt file in `_docs/prompts/`
- files changed: none in working tree (draft in `.scratch/issue-2-groomed.md`, later replaced by `.scratch/issue-2-groomed-v2.md`; both removed by `make clean-scratch`)
- verification (tests run, reviewer verdict): none (no code changed)
- human review (what I checked or corrected, or `none`): human confirmed the orchestrator-appends rule, chose keep-#2-PM/QA-only plus follow-up, and approved updating #2 with the groomed text

### 2026-10-16 — Engineer implements issue #2 (commit 2dcc89d)

- date: 2026-10-16
- task/issue: issue #2 — replace contradicting log line with orchestrator-appends rule in 4 role files
- agent role: Software Engineer (subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to implement groomed #2, leave protected edits uncommitted, run Verify, and return the diff; no key prompt file in `_docs/prompts/`
- files changed: `.opencode/agents/pm.md`, `.opencode/agents/qa-engineer.md`, `.claude/agents/pm.md`, `.claude/agents/qa-engineer.md` (one-line swap each: 4 insertions, 4 deletions; committed as 2dcc89d after human approval with HUMAN_APPROVED=1)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed); `git diff --check` clean; report posted as issue comment 6218874639
- human review (what I checked or corrected, or `none`): human approved this exact diff before the protected commit

### 2026-10-16 — QA checks issue #2 at 2dcc89d (PASS)

- date: 2026-10-16
- task/issue: issue #2 — full QA check of all 7 criteria at commit 2dcc89d
- agent role: QA Engineer (subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to check #2 per `_docs/agent-kit/team/qa-engineer.md` at commit 2dcc89d; no key prompt file in `_docs/prompts/`
- files changed: none (QA changed nothing; `.scratch/` check script and output only, removed by `make clean-scratch`)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: planning phase; whitespace PASS; no test files changed); `make assert-clean` PASS at 2dcc89d; verdict QA PASS — all 7 criteria PASS; E2E not run (`none` in AGENTS.md, no user-facing behaviour); verdict posted as issue comment 6218959705
- human review (what I checked or corrected, or `none`): none

### 2026-10-16 — Orchestrator close-out of issue #2 (follow-up #10, edit, commit, close)

- date: 2026-10-16
- task/issue: issue #2 close-out — file approved follow-up #10, update #2 body to groomed text, commit protected diff, close #2
- agent role: Orchestrator
- model: opencode/muse-spark-1.3-contributor-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): user instruction "work on the next issue and follow process.md"; no key prompt file in `_docs/prompts/`
- files changed: `_docs/ai-usage-log.md` (these entries); `_session-summaries/issue-002-qa-log-rule.md` (new); GitHub: created issue #10 (engineer/auditor log contradiction), edited #2 body to groomed text, posted PM/Engineer/QA relay comments, closed #2
- verification (tests run, reviewer verdict): `make assert-clean` PASS and HEAD unmoved at 2dcc89d confirmed after QA; QA verdict QA PASS at 2dcc89d
- human review (what I checked or corrected, or `none`): human approved the groomed-text edit, the protected commit, and closing #2

### 2026-10-16 — Add `make issue-dump` target and protect the Makefile (commits f999cd6, fc29661)

- date: 2026-10-16
- task/issue: add a Makefile target so fetching a long issue needs no shell redirect or script; add the matching Commands line to `AGENTS.md`; add `Makefile` to the PROTECTED list
- agent role: Orchestrator
- model: opencode/space-bunny-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): user instruction to add the target with the supplied Make recipe and the `Fetch an issue` Commands line, to show both diffs before committing, and to add `Makefile` to PROTECTED; no key prompt file in `_docs/prompts/`
- files changed: `Makefile` (new `# --- Project targets (not from the kit) ---` section with `ISSUE_DIGITS_LEFT` validation and the `issue-dump` target; 13 insertions, commit f999cd6); `AGENTS.md` (`Fetch an issue` Commands line; 1 insertion, commit f999cd6); `agent-kit.conf` (`Makefile` added to PROTECTED; 1 insertion, commit fc29661)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed) over 14 files / 368 insertions vs origin/main; `make issue-dump` with no N exits non-zero with `Usage: make issue-dump N=<issue number>`; `make issue-dump N=11a` exits non-zero with `N must be an issue number`; `make issue-dump N=11` wrote `.scratch/issue-11.json` (10910 bytes) containing body, title, state, labels and comments; `make help` lists `issue-dump`; `git diff --check` clean; recipe lines confirmed as tabs
- human review (what I checked or corrected, or `none`): human approved the Makefile and `AGENTS.md` diffs and the `agent-kit.conf` PROTECTED addition, each committed with `HUMAN_APPROVED=1`; human corrected two facts — `Makefile` was not protected before this entry, and the Makefile had no project section until this change created one

### 2026-10-16 — PM grooms issue #11 (final rubric impact)

- date: 2026-10-16
- task/issue: issue #11 — groom to task template; confront the missing verbatim criteria text; fix stale open-issue range
- agent role: PM (Product Manager subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/space-bunny-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to groom #11 per `_docs/agent-kit/team/pm.md`, with instructions to confront the placeholder text and the stale issue range; no key prompt file in `_docs/prompts/`
- files changed: none in working tree (draft in `.scratch/issue-11-groomed.md`)
- verification (tests run, reviewer verdict): none (no code changed); PM read all five planning documents named in the issue; PM confirmed `_docs/rubric.md` is not in `agent-kit.conf` PROTECTED and that #2 is closed and #10 is open
- human review (what I checked or corrected, or `none`): human supplied the full final Criteria text into the issue's Source section, answering the PM's blocker question; human corrected the PM's read of the source by updating the issue rather than the PM re-grooming it

### 2026-10-16 — Engineer implements issue #11 (commits 0604233, 2cfdf95)

- date: 2026-10-16
- task/issue: issue #11 — replace `_docs/rubric.md` with the final 12 criteria verbatim; write the impact report at `_docs/reviews/2026-10-16-final-rubric-impact.md`
- agent role: Software Engineer (subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: opencode/space-bunny-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to implement #11 from the filed body as amended by the PM comment, with an explicit state check that the interrupted prior run had committed nothing; no key prompt file in `_docs/prompts/`
- files changed: `_docs/rubric.md` (78 insertions, 36 deletions, commit 0604233); `_docs/reviews/2026-10-16-final-rubric-impact.md` (570 insertions, new, commit 2cfdf95); no PROTECTED path touched
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed); `git diff --check` clean; Engineer reported a scripted byte comparison of `_docs/rubric.md` line 2 onward against the criteria text in the issue Source section; counted 12 criteria, max points summing 24, "You need 10 points to pass". Not yet QA'd
- human review (what I checked or corrected, or `none`): human paused the session before QA, having uncommitted their own `AGENTS.md` and `opencode.json` changes; human also stopped the `.scratch/` script approach for GitHub issue data after the PM wrote `dump_issue11.py` and `extract_source.py` in place of `gh --json`/`--jq`, which was a process deviation caused by the orchestrator's role prompts

### 2026-10-17 — Orchestrator resumes issue #11: Engineer handover comment, model record

- date: 2026-10-17
- task/issue: issue #11 — pick up after the pause; post the Engineer handover; record which tool and model built #11
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human handover prompt (read the issue, latest summary, git state, then stop) and human instruction to run step 1, name the tool/model that built #11, record the model change, run QA in a different tool, and not close #11; no key prompt file in `_docs/prompts/`
- files changed: `_docs/ai-usage-log.md` (these entries); GitHub: posted Engineer handover comment 6227197431 on #11
- tool and model history for #11 (as far as the record shows): all #11 work recorded was done in OpenCode, none in Claude Code. The human states the model changed during #11 from Muse Spark 1.3 (`opencode/muse-spark-1.3-contributor-free`) to Space Bunny (`opencode/space-bunny-free`). Filing #11: not recorded. PM grooming: Space Bunny. First Engineer launch (interrupted, no commits): not recorded. Engineer commits 0604233 and 2cfdf95: Space Bunny. Orchestrator entries and summary (ad04f59): not recorded. Muse Spark 1.3's part in #11: not recorded. The human's commit c8dea47 pinned Muse Spark 1.3 in `opencode.json` after the Engineer work
- verification (tests run, reviewer verdict): `make assert-clean` PASS at c8dea47 before QA; `make verify` PASS WITH WARNINGS at c8dea47 (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed)
- human review (what I checked or corrected, or `none`): human confirmed the Orchestrator role for #11 and required QA in a tool other than the one that built it (OpenCode built it, so QA ran in Claude Code)

### 2026-10-17 — QA checks issue #11 at c8dea47 (PASS)

- date: 2026-10-17
- task/issue: issue #11 — full QA check against the filed body as amended by PM comment 6226692732, at commit c8dea47 (Engineer commits 0604233, 2cfdf95)
- agent role: QA Engineer (Claude Code subagent; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: claude-opus-5-5 (Claude Code; the qa-engineer agent sets no model, so it inherits the main session's)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to check #11 per `_docs/agent-kit/team/qa-engineer.md` at c8dea47, carrying the AGENTS.md rule on GitHub issue data; no key prompt file in `_docs/prompts/`
- files changed: none (QA wrote only to `.scratch/`: `qa11_check.py`, `qa-11-comment.md`)
- verification (tests run, reviewer verdict): verdict QA PASS, all criteria PASS, posted as issue comment 6227226075; QA ran `make verify` (PASS WITH WARNINGS, no TEST_CMD) and one `.scratch/` analysis script (byte comparison of `_docs/rubric.md` against the issue Source section and count checks). Orchestrator then ran `make assert-clean` PASS and confirmed HEAD unmoved at c8dea47. QA reported 8 risks outside the criteria (in the comment), none changing the verdict
- human review (what I checked or corrected, or `none`): none yet; human to read the report and record decisions on the two Decision needed items before #11 is closed

### 2026-10-17 — Engineer corrects #11 report for QA risks (commit ed05530)

- date: 2026-10-17
- task/issue: issue #11 follow-up — fix the six QA risks in `_docs/reviews/2026-10-16-final-rubric-impact.md` (US-12 before/after, E6 row, brief line number, #8 criteria count, §1 Totals deployment claim, GitHub Actions Docker VERIFY: tag, §9 counts) and add the source URL and a final newline to `_docs/rubric.md`
- agent role: Software Engineer (Claude Code subagent; entry appended by Orchestrator)
- model: claude-opus-5-5 (Claude Code). Ran in Claude Code, not OpenCode, because OpenCode was unavailable; the human asked for this
- prompt or instruction given (or link to a file in `_docs/prompts/`): human instruction listing the corrections, relayed by the Orchestrator; source URL supplied by the human (https://github.com/DataTalksClub/ai-dev-tools-zoomcamp/blob/main/project/README.md); no key prompt file in `_docs/prompts/`
- files changed: `_docs/reviews/2026-10-16-final-rubric-impact.md`, `_docs/rubric.md` (43 insertions, 22 deletions, commit ed05530); Engineer comment 6227407227 on #11
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (no TEST_CMD: planning phase, no code exists; whitespace PASS; no test files changed); Orchestrator `make assert-clean` PASS at ed05530 before QA
- human review (what I checked or corrected, or `none`): human supplied the source URL; the finalised date 2026-10-17 on rubric line 1 is left for the human to check against the live page

### 2026-10-17 — QA targeted re-check of #11 corrections at ed05530 (PASS)

- date: 2026-10-17
- task/issue: issue #11 — targeted re-check of the seven correction points only (six report points, rubric line 1 and final newline, scope)
- agent role: QA Engineer (fresh Claude Code subagent, separate from the Engineer's context; entry appended by Orchestrator per the write-only-.scratch/ role limit)
- model: claude-opus-5-5 (Claude Code). Ran in Claude Code, not OpenCode, because OpenCode was unavailable; the human asked for this. Engineer and QA ran in the same tool and model this time, as separate subagents
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to re-check the listed points against the files and `gh`, not the Engineer's comment; no key prompt file in `_docs/prompts/`
- files changed: none (QA wrote only to `.scratch/`: `qa11_recheck.py`, `qa11-recheck-comment.md`)
- verification (tests run, reviewer verdict): verdict QA PASS, all seven points PASS, posted as comment 6227431094; QA ran `make verify` (PASS WITH WARNINGS, no TEST_CMD) and one `.scratch/` script (byte comparison of the US-12 BEFORE block against `_docs/specs.md` lines 90-96 and of rubric lines 2 onward against e0a2470). Orchestrator then ran `make assert-clean` PASS, HEAD unmoved at ed05530. QA reported 4 risks outside these points, none changing the verdict
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-17 — Orchestrator relays #11 decisions and applies brief change (commit 111b001)

- date: 2026-10-17
- task/issue: issue #11 decision point — post the human's decisions; apply the approved `_docs/project-brief.md` change from report §7.1
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human decisions of 2026-10-17 (target 24/24 built as Tier A/B/C milestones; all no-longer-scored items kept; scoring path first, then LLM brief, MCP server and n8n; US-12 keeps all three acceptance criteria) and human approval of §7.1 1b plus a CI/CD sentence of the human's wording; no key prompt file in `_docs/prompts/`
- files changed: `_docs/project-brief.md` (workflow step 8 "Watch and respond"; Fixed stack CI/CD item expanded to PR tests, auto deploy to dev, manual promotion of the same image to production; 7 insertions, 2 deletions, commit 111b001 with HUMAN_APPROVED=1); GitHub: posted the human's decisions verbatim as relayed Orchestrator comment 6228520087 on #11
- verification (tests run, reviewer verdict): `git diff --check` clean; final diff shown to the human
- human review (what I checked or corrected, or `none`): human rejected §7.1 1a (MCP server out of the MVP), approved 1b as written, and supplied the CI/CD sentence; human chose to apply all §7 changes before cleanup and closing #11

### 2026-10-17 — Orchestrator applies approved spec and brief changes (commits 701951d, 16e1ec0, b8792b3)

- date: 2026-10-17
- task/issue: issue #11 decision point — apply the approved `_docs/specs.md` changes from report §7.2 and a further brief change; relay the human's hosting decision to #9
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human decisions on §7.2 (reject 2a; accept US-13 and US-14; replace US-15 with the human's text; accept E6 naming Grafana), human edits (Grafana in US-13; US-15 via pull request, CI deploys to dev; open question 5 on the responder's credential and merge; shorten "fixes it with a test"), human's observability-stack sentence for the brief, and the human's hosting decision text for #9; no key prompt file in `_docs/prompts/`
- files changed: `_docs/specs.md` (US-13, US-14, US-15, edge case E6, open questions 4 and 5; 32 insertions, commit 701951d; one-line US-15 follow-up, commit 16e1ec0); `_docs/project-brief.md` (Fixed stack adds OpenTelemetry Collector, Prometheus, Loki, Tempo and Grafana; 3 insertions, 1 deletion, commit b8792b3); all three commits with HUMAN_APPROVED=1. GitHub: posted the human's hosting decision verbatim as relayed Orchestrator comment 6229681999 on #9. `opencode.json` (human's own uncommitted change) left out of all commits at the human's instruction
- verification (tests run, reviewer verdict): `git diff --check` clean before each commit; final diffs shown to the human before each commit (spec diff shown before the last two human edits, which were applied as instructed)
- human review (what I checked or corrected, or `none`): human rejected §7.2 2a (US-12 stays with all three acceptance clauses), rewrote US-15, named Grafana, added open question 5; Orchestrator numbered the US-14 window question 4 because question 3 already existed

### 2026-10-17 — AGENTS.md Layout and "Where to read more" (commit 4075318); issue #12 filed

- date: 2026-10-17
- task/issue: issue #11 decision point — apply report §7.0 to `AGENTS.md`; file the follow-up issue for `_docs/agent-team.md`
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human chose the Orchestrator's revised version of §7.0 (stale Layout fixed, Claude Code layer named, spec and brief added, `_docs/agent-team.md` left out until written) with the human's "when to read" wording for the spec, process and procedures entries; human asked for an issue to write `_docs/agent-team.md`; no key prompt file in `_docs/prompts/`
- files changed: `AGENTS.md` (Layout line updated; "Where to read more" list added; 13 insertions, 1 deletion; drafted by the Orchestrator, diff shown to the human, committed by the human as 4075318 with HUMAN_APPROVED=1). GitHub: filed issue #12 (Write `_docs/agent-team.md` for the Agent Team Specification criterion), not yet groomed by the PM
- verification (tests run, reviewer verdict): every path in the list checked to exist with `ls` before proposing; final diff shown to the human before commit
- human review (what I checked or corrected, or `none`): human chose option (a) with edits and ran the commit; the same-tool QA exception in #12's body is the Orchestrator's wording, flagged to the human for correction

### 2026-10-17 — Planning process and README updated for the final rubric (§7.3)

- date: 2026-10-17
- task/issue: issue #11 decision point — apply report §7.3, adjusted to the human's decisions, to `_docs/planning-process.md`; link the impact report from `README.md`
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator's adjusted §7.3 proposal (items 1-4), accepted by the human with additions: Stage 3 file `_docs/api.md` and CI export of the generated OpenAPI document; Docker-capable dev environment and cost controls with teardown in the Stage 2 deployment bullet; deliberate, documented, removable responder defect in Stage 4; Stage 2 checklist line and component list; Stage 6 Reviewer reading list as a statement; no key prompt file in `_docs/prompts/`
- files changed: `_docs/planning-process.md` (Stage 2 components, observability and deployment bullets, checklist; Stage 3 API design; Stage 4 telemetry, alerting, responder and CI security scan; Stage 5 milestones; Stage 6 12 criteria and Reviewer list), `README.md` (impact report link); committed together (not protected). `opencode.json` and `.claude/settings.json` (changed outside this work, not read) left out of the commit
- verification (tests run, reviewer verdict): `git diff --check` clean; diff shown to the human before the final three additions, which were applied as instructed
- human review (what I checked or corrected, or `none`): human accepted items 1-4 and supplied the additions above; human dropped nothing

### 2026-10-17 — AI usage report header updated (§7.5, commit a535ff7)

- date: 2026-10-17
- task/issue: issue #11 decision point — apply report §7.5 to `_docs/ai-usage-report.md`
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human accepted the proposed header (not a scored criterion; kept for portfolio value and as supporting evidence) and the Orchestrator's change to section 2 (summarise and link `_docs/agent-team.md`, issue #12); no key prompt file in `_docs/prompts/`
- files changed: `_docs/ai-usage-report.md` (6 insertions, 4 deletions, commit a535ff7; not protected)
- verification (tests run, reviewer verdict): `git diff --check` clean
- human review (what I checked or corrected, or `none`): human approved both changes before they were made

### 2026-10-17 — Rubric Evidence Auditor regenerates rubric evidence for the 12 final criteria (§7.4, commit ad5b27d)

- date: 2026-10-17
- task/issue: issue #11 decision point — regenerate `_docs/rubric-evidence.md` for the final rubric (report §7.4)
- agent role: Rubric Evidence Auditor (Claude Code subagent; entry appended by Orchestrator, since the Orchestrator limited the auditor to editing `_docs/rubric-evidence.md` only)
- model: claude-opus-5-5 (Claude Code). Ran in Claude Code, not OpenCode, because OpenCode was unavailable; the human asked for this. An OpenCode re-audit is planned after Stage 2
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction per the human's spec for the table (criterion, max points, full-marks condition quoted from `_docs/rubric.md`, status, evidence, gap), evidence only from what exists now, §7.4 mapping as a cross-check only; no key prompt file in `_docs/prompts/`
- files changed: `_docs/rubric-evidence.md` (12-row table, header with audit date and commit; 43 insertions, 21 deletions; committed by the Orchestrator as ad5b27d)
- verification (tests run, reviewer verdict): audited at a535ff7; 7 of 24 points evidenced (Problem Description PARTIAL 1; Product Specification, Agent Team Specification, Context Management MET 2 each; the other 8 MISSING). Auditor ran `make verify` (PASS WITH WARNINGS, no TEST_CMD) and opened the GitHub evidence with `gh --json/--jq`; no `.scratch/` scripts. Orchestrator checked `git status` showed only that file changed
- human review (what I checked or corrected, or `none`): none yet. Auditor findings for the human: the #11 commits are not pushed, so the public repo (at bd616a5) lacks the evidence for criteria 2-4; `.claude/agents/rubric-auditor.md` still says "14 criteria" and tells the auditor to append to the log (the #10 contradiction); a stray tracked `test.md` at the repo root; the local `origin/main` ref is stale (27d4760 vs remote bd616a5)

### 2026-10-17 — Orchestrator close-out of issue #11

- date: 2026-10-17
- task/issue: issue #11 close-out — clean scratch, session summary, close; plus human-requested housekeeping (fetch, remove `test.md`, #10 scope note, new README issue)
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human instruction to close #11 once `make assert-clean` passes, with an Orchestrator comment linking the decisions comment, and four extra items; no key prompt file in `_docs/prompts/`
- files changed: `_session-summaries/issue-011-final-rubric-impact.md` (updated, commit d013f00); `test.md` removed (0554a9f, human-approved). GitHub: comment 6230949666 on #10 (both rubric-auditor files: 12 criteria, same log-entry rule); filed #13 (README: Problem Description 1 → 2 points); closing Orchestrator comment on #11 linking decisions comment 6228520087; #11 closed. Local `origin/main` refreshed with `git fetch` (27d4760 → bd616a5); nothing pushed
- verification (tests run, reviewer verdict): `make assert-clean` PASS at d7f69a9 before close-out; `make clean-scratch` ran; QA PASS at c8dea47 and targeted re-check PASS at ed05530 stand
- human review (what I checked or corrected, or `none`): human committed their own `opencode.json` fix (d7f69a9) to unblock assert-clean and approved deleting `test.md`

### 2026-10-17 — Engineer implements issue #14 stages A and B (commits 7c12cd4, 6327f01)

- date: 2026-10-17
- task/issue: issue #14 stages A (Stage 3 process change) and B (DRAFT Lovable prompt) only, per PM grooming comment 6231923268
- agent role: Software Engineer (Claude Code subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to implement stages A and B as groomed, not C, D or E; no prompts index row (stage C); no key prompt file saved
- files changed: `_docs/planning-process.md` (§ Stage 3, one sentence, 3 lines added; 7c12cd4); `_docs/prompts/lovable-frontend.md` (new, Status: DRAFT, prompt 605 words; 6327f01). GitHub: Engineer comment 6232712832 on #14
- verification (tests run, reviewer verdict): `make verify BASE=ee0fcfe` PASS WITH WARNINGS (only warning: no TEST_CMD, no code exists); `.scratch/` check of the stage B criteria, including the secrets scan and its refused-case fixture, all PASS. QA not yet run
- human review (what I checked or corrected, or `none`): none yet; the draft awaits the human's approval (stage C)

### 2026-10-17 — Engineer revises the issue #14 Lovable prompt for Decision 3 (commit 2cbffa9)

- date: 2026-10-17
- task/issue: issue #14 stage B revision, applying the human's Decision 3 (build v1 now as discovery; richer model where unsure)
- agent role: Software Engineer (Claude Code subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction quoting Decision 3 verbatim; no key prompt file saved
- files changed: `_docs/prompts/lovable-frontend.md` (still Status: DRAFT; header adds the discovery-build line, #3 ASSUMPTION now fixed versions per affected range with a "no fixed version" state, #6 ASSUMPTION now open / risk accepted / fixed / withdrawn with sources; prompt updates dashboard, detail, mock data and tests; prompt 698 words; 2cbffa9)
- verification (tests run, reviewer verdict): `make verify BASE=ee0fcfe` PASS WITH WARNINGS (only warning: no TEST_CMD, no code exists); updated `.scratch/check_issue14_b.py` (Decision 3 checks added) all PASS. QA not yet run
- human review (what I checked or corrected, or `none`): none yet; the draft awaits the human's approval (stage C)

### 2026-10-17 — Orchestrator runs issue #14 grooming and decisions; applies Decision 1 (commits f6add8a, 79b43e4)

- date: 2026-10-17
- task/issue: issue #14 (human chose it as next); PM grooming, Engineer stages A and B, human's Decisions 1-3; follow-up #15 filed
- agent role: Orchestrator (Claude Code main session), launching PM and Engineer subagents
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): human: "work on the next issue and follow process.md", then chose #14; Decisions 1-3 and notes given in session (quoted in PM comment 6232771876 on #14)
- files changed: `AGENTS.md` (protected, HUMAN_APPROVED=1; one line allowing a mocked frontend prototype in `frontend/` during planning; f6add8a); `_docs/planning-process.md` (same line, same wording; 79b43e4). GitHub, by PM subagent: grooming comment 6231923268 and approval request 6232722317 and decisions comment 6232771876 on #14; comment 6232771639 on #6; filed #15 (stages D-E)
- verification (tests run, reviewer verdict): human reviewed both diffs before they were applied; QA of stages A and B not yet run (human to run it in a fresh OpenCode session, per the #11 rule that QA doesn't run in the tool that built the work)
- human review (what I checked or corrected, or `none`): human approved Decision 1 wording and both diffs; accepted the Engineer's three choices (no "stale" status, dashboard status filter, a mock finding with no aliases); prompt approval to follow separately

### 2026-10-17 — Engineer applies the human's three edits to the issue #14 Lovable prompt (commit 67322c9)

- date: 2026-10-17
- task/issue: issue #14 stage B revision, the human's three edits before prompt approval (services-layer order with no re-sort and pre-ranked mock data; React with TypeScript and `npm test`; demo credentials on the login screen)
- agent role: Software Engineer (Claude Code subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction quoting the human's three edits verbatim; no key prompt file saved
- files changed: `_docs/prompts/lovable-frontend.md` (still Status: DRAFT; screen 2 and first test use the human's wording; mock data pre-ranked by the `_docs/planning-process.md` § Stage 2 tie-breaks; Stage 2 header ASSUMPTION updated, including criticality higher first and missing EPSS last, which Stage 2 does not state; prompt 774 words, up from 698, all from these edits; 67322c9). GitHub: Engineer comment 6232991787 on #14
- verification (tests run, reviewer verdict): `make verify BASE=ee0fcfe` PASS WITH WARNINGS (only warning: no TEST_CMD, no code exists); updated `.scratch/check_issue14_b.py` (word limit is 698 plus the net words of these edits; new-text checks) all PASS. QA not yet run
- human review (what I checked or corrected, or `none`): none yet; the revised draft awaits QA and the human's approval

### 2026-10-17 — Engineer corrects the record for the issue #14 prompt edits (commit 67322c9)

- date: 2026-10-17
- task/issue: issue #14, fix for QA FAIL comment 6233025035 (record correction only)
- agent role: Software Engineer (Claude Code subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to correct the record after QA FAIL 6233025035, with the human's decision recorded in Orchestrator comment 6233052344; no key prompt file saved
- correction: the previous entry (commit 67322c9) and Engineer comment 6232991787 said all 76 added words (698 to 774) came from the human's three edits. That was inaccurate. 12 of the 76 words were the Engineer's own sentence, added after the human's demo-credentials line: "They are fictional; if the username is an email, it uses example.com." QA FAIL comment 6233025035 found this. The human accepted the sentence as part of edit 3 and waived the 700-word limit for this prompt, so 774 words stands (Orchestrator comment 6233052344)
- files changed: `_docs/ai-usage-log.md` (this entry only; the earlier entry is left as written). `_docs/prompts/lovable-frontend.md` not changed. GitHub: new Engineer comment on #14 with the same correction
- verification (tests run, reviewer verdict): `make verify BASE=ee0fcfe` run after this commit; result reported in the Engineer comment on #14. QA not yet re-run
- human review (what I checked or corrected, or `none`): the human decided to accept the sentence and waive the word limit (comment 6233052344); this entry itself not yet reviewed

### 2026-10-17 — Engineer marks the issue #14 Lovable prompt APPROVED and indexes it (commit efa250d)

- date: 2026-10-17
- task/issue: issue #14 stage C (approval and index entry)
- agent role: Software Engineer (Claude Code subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction quoting the human's approval given in session: "I looked at the prompt and approve it, date approval today." Prompt file: `_docs/prompts/lovable-frontend.md`
- files changed: `_docs/prompts/lovable-frontend.md` (line 1 only, `Status: DRAFT` to `Status: APPROVED (human, 2026-10-17)`); `_docs/prompts/README.md` (one index row; "where executed" says Lovable, run by the human, not yet run, since the build is in #15 per Decision 2); efa250d, an amend of unpushed 7ba1140 that corrected the row's issue number from "stage D of #14" to #15. GitHub: Engineer comment on #14
- verification (tests run, reviewer verdict): `make verify BASE=ee0fcfe` PASS WITH WARNINGS (only warning: no TEST_CMD, no code exists); `git diff --stat` showed 2 files, 2 insertions, 1 deletion; `git log --follow` on the prompt lists 6327f01, 2cbffa9, 67322c9, 7ba1140 (re-run after the amend gives efa250d in its place). Decision 3 (approve before #3, #4, #6) was answered by the human, as recorded in PM comment 6232771876. QA of stage C not yet run
- human review (what I checked or corrected, or `none`): the human approved the prompt text; this commit not yet reviewed

### 2026-10-17 — PM re-grooms issue #15 for the Bolt build; issue parked

- date: 2026-10-17
- task/issue: issue #15, lifecycle step 2 (grooming), after the human's commit fea6fb7 added a Bolt-built frontend in `frontend-bolt/`
- agent role: PM (Claude Code subagent), launched by the Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to re-groom #15 for the Bolt build, read-only on `frontend-bolt/`, no npm runs; no key prompt file saved
- files changed: none in the repo (drafts in `.scratch/` only). GitHub: PM comments 6234073282 (re-grooming, three decision questions) and 6234079369 (marks Bolt as settled, quoting the human); Orchestrator comment 6234114564 (the human's answers; issue parked)
- verification (tests run, reviewer verdict): none; the PM read `frontend-bolt/` and grepped it, with nothing run or installed. Issue body not edited
- human review (what I checked or corrected, or `none`): the human explained the switch to Bolt ("I tried to build in lovable but hit a credit limit. I tried the same prompt in Bolt..."), confirmed the prompt was pasted verbatim with no follow-ups, kept `.bolt/` for now, and deferred the other decisions until the Lovable credits reset

### 2026-10-17 — PM grooms issue #12 (agent-team document)

- date: 2026-10-17
- task/issue: issue #12, lifecycle step 2 (grooming)
- agent role: PM (Claude Code subagent), launched by the Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to groom #12 per `task-template.md`; no key prompt file saved
- files changed: none in the repo. GitHub: PM comments 6234146060 (proposed body, two decision questions) and 6234208915 (the human's answers). The issue body was replaced with the groomed body (`gh issue edit 12`): the tool blocked the PM's run, and the Orchestrator ran the command after the human typed it in session
- verification (tests run, reviewer verdict): body length checked after the edit (9086 characters, against 1581 before)
- human review (what I checked or corrected, or `none`): the human chose option 1 for both decisions (the PM's wording for the QA same-tool exception; intent plus record for tool and model)

### 2026-10-17 — Engineer implements issue #12 (commit ede47bf)

- date: 2026-10-17
- task/issue: issue #12, lifecycle step 3: write `_docs/agent-team.md` and link it from `README.md`; propose the `AGENTS.md` line
- agent role: Software Engineer (Claude Code subagent, launched by the Orchestrator; entry appended by the Engineer, as its role file says while #10 is open)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to implement the groomed #12 body with the human's answers in PM comment 6234208915 (option 1 for both decisions), base ccd13b6, and to return the `AGENTS.md` diff for approval rather than commit it; no key prompt file saved
- files changed: `_docs/agent-team.md` (new), `README.md` (one link line); 116 insertions, commit ede47bf. `AGENTS.md` not edited; the one-line diff is proposed in Engineer comment 6234459590 on #12
- verification (tests run, reviewer verdict): `make verify BASE=ccd13b6` PASS WITH WARNINGS (only warning: no TEST_CMD, no code exists; whitespace PASS; no test files changed); `.scratch/check_issue12.py` (relative links and anchors, 15 commits via `git cat-file -e`, cited issues and comment ids via `gh issue view --json`, verbatim exception and intent text, model ids, refused cases) PASS. QA not yet run
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — Orchestrator commits the approved AGENTS.md line for issue #12 (commit 948e332)

- date: 2026-10-18
- task/issue: issue #12, protected-file change
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's in-session answer "Approve as written" to the line proposed in Engineer comment 6234459590; no key prompt file saved
- files changed: `AGENTS.md` (one line in "Where to read more"), committed on its own with `HUMAN_APPROVED=1` as 948e332. GitHub: Orchestrator comment 6243691600 records the approval and the human's choice of QA tool
- verification (tests run, reviewer verdict): `git diff` showed the approved line only; `git diff --check` clean. QA checked it afterwards (next entry)
- human review (what I checked or corrected, or `none`): the human approved the exact line in session

### 2026-10-18 — QA checks issue #12 (PASS at 948e332)

- date: 2026-10-18
- task/issue: issue #12, lifecycle step 4
- agent role: QA Engineer (fresh Claude Code qa-engineer subagent, launched by the Orchestrator; entry appended by the Orchestrator after `make assert-clean`, as the QA role file says)
- model: claude-opus-5-5 (Claude Code). It ran in Claude Code, the same tool as the build, because OpenCode is unavailable and the human chose this (comment 6243691600), under the exception in comment 6234208915
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to check every #12 criterion independently at 948e332, base ccd13b6; no key prompt file saved
- files changed: none in the repo (`.scratch/qa12_check.py`, `.scratch/qa12_hook_test.sh` and `.scratch/qa12-comment.md` only). GitHub: QA comment 6243727864
- verification (tests run, reviewer verdict): QA PASS, all 21 criteria. `make verify BASE=ccd13b6` PASS WITH WARNINGS (only warning: no TEST_CMD); QA's own link, commit, issue, quote and refused-case checks; a hook test in a throwaway repo under `.scratch/` (unapproved `AGENTS.md` staging refused, `HUMAN_APPROVED=1` allowed). The guard hook blocked one `git config core.hooksPath`; QA re-ran it as `git config --get core.hooksPath` (result `.githooks`). After QA, `make assert-clean` PASS and HEAD unchanged at 948e332
- human review (what I checked or corrected, or `none`): none yet; QA's risks go to the human at the decision point

### 2026-10-18 — Engineer fixes `_docs/agent-team.md` after the #12 decision point (commit 32ed2a3)

- date: 2026-10-18
- task/issue: issue #12, lifecycle step 7 back to step 3: apply the human's decision-point answers (Orchestrator comment 6243801494) to `_docs/agent-team.md`
- agent role: Software Engineer (Claude Code subagent, launched by the Orchestrator; entry appended by the Engineer, as its role file says while #10 is open)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction listing the human's four decisions (role "not recorded" where the log says so; `CLAUDE.md` claims match `6541893`; add the #12 Engineer and QA runs, QA under the same-tool exception; settings text consistent with the new `AGENTS.md` rule) and "Don't change anything else"; no key prompt file saved
- files changed: `_docs/agent-team.md` (history table gains a "not recorded" role row for the 2026-10-12 entries and `c631603`; #12 Engineer and QA added; third recorded exception use; handover bullets on `CLAUDE.md` and tracked settings files; 10 insertions, 9 deletions, commit 32ed2a3). GitHub: Engineer comment 6243814434 on #12
- verification (tests run, reviewer verdict): `make verify BASE=ccd13b6` PASS WITH WARNINGS (only warning: no TEST_CMD, no code exists; whitespace PASS; no test files changed); `git diff --check` clean. QA re-check not yet run
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — Orchestrator commits the approved settings and scratchpad change at the issue #12 decision point (commit 6541893)

- date: 2026-10-18
- task/issue: issue #12, lifecycle step 7 (decision point), protected-file change
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's in-session answers, recorded in Orchestrator comment 6243801494: the tracked-settings rule in the human's wording (only the missing spaces from line wrapping fixed, and backticks added); the scratchpad line moved from `CLAUDE.md` into `AGENTS.md`; "Approve as shown" for the exact diff
- files changed: `AGENTS.md` (scratch-files line extended; tracked-settings rule added; home-folder and environment-variables rule kept), `CLAUDE.md` (now only `@AGENTS.md`); committed with `HUMAN_APPROVED=1` as 6541893
- verification (tests run, reviewer verdict): `git diff` reviewed against the approved diff; `git diff --check` clean. QA re-check PASS (next entry)
- human review (what I checked or corrected, or `none`): the human approved the exact diff in session

### 2026-10-18 — QA re-checks the issue #12 decision-point changes (PASS at 92d9926)

- date: 2026-10-18
- task/issue: issue #12, lifecycle step 7: QA re-checks only what changed (6541893, 32ed2a3, 92d9926)
- agent role: QA Engineer (fresh Claude Code qa-engineer subagent, launched by the Orchestrator; entry appended by the Orchestrator after `make assert-clean`)
- model: claude-opus-5-5 (Claude Code). It ran in Claude Code, the same tool as the build, because OpenCode is unavailable and the human chose this (comment 6243691600), under the exception in comment 6234208915
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to re-check the three commits against comments 6243801494 and 6243814434, and to re-confirm file scope over ccd13b6..HEAD; no key prompt file saved
- files changed: none in the repo (`.scratch/qa12_recheck.py` and `.scratch/qa12-recheck-comment.md` only). GitHub: QA comment 6243839013
- verification (tests run, reviewer verdict): QA PASS. `python3 .scratch/qa12_recheck.py`: 19 checks, 0 failed. `make verify BASE=ccd13b6` PASS WITH WARNINGS (only warning: no TEST_CMD). Scope note: `CLAUDE.md`, and the second `AGENTS.md` change, fall outside the criterion's file list; both come from the human-approved 6541893. After QA, `make assert-clean` PASS and HEAD unchanged at 92d9926
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — PM files four follow-up issues from #12 (#16 to #19)

- date: 2026-10-18
- task/issue: #12 follow-ups (lifecycle step 7). After #12 closed, the human asked for the QA risks to be filed as future issues. This replaces "none selected" in Orchestrator comment 6243801494 and in the #12 session summary
- agent role: PM (Claude Code subagent, launched by the Orchestrator; entry appended by the Orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to file one ungroomed issue per risk; no key prompt file saved. A first PM run stopped when the session ended, before filing anything (checked: no new issues or comments, clean tree); a fresh PM run did the task
- files changed: none in the repo. GitHub: #16 (agent-team.md history table upkeep), #17 (`_docs/agent-kit/scripts/check-staged.sh` doesn't enforce "committed alone"; a protected path), #18 (record approvals as exact text), #19 (`_docs/ai-usage-report.md` §2 TODO)
- verification (tests run, reviewer verdict): the PM checked open issues #3-#10, #13 and #15 for duplicates and found none. Not groomed yet
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — Orchestrator compares the Bolt and Lovable prototypes (#15)

- date: 2026-10-18
- task/issue: issue #15. The human asked for both prototypes (`frontend-bolt/` at fea6fb7, `frontend-lovable/` at 0dd108a) to be reviewed, one chosen and renamed `frontend/`, and follow-up issues drafted for course steps 3-6
- agent role: Orchestrator (Claude Code main session)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's in-session request; no key prompt file saved
- files changed: `_docs/reviews/2026-10-18-frontend-comparison.md` (51b477a). GitHub: Orchestrator comment 6244151098 on #15 recording the human's four decisions (Lovable chosen; `frontend-bolt/` deleted in its own commit; F0-F6 filed with F4-F6 gated on the phase line; `openapi.yaml` as contract plus a FastAPI conformance test)
- verification (tests run, reviewer verdict): static read only. Node.js and npm are not installed (`node --version`: command not found), so neither app was installed, built or tested. Read-only greps: every email in both `src/` trees uses example.com/.org/.net; network-call grep hits recorded in the review
- human review (what I checked or corrected, or `none`): the human chose the recommended option on all four decisions

### 2026-10-18 — PM re-grooms #15 for Lovable and files #20-#26

- date: 2026-10-18
- task/issue: issue #15 (lifecycle step 2, re-grooming) and follow-ups F0-F6 from the 2026-10-18 frontend comparison
- agent role: PM (Claude Code pm subagent, launched by the Orchestrator; entry appended by the Orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to re-groom #15 per the human's decisions and file F0-F6; the human's stage D values relayed during the run ("build completition date 18-10-2026. total credits used is 6. no follow up prompts used, only the resume function"); no key prompt file saved
- files changed: none in the repo. GitHub: #15 body and title rewritten (stage D run record; stage E split into E1, no Node needed, and E2, after #20), PM comment 6244224555; new issues #20 (dev container Node and uv), #21 (frontend clean-up), #22 (services layer ready for a real API), #23 (API contract), #24 (FastAPI in-memory backend), #25 (connect frontend and backend), #26 (SQLAlchemy persistence). #24-#26 are blocked until the human changes the AGENTS.md "Current phase" line
- verification (tests run, reviewer verdict): none; the issues are not yet implemented
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — Engineer records the frontend runs and moves Lovable to frontend/ (#15 stage D and part E1)

- date: 2026-10-18
- task/issue: issue #15, stage D (run record) and part E1 (move, delete, scan, document). Part E2 not started: Node.js is not installed and E2 waits for #20
- agent role: Software Engineer (Claude Code software-engineer subagent, launched by the Orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to implement #15 stage D and E1 only; no key prompt file saved
- run facts recorded (from the human, relayed by the Orchestrator; the agent never used either tool): the prompt was `_docs/prompts/lovable-frontend.md` `## Prompt`, pasted verbatim into both tools. Lovable first attempt 2026-10-17 stopped at the credit limit. Bolt, 2026-10-17: no follow-up prompts, credits not recorded, project https://bolt.new/~/sb1-fvxy4uq3, committed by the human in fea6fb7 under `frontend-bolt/` (compared, not chosen). Lovable, build completed 2026-10-18: 6 credits in total, no follow-up prompts (continued with Lovable's resume function), project https://lovable.dev/projects/f9cb1f93-46d1-4d9b-baa6-4e09b65a57f3, committed by the human in 0dd108a under `frontend-lovable/` (chosen)
- files changed: b566fb6 (`git mv frontend-lovable frontend`, 94 renames at 100%); cbe2123 (`git rm -r frontend-bolt`, 37 deletions, human-approved decision 2; code stays at fea6fb7); 73a70af (`frontend/.gitignore`: `.env`, `.env.*`, `!.env.example`); 4a9f328 (`_docs/prompts/lovable-frontend.md` run record and follow-ups line, `_docs/prompts/README.md` "Used with" row, `frontend/README.md` Services layer section); this entry. GitHub: Engineer comment on #15
- verification (tests run, reviewer verdict): `.scratch/issue15_scan.py` over the 94 files in `git ls-files frontend`: 1 hit, the fictional demo password `triage-demo` (harmless); fixture `.scratch/issue15_fixture.txt` flagged all 3 lines. `.scratch/issue15_prompt_check.py`: Status line and `## Prompt` section identical to 0dd108a. Network and backend-key greps run. `make verify`: FAIL on "test files deleted" (2 renamed Lovable tests, a false positive of the gate's `--no-renames` diff, and 4 Bolt tests in the approved deletion); referred to the human. No tests run: no Node.js
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — Orchestrator and PM act on the human's #15 install, Stage 3, n8n/MCP and spec answers

- date: 2026-10-18
- task/issue: issue #15 follow-ups (the human's answers to the PM's three questions and spec note)
- agent role: Orchestrator (Claude Code main session) and PM (Claude Code pm subagent, resumed; entry appended by the Orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's in-session answers: E2 first install with `npm install --before=2026-10-18`; the Stage 3 wording in the human's own text (only the spaces lost to line wrapping restored), recorded on #11 as a change to its decision 2; file the n8n/MCP contract issue; add the owner assumption to `specs.md`
- files changed: `_docs/specs.md` (one Assumptions line, d3a8f11, `HUMAN_APPROVED=1`). GitHub: Orchestrator comment 6244293385 on #11; PM: #15 body (E2 install criterion), comment 6244314164; #23 body (approved Stage 3 text, human review of `openapi.yaml`), comment 6244314486; new issue #27 (n8n and MCP server endpoints, depends on #23)
- verification (tests run, reviewer verdict): `git diff` of the `specs.md` change matched the approved line; `git diff --check` clean
- human review (what I checked or corrected, or `none`): the human approved the `specs.md` line and the Stage 3 text in session

### 2026-10-18 — Engineer fixes the weakened-tests check for renames and approved deletions (#28)

- date: 2026-10-18
- task/issue: issue #28 (verify gate: test-file renames count as moves; `APPROVED_TEST_DELETIONS` in `agent-kit.conf`)
- agent role: Software Engineer (Claude Code software-engineer subagent, launched by the Orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to implement #28, run the fixture script and `make verify BASE=0dd108a`, and return the protected diff with an approval request before committing; no key prompt file saved
- files changed: `_docs/agent-kit/scripts/verify.sh` (rename-aware `-M` diff, R100 moves skipped, edited renames diffed old to new, exact-path approved deletions, glob entries fail) and `agent-kit.conf` (`APPROVED_TEST_DELETIONS` with the four `frontend-bolt/` test paths), both protected, committed alone in 035eafd with `HUMAN_APPROVED=1` (`git show --stat --format= 035eafd` lists only those two files); `lib.sh` unchanged; this entry; `_session-summaries/issue-028-verify-renames.md`. GitHub: Engineer comment on #28
- verification (tests run, reviewer verdict): `.scratch/issue-28-verify-fixtures.sh`: 24 passed, 0 failed (throwaway repos under `.scratch/issue-28-fixtures/`; this repository's HEAD and `git status --short` the same before and after). `make verify BASE=0dd108a` (uncommitted changes): weakened-tests section lists the four Bolt paths under "Deleted with approval", no deletion FAIL; result PASS WITH WARNINGS (only the no-TEST_CMD warning); same result after 035eafd. No QA yet
- human review (what I checked or corrected, or `none`): the human approved the exact diff of `verify.sh` and `agent-kit.conf` in session, 2026-10-18 ("Approve as shown (Recommended)", relayed by the Orchestrator, who checked the working-tree diff matched)

### 2026-10-18 — QA checks #28 (PASS at d32840c); decision point; #15 stage D/E1 QA (FAIL on commit scope)

- date: 2026-10-18
- task/issue: issue #28, lifecycle steps 4-7; issue #15, stage D and part E1, lifecycle step 4
- agent role: QA Engineer (two fresh Claude Code qa-engineer subagents, launched by the Orchestrator; entry appended by the Orchestrator after `make assert-clean`) and Orchestrator (decision point)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instructions to check #28 against its criteria with QA's own fixtures, and #15 stage D and E1 (E2 listed as not yet checked); no key prompt file saved
- files changed: none in the repo (QA scripts in `.scratch/` only). GitHub: QA PASS on #28 (comment 6246783716); QA FAIL on #15 D/E1 (comment 6246840624); Orchestrator decision comments 6247718969 (#28) and 6247719173 (#15)
- verification (tests run, reviewer verdict): #28: QA's `.scratch/qa-28-checks.sh` passed all 27 criteria checks; the Engineer's fixture script passed 24/24; `make verify BASE=0dd108a` PASS WITH WARNINGS (no TEST_CMD only). #15: every D/E1 check passed except E1 (c): `git log --grep="#15"` also matched d3a8f11 (`specs.md`, human-approved), which is outside the allowed paths. After each QA run, `make assert-clean` PASS and HEAD unchanged at d32840c
- human review (what I checked or corrected, or `none`): the human decided QA's risks: #28 risks 1 and 2 to be filed as follow-ups, risk 3 not filed ("bolt was not used"), with a note on #21; #15 E1 (c) to list commits explicitly, "(private)" markings added to #15, and the Lovable project "not linked" to this repo

### 2026-10-18 — Engineer marks the #15 project links "(private)" (new stage D criterion)

- date: 2026-10-18
- task/issue: issue #15, stage D, the new "(private)" criterion (Orchestrator decision comment 6247719173, decision 2; PM comment 6247739573). This entry adds to the d85632b entry, which is not edited
- agent role: Software Engineer (Claude Code software-engineer subagent, launched by the Orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to mark the links, replace the VERIFY line with the human's answer, and list every #15 Engineer commit for E1 (c); no key prompt file saved
- files changed: 26b8757 (`_docs/prompts/lovable-frontend.md`: "(private)" on the Bolt and Lovable link lines, the run record's VERIFY line replaced with the human's answer "both are private on gh" from comment 6246359512; `frontend/README.md`: "(private)" on the Lovable link line); this entry. GitHub: Engineer comment on #15
- verification (tests run, reviewer verdict): `grep -nE "bolt\.new/|lovable\.dev/projects/|VERIFY"` on both files lists 3 link lines, each with "(private)", and no VERIFY line. `.scratch/issue15_prompt_check.py`: Status line and `## Prompt` section identical to 0dd108a. `make verify BASE=0dd108a` result is in the Engineer comment
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — QA re-checks #15 stage D / part E1 (PASS at 3abcc65)

- date: 2026-10-18
- task/issue: issue #15, stage D and part E1, lifecycle step 4 re-check of what changed after QA FAIL 6246840624
- agent role: QA Engineer (fresh Claude Code qa-engineer subagent, launched by the Orchestrator; entry appended by the Orchestrator after `make assert-clean`)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to re-check only the reworded E1 (c), the new "(private)" criterion, the prompt byte-check and `make verify`; no key prompt file saved
- files changed: none in the repo (`.scratch/qa15_recheck.py` and its comment body only). GitHub: QA PASS comment 6247797817
- verification (tests run, reviewer verdict): QA PASS for D/E1. All seven listed #15 Engineer commits touch only allowed paths; 3 link lines carry "(private)" and no VERIFY line is left; the usage log diff since d85632b removes no line; `## Prompt` byte-identical to 0dd108a; `make verify BASE=0dd108a` PASS WITH WARNINGS (no TEST_CMD only). E2 not yet checked (waits for #20). QA reported running one inline `python3 -c "print(1)"`, against the AGENTS.md rule; it changed nothing. After QA, `make assert-clean` PASS, HEAD unchanged at 3abcc65
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-18 — PM grooms issue #20 (dev container Node.js + uv)

- date: 2026-10-18
- task/issue: issue #20 — first grooming; pin the open Node/uv values, correct the stale feature id, close the lockfile question, add refused cases
- agent role: PM (Product Manager subagent, launched by the Orchestrator; entry appended by the Orchestrator per the write-only-`.scratch/` role limit)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to groom #20 per `_docs/agent-kit/team/pm.md`; no key prompt file saved
- files changed: none in the repo (drafts in `.scratch/`). GitHub: PM grooming comment 6247960494; #20 body edited to the groomed text; PM decisions comment 6248923707; filed follow-up #31 (Docker/Compose), linked from #20 out-of-scope
- verification (tests run, reviewer verdict): none (no code changed). PM read `frontend/package.json` (vite 8.1.5), the devcontainers/features node feature, nodejs/Release schedule and PyPI/uv metadata to pin the values
- human review (what I checked or corrected, or `none`): the human answered the four grooming decisions (Node `24.22.0`; uv via `pipx install uv==0.13.1`; file #31; apply the body edits as drafted)

### 2026-10-18 — Engineer implements #20 (uncommitted, held for the human's gated commit)

- date: 2026-10-18
- task/issue: issue #20 — add pinned Node.js (`ghcr.io/devcontainers/features/node:2` at `24.22.0`, `pnpmVersion: none`), remove the duplicate `remoteEnv.PATH`, and add `pipx install uv==0.13.1`
- agent role: Software Engineer (opencode software-engineer subagent, launched by the Orchestrator; entry appended by the Orchestrator per the write-only-`.scratch/` role limit)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to implement #20 from the groomed body, not rebuild, and return the diff and approval request; no key prompt file saved
- files changed: `.devcontainer/devcontainer.json` and `.devcontainer/setup.sh` in the working tree only — UNCOMMITTED, because the pre-commit hook gates any `.devcontainer/` change behind `HUMAN_APPROVED=1`; the Engineer stopped and returned the approval request. `.scratch/issue-20-check.py`, `.scratch/issue-20-tooling.sh`, `.scratch/issue-20-pipx-writable.py` (git-ignored). Proposed (not edited) AGENTS.md Environment line. This entry and `_session-summaries/issue-020-node-uv-devcontainer.md`
- verification (tests run, reviewer verdict): `make verify BASE=HEAD` PASS WITH WARNINGS (only the no-`TEST_CMD` warning; project in planning, no code); `.scratch/issue-20-check.py` all static criteria PASS including the refused-case patterns. Runtime `node`/`npm`/`uv` not run (no Node or uv in this container; deferred to QA after the human rebuilds). `.devcontainer/devcontainer-lock.json` not regenerated (no devcontainer CLI here); raised as a decision question
- human review (what I checked or corrected, or `none`): the human chose to run the `.devcontainer/` commit commands themselves and chose lockfile option 1 with checks (show the regenerated-lock diff after the rebuild; only new feature entries; `github-cli` unchanged; if not updated, stop). The commit and rebuild are pending

### 2026-10-18 — Add `make tool-versions` target and document it (human instruction, no issue)

- date: 2026-10-18
- task/issue: add a `make tool-versions` target that prints the version of node, npm, uv, python3 and docker (or `<tool>: missing`), and add it to the AGENTS.md Commands section (human instruction, no issue)
- agent role: Orchestrator
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): human instruction in-session ("Add a `tool-versions` target to the Makefile's project section (protected; show me the diff) that prints the version of node, npm, uv, python3 and docker, or \"<tool>: missing\" ... Add it to AGENTS.md's Commands section."); no key prompt file saved
- files changed: `Makefile` (new `tool-versions` target with `##` help text, in the project section; 3 insertions); `AGENTS.md` (Commands line "Tool versions:"; the whole file was committed, carrying the human's pre-existing uncommitted Project-rules additions); this entry
- verification (tests run, reviewer verdict): `make tool-versions` printed `node: missing`, `npm: missing`, `uv: missing`, `python3: Python 3.12.15`, `docker: missing`; `make help` lists `tool-versions`; `git diff --check` clean
- human review (what I checked or corrected, or `none`): the human approved committing `Makefile` and `AGENTS.md` with `HUMAN_APPROVED=1`, including the pre-existing AGENTS.md Project-rules edits

### 2026-10-18 — Engineer runs the post-rebuild runtime checks and Verify for #20 (lifecycle step 3)

- date: 2026-10-18
- task/issue: issue #20, lifecycle step 3 continued after the human rebuilt the container: the post-rebuild runtime checks (`node`/`npm`/`uv --version` exit 0, and the non-interactive `make`-shell criterion), run Verify, and post the Engineer comment
- agent role: Software Engineer (opencode software-engineer subagent, launched by the Orchestrator; entry appended by the Engineer, as its role file says)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to run the runtime checks the post-rebuild criteria need, run Verify with the appropriate BASE, post the Engineer `:` comment on #20, and append this entry; no key prompt file saved
- files changed: `.scratch/issue-020-runtime-check.sh` (git-ignored; read-only checks, no installs and no network); this entry. No repo file other than this entry changed. GitHub: Engineer comment 6249655264 on #20 (body drafted in `.scratch/issue-020-engineer-comment.md`)
- verification (tests run, reviewer verdict): `make verify BASE=dc843de` (the issue's own commits 4eb0485 and f3ed87d; 4 files, 35 insertions, 14 deletions) PASS WITH WARNINGS, and `make verify` (default, since `origin/main`) PASS WITH WARNINGS; the only warning in each is the no-`TEST_CMD` one (planning phase, no code exists; whitespace PASS; no test files changed). `.scratch/issue-020-runtime-check.sh` every check exit 0: `node --version` v24.22.0, `npm --version` 11.19.1, `uv --version` uv 0.13.1 (x86_64-unknown-linux-gnu); the same three in a non-interactive `sh -c`; `command -v` resolves node/npm to `/usr/local/share/nvm/versions/node/v24.22.0/bin/` and uv to `/usr/local/py-utils/bin/uv`; `make tool-versions` exit 0. Finding reported to the human: commit 4eb0485 also changes `opencode.json` (not in #20's Constraints). QA not run
- human review (what I checked or corrected, or `none`): none yet; the report raises two items for the human — the `opencode.json` change bundled into 4eb0485 (outside #20's Constraints, protected file, not touched) and the proposed AGENTS.md Environment line, which is not edited

### 2026-10-18 — QA checks #20 (PASS at abaed5d)

- date: 2026-10-18
- task/issue: issue #20 (dev container Node.js and uv), lifecycle step 4
- agent role: QA Engineer (fresh opencode qa-engineer subagent, launched by the Orchestrator; entry appended by the Orchestrator after `make assert-clean` per the role's write-only-`.scratch/` limit)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to check every criterion in #20 against the rebuilt container and the committed diff (`git diff dc843de..HEAD -- .devcontainer` for the refused cases), run `node`/`npm`/`uv --version` and the non-interactive `make`-shell check, run Verify itself, and post a `QA:` verdict; no key prompt file saved
- files changed: none in the repo (`.scratch/issue-020-qa-check.py` and `.scratch/qa-comment-20.md` only). GitHub: QA PASS comment 6249711806
- verification (tests run, reviewer verdict): QA PASS, all nine criteria. `node --version` v24.22.0, `npm --version` 11.19.1, `uv --version` uv 0.13.1; both `sh -c` and `make tool-versions` resolve all three; `remoteEnv` has exactly one `PATH` with all three segments; `git diff dc843de..HEAD -- .devcontainer` shows no refused pattern; the lockfile adds one `node:2` entry and leaves `github-cli:1` byte-identical. The AGENTS.md Environment criterion was treated as PASS (deferred): the issue words it as a protected `HUMAN_APPROVED=1` commit applied at the post-PASS decision point, so QA checked the Engineer's proposed text. `make verify BASE=dc843de` and `make verify` both PASS WITH WARNINGS (only the no-`TEST_CMD` warning). After QA, `make assert-clean` PASS and HEAD unchanged at abaed5d
- human review (what I checked or corrected, or `none`): none yet; risks outside the criteria reported for the decision point — the `opencode.json` change bundled into 4eb0485 (protected, outside #20's Constraints) and the #20 session summary committed at 4bfa89c before QA PASS (candid, no false completion claim)

### 2026-10-18 — Engineer implements #15 stage E2 (install, run, test; protected targets proposed)

- date: 2026-10-18
- task/issue: issue #15, stage E2 (install, run, test), lifecycle step 3, after #20 closed
- agent role: Software Engineer (opencode software-engineer subagent, launched by the Orchestrator; entry appended by the Engineer, as its role file says)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to work the "E2. Install, run, test" and Constraints sections exactly; run `node`/`npm --version`, run `npm install --before=2026-10-18` in `frontend/` (pre-approved), add and verify the make targets, re-run the E1 scan, run Verify, commit non-protected changes only, and post an `Engineer:` comment; no key prompt file saved
- files changed: `frontend/package-lock.json` (new, 9130 insertions) committed in 71e5103; `frontend/README.md` ("Make targets" section and dev-server host/port; Services layer untouched) committed in 99781ee; this entry. Protected `Makefile` (frontend-install/start/stop/test plus the all-tests `test` target), `agent-kit.conf` (`TEST_CMD="make test"`) and `AGENTS.md` (Install/Run/Test/Verify lines) edited in the working tree only — NOT committed; their exact diffs are in the Engineer comment on #15. Git-ignored: `.scratch/issue15-e2-smoke.py`, `.scratch/issue15-e2-engineer-comment.md`. GitHub: Engineer comment on #15
- verification (tests run, reviewer verdict): `node --version` v24.22.0, `npm --version` 11.19.1. `npm install --before=2026-10-18` exit 0 (523 packages; `--before` accepted as written, no fallback). `git diff 0dd108a:frontend-lovable/package.json HEAD:frontend/package.json` prints nothing. `make frontend-install` (`npm ci`) exit 0; `make frontend-test` and `make test` exit 0 with 2 files / 10 tests passed; `.scratch/issue15-e2-smoke.py` `/login` and `/` both HTTP 200 with no backend; `make frontend-stop` stopped only the recorded PID and with no PID file printed "frontend is not running" and stopped nothing; no vite process left (`pgrep -af vite`). E1 scan `.scratch/issue15_scan.py` over 95 committed `frontend/` files: 1 hit, the fictional demo password `triage-demo` at `mockData.ts:3` (harmless; the fixture with `owner@gmail.com`, `ghp_`+36, `sk-`+32 is flagged). `make verify` (default, since origin/main; with the working-tree `TEST_CMD`) PASS, no warnings: tests 10/10, whitespace PASS, weakened tests none (the four `frontend-bolt/` paths are the approved E1 deletions). QA not run
- human review (what I checked or corrected, or `none`): none yet; the decision point covers the three protected diffs and the choices named in the comment (all-tests target named `test`; `npm --prefix frontend test`; direct Vite binary with explicit `--host 127.0.0.1 --port 5173`; port 5173; the extra Verify-line update)

### 2026-10-18 — QA checks #15 stage E2 (first run PASS discarded; clean re-run PASS at 352ff95)

- date: 2026-10-18
- task/issue: issue #15, stage E2 (install, run, test), lifecycle steps 4-5, two runs
- agent role: QA Engineer (two fresh opencode qa-engineer subagents, launched by the Orchestrator; entries appended by the Orchestrator after `make assert-clean` per the role's write-only-`.scratch/` limit) and Orchestrator (`opencode.json` decision)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to check the E2 criteria and Constraints at `e3de014`, then (after the tree was dirtied) a second instruction to re-check at `352ff95` with the tree kept clean; no key prompt file saved
- files changed: none in the repo by QA (`.scratch/` scripts only). GitHub: QA PASS comments 6250209261 (first run, discarded) and 6250305366 (kept re-run). `opencode.json` (protected) gained two allow rules (`git ls-files*`, `pgrep *`) during the first run — the tool persisted them; the human approved keeping them and they were committed as `352ff95` with `HUMAN_APPROVED=1`
- verification (tests run, reviewer verdict): first run QA PASS at `e3de014` (10/10 tests, `/login` HTTP 200 on `127.0.0.1:5173`, secrets scan clean), but `make assert-clean` then FAILED on ` M opencode.json`, so the verdict was discarded per process step 5. Re-run at `352ff95`: QA PASS, all E2 criteria — node v24.22.0, npm 11.19.1, `make frontend-install` (`npm ci`) exit 0, `make frontend-test` and `make test` 10/10, `frontend-start` recorded PID 47104 and `frontend-stop` stopped only it, `/login` and `/` HTTP 200 on port 5173 with no backend, `package.json` unchanged since `0dd108a`, 95-file secrets scan clean and its fixture flagged, no path outside the allowed list for any #15 commit (`352ff95` is the unrelated opencode.json commit). `make verify` and `make verify BASE=0dd108a` both PASS, no warnings. After the re-run `make assert-clean` PASS and HEAD unchanged at `352ff95`
- human review (what I checked or corrected, or `none`): the human chose "Keep and commit" for the two `opencode.json` allow rules (they were the tool persisting an approved read-only check); committed with `HUMAN_APPROVED=1` as `352ff95`

### 2026-10-18 — #15 E2 decision point, follow-up comment, and close

- date: 2026-10-18
- task/issue: issue #15, lifecycle steps 7-9 (decision point, cleanup and summary, close)
- agent role: Orchestrator; Software Engineer (one follow-up comment)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): human decisions at the E2 decision point (post the Engineer follow-up comment naming the remaining E2 commits; then update the summary, clean up and close); no key prompt file saved
- files changed: this entry; `_session-summaries/issue-015-frontend-choice.md` (updated for E2). GitHub: Engineer follow-up comment 6250367523 naming `c95643b` and `e3de014` (and noting `352ff95` is the unrelated `opencode.json` commit). No code changed
- verification (tests run, reviewer verdict): QA PASS at `352ff95` stands; `make assert-clean` PASS; `make clean-scratch` run (`.scratch/` emptied; no process was running)
- human review (what I checked or corrected, or `none`): the human chose to post the Engineer follow-up comment (recommended) rather than accept QA's judgement on the strict E1(c) reading

### 2026-10-18 — Independent review of OpenCode's work on #20 and #15 stage E2

- date: 2026-10-18
- task/issue: issues #20 and #15 (stage E2 and close-out), independent review at HEAD `ac06c02`
- agent role: Reviewer (independent review, asked by the human)
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request for an independent review of OpenCode's work on #20 and #15; exact text not recorded
- files changed: `_docs/reviews/2026-10-18-review-issues-15-20.md` (new; committed 2026-10-19 with the entry below)
- verification (tests run, reviewer verdict): no tests run; read the issues, comments, diffs, Makefile, devcontainer recipe, push check, `verify.sh`, log entries and session summaries; checked the built container. Findings: 1 High (the push check will fail: no `install` target, and the `python:3.12` image has no Node), 2 Medium (corepack shims and unpinned nvm in the rebuilt container; QA ran in the build tool with no recorded exception), 4 Low, 8 not-recommended choices, 4 decisions for the human
- human review (what I checked or corrected, or `none`): none yet; the review's four decisions are open. Finding 3 was overtaken by the 2026-10-19 QA rule change (entry below)

### 2026-10-19 — QA independence rule changed

- date: 2026-10-19
- task/issue: no issue; process rule change in `_docs/agent-team.md` § QA independence
- agent role: Orchestrator
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to replace the QA rule with: "QA always runs in a fresh, isolated context—either in a separate session or via an isolated subagent, never within the context that performed the build. A different tool or model is preferred; when it isn't available, QA proceeds anyway and the QA comment and log entry record which tool and model did the build and the QA."
- files changed: `_docs/agent-team.md` (new rule quoted word for word; the earlier rule, its #12 exception and the three recorded uses kept under "Earlier rule (until 2026-10-19)"; fresh-run and Assert-clean paragraph moved under the new rule); this entry; `_docs/reviews/2026-10-18-review-issues-15-20.md` committed unchanged
- verification (tests run, reviewer verdict): `git diff --check` clean; grep confirmed the rule appears in no role file, `process.md`, `AGENTS.md` or other protected file
- human review (what I checked or corrected, or `none`): the human set the rule wording and approved this commit

### 2026-10-19 — File issue #32 from review errors 1 and 2

- date: 2026-10-19
- task/issue: issue #32 (new), from errors 1 and 2 of `_docs/reviews/2026-10-18-review-issues-15-20.md`
- agent role: Orchestrator
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for an issue covering the two errors that the OpenCode agent can work, with priority and order assessed
- files changed: this entry. GitHub: issue #32 created (body edited once to replace an issue-number placeholder with #32). Not groomed; the PM grooms it first
- verification (tests run, reviewer verdict): none; read the push check (`pre-push` lines 23, 29 and 45), the Makefile and `verify.sh` to confirm the facts in the issue
- human review (what I checked or corrected, or `none`): none yet

### 2026-10-19 — Implement issue #32 Part A proposal and Part B devcontainer fix

- date: 2026-10-19
- task/issue: issue #32, Part A (push check `install` target and `frontend-test` guard; protected-file diffs proposed) and Part B (pin nvm, remove corepack shims)
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, the Engineer role file and issue #32, implement Part A as protected-file diffs (not edits) and Part B with option (b) `corepack disable`, commit only non-protected paths, run `make frontend-install`/`make test`/`make verify`, and post an `Engineer:` comment; no key prompt file saved
- files changed: `.devcontainer/devcontainer.json` (adds `"nvmVersion": "0.40.8"`) and `.devcontainer/setup.sh` (pins the node bin path and runs `corepack disable`), edited and staged; the commit needs `HUMAN_APPROVED=1` and was left for the orchestrator/human. `_docs/ai-usage-log.md` (this entry) and `_session-summaries/issue-032-push-check-and-devcontainer.md`. `Makefile` and `AGENTS.md` (protected) were not edited; their exact proposed diffs are in the `Engineer:` comment on #32. `.devcontainer/devcontainer-lock.json` unchanged. Git-ignored `.scratch/issue-32.json`, `.scratch/issue32-makefile-test/`, `.scratch/proposed-AGENTS.md`
- verification (tests run, reviewer verdict): `make frontend-install` (`npm ci`) exit 0, 518 packages, `frontend/package-lock.json` unchanged; `make test` 2 files / 10 tests passed; `make verify` PASS, no warnings (tests 10/10, whitespace PASS, weakened tests none; the four `frontend-bolt/` deletions are approved). Scratch guard test with the proposed Makefile and no `frontend/node_modules` printed `frontend/node_modules is missing: run make install first` and exited 1; `grep -E '^install[[:space:]]*::?'` matched the proposed target; `make help` listed `install`; `jq . .devcontainer/devcontainer.json` valid; `bash -n .devcontainer/setup.sh` clean. Current container: the four corepack shims still exist, `corepack --version` 0.36.0, node bin dir `drwxrwsr-x vscode nvm`, `nvm --version` 0.40.8. Post-rebuild checks not run; QA not run
- human review (what I checked or corrected, or `none`): none yet; the `.devcontainer/` commit is pending human approval and rebuild, and the protected diffs are pending the Orchestrator's approved commit

### 2026-10-19 — Close out issue #32 after QA PASS and the human's gated push

- date: 2026-10-19
- task/issue: issue #32, lifecycle steps 4-9 (QA, assert-clean, decision point, cleanup and close)
- agent role: Orchestrator; QA engineer (fresh isolated subagent)
- model: opencode/deepseek-v4.1-flash-free (build and QA; QA ran in a fresh isolated subagent, per the 2026-10-19 QA rule)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "check issues and continue", then the gate output pasted into the session; no key prompt file saved
- files changed: `_session-summaries/issue-032-push-check-and-devcontainer.md` (final state); this entry. GitHub: Orchestrator comments 6270008516 and 6271319915; issue #32 closed at the end of this close-out
- verification (tests run, reviewer verdict): QA PASS at `eb2e64b`, all Part A and Part B criteria (rebuilt-container checks: no `yarn`/`yarnpkg`/`pnpm`/`pnpx`, nvm `0.40.8`, node `v24.22.0`, npm `11.19.1`, uv `0.13.1`, `make install verify` PASS). `make assert-clean` PASS before the close-out edits and HEAD unchanged at `eb2e64b`. Human gate in the clean clone: `sandbox/main` and HEAD at `eb2e64b`; `node:24.22.0-bookworm` pulled (digest `sha256:14078204b6bb268c107ceff6d3c43f45a888105e5c2b18b14c32b3409d93a1b0`); `command -v bash git make node npm` printed `/usr/bin/bash`, `/usr/bin/git`, `/usr/bin/make`, `/usr/local/bin/node`, `/usr/local/bin/npm`; the gated push ran `make -C . install verify` (npm ci 518 packages, 10/10 tests, whitespace PASS, weakened tests none), printed `VERIFY: PASS`, and pushed `c1896e4..eb2e64b main -> main`. `make verify` after the close-out edits; `make assert-clean` and `make clean-scratch` at close-out
- human review (what I checked or corrected, or `none`): the human approved the protected diffs and the `.devcontainer/` commit, rebuilt the container, set `AGENT_PUSH_CHECK_IMAGE=node:24.22.0-bookworm`, and ran the real gated push

### 2026-10-19 — Groom issue #21 and resolve the `.npmrc` ownership decision

- date: 2026-10-19
- task/issue: issue #21 (grooming only)
- agent role: PM (subagent); Orchestrator relaying the human's decision
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instructions to groom #21 against the task template and to apply the human's option 1 for `frontend/.npmrc`; no key prompt file saved
- files changed: none in the repo. GitHub: issue #21 body rewritten twice; PM comments 6270448389 and 6271129779
- verification (tests run, reviewer verdict): read-only checks only: `git status --short` clean at `eb2e64b`; `make tool-versions` (node `v24.22.0`, npm `11.19.1`, uv `0.13.1`, python3 `3.12.15`, `docker: missing`); `make frontend-test` 2 files / 10 tests passed; a `.scratch/` audit found 46 `frontend/src/components/ui/` files, exactly 4 imported outside that folder, and 10 `it(` tests; Lovable, network and lockfile greps. No product code changed; no implementation
- human review (what I checked or corrected, or `none`): the human chose option 1: #21 adds `frontend/.npmrc` with `min-release-age=1`; #33 hardening D later appends `ignore-scripts=true`

### 2026-10-19 — Implement issue #21 frontend clean-up

- date: 2026-10-19
- task/issue: issue #21
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, the Engineer role file and issue #21, implement the clean-up, gather build evidence for the three render-mode options, propose (not edit) the protected-file diffs, run `make verify` and return the render-mode decision question; no key prompt file saved
- files changed: commits `c816d51` and `e65448e`. Removed `frontend/bun.lock`, `frontend/bunfig.toml`, `frontend/AGENTS.md`, `frontend/.lovable/project.json`, `frontend/src/lib/lovable-error-reporting.ts` and 42 unused `frontend/src/components/ui/*.tsx`; added `frontend/.npmrc` (`min-release-age=1`); rewrote `frontend/vite.config.ts` (explicit plugins, interim render target), `frontend/package.json`, `frontend/package-lock.json` (pruned), `frontend/README.md`, `frontend/src/routes/__root.tsx` (Lovable error reporting, `twitter:site` and Google Fonts links out) and `frontend/src/styles.css` (system font stacks). `Makefile` and `AGENTS.md` were not edited; the proposed `frontend-build` diff is in the `Engineer:` comment. `_docs/ai-usage-log.md` (this entry), `_session-summaries/issue-021-frontend-cleanup.md`. Git-ignored `.scratch/audit_frontend.py`, `.scratch/issue-21.json`, `.scratch/issue-21-comment.md`, `.scratch/node-build-{start,stop}.sh`
- verification (tests run, reviewer verdict): `make frontend-install` (`npm ci`) exit 0 (390 packages, down from 518) and leaves the lockfile unchanged; `npm --prefix frontend config get min-release-age` prints `1`; `make frontend-test` 2 files / 10 tests passed (unchanged baseline); `make verify` PASS (tests 10/10, whitespace PASS, weakened tests none); Lovable refused-case grep has exactly one hit (README provenance); `npm i`/`npm install` grep in README has no hits; network grep hits only `src/services/mockData.ts` and `src/server.ts` (kept while the render mode is undecided). Build evidence: SPA mode (`spa: { enabled: true }` + `preview.host`) builds `dist/client` 548K (shell `_shell.html`) + `dist/server` 196K; nitro `node-server` builds `.output` 2.0M (`server/index.mjs` + `public` 544K) and served the app on `127.0.0.1:3100` (title `Findings — VulnTriage`); plain TanStack Router + Vite builds `dist` 512K with `index.html` (main bundle 305 kB vs 342 kB). All three spike configs and outputs were deleted; `git status --short` clean. QA not run
- human review (what I checked or corrected, or `none`): none yet; the render-mode decision, the protected `Makefile` diff and QA are open

### 2026-10-19 — Finalize issue #21 render mode: plain TanStack Router + Vite

- date: 2026-10-19
- task/issue: issue #21 — apply the human's render-mode decision (option 3: plain TanStack Router + Vite, Orchestrator comment 6276301196) on top of `25c9b68`
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, the Engineer role file, issue #21 and the human's decision comment, then implement exactly: `tanstackRouter` in `vite.config.ts`, add `frontend/index.html` and `frontend/src/main.tsx`, delete the server files, remove unused dependencies, keep the 10 tests, verify the build serves from `frontend/dist/` and return the final state; no key prompt file saved
- files changed: commit `e367e49`. `frontend/vite.config.ts` (`tanstackStart` → `tanstackRouter({ target: "react", autoCodeSplitting: true })`, other plugins/aliases/dedupe/env/lightningcss/tailwind/tsconfig paths kept); added `frontend/index.html` and `frontend/src/main.tsx`; deleted `frontend/src/server.ts`, `frontend/src/lib/error-capture.ts`, `frontend/src/lib/error-page.ts`, `frontend/src/start.ts`; removed `@tanstack/react-start` and `nitro` from `frontend/package.json` and pruned `frontend/package-lock.json`; `frontend/src/routeTree.gen.ts` regenerated (dropped the `@tanstack/react-start` module augmentation); `frontend/README.md` records the render mode and the `frontend/dist/` output. `frontend/src/routes/__root.tsx` and the route files were not changed. `Makefile`, `AGENTS.md`, `agent-kit.conf` and `opencode.json` not touched. `_docs/ai-usage-log.md` (this entry), `_session-summaries/issue-021-frontend-cleanup.md`
- verification (tests run, reviewer verdict): `npm --prefix frontend run build` exit 0, writes `frontend/dist/index.html` (963 bytes) and `frontend/dist/assets/` (main bundle `index-Mqk3KKZ8.js` 305233 bytes), git-ignored; `.scratch/serve_check.py` served `frontend/dist` with `python3 -m http.server` on `127.0.0.1:8137` and `GET /` returned HTTP 200 (963 bytes, `#root` present) and the main JS asset returned HTTP 200 (305233 bytes), then it stopped only its own server process; `make install` (`npm ci`) exit 0, 351 packages, lockfile stable across two runs (sha256 unchanged); `make frontend-test` 2 files / 10 tests passed; `make test` 10 passed; `make verify` PASS (tests 10/10, whitespace PASS, weakened tests none). Refused cases re-checked: no `@lovable.dev` in `frontend/src`/`vite.config.ts`/`vitest.config.ts`/`package.json`; `grep -rni lovable frontend` has exactly one hit (README provenance); no `npm i`/`npm install` in `frontend/README.md`; `frontend/.npmrc` is exactly `min-release-age=1` and `npm --prefix frontend config get min-release-age` prints `1`; no dependency added (only the two removed); network grep now hits only `frontend/src/services/mockData.ts` (the `src/server.ts` exception has ended). QA not run
- human review (what I checked or corrected, or `none`): none yet; the Orchestrator applies the approved `Makefile` and `AGENTS.md` diffs after this confirmation, then QA runs

### 2026-10-19 — Apply the approved #21 protected changes, run QA and close #21

- date: 2026-10-19
- task/issue: issue #21, lifecycle steps 7-9 (decision point, protected-change commit, QA, cleanup and close)
- agent role: Orchestrator; QA engineer (fresh isolated subagent)
- model: opencode/deepseek-v4.1-flash-free (build and QA; QA ran isolated, per the 2026-10-19 QA rule)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's decisions — render mode option 3, approve the `Makefile` `frontend-build` target and the one `AGENTS.md` Build line, record the decision on #21, note `frontend/dist/` in `frontend/README.md`, end the session after #21 without starting #22, and do not use `uptime` unless a task requires it; no key prompt file saved
- files changed: commit `682c69f` (protected `Makefile` `frontend-build` target + `.PHONY` entry, and the one `AGENTS.md` Build line; committed alone with `HUMAN_APPROVED=1`); this entry; `_session-summaries/issue-021-frontend-cleanup.md` finalized. GitHub: Orchestrator comments 6276301196 (decisions) and the close comment; issue #21 closed
- verification (tests run, reviewer verdict): `make frontend-build` exit 0 and writes `frontend/dist/index.html` (963 bytes); `make verify` PASS at `682c69f` (10/10 tests, whitespace PASS, weakened tests none); QA PASS at `682c69f` (all acceptance criteria and refused cases; `frontend/dist` served HTTP 200; the source app rendered in jsdom from login through demo sign-in to findings; protected diff only the approved two files; `agent-kit.conf` unchanged); `make assert-clean` PASS and HEAD unchanged at `682c69f`; `make clean-scratch` run. QA risks outside the criteria: `__root.tsx` `shellComponent` renders `<html>` inside `#root` (React hydration warning); the built `index.html` has no stylesheet link (runtime-injected CSS, FOUC without JS); `vite-tsconfig-paths` Vite 8 warning; `package.json` name `tanstack_start_ts`; `682c69f` bundles two protected files in one commit
- human review (what I checked or corrected, or `none`): the human approved the render mode (option 3) and the protected changes, directed that `frontend/README.md` record the `frontend/dist/` path, and asked to end the session after #21 (no #22) and not to use `uptime` again unless a task requires it

### 2026-10-19 — Senior-engineer review of #21 and #32; review #34; file #35

- date: 2026-10-19
- task/issue: review of the opencode work on closed issues #21 and #32; review of follow-up #34; file the push-check plan-mode follow-up (#35)
- agent role: Orchestrator (senior-engineer review at the human's request)
- model: Claude Code / claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for a senior-engineer review of the opencode agent's work on #21 and #32, scaled down to save usage; then to review the follow-up issues; then approved posting the review and filing the missing follow-up; no key prompt file saved
- files changed: this entry only. GitHub: review comment on #34 (6277799291), new issue #35 ("Push check: plan mode (AGENT_PUSH_CHECK_PLAN=1) completes the push without checking"), link comment on #32 (6277802711). Git-ignored `.scratch/issue-21.json`, `.scratch/issue-32.json`, `.scratch/issue-34-review.md`, `.scratch/issue-prepush-plan.md`
- verification (tests run, reviewer verdict): read-only review; no build, test or `make verify` run. Read the #21 and #32 issue bodies and comments, the #32 diffs (`7207911`, `eb2e64b`), `frontend/src/routes/__root.tsx`, `frontend/index.html` and `frontend/src/main.tsx` at HEAD, and `pre-push` lines 120-140. Verdicts: #32 sound (minor: `setup.sh` repeats the Node version in a hardcoded path); #21 clean-up sound, but the render-mode switch left the Start `shellComponent` (`<html>` inside `#root`) and no stylesheet link in `index.html`, which QA noted and the close-out deferred (now #34). Found `pre-push` plan mode exits 0 after printing the plan, so the push goes through unchecked (now #35). #34 review: six points, mainly the `head()`/`HeadContent` contradiction, the leftover `?url` CSS import, and no check method for the React warning criterion. Permission review: rule deviations in this session were two inline `python3 -I -c` commands (to print issue JSON) and raw `sed`/`tail` reads instead of the read tool; whether any stopped for approval was not recorded
- human review (what I checked or corrected, or `none`): the human approved posting the #34 review and filing #35

### 2026-10-19 — Check the #21/#32 permission reviews; build the permission review into the agent kit

- date: 2026-10-19
- task/issue: check whether the opencode sessions for #21 and #32 followed the AGENTS.md permission review rule (added in `fbc2a5b`), then make the rule part of the role and close-out steps
- agent role: Orchestrator (review at the human's request)
- model: Claude Code / claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked whether the opencode agent did the permission review, then asked to build it into the process now for long-term efficiency; no key prompt file saved
- files changed: commit `d0884f6` (protected, `HUMAN_APPROVED=1`, approved by the human in this session): `_docs/agent-kit/templates/session-summary.md` (new Permission review section), `_docs/agent-kit/procedures/session-summary.md`, `_docs/agent-kit/process.md` (step 8 bullet, step 9 close condition, definition of done), `_docs/agent-kit/team/pm.md`, `_docs/agent-kit/team/qa-engineer.md`, `_docs/agent-kit/team/software-engineer.md` (a "commands that stopped for approval" line in each role comment). This entry. Git-ignored `.scratch/perm_notes.py` (read-only)
- verification (tests run, reviewer verdict): read-only check with `.scratch/perm_notes.py` over the #21 and #32 issue comments, plus grep of both session summaries. #21: PM and Engineer comments had permission notes; QA and Orchestrator comments did not; the summary section (`eab3ee9`) had the three groups but no settings proposal, and left out the PM's report that `gh issue edit 21` ran without a prompt although `opencode.json:49` sets it to `ask` (cause not found; `.opencode/agents/pm.md` sets no bash rule). #32: no role comment or summary section had a permission review; the session likely started before `fbc2a5b`. The rule appeared nowhere in `_docs/agent-kit/` before `d0884f6`. `git diff --check` clean; `make verify` not run (documentation-only change)
- human review (what I checked or corrected, or `none`): the human said the `4895a12` `rg` allow rule was their own change, not the agent's; the human approved the exact protected diff before the commit

### 2026-10-19 — Implement issue #22 services layer

- date: 2026-10-19
- task/issue: issue #22, "Frontend services layer ready for a real API" (groomed; human decisions: services-owned persisted session, idempotent `logout`, two optional owner fields)
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, `_docs/agent-kit/team/software-engineer.md`, `_docs/agent-kit/procedures/verify.md`, issue #22 and its PM comment, implement every acceptance criterion and refused case, commit at logical milestones, run `make verify`, post an `Engineer:` comment, and return the commits, verify result, criteria evidence, choices, proposed AGENTS.md changes, spec notes and approval-stopped commands; no key prompt file saved
- files changed: commit `759735a` (14 files): `frontend/src/services/{types,index,mockService,mockData}.ts`; `frontend/src/components/vt/AuditTrail.tsx` (new) and `Badges.tsx`; `frontend/src/routes/{login,_authed,_authed.assets.index,_authed.assets.new,_authed.findings.$findingId,_authed.findings.$findingId_.accept}.tsx`; `frontend/src/test/vulntriage.test.tsx`; `frontend/README.md`. This entry in `_docs/ai-usage-log.md` (the issue expected `frontend/**` only; the log is the project rule's record). No `Makefile`, protected file, `package.json` or lockfile change. Git-ignored `.scratch/issue-22.json`
- verification (tests run, reviewer verdict): `make frontend-test` 2 files / 35 tests passed; `make frontend-build` exit 0 (`frontend/dist/`, git-ignored); `frontend/node_modules/.bin/tsc --noEmit -p frontend/tsconfig.json` exit 0 (not a configured project check); `make verify` at `759735a` PASS WITH WARNINGS: tests 35/35, whitespace PASS, weakened tests 7 rewritten assertions, each replaced by a stronger typed assertion (2-arg `acceptRisk`; `ServiceError` code instead of generic throw; non-null `getFinding`; `isOwnerless` instead of `owner === null`; wire value `risk_accepted` instead of `risk accepted`). Refused cases re-checked: no `mockData`/`mockService` import in `routes/`, `components/`, `lib/`; only type-only deep imports of `@/services/...`; no `fetch(`/`axios`/`XMLHttpRequest`/`WebSocket` in `src/services`; `acceptRisk(` has only 2-arg calls; no `owner:` property in `src/`; no dependency added. QA not run
- human review (what I checked or corrected, or `none`): none yet; issue left open for QA. Commands that stopped for approval: none

### 2026-10-19 — Orchestrate issue #22 from grooming to close

- date: 2026-10-19
- task/issue: issue #22, "Frontend services layer ready for a real API" (PM grooming, Engineer implementation, QA check, decision point, cleanup and close)
- agent role: Orchestrator; PM, Software Engineer and QA Engineer (fresh isolated subagents)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to check the issues and start #22 following `_docs/agent-kit/process.md`; answered the three grooming decisions (persisted service-owned session, idempotent `logout`, two optional owner fields) and the decision-point questions (approve both spec notes, the 10 → 35 test-count updates, no partial-owner follow-up, keep a session after a failed login). No key prompt file saved
- files changed: commit `9f742d2` (protected `_docs/specs.md`, human-approved, committed alone); commit `c85c6e8` (protected `AGENTS.md` and `agent-kit.conf`, human-approved, committed alone); this entry; `_session-summaries/issue-022-services-layer.md`. GitHub: PM comment 6278909287, Engineer comment 6279079561, QA PASS comment 6279190817, issue #22 closed
- verification (tests run, reviewer verdict): `make frontend-test` 35/35; `make verify` PASS WITH WARNINGS at `759735a` (7 changed-contract assertions rewritten stronger, each justified); QA independently PASS at `f790ddc` for all 34 criteria and refused cases; `make assert-clean` PASS and HEAD unchanged at `f790ddc`; `make clean-scratch` run
- human review (what I checked or corrected, or `none`): the human chose the three grooming options and approved the spec and protected test-count changes at the decision point

### 2026-10-19 — Senior review of closed issue #22

- date: 2026-10-19
- task/issue: issue #22, "Frontend services layer ready for a real API" (review after close)
- agent role: Orchestrator (senior engineering review)
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for a review of opencode's finished #22 "as a senior engineer who still has a lot more review work this week to complete", then approved posting the follow-ups and this log entry. No key prompt file saved
- files changed: this entry. GitHub: comment on #25 (6279525860: an auth failure shows up as an empty findings/assets list; suggested redirect to `/login`, error states, no retry, one UI test) and on #23 (6279526319: the order in which errors are checked; whether owner fields are always present). Git-ignored `.scratch/issue-22.json`, `.scratch/comment-25.md`, `.scratch/comment-23.md`
- verification (tests run, reviewer verdict): read the diffs of `759735a`, `9f742d2`, `c85c6e8`, the current `frontend/src/services/{types,index,mockService}.ts`, and the PM, Engineer, QA and Orchestrator comments on #22; grep of the list routes' error handling. Verdict: approve, no reopen. Tests and `make verify` not re-run (QA and the orchestrator ran them at `f790ddc`)
- human review (what I checked or corrected, or `none`): the human approved posting both follow-up comments. Commands that stopped for approval: none

### 2026-10-19 — Review opencode's status analysis and record the roadmap

- date: 2026-10-19
- task/issue: no issue; review of opencode's project status and priority analysis, recorded as `_docs/roadmap.md`
- agent role: Orchestrator
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human pasted opencode's analysis and asked for agreements, disagreements and proposed changes, then asked to record the result as a working plan to review progress against. No key prompt file saved
- files changed: `_docs/roadmap.md` (new), `README.md` (link), this entry
- verification (tests run, reviewer verdict): checked opencode's claims against `_docs/planning-process.md`, `_docs/agent-kit/process.md`, `_docs/rubric.md`, `_docs/rubric-evidence.md`, `agent-kit.conf`, `.github/workflows/verify.yml`, the open issue list, #9, #26, #34 and recent CI runs (`55ad78c` success). Found the scope decision already made (2026-10-17) and the 7-point audit likely stale (Testing 1 and CI/CD 1 unconfirmed). No auditor run; tests not run
- human review (what I checked or corrected, or `none`): the human asked for the roadmap; the four open decisions in it are not yet answered. Commands that stopped for approval: none

### 2026-10-19 — Keep deadlines out of the roadmap

- date: 2026-10-19
- task/issue: no issue; follow-up to the roadmap entry above
- agent role: Orchestrator
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human decided that timelines and dates stay out of agent-facing docs because they can adversely affect the agents; the human controls timing. No key prompt file saved
- files changed: `_docs/roadmap.md` (deadline line replaced by "timing and scope trade-offs are the human's"; the deadline decision row removed), this entry
- verification (tests run, reviewer verdict): `git diff --check` clean; no tests run (docs only)
- human review (what I checked or corrected, or `none`): the human declined a proposed deadline edit, then approved this wording. Commands that stopped for approval: none

### 2026-10-19 — Link the roadmap from AGENTS.md

- date: 2026-10-19
- task/issue: no issue; follow-up to the roadmap entries above
- agent role: Orchestrator
- model: Claude Code, claude-opus-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human approved the proposed one-line addition to `AGENTS.md` "Where to read more". No key prompt file saved
- files changed: protected `AGENTS.md` (commit `2efa508`, committed alone with `HUMAN_APPROVED=1`), this entry
- verification (tests run, reviewer verdict): `git diff --check` clean; no tests run (docs only)
- human review (what I checked or corrected, or `none`): the human approved the exact line shown in the session before it was written. Commands that stopped for approval: the `HUMAN_APPROVED=1 git commit` (intended)

### 2026-10-19 — Implement issue #13 README problem, functionality and expected behaviour

- date: 2026-10-19
- task/issue: issue #13, "README: describe the problem, functionality and expected behaviour (Problem Description, 1 → 2 points)" (groomed; PM comment made no repo changes and asked whether to file a follow-up for post-implementation README work)
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, `_docs/agent-kit/team/software-engineer.md`, `_docs/agent-kit/procedures/verify.md`, issue #13 and its latest PM comment, change only `README.md`, run Verify, commit with explicit paths, and append this entry; no key prompt file saved
- files changed: commit `1a000c2` (`README.md` only): added "The problem", "What VulnTriage does" and "Expected behaviour" sections, an explicit planning/not-implemented note, and expanded OSV.dev, CISA KEV, FIRST EPSS, LLM, MCP and n8n on first use; kept the planning and AI-workflow index. This entry in `_docs/ai-usage-log.md` (project rule). Git-ignored `.scratch/issue-13.json`, `.scratch/check_readme_13.py`
- verification (tests run, reviewer verdict): `make verify` before the log entry (README diff identical to `1a000c2`) PASS WITH WARNINGS: tests 2 files / 35 tests passed, whitespace PASS, weakened tests 7 rewritten assertions that predate this task (issue #22 test changes already in the unpushed range; this task changed no test). `.scratch/check_readme_13.py` PASS: every relative link resolves and all three required headings and fixed names are present. No QA run
- human review (what I checked or corrected, or `none`): none yet; issue left open for QA. Commands that stopped for approval: none

### 2026-10-20 — Close out issue #13

- date: 2026-10-20
- task/issue: issue #13, "README: describe the problem, functionality and expected behaviour (Problem Description, 1 → 2 points)"
- agent role: Orchestrator
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to check `_docs/roadmap.md` and start the next issue following `_docs/agent-kit/process.md`; no key prompt file saved
- files changed: `_session-summaries/issue-013-readme-problem-description.md` (new), `_docs/roadmap.md` (step 2 status and check-in line), this entry. Implementation `1a000c2` and the Engineer's log entry `e46fadf` were made by the Engineer
- verification (tests run, reviewer verdict): PM grooming, Engineer implementation and QA PASS were separate subagent runs. QA ran `make verify BASE=1be4f95` PASS (35 tests, whitespace PASS, no test files changed) and `make assert-clean` PASS at `e46fadf`. The orchestrator re-ran `make assert-clean` and confirmed HEAD stayed `e46fadf`. No auditor run
- human review (what I checked or corrected, or `none`): the human answered the decision point: do not file a README follow-up now, and no action on QA's minor findings. The roadmap records that step 2 started ahead of step 1 at the human's request. Commands that stopped for approval: none

### 2026-10-20 — Rubric evidence re-audit (roadmap step 1)

- date: 2026-10-20
- task/issue: roadmap step 1, "Refresh the rubric evidence"; re-audit `_docs/rubric.md` at HEAD `74e9cfc`
- agent role: Rubric Evidence Auditor
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md` and `.opencode/agents/rubric-auditor.md`, re-audit at HEAD `74e9cfc`, confirm Testing 1 (35 cases and passing), CI/CD 1 (`verify.yml` runs the tests on every PR) and Problem Description 2 (README after #13), open every linked file or output, update only `_docs/rubric-evidence.md` and append this entry; no key prompt file saved
- files changed: `_docs/rubric-evidence.md` (rewritten with the 2026-10-20 audit), this entry. No code or other file changed; not committed (orchestrator reviews and commits)
- verification (tests run, reviewer verdict): opened `_docs/rubric.md`, `README.md` at `74e9cfc`, `_docs/specs.md`, `_docs/agent-team.md`, `_docs/agent-kit/process.md`, `AGENTS.md`, `Makefile`, `agent-kit.conf`, `.github/workflows/verify.yml`, both frontend test files, `frontend/src/services/index.ts` and `mockService.ts`. Ran `make test`: 2 files / 35 tests passed (34 in `vulntriage.test.tsx` + 1 in `app-routing.test.tsx`). `gh run view 39344215807 --log` showed the verify workflow ran `make verify`, then "Tests (make test)", 35 passed and "VERIFY: PASS"; the run at `1be4f95` concluded `success`. `gh repo view`, `gh issue list`, `gh issue view 1`, `gh issue view 2`, `gh issue view 13`, `git ls-files`, `git show` and `gh pr list` confirmed the public tracker, the acceptance criteria and role comments, no backend/database/container/deploy/telemetry/alert/responder files, and no pull requests. Audited score 10/24 (was 7). Verdicts: Testing 1 CONFIRMED (PARTIAL 1); CI/CD 1 CONFIRMED (PARTIAL 1, no CD); Problem Description 2 CONFIRMED (MET 2). Criteria changed since 2026-10-17: Testing 0 -> 1, CI/CD 0 -> 1, Problem Description 1 -> 2. Other criteria unchanged: Application 0, Containerization 0, Deployment 0, Observability 0, Alerting 0, On-Call 0; Product Specification, Agent Team and Context Management remain 2
- human review (what I checked or corrected, or `none`): none yet; orchestrator to review and commit. Commands that stopped for approval: none

### 2026-10-20 — Roadmap check-in; groom #35 and #33

- date: 2026-10-20
- task/issue: roadmap steps 1, 2 and 6; grooming of #35 and #33. The roadmap step 6 grooming (#3-#8) was already posted before this session and was verified, not redone
- agent role: Orchestrator, with a Rubric Evidence Auditor subagent and two PM subagents
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked whether #13 and step 6 were done, then approved starting step 1, grooming #35/#33 in parallel and updating the step 6 roadmap status. No key prompt file saved
- files changed: `_docs/roadmap.md` (commit `c15e4db`: steps 1-2 `done`, step 6 `doing` pending the batched decision, check-in line). Auditor commit `639b9a9` (`_docs/rubric-evidence.md`, `_docs/ai-usage-log.md`); the auditor's entry says "not committed", which its own commit `639b9a9` supersedes. Session summary `_session-summaries/planning-2026-10-20-rubric-refresh-and-grooming.md` and this entry. GitHub: PM rewrote and commented on #35 and #33; PM filed #36 (top-level agent-kit duplicate) and #37 (Claude Code settings asks). #17/#18 were groomed by another session at 00:29 UTC, not by this one
- verification (tests run, reviewer verdict): auditor ran `make test` (2 files, 35 tests passed) and read CI run 39344215807 (`success`); audited score 10/24 and confirmed Testing 1, CI/CD 1 and Problem Description 2. Orchestrator ran `make verify` after the roadmap edit: PASS WITH WARNINGS (35 tests, whitespace PASS, 7 pre-existing assertion rewrites from #22). `git diff --check` clean. No QA run for the grooming
- human review (what I checked or corrected, or `none`): none yet. Open: the batched #3-#8 decision, PM's two questions on #35 and one on #33, and whether PM should have filed #36/#37 before asking. Commands that stopped for approval: none

### 2026-10-20 — Implement issue #35 push-check plan mode

- date: 2026-10-20
- task/issue: issue #35, "Push check: plan mode (AGENT_PUSH_CHECK_PLAN=1) completes the push without checking (High)". Grooming answers applied: Q1 fix only `_docs/agent-kit` (top-level duplicate left to #36); Q2 plan mode blocks every push, including no-op, deletion-only and no-project pushes
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, `_docs/agent-kit/team/software-engineer.md`, `_docs/agent-kit/procedures/verify.md`, issue #35 and its comments (PM grooming plus the human's answers), implement the acceptance criteria, leave the protected changes uncommitted for human approval, run Verify, post an Engineer comment and append this entry; no key prompt file saved
- files changed: protected `_docs/agent-kit/environments/local-sandbox/pre-push` and `_docs/agent-kit/environments.md`, left uncommitted pending the human's approval of the exact diff; this entry in `_docs/ai-usage-log.md`. Git-ignored `.scratch/test-push-check-plan.sh` (evidence harness), `.scratch/pre-push-original` (pre-change hook for the non-plan comparison) and `.scratch/push-check-plan-results.txt` (harness output)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS: 2 test files / 35 tests passed, whitespace PASS, weakened tests 7 removed assertion lines that predate this issue (earlier unpushed frontend test changes; this issue changed no test files). `.scratch/test-push-check-plan.sh`: 10 cases, 0 failures (plan line per project, install/install::/none/comment/reinstall detection, working tree versus pushed commit, root fallback, no-new-commits, deletion-only, no-project, removed config, and non-plan byte-for-byte comparison against the original hook for unset/0/other and a failing gate). The sandbox denies `git push`, so the harness invoked the hook directly with git's pre-push stdin and recorded the local bare remote's refs before and after
- human review (what I checked or corrected, or `none`): none yet; the protected diff and its commit await the human's approval, and the human still needs to reinstall the hook in the clean clone and confirm with `cmp`. Commands that stopped for approval: none

### 2026-10-20 — Engineer proposal for issue #17 committed-alone check

- date: 2026-10-20
- task/issue: issue #17, "Pre-commit check: HUMAN_APPROVED=1 does not enforce \"committed alone\" for protected changes"; propose-only because `_docs/agent-kit/scripts/check-staged.sh` is protected
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, `_docs/agent-kit/team/software-engineer.md`, `_docs/agent-kit/procedures/verify.md` and #17, write the exact diff without editing protected files, test a copy in `.scratch/`, and post an Engineer comment; no key prompt file saved
- files changed: no tracked file; the proposed diff was returned to the orchestrator and is posted in Engineer comment 6280738052. Git-ignored `.scratch/test-check-staged.sh` and `.scratch/issue-17-repo` held the harness. This entry was appended by the orchestrator
- verification (tests run, reviewer verdict): throwaway-repo matrix 9/9 PASS (six required cases, both rename directions, forbidden `.env`, whitespace); `make verify BASE=1d31aac` PASS (35 tests, whitespace PASS) on the unmodified tree. The proposal was not applied by this role
- human review (what I checked or corrected, or `none`): the human approved the exact diff in this session; the orchestrator applied it and committed `64308d7`. Commands that stopped for approval: none

### 2026-10-20 — QA for issue #17

- date: 2026-10-20
- task/issue: issue #17, committed state
- agent role: QA Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to check #17 against its criteria at the committed state, run Verify and the throwaway matrix, and post a QA verdict; a re-check was requested after a concurrent session moved HEAD; no key prompt file saved
- files changed: none. QA comments 6281018092 (at `64308d7`) and 6281387668 (re-check at `df72298`). This entry was appended by the orchestrator
- verification (tests run, reviewer verdict): PASS at both commits. `make verify BASE=1d31aac` PASS (35 tests, whitespace PASS, no weakened tests); matrix 12/12 in `.scratch/qa-17-recheck.sh`; `make assert-clean` PASS at `df72298`; script blob unchanged `3712882`
- human review (what I checked or corrected, or `none`): the human chose to file follow-ups #39 (quoted filenames) and #40 (repo-root paths). Commands that stopped for approval: none

### 2026-10-20 — Orchestrator close-out for issue #17

- date: 2026-10-20
- task/issue: issue #17, protected change commit and close-out
- agent role: Orchestrator
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human chose roadmap step 6, answered the batched #3-#8 decisions, chose script-only enforcement for #17, and approved the exact protected diff; no key prompt file saved
- files changed: `_docs/agent-kit/scripts/check-staged.sh` (commit `64308d7`, protected, committed alone with `HUMAN_APPROVED=1` after approval); approval record comment 6280810952; `_session-summaries/issue-017-committed-alone.md` (commit `199f4b7`); this entry; issues #38, #39 and #40 filed by PM. No other repository change
- verification (tests run, reviewer verdict): QA PASS at `df72298`; `make verify BASE=1d31aac` PASS; `make assert-clean` PASS; approval record matches `git show` and blob `3712882`. The first QA run overlapped with the concurrent #35 session and was re-run at the stable HEAD after the human paused that session
- human review (what I checked or corrected, or `none`): the human approved the exact diff, chose script-only enforcement, chose to leave the duplicate folder for #38, approved filing #39/#40, and paused the concurrent orchestration. Commands that stopped for approval: none

### 2026-10-20 — Engineer proposal for issue #18 approval record

- date: 2026-10-20
- task/issue: issue #18, "Record human approvals of protected changes so the exact approved text can be confirmed"; propose-only because all four changed files are protected
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to read `AGENTS.md`, the engineer role, `verify.md`, #18 and its comments, draft the exact diffs without editing tracked files, check them against the criteria, and post Engineer comments; no key prompt file saved
- files changed: no tracked file; diffs returned to the orchestrator and posted in comments 6281798553 (three files) and 6281870795 (the template, after the human chose to include it). Drafts and checks in `.scratch/propose/`. This entry was appended by the orchestrator
- verification (tests run, reviewer verdict): `git apply --check` passed; all four paths match `PROTECTED`; `make verify BASE=ea257c9` PASS (35 tests, whitespace PASS); no docs tests exist, so the criterion check was a read of the drafted text
- human review (what I checked or corrected, or `none`): the human chose to include the template in the same protected commit and approved the exact four-file text; the orchestrator applied it and committed `efae1ea`. Commands that stopped for approval: none

### 2026-10-20 — QA for issue #18

- date: 2026-10-20
- task/issue: issue #18, committed state and its first approval record
- agent role: QA Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): Orchestrator instruction to check every criterion at `efae1ea`, compare the posted record with the stated `git show`, check paths/blob IDs/parent, run Verify and assert-clean, and post a QA verdict; no key prompt file saved
- files changed: none. QA comment 6282208055. This entry was appended by the orchestrator
- verification (tests run, reviewer verdict): PASS. `make verify BASE=ea257c9` PASS (35 tests, whitespace PASS, no weakened tests); posted diff and `git show` output both 8394 bytes and `cmp` clean; `Paths` and all four blob IDs match; single parent; all four paths `PROTECTED`; refused cases rejected by the written rule; `make assert-clean` PASS at `efae1ea`
- human review (what I checked or corrected, or `none`): the QA notes outside the criteria are the documented documentation-only limit and an `index`-line difference in draft snippets; no action requested. Commands that stopped for approval: none

### 2026-10-20 — Orchestrator close-out for issue #18

- date: 2026-10-20
- task/issue: issue #18, protected docs commit and close-out
- agent role: Orchestrator
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human approved the four protected paths (including the template) and approved the exact diff; no key prompt file saved
- files changed: `AGENTS.md`, `_docs/agent-kit/procedures/asking-the-human.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/templates/AGENTS.md.template` (commit `efae1ea`, protected, committed alone with `HUMAN_APPROVED=1`); approval record comment 6282041221; `_docs/roadmap.md` (commit `8bc389e`: step 5 done, step 6 answers recorded, decisions 1 and 3 resolved); `_session-summaries/issue-018-approval-record.md` (commit `6b953f5`); this entry. No other repository change
- verification (tests run, reviewer verdict): QA PASS at `efae1ea`; `make verify BASE=ea257c9` PASS; `make assert-clean` PASS; its own approval record passed the diff, path, blob, parent and `PROTECTED` checks
- human review (what I checked or corrected, or `none`): the human chose to include the template and approved the exact diff; QA's outside-criteria notes need no action. Commands that stopped for approval: none

### 2026-10-20 — Engineer drafts for spec issues #3-#8

- date: 2026-10-20
- task/issue: issues #3, #6, #4, #5, #7, #8 (roadmap step 6), drafted as cumulative `_docs/specs.md` patches
- agent role: Software Engineer
- model: opencode/deepseek-v4.1-flash-free (project default in `opencode.json`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to draft each issue's spec change from its recorded batched answers without editing tracked files; no key prompt file saved
- files changed: no tracked file; patches in `.scratch/spec-draft/`; Engineer comments 6284843229 (#3), 6284856636 (#6), 6284857967 (#4), 6284859024 (#5), 6284863547 (#7), 6284865043 (#8). This entry was appended by the Claude Code orchestrator from those comments
- verification (tests run, reviewer verdict): each comment reports the patch applies cleanly in order and the cumulative scratch spec passes its checks
- human review (what I checked or corrected, or `none`): the human approved each exact diff before its commit. Commands that stopped for approval: none (all six comments)

### 2026-10-20 — Orchestrator commits for spec issues #3-#8

- date: 2026-10-20
- task/issue: roadmap step 6, six protected spec commits and approval records
- agent role: Orchestrator
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's approval of each exact spec diff; no key prompt file saved
- files changed: `_docs/specs.md` in `45f6fa6` (#3), `999fd88` (#6), `e52a07c` (#4), `e0a60ac` (#5), `b03539b` (#7), `fdc7b51` (#8), each committed alone with `HUMAN_APPROVED=1`; approval records 6285069644, 6285087536, 6285106147, 6285123424, 6285146604, 6285163520. This entry was appended by the Claude Code orchestrator; the OpenCode session stopped before logging
- verification (tests run, reviewer verdict): the record for #8 was compared with `git show` by a `.scratch/` script (PASS); every record was later re-checked by QA
- human review (what I checked or corrected, or `none`): approved each diff. Commands that stopped for approval: not collected, because the session was interrupted

### 2026-10-20 — QA for spec issues #3, #6 and #4

- date: 2026-10-20
- task/issue: issues #3, #6, #4
- agent role: QA Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to check each issue's criteria and approval record at its commit and post a verdict; no key prompt file saved
- files changed: none. QA comments 6285218980 (#3), 6285234570 (#6), 6286250358 (#4). This entry was appended by the Claude Code orchestrator
- verification (tests run, reviewer verdict): PASS for all three; `make verify` PASS (35 tests); approval records byte-identical to `git show`; each reports `make assert-clean` PASS at `fdc7b51`
- human review (what I checked or corrected, or `none`): outside-criteria risks went to the step 6 decision point (option 1, #41). Commands that stopped for approval: none

### 2026-10-20 — QA reruns for spec issues #5, #7 and #8

- date: 2026-10-20
- task/issue: issues #5, #7, #8; the OpenCode QA runs stopped before posting, so these are fresh runs
- agent role: QA Engineer
- model: claude-opus-5-5 (Claude Code `qa-engineer` subagent)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to check criteria and approval record, run Verify, not reuse the partial `.scratch/qa-5/`, and post a verdict; no key prompt file saved
- files changed: none. QA comments 6286739493 (#5), 6286726338 (#7), 6286723784 (#8)
- verification (tests run, reviewer verdict): PASS for all three; `make verify` with each parent as `BASE` PASS (35 tests); records byte-identical to `git show`; orchestrator `make assert-clean` PASS, HEAD `fdc7b51` unchanged
- human review (what I checked or corrected, or `none`): outside-criteria risks went to the step 6 decision point (option 1, #41). Commands that stopped for approval: none

### 2026-10-20 — PM follow-up #41 from the #3-#8 QA risks

- date: 2026-10-20
- task/issue: step 6 decision point, option 1
- agent role: PM
- model: claude-opus-5-5 (Claude Code `pm` subagent)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to file one groomed issue for the spec contradictions and gaps, list the Stage 2 details as step 7 inputs, and comment once on #23; no key prompt file saved
- files changed: no tracked file; created #41; comment 6286808327 on #23
- verification (tests run, reviewer verdict): none; #41 asks the human decisions D1-D4 before implementation
- human review (what I checked or corrected, or `none`): the human chose option 1. Commands that stopped for approval: none

### 2026-10-20 — Orchestrator close-out for spec issues #3-#8

- date: 2026-10-20
- task/issue: roadmap step 6 close-out after the OpenCode orchestrator stopped
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to finish the interrupted task; no key prompt file saved
- files changed: `_session-summaries/planning-2026-10-20-spec-review-3-8.md`, `_docs/roadmap.md` (step 6 done, #41 noted, check-in line), this log; closed #3-#8
- verification (tests run, reviewer verdict): checked the state left behind (clean tree, HEAD `fdc7b51`, no verdict on #5/#7/#8, no PID files); `make assert-clean` PASS after the QA reruns
- human review (what I checked or corrected, or `none`): the human chose option 1 at the decision point. Commands that stopped for approval: none

### 2026-10-20 — QA for issue #35 (first run)

- date: 2026-10-20
- task/issue: issue #35, committed state `df72298`
- agent role: QA Engineer
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to check every criterion and post a verdict; no key prompt file saved
- files changed: none. QA comment 6281291470. This entry was appended by the Claude Code orchestrator
- verification (tests run, reviewer verdict): FAIL on criterion 10 only (no approval comment); criteria 1-9, 11, 12 PASS; independent 83-check harness 0 failures; `make verify BASE=4454518` PASS
- human review (what I checked or corrected, or `none`): none. Commands that stopped for approval: none

### 2026-10-20 — Orchestrator close-out for issue #35

- date: 2026-10-20
- task/issue: issue #35 (roadmap step 3), after the OpenCode orchestrator stopped
- agent role: Orchestrator, with a QA Engineer re-check and a PM follow-up as Claude Code subagents
- model: claude-opus-5-5 (Claude Code); the earlier commit `df72298` and free-form note 6281324989 were made by the OpenCode orchestrator (opencode/deepseek-v4.1-flash-free)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to finish the interrupted session; no key prompt file saved
- files changed: approval record 6287006555 (built and checked by a `.scratch/` script against the approval request and `git show`); correction comment 6287127239; QA PASS 6287037242; PM created #42; `_session-summaries/issue-035-push-check-plan-mode.md`, `_docs/roadmap.md` (step 3 done, check-in line), this log; `make clean-scratch` ran; closed #35
- verification (tests run, reviewer verdict): QA re-check PASS (34 record checks, 0 failures; #35 paths unchanged since `df72298`; `make verify BASE=4454518` PASS); `make assert-clean` PASS at `48cbb9d`
- human review (what I checked or corrected, or `none`): the human approved the diff before `df72298` and chose option 1 at the decision point. Commands that stopped for approval: none

### 2026-10-20 — Review of the step 3/6 close-out commits and roadmap check-in

- date: 2026-10-20
- task/issue: roadmap check-in after `48cbb9d` and `b1ab1e5`
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to review the recent commits and update the roadmap; no key prompt file saved
- files changed: `_docs/roadmap.md` (unscheduled follow-ups #36-#40 and #42 placed under "Later", #38/#36 note, decision 4, score table from the 2026-10-20 audit, check-in line), this log
- verification (tests run, reviewer verdict): compared the roadmap with `gh issue list --state all`; `make verify` PASS WITH WARNINGS at `b1ab1e5` (35 tests; the removed-assertion warning comes from earlier frontend commits since `origin/main`)
- human review (what I checked or corrected, or `none`): none yet. Commands that stopped for approval: none

### 2026-10-20 — Roadmap reprioritised toward product work

- date: 2026-10-20
- task/issue: roadmap reshuffle after the human said the project was sidetracked by safeguards
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to weigh priorities toward VulnTriage itself, not the agent kit or dev container, and reshuffle the roadmap; no key prompt file saved
- files changed: `_docs/roadmap.md` (priority rule, `deferred` status, step 4 (#33) deferred to "Later", #41 opens step 7, decision 4 withdrawn, new off-track signal, check-in line), this log
- verification (tests run, reviewer verdict): none (documentation only)
- human review (what I checked or corrected, or `none`): the human set the direction; the edited roadmap is not yet reviewed. Commands that stopped for approval: none

### 2026-10-20 — Decisions for #41 and roadmap decision 2

- date: 2026-10-20
- task/issue: #41 D1-D4 and roadmap decision 2 (#31)
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for more context to make the decisions; no key prompt file saved
- files changed: comments 6287579005 (#41) and 6287579525 (#31); `_docs/roadmap.md` (decision 2 resolved, step 16 unblocked, check-in line), this log
- verification (tests run, reviewer verdict): none (decisions recorded only)
- human review (what I checked or corrected, or `none`): the human chose option 1 for D1, D2, D3 and decision 2 in a multiple-choice question; D4 unanswered. Commands that stopped for approval: none
- follow-up, same day: the human chose D4 option 1 (the recommended status line); recorded in #41 comment 6287964999

### 2026-10-20 — #41 step 3: proposed spec diff

- date: 2026-10-20
- task/issue: #41 lifecycle step 3 (implementation as a proposed diff to the protected `_docs/specs.md`)
- agent role: Engineer (subagent of the orchestrator)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's step 3 task: draft D1-D4 (option 1 each) and D5 option 1 against the PM's groomed criteria (comment 6288008663) in a scratch copy, without editing or committing the spec; no key prompt file saved
- files changed: none tracked except this log. Scratch only: `.scratch/spec-41/specs.md` (draft), `.scratch/spec-41/specs-41.patch` (headers retargeted to `_docs/specs.md`), `.scratch/spec-41/check_41.py` (read-only check), `.scratch/spec-41/comment-41.md`; Engineer comment 6288084947 on #41 with the full diff
- verification (tests run, reviewer verdict): `check_41.py` 61/61 automated checks pass, plus a manual read of the status-setting sentences and external-claim lines it prints; `git apply --check` on the patch passes; `make verify` PASS WITH WARNINGS (35 tests; the removed-assertion warning comes from earlier frontend commits since `origin/main`). No QA or human review yet
- human review (what I checked or corrected, or `none`): none yet; D5 (`repository unavailable`) awaits the human at diff approval. Commands that stopped for approval: none

### 2026-10-20 — #41 protected spec commit and approval record

- date: 2026-10-20
- task/issue: #41, after the human approved the exact diff
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human approved the diff as shown and chose D5 option 1; no key prompt file saved
- files changed: `_docs/specs.md` in `1445ca5`, committed alone with `HUMAN_APPROVED=1`; approval record comment 6288541138; this log
- verification (tests run, reviewer verdict): the applied diff was compared byte for byte with the approved patch before staging (`cmp`, identical), and again after the commit by `.scratch/spec-41/build_record.py` (one parent, only `_docs/specs.md`, `git show` identical to the patch); QA not yet run
- human review (what I checked or corrected, or `none`): approved the exact diff and D5 option 1. Commands that stopped for approval: none

### 2026-10-20 — QA and close-out for #41

- date: 2026-10-20
- task/issue: #41 lifecycle steps 4-9
- agent role: QA Engineer (Claude Code `qa-engineer` subagent), then Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to check the groomed criteria and the approval record, run Verify with `BASE=c77a437`, and post a verdict; no key prompt file saved
- files changed: QA comment 6288587511; decision-point comment 6289212246; `_session-summaries/issue-041-spec-fixes-from-qa-risks.md` (`71aa176`); `_docs/roadmap.md` (step 7 doing, check-in line), this log; `make clean-scratch` ran; closed #41
- verification (tests run, reviewer verdict): QA PASS (own script 81/82, the one miss a gap in its prefix list, cross-checked); `make verify BASE=c77a437` PASS (35 tests); `make assert-clean` PASS at `6a33ba0`, HEAD unchanged
- human review (what I checked or corrected, or `none`): at the decision point the human chose to send QA risks 1-3 to the step 7 issue. Commands that stopped for approval: none

### 2026-10-20 — Plan for Claude Code cloud sessions

- date: 2026-10-20
- task/issue: none (human request: plan how to use Claude Code cloud sessions for this project)
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code), with a `web-fetch` subagent reading the Claude Code on the web and cloud environments docs
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for the most efficient method, the repo adjustments and step-by-step instructions in `_docs`; no key prompt file saved
- files changed: `_docs/cloud-sessions.md` (new; proposal, protected-file changes listed but not made), this log
- verification (tests run, reviewer verdict): none; the doc marks undocumented details `VERIFY:` for a trial session. Repo facts checked: `.claude/settings.json` denies `git push *`, `guard_git.py` blocks push, `make issue-dump` uses `gh issue view`, CI uses the runner's default Node
- human review (what I checked or corrected, or `none`): none yet. Commands that stopped for approval: none
- follow-up, same day: the human chose not to depend on cloud credit; `_docs/cloud-sessions.md` is marked an optional, deferred reference

### 2026-10-20 — Docker options and the human-in-the-loop runbook

- date: 2026-10-20
- task/issue: none directly (feeds step 7 D1 and #31); human request for the cost of Docker in the sandbox, then step-by-step instructions for the human
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for a technical cost breakdown, chose option A (Compose service containers, agent has no Docker control), and asked for instructions for the human who runs containers outside the sandbox; no key prompt file saved
- files changed: `_docs/docker-runbook.md` (new), `_docs/cloud-sessions.md` (status line), this log
- verification (tests run, reviewer verdict): none (documentation). Facts checked: the repo is public (`gh repo view`), the agent token can read Actions runs (`gh run list`), `verify.yml` runs on every push. Setup hours are estimates, not measured
- human review (what I checked or corrected, or `none`): the human chose option A. Commands that stopped for approval: none

### 2026-10-20 — Step 7 issue proposal and creation (#43)

- date: 2026-10-20
- task/issue: roadmap step 7, second part
- agent role: PM (Claude Code `pm` subagent) for the proposal; Orchestrator for creation
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to propose, not create, the Stage 2 issue from the Stage 2 checklist, #9, #41's inputs and QA risks, #31 and #23; no key prompt file saved
- files changed: created #43 from the PM's draft (title line removed); comment 6289876616 with the human's answers; `_docs/roadmap.md` (step 7 row, check-in line), this log
- verification (tests run, reviewer verdict): none; the PM mapped every input (I1-I17, R1-R3, #9 rows) to a criterion or an out-of-scope line
- human review (what I checked or corrected, or `none`): the human approved creating the issue, and chose D1 option 1 (in the Docker discussion), D2 option 1 and the PM's recommendations for D3-D8. Commands that stopped for approval: none (PM and orchestrator)

### 2026-10-20 — #43 Part 1: proposed spec diff

- date: 2026-10-20
- task/issue: #43 Part 1 (the `_docs/specs.md` diff only; `architecture.md` not started)
- agent role: Engineer (Claude Code `software-engineer` subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to draft the Part 1 spec diff in `.scratch/` from #43's criteria and the human's answers (comment 6289876616: D1, D2 and D3-D8 option 1), check it with one script and post it; no key prompt file saved
- files changed: none committed; drafts in `.scratch/spec-43/` (`specs.md`, `specs-43.patch`, `check_spec_43.py`); comment https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6290123115; this log
- verification (tests run, reviewer verdict): `.scratch/spec-43/check_spec_43.py` 43/43 PASS (includes `git apply --check`, hunk locations, `VERIFY:` on new external claims, status/scan status/reason/KEV consistency). No reviewer verdict yet
- human review (what I checked or corrected, or `none`): the human approved the first diff except uncovered choice 3, and decided that a reinstated `withdrawn` finding restores its pre-withdrawal status (`risk accepted` or `open`). Commands that stopped for approval: none
- revision, same day: changed hunks 4 (`open` and `withdrawn` rows) and 7 (E4) for that decision, stated as restoring the human's recorded acceptance rather than a new one; the patch now carries `index 2d02ddc..782a27c 100644`; check script 48/48 PASS; revised diff posted in https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6290358382, awaiting approval of the exact revised diff

### 2026-10-20 — #43 Part 1 protected spec commit and approval record

- date: 2026-10-20
- task/issue: #43 Part 1, after the human approved the exact revised diff
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human approved the revised diff (6290358382) without the optional `risk accepted` row clause; no key prompt file saved
- files changed: `_docs/specs.md` in `faea412`, committed alone with `HUMAN_APPROVED=1`; approval record comment 6290689973; this log. Before review I added only an `index` header line to the first draft's patch, which the Engineer's script later regenerated
- verification (tests run, reviewer verdict): the applied diff was `cmp`-identical to the approved patch before staging; after the commit, `.scratch/spec-43/build_record.py` confirmed one parent, only `_docs/specs.md`, and `git show` identical to the patch. QA runs after Part 2
- human review (what I checked or corrected, or `none`): approved the exact revised diff. Commands that stopped for approval: none

### 2026-10-20 — #43 Parts 2 and 3: architecture.md and README link

- date: 2026-10-20
- task/issue: #43 Parts 2 and 3 (Stage 2 `_docs/architecture.md`, README link, stage report)
- agent role: Engineer (Claude Code `software-engineer` subagent)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instruction to write `architecture.md` to #43's Part 2 criteria and Stage 2, against the spec at HEAD (`faea412`) and the human's answers (comment 6289876616), check it with one script, run Verify and post the stage report; no key prompt file saved
- files changed: `_docs/architecture.md` (new) and `README.md` (one link) in `072c17e`; check script `.scratch/arch-43/check_arch_43.py`; comment https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6290918784; this log (not committed by me)
- verification (tests run, reviewer verdict): check script 25/25 PASS; `make verify BASE=e15bf29` PASS (35 frontend tests passed, whitespace PASS, no weakened tests). No web fetches: every unconfirmed external detail is tagged `VERIFY:`. No QA verdict yet
- human review (what I checked or corrected, or `none`): none yet. Three spec notes raised for the human (US-4 KEV value before the first KEV fetch, E10 for versionless lockfile entries, stale mark for every `scan failed` reason). Commands that stopped for approval: none
- second spec diff, same day: after the human decided the three spec notes (comment 6291276406), drafted `.scratch/spec-43b/specs-43b.patch` (`index 782a27c..c034181`, 4 hunks, +14 / -9; `git apply --check` passes; `.scratch/spec-43b/check_spec_43b.py` 18/18 PASS) and edited `_docs/architecture.md` in the working tree (A7, A12, A14 now cite the spec; architecture check 25/25 PASS), neither committed; posted in https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6291326008, awaiting approval of the exact diff. Commands that stopped for approval: none

### 2026-10-20 — #43 second spec commit and architecture touch-up

- date: 2026-10-20
- task/issue: #43, the Engineer's three spec notes, before QA
- agent role: Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human chose KEV option A, approved fixing all three notes before QA as a second spec commit (criteria change recorded in 6291276406), then approved the exact diff (6291326008); no key prompt file saved
- files changed: `_docs/specs.md` in `3ecd54b`, committed alone with `HUMAN_APPROVED=1`; approval record 6291380101; `_docs/architecture.md` in `631706e` (A7, A12, A14 cite the spec); this log
- verification (tests run, reviewer verdict): the applied diff was `cmp`-identical to the approved patch before staging; after the commit, `.scratch/spec-43b/build_record.py` confirmed one parent, only `_docs/specs.md`, and `git show` identical to the patch. QA next
- human review (what I checked or corrected, or `none`): approved the decisions, the criteria change and the exact diff. Commands that stopped for approval: none

### 2026-10-20 — #43 QA FAIL fix: types.ts differences table

- Engineer (Claude Code `software-engineer` subagent, claude-opus-5-5), after QA FAIL 6291494669: completed the Data model differences table against `frontend/src/services/types.ts` field by field, changed the spec version on line 3 to `3ecd54b`, and made the US-14 rule `max by (finding_id, tier)` to match its text; `_docs/architecture.md` only, in `974c3f6`. Check script 26/26 PASS (added a check that every `specs.md` commit since the base touches only that file); `make verify BASE=16b445b` PASS. Comment https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6291539799. QA re-check not yet run. Commands that stopped for approval: none
- after QA re-check FAIL 6291613521: added the briefs, Scan and Dependency rows, corrected the `affectedRanges` row and the `ServiceErrorCode` 403 citations, made the `epss` row "the score only", and added the server-side-fields rule line after an entity-by-entity pass; `_docs/architecture.md` only, in `6e83ce2`. Check script 26/26 PASS; `make verify BASE=16b445b` PASS. Comment https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6291652743. QA re-check not yet run. Commands that stopped for approval: none
- at the decision point, the human chose "no repeat" for the US-14 alert: removed the 24-hour repeat interval (the notification policy never re-sends while unresolved, with `VERIFY:` on the Grafana setting), added that chasing an overdue finding is US-9's reminders and escalation, and dropped the repeat from A33; `_docs/architecture.md` only, in `4180fe3`. Check script 26/26 PASS; `make verify BASE=16b445b` PASS. Comment https://github.com/andrew-chung-au/vuln-triage/issues/43#issuecomment-6301770281. Commands that stopped for approval: none

### 2026-10-20 — QA and close-out for #43

- date: 2026-10-20
- task/issue: #43 lifecycle steps 4-9 (roadmap step 7)
- agent role: QA Engineer (four fresh Claude Code `qa-engineer` runs), then Orchestrator
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator instructions to check the criteria (then only what changed) and post a verdict; the human's decision-point answers; no key prompt file saved
- files changed: QA comments 6291494669 (FAIL), 6291613521 (FAIL), 6291706212 (PASS), 6301808583 (PASS, alert change); decision-point comment 6301818549; #23 comment 6301758496; #9 body (five boxes ticked) and comment 6301823825; #31 comment 6301824334; `_docs/roadmap.md` (step 7 done, leftovers, check-in line), this log, and the session summary; `make clean-scratch` ran; closed #43
- verification (tests run, reviewer verdict): QA PASS; `make verify BASE=16b445b` PASS (35 tests) in every QA run; `make assert-clean` PASS after each QA run (`e8ce1be`, `741489a`, `4b90629`, `6dd32e6`); the #9 body edit was checked by `.scratch/tick_9.py` to change exactly five lines
- human review (what I checked or corrected, or `none`): the human accepted the Engineer's design choices as assumptions, chose no alert repeat, and chose to record the leftovers on #23 and the roadmap. Two tool calls failed with a transient permission-check error and were retried after the human said to continue. Commands that stopped for approval: none

### 2026-10-21 — #23 OpenAPI contract and Stage 3 API table

- date: 2026-10-21
- task/issue: #23 (contract, Stage 3 table, approved Stage 3 text, README links)
- agent role: Engineer (OpenCode `software-engineer` run)
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for issue #23 against its groomed body and comment 6305987033 (D1-D5 all option 1), with the validator left unrun and its Makefile target supplied as a diff; no key prompt file saved
- files changed: `_docs/openapi.yaml` (new) in `7d6fe6e`, `_docs/api.md` (new) in `3bdc565`, the exact approved Stage 3 text in `_docs/planning-process.md` alone in `dc94837`, and the two README links in `49a296f`; this log. The proposed protected `Makefile` target is unapplied in `.scratch/makefile-target.diff`; it applies cleanly with `git apply --check`
- verification (tests run, reviewer verdict): `.scratch/check_api.cjs` ALL CHECKS PASS (operation set, operationIds, path parameters, security/CSRF, response sets, enums, required keys, forbidden server-side names, api.md coverage, exact Stage 3 text, README links). `make verify` VERIFY: PASS WITH WARNINGS (35/35 frontend tests; whitespace PASS; 7 removed assertions, all from the unpushed #22 commit `759735a`, not from this docs-only issue). The OpenAPI validator was not run: its target needs the human's approval. No reviewer verdict yet
- human review (what I checked or corrected, or `none`): none yet. Awaiting approval for the `openapi-validate` Makefile target and human review of `_docs/openapi.yaml`. Commands that stopped for approval: none

### 2026-10-21 — Permission review: record actions, not outcomes

- date: 2026-10-21
- task/issue: direct human request to correct the permission-review rule; no issue
- agent role: Orchestrator (OpenCode)
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to review how permission requests are recorded in session summaries, then directed that the agent must not record whether permission was granted, only the actions that required asking; no key prompt file saved
- files changed: `1b37fd1` (protected, HUMAN_APPROVED=1; approved in this session): `AGENTS.md` and seven `_docs/agent-kit/` files; this log and `_session-summaries/planning-2026-10-21-permission-review.md`
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (35/35 frontend tests; whitespace PASS; 7 removed assertions from the earlier unpushed #22 test rewrite, not this docs-only change); `git diff --check` clean. No QA verdict (direct docs change)
- human review (what I checked or corrected, or `none`): approved the exact eight-file diff in this session. Commands and changes that required approval, outcomes not recorded: editing the eight protected paths (`edit` `ask` rules); the `HUMAN_APPROVED=1` commit (merits); `gh issue edit 23` by the PM (`gh issue edit*` `ask` rule)

### 2026-10-21 — #23 contract follow-up: A-N review decisions

- date: 2026-10-21
- task/issue: #23 (contract follow-up from the senior review comment 6307744446 and body comment 6307825934)
- agent role: Engineer (OpenCode `software-engineer` run)
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator relayed the A-N items, the instruction not to edit the Makefile or run the validator, and item O's revised-target requirements; no key prompt file saved
- files changed: `_docs/openapi.yaml` in `3cb40af` (A, B, C, F, G, H, I, J, L, M, N) and `_docs/api.md` in `d9817f9` (A, B, F, G, H, I, K, and the contract-order wording); this log. The revised protected-target diff is unapplied in `.scratch/makefile-target.diff`; it applies cleanly with `git apply --check`
- verification (tests run, reviewer verdict): `.scratch/check_api.cjs` ALL CHECKS PASS, including the ten-operation set, 403 on registerAsset/reScan, the 401 -> 403 CSRF -> 404 -> 403 owner -> 422 -> 409 order and its refused case, strict request bodies, the FindingId/AssetId parameter refs, the tightened repositoryUrl pattern and its refused cases, required nullable actorDisplayName, epss bounds, ownerEmail format, and the api.md pagination/owner-match rows. `make verify BASE=5a41e30` VERIFY: PASS (35/35 frontend tests; whitespace PASS; no test files changed). The default `make verify` gave PASS WITH WARNINGS: 35/35 tests, whitespace PASS, and 7 removed assertions from the earlier unpushed #22 commit `759735a`, not from this docs-only change. The validator was not run: the target still needs the human's approval. The proposed target pins `openapi-spec-validator==0.9.0`, checked on the PyPI project page on 2026-10-21 (release 0.9.0, uploaded 2026-05-20)
- human review (what I checked or corrected, or `none`): none yet. Awaiting the human's approval of the revised target diff and review of `_docs/openapi.yaml` at `3cb40af`. Commands that stopped for approval: none

### 2026-10-21 — #23 approved `openapi-validate` target and validator runs

- date: 2026-10-21
- task/issue: #23 (apply the approved revised target, post its approval record, run the validator and refusal cases, run Verify)
- agent role: Engineer (OpenCode `software-engineer` run)
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator relayed the human's 2026-10-21 approval of the revised target diff at `.scratch/makefile-target.diff` and of running the validator on the real file and the broken-`$ref` case; no key prompt file saved
- files changed: the protected `Makefile` in `aa066fc19047042595e252ebbcfd9914955814bb`, committed alone with `HUMAN_APPROVED=1`; approval record https://github.com/andrew-chung-au/vuln-triage/issues/23#issuecomment-6308646350; Engineer comment https://github.com/andrew-chung-au/vuln-triage/issues/23#issuecomment-6308754845; this log. No changes to `_docs/openapi.yaml`, `_docs/api.md` or any test
- verification (tests run, reviewer verdict): `git apply --check .scratch/makefile-target.diff` passed before applying; the posted approval-record diff was checked byte-identical to `git show --format= --no-renames --patch aa066fc19047042595e252ebbcfd9914955814bb -- Makefile`. `make openapi-validate` on `_docs/openapi.yaml` exited 0 with `_docs/openapi.yaml: OK`; on `.scratch/openapi-broken-ref2.yaml` (one broken response `$ref`) exited 2; on `OPENAPI=../x.yaml` exited 2 at `Makefile:59` before the validator ran. Noted: `openapi-spec-validator 0.9.0` did not catch a broken `$ref` placed in a request-body schema (`.scratch/openapi-broken-ref.yaml`, exit 0), so the recorded refusal case uses a response `$ref`. `make verify` over all unpushed work: VERIFY: PASS WITH WARNINGS, 35/35 frontend tests, whitespace PASS, 7 removed/rewritten assertions all from the unpushed #22 commit `759735a`, not this change. No reviewer verdict yet
- human review (what I checked or corrected, or `none`): the human approved the exact revised target diff and the validator runs in this session; the contract review at `3cb40af` is still pending. Commands that stopped for approval: `git apply .scratch/makefile-target.diff` (protected `Makefile`; merits); the `HUMAN_APPROVED=1` commit (protected-file commit; merits); `make openapi-validate` and `uvx openapi-spec-validator==0.9.0 --version` (validator download/run; merits); `cat` reads of project/issue files, `cp` into `.scratch/`, and the `.scratch` check scripts (matched the `*` ask rule)

### 2026-10-21 — Cloud-sessions readiness check and #44 filed

- date: 2026-10-21
- task/issue: status check of `_docs/cloud-sessions.md`; filed #44 for its section 3 repo changes
- agent role: main session (Claude Code, plan mode for the check and draft)
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked how much of `_docs/cloud-sessions.md` is implemented, then asked for an issue for section 3 if none existed; no key prompt file saved
- files changed: this log. Issue https://github.com/andrew-chung-au/vuln-triage/issues/44 created from `.scratch/issue-cloud-sessions.md`
- verification (tests run, reviewer verdict): read-only checks: section 3 is 0 of 5 done (`Makefile` `issue-dump` still uses `gh issue view`; `.claude/settings.json` has the blanket `git push` deny and no SessionStart hook; `guard_git.py` has no cloud exception; `cloud_session_start.sh` absent; `AGENTS.md` has no cloud profile). `gh api .../rulesets` shows "Protect Main Branch" with the planned rules but enforcement `disabled`; `gh api .../rules/branches/main` returns `[]`. GitHub `main` at `5a41e30`, 5 local commits behind `052f53a`. Repo merge-method settings not readable with the read-only token. `gh issue list --state all` found no existing issue for section 3. No tests run
- human review (what I checked or corrected, or `none`): the human approved the issue draft in plan mode before it was filed; #44's "Decision needed" (work now, after #23, or deferred) is open. Commands that stopped for approval: none recorded by this session beyond the plan approval

### 2026-10-21 — #23 decision point: approved AGENTS.md, spec and architecture changes

- date: 2026-10-21
- task/issue: #23 (apply three changes the human approved in this session, each in its own focused commit, and post the two protected-change approval records)
- agent role: Engineer (OpenCode `software-engineer` run)
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator relayed the human's 2026-10-21 in-session approval of the exact AGENTS.md Commands line, the three spec sentences (US-6, US-10, US-11) and the A30 sentence, plus the commit rules; no key prompt file saved
- files changed: protected `AGENTS.md` in `5b35ecee2d59bbc1db82fc49288e7166a528e79d`, committed alone with `HUMAN_APPROVED=1`; approval record https://github.com/andrew-chung-au/vuln-triage/issues/23#issuecomment-6309239012. Protected `_docs/specs.md` in `67a407638bc52f9337cfad5c4c841e3eb955cc24`, committed alone with `HUMAN_APPROVED=1`; approval record https://github.com/andrew-chung-au/vuln-triage/issues/23#issuecomment-6309240051. `_docs/architecture.md` in `525284b7fdc113f94691250fa3c82c1592c079ee`, a normal commit. This log
- verification (tests run, reviewer verdict): `git diff --check` was clean before each commit, and each staged tree contained only the named path. The posted Diff blocks were copied from `git show --format= --no-renames --patch <commit> -- <path>` for the same commit and path. `make verify`: VERIFY: PASS WITH WARNINGS (35/35 frontend tests; whitespace PASS; 7 removed or rewritten assertion lines, all from the unpushed #22 commit `759735a`, not this docs-only change). No reviewer verdict yet
- human review (what I checked or corrected, or `none`): the human approved the exact three changes in this session on 2026-10-21; there is no approval-comment URL. Commands and changes that required approval: editing the protected `AGENTS.md` and `_docs/specs.md` (`ask` rules for those paths, and human approval for protected files); the two `HUMAN_APPROVED=1` commits (protected-file commit, merits); `gh api repos/andrew-chung-au/vuln-triage/issues/comments/6308646350 --jq .body` (`gh api*` `ask` rule)

### 2026-10-21 — #23 decision point, close-out, and #44 scheduling

- date: 2026-10-21
- task/issue: #23 (orchestration from the senior review to close-out); #44 scheduling at the human's request
- agent role: main session (orchestrator), with PM, software-engineer and QA subagents
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to review the roadmap and work the next issue following `process.md`; mid-session they asked to schedule #44 after #23; no key prompt file saved
- files changed: `_docs/roadmap.md` in `13b0ee9` (#44 scheduling; check-in follows), `_session-summaries/issue-023-api-contract.md`, and this log. GitHub writes: comment 6308766939 (human's contract approval at `3cb40af`), comment 6309337943 (#44 scheduling) and the QA re-checks
- verification (tests run, reviewer verdict): QA PASS at `052f53a` (6309058776); the decision-point doc changes passed a re-check at `13b0ee9` (6310520840). `make assert-clean` PASS at `13b0ee9`; `make verify` PASS WITH WARNINGS (35/35 tests; the 7 warnings are from the unpushed #22 test rewrite)
- human review (what I checked or corrected, or `none`): the human approved the contract at `3cb40af`, the validator target and runs, the `AGENTS.md` line, all three spec sentences, the A30 note, one QA-risks follow-up (#46), filing #45, and scheduling #44 after #23. Commands that required approval: `gh issue comment` on #23 and #44 (writes to the record); the protected-file edits and `HUMAN_APPROVED=1` commits (merits requests); `make openapi-validate` (merits request)

### 2026-10-21 — #44 grooming, implementation and close-out

- date: 2026-10-21
- task/issue: #44 (cloud-session repo changes from `_docs/cloud-sessions.md` § 3); PM groomed it, the Engineer implemented it, QA checked it
- agent role: main session (orchestrator), with PM, software-engineer and QA subagents
- model: deepseek-v4.1-flash-free (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to groom #44, then to implement it; no key prompt file saved
- files changed: protected commit `8eeaf53` (`Makefile`, `.claude/settings.json`, `opencode.json`, `_docs/agent-kit/claude-code/hooks/guard_git.py`, new `_docs/agent-kit/claude-code/hooks/cloud_session_start.sh`, `AGENTS.md`), with approval record 6313318576; `_session-summaries/issue-044-cloud-sessions.md`, `_docs/roadmap.md` and this log. GitHub: grooming comment 6310709588, live `make issue-comment` test 6311435040, Engineer evidence 6314178652, QA 6314003194 (FAIL) and 6314208500 (PASS), follow-up #47
- verification (tests run, reviewer verdict): Engineer checks: guard matrix 30/30, SessionStart 7/7, settings 14/14, issue-target refusals 16/16, `make verify BASE=HEAD` PASS. QA FAILed only on two record-keeping criteria (the matrix and the live-comment URL were not in an issue comment); after the Engineer posted 6314178652, QA PASS at `8eeaf53` (6314208500). `make assert-clean` PASS
- human review (what I checked or corrected, or `none`): the human approved the exact six-file protected diff (one commit) and filing #47 for the four outside-criteria risks; they deferred the `_docs/cloud-sessions.md` notes to the § 5 trial follow-up. Commands that required approval: the protected-file edits and the `HUMAN_APPROVED=1 git commit` (merits requests); `make issue-comment` (GitHub write to the record); `gh issue create` for #47 (GitHub write)

### 2026-10-21 — Cloud-session readiness check and setup guide

- date: 2026-10-21
- task/issue: none (human question: are we ready to launch Claude Code cloud sessions after #23 and #44?)
- agent role: main session, no subagents except one web-fetch agent for the docs
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for a readiness check, then explicit settings, then to update `_docs/cloud-sessions.md` without duplication; no key prompt file saved
- files changed: `_docs/cloud-sessions.md` (status line; § 2 table now shows how #44 handles each difference; § 3 records what #44 implemented; § 4 split into 4.1-4.5 with the ruleset, pull request, GitHub connection and environment-form settings; § 5 adds author, `Claude-Session` trailer, `jq` and `HEAD:main` checks; § 6 adds the permission-mode note) and this log
- verification (tests run, reviewer verdict): read-only `gh api` checks: local `main` = GitHub `main` = `d49c2e0`; last three CI `verify` runs on `main` succeeded; ruleset 25525417 "Protect Main Branch" has the right rules but `enforcement: disabled` and admin bypass `always`; merge-method settings unreadable with the sandbox token (`null`). Doc facts checked against code.claude.com pages (claude-code-on-the-web, cloud-environments, web-quickstart) and `guard_git.py`. No tests run (docs only)
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: none beyond the `make *`/`gh api repos/*` allow rules (all `gh api` calls were reads)

### 2026-10-21 — Cloud-session trial (`_docs/cloud-sessions.md` § 5)

- date: 2026-10-21
- task/issue: none (the § 5 trial before real cloud work)
- agent role: a Claude Code cloud session on branch `claude/keen-allen-185yyr`, driven by the human with prompts drafted by the local main session; the local main session recorded the results
- model: local main session claude-opus-5-5 (Claude Code); the cloud session's model was not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): three trial prompts drafted in the local session (trial checks; empty commit and pushes; Docker follow-up); not saved as key prompts
- files changed: `_docs/cloud-sessions.md` (§ 5.1 results; resolved `VERIFY:` items for Node 22, `jq`, branch prefix, commit author and Docker Hub hosts; Docker and Postgres not running at start) and this log. Cloud session: empty commit `1c6286a` pushed to `claude/keen-allen-185yyr` (not merged); `.scratch/` files only in the cloud VM
- verification (tests run, reviewer verdict): reported by the cloud session and pasted by the human: banner printed; `make verify` PASS 35/35 on Node 22.22.0; `make issue-dump N=41` wrote both files; `core.hooksPath` = `.githooks`; author `Claude <noreply@anthropic.com>`, no `Claude-Session` trailer; branch push worked; `git push origin main` and `HEAD:main` refused by `guard_git.py` (GitHub ruleset not reached); Docker daemon not running, `service docker start` failed on `ulimit`, `sudo dockerd` worked and `hello-world` ran, then the daemon was stopped; Postgres service down. The local session read `.githooks/pre-push` to confirm an empty commit has nothing to verify
- human review (what I checked or corrected, or `none`): the human ran the trial and sent each prompt. Commands that required approval: none in the cloud session (it reported none, including its `sudo dockerd` start and stop, which the human's prompt named); none locally beyond the allow rules

### 2026-10-21 — Cloud-trial follow-ups (#48, #47 comment)

- date: 2026-10-21
- task/issue: #48 (new), #47 (comment)
- agent role: main session (orchestrator), no subagents
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human approved filing one Docker-start issue and a #47 comment, after changing the ruleset bypass to `For pull requests only`; no key prompt file saved
- files changed: GitHub: #48 created (draft criteria, D1/D2 for the human; not groomed), #47 comment 6315677576. Repo: `_docs/cloud-sessions.md` (§ 4.2 and § 5.1 follow-ups), `_docs/roadmap.md` (#48 note, check-in line) and this log
- verification (tests run, reviewer verdict): read-only `gh api` check: ruleset 25525417 `enforcement: active`, admin bypass `pull_request`. No tests run (docs and issues only)
- human review (what I checked or corrected, or `none`): the human approved filing #48 and the #47 comment, and changed the bypass themselves; D1/D2 on #48 not answered yet. Commands that required approval: `gh issue create` for #48 (GitHub write to the record); `make issue-comment N=47` (GitHub write to the record, under the `make *` allow rule)

### 2026-10-21 — #27 Engineer: n8n and MCP server API contract

- date: 2026-10-21
- task/issue: #27 (API contract: n8n and MCP server endpoints, Stage 3 part 2)
- agent role: Software Engineer subagent, launched by the orchestrator in a Claude Code cloud session on branch `claude/compassionate-hamilton-k90q3r`
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's Engineer task for #27, with the human's 2026-10-21 US-15 decision (responder moved to follow-up #50); role file `_docs/agent-kit/team/software-engineer.md`; no new key prompt saved
- files changed: `_docs/openapi.yaml` (commit `7355d8e616ef03fb7b9f8cc7b02e9c798c88ce53`: nine n8n/MCP operations, `n8nAuth`/`mcpAuth`, `getAsset` shared with MCP, new schemas, untrusted-text marks, `FindingFields` split), `_docs/api.md` (commit `d89597aa1285d9a5eceb155cb638c91c856a3361`: 19-row table, auth/authorization, check order, schemas, pagination, `types.ts` note, Stage 3 checklist linking #50, #27 wire decisions) and this log. GitHub: Engineer comment https://github.com/andrew-chung-au/vuln-triage/issues/27#issuecomment-6316040760
- verification (tests run, reviewer verdict): `make openapi-validate` exit 0; the same target on `.scratch/openapi-broken-ref.yaml` (one broken response `$ref`) exit 2; `.scratch/check_27.py` ALL PASS (operation set, allowlists by scheme, error codes, untrusted-field list, fixture absent, api.md table equals contract); `make verify BASE=950dcbe` PASS (35/35 tests, whitespace PASS, no test files changed). Runtime refused cases are #24's. No reviewer verdict yet
- human review (what I checked or corrected, or `none`): none yet; the human's review of `_docs/openapi.yaml` at `7355d8e616ef03fb7b9f8cc7b02e9c798c88ce53` is pending (orchestrator). Commands that required approval: none (no `ask` rule matched; no merits request)

### 2026-10-21 — #27 Engineer: cveId untrusted mark and MCP overview fix

- date: 2026-10-21
- task/issue: #27 (two gaps from QA comment 6316919374, fixed by the human's choice after QA PASS)
- agent role: Software Engineer subagent, launched by the orchestrator in a Claude Code cloud session on branch `claude/compassionate-hamilton-k90q3r`
- model: claude-opus-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task to mark `cveId` untrusted and fix the overview text on MCP untrusted fields; no new key prompt saved
- files changed: `_docs/openapi.yaml` (commit `e74b2d18366016d0c6e018766e7e65c20d454a96`: `FindingFields.cveId` description marked untrusted; overview names `vulnerabilityId`, `aliases`, `cveId` and `AffectedRange.range` as individually marked fields outside `untrustedAdvisoryData`; label unchanged), `_docs/api.md` (commit `07e6d40de6f33afd2a00b9ce8566ed29cc3011d2`: `cveId` added to the untrusted list) and this log. GitHub: Engineer comment https://github.com/andrew-chung-au/vuln-triage/issues/27#issuecomment-6316974086
- verification (tests run, reviewer verdict): `.scratch/compare_openapi_no_desc.py` against `97893c1`: parsed schemas identical with `description` keys removed; `make openapi-validate` OK; `make verify BASE=97893c1` PASS (35/35 tests, whitespace PASS, no test files changed). No reviewer verdict on this change
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: none (no `ask` rule matched; no merits request)

### 2026-10-21 — #27 orchestrator: n8n and MCP server API contract closed

- date: 2026-10-21
- task/issue: #27 (API contract: n8n and MCP server endpoints, Stage 3 part 2); follow-up #50 filed
- agent role: main session (orchestrator) in a Claude Code cloud session on branch `claude/compassionate-hamilton-k90q3r`; launched PM, Software Engineer and QA subagents
- model: claude-opus-5-5 (Claude Code), main session and all subagents
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "The next product step is #27. Its grooming comment is already posted"; role launch prompts per `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/architecture.md` (`7855dda4a8e5f8dbc82f7677a82e2a69bbf6ae00`, `1f4515afa1babe5a9d9a5c175069567c72638486`), `_docs/specs.md` (`97893c13aba18647578fe548932872b0c71d11e0`, protected, US-12 any-status line), `_docs/roadmap.md`, this log and `_session-summaries/issue-027-n8n-mcp-contract.md`. Engineer commits: `7355d8e`, `d89597a`, `a9557e0`, `6494f28`, `9191aea`, `e74b2d1`, `07e6d40`, `9086658`, `fe55261`. GitHub: #50 created; #27 body tidy-up (responder bullet links #50); #27 comments 6316222176, 6316873471, 6316890596 (spec approval record), 6317003856, 6317141600
- verification (tests run, reviewer verdict): QA PASS at `a9557e0` (6316386844), R2 re-check PASS at `97893c1` (6316919374), FAIL at `9086658` (6317030883, overview said ranges sit inside each dependency), PASS at `fe55261` (6317071288); `make assert-clean` PASS after every QA run; `make verify` PASS on every push (pre-push hook)
- human review (what I checked or corrected, or `none`): the human chose option 1 for US-15 (follow-up #50); approved the contract at `7355d8e`, re-reviewed and approved `6494f28` (R2), `e74b2d1` (`cveId`, overview) and `fe55261` (overview wording fix); chose all recommendations at the decision point (architecture notes, the US-12 spec line, R3-R5 to #24, R6/R7/R1 accepted), then option 1 for the last two risks (architecture quoting sentence; brief fields left as they are); approved the full spec diff for the approval record. Commands that required approval: GitHub MCP `issue_write` create for #50 (merits request: GitHub write to the record); `gh api -X PATCH .../issues/27` body edit (merits request: GitHub write to the record); `HUMAN_APPROVED=1 git commit` for `_docs/specs.md` (merits request: protected commit)

### 2026-10-21 — #45 Engineer: frontend types, mock and screens aligned with the OpenAPI contract

- date: 2026-10-21
- task/issue: #45 (D4, roadmap step 8)
- agent role: Software Engineer subagent, launched by the orchestrator in a Claude Code cloud session on branch `claude/relaxed-ramanujan-drmkwb`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task to implement #45 with the PM's grooming decisions D1-D4; no new key prompt saved
- files changed: commit `72903cc` (`frontend/src/services/types.ts`, `mockData.ts`, `mockService.ts`, `frontend/src/lib/auth.ts`, `validation.ts`, `frontend/src/routes/_authed.tsx`, `_authed.assets.index.tsx`, `_authed.assets.new.tsx`, `_authed.findings.$findingId.tsx`, `_authed.findings.$findingId_.accept.tsx`, `frontend/src/components/vt/AuditTrail.tsx`, `Badges.tsx`, `FindingsTable.tsx`, `frontend/src/test/vulntriage.test.tsx`) and this log. The Makefile `frontend-typecheck` target and the AGENTS.md Commands line were drafted only (`.scratch/frontend-typecheck.patch`), not committed. GitHub: Engineer comment https://github.com/andrew-chung-au/vuln-triage/issues/45#issuecomment-6325754754
- verification (tests run, reviewer verdict): `make test` 61/61 pass (35 original, 26 new); `make verify` PASS WITH WARNINGS (7 rewritten assertion lines, all old wire values changed to contract values, reasons in the issue comment); `tsc --noEmit` in `frontend/` exit 0 using the drafted target. No reviewer verdict yet
- human review (what I checked or corrected, or `none`): none yet; approval of the Makefile and AGENTS.md change is pending. Commands that required approval: none beyond the protected-file rule (Makefile and AGENTS.md not committed)

### 2026-10-21 — #45 orchestrator: types/mock alignment closed; #50 groomed and placed

- date: 2026-10-21
- task/issue: #45 (D4 alignment, closed); #50 (US-15 responder contract, groomed, roadmap step 8b); follow-up #53 filed
- agent role: main session (orchestrator) in a Claude Code cloud session on branch `claude/relaxed-ramanujan-drmkwb`; launched PM (x3: #45, #50, #53 draft), Software Engineer and QA subagents
- model: claude-sonnet-5-5 (Claude Code), main session and all subagents
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "Next on the roadmap: #45 ... #50 also needs grooming and a place in the roadmap"; role launch prompts per `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/roadmap.md` (`ec7b49c` and the closing check-in), `Makefile` (`0d5197b`, protected), `AGENTS.md` (`3f55509`, `4e10afe`, protected), `agent-kit.conf` (`b18157c`, protected), `frontend/README.md` (`6447082`), this log and `_session-summaries/issue-045-types-mock-alignment.md`. Engineer commits `72903cc`, `a2d3bd9`. GitHub: #45 comments 6317572464 (PM grooming), 6325754754 (Engineer), 6325795173, 6325796249, 6326025911, 6326028192 (approval records), 6325826655 (QA PASS); #50 comment 6317612610 (PM grooming); #53 created
- verification (tests run, reviewer verdict): QA PASS at `3f55509` (6325826655); `make assert-clean` PASS and HEAD `3f55509` unchanged after QA; `make frontend-typecheck` exit 0 after the orchestrator applied the approved Makefile change; `make verify` PASS WITH WARNINGS or PASS on every push (pre-push hook; 61/61 tests; the 7 warnings are old wire values rewritten to contract values). The two PM errors on #45 (a nonexistent `source` enum; `vite build` treated as a type check) were found by the orchestrator reading `openapi.yaml` and `package.json`
- human review (what I checked or corrected, or `none`): the human answered #45 D1-D4 and #50 D1-D3 (all recommended), approved the Makefile and AGENTS.md typecheck changes, chose "leave as is" for the accept-screen client check, asked for the test count not to be hard-coded and approved the three-file rewording, and chose "file a follow-up under Later" for both QA verify-gate gaps (#53). Commands that required approval: `HUMAN_APPROVED=1 git commit` x4 for `Makefile`, `AGENTS.md` (twice) and `agent-kit.conf` (merits requests: protected commits); GitHub MCP `issue_write` create for #53 (merits request: GitHub write to the record); `git push -u origin` of the session branch (cloud-session exception, no merits request)

### 2026-10-21 — #34 Engineer: frontend SPA shell

- date: 2026-10-21
- task/issue: #34 (frontend SPA shell: document owned by index.html, built stylesheet linked)
- agent role: Software Engineer subagent, launched by the orchestrator on branch `claude/clever-allen-v5grbs`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task to implement #34 per PM grooming comment 6326704884 and the human's decisions in comment 6328636205; no new key prompt saved
- files changed: commit `67419b2` (`frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/routes/__root.tsx`, `frontend/src/test/app-routing.test.tsx` (comment only), `frontend/src/test/document-shell.test.tsx` (new)) and this log. GitHub: Engineer comment https://github.com/andrew-chung-au/vuln-triage/issues/34#issuecomment-6328657109
- verification (tests run, reviewer verdict): new regression test failed on the unfixed shell (1 failed, 61 passed) with the `<html> cannot be a child of <div>` warning; after the fix `make test` 62/62 pass, `make frontend-typecheck` clean, `make frontend-build` output has one stylesheet link, `make verify` PASS. Dev-server login and an HTTP 200 check of `dist/` were not run. No reviewer verdict yet
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: none

### 2026-10-21 — #34 orchestrator, PM and QA: frontend SPA shell

- date: 2026-10-21
- task/issue: #34 (lifecycle steps 1-9, except the Engineer's own entry above)
- agent role: Orchestrator (main session), with PM and QA subagents
- model: claude-sonnet-5-5 (Claude Code, cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): "Next product step: step 9 (#34), the frontend SPA shell, is unblocked. follow process.md"; no new key prompt saved
- files changed: `_docs/roadmap.md` (step 9 row, check-in), this log, `_session-summaries/issue-034-spa-shell.md`. GitHub: #34 comments 6326704884 (PM grooming), 6328636205 (human's decisions, posted by the orchestrator), 6328681771 (QA provisional FAIL), 6328697373 (QA PASS)
- verification (tests run, reviewer verdict): QA PASS at `d8c2ffe` (6328697373); `make assert-clean` PASS and HEAD `d8c2ffe` unchanged after both QA runs; `make verify` PASS on the push (62/62). Criterion 9 passed only on the clean dev-server start plus the routeTree tests; sign-in in a real browser was not machine-verified
- human review (what I checked or corrected, or `none`): the human chose D1 and D2 (recommended), approved QA's read-only `.scratch/` HTTP check, and chose "note only" for the QA risks and "discard" for the script. Commands that required approval: the QA `.scratch/check_dist_http.py` run (merits request: local network access); `git push -u origin` of the session branch (cloud-session exception, no merits request)

### 2026-10-21 — #50 Engineer: responder read-only API contract (US-15)

- date: 2026-10-21
- task/issue: #50 (API contract: responder agent read-only endpoints, US-15)
- agent role: Software Engineer subagent, launched by the orchestrator on branch `claude/sleepy-euler-bzyy0r`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task to implement #50 per PM grooming comment 6317612610 and the human's D1-D3 answers (option 1); no new key prompt saved
- files changed: commit `6ff10d9` (`_docs/openapi.yaml`, `_docs/api.md`) and this log. GitHub: Engineer comment on #50
- verification (tests run, reviewer verdict): `make openapi-validate` exit 0 on the final file; negative copy with `ResponderNotificationJob` renamed in the response `$ref` exited 2 and was deleted; `.scratch/check_responder.py` listed exactly two operations using `responderAuth`, both GET, and no recipient, owner, `advisorySummary`, finding or `untrustedAdvisoryData` property on `ResponderNotificationJob`; `make verify` PASS (62/62 tests, no whitespace errors, no test files changed). No reviewer verdict yet
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: none

### 2026-10-22 — #50 orchestrator and QA: responder contract close-out; #56 filed

- date: 2026-10-21 to 2026-10-22
- task/issue: #50 (lifecycle steps 4-9, except the Engineer's own entry above); also filed #56 (roadmap step 10, Stage 4 testing)
- agent role: Orchestrator (main session), with a QA subagent
- model: claude-sonnet-5-5 (Claude Code, cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): "add the new step 10 issue for the other agent first then start #50"; "approve all three, then close #50"; no new key prompt saved
- files changed: `_docs/architecture.md` (protected; `cd870df`, `54bdce3`, `147bd7a`), `_docs/roadmap.md` (step 8b and 10 rows, check-in), this log, `_session-summaries/issue-050-responder-read-only-contract.md`. GitHub: #56 created; #50 comments 6329301519 (QA PASS), 6329360243, 6329361058 and 6329361312 (approval records)
- verification (tests run, reviewer verdict): QA PASS at `9a03ba9` (6329301519); `make assert-clean` PASS and HEAD `9a03ba9` unchanged after QA; `make verify` PASS on the pre-push run for the Engineer's commits (62/62). The three `architecture.md` commits were not re-checked by QA
- human review (what I checked or corrected, or `none`): the human merged PR #57 (the contract diff, `9a03ba9`) and approved spec notes 1-3 in chat. Commands that required approval: `HUMAN_APPROVED=1 git commit` for the three protected commits; `git push -u origin` of the session branch (cloud-session exception); a first `git push origin HEAD:<branch>` was refused by `guard_git.py`

### 2026-10-22 — #58 orchestration: contract follow-ups from #50 QA (job ordering, traceparent, CSRF wording)

- date: 2026-10-22
- task/issue: #58 (contract follow-ups from #50 QA); roadmap review that chose it as the next task alongside the other session's #56
- agent role: Orchestrator (main session) with PM, Engineer and QA subagents (two QA runs), on branch `claude/vigilant-heisenberg-qtr2f3`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request to review the issues and roadmap and pick the highest-priority task that does not conflict with the agent working on #56, then "yes" to start; the subagent task messages followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/openapi.yaml` and `_docs/api.md` (`2e9a4dd`), `_docs/architecture.md` (`4cebbd2`), `_docs/api.md` (`b7b4d36`), `_docs/roadmap.md` (step 8b row, check-in), this log, `_session-summaries/issue-058-contract-follow-ups.md`. GitHub: #58 comments 6329518860 (PM grooming), 6329573230 (human's decisions), 6329595990 (Engineer), 6329679240 (approval record posted by mistake), 6329697265 (QA FAIL), 6329737124 (correction note), 6329743761 (QA PASS); the groomed body was applied to #58 by the orchestrator through the GitHub issue tool because `gh issue edit` is blocked in cloud sessions
- verification (tests run, reviewer verdict): `make openapi-validate` exit 0 and `make verify` PASS (62/62) at `2e9a4dd` (Engineer) and on both pushes; parsed-YAML diff showed description text only; QA FAIL at `b7b4d36` only because `_docs/architecture.md` is not in `PROTECTED`, then QA PASS on the re-check (6329743761), with the other verdicts carried over; `make assert-clean` PASS and HEAD `b7b4d36` unchanged after both QA runs
- human review (what I checked or corrected, or `none`): the human chose D1 and D2 (option 1, recommended), approved spec notes 1 and 3 and the exact `architecture.md` diff, approved the contract at `2e9a4dd`, and chose option 2 (architecture.md gated by convention, `PROTECTED` unchanged) after QA's FAIL. The orchestrator wrongly posted a protected-change record for `4cebbd2` without checking `PROTECTED`; corrected in 6329737124. Commands that required approval: none (the `HUMAN_APPROVED=1` commit of `4cebbd2` was not required by `PROTECTED`; `git push -u origin` of the session branch is the cloud-session exception)

### 2026-10-22 — #60, #37 and #61 Engineer step: proposed permission-settings diffs and `make permission-report`

- date: 2026-10-22
- task/issue: #60 (`gh api` allow rule), #37 (four Edit ask rules), #61 (`make permission-report` and the sweep procedure)
- agent role: Engineer (subagent), on branch `claude/beautiful-lovelace-la54rn`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task message to implement #60, #37 and #61 from the PM grooming comments and the human's answers (Orchestrator comment 6330251791), without editing protected files or committing; no new key prompt saved
- files changed: uncommitted: `_docs/cloud-sessions.md` (line 46), `_docs/permission-sweeps.md` (new), this log, `_session-summaries/issue-060-037-061-permission-settings.md` (new). Proposed but not applied (protected): `.claude/settings.json`, `Makefile`, `_docs/agent-kit/scripts/permission-report.py` (new), `AGENTS.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/templates/session-summary.md`, `_docs/agent-kit/procedures/session-summary.md`, `_docs/agent-kit/procedures/permission-sweep.md` (new). GitHub: Engineer comments 6330334016 (#60), 6330335550 (#37), 6330334233 (#61)
- verification (tests run, reviewer verdict): `python3 -m json.tool` exit 0 on the proposed settings; a script modelling the rule shapes showed the four #60 commands plus two extra flag forms matching the `Bash(gh api *)` ask and no allow rule, and `make issue-dump`, `make issue-comment` and `make issue-close` matched by `make *` allow and the `make issue-close*` ask; `git apply --check` passed for all three diff files; the `.scratch/` regression script (refused `SINCE` values, allowed values, parser fixtures) passed; the report was run on the real session summaries. Not run: `make verify`, a live Claude Code prompt check, QA
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: none known (I cannot see whether the tool prompted for an `ask`-rule command)

### 2026-10-22 — #60, #37 and #61 orchestration: permission settings and the permission sweep

- date: 2026-10-22
- task/issue: #60, #37, #61; chosen from the human's request to prioritise tooling targets and to work them on a separate branch, off the roadmap, beside the product session on step 10
- agent role: Orchestrator (main session) with PM, Engineer and QA subagents (one run each), on branch `claude/beautiful-lovelace-la54rn`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's requests to rank the tooling issues, to groom #60, #37 and #61 together and to go with the recommendations; the subagent task messages followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `.claude/settings.json` (`a5b21c0`), `Makefile` and `_docs/agent-kit/scripts/permission-report.py` (`2520c9c`), `AGENTS.md`, `_docs/agent-kit/process.md`, `_docs/agent-kit/templates/session-summary.md`, `_docs/agent-kit/procedures/session-summary.md`, `_docs/agent-kit/procedures/permission-sweep.md` (`4c42cf3`), `_docs/cloud-sessions.md`, `_docs/permission-sweeps.md`, the Engineer log entry above and this one, `_session-summaries/issue-060-037-061-permission-settings.md` (`509215b` and this session's closing commit). The Engineer's entry above was written before the commits and says "uncommitted" and "proposed, not applied"; the commits above are the real state. GitHub: PM 6330134485, 6330134704, 6330137277; decisions 6330251791; Engineer 6330334016, 6330335550, 6330334233; approval records 6330381464, 6330381694, 6330381921, 6330382170; QA 6330439958, 6330440182, 6330440402
- verification (tests run, reviewer verdict): `make verify` PASS (62/62) on the pre-push run and in QA's run; QA PASS on all three issues at `509215b`, including the approval records against the commits, the settings rule sets, 31 refused `SINCE` values and the report counts; `make assert-clean` PASS after QA. Not verified: a live Claude Code prompt check for the new ask rules (needs a new session)
- human review (what I checked or corrected, or `none`): the human chose the six PM decisions as recommended, approved the three protected diffs as drafted, and kept the work off the roadmap. Commands that required approval: none known; the `HUMAN_APPROVED=1` commits and `git push -u origin` of the session branch are the protected-change and cloud-session cases

### 2026-10-22 — #60, #37 and #61 follow-up: live prompt check result and two follow-up issues

- date: 2026-10-22
- task/issue: #60, #37 (live prompt check); new issues #65 (first permission sweep) and #66 (`make issue-close` ask rule bypassed by option order)
- agent role: Orchestrator (main session), on branch `claude/beautiful-lovelace-la54rn`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's requests for a test prompt and branch instructions for a new session, then "confirmed" and "approve recommendations"; no new key prompt saved
- files changed: `_docs/permission-sweeps.md` (points to #65; notes that cloud sessions skip `Edit` asks), this log. GitHub: comments 6330923566 (#60) and 6330923814 (#37); issues #65 and #66 created through the GitHub MCP `issue_write` tool (no REST make target for creating issues)
- verification (tests run, reviewer verdict): the live check was run by the human in a local default-mode session on the branch, with a test agent running the commands; the human reported prompts on all six `gh api` commands and on the `.devcontainer/` write, and none on the `make issue-dump` control. Tests for `.githooks/`, `.github/` and `.vscode/` were not run. Two earlier runs gave no result (wrong branch; cloud session, which does not prompt for edits). The orchestrator did not observe any prompt itself
- human review (what I checked or corrected, or `none`): the human ran and observed the live check, confirmed the three details, deleted the test file in their sandbox, and approved filing #65 and #66. Commands that required approval: `make issue-comment` and `make issue-close` per the ask rules; creating issues through `issue_write` is the recurring MCP item counted by `make permission-report`

### 2026-10-22 — #56 orchestrator, PM, Engineer and QA: Stage 4 test strategy

- date: 2026-10-22
- task/issue: #56 (Stage 4 `_docs/testing.md`, roadmap step 10); follow-up #63 filed for the four deferred spec notes
- agent role: Orchestrator (main session) with PM, Software Engineer and QA subagents, on branch `claude/issue-056-stage-4-testing`; worktree shared with the paused #50/#58 sessions, so the branch was rebased on the merged `origin/main` before close-out
- model: deepseek-v4.1-flash-free (opencode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "please work on Step 10 issue: #56 ... follow process.md" and the later decisions on D1, branch strategy, deferring the spec notes, note-only QA risks and pushing the branch; role launch prompts followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/testing.md` (new, 385 lines) and `README.md` (`8d9db69`, `2430912`); `_docs/roadmap.md` (step 10 row, #43 leftover line, check-in), this log and `_session-summaries/issue-056-stage-4-testing.md` at close-out. GitHub: #56 comments 6329411066 (PM grooming), 6329460170 (PM body-edit note), 6329735908 (Engineer), 6329945929 (QA PASS); #9 two Stage 4 rows ticked; #63 created
- verification (tests run, reviewer verdict): QA PASS (6329945929) before the rebase, re-check PASS at `ae0d55d` (6330289999) after it; `make assert-clean` PASS and HEAD unchanged after each QA; `make verify` PASS (62/62, no whitespace errors, no test files changed), plus `make verify BASE=origin/main` to cover the branch's missing upstream; `make issue-dump N=9` confirmed only the two Stage 4 rows changed; `make openapi-validate` was not needed (no contract edit)
- human review (what I checked or corrected, or `none`): the human chose D1 option 1 (a resolution is not a second alert), told me to move the work to its own branch and rebase on the merged sessions, chose one follow-up issue for the four spec notes (#63), and chose note-only for the QA risks. Commands that required approval: PM/Engineer `gh api -X PATCH` body edits (#56, #9) and the PM Git read loop (ask rules); PM `gh issue create` for #63 (issue-creation rule); `git push -u origin claude/issue-056-stage-4-testing` (denied by the `git push*` rule; the branch stays local for the human to push)

### 2026-10-22 — #53, #48, #31 orchestration: grooming and scheduling on a parallel tooling track

- date: 2026-10-22
- task/issue: #53, #48, #31 (grooming and roadmap scheduling only; no implementation); new issues #67 and #68
- agent role: Orchestrator (main session) with a PM subagent, on branch `claude/beautiful-lovelace-la54rn`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request to schedule #53 and #48/#31 as parallel tooling work; the PM task message followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/roadmap.md` (parallel tooling track T1-T3, step 16 row, Later list, check-in), this log. GitHub: PM comments 6331077862, 6331105969 (#53), 6331091593 (#48), 6331105799 (#31); human's answers 6331014940 (#48 D1/D2) and 6331160446 and copies on #53, #48, #31; issues #67 (CI passes a real `BASE`) and #68 (run #26's persistence test against Postgres) created through the GitHub MCP `issue_write` tool
- verification (tests run, reviewer verdict): the PM ran `make frontend-typecheck` (exit 0 at `26ac31a`) and read the verify scripts, hooks and `.devcontainer/`; no implementation, no QA. The PM's first #53 comment had two small errors, superseded by its correction comment 6331105969
- human review (what I checked or corrected, or `none`): the human answered #48 D1/D2 and the placement question, then D1-D5 as recommended. Commands that required approval: `make issue-comment` (allowed target); issue creation through `issue_write`

### 2026-10-22 — Human cheatsheet for reviewing, pushing and merging agent work

- date: 2026-10-22
- task/issue: no issue; the human's request for a cheatsheet of the current push process, then for example commands
- agent role: single Claude Code session (no subagents), on branch `claude/human-cheatsheet`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request for a cheatsheet "for using the current process for pushing to the repo from the sandbox", their note that the method has evolved from the original agent kit, and "the cheat sheet needs example commands etc"; no key prompt saved
- files changed: `_docs/human-cheatsheet.md` (new), `README.md` (one index line), this log
- verification (tests run, reviewer verdict): none run on the commands; the process was read from `environments.md`, `process.md`, `cloud-sessions.md`, the roadmap, the #56 summary and `git branch -a`. Items marked `VERIFY:` in the file (the local-sandbox branch flow, `gh pr create` and `gh pr merge` from the human's machine) are unconfirmed. No QA run
- human review (what I checked or corrected, or `none`): the human confirmed the described method "looks correct" and asked for example commands. Commands that required approval: none recorded

### 2026-10-22 — #72 orchestrator, PM, Engineer and QA: Stage 5 task backlog

- date: 2026-10-22
- task/issue: #72 (Stage 5 `_docs/tasks.md`, roadmap step 11); follow-ups #73 (README `withdrawn` and Stage 5 tier-label note) and `andrew-chung-au/agent-kit` #19 (task-template naming)
- agent role: Orchestrator (main session) with PM, Software Engineer and QA subagents, on `main` in the local sandbox
- model: deepseek-v4.1-flash-free (opencode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "check the roadmap and issue for the next product driven issue to work on", the clarification question about Stage 4 and #24, then "ok got it then do step 11"; the role launches followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/tasks.md` (new, 36 tasks) and `README.md` (one link line) at `05e3e60`; `_docs/tasks.md` (`ae6b708`, US-15 `Covers:` alignment); `_docs/roadmap.md`, this log and `_session-summaries/issue-072-stage-5-tasks.md` at close-out. GitHub: #72 created; comments 6331775484 (human D1/D2), 6331821940 (PM grooming), 6332002908 (Engineer), 6332195958 (QA PASS), 6332266585 (Engineer US-15 fix), 6332346303 (QA re-check PASS); #73 and agent-kit #19 created
- verification (tests run, reviewer verdict): QA PASS (6332195958) and re-check PASS (6332346303); `make assert-clean` PASS with HEAD unchanged (`05e3e60`, then `ae6b708`) after each; `make verify` PASS both times (62 tests, no whitespace errors, no test files changed); the Engineer's read-only `.scratch/check_tasks.py` passed (36 tasks, 16 user stories, 12 criteria, lower-numbered acyclic dependencies, dependency chain matches)
- human review (what I checked or corrected, or `none`): the human approved filing #72 and chose D1 (rubric-tier milestones A/B/C then a Committed scope section) and D2 (one planning-evidence task), both recommended; chose fix-now for the US-15 alignment and note-only for the task-sizing risks; directed the three follow-ups (agent-kit #19, and #73 for the two doc notes). Commands that required approval: `gh issue create` for #72 and #73 (issue-creation rule) and for agent-kit #19 (same rule, another repo); `gh issue edit 72` (issue-edit ask rule); `make issue-comment` (allowed target)

### 2026-10-22 — #53 orchestrator, Engineer and QA: verify gate type check and BASE handling

- date: 2026-10-22
- task/issue: #53 (roadmap track T1: type check in `make verify`; BASE warning and failure)
- agent role: Orchestrator (main session) with a Software Engineer subagent and QA subagents (two runs, the second a narrow re-check), on branch `claude/start-53-7oaxg3`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "Start #53"; role launch prompts followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/testing.md` (`291b4bc`); `_docs/agent-kit/scripts/verify.sh` and `_docs/agent-kit/procedures/verify.md` (`bdda483`); `agent-kit.conf` (`e0cf368`); `AGENTS.md` line 35 (`1d869a5`); `_docs/agent-kit/scripts/verify.sh` again (`3d978fe`, one line); `_docs/roadmap.md` (check-in), this log and `_session-summaries/issue-053-verify-gate-gaps.md` at close-out. GitHub on #53: Engineer 6331467458; QA 6331468388; approval records 6331468586, 6331468781, 6331469012, 6331469216
- verification (tests run, reviewer verdict): `make verify BASE=6ed87ed` PASS (62 tests, `PASS: Type check`) and the pre-push runs PASS; QA PASS at `1d869a5`, then re-check PASS at `3d978fe` after the stderr fix; QA re-ran `BASE=HEAD` (warns), `BASE=nosuchref` (fails), `BASE=72903cc^` (lists the changed test file), `BASE=3d38e34` (clean), the empty-tree base and a deliberate type error (`FAIL: Type check`, reverted); `make assert-clean` PASS and HEAD unchanged after both QA runs. Not verified: the sandbox push check was read, not run (no Docker)
- human review (what I checked or corrected, or `none`): the human approved all three protected diffs as drafted, and chose "Fix it now" for the stray stderr line QA found (a fourth protected commit), "No, already tracked" for the other QA notes. Commands that required approval: `HUMAN_APPROVED=1 git commit` of `bdda483`, `e0cf368`, `1d869a5`, `3d978fe` (protected files); `git push -u origin claude/start-53-7oaxg3` (cloud-session exception); `make issue-comment` (allowed target)

### 2026-10-22 — Step 12 orchestration: Milestone A backlog from `_docs/tasks.md`

- date: 2026-10-22
- task/issue: roadmap step 12 (backlog issues from `_docs/tasks.md`); created #74, #75, #76-#88; edited #26; closed #24 and #25
- agent role: Orchestrator (main session) with a PM subagent; no Engineer or QA stage (backlog and tracker work only)
- model: deepseek-v4.1-flash-free (opencode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "groom the next step"; the PM task followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/roadmap.md` (step 12 and 15 rows, check-in), this log, `_session-summaries/planning-2026-10-22-step-12-backlog.md` at close-out. GitHub: #74-#88 created from `.scratch/` body files; #26 edited; #24/#25 closed, comments 6333191444 and 6333194914; block note 6333211529 on #74
- verification (tests run, reviewer verdict): no code or test change; `make verify` not run. The proposal checked `_docs/tasks.md` against `_docs/specs.md` and the open tracker with a read-only `gh issue list`. The human approved the proposal before any issue was created, edited or closed
- human review (what I checked or corrected, or `none`): the human chose Milestone A filing now, closing #24/#25 and rewriting #26, the 9/10 splits, accepting #63 notes before Milestone C, and deciding the LLM/responder runtime at milestone start with stubs. The orchestrator corrected issue 1's draft so `make test` keeps the frontend suite. Commands that required approval: `gh issue create` for #74-#88 (issue-creation rule); `gh issue edit 26` (issue-edit ask rule); `make issue-comment` (allowed target); `make issue-close` on #24/#25 (issue-close ask rule)

### 2026-10-22 — Orchestrator: temporary Tier B/C roadmap

- date: 2026-10-22
- task/issue: none (planning; the human asked for a secondary roadmap for Tiers B and C while another session works roadmap step 11)
- agent role: Orchestrator (main session), on branch `claude/kind-einstein-i39rmh`
- model: Claude Code (cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request with the final-project criteria and the Module 2-4 notes and homework pasted; no new key prompt saved
- files changed: `_docs/roadmap-tiers-b-c.md` (new, temporary), this log, `_session-summaries/planning-2026-10-22-tier-b-c-roadmap.md`. `_docs/roadmap.md` not changed
- verification (tests run, reviewer verdict): `make verify` run before commit (result in the session summary); no QA or rubric-auditor review
- human review (what I checked or corrected, or `none`): none yet; seven decisions (D1-D7) are open in the new file, which maps its milestones to the `tasks.md` task numbers from PR #89. Commands that required approval: none recorded

### 2026-10-22 — Orchestrator: merge the Tier B/C roadmap draft

- date: 2026-10-22
- task/issue: none (planning; the human asked to review and merge `_docs/roadmap-tiers-b-c.md` into `_docs/roadmap.md` and delete the draft)
- agent role: Orchestrator (main session), local sandbox on `main`
- model: deepseek-v4.1-flash-free (opencode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request to review and merge the two roadmap files, delete the draft, then review the roadmap and start the next product issue; no new key prompt saved
- files changed: `_docs/roadmap.md` (step 17 milestones B1-B6/C1-C8, prerequisites, task mapping, AWS-slow order, open decisions 5-11, B/C checkpoints, check-in); `_docs/roadmap-tiers-b-c.md` (deleted); this log; `_session-summaries/planning-2026-10-22-roadmap-tier-b-c-merge.md`
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (62 tests, type check pass, no whitespace errors, no test files changed; the warning is `BASE` equal to `HEAD` for a docs-only change). No QA or rubric-auditor review
- human review (what I checked or corrected, or `none`): the human directed the merge and deletion; D1-D7 were carried over as open, not answered. Commands that required approval: none recorded

### 2026-10-22 — #91 orchestrator, PM, Engineer and QA: Stage 6 plan summary

- date: 2026-10-22
- task/issue: #91 (roadmap step 13, `_docs/plan-summary.md`); follow-up #95 filed
- agent role: Orchestrator (main session) with PM, Software Engineer and QA subagents, local sandbox on `main`
- model: deepseek-v4.1-flash-free (opencode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "review the roadmap and start the next issue to progress the product"; the role launches followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: `_docs/plan-summary.md` (`731f11b`, `e8e4ddb`, `882c75d`) and `README.md` (`731f11b`); `_docs/roadmap.md` (step 13 done and check-in), this log and `_session-summaries/issue-091-stage-6-plan-summary.md` at close-out. GitHub: #91 created; comments 6334007642 (PM), 6334298084 (Engineer), 6335550333 (QA FAIL), 6336177091 (QA re-check PASS); #95 created
- verification (tests run, reviewer verdict): QA FAIL at `e8e4ddb` on the completeness counts and a false checklist PASS; Engineer `882c75d` fixed the label-only counts and evidence; QA re-check PASS at `882c75d` (6336177091); `make verify BASE=1edc468` PASS (62 tests, type check, whitespace, no weakened tests); `make assert-clean` PASS with HEAD unchanged after both QA runs
- human review (what I checked or corrected, or `none`): the human deferred the protected spec Q2-Q4 note to the next spec change, approved filing one follow-up (#95) for the tasks.md Application/task 15 discrepancy with README `withdrawn` left to #73, and chose note-only for the minor checklist recount wording. Commands that required approval: `gh issue create` for #91 and #95 (issue-creation rule); `make issue-comment` (allowed target)

### 2026-10-22 — Orchestrator: parallel-work analysis and AWS setup guide

- date: 2026-10-22
- task/issue: none (planning). The human asked which work can run beside another session's roadmap step 13 (`_docs/plan-summary.md`) without conflict, without editing either roadmap; then, with #48 set aside (cloud credits), for a guide to the AWS setup the Tier B/C work needs
- agent role: Orchestrator (main session), on branch `claude/tender-volta-wiq6xv`
- model: Claude Code (cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's two requests in chat; no new key prompt saved
- files changed: `_docs/aws-setup.md` (new), this log, `_session-summaries/planning-2026-10-22-aws-setup.md`. Neither roadmap and no README link (step 13 edits the README index)
- verification (tests run, reviewer verdict): `make verify` run before commit (result in the session summary); the guide was checked against `_docs/architecture.md` Deployment and Security boundaries by the author only; no QA or rubric-auditor review; nothing in it was run against AWS
- human review (what I checked or corrected, or `none`): none yet; the guide lists seven decisions for the human. Commands that required approval: none recorded

### 2026-10-22 — Orchestrator: #73 and follow-up #92

- date: 2026-10-22
- task/issue: #73 (README `withdrawn`, Stage 5 tier-label sentence); created #92 (follow-ups deferred to avoid conflicting with the step 13 session)
- agent role: Orchestrator (main session) with PM, Engineer and QA subagents, on branch `claude/tender-volta-wiq6xv`
- model: Claude Code (cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request to work #73 and save conflicting README and follow-up changes to a follow-up issue; role launches followed `_docs/agent-kit/process.md`; no new key prompt saved
- files changed: this log and `_session-summaries/issue-073-readme-withdrawn-tier-label.md` (the Engineer's commits are in its own entry). GitHub: #73 comment 6334352037 (human answers), #92 created (body later trimmed and one comment deleted at the human's direction: discussion material was not to be saved), #73 closed
- verification (tests run, reviewer verdict): QA PASS at `6248c29` (6334401494); `make assert-clean` PASS, HEAD unchanged
- human review (what I checked or corrected, or `none`): the human answered the PM's decisions (Stage 5 sentence matches the architecture Tier column; leave the brief). The orchestrator checked the PM's architecture-tier claim against `_docs/architecture.md` before asking. Commands that required approval: none recorded

### 2026-10-22 — Orchestrator: submission and showcase tracks

- date: 2026-10-22
- task/issue: none (planning); created #93 (merge the drafts into the main roadmap; apply decisions H2-H7 before plan review)
- agent role: Orchestrator (main session), on branch `claude/tender-volta-wiq6xv`
- model: Claude Code (cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's questions on the deployment approach, ease and speed, and a CV showcase; the human chose two tracks, Terraform, GHCR, `sslip.io` and deferring n8n; no new key prompt saved
- files changed: `_docs/roadmap-submission-draft.md` (new, temporary), `_docs/roadmap-showcase.md` (new, kept separate), `_docs/aws-setup.md` (status line), this log, `_session-summaries/planning-2026-10-22-submission-showcase.md`. Neither existing roadmap changed
- verification (tests run, reviewer verdict): `make verify` before commit (result in the session summary); no QA or rubric-auditor review; the drafts were checked against `_docs/rubric.md` and the `_docs/tasks.md` task list by the author only
- human review (what I checked or corrected, or `none`): the human made decisions H1-H7 in the session (recorded in the submission draft). Commands that required approval: none recorded

### 2026-10-22 — Engineer: #73 README withdrawn status and Stage 5 tier note

- date: 2026-10-22
- task/issue: #73 (lifecycle step 3, implementation)
- agent role: Software Engineer (subagent of the orchestrator), on branch `claude/tender-volta-wiq6xv`
- model: claude-opus-5-5 (Claude Code, cloud session)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's step 3 task for #73, implementing PM comment 6334306395 with the human's decisions in comment 6334352037; no new key prompt saved
- files changed: `README.md` (line 27: adds `withdrawn`), `_docs/planning-process.md` (one sentence in the Stage 5 "Rules:" paragraph), this log. Commit 0aa61b1
- verification (tests run, reviewer verdict): `make verify BASE=25960f5` PASS (62 tests passed, type check pass, whitespace pass, no test files changed); QA not yet run
- human review (what I checked or corrected, or `none`): none. Commands that required approval: none recorded

### 2026-10-22 — Engineer: #95 reconcile Application coverage with task 15

- date: 2026-10-22
- task/issue: #95 (lifecycle step 3, implementation); option B confirmed by the orchestrator
- agent role: Software Engineer (subagent of the orchestrator), local sandbox on `main`
- model: deepseek-v4.1-flash-free (opencode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's step 3 task for #95, implementing PM comment 6339083871 (option B); no new key prompt saved
- files changed: `_docs/tasks.md` (one `Note:` paragraph after the `ASSUMPTION:` paragraph at line 267, before `## Dependency chain`), `_docs/plan-summary.md` (footnote ¹ line 35 and the D1 `Handling` line 41), this log, `_session-summaries/issue-095-application-coverage.md`. Doc commit e8a7c4d; process records in a separate commit
- verification (tests run, reviewer verdict): `make verify BASE=a1d5dd0` PASS (62 tests passed, type check pass, whitespace pass, no weakened tests; 2 files changed); QA not yet run
- human review (what I checked or corrected, or `none`): none yet; the orchestrator confirmed option B and asked for the two doc edits plus the AGENTS.md process records. Commands that required approval: none recorded

### 2026-10-22 — Orchestrator: #95 close-out, #93 split, #97 and #98

- date: 2026-10-22
- task/issue: #95 QA and close; #93 grooming and split into #97-#100; #97 and #98 implemented and QA'd (continuing a session that hit an opencode rate limit)
- agent role: Orchestrator (main session), with PM, Engineer and QA subagents, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code) for the orchestrator; the subagents' models were not recorded in this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request to continue #93 and #95, then "go with all recommendations", "start the architecture and spec issues" and "ok"; no new key prompt saved
- files changed: `_docs/tasks.md` and `_docs/plan-summary.md` (#95, e8a7c4d); `_docs/architecture.md` and `_docs/aws-setup.md` (#97, d5f6508 and d520876); `_docs/specs.md` (#98, 4fa7a55, protected, `HUMAN_APPROVED=1`); session summaries for #95, #97 and #98; merge 243fcd6 of `origin/main`; this log
- verification (tests run, reviewer verdict): `make verify` PASS (62 tests passed, type check pass, whitespace pass, no weakened tests). QA PASS: #95 at d4c5345, #97 at d5f6508 (follow-up d520876 rechecked PASS), #98 at 4fa7a55 after two FAILs on the approval criterion and a final PASS as a ratification. `make assert-clean` PASS after each QA run
- human review (what I checked or corrected, or `none`): the human approved the #93 split, the #98 proposal on a summary, and commented "Diff approved" on #98 after the commit. The commit was made before the human saw the full diff; QA recorded this as a deviation. Commands that required approval: `HUMAN_APPROVED=1 git commit` of the protected spec; `gh issue edit 93` and `make issue-close` (ask rules)

### 2026-10-22 — Orchestrator: #99-#102 (tasks, showcase marking, architecture, test split)

- date: 2026-10-22
- task/issue: #99, #100, #101, #102 implemented and QA'd; #93 updated by the PM with two clean-up edits (continuing the session above)
- agent role: Orchestrator (main session), with PM, Engineer and QA subagents, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code) for the orchestrator; the subagents' models were not recorded in this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's replies "yes ok", "yes", "approved 3c13321, 2 ok, 3 ok, 4 ok, 5 ok", "approve" and "approve recommedations"; no new key prompt saved
- files changed: `_docs/tasks.md` and `_docs/plan-summary.md` (#99, 70a0f82); `README.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/testing.md` (#100, 3c13321); `_docs/architecture.md` (#101, c098669 and fix 86d3978); `_docs/testing.md`, `_docs/api.md`, `_docs/openapi.yaml` (#102, 5573e03); session summaries for #99-#102; this log
- verification (tests run, reviewer verdict): `make verify` PASS (62 tests passed, type check pass, whitespace pass, no weakened tests); `make openapi-validate` OK. QA PASS: #99 at 70a0f82, #100 at 3c13321, #102 at 5573e03; #101 FAIL at c098669 (submission 403 case named the MCP token), fixed in 86d3978 and PASS on recheck. `make assert-clean` PASS after each QA run
- human review (what I checked or corrected, or `none`): the human replied "approved 3c13321" for #100's contract diff (recorded on #100) and "approve" for #102's diff before its commit (recorded on #102 before the commit). No protected file was committed in this entry. Commands that required approval: `gh issue create` and `gh issue edit 99`/`93` (PM, ask rules); `make issue-close` for #99-#102 (ask rule)

### 2026-10-22 — Orchestrator: #103 and #93 (aws-setup revision, roadmap merge, milestones; #92 folded in)

- date: 2026-10-22
- task/issue: #103 implemented and QA'd; #93 implemented and QA'd; #92 handled (items folded into #93, closed with it); GitHub milestones "Submission" and "Showcase" created (continuing the session above)
- agent role: Orchestrator (main session), with PM, Engineer and QA subagents, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code) for the orchestrator; the subagents' models were not recorded in this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's replies "approve recommendations", "ok that is fine" (milestones) and their instructions for the `aws-setup.md` revision; no new key prompt saved
- files changed: `_docs/aws-setup.md` (#103, 7fa6de1 and fix 9890d28); `README.md`, `_docs/roadmap.md` and deleted `_docs/roadmap-submission-draft.md` (#93, 1b14412); `_docs/architecture.md`, `_docs/plan-summary.md`, `_docs/tasks.md`, `_docs/testing.md` (#93, e6ceb22); session summaries for #103 and #93; this log
- verification (tests run, reviewer verdict): `make verify` PASS (62 tests passed, type check pass, whitespace pass, no weakened tests). QA: #103 FAIL at 7fa6de1 (citations to `roadmap.md` items that did not resolve), fixed in 9890d28 and PASS on recheck; #93 FAIL at e6ceb22 only on the then-uncreated milestones, PASS on recheck after they were created. `make assert-clean` PASS after each QA run
- human review (what I checked or corrected, or `none`): the human approved the recommendations before the work and the milestone creation after an explanation. No protected file was committed in this entry. Commands that required approval: `gh api repos/{owner}/{repo}/milestones` x2 (merits request, tracker write); `gh issue create`/`gh issue edit` (PM, ask rules); `make issue-close` for #103, #93 and #92 (ask rule)

### 2026-10-22 — Orchestrator: #104 and #105 (brief showcase marks, task 15 .env.example)

- date: 2026-10-22
- task/issue: #104 and #105 filed by the PM, implemented and QA'd (continuing the session above)
- agent role: Orchestrator (main session), with PM, Engineer and QA subagents, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code) for the orchestrator; the subagents' models were not recorded in this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's replies approving items 2 and 3 and "the bigger gap", "add a note" (Gemini candidate in Open question 9) and "option a" (`.env.example` in task 15); no new key prompt saved
- files changed: `_docs/testing.md`, `_docs/roadmap-showcase.md`, `_docs/architecture.md` (#104, f6c0efc); `_docs/tasks.md` (#105, 98d0a7e); session summaries for #104 and #105; this log
- verification (tests run, reviewer verdict): `make verify` PASS (62 tests passed, type check pass, whitespace pass, no weakened tests). QA PASS: #104 at f6c0efc, #105 at 98d0a7e. `make assert-clean` PASS after each QA run
- human review (what I checked or corrected, or `none`): the human approved the work before each step; no protected file was committed in this entry. Commands that required approval: `gh issue create` (PM, ask rules); `make issue-close` for #104 and #105 (ask rule)

### 2026-10-22 — Engineer: #107 (pre-review clean-up)

- date: 2026-10-22
- task/issue: #107, implemented as a subagent (not closed; QA not yet run)
- agent role: Software Engineer subagent, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #107; no new key prompt saved
- files changed: `_docs/planning-process.md`, `_docs/architecture.md`, `_docs/roadmap.md` (17fc6d9); `_docs/plan-summary.md` (061de62); this log
- verification (tests run, reviewer verdict): `make verify` PASS (62 tests passed, type check pass, whitespace pass, no weakened tests), run before the commits. No QA or review yet
- human review (what I checked or corrected, or `none`): none in this entry; the human approved the scope before the work. No protected file was committed. Commands that required approval: none

### 2026-10-22 — Engineer: #108 stage 1 (pre-review edits)

- date: 2026-10-22
- task/issue: #108 stage 1 only, implemented as a subagent (not closed; QA and the Reviewer not yet run)
- agent role: Software Engineer subagent, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement stage 1 of #108 following the PM grooming comment, with the human's answers of 2026-10-22; no new key prompt saved
- files changed: `_docs/plan-summary.md`, `_docs/architecture.md`, `_docs/roadmap.md` (check-in line only), this log
- verification (tests run, reviewer verdict): `make verify` run before commit (result in the issue comment). No QA or review yet
- human review (what I checked or corrected, or `none`): none in this entry; the human decided A16-A18, Q8, Q10, Q-A and Q-B before the work. No protected file was committed. Commands that required approval: none

### 2026-10-22 — Reviewer: plan review of #108 (FAIL)

- date: 2026-10-22
- task/issue: #108, Reviewer run 1 at `84e99fd` (roadmap step 14)
- agent role: Reviewer, a fresh general-purpose subagent launched by the orchestrator, following `_docs/prompts/reviewer-plan-review.md` with run notes (the prompt's "OpenCode wrote the plan" sentence corrected; documents-reviewed list per the human's decision)
- model: claude-sonnet-5-5 (Claude Code). Recorded exception, human decision 2026-10-22: same tool as the plan's authors, not the author's model for most of the plan (claude-opus-5-5), but the same model as the Engineer subagents of #107 and #108 stage 1 (claude-sonnet-5-5), which edited the documents just before the run
- prompt or instruction given (or link to a file in `_docs/prompts/`): `_docs/prompts/reviewer-plan-review.md` plus the orchestrator's run notes; no new key prompt saved
- files changed: `_docs/reviews/2026-10-22-plan-review.md` (d31cb02, the Reviewer's only commit); this log entry (appended by the orchestrator)
- verification (tests run, reviewer verdict): verdict `Reviewer: FAIL at 84e99fd`; 24 findings (1 High, 14 Medium, 9 Low), 5 questions for the human. `git show --stat d31cb02` lists one path. `make assert-clean` PASS at d31cb02. The Reviewer read `openapi.yaml` line by line to line 1349 and checked lines 1350-2309 by search only (stated in the review file)
- human review (what I checked or corrected, or `none`): none yet; the High-finding disposition is pending the human. No protected file was committed. Commands that required approval: none

### 2026-10-22 — Engineer: #108 stage 2 (plan review 1 fixes)

- date: 2026-10-22
- task/issue: #108 stage 2, implemented as a subagent: the Medium findings 2-15 and Low findings 16-18, 20-21, 22 (`docker-runbook.md` only), 23 and 24 of `_docs/reviews/2026-10-22-plan-review.md` (not closed; QA and the second Reviewer run not started)
- agent role: Software Engineer subagent, local sandbox on `main`
- model: claude-sonnet-5-5 (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's stage 2 instruction with the human's decisions of 2026-10-22; no new key prompt saved
- files changed: `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`, `_docs/testing.md`, `_docs/tasks.md`, `_docs/plan-summary.md`, `_docs/roadmap.md`, `_docs/aws-setup.md`, `_docs/planning-process.md`, `_docs/docker-runbook.md`, this log; commits b9e3c23 (WP2), 2a0e169 (WP3), ca470b5 (WP4), 5fcfa8f (WP5), aa9b93a (WP6), 971457b (WP8) and the log commit that follows. `specs.md`, `AGENTS.md`, `Makefile`, `_docs/agent-kit/*`, `opencode.json`, `.claude/*`, `agent-kit.conf` and `_docs/rubric-evidence.md` untouched
- verification (tests run, reviewer verdict): `make openapi-validate` exit 0 on the edited `openapi.yaml` (22 operations); read-only `.scratch/` scripts recounted the test case IDs (56 submission, 26 Showcase), the register labels and locations, the task headings (1-39), dependencies and the dependency table (no mismatch); `make verify` result is in the issue comment. No QA or review yet
- human review (what I checked or corrected, or `none`): none in this entry. No protected file was committed. Commands that required approval: none

### 2026-10-23 — Reviewer: plan review of #108 run 2 (PASS)

- date: 2026-10-23
- task/issue: #108, Reviewer run 2 at `46dd403` (roadmap step 14)
- agent role: Reviewer, a fresh OpenCode general-purpose subagent launched by the orchestrator, following `_docs/prompts/reviewer-plan-review.md` with run notes (the prompt's "OpenCode wrote the plan" sentence corrected; `openapi.yaml` read in full; documents-reviewed list per the human's decision; only the review file committed)
- model: `opencode/deepseek-v4.1-flash-free` (OpenCode). The handoff named Claude Code sonnet for run 2; subagents in this environment inherit the main session model, and the review file records the actual model. Human decision 2026-10-23: accept this run as the independent run because it is a different tool and model from the plan's authors (`claude-opus-5-5` and the sonnet engineers), which is the stronger independence; the deviation from the sonnet choice is recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): `_docs/prompts/reviewer-plan-review.md` plus the orchestrator's run notes; no new key prompt saved
- files changed: `_docs/reviews/2026-10-22-plan-review-2.md` (`fc89dcf`, the Reviewer's only commit); this log entry (appended by the orchestrator)
- verification (tests run, reviewer verdict): verdict `Reviewer: PASS at 46dd403`; 4 new findings (0 High, 2 Medium, 2 Low) and 2 questions; all 14 earlier Mediums and the E8 High re-checked; `git show --stat fc89dcf` lists one path; `make assert-clean` PASS at `fc89dcf`; `openapi.yaml` read in full (2421 lines)
- human review (what I checked or corrected, or `none`): the human accepted this run and approved filing one follow-up issue for the leftover findings. No protected file was committed in this entry. Commands that required approval: none

### 2026-10-23 — Orchestrator: #108 stage 2 QA and close-out

- date: 2026-10-23
- task/issue: #108 closed (roadmap step 14)
- agent role: Orchestrator (main session), with a QA subagent, a PM subagent and an Engineer subagent, local sandbox on `main`
- model: `opencode/deepseek-v4.1-flash-free` (OpenCode); the subagents inherited it
- prompt or instruction given (or link to a file in `_docs/prompts/`): the step 14 handoff note and the human's decisions of 2026-10-22 and 2026-10-23; no new key prompt saved
- files changed: `README.md` (`f14ac52`); `AGENTS.md` (`bbce6fb`, protected); `_docs/roadmap.md` and this log; `_session-summaries/issue-108-plan-review.md`; the review file `fc89dcf`; the follow-up issue #109 (GitHub, no repository file)
- verification (tests run, reviewer verdict): QA PASS at `46dd403` (comment 6354307995), `make verify` PASS (62 tests, type check, whitespace, no weakened tests), `make openapi-validate` OK (22 operations); `make assert-clean` PASS after QA and after the Reviewer; the AGENTS.md approval record on #108 matches `git show` (read-only `.scratch/` check, 0 mismatches)
- human review (what I checked or corrected, or `none`): the human approved the AGENTS.md phase-line diff as written (decision question, 2026-10-23), accepted the Reviewer run 2 model, and approved filing one follow-up issue. Protected commit `bbce6fb` with `HUMAN_APPROVED=1`; record comment 6354792932. Commands that required approval: `HUMAN_APPROVED=1 git commit` for AGENTS.md (merits request, protected file); `gh issue create` for #109 (PM, merits request); `make issue-close N=108` (ask rule)

### 2026-10-23 — Engineer: #74 backend skeleton and shared test harness

- date: 2026-10-23
- task/issue: #74 (task 1, "Backend skeleton with one passing test"), implemented as a subagent; issue not closed, QA not run
- agent role: Software Engineer subagent, local sandbox on `main`
- model: `opencode/deepseek-v4.1-flash-free` (OpenCode)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement the PM grooming comment 6355211703, with the human's D1 = A and approved dependency batch; no new key prompt saved
- files changed: `backend/pyproject.toml`, `backend/uv.lock`, `backend/vulntriage/__init__.py`, `backend/vulntriage/main.py`, `tests/conftest.py`, `tests/network_guard.py`, `tests/test_smoke.py`, `tests/test_network_guard.py`, `tests/fixtures/MANIFEST.md` (commit `e673df2`); `.github/workflows/verify.yml` and `Makefile` (working-tree changes left uncommitted for approval at hand-over); this log
- verification (tests run, reviewer verdict): `make test` PASS (frontend 62 tests, backend 3: `test_smoke`, `U-NET`, `I-NET`); `make verify BASE=8910c8a` PASS WITH WARNINGS (whitespace PASS; type check PASS; the only warnings are "test fixtures changed" for the new `tests/conftest.py` and `tests/fixtures/MANIFEST.md`, which are additions, not loosened fixtures); red run with the guard temporarily disabled: U-NET and I-NET both failed (`DID NOT RAISE OutboundNetworkBlocked`), temporary edit reverted; `LLM_MODE=live` manual run exited 4 before collection; scope greps empty; no QA or review yet
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: `uv lock` and `make install` for the approved fastapi/uvicorn/sqlalchemy/pytest batch (network downloads, pre-approved by the human in this session); `git commit` including `.github/workflows/verify.yml` was blocked by the kit hook, which requires `HUMAN_APPROVED=1` (returned to the orchestrator; the CI file is uncommitted); the protected `Makefile` diff is left uncommitted for the orchestrator's `HUMAN_APPROVED=1` commit

### 2026-10-23 — Orchestrator: #74 close-out

- date: 2026-10-23
- task/issue: #74 (task 1, "Backend skeleton with one passing test"), orchestration after the Engineer hand-over: commits, QA, decision point, close-out
- agent role: Orchestrator (main session), resumed after a usage-limit stop; the earlier part of the session ran on `opencode/deepseek-v4.1-flash-free` and this close-out on Claude Code (`claude-sonnet-5-5`)
- model: `claude-sonnet-5-5` (Claude Code) for the close-out steps recorded here
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to pick up the stopped session from its transcript; no new key prompt saved
- files changed: `961f322` (CI: uv 0.13.1), `f2afe1e` (`Makefile`, protected), `4952e6b` (`AGENTS.md`, protected), `bacf137` (`_session-summaries/issue-074-backend-skeleton.md`); this log entry and the `_docs/roadmap.md` check-in. The first three commits were made in the earlier part of the session; the close-out only confirmed them against `git log` and the issue comments
- verification (tests run, reviewer verdict): QA PASS at `f2afe1e` (comment 6356100822); QA's `make verify BASE=8910c8a` PASS WITH WARNINGS (62 frontend + 3 backend tests; the only warning is "test fixtures changed" for the new harness files); `make assert-clean` PASS after QA (as reported in the earlier session). I did not re-run `make verify` in the close-out; the tree was clean at `4952e6b`
- human review (what I checked or corrected, or `none`): the human approved the Makefile diff (record 6355572492) and the AGENTS.md diff (record 6356140221), both committed with `HUMAN_APPROVED=1`, and approved filing the npm-vulnerability follow-up, filed as #111 (Not in S1). I checked the usage log's earlier Engineer entry: its "Makefile and CI uncommitted" statement was true at hand-over and is superseded by the commits above. Commands that required approval: `HUMAN_APPROVED=1 git commit` for `Makefile` and `AGENTS.md` (protected files); `make issue-comment` and `make issue-close` (ask rules)

### 2026-10-23 — Engineer: #26 data model and SQLite persistence (implemented, committed)

- date: 2026-10-23
- task/issue: #26 (task 3, "Backend data model and SQLite persistence"), implemented as a subagent in two stages (second stage after the orchestrator ran `make backend-lock`/`backend-install` and committed the Makefile as d811e9b); issue not closed, QA not run
- agent role: Software Engineer subagent, local sandbox on `main`
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement PM grooming comment 6356748748 with the human's six decisions (Alembic approved, `backend-lock` target only, no Brief, all notification enum values, ORM append-only guard, one `DATABASE_URL` setting); no new key prompt saved
- files changed: `backend/uv.lock`, `backend/vulntriage/db/{__init__,enums,identity,models,session}.py`, `backend/alembic.ini`, `backend/migrations/{env.py,script.py.mako,versions/0001_initial_schema.py}`, `backend/pyproject.toml` (alembic), `tests/conftest.py`, `tests/test_db_schema.py`, `tests/test_db_migration.py`, `_docs/testing.md` (U-SCHEMA, U-ENUM, U-CONSTRAINT, U-AUDIT); this log
- verification (tests run, reviewer verdict): after the lock, `make backend-test` first failed the drift test (the model's inferred float column vs the migration; fixed by declaring `Float` explicitly), then passed: 56 passed. `make verify` PASS WITH WARNINGS (frontend 62, backend 56, type check and whitespace PASS; the only warning is "test fixtures changed" for `tests/conftest.py`, which now enables the foreign-key pragma, a tightening; `tests/fixtures/MANIFEST.md` is flagged only because the diff base is origin/main). No QA or review
- human review (what I checked or corrected, or `none`): none yet. Commands that required approval: protected `Makefile` commit d811e9b with `HUMAN_APPROVED=1` (merits request, protected file); `make backend-lock` and `make backend-install` (network, new dependency alembic 1.20.1 with mako 1.4.3 and markupsafe 3.0.4); WebFetch of the PyPI alembic JSON

### 2026-10-23 — Orchestrator: #26 data model and SQLite persistence, close-out; #112 filed

- date: 2026-10-23
- task/issue: #26 (task 3), orchestration: PM grooming, Engineer, QA, decision point, close-out; and filing #112 (push-check image) at the human's request
- agent role: Orchestrator (main session) with PM, Software Engineer and QA subagents
- model: `claude-sonnet-5-5` (Claude Code) for the orchestrator and all three subagents
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction "work ok S1: #26 (task 3)", then the human's answers to the decision questions; no new key prompt saved
- files changed: `d811e9b` (`Makefile`, protected), `8ec6313` (Engineer's implementation), `b3e08a7` (`_docs/architecture.md`), `b6086fa` (`AGENTS.md`, protected), `_session-summaries/issue-026-data-model-sqlite.md`, `_docs/roadmap.md` check-in; this log entry
- verification (tests run, reviewer verdict): QA PASS at `8ec6313` (comment 6356915049, 17 grooming criteria); QA's `make verify` PASS WITH WARNINGS (62 frontend + 56 backend tests; the only warning is the tightened `tests/conftest.py` fixture and the origin/main-based `MANIFEST.md` flag); `make assert-clean` PASS after QA with HEAD unchanged at `8ec6313`. I did not re-run `make verify` after the later `architecture.md` and `AGENTS.md` commits, which change no code
- human review (what I checked or corrected, or `none`): the human approved Alembic, the exact `Makefile` diff (record 6356828269) and the `AGENTS.md` diff (record 6356930604), the architecture rewording, and noting QA's risks only. I replaced one muddled criterion in the PM's #112 draft before filing. Commands that required approval: `HUMAN_APPROVED=1 git commit` for `Makefile` and `AGENTS.md` (protected files); `make backend-lock` and `make backend-install` (network, new dependency); `make issue-comment` and `make issue-close` (ask rules)

### 2026-10-23 — Engineer: #112 push-check image Dockerfile (committed, not built)

- date: 2026-10-23
- task/issue: #112 (push-check image); issue not closed, QA not run
- agent role: Software Engineer subagent, local sandbox on `main`
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #112 with the human's decisions (custom image, Python 3.12 baked in, `ci/push-check/Dockerfile`, all four extra tools); no new key prompt saved
- files changed: `ci/push-check/Dockerfile` (new, commit 83260c0); this log. `AGENTS.md` not edited (proposed diff returned to the orchestrator)
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (62 frontend + 56 backend tests; the warning is the fixtures flag against origin/main from earlier issues, not from this change). The image was NOT built or tested: there is no Docker in this container. Versions looked up by web fetch: pip-audit 2.10.1 (PyPI), Terraform 1.17.0 with SHA-256 sums (releases.hashicorp.com), Python 3.12.15 (python.org), node:24.22.0-bookworm digest (Docker Hub), uv 0.13.1 release exists (GitHub). Unverified: the npm bundled in the base image, ghcr.io/astral-sh/uv:0.13.1 tag, offline `uvx` from the baked cache
- human review (what I checked or corrected, or `none`): none. Commands that required approval: none

### 2026-10-23 — Orchestrator: #112 push-check image (QA PASS on the static criteria; issue left open)

- date: 2026-10-23
- task/issue: #112 (push-check image), orchestration: PM draft and filing, Engineer, QA
- agent role: Orchestrator (main session) with PM, Software Engineer and QA subagents
- model: `claude-sonnet-5-5` (Claude Code) for the orchestrator and all three subagents
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's request to file an issue for the push-check failure, then their answers (custom image, Python baked in, Dockerfile in the repo, all four extra tools, scheduled right after #26); no new key prompt saved
- files changed: `83260c0` (`ci/push-check/Dockerfile`), `9902d07` (`AGENTS.md`, protected), `_session-summaries/issue-112-push-check-image.md`, `_docs/roadmap.md` check-in; this log entry
- verification (tests run, reviewer verdict): QA PASS for the criteria checkable by reading (comment 6357004988) at `9902d07`; `make verify` PASS WITH WARNINGS (62 frontend + 56 backend tests); `make assert-clean` PASS after QA. The image was not built or run (no Docker in this container); the criteria that need the image are not verified and wait for the human
- human review (what I checked or corrected, or `none`): the human approved filing #112, the image scope, and the `AGENTS.md` text (record 6356988788). I corrected one muddled criterion in the PM draft before filing. Commands that required approval: `HUMAN_APPROVED=1 git commit` for `AGENTS.md` (protected file); `make issue-comment` (ask rule)

### 2026-10-23 — Orchestrator: #112 step-by-step guide for the human

- date: 2026-10-23
- task/issue: #112 (push-check image), at the human's request: a detailed guide saying where each step runs
- agent role: Orchestrator (main session), no subagent
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked for a step-by-step guide in `_docs` with more detail than the bullet points, including where to run each command; no new key prompt saved
- files changed: `_docs/push-check-image-guide.md`; this log
- verification (tests run, reviewer verdict): none. The guide was written from `environments.md`, the `pre-push` script, the Dockerfile and QA's command list (comment 6357004988). None of its commands was run: there is no Docker here, and the sandbox's `git remote` setup was not checked. No QA
- human review (what I checked or corrected, or `none`): none

### 2026-10-23 — Software Engineer: #76 asset registration and repository ingestion

- date: 2026-10-23
- task/issue: #76 (S1 task 4); issue not closed, QA not run
- agent role: Software Engineer subagent, local sandbox on `main`
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #76 from the PM grooming comment 6357191954 and correction 6357691953, with the human's decisions D1-D7 (dependencies `httpx` and `packaging` already committed by the human; token `GITHUB_READ_TOKEN`; interim scan status; `Scan` row as the job; `local_packages`; unguarded `POST /assets`; Makefile diff returned, not committed); no new key prompt saved
- files changed: commits a6a342f (parsers), 6ba1cae (reader, hand-written fixtures, recorder, `.env.example`, MANIFEST), 1d7c25f (scan and worker), c5ef99b (`POST /assets`, `main.py`, `tests/test_smoke.py` route assertion); this log. `Makefile` and `AGENTS.md` not edited (proposed Makefile diff returned)
- verification (tests run, reviewer verdict): `make verify BASE=fb33f75` PASS WITH WARNINGS (62 frontend + 240 backend tests; the warnings are the one rewritten smoke assertion `paths == {}` -> `paths == {"/assets"}` and new fixture files). No live GitHub call was made; the fixtures are hand-written. Reader endpoints and header names are unverified (VERIFY markers in `github.py`)
- human review (what I checked or corrected, or `none`): none. Commands that required approval: none

### 2026-10-23 — Software Engineer: #76 follow-up after QA PASS

- date: 2026-10-23
- task/issue: #76 follow-up (QA risk 1 and doc notes); issue not closed
- agent role: Software Engineer subagent, local sandbox on `main`
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's two-task follow-up (make `read_file` and the include check agree; apply the `testing.md` and `architecture.md` notes); no new key prompt saved
- files changed: commit 9a7950d (`github.py`, `scan.py`, `tests/test_github_reader.py`, `tests/test_ingest.py`); commit c3f5a46 (`_docs/testing.md`, `_docs/architecture.md`); this log
- verification (tests run, reviewer verdict): `make backend-test` 246 passed; `make verify` PASS WITH WARNINGS (62 frontend + 246 backend tests; warnings are the fixture files changed since origin/main, none touched in this follow-up). No reviewer run. After QA FAIL (comment 6359044871) the fixture-layout note in `_docs/testing.md` was corrected to the real `<owner>__<repo>/contents/<path>` layout
- human review (what I checked or corrected, or `none`): none. Commands that required approval: none

### 2026-10-23 — Orchestrator: #76 asset registration and repository ingestion, close-out

- date: 2026-10-23
- task/issue: #76 (task 4), orchestration: PM grooming, Engineer, QA twice, decision point, close-out
- agent role: Orchestrator (main session) with PM, Software Engineer and QA subagents
- model: `claude-sonnet-5-5` (Claude Code) for the orchestrator and all subagents
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to start the next task that would not interfere with #112, then to pause after grooming, then to continue; no new key prompt saved
- files changed: `fb33f75` (dependencies), `95eb7bf` (`Makefile`, protected), `_session-summaries/issue-076-asset-ingestion.md`, `_docs/roadmap.md` check-in; this log entry. The Engineer's commits are recorded in its own entries
- verification (tests run, reviewer verdict): QA FAIL once on a wrong fixture-layout line in `_docs/testing.md` (comment 6359044871), then QA PASS at `2f54435` (comment 6359063365); `make verify` PASS WITH WARNINGS (62 frontend + 246 backend tests); `make assert-clean` PASS after each QA run
- human review (what I checked or corrected, or `none`): the human approved `httpx` and `packaging`, the exact `Makefile` diff (record 6358822028), the fixes at the decision point, and the held `AGENTS.md` line. I added the dependencies myself and ran the lock. Commands that required approval: `make backend-lock` and `make backend-install` (network, new dependencies); `HUMAN_APPROVED=1 git commit` for `Makefile` (protected file); `make issue-comment` and `make issue-close` (ask rules)

### 2026-10-23 — Orchestrator: #112 close-out on the human's report

- date: 2026-10-23
- task/issue: #112 (push-check image), closing after the human's image steps
- agent role: Orchestrator (main session), no subagent
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's message that the real push, the broken-install check and the report-back "all worked fine"; no new key prompt saved
- files changed: `_session-summaries/issue-112-push-check-image.md`, `_docs/roadmap.md` check-in; this log entry
- verification (tests run, reviewer verdict): none run by me. The image steps were run by the human, who gave no output, so versions, image size and the offline `uvx` result are not recorded. QA's earlier PASS covered the static criteria only (comment 6357004988)
- human review (what I checked or corrected, or `none`): the human ran the image steps themselves. Commands that required approval: `make issue-comment` and `make issue-close` (ask rules)

### 2026-10-23 — Software Engineer: #116 README audience and outcome positioning

- date: 2026-10-23
- task/issue: #116 (README audience and outcome in "The problem"); issue not closed
- agent role: Software Engineer subagent, local sandbox on `main`
- model: `claude-sonnet-5-5` (Claude Code)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #116 with the human's three decisions (audience option 1, submission-build claims only, extend "The problem"); no new key prompt saved
- files changed: `README.md` (one audience paragraph and a five-item outcome list added before "VulnTriage addresses that gap"); this log
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (62 frontend + 246 backend tests; the one warning is `tests/fixtures/github/repositories.txt`, modified before this task and not staged). README grep for Dependabot, alerts, unlike, better than, instead of, available, works today and years showed only pre-existing text and the new "alert fires" line. No reviewer run
- human review (what I checked or corrected, or `none`): none. Commands that required approval: none

### 2026-10-24 — Agent: #77 (task 5) OSV matching and fixed-version resolution

- date: 2026-10-24
- task/issue: #77 (task 5): OSV matching, fixed-version resolution, finding creation
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to review the roadmap and work the next issue, noting data from `make record-fixtures SOURCE=github` is present; no new key prompt saved
- files changed: new `backend/vulntriage/ingest/{versions,osv_ranges,osv,matcher}.py`; edits to `backend/vulntriage/ingest/scan.py` and `backend/vulntriage/worker.py` (inject an optional OSV client; replace the interim status rule with the OSV result; add the E3 `feed unavailable` path); new `tests/osv_stub.py` and tests `tests/test_{versions,osv_ranges,osv_client,matcher}.py`; edits to `tests/test_ingest.py` (updated the two interim tests, added the `I-FINDINGS` scan-to-findings case); extended `tests/record_fixtures.py` with `SOURCE=osv`; new `tests/fixtures/osv/` (querybatch, four vuln advisories, packages.txt, README); `tests/fixtures/MANIFEST.md` rows; this log entry
- new dependencies: none. npm SemVer 2.0.0 precedence is implemented in-house in `versions.py` (a SemVer library is approval-gated); PyPI ordering uses `packaging`, already a dependency
- verification (tests run, reviewer verdict): the sandbox is network-mode INTEGRATIONS_ONLY with no PyPI access, so `uv sync`, `make install`, `make test` and `make verify` could NOT be run here. All changed/new Python files byte-compile under CPython 3.12.13. The two pure algorithms were validated standalone against the spec examples and edge cases: SemVer 2.0.0 precedence (semver.org §11.4 chain, leading `v`, numeric vs string); and the five-step fixed-version rule loaded from the real `osv_ranges`/`versions` modules (spec example 1.2.0→1.2.5 and 2.0.0→2.0.1, open-ended and last_affected-only → no fixed version, overlapping intervals → lowest value outside every containing interval, urllib3 merged-advisory case → 1.26.17). The alias union-find grouping was validated standalone (two advisories sharing a CVE → one group; a bridging advisory → one group). The full pytest suite still needs a run by the human on a networked machine (or CI) before merge
- human review (what I checked or corrected, or `none`): pending. The human should run `make install && make verify` (push-check image `vulntriage-push-check:1`) before merging; the `Makefile` was not edited so no protected-path approval was needed

### 2026-10-24 — Agent: #78 (task 6) KEV and EPSS enrichment

- date: 2026-10-24
- task/issue: #78 (task 6): CISA KEV and FIRST EPSS signal enrichment per finding CVE
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue in the plan after #77 merged; no new key prompt saved
- files changed: new `backend/vulntriage/ingest/signals.py` (KEV + EPSS clients and `enrich_asset`); edits to `backend/vulntriage/ingest/scan.py` and `backend/vulntriage/worker.py` (optional KEV/EPSS clients threaded through `run_scan`/`run_pending_scans`/`ScanWorker`; enrichment runs after matching and never changes the OSV scan status, E3); new `tests/signals_stub.py` and `tests/test_signals.py` (U-KEV, U-EPSS, U-FEED); `tests/test_ingest.py` (I-FINDINGS extended to assert KEV/EPSS flow through a scan); `tests/test_github_reader.py` (recorder tests updated now that kev/epss are implemented); `tests/record_fixtures.py` extended with `SOURCE=kev`/`epss`; new `tests/fixtures/kev/`, `tests/fixtures/epss/`, `tests/fixtures/cves.txt`; `tests/fixtures/MANIFEST.md` rows; this log entry
- new dependencies: none
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY with no PyPI access, so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13; the KEV/EPSS fixtures parse and the signal parse helpers (date/float, catalogue membership, EPSS filtering) and `kev_value` derivation were validated standalone. The full pytest suite needs a run by the human on a networked machine (or CI) before merge
- human review (what I checked or corrected, or `none`): pending. The human should run `make install && make verify BASE=origin/main` before merging; the `Makefile` was not edited, so no protected-path approval was needed. VERIFY: the KEV catalogue URL/fields and the EPSS `cve=` batch size/fields are marked in `signals.py`; confirm with a live `make record-fixtures SOURCE=kev` / `SOURCE=epss`

### 2026-10-24 — Agent: #79 (task 7) deterministic ranking and rank reason

- date: 2026-10-24
- task/issue: #79 (task 7): deterministic tier, total order and rank reason per finding
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue in the plan after #78 merged; no new key prompt saved
- files changed: new `backend/vulntriage/ingest/ranking.py` (pure `tier_for`, `sort_key`, `order_findings` and the DB-writing `rank_asset`); edit to `backend/vulntriage/ingest/scan.py` (run `rank_asset` after enrichment, replacing the placeholder rank fields from task 5); new `tests/test_ranking.py` (U-TIER, U-TIE, the I-RANK worked example, and a DB `rank_asset` case); `tests/test_ingest.py` (I-FINDINGS asserts the scan's tiers); this log entry
- new dependencies: none; no new threshold or enum beyond architecture § Prioritisation (T = 0.10, A16-A18)
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY with no PyPI access, so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13; the pure ranking logic (all four tier rules, the 0.10 inclusive threshold, the P1-first precedence, and the architecture worked example order `fnd-0001, 0002, 0004, 0005, 0003, 0006`) was validated standalone. The full pytest suite needs a run by the human on a networked machine (or CI) before merge
- human review (what I checked or corrected, or `none`): pending. The human should run `make install && make verify BASE=origin/main` before merging; the `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #80 (task 8) finding lifecycle, re-scan and audit trail

- date: 2026-10-24
- task/issue: #80 (task 8): re-scan status transitions (fixed/withdrawn/reopen/restore) and the audit trail
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue in the plan after #79 merged; no new key prompt saved
- files changed: new `backend/vulntriage/ingest/lifecycle.py` (the status machine, lifecycle creation and append-only audit writes); `backend/vulntriage/ingest/matcher.py` refactored so `match_asset` reconciles every (asset, package, vulnerability) on each scan — grouping withdrawn advisories too, lazy vulnerability upsert so a withdrawn-at-first-sight advisory records nothing (E4), and closing findings OSV no longer returns; `backend/vulntriage/ingest/ranking.py` sets the E8 `signals_changed` flag on a risk-accepted finding whose tier rises or KEV becomes listed; new `tests/test_lifecycle.py` (US-10, E4 withdraw/restore, E7 reopen, E8 close, audit trail) with a programmable OSV client; `tests/test_ranking.py` E8 flag test; this log entry
- new dependencies: none
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY with no PyPI access, so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13; the full lifecycle state machine (US-10 fix, E4 withdraw/restore, E7 reopen, E8 close) was validated standalone against every transition. The full pytest suite needs a run by the human on a networked machine (or CI) before merge
- human review (what I checked or corrected, or `none`): pending. The human should run `make install && make verify BASE=origin/main` before merging; the `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #80 follow-up, two fixes from the human's make verify run

- date: 2026-10-24
- task/issue: #80 (task 8), after the human ran `make install && make verify` (6 failed, 319 passed)
- agent role: implementation agent (Kiro Web session), on `feat/80-lifecycle-rescan-audit`
- model: Auto (server-selected)
- prompt or instruction given: the human pasted the failing `make verify` output
- files changed: `backend/vulntriage/ingest/scan.py` (clear `finding_dependencies` links to the old dependency rows before the per-scan `DELETE FROM dependencies`, so a re-scan with existing findings does not trip the foreign key — a real production bug, not only a test bug); `backend/vulntriage/ingest/ranking.py` (the first ranking, with empty `rank_inputs`, is a baseline and no longer sets `signals_changed`); `tests/test_lifecycle.py` (the `_set_version` helper mirrors the scan worker's link-clearing); `tests/test_ranking.py` unchanged in intent; this log entry
- verification (tests run, reviewer verdict): the human's run reported 319 passed and 6 failed before these fixes; the failures were the FK violation on re-scan (5 cases) and the spurious first-rank escalation (1 case). Re-run still owed to the human — the Kiro Web sandbox has no PyPI access, so I could not run `make verify` here; the changed files byte-compile under CPython 3.12.13
- human review: pending re-run of `make verify BASE=origin/main`

### 2026-10-24 — Agent: #81 (task 9a) session authentication and CSRF guard

- date: 2026-10-24
- task/issue: #81 (task 9a): session cookie auth, CSRF header guard, login lockout, owner-match rule
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue after #80 merged, then "approve recommendation" for the Argon2id dependency; no new key prompt saved
- new dependencies: `argon2-cffi` added to `backend/pyproject.toml` with the human's explicit approval (Option A) for Argon2id password hashing (architecture § Security boundaries A30). `backend/uv.lock` is NOT yet updated — the sandbox has no PyPI access, so the human must run `make backend-lock` (then `make backend-install`) before `make verify`
- files changed: new `backend/vulntriage/api/security.py` (Argon2id hash/verify, session create/resolve/delete with hashed 256-bit ids and 30-min idle / 8-hour absolute lifetimes, the `vt_session` cookie flags, the in-process login lockout, the CSRF + wrong-consumer `require_session` guard, and the A30 owner-match helper); new `backend/vulntriage/api/auth.py` (`POST /auth/login`, `POST /auth/logout`, `GET /auth/me`); `backend/vulntriage/main.py` (register the auth router, the login-throttle app state, and an HTTPException handler that renders the contract `{code, message}` Error shape); `backend/pyproject.toml` (`argon2-cffi`); new `tests/test_api_auth.py` (I-AUTH-SESSION and the guard cases); this log entry
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI, no argon2/fastapi installed), so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13; the dependency-free logic (login-lockout sliding window and expiry, the owner-match trim/case-fold rule, and the session-token hashing) was validated standalone. The full pytest suite needs a run by the human after `make backend-lock`
- human review (what I checked or corrected, or `none`): the human approved adding `argon2-cffi`. Pending: `make backend-lock && make backend-install && make verify BASE=origin/main`. The `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #82 (task 9b) findings, assets, re-scan and risk-acceptance API

- date: 2026-10-24
- task/issue: #82 (task 9b): the frontend resource endpoints behind the session guard
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue after #81 merged; no new key prompt saved
- files changed: new `backend/vulntriage/api/findings.py` (`GET /findings`, `GET /findings/{id}`, `POST /findings/{id}/risk-acceptance`); new `backend/vulntriage/api/serializers.py` (the Finding/FindingWithAsset wire shape: aliases, derived KEV/EPSS, dependency entries, affected-range projection, audit trail, joined asset); `backend/vulntriage/api/assets.py` (guarded `POST /assets` with session + security-lead; added `GET /assets`, `GET /assets/{id}`, `PATCH /assets/{id}` with per-field audit + re-score, `POST /assets/{id}/rescan`; `asset_to_wire` now shows the latest scan's warnings); `backend/vulntriage/ingest/ranking.py` (`ranked_findings` for the server rank order); `backend/vulntriage/main.py` (register the findings router); new `tests/auth_helpers.py`; updated `tests/test_api_assets.py` (authenticate as a security lead with CSRF) and `tests/test_smoke.py` (route set); new `tests/test_api_findings.py` (I-RISK + reads + error-order + owner-match); this log entry
- new dependencies: none (argon2-cffi was added in #81)
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI, no fastapi/argon2 installed), so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13; the affected-range projection was validated standalone. The contract's error order (risk acceptance: 404 then owner-403 then 422; registerAsset/updateAsset: role-403 before body-422) is enforced by reading the raw body and validating it after the earlier checks, instead of via a pydantic body param. The full pytest suite needs a run by the human (and will exercise the `test_api_assets.py` guard changes)
- human review (what I checked or corrected, or `none`): pending `make verify BASE=origin/main`. The `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #83 (task 10a) service API and notification jobs

- date: 2026-10-24
- task/issue: #83 (task 10a): n8n/responder service operations, top-tier job creation, showcase stubs
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue after #82 merged; no new key prompt saved
- files changed: new `backend/vulntriage/api/service_settings.py` (`N8N_API_TOKEN`/`MCP_API_TOKEN`/`RESPONDER_API_TOKEN` readers, same pattern as `settings.py`); new `backend/vulntriage/api/service_auth.py` (bearer guards `require_n8n`/`require_mcp`/`require_responder`: 401 missing/invalid, 403 wrong-consumer incl. a session cookie, constant-time compare); new `backend/vulntriage/api/service.py` (submission ops `POST /signals/refresh`, `POST /scans`, `GET /responder/findings/{id}`, `GET /responder/notification-jobs`; contract-only showcase stubs for the three `/notification-jobs` ops, `GET /reports/weekly-digest`, and the three `/mcp/` ops); new `backend/vulntriage/ingest/notifications.py` (A27 due-date windows, `(lifecycle id, kind)` idempotency key, `create_top_tier_jobs` with a synthesised valid `traceparent`, idempotent via the unique key); `backend/vulntriage/ingest/scan.py` (create top-tier jobs after ranking); `backend/vulntriage/main.py` (register the service router); `tests/test_api_service.py`; `tests/test_smoke.py` (route set); this log entry
- new dependencies: none
- submission vs showcase: only the `top tier` job kind is created for submission (keyed `(lifecycle, "top tier")`); `signals changed`/reminder/escalation/digest/issue-close job creation, the n8n claim/report/digest behaviour, and the MCP tools are Showcase, present here only as contract-only stubs so task-14 conformance can compare every operation. The delivery worker (claim/email/sent/failed) is task 37; the daily scheduler is task 38
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI/fastapi/argon2), so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13; the service-auth decision table, the A27 due dates, the idempotency key and the traceparent format were validated standalone. The full pytest suite needs a run by the human
- human review (what I checked or corrected, or `none`): pending `make verify BASE=origin/main`. `.env.example` left unchanged: the n8n/MCP tokens are Showcase and the responder token arrives with task 28, per `tasks.md`. The `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #84 (task 10b) MCP and responder read APIs

- date: 2026-10-24
- task/issue: #84 (task 10b): the three MCP read operations and getAsset's dual consumer; responder reads confirmed
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next task after #83 merged; no new key prompt saved
- files changed: `backend/vulntriage/api/service.py` (replaced the three MCP stubs with real reads: `GET /mcp/top-exposures` → `RankedFinding[]` open-only in rank order with `limit` 1-50 and `assetId` filter/404; `GET /mcp/vulnerabilities/{id}/assets` → `AffectedAssets` resolving any alias, known/unknown distinguishable; `GET /mcp/findings/{id}` → `McpFinding` = FindingWithAsset + labelled `untrustedAdvisoryData`); `backend/vulntriage/api/serializers.py` (new `untrusted_advisory_data`, `ranked_finding_to_wire`, the fixed `UNTRUSTED_LABEL`); `backend/vulntriage/api/service_auth.py` (new `require_session_or_mcp` for the shared `getAsset`); `backend/vulntriage/api/assets.py` (`GET /assets/{id}` now accepts a session cookie OR the MCP token); new `tests/test_api_mcp.py`; this log entry
- new dependencies: none
- submission vs showcase: the MCP operations are Showcase (the MCP server with its four tools is task 32), built here as the read API so the task-14 conformance test and the US-12 untrusted-data boundary hold. The responder read ops were already built in #83 (task 10a) and are re-covered by their tests. No write tool exists; every write with the MCP token is 403
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI/fastapi), so `make install`/`make test`/`make verify` could NOT be run here. All changed/new files byte-compile under CPython 3.12.13. The full pytest suite needs a run by the human
- human review (what I checked or corrected, or `none`): pending `make verify BASE=origin/main`. `.env.example` unchanged (MCP token is Showcase). The `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #85 (task 11) frontend dashboard read views

- date: 2026-10-24
- task/issue: #85 (task 11): the dashboard read views for assets and ranked findings
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next issue after #84 merged; no new key prompt saved
- files changed: `frontend/src/test/vulntriage.test.tsx` (added the `F-ASSET` and `F-STATUS` describe blocks that render the real `/assets`, `/findings` and `/findings/{id}` screens and assert US-1, US-4, US-5 and US-6 against the services layer); this log entry
- what was already present: the dashboard read views, components and services/types layer were built by the #34/#45 SPA-shell work (`routes/_authed.assets.index.tsx`, `_authed.findings.index.tsx`, `_authed.findings.$findingId.tsx`, `components/vt/*`, `services/*`). #85 confirms they meet the US-1/4/5/6 acceptance criteria and adds the named `F-ASSET`/`F-STATUS` cases the test strategy calls for; no new view code or dependency was needed
- new dependencies: none (used the existing services layer and types)
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY — the npm registry is blocked (registry.npmjs.org 403), so `npm ci`, `make frontend-test` and `make frontend-typecheck` could NOT be run here. The new tests use only symbols already imported in the suite and assert against the existing components' real markup (verified by reading `FindingsTable.tsx`, `Badges.tsx`, the asset/finding routes and `mockData.ts`: `formatEpss(null)` is `"EPSS: n/a"`, the status label text, the `asset-owner`/`asset-scan`/`rank-reason`/`brief-pending`/`brief-unavailable` test ids). The full frontend suite + type check need a run by the human
- human review (what I checked or corrected, or `none`): pending `make verify` (runs the frontend suite and type check). The `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #86 (task 12) risk acceptance, audit trail and re-scan UI

- date: 2026-10-24
- task/issue: #86 (task 12): the dashboard write path — accept risk, audit trail, manual re-scan
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next task after #85 merged; no new key prompt saved
- files changed: `frontend/src/test/vulntriage.test.tsx` (added the `F-STATUS write path` describe block covering US-10 and US-11 through the real accept form, the assets re-scan button and the AuditTrail component); this log entry
- what was already present: the write views were built by the #34/#45 SPA shell — the accept-risk form (`routes/_authed.findings.$findingId_.accept.tsx`), the `AuditTrail` component, the per-row re-scan button (`routes/_authed.assets.index.tsx`), `validateRiskReason`, and the mock `acceptRisk`/`reScan` with the contract error order (401, 404, owner-403, 422, 409), the who/when/previous/reason audit entry, and no automated `risk accepted`. #86 confirms US-10/US-11 and adds the named write-path coverage; no view or service code changed
- new dependencies: none
- CSRF note: the custom CSRF header (`X-Requested-With`) is a concern of the real API-backed `Services` implementation (built later); the mock services layer has no HTTP, so it enforces only the error-to-`ServiceError` mapping and the behaviour. Recorded as a VERIFY for the real client
- verification (tests run, reviewer verdict): the Kiro Web sandbox blocks the npm registry (`registry.npmjs.org` 403), so `npm ci`, `make frontend-test` and `make frontend-typecheck` could NOT be run here. The new tests use only symbols already imported in the suite and assert via `getByRole`/`getByLabelText`/direct service state (avoiding the ambiguous-text pitfall from #85), checked against the real `accept` route, `AuditTrail.tsx`, assets route and `mockService.ts`. The full frontend suite + type check need a run by the human. `I-RISK` (the backend half) already passes from #82
- human review (what I checked or corrected, or `none`): pending `make verify`. The `Makefile` was not edited, so no protected-path approval was needed

### 2026-10-24 — Agent: #87 (task 13) backend test layers and stored fixtures

- date: 2026-10-24
- task/issue: #87 (task 13): consolidate the backend unit and SQLite integration test layers, fixtures and manifest
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next task after #86 merged; no new key prompt saved
- what was already present: tasks 1-12 built the harness incrementally — the network guard with `U-NET`/`I-NET` (`tests/test_network_guard.py`), all stubs (`github_stub`, `osv_stub`, `signals_stub`, `conftest`), the github/osv/kev/epss fixtures, `tests/record_fixtures.py` (`SOURCE=github|osv|kev|epss`), `tests/fixtures/MANIFEST.md`, and `make test` already running the backend suite after the frontend suite
- files changed: added a module-level `pytestmark` (`unit` or `sqlite_integration`) to the 10 test files that had none, so every `U-*`/SQLite `I-*` case is selectable by marker for the task-21 CI split: `test_github_reader.py`, `test_parser_package_lock.py`, `test_parser_requirements.py`, `test_parser_uv_lock.py` (unit); `test_api_assets.py`, `test_api_auth.py`, `test_api_findings.py`, `test_api_mcp.py`, `test_api_service.py`, `test_ingest.py` (sqlite_integration). `backend/pyproject.toml` gained `addopts = "--strict-markers"` (an unknown marker is now an error; it does not require a mark). Files with existing per-test marks (`test_db_*`, `test_network_guard`, `test_ranking`, `test_smoke`, and the already-marked modules) were left as they were. This log entry and the session summary
- new dependencies: none
- scope: this is a harness/fixtures consolidation task. The `U-*`/SQLite `I-*` cases for tasks 1-12 are implemented; checks that belong to later tasks (I-CONTRACT task 14, I-SCHED task 38, I-OWNER-* task 37, the Showcase I-* cases) stay with those tasks. The task's own check is "`make test` passes with both layers; `make verify` passes"
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI), so `make test`/`make verify` could NOT be run here. All test files byte-compile under CPython 3.12.13; the marker coverage was audited (every file resolves to `unit`, `sqlite_integration` or a correct mix), the MANIFEST was confirmed to name every captured fixture with a source and capture date, and `--strict-markers` was confirmed not to require a mark (only to reject an unknown one). The full suite needs a run by the human
- human review (what I checked or corrected, or `none`): pending `make verify`. The `Makefile` was not edited (so no protected-path approval); `backend/pyproject.toml` is not protected

### 2026-10-24 — Agent: #88 (task 14) OpenAPI conformance and validation

- date: 2026-10-24
- task/issue: #88 (task 14): the I-CONTRACT conformance test comparing FastAPI's generated document with _docs/openapi.yaml
- agent role: implementation agent (Kiro Web session, local sandbox on `main`)
- model: Auto (server-selected)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to work the next task after #87 merged, then "approve recommendation option a" for the conformance granularity; no new key prompt saved
- decision: Option A (human-approved). The hand-built routes (raw-body parsing, dict returns, Depends guards) emit no declared query/header params, no request/response schemas and no security block, so a deep schema compare against app.openapi() is impossible and making the routes conformant is tasks 9b/10a/10b (out of scope). The test compares the dimensions the routes actually express: the path set (template variables normalised so the contract's {id} matches FastAPI's {finding_id}), the method set per path, the success status code per operation, and the security requirement per operation checked against the Depends guard wired on the route (mapping require_session->cookieAuth, require_session_or_mcp->cookieAuth+mcpAuth, require_n8n->n8nAuth, require_mcp->mcpAuth, require_responder->responderAuth, no guard->public). GET /health is excluded by name
- files changed: new `tests/test_openapi_conformance.py` (the comparison, a strict scoped reader of the contract's paths block with no new YAML dependency, the /health-exclusion test, an extra-route-fails test, and a deliberate-mismatch test that flips login's 2xx status in a copy); this log entry
- new dependencies: none (the contract paths block is read by a small strict parser, not a YAML library)
- ignored fields (named per the acceptance criteria): title, description, summary, operationId, examples; and — because the current routes do not declare them — query/header parameters, request/response body schemas and the non-2xx responses. VERIFY: a full schema/response/declared-security conformance test needs response_model and declared parameters/security on every route (a task-9b/10 change)
- verification (tests run, reviewer verdict): the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI/fastapi), so `make test`/`make verify` could NOT be run here. The test byte-compiles under CPython 3.12.13; the strict contract parser was run standalone against the real _docs/openapi.yaml and extracted exactly 22 operations with the right status codes (16x200, 3x202, 2x204, 1x201) and security counts (cookieAuth 9, mcpAuth 4, n8nAuth 6, responderAuth 2; login/logout public), which cross-checks the generated side's guard counts. The full suite needs a run by the human; `make openapi-validate` is unchanged (the contract was not edited)
- human review (what I checked or corrected, or `none`): the human approved Option A. Pending `make verify`. The `Makefile` and `_docs/openapi.yaml` were not edited (openapi.yaml is read-only here), so no protected-path approval was needed

#### 2026-10-24 — follow-up: #88 conformance test fix after first `make verify`

- date: 2026-10-24
- The human's first `make verify` run of PR #130 reported 383 passed, 5 failed: the 5 new conformance tests failed because `_generated_ops()` returned an empty set. Root cause: the generated side identified routes by the `APIRoute` class (`isinstance(route, APIRoute)`), which matched zero routes at the granularity the test iterated.
- Fix (commit `bf3b633` on `feat/88-openapi-conformance`): the generated side now takes the path set, method set and success status from `app.openapi()["paths"]` — the document the test exists to check and the same source `test_smoke` reads successfully — and reads the security requirement off each route's `Depends` guard, matching routes to openapi operations by normalised path + method. Guards are found by duck-typing (`path` + `methods` + `dependant`), not by class identity. Removed the now-unused `from fastapi.routing import APIRoute` import; the two inline helper tests (`/health` exclusion, extra-route-fails) now reuse `_generated_ops(app)`.
- Cross-check (standalone, since the sandbox has no PyPI/fastapi): the backend declares exactly 22 route operations with status codes 1×201, 3×202, 2×204, 16×200, and guard counts require_session 8, require_session_or_mcp 1, require_n8n 6, require_mcp 3, require_responder 2 (→ cookieAuth 9, mcpAuth 4, n8nAuth 6, responderAuth 2; login/logout public). These match the contract parser's 22 ops and the recorded status/security tallies, so the generated and contract sides reconcile.
- verification: still pending the human's `make verify` (sandbox cannot run the fastapi suite). The file byte-compiles under CPython 3.12.13 and carries no trailing whitespace.

#### 2026-10-24 — follow-up 2: #88 guard detection for GET /auth/me

- date: 2026-10-24
- With the `openapi()`-derived generated side in place, the second `make verify` run passed path/method/status for all 22 operations and left a single failure: `('/auth/me', 'get')` reported no guard schemes (`set()`) against the contract's `{cookieAuth}`. `/auth/me` is guarded by `Depends(require_session)` like the other cookie routes, but `_guard_schemes()` scanned only the route dependant's top-level `dependencies` and missed it there.
- Fix (commit `48789b2`): `_guard_schemes()` now walks the entire `dependant` tree — the root dependant plus every sub-dependency, with an `id()`-based cycle guard — so a guard call is found at whatever depth FastAPI nests it. The scheme map and the rest of the test are unchanged.
- verification: pending the human's next `make verify` (the sandbox has no fastapi, so this cannot be run here). The file byte-compiles under CPython 3.12.13 and has no trailing whitespace.

#### 2026-10-24 — follow-up 3: #88 guard read from the endpoint signature

- date: 2026-10-24
- The recursive dependant-tree walk still returned no schemes for `GET /auth/me`, so the guard is simply not reachable via `route.dependant.dependencies` the way the other cookie routes' guards are (that route takes the guard as a value, `user: User = Depends(require_session)`, with no `Request` parameter; the already-passing routes all take `request: Request` plus the guard).
- Fix (commit `8d8d31b`): read guards from the source of truth — the endpoint function signature. Each parameter whose default is a FastAPI `Depends` marker exposes the dependency callable on `.dependency`; the reader collects any whose `__name__` is a known guard and recurses into dependency callables (cycle-guarded). The dependant-tree walk is kept as a backstop for router- or decorator-level `dependencies=[...]` that do not appear in the endpoint signature. Added `import inspect`.
- verification: pending the human's next `make verify`. The file byte-compiles under CPython 3.12.13 and has no trailing whitespace. If this still misses `/auth/me`, the next step is a one-off diagnostic (printing the route's dependant tree and signature) run in the devcontainer, since the sandbox cannot import fastapi.

#### 2026-10-24 — follow-up 4: #88 route walk through FastAPI's own route iterator

- date: 2026-10-24
- agent role: implementation agent (Claude Code cloud session, on `feat/88-openapi-conformance`)
- model: see the session record (not recorded in the repository)
- Root cause: the locked FastAPI (0.161.1) does not copy included routes onto `app.routes`; `include_router` adds one `_IncludedRouter` per router, whose routes live on `.original_router.routes` (not `.routes`). The diagnostic run in the devcontainer showed `app.routes` holding only the four docs routes plus four `_IncludedRouter` objects, so the guard map was empty for every API route. The earlier "only `/auth/me` fails" reading was the guard test stopping at its first failing assertion, not 21 routes passing.
- Fix: `_route_guards()` now walks the app with `fastapi.routing.iter_route_contexts(app.routes)`, the iterator `app.openapi()` itself uses, which yields each effective route with its full path, methods and `original_route` (endpoint and `dependant`). Removed the hand-written `_iter_leaf_routes()` and the TEMP `test_DIAG_dump_guard_map`; kept `test_the_route_tree_is_flattened_and_guards_are_read` as the regression test.
- verification: `tests/test_openapi_conformance.py` 7 passed; `make verify` passed (389 tests, type check, whitespace, weakened-test check).

#### date: 2026-10-24 — task/issue: task 2 (#75) — planning evidence and tracker hygiene

- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to close out S1 by completing task 2 and to add a step-by-step local end-to-end verification guide under `_docs/`.
- files changed: `_docs/tasks.md` (evidence note under task 2 only), `_docs/verify-locally.md` (new local verification guide), `README.md` (index link), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): `make verify` NOT run — the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no PyPI/npm), so dependencies cannot be installed here. The task 2 change is documentation only. CI on `main` is green at the time of writing (latest run success at `b007833`). The human must run `make verify` on a networked machine before relying on it.
- human review (what I checked or corrected, or `none`): none yet. Follow-up recorded in `_docs/verify-locally.md` and the task-2 note: `make dev` / `dev-start` / `dev-stop` (task 11 / #85 acceptance) are not in the Makefile and should be filed as a follow-up.

#### date: 2026-10-24 — task/issue: Tier B review, documentation tidy-up and Milestone B grooming (step 12 for Milestone B)

- date: 2026-10-24
- agent role: PM + doc tidy (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to review the Tier B roadmap for missing planning, tidy the spread-out/confusing docs, then groom the Tier B tasks into issue proposals with a "PM confirm with human" note (no issues filed yet).
- files changed: `_docs/tier-b-build.md` (new consolidated Tier B build sheet), `_docs/roadmap.md` (S1 status -> done; D-numbering disambiguation note), `README.md` (index link to the build sheet), `_session-summaries/planning-2026-10-23-tier-b-grooming.md` (new grooming proposal, 8 issues with acceptance criteria and PM->human confirm blocks), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): docs only; no code changed. `make verify` not run (sandbox has no npm/PyPI; nothing to test). Assessment grounded in tasks.md, architecture.md, testing.md and roadmap.md.
- human review (what I checked or corrected, or `none`): none yet. The grooming doc is a proposal; issues are not filed and await the human's confirmation of the open points. Also flagged separately: PR #135 is needed because the #133 work did not reach `main` via the earlier PR chain.

#### date: 2026-10-24 — task/issue: #133 — add make dev / dev-start / dev-stop and wire the frontend to the backend (completes task 11's single-command Tier A run)

- date: 2026-10-24
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to implement #133 (option A): real fetch service against the existing contract plus the make dev targets, so make dev runs end-to-end.
- files changed: `frontend/src/services/httpService.ts` (new real fetch service), `frontend/src/services/index.ts` (bind services to httpServices; keep mock as a fixture), `frontend/vite.config.ts` (dev server API proxy, one origin), `frontend/src/test/vulntriage.test.tsx` (vi.mock @/services so route-render tests use the mock), `frontend/src/test/http-service.test.ts` (new: cookie, CSRF, 403->forbidden), `Makefile` (dev/dev-start/dev-stop; PROTECTED, human-approved), `AGENTS.md` (Commands: make dev; PROTECTED, human-approved), `_docs/verify-locally.md` (make dev is now the primary path), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): `make verify` NOT run — the Kiro Web sandbox is network-mode INTEGRATIONS_ONLY (no npm/PyPI), so the frontend suite and type check cannot run here. The human must run `make verify` (and a manual `make dev` end-to-end check) on a networked machine before merge; CI on the PR runs the frontend tests.
- human review (what I checked or corrected, or `none`): the human approved the Makefile and AGENTS.md (protected) changes in this session before the commit.

#### date: 2026-10-24 — task/issue: #31 (T3) — Compose-based dev container so Postgres runs as a sibling service

- date: 2026-10-24
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to pick up #31 and approved: add psycopg[binary], keep the write/restart/read persistence test as #68, use a Compose dev container with a small app Dockerfile.
- files changed: `.devcontainer/compose.yaml` (new; app + pinned postgres:16.4 `db` sibling, no docker.sock, workspace-only host mount, pgdata named volume, healthcheck), `.devcontainer/Dockerfile` (new; python:3.12 app image), `.devcontainer/devcontainer.json` (converted from single `image` to Compose: dockerComposeFile/service/runServices/workspaceFolder; DATABASE_URL=postgresql+psycopg://vt:vt@db:5432/vt), `backend/pyproject.toml` (add psycopg[binary]>=3.2,<4; human-approved), `AGENTS.md` (protected: Environment line + the Docker gotcha, human-approved), `_docs/ai-usage-log.md` (this entry), session summary.
- verification (tests run, reviewer verdict): NOT run here. The Kiro Web sandbox is read-only for uv's Python dir and has no PyPI, so `uv lock`, `make backend-lock`, `make backend-test` and the Docker rebuild cannot run. The human must, during the rebuild: run `make backend-lock` (psycopg is a new dependency, so `uv.lock` must be regenerated before `uv sync --locked`), rebuild the dev container, then run `make backend-test` with `DATABASE_URL` set to the `db` service and quote the result. The dedicated write/restart/read persistence test stays #68.
- human review (what I checked or corrected, or `none`): the human approved psycopg[binary], the #68 scope split, and the Compose-devcontainer + app Dockerfile approach before the build; the protected AGENTS.md diff is approved in-session before its HUMAN_APPROVED commit.

#### date: 2026-10-24 — task/issue: Milestone B issues filed (#137-#144) after human confirmation of the grooming proposal

- date: 2026-10-24
- agent role: PM (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human confirmed the grooming proposal: file now, AWS account + Budgets ready so no D5 fallback date needed, security-scan tools and Terraform approved.
- files changed: filed 8 GitHub issues #137-#144 (tasks 15-22); updated `_session-summaries/planning-2026-10-23-tier-b-grooming.md` (status FILED with the numbers), `_docs/roadmap.md` (check-in log line), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): none; grooming/doc work only. Issue bodies follow the Milestone A house style (Goal / Acceptance criteria / Out of scope / Constraints); no milestone or label set, matching the Milestone A convention.
- human review (what I checked or corrected, or `none`): the human approved the grooming open points before filing.

#### date: 2026-10-24 — task/issue: #137 (task 15) — one-command Compose stack, incl. the /api prefix move (Option B

- date: 2026-10-24 
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to start #137, then (on hitting the SPA/API path collision) preferred Option B and asked for an impact analysis + proposal before changes; then approved the recommendations (Option B, root_path=/api, /api/health).
- files changed: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `compose.yaml`, `backend/.dockerignore`, `frontend/.dockerignore`, `.env.example` (rewritten), `backend/vulntriage/main.py` (/health route + root_path=/api), `frontend/src/services/httpService.ts` (API_BASE=/api), `frontend/src/test/http-service.test.ts` (2 URL assertions), `frontend/vite.config.ts` (single /api proxy with rewrite), `_docs/openapi.yaml` (servers.url=/api), `_docs/api.md` (base-path + health notes), `Makefile` (compose-up/compose-down; PROTECTED, human-approved), two session summaries (#137 and the /api proposal), this log entry.
- verification (tests run, reviewer verdict): NOT run here — the Kiro Web sandbox has no Docker/PyPI and a read-only uv dir, so `make compose-up` and `make verify` cannot run. main.py byte-compiles. The human runs `make verify` (frontend + conformance must stay green; backend/tests unchanged by the /api move) and `make compose-up`, then hard-refreshes /findings to confirm the SPA loads.
- human review (what I checked or corrected, or `none`): the human approved Option B and D1/D2 after reading the impact proposal; the protected Makefile (compose targets) is approved in-session before its HUMAN_APPROVED commit.

#### date: 2026-10-24 — task/issue: #137 follow-up — document the Compose stack in _docs/verify-locally.md

- date: 2026-10-24  
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked that the verify steps live in _docs/verify-locally.md.
- files changed: `_docs/verify-locally.md` (new §7 "Run the full Compose stack (phase S2)" with make compose-up, the /env setup, the /api one-origin note and the /findings hard-refresh acceptance; corrected the §6 Vite proxy note to the single /api prefix; renumbered Clean up to §8; added Compose troubleshooting rows and updated the status/scope notes), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): docs only; no code changed. Not run (sandbox has no Docker/PyPI).
- human review (what I checked or corrected, or `none`): none yet; part of PR #147.

#### date: 2026-10-24 — task/issue: #137 fixes from make verify (human-run on the branch)

- date: 2026-10-24
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human ran make verify on feat/137-compose-stack; it FAILED on a stale .env.example test and warned on a deprecated root_path.
- files changed: `backend/vulntriage/main.py` (drop the deprecated FastAPI(root_path="/api") — D1 was optional/cosmetic; proxy strips /api regardless), `tests/test_github_reader.py` (rewrite test_env_example_* to assert the task-15 contract: required names present, showcase names absent, no committed values), `_docs/api.md` (note the app sets no root_path), two session summaries, this log entry.
- verification (tests run, reviewer verdict): byte-compiled; the new env-example test logic validated standalone against the real .env.example (passes). Full pytest not runnable here (no venv/PyPI). The human re-runs make verify on the branch.
- human review (what I checked or corrected, or `none`): the human's make verify run found both issues; this commit addresses them. No test was weakened — the env-example test now asserts a stronger, accurate contract.

#### date: 2026-10-24 — task/issue: #138 (task 16) — real-Postgres integration tests

- date: 2026-10-24
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to work the next task (#138) and approved the design recommendations (transaction-rollback isolation, reuse compose.yaml's db under vt-test, integration-only via the existing sqlite_integration marker, E-GUARD = vt db + compose host check).
- files changed: `tests/conftest.py` (db_engine/db_session + sqlite_* aliases, guard_test_database_url E-GUARD, Alembic upgrade in pytest_configure, VT_TEST_DATABASE_URL branch), `tests/test_integration_guard.py` (new E-GUARD unit cases), `ci/test-integration.sh` (new orchestration), `compose.test.yaml` (new test-only db port override), `Makefile` (test-integration + postgres-integration; PROTECTED, human-approved), `_docs/verify-locally.md` (§7 integration subsection), session summary, this log entry.
- verification (tests run, reviewer verdict): NOT fully run here — sandbox has no Docker/venv/PyPI. Python test files byte-compile; ci/test-integration.sh passes `bash -n`; the E-GUARD accept/reject decisions were cross-checked standalone (3 accept, 5 reject). The human runs `make verify` (SQLite + E-GUARD unit cases) and `make test-integration` (Postgres) on the host.
- human review (what I checked or corrected, or `none`): the human approved the four design decisions before the build; the protected Makefile targets are approved in-session before the HUMAN_APPROVED commit.

#### date: 2026-10-24 — task/issue: #139 (task 19) — CI test pipeline

- date: 2026-10-24
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to work the next task (#139) and chose Option B (thin make targets per marker, so every CI job runs through make).
- files changed: `.github/workflows/verify.yml` (six jobs: unit, sqlite-integration, frontend, openapi-validation, postgres-integration, plus the retained verify gate), `Makefile` (test-unit / test-sqlite-integration / test-conformance; PROTECTED, human-approved), session summary, this log entry.
- verification (tests run, reviewer verdict): NOT run here (sandbox can't run GitHub Actions or the suite). Verified every `- run: make ...` maps to a real Makefile target, and that the unit/sqlite_integration markers partition the backend suite (no unmarked test). The human confirms on the first PR CI run.
- human review (what I checked or corrected, or `none`): the human chose Option B over Option A (raw pytest in CI); the protected Makefile targets are approved in-session before the HUMAN_APPROVED commit.

#### date: 2026-10-24 — task/issue: #138 fix — Postgres isolation switched from shared-connection rollback to fresh schema

- date: 2026-10-24- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): the #139 CI run exercised make test-integration for the first time; the postgres-integration job FAILED with AttributeError: 'dict' object has no attribute 'transaction_status' on 155 tests.
- files changed: `tests/conftest.py` (replace the single-shared-connection rollback with fresh-schema isolation: db_engine drop_all at setup/teardown on Postgres, each test's factory runs create_all as on SQLite; remove the Alembic _run_migrations helper and its call), `_session-summaries/issue-138-postgres-integration.md` (record the change and the reason), this log entry.
- verification (tests run, reviewer verdict): conftest byte-compiles; the fix removes the pooled-connection-proxy misuse that caused the AttributeError. Confirmed every sqlite_integration module builds its own schema via create_all (so fresh-schema works), except test_network_guard whose one integration case needs no tables. The human re-runs make test-integration; CI's postgres-integration job on this fix proves it.
- human review (what I checked or corrected, or `none`): none yet; follow-up fix to the merged #138, discovered by #139's CI.

#### date: 2026-10-24 — fix/111-vite-advisory
  
- date: 2026-10-24
- task/issue: #111 — upgrade Vite from 8.1.5 to 8.1.6 for GHSA-587h-7wmj-h5pm
- agent role: Engineer (OpenCode, software-engineer role)
- model: opencode/deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to implement groomed #111 with D1/D3 (`npm install --save-dev --save-exact vite@8.1.6`), D2 (`make frontend-audit` target, protected Makefile diff approved), and approved the npm network commands and `make install`; return requests instead of running anything needing approval. Groomed body and PM context are in #111 comments 6377705971 and 6377706848.
- files changed: `frontend/package.json`, `frontend/package-lock.json` (vite 8.1.5 -> 8.1.6, exact pin), `Makefile` (add `frontend-audit` target and `.PHONY` entry; PROTECTED, human-approved in-session, committed alone with `HUMAN_APPROVED=1`), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): `make verify BASE=830f14fc0704648502ebe0926d81ed0ad4e2e206` -> PASS (87 frontend tests, 396 backend tests, type check, whitespace, no test files changed). Pre-upgrade `npm audit --json`: 1 high (`vite@8.1.5`, five advisories, metadata high 1 / total 1). Post-upgrade `npm audit --json`: 0 high, 0 critical, 0 total. `make install` twice gave the same lockfile hash `b076df2bd825f867fe1c6a78879b430ce4410d10`.
- human review (what I checked or corrected, or `none`): human approved the exact vite version, the npm install/audit network commands, the `make install` runs, and the exact protected `Makefile` diff before implementation; diff not yet reviewed.

#### date: 2026-10-24 — task/issue: Tier C build sheet (roadmapping document, like tier-b-build.md)

- date: 2026-10-24- agent role: PM / doc (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to start roadmapping the Tier C build document.
- files changed: `_docs/tier-c-build.md` (new; consolidated Tier C/S4 build sheet: per-milestone C2-C9 table with task, builds, depends-on, human step/decision, criterion and done-when; the showcase C1/C4 split; the task-37-built-inside-C3 build-order note; the dependency chain; the open D4 + responder-runtime + main-branch-protection prerequisites; the score checkpoints), `README.md` (index link), this log entry.
- verification (tests run, reviewer verdict): docs only; no code. Grounded in roadmap.md § Tier C milestones, tasks.md tasks 23-29/37-39, architecture.md § Observability / § Responder agent / § Security boundaries, and testing.md. Points to the sources rather than restating design; adds no new precedence rule.
- human review (what I checked or corrected, or `none`): none yet. Flags that D4 (responder false-positive rule, a protected specs.md change) is still open and blocks C6, and that the responder runtime and main branch protection are human prerequisites before task 28.

#### date: 2026-10-24 — task/issue: #141 (task 17) — Terraform verification runbook (written before the Terraform itself)

- date: 2026-10-24- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to write up the Terraform verification steps in _docs if not already there, before writing the Terraform. Running #141 in parallel with the other agent's #140 (no file overlap: #141 adds new terraform/ and a new deploy.yml; it does not touch Makefile or verify.yml).
- files changed: `_docs/terraform-verify.md` (new: §1 static fmt/validate checks that need no AWS, §2 pre-apply security review checklist, §3 per-module apply verification, §4 the #141 dev-URL acceptance, §5 teardown verification; consolidates the Terraform checks that were scattered across architecture.md, aws-setup.md and the push-check guide), `README.md` (index link), this log entry.
- verification (tests run, reviewer verdict): docs only; no code yet. The runbook references real commands (terraform fmt/validate as in push-check-image-guide.md) and the aws-setup.md apply order. The Terraform modules themselves are the next step.
- human review (what I checked or corrected, or `none`): none yet; the runbook defines how the human verifies the modules that come next.

#### date: 2026-10-24 — task/issue: #141 (task 17) — Terraform modules + GHCR build workflow

- date: 2026-10-24- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human approved the recommendations for #141 (Caddy reverse proxy, region ap-southeast-2, Secrets Manager, t3.medium, OIDC-reuse as a variable, SES deferred) and asked that the Terraform verification runbook exist in _docs first (done: _docs/terraform-verify.md).
- files changed: `terraform/README.md`, `terraform/bootstrap/*` (state bucket), `terraform/deploy-roles/*` (OIDC + dev/prod roles), `terraform/server/*` (EC2, EIP, SG, instance role, EBS+DLM snapshots, nightly-stop schedule, user-data.sh, caddy/Caddyfile), each with a terraform.tfvars.example; `.github/workflows/deploy.yml` (new; build-once → tag → GHCR → record digest; dev-deploy job scaffolded for task 21), `.gitignore` (terraform state/tfvars), session summary, this log entry. No Makefile/verify.yml change (parallel with #140).
- verification (tests run, reviewer verdict): NOT run here — the sandbox has no AWS or Terraform. Checked: balanced braces in every .tf, .tfvars.example tracked while state/real tfvars are git-ignored, the workflow uses only GITHUB_TOKEN + the OIDC role. The human runs terraform fmt/validate and every apply per _docs/terraform-verify.md; the task's acceptance (dev sslip.io URL answers, deploy log names a digest) is a human step.
- human review (what I checked or corrected, or `none`): the human approved Caddy and the defaults before the build; the Terraform is reviewed and applied by the human (agents never apply or hold AWS credentials).

#### date: 2026-10-24 — task/issue: Tier C (Milestone C) issue grooming — proposal, not filed
- date: 2026-10-24
- task/issue: Tier C (Milestone C) issue grooming — proposal, not filed
- agent role: PM (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human asked to start grooming the Tier C jobs as was done for Tier B.
- files changed: `_session-summaries/planning-2026-10-23-tier-c-grooming.md` (new; 9 proposed Milestone C issues for tasks 23-29, 37, 38, 39, each with acceptance criteria from tasks.md/architecture.md/testing.md and a PM->human confirm block; filing/build order; the open D4 + responder-runtime + main-branch-protection gates on task 28; the dependency approvals), this log entry.
- verification (tests run, reviewer verdict): docs only; nothing filed. Grounded in the authoritative task descriptions and the Tier C design sections; mirrors the Tier B grooming format.
- human review (what I checked or corrected, or `none`): none yet; the grooming is a proposal awaiting the human's answers to the confirm blocks before any issue is filed.

#### date: 2026-10-24 — task/issue: #154 (task 23) — OpenTelemetry instrumentation and the exclusion helper

- date: 2026-10-24
- task/issue: #154 (task 23) — OpenTelemetry instrumentation and the exclusion helper
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human said work on #154 and approved the 5-package OTel set (incl. opentelemetry-instrumentation-sqlalchemy, kept for the showcase) and showcase notes for host CPU/mem/RPS metrics and the alert owner-annotation decision.
- files changed: new `backend/vulntriage/observability/` (allowlist.py, settings.py, tracing.py, metrics.py, logs.py, __init__.py); `backend/vulntriage/main.py` (setup_tracing/setup_metrics, FastAPI + SQLAlchemy instrumentation); `backend/vulntriage/ingest/scan.py` (scan.run root + repository.read/osv.query/signals.enrich/prioritise child spans; Scan.trace_id from the root span); `backend/vulntriage/ingest/notifications.py` (notification.enqueue span; traceparent from the span, placeholder removed); `backend/pyproject.toml` (5 OTel deps); `tests/test_observability.py` (new); `_docs/roadmap-showcase.md` (X10 host/RPS metrics); `_docs/tier-c-build.md` (alert owner-annotation note); session summary; this log entry.
- verification (tests run, reviewer verdict): NOT run here — the sandbox has no PyPI, so OTel is not installed and make verify/the new tests cannot run. All changed files byte-compile; the allowlist filter was validated standalone (keeps exactly the A32 keys). The human runs make backend-lock then make verify on the host.
- human review (what I checked or corrected, or `none`): the human approved the 5-package set and the two showcase notes before the build. Recorded a task-24 follow-up: the Collector must drop db.statement (SQLAlchemy instrumentation emits it) with a test.

#### date: 2026-10-24 — task/issue: Milestone C issues filed (#154-#163) after human confirmation

- date: 2026-10-24
- task/issue: Milestone C issues filed (#154-#163) after human confirmation
- agent role: PM (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human confirmed the Tier C grooming and said file the issues.
- files changed: filed 10 GitHub issues #154-#163 (tasks 23-29, 37, 38, 39) in build order; updated `_session-summaries/planning-2026-10-23-tier-c-grooming.md` (status FILED with the numbers), `_docs/roadmap.md` (check-in log line), `_docs/ai-usage-log.md` (this entry).
- verification (tests run, reviewer verdict): none; grooming/doc work only. Issue bodies follow the house style (Goal / Acceptance criteria / Out of scope / Constraints); no milestone or label set, matching the Milestone A/B convention. Task 28/#160's Constraints record its gates (D4, responder runtime, main branch protection).
- human review (what I checked or corrected, or `none`): the human confirmed the grooming before filing.

- date: 2026-10-24
- task/issue: #155 (task 24) — observability stack + US-13 dashboard; plus a central pending-verification doc
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human said work on #155 (chosen over #162) and asked to centralize the open cloud/host verification steps in one place.
- files changed: new `observability/` (compose.yaml, otel-collector.yaml with the A32 keep_keys allowlist, prometheus.yml, tempo.yaml, loki-config.yaml, grafana provisioning + the us13-journey dashboard, README.md); new `_docs/pending-verification.md` (cross-issue checklist for #141/#140/#155); `README.md` (index link); session summary; this log entry. No backend/Makefile change, so make verify is unaffected.
- verification (tests run, reviewer verdict): NOT run here — the stack needs Docker, absent in the agent sandbox. The dashboard JSON parses; the YAML/config are hand-checked. The task-24 db.statement drop from #154 is handled by the Collector keep_keys (in-code test already covers the exclusion; the Compose T-REFUSE assertion is task 25). The human runs the stack in a Codespace/cloud/Docker host per observability/README.md and _docs/pending-verification.md.
- human review (what I checked or corrected, or `none`): none yet; Docker-dependent verification is listed in _docs/pending-verification.md.

- date: 2026-10-24
- task/issue: #162 (task 38) — backend scheduler for the daily refresh and scheduled re-scan
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human said work on #162.
- files changed: `backend/vulntriage/scheduler.py` (new Scheduler: run_once/catch_up/tick/start/stop, injected now, last_scheduled_run from Scan rows), `backend/vulntriage/ingest/refresh.py` (new refresh_all helper extracted from the /signals/refresh handler), `backend/vulntriage/api/service.py` (handler calls refresh_all; imports trimmed), `backend/vulntriage/main.py` (lifespan starts/stops the Scheduler behind run_worker; app.state.scheduler), `tests/test_scheduler.py` (new I-SCHED cases), session summary, this log entry.
- verification (tests run, reviewer verdict): NOT run here (sandbox has no PyPI). All files byte-compile; the scheduler time-logic (06:00 gate, 24h catch-up, once-per-day, no-prior-run) validated with a standalone simulation (all paths pass). No new dependency (clock-driven loop, per the issue's dependency note). The human runs make verify; I-SCHED is a make test case (SQLite + stubs, no Docker/network), so no cloud session is needed.
- human review (what I checked or corrected, or `none`): none yet.

- date: 2026-10-24
- task/issue: #156 (task 37) — backend top-tier owner notification and delivery
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human said work on #156 (chosen as the next step in the C3 chain after #154/#155).
- files changed: new `backend/vulntriage/mail/` package — `__init__.py`, `settings.py` (MAIL_TRANSPORT/MAIL_SENDER per-module env readers), `message.py` (plain-text labelled-field formatter, CR/LF header rejection, A31 URL defang), `transport.py` (MailTransport protocol + RecordingTransport in-process sink, MailHogTransport over stdlib smtplib, SesTransport with lazy VERIFY-marked boto3 import, verified-sender refusal, build_transport), `delivery.py` (DeliveryWorker: deliver_pending/start/stop, claim→send→sent/failed, E2/A21 holds, config-error hold, notification.deliver as a child of the stored traceparent, metrics); `backend/vulntriage/observability/tracing.py` (new span_from_traceparent helper via W3C TraceContextTextMapPropagator); `backend/vulntriage/main.py` (lifespan starts/stops the DeliveryWorker behind run_worker; app.state.delivery_worker); `.env.example` (MAIL_* settings); `tests/test_notifications.py` (new I-OWNER-SEND/NOAWS/SENDER/ONCE/HOLD + S-NOTIFY cases); session summary; this log entry.
- verification (tests run, reviewer verdict): NOT run here (sandbox has no PyPI/venv). All modules byte-compile. The pure logic is verified by two standalone sims: the message formatter + defang (every A31 example, header-injection rejection, text/plain body) all pass; the transport verified-sender refusal, build_transport selection/config-error, and the E2/A21 hold-reason branch all pass. The DB-backed I-OWNER-* cases run under `make test` (SQLite + in-process sink, no Docker/AWS/network). The MailHog variants of I-OWNER-NOAWS/SENDER and T-JOURNEY-BE (task 25) run under `make test-compose` — listed in `_docs/pending-verification.md`. The human runs `make verify`.
- new dependencies: none added to backend/uv.lock. MailHog uses stdlib smtplib (the MailHog service was added in #155). The SES route needs boto3, imported lazily inside SesTransport.send and left VERIFY-marked / not added to pyproject.toml until the human's AWS step (per the task text: "ships with MailHog proven and the SES path VERIFY-marked until then").
- human review (what I checked or corrected, or `none`): none yet.

- date: 2026-10-24
- task/issue: #158 (task 26) — US-14 alert metric and provisioned Grafana rule
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human said work on #158 (next step in the C5 milestone after #156 merged), adding the Alerting on User Impact rubric point.
- files changed: `backend/vulntriage/observability/metrics.py` (the observable gauge `vt_top_tier_notification_overdue` now reads stored job state: `compute_overdue_series`/`_series_value` emit per-finding {finding_id,tier} series — 1 for a failed job or a pending/claimed job older than W=30 min from created_at, 0 for a sent job kept 24h after sent_at then dropped, held jobs never emit — plus the always-present label-less 0 heartbeat; `set_overdue_source` installs the DB session factory + injected now seam, mirroring DeliveryWorker/Scheduler); `backend/vulntriage/main.py` (lifespan calls `set_overdue_source(factory)` after the engine is built and `set_overdue_source(None)` on shutdown); new `observability/grafana/provisioning/alerting/us14-overdue.yaml` (the provisioned rule `max by (finding_id, tier)(vt_top_tier_notification_overdue) == 1`, 1-minute eval, noDataState Alerting, dashboard/environment/version annotations; contact points finding-alert = responder webhook + human email and human-email = human only; notification policy routing a finding_id-bearing alert to both and the NoData/default to the human only); new `tests/test_metrics_overdue.py` (SQLite + fake-clock cases for the series logic and the callback through an InMemoryMetricReader); `_docs/pending-verification.md` (new #158 section for the Docker-only Grafana-rule checks); session summary; this log entry.
- verification (tests run, reviewer verdict): NOT run here (sandbox has no PyPI/venv and Python is 3.11 vs the project's >=3.12). All changed/new Python byte-compiles. The overdue decision table (failed=1; pending/claimed 0 before and 1 after the 30-min window; sent 0 kept 24h then dropped; held never emits) is verified by a standalone sim (`.scratch/sim_overdue_series.py`, all boundary cases pass). The new `tests/test_metrics_overdue.py` cases are `make test` cases (SQLite + fake clock + InMemoryMetricReader, no Docker/network) and resolve finding_id by id with an explicit order_by to avoid the SQLite-vs-Postgres row-order trap that broke #156. The Grafana rule is authored here and Docker-verified by the human (listed in `_docs/pending-verification.md` #158); external Grafana details are `VERIFY:`-marked in the YAML. The `alert` Compose test / A-* cases (#159, task 27) and the responder webhook receiver (#160, task 28) are out of scope. The human runs `make verify`.
- new dependencies: none. `backend/uv.lock` should not change (no new package — the gauge uses the already-present opentelemetry/sqlalchemy; the Grafana rule is provisioning YAML).
- human review (what I checked or corrected, or `none`): none yet; the Docker-dependent Grafana-rule verification is listed in `_docs/pending-verification.md`.

- date: 2026-10-24
- task/issue: #157 (task 25) — telemetry Compose test + `make test-compose` JOB selector
- agent role: Engineer (Kiro, Vibe session)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): human said work the recommended next task (#159), which was blocked on #157; then chose "Option C done right" — ship the selector and the non-journey telemetry cases in #157, defer the full scan journey (`T-JOURNEY-BE`) and the feed wiring to a new prerequisite issue; and said to file that prerequisite issue.
- files changed: new `ci/test-compose.sh` (brings up the observability stack under the `vt-telemetry` project, sets the OTLP env, dispatches by `JOB`; `telemetry` runs `T-REFUSE`; `alert`/`responder` exit 3 as "not implemented, tasks 27/28"); new `tests/test_compose_telemetry.py` (the `compose`-marked `T-REFUSE` case), `tests/compose_telemetry.py` (Tempo/Loki query helpers), `tests/compose_driver.py` (drives the backend's real span/log helpers so the Collector drop is exercised); new `tests/test_marker_hygiene.py` (unit guard: the `compose` marker may appear only in the allowlisted compose module, closing the "silently tag a test compose" gap); `backend/pyproject.toml` (register the `compose` marker); `Makefile` (protected, separate human-approved commit): new `test-compose` target + validated `JOB` selector, and `backend-test` gets `-m "not compose"`; `.github/workflows/verify.yml` (new `telemetry` CI job; needs human approval); `_docs/testing.md` (job-table row → `T-REFUSE` shipped, the rest pending #172; a note on the narrowing; US-13 traceability row left as `T-JOURNEY-BE`); `_docs/pending-verification.md` (#157 section); `_docs/roadmap.md` (C5/check-in line); session summary; this log entry. Filed GitHub issue #172 (wire OSV/KEV/EPSS clients into create_app + `VT_FEEDS=fixtures` mode; carries `T-JOURNEY-BE` and the delivery-dependent cases) and posted the scope-update comment on it.
- verification (tests run, reviewer verdict): NOT run here — the telemetry job is Docker-only and the sandbox has no Docker/PyPI/venv (Python 3.11 vs the project's >=3.12). All new/edited Python byte-compiles; `ci/test-compose.sh` passes `bash -n`; the `Makefile` `JOB` validation was exercised with `make -n` (valid passes, bad/multi-word rejected before any shell, empty runs all); the marker-hygiene guard's logic was run as a read-only `.scratch` sim (passes on the clean tree, catches a planted `compose` tag). The `T-REFUSE` case is `compose`-marked and deselected by `make test`/`make verify` (via `-m "not compose"` on `backend-test`), so it never runs or skips in the no-Docker gate (verify.md:26: a new skip/xfail is a hard FAIL — so no placeholder test; visibility is the job-table row and #172). The human runs `make test-compose JOB=telemetry` under Docker (CI route 1), per `_docs/pending-verification.md` #157.
- new dependencies: none. The helpers use stdlib `urllib`; `backend/uv.lock` should not change.
- scope note (recorded decision): the human chose "Option C done right", then narrowed further after review. #157 ships `T-REFUSE` + the `JOB` selector only. The delivery-dependent cases (`T-JOURNEY-BE`, the MailHog forms of `I-OWNER-NOAWS`/`I-OWNER-SENDER`, `T-E6`, and the delivery-half `T-DELIVER-TRACE`) move to prerequisite #172, because each needs the *deployed backend container* to deliver — a host-side driver delivering (my first draft) would test the wrong layer (I-OWNER-NOAWS must prove the container has no AWS credential; I-OWNER-SENDER's refusal must come from the backend's own guard, not a direct `transport.send`). #172 also carries the production feed-wiring gap (a deployed scan currently matches nothing because `create_app` injects no OSV/KEV/EPSS clients) and is needed by task 28/#160 (`P-DEMO-BE`). `T-DELIVER-TRACE` is defined as an export/link check only and must not count toward US-13 (the matrix row stays `T-JOURNEY-BE`). No test was weakened; no placeholder/skip was added.
- human review (what I checked or corrected, or `none`): none yet; the protected `Makefile` and the `.github/` workflow change need the human's approval at commit time, and the Docker verification is listed in `_docs/pending-verification.md`.

- date: 2026-10-24
- task/issue: #159 (task 27) — the `alert` Compose test and CI job (US-14 A-* cases)
- agent role: Engineer (Kiro, cloud session on branch `feat/159-alert-compose-job`)
- model: not recorded
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator said to implement #159 (task 27) as groomed, scope = the `alert` job only (not I-OWNER-SENDER MailHog or T-E6), with the firing-state seam as an in-container manage command, a stdlib stub webhook sink (no new image), and a Compose override (not editing observability/compose.yaml).
- files changed: `backend/vulntriage/manage.py` (new `alert-seed`/`alert-set`/`alert-rescore`/`alert-clear` subcommands — the firing-state seam: create a `top tier` NotificationJob in a named state with set created_at/sent_at/tier, resolvable to a finding through a seeded finding+lifecycle, committed to the same Postgres the overdue gauge reads; backdating only, never touching the backend's W); `tests/alert_webhook_sink.py` (new stdlib `http.server` record-only responder sink — no new dependency, run from the backend image); `tests/compose_alert.py` (new alert helpers: the in-container seam runner via `docker compose run`, the webhook-sink client, MailHog/Prometheus helpers reused from `compose_telemetry.py`); `tests/test_compose_alert.py` (new `compose`-marked A-FIRE/A-FIRE-negative/A-HELD/A-TIER/A-GAP part1+2/A-RESOLVE cases); `tests/test_manage.py` (new SQLite/unit cases for the seam, cross-checked against `compute_overdue_series`); `tests/test_marker_hygiene.py` (allow `test_compose_alert.py` to carry `compose`); `compose.alert.yaml` (new override: Grafana SMTP→MailHog, the webhook-sink service from the backend image, the alert env, and the rule-absent provisioning toggle; does not edit `observability/compose.yaml`); `ci/test-compose.sh` (the `alert` branch now brings the stack up and runs the cases + the rule-absent negative pass; `responder` still returns the not-implemented message); session summary; this log entry; roadmap check-in; `_docs/pending-verification.md` #159 section. NOT committed (protected / needs approval): `.github/workflows/verify.yml` (new `alert` job) — left in the working tree, exact diff in the Engineer comment. The Makefile already wires `COMPOSE_JOBS=alert` (no change needed, confirmed).
- verification (tests run, reviewer verdict): `make verify` / pytest NOT run here — the sandbox blocks PyPI (npm 403) and uv's Python download (read-only home), so no 3.12 venv can be built; Python is 3.11. All new/changed Python byte-compiles; `ci/test-compose.sh` passes `bash -n`; the `JOB=alert` dispatch was exercised with `make -n`. Two read-only `.scratch` sims pass: (1) the firing-state decision table — a standalone copy of `_series_value` confirms the seam's states/backdating map to the 0/1/None the overdue gauge emits (failed=1, pending past/within W=1/0, sent=0 then dropped >24h, held=None) and the recorded-tier-wins invariant; (2) the stub webhook sink end-to-end over a loopback port the script starts/stops — POST a Grafana-shaped firing body, read `/__recorded`, confirm `webhook_finding_ids`/`_is_firing`/`/__reset`. The marker-hygiene guard logic run read-only confirms `compose` appears only in the two allowed modules. The alert cases are `compose`-marked and DESELECTED by `make test`/`make verify` (`-m "not compose"`), so they never run or skip in the no-Docker gate; the seam's own logic is covered under `make test` in `tests/test_manage.py`. The human/CI runs `make verify` and `make test-compose JOB=alert` under Docker; the `.github/workflows/verify.yml` `alert` job needs human approval (see `_docs/pending-verification.md` #159).
- new dependencies: none. The seam is in the existing `manage.py`; the sink and helpers are stdlib (`http.server`, `urllib`, `subprocess`); the sink runs from the backend image already in the stack; `backend/uv.lock` unchanged.
- choices made the issue does not cover: (a) the seam creates a self-contained finding→lifecycle→job chain directly (deterministic, Q2 option A) rather than driving a real pygoat P1 over HTTP — either is valid per the issue; the SET-state + backdate seam is required regardless and is all these commands do; (b) the A-FIRE-negative rule toggle is a provisioning COPY with the rule file removed, selected by `VT_ALERT_PROVISIONING` and recreated with `--no-deps grafana`, driven by `VT_ALERT_RULE_ABSENT=1` in a second pass (the committed provisioning tree is untouched); (c) the stub sink is built from the same `./backend` build context (reuses the backend image, no new image) with the module bind-mounted and `PYTHONPATH=/sink`; (d) `compose.alert.yaml` overrides the imported `grafana` service's env/volumes via a third `-f` file — supported on current Compose (compose-go PR #559), VERIFY-marked for pinned CI versions.
- human review (what I checked or corrected, or `none`): none yet; the `.github/workflows/verify.yml` `alert` job is uncommitted pending approval, and the Docker-only alert run is listed in `_docs/pending-verification.md` #159 with the `VERIFY:` points (GF_SMTP_* keys, NoData semantics, webhook POST shape, firing latency, imported-service override).

- date: 2026-10-24
- task/issue: #159 (task 27) — troubleshoot the failing `verify / alert` CI job on PR #183
- agent role: Engineer (Claude Code, local sandbox, branch `feat/159-alert-compose-job`)
- model: Claude Opus 5.5 (`claude-opus-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human pasted the PR #183 checks page and asked to troubleshoot and fix the failing alert job.
- files changed: `tests/test_compose_alert.py` (the firing cases seed a `claimed` job backdated 31 min past W instead of a `failed` job, via a new `_seed_firing_job` helper); this log entry.
- verification (tests run, reviewer verdict): read the CI log of run 40094180389 (A-FIRE and A-RESOLVE timed out after 300s in `wait_for_overdue_value`; A-TIER and A-GAP part 2, which make the same wait, passed). Cause found by reading the code: the backend's DeliveryWorker polls every 30s and retries `failed` jobs, and the seeded asset has an owner email, so the seeded `failed` job was delivered to MailHog and set to `sent` (gauge 0), usually before the default 60s metric export reported it as 1. The worker never selects `claimed`, and #159's A-FIRE criterion allows "`pending`/`claimed` backdated past W". `make verify` passed (454 backend + 87 frontend). The `compose` alert cases were NOT run here (no Docker); the PR's CI `alert` job is the check.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none yet.

- date: 2026-10-25
- task/issue: #159 (task 27) — second failing `verify / alert` run on PR #183 (at e8cd932)
- agent role: Engineer (Claude Code, local sandbox, branch `feat/159-alert-compose-job`)
- model: Claude Opus 5.5 (`claude-opus-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human pasted the PR #183 checks page again after pushing e8cd932.
- files changed: `tests/test_compose_alert.py` (A-FIRE no-leak check: the fixed routing labels `alertname`/`grafana_folder` must equal the rule file's title/folder exactly and are skipped by the forbidden-substring scan); this log entry.
- verification (tests run, reviewer verdict): read the CI log of run 40142529529: 1 failed, 5 passed, 1 skipped. The claimed-job fix worked (A-TIER, A-GAP part 2 and A-RESOLVE passed; A-FIRE reached both sinks). A-FIRE failed only on `responder alert label leaked 'owner'`, because the rule title "Top-tier owner notification overdue" is the `alertname` label; the labels were exactly `{alertname, finding_id: 1, grafana_folder: VulnTriage, tier: P1}`. `make verify` passed (1 assertion added, 0 removed). The rule-absent negative pass has not run in CI yet (the harness stops after a positive failure). The `compose` cases were NOT run here (no Docker).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none yet.

- date: 2026-10-25
- task/issue: #159 (task 27) — third failing `verify / alert` run on PR #183 (at d7027ad), and the PR's conflict with `main`
- agent role: Engineer (Claude Code, local sandbox, branch `feat/159-alert-compose-job`)
- model: Claude Opus 5.5 (`claude-opus-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human pasted the PR #183 page showing the alert job failing and a conflict in `_docs/pending-verification.md`.
- files changed: `ci/test-compose.sh` (`run_alert` starts Grafana last, after a bounded wait for the overdue-gauge heartbeat in Prometheus; new `wait_for_heartbeat`); this log entry; then a merge of `origin/main` into the branch.
- verification (tests run, reviewer verdict): read the CI log of run 40145258781: 1 failed, 5 passed, 1 skipped; A-FIRE passed. A-HELD failed on a `[RESOLVED]` email sent at 00:11:51 whose labels were `alertname`, `datasource_uid=prometheus`, `grafana_folder`, `ref_id=A` (no `finding_id`): the rule's start-up NoData instance, which fired because Grafana evaluated before the backend's first 60s metric export, and resolved after the default route's 5m group_interval, after A-FIRE's MailHog reset. `bash -n ci/test-compose.sh` passed. The `compose` cases were NOT run here (no Docker).
- new dependencies: none (`curl` is on the CI runner).
- human review (what I checked or corrected, or `none`): the human approved committing the `main` merge with `HUMAN_APPROVED=1`; the agent-kit hook still refused it (protected files must be committed alone, which a merge cannot do), so the merge was aborted here and done on GitHub instead (c055c84).

- date: 2026-10-25
- task/issue: #159 (task 27) — fourth `verify / alert` result on PR #183 (at c055c84): the `push` run passed, the `pull_request` run failed
- agent role: Engineer (Claude Code, local sandbox, branch `feat/159-alert-compose-job`)
- model: Claude Opus 5.5 (`claude-opus-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human pasted the PR page and a GitHub summary of job 121038402739, and asked whether anything is wrong with verify.
- files changed: `tests/compose_alert.py` (new `wait_for_resolution`, `_subject`); `tests/test_compose_alert.py` (`_seed_firing_job` records its finding; the fixture teardown waits for each fired finding's resolved webhook and `[RESOLVED]` email before resetting both sinks, skipped in the rule-absent pass); `_docs/pending-verification.md` (removed a stray `feat/159-alert-compose-job` line and a duplicate "Last updated" line left by the GitHub merge); this log entry.
- verification (tests run, reviewer verdict): read the log of run 40149690798 (pull_request): 2 failed, 4 passed, 1 skipped. A-HELD's unexpected webhook and the A-GAP part 1 failure were `status: resolved` notifications for finding 1 (A-FIRE's; startsAt 01:15:20, endsAt 01:21:20, `grafana_state_reason=MissingSeries`): Grafana resolves a missing series about two evaluations after it leaves Prometheus, after the old teardown had already finished. The `push` run at the same commit passed because the timing was different. `make verify` passed (0 assertion lines added or removed). The `compose` cases were NOT run here (no Docker).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none yet.

- date: 2026-10-25
- task/issue: #159 (task 27) — trim the alert Compose job and move it off push/PR
- agent role: Engineer (Claude Code, local sandbox, branch `feat/159-alert-compose-job`)
- model: Claude Opus 5.5 (`claude-opus-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): at 79f9f47 the pull_request alert run passed and the push run failed (A-FIRE teardown, `wait_for_no_finding_series` timed out at 300s against the Collector's 5m expiry). The human said the testing is onerous and asked to rethink whether it adds value; the agent recommended trimming, and the human chose "Trim + run off-PR".
- files changed: `tests/test_compose_alert.py` (only A-FIRE and the rule-absent negative remain; A-HELD, A-TIER, A-GAP part 1+2 and A-RESOLVE removed by the human's decision; the fixture no longer waits between cases); `tests/compose_alert.py` (removed the helpers only those cases used); `_docs/testing.md` ("Where each case runs": which unit/SQLite test covers each removed case, and that A-GAP part 2 and A-RESOLVE's Grafana half are manual only; the CI-jobs row); `_docs/verify-locally.md` §7b (the manual alert checks); `_docs/pending-verification.md` #159 (scope change; the VERIFY items CI confirmed are ticked); this log entry. Prepared, not committed until the human approves the diff: `.github/workflows/verify.yml` (alert job removed) and a new `.github/workflows/alert.yml` (nightly at 17:00 UTC + `workflow_dispatch`).
- verification (tests run, reviewer verdict): run 40160976080 (pull_request, 79f9f47) was green with both passes, the first CI proof of the rule-absent negative. The kept cases are unchanged apart from the fixture. `make verify` results are in the session's report. The `compose` cases were NOT run here (no Docker).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the human chose the trim (A-FIRE + negative in Compose, nightly/on demand); the workflow diff awaits approval.

- date: 2026-10-25
- task/issue: #65 (permission sweep 1) — sweep analysis and OpenCode permission-prompt log
- agent role: Orchestrator (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`); a `web-fetch` subagent read the OpenCode plugin and permission docs
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to review the permission records in the session summaries, then said agents must record permission detail themselves so the human does not have to note prompts, and that Claude Code did not need a hook but OpenCode did. No new key prompt saved.
- files changed: new `.opencode/plugins/permission-log.js` (protected path, commit 4fa0674, human-approved in the session; it appends OpenCode `permission.asked` / `permission.replied` events to `.scratch/permission-prompts.jsonl`); `_docs/permission-sweeps.md`; this log entry
- verification (tests run, reviewer verdict): the plugin has NOT been run. The OpenCode docs do not document the event payload, whether `node:fs` is available in a plugin, or whether subagent sessions emit the events (VERIFY). `make permission-report SINCE=1b37fd1` was run read-only: 68 summaries, 29 without a Permission review section (mostly Kiro Web and cloud sessions that did not use the template), no settings change supported by the counts. No reviewer verdict.
- human review (what I checked or corrected, or `none`): the human approved the plugin commit; the first OpenCode session after it is the check.

- date: 2026-10-25
- task/issue: #65 (permission sweep 1) — `make permission-report` reads the OpenCode prompt log
- agent role: Orchestrator (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human saw `.scratch/permission-prompts.jsonl` appear after resuming an OpenCode session, and approved a described diff to `permission-report.py`. No new key prompt saved.
- files changed: `_docs/agent-kit/scripts/permission-report.py` (protected path, commit 5fd93d4: `prompt_stats`, `prompt_label`, `render_prompts`; `main` reads `.scratch/permission-prompts.jsonl` when present and no longer returns early when no summaries changed); `.scratch/agent-kit-issue-permission-log.md` (git-ignored draft of an agent-kit issue, not filed by the agent); this log entry
- verification (tests run, reviewer verdict): ran `make permission-report SINCE=9eb4071` against the live log: it listed `gh issue edit` (1 prompt, no reply logged) and `python3|bash .scratch/*` (1 prompt, once). No automated tests were added: the regression script the old docstring mentioned is not tracked in the repo. Subagent coverage of the log is not yet checked. No reviewer verdict. The approval record is on #65 (comment 6394523862) and lists three differences between the approved description and the committed diff.
- human review (what I checked or corrected, or `none`): the human approved the described change before the commit; the three differences were disclosed afterwards in the approval record.

- date: 2026-10-25
- task/issue: #65 (permission sweep 1) — wait time per OpenCode prompt pattern in `make permission-report`
- agent role: Orchestrator (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human pasted the prompt log, which now had replies, and said "let's make the change" after the agent proposed ranking prompts by wait time. No new key prompt saved.
- files changed: `_docs/agent-kit/scripts/permission-report.py` (protected path, commit 3265553: `seconds_between`, `fmt_wait`, total and longest wait per pattern, rows sorted by total wait); this log entry
- verification (tests run, reviewer verdict): ran `make permission-report SINCE=9eb4071` against the live log: `gh issue edit` waited 8m24s, the `.scratch` script 17s, `make issue-close` 1s, matching the log timestamps. No automated tests. Subagent coverage of the log is still not checked. No reviewer verdict. Approval record on #65 (comment 6394566984). The agent had said it would show the diff before committing and did not; the record says so.
- human review (what I checked or corrected, or `none`): the human approved the change from a verbal description; the diff was not shown before the commit.

- date: 2026-10-25
- task/issue: #180 (PM observability helper-caller sweep); decision point filed #193, #194 and #195, folded #177 into #193, and added the exemplar assertion to #172
- agent role: Orchestrator plus a PM subagent (OpenCode, local sandbox, `main`)
- model: deepseek-v4.1-flash-free (both; subagents inherit the main model)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to work #180 after reviewing the remaining-task shortlist, then approved A/B/C, folding #177 into A, adding D to #172, and not filing the Showcase/responder gaps. No new key prompt saved.
- files changed: new `_session-summaries/planning-2026-10-25-observability-helper-sweep.md`; `_docs/human-tasklist.md` (removed #177 as a separate verification row; recorded the fold); `_docs/pending-verification.md` (#177's log-leg proof now points at #193); `_docs/roadmap.md` (check-in line); this log entry. GitHub writes: #193, #194 and #195 created; #172 body gained the T-A4 exemplar criterion; #177 commented on and closed as folded.
- verification (tests run, reviewer verdict): `make verify` PASS (87 frontend tests, 459 backend tests, typecheck, whitespace, weakened-test checks). QA PASS on #180 (criteria 1-3) at `a4926ce`, with two note fixes applied afterwards (the stale "none is filed" line and the dashboard-label citation). The Docker/Compose cases were not run here (no Docker).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): approved all four decisions at the #180 decision point; corrected two process points: never propose allowing `python3 .scratch/*` (the right answer is a make target), and the two modified docs were the human's #65 work, committed as `0e9af39` (the interim "not mine" report was wrong).

- date: 2026-10-25
- task/issue: #193 (delivery worker: outcome span/log/counter on every held branch; folds #177)
- agent role: Software Engineer subagent (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #193 per the issue, the PM grooming comment (6395175402) and the human decisions (comment 6395603152). No new key prompt saved.
- files changed: `backend/vulntriage/mail/delivery.py` (span, log and one counter increment on the ownerless, owner-email-missing and no_target holds; counter added to mail_config and header_injection; `vt.finding.id` omitted for no_target); `tests/test_notifications.py` (new cases for all eight outcomes, second poll, empty traceparent, leak check); `_docs/pending-verification.md` and `_docs/human-tasklist.md` (#177/#193 Loki leg recorded); this log entry
- verification (tests run, reviewer verdict): `make backend-test` passed (471 passed). `make verify` result is in the #193 Engineer comment. The Loki leg was not run (no Docker) and no held-job case was added to `T-JOURNEY-BE`; the reason is in `_docs/pending-verification.md`. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: #194 (emit scan.finished on failed scans)
- agent role: Software Engineer subagent (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #194 per the issue, the PM grooming comment (6395764352) and the human decisions (comment 6396310715). No new key prompt saved.
- files changed: `backend/vulntriage/ingest/scan.py` (`_fail` logs `scan.finished` after its commit; the feed-failure path re-sets `Scan.trace_id` after its rollback); `tests/test_scan_finished_log.py` (new); this log entry
- verification (tests run, reviewer verdict): new tests written first and seen failing; `make verify` PASS (480 backend tests, 87 frontend tests). No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: #195 (US-13 dashboard: align panel queries with exported metric labels)
- agent role: Software Engineer subagent (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #195 per the rewritten issue, the PM grooming comment (6396447910) and the human decisions of 2026-10-25 (live check split to #199; variables marked unverified; doc notes added). No new key prompt saved.
- files changed: `tests/test_us13_dashboard.py` (new); `observability/grafana/dashboards/us13-journey.json` (panel 1 groups by and labels with `vt_notification_kind`, `vt_outcome`); `_docs/testing.md` and `_docs/architecture.md` (one "exported as" note each); this log entry
- verification (tests run, reviewer verdict): test written first and seen failing against the old dashboard (2 failures), then passing after the fix; `make verify` PASS (487 backend tests, 87 frontend tests). The Prometheus label spelling was not checked against a live stack (#199). No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: #198 (finish a scan that dies from an unexpected exception: `scan failed` / `internal error`)
- agent role: Software Engineer subagent (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #198 under option C, with the human's decision (comment 6396530035), the PM list (6396549653) and the approved spec commit 543c87d (record 6396589596). No new key prompt saved.
- files changed: `backend/vulntriage/ingest/scan.py` (catch-all in `run_scan` reusing `_fail`; `_fail` marks kept findings stale, success clears the mark); `backend/vulntriage/db/enums.py`; `backend/migrations/versions/0002_internal_error_failure_reason.py` (new); `backend/vulntriage/observability/tracing.py` (`span` no longer records exception messages); `tests/test_scan_internal_error.py` (new); `tests/test_db_schema.py`; `tests/test_ingest.py`; `_docs/architecture.md`, `_docs/api.md`, `_docs/openapi.yaml`; `frontend/src/services/types.ts`; `frontend/src/test/vulntriage.test.tsx`; this log entry
- verification (tests run, reviewer verdict): tests written first; `make verify` PASS WITH WARNINGS (496 backend tests, 88 frontend tests; the warning is one rewritten assertion in `test_worker_survives_an_unexpected_error`, which asserted the superseded "left unfinished" behaviour); `make openapi-validate` OK. The migration ran on SQLite only, not on Postgres. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CI fix on PR #200 (`verify / postgres-integration` failed on three SQLite-only tests from #198 and #194)
- agent role: Software Engineer subagent (Claude Code, local sandbox, `main`)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to move the two Migration 0002 tests to a `unit`-only module and keep the PRAGMA test off Postgres. No new key prompt saved.
- files changed: `tests/test_migration_0002.py` (new, `unit`; the two migration tests moved unchanged); `tests/test_scan_orphaned_scan.py` (new, `unit`; the PRAGMA test moved unchanged); `tests/test_scan_internal_error.py` and `tests/test_scan_finished_log.py` (the moved tests and their unused imports removed); this log entry
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (496 backend tests, 88 frontend tests; the warning is the earlier #198 rewritten assertion). Not run on Postgres (no Docker here). A `pytest.skip` on the non-SQLite dialect was tried first and the verify gate failed it ("skip markers added"), so the PRAGMA test was moved to a `unit` module instead. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: rubric re-audit at `fb24904` (previous audit 2026-10-20 at `74e9cfc`, 10 of 24)
- agent role: Rubric Evidence Auditor subagent (Claude Code cloud session, no Docker, no AWS credentials)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to re-audit against `_docs/rubric.md` on evidence in the repo and CI only, and not to credit runs that have not happened. No new key prompt saved.
- files changed: `_docs/rubric-evidence.md` (rewritten: 17 of 24); this log entry
- verification (tests run, reviewer verdict): ran no tests. Read the workflows, compose files, Makefile targets, `ci/test-compose.sh` and `tests/test_compose_telemetry.py`; read GitHub Actions run and job records and job logs for runs 40188742150 (verify), 40188742170 (deploy) and 40160976080 (alert) through the GitHub API; checked with `git log` that the alert rule is unchanged since `79f9f47`. Test counts in this log were not re-counted. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: split the human tasklist into a human-only list and a Claude Code cloud tasklist, with cross-references both ways
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the user's request to move tasks the local sandbox could not do from the human list to a cloud-session list, keep only truly human tasks in the human list, and mark dependencies on both lists. No new key prompt saved.
- files changed: `_docs/cloud-tasklist.md` (new, CC1-CC28); `_docs/human-tasklist.md` (rewritten: A4/A5 and section B verification runs moved out; new approval rows B1-B6 and decision rows F1-F3); `_docs/pending-verification.md` (header points at both lists); this log entry
- verification (tests run, reviewer verdict): ran `make install` and `make verify` before the edits (PASS WITH WARNINGS: 88 frontend and 496 backend tests, type check pass; warning was BASE equal to HEAD). Docs-only edits afterwards; `make verify` not re-run. Confirmed the README overclaim and the missing `docs/images/` the re-audit reported by reading `README.md` and globbing. Did not check the re-audit's CI run records myself. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CC9 Terraform static check and CC10 pre-apply review (#141); started `dockerd` for the cloud session (human rows B1, B2)
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the user's approval of B1 and B2 ("approved"). B1 was offered as either the protected #48 change or a manual `sudo dockerd`; I took the manual route because no exact diff for the protected files had been shown. No new key prompt saved.
- files changed: `_docs/reviews/2026-10-25-terraform-pre-apply-review.md` (new); `_docs/cloud-tasklist.md`, `_docs/human-tasklist.md` (status and cross-references); this log entry. `.scratch/` helper scripts and a copy of `terraform/` (git-ignored). Comment 6397164959 posted on #141.
- verification (tests run, reviewer verdict): ran `terraform fmt -check -recursive` on a copy of `terraform/` with `hashicorp/terraform:1.17.0`: pass. `terraform init -backend=false` and `validate` first failed because the session proxy refused `registry.terraform.io`; after the human added the allowed domains they ran: `bootstrap` and `deploy-roles` valid, `server` failed on an apostrophe in a security group description, which I fixed in `terraform/server/network.tf` (a one-word change) and re-validated: all three valid, `fmt -check` clean. Nothing was planned or applied. The review findings are from reading the code against `terraform-verify.md` §2 and `deploy.yml`; AWS and GitHub behaviour is from my knowledge, not tested, and is marked `VERIFY:` where uncertain. No reviewer verdict.
- new dependencies: none. Pulled the `hashicorp/terraform:1.17.0` image into the session's Docker.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CC29, the Terraform fixes from the pre-apply review (#141): dev trust policy to `environment:dev`, secret ARNs without a lookup, `SendCommand` split in two statements, `user-data.sh` waits for the data volume
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's go-ahead after setting the `dev` environment's deployment branch to `main` and accepting the shared deploy policy (F0). No new key prompt saved.
- files changed: `terraform/deploy-roles/main.tf` and `variables.tf`; `terraform/server/iam.tf` and `user-data.sh`; `_docs/terraform-verify.md`, `_docs/aws-setup.md`, `_docs/cloud-tasklist.md`, `_docs/human-tasklist.md`; this log entry
- verification (tests run, reviewer verdict): `terraform fmt -check -recursive` clean, `terraform validate` passes on `deploy-roles` and `server` (`hashicorp/terraform:1.17.0`, aws provider 5.100.0), `bash -n` on `user-data.sh`. Nothing planned or applied. The IAM behaviour (F1, F3) and the `-??????` secret ARN pattern are `VERIFY:` items proven only by a real apply and deploy. `user-data.sh` was not run on an instance. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CC24 (README overclaims), CC25 (CI evidence), CC19 partly (Postgres integration run), CC27 (app evidence screenshots); CC14 attempted and blocked
- agent role: orchestrator (Claude Code cloud session), while the human was away
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction to do the remaining tasks consecutively, in the order I judged best. No new key prompt saved.
- files changed: `README.md` (responder marked planned and not built, CI/CD level claim softened, screenshots section); `docs/images/dashboard.png` and `docs/images/assets.png` (new); `_docs/cloud-tasklist.md`, `_docs/human-tasklist.md`, `_docs/pending-verification.md`; `_session-summaries/planning-2026-10-25-cloud-tasklist.md`; this log entry. Comments on #172 and #157.
- verification (tests run, reviewer verdict): `make test-integration`: 232 passed against Postgres 16.4 in the cloud session. `make test-compose JOB=telemetry` FAILED at the backend image build (`ghcr.io` blob host refused by the network policy); not re-run. The CI telemetry result (run 40188742150, 3 passed) was read from the Actions job log, not produced here. The CC27 run signed in through the real login form on `make dev-start` with recorded fixtures (`POST /api/auth/login` 200); the screenshots show fixture data, and the README says so. `make verify` was not re-run after these edits (README, images and docs only); the pre-push hook runs it. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CC30, remove the leftover mock "Demo credentials" box from the real sign-in page (frontend; found during CC27)
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's instruction "do CC30 and remove the demo credentials box". No new key prompt saved.
- files changed: `frontend/src/routes/login.tsx`, `frontend/src/services/index.ts`, `frontend/src/test/vulntriage.test.tsx`, `frontend/README.md`; `_docs/cloud-tasklist.md`; this log entry
- verification (tests run, reviewer verdict): ran the new regression test red against the old page (stashed the two source files; 1 failed, 88 passed), then green after restoring the fix. `make verify`: PASS WITH WARNINGS, 89 frontend and 496 backend tests, type check pass; the only warning is that `BASE` equalled `HEAD` while the changes were uncommitted. Not checked in a browser after the change. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CC31 reviewer access docs (README "Try it as a reviewer", demo seed, seeder `--wait`, A14 runbook), the A13 `/api` base-URL fix, and the `make demo` proposal
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "yes" to writing the demo recipe and README section, and their decision that a public password is acceptable because reviewers are anonymous. No new key prompt saved.
- files changed: `README.md`, `deploy/seed-pilot.py`, `deploy/demo-seed.json` (new), `_docs/aws-setup.md`, `_docs/human-tasklist.md`, `_docs/cloud-tasklist.md`, `_docs/make-demo-proposal.md` (new); this log entry. Protected files (`Makefile`, `AGENTS.md`) are not changed.
- verification (tests run, reviewer verdict): ran the README local recipe from an empty SQLite database in this session: user created, 4 repositories registered, scans finished, 4 assets and 2 findings (P1 urllib3 CVE-2023-43804, P2 pyyaml CVE-2020-14343). Tested the new `--wait` option against a stopped backend (clean error after 3 s) and a just-started one (signed in). NOT run: the AWS server command in `aws-setup.md` (no server exists; marked `VERIFY:`), the `make demo` target (proposal only), and the README's `printf | uv run` line exactly as written (the test used an equivalent stdin file). The `/api` base-URL finding comes from reading `Caddyfile` and `frontend/nginx.conf`, not from a deployed run. `make verify` runs in the pre-push hook. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: CC32, apply `make demo` and `make demo-reset` (protected `Makefile` and `AGENTS.md`)
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's "approve make demo", approving the diff in `_docs/make-demo-proposal.md`. No new key prompt saved.
- files changed: `Makefile` (commit `7beafd9`, `HUMAN_APPROVED=1`); `AGENTS.md` (commit `936ca53`, `HUMAN_APPROVED=1`); `README.md`, `_docs/make-demo-proposal.md`, `_docs/human-tasklist.md`, `_docs/cloud-tasklist.md`; this log entry
- verification (tests run, reviewer verdict): ran `make demo-reset` then `make demo` from an empty dev database, then a read-only API check: 4 assets (clean, incomplete, findings, clean) and 2 findings (P1 urllib3 CVE-2023-43804, P2 pyyaml CVE-2020-14343). Ran `make dev-stop`. The pre-push `make verify` follows. Not tested: a second `make demo` on a non-empty database (documented as registering the repositories twice), and `make demo` on a machine other than this cloud session (Python 3.13, uv 0.11). No reviewer verdict, no QA run. No GitHub issue exists for this change, so there is no approval record on an issue; the record is in `_docs/make-demo-proposal.md`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the human approved the exact diff before it was applied; the applied Makefile text is the proposed text, unchanged.

- date: 2026-10-25
- task/issue: first AWS deployment (human tasklist A6-A14, #141/#143/#144): guided the human through the Terraform apply, dev deploy, reviewer access and the production promotion with a rehearsed rollback; fixed the deploy code found wrong along the way
- agent role: orchestrator (Claude Code cloud session)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human's step-by-step requests during the session ("walk me through...", "open the PR"). No new key prompt saved.
- files changed: `terraform/deploy-roles/`, `terraform/server/` (trust `sub`, secret policy, security group, data-volume wait, ACME email handling), `deploy/seed-pilot.py`, `deploy/demo-seed.json`, `README.md`, `_docs/human-tasklist.md`, `_docs/aws-setup.md`, `_session-summaries/planning-2026-10-25-aws-deployment.md`, `_docs/roadmap.md`; this log entry (PRs 204, 205, 206 merged; the rest on the session branch)
- verification (tests run, reviewer verdict): `make verify` passed before each push (last: 89 frontend, 496 backend tests, type check). The human ran `terraform apply` and the GitHub Actions deploys; deploy runs #31 (production), #32 (gated rollback to `20261025-152518-37baad0`) and #33 (forward run) succeeded, read from the Actions job logs and pages the human pasted. The human reported that the dev and production URLs load. Not verified by an agent: the live URLs themselves (no outbound access to them), run #33's digests, the `production` environment settings, `GITHUB_READ_TOKEN`. No reviewer verdict, no QA run, no rubric re-audit after the deployment.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the human ran every AWS and GitHub settings step themselves and checked the OSV records for the demo findings by hand. Corrected during the session: a wrong claim of "no findings on KEV" for one demo repo (I had read the first rows only); the trust-policy `sub` claim (found from CloudTrail); the ACME placeholder email.

- date: 2026-10-25
- task/issue: rubric re-audit after the first AWS deployment (`_docs/rubric-evidence.md`)
- agent role: Rubric Evidence Auditor (Claude Code cloud session, subagent)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the launching agent's request to re-audit at `234cccf` against `_docs/rubric.md`, counting only repo and Actions records and marking the human's say-so as human-reported. No new key prompt saved.
- files changed: `_docs/rubric-evidence.md`; this log entry. Nothing committed.
- verification (tests run, reviewer verdict): read the GitHub Actions run and job records and job logs for deploy runs #30, #31, #32, #33, #34 and the verify run 40214720806 through the GitHub API; read `deploy.yml`, `deploy-env.sh`, README, tasklist rows A6 to A14 and the session summary. Result 21 of 24 (was 17). NOT verified: the live dev and production URLs (the session proxy refused `*.sslip.io`), the `production` environment's reviewer rule, branch protection, any approver identity. Ran no tests and no Docker. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: #218 (task 28a): `VT_DEMO_DEFECT=notify_no_fix` and its production refusal
- agent role: Software Engineer (Claude Code cloud session, subagent)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the launching agent's request to implement #218, leaving `responder/` alone and keeping the `_docs/testing.md` edit small. No new key prompt saved.
- files changed: `backend/vulntriage/ingest/settings.py`, `backend/vulntriage/mail/message.py`, `backend/vulntriage/mail/delivery.py`, `backend/vulntriage/main.py`, `tests/test_demo_defect.py`, `tests/test_compose_responder.py`, `tests/test_notifications.py`, `tests/test_marker_hygiene.py`, `_docs/testing.md`; this log entry.
- verification (tests run, reviewer verdict): `make verify` ran: frontend 89 passed, backend 515 passed (7 deselected), type check and whitespace passed; the only warning was that BASE equals HEAD. NOT run: the container form of `P-PROD-REFUSAL` (`tests/test_compose_responder.py`; no Docker or ghcr.io here), so its `docker compose run` flags are unverified. No reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-25
- task/issue: #219 (task 28b of #160): responder service in stub mode (webhook, bearer secret, repeat guard, action log, false-positive path)
- agent role: Software Engineer (Claude Code cloud session, subagent in a worktree)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the launching agent's request to implement #219 in a new top-level `responder/` project without touching `backend/` or protected files. No new key prompt saved.
- files changed: new `responder/` project (`pyproject.toml`, `uv.lock`, `vt_responder/` with config, guard, action log, API client, fakes, stub runner and app, `tests/` with 51 cases); `_docs/testing.md` (new `I-RESP-HOOK-*` rows); this log entry.
- verification (tests run, reviewer verdict): `uv run --project responder pytest responder/tests` via `.scratch/responder_test.sh`: 51 passed. `make verify` PASS WITH WARNINGS (89 frontend, 496 backend tests, type check; the only warning is that BASE equals HEAD); it does not run the `responder/` tests, because the Makefile targets are protected and not yet added. Not run: any Docker or Compose run, a real Grafana webhook, the real runner (task 28d). No reviewer verdict, no QA run.
- new dependencies: none new to the project. `responder/uv.lock` pins `fastapi`, `uvicorn`, `httpx` and `pytest` (and `starlette` as a constraint) at the versions in `backend/uv.lock`; other transitive versions were resolved fresh and may differ.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-26
- task/issue: #160 (task 28), split into #218-#222; orchestration of #218 and #219
- agent role: Orchestrator (Claude Code cloud session); launched PM, Engineer and QA subagents
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the hand-off prompt to run the PM role on #160 once PR 217 was merged, then "Approve all recommendations, create the sub-issues", "Go ahead with #218 and #219 in parallel", and "Go ahead with the diff as shown". No new key prompt saved.
- files changed: `Makefile` and `AGENTS.md` (protected commit `5ab7b7b`: `responder-install`/`responder-test` targets and the matching Layout and Commands lines); `_docs/roadmap.md` (check-in row); `_session-summaries/issue-218-219-responder-stub.md`; this entry. The Engineers' files are in their own entries above.
- verification (tests run, reviewer verdict): PM grooming report on #160; five issues created (#218-#222) with the split recorded in a comment on #160 (6404873337). QA PASS on #218 (6406748025) and #219 (6406748685), each by a fresh QA subagent at `7df3a6f`; `make assert-clean` PASS and HEAD unchanged after QA. `make verify` after the merge and again after `5ab7b7b`: frontend 89, backend 515, responder 51 passed, type check and whitespace passed. Not run: the container form of `P-PROD-REFUSAL`; any Docker or Compose job; the Grafana test-alert payload; a CI run of the `verify` workflow with the new targets.
- new dependencies: none by the orchestrator (the `responder/uv.lock` packages are in the #219 entry).
- human review (what I checked or corrected, or `none`): the owner approved the split and all seven PM recommendations, the parallel start, and the exact `Makefile`/`AGENTS.md` diff before commit. I restored a comma my edit dropped in the `AGENTS.md` Test (all) line before committing.

- date: 2026-10-26
- task/issue: QA of #157 and #172; unverified items collected in #223
- agent role: Orchestrator (Claude Code cloud session); launched two QA subagents
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner pointed out that neither #157 nor #172 had a QA verdict and asked for QA on both; then asked for the unverified items to go in a new issue, `pending-verification.md` and the human tasklist. No new key prompt saved.
- files changed: `_docs/pending-verification.md` (new section "QA unverified items (2026-10-26)" and a note in the #172 section), `_docs/human-tasklist.md` (B5 status, new rows B9, B10, F4, F5), this entry. Created issue #223.
- verification (tests run, reviewer verdict): QA #157 PASS with unverified items (comment 6410124690); QA #172 FAIL on two criteria (comment 6410133733). Both QA runs: `make verify` passed (89 frontend, 515 backend, 51 responder). Not run by anyone in this session: the telemetry CI record (run 40188742150), the T-REFUSE negative-check runs, any Docker job. #157 and #172 are not closed. No `make verify` was run after this docs-only commit.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none yet; the owner has not yet decided the exemplar assertion, the `P-FLAG-GONE` scope, or whether to close #157.

- date: 2026-10-26
- task/issue: #172 follow-up to QA's FAIL (exemplar assertion; `P-FLAG-GONE` re-scope docs)
- agent role: Engineer (Claude Code subagent)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): orchestrator task relaying the owner's 2026-10-26 decisions (add the exemplar assertion; re-scope the fixtures `P-FLAG-GONE` rule to task 29 / #161). No new key prompt saved.
- files changed: `tests/compose_telemetry.py` (`prometheus_exemplar_trace_ids`, `wait_for_exemplar_trace_id`), `tests/test_compose_telemetry.py` (exemplar assertion in `T-JOURNEY-BE`), `observability/otel-collector.yaml` (`enable_open_metrics: true` on the Prometheus exporter), `observability/compose.yaml` (`--enable-feature=exemplar-storage`), `_docs/testing.md`, `_docs/tasks.md` (tasks 29 and 40), `_docs/pending-verification.md` (section C), this entry.
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (frontend 89, backend 515, responder 51 passed; the warning is that BASE equals HEAD so only uncommitted changes were compared). Not run: the new assertion and the config change (no Docker here); `make test-compose JOB=telemetry` is needed. No reviewer verdict. The exporter option name, exemplar support for counters in Collector 0.111.0 (read from upstream source via web fetch, not run) and the `query_exemplars` shape are marked `VERIFY:`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: #219 follow-up: responder spec gap, an alert with no fingerprint (US-15)
- agent role: Engineer (Claude Code subagent, own worktree)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's request to stop returning 400 for an alert with neither a fingerprint nor a `finding_id`, with the owner's decisions on which cases keep 400. No new key prompt saved.
- files changed: `responder/vt_responder/app.py` (parse rule, `no_change` branch in `handle`, module docstring), `responder/tests/test_webhook.py`, `_docs/testing.md` (`I-RESP-HOOK-MALFORMED` and `I-RESP-HOOK-NOCHANGE` rows), this entry. One existing test input was changed on purpose: the `{"labels":{}}` case in `test_hook_malformed_payload_gets_400_and_no_run` now expects 200 under the new rule, so it was replaced by a `finding_id`-without-fingerprint input that still gets 400.
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (89 frontend, 515 backend, 63 responder passed; the warning is that BASE equals HEAD); weakened-test check 21 assertion lines added, 0 removed. Not run: any Docker job, a real Grafana test notification (the missing fingerprint is unconfirmed). No reviewer verdict, no QA run.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-26
- task/issue: #219 QA follow-up: `_SAFE_ID` accepted a trailing newline (`"ok\n"`)
- agent role: Engineer (Claude Code subagent)
- model: Claude Sonnet 5.5 (`claude-sonnet-5-5`)
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's request to reject a trailing newline in fingerprint and `finding_id`, with red-then-green test evidence. No new key prompt saved.
- files changed: `responder/vt_responder/app.py` (`_SAFE_ID` anchors dropped, both uses now `fullmatch`), `responder/tests/test_webhook.py` (new newline and valid-id cases), `_docs/testing.md` (`I-RESP-HOOK-MALFORMED` row), this entry.
- verification (tests run, reviewer verdict): new tests run on the old code first (2 failed: `"ok\n"` and `finding_id "1\n"` got 200; `"ok\r\n"` and `"\n"` already got 400), then on the fixed code (68 responder passed). `make verify` PASS WITH WARNINGS (89 frontend, 515 backend, 68 responder passed; the warning is that BASE equals HEAD). No reviewer verdict, no QA run.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none

- date: 2026-10-26
- task/issue: review of the PR 224 hand-off note on #157/#172; owner verification items regrouped into #225-#229; doc tidy (#225's last section)
- agent role: Orchestrator (Claude Code cloud session, main session, no subagents)
- model: not recorded in the repository for this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner asked for a review of whether #157 and #172 were still a problem, then to round up the outstanding human verification items into fewer, efficient tickets, then for this doc-tidy PR. No new key prompt saved.
- files changed: `_docs/testing.md` (the `telemetry` job row and the deferred-case bullets now point to #181 and #182; the `alert` job is recorded as landed), `_docs/pending-verification.md` (#157 and #172 items ticked with their CI runs, #181's decisions recorded, the closed #159 section removed, the QA-unverified section replaced by where each item went), `_docs/human-tasklist.md` (working-ticket index for #225-#229; B3, B5, B9 and F5 updated), `_docs/roadmap.md` (check-in), this entry. GitHub, outside the diff: created #225-#229, commented on #220 and #223, closed #223 as replaced by #225, and added notes to the #161 and #172 issue bodies.
- verification (tests run, reviewer verdict): facts read from the GitHub Actions record through the GitHub tools: run 40291587781 (PR 224 head, `telemetry` 3 passed with the exemplar assertion, `verify` green), alert run 40226288166 green, check run list for PR 224; `git grep` on `origin/main` for the exemplar call, the `skipif` pair and `alert.yml`. `make verify` result is in the PR. No QA or reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the owner chose to create the five tickets and close #223 (2026-10-26).

- date: 2026-10-26
- task/issue: #225 close-out sweep run by the agent instead of the owner (#157, #174, #141); QA re-check of #172 (PASS, comment 6411988890) and #172 closed
- agent role: Orchestrator (Claude Code cloud session, main session) and one QA subagent for #172
- model: not recorded in the repository for this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner asked for a guide to the highest-value human verification chunk, then asked why the agent could not do it, then said yes to the #172 QA re-check and the doc tidy. No new key prompt saved.
- files changed: `_docs/pending-verification.md` (#141, #157 and QA-unverified sections removed; queue lines updated), `_docs/human-tasklist.md` (B5 and A9 updated), `_docs/roadmap.md` (check-in), this entry. GitHub, outside the diff: comments with the evidence on #157, #174, #141 and #172, and all four closed as completed.
- verification (tests run, reviewer verdict): facts read from the GitHub Actions record through the GitHub tools: `telemetry` job log of run 40291587781 ("3 passed in 61.07s"), job lists of runs 40188742150, 40073386642 and 40073409867, alert run 40226288166, and the `Record the image digests` values in the `deploy-dev` log of run 40291937292. The `skipif` pair at `tests/test_compose_alert.py:136,179` read directly. `make verify` on this branch: PASS WITH WARNINGS (frontend 89, backend 515, responder 68 passed; the warning is only that BASE equals HEAD; docs-only diff). The QA subagent's PASS on #172 (comment 6411988890) was checked against the issue's comment list before closing; it was inferred from the CI run, not a local run, and it did not re-run `make verify`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the owner asked for the sweep to be done by the agent and approved the QA re-check and the tidy; the owner did not look at the Actions pages themselves.

- date: 2026-10-26
- task/issue: #220 closed after the owner's Docker-host run; a step-by-step walkthrough for the human verification (#226); port-clash notes
- agent role: Orchestrator (Claude Code cloud session)
- model: not recorded in the repository for this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner asked for a guided walkthrough of the highest-value human verification block, then pasted each result; asked whether to document or change the port, and for the note to be more prominent in the quick start. No new key prompt saved.
- files changed: `README.md` (a Docker port-clash note under Option B), `_docs/verify-locally.md` (the responder job description, a port-clash note and a troubleshooting row), `_docs/pending-verification.md` (the §#220 section removed), `_docs/human-tasklist.md`, `_docs/roadmap.md`, this entry. GitHub, outside the diff: a result comment on #220 and #220 closed.
- verification (tests run, reviewer verdict): the responder job result is the OWNER's run, not mine: `make test-compose JOB=responder` gave 8 passed in 103.26 s (2m28s wall clock) on the owner's Docker host (WSL, Docker 29.8.2, Compose v5.6.0); I read the pasted tail of the output only, not the full log. I diagnosed the port clash from the owner's `netstat.exe` and `tasklist.exe` output (process `Code.exe` held 127.0.0.1:9099); why VS Code held it was not confirmed. `make verify` PASS before each push (frontend 89, backend 532, responder 77). QA's [D] criteria for #220 were marked unverified (6413501579) and were not re-checked by QA after the owner's run.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the owner ran the job, found and cleared the port clash by closing VS Code, and pasted the results.

- date: 2026-10-26
- task/issue: the live US-13 stack check (#155, #199) walked through with the owner step by step; the dashboard's Environment and Version filters found to filter nothing and dropped; three Grafana screenshots linked; #155 and #199 closed after QA; PR #235 description updated
- agent role: Orchestrator (Claude Code cloud session) with an Engineer and five QA subagent runs for #199 and one QA run for #155
- model: not recorded in the repository for this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner asked to be walked through the biggest human verification block with the agent doing what it could, pasted each result, chose to drop the filters, and asked to submit the PR. No new key prompt saved.
- files changed: `observability/grafana/dashboards/us13-journey.json`, `observability/README.md`, `tests/test_us13_dashboard.py` (a comment) by the Engineer; `README.md` (Observability evidence, a Docker port-clash note), `_docs/verify-locally.md`, `_docs/pending-verification.md`, `_docs/human-tasklist.md`, `_docs/cloud-tasklist.md`, `_docs/roadmap.md`, `_docs/roadmap-future.md` (X12, X13, X14), the session summary, this entry; three images added and two removed under `docs/images/`. GitHub, outside the diff: result comments on #226, #155 and #199, rewritten bodies for #155 and #199, #155 closed, a PR description update.
- verification (tests run, reviewer verdict): the stack, Grafana and Docker results are the OWNER's, pasted into the session; the agent ran no Docker. The agent read the dashboard JSON (the variables are defined but no panel query references them) and the three committed screenshots. QA: #155 PASS (6417378357); #199 FAIL four times on record wording (6417165141, 6417225167, 6417377952, 6417461140) and PASS on the fifth (6417556909); the dashboard change was checked statically only and has not been loaded live. `make verify` PASS at each push (frontend 89, backend 532, responder 77). The agent's first statement that the filters "work" was wrong and was corrected; the agent also had the line colours reversed in a comment and corrected that.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the owner ran every Docker and Grafana step, took the screenshots, committed them, and chose option 2 for the filters.

- date: 2026-10-26
- task/issue: PR hand-off correction and the post-merge rubric audit; tidy-up of the stale score and responder references
- agent role: Orchestrator (Claude Code cloud session), with the `rubric-auditor` subagent (its own entry is above)
- model: not recorded in the repository for this session
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner said they could not see the PR, then pasted an opencode audit made at `8f7a3ee` (21 of 24) and asked for a post-merge audit and a tidy-up of the references. No new key prompt saved.
- files changed: `README.md` (the criterion 10 row, the responder wording in five places, the demo-uptime sentence), `_docs/roadmap.md` (the S2 note, the C3 estimate, a new check-in row), `_docs/human-tasklist.md`, `_docs/cloud-tasklist.md` (CC1), `_docs/agent-team.md` (the auditor row), this entry. GitHub: PR #235's description corrected, PR #236 opened (merged by the owner), a new PR for the audit and the tidy-up.
- verification (tests run, reviewer verdict): the agent first reported PR #235 as open after the owner had merged it, and corrected that after checking the PR's state; it later checked #236's state itself (merged 14:15:38 UTC as `b1f5d0c`) and ran `git diff 20a1fd8 b1f5d0c`, which is empty, so `main` is exactly the tree the auditor audited. The 22-of-24 score is the `rubric-auditor`'s (`1f5f8ca`), not the orchestrator's; the orchestrator read its Observability row and reports its stated limit (the metric-to-trace link is asserted in CI, not shown in a UI view). The old roadmap check-in rows that say 21 were left as history. `make verify` result is in the PR.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none yet; the owner has not reviewed the audit or the tidy-up.

- date: 2026-10-26
- task/issue: #232 responder guard forgets a fingerprint on `resolved` (task 28c-A, split from #220)
- agent role: Engineer (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #232 per the PM grooming in #220 comment 6412133802. No new key prompt saved.
- files changed: `responder/vt_responder/guard.py` (resolve, finish, in-flight and deferred sets), `responder/vt_responder/app.py`, `responder/tests/test_webhook.py`, `_docs/testing.md` (`I-RESP-HOOK-REPEAT`, `I-RESP-HOOK-RESOLVED`), this entry.
- verification (tests run, reviewer verdict): `make verify`: PASS WITH WARNINGS (frontend 89, backend 515, responder 76 passed; the warning is only that BASE equals HEAD, so uncommitted changes were compared). No reviewer verdict; no QA run yet.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: #234 responder guard hardening, first criterion only (raise path)
- agent role: Engineer (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement only the "Raise path" criterion of #234 and run a mutation check. No new key prompt saved.
- files changed: `responder/tests/test_webhook.py` (one test and a raising fake), this entry. No production code.
- verification (tests run, reviewer verdict): `make verify`: PASS WITH WARNINGS (frontend 89, backend 515, responder 77 passed; the warning is only that BASE equals HEAD). Mutation check: with the `try/finally` removed from `app.py` the new test failed (76 passed, 1 failed) and `app.py` was restored with an empty diff. No reviewer verdict; no QA run. The other #234 criteria are not done.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: #220 responder in Compose and the wiring cases (task 28c)
- agent role: Engineer (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #220 per the PM grooming in comment 6412133802, with no Docker available. No new key prompt saved.
- files changed: `compose.responder.yaml` (new), `ci/test-compose.sh` (`responder` branch; teardown between jobs on the no-JOB path), `tests/test_compose_responder_static.py` (new, unit), `tests/compose_responder.py` (new helpers), `tests/test_compose_responder.py` (`--build`, new compose cases), `_docs/tasks.md` (tasks 28/29 wording), this entry.
- verification (tests run, reviewer verdict): `make verify`: PASS WITH WARNINGS (frontend 89, backend 532, responder 77 passed; the warning is one docstring line in `tests/test_compose_responder.py` that was rewritten, no assertion changed). `bash -n ci/test-compose.sh` passes; a unit test runs the script with `JOB=responder` and a fake failing `docker` and gets exit 1, not 3. The `compose`-marked cases collect (8) but were NOT run: no Docker in this session, so every Docker case (P-PROD-REFUSAL, Grafana body shape, test notification, 401, env check, real-mode refusal) is unverified until `make test-compose JOB=responder` runs on a Docker host or in CI. No reviewer verdict; no QA run.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: #199 last criterion: drop the US-13 dashboard's Environment and Version filters (owner decision, option 2)
- agent role: Engineer (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to remove the two template variables and the docs that mention the filter. No new key prompt saved.
- files changed: `observability/grafana/dashboards/us13-journey.json` (templating list now empty; panels and queries unchanged), `observability/README.md`, `_docs/pending-verification.md`, `tests/test_us13_dashboard.py` (comment only), this entry. `us14-overdue.yaml` and `_docs/specs.md` not changed (the spec has no "filter" text).
- verification (tests run, reviewer verdict): `make verify`: PASS WITH WARNINGS (frontend 89, backend 532, responder 77 passed; the warning is one rewritten comment line in the dashboard test, no assertion changed). The dashboard was NOT loaded in Grafana (no Docker); checked statically only. No reviewer verdict; no QA run.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: rubric re-audit at `20a1fd8` (branch `claude/funny-dijkstra-svm6xw`, the content of PR #236)
- agent role: Rubric Evidence Auditor (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to re-audit all criteria at the current tree, look at the three G9 screenshots, and verify the pre-merge 21/24 audit. No new key prompt saved.
- files changed: `_docs/rubric-evidence.md` (rewritten: 22 of 24 at `20a1fd8`), this entry. No other file.
- verification (tests run, reviewer verdict): read-only. Opened the three `docs/images/g9-*.png` and the g1, g2, g5-ruleset and g7 screenshots; read `make issue-dump N=226` comments and #220 comments; read `responder/vt_responder/runner.py` and `ci/test-compose.sh`; read the `verify` jobs of runs 40337986272 (`b1f5d0c`), 40334369080 (`20a1fd8`) and 40291587781 (telemetry job log tail: 3 passed) through the GitHub tools; confirmed with `git grep` that the exemplar assertion is in `43d812d`. The GitHub API showed PR #236 merged as `b1f5d0c` during the audit, so the document says so. `make verify` and the test counts were not run or re-counted by me; nothing was run on Docker or against the live URLs. No QA run, no reviewer verdict.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: #221 remaining criteria (task 28d, real Agent SDK runner) on `claude/f4-real-runner-fix`
- agent role: Engineer (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to build the remaining #221 criteria with a fake SDK and fake GitHub client, no key, no network. No new key prompt saved.
- files changed: `responder/pyproject.toml`, `responder/uv.lock` (new dependency), `responder/vt_responder/{policy,checkout,github_client,sdk_session}.py` (new), `config.py`, `app.py`, `real_runner.py`, `prompt.py`, `actlog.py` (field `tool`), `fakes.py`; tests `test_policy.py`, `test_real_runner_isolation.py`, `test_sdk_session.py`, `test_sdk_isolation.py` (new), `test_mode.py`, `test_real_runner.py` (session factory now takes `(model, ctx)`; real-mode settings now need the key, token and repo); this entry; the roadmap row; the session summary.
- verification (tests run, reviewer verdict): `make verify`: PASS WITH WARNINGS (frontend 89, backend 532, responder 210 passed; the warning is that the branch base equals HEAD, so only uncommitted changes were diffed). The live SDK session was NEVER run: no key, no network to Anthropic or GitHub. SdkSession is tested with a fake SDK, and one test builds the real `ClaudeAgentOptions` (no connection). SDK behaviour (that a PreToolUse deny overrides the permission mode, the `RESULT:` line convention, git over HTTPS with an extraheader) is read from the installed package and marked `VERIFY:`. No reviewer verdict; no QA run.
- new dependencies: `claude-agent-sdk==0.2.174` in `responder/` only (F2); transitive: mcp, jsonschema, cryptography, pyjwt, sse-starlette and others in `responder/uv.lock`. `backend/uv.lock` unchanged (a test asserts it).
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26
- task/issue: PR 238 CI fixes and #221 close-out on `claude/f4-real-runner-fix` (PR 239); #222 runbook script fix; #241 filed
- agent role: Orchestrator (Claude Code cloud session)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner's instructions in the session: test and fix kiro's PR 238, move it to a `claude/*` branch, start the remaining #221 work, fix the #222 script, harden the policy, file the background-run follow-up, close #221 and update the roadmap. No new key prompt saved.
- files changed: `responder/tests/test_real_runner.py` (import), `.env.example` (`RESPONDER_MODEL` empty), `_docs/human-tasklist.md` (merge conflict), `_docs/responder-token-proof.md` (script), `responder/vt_responder/{policy,real_runner,app}.py` and `responder/tests/{test_policy,test_real_runner_isolation}.py` (hardening), the session summary, the roadmap row; this entry.
- verification (tests run, reviewer verdict): `make verify` PASS at each push (final: frontend 89, backend 532, responder 231). The merge fixed the two failing PR 238 checks locally; CI on PR 239 not yet read. QA PASS on #221 at `898083a` (comment 6426404789); the hardening commit `de7ba9c` and the script fix `898083a` were not separately QA-checked. The #222 script was syntax-checked with `sh -n`, never run (it needs the owner's token). The merge conflict was resolved with a shell script, not the editing tool.
- new dependencies: none (the Engineer's `claude-agent-sdk` pin is in its entry above).
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26 - claude/233-p-demo-be
- task/issue: #233 (P-DEMO-BE, task 28c-C: the full stub loop in Compose, run twice), branch `claude/233-p-demo-be`
- agent role: Software Engineer (Claude Code cloud session subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's instruction to implement #233 on the existing containerized harness without running Docker, resolve the three `VERIFY:` items by reading, and return a question if no fixture gave a no-fixed-version top-tier finding; then the owner's decision (a), a project-authored fixture. No new key prompt saved.
- files changed: `tests/fixtures/osv/vulns/GHSA-fixture-nofix-0001.json` (new), `tests/fixtures/osv/querybatch.json`, `tests/fixtures/kev/known_exploited_vulnerabilities.json`, `tests/fixtures/MANIFEST.md`, `tests/test_fixture_nofix_finding.py` (new), `tests/test_compose_demo_be.py` (new, compose-marked), `tests/test_compose_demo_be_static.py` (new), `tests/compose_alert.py` (`set_job_state`), `tests/compose_responder.py` (`recreate_backend`, `backend_demo_defect`, `message_subject`), `tests/test_marker_hygiene.py` (one allowlist entry for the new compose module), `ci/test-compose.sh` (`seed_user` and the second test file in the responder job), `_docs/roadmap.md`, `_session-summaries/issue-233-p-demo-be.md`, this entry. Commits `48c79a8`, `901a37f` and the docs commit.
- verification (tests run, reviewer verdict): `make verify`: PASS WITH WARNINGS (frontend 89, backend 542, responder 85 passed; the warning is the fixture files changed, reason: one advisory, one querybatch entry and one KEV row were added, nothing loosened, 0 assertion lines removed). `make backend-test` before and after adding the fixture: the 532 existing cases unchanged, plus the 2 new fixture cases. A read-only collection of the compose-marked cases found the new case. NOT RUN: the compose-marked case `test_p_demo_be_full_stub_loop_runs_twice_on_one_finding` (no Docker daemon in this session); so no [D] criterion has been observed passing, and the Grafana `resolved` notification is unverified. No reviewer verdict; no QA run.
- new dependencies: none.

- date: 2026-10-26  
- task/issue: #241 real agent in the background, with a retry cap (follow-up to #221), on `claude/241-background-run` (from `claude/f4-real-runner-followup`)
- agent role: Engineer (Claude Code subagent)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task to implement #241 reusing `FingerprintGuard`, deciding what a second concurrent alert gets, with a fake session and no new dependency. No new key prompt saved.
- files changed: `responder/vt_responder/{app,guard,config}.py`, `responder/tests/test_background.py` (new), `.env.example` (three names, no values), this entry, `_docs/roadmap.md`, `_session-summaries/issue-241-background-run.md`.
- verification (tests run, reviewer verdict): `make verify BASE=origin/claude/f4-real-runner-followup` PASS (frontend 89, backend 532, responder 257; 89 assertion lines added, 0 removed). No QA review yet. No live SDK call, no key, no network to Anthropic or GitHub.
- new dependencies: none (standard-library `ThreadPoolExecutor`).
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26 - ci/161-flag-gone-script-and-tests
- task/issue: #161 (P-FLAG-GONE check script + its tests, task 29), branch `ci/161-flag-gone-script-and-tests` (re-land of the non-protected files from the conflicting draft PR #248)
- agent role: Engineer (Kiro)
- model: Auto
- prompt or instruction given (or link to a file in `_docs/prompts/`): owner handoff pass — re-land the non-protected deliverables from stuck draft PR #248 (`claude/161-draft`) onto a clean branch off current `main`, resolving the `_docs/ai-usage-log.md` conflict, and QA-check the script + tests. The protected `.github/` commits (A and B) stay owner-run. No new key prompt saved.
- files changed: `ci/check_flag_gone.py` (new), `tests/test_flag_gone.py` (new), `_docs/161-responder-job-proposal.md` (new), `_session-summaries/issue-161-responder-job-draft.md` (new), this entry. The conflicting `_docs/ai-usage-log.md` change from the draft was NOT carried over; this fresh entry replaces it.
- verification (tests run, reviewer verdict): `python3 -m pytest tests/test_flag_gone.py --noconftest` → 19 passed (the repo `conftest.py` imports `sqlalchemy`, absent in this sandbox, so the suite is run isolated; `make test` runs it normally where deps are installed). `python3 ci/check_flag_gone.py .` → `P-FLAG-GONE: FAIL (103 findings)`, exit 1 — the expected result while the demo defect is present (proposal predicted ~78 on `main`; the tree has grown). No reviewer verdict.
- new dependencies: none (stdlib + pytest).
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: spec notes from #63 (PR #252), approval records for the #161 `.github/` commits, closing #63 and #229, and the task-list update (this PR)
- agent role: Orchestrator (Claude Code cloud session)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the owner's instructions in the session: walk through #229, draft the #63 diffs, "approve all" (the three diffs and the `P-FLAG-GONE` wording), review what changed after the owner's `.github/` commits, and bring the task lists up to date. No new key prompt saved.
- files changed: `_docs/63-spec-notes-proposal.md` (new), `_docs/specs.md` and `_docs/architecture.md` (three owner-approved `HUMAN_APPROVED=1` commits, in PR #252), then `_docs/human-tasklist.md`, `_docs/cloud-tasklist.md`, `_docs/roadmap.md`; this entry.
- verification (tests run, reviewer verdict): `make verify` PASS at each push (docs only). Approval records were generated from git (`git show`, `git rev-parse`) and posted on #63 (comments 6431115787, 6431117320, 6431117575) and on #161 (6431266406, 6431266643). The status of #222, #233, #241 and the `responder` workflow run was read from the issues and the Actions API, not assumed; the first `responder` CI run was still in progress when last read. The `P-FLAG-GONE` gate has not been exercised in a promotion. No reviewer verdict on the docs edits.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: #244 pre-drill hardening of the real runner (findings B1, S1 to S6 from the review of PR #242)
- agent role: Engineer (Claude Code subagent, worktree branch `claude/244-hardening`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task brief for #244 (priority order B1 env scrub, B1 limits note, S1, S4, S3, S2, S5/S6; no container or egress build; owner decision B13 = accept the residual risk, relayed mid-task). No new key prompt saved.
- files changed: `responder/vt_responder/{real_runner,sdk_session,github_client,checkout,config,fakes,app}.py`, new `responder/vt_responder/{envscrub,procs,installer}.py`, `responder/tests/{test_hardening_244,test_hardening_244_runner}.py` (new), `responder/tests/{test_real_runner_isolation,test_background}.py` (adapted to the new branch/PR checks), `.env.example` (name `RESPONDER_MAX_BUDGET_USD`, empty), `_docs/responder-security-limits.md` (new), `_docs/roadmap.md`, `_session-summaries/issue-244-hardening.md` (new), this entry.
- verification (tests run, reviewer verdict): the new B1, S1, S4 and S5 tests were run red against the unchanged code first (27 failed), then green after the fixes; the S2, S3 and S6 tests were written with their fixes and not run red first. `make verify BASE=origin/main` PASS (frontend 89, backend 561, responder 314; 0 assertion lines removed). No live SDK call was made, so the env merge was confirmed by reading `subprocess_cli.py` in the installed package, not by a run. No reviewer verdict (QA not yet run).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: #260 headless `claude -p` runtime on the owner's login, runner pushes and opens the PR (amends F2)
- agent role: Engineer (Claude Code subagent, worktree branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's task brief for #260 (verify the real CLI first from `--help` and the docs, then `cli_session`, the CLI environment, rules generated from `policy.py`, the runner-side diff gate, runner push and PR, docs). The owner confirmed decisions 1 to 4 with "go" on the issue. No new key prompt saved.
- files changed: new `responder/vt_responder/{cli_session,cli_rules,publisher}.py`; `responder/vt_responder/{config,envscrub,policy,prompt,real_runner,app,github_client,fakes}.py`; new `responder/tests/{fake_claude,test_cli_runtime,test_cli_rules,test_publisher}.py`; `responder/tests/test_mode.py` (the SDK cases now name `RESPONDER_RUNTIME=sdk`); `.env.example` (`RESPONDER_RUNTIME`, `RESPONDER_MAX_COMMITS`, empty); new `_docs/responder-cli-runtime.md`; `_docs/{responder-security-limits,drill-runbook,roadmap}.md`; `_session-summaries/issue-260-cli-runtime.md` (new); this entry.
- verification (tests run, reviewer verdict): `make verify BASE=origin/main` (result recorded in the issue comment). The CLI flags were read from `claude --help` and `claude auth status` on the sandbox's `claude` 2.1.311 (no model call, no login created) and from code.claude.com/docs pages; they are not confirmed by a live run, and the `VERIFY:` list is in `_docs/responder-cli-runtime.md`. Every test uses a fake `claude` script; no login, no network and no model call was used. No reviewer verdict (QA not yet run).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: #260 fixes for the four QA failures (comment 6433016307)
- agent role: Engineer (Claude Code subagent, worktree branch `claude/260-qa-fixes` from `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief, built on `_session-summaries/handoff-2026-10-27-260-fixes.md` (red test first per finding, one commit per finding, no push). No new key prompt saved.
- files changed: `responder/vt_responder/{publisher,policy,cli_rules,cli_session}.py`; `responder/tests/{test_publisher_real_git (new),test_publisher,test_cli_rules,test_cli_runtime,fake_claude}.py`; `_docs/{responder-security-limits,responder-cli-runtime,roadmap}.md`; `_session-summaries/issue-260-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): each finding was reproduced red on the old code and green after the fix; `make responder-test` 618 passed. `make verify` did not pass in the worktree only because `frontend/node_modules` is missing (`make install` not authorized); frontend and backend suites were not run. No QA re-check yet; nothing run against a live `claude`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: #260 QA round 2 (comment 6435357864): 1d residual, tool-rule holes, docs overclaims, fence parser
- agent role: Engineer (Claude Code subagent, worktree branch `claude/260-qa-fixes-2` from `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief (red test first per item, one commit per item, no push, no protected files). No new key prompt saved.
- files changed: `responder/vt_responder/{publisher,checkout,cli_rules,policy,prompt,cli_session}.py`; `responder/tests/{test_publisher_real_git,test_cli_rules,test_cli_runtime}.py`; `_docs/{responder-security-limits,responder-cli-runtime,roadmap}.md`; `_session-summaries/issue-260-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): each item reproduced red, then green; `make verify BASE=origin/main` PASS (frontend 89, backend 561, responder 911). Real git on local temp repositories only; nothing run against a live `claude`, login, model or GitHub. No QA re-check yet.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-26 - docs/227-a11-nightly-stop-cost-tag
- task/issue: #227 (AWS console session, task A11), branch `docs/227-a11-nightly-stop-cost-tag`
- agent role: Engineer (Kiro)
- model: Auto
- prompt or instruction given (or link to a file in `_docs/prompts/`): owner working #227 at the AWS console, confirming the nightly-stop decision and the cost-allocation tag. No new key prompt saved.
- files changed: `_docs/human-tasklist.md` (A11 → done; A1 account note corrected from "member account" to "management account"; "Last updated" line), this entry.
- verification (tests run, reviewer verdict): none — documentation-only edit recording the owner's console actions. The AWS state itself is the owner's; no agent has AWS access and none was claimed. `git diff --check` clean.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): the owner confirmed at the console (management account) that the nightly stop is set (04:00 UTC default, off for grading) and the `project` cost-allocation tag is activated and applied; recorded as stated.

- date: 2026-10-27
- task/issue: #260 QA round 3 (comment 6436104728): shell expansion in the CLI git rules, gitlink hidden by an untracked `.gitmodules`, docs corrections, flaky temp-dir test
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief (red test first per item, one commit per item, no push, no protected files). No new key prompt saved.
- files changed: `responder/vt_responder/{cli_rules,publisher}.py`; `responder/tests/{test_cli_rules,test_publisher_real_git,test_cli_runtime}.py`; `_docs/{responder-security-limits,responder-cli-runtime,roadmap}.md`; `_session-summaries/issue-260-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): F1 and F2 reproduced red, then green; `make verify BASE=origin/main` PASS (frontend 89, backend 561, responder 940). Real git on local temp repositories only; nothing run against a live `claude`, login, model or GitHub. No QA re-check yet.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: #260 QA round 4 (comment 6436304070), N1: a tab let a flag past the `git commit` rule
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief (red test first, fix, docs, optional prompt line, no push). No new key prompt saved.
- files changed: `responder/vt_responder/{cli_rules,prompt}.py`; `responder/tests/{test_cli_rules,test_cli_runtime}.py`; `_docs/{responder-security-limits,responder-cli-runtime,roadmap}.md`; `_session-summaries/issue-260-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): the new whitespace cases were red (16 allowed by `evaluate`), then green; `make verify BASE=origin/main` PASS (frontend 89, backend 561, responder 973). Nothing run against a live `claude`. No QA re-check yet.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-27
- task/issue: #260 QA round 5 (comment 6436421743), N2: more `git commit` spellings; fixed as a class
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief (no new deny pattern; one allowed commit shape by positive match; a seeded differential test between the rules and `ToolPolicy`; docs and records). No new key prompt saved.
- files changed: `responder/vt_responder/{cli_rules,prompt}.py`; `responder/tests/{test_cli_rules,test_cli_rules_differential (new),test_cli_runtime}.py`; `_docs/{responder-security-limits,responder-cli-runtime,roadmap}.md`; `_session-summaries/issue-260-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): the six QA forms and the differential test were red, then green (differential disagreements found: 13 of 26 allowed commands, then 13 of 946 after the first fix, then none); `make verify BASE=origin/main` PASS (frontend 89, backend 561, responder 995). Nothing run against a live `claude`. No QA re-check yet.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #163 / #260 owner drill: one source-of-truth step list for the video (`_docs/drill-video-steps.md`)
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief (single copy-paste doc; one `.env`; check step; simple one-action steps; supersede the older commands doc). No new key prompt saved.
- files changed: `_docs/drill-video-steps.md` (new); pointer lines in `_docs/drill-runbook-commands.md`, `_docs/drill-runbook.md`, `README.md`; this entry.
- verification (tests run, reviewer verdict): `docker compose config --quiet` and `--services` ran OK against the `.env` and override file produced by the doc's own A8 and A10 blocks, in a temp copy under `.scratch/`; all 44 bash blocks and both generated scripts pass `bash -n`; the cookie-extraction line tested on a sample header. The Docker daemon is not available in this sandbox, so no container, image pull, user, asset, scan, metric, alert, mail or responder step was run, and the Grafana-image `wget` check is unverified. Nothing run against a live `claude`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #163 / #260 QA fixes F1-F7 and nits N1-N11 on `_docs/drill-video-steps.md`
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's QA-fix brief. No new key prompt saved.
- files changed: `_docs/drill-video-steps.md`; Part 2/3 body replaced by a pointer in `_docs/drill-runbook-commands.md`; Part 1 step 1 body replaced by a pointer in `_docs/drill-runbook.md`; this entry.
- verification (tests run, reviewer verdict): the doc's own env and override blocks regenerated in a temp copy under `.scratch/`; `docker compose config --quiet` and `--services` OK; all bash blocks and both generated scripts pass `bash -n`. No Docker daemon here, so no container, GitHub, Grafana or responder step was run.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #260 follow-up: log why a CLI run failed (first live drill showed `run_failed` `agent_escalated` with no cause)
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief to keep and log the ESCALATE explanation and, if safe, a snippet for the other failure reasons. No new key prompt saved.
- files changed: `responder/vt_responder/cli_session.py`, `responder/vt_responder/real_runner.py`, `responder/tests/test_cli_runtime.py`, `_docs/responder-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): tests were written alongside the code (the red run before the change was not separately captured); `make responder-test` 1006 passed; `make verify BASE=origin/main` PASS. Nothing run against a live `claude`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #260 QA fix for ff691bc: F1 (ESCALATE and `no_change` text cut to 500 before redaction) and F2 (tests did not guard redact-before-cut)
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's relay of the QA verdict. No new key prompt saved.
- files changed: `responder/vt_responder/cli_session.py`, `responder/vt_responder/real_runner.py`, `responder/vt_responder/actlog.py`, `responder/tests/test_cli_runtime.py`, `_docs/responder-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): the new straddle tests were run on the unfixed code first and the escalation, false-positive and 800-bound tests failed; after the fix `make verify BASE=origin/main` PASS (responder 1387 passed). Seven mutants of the fix (`.scratch/mutate2.py`, on a copy) each fail the suite. Nothing run against a live `claude`.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #260 follow-up: log the tool calls the CLI refused (`denied_calls` in `run_failed`) after the live drill's escalation over a denied `git commit`
- agent role: Engineer (Claude Code subagent, branch `claude/260-cli-runtime`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief. No new key prompt saved.
- files changed: `responder/vt_responder/cli_session.py`, `responder/vt_responder/real_runner.py`, `responder/vt_responder/actlog.py`, `responder/tests/test_cli_runtime.py`, `_docs/responder-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): the new tests were run on the unchanged code first and the logging tests failed; then the responder suite passed and `make verify BASE=origin/main` was run (result in the commit's hand-over). Fourteen mutants (`.scratch/mutate3.py`, on a copy) each fail the suite. The `permission_denials` field shape was read from strings in the installed claude 2.1.311 binary (`grep -a`); no model call and no login was used. The command-form table came from `.scratch/commit_forms.py` (`cli_rules.evaluate` and `ToolPolicy.check_command`); the real CLI's behaviour for those forms is unverified.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #260 follow-up: tell the drill agent that code gated by `VT_DEMO_DEFECT` is a planted defect it should fix (owner decision after two live runs escalated)
- agent role: Engineer (Claude Code subagent, branch `claude/260-drill-mandate`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief. No new key prompt saved.
- files changed: `responder/vt_responder/prompt.py`, `responder/tests/test_cli_runtime.py`, `_docs/responder-cli-runtime.md`, `_docs/drill-video-steps.md`; this entry.
- verification (tests run, reviewer verdict): simulated the minimal fix (removed the `raise` branch in `backend/vulntriage/mail/message.py`) and ran `make backend-test`: 2 tests failed (`test_formatter_fails_only_for_no_fix_with_defect_on`, `test_demo_defect_no_fix_finding_fails_sends_nothing_and_logs_no_advisory_text`), 559 passed; the simulation was then reverted. The new prompt test failed first, then `make responder-test` was re-run (result in the hand-over). No model call was made.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #260 follow-up: remove the control-whitespace deny patterns that the real claude CLI read as spaces and denied every plain `git commit -m "..."`
- agent role: Engineer (Claude Code subagent, branch `claude/260-drill-mandate`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief, based on the owner's probe results (V0/V1/V3/V8a/W1-W5). No new key prompt saved.
- files changed: `responder/vt_responder/cli_rules.py`, `responder/tests/test_cli_rules.py`, `responder/tests/test_cli_rules_differential.py`, `_docs/responder-security-limits.md`, `_docs/responder-cli-runtime.md`, `_docs/drill-video-steps.md`; this entry.
- verification (tests run, reviewer verdict): the new tests failed before the change (the model now reads a pattern control character as a space, which flagged the old patterns); then the rules and differential tests passed. `make responder-test` result is in the hand-over. No model call and no real claude run were made here; the real-CLI facts are the owner's probe results as reported to me.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: #260 QA finding: agent text was cut to a window before exact-match redaction (a secret bisected by the window edge survived); plus the live-drill finding that an `agent_escalated` run logged no explanation
- agent role: Engineer (Claude Code subagent, branch `claude/260-redact-first`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief and its follow-up (redact-first for every sink; fall back to the redacted tail of the final message when a verdict has no text). No new key prompt saved.
- files changed: `responder/vt_responder/envscrub.py` (`redacted_window`), `cli_session.py`, `sdk_session.py`, `real_runner.py`, `app.py`, `responder/tests/test_cli_redact_first.py` (new), `responder/tests/test_cli_runtime.py` (rig passes the secrets to the session; two assertions changed on purpose: a verdict with no text now logs the end of the message instead of nothing), `_docs/responder-cli-runtime.md`; this entry.
- verification (tests run, reviewer verdict): `make responder-test` (result in the hand-over). A mutation run on a scratch copy of `responder/` applied 29 single-line mutants (first-occurrence-only redaction, escalation using the tail, limit-error text logged, byte caps, cut-before-redact in each sink, session ignoring the secrets, fallback removed or weakened, SDK and `create_app` wiring); all 29 were killed by the new and existing tests. The redact-first change itself was written before its tests, so the straddle tests were checked against the old behaviour through the cut-before-redact and ignore-the-secrets mutants, not by a run on the old code; only the empty-verdict fallback tests were run red first. A first version that bounded the redaction region and dropped edge characters was found by a test to still bisect a secret, and was replaced by redacting the whole text. No model call and no real claude run were made.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-28
- task/issue: rubric evidence re-audit at `83e0703` (merged PR #269), after the on-call drill
- agent role: Rubric Evidence Auditor (Claude Code subagent, branch `claude/ecstatic-newton-b7whlf`)
- model: claude-sonnet-5-5
- prompt or instruction given (or link to a file in `_docs/prompts/`): the orchestrator's brief (re-run the audit, fix the scores for criteria 9, 10 and 12 only where the evidence supports them, check the README's claims, keep the incomplete QA of #266 honest). No new key prompt saved.
- files changed: `_docs/rubric-evidence.md` (rewritten); this entry.
- verification (tests run, reviewer verdict): no test suite run and no live system touched. Read through the GitHub API: PR #265, PR #266, the `verify`, `deploy`, `responder` and `alert` workflow run lists. Opened with the image reader: `drill-b16` (table), `drill-b18`, `drill-b19` (email), `drill-b21`, `drill-b22`, `drill-b27` (Grafana and terminals), `drill-b30` (exemplar), `g5-github-settings-rulesets-protect-main.png`, `g9-grafana-dashboard-dev-local.png`. Not opened: the other drill screenshots, the YouTube video, issue comments. Result: 24 of 24 evidenced (On-Call Agent 0 to 2; criteria 9 and 10 unchanged at their maximum); the file lists the limits and six README claims that are stale or not fully supported. Independent QA of the final merged runtime code (#266) was not completed and is stated as such.
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none.

- date: 2026-10-29
- task/issue: #271 (permission tooling: safe read-only allows, guarded issue writes, five-group review, optional cloud-session push, top-level kit mirror)
- agent role: Orchestrator (OpenCode session on `main`)
- model: deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human approved the plan and each protected diff ("Approve and commit"), then said "continue"; at the decision point the human chose "Fix now", "Bump to 1.10", "Enable fully", "After the fixes" and "Extend now". No new key prompt was saved.
- files changed: `opencode.json`, `.claude/settings.json`, `Makefile`, `AGENTS.md`, `_docs/agent-kit/**`, `agent-kit/**` (mirror), `_docs/permission-tooling-verification.md` (new), `_docs/permission-sweeps.md`, `_docs/pending-verification.md`, `_docs/ai-usage-log.md`, `_docs/roadmap.md`, `_session-summaries/issue-271-permission-tooling.md` (new). GitHub: issue #271; approval records 6470535173 for `e174151`, 6472423911 plus a second part for `8778092`, 6496389807 for `5a0f256`, 6496400857 for `4a27b30`, 6496418162 for `b50207f`, 6497413564 for `d9986ef`; QA comments 6495904527, 6497370140 and 6498104690.
- verification (tests run, reviewer verdict): `make verify BASE=51bcf57` PASS (89 frontend, 563 backend with 14 deselected, 1638 responder; type check, whitespace and weakened-test checks PASS). `make check-scripts` PASS. `.scratch/check-guard.sh` gave the four expected guard decisions. `make permission-report SINCE=9eb4071` and `SINCE=51bcf57` ran read-only. QA at `5f9cd61`: PASS on the issue scope; it re-ran Verify, the guard cases, the wrappers and the helpers, and listed six risks outside the scope (the `file-at` SSH-key filter, the stale kit version in `AGENTS.md`, the incomplete cloud-push settings merge, the unverified Claude close-ask precedence, the tool-level `.env` block, and the pre-QA log lines). After the fixes, `make verify BASE=5f9cd61` PASS at `b50207f`; re-QA PASS at `b50207f` (6497370140) and at `d9986ef` (6498104690), with the file-at calls refusing `id_rsa`, `keys/id_rsa`, `id_ed25519`, `id_dsa`, `keys/id_ecdsa`, `my_id_rsa_backup`, `my_id_ed25519_backup`, `server.pem` and `server.key`, and allowing `.gitignore` and `README.md`. Residual: the key-name check is case-sensitive, so `ID_RSA`/`id-rsa` are not caught; non-standard names only.
- new dependencies: none (the responder dependencies installed by `make install` were already locked).
- human review (what I checked or corrected, or `none`): corrected QA's statement that the project settings kept a blanket `Bash(git push *)` deny; that deny is in the generic kit copy, while the project settings already used specific `main`, force and delete denies. The protected diffs were approved in chat before each commit.

- date: 2026-10-31
- task/issue: one-off devcontainer feedback bundle for `devcontainer-test` (not a GitHub issue)
- agent role: Orchestrator (OpenCode session on `main`)
- model: deepseek-v4.1-flash-free
- prompt or instruction given (or link to a file in `_docs/prompts/`): the human asked to explore feeding devcontainer improvements back to the upstream `devcontainer-test` project, then chose Node + uv + an optional Compose variant, an issue draft plus a copyable folder, `_docs/devcontainer-feedback/`, and devcontainer-test first with the kit reference later; then said "ok let's build that". No new key prompt was saved.
- files changed: `_docs/devcontainer-feedback/README.md`, `_docs/devcontainer-feedback/issue.md`, `_docs/devcontainer-feedback/files/devcontainer.json`, `_docs/devcontainer-feedback/files/setup.sh`, `_docs/devcontainer-feedback/files/devcontainer-lock.json`, `_docs/devcontainer-feedback/files/verify.yml`, `_docs/devcontainer-feedback/files/optional-compose/README.md`, `_docs/devcontainer-feedback/files/optional-compose/devcontainer.json`, `_docs/devcontainer-feedback/files/optional-compose/compose.yaml`, `_docs/devcontainer-feedback/files/optional-compose/Dockerfile` (all new); this entry.
- verification (tests run, reviewer verdict): `make verify` PASS WITH WARNINGS (89 frontend, 563 backend with 14 deselected, 1638 responder; type check, whitespace and weakened-test checks PASS; the warning is that BASE equals HEAD, because the bundle is uncommitted). `jq empty` on the three JSON files PASS; `bash -n` on the proposed `setup.sh` PASS; `git diff --check` PASS. YAML was not validated locally (no `yq` or PyYAML); the container rebuild, `docker compose config` and the Node/uv checks were not run here (no Docker CLI in this container).
- new dependencies: none.
- human review (what I checked or corrected, or `none`): none yet; the human has not reviewed the bundle or created the upstream issue.
