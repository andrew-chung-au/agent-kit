# Example: Build and Ship a Full-Stack App with AI Coding Assistants

> **Process document:** [`02_development.md`](./02_development.md) — *Build a Full-Stack App with AI Assistance*
>
> This is a worked example of that process. It records the concrete steps taken to build the **Interview Canvas** application (a system-design interview tool) and the reasoning behind each one. Source: Part 2 of the AI Dev Tools Zoomcamp series by Alexey Grigorev.

## What we built

A system-design interview application:
- An interviewer creates a session and shares a link with a candidate.
- The candidate places components on a canvas; the interviewer sees changes in real time.
- Both frontends connect to the same room over WebSockets; a FastAPI backend handles the events and persists them to SQLite.

## The steps (what happened and why)

### 1. Start with a specification
- **What:** Described the application precisely before building — who creates a session, how a candidate joins, which components can be placed, how both people see changes in real time. Used ChatGPT in dictation mode to capture as much detail as possible.
- **Why:** Without a precise spec you get something that works but isn't what you need. The spec is the thing you validate everything else against.

### 2. Build the frontend first (with a mocked backend)
- **What:** Generated a React/TypeScript app from the spec using Lovable. Prompt required: *centralize every backend call in one services layer, and create a mock implementation so the whole app runs without a real backend.* Added tests, then saved the project to GitHub.
- **Why:** For a solo project, the frontend lets you quickly judge whether you're moving in the right direction and whether the idea solves your problem. Mandating a single mocked service layer makes it the future integration point and keeps the app runnable from day one.

### 3. Move the frontend into the project structure
- **What:** Cloned the repo locally and arranged it as `/backend`, `/docs`, `/frontend`, `AGENTS.md`, `openapi.yaml`. Moved the frontend into `frontend/` and the spec into `/docs/spec.md`, then committed. Verified it runs locally (`cd frontend && npm i && npm run dev`).
- **Why:** Establishes the layout the rest of the project depends on, and confirms the exported app actually runs before building further.

### 4. Create `AGENTS.md`
- **What:** Added an `AGENTS.md` at the repo root documenting tool-specific commands — e.g. using `uv` for backend dependency management (`uv sync`, `uv add <pkg>`, `uv run python <file>`) and a reminder to commit regularly.
- **Why:** Agents may not know how to use newer tools like `uv`; documenting the commands explicitly gives them reliable baseline instructions. It's a starting point that grows with the project.

### 5. Define the OpenAPI contract
- **What:** Read the frontend's API client in `frontend/` and generated `openapi.yaml` at the repo root, specifying every endpoint, method, path, request/response body, and which endpoints need authentication.
- **Why:** Gives the backend a precise target instead of inferring requirements from frontend code — saves tokens and produces a clear picture of exactly what the backend needs.

### 6. Implement the backend with a mocked store
- **What:** Asked the assistant to build a FastAPI backend implementing `openapi.yaml`, using an in-memory store seeded with data, with hashed-password + bearer-token auth on the endpoints that need it, split into modules (routers, models, store, auth), plus tests.
- **Why:** Mirrors the mock-first idea from the frontend: get the frontend-backend connection working smoothly before worrying about persistence.

### 7. Add a Makefile
- **What:** Asked the assistant to create a `Makefile` wrapping the verbose run command (`uv run uvicorn backend.main:app --reload --port 8091`) so the app starts with `make run`. Opened `/docs` to compare the FastAPI-generated spec against `openapi.yaml`.
- **Why:** The long startup commands are hard to remember; a Makefile simplifies them. After this, the FastAPI-generated spec supersedes the hand-written `openapi.yaml`.

### 8. Connect frontend and backend
- **What:** Switched the frontend to use the real backend client. Fixed the errors that showed up (CORS and others), then tested with two browser windows — create a session in one, join via the link in the other, and confirm changes propagate.
- **Why:** This is where the real integration happens; manual two-window testing verifies the real-time data flow end to end.

### 9. Add database persistence
- **What:** Replaced the in-memory store with SQLite via SQLAlchemy, configured the database connection through an environment variable, and kept it database-agnostic (no SQLite-specific features). Re-ran the two-window test and restarted the backend to confirm data survives.
- **Why:** Without a real database, restarting the backend loses all data. SQLite is lightweight for local use; SQLAlchemy + env-var config makes swapping to Postgres later easy, which is why SQLite-specific features are avoided now.

## Result

A working local, end-to-end application: idea → specification → frontend → API contract → backend from the contract → connected stack → SQLite persistence. Ready for deployment, which is covered by the next example.

## The step-by-step approach (the key takeaway)

Each step produced something concrete and testable before moving on:
1. Clear specification
2. Working frontend prototype with a mock backend
3. Integrated backend with a mock (in-memory) store
4. Persistence with SQLite

Each step started from a fresh agent session and drove the agent to a working version, one prompt at a time. Once the first version works, you introduce the development *process* (see the process documents) so the app keeps working as it grows.
