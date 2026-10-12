# Development process

How work moves from idea to done, with any AI coding tool. Project-specific values (commands, branching, summary naming) are in `AGENTS.md`; this file refers to them by their bold labels, such as **Verify**.

## Start of every session

Before picking up work, the orchestrator checks the spec:

1. **No `_docs/specs.md`:** the project is in planning. See Planning.
2. **The spec changed since the last session:** take the spec version recorded in the latest session summary and run `git log --oneline <version>..HEAD -- _docs/specs.md`. If that lists any commits, run a backlog review (see Backlog) before starting an issue. If no summary records a version yet, skip this check.
3. **Otherwise:** continue with the lifecycle.

## Planning

Planning produces or revises `_docs/specs.md`. The human may write it outside the repo, or draft it with an agent (for example in a planning mode).

- An agent helping with planning proposes spec text; the human approves it before it's written.
- No issues are created and no product code is written until the spec exists.
- Spec changes are committed on their own, with a message saying what changed.

Mid-project changes and new versions (v2) work the same way: revise the spec, then review the backlog.

## Backlog

- Tasks are GitHub issues, worked one at a time.
- **Building the backlog:** when there are no open issues and the spec has parts not yet built, the PM proposes new issues from the spec.
- **Reviewing the backlog:** when the spec has changed, the PM compares the change with existing issues and proposes new issues, edits to open issues, and open issues to close as not planned.
- The human approves the proposal before any issue is created, edited or closed.
- After grooming, every issue follows `_docs/agent-kit/templates/task-template.md`.

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

## When a role's actions are blocked

If the tool blocks a role's action as risky, or blocks several in a row, the orchestrator stops that role before it continues. It shows the human each blocked command and what the role was trying to do, and checks whether anything was changed or deleted, including git-ignored files and Docker volumes.

To find the blocked commands, the orchestrator first asks the role to list them, if the role can be resumed. Otherwise it asks the human to look in the tool's own view of the run. The tool's session logs live outside the project folder. Read one only after an approval request, read it where it is, and never copy it into the project. Then it proposes, as a decision question, whether to resume the role or discard its run and start fresh. Starting fresh is usually better for QA, whose verdict must come from a clean run.

## When a role stops early

A role can stop part-way: a usage limit, a crash, a timeout or a lost connection. Before relaunching it, the orchestrator checks what it left behind:

1. `git status --short` and `git log --oneline -5`: uncommitted edits or unexpected commits.
2. The issue's text and its latest comments: a half-edited issue or a comment that stops part-way.
3. Anything it started: running processes, temporary system changes.

Treat partial output as unverified. Relaunch the role with a note of what's already done and what it must check or redo, never with what it was about to do. If something can't be repaired without a judgement call, ask the human.

## Lifecycle

1. Pick the next open issue. If there are none, build the backlog (see Backlog).
2. The PM grooms it. Never skip this step.
3. The Engineer implements it, commits, and runs **Verify** following `_docs/agent-kit/procedures/verify.md`. With the Claude Code layer, a hook also re-runs **Verify** when the Engineer tries to finish.
4. The orchestrator notes the current commit (`git rev-parse --short HEAD`), then the QA engineer checks the issue.
5. After QA, the orchestrator runs **Assert clean** and confirms HEAD hasn't moved. If either fails, QA changed something: discard QA's verdict and run QA again.
6. On FAIL, go back to step 3 with the QA comment as input.
7. On PASS, the **decision point**: gather everything waiting for the human into one message and ask once. That's proposed AGENTS.md changes, spec notes from any role, other protected-file changes, choices the Engineer made that the issue doesn't cover, and risks QA reported outside the criteria. Show each as a diff or a short description, using the layouts in `_docs/agent-kit/procedures/asking-the-human.md`, with your recommendation. Then:
   - Apply approved AGENTS.md, spec and other protected-file changes in their own commits, with `HUMAN_APPROVED=1`.
   - If an approved change needs Engineer work, go back to step 3; QA re-checks only what changed.
   - For each risk the human wants handled later, the PM files a follow-up issue.
8. Clean up, then write the session summary following `_docs/agent-kit/procedures/session-summary.md`:
   - Confirm nothing started during the issue is still running (`make <name>-stop` for each).
   - Confirm temporary system changes are undone, or that the human chose to keep them.
   - If a `.scratch/` script is worth keeping, propose it as a test or a make target at the decision point (step 7). Nothing in `.scratch/` survives cleanup.
   - Run `make clean-scratch`. It empties `.scratch/`, including session logs and test tokens, and refuses while a started process is still running. Record in the summary that it ran.
9. Close the issue. Only the orchestrator closes issues: after QA posts PASS, or as not planned after the human approves a backlog review.
10. The human reviews the diff and pushes (see Commits).
11. Repeat until the backlog is empty and every part of the spec is built.

## Commits and pushes

- Small, focused commits at logical milestones; messages say what changed and why.
- Attribution comes from the tool's settings (see Commit attribution in `blueprints.md`). Agents don't add their own co-author lines.
- Staging, protected files and hooks follow the Conventions in `AGENTS.md`.
- **Only the human pushes.** Before pushing, the human reads `git diff origin/main --stat -- .`, then the full diff, and asks about any changed file outside the issue's Constraints. A clean QA report is not proof of a clean diff. The pre-push hook then runs **Verify**. In the local sandbox profile, the human does all of this from the clean clone, and the push check runs **Verify** instead (`environments.md`).

## Keeping the setup current

`_docs/agent-kit/blueprints.md` lists what the project should have and when. When the project gains a capability listed there (a test framework, e2e tests, migrations, a linter), propose the matching blueprint, following the same approval rule as other AGENTS.md changes. To check everything at once, re-run `_docs/agent-kit/setup.md` in review mode.

## Definition of done

An issue is done when:

- **Verify** passes and QA has posted PASS, so every acceptance criterion is met.
- The changes are committed.
- Docs affected by the change are updated, and any AGENTS.md change has human approval.
- The session summary is written.
- The orchestrator has closed the issue.

The human's diff review and push come after this, outside the agent's definition of done.
