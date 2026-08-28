# Phase 1 · Track 1 · Step 1 — Database Schema & Migration Design Review

**Status: DESIGN REVIEW — awaiting approval. Nothing built, nothing migrated.**
Prepared 2026-08-28. Inputs: full data-shape inventory of the working tree
(three read-only exploration passes), docs/phase1-scope.md,
docs/split-classification-notes.md, notes/clarification_triage.csv.

---

## 1. What actually exists — the inventory

### 1.1 The DATA arrays (8 markets, 1,731 records)

| market | records | id styles | notes |
|---|---|---|---|
| heights | 407 | HCAD numeric ×142, pmt_ ×172, act_ ×93 | only market with SOLD subsystem |
| montrose | 213 | act_/pmt_/acq_ | |
| westu | 101 | act_/pmt_/acq_/ACT## | no u/lot/bb fields at all |
| riveroaks | 40 | act_/pmt_/acq_ | |
| springbranch | 417 | act_/pmt_/acq_ | largest permit set |
| springvalley | 6 | sv_/act_ | hand-built, no permits |
| timbergrove | 38 | tg_/tgp_ only | own id convention |
| gardenoaksoakforest | 509 | act_/pmt_ | RECONCILE populated (281 off) |

**Fields in all 8**: `id, a, llc, lat, lng, kind, ty, prod, f, v, c, sd`.
**Partial**: `permits` (7 — not springvalley), `u`/`lot`/`bb` (7 — not westu),
`st` (4), `comp` (4), `units` (2), `soldPrice`/`soldDate` (2), `note` (heights only, 2 recs).

**Enums as found**: `kind` = permit(1018) | active(567) · `ty` = active_single(1337) |
active_split(144) · `prod` = Single Lot(850) | Deed Transfer(407) | Split Lot(116) |
Common Driveway(100) | Frontloader(2) · `st` = sold(383) | pending(12, heights only).

**Dirty shapes the migration must normalize (without losing the original)**:
- `v` ("$600,000") and `lot` ("6680") are display strings → numeric + raw column.
- `c` is polymorphic: list of `{n, p[], e[]}` contacts (771 entries) **or** empty string `""` (437 rows).
- `f` is dual-purpose: comma-separated flag list in heights/GO+OF/timbergrove, free prose
  elsewhere — and prose contains commas inside numbers ("5,000 sqft lot"), so it is
  **not safely splittable**. Kept raw; curated tokens extracted separately (§5 D2).
- `comp` is an estimated-completion **date** despite the name.
- Two id namespaces (slug ids vs MLS numerics) coexist, bridged only by
  `changes[].merges` entries.
- `permits[]` entries: `owner, desc, val, ptype("13" always), proj` + `permitDesc`/`vald`
  (present in some generations, constant "Building Pmt").

### 1.2 Heights-only structures (index.html)

- `SOLD_DATA` — 712 sold comps × 24 fields (`cp, lp, sq, psf, cd, mo, dom, yb, coh, band,
  win, prod, svl, sch, la, ba, bl, nr, p, …`). The 4-band `band` field is **overwritten
  client-side** by a 13-band re-bucket — bands are derived, not data.
- `SOLD_METRICS` — fully derived aggregate (as_of 2026-08-12, 72-cell cube). Recompute, never migrate.
- `LIFE` (240), `INVENTORY` (14), `NC_IDS` (19), `DEED_PULL` — heights-only today,
  structurally market-generic.
- `ZONE_RING` polygon splice (other markets splice by regex only).

### 1.3 Per-page control structures

- `SEED_POINTS` — dict id → `{notes, tags[]}` (117–407 per market). Additive-only merge on
  return visits; contributes annotations, never geometry.
- `RECONCILE` `{off, relist, pending}`, entries `{t: single|split, d: date}` — populated in
  heights (24/2/10) and GO+OF (281/0/0), empty stubs elsewhere. Machine-generated from
  `changes/` by refresh/refresh.py. **Derived state** — the changelogs are the truth.
- `OUT_OF_ZONE` regexes (springvalley.html still carries the leaked Heights copy),
  `HD_POLYS` (GO+OF empty), `REMOTE_EDITS_URL` ('' in GO+OF — no live sync there),
  `MARKET_METRICS` in **three incompatible schemas** (absorption / HAR / null).

### 1.4 Sidecar stores

