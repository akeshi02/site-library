# The Library

A single page that auto-discovers every GitHub Pages site you own and
displays them as book spines on a shelf. Hover (or tap) a spine to pull it
out and read its "cover" — description, language, last updated. Click to
open the site.

This is a catalog, not a monitor — it doesn't ping your sites or check
uptime, it just lists what's there and refreshes once a day.

How it works:
- `scripts/build_library.py` calls the GitHub API to list your repos, finds
  the ones with Pages enabled, and pulls each one's description, primary
  language, star count, and last-updated date into `library.json`.
- `.github/workflows/build-library.yml` runs that script once a day via a
  GitHub Actions cron job, then commits the updated `library.json` back to
  the repo.
- `index.html` is the bookshelf itself — a static page that reads
  `library.json` and renders every site as a spine, grouped into shelves.
  Each spine's color, height, and width are derived deterministically from
  its repo name, so the shelf looks varied but stays consistent between
  visits.

## Setup (5 minutes)

1. Create a new **public** GitHub repo (e.g. `library`), or reuse an
   existing one.
2. Push these files to the `main` branch of that repo.
3. In the repo, go to **Settings → Actions → General → Workflow
   permissions** and select **"Read and write permissions"**. This lets the
   workflow commit `library.json` back to the repo.
4. Go to **Settings → Pages** and set the source to **"Deploy from a
   branch"** → branch `main`, folder `/ (root)`.
5. Go to the **Actions** tab → "Build Site Library" → **Run workflow** to
   trigger the first build manually (don't wait for the daily cron).
6. Visit `https://<your-username>.github.io/<repo-name>/` — your library is
   live.

## Customizing

- **Shelf size** — change `SHELF_SIZE` near the top of the `<script>` in
  `index.html` to fit more or fewer spines per shelf.
- **Spine colors** — edit the `SPINE_COLORS` array in `index.html`.
- **Refresh schedule** — edit the `cron` line in
  `.github/workflows/build-library.yml` (currently once a day at 06:00 UTC).
- **Private repos** — the built-in `GITHUB_TOKEN` only sees Pages config for
  **public** repos. To include private ones, add a personal access token
  with `repo` scope as a repository secret and reference it in the workflow
  instead of `secrets.GITHUB_TOKEN`.
