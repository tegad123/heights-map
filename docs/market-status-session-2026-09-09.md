# Heights market-status ingest and reconciliation — September 9, 2026

Ingest/reconciliation completed for the six supplied files: **119 rows**, not the stated 159. Phase 4 is **deferred for construction-linkage review**, as required by its match-quality gate. Construction, timeline, permit pulling, inspection scraping, DATA, RECONCILE, and supply computation remain unchanged. No property was deleted or retired and no custom/sold_off_market tag was applied.

## Discovery → source evidence

[Phase 0 findings with exact code, commands, counts and provenance](market-status-discovery-2026-09-09.md). The clean runtime baseline is preserved in [baseline JSON](market-status-baseline-2026-09-09.json).

The map starts at 144 forecast homes, 52 Complete homes, 139 deeds and 764 sales. Tabor's old tags overlap: Active (Finished), Pending, Active Single, listed. Its phase is **null**, with no linked permits; “Active (Finished)” is not a construction certificate. Its MLS 85478626 sold August 31, 2026 for $949,000 and already existed in SOLD_DATA.

## Ingest

| Source | Read | Added to status snapshot | Updated | Excluded |
|---|---:|---:|---:|---:|
| heightsactivesinglelots909.csv | 35 | 35 | 0 | 0 |
| heightsactivesplitlots909.csv | 24 | 24 | 0 | 0 |
| heightspendingsinglelots909.csv | 4 | 4 | 0 | 0 |
| heightspendingsplitlots909.csv | 8 | 8 | 0 | 0 |
| heightssoldsinglelotslast180days.csv | 19 | 19 | 0 | 0 |
| heightssoldsplitlotslast180days.csv | 29 | 29 | 0 | 0 |
| **Total** | **119** | **119** | **0** | **0** |

**119/119 lot classifications agree**, derived from the supplied lot sizes; no mismatches. No duplicate input rows or active/pending conflicts occurred. The zero-row dropped ledger is `pulls/dropped_market_status_2026-09-09.csv` (header retained, gitignored with pulls/). Every excluded row would retain source filename/hash/row, MLS, address, reason and raw fields.

[First-run ingest counts and sold merge MLS lists](market-status-ingest-counts-2026-09-09.json). The second invoked `--apply` reported `changed_files: []`, all 119 unchanged; repeated checks hash every artifact and prove byte identity.

The snapshot retains MLS, dated status, Original List Price, close price/date, DOM, lot area/product, builder, all supplied agent/office fields, year built, address, coordinates, source hash and row. **Current asking price was not supplied** and remains null. No size or status was inferred.

## Sold archive union

The 180-day new-construction exports are **not** a superset of the 30-day all-sales exports. Five MLS numbers overlap: 35621139, 72560168, 85478626, 10396812, 88173016.

Against the larger existing 764-sale archive, **45 of 48 incoming sales already exist**. Of these, 41 gain corrected/enriched source fields and four remain unchanged. Three new transactions are added:

- MLS 89124616 — 1737 Tabor Street.
- MLS 88173016 — 826 Ralfallen Street.
- MLS 26903565 — 709 Ridge Street.

**764 + 3 = 767 sales. All 764 prior IDs remain; all 637 resale-comp objects remain exactly unchanged.** Identity is MLS, with normalized address + close date as a fallback; another closing date remains a separate transaction. Incoming metadata updates never replace the entire history with the 180-day subset.

826 Ralfallen and 709 Ridge omit building sqft. Their sales remain present with null sqft/$-per-sqft; the existing sold card now renders “Building size unavailable” instead of throwing. No lot sizes were backfilled.

## September 8 → September 9 active delta

41 prior rows → 59 current rows: **39 shared, 20 newly present, two absent**. September 9 is the authoritative input snapshot; the old September 8 display is retained only because Phase 4 is deferred.

- MLS 56131613 — **602 Jewett Street Unit B:** no supplied pending/sold match; disposition **unconfirmed**, not proven off-market.
- MLS 73224522 — **1822 W 23rd Street:** no supplied pending/sold match; disposition **unconfirmed**. It was already an explicit Heights OUT_OF_ZONE exclusion in the prior pull.

Absence under changed filters is not evidence of a sale, termination, or off-market disposition.

## Full reconciliation and all member lists

[Full 119-row table, every A–H member, Complete member breakdown and historical-sale candidates](market-status-reconciliation-2026-09-09.md) · [CSV table](market-status-reconciliation-2026-09-09.csv) · [Full JSON including all tracked properties](market-status-reconciliation-2026-09-09.json).

