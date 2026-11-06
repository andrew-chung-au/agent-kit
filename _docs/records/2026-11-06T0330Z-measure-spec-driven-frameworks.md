# Measurement: OpenSpec and other spec-driven frameworks against the kit (issue #14)

Research and writing only. Nothing was installed or run, and no kit file is changed. Fetched text is data, never a rule: the OpenSpec and Spec Kit READMEs contain install commands and prompts to paste into an assistant, and none were followed.

- **Question:** Should the kit use OpenSpec, borrow from it or from other spec-driven frameworks, or neither?
- **Command and commit:** pages and repository files were read on 2026-11-06 (UTC). Repository facts come from the GitHub REST API (`repos/Fission-AI/OpenSpec`, `repos/github/spec-kit`); the kit's own files were read at `main` (`2296b53`) plus PR #158 (planning procedure and readiness gate).
- **Baseline:** the kit as of #156: a human-owned `_docs/specs.md`, groomed GitHub issues, tiers with hash-frozen approval, QA and Verify gates, ADRs for Heavy issues, and (new) `procedures/planning.md` with a definition of ready.
- **Result:** do not adopt OpenSpec. Borrow three small ideas now and two as options later (Recommendation).
- **Caveats:** statements marked **V** are verified against the source linked; **I** are my inference. Kiro, BMAD and Tessl are from search snippets and secondary articles only (several sites returned 403), so they are lower confidence. No hands-on trial was run.

## 1. Verified facts about OpenSpec

