# Sold lot floor and recency cross-tab — 2026-09-08

## Diagnosis before editing

Executed `/Users/nemoclaw/insp-venv/bin/python -B /tmp/sold_floor_browser.py` against the unchanged page, clicking the actual Layers controls. Output:

```text
Single Lot alone = 411
Single Lot + 0-30 = 31
independentIntersection = 31
independentUnion = 434
allMatch = true
Page errors: []
```

The controls already AND across dimensions. They select one lot type and one recency bucket; another entry in the same dimension replaces the previous choice. Clicking the selected entry again clears it. The lot-type counts show the selected recency's split, while the recency counts show the selected lot type's distribution. With both cleared, each grouping sums to all 764 sales. Therefore no filter-logic rewrite or nesting was needed. Added explicit instructions and scope labels: LOT TYPE · ALL DATES (or selected period), RECENCY · ALL LOT TYPES (or selected product).

## Classification and market scope

`sold_ingest.py` imports `classify_lot` from `sold_classification.py`. Updated the shared helper: >=4000 Single Lot; positive <4000 Split Lot; absent/null/zero/unparseable Unknown. Negative/nonfinite areas are invalid and also Unknown. Invoked through sold_ingest with boundary cases: `classify_lot boundary checks: 13/13 PASS`.

| Market | Before Single / Split / Unclassified / Unknown | After Single / Split / Unknown | Total |
|---|---|---|---:|
| Heights | 411 / 289 / 56 / 8 | 411 / 345 / 8 | 764 → 764 |
| Montrose | No HAR Sold Comps layer | Unchanged | N/A |
| River Oaks | No HAR Sold Comps layer | Unchanged | N/A |
| Spring Branch | No HAR Sold Comps layer | Unchanged | N/A |
| Spring Valley Village | No HAR Sold Comps layer | Unchanged | N/A |
| Timbergrove/Lazybrook | No HAR Sold Comps layer | Unchanged | N/A |
| West University | No HAR Sold Comps layer | Unchanged | N/A |
| Garden Oaks/Oak Forest | No HAR Sold Comps layer | Unchanged | N/A |

`rg -l 'Unclassified' --glob '*.html'` before edits returned only `index.html`. Executed JSON parsing confirmed only that market has SOLD_DATA. The other seven HTML files remain byte-identical. Their hidden legacy sold DATA collections are separate and unchanged.

All 56 formerly Unclassified sold records now say Split Lot and no longer carry the obsolete `nr` review flag. An executed old/new comparison confirmed that those two keys are their only changed fields. The eight Unknown records are unchanged. No lot areas were backfilled. Unclassified was removed from Layers, Sold dashboard, sold ASK copy, generated metrics and record classifications. Historical audit documents remain historical.

## Cross-tab (as of 2026-09-08, same as the existing data)

| Days since closing | Single Lot | Split Lot | Unknown | Total |
|---|---:|---:|---:|---:|
| 0-30 | 31 | 23 | 0 | 54 |
| 30-60 | 30 | 26 | 0 | 56 |
| 60-90 | 35 | 38 | 0 | 73 |
| 90-180 | 110 | 90 | 2 | 202 |
| 180-365 | 177 | 138 | 4 | 319 |
| 365+ | 28 | 30 | 2 | 60 |
| Total | 411 | 345 | 8 | 764 |

Executed row/column sum assertions and unique-id count: `Cross-tab row/column sums and unique transaction count: PASS (411 + 345 + 8 = 764)`.

## All eight Unknown records

None has a `lot` key. No acreage, lot dimensions, frontage, depth, HCAD area, parcel geometry, or alternate lot-size field exists on these sold records. `sq` is building square footage, NOT lot area. The complete objects below retain every field available for a later backfill decision, including building area, coordinates, builder where supplied, and close/list prices. MLS is the `id` with its leading `s` removed.

| Address | MLS | Building sqft (`sq`) | Latitude | Longitude | Builder (`bl`) |
|---|---|---:|---:|---:|---|
| 521 W 22nd Street | 41813835 | 2242 | 29.806119 | -95.406934 | Not present |
| 2916 Michaux Street | 71522503 | 2500 | 29.784626 | -95.384095 | TOMO Homes |
| 2932 Michaux Street | 63496941 | 2500 | 29.784626 | -95.384095 | TOMO Homes |
| 242 E 28th Street | 59376489 | 2939 | 29.812069 | -95.396813 | Not present |
| 323 W 23rd Street | 55821001 | 2750 | 29.807177 | -95.402515 | Enterra Homes |
| 1210 W 23rd Street | 15221728 | 1883 | 29.806403 | -95.419978 | CIVE |
| 325 W 23rd Street | 4197682 | 2721 | 29.807177 | -95.402515 | Enterra Homes |
| 1216 W 23rd Street | 16275355 | 1624 | 29.806403 | -95.420049 | CIVE |

Complete stored records (all eight):

