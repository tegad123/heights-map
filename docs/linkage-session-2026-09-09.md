# Heights linkage, listing history, and terminated listings — 2026-09-09

Implemented independent market status on all eight pages. Construction and timeline scripts, DATA, RECONCILE, and classification tags are unchanged. The supply snapshot is 128 after excluding three terminated members from the unchanged 131-home construction forecast.

## Phase 0 — diagnosis reported before matching changes

The initial read-only invocation was `/Users/nemoclaw/insp-venv/bin/python -B /tmp/linkage_diagnosis.py`, using a fresh Chromium capture from `/tmp/market_capture.py --output /tmp/market-runtime.json`. The committed reproduction is:
```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/linkage_diagnosis.py
```

Actual output (the complete row ledger is [linkage-phase0-2026-09-09.json](linkage-phase0-2026-09-09.json)):
```json
{
  "rows": 284,
  "new_lot_matches": 165,
  "taxonomy": {
    "LINKED": 230,
    "CONFLICTING_NEARBY_IDENTITY": 10,
    "NOT_TRACKED": 22,
    "HIDDEN_LEGACY_SOLD": 22
  },
  "prior": {
    "rows": 119,
    "linked": 84,
    "with_phase": 51
  },
  "source_records": 430,
  "runtime_pins": 376,
  "runtime_members": 407,
  "mls_records": 0,
  "parcel_records": 0,
  "proximity": {
    "single": 10,
    "ambiguous": 4,
    "nearest_distribution": {
      "0-25m": 14,
      ">100m": 22,
      "50-100m": 9,
      "25-50m": 9
    }
  },
  "active_mls_sets_equal": true,
  "terminated_active_overlap": 0,
  "terminated_years": {
    "2026.0": 75,
    "2025.0": 29,
    "2024.0": 1,
    "2027.0": 1
  },
  "terminated_median_dom": 38.0
}
```

**D1: original join and normalizer.** The old matcher tried only normalized address; no MLS, APN or coordinate fallback. It indexed rendered pins and their `_twin` members:
```python
for pin in runtime['raw']:
    for member in [pin] + ([pin['_twin']] if pin.get('_twin') else []):
        lookup[address_key(member['a'])].append((pin, member))
matches = lookup[rec['address_key']]

def address_key(address):
    """Keep unit/fraction identity; canonicalize directional placement on numbered streets."""
    s = str(address).lower().split(',')[0]
    s = re.sub(r'\b(?:houston|tx|texas|77\d{3})\b.*', '', s)
    s = re.sub(r'\b(?:unit|apt)\s*#?\s*|#', ' ', s)
    s = re.sub(r'(?<=\d)-?([a-f])\b', r' \1', s)
    s = re.sub(r'\b(\d+)\s+(st|nd|rd|th)\b', r'\1\2', s)
    s = re.sub(r'[^a-z0-9/ ]', ' ', s)
    aliases = dict(street='st',avenue='ave',lane='ln',drive='dr',road='rd',court='ct',place='pl',boulevard='blvd',east='e',west='w',north='n',south='s')
    w = [aliases.get(x,x) for x in s.split()]
    if len(w)>2 and w[0].isdigit() and w[1] in 'abcdef' and len(w[1])==1 and w[1] not in ('e','w'):
        w.append(w.pop(1))
    if len(w)>3 and w[1] in ('e','w','n','s') and re.match(r'^\d',w[2]):
        w.append(w.pop(1))
    w = [x for i,x in enumerate(w) if not (i and x == w[i-1] and x in ('st','ave','ln','dr','rd','ct','pl','blvd'))]
    return ' '.join(w)
```

**D2: failure taxonomy.** All counts are source rows, including the intentionally repeated 59 active observations. They are not unique-home counts.

| Category | Rows | Examples |
|---|---:|---|
| Existing normalized-address join | 230 | 715 Merrill, 902 E 25th |
| Exact address exists in DATA but legacy sold flag removes it at startup | 22 | 1119 E 7th 1/2; 2612 Greenleaf; 1321 Alexander |
| No exact address; nearby candidate identity conflicts | 10 | 1111 E 27th versus 1107; 1208 E 26th B versus A |
| No exact address or candidate within 25 m | 22 | 1737 Tabor; 1023 E 23rd; 1430 Nashua |
| Proven recoverable normalization failures in these supplied rows | 0 | A latent fractional-street bug was found by invocation, below |
| Ambiguous exact normalized-address matches | 0 | — |

