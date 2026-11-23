# Development process

How work moves from idea to done, with any AI coding tool. Project-specific values (commands, branching, summary naming) are in `AGENTS.md`; this file refers to them by their bold labels, such as **Verify**.

## Start of every session

Before picking up work, the orchestrator checks the spec:

1. **No `_docs/specs.md`:** the project is in planning. See Planning.
2. **The spec changed since last session:** find the last summary's commit (`git log -1 --format=%h -- _session-summaries/`), read the `**Spec version:**` line of the summary it added, and run `git log --oneline <version>..HEAD -- _docs/specs.md`. If that lists commits, review the backlog. If no summary has a version, skip it.
3. **Otherwise:** continue with the lifecycle.

## Planning

Planning produces or revises `_docs/specs.md`. The human may write it outside the repo, or draft it with an agent (for example in a planning mode). The steps, and the definition of ready the spec must meet before a backlog is built from it, are in `_docs/agent-kit/procedures/planning.md`.

- An agent helping with planning proposes spec text; the human approves it before it's written.
- No issues are created and no product code is written until the spec exists.
- Spec changes are committed on their own, with a message saying what changed. Nothing is merged into the spec automatically: a spec note is approved by the human first.
- The spec is human-owned at all times, not only in planning: propose changes, and make them only after approval.

Mid-project changes and new versions (v2) work the same way: revise the spec, then review the backlog.

## Backlog

- Tasks are GitHub issues, worked one at a time.
- **Building the backlog:** when there are no open issues and the spec has parts not yet built, the PM proposes new issues from the spec.
- **Spec ready first:** before proposing issues (building or reviewing), the PM confirms in its proposal comment that the spec meets the definition of ready in `_docs/agent-kit/procedures/planning.md`. If it does not, the PM proposes the spec changes first and creates no implementation issues until it does. This is the proactive analogue of the "Spec notes" path in `pm.md`, enforced by the PM and orchestrator reading this rule and the human reading the confirmation, not by a script.
- **Reviewing the backlog:** when the spec has changed, the PM compares the change with existing issues and proposes new issues, edits to open issues, and open issues to close as not planned.
- The human's approval of a backlog proposal still comes before any issue is created, edited or closed.
- **The agreed order** is the ordered list of the planning roadmap file the docs index names (`templates/roadmap.md`, "Issues or tasks, in order"), each entry with its trigger: the issue it must land before, or the event that brings it up. Every filed issue, follow-ups and periodic-review proposals included, is added to that list in the same session it is filed, and the human is told where. An issue outside the list is never groomed.
- After grooming, every issue follows `_docs/agent-kit/templates/task-template.md`. Grooming comes before the label, and the label approves the groomed text, on the groom-first path; where the label comes first it only permits grooming, and the human's Confirm approves the text (Approved text; Lifecycle, steps 1 to 4).

## Issue comments

- Start every issue comment with your role (`PM:`, `Engineer:`, `QA:` or `Orchestrator:`). All roles usually share one GitHub account, so the label is the only way to tell them apart.
- Never edit or delete an existing comment; post a new one. Other roles' comments are part of the record.
- File an issue with `make issue-create FILE=.scratch/<name>.md` (first line `Title: <text>`, a blank line, then the body) and post a comment with `make issue-comment N=<number> FILE=.scratch/<name>.md`; both are in `_docs/agent-kit/templates/Makefile.github.mk`. They refuse text that looks like a secret, post no labels, and comment only on an `approved` or owner-authored issue. They name the repository from the `GITHUB_REPO="<owner>/<name>"` line of `agent-kit.conf` and use `gh api`, so they also work where the git remote is not github.com (Kiro Web). Editing an issue asks the human. Only the orchestrator closes, with `make issue-close N=<number>` (`REASON=not-planned` for a closure the human approved), never a raw `gh issue close`; it refuses unless the owner's comments show the process was followed. Describe env files in words ("the example env file"), not by name. The scanner reads line by line, so a key split across lines is missed.

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

