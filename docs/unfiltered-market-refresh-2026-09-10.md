# Unfiltered HAR refresh — 2026-09-10

Approved policy: add only three tracked-property sales; all unmatched sales remain evidence without new comp pins.

## Verified profile

1,338 rows, 26 columns, 1,338 unique MLS numbers. Active 105, Sold 346, Withdrawn 8, Expired 104, Terminated 765, Terminated-Relisted 10. 380 sub-2,000-sf rows; zero overlap across available prior MLS-bearing HAR CSVs. 108 missing lot sizes classify Unknown (61 Terminated, 20 Sold, 18 Expired, 9 Active). Sold date range 2024-02-27 through 2026-09-09; years 89 / 163 / 94 for 2024 / 2025 / 2026.

## Ingest results

836 new + 490 updated + 0 held + 12 OOZ_REGEX ledgered = 1,338. Second run: 1,326 held + 12 ledgered, zero changed files, byte-identical HTML/snapshot/ledger. 640 existing resale records preserved. Incoming source-row/provenance updates count as updates.

## Prior-only MLS records

All 19 retained. The 13 Pending rows are absent from an export containing no Pending status at all: consistent with omitted status scope, not evidence of cancellation/sale. Other listing IDs at the same address do not establish a transition of the missing MLS. The six 335 Harvard/122 E 4th rows have no new address match; exact omission cause cannot be determined from these exports. Do not invent a removal reason.

| MLS | Address | Prior status | Disposition |
|---|---|---|---|
| 65070979 | 335 Harvard Street | Active | Retain prior evidence/history; omission unexplained |
| 90552057 | 122 E 4th Street | Active | Retain prior evidence/history; omission unexplained |
| 58591599 | 1208 E 26th Street Unit#A | Pending | Retain Pending; absent-status scope |
| 11989383 | 1104 Gibbs Street | Pending | Retain Pending; absent-status scope |
| 44304073 | 807 W 22nd Street | Pending | Retain Pending; absent-status scope |
| 61282363 | 1434 Alexander Street | Pending | Retain Pending; absent-status scope |
| 81354398 | 816 W 17TH Street | Pending | Retain Pending; absent-status scope |
| 62144090 | 814 W 17TH Street | Pending | Retain Pending; absent-status scope |
| 89555500 | 827 W 16th Street Unit#A | Pending | Retain Pending; absent-status scope |
| 32141788 | 314 W 21st Street | Pending | Retain Pending; absent-status scope |
| 81689864 | 116 E 23RD Street | Pending | Retain Pending; absent-status scope |
| 62006938 | 1315 Waverly Street | Pending | Retain Pending; absent-status scope |
| 74950038 | 111 E 18th Street | Pending | Retain Pending; absent-status scope |
| 40388055 | 1113 Voight Street | Pending | Retain Pending; absent-status scope |
| 95336494 | 1126 E 7th 1/2 Street | Pending | Retain Pending; absent-status scope |
| 44460494 | 335 Harvard Street | Terminated | Retain prior evidence/history; omission unexplained |
| 38558168 | 335 Harvard Street | Terminated | Retain prior evidence/history; omission unexplained |
| 51069776 | 122 E 4th Street | Terminated | Retain prior evidence/history; omission unexplained |
| 37477045 | 122 E 4th Street | Terminated | Retain prior evidence/history; omission unexplained |

## Resolution headline

19 of 57 resolve. 11 of 22 Common Driveway resolve: 9 sub-2,000 rows and 2 rows missing lot size. Filter hypothesis strongly supported. Sub-2,000 resolutions across all products: 12; missing-lot resolutions: 3; remaining four have lot sizes >=2,000 and cannot be attributed to that filter.

| Product | Before | Active | Terminated | Sold | Remaining | Sub-2,000 resolutions |
|---|---:|---:|---:|---:|---:|---:|
| Common Driveway | 22 | 5 | 5 | 1 | 11 | 9 |
| Split Lot | 12 | 3 | 1 | 0 | 8 | 2 |
| Single Lot | 9 | 0 | 0 | 1 | 8 | 0 |
| Unknown | 14 | 1 | 2 | 0 | 11 | 1 |

Measured product baseline differs from prompt: 22 Common Driveway / 12 Split / 9 Single / 14 Unknown, total 57.

| Address | Product | Result | MLS | CSV row | Lot sf |
|---|---|---|---|---:|---:|
| 118 E 23rd St, Houston, Tx 77008 | Split Lot | active | 5930421 | 67 | 3500.0 |
| 737 W 21st St C, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 737 W 21st St B, Houston, TX 77008 | Common Driveway | active | 31329647 | 19 | 1638.0 |
| 737 W 21st St A, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 737 W 21st St D, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 729 W 21st St A, Houston, TX 77008 | Common Driveway | active | 31414914 | 38 | 1556.0 |
| 723 W 21st St, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 725 W 21st St, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 729 W 21st St B, Houston, TX 77008 | Common Driveway | terminated | 97207025 | 924 | 1556.0 |
| 1432 Alexander St, Houston, TX 77008 | Split Lot | no_record | — | — | missing / no match |
| 112 E 27th Street | Split Lot | no_record | — | — | missing / no match |
| 729 W 21st St C, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 2811 Ave, Houston, TX 77009 | Single Lot | no_record | — | — | missing / no match |
| 1301 Tabor St, Houston, TX 77009 | Single Lot | no_record | — | — | missing / no match |
| 1107 E 24th St, Houston, TX 77009 | Split Lot | active | 70991955 | 43 | 1627.0 |
| 1109 E 24th St, Houston, TX 77009 | Split Lot | active | 11824678 | 44 | 1627.0 |
| 409 Walton St A, Houston, TX 77009 | Split Lot | no_record | — | — | missing / no match |
| 931 Merrill St, Houston, TX 77009 | Single Lot | sold | 16650968 | 443 | missing / no match |
| 706 E 7th St, Houston, TX 77007 | Unknown | terminated | 36132509 | 1322 | 9375.0 |
| 818 Lawrence St, Houston, TX 77007 | Unknown | no_record | — | — | missing / no match |
| 702 E 8th St, Houston, TX 77007 | Single Lot | no_record | — | — | missing / no match |
| 4133 Kolb St A, Houston, TX 77007 | Common Driveway | no_record | — | — | missing / no match |
| 4133 Kolb St B, Houston, TX 77007 | Common Driveway | no_record | — | — | missing / no match |
| 1023 Grovewood Ln, Houston, TX 77008 | Unknown | terminated | 80549945 | 1225 | 7200.0 |
| 910 W 24th St, Houston, TX 77008 | Common Driveway | no_record | — | — | missing / no match |
| 1115 Nashua St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 302 W 23rd St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 213 E 23rd St, Houston, TX 77008 | Single Lot | no_record | — | — | missing / no match |
| 1011 Worthshire St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 809 W 18th St, Houston, TX 77008 | Split Lot | no_record | — | — | missing / no match |
| 1424 W 23rd St B, Houston, TX 77008 | Common Driveway | active | 48429544 | 7 | 1742.0 |
| 1237 Waverly St, Houston, TX 77008 | Split Lot | no_record | — | — | missing / no match |
| 226 E 27th St, Houston, TX 77008 | Split Lot | no_record | — | — | missing / no match |
| 1405 W 21st St C, Houston, TX 77008 | Common Driveway | terminated | 23099716 | 814 | 1925.0 |
| 1405 W 21st St B, Houston, TX 77008 | Common Driveway | sold | 31950581 | 166 | 1589.0 |
| 1405 W 21st St A, Houston, TX 77008 | Common Driveway | terminated | 9963614 | 788 | 1589.0 |
| 1403 W 21st St D, Houston, TX 77008 | Common Driveway | terminated | 92944075 | 725 | 1589.0 |
| 1403 W 21st St C, Houston, TX 77008 | Common Driveway | terminated | 94909002 | 762 | 1589.0 |
| 319 E 24th St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 1519 Glen Oaks St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 1006 Nashua St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 710 E 12th St, Houston, TX 77008 | Single Lot | no_record | — | — | missing / no match |
| 730 E 13th 1/2 St, Houston, TX 77008 | Unknown | no_record | — | — | missing / no match |
| 832 W 19th St, Houston, TX 77008 | Split Lot | terminated | 20884835 | 1013 | 3275.0 |
| 1207 Tulane St, Houston, TX 77008 | Split Lot | no_record | — | — | missing / no match |
| 1312 E 28th St A, Houston, TX 77009 | Unknown | no_record | — | — | missing / no match |
| 1115 E 26th St, Houston, TX 77009 | Split Lot | no_record | — | — | missing / no match |
| 605 Cordell St, Houston, TX 77009 | Single Lot | no_record | — | — | missing / no match |
| 121 Northwood St, Houston, TX 77009 | Single Lot | no_record | — | — | missing / no match |
| 1805 Palmetto Landing Dr, Houston, TX 77009 | Unknown | active | 73440928 | 5 | 1943.0 |
| 2928 Michaux St, Houston, TX 77009 | Common Driveway | active | 11138011 | 60 | missing / no match |
| 2926 Michaux St, Houston, TX 77009 | Common Driveway | active | 46686786 | 61 | missing / no match |
| 2701 Julian St, Houston, TX 77009 | Unknown | no_record | — | — | missing / no match |
| 1040 Voight St, Houston, TX 77009 | Unknown | no_record | — | — | missing / no match |
| 1127 Robbie St, Houston, TX 77009 | Single Lot | no_record | — | — | missing / no match |
| 610 Skyland Terrace Way, Houston, TX 77009 | Common Driveway | no_record | — | — | missing / no match |
| 614 Skyland Terrace Way, Houston, TX 77009 | Common Driveway | no_record | — | — | missing / no match |

