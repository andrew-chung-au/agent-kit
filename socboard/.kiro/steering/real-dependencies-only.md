---
inclusion: always
---

# Wait only for a real dependency (maintainer's ruling, 2026-11-16)

On 2026-11-16 the maintainer was held up several times by waits that protected nothing: #266 "waits for #237's first deploy" (applying it first was better: nothing was running, so the replacement restarted nothing and no instance id needed updating), the step 9 snapshot check (it blocks no work), and a QA or start gate written into an issue before the facts were known. These rules apply to every lane.

1. **A wait needs a reason that is still true.** Before you hold work back because of an issue's start condition, an order in a roadmap, a clock or another issue, say in one sentence what would actually break or be done twice if the work went ahead now. If you can't name it, or it is no longer true, the wait does not apply: go ahead, and say in your message that you did and why.
2. **Writing code is not applying it.** Building, testing, QA and merging never wait for a deploy, an apply or a human run, unless the change itself would be applied automatically by merging it. Only the step that changes a live system waits for what that system needs.
3. **Prefer changing the server before anything runs on it.** A change that replaces the instance or restarts services costs least while nothing is deployed. Do not delay it until after a deploy "to protect the deploy" unless the deploy needs the old state.
4. **Recording is not a dependency.** Filling a result table, an evidence row or a `VERIFY:` note never blocks other work. Record it when the result exists; mark it pending until then.
5. **When a wait is real, say what ends it.** Name the event (a merge, an apply, a run), not a time, and the one thing it protects.
6. **The maintainer's ruling wins.** If the maintainer says go, go, and record the ruling in the issue or pull request; do not ask again for the same wait.
