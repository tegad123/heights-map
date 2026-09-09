# Timeline model Phase 0 — read-only confirmation

No committed files modified. Baseline command: `/Users/nemoclaw/insp-venv/bin/python -B tests/browser_calibration.py --all-markets --output /tmp/timeline-before.json`. The existing harness fixes time to September 8, 2026 for its legacy fixtures. Actual result: eight pages each taxonomy 83/83; Heights fixtures 12/12; page errors [].

## D0a–b: current phase and ETA code
```js
const INSP_PHASE=[
  [/fdn[ -]*wood|fdn[ -]*insul/i,'framing'],
  [/nail pattern|nailing|fire[ -]?wall/i,'exterior'],
  [/brick ties?|\btci\b/i,null], // no structural evidence: arbitrarily timed brick ties / temporary power
  [/1035[ -]*frame|^frame$|rough in|^rough$|rough electric|rough plumb|rough mech|mechanical rough|\bac rough\b/i,'finishing'],
  [/makeup (?:foundation|fdn)|\b(?:form|frm)\b/i,'foundation'],
  [/precon|pre-?fill|sewer|invert|bedding|flowable|bore|manhole|pipe instal|mandrel|utility|apron|flatwork|ele grnd|grnd insp|ditch ?cover|trench cover/i,'sitework'],
  [/sawpole|saw pole|pole final/i,'sitework'], // temp power pole = job start, pre-slab
  // Site / civil / utility work certifies nothing about the house above the slab, so it can never
  // sit above foundation: P1..P5 FINAL + STORM SEWER are the public-works tie-in finals, Site Final /
  // EC = erosion control, Flood Final = elevation cert, TEMP GAS = meter set, WATER SERVICE = yard
  // line, WW Final / Punch List / Restoration = the wastewater civil sub-permit, SLAB COVER = pre-pour.
  // Must precede every generic FINAL / COVER / gas rule below. 2026-09-01 street audit: P1 FINAL was
  // reading as Finishing on foundation-stage homes (710 Waverly, 835 Lawrence), WATER SERVICE as
  // Framing (832 E 27th), 2nd EC as Dried-In (1008 E 28th, 1306 W 24th).
  [/\bp\d ?final\b|site final|flood final|temp gas|storm sewer|culvert|driveway|sidewalk|\bww final\b|\bsw final\b|\bec\b|water service|slab cover|punch list|restoration/i,'sitework'],
  [/elect final|gas final|cc final|add el final|\bv\d final\b|\bc\d final\b|ac final|mech(?:anical)? final|plumb(?:ing)? final/i,'finishing'],
  [/certificate of occupancy|\bc\.?o\.?\b|building final|struct(?:ural)? final|final building|\bfinal\b|\btci\b|reconnect|visitab/i,'market'],
  [/insulation|shower pan|lath|grille|duct seal|egress|sfr kitchen|tree\/shrub|sprinkler|decor/i,'finishing'],
  // DITCH COVER = foundation-era trench cover, must be caught BEFORE the generic \bcover\b dried-in gate
  [/ditch ?cover|trench cover/i,'foundation'],
  // Framed / Drying-In (F4, 2026-09-01): WINDSTORM is the entry point - the windstorm engineer certifies the
  // structure is complete, after which the house dries in and gets siding (street audit: siding 1-4 wks later).
  // Trade COVER rows do not certify a closed structural shell.
  [/windstorm|windstrom/i,'dried_in'],
  // Rough-trades (rough in, top out, gas rough) are the tail end of FRAMING, not dried-in.
  [/rough in|top out|gas test|gas insp|rough electric|rough plumb|rough mech|mechanical rough|\bac rough\b|frame|framing|\brough\b|nail pattern|nailing|brick tie|sheath|fire ?wall|1035/i,'framing'],
  [/1031|fdn|foundation|ground in|ele grnd|grnd insp|\bground\b|slab|piers?|t-beam|footing|sewer|invert|bedding|fill|flowable|bore|manhole|pipe instal|mandrel|utility|precon|prefill|pre-?fill|apron|flatwork|building layout|layout|form survey/i,'foundation'],
  // Unrecognized trade names are not structural-stage evidence.
];
const PHASE_RANK={sitework:0.5,foundation:1,framing:2,dried_in:3,exterior:3.5,finishing:4,market:5,complete:6};
function inspPhase(type,row){
  // Legacy rows without raw status cannot prove full FDN approval.
  if(/1031|fdn[ -]*pm/i.test(type||''))return row&&/^approved$/i.test(row.raw||'')?'framing':'foundation';
  for(const [re,ph] of INSP_PHASE){if(re.test(type||''))return ph;}return null;
}
function structuralFinal(ins){
  return (ins&&ins.inspections||[]).filter(it=>/pass/i.test(it.result||'')&&
    /\bstruct(?:ural)?[ -]+final\b/i.test(it.type||'')&&inspPhase(it.type,it)==='market')
    .sort((a,b)=>String(b.date||'').localeCompare(String(a.date||'')))[0]||null;
}
function inspectionEta(r,now=new Date()){
  const ins=inspForPin(r),done=structuralFinal(ins);
  if(done)return {anchor:'Struct Final',target:done.date||null,months:null,complete:true,overdue:false};
  const passed=(ins&&ins.inspections||[]).filter(it=>it.date&&/pass/i.test(it.result||''));
  for(const [pattern,anchor,months] of [[/^insulation$/i,'INSULATION',5],[/windstorm|windstrom/i,'WINDSTORM',6.5],[/^ground[ -]*in$/i,'GROUND IN',8]]){
    const row=passed.filter(it=>pattern.test(it.type)).sort((a,b)=>String(a.date).localeCompare(String(b.date)))[0];
    if(!row)continue;
    const d=new Date(row.date+'T00:00:00');if(!Number.isFinite(+d))continue;
    // Calendar months, clamped at month end; a half-month is 15.22 days.
    const day=d.getDate();d.setDate(1);d.setMonth(d.getMonth()+Math.floor(months));
    d.setDate(Math.min(day,new Date(d.getFullYear(),d.getMonth()+1,0).getDate()));
    d.setTime(+d+(months%1)*30.44*864e5);
    const remaining=(d-now)/(30.44*864e5),overdue=remaining<0;
    const target=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
    return {anchor,target,months:overdue?null:Math.max(0.5,Math.round(remaining*2)/2),complete:false,overdue};
  }
  return {anchor:'bucket default',target:null,months:null,complete:false,overdue:false};
}
function etaText(r){
  const eta=inspectionEta(r);
  if(eta.complete)return 'Complete';
  if(eta.overdue)return 'overdue vs typical pace';
  const months=monthsLeft(r.id);
  return months==null?'':'~'+months+' month'+(months===1?'':'s')+' to completion';
}
// Popup order: newest first. The feed stores rows in COH grid order (grouped by sub-permit, not by
// date), so a plain reverse() surfaced pre-con civil rows and hid the recent ones behind '+N earlier'.
function inspectionDisplayDate(ins,it){
  if(structuralFinal(ins)&&/insulation|1031[ -]*fdn|fire[ -]?wall|rough in|nail pattern|sewer/i.test(it.type||''))return '';
  return it.date||'';
}
function inspSorted(ins){return ((ins&&ins.inspections)||[]).slice().sort((a,b)=>inspectionDisplayDate(ins,b).localeCompare(inspectionDisplayDate(ins,a)));}
// Display-layer annotations (2026-09-01). Never change a stage or a count.
function inspAnnotations(r,ins){
  const out={notes:[],last:''}; if(!ins)return out;
  const done=structuralFinal(ins);
  if(done){out.last=done.date?'Completed '+done.date:'Complete';return out;}
  const rows=(ins.inspections||[]).filter(it=>it.type); const now=new Date();
  const days=d=>Math.round((now-new Date(d+'T00:00:00'))/864e5);
  const passed=rows.filter(it=>it.date&&/pass/i.test(it.result||''));
  const roughTrades=new Set(passed.filter(it=>/rough/i.test(it.type)).map(it=>/plumb/i.test(it.permit_type||'')?'plumbing':/elect/i.test(it.permit_type||'')?'electrical':/mechan|hvac|air condition/i.test(it.permit_type||'')?'hvac':null).filter(Boolean));
  if(!passed.some(it=>/^insulation$/i.test(it.type))&&(passed.some(it=>/1035[ -]*frame|^frame$/i.test(it.type))||roughTrades.size===3))out.notes.push('insulation imminent');
  if(homePhase(r.id)==='foundation'){
    // FDN package = the structural foundation inspections only; civil/site rows (EC, storm sewer, driveway,
    // P1 FINAL...) also map to foundation but say nothing about when the slab was poured.
    const FDN_PKG=/1031|fdn|foundation|piers?|slab|footing|t-beam|ground in|ele grnd|grnd insp|form survey|layout/i;
    const fdn=passed.filter(it=>inspPhase(it.type,it)==='foundation'&&FDN_PKG.test(it.type)).map(it=>it.date).sort().pop();
    const anyFraming=rows.some(it=>(_PHRANK[inspPhase(it.type,it)]||0)>=_PHRANK.framing);
    if(fdn&&days(fdn)>21&&!anyFraming)out.notes.push('framing likely underway');}
  for(const t of new Set(rows.filter(it=>/pend/i.test(it.result||'')&&(!it.raw||/schedul|request|pending/i.test(it.raw))).map(it=>it.type)))out.notes.push(t+' inspection scheduled');
  const last=rows.filter(it=>it.date&&!/pend/i.test(it.result||'')).map(it=>it.date).sort().pop();
  if(last){const d=days(last),w=Math.floor(d/7);out.last='Last inspection: '+(d<7?d+' day'+(d===1?'':'s'):w+' week'+(w===1?'':'s'))+' ago';}
  return out;}
function inspToPhase(ins){
  // Phase = the FURTHEST phase any PASSED inspection has reached.
  // Construction is monotonic: passed insulation means the house is framed and dried-in,
  // no matter what civil paperwork (ground-in, culvert, storm sewer) posts afterwards.
  // Failed and scheduled inspections never count (a failed Site Final is not completion).
  if(structuralFinal(ins))return 'complete';
  const live=(ins.inspections||[]).filter(it=>it.type&&/pass/i.test(it.result||''));
  let best=null,bestR=0;
  for(const it of live){const p=inspPhase(it.type,it);if(p&&_PHRANK[p]>bestR){best=p;bestR=_PHRANK[p];}}
  return best;
}

```

