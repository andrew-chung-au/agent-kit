# Agent kit

**Version 1.10 (2026-11-09).** A tool-agnostic way to run a project with AI coding agents: a PM, Engineer and QA team working from GitHub issues, a verification gate that catches weakened tests, and git hooks as a safety net. It works with any agent that can read `AGENTS.md` and run shell commands, in a codespace, a local dev container sandbox or a local checkout.

The kit is one folder, `_docs/agent-kit/`, copied unchanged into each project. It holds four kinds of material:

- **Shared process:** the lifecycle, team roles and procedures, used as is.
- **Blueprints:** templates plus rules for *when* each applies, for the parts that must be tailored to a project, such as `AGENTS.md`, Makefile targets, settings, hooks and CI.
- **A setup procedure:** an agent reviews the project folder, maps what's already there, and proposes how to build the kit around it.
- **Reference copies of installed files:** the dev container recipe, the push check, the push-check image and the CI workflow template. They sit inside the kit folder but are installed outside it, by you, from a clean clone. `installed-files.txt` maps each one to its install path.

A project can take the kit alone, or the kit plus the dev container (the local sandbox profile). See "Adding the kit to a project folder".

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
  environments.md    where agents run: Codespaces, local sandbox, local checkout
  environments/      local-sandbox/: push check, push-check image, dev container recipe, Compose variant (reference copies)
  claude-code/       optional Claude Code layer: START.md, role definitions, sweep skill, hooks, settings
  opencode/          optional OpenCode layer: START.md, role definitions, sweep skill, permission settings, permission log plugin
