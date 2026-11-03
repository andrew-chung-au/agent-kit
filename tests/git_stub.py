"""A stub `git` that fails for chosen commands and passes everything else to the real git (#43).

Not named test*.py, so `unittest discover` does not collect it. Put the folder that
`install` returns first on PATH. The stub fails a call when its argument string
(`$*`) matches one of the glob patterns in GIT_STUB_FAIL (one per line), prints a
reason on stderr and exits 128, the way git itself fails. Every call is appended to
a log file, so a test can show the stub was reached and was not skipped.

Patterns match the whole argument string, for example:
    status *                 any `git status ...`
    diff *                   any `git diff ...`
    rev-parse HEAD           exactly `git rev-parse HEAD`
    rev-parse --short HEAD   exactly that call
"""
from __future__ import annotations

import shutil
from pathlib import Path

STUB = """#!/bin/sh
args="$*"
echo "$args" >> "{log}"
set -f
fail=0
OLDIFS=$IFS
IFS='
'
for pattern in $GIT_STUB_FAIL; do
  case "$args" in
    $pattern) fail=1 ;;
  esac
done
IFS=$OLDIFS
if [ "$fail" = 1 ]; then
  echo "stub git: failing on purpose: $args" >&2
  exit 128
fi
exec "{real}" "$@"
"""


def install(work: Path):
    """Write the stub under `work`. Returns (folder to put first on PATH, log file)."""
    real = shutil.which("git")
    assert real, "git is needed to run these tests"
    folder = work / "git-stub-bin"
    folder.mkdir(exist_ok=True)
    log = work / "git-stub.log"
    stub = folder / "git"
    stub.write_text(STUB.format(log=log, real=real), encoding="utf-8")
    stub.chmod(0o755)
    return str(folder), log


def calls(log: Path) -> list:
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []
