# CodeBuddy layer

Start here if you run the agent kit with CodeBuddy. CodeBuddy reads `AGENTS.md`, so the core kit works without this layer. The layer adds CodeBuddy's own enforcement: permission rules, role definitions, the sweep skill and the shared git guard. It adds no `CODEBUDDY.md`.

The process, roles, verify gate and git hooks are the core kit's and apply unchanged. Nothing here replaces them.

## What it adds

| File | Installed as | What it does |
|---|---|---|
| `agents/pm.md`, `agents/software-engineer.md`, `agents/qa-engineer.md` | `.codebuddy/agents/` | Role definitions (subagents), each pointing to its file in `team/`. The PM and QA have Write but no Edit; their text limits them to `.scratch/`. The Engineer has Edit and runs Verify because its role file says so. |
| `skills/sweep/SKILL.md` | `.codebuddy/skills/sweep/SKILL.md` | The sweep skill, pointing at `procedures/sweep.md`. `disable-model-invocation: true` keeps it manual: you run `/sweep`, and the model cannot call it. |
| `settings.json` | Merged into `.codebuddy/settings.json` | Pre-approves `make` targets and read-only git; asks before edits to protected files; blocks reading `.env` files, `git push`, remote changes and `gh run view --log`; registers the shared git guard; disables bypass-permissions mode; sets no co-author line. |
| `claude-code/hooks/guard_git.py` | Runs in place from the kit | Before any Bash command: blocks broad staging, `git commit -a`/`--all`, `--no-verify`, `git commit -n`, `git push`, and changes to `core.hooksPath`, with the reason and the allowed alternative. The hook command ends with `|| exit 2`, so a crash blocks too. |

The guard is the Claude Code layer's, run from the kit. Upgrading the kit upgrades it for CodeBuddy too.

## Install

Setup does this when you say you use CodeBuddy (`setup.md`, step 4). To do it by hand, from the project folder:

1. **Start CodeBuddy in the project folder**, not the repository root. The guard is found through `CODEBUDDY_PROJECT_DIR`, which is the folder the session started in; the hook command falls back to `.` if the variable is absent.
2. **Role definitions:** copy the three files in `codebuddy/agents/` into `.codebuddy/agents/`, and `codebuddy/skills/sweep/` into `.codebuddy/skills/sweep/`.
3. **Settings:** merge `codebuddy/settings.json` into `.codebuddy/settings.json`, keeping any settings already there. Then make the `ask` list match the project's `PROTECTED` list in `agent-kit.conf`: one `Edit(<path>)` rule per entry. **CodeBuddy resolves a leading `/` relative to the settings file**, so write paths relative to the project folder: `Edit(AGENTS.md)`, not `Edit(/AGENTS.md)`. A folder pattern ending in `/*` becomes `**`, because `*` does not cross into subfolders: `_docs/agent-kit/*` becomes `Edit(_docs/agent-kit/**)`. If the project's secrets use other names, add a `Read(...)` and an `Edit(...)` deny rule for each one.
4. **Protection:** add `'.codebuddy/*'` to `PROTECTED` in `agent-kit.conf`. These files decide what agents may do.
5. **Restart CodeBuddy.** It reads settings, agents and skills at session start; a new file added by hand is not loaded in the running session.
6. **Check it.** Restart, then:
   - `/agents` lists `pm`, `software-engineer` and `qa-engineer`;
   - `/permissions` shows the rules;
   - ask it to run `git add .`: the guard blocks it with "Stage explicit paths only";
   - ask it to run `git push --dry-run`: the guard blocks it with "Don't push";
   - ask the `pm` agent to edit `README.md`: it has no Edit tool, and its text limits it to `.scratch/`. This is a tool-list and instruction limit, not a path rule; **Assert clean** after QA catches a write elsewhere;
   - `/sweep` runs the sweep skill; the model cannot call it.

## Monorepos: `memory.parentDiscovery`

CodeBuddy walks upward from the launch folder for `CODEBUDDY.md` and `AGENTS.md` by default. In a monorepo, a child project then inherits the repo root's instructions. Set `parentDiscovery` to `false` to load only the launch folder's `AGENTS.md`. The 2026-11-21 spike on 2.185.0 confirmed the key is accepted without a warning and the child loads alone.

The template leaves it out, so the default is on. For a monorepo, add this to the top-level object of `.codebuddy/settings.json` and restart:

```jsonc
// Monorepos only: load only the launch folder's AGENTS.md, not parent folders.
// "memory": {
//   "parentDiscovery": false
// }
```

