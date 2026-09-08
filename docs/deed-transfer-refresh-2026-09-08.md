# Deed transfer refresh — 2026-09-08

## Phase 0 — source and schema

The live layer is embedded in `index.html` DATA; `heights_deed.data.json` is historical cross-reference metadata, not a fetched layer. DATA has no `kind: "deed"` records. LIFE entries with `s: "deed"` seed `state.points[id].tags = ["deed"]`. `deedCount()` calls `tagCount('deed')`, which requires a rendered marker in `mById` and sums `UW(id)`.

Read-only commands executed before building:

- `cat sold_ingest.py` (entire file).
- Python JSONDecoder probes of DATA, LIFE, SEED_POINTS, the historical metadata, the real CSV, and all configured market polygons.
- `/Users/nemoclaw/insp-venv/bin/python -B tests/browser_calibration.py --output /tmp/deed-phase0-browser.json`.
- `/Users/nemoclaw/insp-venv/bin/python -B /tmp/deed_discovery.py` (initial read-only browser audit, baseline saved to `/tmp/deed-baseline.json`).

Actual baseline output:

```text
DATA 409
LIFE 240
LIFE deed DATA 133
LIFE deed total 137
raw deeds 133 after zone 133
executed browser deedCount: 118
tagged deed rows 118
missingMarkers: []
page errors: []
```

Thirteen of those 133 raw deed entries have advanced by inspection evidence. Of the other two absent runtime rows, 527 W 27th is removed in split-project pairing; 241 W 26th has `st: "sold"` and is filtered from the live map. Four LIFE deed IDs have no DATA row. This explains both the displayed 118 and the earlier zero-field probe. No existing filtering or classification was changed.

The existing deed record shape is:

```javascript
{
  id: "2131238842",                       // DealMachine property ID, not APN
  a: "905 Dorothy St, Houston, Tx 77008",
  llc: "Terra Holdings Group Inc",
  v: "$402,022",                         // Assessed, NOT sale price
  sd: "2026-07-09",                      // Sale date
  lot: "4750",
  f: "Recently Sold, High Equity, Corporate Owner",
  u: "https://app.dealmachine.com/leads#property(id)=2131238842",
  lat: 29.787195,
  lng: -95.40857,
  c: null                               // existing contact shape: [{n, p: [], e: []}]
}
```

Existing rows can additionally carry `ty`, `prod`, `permits`, and `st`. The popup reads owner/address, assessed value, sale date, lot area, flags, contact name/phone/email arrays, and DealMachine URL. It also reads runtime notes/tags, the per-ID DEED_PULL capture date, permit objects (`desc`, `owner`, `permitDesc`, `val`, `proj`) and the inspection feed. Active-row-only branches read `comp`/`bb` and interpret `v`, `sd`, `lot` differently; the ingest preserves those listing fields on matched active pins. Pairing can add `_chip`, `_twin`, `_soloSplit`, and `units` at runtime. The ingest does not invent those fields.

New rows have the same base keys and `c: null`; no contact fields were imported. Unknown optional product/status/permit fields are left absent, with no inferred product or stage. APN and year built use the already-existing historical metadata fields `apn` and `year_built`. No sale-price column exists in this export, so no sale price is fabricated. Assessment components, estimated value, property type, corporate flag, market status, and assemblage relationships are not new DATA fields. Property type validates input; corporate owners remain eligible.

`sold_ingest.py` stays untouched. Its date/numeric parsing and polygon method are useful concepts, but it deduplicates MLS IDs, expects HAR headers, computes sold-comp cohorts and metrics, and emits SOLD_DATA/SOLD_METRICS into sold_emit.txt. It performs no geocoding, no cross-market routing, and no deed update. The new pipeline uses CSV coordinates and imports none of its sold-comp behavior.

## Market boundary rule

Use every enabled market in market_config.py. Polygon containment is authoritative for markets with polygons; West U retains its configured 77005-plus-coordinate-box rule. After polygon assignment, enforce the destination HTML street regex and the configured east_lng cutoff (Heights only). Multiple eligible destinations or conflicting existing-pin markets are explicitly excluded, not guessed. The script fails closed when required HTML/JSON inputs cannot be parsed.

