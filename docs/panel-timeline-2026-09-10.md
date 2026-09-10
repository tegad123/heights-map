# Capped overdue timelines and Heights panel — 2026-09-10

Comparison clock: 2026-09-09, matching the existing fixture suite. Heights uses the saved shared-edit snapshot; other markets use their repository defaults. The remote shared-edit endpoint returned 404 in the preceding session; this is a deterministic comparison, not a fresh remote-state audit.

## Timeline decision

Use a 1× phase-duration cap on the overdue ETA contribution. Keep full elapsed and overdue days as stall evidence. Base durations and phase derivation are unchanged. MEP Finals is capped at 42 remaining days (six weeks); 2× permits 63 days (nine weeks). Across eight markets, 1× changes 154 homes; 2× would change 129.

115 Northwood: 181 days / 2027-03-09 → 42 days / 2026-10-21. It remains stalled 26 weeks in MEP Finals, 23 weeks overdue. 727 W 21st is another six-month fixture: 174 → 42 days. The approximately 22-week example, 606 Skyland Terrace, moves 152 → 42 days. Harvard remains 247 days / 2027-05-14; 629 E 26th remains 200 days / 2027-03-28.

## Full distribution (homes, including paired-home weights)

| Market | Unchanged | 1–30 days | 31–90 days | 91–180 days | >180 days | No remaining ETA |
|---|---:|---:|---:|---:|---:|---:|
| index | 145 | 13 | 21 | 7 | 24 | 386 |
| montrose | 62 | 11 | 2 | 7 | 0 | 144 |
| riveroaks | 7 | 0 | 0 | 2 | 0 | 31 |
| springbranch | 92 | 4 | 11 | 12 | 1 | 300 |
| springvalley | 0 | 0 | 0 | 0 | 0 | 6 |
| timbergrove | 16 | 0 | 3 | 1 | 0 | 21 |
| westu | 22 | 1 | 1 | 2 | 0 | 74 |
| gardenoaksoakforest | 9 | 2 | 0 | 4 | 25 | 112 |

All changes move dates earlier; none moves later. No remaining ETA includes completed homes and records without dated construction evidence. The companion CSV records every pin’s before/after date and both cap candidates.

## Ten largest moves across all markets

All ten are in Garden Oaks / Oak Forest.

| Address | Before days | After days | Before date | After date | Days earlier |
|---|---:|---:|---|---|---:|
| 1721 DU BARRY LN, Houston, TX 77018 | 910 | 42 | 2029-03-07 | 2026-10-21 | 868 |
| 5214 LIDO LN, Houston, TX 77092 | 901 | 42 | 2029-02-26 | 2026-10-21 | 859 |
| 4721 WATONGA BLVD, Houston, TX 77092 | 894 | 42 | 2029-02-19 | 2026-10-21 | 852 |
| 1358 W 43RD ST, Houston, TX 77018 | 838 | 42 | 2028-12-25 | 2026-10-21 | 796 |
| 710 W 41ST ST, Houston, TX 77018 | 782 | 42 | 2028-10-30 | 2026-10-21 | 740 |
| 1431 WOODCREST DR, Houston, TX 77018 | 763 | 42 | 2028-10-11 | 2026-10-21 | 721 |
| 1450 GARDENIA DR, Houston, TX 77018 | 758 | 42 | 2028-10-06 | 2026-10-21 | 716 |
| 1218 DU BARRY LN, Houston, TX 77018 | 730 | 42 | 2028-09-08 | 2026-10-21 | 688 |
| 1218 LAMONTE LN, Houston, TX 77018 | 723 | 42 | 2028-09-01 | 2026-10-21 | 681 |
| 1587 SUE BARNETT DR, Houston, TX 77018 | 721 | 42 | 2028-08-30 | 2026-10-21 | 679 |

## Panel proposal reported before application

Measured baseline: Under Construction 237, Finished 150, Sold Comps 791. Proposed/applied: Under Construction 225; Finished 138; Sold Comps view 790, with all 791 sale records retained. Twelve closed-sale MEP Finals homes also leave construction inventory; their phases remain unchanged.

Finished: On Market 34; Pending 9; Terminated 19; No Market Record 76. Every status has all four product rows, including zero-count Unknown.

Overlapping construction flags: On the Market (building) 14 = Framing 2 + MEP Roughs 1 + INT.CAB 6 + MEP Finals 5. Pending, not Complete 8 = INT.CAB 4 + MEP Finals 4. These are represented-home counts for the existing paired-pin filters, not independent listing totals. The panel footnote explicitly warns against adding flags to phases.

Under Construction exclusive product counts: Single 55 + Split 49 + Common Driveway 94 + Unknown 27 = 225. The product phase leaves total 198, plus the Unknown row 27 = 225. The two overlapping flags are not added.

Retired 47: Active 21, Pending 4, Terminated 6, Sold 11, unknown-market companion homes 5. The latter retain pre-existing paired-home weights; no identity, market status or construction phase is invented. Every disposition is listed in panel-retired-47-2026-09-10.csv.

All 48 former Finished Sold and 11 unphased Sold members already exist in the sale archive. To keep Finished and Sold Comps disjoint, the old sale of 2932 Michaux (MLS 63496941) is excluded from the comp view while its current Terminated listing remains in Finished. Its sale record is retained unchanged. Normalized-address overlap between Finished and the comp view: zero.

Other remains useful for exceptions: Flagged for review 5, Market status unverified 2 (seven distinct homes). The second row includes the former off-market/unverified member and 616 Ridge, which has only a legacy pending tag, no current market evidence and no construction phase.

## Invocation evidence

`python -B tests/panel_timeline_browser.py --shared pulls/product_classification_20260910/shared_frozen.json --output pulls/panel_timeline_20260910/check-1.json`

Actual Heights output: `homes: 596; uc: 225; ucUnknown: 27; deeds: 139; sold: 791; finishedHeader: 138`. The explicit comp-view assertion is 790. All eight markets pass the base monotonicity test: 8,961 pairs, zero violations. Every runtime phase and home weight matches the before snapshot. DATA substrings are byte-identical across all eight HTML files.

Merrill remains Active with terminated MLS 50361472 in history. Allston remains present. Harvard, 629, Munford, Voight, the two Complete fixtures and the unphased 830 E 26th pass the existing fixture tests. Custom 19, Sold Off Market 1 and deeds 139 remain unchanged.

Three full runs (`check-1.json`, `check-2.json`, `check-3.json`) are byte-identical: 199 checks per run, SHA-256 `5045934d598a87d3cd1b81c4a5412f0c825fd7000e304d01a67f6aece76c0043`.
