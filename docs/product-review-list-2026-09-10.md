# Heights product review — 2026-09-10

Source cohort: 147 Unknown → 138. Nine gaps filled as Split Lot. Three explicitly authorized stored Single Lot fixtures corrected separately; all other stored labels and all 80 triage holds are unchanged.

The live/shared baseline has four held records already labeled Single Lot by remote edits: its 143 Unknown become 134. This list preserves all 138 unresolved source-cohort records, including those four human overrides.

HCAD reachability: metadata HTTP 200; account 0350790000007 returned one polygon and full legal/land/improvement attributes. Four sandbox DNS attempts failed and were logged separately; the outside-sandbox fetch succeeded. Successful responses are persisted individually; failures are never stored as zero features.

Dimensions below are measured geometry proxies, not deed/plat dimensions. Values are the current HCAD service values (valuation year not supplied by this layer); zero improvement value is not proof of no completed house. History is an observed polygon SPLIT/ASSEMBLY between cached HCAD vintages, not a title history or a newly fetched deed record. No lot-area threshold was used.

## Applied observed-split decisions

| Address | Account | Depth ft | Prior group | Evidence |
|---|---|---:|---|---|
| 1239 Waverly St, Houston, TX 77008 | 0201760000046 | 132.054 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": true, "addresses": {"child": ["1237 WAVERLY ST", "1239 WAVERLY ST"], "parent": ["1239 WAVERLY ST"]}, "areas": {"child_sf": [4400.2, 4400.2], "delta_pct": -1.07, "parent_sf": [8895.6], "sum_child_sf": 8800.4, "sum_parent_sf": 8895.6}, "child_accts": ["0201760000004", "0201760000046"], "event": "SPLIT", "lat": 29.793801, "lng": -95.404887, "parent_accts": ["0201760000004"], "vintage": "2025_Oct->2026_Jul"}] |
| 310 E 28th St, Houston, TX 77008 | 0350790000043 | 119.9756 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": true, "addresses": {"child": ["308 E  28TH ST", "310 E  28TH ST"], "parent": ["308 E  28TH ST"]}, "areas": {"child_sf": [2999.7, 2999.1], "delta_pct": -4.76, "parent_sf": [6298.8], "sum_child_sf": 5998.8, "sum_parent_sf": 6298.8}, "child_accts": ["0350790000007", "0350790000043"], "event": "SPLIT", "lat": 29.812, "lng": -95.395427, "parent_accts": ["0350790000007"], "vintage": "2025_Oct->2026_Jul"}] |
| 323 W 23rd St, Houston, TX 77008 | 0200410000068 | 131.1374 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": false, "addresses": {"child": ["323 W  23RD ST", "325 W  23RD ST"], "parent": ["323 W  23RD ST"]}, "areas": {"child_sf": [3274.9, 3274.9], "delta_pct": -0.0, "parent_sf": [6549.9], "sum_child_sf": 6549.9, "sum_parent_sf": 6549.9}, "child_accts": ["0200410000068", "0200410000067"], "event": "SPLIT", "lat": 29.807236, "lng": -95.402493, "parent_accts": ["0200410000039"], "vintage": "2025_Oct->2026_Jul"}] |
| 243 W 26th St, Houston, TX 77008 | 0200240000073 | 131.0001 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": false, "addresses": {"child": ["243 W  26TH ST", "241 W  26 TH ST"], "parent": ["241 W  26TH ST"]}, "areas": {"child_sf": [3275.0, 3275.0], "delta_pct": 0.0, "parent_sf": [6549.9], "sum_child_sf": 6550.0, "sum_parent_sf": 6549.9}, "child_accts": ["0200240000073", "0200240000072"], "event": "SPLIT", "lat": 29.810312, "lng": -95.401231, "parent_accts": ["0200240000028"], "vintage": "2025_Oct->2026_Jul"}] |
| 1237 Waverly St, Houston, TX 77008 | 0201760000004 | 132.0537 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": true, "addresses": {"child": ["1237 WAVERLY ST", "1239 WAVERLY ST"], "parent": ["1239 WAVERLY ST"]}, "areas": {"child_sf": [4400.2, 4400.2], "delta_pct": -1.07, "parent_sf": [8895.6], "sum_child_sf": 8800.4, "sum_parent_sf": 8895.6}, "child_accts": ["0201760000004", "0201760000046"], "event": "SPLIT", "lat": 29.793801, "lng": -95.404887, "parent_accts": ["0201760000004"], "vintage": "2025_Oct->2026_Jul"}] |
| 222 E 27th St, Houston, TX 77008 | 0350870330013 | 119.9998 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": true, "addresses": {"child": ["222 E  27TH ST", "224 E  27TH ST", "226 E  27TH ST"], "parent": ["226 E  27TH ST"]}, "areas": {"child_sf": [3000.0, 3000.0, 3000.0], "delta_pct": -0.0, "parent_sf": [9000.0], "sum_child_sf": 9000.0, "sum_parent_sf": 9000.0}, "child_accts": ["0350870330013", "0350870330040", "0350870330041"], "event": "SPLIT", "lat": 29.811149, "lng": -95.396391, "parent_accts": ["0350870330013"], "vintage": "2024_Oct->2025_Oct"}] |
| 325 W 23rd St, Houston, TX 77008 | 0200410000067 | 131.1378 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": false, "addresses": {"child": ["323 W  23RD ST", "325 W  23RD ST"], "parent": ["323 W  23RD ST"]}, "areas": {"child_sf": [3274.9, 3274.9], "delta_pct": -0.0, "parent_sf": [6549.9], "sum_child_sf": 6549.9, "sum_parent_sf": 6549.9}, "child_accts": ["0200410000068", "0200410000067"], "event": "SPLIT", "lat": 29.807236, "lng": -95.402493, "parent_accts": ["0200410000039"], "vintage": "2025_Oct->2026_Jul"}] |
| 829 E 25th St, Houston, TX 77009 | 0350940470055 | 120.0339 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": true, "addresses": {"child": ["827 E  25TH ST", "829 E  25TH ST"], "parent": ["827 E  25TH ST"]}, "areas": {"child_sf": [3000.0, 3000.0], "delta_pct": -0.0, "parent_sf": [6000.0], "sum_child_sf": 6000.0, "sum_parent_sf": 6000.0}, "child_accts": ["0350940470091", "0350940470055"], "event": "SPLIT", "lat": 29.809237, "lng": -95.388555, "parent_accts": ["0350940470055"], "vintage": "2025_Oct->2026_Jul"}] |
| 827 E 25th St, Houston, TX 77009 | 0350940470091 | 120.0339 | PARCEL_HISTORY_CONFLICT | [{"acct_continuity": true, "addresses": {"child": ["827 E  25TH ST", "829 E  25TH ST"], "parent": ["827 E  25TH ST"]}, "areas": {"child_sf": [3000.0, 3000.0], "delta_pct": -0.0, "parent_sf": [6000.0], "sum_child_sf": 6000.0, "sum_parent_sf": 6000.0}, "child_accts": ["0350940470091", "0350940470055"], "event": "SPLIT", "lat": 29.809237, "lng": -95.388555, "parent_accts": ["0350940470055"], "vintage": "2025_Oct->2026_Jul"}] |
| 308 E 28th St, Houston, TX 77008 | 0350790000007 | 120.0002 | AUTHORIZED_FIXTURE | [{"acct_continuity": true, "addresses": {"child": ["308 E  28TH ST", "310 E  28TH ST"], "parent": ["308 E  28TH ST"]}, "areas": {"child_sf": [2999.7, 2999.1], "delta_pct": -4.76, "parent_sf": [6298.8], "sum_child_sf": 5998.8, "sum_parent_sf": 6298.8}, "child_accts": ["0350790000007", "0350790000043"], "event": "SPLIT", "lat": 29.812, "lng": -95.395427, "parent_accts": ["0350790000007"], "vintage": "2025_Oct->2026_Jul"}] |
| 1125 E 24th St, Houston, TX 77009 | 0351020630023 | 120.1889 | AUTHORIZED_FIXTURE | [{"acct_continuity": true, "addresses": {"child": ["1121 E  24TH ST", "1125 E  24TH ST"], "parent": ["1121 E  24TH ST"]}, "areas": {"child_sf": [2999.9, 2999.9], "delta_pct": -2.15, "parent_sf": [6131.4], "sum_child_sf": 5999.8, "sum_parent_sf": 6131.4}, "child_accts": ["0351020630027", "0351020630023"], "event": "SPLIT", "lat": 29.808616, "lng": -95.383568, "parent_accts": ["0351020630023"], "vintage": "2025_Oct->2026_Jul"}] |
| 1121 E 24th St, Houston, TX 77009 | 0351020630027 | 120.1889 | AUTHORIZED_FIXTURE | [{"acct_continuity": true, "addresses": {"child": ["1121 E  24TH ST", "1125 E  24TH ST"], "parent": ["1121 E  24TH ST"]}, "areas": {"child_sf": [2999.9, 2999.9], "delta_pct": -2.15, "parent_sf": [6131.4], "sum_child_sf": 5999.8, "sum_parent_sf": 6131.4}, "child_accts": ["0351020630027", "0351020630023"], "event": "SPLIT", "lat": 29.808616, "lng": -95.383568, "parent_accts": ["0351020630023"], "vintage": "2025_Oct->2026_Jul"}] |

## Residual groups

{'DEPTH_BOUNDARY_UNCERTAIN': 12, 'ASSEMBLED_REVIEW': 14, 'UNVERIFIED_PLAT': 31, 'LEGAL_UNAVAILABLE': 1, 'HELD_TRIAGE': 80}

