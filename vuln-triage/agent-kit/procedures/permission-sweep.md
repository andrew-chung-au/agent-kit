# Permission sweep

A sweep turns the approvals that sessions recorded into one decision about the settings files. Sessions only record; they do not propose settings changes. Run a sweep as its own small issue, every so often (for example after a batch of issues, or when the same approval keeps stopping the human).

## When and where

- Apply settings changes only between sessions, never while a role is mid-issue. Settings files load when a session starts (VERIFY: the Claude Code permissions page does not say when settings load; treat it as session start).
- Do not run the sweep in the local tree while another session is committing to `main` (two sessions in one tree caused the #17/#35 clash). Run it in a cloud session, or between local issues.

## Steps

1. Read the last sweep's commit from `_docs/permission-sweeps.md` (the last line). If no sweep has happened yet, use the commit before the first session summary you want counted.
2. Run `make permission-report SINCE=<that commit>`. It reads session summaries only, counts distinct summaries per command pattern in each group, and lists summaries with no Permission review section or with "none" only. `SINCE` is exclusive. Summaries that used the older three groups are read as read-only, protected record writes and risky.
3. Read the report next to the current `.claude/settings.json` and `opencode.json`. A pattern already allowed or asked is not a candidate; check the report's "Uncategorised or to read by hand" lines yourself.
4. Apply the decision rules below to each pattern.
5. Write the exact diffs for both settings files. Where the two tools should agree, say so, or write down the reason they differ.
6. Ask the human one decision question with both diffs (layout in `asking-the-human.md`).
7. After approval: one `HUMAN_APPROVED=1` commit for the settings files; post the protected-change approval record on the sweep issue.
8. Add one line to `_docs/permission-sweeps.md`: date, the commit the sweep counted up to (the commit that was `HEAD` when the report ran), and the outcome in a few words. The next sweep starts from that commit.

## Decision rules

- Read-only patterns: propose allowing a pattern once it has come up in three distinct session summaries. Fewer than three: leave it. Prefer a validated `make` target (`make branches`, `make ci`, `make ci-run`, `make file-at`) over a broad shell pattern.
- Routine issue writes (append-only comments and issue creation): already allowed through `make issue-comment` and `make issue-create`; do not add a rule. If a summary records one, treat it as stale wording, not a candidate.
- Protected record writes (issue edits and closes, protected commits, pushes): keep on ask. Issue comments and creation are the only routine issue writes; editing, closing and deleting stay `ask`/`deny`.
- System and external changes (installs, processes, network, settings outside the repo): keep on ask. A check that keeps coming back becomes a `make` target proposed to the human.
- `python3 .scratch/*` and `bash .scratch/*`: never allow. They run whatever code the agent writes. A check that keeps coming back becomes a `make` target proposed to the human (`make *` is already allowed and the `Makefile` is protected). The report labels these "make target, never allow".
- Risky items (a refused push, a destructive command): propose a deny rule. A risky item that just happened is not left for the sweep; the orchestrator brings it to the human at the decision point of its own issue.
- Cloud push is not a sweep candidate. It is off unless the project enables the optional `claude-code/cloud-session/` module (`AGENT_KIT_CLOUD_PUSH=1`), and then only the session's `claude/*` branch. The core kit stays no-push.
- Never propose an allow rule with a `*` inside the arguments of a command that can write. The Claude Code permissions page calls argument patterns fragile: `Bash(gh api repos/*)` let flag-after-path writes run unprompted (#60). Prefer a `make` target, or ask.
- When the same command is allowed in one tool and asked in the other, either make them agree or write the reason in the diff.

## What the report does not tell you

Summaries record requests, not outcomes, and the report does not read GitHub role comments. A pattern missing from the report may still have been approved in a session whose summary did not list it. Revisit if sweeps keep missing items.
