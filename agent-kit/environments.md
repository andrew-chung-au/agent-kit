# Environments

The kit's rules are the same wherever agents run. What changes is:
- where the agent works;
- where the kit's git hooks are active;
- where you review and push;
- what checks a push before it reaches GitHub.

There are two separate choices:
- **Which agent tool:** the core kit works with any tool that reads `AGENTS.md`. A tool layer adds that tool's own enforcement: `claude-code/` or `opencode/`.
- **Where it runs:** one of the three profiles below. Record it in the **Environment** setting in `AGENTS.md`, so agents know what's available to them.

| | Codespaces | Local sandbox | Local, no sandbox |
|---|---|---|---|
| Agent works in | The codespace | A dev container, in the `<repo>-sandbox` folder | Your own checkout |
| You review and push from | The same codespace | A separate clean clone, `<repo>` | The same checkout |
| Kit's git hooks (`make hooks`) | In the codespace | In the container only | In the checkout |
| What checks a push | The kit's pre-push hook, then CI | Your push check (`environments/local-sandbox/pre-push`) in a throwaway container, then CI | The kit's pre-push hook, then CI |
| Can the agent push? | Yes: the codespace's GitHub token can. Only the rules and hooks stop it | No: its token has read-only code access | Yes: it can use your login |
| Docker | Available | Not available | Available |
| Best for | Projects that need Docker (Compose stacks, databases) | Everything else | Quick experiments only |

## Codespaces

This is the kit as the README describes it. Run `make hooks` once per codespace. The kit's pre-push hook runs `make verify` before you push, and the optional CI workflow runs it again on GitHub.

The codespace's own token can push to the repo, so nothing technical stops an agent pushing; the rules and the Claude Code layer's git guard ask it not to. Your review before pushing is the real control. Codespaces stop after a period of inactivity, even while an agent is working.

## Local sandbox

The agent works in a dev container with a GitHub token that can't push, in its own clone of the repo. You review its commits from a second, clean clone that is never opened in the container, and push from there. The guide that sets this up lives outside the kit. The kit supplies reference copies of its files in `environments/local-sandbox/`:

| File | Installed as | Notes |
|---|---|---|
| `pre-push` | `~/.agent-hooks/pre-push`, copied into each clean clone's `.git/hooks/pre-push` | The push check. Monorepo-aware: it finds every project the new commits change, using git only, then runs `make -C <project> install verify` for each in a throwaway container. The container sees only a bundle of the pushed commits: no ignored files, git settings or other branches. It blocks the push if a project's `agent-kit.conf` was removed. Never run it from the repo. |
| `devcontainer.json`, `setup.sh` | `.devcontainer/` at the repo root | The container recipe. Fill in your name and noreply email in `setup.sh`. |
| `templates/ci-verify.yml.template` | `.github/workflows/` at the repo root | CI with `permissions: contents: read` and no secrets |

**Copy these files only from a clean clone, never from a sandbox.** An agent can change anything in its sandbox, including the kit.

### The sandbox token

As the human stated it from the token settings (2026-11-02): repository permissions are read access to code and metadata, and read and write access to issues; no user permissions. Whether the token is scoped to a single repository is not verified; scope it to one repository. Git credentials come from a credential helper rather than the remote URL. You set the token in your GitHub account's token settings; agents never print or read it.

**Limit:** with issues write, the token can also edit or close issues and add labels, including `approved`. The `AGENTS.md` rule that agents never add that label is a text rule the token does not enforce. So OpenCode's `gh issue edit*`, `gh issue close*` and `gh api*` stay at ask, and a scanned `make` target is the structured way to write issues.

With no Docker, the sandbox can't run the push check end to end; it runs on your machine.

### Rules for the local sandbox

