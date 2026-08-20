#!/bin/bash
# weekly_permit_ingest.sh — Sunday auto-ingest of the freshest nightly pulls.
# Confidence gating + anomaly cap live in weekly_ingest_driver.py (which wraps
# permit_pull.ingest — the only filter/geocode engine). This script owns:
# input freshness, git, deploy verification, Discord, ingest_log.txt.
# DISCORD_WEBHOOK_URL comes from the launchd plist env — never hardcode.
set -u

REPO=/Users/tegaumukoro/heights-map
ZIPS="77008 77009 77007"
SITE="https://tangerine-sorbet-eca5f5.netlify.app"
LOG="$REPO/pulls/ingest_log.txt"
TODAY=$(date +%Y-%m-%d)

discord() {
    [ -z "${DISCORD_WEBHOOK_URL:-}" ] && { echo "discord (not configured): $1"; return; }
    python3 - "$1" <<'PY'
import json, os, sys, urllib.request
req = urllib.request.Request(os.environ['DISCORD_WEBHOOK_URL'],
    data=json.dumps({'content': sys.argv[1][:1900]}).encode(),
    headers={'Content-Type': 'application/json'})
try:
    urllib.request.urlopen(req, timeout=20)
except Exception as e:
    print(f'discord post failed: {e}', file=sys.stderr)
PY
}

fail() {
    echo "$TODAY, FAIL, $1" >> "$LOG"
    discord "🚨 Heights weekly ingest FAILED: $1"
    exit 1
}

source "$HOME/insp-venv/bin/activate" || { echo "$TODAY, FAIL, venv" >> "$LOG"; exit 1; }
cd "$REPO" || exit 1
git pull --ff-only >/dev/null 2>&1 || fail "git pull --ff-only"

# --- newest pull per zip; all three must exist and be < 8 days old ---
if date -v-1d >/dev/null 2>&1; then MINDATE=$(date -v-8d +%Y%m%d)
else MINDATE=$(date -d '8 days ago' +%Y%m%d); fi
INPUTS=""
for Z in $ZIPS; do
    NEWEST=$(ls pulls/permits_${Z}_*.csv 2>/dev/null | sort | tail -1)
    [ -z "$NEWEST" ] && fail "no pull CSV for $Z"
    FDATE=$(basename "$NEWEST" .csv | awk -F_ '{print $NF}')
    [ "$FDATE" -ge "$MINDATE" ] 2>/dev/null || fail "stale pull for $Z ($NEWEST)"
    INPUTS="$INPUTS $NEWEST"
done

# --- classify + confidence-gated apply (driver enforces the 15-row cap) ---
python3 weekly_ingest_driver.py $INPUTS
RC=$?
REPORT=$(cat pulls/ingest_report.txt 2>/dev/null || echo "no report produced")
if [ "$RC" -eq 3 ]; then
    echo "$TODAY, CAP_TRIPPED, applied=0" >> "$LOG"
    discord "@here $REPORT"
    exit 3
elif [ "$RC" -ne 0 ]; then
    fail "driver exit $RC"
fi

APPLIED=$(python3 -c "import json;print(len(json.load(open('pulls/ingest_summary.json'))['applied']))")
QUAR=$(python3 -c "import json;print(len(json.load(open('pulls/ingest_summary.json'))['quarantined']))")

if [ "$APPLIED" -gt 0 ]; then
    # commit ONLY the standard refresh files — never git add -A
    git add index.html heights_permits.json
    git commit -m "heights: weekly auto-ingest $TODAY — $APPLIED pin(s), $QUAR quarantined" \
        || fail "git commit"
    git push >/dev/null 2>&1   # auto-push hook usually already pushed; no-op then
    # --- post-deploy check: new proj numbers must appear in live DATA ---
    PROJS=$(python3 -c "import json;print(' '.join(a['proj'] for a in json.load(open('pulls/ingest_summary.json'))['applied']))")
    DEPLOY=FAIL
    for i in 1 2 3 4 5 6 7 8 9 10; do
        sleep 60
        LIVE=$(curl -fsm 30 "$SITE/index.html?cb=$(date +%s)" 2>/dev/null)
        OK=1
        for P in $PROJS; do echo "$LIVE" | grep -q "$P" || OK=0; done
        [ "$OK" -eq 1 ] && { DEPLOY=OK; break; }
    done
    if [ "$DEPLOY" != OK ]; then
        echo "$TODAY, DEPLOY_MISMATCH, applied=$APPLIED quarantined=$QUAR" >> "$LOG"
        discord "🚨 Heights weekly ingest: committed $APPLIED pin(s) but live site does NOT show them after 10 min. Check Netlify. $REPORT"
        exit 1
    fi
fi

echo "$TODAY, OK, applied=$APPLIED quarantined=$QUAR" >> "$LOG"
discord "$REPORT"
exit 0
