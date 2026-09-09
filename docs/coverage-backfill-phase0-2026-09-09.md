# Coverage backfill — Phase 0 diagnosis, 2026-09-09

Phase 0 only. **Phases 1–3 did not run**: this session is the same remote
Linux container as the Allston investigation, and both the COH portal and the
HCAD geocoder are blocked by the environment's network policy. D5 says stop and
report in that case, so that is what this is. Nothing in the repo was modified;
the one command that writes was pointed at a scratchpad copy of `index.html`.

Environment note: the brief gives `/Users/nemoclaw/jarvis/heights-map` and
`/Users/nemoclaw/insp-venv`. Neither exists here. Working tree is
`/home/user/heights-map` at `cbef3a2`.

---

## D1 — Window logic

`permit_pull.py` has **no window of its own**. The portal's date fields default
to empty, and the script only fills them when `--from`/`--to` are passed:

```python
ap.add_argument('--from', dest='date_from', default='',
                help='BDT date window start, YYYYMMDD (server-side filter)')
ap.add_argument('--to', dest='date_to', default='',
                help='EDT date window end, YYYYMMDD')
```

```python
# permit_pull.py:140 — pull()
# Date window: YYYYMMDD ONLY (any other format -> "under Maintenance" wedge)
for fld, val in (('#edit2', date_from), ('#edit3', date_to)):
    if val:
        assert re.fullmatch(r'\d{8}', val), f'date {val!r} must be YYYYMMDD'
        pg.fill(fld, val)
```

The trailing window is imposed by the **wrapper**, not the engine
(`nightly_permit_pull.sh:27`):

```sh
FROM=$(date -v-14d +%Y%m%d)
TO=$(date +%Y%m%d)
```

**So a normal run reaches back exactly 14 days.** Called with no `--from`/`--to`
the portal returns everything it has — a wide-window pull needs no code change,
only different arguments.

### A second, independent window that Phase 1 must not trip over

`ingest()` drops anything whose project-number year prefix is below
`--min-proj-year`, default **25**:

```python
if int(proj[:2]) < min_proj_year:
    skipped['old_proj'] += 1
    dropped.append((proj, addr_raw, 'OLD_PROJ', f'proj year {proj[:2]} < {min_proj_year}')); continue
```

A 24-month backfill from 2026-09-09 reaches 2024-09-09, so **the 2024 slice
would be discarded as `OLD_PROJ` at the default**. Phase 1 must pass
`--min-proj-year 24`, or accept losing that slice knowingly. It lands in the
ledger either way, so it will not be silent — but it will be gone.

## D2 — Pull history

Cannot be reconstructed to the depth asked, and the reason is structural:

| Artifact | Status |
|---|---|
| `pulls/` (CSVs, `pull_log.txt`, `ingest_log.txt`, `LAST_GOOD_PULL`) | gitignored (`.gitignore:4`), absent from this container |
| `deploy.log` | gitignored; recoverable from history, but it is the **inspection scraper** log, not the permit pull log |
| Repo history | begins **2026-08-28** (`c35415b`, initial import) — nothing before that exists to inspect |

`git log --all --name-only` finds no `pull_log`, `ingest_log`, `dropped_*`,
`quarantine_*` or `LAST_GOOD_PULL` ever committed.

What git *can* prove is ingest activity, via `heights_permits.json` — the file
`ingest()` updates on every apply:

```
$ git log --format='%ad %h %s' --date=short -- heights_permits.json
2026-08-30 9fd49b1 heights: weekly auto-ingest 2026-08-30 — 2 pin(s), 1 quarantined
2026-08-28 c35415b docs: Phase 1 productization scope
```

**One permit ingest has ever applied in this repo's visible history**
— 2026-08-30, 2 pins. The only other scheduled Sunday in range, 2026-09-06,
produced no commit at all.

Daily commit activity, whole history:

```
2 2026-08-28   2 2026-08-30   1 2026-08-31   3 2026-09-01
5 2026-09-03   1 2026-09-07  16 2026-09-08  21 2026-09-09
```

