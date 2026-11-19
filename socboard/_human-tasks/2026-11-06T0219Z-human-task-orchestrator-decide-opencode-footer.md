# Decide: keep or switch off OpenCode's own commit footer

## Purpose

Now that `Assisted-by: <Tool>` is required, decide what to do about OpenCode's own footer, which may add a co-author line with an email. Blocks: nothing urgent. Depends on step 2 of the task "check each tool's commits carry the Assisted-by line". Issue: none.

## Where to decide

In the orchestrator session, after that check shows what OpenCode really writes. Nothing to run.

## Options

1. Keep both lines. The marker is duplicated and the email line stays, which the kit's attribution blueprint avoids. The metrics script tolerates it.
2. Switch the footer off in OpenCode's settings, if it offers one. I could not confirm such a setting; check OpenCode's documentation for your version.
3. Leave it and revisit only if it causes noise.

## Recommendation

Decide after the check. If OpenCode adds the email line and a setting exists, choose option 2. Otherwise choose option 1.

## Record the result

Write Pass once decided, and name the option in the note.

| Step | Pass or fail | Output or note |
|---|---|---|
| Decide | Pass | Option 1: keep both lines. Human decided 2026-11-09: OpenCode's own footer is accepted on purpose and not suppressed. The opencode-git-trailers plugin was tried and dropped (it only appends trailers, it cannot remove the default footer); its line was removed from the kit config in 4f5365e. Step 2 of the commit-lines check still confirms what OpenCode really writes. |

## Risk

None to the work. The trial only needs one reliable marker per commit.
