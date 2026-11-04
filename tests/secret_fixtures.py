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

# The env file name, built from pieces so no complete name sits in this file (as the tokens below).
ENV = ".en" + "v"

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
    # Added by #63.
    ("sk-proj key", "sk-" + "proj-" + "Ab3dE_fG-hI" * 3, 9, "proj-Ab3dE"),
    ("sk-ant key", "sk-" + "ant-" + "api03-" + "Zx9_Yw8-Vu7T" * 2, 9, "api03-Zx9"),
    ("gho_ token", "gho_" + "A1b2" * 9, 10, "gho_A1b2"),
    ("ghs_ token", "ghs_" + "C3d4" * 9, 10, "ghs_C3d4"),
    ("ghr_ token", "ghr_" + "E5f6" * 9, 10, "ghr_E5f6"),
    ("lower-case bearer header", "authorization: bearer " + "abcdefghij" * 2 + "XYZ", 11, "abcdefghij"),
    ("upper-case bearer header", "AUTHORIZATION: Bearer " + "0123456789" * 2 + "abc", 11, "0123456789"),
    ("basic auth header", "Authorization: Basic " + "dXNlcjpw" + "YXNzd29yZA==", 12, "dXNlcjpw"),
    ("PGP private key header", "-----BEGIN PGP " + "PRIVATE KEY BLOCK-----", 13, "PRIVATE KEY BLOCK"),
    ("JWT", "eyJ" + "hbGciOiJI" + ".eyJ" + "zdWIiOiIx" + "." + "SflKxwRJSM" + "eKKF2QT4", 14, "hbGciOiJI"),
    ("Slack webhook", "https://hooks." + "slack.com/services/" + "T0000AAAA/" + "B0000BBBB/" + "XXXXxxxxYYYY", 15,
     "B0000BBBB"),
    ("AWS secret key, lower case", "aws_secret_access_key = " + "wJalrXUtnFEMI/K7MDENG/" + "bPxRfiCYEXAMPLEKEY", 16,
     "wJalrXUtn"),
    ("AWS secret key, upper case", "AWS_SECRET_ACCESS_KEY: '" + "AbCdEfGhIjKlMnOpQrSt" + "UvWxYz0123456789+/AB" + "'",
     16, "AbCdEfGhIj"),
    # Added by #86: the redactors replace only the matched span, so the whole file name token must
    # match. The last part is the variant suffix, which must not be left visible.
    ("bare env file name", "cat " + ENV, 8, ENV),
    ("env file name after a folder", "cat config/deploy/" + ENV, 8, ENV),
    ("production variant", "cat " + ENV + ".prod" + "uction", 8, "production"),
    ("local variant", "cat " + ENV + ".lo" + "cal", 8, "local"),
    ("staging variant with a backup suffix", "cp " + ENV + ".stag" + "ing.bak /backup/", 8, "staging.bak"),
    ("variant at the end of a longer command", "docker run --rm --env-file " + ENV + ".devel" + "opment", 8,
     "development"),
]

NON_MATCH = [
    ("git status", "git status"),
    ("make verify", "make verify"),
    (".env.example", ".env.example"),
    ("config/.env.example", "config/.env.example"),
    ("sk-short", "sk-short"),
    # Added by #63: near misses that must pass.
    ("a word ending in sk- before proj-", "brisk-proj-planning-for-the-next-quarter-long"),
    ("a hyphenated word containing sk-", "risk-assessment-for-something-long"),
    ("a 39-character ghs_ body", "ghs_" + "a" * 39),
    ("a 35-character ghs_ body", "ghs_" + "a" * 35),
    ("dotted version strings", "release 1.2.3 and v2.10.4"),
    ("a JWT with two parts", "eyJ" + "hbGciOiJI" + ".eyJ" + "zdWIiOiIx"),
    ("a Slack URL without the three-part path", "https://hooks." + "slack.com/services/T0000AAAA"),
    ("the AWS key name without a value", "aws_secret_access_key = (not set)"),
    ("a 40-character commit hash", "commit " + "0123456789abcdef" * 2 + "01234567"),
    ("a short Basic value", "Authorization: Basic short"),
    ("a PGP public key header", "-----BEGIN PGP PUBLIC KEY BLOCK-----"),
    ("a password= value (left out on purpose)", "password=hunter2"),
    ("a short lower-case bearer value", "authorization: bearer short"),
    # Added by #86: near misses for the env file pattern. The example forms stay unmatched, with a
    # backup suffix too (the example file is still the example); names that merely start with the
    # same letters are not env files.
    ("the example env file with a backup suffix", "cp " + ENV + ".example.bak /backup/"),
    ("the example env file in a longer command", "diff " + ENV + ".example config/" + ENV + ".example"),
    ("a direnv file", "cat " + ENV + "rc"),
    ("a name that only contains env", "cat my" + ENV + ".txt"),
    ("an environment folder", "ls " + ENV + "ironment"),
    ("a word before the dot", "see the dev" + ENV + " docs"),
    ("env without a leading dot", "cat env.production"),
]

PATTERN_COUNT = 16
