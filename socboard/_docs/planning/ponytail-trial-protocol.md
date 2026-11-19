# Ponytail trial protocol

**Version 1.** Registered when this file is first merged: that merge commit is the pre-registration. Later changes are appended under Amendments, never edited in place. Decision: `_docs/decisions/2026-11-06T0024Z-ponytail-trial.md`. What was read and pinned: `_docs/records/2026-11-06T0024Z-source-ponytail.md`. Order: `_docs/planning/roadmap-2-ponytail-trial.md`.

For the human, the orchestrator and the sweep PM. Engineers and reviewers do not need it (see Integrity).

## 1. Questions

1. **Safe:** does it break an invariant or a process rule?
2. **Useful:** does it find, or prevent, things our process misses?
3. **Worth it:** is the cost in extra launches and effort justified?
4. **Fit:** which function belongs in our process, in which role?
5. **Portable:** does it hold across the tools and models we rotate between?

Out of scope: whether the vendor's published numbers are true in general.

## 2. Functions under test

- **F1, independent diff review** (`ponytail-review`): read-only and advisory, run by the orchestrator after the Engineer.
- **F2, generation-time skill** (`ponytail`) loaded by the Engineer on issues that ask for it.

Deferred, each needing its own trial after F1 and F2 are decided: scope challenge at grooming, the `shortcut:` debt ledger, periodic repo audit.

## 3. Definitions

- **Qualifying issue:** Standard or Heavy tier, at least 3 acceptance criteria, QA PASS, not the Lovable scaffold.
- **Run:** one role launch on one issue. The issue is the unit of analysis. Findings cluster within an issue, so they are never counted as independent samples.
- **Arm:** treated if the approved issue's Constraints say `ponytail: on`; otherwise control. Control issues carry no ponytail line, so they are not primed. The arm is set at grooming, before a tool is chosen, alternating among comparable issues.
- **Epoch:** a period during which nothing changes that could alter behaviour on a control issue: kit version, Engineer/QA/PM role files, AGENTS.md rules that apply to control issues, the pinned skill. A change starts a new epoch; epochs are not pooled in the primary comparison.
- **Baseline band:** minimum to maximum of a metric across control issues in the epoch.

## 4. Phases and gates

Gates are sweep reviews. Each phase has at most 2 sweeps and one extension. The default when undecided is **hold**: never advance automatically.

| Phase | Minimum volume | What runs | Gate to advance | If short |
|---|---|---|---|---|
| **1 Baseline and shadow** | 5 qualifying control issues | Normal process. After QA PASS the reviewer reviews the finished diff, with findings not applied inside that issue. One cross-tool calibration (same diff, two tools). | Plumbing works (metrics from git and GitHub only; every tool used loads the skill). Baseline band recorded. At least 1 useful finding QA did not raise. **Headroom:** applying the reviewer's "smaller" findings would shrink the primary metric by more than the baseline spread. | Extend once, then inconclusive |
| **2 Treatment** | 4 treated plus 3 concurrent control | 2A: `ponytail: on` issues. 2B: live reviewer feedback on a separate subset. The reviewer rates both arms. One calibration. | Band rule and guards (section 5) | Extend once, then inconclusive |
| **3 Embed** | none | Keep, Drop or Defer per function and per tool, in a gate decision record. Monitor at each sweep. | next sweep | Hold |

**Routing after Phase 1,** by the class of useful findings: at least half "smaller or reuse" goes to 2A. At least half "correctness, security or test gap" goes to 2B. Mixed runs both. No finding QA missed stops the trial.

**Band rule (Phase 2).** *Clear:* at least 3 of 4 treated issues beat the baseline's best value on the primary metric. If issues were interchangeable that happens by chance about 1 time in 20, and they are not, so the real risk is higher. *Directional:* a majority of concurrent pairs favourable but inside the band. Extend, do not adopt.

## 5. Metrics

Every number comes from git, GitHub or the tool. A role never scores its own work. Labels come from the human.

- **Primary:** non-test, non-generated lines changed per acceptance criterion, taken at the QA PASS commit.
- **Secondary:** Engineer elapsed or active time per criterion (coarse; GitHub timestamps include idle time), tests added per criterion, reviewer time against QA time on the same issue.
- **Guards:** invariant violations (zero tolerance), files outside Constraints, defects after PASS, Verify at PASS, tests present for risky logic, QA FAIL rounds (the weakest guard, since QA strength varies). A value outside the baseline band means stop and attribute the cause; revert only if ponytail is responsible.
- **Reviewer:** at most 8 ranked findings per review. The human labels each *useful*, *correct-minor*, *wrong* or *harmful if followed*, and each is classed *smaller-reuse*, *correctness-risk*, *scope* or *invariant-conflict*. A finding is *unique* if QA did not raise it.

Human review time and approval counts are recorded, never targeted.

## 6. Covariates

