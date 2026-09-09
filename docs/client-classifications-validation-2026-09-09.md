# Classification browser validation logs

Actual full-run logs; trailing whitespace trimmed for repository formatting.

## Run 1
```text
$ node tests/phase_structure.js
FIXTURE 22030746 interior PASS
FIXTURE 25059398 complete PASS
FIXTURE 25071971 complete PASS
FIXTURE 25092767 complete PASS
FIXTURE 25118994 exterior PASS
FIXTURE 26009059 exterior PASS
FIXTURE 26011885 interior PASS
FIXTURE 26012829 interior PASS
FIXTURE 26022264 framing PASS
index 6378 checks PASS
montrose 2945 checks PASS
riveroaks 795 checks PASS
springbranch 3656 checks PASS
springvalley 67 checks PASS
timbergrove 727 checks PASS
westu 682 checks PASS
gardenoaksoakforest 5456 checks PASS
TOTAL 20706 checks PASS; no feed-order stage regressions

$ /Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --spots --output /tmp/timeline-full-1.json
127.0.0.1 - - [09/Sep/2026 11:22:41] "GET /index.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:41] "GET /active_listings.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:41] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:41] "GET /inspections.json HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:41] "GET /heights_active.data.json HTTP/1.1" 200 -
SPOT 26022264 KEY PROPERTY INVESTMENT LLC
2005 Harvard St, Houston, TX 77008
LISTING EVIDENCE · 2026-09-08
2005 Harvard St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FRAMING
Next: Framed / Exterior Close-In — overdue
Completion: ~8 months · 2027-05-14
3 weeks overdue for windstorm
Phase anchor: 2026-07-29
PERMIT
HCAD
S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: KEY PROPERTY INVESTMENT LLC
Building Pmt
$920,000
#26022264
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26022264
▲ FRAMING — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 6 weeks ago
City: Final Project Inspection is Outstanding
1031-FDN PM · Building Pmt
2026-07-29
Approved
SEWER · Plumbing Pmt
2026-07-09
Correction Necessary
GROUND IN · Plumbing Pmt
2026-07-09
Partial Approval
Piers AM · Building Pmt
2026-07-06
Partial Approval
SAWPOLE FINAL · ES-SAWPOLE PT
2026-06-23
Approved
PRIOR STORED TAGS · MAY BE STALE
Framing
STORED NOTES · HISTORICAL
OWNER
KEY PROPERTY INVESTMENT LLC
PERMIT
S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
SPOT 26009059 TOMO DEVELOPMENT LLC
629 E 26th St, Houston, TX 77008
LISTING EVIDENCE · 2026-09-08
629 E 26th St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FRAMED / EXTERIOR CLOSE-IN
Next: MEP Roughs in ~3 weeks
Completion: ~6.5 months · 2027-03-28
Phase anchor: 2026-09-04
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$605,502
#26009059
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26009059
▲ FRAMED / EXTERIOR CLOSE-IN — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 6 days ago
City: Final Project Inspection is Outstanding
WINDSTORM · Building Pmt
2026-09-04
Partial Approval
2nd EC · SFR New
2026-09-02
Approved
Ele Grnd Insp · Building Pmt
2026-07-30
Approved
1031-FDN PM · Building Pmt
2026-07-30
Partial Approval
SEWER · Plumbing Pmt
2026-07-24
Approved
GROUND IN · Plumbing Pmt
2026-07-24
Approved
SAWPOLE FINAL · ES-SAWPOLE PT
2026-07-20
Approved
Precon · SFR New
2026-07-17
Approved
+3 earlier
PRIOR STORED TAGS · MAY BE STALE
Framed / Exterior Close-In
STORED NOTES · HISTORICAL
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
SPOT 26005892 CLEVENGER BRYAN
930 Waverly St, Houston, TX 77008
Custom · excluded from inventory
LISTING EVIDENCE · 2026-09-08
930 Waverly St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
MEP ROUGHS
Next: Insulation — overdue
Completion: ~8.5 months · 2027-05-19
11 weeks overdue for 1035-Frame
Phase anchor: 2026-06-05
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: CLEVENGER BRYAN
Building Pmt
$989,472
#26005892
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26005892
▲ MEP ROUGHS — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 8 weeks ago
City: Final Project Inspection is Outstanding
COVER · HVAC Permit
2026-09-09
Inspection Requested
Fire Wall · Building Pmt
2026-08-12
Permit Currently on Hold
EV Level 1 · Electrical Pmt
2026-07-14
Action Required
Nail Pattern · Building Pmt
2026-06-23
Permit Currently on Hold
ROUGH IN · Plumbing Pmt
2026-06-05
Approved
WINDSTORM · Building Pmt
2026-04-30
Approved
1031-FDN AM · Building Pmt
2026-03-26
Permit Currently on Hold
SAWPOLE FINAL · ES-SAWPOLE PT
2026-03-25
Approved
+2 earlier
PRIOR STORED TAGS · MAY BE STALE
MEP Roughs
Custom
STORED NOTES · HISTORICAL
OWNER
CLEVENGER BRYAN
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research ·
SPOT 26012829 TOMO DEVELOPMENT LLC
118 Munford St, Houston, Tx 77008
LISTING EVIDENCE · 2026-09-08
118 Munford St, Houston, Tx 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
INT.CAB, TILE, ETC
Next: MEP Finals in ~10 weeks
Completion: ~3 months · 2026-12-10
Phase anchor: 2026-07-28
ASSESSED
$497,049
SALE DATE
2025-07-30
LOT SQ FT
5,200
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$703,801
#26012829
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26012829
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 1 week ago
City: Final Project Inspection is Outstanding
SHOWER PAN · Plumbing Pmt
2026-09-03
Approved
Gas Test · Plumbing Pmt
2026-09-01
Approved
TEMP GAS INSP · *PG*TEMP GAS
2026-09-01
Approved
TEMP GAS FINAL · *PG*TEMP GAS
2026-09-01
Approved
Driveway PM · Sidewalk,DW,PV
2026-08-21
Approved
Sidewalk PM · Sidewalk,DW,PV
2026-08-21
Approved
GRILLE SEAL · HVAC Permit
2026-08-19
Approved
WATER SERVICE · Plumbing Pmt
2026-08-07
Approved
+16 earlier
PRIOR STORED TAGS · MAY BE STALE
INT.CAB, Tile, ETC
STORED NOTES · HISTORICAL
LIFECYCLE
Deed transfer 2025-07-30 · Tomo Development Llc
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21
SPOT 26011885 TOMO34, LLC
711 E 25th St A, Houston, TX 77008
711 E 25th St B, Houston, TX 77008 paired · 2 homes
LISTING EVIDENCE · 2026-09-08
711 E 25th St A, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
711 E 25th St B, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited. Construction evidence below belongs to the paired project.
INT.CAB, TILE, ETC
Next: MEP Finals in ~13 weeks
Completion: ~3.5 months · 2026-12-30
Phase anchor: 2026-08-17
ASSESSED
$541,525
SALE DATE
2025-12-29
2 PERMITS
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-3-5-R3-B) 21 IRC/21 IECC (M OF 2)
Owner occupant: TOMO34, LLC
Building Pmt
$530,553
#26011885
S.F. RES W/ATT. GARAGE (1-3-5-R3-B) 21 IRC/21 IECC (M#26011885)
Owner occupant: TOMO34, LLC
Building Pmt
$530,553
#26011886
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26011885
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 2 days ago
City: Final Project Inspection is Outstanding
WW Final · Wastewater
2026-09-08
Approved
SHOWER PAN · Plumbing Pmt
2026-09-04
Approved
SHOWER PAN · Plumbing Pmt
2026-09-04
Approved
GRILLE SEAL · HVAC Permit
2026-09-03
Approved
GRILLE SEAL · HVAC Permit
2026-09-03
Approved
SEWER · Plumbing Pmt
2026-08-25
Approved
SEWER · Plumb
SPOT 25071971 TOMO34 HOMES LLC
112 E 27th St A, Houston, TX 77008
112 E 27th Street paired · 2 homes
LISTING EVIDENCE · 2026-09-08
112 E 27th St A, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
112 E 27th Street
Active in HAR export
MLS 34333707 · Split Lot
Original list price: $999,000
DOM: 48 days · Lot: 3,000 sq ft
Builder: J. Christopher Builders
List agent: Spencer Huck
Original list price is not a verified current asking price. Export coverage is limited. Construction evidence below belongs to the paired project.
COMPLETE
Complete · 2026-07-07
FIVE FINALS
#25071971
plumbing: Passed · 2026-07-06
hvac: Passed · 2026-06-05
electrical: Passed · 2026-05-29
grading: Passed · 2026-06-11
structural: Passed · 2026-07-07
#25071972
plumbing: Passed · 2026-06-08
hvac: Passed · 2026-06-05
electrical: Passed · 2026-05-29
grading: Passed · 2026-06-09
structural: Passed · 2026-06-08
2 PERMITS
HCAD
S.F. RES. W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC (MST OF 2)
Owner occupant: TOMO34 HOMES LLC
Building Pmt
$528,968
#25071971
S.F. RES. W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC (M# 25071971)
Owner occupant: TOMO34 HOMES LLC
Building Pmt
$528,968
#25071972
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#25071971
▲ COMPLETE — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Completed 2026-07-07
City: Final Project Inspection is Outstanding
Struct Final
CATEGORY SPOT pmt_1032-key-st-77009 {"category": "custom", "phase": "foundation", "eta": {"anchor": null, "anchorDate": null, "target": null, "months": null, "complete": false, "overdue": false, "overdueDays": 0, "baseDays": null, "remainingDays": null, "nextDays": null, "nextPhase": null, "phase": "foundation", "missingAnchor": true}, "projects": ["25117865"]} HILL KRYSTAL
1032 Key St, Houston, TX 77009
Custom · excluded from inventory
LISTING EVIDENCE · 2026-09-08
1032 Key St, Houston, TX 77009
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FOUNDATION
Next / completion: unavailable — no dated phase evidence
PERMIT
HCAD
S.F. RES W/DET. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: HILL KRYSTAL
Building Pmt
$415,679
#25117865
Look up on COH ↗
INSPECTIONS
NONE
Updated 2026-09-08
#25117865
▲ FOUNDATION — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
City: Final Project Inspection is Outstanding
No inspection records yet
PRIOR STORED TAGS · MAY BE STALE
Foundation
Custom
STORED NOTES · HISTORICAL
OWNER
HILL KRYSTAL
PERMIT
S.F. RES W/DET. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research · 2026-09-09
CATEGORY SPOT pmt_728-euclid-st-77009 {"category": "sold_off_market", "phase": "interior", "eta": {"anchor": "INSULATION", "anchorDate": "2026-08-07", "target": "2026-12-20", "months": 3.5, "complete": false, "overdue": false, "overdueDays": 0, "baseDays": 102, "remainingDays": 102, "nextDays": 81, "nextPhase": "mep_finals", "duration": 114, "elapsed": 33, "anchorTarget": "2026-12-20", "baseTarget": "2026-12-20", "phase": "interior", "anchorProject": "26006967"}, "projects": ["26006967"]} TOMO DEVELOPMENT LLC
728 Euclid St, Houston, TX 77009
Sold Off Market · excluded from inventory
LISTING EVIDENCE · 2026-09-08
728 Euclid St, Houston, TX 77009
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
INT.CAB, TILE, ETC
Next: MEP Finals in ~12 weeks
Completion: ~3.5 months · 2026-12-20
Phase anchor: 2026-08-07
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$683,190
#26006967
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26006967
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 1 week ago
City: Final Project Inspection is Outstanding
SEWER · Plumbing Pmt
2026-09-01
Approved
SHOWER PAN · Plumbing Pmt
2026-09-01
Approved
WATER SERVICE · Plumbing Pmt
2026-08-31
Approved
TCI · Electrical Pmt
2026-08-11
Approved
INSULATION · Building Pmt
2026-08-07
Partial Approval
DITCH COVER · Electrical Pmt
2026-08-05
Approved
1035-Frame · Building Pmt
2026-08-05
Approved
Nail Pattern · Building Pmt
2026-07-29
Approved
+7 earlier
PRIOR STORED TAGS · MAY BE STALE
INT.CAB, Tile, ETC
Sold Off Market
STORED NOTES · HISTORICAL
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research · 2026-09-09
CATEGORY LAYERS Custom
19
Single Lot
17
Unknown
2 Sold Off Market
1
index {"supply": 131, "columns": {"foundation": 37, "framing": 10, "exterior": 28, "mep_roughs": 5, "insulation": 12, "interior": 53, "mep_finals": 19, "complete": 49}, "uc": 213, "deed": 139, "sold": 767}
CHECKS index 57 / 57 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:22:51] "GET /montrose.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:51] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:51] "GET /inspections_montrose.json HTTP/1.1" 200 -
montrose {"supply": 80, "columns": {"foundation": 27, "framing": 14, "exterior": 7, "mep_roughs": 4, "insulation": 0, "interior": 31, "mep_finals": 7, "complete": 21}, "uc": 111, "deed": 83, "sold": null}
CHECKS montrose 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:22:52] "GET /riveroaks.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:52] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:52] "GET /inspections_riveroaks.json HTTP/1.1" 200 -
riveroaks {"supply": 9, "columns": {"foundation": 5, "framing": 0, "exterior": 4, "mep_roughs": 1, "insulation": 0, "interior": 3, "mep_finals": 0, "complete": 0}, "uc": 13, "deed": 22, "sold": null}
CHECKS riveroaks 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:22:54] "GET /springbranch.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:54] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:54] "GET /inspections_springbranch.json HTTP/1.1" 200 -
springbranch {"supply": 120, "columns": {"foundation": 27, "framing": 5, "exterior": 14, "mep_roughs": 4, "insulation": 6, "interior": 48, "mep_finals": 26, "complete": 33}, "uc": 163, "deed": 204, "sold": null}
CHECKS springbranch 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:22:55] "GET /springvalley.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:55] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:55] "GET /inspections_springvalley.json HTTP/1.1" 200 -
springvalley {"supply": 0, "columns": {"foundation": 0, "framing": 0, "exterior": 0, "mep_roughs": 0, "insulation": 0, "interior": 0, "mep_finals": 0, "complete": 0}, "uc": 0, "deed": 0, "sold": null}
CHECKS springvalley 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:22:57] "GET /timbergrove.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:57] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:57] "GET /inspections_timbergrove.json HTTP/1.1" 200 -
timbergrove {"supply": 19, "columns": {"foundation": 2, "framing": 3, "exterior": 4, "mep_roughs": 3, "insulation": 1, "interior": 6, "mep_finals": 2, "complete": 10}, "uc": 31, "deed": 3, "sold": null}
CHECKS timbergrove 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:22:58] "GET /westu.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:58] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:22:58] "GET /inspections_westu.json HTTP/1.1" 200 -
westu {"supply": 26, "columns": {"foundation": 4, "framing": 3, "exterior": 4, "mep_roughs": 3, "insulation": 1, "interior": 7, "mep_finals": 4, "complete": 3}, "uc": 29, "deed": 63, "sold": null}
CHECKS westu 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:00] "GET /gardenoaksoakforest.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:00] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:00] "GET /inspections_gardenoaksoakforest.json HTTP/1.1" 200 -
gardenoaksoakforest {"supply": 14, "columns": {"foundation": 8, "framing": 3, "exterior": 0, "mep_roughs": 2, "insulation": 0, "interior": 8, "mep_finals": 25, "complete": 34}, "uc": 80, "deed": 36, "sold": null}
CHECKS gardenoaksoakforest 18 / 18 FAILURES []
ERRORS []

```

