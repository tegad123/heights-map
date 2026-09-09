# Heights sold refresh — 2026-09-08

712 → 764 HAR sold transactions; 52 added, 2 updated, 2 excluded. 761 unique property pins. Source classification cross-check: 56/56 agree.

## Phase 0: discovery and schema resolution

Read-only commands: `git status --short --branch`, `git diff -- deed_ingest.py`, `git log -4 --format='%h %ai %s' -- deed_ingest.py`, `cat sold_ingest.py`, Python AST/CSV header comparison and JSON decoding of all eight market pages; `rg -n --max-columns 250 'const SOLD|let SOLD|closed sales|SOLD_DATA|Sold Comps' --glob '*.html' --glob '!index.html'`.

Deed code was committed in `7b6556f`, followed by data commit `c750005`; its diff was empty. No deed file was changed.

Both exports matched every expected column: `33 rows missing []` and `23 rows missing []`. UTF-8 BOM and CRLF already work with `utf-8-sig` and `newline=''`.

Required: MLS Number, Address, Latitude, Longitude, Close Price, Building SqFt, Close Date. Positive price and building area required. Dates: `%m/%d/%Y`, `%Y-%m-%d`, `%m/%d/%y`. Optional: Original List Price, Lot Size, DOM, Year Built, Builder Name, School Elementary, List Agent Full Name, Selling Agent Full Name.

Originally unused columns (identical in both files): Co List Team Name, Co Selling Agent Full Name, Co Selling Office Name, County, List Office Name, Master Planned Community, Price Sq Ft Sold, School District, Selling Office Name, Subdivision. `Price Sq Ft Sold` is now retained as `har_psf`; the other nine remain outside the existing sold schema.

The old filenames described year-built cohorts, whereas the new filenames describe product queries. Cohort now derives from Year Built (2025+ → nc, earlier → resale); product derives independently from lot size. No input file was edited.

The old parsing implementation, read before changes:

```python
def money(s):
    s = str(s or '').replace('$', '').replace(',', '').strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def intval(s):
    v = money(s)
    return int(round(v)) if v is not None else None


def parse_close(s):
    s = str(s or '').strip()
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None



    for path, cohort in cfg['csvs']:
        with open(path, encoding='utf-8-sig', newline='') as f:
            for rec in csv.DictReader(f):
                mls = (rec.get('MLS Number') or '').strip()
                if not mls:
                    continue
                if mls in seen:
                    dupes += 1
                    continue
                seen.add(mls)
                addr = (rec.get('Address') or '').strip()
                lat = money(rec.get('Latitude'))
                lng = money(rec.get('Longitude'))
                cp = intval(rec.get('Close Price'))
                lp = intval(rec.get('Original List Price'))
                sq = intval(rec.get('Building SqFt'))
                cd = parse_close(rec.get('Close Date'))
                if not (addr and lat and lng and cp and sq and cd):
                    bad.append((mls, addr))
                    continue
                # zone guard, pipeline level (same as permit_pull.py)
                if zone_re.search(addr):
                    excl_zone.append(addr)
                    continue
                if lng > lng_max:
                    excl_lng.append(addr)
                    continue
                if not in_zone_poly(ring, lng, lat):
                    excl_poly.append(addr)
                    continue
                lot = intval(rec.get('Lot Size'))
                dom = intval(rec.get('DOM'))
                days = (today - cd).days
                if days < 0:
                    days = 0
                unit_letter = bool(UNIT_LETTER_RE.search(addr))
                if not lot:
                    prod, review = 'Unclassified', True
                elif lot <= SPLIT_MAX:
                    prod, review = 'Split Lot', False
                elif lot >= SINGLE_MIN:
                    # unit-letter address on a full-size lot: HAR likely reports the
                    # PARENT lot on a shared-lot unit — keep Single but flag for review
                    prod, review = 'Single Lot', unit_letter
                else:
                    prod, review = 'Unclassified', True  # 4,000-5,000 ambiguity gap
                row = {
                    'id': 's' + mls,
                    'a': addr,
                    'lat': round(lat, 7), 'lng': round(lng, 7),
                    'cp': cp, 'lp': lp, 'sq': sq,
                    'psf': round(cp / sq, 1),
                    'cd': cd.isoformat(), 'mo': cd.strftime('%Y-%m'),
                    'dom': dom, 'yb': intval(rec.get('Year Built')),
                    'coh': cohort, 'band': band_of(cp), 'win': win_of(days),
                    'prod': prod,
                }
                if lot: row['lot'] = lot
                if lp: row['svl'] = round((cp - lp) / lp, 4)
                if dom == 0: row['p'] = 1          # presold new construction — signal, not junk
                if review: row['nr'] = 1            # needs_review: null/gap lot, or letter-address Single
                for k, col in (('bl', 'Builder Name'), ('sch', 'School Elementary'),
                               ('la', 'List Agent Full Name'), ('ba', 'Selling Agent Full Name')):
                    v = (rec.get(col) or '').strip()
                    if v: row[k] = v
                rows.append(row)

```

