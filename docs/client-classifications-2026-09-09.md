# Client Custom / Sold Off Market classifications — September 9, 2026

**Supply: 144 − 12 Custom − 1 Sold Off Market = 131 homes.** Applied exactly the 24 actionable properties supplied: 19 Custom, 1 Sold Off Market and 4 Needs Clarification. The context mentions 64 researched properties, but no others were tagged. Client research is authoritative; no classifications were derived from permits.

## Applied properties
| Record ID | Address | Prior category | New category | Construction phase (unchanged) | Previously in 12-month supply |
|---|---|---|---|---|---|
| pmt_1032-key-st-77009 | 1032 Key St, Houston, TX 77009 | Under Construction / Foundation | custom | Foundation | No |
| pmt_1225-ashland-st-a-77008 | 1225 Ashland St A, Houston, TX 77008 | Under Construction / Foundation | custom | Foundation | No |
| pmt_1336-herkimer-st-77008 | 1336 Herkimer St, Houston, TX 77008 | Under Construction / Foundation | custom | Foundation | No |
| pmt_1434-herkimer-st-77008 | 1434 Herkimer St, Houston, TX 77008 | Under Construction / Foundation | custom | Foundation | No |
| pmt_1132-e-6th-1-2-st-77009 | 1132 E 6th 1/2 St, Houston, TX 77009 | Under Construction / Foundation | custom | Foundation | Yes |
| pmt_625-merrill-st-77009 | 625 Merrill St, Houston, TX 77009 | Under Construction / Framing | custom | Framing | Yes |
| pmt_705-e-13th-st-77008 | 705 E 13th St, Houston, TX 77008 | Under Construction / Foundation | custom | Foundation | Yes |
| pmt_745-e-16th-st-77008 | 745 E 16th St, Houston, TX 77008 | Under Construction / Foundation | custom | Foundation | Yes |
| pmt_806-peddie-st-77008 | 806 Peddie St, Houston, TX 77008 | Under Construction / Foundation | custom | Foundation | Yes |
| pmt_839-allston-st-77007 | 839 Allston St, Houston, TX 77007 | Under Construction / Foundation | custom | Foundation | Yes |
| pmt_1314-e-28th-st-77009 | 1314 E 28th St, Houston, TX 77009 | Under Construction / MEP Roughs | custom | MEP Roughs | Yes |
| pmt_734-e-7th-1-2-st-77007 | 734 E 7th 1/2 St, Houston, TX 77007 | Under Construction / Framed / Exterior Close-In | custom | Framed / Exterior Close-In | Yes |
| pmt_918-dorothy-st-77008 | 918 Dorothy St, Houston, TX 77008 | Under Construction / Insulation | custom | Insulation | Yes |
| pmt_930-waverly-st-77008 | 930 Waverly St, Houston, TX 77008 | Under Construction / MEP Roughs | custom | MEP Roughs | Yes |
| pmt_1602-turnpike-rd-77008 | 1602 Turnpike Rd, Houston, TX 77008 | Under Construction / Complete | custom | Complete | No |
| pmt_410-columbia-st-77007 | 410 Columbia St, Houston, TX 77007 | Under Construction / MEP Finals | custom | MEP Finals | Yes |
| pmt_715-e-12th-st-77008 | 715 E 12th St, Houston, TX 77008 | Under Construction / Complete | custom | Complete | No |
| pmt_826-e-27th-st-77009 | 826 E 27th St, Houston, TX 77009 | Under Construction / Complete | custom | Complete | No |
| 2131284475 | 1518 Herkimer St, Houston, Tx 77008 | Under Construction / INT.CAB, Tile, ETC | custom | INT.CAB, Tile, ETC | Yes |
| pmt_728-euclid-st-77009 | 728 Euclid St, Houston, TX 77009 | Under Construction / INT.CAB, Tile, ETC | sold_off_market | INT.CAB, Tile, ETC | Yes |
| pmt_1019-e-7th-st-77009 | 1019 E 7th St, Houston, TX 77009 | Under Construction / Foundation | needs_clarification | Foundation | No |
| pmt_822-nashua-st-77008 | 822 Nashua St, Houston, TX 77008 | Under Construction / Framed / Exterior Close-In | needs_clarification | Framed / Exterior Close-In | Yes |
| pmt_1109-voight-st-77009 | 1109 Voight St, Houston, TX 77009 | Under Construction / MEP Finals | needs_clarification | MEP Finals | Yes |
| pmt_433-w-23rd-st-77008 | 433 W 23rd St, Houston, TX 77008 | Under Construction / INT.CAB, Tile, ETC | needs_clarification | INT.CAB, Tile, ETC | Yes |