The `lng > -95.370` rejection removes EASTERN points. Actual CSV probe: 28 west of/equal to the cutoff, 16 east. The western 28 pass the longitude check. The Heights polygon itself extends east of the cutoff; the browser globally applies both checks to all Heights DATA, including deeds. This is not merely a permit filter. Sold comps also have this guard; other market configs set east_lng to None. Thus the cutoff is appropriate to this map's current Heights coverage and was not reversed or broadened.

6727 Grovewood Ln, 2326 Haverhill Dr, and 2230 Tannehill Dr are inside Timbergrove's polygon and route there. Both Washington Avenue parcels are outside every tracked polygon. Of 18 exclusions, 9 are inside the Heights polygon but fail its eastern cutoff, and 9 are outside every tracked polygon (7 farther east plus the 2 Washington addresses).

The existing `permit_pull.write_dropped_ledger()` is reused without modifying permit_pull.py. Before building, it was invoked on the real 6309 Washington row in `/tmp/deed-ledger-audit.csv`, producing:

```csv
MARKET,PROJECT_NO,ADDRESS,REASON,DETAIL
heights,,6309 Washington Ave,OUT_OF_MARKET,deed source row; parcel 054-111-000-0023
```

Deed exclusions have an empty PROJECT_NO. DETAIL carries source SHA-256, physical CSV row number, normalized APN, and reason detail. Repeated identical exclusions do not append duplicates. Accepted existing records are reported as UNCHANGED rather than treated as excluded rows.

## Full dry-run output

Command: `/Users/nemoclaw/insp-venv/bin/python -B deed_ingest.py dealmachine-properties-deedtransfersheights.csv --dry-run`

```text
DRY RUN | source=dealmachine-properties-deedtransfersheights.csv | rows read=44
Rule: configured polygons; Heights street guard + lng <= -95.370; route across enabled markets.
02 UNCHANGED 905 Dorothy St -> heights | id=2131238842
03 ADDED 1439 Laird St -> heights | id=2131085991
04 ADDED 1133 Adele St -> heights | id=2131191490
05 ADDED 1440 Arlington St -> heights | id=2131043751
06 ADDED 1619 Cortlandt St -> heights | id=2131283575
07 ADDED 1424 Ashland St -> heights | id=2131284732
08 ADDED 813 Bayland Ave -> heights | id=2131249205
09 UNCHANGED 1516 Lawrence St -> heights | id=2131218924
10 ADDED 1811 W 14th 1/2 St -> heights | id=2131475807
11 ADDED 1129 Highland St -> heights | id=2131374679
12 ADDED 1014 Robbie St -> heights | id=2131191859
13 ADDED 1005 E 27th St -> heights | id=2131208519
14 ADDED 6727 Grovewood Ln -> timbergrove | id=2130421544
15 ADDED 2326 Haverhill Dr -> timbergrove | id=2130573149
16 ADDED 2230 Tannehill Dr -> timbergrove | id=2130573761
17 EXCLUDE 1307 Genova St | OUT_OF_MARKET: outside all tracked market boundaries
18 EXCLUDE 3807 Edison St | OOZ_EAST: no other tracked market
19 EXCLUDE 3903 Billingsley St # 1 | OOZ_EAST: no other tracked market
20 EXCLUDE 5418 Elysian St | OUT_OF_MARKET: outside all tracked market boundaries
21 EXCLUDE 1309 Tarley St | OUT_OF_MARKET: outside all tracked market boundaries
22 EXCLUDE 1502 Fairbanks St | OUT_OF_MARKET: outside all tracked market boundaries
23 ADDED 1031 Nadine St -> heights | id=2131191265
24 ADDED 206 Tabor St -> heights | id=2131227325
25 ADDED 1604 Spring St -> heights | id=2131271381
26 ADDED 1017 Rutland St -> heights | id=2131285466
27 EXCLUDE 4718 Averill St | OOZ_EAST: no other tracked market
28 EXCLUDE 1221 Lee St | OUT_OF_MARKET: outside all tracked market boundaries
29 EXCLUDE 5017 Terry St | OUT_OF_MARKET: outside all tracked market boundaries
30 ADDED 617 Peddie St -> heights | id=2131312302
31 EXCLUDE 6309 Washington Ave | OUT_OF_MARKET: outside all tracked market boundaries
32 EXCLUDE 6311 Washington Ave | OUT_OF_MARKET: outside all tracked market boundaries
33 ADDED 1144 Dorothy St -> heights | id=2131360419
34 EXCLUDE 4002 Beggs St | OOZ_EAST: no other tracked market
35 ADDED 912 Robbie St -> heights | id=2131370516
36 ADDED 1126 Bayland Ave -> heights | id=2131374781
37 EXCLUDE 3816 Moore St | OUT_OF_MARKET: outside all tracked market boundaries
38 ADDED 1214 Farwood St -> heights | id=2131377369
39 ADDED 1317 Oleander St -> heights | id=2131377371
40 ADDED 1315 Oleander St -> heights | id=2131377372
41 EXCLUDE 1313 Oleander St | OOZ_EAST: no other tracked market
42 EXCLUDE 1215 Farwood St | OOZ_EAST: no other tracked market
43 EXCLUDE 906 Booth St | OOZ_EAST: no other tracked market
44 EXCLUDE 904 Booth St | OOZ_EAST: no other tracked market
45 EXCLUDE 301 Kelley St | OOZ_EAST: no other tracked market
TOTAL read=44 accepted=26 added=24 updated=0 unchanged=2 excluded=18
MARKET heights: added=21 updated=0 unchanged=2
MARKET timbergrove: added=3 updated=0 unchanged=0
EXCLUSIONS {"OOZ_EAST": 9, "OUT_OF_MARKET": 9}
PERMIT OVERLAPS 0
FILES index.html, heights_deed.data.json, timbergrove.html, timbergrove_deed.data.json
LEDGER pulls/dropped_2026-09-08.csv: excluded=18 new_entries=18
No files written.
```

