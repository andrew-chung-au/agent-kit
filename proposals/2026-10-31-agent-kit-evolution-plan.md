# Agent kit evolution plan

**Status:** proposal only. Nothing in this plan has been implemented. Decision 2026-11-02: the 'Approved-by' commit trailer (G9) is dropped as redundant with `HUMAN_APPROVED` plus the issue comment.
**Date:** 2026-10-31
**Scope:** what to take from `vuln-triage/agent-kit`, how to make permission
auditing work, how to speed the process up without losing its controls, and
how to fix the documentation sprawl.

This plan deliberately separates four questions that were being mixed together
in the vuln-triage work:

1. Which changes are general enough for the main kit?
2. How do we actually observe approval requests?
3. Which changes need the full PM → Engineer → QA chain?
4. How should project documentation and templates be organised?

---

## 1. What the comparison found

`vuln-triage/agent-kit/` is an evolved but **incomplete** snapshot of the kit.
Several capabilities the docs advertise live in the VulnTriage project's own
Makefile, not in the kit folder.

Examples:

- `make issue-create`, `issue-comment`, `issue-close`, `issue-dump` are
  implemented in the VulnTriage Makefile. The kit README and role files refer to
  them, but the kit does not ship them.
- `make permission-report`, `branches`, `ci`, `ci-run` and `file-at` are also in
  the project Makefile, not the kit.
- `permission-sweep.md` depends on `make permission-report` and
  `_docs/permission-sweeps.md`; neither exists in the kit.
- `cloud_session_start.sh` is not registered by `settings.json` or by the
  cloud-session fragment.
- `blueprints.md` and `setup.md` were not updated for any of the new modules.
- Some content is project-specific: Postgres, issue numbers `#17/#35`, `#60`,
  `sha256sum`, and `make openapi-validate` / fixture / compose targets.

The lesson is not "copy the folder". It is: **take the generic ideas, keep the
project-specific machinery in a project blueprint, and do not document features
that do not exist.**

---

## 2. Principles for this work

1. **Observe, don't ask agents to remember.** Permission auditing must come
   from a tool hook that records real permission events. Instructions to agents
   to write down approvals failed in practice: from the agent's side there was
   no request to see.
2. **One canonical source per topic.** Docs, settings and templates must not
   repeat each other. Repetition is what made `_docs/` chaotic and expensive in
   tokens.
3. **Process scales with risk.** A typo fix and a schema change must not take
   the same path through PM, Engineer and QA.
4. **Optional means opt-in.** Cloud push, Ponytail, GitHub helpers and extra
   roles stay separate modules, never default behaviour.
5. **No new dependency without a decision.** Replace `jq` in kit checks with
   `python3 -m json.tool`, which the kit already requires.
6. **Everything must pass `make test` and `make verify`.** New scripts and
   plugins need a syntax check and at least one behaviour test.

---

## 3. Workstream A — What to take from vuln-triage

### A1. Adopt (core kit)

| Change | Why | Notes |
|---|---|---|
| Read/search guidance: use the tool's read/grep/glob, not shell `cat`/`head`/`tail`/`grep`/`find`/`sed` | Cuts prompts and token use; matches how the tools are designed | Update `process.md` and `templates/AGENTS.md.template` |
| Routine issue writes are allowed; issue edits/closes ask | Removes pointless decision-point items | Keep the project's own issue-label rules as project-specific overlays |
| `.env` edit deny in both tool layers | Current kit denies reading but not editing | Add `Edit(.env*)` to Claude Code and OpenCode |
| Expanded read-only permissions (`git remote`, `git cat-file`, `gh issue view/list`, `gh run list/view`, `sha256sum` optional) | Fewer prompts for safe inspection | Prefer `make` helpers over broad shell rules |
| `scan-issue-body.sh` | Secrets in issue bodies are a real leak path | Only useful once an issue wrapper calls it |
| Protected-change approval record | Makes protected commits auditable | Define the format in `asking-the-human.md`; do not rely on agent memory |
| `check-scripts` target | Catches broken kit scripts before `make verify` | Fix path drift and remove `jq` |
| `blueprints.md` / `setup.md` rows for every new module | The catalog is the source of truth | Currently missing for all new material |

### A2. Redesign, do not port as-is (permission audit)

The following vuln-triage changes assume agents can record approvals:

- the "Commands and changes that required approval" line in `team/*.md`;
- the **Permission review** section in the session-summary template and
  procedure;
- `procedures/permission-sweep.md`;
- `make permission-report` reading session summaries.

**Do not port these as the source of truth.** Replace them with the hook-based
design in section 4. A short human-written summary can remain, but the data must
come from the tool.

### A3. Move to an optional GitHub workflow template

These are useful but too large for the core Makefile template:

- `issue-create`, `issue-comment`, `issue-close`, `issue-dump`;
- `branches`, `ci`, `ci-run`, `file-at`;
- `permission-report` (redesigned, see section 4).

Recommended shape:

```
agent-kit/templates/Makefile.github.mk   # optional, merged at setup
agent-kit/scripts/issue-create.sh        # or make-only, project choice
agent-kit/scripts/issue-comment.sh
agent-kit/scripts/scan-issue-body.sh
```

The make-level validation in the VulnTriage Makefile is good: digits-only issue
numbers, `.scratch/`-only file paths, character allow-lists, symlink and size
checks, dollar-quoting for `$(value ...)`. Keep that style, but add tests for
the reject cases. Do not put 100+ lines of GitHub helpers into every project by
default.

### A4. Adopt the cloud-session module as opt-in

- Keep core "no push".
- Keep `AGENT_KIT_CLOUD_PUSH=1` + `CLAUDE_CODE_REMOTE=true` + current
  `claude/*` branch + exact `git push -u origin <branch>`.
- Tighten the fragment's `ask` rule to the exact form the guard allows.
- Either register `cloud_session_start.sh` as a `SessionStart` hook or drop it.
- Add a `blueprints.md` row and a `setup.md` install step.
- Add a behaviour test for `guard_git.py` that covers: no env var, local
  session, `main`, non-`claude` branch, force push, another ref, and the happy
  path.

### A5. Do not include

- README version 1.10 and its changelog as written (claims missing features).
- Postgres, Grafana/Prometheus, issue numbers, `sha256sum` and any other
  VulnTriage-specific text.
- `openapi-validate`, fixture recording, demo, compose and dev-server targets.
- `git add *` / `git commit *` **allow** rules in OpenCode. OpenCode has no hook
  to stop broad staging, so this would bypass the kit's explicit-path rule.
- `make ci-run` as a routine allow until it is clear whether it triggers work.
- Claims about targets that the kit does not ship.
- The AI usage report and AI usage log (`ai-usage-report.md`,
  `ai-usage-log.md`). They are specific to the AI devtools course, not a
  general kit capability.

---

## 4. Workstream B — Permission logging that actually works

### B1. Why the current idea failed

The human sees the permission prompt. The agent does not. Asking the agent to
record "commands that required approval" creates a second-hand log that is
incomplete and easy to skip. It also adds text to every role comment and
session summary, which is exactly the kind of duplication that slows sessions
down.

### B2. OpenCode: log real permission events

OpenCode's plugin API exposes the events we need:

- `permission.ask` gives a `Permission` object and the current
  `output.status` (`ask`, `deny`, `allow`);
- the event bus emits `permission.updated` when a request is created and
  `permission.replied` when the human answers.

A small auto-discovered plugin can append JSONL records without changing the
decision:

```
.opencode/plugins/permission-log.ts
```

Proposed record shape:

```json
{"event":"ask","time":"2026-10-31T10:00:00Z","sessionID":"...","id":"...","type":"bash","pattern":"git push *","title":"...","callID":"...","status":"ask"}
{"event":"reply","time":"...","sessionID":"...","permissionID":"...","response":"once"}
```

Rules:

- Observe only. Never mutate `output.status`.
- Write to a git-ignored local folder, for example
  `.agent-kit/logs/permissions/YYYY-MM-DD.jsonl`.
- Redact secrets and truncate long commands. Reuse the patterns from
  `scan-issue-body.sh`.
- Rotate daily and cap size.
- Do not log file contents or full diffs.

### B3. Report instead of a summary section

`make permission-report SINCE=<commit>` should read the JSONL logs and group by
permission type and pattern:

- how many times it was asked;
- how many times the human allowed, denied or chose "always";
- the first and last occurrence;
- the sessions that produced it.

The existing make-level `SINCE` validation is worth keeping (lowercase hex,
7–40 characters, checked before any shell command).

