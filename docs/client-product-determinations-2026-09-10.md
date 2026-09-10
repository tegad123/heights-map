# Client product determinations and Heights boundary audit — 2026-09-10

Client determinations are authoritative. Nine addresses match eleven saved records because White Oak and 1016 E 27th each have separate listing and permit records. All are annotated with source=client, reason_code=CLIENT_DETERMINATION, and the review date. Stale shared product edits cannot override them. No other product assignments were persisted.

## Determinations

| Address | Prior saved product | Prior rendered product | Client product | Explicit pair |
|---|---|---|---|---|
| 2436 White Oak | Single Lot | Single Lot | Single Lot |  |
| 2436 White Oak Dr, Houston, TX 77009 | Unknown | Single Lot | Single Lot |  |
| 1438 Dian St A, Houston, TX 77008 | Unknown | Unknown | Split Lot | 1438 Dian |
| 1438 Dian St B, Houston, TX 77008 | Unknown | Split Lot | Split Lot | 1438 Dian |
| 305 W 17th St, Houston, TX 77008 | Unknown | Single Lot | Single Lot |  |
| 845 W 23rd St A, Houston, TX 77008 | Unknown | Unknown | Split Lot | 845 W 23rd |
| 845 W 23rd St B, Houston, TX 77008 | Unknown | Unknown | Split Lot | 845 W 23rd |
| 1807 Palmetto Landing Dr, Houston, TX 77009 | Unknown | Unknown | Split Lot | Palmetto Landing |
| 1809 Palmetto Landing Dr, Houston, TX 77009 | Unknown | Unknown | Split Lot | Palmetto Landing |
| 1016 E 27 th Street | Single Lot | Single Lot | Split Lot |  |
| 1016 E 27th St, Houston, TX 77009 | Unknown | Split Lot | Split Lot |  |

Dian A/B, 845 W 23rd A/B, and 1807/1809 Palmetto each change from two independent one-home pins to one twin project with two homes. The existing merge mechanism retains both records in source DATA, both permit sets and both market members. No homes are removed by pairing.

845 W 23rd A: the client Split Lot decision resolves the 6,550-sf parent-parcel ambiguity. The parent-lot size is not used to override this decision. Palmetto similarly receives the client label without applying the prior shallow-parcel classifier candidate. The saved Single Lot listing label at 1016 E 27th is corrected to Split Lot.

Triage protection: 77 of the 80 held source records are byte-identical. The three explicit client exceptions are 2436 White Oak and 845 W 23rd A/B. The holds policy file is unchanged; stored client labels take precedence. The historical 138-record review list is retained for evidence; product-review-remaining-after-client-2026-09-10.csv contains the 129 unresolved source-cohort records after these nine determinations.

## Boundary findings reported before disposition

**The full outside-ZONE_RING list is empty.** All 605 saved DATA records and 791 sale records are inside the unchanged polygon. The ring exactly matches heights_boundary.geojson. All 550 pre-change rendered DATA marker positions, 547 post-pairing positions, and all sale coordinates also pass. All 152 current shared position edits are inside; none breaches the separate -95.370 longitude limit.

The specified polygon reaches latitude 29.769 at its southern edge. Center, Edwards, Winter and Schuler records are inside it. These are not demonstrated zone-check bypasses. Removing them under an outside-polygon rule would contradict the unchanged boundary. No boundary geometry, exclusions, coordinates or records were changed. The per-record saved-coordinate audit is heights-boundary-audit-2026-09-10.csv; each row includes kind, coordinates, outside distance and disposition.

Cause groups for Heights out-of-boundary records: none to attribute to historical import, omitted importer guard, or changed centroid. Disposition: keep all 1,396 audited source records; removals 0; reassignments 0; dropped rows 0. The dedicated zero-row ledger is pulls/client_boundary_20260910/dropped_client_boundary_2026-09-10.csv.

## Other markets — saved coordinate counts only

