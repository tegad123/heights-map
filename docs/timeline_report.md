# Permit-anchored timeline and eight-phase delivery — 2026-09-09

Validated at September 9, 2026, noon America/Chicago against the September 8 inspection feeds. Baseline commit `7eb7ab9`; eight market pages. No DATA, sold, deed, permit feed, inspection feed or RECONCILE payload changes. No Custom or Sold Off Market tags applied to actual properties.

## Phase 0 and approved corrections

[Original code, exact final-name inventory, fields and runtime findings](timeline-evidence/phase0.md). [Partial-status counts and ground-truth rule review](timeline-evidence/partial-status-audit.md). These retain the actual commands and captured output, including the pasted original classifier and ETA implementation.

Original ETA was independent flat offsets (ground-in +240 days, windstorm +195 days, insulation +153 days), counting down without new evidence. The classifier receives raw Partial Approval, Approved and failure statuses. Inspection comments are not in the render-time feed. Listing tags are a separate overlay; they do not establish a construction phase. On the Market (building) remains a listing cross-cut and overlaps the displayed phase counts.

Across 645 unique linked home addresses, among 453 without a passed structural final, insulation was Partial/Approved 144/43; frame 29/184. Among 192 with a passed structural final, each was 0/189 (remaining records absent/other). The evidence does not say both milestones are overwhelmingly Partial; the approved change follows observed field practice and Munford/Voight ground truth.

## Exact implemented phase-entry rules

All qualifying inspections accept Approved or Partial Approval; failed, requested and canceled statuses do not advance. The sole partial distinction is 1031-FDN. Highest evidenced phase wins, independent of row order.

| Phase | Entry | Standard days |
|---|---|---:|
| Foundation | Permit exists; ground-in, piers/foundation evidence; 1031-FDN Partial stays here. Site-only evidence does not advance. | 14 |
| Framing | 1031-FDN fully Approved, or FDN-WOOD/INSUL Partial/Approved. | 21 |
| Framed / Exterior Close-In | WINDSTORM, Nail Pattern or Fire Wall Partial/Approved. | 28 |
| MEP Roughs | Plumbing ROUGH IN, electrical ROUGH or HVAC COVER Partial/Approved. Remains until frame or higher evidence. | 21 |
| Insulation | 1035-FRAME Partial/Approved. | 21 |
| INT.CAB, Tile, ETC | INSULATION Partial/Approved. | 114 |
| MEP Finals | First qualifying plumbing, HVAC/AC, electrical, grading or structural final Partial/Approved. | 21 |
| Complete | All five final kinds passed on every represented inspection project; date is last of their first qualifying passes. | 0 |

INT.CAB through Complete totals **114 + 21 = 135 days**, including finals. No extra three weeks added. An insulation inspection directly establishes INT.CAB; frame without insulation establishes the short Insulation phase. Site/utility/civil finals, Brick Tie, TCI and temporary-gas inspections never promote; generic FINAL is grading only when its permit trade is grading. Paired-home finals cannot be assembled across projects to invent completion.

## Timeline formula

Let `d` be current standard phase days, `e = max(0, today − anchor)` and `S` the sum of all later phase durations. The anchor is the latest dated qualifying inspection in the current phase, except MEP Finals uses its first qualifying final. No dated anchor means no forecast. Permit-only homes remain Foundation with an unavailable timeline; no permit means no phase or ETA.

```text
next = max(0, d − e)
overdue = max(0, e − d)
base = (overdue > 0 ? d : next) + S
completion remaining = base + overdue
completion date = today + completion remaining
raw anchor target (diagnostic) = anchor + d + S
```

Before the deadline, the current phase counts down. After it, the forecast uses a fresh standard phase window plus its explicit overdue delay and subsequent phases. This produces the requested “five-week-old Framing is two weeks later than fresh Framing” behavior without assuming unobserved work is complete. There are no cross-property clamps. Base monotonicity checks the phase-duration remaining-time intervals; it does not claim arbitrary raw anchor dates are ordered across different properties. Overdue can legitimately reorder displayed forecasts.