## D0c: all final strings and permit types
```json
{
  "SAWPOLE FINAL": {
    "ES-SAWPOLE PT": 604
  },
  "Site Final": {
    "SFR New": 116,
    "SFR Substantial": 1,
    "CMFR Non Subst": 1
  },
  "PLUMBING FINAL": {
    "Plumbing Pmt": 369
  },
  "TEMP GAS FINAL": {
    "*PG*TEMP GAS": 365
  },
  "ELECT FINAL": {
    "Electrical Pmt": 364
  },
  "AC FINAL": {
    "HVAC Permit": 364
  },
  "DECOR AD FINAL": {
    "DECOR APPLANCE": 215
  },
  "P1 FINAL": {
    "*P1*ADD-PL-PMT": 273
  },
  "P2 FINAL": {
    "*P2*ADD-PL-PMT": 175
  },
  "Struct Final": {
    "Building Pmt": 335
  },
  "FINAL": {
    "GRADING , FILL": 321,
    "OUTDOOR KITCHEN": 35,
    "DEVEL-REVIEW": 2,
    "CENTRAL VAC": 1
  },
  "15 Final": {
    "Sidewalk,DW,PV": 285
  },
  "ADD EL FINAL 1": {
    "E1-ADDL-ELECT": 72
  },
  "CC FINAL": {
    "CRT/COMPLIANCE": 186
  },
  "WW Final": {
    "Wastewater": 59
  },
  "ADD EL FINAL 2": {
    "E2,ADDL-ELECT": 8
  },
  "ADD AC FINAL 1": {
    "A1-ADDL-HVAC": 11
  },
  "Flood Final": {
    "SFR New": 9,
    "SFR Substantial": 1,
    "CMFR Non Subst": 1
  },
  "C1 FINAL": {
    "C1-DUP/CHNG": 1
  },
  "P3 FINAL": {
    "*P3*ADD-PL-PMT": 37
  },
  "ADD EL FINAL 3": {
    "E3,ADDL-ELECT": 2
  },
  "V2 Final": {
    "RES ELEV INSTL": 17
  },
  "DECO AE FINAL": {
    "ADD DECO APP#2": 4
  },
  "P4 FINAL": {
    "ADDL PL PMT #4": 7
  },
  "Final": {
    "Health Dept": 4,
    "Refrigeration": 2,
    "X7-PPC Overtime": 1
  },
  "AT-FINAL": {
    "AC-EMERGNCY-PT": 4
  },
  "CO FINAL": {
    "CERT OF OCCUP.": 5
  },
  "ADMIN.FINAL": {
    "*PG*TEMP GAS": 4
  },
  "TEMP C/O FINAL": {
    "TEMPORARY C/O": 1
  },
  "V1 Final": {
    "COMM.ELEV.INST": 1
  },
  "ADMIN FINAL": {
    "*P1*ADD-PL-PMT": 7,
    "*P3*ADD-PL-PMT": 2,
    "E1-ADDL-ELECT": 1,
    "ES-SAWPOLE PT": 1
  },
  "DECO AF FINAL": {
    "ADD DECO APP#3": 1
  },
  "ADD AC FINAL 2": {
    "A2-ADDL-HVAC": 1
  },
  "Admin Final": {
    "FM Alarm Permit": 2,
    "Sprinklers Plans": 1
  },
  "ADD EL FINAL 4": {
    "E4,ADDL-ELECT": 1
  },
  "P5 FINAL": {
    "ADDL PL PMT #5": 1
  },
  "SW Final": {
    "Drive/Sidewalk": 1
  },
  "CELL >60 FINAL": {
    "CELL TOWER >60": 1
  },
  "ADD AC FINAL 3": {
    "ADDL-HVAC-PT#3": 1
  }
}
```

