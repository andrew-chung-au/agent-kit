# Agent kit

The agent kit is a reusable, tool-agnostic process for running a software project with AI coding agents. Agents take three roles (a PM that writes up the work, an Engineer that builds it and a QA that checks it) and work from GitHub issues (one issue is one task); a verification gate (`make verify`, which runs the tests and looks for weakened ones) checks each change, and git hooks act as a safety net. It is for developers who want agents to do routine work while a human keeps the approvals, the review and every push.

This repository holds two things. One is the kit, in `agent-kit/`: Markdown instructions, shell and Python scripts, git hooks and tool settings. The other is the dev container recipe for the local sandbox profile, with the push check and the push-check image that go with it: reference copies in `agent-kit/environments/local-sandbox/`, and this repository's own working copy in `.devcontainer/`. Both are plain files. You can take the kit alone, or the kit plus the dev container.

Full details are in [agent-kit/README.md](agent-kit/README.md). The license is in [LICENSE](LICENSE) (MIT).

## Problem and design principles

A coding agent can change a lot of code quickly. Nothing in a plain repository stops it from pushing its own work, making a failing test pass by weakening the test, editing the rules it works under, or following instructions planted in an issue. The kit is a set of written rules and checks that keep a human in control at those points. Each principle below names where to see it.

- **A sandbox and human-only pushes.** A sandbox is the separate environment where the agent works. In the local sandbox profile its GitHub token can't push, so the human reviews and pushes. The other profiles rely on rules and hooks instead. See [agent-kit/environments.md](agent-kit/environments.md).
- **Separate roles.** The PM, Engineer and QA each follow their own file in `agent-kit/team/`. QA changes nothing, and `make assert-clean` checks that.
- **A gate that catches weakened tests.** `make verify` fails when a test file is deleted or a skip marker is added to one. See `agent-kit/procedures/verify.md`.
- **Git hooks as a safety net.** The pre-commit and pre-push hooks in `agent-kit/githooks/` refuse secrets and generated files, protected-file changes without the human's approval, and pushes that fail `make verify`.
- **Only approved issues, with the approved text frozen.** Agents work only on issues the human has labelled `approved`. The groomed text is recorded as a hash and re-checked with `make issue-hash` before the Engineer and QA start. See [agent-kit/process.md](agent-kit/process.md#approved-text).
- **Issue text is untrusted.** Issues can be opened by anyone, so their text describes work and never overrides the rules. See [AGENTS.md](AGENTS.md#issues).
- **Session summaries with reflection.** Each issue ends with a written summary and a short reflection from each role. See `_session-summaries/` and [agent-kit/procedures/session-summary.md](agent-kit/procedures/session-summary.md#reflection).
- **Tiers.** The human's label sets how much process a change gets. See [agent-kit/process.md](agent-kit/process.md#tiers).

## How it works

An issue moves through these steps. The orchestrator is the main agent session; it launches the roles and passes work between them.

1. **File.** An issue is filed. Issues from the PM wait unlabelled.
2. **Groom.** The PM rewrites it with acceptance criteria and records a hash of the text.
3. **Human approves.** The human reads it and adds the `approved` label. Only the human labels.
4. **Implement.** The Engineer builds it, commits, and runs `make verify`. It does not push.
5. **QA.** QA checks each criterion against the code, changes nothing, and posts PASS or FAIL.
6. **Human reviews and pushes.** The orchestrator brings every open decision to the human in one message. The human reads the diff and pushes; a push check (the pre-push hook, or the sandbox's own push check) and, where the project has it, CI run the gate again.

This is the Standard path. A Light change (a small edit to a few kit docs) gets a short PM step instead of grooming and has no QA, and a Heavy change adds an approved decision record and a second QA launch. The human's label sets the tier. The steps are defined in [agent-kit/process.md](agent-kit/process.md#lifecycle) and the tiers in [agent-kit/process.md](agent-kit/process.md#tiers).

## Evidence of quality

Each item says how to check it.

- **The test suite.** `make test` runs syntax checks, the claims check and the tests in `tests/`.
- **A claims check.** `agent-kit/scripts/check-claims.py` fails when a kit document names a make target or kit path that does not exist. `tests/test_root_readme.py` applies the same idea to this page.
- **Tests for the gates.** The files `tests/test_gate_*.py` run the real commit and push scripts against small throwaway git repositories.
- **QA mutation checks.** On some issues QA has changed a scratch copy of the code to see whether the tests notice. This is something QA has done, not a standing rule. Examples: [issue 40](_session-summaries/2026-11-01T2239Z-issue-040-orchestrator-gate-behaviour-tests.md) and [issue 45](_session-summaries/2026-11-01T2355Z-issue-045-orchestrator-github-intake-form.md).
- **Built with its own process.** See the section below.

No test counts are given here, because a number written in prose goes stale and no check would catch it. Run `make test` to see the current ones.

## Built with its own process

This repository is developed with the kit. Its closed issues (the Issues tab) and `_session-summaries/` record the work. Three summaries to start with:

- [Issue 1](_session-summaries/2026-11-01T1128Z-issue-001-orchestrator-gate-behaviour-tests.md): behaviour tests for the commit and push gates, and the bugs they exposed.
- [Issue 40](_session-summaries/2026-11-01T2239Z-issue-040-orchestrator-gate-behaviour-tests.md): tests for two more gate scripts, with QA's mutation checks.
- [Issue 45](_session-summaries/2026-11-01T2355Z-issue-045-orchestrator-github-intake-form.md): an issue form for public repositories, with QA's mutation checks.

## Install and quick start

There is no tagged release or release zip yet (issue #9 tracks it), so installing means cloning this repository and copying files out of it. You need `git`, `make` and `bash`; the container path also needs Docker on your own machine.

### Path 1: kit only

1. Clone this repository, and copy its `agent-kit/` folder into your project as `_docs/agent-kit/`.
2. Start your AI coding tool in the project folder and say: "Set up this project using `_docs/agent-kit/setup.md`." Review what it proposes, then approve or correct it.
3. Run `make hooks` wherever agents commit (not in a clean clone in the local sandbox profile).

### Path 2: kit plus dev container

This is the local sandbox profile: the agent works in a container with a token that cannot push, and you review and push from a separate clean clone. Do steps 1 and 2 of path 1 first, then:

1. From your clone of this repository (a clean clone, never a sandbox), copy `agent-kit/environments/local-sandbox/devcontainer.json` and `setup.sh` into your project's `.devcontainer/`, and `agent-kit/templates/ci-verify.yml.template` to `.github/workflows/verify.yml`. Put your git name and noreply email in `setup.sh`.
2. Open only the project's `<repo>-sandbox` folder in the container. The first build runs `make hooks` there. Commit the `.devcontainer/devcontainer-lock.json` that the first rebuild creates.
3. On your own machine, copy `agent-kit/environments/local-sandbox/pre-push` to `~/.agent-hooks/pre-push` and into each clean clone's `.git/hooks/pre-push`, and make it executable. This is the push check.
4. Optional: if your project's install step needs Node or uv, build the push-check image from `agent-kit/environments/local-sandbox/push-check.Dockerfile` and set `AGENT_PUSH_CHECK_IMAGE` to it. Without it the push check uses `python:3.12`. Run `AGENT_PUSH_CHECK_PLAN=1 git push` first to see what it would check.
5. If your checks need a database, use the Compose variant in `agent-kit/environments/local-sandbox/compose/`: copy its three files into `.devcontainer/`, next to the standard `setup.sh`.

Never run `make` in the clean clone. The reasons, the sandbox token and the exact commands are in [agent-kit/environments.md](agent-kit/environments.md#local-sandbox); the image is described under [the push-check image](agent-kit/environments.md#the-push-check-image). The steps for path 1 are written out in [agent-kit/README.md](agent-kit/README.md#adding-the-kit-to-a-project-folder); that document stays the reference.

### Installed files

Some kit files are installed outside the kit folder: the dev container recipe, the CI workflow and the push check. `agent-kit/installed-files.txt` is the map of which kit file goes where. `make kit-check` reads it, read-only, and reports each repository entry as `unchanged`, `local, ignored`, `drift` or `missing`; the two push-check entries it only names, because they live on your machine and no sandbox tool opens them. No agent copies an installed file: you do, from a clean clone. The forward import is step 7 of `agent-kit/procedures/kit-import.md`, `make kit-feedback` writes the reverse-import bundle, and comparing the installed push check is a human-only step in [agent-kit/environments.md](agent-kit/environments.md#comparing-the-installed-push-check-human-only). The map ships inside the kit folder at release.

## Where things live

This repository develops the kit, so here the kit lives at `agent-kit/`. In a project that uses it, the same folder lives at `_docs/agent-kit/`.

- `agent-kit/`: the kit itself.
- `tests/`: the tests, run by `make test`.
- `_session-summaries/`: one summary per finished issue.
- `.github/`: this repository's CI workflow and issue form.
- `_human-tasks/`: steps the human runs or checks by hand, written down before the human is asked.
- `_docs/`: this repository's own documentation index and records.
- `.devcontainer/`: this repository's own sandbox recipe, and the source of the reference copy in `agent-kit/environments/local-sandbox/`, which also holds the push check and the push-check image (`AGENT_PUSH_CHECK_IMAGE` selects the image).
- `AGENTS.md`, `agent-kit.conf` and `Makefile`: this repository's own rules, settings and commands.
- `.claude/`, `.opencode/` and `opencode.json`: the Claude Code and OpenCode settings and role definitions this repository uses.

## Limits and non-goals

- **Agents can bypass git hooks.** An agent can skip them with `--no-verify`, or set `HUMAN_APPROVED=1` itself. The instructions forbid both, so a breach is a visible rule violation, but nothing technical prevents it. The human's review is the real control, and CI is the only layer an agent cannot skip.
- **Hooks do not run for commits made on the GitHub website.**
- **One shared GitHub login.** The roles usually share one login, so GitHub cannot tell them apart or stop one role editing another's comments.
- **The push check is a quality gate, not a security gate.** Whoever controls a project's Makefile controls what `make verify` does.
- **The QA check detects changes after the fact.** `make assert-clean` does not prevent them.
- **The kit is not a security product.** It reduces the chance and the cost of mistakes; it does not contain an agent that ignores its instructions.

These limits are described in more detail in [agent-kit/README.md](agent-kit/README.md#how-the-controls-work) and [agent-kit/environments.md](agent-kit/environments.md).

## Not verified by automation

No test or CI run checks the following.

- **The push check, end to end.** `agent-kit/environments/local-sandbox/pre-push` runs on the human's machine in a throwaway Docker container. The sandbox has no Docker. `tests/test_gate_push_check.py` tests its logic with a stand-in for Docker.
- **The container build, the push-check image and the Compose variant.** Nothing here builds the dev container, builds the image, or starts the Compose stack, and the sandbox has no Docker. The Node, nvm and uv pins and the Postgres tag are unverified until someone rebuilds; they are listed in `agent-kit/environments.md`. Tests check the recipe files as text.
- **The Codespaces profile.** Issue #10 is open and marked "needs testing".
- **The OpenCode layer.** `agent-kit/opencode/` holds role definitions, permission rules and a permission-logging plugin. Its JSON is syntax-checked and some tests compare its settings as text, but no automated check runs OpenCode itself, so this README does not claim it works end to end. The human checked most of the permission rules by hand on one OpenCode version (1.19.5), with the steps in `_human-tasks/2026-11-02T1220Z-human-task-047-engineer-opencode-by-hand-checks.md`; one rule, the block on `git commit --no-verify`, is covered by tests only. The logging plugin's checks in a real session are still open under issue #20.
- **Whether the prose here is true.** `tests/test_root_readme.py` checks links, paths and make targets, not sentences. A person reads the diff.

## License

See [LICENSE](LICENSE).
