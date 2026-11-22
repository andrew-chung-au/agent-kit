# Antigravity CLI layer

Start here if you run the agent kit with Google's Antigravity CLI (`agy`). Antigravity reads `AGENTS.md` directly and walks ancestor folders up to the checkout root, so the core kit works without this layer. The layer adds Antigravity's own enforcement: role definitions (subagents), the shared git guard through a `PreToolUse` hook adapter, and documented global permission settings. It adds no separate rules copy or pointer file.

The process, roles, verify gate and git hooks are the core kit's and apply unchanged. Nothing here replaces them.

## What it adds

| File | Installed as | What it does |
|---|---|---|
| `agents/pm.md`, `agents/software-engineer.md`, `agents/qa-engineer.md` | `.agents/agents/` | Role definitions (subagents), each pointing to its file in `team/`. The PM and QA have `write_file` but no `replace_file_content`; their text limits them to `.scratch/`. The Engineer has `replace_file_content` and runs Verify because its role file says so. |
| `hooks.json` | Merged into `.agents/hooks.json` | Registers the `PreToolUse` hook on `run_command` calling the git guard adapter. |
| `antigravity/guard_adapter.py` | Runs in place from the kit | Translates Antigravity's `run_command` payload into the shared git guard's input and returns `{"decision": "deny", "reason": ...}` when the guard blocks, or `{"decision": "allow"}` when it allows. |

The guard is the shared git guard from `claude-code/hooks/guard_git.py`, run through the adapter in place from the kit. Upgrading the kit upgrades both for Antigravity too.

## Install

Setup does this when you say you use Antigravity CLI (`setup.md`, step 4). To do it by hand, from the project folder:

1. **Start Antigravity in the project folder.** Antigravity loads `AGENTS.md` from the current working directory and walks parent folders up to the repository root.
2. **Role definitions:** copy the three files in `antigravity/agents/` into `.agents/agents/`.
3. **Hooks:** merge `antigravity/hooks.json` into `.agents/hooks.json`, keeping any hooks already there. The command it adds is `python3 _docs/agent-kit/antigravity/guard_adapter.py`, a path relative to the project folder. Antigravity does not document the working directory a hook command runs in, so start `agy` in the project folder and let step 6 confirm the path resolves.
4. **Global permissions (human step):** Antigravity reads permissions only from the global file `~/.gemini/antigravity-cli/settings.json`, so permissions cannot ship in the repository and cannot be byte-compared. Follow the documented human step below or run the task in `_human-tasks/`.
5. **Protection:** add `'.agents/*'` to `PROTECTED` in `agent-kit.conf`. These files configure subagents and hooks.
6. **Restart Antigravity.** Check that:
   - `/agents` lists `pm`, `software-engineer` and `qa-engineer`;
   - ask it to run `git add .`: the guard blocks it with "Stage explicit paths only";
   - ask it to run `git push --dry-run`: the guard blocks it with "Don't push";
   - ask the `pm` agent to edit a file outside `.scratch/`: it has no `replace_file_content` tool, and its text limits it to `.scratch/`.

   If instead every command is blocked and the reason says the hook command failed, the adapter path did not resolve: start `agy` in the project folder, or write the adapter's absolute path into `.agents/hooks.json`.

## Instruction files and parent directory walking

Antigravity discovers `AGENTS.md` and `GEMINI.md` hierarchically by walking upward from the current working directory to the repository root. All ancestor instruction files are cumulative and loaded into context automatically. There is nothing to install for project rules: no pointer file, no copy, and no workspace configuration needed to enable `AGENTS.md`.

Unlike CodeBuddy, Antigravity has no documented setting to disable parent directory walking in monorepos. All instructions up to the checkout root are always active.

## Global permission rules

Antigravity CLI reads permission rules strictly from `~/.gemini/antigravity-cli/settings.json`, never from workspace files. Because they sit outside the repository on the human's machine, they are a documented human step, the way the local sandbox push check is, and cannot be byte-compared by `make kit-check`.

