> Superseded: this review (2026-10-12) reviewed an empty plan (only the brief existed) and is superseded by the reviews in `_docs/reviews/`.

# Plan review — VulnTriage (2026-10-12)

Scope reviewed: `_docs/project-brief.md` (present) plus `product-spec.md`,
`_docs/architecture.md`, `openapi.yaml`, `_docs/testing.md`, `_docs/tasks.md`,
`_docs/plan-summary.md` (all missing at review time, searched from repo root).
Role: independent reviewer; no plan files were edited.

Verdict: **FAIL** (any failed check fails the plan).

## Checks (PASS/FAIL + one-line reason)

1. Brief workflow / MVP features / success criteria in spec and tasks — **FAIL**:
   `product-spec.md` and `_docs/tasks.md` do not exist, so coverage cannot be verified.
2. Nothing out of scope has crept in — **FAIL**:
   with no spec/tasks there is no artefact to check against the brief's out-of-scope list.
3. Every acceptance criterion checkable, covered by a test and a task — **FAIL**:
   no acceptance criteria, no `_docs/testing.md`, no tasks exist to trace.
4. Prioritisation formula deterministic with worked example — **FAIL**:
   no formula or worked example found; brief only states "deterministic, explainable score. No AI."
5. LLM version guardrail and prompt-injection handling specified — **FAIL**:
   brief mentions only the fix-version reject guardrail; no model pinning, injection handling, or tests specified.
6. Only backend touches database; MCP server and n8n use the API — **FAIL**:
   `_docs/architecture.md` missing, so DB-access boundaries cannot be verified.
7. MCP tools read-only, with separate read-only credential — **FAIL**:
   no MCP tool list, auth design, or credential separation documented.
8. OpenAPI covers every call from frontend, n8n and MCP server — **FAIL**:
   `openapi.yaml` missing, so endpoint coverage cannot be verified.
9. Backlog has no dependency cycles, task 1 is empty project with passing test,
   each task fits one session — **FAIL**: `_docs/tasks.md` missing, so no
   backlog, dependencies, or sizing to check.
10. All 14 rubric criteria map to tasks — **FAIL**:
    no rubric mapping or tasks exist; the rubric itself was not found in the reviewed files.
11. External API details that look invented/uncertain marked VERIFY: — **FAIL**:
    no spec to audit; OSV.dev / CISA KEV / FIRST EPSS integration details are absent,
    so unmarked uncertain details cannot be ruled out (list of unmarked items: none auditable — the docs are missing).
12. Assumptions and open questions collected in one place — **FAIL**:
    no assumptions/open-questions section found in any reviewed file.

## Five most important problems (priority order)

1. **Plan documents are missing.** Only `_docs/project-brief.md` exists;
   spec, architecture, OpenAPI, testing, tasks, and plan-summary are absent, so
   none of the 12 checks can pass.
   *Fix:* author the six missing documents through the planning process and
   re-submit for review; do not start application code until the plan passes.
2. **No deterministic prioritisation formula with worked example.**
   The brief requires it ("deterministic, explainable score. No AI") but gives
   no formula, inputs/weights, tie-breaks, or example.
   *Fix:* specify the exact formula, input sources, normalisation, tie-breaking,
   and one fully worked numeric example in the spec, with tests in `_docs/testing.md`.
3. **LLM brief guardrail and prompt-injection handling underspecified.**
   Only the fix-version-mismatch reject is stated; model version pinning,
   advisory-text-as-untrusted-data handling, failure modes, and "no wrong fix
   version reaches owner" tests are missing.
   *Fix:* specify pinned model/version, prompt boundaries, output validation
   (fix-version equality check), logging/quarantine of rejected briefs, and
   negative tests including injection cases.
4. **No API / data-access / auth contract.**
   Backend-only DB access, n8n-via-API, MCP read-only tools with separate
   read-only token, dashboard status transitions, and audit trail are asserted
   in the brief but have no architecture or OpenAPI backing.
   *Fix:* add `_docs/architecture.md` (DB ownership, service boundaries, auth)
   and `openapi.yaml` covering every frontend, n8n, and MCP call; verify
   read-only MCP scope with tests.
5. **No task breakdown with test/rubric traceability.**
   There is no backlog, so dependency cycles, task-1 scaffold-with-passing-test,
   one-session sizing, acceptance-criteria coverage, 14-rubric-criteria mapping,
   VERIFY: marking, and assumptions log cannot be checked.
   *Fix:* write `_docs/tasks.md` starting with an empty-project-plus-passing-test
   task 1, acyclic dependencies, per-task tests and acceptance criteria, a
   rubric-to-task map, VERIFY: tags on OSV/KEV/EPSS details, and a single
   assumptions/open-questions section; summarise in `_docs/plan-summary.md`.
