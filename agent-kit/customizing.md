# Customizing the kit

Where a project goes to change a kit value. Reader: the human running a project, and the roles that grade work.

Every value the process uses is a **setting** with a kit default. A project changes one with a single line in `agent-kit.conf`, or picks a **profile** that sets a few of them at once, instead of editing the kit's text and carrying a fork. `make settings` prints each setting, its value and where that value comes from. This page also holds the **grade vocabulary** every role uses.

Nothing in the kit acts on the settings yet. Each setting below names the issue that makes it take effect; until that issue lands, a value you write has no effect.

## Grades

Three grades, three levels each, and no word or letter shared between them:

| Grade | Low | Middle | High | Graded by | Used for |
|---|---|---|---|---|---|
| Reasoning | Basic (B) | Normal (N) | Deep (D) | PM, at grooming | Which subagent variant to launch |
| Effort | Short (S) | Regular (R) | Extended (E) | PM for issues, QA for findings | Splitting, lanes, fix routing (points 1, 2, 3) |
| Impact | Low (L) | Moderate (M) | Critical (C) | QA | PASS or FAIL |

Agents need more than the table: two runs grade alike only when each level has a test and an example.

| Grade | Level | Test | Example |
|---|---|---|---|
| Reasoning | B | The answer follows from the issue text; no judgement between options | Rename a target everywhere; add an index row |
| | N | Choices between known options, inside one area | Add a make target with input checks; a doc section with a new rule |
| | D | Security, concurrency, interfaces others depend on, or rules that interact | A permission gate; a hook that parses commands; a change to the lifecycle |
| Effort | S | Under 10 minutes of agent work; one small change in one file or a few lines | A wording fix; a one-line test |
| | R | 10 to 30 minutes; a few files, a focused task with tests | A new script with its tests |
| | E | Over 30 minutes, or likely to span more than one session; consider splitting | Changes across the project; a procedure rewrite across the kit |
| Impact | L | Cosmetic: meaning and outcome stay correct, with no material inconvenience | A typo; an unclear but correct sentence |
| | M | Confusion, a workaround or a minor delay, but the correct outcome is still reachable | A wrong expected output; a misleading error message |
| | C | An incorrect outcome, a risk of data loss or to security, or an essential task that can't be completed | A check that accepts invalid input; a command that fails as written and blocks the procedure |

Effort counts agent work: Short is under 10 minutes, Regular 10 to 30 minutes, Extended over 30 minutes.

**Tie-break rule:** when unsure between two levels, take the higher one for Impact and Reasoning (the cost of under-grading is a missed defect or a weak model), and the lower for Effort (an underestimate is found out at the fix check, cheaply). Each grade comes with one line of reason, so a wrong grade can be challenged.

## Levels

| Level | Where | Who changes it | Lasts |
|---|---|---|---|
| Kit default | Kit docs | Upstream | Until the kit changes |
| Profile | `PROFILE=` in `agent-kit.conf` | The human (protected file) | Until changed |
| Project setting | One line per setting in `agent-kit.conf` | The human | Until changed |
| Path rule | A path pattern in `agent-kit.conf`, as `LIGHT_ALLOWED` works now | The human | Until changed |
| Issue override | The `Overrides:` line plus the `overrides` label | PM proposes, human approves | That issue |
| Session ruling | The human, in a session, recorded in an `Orchestrator:` comment | The human | That issue; it becomes a setting only at a sweep |

Each level overrides the one above. `make settings` and `scripts/settings.py` resolve five levels: kit default, then profile, then project setting, then, with `make settings N=<n>`, the issue override and the session ruling of issue `<n>`. The path rule level stays with `scripts/check-tier.sh`. Environment variables and make variables with a setting's name are ignored.

**A profile never stops you customizing.** It is only a set of defaults for a few settings. Any setting you write yourself wins over the profile, whatever the profile is. So `PROFILE=fleet` plus `LANES=2` gives the fleet defaults with two lanes. Switching the profile later changes only the settings you haven't written. A profile saves writing several lines, and lets you switch the whole shape at once (a Kiro sprint, then back) without losing your own choices.

