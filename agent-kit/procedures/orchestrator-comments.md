# Orchestrator comments

Layouts for the orchestrator's five issue comments. Copy one, keep the fixed lines, fill the per-issue facts.

Rules: start with `Orchestrator:`. Post with `make issue-comment N=<n> FILE=.scratch/<name>.md`, never a raw `gh` write (target in `templates/Makefile.github.mk`). Name no env file; the scanner refuses it.

Lines scripts read: each is `<Label>: <value>` alone on its line from column 1, the label worded exactly, in an owner comment with the named first line.

## Claim

Fixed: `Approved by: approved label, seen <date>`, naming the body hash the label covers; the body hash with its re-check (`make issue-hash N=<n>`, `Body sha256:` against `Recorded sha256:`); the "live scripts" warning when the issue touches `scripts/` or hooks; cloud `gh` limits; REST fallback for reads; writes still use `make issue-comment`; "do not close or merge"; the return path.
**Fact:** issue, branch, hash, expected paths, protected files needing approval.
Never name an env file in a claim.

## Release

Fixed: the claim is released; nothing is merged or closed.
**Fact:** why, the branch and commit left behind, what is unfinished.

## Confirm

Fixed: the human confirmed the new body; the hash re-check ran; the PM records the hash in a `PM:` comment. After a label first: `Approved by: human confirmation in session, <date>` and the new hash; the label stays.
**Fact:** the new hash, the old hash, what changed; an amend's criterion id and its finding or review.

## Ruling

Fixed: first line `Orchestrator: Ruling`, then `Human ruled: <YYYY-MM-DD>`; record only what the human said. Each `Ruling: NAME=value` sets a setting for this issue; other `Ruling:` text records a process ruling, such as a human ship naming the finding. `Waiver: <gate> - <reason>` names a QA gate the human waived: `heavy-second-qa` or `qa-recheck`, as `WAIVABLE_GATES` allows (`customizing.md`). A waiver is recorded but no script acts on it yet.
**Fact:** the date, each ruling and waiver.

## Close

Fixed: who built it, what moved or was not done, what is not verified, and these lines, which `make issue-close` matches: `QA PASS commit: <7 to 40 hex>` (named in the latest `QA:` PASS; not for Light), `Merge commit: <7 to 40 hex>`, `Verify: <text>`, `Summary: <path>`, and for Light `Human approved diff: yes`.
Logged findings: `Findings (<grade>: logged)` headings, one bullet each (`asking-the-human.md`).
**Fact:** every value in those lines; each shipped finding, and how; each logged finding; each decision point, with its impact, effort, mode and answer.
Never close without QA PASS. Post after the last PASS (Light: after `tier-check: PASS`), then `make issue-close N=<n>`. Close as not planned only after the human approved that closure: `Orchestrator: Close as not planned` with `Human approved closure: <YYYY-MM-DD>` and `Backlog review: <path or comment URL>`, then add `REASON=not-planned`.
