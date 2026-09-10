# Heights market ingest and permit backfill — 2026-09-10

Executed locally on the Mac Mini. Market data was applied before permit DATA. No boundary, stage-classifier, timeline, RECONCILE, or DUP_ADDR merge changes. Raw exports remain untracked.

## Phase A: market evidence

`python -B combined_market_ingest.py --runtime /tmp/market-runtime.json --output pulls/market_backfill_20260910/phase_a --apply` returned:

```text
rows 513; columns 26; unique MLS 513
Active 65; Pending 14; Sold 140; Withdrawn 4; Expired 29; Terminated 258; Terminated-Relisted 3
Single Lot 210; Split Lot 303; missing/unparseable lots 0
Sold closing range 2025-07-01 through 2026-09-04
new 284; updated 225; already held 0; ledgered 4
sold before 767; after 791; original resale comps preserved 637
```

Sold → sold; Active → active; Pending → pending. Withdrawn, Expired, Terminated, and Terminated-Relisted → terminated. `har_status` and the original source row retain the exact HAR status; cards/history now display it. Counts above describe listing-evidence records, not new pins. Existing MLS identities are refreshed; different MLS listings at the same normalized address remain history, not duplicate homes. The sold archive adds 24 transactions; new registry records can overlap transactions already in that archive. All 767 prior sale identities survive; all 637 original resale objects are exactly unchanged. Four new year-2024 sales use the existing resale-cohort convention, bringing that cohort to 641.

All four excluded rows are 1822 W 23rd Street (MLS 73224522, 98009765, 75428614, 63800829), excluded by the unchanged existing street rule. Ledger: `pulls/dropped_combined_market_2026-09-10.csv`. 284 + 225 + 0 + 4 = 513.

127 literal addresses have multiple listings; normalization yields 129 multi-listing properties. Aliases include 611B E 25th / 611 E 25th Unit B, 1438 A/B Dian unit placement, repeated Street at 830 E 27th, and Nashua St/Street. Of the multi-listing properties, one previously held current status changes: 1109 Tabor, Terminated → Active. Another 54 gain a first known current status. Resolution remains sold > pending > active > terminated, then known event date. Same-status non-sold ties lack event dates and remain explicitly flagged; MLS ordering is a display reference, not claimed chronology.

715 Merrill: Active MLS 88557637, with terminated MLS 50361472 retained as visible history.

Second identical invocation returned `held: 509`, `ledgered: 4`, `changed_files: []`. The importer compares output text and writes only changed files, so files remain byte-identical.

## Phase B: permits

`python -B permit_backfill_ingest.py --min-proj-year 24 --finals-since 2025-07-01` replayed the reviewed 2026-09-09 HCAD responses through the current engine: 191 before cutoff, 174 selected, 17 old-final exclusions. Both 6808 N Main A and 102 Sylvester remain excluded. This was a cached-evidence replay, not a new 602-address network pull.

Fresh HCAD invocation for 742 Allston returned `FAIL`. A local Census query returned exactly `742 ALLSTON ST, HOUSTON, TX, 77007`, at 29.784142313405, -95.399882128768, inside the existing boundary. COH scraper returned project 26018730, Partial, seven inspections. Invoking the existing classifier on its passed inspections gives Exterior. This separately recovered hard fixture increases the actual additions to **175**, without changing the original 174 cohort. Its record explicitly identifies the location as Census street interpolation, not an HCAD parcel centroid.

Apply command:
```text
python -B permit_backfill_ingest.py --min-proj-year 24 --finals-since 2025-07-01 --allston-census pulls/market_backfill_20260910/allston_census.json --apply
selected 175; changed index.html, heights_permits.json, inspections.json
repeat: selected 0; changed_files []
```

175 added, zero existing DATA rows updated. Raw permit rows account exactly: **175 accepted + 57,688 ledgered = 57,863**. First-apply ledger: `pulls/market_backfill_20260910/dropped_permits_first_apply.csv`. Exclusions: NOT_SFRES 56,847; OLD_PROJ 97; DUP_PROJ 235; DUP_ADDR 42; OOZ_REGEX 40; OOZ_POLY 169; OOZ_EAST 96; GEOCODE_FAIL 133; GEOCODE_AMBIG 12; FINALS_BEFORE_CUTOFF 17.