Most settings aren't in any profile at all: they have one default and are set on their own. Only the settings that really follow the usage plan (lanes, grooming ahead, the delivery lead, status frequency) are in profiles.

## Settings

**Writing a setting.** One line in `agent-kit.conf`, starting at the beginning of the line: `NAME=value`, `NAME="value"` or `NAME='value'`, with nothing after it but spaces or tabs. The template (`templates/agent-kit.conf.template`) carries every setting commented out with its default; remove the `# ` to set one. `make settings` (read-only) prints `PROFILE`, then one `<NAME>=<value> (<source>)` line per setting, where the source is `kit default`, `profile <name>` or `agent-kit.conf line <n>`, and with `N=<n>` also `issue #<n> body line <l>` or `issue #<n> ruling <createdAt> line <l>` (see "One issue" below).

**What is refused.** The reader reads `agent-kit.conf` as text and never runs it. It refuses, with `settings: agent-kit.conf line <n>: <reason>` and exit status 1, and never falls back to a default: an unknown name at the start of a line (so if your project keeps its own variables in `agent-kit.conf`, move them out before using `make settings`), an unknown profile, a value outside the allowed values (an empty value or the wrong letter case included), the same setting written twice, anything after the value other than spaces or tabs (a trailing comment too), a setting name followed by `=` anywhere other than its own line at column 1 (indented, after `export`, after another assignment such as `KIT_DIR=x LANES=5`, after `;`, or inside `if ... fi`), and a file that starts with a UTF-8 byte order mark. The reader doesn't parse bash, so it is conservative: it also refuses a setting name followed by `=` where bash would not assign it, such as an indented line inside a `PROTECTED=( ... )` array or inside a multi-line quoted value. Comment lines are always passed over. A conf that is missing or can't be opened is refused too.

**Whole number** means `0` or digits without a leading zero, with no sign.

**Profile settings** (the profile sets the default; writing the setting overrides it):

| Setting | `solo` | `team` | `fleet` | Allowed values | What it does | Takes effect with |
|---|---|---|---|---|---|---|
| `GROOM_AHEAD` | `2` | `4` | `6` | whole number 0 to 99 | Issues groomed ahead of the one in progress | #203 |
| `LANES` | `1` | `2` | `3` | whole number 1 to 99 | Parallel lanes | #214 |
| `DELIVERY_LEAD` | `off` | `off` | `on` | `on`, `off` | The delivery-lead role | #214 |
| `STATUS_EVERY` | `milestone` | `milestone` | `15m` | `milestone`, or `<n>m` with n a whole number 1 to 999 | How often a running role posts status | #214, #215 |

**Standalone settings** (one default, in no profile; `PROFILE` itself is listed first):