The old script emitted `sold_emit.txt`, manually spliced into `index.html` as separate `SOLD_DATA` and `SOLD_METRICS` constants. The Sold Comps layer/dashboard reads those constants, not hand-authored DATA. The supply snapshot read legacy `SOLD.length` (21) and now reads `SOLD_DATA.length` (764). The old MARKET_METRICS snapshot of 103 is explicitly identified as historical 2026-07-05 in ASK context, not current totals.

Existing SOLD_DATA: 712 rows, 704 usable `lot` values. Old labels: Single Lot 324, Split Lot 324, Unclassified 64. Old rules were ≤4000 Split, ≥5000 Single, otherwise Unclassified. The new rules are ≥4000 Single, ≥2000 and <4000 Split, nonzero <2000 Unclassified, missing/zero/unparseable Unknown. Negative values are not treated as valid classified lots. Boundary tests: 4000, 3999, 2000, 1999, zero, None, bad text, comma-formatted 4000, NaN: 9/9 PASS.

`prodKeyR()` reads stored prod/ty and shared tags; the UI allows manual edits. Historical permit chain, unit-letter and area classifications were supplemented by HCAD geometry corrections, documented in `docs/split-classification-notes.md`. There is no live geometry computation in that function. Browser audits below use repository seed state with remote shared edits intercepted, so uncommitted remote user overrides are not audited.

## Dry run (full actual output, before data apply)

Command: `/Users/nemoclaw/insp-venv/bin/python -B sold_ingest.py --dry-run --as-of 2026-09-08`

