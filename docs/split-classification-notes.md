# Split vs Single classification — findings, 2026-08-26

Working notes for the next session. Covers what the HCAD parcel-geometry
diff established, what it broke, and the cascade revision it implies.
Nothing here has been applied to the live cascade — see **Open** at the end.

---

## 1. What started this

614 and 629 E 26th St were labelled **Split Lot** but are single-lot builds.
Both carry the badge `split project · 2 homes · twin not tracked`.

The badge was a symptom, not the cause. `index.html:492` sets `_soloSplit`
only on records *already* labelled split whose twin it cannot find; the
pair-merge engine was reporting the inconsistency correctly.

Root cause: `classify_v6.py` / `classify_v9.py` contained

```python
if w>=2: return "Split", f"spans {w} lots"
```

Heights and Sunset Heights original plat lots are ~25 ft. A legal like
`LTS 6 & 7 BLK 40` therefore describes **two plat lots assembled into one
50 ft lot** carrying one house — the opposite of a subdivision.
`classify_final.py:58` already had this right (`LEGAL assembled` → Single);
v6/v9 did not. The bad labels reached DATA via commit `d1040e6`
(2026-07-23, "Apply 73 manual lot classifications from satellite review"),
which flipped 32 records Single→Split.

---

## 2. The geometry diff

`refresh/parcel_diff.py` compares HCAD parcel polygons across three
vintages (2024 Oct, 2025 Oct, 2026 Jul) by representative-point containment
plus an area-sum test. Signal generation only — it never writes DATA,
RECONCILE, or any classify script.

Zone: `ZONE_RING` (lifted from `index.html` at runtime, so it stays in
sync) plus the CLAUDE.md eastern cut at `lng > -95.370`. ~29.6–30.0k
parcels per vintage. Runs in ~10 s once the per-vintage cache in
`~/hcad-gis/.parcel_diff_cache/` is warm.

Output `refresh/parcel_events.json`, 458 events:
`SPLIT 156 · VANISHED 120 · RESHAPE 103 · ASSEMBLY 43 · PARTIAL 36`.

### Gotchas already paid for

- **2026 ships as a File Geodatabase**, not a shapefile. Needs a one-time
  `ogr2ogr` conversion — see `parcel_diff.py --help-gdb`.
- **Never pass `-nlt POLYGON`** to that conversion. It keeps only one part
  of every multipart parcel (`0200870000001`: 39,062 sf instead of 86,958)
  and fabricates ~35 bogus 50%-shrink "half-split" events, all landing in
  whichever pair uses the converted vintage. The tell was that every one
  was in a single vintage pair. The recipe in `--help-gdb` documents this.
- **geopandas is unusable on this box** (py3.14 GIL-enabled: no `fiona`
  cp314 wheel, `pyogrio` only ships cp314t). The script uses
  `pyshp` + `shapely` + `pyproj` instead.
- `ogr2ogr` writes ISO-8859-1 DBFs; the reader honours `.cpg` and falls
  back to latin1 with `encodingErrors='replace'`.

---

## 3. Finding: `MST OF 2` does not mean the lot was subdivided

This is the important one. The permit chain marker was rank-1 in the
proposed cascade, short-circuiting every other signal. Geometry says it
should not be.

| record | permit | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| 713 E 26th | `MST OF 2` | 6,000 sf | 6,000 | 6,000 |
| 711 E 26th | `M # 25087111` | 6,000 sf (separate parcel) | 6,000 | 6,000 |
| 1010 E 26th | `MST OF 2` | 3,020 sf | 3,000 | 3,000 |
| 1012 E 26th | `M# 25091918` | 2,979 sf (separate parcel) | 3,000 | 3,000 |
| 1120 E 26th | `MST OF 2` | 6,127 sf | 6,024 | 6,000 |

None of these parcels ever changed. 713 and 1120 sit on **full 6,000 sf
assembled lots** — geometrically identical to 614 and 629, the two records
that started this. `MST OF 2` marks a *two-permit project*; whether it sits
on a subdivided parcel is a separate question it does not answer.

Counter-example that *is* real: **527 W 26th** went 6,550 → 3,275 sf in
2025→2026. Its sibling half is not yet published in the parcel layer (I
checked every parcel within 120 ft), so it surfaces as `RESHAPE −50%`
rather than `SPLIT`. **A `RESHAPE` near −50% is a half-published split**
and should be treated as split evidence.

---