Silent days: **08-29, 09-02, 09-04, 09-05, 09-06** — a three-day silence from
09-04 through 09-06 that swallows the 09-06 Sunday ingest window. That is
consistent with the machine being down, but it is not proof: a Sunday ingest
that legitimately found nothing to apply also commits nothing.

### Correction to the brief's premise

The brief says "the cron runs Mon/Thu 5am". That is the **inspections** scrape.
The permit schedule is different (`catchup_check.sh:6`, CLAUDE.md):

- nightly permit **pull** — daily 05:30 (`com.heightsmap.permitpull`)
- weekly **ingest** — Sundays 07:00 (`com.heightsmap.permitingest`)

And the Mon/Thu inspection cron did **not** miss a run in the visible window —
`inspections.json` commits land 08-31 (Mon), 09-03 (Thu), 09-07 (Mon), plus an
extra refresh 09-08. So "the Mac was offline repeatedly Sep 1–9" is not
supported for the inspection job. For the permit pull it is simply unknown,
because its log is gitignored.

## D3 — Earliest coverage

DATA permit rows carry no issue date; the project number's 2-digit year prefix
is the only date signal. Distribution over the 252 DATA rows holding permits:

| Project year | DATA rows | `heights_permits.json` |
|---|---:|---:|
| 2022 | 11 | 11 |
| 2023 | 2 | 2 |
| 2024 | 5 | 8 |
| 2025 | 158 | 172 |
| 2026 | 76 | 81 |

`inspections.json` holds 6,580 dated records, earliest **2022-04-21**, latest
2026-09-10.

**Coverage starts in 2022 — but none of it came from this pipeline.** With
`min_proj_year=25` the ingest engine cannot produce a 2022/2023/2024 row at
all. Those 18 pre-2025 rows are hand-authored, from the original import. The
pipeline's own practical coverage floor is project year 25, and its observed
contribution is the 2 pins of 2026-08-30.

## D4 — H2 quantified

Composition of DATA (static parse of the file, 430 rows):

| | count |
|---|---:|
| rows carrying ≥1 permit | 252 |
| rows with no permit | 178 |
| rows whose id is `pmt_*` | 174 |
| **permit-carrying rows with a NON-`pmt_` id** | **78** |

Those 78 are the important number. They are lead/sold/deed identities that
**already hold permits in the same row** — so the schema does not merely
tolerate multiple identities per address, it already represents them that way.
All 78 were present in the initial import `c35415b`; `ingest()` has never
produced one.

**Shadowed permits in the COH data we already hold: 0.**

Cross-referencing every no-permit DATA row against the 281 distinct normalized
addresses in `heights_permits.json` + `inspections.json` (using
`permit_pull.norm_addr`, the same function ingest uses) returns **no matches**.
Every held COH permit is already attached to a DATA row.

### The mechanism is real — confirmed by invocation, not by reading

A three-row fixture through the actual ingest, against a scratchpad copy:

```
$ python3 permit_pull.py --ingest --from-csv fixture.csv --html ./index_copy.html
candidates after filter+dedupe: 1  skipped: {'dup_proj': 0, 'dup_addr': 2,
                                  'not_sfres': 0, 'old_proj': 0, 'ooz_addr': 0}
```

- `615 ALLSTON ST` → **DUP_ADDR skipped.** The lead row `2131149358` carries no
  permit, and it still blocked one. H2 confirmed.
- `2225 SINGLETON ST` → DUP_ADDR skipped. Correct: that row already holds
  proj 25039460.
- `742 ALLSTON ST` → survived dedupe, reached geocode, died on the blocked HCAD
  call.

### Correction to the brief's premise

The brief calls 615 Allston "a confirmed instance" of shadowing. It is a
confirmed instance of *the mechanism firing*, as above. It is **not** evidence
that a real permit was lost there: `heights_permits.json` and `inspections.json`
contain no permit at 615 Allston. Whether one exists is a question only a COH
pull can answer, and it is the same question as 742/224. Phase 2's fixture
requirement — "615 Allston must gain its permit and construction phase" —
cannot be satisfied unless COH actually returns a permit for it.