1. Record at launch, never afterwards: tool, model (`auto` counts as its own model), role-file version, skill pin, tier, layer, criteria count.
2. Tool comes from git (author `Kiro Agent`, or the attribution line for other tools) and is cross-checked against the `Launch usage` line. The model is recorded there too, and `unknown` is allowed.
3. **Common support:** a tool must run issues in both arms, or its issues are excluded from the primary comparison and reported apart.
4. Stratify by tool or model only with at least 3 issues per cell; otherwise pool and flag lower confidence.
5. No statistical adjustment at this sample size.
6. **Leave-one-out:** a conclusion must survive dropping any single issue.
7. **Per-tool adoption:** adopt for a tool only after at least 2 treated issues on it, no guard failure and no worse than that tool's own baseline. Otherwise it stays off. Not proven is not the same as bad.

## 7. Reporting

Raw per-issue values always come first. Below 3 issues in a group, report raw values only; at 3 or 4, add the range; from 5, the median and band. Allowed confidence labels: **Directional** and **Clear**. Nothing is called proven.

## 8. Integrity

- **Pre-registration and amendments:** this file is fixed once merged. Each amendment is dated and carries its reason.
- **Exclusions** are listed in every measurement record with their reason (common support, epoch, quota failure).
- **Durable evidence:** `make clean-scratch` deletes `.scratch/`, so reviewer findings are posted to the issue before cleanup. Tool session logs and prompts are not archived.
- **Reproducibility:** each measurement record states this protocol's version and the metrics script's commit.
- **Agent visibility:** Engineers see only the `ponytail: on` rule. Hypotheses, metrics and targets stay out of the Engineer's read paths, so they cannot be optimised against. Agents can read the repo, so this reduces exposure and does not remove it. State that limit in the write-up.
- **Hold:** the human may say "hold" at any time and every phase stays where it is. It is recorded as "hold" with no reason and no date. No deadline appears in the repo.
- **Publish regardless of outcome.**

## 9. Documentation trail

| What | Where | Written by | When |
|---|---|---|---|
| Decision and rejected alternatives | `_docs/decisions/` | orchestrator, human approves | once, then per amendment |
| Method | this file | PM or orchestrator proposes | once |
| Provenance and pin | `_docs/records/` (source) | orchestrator | once; new record on a re-pin |
| Per issue: tool, model, arm | `Launch usage` line in the session summary | orchestrator | each launch |
| Per issue: qualitative notes | `### Ponytail` block under Reflection | reviewer, copied unchanged | each reviewed issue |
| Per issue: finding labels | "Decisions made by the human", one line each: `Finding <issue>-<n>: <label> <class>` | orchestrator, from the human | decision point |
| Per issue: reviewer findings | comment on the issue | orchestrator relays | before cleanup |
| Per sweep: figures and exclusions | `_docs/records/<timestamp>-measure-ponytail-<phase>.md` | sweep PM, from the script | each sweep |
| Per gate: outcome and reasons | `_docs/decisions/<timestamp>-ponytail-gate-<n>.md` | orchestrator, human decides | each gate |
| End: result | final measurement record, plus one headline line and a link in the README | owner | after Phase 3 |

Every artefact has `ponytail` in its file name, so a glob finds the whole trail. The human may label trial issues `trial:ponytail` for filtering on GitHub.

## 10. Write-up commitment

Outline: the question; the method as registered; what happened, with deviations and exclusions; results, raw first; limits; the decision; what we would change.

## Amendments

1. **2026-11-06, before any data.** The `trial:ponytail` label in section 9 must not be put on control issues. Labels are visible to the Engineer, so it would prime them and defeat the unprimed-control rule in section 3. Apply it only to plumbing issues and treated issues, or not at all. Nothing else changes.
2. **2026-11-11, after #8 and #51 were measured; applies from #9 on.** Section 3, Epoch: a change starts a new epoch if it alters what an existing command a role already runs does (Install, Test, Verify, Assert clean, the issue wrappers), or adds or changes a rule sentence a role reads, in any file. Adding a new target for a feature the same issue builds does not start a new epoch, and neither does a `KIT_VERSION` bump on its own. Test: "Would a control Engineer on an unrelated issue run or obey something different after this change?" Earlier moves stand as recorded. Reason: the section 3 file list counted every `AGENTS.md` edit as a move, which would split the control group on edits that change nothing a control Engineer runs or reads (for example the run and stop targets added by #10), while #46's Commands-only edit changed what `make verify` runs and did need to count. Nothing else changes.
3. **2026-11-12, after #12 closed; the trial is shelved.** It was considered and its plumbing built, but it was not fully implemented: no Phase 1 shadow review ran, so there is no result to report (inconclusive, not negative). Until it is resumed, ponytail is used in normal work: the Engineer loads the core skill by path, the Reviewer runs after the last QA PASS, and the human judges any benefit. While the trial is shelved, phases, epochs, arms, metrics and gates do not apply. This protocol stays as registered, so a resumed trial can start from it (steps in `_docs/planning/roadmap-2-ponytail-trial.md`). Note that the human's informal use primes the Engineer, so a resumed trial needs a new epoch. Reason: `_docs/decisions/2026-11-12T2300Z-ponytail-adopt.md`.
