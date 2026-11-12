# Agent kit

**Version 1.10 (2026-11-09).** A tool-agnostic way to run a project with AI coding agents: a PM, Engineer and QA team working from GitHub issues, a verification gate that catches weakened tests, and git hooks as a safety net. It works with any agent that can read `AGENTS.md` and run shell commands, in a codespace, a local dev container sandbox or a local checkout.

The kit is one folder, `_docs/agent-kit/`, copied unchanged into each project. It holds four kinds of material:

- **Shared process:** the lifecycle, team roles and procedures, used as is.
- **Blueprints:** templates plus rules for *when* each applies, for the parts that must be tailored to a project, such as `AGENTS.md`, Makefile targets, settings, hooks and CI.
- **A setup procedure:** an agent reviews the project folder, maps what's already there, and proposes how to build the kit around it.
- **Reference copies of installed files:** the dev container recipe, the push check, the push-check image and the CI workflow template. They sit inside the kit folder but are installed outside it, by you, from a clean clone. `installed-files.txt` maps each one to its install path.

A project can take the kit alone, or the kit plus the dev container (the local sandbox profile). To install or upgrade, pick your situation in `install-and-upgrade.md` and follow its numbered steps.

## Which file to open

Each doc states its purpose and reader in its first lines. H is the human, A an agent.

| I want to | Open | Reader |
|---|---|---|
| Install the kit, or upgrade a project | `install-and-upgrade.md` | H |
| See what changed in a version and what my project must do | `CHANGELOG.md` | H |
| Cut a release and build the kit zip | `releasing.md` | H (maintainer) |
| Know where agents run and the rules for each place | `environments.md` | H |
| Set up the local sandbox, or look up a pin or a push-check detail | `environments/local-sandbox/README.md` | H |
| Set up or review a project with the kit | `setup.md` | A |
| Know how work moves from idea to done | `process.md` | A |
| Know what a project needs and when | `blueprints.md` | A |
| Review a newer kit against my kit | `procedures/kit-import.md` | A |
| Use one step of the process (verify, ask the human, plan, sweep) | `procedures/` | A |
| Use Claude Code or OpenCode with the kit | `claude-code/START.md`, `opencode/START.md` | H, A |

## How the controls work

No tool-agnostic equivalent of an AI tool's own hooks or permission system exists, so the kit layers four controls:

1. **Instructions (primary).** `AGENTS.md` and the role files carry the rules: stage explicit paths only, don't push, don't edit protected files without approval, never skip hooks. Every tool reads these, so they do most of the work.
2. **Git hooks (safety net).** They run whichever tool commits or pushes:
   - **Pre-commit** refuses secrets and generated files, whitespace errors, and changes to protected files unless `HUMAN_APPROVED=1` is set.
   - **Pre-push** runs `make verify`, and blocks the push if tests fail or have been weakened.
3. **Your review (the real control).** You approve protected changes, read the diff, and do every push yourself.
4. **CI (optional backstop).** A GitHub Actions workflow running `make verify` is the only layer an agent can't bypass.

**Limits, stated plainly:**
- Any agent can skip git hooks with `--no-verify`, or set `HUMAN_APPROVED=1` itself. The instructions forbid both, which makes a breach a visible rule violation rather than an accident.
- The QA check (`make assert-clean`) detects changes after the fact; it doesn't prevent them.
- Hooks don't run for commits made on the GitHub website.
- All roles usually share one GitHub login, so GitHub can't stop one role editing another's comments or closing an issue. The rules forbid it, and GitHub's edit history shows if it happened.

## What's in the kit