```json
{
  "mode": "DRY RUN",
  "as_of": "2026-09-08",
  "files": [
    {
      "file": "Heightssoldsinglelotslast30days.csv",
      "read": 33,
      "added": 30,
      "updated": 1,
      "excluded": {
        "MISSING_REQUIRED_FIELD": 2
      },
      "crosscheck_matches": 33
    },
    {
      "file": "Heightssoldsplitlotslast30days.csv",
      "read": 23,
      "added": 22,
      "updated": 1,
      "excluded": {},
      "crosscheck_matches": 23
    }
  ],
  "old_total": 712,
  "new_total": 764,
  "products": {
    "Single Lot": 411,
    "Split Lot": 289,
    "Unclassified": 56,
    "Unknown": 8
  },
  "crosscheck_mismatches": [],
  "flagged": [
    {
      "id": "s38531074",
      "address": "415 W 16th Street Unit#D",
      "lot": 1808,
      "product": "Unclassified"
    },
    {
      "id": "s92874787",
      "address": "1708 Ashland Street",
      "lot": 1696,
      "product": "Unclassified"
    },
    {
      "id": "s13973985",
      "address": "732 W 17th Street",
      "lot": 1900,
      "product": "Unclassified"
    },
    {
      "id": "s4582337",
      "address": "1202 W 16th Street Unit#C",
      "lot": 1757,
      "product": "Unclassified"
    },
    {
      "id": "s3196281",
      "address": "1007 E 28th Street",
      "lot": 1688,
      "product": "Unclassified"
    },
    {
      "id": "s92057150",
      "address": "1207 E 24th Street Unit#A",
      "lot": 1987,
      "product": "Unclassified"
    },
    {
      "id": "s82968775",
      "address": "904 W 25th Street Unit#D",
      "lot": 1747,
      "product": "Unclassified"
    },
    {
      "id": "s44955770",
      "address": "2409 Bevis Street",
      "lot": 1630,
      "product": "Unclassified"
    },
    {
      "id": "s89661396",
      "address": "411 W 17th Street Unit#C",
      "lot": 1525,
      "product": "Unclassified"
    },
    {
      "id": "s51365389",
      "address": "2407 Bevis Street",
      "lot": 1630,
      "product": "Unclassified"
    },
    {
      "id": "s38400412",
      "address": "415 W 16th Street Unit#B",
      "lot": 1529,
      "product": "Unclassified"
    },
    {
      "id": "s56515043",
      "address": "621 Rutland Street Unit#D",
      "lot": 1600,
      "product": "Unclassified"
    },
    {
      "id": "s15873888",
      "address": "1034 W 17th Street Unit#E",
      "lot": 1601,
      "product": "Unclassified"
    },
    {
      "id": "s41813835",
      "address": "521 W 22nd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s84476590",
      "address": "1403 W 21st St Unit#B",
      "lot": 1925,
      "product": "Unclassified"
    },
    {
      "id": "s98028179",
      "address": "1122 W 17th Street Unit#E",
      "lot": 1756,
      "product": "Unclassified"
    },
    {
      "id": "s57714605",
      "address": "621 Rutland Street Unit#A",
      "lot": 1900,
      "product": "Unclassified"
    },
    {
      "id": "s72552965",
      "address": "912 W 19th Street Unit#C",
      "lot": 1693,
      "product": "Unclassified"
    },
    {
      "id": "s57916930",
      "address": "1122 W 17th Street Unit#D",
      "lot": 1756,
      "product": "Unclassified"
    },
    {
      "id": "s71522503",
      "address": "2916 Michaux Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s25084620",
      "address": "1106 W 12th Street",
      "lot": 1917,
      "product": "Unclassified"
    },
    {
      "id": "s25834381",
      "address": "1114 W 15th Street",
      "lot": 1600,
      "product": "Unclassified"
    },
    {
      "id": "s30213229",
      "address": "1003 E 28th Street",
      "lot": 1812,
      "product": "Unclassified"
    },
    {
      "id": "s70120584",
      "address": "1020 W 15th 1/2 Street Unit#A",
      "lot": 1745,
      "product": "Unclassified"
    },
    {
      "id": "s8506478",
      "address": "1403 W 21st St Unit#A",
      "lot": 1589,
      "product": "Unclassified"
    },
    {
      "id": "s19205728",
      "address": "2213 Bevis Street",
      "lot": 1969,
      "product": "Unclassified"
    },
    {
      "id": "s59083207",
      "address": "1236 W 21st Street",
      "lot": 1671,
      "product": "Unclassified"
    },
    {
      "id": "s67455121",
      "address": "704 W 8th Street",
      "lot": 1406,
      "product": "Unclassified"
    },
    {
      "id": "s32780196",
      "address": "2505 Couch Street Unit#A",
      "lot": 1960,
      "product": "Unclassified"
    },
    {
      "id": "s63496941",
      "address": "2932 Michaux Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s61894487",
      "address": "1149 W 22nd Street",
      "lot": 1753,
      "product": "Unclassified"
    },
    {
      "id": "s39369334",
      "address": "725 Dorothy Street",
      "lot": 1428,
      "product": "Unclassified"
    },
    {
      "id": "s35385701",
      "address": "1031 Ashland Street",
      "lot": 1570,
      "product": "Unclassified"
    },
    {
      "id": "s60649491",
      "address": "712 W 22nd Street Unit#B",
      "lot": 1900,
      "product": "Unclassified"
    },
    {
      "id": "s13341494",
      "address": "907 W 16th Street Unit#A",
      "lot": 1749,
      "product": "Unclassified"
    },
    {
      "id": "s25632612",
      "address": "1053 W 15th 1/2 Street",
      "lot": 1948,
      "product": "Unclassified"
    },
    {
      "id": "s55845584",
      "address": "1415 W 21st Street Unit#A",
      "lot": 1813,
      "product": "Unclassified"
    },
    {
      "id": "s74251844",
      "address": "730 W 17th Street",
      "lot": 1900,
      "product": "Unclassified"
    },
    {
      "id": "s21439171",
      "address": "1505 W 23rd Street Unit#D",
      "lot": 1787,
      "product": "Unclassified"
    },
    {
      "id": "s28426564",
      "address": "1633 Beall Street",
      "lot": 1726,
      "product": "Unclassified"
    },
    {
      "id": "s35662209",
      "address": "1530 Yale Street Unit#A",
      "lot": 1822,
      "product": "Unclassified"
    },
    {
      "id": "s37163800",
      "address": "1139 W 22nd Street",
      "lot": 1753,
      "product": "Unclassified"
    },
    {
      "id": "s22459966",
      "address": "1219 W 25th Street Unit#A",
      "lot": 1887,
      "product": "Unclassified"
    },
    {
      "id": "s59376489",
      "address": "242 E 28th Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s55821001",
      "address": "323 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s43181987",
      "address": "911 W 25th Street Unit#B",
      "lot": 1800,
      "product": "Unclassified"
    },
    {
      "id": "s21040862",
      "address": "2219 Bevis Street",
      "lot": 1969,
      "product": "Unclassified"
    },
    {
      "id": "s88903779",
      "address": "2211 Bevis Street",
      "lot": 1969,
      "product": "Unclassified"
    },
    {
      "id": "s56615515",
      "address": "2215 Bevis Street",
      "lot": 1969,
      "product": "Unclassified"
    },
    {
      "id": "s30124484",
      "address": "1129 W 21st Street",
      "lot": 1868,
      "product": "Unclassified"
    },
    {
      "id": "s15221728",
      "address": "1210 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s4927335",
      "address": "712 W 22nd Street Unit#D",
      "lot": 1900,
      "product": "Unclassified"
    },
    {
      "id": "s4197682",
      "address": "325 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s39081009",
      "address": "1801 Ashland Street",
      "lot": 1980,
      "product": "Unclassified"
    },
    {
      "id": "s31845908",
      "address": "513 E 4th Street",
      "lot": 1782,
      "product": "Unclassified"
    },
    {
      "id": "s52201670",
      "address": "1631 Beall Street",
      "lot": 1726,
      "product": "Unclassified"
    },
    {
      "id": "s89770702",
      "address": "604 W 28th Street Unit#A",
      "lot": 1615,
      "product": "Unclassified"
    },
    {
      "id": "s89389635",
      "address": "2221 Bevis Street",
      "lot": 1969,
      "product": "Unclassified"
    },
    {
      "id": "s77272535",
      "address": "602 W 28th Street Unit#B",
      "lot": 1615,
      "product": "Unclassified"
    },
    {
      "id": "s68488073",
      "address": "608 W 28th Street Unit#C",
      "lot": 1455,
      "product": "Unclassified"
    },
    {
      "id": "s63715206",
      "address": "602 W 28th Street Unit#A",
      "lot": 1740,
      "product": "Unclassified"
    },
    {
      "id": "s47467677",
      "address": "905 W 16TH Street Unit#B",
      "lot": 1749,
      "product": "Unclassified"
    },
    {
      "id": "s16275355",
      "address": "1216 W 23rd Street",
      "lot": null,
      "product": "Unknown"
    },
    {
      "id": "s78756510",
      "address": "1611 W 22nd Street Unit#C",
      "lot": 1718,
      "product": "Unclassified"
    }
  ],
  "html_changed": true,
  "ledger_rows": 2
}
```

