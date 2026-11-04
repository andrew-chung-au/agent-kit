# Agent kit development repo. Core targets from agent-kit/templates/Makefile.mk,
# with the kit at agent-kit/ instead of _docs/agent-kit/.

help: ## List targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_ -]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

verify: ## Run the verification gate: make verify [BASE=<commit>]
	$(if $(findstring $$,$(value BASE)),$(error Usage: make verify [BASE=<commit>] - BASE must not contain $$))
	@bash agent-kit/scripts/verify.sh "$$BASE"

assert-clean: ## Fail if this folder has uncommitted changes (used after QA)
	@bash agent-kit/scripts/assert-clean.sh

hooks: ## Install the repo's git hooks (where agents commit; never in a clean clone)
	@bash agent-kit/scripts/install-hooks.sh

clean-scratch: ## Empty .scratch/ at the end of an issue (refuses while a started process is running)
	@for f in .scratch/*.pid; do if [ -f "$$f" ] && kill -0 "$$(cat "$$f")" 2>/dev/null; then echo "$$f: process $$(cat "$$f") is still running; stop it first"; exit 1; fi; done
	@mkdir -p .scratch && find .scratch -mindepth 1 -delete && echo ".scratch/ is now empty"

issue-number-ok = $(and $(filter 1,$(words $(1))),$(if $(subst 0,,$(subst 1,,$(subst 2,,$(subst 3,,$(subst 4,,$(subst 5,,$(subst 6,,$(subst 7,,$(subst 8,,$(subst 9,,$(1))))))))))),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(filter 0%,$(1)),,ok),$(if $(word 10,$(subst 0,x ,$(subst 1,x ,$(subst 2,x ,$(subst 3,x ,$(subst 4,x ,$(subst 5,x ,$(subst 6,x ,$(subst 7,x ,$(subst 8,x ,$(subst 9,x ,$(1)))))))))))),,ok))

issue-hash: ## Print an issue body's sha256, author and owner check: make issue-hash N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-hash N=<issue number>))
	@python3 -B agent-kit/scripts/issue-hash.py "$$N"

issue-dump: ## Write an issue as JSON to .scratch/issue-<N>.json: make issue-dump N=<issue number>
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-dump N=<issue number>))
	@mkdir -p .scratch
	@if gh issue view "$(N)" --json number,title,body,state,labels,author,comments > ".scratch/issue-$(N).json.tmp" 2>/dev/null && python3 -B -m json.tool ".scratch/issue-$(N).json.tmp" > /dev/null 2>&1; then mv ".scratch/issue-$(N).json.tmp" ".scratch/issue-$(N).json" && echo ".scratch/issue-$(N).json"; else rm -f ".scratch/issue-$(N).json.tmp"; echo "issue-dump: gh could not return valid JSON for issue $(N)" >&2; exit 1; fi

issue-file-chars := a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 . _ / -
issue-strip-chars = $(if $(2),$(call issue-strip-chars,$(subst $(firstword $(2)),,$(1)),$(wordlist 2,$(words $(2)),$(2))),$(1))
issue-file-ok = $(and $(filter 1,$(words $(1))),$(if $(call issue-strip-chars,$(1),$(issue-file-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(filter .scratch/%,$(1)),$(if $(findstring ..,$(1)),,ok))

issue-create: ## File one issue from a file under .scratch/ (first line Title: <text>, blank line, body): make issue-create FILE=.scratch/<name>.md
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make issue-create FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash agent-kit/scripts/issue-create.sh "$(FILE)"

issue-comment: ## Post a file under .scratch/ as one comment (first line PM: Engineer: QA: or Orchestrator:): make issue-comment N=<issue number> FILE=.scratch/<name>.md
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-comment N=<issue number> FILE=.scratch/<name>.md))
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make issue-comment N=<issue number> FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash agent-kit/scripts/issue-comment.sh "$(N)" "$(FILE)"

# REASON: empty, or exactly one word that is completed or not-planned, with no stray
# whitespace. Checked through $(value ...) and passed to the script as "$$REASON" from the
# environment, so make never expands its text and the shell never sees it unquoted.
issue-reason-ok = $(and $(filter 1,$(words $(1))),$(filter completed not-planned,$(1)),$(if $(filter-out completed not-planned,$(1)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok))

issue-close: ## Close one issue when its recorded history shows the process was followed (the orchestrator only): make issue-close N=<issue number> [REASON=not-planned]
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-close N=<issue number> [REASON=not-planned]))
	$(if $(value REASON),$(if $(call issue-reason-ok,$(value REASON)),,$(error Usage: make issue-close N=<issue number> [REASON=completed|not-planned])))
	@bash agent-kit/scripts/issue-close.sh "$(N)" $(if $(value REASON),"$$REASON")

sweep-due: ## Say whether a sweep is due (read-only; the sweep interval is set in the script)
	@python3 -B agent-kit/scripts/sweep-due.py

tier-check: ## Check a change against its tier's path limit: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]
	$(if $(and $(filter 1,$(words $(value TIER))),$(filter light standard heavy,$(value TIER))),,$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>]))
	$(if $(findstring $$,$(value BASE)),$(error Usage: make tier-check TIER=<light|standard|heavy> [BASE=<commit>] - BASE must not contain $$))
	@bash agent-kit/scripts/check-tier.sh "$$TIER" "$$BASE"

kit-check: ## Say whether the kit folder is pristine or a derivative of KIT_VERSION (read-only)
	@python3 -B agent-kit/scripts/kit-check.py

kit-other-chars := a b c d e f g h i j k l m n o p q r s t u v w x y z A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 0 1 2 3 4 5 6 7 8 9 . _ / -
kit-other-strip = $(if $(2),$(call kit-other-strip,$(subst $(firstword $(2)),,$(1)),$(wordlist 2,$(words $(2)),$(2))),$(1))
kit-other-ok = $(and $(filter 1,$(words $(1))),$(if $(call kit-other-strip,$(1),$(kit-other-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(filter .scratch/%,$(1)),$(if $(findstring ..,$(1)),,ok))

kit-compare: ## List how the kit folder differs from another kit copy under .scratch/ (read-only): make kit-compare OTHER=.scratch/<folder>
	$(if $(call kit-other-ok,$(value OTHER)),,$(error Usage: make kit-compare OTHER=.scratch/<folder> - one word under .scratch/ with letters digits . _ / - only))
	@python3 -B agent-kit/scripts/kit-compare.py "$$OTHER"

kit-path-ok = $(and $(filter 1,$(words $(1))),$(if $(call kit-other-strip,$(1),$(kit-other-chars)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(findstring ..,$(1)),,ok))

kit-feedback: ## Write a read-only feedback bundle under .scratch/ from a project's kit (reverse import): make kit-feedback PROJECT=<project root> KIT=<reference kit>
	$(if $(call kit-path-ok,$(value PROJECT)),,$(error Usage: make kit-feedback PROJECT=<project root> KIT=<reference kit> - PROJECT: one word, letters digits . _ / - only, no ..))
	$(if $(call kit-path-ok,$(value KIT)),,$(error Usage: make kit-feedback PROJECT=<project root> KIT=<reference kit> - KIT: one word, letters digits . _ / - only, no ..))
	@python3 -B agent-kit/scripts/kit-feedback.py "$$PROJECT" "$$KIT"

dup-report: ## Report repeated sentences and decision keys with differing status in the docs (read-only; never a gate)
	@python3 -B agent-kit/scripts/dup-report.py --exclude .scratch/ --exclude _session-summaries/ --exclude _docs/records/ --exclude vuln-triage/ --exclude proposals/ .

permission-days-ok = $(and $(filter 1,$(words $(1))),$(if $(subst 0,,$(subst 1,,$(subst 2,,$(subst 3,,$(subst 4,,$(subst 5,,$(subst 6,,$(subst 7,,$(subst 8,,$(subst 9,,$(1))))))))))),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok),$(if $(filter 0%,$(1)),,ok),$(if $(word 5,$(subst 0,x ,$(subst 1,x ,$(subst 2,x ,$(subst 3,x ,$(subst 4,x ,$(subst 5,x ,$(subst 6,x ,$(subst 7,x ,$(subst 8,x ,$(subst 9,x ,$(1)))))))))))),,ok))

permission-report: ## Summarise the permission logs of all tools: make permission-report [SINCE=<YYYY-MM-DD or YYYY-MM-DDTHH:MMZ>]
	$(if $(findstring $$,$(value SINCE)),$(error Usage: make permission-report [SINCE=<YYYY-MM-DD or YYYY-MM-DDTHH:MMZ>] - SINCE must not contain $$))
	@python3 -B agent-kit/scripts/permission-report.py "$$SINCE"

permission-logs-prune: ## Delete permission logs older than DAYS days (the human runs it): make permission-logs-prune DAYS=<1 to 3650>
	$(if $(call permission-days-ok,$(value DAYS)),,$(error Usage: make permission-logs-prune DAYS=<1 to 3650>))
	@python3 -B agent-kit/scripts/permission-logs-prune.py "$$DAYS"

test: ## Syntax checks, the kit's claims check, and the unit tests in tests/
	@for f in agent-kit/scripts/*.sh agent-kit/githooks/* agent-kit/environments/local-sandbox/setup.sh agent-kit/environments/local-sandbox/pre-push; do bash -n "$$f" || exit 1; done; echo "shell: OK"
	@python3 -B -c 'import ast, sys; [ast.parse(open(f).read(), f) for f in sys.argv[1:]]' agent-kit/claude-code/hooks/*.py agent-kit/scripts/*.py tests/*.py && echo "python: OK"
	@for f in agent-kit/claude-code/settings.json agent-kit/opencode/opencode.json agent-kit/environments/local-sandbox/devcontainer.json agent-kit/environments/local-sandbox/compose/devcontainer.json; do python3 -m json.tool "$$f" > /dev/null || exit 1; done; echo "json: OK"
	@python3 -B agent-kit/scripts/check-claims.py
	@python3 -B -m unittest discover tests
