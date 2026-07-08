#!/usr/bin/env python3
"""
run_and_deploy.py
=====================================================================
The hands-off updater that lives on the Mac Mini.

It does two things, in order, with zero manual steps:
  1. Runs scrape_inspections.py to refresh inspections.json from the
     Houston Permitting Center.
  2. Pushes the fresh inspections.json straight to your live Netlify
     site via the Netlify API — NO git commit, NO full rebuild, no
     re-upload. The map sees the new data on its next 6-hour refresh
     (or whenever someone reloads).

This is the "clean" architecture: your map code lives in GitHub and
deploys on your pushes; the every-few-days DATA refresh goes directly
to Netlify so it doesn't spam your git history with "data update"
commits or trigger a rebuild each time.

---------------------------------------------------------------------
ONE-TIME SETUP ON THE MAC MINI
---------------------------------------------------------------------
1. You already have the venv from the scraper:
       source ~/insp-venv/bin/activate
       pip install requests          # (scraper already needs playwright)

2. Get two values from Netlify and put them in this script (or, better,
   in environment variables so they're not sitting in a file):

   NETLIFY_SITE_ID  - Netlify dashboard -> your site -> Site configuration
                      -> "Site ID" (looks like a UUID).
   NETLIFY_TOKEN    - Netlify -> User settings -> Applications ->
                      "Personal access tokens" -> New access token.
                      Scope it to this one site if you can.

   Set them in your shell profile (~/.zshrc) so cron picks them up:
       export NETLIFY_SITE_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
       export NETLIFY_TOKEN="nfp_xxxxxxxxxxxxxxxxxxxx"

3. Test it once by hand:
       source ~/insp-venv/bin/activate
       python3 run_and_deploy.py --limit 5      # scrape 5, deploy
   Watch the output. If it says "Deployed inspections.json", you're done.

4. Schedule it (cron, every Mon/Thu at 5am):
       crontab -e
   add:
       0 5 * * 1,4  cd /Users/spencer/jarvis/inspections && \
                    /Users/spencer/insp-venv/bin/python run_and_deploy.py \
                    >> deploy.log 2>&1

After that you never touch it. Scrape -> deploy -> map updates. Done.

---------------------------------------------------------------------
ALTERNATIVE: commit to GitHub instead of direct Netlify upload
---------------------------------------------------------------------
If you'd rather have the data versioned in git (and don't mind a
rebuild each run), pass --mode git. That stages inspections.json,
commits, and pushes; Netlify's GitHub integration rebuilds the site.
Requires the repo cloned on the Mac Mini and git push auth set up.
=====================================================================
"""

import argparse
import os
import subprocess
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SCRAPER = os.path.join(HERE, "scrape_inspections.py")

# Each market: which permit list feeds it, which inspections file it writes,
# and the path Netlify serves it at. Add West U here later — one line.
MARKETS = [
    {"name": "heights",
     "permits": os.path.join(HERE, "heights_permits.json"),
     "out":     os.path.join(HERE, "inspections.json"),
     "netlify_path": "/inspections.json"},
    {"name": "montrose",
     "permits": os.path.join(HERE, "montrose_permits.json"),
     "out":     os.path.join(HERE, "inspections_montrose.json"),
     "netlify_path": "/inspections_montrose.json"},
]

# Read from env first; fall back to inline (leave blank and use env in prod).
NETLIFY_SITE_ID = os.environ.get("NETLIFY_SITE_ID", "")
NETLIFY_TOKEN = os.environ.get("NETLIFY_TOKEN", "")


def run_scraper(market, limit):
    """Run the Playwright scraper for one market; writes/merges its out file."""
    if not os.path.exists(market["permits"]):
        print(f"[{market['name']}] permit file missing ({market['permits']}); skipping.")
        return False
    cmd = [
        sys.executable, SCRAPER,
        "--permits", market["permits"],
        "--out", market["out"],
    ]
    if limit:
        cmd += ["--limit", str(limit)]
    print(f"[{market['name']}] running scraper:", " ".join(cmd), "\n")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"[{market['name']}] scraper exited non-zero; deploying existing data anyway.")
    try:
        data = json.load(open(market["out"]))
        print(f"[{market['name']}] {os.path.basename(market['out'])} holds {len(data)} permits — ready to deploy.")
        return True
    except Exception as e:
        print(f"[{market['name']}] {os.path.basename(market['out'])} missing or invalid ({e}); skipping deploy.")
        return False


