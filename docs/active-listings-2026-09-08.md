# Heights active listings — discovery, ingest, reconciliation and display

## Phase 0 — read-only discovery

Discovery preceded implementation. Commands executed: `git status --short`, `git log --format='%h %ad %s' --date=short -- changes refresh/refresh.py`, targeted `sed` reads of index.html, Python JSON decoding of the embedded arrays, and `/Users/nemoclaw/insp-venv/bin/python -B /tmp/active_discovery.py` in Chromium. The browser captured the running application after inspection load, not a Python reimplementation of its classifier. Its reduced, contact-free capture is [active-runtime-baseline-2026-09-08.json](active-runtime-baseline-2026-09-08.json).

Actual output:

```
DATA 376 SOLD 764 SUPPLY 138
complete 57; market 37; under construction 152; deeds 139
raw records 430; raw units 432; runtime represented homes 420
permit linked 252; direct parcel/APN 0; external deed-metadata APN matches 0
```

The requested 422 tracked / 137 supply baseline was not reproduced. Runtime split pairing, synthetic companion weights, zone exclusions and sold filtering change raw-record counts. The capture is a specific runtime state, not proof of what every returning visitor's cached/shared edits display. Verification blocks external writes and uses a controlled empty shared-edit response. A discovery attempt allowing the shared GET produced the same totals but did not establish that the remote service successfully delivered all current edits. The literal 137 baseline would yield `137 - 1 + 45 = 181` under the requested home-addition scenario; the measured counter yields 182.

### D1. Storage and writers

DATA stores `kind`, `st`, `v`, `ty` and `prod`. Tags and notes live in `state.points[id]`, seeded from SEED_POINTS and LIFE, saved in localStorage and shared through the Apps Script endpoint. User tag controls can add/remove them; remote points replace local points on merge. `applyReconcile` runs at seed and remote merge; inspection promotions and `syncListed` subsequently also write tags. Consequently RECONCILE's authoritative intent, raw `st`, and visible tags can diverge.

“Pending / Under Contract” is the `pending` tag. Off Market Single/Split are `off_market_single`/`off_market_split`; the legend suppresses their counts when pending also exists. “Active (Finished)” is `market`. “On the Market (building)” is a runtime intersection of BUILD_PHASES with `listed` or `market`, not a separate stored status. “Needs Clarification” is `needs_clarification`: `applyNC()` adds it for NC_IDS until a fieldEdits product resolves it. A second UC clarification count is computed from missing product classification.

Observed Other counts: pending 14 weighted homes, Off Market Single 5, Split 4, Needs Clarification 6. These differ from the requested 6/4/2; no counts were forced to match the prompt. The construction group has an additional 16 homes lacking product classification. Listed while building is Single 10 plus Split 11, not 10 across both products.

### D2. History and age

```
34176d2 2026-08-18 heights: actives refresh 2026-08-18 — 11 new, 9 drops, HAR dispositions
688842a 2026-07-28 Refresh pipeline stage (a): diff engine + changelog with 7/27-7/28 backfill
```

`refresh/refresh.py` already parses HAR exports, diffs addresses, and folds changes into RECONCILE. This is a human-invoked refresh path, not a scheduled complete listing-status feed. changes/index.json's last update is 2026-08-18. Its latest pass records 51 matched, 9 dropped, 11 new. `syncListed` still infers listing status from legacy DATA fields rather than these September exports or SOLD_DATA.

Reconciliation event ages on September 8: **9 entries 21 days old**, **3 entries 42 days old**, **24 entries 43 days old**. Off: 18 July 27, 1 July 28, 5 August 18. Relist: 2 July 28. Pending: 6 July 27, 4 August 18. These are dated event ages, not universal per-tag freshness timestamps. Free-form lifecycle notes and DATA.sd are not reliable refresh timestamps.

### D3. Supply calculation

RDY=37 and DONE=57 use `phaseBreakdown()`, which sums `UW(id)` weights over pipeline homes by `homePhase()`. The big counter uses `comingOnline(12)`, incrementing by one record. Complete returns null from `monthsLeft`, excluding it from the counter. Product tags can fall back to `market` without passed completion evidence. Pending is not independently excluded in comingOnline, which allows Tabor to contribute.

### D4. Coexisting schema

Tabor's raw row contains `id=act_1207-tabor`, `kind=active`, `v=$1,099,000`, `sd=2026-05-17`, coordinates, product, and no permit/MLS/APN field. The captured tags are `market,pending,active_single,listed`. Its lifecycle note records under contract August 18. SOLD_DATA independently contains `s85478626`, address 1207 Tabor Street, close date **2026-08-31**, sold price **$949,000**. The schema permits independent construction/listing/sale facts; the old UI simply had no join.

### D5. Join keys and coverage

All 430 raw DATA records lack direct MLS/APN/parcel fields. All 252 permit-linked raw records lack a parcel/APN key, and none gains one via the existing deed-metadata ID cross-reference. DealMachine IDs and COH project IDs are not MLS or APN values. HAR actives provide MLS, address and coordinates but no APN. Unit-preserving normalized addresses provide unique joins for all 40 eligible listings; coordinates are supporting evidence, never a proximity-only automatic join. Matching includes the retained `_twin` member of paired pins. Explicit suffix-duplication normalization resolves “830 E 27th Street Street”; its source and map positions are close but coordinates alone did not establish the join. No unit is discarded to force a match.

## Phase 1 — ingest and idempotency

Commands:

```
/Users/nemoclaw/insp-venv/bin/python -B active_ingest.py
/Users/nemoclaw/insp-venv/bin/python -B active_ingest.py --apply
```

Actual first apply: single read 22 / added 22 / updated 0 / excluded 0; split read 19 / added 18 / updated 0 / excluded 1 OOZ_REGEX. **41/41 source classifications match, zero mismatches.** Excluded: **1822 W 23rd Street**, MLS **73224522**. The complete source row and SHA256 are in `pulls/dropped_active_2026-09-08.csv`; pulls is intentionally not committed. Unchanged rows remain in the output and are counted as unchanged, not silently dropped or described as excluded.

The active JSON holds MLS, original list price, DOM, lot size, derived product, builder, list agent, year built, address, coordinates, source row/hash, and as-of date. Original List Price is not current asking price; the UI and schema say so.

Final second-apply output:

```
Single: read 22, added 0, updated 0, unchanged 22, excluded {}
Split: read 19, added 0, updated 0, unchanged 18, excluded {OOZ_REGEX: 1}
crosscheck_mismatches: []
changed_files: []
PASS final idempotency; functions executed ['address_key', 'run']
```

Both snapshot and ledger were compared as bytes before and after the run. The normalization correction was applied before the final idempotency proof.

## Phase 2 — complete reconciliation deliverables

[Full 376-pin reconciliation table, all 41 source listings, and every conflict member](active-reconciliation-2026-09-08.md). [CSV](active-reconciliation-2026-09-08.csv). [Structured JSON including the 57 represented Complete homes](active-reconciliation-2026-09-08.json).

Reproduce with:

```
/Users/nemoclaw/insp-venv/bin/python -B active_reconcile.py docs/active-runtime-baseline-2026-09-08.json
```

A: 9 pending-state/sold candidates: 709 E 17th, 1324 Lawrence, **1207 Tabor**, 1023 Euclid, 710 E 18th, 1229 Prince, 1326 Lawrence, 815 Lawrence Unit A, 611 E 25th Unit A. Includes authoritative pending entries whose visible tags were overwritten by promotions or pairing. The sale at 611 E 25th Unit A predates its July pending event; that temporal inversion needs review and is not sufficient proof of the current transaction closing. **Only Tabor is in the current supply counter.**

B: 43 Complete pins represent 57 homes: **9 address-matched actives, 3 address-matched sold, 45 neither**. Four “neither” entries are unnamed companions inferred by existing weighting; 41 have named addresses. At the project level, 9 pins have active evidence, 3 have sold evidence, one is in both (1322/1324 Lawrence), and 32 whole pins have neither. Those 32 represent 39 homes. Six additional neither homes are companions on partially evidenced pins. A sold companion must not make its active neighbor sold.

C: 1 unmatched input: 1822 W 23rd, year built 2026, legitimately excluded by the explicit zone rule; **zero eligible coverage gaps**.

D: 42 legacy-active addresses absent from these exports (unconfirmed absence); 1 off-market/export-active conflict, 1520 W 21st Unit A. All members are in the detailed report. No absence has been converted into sold or off-market status.

