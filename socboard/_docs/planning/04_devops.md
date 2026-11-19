# Process: DevOps and Observability with AI Assistance

> **Worked example:** [`04_devops-example.md`](./04_devops-example.md)
>
> Continues from [`03_deployment.md`](./03_deployment.md).

This document describes the process for taking a deployed application and making it production-ready: what to do, when to do it, and why. The starting point is a containerized, tested application deployed to the cloud with CI/CD auto-deploying every push. The principles are tool-agnostic even where specific tools are named.

## Philosophy

- **Dev and prod are separate.** Dev always runs the latest code and auto-deploys on push; prod changes arrive deliberately, with more control.
- **Deploy once, promote the artifact.** Deploying puts a new build somewhere; promoting moves an *already tested* build forward. Promotion must never involve a new build.
- **Immutable artifacts.** Build an image once, store it in a registry, and deploy that same artifact to every environment so prod runs exactly what was tested.
- **Observability by design.** Collect enough telemetry to understand application behavior and find problems quickly; instrument from the start rather than retrofitting.
- **Detection must be automatic.** Nobody watches dashboards continuously, so failures are surfaced by alerts, and alerts have a responder.

## The pipeline (what, when, why)

### 1. Separate dev and prod environments
- **What:** Reuse the infrastructure-as-code to create an independent production copy; the existing stack becomes dev. Expect small differences (e.g. machine size) but keep most resources identical.
- **When:** First, once real users exist (or are imminent).
- **Why:** Auto-deploying every push straight to users is fine early on, but once there are real users you need a place to catch regressions before they reach them.

### 2. Controlled promotion
- **What:** Keep auto-deploy to dev on every push; add a manually triggered workflow (with a confirmation step and optional release tag) that promotes the current dev version to prod.
- **When:** As soon as a separate prod environment exists.
- **Why:** Dev should track the latest code automatically; prod changes should be deliberate and gated by a human.

### 3. Build once, deploy many
- **What:** Split the combined deploy step into **build** (build the image, tag it with a sortable, traceable tag such as `YYYYMMDD-HHMMSS-shortsha`, and push to a container registry) and **deploy** (pull the tagged image and run it). Promotion to prod pulls the *same* tag already running in dev.
- **When:** Before relying on promotion between environments.
- **Why:** Building on the host during deploy is an anti-pattern — build and deploy are separate concerns (a failed build should stop deployment), and rebuilding at promotion time means prod may differ from what was tested. A timestamp plus commit SHA ties any running image back to exact source.

### 4. Instrument the application
- **What:** Add OpenTelemetry to the backend, attaching service name, environment, and deployed version to all telemetry. Export over OTLP; auto-instrumentation covers common libraries with minimal setup.
- **When:** Once the build/deploy separation and environments are in place.
- **Why:** Two environments reduce accidents but bugs still escape. Baseline metrics (CPU, memory, requests per second) show *that* something is wrong; metrics, logs, and traces together explain *why*.

### 5. Collector and storage
- **What:** Run an OpenTelemetry Collector between the app and storage, routing metrics, logs, and traces to appropriate backends (e.g. Prometheus, Loki, Tempo) with a dashboarding tool (e.g. Grafana). Keep this as a separate project from the application stack.
- **When:** After the app is instrumented and exporting telemetry.
- **Why:** Exported telemetry isn't stored on its own. The collector decouples the app from storage, so backends can change without touching app code. Keeping it separate means observability survives app-stack changes.

### 6. Application metrics and dashboards
- **What:** Define product-specific metrics (not just infrastructure ones), labelled with environment and deployed version, and build dashboards filterable by those labels. Verify by exercising the app and confirming the metrics appear.
- **When:** Once telemetry is being stored.
- **Why:** Infrastructure metrics aren't enough; measuring what matters for this product lets you isolate a problem to a specific environment or release.

### 7. Alerting
- **What:** Add actionable alerts on meaningful failure conditions, using both a threshold and a duration that reflect real user impact. Include service, environment, deployed version, owner, and dashboard URL in the alert payload.
- **When:** Once dashboards exist.
- **Why:** Threshold-plus-duration avoids firing on a single blip; rich context lets a responder act immediately.

### 8. On-call response
- **What:** Provide a responder for alerts. An AI agent can serve this role: on a firing alert it investigates the root cause, reproduces the failure, and — if it's a real bug — makes the smallest fix, runs the tests, and commits; if it's a false positive, it explains why and changes nothing. In real setups the responder must also decide whether to escalate to a human.
- **When:** Once alerts can fire.
- **Why:** Alerts need someone (or something) to react. A narrow mandate keeps an autonomous responder from making sweeping or unjustified changes.

### 9. Validate the detection loop
- **What:** Deliberately introduce a realistic, reproducible failure that existing tests don't catch, and confirm the alert fires and the responder reacts.
- **When:** After the alert and on-call response are wired up.
- **Why:** Injecting a bug that passes existing tests proves the full detection → alert → response chain works end to end.

### 10. Clean up
- **What:** Delete environment and observability resources when no longer needed, and independently verify nothing is still running.
- **When:** When environments are no longer in use.
- **Why:** Forgotten resources incur ongoing cost.

## Deliverables

- CI/CD workflows: automatic test/build/push/deploy-to-dev plus a manual prod-promotion workflow.
- Infrastructure templates for independent dev and prod stacks.
- An `observability/` project: collector, metrics/logs/traces storage, and dashboards.
- An on-call responder: an alert poller plus the responder's prompt/mandate.
- Backend changes: OpenTelemetry instrumentation (service/environment/version) and custom application metrics.
- Dashboards and alerts filterable by environment and version.

## Architecture flows

- **Deployment:** push to main → CI tests → build (image → registry with tag) → deploy tag to dev → manual trigger → prod pulls the dev tag.
- **Telemetry:** dev + prod apps → OTLP → collector → metrics/logs/traces storage → dashboards → alerts → on-call responder.

## Recommended tooling

- **Cloud & IaC:** any cloud with infrastructure-as-code (e.g. AWS + CloudFormation).
- **CI/CD:** GitHub Actions — an automatic workflow for dev, a manual workflow for prod promotion.
- **Container registry:** any registry (e.g. Amazon ECR, Docker Hub).
- **Telemetry:** OpenTelemetry SDK + auto-instrumentation, exported over OTLP.
- **Self-hosted observability:** OTel Collector, Prometheus (metrics), Loki (logs), Tempo (traces), Grafana (dashboards/alerts).
- **Managed alternatives:** CloudWatch, Grafana Cloud, Datadog, or Sentry — these remove the need to self-host the observability stack.

## Beyond this process (production gaps)

- Replace host-run deploy scripts with a container management system (e.g. ECS).
- Make rollback of a bad prod promotion easy (tagged registry images make this feasible).
- Use a managed database service.
- Back up the database regularly, keep backups outside the IaC stack and in multiple independent copies, and test that restores work.
- Put internal services on private subnets with restricted access and authentication (don't expose observability tools or databases publicly).
- Learn load balancing and scaling for high traffic; container orchestration makes this easier.
- Have strong models (more than one) audit the code for security vulnerabilities, repeatedly.
