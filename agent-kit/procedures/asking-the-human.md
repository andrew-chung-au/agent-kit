# Ask the human

How any role asks the human for an approval or a decision, so the human can see what's happening, why, and what else could be done before answering.

## Command descriptions

Most tools show a short description with each command, including when they ask the human to approve it. Write every description as what the command does and what it's for, naming the issue and step:

- Good: "Send the ResponderTest alert to check criterion 4 of #10"
- Not enough: "Send alert", "Run check", "Inspect folder"

If the tool asks for approval only because it couldn't check the command, the description is all the human sees. Prefer rewriting the command in a simpler form (see the command-shape rules in the Non-negotiables of `AGENTS.md`).

## When to ask before acting

Some actions need the human's approval on their merits, not just because the tool couldn't check the command:

- changing system configuration (firewall rules, packages, services, git config)
- stopping a process you didn't start
- reading or writing anything outside this folder
- installing a dependency, or anything large into `.scratch/`
- committing a protected file
- anything that can't be undone

For these, send an approval request before running anything. The approval prompt that follows should then hold no surprises.

**If you're a subagent,** the human sees only your commands, not your messages. Don't run the command. Stop, and return the request to the orchestrator as your final message, with a note of where you got to. The orchestrator asks the human and resumes you with the answer.

## Approval request

```
Approval needed: <what you want to do, in one line>
- Why: <the issue and step it serves, and what goes wrong without it>
- Seen before: <the earlier issue or runbook entry, or "no">
- What will run or change: <the exact command(s), or the diff>
- Checked just now: <the check that produced any addresses, IDs or ports in the command, and its result>
- Risk and undo: <what it could affect and for how long, and the command that reverses it, or "can't be undone">
- Alternatives: <other ways to reach the same goal, each with its cost: fixing the cause rather than
  working around it, the human running it themselves, skipping it>
- Recommendation: <which option, and why>
```

Every field is required. Write "none" or "no" rather than leaving one out.

- **Current values.** Take addresses, IDs, ports and paths from a check you ran just now, not from an earlier session or summary. Docker networks, process IDs and similar values change when things are recreated.
- **System changes.** Offer the human running the command themselves as an option, and run commands with `sudo` only if the human chooses that.
- **When the human runs it.** Put the steps in a task file (`process.md`, Human tasks) and name it in "What will run or change"; don't copy its steps into the request.
- **Recurring problems.** If the same approval came up in an earlier issue, say so. Propose a runbook entry for it (see Known environment issues in `blueprints.md`), so next time the request can point to it.

Example:

```
Approval needed: add a temporary firewall rule so the containers can reach each other.
- Why: #11, criterion 3. Grafana can't reach Prometheus, so the 5xx alert can't fire; a stale rule
  in the codespace drops traffic between containers.
- Seen before: yes, in #9. No runbook entry yet; I'll propose one at the decision point.
- What will run: sudo iptables-legacy -I DOCKER-USER -s 172.18.0.0/16 -d 172.18.0.0/16 -j ACCEPT
- Checked just now: docker network inspect order-tracker_default -f '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
  printed 172.18.0.0/16.
- Risk and undo: allows traffic only inside the project's Docker network, until the codespace restarts.
  Undo: sudo iptables-legacy -D DOCKER-USER -s 172.18.0.0/16 -d 172.18.0.0/16 -j ACCEPT
- Alternatives:
  1. You run the rule yourself, and I continue. No sudo for the agent.
  2. I run it, and remove it at cleanup.
  3. Restart the codespace, which clears the stale rule (fixes the cause, but stops everything running).
  4. Skip the live checks (criterion 3 stays unverified, so QA can't pass the issue).
- Recommendation: 1. It's narrow, has a one-line undo, and keeps sudo with you.
```

## Decision question

For choices rather than permissions: a design choice, a criterion that can't be met as written, a risk QA found.

```
Decision needed: <the question, in one line>
- Context: <the issue and step, and what led here>
- Options:
  1. <option>: <what happens, and its cost or risk>
  2. <option>: <...>
  Include "defer" or "do nothing" when that's possible.
- Recommendation: <which option, and why>
- If you don't answer: <what happens meanwhile, or that the work is blocked>
```