## Ingest accounting and captured fields

| Source | Read | Added | Updated | Excluded |
|---|---:|---:|---:|---:|
| Single-lot export | 33 | 30 | 1 | 2 missing Building SqFt |
| Split-lot export | 23 | 22 | 1 | 0 |

Excluded: MLS 88173016, 826 Ralfallen Street, 5000 sqft lot, $1,655,000; MLS 10313088, 824 Cortlandt Street, 6600 sqft lot, $1,700,000. Both have empty Building SqFt and Price Sq Ft Sold. No missing lot sizes in either export. No out-of-market or missing-geocode exclusions in this run. All 56 rows, including both exclusions, passed the independent product/source cross-check (33 Single, 23 Split; zero Unclassified or Unknown).

MLS is the primary transaction identity; normalized address plus close date is the fallback. Existing transactions at 811 Redan Street, 1109 Rutland Street, and 1026 Allston Street each have two dates, and remain separate sales. Rendering deduplicates the property pin while historical cards open the selected closing. Executed ID-set assertion: all 712 old transaction IDs retained. Updated MLS records are s42235659 (1205 Temple Street) and s97528053 (217 W 10th Street).

Ledger: `pulls/dropped_sold_2026-09-08.csv` (gitignored, dedicated sold ledger so permit/deed ledger schemas cannot collide). Every exclusion has source filename, SHA256, CSV row number, MLS, address, reason, and full raw JSON. First apply logged two missing-required rows; second apply also logged the 54 duplicate rows, with stable deduplication of ledger entries on later reruns. No silent drops.