## 4. Finding: the child-area rule

A parcel splitting does **not** by itself mean a Split-Lot product. What
the children measure decides it:

| event | children | product |
|---|---|---|
| 314 W 21st: 7,055 sf → 2 × 3,500 | half lots | **Split Lot** |
| 625/633 Oxford: 13,200 → 2 × 6,600 | full lots | **Single Lot** |
| 402–410 Columbia: 33,000 → 5 × 6,600 | full lots | **Single Lot** |

A large tract subdividing into full 6,600 sf lots produces five
single-lot builds. Only a ~6,000–7,000 sf lot halving into ~3,000–3,500 sf
children is a split-lot product. `areas.child_sf` is in
`parcel_events.json` for exactly this test.

---

## 5. What was applied

**13 DATA corrections** (`index.html`, surgical string replacement anchored
on record id, `ty`→`active_single` + `prod`→`Single Lot`). Split-labelled
records 105 → 92. All 13 are geometrically `unchanged` across all three
vintages:

```
1006 E 28th · 1008 E 28th · 1220 Prince · 2811 Ave · 408 Columbia
410 Columbia · 614 E 26th · 625 Oxford · 629 E 26th · 826 E 27th
845 E 26th  · 902 Jewett  · 930 Waverly
```

**314 W 21st St was NOT flipped.** It was in the original 14-record
proposal; geometry refuted it (7,055 → 3,500 + 3,500 in 2025→2026). It is
a genuine half-lot split and stays `Split Lot`. This is the one case where
the geometry diff overturned the lot-size cascade.

**classify_v6.py / classify_v9.py**: `w>=2` now returns
`("Review", "assembled N lots -> needs_review")` instead of `Split`.
Both call sites handle it as undecided rather than falling through to the
Single default:
- v6: Split decisions 315 → 261; 54 rows routed to review.
- v9: `Split Lot` 166 → 131, `needs_review` 5 → 42, **`Single Lot`
  unchanged at 73** — it defers, it does not manufacture Singles.

These two scripts are offline review tooling, not in the deploy path.

---

## 6. Proposed cascade revision (NOT applied)

Current live cascade, in order: chain marker → unit letter → lot size.
Measured against the 202 DATA rows with a label in
`heights_review_FINAL.csv`, it is **100% precise when it says Single
(107/107)** but only **65% when it says Split (62/95)**. That asymmetry is
why the 13 corrections were safe to apply one-directionally, and why the
Split direction must not be auto-applied.

Suggested revision, strongest evidence first:

1. **Parcel event** from `parcel_events.json` — `SPLIT` or `RESHAPE ≈ −50%`
   **with children ≤ 4,000 sf** → Split. Children ≥ 5,000 sf → Single.
2. **Unit letter** in the address → Split (100% precision, ~33% recall).
   Special case: **3+ lettered units on ONE parcel is Common Driveway**, not
   Split (906 W 20th A–F, five permits on one 10,889 sf parcel).
3. **Whole-lot legal count, ALWAYS GATED ON AREA.** Both ungated forms of
   this rule are wrong and were corrected on 2026-08-26:
   - ~~`LT N` alone → Single~~. In Sunset Heights the plat lot is ~25 ft /
     3,000 sf, so one whole platted lot is a **half-width build**.
     1010 and 1012 E 26th are `LT 18` / `LT 19 BLK 43` at 3,000 sf and are
     genuine Splits. Correct form: `LT n` + area ≥ 5,000 → Single;
     `LT n` + area ≤ 4,000 → Split.
   - ~~`TR` fragments → split evidence~~. Of 31 TR-only records, **none**
     were ≤ 4,000 sf and 15 were ≥ 8,000 (up to 20,117). A tract fragment
     means "not a whole platted lot" and says nothing about size. Correct
     form: same area gate as above.
   - `LTS N & M` (assembled) → Single only when area ≥ N × 2,400;
     below that the legal is stale after a split → review.
4. **Parcel area** (HCAD `Shape.STArea()` / HAR `lot`): ≤ 4,000 → Split,
   ≥ 5,000 → Single, conflict between the two sources → review. Use the
   per-plat median where one exists (see Open).
   Guard: **≥ 12,000 sf is not a lot-level product at all** — treat as
   Common Driveway / commercial pending a unit count. Use an ABSOLUTE
   threshold, not a multiple of the plat median: a ≥2× median test flags
   629 E 26th (a known Single at 6,195 sf) because its Sunset Heights block
   median is 3,001.
