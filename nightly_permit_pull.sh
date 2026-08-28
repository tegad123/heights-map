#!/bin/bash
# nightly_permit_pull.sh — scheduled COH permit PULLS, all live markets.
# Pull only: never runs ingest, never touches market HTML, never commits CSVs.
# Zip list comes from market_config.ALL_ZIPS (single source of truth).
# Ingest is weekly_permit_ingest.sh (Sun 07:00) or manual dry-run + --apply.
set -u

REPO=/Users/tegaumukoro/heights-map
PTYPE=Structural

LOG="$REPO/pulls/pull_log.txt"
FAIL=0

# --- environment ---
source "$HOME/insp-venv/bin/activate" || exit 1
cd "$REPO" || exit 1
mkdir -p pulls
ZIPS=$(python3 -c "from market_config import ALL_ZIPS; print(' '.join(ALL_ZIPS))") || exit 1

if ! git pull --ff-only >/dev/null 2>&1; then
    echo "$(date +%Y-%m-%d), -, -, FAIL(git pull --ff-only)" >> "$LOG"
    exit 1
fi

# --- date window (BSD vs GNU date) ---
if date -v-1d >/dev/null 2>&1; then
    FROM=$(date -v-14d +%Y%m%d)
    CUTOFF=$(date -v-3d +%Y-%m-%d)
else
    FROM=$(date -d '14 days ago' +%Y%m%d)
    CUTOFF=$(date -d '3 days ago' +%Y-%m-%d)
fi
TO=$(date +%Y%m%d)
TODAY=$(date +%Y-%m-%d)
STAMP=$(date +%Y%m%d)

# --- staleness guard: LAST_GOOD_PULL older than 3 days => STALE: prefix ---
STALE=""
LGP=$(cat pulls/LAST_GOOD_PULL 2>/dev/null || true)
if [ -z "$LGP" ] || [ "${LGP//-/}" -lt "${CUTOFF//-/}" ] 2>/dev/null; then
    STALE="STALE: "
fi

# --- pull per zip ---
for Z in $ZIPS; do
    OUT="pulls/permits_${Z}_${STAMP}.csv"
    CAP=$(mktemp)
    python3 permit_pull.py --zip "$Z" --ptype "$PTYPE" \
        --from "$FROM" --to "$TO" --out "$OUT" >"$CAP" 2>&1
    RC=$?

    ROWS=0
    if [ -f "$OUT" ]; then
        ROWS=$(( $(wc -l < "$OUT") - 1 ))
        [ "$ROWS" -lt 0 ] && ROWS=0
    fi

    REASON=""
    if [ "$RC" -ne 0 ]; then
        REASON="exit=$RC"
    elif [ ! -f "$OUT" ] || [ "$ROWS" -eq 0 ]; then
        REASON="no-rows"
    elif grep -qi "under Maintenance" "$CAP"; then
        # fake maintenance page = date-format rejection, treat as failure
        REASON="under-Maintenance"
    fi

    if [ -n "$REASON" ]; then
        FAIL=1
        echo "${STALE}${TODAY}, ${Z}, ${ROWS}, FAIL(${REASON})" >> "$LOG"
        echo "--- $Z output ---"; cat "$CAP"
    else
        echo "${STALE}${TODAY}, ${Z}, ${ROWS}, OK" >> "$LOG"
    fi
    rm -f "$CAP"
done

if [ "$FAIL" -eq 0 ]; then
    echo "$TODAY" > pulls/LAST_GOOD_PULL
fi
exit "$FAIL"
