# Run the single-page-mode spike for the frontend build

## Purpose

Find out whether TanStack Start's single-page mode (`spa: { enabled: true }`) builds `frontend/` to static files only, or still emits server, Nitro or Cloudflare worker output. The answer picks the route for #27. Issue: #27.

## Where to run it

The dev container (or any shell with the registry reachable), in the clean clone, on a scratch branch or the current `main`. Not here: the Kiro Web sandbox, where the npm registry answers `403 Forbidden`.

Nothing here is committed. The only tracked file touched is `frontend/vite.config.ts`, and step 6 restores it. `node_modules`, `dist` and `.output` are git-ignored.

Approval: running `bun install --frozen-lockfile` installs the packages already pinned in `bun.lock`. It adds no dependency and must not change the lockfile. If you would rather not install into the clone, say so and I will wait.

## Before you start

1. Check bun is available and the tree is clean.

```
bun --version
git status --short
```

Expected: a version number (1.2.x was used when this was written), and no output from `git status`.

## Steps

### Step 1: Install from the lockfile without changing it

```
cd frontend
bun install --frozen-lockfile
```

Expected: install completes, no "lockfile had changes" error.
If different: stop and paste the output. A registry or release-age error here is a finding, not something to work around. Don't edit `bunfig.toml`.

### Step 2: Baseline build, before any change

```
bun run build
find dist .output -maxdepth 3 -not -path '*/node_modules/*' | sort
```

Expected: a build that finishes. Paste the file listing. The point is to see what the unmodified Lovable config emits (likely `dist/client`, `dist/server`, `.output/` with Cloudflare or Nitro files).
If different: if the build fails, paste the last 30 lines and stop.

Then clear the output before the next build:

```
rm -rf dist .output
```

### Step 3: Turn on single-page mode

In `frontend/vite.config.ts`, add `spa: { enabled: true },` inside the `tanstackStart` object, next to `server`:

```ts
export default defineConfig({
  tanstackStart: {
    server: { entry: "server" },
    spa: { enabled: true },
  },
});
```

Leave everything else unchanged.

### Step 4: Build again and list the output

```
bun run build
find dist .output -maxdepth 4 -not -path '*/node_modules/*' | sort
```

Expected for a pass: an `index.html` plus assets, and none of: `server/`, `.output/server`, `wrangler.json`, `_worker.js`, `nitro.json`.
If different:
- If there is a shell page named `_shell.html` and no `index.html`, TanStack's docs say the shell's output path can be set with `spa.prerender.outputPath`. Try `spa: { enabled: true, prerender: { outputPath: "/index" } }`, rebuild, and record both results. Check the current TanStack docs for the exact option names, since the project pins a recent beta.
- If server, Nitro or worker output is still produced, that is the result: the fall-back (plain Vite and React) applies. Record it and go to step 6.

### Step 5: Serve the folder with a plain static server and check the login screen

Use the folder that holds `index.html` (for this project that was `.output/public`, not `dist/client`). Python is used so nothing is installed.

```
python3 -m http.server 4173 --directory .output/public
```

Open `http://localhost:4173/` in a browser. Make sure `VITE_USE_MOCK` is on for this build (as set in the default env; if the login page shows no demo credentials, say so).

Expected: the login screen renders. Reloading `/cases/1` is expected to fail with 404 on this server; that is the known deep-link need for the Deploy phase, not a spike failure.
If different: note what the page shows and any console errors. Stop the server with Ctrl+C.

### Step 6: Restore the config and clean up

```
git checkout -- vite.config.ts
rm -rf dist .output
git status --short
```

Expected: no output from `git status` (`bun.lock` unchanged, no tracked file modified).
If different: paste the output. A changed `bun.lock` is a finding.

## Record the result

Paste the output or write pass or fail for each step. Then tell the orchestrator the outcome so I can post it on #27 and add it to `lovable-guidance.md`.

Run on 2026-11-10 (about 23:06 to 23:09 local) in the clean clone, `vite` 8.1.5, Nitro preset `cloudflare-module`.

| Step | Pass or fail | Output or note |
|---|---|---|
| 1 install | Not shown | The build ran, so packages were installed. The `bun install --frozen-lockfile` output was not pasted. |
| 2 baseline listing | Pass (build ran) | Output only in `.output/`, no `dist/`. `.output/public` holds `assets/*`, `favicon.ico`, `robots.txt`, `_headers`, and no `index.html`. `.output/server` holds the Cloudflare worker (`index.mjs`, `_ssr/*`, `_libs/*`, `wrangler.json`), plus `.output/nitro.json`. |
| 4 spa-mode listing (server/Nitro/worker output present?) | **Fail** | Server output is still produced: `.output/server/*`, `.output/server/wrangler.json`, `.output/nitro.json`, and a new `dist/server`. Prerender log: `Prerendered 1 pages: /`. |
| 4b `_shell.html` vs `index.html` | **Fail** | Only `.output/public/_shell.html`; no `index.html`. The `outputPath: "/index"` variant was not tried: it could rename the file but not remove the server output. |
| 5 login screen | Not run / invalid | `dist/client` does not exist (the step named the wrong folder; the static output is `.output/public`). `GET /` returned 404 because the folder was missing. Skipped as moot after step 4. |
| 6 clean tree | Not shown | `git checkout -- vite.config.ts`, `rm -rf dist .output .wrangler` and `git status --short` still to run and paste. |

**Result:** single-page mode does not give static files only. The build still emits server, Nitro and Cloudflare worker output and no `index.html`. By the issue's rule, the route is the fall-back: remove TanStack Start, Nitro and the Lovable build wrapper, and build with plain Vite and React keeping TanStack Router.

**Corrections to this file:** step 5 should serve `.output/public`, not `dist/client`. In step 2, `dist` only appears after the SPA-mode build; the baseline output is `.output/` alone.

## Risk

Low. The install is from the existing lockfile; the only tracked edit is reverted in step 6. If you stop part-way, run `git checkout -- frontend/vite.config.ts` from the repository root.
