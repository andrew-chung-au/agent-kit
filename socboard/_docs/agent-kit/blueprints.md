# Blueprints

What a project using this kit should have, when each piece applies, and how to create it for the folder it's in. Setup (`setup.md`) works through this list; so does any later review. The templates are starting points: adapt every placeholder to the project, never copy one in unchanged.

## Rules for every blueprint

- **Build on what exists.** Merge into existing files; never replace or delete them. When an existing file does the same job as a blueprint, adapt the blueprint to it, or propose moving the old one to `_docs/archive/`. The human decides.
- **Only when it applies.** Each blueprint has a trigger. If it hasn't happened yet, record the blueprint as "later", not "not needed".
- **Propose first.** Show every new file or change as a diff, and create nothing until the human approves.
- **Don't loosen a gate to make existing code pass.** If existing code fails a new check, leave that check off in `agent-kit.conf` and propose an issue to fix the code.

## Catalog

| Blueprint | Applies when | Where | Source |
|---|---|---|---|
| Project instructions | Always, at setup | `AGENTS.md` in the project folder | `templates/AGENTS.md.template` |
| Tool pointer file | The human uses a tool that doesn't read `AGENTS.md` | Project folder | See Tool pointers below |
| Kit settings | Always, at setup | `agent-kit.conf` in the project folder | `templates/agent-kit.conf.template` |
| Core make targets: `help`, `verify`, `assert-clean`, `hooks`, `clean-scratch` | Always, at setup | Project `Makefile` | `templates/Makefile.mk` |
| `install`, `test` targets | The stack is known: code or a spec naming it | Project `Makefile` | `templates/Makefile.mk` |
| `run`, `test-one`, `e2e`, `migration` targets | The project has that capability | Project `Makefile` | `templates/Makefile.mk` |
| `<name>-start` and `<name>-stop` targets | The project has a long-running process that agents start and stop while testing (a server, a watcher, a responder) | Project `Makefile` | `templates/Makefile.mk` |
| `issue-hash` target | The project's tasks are GitHub issues | Project `Makefile` | `templates/Makefile.mk`, running `scripts/issue-hash.py` (with `scripts/github_api.py`; the repository is the `GITHUB_REPO` line of `agent-kit.conf`) |
| `issue-dump` target | The project's tasks are GitHub issues | Project `Makefile` | `templates/Makefile.mk`, running `scripts/github_api.py` |
| GitHub module: `issue-create`, `issue-comment` and `issue-close` targets | The project's tasks are GitHub issues and the human wants agents to file, comment and (the orchestrator) close through wrappers | Project `Makefile` (needs `issue-number-ok` from `templates/Makefile.mk`) | `templates/Makefile.github.mk`, running `scripts/issue-create.sh`, `scripts/issue-comment.sh` and `scripts/issue-close.sh`, which use `scripts/scan-issue-body.sh`, `scripts/issue-text-lib.sh`, `scripts/github_api.py` and the shared pattern file `scripts/secret-patterns.txt` |
| `sweep-due` target | The project runs the periodic sweep and its tasks are GitHub issues | Project `Makefile` | `templates/Makefile.mk`, running `scripts/sweep-due.py` (with `scripts/github_api.py`) |
| `kit-check` target | The project's kit came with a `MANIFEST.sha256` (a released kit) | Project `Makefile` | `templates/Makefile.mk`, running `scripts/kit-check.py`; read-only, not part of `make verify`. It also reports each installed file in `installed-files.txt` as `unchanged`, `local, ignored`, `drift` or `missing`, through the shared `scripts/kit-map.py` scan, and never opens a human-machine install path |
| Duplicate report: `dup-report` target | The human asks for it | Project `Makefile` | `templates/Makefile.mk`, running `scripts/dup-report.py`; `make dup-report` is read-only, always exits 0 and is never part of `make verify`, `make test` or a hook |
| `kit-compare` target | One kit folder is compared with another, both named (kit import) | Project `Makefile` | `templates/Makefile.mk`, running `scripts/kit-compare.py`; read-only, a two-way list, not part of `make verify` |
| `kit-baseline` target | A live kit has no manifest and is imported against a newer kit (kit import, "No manifest") | Project `Makefile` | `templates/Makefile.mk`, running `scripts/kit-baseline.py`; read-only, needs a clone of the kit's repository, not part of `make verify` |
| `kit-feedback` target | A project's kit is reviewed and its changes bundled for the kit (reverse import) | Project `Makefile` | `templates/Makefile.mk`, running `scripts/kit-feedback.py`; read-only, writes only under `.scratch/` through the shared `scripts/kit-map.py` scan, never opens a human-machine install path, not part of `make verify` |
| Installed-file map `installed-files.txt` | The kit installs files outside its folder (`.devcontainer/`, the CI workflow, the push check); read as text only, never generated in a project | The kit folder, shipped in the release and covered by `MANIFEST.sha256` | `installed-files.txt`, read by `scripts/kit-map.py` (the one shared parser and scan: `make kit-check` reports its drift); the human installs the files |
| Kit version claim `KIT_VERSION` | The project carries a released kit; `<base>+<repo>.<n>` once it changes a kit file | `agent-kit.conf` (read as text by `make kit-check`) | `templates/agent-kit.conf.template`; the scheme is in README, Updating the kit |
| Kit import procedure | The project carries a kit and meets a newer one, or this repo reviews a project's customised kit | Read through the review-mode drift list in `setup.md` and the README upgrade steps | `procedures/kit-import.md` |
| Kit hash manifest `MANIFEST.sha256` | A kit release; never generated in a project | The kit folder, shipped in the release | `scripts/kit-manifest.py <kit folder> <version>`, a release step (#9). The kit's own repo ships none between releases, so it isn't expected to pass `make kit-check` |
| `tier-check` target | The project's tasks are GitHub issues and it uses the tiers | Project `Makefile` | `templates/Makefile.mk`, running `scripts/check-tier.sh` |
| Tier labels `tier:light`, `tier:standard`, `tier:heavy` | The project's tasks are GitHub issues and it uses the tiers | The repository's labels; the human creates them, agents never do | `process.md`, Tiers |
| Sweep procedure and skill | The project wants periodic reflection and measures | `procedures/sweep.md`; the skill in `.claude/skills/sweep/` or `.opencode/skills/sweep/` | `procedures/sweep.md`, `claude-code/skills/`, `opencode/skills/` |
| Sweep entries | The first sweep | The folder the index names for records, listed in `_docs/index.md` | `procedures/sweep.md`, `templates/measurement.md` |
| Long-running process procedure | The project has a long-running process that agents start and stop (see the start and stop targets) | Read through the "Read when" trigger in `AGENTS.md` | `procedures/processes.md` |
| Orchestrator comment layouts | The project's tasks are GitHub issues and an orchestrator writes claim, release, confirm and close comments | Read through the "Read when" trigger in `AGENTS.md` | `procedures/orchestrator-comments.md` |
| Stub setting for external processes | The project's code starts a paid or external process (an AI agent, a cloud service) | The project's own configuration | Added by the Engineer with the feature; see below |
| Lint and type-check gates | A linter or type checker is installed **and** existing code passes it | `lint`/`typecheck` targets, then `LINT_CMD`/`TYPECHECK_CMD` in `agent-kit.conf` | `templates/Makefile.mk` |
| Environment profile | Always, at setup | **Environment** setting in `AGENTS.md` | `environments.md` |
| Git hooks | Always, at setup; once per repository | `.githooks/` at the repo root, activated by `make hooks` wherever agents commit (never in a clean clone) | `githooks/`, via `scripts/install-hooks.sh` |
| Ignore rules | Always, at setup | Project `.gitignore` | See Ignore rules below |
| Product spec | Planning; written or approved by the human | `_docs/specs.md` | Human-owned; see `process.md` |
| Session summaries folder | The first session summary | `_session-summaries/` | `procedures/session-summary.md`, `templates/session-summary.md` |
| Human task files | The first time the human must run or check something by hand beyond a one-line command | `_human-tasks/` at the project root | `templates/human-task.md`, `procedures/session-summary.md` |
| Issue task format | Always, at setup | Every groomed issue | `templates/task-template.md` |
| Starter docs | Always, at setup | The three day-one files; anything else is created at its first entry | `templates/starter-docs.md` |
| Docs index | Always, at setup | `_docs/index.md` | `templates/docs-index.md` |
| Roadmap | The first planned phase or milestone; one file per phase or milestone | The folder the index names for planning | `templates/roadmap.md` |
| Entry-type folders | The first doc of that type; the folder the index names | One folder per entry type, as the index's entry-types table defines | `templates/docs-index.md` |
| Source entries | The project depends on something external (data, API, vendor doc, standard, tool version) | Source folder from the index | `templates/source.md` |
| Measurement entries | The project has a repeatable check of quality or cost | Measurement folder from the index | `templates/measurement.md` |
| Decision records | A choice that may be revisited, and every `tier:heavy` issue (its ADR; one row per ADR in the docs index), including one that is Heavy only by an approved proposal | Decision folder from the index | `templates/adr.md` |
| Runbook entries | A problem needed the same fix twice | Runbook folder from the index | `templates/runbook.md` |
| CI backstop | The human asks for it, or uses the local sandbox profile | `.github/workflows/` at the repo root | `templates/ci-verify.yml.template` |
| Issue intake form | The repository is public or takes issues from outside reporters. The form asks for the problem, what they expected and evidence, and applies no label. The PM grooms an intake issue into the `task-template.md` shape, as for any issue | `.github/ISSUE_TEMPLATE/intake.yml` at the repo root | `templates/github/ISSUE_TEMPLATE/intake.yml` |
| Pull request template | Agents open pull requests (for example a cloud session). It says `Refs #N`, never a close keyword, and lists what `make verify` ran. GitHub applies it only to pull requests opened in the web UI, so an agent opening one over the API reads the file | `.github/pull_request_template.md` at the repo root | `templates/github/pull_request_template.md` |
| Local sandbox files | The human uses the local sandbox profile | `.devcontainer/` at the repo root; the push check in `~/.agent-hooks/` | `environments/local-sandbox/`, copied by the human from a clean clone |
| Claude Code layer | The human uses Claude Code | `CLAUDE.md` and `.claude/` in the project folder | `claude-code/START.md`, with `claude-code/agents/` and `claude-code/hooks/` |
| OpenCode layer | The human uses OpenCode | `opencode.json` and `.opencode/` in the project folder | `opencode/START.md`, with `opencode/agents/` |
| Permission log (Claude Code) | The human uses Claude Code and wants a record of what it asked to approve | The `PermissionRequest` entry of `.claude/settings.json`; the log in `.agent-kit/logs/permissions/`, git-ignored | `claude-code/hooks/log_permission.py` and `scripts/permission_log_lib.py`, registered by `claude-code/settings.json`; the record format in `procedures/permission-log.md`; it reads `scripts/secret-patterns.txt` |
| `permission-report` and `permission-logs-prune` targets | The project keeps the permission log | Project `Makefile` | `templates/Makefile.mk`, running `scripts/permission-report.py` and `scripts/permission-logs-prune.py`; the human runs prune |
| Permission log (OpenCode) | The human uses OpenCode and wants a record of what it asked to approve | `.opencode/plugins/permission-log.js`; the log in `.agent-kit/logs/permissions/`, git-ignored | `opencode/plugins/permission-log.js`; the record format in `procedures/permission-log.md`; it reads `scripts/secret-patterns.txt` |
| Tool-native enforcement for other tools | The human wants hard enforcement in a tool without a layer | That tool's own config folder | Not in the kit; see README |
| Tool permission allow-list | The human's tool asks for approval on routine commands | That tool's own settings file | See Tool permissions below |
| Role definitions | The human's tool can define named subagents, and the orchestrator launches roles as subagents | That tool's agents folder, for example `.claude/agents/` | See Role definitions below |
| Commit attribution | An AI agent commits to the project | The agent's commit message; optionally the tool's settings file | See Commit attribution below |
| Known environment issues | An environment problem (firewall, disk, Docker, ports) needed the human's fix in an earlier issue | A "Known environment issues" section in the project README | See below |

## Notes on specific blueprints

**Project instructions.** Fill the project half from what the folder actually contains; write "none" for command slots the project doesn't have yet. Keep the shared block (between the SHARED START and SHARED END markers) unchanged. Carry useful content from any existing instruction file into the project half, and say where each part went. In a monorepo, include the line that limits work to this folder. Leave nested instruction files that other tools generated (for example `frontend/AGENTS.md`) in place, and check they don't contradict the root file.

**Kit settings.** Set `TEST_CMD` to the test target. Adjust `TEST_FILES` to the project's test layout and `FORBIDDEN` to its secrets and generated files. Keep `PROTECTED` covering at least `AGENTS.md`, `Makefile`, `agent-kit.conf`, the spec and the kit folder. New projects get `LIGHT_ALLOWED` (empty, so nothing qualifies for Light until the human lists paths) and may set `LIGHT_MAX_LINES` (default 20); both are read by `make tier-check`.

**Make targets.** Wrap the project's existing commands; don't introduce new tools. Add missing targets to an existing Makefile, and never rename or replace existing ones. Add a `## description` comment after each existing target's name so `make help` lists it. When a target is added, the Commands section of `AGENTS.md` gets the matching slot, except for process helpers such as `issue-hash`, `issue-create`, `issue-comment`, `issue-close`, `sweep-due`, `tier-check`, `permission-report` and `permission-logs-prune`, which `pm.md`, `process.md` and the Issues rule introduce. `issue-dump` is a process helper that does get a slot (**Fetch an issue**, from `templates/AGENTS.md.template`). Any target that takes a variable follows the validation rule in `templates/Makefile.mk`, under the GitHub-issues heading; the project's own targets go under its "Project targets" heading.

**GitHub module.** The create and comment wrappers only create an issue or post a comment; they never label, edit or close. `issue-close` closes one issue after checking its recorded history, and does nothing else. `scripts/secret-patterns.txt` is the one pattern list (read by `grep -E -f` here and by a later plugin), so keep its patterns to what `grep -E`, Python and JavaScript read alike.

**Start and stop targets.** Agents trigger approval prompts, and risk stopping the wrong process, when they start a server with `&` and stop it with `pgrep` and `kill`. A target pair keeps the process ID and log in `.scratch/`, refuses to start a second copy, and stops only the process it started. Name the pair after the process, for example `responder-start` and `responder-stop`, and add both to the Commands section of `AGENTS.md`. Keep the project's foreground target (such as `make run`) for humans.

**Stub setting for external processes.** Tests and smoke checks shouldn't start a real AI agent or call a paid service. When the code starts one, it gets a setting that swaps in a stub (for example `RESPONDER_AGENT_CMD`), and the tests use it. Real runs stay a manual, deliberate step.

**Known environment issues.** When the same environment problem comes back, the human shouldn't have to work it out again from an approval prompt. Add one entry per problem to the project README, proposed at the decision point:

```
### Grafana can't reach Prometheus (codespaces)
- Symptom: data source errors in Grafana; the 5xx alert never fires.
- Check: docker network inspect order-tracker_default -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
- Fix (human): sudo iptables-legacy -I DOCKER-USER -s <subnet> -d <subnet> -j ACCEPT
- Undo: sudo iptables-legacy -D DOCKER-USER -s <subnet> -d <subnet> -j ACCEPT
- Lasts until: the codespace restarts, or the stack's network is recreated with a new subnet. Re-run the check after `make run`.
```

Agents then cite the entry in their approval request instead of rediscovering the fix.

**Lint and type-check gates.** Order matters: add the targets, fix or suppress the existing errors (as an issue, through the normal process), and only then set `LINT_CMD`/`TYPECHECK_CMD`. Setting them earlier would block every push on errors nobody introduced.

**Git hooks.** Hooks are repository-wide, so they live at the repo root even when the project is a subfolder. They only act on folders containing `agent-kit.conf`, so other folders are unaffected. Once installed, git ignores `.git/hooks`, so `install-hooks.sh` checks what's there first. Standard Git LFS hooks are replaced automatically: the kit installs LFS pass-throughs, and its `pre-push` uploads LFS objects after verify passes. Any other existing hook stops the install until the human merges it or approves `FORCE=1`. The `.githooks/` folder is committed once, and `make hooks` runs once wherever agents commit. In the local sandbox profile that's the dev container only, never the clean clone (`environments.md`). The pre-commit hook also asks for `HUMAN_APPROVED=1` on repo-root `.github/` and `.devcontainer/` changes.

**Ignore rules.** Make sure the project's `.gitignore` contains these lines, in this order, so `.env.example` stays tracked:

```
.env
.env.*
!.env.example
.scratch/
.agent-kit/logs/
```

The last line is for projects with the permission log. Add local databases, and build, cache and dependency folders for the stack. Check the result with `git check-ignore .env.example`, which should print nothing (without `-v`; with it, git also prints the `!.env.example` line that un-ignores the file). The pre-commit hook catches these files too, but ignore rules keep them out of `git status`.

**Session summaries.** If the project already has summaries with a naming scheme, keep that scheme and record it in the **Session summaries** setting in `AGENTS.md`.

**CI backstop.** Keep the template's `permissions: contents: read` and never give the job secrets. In a monorepo, the workflow must sit in `.github/workflows/` at the repo root, with a `paths:` filter for the project folder. A `.github/` folder inside a project folder is ignored by GitHub. Fill in the stack setup steps from the project's tooling.

## Tool pointers

Many AI coding tools read `AGENTS.md` directly. For a tool that reads its own file instead, add a short pointer file so every tool gets the same instructions. Check the tool's documentation for its file name and import syntax. For example:

- **Claude Code** reads `CLAUDE.md`, which can import other files. The Claude Code layer installs it from `claude-code/CLAUDE.md.template`: `@AGENTS.md`, then a line pointing temporary files at `.scratch/`, because Claude Code's default scratchpad is outside the project folder and triggers approval prompts.
- **OpenCode** reads `AGENTS.md` directly, so it needs no pointer file.
- **Other tools:** a pointer file that says "Follow the instructions in AGENTS.md", if the tool can't import files.

Create pointer files only for tools the human actually uses.

## Tool permissions

Tools that ask before running commands can usually pre-approve safe ones. Allowing the project's `make` targets, read-only git commands (`git status`, `git diff`, `git log`) and scripts in `.scratch/` (`python3 .scratch/…`, `bash .scratch/…`) removes most routine prompts, while pushes and edits to protected files still ask. Only propose this for a tool the human uses, and show the settings change for approval. For Claude Code, the layer's `claude-code/settings.json` already holds these rules.

Never allow-list `git push` or commits with `HUMAN_APPROVED=1`. The prompt before an approved commit is the human's last check that what's staged is what they approved.

Allow rules don't help with commands the tool can't analyse (shell variables, heredocs, chains, paths outside the folder). Those still ask whatever the allow rules say, so the only fix is the agent writing simpler commands, as the command-shape rules in the Non-negotiables of `AGENTS.md` describe.

In a monorepo, tools that restrict reads to the project folder will ask each time a kit review reads the repo-root `.githooks/`. Add that one folder to the tool's allowed directories, not the whole repo root. In Claude Code, that's `/add-dir <repo root>/.githooks` for one session, or `permissions.additionalDirectories` in `.claude/settings.local.json` to keep it.

## Role definitions

Some tools let a project define named subagents. The orchestrator can then launch "the QA engineer" instead of a general-purpose agent that has to be told, in each launch message, to read the project's instructions. Each definition is a short pointer, so the role files in `_docs/agent-kit/team/` stay the single source of truth.

For Claude Code and OpenCode, the layers provide all three: see `claude-code/START.md` and `opencode/START.md`. For another tool, write the same short pointer in that tool's format: "Read `AGENTS.md`, then `_docs/agent-kit/team/<role>.md`, and follow both. If something needs the human's approval, return the request to the orchestrator instead of running it." Protect the definitions in `agent-kit.conf`, because they decide what each role is told, and create them only for tools the human uses.

## Commit attribution

Mark AI-assisted commits with one plain line naming the tool, so a commit's tool can be read from git. The agent writes it as the last line of the commit message: `Assisted-by: <Tool>`, for example `Assisted-by: OpenCode`. Leave out co-author lines with an email address and model versions: the address may not be one you'd choose, and both go stale. Record the model in the session summary's launch usage line instead. A tool setting may add a line of its own as well, such as the Claude Code block below; an extra line is harmless. <!-- local deviation: _docs/decisions/2026-11-06T0111Z-commit-attribution.md -->

In Claude Code, the layer's `settings.json` already includes this block. To apply it to every project instead, put it in the human's user settings:

```json
{
  "attribution": {
    "commit": "Generated with Claude Code",
    "pr": "",
    "sessionUrl": false
  }
}
```

`"pr": ""` adds nothing to pull request descriptions, and `"sessionUrl": false` leaves out the session link. For other tools a setting is optional, because the agent writes the line itself; add one only if the human wants the tool to add its own as well.