Captured: Builder Name → `bl`; DOM → `dom`; Original List Price → `lp`; Close Price → `cp`; source Price Sq Ft Sold → new `har_psf`. Existing `psf` stays the recomputed close-price/building-area value, preserving prior display and metrics. Lot Size → `lot`; classification → `prod`; normalized property identity → `ak`. Year Built, school, listing and selling agents remain retained. Executed source-field comparison: 54 accepted rows × 5 requested fields = 270/270 PASS; 10 accepted rows have nonempty Builder Name. The complete raw data for both excluded records is in the ledger; their builder/price information is not inserted into map records.

## Per-market post-ingest counts

HAR Sold Comps exists only in Heights. No new sold layer was created in the other markets. Legacy hidden `st=sold` records inside DATA are a separate collection and were not classified or changed in this session.

| Market | HAR total | Single | Split | Unclassified | Unknown | Legacy DATA sold (unchanged) |
|---|---:|---:|---:|---:|---:|---:|
| Heights | 764 | 411 | 289 | 56 | 8 | 21 |
| Montrose | N/A | N/A | N/A | N/A | N/A | 2 |
| River Oaks | N/A | N/A | N/A | N/A | N/A | 0 |
| Spring Branch | N/A | N/A | N/A | N/A | N/A | 0 |
| Spring Valley Village | N/A | N/A | N/A | N/A | N/A | 0 |
| Timbergrove/Lazybrook | N/A | N/A | N/A | N/A | N/A | 0 |
| West University | N/A | N/A | N/A | N/A | N/A | 1 |
| Garden Oaks/Oak Forest | N/A | N/A | N/A | N/A | N/A | 359 |

The full 64-address Unknown/Unclassified log is in the dry-run JSON above (all pre-existing records). No external lot-size backfill was attempted.

## Product-mechanism conflicts (unchanged)

Matched sold addresses versus current stored construction-side product labels:

| Address | Sold lot sqft | Sold label | Stored construction label |
|---|---:|---|---|
| 308 E 28th Street | 3000 | Split Lot | Single Lot |
| 1125 E 24th Street | 3000 | Split Lot | Single Lot |
| 1121 E 24th Street | 3000 | Split Lot | Single Lot |

Those three records have no certified current construction phase in the browser audit. The following broader comparison applies the new area rule to each stored construction-side record’s own lot value, not to a matching sold transaction. Full list of 28 disagreements (includes marketed/completed/no-stage records, not just under-construction records):

