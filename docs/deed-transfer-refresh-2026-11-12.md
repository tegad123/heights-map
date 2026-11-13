# Deed transfer refresh — 2026-11-12

Applied 2026-11-13 from the DealMachine export saved as `deed_slim.csv`
(filter "DEED TRANSFER": single family, sale within about two months, lot
over 4,000 sqft, corporate owned). Sale dates in the file run 2026-09-14
through 2026-11-02. Zips: 77005, 77006, 77007, 77008, 77009, 77018, 77019,
77027, 77055, 77080, 77098.

The source CSV is not committed. It has no phone, email, or mailing-address
columns. New pin and metadata rows set `c` to null. `v` stays assessed value.
The export's `sale_price` column is not written onto the pin (see open items).
SHA-256 of the file used here:
`b21b510fef955c6ad1f5852f030609933ace0cbb4f4ceb31715b2b1750e46dd4`.

`sold_ingest.py` was not modified. Routing is unchanged: configured polygons,
the Heights street regex, and Heights `lng <= -95.370`. West U stays on its
zip-plus-box rule. Ambiguous markets are excluded, not guessed.

## Overlap rule

Two DATA pins in one market with the same normalized street address are one
property recorded twice. `deed_ingest.py` merges them before it matches the
CSV. The surviving pin keeps the other pin's id (`listing_alias_ids`), permit
rows, sale facts, lifecycle text, and notes. A listing or staged build does
not gain a `deed` tag, because `pinColor()` checks that tag before
`active_single` and would repaint the pin. The deed sentence still lands in
the notes. A plain permit pin does gain the tag, and it keeps its `permits`
array.

Distinct unit letters stay separate (711 E 25th St A and B share one
DealMachine id and are not merged). House numbers that are merely close are
not merged.

Pins within 0.70 m are treated as the same map point (stacked units, or two
geocodes on top of each other). Every market page, including Spring Valley,
spreads that cluster so the drawn markers are 16 m apart. `tests/test_pin_overlap.py`
fails if any market still has a duplicate address, two pins with the same
DealMachine id and the same address, or two display positions within 0.70 m.
`.github/workflows/tests.yml` runs that test on push and pull request.

## Counts

Command, before this branch's merge step, on `d483f79`:

```text
TOTAL read=160 accepted=119 added=110 updated=9 unchanged=0 excluded=41
EXCLUSIONS {"AMBIGUOUS_MARKET": 4, "AMBIGUOUS_MATCH": 1, "OOZ_EAST": 5, "OUT_OF_MARKET": 31}
```

The one `AMBIGUOUS_MATCH` was 1300 Waverly St. After the merge step the same
file applies as:

```text
TOTAL read=160 accepted=120 added=110 updated=10 unchanged=0 excluded=40
MARKET gardenoaksoakforest: added=17 updated=2
MARKET heights: added=38 updated=5
MARKET montrose: added=8 updated=2
MARKET riveroaks: added=2 updated=0
MARKET springbranch: added=34 updated=1
MARKET timbergrove: added=3 updated=0
MARKET westu: added=8 updated=0
EXCLUSIONS {"AMBIGUOUS_MARKET": 4, "OOZ_EAST": 5, "OUT_OF_MARKET": 31}
MERGES 49
```

A second run of the same file reported `added=0 updated=0 unchanged=120`,
`MERGES 0`, and wrote no files. The dropped ledger
`pulls/dropped_2026-11-13.csv` is gitignored. The first apply appended 40
rows; the second append added none.

The six permit-overlap rows are single pins. Three already had a city permit
array; three were acquisition pins (`kind: "permit"`). Each now also has the
new sale date, assessed value, buyer, lot size, DealMachine URL, and a note
that keeps the previous owner:

| Address | Market | Pin | Permit rows | Sale |
| --- | --- | --- | --- | --- |
| 4510 Yoakum Blvd | montrose | `acq_4510-yoakum-blvd` | 0 (acquisition pin) | 2026-10-21 |
| 221 Emerson St | montrose | `acq_221-emerson-st` | 0 (acquisition pin) | 2026-10-20 |
| 902 W 42nd St | gardenoaksoakforest | `pmt_902-w-42nd-st-77018` | 1 (`26083483`) | 2026-09-21 |
| 1602 Viking Dr | gardenoaksoakforest | `pmt_1602-viking-dr-77018` | 1 (`25045112`) | 2026-10-09 |
| 940 Nadine St | heights | `pmt_940-nadine-st-77009` | 1 (`25120411`) | 2026-10-08 |
| 1836 Lynnview Dr | springbranch | `acq_1836-lynnview-dr` | 0 (acquisition pin) | 2026-10-16 |

## Merged duplicates

49 pairs. The canonical id is the one that already had the permit, the
listing, or the product label. The retired id is on `listing_alias_ids` and
in the seed note, with any assessed value, lot, or coordinate that differed.