| Worked example | Anchor / elapsed | Arithmetic at Sep 9 | Forecast |
|---|---|---|---|
| 2005 Harvard | Approved 1031-FDN Jul 29; 42 days | Base 21 + 28 + 21 + 21 + 114 + 21 = 226; overdue 42 − 21 = 21; total 247 days | May 14, 2027; ~8 months; 3 weeks overdue |
| 629 E 26th | Partial WINDSTORM Sep 4; 5 days | (28 − 5) + 21 + 21 + 114 + 21 = 200 days; overdue 0 | Mar 28, 2027; ~6.5 months |
| 711 E 25th | Approved insulation Aug 17; 23 days | (114 − 23) + 21 = 112 days = insulation +135 days | Dec 30, 2026; ~3.5 months remaining |

## Fixtures and assertions

| Fixture | Result | Phase / date evidence |
|---|---|---|
| Real fixture 26022264 | PASS | framing; 2026-07-29 2027-05-14 |
| Real fixture 26009059 | PASS | exterior; 2026-09-04 2027-03-28 |
| Real fixture 25118994 | PASS | exterior; 2026-07-22 2027-04-23 |
| Real fixture 26012829 | PASS | interior; 2026-07-28 2026-12-10 |
| Real fixture 26011885 | PASS | interior; 2026-08-17 2026-12-30 |
| Real fixture 25071971 | PASS | complete; 2026-07-07 2026-07-07 |
| Real fixture 25059398 | PASS | complete; 2026-06-18 2026-06-18 |
| Real fixture 25092767 | PASS | complete; 2026-08-25 2026-08-25 |
| Real fixture 22030746 | PASS | interior; 2026-08-04 2026-12-17 |
| Retained fixture 112 E 27th | PASS | complete;   |
| Retained fixture 609 E 25th | PASS | complete;   |
| Retained fixture 118 Munford | PASS | interior;   |
| Retained fixture 711 E 25th A | PASS | interior;   |
| Retained fixture 1033 Voight | PASS | interior;   |
| Retained fixture 1035 Voight | PASS | interior;   |
| Retained fixture 830 E 26th | PASS | None;   |
| Retained fixture 710 Waverly A | PASS | foundation;   |
| Retained fixture 710 Waverly B | PASS | foundation;   |
| Retained fixture 710 Waverly C | PASS | foundation;   |
| Retained fixture 832 E 27th | PASS | framing;   |
| Retained fixture 835 Lawrence | PASS | foundation;   |

Both synthetic four-of-five cases read MEP Finals: structural passed/grading absent, and the inverse. 212 E 24th (`25092767`) reaches Complete from the five actual final dates regardless of order; the feed’s actual dates are preserved rather than forced to match the verbal example.

Mutations caught: (1) restore full-approval-only frame/insulation stickiness → Munford incorrectly demotes; (2) restore former flat offsets → Harvard precedes 629; (3) replace five-finals completion with Struct Final alone → structural-only fixture incorrectly completes. The first mutation reflects the approved rule reversal; the originally requested strict-stickiness expectation was superseded.

| Market | Same-product base pairs tested | Violations | Browser assertions |
|---|---:|---:|---:|
| index | 1969 | 0 | 47/47 |
| montrose | 730 | 0 | 18/18 |
| riveroaks | 27 | 0 | 18/18 |
| springbranch | 3897 | 0 | 18/18 |
| springvalley | 0 | 0 | 18/18 |
| timbergrove | 162 | 0 | 18/18 |
| westu | 160 | 0 | 18/18 |
| gardenoaksoakforest | 338 | 0 | 18/18 |

## Three complete runs and command evidence

Command: `/Users/nemoclaw/insp-venv/bin/python -B tests/full_timeline_check.py`. Each run invokes `node tests/phase_structure.js` and the actual Chromium eight-market fixture/display runner with `--checks --spots`. Raw command output is linked below.

| Run | Classifier | Browser | Base pairs / violations | Errors | JSON SHA256 |
|---|---|---|---|---|---|
| [1](timeline-evidence/run-1.log) | 20706/20706 | 173/173 | 7283 / 0 | [] | `1f7d4da68b0c48a308ec37a80c7e019775f29dc1893e207f8268acd4be3ce765` |
| [2](timeline-evidence/run-2.log) | 20706/20706 | 173/173 | 7283 / 0 | [] | `1f7d4da68b0c48a308ec37a80c7e019775f29dc1893e207f8268acd4be3ce765` |
| [3](timeline-evidence/run-3.log) | 20706/20706 | 173/173 | 7283 / 0 | [] | `1f7d4da68b0c48a308ec37a80c7e019775f29dc1893e207f8268acd4be3ce765` |