E: 14 active listings at pre-Complete construction stages, compatible with listing before completion; 0 with a simultaneous finished `market` tag. The export itself contains no finished-status field, so it cannot prove a builder is advertising these as finished. Seventeen additional active matches have legacy market/no-stage/paired-state ambiguity and are listed separately. Nine active listings match Complete pins.

## Phase 3 — impact scenarios, no computation change

Measured current counter: **138 pin records**, representing **159 homes**.

- Remove A already in supply: `138 - 1 = 137` (Tabor only).
- Add whole Complete pins with neither evidence using existing pin counting: `138 - 1 + 32 = 169`.
- Requested scenario adding all 45 represented neither homes: `138 - 1 + 45 = 182`, explicitly mixing current pin units and added home units.
- Consistent represented-home scenario: `159 - 1 + 45 = 203`.

The 45 are not proven unsold, unlisted or immediately available. The sold archive and exports have finite coverage; four homes lack individual identities. These are sensitivity estimates for human review, not replacement supply claims.

## Phase 4 — display decision

**Proceeded: 40/40 eligible matches (97.6% of all 41 input rows; the remainder intentionally excluded).** Active Listings has Single Lot 22 and Split Lot 18 controls, counting listings. Existing property popups show dated address-specific active/sold evidence, original list price, DOM, and construction facts. Prior tags/notes/prices are visibly historical. RECONCILE intent is shown as prior recorded status when contradicted. Paired properties retain separate evidence lines. The display never changes tags, DATA or the snapshot calculation.

## Validation evidence

```
/Users/nemoclaw/insp-venv/bin/python -B tests/browser_calibration.py --all-markets --output /tmp/active-fixtures.json
```

Actual: taxonomy 83/83 on each of eight HTML pages; Heights property fixtures 12/12; page errors [].

```
/Users/nemoclaw/insp-venv/bin/python -B tests/active_browser.py
```

Actual: active 40, sold 764, deeds 139, supply 138. Clicking Single Lot produced 22 listings / 22 pins; Split Lot 18 / 18. Popup assertions passed for Tabor, 902 E 25th (Complete/listed), 1623 Blount (Complete/neither), 1322/1324 Lawrence (active/sold pair), and 1520 W 21st A/B (relisted twin). Python and JavaScript normalized keys agree 40/40. Reload left serialized DATA/tags/supply/sold/deeds byte-identical; page errors [].

`git diff --stat` for the existing HTML: `index.html | 3 ++-`, 2 insertions / 1 deletion. Direct comparison of JSON payload substrings against HEAD returned PASS for DATA, SOLD_DATA, RECONCILE, LIFE and SEED_POINTS. DATA SHA256: `95d0052836052ab830ba2286dc65c945b85228131bd3b036f1ae9f95c95c2f92`. No DATA serialization, stage-classifier change, permit/scraper change, sold/deed ingest change, or RECONCILE write occurred.

## Open items

- Resolve pin-versus-home counting and the 137/422 reported baseline versus measured 138/420 before changing supply.
- Review the dated Class A candidates, especially sales predating pending events.
- Validate availability and individual identity of all 45 neither homes, particularly inferred companions.
- Verify present listing status of the 42 absent legacy actives against a complete status export.
- Obtain current asking prices if required; these inputs only supply original list prices.
- Improve per-unit inspection and parcel linkage. Combined project evidence does not separately certify each companion home.
- Reconcile persistent tags/changelog only after human review. The new display does not update old layer counts, ASK aggregates, or the forecast.

## Phase 0 source excerpts

Read with `sed`; computations separately executed by the browser commands above.

### Reconciliation tags — index.html:659

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

### Listing regeneration — index.html:805

```js
function syncListed(){for(const r of DATA){const p=pt(r.id);const should=r.kind==='active'&&r.v!==undefined&&r.st!=='pending';const has=(p.tags||[]).includes('listed');
  if(should&&!has)p.tags=(p.tags||[]).concat(['listed']);
  else if(!should&&has)p.tags=p.tags.filter(t=>t!=='listed');}}
```

### Clarification — index.html:1137

