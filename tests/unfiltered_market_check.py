"""Heights-only staged market refresh regression; no mutations to the live app."""
import sys,json,re
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'pulls/unfiltered_20260910';stage=W/'stage';live='--live' in sys.argv;shared=json.load(open(W/'shared.json'))
from collections import Counter
html=(ROOT/'index.html').read_text();candidate=(stage/'index.html').read_text()
def data(s):
 a=s.index('let DATA = ')+len('let DATA = ');_,b=json.JSONDecoder().raw_decode(s,a);return s[a:b]
assert data(html)==data(candidate)
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for run in range(3):
  p=b.new_page()
  def route(r):
   name=r.request.url.split('?')[0].split('/')[-1]
   if r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=shared)
   elif not live and name in ['index.html','heights_market_status.data.json']:r.fulfill(body=(stage/name).read_text(),content_type='text/html' if name.endswith('.html') else 'application/json')
   elif not live and name=='market_status.js':r.fulfill(body=(ROOT/name).read_text(),content_type='application/javascript')
   else:r.continue_()
  p.route('**/*',route);p.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
  p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html?unfiltered-check=20260910',wait_until='networkidle');p.wait_for_function('INSP_LOADED&&MARKET_VIEW.ready');p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();}')
  checks=p.evaluate((ROOT/'tests/timeline_cases.js').read_text(),{'heights':True,'fixtures':json.load(open(ROOT/'fixtures.json'))});assert all(c['pass'] for c in checks),[c for c in checks if not c['pass']]
  p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();}')
  j=p.evaluate('''()=>({rows:DATA.map(r=>({id:r.id,phase:homePhase(r.id),weight:UW(r.id),product:prodKeyR(r),classification:r.product_classification})),market:marketRows(),finished:finishedRows(),finishedCount:finishedRows().reduce((n,r)=>{n[r.status]=(n[r.status]||0)+1;return n;},{}),finishedHeader:Number(document.querySelector('[data-grp="finished"] .grp-h>.ct2').textContent),homes:DATA.reduce((n,r)=>n+UW(r.id),0),pins:DATA.length,sold:SOLD_DATA.length,soldPanel:soldFiltered().length,deeds:deedCount(),custom:categoryCount('custom'),soldOff:categoryCount('sold_off_market'),uc:ucCount(),map:Number(document.getElementById('sc-big').textContent),overview:Number(document.querySelector('.ovx-big').textContent),merrill:marketEvidence(byId['act_715-merrill']),unitA:marketEvidence(byId['pmt_112-e-27th-st-a-77008']),active:activeMarketCounts(),allston:DATA.some(r=>(r.permits||[]).some(p=>p.proj==='26018730')),geometryCheck:DATA.flatMap(r=>marketMembers(r)).filter(m=>constructionProductDisplay(m)?.source==='parcel-backed construction classification').every(m=>!marketProductDisplay(m,marketEvidence(m).current).includes('provisional')),spots:['pmt_737-w-21st-st-b-77008','pmt_737-w-21st-st-a-77008','act_715-merrill'].map(id=>({id,status:marketEvidence(byId[id]).status,popup:popupHTML(byId[id])}))})''')
  (W/'last-check.json').write_text(json.dumps(j,indent=2))
  assert j['merrill']['status']=='active' and any(x['mls']=='50361472' for x in j['merrill']['history']);assert j['unitA']['status']=='active' and j['unitA']['current']['mls']=='34333707';assert j['allston'];assert j['geometryCheck'];assert j['map']==j['overview'];assert sum(j['finishedCount'].values())==j['finishedHeader'];assert (j['custom'],j['soldOff'],j['deeds'])==(19,1,138)
  assert [r['status'] for r in j['spots']]==['active','no_record','active'];j['checks']=checks;results.append(j);p.close()
 b.close()
assert results[0]==results[1]==results[2]
baseline=json.load(open(W/'runtime.json'))['index'];a={r['id']:r['phase'] for r in baseline['rows']};assert all(a[r['id']]==r['phase'] for r in results[0]['rows']);assert baseline['homes']==results[0]['homes'] and baseline['pins']==results[0]['pins']
(W/('live-validation.json' if live else 'preview-validation.json')).write_text(json.dumps(results[0],indent=2))
print(('LIVE ' if live else 'PREVIEW ')+'PASS THREE IDENTICAL CHECKS',json.dumps({k:v for k,v in results[0].items() if k not in ['rows','market','finished','merrill','unitA','spots','checks']}));print('MONOTONICITY',results[0]['checks'][0]['detail'])