Existing suite command: `/Users/nemoclaw/insp-venv/bin/python -B tests/browser_calibration.py --all-markets --output /tmp/timeline-legacy.json`; output: `index.html fixtures 12 / 12`, `page errors: []`. Expectations were migrated to the approved phases and dates; prior ETA values are retained in fixtures.json.

Active regression command: `/Users/nemoclaw/insp-venv/bin/python -B tests/active_browser.py`; output: `active: 40, sold: 764, deeds: 139`; actual Single Lot click 22 listings/22 pins, Split Lot 18 listings/18 pins; normalization 40/40, reload leaves DATA/tags/supply/sold/deeds byte-identical; page errors []. This earlier regression printed supply 125 before the subsequent paired-home count correction; final full runs validate weighted supply 144.

## Supply impact

Heights baseline at the fixed audit date is **138 pins**, not the prompt’s 137. Those pins represent **159 homes**. The old headline used `n++`, while phase columns used home weights. Corrected headline and filters now use the same `UW(id)` weights.

```text
138 old headline + 21 paired-home correction = 159 baseline homes
159 − 26 homes with no permit/phase − 11 with no dated phase anchor
    + 22 newly forecastable homes = 144
144 − 0 Custom − 0 Sold Off Market = 144 homes ready next 12 months
```

This is a construction-timing forecast, not verified for-sale inventory. Complete homes have no ETA and remain outside the completion-within forecast, as before. No sold/listing reconciliation was performed in this change.

| Market | Old headline pins | Old weighted homes | New weighted homes | Change on same home basis |
|---|---:|---:|---:|---:|
| index | 138 | 159 | 144 | -15 |
| montrose | 94 | 114 | 80 | -34 |
| riveroaks | 14 | 14 | 9 | -5 |
| springbranch | 137 | 140 | 120 | -20 |
| springvalley | 6 | 6 | 0 | -6 |
| timbergrove | 27 | 27 | 19 | -8 |
| westu | 28 | 29 | 26 | -3 |
| gardenoaksoakforest | 45 | 45 | 14 | -31 |

Full old phase columns (sitework, foundation, framing, dried-in, exterior, finishing, market, complete):

| Market | SITE | FDN | FRM | DRY | EXT | FIN | RDY | DONE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| index | 8 | 17 | 11 | 4 | 25 | 87 | 37 | 57 |
| montrose | 2 | 19 | 14 | 1 | 6 | 37 | 37 | 21 |
| riveroaks | 0 | 1 | 0 | 1 | 3 | 4 | 5 | 0 |
| springbranch | 0 | 17 | 5 | 1 | 13 | 66 | 56 | 47 |
| springvalley | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| timbergrove | 1 | 1 | 3 | 3 | 1 | 12 | 7 | 10 |
| westu | 0 | 4 | 3 | 0 | 4 | 11 | 9 | 6 |
| gardenoaksoakforest | 0 | 2 | 3 | 0 | 0 | 10 | 38 | 52 |

Full new columns:

| Market | FDN | FRM | EXT | ROUGH | INSUL | INT.CAB | FINALS | DONE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| index | 46 | 11 | 29 | 7 | 13 | 55 | 20 | 52 |
| montrose | 27 | 14 | 7 | 4 | 0 | 31 | 7 | 21 |
| riveroaks | 5 | 0 | 4 | 1 | 0 | 3 | 0 | 0 |
| springbranch | 27 | 5 | 14 | 4 | 6 | 48 | 26 | 33 |
| springvalley | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| timbergrove | 2 | 3 | 4 | 3 | 1 | 6 | 2 | 10 |
| westu | 4 | 3 | 4 | 3 | 1 | 7 | 4 | 3 |
| gardenoaksoakforest | 8 | 3 | 0 | 2 | 0 | 8 | 25 | 34 |

Heights construction group includes 233 homes: 181 pre-Complete +52 Complete. The old standalone Complete row is removed. Product phase entries have checkboxes; Custom and Sold Off Market have separate top-level filters.

### Full Heights forecast membership changes