### B4. Claude Code

Claude Code does not expose the same structured permission-reply event. Options,
in order:

1. `PreToolUse` currently runs `guard_git.py`. Extend it to log every git
   command it sees, including whether it blocked it. This gives accurate data
   for the commands the guard knows about.
2. Test whether the `Notification` hook carries enough information for
   permission prompts. If it does, add a logger.
3. If neither is reliable, document the gap: permission reports are complete
   for OpenCode and partial for Claude Code. Do not fake it.

### B5. What to remove

- The approval lines from `team/*.md`.
- The "Permission review" instructions that tell agents to collect their own
  approvals.
- `permission-sweep.md`'s dependency on session summaries.
- The idea that a role comment is the audit trail.

Keep a short "Approvals" note only for non-tool approvals (system changes,
installs, things outside the folder), and take those from the hook log where
possible.

### B6. Acceptance criteria

- A real OpenCode ask produces exactly one `ask` record and one `reply` record.
- A denied/blocked command is recorded without the secret text.
- The report counts distinct sessions, not comments.
- No permission log is ever committed; `.gitignore` covers it.
- `make test` syntax-checks the plugin and the report script.

---

## 5. Workstream C — Process tiers and role model

### C1. Change classes

Classify every issue at creation or triage. The class decides the roles and the
gates, not the agent's mood.

| Class | Examples | Path | Gates |
|---|---|---|---|
| **A. Trivial** | typo, comment, link, formatting, docs-only | Engineer (or human) directly | `make verify`, `make docs-check`, human diff review |
| **B. Small** | one component, clear acceptance, no interface change | short issue → Engineer → self-check | `make verify`, optional independent review |
| **C. Standard** | behaviour change, two or more components | PM groom → Engineer → QA | full verify, QA PASS, decision point |
| **D. Architectural** | schema, API, security boundary, cross-repo interface | Architect writes spec/ADR → PM → Engineer → QA → Reviewer | spec approval, verify, QA PASS, independent review, human decision |
| **E. Incident** | production outage, on-call response | project-specific responder | project-specific |

Add a **Change class** field to the issue template and a short triage table to
`process.md`.

### C2. Roles

Keep the core team small:

- **PM** — only for class C and D, and for backlog/spec work.
- **Engineer** — class A–D.
- **QA** — class C and D. For class B, automated checks plus optional
  reviewer replace a full QA session.
- **Architect** (new, optional) — class D: spec, ADR, schemas, interfaces,
  module boundaries. Never writes application code.
- **Reviewer** (new, optional) — fresh-context review of a diff or PR for
  class C/D. Checks bugs, security, tests, scope and docs. This is the peer
  project's "independent reviewer" idea.
- **Docs checker** — a script, not a role: `make docs-check`.
- **On-call responder** — not part of the kit; keep it as an example blueprint.

Rationale: add roles only where a distinct context or authority is needed.
Deterministic checks belong in scripts, not in another agent.

### C3. Fast paths

- **Docs-only:** no PM, no QA. `make docs-check` + `make verify` + human
  review.
- **Small:** one issue comment with the plan, implement, verify, human review.
  QA is optional.
- **Standard/architectural:** the current chain, but with a time-boxed PM groom
  and a single decision point.

### C4. PR profile (optional)

The peer project's flow is worth offering as a profile, especially for cloud
sessions:

1. branch per issue (`claude/<issue>-<name>` or `feat/<issue>-<name>`);
2. Conventional Commits;
3. PR with `Closes #N`, change class, test output and rollback;
4. CI runs `make verify`;
5. independent reviewer (fresh context) comments;
6. human approves and merges.

This fits the cloud-session module naturally: the agent pushes its branch, the
human reviews the PR and merges. Keep the current commit-direct profile as the
default for local sandboxes.

### C5. Metrics

Track only three things, in the session log or a small dashboard:

- wall-clock time from issue to merge, by change class;
- number of human approval prompts per issue;
- tokens or cost per issue (Ponytail can report this).

Use them to tune the classes, not to rank agents.

---

## 6. Workstream D — Documentation architecture

### D1. Target structure

Do not reorganise everything at once. Add a stable index, a logs folder and an
archive, then migrate the worst offenders.

