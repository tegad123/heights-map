# Heights Map — where the jobs actually run

The live site is Netlify (`tangerine-sorbet-eca5f5.netlify.app`). It
rebuilds from GitHub `main`. There is no other deploy path. A direct
Netlify upload used to replace the whole site with just the JSON files
and wipe the HTML. Do not bring that back.

Permit pulls and the Sunday ingest still run on **Tega's Mac**
(`/Users/tegaumukoro/heights-map`), using `~/insp-venv`:

| Job | When (America/Chicago) | launchd label | Script |
|---|---|---|---|
| Permit pull | every day 05:30 | `com.heightsmap.permitpull` | `nightly_permit_pull.sh` |
| Permit ingest | Sunday 07:00 | `com.heightsmap.permitingest` | `weekly_permit_ingest.sh` |
| Catch-up | hourly | `com.heightsmap.catchup` | `catchup_check.sh` |

Inspection data is different. **GitHub Actions** scrapes Houston ILMS
and commits the JSON. The Mac inspection agent is a legacy fallback,
described at the bottom. Do not run both.

`pulls/` is gitignored. Permit logs stay on the Mac. The Discord
webhook is only in the permit launchd plists (`DISCORD_WEBHOOK_URL`),
never in git.

---

## Inspections — GitHub Actions (the scheduled path)

Workflow: `.github/workflows/inspection-refresh.yml`.

It runs Monday and Thursday. GitHub cron is UTC and does not follow
daylight saving time, so one UTC hour cannot stay at 5:00 AM Central
all year. The cron is:

```
0 11 * * 1,4
```

That is **11:00 UTC**, which is:

- **5:00 AM America/Chicago** in Central Standard Time (CST, UTC−6),
  from the first Sunday in November through the second Sunday in March.
  That is the time in effect now.
- **6:00 AM America/Chicago** in Central Daylight Time (CDT, UTC−5),
  the rest of the year.

6:00 AM CDT is the summer slip. The run does not move earlier than
5:00 AM Central. The workflow sets `TZ=America/Chicago`, so the
`updated` dates written into the JSON are Houston dates either way.

You can also run it by hand: GitHub → Actions → Inspection refresh →
Run workflow. Leave the limit at `0` for a real refresh. A limit above
`0` scrapes that many permits per market and does not commit.

### What one run does

1. Checks out the repo on `ubuntu-latest` (6 hour job timeout).
2. Installs Python 3.12, Playwright, and Chromium.
3. Runs `run_and_deploy.py --no-push` for every market in that
   script's `MARKETS` list that has a permits file.
4. If the inspection JSON changed, commits those files to `main` as
   `github-actions[bot]` with the message
   `data: refresh inspections (GitHub Actions)` and pushes with the
   built-in `GITHUB_TOKEN` (`contents: write`).
5. Netlify rebuilds from that push. A push made with `GITHUB_TOKEN`
   does not start another Actions run. Netlify's GitHub hook still
   fires.

Markets and files:

- Heights → `inspections.json`
- Montrose, West U, River Oaks, Spring Branch, Timbergrove,
  Garden Oaks + Oak Forest → `inspections_<market>.json`

Spring Valley is in the list and is skipped. There is no
`springvalley_permits.json`, and `inspections_springvalley.json` is
`{}`. The job refuses to start if that file is no longer an empty
object. When a real permits file is added, the next run picks the
market up with no other change.

The Overview badge does not have its own file. It reads the newest
`updated` or `scraped_at` in that market's inspections JSON. Those
are the files the workflow commits. An empty file says **NONE ON
FILE**. Older than 10 days, the badge turns orange.

About a thousand permits are scraped, one ILMS page each. When Submit
opens the grid, a permit takes a few seconds. When the click is
swallowed, the scraper retries after five seconds and then loads the
page once more, instead of waiting twenty seconds on a grid that is
not coming. The job timeout is 6 hours, which covers a full run even
if a stretch of those retries fires. Concurrency group
`inspection-refresh` keeps a second run queued instead of overlapping
the first. `cancel-in-progress` is false: a running scrape is not
killed to start the next one.

### When it refuses to write

`scrape_inspections.py` writes a market file only when the run is
safe to publish:

- At least half of the permits it attempted were accepted. A blocked
  IP or a challenge page that misses the grid fails this and the
  existing file is left untouched.
- An empty inspection list does not replace a project that already
  has rows.
- The merged file is not allowed to collapse below half of its
  previous inspection-row count (once that count is at least 20).

The commit step checks again and will not push an empty or collapsed
file, and will not overwrite a file `main` changed while the job was
running. A failed market is not in the commit. If any market fails,
the workflow is red after it has committed the markets that passed.
If every market fails, nothing is pushed.

A one-permit smoke test (`--limit 1`, or the workflow limit input)
must not point at the live JSON if you are running it by hand on a
checkout you might commit. One fresh project makes the badge's newest
date look like today. The workflow's non-zero limit does not commit.

### What you have to allow on GitHub

The workflow asks for `permissions: contents: write`. That is enough
only if the repository lets Actions write:

- Settings → Actions → General → Workflow permissions → **Read and
  write permissions**. If this stays on "Read repository contents",
  the token cannot push and the scrape will fail at the commit step.