Byte comparison around dry-run returned `DRY-RUN HASH CHECK: 8 files unchanged`.

## Apply output

Command: `/Users/nemoclaw/insp-venv/bin/python -B deed_ingest.py dealmachine-properties-deedtransfersheights.csv` (first invocation run through Python trace to verify function execution).

```text
APPLY | source=dealmachine-properties-deedtransfersheights.csv | rows read=44
Rule: configured polygons; Heights street guard + lng <= -95.370; route across enabled markets.
02 UNCHANGED 905 Dorothy St -> heights | id=2131238842
03 ADDED 1439 Laird St -> heights | id=2131085991
04 ADDED 1133 Adele St -> heights | id=2131191490
05 ADDED 1440 Arlington St -> heights | id=2131043751
06 ADDED 1619 Cortlandt St -> heights | id=2131283575
07 ADDED 1424 Ashland St -> heights | id=2131284732
08 ADDED 813 Bayland Ave -> heights | id=2131249205
09 UNCHANGED 1516 Lawrence St -> heights | id=2131218924
10 ADDED 1811 W 14th 1/2 St -> heights | id=2131475807
11 ADDED 1129 Highland St -> heights | id=2131374679
12 ADDED 1014 Robbie St -> heights | id=2131191859
13 ADDED 1005 E 27th St -> heights | id=2131208519
14 ADDED 6727 Grovewood Ln -> timbergrove | id=2130421544
15 ADDED 2326 Haverhill Dr -> timbergrove | id=2130573149
16 ADDED 2230 Tannehill Dr -> timbergrove | id=2130573761
17 EXCLUDE 1307 Genova St | OUT_OF_MARKET: outside all tracked market boundaries
18 EXCLUDE 3807 Edison St | OOZ_EAST: no other tracked market
19 EXCLUDE 3903 Billingsley St # 1 | OOZ_EAST: no other tracked market
20 EXCLUDE 5418 Elysian St | OUT_OF_MARKET: outside all tracked market boundaries
21 EXCLUDE 1309 Tarley St | OUT_OF_MARKET: outside all tracked market boundaries
22 EXCLUDE 1502 Fairbanks St | OUT_OF_MARKET: outside all tracked market boundaries
23 ADDED 1031 Nadine St -> heights | id=2131191265
24 ADDED 206 Tabor St -> heights | id=2131227325
25 ADDED 1604 Spring St -> heights | id=2131271381
26 ADDED 1017 Rutland St -> heights | id=2131285466
27 EXCLUDE 4718 Averill St | OOZ_EAST: no other tracked market
28 EXCLUDE 1221 Lee St | OUT_OF_MARKET: outside all tracked market boundaries
29 EXCLUDE 5017 Terry St | OUT_OF_MARKET: outside all tracked market boundaries
30 ADDED 617 Peddie St -> heights | id=2131312302
31 EXCLUDE 6309 Washington Ave | OUT_OF_MARKET: outside all tracked market boundaries
32 EXCLUDE 6311 Washington Ave | OUT_OF_MARKET: outside all tracked market boundaries
33 ADDED 1144 Dorothy St -> heights | id=2131360419
34 EXCLUDE 4002 Beggs St | OOZ_EAST: no other tracked market
35 ADDED 912 Robbie St -> heights | id=2131370516
36 ADDED 1126 Bayland Ave -> heights | id=2131374781
37 EXCLUDE 3816 Moore St | OUT_OF_MARKET: outside all tracked market boundaries
38 ADDED 1214 Farwood St -> heights | id=2131377369
39 ADDED 1317 Oleander St -> heights | id=2131377371
40 ADDED 1315 Oleander St -> heights | id=2131377372
41 EXCLUDE 1313 Oleander St | OOZ_EAST: no other tracked market
42 EXCLUDE 1215 Farwood St | OOZ_EAST: no other tracked market
43 EXCLUDE 906 Booth St | OOZ_EAST: no other tracked market
44 EXCLUDE 904 Booth St | OOZ_EAST: no other tracked market
45 EXCLUDE 301 Kelley St | OOZ_EAST: no other tracked market
TOTAL read=44 accepted=26 added=24 updated=0 unchanged=2 excluded=18
MARKET heights: added=21 updated=0 unchanged=2
MARKET timbergrove: added=3 updated=0 unchanged=0
EXCLUSIONS {"OOZ_EAST": 9, "OUT_OF_MARKET": 9}
PERMIT OVERLAPS 0
FILES index.html, heights_deed.data.json, timbergrove.html, timbergrove_deed.data.json
LEDGER pulls/dropped_2026-09-08.csv: excluded=18 new_entries=18
WROTE 4 files; ledger rows appended=18
```

