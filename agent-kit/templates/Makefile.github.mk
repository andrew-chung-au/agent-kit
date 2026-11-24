# Agent kit GitHub module, part 1: file an issue, post a comment and open a draft
# pull request through
# wrappers that check every input first. Setup merges these targets into the
# project's Makefile when the project's tasks are GitHub issues and the human
# wants agents to file and comment through the wrappers (see blueprints.md).
# Recipe lines must start with a TAB.
#
# Needs `issue-number-ok` and `issue-file-ok` (FILE: one word, letters digits . _ / -
# only, under .scratch/, no "..") from templates/Makefile.mk (GitHub-issues section).
# Follows the validation rule stated there: each variable is checked with make
# functions before it is used, through $(value ...) so that make never expands
# the text it is checking. The scripts check again.
#
# The issue-create and issue-comment wrappers can do two things to GitHub: create
# one issue, and post one comment. They add no label, assignee, project or
# milestone, and edit, close or delete nothing. They refuse text that looks like
# a secret (scripts/secret-patterns.txt). Only issue-close can close, one issue,
# after checking the issue's recorded history; nothing here edits an issue.

issue-create: ## File one issue from a file under .scratch/ (first line Title: <text>, blank line, body): make issue-create FILE=.scratch/<name>.md
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make issue-create FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash _docs/agent-kit/scripts/issue-create.sh "$(FILE)"

issue-comment: ## Post a file under .scratch/ as one comment (first line PM: Engineer: QA: or Orchestrator:): make issue-comment N=<issue number> FILE=.scratch/<name>.md
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-comment N=<issue number> FILE=.scratch/<name>.md))
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make issue-comment N=<issue number> FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash _docs/agent-kit/scripts/issue-comment.sh "$(N)" "$(FILE)"

# REASON: empty, or exactly one word that is completed or not-planned, with no stray
# whitespace. Checked through $(value ...) and passed to the script as "$$REASON" from the
# environment, so make never expands its text and the shell never sees it unquoted.
issue-reason-ok = $(and $(filter 1,$(words $(1))),$(filter completed not-planned,$(1)),$(if $(filter-out completed not-planned,$(1)),,ok),$(if $(subst x$(strip $(1))x,,x$(1)x),,ok))

issue-close: ## Close one issue when its recorded history shows the process was followed (the orchestrator only): make issue-close N=<issue number> [REASON=not-planned]
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make issue-close N=<issue number> [REASON=not-planned]))
	$(if $(value REASON),$(if $(call issue-reason-ok,$(value REASON)),,$(error Usage: make issue-close N=<issue number> [REASON=completed|not-planned])))
	@bash _docs/agent-kit/scripts/issue-close.sh "$(N)" $(if $(value REASON),"$$REASON")

# pr-open opens one draft pull request from the current, pushed branch to the default
# branch, and nothing else: it refuses a closing keyword, a body without `Refs #<N>`, a
# secret, the default branch, a detached HEAD and an unpushed branch. It never readies,
# merges or closes (process.md, Commits and pushes).
pr-open: ## Open a draft pull request from the pushed session branch (FILE: first line Title: <text>, blank line, body with Refs #N): make pr-open N=<issue number> FILE=.scratch/<name>.md
	$(if $(call issue-number-ok,$(value N)),,$(error Usage: make pr-open N=<issue number> FILE=.scratch/<name>.md))
	$(if $(call issue-file-ok,$(value FILE)),,$(error Usage: make pr-open N=<issue number> FILE=.scratch/<name>.md - one word under .scratch/ with letters digits . _ / - only))
	@bash _docs/agent-kit/scripts/pr-open.sh "$(N)" "$(FILE)"
