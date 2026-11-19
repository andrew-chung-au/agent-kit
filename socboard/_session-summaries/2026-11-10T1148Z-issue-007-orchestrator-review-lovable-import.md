# Issue #7: Review and record the imported Lovable frontend base

**Date:** 2026-11-10T11:48Z (UTC)
**Spec version:** d913e19

## What changed and why

- #7 was re-scoped earlier today from "import the frontend" to "review and record it", because the human had already committed the Lovable output (`fab3dd3`) and it turned out to be a TanStack Start project (server-side rendering), not the static single-page app the stack record requires.
- The Engineer (Kiro Web) reviewed `frontend/` read-only against the seven guardrails and the named checks, listed the differences between the service layer and the contract, posted the dependency list (52 runtime, 21 development), proposed the `AGENTS.md` Layout line, and added the source record `_docs/records/2026-11-10T0946Z-source-lovable-frontend.md` with its index row. Nothing under `frontend/` changed.
- The human approved the dependency list as a retroactive record, the Layout line, and self-hosting IBM Plex (a criterion of #27). The Layout line was committed with `HUMAN_APPROVED=1`.
- QA was run by the human in Claude Code and passed at 4f0792f (comment 6766386157): 8 of 8 criteria, Verify 23 tests.
- Merged through GitHub as PR #28 (merge commit 992d941), together with PR #29 (the guidance, roadmap and stack-record note, merge commit 9845737).
- #27's body was updated before its approval (self-hosted fonts, a production-bundle check for the mock's demo credentials, removal of unused code); the human then approved it. Its hash is 0b17057e196e8e588f6e03efc90cbce0e4513a70c7f7fad7be0ef246c1e9bebf.

**What I learned:** a read-only success is not a write test. A probe that returned 404 for a nonexistent issue looked like proof the token could write, and it was not: GitHub returns 404 before it checks permission. The real cause was the token's repository access, found only when the real post failed with a visible 403.

## Reflection

### Orchestrator

**What slowed you down (evidence):** the QA agent in the container could not post comments for several rounds (`make issue-comment` exit 1, then a misleading 404 probe) until the token's repository access was fixed; the script hides gh's stderr, so the 403 was invisible until a debug copy kept it.
**What nearly went wrong or was blocked:** I read the 404 probe as "writes allowed" and sent the human down a wrong path before the 403 appeared; I should have said a nonexistent-issue probe cannot show write permission.
**One proposed change (file, expected effect, measure):** `_docs/agent-kit/scripts/issue-comment.sh`: print gh's stderr (without the token) on a failed POST instead of discarding it. Expected effect: the cause shows on the first failure. Measure: rounds of diagnosis before a failed post is understood. (A protected kit file; raise it upstream, do not patch locally.)

### PM

unknown (role not asked)

### Engineer

unknown (role not asked)

### QA

unknown (role not asked)

## Launch usage

- QA, #7, Claude Code (the human's launch of the `qa-engineer` agent): active time unknown, tool uses unknown; model unknown.
- QA, #7 diagnostic runs in the container (read-only checks, a probe, a retry): unknown, unknown; Claude Code.
- Engineer work on #7 was done by the orchestrator in Kiro Web, model auto, not as a separate launch: none.

## Files created or modified

- `_docs/records/2026-11-10T0946Z-source-lovable-frontend.md`, `_docs/index.md`, `AGENTS.md` (Layout line) via PR #28.
- `_docs/planning/lovable-guidance.md`, `_docs/planning/core-backlog.md`, `_docs/planning/roadmap-1-core.md`, `_docs/planning/roadmap-2-ponytail-trial.md`, `_docs/decisions/20261105T133030Z-stack-choice.md` via PR #29.
- This file.

## Decisions made by the human

- Dependency list approved as a retroactive record; #27 removes the Lovable, server and unused packages.
- `AGENTS.md` Layout line approved.
- Google Fonts: self-host IBM Plex, inside #27.
- #27 approved with its updated body.
- The human fixed the container's GitHub token (repository access) so the QA agent can post.
- Allowed the orchestrator to open pull requests again (PR #28, PR #29).

## Mismatches with the spec or design docs

- The spec notes on #15 (the meaning of "age" in the queue order) and #19 (who may read the audit trail) are still undecided.
- The mock in the import lacks the 20-second new-alert timer, the `VITE_FEATURE_REASSIGN` flag and Lead-only limits on the closed list and the audit trail; these are in #8.

## Commands to validate

**Verify:** `make verify` (QA: 23 tests passed at 4f0792f in the human's container).
**Decisions:** `make decisions`

## Proposed AGENTS.md changes

none

## Temporary changes

- `.scratch/` holds drafts and dumps (git-ignored); `make clean-scratch` clears it.
- The container's `GH_TOKEN` repository access was changed by the human; the rebuild of the container is the human's.

## Interruptions

- The first QA launch in Claude Code stopped before posting (`make issue-comment` failed); it left no changes and was re-run after the token fix.
- PRs #28 and #29 were merged through GitHub, so the clean-clone push check did not run for them.

## Unrelated problems noticed but not fixed

- `issue-comment.sh` hides gh's stderr (see Reflection).
- The OpenCode and Claude Code read checks of the vendored ponytail file are still recorded "not tested" on #23.
- `make kit-check` still reports drift on several kit files (noted in earlier summaries).

## Follow-ups for the next session

- Start #27 (approved; the spike first). The handoff is the last section of this file. Ask before installing dependencies; a font package or files need the human's approval before the commit.
- Then #8, then #9 onward, approving each as the previous nears done.
- Ponytail: settle the human tasks `decide-claude-code-layer` and `check-agent-commit-lines`, record the epoch start, decide whether #27 counts as a baseline issue, and run the first shadow review after the first baseline issue's QA PASS.
- Raise the `issue-comment.sh` stderr change upstream.

## Handoff for #27 (Make the frontend build static and remove Lovable coupling)

**State:** `main` is at 9845737 (PR #28 merged as 992d941, PR #29 as 9845737). #27 is open and `approved`; its body hash `0b17057e196e8e588f6e03efc90cbce0e4513a70c7f7fad7be0ef246c1e9bebf` equals the recorded hash (run `make issue-hash N=27` and compare before starting). Tier: Standard (PM proposal). Next in order after #27: #8, then #9 onward.

**Read first, in order:** `AGENTS.md`; `_docs/agent-kit/process.md` and `_docs/agent-kit/team/software-engineer.md`; `make issue-dump N=27`, then `.scratch/issue-27.json` (the body and both PM comments, including the open package-manager question, which defaults to keeping bun); the four review comments on #7 (findings, service-layer differences, dependency list, Layout line); `_docs/records/2026-11-10T0946Z-source-lovable-frontend.md`; the "Update 2026-11-10" section of `_docs/planning/lovable-guidance.md`.

**Do:**
1. Post an `Orchestrator:` claim comment (`_docs/agent-kit/procedures/orchestrator-comments.md`), then work on a branch such as `issue-27-static-frontend-build` from `main`.
2. Spike first, as the issue says: try TanStack Start's single-page mode in `frontend/vite.config.ts`; if the build still produces server, Nitro or Cloudflare output, fall back to plain Vite and React with TanStack Router. Record the result on the issue and in `lovable-guidance.md`.
3. Remove the Lovable coupling and unused code (list in #7 comment 1 and the source record): `@lovable.dev/*`, `src/lib/lovable-error-reporting.ts` and its callers in `src/routes/__root.tsx`, `.lovable/`, the Lovable block of `frontend/AGENTS.md` (keep its "Project rules"), the Lovable boilerplate in `frontend/README.md`, `src/components/ui/chart.tsx` with `recharts`, and shadcn component files nothing imports (compute that list with a search of `frontend/src`; 8 of 46 are imported directly).
4. Self-host IBM Plex Sans and Mono (weights 400, 500, 600); the built output must not mention `fonts.googleapis.com` or `fonts.gstatic.com`. Record the font licence in the source record.
5. Add the production-bundle check: a build with `VITE_USE_MOCK` false must not contain `analyst-a-pass`, `analyst-b-pass`, `lead-pass` or the `<script>alert('xss')` fixture, and `make frontend-build` fails if one appears.
6. Add `make frontend-install` and `make frontend-build`. They are in the protected `Makefile`: show the human the diff and commit with `HUMAN_APPROVED=1` only after approval. `frontend-install` must install from the lockfile without changing it; `frontend-build` must fail if `index.html` is missing or server/worker output appears.

**Ask the human before:** installing dependencies or anything large, adding a font package or font files, changing the package manager, and committing the `Makefile`.

**Unknowns and limits:**
- Whether the Kiro Web sandbox can reach the npm or bun registry is unconfirmed; check with a read-only call before relying on it. If it cannot, write the changes and checks and ask the human to run the spike in the container.
- `make verify`'s tests step may not run in Kiro Web (`uv` cannot create its Python directory); the human's container can run it.
- The container's agents now post issue comments after the token fix; Kiro Web posts through `make issue-comment`. Use `make issue-dump` (works in both) to read issues.
- Commits end with `Assisted-by: Kiro`. Stage files by name. The human runs QA in Claude Code; the orchestrator runs `make assert-clean` afterwards and posts the Close comment after the human merges.
- Ponytail trial: record tool and model on the `Launch usage` line. Whether #27 counts as a baseline issue is undecided (it cleans up the scaffold); do not treat it as one until the human says so.

**Out of scope for #27:** mock rules, fixtures, tests and the dev-server and test make targets (#8); the OpenAPI contract (#9); serving the build from FastAPI and deep-link fallback (Deploy phase); visual changes.
