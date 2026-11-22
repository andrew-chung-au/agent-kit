# Configure Antigravity CLI global permissions

## Purpose

Configure routine command pre-approvals, protected-file prompts and hard denials in Antigravity's global settings file `~/.gemini/antigravity-cli/settings.json`. Issue: #221.

## Where to run it

A terminal on the machine or container where the Antigravity CLI (`agy`) runs. Not in an agent session.

## Before you start

1. Confirm the settings file exists and note its size.

```
ls -l ~/.gemini/antigravity-cli/settings.json
```

Expected: the path and a size. If it is missing, create the folder first with `mkdir -p ~/.gemini/antigravity-cli` and start Step 1 from an empty `{}` file.

## Steps

### Step 1: Back up the existing settings

```
cp ~/.gemini/antigravity-cli/settings.json ~/.gemini/antigravity-cli/settings.json.bak
```

Expected: no output, and `settings.json.bak` now exists beside the original.
If different: if the file did not exist, create it containing `{}` and skip the backup.
Risk: none.

### Step 2: Merge the permissions block into settings.json

Open `~/.gemini/antigravity-cli/settings.json` in an editor and merge this object into the top level, keeping every key already there:

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
      "command(git push)"
    ]
  }
}
```

Then add these three strings to that `deny` list. Denying `read_file` on a path also denies writing it, so three entries cover both directions. They sit outside the block because the task checker rejects a dotenv name inside a command block.

| Add to `deny` | What it protects |
|---|---|
| `read_file(.env)` | the dotenv file at the project root |
| `read_file(.env.local)` | the local override |
| `read_file(.env.*.local)` | per-machine overrides |

Expected: valid JSON whose `permissions` object has 11 allow rules, 5 ask rules and 4 deny rules.
If different: run the Step 3 command to find the syntax error before saving.
Risk: changes live permissions for `agy` on this machine. Undo: `cp ~/.gemini/antigravity-cli/settings.json.bak ~/.gemini/antigravity-cli/settings.json`.

### Step 3: Confirm the file still parses

```
python3 -m json.tool ~/.gemini/antigravity-cli/settings.json
```

Expected: the whole file printed back as indented JSON, ending with `}`.
If different: fix the syntax error it names, then run this step again before starting `agy`.
Risk: none.

## Record the result

Paste the output or write pass or fail for each step. Commit this file with the result so a later run can compare. Results contain no secrets.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

## Risk

The file is global to the user account on this machine, so the rules apply to every project `agy` opens. Restoring the `.bak` file reverses all of it.