- If `main` has branch protection or a ruleset that blocks direct
  pushes, let `github-actions[bot]` push to `main` (a bypass for that
  actor). The data commit is a push, not a pull request.
- Actions has to be enabled for the repository. The schedule runs
  only after this workflow file is on `main`.

No new secret is required. The job does not post to Discord.

### How to tell the site is honest

Overview shows two dates:

- **FORECAST · AS OF** — today in America/Chicago. The supply curve is
  computed from today's date. It is not an inspection timestamp.
- **INSPECTIONS · AS OF** — the newest `updated` / `scraped_at` in that
  market's inspections file. If that date is more than 10 days old the
  badge turns orange and a warning is shown. An empty file (Spring
  Valley) says **NONE ON FILE** instead of inventing a date.

Permit ingest moving does not move the inspection date. The Actions
run log is the inspection log. A green run with "Inspection JSON
unchanged" means ILMS was reached and the file already matched.

---

## HAR sold comps and active listings

Heights stays on its own scripts (`active_ingest.py`, `sold_ingest.py`).
Do not point those at a multi-market export.

Every other live market, including Spring Valley Village, is one command.
The two CSVs are the address-led HAR export (no separate single/split
files). The command assigns each row by the market boundary, or by the
coordinate box where a market has no boundary (West University). It
keeps year built 2025 or later and lots of at least 2,200 sqft. Lots of
4,000 sqft or more are Single Lot. Lots of 2,200 to 3,999 are Split Lot.
Pending rows are tagged pending. They are not Off Market and they are
not sold comps.

Dry run, then apply:

```bash
python3 har_refresh.py \
  --active markets_active.csv \
  --sold markets_sold.csv \
  --as-of 2026-11-12
python3 har_refresh.py \
  --active markets_active.csv \
  --sold markets_sold.csv \
  --as-of 2026-11-12 \
  --apply
```

`--market montrose` limits the write to one market. `--market heights`
is refused. The raw CSVs stay out of git. Dropped rows go to
`pulls/dropped_har_<date>.csv`, which is gitignored. Apply writes, per
market, `<market>_active.data.json`, `<market>_sold.data.json`, and
`<market>_market_status.data.json`. The map page reads those. It does
not rewrite DATA or RECONCILE.

Spring Valley's ring is the Census city limit (GEOID 4869830), not all
of 77024. It is still excluded from the permit ingest until
`springvalley_permits.json` exists.

## Legacy fallback — Mac launchd / cron

Use this only if GitHub-hosted runners cannot reach ILMS. While the
Actions workflow is on and scheduled, this Mac job has to be **off**.
Two writers will overwrite each other's inspection commits.

Scripts kept on purpose:

- `inspection_refresh.sh` — scrape, commit, push. Hardcoded to
  `/Users/tegaumukoro/heights-map`.
- `install_inspection_launchd.sh` — installs
  `com.heightsmap.inspections` from
  `launchd/com.heightsmap.inspections.plist`.
- `catchup_check.sh` — can retry a missed Monday/Thursday slot on
  Tuesday or Friday morning, but only when `INSPECTION_LEGACY_MAC=1`
  is set in that agent's environment. Leave the variable unset so the
  hourly permit catch-up does not also start a scrape.

The retired path is the Mac Mini crontab
(`/Users/spencer/jarvis/inspections`, Monday/Thursday 05:00). Those
commits stopped on 28 Sep 2026. Do not turn that crontab back on.

### Install the Mac fallback (only if Actions is not the scheduler)

```bash
cd /Users/tegaumukoro/heights-map
git pull --ff-only
source ~/insp-venv/bin/activate
python3 -c "import playwright"
playwright install chromium
bash install_inspection_launchd.sh
sudo systemsetup -gettimezone    # must print America/Chicago
```

`install_inspection_launchd.sh` copies the plist into
`~/Library/LaunchAgents/` and fills `DISCORD_WEBHOOK_URL` from the
permit-ingest plist. It does not print the webhook. It aborts unless
the checkout is `/Users/tegaumukoro/heights-map`.

launchd fires Monday and Thursday at 05:00 **local** time. It does
not read `TZ` for the schedule, so the Mac's own timezone has to be
Central. The script still exports `TZ=America/Chicago` so the scrape
dates are Houston dates.

To also retry a slept-through slot, add `INSPECTION_LEGACY_MAC` =
`1` to `com.heightsmap.catchup`. Then unload the Actions schedule
(disable the workflow) before the next Monday or Thursday.

Unload the agent when Actions takes the job back:

```bash
launchctl bootout gui/$(id -u)/com.heightsmap.inspections
```

### Smoke one permit from a checkout, without committing

```bash
source ~/insp-venv/bin/activate
cd /Users/tegaumukoro/heights-map
python3 scrape_inspections.py --permits heights_permits.json \
    --out /tmp/insp-smoke.json --limit 1
```

A line like `Passed` or `Partial`, plus `PUBLISH_CHECK ok=true`,
means ILMS answered. If the check says `partial-` or `REFUSING to
write`, the output file was not written.

### Playwright, if the venv is new

```bash
python3 -m venv ~/insp-venv
source ~/insp-venv/bin/activate
pip install playwright
playwright install chromium
```

The nightly permit pull imports Playwright from this same venv.
