# Process: Build a Full-Stack App with AI Assistance

> **Worked example:** [`02_development-example.md`](./02_development-example.md)
>
> Follows the planning process in [`01_planning.md`](./01_planning.md).

This document describes the process for building a full-stack application with AI coding assistants: what to do, when to do it, and why. The end state is a locally running application with a frontend, a backend, an OpenAPI contract, and data persisted in SQLite.

## Philosophy

- **Controlled AI workflow.** AI accelerates development, but you verify every step rather than letting a tool build everything unchecked.
- **Incremental verification.** Each step must produce a concrete, testable component before you move to the next layer of the stack.
- **Mock-first isolation.** Mocking backend calls during the frontend phase, and using an in-memory store during the early backend phase, isolates errors so interactions can be verified one layer at a time.
- **Contract-driven development.** An explicit OpenAPI contract gives the backend a precise target instead of forcing it to infer requirements from frontend code.

## The pipeline (what, when, why)

### 1. Product specification
- **What:** Write a small product spec — user stories, acceptance criteria, non-goals — before generating any code.
- **When:** First, before any other work.
- **Why:** A precise spec is the reference everything else is validated against; without it you get something that works but isn't what you need.

### 2. Frontend prototype (mocked)
- **What:** Generate a frontend prototype. Require the AI to centralize every backend call into one service layer and create a mock implementation so the app runs without a real backend. Add tests.
- **When:** After the spec exists, before any backend work.
- **Why:** For simple solo projects, a working frontend quickly validates whether the idea solves the problem. The single mocked service layer becomes the later integration point and keeps the app runnable from the start.

### 3. Project structure
- **What:** Arrange the repository into `/frontend`, `/backend`, `/docs`, plus `AGENTS.md` and `openapi.yaml` at the root. Move the prototype into `frontend/` and the spec into `docs/`, then verify the app still runs locally.
- **When:** Immediately after exporting the frontend prototype.
- **Why:** Establishes the layout the rest of the project depends on, and confirms the exported app actually runs before building further.

### 4. Agent context (`AGENTS.md`)
- **What:** Document tool-specific commands agents need — e.g. `uv` for Python dependency management (`uv sync`, `uv add <pkg>`, `uv run`) — and conventions such as committing regularly.
- **When:** Early, as soon as the project structure exists; update it as the project grows.
- **Why:** Agents may not know how to use newer tools correctly; explicit commands give them reliable baseline instructions.

### 5. OpenAPI contract
- **What:** Read the frontend's API client and generate `openapi.yaml` defining every endpoint, method, path, request/response body, and which endpoints require authentication.
- **When:** After the frontend's service layer exists, before implementing the backend.
- **Why:** Gives the backend an explicit target rather than inferred requirements — saves tokens and produces a clear picture of exactly what the backend must provide.

### 6. Backend implementation (mocked store)
- **What:** Build a backend (e.g. FastAPI) that implements the OpenAPI spec, starting with an in-memory store seeded with data. Split code into modules (routers, models, store, auth) and add tests.
- **When:** After the contract is defined.
- **Why:** Starting with an in-memory store lets you confirm the frontend-backend connection works smoothly before dealing with persistence.

### 7. Run command simplification (Makefile)
- **What:** Wrap verbose startup commands in a `Makefile` so the app starts with a simple command like `make run`.
- **When:** Once the backend is runnable.
- **Why:** Long startup commands are error-prone and hard to remember; a Makefile makes running the app trivial for both humans and agents.

### 8. Connect the stack
- **What:** Switch the frontend from the mock service to the real backend client. Fix integration issues (CORS and others) and test manually across multiple browser windows.
- **When:** After the backend runs against its in-memory store.
- **Why:** This is where real integration happens; manual multi-window testing verifies data actually flows end to end.

### 9. Database persistence
- **What:** Replace the in-memory store with a real database (SQLite via SQLAlchemy). Configure the connection via an environment variable and keep it database-agnostic (no database-specific features).
- **When:** Last, once the connected stack works.
- **Why:** Without a database, a backend restart loses all data. SQLite is lightweight for local use; an ORM plus env-var config makes a later switch to Postgres simple, which is why database-specific features are avoided now.

## Deliverables

- `product-spec.md` — project scope and acceptance criteria.
- `AGENTS.md` — baseline instructions for coding agents.
- `frontend/` and `backend/` — the application code.
- `openapi.yaml` — the API contract and source of truth between frontend and backend.
- `tests/` — unit and frontend tests covering behaviors from the spec and the contract.

## Recommended tooling

- **Frontend generation:** Lovable, v0, Bolt, Claude Design, or Replit for generating a React app from a prompt (they tend to make sensible UI choices automatically). A coding assistant can also scaffold the frontend directly.
- **Backend stack:** Python + FastAPI with `uv` for dependency management; SQLAlchemy + SQLite for lightweight local persistence.
