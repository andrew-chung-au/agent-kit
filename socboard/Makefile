# SOCBoard project commands. Core targets come from the agent kit's
# templates/Makefile.mk; recipe lines are TAB-indented.

help: ## List targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_ -]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

verify: ## Run the verification gate: make verify [BASE=<commit>]
	$(if $(findstring $$,$(value BASE)),$(error Usage: make verify [BASE=<commit>] - BASE must not contain $$))
	@bash _docs/agent-kit/scripts/verify.sh "$$BASE"

assert-clean: ## Fail if this folder has uncommitted changes (used after QA)
	@bash _docs/agent-kit/scripts/assert-clean.sh

hooks: ## Install the repo's git hooks (where agents commit; never in a clean clone)
	@bash _docs/agent-kit/scripts/install-hooks.sh

clean-scratch: ## Empty .scratch/ at the end of an issue (refuses while a started process is running)
	@for f in .scratch/*.pid; do if [ -f "$$f" ] && kill -0 "$$(cat "$$f")" 2>/dev/null; then echo "$$f: process $$(cat "$$f") is still running; stop it first"; exit 1; fi; done
	@mkdir -p .scratch && find .scratch -mindepth 1 -delete && echo ".scratch/ is now empty"

tool-versions:: ## Print each tool's version, or "<tool>: missing"
	@for t in git gh node npm python3 uv docker; do if command -v "$$t" >/dev/null 2>&1; then "$$t" --version 2>&1 | { read -r first; echo "$$t: $$first"; }; else echo "$$t: missing"; fi; done

tool-versions::
	@if command -v bun >/dev/null 2>&1; then echo "bun: $$(bun --version)"; else echo "bun: missing"; fi

# --- GitHub issues (the project's tasks) ------------------------------------

issue-number-ok = $(and $(filter 1,$(words $(1))),$(if $(subst 0,,$(subst 1,,$(subst 2,,$(subst 3,,$(subst 4,,$(subst 5,,$(subst 6,,$(subst 7,,$(subst 8,,$(subst 9,,$(1))))))))))),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(filter 0%,$(1)),,ok),$(if $(word 10,$(subst 0,x ,$(subst 1,x ,$(subst 2,x ,$(subst 3,x ,$(subst 4,x ,$(subst 5,x ,$(subst 6,x ,$(subst 7,x ,$(subst 8,x ,$(subst 9,x ,$(1)))))))))))),,ok))

issue-hash: ## Print an issue body's sha256, author and owner check: make issue-hash N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-hash N=<issue number>))
	@python3 -B _docs/agent-kit/scripts/issue-hash.py "$$N"

issue-dump: ## Write an issue as JSON to .scratch/issue-<N>.json: make issue-dump N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-dump N=<issue number>))
	@mkdir -p .scratch
	@if python3 -B _docs/agent-kit/scripts/github_api.py dump "$(N)" > ".scratch/issue-$(N).json.tmp" 2>/dev/null && python3 -B -m json.tool ".scratch/issue-$(N).json.tmp" > /dev/null 2>&1; then mv ".scratch/issue-$(N).json.tmp" ".scratch/issue-$(N).json" && echo ".scratch/issue-$(N).json"; else rm -f ".scratch/issue-$(N).json.tmp"; echo "issue-dump: gh could not return valid JSON for issue $(N)" >&2; exit 1; fi

issue-body: ## Write an issue's title, labels and body, without comments, as JSON to .scratch/issue-<N>-body.json: make issue-body N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-body N=<issue number>))
	@mkdir -p .scratch
	@if r=$$(python3 -B _docs/agent-kit/scripts/github_api.py repo 2>/dev/null) && python3 -B _docs/agent-kit/scripts/github_api.py head "$$r" "$(N)" > ".scratch/issue-$(N)-body.json.tmp" 2>/dev/null && python3 -B -m json.tool ".scratch/issue-$(N)-body.json.tmp" > /dev/null 2>&1; then mv ".scratch/issue-$(N)-body.json.tmp" ".scratch/issue-$(N)-body.json" && echo ".scratch/issue-$(N)-body.json"; else rm -f ".scratch/issue-$(N)-body.json.tmp"; echo "issue-body: gh could not return valid JSON for issue $(N)" >&2; exit 1; fi

ponytail-metrics: ## Print the ponytail trial's per-issue figures from git and GitHub (read-only): make ponytail-metrics N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make ponytail-metrics N=<issue number>))
	@python3 -B scripts/ponytail_metrics.py "$$N"

sweep-due: ## Say whether a sweep is due (read-only; the sweep interval is set in the script)
	@python3 -B _docs/agent-kit/scripts/sweep-due.py

tier-check: ## Check a change against its tier's path limit: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]
	$(if $(and $(filter 1,$(words $(value TIER))),$(filter light standard heavy,$(value TIER))),,$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]))
	$(if $(findstring $$,$(value BASE)),$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>] - BASE must not contain $$))
	@bash _docs/agent-kit/scripts/check-tier.sh "$$TIER" "$$BASE"

# --- Stack -----------------------------------------------------------------

install: ## Install dependencies
	uv sync --locked --all-groups
	$(MAKE) frontend-install

test: ## Run all unit tests (Python, then frontend)
	uv run --locked pytest
	$(MAKE) frontend-test

test-one: ## Run one test file: make test-one FILE=path
	$(if $(findstring $$,$(value FILE)),$(error Usage: make test-one FILE=path/to/test_file - FILE must not contain $$))
	@test -n "$$FILE" || { echo "Usage: make test-one FILE=path/to/test_file"; exit 1; }
	uv run --locked pytest "$$FILE"

# e2e is also the name of the folder, so make would call the target up to date without this line.
.PHONY: e2e

e2e-install: ## Install the browser test's packages from e2e/bun.lock (Playwright, pinned); fails if the lockfile would change. The browser itself: cd e2e && bunx playwright install chromium
	cd e2e && bun install --frozen-lockfile

e2e: ## Drive the built site in a browser against the running Compose stack at SOCBOARD_BASE_URL (loopback http only; make compose-up first; make e2e-install and Chromium once); adds cases and uses a few of the key's 60 requests a minute
	@test -n "$$SOCBOARD_BASE_URL" || { echo "e2e: set SOCBOARD_BASE_URL to the stack's http address on the loopback (make compose-up publishes http://127.0.0.1:8080); the stack must be up"; exit 2; }
	@test -x e2e/node_modules/.bin/playwright || { echo "e2e: e2e/node_modules/.bin/playwright is missing; run make e2e-install first"; exit 1; }
	cd e2e && bun run test

test-stack: ## Run the journeys and the stack tests against the live Compose stack at SOCBOARD_BASE_URL (loopback http only; start it with make compose-up; adds cases and uses up the ingest key's allowance for a minute)
	@test -n "$$SOCBOARD_BASE_URL" || { echo "test-stack: set SOCBOARD_BASE_URL to the stack's http address on the loopback (make compose-up publishes http://127.0.0.1:8080)"; exit 2; }
	uv run --locked pytest tests/test_journeys.py tests/test_stack.py

# --- GitHub module (wrappers; no labels, edits or closes except issue-close) ----

issue-file-chars := a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 . _ / -
issue-strip-chars = $(if $(2),$(call issue-strip-chars,$(subst $(firstword $(2)),,$(1)),$(wordlist 2,$(words $(2)),$(2))),$(1))
issue-file-ok = $(and $(filter 1,$(words $(1))),$(if $(call issue-strip-chars,$(1),$(issue-file-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(filter .scratch/%,$(1)),$(if $(findstring ..,$(1)),,ok))

issue-create: ## File one issue from a file under .scratch/ (first line Title: <text>, blank line, body): make issue-create FILE=.scratch/<name>.md
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make issue-create FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash _docs/agent-kit/scripts/issue-create.sh "$(FILE)"

issue-comment: ## Post a file under .scratch/ as one comment (first line PM: Engineer: QA: or Orchestrator:): make issue-comment N=<issue number> FILE=.scratch/<name>.md
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-comment N=<issue number> FILE=.scratch/<name>.md))
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make issue-comment N=<issue number> FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash _docs/agent-kit/scripts/issue-comment.sh "$(N)" "$(FILE)"

issue-reason-ok = $(and $(filter 1,$(words $(1))),$(filter completed not-planned,$(1)),$(if $(filter-out completed not-planned,$(1)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok))

issue-close: ## Close one issue when its recorded history shows the process was followed (the orchestrator only): make issue-close N=<issue number> [REASON=not-planned]
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-close N=<issue number> [REASON=not-planned]))
	$(if $(value REASON),$(if $(call issue-reason-ok,$(value REASON)),,$(error Usage: make issue-close N=<issue number> [REASON=completed|not-planned])))
	@bash _docs/agent-kit/scripts/issue-close.sh "$(N)" $(if $(value REASON),"$$REASON")

# --- Permission log (procedures/permission-log.md) --------------------------

# Both targets follow the validation rule above. permission-report passes SINCE on and the
# script accepts only a real YYYY-MM-DD date (an empty SINCE means no limit).
# permission-logs-prune checks DAYS here (1 to 4 digits, no leading zero) and the script
# checks the 3650 limit, so a bad value deletes nothing.

permission-days-ok = $(and $(filter 1,$(words $(1))),$(if $(subst 0,,$(subst 1,,$(subst 2,,$(subst 3,,$(subst 4,,$(subst 5,,$(subst 6,,$(subst 7,,$(subst 8,,$(subst 9,,$(1))))))))))),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(filter 0%,$(1)),,ok),$(if $(word 5,$(subst 0,x ,$(subst 1,x ,$(subst 2,x ,$(subst 3,x ,$(subst 4,x ,$(subst 5,x ,$(subst 6,x ,$(subst 7,x ,$(subst 8,x ,$(subst 9,x ,$(1)))))))))))),,ok))

permission-report: ## Summarise the permission logs of all tools: make permission-report [SINCE=<YYYY-MM-DD or YYYY-MM-DDTHH:MMZ>]
	$(if $(findstring $$,$(value SINCE)),$(error Usage: make permission-report [SINCE=<YYYY-MM-DD or YYYY-MM-DDTHH:MMZ>] - SINCE must not contain $$))
	@python3 -B _docs/agent-kit/scripts/permission-report.py "$$SINCE"

permission-logs-prune: ## Delete permission logs older than DAYS days (the human runs it): make permission-logs-prune DAYS=<1 to 3650>
	$(if $(call permission-days-ok,$(value DAYS)),,$(error Usage: make permission-logs-prune DAYS=<1 to 3650>))
	@python3 -B _docs/agent-kit/scripts/permission-logs-prune.py "$$DAYS"

# --- When the kit came with a MANIFEST.sha256 (a released kit) -------------

kit-check: ## Say whether the kit folder is pristine or a derivative of KIT_VERSION (read-only)
	@python3 -B _docs/agent-kit/scripts/kit-check.py

kit-other-chars := a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 . _ / -
kit-other-strip = $(if $(2),$(call kit-other-strip,$(subst $(firstword $(2)),,$(1)),$(wordlist 2,$(words $(2)),$(2))),$(1))
kit-root-ok = $(and $(filter 1,$(words $(1))),$(if $(call kit-other-strip,$(1),$(kit-other-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(filter-out /% -%,$(1)),$(if $(findstring ..,$(1)),,ok))

kit-compare: ## List how one kit folder differs from another (read-only, no default roots): make kit-compare KIT_A=<folder> KIT_B=<folder>
	$(if $(call kit-root-ok,$(value KIT_A)),,$(error Usage: make kit-compare KIT_A=<folder> KIT_B=<folder> - each one word, a relative path with letters digits . _ / - only))
	$(if $(call kit-root-ok,$(value KIT_B)),,$(error Usage: make kit-compare KIT_A=<folder> KIT_B=<folder> - each one word, a relative path with letters digits . _ / - only))
	@python3 -B _docs/agent-kit/scripts/kit-compare.py "$$KIT_A" "$$KIT_B"

kit-baseline: ## Find the commit of a clone of the kit repo that a live kit with no manifest was copied from (read-only): make kit-baseline KIT=<live kit folder> SOURCE=<clone folder>
	$(if $(call kit-root-ok,$(value KIT)),,$(error Usage: make kit-baseline KIT=<live kit folder> SOURCE=<clone folder> - each one word, a relative path with letters digits . _ / - only))
	$(if $(call kit-root-ok,$(value SOURCE)),,$(error Usage: make kit-baseline KIT=<live kit folder> SOURCE=<clone folder> - each one word, a relative path with letters digits . _ / - only))
	@python3 -B _docs/agent-kit/scripts/kit-baseline.py "$$KIT" "$$SOURCE"

# A plain relative path: one word of letters, digits, . _ / - only, no $ and no "..".
# Reuses kit-other-chars and kit-other-strip above (no .scratch/ requirement here).
kit-path-ok = $(and $(filter 1,$(words $(1))),$(if $(call kit-other-strip,$(1),$(kit-other-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(findstring ..,$(1)),,ok))

kit-feedback: ## Write a read-only feedback bundle under .scratch/ from a project's kit (reverse import): make kit-feedback PROJECT=<project root> KIT=<reference kit>
	$(if $(call kit-path-ok,$(value PROJECT)),,$(error Usage: make kit-feedback PROJECT=<project root> KIT=<reference kit> - PROJECT: one word, letters digits . _ / - only, no ..))
	$(if $(call kit-path-ok,$(value KIT)),,$(error Usage: make kit-feedback PROJECT=<project root> KIT=<reference kit> - KIT: one word, letters digits . _ / - only, no ..))
	@python3 -B _docs/agent-kit/scripts/kit-feedback.py "$$PROJECT" "$$KIT"

# --- Project targets (this project's own; add below) -------------------------

decisions: ## List the decision records with their Status word (proposed, approved or superseded)
	@for f in _docs/decisions/*.md; do s=$$(grep -m1 -i -o 'status: [a-z]*' "$$f" | cut -d' ' -f2); printf '%-11s %s  (%s)\n' "$${s:-MISSING}" "$$(head -n 1 "$$f" | sed 's/^# //')" "$$(basename "$$f")"; done

# --- API contract (issue #9) -------------------------------------------------

contract-check: ## Validate openapi.yaml against the OpenAPI version it declares (3.1); fails on an invalid file: make contract-check [FILE=<path>]
	$(if $(value FILE),$(if $(call kit-root-ok,$(value FILE)),,$(error Usage: make contract-check [FILE=<path>] - FILE must be one word, a relative path of letters, digits and . _ / - only, not starting with - or /, and not containing two dots (..))))
	uv run --locked openapi-spec-validator "$(if $(value FILE),$(FILE),openapi.yaml)"

# --- Terraform offline checks (issue #199; never plan or apply) ----------------

tf-check: ## Offline fmt, validate and (where tests/ exists) test of every terraform/ folder, on a copy in .scratch/tf-check; no AWS credential: make tf-check [TERRAFORM=<path>]
	$(if $(value TERRAFORM),$(if $(call kit-root-ok,$(value TERRAFORM)),,$(error Usage: make tf-check [TERRAFORM=<path>] - TERRAFORM must be one word, a relative path of letters, digits and . _ / - only, not starting with - or /, and not containing two dots (..))))
	@command -v "$(or $(TERRAFORM),terraform)" >/dev/null 2>&1 || { echo "tf-check: $(or $(TERRAFORM),terraform) not found; install the version in terraform/.terraform-version"; exit 2; }
	$(or $(TERRAFORM),terraform) -chdir=terraform fmt -check -recursive
	@rm -rf .scratch/tf-check && mkdir -p .scratch/tf-check .scratch/tf-plugin-cache
	@git ls-files --cached --others --exclude-standard -z -- terraform | xargs -0 cp --parents -t .scratch/tf-check
	@export TF_PLUGIN_CACHE_DIR="$(CURDIR)/.scratch/tf-plugin-cache" TF_IN_AUTOMATION=1 CHECKPOINT_DISABLE=1; \
	for d in $$(find .scratch/tf-check/terraform -name '*.tf' -printf '%h\n' | sort -u); do \
	  echo "== $$d"; \
	  $(or $(TERRAFORM),terraform) -chdir="$$d" init -backend=false -input=false >/dev/null || exit 1; \
	  $(or $(TERRAFORM),terraform) -chdir="$$d" validate || exit 1; \
	  if [ -d "$$d/tests" ]; then $(or $(TERRAFORM),terraform) -chdir="$$d" test || exit 1; fi; \
	done

# --- Frontend (issue #27) ----------------------------------------------------

frontend-install: ## Install the frontend packages from frontend/bun.lock; fails if the lockfile would change
	cd frontend && bun install --frozen-lockfile

frontend-build: ## Build the frontend to static files in frontend/dist (mock off) and check the output
	cd frontend && VITE_USE_MOCK=false bun run build
	@test -f frontend/dist/index.html || { echo "frontend-build: frontend/dist/index.html is missing"; exit 1; }
	@if [ -e frontend/.output ] || [ -e frontend/.wrangler ] || [ -n "$$(find frontend/dist \( -name server -o -name wrangler.json -o -name nitro.json -o -name '_worker.js' -o -name '*.mjs' \) -print -quit)" ]; then echo "frontend-build: server, worker or Nitro output found (a stale frontend/.output or frontend/.wrangler counts: remove it)"; exit 1; fi
	@if grep -rIlE 'analyst-a-pass|analyst-b-pass|lead-pass|<script>alert\(' frontend/dist; then echo "frontend-build: a demo credential or hostile fixture is in the production build"; exit 1; fi
	@if grep -rIlE 'fonts\.googleapis\.com|fonts\.gstatic\.com' frontend/dist; then echo "frontend-build: the build still mentions a Google fonts host"; exit 1; fi
	@echo "frontend-build: frontend/dist has index.html, no server output, no demo data, no Google fonts host"

frontend-test: ## Run the frontend tests (Vitest); run make frontend-install first
	@test -x frontend/node_modules/.bin/vitest || { echo "frontend-test: frontend/node_modules/.bin/vitest is missing; run make frontend-install first"; exit 1; }
	cd frontend && bun run test

frontend-lint: ## Run the frontend lint (ESLint with the Prettier check); run make frontend-install first
	@test -x frontend/node_modules/.bin/eslint || { echo "frontend-lint: frontend/node_modules/.bin/eslint is missing; run make frontend-install first"; exit 1; }
	cd frontend && bun run lint

frontend-format: ## Rewrite the frontend files with Prettier (prettier --write .); run make frontend-install first
	@test -x frontend/node_modules/.bin/prettier || { echo "frontend-format: frontend/node_modules/.bin/prettier is missing; run make frontend-install first"; exit 1; }
	cd frontend && bun run format

frontend-start: ## Start the frontend dev server in the background (mock on; log: .scratch/frontend.log; http://127.0.0.1:5173/)
	@mkdir -p .scratch
	@test -x frontend/node_modules/.bin/vite || { echo "frontend-start: frontend/node_modules/.bin/vite is missing; run make frontend-install first"; exit 1; }
	@if [ -f .scratch/frontend.pid ]; then pid=$$(cat .scratch/frontend.pid); case "$$pid" in ''|*[!0-9]*|0*) echo "frontend-start: .scratch/frontend.pid does not hold a plain pid; check it and remove it by hand"; exit 1;; esac; if kill -0 "$$pid" 2>/dev/null; then echo "frontend is already running (pid $$pid)"; exit 1; fi; fi
	@nohup sh -c 'cd frontend && exec node_modules/.bin/vite dev --strictPort' > .scratch/frontend.log 2>&1 & echo $$! > .scratch/frontend.pid
	@sleep 1; pid=$$(cat .scratch/frontend.pid); if ! kill -0 "$$pid" 2>/dev/null || grep -q '^State:[[:space:]]*Z' "/proc/$$pid/status" 2>/dev/null; then echo "frontend-start: the server exited at once; last lines of .scratch/frontend.log:"; tail -n 20 .scratch/frontend.log; rm -f .scratch/frontend.pid; exit 1; fi; echo "frontend started (pid $$pid); log: .scratch/frontend.log"

frontend-stop: ## Stop the dev server started by frontend-start
	@if [ ! -f .scratch/frontend.pid ]; then echo "frontend is not running"; exit 0; fi; \
	pid=$$(cat .scratch/frontend.pid); \
	case "$$pid" in ''|*[!0-9]*|0*) echo "frontend-stop: .scratch/frontend.pid does not hold a plain pid; nothing killed; check the file"; exit 1;; esac; \
	if ! kill -0 "$$pid" 2>/dev/null; then rm -f .scratch/frontend.pid; echo "frontend was not running (stale pid file removed)"; exit 0; fi; \
	if [ -r "/proc/$$pid/cmdline" ]; then cmd=$$(tr '\0' ' ' < "/proc/$$pid/cmdline"); elif command -v ps >/dev/null 2>&1; then cmd=$$(ps -o command= -p "$$pid"); else cmd=; fi; \
	case "$$cmd" in *node_modules/.bin/vite\ dev*) ;; *) echo "frontend-stop: pid $$pid does not look like the dev server (its command line is not the one frontend-start runs, or it cannot be read); nothing killed; stop it by hand if it is yours"; exit 1;; esac; \
	kill "$$pid" 2>/dev/null; \
	for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$$pid" 2>/dev/null || break; sleep 1; done; \
	if kill -0 "$$pid" 2>/dev/null; then echo "frontend (pid $$pid) did not stop within 10 s; not forced; pid file kept"; exit 1; fi; \
	rm -f .scratch/frontend.pid; echo "frontend stopped"

# --- Backend (issue #10) -----------------------------------------------------

backend-run: ## Start the backend in the background on localhost (SOCBOARD_PORT, default 8000; log: .scratch/backend.log)
	@mkdir -p .scratch
	@test -x .venv/bin/python || { echo "backend-run: .venv/bin/python is missing; run make install first"; exit 1; }
	@if [ -f .scratch/backend.pid ]; then pid=$$(cat .scratch/backend.pid); case "$$pid" in ''|*[!0-9]*|0*) echo "backend-run: .scratch/backend.pid does not hold a plain pid; check it and remove it by hand"; exit 1;; esac; if kill -0 "$$pid" 2>/dev/null; then echo "backend is already running (pid $$pid)"; exit 1; fi; fi
	@.venv/bin/python scripts/backend_probe.py port; rc=$$?; if [ "$$rc" != 0 ] && [ "$$rc" != 3 ]; then exit 1; fi
	@if [ -n "$${SOCBOARD_MODE+x}" ]; then echo "backend-run: SOCBOARD_MODE is ignored for this development run"; fi
	@nohup sh -c 'exec env -u SOCBOARD_MODE .venv/bin/python -m socboard.server' > .scratch/backend.log 2>&1 & echo $$! > .scratch/backend.pid
	@pid=$$(cat .scratch/backend.pid); \
	alive() { kill -0 "$$pid" 2>/dev/null && ! grep -q '^State:[[:space:]]*Z' "/proc/$$pid/status" 2>/dev/null; }; \
	end=$$(( $$(date +%s) + 30 )); \
	while [ "$$(date +%s)" -lt "$$end" ]; do \
		if ! alive; then echo "backend-run: the server exited before it answered /api/health; last lines of .scratch/backend.log:"; tail -n 20 .scratch/backend.log; rm -f .scratch/backend.pid; exit 1; fi; \
		if .venv/bin/python scripts/backend_probe.py health && alive; then echo "backend started (pid $$pid); log: .scratch/backend.log"; exit 0; fi; \
		sleep 1; \
	done; \
	echo "backend-run: no healthy answer from /api/health within 30 s; last lines of .scratch/backend.log:"; tail -n 20 .scratch/backend.log; \
	kill "$$pid" 2>/dev/null; \
	for i in 1 2 3 4 5 6 7 8 9 10; do alive || break; sleep 1; done; \
	if alive; then echo "backend (pid $$pid) did not stop within 10 s; not forced; pid file kept"; exit 1; fi; \
	rm -f .scratch/backend.pid; exit 1

backend-stop: ## Stop the backend started by backend-run
	@if [ ! -f .scratch/backend.pid ]; then echo "backend is not running"; exit 0; fi; \
	pid=$$(cat .scratch/backend.pid); \
	case "$$pid" in ''|*[!0-9]*|0*) echo "backend-stop: .scratch/backend.pid does not hold a plain pid; nothing killed; check the file"; exit 1;; esac; \
	if ! kill -0 "$$pid" 2>/dev/null && [ ! -d "/proc/$$pid" ]; then rm -f .scratch/backend.pid; echo "backend was not running (stale pid file removed)"; exit 0; fi; \
	if [ -r "/proc/$$pid/cmdline" ]; then cmd=$$(tr '\0' ' ' < "/proc/$$pid/cmdline"); elif command -v ps >/dev/null 2>&1; then cmd=$$(ps -o command= -p "$$pid"); else cmd=; fi; \
	case "$$cmd" in *-m\ socboard.server*) ;; *) echo "backend-stop: pid $$pid does not look like the backend (its command line is not the one backend-run starts, or it cannot be read); nothing killed; stop it by hand if it is yours"; exit 1;; esac; \
	root=$$(readlink -f . 2>/dev/null); raw=$$(readlink "/proc/$$pid/cwd" 2>/dev/null); cwd=$$(readlink -f "/proc/$$pid/cwd" 2>/dev/null); \
	if [ -z "$$root" ] || [ -z "$$raw" ] || [ -z "$$cwd" ]; then echo "backend-stop: the working directory of pid $$pid could not be read (/proc/$$pid/cwd); nothing killed; stop it by hand if it is yours"; exit 1; fi; \
	if [ "$$cwd" != "$$root" ]; then echo "backend-stop: the working directory of pid $$pid is not this checkout; nothing killed; pid file kept; stop it by hand if it is yours"; exit 1; fi; \
	kill "$$pid" 2>/dev/null; \
	for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$$pid" 2>/dev/null || break; sleep 1; done; \
	if kill -0 "$$pid" 2>/dev/null; then echo "backend (pid $$pid) did not stop within 10 s; not forced; pid file kept"; exit 1; fi; \
	rm -f .scratch/backend.pid; echo "backend stopped"

# --- Database (issue #11) ----------------------------------------------------

migration-name-chars := a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 _ -
migration-name-ok = $(and $(filter 1,$(words $(1))),$(if $(call kit-other-strip,$(1),$(migration-name-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok))

migrate: ## Apply all database migrations to SOCBOARD_DATABASE_URL (default: socboard.db in the repository root)
	uv run --locked python -m socboard.migrate

seed: ## Load the synthetic assets and the users analyst-a, analyst-b and lead into SOCBOARD_DATABASE_URL (run make migrate first; needs SOCBOARD_SEED_PASSWORD_ANALYST_A, SOCBOARD_SEED_PASSWORD_ANALYST_B and SOCBOARD_SEED_PASSWORD_LEAD on every run; a second run changes nothing)
	uv run --locked python -m socboard.seed

set-password: ## Set a new password for one existing user: make set-password ACCOUNT=<username> (run make migrate first; reads SOCBOARD_NEW_PASSWORD, at least 12 characters, from the environment, never from the command line; the old password stops working)
	$(if $(findstring $$,$(value ACCOUNT)),$(error Usage: make set-password ACCOUNT=<username> - ACCOUNT must not contain $$))
	$(if $(call migration-name-ok,$(value ACCOUNT)),,$(error Usage: make set-password ACCOUNT=<username> - one word of letters, digits, _ and - only))
	uv run --locked python -m socboard.set_password "$$ACCOUNT"

migration-new: ## Create a migration file from the model changes: make migration-new NAME=<letters, digits, _ and ->
	$(if $(findstring $$,$(value NAME)),$(error Usage: make migration-new NAME=<words> - NAME must not contain $$))
	$(if $(call migration-name-ok,$(value NAME)),,$(error Usage: make migration-new NAME=<words> - one word of letters, digits, _ and - only))
	uv run --locked python -m socboard.migrate new "$$NAME"

smoke-url-chars := $(migration-name-chars) : / . [ ]
smoke-url-ok = $(and $(filter 1,$(words $(1))),$(if $(call kit-other-strip,$(1),$(smoke-url-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok))

smoke: ## Check a running app (issue #191): make smoke URL=<url> [HEALTH_ONLY=1]; the full check needs SOCBOARD_SEED_PASSWORD_LEAD and SOCBOARD_INGEST_API_KEY and adds one New case; HEALTH_ONLY=1 needs no credential
	$(if $(findstring $$,$(value URL)),$(error Usage: make smoke URL=<url> [HEALTH_ONLY=1] - URL must not contain $$))
	$(if $(call smoke-url-ok,$(value URL)),,$(error Usage: make smoke URL=<url> [HEALTH_ONLY=1] - URL is one word of letters, digits and : / . - _ [ ] only))
	$(if $(value HEALTH_ONLY),$(if $(subst x1x,,x$(value HEALTH_ONLY)x),$(error Usage: make smoke URL=<url> [HEALTH_ONLY=1] - HEALTH_ONLY is empty or 1)))
	uv run --locked python -m socboard.smoke $(if $(value HEALTH_ONLY),--health-only )-- "$$URL"

# --- Full stack (issue #22) --------------------------------------------------

run: ## Start the whole local stack in the background: migrate, seed, backend, frontend on the real API (needs SOCBOARD_TOKEN_SECRET, SOCBOARD_SEED_PASSWORD_ANALYST_A, SOCBOARD_SEED_PASSWORD_ANALYST_B, SOCBOARD_SEED_PASSWORD_LEAD and SOCBOARD_INGEST_API_KEY; starts nothing if one fails)
	@.venv/bin/python scripts/run_preflight.py
	@for f in .scratch/backend.pid .scratch/frontend.pid; do if [ -f "$$f" ] && kill -0 "$$(cat "$$f")" 2>/dev/null; then echo "run: the stack is already running ($$f names live process $$(cat "$$f")); run make stop first"; exit 1; fi; done
	@SOCBOARD_HOST=127.0.0.1 SOCBOARD_PORT=5173 .venv/bin/python scripts/backend_probe.py port > /dev/null || { echo "run: port 5173 on 127.0.0.1 (the frontend) is already in use; nothing started"; exit 1; }
	@.venv/bin/python scripts/backend_probe.py port
	@$(MAKE) --no-print-directory migrate
	@$(MAKE) --no-print-directory seed
	@$(MAKE) --no-print-directory backend-run
	@if ! VITE_USE_MOCK=false $(MAKE) --no-print-directory frontend-start; then \
		echo "run: the frontend did not start; stopping the backend this run started"; $(MAKE) --no-print-directory backend-stop; exit 1; \
	fi; \
	pid=$$(cat .scratch/frontend.pid); end=$$(( $$(date +%s) + 30 )); \
	until SOCBOARD_HOST=127.0.0.1 SOCBOARD_PORT=5173 .venv/bin/python scripts/backend_probe.py health; do \
		if ! kill -0 "$$pid" 2>/dev/null || grep -q '^State:[[:space:]]*Z' "/proc/$$pid/status" 2>/dev/null || [ "$$(date +%s)" -ge "$$end" ]; then \
			echo "run: the frontend did not answer /api/health on 127.0.0.1:5173 within 30 s (it exited, or its proxy to 127.0.0.1:8000 found no backend); last lines of .scratch/frontend.log:"; tail -n 20 .scratch/frontend.log; \
			$(MAKE) --no-print-directory frontend-stop; $(MAKE) --no-print-directory backend-stop; exit 1; \
		fi; \
		sleep 1; \
	done
	@echo "run: backend  http://127.0.0.1:$${SOCBOARD_PORT:-8000}/ (log: .scratch/backend.log)"
	@echo "run: frontend http://127.0.0.1:5173/ (mock off; its /api proxy goes to 127.0.0.1:8000; log: .scratch/frontend.log)"
	@echo "run: make stop stops both"

stop: ## Stop the stack that make run started (frontend, then backend); refuses a process the stack did not start
	@$(MAKE) --no-print-directory frontend-stop; f=$$?; $(MAKE) --no-print-directory backend-stop || exit 1; exit $$f

# --- Compose stack (issue #221) ----------------------------------------------

compose-up: ## Start Postgres, the app and a local proxy with Docker Compose (needs Docker); the first run makes local secrets in compose.secrets without printing them; waits until the app is healthy
	uv run --locked python scripts/compose_secrets.py
	docker compose --env-file compose.secrets up --build --wait --wait-timeout 300

compose-down: ## Stop the Compose stack: containers and network are removed, the Postgres data is kept
	docker compose --env-file compose.secrets down

# --- Observability stack (issue #293) ----------------------------------------

observability-up: ## Start the app stack with the observability layer (collector, Tempo, Loki, Prometheus, Alertmanager, Grafana) with Docker Compose (needs Docker); the first run makes Grafana's admin password in observability.secrets without printing it; waits until the app and Grafana are healthy
	uv run --locked python scripts/observability_up.py up

observability-down: ## Stop the observability stack: containers and network are removed, the volumes are kept
	uv run --locked python scripts/observability_up.py down