**101 Complete arrivals: Sold 44; Active 0; Pending 0; Terminated/Expired 6; No Market Record 51.** All 175 arrivals: Sold 56, Terminated 6, No Market Record 113. Per-permit results: [arrival audit](market-backfill-arrivals-2026-09-10.json).

The retained evidence cohort is still 101 Complete / 40 MEP Finals / 33 without a passed final; Allston adds one Exterior. Actual unchanged runtime classifier renders the 175 as Complete 101, MEP Finals 44, Foundation 15, Interior 11, Exterior 2, Framing 1, MEP Roughs 1. Four 1443 W 25th units roll up from Interior to MEP Finals via the existing shared-project rule. Nine no-stage/no-inspection projects default to Foundation in existing `inspToPhase`. 320 E 18th uses its existing inspection-feed entry (Framing), preserved rather than replaced by a newer standalone audit. These are reported discrepancies, not silently forced to the earlier standalone classification.

Finished grows by 100 represented homes, although 101 Complete permits arrive: 1208 E 26th A previously represented an unnamed second home; adding B reduces A’s weight from 2 to 1 and gives B its own identity. No existing DATA row is edited for that runtime behavior.

## Phase D: display

Finished Active #006B4F; Pending #26A269; Sold #74C69D; Terminated #456B58; No Record #B7E4C7. Exact collision scan against all 66 pre-existing map colors: zero. Browser invocation verifies all five swatches and Finished pin colors. A mixed-status paired pin follows the selected Finished-status filter; otherwise uses the existing status precedence. The shared display hook is identical across all eight pages; classification and forecasting functions are untouched.

Actual shared-edit state before cleanup (counts are represented homes; overlaps are intentional):

| Former row | Homes | Market evidence | Finished overlap | Lose only layer filter if removed alone |
|---|---:|---:|---:|---:|
| Pending / Under Contract | 18 | 17 | 4 | 14 |
| Off Market – Single Lot | 8 | 7 | 1 | 6 |
| Off Market – Split Lot | 6 | 6 | 0 | 4 |
| Needs Clarification | 5 | 1 | 0 | 0 |
| On the Market (building) | 14 | 14 | 0 | 0 |

Both product-specific Off Market rows retired; their resolved, phase-less members are reachable under the new market-evidence row. The unresolved 1016 E 27th home remains under Off market, status unverified. Finished pending homes stay in Finished; non-Complete pending uses market evidence, retaining the one legacy pending home without evidence. Explicit research/product-review tags are now Flagged for review; the construction product fallback is Product type unknown. Stored tags are preserved, and On the Market (building) is unchanged.

| Final Other row | Homes |
|---|---:|
| Flagged for review | 5 |
| On the Market (building) | 14 |
| Pending, not Complete | 13 |
| Off market, status unverified | 1 |
| Market evidence, no construction phase | 47 |

Other header **5 → 75**: root cause was `.leafrow.length`, the number of filters. It now counts the union of represented homes once. Rows sum to 80 because five homes overlap. Invocation comparing all old members to replacement filters returned `Former Other members without replacement: []`.

## Bucket and supply deltas

Both columns below use actual shared edits. A reproducible clean-browser capture also exists; do not mix its baseline with these counts.

| Bucket | Before | After | Delta |
|---|---:|---:|---:|
| Snapshot foundation | 36 | 51 | +15 |
| Snapshot framing | 10 | 11 | +1 |
| Snapshot exterior | 28 | 30 | +2 |
| Snapshot mep_roughs | 5 | 6 | +1 |
| Snapshot insulation | 12 | 12 | +0 |
| Snapshot interior | 51 | 62 | +11 |
| Snapshot mep_finals | 19 | 63 | +44 |
| Snapshot complete | 45 | 145 | +100 |
| Under Construction panel | 164 | 238 | +74 |
| Finished panel | 49 | 149 | +100 |
| Deeds | 139 | 139 | +0 |
| Sold archive | 767 | 791 | +24 |
| Custom | 19 | 19 | +0 |
| Sold Off Market | 1 | 1 | +0 |
| Finished Active | 13 | 13 | +0 |
| Finished Pending | 5 | 5 | +0 |
| Finished Sold | 4 | 48 | +44 |
| Finished Terminated | 3 | 12 | +9 |
| Finished No Market Record | 24 | 71 | +47 |

