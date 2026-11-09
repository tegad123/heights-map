#!/bin/bash
# LEGACY FALLBACK. GitHub Actions runs the inspection scrape. Install
# this launchd agent only if Actions cannot reach ILMS and a Mac has to
# own the job instead. Unload com.heightsmap.inspections before turning
# Actions back on. Catch-up retries also need INSPECTION_LEGACY_MAC=1
# in the catchup agent's environment; leave that unset while Actions is
# the scheduler.
#
# Install the Monday/Thursday inspection scrape on Tega's Mac.
# The permit jobs already live in ~/Library/LaunchAgents as
# com.heightsmap.permitpull, com.heightsmap.permitingest, and
# com.heightsmap.catchup. This adds com.heightsmap.inspections beside them.
#
# Run on that Mac, from the same checkout the other jobs use:
#   cd /Users/tegaumukoro/heights-map
#   bash install_inspection_launchd.sh
#
# The Discord webhook is copied from com.heightsmap.permitingest.plist
# (or from DISCORD_WEBHOOK_URL in the environment). It is never printed.
set -euo pipefail

if [ "$(uname)" != "Darwin" ]; then
    echo "This installs a macOS launchd agent. Run it on Tega's Mac."
    exit 1
fi

REPO="$(cd "$(dirname "$0")" && pwd)"
EXPECTED=/Users/tegaumukoro/heights-map
if [ "$REPO" != "$EXPECTED" ]; then
    echo "This checkout is $REPO"
    echo "The permit jobs hardcode $EXPECTED. Install from that checkout so inspections commit the same clone."
    exit 1
fi

LABEL=com.heightsmap.inspections
DEST="$HOME/Library/LaunchAgents/$LABEL.plist"
TEMPLATE="$REPO/launchd/com.heightsmap.inspections.plist"
UID_NUM="$(id -u)"

WEBHOOK="${DISCORD_WEBHOOK_URL:-}"
if [ -z "$WEBHOOK" ]; then
    SRC_PLIST="$HOME/Library/LaunchAgents/com.heightsmap.permitingest.plist"
    if [ -f "$SRC_PLIST" ]; then
        WEBHOOK="$(/usr/libexec/PlistBuddy -c 'Print :EnvironmentVariables:DISCORD_WEBHOOK_URL' "$SRC_PLIST" 2>/dev/null || true)"
    fi
fi
if [ -z "$WEBHOOK" ] || [ "$WEBHOOK" = "__DISCORD_WEBHOOK_URL__" ]; then
    echo "DISCORD_WEBHOOK_URL is not in the environment and was not in com.heightsmap.permitingest.plist."
    echo "Export it in this shell and rerun. The value is not printed."
    exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents" "$REPO/pulls"
WEBHOOK="$WEBHOOK" python3 - "$TEMPLATE" "$DEST" <<'PY'
import os, pathlib, sys
src, dest = sys.argv[1:]
webhook = os.environ["WEBHOOK"]
text = pathlib.Path(src).read_text()
if "__DISCORD_WEBHOOK_URL__" not in text:
    sys.exit("template is missing __DISCORD_WEBHOOK_URL__")
pathlib.Path(dest).write_text(text.replace("__DISCORD_WEBHOOK_URL__", webhook))
print(f"wrote {dest}")
PY

launchctl bootout "gui/${UID_NUM}/${LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/${UID_NUM}" "$DEST"
launchctl enable "gui/${UID_NUM}/${LABEL}"
echo "Installed ${LABEL}."
echo "Fires Monday and Thursday at 05:00 in the Mac's local timezone."
echo "That timezone needs to be America/Chicago (the permit commits already are)."
echo "Check with: sudo systemsetup -gettimezone"
echo "A closed lid is retried by the hourly catchup agent on Tuesday and Friday morning."
echo "Smoke one permit without writing the repo:"
echo "  source ~/insp-venv/bin/activate"
echo "  python3 scrape_inspections.py --permits heights_permits.json --out /tmp/insp-smoke.json --limit 1"