No other market was classified, browser-validated, modified or reassigned. These are raw saved-row comparisons to the configured market boundary, not claims that all such rows render live.

| Market | Source rows | Outside configured boundary/box | Reference |
|---|---:|---:|---|
| heights | 605 | 0 | heights_boundary.geojson |
| montrose | 213 | 37 | montrose_boundary.geojson |
| westu | 101 | 13 | configured coordinate box; no market polygon |
| riveroaks | 40 | 0 | riveroaks_boundary.geojson |
| springbranch | 417 | 26 | springbranch_boundary.geojson |
| timbergrove | 41 | 0 | timbergrove_boundary.geojson |
| gardenoaksoakforest | 511 | 2 | gardenoaksoakforest_boundary.geojson |
| springvalley | 6 | Not assessed | No configured market boundary; ingest disabled |

West University has no market polygon by design; 13 is a configured-box comparison and is not sufficient evidence to remove those homes. Spring Valley has no configured ingest boundary, so no substitute polygon was invented.

## Recurrence check

No missing Heights importer zone call was found in the active permit, combined HAR, sold, active-listing, market-status or deed paths. No importer code was changed. Invoking combined_market_ingest.load() with a copied valid sale row placed at latitude 29.7500, longitude -95.3900 returned eligible=0, ledger=1, reason=OOZ_POLY. This synthetic rejection is separate from the zero actual removals. The imported southern rows pass because the existing polygon contains their coordinates.

## Totals and invocation evidence

The current shared endpoint answered successfully, with snapshot timestamp 2026-09-10T15:59:06.759Z, 51 product edits and 152 position edits. The earlier reported 404 did not recur on this read. Existing shared edits are left intact, including edits outside the six requested client determinations.

| Measure | Before | After |
|---|---:|---:|
| Saved DATA records | 605 | 605 |
| Rendered project pins | 550 | 547 |
| Represented homes | 597 | 597 |
| Permit-bearing rendered pins | 378 | 375 |
| Unique rendered permit projects | 406 | 406 |
| Unique saved DATA permit projects | 423 | 423 |
| Inspection-feed projects (header badge) | 452 | 452 |
| Permit references across rendered pins | 410 | 410 |
| Under Construction homes | 226 | 226 |
| Product Unknown homes (current shared state) | 111 | 106 |
| Under Construction Unknown homes | 9 | 5 |
| Original source-review Unknowns | 138 | 129 |
| Finished | 138 | 138 |
| Sold archive | 791 | 791 |
| Deeds | 139 | 139 |
| Custom | 19 | 19 |
| Sold Off Market | 1 | 1 |

`/Users/nemoclaw/insp-venv/bin/python -B tests/client_boundary_browser.py --shared pulls/client_boundary_20260910/shared.json --output pulls/client_boundary_20260910/browser-after.json` returned `homes: 597, uc: 226, ucUnknown: 5, deeds: 139, sold: 791, finishedHeader: 138`. This Heights-only browser invocation verifies all three actual twin projects, their two-home weights and both client annotations; rejects a stale conflicting shared product edit; and checks marker coordinates.

`/Users/nemoclaw/insp-venv/bin/python -B tests/client_boundary_check.py` returned: six determinations, 11 source records, three paired projects; 594 unrelated source records byte-identical; all individual-home phases unchanged; 4,410 base-timeline pairs with zero violations. Finished rows remain 34 + 9 + 19 + 76 = 138. Construction fixtures, Allston, and Merrill Active with terminated history pass.

## Open items

The desired freeway-based southern extent differs from the polygon currently designated authoritative. Additional explicit address exclusions or a separately authorized boundary decision are needed to remove inside-polygon southern properties. No such exclusions were invented here.

The client notes call 305 W 17th and 1016 E 27th terminated. Their permit records currently have No Market Record in the separate market snapshot, and the duplicate 1016 listing carries a legacy pending tag. These market-linkage discrepancies are reported without changing market-status data or logic. White Oak and 1016 retain their separate listing/permit records; only the three explicitly requested pairs are merged.
