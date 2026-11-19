# Hand over the grooming of #115, #112 and #122

> Written 2026-11-13T10:00Z by the Kiro Web orchestrator. The PM's drafts were produced in the Kiro Web session on 2026-11-13 and would have been lost with its scratch folder, so they are committed here. Nothing in this folder has been applied to GitHub: no issue body was edited, no PM comment was posted, no label or title was changed.

## Purpose

Three issues were groomed ahead (`delivery-pace.md` item 3) but parked so that #21 could proceed without waiting. #21 is now closed. Whoever grooms them next (another session, a PM launch, or the human) starts from these drafts instead of from scratch.

## What is here

`_human-tasks/groom-handover-2026-11-13/` holds, per issue, the groomed body (`groomed-<n>.md`) and the PM comment draft (`pm-comment-<n>.md`, first line `PM:`, with `Proposed tier:` and `Body sha256:`). The hash in each comment is of the exact bytes of the matching body file.

| Issue | Proposed tier | Body changes | Body sha256 |
|---|---|---|---|
| #115 Bring `openapi.yaml` in line with the code | Standard | Yes | `6c08ec36942905820365ccd8ea0009ebcf35630992360d67cdc4177aea11ef9c` |
| #112 A retryable contract code for a claim's lock timeout | Heavy | Yes, with a `## Decision record` | `5cedf334368eabec5832721c855bdd85d65b2388fdf0678a6b7ad0422492e749` |
| #122 Make the close floor test the shape of a reflection | Heavy | Minimal | `78dec8119b48d15ca9fbf97a261fd42f93fc23fe7b4213e5f0dccdb70d31b782` |

Check any file with `sha256sum _human-tasks/groom-handover-2026-11-13/groomed-115.md` (and the others); it must print the hash above.

## Read first: these drafts are a baseline, not a finished product

They were written against `main` at 8d2ee9e. `main` has moved (#21's frontend, #63's merge, more). Before applying a draft:

1. Run `make issue-hash N=<n>`. The issue body may have changed since. If it differs from the baseline, show the diff to the human first.
2. Re-check the draft's file and line references against current `main` (`openapi.yaml`, `socboard/cases.py`, `socboard/schemas.py`, the contract tests). Update stale ones; that changes the body, so recompute its hash the same way (`sha256sum` of the exact file, which ends in one newline like the live bodies).
3. Do the claim-time check: no decision record dated after the issue's grooming contradicts a criterion (`make decisions`, then search the newer ones).

## Questions for the human (not yet answered)

The orchestrator's recommendation is in brackets. None of these has been approved.

- **#112, scope of the handler:** app-wide (the draft's choice), or only the four write routes (`claimCase`, `transitionCase`, `addNote`, `ingestAlert`)? [app-wide]
- **#112, code and header:** `503` `service_busy` with `Retry-After: 1`? [yes]
- **#112, Postgres:** file a follow-up for the Postgres lock-timeout mapping now, or leave it to Deploy planning? [leave it to Deploy planning]
- **#122, the extra criterion:** the draft marks as an open question a limit on the Reflection block (three lines, 150 words). The real #51 reflection (293 words) and #16 reflection (222 words) must be accepted and are longer, and the real work comments are shorter than the reflections, so no length separates them. [drop the limit; keep the three-line, 150-word figure as guidance in `procedures/session-summary.md`, not as a script rule]
- **#122, the regression test:** a committed test needs a place in `tests/` (a separate approval). Accept a `.scratch/` check if none is approved? [approve a `tests/` file in the same sitting]

## How to apply a draft (each step needs the human's approval; editing an issue asks the human)

Run from the repository root, for one issue at a time (replace `<n>`).

1. Show the human the diff of the body: `gh api repos/andrew-chung-au/socboard/issues/<n> --jq .body` against `_human-tasks/groom-handover-2026-11-13/groomed-<n>.md`.
2. After approval, apply the body:
   ```
   gh api repos/andrew-chung-au/socboard/issues/<n> --method PATCH -F body=@_human-tasks/groom-handover-2026-11-13/groomed-<n>.md
   ```
3. Check the hash: `make issue-hash N=<n>`. `Body sha256:` must equal the hash in the table above. If it differs (the editor can change line endings or the trailing newline), have the PM record the new hash instead.
4. Post the PM comment: copy `pm-comment-<n>.md` to `.scratch/`, correct anything stale, then `make issue-comment N=<n> FILE=.scratch/pm-comment-<n>.md`. (Comments are posted from the owner's account; the `PM:` prefix is what marks the role.)
5. Add the `[groomed] ` prefix to the title (`gh api -X PATCH repos/andrew-chung-au/socboard/issues/<n> -f title="[groomed] <title>"`), as `.kiro/steering/backlog-order.md` requires, and tell the human it is ready to read.
6. The human reads it and adds `approved`. For #112 and #122, the approval names the `## Decision record` section. Nobody else changes a label.

## Order and effects

- #115 before #112: both edit `openapi.yaml` and the same status-set assertions in the claim and notes contract tests, so open together they conflict. #115 makes the sets equal; #112 then adds `"503"` to both sides. Delivery pace also stops two Core Engineer launches at once.
- Neither is a dependency of #21 any more. The roadmap still lists #115 and #112 before the frontend contract is relied on by #22.
- #122 is independent. It touches only protected kit files (`_docs/agent-kit/`), so it can share a sitting with #73 and #71, and each protected commit needs the human's approval of the exact diff.
- This folder can be deleted once all three are applied and approved.

## Risk

None to the running system: the folder holds text only. The risk is applying a stale draft; steps 1 to 3 under "Read first" are there for that.
