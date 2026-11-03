# Development process

How work moves from idea to done, with any AI coding tool. Project-specific values (commands, branching, summary naming) are in `AGENTS.md`; this file refers to them by their bold labels, such as **Verify**.

## Start of every session

Before picking up work, the orchestrator checks the spec:

1. **No `_docs/specs.md`:** the project is in planning. See Planning.
2. **The spec changed since last session:** find the last summary's commit (`git log -1 --format=%h -- _session-summaries/`), read the `**Spec version:**` line of the summary it added, and run `git log --oneline <version>..HEAD -- _docs/specs.md`. If that lists commits, review the backlog. If no summary has a version, skip it.
3. **Otherwise:** continue with the lifecycle.

## Planning

Planning produces or revises `_docs/specs.md`. The human may write it outside the repo, or draft it with an agent (for example in a planning mode).

- An agent helping with planning proposes spec text; the human approves it before it's written.
- No issues are created and no product code is written until the spec exists.
- Spec changes are committed on their own, with a message saying what changed.
- The spec is human-owned at all times, not only in planning: propose changes, and make them only after approval.

Mid-project changes and new versions (v2) work the same way: revise the spec, then review the backlog.

## Backlog

- Tasks are GitHub issues, worked one at a time.
- **Building the backlog:** when there are no open issues and the spec has parts not yet built, the PM proposes new issues from the spec.
- **Reviewing the backlog:** when the spec has changed, the PM compares the change with existing issues and proposes new issues, edits to open issues, and open issues to close as not planned.
- The human's approval of a backlog proposal still comes before any issue is created, edited or closed.
- After grooming, every issue follows `_docs/agent-kit/templates/task-template.md`. Grooming comes before the label, and the label approves the groomed text (Lifecycle, steps 1 and 2).

## Issue comments

- Start every issue comment with your role (`PM:`, `Engineer:`, `QA:` or `Orchestrator:`). All roles usually share one GitHub account, so the label is the only way to tell them apart.
- Never edit or delete an existing comment; post a new one. Other roles' comments are part of the record.
- File an issue with `make issue-create FILE=.scratch/<name>.md` (first line `Title: <text>`, a blank line, then the body) and post a comment with `make issue-comment N=<number> FILE=.scratch/<name>.md`; both are in `_docs/agent-kit/templates/Makefile.github.mk`. They refuse text that looks like a secret, post no labels, and comment only on an `approved` or owner-authored issue. Editing an issue asks the human. Only the orchestrator closes, with `make issue-close N=<number>` (`REASON=not-planned` for a closure the human approved), never a raw `gh issue close`; it refuses unless the owner's comments show the process was followed. Describe env files in words ("the example env file"), not by name. The scanner reads line by line, so a key split across lines is missed.

## Roles

Each role follows its file in `_docs/agent-kit/team/`:

- **PM** (`pm.md`) builds and reviews the backlog, and grooms an issue before anyone implements it.
- **Engineer** (`software-engineer.md`) implements one groomed issue.
- **QA** (`qa-engineer.md`) checks the result against the acceptance criteria and changes nothing.

How to run a role depends on the tool:

- **If your tool can launch subagents,** the orchestrator launches each role as a subagent. If the project has role definitions for the tool (see Role definitions in `blueprints.md`), launch those. Otherwise subagents don't always receive the project's instructions automatically, so start every launch message with: "Read `AGENTS.md`, then `_docs/agent-kit/team/<role>.md`. Use your tool's built-in features to read, search and edit files, and put multi-step checks in `.scratch/` scripts. If something needs the human's approval, return the request to me instead of running it." Then give the issue number and the task.
- **Otherwise,** run each role in a fresh session: "You are the QA engineer. Read `_docs/agent-kit/team/qa-engineer.md` and check issue #N." A fresh session is the point: the reviewer shouldn't share the context of the author.

## Orchestrator

The main session is the orchestrator. It launches the roles and passes work between them. It does not plan the backlog, groom, implement or test itself.

It asks the human mid-issue only when the work can't continue without an answer. Everything else waits for the decision point at the end of the issue (Lifecycle, step 7).

Every question to the human, from any role, follows `_docs/agent-kit/procedures/asking-the-human.md`: an approval request or a decision question, each with the reason, the alternatives and a recommendation. When a subagent returns with a request, the orchestrator passes it on in full, adding anything the human needs from other roles' work, and doesn't shorten it to a yes/no question. It then resumes the same role with the answer, or relaunches it with the answer and a note of what's done.

