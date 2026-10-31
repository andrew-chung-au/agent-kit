# Cloud session module (optional)

The core kit never pushes: the human reviews the diff and pushes. This optional module lets a Claude Code cloud session push only the branch it created, so the human can review a pull request. It is off by default and only the project can enable it.

## Enable it

1. Merge `settings.fragment.json` into `.claude/settings.json`. It sets `AGENT_KIT_CLOUD_PUSH=1` and asks before the one allowed push form.
2. Remove the blanket `Bash(git push *)` rule from the `deny` list. Keep every other push rule (`main`, force, delete). The fragment's `ask` rule and the git guard are what limit the push.
3. Keep `hooks/guard_git.py` installed. With the module enabled it allows only `git push -u origin <current branch>`, and only when the branch starts with `claude/`, is not `main`, and `CLAUDE_CODE_REMOTE=true` (Claude Code sets it in a cloud session).
4. Tell the human which branch the session will push, and let them review the pull request and merge it.

## What the module guarantees

- The agent may push only the current `claude/*` branch, with exactly `git push -u origin <current branch>`.
- It cannot push `main`, force-push, delete a branch, push another ref or use a different remote.
- Every push still asks the human, and the human reviews the diff and merges.

## Limits

- This is a guard against habits, not a security boundary. A command written another way, or a push run through a script, can get past it. The git hooks and the human's review catch what gets past.
- The module does not change the core kit's rules for local sessions: without `AGENT_KIT_CLOUD_PUSH=1`, `git push` is blocked.