## D0d: comments
No comment keys in any inspection row or project. The parser skips the Display Project / Inspection Comments control; it does not emit comments. Exact row keys:
```json
{
  "type": 19314,
  "permit_type": 19314,
  "date": 19314,
  "result": 19314,
  "raw": 19314,
  "inspector": 19314
}
```

## D0e: listing interaction
Raw st=pending bypasses inspection promotion. Sold DATA rows are filtered from live pins. Other listing statuses remain independent tags; onmkt is BUILD_PHASES intersect listed/market. RECONCILE can add pending/off-market without deleting all stage/listed tags.
```js
function applyInspectionPromotions(){
  let changed=false;
  const PROJ=projectPhase();
  for(const r of DATA){
    if(!r.permits||!r.permits.length){ if(r.st!=='pending'&&stripUnevidencedStage(r))changed=true; continue; }
    // pending wins over inspection phase: an under-contract home is spoken-for supply,
    // whatever its trade finals say. Keep the pending tag, skip promotion entirely.
    if(r.st==='pending'){const ty=(LIFE[r.id]&&LIFE[r.id].ty)||(INVENTORY[r.id]&&INVENTORY[r.id].type)||r.ty||null;
      const p0=pt(r.id);const want=['pending'].concat(ty?[ty]:[]);
      if(JSON.stringify(p0.tags)!==JSON.stringify(want)){p0.tags=want;changed=true;}
      continue;}
    const ins=inspForPin(r); if(!ins){ if(stripUnevidencedStage(r))changed=true; continue; }
    let ph=inspToPhase(ins);
    const _pk=projectBaseKey(r); const _pr=['market','complete'].includes(PROJ[_pk])?'finishing':PROJ[_pk]; if(_pr&&_PHRANK[_pr]>(_PHRANK[ph]||0))ph=_pr;
    if(ph==='market'&&!(r.kind==='active'&&r.v!==undefined)){
      // completed but not listed: recent final = imminent supply; old final = built & gone
      const mk=(ins.inspections||[]).filter(it=>it.type&&/pass/i.test(it.result||'')&&it.date&&inspPhase(it.type,it)==='market')
        .map(it=>it.date).sort().pop();
      const ageMo=mk?((new Date())-new Date(mk+'T00:00:00'))/(30.44*24*3600e3):99;
      ph=(ageMo<=6)?'finishing':'built';
    }
    const _lst=(r.kind==='active'&&r.v!==undefined&&r.st!=='pending');
    const p=pt(r.id);
    if(ph==='complete'){
      const ty=(LIFE[r.id]&&LIFE[r.id].ty)||(INVENTORY[r.id]&&INVENTORY[r.id].type)||r.ty||null;
      const want=['complete'].concat(ty?[ty]:[]).concat(_lst?['listed']:[]);
      if(JSON.stringify(p.tags)!==JSON.stringify(want)){p.tags=want;p.inspPromoted=true;changed=true;}
    } else if(ph==='market'){
      // final passed -> ready/on market, keep product type if known
      const ty=(LIFE[r.id]&&LIFE[r.id].ty)||(INVENTORY[r.id]&&INVENTORY[r.id].type)||r.ty||null;
      const want=['market'].concat(ty?[ty]:[]).concat(_lst?['listed']:[]);
      if(JSON.stringify(p.tags)!==JSON.stringify(want)){p.tags=want;p.inspPromoted=true;changed=true;}
    } else if(ph==='built'){
      const ty=(LIFE[r.id]&&LIFE[r.id].ty)||(INVENTORY[r.id]&&INVENTORY[r.id].type)||r.ty||null;
      const want=['built'].concat(ty?[ty]:[]);
      if(JSON.stringify(p.tags)!==JSON.stringify(want)){p.tags=want;changed=true;}
    }
    else if(ph){
      const ty=(LIFE[r.id]&&LIFE[r.id].ty)||(INVENTORY[r.id]&&INVENTORY[r.id].type)||r.ty||null;
      const want=[ph].concat(ty?[ty]:[]).concat(_lst?['listed']:[]);
      if(JSON.stringify(p.tags)!==JSON.stringify(want)){p.tags=want;p.inspPromoted=true;changed=true;}
    }
    else { if(stripUnevidencedStage(r))changed=true; } // nothing passed yet -> no stage, back in the permit layer
  }
  syncListed();
  if(changed){Object.keys(mById).forEach(recolor);renderLegend();refresh();
    // keep Overview and Timeline tabs in sync with inspection-driven phases
    if(typeof buildOverview==='function')buildOverview();
    if(typeof buildTimeline==='function')buildTimeline();
  }
}

```