| Change | Address | Homes | Old phase → new phase |
|---|---|---:|---|
| Removed | 1002 E 25th Street | 1 | market → None |
| Removed | 1032 W 17th Street Unit#A | 1 | market → None |
| Removed | 111 E 18th Street | 1 | market → None |
| Removed | 1207 Tabor Street | 1 | market → None |
| Removed | 1315 Waverly Street | 1 | market → None |
| Removed | 1502 W 21st Street | 2 | market → None |
| Removed | 1906 W 14th | 1 | market → None |
| Removed | 2015 Harvard Street | 1 | market → None |
| Removed | 2218 Gostick Street | 1 | market → None |
| Removed | 3115 Beauchamp Street | 1 | market → None |
| Removed | 602 Jewett Street Unit#B | 2 | market → None |
| Removed | 613 Wendel Street | 1 | market → None |
| Removed | 614 Ridge Street | 1 | market → None |
| Removed | 615 Wendel Street | 1 | market → None |
| Removed | 705 Walton Street | 1 | market → None |
| Removed | 710 Waverly Street Unit#D | 1 | market → None |
| Removed | 741 W 21st Street Unit#A | 2 | market → None |
| Removed | 814 W 17TH Street | 2 | market → None |
| Removed | 830 E 27th Street | 1 | market → None |
| Removed | 830 WAVERLY Street | 1 | market → None |
| Removed | 834 WAVERLY Street | 1 | market → None |
| Removed | 845 West 23rd Street | 1 | market → None |
| Removed | 1108 W 17th St, Houston, TX 77008 | 1 | sitework → foundation |
| Removed | 1110 W 17th St, Houston, TX 77008 | 1 | sitework → foundation |
| Removed | 1112 W 17th St, Houston, TX 77008 | 1 | sitework → foundation |
| Removed | 1114 W 17th St, Houston, TX 77008 | 1 | sitework → foundation |
| Removed | 1116 W 17th St, Houston, TX 77008 | 1 | sitework → foundation |
| Removed | 1118 W 17th St, Houston, TX 77008 | 1 | sitework → foundation |
| Removed | 1306 W 24th St D, Houston, TX 77008 | 1 | exterior → exterior |
| Removed | 1306 W 24th St E, Houston, TX 77008 | 1 | exterior → exterior |
| Removed | 1306 W 24th St F, Houston, TX 77008 | 1 | exterior → exterior |
| Removed | 1922 Bonner St, Houston, TX 77007 | 1 | sitework → foundation |
| Removed | 2311 Roy Cir, Houston, TX 77007 | 1 | sitework → foundation |
| Added | 711 E 12th St, Houston, Tx 77008 | 1 | finishing → interior |
| Added | 1002 E 6TH 1/2 Street | 1 | finishing → mep_finals |
| Added | 1109 Tabor Street | 1 | market → mep_finals |
| Added | 1113 Voight Street | 1 | complete → mep_finals |
| Added | 1140 Waverly Street | 1 | finishing → interior |
| Added | 603 E 23rd Street | 1 | finishing → interior |
| Added | 623 E 13th Street | 1 | market → mep_finals |
| Added | 1104 Gibbs St, Houston, TX 77009 | 1 | complete → mep_finals |
| Added | 1109 Voight St, Houston, TX 77009 | 1 | finishing → mep_finals |
| Added | 2013 Cortlandt St, Houston, TX 77008 | 2 | finishing → interior |
| Added | 310 W 9th St, Houston, TX 77007 | 2 | finishing → interior |
| Added | 625 Oxford St, Houston, TX 77007 | 1 | finishing → interior |
| Added | 718 E 7th St, Houston, TX 77007 | 1 | finishing → interior |
| Added | 727 W 21st St, Houston, TX 77008 | 1 | complete → mep_finals |
| Added | 915 W 18th St A, Houston, TX 77008 | 1 | finishing → insulation |
| Added | 915 W 18th St B, Houston, TX 77008 | 1 | finishing → insulation |
| Added | 915 W 18th St C, Houston, TX 77008 | 1 | finishing → insulation |
| Added | 915 W 18th St D, Houston, TX 77008 | 1 | finishing → insulation |
| Added | 915 W 18th St E, Houston, TX 77008 | 1 | finishing → insulation |
| Added | 915 W 18th St F, Houston, TX 77008 | 1 | finishing → insulation |

### Bucket transitions by market

Counts below are home weights, not pins; unchanged phase memberships are omitted. No-phase records include listing-only and raw deed records.

**index**

