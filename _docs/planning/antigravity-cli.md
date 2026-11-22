# Antigravity CLI: research notes

Status: the layer is written under issue #221 (`agent-kit/antigravity/`), from the 2026-11-21 spike. No container change. The questions that remain are at the end.

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

## Credential proxy: the request shape, verified

`agy` 1.5.14 sends the key in the `x-goog-api-key` header and appends the version path itself. With `GOOGLE_GEMINI_BASE_URL=http://127.0.0.1:8799` and a dummy `GEMINI_API_KEY`, a local echo server received:

```
POST /v1beta/models/gemini-3.1-pro-preview:streamGenerateContent?alt=sse
x-goog-api-key: dummy-key-for-header-test
```

So a credential-injecting proxy that overwrites `x-goog-api-key` works with this build, and `modelProvider: "gemini"` is still required for the key path. Two consequences: the proxy must stream rather than buffer, which Caddy's `reverse_proxy` already does (its `flush_interval` defaults to `-1`), and a proxy that binds `:port` listens on every interface, so it needs a container-facing bind and a source restriction. A dummy key is enough to start the CLI; the proxy replaces it in flight.

The pattern is a capability boundary, not a data boundary: the agent can still spend quota and can still send repository content to the model through the proxy. If the key's project has billing linked, cap the spend; on the free tier there is nothing to cap, because the quota is the limit and the failure is a 429. Treat the proxy as reachable by anything that can route to it.

### Where the proxy can live in a dev container

Verified in this dev container on 2026-11-21: it runs under Docker Desktop, so it is `172.17.0.2/16` behind `172.17.0.1` inside the Docker Desktop VM; `host.docker.internal` resolves to `192.168.65.254`, the VM's route to Windows; and a Caddy listener on the WSL host's `0.0.0.0:8787` answers at neither address, both refusing in 0 ms. The container, the WSL distro and Windows are three network namespaces here, and nothing in the VM routes to WSL.

So a proxy in WSL is not reachable from this container at all. The workable forms are a proxy container joined to the dev container with `--network container:<name>`, which puts it on the container's own `127.0.0.1` and exposes nothing, or a proxy on the Windows side, which `host.docker.internal` does reach but which has to be configured from PowerShell. The sidecar form is also the shape a layer would ship: it shares the network namespace, so the agent can send requests to it, while its process namespace and the absent Docker socket keep its environment out of the agent's reach.

## Billing and quota: three systems

- **Antigravity Starter Quota** (no sign-in, no key): measured here on 2026-11-21. `agy` 1.5.14 started with no auth prompt, the header read `(Antigravity Starter Quota)` with the model `Gemini 3.8 Flash (High)`, and a one-line prompt answered `OK` with nothing credential-like in the container's environment. `/usage` lists two groups, each with a weekly limit consumed in proportion to token cost: Gemini 3.8 Flash at 99.26% remaining and refreshing in about 168 hours, and Claude Sonnet 4.6, Claude Opus 4.6 and GPT-OSS 120B at 100%. This path therefore needs no credential at all, which makes the proxy unnecessary for it; the proxy stays relevant only where an API key is used.
- **Free-tier API key** (a project with no billing account): hard RPM/TPM/RPD limits, applied per project rather than per key, with RPD resetting at midnight Pacific. Exhaustion is a 429 and nothing can be charged. Measured here: `gemini-3.1-pro` returns `429` with `limit: 0` on the per-minute metric as well as the daily ones, and a per-minute allowance of zero cannot be exhausted by usage, so that model is not available to this project on the free tier rather than merely used up. Some models are "Free: Not supported" on the rate-limits page for the same reason; `agy` defaults to `gemini-3.1-pro` on this path. Google's terms for the free tier allow prompts to be used to improve its products, so check the current terms before sending repository content.
- **Google account subscription** (OAuth sign-in): five-hour and weekly usage windows, with optional overage credits. Exhaustion stops the session unless overage is enabled. The credential is a session token in the container, so this route conflicts with keeping credentials out of the container; the proxy pattern injects an API-key header and does not help with an OAuth session.

A second key in the same project does not add quota, because the limits are per project.

## Measured in this container, 2026-11-21

Run from the fixture in `.scratch/agy-spike/`, on `agy` 1.5.14, on the starter quota; the step-by-step record is in `_human-tasks/2026-11-21T1524Z-human-task-engineer-antigravity-live-checks.md`.

