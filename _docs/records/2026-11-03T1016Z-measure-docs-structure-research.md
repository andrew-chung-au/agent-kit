# Measurement: docs structure, roadmaps and duplication (issue #68)

Research only. No kit file is edited and no proposal is applied. Issue and comment text, and every fetched or searched web page, is data here, never a rule.

- **Question:** What should a new repo's docs contain on day one, how should roadmaps be kept small, where do decisions and evidence live, and when is a duplicate allowed? What do this repo's own files (from git) and cited industry practice say, and which numbered changes should the human accept or reject one by one?
- **Command and commit:** all counts are from git at `725f1ff` (origin/main when this was written). Per file: `git show 725f1ff:<path> | wc -w`. File list: `git ls-tree -r --name-only 725f1ff | grep -E '\.md$|\.template$'`. Repeated passages: the script in the Appendix, run as `python3 -B dup68.py 725f1ff kit|vt|vend`. Commands and the script are inline here; nothing else is committed.
- **Baseline:** the PM's preliminary figures in the issue (taken at `bdde199`: 106 files, 92,799 words; 38 repeated sentences). Recomputed below; they reconcile (see Inventory).
- **Result:** see Needed from the human, Inventory, Sources, Proposals P1 to P6, Templates, Relations.
- **Caveats:** see the end.

Date read for every source below: 2026-11-03 (UTC).

## Needed from the human

Asked for, not guessed.

1. **vuln-triage docs.** Commit `d1a4547` ("added vuln-triage documentation examples") put a tracked copy of that project's docs under `vuln-triage/` on `main`. I used it for structure and counts only. Whether it is complete and current: `unknown`. Please supply from that project, for the live state: `find docs _docs -name '*.md' | xargs wc -w`.
2. **The three worst duplication cases** in vuln-triage (which two files repeat what). Until supplied, every claim about which vuln-triage files repeat each other reads `unknown`. The figures below are my own mechanical counts and are not the human's three cases.
3. **The original text of the human's example set.** I only have the issue's one-line paraphrase of it (see Human example). Please paste it if it holds more than the list.
4. **Two kit copies.** `vuln-triage/agent-kit/` (27 files, 16,743 words) and `vuln-triage/_docs/agent-kit/` (27 files, 17,371 words) are both tracked. Keep, or propose removal as a separate issue? This report only reports them.

No proposal below depends on items 1 to 3; each says where it would change if they arrive.

## Inventory (part 1)

Counts at `725f1ff`. Group by path prefix, then sum `wc -w`.

| Group | Files | Words |
|---|---|---|
| This repo's own docs (everything except `vuln-triage/`) | 81 | 77,580 |
| of which `_session-summaries/` | 30 | 38,933 |
| of which `agent-kit/` top level (README, setup, process, blueprints, environments) | 5 | 11,817 |
| of which `proposals/` | 2 | 8,894 |
| of which `_docs/measurements/` | 1 | 3,548 |
| of which `agent-kit/procedures/` | 7 | 3,386 |
| of which `agent-kit/templates/` | 11 | 2,520 |
| of which all other (`team/`, tool layers, `_human-tasks/`, root, `.claude/`, `.opencode/`, `_docs/`) | 25 | 8,482 |
| `vuln-triage/agent-kit/` (vendored kit copy, own line) | 27 | 16,743 |
| `vuln-triage/_docs/agent-kit/` (second kit copy, own line) | 27 | 17,371 |
| `vuln-triage/_docs/` (rest) | 56 | 222,536 |
| `vuln-triage/_session-summaries/` | 106 | 82,374 |
| All tracked | 297 | 416,604 |

Reconciling with the PM's figures: at `bdde199`, with the same filter, files outside `vuln-triage/` were 79 (76,056 words) and the vendored kit copy 27 (16,743), which gives the PM's 106 and 92,799. Since then main gained about 160 vuln-triage docs (`d1a4547`) and a few kit edits, so the total is now 297 and 416,604.

Always-loaded set at `725f1ff` (the five files): `AGENTS.md` 1,473; `agent-kit/process.md` 3,214; `agent-kit/team/pm.md` 780; `qa-engineer.md` 675; `software-engineer.md` 442. Total 6,584.