**Human tasks.** Anything the human must run or check by hand, beyond a one-line command, goes in a task file in `_human-tasks/`, from `templates/human-task.md`, written before the human is asked; the message links it instead of repeating the steps. This covers by-hand checks of tool behaviour, pushes from the clean clone, label commands and protected-file commits the human performs (not the Engineer's `HUMAN_APPROVED=1` commit, which keeps its approval request). The orchestrator writes it, or the role drafts it and returns it, since a subagent can't ask the human.

**Report by reference.** If a result is in a file (session summary, issue comment, `.scratch/` file, task file), a message to the human or a role's return gives the path or link, a one-line size or outcome, and the decisions or exceptions needing them, never its contents. Exceptions, kept in full: a protected-commit approval request (its diff and `git diff --cached --stat`); a security finding (never the secret); a blocking question. `make clean-scratch` deletes untracked `.scratch/`, so post or commit anything lasting; clean up after the human has read it.

## When a role's actions are blocked

If the tool blocks a role's action as risky, or blocks several in a row, the orchestrator stops that role before it continues. It shows the human each blocked command and what the role was trying to do, and checks whether anything was changed or deleted, including git-ignored files and Docker volumes.

To find the blocked commands, the orchestrator first asks the role to list them, if the role can be resumed. Otherwise it asks the human to look in the tool's own view of the run. The tool's session logs live outside the project folder. Read one only after an approval request, read it where it is, and never copy it into the project. Then it proposes, as a decision question, whether to resume the role or discard its run and start fresh. Starting fresh is usually better for QA, whose verdict must come from a clean run.

## When a role stops early

A role can stop part-way: a usage limit, a crash, a timeout or a lost connection. Before relaunching it, the orchestrator checks what it left behind:

1. `git status --short` and `git log --oneline -5`: uncommitted edits or unexpected commits.
2. The issue's text and its latest comments: a half-edited issue or a comment that stops part-way.
3. Anything it started: running processes, temporary system changes.

Treat partial output as unverified. Relaunch the role with a note of what's already done and what it must check or redo, never with what it was about to do. If something can't be repaired without a judgement call, ask the human.

## Tiers

| Tier | Who works it | Gates | For |
|---|---|---|---|
| Light | Engineer only; no PM grooming, no QA | `make verify`, `make tier-check TIER=light`, the human's review of the diff | Small changes to the paths `LIGHT_ALLOWED` lists in `agent-kit.conf` |
| Standard | PM grooms, Engineer implements, QA checks | The Lifecycle below | Everything else |
| Heavy | The Standard path | An approved ADR before the Engineer starts; a second QA launch (Heavy gates, below) | Changes to the process itself, security boundaries and interfaces other code depends on |

- **The label sets the tier; `approved` approves a raising proposal.** Labels are `tier:light`, `tier:standard` and `tier:heavy`, read with `gh issue view <N> --json labels`. A tier label always wins, lowering included. Two or more tier labels mean the highest. With `approved` and no tier label, the tier is the highest of Standard and the `Proposed tier:` line in the first owner `PM:` comment that has one and names the approved `Body sha256:`; none means Standard. Hash re-records without that line and later comments change nothing; a changed body needs a new hash record. A Light proposal has no effect without `tier:light`: Light skips QA, and all roles share one GitHub login. A tier named in the issue body or in any other comment is ignored; an `Orchestrator:` comment can only raise, as below.
- **Proposals:** every PM grooming comment states `Proposed tier: <light|standard|heavy>`, a one-line reason and the paths the change is expected to touch, so the human can compare them with `LIGHT_ALLOWED` and the escalation list in `scripts/check-tier.sh`. A grooming comment without that line is incomplete. The orchestrator may also propose a tier in an `Orchestrator:` comment, never as a label and never as a decision. When in doubt, propose the higher tier, and never a lower one than `make tier-check` allows.
- **Light issues get a short PM launch.** They are not groomed, so the PM cannot carry the proposal in a grooming comment. When the human says an issue is meant to be Light, the orchestrator launches the PM only to post one `PM:` comment with the `Body sha256:` line (from `make issue-hash N=<number>`) and the same `Proposed tier:` line, reason and expected paths, before the human labels. Only a `PM:` comment from the owner's account records the hash; the orchestrator's own record does not count. If a would-be-Light issue has a recorded hash but no `Proposed tier:` line in the latest `PM:` comment, the orchestrator stops and asks for the proposal first. Only a Standard or Heavy proposal takes effect without a label; Light still needs `tier:light`. The orchestrator never decides that an issue is Light.
- **Raise, never lower.** An agent may raise the tier: the orchestrator runs the higher tier's steps and posts an `Orchestrator:` comment naming the new tier and the reason. It never touches labels. Lowering needs the human to change the label and say so in the session.
- **When Light stops being Light:** if `make tier-check TIER=light` fails, or the change grows past the allowance while being done, the orchestrator stops the Light path, posts that comment, and the change goes through PM grooming, Engineer and QA as Standard. Carrying on as Light after a failed check is not allowed.
- **Heavy gates.** An effective-Heavy issue (a `tier:heavy` label, or an approved Heavy proposal) follows the Lifecycle with two added gates:
  - **ADR before the Engineer.** While grooming, the PM adds a `## Decision record` section to the issue body, filled from `_docs/agent-kit/templates/adr.md` (Decision, Reason, Alternatives, Trade-offs). The body hash the PM records covers it, and the human's `approved` message names that section. If the human rejects or changes the ADR, the issue returns to the PM and the Engineer does not start; an edit after approval follows Approved text. The orchestrator's hash check before the Engineer launches is the only enforcement (no script), and an ADR that differs from the approved hash does not count. The Engineer then commits the ADR as a file and adds its row to the docs index.
  - **Second QA launch.** After the first QA PASS (and its **Assert clean**), the orchestrator launches QA again as a fresh launch, never a resumed one, because shared context defeats an independent review. The launch message limits it to the Code review checklist in `_docs/agent-kit/team/qa-engineer.md`. A resumed second launch is discarded and run again; the orchestrator's check and the human's reading enforce this. **Assert clean** runs after it as after the first. If it posts FAIL, the issue goes back to the Engineer like any QA FAIL. The issue is done only when both launches have posted PASS.
  - **Lowering.** An agent never lowers a Heavy issue to Standard or Light; only the human's changed label does (Raise, never lower).
- **What enforces this:** the label rule in `AGENTS.md` (only the human labels) and the rules above. `make tier-check` checks paths and size only; no hook runs it, so the orchestrator runs it and its output is shown at the human's diff review. Raising-only and the proposal line are process rules, enforced by the orchestrator's read and `PM:` hash match before the Engineer launches and by the human's reading. No script or hook computes the tier.
- **Every Light change has its own `approved` issue.** There is no standing housekeeping issue. The session summary is still written, and its first line names the tier.
- **Review of Light** after its first ten uses: did any Light change need a follow-up fix to the same paths? Was the short PM launch wasteful enough to reopen the decision above? Narrow `LIGHT_ALLOWED` if so.

## Lifecycle

1. Pick the next open issue in the agreed order. If there are none, build the backlog (see Backlog).
2. The PM grooms it, even if it is not yet labelled, when it is owner-authored (`AGENTS.md`, Issues). Groom only the next issue in the agreed order, not a second unlabelled issue while the first waits for the label. The PM's comment records the body hash. Then the human reads the groomed text and adds `approved`; the Engineer starts only after that. If the human changes the text, the orchestrator has the PM record the new hash in a new `PM:` comment before the label is added. Never skip this step. By default (no tier label and no raising proposal is Standard) the PM grooms in full, and the grooming comment carries the `Proposed tier:` line. Only when the human has said the issue is meant to be Light does the PM do the short launch instead (hash record and proposal, no rewrite of the body; see Tiers). The orchestrator reads the effective tier but never decides one.
3. Before launching the Engineer, and before relaunching it after a QA FAIL, run the hash check (see Approved text), for every tier. Read the labels and the matching `PM:` comment, state the effective tier, and when the tier comes from the PM proposal rather than a label, post an `Orchestrator:` comment naming it "from the PM proposal". The Engineer implements it, commits, and runs **Verify** following `_docs/agent-kit/procedures/verify.md`. With the Claude Code layer, a hook also re-runs **Verify** when the Engineer tries to finish. For Light, the Engineer also runs `make tier-check TIER=light` and lists its output in the `Engineer:` comment.
4. Before launching QA, the orchestrator runs the hash check and notes the current commit (`git rev-parse --short HEAD`). Then the QA engineer checks the issue. QA puts an injection or bypass attempt in a test or a `.scratch/` script, never in a live shell command. Steps 4 to 6 apply to Standard and Heavy only; Light has no QA. For Standard, this single launch also fills the `Code review` block; for Heavy, see the second QA launch in Tiers.
5. After QA, the orchestrator runs **Assert clean** and confirms HEAD hasn't moved. If either fails, QA changed something: discard QA's verdict and run QA again.
6. On FAIL, go back to step 3 with the QA comment as input; the hash check runs again.
7. On PASS, the **decision point**: run `make sweep-due`, then gather everything waiting for the human into one message and ask once. That's proposed AGENTS.md changes, spec notes from any role, other protected-file changes, choices the Engineer made that the issue doesn't cover, risks QA reported outside the criteria, and a sweep proposal (`_docs/agent-kit/procedures/sweep.md`) if it says due. Show each as a diff or a short description, using the layouts in `_docs/agent-kit/procedures/asking-the-human.md`, with your recommendation. Then:
   - Apply approved AGENTS.md, spec and other protected-file changes in their own commits, with `HUMAN_APPROVED=1`.
   - If an approved change needs Engineer work, go back to step 3; QA re-checks only what changed.
   - For each risk the human wants handled later, the PM files a follow-up issue.
8. Clean up, then write the session summary following `_docs/agent-kit/procedures/session-summary.md`:
   - Confirm nothing started during the issue is still running (`make <name>-stop` for each).
   - Confirm temporary system changes are undone, or that the human chose to keep them.
   - If a `.scratch/` script is worth keeping, propose it as a test or a make target at the decision point (step 7). Nothing in `.scratch/` survives cleanup.
   - Run `make clean-scratch`. It empties `.scratch/`, including session logs and test tokens, and refuses while a started process is still running. Record in the summary that it ran.
9. Close the issue. Only the orchestrator closes issues: after QA posts PASS on an `approved` issue, or as not planned after the human approves that closure in a backlog review, whatever the label. A Light issue is closed once its Definition of done is met, with no QA PASS. Post the Close comment (`procedures/orchestrator-comments.md`), then run `make issue-close N=<number>`.
10. The human reviews the diff and pushes (see Commits).
11. Repeat until the backlog is empty and every part of the spec is built.

### Approved text

The `approved` label means the human approved the groomed body as recorded. The hash check: run `make issue-hash N=<number>` and compare `Body sha256:` with `Recorded sha256:`. If they differ, `Recorded sha256:` is `none` or `unknown`, or the command exits non-zero or prints `unknown`, don't launch the role; show the human the diff of the body, not a paraphrase.

A recorded hash counts only from a comment that starts with `PM:` and is authored by the repository owner's account: the script compares each comment's `comments[].author.login` with `Repository owner:`, and the latest valid line wins. A `Body sha256:` line anywhere else is ignored.

To change the body after approval, the human confirms it in this session, recorded in an `Orchestrator:` comment naming the new hash; the PM then records that hash in a `PM:` comment. Without that `PM:` line the launch stays blocked. Neither the orchestrator nor the PM edits an approved body and carries on without the confirmation comment. A title change is reported to the human as a note, not a freeze failure.

## Commits and pushes

- Small, focused commits at logical milestones; messages say what changed and why.
- Attribution comes from the tool's settings (see Commit attribution in `blueprints.md`). Agents don't add their own co-author lines.
- Staging, protected files and hooks follow `_docs/agent-kit/team/software-engineer.md#commits` and the hook line in `AGENTS.md`.
- **Only the human pushes.** Before pushing, the human reads `git diff origin/main --stat -- .`, then the full diff, and asks about any changed file outside the issue's Constraints. A clean QA report is not proof of a clean diff. The pre-push hook then runs **Verify**. In the local sandbox profile, the human does all of this from the clean clone, and the push check runs **Verify** instead (`environments.md`).

## Keeping the setup current

`_docs/agent-kit/blueprints.md` lists what the project should have and when. When the project gains a capability listed there (a test framework, e2e tests, migrations, a linter), propose the matching blueprint, following the same approval rule as other AGENTS.md changes. To check everything at once, re-run `_docs/agent-kit/setup.md` in review mode.

## Definition of done

An issue is done when:

- **Verify** passes and QA has posted PASS (for Heavy, both launches), so every acceptance criterion is met. A test is never weakened or skipped to make **Verify** pass.
- For Light, instead of QA's PASS: `make tier-check TIER=light` passes, the human has approved the diff (for a protected file, the exact diff), and the `Engineer:` comment on the issue lists the changed paths, the **Verify** result and the `tier-check` output.
- The changes are committed.
- Docs affected by the change are updated, and any AGENTS.md change has human approval.
- The session summary is written.
- The orchestrator has closed the issue through `make issue-close`.

The human's diff review and push come after this, outside the agent's definition of done.
