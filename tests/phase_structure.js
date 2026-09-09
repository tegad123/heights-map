/* Execute the actual inline classifier from every market, against feeds and mutations. */
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const markets=['index','montrose','riveroaks','springbranch','springvalley','timbergrove','westu','gardenoaksoakforest'];
const expected={'26022264':'framing','26009059':'exterior','25118994':'exterior','26012829':'interior','26011885':'interior','25071971':'complete','25059398':'complete','25092767':'complete','22030746':'interior'};
const row=(type,raw='Partial Approval',permit_type='Building Pmt',date='2026-09-01')=>({type,raw,permit_type,date,result:/Approved|Partial Approval/.test(raw)?'Passed':'Failed'});
const finalRows=[row('PLUMBING FINAL'),row('AC FINAL'),row('ELECT FINAL'),row('FINAL','Partial Approval','GRADING , FILL'),row('Struct Final')];
let total=0;
for(const market of markets){
 const html=fs.readFileSync(market+'.html','utf8');
 const core=html.slice(html.indexOf('// Inspection evidence:'),html.indexOf('function inspectionEta('));
 const derivation=html.slice(html.indexOf('function inspToPhase(ins){'),html.indexOf('// Project-level rollup:'));
 const context=vm.createContext({});vm.runInContext(core+derivation+';this.api={inspToPhase,inspPhase,inspectionPassed,finalKind,finalChecklist,completionFinal,structuralFinal,PHASE_RANK};',context);
 const a=context.api,feed=JSON.parse(fs.readFileSync(market==='index'?'inspections.json':'inspections_'+market+'.json'));
 let checks=0;const check=(actual,want,label)=>{assert.strictEqual(actual,want,market+': '+label);checks++;};
 for(const type of ['WINDSTORM','Nail Pattern','FIRE WALL'])for(const status of ['Partial Approval','Approved'])check(a.inspToPhase({inspections:[row(type,status)]}),'exterior',type+' '+status);
 for(const type of ['ROUGH','ROUGH IN'])for(const status of ['Partial Approval','Approved'])check(a.inspToPhase({inspections:[row(type,status)]}),'mep_roughs',type+' '+status);
 for(const status of ['Partial Approval','Approved']){
  check(a.inspToPhase({inspections:[row('COVER',status,'HVAC Permit')]}),'mep_roughs','HVAC COVER');
  check(a.inspToPhase({inspections:[row('1035-Frame',status)]}),'insulation','Frame');
  check(a.inspToPhase({inspections:[row('INSULATION',status)]}),'interior','Insulation');
  check(a.inspToPhase({inspections:[row('FDN-WOOD/INSUL',status)]}),'framing','FDN-WOOD/INSUL');
 }
 check(a.inspToPhase({inspections:[row('1031-FDN PM')]}),'foundation','Partial foundation');
 check(a.inspToPhase({inspections:[row('1031-FDN PM','Approved')]}),'framing','Approved foundation');
 for(const type of ['Brick Tie','TCI','TEMP GAS FINAL','SAWPOLE FINAL','Site Final','Flood Final','2nd EC','Driveway AM','Sidewalk PM','CULVERT','STORM SEWER','WATER SERVICE','P1 FINAL','CC FINAL','ADD EL FINAL 1','ADD AC FINAL 1'])check(a.inspToPhase({inspections:[row(type)]}),'foundation','Ignored '+type);
 check(a.inspToPhase({inspections:[row('COVER','Approved','DECOR APPLANCE')]}),'foundation','Non-HVAC COVER');
 check(a.inspToPhase({inspections:[]}), 'foundation','Permit only');check(a.inspToPhase(null),null,'No permit');
 for(const type of ['1031-FDN PM','WINDSTORM','Nail Pattern','ROUGH','1035-Frame','INSULATION','Struct Final'])for(const status of ['Correction Necessary','Inspection Requested','Canceled/Revoked'])check(a.inspToPhase({inspections:[row(type,status)]}),'foundation','Failure/nonpassed '+type);
 check(a.inspToPhase({inspections:finalRows}),'complete','All five partial finals');
 check(a.inspToPhase({inspections:finalRows.filter(r=>r.type!=='FINAL')}),'mep_finals','Grading missing');
 check(a.inspToPhase({inspections:finalRows.filter(r=>r.type!=='Struct Final')}),'mep_finals','Struct missing');
 check(a.inspToPhase({inspections:[row('Struct Final')]}),'mep_finals','Struct only');
 check(a.inspToPhase({inspections:finalRows.map((r,i)=>({...r,proj:i%2?'A':'B'}))}),'mep_finals','Mixed homes cannot manufacture completion');
 check(a.finalChecklist({inspections:finalRows}).outstanding.length,0,'Checklist');check(a.structuralFinal({inspections:finalRows}).type,'Struct Final','Structural evidence');
 for(const [proj,ins] of Object.entries(feed)){
  const phase=a.inspToPhase(ins),reverse=a.inspToPhase({...ins,inspections:ins.inspections.slice().reverse()});check(phase,reverse,'Order independence '+proj);
  const accepted=[];let rank=1;
  for(const r of ins.inspections){accepted.push(r);const next=a.PHASE_RANK[a.inspToPhase({...ins,inspections:accepted})];assert(next>=rank,market+' regression '+proj);rank=next;checks++;}
  if(market==='index'&&expected[proj])check(phase,expected[proj],proj);
 }
 // Mutants must fail the same real or synthetic ground-truth assertions.
 if(market==='index'){
  const munford=feed['26012829'],harvard=feed['26022264'],wind=feed['26009059'];
  check(a.inspToPhase({...munford,inspections:munford.inspections.map(r=>/1035|^insulation$/i.test(r.type)&&r.raw==='Partial Approval'?{...r,raw:'Correction Necessary',result:'Failed'}:r)}),'mep_roughs','Strict-partial mutant caught (Munford must be interior)');
  check(a.inspToPhase({...wind,inspections:wind.inspections.map(r=>/windstorm/i.test(r.type)?{...r,raw:'Correction Necessary',result:'Failed'}:r)}),'foundation','Partial-windstorm mutant caught (629 must be exterior)');
  check(a.structuralFinal({inspections:[row('Struct Final')]})!==null,true,'Struct-only-complete mutant would incorrectly pass old completion shortcut');
  for(const [proj,want] of Object.entries(expected))console.log('FIXTURE',proj,a.inspToPhase(feed[proj]),'PASS');
 }
 total+=checks;console.log(market,checks,'checks PASS');
}
console.log('TOTAL',total,'checks PASS; no feed-order stage regressions');
