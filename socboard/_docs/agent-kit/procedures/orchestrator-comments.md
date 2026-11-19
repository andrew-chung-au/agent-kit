# Orchestrator comments

Layouts for the four comments the orchestrator writes on an issue. Copy one, keep the fixed lines, fill the per-issue facts (marked **fact**).

Rules: start with `Orchestrator:`. Post with `make issue-comment N=<n> FILE=.scratch/<name>.md`, never a raw `gh` write (target in `templates/Makefile.github.mk`). Name no env file; the scanner refuses it.

## Claim

Fixed: the body hash with its re-check (`make issue-hash N=<n>`, `Body sha256:` against `Recorded sha256:`); the "live scripts" warning when the issue touches `scripts/` or hooks; cloud `gh` limits; REST fallback for reads; writes still use `make issue-comment`; "do not close or merge"; the return path.
**Fact:** issue, branch, hash, expected paths, protected files needing approval, and the environment the next role will run in with its missing tools (for example no bun, so the tests step of `make verify` cannot run).
Before claiming, check that no decision record approved after the PM's grooming comment contradicts a criterion; if one does, stop and ask the human.
Never name an env file in a claim.

## Release

Fixed: the claim is released; nothing is merged or closed.
**Fact:** why, the branch and commit left behind, what is unfinished.

## Confirm

Fixed: the human confirmed the new body in this session; the hash re-check ran; the PM must record the hash in a `PM:` comment.
**Fact:** the new hash, the old hash, what changed.

## Close

Fixed: who built it, what moved or was not done, what is not verified, and these lines, each alone and worded exactly, because `make issue-close` matches them: `QA PASS commit: <7 to 40 hex>` (named in the latest `QA:` PASS; not for Light), `Merge commit: <7 to 40 hex>`, `Verify: <text>`, `Summary: <path>`, and for Light `Human approved diff: yes`.
**Fact:** every value in those lines.
Never close without QA PASS. Post after the last PASS (Light: after `tier-check: PASS`), then `make issue-close N=<n>`. Close as not planned only after the human approved that closure: `Orchestrator: Close as not planned` with `Human approved closure: <YYYY-MM-DD>` and `Backlog review: <path or comment URL>`, then add `REASON=not-planned`.