| store | shape | volume | schema note |
|---|---|---|---|
| `<market>_permits.json` ×7 | list of `{proj, address[, owner]}` | 793 | proj unique in every file — clean natural key |
| `inspections[_market].json` ×8 | dict proj → `{status, updated, address, scraped_at, inspections[]}` | 802 rollups, **18,498 line items** | items `{type, date, result, inspector}`; 130 raw type strings; results Passed/Failed/Pending; springvalley `{}` |
| `refresh/parcel_events.json` | list | 458 | SPLIT 156 / VANISHED 120 / RESHAPE 103 / ASSEMBLY 43 / PARTIAL 36; account arrays; vintage pairs; coordinate-matched (HCAD reissues accounts on split) |
| `changes/**/changes_*.json` | changelogs | 4 files | buckets dropped(317)/new(17)/relisted(2)/excluded(3)/merges(3)/dispositionUpdates(25) + sources + counts — **the auditable event source** |
| `heights_off_market.csv` + 7 siblings | 14-col CSV | heights 24, GO+OF 281, 6 stubs | display overlay; RECONCILE-driven |
| `pulls/quarantine_*.csv` | 2 header generations (4-col, 5-col +MARKET) | 16 rows | old rows are heights-era, need MARKET backfill |
| `<market>_acquisitions.json` ×4 | deed-transfer records | montrose 83, springbranch 204, westu 63, riveroaks 25 | riveroaks older generation (`in_river_oaks` vs `zip/corporate/id`) |
| `upperkirby_holdout.json` | 30 full DATA-shape records | | a 9th market held outside config |
| `notes/clarification_triage.csv` | 231 rows × 18 cols | **GITIGNORED** | RESOLVED-SINGLE 176 / GENUINELY-AMBIGUOUS 46 / RESOLVED-SPLIT 9; every cascade signal materialized |
| `heights_review_FINAL.csv` | 202 labeled rows | | `final_source='hand'` is NOT independent provenance (accept.py stamps it) |
| garden_oaks/ staging set | staged pins, allowlists, solds, review CSVs | | one-off chain; staged pins (31+113) not yet promoted |
| HCAD parcel geojsons | 7k+ parcels | garden_oaks/ | `legal_lines`, areas — the classification evidence base |
| `store_backup_2026-07-28.json`, `refresh/staging/remote_edits_snapshot.json` | edit-store snapshots | | fieldEdits/offMarketEdits history |

### 1.5 Runtime semantics the schema must reproduce (not lose)

1. **Five edit-override structures** (Apps Script shared blob, full-blob overwrite,
   known last-write-wins race): `points[id].{notes,tags}`, `fieldEdits[id].prod`
   (→ derives `r.ty`), `posEdits[id]=[lat,lng]`, `pairOverrides.off[]`,
   `offMarketEdits[id].{disposition,note,updated}` (the only one with newest-wins).
2. **Phase is not stored** — inspection promotions write tags (furthest-**passed**
   inspection, failed/pending never count, 548-day stale guard, project rollup by
   address-base, `pending` short-circuit, stale-market→built demotion), and
   `homePhase` reads tags. Monotonic per CLAUDE.md.
3. **Pairing engine** derives `_twin`/`_pairKey`/`units` at load (master-ref `M #proj`,
   unit letters, ±2 house numbers <90m); suppressed by `pairOverrides.off`.
   **Derived — never migrated.** One hardcoded merge (710 Waverly, 3 pins → 1).