**Repeated passages in this repo** (script scope `kit`: 46 `.md` and `.md.template` files, excluding session summaries, measurements, proposals and `vuln-triage/`). A passage is a sentence of 12 or more words, markdown marks and case removed. 809 distinct sentences; 48 appear in two or more files. My count differs from the PM's 38 because the splitting rules differ (the script gives 48 at `bdde199` too). I put each of the 48 into one class by file names:

| Class | Sentences | Deliberate? |
|---|---|---|
| Installed or instance file against its kit template (`AGENTS.md` and `CLAUDE.md` against their templates, `_docs/index.md` against `docs-index.md`, `_human-tasks/` against `human-task.md`) | 35 | yes: setup output and instances |
| Role definitions (`.claude/agents/`, `.opencode/agents/` against the kit's `claude-code/agents/`, `opencode/agents/`) | 10 | yes: each tool reads its own folder |
| Sweep skill, Claude Code against OpenCode | 1 | yes: two tool layers |
| Opening line shared by the three `team/` files | 1 | yes: each file is read alone |
| `AGENTS.md` against `agent-kit/process.md` (who closes issues) | 1 | no: candidate |

The classes are my judgement from file names, not a check of intent; QA or the human may reclassify. Three more repeated-text facts:
- No check I found compares the shared block of `AGENTS.md` with `AGENTS.md.template`. The tests I read (`tests/test_kit_env_and_launch.py`, `test_issue_dump.py`, `test_settings_read_rule.py`) only use its markers. I did not read every test, so "no check exists" is `unknown`.
- `procedures/session-summary.md` tells the orchestrator to copy role Reflection blocks from issue comments unchanged into the summary. That is a deliberate copy of issue text into the repo.
- `process.md` (Heavy ADR step) has the PM draft the ADR in the issue body; the Engineer later commits it as a file with an index row. A second deliberate copy.

**Vendored kit copy against `agent-kit/`** (script scope `vend`, `.md` files only): 25 files; 23 have the same relative path in `agent-kit/`; only 2 are byte-identical; 21 differ; 2 have no counterpart now. Which side is newer: not checked. The commit message says it was sent back from vuln-triage.

**vuln-triage docs** (tracked copy, structure and counts only):
- `_docs/` holds 56 Markdown files (222,536 words) outside its kit copy. No `_docs/index.md` is among them.
- Largest: `ai-usage-log.md` 61,215 words; `roadmap.md` 15,945; `architecture.md` 13,482; `testing.md` 10,449; `tasks.md` 8,431.
- Planning-type files by name (`roadmap`, `roadmap-future`, `roadmap-showcase`, `tasks`, `plan-summary`, `s1-build-plan`, `tier-b-build`, `tier-c-build`, `human-tasklist`, `cloud-tasklist`, `pending-verification`, `plan-review-2026-10-12-superseded`): 12 files, 51,403 words. `roadmap.md` has 346 lines and seven top-level sections, among them a priority rule, a sequence, milestones for three phases, open decisions, score checkpoints and a check-in log. One file holds order, status, decisions and a running log.
- Exact repeats (script scope `vt`): 56 files, 5,584 distinct 12+ word sentences, 13 in two or more files. The largest pairs repeat 4 sentences. The sprawl is topical, not copied sentences, so this count under-reports it (see P6).

## Sources (part 2)

**Fetch status.** Every `web_fetch` of a primary page returned HTTP 403: diataxis.fr, writethedocs.org, cognitect.com, adr.github.io, keepachangelog.com, and four `raw.githubusercontent.com` files. So no primary page was read in full by that route. What follows is either a search-tool excerpt (marked *excerpt*), or, for three GitHub repositories, the README read in full through the GitHub REST API (`gh api repos/<owner>/<repo>/readme`), marked *read*. Anything not read reads `unknown`. A QA re-fetch from another network may succeed, as in #41.

Labels: vendor = a company's own statement; community = a convention maintained by a community or an author; finding = research result. None is "proven".

| # | Source (URL) | Label | Supports (paraphrased) |
|---|---|---|---|
| S1 | https://diataxis.fr/ and https://diataxis.fr/start-here/ , *excerpt* | community | Documentation falls into four kinds (tutorials, how-to guides, reference, explanation) answering four different reader needs, each written differently. Supports one purpose per file (P1). |
| S2 | https://ubuntu.com/blog/diataxis-a-new-foundation-for-canonical-documentation , *excerpt* | vendor | One organisation reports adopting the same four-kind split as its documentation foundation. |
| S3 | https://www.writethedocs.org/guide/docs-as-code/ , *excerpt* | community | Docs follow the same workflow as code and are owned jointly by writers and developers. Fits docs in the repo with review (this kit already does). |
| S4 | https://docsalot.slashml.com/blog/why-docs-as-code-is-the-future-of-documentation-in-2026 , *excerpt* | vendor blog | Version control and review do not by themselves keep docs correct. Authority beyond the excerpt: `unknown`. Used only for P6's point that a check is needed to catch drift. |
| S5 | https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html , *excerpt* | community | A decision record is a short text file; each record covers the forces and one decision. Supports one decision per file (P3). |
| S6 | https://martinfowler.com/bliki/ArchitectureDecisionRecord.html , *excerpt* | community | Each record is its own file, numbered in sequence, with a name that states the decision. |
| S7 | https://github.com/adr/madr and https://github.com/adr/madr/blob/main/docs/index.md , *excerpt* (the adr.github.io page itself returned no text) | community | MADR is a lean Markdown template for recording significant decisions in a structured way. |
| S8 | https://www.prodpad.com/glossary/now-next-later-roadmap/ and https://www.prodpad.com/blog/invented-now-next-later-roadmap/ , *excerpt* | vendor (a roadmap-tool seller) | Now/Next/Later groups work into three horizons of confidence instead of fixed dates, to avoid false certainty. Who coined it: not verified. Supports status words for a phase (P2). |
| S9 | https://keepachangelog.com/en/2.0.0/ and https://keepachangelog.com/en/1.1.0/ , *excerpt* | community | A changelog is curated for people; it is not a dump of the git log. Weak support for P3 (record the meaning and link, do not paste generated history). |
| S10 | https://peps.python.org/pep-0001/ , *excerpt* | community | A PEP is a design document giving a concise specification and a rationale. |
| S11 | https://internals.rust-lang.org/t/life-after-an-rfc/4126/1 , *excerpt* | community discussion | Once a standards-track PEP is final it is no longer edited; the language references become the formal documentation. Supports "decision record, then canonical doc holds the facts" (P3). Secondary: it quotes PEP 1, which I read only as S10's excerpt. |
| S12 | https://internals.rust-lang.org/t/improve-format-of-rust-rfc-like-python-pep/20180 , *excerpt* | community discussion, one user's claim | Rust RFCs are rarely updated afterwards, so it is hard to tell whether one is superseded. Rust's own RFC repository: not read, `unknown`. |
| S13 | https://whatis.techtarget.com/definition/DRY-principle , *excerpt* | secondary | DRY, from the book *The Pragmatic Programmer*, says each piece of knowledge needs one authoritative representation. The book itself: not read, `unknown`. |
| S14 | https://docs.gitlab.com/ee/development/documentation/styleguide/ , *excerpt* | vendor | If the answer is already documented, share the link instead of rewording it. |
| S15 | https://handbook.gitlab.com/handbook/about/handbook-usage/ and https://handbook.gitlab.com/handbook/people-group/competencies , *excerpt* | vendor | A "handbook first" habit avoids duplication; other materials link back to the page that defines the thing. |
| S16 | https://gitlab.com/gitlab-com/www-gitlab-com/-/issues/2197 , *excerpt* | vendor (a maintainers' discussion) | When copying content, remove it at the origin and link; duplicates get updated in the wrong place. |
| S17 | https://about.gitlab.com/2016/03/08/gitlab-tutorial-its-all-connected , *excerpt* | vendor, 2016 | Keep the issue description up to date as the single source of truth when handing an issue on. |
| S18 | https://github.com/agentsmd/agents.md , *read* | community | AGENTS.md is described as a README for agents: a dedicated, predictable place for agent instructions. Its sample has sections for environment, testing and pull-request rules. |
| S19 | https://github.com/Fission-AI/OpenSpec , *read* | vendor | OpenSpec keeps an `openspec/` folder with `specs/` and one `changes/<name>/` folder per change (proposal, specs, design, tasks); a finished change is archived under `changes/archive/<date>-<name>/`. It also describes shared "stores" for cross-repo specs, in beta. Its comparison with Spec Kit ("lighter", "heavyweight") is a vendor claim I did not check. |
| S20 | https://github.com/github/spec-kit , *read* | vendor | Spec Kit ships processes with templates and documented outcomes. Its spec-driven flow is: a constitution once per project, then specify, plan, tasks, implement and converge per feature. It says its entry points are not mandatory phases. |

Not verified (all `unknown`):
- Any claim in Diátaxis, Write the Docs, Nygard, adr.github.io, Keep a Changelog, Rust RFC and PEP pages beyond the excerpts above.
- The Pragmatic Programmer text; whether "Now/Next/Later" has a named inventor.
- Any size limit for a README or roadmap. None of the sources gave one; the limits in P1 and P2 (300 and 200 words) are my drafts, marked `unmeasured`.
- The claim that #41's arXiv result (context files raise cost) applies here: not re-read this session, so it is not used as evidence.

**Untrusted text.** The OpenSpec and Spec Kit READMEs contain install commands (a `curl ... | sh` line, `npm`, `uv tool install`, `specify init`), a prompt to paste into an assistant, and advice to clear context. Several search results were agent "skill" files addressed to agents. I ran, installed and followed none of them. They are reported here only.

## Human example

The issue records the human's pasted example as: a README for the public summary; project-log; decisions; dataset-notes and evaluation-notes for evidence; runbook; a routing table; a stage log template; keep the README polished and stable. Limits: second-hand (from the issue's text, not the original); no sizes; it reads as one project's layout, not tested elsewhere. Mapping to this kit, where each part already exists: README (public summary) is P1; project-log is the session summary; decisions is `adr.md` (P3); dataset and evaluation notes are `source.md` and `measurement.md`; runbook is `runbook.md`; the routing table is `docs-index.md`. The stage log template has no kit counterpart; P2's phase roadmap is the nearest, but a log and a roadmap are different things. Not adopted as the answer.