- **Never run `make` in a clean clone.** That includes `make hooks`, `make verify` and `make test`. The Makefile is repo code that an agent may have changed, and in a clean clone it would run on your machine with your login. `make hooks` refuses in a clean clone (it spots the `sandbox` remote or the push check), but that's only a convenience: by the time it refuses, `make` has already run.
- **Run `make hooks` in the container only.** `setup.sh` does it on the first build. Run it again in the container after a kit upgrade.
- **The kit's pre-push hook never fires here.** The agent can't push, and the clean clone doesn't use the kit's hooks. Your push check and CI do that job.
- **Protected changes are committed in the container,** with `HUMAN_APPROVED=1`, after your approval. Never commit in the sandbox folder from Ubuntu.
- **The kit's pre-commit hook asks for approval on repo-root `.github/` and `.devcontainer/` changes**, as well as `.githooks/`. An agent can set `HUMAN_APPROVED=1` itself, so your review of the diff is still the real check.
- **Pushing:** instead of the README's "read the diff, then push", fetch the sandbox's commits into the clean clone, read the full diff, merge and push from there. The push check runs automatically. The commands, step by step, are in `_human-tasks/2026-11-02T1220Z-human-task-engineer-push-review-from-clean-clone.md`; this file keeps the reasons.
- **The push check is a quality gate, not a security gate.** Whoever controls a project's Makefile controls what `verify` does, so an agent could make it pass. It proves the tests pass; your review of the diff is what proves the change is safe.
- **From Ubuntu, touch the sandbox folder only with `git fetch sandbox`, run from the clean clone.** The sandbox folder is shared with the container, so the agent can change files there without committing them:
  - `.devcontainer/`: an `initializeCommand` runs on your machine at the next rebuild, and extra mounts can expose your files to the container. Compare the recipe with the clean clone's before every open or rebuild.
  - `.git/config`: some settings run commands whenever git works in that folder.

  Keep git on your machine up to date, because fetching from a local folder has had security fixes.
- **Open the clean clone in VS Code's Restricted Mode,** and don't let direnv or mise load settings there. `.vscode/tasks.json`, `.envrc` and `mise.toml` can run commands when a folder opens. The pre-commit hook asks for approval when an agent changes `.vscode/`, `.envrc` or `.gitmodules` at the repo root, but your review is what catches them.
- **One Claude login volume per repo is safer.** The reference recipe shares one `claude-config` volume across all sandboxes, so an agent in one sandbox could change Claude settings that every other sandbox uses. Naming the volume `claude-config-${devcontainerId}` gives each repo its own; you then log in once per repo.
- **Docker isn't available in the container.** A project whose checks need Docker can't run them there, and running them from Ubuntu would run agent code outside the sandbox. Either put that project in a codespace, or give it a Compose-based container recipe, so its services run as separate containers that the agent can reach but can't control.

### Upgrading the kit in the local sandbox

The container reviews and commits the new kit; you fetch the result and push, as in `procedures/kit-import.md`. The new kit is untrusted data until you have read its diff.

1. **Drop the zip into the container.** In the dev container's VS Code window, drop the new kit zip into the workspace's `.scratch/`. Don't copy it in from Ubuntu's file manager or a terminal on your machine: that would break the rule above about touching the sandbox folder from Ubuntu.
2. **The agent unpacks and reviews it in the container.** It unpacks the zip into a new, empty folder under `.scratch/`, never over the kit folder or into the clean clone, and follows `procedures/kit-import.md`. `make kit-check` and `make kit-compare` run in the container. Read the agent's list of every file and its outcome before anything is staged.
3. **The agent commits in the container, after your approval.** It stages explicit paths and sends you the approval request with `git diff --cached --stat`. The kit folder is protected, so it commits with `HUMAN_APPROVED=1` only after you approve. Then the agent runs `make hooks` in the container.
4. **Give the agent the README's upgrade prompt** for the `AGENTS.md` and blueprint changes. Its commits wait for your approval in the same way.
5. **Fetch and push from the clean clone.** Run `git fetch sandbox`, read the full diff, then merge and push, as in "Pushing" above. Don't run `make` in the clean clone.

If the new kit changes `environments/local-sandbox/pre-push`, copy it from the clean clone, after the fetch and merge, to `~/.agent-hooks/pre-push` and refresh each clean clone's copy. Never copy it from the container's `.scratch/` copy. These steps don't touch `.devcontainer/` or the CI template.

## Local, no sandbox

The agent runs in your own checkout, with your login and files within its reach. The kit works exactly as in Codespaces: run `make hooks` once, and the kit's pre-push hook checks your pushes. Use this profile only for quick experiments. For real work, use the local sandbox.