```
_docs/
  README.md              # index: one line per canonical doc, owner, status
  specs.md               # product source of truth (human-owned, protected)
  architecture/          # ADRs and module boundaries
  runbooks/              # operational fixes (symptom, check, fix, undo)
  tasks/                 # backlog / task descriptions
  reviews/               # review reports, one file per review
  logs/                  # one file per agent session, never a shared log
  proposals/             # ideas not yet accepted; each has a status
  archive/               # superseded docs, kept but out of the way
  agent-kit/             # the kit
```

### D2. Logs are a folder, not a file

Replace a shared dated log file with:

```
_docs/logs/2026-10-31-issue-123-engineer.md
_docs/logs/2026-10-31-issue-123-qa.md
_docs/logs/2026-10-31-permission-sweep.md
```

Each agent writes its own file. No agent edits another agent's file. The
orchestrator updates `_docs/README.md` or the index is generated by
`make docs-check --fix`. This removes the shared-file contention the user saw
with multiple agents.

This is about session and review notes, not AI usage accounting. VulnTriage's
`ai-usage-report.md` and `ai-usage-log.md` stay course-specific and are not
part of the kit.

### D3. Front matter and rules

Every canonical doc starts with:

```yaml
---
owner: human | pm | engineer | qa
status: draft | active | superseded
canonical-for: authentication | permissions | deployment | ...
last-reviewed: 2026-10-31
supersedes: path or "none"
---
```

Rules:

- one canonical doc per topic; link instead of copying;
- proposals expire: accepted → canonical, rejected → archive;
- no dated copies in the root;
- no doc without an index entry;
- runbooks are the only place for environment fixes.

### D4. `make docs-check`

A stdlib Python script, run in `make verify` only for docs changes or as a
separate target:

- every doc has front matter and an index entry;
- index entries point to real files;
- no two active docs claim the same `canonical-for`;
- no broken relative links;
- no `superseded` doc linked from an active doc;
- no file over a size limit (encourage splitting);
- no stale `last-reviewed` beyond a threshold (warning only).

### D5. Migration

1. Create the index, logs folder and archive.
2. Move superseded/ddated docs to `archive/`; add `supersedes`.
3. Collapse duplicate runbooks into `runbooks/`.
4. Move proposals into `proposals/` with a status.
5. Add `docs-check` and fix the first failures.
6. Only then consider moving `specs.md`; it is protected and used by the kit.

---

## 7. Workstream E — Templates

The agents currently look for a template, fail to find one, and invent one.
Fix that with templates and make targets.

### E1. Files

```
agent-kit/templates/issue.md          # goal, AC, out of scope, constraints, change class
agent-kit/templates/pr.md             # summary, Closes #N, class, test output, risk/rollback, checklist
agent-kit/templates/adr.md            # context, decision, consequences, alternatives
agent-kit/templates/review.md         # findings, severity, evidence, recommendation
agent-kit/templates/log.md            # one session log
agent-kit/templates/docs-index.md     # index skeleton
agent-kit/templates/github/ISSUE_TEMPLATE/task.yml
agent-kit/templates/github/pull_request_template.md
```

### E2. Make targets

- `make issue-create` uses the issue template by default.
- `make pr-create` (new) uses the PR template, validates the body file the same
  way `issue-create` does, and runs `scan-issue-body.sh`.
- `make review-comment` (optional) posts a review file.

### E3. Prompt wiring

- `AGENTS.md` points to the templates explicitly.
- `team/pm.md`, `team/software-engineer.md` and `process.md` say which template
  to use and where it lives.
- The templates are protected in `agent-kit.conf` once installed.

### E4. Acceptance

- An agent asked to "create an issue" finds `templates/issue.md` without
  searching.
- `make issue-create` rejects a path outside `.scratch/`, a symlink, an empty
  file, an oversized body and a body with a secret.
- The PR template includes the test output and the change class.

---

## 8. Workstream F — Ponytail

