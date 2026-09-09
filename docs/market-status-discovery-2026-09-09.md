# Phase 0 — market-status discovery

Read-only baseline at git 71033db, captured 2026-09-09 before ingest. Runtime uses clean browser storage and a blocked shared-edits response; individual users may have different local/remote historical tags. No external writes were sent.

Commands invoked:
```text
/Users/nemoclaw/insp-venv/bin/python -B tests/timeline_browser.py --checks --output /tmp/market-baseline.json
/Users/nemoclaw/insp-venv/bin/python -B /tmp/market_capture.py --output /tmp/market-runtime.json
```
The capture adds raw DATA, state.points, SEED_POINTS, RECONCILE, tagNames and SOLD_DATA to the existing browser evaluation; otherwise it uses the same page initialization. Captured runtime is preserved in market-status-baseline-2026-09-09.json.

Actual runtime output:
```json
{
  "supply": 144,
  "columns": {
    "foundation": 46,
    "framing": 11,
    "exterior": 29,
    "mep_roughs": 7,
    "insulation": 13,
    "interior": 55,
    "mep_finals": 20,
    "complete": 52
  },
  "uc": 233,
  "deed": 139,
  "sold": 764
}
```

## D1 — storage and tag counts
| Key | Raw seed tags on 430 DATA records | Runtime tags on 376 paired pins |
|---|---:|---:|
| market | 0 | 21 |
| pending | 9 | 11 |
| listed | 0 | 63 |
| active_single | 38 | 43 |
| active_split | 34 | 20 |
| off_market_single | 8 | 9 |
| off_market_split | 8 | 6 |
| needs_clarification | 0 | 19 |

Active (Finished) is market; Pending / Under Contract is pending; listed feeds the on-market/building presentation. Active Single/Split and Off Market Single/Split are independent product/status tags. Needs Clarification is a review/product flag, not market evidence. Counts overlap. DATA fields also include kind, st, v, sd, soldPrice and soldDate (the latter two occur on six rows each).

The original runtime capture’s SEED_POINTS object aliases state.points, so the raw seed counts above are parsed separately from the source assignment, not from that mutated object.

