# Example: Deploy a Full-Stack App with AI Coding Assistants

> **Process document:** [`03_deployment.md`](./03_deployment.md) — *Deploying with AI Assistance*
>
> This is a worked example of that process. It records the concrete steps taken to deploy the **Interview Canvas** application and the reasoning behind each one. It continues from [`02_development-example.md`](./02_development-example.md). Source: Part 3 of the AI Dev Tools Zoomcamp series by Alexey Grigorev.

## Starting point

The locally working application from the previous example: a React frontend, a FastAPI backend, and SQLite persistence for the system-design interview tool. The goal here is to make it accessible to everyone on the internet.

## The steps (what happened and why)

### 1. Containerize into a single image
- **What:** Asked the assistant for a Dockerfile that builds the frontend with Node, then builds a Python image containing the backend plus the compiled frontend static files, with the backend serving the frontend. Result is a two-stage build: compile the frontend, then copy only the built files into the backend image (no Node dependencies). Built and ran it with a named volume for the SQLite file, then ran the **two-session test** (create a session, join from a second browser, move an element as the candidate, confirm the interviewer sees it).
- **Why:** In development the frontend runs separately because Vite watches and hot-reloads. In production the frontend is static after one build, so the backend can serve it — meaning only **one** container is needed, not two.

### 2. Switch from SQLite to Postgres
- **What:** Started a local Postgres container, then asked the assistant to add Postgres support to the backend. Ran the backend against Postgres via the `SDIP_DATABASE_URL` env var and repeated the two-session test.
- **Why:** SQLite is convenient locally, but production typically uses Postgres. This is exactly why the backend was built on SQLAlchemy earlier — the switch is simple and requires no rewrite.

### 3. Add Docker Compose
- **What:** Asked the assistant to create `docker-compose.yaml` with two services — Postgres and the app — including a health check so the app waits until Postgres accepts connections. Ran the whole stack with `docker compose up --build`.
- **Why:** Replaces the separate manual `docker run` for Postgres with a single source of truth that starts the entire application with one command.

### 4. Add integration and end-to-end tests
- **What:** Asked the assistant to create integration tests that run against `docker-compose.yaml`, verifying the two newly added things that could break: the frontend compiles correctly, and the backend can talk to Postgres. Then added a Playwright end-to-end test (in an `e2e/` folder) that automates the two-session test — log in as interviewer, create a session, share the link, join as candidate, change the canvas, verify the interviewer sees it. Ran with `make e2e`.
- **Why:** Containerization and the Postgres switch introduced new failure points; automated integration and E2E tests cover them so regressions are caught automatically.

### 5. Deploy to AWS
- **What:** Asked the assistant to deploy using AWS CloudFormation, run with a temporary admin user while watching every step. The result runs the app, Postgres, and Caddy (for HTTPS/WSS) on a single EC2 instance.
- **Why:** The app runs in one container and only needs Postgres, so many managed-container hosts work (Render, Railway, Fly.io, AWS). A single EC2 instance is fine for a proof-of-concept — though a managed database (e.g. RDS) would be better for real use.

### 6. Set up CI/CD with GitHub Actions
- **What:** Created a GitHub OIDC role and a workflow so that on every push to `main` it: runs frontend and backend tests in parallel, builds the containers, runs integration tests, runs end-to-end tests, and — only if everything passes — deploys the new version. The runner assumes a restricted AWS role via OIDC instead of using admin credentials.
- **Why:** The admin-user deploy was acceptable only while watched manually. CI automatically guards against breakage on every push; CD deploys automatically once checks pass; and OIDC with a restricted role removes the standing admin access.

### 7. Clean up
- **What:** Deleted all CloudFormation-created resources (`aws cloudformation delete-stack` + `wait stack-delete-complete`).
- **Why:** These resources were created for learning; leaving them running costs money.

## Result

The locally working app, taken to production: containerized into one image, switched to Postgres, orchestrated with Docker Compose, covered by integration and E2E tests, deployed to AWS via CloudFormation, and deployed automatically on every passing push through a CI/CD pipeline. Making this deployment production-ready is covered by the next example.