Leave it out for a single project. A parent `CODEBUDDY.md` does not shadow a child `AGENTS.md`, but a `CODEBUDDY.md` in the same folder does, which is why the kit adds none.

## Permission rules

- **Bash rules are prefix matches**, not regular expressions or globs; the `:*` wildcard is only valid at the end. Use the documented colon form, `Bash(make:*)`. The space form `Bash(make *)` also worked in the 2.185.0 spike, but it is undocumented, so the template does not rely on it.
- **Deny beats ask, and ask beats allow.** A deny rule is a hard stop with no approval path.
- **`Read` and `Edit` follow gitignore semantics.** A leading `/` is relative to the settings file, not the project root; the template uses bare paths relative to the project folder, so start CodeBuddy there. A leading `//` is an absolute path, and `~/` is the home folder. `Edit` covers every built-in file-writing tool, including Write.
- **`gh run view` is not allowed**, because a prefix rule cannot exclude `--log` in the middle of the command; it asks instead. The two `--log` prefixes are denied as a backstop for the `--log`-first form.
- **These rules catch mistakes and cut prompts.** They are not a security boundary; the guard, the git hooks, the read-only token and your review are.

## Hooks and failures

The settings register the shared guard for `PreToolUse` on `Bash`. The 2.185.0 spike settled the failure behaviour:

- **Exit 0** allows the command.
- **Exit 2** blocks it and shows the message.
- **Any other non-zero exit** is a non-blocking error: stderr is shown and the command continues. The hook command ends with `|| exit 2`, so a guard crash (exit 1, 3, 127, ...) becomes 2 and blocks. The spike confirmed both a direct exit 2 and a failing hook through the wrapper.
- **Timeout:** the default is 60 seconds. A timed-out hook is terminated; if the runner kills the shell before `|| exit 2` runs, the command may continue. The guard is fast, so this is a narrow gap; the git hooks and your review still apply.
- **JSON output:** `hookSpecificOutput.permissionDecision` can allow, deny or ask, but the guard uses exit 2, so no JSON adapter is needed.
- **Frontmatter hooks:** `allowUntrustedFrontmatterHooks` defaults to `false`; the spike confirmed a subagent frontmatter `Stop` hook did not run. The layer does not enable it. `SubagentStop` fires globally with `agent_id` and `agent_type`, so a global hook can identify a subagent; a subagent cannot self-block through frontmatter.
- **Permission payloads:** `PermissionRequest` fires for an ask and carries `tool_use_id`/`call_id`; `PermissionDenied` fires for a deny rule with the same `call_id` and a `reason`. A human-rejected ask produced no `PermissionDenied`, so a log can record asks and hard denials but not the human's decision on an ask. The permission log is not part of this layer yet.

## Limits

- **No `CODEBUDDY.md`.** CodeBuddy loads a folder's `AGENTS.md` when that folder has no `CODEBUDDY.md`; adding one would shadow `AGENTS.md` in the same folder. The core `AGENTS.md` stays the single rules home.
- **No model swapping.** `STEP_UP` is Claude Code only; in CodeBuddy a step-up attempt notes that no escalated model is configured, and the patchwork guard's approach review is the only step up.
- **The role tool lists are not path rules.** The PM and QA have Write but no Edit; their text limits them to `.scratch/`. CodeBuddy's agent frontmatter has no path-specific permission, so **Assert clean** after QA and your review still catch a write elsewhere.
- **The permission log is not included yet.** The payloads above support a later logger that pairs an ask and a hard denial by `call_id`; a human-rejected ask cannot be logged as a decision.
- **The guard is a habit guard, not a security boundary.** Wrappers (`bash -c`, `xargs`, a script) and `GIT_CONFIG_*` can get past it. The read-only token, the git hooks and your review remain the boundary.
- **Hooks and rules apply only inside CodeBuddy.** The core kit's git hooks still cover every tool.

## Projects that already have a CodeBuddy setup

Setup classifies existing `.codebuddy/` files and `AGENTS.md` like any other agent setup ("Existing agent setups" in `setup.md`). Ask for the CodeBuddy layer in the setup prompt: "Set up this project using `_docs/agent-kit/setup.md`, including the CodeBuddy layer in `_docs/agent-kit/codebuddy/START.md`."

If the project already has a `CODEBUDDY.md`, do not add another. Decide with the human whether to merge its content into `AGENTS.md` and remove it, because a `CODEBUDDY.md` in the same folder shadows `AGENTS.md`.
