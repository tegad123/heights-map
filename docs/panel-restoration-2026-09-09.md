# Layers panel restoration — 2026-09-09

Restored the requested hierarchy across all eight market pages. The top-level Market Status block and all market-status sub-rows under Complete are removed. The existing 14-home Single Lot On the Market (building) filter is now in Other, as an overlapping filter. No construction record was reassigned. Future Layers hierarchy changes require explicit user approval.

## Final Heights panel

```text
Deed Transfer — 139
  Recently sold — 139
Market Intel — 0
  New Construction (Permit) — 0
  Built (not listed) — 0
Under Construction — 213
  Single Lot — 64
  Split Lot — 72
  Common Driveway — 53
  Needs Clarification — 24 (product type, not missing phase)
Custom — 19
  Single Lot — 17
  Unknown — 2 (existing Custom subdivision)
Sold Off Market — 1
Other — 5 filters
  Pending / Under Contract — 14
  Off Market – Single Lot — 8
  Off Market – Split Lot — 10
  Needs Clarification — 16
  On the Market (building) — 14
Sold Comps — 767
  Lot type: Single 414; Split 345; Unknown 8
  Recency: 0–30d 55; 30–60d 57; 60–90d 73; 90–180d 203; 180–365d 319; 365+d 60
```

| Construction phase | Single Lot | Split Lot | Common Driveway |
|---|---:|---:|---:|
| Foundation | 6 | 3 | 12 |
| Framing | 4 | 2 | 0 |
| Framed / Exterior Close-In | 9 | 1 | 18 |
| MEP Roughs | 1 | 2 | 1 |
| Insulation | 4 | 2 | 6 |
| INT.CAB, Tile, ETC | 20 | 26 | 6 |
| MEP Finals | 8 | 8 | 1 |
| Complete | 12 | 28 | 9 |

Each product’s eight phase counts sum to its product total: 64, 72, and 53. The additional 24 Under Construction homes have an unresolved product type but a construction phase, giving 64 + 72 + 53 + 24 = 213. Complete is one leaf row per product with counts 12 / 28 / 9.

## Under Construction phase verification

The earlier phase-coverage statement used the wrong scope for the Under Construction question. It is withdrawn. No missing-phase assertion is made about the whole map. The browser query below tests the actual Under Construction membership:

```javascript
const uc = DATA.filter(r => matchSel(pt(r.id).tags, 'G:uc', r.id));
({
  homes: uc.reduce((n, r) => n + UW(r.id), 0),
  missingPhaseIds: uc.filter(r => !homePhase(r.id)).map(r => r.id),
  invalidPhaseTagIds: uc.filter(r =>
    CONSTRUCTION_PHASES.filter(ph => pt(r.id).tags.includes(ph)).length !== 1
  ).map(r => r.id)
})
```

Actual result, repeated identically in the browser runs:

```json
{"homes": 213, "missingPhaseIds": [], "invalidPhaseTagIds": []}
```

All 213 Under Construction homes have exactly one construction phase. Missing-phase record IDs: `[]`. Multiple/invalid-phase record IDs: `[]`. The 24 product-type clarification records are included in this check.

## Reconciliation of the 14-home filter

No homes moved between phases. The prior change only removed the existing filter’s DOM row. Its 14 homes are already counted within Framing 2 + MEP Roughs 1 + Interior 6 + MEP Finals 5 = 14. The filter remains an overlap and is not added to construction totals. The requested 14-home filter retains its original selector and membership.

Exact retained IDs and phases:

| ID | Phase | Homes |
|---|---|---:|
| 2131129832 | mep_finals | 1 |
| act_1109-tabor | mep_finals | 1 |
| act_2603-julian | mep_roughs | 1 |
| act_623-e-13 | mep_finals | 1 |
| act_603-e-23 | interior | 1 |
| act_735-e-8-12 | interior | 1 |
| act_731-e-8-12 | interior | 1 |
| act_248-w-22 | interior | 1 |
| act_2434-white-oak | framing | 1 |
| act_1113-voight | mep_finals | 1 |
| act_1140-waverly | interior | 1 |
| act_2436-white-oak | framing | 1 |
| act_1002-e-6-12 | mep_finals | 1 |
| act_2924-watson-street | interior | 1 |

## Preserved behavior

- 715 Merrill remains Active, MLS 88557637, 8 DOM, with terminated MLS 50361472 at 174 DOM visible in history alongside Complete construction.
- Terminated ingest, listing-history resolution, linkage repair, market data, popup functions, and snapshot calculations are unchanged.
- Custom 19, Sold Off Market 1, deeds 139, sold comps 767, and snapshot 128 remain unchanged.
- No HTML, DATA, RECONCILE, construction phase, timeline, scraper, or ingest source was changed by this restoration.

## Executed verification

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --three
/Users/nemoclaw/insp-venv/bin/python -B tests/full_timeline_check.py
```

Panel/property tests: three identical result hashes `e4d9bf4ccec8ad1a60659c35ec1b6cc52d4f229e1e518425cf502b1f366e4f74`.
Construction tests: three identical result hashes `01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a`; each run passed 20,706 phase checks, 183/183 browser checks, 7,283 base-timeline pairs, zero violations, and zero page errors.

The panel tests invoke every popup, verify the group order on all eight pages, require eight construction phase rows per product, assert each product subtotal, and click the relocated Other filter to prove it selects 14 homes. Ingest idempotency still returns zero changes and identical artifact hashes.

Code commit: `250af51`. Verified with `git show --format=fuller --stat HEAD` before pushing to `origin main`.

Raw local evidence: [panel-local-validation-2026-09-09.txt](panel-local-validation-2026-09-09.txt).
Raw construction evidence: [panel-construction-validation-2026-09-09.txt](panel-construction-validation-2026-09-09.txt).

## Live verification

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --live https://tangerine-sorbet-eca5f5.netlify.app --three
```

All three live runs returned the same result hash as the local panel runs: `e4d9bf4ccec8ad1a60659c35ec1b6cc52d4f229e1e518425cf502b1f366e4f74`. Each verified the deployed shared script and market snapshot byte-for-byte, all eight panel hierarchies, the 14-home Other filter, and all popup fixtures.

Actual repeated output:

```text
PANEL Under Construction 213; missing phase IDs []; invalid phase-tag IDs []; Other on-market overlap 14
PASS live market scripts and snapshot byte-identical
PASS all runs identical
```

Raw live evidence: [panel-live-validation-2026-09-09.txt](panel-live-validation-2026-09-09.txt).