```

**Two choices per project.** The core kit is the same everywhere; two things vary:
- **Which agent tool.** A tool layer adds that tool's own enforcement on top of the core kit. `claude-code/START.md` adds role definitions, a hook that blocks forbidden git commands before they run, a hook that won't let the Engineer finish while `make verify` fails, and permission rules. `opencode/START.md` adds role definitions and permission rules. Setup installs the layer for the tool you use.
- **Where agents run.** `environments.md` describes the three profiles: where the agent works, where the kit's hooks are active, where you review and push, and what checks a push. Read it before setting up a local sandbox.

## Adding the kit to a project folder

You need `git`, `make` and `bash`: WSL, macOS, Linux or Codespaces.

There is no tagged release or release zip yet (issue #9 tracks it). Get the kit by cloning the kit's repository, which holds the kit in its `agent-kit/` folder and this README as `agent-kit/README.md`. Treat the clone as a clean clone: copy from it, and never open it in a container or run `make` in it.

**Path 1: kit only.**

1. Copy the clone's `agent-kit/` folder into `<project>/_docs/agent-kit/`.
2. Optional: put a product spec at `<project>/_docs/specs.md`. Without one, the project starts in planning.
3. Start your AI coding tool in the project folder and say: "Set up this project using `_docs/agent-kit/setup.md`."
4. Review what it proposes, approve or correct it, then approve the setup commit.
5. Run `make hooks` once wherever agents commit: the codespace or your local checkout. In the local sandbox profile, never run it (or any `make` target) in the clean clone; see `environments.md`.

**Path 2: kit plus dev container (the local sandbox profile).** Do steps 1 to 4 of path 1, then, from the clean clone:

1. Copy `environments/local-sandbox/devcontainer.json` and `setup.sh` to the project's `.devcontainer/`, and `templates/ci-verify.yml.template` to `.github/workflows/verify.yml`. Put your git name and noreply email in `setup.sh`.
2. Open only the project's `<repo>-sandbox` folder in the container. `setup.sh` runs `make hooks` on the first build. Commit the `.devcontainer/devcontainer-lock.json` that the first rebuild creates.
3. Copy `environments/local-sandbox/pre-push` to `~/.agent-hooks/pre-push` and into each clean clone's `.git/hooks/pre-push`, and make it executable. This is the push check; it needs git, Docker and coreutils on your machine.
4. If the project's `make install` needs Node or uv, build the image from `environments/local-sandbox/push-check.Dockerfile` and set `AGENT_PUSH_CHECK_IMAGE` to it; otherwise the push check uses `python:3.12`. Dry-run it with `AGENT_PUSH_CHECK_PLAN=1 git push`.
5. If the project's checks need a database, use the files in `environments/local-sandbox/compose/`: copy its three files into `.devcontainer/`, next to the standard `setup.sh`.

`environments.md` has the reasons, the token limits and the full rules. The Node, uv and Postgres pins in these files are unverified until you rebuild.

After either path, `make kit-check` tells you whether the kit folder is pristine and, from `installed-files.txt`, whether each installed file still matches its kit source; see "Installed files" under "Updating the kit".

In a monorepo, the hooks go at the repository root and only act on folders that contain `agent-kit.conf`, so projects without the kit are unaffected.

If the repo already has hooks, `make hooks` checks them first. Standard Git LFS hooks are replaced automatically, because the kit's hooks call Git LFS themselves. Any other hook stops the install, so you can merge it by hand.

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

The kit's files are protected in every project, so changes need your approval. Improve the kit in the project you're working on, then copy the folder to other projects you're still actively working on; finished homework can keep the version it was built with. Bump the version at the top of this file when you change it.

**Versions in a project.** A pristine kit claims a plain version, such as `1.9`. Once a project changes a kit file, its kit is a derivative and claims `<base>+<repo>.<n>`, such as `1.9+vuln-triage.2`: `<n>` rises with each local change and restarts at 1 on a new base. The claim is `KIT_VERSION` in `agent-kit.conf`, and `make kit-check` compares the kit folder with the `MANIFEST.sha256` a released kit ships. Leave the version line at the top of this file alone in a derivative; it is one of the hashed files. `make kit-compare KIT_A=<kit folder> KIT_B=<other kit folder>` lists how kit A differs from kit B, read-only; both folders are named, there is no default. The manifest shows drift, not tampering. The kit's own repo ships no manifest between releases.

**Installed files.** `installed-files.txt` lists each kit file that is installed outside the kit folder, where it goes, whether it is a `repo` file or a `human-machine` file (the push check), and what a local copy may differ in. In a project:
- `make kit-check` reads the map, read-only, and reports each `repo` entry as `unchanged`, `local, ignored` (it differs only where the map allows), `drift` or `missing`. A `human-machine` entry is only named ("not checked here"); no sandbox tool opens that path. A map entry the parser rejects stops the check with the parser's message.
- The tool layers' copied files (`.opencode/agents/`, `.opencode/skills/sweep/SKILL.md`, `.opencode/plugins/permission-log.js`, `.claude/agents/` and `.claude/skills/sweep/SKILL.md`) are on the map with the rule `optional`: a project may use one tool, both or neither, and the permission log is optional. A file that is not installed reads `not installed (optional)` and is not a failure; one that is installed must match exactly, so an old copy is `drift`. The files that are merged rather than copied (`opencode.json`, `.claude/settings.json`, `CLAUDE.md`) are not on the map: they differ by project, so `make kit-check` does not compare them; review them at an import.
- The forward import has an installed-files step, step 7 of `procedures/kit-import.md`.
- The reverse import can write a feedback bundle of a project's changed installed and kit files: `make kit-feedback PROJECT=<project root> KIT=<reference kit>` (read-only, writes only under `.scratch/`).
- No agent copies an installed file. You do, from a clean clone. To compare the installed push check, follow "Comparing the installed push check (human only)" in `environments.md`.

**Installed files in a release.** The release zip unpacks only the kit folder. The files the kit installs outside that folder (`.devcontainer/`, the CI workflow, the push check) are not placed by the unzip; the human places them, using `installed-files.txt`, which ships inside the kit folder (so it is in the zip and in `MANIFEST.sha256`). No agent places an installed file. For the `human-machine` entries (the push check), compare the installed copy as in "Comparing the installed push check (human only)" in `environments.md`.

**Cutting a release (human only).** No agent pushes, tags or generates the release manifest. The version line and changelog are committed first; the steps are:
1. Merge the release's issues, and push `main`. `git log origin/main..main` must list nothing, and `git status --short` must be clean.
2. Tag the release commit: `git tag -a v<version> <commit> -m "Kit <version>"`, then `git push origin v<version>`. The tag's README header must read `Version <version>`.
3. Put the tagged kit in a new, empty folder, from the tag and nothing else: `git archive v<version> agent-kit | tar -x -C <empty folder>`.
4. Generate the manifest into that copy: `python3 -B agent-kit/scripts/kit-manifest.py <empty folder>/agent-kit <version>`. The manifest is not committed to this repo.
5. Check it: copy that kit folder into a project's `_docs/agent-kit/`, set `KIT_VERSION="<version>"` and run `make kit-check`; it must report a pristine `<version>`.
6. A project gets the release as the `agent-kit` folder from step 3 with its `MANIFEST.sha256`, imported by `procedures/kit-import.md`. A zip, its unpack layout and a GitHub release are not defined yet (issues #9 and #8).

Refused: a manifest generated from a working tree, a tree with uncommitted or unpushed kit changes, or a commit no one has reviewed on a remote. It would claim a version that no tag holds, so every `kit-check` against it would mislead. Generate only from the `git archive` of the pushed tag.

The git hooks carry their own version number. `make hooks` upgrades an older installed version and leaves an equal or newer one alone, so projects with different kit versions can share one repository.

### Upgrading a project that already uses the kit

Agents take their rules from the project's `AGENTS.md`, not from the kit folder, so replacing the kit files isn't enough on its own. These steps fit Codespaces and a local checkout. In the local sandbox profile, follow "Upgrading the kit in the local sandbox" in `environments.md` instead.

1. Pause at a clean point: finish the current step, commit, and exit the agent session. `git status --short` should show nothing.
2. Unpack the new kit into a new, empty folder under `.scratch/`, never over the live kit folder, and follow `procedures/kit-import.md` to review it file by file.
3. Run `make hooks`. It upgrades older hooks and leaves current ones alone.
4. Start an agent and say: "The agent kit in `_docs/agent-kit/` has been upgraded to <version>. Review this project using `_docs/agent-kit/setup.md` in review mode. Update the shared block in `AGENTS.md` (between SHARED START and SHARED END) to match the template, leaving the project half unchanged (see the note below if it has no marker pair yet), and apply any blueprint changes. The only config files you may read are those listed in the `Readable config` slot of `AGENTS.md`; ask me for anything else. Show me the diffs and the exact `git add` paths, including `_docs/agent-kit/`, and wait for my approval."
5. Review and approve, then commit the kit folder, `AGENTS.md` and any other changed files with `HUMAN_APPROVED=1`. Check that `_docs/agent-kit/` is among the staged paths. Include `.githooks/` at the repo root if `make hooks` changed it.
6. Start a fresh agent session, so the new rules load.

**Note on the settings-read rule:** the shared block now carries the strict ban on reading the tool's settings, plus an opt-in. The project half needs a `Readable config` line, default `none`, which is stricter than the wording only this repo has seen. A project that does nothing keeps the strict ban. To opt in, list the specific files, with the human's approval after checking that they hold no secrets. The step 4 prompt names that slot as the only list of config files the agent may read.

**Note for projects last upgraded before the slimmed template:** the shared rules moved into Non-negotiables, the hook line, Read when triggers and the step docs. The shared block is now bracketed by `<!-- SHARED START ... -->` and `<!-- SHARED END -->`. A project with only the old single `<!-- SHARED: ... -->` marker takes the new block from that marker to the end of its file, and its Project gotchas go after SHARED END. An upgrade never replaces a project's `AGENTS.md` wholesale: the change is a diff you approve. Review the project's own settings and gotchas for rules that now duplicate the moved ones.

### Changes in 1.10

1.10 is the first release that ships a `MANIFEST.sha256` (see "Cutting a release"), so a project can import it by `procedures/kit-import.md` and compare with `make kit-check`. Each change says what an existing project must do. A project last at 1.9 should do them all, in the order of "Upgrading a project that already uses the kit".

**Not verified in a real run** (shipped as written; none changes what an existing project must do): the Compose variant, the push-check image, the OpenCode permission rules on 2.2.5 (the 2026-11-04 re-run was not comparable), `pipx` run directly in the dev container, and the CI template's action major versions (the first CI run confirms those). Verified in a real run: the dev container pins and clean-clone refusal (rebuild check, 2026-11-07) and the OpenCode 2.2.5 permission-log plugin (2026-11-08). Known gaps: this repo's own `.devcontainer/` still lags the reference, and merge commits still skip the `HUMAN_APPROVED` gate.

**Process and roles**
- **Tiers and Heavy gates** (`process.md`, `team/`, `scripts/check-tier.sh`, `make tier-check`): Light, Standard and Heavy tiers with a path limit per tier; Heavy needs an ADR before the Engineer starts and a second fresh QA launch. QA gets a code-review checklist. Existing projects: add the `tier-check` target; nothing else unless you want tiers.
- **Grooming and approval** (`process.md`, `team/pm.md`): the PM grooms before approval, the approved body is frozen by hash (`make issue-hash`), and `approved` can also approve the PM's Standard or Heavy tier proposal. Existing projects: add `issue-hash`; the label rules already in your `AGENTS.md` still hold.
- **Planning** (`procedures/planning.md`, the spec definition of ready, spec notes layout, roadmap template, optional Design section in the issue template): one intent per issue, a testable example, a plan-review checklist. Existing projects: nothing; use the new templates when you next file an issue or plan.
- **Templates and records** (`templates/`): the issue template's required Why section, a GitHub issue intake form, the pull request template (`Refs #N`, never `Closes`), human task files, the docs index with entry-type folders and starter docs, decision records linked to their evidence. `make dup-report` lists repeated sentences and decision keys with differing status (read-only, never a gate). Existing projects: copy `templates/github/ISSUE_TEMPLATE/` and `templates/github/pull_request_template.md` into your `.github/` if you want them; add the `dup-report` target.
- **Procedures**: the orchestrator comments procedure (claim, release, confirm and close comments start with `Orchestrator:`), a periodic sweep procedure with skill wrappers, the Report by reference rule, and the session-summary reflection and launch usage lines. Existing projects: copy the kit folder; copy the sweep skills (`.claude/skills/sweep/`, `.opencode/skills/sweep/`) if you use them.

