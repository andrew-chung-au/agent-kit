Title: Make Verify quiet by default, printing the test output only on failure or with V=1

**What is wrong or missing**

`make verify` prints the whole test command's output on every run, even when it passes. Every role runs it (the Engineer, QA, the Claude Code stop hook), so a passing run fills the agent's context with hundreds of lines nobody reads. The useful result is a few `PASS:` / `FAIL:` lines and the final `VERIFY:` line.

**What you expected**

Verify prints its own check lines and the final verdict; the test command's output is shown only when that step fails, or in full with `make verify V=1`.

Plan fields:

- Proposed tier: standard (section 9). Note: `agent-kit/scripts/verify.sh` is on the tier-check escalation list and runs live, so the change affects the gate for this very issue.
- Effort: S. One script, the make targets, the doc and a test. (Tie-break: lower for Effort; it may come out R with tests.)
- Reasoning: N. The failure path must still show everything needed to fix it.
- Impact: C. If a failure's output were hidden, or the exit code changed, Verify would pass or fail wrongly.
- Needs: none (section 9: parallel lane).
- Runs in: sandbox.
- Debt: none.
- Touches protected `agent-kit/` files: yes; also this repo's `Makefile`.
- Files: `agent-kit/scripts/verify.sh`, `agent-kit/templates/Makefile.mk` and this repo's `Makefile` (pass `V`), `agent-kit/procedures/verify.md`, `agent-kit/claude-code/hooks/verify_on_stop.py` (only if it parses the output; it runs live), `agent-kit/CHANGELOG.md`, `tests/test_gate_verify.py`, `tests/test_verify_on_stop_names.py`. The push check (`agent-kit/environments/local-sandbox/pre-push`) is not touched; if it needs `V=1`, the Engineer posts a diff for the human (`AGENTS.md`, Project gotchas).

Acceptance criteria:

- [ ] C1. With tests passing, `make verify` prints no test-command output: only Verify's own lines (`PASS:`, `WARN:`, `FAIL:`, the assertion count, the untracked-files list) and the final `VERIFY:` line.
  Check: `tests/test_gate_verify.py` case with a passing stub `TEST_CMD` that prints 50 lines; none appear in the output.
- [ ] C2. When the test command fails, its full output is printed (or the last N lines plus the path of a full log under `.scratch/`; a grooming choice, recommend full output), followed by `FAIL:` and `VERIFY: FAIL`.
  Check: `tests/test_gate_verify.py` case with a failing stub; its output appears.
- [ ] C3. `make verify V=1` prints the full test output whatever the result.
  Check: `tests/test_gate_verify.py` with `V=1`.
- [ ] C4. Exit codes and verdict lines are unchanged in every case; the stop hook and the push check read the same result.
  Check: existing `tests/test_gate_verify.py` and `tests/test_verify_on_stop_names.py` pass unchanged.
- [ ] C5. Refused: a `V` value other than empty, `0` or `1` is rejected with a message, not treated as on.
  Check: `tests/test_gate_verify.py` case `V=yes`.
- [ ] C6. `procedures/verify.md` documents `V=1`.
  Check: read `agent-kit/procedures/verify.md`.

Scope note: `verify.sh` runs tests, lint and type check through one function (`run_gate`), so the quiet rule applies to all three; the criteria above apply to each. The `git diff --stat` section stays.

Out of scope: changing what Verify checks.

Proposed split: none.

**Evidence**

- Proposal section 9 row 10 ("Quiet Verify (`V=1` for full output)"); no other section describes it, so the criteria above are the PM's reading (see index, gaps).
- Current output: `agent-kit/scripts/verify.sh` runs `TEST_CMD` unfiltered; this repo's `make test` prints the whole unittest run on every Verify.
