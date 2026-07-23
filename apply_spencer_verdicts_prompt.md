# Prompt for Claude Code: apply Spencer review verdicts to the Heights map

Paste everything below into Claude Code once the `spencer_verdict` column in
`spencer_review_2026-07-23.csv` is filled in. Valid verdict values:
`Single Lot`, `Split Lot`, `Common Driveway`, `Frontloader`, or `skip`.

---

Working dir: ~/heights-map. This repo auto-deploys to Netlify on push. Verify everything before committing. Do not touch any file except index.html.

TASK: Apply the classifications from spencer_review_2026-07-23.csv (column `spencer_verdict`) to the DATA array in index.html. These are hand-verified ground-truth labels. Do NOT apply any auto-classification logic, do NOT infer labels from permit text - the verdict column is the only source.

STEP 0 - safety:
- git pull --ff-only && git status. Tracked files must be clean. cp index.html /tmp/index.html.bak
- Read spencer_review_2026-07-23.csv. Skip any row where spencer_verdict is empty or "skip". Report how many rows will be applied.

STEP 1 - locate each entry:
- DATA is a single-line JSON array in index.html at `let DATA = [...]`. Parse it with Python (json + regex extract), do NOT regenerate or re-serialize the whole array - the file is hand-authored and every edit must be a surgical string replacement inside the matching entry only.
- Match CSV addresses to DATA entries by normalized address: lowercase, strip ", Houston..." suffix, "Street"->"St", "Unit#A"->" a", collapse whitespace. Every row must match exactly ONE entry. If a row matches zero or 2+ entries, STOP and report it - do not guess.

STEP 2 - edit rules (all three fields must move in lockstep):
- `prod`: set to the verdict. If the entry has no prod key, insert `"prod": "<verdict>",` immediately after the `"id": "...",` field.
- `ty`: prodKeyR() in this file checks ty BEFORE prod for Single/Split, so a prod change without a ty change is silently ignored. Rules:
  * verdict Single Lot -> if a ty key exists, set it to "active_single"
  * verdict Split Lot  -> if a ty key exists, set it to "active_split"
  * verdict Common Driveway -> REMOVE the ty key entirely (mind the comma on whichever side); every existing Common Driveway entry in this file has no ty key
  * verdict Frontloader -> leave ty as-is
  * if no ty key exists, do not add one (prodKeyR falls through to prod)
- `f` flag chip: if the entry's f value STARTS with one of "Single Lot", "Split Lot", "Common Driveway", "Frontloader" followed by ", " (or is exactly that label), replace that leading label with the verdict. Never touch other tokens in f.
- Special rows in this CSV:
  * 1021 Nadine St and 830 E 26th St have NO permits field and LIFE stage "uc" - apply the verdict normally; if Spencer also supplied a permit number in his notes, do NOT add it to the file, just report it back to me.
  * 1518 Herkimer St is tagged deed in LIFE despite having a permit (stale lifecycle). Apply the prod verdict but do NOT edit the LIFE object - it self-corrects on regeneration.

STEP 3 - verify (mandatory, entry-by-entry):
- Re-extract DATA from the edited file and json-parse it. Must still be 329 entries, zero duplicate ids.
- For every applied row: prod equals the verdict; ty consistent per the rules above; f chip consistent.
- For every NON-applied entry: must be byte-identical to the original (compare parsed dicts). Any unexpected change = restore /tmp/index.html.bak and report.
- Also run this consistency sweep over the WHOLE file and report violations:
  * any prod="Common Driveway" entry that still has a ty key
  * any prod="Split Lot" with ty other than "active_split"; any prod="Single Lot" with ty other than "active_single"
  * any f chip whose leading label disagrees with prod
- Print the before/after label distribution: Counter(r.get('prod') for r in DATA).

STEP 4 - local check, commit, deploy verify:
- python3 -m http.server 8000 in background; curl -s localhost:8000 | grep -c "Common Driveway" must be > 0; kill server. (Human eyeballs the map separately.)
- git add index.html && git commit -m "Apply Spencer review verdicts: <N> classifications (spencer_review_2026-07-23)" && git push
- Wait 90s, then: curl -sL https://tangerine-sorbet-eca5f5.netlify.app | grep -o 'Common Driveway' | wc -l and confirm it matches the local count. If not (Netlify drops webhooks), git commit --allow-empty -m "redeploy" && git push and re-check.
- Report: rows applied, rows skipped, verification output, before/after distribution, deploy confirmation.
