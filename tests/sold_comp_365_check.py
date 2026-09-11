"""One Heights browser check plus real ASK invocation for 365-day comp policy."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from deed_ingest import span
R=Path(__file__).resolve().parents[1];W=R/'pulls/unfiltered_20260910';results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for before in [True,False]:
  p=b.new_page()
  def route(r):
   name=r.request.url.split('?')[0].split('/')[-1]
   if r.request.method=='POST' and name=='ask':r.continue_()
   elif r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=json.loads((W/'shared.json').read_text()))
   elif name in ['index.html','heights_market_status.data.json','market_status.js','inventory_classifications.js']:
    path=Path('/tmp/sold-comp-before.html') if before and name=='index.html' else R/name
    r.fulfill(body=path.read_text(),content_type='text/html' if name.endswith('.html') else 'application/json' if name.endswith('.json') else 'application/javascript')
   else:r.continue_()
  p.route('**/*',route);p.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-10T12:00:00-05:00']));}static now(){return new D('2026-09-10T12:00:00-05:00').getTime();}};}")
  p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED&&MARKET_VIEW.ready');p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();buildTimeline();}')
  j=p.evaluate('''()=>({raw:DATA,rows:DATA.map(r=>({id:r.id,phase:homePhase(r.id),eta:inspectionEta(r),product:prodKeyR(r),tags:pt(r.id).tags})),market:marketRows(),finished:finishedRows(),snapshot:marketSnapshot(),phases:phaseBreakdown(),uc:ucCount(),custom:categoryCount('custom'),soldOff:categoryCount('sold_off_market'),deeds:deedCount(),homes:DATA.reduce((n,r)=>n+UW(r.id),0),pins:DATA.length,sold:SOLD_DATA,soldPanel:soldFiltered().length,metrics:SOLD_METRICS})''');results.append(j)
  if not before:
   proof=p.evaluate('''()=>{activeF.add('G:sold');renderSoldAll();const pins=soldLayer.getLayers().length;const geometry=DATA.flatMap(marketMembers).filter(m=>constructionProductDisplay(m)?.source==='parcel-backed construction classification').every(m=>!marketProductDisplay(m,marketEvidence(m).current).includes('provisional'));const oldSales=marketRows().filter(r=>r.status==='sold'&&(r.current?.close_date||r.archive_current?.cd||'9999')<'2025-09-10').map(r=>{const date=r.current?.close_date||r.archive_current?.cd,price=r.current?.close_price||r.archive_current?.cp,html=popupHTML(byId[r.pin]);return {address:r.address,date,price,shownDate:html.includes(date),shownPrice:html.includes(Number(price).toLocaleString())};});return {pins,geometry,oldSales,finishedCounts:finishedRows().reduce((n,r)=>(n[r.status]=(n[r.status]||0)+1,n),{}),context:soldAskContext(),snapshot:marketSnapshot(),overview:Number(document.querySelector('.ovx-big').textContent)};}''')
   assert len(j['sold'])==j['soldPanel']==proof['pins']==136,(len(j['sold']),j['soldPanel'],proof['pins'])
   assert all(r['coh']=='nc' and '2025-09-10'<=r['cd']<='2026-09-10' for r in j['sold'])
   assert sum(r['prod']=='Unknown' for r in j['sold'])==4
   assert all(r['prod']=='Split Lot' for r in j['sold'] if r.get('lot') and r['lot']<2000)
   assert proof['geometry'] and all(r['shownDate'] and r['shownPrice'] for r in proof['oldSales']),proof['oldSales']
   assert proof['overview']==proof['snapshot']['available']==153
   (W/'sold-comp-context.txt').write_text(proof['context'])
   question='How many sold comps are currently displayed, what construction cohort and closing window do they cover, and what is their median close price? Are retired resale sales or older historical evidence included in that comp count? Answer briefly using SOLD_COMP_METRICS.'
   p.evaluate('q=>{document.getElementById("askIn").value=q;}',question)
   p.evaluate('async()=>{await askSend();}')
   answer=p.evaluate('()=>document.querySelector("#askLog").lastElementChild.textContent')
   (W/'sold-comp-ask-answer.txt').write_text(answer)
   assert '136' in answer and ('814,500' in answer or '814500' in answer),answer
   print('ASK ANSWER',answer)
  p.close()
 b.close()
a,z=results
for k in ['raw','rows','market','finished','snapshot','phases','uc','custom','soldOff','deeds','homes','pins']:assert a[k]==z[k],k
oldhtml=Path('/tmp/sold-comp-before.html').read_text();newhtml=(R/'index.html').read_text()
for name in ['DATA','RECONCILE']:
 a1,b1,_=span(oldhtml,name);a2,b2,_=span(newhtml,name);assert oldhtml[a1:b1]==newhtml[a2:b2]
archive={r['id']:r for r in span(newhtml,'SOLD_EVIDENCE')[2]};assert all(archive[r['id']]==r for r in span(oldhtml,'SOLD_DATA')[2])
(W/'sold-comp-validation.json').write_text(json.dumps({'before':a,'after':z,'proof':proof,'ask':answer},indent=2))
print('HEIGHTS PASS ONE CHECK: all tracked statuses, phases, ETAs, product types and supply unchanged')
print('RESULT',json.dumps({'sold_before':a['soldPanel'],'sold_after':z['soldPanel'],'finished':proof['finishedCounts'],'snapshot':z['snapshot'],'custom':z['custom'],'soldOff':z['soldOff'],'deeds':z['deeds'],'historicalSold':proof['oldSales']}))
