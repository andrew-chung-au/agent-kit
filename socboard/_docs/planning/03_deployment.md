# Process: Deploy a Full-Stack App with AI Assistance

> **Worked example:** [`03_deployment-example.md`](./03_deployment-example.md)
>
> Continues from [`02_development.md`](./02_development.md).

This document describes the process for taking a locally working full-stack application and making it a reliable, reproducible, internet-accessible deployment: what to do, when to do it, and why. The starting point is the locally running app produced by the development process (frontend, backend, OpenAPI contract, SQLite persistence).

## Philosophy

- **Container-centric development.** Package and isolate the runtime so it behaves the same everywhere, preventing drift between development and production.
- **Immutable, repeatable deployments.** Deployments should be reproducible and revertible; avoid ad-hoc changes in production.
- **One source of truth for the stack.** A single Compose/manifest file describes the services, environment variables, and configuration.
- **Automate the checks.** Builds, tests, and deployments run automatically so delivery is fast and manual toil is minimized.
- **Test the new failure points.** Each change (containerization, database swap) adds something that can break; add tests that cover it.

## The pipeline (what, when, why)

### 1. Containerize the application
- **What:** Build the frontend into static files and produce a single container image where the backend serves those static files (a multi-stage build: compile the frontend, then copy only the built files into the backend image). Verify by running the container and testing the full user flow.
- **When:** First, once the app works locally.
- **Why:** In development the frontend runs separately for hot-reload; in production it's static after one build, so the backend can serve it. This means one container, not two — simpler to build, ship, and run.

### 2. Switch to a production database
- **What:** Move from SQLite to Postgres. With an ORM already in place, add Postgres support and point the backend at it via an environment variable. Re-run the full user flow against Postgres.
- **When:** After containerization, before orchestrating the full stack.
- **Why:** SQLite is convenient locally, but production typically needs Postgres. Building on an ORM earlier is what makes this switch simple and rewrite-free.

### 3. Orchestrate locally with Docker Compose
- **What:** Define a Compose file with the app and database services, including a health check so the app waits until the database accepts connections. Run the whole stack with a single `docker compose up`.
- **When:** Once the app runs against the production database.
- **Why:** Replaces separate manual commands with one source of truth that starts the entire application consistently.

### 4. Integration and end-to-end tests
- **What:** Add integration tests that run against the Compose stack, covering the newly introduced failure points (the frontend compiles, the backend reaches the database). Add an end-to-end test (e.g. Playwright) that automates the full multi-user flow.
- **When:** After the stack runs under Compose.
- **Why:** Containerization and the database swap added things that can break; automated integration and E2E tests catch regressions without manual testing.

### 5. Deploy to the cloud
- **What:** Deploy the container to a managed environment. Define infrastructure as code (e.g. CloudFormation) so the deployment is reproducible. For the first deploy, run with elevated credentials only while watching every step.
- **When:** Once the application is verified under Compose with passing tests.
- **Why:** The app runs in one container and only needs a database, so many managed hosts work. Infrastructure-as-code makes the environment repeatable and sets up reuse for later environments.

### 6. CI/CD automation
- **What:** Configure a pipeline that, on every push to the main branch, runs frontend and backend tests in parallel, builds the containers, runs integration and end-to-end tests, and deploys only if everything passes. Use a scoped, short-lived credential (e.g. a GitHub OIDC role) for the deploy instead of standing admin access.
- **When:** After a successful first manual deploy.
- **Why:** CI guards against breakage on every push; CD deploys automatically once checks pass; scoped credentials remove the standing elevated access used for the first deploy.

### 7. Clean up
- **What:** Delete all cloud resources created for the deployment when they are no longer needed, and verify nothing is left running.
- **When:** When the environment is no longer in use.
- **Why:** Idle resources incur ongoing cost.

## Deliverables

- `frontend/`, `backend/` — application code, unchanged in behavior from the development process.
- `Dockerfile` — multi-stage build producing a single image (backend serves the built frontend).
- `docker-compose.yaml` — runs the app and database locally with health checks.
- `openapi.yaml` — the same API contract, upheld for the containerized services.
- `tests/` and an end-to-end suite (e.g. `e2e/`) — unit, integration, and E2E coverage.
- Infrastructure-as-code templates and CI/CD workflow definitions.

## Recommended tooling

- **Containerization:** Docker with multi-stage builds and minimal base images.
- **Local orchestration:** Docker Compose for development/production parity.
- **Database:** Postgres for production; SQLite remains fine for local development.
- **Hosting:** Any managed container host (AWS, Render, Railway, Fly.io). TLS/WSS can be handled by a reverse proxy such as Caddy.
- **CI/CD:** GitHub Actions, authenticating to the cloud with a scoped OIDC role.

## Beyond this process

A single-instance deploy is suitable for a proof of concept. For real production use, prefer a managed database service, put internal resources on private networks, and plan for scaling and load balancing (covered by the DevOps process).
