"""One Heights-only check: client determinations and target-month routing."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];W=R/'pulls/unfiltered_20260910'
NAMES=['1002 E 6','1013 Woodland','1040 Louise','1104 Gibbs','1109 Tabor','1110 Jerome','1113 Voight','1140 Waverly','115 Northwood','1219 Bay Oaks','1410 Herkimer','1510 Glen Oaks','1910 W 14','2005 Harvard','2008 W 14','2434 White Oak','248 W 22','2603 Julian','602 Northwood','603 E 23','618 Wendel','623 E 13','625 Oxford','708 Ralfallen','710 Le Green','711 E 12','718 E 7','721 Usener','822 Nashua']
collect='''()=>({rows:DATA.map(r=>({id:r.id,address:r.a,phase:homePhase(r.id),product:prodKeyR(r),weight:UW(r.id),eta:inspectionEta(r),category:inventoryCategory(r.id),tags:pt(r.id).tags,record:r})),uc:ucCount(),foundation:phaseBreakdown().foundation,custom:categoryCount('custom'),needs:DATA.reduce((n,r)=>n+(pt(r.id).tags.includes('needs_clarification')?UW(r.id):0),0),excludedNeeds:categoryCount('needs_clarification'),snapshot:marketSnapshot(),finished:finishedRows().reduce((o,r)=>(o[r.status]=(o[r.status]||0)+1,o),{}),map:Number(document.getElementById('sc-big').textContent),overview:Number(document.querySelector('.ovx-big').textContent),homes:DATA.reduce((n,r)=>n+UW(r.id),0),pins:DATA.length,sold:SOLD_DATA.length,deeds:deedCount()})'''
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for before in [True,False]:
  p=b.new_page()
  def route(r):
   name=r.request.url.split('?')[0].split('/')[-1]
   if r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=json.loads((W/'shared.json').read_text()))
   elif name in ['index.html','heights_market_status.data.json','market_status.js','inventory_classifications.js']:
    path=Path('/tmp/rolling-before.html') if before and name=='index.html' else Path('/tmp/rolling-before-classifications.js') if before and name=='inventory_classifications.js' else R/name
    r.fulfill(body=path.read_text(),content_type='text/html' if name.endswith('.html') else 'application/json' if name.endswith('.json') else 'application/javascript')
   else:r.continue_()
  p.route('**/*',route);p.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-10T12:00:00-05:00']));}static now(){return new D('2026-09-10T12:00:00-05:00').getTime();}};}")
  p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED&&MARKET_VIEW.ready');p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();buildTimeline();}')
  if not before:
   proof=p.evaluate('''names=>{
    document.querySelectorAll('#tlBody [data-more]').forEach(x=>x.click());
    const chosen=names.map(prefix=>{const rs=DATA.filter(r=>r.a.toLowerCase().startsWith(prefix.toLowerCase()));if(rs.length!==1)throw Error(prefix+': '+rs.length+' matches');const r=rs[0],eta=inspectionEta(r);const el=document.querySelector('#tlBody [data-go="'+r.id+'"]');return {address:r.a,id:r.id,phase:homePhase(r.id),target:eta.target,month:eta.targetMonth,remaining:eta.remainingDays,category:inventoryCategory(r.id),inCurve:comingOnline(12).homes.some(x=>x.id===r.id),bucket:el?.closest('.tlx-bucket').querySelector('.tlx-bh .t').textContent||null};});
    const noText=DATA.every(r=>!(/overdue/i.test(popupHTML(r))))&&!/overdue/i.test(document.getElementById('tlBody').textContent+document.getElementById('sc-foot').textContent);
    let phasePairs=0,timePairs=0,phaseViolations=0,timeViolations=0;const rows=DATA.map(r=>({r,p:homePhase(r.id),e:inspectionEta(r)})).filter(x=>x.e.remainingDays!=null);
    for(const a of rows)for(const b of rows){if(a.p===b.p&&!a.e.clientCompletion&&!b.e.clientCompletion&&a.e.anchorDate<b.e.anchorDate){timePairs++;if(a.e.target>b.e.target)timeViolations++;}if(prodKeyR(a.r)===prodKeyR(b.r)&&PHASE_RANK[a.p]>PHASE_RANK[b.p]){phasePairs++;if(a.e.baseDays>b.e.baseDays)phaseViolations++;}}
    return {chosen,noText,timePairs,timeViolations,phasePairs,phaseViolations,noPast:rows.every(x=>x.e.target>=new Date().toISOString().slice(0,10)),rolled:rows.filter(x=>x.e.rolled).length,rollExamples:[rollingCompletionTarget('2026-09-15',new Date('2026-10-06')),rollingCompletionTarget('2026-09-15',new Date('2026-10-27'))],nearTerm:rows.filter(x=>x.p==='mep_finals').every(x=>x.e.remainingDays<=31),jeromeVisible:matchSel(pt('pmt_1110-jerome-st-77009').tags,'L:needs_clarification','pmt_1110-jerome-st-77009'),fallback:inspToPhase({inspections:[]}),pairDates:['pmt_310-w-9th-st-77007','pmt_2013-cortlandt-st-77008'].map(id=>inspectionEta(byId[id])),merrill:marketEvidence(byId['act_715-merrill']).status};}''',NAMES)
   assert proof['noText'] and proof['noPast'] and proof['nearTerm'] and proof['jeromeVisible'] and proof['fallback'] is None,proof
   assert proof['timeViolations']==proof['phaseViolations']==0
   assert [x['target'] for x in proof['rollExamples']]==['2026-10-15','2026-11-15']
   assert all(x['remainingDays']==28 for x in proof['pairDates']);assert proof['merrill']=='active'
   for r in proof['chosen']:
    if r['category']:assert not r['inCurve'] and r['bucket'] is None,r
    else:
     assert r['inCurve'] and r['bucket'],r
     from datetime import datetime
     assert datetime.strptime(r['month'],'%Y-%m').strftime('%b %Y').upper() in r['bucket'],r
   assert len([r for r in proof['chosen'] if not r['category']])==26
  results.append(p.evaluate(collect));p.close()
 b.close()
a,z=results;old={r['id']:r for r in a['rows']};new={r['id']:r for r in z['rows']}
assert all(old[r['id']]['phase']==r['phase'] for r in z['rows'])
for id in ['act_1113-voight','act_1140-waverly']:assert old[id]['record']==new[id]['record'] and old[id]['tags']==new[id]['tags']
assert new['pmt_1104-gibbs-st-77009']['product']=='Split Lot' and new['pmt_1104-gibbs-st-77009']['phase']=='mep_finals'
assert new['act_1002-e-6-12']['eta']['target']=='2026-10-01' and new['act_1002-e-6-12']['eta']['remainingDays']==21
assert new['act_1109-tabor']['category']==new['pmt_115-northwood-st-77009']['category']=='custom'
assert new['pmt_1110-jerome-st-77009']['category']=='needs_clarification'
assert z['foundation']==a['foundation']==9 and z['map']==z['overview']==z['snapshot']['available']
for k in ['homes','pins','sold','deeds']:assert a[k]==z[k]
# Raw DATA changed only in the two authorized records; no array serialization.
def objects(s):
 start=s.index('let DATA = ')+len('let DATA = ');rows,end=json.JSONDecoder().raw_decode(s,start);return rows,s[start:end]
oldrows,oldraw=objects(Path('/tmp/rolling-before.html').read_text());newrows,newraw=objects((R/'index.html').read_text());nr={r['id']:r for r in newrows};allowed={'act_1002-e-6-12','pmt_1104-gibbs-st-77009'}
for r in oldrows:
 if r['id'] not in allowed:assert r==nr[r['id']]
 else:oldraw=oldraw.replace(json.dumps(r),json.dumps(nr[r['id']]))
assert oldraw==newraw
out={'before':a,'after':z,'proof':proof};(W/'rolling-validation.json').write_text(json.dumps(out,indent=2))
print('HEIGHTS PASS ONE CHECK')
for label,j in [('BEFORE',a),('AFTER',z)]:print(label,json.dumps({k:v for k,v in j.items() if k!='rows'}))
print('PROOF',json.dumps(proof))
