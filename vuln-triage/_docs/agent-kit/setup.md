# Set up or review a project with the agent kit

Run by an AI coding agent, from the project folder: the folder containing `_docs/agent-kit/`. The human starts it with: "Set up this project using `_docs/agent-kit/setup.md`."

- **Adopt mode:** the folder has no `agent-kit.conf` yet. Setup maps what's there and builds the kit around it.
- **Review mode:** `agent-kit.conf` exists. Setup checks the project against `blueprints.md` and proposes what's missing, now applicable or out of date.

Propose everything before changing anything. Never delete or overwrite existing files.

## 1. Locate

- The project folder is the current folder. Find the repository root with `git rev-parse --show-toplevel`.
- If they differ, the repo is a monorepo. Other folders at the root belong to other projects: read nothing there except repo-root git config and `.githooks/`, and change nothing there except `.githooks/` and, if the human asks for CI, `.github/workflows/`.

## 2. Inventory (read only)

List what exists, with evidence from the files themselves, not assumptions:

- **Instructions:** `AGENTS.md`, `CLAUDE.md` and other tool instruction files, including nested ones such as `frontend/AGENTS.md`, and tool role definitions such as `.claude/agents/`.
- **Process docs:** process files, role files, task templates, prompt collections.
- **Spec:** `_docs/specs.md`, or wherever the product description lives.
- **Session summaries:** the folder and its naming scheme.
- **Build and test:** Makefile targets, package managers and lock files, test frameworks and test layout, e2e tests, migrations, linters and type checkers, containers.
- **Git:** `.gitignore` coverage, `git config core.hooksPath`, any hooks in `.git/hooks`, CI files and whether they're at the repo root.

## 3. Classify

For each existing item, choose one:

- **Keep:** stays as is. Course material, prompts and history usually belong here.
- **Merge:** its content moves into a kit file. For example, an existing `AGENTS.md` becomes the project half of the new one.
- **Superseded:** the kit replaces it, for example old process or role files. Propose moving it to `_docs/archive/`; the human decides.
- **Out of scope:** unrelated to the kit; leave it alone.

**Existing agent setups.** The project may already have its own way of running agents: an older version of this kit, another kit, or tool-specific files such as subagents, skills, hooks, permission settings or instruction files. Don't rely on names or version numbers. Read each piece and work out what it does, then compare it with what the kit provides:
- **Does the same job as a kit component** (a verify script, a role definition, a hook that blocks `git add .`): Superseded. Name the kit component that replaces it, and check that nothing it did is lost.
- **Holds project-specific content** (commands, gotchas, settings, permission rules for project files): Merge it into the matching kit file, usually the project half of `AGENTS.md` or the layer's settings.
- **Does something the kit doesn't** (a project-specific skill, an extra check): Keep it. Say how it fits alongside the kit, and if it seems generally useful, suggest it as a kit improvement.
- **Conflicts with the kit's rules** (a hook or setting that allows what the Conventions forbid): flag it as a question for the human.

## 4. Match against the blueprints

For every row in `blueprints.md`, record **now**, **later** (with its trigger) or **not applicable**, and the evidence. In review mode, also report drift:

- A shared Conventions block in `AGENTS.md` that differs from `templates/AGENTS.md.template`.
- Command slots in `AGENTS.md` that don't match Makefile targets.
- A long-running process (a server, a watcher) without `<name>-start` and `<name>-stop` targets.
- Hooks not active in this clone (`git config core.hooksPath` isn't `.githooks`).
- A newer kit hook version than the one installed at the repo root.
- `LINT_CMD`/`TYPECHECK_CMD` still empty although the lint or type-check target now passes.

**Tool layers.** Find out which AI coding tools the human uses: from `CLAUDE.md`, `.claude/`, `opencode.json` or `.opencode/`, or ask. For Claude Code, include the files from `claude-code/START.md` (Install, steps 2 to 5) in the proposal, with the `ask` rules matched to `PROTECTED`. For OpenCode, do the same from `opencode/START.md` (Install, steps 2 to 4).

**Environment.** Find out which profile in `environments.md` applies, from a `.devcontainer/` folder, a codespace, or by asking, and fill in the **Environment** setting in `AGENTS.md`, including what isn't available there (for example Docker in the local sandbox). For the local sandbox, also propose adding `.devcontainer/` and `.github/` at the repo root if they're missing, from `environments/local-sandbox/` and `templates/ci-verify.yml.template`; the human copies them in the clean clone. Existing `.claude/` files are classified like any other agent setup (step 3).

## 5. Propose and wait

Show the human, in one message:

1. The classification table from step 3.
2. The blueprint table from step 4.
3. Diffs for every file to be created or changed: `AGENTS.md`, `agent-kit.conf`, Makefile additions, `.gitignore` additions, pointer files, archive moves.
4. Anything you guessed or couldn't determine, each as a question for the human. Their answers replace the guesses; never commit a guess marked "confirm" or "observed".

Wait for approval. Apply only what the human approves.

## 6. Apply and check

1. Create and merge the approved files.
2. Run `make hooks`. If it refuses because of an existing hooks setup, stop and show the human its message.
3. Run `make help`, then `make verify`, and report both results as the **baseline**.
4. If the baseline fails on existing code, don't fix the code and don't weaken the gate. Report the failure and propose issues for it, which the PM files through the normal process.

## 7. Commit and hand over

- The setup commit touches protected files (`AGENTS.md`, `agent-kit.conf`, the kit, `.githooks/`), so it needs the human's approval. Show the exact `git add` paths, and commit with `HUMAN_APPROVED=1` only after the human approves the commit.
- Tell the human where `make hooks` needs running once: each codespace, dev container or local checkout where agents commit, and never a clean clone (`environments.md`).
- If the Claude Code layer was installed, tell the human to restart Claude Code, accept the workspace trust prompt, and run the checks in `claude-code/START.md` (Install, step 6).
- Hand over with the next step from `process.md`: planning if there's no spec, otherwise building or reviewing the backlog.

Done when:

- `make help` lists the core targets.
- Every command slot in `AGENTS.md` is a make target or "none".
- `git config core.hooksPath` is `.githooks`.
- The baseline `make verify` result is reported, with issues proposed for any failures.
- No placeholders (`<...>`) or unconfirmed notes remain in the project half of `AGENTS.md`. The shared Conventions block keeps its generic examples, such as `make <target> VAR=value`.
