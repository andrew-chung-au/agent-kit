# Orchestrator comments

Layouts for the four comments the orchestrator writes on an issue. Copy one, keep the fixed lines, fill the per-issue facts (marked **fact**).

Rules: start with `Orchestrator:`. Post with `make issue-comment N=<n> FILE=.scratch/<name>.md`, never a raw `gh` write (target in `templates/Makefile.github.mk`). Name no env file; the scanner refuses it.

## Claim

Fixed: the body hash with its re-check (`make issue-hash N=<n>`, `Body sha256:` against `Recorded sha256:`); the "live scripts" warning when the issue touches `scripts/` or hooks; cloud `gh` limits and the REST fallback; "do not close or merge"; the return path.
**Fact:** issue, branch, hash, expected paths, protected files needing approval.
Never name an env file in a claim.

## Release

Fixed: the claim is released; nothing is merged or closed.
**Fact:** why, the branch and commit left behind, what is unfinished.

## Confirm

Fixed: the human confirmed the new body in this session; the hash re-check ran; the PM must record the hash in a `PM:` comment.
**Fact:** the new hash, the old hash, what changed.

## Close

Fixed: the QA PASS commit, who built it, the merge commit, the verify result, what moved or was not done, what is not verified, the summary path.
**Fact:** every value in those lines.
Never close without QA PASS. Close as not planned only after the human approved that closure.
