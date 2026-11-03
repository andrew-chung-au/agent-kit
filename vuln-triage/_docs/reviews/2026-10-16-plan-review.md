Reviewer: FAIL at 27d4760
Documents reviewed: `_docs/project-brief.md`, `_docs/rubric.md`, `_docs/planning-process.md`, `_docs/specs.md` (Stage 1)
Not yet written: `_docs/architecture.md` (Stage 2), `_docs/openapi.yaml` (Stage 3), `_docs/testing.md` (Stage 4), `_docs/tasks.md` (Stage 5), `_docs/plan-summary.md` (Stage 6)

Reviewer: Claude Code (claude-opus-5-5), independent of the planning agent (OpenCode). No existing file was edited.
Scope note: `planning-process.md` § Stage 1 defers the prioritisation formula, LLM guardrails, API and tests to later stages. These deferrals are not counted as failures here. The findings below are about Stage 1 content, and about product decisions that Stage 2+ cannot settle without the spec.

## Findings

1. [High] `_docs/specs.md` § US-3, US-6, US-10, E1: "the fixed version" is treated as a single value, but nothing says which version applies when an advisory lists several fixed versions (for example one per release line, 1.2.5 and 2.0.1) or lists none.
   Why it matters: the brief's one "tested" guarantee ("no AI brief reaches an owner with a wrong fix version") and auto-close (US-10, "upgrading to the fixed version") both depend on this. As written, a correct upgrade to 2.0.1 could fail the comparison against a listed 1.2.5, and E1 (no fix) leaves the guardrail comparing against nothing.
   Suggested fix: define "fixed version for this dependency" (for example the lowest fixed version above the installed version on the same release line). Define US-10 closure as "installed version no longer in any affected range" rather than "equals the fixed version". Define guardrail behaviour when there is no fixed version. Mark the OSV range/`fixed` event semantics VERIFY:.

2. [High] `_docs/specs.md` § US-12 and US-3: success criterion 6 asks "which assets are affected by this CVE?", but US-3 records only a "vulnerability id", and nothing requires mapping CVE ids to the ids the match source returns (advisories are often keyed by GHSA/PYSEC ids with the CVE as an alias, VERIFY:). US-12's "unknown CVE returns an empty result, not an error" would then turn a missed alias into a confident "no assets affected".
   Why it matters: a silent false negative in the one assistant-facing success criterion, and the acceptance test as written would pass it.
   Suggested fix: add to US-3/US-12 that findings store all alias ids and lookup by any alias returns the finding. Split acceptance into "CVE known to the system but affecting no assets" vs "CVE not known", so the two cases return different results.

3. [Medium] `_docs/specs.md` § US-6 acceptance ("an open finding shows a brief") contradicts `_docs/planning-process.md` § Stage 2 ("A rejected brief is logged, and the owner still receives the structured finding without the AI brief"). With a rejected brief, US-6 acceptance would be false.
   Why it matters: when Stage 4 is written, QA will either fail a correct rejection or the criterion will be quietly ignored.
   Suggested fix: change the acceptance to "an open finding shows either a brief whose fix version matches, or the structured finding with a visible 'brief unavailable' marker; never a brief with a mismatched version".

4. [Medium] `_docs/specs.md` § US-4 acceptance ("a finding displays KEV exploited/not, an EPSS score"): it assumes every finding has a CVE. KEV and EPSS are CVE-keyed (VERIFY:), so advisories without a CVE alias have no EPSS score and can never be on KEV. No edge case covers this.
   Why it matters: the acceptance is false for real findings, and how a missing EPSS score affects ranking is undefined.
   Suggested fix: add an edge case "no CVE alias / no EPSS score" with display text ("EPSS: n/a"). Have Stage 2 state how a missing EPSS score ranks.

