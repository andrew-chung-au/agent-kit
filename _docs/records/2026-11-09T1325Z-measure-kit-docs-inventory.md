# Kit docs inventory (issue #182, step 1)

**Measured:** 2026-11-09, on branch `issue-182-doc-structure` (main at `7c53c54` plus the #181 branch, which adds `install-and-upgrade.md`). Word counts are `wc -w`. Repeats are from `make dup-report` (72 files scanned, 60 repeated sentences of 12 or more words, 0 decision keys). Method and limits: word counts include code blocks; the reader column is judged from each file's own opening lines, not measured.

Reader: **H** = the human, **A** = an agent, **S** = a script or test reads it.

## Core docs in `agent-kit/`

| File | Words | Purpose today (one line) | Reader | Jobs it does now | Verdict |
|---|---|---|---|---|---|
| `README.md` | 5,826 | Overview | H | 1 overview and controls; 2 layout listing; 3 install paths; 4 day to day and approval prompts; 5 updating (versions, installed files, release); 6 upgrade steps; 7 changelog 1.6 to 1.10 (about 2,700 words); 8 tool-layer note | Does 8 jobs. Split. |
| `install-and-upgrade.md` | 4,270 | Step-by-step install and upgrade per situation, with prompts (#181) | H | Install, upgrade, dev container upgrade, building the kit zip | Keep as the one home for walkthroughs. Move the release situation out (see target). |
| `environments.md` | 3,348 | Where agents run | H | 1 three profiles; 2 one-time setup (bootstrap, recipe table, pins, token, push-check image, Compose); 3 sandbox security rules; 4 sandbox upgrade steps; 5 push-check comparison | Does 4 jobs. Split. |
| `process.md` | 3,555 | Lifecycle from idea to done | A (H reads it) | Session start, planning, backlog, roles, orchestrator, tiers, lifecycle, commits, definition of done | One purpose, but long. Keep; check overlap with `setup.md` and `team/`. |
| `blueprints.md` | 3,408 | What a project needs and when | A | Catalog, notes on specific blueprints (including a Grafana/Prometheus note), tool pointers, permissions, attribution | One purpose. The Grafana note is project-specific; candidate to move out. |
| `setup.md` | 1,434 | The setup and review procedure | A | Seven steps from locate to hand over | One purpose. Keep. |
| `installed-files.txt` | 317 | Map of files installed outside the kit folder | S | Data read by `kit-map.py` | Keep. |

## Procedures, roles, tool layers

| File | Words | Purpose | Reader | Verdict |
|---|---|---|---|---|
| `procedures/kit-import.md` | 945 | Review a newer kit file by file | A | Keep. Owns the classification table. Stop repeating the unzip/clone steps that `install-and-upgrade.md` also gives (it now links). |
| `procedures/asking-the-human.md` | 1,074 | How a role asks for approval | A | Keep. |
| `procedures/planning.md` | 460 | Spec planning guideline | A | Keep. |
| `procedures/session-summary.md` | 600 | Session summary format | A | Keep. |
| `procedures/sweep.md` | 578 | Periodic sweep | A | Keep. |
| `procedures/verify.md` | 264 | Verify a change | A | Keep. |
| `procedures/permission-log.md` | 329 | Permission log record format | A, S | Keep. |
| `procedures/orchestrator-comments.md` | 293 | Four comment layouts | A | Keep. |
| `procedures/processes.md` | 87 | Start and stop servers | A | Keep. |
| `team/pm.md`, `qa-engineer.md`, `software-engineer.md` | 966 / 675 / 449 | Role instructions | A | Keep. All three repeat one sentence ("Its Non-negotiables apply to you, including when you run as a subagent"); intended. |
| `claude-code/START.md` | 1,046 | Claude Code layer start page | H, A | Keep. |
| `opencode/START.md` | 1,534 | OpenCode layer start page | H, A | Keep. |

## Templates

Thirteen templates under `templates/` (about 3,800 words in all). Each is a copy source, not a fact home. Intended copies are in the next table.

## Where the facts live now (facts with more than one home)

These are the facts a reader needs that are stated in more than one doc. "Home" is the proposed single owner.

| Fact | Stated in today | Proposed home |
|---|---|---|
| How to install the kit (Path 1, Path 2) | README "Adding the kit", `environments.md` "Local sandbox", `install-and-upgrade.md` | `install-and-upgrade.md` |
| How to upgrade a project (Codespace or checkout) | README "Upgrading a project", `install-and-upgrade.md` situation 8 | `install-and-upgrade.md` |
| How to upgrade in the local sandbox | `environments.md` "Upgrading the kit in the local sandbox", `install-and-upgrade.md` situations 4 to 6 | `install-and-upgrade.md` |
| The upgrade prompt | README step 4, `install-and-upgrade.md` Prompt C, `environments.md` | `install-and-upgrade.md` (Prompt C) |
| What the bootstrap script does | script header, `environments.md`, `install-and-upgrade.md` | The script header owns what it does; `environments.md` owns why; the walkthrough owns how to run it |
| How the kit import is classified | `procedures/kit-import.md`, `install-and-upgrade.md` (summary) | `procedures/kit-import.md` |
| Release steps (tag, archive, manifest, zip) | README "Cutting a release", `install-and-upgrade.md` situation 9 | One release doc (see target) |
| Version scheme (`<base>+<repo>.<n>`) | README "Updating the kit", `procedures/kit-import.md` Version | `procedures/kit-import.md` for how to set it; README keeps one sentence |
| What each version changed, and what a project must do | README changelog 1.6 to 1.10 | `CHANGELOG.md` (new) |
| Installed files and their map | README "Installed files", `installed-files.txt` header, `procedures/kit-import.md` step 7, `blueprints.md` | `installed-files.txt` header for the format; one prose home (README signpost) |
| Who closes issues | `AGENTS.md`, `process.md` | `process.md`; the `AGENTS.md` line is an intended copy |

## Intended copies (need a named source and a drift check)

| Copy | Source | Drift check today |
|---|---|---|
| Shared block of `AGENTS.md` (about 30 sentences) | `templates/AGENTS.md.template` | Markers say "change it there first"; no automated check found |
| `.claude/agents/*`, `.opencode/agents/*` (6 files) | `claude-code/agents/*`, `opencode/agents/*` | `installed-files.txt` plus `make kit-check` report `drift` in a project; none in this repo |
| `.github/pull_request_template.md` | `templates/github/pull_request_template.md` | None found |
| `_docs/index.md` | `templates/docs-index.md` | None found |
| `CLAUDE.md` | `claude-code/CLAUDE.md.template` | None found |
| Sweep skills (2 files) | each other | None found |
| `_human-tasks/*` | `templates/human-task.md` | Not copies to police: dated records that reuse its boilerplate |

## Findings

1. The README mixes the overview with procedures that now have a home in `install-and-upgrade.md`. After #181, two homes exist for install and upgrade until the README's copy goes.
2. About 20,400 of the 35,400 words counted sit in five files (`README.md`, `install-and-upgrade.md`, `process.md`, `blueprints.md`, `environments.md`); `README.md` and `environments.md` are the two that do more than one job.
3. 30 of the 60 repeated sentences are `AGENTS.md` against another file (29 against its template: the shared block, intended, but guarded only by the marker comment). 13 are `_human-tasks/` boilerplate, and 17 are role files, sweep skills, the PR template, `docs-index` and `CLAUDE.md` against their copies or each other (30 + 13 + 17 = 60).
4. About 30 test files read docs (README, `environments.md`, `process.md`, `blueprints.md`, `setup.md`). A move will touch them, and `check-claims.py` requires every installable path to be named in `blueprints.md`.
5. A moved changelog changes `MANIFEST.sha256` at the next release, as the issue says.

## Not measured

Whether readers actually find the right file faster after a split. The reader column is a judgment from each file's opening lines.
