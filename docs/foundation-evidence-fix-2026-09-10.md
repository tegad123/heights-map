# Heights Foundation evidence correction — 2026-09-10

A permit alone no longer establishes Foundation. Empty, failed-only, and site/preconstruction-only inspection lists return null. Phase promotion preserves permit-layer visibility and removes stale phase tags. No timeline, product, market-status routing, boundary or DATA changes. The market popup wrapper now preserves the explicit permit/no-construction-inspections label.

## Invocation

`/Users/nemoclaw/insp-venv/bin/python -B tests/foundation_evidence_check.py` returned `HEIGHTS PASS ONE CHECK`. The first browser attempt caught a popup-label override; after fixing it, one full Heights run passed.

```json
{"empty": null, "failed": null, "site": null, "partial": "foundation", "approved": "framing"}
```

Existing 1031 semantics retained: Partial Approval establishes Foundation; full Approval certifies the pour and advances to Framing. Louise and Sylvester retain Foundation from partial approvals.

37 homes lose unsupported Foundation, including four Custom homes already outside pipeline counts: 1434 Herkimer, 1032 Key, 1336 Herkimer, 1225 Ashland A. Under Construction: 211→178.

| Phase | Before | After |
|---|---:|---:|
| foundation | 42 | 9 |
| framing | 10 | 10 |
| exterior | 30 | 30 |
| mep_roughs | 6 | 6 |
| insulation | 11 | 11 |
| interior | 65 | 65 |
| mep_finals | 47 | 47 |
| complete | 88 | 88 |

Supply unchanged: 170 forecast − 14 terminated = 156, matching Overview. Finished Active 44, Pending 8, No Market Record 38 unchanged; Terminated 25→26 because 305 W 17th now has no phase and routes by existing market evidence rules. Its card explicitly does not assert construction completion.

All 567 represented homes / 521 project pins retained; sold 793, deeds 138, Custom 19, Sold Off Market 1 unchanged. DATA byte-identical. Retained construction/market fixtures passed; phase monotonicity 3,257 pairs with zero violations; elapsed-time ordering check passed.

## All affected homes

| Address | Before | After |
|---|---|---|
| 1811 Bonner St, Houston, TX 77007 | Foundation | No phase |
| 1108 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 1110 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 1112 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 1114 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 1116 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 1118 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 745 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 1434 Herkimer St, Houston, TX 77008 | Foundation | No phase |
| 902 Jewett St, Houston, TX 77009 | Foundation | No phase |
| 940 Nadine St, Houston, TX 77009 | Foundation | No phase |
| 1032 Key St, Houston, TX 77009 | Foundation | No phase |
| 906 W 20th St E, Houston, TX 77008 | Foundation | No phase |
| 906 W 20th St F, Houston, TX 77008 | Foundation | No phase |
| 906 W 20th St A, Houston, TX 77008 | Foundation | No phase |
| 906 W 20th St B, Houston, TX 77008 | Foundation | No phase |
| 906 W 20th St C, Houston, TX 77008 | Foundation | No phase |
| 1336 Herkimer St, Houston, TX 77008 | Foundation | No phase |
| 914 W 16th St, Houston, TX 77008 | Foundation | No phase |
| 1225 Ashland St A, Houston, TX 77008 | Foundation | No phase |
| 1922 Bonner St, Houston, TX 77007 | Foundation | No phase |
| 606 Link Rd F, Houston, TX 77009 | Foundation | No phase |
| 606 Link Rd E, Houston, TX 77009 | Foundation | No phase |
| 606 Link Rd D, Houston, TX 77009 | Foundation | No phase |
| 606 Link Rd C, Houston, TX 77009 | Foundation | No phase |
| 606 Link Rd B, Houston, TX 77009 | Foundation | No phase |
| 606 Link Rd A, Houston, TX 77009 | Foundation | No phase |
| 2311 Roy Cir, Houston, TX 77007 | Foundation | No phase |
| 1019 E 7th St, Houston, TX 77009 | Foundation | No phase |
| 5212 Kansas St, Houston, TX 77007 | Foundation | No phase |
| 1032 W 17th St C, Houston, TX 77008 | Foundation | No phase |
| 1032 W 17th St B, Houston, TX 77008 | Foundation | No phase |
| 1813 W 14th St, Houston, TX 77008 | Foundation | No phase |
| 305 W 17th St, Houston, TX 77008 | Foundation | No phase |
| 321 E 24th St, Houston, TX 77008 | Foundation | No phase |
| 707 Teetshorn St, Houston, TX 77009 | Foundation | No phase |
| 606 Link Rd G, Houston, TX 77009 | Foundation | No phase |

## Review item

1019 E 7th retains needs_clarification and Single Lot. Building Pmt 26064937 valued $821,702 contradicts the earlier no-build-permit note. Added to docs/product-review-list-2026-09-10.md for verification; no identity/scope adjudication made.