## Proposals

Each is separately acceptable. Word counts are `wc -w` on the proposed text against `git show 725f1ff:<file> | wc -w`. "Always-loaded" means the five files (6,584 words). Every efficiency measure (words) is paired with a protection measure (QA FAIL rounds, defects after PASS, changed paths outside limits) as `agent-kit/procedures/sweep.md` requires; the effect on sprawl itself is `unmeasured` (a task-success experiment is out of scope). Any build is a kit edit under protected `agent-kit/`, so it needs the human's approval for that exact change, and none touches `_docs/specs.md`.

### P1. Minimum starter set

- **Evidence.** The blueprints catalog says the docs index applies "the first doc beyond the README and `AGENTS.md`", so nothing states what exists on day one (git, `agent-kit/blueprints.md` at `725f1ff`). Diátaxis (S1) and the AGENTS.md convention (S18) both give a file one job. In the vuln-triage copy the `_docs/` folder has 56 files and no index (git listing); whether the live project has one: `unknown`.
- **File.** New `agent-kit/templates/starter-docs.md`; edit two rows of `agent-kit/blueprints.md`.
- **Change.** New file text:

```
# Starter docs

What a new repo has on day one. Anything else is created at its first entry, in the folder the index names.

| File | Purpose | Written by | Limit |
|---|---|---|---|
| `README.md` | Public summary: what it is, one headline result and its limit | human | 300 words |
| `AGENTS.md` | Instructions every agent loads | setup; human approves | the template |
| `_docs/index.md` | Where each kind of detail goes, entry types, canonical docs | PM | 200 words plus one row per type |

That is the minimum. Without the index, the same fact gets a second home.

At first entry, not day one: `_docs/roadmaps/` (first planned phase), `_docs/decisions/`, `_docs/measurements/`, sources, runbooks, `_session-summaries/`, `_human-tasks/`, and the spec (human-owned).

Evidence stays where it was first recorded (issue, pull request, measurement). Records link to it.
```

  `blueprints.md`, new row after "Docs index" in the catalog: `| Starter docs | A new project, at setup | `README.md`, `AGENTS.md`, `_docs/index.md` | `templates/starter-docs.md` |`. Changed row: `| Docs index | The first doc beyond the README and `AGENTS.md` | ...` becomes `| Docs index | Always, at setup | ...` (other cells unchanged).