Every remaining no_record row above lacks safely matched unit-specific current listing/sale evidence in the supplied exports. 112 E 27th unsuffixed companion is deliberately unknown after client MLS assignment to A; sibling evidence is not transferred. 2811 Ave has an incomplete stored street identity and needs address verification. No fuzzy assignment made.

## Other cohorts

24 Under Construction members gain evidence: 11 Active, 13 Terminated. Old retired 47: 42 real members still matched, statuses unchanged; 5 historical synthetic companions have no member identity and stay excluded from Finished status buckets.

## Approved tracked-only sold policy

Unrestricted additions: 177 sales, 88 from 2024, 174 unmatched to tracked members. Approved: 3 tracked sales only. 174 excluded from new comp pins but retained as market evidence, with separate policy ledger. No new listing pins; 661 eligible unmatched non-sold listing rows retained as evidence only.

| Three approved additions | MLS | Closed |
|---|---|---|
| 1405 W 21st St Unit#B | 31950581 | 2026-09-01 |
| 1116 Highland Street | 42468659 | 2026-09-09 |
| 931 Merrill | 16650968 | 2026-02-20 |

## Totals

| Metric | Before | After |
|---|---:|---:|
| DATA project pins | 521 | 521 |
| DATA represented homes | 567 | 567 |
| Sold archive | 790 | 793 |
| Sold panel | 789 | 793 |
| Deeds | 138 | 138 |
| Custom | 19 | 19 |
| Sold Off Market | 1 | 1 |
| Finished Active | 34 | 44 |
| Finished Pending | 9 | 8 |
| Finished Terminated | 19 | 25 |
| Finished No Market Record | 57 | 38 |
| Finished total | 119 | 115 |

Deeds 139 in prompt predates the authorized I-10 cleanup; actual protected baseline is 138. No DATA reserialization; geometry products unchanged. Snapshot/Overview reconcile at 156 after new termination evidence (170 construction forecast minus 14 terminated), versus prior168 (170 minus2).

## All market status movements

