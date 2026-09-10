"""One Heights check: display-only missed-target label and actual Layers filter."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];W=R/'pulls/unfiltered_20260910';results=[]
with sync_playwright() as pw:
 b=pw.chromium.launch()
 for before in [True,False]:
  p=b.new_page()
  def route(r):
   name=r.request.url.split('?')[0].split('/')[-1]
   if r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=json.loads((W/'shared.json').read_text()))
   elif name in ['index.html','heights_market_status.data.json','market_status.js','inventory_classifications.js']:
    path=Path('/tmp/overdue-label-before.html') if before and name=='index.html' else R/name
    r.fulfill(body=path.read_text(),content_type='text/html' if name.endswith('.html') else 'application/json' if name.endswith('.json') else 'application/javascript')
   else:r.continue_()
  p.route('**/*',route);p.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-10T12:00:00-05:00']));}static now(){return new D('2026-09-10T12:00:00-05:00').getTime();}};}")
  p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED&&MARKET_VIEW.ready');p.evaluate('()=>{renderLegend();renderSupplyCard();buildOverview();buildTimeline();}')
  results.append(p.evaluate('''()=>({rows:DATA.map(r=>({id:r.id,phase:homePhase(r.id),eta:inspectionEta(r),tags:pt(r.id).tags,product:prodKeyR(r)})),snapshot:marketSnapshot(),uc:ucCount(),foundation:phaseBreakdown().foundation,custom:categoryCount('custom'),excludedNeeds:categoryCount('needs_clarification'),finished:finishedRows(),map:Number(document.getElementById('sc-big').textContent),overview:Number(document.querySelector('.ovx-big').textContent)})'''))
  if not before:
   proof=p.evaluate('''()=>{const rows=DATA.filter(r=>missedCompletionTarget(r)),ids=rows.map(r=>r.id).sort();const el=document.querySelector('.leafrow[data-sel="T:missed_completion"]');const count=Number(el.querySelector('.ct2').textContent);el.click();const filtered=layer.getLayers().map(m=>m._rec.id).sort();document.querySelector('.leafrow[data-sel="T:missed_completion"]').click();
    document.querySelectorAll('#tlBody [data-more]').forEach(el=>el.click());
    const popupOK=DATA.every(r=>{const d=document.createElement('div');d.innerHTML=popupHTML(r);const label=!!d.querySelector('.missed-target'),expected=!!missedCompletionTarget(r);return label===expected&&[...d.querySelectorAll('.phasetime')].filter(x=>x.textContent.startsWith('Completion:')).every(x=>!/overdue/i.test(x.textContent));});
    const timelineOK=rows.filter(r=>inPipeline(r)).every(r=>{const el=document.querySelector('#tlBody [data-go="'+r.id+'"]');return el&&/Overdue/.test(el.textContent)&&!/OVERDUE VS/.test(el.closest('.tlx-bucket').querySelector('.tlx-bh').textContent);});
    const cases=[{target:'2026-10-01',anchorTarget:'2026-08-15'},{target:'2026-10-01',anchorTarget:'2026-09-01'},{target:'2026-10-01',anchorTarget:'2026-08-15',clientCompletion:{target:'2026-10-01'}},{target:'2026-08-15',anchorTarget:'2026-07-01',complete:true},{target:null}].map(e=>missedCompletionTarget({},e));
    return {count,ids,filtered,popupOK,timelineOK,cases,homes:rows.reduce((n,r)=>n+UW(r.id),0),phases:rows.reduce((o,r)=>(o[homePhase(r.id)]=(o[homePhase(r.id)]||0)+UW(r.id),o),{}),excluded:rows.filter(r=>inventoryCategory(r.id)).reduce((n,r)=>n+UW(r.id),0),details:rows.map(r=>({address:r.a,id:r.id,homes:UW(r.id),phase:homePhase(r.id),category:inventoryCategory(r.id),target:inspectionEta(r).target,...missedCompletionTarget(r)}))};}''')
   (W/'missed-target-proof.json').write_text(json.dumps(proof,indent=2))
   print('FILTER',proof['count'],proof['homes'],'missing',set(proof['ids'])-set(proof['filtered']),'extra',set(proof['filtered'])-set(proof['ids']))
   assert proof['ids']==proof['filtered'] and proof['count']==proof['homes']
   assert proof['popupOK'] and proof['timelineOK'];assert proof['cases'][0]['months']==1 and proof['cases'][1:]==[None]*4
  p.close()
 b.close()
assert results[0]==results[1], 'Label changed ETA, phase, tags, product, counts or supply'
s=Path('/tmp/overdue-label-before.html').read_text();t=(R/'index.html').read_text()
for start,end in [('function phaseTimeline(', 'function rollingCompletionTarget('),('function rollingCompletionTarget(', 'function inspectionEta('),('function inspectionEta(', 'function missedCompletionTarget(')]:
 if end not in s:end='function timelineDuration('
 def block(v):return v[v.index(start):v.index(end,v.index(start))].strip()
 # New helper follows inspectionEta; compare just that function's source.
 if start=='function inspectionEta(':
  assert s[s.index(start):s.index('function timelineDuration(')].strip()==t[t.index(start):t.index('// Display-only comparison')].strip()
 else:assert block(s)==block(t)
def data(s):
 a=s.index('let DATA = ')+len('let DATA = ');_,b=json.JSONDecoder().raw_decode(s,a);return s[a:b]
assert data(s)==data(t)
(W/'missed-target-validation.json').write_text(json.dumps({'proof':proof,'after':results[1]},indent=2))
print('HEIGHTS PASS ONE CHECK: all ETA results, phase tags, products, counts and supply byte-identical')
print(json.dumps({k:v for k,v in proof.items() if k not in ['ids','filtered','details']}));print('SUPPLY',results[1]['snapshot'])
