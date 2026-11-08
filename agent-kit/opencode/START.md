# OpenCode layer

Start here if you run the agent kit with OpenCode. OpenCode reads `AGENTS.md` directly, so the core kit works without this layer. The layer adds OpenCode's own enforcement: role definitions and permission rules. It's deliberately minimal for now, with no hooks; see Limits.

## What it adds

| File | Installed as | What it does |
|---|---|---|
| `agents/pm.md`, `agents/software-engineer.md`, `agents/qa-engineer.md` | `.opencode/agents/` | Role definitions (subagents), each pointing to its file in `team/`. PM and QA can edit files only in `.scratch/`; OpenCode enforces that. The file name is the agent's name. |
| `skills/sweep/SKILL.md` | `.opencode/skills/sweep/SKILL.md` | The sweep skill, pointing at `procedures/sweep.md`. OpenCode lists its one-line description to every agent; the body loads only when the skill is called. |
| `plugins/permission-log.js` | `.opencode/plugins/permission-log.js` | Optional. Records each permission request and your reply in `.agent-kit/logs/permissions/` (git-ignored), with secrets removed. It only observes and changes no decision. Format: `procedures/permission-log.md`. |
| `opencode.json` | Merged into `opencode.json` in the project folder | Blocks `.env` files (not `.env.example`), in shell commands by text pattern; asks before protected-file edits and unlisted commands; allows `make`, read-only commands and plain commits; blocks broad staging, `-a`, `-n`, `--no-verify`, `git push` and token-printing commands |

## Permission rules

The last matching rule wins, so the `bash` list is ordered: `*` ask, the allows, the metacharacter and path asks, the specific asks and denies, and last the `*.env*` deny. An ask after a deny would downgrade it.

These are text patterns that catch mistakes and cut prompts, not a security boundary. The boundary is the sandbox, a read-only-code token and your review before push. Restart OpenCode after editing the config.

