#!/bin/bash
# LEGACY FALLBACK. The scheduled inspection scrape is GitHub Actions
# (.github/workflows/inspection-refresh.yml). Keep this script for a Mac
# that has to run the scrape itself. Do not leave it scheduled while
# Actions is enabled — both would push inspections JSON to main.
#
# inspection_refresh.sh — Mon/Thu 05:00 America/Chicago ILMS inspection scrape.
# Same machine and checkout as the permit jobs:
#   /Users/tegaumukoro/heights-map
# launchd label com.heightsmap.inspections (install_inspection_launchd.sh).
# Scrapes every market in run_and_deploy.MARKETS that has a permits file,
# commits that market's inspections JSON, and pushes main.
# Spring Valley has no springvalley_permits.json; it is skipped and
# inspections_springvalley.json is left as {}.
# DISCORD_WEBHOOK_URL comes from the launchd plist env — never hardcode.
# A missed slot is retried by catchup_check.sh (Tue/Fri morning).
set -u

export TZ=America/Chicago
REPO=/Users/tegaumukoro/heights-map
LOG="$REPO/pulls/inspection_log.txt"
LOCK="$REPO/pulls/inspection_refresh.lock"
TODAY=$(date +%Y-%m-%d)

discord() {
    [ -z "${DISCORD_WEBHOOK_URL:-}" ] && { echo "discord (not configured): $1"; return; }
    python3 - "$1" <<'PY'
import json, os, sys, urllib.request
# Discord 403s the default Python-urllib User-Agent; any custom UA passes
req = urllib.request.Request(os.environ['DISCORD_WEBHOOK_URL'],
    data=json.dumps({'content': sys.argv[1][:1900]}).encode(),
    headers={'Content-Type': 'application/json',
             'User-Agent': 'heights-map-inspections/1.0'})
try:
    urllib.request.urlopen(req, timeout=20)
except Exception as e:
    print(f'discord post failed: {e}', file=sys.stderr)
PY
}

mkdir -p "$REPO/pulls"
if [ -f "$LOCK" ]; then
    old=$(cat "$LOCK" 2>/dev/null || true)
    if [ -n "${old:-}" ] && kill -0 "$old" 2>/dev/null; then
        echo "inspection refresh already running (pid $old)"
        exit 0
    fi
    rm -f "$LOCK"
fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT

source "$HOME/insp-venv/bin/activate" || {
    echo "$TODAY, FAIL, venv" >> "$LOG"
    discord "🚨 Inspection refresh FAILED $TODAY: ~/insp-venv did not activate"
    exit 1
}
cd "$REPO" || exit 1

branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" != "main" ]; then
    echo "$TODAY, FAIL, branch $branch" >> "$LOG"
    discord "🚨 Inspection refresh FAILED $TODAY: checkout is on $branch, not main"
    exit 1
fi
if ! git pull --ff-only >/dev/null 2>&1; then
    echo "$TODAY, FAIL, git pull --ff-only" >> "$LOG"
    discord "🚨 Inspection refresh FAILED $TODAY: git pull --ff-only"
    exit 1
fi

# Confirm Spring Valley is still the empty placeholder before we start.
if [ ! -f springvalley_permits.json ]; then
    if ! python3 -c 'import json,sys; sys.exit(0 if json.load(open("inspections_springvalley.json"))=={} else 1)'; then
        echo "$TODAY, FAIL, inspections_springvalley.json is not empty and there is no permits file" >> "$LOG"
        discord "🚨 Inspection refresh FAILED $TODAY: inspections_springvalley.json is not {} and springvalley_permits.json does not exist. Refusing to scrape."
        exit 1
    fi
fi

OUT=$(mktemp)
python3 run_and_deploy.py >"$OUT" 2>&1
RC=$?
cat "$OUT"
SUMMARY=$(grep '^INSPECTION_RESULT ' "$OUT" | sed 's/^INSPECTION_RESULT //' | tr '\n' '; ')
rm -f "$OUT"

if [ ! -f springvalley_permits.json ]; then
    if ! python3 -c 'import json,sys; sys.exit(0 if json.load(open("inspections_springvalley.json"))=={} else 1)'; then
        echo "$TODAY, FAIL, springvalley file changed" >> "$LOG"
        discord "🚨 Inspection refresh FAILED $TODAY: inspections_springvalley.json was modified without a permits file."
        exit 1
    fi
fi

if [ "$RC" -eq 0 ]; then
    echo "$TODAY, OK, ${SUMMARY:-no-result-lines}" >> "$LOG"
    discord "Inspection refresh $TODAY OK. ${SUMMARY:-no result lines}"
    exit 0
fi
echo "$TODAY, FAIL, exit=$RC ${SUMMARY:-no-result-lines}" >> "$LOG"
discord "🚨 Inspection refresh FAILED $TODAY (exit $RC). ${SUMMARY:-no result lines}"
exit "$RC"
