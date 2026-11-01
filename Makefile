# Agent kit development repo. Core targets from agent-kit/templates/Makefile.mk,
# with the kit at agent-kit/ instead of _docs/agent-kit/.

help: ## List targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_ -]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

verify: ## Run the verification gate: make verify [BASE=<commit>]
	@bash agent-kit/scripts/verify.sh $(BASE)

assert-clean: ## Fail if this folder has uncommitted changes (used after QA)
	@bash agent-kit/scripts/assert-clean.sh

hooks: ## Install the repo's git hooks (where agents commit; never in a clean clone)
	@bash agent-kit/scripts/install-hooks.sh

clean-scratch: ## Empty .scratch/ at the end of an issue (refuses while a started process is running)
	@for f in .scratch/*.pid; do if [ -f "$$f" ] && kill -0 "$$(cat "$$f")" 2>/dev/null; then echo "$$f: process $$(cat "$$f") is still running; stop it first"; exit 1; fi; done
	@mkdir -p .scratch && find .scratch -mindepth 1 -delete && echo ".scratch/ is now empty"

issue-hash: ## Print an issue body's sha256, author and owner check: make issue-hash N=<issue number>
	$(if $(and $(filter 1,$(words $(N))),$(if $(strip $(subst 0,,$(subst 1,,$(subst 2,,$(subst 3,,$(subst 4,,$(subst 5,,$(subst 6,,$(subst 7,,$(subst 8,,$(subst 9,,$(N)))))))))))),,x)),,$(error Usage: make issue-hash N=<issue number>))
	@python3 -B agent-kit/scripts/issue-hash.py "$(N)"

sweep-due: ## Say whether a sweep is due (read-only; the sweep interval is set in the script)
	@python3 -B agent-kit/scripts/sweep-due.py

tier-check: ## Check a change against its tier's path limit: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]
	$(if $(and $(filter 1,$(words $(TIER))),$(filter light standard heavy,$(TIER))),,$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]))
	@bash agent-kit/scripts/check-tier.sh "$(TIER)" "$(BASE)"

test: ## Syntax checks, the kit's claims check, and the unit tests in tests/
	@for f in agent-kit/scripts/*.sh agent-kit/githooks/* agent-kit/environments/local-sandbox/setup.sh agent-kit/environments/local-sandbox/pre-push; do bash -n "$$f" || exit 1; done; echo "shell: OK"
	@python3 -B -c 'import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]' agent-kit/claude-code/hooks/*.py agent-kit/scripts/*.py tests/*.py && echo "python: OK"
	@for f in agent-kit/claude-code/settings.json agent-kit/opencode/opencode.json agent-kit/environments/local-sandbox/devcontainer.json; do python3 -m json.tool "$$f" > /dev/null || exit 1; done; echo "json: OK"
	@python3 -B agent-kit/scripts/check-claims.py
	@python3 -B -m unittest discover tests