### Blast radius

Prospective only. Against held data the fix lands **0** permits, because
nothing held is shadowed. Its value is on future pulls; its cost is below.

## D5 — Reachability: COH is NOT reachable from here

```
$ curl -o /dev/null -w "%{http_code}" https://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm
curl: (56) CONNECT tunnel failed, response 403
$ curl -o /dev/null -w "%{http_code}" "https://arcweb.hcad.org/.../MapServer/0?f=json"
curl: (56) CONNECT tunnel failed, response 403
```

Proxy's own record:

```
2026-09-09T22:18:16 connect_rejected  gateway answered 403 to CONNECT
                    (policy denial or upstream failure) -> cohtora.houstontx.gov:443
2026-09-09T22:18:16 connect_rejected  ... -> arcweb.hcad.org:443
```

Both the pull (COH) and the geocode (HCAD) are blocked, so **Phase 1 and
Phase 3 cannot run here at all** — not the pull, and not an ingest of a CSV
someone else pulled, since every insertable row must be geocoded.

Also blocked: cdnjs and unpkg, so Leaflet and maplibre never load and the
browser test suites (`tests/market_status_check.py`, `tests/full_timeline_check.py`)
cannot run either. Note `hcad_geocode()` does not catch network errors — a
blocked or flaky HCAD aborts the whole ingest with a raw `URLError` traceback
rather than a `GEOCODE_FAIL` ledger row. Worth hardening, out of scope here.

### Partial runtime measurement that *was* possible

Chromium is present and Playwright installs from PyPI, so `index.html` was
loaded for real. Execution stops at the first `L.*` call (`"L is not defined"`),
but everything before it — the zone splice, the Waverly merge, the split-lot
pairing, `UNITS`/`UW` — is real code that really ran:

```json
{"rows": 376, "droppedByPairMerge": 33, "homesTotal": 420,
 "permitRows": 204, "distinctProjects": 231, "pmtIdRows": 144,
 "mergedIdentityRows": 60, "noPermitRows": 172, "coincidentCoordGroups": 2}
```

**These do not match the brief's baseline** (422 tracked homes, 152 permits).
`homesTotal` measures 420 and distinct permit projects measure 231. The gap is
unexplained and is flagged rather than reconciled: this probe stops before the
remote merge and legend build, so it is a floor, not the final runtime state.
Confirm the 422/152 figures on the Mac before treating any delta as a result.

---

## Phase 2 design question — STOP, this would ship duplicate pins

Phase 2 step 2 asked whether the fix creates duplicates. **It does**, and the
instruction was to stop and report rather than ship them.

The renderer builds **one marker per DATA row**, and deliberately spreads
coincident coordinates apart so both stay clickable (`index.html:1098`):

```js
// spread coincident pins (e.g. units A/B/C at one address) so each is individually clickable
const dispLL={};{const grp={};for(const r of DATA){const k=r.lat.toFixed(6)+','+r.lng.toFixed(6);(grp[k]=grp[k]||[]).push(r);}
  for(const k in grp){const a=grp[k];if(a.length<2){dispLL[a[0].id]=[a[0].lat,a[0].lng];continue;}
    const rad=0.000058*(a.length>4?1.5:1),cl=Math.cos(a[0].lat*Math.PI/180)||1;
```

and the home total sums every row (`index.html:1116`):

```js
const HOMES_TOTAL=DATA.reduce((a,r)=>a+(r.units||1),0);
```

So the literal fix as specified — build DUP_ADDR from permit identities only,
leave the insert path alone — makes ingest insert `pmt_615-allston-st-77007`
**alongside** the surviving lead row `2131149358`. Result: two markers ~6 m
apart on one parcel, and `HOMES_TOTAL` inflated by one per shadowed address.

