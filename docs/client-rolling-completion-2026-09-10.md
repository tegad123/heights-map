# Heights client determinations and rolling completion — 2026-09-10

## Client actions

All seven addresses matched uniquely. 1002 E 6th½ is actually MEP Finals, not Foundation: model September 17 (7 days), client October 1 (21 days). Client completion metadata now records October 1, separately from phase. 1104 Gibbs corrected Single Lot→Split Lot with authoritative client product provenance; remains MEP Finals with September target. 1109 Tabor and 115 Northwood become Custom; 1110 Jerome becomes Needs Clarification and is individually excluded from inventory. 1113 Voight and 1140 Waverly records/tags/phases are untouched. No other properties tagged.

## Counts

| Measure | Before | After |
|---|---:|---:|
| Custom | 19 | 21 |
| Needs Clarification tags (all homes) | 21 | 22 |
| Needs Clarification inventory exclusions | 0 | 1 |
| Under Construction | 178 | 175 |
| Foundation | 9 | 9 |

Supply: 170 − 14 terminated = 156 before; 167 − 14 = 153 after. Map and Overview reconcile. Finished stays 44 Active / 8 Pending / 26 Terminated / 38 No Market Record. Homes 567, pins 521, sold 793, deeds 138 unchanged.

## Target months

The supplied list contains 29 addresses, not 28: 26 remain in inventory and three are excluded. Listed phases in the request were often stale; actual phases are shown below and none changed. September targets are future dates within the current month.

| Address | Actual phase | Target month | Forecast |
|---|---|---|---|
| 1002 E 6TH 1/2 Street | mep_finals | 2026-10 | Verified in month bucket and curve |
| 1013 Woodland St, Houston, TX 77009 | framing | 2027-04 | Verified in month bucket and curve |
| 1040 Louise St, Houston, TX 77009 | foundation | 2027-05 | Verified in month bucket and curve |
| 1104 Gibbs St, Houston, TX 77009 | mep_finals | 2026-09 | Verified in month bucket and curve |
| 1109 Tabor Street | mep_finals | 2026-09 | Excluded: custom |
| 1110 Jerome St, Houston, TX 77009 | mep_roughs | 2027-02 | Excluded: needs_clarification |
| 1113 Voight Street | mep_finals | 2026-09 | Verified in month bucket and curve |
| 1140 Waverly Street | interior | 2026-10 | Verified in month bucket and curve |
| 115 Northwood St, Houston, TX 77009 | mep_finals | 2026-09 | Excluded: custom |
| 1219 Bay Oaks Rd, Houston, Tx 77008 | mep_roughs | 2027-02 | Verified in month bucket and curve |
| 1410 Herkimer St, Houston, TX 77008 | exterior | 2027-03 | Verified in month bucket and curve |
| 1510 Glen Oaks St, Houston, Tx 77008 | insulation | 2027-01 | Verified in month bucket and curve |
| 1910 W 14th 1/2 St, Houston, TX 77008 | mep_finals | 2026-09 | Verified in month bucket and curve |
| 2005 Harvard St, Houston, TX 77008 | framing | 2027-04 | Verified in month bucket and curve |
| 2008 W 14th 1/2 St, Houston, TX 77008 | mep_finals | 2026-09 | Verified in month bucket and curve |
| 2434 White Oak Drive | framing | 2027-04 | Verified in month bucket and curve |
| 248 W 22nd Street | interior | 2026-10 | Verified in month bucket and curve |
| 2603 JULIAN Street | mep_roughs | 2027-02 | Verified in month bucket and curve |
| 602 Northwood St, Houston, TX 77009 | interior | 2026-10 | Verified in month bucket and curve |
| 603 E 23rd Street | interior | 2026-10 | Verified in month bucket and curve |
| 618 Wendel St, Houston, Tx 77009 | insulation | 2027-01 | Verified in month bucket and curve |
| 623 E 13th Street | mep_finals | 2026-09 | Verified in month bucket and curve |
| 625 Oxford St, Houston, TX 77007 | interior | 2026-10 | Verified in month bucket and curve |
| 708 Ralfallen St, Houston, TX 77008 | mep_finals | 2026-09 | Verified in month bucket and curve |
| 710 Le Green St, Houston, TX 77008 | framing | 2027-04 | Verified in month bucket and curve |
| 711 E 12th St, Houston, Tx 77008 | interior | 2026-10 | Verified in month bucket and curve |
| 718 E 7th St, Houston, TX 77007 | interior | 2026-10 | Verified in month bucket and curve |
| 721 Usener St, Houston, TX 77009 | mep_finals | 2026-09 | Verified in month bucket and curve |
| 822 Nashua St, Houston, TX 77008 | exterior | 2027-03 | Verified in month bucket and curve |

## Computation and validation

The seven-day floor and subsequent phase durations remain intact. The timeline now groups homes by target month instead of a separate overdue bucket. No overdue wording appears in any popup or forecast; factual stalled duration remains. A past target advances by calendar months until it is future/current, clamping short-month days. Current model targets are already future, so **zero homes rolled today**. 1002’s change is a client estimate, not a rollover. Completed homes retain historical completion dates; no unfinished forecast sits in the past.

Command: `/Users/nemoclaw/insp-venv/bin/python -B tests/rolling_completion_check.py`. Output: `HEIGHTS PASS ONE CHECK`. All 26 expected month placements checked against expanded timeline DOM and the forecast curve; excluded three absent. 3,103 same-phase time comparisons and 3,225 base-phase comparisons, zero violations. Client dates are explicit overrides, excluded from the model-only elapsed-time comparison.

Rollover invocation examples: September 15 target evaluated October 6 → October 15; evaluated October 27 → November 15. All MEP Finals estimates within 31 days. 310/312 W 9th and 2013 Cortlandt each remain 28 days, October 8. Foundation 9; empty inspection feed still returns null.

DATA is not reserialized: exactly two individually matched objects were surgically replaced (Gibbs product and 1002 client completion metadata); all other DATA bytes are identical. Other markets untouched.
