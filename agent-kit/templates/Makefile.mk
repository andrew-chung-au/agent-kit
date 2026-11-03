# Agent kit Makefile blueprint. Setup merges these targets into the project's
# Makefile: add what's missing, never replace existing targets. Recipe lines
# must start with a TAB. See blueprints.md for when each target applies.

# --- Always (added at setup) ---------------------------------------------

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

# --- When the project's tasks are GitHub issues --------------------------------

# Rule for every target that takes a variable: validate it with make functions
# before it is used. `make *` is allowed without approval and make pastes
# variables into shell commands unquoted, so an unchecked variable is an
# injection point. Free text never goes in a variable (pass a path under
# .scratch/). issue-dump is the worked example: $(subst) strips the allowed
# characters and $(error) refuses what is left. Checks read $(value X), which make
# does not expand, and refuse a $ in the value; recipes pass "$$X", the shell
# variable, never $(X). Nothing in the tool settings can
# check a project's own targets; the Engineer and QA read new ones against this rule.

issue-number-ok = $(and $(filter 1,$(words $(1))),$(if $(subst 0,,$(subst 1,,$(subst 2,,$(subst 3,,$(subst 4,,$(subst 5,,$(subst 6,,$(subst 7,,$(subst 8,,$(subst 9,,$(1))))))))))),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(filter 0%,$(1)),,ok),$(if $(word 10,$(subst 0,x ,$(subst 1,x ,$(subst 2,x ,$(subst 3,x ,$(subst 4,x ,$(subst 5,x ,$(subst 6,x ,$(subst 7,x ,$(subst 8,x ,$(subst 9,x ,$(1)))))))))))),,ok))

issue-hash: ## Print an issue body's sha256, author and owner check: make issue-hash N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-hash N=<issue number>))
	@python3 -B _docs/agent-kit/scripts/issue-hash.py "$$N"

issue-dump: ## Write an issue as JSON to .scratch/issue-<N>.json: make issue-dump N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-dump N=<issue number>))
	@mkdir -p .scratch
	@if gh issue view "$(N)" --json number,title,body,state,labels,author,comments > ".scratch/issue-$(N).json.tmp" 2>/dev/null && python3 -B -m json.tool ".scratch/issue-$(N).json.tmp" > /dev/null 2>&1; then mv ".scratch/issue-$(N).json.tmp" ".scratch/issue-$(N).json" && echo ".scratch/issue-$(N).json"; else rm -f ".scratch/issue-$(N).json.tmp"; echo "issue-dump: gh could not return valid JSON for issue $(N)" >&2; exit 1; fi

sweep-due: ## Say whether a sweep is due (read-only; the sweep interval is set in the script)
	@python3 -B _docs/agent-kit/scripts/sweep-due.py

tier-check: ## Check a change against its tier's path limit: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]
	$(if $(and $(filter 1,$(words $(value TIER))),$(filter light standard heavy,$(value TIER))),,$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]))
	$(if $(findstring $$,$(value BASE)),$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>] - BASE must not contain $$))
	@bash _docs/agent-kit/scripts/check-tier.sh "$$TIER" "$$BASE"

# --- When the stack is known (wrap the project's own commands) -------------

install: ## Install dependencies
	<the project's install command(s)>

test: ## Run all unit tests
	<the project's test command(s)>

# --- Only when the project has the capability --------------------------------

run: ## Run the project in the foreground (for humans; agents use <name>-start)
	<the project's run command>

test-one: ## Run one test file: make test-one FILE=path
	$(if $(findstring $$,$(value FILE)),$(error Usage: make test-one FILE=path/to/test_file - FILE must not contain $$))
	@test -n "$$FILE" || { echo "Usage: make test-one FILE=path/to/test_file"; exit 1; }
	<the project's single-file test command> "$$FILE"

e2e: ## Run end-to-end tests
	<the project's e2e command, including any stack start and teardown>

migration: ## Create a database migration: make migration MSG="what changed"
	$(if $(findstring $$,$(value MSG)),$(error Usage: make migration MSG="what changed" - MSG must not contain $$))
	@test -n "$$MSG" || { echo 'Usage: make migration MSG="what changed"'; exit 1; }
	<the project's migration command> "$$MSG"

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

# --- Project targets (this project's own; add below) -------------------------