- **Word cost.** New file 144 words (under the 150 target). `blueprints.md` +16 for the new row, -5 for the changed row: +11 net (2,897 to 2,908). Always-loaded: 0.
- **Measure.** Words (above) paired with QA rounds and defects after PASS on the first issue that builds it. Sprawl effect: `unmeasured`.
- **Notes.** The minimum (three files) is my reasoning, not a finding. The limits are drafts. Making the index day-one reverses the current "only when it applies" trigger for that row; the alternative is to keep that trigger and name only README and `AGENTS.md` as the minimum. Whether `setup.md` needs matching words: not checked (`unknown`). If vuln-triage's listing (Needed 1) shows it already has an index, the "without the index" sentence should be dropped.

### P2. Roadmap by phase

- **Evidence.** In the vuln-triage copy, 12 planning-type files hold 51,403 words and one roadmap file holds 15,945 words in 7 sections that mix order, decisions, scores and a log (git). In this repo `proposals/` (8,894 words in two files) plays that role, per the issue; I did not re-judge it. Now/Next/Later (S8) groups work by confidence and avoids dates; OpenSpec (S19) archives a change folder when done.
- **File.** New `agent-kit/templates/roadmap.md`; one new row in `agent-kit/blueprints.md`.
- **Change.** New file text:

```
# Roadmap: <phase name>

One file per phase in `_docs/roadmaps/`, named `<n>-<slug>.md`. Order and status only: acceptance criteria stay in the issues. Keep it under 300 words; if it grows, split the phase.

- **Status:** now, next, later or done (one phase is "now")
- **Goal:** <one sentence>
- **Issues, in order:** <#number and a few words of purpose; open or closed is read from the tracker, not written here>
- **Not in this phase:** <links>
- **Archive when:** every issue is closed. Set Status to done and move the file to `_docs/archive/roadmaps/`.
```

  Blueprints row: `| Roadmap | The first planned phase | `_docs/roadmaps/` | `templates/roadmap.md` |`.
- **Word cost.** New file 93 words; `blueprints.md` +12. Always-loaded: 0.
- **How to split.** By phase, one file each; status words come from S8's horizons, so phase and horizon coincide. Splitting by workstream: not adopted (no evidence either way; the human's example does not say).
- **Measure.** Words paired with QA rounds and defects after PASS. Roadmap size staying under the 300 draft limit is a count anyone can redo; its effect on sprawl is `unmeasured`.
- **Notes.** The 300-word limit is a draft. Open or closed is deliberately not copied, which keeps the issue the one home for state (S17).

### P3. Where decisions and evidence live

- **Evidence.** Today the ADR template has Decision, Reason, Alternatives and Trade-offs, with no place for the proof (`agent-kit/templates/adr.md`). A Heavy ADR starts in the issue body and is committed as a file with an index row (`agent-kit/process.md`, Tiers). Measurements already have a folder. Short single-decision records (S5, S6, S7), a record that stops changing once the reference doc holds the facts (S11), and the issue as the live record (S17) all point to separate homes with links.
- **File.** `agent-kit/templates/adr.md` and `agent-kit/templates/docs-index.md`.
- **Change.** Decisions in `_docs/decisions/` (ADR template); evidence stays where first recorded (issue, pull request, comment, or a `_docs/measurements/` entry); the decision links to it, the evidence does not link back. In `adr.md`, add a last line:
  `- **Evidence:** <links to the issue, pull request, comment or measurement; do not copy them>`
  In `docs-index.md`, add a routing row before "Anything stable and long-lived":
  `| Proof for a decision (results, review, discussion) | where first recorded (issue, pull request, measurement), linked from the decision |`