```
_docs/agent-kit/
  README.md          this file (for humans)
  setup.md           setup and review procedure (for agents)
  blueprints.md      what a project needs, and when
  process.md         lifecycle: planning, backlog, roles, verification, handover
  team/              pm.md, software-engineer.md, qa-engineer.md
  procedures/        verify.md, session-summary.md, asking-the-human.md, sweep.md, processes.md, permission-log.md, kit-import.md, orchestrator-comments.md, planning.md
  templates/         AGENTS.md, agent-kit.conf, Makefile (core and GitHub parts), task, human-task, session-summary, docs-index, starter-docs, roadmap, source, measurement, adr, runbook, CI workflow, and GitHub issue and pull request templates
  scripts/           verify.sh, check-staged.sh, check-tier.sh, assert-clean.sh, install-hooks.sh, lib.sh, issue-*.sh, issue-hash.py and github_api.py (issue text and the `gh api` reads), scan-issue-body.sh, kit-check.py, kit-compare.py, kit-baseline.py, kit-feedback.py, kit-manifest.py, kit-map.py (kit and installed-file checks), check-claims.py, dup-report.py, sweep-due.py, permission-report.py, permission-logs-prune.py and helpers
  githooks/          pre-commit, pre-push and a Git LFS pass-through, installed at the repo root
  installed-files.txt  map of kit files installed outside the kit folder, and where
  releasing.md       cutting a release and building the kit zip (human only)
  CHANGELOG.md       what changed in each version, and what an existing project must do
  install-and-upgrade.md  step-by-step install and upgrade, one section per situation, for humans
  environments.md    where agents run: Codespaces, local sandbox, local checkout
  environments/      local-sandbox/: README (setup and reference), push check, push-check image, dev container recipe, Compose variant (reference copies)
  claude-code/       optional Claude Code layer: START.md, role definitions, sweep skill, hooks, settings
  opencode/          optional OpenCode layer: START.md, role definitions, sweep skill, permission settings, permission log plugin
```

**Two choices per project.** The core kit is the same everywhere; two things vary:
- **Which agent tool.** A tool layer adds that tool's own enforcement on top of the core kit. `claude-code/START.md` adds role definitions, a hook that blocks forbidden git commands before they run, a hook that won't let the Engineer finish while `make verify` fails, and permission rules. `opencode/START.md` adds role definitions and permission rules. Setup installs the layer for the tool you use.
- **Where agents run.** `environments.md` describes the three profiles: where the agent works, where the kit's hooks are active, where you review and push, and what checks a push. Read it before setting up a local sandbox.

## Installing and upgrading

Open `install-and-upgrade.md`: pick your situation and follow its numbered steps. They say where each command and prompt is typed and what you should see. A kit zip is built by the human as in `releasing.md`. What changed in each version is in `CHANGELOG.md`. `make kit-check` after an install or upgrade tells you whether the kit folder is pristine and, from `installed-files.txt`, whether each installed file still matches its kit source; see "Installed files" under "Updating the kit".

## Day to day

- **Work:** "Work the next issue following `_docs/agent-kit/process.md`."
- **Decisions:** after QA passes, the orchestrator brings everything that needs you (AGENTS.md and spec changes, protected files, risks QA found) in one message, each with a recommendation.
- **Approvals and questions:** anything that needs your approval on its merits (a system change, stopping a process, an install, anything outside the project) comes as a request first: what and why, the exact command, the risk and how to undo it, the alternatives, and a recommendation. Questions come with options and a recommendation too. See `procedures/asking-the-human.md`. If an approval prompt appears with no request before it and a description that doesn't say why, decline with "explain first".
- **Approving a protected change:** once you've read the diff, tell the agent "approved, commit it with `HUMAN_APPROVED=1`", or commit it yourself. Tools that check commands will ask once more before that commit. That's intended: check that the staged paths match what you approved, then accept. Never pre-approve these commits.
- **Pushing:** read `git diff origin/main --stat -- .` and the diff, then push. If the pre-push hook blocks you, its output says why. In the local sandbox profile you review and push from the clean clone, and your push check runs instead; see `environments.md`.
- **Checking the setup later:** "Review this project using `_docs/agent-kit/setup.md`." Review mode reports blueprints that now apply, such as a new linter, and any drift.

## Fewer approval prompts