All 13 functions executed against the real export: assign, elements, encode, in_boundary, in_ring, load_markets, main, normalize, number, parcel, patch, span, validate.

## Idempotency and preservation

An immediate second CLI invocation returned:

```text
APPLY | source=dealmachine-properties-deedtransfersheights.csv | rows read=44
Rule: configured polygons; Heights street guard + lng <= -95.370; route across enabled markets.
02 UNCHANGED 905 Dorothy St -> heights | id=2131238842
03 UNCHANGED 1439 Laird St -> heights | id=2131085991
04 UNCHANGED 1133 Adele St -> heights | id=2131191490
05 UNCHANGED 1440 Arlington St -> heights | id=2131043751
06 UNCHANGED 1619 Cortlandt St -> heights | id=2131283575
07 UNCHANGED 1424 Ashland St -> heights | id=2131284732
08 UNCHANGED 813 Bayland Ave -> heights | id=2131249205
09 UNCHANGED 1516 Lawrence St -> heights | id=2131218924
10 UNCHANGED 1811 W 14th 1/2 St -> heights | id=2131475807
11 UNCHANGED 1129 Highland St -> heights | id=2131374679
12 UNCHANGED 1014 Robbie St -> heights | id=2131191859
13 UNCHANGED 1005 E 27th St -> heights | id=2131208519
14 UNCHANGED 6727 Grovewood Ln -> timbergrove | id=2130421544
15 UNCHANGED 2326 Haverhill Dr -> timbergrove | id=2130573149
16 UNCHANGED 2230 Tannehill Dr -> timbergrove | id=2130573761
17 EXCLUDE 1307 Genova St | OUT_OF_MARKET: outside all tracked market boundaries
18 EXCLUDE 3807 Edison St | OOZ_EAST: no other tracked market
19 EXCLUDE 3903 Billingsley St # 1 | OOZ_EAST: no other tracked market
20 EXCLUDE 5418 Elysian St | OUT_OF_MARKET: outside all tracked market boundaries
21 EXCLUDE 1309 Tarley St | OUT_OF_MARKET: outside all tracked market boundaries
22 EXCLUDE 1502 Fairbanks St | OUT_OF_MARKET: outside all tracked market boundaries
23 UNCHANGED 1031 Nadine St -> heights | id=2131191265
24 UNCHANGED 206 Tabor St -> heights | id=2131227325
25 UNCHANGED 1604 Spring St -> heights | id=2131271381
26 UNCHANGED 1017 Rutland St -> heights | id=2131285466
27 EXCLUDE 4718 Averill St | OOZ_EAST: no other tracked market
28 EXCLUDE 1221 Lee St | OUT_OF_MARKET: outside all tracked market boundaries
29 EXCLUDE 5017 Terry St | OUT_OF_MARKET: outside all tracked market boundaries
30 UNCHANGED 617 Peddie St -> heights | id=2131312302
31 EXCLUDE 6309 Washington Ave | OUT_OF_MARKET: outside all tracked market boundaries
32 EXCLUDE 6311 Washington Ave | OUT_OF_MARKET: outside all tracked market boundaries
33 UNCHANGED 1144 Dorothy St -> heights | id=2131360419
34 EXCLUDE 4002 Beggs St | OOZ_EAST: no other tracked market
35 UNCHANGED 912 Robbie St -> heights | id=2131370516
36 UNCHANGED 1126 Bayland Ave -> heights | id=2131374781
37 EXCLUDE 3816 Moore St | OUT_OF_MARKET: outside all tracked market boundaries
38 UNCHANGED 1214 Farwood St -> heights | id=2131377369
39 UNCHANGED 1317 Oleander St -> heights | id=2131377371
40 UNCHANGED 1315 Oleander St -> heights | id=2131377372
41 EXCLUDE 1313 Oleander St | OOZ_EAST: no other tracked market
42 EXCLUDE 1215 Farwood St | OOZ_EAST: no other tracked market
43 EXCLUDE 906 Booth St | OOZ_EAST: no other tracked market
44 EXCLUDE 904 Booth St | OOZ_EAST: no other tracked market
45 EXCLUDE 301 Kelley St | OOZ_EAST: no other tracked market
TOTAL read=44 accepted=26 added=0 updated=0 unchanged=26 excluded=18
MARKET heights: added=0 updated=0 unchanged=23
MARKET timbergrove: added=0 updated=0 unchanged=3
EXCLUSIONS {"OOZ_EAST": 9, "OUT_OF_MARKET": 9}
PERMIT OVERLAPS 0
FILES (none)
LEDGER pulls/dropped_2026-09-08.csv: excluded=18 new_entries=0
WROTE 0 files; ledger rows appended=0
```