- **Allow read-only commands in the config; turn repeated tasks into `make` targets whose variables are validated before use; keep ad-hoc code at ask.** Don't click "Allow always" for interpreters; put permanent approvals in `opencode.json`: versioned and reviewable, unlike a click-through approval, which leaves no record and has no documented scope.
- **Left out on purpose:** `echo *` (`echo $GITHUB_TOKEN` prints a token); `jq *` (`jq -n 'env'` prints every variable); `rg *` (`--pre` runs a command); `date*` (`date -s` sets the clock); `pgrep *` (`-a` prints others' command lines); `git add *` (broad staging); `git fetch*` (`--upload-pack` runs a command); interpreters. Raw `gh issue` writes and `gh api*` ask.
- **Commits:** `git commit *` runs silently, `--amend` asks, and `-n`, `-a`, `--all`, `--no-verify` are denied. Git accepts any unambiguous option prefix, so `--no-v` is denied and `--am` asks too; a message containing either is over-blocked. `HUMAN_APPROVED=1 git commit` prompts (it starts with a variable): your approval point. The pre-commit hook, not these patterns, stops unapproved protected commits.
- **Sibling subcommands:** `git diff` and `git show` are allowed bare and as `git diff *`, `git show *`, never `git diff*`, which also matches `git difftool` (`--extcmd` runs a command) and `git show-ref`. `git diff --ext-diff` and `git log --textconv` run a driver only if the repo's config or attributes name one: those files are a trust root, as with `make *`.
- **Chains (by hand: OpenCode 1.19.5, 2026-11-02, one model, one session):** OpenCode checks each command of a chain on its own. Allowed commands chained run silently; an unallowed one prompts alone. The `*;*`, `*&*` and `*|*` asks are belt and braces: they can fire only on those characters inside quotes (untested). The `$` and `>` asks fired.
- **Tokens:** `gh auth token`, `gh auth status` with `--show-token` or `-t`, `gh auth git-credential`, `git credential` and `git config` with `credential` are denied; `git config --list` and `--get-regexp` ask. `gh api`, `gh config` and shell indirection reach the same data.
- **The token can write issues** (`environments.md`): it can edit or close issues and add labels, including `approved`. The `AGENTS.md` rule against that is text the token does not enforce, so raw `gh issue` writes ask.
- **Remote URLs:** `git remote -v` and `get-url *` are allowed because sandbox git credentials come from a helper, not the URL. A project whose remote URL embeds credentials must not copy them.
- **Paths and options:** values after `=/`, quoted absolute or `..` paths, attached `-F/x`, `-f/x`, `-O/x` and a tab before `/` ask, as do `grep` or `diff` with a dash then an `r` (recursive), `tail -f` and `file -C`. `git config --get` is allowed for four exact keys (`user.name`, `user.email`, `core.hooksPath`, `remote.origin.url`): names are case-insensitive and values can hold credentials.
- **`make *` runs any command:** the Makefile is the trust root. `make -f`, `--file`, `--makefile`, `SHELL=` and `--eval` ask; abbreviated options (`--fi`), clusters (`-sf`) and project variables stay open. Real controls: the `Makefile` edit ask, the pre-commit hook, your review.
- **Over-prompts:** `--format=/x` values, quoted absolute paths, `grep -n x README.md` (dash, then `r`), commit messages, `--jq` and `grep -E` expressions containing `|`, `;`, `&`, `$`, `<` or `>` ask, as does `2>&1`. `*.env*` also denies `cat my.env.txt`, `ls .envrc`, `cat .environment` and `git commit -m "document the .env rule"`; read `.env.example` with the read tool.
- **Residual gaps:** short-flag clusters where `n` or `a` is not first (`-mn`, `-qn`), globs such as `head .e*`, symlinks and shell indirection. `git cat-file -p <hash>` can print a committed `.env` blob (the pre-commit hook stops new ones), and `git show HEAD:.e"nv"` passes the `.env` rule, like the glob gap. The pre-push check, CI and your review still catch a skipped hook.
- **Not verified:** whether the path prompts (`ls /`, `ls ..`) came from the bash path asks or `external_directory`. Untested: backticks, `<`, newlines, quoted operators.

## Install

Setup does this when you say you use OpenCode (`setup.md`, step 4). To do it by hand, from the project folder:

1. **Start OpenCode in the project folder**, not the repository root.
2. **Role definitions:** copy the three files in `opencode/agents/` into `.opencode/agents/`, and `opencode/skills/sweep/` into `.opencode/skills/sweep/`.
3. **Settings:** merge `opencode/opencode.json` into the project's `opencode.json`, keeping anything already there. Then make the `edit` rules match the project's `PROTECTED` list in `agent-kit.conf`: one `"<pattern>": "ask"` entry per protected file, kept in sync with that list. If the project's secrets use other names, add `read` deny rules for them.
4. **Protection:** add `'opencode.json'` and `'.opencode/*'` to `PROTECTED` in `agent-kit.conf`. These files decide what agents may do.
5. **Permission log (optional):** copy `opencode/plugins/permission-log.js` into `.opencode/plugins/`, and add `.agent-kit/logs/` to `.gitignore`. It reads `scripts/secret-patterns.txt`, so the project needs the GitHub module's pattern file first. Plugins load when OpenCode starts, so restart it.
6. **Check it.** Restart OpenCode, then:
   - ask it to list its agents: `pm`, `software-engineer` and `qa-engineer` should appear;
   - ask it to run `git add .`: the command should be denied;
   - ask the `pm` agent to edit `README.md`: the edit should be denied;
   - With the permission log plugin, run this hand check now and again after every OpenCode
     upgrade. Use the normal interactive interface, not `--auto` (auto-approval skips the
     prompt this checks). If `.scratch/` does not exist yet, run `mkdir -p .scratch` first
     (it prompts too). Read the last two lines after each step:

         tail -n 2 ".agent-kit/logs/permissions/$(date -u +%F).jsonl"

     1. **Allow once.** Prompt it: "Run `touch .scratch/hand-check-allowed`." Choose **once**.
        The command runs, and the log gains an `ask` with
        `"pattern":"touch .scratch/hand-check-allowed"`, then a `reply` with
        `"response":"once"` and the same `id`.
     2. **Fake key.** In a terminal (not through the agent), print a safe test command:

            printf 'echo sk-%s\n' aaaaaaaaaaaaaaaaaaaaaaaa

        Paste the line it prints into OpenCode and choose **once**. The prompt still
        appears, the `ask` line holds `"pattern":"echo [redacted]"`, and no log line holds the
        key:

            grep -c 'sk-a' ".agent-kit/logs/permissions/$(date -u +%F).jsonl"

        It must print `0`.
     3. **Reject.** Prompt it: "Run `touch .scratch/hand-check-rejected`." Choose **reject**.
        The command does not run (`ls .scratch/hand-check-rejected` says no such file), the
        log gains a `reply` with `"response":"reject"`, and the agent's turn ends: tell it to
        continue.

     Pass: all three prompts appeared, allow ran the command, reject did not, and the fake
     key is redacted. If a prompt disappears or a rejected command runs, stop using the
     plugin and report it.

   If a path rule doesn't match as expected, check OpenCode's permissions documentation for how it matches paths. The rules here assume paths relative to the project folder.

## Limits

- **No hooks yet.** The Claude Code layer stops the Engineer finishing while `make verify` fails; OpenCode has no such check here. The Engineer runs **Verify** because its role file says so, and the git hooks, your push check and CI catch what it misses.
- **Pattern matching only.** The rules match how a command is written, so a variant can get past them.
- **Settings apply only inside OpenCode.** The core kit's git hooks still cover every tool.
- **The permission log is complete for OpenCode only.** Claude Code arrives with #36. The plugin uses the V2 plugin API and needs OpenCode 2.x (written for 2.2.5; the real-session hand check passed on 2026-11-08); it is not compatible with 1.x. Run the hand check in step 6 first.

## Projects that already have an OpenCode setup

Setup classifies existing `.opencode/` files and `opencode.json` like any other agent setup ("Existing agent setups" in `setup.md`). Ask for the OpenCode layer in the setup prompt: "Set up this project using `_docs/agent-kit/setup.md`, including the OpenCode layer in `_docs/agent-kit/opencode/START.md`."