Example:

```
Decision needed: how should the on-call agent's "curl to localhost only" limit be enforced?
- Context: #10, QA FAIL on criterion 6. The tool's prefix rules can't limit curl to one host:
  a rule for http://localhost also matches http://localhost.example.com.
- Options:
  1. A `make <probe-target> URL=...` wrapper that checks the URL, and no direct curl: simple and testable,
     but the agent could still edit the Makefile during a run.
  2. A tool hook that parses every curl command: stronger, but more code and harder to test.
  3. Keep the prefix rules and document the gap: no work, but the limit isn't enforced.
- Recommendation: 1. It can be enforced and tested now, and protecting the Makefile stops the
  agent committing a looser version.
- If you don't answer: QA's other finding goes back to the Engineer; this criterion stays failed.
```

If your tool offers multiple-choice questions, use the same content: the context in the question, each option's consequence in its description, and your recommendation first and marked.

Keep requests short: one line per field. Several decisions at once go in one message, each in this layout, as at the decision point in `process.md`.

## Message to the human

The orchestrator's message to the human starts with fixed fields, in the line rule of `_docs/agent-kit/procedures/formats.md`. Line 1 is `Needs you: <n> decision points, <n> ship-or-fix`. Then one block per item, each after one blank line:

- a decision: `Decision: D-<issue>-<n>`, `Question:`, `Impact:` (`L`, `M`, `C`), `Recommended:`
- a ship-or-fix: `Ship-or-fix: F-<issue>-<n>`, `Impact:`, `Effort:` (`S`, `R`, `E`), `Points:` (the finding's points from `make route-findings N=<n>`, a whole number from 1), `Recommended:`

The counts match the blocks. Then a blank line and `Status: <text>`. Anything after that is detail, such as the approval requests and decision questions above in full. `Recommended:` is never empty; `none` only as `none, because <reason>`. Check the message with `make check-format KIND=message FILE=<file>`.

**Ship or fix has three answers.** Every ship-or-fix question offers them, and its `Recommended:` names one:
- **fix:** the code is wrong; the Engineer fixes it.
- **ship:** the criterion is right, but finishing it now isn't worth it; the finding leaves the issue's scope and a follow-up issue takes it (`process.md`, Lifecycle step 6).
- **amend:** the criterion is wrong, not the code; the human changes the criterion through the approved-text steps (`process.md`, Approved text).

Only the human chooses ship (unless a `SHIP_RULE` ships it) or amend. Answering is a stop point: a finding routed to the human gets no fix until answered.

**Logged findings.** A finding that is logged and fails nothing (`procedures/formats.md`, Findings log) is reported under a heading that names its grade and outcome, then one bullet per finding: its id (the one `make findings` prints), then one or two plain sentences on what happens and when it matters. Findings that fail or come to the human keep the ship-or-fix block. `check-format KIND=message` does not check this layout; it is for the Close comment and chat.

```
Findings (Low: logged)
- F-12-2: the signup handler logs each username. Harmless until #14 adds log levels.

Findings (Medium, out of scope: logged)
- F-12-3: the lint run is red on the base commit too. Every issue sees it until it is fixed.
```

```
Needs you: 1 decision points, 1 ship-or-fix

Decision: D-12-1
Question: Should signup log usernames at all?
Impact: L
Recommended: No; drop the log line in #14.

Ship-or-fix: F-12-2
Impact: M
Effort: S
Points: 4
Recommended: Ship; fix it with #14.

Status: #12 failed QA at 1a2b3c4; F-12-2 has failed three re-checks and waits for fix, ship or amend.
```

## Spec note

For spec text that looks wrong or incomplete. Roles raise it; the human decides, and only then is `_docs/specs.md` changed.

```
Spec note: <what is wrong or missing, in one line>
- Added: <requirement>, or "none"
- Changed: <new text> (was: <old text>), or "none"
- Removed: <requirement>: <reason>, or "none"
- Why: <one line, with the issue or evidence>
```

A one-line note may skip the layout. Nothing is merged into the spec automatically (`process.md`, Planning).
