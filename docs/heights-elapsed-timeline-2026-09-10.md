# Heights elapsed-phase timeline correction — 2026-09-10

Remaining days = max(7, phase duration − elapsed) + subsequent phase durations. Overdue remains visible but adds zero days. Phase derivation and all DATA bytes are unchanged.

Market refresh deployed and live-verified at b726ac3. Three identical checks: Finished 44 Active / 8 Pending / 25 Terminated / 38 No Record; 115 total. Homes 567; project pins 521; sold 793; deeds 138.

## Before / after invocation preview

Command: `/Users/nemoclaw/insp-venv/bin/python -B /tmp/heights_elapsed_probe.py`. Frozen September 10, 2026. Snapshot before/after: construction 170, terminated 14, available 156. Three-month construction forecast 66→89; six-month 106→138.

| Address | Market evidence | Phase | Before | After | Days earlier |
|---|---|---|---|---|---:|
| 713 E 26th St, Houston, Tx 77009 | 713 E 26th St, Houston, Tx 77009: no_record; 711 E 26TH Street: active | interior | 2026-10-04 | 2026-10-08 | -4 |
| 618 Wendel St, Houston, Tx 77009 | 618 Wendel St, Houston, Tx 77009: no_record | insulation | 2027-02-21 | 2027-01-30 | 22 |
| 1006 E 28th St, Houston, Tx 77009 | 1006 E 28th St, Houston, Tx 77009: no_record | framing | 2027-05-15 | 2027-04-10 | 35 |
| 711 E 12th St, Houston, Tx 77008 | 711 E 12th St, Houston, Tx 77008: no_record | interior | 2027-04-09 | 2026-10-08 | 183 |
| 820 Waverly St A, Houston, TX 77007 | 820 Waverly St A, Houston, TX 77007: no_record; 820 Waverly St B, Houston, TX 77007: no_record | framing | 2027-05-08 | 2027-04-10 | 28 |
| 310 W 9th St, Houston, TX 77007 | 310 W 9th St, Houston, TX 77007: no_record; 312 w 9th St: active | interior | 2027-04-18 | 2026-10-08 | 192 |
| 410 Columbia St, Houston, TX 77007 | 410 Columbia St, Houston, TX 77007: no_record | mep_finals | 2026-10-10 | 2026-09-17 | 23 |
| 625 Oxford St, Houston, TX 77007 | 625 Oxford St, Houston, TX 77007: no_record | interior | 2027-03-19 | 2026-10-08 | 162 |
| 734 E 7th 1/2 St, Houston, TX 77007 | 734 E 7th 1/2 St, Houston, TX 77007: no_record | exterior | 2027-04-12 | 2027-03-13 | 30 |
| 710 Waverly St A / B / C, Houston, TX 77007 | 710 Waverly St A / B / C, Houston, TX 77007: no_record | foundation | 2027-05-22 | 2027-05-01 | 21 |
| 718 E 7th St, Houston, TX 77007 | 718 E 7th St, Houston, TX 77007: no_record | interior | 2027-04-16 | 2026-10-08 | 190 |
| 915 W 18th St D, Houston, TX 77008 | 915 W 18th St D, Houston, TX 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 915 W 18th St C, Houston, TX 77008 | 915 W 18th St C, Houston, TX 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 915 W 18th St B, Houston, TX 77008 | 915 W 18th St B, Houston, TX 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 915 W 18th St A, Houston, TX 77008 | 915 W 18th St A, Houston, TX 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 915 W 18th St E, Houston, TX 77008 | 915 W 18th St E, Houston, TX 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 915 W 18th St F, Houston, TX 77008 | 915 W 18th St F, Houston, TX 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 2013 Cortlandt St, Houston, TX 77008 | 2013 Cortlandt St, Houston, TX 77008: no_record | interior | 2027-03-24 | 2026-10-08 | 167 |
| 1410 Herkimer St, Houston, TX 77008 | 1410 Herkimer St, Houston, TX 77008: no_record | exterior | 2027-04-16 | 2027-03-13 | 34 |
| 2464 Nicholson St, Houston, TX 77008 | 2464 Nicholson St, Houston, TX 77008: no_record | exterior | 2027-04-13 | 2027-03-13 | 31 |
| 2462 Nicholson St, Houston, TX 77008 | 2462 Nicholson St, Houston, TX 77008: no_record | exterior | 2027-04-13 | 2027-03-13 | 31 |
| 2450 Nicholson St, Houston, TX 77008 | 2450 Nicholson St, Houston, TX 77008: no_record | exterior | 2027-04-17 | 2027-03-13 | 35 |
| 2452 Nicholson St, Houston, TX 77008 | 2452 Nicholson St, Houston, TX 77008: no_record | exterior | 2027-04-17 | 2027-03-13 | 35 |
| 1320 Alexander St A, Houston, TX 77008 | 1320 Alexander St A, Houston, TX 77008: no_record; 1320 Alexander St B, Houston, TX 77008: active | mep_finals | 2026-09-15 | 2026-09-17 | -2 |
| 705 E 13th St, Houston, TX 77008 | 705 E 13th St, Houston, TX 77008: no_record | foundation | 2027-05-22 | 2027-05-01 | 21 |
| 727 W 21st St, Houston, TX 77008 | 727 W 21st St, Houston, TX 77008: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 745 E 16th St, Houston, TX 77008 | 745 E 16th St, Houston, TX 77008: no_record | foundation | 2027-05-22 | 2027-05-01 | 21 |
| 1595 W 25th St, Houston, TX 77008 | 1595 W 25th St, Houston, TX 77008: no_record | mep_roughs | 2027-03-20 | 2027-02-20 | 28 |
| 1597 W 25th St, Houston, TX 77008 | 1597 W 25th St, Houston, TX 77008: terminated | interior | 2027-02-06 | 2026-10-08 | 121 |
| 1599 W 25th St, Houston, TX 77008 | 1599 W 25th St, Houston, TX 77008: terminated | interior | 2027-02-06 | 2026-10-08 | 121 |
| 1601 W 25th St, Houston, TX 77008 | 1601 W 25th St, Houston, TX 77008: active | interior | 2027-02-05 | 2026-10-08 | 120 |
| 1603 W 25th St, Houston, TX 77008 | 1603 W 25th St, Houston, TX 77008: terminated | interior | 2027-02-05 | 2026-10-08 | 120 |
| 1220 Prince St, Houston, TX 77008 | 1220 Prince St, Houston, TX 77008: no_record | foundation | 2027-05-22 | 2027-05-01 | 21 |
| 2005 Harvard St, Houston, TX 77008 | 2005 Harvard St, Houston, TX 77008: no_record | framing | 2027-05-15 | 2027-04-10 | 35 |
| 1132 E 6th 1/2 St, Houston, TX 77009 | 1132 E 6th 1/2 St, Houston, TX 77009: no_record | foundation | 2027-05-22 | 2027-05-01 | 21 |
| 523 Link Rd, Houston, TX 77009 | 523 Link Rd, Houston, TX 77009: no_record | exterior | 2027-04-20 | 2027-03-13 | 38 |
| 519 Link Rd, Houston, TX 77009 | 519 Link Rd, Houston, TX 77009: no_record | exterior | 2027-04-24 | 2027-03-13 | 42 |
| 1910 Northwood St, Houston, TX 77009 | 1910 Northwood St, Houston, TX 77009: no_record | exterior | 2027-04-16 | 2027-03-13 | 34 |
| 1914 Northwood St, Houston, TX 77009 | 1914 Northwood St, Houston, TX 77009: no_record | exterior | 2027-04-23 | 2027-03-13 | 41 |
| 1918 Northwood St, Houston, TX 77009 | 1918 Northwood St, Houston, TX 77009: no_record | exterior | 2027-04-24 | 2027-03-13 | 42 |
| 1104 Gibbs St, Houston, TX 77009 | 1104 Gibbs St, Houston, TX 77009: pending | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 602 Northwood St, Houston, TX 77009 | 602 Northwood St, Houston, TX 77009: no_record | interior | 2027-02-27 | 2026-10-08 | 142 |
| 932 Algregg St, Houston, TX 77009 | 932 Algregg St, Houston, TX 77009: no_record; 934 Algregg St, Houston, TX 77009: no_record | mep_roughs | 2027-02-13 | 2027-02-20 | -7 |
| 1109 Tabor Street | 1109 Tabor Street: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 2603 JULIAN Street | 2603 JULIAN Street: active | mep_roughs | 2027-03-12 | 2027-02-20 | 20 |
| 623 E 13th Street | 623 E 13th Street: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 603 E 23rd Street | 603 E 23rd Street: active | interior | 2027-04-29 | 2026-10-08 | 203 |
| 248 W 22nd Street | 248 W 22nd Street: active | interior | 2027-01-28 | 2026-10-08 | 112 |
| 2434 White Oak Drive | 2434 White Oak Drive: active | framing | 2027-05-15 | 2027-04-10 | 35 |
| 1113 Voight Street | 1113 Voight Street: pending | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1140 Waverly Street | 1140 Waverly Street: active | interior | 2027-05-13 | 2026-10-08 | 217 |
| 1002 E 6TH 1/2 Street | 1002 E 6TH 1/2 Street: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 827 W 16th Street Unit#A | 827 W 16th Street Unit#A: pending | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 407 E 27TH Street | 407 E 27TH Street: active; 409 E 27th St, Houston, TX 77008: no_record | mep_finals | 2026-09-11 | 2026-09-17 | -6 |
| 1922 Northwood St, Houston, TX 77009 | 1922 Northwood St, Houston, TX 77009: no_record | exterior | 2027-04-20 | 2027-03-13 | 38 |
| 1926 Northwood St, Houston, TX 77009 | 1926 Northwood St, Houston, TX 77009: no_record | exterior | 2027-04-24 | 2027-03-13 | 42 |
| 1219 Bay Oaks Rd, Houston, Tx 77008 | 1219 Bay Oaks Rd, Houston, Tx 77008: no_record | mep_roughs | 2027-03-08 | 2027-02-20 | 16 |
| 1510 Glen Oaks St, Houston, Tx 77008 | 1510 Glen Oaks St, Houston, Tx 77008: no_record | insulation | 2027-03-06 | 2027-01-30 | 35 |
| 822 Nashua St, Houston, TX 77008 | 822 Nashua St, Houston, TX 77008: no_record | exterior | 2027-04-25 | 2027-03-13 | 43 |
| 1013 Woodland St, Houston, TX 77009 | 1013 Woodland St, Houston, TX 77009: no_record | framing | 2027-05-15 | 2027-04-10 | 35 |
| 625 Merrill St, Houston, TX 77009 | 625 Merrill St, Houston, TX 77009: no_record | framing | 2027-05-10 | 2027-04-10 | 30 |
| 1040 Louise St, Houston, TX 77009 | 1040 Louise St, Houston, TX 77009: no_record | foundation | 2027-05-18 | 2027-05-01 | 17 |
| 835 Lawrence St, Houston, TX 77007 | 835 Lawrence St, Houston, TX 77007: no_record | foundation | 2027-05-17 | 2027-05-01 | 16 |
| 806 Peddie St, Houston, TX 77008 | 806 Peddie St, Houston, TX 77008: no_record | foundation | 2027-05-11 | 2027-05-01 | 10 |
| 710 Le Green St, Houston, TX 77008 | 710 Le Green St, Houston, TX 77008: no_record | framing | 2027-04-27 | 2027-04-10 | 17 |
| 845 W 23rd St A, Houston, TX 77008 | 845 W 23rd St A, Houston, TX 77008: active; 845 W 23rd St B, Houston, TX 77008: no_record | foundation | 2027-04-28 | 2027-05-01 | -3 |
| 214 Sylvester Rd, Houston, TX 77009 | 214 Sylvester Rd, Houston, TX 77009: no_record | foundation | 2027-04-28 | 2027-05-01 | -3 |
| 717 E 5th 1/2 St, Houston, TX 77007 | 717 E 5th 1/2 St, Houston, TX 77007: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 2008 W 14th 1/2 St, Houston, TX 77008 | 2008 W 14th 1/2 St, Houston, TX 77008: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1443 W 25th St H, Houston, TX 77008 | 1443 W 25th St H, Houston, TX 77008: no_record | mep_finals | 2026-10-07 | 2026-09-17 | 20 |
| 1443 W 25th St A, Houston, TX 77008 | 1443 W 25th St A, Houston, TX 77008: no_record | mep_finals | 2026-10-15 | 2026-09-17 | 28 |
| 1910 W 14th 1/2 St, Houston, TX 77008 | 1910 W 14th 1/2 St, Houston, TX 77008: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1034 W 17th St D, Houston, TX 77008 | 1034 W 17th St D, Houston, TX 77008: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1034 W 17th St C, Houston, TX 77008 | 1034 W 17th St C, Houston, TX 77008: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1034 W 17th St E, Houston, TX 77008 | 1034 W 17th St E, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1034 W 17th St B, Houston, TX 77008 | 1034 W 17th St B, Houston, TX 77008: terminated | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1034 W 17th St A, Houston, TX 77008 | 1034 W 17th St A, Houston, TX 77008: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1438 Dian St A, Houston, TX 77008 | 1438 Dian St A, Houston, TX 77008: sold; 1438 Dian St B, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1239 Waverly St, Houston, TX 77008 | 1239 Waverly St, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 310 E 28th St, Houston, TX 77008 | 310 E 28th St, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1507 W 23rd St E, Houston, TX 77008 | 1507 W 23rd St E, Houston, TX 77008: no_record | interior | 2027-03-27 | 2026-10-08 | 170 |
| 1507 W 23rd St D, Houston, TX 77008 | 1507 W 23rd St D, Houston, TX 77008: no_record | interior | 2027-03-27 | 2026-10-08 | 170 |
| 1507 W 23rd St C, Houston, TX 77008 | 1507 W 23rd St C, Houston, TX 77008: no_record | interior | 2027-03-27 | 2026-10-08 | 170 |
| 1507 W 23rd St B, Houston, TX 77008 | 1507 W 23rd St B, Houston, TX 77008: no_record | interior | 2027-03-27 | 2026-10-08 | 170 |
| 1507 W 23rd St A, Houston, TX 77008 | 1507 W 23rd St A, Houston, TX 77008: active | interior | 2027-03-27 | 2026-10-08 | 170 |
| 827 W 16th St B, Houston, TX 77008 | 827 W 16th St B, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1424 W 23rd St C, Houston, TX 77008 | 1424 W 23rd St C, Houston, TX 77008: terminated | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1021 Ashland St, Houston, TX 77008 | 1021 Ashland St, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 708 Ralfallen St, Houston, TX 77008 | 708 Ralfallen St, Houston, TX 77008: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 326 W 27th St, Houston, TX 77008 | 326 W 27th St, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 324 W 27th St, Houston, TX 77008 | 324 W 27th St, Houston, TX 77008: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1424 W 23rd St A, Houston, TX 77008 | 1424 W 23rd St A, Houston, TX 77008: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1807 Palmetto Landing Dr, Houston, TX 77009 | 1807 Palmetto Landing Dr, Houston, TX 77009: terminated; 1809 Palmetto Landing Dr, Houston, TX 77009: terminated | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 721 Usener St, Houston, TX 77009 | 721 Usener St, Houston, TX 77009: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1106 Robbie St, Houston, TX 77009 | 1106 Robbie St, Houston, TX 77009: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 115 Northwood St, Houston, TX 77009 | 115 Northwood St, Houston, TX 77009: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 2922 Michaux St, Houston, TX 77009 | 2922 Michaux St, Houston, TX 77009: terminated | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 2924 Michaux St, Houston, TX 77009 | 2924 Michaux St, Houston, TX 77009: terminated | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 2920 Michaux St, Houston, TX 77009 | 2920 Michaux St, Houston, TX 77009: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1110 Jerome St, Houston, TX 77009 | 1110 Jerome St, Houston, TX 77009: no_record | mep_roughs | 2027-03-27 | 2027-02-20 | 35 |
| 827 E 25th St, Houston, TX 77009 | 827 E 25th St, Houston, TX 77009: no_record | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1042 Voight St, Houston, TX 77009 | 1042 Voight St, Houston, TX 77009: sold | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 1016 E 27th St, Houston, TX 77009 | 1016 E 27th St, Houston, TX 77009: no_record | interior | 2027-05-17 | 2026-10-08 | 221 |
| 606 Skyland Terrace Way, Houston, TX 77009 | 606 Skyland Terrace Way, Houston, TX 77009: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 602 Skyland Terrace Way, Houston, TX 77009 | 602 Skyland Terrace Way, Houston, TX 77009: terminated | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 603 Skyland Terrace Way, Houston, TX 77009 | 603 Skyland Terrace Way, Houston, TX 77009: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |
| 615 Skyland Terrace Way, Houston, TX 77009 | 615 Skyland Terrace Way, Houston, TX 77009: no_record | interior | 2027-05-17 | 2026-10-08 | 221 |
| 611 Skyland Terrace Way, Houston, TX 77009 | 611 Skyland Terrace Way, Houston, TX 77009: no_record | interior | 2027-05-17 | 2026-10-08 | 221 |
| 607 Skyland Terrace Way, Houston, TX 77009 | 607 Skyland Terrace Way, Houston, TX 77009: active | mep_finals | 2026-10-22 | 2026-09-17 | 35 |

## Applied validation

`/Users/nemoclaw/insp-venv/bin/python -B tests/unfiltered_market_check.py --once` returned `PREVIEW PASS ONE HEIGHTS CHECK`; phase monotonicity: 3,257 pairs, zero violations. All Heights construction and market fixtures passed.

Node invoked the actual `phaseTimeline` extracted from index.html against the refreshed Heights runtime anchors: `{"samePhaseEarlierEntryPairs":3152,"violations":0}`. The browser also checked 5,117 elapsed-day samples (0–730 days in each of seven phases), zero violations.

September 10 fixture output: 310/312 W 9th elapsed 199 days, overdue 85; 2013 Cortlandt elapsed 174, overdue 60. Both return remainingDays 28 and target 2026-10-08.