```js
// ---- Needs Clarification: flag unresolved review properties until Spencer sets a product ----
const NC_IDS=["2131318733", "2131421176", "pmt_745-w-17th-st-77008", "pmt_1410-herkimer-st-77008", "pmt_433-w-23rd-st-77008", "pmt_918-dorothy-st-77008", "pmt_1434-herkimer-st-77008", "pmt_949-ridge-st-77009", "pmt_1314-e-28th-st-77009", "act_231-e-26", "act_1011-e-25", "2131191267", "2131194125", "2131284475", "2131537524", "2131538725", "pmt_1602-turnpike-rd-77008", "pmt_822-nashua-st-77008", "pmt_1118-worthshire-st-77008"];
function applyNC(){
  if(!state.tags.needs_clarification)state.tags.needs_clarification={name:'Needs Clarification',color:'#f03e3e'};
  for(const id of NC_IDS){ if(!byId[id])continue; const p=pt(id);
    const resolved=state.fieldEdits&&state.fieldEdits[id]&&state.fieldEdits[id].prod;
    if(resolved){ p.tags=p.tags.filter(t=>t!=='needs_clarification'); }
    else{ p.tags=p.tags.filter(t=>t!=='active_single'&&t!=='active_split');
      if(!p.tags.includes('needs_clarification'))p.tags.push('needs_clarification'); } }
  const _ncset=new Set(NC_IDS);
  for(const id in state.points){ if(_ncset.has(id))continue; const tg=state.points[id].tags;
    if(tg&&tg.includes('needs_clarification'))state.points[id].tags=tg.filter(t=>t!=='needs_clarification'); } }
applyNC();
applyFieldEdits();applyPosEdits();markers.forEach(mm=>mm.setStyle(mkStyle(mm._rec.id)));
// ---- shared edits: pull from remote at load; server wins for edit fields ----
```

### Legend and listing/building counts — index.html:1411

```js
function tagCount(tid){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(!t.includes(tid))continue;
  if(tid.indexOf('off_market')===0&&t.includes('pending'))continue; // pending is never counted as Off Market
  n+=UW(id);}return n;}
const TY2K={active_single:'Single Lot',active_split:'Split Lot',active_cd:'Common Driveway',off_market_single:'Single Lot (Off Market)',off_market_split:'Split Lot (Off Market)'};
function typeKeyOf(id){const r=byId[id];return r?prodKeyR(r):null;}
function comboCount(a,b){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(typeKeyOf(id)!==TY2K[a])continue;const bld=BUILD_PHASES.some(p=>t.includes(p));if(!bld)continue;if(b==='onmkt'){if(_mkted(t))n+=UW(id);}else{if(t.includes(b)&&!_mkted(t))n+=UW(id);}}return n;}
const BUILD_PHASES=['sitework','foundation','framing','dried_in','exterior','finishing'];
const _mkted=t=>t.includes('listed')||t.includes('market');
function ucCount(){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(BUILD_PHASES.some(p=>t.includes(p)))n+=UW(id);}return n;}
function ucTypeCount(ty){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(typeKeyOf(id)===TY2K[ty]&&BUILD_PHASES.some(p=>t.includes(p)))n+=UW(id);}return n;}
function ucNCCount(){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(!typeKeyOf(id)&&BUILD_PHASES.some(p=>t.includes(p)))n+=UW(id);}return n;}
function mktCount(){return tagCount('market');}
function listedCount(){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(_mkted(t)&&!BUILD_PHASES.some(p=>t.includes(p)))n+=UW(id);}return n;}
function listedTypeCount(k){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(_mkted(t)&&!BUILD_PHASES.some(p=>t.includes(p))&&typeKeyOf(id)===k)n+=UW(id);}return n;}
function listedReadyCount(k,ready){let n=0;for(const id in state.points){if(!mById[id])continue;const t=state.points[id].tags||[];if(!t.includes('listed')||typeKeyOf(id)!==k)continue;const r=t.includes('market')||t.includes('complete');if(r===ready)n+=UW(id);}return n;}
```

### Snapshot algorithms — index.html:1666