The documented configuration in `~/.gemini/antigravity-cli/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "command(make)",
      "command(git status)",
      "command(git diff)",
      "command(git log)",
      "command(git show)",
      "command(git cat-file)",
      "command(git remote)",
      "command(sha256sum)",
      "command(gh issue view)",
      "command(gh issue list)",
      "command(gh run list)"
    ],
    "ask": [
      "command(gh issue create)",
      "command(gh issue comment)",
      "command(gh issue edit)",
      "command(gh issue close)",
      "command(gh api)"
    ],
    "deny": [
      "read_file(.env)",
      "read_file(.env.local)",
      "read_file(.env.*.local)",
      "command(git push)"
    ]
  }
}
```

- **Command matching is token-prefix by default.** Prefix matching is automatically disabled when a command uses shell constructs that can hide execution (`$(...)`, backticks, brace expansion, redirections) and falls back to asking.
- **Deny beats ask, and ask beats allow.** A deny rule is a hard stop with no approval path.
- **A `read_file` deny also denies writing that path**, so one rule per dotenv name covers both reading and writing it. `read_file` and `write_file` targets are absolute paths, folders, or paths relative to a workspace root, and a folder grants its whole tree.
- **These rules catch routine prompts.** They are not a security boundary; the git guard hook, git hooks, the read-only token and your review are.

## Hooks and failures

The settings in `.agents/hooks.json` register the PreToolUse adapter on `run_command`. The 2026-11-21 live measurements settled the hook failure behaviour:

- **JSON deny blocks:** `{"decision": "deny", "reason": ...}` immediately blocks the tool call and displays the reason.
- **Exit 1 blocks:** a non-zero exit from the hook command fails closed.
- **Timeout blocks:** execution terminates at 30 seconds and blocks.
- **Malformed JSON blocks:** invalid JSON fails closed (`failed to unmarshal result from hook ... via protojson`).
- **Exit 0 with no output ALLOWS:** a hook that exits 0 silently without printing JSON fails open. The adapter therefore emits an explicit JSON decision on every path, including its own error paths, and never exits 0 silently.
- **The adapter finds the kit from its own file, then the payload.** It looks beside `guard_adapter.py` first, then under `workspacePaths`, `toolCall.args.Cwd` and `cwd`, which the docs and the spike payload each provide. If none resolves, it denies with a reason rather than allowing.
- **`--dangerously-skip-permissions` does not bypass hooks:** hooks run and enforce decisions regardless of whether the permission prompt bypass flag is set.
- **Headless mode soft-denies:** when running `agy -p`, blocked commands soft-deny with a denial explanation in the response body while the CLI process exits 0. Pipelines and test scripts must inspect the response payload rather than relying on the process exit code as a verdict.

## Limits

- **No permissions file in the repository.** Permissions are configured exclusively in `~/.gemini/antigravity-cli/settings.json`.
- **No sweep skill.** Antigravity skills (`.agents/skills/<name>/SKILL.md`) are model-invocable and lack a `disable-model-invocation` setting. In the spike, an uninvoked skill read its own `SKILL.md` and ran shell commands autonomously, breaking the kit's sweep rule ("only the human runs it"). The sweep skill is therefore intentionally omitted. Run the sweep manually following `procedures/sweep.md`.
- **Role tool lists are not path rules.** The PM and QA have `write_file` but no `replace_file_content`; their text limits them to `.scratch/`. Antigravity's agent frontmatter has no path-specific write restrictions, so **Assert clean** after QA and your review remain the check. A tool name the CLI does not recognise makes the subagent hang instead of failing, so the step 6 check that `/agents` loads and the `pm` agent answers is what confirms the list.
- **The guard is a habit guard, not a security boundary.** Wrappers (`bash -c`, `xargs`, a script) and `GIT_CONFIG_*` can bypass it. The read-only token, git hooks and your review remain the boundary.
- **Hooks and rules apply only inside Antigravity CLI.** The core kit's git hooks still cover every tool.

## Projects that already have an Antigravity setup

Setup classifies existing `.agents/` files like any other agent setup ("Existing agent setups" in `setup.md`). Ask for the Antigravity layer in the setup prompt: "Set up this project using `_docs/agent-kit/setup.md`, including the Antigravity CLI layer in `_docs/agent-kit/antigravity/START.md`."

Existing rules in `.agents/rules/` are preserved if they don't contradict `AGENTS.md`. Existing hooks in `.agents/hooks.json` are merged with the git guard hook.
