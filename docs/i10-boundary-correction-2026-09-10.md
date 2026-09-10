# Heights I-10 boundary correction — 2026-09-10

Implemented the authorized removal of 26 permits, one deed and one sold transaction. No reassignment.

Boundary: midpoint between the COH I-10 mainline carriageway centerlines at each road-vertex longitude, clipped against the prior polygon; north side retained, south side removed. index.html ZONE_RING and heights_boundary.geojson use the exact same ring. The centerline artifact is i10-centerline-2026-09-10.geojson. COH source: https://services.arcgis.com/NummVBqZSIJKUeVR/ArcGIS/rest/services/COH_RoadCenterline/FeatureServer/0

No tracked record lies between the mainline centerlines or within the envelope bounded by mapped mainline/frontage-road centerlines. This tests the mapped freeway corridor, not a surveyed legal ROW edge. No membership-sensitive record was found in that corridor.

The 6539334 deploy was verified before editing: deployed inline scripts matched the commit and the 745 permit-review note was present. Netlify rewrites navigation URLs, so whole HTML byte equality is not claimed.

## Counts

Current shared snapshot: 2026-09-10T16:33:56.501Z, zero field/position overrides. Earlier 597-home baseline used an older snapshot. Same shared snapshot and frozen 2026-09-09 clock used for both comparison sides and all three checks.

| Metric | Before | After |
|---|---:|---:|
| Homes | 594 | 567 |
| Permit project IDs on rendered DATA | 406 | 380 |
| Permit project records | 309 | 283 |
| Under Construction | 225 | 211 |
| Finished | 137 | 125 |
| Sold archive | 791 | 790 |
| Sold Comps panel | 790 | 789 |
| Deeds | 139 | 138 |
| Custom | 19 | 19 |
| Sold Off Market | 1 | 1 |

Supply-card permit-home count: 328 → 302 (different from 309 → 283 permit project records and 406 → 380 distinct permit IDs). Historical permit registry and inspection feed retained; removed homes do not render.

| Finished row | Before | After |
|---|---:|---:|
| no_record | 75 | 63 |
| pending | 9 | 9 |
| terminated | 19 | 19 |
| active | 34 | 34 |

| Supply checkpoint | Before | After |
|---|---:|---:|
| 3 months | 69 | 66 |
| 6 months | 109 | 106 |
| 9 months | 183 | 170 |
| 12 months | 183 | 170 |
| 18 months | 183 | 170 |
| 24 months | 183 | 170 |

Forecast 183 → 170: 13 construction forecast arrivals removed. Under Construction loses 14; snapshot filters differ, so these are distinct totals. Finished loses 12 No Market Record homes. DATA loses 27 rows; SOLD_DATA loses one row. All 578 surviving DATA JSON objects and 790 surviving sold records retain their original values; DATA was not reserialized. Sold summary metrics recomputed from retained sales.

## Ledger and guard

Real removals: pulls/i10_correction_20260910/dropped_i10_2026-09-10.csv; committed copy docs/dropped-i10-2026-09-10.csv. Exactly 28 entries, reason OOZ_POLY_I10_SOUTH, with original record JSON. No silent deletions.

The actual permit_pull.ingest() was invoked on synthetic project 26999999 at 4605 Nolda. Only the geocoder was stubbed to its verified coordinates (29.7761265,-95.4078864); existing filter/dedupe/polygon/ledger code executed. Output:

```text
candidates after filter+dedupe: 1
OOZ-POLY (29.7761265,-95.4078864): 26999999 4605 NOLDA ST
insertable: 0  geocode-flagged: 0  dropped (all reasons): 1
DRY RUN — no write.
heights,26999999,4605 NOLDA ST,OOZ_POLY,"29.7761265,-95.4078864 outside boundary"
```

No importer code change needed: the existing importer reads the corrected shared boundary.

## Validation

Command: `/Users/nemoclaw/insp-venv/bin/python -B tests/i10_boundary_check.py`

```text
PASS 3 identical Heights checks; surviving phases unchanged; 28 removals ledgered; 578 surviving DATA objects byte-identical
monotonicity pairs=3257 violations=[]
```

All existing timeline fixtures passed, including Harvard, 629 E 26th, Munford/Voight, completed fixtures, 830 E 26th no phase. 742 Allston remains present and 715 Merrill Active with terminated history. 745 remains Unknown with its review note. Other markets untouched.