4. **Two independent "sold" concepts**: DATA rows with `st='sold'` (footer "closed
   sales") vs SOLD_DATA comps (analytics). Both must exist distinctly.
5. `applyReconcile` is an idempotent tag-rewriter that runs on every load —
   off-market records are **tagged, never deleted**.

---

## 2. Proposed Postgres schema

Conventions: `uuid` surrogate PKs; every migrated row keeps its `legacy_id`; raw
source strings preserved alongside normalized columns; enums as lookup tables
(cheap to extend when market #9 brings a new value); `created_at/updated_at`
everywhere; RLS-ready (step 3).

### 2.1 `markets` + `market_zips`  — absorbs market_config.py

```sql
markets (
  slug          text primary key,          -- 'heights', 'montrose', …
  name          text not null,
  boundary      jsonb,                     -- geojson FeatureCollection; NULL = box-only (westu)
  coord_box     numeric[4] not null,       -- lat_min, lat_max, lng_min, lng_max
  east_lng      numeric,                   -- heights only (-95.370)
  enabled       boolean not null default true,
  ingest_order  int not null,
  legacy_html   text,                      -- 'index.html' etc., until step-2 cutover
  meta          jsonb                      -- BUILD strings, MARKET_METRICS raw, misc
)
market_zips (market_slug fk, zip text, primary key (market_slug, zip))
```
77008 and 77019 are legitimately shared → m2m, not an array. springvalley and
upperkirby enter as `enabled=false` rows (§5 D3). **Until step 4, market_config.py
stays the pipelines' authority** — the table mirrors it; a `check_config_parity`
script asserts equality so drift is impossible during the transition.

### 2.2 `properties` — the DATA array, atomized

```sql
properties (
  id             uuid primary key,
  market_slug    text fk not null,
  legacy_id      text not null,            -- 'pmt_…', 'act_…', HCAD numeric, …
  address_raw    text not null,            -- exactly as in DATA.a
  address_norm   text,                     -- permit_pull.norm_addr()-style
  lat, lng       numeric not null,
  kind           text fk lookup,           -- permit | active
  status         text fk lookup,           -- sold | pending | NULL
  owner_entity   text,                     -- llc
  price_cents    bigint,  price_raw text,  -- from v
  sale_date      date,                     -- sd (only when date-shaped; raw kept in extras)
  lot_sqft       int,     lot_raw  text,
  bed_bath       text,                     -- bb, display string
  est_completion date,                     -- comp
  units          int not null default 1,
  dealmachine_url text,                    -- u
  flags_raw      text,                     -- f, verbatim (see §5 D2)
  note           text,                     -- manual-coords caveats etc.
  extras         jsonb not null default '{}',  -- lossless catch-all: soldPrice/soldDate,
                                               -- non-date sd values, any future stray field
  unique (market_slug, legacy_id)
)
```
`ty` is **not stored**: it is `prod`-derived (`Split Lot`→active_split, else
active_single) exactly as `applyFieldEdits` already derives it — one source of truth.
The `extras` jsonb is the migration's lossless floor: any field the schema doesn't
model lands there byte-preserved, so "must not lose fields" holds by construction.

### 2.3 `contacts` — PII isolated

```sql
contacts (id uuid pk, property_id fk, name text, phones text[], emails text[], position int)
```
Owner phones/emails (771 entries) leave the property row so step-3 RLS can deny the
client role this table wholesale (§5 D1). The `c=""` polymorphism dies here: empty
string → zero rows.

### 2.4 `permits` — de-embedded + merged with scrape lists

```sql
permits (
  id uuid pk, market_slug fk, proj text not null,
  property_id  uuid fk null,               -- null = scrape-list-only entry
  owner text, description text, valuation_raw text, valuation_cents bigint,
  ptype text, permit_desc text,
  in_scrape_list boolean not null,         -- was in <market>_permits.json
  embedded       boolean not null,         -- was in DATA[].permits[]
  unique (market_slug, proj)
)
```
Resolves the flagged denormalization: today a permit lives inside its property
record AND (as proj+address) in the scrape-list JSON. One row, two provenance flags;
the inspection scraper's list becomes `select proj where in_scrape_list`.

### 2.5 `inspections` + `inspection_items` + `inspection_types`

```sql
inspections (id uuid pk, market_slug fk, proj text,      -- fk (market_slug, proj) → permits
             rollup_status text,                          -- Passed|Partial|Pending|'None'
             updated date, scraped_at date, address_raw text,
             unique (market_slug, proj))
inspection_items (id uuid pk, inspection_id fk, type_raw text,
                  type_id fk → inspection_types null,     -- mapped lazily
                  date date, result text fk lookup,       -- Passed|Failed|Pending
                  inspector text, position int)
inspection_types (id pk, raw text unique, canonical text, phase_hint text)
```
18,498 items; the 130 raw type strings get a lookup with `phase_hint` seeded from
the existing `INSP_PHASE` regex table — the phase-promotion logic becomes a SQL
view instead of client JS at step-2 cutover (same furthest-passed semantics).

### 2.6 `sales` — SOLD_DATA now, Track-5 normalizer target later

```sql
sales (id uuid pk, market_slug fk, mls_id text,           -- 's97528053' → '97528053'
       address_raw text, lat, lng numeric,
       close_price_cents bigint, list_price_cents bigint,
       sqft int, close_date date, dom int, year_built int,
       cohort text fk lookup,                             -- nc | resale
       product text fk lookup,                            -- Single Lot | Split Lot | Unclassified
       list_agent text, buyer_agent text, builder text, school text,
       not_representative boolean,                        -- nr
       presold boolean,                                   -- p
       source text fk lookup not null,                    -- har_csv | trestle | migration
       source_batch uuid fk → pipeline_runs,
       unique (market_slug, mls_id, source))
```
`psf`, `svl`, `band`, `win`, `mo` are **derived** (the UI already re-buckets band
client-side into 13 bands) — computed in views, never stored. `SOLD_METRICS`
becomes a materialized view with the same `{n, med_psf, med_dom, avg_svl_pct,
med_price, presold_n, absorption_per_month}` leaf shape. This table IS the
Track-5 normalizer's target: HAR-CSV adapter and Trestle adapter both write here.

### 2.7 `classifications` — label changes as auditable events

```sql
classifications (
  id uuid pk, property_id fk not null,
  label        text fk lookup null,        -- Single Lot|Split Lot|Common Driveway|
                                           -- Frontloader|Deed Transfer|NULL = explicitly unlabeled
  state        text not null,              -- applied | proposed | held_pending | superseded
  evidence_rank int,                       -- 1 parcel-event · 2 unit-letter · 3 legal-count ·
                                           -- 4 area · 5 chain-marker · 6 review  (per docs)
  evidence     jsonb,                      -- the signals that produced it
  source       text not null,              -- 'migration:<commit>' | 'triage_csv' | 'cascade:vN'
                                           -- | 'user:<uuid>' | 'hand(untrusted)'
  created_at   timestamptz not null default now()
)
plat_thresholds (plat_name text pk, split_max_sf int, single_min_sf int,
                 median_lot_sf int, source text)
```
Current label = latest `applied` per property (view `current_classification`).
This is the scope doc's "label change is an auditable event": nothing overwrites,
`applied` supersedes. Seeds at migration: every current `prod` (one `applied` event,
source `migration:<commit>`), the 231 triage rows (176 RESOLVED-SINGLE + 9
RESOLVED-SPLIT as `proposed` with their `deciding_signal` as evidence; 46
GENUINELY-AMBIGUOUS as `held_pending`), and heights_review_FINAL labels with
source `hand(untrusted)` — the docs are explicit that `final_source='hand'` isn't
independent provenance, so the schema says so. `plat_thresholds` makes the per-plat
threshold problem (3,346 dead-zone parcels) config-as-data, keyed by the plat name
parsed from `legal_lines`. Unlabeled pins become a queryable queue
(`current label IS NULL`) instead of invisible.

### 2.8 `status_events` — the changes/ changelogs, first-class

```sql
status_events (id uuid pk, property_id fk null, market_slug fk not null,
               event text fk lookup,       -- off_market|relist|pending|merge|exclude|
                                           -- disposition_update|new
               disposition text fk lookup null,  -- sold|terminated|unconfirmed|under contract
               effective_date date, source text not null,  -- changelog file / 'ground truth …'
               payload jsonb)              -- merge from/to, exclusion rule, etc.
```
RECONCILE's `{off, relist, pending}` and the off-market CSVs become **views over
this table** (latest event per property wins, buckets disjoint by construction —
the same invariants refresh.py asserts today). Business rule preserved: pending ≠
off_market, excluded from off-market exports. refresh/refresh.py and the HTML
marker blocks are untouched until each market's step-2 cutover.

### 2.9 `property_edits` — the edit backend, race-free by design

```sql
property_edits (id uuid pk, property_id fk, field text fk lookup,
                -- prod | position | notes | tags | off_market | pair_off | stage_tag
                value jsonb, author text not null,   -- step 3: user uuid; migration: 'legacy'
                created_at timestamptz default now())
```
Per-field append-only log. Two editors touching different fields can no longer
clobber each other (the Apps-Script full-blob overwrite race documented 07-31 dies
structurally). Current state = latest per (property, field) — matches today's
newest-wins `offMarketEdits` semantics, extends it to everything. Migration seeds:
SEED_POINTS + LIFE + INVENTORY notes/tags (as `notes`/`tags`/`stage_tag` events,
author 'seed'), remote-edits snapshots + store_backup (fieldEdits → `prod`,
posEdits → `position`, pairOverrides → `pair_off`, offMarketEdits → `off_market`
with their original `updated` timestamps).

### 2.10 Supporting tables

```sql
parcel_events (id uuid pk, event text, vintage text, lat, lng numeric,
               parent_sf numeric, child_sf numeric, sum_parent_sf, sum_child_sf,
               acct_continuity boolean, raw jsonb)
parcel_event_accounts (parcel_event_id fk, role text, -- parent|child
                       hcad_acct text, address text)
quarantine (id uuid pk, market_slug fk, proj text, address text, reason text,
            detail text, run_date date, resolved_at timestamptz, resolution text)
pipeline_runs (id uuid pk, kind text,     -- pull|ingest|migration|sold_import
               market_slug fk null, started_at, finished_at,
               summary jsonb)             -- fixes ingest_summary.json's single-slot overwrite
migration_snapshots (id uuid pk, market_slug, taken_at, source_commit text,
                     sha256 text, snapshot jsonb)   -- §4
```

### 2.11 Explicitly NOT migrated (derived state, recomputed)

Pairing (`_twin`/`_pairKey`/units-summing — stays a read-time derivation; the
710 Waverly hardcode becomes a recorded `merge` status_event), SOLD_METRICS,
RECONCILE blocks, MARKET_METRICS (3 schemas — unified later as views over
sales+properties), band/window buckets, `_s` search strings, homePhase, DATA_ALL.

---

## 3. Hosting recommendation: **Supabase (Pro, ~$25/mo)**

This choice is load-bearing because step 2 (API) and step 3 (auth) inherit it.

| option | API layer | auth + roles | ops burden | verdict |
|---|---|---|---|---|
| **Supabase Pro** | PostgREST auto-API over views | built-in, RLS row policies | none | **recommended** |
| Neon | none — build one | none — build one | low | good PG, but steps 2–3 become custom builds |
| DO managed PG / existing droplet | build | build | patching, backups, TLS | keeps the "depends on our box" smell Phase 1 exists to remove |
| Firebase | yes | yes | none | not relational; classification history + joins don't fit |
| Hasura + Neon | GraphQL | JWT plumbing | medium | heavier than a 1.7k-record map needs |

Why it fits *this* system specifically:
- **Step 2's "thin API" is nearly free**: expose curated SQL views
  (`api_properties`, `api_current_classification`, `api_reconcile`, `api_sold_metrics`)
  through PostgREST — records by market / product / phase / tag without writing a server.
  Views are the API contract, which also caps PostgREST lock-in: anything can serve a view.
- **Step 3's team/client model is RLS**: `client` role → `SELECT` on api_* views
  filtered by a `user_markets` join, zero access to `contacts`; `team` role → writes
  to `property_edits`/`classifications`. This replaces the Apps-Script blob with
  authenticated per-field writes — the race fix and the auth land together.
- Storage bucket holds migration snapshots + raw pull CSVs off-repo (ends the
  "raw CSVs must never be committed" tension for cloud pipelines in step 4).
- Scheduled Edge Functions are a candidate step-4 runner (decision deferred to step 4;
  GitHub Actions remains the fallback — nothing in this schema binds to either).
- Cost matches the scope doc's budget line.

Risks, stated: PostgREST idioms in the frontend (mitigated by the views-as-contract
rule above); Supabase auth vendor coupling (standard JWT — replaceable); free-tier
pausing is a non-issue on Pro. Data is plain Postgres — `pg_dump` restores anywhere,
which is also the DR story.

---

## 4. Migration design — verified, reversible, dry-run-first

New `migrate/` package (repo, committed; pure Python + psycopg, no framework).
**The site never reads from the DB in step 1** — cutover is step 2+, per market,
so migration risk is contained entirely inside the DB.

### 4.1 Pipeline: extract → transform → load → verify, per market

1. **Extract** — parse the repo's market HTML (`DATA`, `SEED_POINTS`, `RECONCILE`,
   `LIFE`, `INVENTORY`, `NC_IDS`, globals) + every sidecar in §1.4 into one
   canonical snapshot JSON per market; `sha256` it; record `(market, source_commit,
   sha256)` in `migration_snapshots` (and the snapshot itself — the audit trail
   survives even if repo history rewrites). **Pre-flight**: cache-busted fetch of
   the live page must parse to the identical DATA sha256 as the repo file (the
   deploy-check discipline) — proves we're migrating what clients see.
2. **Transform** — pure functions snapshot → row sets. Every source field maps to a
   column or lands verbatim in `extras`/`raw` jsonb: **loss is structurally
   impossible**, divergences (westu's missing fields, riveroaks' older acquisitions
   generation, quarantine's two header gens) are absorbed by nullability + extras,
   not special-cased code paths.
3. **Load** — one transaction per market: `DELETE` the market's scope (FK-cascaded),
   insert all rows, write a `pipeline_runs(kind='migration')` record. Idempotent:
   re-running a market is safe and is also the **rollback-forward** path.
4. **Verify** — hard asserts, any failure rolls the transaction back:
   - record counts: DATA records == properties rows; per-kind, per-status counts equal;
     sidecar counts equal per table (permits, inspections, items, sales, events, edits).
   - id-set equality: source legacy ids == `properties.legacy_id` set, exactly.
   - per-field non-null parity: for every source field, count of records having it
     == count of rows/extras carrying it.
   - **round-trip checksum**: project DB rows back into source shape (a `to_data_record()`
     inverse), canonical-JSON sha256 must equal the extract's per-record sha256 —
     field-exact, record by record; first mismatch printed with a diff.
   - cross-refs: every embedded `permits[].proj` exists in `permits`; every inspection
     proj has a permit row or is explicitly flagged; every triage `data_id` resolves to
     a property or is logged unresolved (the known ~30 group-A address-keyed rows).
   - invariant checks: RECONCILE buckets disjoint; status_events reproduce the exact
     RECONCILE dict when projected through the view.
5. **Report** — per-market verification report written to
   `docs/phase1/migration-verify-<market>.md` and committed. Same shape as the
   Stage-1 pipeline validation reports.

### 4.2 Modes and ordering

- `--dry-run` (default): extract + transform + verify-against-source in memory,
  print the full report, touch nothing.
- `--apply --market <slug>`: one market. Order: **westu first** (smallest field
  surface, 101 records), then riveroaks, timbergrove, springvalley(disabled),
  montrose, springbranch, gardenoaksoakforest, **heights last** (largest surface:
  SOLD subsystem, LIFE/INVENTORY, populated RECONCILE, NC_IDS, DEED_PULL).
- Schema itself is versioned migration files (`migrate/schema/00N_*.sql`) applied
  by a tiny runner recording to a `schema_migrations` table — reversible by
  down-scripts, rebuildable from scratch.

### 4.3 Rollback story

Step 1 creates a parallel data plane; the site keeps reading its HTML. Therefore:
- bad load → transaction already rolled back by a failed verify;
- bad market discovered later → `DELETE` market scope, re-run from its snapshot;
- lose confidence entirely → drop schema; zero user impact at every point.
The DATA arrays + RECONCILE rules remain in force and authoritative until each
market passes step-2 cutover verification. Nightly/weekly pipelines are not
modified by anything in this step.

---

## 5. Decisions flagged for approval

| # | decision | recommendation |
|---|---|---|
| D1 | **Contacts PII** (771 owner names/phones/emails) | migrate into `contacts`, RLS denies `client` role entirely; team-only. Confirm no client-facing use is intended. |
| D2 | **`f` field** | keep verbatim in `flags_raw`; extract only a curated token set (Corporate Owner, Cash Buyer, Off Market, YB ####, …) into tags. No naive comma-split — prose values make it lossy. |
| D3 | **springvalley + upperkirby_holdout** | migrate both as `enabled=false` markets (6 + 30 records) so nothing lives outside the DB; springvalley's OUT_OF_ZONE leak gets fixed when its market is wired (tracked, untouched now). |
| D4 | **clarification_triage.csv is gitignored** | capture it into `classifications` during migration (176/9 proposed + 46 held_pending). It's currently one `rm` away from gone. |
| D5 | **Migration order** | westu-first shakedown, heights last (§4.2). |
| D6 | **Hosting** | Supabase Pro (§3). |

## 6. What approval unlocks (and what it doesn't)

Approved → build order: schema SQL files → extract/transform with dry-run reports
for all 8 markets (still no DB) → Supabase project + apply schema → migrate
westu → full verify → remaining markets → final cross-market verification report.
Each stage shown before the next runs.

Not unlocked: no site changes, no pipeline changes, no API, no auth, no cutover —
those are steps 2–4 with their own reviews.