Held evidence availability versus the prior classification audit: `{"current_geometry": 70, "current_history": 0, "current_legal": 70, "held_with_unverified_context": 8, "new_geometry": 0, "new_history": 0, "new_legal": 0, "prior_geometry": 70, "prior_history": 0, "prior_legal": 70, "unverified_context_with_history": 1}`. The earlier human triage CSV did not record polygon payloads, so these comparisons do not assert what its reviewers personally saw. Held composition: 46 held Single candidates, four held Split candidates, 30 ambiguous. All 80 remain untouched.

Twelve boundary cases retain their ±0.01 ft abstention. Ten have observed split history; this confirms subdivision but does not independently establish common access or resolve the depth measurement. None has a three-or-more unit/master signal. 742 Allston has no exact match in the successful full-house-number query. Assembled and unverified-plat groups receive recommendations only.

## Per-record review (closest to decidable first)

### 1. 1040 Voight St, Houston, TX 77009

- ID: `pmt_1040-voight-st-77009`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1483980010002`; match: EXACT.
- Legal: LT 2 BLK 1|VOIGHT STREET VIEWS. Measured depth × width: 99.9999 × 25.0 ft; area: 2499.98 sf.
- Unit letters: none; verified unit count: 1; master size: 2 (project 24120301).
- Land value: 250000; improvement value: 675583. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1040 VOIGHT ST", "1042 VOIGHT ST"], "parent": ["1040 VOIGHT ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.23, "parent_sf": [4988.3], "sum_child_sf": 5000.0, "sum_parent_sf": 4988.3}, "child_accts": ["1483980010002", "1483980010001"], "event": "SPLIT", "lat": 29.780284, "lng": -95.386061, "parent_accts": ["0512040010015"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 2. 1042 Voight St, Houston, TX 77009

- ID: `pmt_1042-voight-st-77009`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1483980010001`; match: EXACT.
- Legal: LT 1 BLK 1|VOIGHT STREET VIEWS. Measured depth × width: 99.9999 × 25.0 ft; area: 2499.98 sf.
- Unit letters: none; verified unit count: 1; master size: 2 (project 24120301).
- Land value: 250000; improvement value: 705055. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1040 VOIGHT ST", "1042 VOIGHT ST"], "parent": ["1040 VOIGHT ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.23, "parent_sf": [4988.3], "sum_child_sf": 5000.0, "sum_parent_sf": 4988.3}, "child_accts": ["1483980010002", "1483980010001"], "event": "SPLIT", "lat": 29.780284, "lng": -95.386061, "parent_accts": ["0512040010015"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 3. 1132 Adele St, Houston, TX 77009

- ID: `pmt_1132-adele-st-77009`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1446520010002`; match: EXACT.
- Legal: LT 2 BLK 1|ADELE LANDING. Measured depth × width: 100.0001 × 24.9998 ft; area: 2499.98 sf.
- Unit letters: none; verified unit count: 1; master size: 2 (project 25039338).
- Land value: 175000; improvement value: 487741. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 4. 1308 Edwards St A, Houston, TX 77007

- ID: `pmt_1308-edwards-st-a-77007`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1490260010002`; match: EXACT.
- Legal: LT 2 BLK 1|EDWARDS HEIGHTS. Measured depth × width: 100.0002 × 25.5 ft; area: 2550.0 sf.
- Unit letters: A; verified unit count: 2; master size: unavailable (project none).
- Land value: 166000; improvement value: 263283. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1308 EDWARDS ST", "1308 EDWARDS ST"], "parent": ["1308 EDWARDS ST"]}, "areas": {"child_sf": [2450.0, 2550.0], "delta_pct": 0.0, "parent_sf": [4999.9], "sum_child_sf": 5000.0, "sum_parent_sf": 4999.9}, "child_accts": ["1490260010001", "1490260010002"], "event": "SPLIT", "lat": 29.771016, "lng": -95.370395, "parent_accts": ["0050880000002"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 5. 1308 Edwards St B, Houston, TX 77007

- ID: `pmt_1308-edwards-st-b-77007`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1490260010001`; match: EXACT.
- Legal: LT 1 BLK 1|EDWARDS HEIGHTS. Measured depth × width: 100.0001 × 24.5 ft; area: 2450.0 sf.
- Unit letters: B; verified unit count: 2; master size: 2 (project 25048881).
- Land value: 162000; improvement value: 294871. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1308 EDWARDS ST", "1308 EDWARDS ST"], "parent": ["1308 EDWARDS ST"]}, "areas": {"child_sf": [2450.0, 2550.0], "delta_pct": 0.0, "parent_sf": [4999.9], "sum_child_sf": 5000.0, "sum_parent_sf": 4999.9}, "child_accts": ["1490260010001", "1490260010002"], "event": "SPLIT", "lat": 29.771016, "lng": -95.370395, "parent_accts": ["0050880000002"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 6. 1438 Dian St A, Houston, TX 77008

- ID: `pmt_1438-dian-st-a-77008`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `0391150000436`; match: EXACT.
- Legal: LT 437|HOUSTON HEIGHTS ANNEX. Measured depth × width: 100.0001 × 25.0 ft; area: 2500.0 sf.
- Unit letters: A; verified unit count: 2; master size: unavailable (project none).
- Land value: 225000; improvement value: 365000. Observed parcel history: `[{"acct_continuity": true, "addresses": {"child": ["1438 DIAN ST", "1438 DIAN ST"], "parent": ["1438 DIAN ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.0, "parent_sf": [5000.0], "sum_child_sf": 5000.0, "sum_parent_sf": 5000.0}, "child_accts": ["0391150000436", "0391150000502"], "event": "SPLIT", "lat": 29.797446, "lng": -95.413772, "parent_accts": ["0391150000436"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 7. 1438 Dian St B, Houston, TX 77008

- ID: `pmt_1438-dian-st-b-77008`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `0391150000502`; match: EXACT.
- Legal: LT 436|HOUSTON HEIGHTS ANNEX. Measured depth × width: 100.0002 × 25.0003 ft; area: 2500.0 sf.
- Unit letters: B; verified unit count: 2; master size: unavailable (project none).
- Land value: 225000; improvement value: 452653. Observed parcel history: `[{"acct_continuity": true, "addresses": {"child": ["1438 DIAN ST", "1438 DIAN ST"], "parent": ["1438 DIAN ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.0, "parent_sf": [5000.0], "sum_child_sf": 5000.0, "sum_parent_sf": 5000.0}, "child_accts": ["0391150000436", "0391150000502"], "event": "SPLIT", "lat": 29.797446, "lng": -95.413772, "parent_accts": ["0391150000436"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 8. 4605 Nolda St, Houston, TX 77007

- ID: `pmt_4605-nolda-st-77007`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1478650010001`; match: EXACT.
- Legal: LT 1 BLK 1|NOLDA ENCLAVE. Measured depth × width: 99.9998 × 25.0001 ft; area: 2500.0 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 212500; improvement value: 0. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["4605 NOLDA ST", "4603 NOLDA ST"], "parent": ["4605 NOLDA ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.14, "parent_sf": [4993.2], "sum_child_sf": 5000.0, "sum_parent_sf": 4993.2}, "child_accts": ["1478650010001", "1478650010002"], "event": "SPLIT", "lat": 29.776112, "lng": -95.407845, "parent_accts": ["0072840000010"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 9. 5016 Schuler St, Houston, TX 77007

- ID: `pmt_5016-schuler-st-77007`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1495650010002`; match: EXACT.
- Legal: LT 2 BLK 1|SCHULER POINT. Measured depth × width: 100.0007 × 25.0007 ft; area: 2500.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 175000; improvement value: 0. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["5018 SCHULER ST", "5016 SCHULER ST"], "parent": ["5018 SCHULER ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.0, "parent_sf": [5000.0], "sum_child_sf": 5000.0, "sum_parent_sf": 5000.0}, "child_accts": ["1495650010001", "1495650010002"], "event": "SPLIT", "lat": 29.772876, "lng": -95.412219, "parent_accts": ["0072600000007"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 10. 5018 Schuler St, Houston, TX 77007

- ID: `pmt_5018-schuler-st-77007`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1495650010001`; match: EXACT.
- Legal: LT 1 BLK 1|SCHULER POINT. Measured depth × width: 100.0008 × 25.0008 ft; area: 2500.04 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 175000; improvement value: 0. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["5018 SCHULER ST", "5016 SCHULER ST"], "parent": ["5018 SCHULER ST"]}, "areas": {"child_sf": [2500.0, 2500.0], "delta_pct": 0.0, "parent_sf": [5000.0], "sum_child_sf": 5000.0, "sum_parent_sf": 5000.0}, "child_accts": ["1495650010001", "1495650010002"], "event": "SPLIT", "lat": 29.772876, "lng": -95.412219, "parent_accts": ["0072600000007"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 11. 513 W 8th St, Houston, TX 77007

- ID: `pmt_513-w-8th-st-77007`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `0202380000038`; match: EXACT.
- Legal: TRS 19B 20B & 21B BLK 242|HOUSTON HEIGHTS. Measured depth × width: 100.0002 × 44.0 ft; area: 4400.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 484000; improvement value: 968100. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 12. 602 Jewett St A, Houston, TX 77009

- ID: `pmt_602-jewett-st-a-77009`; group: **DEPTH_BOUNDARY_UNCERTAIN**; HCAD: `1482900010002`; match: EXACT.
- Legal: LT 2 BLK 1|PLAZA ESTATES AT JEWETT. Measured depth × width: 99.9999 × 50.0001 ft; area: 2959.61 sf.
- Unit letters: A; verified unit count: 2; master size: 2 (project 25007490).
- Land value: 146020; improvement value: 460204. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["0 JEWETT ST", "0 VINCENT ST"], "parent": ["602 JEWETT ST"]}, "areas": {"child_sf": [2040.0, 2960.0], "delta_pct": 0.0, "parent_sf": [5000.0], "sum_child_sf": 5000.0, "sum_parent_sf": 5000.0}, "child_accts": ["1482900010001", "1482900010002"], "event": "SPLIT", "lat": 29.799285, "lng": -95.373175, "parent_accts": ["0331150630008"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.

### 13. 1001 E 27th St, Houston, TX 77009

- ID: `pmt_1001-e-27th-st-77009`; group: **ASSEMBLED_REVIEW**; HCAD: `0350820240027`; match: EXACT.
- Legal: LTS 27 & 28 BLK 24|SUNSET HEIGHTS. Measured depth × width: 121.3116 × 50.202 ft; area: 6057.36 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 622788. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 14. 1005 E 27th St, Houston, Tx 77009

- ID: `2131208519`; group: **ASSEMBLED_REVIEW**; HCAD: `0350820240025`; match: EXACT.
- Legal: LTS 25 & 26 BLK 24|SUNSET HEIGHTS. Measured depth × width: 121.3685 × 50.1906 ft; area: 6059.0 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 38557. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 15. 1016 E 27th St, Houston, TX 77009

- ID: `pmt_1016-e-27th-st-77009`; group: **ASSEMBLED_REVIEW**; HCAD: `0350830260020`; match: EXACT.
- Legal: LTS 20 & 21 BLK 26|SUNSET HEIGHTS. Measured depth × width: 120.0 × 50.0001 ft; area: 5999.87 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 348620. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 16. 1017 Rutland St, Houston, Tx 77008

- ID: `2131285466`; group: **ASSEMBLED_REVIEW**; HCAD: `0202090000013`; match: EXACT.
- Legal: LTS 13 & 14 BLK 213|HOUSTON HEIGHTS. Measured depth × width: 132.0533 × 66.6221 ft; area: 8791.55 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 958320; improvement value: 89877. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 17. 1439 Laird St, Houston, Tx 77008

- ID: `2131085991`; group: **ASSEMBLED_REVIEW**; HCAD: `0391180000610`; match: EXACT.
- Legal: LTS 610 611 612 & 613|HOUSTON HEIGHTS ANNEX. Measured depth × width: 100.001 × 100.0005 ft; area: 10000.05 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 950000; improvement value: 100. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 18. 302 W 23rd St, Houston, TX 77008

- ID: `pmt_302-w-23rd-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0200520000001`; match: EXACT.
- Legal: LTS 1 & 2 BLK 56|HOUSTON HEIGHTS. Measured depth × width: 131.0 × 50.0004 ft; area: 6550.03 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 659585; improvement value: 611675. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 19. 305 W 17th St, Houston, TX 77008

- ID: `pmt_305-w-17th-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0201160000047`; match: EXACT.
- Legal: LTS 47 & 48 BLK 120|HOUSTON HEIGHTS. Measured depth × width: 132.0012 × 50.0 ft; area: 6600.02 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 627000; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 20. 310 E 27th St, Houston, TX 77008

- ID: `pmt_310-e-27th-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0350860320008`; match: EXACT.
- Legal: LTS 8 & 9 BLK 32|SUNSET HEIGHTS. Measured depth × width: 120.0001 × 50.0005 ft; area: 6000.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 510000; improvement value: 834100. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 21. 319 E 24th St, Houston, TX 77008

- ID: `pmt_319-e-24th-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0350980550023`; match: EXACT.
- Legal: LTS 23 & 24 BLK 55|SUNSET HEIGHTS. Measured depth × width: 120.0005 × 50.0005 ft; area: 6000.06 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 510000; improvement value: 997184. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 22. 321 E 24th St, Houston, TX 77008

- ID: `pmt_321-e-24th-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0350980550021`; match: EXACT.
- Legal: LTS 21 & 22 BLK 55|SUNSET HEIGHTS. Measured depth × width: 120.0001 × 50.0006 ft; area: 6000.02 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 510000; improvement value: 109495. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 23. 501 E 26th St, Houston, TX 77008

- ID: `pmt_501-e-26th-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0350850300023`; match: EXACT.
- Legal: LTS 23 & 24 BLK 30|SUNSET HEIGHTS. Measured depth × width: 120.3136 × 50.0004 ft; area: 5999.9 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 510000; improvement value: 71841. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 24. 608 E 26th St, Houston, TX 77008

- ID: `pmt_608-e-26th-st-77008`; group: **ASSEMBLED_REVIEW**; HCAD: `0350900400004`; match: EXACT.
- Legal: LTS 4 & 5 BLK 40|SUNSET HEIGHTS. Measured depth × width: 120.2149 × 49.9998 ft; area: 5999.94 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 510000; improvement value: 1067041. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 25. 706 E 7th St, Houston, TX 77007

- ID: `pmt_706-e-7th-st-77007`; group: **ASSEMBLED_REVIEW**; HCAD: `0350290550001`; match: EXACT.
- Legal: LT 2 & W 10 FT OF LT 4 BLK 55|STUDES SEC 2 5TH AMEND. Measured depth × width: 124.9997 × 50.0002 ft; area: 6250.0 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 562500; improvement value: 1072165. Observed parcel history: `[{"acct_continuity": true, "addresses": {"child": ["706 E  7TH ST", "710 E  7TH ST", "714 E  7TH ST"], "parent": ["710 E  7TH ST"]}, "areas": {"child_sf": [6250.0, 6250.0, 8125.0], "delta_pct": 10.0, "parent_sf": [18749.9], "sum_child_sf": 20624.9, "sum_parent_sf": 18749.9}, "child_accts": ["0350290550001", "0350290550024", "0350290550023"], "event": "PARTIAL", "lat": 29.783166, "lng": -95.389326, "parent_accts": ["0350290550001"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 26. 818 Lawrence St, Houston, TX 77007

- ID: `pmt_818-lawrence-st-77007`; group: **ASSEMBLED_REVIEW**; HCAD: `0621980010011`; match: EXACT.
- Legal: LTS 11 & 12 BLK 1|HARDING HEIGHTS. Measured depth × width: 100.0041 × 42.9999 ft; area: 4300.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 430000; improvement value: 864948. Observed parcel history: `[{"acct_continuity": true, "addresses": {"child": ["818 LAWRENCE ST"], "parent": ["818 LAWRENCE ST"]}, "areas": {"child_sf": [4300.0], "delta_pct": -14.0, "parent_sf": [4999.9], "sum_child_sf": 4300.0, "sum_parent_sf": 4999.9}, "child_accts": ["0621980010011"], "event": "RESHAPE", "lat": 29.786024, "lng": -95.406662, "parent_accts": ["0621980010011"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Review Single Lot possibility; assembled legal lots alone cannot confirm one home. Blocking reason: Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.

### 27. 1006 Nashua St, Houston, TX 77008

- ID: `pmt_1006-nashua-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0771820130008`; match: EXACT.
- Legal: LT 8 BLK 13|TIMBERGROVE MANOR SEC 3. Measured depth × width: 137.4781 × 62.8696 ft; area: 8588.59 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 402084; improvement value: 402583. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 28. 1011 Worthshire St, Houston, TX 77008

- ID: `pmt_1011-worthshire-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0771820200019`; match: EXACT.
- Legal: LT 19 BLK 18|TIMBERGROVE MANOR SEC 4. Measured depth × width: 120.0635 × 64.9685 ft; area: 7367.85 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: None; improvement value: None. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 29. 1021 Ashland St, Houston, TX 77008

- ID: `pmt_1021-ashland-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `1417040010003`; match: EXACT.
- Legal: LT 3 BLK 1|UNIKA VILLAGE IN THE HEIGHTS. Measured depth × width: 131.9999 × 39.9998 ft; area: 5279.96 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 580800; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 30. 1023 Grovewood Ln, Houston, TX 77008

- ID: `pmt_1023-grovewood-ln-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0771810030023`; match: EXACT.
- Legal: LT 23 BLK 3|TIMBERGROVE MANOR. Measured depth × width: 117.6722 × 58.4283 ft; area: 6821.14 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 432000; improvement value: 1046562. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 31. 1110 Jerome St, Houston, TX 77009

- ID: `pmt_1110-jerome-st-77009`; group: **UNVERIFIED_PLAT**; HCAD: `0620810030020`; match: EXACT.
- Legal: LT 2 BLK 103|NORTH NORHILL. Measured depth × width: 100.0022 × 50.1708 ft; area: 5008.56 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 293916. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 32. 1115 Nashua St, Houston, TX 77008

- ID: `pmt_1115-nashua-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0771820110017`; match: EXACT.
- Legal: LT 17 BLK 11|TIMBERGROVE MANOR SEC 2 AMEND. Measured depth × width: 124.0003 × 120.0 ft; area: 14880.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 878400; improvement value: 1044068. Observed parcel history: `[{"acct_continuity": true, "addresses": {"child": ["1115 NASHUA ST"], "parent": ["1115 NASHUA ST"]}, "areas": {"child_sf": [14880.0], "delta_pct": 100.86, "parent_sf": [7408.3], "sum_child_sf": 14880.0, "sum_parent_sf": 7408.3}, "child_accts": ["0771820110017"], "event": "RESHAPE", "lat": 29.791084, "lng": -95.412755, "parent_accts": ["0771820110017"], "vintage": "2025_Oct->2026_Jul"}, {"acct_continuity": true, "addresses": {"child": ["1115 NASHUA ST"], "parent": ["1111 NASHUA ST", "1115 NASHUA ST"]}, "areas": {"child_sf": [14880.0], "delta_pct": -0.41, "parent_sf": [7410.0, 7408.3], "sum_child_sf": 14880.0, "sum_parent_sf": 14818.3}, "child_accts": ["0771820110017"], "event": "ASSEMBLY", "lat": 29.790913, "lng": -95.412751, "parent_accts": ["0771820110018", "0771820110017"], "vintage": "2025_Oct->2026_Jul"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 33. 1134 Adele St, Houston, TX 77009

- ID: `pmt_1134-adele-st-77009`; group: **UNVERIFIED_PLAT**; HCAD: `1446520010001`; match: EXACT.
- Legal: LT 1 BLK 1|ADELE LANDING. Measured depth × width: 100.0001 × 25.0001 ft; area: 2500.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 175000; improvement value: 487741. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 34. 1211 Bay Oaks Rd, Houston, TX 77008

- ID: `pmt_1211-bay-oaks-rd-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0771810060014`; match: EXACT.
- Legal: LT 14 BLK 6|TIMBERGROVE MANOR. Measured depth × width: 175.4352 × 64.2205 ft; area: 9808.0 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 523800; improvement value: 950001. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 35. 1214 Farwood St, Houston, Tx 77009

- ID: `2131377369`; group: **UNVERIFIED_PLAT**; HCAD: `0571440000007`; match: EXACT.
- Legal: LT 7 BLK 2|FARWOOD. Measured depth × width: 102.2823 × 49.5373 ft; area: 4993.57 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 185250; improvement value: 100551. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 36. 1312 E 28th St A, Houston, TX 77009

- ID: `pmt_1312-e-28th-st-a-77009`; group: **UNVERIFIED_PLAT**; HCAD: `0580150000005`; match: EXACT.
- Legal: LT 5 BLK 3|EAST SUNSET HEIGHTS. Measured depth × width: 100.0293 × 50.0009 ft; area: 5000.08 sf.
- Unit letters: A; verified unit count: 1; master size: unavailable (project none).
- Land value: 250000; improvement value: 490357. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 37. 1315 Oleander St, Houston, Tx 77009

- ID: `2131377372`; group: **UNVERIFIED_PLAT**; HCAD: `0571440000012`; match: EXACT.
- Legal: LT 12 BLK 2|FARWOOD. Measured depth × width: 99.3605 × 52.9295 ft; area: 5066.29 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 185250; improvement value: 89028. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 38. 1317 Oleander St, Houston, Tx 77009

- ID: `2131377371`; group: **UNVERIFIED_PLAT**; HCAD: `0571440000011`; match: EXACT.
- Legal: LT 11 BLK 2|FARWOOD. Measured depth × width: 101.4819 × 50.9187 ft; area: 5039.56 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 185250; improvement value: 67796. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 39. 1519 Glen Oaks St, Houston, TX 77008

- ID: `pmt_1519-glen-oaks-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0771820170009`; match: EXACT.
- Legal: LT 9 BLK 17|TIMBERGROVE MANOR SEC 3. Measured depth × width: 246.6927 × 84.8158 ft; area: 16066.41 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 584757; improvement value: 834034. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 40. 1520 Winter St, Houston, TX 77007

- ID: `pmt_1520-winter-st-77007`; group: **UNVERIFIED_PLAT**; HCAD: `1477970010006`; match: EXACT.
- Legal: LT 6 BLK 1|WINTER FALLS. Measured depth × width: 65.7691 × 25.2572 ft; area: 1619.04 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 128760; improvement value: 229584. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1520 WINTER ST", "1522 WINTER ST", "0 JOHNSON ST", "0 JOHNSON ST", "0 JOHNSON ST"], "parent": ["1520 WINTER ST"]}, "areas": {"child_sf": [1619.0, 1787.4, 319.1, 225.4, 197.3], "delta_pct": -19.92, "parent_sf": [5180.0], "sum_child_sf": 4148.3, "sum_parent_sf": 5180.0}, "child_accts": ["1477970010006", "1477970010007", "1477970010008", "1477970010010", "1477970010009"], "event": "PARTIAL", "lat": 29.772471, "lng": -95.373406, "parent_accts": ["0051050000001"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 41. 1522 Winter St, Houston, TX 77007

- ID: `pmt_1522-winter-st-77007`; group: **UNVERIFIED_PLAT**; HCAD: `1477970010007`; match: EXACT.
- Legal: LT 7 BLK 1|WINTER FALLS. Measured depth × width: 69.14 × 25.9999 ft; area: 1787.44 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 135480; improvement value: 229584. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1520 WINTER ST", "1522 WINTER ST", "0 JOHNSON ST", "0 JOHNSON ST", "0 JOHNSON ST"], "parent": ["1520 WINTER ST"]}, "areas": {"child_sf": [1619.0, 1787.4, 319.1, 225.4, 197.3], "delta_pct": -19.92, "parent_sf": [5180.0], "sum_child_sf": 4148.3, "sum_parent_sf": 5180.0}, "child_accts": ["1477970010006", "1477970010007", "1477970010008", "1477970010010", "1477970010009"], "event": "PARTIAL", "lat": 29.772471, "lng": -95.373406, "parent_accts": ["0051050000001"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 42. 1604 Spring St, Houston, Tx 77007

- ID: `2131271381`; group: **UNVERIFIED_PLAT**; HCAD: `0142570000007`; match: EXACT.
- Legal: TRS 2A 3B & 4A BLK 3|FRITZ. Measured depth × width: 149.9988 × 44.8838 ft; area: 5279.99 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 271440; improvement value: 101030. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 43. 1805 Palmetto Landing Dr, Houston, TX 77009

- ID: `pmt_1805-palmetto-landing-dr-77009`; group: **UNVERIFIED_PLAT**; HCAD: `1385300010008`; match: EXACT.
- Legal: LT 8 BLK 1|NEWER HEIGHTS VILLAGE. Measured depth × width: 67.0095 × 29.0077 ft; area: 1943.34 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 136010; improvement value: 212151. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 44. 1807 Palmetto Landing Dr, Houston, TX 77009

- ID: `pmt_1807-palmetto-landing-dr-77009`; group: **UNVERIFIED_PLAT**; HCAD: `1385300010009`; match: EXACT.
- Legal: LT 9 BLK 1|NEWER HEIGHTS VILLAGE. Measured depth × width: 67.0032 × 29.0001 ft; area: 1943.06 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 136010; improvement value: 176500. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 45. 1809 Palmetto Landing Dr, Houston, TX 77009

- ID: `pmt_1809-palmetto-landing-dr-77009`; group: **UNVERIFIED_PLAT**; HCAD: `1385300010010`; match: EXACT.
- Legal: LT 10 BLK 1|NEWER HEIGHTS VILLAGE. Measured depth × width: 67.0035 × 29.0002 ft; area: 1943.05 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 136010; improvement value: 176500. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 46. 1811 W 14th 1/2 St, Houston, Tx 77008

- ID: `2131475807`; group: **UNVERIFIED_PLAT**; HCAD: `0720130080014`; match: EXACT.
- Legal: TR 1C BLK 8|CLARK PINES SEC 2. Measured depth × width: 107.2999 × 59.8527 ft; area: 5971.21 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 384150; improvement value: 56668. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 47. 1813 W 14th St, Houston, TX 77008

- ID: `pmt_1813-w-14th-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0720120020011`; match: EXACT.
- Legal: TR 11B BLK 2|CLARK PINES. Measured depth × width: 132.7281 × 60.0005 ft; area: 7949.88 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 491400; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 48. 1910 W 14th 1/2 St, Houston, TX 77008

- ID: `pmt_1910-w-14th-1-2-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0720130090001`; match: EXACT.
- Legal: LT 1 BLK 9|CLARK PINES SEC 2. Measured depth × width: 110.0003 × 90.0003 ft; area: 9890.59 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 555750; improvement value: 899826. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 49. 1918 Johnson St, Houston, TX 77007

- ID: `pmt_1918-johnson-st-77007`; group: **UNVERIFIED_PLAT**; HCAD: `1478670010002`; match: EXACT.
- Legal: LT 2 BLK 1|CUSTUS ESTATES. Measured depth × width: 88.1904 × 50.0005 ft; area: 4409.53 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 286650; improvement value: 180843. Observed parcel history: `[{"acct_continuity": false, "addresses": {"child": ["1918 JOHNSON ST"], "parent": ["0 JOHNSON ST"]}, "areas": {"child_sf": [4409.5], "delta_pct": 121.03, "parent_sf": [1995.0], "sum_child_sf": 4409.5, "sum_parent_sf": 1995.0}, "child_accts": ["1478670010002"], "event": "RESHAPE", "lat": 29.774901, "lng": -95.373443, "parent_accts": ["1368150010005"], "vintage": "2024_Oct->2025_Oct"}]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Common Driveway; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 50. 2008 W 14th 1/2 St, Houston, TX 77008

- ID: `pmt_2008-w-14th-1-2-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0720130110005`; match: EXACT.
- Legal: LT 5 BLK 11|CLARK PINES SEC 2. Measured depth × width: 111.5717 × 70.5235 ft; area: 7814.86 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 484250; improvement value: 975750. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 51. 2311 Roy Cir, Houston, TX 77007

- ID: `pmt_2311-roy-cir-77007`; group: **UNVERIFIED_PLAT**; HCAD: `0800710000011`; match: EXACT.
- Legal: LT 11 BLK 1|COTTAGE OAKS. Measured depth × width: 120.8933 × 56.6612 ft; area: 6819.89 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: None; improvement value: None. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 52. 2701 Julian St, Houston, TX 77009

- ID: `pmt_2701-julian-st-77009`; group: **UNVERIFIED_PLAT**; HCAD: `0562880000025`; match: EXACT.
- Legal: LT 25 BLK 2|RIDGEMONT SEC 1. Measured depth × width: 102.5262 × 92.8685 ft; area: 7062.3 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 812500; improvement value: 597286. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 53. 5114 Eigel St, Houston, TX 77007

- ID: `pmt_5114-eigel-st-77007`; group: **UNVERIFIED_PLAT**; HCAD: `0072760000004`; match: EXACT.
- Legal: LT 4 BLK 92|BRUNNER. Measured depth × width: 100.0001 × 50.0001 ft; area: 4999.98 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 399900; improvement value: 100. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 54. 5212 Kansas St, Houston, TX 77007

- ID: `pmt_5212-kansas-st-77007`; group: **UNVERIFIED_PLAT**; HCAD: `0102020000087`; match: EXACT.
- Legal: LTS 1087 1088 & 1089|COTTAGE GROVE SEC 1. Measured depth × width: 107.6593 × 74.8182 ft; area: 8036.58 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 481500; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 55. 717 E 5th 1/2 St, Houston, TX 77007

- ID: `pmt_717-e-5th-1-2-st-77007`; group: **UNVERIFIED_PLAT**; HCAD: `1464340010002`; match: EXACT.
- Legal: LT 2 BLK 1|SOLAR STREET PLAZA. Measured depth × width: 125.056 × 78.2435 ft; area: 7144.02 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 646200; improvement value: 1253800. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 56. 730 E 13th 1/2 St, Houston, TX 77008

- ID: `pmt_730-e-13th-1-2-st-77008`; group: **UNVERIFIED_PLAT**; HCAD: `0522740000008`; match: EXACT.
- Legal: LT 8 BLK 6|KUTSCHBACH. Measured depth × width: 125.0899 × 49.9998 ft; area: 6254.47 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 593750; improvement value: 1204250. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 57. 912 Robbie St, Houston, Tx 77009

- ID: `2131370516`; group: **UNVERIFIED_PLAT**; HCAD: `0513500000012`; match: EXACT.
- Legal: LT 12 & TR 13A BLK 6|PINERIDGE. Measured depth × width: 100.0009 × 60.0001 ft; area: 6000.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 41196. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Unverified v9 candidate: Split Lot; retain Unknown pending plat/access review. Blocking reason: Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.

### 58. 742 Allston St, Houston, TX 77007

- ID: `pmt_742-allston-st-77007`; group: **LEGAL_UNAVAILABLE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Retain Unknown. Blocking reason: Verified HCAD account or recorded plat for this exact home; successful address query found no exact match.

### 59. 1003 Enid St, Houston, Tx 77009

- ID: `2131312670`; group: **HELD_TRIAGE**; HCAD: `0331310910008`; match: EXACT.
- Legal: LT 8 BLK 91|BROOKE SMITH. Measured depth × width: 100.0002 × 50.0007 ft; area: 5000.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 42508. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,000 sf full lot

### 60. 1007 Cordell St, Houston, Tx 77009

- ID: `2131312288`; group: **HELD_TRIAGE**; HCAD: `0331260820010`; match: EXACT.
- Legal: LT 10 BLK 82|BROOKE SMITH. Measured depth × width: 100.0005 × 50.0004 ft; area: 5000.04 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 254737. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,000 sf full lot

### 61. 1010 Woodland St, Houston, Tx 77009

- ID: `2131374828`; group: **HELD_TRIAGE**; HCAD: `0620660000003`; match: EXACT.
- Legal: LT 3 BLK 15|NORHILL. Measured depth × width: 100.7704 × 50.4128 ft; area: 5078.13 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 625000; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,078 sf full lot

### 62. 1013 Woodland St, Houston, TX 77009

- ID: `pmt_1013-woodland-st-77009`; group: **HELD_TRIAGE**; HCAD: `0620650000013`; match: EXACT.
- Legal: LT 13 BLK 14|NORHILL. Measured depth × width: 101.0974 × 50.4094 ft; area: 5090.96 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 625000; improvement value: 115647. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,091 sf full lot

### 63. 1015 Adele St, Houston, Tx 77009

- ID: `2131191611`; group: **HELD_TRIAGE**; HCAD: `0350120060007`; match: EXACT.
- Legal: LT 7 BLK 6|STUDES SEC 1. Measured depth × width: 99.7158 × 50.1805 ft; area: 4981.25 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: None; improvement value: None. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,981 sf = 100% of plat median 5,000

### 64. 1021 Nadine St, Houston, Tx 77009

- ID: `2131191267`; group: **HELD_TRIAGE**; HCAD: `0350110030005`; match: EXACT.
- Legal: LT 5 BLK 3|STUDES SEC 1. Measured depth × width: 100.0002 × 50.0003 ft; area: 5000.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 12862. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,000 sf full lot

### 65. 1025 Adele St, Houston, Tx 77009

- ID: `2131191607`; group: **HELD_TRIAGE**; HCAD: `0350120060004`; match: EXACT.
- Legal: LT 4 BLK 6|STUDES SEC 1. Measured depth × width: 100.0 × 54.0847 ft; area: 5370.85 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 159915. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,371 sf full lot

### 66. 1032 Key St, Houston, TX 77009

- ID: `pmt_1032-key-st-77009`; group: **HELD_TRIAGE**; HCAD: `0621120000029`; match: EXACT.
- Legal: LT 8 BLK 133|NORTH NORHILL. Measured depth × width: 100.0003 × 50.0001 ft; area: 5000.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 0; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,000 sf full lot

### 67. 1040 Louise St, Houston, TX 77009

- ID: `pmt_1040-louise-st-77009`; group: **HELD_TRIAGE**; HCAD: `0350120060020`; match: EXACT.
- Legal: LT 20 BLK 6|STUDES SEC 1. Measured depth × width: 103.8557 × 50.1848 ft; area: 5205.19 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 25705. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,908 sf = 98% of plat median 5,000

### 68. 1107 E 27th St, Houston, Tx 77009

- ID: `2131242651`; group: **HELD_TRIAGE**; HCAD: `0351100060003`; match: EXACT.
- Legal: LT 3 BLK 6|SUNSET HEIGHTS EXTN . Measured depth × width: 100.7883 × 49.9936 ft; area: 4999.45 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 29962. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,999 sf = 100% of plat median 4,999

### 69. 1115 Adele St, Houston, Tx 77009

- ID: `2131191542`; group: **HELD_TRIAGE**; HCAD: `0350120050008`; match: EXACT.
- Legal: LT 8 BLK 5|STUDES SEC 1. Measured depth × width: 100.0001 × 49.9998 ft; area: 4998.86 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 42612. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,999 sf = 100% of plat median 5,000

### 70. 1123 Nadine St, Houston, Tx 77009

- ID: `2131191409`; group: **HELD_TRIAGE**; HCAD: `0350110040006`; match: EXACT.
- Legal: LT 6 BLK 4|STUDES SEC 1. Measured depth × width: 100.0002 × 49.999 ft; area: 4999.85 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 33000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 5,000 sf = 100% of plat median 5,000

### 71. 1124 W 21st St, Houston, Tx 77008

- ID: `2131200959`; group: **HELD_TRIAGE**; HCAD: `0610190030009`; match: EXACT.
- Legal: TR 9A BLK 3|QUENSELL LAWN. Measured depth × width: 73.7836 × 60.0006 ft; area: 4293.83 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300300; improvement value: 73762. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SPLIT. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,294 sf = 59% of plat median 7,250

### 72. 1126 W 22nd St, Houston, Tx 77008

- ID: `2131200820`; group: **HELD_TRIAGE**; HCAD: `0610190020015`; match: EXACT.
- Legal: LTS 14 & 15 BLK 2|QUENSELL LAWN. Measured depth × width: 144.9996 × 100.0004 ft; area: 14499.93 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 942500; improvement value: 105606. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 14,500 sf — larger than any Heights full lot

### 73. 1128 Adele St, Houston, Tx 77009

- ID: `2131191475`; group: **HELD_TRIAGE**; HCAD: `0350110040018`; match: EXACT.
- Legal: LT 18 BLK 4|STUDES SEC 1. Measured depth × width: 100.0762 × 50.0308 ft; area: 4995.54 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 375000; improvement value: 10000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,996 sf = 100% of plat median 5,000

### 74. 1138 Fugate St, Houston, TX 77009

- ID: `pmt_1138-fugate-st-77009`; group: **HELD_TRIAGE**; HCAD: `0621010000010`; match: EXACT.
- Legal: LT 10 BLK 122|NORTH NORHILL. Measured depth × width: 99.9997 × 49.9999 ft; area: 4999.94 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. no parcel, no legal

### 75. 117 E 25th St, Houston, Tx 77008

- ID: `2131437447`; group: **HELD_TRIAGE**; HCAD: `0562820000009`; match: EXACT.
- Legal: LTS 8 & 9 BLK 8|MILROY PLACE. Measured depth × width: 104.0015 × 91.0 ft; area: 9463.93 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 804440; improvement value: 45560. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal assembled 2 lots, 9,464 sf >= 2x2400

### 76. 117 Munford St, Houston, Tx 77008

- ID: `2131437359`; group: **HELD_TRIAGE**; HCAD: `0562790000009`; match: EXACT.
- Legal: LT 9 BLK 5|MILROY PLACE. Measured depth × width: 100.0007 × 51.9997 ft; area: 5199.95 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 442000; improvement value: 148000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,200 sf full lot

### 77. 118 E 24th St, Houston, Tx 77008

- ID: `2131437170`; group: **HELD_TRIAGE**; HCAD: `0562750000012`; match: EXACT.
- Legal: LT 12 BLK 1|MILROY PLACE. Measured depth × width: 99.7411 × 50.9029 ft; area: 5069.44 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 442000; improvement value: 111521. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,069 sf full lot

### 78. 1201 Cordell St, Houston, Tx 77009

- ID: `2131177133`; group: **HELD_TRIAGE**; HCAD: `0331250800007`; match: EXACT.
- Legal: LT 7 BLK 80|BROOKE SMITH. Measured depth × width: 100.1041 × 50.1777 ft; area: 5021.92 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 120537. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,022 sf full lot

### 79. 1204 Cordell St, Houston, Tx 77009

- ID: `2131176672`; group: **HELD_TRIAGE**; HCAD: `0331220730005`; match: EXACT.
- Legal: LT 5 BLK 73|BROOKE SMITH. Measured depth × width: 100.0003 × 49.9998 ft; area: 4999.99 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 102101. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 5,000 sf = 100% of plat median 5,000

### 80. 1208 Cordell St, Houston, Tx 77009

- ID: `2131176668`; group: **HELD_TRIAGE**; HCAD: `0331220730003`; match: EXACT.
- Legal: LT 3 BLK 73|BROOKE SMITH. Measured depth × width: 100.0 × 49.9998 ft; area: 4999.97 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 505758. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 5,000 sf = 100% of plat median 5,000

### 81. 1211 Gibbs St, Houston, Tx 77009

- ID: `2131318291`; group: **HELD_TRIAGE**; HCAD: `0350930450029`; match: EXACT.
- Legal: LTS 29 THRU 34 BLK 45|SUNSET HEIGHTS. Measured depth × width: 196.7673 × 120.2812 ft; area: 20490.69 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1560900; improvement value: 169560. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 20,491 sf — larger than any Heights full lot

### 82. 1211 N Durham Dr, Houston, Tx 77008

- ID: `2131179219`; group: **HELD_TRIAGE**; HCAD: `1468120010001`; match: EXACT.
- Legal: RES A BLK 1|FUR PAWS CENTER. Measured depth × width: 124.1408 × 100.0 ft; area: 12399.98 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1240000; improvement value: 101771. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 12,400 sf — larger than any Heights full lot

### 83. 1219 Bay Oaks Rd, Houston, Tx 77008

- ID: `2131537524`; group: **HELD_TRIAGE**; HCAD: `0771810060016`; match: EXACT.
- Legal: LT 16 BLK 6|TIMBERGROVE MANOR. Measured depth × width: 301.942 × 57.6252 ft; area: 16833.53 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 666000; improvement value: 100. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 16,834 sf — larger than any Heights full lot

### 84. 1412 Northwood St, Houston, Tx 77009

- ID: `2131228942`; group: **HELD_TRIAGE**; HCAD: `0331430150002`; match: EXACT.
- Legal: LT 2 BLK 115|BROOKE SMITH. Measured depth × width: 105.5318 × 50.179 ft; area: 5215.23 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 225832. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,215 sf full lot

### 85. 1506 Tabor St, Houston, Tx 77009

- ID: `2131312852`; group: **HELD_TRIAGE**; HCAD: `0331340970003`; match: EXACT.
- Legal: LT 3 & TR 4A BLK 97|BROOKE SMITH. Measured depth × width: 99.714 × 62.618 ft; area: 6221.55 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 360000; improvement value: 416225. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 1 TR + 6,222 sf full lot

### 86. 1518 W 25th St, Houston, Tx 77008

- ID: `2131330179`; group: **HELD_TRIAGE**; HCAD: `0561650000288`; match: EXACT.
- Legal: TR 141E|SHADY ACRES SEC 2. Measured depth × width: 181.4144 × 145.1903 ft; area: 20116.89 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1215240; improvement value: 23898. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 20,117 sf — larger than any Heights full lot

### 87. 1522 Glen Oaks St, Houston, Tx 77008

- ID: `2131538738`; group: **HELD_TRIAGE**; HCAD: `0771820170006`; match: EXACT.
- Legal: LT 6 BLK 17|TIMBERGROVE MANOR SEC 3. Measured depth × width: 237.4591 × 123.8498 ft; area: 15959.58 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 704700; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 15,954 sf — larger than any Heights full lot

### 88. 1602 Turnpike Rd, Houston, TX 77008

- ID: `pmt_1602-turnpike-rd-77008`; group: **HELD_TRIAGE**; HCAD: `0771820170019`; match: EXACT.
- Legal: LT 19 BLK 17|TIMBERGROVE MANOR SEC 3. Measured depth × width: 303.5196 × 74.9627 ft; area: 17333.03 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 619992; improvement value: 943750. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 17,339 sf — larger than any Heights full lot

### 89. 1610 W 21st St, Houston, Tx 77008

- ID: `2131331239`; group: **HELD_TRIAGE**; HCAD: `0561660000250`; match: EXACT.
- Legal: LTS 250 & 251|SHADY ACRES SEC 2. Measured depth × width: 126.9222 × 99.9995 ft; area: 12653.55 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 737100; improvement value: 50782. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 12,654 sf — larger than any Heights full lot

### 90. 1631 Walton St, Houston, Tx 77009

- ID: `2131313407`; group: **HELD_TRIAGE**; HCAD: `0521510000008`; match: EXACT.
- Legal: LT 8|OAKDALE PLACE 2ND R/P. Measured depth × width: 100.6901 × 52.8305 ft; area: 5278.85 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 250000; improvement value: 90000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,279 sf full lot

### 91. 1808 N Shepherd Dr, Houston, Tx 77008

- ID: `2131187484`; group: **HELD_TRIAGE**; HCAD: `1455700010001`; match: EXACT.
- Legal: RES A BLK 1|HEIGHTS HAVEN. Measured depth × width: 150.1282 × 131.0002 ft; area: 19649.92 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1964600; improvement value: 484873. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 19,650 sf — larger than any Heights full lot

### 92. 205 E 24th St, Houston, Tx 77008

- ID: `2131437247`; group: **HELD_TRIAGE**; HCAD: `0562770000003`; match: EXACT.
- Legal: LT 3 BLK 3|MILROY PLACE. Measured depth × width: 100.2215 × 52.9994 ft; area: 5298.31 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450500; improvement value: 138500. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,298 sf full lot

### 93. 205 Northwood St, Houston, Tx 77009

- ID: `2131195093`; group: **HELD_TRIAGE**; HCAD: `0330700000009`; match: EXACT.
- Legal: LT 9 BLK 4|BROOKE SMITH. Measured depth × width: 102.3079 × 49.9874 ft; area: 5084.71 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 149112. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,085 sf full lot

### 94. 2119 Gostick St, Houston, Tx 77008

- ID: `2131129729`; group: **HELD_TRIAGE**; HCAD: `0151570000010`; match: EXACT.
- Legal: TRS 10 & 11A BLK 1|GOSTICK. Measured depth × width: 100.0852 × 46.0002 ft; area: 4599.91 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 437000; improvement value: 183003. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,600 sf = 81% of plat median 5,700

### 95. 212 E 25th St, Houston, Tx 77008

- ID: `2131437380`; group: **HELD_TRIAGE**; HCAD: `0562800000012`; match: EXACT.
- Legal: LT 12 & E 7FT OF LT 13 BLK 6|MILROY PLACE. Measured depth × width: 98.8866 × 60.0002 ft; area: 5907.92 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 510000; improvement value: 150000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal assembled 2 lots, 5,908 sf >= 2x2400

### 96. 301 Enid St, Houston, Tx 77009

- ID: `2131227429`; group: **HELD_TRIAGE**; HCAD: `0330830000007`; match: EXACT.
- Legal: LT 7 BLK 17|BROOKE SMITH. Measured depth × width: 100.9802 × 50.6869 ft; area: 5093.01 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 25000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,093 sf full lot

### 97. 303 Enid St, Houston, Tx 77009

- ID: `2170723831`; group: **HELD_TRIAGE**; HCAD: `0330830000014`; match: EXACT.
- Legal: LT 8 BLK 17|BROOKE SMITH. Measured depth × width: 101.0749 × 50.4194 ft; area: 5093.03 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 65000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,093 sf full lot

### 98. 305 Tabor St, Houston, Tx 77009

- ID: `2131226980`; group: **HELD_TRIAGE**; HCAD: `0330740000009`; match: EXACT.
- Legal: LT 9 BLK 8|BROOKE SMITH. Measured depth × width: 101.7885 × 50.2026 ft; area: 5090.2 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 60041. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,090 sf full lot

### 99. 404 W 21st St, Houston, Tx 77008

- ID: `2131186526`; group: **HELD_TRIAGE**; HCAD: `0200800000001`; match: EXACT.
- Legal: LTS 1 THRU 9 BLK 84|HOUSTON HEIGHTS. Measured depth × width: 224.9905 × 131.0007 ft; area: 29473.05 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 2210625; improvement value: 40086. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 29,473 sf — larger than any Heights full lot

### 100. 423 E 28th St, Houston, Tx 77008

- ID: `2131207530`; group: **HELD_TRIAGE**; HCAD: `0350760120013`; match: EXACT.
- Legal: LT 13 & TR 14A BLK 12|SUNSET HEIGHTS. Measured depth × width: 120.2277 × 37.1434 ft; area: 4447.55 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 369750; improvement value: 34271. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,448 sf = 77% of plat median 5,754

### 101. 427 E 24th St, Houston, Tx 77008

- ID: `2131318786`; group: **HELD_TRIAGE**; HCAD: `0350980560013`; match: EXACT.
- Legal: LTS 13 THRU 17 BLK 56|SUNSET HEIGHTS. Measured depth × width: 123.4265 × 120.0007 ft; area: 14669.56 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1275000; improvement value: 336910. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 14,670 sf — larger than any Heights full lot

### 102. 4308 Julian St, Houston, Tx 77009

- ID: `2131347730`; group: **HELD_TRIAGE**; HCAD: `0590270000006`; match: EXACT.
- Legal: LT 6 BLK 1|PARKER. Measured depth × width: 104.8817 × 46.3412 ft; area: 4639.1 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 171463. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,639 sf = 101% of plat median 4,603

### 103. 507 Cordell St, Houston, Tx 77009

- ID: `2131227565`; group: **HELD_TRIAGE**; HCAD: `0330860000012`; match: EXACT.
- Legal: LT 12 BLK 20|BROOKE SMITH. Measured depth × width: 98.6687 × 50.1929 ft; area: 4939.81 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 106477. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,940 sf = 100% of plat median 4,940

### 104. 511 Cordell St, Houston, Tx 77009

- ID: `2131227567`; group: **HELD_TRIAGE**; HCAD: `0330860000013`; match: EXACT.
- Legal: LT 13 BLK 20|BROOKE SMITH. Measured depth × width: 98.6742 × 49.9733 ft; area: 4925.55 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 60808. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,926 sf = 100% of plat median 4,940

### 105. 512 Threlkeld St, Houston, Tx 77007

- ID: `2131370103`; group: **HELD_TRIAGE**; HCAD: `0512050030014`; match: EXACT.
- Legal: LT 14 BLK 3|USENER. Measured depth × width: 99.9992 × 50.0005 ft; area: 4999.95 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 150428. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 5,000 sf = 100% of plat median 5,000

### 106. 519 Threlkeld St, Houston, Tx 77007

- ID: `2130814684`; group: **HELD_TRIAGE**; HCAD: `1244690010005`; match: EXACT.
- Legal: LT 5 BLK 1|THRELKELD POINT. Measured depth × width: 136.3517 × 35.0025 ft; area: 4758.02 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 475800; improvement value: 174200. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,758 sf in the 4-5k dead zone, no plat median

### 107. 531 Threlkeld St, Houston, Tx 77007

- ID: `2131370154`; group: **HELD_TRIAGE**; HCAD: `0512050040005`; match: EXACT.
- Legal: TR 23 BLK 4|USENER. Measured depth × width: 100.001 × 60.0003 ft; area: 5999.99 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 477855; improvement value: 37798. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal TR only (1 frag) + 6,000 sf full lot

### 108. 533 Studewood St, Houston, Tx 77007

- ID: `2131370113`; group: **HELD_TRIAGE**; HCAD: `0512050030021`; match: EXACT.
- Legal: LT 21 BLK 3|USENER. Measured depth × width: 115.0004 × 49.9999 ft; area: 5749.99 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 465750; improvement value: 161151. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,750 sf full lot

### 109. 607 Melwood St, Houston, Tx 77009

- ID: `2131228154`; group: **HELD_TRIAGE**; HCAD: `0330960000012`; match: EXACT.
- Legal: LT 12 BLK 30|BROOKE SMITH. Measured depth × width: 100.5492 × 49.5749 ft; area: 4967.4 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 325000; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,967 sf = 99% of plat median 5,001

### 110. 611 Mathis St, Houston, Tx 77009

- ID: `2131175661`; group: **HELD_TRIAGE**; HCAD: `0331140610001`; match: EXACT.
- Legal: LT 1 BLK 61|BROOKE SMITH. Measured depth × width: 100.0033 × 50.0003 ft; area: 4999.85 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 240000; improvement value: 183144. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 5,000 sf = 100% of plat median 5,000

### 111. 626 E 22nd St, Houston, Tx 77008

- ID: `2131145222`; group: **HELD_TRIAGE**; HCAD: `0200610000001`; match: EXACT.
- Legal: LT 1 BLK 65|HOUSTON HEIGHTS 72ND AMEND . Measured depth × width: 142.5006 × 31.7801 ft; area: 4510.19 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 360800; improvement value: 739436. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,510 sf = 90% of plat median 4,987

### 112. 707 E 6th 1/2 St, Houston, Tx 77007

- ID: `2131074923`; group: **HELD_TRIAGE**; HCAD: `0350290550020`; match: EXACT.
- Legal: LTS 21 22 & 23 & TRS 20 & 24|BLK 55|STUDES SEC 2. Measured depth × width: 202.116 × 124.9991 ft; area: 24982.95 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 2137500; improvement value: 245288. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 24,983 sf — larger than any Heights full lot

### 113. 710 E 13th St, Houston, Tx 77008

- ID: `2161199012`; group: **HELD_TRIAGE**; HCAD: `1393250010002`; match: EXACT.
- Legal: LT 2 BLK 1|EAST 13TH STREET GROVE. Measured depth × width: 191.5001 × 25.001 ft; area: 4784.59 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 454480; improvement value: 945520. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,785 sf in the 4-5k dead zone, no plat median

### 114. 710 Le Green St, Houston, TX 77008

- ID: `pmt_710-le-green-st-77008`; group: **HELD_TRIAGE**; HCAD: `0520390000072`; match: EXACT.
- Legal: LT 72|RIDGEWOOD. Measured depth × width: 100.2083 × 50.4452 ft; area: 5042.63 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 475000; improvement value: 175189. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,043 sf full lot

### 115. 731 E 27th St, Houston, Tx 77009

- ID: `2131208376`; group: **HELD_TRIAGE**; HCAD: `0350810220024`; match: EXACT.
- Legal: LTS 24 THRU 29 BLK 22|SUNSET HEIGHTS. Measured depth × width: 149.9985 × 120.0002 ft; area: 17999.79 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: None; improvement value: None. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 18,000 sf — larger than any Heights full lot

### 116. 741 W 21st St, Houston, Tx 77008

- ID: `2131042481`; group: **HELD_TRIAGE**; HCAD: `0200740000027`; match: EXACT.
- Legal: LTS 27 & 28 BLK 78|HOUSTON HEIGHTS. Measured depth × width: 131.0002 × 50.0001 ft; area: 6550.0 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 524000; improvement value: 30323. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal assembled 2 lots, 6,550 sf >= 2x2400

### 117. 745 E 11th 1/2 St, Houston, Tx 77008

- ID: `2131240334`; group: **HELD_TRIAGE**; HCAD: `0350190360013`; match: EXACT.
- Legal: LTS 13 & 14 BLK 36|STUDES SEC 2. Measured depth × width: 124.923 × 100.0581 ft; area: 12472.73 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1125000; improvement value: 15300. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 12,473 sf — larger than any Heights full lot

### 118. 805 Tabor St, Houston, Tx 77009

- ID: `2131228576`; group: **HELD_TRIAGE**; HCAD: `0331400090009`; match: EXACT.
- Legal: LT 9 BLK 109|BROOKE SMITH. Measured depth × width: 100.3097 × 50.1904 ft; area: 5012.55 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 250000; improvement value: 40000. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,013 sf full lot

### 119. 805 Walton St, Houston, Tx 77009

- ID: `2131313166`; group: **HELD_TRIAGE**; HCAD: `0331370040009`; match: EXACT.
- Legal: LT 9 BLK 104|BROOKE SMITH. Measured depth × width: 100.0459 × 49.9746 ft; area: 4992.77 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 300000; improvement value: 51702. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,993 sf = 100% of plat median 5,000

### 120. 835 Lawrence St, Houston, TX 77007

- ID: `pmt_835-lawrence-st-77007`; group: **HELD_TRIAGE**; HCAD: `0621980020043`; match: EXACT.
- Legal: LTS 43 & 44 & S 7 FT OF LT 45 BLK 2|HARDING HEIGHTS. Measured depth × width: 100.5315 × 56.9987 ft; area: 5699.76 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 570000; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal claims 3 lots but only 5,700 sf

### 121. 838 Waverly St, Houston, Tx 77007

- ID: `2131044801`; group: **HELD_TRIAGE**; HCAD: `0202370000031`; match: EXACT.
- Legal: LTS 31 32 & 33 BLK 241|HOUSTON HEIGHTS. Measured depth × width: 132.0012 × 99.9995 ft; area: 13199.95 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1452000; improvement value: 87050. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 13,200 sf — larger than any Heights full lot

### 122. 839 E 26th St, Houston, Tx 77009

- ID: `2131192777`; group: **HELD_TRIAGE**; HCAD: `0350840270029`; match: EXACT.
- Legal: LTS 29 & 30 BLK 27|SUNSET HEIGHTS. Measured depth × width: 120.0003 × 49.9999 ft; area: 5999.97 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 450000; improvement value: 0. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal assembled 2 lots, 6,000 sf >= 2x2400

### 123. 902 W 22nd St, Houston, Tx 77008

- ID: `2131200768`; group: **HELD_TRIAGE**; HCAD: `0610190010019`; match: EXACT.
- Legal: LTS 22 23 & 24 BLK 1|QUENSELL LAWN. Measured depth × width: 163.8547 × 148.1943 ft; area: 23939.75 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 1321680; improvement value: 33444. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 23,940 sf — larger than any Heights full lot

### 124. 905 Adele St, Houston, Tx 77009

- ID: `2131370476`; group: **HELD_TRIAGE**; HCAD: `0513480000009`; match: EXACT.
- Legal: LT 9 & TR 10A BLK 4|PINERIDGE. Measured depth × width: 100.9294 × 44.4175 ft; area: 4459.03 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 337500; improvement value: 16521. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,500 sf = 90% of plat median 5,000

### 125. 905 Bay Oaks Rd, Houston, Tx 77008

- ID: `2131538718`; group: **HELD_TRIAGE**; HCAD: `0771820160010`; match: EXACT.
- Legal: LT 10 BLK 16|TIMBERGROVE MANOR SEC 3. Measured depth × width: 129.9474 × 120.5125 ft; area: 13835.48 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 865500; improvement value: 101846. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 13,835 sf — larger than any Heights full lot

### 126. 909 Bayland Ave, Houston, Tx 77009

- ID: `2131152146`; group: **HELD_TRIAGE**; HCAD: `0513780000023`; match: EXACT.
- Legal: TRS 23 & 24A BLK 6|WOODSON PLACE. Measured depth × width: 98.851 × 49.7186 ft; area: 4893.35 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 625000; improvement value: 40156. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,893 sf = 99% of plat median 4,959

### 127. 932 W Temple St, Houston, Tx 77009

- ID: `2131387479`; group: **HELD_TRIAGE**; HCAD: `0621330190002`; match: EXACT.
- Legal: LT 2 BLK 219|EAST NORHILL. Measured depth × width: 106.4632 × 49.7377 ft; area: 5284.46 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 468000; improvement value: 137215. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,284 sf full lot

### 128. 949 Ridge St, Houston, TX 77009

- ID: `pmt_949-ridge-st-77009`; group: **HELD_TRIAGE**; HCAD: `0562880000014`; match: EXACT.
- Legal: LT 14 BLK 2|RIDGEMONT SEC 1. Measured depth × width: 105.6837 × 50.0691 ft; area: 5227.63 sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: 625000; improvement value: 130059. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SINGLE. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal LT n + 5,228 sf full lot

### 129. 1300 Waverly St, Houston, Tx 77008

- ID: `2131146860`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: AMBIGUOUS.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 47296, "land_value": 720000, "parcel": {"account": "0201720000038", "area_sf": 8059.33, "depth_ft": 100.1031, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "TRS 19B 20B & 21B BLK 176|HOUSTON HEIGHTS", "matched": "1300 WAVERLY ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 80.6066}}, {"history": [], "improvement_value": 0, "land_value": 468000, "parcel": {"account": "0201720000019", "area_sf": 4931.71, "depth_ft": 100.1509, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LTS 19A 20A & 21A BLK 176|HOUSTON HEIGHTS", "matched": "1300 WAVERLY ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 49.311}}]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,932 sf = 68% of plat median 7,263

### 130. 2436 White Oak Dr, Houston, TX 77009

- ID: `pmt_2436-white-oak-dr-77009`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. no parcel, no legal

### 131. 631 Mazal (Pvt) Ln, Houston, TX 77009

- ID: `pmt_631-mazal-pvt-ln-77009`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: 3 (project 25114941).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 0, "land_value": 294000, "parcel": {"account": "1368390010007", "area_sf": 4170.46, "depth_ft": 99.9512, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LTS 7 8 & 9 BLK 1|NORTHWOOD ESTATES", "matched": "0 MAZAL LN", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 42.1076}}]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. legal claims 3 lots but only 4,170 sf

### 132. 745 W 17th St, Houston, TX 77008

- ID: `pmt_745-w-17th-st-77008`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 0, "land_value": 1206148, "parcel": {"account": "1365530010001", "area_sf": 16972.87, "depth_ft": 136.5489, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LTS 1 THRU 10 BLK 1|CITY VIEW LOFTS AT W 17TH", "matched": "0 W 17TH ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 130.9981}}]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 16,983 sf — larger than any Heights full lot

### 133. 832 E 27th St, Houston, TX 77009

- ID: `pmt_832-e-27th-st-77009`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. no parcel, no legal

### 134. 837 W 25th St, Houston, Tx 77008

- ID: `2131282520`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: AMBIGUOUS.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 178912, "land_value": 146000, "parcel": {"account": "1265010010001", "area_sf": 1824.99, "depth_ft": 50.0002, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LT 1 BLK 1|COTTAGES AT THE HEIGHTS", "matched": "837 W 25TH ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 36.4998}}, {"history": [], "improvement_value": 128234, "land_value": 128000, "parcel": {"account": "1265010010002", "area_sf": 1600.0, "depth_ft": 50.0001, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LT 2 BLK 1|COTTAGES AT THE HEIGHTS", "matched": "837 W 25TH ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 31.9999}}, {"history": [], "improvement_value": 187798, "land_value": 128000, "parcel": {"account": "1265010010003", "area_sf": 1600.01, "depth_ft": 50.0002, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LT 3 BLK 1|COTTAGES AT THE HEIGHTS", "matched": "837 W 25TH ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 32.0003}}, {"history": [{"acct_continuity": true, "addresses": {"child": ["833 W  25TH ST", "835 W  25TH ST"], "parent": ["837 W  25TH ST"]}, "areas": {"child_sf": [3275.0, 3275.0], "delta_pct": -0.0, "parent_sf": [6550.0], "sum_child_sf": 6550.0, "sum_parent_sf": 6550.0}, "child_accts": ["0200310000066", "0200310000027"], "event": "SPLIT", "lat": 29.809074, "lng": -95.413819, "parent_accts": ["0200310000027"], "vintage": "2025_Oct->2026_Jul"}], "improvement_value": 83359, "land_value": 262000, "parcel": {"account": "0200310000027", "area_sf": 3274.99, "depth_ft": 131.0001, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LT 27 BLK 35|HOUSTON HEIGHTS", "matched": "835 W 25TH ST", "parcel_history": [{"children": ["0200310000066", "0200310000027"], "event": "SPLIT", "parents": ["0200310000027"], "source": "refresh/parcel_events.json", "vintage": "2025_Oct->2026_Jul"}], "source": "HCAD unverified contextual parcel", "width_ft": 25.0001}}]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SPLIT. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. parcel SPLIT into half lots (children ~3,275 sf)

### 135. 845 W 23rd St A, Houston, TX 77008

- ID: `pmt_845-w-23rd-st-a-77008`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: A; verified unit count: 2; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 38121, "land_value": 524000, "parcel": {"account": "0200460000024", "area_sf": 6549.58, "depth_ft": 131.475, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LTS 24 & 25 BLK 50|HOUSTON HEIGHTS", "matched": "845 W 23RD ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 49.9977}}]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SPLIT. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 2 lettered units on one parcel (6,550 sf)

### 136. 845 W 23rd St B, Houston, TX 77008

- ID: `pmt_845-w-23rd-st-b-77008`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: B; verified unit count: 2; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 38121, "land_value": 524000, "parcel": {"account": "0200460000024", "area_sf": 6549.58, "depth_ft": 131.475, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LTS 24 & 25 BLK 50|HOUSTON HEIGHTS", "matched": "845 W 23RD ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 49.9977}}]`.
- Recommendation: Not evaluated: human hold; RESOLVED-SPLIT. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 2 lettered units on one parcel (6,550 sf)

### 137. Enid St, Houston, Tx 77009

- ID: `2177158676`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 25089, "land_value": 205550, "parcel": {"account": "0690710020001", "area_sf": 4110.6, "depth_ft": 123.3298, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LT 1 BLK 1|MCFARLAND COURT 3RD PAR R/P", "matched": "0 ENID ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 33.3301}}]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,111 sf = 63% of plat median 6,479

### 138. Enid St, Houston, Tx 77009

- ID: `2177158678`; group: **HELD_TRIAGE**; HCAD: `unresolved`; match: NO_MATCH.
- Legal: Unavailable. Measured depth × width: unavailable × unavailable ft; area: unavailable sf.
- Unit letters: none; verified unit count: 1; master size: unavailable (project none).
- Land value: Unavailable; improvement value: Unavailable. Observed parcel history: `[]`.
- Unverified alternative/parent context (never used for assignment): `[{"history": [], "improvement_value": 33534, "land_value": 205550, "parcel": {"account": "0690710020003", "area_sf": 4111.81, "depth_ft": 123.3298, "depth_method": "minimum rotated rectangle, longest side", "geometry_crs": "EPSG:2278", "legal": "LT 3 BLK 1|MCFARLAND COURT 3RD PAR R/P", "matched": "0 ENID ST", "parcel_history": [], "source": "HCAD unverified contextual parcel", "width_ft": 33.34}}]`.
- Recommendation: Not evaluated: human hold; GENUINELY-AMBIGUOUS. Blocking reason: Prior human hold: requires explicit re-review; no classification authorized this session. 4,112 sf = 63% of plat median 6,479

## Construction-evidence discrepancy — 1019 E 7th (2026-09-10)

Retain the existing `needs_clarification` flag and stored Single Lot classification. The earlier review said “no build permit,” with a May 2026 purchase and the 1926 house still standing. The saved record actually carries Building Pmt **26064937**, valuation **$821,702**, description “QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC.” Its September 10 inspection feed is empty. Verify the permit identity/scope and the earlier note; do not resolve the contradiction by assuming construction has started. Removal of its unsupported Foundation label does not adjudicate this review.
