#!/usr/bin/env python3
"""
run_and_deploy.py
=====================================================================
The hands-off inspections updater. Runs on any machine that has the
repo cloned and git push access — no specific host.

It does two things, in order, with zero manual steps:
  1. Runs scrape_inspections.py to refresh each market's inspections
     JSON from the Houston Permitting Center.
  2. Commits the fresh inspection files and pushes to GitHub main.
     The site is hosted on Netlify and rebuilds from main via CI, so
     the push is the whole deploy — there is no other path.

The map code and the inspection DATA both live in git and ship the
same way: push to main, Netlify CI rebuilds. Data refreshes add a
"data: refresh inspections" commit each run; that is expected.

---------------------------------------------------------------------
ONE-TIME SETUP (any machine with the repo cloned)
---------------------------------------------------------------------
1. You already have the venv from the scraper:
       source ~/insp-venv/bin/activate

2. Clone the repo on that machine with git push auth set up (the push
   in step 4 must succeed non-interactively for cron).

3. Test it once by hand:
       source ~/insp-venv/bin/activate
       python3 run_and_deploy.py --limit 5      # scrape 5, commit+push
   Watch the output. If it says "Pushed inspection files to GitHub",
   Netlify CI will rebuild from main.

4. Schedule it (cron, every Mon/Thu at 5am):
       crontab -e
   add:
       0 5 * * 1,4  cd /Users/spencer/jarvis/inspections && \
                    /Users/spencer/insp-venv/bin/python run_and_deploy.py \
                    >> deploy.log 2>&1

After that you never touch it. Scrape -> push -> Netlify rebuilds. Done.
=====================================================================
"""

import argparse
import os
import subprocess
import sys
import json

HERE = os.path.dirname(os.path.abspath(__file__))
SCRAPER = os.path.join(HERE, "scrape_inspections.py")

# Each market: which permit list feeds it and which inspections file it
# writes (committed to git and served by Netlify at /<basename>). New
# markets are one entry each; the scraper skips any market whose permit
# file doesn't exist yet.
MARKETS = [
    {"name": "heights",
     "permits": os.path.join(HERE, "heights_permits.json"),
     "out":     os.path.join(HERE, "inspections.json")},
    {"name": "montrose",
     "permits": os.path.join(HERE, "montrose_permits.json"),
     "out":     os.path.join(HERE, "inspections_montrose.json")},
    {"name": "westu",
     "permits": os.path.join(HERE, "westu_permits.json"),
     "out":     os.path.join(HERE, "inspections_westu.json")},
    {"name": "riveroaks",
     "permits": os.path.join(HERE, "riveroaks_permits.json"),
     "out":     os.path.join(HERE, "inspections_riveroaks.json")},
    {"name": "springbranch",
     "permits": os.path.join(HERE, "springbranch_permits.json"),
     "out":     os.path.join(HERE, "inspections_springbranch.json")},
    {"name": "springvalley",
     "permits": os.path.join(HERE, "springvalley_permits.json"),
     "out":     os.path.join(HERE, "inspections_springvalley.json")},
    {"name": "timbergrove",
     "permits": os.path.join(HERE, "timbergrove_permits.json"),
     "out":     os.path.join(HERE, "inspections_timbergrove.json")},
]

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
    ap.add_argument("--mode", choices=["git"], default="git",
                    help="git = commit+push; Netlify CI rebuilds from the push")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only scrape first N permits (testing). 0 = all")
    ap.add_argument("--skip-scrape", action="store_true",
                    help="Deploy existing inspection files without re-scraping")
    ap.add_argument("--market", default="",
                    help="Only run one market (heights|montrose|westu|riveroaks|springbranch|springvalley|timbergrove). Default = all.")
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

    deploy_git(markets)


if __name__ == "__main__":
    main()