No supplied Record IDs were missing from DATA. 1518 Herkimer uniquely matched normalized address to **2131284475**. Its classification is Custom. 745 E 16th is Custom, with **remodel** recorded in dated classification metadata and shown on its popup. DATA has no dedicated construction subtype field; classification metadata is separate from construction.

**Already Needs Clarification:** pmt_822-nashua-st-77008 and pmt_433-w-23rd-st-77008. Their existing tags were retained. The tag was added to pmt_1019-e-7th-st-77009 and pmt_1109-voight-st-77009. None of these four was tagged Custom.

## Supply and phase bucket deltas
12 of 19 Custom properties were in the forecast; the remaining seven were outside it. 728 Euclid (Sold Off Market) was also counted, so the total reduction is 13. The four uncertain properties remain eligible for inventory and supply.

| Phase | Before | After | Delta |
|---|---:|---:|---:|
| Foundation | 46 | 37 | -9 |
| Framing | 11 | 10 | -1 |
| Framed / Exterior Close-In | 29 | 28 | -1 |
| MEP Roughs | 7 | 5 | -2 |
| Insulation | 13 | 12 | -1 |
| INT.CAB, Tile, ETC | 55 | 53 | -2 |
| MEP Finals | 20 | 19 | -1 |
| Complete | 52 | 49 | -3 |

Under Construction total: **233 → 213**, a reduction of 20. Category counts: **Custom 19; Sold Off Market 1**. Sold comps remain **767**; deeds remain **139**.

## Layers and persistence
All eight pages load the same category display. Custom and Sold Off Market remain top-level siblings of Under Construction and Market Intel, with working filter checkboxes. Categories with at least three homes show populated product subfilters; Unknown is retained when a product is not supplied. Smaller categories remain flat. No product/lot data was backfilled.
The dated exact-ID client list reapplies tags during legend initialization after shared edits merge. All original phase tags, permits, ETA computations and inspections remain intact. Stale shared tags are exercised in the browser test. Other markets have an empty client list; the category mechanism remains usable there.

## Complete / no-market-record intersection
**3 of 19 Custom homes intersect the prior group of 30; 27 remain.** Removed from the residual:
- 715 E 12th St, Houston, TX 77008 — pmt_715-e-12th-st-77008
- 826 E 27th St, Houston, TX 77009 — pmt_826-e-27th-st-77009
- 1602 Turnpike Rd, Houston, TX 77008 — pmt_1602-turnpike-rd-77008

Full residual list follows. These are finished homes with no market evidence in the previous finite exports/archive; that does not establish that each is available or unlisted today. The prior analysis also includes unnamed inferred companions, which cannot be independently researched without an address.

| Address / represented home | Record ID / member |
|---|---|
| 118 E 23rd St, Houston, Tx 77008 | 2131144961 |
| 1520 W 21st St Unit#B | act_1520-w-21st-st-unit-b |
| 1623 Blount St, Houston, TX 77008 | pmt_1623-blount-st-77008 |
| 1343 Nashua St, Houston, TX 77008 | pmt_1343-nashua-st-77008 |
| 2013 Sheldon St B, Houston, TX 77008 | pmt_2013-sheldon-st-b-77008 |
| 737 W 21st St C, Houston, TX 77008 | pmt_737-w-21st-st-c-77008 |
| 737 W 21st St B, Houston, TX 77008 | pmt_737-w-21st-st-b-77008 |
| 737 W 21st St A, Houston, TX 77008 | pmt_737-w-21st-st-a-77008 |
| 737 W 21st St D, Houston, TX 77008 | pmt_737-w-21st-st-d-77008 |
| 729 W 21st St A, Houston, TX 77008 | pmt_729-w-21st-st-a-77008 |
| 723 W 21st St, Houston, TX 77008 | pmt_723-w-21st-st-77008 |
| 725 W 21st St, Houston, TX 77008 | pmt_725-w-21st-st-77008 |
| 729 W 21st St B, Houston, TX 77008 | pmt_729-w-21st-st-b-77008 |
| 1432 Alexander St, Houston, TX 77008 | pmt_1432-alexander-st-77008 |
| 112 E 27th St A, Houston, TX 77008 | pmt_112-e-27th-st-a-77008 |
| 729 W 21st St C, Houston, TX 77008 | pmt_729-w-21st-st-c-77008 |
| 2811 Ave, Houston, TX 77009 | pmt_2811-ave-77009 |
| 1301 Tabor St, Houston, TX 77009 | pmt_1301-tabor-st-77009 |
| 1107 E 24th St, Houston, TX 77009 | pmt_1107-e-24th-st-77009 |
| 1109 E 24th St, Houston, TX 77009 | pmt_1109-e-24th-st-77009 |
| 409 Walton St A, Houston, TX 77009 | pmt_409-walton-st-a-77009 |
| 931 Merrill St, Houston, TX 77009 | pmt_931-merrill-st-77009 |
| 833 W 25th Street | act_833-w-25th-street |
| 607 W 27th St, Houston, TX 77008 | pmt_607-w-27th-st-77008 |
| Unidentified represented home 1 at 122 E 4th Street | Unidentified companion; project act_122-e-4 |
| Unidentified represented home 1 at 1208 E 26th Street Unit#A | Unidentified companion; project act_1208-e-26th-street-unit-a |
| Unidentified represented home 1 at 335 Harvard Street | Unidentified companion; project act_335-harvard-street |