**`AGENTS.md`**
- The template changed since 1.9 and has not changed since 2026-11-03 (`67153ed`; the permission, install and release changes after that did not touch it). The shared block is now Non-negotiables, Enforced by hooks and Read when, bracketed by `SHARED START` and `SHARED END`; the project half gains a `Readable config` line (default `none`), a `Fetch an issue` command and a session-summaries line. Existing projects: update the shared block by the diff in step 4 of "Upgrading a project that already uses the kit"; keep the project half and add the new lines.

**Scripts, Makefile and hooks**
- **Issue wrappers** (`scripts/issue-create.sh`, `issue-comment.sh`, `issue-close.sh`, `issue-hash.py`, `secret-patterns.txt`; `make issue-dump`, `issue-hash`, `sweep-due`): create and comment through a secret scanner and an owner check; `issue-close` can close an issue and nothing else. Existing projects: copy `scripts/` and the new `Makefile.mk` targets.
- **Safer file handling** (`scripts/check-staged.sh`, `verify.sh`, `check-tier.sh`, `assert-clean.sh`, `githooks/pre-commit` version 4, `githooks/pre-push`, `claude-code/hooks/verify_on_stop.py`): changed names are read NUL-delimited, so non-ASCII and quoted names are checked, and the checks fail closed. A make variable is validated without being expanded. Existing projects: copy `scripts/`, then run `make hooks`, which upgrades the hooks.
- **Claude Code git guard** (`claude-code/hooks/guard_git.py`, `claude-code/settings.json`): also blocks shell commands naming `.env` files (not `.env.example`) and has a stricter allow-list and ask rules. The OpenCode permission template has safer read-only allows and more command patterns (`opencode/opencode.json`). The settings-read rule is narrowed: a project may list committed config files under `Readable config`. Existing projects: the hooks run in place from the kit folder; merge the settings by review, because `.claude/settings.json` and `opencode.json` are merged, not copied.
- **Project bootstrap** (`scripts/bootstrap-project.sh`): the human runs it once from a plain folder to create the clean clone and sandbox folder, install the push check and copy the tracked kit files, the recipe and the CI template; it refuses a kit with unpushed commits or uncommitted changes. Existing projects: nothing.
- **Claims check** (`scripts/check-claims.py`, run by `make test` in this repo): fails when a doc names a make target or file the kit doesn't ship. Existing projects: nothing.

