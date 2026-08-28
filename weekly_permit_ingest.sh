#!/bin/bash
# weekly_permit_ingest.sh — Sunday auto-ingest of the freshest nightly pulls,
# all live markets (multi-market since 2026-08-27; market_config.py is the
# single source of truth for markets/zips/zone guards).
# Confidence gating + anomaly cap live in weekly_ingest_driver.py (which wraps
# permit_pull.ingest — the only filter/geocode engine). This script owns:
# input freshness, git (per-market commits, never add -A), deploy
# verification, Discord, ingest_log.txt.
# DISCORD_WEBHOOK_URL comes from the launchd plist env — never hardcode.
set -u

REPO=/Users/tegaumukoro/heights-map
SITE="https://tangerine-sorbet-eca5f5.netlify.app"
LOG="$REPO/pulls/ingest_log.txt"
TODAY=$(date +%Y-%m-%d)

discord() {
    [ -z "${DISCORD_WEBHOOK_URL:-}" ] && { echo "discord (not configured): $1"; return; }
    python3 - "$1" <<'PY'
import json, os, sys, urllib.request
# Discord 403s the default Python-urllib User-Agent; any custom UA passes
req = urllib.request.Request(os.environ['DISCORD_WEBHOOK_URL'],
    data=json.dumps({'content': sys.argv[1][:1900]}).encode(),
    headers={'Content-Type': 'application/json',
             'User-Agent': 'heights-map-ingest/1.0'})
try:
    urllib.request.urlopen(req, timeout=20)
except Exception as e:
    print(f'discord post failed: {e}', file=sys.stderr)
PY
}

source "$HOME/insp-venv/bin/activate" || { echo "$TODAY, -, FAIL, venv" >> "$LOG"; exit 1; }
cd "$REPO" || exit 1
if ! git pull --ff-only >/dev/null 2>&1; then
    echo "$TODAY, -, FAIL, git pull --ff-only" >> "$LOG"
    discord "🚨 Weekly ingest FAILED before start: git pull --ff-only"
    exit 1
fi

if date -v-1d >/dev/null 2>&1; then MINDATE=$(date -v-8d +%Y%m%d)
else MINDATE=$(date -d '8 days ago' +%Y%m%d); fi

ANYFAIL=0
REPORT_ALL=""
CHECKS=""     # "html:proj proj ..." per changed page, for deploy verification

# market html permits_json zip,zip,... — ingest order from market_config
while read -r MK HTML PJSON ZIPCSV; do
    # --- newest pull per zip; all must exist and be < 8 days old ---
    INPUTS=""
    MISSING=""
    for Z in ${ZIPCSV//,/ }; do
        NEWEST=$(ls pulls/permits_${Z}_*.csv 2>/dev/null | sort | tail -1)
        if [ -z "$NEWEST" ]; then MISSING="no pull CSV for $Z"; break; fi
        FDATE=$(basename "$NEWEST" .csv | awk -F_ '{print $NF}')
        if ! [ "$FDATE" -ge "$MINDATE" ] 2>/dev/null; then
            MISSING="stale pull for $Z ($NEWEST)"; break
        fi
        INPUTS="$INPUTS $NEWEST"
    done
    if [ -n "$MISSING" ]; then
        ANYFAIL=1
        echo "$TODAY, $MK, FAIL, $MISSING" >> "$LOG"
        REPORT_ALL="$REPORT_ALL
🚨 $MK: SKIPPED — $MISSING"
        continue
    fi

    # --- classify + confidence-gated apply (driver enforces the 15-row cap) ---
    python3 weekly_ingest_driver.py --market "$MK" $INPUTS
    RC=$?
    REPORT=$(cat pulls/ingest_report.txt 2>/dev/null || echo "$MK: no report produced")
    if [ "$RC" -eq 3 ]; then
        ANYFAIL=1
        echo "$TODAY, $MK, CAP_TRIPPED, applied=0" >> "$LOG"
        discord "@here $REPORT"
        REPORT_ALL="$REPORT_ALL
$REPORT"
        continue
    elif [ "$RC" -ne 0 ]; then
        ANYFAIL=1
        echo "$TODAY, $MK, FAIL, driver exit $RC" >> "$LOG"
        REPORT_ALL="$REPORT_ALL
🚨 $MK: driver exit $RC"
        continue
    fi

    APPLIED=$(python3 -c "import json;print(len(json.load(open('pulls/ingest_summary.json'))['applied']))")
    QUAR=$(python3 -c "import json;print(len(json.load(open('pulls/ingest_summary.json'))['quarantined']))")

    if [ "$APPLIED" -gt 0 ]; then
        # commit ONLY this market's standard refresh files — never git add -A
        git add "$HTML" "$PJSON"
        if ! git commit -q -m "$MK: weekly auto-ingest $TODAY — $APPLIED pin(s), $QUAR quarantined"; then
            ANYFAIL=1
            echo "$TODAY, $MK, FAIL, git commit" >> "$LOG"
            REPORT_ALL="$REPORT_ALL
🚨 $MK: git commit failed"
            continue
        fi
        git push >/dev/null 2>&1   # auto-push hook usually already pushed; no-op then
        PROJS=$(python3 -c "import json;print(' '.join(a['proj'] for a in json.load(open('pulls/ingest_summary.json'))['applied']))")
        CHECKS="$CHECKS
$HTML:$PROJS"
    fi
    echo "$TODAY, $MK, OK, applied=$APPLIED quarantined=$QUAR" >> "$LOG"
    REPORT_ALL="$REPORT_ALL
$REPORT"
done < <(python3 -c "
from market_config import MARKETS, INGEST_ORDER
for mk in INGEST_ORDER:
    c = MARKETS[mk]
    if c['enabled']:
        print(mk, c['html'], c['permits_json'], ','.join(c['zips']))")

# --- post-deploy check: every applied proj must appear in its live page ---
if [ -n "$CHECKS" ]; then
    DEPLOY=FAIL
    for i in 1 2 3 4 5 6 7 8 9 10; do
        sleep 60
        OK=1
        while read -r LINE; do
            [ -z "$LINE" ] && continue
            PAGE=${LINE%%:*}
            LIVE=$(curl -fsm 30 "$SITE/$PAGE?cb=$(date +%s)" 2>/dev/null)
            for P in ${LINE#*:}; do echo "$LIVE" | grep -q "$P" || OK=0; done
        done <<< "$CHECKS"
        [ "$OK" -eq 1 ] && { DEPLOY=OK; break; }
    done
    if [ "$DEPLOY" != OK ]; then
        ANYFAIL=1
        echo "$TODAY, -, DEPLOY_MISMATCH" >> "$LOG"
        REPORT_ALL="$REPORT_ALL
🚨 committed pins but live site does NOT show them all after 10 min. Check Netlify."
    fi
fi

discord "Weekly ingest $TODAY:$REPORT_ALL"
exit "$ANYFAIL"