| Address | Reported lot sqft | Stored label | Area rule | Current phase |
|---|---:|---|---|---|
| 118 E 23rd St, Houston, Tx 77008 | 7250 | Split Lot | Single Lot | complete |
| 314 W 21st St, Houston, Tx 77008 | 7000 | Split Lot | Single Lot | finishing |
| 1123 Louise St, Houston, Tx 77009 | 5000 | Split Lot | Single Lot | finishing |
| 713 E 26th St, Houston, Tx 77009 | 6000 | Split Lot | Single Lot | finishing |
| 1120 E 26th St, Houston, Tx 77009 | 6000 | Split Lot | Single Lot | finishing |
| 845 West 23rd Street | 2455 | Single Lot | Split Lot | market |
| 231 E 26th Street | 3920 | Single Lot | Split Lot | No stage |
| 1207 Tabor Street | 3297 | Single Lot | Split Lot | market |
| 1109 Tabor Street | 3384 | Single Lot | Split Lot | market |
| 1315 Waverly Street | 3610 | Single Lot | Split Lot | market |
| 111 E 18th Street | 2892 | Single Lot | Split Lot | market |
| 830 E 27th Street | 3521 | Single Lot | Split Lot | market |
| 902 E 25TH Street | 3210 | Single Lot | Split Lot | complete |
| 1520 Nicholson Street | 3635 | Single Lot | Split Lot | No stage |
| 2603 JULIAN Street | 3593 | Single Lot | Split Lot | finishing |
| 826 Ralfallen Street | 3551 | Single Lot | Split Lot | complete |
| 3115 Beauchamp Street | 3400 | Single Lot | Split Lot | market |
| 603 E 23rd Street | 3970 | Single Lot | Split Lot | finishing |
| 616 Ridge Street | 3960 | Single Lot | Split Lot | No stage |
| 107 E 24th Street | 3394 | Single Lot | Split Lot | No stage |
| 1011 E 25th Street | 3470 | Single Lot | Split Lot | No stage |
| 1016 E 27 th Street | 3521 | Single Lot | Split Lot | No stage |
| 1032 W 17th Street Unit#A | 2263 | Common Driveway | Split Lot | market |
| 1002 E 25th Street | 3240 | Single Lot | Split Lot | market |
| 834 WAVERLY Street | 3215 | Single Lot | Split Lot | market |
| 830 WAVERLY Street | 3635 | Single Lot | Split Lot | market |
| 614 Ridge Street | 3960 | Single Lot | Split Lot | market |
| 2218 Gostick Street | 3600 | Single Lot | Split Lot | market |

The disagreement alone does not establish which classification is correct: a construction record can report a parent parcel, while a closed sale reports the child lot. No construction label, classifier, parcel or permit pipeline was changed.

## Validation evidence

Command: `/Users/nemoclaw/insp-venv/bin/python -B /tmp/sold_validation.py --preview` (temporary isolated copies of the real input files; existing Playwright setup, all shared-edit writes blocked).

Actual output:

```text
Preview apply twice: index.html and sold_emit.txt byte-identical; second added=0 updated=0
Ledger: 2 missing-required rows + 54 duplicate rows, all source rows accounted for
Counts: total=764; Single Lot=411; Split Lot=289; Unclassified=56; Unknown=8; metrics=764
Footer: 420 homes · 153 permits · 764 closed sales
Single Lot filter: 411 sales / 408 unique pins
Split Lot filter: 289 sales / 289 unique pins
Unclassified filter: 56 sales / 56 unique pins
Unknown filter: 8 sales / 8 unique pins
Repeat-sale history popup checks: PASS
Page errors: []
```

All product filters, sibling bucket counts, recency selection, dashboard, ASK context, historical popup identity and five actual source→stored row→rendered popup comparisons were invoked.

| Sample | Address | Lot sqft | Close price | Product |
|---|---|---:|---:|---|
| largest | 514 W 16th Street | 12,000 | $1,910,000 | Single Lot |
| smallest | 1011 W 14th Street | 2,050 | $619,000 | Split Lot |
| above4000 | 1243 W 15th 1/2 Street | 4,217 | $740,000 | Single Lot |
| below4000 | 1507 Blair Street | 3,636 | $825,000 | Split Lot |
| midSplit | 828 E 28th Street | 3,000 | $747,000 | Split Lot |

Closest available source rows to 4000 are 4217 above and 3636 below; no fabricated near-threshold examples.

Actual rendered popup text:

```text
514 W 16th Street
Single Lot
$1,910,000
4,067 sqft
$469.6/sqft
12,000 sqft lot
2026-08-27
9 DOM
+0.5% vs list
Elem: LOVE ELEMENTARY SCHOOL · List: Cathryn Renfrow · Sell: Kimberly Wilkie · RESALE

1011 W 14th Street
Split Lot
$619,000
2,638 sqft
$234.6/sqft
2,050 sqft lot
2026-08-26
5 DOM
0.0% vs list
Elem: LOVE ELEMENTARY SCHOOL · List: Caroline Schlemmer · Sell: Michelle Comstock · RESALE

1243 W 15th 1/2 Street
Single Lot
$740,000
3,104 sqft
$238.4/sqft
4,217 sqft lot
2026-08-13
70 DOM
-4.5% vs list
Elem: SINCLAIR ELEMENTARY SCHOOL (HOUSTON) · List: Virginia Calise · Sell: Linda Jamail Marshall · RESALE

1507 Blair Street
Split Lot
$825,000
2,145 sqft
$384.6/sqft
3,636 sqft lot
2026-08-28
5 DOM
+3.1% vs list
Elem: LOVE ELEMENTARY SCHOOL · List: Ashli Young · Sell: Ben Whittle · RESALE

828 E 28th Street
Split Lot
$747,000
2,783 sqft
$268.4/sqft
3,000 sqft lot
2026-09-02
34 DOM
-0.4% vs list
Elem: FIELD ELEMENTARY SCHOOL · List: Andrea Tran · Sell: Brandon Guhl · RESALE
```