| Setting | Default | Allowed values | What it does | Takes effect with |
|---|---|---|---|---|
| `PROFILE` | `solo` | `solo`, `team`, `fleet` | Selects the profile column above; unset means `solo` | #196 |
| `DECISION_BUDGET` | `3` | whole number 0 to 99 | Open Continue weight before new work stops; 0 means every decision point stops. Often changed by a session ruling, for example before you go away | #204 |
| `QA_FAIL_AT` | `M` | `L`, `M`, `C` | Lowest impact that fails | #199 |
| `QA_SCOPE_STRICT` | `yes` | `yes`, `no` | QA fails only on criteria and listed standards | #199 |
| `RECHECK` | `changed` | `changed`, `full` | `changed` (with its automatic step-ups) or `full` | #199 |
| `FIX_CHECK_LOOPS` | `2` | whole number 1 to 99 | Inner loop: fix and fix check, within one round | #199 |
| `ASK_AT` | `4` | whole number 1 to 99 | Outer loop: a failing finding with fewer points goes back to the Engineer; at this many, "ship or fix?" goes to the human | #199 |
| `SHIP_RULE` | `none` | `none`, or one to three comma-separated `key:value` pairs, no spaces, each key at most once: `impact:` `L`/`M`/`C`, `effort:` `S`/`R`/`E`, `rounds:` whole number 0 to 99 | When a failing finding may ship without asking; its meaning comes with #199 | #199 |
| `STEP_UP` | `ask` | `auto`, `ask`, `off` | Claude Code only: whether a finding's second failure moves the next fix to a stronger variant: `auto`, `ask` or `off` | #199; `auto` acts as `ask` until #210 |
| `FINDINGS_TO_ISSUE_AT` | `C` | `L`, `M`, `C` | Lowest impact that gets an issue straight away; the rest goes to the findings log | #200 |
| `FINDINGS_GROUP_AT` | `5` | whole number 1 to 99 | Log entries in one group before the sweep drafts one issue for them | #200 |
| `FINDINGS_KEEP_SWEEPS` | `5` | whole number 1 to 99 | Sweeps a log entry may stay open before the human is asked to keep or drop it | #200 |
| `HEAVY_SECOND_QA` | `on` | `on`, `off` | The independent second QA launch for Heavy | no 1.11 issue wires `off` yet; `on` is what the kit does today |
| `WAIVABLE_GATES` | `heavy-second-qa,qa-recheck` | `none`, or one or more of `heavy-second-qa`, `qa-recheck`, comma-separated, no spaces, each at most once | Which QA gates a recorded `Waiver:` may name; set in `agent-kit.conf` only | #197 checks `Waiver:` lines against it, #218 lets `make issue-close` accept them |

`FIX_CHECK_LOOPS` and `ASK_AT` are not duplicates. They limit different loops: `FIX_CHECK_LOOPS` limits the cheap inner loop (fix, fix check) inside one round, and adds no points. `ASK_AT` acts on the outer loop of QA re-checks, where each failed re-check adds a point. A round looks like this: the Engineer fixes; the fix check runs, up to `FIX_CHECK_LOOPS` times; QA re-checks; if the finding fails again it gains a point; below `ASK_AT` it goes back to the Engineer for another round, and at `ASK_AT` it goes to the human.

**`STEP_UP` applies in Claude Code only.** OpenCode, Kiro and CodeBuddy ignore it: OpenCode runs free models, so there is no stronger variant to move to; in Kiro a named model uses more credits than its automatic choice; and the kit configures no model swapping in CodeBuddy. When a finding fails twice on a tool without a step up, the orchestrator notes that no escalated model is configured, so the patchwork guard's approach review is the only step up.

**Not settings:**
- The model for each reasoning level: it is set in the project's role definitions, not here.
- `LIGHT_ALLOWED` (the path rule level) and `LIGHT_MAX_LINES` stay as they are. `scripts/check-tier.sh` reads them, not `scripts/settings.py`.
- The other `agent-kit.conf` lines (`KIT_DIR`, `KIT_VERSION`, `GITHUB_REPO`, `TEST_CMD` and the rest) are explained by the comments in `templates/agent-kit.conf.template`.

**Defaults that differ from what the kit does today.** The human kept these decided defaults (2026-11-19). The issue that wires each one states the change, and the conf line that keeps today's behaviour, in its changelog entry:
- `GROOM_AHEAD=2`: today `process.md` (Lifecycle, step 2) grooms only the next issue. Wired by #203.
- `DECISION_BUDGET=3`: today every decision waits for the decision point at the end of the issue. Wired by #204.
- `QA_SCOPE_STRICT=yes`: today the Heavy second QA launch fails on any problem (`team/qa-engineer.md`). Wired by #199.
- `HEAVY_SECOND_QA=off` has no effect yet; a follow-up issue makes it work.

## One issue: overrides and session rulings

`make settings N=<n>` writes the issue's dump (as `make issue-dump N=<n>` does, so it needs `gh`), then reads `.scratch/issue-<n>.json` with the conf. The orchestrator runs it before each Engineer and QA launch, right after the hash check; a refusal stops the launch. Two levels sit above the project lines, and both last for that issue only:

- **Issue override.** One body line, at column 1: `Overrides: NAME=value, NAME=value` (items separated by a comma and one space; a value has no spaces, so `SHIP_RULE=impact:M,effort:E` is one item). It applies only when the issue also has the `overrides` label, which only the human adds. The approved body hash covers the line. The PM writes it at grooming.
- **Session ruling.** A comment from the repository owner's account whose first line starts `Orchestrator: Ruling` and that has a `Human ruled: <YYYY-MM-DD>` line (layout: `procedures/orchestrator-comments.md`). Each `Ruling: NAME=value` line in it sets a value; a later ruling comment beats an earlier one, and a ruling beats an override. A `Ruling:` line that doesn't start with `NAME=` is a process ruling: recorded, not read as a setting. A `Waiver: <gate> - <reason>` line records a QA gate the human waived; the gate must be in `WAIVABLE_GATES`. A waiver changes no setting, and nothing acts on it yet: #218 lets `make issue-close` (`templates/Makefile.github.mk`) accept it.

**What is refused** at both levels, naming the issue and the line (`settings: issue #<n> body line <l>: <reason>` or `settings: issue #<n> ruling <createdAt> line <l>: <reason>`, exit status 1): an `Overrides:` line without the `overrides` label; two `Overrides:` lines; an empty list or an item that isn't `NAME=value`; a name that isn't a setting (the other conf names, such as `PROTECTED` or `LIGHT_MAX_LINES`, included); `PROFILE` and `WAIVABLE_GATES`, which only a project line sets; the same name twice; a value outside the allowed values; a value that crosses a bound (below); a bullet or indented `Overrides:`, `Ruling:` or `Waiver:` line; a ruling comment without the `Human ruled:` line; and a `Waiver:` line with a gate `WAIVABLE_GATES` doesn't list, no ` - `, an empty reason or a gate named twice. A missing or malformed dump, or one for another issue, is refused too. Passed over: a mention inside a sentence (such as `` `Overrides: X=1` ``), and `Ruling:` and `Waiver:` lines anywhere but an owner ruling comment.

## Bounds no level can cross

Some limits no override or ruling can change. `scripts/settings.py` enforces them with one table, `BOUNDS`, at the issue override and session ruling levels: today `HEAVY_SECOND_QA=off` is refused there on every issue (a project line may still write it, and it has no effect yet). The other bounds hold because no level can name them: there is no setting for the tier, the `approved` or `tier:` labels, protected files or pushes; the conf names that hold path rules are refused at the issue levels; and a `Waiver:` can name only a gate in `WAIVABLE_GATES`, whose allowed values are the two QA gates, never QA itself or any rule above, and which an issue can't widen for itself.

## Profiles follow your usage, not the project's size

| Profile | Fits | Why |
|---|---|---|
| `solo` | OpenCode on a small quota; Claude Code within a five-hour window | Parallel work and a coordinating role would spend the usage the work needs |
| `team` | One long Claude Code session with subagents | Some parallel work; the main session coordinates |
| `fleet` | Kiro, or any large pooled budget used in one go | Many lanes; coordination pays for itself |

## When to add a setting

The kit should not make everything configurable at once. Each setting is one more thing to read, explain, test and keep working across upgrades. So the kit adds a setting only when there's evidence that projects need different values, for example when two projects have changed the same value in their copy of the kit, or a sweep shows a different value would have saved rounds. Until then the value stays fixed in the kit's text.

When a setting is added, its default keeps what the kit did before, unless the human decides otherwise. An existing project that upgrades then behaves as it did, and changes only if it writes the setting. Every default the human decides differently is listed under "Defaults that differ from what the kit does today" above, and the issue that wires it announces the change in its changelog entry, so nobody is surprised by an upgrade.

A new setting goes in the table in `scripts/settings.py` and in a table on this page; `tests/test_settings.py` checks that the two agree. A new setting that could drop QA, lower a tier or loosen the label, protected-file or push rules adds its `BOUNDS` row in the same issue, or its `PROJECT_ONLY` entry when no issue may change it at all.