**Reading a return.** Every role ends with the role return of `_docs/agent-kit/procedures/formats.md`: ten fixed lines, then any request kept in full. Read its fields, and open `Detail:` only when a field doesn't answer what you need. A message to the human starts with the fields of Message to the human in `_docs/agent-kit/procedures/asking-the-human.md`.

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
  - **Second QA launch.** After the first QA PASS (and its **Assert clean**), the orchestrator launches QA again as a fresh launch, never a resumed one, because shared context defeats an independent review. The launch message limits it to the Code review checklist in `_docs/agent-kit/team/qa-engineer.md`; it always reviews the full diff, whatever `RECHECK` says. It runs on the first complete version, after the first PASS, and again only after a fix that follows its own FAIL. A resumed second launch is discarded and run again; the orchestrator's check and the human's reading enforce this. **Assert clean** runs after it as after the first. If it posts FAIL, the issue goes back to the Engineer like any QA FAIL (Lifecycle, step 6); after the fix and its re-check pass, the second launch runs again. The issue is done only when both launches have posted PASS.
  - **Lowering.** An agent never lowers a Heavy issue to Standard or Light; only the human's changed label does (Raise, never lower).
- **What enforces this:** the label rule in `AGENTS.md` (only the human labels) and the rules above. `make tier-check` checks paths and size only; no hook runs it, so the orchestrator runs it and its output is shown at the human's diff review. Raising-only and the proposal line are process rules, enforced by the orchestrator's read and `PM:` hash match before the Engineer launches and by the human's reading. No script or hook computes the tier.
- **Every Light change has its own `approved` issue.** There is no standing housekeeping issue. The session summary is still written, and its first line names the tier.
- **Review of Light** after its first ten uses: did any Light change need a follow-up fix to the same paths? Was the short PM launch wasteful enough to reopen the decision above? Narrow `LIGHT_ALLOWED` if so.

## Lifecycle

