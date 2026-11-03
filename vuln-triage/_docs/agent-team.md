# Agent team

Who does what on VulnTriage, which tool and model has run each role according to the record, and how work passes between roles and between OpenCode and Claude Code. Written for the Agent Team Specification criterion in [rubric.md](rubric.md) ("The project defines the agent team and process of how they work together", 2 points), issue [#12](https://github.com/andrew-chung-au/vuln-triage/issues/12).

This page summarises and links. Where it disagrees with a source, the source wins: [agent-kit/process.md](agent-kit/process.md) for the process, the role files for each role, [ai-usage-log.md](ai-usage-log.md) for what happened.

## Roles

Six roles plus the human. Every role has a definition file or a saved prompt.

| Role | Responsibility | May write | Defined in |
|---|---|---|---|
| Orchestrator | The main session. Launches the roles, passes work between them and brings every question to the human. It does not plan the backlog, groom, implement or test. | Log entries for PM and QA runs (their role files say the Orchestrator appends them); approved protected-file commits with `HUMAN_APPROVED=1` (lifecycle step 7); the session summary (step 8). Runs **Assert clean** after QA. Only the Orchestrator closes issues (step 9). | [process.md § Orchestrator](agent-kit/process.md#orchestrator) |
| PM | Grooms one issue before anyone implements it, using the task template, and builds or reviews the backlog from the spec. Asks the human only when a choice changes scope, an interface, the spec or a security limit. | Only `.scratch/` (both role files). Posts `PM:` comments; creates, edits or closes issues only after the human approves. The Orchestrator appends its log entry. | [team/pm.md](agent-kit/team/pm.md), [.opencode/agents/pm.md](../.opencode/agents/pm.md), [.claude/agents/pm.md](../.claude/agents/pm.md) |
| Software Engineer | Implements one groomed issue against its acceptance criteria, writes tests, runs **Verify**, and hands over in an `Engineer:` comment. | The files the issue names; commits them. Does not edit protected files (proposes the change instead), does not close the issue, does not push. Its role files say to append its own log entry (see Known contradictions). | [team/software-engineer.md](agent-kit/team/software-engineer.md), [.opencode/agents/software-engineer.md](../.opencode/agents/software-engineer.md), [.claude/agents/software-engineer.md](../.claude/agents/software-engineer.md) |
| QA Engineer | Checks finished work against the issue's acceptance criteria, runs **Verify** itself, tries to get around every limit, and posts `QA: PASS` or `QA: FAIL`. Fixes nothing. | Only `.scratch/` (both role files). Posts the `QA:` comment. The Orchestrator appends its log entry. | [team/qa-engineer.md](agent-kit/team/qa-engineer.md), [.opencode/agents/qa-engineer.md](../.opencode/agents/qa-engineer.md), [.claude/agents/qa-engineer.md](../.claude/agents/qa-engineer.md) |
| Reviewer | Independent reviewer of the planning documents, run in a different tool from the one that wrote the plan. Finds problems; does not fix them. | Only its review file and its log entry ("Do not edit any existing file. Write only your review file and your log entry."). | [prompts/reviewer-plan-review.md](prompts/reviewer-plan-review.md) (saved prompt; no role file) |
| Rubric Evidence Auditor | Checks the project against [rubric.md](rubric.md) and records each criterion's status, evidence and gap. | Only [rubric-evidence.md](rubric-evidence.md) ("You do not change any other file"). Its role files also say to append its own log entry (see Known contradictions). | [.opencode/agents/rubric-auditor.md](../.opencode/agents/rubric-auditor.md), [.claude/agents/rubric-auditor.md](../.claude/agents/rubric-auditor.md), [skill update-rubric-evidence](../.agents/skills/update-rubric-evidence/SKILL.md) |
| The human | Owns the spec and the protected files ([agent-kit.conf](../agent-kit.conf) PROTECTED), answers decision questions and approval requests, reviews the diff and pushes, and runs external app builders. | Any file; protected files are committed with `HUMAN_APPROVED=1`. Only the human pushes ([process.md § Commits and pushes](agent-kit/process.md#commits-and-pushes)). | [AGENTS.md](../AGENTS.md) Conventions, [procedures/asking-the-human.md](agent-kit/procedures/asking-the-human.md) |

External app builders are tools the human runs, not team roles. The prompt approved in [#14](https://github.com/andrew-chung-au/vuln-triage/issues/14) was written for Lovable ([prompts/lovable-frontend.md](prompts/lovable-frontend.md)). The human tried it in Lovable, hit a credit limit, and ran the same prompt in Bolt. The committed prototype in `frontend-bolt/` was built with Bolt (commit `fea6fb7` "added frontend built by bolt"; log, 2026-10-17 "PM re-grooms issue #15 for the Bolt build; issue parked"). Its build record belongs to [#15](https://github.com/andrew-chung-au/vuln-triage/issues/15).

## Tool and model

### How a model is chosen

- No role file sets a model: none of the eight files in `.opencode/agents/` and `.claude/agents/` has a `model` field.
- Claude Code subagents inherit the main session's model (log, 2026-10-17 "QA checks issue #11 at c8dea47 (PASS)": "the qa-engineer agent sets no model, so it inherits the main session's").
- OpenCode uses `model` in [opencode.json](../opencode.json). Its current value is `opencode/deepseek-v4.1-flash-free` (set by the human in `5feca25`, id fixed in `d7f69a9`). This is configuration only: no log entry or summary records any work done with that model.

### Intent and record

The stated intent is in [the 2026-10-16 planning summary](../_session-summaries/planning-2026-10-16-claude-code-layer.md) (line 8): "The human uses OpenCode to do the work and Claude Code to supervise and review it."

From 2026-10-17 the record differs from that intent because OpenCode was unavailable: every run recorded from that date is in Claude Code, including the Engineer work. Where the log or a summary gives a reason, it is that OpenCode was unavailable and the human asked (log, 2026-10-17 "Engineer corrects #11 report for QA risks (commit ed05530)" and "Rubric Evidence Auditor regenerates rubric evidence"; [#14 summary](../_session-summaries/issue-014-lovable-frontend-prompt.md) line 36). This page makes no forward assignment of a tool or model to any role.

### Recorded history

Model ids are copied from [ai-usage-log.md](ai-usage-log.md). Where an entry names a model but no tool, the Tool column says so. Where an entry records the agent role as "not recorded", the Role column says "not recorded" and no role is inferred: the role-recording policy was not applied at the time (the human, [comment 6243801494](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6243801494)).

| Role | Tool | Model | Issues and source |
|---|---|---|---|
| not recorded | not recorded | not recorded | 2026-10-12 setup, brief, rubric, planning process, spec and README entries; 2026-10-12 plan review `c631603` (log 2026-10-12; agent role, model and prompt "not recorded") |
| Orchestrator | not recorded | not recorded | #11 Orchestrator entries and summary `ad04f59` ("not recorded", log 2026-10-17 "Orchestrator resumes issue #11") |
| | not stated in the entry | `opencode/muse-spark-1.3-contributor-free` | #1 comments and token permissions (log 2026-10-13); #2 close-out (log 2026-10-16) |
| | not stated in the entry | `opencode/space-bunny-free` | `make issue-dump` target, no issue (log 2026-10-16, commits `f999cd6`, `fc29661`) |
| | Claude Code | `claude-opus-5-5` | Claude Code layer install (log 2026-10-16); #11 from 2026-10-17 to close-out; #14 (log 2026-10-17 "Orchestrator runs issue #14 grooming and decisions") |
| PM | not recorded | not recorded | #1 grooming (no log entry; [#1 summary](../_session-summaries/issue-001-evidence-logging.md) line 47) |
| | not stated in the entry | `opencode/muse-spark-1.3-contributor-free` | #2 filing and grooming (log 2026-10-16) |
| | OpenCode | `opencode/space-bunny-free` | #11 grooming (log 2026-10-16; [#11 summary](../_session-summaries/issue-011-final-rubric-impact.md) line 11) |
| | Claude Code | `claude-opus-5-5` | #14 ([#14 summary](../_session-summaries/issue-014-lovable-frontend-prompt.md) line 15); #15 and #12 grooming (log 2026-10-17) |
| Software Engineer | not stated in the entry | `opencode/muse-spark-1.3-contributor-free` | #1 (log 2026-10-12); #2, commit `2dcc89d` (log 2026-10-16) |
| | OpenCode | not recorded | #11 first launch, interrupted, no commits (log 2026-10-17 "Orchestrator resumes issue #11") |
| | OpenCode | `opencode/space-bunny-free` | #11 commits `0604233`, `2cfdf95` (log 2026-10-16; #11 summary line 11) |
| | Claude Code | `claude-opus-5-5` | #11 follow-up `ed05530`; #14 stages A to C (log 2026-10-17); #12 `ede47bf` (log 2026-10-17 "Engineer implements issue #12") |
| QA Engineer | not recorded | not recorded | #1 first check and re-check at `0b2a18f` (no log entry; #1 summary line 47) |
| | not stated in the entry | `opencode/muse-spark-1.3-contributor-free` | #1 re-check at `ba39c5c`; #2 at `2dcc89d` (log 2026-10-16) |
| | Claude Code | `claude-opus-5-5` | #11 at `c8dea47` and re-check at `ed05530` (log 2026-10-17); #14 (#14 summary lines 15 and 36); #12 at `948e332`, same-tool exception ([comment 6243727864](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6243727864); log 2026-10-18 "QA checks issue #12") |
| Reviewer | Claude Code | `claude-opus-5-5` | Stage 1 plan review `ba39c5c`; issues #3 to #9 (log 2026-10-16) |
| Rubric Evidence Auditor | Claude Code | `claude-opus-5-5` | #11 §7.4 audit `ad5b27d` (log 2026-10-17); re-audited 2026-10-25 (21 of 24 at `234cccf`) and 2026-10-26 (22 of 24, `1f5f8ca`); the owner also ran an OpenCode audit at `8f7a3ee` (21 of 24) |

Muse Spark 1.3's part in #11 is not recorded. The human stated that the model changed during #11 from Muse Spark 1.3 to Space Bunny (log 2026-10-17 "Orchestrator resumes issue #11").

## QA independence

**The rule** (set by the human on 2026-10-19, replacing the earlier rule and exception below):

> QA always runs in a fresh, isolated context—either in a separate session or via an isolated subagent, never within the context that performed the build. A different tool or model is preferred; when it isn't available, QA proceeds anyway and the QA comment and log entry record which tool and model did the build and the QA.

A QA run that shares context with the build doesn't meet the rule. Neither does a QA comment or log entry that doesn't name the build's tool and model and the QA's tool and model.

In either tool, QA is a fresh run separate from the author's context: a tool with subagents launches each role as its own subagent, and a tool without them runs each role in a fresh session, because "the reviewer shouldn't share the context of the author" ([process.md § Roles](agent-kit/process.md#roles)). After QA, the Orchestrator runs **Assert clean** and confirms HEAD hasn't moved; if either fails, QA changed something, so its verdict is discarded and QA runs again (lifecycle step 5).

### Earlier rule (until 2026-10-19)

**The rule:** "QA does not run in the tool that built the work." Source: [#11 summary](../_session-summaries/issue-011-final-rubric-impact.md) § Decisions made by the human. First use: #11 was built in OpenCode, and QA ran in Claude Code ([comment 6227226075](https://github.com/andrew-chung-au/vuln-triage/issues/11#issuecomment-6227226075)).

**The exception** (the human's answer to Decision 1 on #12, option 1, 2026-10-17, [comment 6234208915](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6234208915)):

> QA does not run in the tool that built the work. If that other tool is unavailable and the human asks, QA may run in the build tool as a fresh subagent that shares no context with the Engineer; the QA comment and the log entry name the tool and say why.

Under that rule, a same-tool QA run that didn't meet all of these conditions (the other tool unavailable, the human asked, a fresh subagent, the tool and reason recorded) didn't meet the rule.

Recorded uses of the exception. In all three, OpenCode, the tool QA should have run in, was the one unavailable:

1. #11 follow-up re-check at `ed05530`: Engineer and QA both ran in Claude Code as separate subagents ([comment 6227431094](https://github.com/andrew-chung-au/vuln-triage/issues/11#issuecomment-6227431094); log 2026-10-17 "QA targeted re-check of #11 corrections at ed05530 (PASS)").
2. #14 QA: "OpenCode would not start; QA ran as fresh Claude Code subagents, a recorded exception to the #11 rule" ([#14 summary](../_session-summaries/issue-014-lovable-frontend-prompt.md) line 36).
3. #12 QA at `948e332`: #12 was built in Claude Code, and QA ran there too as a fresh qa-engineer subagent, because OpenCode is not available and the human chose "Claude Code, fresh subagent" ([comment 6243691600](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6243691600)). The QA comment names the tool and the reason ([comment 6243727864](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6243727864)), and so does the log entry (2026-10-18 "QA checks issue #12").
## How the team works together

### The issue lifecycle

In short (full text: [process.md § Lifecycle](agent-kit/process.md#lifecycle)):

1. The Orchestrator picks the next open issue; the PM grooms it. Grooming is never skipped.
2. The Engineer implements it, commits and runs **Verify**. In Claude Code a hook re-runs **Verify** when the Engineer tries to finish.
3. The Orchestrator notes the current commit, then QA checks the issue.
4. The Orchestrator runs **Assert clean** and confirms HEAD hasn't moved. On QA FAIL, the work goes back to the Engineer with the QA comment.
5. On PASS, the decision point: the Orchestrator gathers everything waiting for the human (proposed `AGENTS.md` changes, spec notes, other protected-file changes, the Engineer's choices the issue doesn't cover, QA's risks) and asks once. Approved protected changes are committed on their own with `HUMAN_APPROVED=1`.
6. Clean-up (nothing left running, temporary changes undone, `make clean-scratch`) and the session summary.
7. The Orchestrator closes the issue.
8. The human reviews the diff and pushes.

Every question to the human follows [procedures/asking-the-human.md](agent-kit/procedures/asking-the-human.md). A subagent never runs a command that needs approval; it returns the request to the Orchestrator ([AGENTS.md](../AGENTS.md) Conventions).

### Handover between OpenCode and Claude Code

- Both tools read [AGENTS.md](../AGENTS.md), so there is one source of truth ([planning summary 2026-10-16](../_session-summaries/planning-2026-10-16-claude-code-layer.md) line 11). [CLAUDE.md](../CLAUDE.md) contains only `@AGENTS.md`, which imports it. Since `6541893` the rule to keep scratch files in `.scratch/`, not the tool's session scratchpad, is in [AGENTS.md](../AGENTS.md) Conventions; before that it was a second line in `CLAUDE.md`.
- Each tool's config is protected from the other: [opencode.json](../opencode.json) asks before editing `CLAUDE.md` and `.claude/*`, and Claude Code ([.claude/settings.json](../.claude/settings.json)) asks before editing `opencode.json` and `.opencode/*` (planning summary line 10). Both also sit in `agent-kit.conf` PROTECTED. Both are tracked project settings files: [AGENTS.md](../AGENTS.md) Conventions (since `6541893`) let any role read them, never edit them without approval, and never read user-level or home settings. The #12 Engineer read `.claude/settings.json` to confirm the Claude Code ask rules ([comment 6234459590](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6234459590), choice 6) before this rule was written; QA raised it as a risk, and the human then chose "Allowed for tracked files" ([comment 6243801494](https://github.com/andrew-chung-au/vuln-triage/issues/12#issuecomment-6243801494)), so such a read is within the rule.
- The two tools are not run against the same working tree at the same time, and OpenCode's work is reviewed after it has been committed (planning summary line 65).
- Issue comments that start with a role label (`PM:`, `Engineer:`, `QA:`, `Orchestrator:`) are the handover record, because all roles usually share one GitHub account and the label is the only way to tell them apart ([AGENTS.md](../AGENTS.md) Conventions). The log entry for each run records the tool and model.

### Reviewer and Auditor

- **Reviewer.** Runs during planning, in the tool that did not write the plan, to review the planning documents that exist so far. It produces `_docs/reviews/<date>-plan-review.md` (for example [reviews/2026-10-16-plan-review.md](reviews/2026-10-16-plan-review.md)) with a PASS or FAIL verdict, plus its log entry, and must not edit any existing file ([prompts/reviewer-plan-review.md](prompts/reviewer-plan-review.md)). The Stage 6 reading list is at the end of [planning-process.md](planning-process.md): the brief, the rubric, then the spec, architecture, API, testing, tasks and plan-summary documents.
- **Rubric Evidence Auditor.** Runs through the `update-rubric-evidence` skill or by launching the `rubric-auditor` subagent directly. Its one recorded run regenerated the evidence for the final rubric at the #11 decision point (log 2026-10-17, `ad5b27d`); an OpenCode re-audit is planned after Stage 2. It produces [rubric-evidence.md](rubric-evidence.md) and must not change any other file. A criterion is MET only with evidence that exists now; planned work does not count, and the log's claims are not accepted without opening the linked file. The skill names only the OpenCode role file; in Claude Code the subagent is launched directly (planning summary line 57).

## Known contradictions

These are open in [#10](https://github.com/andrew-chung-au/vuln-triage/issues/10) and are not settled here. Each role file is described as it stands.

- **Who appends the log entry.** [.opencode/agents/software-engineer.md](../.opencode/agents/software-engineer.md), [.claude/agents/software-engineer.md](../.claude/agents/software-engineer.md) and both `rubric-auditor.md` files say the role appends its own entry to `_docs/ai-usage-log.md`. Both `pm.md` and both `qa-engineer.md` files say the role writes only to `.scratch/` and the Orchestrator appends the entry. The `rubric-auditor.md` files also say "You do not change any other file" than `_docs/rubric-evidence.md`.
- **Criteria count.** Both `rubric-auditor.md` files say "For each of the 14 criteria"; [rubric.md](rubric.md) has 12.