```json
[
  {
    "id": "s41813835",
    "a": "521 W 22nd Street",
    "lat": 29.806119,
    "lng": -95.406934,
    "cp": 890000,
    "lp": 919000,
    "sq": 2242,
    "psf": 397.0,
    "cd": "2026-05-21",
    "mo": "2026-05",
    "dom": 6,
    "yb": 2012,
    "coh": "resale",
    "band": "800k-1.3M",
    "win": "90-180",
    "prod": "Unknown",
    "svl": -0.0316,
    "sch": "HELMS ELEMENTARY SCHOOL",
    "la": "Ginny Jackson",
    "ba": "Kyla Phung Linn",
    "ak": "521 w 22nd st",
    "nr": 1
  },
  {
    "id": "s71522503",
    "a": "2916 Michaux Street",
    "lat": 29.784626,
    "lng": -95.384095,
    "cp": 880000,
    "lp": 900000,
    "sq": 2500,
    "psf": 352.0,
    "cd": "2026-03-31",
    "mo": "2026-03",
    "dom": 43,
    "yb": 2025,
    "coh": "nc",
    "band": "800k-1.3M",
    "win": "90-180",
    "prod": "Unknown",
    "svl": -0.0222,
    "bl": "TOMO Homes",
    "sch": "TRAVIS ELEMENTARY SCHOOL (HOUSTON)",
    "la": "Spencer Huck",
    "ba": "Steven Kinne",
    "ak": "2916 michaux st",
    "nr": 1
  },
  {
    "id": "s63496941",
    "a": "2932 Michaux Street",
    "lat": 29.784626,
    "lng": -95.384095,
    "cp": 880000,
    "lp": 900000,
    "sq": 2500,
    "psf": 352.0,
    "cd": "2025-11-24",
    "mo": "2025-11",
    "dom": 87,
    "yb": 2025,
    "coh": "nc",
    "band": "800k-1.3M",
    "win": "180-365",
    "prod": "Unknown",
    "svl": -0.0222,
    "bl": "TOMO Homes",
    "sch": "TRAVIS ELEMENTARY SCHOOL (HOUSTON)",
    "la": "Spencer Huck",
    "ba": "Steven Kinne",
    "ak": "2932 michaux st",
    "nr": 1
  },
  {
    "id": "s59376489",
    "a": "242 E 28th Street",
    "lat": 29.812069,
    "lng": -95.396813,
    "cp": 510000,
    "lp": 520000,
    "sq": 2939,
    "psf": 173.5,
    "cd": "2025-09-18",
    "mo": "2025-09",
    "dom": 5,
    "yb": 2013,
    "coh": "resale",
    "band": "<800k",
    "win": "180-365",
    "prod": "Unknown",
    "svl": -0.0192,
    "sch": "HELMS ELEMENTARY SCHOOL",
    "la": "Ashley Graves",
    "ba": "Tiffany Payne",
    "ak": "242 28th st e",
    "nr": 1
  },
  {
    "id": "s55821001",
    "a": "323 W 23rd Street",
    "lat": 29.807177,
    "lng": -95.402515,
    "cp": 1239000,
    "lp": 1289000,
    "sq": 2750,
    "psf": 450.5,
    "cd": "2025-09-16",
    "mo": "2025-09",
    "dom": 0,
    "yb": 2025,
    "coh": "nc",
    "band": "800k-1.3M",
    "win": "180-365",
    "prod": "Unknown",
    "svl": -0.0388,
    "p": 1,
    "bl": "Enterra Homes",
    "sch": "HELMS ELEMENTARY SCHOOL",
    "la": "Tommy Walker",
    "ba": "Maria Olguin",
    "ak": "323 w 23rd st",
    "nr": 1
  },
  {
    "id": "s15221728",
    "a": "1210 W 23rd Street",
    "lat": 29.806403,
    "lng": -95.419978,
    "cp": 520000,
    "lp": 535000,
    "sq": 1883,
    "psf": 276.2,
    "cd": "2025-09-09",
    "mo": "2025-09",
    "dom": 43,
    "yb": 2025,
    "coh": "nc",
    "band": "<800k",
    "win": "180-365",
    "prod": "Unknown",
    "svl": -0.028,
    "bl": "CIVE",
    "sch": "SINCLAIR ELEMENTARY SCHOOL (HOUSTON)",
    "la": "Eli Stephan",
    "ba": "Anisa Hoxha",
    "ak": "1210 w 23rd st",
    "nr": 1
  },
  {
    "id": "s4197682",
    "a": "325 W 23rd Street",
    "lat": 29.807177,
    "lng": -95.402515,
    "cp": 1165020,
    "lp": 1199000,
    "sq": 2721,
    "psf": 428.2,
    "cd": "2025-09-05",
    "mo": "2025-09",
    "dom": 14,
    "yb": 2025,
    "coh": "nc",
    "band": "800k-1.3M",
    "win": "365+",
    "prod": "Unknown",
    "svl": -0.0283,
    "bl": "Enterra Homes",
    "sch": "HELMS ELEMENTARY SCHOOL",
    "la": "Tommy Walker",
    "ba": "Tommy Walker",
    "ak": "325 w 23rd st",
    "nr": 1
  },
  {
    "id": "s16275355",
    "a": "1216 W 23rd Street",
    "lat": 29.806403,
    "lng": -95.420049,
    "cp": 505000,
    "lp": 509900,
    "sq": 1624,
    "psf": 311.0,
    "cd": "2025-08-14",
    "mo": "2025-08",
    "dom": 17,
    "yb": 2025,
    "coh": "nc",
    "band": "<800k",
    "win": "365+",
    "prod": "Unknown",
    "svl": -0.0096,
    "bl": "CIVE",
    "sch": "SINCLAIR ELEMENTARY SCHOOL (HOUSTON)",
    "la": "Eli Stephan",
    "ba": "Adeela Rashid",
    "ak": "1216 w 23rd st",
    "nr": 1
  }
]
```

