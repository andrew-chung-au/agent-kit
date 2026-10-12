# Claude Code layer

Start here if you run the agent kit with Claude Code. The core kit works with any AI coding tool, but it can only ask agents to follow its rules; the git hooks catch problems at commit and push. This layer adds Claude Code's own enforcement on top, so the same rules are checked before a command runs or an agent finishes.

The process, roles, verify gate and git hooks are the core kit's and apply unchanged. Nothing here replaces them.

## What it adds

| File | Installed as | What it does |
|---|---|---|
| `CLAUDE.md.template` | `CLAUDE.md` in the project folder | Loads `AGENTS.md`, and points Claude Code's scratch files at `.scratch/` |
| `agents/pm.md`, `agents/software-engineer.md`, `agents/qa-engineer.md` | `.claude/agents/` | Role definitions, so the orchestrator launches each role by name. Each points to its file in `team/`. PM and QA can't edit files; they write only to `.scratch/`. The Engineer carries the verify hook. |
| `hooks/guard_git.py` | Runs in place from the kit | Before any shell command: blocks `git add .`/`-A`/`-u`, `git commit -a`, `--no-verify`, `git commit -n`, `git push` and changes to `core.hooksPath`, with the reason and the allowed alternative |
| `hooks/verify_on_stop.py` | Runs in place from the kit | When the Engineer tries to finish: runs `make verify` and sends it back to fix any failure, up to three times, then lets it stop and warns you |
| `settings.json` | Merged into `.claude/settings.json` | Pre-approves `make` targets and read-only git; asks before edits to protected files; blocks reading `.env` files and `git push`; registers the git guard; sets commit attribution |

The hooks run from `_docs/agent-kit/claude-code/hooks/`, so upgrading the kit upgrades them too.

## Install

Setup does this when you say you use Claude Code (`setup.md`, step 4). To do it by hand, from the project folder:

1. **Start Claude Code in the project folder**, not the repository root. The hooks find the kit through `$CLAUDE_PROJECT_DIR`, which is the folder the session started in.
2. **`CLAUDE.md`:** copy `claude-code/CLAUDE.md.template` as `CLAUDE.md`, or merge its two lines into an existing `CLAUDE.md`.
3. **Role definitions:** copy the three files in `claude-code/agents/` into `.claude/agents/`.
4. **Settings:** merge `claude-code/settings.json` into `.claude/settings.json`, keeping any settings already there. Then make the `ask` list match the project's `PROTECTED` list in `agent-kit.conf`: one `Edit(/<pattern>)` rule per entry. For example, `incident-response/probe.py` becomes `Edit(/incident-response/probe.py)`. A folder pattern ending in `/*` becomes `/**`, because in these rules `*` doesn't cross into subfolders: `_docs/agent-kit/*` becomes `Edit(/_docs/agent-kit/**)`. If the project's secrets use other names, add a `Read(...)` deny rule for each one.
5. **Protection:** add `'.claude/*'` to `PROTECTED` in `agent-kit.conf`. These files decide what agents may do.
6. **Check it.** Restart Claude Code and accept the workspace trust prompt; the Engineer's hook only runs in a trusted folder. Then check:
   - `/agents` lists `pm`, `software-engineer` and `qa-engineer`;
   - `/hooks` lists the git guard;
   - `/permissions` shows the rules.

   To test the guard, ask Claude to run `git add .`. It should be blocked with the message "Stage explicit paths only".

## Limits

- The hooks and rules apply only inside Claude Code. The core kit's git hooks still cover every tool, and your review of the diff is still the real control.
- Rules and the git guard match the commands Claude usually writes. They aren't a security boundary: a command written another way can get past them. For example, a push run through a script. The git hooks and your review catch what gets past.
- PM and QA have the Write tool so they can use `.scratch/`. Nothing enforces that they write only there; **Assert clean** after QA catches any change to the project's files.

## Projects that already have a Claude Code setup

Nothing here is version-specific. If the project already has its own Claude Code setup (subagents, skills, hooks, settings, an older kit), setup works out what each piece does and compares it with this layer and the core kit, following "Existing agent setups" in `setup.md`.

1. Pause at a clean point and exit Claude Code. `git status --short` should show nothing.
2. Copy or unzip the kit into the project folder.
3. Start Claude Code and say: "Set up this project using `_docs/agent-kit/setup.md`, including the Claude Code layer in `_docs/agent-kit/claude-code/START.md`. Show me every diff and the exact `git add` paths, and wait for my approval."
4. In the proposal, check that every existing agent file is accounted for (kept, merged, superseded or out of scope), with a reason, and that project-specific content is carried over rather than lost.
5. Approve, commit with `HUMAN_APPROVED=1`, run `make hooks`, and start a fresh session.
