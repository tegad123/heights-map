#!/bin/bash
# Publish inspection JSON onto main. Called by the inspection-refresh
# workflow after a full scrape. A non-zero LIMIT is a smoke test and
# must not commit. Refuses to replace a populated file with an empty
# or collapsed one, and refuses to overwrite a file main changed while
# this job was running.
set -euo pipefail

if [ -z "${GITHUB_ACTIONS:-}" ]; then
    echo "Refusing to commit outside GitHub Actions."
    exit 1
fi

cd "$(git rev-parse --show-toplevel)"

LIMIT="${LIMIT:-0}"
if [ -z "$LIMIT" ]; then LIMIT=0; fi
if [ "$LIMIT" != "0" ]; then
    echo "Limit is ${LIMIT}. Not committing."
    exit 0
fi

FILES=(
    inspections.json
    inspections_montrose.json
    inspections_riveroaks.json
    inspections_springbranch.json
    inspections_springvalley.json
    inspections_timbergrove.json
    inspections_westu.json
    inspections_gardenoaksoakforest.json
)

changed=()
for f in "${FILES[@]}"; do
    if [ -f "$f" ] && ! git diff --quiet -- "$f"; then
        changed+=("$f")
    fi
done

if [ "${#changed[@]}" -eq 0 ]; then
    echo "Inspection JSON unchanged. Not committing."
    exit 0
fi

python3 - "${changed[@]}" <<'PY'
import json, os, subprocess, sys

def rows(data):
    total = 0
    if not isinstance(data, dict):
        return 0
    for rec in data.values():
        if isinstance(rec, dict) and isinstance(rec.get("inspections"), list):
            total += len(rec["inspections"])
    return total

failed = False
for path in sys.argv[1:]:
    try:
        new = json.loads(open(path).read())
    except Exception as exc:
        print(f"REFUSING to commit {path}: not valid JSON ({exc})")
        failed = True
        continue
    try:
        old_raw = subprocess.check_output(["git", "show", f"HEAD:{path}"], text=True)
        old = json.loads(old_raw)
    except subprocess.CalledProcessError:
        old = None
    if path.endswith("inspections_springvalley.json") and old == {} and new != {}:
        if not os.path.exists("springvalley_permits.json"):
            print(f"REFUSING to commit {path}: still no springvalley_permits.json")
            failed = True
            continue
    if isinstance(old, dict) and old:
        if not isinstance(new, dict) or not new:
            print(f"REFUSING to commit {path}: new file is empty")
            failed = True
            continue
        if len(new) < len(old) * 0.5:
            print(f"REFUSING to commit {path}: project count {len(old)} -> {len(new)}")
            failed = True
            continue
        old_rows, new_rows = rows(old), rows(new)
        if old_rows >= 20 and new_rows < old_rows * 0.5:
            print(f"REFUSING to commit {path}: inspection rows {old_rows} -> {new_rows}")
            failed = True
            continue
    elif not isinstance(new, dict):
        print(f"REFUSING to commit {path}: not a JSON object")
        failed = True
if failed:
    sys.exit(1)
print("Commit guard passed for " + ", ".join(sys.argv[1:]))
PY

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT
for f in "${changed[@]}"; do
    cp "$f" "$tmpdir/$f"
done

git fetch origin main
base=$(git merge-base HEAD origin/main)
for f in "${changed[@]}"; do
    if ! git diff --quiet "$base" origin/main -- "$f"; then
        echo "origin/main updated ${f} after this job read it. Refusing to overwrite."
        exit 1
    fi
done

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# The scrape may have run on a non-main ref (a manual dispatch of a
# branch). Land only the JSON files on the current main.
git reset --hard HEAD
git checkout -B main origin/main
for f in "${changed[@]}"; do
    cp "$tmpdir/$f" "$f"
done

git add -- "${changed[@]}"
if git diff --cached --quiet -- "${changed[@]}"; then
    echo "Nothing staged. Not committing."
    exit 0
fi

today=$(TZ=America/Chicago date +%Y-%m-%d)
git commit \
    -m "data: refresh inspections (GitHub Actions)" \
    -m "ILMS scrape ${today} America/Chicago. Updates the inspection JSON the Overview badge reads (updated / scraped_at). Netlify rebuilds from main."

git push origin HEAD:main
echo "Pushed inspection files to main."