## Verification commands and actual output

`/Users/nemoclaw/insp-venv/bin/python -B sold_ingest.py --dry-run --as-of 2026-09-08` ran before apply. `/Users/nemoclaw/insp-venv/bin/python -B sold_ingest.py --apply --as-of 2026-09-08` then ran twice. Actual second report:

```json
{
  "mode": "APPLY",
  "as_of": "2026-09-08",
  "files": [
    {
      "file": "Heightssoldsinglelotslast30days.csv",
      "read": 33,
      "added": 0,
      "updated": 0,
      "excluded": {
        "DUP_EXISTING": 31,
        "MISSING_REQUIRED_FIELD": 2
      },
      "crosscheck_matches": 33
    },
    {
      "file": "Heightssoldsplitlotslast30days.csv",
      "read": 23,
      "added": 0,
      "updated": 0,
      "excluded": {
        "DUP_EXISTING": 23
      },
      "crosscheck_matches": 23
    }
  ],
  "old_total": 764,
  "new_total": 764,
  "products": {
    "Single Lot": 411,
    "Split Lot": 345,
    "Unknown": 8
  },
  "crosscheck_mismatches": [],
  "flagged": [
    {
      "id": "s41813835",
      "address": "521 W 22nd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s71522503",
      "address": "2916 Michaux Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s63496941",
      "address": "2932 Michaux Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s59376489",
      "address": "242 E 28th Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s55821001",
      "address": "323 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s15221728",
      "address": "1210 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s4197682",
      "address": "325 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s16275355",
      "address": "1216 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    }
  ],
  "html_changed": false,
  "ledger_rows": 56
}
```

Independent SHA256 comparisons:

```text
Stored records changed: 56; only prod and obsolete nr flag changed: PASS
All eight hand-authored DATA arrays byte-identical: PASS
Second ingest: added=0 updated=0 html_changed=false; index.html + sold_emit.txt byte-identical PASS
```

The existing two missing-building-area rows remain excluded, and 54 accepted input rows are now duplicates; all decisions remain in the existing ignored sold ledger. This run adds no transaction.

`/Users/nemoclaw/insp-venv/bin/python -B /tmp/sold_floor_browser.py --after` actual output:

```text
0-30 panel: Sold Comps 54; LOT TYPE · 0-30 DAYS; Single Lot 31; Split Lot 23; Unknown 0
Reclassified popup: 415 W 16th Street Unit#D; Split Lot; $599,000; 2,394 sqft; $250.2/sqft; 1,808 sqft lot; 2026-08-06; 26 DOM
Conflicts: 1121 E 24th Street, 1125 E 24th Street, 308 E 28th Street — sold Split Lot; construction Single Lot
Page errors: []
```

The conflict count remains three. All three have 3000 sqft sold lot areas and therefore were Split before and after. Audit uses stored construction labels and seed tags; remote shared edits are intercepted during tests. No construction classifier or data was changed.

`/Users/nemoclaw/insp-venv/bin/python -B tests/browser_calibration.py --output /tmp/sold-floor-stage.json --all-markets` output:

```text
gardenoaksoakforest.html: taxonomy tests 83/83; property fixtures 0/0
index.html: taxonomy tests 83/83; property fixtures 12/12
montrose.html: taxonomy tests 83/83; property fixtures 0/0
riveroaks.html: taxonomy tests 83/83; property fixtures 0/0
springbranch.html: taxonomy tests 83/83; property fixtures 0/0
springvalley.html: taxonomy tests 83/83; property fixtures 0/0
timbergrove.html: taxonomy tests 83/83; property fixtures 0/0
westu.html: taxonomy tests 83/83; property fixtures 0/0
page errors: []
```

`git diff --stat` before this report:

```text
 index.html             | 15 +++++++++------
 sold_classification.py |  6 ++----
 sold_emit.txt          |  4 ++--
 sold_ingest.py         |  6 +++---
 4 files changed, 16 insertions(+), 15 deletions(-)
```

No stage classifier, permit pull, inspection scraper, deed ingest or hand-authored DATA was modified.