| Market | Address | Kept | Retired |
| --- | --- | --- | --- |
| heights | 1300 Waverly St | `2131146866` | `2131146860` |
| heights | Enid St | `2177158676` | `2177158678` |
| montrose | 1125 Jackson Blvd | `pmt_1125-jackson-blvd` | `acq_1125-jackson-blvd` |
| montrose | 1223 W Drew St | `pmt_1223-w-drew-st` | `acq_1223-w-drew-st` |
| montrose | 1304 Welch St | `pmt_1304-welch-st` | `acq_1304-welch-st` |
| montrose | 1720 Kipling St | `pmt_1720-kipling-st` | `acq_1720-kipling-st` |
| montrose | 1744 Harold St | `pmt_1744-harold-st` | `acq_1744-harold-st` |
| montrose | 1906 Woodhead St | `act_1906-woodhead-street` | `acq_1906-woodhead-st` |
| montrose | 1907 Sul Ross St | `act_1907-sul-ross-street` | `acq_1907-sul-ross-st` |
| montrose | 1916 Hawthorne St | `pmt_1916-hawthorne-st` | `acq_1916-hawthorne-st` |
| montrose | 1918 Huldy St | `pmt_1918-huldy-st` | `acq_1918-huldy-st` |
| montrose | 2415 Elmen St | `act_2415-elmen-street` | `acq_2415-elmen-st` |
| montrose | 608 Peden St | `pmt_608-peden-st` | `acq_608-peden-st` |
| westu | 2328 Quenby St | `pmt_2328-quenby-st` | `acq_2328-quenby-st` |
| westu | 2405 Nottingham St | `pmt_2405-nottingham-st` | `acq_2405-nottingham-st` |
| westu | 3743 Westerman St | `pmt_3743-westerman-st` | `acq_3743-westerman-st` |
| westu | 3771 Purdue St | `pmt_3771-purdue-st` | `acq_3771-purdue-st` |
| westu | 4002 Marquette St | `ACT08` | `acq_4002-marquette-st` |
| riveroaks | 3713 Chevy Chase Dr | `pmt_3713-chevy-chase` | `acq_3713-chevy-chase-dr` |
| springbranch | 8922 Carousel Ln | `acq_8922-carousel-ln` | `acq_8922-carousel-ln-2` |
| springbranch | 1305 Confederate Rd | `pmt_1305-confederate` | `acq_1305-confederate-rd` |
| springbranch | 1402 Pine Chase Dr | `pmt_1402-pine-chase` | `acq_1402-pine-chase-dr` |
| springbranch | 1457 Confederate Rd | `act_1457-confederate` | `acq_1457-confederate-rd` |
| springbranch | 1521 Bracher St | `pmt_1521-bracher` | `acq_1521-bracher-st` |
| springbranch | 1606 Afton St | `pmt_1606-afton` | `acq_1606-afton-st` |
| springbranch | 1606 Monarch Oaks St | `pmt_1606-monarch-oaks` | `acq_1606-monarch-oaks-st` |
| springbranch | 1618 Ronson Rd | `pmt_1618-ronson` | `acq_1618-ronson-rd` |
| springbranch | 1707 Bayram Dr | `act_1707-bayram` | `acq_1707-bayram-dr` |
| springbranch | 1909 Restridge Dr | `pmt_1909-restridge` | `acq_1909-restridge-dr` |
| springbranch | 1941 Coulcrest Dr | `act_1941-coulcrest` | `acq_1941-coulcrest-dr` |
| springbranch | 1946 Pech Rd | `act_1946-pech` | `acq_1946-pech-rd` |
| springbranch | 7106 Raton St | `pmt_7106-raton` | `acq_7106-raton-st` |
| springbranch | 7119 Housman St | `act_7119-housman` | `acq_7119-housman-st` |
| springbranch | 7127 Northampton Way | `pmt_7127-northampton` | `acq_7127-northampton-way` |
| springbranch | 7214 Blandford Ln | `pmt_7214-blandford` | `acq_7214-blandford-ln` |
| springbranch | 7218 Schiller St | `act_7218-schiller` | `acq_7218-schiller-st` |
| springbranch | 7602 Bryonwood Dr | `pmt_7602-bryonwood` | `acq_7602-bryonwood-dr` |
| springbranch | 7719 Bryonwood Dr | `pmt_7719-bryonwood` | `acq_7719-bryonwood-dr` |
| springbranch | 7726 Betty Jane Ln | `pmt_7726-betty-jane` | `acq_7726-betty-jane-ln` |
| springbranch | 8029 Ridgeview Dr | `pmt_8029-ridgeview` | `acq_8029-ridgeview-dr` |
| springbranch | 8033 Ridgeview Dr | `act_8033-ridgeview` | `acq_8033-ridgeview-dr` |
| springbranch | 8046 Turquoise Ln | `pmt_8046-turquoise` | `acq_8046-turquoise-ln` |
| springbranch | 8550 Montridge Dr | `act_8550-montridge` | `acq_8550-montridge-dr` |
| springbranch | 8561 Forum Dr | `pmt_8561-forum` | `acq_8561-forum-dr` |
| springbranch | 9306 Livernois Rd | `pmt_9306-livernois` | `acq_9306-livernois-rd` |
| springbranch | 9349 Leto Rd | `act_9349-leto` | `acq_9349-leto-rd` |
| springbranch | 9541 Kerrwood Ln | `act_9541-kerrwood` | `acq_9541-kerrwood-ln` |
| springbranch | 9626 Carousel Ln | `pmt_9626-carousel` | `acq_9626-carousel-ln` |
| springbranch | 9741 Warwana Rd | `pmt_9741-warwana` | `acq_9741-warwana-rd` |

