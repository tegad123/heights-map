() => {
  const results=[];
  const check=(name,actual,expected)=>{results.push({name,actual,expected,pass:JSON.stringify(actual)===JSON.stringify(expected)});};
  const row=(type,raw='Approved',date='2026-08-01',permit_type='Building Pmt')=>({type,raw,date,permit_type,result:raw==='Approved'||raw==='Partial Approval'?'Passed':'Failed'});
  const phase=rows=>inspToPhase({inspections:rows});
  const cases=[['SAWPOLE FINAL','sitework'],['WATER SERVICE','sitework'],['P1 FINAL','sitework'],['2nd EC','sitework'],['STORM SEWER','sitework'],['Precon','sitework'],['GROUND IN','foundation'],['FORM','foundation'],['FRM','foundation'],['MAKEUP FOUNDATION','foundation'],['MAKEUP FDN','foundation'],['FDN-WOOD/INSUL','framing'],['WINDSTORM','dried_in'],['Nail Pattern','exterior'],['FIRE WALL','exterior'],['1035-Frame','finishing'],['ROUGH IN','finishing'],['INSULATION','finishing'],['BRICK TIE',null],['BRICK TIES',null],['TCI',null],['COVER',null],['Electrical Visit',null]];
  for(const [type,expected] of cases){check(type,phase([row(type)]),expected);check(type+' failed',phase([row(type,'Disapproved')]),null);}
  check('Partial FDN',phase([row('1031-FDN PM','Partial Approval')]),'foundation');
  check('Full FDN',phase([row('1031-FDN PM')]),'framing');
  const legacy=row('1031-FDN PM');delete legacy.raw;check('Legacy FDN no invented full approval',phase([legacy]),'foundation');
  for(const type of ['STRUCT FINAL','Structural Final','STRUCTURAL FINAL'])check(type,phase([row(type)]),'complete');
  const ladder=[row('SAWPOLE FINAL'),row('GROUND IN'),row('1031-FDN PM'),row('WINDSTORM'),row('Nail Pattern'),row('ROUGH IN'),row('Struct Final')];
  let rank=0,monotonic=true;const accepted=[];
  for(const it of ladder){accepted.push(it);const next=PHASE_RANK[phase(accepted)];monotonic=monotonic&&next>=rank;rank=next;}
  check('Monotonic stage ladder',monotonic,true);
  check('Late site work cannot erase old shell evidence',phase([row('WINDSTORM','Approved','2020-01-01'),row('Site Final','Approved','2026-08-01')]),'dried_in');
  check('Max stage is independent of row order',phase(ladder.slice().reverse()),'complete');
  check('Failure does not block another trade',phase([row('1035-Frame'),row('PLUMBING FINAL','Disapproved')]),'finishing');
  const id='__calibration__',proj='__calibration__',r={id,kind:'permit',a:'1 Calibration St',permits:[{proj}]};
  const before=INSPECTIONS[proj];byId[id]=r;state.points[id]={tags:['finishing'],notes:''};
  const set=rows=>INSPECTIONS[proj]={inspections:rows};
  try {
    set([row('INSULATION','Approved','2026-08-17'),row('WINDSTORM','Approved','2026-06-01')]);
    check('Insulation anchor priority',inspectionEta(r).anchor,'INSULATION');check('Five calendar months',inspectionEta(r).target,'2027-01-17');
    set([row('WINDSTORM','Approved','2026-06-01'),row('GROUND IN','Approved','2026-04-01')]);check('Windstorm anchor priority',inspectionEta(r).anchor,'WINDSTORM');check('Windstorm 6.5 months',inspectionEta(r).target,'2026-12-16');
    set([row('GROUND IN','Approved','2026-04-01')]);check('Ground-in eight months',inspectionEta(r).target,'2026-12-01');
    set([row('INSULATION','Approved','2025-01-01')]);check('Overdue text',etaText(r),'overdue vs typical pace');check('Overdue no false ready-now',monthsLeft(id),null);
    set([]);check('No anchor default',monthsLeft(id),2);
    set([row('INSULATION','Approved','2026-08-31')]);check('Month-end anchor',inspectionEta(r).target,'2027-01-31');
    const completed=[row('Struct Final','Approved','2026-07-07'),row('INSULATION','Approved','2026-07-07'),row('1031-FDN PM','Approved','2026-07-07'),row('GROUND IN','Approved','2026-01-01')];
    set(completed);check('Complete no ETA',monthsLeft(id),null);check('Completed date annotation',inspAnnotations(r,INSPECTIONS[proj]).last,'Completed 2026-07-07');
    check('Insulation restamp hidden',inspectionDisplayDate(INSPECTIONS[proj],completed[1]),'');check('Ground-in date retained',inspectionDisplayDate(INSPECTIONS[proj],completed[3]),'2026-01-01');check('Display sort trusts struct final',inspSorted(INSPECTIONS[proj])[0].type,'Struct Final');
    set([row('1035-Frame')]);check('Frame imminent',inspAnnotations(r,INSPECTIONS[proj]).notes.includes('insulation imminent'),true);
    set(['Plumbing Pmt','Electrical Pmt','Mechanical Pmt'].map(t=>row('ROUGH IN','Approved','2026-08-01',t)));check('Three trade roughs imminent',inspAnnotations(r,INSPECTIONS[proj]).notes.includes('insulation imminent'),true);
    INSPECTIONS[proj].inspections.pop();check('Two roughs insufficient',inspAnnotations(r,INSPECTIONS[proj]).notes.includes('insulation imminent'),false);
    set([row('1035-Frame'),row('INSULATION')]);check('Insulation ends imminent',inspAnnotations(r,INSPECTIONS[proj]).notes.includes('insulation imminent'),false);
    const oldTags=['framing','exterior','sitework'];state.points[id].tags=oldTags;stripUnevidencedStage(r);check('No-evidence strip',state.points[id].tags,['permit']);
    state.points[id].tags=['complete','listed'];check('Complete excluded from UC selector',matchSel(state.points[id].tags,'G:uc',id),false);check('Complete filter',matchSel(state.points[id].tags,'L:complete',id),true);
    for(const ph of ['sitework','exterior']){state.points[id].tags=[ph];check(ph+' UC selector',matchSel(state.points[id].tags,'G:uc',id),true);check(ph+' promoted permit',isPromotedPermit(r),true);}
  } finally {delete byId[id];delete state.points[id];if(before)INSPECTIONS[proj]=before;else delete INSPECTIONS[proj];}
  return results;
}
