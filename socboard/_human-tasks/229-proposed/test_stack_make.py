"""`make test-stack` (#229): the target refuses without a stack address, and is listed in `make help`.

The set case is shown by CI's Compose job, which runs the target against the stack.
"""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIABLE = "SOCBOARD_BASE_URL"


def run(*arguments, **environ):
    env = {key: value for key, value in os.environ.items() if key != VARIABLE}
    env.update(environ)
    return subprocess.run(["make", *arguments], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)


def assert_refused(done):
    shown = done.stdout + done.stderr
    assert done.returncode == 2, shown
    assert VARIABLE in shown
    # No test ran: pytest prints neither its header line nor a result line.
    assert "stack_only" not in shown and "passed" not in shown and "test session" not in shown


def test_the_target_refuses_when_the_address_is_unset():
    assert_refused(run("test-stack"))


def test_the_target_refuses_when_the_address_is_empty():
    assert_refused(run("test-stack", **{VARIABLE: ""}))


def test_the_target_is_listed_in_make_help():
    done = run("help")
    assert done.returncode == 0
    assert any(line.split()[:1] == ["test-stack"] for line in done.stdout.splitlines())