## Conflicting requirements needing decisions
1. The durations total 217 days from windstorm when 135 interior days plus 21 finals days are separate (~7.1 months). Including finals in 135 gives 196 (~6.4 months).
2. Independent anchors permit cross-property ordering inversions. Strict phase ordering needs an explicit adjustment, or the test must allow anchor-age differences as well as overdue.
3. Harvard has fully Approved 1031-FDN dated 2026-07-29, later than July 9 ground-in. As of September 9: 42 days elapsed - 21-day Framing duration = 21 overdue days, not at least 35.
4. Voight 22030746 has Partial Approval for 1035-Frame and INSULATION, like Munford. The requested sticky rule means MEP Roughs; old Interior Finishing was based on treating partial approvals as full.

## Raw fixture evidence

### 26022264 2005 Harvard St, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "2005 Harvard St, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-09",
      "result": "Failed",
      "raw": "Correction Necessary",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-09",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "Piers AM",
      "permit_type": "Building Pmt",
      "date": "2026-07-06",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-07-29",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    }
  ]
}
```

### 26009059 629 E 26th St, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "629 E 26th St, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-24",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-24",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2026-07-30",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-07-30",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2026-09-04",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2026-07-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Precon",
      "permit_type": "SFR New",
      "date": "2026-07-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Prefill",
      "permit_type": "SFR New",
      "date": "2026-07-17",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "2nd EC",
      "permit_type": "SFR New",
      "date": "2026-09-02",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "3rd EC",
      "permit_type": "SFR New",
      "date": "2026-05-05",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "Site Final",
      "permit_type": "SFR New",
      "date": "2026-05-05",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    }
  ]
}
```

