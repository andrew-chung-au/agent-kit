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

There is no tagged release or release zip yet (issue #9 tracks it), so installing means cloning this repository and copying files out of it. Every install and upgrade path (a new project, an existing repo, with or without the dev container, a Codespace or a local checkout) is written out step by step in [agent-kit/install-and-upgrade.md](agent-kit/install-and-upgrade.md): pick your situation there. The release steps are in [agent-kit/releasing.md](agent-kit/releasing.md), and what changed in each version is in [agent-kit/CHANGELOG.md](agent-kit/CHANGELOG.md).

Never run `make` in a clean clone. The reasons and the sandbox rules are in [agent-kit/environments.md](agent-kit/environments.md#local-sandbox); the sandbox token and the push-check image are in [agent-kit/environments/local-sandbox/README.md](agent-kit/environments/local-sandbox/README.md).

Some kit files are installed outside the kit folder (the dev container recipe, the CI workflow and the push check). `make kit-check` reports whether each still matches; the map and the rules are under "Installed files" in [agent-kit/README.md](agent-kit/README.md#updating-the-kit).

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
