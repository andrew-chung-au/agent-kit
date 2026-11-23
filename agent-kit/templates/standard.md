# Standard: <the rule in a few words>

One file per rule, at most 120 words. An issue names it on its `Standards:` line; QA fails a breach of a listed standard.

- **Rule:** one sentence a result can breach
- **Why:** the problem it prevents, with where it showed up
- **When it applies:** which issues it covers; the PM lists the file on every issue that matches
- **Check:** a `make` target the project provides, or `read <file>` when the rule is not mechanical
- **Added by:** #<issue>
