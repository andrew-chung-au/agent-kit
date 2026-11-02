# Review: Agent kit evolution plan

**Status:** review of a proposal. Nothing here has been implemented.
**Date:** 2026-10-31
**Reviews:** `proposals/2026-10-31-agent-kit-evolution-plan.md` (called "the plan" below)
**Checked against:** `agent-kit/` at `fac2271`, and the `vuln-triage/agent-kit/` snapshot in this repo.

---

## 1. Verdict

The plan diagnoses the problem correctly: the vuln-triage kit advertises features it doesn't ship, permission auditing that relies on agents remembering doesn't work, and one process for every change is too slow. Its principles (observe, don't ask; one canonical source; process scales with risk; opt-in modules) are the right ones.

Where it falls short is in applying those principles to itself. In several places it repeats the mistakes it diagnoses:

- It **adds duplicate templates** (`issue.md` next to `task-template.md`, `log.md` next to `session-summary.md`) while making "one canonical source" a principle.
- It **ports machinery before the code that uses it** (`scan-issue-body.sh` and the "issue writes are allowed" rule in Phase 1, while the issue wrappers wait until Phase 5). That is the same "documented but not shipped" gap it criticises.
- It **brings in a dependency without saying so.** A TypeScript OpenCode plugin that `make test` syntax-checks needs `node`, `bun` or `tsc`.
- It **contradicts itself on log retention.** Logs are deleted at cleanup (§10), yet a report runs across many sessions (§4 B3).
- It **leaves the most important new control unowned.** Change classes decide whether QA runs, but the plan never says who sets the class. In a public repository with untrusted issues, that's a security question, not a convenience.

**Recommendation: approve the plan with the amendments below.** The biggest changes are:

1. Make a **"claims check"** (the docs and make targets the kit refers to must exist) the first deliverable. It enforces the plan's main lesson automatically.
2. **Group work by module, not by size,** so nothing ships before the code that uses it.
3. **Have the human set the change class,** with automatic escalation based on the paths a change touches.
4. Ship **three tiers instead of five classes,** and **defer the Architect role.**
5. **Cut Workstream D down** to an index and a check. It is mostly a VulnTriage problem, not a kit problem.
6. **Slim `AGENTS.md` itself** (3.13). It's the most expensive doc in the kit and the plan doesn't touch it. Keep the judgment rules inline, cover hook-enforced rules in one line, and move step-specific rules behind a trigger-based "Read when" index.

---

## 2. What the plan gets right (keep as is)

- **A2/B1:** dropping agent-recorded approvals as the source of truth. The vuln-triage `permission-sweep.md` admits as much itself: "Summaries record requests, not outcomes."
- **A5:** the exclusions list, especially refusing `git add *` / `git commit *` allow rules in OpenCode. OpenCode has no `PreToolUse`-style guard, so its permission patterns are the only barrier.
- **A4:** the cloud push guard conditions, and the behaviour-test matrix for `guard_git.py`.
- **§2.5:** replacing `jq` with `python3 -m json.tool`. This repo's `Makefile` `test` target already does that, so the vuln-triage `check-scripts` target adds nothing new.
- **F1/F2:** treating Ponytail as a pinned, trialled, optional third-party skill.
- **§10 non-goals:** especially "Replacing QA with a reviewer or a skill."

---

## 3. Major issues and amendments

Each item gives the problem, why it matters, the trade-off and the recommended amendment.

### 3.1 Prevent unshipped claims mechanically, not by intention

**Problem.** The plan's main lesson (§1) is "do not document features that do not exist". Its answer is reviewer discipline plus a `blueprints.md` row per module. That is exactly what failed in vuln-triage: the README, `pm.md`, `AGENTS.md.template` and `permission-sweep.md` all name `make issue-create`, `make permission-report` and `_docs/permission-sweeps.md`, and nothing caught it.

**Why it matters.** Agents treat the kit's docs as instructions. When a doc names a target that doesn't exist, the agent improvises, which is the "invents a template" behaviour §7 complains about.

**Trade-off.** A check costs about 80 lines of stdlib Python and some false positives (for example placeholders like `make <name>-start`). The alternative is the failure we just had.

**Amendment.** Add a **claims check** to Phase 1, run by `make test`:

- Every `make <target>` mentioned in `agent-kit/**/*.md` exists in `templates/Makefile.mk` or in the Makefile fragment of a module that the same doc names. Placeholders in `<...>` are skipped.
- Every kit-relative path in backticks (`templates/...`, `procedures/...`, `scripts/...`) exists.
- Every file under `agent-kit/` that a project installs has a `blueprints.md` row.

This is the useful core of D4's `docs-check`, pointed at the kit itself. It should come before any other workstream, because every later phase adds docs.

### 3.2 Group work by module, not by size

**Problem.** Phase 1 ports `scan-issue-body.sh` and adopts "routine issue writes are allowed" (A1). The thing that makes both meaningful, the `issue-create`/`issue-comment` wrappers, is put in an optional module in Phase 5 (A3). A1's own Notes column says the scanner is "only useful once an issue wrapper calls it".

**Why it matters.** Between Phase 1 and Phase 5 the kit would ship a script nothing calls, plus a permission rule that points at targets that don't exist. That is the vuln-triage README problem again.

**Trade-off.** Grouping by module makes Phase 1 smaller and the GitHub module bigger. That's fine: the module is opt-in, so its size doesn't burden core users.

**Amendment.** Move `scan-issue-body.sh`, the issue-write rule, `issue-create`/`issue-comment`/`issue-dump` and (later) `pr-create` into one **GitHub module**, delivered as a single phase with its tests. In core, keep issue edits and closes on `ask`, as today.

### 3.3 Permission logging: dependency, retention and the Claude Code gap

**3.3a Hidden dependency.** B6 asks `make test` to syntax-check `.opencode/plugins/permission-log.ts`. With bash, git, make, coreutils and the Python standard library, that isn't possible. Checking TypeScript needs `node`/`bun`/`tsc`, and the kit's rules say "Propose any new dependency at the decision point; never install one."

- *Option 1 (recommended):* keep the plugin very small (event in, one JSON line out, no logic). Put all redaction, grouping and reporting in a stdlib Python report script with fixture-based tests. Test the plugin end to end once per OpenCode version bump, by hand, using a checklist in the module's README. `make test` then only checks that the plugin file exists and is the expected size.
- *Option 2:* skip the plugin check when `node` is missing, and run it in CI where node is available. The cost is a test that only runs in CI.
- *Option 3:* make Node a dev dependency of the kit repo only, not of projects. That's a real decision for the human to make; the plan shouldn't make it in passing.

**3.3b Retention contradiction.** §10 says to "delete at cleanup", and `process.md` step 8 runs `make clean-scratch` at the end of every issue. B3, though, wants `make permission-report SINCE=<commit>` across sessions. Something has to give:

- *Recommended:* logs go to a git-ignored folder **outside** `.scratch/` (for example `.agent-kit/logs/permissions/`), so `clean-scratch` doesn't touch them. Add a `make permission-logs-prune DAYS=30` target, and record each sweep's cut-off date. Add the folder to the `.gitignore` blueprint row and to `assert-clean`'s expectations.
- *Trade-off:* that keeps sensitive-ish data on disk longer. Redaction plus the size cap plus pruning make the risk acceptable. If it isn't, the alternative is to reduce each issue's log to counts at cleanup (pattern → ask/allow/deny counts, with no command text) and delete the raw lines.

**3.3c `SINCE=<commit>` doesn't fit time-stamped logs.** The JSONL records carry timestamps and session IDs, not commits. Use `SINCE=<YYYY-MM-DD>` or `SINCE=<ISO time>`. If a commit has to be accepted, convert it with `git log -1 --format=%cI <commit>` inside the script, and keep the existing hex validation.

**3.3d Redaction patterns would exist three times.** "Reuse the patterns from `scan-issue-body.sh`" in a TypeScript plugin and a Python report means three copies of the same regexes. Put them in one plain data file (`agent-kit/scripts/secret-patterns.txt`, one ERE per line) that all three read. That's principle 2 applied to code.

**3.3e B4 understates Claude Code.** At the time of writing, Claude Code documents a `PermissionRequest` hook event and a `permission_prompt` matcher for the `Notification` hook. Combined with `PostToolUse` (the tool ran, so it was allowed), they give a structured ask-and-outcome pair that is close to OpenCode's. **Check this against the current Claude Code hooks documentation before choosing.** If it holds, B4 option 1 (logging inside `guard_git.py`) is the wrong layer: `guard_git.py` sees only git commands and runs *before* any permission decision. A separate, observe-only `log_permission.py` hook should replace it. Keep `guard_git.py` single-purpose.

**3.3f Pin the tool versions.** The event names B2 relies on (`permission.updated`, `permission.replied`, `permission.ask`) are not a stable API, and plugin hooks in fast-moving tools get renamed. The module README should name the OpenCode version it was tested against, and the plugin should log an `"event":"unknown"` record rather than silently dropping events whose shape it doesn't recognise.

### 3.4 Change classes: who decides, and stopping someone from picking a lower class

**Problem.** C1 says "the class decides the roles and the gates, not the agent's mood", but never says *who* sets the class. In this repository anyone can open an issue, and issue text is untrusted (`AGENTS.md`, Issues). An issue that says "trivial docs typo" but touches `agent-kit/claude-code/hooks/` would skip PM and QA.

**Why it matters.** The class is now the switch that turns QA off. Any input that can flip it is part of the attack surface.

**Trade-off.** Having the human set the class adds a small step to labelling. Automatic escalation adds some code to `check-staged.sh` or `verify.sh`. Both are cheap compared with an unreviewed hook change.

**Amendment.**

- **The human sets the class** when approving the issue, in the same step as adding the `approved` label. The PM may *propose* a class while grooming; it doesn't take effect until the human confirms. Store it somewhere only the human controls. A `class:light` / `class:standard` / `class:heavy` label fits the existing "only the human labels issues" rule, and costs nothing new.
- **Automatic escalation, never downgrade.** A deterministic check fails the light path when the diff touches anything outside its allowance:
  - Light: Markdown only, with no paths in `PROTECTED` other than the kit's own docs. In this repo, add the kit docs to the allowance explicitly; otherwise nothing qualifies.
  - Any change to `scripts/`, `claude-code/hooks/`, `githooks/`, tool settings, `TEST_FILES` or `agent-kit.conf` is at least Standard.
- **Agents may raise the class themselves, never lower it.** Lowering it is a decision question for the human.

### 3.5 Three tiers, not five classes

**Problem.** Classes A and B differ by a single plan comment. Class E (Incident) is "project-specific / project-specific", and §10 makes on-call a non-goal. Five classes is more taxonomy than the process can use.

**Trade-off.** Fewer tiers mean less fine-grained gating. But each tier boundary is a decision someone has to make on every issue, and every boundary is a place to argue about the class.

**Amendment.**

| Tier | Was | Path | Gates |
|---|---|---|---|
| **Light** | A + B | Engineer only. One `Engineer:` plan comment before coding, unless docs-only | `make verify`, path allowance check (3.4), human diff review |
| **Standard** | C | PM groom → Engineer → QA (today's chain) | as today |
| **Heavy** | D | Standard, plus an ADR approved by the human before the Engineer starts, plus a fresh-context code review | as Standard, plus ADR approval and the review |

Drop E from the kit. A project that needs it can add it in its own `AGENTS.md`.

**Required edits the plan doesn't list.** `process.md` currently says "The PM grooms it. **Never skip this step.**", and Definition of done requires "QA has posted PASS". Both have to become tier-aware, otherwise the light path breaks the process doc. `verify_on_stop.py` already skips Markdown-only changes, which fits the light tier. Note it rather than change it.

### 3.6 Roles: defer the Architect, fold the Reviewer in

**Problem.** C2 adds two roles while saying "keep the core team small" and "add roles only where a distinct context or authority is needed".

- **Architect.** For a heavy change the needed *authority* belongs to the human (spec and ADR approval). The *context* is the same as the PM's, who already reads the spec. A new role means a new team file, two new agent definitions, setup steps and blueprint rows. That's about 150 lines of docs for a tier that may come up a few times a year.
- **Reviewer.** QA already runs in a fresh context and is forbidden from changing anything. The difference is the remit: QA checks acceptance criteria, a reviewer checks code quality, security and scope.

**Trade-off.** A separate Reviewer gives an independent second opinion. Folding it into QA means one fewer launch and less orchestration. For the Heavy tier, independence is worth the extra launch.

**Amendment.**

- **Architect: defer.** Ship `templates/adr.md` only. In the Heavy tier, the PM drafts the ADR from the template and the human approves it. Add the Architect role when the metrics show ADRs being drafted poorly, not before.
- **Reviewer: ship as an optional checklist section in `qa-engineer.md`** ("Code review: bugs, security, tests weakened, scope"). QA fills it in for Standard work. For Heavy work, run it as a **second QA launch** with only that remit, so it gets a fresh context without needing a new role file.

### 3.7 Workstream D is mostly a VulnTriage problem

**Problem.** `_docs/` sprawl, the shared dated log file and duplicate runbooks are things that happened in VulnTriage. This repo has no `_docs/` at all. The kit's own convention already gives one file per session (`_session-summaries/issue-<NNN>-<short-name>.md`), so the "shared log file" problem D2 solves doesn't exist in the kit. D2's `_docs/logs/` would also be a **second** session-notes folder next to `_session-summaries/`.

Five front-matter fields on every doc cost tokens on every read and need upkeep: `last-reviewed` goes stale by design, and `owner` duplicates `PROTECTED`. It also scatters metadata across files, against principle 2.

**Trade-off.** Front matter keeps the metadata next to the content. An index keeps it in one place that the check can validate cheaply.

**Amendment.**

- **Kit ships:** `templates/docs-index.md` (one table: path, what it's canonical for, status), and the D4 checks pointed at the index rather than at front matter: every doc listed, every listed path exists, no duplicate "canonical for", no broken relative links, size warning.
- **No front matter requirement.** The index is the single source of doc metadata.
- **Keep `_session-summaries/`.** Don't introduce `_docs/logs/`. If role-level notes are needed, extend the naming convention instead (`issue-<NNN>-<short-name>-qa.md`).
- **The VulnTriage migration (D5) is VulnTriage work.** Track it in that project, not as a phase of the kit plan. Use it as the pilot that proves the index and the check.
- **Small fix:** `make docs-check --fix` isn't valid make syntax. Use `make docs-check FIX=1`.

### 3.8 Templates: the plan adds duplicates

**Problem.** E1 adds `issue.md` (the kit already has `task-template.md`) and `log.md` (the kit already has `templates/session-summary.md`). It also adds `github/ISSUE_TEMPLATE/task.yml`, a third version of the issue shape.

**Amendment.**

- Keep `task-template.md` as the single shape of a **groomed** issue, and add a `Tier` line to it.
- A GitHub issue form, if shipped, is an **intake** form for outside reporters (problem, expected behaviour, evidence). It's deliberately different from the groomed shape, and it lives in the GitHub module.
- No `log.md`: use `session-summary.md`.
- New and justified: `adr.md`, `pr.md` (PR profile only), `docs-index.md`.
- E2 (`make pr-create`, `make review-comment`) depends on pushing and write tokens. It belongs in the GitHub/PR module, not in the templates workstream.
- E4's "an agent finds `templates/issue.md` without searching" can't be tested. Replace it with: the claims check (3.1) confirms that every template path named in `AGENTS.md.template`, `process.md` and `team/*.md` exists.

### 3.9 `.env` edit deny: watch the pattern

**Problem.** A1 suggests `Edit(.env*)`. In Claude Code a deny rule always wins, so `.env*` also blocks `.env.example`, which the kit explicitly allows (`ALLOWED` in `agent-kit.conf`, and the `.gitignore` exception).

**Amendment.** Mirror the existing read deny list exactly: `Edit(.env)`, `Edit(.env.local)`, `Edit(.env.*.local)`, plus any project-specific names. In OpenCode, add `"*.env": "deny"`, `"*.env.*": "deny"` and `"*.env.example": "allow"` under `edit`, matching its `read` block. Add a test case for each tool showing `.env.example` stays editable.

### 3.10 PR profile: closing issues, and the pending push check

- `Closes #N` closes the issue on merge, so the human's merge closes it, not the orchestrator. `process.md` step 9 ("Only the orchestrator closes issues") needs a PR-profile exception. Otherwise the two rules conflict.
- `proposals/pre-push-v3` and `proposals/helpers.sh` are already in this repo and touch the same area (push checks, cloud and PR flows). The plan doesn't mention them. Say whether the PR profile depends on push check v3, so the two don't change the same area separately. Agents never edit `environments/local-sandbox/pre-push` (`AGENTS.md`, Project gotchas), so any dependency becomes a human-applied step.

### 3.11 Metrics need a source

C5 lists three metrics without saying where the data comes from. Wall-clock time can come from issue timestamps (`gh issue view --json createdAt,closedAt`). Approval prompts per issue come from the permission log, which is a good reason to finish Workstream B first. **Tokens/cost: "Ponytail can report this" is unverified.** Ponytail is described as a code-minimalism skill, and nothing in the plan shows it reports usage. Until a source is confirmed, drop the token metric, or name the tool-native usage view the human reads by hand.

### 3.12 Doc budget

The kit's Markdown is about 1,000 lines today (kit root, `team/`, `procedures/`, tool `START.md` files and templates). As written, the plan adds two role files with agent definitions for two tools, eight templates, a docs index, front matter, a triage table, a PR profile and four module READMEs. That's plausibly +40–60%, in a plan whose principle 2 is about token cost.

**Amendment.** Set two budgets, because they measure different costs:

- **Always-loaded context** (`AGENTS.md` plus whatever each role launch reads first): **should shrink.** The target is −40% in words; see 3.13. This is what every session and every subagent pays.
- **Total core Markdown: net growth ≤ 15% across all phases.** Modules are excluded, because they're opt-in. Moving text from `AGENTS.md` into linked docs counts as zero.

Measure both with `wc -w` in each phase's verification, and report them at the decision point.

### 3.13 The plan doesn't address the size of `AGENTS.md`

**Problem.** The plan's token argument (principle 2) is aimed at `_docs/` sprawl. It never looks at the file that costs the most: `AGENTS.md`, which is read at the start of every session and every role launch.

- This repo's `AGENTS.md` is about 1,550 words. The template is about 1,100 words, before a project adds its own settings and gotchas.
- `Conventions` has 27 rule bullets, all at the same weight. The rule about untrusted issue text sits at the same level as "give every command a description".
- Each issue launches the orchestrator, PM, Engineer and QA, and each reads `AGENTS.md` before its role file. So the file is paid for at least four times per issue, more with FAIL loops.
- **Possible double load (check this).** `CLAUDE.md.template` is `@AGENTS.md`, which Claude Code inlines eagerly. The role definitions then say "Read `AGENTS.md`, then …" again. If Claude Code subagents receive `CLAUDE.md`, as I believe they do, every Claude Code role reads `AGENTS.md` twice.

Current guidance from tool makers, Anthropic's Claude Code docs included, is to keep the always-loaded file short and specific: cut any line whose removal wouldn't cause a mistake, and load detail on demand. The cost of a long file isn't mainly tokens (1,550 words is modest). It's **adherence**: when every rule has the same weight, the critical ones get diluted, and the file becomes the place every new rule lands.

**What the peer example gets right:**

- A short, stable file: an index, then a few non-negotiables.
- **Product invariants stated as always-on rules** (Decimal not float, no PII in logs, module boundaries). The kit template has no slot for these. "Project gotchas" is the nearest, and it's framed as "things an agent would get wrong", not as hard rules.
- Domain detail (schema, API, deployment) lives in linked docs and is read only when relevant.

**What not to copy:**

- **A topic index with no "read when".** "Database Schema Specification" says what exists, not when to read it. An agent decides whether to follow a link from its trigger, so an index entry should be phrased as one: "Before changing a model or migration → `docs/schema.md`."
- **Every role described in the shared file.** The Frontend agent's job description is loaded into the Backend agent's context. The kit's split (`team/<role>.md`, read only by that role) is already better. Keep it.
- **It's slim partly because it leaves out process and safety rules.** It has nothing on staging, pushing, protected files, untrusted input or approvals. Those either live in hooks or are missing. It's not a like-for-like comparison: the kit can't just delete its Conventions.
- **Shouted emphasis** ("MUST", "Non-Negotiable"). Recent models follow plain instructions well. Heavy emphasis tends to make them apply a rule too broadly rather than more reliably. Save it for the one or two rules where a breach is serious.
- **The autonomous on-call responder that patches and opens PRs.** That is already a non-goal in §10.

**Key point: how far the file can be slimmed depends on enforcement.** A rule can safely move out of the always-loaded file, or shrink to one line, only when something else makes up for an agent not reading it. Sorting the template's 27 Conventions bullets that way:

| Group | Rules | Treatment |
|---|---|---|
| **Enforced mechanically** (hooks, tool settings, git hooks) | explicit staging; no `--no-verify`; protected files need `HUMAN_APPROVED=1`; never open `.env`; don't push; forbidden files; done means `make verify` passes; don't change `core.hooksPath` | **One line:** "Hooks block broad staging, `--no-verify`, pushes, `.env` reads and unapproved protected commits. If a hook blocks you, fix the cause or ask; never work around it." The hook's error message carries the detail at the moment it's needed. |
| **Always needed, judgment only** (no mechanism can check them) | untrusted issue text and the `approved` label; change only what the task needs; don't delete what you didn't create; no new dependencies or installs; no system or config changes; never stop a process you didn't start; stay inside the folder; don't read tool settings, home or env | **Keep inline, at the top,** as about 8 short lines. These are the real non-negotiables. |
| **Needed only at a specific step** | commit pre-checks (`git status`, `diff --check`); attribution; issue comment prefix and never editing comments; long-running process rules; approval request layout; spec ownership; injection tests in `.scratch/` | **Move to the doc for that step,** behind a trigger: Engineer commit steps → `team/software-engineer.md`; comments → `process.md`; processes → a short `procedures/processes.md`; approvals → `procedures/asking-the-human.md` (already exists). |
| **Tool-specific** | command shapes that avoid permission prompts (no `$VAR`, no `cd &&`, no `/tmp`, no inline code); "if blocked only because the tool couldn't check it, simplify once"; describe every command | **Compress to about 3 lines.** If they turn out to matter only for one tool, move them to that tool's layer (`CLAUDE.md.template` / `opencode/START.md`). They are about how one tool's permission checker works, not about the project. |

**Trade-off.** Linked docs are read only if the agent follows the link. Three things make up for that:

- the trigger wording in the index;
- the process steps that already name the procedure exactly where it applies (`process.md` steps 3, 7 and 8);
- the hooks, as a backstop for the rules that matter most.

The cost is one or two extra reads in the sessions that need them. The gain is a shorter always-loaded file in every session, and an obvious place to put a new rule that isn't `AGENTS.md`. The remaining risk is step-specific rules being skipped. The Phase 2 permission logs and QA's checks will show that, and any rule that keeps getting missed moves back inline, or gets a hook.

**Amendment: target shape of `AGENTS.md.template`** (about 60 short lines, under 800 words before project additions):

```
# AGENTS.md
<one paragraph: what this project is>

## Commands            (unchanged; every session needs them)
## Project settings    (unchanged)
## Non-negotiables     (~8 judgment rules from the table, plus the project's product
                        invariants, e.g. "never float for money", "no PII in logs")
## Enforced by hooks   (one line, see table)
## Read when           (trigger → doc, one line each)
- Working a GitHub issue → process.md, then your team/<role>.md
- Before asking the human anything → procedures/asking-the-human.md
- Before committing → team/software-engineer.md#commits
- Before starting a server or watcher → procedures/processes.md
- Before changing <area> → <project doc>          (project adds its own)
- Looking for any other project doc → _docs/README.md   (the 3.7 index; don't duplicate it here)
## Project gotchas
```

**Related changes:**

- **One index, not two.** The "Read when" list covers the kit and names the project's `_docs/README.md` (3.7) once. Project docs are listed there, not in `AGENTS.md`.
- **Fix the double load** if it's confirmed. Either drop "Read `AGENTS.md`" from the Claude Code role definitions (keep it for OpenCode and in the generic launch message, if OpenCode subagents don't get it automatically), or drop `@AGENTS.md` from `CLAUDE.md` in favour of a plain pointer. Check each tool's behaviour before choosing.
- **The claims check (3.1) must cover the "Read when" links,** including anchors like `#commits`. Linked docs only work if the links don't break, which is why this comes after Phase 1.
- **Tool-native on-demand loading** (Claude Code skills or path-scoped rules, OpenCode skills) is an option *later*, as thin wrappers that point at the canonical procedure docs and never copy them. Plain links are tool-agnostic and enough for now. Skills are worth a trial only if the logs show procedures being skipped.
- **Projects already using the kit** need an upgrade note. Their `AGENTS.md` is protected and has local edits, so the change is a proposed diff that the human approves, not a file replacement.

---

## 4. Smaller amendments, by section

| Plan § | Amendment | Reason |
|---|---|---|
| §1 | Note that the vuln-triage *project* Makefile isn't in this repo, so the claims about it can't be checked here | Accuracy; the reviewer could check only `vuln-triage/agent-kit/` |
| A1 read/search guidance | Already in this repo's `AGENTS.md` Conventions; port only the wording that's missing from `AGENTS.md.template` | Avoid duplicating text that already exists |
| A1 `gh run view` | Allow `gh run view` without `--log`; keep `--log` on ask or behind a `make` target that truncates | Logs can be large and can contain secrets |
| A1 protected-change record | Define it as one line in the commit message trailer (`Approved-by: human, <date>, <what>`), not as a separate record | The commit is already the audit trail; avoids a new doc |
| A4 `cloud_session_start.sh` | **Drop it** rather than register it | It only prints where the session runs; every hook is a moving part with little value here |
| A4 tests | Python `unittest` (stdlib) under `tests/`; `make test` runs `python3 -m unittest discover tests` | First real tests in the repo; `TEST_FILES` already matches `tests/*`, so the weakened-test check covers them automatically |
| C3 | "Time-boxed PM groom": say what happens when the time box runs out (return to the human with open questions) | A time box with no rule for running out is not a rule |
| §9 Phase 1 | Remove "correct the false claims in the vuln-triage README" | Different project; non-goal §10 already says so |
| §9 every phase | Add "propose a version bump and changelog lines" | `AGENTS.md` Project gotchas require it for every kit change |
| §9 every phase | Add "upgrade note for existing projects" | VulnTriage and others need to know which settings, files and rules change |
| §11 Q6 | Answer it in the plan: one `approved` issue **per phase**, each with testable acceptance criteria | This repo works only on approved issues, and a single mega-issue can't get a meaningful QA PASS |

---

## 5. Revised phase plan

Each phase is one GitHub issue, approved by the human, with a version bump.

| Phase | Contents | Tier | Validation |
|---|---|---|---|
| **0. Decisions** | Answer §6 below | – | – |
| **1. Guardrails** | Claims check (3.1); `.env` edit deny with correct patterns (3.9); missing read-only allows; `unittest` harness and `guard_git.py` behaviour tests; doc budget baseline | Standard | `make verify`; the claims check passes on today's kit, or its first failures are fixed in the same issue |
| **1b. Slim `AGENTS.md`** | Restructure `AGENTS.md.template` to the 3.13 shape; move step-specific rules into role and procedure docs behind triggers; product-invariants slot; fix the double load if confirmed; apply the same restructure to this repo's `AGENTS.md` (protected, so a human-approved diff) | Standard | Claims check passes on every "Read when" link; always-loaded words down ≥ 40%; every rule removed from `AGENTS.md` is either enforced or reachable from a trigger (QA checks the mapping table) |
| **2. Permission logging** | Observe-only OpenCode plugin (minimal); Claude Code `PermissionRequest`/`Notification` logger if the docs confirm the events (3.3e); one shared secret-patterns file; stdlib report with fixtures; retention and prune target | Heavy (new hooks run live from the working tree) | Fixture tests; one real ask/allow/deny per tool; log is git-ignored; `clean-scratch` leaves it in place |
| **3. Tiers** | Three tiers; human-set tier label; path-based escalation check; tier-aware edits to `process.md` and Definition of done; code-review checklist in `qa-engineer.md`; `adr.md` | Heavy (changes the process itself) | Dry-run one Light and one Standard issue; compare prompts (from Phase 2 logs) and wall-clock time |
| **4. GitHub module** | `issue-*` wrappers + `scan-issue-body.sh` + issue-write rule + intake form + reject-case tests (3.2) | Standard | Reject cases from E4; blueprint row; claims check passes |
| **5. Docs index** | `docs-index.md` template + index-based `docs-check` (3.7) | Light/Standard | Pilot in VulnTriage, tracked there |
| **6. Optional modules** | Cloud session (without the start hook); PR profile + `pr.md` + `pr-create`, reconciled with push check v3; Ponytail trial in VulnTriage | Standard each | Each module: README with limits, blueprint row, test |

Phases 2 and 3 are in that order on purpose: the permission log gives Phase 3's dry runs a real prompt count instead of a guess.

---

## 6. Decisions needed (with recommendations)

1. **Scope.** *Recommended:* approve Phases 1–3 now. Decide 4–6 after seeing Phase 3's dry-run numbers. *Alternative:* Phase 1 only. That's lower risk but leaves permission auditing broken.
2. **Permission auditing.** *Recommended:* adopt the observe-only design for both tools (subject to the Claude Code doc check in 3.3e), with logs kept outside `.scratch/` and pruned after 30 days. *Alternative:* keep only per-issue counts and delete the raw logs at cleanup. Safer, but you can't see which commands caused a pattern.
3. **TypeScript plugin dependency.** *Recommended:* Option 1 in 3.3a (minimal plugin, logic in Python, no Node in the kit). *Alternative:* Node as a dev dependency of this repo only.
4. **Tiers.** *Recommended:* three tiers, set by the human as a label, with escalation by path only. *Alternative:* the plan's five classes.
5. **Roles.** *Recommended:* no new roles now. ADR template plus a QA code-review checklist; a second QA launch for Heavy. *Alternative:* the plan's Architect and Reviewer.
6. **Docs.** *Recommended:* index-only metadata, keep `_session-summaries/`, VulnTriage migration tracked in VulnTriage. *Alternative:* front matter on every doc.
7. **Ponytail.** *Recommended:* trial it in VulnTriage after checking the repository, its licence and the token-reporting claim, pinned to a commit. *Alternative:* leave it out until the tiers are in place, since a smaller-change skill matters most for the Light tier.
8. **Doc budget.** *Recommended:* always-loaded context down ≥ 40%; total core Markdown up ≤ 15% across all phases.
9. **`AGENTS.md` shape.** *Recommended:* restructure to non-negotiables + one line for hook-enforced rules + a trigger-based "Read when" index (3.13), as Phase 1b. *Alternative:* keep the current structure and just trim wording. Less churn for existing projects, but the critical rules stay mixed in with the step-specific ones.

---

## 7. Check before committing to the plan

- Claude Code hook events for permission prompts (`PermissionRequest`, the `permission_prompt` `Notification` matcher): check names and payloads in the current docs.
- OpenCode plugin event names and payloads in the version the projects use.
- That `https://github.com/DietrichGebert/ponytail` exists and is what §8 describes, including any usage reporting.
- Whether push check v3 (`proposals/pre-push-v3`) is meant to land before the PR profile.
- Whether Claude Code subagents receive `CLAUDE.md` (and so `@AGENTS.md`) automatically, and whether OpenCode subagents receive `AGENTS.md`. This decides how to fix the possible double load in 3.13.