A byte comparison against the first-run snapshot returned:

```text
SECOND RUN BYTE DIFF: [] files checked: 10
```

The browser revealed duplicate lifecycle note text in the new seed entries. The new notes were aligned with the existing `Lifecycle:` prefix, then the browser checks were rerun successfully. After that correction, two further actual CLI invocations both returned:

```text
TOTAL read=44 accepted=26 added=0 updated=0 unchanged=26 excluded=18
FILES (none)
LEDGER pulls/dropped_2026-09-08.csv: excluded=18 new_entries=0
WROTE 0 files; ledger rows appended=0
FINAL SECOND-RUN DIFF: [] (10 HTML/metadata/ledger files byte-identical)
```

Surgical preservation checks used JSONDecoder element offsets and compared the original raw text, not just parsed values:

```text
index.html: 409/409 original DATA objects BYTE IDENTICAL; original array prefix preserved; added 21
index.html: changed lines 4; line counts 2263 2263
timbergrove.html: 38/38 original DATA objects BYTE IDENTICAL; original array prefix preserved; added 3
timbergrove.html: changed lines 4; line counts 1922 1922
Historical metadata pulls unchanged: 1
```

Only DATA, SEED_POINTS, LIFE, and DEED_PULL JSON entries were edited. DATA was never reserialized. The original array text excluding its closing bracket is an exact prefix of the updated array. The script validates the full spliced DATA JSON, unique IDs, and all four containers, then masks their spans and proves the remainder of the HTML is identical, including RECONCILE, stage code, and inspection code.

