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
INSPECTIONS_FILE = os.path.join(HERE, "inspections.json")
PERMITS_FILE = os.path.join(HERE, "heights_permits.json")
SCRAPER = os.path.join(HERE, "scrape_inspections.py")

# Read from env first; fall back to inline (leave blank and use env in prod).
NETLIFY_SITE_ID = os.environ.get("NETLIFY_SITE_ID", "")
NETLIFY_TOKEN = os.environ.get("NETLIFY_TOKEN", "")


def run_scraper(limit):
    """Run the Playwright scraper; it writes/merges inspections.json."""
    cmd = [
        sys.executable, SCRAPER,
        "--permits", PERMITS_FILE,
        "--out", INSPECTIONS_FILE,
    ]
    if limit:
        cmd += ["--limit", str(limit)]
    print("Running scraper:", " ".join(cmd), "\n")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print("Scraper exited non-zero; deploying whatever data exists anyway.")
    # sanity check the file is valid JSON before we deploy it
    try:
        data = json.load(open(INSPECTIONS_FILE))
        print(f"\ninspections.json holds {len(data)} permits — ready to deploy.")
        return True
    except Exception as e:
        print(f"inspections.json is missing or invalid ({e}); aborting deploy.")
        return False


def deploy_netlify():
    """Upload only inspections.json to the live site via Netlify's API.

    Uses the file-digest deploy endpoint: we tell Netlify the SHA1 of
    the one file we want live, it tells us if it needs the bytes, we PUT
    them. This updates a single file without touching the rest of the
    deployed site.
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
    blob = open(INSPECTIONS_FILE, "rb").read()
    sha = hashlib.sha1(blob).hexdigest()
    headers = {"Authorization": f"Bearer {NETLIFY_TOKEN}"}

    # 1) create a deploy that declares the file we intend to ship
    base = f"https://api.netlify.com/api/v1/sites/{NETLIFY_SITE_ID}"
    r = requests.post(
        f"{base}/deploys",
        headers={**headers, "Content-Type": "application/json"},
        json={"files": {"/inspections.json": sha}},
        timeout=60,
    )
    r.raise_for_status()
    deploy = r.json()
    deploy_id = deploy["id"]

    # 2) if Netlify still needs the bytes, PUT them
    required = deploy.get("required") or []
    if sha in required:
        up = requests.put(
            f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files/inspections.json",
            headers={**headers, "Content-Type": "application/octet-stream"},
            data=blob,
            timeout=120,
        )
        up.raise_for_status()
        print("Uploaded inspections.json bytes to Netlify.")
    else:
        print("Netlify already had this exact file (no change to upload).")

    print(f"Deployed inspections.json — deploy id {deploy_id}")
    print(f"Live URL: {deploy.get('ssl_url') or deploy.get('url','(check dashboard)')}")


def deploy_git():
    """Commit + push inspections.json; Netlify's GitHub integration rebuilds."""
    subprocess.run(["git", "-C", HERE, "add", "inspections.json"], check=True)
    msg = "data: refresh inspections.json"
    r = subprocess.run(["git", "-C", HERE, "commit", "-m", msg])
    if r.returncode != 0:
        print("Nothing to commit (data unchanged).")
        return
    subprocess.run(["git", "-C", HERE, "push"], check=True)
    print("Pushed inspections.json to GitHub — Netlify will rebuild.")


def main():
    ap = argparse.ArgumentParser(description="Scrape inspections then auto-deploy")
    ap.add_argument("--mode", choices=["netlify", "git"], default="netlify",
                    help="netlify = direct API upload (no rebuild); git = commit+push")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only scrape first N permits (testing). 0 = all")
    ap.add_argument("--skip-scrape", action="store_true",
                    help="Deploy the existing inspections.json without re-scraping")
    args = ap.parse_args()

    if not args.skip_scrape:
        if not run_scraper(args.limit):
            sys.exit(1)

    if args.mode == "netlify":
        deploy_netlify()
    else:
        deploy_git()


if __name__ == "__main__":
    main()