### 25118994 822 Nashua St, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "822 Nashua St, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-06-10",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-06-10",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Piers AM",
      "permit_type": "Building Pmt",
      "date": "2026-06-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2026-06-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-06-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2026-07-22",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "FDN-WOOD/INSUL",
      "permit_type": "Building Pmt",
      "date": "2026-07-22",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2026-05-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    }
  ]
}
```

### 26012829 118 Munford St, Houston, Tx 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "118 Munford St, Houston, Tx 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "DITCH COVER",
      "permit_type": "Electrical Pmt",
      "date": "2026-07-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH",
      "permit_type": "Electrical Pmt",
      "date": "2026-07-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TCI",
      "permit_type": "Electrical Pmt",
      "date": "2026-07-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-05-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Gas Test",
      "permit_type": "Plumbing Pmt",
      "date": "2026-09-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-05-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-08",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "SHOWER PAN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-09-03",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WATER SERVICE",
      "permit_type": "Plumbing Pmt",
      "date": "2026-08-07",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1035-Frame",
      "permit_type": "Building Pmt",
      "date": "2026-07-23",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "Brick Tie",
      "permit_type": "Building Pmt",
      "date": "2026-07-21",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2026-06-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Nail Pattern",
      "permit_type": "Building Pmt",
      "date": "2026-06-25",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-06-01",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "INSULATION",
      "permit_type": "Building Pmt",
      "date": "2026-07-28",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "HVAC Permit",
      "date": "2026-07-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GRILLE SEAL",
      "permit_type": "HVAC Permit",
      "date": "2026-08-19",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Driveway PM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-08-21",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Sidewalk PM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-08-21",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "DECOR APPLANCE",
      "date": "2026-07-28",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2026-05-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS INSP",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-09-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS FINAL",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-09-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    }
  ]
}
```

