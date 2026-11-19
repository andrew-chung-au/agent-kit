"""Shared by the Claude Code permission logger and `make permission-report` (issue #36).

Record format and limits: procedures/permission-log.md. Python 3 standard library only.
Secrets are removed with the lines of secret-patterns.txt (the one shared copy, next to this
file), the same way at write time and at report time.
"""
from __future__ import annotations

import re
from pathlib import Path

MAX_PATTERN = 200  # characters, after redaction
NO_PATTERNS = "[redacted: no patterns]"
PATTERNS_FILE = Path(__file__).resolve().with_name("secret-patterns.txt")
CONTROL = re.compile(r"[\x00-\x1f\x7f-\x9f\u2028\u2029]")


def load_patterns(file: Path = PATTERNS_FILE):
    """The compiled patterns, or None when they cannot be read or one would match everything."""
    try:
        lines = [l.rstrip("\r") for l in file.read_text(encoding="utf-8").split("\n")]
        lines = [l for l in lines if l != ""]
        if not lines:
            return None
        regexes = [re.compile(l, re.MULTILINE) for l in lines]
    except (OSError, UnicodeDecodeError, re.error):
        return None
    return None if any(r.search("") for r in regexes) else regexes


def redact(value: str, file: Path = PATTERNS_FILE) -> str:
    """Secrets replaced by [redacted], control characters by a space, then cut to 200 characters.

    The cut ends in "...". When the patterns cannot be used the value is not shown at all.
    """
    regexes = load_patterns(file)
    if regexes is None:
        return NO_PATTERNS
    for regex in regexes:
        value = regex.sub("[redacted]", value)
    value = CONTROL.sub(" ", value)
    return value if len(value) <= MAX_PATTERN else value[:MAX_PATTERN - 3] + "..."


def plain(value, max_length: int = 200) -> str:
    """A short string field: not a string gives "", control characters become a space, then cut."""
    if not isinstance(value, str):
        return ""
    return CONTROL.sub(" ", value)[:max_length]