def deploy_netlify(markets):
    """Upload all markets' inspection files to the live site in ONE deploy.

    Uses the file-digest deploy endpoint: declare the SHA1 of every file
    we want live, Netlify tells us which bytes it still needs, we PUT those.
    Declaring all files in a single deploy keeps the other files on the site
    intact (a deploy that names only some files leaves the rest as-is only
    when we pass the full digest set — so we include every market's file).
    """
    try:
        import requests
    except ImportError:
        sys.exit("pip install requests  (needed for Netlify upload)")

    if not NETLIFY_SITE_ID or not NETLIFY_TOKEN:
        sys.exit(
            "NETLIFY_SITE_ID / NETLIFY_TOKEN not set.\n"
            "Set them as environment variables (see the header of this file)."
        )

    import hashlib
    headers = {"Authorization": f"Bearer {NETLIFY_TOKEN}"}
    base = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}"

    # Build the digest map for every market file that exists on disk.
    files_map = {}
    blobs = {}
    for m in markets:
        if not os.path.exists(m["out"]):
            continue
        blob = open(m["out"], "rb").read()
        sha = hashlib.sha1(blob).hexdigest()
        files_map[m["netlify_path"]] = sha
        blobs[m["netlify_path"]] = (sha, blob)
    if not files_map:
        print("No inspection files to deploy.")
        return

    r = requests.post(
        f"{base}/deploys",
        headers={**headers, "Content-Type": "application/json"},
        json={"files": files_map},
        timeout=60,
    )
    r.raise_for_status()
    deploy = r.json()
    deploy_id = deploy["id"]
    required = set(deploy.get("required") or [])

    for path, (sha, blob) in blobs.items():
        if sha in required:
            up = requests.put(
                f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files{path}",
                headers={**headers, "Content-Type": "application/octet-stream"},
                data=blob,
                timeout=120,
            )
            up.raise_for_status()
            print(f"Uploaded {path} bytes to Netlify.")
        else:
            print(f"Netlify already had current {path} (no change).")

    print(f"Deployed {len(files_map)} inspection file(s) — deploy id {deploy_id}")
    print(f"Live URL: {deploy.get('ssl_url') or deploy.get('url','(check dashboard)')}")


def deploy_git(markets):
    """Commit + push all markets' inspection files; Netlify rebuilds."""
    for m in markets:
        if os.path.exists(m["out"]):
            subprocess.run(["git", "-C", HERE, "add", os.path.basename(m["out"])], check=True)
    msg = "data: refresh inspections (all markets)"
    r = subprocess.run(["git", "-C", HERE, "commit", "-m", msg])
    if r.returncode != 0:
        print("Nothing to commit (data unchanged).")
        return
    subprocess.run(["git", "-C", HERE, "push"], check=True)
    print("Pushed inspection files to GitHub — Netlify will rebuild.")


def main():
    ap = argparse.ArgumentParser(description="Scrape inspections then auto-deploy")
    ap.add_argument("--mode", choices=["netlify", "git"], default="netlify",
                    help="netlify = direct API upload (no rebuild); git = commit+push")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only scrape first N permits (testing). 0 = all")
    ap.add_argument("--skip-scrape", action="store_true",
                    help="Deploy existing inspection files without re-scraping")
    ap.add_argument("--market", default="",
                    help="Only run one market (heights|montrose). Default = all.")
    args = ap.parse_args()

    # Optional: restrict to one market from the CLI (default = all)
    markets = MARKETS
    if args.market:
        markets = [m for m in MARKETS if m["name"] == args.market]
        if not markets:
            sys.exit(f"Unknown --market {args.market}; known: {[m['name'] for m in MARKETS]}")

    if not args.skip_scrape:
        any_ok = False
        for m in markets:
            if run_scraper(m, args.limit):
                any_ok = True
        if not any_ok:
            print("No market produced valid data; nothing to deploy.")
            sys.exit(1)

    if args.mode == "netlify":
        deploy_netlify(markets)
    else:
        deploy_git(markets)


if __name__ == "__main__":
    main()
