"""One Heights-only browser regression for evidence-based permit promotion."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];W=R/'pulls/unfiltered_20260910'
shared=json.loads((W/'shared.json').read_text())
collect='''()=>({rows:DATA.map(r=>({id:r.id,address:r.a,phase:homePhase(r.id),weight:UW(r.id),product:prodKeyR(r),eta:inspectionEta(r),tags:pt(r.id).tags,inspections:inspForPin(r)?.inspections||[]})),uc:ucCount(),phases:phaseBreakdown(),snapshot:marketSnapshot(),finished:finishedRows().reduce((o,r)=>(o[r.status]=(o[r.status]||0)+1,o),{}),map:Number(document.getElementById('sc-big').textContent),overview:Number(document.querySelector('.ovx-big').textContent),homes:DATA.reduce((n,r)=>n+UW(r.id),0),pins:DATA.length,sold:SOLD_DATA.length,deeds:deedCount(),custom:categoryCount('custom'),soldOff:categoryCount('sold_off_market'),merrill:marketEvidence(byId['act_715-merrill']),unitA:marketEvidence(byId['pmt_112-e-27th-st-a-77008'])})'''
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for before in [True,False]:
  p=b.new_page()
  def route(r):
   name=r.request.url.split('?')[0].split('/')[-1]
   if r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=shared)
   elif name in ['index.html','heights_market_status.data.json','market_status.js']:
    path=Path('/tmp/foundation-before.html') if before and name=='index.html' else R/name
    r.fulfill(body=path.read_text(),content_type='text/html' if name.endswith('.html') else 'application/json' if name.endswith('.json') else 'application/javascript')
   else:r.continue_()
  p.route('**/*',route)
  p.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
  p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED&&MARKET_VIEW.ready');p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();}')
  if not before:
   checks=p.evaluate((R/'tests/timeline_cases.js').read_text(),{'heights':True,'fixtures':json.loads((R/'fixtures.json').read_text())})
   assert all(c['pass'] for c in checks),[c for c in checks if not c['pass']]
   proof=p.evaluate('''()=>{const row=(type,raw='Approved')=>({type,raw,result:raw==='Disapproved'?'Failed':'Passed',date:'2026-09-01'});const out={empty:inspToPhase({inspections:[]}),failed:inspToPhase({inspections:[row('1031-FDN AM','Disapproved')]}),site:inspToPhase({inspections:['Precon','Prefill','Sawpole Final','EC'].map(x=>row(x))}),partial:inspToPhase({inspections:[row('1031-FDN AM','Partial Approval')]}),approved:inspToPhase({inspections:[row('1031-FDN AM')]}),fixtures:{}};for(const prefix of ['940 Nadine','902 Jewett','1040 Louise','914 W 16th','214 Sylvester','1813 W 14th','305 W 17th','1922 Bonner','707 Teetshorn','2311 Roy','1019 E 7th']){const r=DATA.find(r=>r.a.toLowerCase().startsWith(prefix.toLowerCase()));out.fixtures[prefix]={phase:homePhase(r.id),eta:inspectionEta(r).target,visible:!!mById[r.id],permitLayer:matchSel(pt(r.id).tags,'L:permit',r.id),label:popupHTML(r).includes('Permitted, no passed construction inspections'),review:pt(r.id).tags.includes('needs_clarification')};}return out;}''')
   assert proof['empty'] is None and proof['failed'] is None and proof['site'] is None
   assert proof['partial']=='foundation' and proof['approved']=='framing'
   for addr,f in proof['fixtures'].items():
    if addr in ['1040 Louise','214 Sylvester']:assert f['phase']=='foundation' and f['eta']
    else:assert f['phase'] is None and f['eta'] is None and f['label'] and f['visible'] and f['permitLayer'],(addr,f)
   assert proof['fixtures']['1019 E 7th']['review']
   p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();}')
  results.append(p.evaluate(collect));p.close()
 b.close()
a,z=results
changes=[{'address':x['address'],'id':x['id'],'weight':x['weight'],'before':x['phase'],'after':y['phase']} for x,y in zip(a['rows'],z['rows']) if x['phase']!=y['phase']]
assert all(c['before']=='foundation' and c['after'] is None for c in changes),changes
for k in ['homes','pins','sold','deeds','custom','soldOff','snapshot']:assert a[k]==z[k],(k,a[k],z[k])
assert z['map']==z['overview']==z['snapshot']['available']
assert z['merrill']['status']=='active' and any(h['mls']=='50361472' for h in z['merrill']['history'])
assert z['unitA']['status']=='active' and z['unitA']['current']['mls']=='34333707'
assert all(None not in r['tags'] for r in z['rows'])
# No DATA or other embedded datasets were edited.
s=Path('/tmp/foundation-before.html').read_text();t=(R/'index.html').read_text()
def data(s):
 a=s.index('let DATA = ')+len('let DATA = ');_,b=json.JSONDecoder().raw_decode(s,a);return s[a:b]
assert data(s)==data(t)
out={'before':a,'after':z,'changes':changes,'proof':proof,'checks':checks};(W/'foundation-fix-validation.json').write_text(json.dumps(out,indent=2))
print('HEIGHTS PASS ONE CHECK')
for label,v in [('BEFORE',a),('AFTER',z)]:print(label,json.dumps({k:v[k] for k in ['uc','phases','snapshot','finished','homes','pins','sold','deeds']}))
print('CHANGES',json.dumps(changes));print('PROOF',json.dumps(proof));print('MONOTONICITY',checks[0]['detail'])