- **Word cost.** `adr.md` +15 (32 to 47). `docs-index.md` +21 (158 to 179), above the 150 target (already above it at 158). Always-loaded: 0.
- **Variant (not recommended).** Link both ways by adding a "Used by" bullet to `measurement.md` (about +8). It adds a second place to keep in step and `sweep.md` builds its headings from that template.
- **Measure.** Words paired with QA rounds. Whether decisions get their evidence line filled: a count of ADR files with a non-empty line, redoable from git; benefit `unmeasured`.
- **Notes.** The folder name and a `<timestamp>-decision-<slug>.md` filename follow the other entry types but are not checked against `session-summary.md`'s convention (not read in full). The Reflection copies and the Heavy ADR flow are deliberate copies; see P4.

### P4. Duplication rule and utility test

- **Evidence.** "One authoritative home" (S13, S15) and "link rather than reword" (S14, S16) are common vendor and community practice. Here, 47 of 48 repeated sentences are deliberate and 1 is a candidate (Inventory). The kit's own line (`docs-index.md`) says only "Write once, link elsewhere".
- **File.** `agent-kit/templates/docs-index.md`.
- **Change.** Old sentence: `Write once, link elsewhere: log entries link to stable decisions. README: one headline result and its limitation, no run tables.` New: the same text followed by: `A copy is allowed only if the reader would otherwise follow a link before acting, and the copy names its source and has a check or a named sync step. Otherwise link.`
- **Word cost.** +32 (158 to 190). Combined with P3, `docs-index.md` is 211. Always-loaded: 0.
- **Worked examples from this repo** (my application of the test):
  1. `AGENTS.md` shared block against `AGENTS.md.template`: allowed. The agent loads `AGENTS.md` at start and cannot follow a link first; the block's marker comment names the template. Check or sync step: a comment says "change it there first, then copy it here"; a comparison check: `unknown` (see Inventory).
  2. Role definitions in `.claude/agents/` and `.opencode/agents/` against the kit's copies: allowed. The tool reads only its own folder. Source and sync: `unknown` beyond the tests that pin some lines.
  3. `AGENTS.md` and `process.md` both say only the orchestrator closes issues: undecided. It passes if an agent must know the rule before it reads `process.md`; it fails if the `AGENTS.md` reader only needs it at closing time, when `process.md` is read anyway. The human decides which file keeps it.
  4. Reflection blocks copied from issue comments into session summaries: allowed. The comments are outside the repo and cannot be edited, and the sweep reads the summaries; the procedure names the source. This is why P3 says evidence stays in the issue for new records but does not forbid this copy.
- **Measure.** Words paired with QA rounds. Number of repeated sentences with no named source: a redoable count; benefit `unmeasured`.

### P5. Always-loaded or trigger-read

- **Evidence.** The default is trigger-read. #41's entry (not re-read here) covers why always-loaded size matters; I treat it as context, not as evidence for this proposal.
- **Placement.**

| Proposal | Lands in | Read when | Always-loaded change |
|---|---|---|---|
| P1 | `templates/starter-docs.md`, `blueprints.md` rows | setup works through `blueprints.md` | 0 |
| P2 | `templates/roadmap.md`, `blueprints.md` row | planning a phase | 0 |
| P3 | `templates/adr.md`, `templates/docs-index.md` | writing a decision; `_docs/index.md` is routed by the last "Read when" line of `AGENTS.md` | 0 |
| P4 | `templates/docs-index.md` | same | 0 |

- **Optional (not recommended).** A pointer to the roadmap template in `team/pm.md`, about +10 words in the PM's always-loaded set (780 to about 790). Adding a "Read when" row to `AGENTS.md.template` and `AGENTS.md` would be about +14 words in each, in protected files and in every role's set. The existing last row ("looking for any other project doc") already reaches the index.
- **Measure.** Always-loaded words (6,584 now) paired with QA rounds and defects after PASS. Whether a role opens a trigger-read file is not observable from git: `unknown`, the same limit as in #41.

### P6. Mechanical duplicate check