Agents trigger most approval prompts in two ways: working outside the project folder (scratch files in `/tmp`, redirects to `/dev/null`, reading the tool's own settings), and shell commands too complex for the tool to check. The commonest are editing files from the shell (`sed -i`, heredoc scripts), `$?` and other shell variables, `cd … &&` chains, and settings put before a command (`VAR=x make run`). The command-shape rules in the Non-negotiables list these forms and their replacements: the tool's own editor, `.scratch/` scripts, `make <target> VAR=x`, and start/stop targets for servers.

A prompt is worth stopping for when it's a real decision (a design or security choice), a protected commit, or something outside the project. For the rest, approve if the purpose is fine. If you decline, say why in a few words, such as "use the Edit tool" or "no `$?`". The agent is told never to pursue a declined goal another way, so the reason tells it what to fix.

To pre-approve routine commands in your tool, see Tool permissions in `blueprints.md`. Allow rules can't remove prompts for commands the tool can't analyse; only simpler commands can.

## Updating the kit

The kit's files are protected in every project, so changes need your approval. Improve the kit in the project you're working on, then bring the change into other projects you're still actively working on by the steps in `install-and-upgrade.md`; finished homework can keep the version it was built with. Bump the version at the top of this file when you change it.

**Versions in a project.** A pristine kit claims a plain version, such as `1.9`. Once a project changes a kit file, its kit is a derivative and claims `<base>+<repo>.<n>`, such as `1.9+vuln-triage.2`: `<n>` rises with each local change and restarts at 1 on a new base. The claim is `KIT_VERSION` in `agent-kit.conf`, and `make kit-check` compares the kit folder with the `MANIFEST.sha256` a released kit ships. Leave the version line at the top of this file alone in a derivative; it is one of the hashed files. `make kit-compare KIT_A=<kit folder> KIT_B=<other kit folder>` lists how kit A differs from kit B, read-only; both folders are named, there is no default. The manifest shows drift, not tampering. The kit's own repo ships no manifest between releases.

**Installed files.** `installed-files.txt` lists each kit file that is installed outside the kit folder, where it goes, whether it is a `repo` file or a `human-machine` file (the push check), and what a local copy may differ in. In a project:
- `make kit-check` reads the map, read-only, and reports each `repo` entry as `unchanged`, `local, ignored` (it differs only where the map allows), `drift` or `missing`. A `human-machine` entry is only named ("not checked here"); no sandbox tool opens that path. A map entry the parser rejects stops the check with the parser's message.
- The tool layers' copied files (`.opencode/agents/`, `.opencode/skills/sweep/SKILL.md`, `.opencode/plugins/permission-log.js`, `.claude/agents/` and `.claude/skills/sweep/SKILL.md`) are on the map with the rule `optional`: a project may use one tool, both or neither, and the permission log is optional. A file that is not installed reads `not installed (optional)` and is not a failure; one that is installed must match exactly, so an old copy is `drift`. The files that are merged rather than copied (`opencode.json`, `.claude/settings.json`, `CLAUDE.md`) are not on the map: they differ by project, so `make kit-check` does not compare them; review them at an import.
- The forward import has an installed-files step, step 7 of `procedures/kit-import.md`.
- The reverse import can write a feedback bundle of a project's changed installed and kit files: `make kit-feedback PROJECT=<project root> KIT=<reference kit>` (read-only, writes only under `.scratch/`).
- No agent copies an installed file. You do, from a clean clone. To compare the installed push check, follow "Comparing the installed push check (human only)" in `environments/local-sandbox/README.md`.

**Intended copies.** Some files are copies of a named kit source. `tests/test_intended_copies.py`, run by `make test`, fails when one drifts; the table gives each copy's rule, and in a project `make kit-check` reports drift for every copy on `installed-files.txt`.

| Copy | Source | Rule |
|---|---|---|
| Shared block of `AGENTS.md`, from `## Non-negotiables` to the `SHARED END` marker | `templates/AGENTS.md.template` | Equal, apart from the template's `- <...>` placeholder lines, which a project deletes or fills |
| `.claude/agents/*` and `.opencode/agents/*` | `claude-code/agents/*` and `opencode/agents/*` | In a project, byte for byte. In this repo each copy tells the role to read `AGENTS.md` first and names the kit folder `agent-kit/` or `_docs/agent-kit/`; the test removes those two differences and fails on any other |
| `.github/pull_request_template.md` | `templates/github/pull_request_template.md` | Byte for byte |
| `CLAUDE.md` | `claude-code/CLAUDE.md.template` | Byte for byte in this repo. A project merges it rather than copying it, so it is off `installed-files.txt` and is reviewed at an import |
| `claude-code/skills/sweep/SKILL.md` | `opencode/skills/sweep/SKILL.md` | Equal, apart from Claude Code's `disable-model-invocation: true` front-matter line, which the OpenCode copy leaves out |
| `_docs/index.md` | `templates/docs-index.md` | Instantiated once, then filled in with this project's tables, so only its section headings are compared; `tests/test_human_task.py` keeps the human-task entry type in both |

`_human-tasks/*` reuse the boilerplate in `templates/human-task.md`, but they are dated records, not copies, so no check polices them.

**Releases (human only).** The steps for cutting a release, and for installed files in a release, are in `releasing.md`.

The git hooks carry their own version number. `make hooks` upgrades an older installed version and leaves an equal or newer one alone, so projects with different kit versions can share one repository.

## Tool-native enforcement

Tools with their own hooks or permission systems can enforce the rules harder than instructions can. For Claude Code, that's the `claude-code/` layer. For other tools, follow the same pattern: keep the configuration in the tool's own folder, have it call the kit's scripts and `make` targets, and keep `AGENTS.md` and this kit as the source of truth.
