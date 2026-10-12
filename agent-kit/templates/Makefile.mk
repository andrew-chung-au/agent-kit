# Agent kit Makefile blueprint. Setup merges these targets into the project's
# Makefile: add what's missing, never replace existing targets. Recipe lines
# must start with a TAB. See blueprints.md for when each target applies.

# --- Always (added at setup) ---------------------------------------------

help: ## List targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_ -]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

verify: ## Run the verification gate: make verify [BASE=<commit>]
	@bash _docs/agent-kit/scripts/verify.sh $(BASE)

assert-clean: ## Fail if this folder has uncommitted changes (used after QA)
	@bash _docs/agent-kit/scripts/assert-clean.sh

hooks: ## Install the repo's git hooks (where agents commit; never in a clean clone)
	@bash _docs/agent-kit/scripts/install-hooks.sh

clean-scratch: ## Empty .scratch/ at the end of an issue (refuses while a started process is running)
	@for f in .scratch/*.pid; do if [ -f "$$f" ] && kill -0 "$$(cat "$$f")" 2>/dev/null; then echo "$$f: process $$(cat "$$f") is still running; stop it first"; exit 1; fi; done
	@mkdir -p .scratch && find .scratch -mindepth 1 -delete && echo ".scratch/ is now empty"

# --- When the stack is known (wrap the project's own commands) -------------

install: ## Install dependencies
	<the project's install command(s)>

test: ## Run all unit tests
	<the project's test command(s)>

# --- Only when the project has the capability --------------------------------

test-one: ## Run one test file: make test-one FILE=path
	@test -n "$(FILE)" || { echo "Usage: make test-one FILE=path/to/test_file"; exit 1; }
	<the project's single-file test command> "$(FILE)"

e2e: ## Run end-to-end tests
	<the project's e2e command, including any stack start and teardown>

migration: ## Create a database migration: make migration MSG="what changed"
	@test -n "$(MSG)" || { echo 'Usage: make migration MSG="what changed"'; exit 1; }
	<the project's migration command> "$(MSG)"

lint: ## Run the linter
	<the project's lint command>

typecheck: ## Run the type checker
	<the project's type-check command>

# --- Background services: one pair per long-running process -----------------
# Replace <name> and <command>. <command> runs the process in the foreground,
# and the process should exit cleanly on SIGTERM. If <command> is a wrapper
# (for example `uv run`), check that it passes SIGTERM on to the process.

<name>-start: ## Start <name> in the background (log: .scratch/<name>.log)
	@mkdir -p .scratch
	@if [ -f .scratch/<name>.pid ] && kill -0 "$$(cat .scratch/<name>.pid)" 2>/dev/null; then echo "<name> is already running (pid $$(cat .scratch/<name>.pid))"; exit 1; fi
	@nohup <command> > .scratch/<name>.log 2>&1 & echo $$! > .scratch/<name>.pid
	@echo "<name> started (pid $$(cat .scratch/<name>.pid)); log: .scratch/<name>.log"

<name>-stop: ## Stop the <name> started by <name>-start
	@if [ ! -f .scratch/<name>.pid ]; then echo "<name> is not running"; exit 0; fi; \
	pid=$$(cat .scratch/<name>.pid); kill "$$pid" 2>/dev/null; \
	for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 "$$pid" 2>/dev/null || break; sleep 1; done; \
	if kill -0 "$$pid" 2>/dev/null; then echo "<name> (pid $$pid) did not stop within 10 s"; exit 1; fi; \
	rm -f .scratch/<name>.pid; echo "<name> stopped"