`git diff --check` returned no output. Pre-staging `git diff --stat` (new untracked files are absent from this view) returned:

```text
 heights_deed.data.json | 327 ++++++++++++++++++++++++++++++++++++++++++++++++-
 index.html             |   8 +-
 timbergrove.html       |   8 +-
 3 files changed, 334 insertions(+), 9 deletions(-)
```

Additional isolated-copy tests ran using the real export:

Command: `/Users/nemoclaw/insp-venv/bin/python -B /tmp/deed_regressions.py`

```text
PASS real CSV updates existing deed date/assessment on same permit ID; permit data and stage tags preserved; overlap reported
PASS parcel-first dedupe finds address alias without adding a disconnected pin
PASS normalized-address fallback retains existing ID when parcel history is unavailable
PASS second run after update/permit/alias fixtures has zero file changes, including ledger
```

These four checks deliberately changed existing records in a temporary copy; they did not modify the production input or repository data.

## Three rendered popup checks

Command: `/Users/nemoclaw/insp-venv/bin/python -B /tmp/deed_discovery.py`

Browser checks open each real map marker and wait for its own rendered popup before comparing against its CSV row. Shared-edit writes are intercepted; local tests use an empty remote-edit response. The export itself is never sent to a service.

### 1133 Adele St — heights

CSV sale date: 2026-08-03; CSV assessed value: $407,019; ID: 2131191490. Actual popup text:

```text
ROC HOMES TEXAS LTD
1133 Adele St, Houston, Tx 77009
NO PERMIT ACTIVITY
ASSESSED
$407,019
SALE DATE
2026-08-03
LOT SQ FT
5,000
Pulled: Sep 08, 2026
TAGS
Deed Transfer
NOTES
LIFECYCLE
Deed transfer 2026-08-03 · Roc Homes Texas Ltd
Recently Sold
Off Market
Low Equity
Senior Owner
Corporate Owner
OPEN IN DEALMACHINE
```

### 1439 Laird St — heights

CSV sale date: 2026-08-03; CSV assessed value: $956,233; ID: 2131085991. Actual popup text:

```text
1702 MCGOWEN LLC
1439 Laird St, Houston, Tx 77008
NO PERMIT ACTIVITY
ASSESSED
$956,233
SALE DATE
2026-08-03
LOT SQ FT
10,000
Pulled: Sep 08, 2026
TAGS
Deed Transfer
NOTES
LIFECYCLE
Deed transfer 2026-08-03 · 1702 Mcgowen Llc
Recently Sold
Low Equity
Absentee Owner
Corporate Owner
OPEN IN DEALMACHINE
```

### 6727 Grovewood Ln — timbergrove

CSV sale date: 2026-07-29; CSV assessed value: $535,085; ID: 2130421544. Actual popup text:

```text
6727 GROVEWOOD LLC
6727 Grovewood Ln, Houston, Tx 77008
NO PERMIT ACTIVITY
ASSESSED
$535,085
SALE DATE
2026-07-29
LOT SQ FT
8,645
Pulled: Sep 08, 2026
TAGS
Deed Transfer
NOTES
LIFECYCLE
Deed transfer 2026-07-29 · 6727 Grovewood Llc
Recently Sold
Off Market
Cash Buyer
High Equity
Senior Owner
Corporate Owner
OPEN IN DEALMACHINE
```

Actual browser summary:

```text
Heights Layers: Deed Transfer 139 / Recently sold 139
Timbergrove Layers: Deed Transfer 3 / Recently sold 3
prior_deeds_retained: 118
RETURNING VISITOR: 139
PAGE ERRORS: []
```