## Invoked validation
```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --output /tmp/custom-before.json
/Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --output /tmp/custom-after.json
/Users/nemoclaw/insp-venv/bin/python -B tests/full_timeline_check.py
```
Initial after-check actual output:
```text
index {"supply": 131, "columns": {"foundation": 37, "framing": 10, "exterior": 28, "mep_roughs": 5, "insulation": 12, "interior": 53, "mep_finals": 19, "complete": 49}, "uc": 213, "deed": 139, "sold": 767}
CHECKS index 57 / 57 FAILURES []
Other seven markets: 18 / 18 each; ERRORS []
```
Invoked Python comparison of before/after browser JSON returned `PASS all eight markets: every property phase/ETA/product/home weight unchanged`. Source-span comparison against `git show 555edb4:<market>.html` asserted every DATA array byte-identical; hashes are in the accompanying JSON.

`git diff --stat` for page changes: **one script include added per HTML file, eight lines total**. No DATA serialization, phase/timeline functions, scraper or ingest changes.

## Open items
- 27 residual Complete/no-market-record entries need market-status research, including unnamed companions.
- Only the supplied 24 properties were actionable; the other 40 mentioned in context were not provided.
- Four uncertain properties remain Needs Clarification, as requested.

## Three identical full checks — actual output

```text
RUN 1: phase 20706/20706; browser 183/183; base pairs 7283, violations 0; page errors []; SHA256 01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a
RUN 2: phase 20706/20706; browser 183/183; base pairs 7283, violations 0; page errors []; SHA256 01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a
RUN 3: phase 20706/20706; browser 183/183; base pairs 7283, violations 0; page errors []; SHA256 01f7858ff12e7956125492e8c177eb377f79b421ee5e15cc63c8a4c34aa8bd7a
PASS: all three full results byte-identical
```

Harvard/629, Munford, 1033 Voight, 112 E 27th, 609 E 25th and 830 E 26th construction fixtures passed in every run. The unchanged 376 Heights phase/ETA tuples are independently compared against the before-capture.

Actual category panel text: Custom 19; Single Lot 17; Unknown 2; Sold Off Market 1. The two unknown products were not inferred or filled.

## Live verification

Deployed implementation commit: `7e1bdd5` (pushed to origin/main). All eight HTML files and inventory_classifications.js were verified in its tree.

```sh
/Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --spots --live https://tangerine-sorbet-eca5f5.netlify.app --output /tmp/custom-live.json
```

Actual output: Heights `57 / 57 FAILURES []`; other seven markets `18 / 18 FAILURES []`; `ERRORS []`; `PASS live classification JS byte-identical`. A parser comparison asserted the entire live JSON result equals the three-run local result.

Live category panel: Custom **19**, Single Lot **17**, Unknown **2**; Sold Off Market **1**. Live supply **131**, Under Construction **213**, deeds **139**, sold comps **767**.

Custom spot: **1032 Key**, Foundation, permit **25117865**, phase/ETA card retained (ETA remains unavailable because its existing model has no dated anchor). Another exercised Custom popup, **930 Waverly**, retains MEP Roughs and its ETA card. Sold Off Market spot: **728 Euclid**, INT.CAB, permit **26006967**, unchanged completion **~3.5 months / 2026-12-20**. Both retain inspections and dated client classification metadata.