5. **Chain marker** demoted to corroboration only — it distinguishes a
   two-permit project, not a subdivided parcel.
6. Otherwise → review. Never default to Split.

Caveat on the labelled set: `final_source='hand'` in
`heights_review_FINAL.csv` is **not** independent human adjudication —
`accept.py:24` stamps "hand" onto whatever the `prod` column held, and that
column is the 2026-07-22 DATA snapshot, i.e. the state `d1040e6` then
overwrote. Treat it as a record of the pre-regression labels, not a second
opinion. The independent evidence is parcel geometry.

---

---

## 7. Triage of everything needing clarification (2026-08-26)

231 unique records across the three clarification groups, run through the
full stack above. Full table: `notes/clarification_triage.csv` (gitignored).

| bucket | n |
|---|---|
| RESOLVED-SINGLE | 176 |
| RESOLVED-SPLIT | 9 |
| GENUINELY-AMBIGUOUS | 46 |

| group | n | Single | Split | Ambiguous |
|---|---|---|---|---|
| A — v9 needs_review (multi-lot legals) | 42 | 31 | 1 | 10 |
| B — HAR/HCAD size conflict | 30 | 24 | 5 | 1 |
| C — unlabeled permit-ingest pins | 163 | 123 | 5 | 35 |

231 unique, not 235: 4 records are in both B and C. Group A is keyed by
review-CSV address and B/C by DATA id, so ~30 physical properties appear
under two keys.

### The 46 ambiguous, by what would settle each

| reason | n | evidence that would settle it |
|---|---|---|
| oversized tract (≥ 12,000 sf) | 24 | unit count / site plan — assign Common Driveway or commercial |
| no parcel at the pin | 8 | geocode fix — no HCAD parcel contains the coordinate |
| 4–5k dead zone | 7 | frontage/depth from the parcel polygon (50×100 vs 25×100) |
| multi-unit on one parcel | 5 | all `906 W 20th A–F` — resolved to Common Driveway in ea2daaa |
| stale legal | 2 | `631 Mazal` (3 lots, 4,170 sf), `835 Lawrence` (3 lots, 5,700 sf) — HCAD legal refresh |

### Applied

`ea2daaa` labelled **77 Single** (the group-C resolved-Singles *minus* 46
carrying the plat-risk flag) and **5 Common Driveway** (906 W 20th A–F).
Unlabeled DATA records 163 → 81.

**Held pending per-plat thresholds:** the 46 plat-risk Singles and the
9 resolved Splits. Brooke Smith, Studes, Milroy Place and Norhill are all
~5,000 sf plats, so 59 of the 231 sit where the global 5,000 line is unsafe
— this is the per-plat issue at scale, not a handful of edge cases.

### Chain-marker candidates

Control validation ran 14 known-truth records; 12 matched. The 2 that
differed are **711 E 26th** and **1122 E 26th** — both `MST OF 2` / `M #`
records sitting on full 6,000 sf assembled lots, which the evidence stack
calls Single while DATA says Split. With **713** and **1120 E 26th** (same
pattern, found in §3) that is **4 records** that would flip Single if the
chain marker is demoted. They are the concrete test case for that decision.

## Open

### Per-plat threshold miscalibration (multi-market blocker)

`SPLIT_MAX=4000` / `SINGLE_MIN=5000` (`sold_ingest.py:72-73`) were calibrated
on Houston Heights / Sunset Heights geometry: ~6,600 sf original lots with
~3,300 sf halves, leaving a genuinely empty 4,000–5,000 gap. That gap is not
empty in other plats.

**Ridgewood / North Norhill is platted at ~5,000 sf, not 6,600** — the full
lot sits exactly on the threshold. On the 806 Peddie block, **12 of 33
parcels (36%) fall inside the dead zone despite being identical full lots**:

```
810 PEDDIE ST    4,978 sf   DEAD ZONE
802 PEDDIE ST    4,986 sf   DEAD ZONE
811 LE GREEN ST  4,963 sf   DEAD ZONE
805 LE GREEN ST  4,981 sf   DEAD ZONE
806 PEDDIE ST    5,026 sf   Single — clears by 26 sf (0.5%)
```

Zone-wide (2026 vintage, 29,974 parcels): **3,346 = 11.2% sit in the dead
zone**, and 3,561 are within ±200 sf of the 5,000 line. So more than a tenth
of the zone is decided by survey rounding rather than by evidence.