[Ponytail](https://github.com/DietrichGebert/ponytail) is a prompt/skill that
makes an agent look for the smallest correct change: reuse first, then standard
library, then the minimum implementation. It ships as an agent skill/plugin and
also gives `/ponytail-review` and `/ponytail-audit`.

### F1. Recommendation

Offer it as an **optional coding-discipline skill**, not core kit behaviour.

Reasons to consider it:

- less code, fewer tokens, faster sessions;
- a review/audit command that complements the independent reviewer;
- MIT licence and a plain `SKILL.md`, so it is easy to inspect.

Reasons to keep it optional:

- it changes coding behaviour in every session;
- it can conflict with acceptance criteria or security requirements if applied
  blindly;
- it is third-party supply chain; pin a commit or npm version and review the
  skill text;
- it does not replace QA or the kit's verify gate.

### F2. Trial

1. Install it in one project only (VulnTriage is the natural candidate).
2. Pin the version/commit.
3. Run one class-B and one class-C issue with and without it.
4. Compare time, tokens, lines changed and test coverage.
5. Keep it if it reduces work without reducing tests or security.

### F3. Integration

- Add a `blueprints.md` row: "Optional code-minimalism skill".
- Document install in the tool layer's `START.md`, not in core `AGENTS.md`.
- Mention `/ponytail-review` as an optional input to the Reviewer role, not a
  gate.
- Do not make it a default for security-sensitive or data-loss-sensitive code.

---

## 9. Delivery phases

### Phase 0 — Decisions (no code)

- Choose scope: core-only, core + permission logging, or all workstreams.
- Decide whether to open an issue (this repo requires `approved` issues) or
  treat the plan as human-directed work.
- Decide whether `_docs/specs.md` stays the spec path or moves.

### Phase 1 — Quick wins (low risk)

- Port the read/search guidance, `.env` edit deny, read-only permissions, and
  `scan-issue-body.sh`.
- Fix `check-scripts` (paths, no `jq`).
- Add `blueprints.md`/`setup.md` rows.
- Remove or correct the false claims in the vuln-triage README.

Validation: `make test`, `make verify`, diff review.

### Phase 2 — Permission logging

- Add the OpenCode plugin and the JSONL schema.
- Add the report script and `make permission-report`.
- Add the redaction and git-ignore rules.
- Test with real asks.
- Add the Claude Code logger if the hook proves reliable.

Validation: plugin test, report test, one real session.

### Phase 3 — Process tiers

- Add change classes, the triage step and the role activation matrix.
- Add optional Architect and Reviewer roles.
- Add the PR profile.
- Update `process.md`, `team/*.md`, `blueprints.md`, `setup.md`.

Validation: dry-run one class A, one class B and one class C issue; compare
time and prompts.

### Phase 4 — Docs architecture and templates

- Add the index, logs folder, archive and front matter.
- Add `make docs-check`.
- Add issue, PR, ADR, review and log templates.
- Add GitHub issue forms and PR template.
- Migrate the worst duplicate docs in VulnTriage as a pilot.

Validation: `make docs-check`, `make verify`, one issue created and one PR
opened from the templates.

### Phase 5 — Optional modules

- Cloud session module (wired and tested).
- Ponytail trial.
- GitHub Makefile helpers, if the pilot shows they remove prompts.

Validation: each module has its own install note, limits and test.

---

## 10. Risks and non-goals

### Risks

- **Permission logs can contain secrets.** Redact, git-ignore, cap size and
  delete at cleanup.
- **More roles can slow things down.** Add them only for class D, and measure.
- **Docs migration can break links and the kit's `_docs/specs.md` assumption.**
  Do it in stages; keep the spec path until a separate decision.
- **Optional modules can drift.** Each needs a `blueprints.md` row and a
  `setup.md` step, or it will rot.
- **Third-party skills are supply chain.** Pin and review before installing.

### Non-goals

- Rewriting VulnTriage's whole `_docs/` tree in this repo.
- Making Ponytail, cloud push or PR flow the default.
- Replacing QA with a reviewer or a skill.
- Adding a dependency to the core kit.
- Implementing an on-call responder.
- Adding AI usage reporting or logging to the kit; that is specific to the AI
  devtools course.

---

## 11. Decisions needed

1. **Scope:** Phase 1 only, Phases 1–3, or all five phases?
2. **Permission auditing:** adopt the hook-based OpenCode design and drop the
   agent-recorded approval lines? (Recommended.)
3. **Process:** adopt change classes and the optional Architect/Reviewer roles,
   or only the fast paths?
4. **Docs:** add the index + logs folder + docs-check first, or do the full
   reorganisation?
5. **Ponytail:** trial it in VulnTriage as an optional skill, or leave it out
   for now?
6. **Issue:** open a GitHub issue for the approved scope, or keep this as a
   human-directed plan?