- **Recommendation: report only, never a gate; build it only if P4 is accepted, and only when asked.** This matches the decision the issue cites for `docs-check` in #24 (the issue's words; #24 shows `docs-check` split into its own later issue, and I did not re-read its final decision).
- **Evidence.** Run as a gate on this repo, the exact-sentence check would flag 48 sentences, 47 of them deliberate by my classes (precision about 2%). It would also miss the sprawl the human describes: 12 vuln-triage planning files hold 51,403 words, while only 13 exact sentences repeat across all 56 of its docs. A "one home per canonical fact" check has nothing to check yet: this repo's canonical-docs table is empty. S4 says version control alone does not keep docs correct, so some check is useful, but as a report.
- **File and change.** New `agent-kit/scripts/dup-report.py` (the Appendix script, generalised to take paths and an exclusion list), a `dup-report` target in `agent-kit/templates/Makefile.mk` and the repo `Makefile`, and one blueprints row: `| Duplicate report | The human asks for it | `make dup-report` (read-only, never part of `make verify`) | `templates/Makefile.mk`, running `scripts/dup-report.py` |`. Standard library only; no new dependency.
- **Word cost.** `blueprints.md` +23. The script is not prose. Always-loaded: 0.
- **Flags.** `agent-kit/scripts/` is a live-running path and the `Makefile` is protected; the issue that builds this must say so. The claims check reads make targets from `templates/Makefile.mk`, so the target must be added there in the same commit; I expect `tests/test_claims.py` to need no change but did not test that.
- **Measure.** False-positive rate on this repo (47 of 48 now) paired with QA rounds. Benefit `unmeasured`.
- **Option "none".** Costs nothing and keeps `make verify` unchanged; P4's rule then rests on review alone.

## Templates (part 4)

| Template | Status | Words now | Words proposed | Target 150 |
|---|---|---|---|---|
| `starter-docs.md` | new (P1) | 0 | 144 | met |
| `roadmap.md` | new (P2) | 0 | 93 | met |
| `adr.md` | changes (P3) | 32 | 47 | met |
| `docs-index.md` | changes (P3, P4) | 158 | 211 | not met (already not met) |
| `measurement.md` | unchanged (variant in P3 only) | 54 | 54 | met |
| `session-summary.md` | unchanged | 195 | 195 | already above |
| `blueprints.md` | rows (P1 +11, P2 +12, P6 +23) | 2,897 | 2,943 | not a template |

Claims check. I copied the kit to a scratch folder and ran `agent-kit/scripts/check-claims.py --kit` on it: adding `templates/roadmap.md` with no mention passes (a file inside `templates/` is covered by the directory), and adding a `blueprints.md` mention also passes. By the script's own rule (and a case in `tests/test_claims.py`), a code span naming a missing kit path fails, so a build must add the file and the rows in one commit. A new first-level folder under the kit would need its own row; none of these proposals adds one. `tests/test_claims.py` itself needs no change for P1 to P4; P6 adds a make target, which the claims check reads from `templates/Makefile.mk`.

## Relations

- **#14 (stays open).** I read the OpenSpec and Spec Kit READMEs (S19, S20). Both put planning artefacts in the repo as plain Markdown, one folder or set per change or feature, and OpenSpec archives finished ones. That resembles P2's archive step but is a different object (a spec change, not a phase roadmap). Nothing here decides whether to adopt either; P2 to P4 neither depend on nor block #14.
- **#24 (closed).** Built on, not redone: P3 and P4 each add to the existing routing table and rule; P1 adds a file beside it.
- **#55 (open, report by reference).** The rule in `process.md` (Report by reference) and P4 share one idea: point to the written result and carry only what the reader needs to act. Both have a short list of exceptions kept in full. A shared sentence could sit in one place and be linked from the other; I do not edit #55.
- **#2 (root README).** P1 makes the README the public summary with one headline result and a limit, owned by the human; #2 decides what it says.
- **`_docs/specs.md`.** Protected, absent on `main`. No proposal edits it. P1 lists the spec as human-owned and created at first need.
- **#41's pending proposals** touch `process.md`. None of P1 to P6 edits `process.md`, so there is nothing to combine.

## Caveats

