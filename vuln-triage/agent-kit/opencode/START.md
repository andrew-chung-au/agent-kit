# OpenCode layer

Start here if you run the agent kit with OpenCode. OpenCode reads `AGENTS.md` directly, so the core kit works without this layer. The layer adds OpenCode's own enforcement: role definitions and permission rules. It's deliberately minimal for now, with no hooks; see Limits.

## What it adds

| File | Installed as | What it does |
|---|---|---|
| `agents/pm.md`, `agents/software-engineer.md`, `agents/qa-engineer.md` | `.opencode/agents/` | Role definitions (subagents), each pointing to its file in `team/`. PM and QA can edit files only in `.scratch/`; OpenCode enforces that. The file name is the agent's name. |
| `opencode.json` | Merged into `opencode.json` in the project folder | Blocks reading `.env` files (but not `.env.example`); asks before edits to protected files; asks before shell commands except `make` targets and read-only git; blocks broad staging, `commit -a`, `--no-verify`, `git push` and `core.hooksPath` changes |

In OpenCode's permission rules, the last matching rule wins, so the file lists the general `*` rule first and the specific rules after it.

## Install

Setup does this when you say you use OpenCode (`setup.md`, step 4). To do it by hand, from the project folder:

1. **Start OpenCode in the project folder**, not the repository root.
2. **Role definitions:** copy the three files in `opencode/agents/` into `.opencode/agents/`.
3. **Settings:** merge `opencode/opencode.json` into the project's `opencode.json`, keeping anything already there. Then make the `edit` rules match the project's `PROTECTED` list in `agent-kit.conf`: one `"<pattern>": "ask"` entry per protected file. If the project's secrets use other names, add `read` deny rules for them.
4. **Protection:** add `'opencode.json'` and `'.opencode/*'` to `PROTECTED` in `agent-kit.conf`. These files decide what agents may do.
5. **Check it.** Restart OpenCode, then:
   - ask it to list its agents: `pm`, `software-engineer` and `qa-engineer` should appear;
   - ask it to run `git add .`: the command should be denied;
   - ask the `pm` agent to edit `README.md`: the edit should be denied.

   If a path rule doesn't match as expected, check OpenCode's permissions documentation for how it matches paths. The rules here assume paths relative to the project folder.

## Limits

- **No hooks yet.** The Claude Code layer stops the Engineer finishing while `make verify` fails; OpenCode has no such check here. The Engineer runs **Verify** because its role file says so, and the git hooks, your push check and CI catch what it misses.
- **Pattern matching only.** The git rules match how a command is written, so a variant can get past them, such as `git commit -m x -a` with the `-a` at the end. The kit's git hooks and your review still apply.
- **Settings apply only inside OpenCode.** The core kit's git hooks still cover every tool.

## Projects that already have an OpenCode setup

Setup classifies existing `.opencode/` files and `opencode.json` like any other agent setup ("Existing agent setups" in `setup.md`). Ask for the OpenCode layer in the setup prompt: "Set up this project using `_docs/agent-kit/setup.md`, including the OpenCode layer in `_docs/agent-kit/opencode/START.md`."
