# Heights Map — where the jobs actually run

The live site is Netlify. It rebuilds from GitHub `main`. There is no
other deploy path. A direct Netlify upload used to replace the whole
site with just the JSON files and wipe the HTML. Do not bring that back.

Two different schedules commit to this repo, both from **Tega's Mac**
(`/Users/tegaumukoro/heights-map`), both using `~/insp-venv`:

| Job | When (America/Chicago) | launchd label | Script |
|---|---|---|---|
| Permit pull | every day 05:30 | `com.heightsmap.permitpull` | `nightly_permit_pull.sh` |
| Permit ingest | Sunday 07:00 | `com.heightsmap.permitingest` | `weekly_permit_ingest.sh` |
| Catch-up | hourly | `com.heightsmap.catchup` | `catchup_check.sh` |
| **Inspections** | **Monday and Thursday 05:00** | `com.heightsmap.inspections` | `inspection_refresh.sh` |

The Mac Mini path in older notes (`/Users/spencer/jarvis/inspections`,
user crontab) is retired. Inspection commits ran on that old schedule
through 28 Sep 2026 and then stopped, while the permit launchd jobs on
Tega's Mac kept committing. The inspection scrape was never moved onto
the launchd setup.

Git identity on the permit jobs is "Tega Umukoro". The retired inspection
cron committed as `tegad123`. After this job is installed, inspection
commits come from the same checkout as the permit jobs.

`pulls/` is gitignored. Logs stay on the Mac. The Discord webhook is
only in the launchd plists (`DISCORD_WEBHOOK_URL`), never in git.

---

## Install the inspection job (once, on Tega's Mac)

The permit venv is already there if the nightly pull runs. Chromium
still has to be installed for Playwright.

```bash
cd /Users/tegaumukoro/heights-map
git pull --ff-only
source ~/insp-venv/bin/activate
python3 -c "import playwright"
playwright install chromium
bash install_inspection_launchd.sh
sudo systemsetup -gettimezone    # must print America/Chicago
```

`install_inspection_launchd.sh` copies
`launchd/com.heightsmap.inspections.plist` into
`~/Library/LaunchAgents/com.heightsmap.inspections.plist` and fills
`DISCORD_WEBHOOK_URL` from the existing permit-ingest plist. It does
not print the webhook. It aborts if this checkout is not
`/Users/tegaumukoro/heights-map`, because the permit scripts hardcode
that path and the inspection job has to commit the same clone.

The agent fires Monday and Thursday at 05:00 **local** time. launchd
does not read the `TZ` variable for the schedule, so the Mac's own
timezone has to be Central. The script still exports `TZ=America/Chicago`
so the scrape dates written into the JSON are Houston dates.

If the lid is closed at 05:00, `catchup_check.sh` runs the scrape on
Tuesday or Friday before noon. It will not start a second copy while
the first is still running.

### Smoke one permit without touching the repo

```bash
source ~/insp-venv/bin/activate
cd /Users/tegaumukoro/heights-map
python3 scrape_inspections.py --permits heights_permits.json \
    --out /tmp/insp-smoke.json --limit 1
```

A line like `Passed` or `Partial` plus `SCRAPE_SUMMARY ... updated=1`
means ILMS answered. Do not point `--out` at `inspections.json` for a
one-permit test. A partial file would make the map look current.

### Run the real job once by hand

This scrapes every market, commits, and pushes `main`:

```bash
bash /Users/tegaumukoro/heights-map/inspection_refresh.sh
```

The checkout must be on `main` with a clean fast-forward. Expect this
to take a while (about a thousand permits).

---

## What the job scrapes

`run_and_deploy.py` walks its MARKETS list. A market is scraped only
when its permits file exists:

- Heights → `inspections.json`
- Montrose, West U, River Oaks, Spring Branch, Timbergrove,
  Garden Oaks + Oak Forest → `inspections_<market>.json`

Spring Valley is in that list and is skipped. There is no
`springvalley_permits.json`, and `inspections_springvalley.json` is
`{}`. The job refuses to start if that file is no longer an empty
object. When a real permits file is added, the next run picks the
market up with no other change.

A market whose scrape does not change a stale file (ILMS never
returned) is a failure. Discord gets the `INSPECTION_RESULT` lines.
Successes still commit. The log line is `pulls/inspection_log.txt`.

---

## How to tell the site is honest

Overview shows two dates:

- **FORECAST · AS OF** — today in America/Chicago. The supply curve is
  computed from today's date. It is not an inspection timestamp.
- **INSPECTIONS · AS OF** — the newest `updated` / `scraped_at` in that
  market's inspections file. If that date is more than 10 days old the
  badge turns orange and a warning is shown. An empty file (Spring
  Valley) says **NONE ON FILE** instead of inventing a date.

Permit ingest moving does not move the inspection date.

---

## Playwright, if the venv is new

```bash
python3 -m venv ~/insp-venv
source ~/insp-venv/bin/activate
pip install playwright
playwright install chromium
```

The nightly permit pull imports Playwright from this same venv. `pip
install` is only needed when the venv itself is missing.