```js
const PHASE_MONTHS={sitework:9,foundation:8,framing:6,dried_in:4,exterior:4,finishing:2,market:0};
// A permit pin that inspections promoted carries a real phase tag; treat it like a tracked pin.
function isPromotedPermit(r){if(!r||r.kind!=='permit')return false;const t=(state.points[r.id]||{}).tags||[];return t.some(x=>['complete','sitework','foundation','framing','dried_in','exterior','finishing','market'].includes(x));}
function inPipeline(r){return r.kind!=='permit'||isPromotedPermit(r);}
function primaryStage(pid){const t=(state.points[pid]||{}).tags||[];
  if(t.includes('built')) return null; // completed long ago, not pipeline supply
  for(const k of PHASE_ORDER) if(t.includes(k)) return k;
  if(t.includes('active_single')) return 'active_single';
  if(t.includes('active_split')) return 'active_split';
  if(t.includes('deed')) return 'deed'; return null;}
function monthsLeft(pid){const r=byId[pid]||{};
  const s=primaryStage(pid); if(s===null||s==='deed'||s==='complete') return null;
  const eta=inspectionEta(r);if(eta.complete||eta.overdue)return null;if(eta.anchor!=='bucket default')return eta.months;
  const t=(state.points[pid]||{}).tags||[];
  const compM=r.comp?(function(){const d=new Date(r.comp+'T00:00:00'),n=new Date();return (d.getFullYear()-n.getFullYear())*12+(d.getMonth()-n.getMonth());})():null;
  // ready homes: 0 (punch list: 1)
  if(t.includes('market')) return t.includes('punch')?1:0;
  // under construction: NEVER "available now" — future comp date wins, overdue comp falls back to phase estimate
  const ph=['finishing','exterior','dried_in','framing','foundation','sitework'].find(p=>t.includes(p));
  if(ph){ if(compM!==null&&compM>0) return compM; return Math.max(1,(PHASE_MONTHS[ph]!==undefined?PHASE_MONTHS[ph]:1)); }
  if(s==='active_single'||s==='active_split') return (compM!==null&&compM>0)?compM:0;
  if(compM!==null) return Math.max(0,compM);
  const tm=(((state.points[pid]||{}).notes)||'').match(/timeline:\s*(\d+)\s*month/i); return tm?parseInt(tm[1],10):null;}
function stageColor(s){ return state.tags[s]?state.tags[s].color:'#8c857a';}
// ============================================================
// SUPPLY FORECAST — Spencer's core question: how many homes come
// online (reach market) within a given window, and what phase is
// everything in right now. Built on inspection-driven phases.
// ============================================================
const PHASE_LABELS={sitework:'Sitework / Pre-Pour',exterior:'Exterior Close-In',complete:'Complete',foundation:'Foundation',framing:'Framing',dried_in:'Framed / Drying-In',finishing:'Interior Finishing',market:'Active'};
const PHASE_SEQ=['complete','sitework','foundation','framing','dried_in','exterior','finishing','market'];

// Every home currently in the construction pipeline (tracked builds + inspection-promoted permits).
function pipelineHomes(){
  return DATA.filter(inPipeline).filter(r=>{
    const s=primaryStage(r.id);
    return s && s!=='deed';           // exclude raw deed transfers (pre-construction)
  });
}

// A home's current construction phase (foundation..market), from inspections/tags.
function homePhase(pid){
  const t=(state.points[pid]||{}).tags||[];
  if(t.includes('built')) return null; // completed long ago — grey pin keeps its color, no false FINISHED ON MARKET badge
  for(const p of PHASE_SEQ) if(t.includes(p)) return p;
  if(t.includes('active_single')||t.includes('active_split')) return 'market';
  return null;
}

// Count of homes by phase — the "what phase is everything in" snapshot.
function phaseBreakdown(){
  const out={complete:0,sitework:0,foundation:0,framing:0,dried_in:0,exterior:0,finishing:0,market:0};
  for(const r of pipelineHomes()){const p=homePhase(r.id); if(p&&out[p]!==undefined)out[p]+=UW(r.id);}
  return out;
}

// How many homes reach market within N months (cumulative supply curve).
// A home "comes online" when its monthsLeft <= N.
function comingOnline(months,prodTag){
  let n=0; const list=[];
  for(const r of pipelineHomes()){
    const _T=TY2K[prodTag];
    if(_T){const k=prodKeyR(r);if(k){if(k!==_T)continue;}else if(!((state.points[r.id]||{}).tags||[]).includes(prodTag))continue;}
    else if(prodTag && !((state.points[r.id]||{}).tags||[]).includes(prodTag))continue;
    const ml=monthsLeft(r.id);
    if(ml!==null && ml!==undefined && ml<=months){n++; list.push(r);}
  }
  return {count:n, homes:list};
}

// The full supply curve at standard checkpoints — feeds the redesign's forecast view.
function supplyCurve(){
```