1. Pick the next open issue in the agreed order. If there are none, build the backlog (see Backlog).
2. The PM grooms it, even if it is not yet labelled, when it is owner-authored (`AGENTS.md`, Issues). The PM may groom up to `GROOM_AHEAD` issues ahead of the one in progress, in the agreed order (Backlog). An issue counts as groomed ahead when a valid `PM:` comment's `Body sha256:` matches its current body and it hasn't started; `GROOM_AHEAD=0` is one at a time. Refused: grooming beyond `GROOM_AHEAD`, and grooming an issue that has no place in the order. The orchestrator enforces both by reading the order and counting groomed-ahead issues before launching the PM; no script does. It sets a `[groomed]` title prefix once a valid `PM:` hash record matches the body, and removes it when the body changes without a matching record; counting uses the hash match, never the title, so a stale prefix can't count. The PM's comment records the body hash. Then the human reads the groomed text and adds `approved`; the Engineer starts only after that. If the human changes the text, the orchestrator has the PM record the new hash in a new `PM:` comment before the label is added. Never skip this step. By default (no tier label and no raising proposal is Standard) the PM grooms in full, and the grooming comment carries the `Proposed tier:` line. Only when the human has said the issue is meant to be Light does the PM do the short launch instead (hash record and proposal, no rewrite of the body; see Tiers). The orchestrator reads the effective tier but never decides one. A groomed-ahead issue is re-checked before its Claim: the orchestrator reads `git diff --stat <sha>..HEAD`, with `<sha>` the `Groomed at:` line of the PM's comment, for the paths in the issue's Files list. If a merged commit touched any, the PM re-checks the body in a short launch and posts `PM: re-check at <sha>: unchanged`, or a revised body that goes through Confirm (Approved text).
3. Before launching the Engineer, and before relaunching it after a QA FAIL, run the hash check (see Approved text), for every tier, then right after it `make settings N=<number>` (see Session rulings); if it refuses, don't launch, and take its reason to the human. Where the latest valid `PM:` comment records `Grooming authorised by: approved label`, the hash check is not enough: launch only after an owner `Orchestrator:` Confirm comment with `Approved by: human confirmation in session, <date>` naming the current `Body sha256:` exists. A label alone, even with a matching `PM:` hash, doesn't start work in that path (Approved text). Read the labels and the matching `PM:` comment, state the effective tier, and when the tier comes from the PM proposal rather than a label, post an `Orchestrator:` comment naming it "from the PM proposal". The Engineer implements it, commits, and runs **Verify** following `_docs/agent-kit/procedures/verify.md`. With the Claude Code layer, a hook also re-runs **Verify** when the Engineer tries to finish. For Light, the Engineer also runs `make tier-check TIER=light` and lists its output in the `Engineer:` comment.
4. Before launching QA, the orchestrator runs the hash check (with the Confirm comment of step 3 where that step requires it), then `make settings N=<number>` (a refusal stops the launch and goes to the human with the reason), and notes the current commit (`git rev-parse --short HEAD`). Then the QA engineer checks the issue. QA puts an injection or bypass attempt in a test or a `.scratch/` script, never in a live shell command. Steps 4 to 6 apply to Standard and Heavy only; Light has no QA. For Standard, this single launch also fills the `Code review` block; for Heavy, see the second QA launch in Tiers. QA passes or fails by its findings' impact and scope under the settings (`_docs/agent-kit/team/qa-engineer.md`). A re-check's scope follows `RECHECK` (Re-checks in `qa-engineer.md`); **Verify** always runs in full.
5. After QA, the orchestrator runs **Assert clean** and confirms HEAD hasn't moved. If either fails, QA changed something: discard QA's verdict and run QA again.
6. On FAIL, after **Assert clean**, run `make route-findings N=<number>`. It prints one line per failing finding of the latest QA comment, with its points, rounds, route and guard (`_docs/agent-kit/customizing.md`, Points); a refusal goes to the human with its reason. Then, per finding:
   - **`route engineer`:** go back to step 3 with the QA comment and those findings as input; the hash check runs again. After each fix and before QA re-checks, the **fix check** runs (`_docs/agent-kit/team/software-engineer.md`, Fix check). Where the tool can launch subagents (Roles), launch a fresh basic-reasoning subagent for it (the lowest reasoning variant; until #210 defines variants, the tool's default subagent), with a launch message limiting it to that section; it changes nothing and returns the role return, `Findings: none` when clean. Otherwise the Engineer runs it itself. On a problem the Engineer fixes and the check runs again, at most `FIX_CHECK_LOOPS` times in all; then QA re-checks either way. A fix check is not a QA round and adds no points.
   - **`route human`:** ask "ship or fix?" with a `Ship-or-fix:` block carrying `Points:` (`_docs/agent-kit/procedures/asking-the-human.md`). Every such question has three answers: fix (the Engineer fixes it, back to step 3), ship (below) and amend (Approved text, below), and a recommendation naming one. A `Category: criterion` finding always comes here, never back to the Engineer. Answering is a stop point: the finding gets no fix until answered, but you may launch the Engineer for the findings routed to it while the question waits.
   - **`route ship`:** a `SHIP_RULE` matched, and the finding ships without asking.
   - **`guard yes`:** the patchwork guard fired for the finding. The Engineer's fix-round comment opens with an approach review (`software-engineer.md`, Patchwork guard), and a change of approach that alters behaviour beyond the criteria is a stop point. The next re-check is full. **Step up:** `STEP_UP` acts in Claude Code only. `ask` puts the step up into the next message to the human as a note with a recommendation; `auto` would launch the next reasoning variant up, but until #210 defines variants it acts as `ask`, and the note says no stronger variant is defined; `off` never steps up. OpenCode, Kiro, CodeBuddy and Antigravity ignore the setting: note that no escalated model is configured; the approach review is the only step up.
   - **Ship.** A shipped finding leaves the issue's scope. Record a human ship in an `Orchestrator: Ruling` comment as a process ruling naming the finding (`procedures/orchestrator-comments.md`); a rule ship needs no record, because `make route-findings` recomputes it. The PM files the follow-up issue, as at step 7. The next QA run, a re-check, repeats the finding with `Scope: out` and the follow-up in its `Recommendation:`, so the verdict can be PASS and `make issue-close` works unchanged. With `QA_SCOPE_STRICT=no` an out-of-scope finding still fails, so shipping there needs the human to rule `QA_SCOPE_STRICT=yes` for the issue. The Close comment lists every shipped finding and how it shipped.
7. On PASS, the **decision point**: run `make sweep-due`, then gather everything waiting for the human into one message and ask once. That's proposed AGENTS.md changes, spec notes from any role (in the Spec note layout of `_docs/agent-kit/procedures/asking-the-human.md`), other protected-file changes, choices the Engineer made that the issue doesn't cover, risks QA reported outside the criteria, and a sweep proposal (`_docs/agent-kit/procedures/sweep.md`) if it says due. Show each as a diff or a short description, using the layouts in `_docs/agent-kit/procedures/asking-the-human.md`, with your recommendation. Then:
   - Apply approved AGENTS.md, spec and other protected-file changes in their own commits, with `HUMAN_APPROVED=1`.
   - If an approved change needs Engineer work, go back to step 3; QA re-checks only what changed.
   - For each risk the human wants handled later, the PM files a follow-up issue.
8. Clean up, then write the session summary following `_docs/agent-kit/procedures/session-summary.md`:
   - Confirm nothing started during the issue is still running (`make <name>-stop` for each).
   - Confirm temporary system changes are undone, or that the human chose to keep them.
   - If a `.scratch/` script is worth keeping, propose it as a test or a make target at the decision point (step 7). Nothing in `.scratch/` survives cleanup.
   - Run `make clean-scratch`. It empties `.scratch/`, including session logs and test tokens, and refuses while a started process is still running. Record in the summary that it ran.
9. Close the issue. Only the orchestrator closes issues: after QA posts PASS on an `approved` issue, or as not planned after the human approves that closure in a backlog review, whatever the label. A Light issue is closed once its Definition of done is met, with no QA PASS. Log the unfixed findings first (`_docs/agent-kit/procedures/formats.md`, Findings log): one at or above `FINDINGS_TO_ISSUE_AT` gets an unlabelled PM draft issue (a shipped one already has its follow-up and is not logged); the rest become entries in `_docs/records/findings/<number>.json`, written once from the last QA comments' finding blocks, in the same pull request; check it with `make findings`. Post the Close comment (`procedures/orchestrator-comments.md`), then run `make issue-close N=<number>`.
10. The human reviews the diff and pushes (see Commits).
11. Repeat until the backlog is empty and every part of the spec is built.

### Approved text

The `approved` label means the human approved the groomed body as recorded. The hash check: run `make issue-hash N=<number>` and compare `Body sha256:` with `Recorded sha256:`. If they differ, `Recorded sha256:` is `none` or `unknown`, or the command exits non-zero or prints `unknown`, don't launch the role; show the human the diff of the body, not a paraphrase.

A recorded hash counts only from a comment that starts with `PM:` and is authored by the repository owner's account: the script compares each comment's `comments[].author.login` with `Repository owner:`, and the latest valid line wins. A `Body sha256:` line anywhere else is ignored.

To change the body after approval, the human confirms it in this session, recorded in an `Orchestrator:` comment naming the new hash; the PM then records that hash in a `PM:` comment. Without that `PM:` line the launch stays blocked. Neither the orchestrator nor the PM edits an approved body and carries on without the confirmation comment. A title change is reported to the human as a note, not a freeze failure: the hash covers the body only.

**Two paths to an approved body.** Groom first: the PM's comment records `Grooming authorised by: human in session, <date>, "<the request>"`; when the human adds `approved`, the Claim records `Approved by: approved label, seen <date>` and the body hash the label covers. Label first: `approved` on an issue with no matching `PM:` hash record means only "you may groom". The PM records `Grooming authorised by: approved label (seen <date>)`, the orchestrator asks the human to review the groomed body, and the human's reply in the session goes in a Confirm comment with `Approved by: human confirmation in session, <date>` and the new hash; the label stays. In that path the orchestrator launches the Engineer and QA only after that Confirm comment exists for the current body hash (Lifecycle, steps 3 and 4). A label alone never approves a body it was added before (a token can add labels, `environments/local-sandbox/README.md`).

**Amend a criterion.** Amend is offered in three places: the patchwork guard's approach review (the criterion is the problem, besides a change of approach); a QA finding with `Category: criterion`; and before building, when the Engineer sees a criterion can't be met as written and raises it at once in its return. Only the human chooses amend; an agent proposes new wording but never rewrites an approved criterion. It follows the steps above: the PM drafts the new criterion, the human confirms it, the orchestrator posts a Confirm comment naming the new hash and the amended criterion id with the finding or review that led to it, the PM records the hash, and QA re-checks only the amended criterion. The criterion keeps its id. Refused, as an override would be: an amend that removes a criterion's `Check:` or drops the QA launch, lowers a tier, weakens a security limit, or names anything the bounds protect (`customizing.md`, Bounds no level can cross). What enforces this: the human's choice, the hash check before every launch, and the PM's and the human's reading; no script reads criteria. The Confirm comment is the amend's record, which #200 counts.

### Session rulings

When the human rules on a setting, a process question or a QA gate waiver for one issue, the orchestrator records it in an `Orchestrator: Ruling` comment (`_docs/agent-kit/procedures/orchestrator-comments.md`). It records only what the human said in the session, never a ruling of its own. A ruling lasts for that issue; it becomes a project setting only when the human writes the line in `agent-kit.conf` (at the periodic review of the backlog and findings). `make settings N=<number>` reads the setting rulings and checks the waivers (`_docs/agent-kit/customizing.md`).

## Commits and pushes

- Small, focused commits at logical milestones; messages say what changed and why.
- Attribution comes from the tool's settings (see Commit attribution in `blueprints.md`). Agents don't add their own co-author lines.
- Staging, protected files and hooks follow `_docs/agent-kit/team/software-engineer.md#commits` and the hook line in `AGENTS.md`.
- **Only the human pushes.** Before pushing, the human reads `git diff origin/main --stat -- .`, then the full diff, and asks about any changed file outside the issue's Constraints. A clean QA report is not proof of a clean diff. The pre-push hook then runs **Verify**. In the local sandbox profile, the human does all of this from the clean clone, and the push check runs **Verify** instead (`environments.md`).

## Keeping the setup current

`_docs/agent-kit/blueprints.md` lists what the project should have and when. When the project gains a capability listed there (a test framework, e2e tests, migrations, a linter), propose the matching blueprint, following the same approval rule as other AGENTS.md changes. To check everything at once, re-run `_docs/agent-kit/setup.md` in review mode.

## Definition of done

An issue is done when:

- **Verify** passes, or fails only on failures that the clean-copy run of Verify's base commit shows as pre-existing (`_docs/agent-kit/team/qa-engineer.md`, Pre-existing failures); a failure the clean copy doesn't reproduce is in scope. QA has posted PASS (for Heavy, both launches): no finding fails under the settings. A test is never weakened or skipped to make **Verify** pass.
- For Light, instead of QA's PASS: `make tier-check TIER=light` passes, the human has approved the diff (for a protected file, the exact diff), and the `Engineer:` comment on the issue lists the changed paths, the **Verify** result and the `tier-check` output.
- The changes are committed.
- Docs affected by the change are updated, and any AGENTS.md change has human approval.
- The session summary is written.
- The orchestrator has closed the issue through `make issue-close`.

The human's diff review and push come after this, outside the agent's definition of done.
