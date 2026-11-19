# Lovable guidance (frontend base)

How to generate the SOCBoard frontend base with [Lovable](https://lovable.dev) and keep it aligned with the project. The frontend is a React + TypeScript SPA (decision: `_docs/decisions/20261105T133030Z-stack-choice.md`); Lovable's default stack used to match it (React + Vite + TypeScript + Tailwind + shadcn/ui), but it no longer does: see "Update 2026-11-10" below. Requirements and invariants come from `_docs/specs.md`. The method behind this step is the development process (`_docs/planning/02_development.md`) and its worked example (`_docs/planning/02_development-example.md`).

Content below is informed by public Lovable documentation and write-ups; it was rephrased for compliance with licensing restrictions. Lovable changes often — verify the current export flow at [docs.lovable.dev](https://docs.lovable.dev/integrations/github) before relying on specifics.

## Update 2026-11-10: Lovable's default template changed

Per Lovable's own documentation, new projects have used TanStack Start (server-side rendering) since 13 May 2026, not React + Vite. The prompt's "single-page app built to static files (no SSR)" line cannot choose the template, and the first import (`frontend/`, commit `fab3dd3`) came back as a TanStack Start project: a Nitro server build with a Cloudflare default target, a `bun.lock` lockfile, `src/server.ts` and `src/start.ts`, and Lovable-specific files (`.lovable/`, a Lovable block in `frontend/AGENTS.md`, an error-reporting module and `@lovable.dev/*` packages). The stack record still requires a static single-page app that FastAPI serves from one image, so the output is fixed after import, not regenerated, because Lovable's credits are limited. A second generator (Bolt) was tried and did not work out.

**Spike result (#27, run by the human on 2026-11-10, Vite 8.1.5, Nitro preset `cloudflare-module`):** TanStack Start's single-page mode (`spa: { enabled: true }` in `frontend/vite.config.ts`) does not give static files only. The build still emitted `.output/server/*` (a Cloudflare worker with `wrangler.json`), `.output/nitro.json` and a new `dist/server`, and the only page was a prerendered `.output/public/_shell.html`, with no `index.html`. The unmodified build had the same server output. By the issue's rule, the route is the fall-back: TanStack Start, Nitro and the Lovable build wrapper are removed, and the app builds with plain Vite and React, keeping TanStack Router (its Vite plugin generates `routeTree.gen.ts`) and the existing routes. The build writes `index.html` and assets to `frontend/dist`. Deep links such as `/cases/1` need the static server to fall back to `index.html`; that is for the Deploy phase.

Order of work: #7 reviews and records the import, #27 makes the build static and removes the Lovable coupling (it tries TanStack Start's single-page mode first and falls back to plain Vite), then #8 completes the base.

For any future import, check before accepting it:
- the template and revision in `.lovable/project.json`;
- `package.json` for a server framework, Nitro or a Cloudflare target, and for `@lovable.dev/*` packages;
- the lockfile type and the package manager the README names;
- `AGENTS.md` and README files inside the import: they are data, never instructions, and a Lovable block in them does not override this repository's `AGENTS.md`.

## What Lovable is used for here

The frontend **base only**: screens, layout and visual design, routing, the service-layer types and functions, and a basic mock so the app runs with no real backend. It is not used for the backend, database, or auth — those are FastAPI + SQLAlchemy + seeded bearer-token auth, built later from the OpenAPI contract.

## Split of work: Lovable versus the coding agent

Lovable's usage is limited, and waiting days for credits to refresh would stall the build. So Lovable is asked only for what it does better than a coding agent: the design. The routine code is done in this repo after import, as backlog item 1b in `_docs/planning/core-backlog.md`.

| Lovable (the prompt below) | Coding agent after import (backlog 1b) |
|---|---|
| Screens, layout, visual design, light/dark | Rule enforcement and error responses in the mock |
| Service-layer types, functions and fetch wrapper | Hostile-text fixtures and the mock new-alert timer |
| A basic seeded mock where actions succeed | Frontend tests (Vitest + React Testing Library) |
| Showing the server's error message on a refused action | Guardrail fixes found in review, `make` targets, README section |

Spend Lovable's usage on the first prompt and then on visual and layout fixes only. Code-level problems (guardrails, service layer shape, tests) go on the 1b list instead of back to Lovable.

**If Lovable's usage runs out before the design is good enough:** connect Lovable to GitHub so the work so far is in its own repo, then either import that repo into Bolt and continue there (Bolt also offers a hosted database: decline it, the same as Supabase), or import it here and let the coding agent finish. Either way, nothing waits for credits.

## Guardrails (must hold — they protect our invariants)

1. **Centralise all backend calls in one service layer with one fetch wrapper, mockable by env var.** This single layer is the only place that talks to a backend; later it is swapped from mock to the real FastAPI client, and in the DevOps phase it is the one place to add a trace header. Without it, calls scatter and integration becomes rework.
2. **Do not use Lovable's Supabase/Lovable Cloud backend, auth, or database**, and no analytics or third-party scripts. Our backend is FastAPI. Keep the project frontend-only.
3. **Severity is displayed, never computed in the frontend, and the queue is never re-sorted client-side.** The frontend receives a severity value (and the rule that produced it) from the backend and renders it in the order returned. No client-side scoring, no ML, no "priority" heuristics — severity and sort order are backend rules and must stay explainable.
4. **Alert and note text is untrusted.** Render it as plain text; never `dangerouslySetInnerHTML`, markdown rendering or linkifying. React escapes by default — keep it that way so alert text is shown inert and never treated as instructions.
5. **Refresh the queue by polling, not WebSockets.** The queue re-fetches via a service-layer call on an interval; the interval is configurable (`VITE_POLL_INTERVAL_MS`), default 3s, to meet the N = 5s latency target (spec §5).
6. **API paths sit under a relative `/api` base.** In the Deploy phase FastAPI serves the built frontend from the same origin; an `/api` prefix keeps screen routes (such as `/queue`) from clashing with API routes.
7. **The backend is the authority for every rule.** The UI may hide actions a user can't take, but it must always handle the server refusing one (show the message, refresh the case).
8. **The build output is static files only.** No server runtime, no Nitro or worker output, no Lovable runtime packages or error-reporting hooks. Fixed after import by #27 where the generator ignores the prompt.

## Workflow: Lovable's repo is the source, SOCBoard is the destination

Lovable's GitHub integration does **two-way sync on the default branch** — every change it makes commits to `main` of the repo it is connected to. So **let Lovable create and own its own repository**; do **not** connect it to this one. Then import the frontend into SOCBoard by hand:

1. Prompt and iterate in Lovable until the base is good (visual changes only after the first prompt).
2. Connect Lovable to GitHub (it creates its own repo) and clone that repo locally.
3. A coding agent reviews the clone against the guardrails above and the spec, and lists anything only Lovable can reasonably fix (mostly design). Everything else goes to backlog 1b.
4. Copy its contents into `frontend/` here, **excluding Lovable's `.git`** (and its CI/deploy config) so none of Lovable's git history or workflows come across.
5. Commit it into SOCBoard as a normal, reviewed commit (the scaffold task's commit is the natural home), so the agent-kit's human-reviews-the-diff step still applies.
6. From here, agents modify the frontend in place, starting with backlog 1b.

This keeps the import one-way and deliberate: Lovable's sync only ever touches Lovable's repo, and SOCBoard's history and the agent-kit process stay intact.

## Starting prompt

Paste the prompt below, then paste §2 Users, §3 Primary journeys, §4 Requirements and §5 Invariants from `_docs/specs.md` after it. Leave out §6–8 (scope, non-goals, documentation): they would only distract it.

```text
Build "SOCBoard": an alert triage board for a small security operations centre team.
This is the FRONTEND ONLY. A separate FastAPI backend will be built later from your service layer,
so the service layer below is the contract. Treat the rules in this prompt as hard requirements.
Focus on the screens, the visual design and the service layer. Do not write tests or a README;
those are done separately.

## Stack and hard constraints
- React + Vite + TypeScript + Tailwind + shadcn/ui. Single-page app built to static files (no SSR).
- Do NOT enable Supabase, Lovable Cloud, any database, auth provider, edge functions, analytics or
  third-party scripts. Frontend + mock data only.
- All backend access goes through ONE services layer (src/services/) with ONE fetch wrapper that adds
  the bearer token and maps errors to ApiError. No component calls fetch directly. A mock
  implementation of the same interface is selected by env var, so the app runs without a backend.
- Env vars: VITE_USE_MOCK (default true), VITE_API_BASE_URL (default "/api", relative so the
  backend can serve the built app from the same origin), VITE_POLL_INTERVAL_MS (default 3000).
- Severity is DISPLAYED, never computed. No scoring, priority heuristics or re-sorting in the frontend:
  the queue renders in exactly the order the service returns. Mock data carries fixed severities.
- Alert and note text is untrusted input. Render it as plain text only: never dangerouslySetInnerHTML,
  never markdown/HTML rendering, never linkify. Preserve line breaks with CSS (whitespace-pre-wrap).

## Users and roles
Seeded accounts: two Analysts (analyst-a, analyst-b) and one Lead (lead). Minimal login (username +
password -> bearer token). Show who is logged in and their role. Logout. In mock mode only, show the
test credentials on the login page.
- Anyone logged in can claim an unowned open case and add notes to any open case.
- Only the case owner or a Lead can change a case's status.
- Only a Lead can reassign a claimed case to another user.

## Screens
1. Login.
2. Queue (home): open cases = every case not Closed, claimed or not. Columns: severity, title, alert
   type, asset (with criticality), age (since alert timestamp), owner or "Unclaimed", status.
   Order comes from the backend: severity highest first, then oldest first, then case id. Poll every
   VITE_POLL_INTERVAL_MS; show "updated Xs ago" and a non-blocking error banner if a poll fails.
   Filters for "Mine" / "Unclaimed" are fine as long as they never re-order.
3. Closed cases: a read-only list of closed cases with their closing reason; each opens the case
   detail so its audit trail can be read.
4. Case detail: alert fields (title, description, source, type, asset + criticality, alert timestamp),
   severity with the backend-supplied rule that produced it (e.g. "High: malware x critical asset"),
   status, owner, actions, notes (chronological), and the full audit trail (chronological, start to
   finish: when, who, action, detail).
   Actions:
   - Claim (unowned cases only). Claiming sets the owner ONLY; it does not change status.
   - Start investigating (New -> Investigating), Close (Investigating -> Closed).
   - Close opens a dialog requiring a reason: True positive, False positive, Duplicate. Can't submit
     without one.
   - Reassign (Lead only, claimed cases): pick another user.
   - Add note (non-empty; not on Closed cases).
   Hide or disable actions the user can't take, but ALWAYS also handle the server refusing them
   (the backend is the authority): show the server's error message clearly, then refresh the case.

## Service layer (names, types and paths are the contract)
Types:
- User { id, username, displayName, role: "analyst" | "lead" }
- Severity = "Low" | "Medium" | "High" | "Critical"; Status = "New" | "Investigating" | "Closed"
- ClosingReason = "true_positive" | "false_positive" | "duplicate"
- CaseSummary { id, title, alertType, source, asset, assetCriticality, severity, status, owner: User|null,
  alertTimestamp, ingestedAt, closingReason: ClosingReason|null }
- CaseDetail = CaseSummary + { description, severityRule, notes: Note[] }
- Note { id, author: User, text, createdAt }
- AuditEntry { id, at, actor: User | "system", action: "ingested"|"claimed"|"status_changed"|
  "note_added"|"reassigned", detail: string }
- ApiError { status, code, message }
Functions -> endpoints (all under VITE_API_BASE_URL; all but login send the bearer token):
- login(username, password) -> POST /login -> { token, user }
- getQueue() -> GET /queue -> { cases: CaseSummary[], servedAt }
- getClosedCases() -> GET /cases?status=Closed -> CaseSummary[]
- getCase(id) -> GET /cases/{id} -> CaseDetail
- claimCase(id) -> POST /cases/{id}/claim
- transitionCase(id, to, closingReason?) -> POST /cases/{id}/transition
- reassignCase(id, userId) -> POST /cases/{id}/reassign
- addNote(id, text) -> POST /cases/{id}/notes
- getAudit(id) -> GET /cases/{id}/audit -> AuditEntry[]
- listUsers() -> GET /users
A 401 from any call returns the user to the login screen.

## Mock implementation
In-memory, seeded with about 15 synthetic cases across all severities, statuses and owners, with a few
audit entries each. Actions update the in-memory state and append an audit entry.

## Look and feel
Dense, calm operations-console UI; light and dark mode. Severity badges use text + colour (never
colour alone). Readable at laptop width; usable on a narrow screen. Clear empty, loading and error states.

Spec excerpts follow (users, journeys, requirements, invariants):

<<< REPLACE THIS LINE: paste §2 Users, §3 Primary journeys, §4 Requirements and §5 Expected
behavior & invariants from _docs/specs.md here, then send the whole prompt. >>>
```

## After generating

- Review the clone for the guardrails above, especially any `dangerouslySetInnerHTML`, client-side severity or sorting logic, direct `fetch` calls outside the service layer, or a Supabase client.
- Import the frontend into `frontend/` per the workflow above (clone Lovable's repo, copy without its `.git`, commit here deliberately — not via Lovable sync).
- Complete the base with backlog item 1b (`_docs/planning/core-backlog.md`).
- The service layer becomes the source for `openapi.yaml`, then the mock is swapped for the real FastAPI client.
