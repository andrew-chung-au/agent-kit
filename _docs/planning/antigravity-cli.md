# Antigravity CLI: research notes

Status: research only, 2026-11-21. No layer, no container change. The live test (does `agy` run here, does an API key authenticate, what a hook does on failure) has not been done yet; the questions are at the end.

Sources: `antigravity.google/docs/{rules,hooks,permissions,settings,subagents,skills,cli/headless,install}`, read on 2026-11-21. The vendor summary that prompted this note claims settings, permissions, skills, hooks and MCP sync bidirectionally; the docs contradict that in two places, marked below.

## What it is

`agy` is Google's terminal surface for Antigravity. Three surfaces share `~/.gemini/config/` (global agents, skills, hooks, MCP): the App, the IDE and the CLI. Each also has its own app data folder: `~/.gemini/antigravity`, `~/.gemini/antigravity-ide`, `~/.gemini/antigravity-cli`. Binary: `~/.local/bin/agy`; `agy -p` is the non-interactive form.

Installed here on 2026-11-21: 1.5.14, from the official installer, SHA512-verified against its manifest. The installer also prints that the CLI **self-updates in the background during regular runs**, so a pinned version in a container recipe would not stay pinned; pinning would need the updater disabled, which the installer does not document.

## Verified against the docs

| Area | Fact | Fit |
|---|---|---|
| Project rules | `AGENTS.md` and `GEMINI.md` per folder, cumulative, walking parents up to the repository root. Also `.agents/rules/*.md` with `trigger: always_on`, `model_decision`, `glob` or `manual`. | `AGENTS.md` works unchanged and needs no pointer file. `glob` rules are the path-scoped area rules issue #211 C4 wants. |
| Rule gotchas | A rule file in `.agents/rules/` without valid frontmatter is silently discarded; 24,000 bytes per file; a 20,000-token aggregate budget demotes the largest files to pointers. | Any rules the kit ships there must be tested, not assumed. |
| Monorepos | Parent walking is on with no documented off switch. | The opposite of CodeBuddy's `memory.parentDiscovery`. |
| Permissions | `~/.gemini/antigravity-cli/settings.json` only: `permissions.{allow,ask,deny}`, resources `command(prefix)`, `command(regex:...)`, `read_file`, `write_file`, `read_url`, `mcp`. Deny > ask > allow. | **No workspace permissions.** A layer cannot ship them in the repo; they are a human step in a home file. |
| Command matching | Token-prefix by default; `regex:` is anchored per token. Prefix matching is disabled for the whole line when the shell can hide execution (`$(...)`, backticks, brace expansion, redirections) and falls back to ask. | Closer to the kit's guard intent than CodeBuddy's plain prefix rules, but not a guard. |
| Hooks | `.agents/hooks.json` (workspace) or `~/.gemini/config/hooks.json` (global). Events `SessionStart`, `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`. Matcher is a regex on tool name; the shell tool is `run_command`. Timeout default 30 s. | Project-scoped, so a layer can ship them. |
| Hook blocking | Stdout JSON `{"decision": "deny", "reason": ...}`; also `allow`, `ask`, `auto_approve`, `force_ask`, `deny_unless_prior_grant`. `Stop` returns `{"decision": "continue"}`. **No exit-code contract is documented.** | The kit's `|| exit 2` does not apply. The guard and `verify_on_stop.py` both need a JSON adapter, and what a crashed or silent hook does is unknown. |
| Hook loading | "Hooks don't go in `settings.json`: the CLI keeps a `hooks` key there but never loads it." | Contradicts the vendor summary's sync claim. |
| Subagents | `.agents/agents/<name>.md` or `.agents/agents/<name>/agent.md`; frontmatter `name`, `description`, `tools`, `mainAgent`, `subagent`, `model`, `commandExecutionPolicy`, `mcpServers`, `skills`. Invoked with `invoke_subagent`, `@name:` or the `/agents` panel. | Role definitions work, but `tools` uses Antigravity names (`view_file`, `replace_file_content`, `grep_search`, `run_command`), and a misspelled tool name can hang the subagent. |
| Skills | `.agents/skills/<name>/SKILL.md`; only `name` and `description` are documented. Any skill becomes a slash command. | **No `disable-model-invocation`.** The sweep skill cannot be kept manual, so it conflicts with the kit's "only the human runs it" rule. |
| Headless | `agy -p`, `--output-format text|json|stream-json`, `--json-schema`, `--sandbox`, `--agent`, `--mode`; CLI exit codes 0/1/2. | Usable for QA, but actions that cannot be approved are soft-denied and the run still exits 0. |
| Auth | API key: `modelProvider: "gemini"` in `~/.gemini/antigravity-cli/settings.json` plus `GEMINI_API_KEY` in the environment (the only source it reads). Personal Google account: browser or, over SSH, a printed URL plus a code. | API-key mode is the headless path and needs no browser. |

## What a layer would look like

- `AGENTS.md` is the always-loaded rules home, as for CodeBuddy; no pointer file and no `AGENTS.md` copy.
- `.agents/agents/{pm,qa-engineer,software-engineer}.md` as role definitions, with Antigravity tool names.
- `.agents/hooks.json` with a `PreToolUse` hook on `run_command`, calling a small adapter that translates Antigravity's `toolCall` payload to the guard's input and its block to `{"decision": "deny", "reason": ...}`. `Stop` gets a similar adapter for `make verify`.
- No `.agents/skills/sweep/`: the model can invoke it, which breaks the sweep rule. Leave the sweep out, or accept a model-invocable skill and say so.
- Permissions: a documented human step editing `~/.gemini/antigravity-cli/settings.json`, not an installed file. That makes it like the push check (`human-machine`), and it cannot be byte-compared.
- No workspace settings file exists, so `installed-files.txt` gets lines only for the agents, the hook adapter and any rules file; the permission rules stay off the map.

## Open questions for the live test

1. Does `agy -p` run in this dev container with `GEMINI_API_KEY` and `modelProvider: "gemini"`, and what does it print when the key is absent or invalid?
2. Does a `PreToolUse` hook on `run_command` returning `{"decision": "deny"}` block a `git add .`?
3. What does the same hook do when it exits 1, exits 2, prints nothing, or prints malformed JSON? (The docs are silent; this decides whether an adapter can fail closed.)
4. What happens at the 30 s timeout: is the command allowed or blocked?
5. Do `command(...)` rules in the global settings apply to `run_command` arguments, and does a `command(git push)` deny stop a push?
6. Does a subagent in `.agents/agents/` appear in `/agents`, launch by `@name:`, and hang on a wrong tool name?
7. Can the model invoke a workspace skill without being asked?
8. In headless mode, does an ask that cannot be answered really soft-deny with exit 0?

## Recommendation

Spike first, then decide. If only the container install is wanted, install a pinned version in `setup.sh` rather than piping an unpinned script at build time, and leave authentication to the human. A full layer is a 1.11-sized change and needs an approved issue; the guard adapter and the missing manual-skill control are the two design decisions to settle first.