Finished arithmetic: **13 + 5 + 48 + 12 + 71 = 149**. Snapshot construction columns retain the pre-existing pipeline exclusions; they are not interchangeable with the Finished layer total.

Actual shared-state supply snapshot: **130 − 3 terminated = 127 before; 177 − 3 = 174 after; +47**. Clean-browser deterministic comparison: **131 − 3 = 128 → 178 − 3 = 175**, also +47. Supply is the existing forecast calculation, not a claim that every No Market Record home is unsold.

Shared-state map totals: **375 pins / 422 represented homes → 550 pins / 596 represented homes**.

## Invocation evidence and validation

Artifacts are in `pulls/market_backfill_20260910/`; original timeline logs are `/tmp/timeline-full-{1,2,3}.log`.

```text
python -B -m unittest discover -s tests -p test_permit_pull.py
Ran 9 tests ... OK

python -B tests/full_timeline_check.py
RUN 1/2/3: phase 20706/20706; browser 183/183; base pairs 9039; violations 0; errors []
SHA256 e2aa3cce060b044ba594dc0c1daa40f918b4fc5992f508262da0a66c6d216cfc
PASS: all three full results byte-identical

python -B tests/full_backfill_check.py
BACKFILL RUN 1/2/3: PASS
SHA256 2b87274a435f6ad70fc6ccdb32d9f5c572140d5f34750ae7aa62c70ca728de8d
PASS: three market/backfill/display results byte-identical

DATA original rows byte-preserved: 430; new: 175
Original resale objects unchanged: 637
git diff --numstat 3b59c73 -- index.html: 180 additions, 4 deletions
```

Timeline fixtures pass unchanged: Harvard 21 days overdue (~8 months 3 weeks total), 629 ~6.5 months, Munford/Voight Interior, 112 E 27th and 609 E 25th Complete, 830 E 26th no phase. All existing DATA row bytes preserved; SOLD_DATA is the separate archive constant that changed. Display-only edits add one pin-color hook line per HTML page.

## Open items

- 145 unresolved geocodes remain (133 no match, 12 ambiguous). No coordinates guessed.
- Nine new permits inherit the existing Foundation fallback despite lacking passed stage evidence. The requested classifier/timeline freeze was respected; this conflicts with the broader passed-evidence policy and needs a separate classifier decision.
- Four shared-project phase rollups and one older retained inspection feed explain the other phase-report differences.
- Non-sold event dates are absent; same-status chronology cannot be established from DOM or MLS number.
- DUP_ADDR merge remains deferred; no merge design or duplicate-pin insertion attempted.
- Market coverage is limited to this supplied export; No Market Record is not proof of unsold inventory.


## Deployment and live verification

Pushed `3b59c73..2024706` to `origin main`; Netlify CI deployed the full tree. Commits: `d906de2` ingest code, `951aa08` market data, `75a0686` permit data, `e3220da` display code, `2024706` audit. Every intended application/data file was checked against the committed blob. No API deploy or empty rebuild commit was needed.

`python -B tests/backfill_browser.py --checks --live https://tangerine-sorbet-eca5f5.netlify.app --output pulls/market_backfill_20260910/live.json` exited 0. Actual popup output in `pulls/market_backfill_20260910/live.log`:

```text
LIVE SPOT act_715-merrill
Active; MLS 88557637; Prior listing history: Terminated MLS 50361472
LIVE SPOT pmt_742-allston-st-77007
No Market Record; project 26018730; Exterior
LIVE SPOT pmt_406-columbia-st-77007
Sold; COMPLETE
LIVE SPOT pmt_4327-center-st-77007
No Market Record; COMPLETE
errors []
```

Live JS, market snapshot, and inspection feed are byte-identical. Netlify rewrites HTML navigation URLs (`index.html` → `/`, etc.); all embedded application scripts are identical, so an exact whole-HTML byte comparison is inappropriate. Screenshots were captured and inspected. Live checks use the same fixed clock and empty shared-edit response as deterministic tests; actual shared-edit counts are separately reported above. All non-GET browser requests are blocked during verification.

Final reapplication of both importers returned `changed_files: []`; SHA256 hashes of index.html, heights_market_status.data.json, heights_permits.json, and inspections.json stayed identical (`pulls/market_backfill_20260910/idempotency.log`).