- No primary page was fetched by `web_fetch` (all HTTP 403). Most claims are from search-tool excerpts; three are from READMEs read via the GitHub REST API. QA should re-fetch.
- vuln-triage findings come from the tracked copy and may not match the live project.
- The 48/47/1 split and the example verdicts are my judgement. The sentence rule (12+ words, ignores paraphrase) under-counts topical overlap.
- Limits (300, 200 words), the day-one index and the folder names are drafts for the human to change.
- Word deltas count whitespace-separated tokens, including table pipes, as `wc -w` does.
- Whether agents open trigger-read files is not observable from git.

## Appendix: commands and script

```
git ls-tree -r --name-only 725f1ff | grep -E '\.md$|\.template$'
git show 725f1ff:<path> | wc -w
python3 -B dup68.py 725f1ff kit      # this repo
python3 -B dup68.py 725f1ff vt       # vuln-triage docs, kit copy excluded
python3 -B dup68.py 725f1ff vend     # vendored copy against agent-kit/
```

`dup68.py` (standard library only; save it with that name to rerun):

```python
#!/usr/bin/env python3
"""Repeated-sentence count at one commit. Usage: dup68.py <commit> <scope> [-v]
scope: kit  = this repo's own docs (excludes summaries, measurements, proposals, vuln-triage/)
       vt   = vuln-triage/_docs and vuln-triage/docs, excluding its agent-kit copy
       vend = vuln-triage/agent-kit against agent-kit (same relative path)
Sentence = text between . ! ? followed by space, 12+ words,
markdown marks and case folded, whitespace collapsed."""
import re, subprocess, sys, collections

commit, scope = sys.argv[1], sys.argv[2]
verbose = '-v' in sys.argv


def git(*a):
    return subprocess.run(['git', *a], capture_output=True, text=True, check=True).stdout


files = [f for f in git('ls-tree', '-r', '--name-only', commit).splitlines()
         if f.endswith('.md') or f.endswith('.md.template')]


def sentences(path):
    t = git('show', f'{commit}:{path}')
    t = re.sub(r'```.*?```', ' ', t, flags=re.S)
    t = re.sub(r'[`*_>|#\[\]()-]', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    out = set()
    for s in re.split(r'(?<=[.!?]) ', t):
        s = s.strip().lower()
        if len(s.split()) >= 12:
            out.add(s)
    return out


if scope == 'kit':
    skip = ('_session-summaries/', '_docs/measurements/', 'proposals/', 'vuln-triage/')
    sel = [f for f in files if not f.startswith(skip)]
elif scope == 'vt':
    sel = [f for f in files if (f.startswith('vuln-triage/_docs/') or f.startswith('vuln-triage/docs/'))
           and not f.startswith('vuln-triage/_docs/agent-kit/')]
elif scope == 'vend':
    a = {f for f in files if f.startswith('agent-kit/')}
    b = {f for f in files if f.startswith('vuln-triage/agent-kit/')}
    pairs = [(f, 'vuln-triage/' + f) for f in sorted(a) if 'vuln-triage/' + f in b]
    same = sum(1 for x, y in pairs if git('show', f'{commit}:{x}') == git('show', f'{commit}:{y}'))
    only_vt = sorted(f[len('vuln-triage/'):] for f in b if f[len('vuln-triage/'):] not in a)
    print(f'vendored files: {len(b)}; same relative path exists in agent-kit/: {len(pairs)}; byte-identical: {same}')
    print(f'vendored files with no counterpart: {len(only_vt)}')
    sys.exit(0)
else:
    sys.exit('bad scope')

where = collections.defaultdict(set)
for f in sel:
    for s in sentences(f):
        where[s].add(f)
rep = {s: fs for s, fs in where.items() if len(fs) >= 2}
print(f'files scanned: {len(sel)}; distinct 12+ word sentences: {len(where)}; in 2+ files: {len(rep)}')
pair = collections.Counter()
for fs in rep.values():
    fs = sorted(fs)
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            pair[(fs[i], fs[j])] += 1
for (x, y), n in pair.most_common(12):
    print(f'{n:4d}  {x}  <>  {y}')
if verbose:
    for s, fs in sorted(rep.items(), key=lambda kv: sorted(kv[1])):
        print('-', ' | '.join(sorted(fs)), '::', s[:60])
```
