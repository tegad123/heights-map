# Allston St missing addresses — investigation, 2026-09-09

Read-only trace of 742 Allston, 224 Allston and 839 Allston. **No boundary,
DATA, config or guard was changed.** Conclusion up front: the three misses are
three different causes, and none of them is the market polygon or the
longitude cutoff.

| Address | Where it is | Why it looks missing |
|---|---|---|
| 839 Allston St | In DATA (`pmt_839-allston-st-77007`), pin renders | Tagged `custom` by client research on 2026-09-09 — removed from Under Construction and every phase/product panel by design |
| 742 Allston St | Absent from every layer in the repo | No COH record ever reached this repo. Cannot be attributed further without `pulls/` |
| 224 Allston St | Absent from every layer in the repo | Same. Already the documented motivating case for the dropped-rows ledger (`permit_pull.py:210`) |

## 1. Raw permit pull output — NOT ANSWERABLE FROM THIS ENVIRONMENT

`pulls/` is gitignored (`.gitignore:4`) and does not exist in this container;
the pull CSVs live only on Tegas-MacBook-Air. `arcweb.hcad.org` is also blocked
by this environment's network policy (403 at the proxy), so no geocode could be
re-run either. Commands to close this locally are in the last section.

## 2. pulls/dropped_*.csv — NOT ANSWERABLE FROM THIS ENVIRONMENT

Same reason. Note the ledger only starts 2026-09-01, so a row dropped before
that date has no ledger entry by construction — which is exactly the 224
Allston situation the ledger was added to prevent recurring.

## 3. In DATA but not rendering

**839 Allston — yes, and this is the real answer for it.**

```
{"id": "pmt_839-allston-st-77007", "a": "839 Allston St, Houston, TX 77007",
 "kind": "permit", "lat": 29.7865047, "lng": -95.4002707,
 "permits": [{"proj": "26055391", "desc": "S.F. RES W/ATT. GARAGE ...",
              "val": "775003", "permitDesc": "Building Pmt"}],
 "ty": "active_single", "prod": "Single Lot"}
```

It survives all three render-side guards (OUT_OF_ZONE regex, `lng > -95.370`,
`inZonePoly`) and it has an inspection record (`inspections.json`, key
`26055391`). The pin is on the map.

What changed is its category. `inventory_classifications.js:5` lists
`pmt_839-allston-st-77007` in `CLIENT_CLASSIFICATIONS.custom`, applied
2026-09-09 (`7e1bdd5`, recorded in `docs/client-classifications-2026-09-09.md`
as "Under Construction / Foundation -> custom"). Every construction counter in
`index.html` opens with `if(!mById[id]||inventoryCategory(id))continue;`
(`ucCount`, `ucTypeCount`, `comboCount`, `listedCount`, `tagCount`, ...), so a
`custom` record is deliberately excluded from Under Construction, from the
phase rows, and from the 12-month supply. It now appears only under the
**Custom** legend group.

So 839 is not lost — it moved, on the client's own instruction, one day ago.

**615 Allston** is also in DATA, but as a DealMachine lead (id `2131149358`,
sold 2025-08-15), not a permit. It renders on the off-market/lead layer.

**742 and 224 are not in DATA at all**, and no DATA row on any street carries
house number 742 or 224, so neither was mis-geocoded onto a neighbouring
street.

## 4. Absent from COH results entirely

742 and 224 Allston appear in **no** repo layer: not `index.html` DATA, not
`SOLD_DATA`, not `heights_permits.json`, not `inspections.json`, not
`heights_deed.data.json`, not `heights_active.data.json`, not
`heights_market_status.data.json`, not `heights_off_market.csv`, and not in any
other market's HTML. The only in-repo mention of either is the comment at
`permit_pull.py:210` recording 224 Allston as a prior unexplained miss.

The repo therefore cannot distinguish "COH never returned it" from "the pull
returned it and a guard ate it". The structural reason is that pull CSVs are
gitignored and the dropped ledger only began 2026-09-01, so nothing durable
records what COH returned before that date.

## Boundary and longitude check — the boundary is NOT clipping Allston

Allston St runs almost due north–south at **lng -95.3997 to -95.4005**
(15 in-repo records with coordinates). Both guards are far away:

| Address | est. lat | distance E of the west ring edge | distance W of the -95.370 cutoff |
|---|---|---:|---:|
| 224 Allston | 29.77477 | 1,422 m | 2,928 m |
| 742 Allston | 29.78443 | 1,717 m | 2,927 m |
| 839 Allston | 29.78624 (actual) | 1,773 m | 2,927 m |

Latitudes for 224 and 742 are a linear fit over ten Allston sold comps
(606 -> 1528), 0.001866 deg per 100 house numbers, max residual 0.00029 deg
(32 m) — far tighter than the 557 m margin 224 Allston has over the ring's
southern edge.

Four independent checks, all negative:

