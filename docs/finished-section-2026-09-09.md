# Finished section — 2026-09-09

Finished homes now leave Under Construction. Construction certification is unchanged: Complete still requires all five passed finals. Finished is a top-level sibling immediately after Under Construction and before Custom. Each completed home is routed by its resolved current market status.

| Finished row | Single Lot | Split Lot | Common Driveway | Total |
|---|---:|---:|---:|---:|
| Finished on Market | 4 | 9 | 0 | 13 |
| Finished Pending | 2 | 3 | 0 | 5 |
| Finished Sold | 2 | 2 | 0 | 4 |
| Finished Terminated | 0 | 3 | 0 | 3 |
| Finished, No Market Record | 4 | 11 | 9 | 24 |
| **Total** | **12** | **28** | **9** | **49** |

Row sum: **13 + 5 + 4 + 3 + 24 = 49**. Product sum: **12 + 28 + 9 = 49**. Each named home has exactly one current status; prior listings do not generate extra homes. Three unnamed represented homes remain No Market Record. Paired properties share an existing map pin, so that pin can appear when filtering either member’s status; the individual home counts remain mutually exclusive.

Product grouping follows the existing construction grouping. 122 E 4th remains in Split Lot, preserving the prior 4 Single / 9 Split active reconciliation. No product data changed.

| Under Construction | Before | After | Moved to Finished |
|---|---:|---:|---:|
| Single Lot | 64 | 52 | 12 |
| Split Lot | 72 | 44 | 28 |
| Common Driveway | 53 | 44 | 9 |
| Needs Clarification (product) | 24 | 24 | 0 |
| **Total** | **213** | **164** | **49** |

**164 + 49 = 213**. Under Construction phase lists now end at MEP Finals: Foundation, Framing, Framed / Exterior Close-In, MEP Roughs, Insulation, INT.CAB Tile ETC, MEP Finals. No Complete or Finished on Market child remains there. Homes still building retain their market facts on the popup. The existing Other → On the Market (building) overlapping filter remains 14.

## Named-property verification

| Property | Finished row | Evidence |
|---|---|---|
| 709 E 17th St | Finished Sold | MLS 72560168; closed 2026-08-24 at $1,755,000 |
| 212 E 24th St | Finished on Market | Active MLS 29120139 |
| 609 E 25th St | Finished on Market | Active MLS 53672595 |
| 902 E 25th St | Finished on Market | Active MLS 32496070 |
| 715 Merrill St | Finished on Market | Active MLS 88557637; terminated MLS 50361472 remains prior history |
| 1126 E 7th 1/2 St | Finished Pending | Pending MLS 95336494 |
| 1623 Blount St | Finished, No Market Record | No matching supplied market evidence |

931 Merrill (`pmt_931-merrill-st-77009`) is Complete and remains in Finished, No Market Record using the supplied exports. The client confirms a 2026-02-26 sale, outside the 180-day pull. A 12-month sold export covering 2025-09-09 through 2026-09-09 would include that date. No export was run and no sale record was fabricated. Once verified and ingested, this would move one Single Lot home from No Market Record to Sold without changing Finished’s total.

## Supply snapshot

**Before 128; after 128; change 0.** The existing 12-month forecast is 131, minus 3 terminated homes = 128. Complete homes already have no remaining construction ETA and are excluded from that forecast. The 13 Finished on Market homes are now visible separately as available completed homes; this panel change does not add them to the forecast snapshot. Custom 19, Sold Off Market 1, deeds 139, and sold comps 767 remain intact.

## Read-only audit

Invoked `/Users/nemoclaw/insp-venv/bin/python -B /tmp/finished_audit.py` before edits. Its browser query grouped `marketRows().filter(r=>r.phase==="complete")` by status and `typeKeyOf(r.pin)`, and returned:

```json
{
  "counts": {
    "no_record": {
      "Split Lot": 11,
      "Single Lot": 4,
      "Common Driveway": 9
    },
    "pending": {
      "Split Lot": 3,
      "Single Lot": 2
    },
    "sold": {
      "Single Lot": 2,
      "Split Lot": 2
    },
    "terminated": {
      "Split Lot": 3
    },
    "active": {
      "Split Lot": 9,
      "Single Lot": 4
    }
  },
  "uc": 213,
  "ucTypes": [
    {
      "label": "Single Lot",
      "before": 64,
      "after": 52
    },
    {
      "label": "Split Lot",
      "before": 72,
      "after": 44
    },
    {
      "label": "Common Driveway",
      "before": 53,
      "after": 44
    }
  ],
  "snapshot": {
    "construction": 131,
    "terminated": 3,
    "available": 128
  }
}
```

## Verification commands and actual results

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --three
/Users/nemoclaw/insp-venv/bin/python -B tests/full_timeline_check.py
git diff --stat
```

[Local browser command output](finished-section-local-validation-2026-09-09.txt): three identical runs, SHA256 `02813dc0eddec7045fc0a30bcafeea1ec9b7a64301c7f2b67a956641ff6391c6`. [Construction command output](finished-section-construction-validation-2026-09-09.txt): three identical runs; 20,706/20,706 phase checks, 183/183 browser checks, 7,283 timeline pairs and zero violations. Browser tests click every Finished status/product filter and compare actual map-layer IDs, invoke Under Construction’s checkbox, check all named-property popups and verify every status/product sum across all eight markets.

Market ingest runs three times with zero changed files and byte-identical hashes; all 284 input rows and 165/165 new lot classifications are checked. All eight DATA/RECONCILE regions and inline construction/timeline scripts remain byte-identical to `2bb69f5`. Every Heights phase, ETA, and home weight matches the pre-panel baseline.

Application diff: only `market_status.js`, `tests/market_status_check.py`, and `tests/timeline_cases.js`; 95 insertions, 42 deletions. No HTML, DATA, market-history data, scraper, or construction model edits. The changed timeline test replaces its old Complete-checkbox placement assertion with Finished-section placement while retaining all certification checks.

## Other live-market pages

The same shared section and filter logic was invoked on all eight pages. The seven other markets have no supplied market-status export, so their finished homes remain No Market Record. None currently needs an unknown-product child.

| Page | Under Construction | Finished |
|---|---:|---:|
| index | 164 | 49 |
| montrose | 90 | 21 |
| riveroaks | 13 | 0 |
| springbranch | 130 | 33 |
| springvalley | 0 | 0 |
| timbergrove | 21 | 10 |
| westu | 26 | 3 |
| gardenoaksoakforest | 46 | 34 |

## Deployment and live verification

Application commit `d2624a1` was pushed with `git push origin main`. `git show --format=fuller --stat HEAD` verified all three application/test files were in the commit. The initial live attempt reached the previous deployment before CI finished; after `curl` downloaded the deployed script and `cmp market_status.js /tmp/finished-deployed.js` returned exit 0, the full live suite was rerun.

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --three --live https://tangerine-sorbet-eca5f5.netlify.app
```

[Actual live command output](finished-section-live-validation-2026-09-09.txt): three passing, identical runs with SHA256 `02813dc0eddec7045fc0a30bcafeea1ec9b7a64301c7f2b67a956641ff6391c6`, identical to all three local runs. All eight pages, every Finished control, construction separation, named-property popups, idempotency, and byte-identical deployed market script/snapshot passed on each run.
