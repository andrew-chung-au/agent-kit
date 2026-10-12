# Agent kit

**Version 1.9 (2026-10-10).** A tool-agnostic way to run a project with AI coding agents: a PM, Engineer and QA team working from GitHub issues, a verification gate that catches weakened tests, and git hooks as a safety net. It works with any agent that can read `AGENTS.md` and run shell commands, in a codespace, a local dev container sandbox or a local checkout.

The kit is one folder, `_docs/agent-kit/`, copied unchanged into each project. It holds three kinds of material:

- **Shared process:** the lifecycle, team roles and procedures, used as is.
- **Blueprints:** templates plus rules for *when* each applies, for the parts that must be tailored to a project, such as `AGENTS.md`, Makefile targets, settings, hooks and CI.
- **A setup procedure:** an agent reviews the project folder, maps what's already there, and proposes how to build the kit around it.

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
  procedures/        verify.md, session-summary.md, asking-the-human.md
  templates/         AGENTS.md, agent-kit.conf, Makefile, task, session-summary and CI templates
  scripts/           verify.sh, check-staged.sh, assert-clean.sh, install-hooks.sh, lib.sh
  githooks/          pre-commit, pre-push and a Git LFS pass-through, installed at the repo root
  environments.md    where agents run: Codespaces, local sandbox, local checkout
  environments/      local-sandbox/: push check, dev container recipe (reference copies)
  claude-code/       optional Claude Code layer: START.md, role definitions, hooks, settings
  opencode/          optional OpenCode layer: START.md, role definitions, permission settings
```

**Two choices per project.** The core kit is the same everywhere; two things vary:
- **Which agent tool.** A tool layer adds that tool's own enforcement on top of the core kit. `claude-code/START.md` adds role definitions, a hook that blocks forbidden git commands before they run, a hook that won't let the Engineer finish while `make verify` fails, and permission rules. `opencode/START.md` adds role definitions and permission rules. Setup installs the layer for the tool you use.
- **Where agents run.** `environments.md` describes the three profiles: where the agent works, where the kit's hooks are active, where you review and push, and what checks a push. Read it before setting up a local sandbox.

## Adding the kit to a project folder

You need `git`, `make` and `bash`: WSL, macOS, Linux or Codespaces.

1. Copy `_docs/agent-kit/` from your newest project into `<project>/_docs/agent-kit/`.
2. Optional: put a product spec at `<project>/_docs/specs.md`. Without one, the project starts in planning.
3. Start your AI coding tool in the project folder and say: "Set up this project using `_docs/agent-kit/setup.md`."
4. Review what it proposes, approve or correct it, then approve the setup commit.
5. Run `make hooks` once wherever agents commit: the codespace, the dev container or your local checkout. In the local sandbox profile, never run it (or any `make` target) in the clean clone; see `environments.md`.

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

Agents trigger most approval prompts in two ways: working outside the project folder (scratch files in `/tmp`, redirects to `/dev/null`, reading the tool's own settings), and shell commands too complex for the tool to check. The commonest are editing files from the shell (`sed -i`, heredoc scripts), `$?` and other shell variables, `cd … &&` chains, and settings put before a command (`VAR=x make run`). The shared Conventions list these forms and their replacements: the tool's own editor, `.scratch/` scripts, `make <target> VAR=x`, and start/stop targets for servers.

A prompt is worth stopping for when it's a real decision (a design or security choice), a protected commit, or something outside the project. For the rest, approve if the purpose is fine. If you decline, say why in a few words, such as "use the Edit tool" or "no `$?`". The agent is told never to pursue a declined goal another way, so the reason tells it what to fix.

To pre-approve routine commands in your tool, see Tool permissions in `blueprints.md`. Allow rules can't remove prompts for commands the tool can't analyse; only simpler commands can.

## Updating the kit

The kit's files are protected in every project, so changes need your approval. Improve the kit in the project you're working on, then copy the folder to other projects you're still actively working on; finished homework can keep the version it was built with. Bump the version at the top of this file when you change it.

The git hooks carry their own version number. `make hooks` upgrades an older installed version and leaves an equal or newer one alone, so projects with different kit versions can share one repository.

### Upgrading a project that already uses the kit

Agents take their rules from the project's `AGENTS.md`, not from the kit folder, so replacing the kit files isn't enough on its own. These steps fit Codespaces and a local checkout. In the local sandbox profile, follow "Upgrading the kit in the local sandbox" in `environments.md` instead.

1. Pause at a clean point: finish the current step, commit, and exit the agent session. `git status --short` should show nothing.
2. From the project folder, unzip the new kit over the old one: `unzip -o <path>/agent-kit.zip`.
3. Run `make hooks`. It upgrades older hooks and leaves current ones alone.
4. Start an agent and say: "The agent kit in `_docs/agent-kit/` has been upgraded to <version>. Review this project using `_docs/agent-kit/setup.md` in review mode. Update the shared Conventions block in `AGENTS.md` to match the template, leaving the project half unchanged, and apply any blueprint changes. Show me the diffs and the exact `git add` paths, including `_docs/agent-kit/`, and wait for my approval."
5. Review and approve, then commit the kit folder, `AGENTS.md` and any other changed files with `HUMAN_APPROVED=1`. Check that `_docs/agent-kit/` is among the staged paths. Include `.githooks/` at the repo root if `make hooks` changed it.
6. Start a fresh agent session, so the new rules load.

### Changes in 1.9

- **Environment profiles** (`environments.md`): Codespaces, local sandbox (dev container plus a clean clone) and local checkout, with where agents work, where hooks run, where you push and what checks a push. A new **Environment** setting in `AGENTS.md` tells agents which profile applies.
- **Local sandbox reference files** (`environments/local-sandbox/`): a monorepo-aware push check that finds every project the new commits change, with git alone, and runs `make -C <project> install verify` in a throwaway container that sees only a bundle of the pushed commits; the dev container recipe. Copy them only from a clean clone. `environments.md` also lists the ways a sandbox folder or clean clone can still run code on your machine, and how to avoid them.
- **Never run `make` in a clean clone.** `make hooks` also refuses there, detected by a `sandbox` remote or the push check, but that's only a convenience.
- **Repo-root protection** (pre-commit hook version 3): changes to `.github/`, `.devcontainer/`, `.vscode/`, `.envrc` and `.gitmodules` at the repo root need `HUMAN_APPROVED=1`, like `.githooks/`, including files with unusual names.
- **CI template** limits the job to `permissions: contents: read` and says never to add secrets.
- **OpenCode layer** (`opencode/`, start at `START.md`): role definitions, with PM and QA limited to writing in `.scratch/`, and permission rules. Minimal for now: no hooks.

### Changes in 1.8

- **Claude Code layer** (`claude-code/`, start at `START.md`). It replaces the separate Claude Code-only kit 1.0 used in Table Ready, and brings it fully up to date with the core kit:
  - role definitions that point to `team/`: PM and QA can't edit files, and the Engineer carries a hook that re-runs `make verify` before it can finish;
  - a git guard hook that blocks broad staging, `commit -a`, `--no-verify`, `git push` and `core.hooksPath` changes before they run;
  - settings with the allow-list, ask rules for protected files, deny rules for `.env` files and `git push`, and commit attribution.

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
