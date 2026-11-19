# Issue #104: Small follow-ups from #13 (missing database, seed variables, seed help text, hash bounds, secret check)

**Date:** 2026-11-13T22:52Z (UTC)
**Spec version:** 36d9ad7

## What changed and why

Tier: Standard (from the PM proposal; no tier label). Claude Code worked it in the local sandbox on `main` from `bce11aa`. Ponytail was on. Third of the issues the human ordered before #22 (#120, #114, #104). Groomed in this session; the PM drafted the body, the orchestrator applied it with `gh api` after the human approved the command, and the human labelled it.

- **Items 2 to 6 (first round, `cae1bc1`; protected edits `73d0d34`):** `make seed`'s three password variables are documented as needed on every run (`AGENTS.md` Seed line, `README.md`) and pinned by two tests; the `Makefile` `seed:` help text names the users and the variables; `parse_hash` bounds stored scrypt parameters (`n` up to 2^18, `r` up to 8, `p` up to 2, memory up to 2^28), each refused case tested, with a spy on `hashlib.scrypt`; the token secret needs 32 characters after `str.strip()` (value used as given), with the exact message and README guidance; a NUL in the login username is "no such user" (401, dummy-hash work, no query). The `## As built (#13)` section of `_docs/decisions/2026-11-12T2255Z-auth-tokens.md` states the new bounds and the trimming rule. `AGENTS.md` (lines 19 and 28) and `Makefile` (line 239) were committed with `HUMAN_APPROVED=1` after the human approved the exact diff. All of these passed QA at the first run.
- **Item 1, a request never creates a missing SQLite file, took five Engineer rounds:**
  - Round 1 checked the URL in Python before building the engine. QA FAIL at `73d0d34` (`?uri=false`, `?uri=0` and a `file:` URI still created the file).
  - Round 2 (`8642e81`) read `uri` as the dialect does and resolved `file:` paths. QA FAIL at `8642e81` (a repeated `uri` and a `#` fragment wrongly refused a real file). The human accepted those two as Low; a third QA run passed at `8642e81`.
  - The first Reviewer then found (Medium) that the check, run at engine creation, turned a 401 (no token) or a 422 (bad login body) into a 500 when the file is missing. The human chose to replace the check.
  - Round 3 (`94184f4`, Engineer on Opus): a `do_connect` listener on the request engine only makes SQLite open the file with `mode=rw`, so SQLite itself refuses to create it, at the first connection; `make migrate` and `make seed` keep their own engines. QA FAIL at `94184f4` (`mode=rwc%2500`: SQLite ends a value at a decoded NUL; the hook still decoded).
  - Round 4 (`4826cac`, Opus): the hook never decodes a `file:` URI; it keeps it only when its last `mode` is a plain `ro`, `rw` or `memory` with no `%` after it, else appends `mode=rw`. The Engineer first measured SQLite 3.46.1 and found the ruling's premise ("the last `mode` wins") false; the human approved the corrected costs. QA PASS at `4826cac` (135 spellings, mutation runs).
  - Round 5 (`ab2b73e`, `6056f63`): the second Reviewer's four findings. A test for the "no `%` after the last mode" guard (SQLite does create the file for `mode=memory&mode=rwc` without the hook, as measured), the docstrings corrected to what was measured, `quote(os.fsencode(...))` for paths that are not valid UTF-8, and one test comment. QA PASS at `6056f63`.
- **The order of checks is kept:** with a missing database file, no token gives 401, a bad login body 422, health 200; only a request that queries gets the generic 500 `internal_error`.

**What I learned:** a criterion that forbids a side effect of a library (a file created) should be met by a guard the library enforces itself, and every claim about how the library parses input should be measured against the installed version before the design rests on it. Item 1 failed three times on unmeasured claims.

## Reflection

### PM

PM: reflection on grooming #104 (body hash `1388505c…`; QA passed, the issue is being closed).

