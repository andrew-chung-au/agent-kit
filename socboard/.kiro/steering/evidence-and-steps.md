---
inclusion: always
---

# Evidence for reviewers, and steps a person can follow (human ruling, 2026-11-16)

Peer reviewers score this project against `_docs/planning/rubric.md`. They read the README and follow links; they cannot open the maintainer's GitHub settings, AWS account or terminal. These rules apply to every lane and every issue from now on.

1. **Every issue says what evidence it leaves.** Its acceptance criteria name the artefact a reviewer can open (a CI run, a pull request, a committed result file, a screenshot, a job summary) and the rubric criterion it supports. The Engineer links it from the README's reviewer section in the same pull request.
2. **Record a check when it happens, once.** When the maintainer or CI checks something, the result goes straight into a committed, dated record (a human task's result table, or the evidence timeline), with the date, what was checked, the result and a link. Nobody repeats a check only to produce evidence. A check is run again only when the thing it checked has changed since (for example, a bootstrap change replaces the instance), and the record says why.
3. **Steps a person runs are written as steps.** Any instruction a person is expected to carry out (a human task, a README section, a runbook, an issue or chat message) gives one command per block, what the person should see, and what to do if it differs, following `_docs/agent-kit/templates/human-task.md` until #252 replaces it. A value the person must choose comes with a suggested default made by a command.
   - **Values in commands (maintainer's ruling, 2026-11-17, after the first prod deploy).** A command block holds no angle-bracket placeholder (`<digest>` was typed literally and the shell read `<` as a redirect). Prefer a shortcut set by a command that reads the value (`I=$(terraform -chdir=terraform/server output -raw instance_id)`), then an `echo "I=[$I]"` block with its expected output. Where the person must paste a value, use a placeholder in capitals (`PASTE-DIGEST-HERE`), and:
     - at the step that **produces** the value, say in its `Expected:` line that this is the value to keep, and where it will be pasted;
     - **repeat** it in the sentence right before the block that uses it: which placeholder to replace, with what, and what it should look like;
     - follow that block with an echo or an `If different:` that catches the placeholder left in place.
   - Commands run from the repository root (`-chdir=...` for Terraform), and the file says so once. Shortcuts live only in the terminal that set them. `file://` paths are written in full, so the three slashes show (`file:///tmp/...`). `aws ssm send-command` parameters are JSON. Model: `_human-tasks/2026-11-17T0030Z-human-task-267-engineer-first-prod-deploy.md` and `_docs/runbooks/deploy-and-teardown.md`.
4. **No video is planned.** Evidence is run links, committed results and screenshots, and the on-call agent's own pull request. A recording is optional and never the only evidence for a criterion.
5. **Evidence outlives the deployment.** The server runs for about a week. Before teardown, every link the README relies on must work without the live server (run logs, pull requests, committed files and images), and the README says the URLs are no longer live.
