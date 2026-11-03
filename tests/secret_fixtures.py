"""The one fixture list for the secret patterns (agent-kit/scripts/secret-patterns.txt).

Not named test*.py, so `unittest discover` does not collect it. Test modules
import it with `from secret_fixtures import MATCH, NON_MATCH`. The scanner tests
(this issue, #44) and the OpenCode plugin test (#20, later) both use this list,
so the two readers of the pattern file are tested against the same examples.

Every token-like value is built from pieces, so no complete secret-looking
string appears in the repository (a push scanner would flag one). None of them
is a real credential.
"""
from __future__ import annotations

# (name, text, number of the pattern that must match it, the part a scanner
# must never print). The pattern number is the line in secret-patterns.txt.
MATCH = [
    ("PEM private key header", "-----BEGIN " + "RSA PRIVATE KEY" + "-----", 1, "PRIVATE KEY"),
    ("ghp_ token", "ghp_" + "A1b2" * 9, 2, "ghp_A1b2"),
    ("github_pat_ token", "github_pat_" + "11AB" * 6, 3, "github_pat_11AB"),
    ("AKIA key", "AKIA" + "ABCD1234" * 2, 4, "AKIAABCD"),
    ("xoxb- token", "xoxb-" + "1234567890" + "ab", 5, "xoxb-1234"),
    ("sk- key", "sk-" + "A1b2C3d4E5f6G7h8I9j0", 6, "sk-A1b2"),
    ("Authorization Bearer header", "Authorization: Bearer " + "abcdefghij" + "0123456789", 7, "abcdefghij"),
    ("cat .env", "cat .env", 8, ".env"),
    ("config/.env.local", "config/.env.local", 8, ".env.local"),
]

NON_MATCH = [
    ("git status", "git status"),
    ("make verify", "make verify"),
    (".env.example", ".env.example"),
    ("config/.env.example", "config/.env.example"),
    ("sk-short", "sk-short"),
]

PATTERN_COUNT = 8
