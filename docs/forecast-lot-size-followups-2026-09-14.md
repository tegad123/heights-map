# Forecast lot-size follow-ups — 2026-09-14

Status: **18 open items: 14 propagation gaps and 4 parcel identity conflicts.**

The client-report export contains supplementary recovered values only. No map lot sizes or product classifications were changed. Map writes are not authorized by this export request. The original forecast CSV remains unchanged.

Report: [single-lot forecast with recovered areas](../pulls/2026-09-14/forecast-single-lot-2026-09-14-recovered.csv). It retains 46 homes and the original forecast dates. Recovery fields are populated for exactly 14 homes.

## Propagation gaps — 14 open

Common follow-up: prepare a lot-only backfill proposal with per-record provenance, reconcile parcel identity and area where necessary, and obtain approval before changing the map. Preserve existing product classifications. A polygon area is not necessarily a deed-recorded lot measurement. These entries remain open until an approved backfill and verification are complete.

Cache sources refer to [.hcad_cache.json](../.hcad_cache.json), field Shape.STArea(), rounded to two decimals. Triage sources refer to [notes/clarification_triage.csv](../notes/clarification_triage.csv), field hcad_area_sf.

| Work ID | Status | Address | Map record ID | Recovered sf | Source / follow-up detail |
|---|---|---|---|---:|---|
| P01 | Open | 2052 Columbia St | pmt_2052-columbia-st-77008 | 7920 | HAR_Export_2024-heights.csv, Address = 2052 Columbia Street, Lot Size = 7920. Cache account 0200630000026 has polygon area 7919.89. Preserve the source distinction. |
| P02 | Open | 408 Columbia St | pmt_408-columbia-st-77007 | 6599.97 | Cache account 1482430010001. Existing Single Lot label is protected; separate lot-area backfill from the documented plat/product question. |
| P03 | Open | 625 Oxford St | pmt_625-oxford-st-77007 | 6600.03 | Cache account 1488260010002. Existing Single Lot label is protected; separate lot-area backfill from the documented plat/product question. |
| P04 | Open | 602 Northwood St | pmt_602-northwood-st-77009 | 5000.00 | Cache account 0331390070005, address 602 NORTHWOOD ST. |
| P05 | Open | 1118 Adele St | pmt_1118-adele-st-77009 | 5000.00 | Cache account 0350110040016, address 1118 ADELE ST. |
| P06 | Open | 1118 Worthshire St | pmt_1118-worthshire-st-77008 | 6733 | Triage row 126, account 0771810090009, RESOLVED-SINGLE. |
| P07 | Open | 1410 Herkimer St | pmt_1410-herkimer-st-77008 | 8799.05 | Cache account 0201450000013; triage row 146 rounds to 8799. Preserve the reviewed product despite the lot-plus-fragments classification question. |
| P08 | Open | 702 Euclid St | pmt_702-euclid-st-77009 | 7565.00 | Cache account 0373020000008. Review observed parcel history when preparing propagation; do not infer a product change. |
| P09 | Open | 822 Nashua St | pmt_822-nashua-st-77008 | 8402 | Triage row 213, account 0771820130025, RESOLVED-SINGLE. |
| P10 | Open | 2005 Harvard St | pmt_2005-harvard-st-77008 | 6953.90 | Cache account 0200670000011; duplicate coordinate-cache entries agree on area. |
| P11 | Open | 1220 Prince St | pmt_1220-prince-st-77008 | 6170.84 | Cache account 0582430030008. Preserve existing product and represented-home count. |
| P12 | Open | 433 W 23rd St | pmt_433-w-23rd-st-77008 | 9777.48 | Cache account 0200420000034. Triage rows 70/180 report 9825: difference 47.52 sf, approximately 48 sf. Client chose cache value for supplementary export. Reconcile the disagreement before proposing a map value; assembled-lot classification is a separate issue. |
| P13 | Open | 629 E 26th St | pmt_629-e-26th-st-77008 | 6195.40 | Cache account 0350850290026; triage row 77 reports 6195. Two assembled legal lots; triage is RESOLVED-SINGLE. Preserve product. |
| P14 | Open | 845 E 26th St | pmt_845-e-26th-st-77009 | 6000.00 | Cache account 0350840270025; triage row 84 reports 6000. Two assembled legal lots; triage is RESOLVED-SINGLE. Preserve product. |

Root cause to address: [product_backfill.py](../product_backfill.py) protects already classified records; [product_classification.py](../product_classification.py) returns product fields rather than a general lot-size update. The forecast export reads matched current market evidence, the home's DATA lot, and embedded parcel evidence; standalone cache/review values are not automatically propagated.

## Parcel identity conflicts — 4 open

These homes have **blank supplementary recovery fields**. Candidate areas below are evidence to investigate, not accepted home lot sizes.

| Work ID | Status | Address | Map record ID | Evidence and required follow-up |
|---|---|---|---|---|
| I01 | Open | 718 E 7th St | pmt_718-e-7th-st-77007 | Coordinate-cache account 0350290550023 has area 8125.00 sf but address 714 E 7TH ST. heights_review_v9.csv row 124 carries that account under 718; refresh/parcel_events.json also associates it with 714. Resolve the address/account relationship before recovering a value. |
| I02 | Open | 1008 E 28th St | pmt_1008-e-28th-st-77009 | Coordinate-cache account 0350820240004 has area 7559.97 sf but address 1006 E 28TH ST. Later docs/product-conflicts-2026-09-10.csv row 83 lacks usable exact-address evidence for 1008. Establish the correct child/parent parcel and lot area. |
| I03 | Open | 627 Mazal (Pvt) Ln | pmt_627-mazal-pvt-ln-77009 | Triage row 198 associates 10206 sf with account 1368390010012, legal ROW- PRIVATE STREET. DATA says the coordinates are estimated and lots 7–9 remain one unaddressed parcel. Identify the residential parcel; do not use the street/ROW area as the home lot. |
| I04 | Open | 214 Sylvester Rd | pmt_214-sylvester-rd-77009 | Triage row 169 gives 8936 sf for account 0660270020019. Later docs/product-conflicts-2026-09-10.csv row 184 cites exact-address account 0400770000094. Reconcile the account identities and obtain the area belonging to the correct parcel; retain the current product pending access/plat review. |

## Separate pre-existing linkage issue

2436 White Oak Dr is outside the 18 items requested here and remains blank in the supplementary export. The permit ID pmt_2436-white-oak-dr-77009 lacks lot size, while the separate same-address active record act_2436-white-oak has 4718 sf. Its historical HELD_TRIAGE classification was overridden by the client. No value was transferred between those records.

## Closure evidence

For each item, record the disposition, confirmed source/account, any authorized map change or reason for retaining a blank, and the validation/commit reference. Do not close an item merely because its supplementary value appeared in the client report.

