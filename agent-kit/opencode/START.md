# OpenCode layer

Start here if you run the agent kit with OpenCode. OpenCode reads `AGENTS.md` directly, so the core kit works without this layer. The layer adds OpenCode's own enforcement: role definitions and permission rules. It's deliberately minimal for now, with no hooks; see Limits.

## What it adds

| File | Installed as | What it does |
|---|---|---|
| `agents/pm.md`, `agents/software-engineer.md`, `agents/qa-engineer.md` | `.opencode/agents/` | Role definitions (subagents), each pointing to its file in `team/`. PM and QA can edit files only in `.scratch/`; OpenCode enforces that. The file name is the agent's name. |
| `skills/sweep/SKILL.md` | `.opencode/skills/sweep/SKILL.md` | The sweep skill, pointing at `procedures/sweep.md`. OpenCode lists its one-line description to every agent; the body loads only when the skill is called. |
| `opencode.json` | Merged into `opencode.json` in the project folder | Blocks `.env` files (not `.env.example`) in its file tools and, as a text pattern, in shell commands; asks before edits to protected files; allows `make`, read-only commands and plain commits; asks before anything else; blocks broad staging, `-a`, `-n`, `--no-verify`, `git push`, `core.hooksPath` changes and token-printing commands |

## Permission rules

In OpenCode's permission rules, the last matching rule wins. So the `bash` list is ordered: the general `*` ask, then the allows, then the metacharacter asks (`$`, backtick, `;`, `&`, `|`, `>`, `<`, newline; absolute paths, `..` and `~` arguments; recursive `grep`), then the specific asks and denies, and last the `*.env*` deny. An ask placed after a deny would downgrade it.

These are text patterns. They catch mistakes and cut prompts; they are not a security boundary. The boundary is the sandbox, a read-only-code token and your review before push. Restart OpenCode after editing the config.

- **Allow read-only commands in the config; turn repeated tasks into `make` targets whose variables are validated before use; keep ad-hoc code at ask.** Don't click "Allow always" for interpreter commands. Put permanent approvals in `opencode.json`: it is versioned and reviewable, while a click-through approval leaves no record and its scope is not documented.
- **Left out on purpose:** `echo *` (`echo $GITHUB_TOKEN` prints a token); `jq *` (`jq -n 'env'` prints every environment variable); `rg *` (`--pre` runs a command); `date*` (`date -s` sets the clock); `pgrep *` (`-a` and `-f` print other processes' command lines); `git add *` (broad staging no check blocks); `git fetch*` (`--upload-pack` runs a command; only `git fetch` and `git fetch origin` are allowed); interpreters (`python3`, `node`, `bash`, `sh`). Raw `gh issue` writes and `gh api*` stay at ask.
- **Commits:** `git commit *` runs without a prompt, `--amend` asks, and `-n`, `-a`, `--all` and `--no-verify` are denied. `HUMAN_APPROVED=1 git commit` starts with a variable, so it prompts: that is your approval point. A protected-file commit without it is stopped by the pre-commit hook, not by these patterns.
- **Tokens:** `gh auth token`, `gh auth status` with `--show-token` or `-t`, `gh auth git-credential`, `git credential` and `git config` with `credential` are denied. `git config --list` and `--get-regexp` ask. `gh api`, `gh config`, interpreters and shell indirection can reach the same data.
- **The token can write issues** (`environments.md`), so it can also edit or close issues and add labels, including `approved`. The `AGENTS.md` rule that agents never add that label is a text rule the token does not enforce; raw `gh issue` writes stay at ask for that reason.
- **Remote URLs:** `git remote -v` and `get-url *` are allowed because the sandbox's git credentials come from a credential helper, not the URL. A project whose remote URL embeds credentials must not copy those two.
- **Over-prompts:** commit messages, `--jq` and `grep -E` expressions containing `|`, `;`, `&`, `$`, `<` or `>` ask, as does `2>&1`; a prompt is cheap, a slipped chain is not. `*.env*` also denies `cat my.env.txt`, `ls .envrc`, `cat .environment` and `git commit -m "document the .env rule"`. Read `.env.example` with the read tool.
- **Residual gaps:** short-flag clusters such as `-mn` and `grep -nr`, globs such as `head .e*`, and symlinks are not matched.
- **Not verified:** whether OpenCode 1.19.5 splits a command on `;`, `&&` and `|` before matching, and whether it checks bash path arguments (`external_directory`). The patterns don't depend on either. By hand: run `ls ; touch .scratch/marker`, `head -n 1 /proc/self/environ` and `ls /`, and note whether each prompted and which rule asked.

## Install

Setup does this when you say you use OpenCode (`setup.md`, step 4). To do it by hand, from the project folder:

1. **Start OpenCode in the project folder**, not the repository root.
2. **Role definitions:** copy the three files in `opencode/agents/` into `.opencode/agents/`, and `opencode/skills/sweep/` into `.opencode/skills/sweep/`.
3. **Settings:** merge `opencode/opencode.json` into the project's `opencode.json`, keeping anything already there. Then make the `edit` rules match the project's `PROTECTED` list in `agent-kit.conf`: one `"<pattern>": "ask"` entry per protected file, kept in sync with that list. If the project's secrets use other names, add `read` deny rules for them.
4. **Protection:** add `'opencode.json'` and `'.opencode/*'` to `PROTECTED` in `agent-kit.conf`. These files decide what agents may do.
5. **Check it.** Restart OpenCode, then:
   - ask it to list its agents: `pm`, `software-engineer` and `qa-engineer` should appear;
   - ask it to run `git add .`: the command should be denied;
   - ask the `pm` agent to edit `README.md`: the edit should be denied.

   If a path rule doesn't match as expected, check OpenCode's permissions documentation for how it matches paths. The rules here assume paths relative to the project folder.

## Limits

- **No hooks yet.** The Claude Code layer stops the Engineer finishing while `make verify` fails; OpenCode has no such check here. The Engineer runs **Verify** because its role file says so, and the git hooks, your push check and CI catch what it misses.
- **Pattern matching only.** The git rules match how a command is written, so a variant can get past them (see Residual gaps above). The kit's git hooks and your review still apply.
- **Settings apply only inside OpenCode.** The core kit's git hooks still cover every tool.

## Projects that already have an OpenCode setup

Setup classifies existing `.opencode/` files and `opencode.json` like any other agent setup ("Existing agent setups" in `setup.md`). Ask for the OpenCode layer in the setup prompt: "Set up this project using `_docs/agent-kit/setup.md`, including the OpenCode layer in `_docs/agent-kit/opencode/START.md`."
