#!/bin/bash
# catchup_check.sh — hourly launchd guard (com.heightsmap.catchup) for runs
# missed while the Mac was asleep/off. launchd's StartCalendarInterval only
# fires missed jobs on wake in some power states (2026-08-27: the 05:30 pull
# silently never ran). Idempotent: keyed off dated lines in the run logs.
#   - nightly pull: if pull_log.txt has no line for today and it's >= 05:35,
#     run nightly_permit_pull.sh.
#   - weekly ingest: if it's Sunday >= 07:05 (or Monday < 12:00, catching a
#     slept-through Sunday) and ingest_log.txt has no line dated >= that
#     Sunday, run weekly_permit_ingest.sh.
set -u

REPO=/Users/tegaumukoro/heights-map
cd "$REPO" || exit 1
mkdir -p pulls
CLOG="pulls/catchup_log.txt"
TODAY=$(date +%Y-%m-%d)
NOW=$(date +%H%M)
DOW=$(date +%w)     # 0=Sunday

# --- nightly pull catchup ---
if [ "$NOW" -ge 0535 ] 2>/dev/null && ! grep -q "$TODAY," pulls/pull_log.txt 2>/dev/null; then
    echo "$TODAY $(date +%H:%M) CATCHUP: nightly pull missing — running" >> "$CLOG"
    /bin/bash "$REPO/nightly_permit_pull.sh"
    echo "$TODAY $(date +%H:%M) CATCHUP: nightly pull done (exit $?)" >> "$CLOG"
fi

# --- weekly ingest catchup ---
SUNDAY=""
if [ "$DOW" -eq 0 ] && [ "$NOW" -ge 0705 ] 2>/dev/null; then
    SUNDAY=$TODAY
elif [ "$DOW" -eq 1 ] && [ "$NOW" -lt 1200 ] 2>/dev/null; then
    if date -v-1d >/dev/null 2>&1; then SUNDAY=$(date -v-1d +%Y-%m-%d)
    else SUNDAY=$(date -d 'yesterday' +%Y-%m-%d); fi
fi
if [ -n "$SUNDAY" ]; then
    # any ingest_log line dated >= that Sunday counts (a Monday catchup run
    # logs Monday's date — must not re-fire)
    RAN=$(awk -F, -v s="${SUNDAY//-/}" '{gsub(/-/,"",$1); if ($1+0 >= s+0) n++} END{print n+0}' \
          pulls/ingest_log.txt 2>/dev/null || echo 0)
    if [ "$RAN" -eq 0 ]; then
        echo "$TODAY $(date +%H:%M) CATCHUP: weekly ingest for $SUNDAY missing — running" >> "$CLOG"
        /bin/bash "$REPO/weekly_permit_ingest.sh"
        echo "$TODAY $(date +%H:%M) CATCHUP: weekly ingest done (exit $?)" >> "$CLOG"
    fi
fi
exit 0
