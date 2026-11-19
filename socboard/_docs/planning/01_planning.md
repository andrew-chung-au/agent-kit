# Process: Plan a Full-Stack App with AI Assistance

> **Next process:** [`02_development.md`](./02_development.md) — *Build a Full-Stack App with AI Assistance*

This document describes the process for planning a full-stack application *before* any building begins: what to produce, when to produce it, and why. It sits in front of the development process and exists to turn a raw idea into a precise, agreed, buildable specification — the exact input the first development step assumes already exists.

The guiding principle across modern AI-assisted workflows is that the *specification*, not the code, is the source of truth an agent builds against. Ambiguity is the main failure mode of "vibe coding": vague prompts produce inconsistent, unreviewable output. Planning removes that ambiguity up front. ([spec-driven development overview](https://codewave.com/feeds/blog/spec-driven-development-ai-agentic-sdlc-2026)) *Content was rephrased for compliance with licensing restrictions.*

## Philosophy

- **Specify before you build.** A clear, testable specification captured before implementation is what lets an agent produce code that fits the project instead of guessing.
- **Decide the expensive things first.** Planning makes the costly, hard-to-reverse decisions — scope, data model, the one problem being solved — visible before any code locks them in. ([planning before development](https://hapy.co/journal/how-to-plan-software-project)) *Content was rephrased for compliance with licensing restrictions.*
- **Human-gated phases.** Planning moves through a short pipeline where each phase has a human review gate before the next. The gate, not the artifact, is the mechanism that keeps the work honest.
- **Scope ruthlessly.** A first version should prove the core idea, not carry every feature. Explicit non-goals are as valuable as goals.
- **Testable intent.** Every requirement is written so you can later tell, objectively, whether it was met. If it can't be verified, it isn't done.
- **Keep it proportionate.** For a project of this size (roughly one person, a few weeks), the plan is a handful of short, living documents — not a heavyweight requirements binder.

## The pipeline (what, when, why)

### 1. Frame the problem
- **What:** Write one to two paragraphs capturing the single problem the application solves, who has that problem, and what "better" looks like for them. State the core assumption you most need to prove.
- **When:** First, before anything else.
- **Why:** Everything downstream is validated against this. Naming the one problem and the key assumption keeps scope honest and gives the MVP a clear target. ([focusing an MVP on one problem](https://www.codersarts.com/post/how-to-decide-what-goes-into-your-mvp-a-feature-prioritization-guide-for-founders)) *Content was rephrased for compliance with licensing restrictions.*

### 2. Establish project principles (the "constitution")
- **What:** Record the durable, non-negotiable constraints and preferences that every later decision must respect: language/stack intent, quality bar, security and privacy rules, licensing, deployment target, and any hard constraints (budget, time, data residency).
- **When:** Early, right after the problem is framed.
- **Why:** These principles frame the questions you ask when specifying, constrain the architecture when planning, and keep each agent prompt from "resetting" to arbitrary defaults. ([role of a project constitution](https://never-stop-learning.de/spec-driven-development-the-methodology-behind-the-magic/)) *Content was rephrased for compliance with licensing restrictions.*

### 3. Discover users and journeys
- **What:** Identify the user roles and sketch the one or two primary end-to-end journeys through the app (the "happy paths"). Note the key screens or interactions each journey touches.
- **When:** Once the problem and principles are set.
- **Why:** Journeys convert an abstract idea into concrete flows you can turn into requirements and, later, into the end-to-end tests the development and deployment processes rely on.

### 4. Write user stories with acceptance criteria
- **What:** Break each journey into small user stories in the form *"As a [role], I want [goal], so that [benefit]."* Give every story explicit, testable acceptance criteria (ideally Given/When/Then).
- **When:** After the journeys are mapped.
- **Why:** Stories keep the focus on user value rather than implementation, and acceptance criteria are the objective definition of done — the same criteria that tests are written against later. ([user stories and acceptance criteria](https://thinkcloudly.com/blog/user-stories-acceptance-agile/)) *Content was rephrased for compliance with licensing restrictions.*

### 5. Prioritize and set the MVP scope
- **What:** Classify every story with MoSCoW — Must have, Should have, Could have, Won't have (this release). The Must-haves are the MVP. Write an explicit **non-goals** list from the "Won't have" items.
- **When:** Once stories exist and before planning the build.
- **Why:** Time and capacity are limited; MoSCoW gives a shared language for scope decisions and keeps the first build lean enough to prove the core assumption. Recording non-goals prevents silent scope creep. ([MoSCoW for MVP scope](https://hapy.co/journal/moscow-prioritization)) *Content was rephrased for compliance with licensing restrictions.*

### 6. Clarify edge cases and unknowns
- **What:** Review the Must-have stories for ambiguity, missing edge cases, and open questions. Resolve each one, or record it as an explicit assumption. An AI assistant is useful here to interrogate the spec and surface gaps.
- **When:** After scope is fixed, before the technical plan.
- **Why:** Clarifying before planning is cheaper than discovering the gap mid-build; unresolved ambiguity is exactly what produces inconsistent agent output.

### 7. Sketch the high-level plan
- **What:** Decide the shape of the solution at a high level: the major components (frontend / backend / database, aligned with the development process), the core data entities and their relationships, the main API surface, and any external dependencies. Keep it a sketch, not a detailed design — the contract and schema are produced during development.
- **When:** Once the scope is clear and unambiguous.
- **Why:** A high-level plan constrains the architecture so later implementation fits the project, and surfaces the data model early — the decision most expensive to change later.

### 8. Assess risks
- **What:** List the main things that could derail the project — technical unknowns, risky integrations, time constraints — and note a mitigation or fallback for each. Flag any Must-have that depends on an unproven piece.
- **When:** Alongside the high-level plan.
- **Why:** Making risks visible before development lets you de-risk cheaply (spike, simplify, or cut scope) instead of discovering the problem late.

### 9. Break down into tasks on a tracker
- **What:** Turn the Must-have stories into discrete, ordered tasks in a publicly accessible task tracker, each carrying its acceptance criteria and an owner (human or a specific agent). Sequence them so each produces something testable, matching the incremental-verification approach of the development process.
- **When:** Last planning step, immediately before development starts.
- **Why:** A task breakdown maps intent to executable work and owners, gives agents a durable backlog to work from, and provides the evidence trail that the work followed the plan.

### 10. Review gate before build
- **What:** Do a final human review of the whole plan — problem, principles, stories + acceptance criteria, scope/non-goals, high-level plan, risks, task list — and sign off. Confirm the specification is complete enough to hand to the development process.
- **When:** The boundary between planning and development.
- **Why:** The human gate is the safeguard: it catches ambiguity and scope problems while they're still cheap, and produces the agreed spec that development step 1 assumes already exists.

## Deliverables

These are the planning artifacts that feed the rest of the pipeline. Keep them as short, living documents.

- `product-spec.md` — problem statement, user roles and journeys, user stories with acceptance criteria, MVP scope, and an explicit **non-goals** list. (This is the spec the development process consumes.)
- `principles.md` (or a section of `AGENTS.md`) — the project "constitution": durable constraints, stack intent, quality/security/privacy rules.
- `plan.md` — high-level solution sketch: components, core data entities, main API surface, external dependencies, and the risk assessment.
- A **task tracker** — the Must-have stories broken into ordered, owned tasks with acceptance criteria attached.

## Recommended tooling

- **Idea shaping & specification:** A conversational AI assistant (e.g. ChatGPT) to brainstorm, dictate the initial idea, and draft/interrogate the spec. Dictation mode is useful for getting as much context down as possible early.
- **Spec-driven scaffolding (optional):** Tools such as GitHub Spec Kit formalize the constitution → specify → clarify → plan → tasks phases with per-phase prompts and reviewable Markdown outputs, and run inside agents like Claude Code, Codex, or Cursor. ([Spec Kit phases](https://xebia.com/blog/building-software-with-spec-kit/)) *Content was rephrased for compliance with licensing restrictions.*
- **Prioritization:** MoSCoW for scope; a simple Must/Should/Could/Won't table is enough at this scale.
- **Task tracking:** Any publicly accessible tracker (GitHub Issues/Projects, a kanban board) so progress and the plan-to-work link are visible and auditable.

## Beyond this process

- **The plan is living.** Revisit scope, non-goals, and the task list as you learn during development; the spec is the source of truth, so keep it current rather than letting code drift away from it.
- **Define the agent team here if you use one.** If specialized agents (PM, engineer, QA, on-call) will do the work, decide their roles and how they hand off during planning so the task owners in the tracker are meaningful.
- **Right-size the ceremony.** Scale the depth of each artifact to the project. A small idea needs only a page or two per document; the value is in the decisions, not the word count.