### 26011885 711 E 25th St A, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "711 E 25th St A, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "DITCH COVER",
      "permit_type": "Electrical Pmt",
      "date": "2026-08-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH",
      "permit_type": "Electrical Pmt",
      "date": "2026-07-30",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-08-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-04-30",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-27",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "SHOWER PAN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-09-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN AM",
      "permit_type": "Building Pmt",
      "date": "2026-05-07",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "1035-Frame",
      "permit_type": "Building Pmt",
      "date": "2026-08-12",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Brick Tie",
      "permit_type": "Building Pmt",
      "date": "2026-08-17",
      "result": "Failed",
      "raw": "Correction Necessary",
      "inspector": ""
    },
    {
      "type": "Fire Wall",
      "permit_type": "Building Pmt",
      "date": "2026-08-12",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "Nail Pattern",
      "permit_type": "Building Pmt",
      "date": "2026-08-12",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-05-06",
      "result": "Failed",
      "raw": "Correction Necessary",
      "inspector": ""
    },
    {
      "type": "INSULATION",
      "permit_type": "Building Pmt",
      "date": "2026-08-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2026-08-12",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "HVAC Permit",
      "date": "2026-07-30",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GRILLE SEAL",
      "permit_type": "HVAC Permit",
      "date": "2026-09-03",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Driveway AM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-05-13",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Sidewalk AM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-05-13",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Culvert",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-05-13",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2026-04-28",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Precon",
      "permit_type": "SFR Substantial",
      "date": "2026-02-26",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "Pre-fill",
      "permit_type": "SFR Substantial",
      "date": "2026-02-26",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "2nd EC",
      "permit_type": "SFR Substantial",
      "date": "2026-02-26",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "3rd EC",
      "permit_type": "SFR Substantial",
      "date": "2026-02-26",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "Site Final",
      "permit_type": "SFR Substantial",
      "date": "2026-02-26",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "Flood Final",
      "permit_type": "SFR Substantial",
      "date": "2026-02-26",
      "result": "Failed",
      "raw": "Action Required",
      "inspector": ""
    },
    {
      "type": "Date Received",
      "permit_type": "Wastewater",
      "date": "2026-08-10",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Str Cut Permit",
      "permit_type": "Wastewater",
      "date": "2026-08-10",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Lane Closure",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Bore and Jack",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Bedding & Fill",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ce-Sand Sample",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Manhole Instal",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Manhole Drop",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "INVERT",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Pipe Instal",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "MH/Pipe Test",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Lab Reports",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Mandrel Test",
      "permit_type": "Wastewater",
      "date": "2026-08-20",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Punch List",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "WW Final",
      "permit_type": "Wastewater",
      "date": "2026-09-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Restoration",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Mylar",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Aband Sewer",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Clean Sewer",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Flowable Fill",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Manufact Plug",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Dispose Waste",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Plug End Main",
      "permit_type": "Wastewater",
      "date": "2026-08-24",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    }
  ]
}
```

### 25071971 112 E 27th St A, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "112 E 27th St A, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "DITCH COVER",
      "permit_type": "Electrical Pmt",
      "date": "2026-02-19",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH",
      "permit_type": "Electrical Pmt",
      "date": "2026-01-29",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "MLS",
      "permit_type": "Electrical Pmt",
      "date": "2026-05-29",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TCI",
      "permit_type": "Electrical Pmt",
      "date": "2026-03-24",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ELECT FINAL",
      "permit_type": "Electrical Pmt",
      "date": "2026-05-29",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-06-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Gas Test",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2025-11-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SHOWER PAN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-04-27",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "PLUMBING FINAL",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1035-Frame",
      "permit_type": "Building Pmt",
      "date": "2026-02-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Brick Tie",
      "permit_type": "Building Pmt",
      "date": "2026-01-21",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Struct Final",
      "permit_type": "Building Pmt",
      "date": "2026-07-07",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2025-11-19",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Fire Wall",
      "permit_type": "Building Pmt",
      "date": "2026-07-07",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Nail Pattern",
      "permit_type": "Building Pmt",
      "date": "2026-02-19",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-07-07",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "INSULATION",
      "permit_type": "Building Pmt",
      "date": "2026-07-07",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2025-12-16",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "HVAC Permit",
      "date": "2026-02-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "AC FINAL",
      "permit_type": "HVAC Permit",
      "date": "2026-06-05",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GRILLE SEAL",
      "permit_type": "HVAC Permit",
      "date": "2026-03-10",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Driveway AM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-04-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Sidewalk AM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-04-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "15 Final",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-06-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Culvert",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-04-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2025-11-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "FINAL",
      "permit_type": "GRADING , FILL",
      "date": "2026-06-11",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TREE/SHRUB FNL",
      "permit_type": "LAND-TREE/SHRB",
      "date": "2026-06-11",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS INSP",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-07-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS FINAL",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-07-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Date Received",
      "permit_type": "Wastewater",
      "date": "2026-06-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Str Cut Permit",
      "permit_type": "Wastewater",
      "date": "2026-06-05",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Lane Closure",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Bore and Jack",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Bedding & Fill",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ce-Sand Sample",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Manhole Instal",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Manhole Drop",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "INVERT",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Pipe Instal",
      "permit_type": "Wastewater",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "MH/Pipe Test",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Lab Reports",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Mandrel Test",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "Punch List",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WW Final",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Restoration",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Mylar",
      "permit_type": "Wastewater",
      "date": "2026-06-25",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    }
  ]
}
```