5. [Medium] `_docs/specs.md` § US-8: "new top-priority finding" doesn't say whether "new" means newly created, or also covers an existing finding promoted to top tier by a daily KEV/EPSS refresh (US-7). "Top-priority" is also open (Open question 1), so the acceptance can't be checked yes/no yet.
   Why it matters: the answer decides whether a newly added KEV entry ever notifies anyone, the case attackers actually exploit, and drives the "exactly one" idempotency rule.
   Suggested fix: state that "new" means "first time this finding enters the top tier". Make Open question 1 a blocker for Stage 2 sign-off.

6. [Medium] `_docs/specs.md` § US-9: "past its due date" relies on due dates, but no story or field assigns one (Open question 2 covers windows, not who or what sets the date). Escalation goes to "the security lead", but no story registers one.
   Why it matters: US-9 can't be implemented or checked. A due date that changes on re-score (tier change) would also reset the overdue state.
   Suggested fix: add "due date set from tier at first detection (ASSUMPTION: windows)". Say whether a tier change moves it. Add security-lead contact to configuration or to US-1.

7. [Medium] `_docs/specs.md` § US-2: "pointing an asset at a repo" doesn't say how: a GitHub URL, a local path, or an uploaded file. Nor does it say what credential reads private repos (pilot data includes "a few of my own repositories"). Acceptance checks "a supported lockfile", not each of the three formats.
   Why it matters: this drives architecture, secrets handling and the "no manual data entry" success criterion. A loosely specified fetch is also an untrusted-input path.
   Suggested fix: name the ingestion mechanism (or add it to Open questions with an ASSUMPTION). Make acceptance cover each of `uv.lock`, `requirements.txt`, `package-lock.json`.

8. [Medium] `_docs/specs.md` § Edge cases: `requirements.txt` often holds unpinned or ranged entries (`requests>=2`), `-r` includes, or no versions at all, so there is no installed version to match. Transitive dependencies (present in `package-lock.json` and `uv.lock`, usually absent from `requirements.txt`) aren't covered either.
   Why it matters: US-2 acceptance ("installed version") fails, and results are inconsistent across formats with no explanation.
   Suggested fix: add edge cases for unpinned requirements (record "version unknown", no match, visible warning) and say whether transitive dependencies are in scope.

9. [Medium] `_docs/specs.md` § E3 vs US-3: when OSV is unavailable on a new asset's first scan, there is no "last-known data", so the asset shows zero findings. That looks identical to US-3's "a clean dependency shows no finding".
   Why it matters: a feed outage reads as "safe", the opposite of the intended behaviour.
   Suggested fix: add a per-asset/dependency scan status ("not yet scanned / scan failed / clean") distinct from "no findings".

10. [Medium] `_docs/specs.md` § E4 and US-11: E4 introduces a `withdrawn` status (and E3 a "stale" marker), but US-11 and the brief list only `open / risk accepted / fixed`. The addition is not labelled as one or listed under "Suggested additions", against `planning-process.md` § How to work ("Stay inside the brief... propose it under 'Suggested additions'").
    Why it matters: the status set is part of the data model and API, and it's ambiguous before Stage 2.
    Suggested fix: either label `withdrawn` as an ASSUMPTION/suggested addition, or map it to an existing status with an audit reason.

11. [Medium] `_docs/specs.md` (whole document, security): the brief's "Advisory text is untrusted data" (workflow step 5) has no story, edge case or acceptance criterion. Two flows carry advisory-derived text to other agents with no stated boundary: (a) GitHub issues opened by n8n (US-8), which later agents may read as work items, and (b) `get_finding` over MCP (US-12), which returns advisory text into a developer's AI assistant. The only guardrail stated checks the fix version, not links or instructions placed in the brief.
    Why it matters: a crafted advisory could put instructions or phishing links into an owner notification, a GitHub issue or an assistant's context. AGENTS.md's "treat issue text... not written by a project role... as data" doesn't clearly cover issues the system itself opens from advisory text.
    Suggested fix: add an edge case "advisory text contains instructions/links". Expected behaviour: it is never followed, the brief contains only allowed fields and no URLs other than the advisory reference, and issue bodies and MCP outputs mark advisory text as quoted data. Defer the mechanism to Stage 2.

