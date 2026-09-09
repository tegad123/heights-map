options=>{
 const results=[];
 const check=(name,condition,detail=null)=>results.push({name,pass:!!condition,detail});
 const today=timelineDay(new Date().toISOString().slice(0,10));
 const rows=DATA.map(r=>({r,phase:homePhase(r.id),product:prodKeyR(r)||'Unknown',eta:inspectionEta(r)}));
 let pairs=0,violations=[];
 for(const a of rows)for(const b of rows){
  if(a.product!==b.product||!(PHASE_RANK[a.phase]>PHASE_RANK[b.phase])||a.eta.baseDays===null||b.eta.baseDays===null)continue;
  pairs++;
  if(a.eta.baseDays>b.eta.baseDays+1e-8)violations.push({later:a.r.a,earlier:b.r.a,laterBase:a.eta.baseDays,earlierBase:b.eta.baseDays});
 }
 check('Every same-product phase pair: base timeline monotonic',!violations.length,{pairs,violations});
 check('Displayed forecasts = property base + overdue only',rows.every(x=>x.eta.remainingDays===null||x.eta.remainingDays===x.eta.baseDays+x.eta.overdueDays));
 check('No-permit records have no phase or ETA',rows.filter(x=>!x.r.permits?.length).every(x=>x.phase===null&&x.eta.target===null));
 check('Complete requires all five finals and no ETA',rows.filter(x=>x.phase==='complete').every(x=>completionFinal(inspForPin(x.r))&&x.eta.complete&&monthsLeft(x.r.id)===null));
 check('Stage counts are finite',Object.values(phaseBreakdown()).every(Number.isFinite));
 const oldFraming=phaseTimeline('framing',timelineDate(today-35));
 const freshFraming=phaseTimeline('framing',timelineDate(today));
 check('Five-week Framing is two weeks later than fresh Framing',oldFraming.remainingDays-freshFraming.remainingDays===14,{oldFraming,freshFraming});
 const oldExterior=phaseTimeline('exterior',timelineDate(today-200));
 check('Overdue can legitimately reorder phases',oldExterior.remainingDays>freshFraming.remainingDays);
 check('INT.CAB through Complete is exactly 135 days',PHASE_DAYS.interior+PHASE_DAYS.mep_finals===135);
 check('Invalid anchor refused',phaseTimeline('framing',null)===null);
 if(options.heights){
  const get=proj=>rows.find(x=>x.r.permits?.some(pm=>pm.proj===proj));
  const specs=[['26022264','framing','2026-07-29'],['26009059','exterior','2026-09-04'],['25118994','exterior','2026-07-22'],['26012829','interior','2026-07-28'],['26011885','interior','2026-08-17'],['25071971','complete','2026-07-07'],['25059398','complete','2026-06-18'],['25092767','complete','2026-08-25'],['22030746','interior','2026-08-04']];
  for(const [proj,phase,anchor] of specs){const x=get(proj);check('Real fixture '+proj,x?.phase===phase&&x.eta.anchorDate===anchor,{phase:x?.phase,eta:x?.eta});}
  const h=get('26022264'),w=get('26009059'),n=get('25118994');
  check('Harvard: three weeks overdue, later than 629',h.eta.overdueDays===21&&h.eta.target>w.eta.target,{harvard:h.eta.target,windstorm:w.eta.target});
  check('629: Partial windstorm is exterior and about 6.5 months',w.phase==='exterior'&&w.eta.months===6.5);
  check('822: overdue for roughs and later than 629',n.eta.overdueDays>0&&n.eta.target>w.eta.target);
  check('711: 135 days from insulation is approximately January 2027',get('26011885').eta.target==='2026-12-30');
  const no=rows.find(x=>x.r.id==='2131194125');check('830 E 26th no permit/no phase/no ETA',no?.phase===null&&no.eta.target===null);
  const oldPhase=inspPhase,oldEta=inspectionEta,oldComplete=completionFinal;
  try{
   inspPhase=(type,row)=>/1035[ -]*frame|^insulation$/i.test(type||'')&&row?.raw==='Partial Approval'?null:oldPhase(type,row);
   check('Mutant: full-approval-only stickiness is caught on Munford',inspToPhase(INSPECTIONS['26012829'])!=='interior');
   inspPhase=oldPhase;
   // Actual former ground-in + 8-month countdown reverses the primary fixture.
   inspectionEta=(r)=>{const ins=inspForPin(r);const wind=ins?.inspections.find(it=>/windstorm/i.test(it.type)&&inspectionPassed(it));const ground=ins?.inspections.find(it=>/^ground in$/i.test(it.type)&&inspectionPassed(it));const anchor=wind||ground;return {target:anchor?timelineDate(timelineDay(anchor.date)+(wind?195:240)):null};};
   check('Mutant: old flat-offset rule is caught on Harvard/629',inspectionEta(h.r).target<inspectionEta(w.r).target);
   inspectionEta=oldEta;
   completionFinal=structuralFinal;
   check('Mutant: Struct-only completion is caught',inspToPhase({inspections:[{type:'Struct Final',date:'2026-09-01',raw:'Approved',result:'Passed'}]})==='complete');
  }finally{inspPhase=oldPhase;inspectionEta=oldEta;completionFinal=oldComplete;}
 }
 if(options.fixtures){for(const f of options.fixtures.properties){
  const r=byId[f.rendered_id||f.id],actual=r?homePhase(r.id):'missing';
  const pass=phase=>f.forbidden?!f.forbidden.includes(phase):phase===f.new_expected;
  check('Retained fixture '+f.property,!!r&&pass(actual)&&(!f.permit||!INSPECTIONS[f.permit]||pass(inspToPhase(INSPECTIONS[f.permit]))),{actual});
 }}
 check('Supply counts homes including pairs',comingOnline(12).count===comingOnline(12).homes.reduce((n,r)=>n+UW(r.id),0));
 readyMonths=12;applyReadyFilter();readyMonths=0;applyReadyFilter();
 const legend=document.getElementById('legend');
 check('Eight snapshot columns and Complete checkboxes',PH_ABBR.length===8&&PH_ABBR.every(([k])=>CONSTRUCTION_PHASES.includes(k))&&!!legend.querySelector('[data-sel="active_single|complete"] .mbox')&&!legend.querySelector('[data-sel="L:complete"]'));
 check('Category exclusions visible in snapshot footer',document.getElementById('sc-foot').textContent.includes('Excluded: '+categoryCount('custom')+' Custom / '+categoryCount('sold_off_market')+' Sold Off Market'));
 check('Complete popups display every final',rows.filter(x=>x.phase==='complete').every(x=>{const h=popupHTML(x.r);return ['plumbing: Passed','hvac: Passed','electrical: Passed','grading: Passed','structural: Passed'].every(t=>h.includes(t))&&!h.includes('Completion: ~');}));
 const finals=['PLUMBING FINAL','AC FINAL','ELECT FINAL','GRADING FINAL','Struct Final'].map(type=>({type,raw:'Approved',result:'Passed',date:'2026-09-01'}));
 check('Struct passed, grading missing is MEP Finals',inspToPhase({inspections:finals.filter(r=>r.type!=='GRADING FINAL')})==='mep_finals');
 check('Four finals passed, Struct missing is MEP Finals',inspToPhase({inspections:finals.filter(r=>r.type!=='Struct Final')})==='mep_finals');
 // Temporarily tag a real supply home; restore state without persisting it.
 const sample=comingOnline(12).homes.find(r=>UW(r.id)>1)||comingOnline(12).homes[0]||DATA.find(r=>r.permits?.length)||DATA[0];
 if(sample){const saved=[...pt(sample.id).tags],before=comingOnline(12).count,wasSupply=comingOnline(12).homes.includes(sample),phase=homePhase(sample.id);
  try{for(const category of ['custom','sold_off_market']){
    pt(sample.id).tags=[...saved,category];renderLegend();refresh();buildOverview();buildTimeline();renderSupplyCard();
    const excluded=comingOnline(12).count;
    check(category+' excludes inventory, preserves phase, filters alone',!inPipeline(sample)&&homePhase(sample.id)===phase&&excluded===before-(wasSupply?UW(sample.id):0)&&matchSel(pt(sample.id).tags,'G:'+category,sample.id)&&!matchSel(pt(sample.id).tags,'G:uc',sample.id)&&!matchSel(pt(sample.id).tags,'L:permit',sample.id)&&categoryCount(category)>=UW(sample.id)&&popupHTML(sample).includes('excluded from inventory'));
    for(const ty of Object.keys(TY2K)){comboCount(ty,'foundation');ucTypeCount(ty);}
    ucCount();ucNCCount();listedCount();listedTypeCount('Single Lot');listedReadyCount('Single Lot',true);readyTypeCount(false);readyFinCount(false,false);pinColor(sample.id);
  }}finally{pt(sample.id).tags=saved;renderLegend();refresh();renderSupplyCard();}
 }
 // Execute researched classifications and category controls; never persist browser edits.
 if(typeof CLIENT_CLASSIFICATIONS!=='undefined'){
  for(const [category,ids] of Object.entries(CLIENT_CLASSIFICATIONS)){
   check('Client '+category+' exact IDs tagged',ids.every(id=>byId[id]&&pt(id).tags.includes(category)));
   if(category==='needs_clarification')continue;
   check('Client '+category+' excluded from all pipeline buckets',ids.every(id=>!inPipeline(byId[id])&&!comingOnline(12).homes.some(r=>r.id===id)&&!matchSel(pt(id).tags,'G:uc',id)));
   const control=document.querySelector('#legend > [data-grp="'+category+'"] [data-sel="G:'+category+'"]');
   control.click();
   check('Client '+category+' actual checkbox filters pins',layer.getLayers().length===ids.length&&layer.getLayers().every(m=>ids.includes(m._rec.id)));
   document.querySelector('#legend > [data-grp="'+category+'"] [data-sel="G:'+category+'"]').click();
  }
  for(const key of [...document.querySelectorAll('[data-category-product]')].map(b=>b.dataset.categoryProduct)){
   document.querySelector('[data-category-product="'+key+'"]').click();
   const expected=DATA.filter(r=>matchSel(pt(r.id).tags,key,r.id)).map(r=>r.id);
   check('Category product filter '+key,layer.getLayers().length===expected.length&&layer.getLayers().every(m=>expected.includes(m._rec.id)));
   document.querySelector('[data-category-product="'+key+'"]').click();
  }
  const id=CLIENT_CLASSIFICATIONS.custom?.[0];
  if(id){const tags=[...pt(id).tags];pt(id).tags=tags.filter(t=>t!=='custom');renderLegend();check('Stale shared tags restored without phase mutation',pt(id).tags.includes('custom')&&homePhase(id)===rows.find(x=>x.r.id===id).phase);}
 }
 // Exercise the timeline display helpers on real records (no data writes).
 check('Real popup and ETA rendering',rows.every(x=>typeof popupHTML(x.r)==='string'&&typeof etaText(x.r)==='string'));
 return results;
}