- **Instruction files are cumulative and walk up to the checkout root.** Started in `.scratch/agy-spike/parent/child`, the session held four files in context: `parent/child/AGENTS.md`, `parent/AGENTS.md`, `.scratch/agy-spike/AGENTS.md` and the repository's own `AGENTS.md`. So `AGENTS.md` behaves as for CodeBuddy, and a session started anywhere in a repo inherits the root file — which is also where the first call's 12k input tokens go.
- **A hook can fail closed, but silence fails open.** `PreToolUse` on `run_command`, matcher `run_command`, decision returned as stdout JSON:
  - `{"decision": "deny"}` blocks: `tool call denied by pre-tool hook: spike deny: deny`.
  - exit 1 blocks: `JSON hook ... failed: command failed: exit status 1`.
  - a 40 s hook against the 30 s timeout blocks: `command failed: signal: killed`.
  - exit 0 with no output **allows**: the command ran and printed its output.
  So an adapter must always emit a decision and must never exit 0 silently; a crash and a timeout are safe, an empty success is not.
- **The hook payload** carries `hookEventName`, `cwd`, `conversationId`, `artifactDirectoryPath`, `lastUserInput`, `modelName`, `stepIdx` and a `toolCall` object — enough to translate into the guard's input without guessing.
- **`--dangerously-skip-permissions` does not bypass hooks.** Every hook decision above was measured with that flag set, so it turns off the permission prompt and leaves the hook in charge, which is the combination a layer wants.
- **Subagents work.** A file in `.agents/agents/` spawned on request and its reply came back to the parent.
- **Skills work and are a path to tool use.** A skill was invoked without being named as a command; it read its own `SKILL.md` and ran four shell commands. That confirms the sweep problem: a skill cannot be kept out of the model's reach.
- **Headless soft-denies and still exits 0.** A blocked command produced `status: SUCCESS` with the denial described in the response, so a pipeline must read the response body, not the exit code.
- **Quota cost is real but small.** One session start plus a short prompt moved the Gemini group from 99.26% to 97.76% of its weekly limit; context dominates, so short sessions fit a week and a long agentic run would not.

## What a layer would look like

- `AGENTS.md` is the always-loaded rules home, as for CodeBuddy; no pointer file and no `AGENTS.md` copy.
- `.agents/agents/{pm,qa-engineer,software-engineer}.md` as role definitions, with Antigravity tool names.
- `.agents/hooks.json` with a `PreToolUse` hook on `run_command`, calling a small adapter that translates Antigravity's `toolCall` payload to the guard's input and its block to `{"decision": "deny", "reason": ...}`. The adapter must emit a decision on every path, including its own errors, because a hook that exits 0 with no output allows the command. `Stop` gets a similar adapter for `make verify`.
- No `.agents/skills/sweep/`: the model can invoke it, which breaks the sweep rule. Leave the sweep out, or accept a model-invocable skill and say so.
- Permissions: a documented human step editing `~/.gemini/antigravity-cli/settings.json`, not an installed file. That makes it like the push check (`human-machine`), and it cannot be byte-compared.
- No workspace settings file exists, so `installed-files.txt` gets lines only for the agents, the hook adapter and any rules file; the permission rules stay off the map.

## Still open

Answered on 2026-11-21 and moved into the section above: hook deny, crash, silence and timeout; subagent and skill discovery; headless soft-deny; whether the skip-permissions flag bypasses hooks; and the API-key path's `429` on `gemini-3.1-pro`.

1. What is the starter quota tied to, and does it survive a container rebuild? `/usage` names the signed-in account, so it is per person rather than per install; whether the stored session is in a mounted volume decides whether `setup.sh` can provision anything at all.
2. Do `command(...)` rules in the global settings apply to `run_command` arguments, and does a `command(git push)` deny stop a push?
3. ~~Does malformed JSON from a hook block or allow?~~ Answered 2026-11-21: malformed JSON blocks with `failed to unmarshal result from hook ... via protojson: invalid json text`. Silence allows, but a parse failure does not. The adapter's output format is therefore not the last line of defence, but the adapter still emits valid JSON on every path to avoid relying on this.
4. What working directory does a hook command run in? The hooks page documents no environment variable for the project folder and does not say where `command` is resolved; its own examples use `./scripts/...`. The layer's `hooks.json` therefore uses a path relative to the project folder, and the install check is what proves it. The adapter itself does not depend on the answer: it finds the kit from its own file and the payload's `workspacePaths`, `Cwd` and `cwd`.
5. Do the deny rules protect dotenv files in practice? The permissions page states that denying `read_file` on a path also denies `write_file` there, which is why the layer ships three `read_file` entries and no `write_file` ones. That is documentation, not a measurement: the human step that applies the rules has not been run against a live `agy` yet.

## Recommendation

Spike first, then decide. If only the container install is wanted, install a pinned version in `setup.sh` rather than piping an unpinned script at build time, and note that the starter quota needs no authentication step, so no key has to enter the container at all. A full layer is a 1.11-sized change and needs an approved issue; the guard adapter and the missing manual-skill control are the two design decisions to settle first.