| Old phase | New phase | Homes |
|---|---|---:|
| complete | mep_finals | 5 |
| dried_in | exterior | 4 |
| finishing | insulation | 13 |
| finishing | interior | 55 |
| finishing | mep_finals | 12 |
| finishing | mep_roughs | 7 |
| market | mep_finals | 3 |
| market | no phase | 34 |
| no phase | foundation | 21 |
| sitework | foundation | 8 |

**montrose**

| Old phase | New phase | Homes |
|---|---|---:|
| dried_in | exterior | 1 |
| finishing | interior | 29 |
| finishing | mep_finals | 4 |
| finishing | mep_roughs | 4 |
| market | interior | 2 |
| market | mep_finals | 3 |
| market | no phase | 32 |
| no phase | foundation | 6 |
| sitework | foundation | 2 |

**riveroaks**

| Old phase | New phase | Homes |
|---|---|---:|
| dried_in | exterior | 1 |
| finishing | interior | 3 |
| finishing | mep_roughs | 1 |
| market | no phase | 5 |
| no phase | foundation | 4 |

**springbranch**

| Old phase | New phase | Homes |
|---|---|---:|
| complete | mep_finals | 14 |
| dried_in | exterior | 1 |
| finishing | insulation | 6 |
| finishing | interior | 47 |
| finishing | mep_finals | 10 |
| finishing | mep_roughs | 3 |
| market | interior | 1 |
| market | mep_finals | 2 |
| market | no phase | 53 |
| no phase | foundation | 10 |
| no phase | mep_roughs | 1 |

**springvalley**

| Old phase | New phase | Homes |
|---|---|---:|
| market | no phase | 6 |

**timbergrove**

| Old phase | New phase | Homes |
|---|---|---:|
| dried_in | exterior | 3 |
| finishing | insulation | 1 |
| finishing | interior | 6 |
| finishing | mep_finals | 2 |
| finishing | mep_roughs | 3 |
| market | no phase | 7 |
| sitework | foundation | 1 |

**westu**

| Old phase | New phase | Homes |
|---|---|---:|
| complete | mep_finals | 3 |
| finishing | insulation | 1 |
| finishing | interior | 7 |
| finishing | mep_roughs | 3 |
| market | mep_finals | 1 |
| market | no phase | 8 |

**gardenoaksoakforest**

| Old phase | New phase | Homes |
|---|---|---:|
| complete | mep_finals | 18 |
| finishing | interior | 7 |
| finishing | mep_finals | 1 |
| finishing | mep_roughs | 2 |
| market | interior | 1 |
| market | mep_finals | 1 |
| market | no phase | 36 |
| no phase | foundation | 6 |
| no phase | mep_finals | 5 |

## Open items and limits

- No Custom/Sold Off Market property list was supplied; the mechanism is ready, assignments remain with the client. If both tags exist, Sold Off Market has precedence so categories remain disjoint.
- Dated phase anchors are missing for 32 Heights homes (32 pins). They retain their evidence-based phase and explicitly show an unavailable timeline. The report does not invent permit issue dates or borrow a neighboring project’s inspection date.
- Spring Valley still has an empty inspection feed and no permit linkage. Its six old listing-only “ready” entries now have no construction phase/ETA; files were edited in place, never regenerated.
- Five-final completion is conservative for grouped projects. Phase sharing can retain a higher construction phase where another project supplies evidence; without its own current-phase date, an individual home receives no ETA.
- The supplied durations do not calibrate product-specific differences beyond the common standards explicitly requested. The short Insulation phase uses 21 days; verified interior-to-done total remains 135 days.
- No listing/sold status cleanup, comment-driven timing, scraper changes or inventory tag assignments are included.
- Shared-edit writes were blocked during browser validation. Any SYNC FAILED banner in audit screenshots is caused by that isolation, not a deployed server failure.

## Integrity and shipment

Invoked the anchored editor and compared protected JSON payloads against `git show 7eb7ab9:<market>.html`: all eight reported `DATA/SOLD/SEED/LIFE/RECONCILE byte-identical`; inspection and permit feed bytes also unchanged. `git diff --check` returned no output. HTML changes are bounded code edits, not DATA reserialization.

Logical commits: `bbe1532` phase structure; `ae981c3` timeline model; `61af51a` custom/off-market; final display/validation commit follows. Deployment is git push origin main; live confirmation is recorded in the final delivery message.
