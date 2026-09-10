"""Heights-only boundary cleanup: source integrity and three browser snapshots."""
import sys,json,re,csv,threading,http.server,functools,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from permit_pull import extract_data
from heights_product_residual import objects
ROOT=Path(__file__).resolve().parents[1];W=ROOT/'pulls/i10_correction_20260910'
before=(W/'before.html').read_text();after=(ROOT/'index.html').read_text();ledger=list(csv.DictReader((W/'dropped_i10_2026-09-10.csv').open()));removed={r['ID'] for r in ledger};assert len(removed)==28
old=objects(before);new=objects(after);assert len(old)==605 and len(new)==578
assert set(old)-set(new)=={r['ID'] for r in ledger if r['SOURCE']=='let DATA'}
assert all(old[k][2]==v[2] for k,v in new.items())
def sold(s):return json.JSONDecoder().raw_decode(s.split('const SOLD_DATA=',1)[1])[0]
assert sold(after)==[r for r in sold(before) if r['id'] not in removed]
assert len(sold(after))==790
ring=json.loads(re.search(r'const ZONE_RING=(\[.*?\]);',after)[1]);assert ring==json.load(open(ROOT/'heights_boundary.geojson'))['features'][0]['geometry']['coordinates'][0]
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start()
shared=json.load(open(W/'shared.json'));results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 for run in range(4):
  ctx=browser.new_context();p=ctx.new_page()
  def route(r):
   if r.request.method!='GET':r.abort()
   elif 'script.google' in r.request.url:r.fulfill(json=shared)
   elif run==0 and r.request.url.split('?')[0].endswith('/index.html'):r.fulfill(body=before,content_type='text/html')
   else:r.continue_()
  p.route('**/*',route);p.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
  p.goto(f'http://127.0.0.1:{server.server_port}/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
  checks=p.evaluate((ROOT/'tests/timeline_cases.js').read_text(),{'heights':True,'fixtures':json.load(open(ROOT/'fixtures.json'))});assert all(c['pass'] for c in checks),[c for c in checks if not c['pass']]
  result=p.evaluate('''()=>{renderLegend();renderSupplyCard();return {rows:DATA.map(r=>({id:r.id,phase:homePhase(r.id),twins:r._twin?[r._twin.id]:[],weight:UW(r.id),permits:(r.permits||[]).map(p=>p.proj)})),homes:DATA.reduce((s,r)=>s+UW(r.id),0),permitRecords:DATA.filter(r=>r.kind==='permit').length,permitProjects:new Set(DATA.flatMap(r=>(r.permits||[]).map(p=>p.proj))).size,uc:ucCount(),deeds:deedCount(),soldArchive:SOLD_DATA.length,soldView:soldFiltered().length,custom:categoryCount('custom'),soldOff:categoryCount('sold_off_market'),phases:phaseBreakdown(),supply:supplyCurve().map(r=>({months:r.months,count:r.count})),supplyText:document.getElementById('sc-foot').textContent,finished:finishedRows().reduce((n,r)=>{n[r.status]=(n[r.status]||0)+1;return n;},{}),finishedTotal:Number(document.querySelector('[data-grp="finished"] .grp-h>.ct2').textContent),merrill:marketEvidence(byId['act_715-merrill']),allston:DATA.find(r=>(r.permits||[]).some(p=>p.proj==='26018730'))?.id,reviewUnknown:!prodKeyR(byId['pmt_745-w-17th-st-77008']),reviewVisible:popupHTML(byId['pmt_745-w-17th-st-77008']).includes('$11,614'),outside:markers.filter(m=>!inZonePoly(m.getLatLng().lng,m.getLatLng().lat)).length};}''')
  assert sum(result['finished'].values())==result['finishedTotal'];assert result['merrill']['status']=='active' and any(r['mls']=='50361472' for r in result['merrill']['history']);assert result['allston'];assert result['reviewUnknown'] and result['reviewVisible'];assert result['outside']==0
  result['checks']=checks;results.append(result);ctx.close()
 browser.close()
old,new=results[0],results[1];assert results[1]==results[2]==results[3]
def phases(j):return {i:r['phase'] for r in j['rows'] for i in [r['id']]+r['twins']}
a,b=phases(old),phases(new);assert all(a[i]==v for i,v in b.items());assert set(a)-set(b)==removed-{r['id'] for r in sold(before)}
assert old['homes']-new['homes']==27 and old['deeds']-new['deeds']==1 and old['soldArchive']-new['soldArchive']==1
assert (old['custom'],old['soldOff'])==(new['custom'],new['soldOff'])
(W/'validation.json').write_text(json.dumps({'before':old,'after':new},indent=2))
for name,r in [('BEFORE',old),('AFTER',new)]:print(name,json.dumps({k:v for k,v in r.items() if k not in ['rows','checks','merrill']}))
print('PASS 3 identical Heights checks; surviving phases unchanged; 28 removals ledgered; 578 surviving DATA objects byte-identical; monotonicity',new['checks'][0]['detail'])