## D2 — writers and freshness
git log identified 34176d2 (2026-08-18 12:46:24 -0500), the last dated active refresh in changes/, and 042180b (2026-09-08 23:27:07 -0500), the independent active ingest. The latter writes heights_active.data.json and explicitly leaves tags/supply alone. Existing refresh/refresh.py generates dated RECONCILE state from changes/*.json; there is no automatic all-status refresh against construction/sold evidence.
Tags are seeded, transformed by LIFE and syncListed, re-applied from RECONCILE after seeding and remote merge, and editable through browser storage/shared edits. Dates in RECONCILE are July 27/28 and August 18; individual tags have no timestamp. _sharedSlice supplies a whole-payload updated timestamp.

## D3 — supply computation
Current 144 is home-weighted UW, not raw pin count. Complete returns null from monthsLeft and is excluded. Unfinished inspection-derived phases count only when their ETA is <=12 months; custom/sold_off_market categories are excluded by inPipeline. Pending/HAR sold status is not consulted.

## D4 — simultaneous axes
DATA supplies the stable property id, address, permits, coordinates and optional legacy listing fields. state.points[id] supplies overlapping tags/notes. homePhase(id)/inspectionEta(record) supplies the construction axis. SOLD_DATA is a separate transaction array. activeEvidence(member) joins sales and the September 8 active snapshot by normalized address. No embedded MLS or sold-record foreign key exists. A separate market evidence snapshot can carry MLS/status/closing and resolve to property/member IDs without rewriting DATA.

## D5 — join reliability
Invoked parser: 430 DATA records; all 430 have coordinates; 428 distinct normalized addresses; 0 MLS fields; 0 APN fields. 252 records contain permits; 0/252 have an external APN cross-reference in heights_deed.data.json, so 252 lack complete parcel linkage. Coordinates are not property identity and were not used for nearest-neighbor matching.
Executed address joins: active 58/59, pending 12/12, sold 14/48 unique paired pins; total 84/119 (70.6%). With construction phase: active 39/59, pending 9/12, sold 3/48; total 51/119 (42.9%). Units/fractions retained; twin addresses resolve to their own members on the shared project. The 35 unmatched source rows are one active and 34 sold; G also enumerates the 33 matched rows without construction evidence.

## D6 — sold relationship and Tabor
764 separate sales pins existed before this ingest. Popups use normalized-address joins, including paired members; transaction identity remains independent of property/project identity. 1207 Tabor is MLS 85478626, sold August 31 for $949,000, already in the archive. Runtime phase is null and permit list empty. Runtime tags are market, pending, active_single, listed; note says Lifecycle: Under contract as of 2026-08-18. Never treat market as a construction completion certificate.

## Code excerpts (exact current source; unchanged by this work)

```js
function syncListed(){for(const r of DATA){const p=pt(r.id);const should=r.kind==='active'&&r.v!==undefined&&r.st!=='pending';const has=(p.tags||[]).includes('listed');
  if(should&&!has)p.tags=(p.tags||[]).concat(['listed']);
  else if(!should&&has)p.tags=p.tags.filter(t=>t!=='listed');}}
```

```js
function monthsLeft(pid){
  const r=byId[pid];if(!r)return null;
  const eta=inspectionEta(r);return eta.complete?null:eta.months;
}
```

```js
function pipelineHomes(){
  return DATA.filter(inPipeline).filter(r=>{
    const s=primaryStage(r.id);
    return s && s!=='deed';           // exclude raw deed transfers (pre-construction)
  });
}
```

```js
function comingOnline(months,prodTag){
  let n=0; const list=[];
  for(const r of pipelineHomes()){
    const _T=TY2K[prodTag];
    if(_T){const k=prodKeyR(r);if(k){if(k!==_T)continue;}else if(!((state.points[r.id]||{}).tags||[]).includes(prodTag))continue;}
    else if(prodTag && !((state.points[r.id]||{}).tags||[]).includes(prodTag))continue;
    const ml=monthsLeft(r.id);
    if(ml!==null && ml!==undefined && ml<=months){n+=UW(r.id); list.push(r);}
  }
  return {count:n, homes:list};
}
```

```js
function applyReconcile(pts){
  for(const id in RECONCILE.off){
    const p=pts[id]; if(!p) continue;
    const e=RECONCILE.off[id], want='off_market_'+e.t;
    let tg=Array.isArray(p.tags)?p.tags:[];
    tg=tg.filter(t=>t!=='active_single'&&t!=='active_split');
    if(!tg.includes(want)) tg.push(want);
    p.tags=tg;
    if(typeof p.notes==='string'){
      if(!/Off market as of \d{4}-\d{2}-\d{2}/.test(p.notes)) p.notes='Off market as of '+e.d+'. '+p.notes;
    } else p.notes='Off market as of '+e.d+'. ';
  }
  for(const id in RECONCILE.relist){
    const p=pts[id]; if(!p) continue;
    const want='active_'+RECONCILE.relist[id].t;
    let tg=Array.isArray(p.tags)?p.tags:[];
    tg=tg.filter(t=>t!=='off_market_single'&&t!=='off_market_split');
    if(!tg.includes(want)) tg.push(want);
    p.tags=tg;
    if(typeof p.notes==='string')p.notes=p.notes.replace(/Off market as of \d{4}-\d{2}-\d{2}\. /g,'');
  }
  for(const id in (RECONCILE.pending||{})){ // under contract: pending only, never off-market
    const p=pts[id]; if(!p) continue;
    let tg=Array.isArray(p.tags)?p.tags:[];
    tg=tg.filter(t=>t!=='off_market_single'&&t!=='off_market_split');
    if(!tg.includes('pending')) tg.unshift('pending');
    p.tags=tg;
  }
}
```

## Executed layer counts
`python -B tests/market_status_check.py --three` invoked the actual layer count functions and returned:
```text
LEGACY_COUNTS {"finishedOnMarket": 54, "needsClarification": 26, "onMarketBuilding": {"active_cd": 0, "active_single": 14, "active_split": 13}}
```
On the Market (building) is a derived row, not a stored tag: `_mkted(t)` accepts `listed` OR `market`, then `comboCount` requires an unfinished construction phase and the product. Its total is 27 homes. The Needs Clarification layer count (26) differs from the literal stored tag count (19): it selects construction records without a resolved product. At 71033db, Complete already has product checkboxes, verified by the existing fixture; the requested new market-status disclosure structure remains deferred.
