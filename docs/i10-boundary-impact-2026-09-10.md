# Proposed I-10 southern edge: impact audit — 2026-09-10

No boundary changes or removals applied. Scope: replace the southern reach of Heights with I-10, from the existing western polygon intersection through the eastern -95.370 cutoff. This is the full affected southern stretch, not merely west of Shepherd.

Method: City of Houston RoadCenterline FeatureServer/0, highway segments with shieldnum=10, queried within -95.43,29.76,-95.365,29.79. Interpolate both mainline carriageways at each record longitude; count records south of both. Zero records lie between the carriageways, so either mainline gives identical membership. This is a coordinate-based impact estimate, not a surveyed right-of-way boundary.

Source: https://services.arcgis.com/NummVBqZSIJKUeVR/ArcGIS/rest/services/COH_RoadCenterline/FeatureServer/0

605 saved DATA + 791 SOLD_DATA checked. Affected: 26 permit records, 1 deed, 1 sold comp = 28. DATA runtime: 27 distinct projects representing 27 homes; sold archive adds 1 transaction. No additional listing/lead records. Phases: 10 Foundation, 1 Exterior, 3 MEP Finals, 12 Complete, 1 deed with no phase. Sold comp has no construction phase.

Fresh shared snapshot: 2026-09-10T16:33:56.501Z, 0 fieldEdits and 0 posEdits, 548 points. Browser invoked with GET-only shared snapshot replay. Earlier snapshot had moved 408 Columbia south; current snapshot does not. Its saved coordinate is north and it is NOT included.

| Address | Kind | Phase | Latitude | Longitude |
|---|---|---|---:|---:|
| 4616 Eli St C, Houston, TX 77007 | permit | Foundation | 29.7735328 | -95.4079459 |
| 4612 Eli St B, Houston, TX 77007 | permit | Foundation | 29.7735054 | -95.4074178 |
| 4616 Eli St A, Houston, TX 77007 | permit | Foundation | 29.7739068 | -95.4085833 |
| 1604 Spring St, Houston, Tx 77007 | deed | No phase | 29.775384 | -95.374036 |
| 4327 Center St, Houston, TX 77007 | permit | Complete | 29.7708676 | -95.4050481 |
| 4325 Center St, Houston, TX 77007 | permit | Complete | 29.7709404 | -95.4050537 |
| 4323 Center St, Houston, TX 77007 | permit | Complete | 29.7710105 | -95.4050549 |
| 4105 Allen St, Houston, TX 77007 | permit | Complete | 29.7715778 | -95.4026248 |
| 4107 Allen St, Houston, TX 77007 | permit | Complete | 29.7716539 | -95.4026259 |
| 4103 Allen St, Houston, TX 77007 | permit | MEP Finals | 29.7715031 | -95.4026237 |
| 1918 Johnson St, Houston, TX 77007 | permit | Complete | 29.774913 | -95.373384 |
| 1520 Winter St, Houston, TX 77007 | permit | Complete | 29.7724291 | -95.3733714 |
| 5111 Allen St, Houston, TX 77007 | permit | Foundation | 29.7731317 | -95.4131098 |
| 5113 Allen St, Houston, TX 77007 | permit | Exterior | 29.7732421 | -95.413116 |
| 1521 Ovid St, Houston, TX 77007 | permit | Complete | 29.7757274 | -95.373483 |
| 5109 Allen St, Houston, TX 77007 | permit | Foundation | 29.773041 | -95.4131085 |
| 1522 Winter St, Houston, TX 77007 | permit | Complete | 29.7724347 | -95.3734524 |
| 1610 Johnson St, Houston, TX 77007 | permit | Complete | 29.7725683 | -95.3731749 |
| 4605 Nolda St, Houston, TX 77007 | permit | Foundation | 29.7761265 | -95.4078864 |
| 5114 Eigel St, Houston, TX 77007 | permit | Foundation | 29.775 | -95.4132467 |
| 1308 Edwards St B, Houston, TX 77007 | permit | Complete | 29.7710218 | -95.3704417 |
| 1308 Edwards St A, Houston, TX 77007 | permit | Complete | 29.7710227 | -95.3703629 |
| 4612 Eli St C, Houston, TX 77007 | permit | Foundation | 29.7737139 | -95.4078 |
| 4616 Eli St B, Houston, TX 77007 | permit | Foundation | 29.7736217 | -95.4079558 |
| 4612 Eli St A, Houston, TX 77007 | permit | Foundation | 29.7735343 | -95.4077964 |
| 5016 Schuler St, Houston, TX 77007 | permit | MEP Finals | 29.7728294 | -95.4121856 |
| 5018 Schuler St, Houston, TX 77007 | permit | MEP Finals | 29.7728286 | -95.4122644 |
| 4310 Koehler Street Unit#A | sold comp | No phase | 29.77432 | -95.40479 |

## 745 W 17th

Retain Unknown and existing needs_clarification review tag. Added durable record review_note displayed in popup: ten-lot legal, $0 improvements, $1,206,148 land value, HAR land/commercial-use marketing, project 23091472 valuation $11,614; verify actual permit scope and whether it represents home construction. No phase change.

## Invocation results

`/Users/nemoclaw/insp-venv/bin/python -B /tmp/i10_impact.py`

```text
SOURCE COUNTS permit=26 deed=1 sold_comp=1 total=28
RUNTIME projects=27 homes=27
phases foundation=10 complete=12 mep_finals=3 exterior=1 no_phase=1
CARRIAGEWAY SENSITIVE []
```

`/Users/nemoclaw/insp-venv/bin/python -B /tmp/i10_runtime.py`

```text
PASS 745 Unknown, review flag, visible $11,614 permit question
```

Recommendation: this is 28 south-of-freeway records, not only four, but the count does not show dozens of legitimate north-of-I-10 Heights homes being lost. Review the listed streets and authorize the precise freeway-edge definition before implementation.
