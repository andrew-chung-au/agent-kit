# Cutting a release (human only)

Builds the kit zip that projects import. Reader: the maintainer, on their own machine. No agent pushes, tags or generates the release manifest. The version line in `README.md` and the entry in `CHANGELOG.md` are committed first. The adopter-side steps that use the zip are in `install-and-upgrade.md`.

## Places

| Place | What it is |
|---|---|
| **KIT CLONE** | A terminal in `~/projects/agent-kit`: your clean clone of the kit repository. Never open it in a container or run `make` in it. |
| **RELEASE FOLDER** | A terminal in `~/kit-release-<version>`: a new empty folder outside every repository. |

## Steps

Build it in a **new empty folder outside every repository**: not inside the kit clone, not inside any project, and never in a sandbox's `.scratch/`. You need `git`, `tar`, `python3` and `zip`.

1. **WHERE: KIT CLONE.** Check the release commit is merged and pushed, and the version line is committed:

   ```
   # KIT CLONE
   cd ~/projects/agent-kit
   git status --short
   git log origin/main..main
   head -3 agent-kit/README.md
   ```

   Expect the first two to print nothing, and the README header to read `**Version <version> (<date>).**`.

2. **WHERE: KIT CLONE.** Tag the release commit and push the tag:

   ```
   # KIT CLONE
   git tag -a v<version> -m "Kit <version>"
   git push origin v<version>
   git tag --list v<version>
   ```

   Expect `* [new tag]         v<version> -> v<version>` from the push, and `v<version>` from the last line. If you only ran `git tag -d` and pushed `main`, no tag exists; this step creates it.

3. **WHERE: KIT CLONE.** Make the new empty folder and put the tagged kit in it:

   ```
   # KIT CLONE
   mkdir ~/kit-release-<version>
   git archive v<version> agent-kit | tar -x -C ~/kit-release-<version>
   ls ~/kit-release-<version>/agent-kit
   ```

   Expect `README.md`, `scripts`, `procedures` and the other kit entries, and no `MANIFEST.sha256` yet.

4. **WHERE: KIT CLONE.** Write the manifest. `kit-manifest.py` hashes every kit file and records the version, so a project can later run `make kit-check` to see whether its copy is pristine or changed:

   ```
   # KIT CLONE
   python3 -B agent-kit/scripts/kit-manifest.py ~/kit-release-<version>/agent-kit <version>
   ```

   Expect `kit-manifest: wrote /home/<you>/kit-release-<version>/agent-kit/MANIFEST.sha256 (<n> files, version <version>)` (`<n>` is however many files the kit holds; it changes with the release). A refusal reads `kit-manifest: <reason>; nothing written`.

5. **WHERE: RELEASE FOLDER.** Zip the `agent-kit` folder so the zip's top-level folder is `agent-kit` and it holds `MANIFEST.sha256`:

   ```
   # RELEASE FOLDER
   cd ~/kit-release-<version>
   zip -qr agent-kit-<version>.zip agent-kit
   unzip -l agent-kit-<version>.zip | grep MANIFEST
   ```

   Expect one line ending `MANIFEST.sha256` under `agent-kit`. This zip is the file you drag into `.scratch/` in situations 4, 5 and 8 of `install-and-upgrade.md`.

6. **WHERE: RELEASE FOLDER, optional.** Check the zip unpacks to the same files as the folder you zipped:

   ```
   # RELEASE FOLDER
   mkdir check
   unzip -q agent-kit-<version>.zip -d check
   python3 -B agent-kit/scripts/kit-compare.py check/agent-kit agent-kit
   ```

   Expect the last line `kit-compare: identical`. For a full check, copy `check/agent-kit` to a scratch project's `_docs/agent-kit/`, set `KIT_VERSION="<version>"` in its `agent-kit.conf`, and run `make kit-check` in that project: expect `kit-check: pristine; claim <version> is correct`.

   Do not put the folder in the kit repository: the manifest is not committed there. A GitHub release page is not part of this process (issues #8 and #9); if you create one, attach this zip, not GitHub's automatic source zips.

## Refused

A manifest generated from a working tree, a tree with uncommitted or unpushed kit changes, or a commit no one has reviewed on a remote. It would claim a version that no tag holds, so every `kit-check` against it would mislead. Generate only from the `git archive` of the pushed tag.

## Installed files in a release

The release zip unpacks only the kit folder. The files the kit installs outside that folder (`.devcontainer/`, the CI workflow, the push check) are not placed by the unzip; the human places them, using `installed-files.txt`, which ships inside the kit folder (so it is in the zip and in `MANIFEST.sha256`). No agent places an installed file. For the `human-machine` entries (the push check), compare the installed copy as in "Comparing the installed push check (human only)" in `environments/local-sandbox/README.md`.