**Permission logs** (optional)
- **OpenCode plugin** (`opencode/plugins/permission-log.js`, the OpenCode 2 plugin API) and a **Claude Code logger** (`claude-code/hooks/log_permission.py`) record each permission prompt; `make permission-report [SINCE=<YYYY-MM-DD or YYYY-MM-DDTHH:MMZ>]` summarises both and `make permission-logs-prune DAYS=<n>` deletes old logs (the human runs it). The logger refuses a symlinked log folder or file and the plugin resubscribes when the event stream ends. Existing projects: to use OpenCode's log, copy `.opencode/plugins/permission-log.js` from a clean clone (it needs OpenCode 2.2.5 and replaces any 1.x plugin); for Claude Code, merge the hook entry from `claude-code/settings.json`. Skip both if you don't want logs.

**Kit versions, import and the installed-file map**
- **Hash manifest and import** (`scripts/kit-manifest.py`, `kit-check.py`, `kit-compare.py`, `kit-feedback.py`, `kit-map.py`; `procedures/kit-import.md`; `installed-files.txt`): `make kit-check` says whether the kit folder is pristine or a derivative of `KIT_VERSION`, `make kit-compare` lists how two kit folders differ, `make kit-feedback` writes a read-only bundle of a project's changes for the reverse import, and the forward import (which replaces the old unzip-over-the-kit upgrade step) reviews a new kit file by file and reviews installed files at step 7. A live kit without a manifest is imported by finding its baseline commit (`scripts/kit-baseline.py`, below). Existing projects: copy the scripts and the `kit-check`, `kit-compare`, `kit-baseline` and `kit-feedback` targets; add `KIT_VERSION` and `GITHUB_REPO` to `agent-kit.conf` (see `templates/agent-kit.conf.template`); a project at "1.9" that is really a later snapshot should claim `1.9+<repo>.1` until it imports 1.10.
- **Manifest and map details**: the generator, `kit-check` and `kit-compare` refuse invisible and direction-changing characters in file names and symlinks, and the map parser refuses line breaks other than newline. Existing projects: nothing.

