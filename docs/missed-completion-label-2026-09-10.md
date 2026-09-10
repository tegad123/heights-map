# Heights missed-target label — 2026-09-10

Display-only Overdue label on popup and timeline cards, plus Layers → Other → Overdue — missed target. Completion lines retain plain future month text; no arithmetic or stored tags changed.

The label measures calendar months past the **original target month**, not historical logged roll events. Original target is client completion target when supplied; otherwise phase anchor plus standard remaining phase durations. It applies only after that month has passed and the current target month is later. Completed homes and records represented solely as Sold Comps are excluded. The current-month target is not labeled merely because its day has passed.

**51 homes / 45 pins:** MEP Finals 29, INT.CAB 18, Foundation 3, MEP Roughs 1. Includes 1109 Tabor and 115 Northwood (Custom), and 1110 Jerome (Needs Clarification): all three remain excluded from inventory. 48 labeled homes remain eligible for inventory.

The preliminary 63-home calculation included 12 homes / 11 pins already routed exclusively to Sold Comps. The actual filter check caught that mismatch; the final predicate excludes them without modifying market-status logic.

## Verification

`/Users/nemoclaw/insp-venv/bin/python -B tests/missed_completion_label_check.py` completed with:

```text
FILTER 51 51 missing set() extra set()
HEIGHTS PASS ONE CHECK: all ETA results, phase tags, products, counts and supply byte-identical
SUPPLY {'construction': 167, 'terminated': 14, 'available': 153}
```

The check clicks the actual Layers control, compares every marker ID with the derived label set, expands timeline cards, and verifies popup labels. Completion lines contain no Overdue text. Source and runtime comparisons prove phaseTimeline, rollingCompletionTarget, inspectionEta, every ETA result, all DATA bytes and inventory totals unchanged. Boundary cases cover current-month/future targets, completed homes, missing evidence, and client-target precedence. Earlier failed checks identified the sold-only filter mismatch and a synthetic-case fixture edge; one completed full check passed after correction.

## Labeled homes

| Address | Phase | Original month | Months past | Current target | Category |
|---|---|---|---:|---|---|
| 711 E 12th St, Houston, Tx 77008 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 310 W 9th St, Houston, TX 77007 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 625 Oxford St, Houston, TX 77007 | interior | 2026-08 | 1 | 2026-10-08 | Inventory |
| 710 Waverly St A / B / C, Houston, TX 77007 | foundation | 2026-04 | 5 | 2027-05-01 | Inventory |
| 718 E 7th St, Houston, TX 77007 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 2013 Cortlandt St, Houston, TX 77008 | interior | 2026-08 | 1 | 2026-10-08 | Inventory |
| 727 W 21st St, Houston, TX 77008 | mep_finals | 2026-04 | 5 | 2026-09-17 | Inventory |
| 1104 Gibbs St, Houston, TX 77009 | mep_finals | 2026-08 | 1 | 2026-09-17 | Inventory |
| 602 Northwood St, Houston, TX 77009 | interior | 2026-08 | 1 | 2026-10-08 | Inventory |
| 1109 Tabor Street | mep_finals | 2026-06 | 3 | 2026-09-17 | custom |
| 623 E 13th Street | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 603 E 23rd Street | interior | 2026-06 | 3 | 2026-10-08 | Inventory |
| 1113 Voight Street | mep_finals | 2026-06 | 3 | 2026-09-17 | Inventory |
| 1140 Waverly Street | interior | 2026-06 | 3 | 2026-10-08 | Inventory |
| 827 W 16th Street Unit#A | mep_finals | 2025-08 | 13 | 2026-09-17 | Inventory |
| 2008 W 14th 1/2 St, Houston, TX 77008 | mep_finals | 2025-10 | 11 | 2026-09-17 | Inventory |
| 1443 W 25th St A, Houston, TX 77008 | mep_finals | 2026-08 | 1 | 2026-09-17 | Inventory |
| 1910 W 14th 1/2 St, Houston, TX 77008 | mep_finals | 2025-08 | 13 | 2026-09-17 | Inventory |
| 1034 W 17th St D, Houston, TX 77008 | mep_finals | 2026-06 | 3 | 2026-09-17 | Inventory |
| 1034 W 17th St C, Houston, TX 77008 | mep_finals | 2026-06 | 3 | 2026-09-17 | Inventory |
| 1034 W 17th St B, Houston, TX 77008 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 1034 W 17th St A, Houston, TX 77008 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 1507 W 23rd St E, Houston, TX 77008 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 1507 W 23rd St D, Houston, TX 77008 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 1507 W 23rd St C, Houston, TX 77008 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 1507 W 23rd St B, Houston, TX 77008 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 1507 W 23rd St A, Houston, TX 77008 | interior | 2026-07 | 2 | 2026-10-08 | Inventory |
| 1424 W 23rd St C, Houston, TX 77008 | mep_finals | 2026-06 | 3 | 2026-09-17 | Inventory |
| 708 Ralfallen St, Houston, TX 77008 | mep_finals | 2025-10 | 11 | 2026-09-17 | Inventory |
| 1424 W 23rd St A, Houston, TX 77008 | mep_finals | 2026-06 | 3 | 2026-09-17 | Inventory |
| 1807 Palmetto Landing Dr, Houston, TX 77009 | mep_finals | 2025-06 | 15 | 2026-09-17 | Inventory |
| 721 Usener St, Houston, TX 77009 | mep_finals | 2025-11 | 10 | 2026-09-17 | Inventory |
| 115 Northwood St, Houston, TX 77009 | mep_finals | 2026-04 | 5 | 2026-09-17 | custom |
| 2922 Michaux St, Houston, TX 77009 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 2924 Michaux St, Houston, TX 77009 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 2920 Michaux St, Houston, TX 77009 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 1110 Jerome St, Houston, TX 77009 | mep_roughs | 2026-04 | 5 | 2027-02-20 | needs_clarification |
| 827 E 25th St, Houston, TX 77009 | mep_finals | 2025-09 | 12 | 2026-09-17 | Inventory |
| 1016 E 27th St, Houston, TX 77009 | interior | 2026-01 | 8 | 2026-10-08 | Inventory |
| 606 Skyland Terrace Way, Houston, TX 77009 | mep_finals | 2026-05 | 4 | 2026-09-17 | Inventory |
| 602 Skyland Terrace Way, Houston, TX 77009 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 603 Skyland Terrace Way, Houston, TX 77009 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
| 615 Skyland Terrace Way, Houston, TX 77009 | interior | 2026-04 | 5 | 2026-10-08 | Inventory |
| 611 Skyland Terrace Way, Houston, TX 77009 | interior | 2026-04 | 5 | 2026-10-08 | Inventory |
| 607 Skyland Terrace Way, Houston, TX 77009 | mep_finals | 2026-07 | 2 | 2026-09-17 | Inventory |