Implications:

- **Rank the whole-lot legal count above area in the cascade.** `legal_lines`
  gives `LT 30` (one whole lot, no fragment) — plat-independent, already
  fetched, and decisive exactly where area is not. `classify_v6`'s
  "one whole lot" rule measures 83% and does not care what the plat
  dimension is.
- **Make `SPLIT_MAX`/`SINGLE_MIN` per-plat**, keyed off the `legal_lines`
  plat name (the part after the `|`). Ridgewood/North Norhill wants roughly
  `SINGLE_MIN≈4,700`, `SPLIT_MAX≈2,800`; Heights/Sunset Heights keeps
  5,000/4,000. A single global pair cannot serve both.
- **This is the blocker for extending the cascade to other markets.** Garden
  Oaks, Oak Forest, Spring Branch and West U are all platted differently
  again; shipping the Heights constants into them would repeat this error
  market by market. `garden_oaks/stage_permits.py` already sidesteps it by
  measuring true depth from the parcel polygon
  (`minimum_rotated_rectangle`, EPSG:2278) instead of thresholding area —
  that is the pattern to port, since 50×100 vs 25×100 is unambiguous
  regardless of plat.

### Permit-ingested pins land unlabeled (multi-market blocker)

`permit_pull.py` contains **no split/single classifier**, so every pin it
inserts arrives with no `ty` and no `prod`. `prodKeyR()` (`index.html:684`)
then returns `null` and the pin renders with no product category — it is not
Split, not Single, and not counted in either legend bucket.

806 Peddie (`pmt_806-peddie-st-77008`, commit `1d3e70e`) is the worked
example: unlabeled from ingest until hand-labelled, despite every available
signal agreeing on Single. This backlog was 163 of 398 DATA records; the
§7 triage brought it to **81**, and the weekly auto-ingest
(`weekly_permit_ingest.sh`, Sundays 07:00) adds more on every run.

Two consequences worth separating:

- The classification gap is silent. Nothing flags an unlabeled pin, so the
  backlog only surfaces when someone traces an individual address.
- Any classifier improvement is retroactive-only until the ingest itself
  classifies. Fixing the cascade does not fix the pins already in DATA, and
  does not stop the next Sunday run adding more.

The natural fix is to run the cascade inside `permit_pull.ingest()` at
insert time and write `ty`/`prod` — with anything short of a confident call
left deliberately unlabeled rather than defaulted, which is the same
discipline the `w>=2` → `needs_review` change applies in v6/v9. This affects
every market that uses the permit-pull path, not just Heights.

### Smaller items

- Whether to demote the chain marker as in §6.4. Deliberately deferred
  until `parcel_events.json` has been exercised as a signal.
- **30** records where HAR `lot` and HCAD `Shape.STArea()` disagree
  (26 HAR-split/HCAD-single, 4 the other way). An earlier draft of this
  file said 27 — that was a different and wrongly-described set (records
  *currently labelled Single that the cascade would flip to Split*, which
  includes HAR-only records with no HCAD area, i.e. not conflicts at all).
  Triaged 2026-08-26: 24 resolve Single, 5 Split, 1 ambiguous.
- `index.html:1059` hardcodes `2 homes` in the `_soloSplit` badge even
  when `units` is higher. Cosmetic, untouched.
- The `_soloSplit` pass runs *after* `DATA` is filtered (`:478` before
  `:481`), so a pin whose twin was merged away can be double-counted.
  Untouched.

## Re-running

```
python3 refresh/parcel_diff.py --verify-only              # counts per vintage
python3 refresh/parcel_diff.py --pairs 2024_Oct-2025_Oct  # no GDAL needed
python3 refresh/parcel_diff.py                            # all pairs
python3 refresh/parcel_diff.py --help-gdb                 # 2026 conversion recipe
```

The 2026 conversion output (`~/hcad-gis/Parcels_2026_Jul/`, 1.5 GB) was
deleted after caching; regenerate it with the `--help-gdb` recipe (~25 s)
if `~/hcad-gis/.parcel_diff_cache/2026_Jul.pkl` is ever cleared.

The sanity gate refuses to write `parcel_events.json` if 614 or 629 E 26th
ever comes out as `SPLIT`. Both are located by coordinate, not account — a
real split reissues the `HCAD_NUM`, so an account lookup would miss exactly
the case being guarded against.