## Run 2
```text
$ node tests/phase_structure.js
FIXTURE 22030746 interior PASS
FIXTURE 25059398 complete PASS
FIXTURE 25071971 complete PASS
FIXTURE 25092767 complete PASS
FIXTURE 25118994 exterior PASS
FIXTURE 26009059 exterior PASS
FIXTURE 26011885 interior PASS
FIXTURE 26012829 interior PASS
FIXTURE 26022264 framing PASS
index 6378 checks PASS
montrose 2945 checks PASS
riveroaks 795 checks PASS
springbranch 3656 checks PASS
springvalley 67 checks PASS
timbergrove 727 checks PASS
westu 682 checks PASS
gardenoaksoakforest 5456 checks PASS
TOTAL 20706 checks PASS; no feed-order stage regressions

$ /Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --spots --output /tmp/timeline-full-2.json
127.0.0.1 - - [09/Sep/2026 11:23:02] "GET /index.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:02] "GET /active_listings.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:02] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:02] "GET /inspections.json HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:02] "GET /heights_active.data.json HTTP/1.1" 200 -
SPOT 26022264 KEY PROPERTY INVESTMENT LLC
2005 Harvard St, Houston, TX 77008
LISTING EVIDENCE · 2026-09-08
2005 Harvard St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FRAMING
Next: Framed / Exterior Close-In — overdue
Completion: ~8 months · 2027-05-14
3 weeks overdue for windstorm
Phase anchor: 2026-07-29
PERMIT
HCAD
S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: KEY PROPERTY INVESTMENT LLC
Building Pmt
$920,000
#26022264
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26022264
▲ FRAMING — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 6 weeks ago
City: Final Project Inspection is Outstanding
1031-FDN PM · Building Pmt
2026-07-29
Approved
SEWER · Plumbing Pmt
2026-07-09
Correction Necessary
GROUND IN · Plumbing Pmt
2026-07-09
Partial Approval
Piers AM · Building Pmt
2026-07-06
Partial Approval
SAWPOLE FINAL · ES-SAWPOLE PT
2026-06-23
Approved
PRIOR STORED TAGS · MAY BE STALE
Framing
STORED NOTES · HISTORICAL
OWNER
KEY PROPERTY INVESTMENT LLC
PERMIT
S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
SPOT 26009059 TOMO DEVELOPMENT LLC
629 E 26th St, Houston, TX 77008
LISTING EVIDENCE · 2026-09-08
629 E 26th St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FRAMED / EXTERIOR CLOSE-IN
Next: MEP Roughs in ~3 weeks
Completion: ~6.5 months · 2027-03-28
Phase anchor: 2026-09-04
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$605,502
#26009059
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26009059
▲ FRAMED / EXTERIOR CLOSE-IN — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 6 days ago
City: Final Project Inspection is Outstanding
WINDSTORM · Building Pmt
2026-09-04
Partial Approval
2nd EC · SFR New
2026-09-02
Approved
Ele Grnd Insp · Building Pmt
2026-07-30
Approved
1031-FDN PM · Building Pmt
2026-07-30
Partial Approval
SEWER · Plumbing Pmt
2026-07-24
Approved
GROUND IN · Plumbing Pmt
2026-07-24
Approved
SAWPOLE FINAL · ES-SAWPOLE PT
2026-07-20
Approved
Precon · SFR New
2026-07-17
Approved
+3 earlier
PRIOR STORED TAGS · MAY BE STALE
Framed / Exterior Close-In
STORED NOTES · HISTORICAL
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
SPOT 26005892 CLEVENGER BRYAN
930 Waverly St, Houston, TX 77008
Custom · excluded from inventory
LISTING EVIDENCE · 2026-09-08
930 Waverly St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
MEP ROUGHS
Next: Insulation — overdue
Completion: ~8.5 months · 2027-05-19
11 weeks overdue for 1035-Frame
Phase anchor: 2026-06-05
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: CLEVENGER BRYAN
Building Pmt
$989,472
#26005892
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26005892
▲ MEP ROUGHS — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 8 weeks ago
City: Final Project Inspection is Outstanding
COVER · HVAC Permit
2026-09-09
Inspection Requested
Fire Wall · Building Pmt
2026-08-12
Permit Currently on Hold
EV Level 1 · Electrical Pmt
2026-07-14
Action Required
Nail Pattern · Building Pmt
2026-06-23
Permit Currently on Hold
ROUGH IN · Plumbing Pmt
2026-06-05
Approved
WINDSTORM · Building Pmt
2026-04-30
Approved
1031-FDN AM · Building Pmt
2026-03-26
Permit Currently on Hold
SAWPOLE FINAL · ES-SAWPOLE PT
2026-03-25
Approved
+2 earlier
PRIOR STORED TAGS · MAY BE STALE
MEP Roughs
Custom
STORED NOTES · HISTORICAL
OWNER
CLEVENGER BRYAN
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research ·
SPOT 26012829 TOMO DEVELOPMENT LLC
118 Munford St, Houston, Tx 77008
LISTING EVIDENCE · 2026-09-08
118 Munford St, Houston, Tx 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
INT.CAB, TILE, ETC
Next: MEP Finals in ~10 weeks
Completion: ~3 months · 2026-12-10
Phase anchor: 2026-07-28
ASSESSED
$497,049
SALE DATE
2025-07-30
LOT SQ FT
5,200
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$703,801
#26012829
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26012829
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 1 week ago
City: Final Project Inspection is Outstanding
SHOWER PAN · Plumbing Pmt
2026-09-03
Approved
Gas Test · Plumbing Pmt
2026-09-01
Approved
TEMP GAS INSP · *PG*TEMP GAS
2026-09-01
Approved
TEMP GAS FINAL · *PG*TEMP GAS
2026-09-01
Approved
Driveway PM · Sidewalk,DW,PV
2026-08-21
Approved
Sidewalk PM · Sidewalk,DW,PV
2026-08-21
Approved
GRILLE SEAL · HVAC Permit
2026-08-19
Approved
WATER SERVICE · Plumbing Pmt
2026-08-07
Approved
+16 earlier
PRIOR STORED TAGS · MAY BE STALE
INT.CAB, Tile, ETC
STORED NOTES · HISTORICAL
LIFECYCLE
Deed transfer 2025-07-30 · Tomo Development Llc
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21
SPOT 26011885 TOMO34, LLC
711 E 25th St A, Houston, TX 77008
711 E 25th St B, Houston, TX 77008 paired · 2 homes
LISTING EVIDENCE · 2026-09-08
711 E 25th St A, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
711 E 25th St B, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited. Construction evidence below belongs to the paired project.
INT.CAB, TILE, ETC
Next: MEP Finals in ~13 weeks
Completion: ~3.5 months · 2026-12-30
Phase anchor: 2026-08-17
ASSESSED
$541,525
SALE DATE
2025-12-29
2 PERMITS
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-3-5-R3-B) 21 IRC/21 IECC (M OF 2)
Owner occupant: TOMO34, LLC
Building Pmt
$530,553
#26011885
S.F. RES W/ATT. GARAGE (1-3-5-R3-B) 21 IRC/21 IECC (M#26011885)
Owner occupant: TOMO34, LLC
Building Pmt
$530,553
#26011886
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26011885
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 2 days ago
City: Final Project Inspection is Outstanding
WW Final · Wastewater
2026-09-08
Approved
SHOWER PAN · Plumbing Pmt
2026-09-04
Approved
SHOWER PAN · Plumbing Pmt
2026-09-04
Approved
GRILLE SEAL · HVAC Permit
2026-09-03
Approved
GRILLE SEAL · HVAC Permit
2026-09-03
Approved
SEWER · Plumbing Pmt
2026-08-25
Approved
SEWER · Plumb
SPOT 25071971 TOMO34 HOMES LLC
112 E 27th St A, Houston, TX 77008
112 E 27th Street paired · 2 homes
LISTING EVIDENCE · 2026-09-08
112 E 27th St A, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
112 E 27th Street
Active in HAR export
MLS 34333707 · Split Lot
Original list price: $999,000
DOM: 48 days · Lot: 3,000 sq ft
Builder: J. Christopher Builders
List agent: Spencer Huck
Original list price is not a verified current asking price. Export coverage is limited. Construction evidence below belongs to the paired project.
COMPLETE
Complete · 2026-07-07
FIVE FINALS
#25071971
plumbing: Passed · 2026-07-06
hvac: Passed · 2026-06-05
electrical: Passed · 2026-05-29
grading: Passed · 2026-06-11
structural: Passed · 2026-07-07
#25071972
plumbing: Passed · 2026-06-08
hvac: Passed · 2026-06-05
electrical: Passed · 2026-05-29
grading: Passed · 2026-06-09
structural: Passed · 2026-06-08
2 PERMITS
HCAD
S.F. RES. W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC (MST OF 2)
Owner occupant: TOMO34 HOMES LLC
Building Pmt
$528,968
#25071971
S.F. RES. W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC (M# 25071971)
Owner occupant: TOMO34 HOMES LLC
Building Pmt
$528,968
#25071972
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#25071971
▲ COMPLETE — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Completed 2026-07-07
City: Final Project Inspection is Outstanding
Struct Final
CATEGORY SPOT pmt_1032-key-st-77009 {"category": "custom", "phase": "foundation", "eta": {"anchor": null, "anchorDate": null, "target": null, "months": null, "complete": false, "overdue": false, "overdueDays": 0, "baseDays": null, "remainingDays": null, "nextDays": null, "nextPhase": null, "phase": "foundation", "missingAnchor": true}, "projects": ["25117865"]} HILL KRYSTAL
1032 Key St, Houston, TX 77009
Custom · excluded from inventory
LISTING EVIDENCE · 2026-09-08
1032 Key St, Houston, TX 77009
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FOUNDATION
Next / completion: unavailable — no dated phase evidence
PERMIT
HCAD
S.F. RES W/DET. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: HILL KRYSTAL
Building Pmt
$415,679
#25117865
Look up on COH ↗
INSPECTIONS
NONE
Updated 2026-09-08
#25117865
▲ FOUNDATION — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
City: Final Project Inspection is Outstanding
No inspection records yet
PRIOR STORED TAGS · MAY BE STALE
Foundation
Custom
STORED NOTES · HISTORICAL
OWNER
HILL KRYSTAL
PERMIT
S.F. RES W/DET. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research · 2026-09-09
CATEGORY SPOT pmt_728-euclid-st-77009 {"category": "sold_off_market", "phase": "interior", "eta": {"anchor": "INSULATION", "anchorDate": "2026-08-07", "target": "2026-12-20", "months": 3.5, "complete": false, "overdue": false, "overdueDays": 0, "baseDays": 102, "remainingDays": 102, "nextDays": 81, "nextPhase": "mep_finals", "duration": 114, "elapsed": 33, "anchorTarget": "2026-12-20", "baseTarget": "2026-12-20", "phase": "interior", "anchorProject": "26006967"}, "projects": ["26006967"]} TOMO DEVELOPMENT LLC
728 Euclid St, Houston, TX 77009
Sold Off Market · excluded from inventory
LISTING EVIDENCE · 2026-09-08
728 Euclid St, Houston, TX 77009
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
INT.CAB, TILE, ETC
Next: MEP Finals in ~12 weeks
Completion: ~3.5 months · 2026-12-20
Phase anchor: 2026-08-07
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$683,190
#26006967
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26006967
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 1 week ago
City: Final Project Inspection is Outstanding
SEWER · Plumbing Pmt
2026-09-01
Approved
SHOWER PAN · Plumbing Pmt
2026-09-01
Approved
WATER SERVICE · Plumbing Pmt
2026-08-31
Approved
TCI · Electrical Pmt
2026-08-11
Approved
INSULATION · Building Pmt
2026-08-07
Partial Approval
DITCH COVER · Electrical Pmt
2026-08-05
Approved
1035-Frame · Building Pmt
2026-08-05
Approved
Nail Pattern · Building Pmt
2026-07-29
Approved
+7 earlier
PRIOR STORED TAGS · MAY BE STALE
INT.CAB, Tile, ETC
Sold Off Market
STORED NOTES · HISTORICAL
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research · 2026-09-09
CATEGORY LAYERS Custom
19
Single Lot
17
Unknown
2 Sold Off Market
1
index {"supply": 131, "columns": {"foundation": 37, "framing": 10, "exterior": 28, "mep_roughs": 5, "insulation": 12, "interior": 53, "mep_finals": 19, "complete": 49}, "uc": 213, "deed": 139, "sold": 767}
CHECKS index 57 / 57 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:11] "GET /montrose.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:11] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:11] "GET /inspections_montrose.json HTTP/1.1" 200 -
montrose {"supply": 80, "columns": {"foundation": 27, "framing": 14, "exterior": 7, "mep_roughs": 4, "insulation": 0, "interior": 31, "mep_finals": 7, "complete": 21}, "uc": 111, "deed": 83, "sold": null}
CHECKS montrose 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:13] "GET /riveroaks.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:13] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:13] "GET /inspections_riveroaks.json HTTP/1.1" 200 -
riveroaks {"supply": 9, "columns": {"foundation": 5, "framing": 0, "exterior": 4, "mep_roughs": 1, "insulation": 0, "interior": 3, "mep_finals": 0, "complete": 0}, "uc": 13, "deed": 22, "sold": null}
CHECKS riveroaks 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:14] "GET /springbranch.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:14] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:14] "GET /inspections_springbranch.json HTTP/1.1" 200 -
springbranch {"supply": 120, "columns": {"foundation": 27, "framing": 5, "exterior": 14, "mep_roughs": 4, "insulation": 6, "interior": 48, "mep_finals": 26, "complete": 33}, "uc": 163, "deed": 204, "sold": null}
CHECKS springbranch 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:15] "GET /springvalley.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:15] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:15] "GET /inspections_springvalley.json HTTP/1.1" 200 -
springvalley {"supply": 0, "columns": {"foundation": 0, "framing": 0, "exterior": 0, "mep_roughs": 0, "insulation": 0, "interior": 0, "mep_finals": 0, "complete": 0}, "uc": 0, "deed": 0, "sold": null}
CHECKS springvalley 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:17] "GET /timbergrove.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:17] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:17] "GET /inspections_timbergrove.json HTTP/1.1" 200 -
timbergrove {"supply": 19, "columns": {"foundation": 2, "framing": 3, "exterior": 4, "mep_roughs": 3, "insulation": 1, "interior": 6, "mep_finals": 2, "complete": 10}, "uc": 31, "deed": 3, "sold": null}
CHECKS timbergrove 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:18] "GET /westu.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:18] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:18] "GET /inspections_westu.json HTTP/1.1" 200 -
westu {"supply": 26, "columns": {"foundation": 4, "framing": 3, "exterior": 4, "mep_roughs": 3, "insulation": 1, "interior": 7, "mep_finals": 4, "complete": 3}, "uc": 29, "deed": 63, "sold": null}
CHECKS westu 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:19] "GET /gardenoaksoakforest.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:19] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:19] "GET /inspections_gardenoaksoakforest.json HTTP/1.1" 200 -
gardenoaksoakforest {"supply": 14, "columns": {"foundation": 8, "framing": 3, "exterior": 0, "mep_roughs": 2, "insulation": 0, "interior": 8, "mep_finals": 25, "complete": 34}, "uc": 80, "deed": 36, "sold": null}
CHECKS gardenoaksoakforest 18 / 18 FAILURES []
ERRORS []

```

