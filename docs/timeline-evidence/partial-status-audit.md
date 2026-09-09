# Frame / insulation partial-status audit — 2026-09-09

Read-only. No classifier, fixture, feed, or HTML changes.

## Commands and observed output
```text
/Users/nemoclaw/insp-venv/bin/python -B /tmp/partial_status_audit.py
ADDRESS HOMES 844 PERMITS 844 MISSING ADDRESSES 0
/Users/nemoclaw/insp-venv/bin/python -B /tmp/partial_runtime_audit.py
CAPTURED heights pins 204 individual permits 231
CAPTURED montrose pins 94 individual permits 104
CAPTURED riveroaks pins 13 individual permits 13
CAPTURED springbranch pins 162 individual permits 162
CAPTURED springvalley pins 0 individual permits 0
CAPTURED timbergrove pins 31 individual permits 31
CAPTURED westu pins 26 individual permits 29
CAPTURED gardenoaksoakforest pins 80 individual permits 80
ERRORS []
RUNTIME UNIQUE ADDRESSES 645 EXTRA MEMBERSHIPS 5
```

## Definitions
Each individual home is a unit-preserving normalized inspection-project address attached to a visible DATA pin after runtime zone/sold/pair filters. No inferred twin weights are added. Five cross-market duplicates are deduplicated in global counts (their statuses agree). Per-market counts retain membership in each market. Visible/unfinished is not the same as MLS-active. Approved and Partial are exact raw statuses; other means an inspection exists with neither of those statuses. None of these homes has both Partial and Approved rows for the same milestone. Struct Final exists is literal presence of a structural-final row; Struct Final passed uses result=Passed, including Partial Approval.

## Global counts: literal Struct Final existence
| Structural final row | Homes | Insulation P / A / other / absent | 1035-Frame P / A / other / absent |
|---|---:|---|---|
| Absent | 436 | 142 / 34 / 12 / 248 | 28 / 168 / 11 / 229 |
| Exists | 209 | 2 / 198 / 7 / 2 | 1 / 205 / 1 / 2 |

## Global counts: passed Struct Final
| Passed structural final | Homes | Insulation P / A / other / absent | 1035-Frame P / A / other / absent |
|---|---:|---|---|
| No | 453 | 144 / 43 / 18 / 248 | 29 / 184 / 11 / 229 |
| Yes | 192 | 0 / 189 / 1 / 2 | 0 / 189 / 1 / 2 |

## Per-market linked homes
P/A counts exclude absent and other statuses; full denominators and status breakdowns are in partial-runtime-audit.json.
| Market | Passed Struct homes | Insulation P/A | Frame P/A | No passed Struct homes | Insulation P/A | Frame P/A |
|---|---:|---|---|---:|---|---|
| heights | 60 | 0/60 | 0/60 | 171 | 52/12 | 14/63 |
| montrose | 19 | 0/19 | 0/19 | 85 | 22/9 | 5/30 |
| riveroaks | 0 | 0/0 | 0/0 | 13 | 1/2 | 2/1 |
| springbranch | 47 | 0/47 | 0/47 | 115 | 50/8 | 3/62 |
| springvalley | 0 | 0/0 | 0/0 | 0 | 0/0 | 0/0 |
| timbergrove | 10 | 0/10 | 0/10 | 21 | 7/1 | 0/9 |
| westu | 5 | 0/5 | 0/5 | 24 | 2/7 | 1/9 |
| gardenoaksoakforest | 52 | 0/49 | 0/49 | 28 | 10/4 | 4/11 |

## Interpretation and proposed rule
Without a passed Struct Final, insulation is Partial in 144 of 187 Partial-or-Approved homes (77.0%). Frame is Partial in only 29 of 213 (13.6%); both are Partial on 19 homes. Thus “overwhelmingly Partial on both” is not supported. All 189 homes with a passed Struct Final and a Partial-or-Approved frame/insulation record have Approved for both. That is consistent with, but does not longitudinally prove, completion-time conversion.

Propose: MEP Roughs stays until 1035-Frame is Partial Approval or Approved, which enters Insulation. INSULATION Partial Approval or Approved enters INT.CAB, Tile, ETC, even if the frame milestone is absent. Max-of-evidenced-stage aggregation remains monotonic; failures, canceled and requested inspections do not advance. Do not extend this concession to the FDN gate: Partial 1031 stays Foundation, Approved advances Framing. Use the actual milestone date, not comments or owner notes, for the phase/ETA anchor. Preserve the partial status visibly. No property-specific overrides are needed.

Munford 26012829: frame Partial July 23, insulation Partial July 28 -> INT.CAB, anchor July 28. Voight 22030746: frame Partial July 21, insulation Partial August 4 -> INT.CAB, anchor August 4. Voight companion 22030748 is also Partial/Partial.

The 135 days includes finals. No cross-property forecast clamping or date adjustments. Overdue is a separate term and may reorder forecasts.

## Both-partial member list
- heights: 713 E 26th St, Houston, Tx 77009 — 25087111
- heights: 711 E 26th St, Houston, TX 77009 — 25087112
- heights: 614 E 26th St, Houston, Tx 77008 — 25116392
- heights: 118 Munford St, Houston, Tx 77008 — 26012829
- heights: 529 W 27th St, Houston, TX 77008 — 25102310
- heights: 527 W 27th St, Houston, Tx 77008 — 25102311
- heights: 1033 Voight St, Houston, TX 77009 — 22030746
- heights: 1035 Voight St, Houston, TX 77009 — 22030748
- heights: 845 E 26th St, Houston, TX 77009 — 25114005
- heights: 1140 Waverly St, Houston, Tx 77008 — 23084458
- heights: 1138 Fugate St, Houston, TX 77009 — 26007211
- montrose: 10 COURTLANDT PLACE 77006 — 25031363
- montrose: 1125 JACKSON BLVD 77006 — 25119218
- springbranch: 2311 Hollister Street, Houston, TX — 25087139
- springbranch: 2309 Hollister Street, Houston, TX — 25089873
- springbranch: 7610 Janak Spring St 77055 — 25090332
- gardenoaksoakforest: 934 W 43rd Street, Houston, TX — 24060955
- gardenoaksoakforest: 1725 Ebony Lane, Houston, TX — 24024930
- gardenoaksoakforest: 5313 Verdome Lane, Houston, TX — 25050560
