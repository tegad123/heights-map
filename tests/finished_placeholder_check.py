"""Read-only Heights browser regression: real members vs inferred twins."""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
shared=json.load(open('/tmp/product_shared.json'))
oldjs=subprocess.check_output(['git','show','7a640d1:market_status.js'],cwd=ROOT,text=True)
results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for before in [True,False]:
  p=b.new_page()
  def route(r):
   if r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=shared)
   elif r.request.url.split('?')[0].endswith('/index.html'):r.fulfill(body=(ROOT/'index.html').read_text(),content_type='text/html')
   elif r.request.url.split('?')[0].endswith('/market_status.js'):r.fulfill(body=oldjs if before else (ROOT/'market_status.js').read_text(),content_type='application/javascript')
   else:r.continue_()
  p.route('**/*',route);p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
  j=p.evaluate('''()=>{renderLegend();const f=finishedRows();return {rows:f,counts:f.reduce((n,r)=>{n[r.status]=(n[r.status]||0)+1;return n;},{}),total:f.length,header:Number(document.querySelector('[data-grp="finished"] .grp-h>.ct2').textContent),projects:DATA.map(r=>({id:r.id,phase:homePhase(r.id),weight:UW(r.id),evidence:marketMembers(r).map(m=>marketEvidence(m)),noRecord:matchSel(pt(r.id).tags,'F:no_record',r.id),finished:matchSel(pt(r.id).tags,'G:finished',r.id)})),fixture:popupHTML(byId['act_741-w-21st-street-unit-a']),note:popupHTML(byId['pmt_112-e-27th-st-a-77008'])};}''')
  assert j['total']==j['header'];results.append(j);p.close()
 b.close()
a,z=results
synthetic=[r for r in a['rows'] if r.get('member') is None];assert len(synthetic)==6
assert [r for r in z['rows'] if r['pin']!='pmt_112-e-27th-st-a-77008']==[r for r in a['rows'] if r.get('member') is not None and r['pin']!='pmt_112-e-27th-st-a-77008']
assert a['counts']['no_record']-z['counts']['no_record']==6
assert all(a['counts'][k]==z['counts'][k] for k in a['counts'] if k!='no_record')
assert [{k:r[k] for k in ['id','phase','weight','evidence']} for r in a['projects'] if r['id']!='pmt_112-e-27th-st-a-77008']==[{k:r[k] for k in ['id','phase','weight','evidence']} for r in z['projects'] if r['id']!='pmt_112-e-27th-st-a-77008']
for r in synthetic:assert not next(p for p in z['projects'] if p['id']==r['pin'])['noRecord']
assert '7364673' in z['fixture'] and 'HAR status: Active' in z['fixture'] and '<strong>No Market Record</strong>' not in z['fixture']
assert 'Identity review requested' not in z['note'] and '34333707' in z['note']
for term in ['118 E 23rd','1432 Alexander','112 E 27th Street','409 Walton St A','1403 W 21st St C','1403 W 21st St D']:
 assert any(term in r.get('address','') and r['status']=='no_record' for r in z['rows']),term
Path('/tmp/finished-placeholder-validation.json').write_text(json.dumps({'before':a,'after':z},indent=2))
print('BEFORE',a['counts'],'total',a['total']);print('AFTER',z['counts'],'total',z['total'])
print('PASS exactly six synthetic rows excluded; six real mixed/development members unchanged; all phases, weights and market evidence unchanged; 741 Active popup and filter agree; 112 identity review visible')