### 25059398 609 E 25th St, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "609 E 25th St, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "DITCH COVER",
      "permit_type": "Electrical Pmt",
      "date": "2026-01-28",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH",
      "permit_type": "Electrical Pmt",
      "date": "2026-01-05",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "MLS",
      "permit_type": "Electrical Pmt",
      "date": "2026-06-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TCI",
      "permit_type": "Electrical Pmt",
      "date": "2026-02-02",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ELECT FINAL",
      "permit_type": "Electrical Pmt",
      "date": "2026-06-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2025-11-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Gas Test",
      "permit_type": "Plumbing Pmt",
      "date": "2026-03-12",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2025-11-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-05-29",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SHOWER PAN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-03-27",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "PLUMBING FINAL",
      "permit_type": "Plumbing Pmt",
      "date": "2026-05-29",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1035-Frame",
      "permit_type": "Building Pmt",
      "date": "2026-01-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Struct Final",
      "permit_type": "Building Pmt",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2025-11-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Nail Pattern",
      "permit_type": "Building Pmt",
      "date": "2025-12-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "INSULATION",
      "permit_type": "Building Pmt",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2025-11-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "HVAC Permit",
      "date": "2026-01-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "AC FINAL",
      "permit_type": "HVAC Permit",
      "date": "2026-06-01",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GRILLE SEAL",
      "permit_type": "HVAC Permit",
      "date": "2026-04-15",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Driveway AM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-02-19",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Sidewalk AM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "15 Final",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "DECOR APPLANCE",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "DECOR AD FINAL",
      "permit_type": "DECOR APPLANCE",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2025-11-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "FINAL",
      "permit_type": "GRADING , FILL",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "TREE/SHRUB FNL",
      "permit_type": "LAND-TREE/SHRB",
      "date": "2026-06-18",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "STORM SEWER",
      "permit_type": "*P1*ADD-PL-PMT",
      "date": "2026-03-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS INSP",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-03-12",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS FINAL",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-03-12",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    }
  ]
}
```

### 25092767 212 E 24th St, Houston, TX 77008
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "212 E 24th St, Houston, TX 77008",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "DITCH COVER",
      "permit_type": "Electrical Pmt",
      "date": "2026-04-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH",
      "permit_type": "Electrical Pmt",
      "date": "2026-03-27",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "MLS",
      "permit_type": "Electrical Pmt",
      "date": "2026-08-24",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TCI",
      "permit_type": "Electrical Pmt",
      "date": "2026-04-15",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ELECT FINAL",
      "permit_type": "Electrical Pmt",
      "date": "2026-08-24",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-01-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Gas Test",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-01-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-08-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SHOWER PAN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-04-27",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "PLUMBING FINAL",
      "permit_type": "Plumbing Pmt",
      "date": "2026-08-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1035-Frame",
      "permit_type": "Building Pmt",
      "date": "2026-04-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Brick Tie",
      "permit_type": "Building Pmt",
      "date": "2026-03-13",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Struct Final",
      "permit_type": "Building Pmt",
      "date": "2026-08-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2026-01-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Nail Pattern",
      "permit_type": "Building Pmt",
      "date": "2026-02-13",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2026-08-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "INSULATION",
      "permit_type": "Building Pmt",
      "date": "2026-08-25",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2026-02-10",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "HVAC Permit",
      "date": "2026-03-27",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "AC FINAL",
      "permit_type": "HVAC Permit",
      "date": "2026-08-19",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "GRILLE SEAL",
      "permit_type": "HVAC Permit",
      "date": "2026-06-23",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Driveway PM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-07-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Sidewalk PM",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-07-08",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "15 Final",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-07-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Culvert",
      "permit_type": "Sidewalk,DW,PV",
      "date": "2026-07-08",
      "result": "Failed",
      "raw": "No Action Required",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "DECOR APPLANCE",
      "date": "2026-04-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "DECOR AD FINAL",
      "permit_type": "DECOR APPLANCE",
      "date": "2026-08-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SAWPOLE FINAL",
      "permit_type": "ES-SAWPOLE PT",
      "date": "2026-01-15",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "FINAL",
      "permit_type": "GRADING , FILL",
      "date": "2026-08-20",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS INSP",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-07-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "TEMP GAS FINAL",
      "permit_type": "*PG*TEMP GAS",
      "date": "2026-07-14",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    }
  ]
}
```