Reflection:
(1) Slowed down: I missed that `_docs/decisions/2026-11-12T2255Z-auth-tokens.md` (`## As built (#13)`, lines 15 and 17) states the scrypt parameters and the 32-character secret minimum, so the coordinator had to resume me to add the record update to the criteria and the expected paths. I had searched `_docs/` for paths and names, but not for the values the issue changes.
(2) Nearly went wrong: item 1's criterion and Design had our code predict which SQLite URLs SQLite would create a file for ("applies only to a SQLite URL with a file path"). Nothing said how the prediction would be shown to be complete, so QA kept finding spellings it missed (`?uri=false`, `mode=rwc%2500`). The criterion should have said: the request engine must make creation impossible through an option SQLite itself enforces (open with `mode=rw`); the check runs a fixed list of URL spellings through the real driver; and any spelling that is not listed must fail closed, with no file created.
(3) Proposed change: in `_docs/agent-kit/team/pm.md`, after the text-check rule, add: "When a criterion forbids a side effect of a library or tool (a file created, a connection made), require a guard the library enforces itself, not code that predicts its parsing. Check it with a listed set of inputs run through the real library, plus a fail-closed rule for any input not listed. Also search `_docs/decisions/` for every value the issue changes." Expected effect: no multi-round FAIL loops on such criteria, and no missed record updates. Measure: QA FAILs per criterion of this kind, and amendments made for a missed record, over the next five groomed issues (target: at most one FAIL, zero amendments).

### Engineer

Engineer: final reflection on #104 (rounds 1 to 5; rounds 1 to 4 by other launches, rounds 3 and 4 of them on Opus)

Ponytail: reused SQLite's own `mode=rw` refusal through one SQLAlchemy `do_connect` hook. The URL-parsing check was deleted rather than patched, and decoding SQLite URIs in Python was left out. No dependency was added.

Reflection:
1. Slowed: every design rested on unmeasured claims about how SQLite reads a URI ("the last `mode` wins", then "a later `mode` only narrows"). Each was disproved later, by QA or by the round 4 and 5 measurements.
2. Nearly wrong: three spellings created the file from a request (`uri=false`, `mode=rwc%2500`, and `mode=memory&mode%00=rwc`, which needed line 67 and had no test until round 5). Also, round 1's check would have turned 401 and 422 responses into 500s.
3. Proposal for `_docs/agent-kit/team/software-engineer.md`: when code depends on how an outside parser reads input, measure each claimed fact against the installed version in a `.scratch/` test before coding, and list the results in the comment. Expected effect: fewer QA FAILs per criterion. Measure: FAILs and rounds per criterion in `make ponytail-metrics` on the next parser-bound issues.

### QA