1300 Waverly St is the pair the importer used to reject. HCAD has two tracts
at that address (19A/20A/21A on `2131146860`, lot 5,200, assessed $468,000;
19B/20B/21B on `2131146866`, lot 8,000, product Single Lot). The incoming row
is property `2131146866`, sale 2026-10-16, buyer Bla Ventures Llc, assessed
$767,296. That id is the pin. The retired tract's value, lot, and coordinate
are in the seed note. The new sale note also keeps the March 16, 2026 sale
and the previous assessed $775,265.

Enid St is the other Heights pair: both pins were unnumbered, 22 m apart,
same buyer and sale date, different assessed values. They normalized to the
same address, so they were merged onto `2177158676`. If they are two lots,
they should be split back apart with real street numbers.

## Exclusions

40 rows. Ledger market column is `heights` because that is the source market
argument; the reason says which destination was refused.

| Reason | Count |
| --- | --- |
| OUT_OF_MARKET | 31 |
| OOZ_EAST | 5 |
| AMBIGUOUS_MARKET | 4 |

OOZ_EAST (Heights longitude east of -95.370, no other market): 1103 Harrington
St, 4106 Siegel St, 4119 Beggs St, 411 Marie St, 305 Frawley St.

AMBIGUOUS_MARKET, left off the map on purpose:

| Address | Zip | Coordinate | Markets | Sale | DealMachine id |
| --- | --- | --- | --- | --- | --- |
| 315 W 32nd St | 77018 | 29.815854, -95.402646 | heights, gardenoaksoakforest | 2026-09-14 | 2131395799 |
| 702 W 32nd St | 77018 | 29.816624, -95.411972 | heights, gardenoaksoakforest | 2026-10-27 | 2131442049 |
| 1102 Bay Oaks Rd | 77008 | 29.790467, -95.414095 | heights, timbergrove | 2026-10-15 | 2131538003 |
| 1018 Worthshire St | 77008 | 29.789929, -95.415051 | heights, timbergrove | 2026-09-30 | 2131538929 |

OUT_OF_MARKET (outside every tracked polygon): 1202 Birdsall St, 1204
Birdsall St, 502 Jackson Hill St, 504 Jackson Hill St, 1004 Candlelight Ln,
1230 Del Norte St, 2323 Bron Holly Dr, 110 E 44th St, 237 Hyta St, 932 Lehman
St, 5418 Elysian St, 3703 Moore St, 1113 Collingsworth St, 1102 Bingham St,
1620 Gano St, 2703 Cochran St, 713 Fairbanks St, 2012 Marion St Unit 1, 1413
Egypt St, 4609 Billingsley St, 8734 Lanell Ln, 8411 Lofland Dr, 8429
Winningham Ln, 6 Tam Ct, 4119 Portsmouth Ave, 4702 Banning Dr, 4028 Essex Ln,
4013 W Alabama St, 1337 Mickey Way, 8849 Larston St, 1018 Ben Hur Dr.

## Open items

- Four ambiguous-market rows above need a person to pick the map. The same
  boundary already puts these existing DealMachine ids on both Heights and
  Timbergrove, so a new row for Bay Oaks or Worthshire was not guessed:
  `2131537524` 1219 Bay Oaks Rd, `2131538328` 922 Prince St, `2131538429`
  1023 Nashua St, `2131538680` 911 Bay Oaks Rd, `2131538718` 905 Bay Oaks Rd,
  `2131538725` 1510 Glen Oaks St, `2131538738` 1522 Glen Oaks St. Each
  Timbergrove copy is `tg_mig_<id>`. They are one pin per map, not two pins
  on one map, and were not deleted.
- 1300 Waverly St is one pin now, with both tract facts in the note. The
  product hold on retired id `2131146860` is still in
  `product_classification_holds.json` and no longer matches a pin.
- Enid St may be two unnumbered lots. See the merge note.
- `0 Enid` (id `2131227419`, 29.792316, -95.375666, 77009, sale 2026-10-26)
  was added to Heights. The street number in the export is 0. It did not
  match the Enid St pair.
- `sale_price` is populated on 78 of 160 rows and 0 on the other 82. `v`
  remains assessed value. A separate sale-price field is still not on the
  pin or the popup.
- Neighboring house numbers more than 0.70 m apart are left where they were
  geocoded. At a zoomed-out view their circles can still touch. Spreading
  every townhouse row would move whole blocks. Same-point stacks are the
  ones the page separates.
- Checked by parsing every market DATA and SEED block after the apply, and
  by `tests/test_pin_overlap.py`. The password-gated live site was not opened.