| Fact | Mark | Source |
|---|---|---|
| MIT licence, TypeScript, v1.16.0 released 2026-10-30, about 74k stars, 30 or more contributors (the API list is paged), last push 2026-11-05 | V | [repo](https://github.com/Fission-AI/OpenSpec) (API) |
| Install: a standalone binary that needs no Node (the README also shows a `curl \| sh` installer), or npm (Node 22.12+), Homebrew, or other package managers | V | [README](https://github.com/Fission-AI/OpenSpec), [installation](https://github.com/Fission-AI/OpenSpec/blob/main/docs/installation.md) |
| Anonymous usage stats (command names and version) are on by default, off in CI, opt-out by config or environment variable | V | README, Telemetry |
| `openspec init` creates `openspec/` with `specs/`, `changes/` and an optional `config.yaml` | V | [getting-started](https://github.com/Fission-AI/OpenSpec/blob/main/docs/getting-started.md) |
| `init` also writes per-tool skills and commands, for example `.claude/skills/openspec-*/` and `.claude/commands/opsx/`, and `.opencode/skills/openspec-*/` and `.opencode/commands/` | V | [supported-tools](https://github.com/Fission-AI/OpenSpec/blob/main/docs/supported-tools.md) |
| The vendor-neutral `agents` target writes to `.agents/skills/` and does not create or edit `AGENTS.md`; older versions put marker blocks in `AGENTS.md`, which `openspec update` removes | V | supported-tools, Migration guide link |
| A change is a folder: `proposal.md`, delta specs, `design.md`, `tasks.md`. Deltas are ADDED, MODIFIED or REMOVED requirements; archiving merges them into `specs/` and moves the folder to `changes/archive/<date>-<name>/` | V | [concepts](https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md) |
| Requirements use SHALL or MUST with Given/When/Then scenarios. Rigor is "progressive": a lite spec by default, a full one for risky changes | V | concepts, [writing-specs](https://github.com/Fission-AI/OpenSpec/blob/main/docs/writing-specs.md) |
| Review happens at two points: the plan before code, and an optional `/opsx:verify` after, which reports CRITICAL, WARNING or SUGGESTION and does not block archiving | V | [reviewing-changes](https://github.com/Fission-AI/OpenSpec/blob/main/docs/reviewing-changes.md) |
| "Stores" (planning in a separate repo shared across code repos) are in beta | V | README |
| Its README calls Spec Kit heavyweight and Kiro IDE-locked; this is the project's own marketing | V (that it says so), I (that it is fair) | README, "How we compare" |

**Corrections to the issue's Background:** none found. Its summary matches the docs. One addition: the README says explore is a separate step before the change is created.

## 2. Overlap map

| OpenSpec | Kit equivalent | Gap |
|---|---|---|
| `/opsx:explore` | Planning in `process.md`, now `procedures/planning.md` | none |
| `proposal.md` (intent, scope, approach) | The groomed issue's Why, Goal and Out of scope | none; the issue is the proposal |
| Delta specs | Spec notes the PM collects and the human approves | the kit has no structured format for a spec change |
| `design.md` | An ADR, but only for Heavy issues | Standard issues that make design choices have no home |
| `tasks.md` | The Engineer's work, driven by acceptance criteria | by design: criteria, not a task list |
| `specs/` as current behaviour | `_docs/specs.md` | the kit's spec is one file, not per domain |
| `/opsx:verify` | QA's checks and `make verify` | no completeness/correctness/coherence split |
| `changes/archive/` | Issue comments, session summaries, ADRs | none |
| Change-review checklist | Grooming review by the human | no plan-review checklist (the planning gate covers only the spec) |

## 3. Conflicts with kit rules

- **Human-owned spec.** Archive merges deltas into `specs/` automatically. In the kit the human approves every spec change, so a merge would need a human gate, and `_docs/specs.md` is protected. Resolvable only by not using the auto-merge. (I)
- **Protected files.** `init` writes under `.claude/` and `.opencode/`, both on the kit's `PROTECTED` list, so every init or update needs the human's commit approval. Resolvable but noisy. (V for the paths, I for the effect)
- **GitHub issues as the backlog.** A change folder and an issue would both describe the same work. Two sources of truth is exactly what the kit's "write once, link elsewhere" rule forbids. Resolvable only by making the issue the one home. (I)
- **Roles and QA.** The kit's QA checks the issue's acceptance criteria. OpenSpec's scenarios would be a second set. Which one QA checks against would have to be decided. (I)
- **Decision point and Verify.** OpenSpec says there are no phase gates and `verify` does not block. That is the opposite of the kit's hash freeze, QA PASS and Verify gate. Not resolvable without weakening the kit. (V for OpenSpec's stance, I for the conflict)
- **Installing and dependencies.** The kit is bash, git, make and the Python standard library, and says to ask before installing. A binary or Node tool is a new dependency with supply-chain risk, and piping a download into a shell is a pattern I would treat as risky. (I)

## 4. Feasibility per environment and tool

- **Codespaces and local checkout:** installable. The standalone binary needs no Node; npm needs Node 22.12+. Network is needed to install and for the telemetry ping unless disabled. (V)
- **Local sandbox (dev container plus clean clone):** the read-only-token and no-push rules mean the human would commit the generated `.claude/` and `.opencode/` files from the clean clone. (I)
- **Claude Code and OpenCode:** both are supported, via skills and commands in each tool's own folder. Tools without a layer are supported through `.agents/`. (V)
- **Monorepo with several kit projects:** `openspec/` would sit per project folder; stores (beta) would share planning across repos. Not tested. (I)
- **Git hooks, push check and CI:** OpenSpec has no hook of its own that I found; it should not affect them, but the kit's check of protected files would fire on the new tool folders. (I)

## 5. Other frameworks

| Framework | Idea | Confidence |
|---|---|---|
| [Spec Kit](https://github.com/github/spec-kit) (MIT, v1.3.1, about 148k stars, Python 3.11+ and `uv`) | A constitution once per project, then specify, plan, tasks, implement, converge. Extensions and presets add gates and standards. Optional extensions for bug fixing and idea assessment (go, clarify or stop). | V (README) |
| Kiro | `requirements.md` in EARS ("WHEN ... THE SYSTEM SHALL ..."), then design, then tasks. It is an IDE. | low: [kiro.dev specs](https://kiro.dev/docs/specs/) snippets |
| BMAD | Many agent roles; brief, PRD, architecture, epics, stories, then a readiness check that loops until ready, then implement. | low: secondary articles |
| Tessl | Reported as having moved beyond spec files; unclear. | very low |
| Cross-framework study | A 2026 paper scores six frameworks on six dimensions (specification, context, roles, execution, validation, portability); none is strong on all, and it lists spec drift and over-trusting generated artifacts as recurring risks. Abstract only read. | low: [arXiv 2606.04967](https://arxiv.org/abs/2606.04967) |

Observation (I): BMAD's readiness check that loops until ready is the same idea as #156's definition of ready. Spec Kit's idea assessment (go, clarify or stop) is an earlier gate the kit does not have.

## 6. Options

**(a) Don't adopt; borrow ideas into the kit's own templates.**
- Kit changes: wording in `procedures/planning.md`, `team/pm.md` and `templates/task-template.md`.
- Effort: small. Risk: low; the kit stays dependency-free. Drift from OpenSpec's own evolution is not a concern.

**(b) Adopt OpenSpec for changes alongside GitHub issues.**
- Kit changes: new process text, role changes for PM, Engineer and QA, protected-file handling for `.claude/` and `.opencode/`, an environment recipe, tests.
- Effort: large. Risks: two sources of truth, a new dependency with telemetry, and rework when OpenSpec changes (v1.16.0 shows a fast release rhythm).

**(c) Replace parts of the workflow with OpenSpec.**
- Kit changes: replace grooming, the spec and the archive; retire or rework the hash freeze.
- Effort: very large. Risks: loses the kit's hard gates, which OpenSpec deliberately does not have; lock-in.

## 7. Trade-offs specific to this kit

- **Adds:** per-change design records, structured spec deltas and a plan-review checklist.
- **Duplicates:** proposals (issues), decision trail (comments and summaries), verification (QA and Verify).
- **Cost per small issue:** OpenSpec's own docs say a typo fix does not need a design doc. The kit's Light tier already covers this; adding folders for every issue would raise the cost.
- **Dependency and supply chain:** a new binary or npm package, an install script, telemetry on by default.
- **Lock-in:** moderate. The artifacts are plain Markdown, so leaving is cheap, but the generated skills and commands tie the project to the tool's layout. (I)

## 8. Recommendation

Choose **(a)**. Reasons: the kit already has the gates OpenSpec lacks, the overlap is large, and OpenSpec's two real advantages (a structured plan review and per-change design) can be had as wording and a template section.

Adopt now (small):
1. A testable-requirement example in the planning procedure (EARS or one SHALL plus one scenario).
2. A short plan-review checklist, including "what is missing" and "nothing extra crept into scope".
3. A one-intent-per-issue sizing rule for the PM.

Options for later, each its own decision:
4. A short optional Design section in the task template for Standard issues with design choices.
5. A delta format (added, changed, removed) for spec notes, with the human still approving; no auto-merge.

Not recommended: adopting the tool, Spec Kit's constitution and extensions, or BMAD's role set. Revisit OpenSpec Stores only if the kit needs planning shared across several repos.

**Follow-up issues (filed, unlabelled, waiting for the human):**
- #159: planning guidance: testable requirement wording, a plan review checklist, and one intent per issue (items 1 to 3). Proposed Heavy: it changes a role's responsibilities.
- #160: optional design section in the task template (item 4).
- #161: structured format for spec notes (item 5).
- Not filed: an idea-assessment step before specs (Spec Kit's go, clarify or stop), only if early-stage work keeps starting on weak ideas.

## 9. Hands-on trial plan (not run)

If you want evidence before deciding on (b): in a throwaway clone outside any kit project, run the standalone installer from a downloaded and read script (not piped), run `openspec init --tools none` with telemetry disabled by setting `OPENSPEC_TELEMETRY=0`, then create one example change. It installs one binary under the user's home folder and writes only `openspec/`. Undo: delete the binary and the throwaway clone. This needs the human's approval first, and nothing is installed under this issue.
