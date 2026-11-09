#!/usr/bin/env python3
"""
run_and_deploy.py
=====================================================================
Refreshes every market's inspections JSON from Houston ILMS.

The scheduled run is GitHub Actions
(.github/workflows/inspection-refresh.yml), Monday and Thursday at
11:00 UTC. That workflow calls this script with --no-push and commits
the JSON itself. Netlify CI rebuilds from the push to main.

inspection_refresh.sh and install_inspection_launchd.sh are the legacy
Mac fallback. They call this script without --no-push, so the script
still commits and pushes when invoked that way. SETUP.md is the
operator doc.

Spring Valley is in MARKETS but has no springvalley_permits.json.
That market is skipped and inspections_springvalley.json is left
alone (it is an empty object). The run refuses to continue if that
placeholder is no longer empty.
=====================================================================
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SCRAPER = os.path.join(HERE, "scrape_inspections.py")

# Each market: which permit list feeds it and which inspections file it
# writes (committed to git and served by Netlify at /<basename>). The
# scraper skips any market whose permit file doesn't exist yet.
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
    {"name": "gardenoaksoakforest",
     "permits": os.path.join(HERE, "gardenoaksoakforest_permits.json"),
     "out":     os.path.join(HERE, "inspections_gardenoaksoakforest.json")},
]


def file_sha(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return ""


def newest_stamp(path):
    """Newest per-project scrape date stored in an inspections file."""
    try:
        with open(path) as f:
            data = json.load(f)
    except Exception:
        return ""
    stamps = []
    if isinstance(data, dict):
        for rec in data.values():
            if not isinstance(rec, dict):
                continue
            stamp = rec.get("updated") or rec.get("scraped_at") or ""
            if isinstance(stamp, str) and stamp:
                stamps.append(stamp)
    return max(stamps) if stamps else ""


def classify_market(permits_exist, returncode, changed, newest, today):
    """Return (status, reason) for one market.

    A missing permits file is a skip, not a failure. Spring Valley is
    that case: inspections_springvalley.json stays {}. A scrape that
    exits 0 but leaves a stale file unchanged did not reach ILMS.
    """
    if not permits_exist:
        return "SKIP", "no-permits-file"
    if returncode != 0:
        return "FAIL", f"exit-{returncode}"
    if changed:
        return "OK", "updated"
    if newest == today:
        return "OK", "already-fresh"
    return "FAIL", "unchanged-stale"


def spring_valley_placeholder_ok():
    """Spring Valley stays {} until springvalley_permits.json exists."""
    permits = os.path.join(HERE, "springvalley_permits.json")
    out = os.path.join(HERE, "inspections_springvalley.json")
    if os.path.exists(permits):
        return True
    try:
        with open(out) as f:
            return json.load(f) == {}
    except Exception:
        return False


def run_scraper(market, limit, today):
    """Run the Playwright scraper for one market.

    Returns (status, reason, newest). Does not write a market whose
    permits file is missing.
    """
    if not os.path.exists(market["permits"]):
        print(f"[{market['name']}] permit file missing ({os.path.basename(market['permits'])}); "
              f"leaving {os.path.basename(market['out'])} untouched.")
        return classify_market(False, 0, False, "", today) + (newest_stamp(market["out"]),)

    before = file_sha(market["out"])
    cmd = [sys.executable, SCRAPER, "--permits", market["permits"], "--out", market["out"]]
    if limit:
        cmd += ["--limit", str(limit)]
    print(f"[{market['name']}] running scraper:", " ".join(cmd), "\n")
    result = subprocess.run(cmd)
    newest = newest_stamp(market["out"])
    changed = file_sha(market["out"]) != before
    status, reason = classify_market(True, result.returncode, changed, newest, today)
    print(f"[{market['name']}] {status} {reason} newest={newest or '-'}")
    return status, reason, newest


def deploy_git(markets):
    """Commit + push these markets' inspection files. Netlify rebuilds.

    Only the named JSON files are committed, even if something else is
    staged. Refuses to push from any branch other than main.
    """
    branch = subprocess.check_output(
        ["git", "-C", HERE, "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()
    if branch != "main":
        raise SystemExit(f"Refusing to push inspection data from branch {branch}.")

    rels = [os.path.basename(m["out"]) for m in markets if os.path.exists(m["out"])]
    if not rels:
        print("Nothing to commit (data unchanged).")
        return
    subprocess.run(["git", "-C", HERE, "add", "--"] + rels, check=True)
    staged = subprocess.run(["git", "-C", HERE, "diff", "--cached", "--quiet", "--"] + rels)
    if staged.returncode == 0:
        print("Nothing to commit (data unchanged).")
        return
    msg = "data: refresh inspections (all markets)"
    subprocess.run(["git", "-C", HERE, "commit", "-m", msg, "--"] + rels, check=True)
    subprocess.run(["git", "-C", HERE, "push"], check=True)
    print("Pushed inspection files to GitHub — Netlify will rebuild.")


def main():
    known = [m["name"] for m in MARKETS]
    ap = argparse.ArgumentParser(description="Scrape inspections then auto-deploy")
    ap.add_argument("--mode", choices=["git"], default="git",
                    help="git = commit+push; Netlify CI rebuilds from the push")
    ap.add_argument("--limit", type=int, default=0,
                    help="Only scrape first N permits (testing). Does not commit or push.")
    ap.add_argument("--no-push", action="store_true",
                    help="Scrape and validate, but do not commit or push. "
                         "GitHub Actions commits the JSON itself.")
    ap.add_argument("--skip-scrape", action="store_true",
                    help="Deploy existing inspection files without re-scraping")
    ap.add_argument("--market", default="",
                    help="Only run one market. Default = all. Known: " + ",".join(known))
    args = ap.parse_args()

    markets = MARKETS
    if args.market:
        markets = [m for m in MARKETS if m["name"] == args.market]
        if not markets:
            sys.exit(f"Unknown --market {args.market}; known: {known}")

    if not spring_valley_placeholder_ok():
        print("INSPECTION_RESULT market=springvalley status=FAIL "
              "reason=placeholder-not-empty newest=-")
        print("inspections_springvalley.json is not {} and "
              "springvalley_permits.json does not exist. Refusing to scrape.")
        sys.exit(1)

    today = date.today().isoformat()
    ready = []
    failed = False
    produced = False

    if args.skip_scrape:
        for m in markets:
            if os.path.exists(m["permits"]) and os.path.exists(m["out"]):
                ready.append(m)
                produced = True
                print(f"INSPECTION_RESULT market={m['name']} status=OK reason=skip-scrape "
                      f"newest={newest_stamp(m['out']) or '-'}")
            elif not os.path.exists(m["permits"]):
                print(f"INSPECTION_RESULT market={m['name']} status=SKIP reason=no-permits-file "
                      f"newest={newest_stamp(m['out']) or '-'}")
            else:
                failed = True
                print(f"INSPECTION_RESULT market={m['name']} status=FAIL reason=missing-out newest=-")
    else:
        for m in markets:
            status, reason, newest = run_scraper(m, args.limit, today)
            print(f"INSPECTION_RESULT market={m['name']} status={status} reason={reason} "
                  f"newest={newest or '-'}")
            if status == "OK":
                ready.append(m)
                produced = True
            elif status == "FAIL":
                failed = True

    if not spring_valley_placeholder_ok():
        print("INSPECTION_RESULT market=springvalley status=FAIL "
              "reason=placeholder-changed newest=-")
        print("inspections_springvalley.json changed without a permits file. "
              "Refusing to publish.")
        sys.exit(1)

    if args.limit or args.no_push:
        if args.limit:
            print("Limit run: inspection files may have been updated on disk. Not committing.")
        else:
            print("No-push run: not committing. The caller commits inspection JSON.")
        if failed:
            sys.exit(2)
        if not produced:
            sys.exit(1)
        return

    if not produced and failed:
        print("No market produced valid data; nothing to deploy.")
        sys.exit(1)
    if not produced:
        print("No market produced valid data; nothing to deploy.")
        sys.exit(1)

    try:
        deploy_git(ready)
    except subprocess.CalledProcessError as exc:
        print(f"INSPECTION_RESULT market=- status=FAIL reason=git-{' '.join(exc.cmd)}")
        sys.exit(1)
    if failed:
        sys.exit(2)


if __name__ == "__main__":
    main()