## Run 3
```text
$ node tests/phase_structure.js
FIXTURE 22030746 interior PASS
FIXTURE 25059398 complete PASS
FIXTURE 25071971 complete PASS
FIXTURE 25092767 complete PASS
FIXTURE 25118994 exterior PASS
FIXTURE 26009059 exterior PASS
FIXTURE 26011885 interior PASS
FIXTURE 26012829 interior PASS
FIXTURE 26022264 framing PASS
index 6378 checks PASS
montrose 2945 checks PASS
riveroaks 795 checks PASS
springbranch 3656 checks PASS
springvalley 67 checks PASS
timbergrove 727 checks PASS
westu 682 checks PASS
gardenoaksoakforest 5456 checks PASS
TOTAL 20706 checks PASS; no feed-order stage regressions

$ /Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --spots --output /tmp/timeline-full-3.json
127.0.0.1 - - [09/Sep/2026 11:23:21] "GET /index.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:21] "GET /active_listings.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:21] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:22] "GET /inspections.json HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:22] "GET /heights_active.data.json HTTP/1.1" 200 -
SPOT 26022264 KEY PROPERTY INVESTMENT LLC
2005 Harvard St, Houston, TX 77008
LISTING EVIDENCE · 2026-09-08
2005 Harvard St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FRAMING
Next: Framed / Exterior Close-In — overdue
Completion: ~8 months · 2027-05-14
3 weeks overdue for windstorm
Phase anchor: 2026-07-29
PERMIT
HCAD
S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: KEY PROPERTY INVESTMENT LLC
Building Pmt
$920,000
#26022264
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26022264
▲ FRAMING — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 6 weeks ago
City: Final Project Inspection is Outstanding
1031-FDN PM · Building Pmt
2026-07-29
Approved
SEWER · Plumbing Pmt
2026-07-09
Correction Necessary
GROUND IN · Plumbing Pmt
2026-07-09
Partial Approval
Piers AM · Building Pmt
2026-07-06
Partial Approval
SAWPOLE FINAL · ES-SAWPOLE PT
2026-06-23
Approved
PRIOR STORED TAGS · MAY BE STALE
Framing
STORED NOTES · HISTORICAL
OWNER
KEY PROPERTY INVESTMENT LLC
PERMIT
S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
SPOT 26009059 TOMO DEVELOPMENT LLC
629 E 26th St, Houston, TX 77008
LISTING EVIDENCE · 2026-09-08
629 E 26th St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FRAMED / EXTERIOR CLOSE-IN
Next: MEP Roughs in ~3 weeks
Completion: ~6.5 months · 2027-03-28
Phase anchor: 2026-09-04
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$605,502
#26009059
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26009059
▲ FRAMED / EXTERIOR CLOSE-IN — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 6 days ago
City: Final Project Inspection is Outstanding
WINDSTORM · Building Pmt
2026-09-04
Partial Approval
2nd EC · SFR New
2026-09-02
Approved
Ele Grnd Insp · Building Pmt
2026-07-30
Approved
1031-FDN PM · Building Pmt
2026-07-30
Partial Approval
SEWER · Plumbing Pmt
2026-07-24
Approved
GROUND IN · Plumbing Pmt
2026-07-24
Approved
SAWPOLE FINAL · ES-SAWPOLE PT
2026-07-20
Approved
Precon · SFR New
2026-07-17
Approved
+3 earlier
PRIOR STORED TAGS · MAY BE STALE
Framed / Exterior Close-In
STORED NOTES · HISTORICAL
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
SPOT 26005892 CLEVENGER BRYAN
930 Waverly St, Houston, TX 77008
Custom · excluded from inventory
LISTING EVIDENCE · 2026-09-08
930 Waverly St, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
MEP ROUGHS
Next: Insulation — overdue
Completion: ~8.5 months · 2027-05-19
11 weeks overdue for 1035-Frame
Phase anchor: 2026-06-05
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: CLEVENGER BRYAN
Building Pmt
$989,472
#26005892
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26005892
▲ MEP ROUGHS — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 8 weeks ago
City: Final Project Inspection is Outstanding
COVER · HVAC Permit
2026-09-09
Inspection Requested
Fire Wall · Building Pmt
2026-08-12
Permit Currently on Hold
EV Level 1 · Electrical Pmt
2026-07-14
Action Required
Nail Pattern · Building Pmt
2026-06-23
Permit Currently on Hold
ROUGH IN · Plumbing Pmt
2026-06-05
Approved
WINDSTORM · Building Pmt
2026-04-30
Approved
1031-FDN AM · Building Pmt
2026-03-26
Permit Currently on Hold
SAWPOLE FINAL · ES-SAWPOLE PT
2026-03-25
Approved
+2 earlier
PRIOR STORED TAGS · MAY BE STALE
MEP Roughs
Custom
STORED NOTES · HISTORICAL
OWNER
CLEVENGER BRYAN
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research ·
SPOT 26012829 TOMO DEVELOPMENT LLC
118 Munford St, Houston, Tx 77008
LISTING EVIDENCE · 2026-09-08
118 Munford St, Houston, Tx 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
INT.CAB, TILE, ETC
Next: MEP Finals in ~10 weeks
Completion: ~3 months · 2026-12-10
Phase anchor: 2026-07-28
ASSESSED
$497,049
SALE DATE
2025-07-30
LOT SQ FT
5,200
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$703,801
#26012829
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26012829
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 1 week ago
City: Final Project Inspection is Outstanding
SHOWER PAN · Plumbing Pmt
2026-09-03
Approved
Gas Test · Plumbing Pmt
2026-09-01
Approved
TEMP GAS INSP · *PG*TEMP GAS
2026-09-01
Approved
TEMP GAS FINAL · *PG*TEMP GAS
2026-09-01
Approved
Driveway PM · Sidewalk,DW,PV
2026-08-21
Approved
Sidewalk PM · Sidewalk,DW,PV
2026-08-21
Approved
GRILLE SEAL · HVAC Permit
2026-08-19
Approved
WATER SERVICE · Plumbing Pmt
2026-08-07
Approved
+16 earlier
PRIOR STORED TAGS · MAY BE STALE
INT.CAB, Tile, ETC
STORED NOTES · HISTORICAL
LIFECYCLE
Deed transfer 2025-07-30 · Tomo Development Llc
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21
SPOT 26011885 TOMO34, LLC
711 E 25th St A, Houston, TX 77008
711 E 25th St B, Houston, TX 77008 paired · 2 homes
LISTING EVIDENCE · 2026-09-08
711 E 25th St A, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
711 E 25th St B, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited. Construction evidence below belongs to the paired project.
INT.CAB, TILE, ETC
Next: MEP Finals in ~13 weeks
Completion: ~3.5 months · 2026-12-30
Phase anchor: 2026-08-17
ASSESSED
$541,525
SALE DATE
2025-12-29
2 PERMITS
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-3-5-R3-B) 21 IRC/21 IECC (M OF 2)
Owner occupant: TOMO34, LLC
Building Pmt
$530,553
#26011885
S.F. RES W/ATT. GARAGE (1-3-5-R3-B) 21 IRC/21 IECC (M#26011885)
Owner occupant: TOMO34, LLC
Building Pmt
$530,553
#26011886
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26011885
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 2 days ago
City: Final Project Inspection is Outstanding
WW Final · Wastewater
2026-09-08
Approved
SHOWER PAN · Plumbing Pmt
2026-09-04
Approved
SHOWER PAN · Plumbing Pmt
2026-09-04
Approved
GRILLE SEAL · HVAC Permit
2026-09-03
Approved
GRILLE SEAL · HVAC Permit
2026-09-03
Approved
SEWER · Plumbing Pmt
2026-08-25
Approved
SEWER · Plumb
SPOT 25071971 TOMO34 HOMES LLC
112 E 27th St A, Houston, TX 77008
112 E 27th Street paired · 2 homes
LISTING EVIDENCE · 2026-09-08
112 E 27th St A, Houston, TX 77008
Not in this active export; no matching sold comp. Availability unverified.
112 E 27th Street
Active in HAR export
MLS 34333707 · Split Lot
Original list price: $999,000
DOM: 48 days · Lot: 3,000 sq ft
Builder: J. Christopher Builders
List agent: Spencer Huck
Original list price is not a verified current asking price. Export coverage is limited. Construction evidence below belongs to the paired project.
COMPLETE
Complete · 2026-07-07
FIVE FINALS
#25071971
plumbing: Passed · 2026-07-06
hvac: Passed · 2026-06-05
electrical: Passed · 2026-05-29
grading: Passed · 2026-06-11
structural: Passed · 2026-07-07
#25071972
plumbing: Passed · 2026-06-08
hvac: Passed · 2026-06-05
electrical: Passed · 2026-05-29
grading: Passed · 2026-06-09
structural: Passed · 2026-06-08
2 PERMITS
HCAD
S.F. RES. W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC (MST OF 2)
Owner occupant: TOMO34 HOMES LLC
Building Pmt
$528,968
#25071971
S.F. RES. W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC (M# 25071971)
Owner occupant: TOMO34 HOMES LLC
Building Pmt
$528,968
#25071972
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#25071971
▲ COMPLETE — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Completed 2026-07-07
City: Final Project Inspection is Outstanding
Struct Final
CATEGORY SPOT pmt_1032-key-st-77009 {"category": "custom", "phase": "foundation", "eta": {"anchor": null, "anchorDate": null, "target": null, "months": null, "complete": false, "overdue": false, "overdueDays": 0, "baseDays": null, "remainingDays": null, "nextDays": null, "nextPhase": null, "phase": "foundation", "missingAnchor": true}, "projects": ["25117865"]} HILL KRYSTAL
1032 Key St, Houston, TX 77009
Custom · excluded from inventory
LISTING EVIDENCE · 2026-09-08
1032 Key St, Houston, TX 77009
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
FOUNDATION
Next / completion: unavailable — no dated phase evidence
PERMIT
HCAD
S.F. RES W/DET. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: HILL KRYSTAL
Building Pmt
$415,679
#25117865
Look up on COH ↗
INSPECTIONS
NONE
Updated 2026-09-08
#25117865
▲ FOUNDATION — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
City: Final Project Inspection is Outstanding
No inspection records yet
PRIOR STORED TAGS · MAY BE STALE
Foundation
Custom
STORED NOTES · HISTORICAL
OWNER
HILL KRYSTAL
PERMIT
S.F. RES W/DET. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research · 2026-09-09
CATEGORY SPOT pmt_728-euclid-st-77009 {"category": "sold_off_market", "phase": "interior", "eta": {"anchor": "INSULATION", "anchorDate": "2026-08-07", "target": "2026-12-20", "months": 3.5, "complete": false, "overdue": false, "overdueDays": 0, "baseDays": 102, "remainingDays": 102, "nextDays": 81, "nextPhase": "mep_finals", "duration": 114, "elapsed": 33, "anchorTarget": "2026-12-20", "baseTarget": "2026-12-20", "phase": "interior", "anchorProject": "26006967"}, "projects": ["26006967"]} TOMO DEVELOPMENT LLC
728 Euclid St, Houston, TX 77009
Sold Off Market · excluded from inventory
LISTING EVIDENCE · 2026-09-08
728 Euclid St, Houston, TX 77009
Not in this active export; no matching sold comp. Availability unverified.
Original list price is not a verified current asking price. Export coverage is limited.
INT.CAB, TILE, ETC
Next: MEP Finals in ~12 weeks
Completion: ~3.5 months · 2026-12-20
Phase anchor: 2026-08-07
PERMIT
HCAD
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Owner occupant: TOMO DEVELOPMENT LLC
Building Pmt
$683,190
#26006967
Look up on COH ↗
INSPECTIONS
PARTIAL
Updated 2026-09-08
#26006967
▲ INT.CAB, TILE, ETC — FURTHEST STAGE CERTIFIED BY A PASSED INSPECTION
Last inspection: 1 week ago
City: Final Project Inspection is Outstanding
SEWER · Plumbing Pmt
2026-09-01
Approved
SHOWER PAN · Plumbing Pmt
2026-09-01
Approved
WATER SERVICE · Plumbing Pmt
2026-08-31
Approved
TCI · Electrical Pmt
2026-08-11
Approved
INSULATION · Building Pmt
2026-08-07
Partial Approval
DITCH COVER · Electrical Pmt
2026-08-05
Approved
1035-Frame · Building Pmt
2026-08-05
Approved
Nail Pattern · Building Pmt
2026-07-29
Approved
+7 earlier
PRIOR STORED TAGS · MAY BE STALE
INT.CAB, Tile, ETC
Sold Off Market
STORED NOTES · HISTORICAL
OWNER
TOMO DEVELOPMENT LLC
PERMIT
QS2 S.F. RES W/ATT. GARAGE (1-2-5-R3-B) 21 IRC/21 IECC
Client research · 2026-09-09
CATEGORY LAYERS Custom
19
Single Lot
17
Unknown
2 Sold Off Market
1
index {"supply": 131, "columns": {"foundation": 37, "framing": 10, "exterior": 28, "mep_roughs": 5, "insulation": 12, "interior": 53, "mep_finals": 19, "complete": 49}, "uc": 213, "deed": 139, "sold": 767}
CHECKS index 57 / 57 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:31] "GET /montrose.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:31] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:31] "GET /inspections_montrose.json HTTP/1.1" 200 -
montrose {"supply": 80, "columns": {"foundation": 27, "framing": 14, "exterior": 7, "mep_roughs": 4, "insulation": 0, "interior": 31, "mep_finals": 7, "complete": 21}, "uc": 111, "deed": 83, "sold": null}
CHECKS montrose 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:32] "GET /riveroaks.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:32] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:32] "GET /inspections_riveroaks.json HTTP/1.1" 200 -
riveroaks {"supply": 9, "columns": {"foundation": 5, "framing": 0, "exterior": 4, "mep_roughs": 1, "insulation": 0, "interior": 3, "mep_finals": 0, "complete": 0}, "uc": 13, "deed": 22, "sold": null}
CHECKS riveroaks 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:33] "GET /springbranch.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:33] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:33] "GET /inspections_springbranch.json HTTP/1.1" 200 -
springbranch {"supply": 120, "columns": {"foundation": 27, "framing": 5, "exterior": 14, "mep_roughs": 4, "insulation": 6, "interior": 48, "mep_finals": 26, "complete": 33}, "uc": 163, "deed": 204, "sold": null}
CHECKS springbranch 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:35] "GET /springvalley.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:35] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:35] "GET /inspections_springvalley.json HTTP/1.1" 200 -
springvalley {"supply": 0, "columns": {"foundation": 0, "framing": 0, "exterior": 0, "mep_roughs": 0, "insulation": 0, "interior": 0, "mep_finals": 0, "complete": 0}, "uc": 0, "deed": 0, "sold": null}
CHECKS springvalley 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:37] "GET /timbergrove.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:37] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:37] "GET /inspections_timbergrove.json HTTP/1.1" 200 -
timbergrove {"supply": 19, "columns": {"foundation": 2, "framing": 3, "exterior": 4, "mep_roughs": 3, "insulation": 1, "interior": 6, "mep_finals": 2, "complete": 10}, "uc": 31, "deed": 3, "sold": null}
CHECKS timbergrove 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:38] "GET /westu.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:38] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:38] "GET /inspections_westu.json HTTP/1.1" 200 -
westu {"supply": 26, "columns": {"foundation": 4, "framing": 3, "exterior": 4, "mep_roughs": 3, "insulation": 1, "interior": 7, "mep_finals": 4, "complete": 3}, "uc": 29, "deed": 63, "sold": null}
CHECKS westu 18 / 18 FAILURES []
127.0.0.1 - - [09/Sep/2026 11:23:39] "GET /gardenoaksoakforest.html HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:39] "GET /inventory_classifications.js HTTP/1.1" 200 -
127.0.0.1 - - [09/Sep/2026 11:23:39] "GET /inspections_gardenoaksoakforest.json HTTP/1.1" 200 -
gardenoaksoakforest {"supply": 14, "columns": {"foundation": 8, "framing": 3, "exterior": 0, "mep_roughs": 2, "insulation": 0, "interior": 8, "mep_finals": 25, "complete": 34}, "uc": 80, "deed": 36, "sold": null}
CHECKS gardenoaksoakforest 18 / 18 FAILURES []
ERRORS []

```