The 22 hidden rows represent 15 retained source identities. Startup uses `DATA = DATA.filter(r=>r.st!=='sold')`. Those records remain retained and hidden, with review flags; this repair does not relist, delete, retire, or restore them. Every failed or hidden join, with candidates and distances, is in [linkage-review-2026-09-09.json](linkage-review-2026-09-09.json).

**D3:** 430 source DATA records; zero MLS fields; zero parcel/APN/account fields. The runtime has 376 pins and 407 named members. Missing MLS is universal, not a mutually exclusive cause for the 54 runtime failures.

**D4:** Of 54 runtime-unlinked rows, 14 have a candidate within 25 m: 10 exactly one, four multiple. Nearest-distance bins are 14 at 0–25 m, 9 at 25–50 m, 9 at 50–100 m, and 22 beyond 100 m. A 0.02 m A/B collision proves that even a single candidate does not establish identity. No conflicting nearby identity is accepted.

**D5:** 715 Merrill is `act_715-merrill`, permit 25049520, Complete. It already matched MLS 88557637 and was also in the older active popup snapshot. Its missing Complete-category indicator was a missing market display axis, not a failed address join. 931 Merrill is `pmt_931-merrill-st-77009`, permit 25053903, Complete; it has no row in the provided exports or 767-comp archive. The client-provided 2026-02-26 sale is outside the 180-day export, and was not inserted without source evidence.

## Linkage repair and measured rates

| Measure | Before | After |
|---|---:|---:|
| All 284 rows linked to source identities | 230 / 284 (81.0%) under old runtime-only matcher | 252 / 284 (88.7%) |
| All rows linked to rendered members | 230 / 284 | 230 / 284 |
| All rows linked to an evidenced construction phase | 138 / 284 (48.6%) | 138 / 284 (48.6%) |
| Original 119 rows linked | 84 / 119 (70.6%) | 99 / 119 (83.2%) |
| Original 119 rows with evidenced construction phase | 51 / 119 (42.9%) | 51 / 119 (42.9%) |

The reported 43% baseline was construction-evidence coverage, not the address-link rate. No construction evidence was invented to raise that number. The 22 recovered source joins do not create markers or certify stages.

| Method, all 284 rows | Matches |
|---|---:|
| MLS | 0 (DATA has no MLS) |
| Normalized address | 252 |
| Coordinate fallback | 0 accepted |
| Unlinked | 32 |

| Source status | Input rows | Source joins | Rendered joins |
|---|---:|---:|---:|
| Active, including repeated 365-day pull | 118 | 116 | 116 |
| Pending | 12 | 12 | 12 |
| Sold | 48 | 29 | 14 |
| Terminated | 106 | 95 | 88 |

Order is MLS, normalized address, then a single candidate within 25 m with no house-number, unit, directional, or fractional-street conflict. Every join stores its method. The market-only normalizer protects fractions before ordinal folding: an invoked test demonstrated that the old `1/2 St` became `1/2st`, unlike `1/2 Street`. Tests now prove equivalent variants join, and different units/fractional streets remain distinct. Other ingest engines were not changed.

**Display decision:** 88.7% source identity linkage, 58/59 active listings rendered and 12/12 pending rendered support the independent market axis. Sold construction coverage is still limited and is explicitly not represented as phase coverage. Hidden source records remain hidden. Other markets show that no market-status export was supplied.

## Listing histories and terminated ingest

284 observations contain 225 distinct MLS/status records. The repeated 59 active rows are recorded as DUP_INPUT; no distinct terminated history is dropped as a duplicate property/status. All 165 new lot classifications agree with their source files. Active MLS sets match exactly, terminated/active MLS overlap is zero, terminated year-built counts are 75 (2026), 29 (2025), one (2024), one (2027), and median DOM is 38.

225 records resolve to 134 properties: 59 Active, 12 Pending, 48 Sold, and 15 Terminated. **58 properties have multiple listings.** Histories retain MLS, DOM, source provenance, original price, and available dates. Current status uses the requested sold-with-close-date > pending > active > terminated order; later available dates win within a status. Same-status records without event dates are not presented as proven chronological order.

106 terminated rows represent 70 properties: **30 resolve Active, 16 Sold, nine Pending, 15 Terminated**. These are cross-status resolutions, not claims that the exports contain dates proving each later event. Eleven of the 15 currently terminated properties have rendered cards; four are untracked. The other 55 properties retain failed-listing history without being counted as terminated today.

715 Merrill hard fixture: **Active MLS 88557637, 8 DOM**, with **terminated MLS 50361472, 174 DOM** visible in prior history, and **Complete** construction on the same card. The snapshot supplies Original List Price $2,099,900; it is not labelled as current asking price.