Real repo apply command (run twice): `/Users/nemoclaw/insp-venv/bin/python -B sold_ingest.py --apply --as-of 2026-09-08`.

Second-run actual output:

```json
{
  "mode": "APPLY",
  "as_of": "2026-09-08",
  "files": [
    {
      "file": "Heightssoldsinglelotslast30days.csv",
      "read": 33,
      "added": 0,
      "updated": 0,
      "excluded": {
        "DUP_EXISTING": 31,
        "MISSING_REQUIRED_FIELD": 2
      },
      "crosscheck_matches": 33
    },
    {
      "file": "Heightssoldsplitlotslast30days.csv",
      "read": 23,
      "added": 0,
      "updated": 0,
      "excluded": {
        "DUP_EXISTING": 23
      },
      "crosscheck_matches": 23
    }
  ],
  "old_total": 764,
  "new_total": 764,
  "products": {
    "Single Lot": 411,
    "Split Lot": 289,
    "Unclassified": 56,
    "Unknown": 8
  },
  "crosscheck_mismatches": [],
  "html_changed": false,
  "ledger_rows": 56
}
```

SHA256 comparison before and after second apply: `SECOND-RUN DIFF: empty (index.html and sold_emit.txt byte-identical)`. The ignored ledger additionally records the second-run duplicate decisions as required; it does not affect the deploy diff.

Executed JSONDecoder slicing comparison against `git show c750005:index.html`: `Hand-authored DATA byte-identical to c750005: PASS`. Both replacement constants reparse, and the ingest asserts all text outside their payloads is identical before writing; this also preserves RECONCILE.

Actual `git diff --stat` after data apply, before this report:

```text
 index.html    | 4 ++--
 sold_emit.txt | 4 ++--
 2 files changed, 4 insertions(+), 4 deletions(-)
```

Stage regression command: `/Users/nemoclaw/insp-venv/bin/python -B tests/browser_calibration.py --output /tmp/sold-stage-after.json --all-markets`.

Actual output summary:

```text
gardenoaksoakforest.html: taxonomy tests 83/83; property fixtures 0/0
index.html: taxonomy tests 83/83; property fixtures 12/12
montrose.html: taxonomy tests 83/83; property fixtures 0/0
riveroaks.html: taxonomy tests 83/83; property fixtures 0/0
springbranch.html: taxonomy tests 83/83; property fixtures 0/0
springvalley.html: taxonomy tests 83/83; property fixtures 0/0
timbergrove.html: taxonomy tests 83/83; property fixtures 0/0
westu.html: taxonomy tests 83/83; property fixtures 0/0
page errors: []
```

## Open items

- Supply Building SqFt for 826 Ralfallen and 824 Cortlandt, or make a separately reviewed schema decision permitting absent area and $/sqft.
- Review the 56 older sub-2000 sqft sales and eight older missing-lot records; their visible labels remain Unclassified/Unknown.
- Review the three sold/construction overlaps and 28 construction-area disagreements; no reconciliation this session.
- The original archive and incremental exports have different source filters. Retain history, expose 365+ records, and describe absorption as sample sales per month; a full consistent-filter rolling-year export is needed for comprehensive market estimates. Eight new source rows are below $500k and were not discarded on price.
- Legacy hidden sold DATA in the other markets remains separate; extending HAR Sold Comps there requires a distinct scope and suitable exports.
- No builder analysis or external lot backfill. Sold/deed pipelines remain separate; shared normalization could be considered later with cross-pipeline fixtures.
