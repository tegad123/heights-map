# Heights Active market reconciliation — 2026-09-10

Overview now shows two current-evidence member counts: Finished on Market 34 and Under Construction on Market 27. Synthetic twins excluded. Current status/phase derivation and stored tags unchanged. Other markets unchanged.

Legacy 53 = 30 Active + 7 Sold + 5 Terminated + 5 Pending + 1 No Market Record + 5 synthetic twins. Zero are under construction: legacy listedCount explicitly excludes build-phase tags. Four Finished Active members were absent from legacy population, so 53 - 23 + 4 = 34.

The four missing Finished Active members: 112 E 27th Street (unsuffixed listing), 409 Walton B, 1227 Prince, 611 E 25th B. The 112 E 27th A identity review remains unresolved; the unsuffixed listing is counted only as its own tracked member.

## Legacy non-Active members

| Address | Current evidence |
|---|---|
| 709 E 17th St, Houston, Tx 77008 | sold |
| 1520 W 21st St Unit#B | terminated |
| 1324 Lawrence Street | sold |
| 845 West 23rd Street | no_record |
| 231 E 26th Street | terminated |
| 1207 Tabor Street | sold |
| 1315 Waverly Street | pending |
| 111 E 18th Street | pending |
| 1520 Nicholson Street | sold |
| 122 E 4th Street — inferred untracked twin | Synthetic; no member |
| 826 Ralfallen Street | sold |
| 1023 Euclid Street | sold |
| 1116 Highland Street | pending |
| 1126 E 7th 1/2 Street | pending |
| 1208 E 26th Street Unit#A | pending |
| 1122 E 27TH ST Unit#B | sold |
| 833 W 25th Street | terminated |
| 227 E 26th Street | terminated |
| 227 E 26th Street — inferred untracked twin | Synthetic; no member |
| 607 W 27th St, Houston, TX 77008 | terminated |
| 335 Harvard Street — inferred untracked twin | Synthetic; no member |
| 602 Jewett Street Unit#B — inferred untracked twin | Synthetic; no member |
| 741 W 21st Street Unit#A — inferred untracked twin | Synthetic; no member |

## Current Active construction members

| Address | Phase |
|---|---|
| 2011 Singleton St, Houston, Tx 77008 | mep_finals |
| 711 E 26TH Street | interior |
| 1120 E 26th St, Houston, Tx 77009 | interior |
| 410 Merrill St, Houston, Tx 77009 | interior |
| 312 w 9th St | interior |
| 906 Bayland Ave, Houston, TX 77009 | mep_finals |
| 1012 E 26TH Street | insulation |
| 1122 Robbie Street | mep_finals |
| 1109 Tabor Street | mep_finals |
| 920 E 25TH Street | interior |
| 2603 JULIAN Street | mep_roughs |
| 623 E 13th Street | mep_finals |
| 603 E 23rd Street | interior |
| 735 E 8TH 1/2 Street | interior |
| 731 E 8TH 1/2 Street | interior |
| 248 W 22nd Street | interior |
| 2434 White Oak Drive | framing |
| 1140 Waverly Street | interior |
| 2436 White Oak | framing |
| 1002 E 6TH 1/2 Street | mep_finals |
| 1218 Prince Street | exterior |
| 805 W 22nd Street | interior |
| 318 W 21st Street | interior |
| 407 E 27TH Street | mep_finals |
| 1138 Fugate St, Houston, TX 77009 | mep_finals |
| 2924 Watson Street | interior |
| 845 W 23rd St A, Houston, TX 77008 | foundation |

Invocation: `/Users/nemoclaw/insp-venv/bin/python -B /tmp/active_compare.py` returned `TOTALS 53 34 active all 61 UC active 27`. Browser regression: `/Users/nemoclaw/insp-venv/bin/python -B tests/supply_views_check.py` verifies both labels against current member evidence, Finished panel equality, no synthetic members, and construction phase presence. The supply snapshot/Overview exclusion reconciliation remains passing.