| Class | Count | Interpretation |
|---|---:|---|
| A | 4 | Complete with new-construction sale evidence |
| B | 13 | Complete and active |
| C | 5 | Complete and pending |
| D | 30 | Complete without matched market evidence; availability unverified |
| E | 0 | No confirmed current-build sale while unfinished |
| F | 19 | Prior tags contradict fresh/current evidence |
| G | 68 | 35 rows without a matched pin, plus 33 matched pins without construction phase |
| H | 26 | Under construction and active |

G is fully enumerated with year-built assessments. All 34 unmatched sold rows are 2025/2026 builds: construction-coverage gaps, not legitimate older resale explanations. The one unmatched active is also reported. Address matches without permits/phase are distinguished from completely missing properties.

Two historical resale matches are separately flagged, never treated as the current build being sold: **310 E 25th** (1920 house, sold December 16, 2025) and **2052 Columbia** (1941 house, sold September 30, 2025). Their current construction phases are Interior. Both remain “no market record” on the current-build axis.

H distribution: **Foundation 1, Framing 2, Exterior 1, MEP Roughs 1, Insulation 1, Interior 13, MEP Finals 7**. Early-stage members are 2434 White Oak and 2436 White Oak (Framing), and 845 W 23rd A (Foundation).

## Complete and supply scenario — review required

**52 = 4 sold + 13 active + 5 pending + 30 no market record.** Counts are represented homes, including named twins and explicitly labeled unidentified companions; a shared project phase does not certify each companion separately.

Requested arithmetic: **144 − 0 A − 0 C + 13 B + 30 D = 187**. A/C are already absent because Complete has null monthsLeft. No double addition/subtraction of existing Complete inventory occurs.

Three known pending members remain inside the original forecast: **314 W 21st, 1113 Voight, and 807 W 22nd**. Removing these too gives **187 − 3 = 184**. The original 144 remains live; neither scenario has been applied. D means no evidence in finite exports/archive, not verified unlisted/unsold, so treating all 30 as available is a scenario rather than a factual availability claim.

## Match-quality gate and display

Unique address-to-pin match: **84/119 (70.6%)**. Actual construction-phase coverage: **51/119 (42.9%)**. By status: active **39/59**, pending **9/12**, sold **3/48** have a construction phase.

**Phase 4 did not proceed.** Only three of 48 sold exports have construction-phase linkage, and no other-market exports were supplied. No eight-market market-status layer or new Complete status subdivisions were published. Legacy labels and September 8 active display remain historical and can still disagree; resolving that display is an open item, not claimed fixed. At the starting commit, Complete already had product checkboxes; the requested new disclosure structure is still deferred.

## Verification and deployment

[Commands, actual test logs, three-run hashes and protected-data checks](market-status-validation-2026-09-09.md).

- All three full checks: **20,706/20,706 phase cases; 173/173 browser checks; 7,283 base pairs, zero violations; zero page errors; identical results**.
- All three market checks: zero-change ingest, 119/119 classifications, all 767 sold-card invocations, four real popups; identical outputs.
- All **376 phase/ETA/weight tuples unchanged**. Harvard/629, Munford, 1033 Voight, 112 E 27th, 609 E 25th and 830 E 26th fixtures pass. 1113 Voight is a different property from the Interior fixture.
- DATA and RECONCILE byte-identical to 71033db. HTML diff: only three replaced lines. Deeds remain 139; sales 767.

Deployment uses committed main and Netlify CI only. Live validation command:

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --live https://tangerine-sorbet-eca5f5.netlify.app
```

It verifies exact live inline scripts, external active JS and snapshot bytes (Netlify rewrites navigation URLs) and Tabor, 902 E 25th (Complete/active), 826 Ralfallen (Complete/sold), and 1623 Blount (Complete/no market record). All three live runs passed with identical SHA256 `532f683313eecbd679dd7da6105747f8c43e270a26d66f3afbdbbbbe267a03ee`; full output is recorded in the validation report.

## Open review items

1. Confirm whether 119 is the intended complete input set or supply the missing 40 referenced rows.
2. Resolve G construction coverage and paired-member evidence before enabling Phase 4. Do not infer completion from marketing labels.
3. Review both supply scenarios, particularly the availability assumption for D and the three unfinished pending members.
4. Resolve the two missing prior actives' disposition with additional evidence.
5. Review 19 stale-tag conflicts, especially Tabor; original tags remain retained, not silently erased.
6. Keep historical resale transactions distinct from current-build sales; no record retirement is authorized by a conflict.

To reproduce the ingest locally with the original supplied CSVs:

```sh
/Users/nemoclaw/insp-venv/bin/python -B market_status_ingest.py --runtime docs/market-status-baseline-2026-09-09.json
/Users/nemoclaw/insp-venv/bin/python -B market_status_ingest.py --runtime docs/market-status-baseline-2026-09-09.json --apply
```