**Environments and installed copies**
- **Docs and reference files** (`environments.md`, `environments/local-sandbox/`): why a clean clone is never opened in a container, the human-only read-only push-check comparison, the WSL 2 with Docker Desktop Wayland mount failure, and the rewritten READMEs for the merged kit and dev container repo. Existing projects: nothing.
- **Installed files to recopy from a clean clone**: `.devcontainer/devcontainer.json` and `setup.sh` (the OpenCode 2.2.5 pin, Node, uv, `PATH`, container name, early clean-clone refusal; keep your own `git config --global user.` lines), then rebuild; `.github/workflows/verify.yml` from `templates/ci-verify.yml.template` if you use it (Node and uv pins); `.opencode/` and `.claude/` agent files and skills (they changed with the roles). The push check (`environments/local-sandbox/pre-push`) is unchanged since 1.9. `make kit-check` lists each one as `unchanged`, `local, ignored`, `drift` or `missing`.

**Details of the later changes**

- **Manifest refuses symlinks with skipped names** (`scripts/kit-manifest.py`): a symlink named `*.pyc`, `__pycache__` or `MANIFEST.sha256` is now refused like every other symlink, by the generator and by `kit-check`, `kit-compare` and `kit-feedback`, with a test per caller. Existing projects need nothing; a kit folder holding such a link now fails the generator instead of silently skipping it.
- **GitHub wrappers use the REST API and name the repository** (`scripts/github_api.py`, `issue-create.sh`, `issue-comment.sh`, `issue-close.sh`, `issue-hash.py`, `sweep-due.py`, the `issue-dump` target): they read the repository from one `GITHUB_REPO="<owner>/<name>"` line in `agent-kit.conf` (read as text, validated, protected) and call `gh api`, so they work where the git remote is not github.com, such as Kiro Web. Every comment page is read. Existing projects: add the `GITHUB_REPO` line to `agent-kit.conf` (see `templates/agent-kit.conf.template`), copy `scripts/github_api.py` with the other scripts, and update the `issue-dump` recipe in your `Makefile` from `templates/Makefile.mk`; without the line every wrapper refuses.
- **Installed-file map covers the tool layers** (`installed-files.txt`, `scripts/kit-map.py`, `README.md` "Installed files"): the OpenCode and Claude Code agents, the sweep skills and the permission-log plugin now have map lines, so `make kit-check` reports them as unchanged, drift or missing. The permission-log plugin is optional: a project without it reads `not installed (optional)` and exits 0. Existing projects: copy the new `installed-files.txt` lines and `scripts/kit-map.py`.
- **Kit import with no manifest** (`procedures/kit-import.md`, `scripts/kit-baseline.py`, the `kit-baseline` target): a live kit that has no `MANIFEST.sha256` can be imported by finding the commit of the kit's repository it was copied from, with the human approving the baseline. The procedure runs the script from the source clone (`python3 -B .scratch/kit-src/agent-kit/scripts/kit-baseline.py <live kit folder> .scratch/kit-src`), so a project from before 1.10 needs nothing. To get `make kit-baseline`, add the target from `templates/Makefile.mk` to your `Makefile` and copy `scripts/kit-baseline.py` with the other scripts. A kit file name that is not valid UTF-8 now makes the manifest scripts refuse the kit folder, as a control character already did.
- **Push-check image** (`environments/local-sandbox/push-check.Dockerfile`, `environments.md`): a reference image with Node and uv at the dev container recipe's pins, and the first documentation of `AGENT_PUSH_CHECK_IMAGE`. Existing projects need nothing unless their push check lacks an image with the tools `make install` needs.
- **Dev container recipe for Python plus frontend projects** (`environments/local-sandbox/`): Node and uv at pinned versions (all unverified until you rebuild and check), the `claude` and `opencode` folders on `PATH`, a container named after its folder, and `setup.sh` that refuses early in a clean clone. The CI template shows the same Node and uv pins, and the Makefile blueprint has a `tool-versions` target. Existing projects: copy the recipe changes into your `.devcontainer/` from a clean clone, then rebuild; commit the lock file the rebuild creates.
- **Optional Compose variant** (`environments/local-sandbox/compose/`): an `app` plus Postgres `db` recipe for projects whose checks need a database, with its limits pinned by tests. Existing projects need nothing.