The three unresolved same-status ordering cases are:
- 1520 W 21st St Unit#B: 91497078, 53880556
- 1430 Nashua Street: 88928845, 62838228, 6048401
- 1522 W 21st St: 64033189, 43902226

## Complete breakdown and residual no-market-record list

Heights: **13 Active + 5 Pending + 4 Sold + 3 Terminated + 24 No Market Record = 49 homes**. The three newly explained Complete homes are 1520 W 21st B, 833 W 25th, and 607 W 27th. The older report had 30 no-record homes; the pre-session Custom classifications removed three from this category, leaving the client’s 27. Terminated evidence explains three more, leaving 24.

| Market | Active | Pending | Sold | Terminated | No Market Record |
|---|---:|---:|---:|---:|---:|
| Heights | 13 | 5 | 4 | 3 | 24 |
| Montrose | 0 | 0 | 0 | 0 | 21 |
| River Oaks | 0 | 0 | 0 | 0 | 0 |
| Spring Branch | 0 | 0 | 0 | 0 | 33 |
| Spring Valley | 0 | 0 | 0 | 0 | 0 |
| Timbergrove | 0 | 0 | 0 | 0 | 10 |
| West University | 0 | 0 | 0 | 0 | 3 |
| Garden Oaks / Oak Forest | 0 | 0 | 0 | 0 | 34 |

Non-Heights no-record counts mean no supplied export, not confirmed unlisted homes. All eight pages include the axis and Complete subentries. HAR lot classes drive the market axis; existing construction-product grouping is preserved for its Complete subentries. At 122 E 4th, HAR says Single Lot while the existing construction grouping is Split Lot/two represented homes. This source discrepancy remains for review.

Full residual Heights list (21 named members and three unnamed represented homes):

- 118 E 23rd St, Houston, Tx 77008
- 1623 Blount St, Houston, TX 77008
- 1343 Nashua St, Houston, TX 77008
- 2013 Sheldon St B, Houston, TX 77008
- 737 W 21st St C, Houston, TX 77008
- 737 W 21st St B, Houston, TX 77008
- 737 W 21st St A, Houston, TX 77008
- 737 W 21st St D, Houston, TX 77008
- 729 W 21st St A, Houston, TX 77008
- 723 W 21st St, Houston, TX 77008
- 725 W 21st St, Houston, TX 77008
- 729 W 21st St B, Houston, TX 77008
- 1432 Alexander St, Houston, TX 77008
- 112 E 27th St A, Houston, TX 77008
- 729 W 21st St C, Houston, TX 77008
- 2811 Ave, Houston, TX 77009
- 1301 Tabor St, Houston, TX 77009
- 1107 E 24th St, Houston, TX 77009
- 1109 E 24th St, Houston, TX 77009
- 409 Walton St A, Houston, TX 77009
- 931 Merrill St, Houston, TX 77009
- Unidentified represented home 1 at 122 E 4th Street
- Unidentified represented home 1 at 1208 E 26th Street Unit#A
- Unidentified represented home 1 at 335 Harvard Street

## Supply snapshot arithmetic

Before writing display code, the reported arithmetic was:
```text
131 construction-forecast homes − 3 terminated named members = 128 snapshot homes
131 − 3 terminated − 3 pending = 125 (not applied)
125 + 13 Complete actives = 138 (not applied)
```

The three deducted homes are 1109 Voight, 949 Ridge, and 1109 Tabor. The snapshot wrapper makes only that three-member deduction. `comingOnline`, supply curves, construction phase derivation, and timeline models are unchanged. The three pending members still in the construction forecast are 314 W 21st, 1113 Voight, and 807 W 22nd (paired under 805 W 22nd); broader availability policy remains an open item. No Market Record is not proof of available supply.

## Sold-window recommendation — report only

931 Merrill’s client-confirmed 2026-02-26 closing is 195 days before the 2026-09-09 export date. A **12-month pull beginning 2025-09-09** covers that date and all currently evidenced Complete anchors (earliest 2025-12-10). A **24-month pull beginning 2024-09-09** is the better coverage backfill for older builds and listing history. The tracked permit set includes 2022 and 2023 projects, so neither fixed window guarantees coverage of every historical build; those require targeted older closing histories if still unresolved.

For the original 27 unexplained Complete homes: three now resolve through terminated evidence; 931 is **one known potential additional resolution under either 12 or 24 months**, based on the client’s supplied sale fact. The remaining 20 named no-record properties have no closing evidence in the inputs; no defensible numerical forecast can distinguish how many a 12-month versus 24-month pull will resolve. Three residual entries also need per-home addresses before reliable matching. The existing archive already spans beyond 12 months yet lacks 931, so export filters/coverage matter as well as duration. No HAR export was run and no sale was fabricated or added.