The 78 hand-authored merged rows show the intended shape: **one row, one
identity, a populated `permits` array**. So the correct fix is a *merge* path,
not an insert path — on an address match against a permit-less row, append the
permit to that row's `permits` rather than creating a new row.

That is a bigger change than the brief scopes, and it collides with hard rule 1.
The current splice appends before the closing `]`, which never rewrites an
existing row. A merge must edit one existing row's serialized JSON in place.
That is still achievable as a surgical single-row string replacement, but it is
a different operation with different failure modes, and it needs a decision
before anyone writes it. Three questions for you:

1. **Merge or insert?** Merge is the only option that matches the 78 existing
   rows and avoids duplicate pins. Confirm.
2. **Which row's fields win** when a lead row (DealMachine `v`, `sd`, `lot`,
   `f`, `u`, contacts) absorbs a permit — and does the row keep its DealMachine
   id, or take the `pmt_` id? Keeping the DealMachine id preserves every
   existing reference to it, including the client classification lists.
3. **Does `prod`/`ty` get recomputed** from the permit, or does the lead's
   existing product classification stand?

Given D4 returns 0 shadowed permits against held data, there is no urgency to
get this wrong: the fix changes nothing until a pull actually returns a permit
at a lead's address.

---

## What must run on the Mac

Phase 0's D2 gap closes with the first two; Phase 1 is the rest.

```sh
cd ~/jarvis/heights-map && source ~/insp-venv/bin/activate

# D2: the pull history this container cannot see
cat pulls/pull_log.txt | tail -40
cat pulls/ingest_log.txt
cat pulls/LAST_GOOD_PULL
grep -i -h allston pulls/permits_*.csv | sort -u          # did a pull ever return it
grep -i -h allston pulls/dropped_*.csv pulls/quarantine_*.csv

# Phase 1: wide-window pull, 24 months, three Heights zips. PULL ONLY.
for Z in 77007 77008 77009; do
  python3 permit_pull.py --zip $Z --ptype Structural \
      --from 20240909 --to 20260909 --out pulls/backfill_${Z}_20260909.csv
done
grep -ci . pulls/backfill_*.csv                            # COH row counts
grep -i allston pulls/backfill_*.csv                       # the 742 / 224 test

# Phase 1 dry-run. --min-proj-year 24 or the 2024 slice dies as OLD_PROJ.
python3 permit_pull.py --ingest --min-proj-year 24 \
    --from-csv pulls/backfill_77007_20260909.csv \
    --from-csv pulls/backfill_77008_20260909.csv \
    --from-csv pulls/backfill_77009_20260909.csv
cut -d, -f4 pulls/dropped_$(date +%F).csv | sort | uniq -c | sort -rn
```

The headline number the brief asks for — COH returns vs. DATA holds — falls out
of `grep -c` on the pull CSVs against the 231 distinct projects measured above.
Do not `--apply` before the dry-run is reviewed and the Phase 2 design question
is settled.

## Open items

1. **Trailing window.** 14 days is the whole H1 exposure: one missed Sunday
   ingest plus a >14-day pull gap loses permits permanently, and nothing in the
   repo records the loss. Recommend widening `nightly_permit_pull.sh` `FROM` to
   `-v-45d` — cheap (the portal filters server-side), and it makes any single
   missed run recoverable by the next one. Not changed here: cron is out of
   scope per the brief.
2. **`pulls/` is gitignored,** so pull and ledger history die with the machine.
   Consider committing `pull_log.txt` / `ingest_log.txt` / `dropped_*.csv`
   (not the raw CSVs) so coverage questions are answerable from the repo.
3. **`hcad_geocode()` has no network error handling** — a blocked HCAD aborts
   the run instead of producing `GEOCODE_FAIL` ledger rows.
4. **Baseline mismatch** — 422/152 in the brief vs. 420/231 measured. Reconcile
   before treating post-ingest deltas as results.
5. **615 Allston's fixture status** is unresolvable until COH is queried.