### Changes in 1.9

- **Environment profiles** (`environments.md`): Codespaces, local sandbox (dev container plus a clean clone) and local checkout, with where agents work, where hooks run, where you push and what checks a push. A new **Environment** setting in `AGENTS.md` tells agents which profile applies.
- **Local sandbox reference files** (`environments/local-sandbox/`): a monorepo-aware push check that finds every project the new commits change, with git alone, and runs `make -C <project> install verify` in a throwaway container that sees only a bundle of the pushed commits; the dev container recipe. Copy them only from a clean clone. `environments.md` also lists the ways a sandbox folder or clean clone can still run code on your machine, and how to avoid them.
- **Never run `make` in a clean clone.** `make hooks` also refuses there, detected by a `sandbox` remote or the push check, but that's only a convenience.
- **Repo-root protection** (pre-commit hook version 3): changes to `.github/`, `.devcontainer/`, `.vscode/`, `.envrc` and `.gitmodules` at the repo root need `HUMAN_APPROVED=1`, like `.githooks/`, including files with unusual names.
- **CI template** limits the job to `permissions: contents: read` and says never to add secrets.
- **OpenCode layer** (`opencode/`, start at `START.md`): role definitions, with PM and QA limited to writing in `.scratch/`, and permission rules. Minimal for now: no hooks.

### Changes in 1.8

