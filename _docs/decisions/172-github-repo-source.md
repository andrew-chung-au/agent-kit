# Decision: the repository the GitHub wrappers talk to comes from `GITHUB_REPO` in `agent-kit.conf`

Issue #172 (Heavy). The human approved this record in a comment on #172 (body sha256 `d369ddd89f0e29722f00ce7bdfac2284a3a97045c2e0a171803cd029fecdcfa7`), copied here from the issue body.

- **Decision:** The kit's GitHub wrappers (`issue-hash`, `issue-create`, `issue-comment`, `issue-close`, `sweep-due`, `issue-dump`) take the repository from one place: a single `GITHUB_REPO="<owner>/<name>"` line in `agent-kit.conf`. The file is read as text and never sourced or run. The value is validated against `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` (no `..`, no `.` part) before any `gh` call, and the wrappers use `gh api` with that name. With no valid value, or more than one such line, every wrapper refuses and runs no `gh` command. Nothing else (environment, git remote, make variable, issue text) can name the repository.
- **Reason:** `gh issue ...` and `gh repo view` work out the repository from the git remote, which in Kiro Web points at Kiro's gateway, so every wrapper fails there while `gh api repos/<owner>/<name>/...` works. `agent-kit.conf` is already protected (commits need `HUMAN_APPROVED=1`, edits ask), so an agent cannot silently retarget the wrappers at another repository.
- **Alternatives:**
  - Keep reading the repository from the git remote: rejected, it is the failure.
  - An environment variable (`GH_REPO` or `GITHUB_REPO`): rejected, an agent or a tool setting can change it unseen, and it is not reviewed in a diff.
  - A make variable on every call: rejected, it moves the choice to whoever types the command.
  - A new config file: rejected, a second place for settings next to `agent-kit.conf`.
  - Ask `gh` for the default repository: rejected, that needs the same git remote.
- **Trade-offs:**
  - Every existing project must add the `GITHUB_REPO` line to `agent-kit.conf`, or its wrappers refuse. This is a compatibility break; the README changelog's "Existing projects:" note says so, and the template carries the line.
  - The kit import procedure does not yet look for the new line in a project's conf; a refusal message names the missing line instead.
  - The value is checked as text, so a repository whose name needs characters outside the pattern cannot be used.
  - One repository per project folder.
- **Evidence:** #172; PR #176 (the Engineer chose this before the record was approved; QA FAIL at https://github.com/andrew-chung-au/agent-kit/issues/172#issuecomment-6683463871); Kiro Web error text in this issue's Why section.