| Address | Phase | Before | After | MLS | CSV row |
|---|---|---|---|---|---:|
| 118 E 23rd St, Houston, Tx 77008 | complete | no_record | active | 5930421 | 67 |
| 737 W 21st St B, Houston, TX 77008 | complete | no_record | active | 31329647 | 19 |
| 729 W 21st St A, Houston, TX 77008 | complete | no_record | active | 31414914 | 38 |
| 729 W 21st St B, Houston, TX 77008 | complete | no_record | terminated | 97207025 | 924 |
| 1320 Alexander St B, Houston, TX 77008 | mep_finals | no_record | active | 63577062 | 55 |
| 727 W 21st St, Houston, TX 77008 | mep_finals | no_record | active | 47935112 | 45 |
| 1597 W 25th St, Houston, TX 77008 | interior | no_record | terminated | 83975105 | 850 |
| 1599 W 25th St, Houston, TX 77008 | interior | no_record | terminated | 91778818 | 884 |
| 1601 W 25th St, Houston, TX 77008 | interior | no_record | active | 66726875 | 37 |
| 1603 W 25th St, Houston, TX 77008 | interior | no_record | terminated | 24034535 | 846 |
| 1107 E 24th St, Houston, TX 77009 | complete | no_record | active | 70991955 | 43 |
| 1109 E 24th St, Houston, TX 77009 | complete | no_record | active | 11824678 | 44 |
| 931 Merrill St, Houston, TX 77009 | complete | no_record | sold | 16650968 | 443 |
| 1116 Highland Street | complete | pending | sold | 42468659 | 429 |
| 832 E 27th St, Houston, TX 77009 | framing | no_record | terminated | 98707840 | 1015 |
| 706 E 7th St, Houston, TX 77007 | complete | no_record | terminated | 36132509 | 1322 |
| 1023 Grovewood Ln, Houston, TX 77008 | complete | no_record | terminated | 80549945 | 1225 |
| 1122 W 17th St C, Houston, TX 77008 | interior | no_record | terminated | 86945968 | 487 |
| 1034 W 17th St D, Houston, TX 77008 | mep_finals | no_record | active | 44098392 | 28 |
| 1034 W 17th St B, Houston, TX 77008 | mep_finals | no_record | terminated | 92908425 | 493 |
| 1034 W 17th St A, Houston, TX 77008 | mep_finals | no_record | active | 97764445 | 29 |
| 1507 W 23rd St A, Houston, TX 77008 | interior | no_record | active | 96923068 | 33 |
| 1424 W 23rd St C, Houston, TX 77008 | mep_finals | no_record | terminated | 41409523 | 1333 |
| 1424 W 23rd St B, Houston, TX 77008 | complete | no_record | active | 48429544 | 7 |
| 1405 W 21st St C, Houston, TX 77008 | complete | no_record | terminated | 23099716 | 814 |
| 1405 W 21st St B, Houston, TX 77008 | complete | no_record | sold | 31950581 | 166 |
| 1405 W 21st St A, Houston, TX 77008 | complete | no_record | terminated | 9963614 | 788 |
| 1403 W 21st St D, Houston, TX 77008 | complete | no_record | terminated | 92944075 | 725 |
| 1403 W 21st St C, Houston, TX 77008 | complete | no_record | terminated | 94909002 | 762 |
| 832 W 19th St, Houston, TX 77008 | complete | no_record | terminated | 20884835 | 1013 |
| 1424 W 23rd St A, Houston, TX 77008 | mep_finals | no_record | active | 82102101 | 20 |
| 305 W 17th St, Houston, TX 77008 | foundation | no_record | terminated | 56122144 | 1280 |
| 1807 Palmetto Landing Dr, Houston, TX 77009 | mep_finals | no_record | terminated | 7891780 | 454 |
| 1809 Palmetto Landing Dr, Houston, TX 77009 | mep_finals | no_record | terminated | 44578196 | 490 |
| 1805 Palmetto Landing Dr, Houston, TX 77009 | complete | no_record | active | 73440928 | 5 |
| 2922 Michaux St, Houston, TX 77009 | mep_finals | no_record | terminated | 22976765 | 1069 |
| 2932 Michaux St, Houston, TX 77009 | complete | terminated | sold | 63496941 | 328 |
| 2928 Michaux St, Houston, TX 77009 | complete | no_record | active | 11138011 | 60 |
| 2926 Michaux St, Houston, TX 77009 | complete | no_record | active | 46686786 | 61 |
| 2924 Michaux St, Houston, TX 77009 | mep_finals | no_record | terminated | 41400328 | 1070 |
| 2920 Michaux St, Houston, TX 77009 | mep_finals | no_record | active | 62384568 | 62 |
| 2918 Michaux St, Houston, TX 77009 | complete | terminated | active | 33656109 | 59 |
| 606 Skyland Terrace Way, Houston, TX 77009 | mep_finals | no_record | active | 45048456 | 11 |
| 602 Skyland Terrace Way, Houston, TX 77009 | mep_finals | no_record | terminated | 13177633 | 707 |
| 603 Skyland Terrace Way, Houston, TX 77009 | mep_finals | no_record | active | 80759930 | 10 |
| 607 Skyland Terrace Way, Houston, TX 77009 | mep_finals | no_record | active | 39931380 | 9 |

## Commands and actual validation

`combined_market_ingest.py --input Everythingsince2023.csv --runtime pulls/unfiltered_20260910/runtime.json --sale-policy tracked --output pulls/unfiltered_20260910/preview` returned 836 new, 490 updated, 12 ledgered, sold790→793.

`/Users/nemoclaw/insp-venv/bin/python -B /tmp/unfiltered_preview.py`: PASS STAGED IDEMPOTENCE zero changes; all output bytes identical.

`/Users/nemoclaw/insp-venv/bin/python -B tests/unfiltered_market_check.py`: PREVIEW PASS THREE IDENTICAL CHECKS; monotonicity3,257pairs, violations[]. Construction fixtures passed; 715 Merrill Active with terminated50361472; 112 E27 A Active34333707; 742Allston present; geometry display protection passes.

Open: exact cause of the two missing-address clusters and 38 unresolved homes. Live verification is recorded after deployment.

All nine newly Active former No Market Record members were individually checked in finishedRows(). Active totals rise by ten because 2918 Michaux additionally changes Terminated→Active. Pending falls by one (1116 Highland→Sold); Terminated gains eight former unknowns and loses 2918/2932 Michaux to Active/Sold respectively. Four Finished homes move to Sold overall.