QA: Reflection (#104, all six QA runs)

Reflection:
1. Slowed: each run rebuilt and extended a spelling probe (67, then 135, then 139 spellings across `qa104_r2` to `qa104_r7`), because the ruling's SQLite assumptions had to be measured, not read.
2. Nearly wrong: QA passed `4826cac` without testing the "no `%` after last mode" guard; the Reviewer found it; my r7 mutant wrapper caught `Exception`, so the fail showed as an error.
3. Change: in `_docs/agent-kit/team/qa-engineer.md`, require removing each guard condition of a security check in a `.scratch/` copy and confirming a tracked test fails. Effect: untested guards are found before the Reviewer. Measure: Reviewer "untested guard" findings after a QA PASS, per issue.

### Ponytail

Engineer: see the `Ponytail:` line above.

## Launch usage

Tool: Claude Code. Figures copied from the completion notifications; a resumed launch's figure may be cumulative or per-resume (unknown). Opus marks the launches the human asked to run on the stronger model.

- PM grooming: 157 s, 38 tool uses; amendment: 24 s, 7; hash record: 66 s, 14; Reflection and #153: 106 s, 21. PM filing #144: 67 s, 16.
- Engineer round 1: 547 s, 66; round 2 (resumed): 437 s, 19.
- QA run 1 (FAIL at `73d0d34`): 477 s, 28. QA run 2 (FAIL at `8642e81`): 467 s, 26. QA run 3, first launch: stopped early at a usage limit (figures unknown; left nothing); relaunch (PASS at `8642e81`): 560 s, 22.
- Reviewer 1: 150 s, 10.
- Engineer round 3 (Opus): 1049 s, 57. QA run 4 (FAIL at `94184f4`): 676 s, 49.
- Engineer round 4 (Opus): fact check that stopped as instructed: 161 s, 22; implementation (resumed): 568 s, 33. QA run 5 (PASS at `4826cac`): 860 s, 65.
- Reviewer 2: 207 s, 14.
- Engineer round 5: 584 s, 44; comment fix (resumed): 897 s, 58 (likely cumulative); Reflection: 36 s, 8. QA run 6 (PASS at `6056f63`): 289 s, 25; Reflection: 339 s, 30 (likely cumulative).

## Files created or modified

`socboard/sessions.py`, `socboard/passwords.py`, `socboard/auth.py`, `README.md`, `_docs/decisions/2026-11-12T2255Z-auth-tokens.md` (its `As built (#13)` section), `AGENTS.md` and `Makefile` (protected, approved diff), `tests/test_auth_follow_ups.py` (new), `tests/test_auth_seed.py`, `_docs/planning/roadmap-1-core.md` (#120, #114, #104 done; #144 and #153 placed), the merge of `origin/main` (Deploy planning, PR #138, #145, #146), this file.

## Decisions made by the human

- Grooming: option A on all five questions (keep 500 `internal_error`; document and pin the seed variables; bounds of twice the current work; strip then 32 characters; include the NUL login case); Standard tier; six items; the `gh api` body edit.
- The protected diff (`AGENTS.md` lines 19 and 28, `Makefile` line 239), committed with `HUMAN_APPROVED=1`.
- #144 filed (a trailing NUL in a password verifies as the same password): option A with 401 and a one-line `openapi.yaml` note; not before #22.
- After the second QA FAIL: accept the two spellings (a repeated `uri`, a `#` fragment) as Low; later superseded.
- The first Reviewer's finding 1: replace the check with a connect-time `mode=rw` listener, run by an Opus Engineer; the error moves from engine creation to the first connection (a deviation from the body's Design section only; body and hash unchanged).
- After the QA FAIL at `94184f4`: option C (never decode; plain last mode or append `mode=rw`); then the corrected costs after the Engineer measured SQLite: an oddly encoded `ro` is refused, an oddly encoded `memory` opens the named file read-write. QA's Low at `4826cac` (the same two effects when a plain `ro` or `memory` is followed by a parameter holding `%`) accepted under the same ruling.
- The second Reviewer's four findings applied; one more test comment fixed under finding 2.
- #153 filed for two clock-dependent tests, before #22.
- The human asked the orchestrator to use a stronger model when needed, as a judgment call, not a fixed rule.

## Mismatches with the spec or design docs

- Item 1's Design section says the error is raised from `DatabaseState.engine()` before `create_db_engine`; it now arises at the first connection (approved by the human; the body is not edited).

## Commands to validate

- **Verify:** `make verify` (`PASS WITH WARNINGS` at `6056f63`: 1611 Python, 208 frontend, whitespace clean; the warnings, 3 removed assertion lines and `tests/conftest.py` changed, come from #114's commits, which are ahead of `origin/main`); `make verify BASE=bce11aa` (#104 alone): PASS, 86 assertion lines added, 0 removed.

## Proposed AGENTS.md changes

none. (The Reflection proposals touch `_docs/agent-kit/` files; they are for the sweep.)

## Temporary changes

none. No process was started. `make clean-scratch` has not run: `.scratch/` holds the Engineer's SQLite measurements (`.scratch/test_sqlite_uri_facts_104.py`, `.scratch/test_sqlite_memory_mode_104.py`), which pin the SQLite behaviour the hook relies on. They are proposed below as a tracked test before cleanup.

## Interruptions

- The first launch of QA run 3 stopped at a usage limit. Checked with `git status`, `git log` and the issue comments: it left no comment and no change; it was relaunched fresh.
- Process slips, all by launches, none of them changing the repository beyond the issue: the round 1 Engineer appended two tests with a heredoc, and the round 2 Engineer ran one `python -I -c` command (both against the command-shape rule); the round 3 Engineer amended its own unpushed commit once; one QA launch tried to edit its comment file through the Artifact tool, which the permission check blocked (nothing was published).

## Unrelated problems noticed but not fixed

- A trailing NUL in a login password verifies as the same password: #144.
- Two clock-dependent tests failed once each during the QA runs: #153.
- SQLite's error text for a malformed URI includes part of the name (log only; it predates #104).
- `make verify` has no line-length check (the Engineer's #120 Reflection proposes one).
- #144's branch (`issue-144-nul-password`) exists on origin; it will need a merge with this issue's `socboard/passwords.py` change.

## Follow-ups for the next session

- Proposal: commit the Engineer's SQLite measurements as a tracked test (it pins the behaviour of the installed SQLite that the hook's safety depends on, so a SQLite upgrade that changes it fails a test). Needs the human's approval as a small follow-up issue.
- #112 (before #22; its groomed draft needs the human's confirmation), #153 (before #22; needs grooming), then #22 (Engineer on Opus).
- Sweep proposals from the Reflections: require a library-enforced guard and measured parser facts (PM and Engineer), and require removing each guard condition in QA's mutation runs (QA).