- **Claude Code layer** (`claude-code/`, start at `START.md`). It replaces the separate Claude Code-only kit 1.0 used in Table Ready, and brings it fully up to date with the core kit:
  - role definitions that point to `team/`: the PM edits files only under `.scratch/` by instruction, QA can't edit files, and the Engineer carries a hook that re-runs `make verify` before it can finish;
  - a git guard hook that blocks broad staging, `commit -a`, `--no-verify`, `git push` and `core.hooksPath` changes before they run;
  - settings with the allow-list, ask rules for protected files, deny rules for `.env` files and `git push`, and commit attribution. The git guard also blocks shell commands naming `.env` files (not `.env.example`); indirection such as `bash -c "cat .env"` is a known gap for both tools. The OpenCode template denies shell commands naming `.env` files by a text pattern, not a boundary.

  The hooks run in place from the kit, so kit upgrades update them.
- **Existing agent setups:** setup no longer needs to know where a project's current setup came from. It reads each existing agent file, works out what it does, and classifies it against the kit: superseded, merged, kept or flagged as a conflict. That covers older kit versions, other kits and hand-built tool configurations alike.
- **Setup** asks which AI tools you use, and installs the Claude Code layer when it applies.

### Changes in 1.7

- **Asking the human:** a new procedure, `procedures/asking-the-human.md`. Every command's description says what it does and why, naming the issue and step. Anything that needs approval on its merits gets an approval request before the command runs: what and why, the exact command, risk and undo, alternatives, and a recommendation. Decisions come as decision questions with options and a recommendation.
- **Subagents:** the human can't see a subagent's messages, so a subagent returns its request to the orchestrator instead of running the command. The orchestrator passes the request on in full and resumes the role with the answer.
- **Approval requests also cover:** whether the request came up before; a check run just now for any addresses or IDs in the command; risk with duration; and alternatives that fix the cause or let the human run the command, so agents don't need `sudo`.
- **Known environment issues:** a new blueprint. A problem that needed the human's fix more than once gets a README entry (symptom, check, fix, undo), which later requests point to.
- **Deletions and safety blocks:** agents don't delete files or data they didn't create, including git-ignored files and Docker volumes, which **Assert clean** can't see. When the tool blocks an action as risky, the agent stops and reports instead of trying variations. The orchestrator then shows the human each blocked command, checks what changed, and proposes resuming or starting the role fresh.
- **Destructive checks:** when checking a criterion needs a destructive step, such as deleting a Docker volume, the PM says so when grooming, and the human performs that step.
- **`make clean-scratch`:** a new core target. At the end of every issue the orchestrator empties `.scratch/`, including test tokens and copied session logs, after proposing any script worth keeping as a test or make target. It refuses while a process started with `<name>-start` is still running.
- **Upgrades:** the upgrade prompt asks for the exact `git add` paths, including the kit folder.
- **Commit attribution:** a new blueprint. AI-assisted commits carry one plain line, "Generated with Claude Code", set in the tool's settings, with no co-author email or model version. Agents don't add their own co-author lines.

### Changes in 1.6

- **Conventions:** one list of shell forms to avoid, with replacements; files are edited only with the tool's editor; no reading the tool's settings, the home folder or environment variables; servers start and stop through make targets or `.scratch/` scripts, and agents stop only processes they started; bypass attempts go in tests or scripts; requests for system changes include the undo command; large `.scratch/` installs need asking and are deleted afterwards.
- **Process:** a standard launch message for roles; one decision point after QA passes; clean-up before the session summary; a procedure for a role that stops early.
- **PM:** decides edge cases itself and asks only about scope, interfaces, the spec or security limits; every limit says how it's enforced, with a case that must be refused; fixed text records where it comes from; spec notes are collected, not stopped for.
- **Engineer:** lists choices the issue doesn't cover and spec notes; adds a stub setting for anything that starts a paid or external process.
- **QA:** a fuller comment layout; tries to get around every limit; reports risks outside the criteria separately from the verdict.
- **Blueprints:** start/stop targets, the stub setting and role definitions for tools with named subagents. The session summary template gains decisions, temporary changes and interruptions.

## Tool-native enforcement

Tools with their own hooks or permission systems can enforce the rules harder than instructions can. For Claude Code, that's the `claude-code/` layer. For other tools, follow the same pattern: keep the configuration in the tool's own folder, have it call the kit's scripts and `make` targets, and keep `AGENTS.md` and this kit as the source of truth.
