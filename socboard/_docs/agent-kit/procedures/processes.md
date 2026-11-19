# Long-running processes

How to start and stop a server, watcher or responder while working or testing.

- Start and stop only through `<name>-start` and `<name>-stop` make targets, or a `.scratch/` script that records the process ID it started and stops only that process. See Start and stop targets in `blueprints.md`.
- Wait for results with a timeout, never an open-ended loop.
- Never stop a process you didn't start; ask the human.
- Before finishing, confirm nothing you started is still running (`make <name>-stop` for each).