## Invoked validation and actual results

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/full_timeline_check.py
```
```text
RUN 1: phase 20706/20706; browser 183/183; base pairs 7283, violations 0; page errors []; SHA256 01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a
RUN 2: phase 20706/20706; browser 183/183; base pairs 7283, violations 0; page errors []; SHA256 01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a
RUN 3: phase 20706/20706; browser 183/183; base pairs 7283, violations 0; page errors []; SHA256 01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a
PASS: all three full results byte-identical
```

Fixtures passed: Harvard target 2027-05-14 (~8 months), three weeks overdue; 629 target 2027-03-28 (~6.5 months); Munford and both Voight fixtures interior; 112 E 27th and 609 E 25th Complete; 830 E 26th no phase or ETA. All 376 runtime phase/ETA/weight tuples match the pre-change capture.

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --three
/Users/nemoclaw/insp-venv/bin/python -B tests/market_status_check.py --live https://tangerine-sorbet-eca5f5.netlify.app --three
```

The market runs invoke `market_status_ingest.py --apply` each time. Raw invoked output is preserved in [the local market log](linkage-market-local-2026-09-09.txt), [the live market log](linkage-market-live-2026-09-09.txt), and [the full construction-suite log](linkage-full-check-2026-09-09.txt). Actual repeated output:
```text
PASS --apply: zero changes; 284 rows; 165/165 new lot classifications; all file hashes identical
PASS all eight DATA/RECONCILE regions and inline construction/timeline scripts byte-identical to 2bb69f5
SPOT act_715-merrill active ["88557637", "8 days", "50361472", "174 DOM", "COMPLETE"]
SPOT act_1520-w-21st-st-unit-b terminated ["Terminated / Expired", "COMPLETE"]
SPOT act_902-e-25 active ["Active", "COMPLETE"]
SPOT pmt_931-merrill-st-77009 no_record ["No Market Record", "COMPLETE"]
RUN 1 SHA256 7075283331bbeaf06ef60e7ea23024301e159d2def3cafbf227e99b2e637f956
RUN 2 SHA256 7075283331bbeaf06ef60e7ea23024301e159d2def3cafbf227e99b2e637f956
RUN 3 SHA256 7075283331bbeaf06ef60e7ea23024301e159d2def3cafbf227e99b2e637f956
PASS all runs identical
```

Custom 19 / Sold Off Market 1; deeds 139; sold comps 767; no sold additions. All popup builders and market-filter predicates are invoked across all eight pages. The final filter checks also assert each Complete subtotal agrees with its parent construction-product count.

`git diff --stat -- "*.html"` before committing returned:
```text
 gardenoaksoakforest.html | 1 +
 index.html               | 2 +-
 montrose.html            | 1 +
 riveroaks.html           | 1 +
 springbranch.html        | 1 +
 springvalley.html        | 1 +
 timbergrove.html         | 1 +
 westu.html               | 1 +
 8 files changed, 8 insertions(+), 1 deletion(-)
```

`git diff --check` and `node --check market_status.js` exited 0 with no output. These HTML changes are only external-script references; byte comparisons explicitly protect DATA and all inline scripts.

## Deployment and open review items

Backend commit: `49cb019`. Initial display commit: `4eedff7`. Complete-product subtotal correction: `29e524e`. `git show --format=fuller --stat HEAD` and `git ls-tree --name-only HEAD ...` verified the committed files, including all eight HTML files, before `git push origin main`. Initial push output:
```text
To https://github.com/tegad123/heights-map.git
   2bb69f5..4eedff7  main -> main
```

Netlify rebuilt from GitHub; the live checks compare every page’s scripts and the shared JS/snapshot byte-for-byte. No direct deploy API or empty rebuild trigger was needed.

- Review the 15 hidden legacy-sold identities and 32 unmatched source rows (including repeated observations). No deletion, retirement, or restoration was performed.
- The one untracked active is 1111 E 27th; its nearest pin is 1107 E 27th at 12.27 m. That is a conflicting house number, not authority to attach it.
- Obtain event dates for the three flagged same-status ordering cases; current asking prices are not supplied.
- Resolve the 122 E 4th HAR-versus-construction product discrepancy and three unnamed Complete members without changing reliable construction evidence.
- Obtain the wider sold exports and exports for the other seven markets; decide whether the supply snapshot should also exclude known pending members or include Complete actives.
- Source input CSVs remain untracked and were not committed. Scrapers, permit ingests, phase logic, timeline logic, RECONCILE, and inventory classifications were not modified.
