# Example: DevOps and Observability for an AI-Built App

> **Process document:** [`04_devops.md`](./04_devops.md) — *DevOps and Observability with AI Assistance*
>
> This is a worked example of that process. It records the concrete steps taken to make the **Interview Canvas** deployment production-ready and the reasoning behind each one. It continues from [`03_deployment-example.md`](./03_deployment-example.md). Source: Part 4 of the AI Dev Tools Zoomcamp series by Alexey Grigorev.

## Starting point

The deployed application from the previous example: containerized, tested (integration + E2E), running on AWS via CloudFormation, and auto-deployed by GitHub Actions on every push to `main`. The goal here is to make this deployment follow production best practices. The work uses AWS and CloudFormation, but the principles are tool-agnostic.

## The steps (what happened and why)

### 1. Separate dev and prod environments
- **What:** Asked the assistant to create a second, independent copy of the infrastructure (reusing the infrastructure-as-code); the existing stack becomes **dev**, the copy becomes **prod**. Some things change (e.g. machine size) but most resources stay identical.
- **Why:** Auto-deploying every push straight to users is fine early on. Once there are real users, you want a place to catch regressions before they reach them.

### 2. Add a manual promotion workflow
- **What:** Kept auto-deploy to dev on every push, and added a manually triggered GitHub Actions workflow (confirmation checkbox + optional release tag) that promotes the current dev version to prod.
- **Why:** Dev should always run the latest code automatically; prod changes should be deliberate and controlled, gated by a human.

### 3. Split build from deploy (build once, deploy many)
- **What:** Split the old combined "deploy" stage into **Build** (build the image, tag it `YYYYMMDD-HHMMSS-shortsha`, push to Amazon ECR) and **Deploy** (pull the tagged image and run it on dev). Prod promotion pulls the *same* image tag already running in dev.
- **Why:** Building on the EC2 host during deploy is an anti-pattern: build and deploy are separate concerns (a failed build should stop deployment), and rebuilding at promotion time means prod might not be identical to what was tested in dev. The sortable timestamp + commit SHA ties any running image back to exact source.

### 4. Instrument the backend with OpenTelemetry
- **What:** Asked the agent to instrument the FastAPI backend with OpenTelemetry, attaching **service name**, **environment**, and **deployed version** to all telemetry. FastAPI auto-instrumentation needs only a few lines of setup; telemetry is exported over OTLP.
- **Why:** Two environments reduce accidents but bugs still escape. You need to detect failures quickly and understand *why* they happen. Baseline metrics (CPU, memory, RPS) show *that* something is wrong; richer telemetry (metrics, logs, traces) explains *why*.

### 5. Add a collector and storage backends
- **What:** Created an `observability/` directory as a *separate* Docker Compose project containing the OTel Collector, Prometheus (metrics), Loki (logs), Tempo (traces), and Grafana (dashboards).
- **Why:** The exported OTLP telemetry isn't saved anywhere on its own. The collector sits between the app and storage and routes each signal type, so storage backends can change without touching app code.

### 6. Define application metrics and a dashboard
- **What:** Tracked product-specific metrics — interview rooms created, active participants, canvas elements created, component-creation failures — labelled with environment and version. Added a Grafana panel filterable by environment and deployed version. Verified locally: create a room, add an element, confirm it shows up in Grafana.
- **Why:** Infrastructure metrics aren't enough; you must measure what matters for *this* product so you can isolate a problem to a specific environment or release.

### 7. Deploy the observability stack
- **What:** Deployed the observability stack separately from the app stack and connected both dev and prod to it, then repeated the local test against the deployed Grafana. (If using a managed OTel-compatible service — CloudWatch, Grafana Cloud, Datadog, Sentry — this step can be skipped.)
- **Why:** Deploying it separately means observability survives app-stack changes. Note: the course exposes Grafana publicly for simplicity; in practice put such services on private networks with restricted access and authentication.

### 8. Add alerting
- **What:** Added an actionable alert for repeated canvas component-creation failures, using a threshold *and* duration that represent real user impact, with the alert payload including service, environment, deployed version, owner, and dashboard URL.
- **Why:** Nobody watches dashboards 24/7, so detection must be automatic. Threshold-plus-duration avoids firing on a single blip, and rich context lets the responder act immediately.

### 9. Add an AI on-call engineer
- **What:** Added an `on-call-engineer/` directory with a script that polls the alert API every minute and, when an alert fires, hands the alert details to a headless coding agent. The agent's mandate: investigate root cause, reproduce the failure, and — if it's a real bug — make the smallest fix, run backend tests, and commit; if it's a false positive, explain why and change nothing.
- **Why:** Alerts need someone (or something) to respond. The narrow mandate keeps an autonomous agent from making sweeping or unjustified changes. (The course uses a simple polling PoC; a production setup would be Alert → SNS → Lambda → isolated container job → headless agent → saved session log → terminated compute.)

### 10. Test the loop with a deliberate bug
- **What:** Asked an agent to introduce a realistic, reproducible bug in canvas component creation that the existing tests don't catch, then confirmed the alert fires and the on-call agent wakes up and responds.
- **Why:** Deliberately injecting a bug that passes existing tests proves the full detection → alert → response chain actually works end to end.

### 11. Clean up
- **What:** Deleted the CloudFormation stacks and independently verified nothing is still running (AWS console or a second agent scanning the account).
- **Why:** These resources were created for learning; forgotten resources mean a bigger bill.

## Result

The deployed app, made production-ready: separate dev/prod environments, controlled manual promotion, immutable build-once artifacts in a registry, full OpenTelemetry instrumentation, dashboards, actionable alerts, and an AI on-call responder — validated end to end with a deliberate bug.

## Beyond this example (production gaps to consider)

- Replace the EC2 shell-script deploy with a container management system (ECS or alternative).
- Make it easy to roll back a bad prod promotion (the tagged registry images make this feasible).
- Use a managed database service.
- Back up the database regularly, keep backups *outside* the IaC stack and in multiple independent copies, and test that restores work.
- Put internal services and resources on private subnets inside a VPC with restricted access.
- Learn load balancing and scaling for high traffic; container orchestration makes this easier.
- Have strong models (more than one) audit the code for security vulnerabilities, repeatedly.