### 22030746 1033 Voight St, Houston, TX 77009
```json
{
  "status": "Partial",
  "updated": "2026-09-08",
  "scraped_at": "2026-09-08",
  "address": "1033 Voight St, Houston, TX 77009",
  "final_project_inspection_outstanding": true,
  "inspections": [
    {
      "type": "DITCH COVER",
      "permit_type": "Electrical Pmt",
      "date": "2026-01-13",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH",
      "permit_type": "Electrical Pmt",
      "date": "2026-05-28",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2025-11-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Gas Test",
      "permit_type": "Plumbing Pmt",
      "date": "2026-07-28",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "GROUND IN",
      "permit_type": "Plumbing Pmt",
      "date": "2025-11-18",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "ROUGH IN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-05-15",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "SHOWER PAN",
      "permit_type": "Plumbing Pmt",
      "date": "2026-08-31",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "STORM SEWER",
      "permit_type": "Plumbing Pmt",
      "date": "2026-01-30",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN AM",
      "permit_type": "Building Pmt",
      "date": "2025-12-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1035-Frame",
      "permit_type": "Building Pmt",
      "date": "2026-07-21",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "Ele Grnd Insp",
      "permit_type": "Building Pmt",
      "date": "2025-12-17",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "Fire Wall",
      "permit_type": "Building Pmt",
      "date": "2026-07-21",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "Nail Pattern",
      "permit_type": "Building Pmt",
      "date": "2026-08-06",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "1031-FDN PM",
      "permit_type": "Building Pmt",
      "date": "2025-12-16",
      "result": "Failed",
      "raw": "Correction Necessary",
      "inspector": ""
    },
    {
      "type": "Piers PM",
      "permit_type": "Building Pmt",
      "date": "2025-12-16",
      "result": "Failed",
      "raw": "Correction Necessary",
      "inspector": ""
    },
    {
      "type": "INSULATION",
      "permit_type": "Building Pmt",
      "date": "2026-08-04",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "WINDSTORM",
      "permit_type": "Building Pmt",
      "date": "2026-04-09",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "FDN-WOOD/INSUL",
      "permit_type": "Building Pmt",
      "date": "2026-02-06",
      "result": "Passed",
      "raw": "Partial Approval",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "HVAC Permit",
      "date": "2026-05-26",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    },
    {
      "type": "COVER",
      "permit_type": "DECOR APPLANCE",
      "date": "2026-06-04",
      "result": "Passed",
      "raw": "Approved",
      "inspector": ""
    }
  ]
}
```