1. **The whole Allston corridor is inside the ring.** At lng -95.400 the
   `ZONE_RING` interior spans lat **29.76975 to 29.81680**, which covers
   Allston house numbers from roughly 0 to 2470. No real Allston address can
   fall outside it.
2. **The render-side splice removes nothing today.** Replaying
   `OUT_OF_ZONE` + `lng > -95.370` + `inZonePoly` over all 430 DATA rows:
   **0 spliced out.**
3. **`heights_boundary.geojson` and the embedded `ZONE_RING` are identical**
   (same 14 vertices), so ingest-side and render-side agree — there is no
   drift between the two gates.
4. **All 767 sold comps are inside the ring.** Those come from the client's
   own HAR search polygon, so if the ring were tighter than the market the
   client works, comps would fall outside it. None do.

Allston is not on the western edge either. Permit pins by longitude band:

```
-95.430..-95.425:  6    -95.405..-95.400: 12   <- Allston sits here
-95.425..-95.420:  6    -95.400..-95.395:  4
-95.420..-95.415:  9    -95.395..-95.390: 11
-95.415..-95.410: 32    -95.390..-95.385: 28
-95.410..-95.405: 20    -95.385..-95.380: 18
                        -95.380..-95.375: 23
                        -95.375..-95.370:  5
```

The westernmost permit pin is 1605 W 25th St at **-95.42798**, well past
Allston and still inside the ring. The west edge is being reached, not clipped.

## How many other Allston addresses are absent

The repo knows **16 distinct Allston addresses**, and all 16 render on their
respective layers:

- 14 sold comps in `SOLD_DATA` — 606, 615, 732, 810, 836, 924, 1021, 1022,
  1026, 1136, 1314, 1342, 1343, 1528
- 1 DealMachine lead in DATA — 615
- 1 permit in DATA — 839

**Zero** Allston addresses anywhere in repo data are removed by the guards.
The only Allston addresses absent from the map are 742 and 224, and they are
absent from every input, not filtered out of one.

Extent of a boundary problem, if the question is "how much legitimate Heights
territory is the ring cutting": **none that this repo's data can show.** 0 of
430 DATA rows and 0 of 767 sold comps fall outside it.

## What "three on one street" most likely is

Not one cause. 839 is a category move made yesterday. 742 and 224 are input
misses that the pipeline has no durable record of, which makes any single
street look like a cluster once someone checks it address by address.

One mechanism worth ruling out while the raw CSVs are in hand — it is a real
silent-drop path even though it does not explain these three. `ingest()`
builds its dedupe set from **every** DATA row, permit or not:

```python
norms = {norm_addr(r['a']) for r in data if 'a' in r}
...
if norm_addr(street) in norms:
    skipped['dup_addr'] += 1
    dropped.append((proj, street, 'DUP_ADDR', ...)); continue
```

256 of the 430 DATA rows are non-permit leads/sold/deed records. Any of those
addresses shadows a later COH permit at the same address — the permit is
skipped as `DUP_ADDR` and the pin keeps its lead identity with no permit and no
phase. 615 Allston is exactly such a shadowing row. This is now visible in the
ledger (since 2026-09-01) rather than silent, but it is worth grepping for.

## Commands to close questions 1 and 2 — run on Tegas-MacBook-Air

```sh
cd ~/heights-map

# 1. did any pull ever return Allston?
grep -i -h allston pulls/permits_*.csv | sort -u

# 2. did a guard drop it, and under what reason?
grep -i -h allston pulls/dropped_*.csv pulls/quarantine_*.csv

# 3. ask COH directly over a wide window, both Allston zips (PULL ONLY)
python3 permit_pull.py --zip 77007 --ptype Structural \
    --from 20250101 --to 20260909 --out /tmp/allston_77007.csv
python3 permit_pull.py --zip 77008 --ptype Structural \
    --from 20250101 --to 20260909 --out /tmp/allston_77008.csv
grep -i allston /tmp/allston_77007.csv /tmp/allston_77008.csv

# 4. if COH does return them, dry-run only and read the drop reasons
python3 permit_pull.py --ingest --from-csv /tmp/allston_77007.csv /tmp/allston_77008.csv

# 5. how often DUP_ADDR shadowing is firing
cut -d, -f4 pulls/dropped_*.csv | sort | uniq -c | sort -rn
```

Step 3 is a pull, not an ingest — it writes only to `/tmp`. Step 4 is a
dry-run; it prints candidates and drop reasons and writes nothing.

## No fix proposed yet

Per instruction the boundary was left alone, and on this evidence it should
stay alone — the ring is not the defect. The next move is step 3 above: if COH
returns 742/224 Allston, the defect is in the filter/geocode chain and the
dry-run names it; if COH does not return them, the defect is upstream in the
14-day trailing pull window (`nightly_permit_pull.sh`), and the fix is a
one-off wide-window backfill, not a boundary edit.
