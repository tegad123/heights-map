# Heights Map — Auto-Deploy Setup

Goal: stop manually re-uploading. After this, you `git push` to update the
map, and the Mac Mini pushes inspection data on its own. You never drag a
file into Netlify again.

Everything ships the same way — a push to GitHub `main`. The site is
hosted on Netlify and rebuilds from `main` via CI, so there is one path:

- **Map code (index.html)** → commit + push → Netlify CI rebuilds.
- **Inspection data (inspections.json + per-market files)** → the Mac Mini
  scraper commits and pushes them → Netlify CI rebuilds.

(There used to be a direct Netlify-API upload for data. It has been
removed — it replaced the whole site with just the JSON files and wiped
everything else. Do not reintroduce it. Push to `main` is the only deploy.)

---

## PART 1 — Put the map on GitHub + connect Netlify (one time, ~10 min)

### 1. Create the repo
On github.com → New repository → name it `heights-map` → Private → Create.
Don't add a README (we have files already).

### 2. Push these files up
On your computer, in this folder (the one with `index.html`):

```bash
git init
git add .
git commit -m "Heights map + inspections pipeline"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/heights-map.git
git push -u origin main
```

### 3. Point your EXISTING Netlify site at the repo
You already have the site (`splendorous-basbousa-9270fc`). Connect it to Git
so it stops being a manual-upload site:

- Netlify dashboard → your site → **Site configuration** → **Build & deploy**
  → **Continuous deployment** → **Link repository**.
- Choose GitHub → authorize → pick `heights-map`.
- Branch to deploy: `main`. Build command: leave blank. Publish directory: `.`
- Save.

(If Netlify won't let you link a repo to the existing site, just create a new
site from the repo — "Add new site" → "Import an existing project" → GitHub →
`heights-map`. Then update your bookmarked URL, or set the custom domain on the
new site so the link stays the same.)

### 4. Done with manual uploads for the map
From now on: edit `index.html`, then:
```bash
git add index.html && git commit -m "map update" && git push
```
Netlify rebuilds in ~30s. Refresh the live URL. That's it.

---

## PART 2 — Make the Mac Mini auto-deploy inspection data (one time, ~10 min)

This is what makes the every-few-days scrape land on the live site by itself.

### 1. Put the scraper files on the Mac Mini
Copy `scrape_inspections.py`, `heights_permits.json`, and `run_and_deploy.py`
into a folder, e.g. `/Users/spencer/jarvis/inspections/`.

### 2. Python env (if not already done for the scraper)
```bash
python3 -m venv ~/insp-venv
source ~/insp-venv/bin/activate
pip install playwright
playwright install chromium
```

### 3. Clone the repo with push access
The scraper commits and pushes, so the Mac Mini needs the repo cloned and
git push auth set up to work non-interactively (SSH key or a cached
credential helper) — cron cannot answer a password prompt.
```bash
git clone git@github.com:YOUR_USERNAME/heights-map.git /Users/spencer/jarvis/inspections
```

### 4. Test it once
```bash
source ~/insp-venv/bin/activate
cd /Users/spencer/jarvis/inspections
python3 run_and_deploy.py --limit 5
```
Watch for `Pushed inspection files to GitHub`. Netlify CI rebuilds from
`main` in ~30s; then open the live map — the header badge should read green
"● inspections: N permits live". If it does, the whole pipeline works.

### 5. Schedule it (every Mon & Thu, 5am)
```bash
crontab -e
```
add this line (fix the paths to match where you put things):
```
0 5 * * 1,4  cd /Users/spencer/jarvis/inspections && /Users/spencer/insp-venv/bin/python run_and_deploy.py >> deploy.log 2>&1
```

Save. From now on the Mac Mini scrapes Houston's inspection records twice a
week and pushes them to the live map automatically. You do nothing.

---

## How to tell it's working
- Live map header shows green "● inspections: N permits live".
- Permit popups show the **Inspections** box with passed/failed/pending rows.
- Permits with passed inspections move out of the gray "New Construction"
  layer into the right Under-Construction phase on their own.
- `deploy.log` on the Mac Mini shows each run's results.

## If the badge says "feed not loaded"
- The map (index.html) and inspections.json must both be live on the same site.
  After Part 1 they will be. Until the first scrape runs, the committed
  inspections.json (sample data) is what shows — that's fine.
- Check the browser console (right-click → Inspect → Console) for the
  `[inspections]` log line; it says exactly what loaded or why it failed.

## Deploy path
Data is versioned in git and Netlify rebuilds on each push — this is the
only path. `git` is the default mode; `--mode git` is accepted but
redundant. Requires the repo cloned on the Mac Mini with push access.