All 118 old deed IDs remain tagged and rendered. The original records are byte-identical. The Timbergrove example is absent from Heights. Washington parcels are absent from Heights and have ledger rows below.

## Permit/deed overlap list

Actual complete-input result: `PERMIT OVERLAPS 0`.

The check compared normalized addresses across DATA and permits JSONs for all seven enabled markets. Available historical APNs are used first for pin deduplication, followed by normalized address. Existing DATA/permit inventories have no APN fields, so APN-only permit matches with different street addresses cannot be proven without additional parcel linkage. No nearby-address or same-owner guess was used to merge separate properties. The two existing deed matches were 905 Dorothy St and 1516 Lawrence St; both already have the input sale date and assessment and were unchanged.

## Full dropped ledger for this input

File: `pulls/dropped_2026-09-08.csv` (gitignored; not deployed). All 18 exclusions:

```csv
MARKET,PROJECT_NO,ADDRESS,REASON,DETAIL
heights,,1307 Genova St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=17; parcel=0111470000009; outside all tracked market boundaries
heights,,3807 Edison St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=18; parcel=0211750430013; Heights lng -95.363196 > -95.370; no other tracked market
heights,,3903 Billingsley St # 1,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=19; parcel=0211750440023; Heights lng -95.362163 > -95.370; no other tracked market
heights,,5418 Elysian St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=20; parcel=0311790000001; outside all tracked market boundaries
heights,,1309 Tarley St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=21; parcel=0311820000011; outside all tracked market boundaries
heights,,1502 Fairbanks St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=22; parcel=0311840000001; outside all tracked market boundaries
heights,,4718 Averill St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=27; parcel=0211880810002; Heights lng -95.363623 > -95.370; no other tracked market
heights,,1221 Lee St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=28; parcel=0230210000017; outside all tracked market boundaries
heights,,5017 Terry St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=29; parcel=0311480000003; outside all tracked market boundaries
heights,,6309 Washington Ave,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=31; parcel=0541110000023; outside all tracked market boundaries
heights,,6311 Washington Ave,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=32; parcel=0541110000112; outside all tracked market boundaries
heights,,4002 Beggs St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=34; parcel=0550590000011; Heights lng -95.365287 > -95.370; no other tracked market
heights,,3816 Moore St,OUT_OF_MARKET,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=37; parcel=0550030000009; outside all tracked market boundaries
heights,,1313 Oleander St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=41; parcel=0571440000013; Heights lng -95.369973 > -95.370; no other tracked market
heights,,1215 Farwood St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=42; parcel=0571450000004; Heights lng -95.36985 > -95.370; no other tracked market
heights,,906 Booth St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=43; parcel=0542630000122; Heights lng -95.362537 > -95.370; no other tracked market
heights,,904 Booth St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=44; parcel=0542630000124; Heights lng -95.362685 > -95.370; no other tracked market
heights,,301 Kelley St,OOZ_EAST,deed sha256=b692bfa09137439b5c5def9a702c02b7c09344cb0cb9d12407603ec817cc2e69; row=45; parcel=0660640430034; Heights lng -95.368147 > -95.370; no other tracked market
```

## Shipping

Code and data are committed separately; only git push to main deploys. The source CSV remains untracked and is not staged. No Netlify API deploy path is used. Live verification is recorded separately after the push.

## Open items

- Actual transaction price is unavailable. `v` remains assessed value. Propose a separately labeled sale-price field only when a source supplies it.
- Proposed future schema extensions: estimated value, assessment components, explicit market status, and related-parcel/assemblage links. None implemented. The two Washington lots share Juergen 32 Llc and the 2026-08-19 sale date but are outside tracked coverage.
- Historical APNs exist for the previous 25-row pull, not every legacy deed/permit. Address fallback is required for those older rows; a full parcel cross-reference would improve future linkage.
- Several Farwood/Oleander addresses straddle the existing numeric cutoff. This ingest preserves the configured rule; any coverage change should update the authoritative boundary/render rules together in a separate task.
- HAR sold comps remain separate. Unifying their transaction history with deed history would require explicit price/source semantics and identity reconciliation; sold_ingest.py was not modified.
