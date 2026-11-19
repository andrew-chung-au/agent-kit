# Kit 1.11: workflow review and proposals

Date: 2026-11-19 (third version, after the human's review). Status: proposal. Nothing here is filed or changed in the kit.

Contents: 1 the evidence · 2 design principles · 3 the workflow, end to end · 4 configuration guide · 5 formats (the schemas) · 6 roles and the delivery lead · 7 human tasks and status · 8 what is left out · 9 the 1.11 scope · 10 dmux · 11 trimming the project copies · 12 open questions · 13 sources

## 1. The evidence

Sources: the kit on `main`; `socboard/` (kit `1.10+socboard.2`: 18 kit files changed, six steering rulings in `.kiro/steering/`, 11 approved patches never landed in `_docs/planning/epoch-batch-1/`, 113 session summaries); `vuln-triage/` (`_docs/agent-team.md`, `cloud-sessions.md`); the October evolution plan; the human's reflections; dmux.

| Signal | Number | Meaning |
|---|---|---|
| socboard issues with at least one QA FAIL | 57 of 146 (39%) | QA rounds are the biggest cost |
| Worst cases | #139: eight Engineer rounds; #63: four QA runs | No stopping rule until the human wrote one |
| Human tasks | 45 in 12 days, mostly applies and deploys | Prerequisites found one by one |
| Session summaries | about 890 words each | A cost that issues and PRs now duplicate |
| Kit adjustments | 18 files, 6 steering files, 11 queued patches in two weeks | The kit was too rigid; adjusting it took real time |
| The human as relay | every message between Kiro sessions | No channel between sessions |

What socboard proved (the human's rulings): grooming 2 to 3 ahead with a `[groomed]` title prefix; every filed issue placed in the order; "wait only for a real dependency"; Medium-or-higher fails; "ship or fix?" after repeated rounds; a fix round re-checks only the changed lines; the step format for human instructions; lanes that own files; "gates on mechanics" (say the work is done; don't launch a round to satisfy a script); findings in a file per issue.

What didn't work: the Ponytail trial (its freeze on process changes made work serial); the Reviewer role (added and dropped within four days); gates that read comment prose (the close-floor decision took about 900 words to tell a reflection from a work comment); relaying between sessions by hand.

## 2. Design principles

1. **Adjustable without editing the kit.** Most of socboard's kit edits changed a value, not a rule. Values move into settings with defaults, and a project changes a value in one line without forking the kit's text.
2. **Grade once, route by rule.** Findings, decisions, tasks and human tasks each carry a few fixed fields. Standing rules act on those fields, so fewer things need the human, and the ones that do arrive with the facts first.
3. **Structured first, prose second.** Every message, comment and task starts with fixed fields (verdict, impact, cost, scope, recommendation), then the explanation. Scripts read the fields, never the prose.
4. **The trail never blocks the build.** Records, summaries and docs are written when the facts exist, and no core work waits for them unless an issue needs the document itself.
5. **The Engineer and QA work from one list.** Grooming writes the criteria and names the standards with the QA check in mind. Nothing is checked that wasn't asked for.
6. **Run where it's cheapest.** The sandbox first; CI or the human only for what the sandbox can't run. Planning suggests where, per issue, as a reminder. A plan never blocks work because events didn't follow it: a deviation is noted and the work goes on.
7. **The smallest process that works over its lifetime** (Ponytail applied to the process). Every new rule says what it replaces and what it costs. Cost counts the long run: a small step repeated on every issue, or a shortcut that comes back as a series of small fixes, can cost more than a larger one-off change. When the smallest option has a recurring cost, compare it with the one-off alternative and say which was chosen and why.
8. **One vocabulary.** The three grades never share a word, so "medium" can't mean two things (section 4.0).

## 3. The workflow, end to end

### 3.1 Consult (new stage, before planning)

Planning today starts from the human's brief and writes the spec. It lacks a stage where the agent acts as an adviser: it analyses, asks, challenges and recommends before anything is written down. The consult stage produces one file, `_docs/planning/consult.md`:

- **Questions:** what the brief leaves open, each with options and a recommendation.
- **Risks and challenges:** where the brief is costly, fragile or over-built, and a simpler way if there is one.
- **The environment map:** what the human has (the local sandbox and what it can run, CI, Kiro, cloud sessions, servers, accounts), and what each issue type will need. It recommends dev container upgrades where a tool is missing (for example Terraform or Docker), since running in the sandbox is faster than CI.
- **Prerequisites for the end state:** everything the finished project needs from the human, even for later phases (accounts, a dev and a production server, secrets, CI access, packages), ordered by when each blocks.
- **Recommended settings:** a profile and any changes (section 4) for this project and the usage plan the human has.

The human answers in one sitting; the answers feed the spec.

### 3.2 Plan

The spec and backlog as now (`procedures/planning.md`), plus per issue:

- **Grade:** `Effort: S|R|E` (how much work) and `Reasoning: B|N|D` (how hard the judgement is), in the vocabulary of 4.0. They are independent: an extended but basic task (a long mechanical rename) is `E`/`B`; a short but deep one (a permission check) is `S`/`D`. Effort decides whether to split the issue and how to fill lanes, and in planning it gives a rough timeline and resource plan: the sum of efforts per lane, which lanes need a deep-reasoning session, and where the usage will go. Reasoning tells the orchestrator which kind of subagent to launch: the project's role definitions can come in a variant per reasoning level (in Claude Code, a role file with a stronger model in its frontmatter), and the orchestrator picks the variant that matches. The model itself is set in the role definitions, not in the kit's settings. The human agrees the grade with the label; launching a weaker variant than agreed is a stop decision (3.6), a stronger one a note.
- **Debt:** any tech debt the issue knowingly creates or pays down, in one line (`Debt: adds a second copy of the parser; removed by #40`). Consult (3.1) names the long-term costs of the design; this line tracks them per issue.
- **Runs in:** `sandbox`, `ci`, `human` or `cloud`, from the environment map, as a reminder. `ci` is suggested only when the sandbox lacks a tool and no dev container upgrade is planned. If the work runs somewhere else, that's a note, not a stop.
- **Needs:** dependencies on a specific criterion, not on a whole issue: `Needs: #12/C3 (built)`, where the type is `info`, `decision`, `built` (on a branch) or `merged`. Documentation criteria are separate from build criteria, so a dependent issue can start once the build criterion it needs is done, while the docs are backfilled.
- **Standards:** the standards files that apply (3.4).

### 3.3 Groom and approve

- The PM grooms up to `GROOM_AHEAD` issues ahead and marks each with the `[groomed]` title prefix. The human labels them in one sitting.
- **Criteria are written as QA's checklist.** Each criterion has a `Check:` line saying how it will be verified (a command, a test name, a reading of a named file). The Engineer self-checks the same list. Disagreements between what the Engineer built and what QA expected become wording problems found at grooming, not FAILs found in QA.
- **Overrides:** an issue that needs different settings carries an `Overrides:` line in its body (for example `Overrides: QA_FAIL_AT=C, RECHECK=full`), covered by the approved hash. The human also adds an `overrides` label, so overrides are visible in the issue list; the orchestrator refuses an `Overrides:` line without the label. The `approved` label keeps its single meaning.

### 3.4 Build

- The Engineer builds to the criteria and the listed standards, runs the standards' check scripts and **Verify**, and fills the criteria checklist in its comment: `C1: done (test_x)`, `C2: done`, `C3: not checked (needs CI)`.
- A dependent issue reads that checklist: when `#12/C3` says `done` at a commit on a branch (for `built`) or on `main` (for `merged`), it can start.
- **Standards** are short files under `_docs/standards/` (for example `human-steps.md`), each with a script when the rule is mechanical. A standard added mid-project applies to issues groomed after it, plus one audit issue for the files already written.
- **Generated, not hand-formatted:** where a format is strict (human steps, findings, role returns), the Engineer writes data and a script renders and validates it (section 5). The format can't be wrong, so QA can't fail on it.

### 3.5 QA, fix and re-check

The loop:

```
QA (full)  ->  FAIL  ->  route each failing finding (4.4)
                         -> fix: Engineer fixes  ->  fix check  ->  QA re-check
                         -> ask: "ship or fix?" to the human
                         -> ship: logged, issue continues
```

- **Findings** carry three fields (section 5.2): **impact** (`L`, `M` or `C`) decides PASS or FAIL against `QA_FAIL_AT`; **effort** (`S`, `R` or `E`) and **scope** (`in` or `out`) only route. By default (`QA_SCOPE_STRICT=yes`), out-of-scope findings and breaches of a standard the issue doesn't list never fail. QA also marks a finding `related: F-12-1` when it has the same cause as an earlier one, or touches the same criterion.
- **Two loops, two limits.** The inner loop runs inside one round: the Engineer fixes, then a **fix check** runs. The fix check is small and bounded: it checks only that the fix clears the failed criterion and breaks nothing next to it (the fix's diff, the tests around it, the standards' scripts), on a basic-reasoning subagent. It is not a QA round. The inner loop stops when the fix check is clean, or after `FIX_CHECK_LOOPS` tries (default 2). The outer loop is QA rounds: each failed QA re-check adds a point to the finding (4.4), and the points decide whether the next step is another fix, asking the human, or shipping.
- **Patchwork guard:** when a finding or one related to it fails a second time, the Engineer stops patching and writes a short approach review in its comment before the next fix: the root cause, why the earlier fixes missed it, and whether the approach should change. If the answer is a different approach, that is a decision point (3.6), because it may change the issue's scope.
- **Step up the reasoning (`STEP_UP`, default `ask`):** at the same moment, the next fix can run on the next reasoning variant up (B to N, N to D), since a finding that has failed twice has shown it is harder than graded. If the issue is already at D, the guard's approach review is the step up. How it works depends on the tool, and needs checking per tool in issue 8 before it is automatic:
  - **Claude Code:** a role variant is a role file whose frontmatter names a stronger model, and the orchestrator can also choose the model for a single launch. It runs under the same login as the session, so on a subscription it uses the plan's usage (no API key), but a stronger model uses that usage faster, and not every plan offers every model.
  - **OpenCode:** no step up. The human runs free models there, so there is no stronger variant to move to.
  - **Kiro:** no step up. Choosing a named model instead of Kiro's automatic choice uses more credits, so the session stays on auto.
  - **The setting applies in Claude Code only:** `auto` switches without asking where the variant exists; `ask` (the default) puts the step up into the next message to the human as a note with a recommendation, so it can be approved while work continues; `off` never steps up. Where no stronger variant is defined, the step up is skipped and noted. In OpenCode and Kiro the setting is ignored, and the patchwork guard's approach review is the only step up.
- **QA re-check:** `RECHECK=changed` (the default) checks the failed criteria, every criterion whose files the fix touched, and the standards' scripts; **Verify** always runs in full, so the whole test suite still runs. It steps up to a full re-check on its own when the fix touched files outside the failed criteria, or when the patchwork guard has fired. `RECHECK=full` always re-runs everything. With the fix check now catching local breakage, `changed` plus these step-ups catches most of what a full re-check would, for less. The Heavy second launch is always full and runs once, on the first complete version.
- **Findings not fixed** (passed findings, out-of-scope ones and anything shipped) go one of two ways:
  - **An issue now** for `C` impact, and for anything whose fix is worth doing on its own (`FINDINGS_TO_ISSUE_AT`, default `C`). The PM drafts it unlabelled, as always.
  - **The findings log** for the rest: one entry in `_docs/records/findings/<issue>.json`, with a `group` naming its theme (socboard already does this, for example `checker-looser-than-intent`). The sweep reads the log and drafts one issue per group once the group reaches `FINDINGS_GROUP_AT` entries (default 5), so one fix covers several findings.
  - **Not losing track:** `make findings` lists open entries by group, with their age. An entry still open after `FINDINGS_KEEP_SWEEPS` sweeps (default 5) gets an explicit keep or drop from the human at the next decision point, so nothing sits forgotten.
  - Both have a place: one-off fixes worth doing go to issues straight away, and small related problems wait until a single fix can handle several of them. Sweeping is cheaper for small items, because one groomed issue and one QA cover several. The age rule removes the risk of losing them.
- **Debt is a finding category.** A shortcut the Engineer takes on purpose (Ponytail's `shortcut:` comment) is logged as a finding with `category: debt`, and so is debt QA notices. The sweep reports total debt by group, so it is weighed against new work rather than discovered later.

### 3.6 Decisions while work runs

- A **decision point** is one message to the human, which may hold several questions. Each point gets an id (`D-<issue>-<n>`), a weight (1 to 3 by blast radius: 1 for a choice inside one file, 2 for an interface or a doc structure others use, 3 for something many issues build on), and a recommendation per question.
- **Stop points** wait for the human: the spec, security limits, money, irreversible or outside-the-repo actions, a weaker subagent variant than the agreed reasoning level, a change of approach from the patchwork guard, shipping a failing finding.
- **Continue points:** the agent takes its recommended options, logs the point in `_docs/planning/decisions-pending.md` with the rollback, and keeps working. New work stops starting when open points reach `DECISION_BUDGET` (weighted).
- **Answering:** the human answers per point, not just yes or no: `D-12-1 approve` (all recommendations); `D-12-2 q2=B` (a different option for one question); `D-12-3 reject`. Each answer lowers the open weight. An amended or rejected point gives the owning Engineer a rework item on its branch, listed in the ledger.
- **The rollback is the branch:** nothing that depends on an open point is merged to `main` (on a branch project) or pushed (on a project that commits to `main`, like this one) until the point is closed. The human usually clears points at the PR review they already do.
- `make decisions` lists the open points with weight, age and what depends on each.

### 3.7 Merge and close

Merge, close, and on to the next issue. The session summary is replaced (section 7.2).

### 3.8 Learn

- **Reflections are written to files,** `_docs/records/reflections/<issue>-<role>.md`, never in an issue comment. They stay out of the comments that gates read: work comments, verdicts and reflections live in different places, linked by the issue number, so no gate has to tell them apart.
- **A sweep** (as now) reads the findings, reflections and ledger history, and proposes either a settings change (cheap) or a kit issue (if a rule is wrong).
- **A project's local deviation** goes upstream as one kit issue within a week, with its patch.

## 4. Configuration guide

This section is the draft of a new kit doc, `customizing.md`.

### 4.0 Vocabulary

Three grades, three levels each, and no word or letter shared between them:

| Grade | Low | Middle | High | Graded by | Used for |
|---|---|---|---|---|---|
| Reasoning | Basic (B) | Normal (N) | Deep (D) | PM, at grooming | Which subagent variant to launch |
| Effort | Short (S) | Regular (R) | Extended (E) | PM for issues, QA for findings | Splitting, lanes, fix routing (points 1, 2, 3) |
| Impact | Low (L) | Moderate (M) | Critical (C) | QA | PASS or FAIL |

Agents need more than the table: two runs grade alike only when each level has a test and an example. The kit's guide gives, per grade:

| Grade | Level | Test | Example |
|---|---|---|---|
| Reasoning | B | The answer follows from the issue text; no judgement between options | Rename a target everywhere; add an index row |
| | N | Choices between known options, inside one area | Add a make target with input checks; a doc section with a new rule |
| | D | Security, concurrency, interfaces others depend on, or rules that interact | A permission gate; a hook that parses commands; a change to the lifecycle |
| Effort | S | Under 10 minutes of agent work; one small change in one file or a few lines | A wording fix; a one-line test |
| | R | 10 to 30 minutes; a few files, a focused task with tests | A new script with its tests |
| | E | Over 30 minutes, or likely to span more than one session; consider splitting | Changes across the project; a procedure rewrite across the kit |
| Impact | L | Cosmetic: meaning and outcome stay correct, with no material inconvenience | A typo; an unclear but correct sentence |
| | M (Moderate) | Confusion, a workaround or a minor delay, but the correct outcome is still reachable | A wrong expected output; a misleading error message |
| | C | An incorrect outcome, a risk of data loss or to security, or an essential task that can't be completed | A check that accepts invalid input; a command that fails as written and blocks the procedure |

**Tie-break rule:** when unsure between two levels, take the higher one for Impact and Reasoning (the cost of under-grading is a missed defect or a weak model), and the lower for Effort (an underestimate is found out at the fix check, cheaply). Each grade comes with one line of reason, so a wrong grade can be challenged.

### 4.1 Levels

| Level | Where | Who changes it | Lasts |
|---|---|---|---|
| Kit default | Kit docs | Upstream | Until the kit changes |
| Profile | `PROFILE=` in `agent-kit.conf` | The human (protected file) | Until changed |
| Project setting | One line per setting in `agent-kit.conf` | The human | Until changed |
| Path rule | A path pattern in `agent-kit.conf`, as `LIGHT_ALLOWED` works now | The human | Until changed |
| Issue override | The `Overrides:` line plus the `overrides` label | PM proposes, human approves | That issue |
| Session ruling | The human, in a session, recorded in an `Orchestrator:` comment | The human | That issue; it becomes a setting only at a sweep |

Each level overrides the one above. **A profile never stops you customizing.** It is only a set of defaults for a few settings. Any setting you write yourself wins over the profile, whatever the profile is. So `PROFILE=fleet` plus `LANES=2` gives the fleet defaults with two lanes. Switching the profile later changes only the settings you haven't written. A profile saves writing several lines, and lets you switch the whole shape at once (a Kiro sprint, then back) without losing your own choices.

Most settings aren't in any profile at all: they have one default and are set on their own (4.2). Only the settings that really follow the usage plan (lanes, grooming ahead, the delivery lead, status frequency) are in profiles.

**Settings you change often,** such as the decision budget when you're about to be away, don't need a protected-file commit each time. Tell the session ("decision budget 8 until I'm back"). The orchestrator records it in an `Orchestrator:` comment, and it lasts for that issue, or until you change it. That's the session-ruling level.

**Bounds no level can cross:** QA can't be dropped from paths on the escalation list (security, CI, hooks, the kit); the human's label, protected-file approval and push stay; an agent can never lower a tier the human set.

### 4.2 Settings

**Profile settings** (the profile sets the default; writing the setting overrides it):

| Setting | `solo` | `team` | `fleet` | What it does |
|---|---|---|---|---|
| `GROOM_AHEAD` | 2 | 4 | 6 | Issues groomed ahead of the one in progress |
| `LANES` | 1 | 2 | 3 | Parallel lanes |
| `DELIVERY_LEAD` | off | off | on | The delivery-lead role (section 6) |
| `STATUS_EVERY` | milestone | milestone | 15m | How often a running role posts status (section 6) |

**Standalone settings** (one default, in no profile):

| Setting | Default | What it does |
|---|---|---|
| `DECISION_BUDGET` | 3 | Open Continue weight before new work stops; 0 means every decision point stops. Often changed by a session ruling, for example before you go away |
| `QA_FAIL_AT` | M | Lowest impact that fails |
| `QA_SCOPE_STRICT` | yes | QA fails only on criteria and listed standards |
| `RECHECK` | changed | `changed` (with its automatic step-ups) or `full` |
| `FIX_CHECK_LOOPS` | 2 | Inner loop: fix and fix check, within one round |
| `ASK_AT` | 4 | Outer loop: a failing finding with fewer points goes back to the Engineer; at this many, "ship or fix?" goes to the human |
| `SHIP_RULE` | none | When a failing finding may ship without asking (4.4) |
| `STEP_UP` | ask | Claude Code only: whether a finding's second failure moves the next fix to a stronger variant: `auto`, `ask` or `off` (3.5) |
| `FINDINGS_TO_ISSUE_AT` | C | Lowest impact that gets an issue straight away; the rest goes to the findings log |
| `FINDINGS_GROUP_AT` | 5 | Log entries in one group before the sweep drafts one issue for them |
| `FINDINGS_KEEP_SWEEPS` | 5 | Sweeps a log entry may stay open before the human is asked to keep or drop it |
| `HEAVY_SECOND_QA` | on | The independent second QA launch for Heavy |

`LIGHT_ALLOWED` stays as it is. The model for each reasoning level is not a setting: it is set in the project's role definitions (3.2).

`FIX_CHECK_LOOPS` and `ASK_AT` are not duplicates. They limit different loops: `FIX_CHECK_LOOPS` limits the cheap inner loop (fix, fix check) inside one round, and adds no points. `ASK_AT` acts on the outer loop of QA re-checks, where each failed re-check adds a point. A round looks like this: the Engineer fixes; the fix check runs, up to two times; QA re-checks; if the finding fails again it gains a point; below `ASK_AT` it goes back to the Engineer for another round, and at `ASK_AT` it goes to the human.

### 4.3 Profiles follow your usage, not the project's size

| Profile | Fits | Why |
|---|---|---|
| `solo` | OpenCode on a small quota; Claude Code within a five-hour window | Parallel work and a coordinating role would spend the usage the work needs |
| `team` | One long Claude Code session with subagents | Some parallel work; the main session coordinates |
| `fleet` | Kiro, or any large pooled budget used in one go | Many lanes; coordination pays for itself |

### 4.4 Routing a failing finding: points

Each failing finding has points: **effort** (S = 1, R = 2, E = 3) **plus 1 for each QA re-check that has already failed on it, or on a related finding**. Impact is not in the points: impact decides whether it fails at all; points decide what happens next.

- **Fix rule:** below `ASK_AT` (default 4), the Engineer fixes without asking.
- **Ask:** at `ASK_AT` or above, "ship or fix?" goes to the human with the finding's fields and a recommendation.
- **Ship rule:** a failing finding ships without asking only if `SHIP_RULE` matches. The default, `none`, means only the human ships a failing finding (socboard's ruling). An example a project might set: `SHIP_RULE=impact:M,effort:E,rounds:1`.

Every failing finding is in scope and at least Moderate (out-of-scope and Low findings never fail), so each is worth one fix attempt before the human is asked. With the defaults:

| Effort of the fix | Points at the first FAIL | Asked about | QA runs at most |
|---|---|---|---|
| E (3) | 3 | After one failed re-check | 2 |
| R (2) | 2 | After two failed re-checks | 3 |
| S (1) | 1 | After three failed re-checks | 4 |

The patchwork guard and the step up in reasoning (3.5) fire on a finding's second failure, so every finding gets an approach review, and where possible a stronger variant, before it reaches the human. `ASK_AT=3` asks one round sooner for each, and sends extended fixes to the human straight away.

Fix checks don't add points; only failed QA re-checks do.

### 4.5 When to add a setting

The kit should not make everything configurable at once. Each setting is one more thing to read, explain, test and keep working across upgrades. So the kit adds a setting only when there's evidence that projects need different values, for example when two projects have changed the same value in their copy of the kit, or a sweep shows a different value would have saved rounds. Until then the value stays fixed in the kit's text.

When a setting is added, its default is the value the kit used before. An existing project that upgrades then behaves exactly as it did, and changes only if it writes the setting. Projects opt in, and nobody is surprised by an upgrade.

## 5. Formats (the schemas)

Each format puts the facts first, in fixed fields, and the explanation after. A recommendation is required; "none" must say why.

**Why not pydantic:** the schemas are flat (a few `Key: value` fields and short lists), and a standard-library check of that size is a few dozen lines: a dataclass per format, plus a function that reports the missing or invalid fields. Pydantic would make every project that uses the kit install and pin a package, including projects in other languages and the host-side push check, which has only git, docker and coreutils. The kit's rule is no dependency without a decision, and pydantic's benefits (nested models, type coercion) aren't needed here. Revisit only if the formats become nested.

### 5.1 Role return (every role, to whoever launched it; ten lines at most)

```
Status: done | blocked | stopped-early
Issue: #12   Commit: 1a2b3c4   Verdict: FAIL
Findings: 2 fail (C/R/in, M/S/in), 1 log (L/S/out)
Decisions: D-12-1 (weight 2, continue)
Needs the human: none
Recommendation: fix both; F-12-2 is a one-line change
Detail: <link to the issue comment>
Checkpoint: .scratch/progress-12.md
```

### 5.2 Finding (inside a QA comment and in the findings file)

```
F-12-1  impact: C  effort: R  scope: in  criterion: C3  category: defect  group: restore-checks  related: none
Recommendation: fix
What: the restore step skips the checksum
How found: ran restore.sh against a truncated archive; exit 0
```

### 5.3 QA comment

The first line stays `QA: PASS` or `QA: FAIL` (gates read it). Then the summary line `Findings: <n fail> / <n log>`, then the findings in the 5.2 form, then the criteria checklist, then Verify, then detail.

### 5.4 Message to the human (orchestrator or delivery lead)

```
Needs you: 2 decision points (weight 3), 1 ship-or-fix
D-12-2  weight 2  q1: A or B?  Recommended: A, because ...
F-14-1  impact: M  effort: E  points: 4  Recommended: ship, because ...
Status: #12 in QA, #14 fixing, #15 waiting on D-12-2
```

### 5.5 Status comment (from a running role, for the delivery lead)

```
Status: #12 building | 3 of 5 criteria done | blocked: no | next: C4 | at: 1a2b3c4
```

One line, posted at each milestone (`STATUS_EVERY=milestone`) or on a timer in `fleet`. The delivery lead reads only these lines and the role returns, never the full output.

### 5.6 Human task header (section 7.1)

```
Blocks: #14, #15 | Priority: 1 | Kind: one-off | Time: 10 min | Status: open
```

The steps follow, each written as data (`command`, `expected`, `if_different`) and rendered by `make human-task-render`, so the step format can't be broken by hand.

## 6. Roles and the delivery lead

- **Roles:** PM, Engineer and QA as now. The Reviewer stays dropped. The **delivery lead** is new and optional (`DELIVERY_LEAD=on`, the `fleet` default).
- **Shape:** one session is the delivery lead and stays open. Worker sessions each run one lane through the normal lifecycle (Engineer, QA, decision point). The lead doesn't build, groom or test. It holds the board (lanes, order, grades, the decision ledger, human tasks), assigns the next issue to a free lane, sets the merge order, answers the human's "where are we?", and relays the facts in the 5.4 form.
- **Lanes:** the lead names lanes and owns their mapping to issues. Lane names appear only in status lines and the board, never in durable docs, commits or issue bodies. That ends the drift between Session A/B and lanes by area.
- **Keeping the lead's context small:** it reads only role returns (5.1) and status lines (5.5), not the work. A worker posts detail in its issue comment; the lead opens one only when a status line says blocked.
- **Responsiveness:** it depends on the channel the tool offers.
  - **Claude Code:** the lead launches workers as background subagents, each in its own worktree. It is notified the moment one finishes, can message one to steer it, and can stop one. This is the most responsive shape.
  - **Kiro and other cloud sessions:** GitHub comments are the only channel every session shares. The lead polls on a short interval (for example every five minutes, through the tool's own scheduling). Workers post `Status:` lines there, and the lead posts its orders as `Lead:` comments. That is slower than messages, but it removes the human as relay, and the comments are a record.
  - **A shared machine:** workers in worktrees of one clone can also write `.scratch/status/<lane>` files that the lead watches. That's faster than GitHub, but the files aren't a record.
- **Usage limits:** the agent can't see the usage percentage that the terminal shows; it isn't in the agent's context. Whether a tool exposes it to scripts (for example to a status line or a hook) is not verified; issue #191 investigates it, later. Until then there is a **soft stop on request:** the human says "wrap up" (or a status line reports that the limit is near), and every running role writes its checkpoint and stops at the next safe point. A relaunch starts from `.scratch/progress-<N>.md`, not from zero.

## 7. Human tasks and status

### 7.1 Human tasks

- Each task file starts with the 5.6 header: what it blocks, a priority, the kind (`one-off` or `recurring`, with `Recurs: after each dev container rebuild` or `Recurs: monthly`), a time estimate and a status.
- `make human-tasks` lists open tasks, blockers first, ordered by how close the work they unlock is, plus recurring tasks that are due (from their last-done date).
- **Done one-off tasks** move to `_docs/records/human-tasks/` with their result table filled, so `_human-tasks/` holds only what is still to do. Recurring tasks stay and record each run.
- **Fewer tasks:** a task goes to the human only for what the sandbox, CI and the agent can't do, and the file says why. Planning's prerequisites list (3.1) batches what can be done early.

### 7.2 Status instead of session summaries

The session summary began as the human's way to see what had been done and where things stood. Issues, PRs and CI now hold that. Replace it with:

- **`make status`:** reads GitHub and the repo, and prints open issues by state (grooming, approved, building, in QA, waiting), what merged in the last N days, open decision points, open human tasks, and failing CI. `make status DAYS=3` covers recent work.
- **The Close comment** keeps what only the session knows: the merge commit, the QA verdicts, the decisions and the findings ids.
- **Reflections** stay: each role that worked on the issue answers the reflection questions (what slowed it, what nearly went wrong, one proposed change) in its own file under `_docs/records/reflections/` (3.8). A role with nothing to report writes one line saying so, rather than a full block. The sweep reads them, as it reads the findings.

This drops the summary's narrative (about 890 words per issue), which duplicated the issue thread, and the conflicts between parallel sessions. What only the session knew is kept: the facts in the Close comment, and the lessons in the reflections.

### 7.3 Instructions the tools actually follow

The kit's rules are long docs, read when a "Read when" trigger fires, and they are not always followed. Kiro's `.kiro/steering/` files with `inclusion: always` are loaded into every session, which is why socboard's rulings stuck. Proposal: the kit ships one short core-rules file (at most about 500 words: the non-negotiables, the formats in section 5, the routing rules) installed where each tool always loads it: Kiro steering with `inclusion: always`, `AGENTS.md` for OpenCode, and Claude Code through `CLAUDE.md`. The long docs stay as references. Rules that apply to one area (the human-step standard, say) go in files that load only for those paths where the tool supports it (Kiro's file-match inclusion; nested `CLAUDE.md` files in Claude Code).

## 8. Deliberately left out

- No role that is always on: the delivery lead runs only in `fleet`.
- No homegrown multiplexer (section 10).
- No approval proxy yet: the decision budget covers most of its use. Trial it later for weight-1 points only, with a fixed context.
- No pre-registered process trials: use before-and-after comparisons.
- No new dependency: schemas use standard-library scripts.

## 9. The 1.11 scope

Drafts are in `_docs/planning/kit-1.11/issues/` (index: `00-index.md`). Each split is filed as its own issue.

| Order | Issue | Tier | Needs |
|---|---|---|---|
| 1a | Settings and profiles, `customizing.md`, the vocabulary and grading guide (4.0, with the tie-break), and the numbered-criteria format (`C1`.. each with a `Check:` line) (section 4) | Heavy | |
| 1b | Issue overrides (the `Overrides:` line and `overrides` label), session rulings, and the bounds no level can cross (4.1) | Heavy | 1a |
| 2 | Formats: the role return, finding, QA comment and message schemas with their check script; recommendation required (section 5) | Heavy | 1a |
| 3a | QA loop: impact, effort and scope routing; points; the fix check and patchwork guard; `RECHECK` with its step-ups; `STEP_UP` (Claude Code only; `auto` acts as `ask` until 8c) (3.5, 4.4) | Heavy | 1a, 2 |
| 3b | Findings log with groups, `make findings`, the age rule, debt as a category, and the sweep reading them (3.5) | Heavy | 3a |
| 4a | Grooming: criteria written in the 1a format, the Engineer's criteria checklist (3.3) | Heavy | 1a |
| 4b | Standards: the `Standards:` line and the standards register (3.2, 3.3) | Heavy | 4a |
| 4c | Groom ahead with `[groomed]`; every issue placed in the order (3.3) | Standard | 4a |
| 5 | Decision points: weights, the ledger, the budget, per-point answers, `make decisions` (3.6) | Heavy | 2 |
| 6 | Human tasks: header, `make human-tasks`, the rendered step format, the archive for one-off tasks (7.1) | Standard | |
| 7a | Reflections become files under `_docs/records/reflections/` (3.8) | Heavy | |
| 7b | `make status` replaces the session summary: shows decision points and human tasks, prints the spec version for the start-of-session check; launch-usage lines dropped (issue #191 covers usage) (7.2) | Heavy | 5, 6, 7a |
| 8a | Consult stage (3.1) | Heavy | 1a |
| 8b | Planning lines: the environment map, `Runs in:`, `Debt:`, criterion-level `Needs:` (3.2) | Heavy | 1a, 4a |
| 8c | Reasoning variants of the role definitions; `STEP_UP=auto` takes effect (3.2, 3.5) | Heavy | 3a |
| 9a | Core-rules file loaded by each tool (7.3); absorbs issue #15's three rules | Heavy | |
| 9b | Kiro layer for the core-rules file (the kit's first Kiro files) | Heavy | 9a |
| 10 | Quiet Verify (`V=1` for full output) | Standard | |
| 11a | Delivery-lead role and its Claude Code channel (section 6); absorbs issue #17's parallel-safety rules | Heavy | all of 1 to 8 |
| 11b | Delivery lead's GitHub-comment channel: `Lead:` and `Status:` prefixes in `issue-comment.sh` and `AGENTS.md` | Heavy | 11a |
| 12 | This repo's own docs structure, following socboard's layout: one `_docs/` with `decisions/`, `records/`, `planning/`, `runbooks/`, `reference/` and an index row for each file. That means moving `proposals/` into `_docs/planning/`, `_docs/human-inputs/` into `records/`, and the two project copies under `_docs/reference/` (decision 091 names their paths, so it needs a note) | Standard | |

Issues 6, 7a, 9a, 10 and 12 depend on nothing else and can run in a parallel lane. Issue 11 comes last, because it reads everything the others define. Issues 7 and 9 are Heavy because they change what every session does.

## 10. dmux

A tmux pane per task, each with its own git worktree and branch, launching Claude Code, OpenCode, Codex and others (MIT licensed, about 1.8k stars, `npm install -g dmux`; needs tmux 3.0+, Node 18+, Git 2.20+). Its merge action auto-commits and merges into the main branch, or pushes and opens a PR, with lifecycle hooks. No coordinator, usage tracking, pausing or steering was found. It covers the parallel lanes, not the delivery lead. Its auto-commit may break the kit's staging hooks, and it needs Node and tmux in the dev container. Recommendation: use Claude Code's worktree subagents for lanes first; trial dmux in one lane after issue 11, merging by hand.

## 11. Trimming the project copies

Done:

- `socboard/AGENTS.md` and `socboard/CLAUDE.md` renamed to `*.artifact.md` (commit `c68bfe7`), so no tool loads them as instructions.
- The trim below, apart from the two rows marked "later" (commit `5fcddf7`, 99 files). The three kit copies are kept: `socboard/_docs/agent-kit/`, `vuln-triage/agent-kit/` and `vuln-triage/_docs/agent-kit/`.

The plan as approved:

| Path | Suggestion |
|---|---|
| `vuln-triage/docs/images/` (7.6 MB) | Remove: product screenshots |
| vuln-triage product docs (`api.md`, `openapi.yaml`, `aws-setup.md`, runbooks, roadmaps, rubric) | Remove |
| vuln-triage process docs (`agent-team.md`, `ai-usage-*`, `planning-process.md`, `cloud-sessions.md`, `human-tasklist.md`, `reviews/`, `prompts/`) | Keep |
| socboard product decisions (data model, auth, Postgres, Terraform, deploy, observability) | Remove; keep the process ones (commit attribution, reviewer role and drop, Ponytail, close floor, Claude branches) |
| socboard planning | Keep `deploy-coordination.md`, `epoch-batch-1/`, `sweep-4-candidates.md`, the Ponytail files and roadmap 1; remove the rest |
| `socboard/.kiro/steering/` | Keep: the model for 7.3 |
| `socboard/_human-tasks/` | Later: keep the 267 prod-deploy task and the groom handover; remove the rest after issue 6 |
| Both projects' `_session-summaries/` | Later: keep until issue 7 lands, then keep a sample of five |
| `socboard/_docs/records/` | Keep sweeps and findings; remove product measurements |

## 12. Open questions for the human

Decided by the human on 2026-11-19:

- The 1.11 order: settings, then formats, then the QA loop, as in section 9; issue 12 (docs structure) is part of 1.11.
- The vocabulary and thresholds in 4.0, with Effort at under 10, 10 to 30, and over 30 minutes.
- `ASK_AT=4`: every failing finding (in scope, Moderate or higher) gets at least one fix attempt.
- The step up to a stronger variant is Claude Code only (`STEP_UP=ask` by default). There's none in OpenCode (free models) or Kiro (a named model costs more credits than auto).
- The tie-break rule in 4.0, and the profile defaults in 4.2.
- Findings: an issue straight away for Critical; one issue per group at 5 entries; keep or drop after 5 sweeps.
- `make status` replaces the session summary; reflections stay, as files.
- One short core-rules file loaded by every tool.
- Usage visible to scripts: later, filed as issue #191.
- From the PM's draft review: the vocabulary and criteria format move into issue 1a; the PM's splits; issue 7b after issues 5 and 6, with `make status` printing the spec version; issues 7 and 9 Heavy; a session ruling lasts for that issue; on a project that commits to `main`, work behind an open decision point isn't pushed until it is closed.
- Existing issues: issue #15 folds into 9a and issue #17 into 11a; issue #142 and issue #26 close when 7b is approved; issue #141 keeps only its audit (`_docs/planning/kit-1.11/backlog-review-2026-11-19.md`).

Nothing is open. Next step: the human reviews the drafts in `_docs/planning/kit-1.11/issues/`, then they are filed in the section 9 order.

## 13. Sources

- dmux README: https://raw.githubusercontent.com/standardagents/dmux/main/README.md
- dmux repository: https://github.com/standardagents/dmux
- dmux CONTRIBUTING: https://raw.githubusercontent.com/standardagents/dmux/main/CONTRIBUTING.md
- Independent review of dmux (about June 2026): https://rywalker.com/research/dmux
- Ponytail: https://github.com/DietrichGebert/ponytail
