# Product display provenance — 2026-09-10

Display only. Stored DATA, SOLD_DATA, SOLD_METRICS and market snapshot unchanged. No classify_lot, stage, timeline, status or filter-classification changes.

Geometry-backed requires a high-confidence stored product matching its classification metadata, a parcel account/source and measured depth. Existing client determinations remain authoritative. Unverified old labels are not silently promoted to geometry-backed evidence.

Current market evidence: 40 geometry-backed labels suppress HAR product (20 actual product conflicts), 115 lot-size labels marked provisional, 4 already-client-labelled displays unchanged. An additional 92 geometry-backed members without current listing evidence gain an explicit construction-product line. Thus 247 construction/member card sections change; paired cards can contain more than one member.

Sold records: 42 uniquely linked geometry-backed labels, 2 uniquely linked client labels, 746 provisional lot-size labels; 790 card displays change. Matching uses existing current Sold MLS or archive_current transaction links only; no fuzzy address/parcel inference. Historical listings are not automatically assigned the product of a later build.

All 790 archive records are audited, including records not currently shown by the Sold panel filter. These counts are display records, not unique physical homes across datasets.

Invocation: `/Users/nemoclaw/insp-venv/bin/python -B tests/product_display_check.py`

```text
{"marketGeometry": 40, "marketClient": 4, "marketProvisional": 115, "geometryLabelConflicts": 20, "geometryCardsWithoutCurrentListing": 92, "soldGeometry": 42, "soldClient": 2, "soldProvisional": 746}
probe: Common Driveway · parcel-backed construction classification
unchanged: true
Finished: 34 Active / 9 Pending / 19 Terminated / 57 No Market Record
```