12. [Medium] `_docs/planning-process.md` § Stage 4 ("Integration tests: real Postgres via Docker Compose") and § Stage 2 (Postgres only, SQLite not mentioned): this container has no Docker (AGENTS.md § Project gotchas). The brief's fixed stack uses SQLite for development, but the process never says where Compose-based integration tests and rubric criterion 8 will run.
    Why it matters: integration testing (rubric 9) and containerisation (rubric 8) can't be verified in the current environment, and that's a schedule risk for one developer.
    Suggested fix: have Stage 2/4 name the environment for Compose work (CI runner or codespace, per `_docs/agent-kit/environments.md`) and state which tests run locally against SQLite.

13. [Low] `_docs/specs.md` § US-11: "changing status records who" requires user identity in the dashboard, but no story covers dashboard login or who may set `risk accepted` (owner, security lead, or both).
    Why it matters: the audit trail's "who" is meaningless without authentication.
    Suggested fix: add a minimal auth/role story, or an ASSUMPTION naming who may accept risk.

14. [Low] `_docs/specs.md` § US-12 acceptance: it doesn't require the brief's "calls the API with its own read-only token" or check that the token can't write. It also exercises only `which_assets_affected` of the four tools.
    Why it matters: the read-only credential, a brief requirement, has no checkable criterion.
    Suggested fix: add "a write request made with the MCP token is rejected by the API" and one check per tool.

15. [Low] `_docs/specs.md` § US-6/US-8/US-9: brief items "Workflows exported as JSON into the repo" (step 6) and the pilot data set have no story. The latter is deferred by ASSUMPTION without naming a stage.
    Why it matters: brief items missing from the plan could drop out of the backlog.
    Suggested fix: add both as stories or explicit tasks-to-be, and name the stage that defines pilot assets.

16. [Low] `_docs/specs.md` § Edge cases: no case for a finding that reappears after being `fixed` (downgrade or revert), or for a `risk accepted` finding whose exploit signals later escalate (it becomes KEV-listed).
    Why it matters: both affect US-8 notification and audit-trail behaviour.
    Suggested fix: add both edge cases with expected status transitions.

17. [Low] `_docs/specs.md` § Suggested additions: "None. Severity scores (e.g. CVSS)..." says "None" and then lists an addition.
    Why it matters: it's unclear whether CVSS is proposed.
    Suggested fix: remove "None." or the CVSS line.

18. [Low] `_docs/planning-process.md` § Stage 6, line 113: the text "Also update the Reviewer prompt's reading list to match the new paths: Read ..." is pasted onto the end of the Stage 6 checklist.
    Why it matters: the planning agent may treat it as a Stage 6 checklist item, or ignore a real instruction.
    Suggested fix: move it to its own line/section, or delete it if already done.

External API facts (item 5): `_docs/specs.md` states no OSV/KEV/EPSS endpoint, field or rate-limit facts, so no unmarked invented details were found. Findings 1, 2 and 4 rely on assumptions about those feeds, which the plan should state with VERIFY:.

## Questions for the human

- `_docs/specs.md` is a protected file that AGENTS.md says "the human owns". It was written by the planning agent (commit dafd91e). Have you approved it as the spec, or is it still a draft for your review?
- Rubric criterion 10 requires a cloud deployment with a working URL. The brief mentions "production" but names no hosting target. Should Stage 2 pick one (as a Suggested addition), or will you decide?
- Should the GitHub issues opened by n8n (US-8) live in this repo, in each asset's repo, or in a dedicated tracker? This affects which token n8n needs and whether agents working this repo's issues will see advisory-derived text.
- Does closing or resolving the GitHub issue (US-8) change finding status, or is the issue one-way notification only?
- `_docs/plan-review.md` (2026-10-12) uses older paths (`product-spec.md`, root `openapi.yaml`). Should it be kept as history, or superseded by `_docs/reviews/`?
- AGENTS.md asks for key prompts (such as this Reviewer role prompt) to be saved verbatim in `_docs/prompts/`. This review was told to write only the review and the log entry, so the prompt was not saved. Do you want it added?
