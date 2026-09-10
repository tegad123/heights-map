"""Read-only browser audit for the combined HAR ingest and permit backfill."""
import argparse,functools,http.server,json,pathlib,threading,subprocess
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run(args):
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
 threading.Thread(target=server.serve_forever,daemon=True).start(); errors=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(); ctx=browser.new_context(viewport={'width':1440,'height':1000})
  def route(req):
   if req.request.method!='GET':req.abort()
   elif 'script.google' in req.request.url and not args.shared:req.fulfill(json={'points':{}})
   elif args.ref and '127.0.0.1' in req.request.url:
    name=req.request.url.split('/')[-1].split('?')[0]
    if name.endswith(('.html','.js','.json')):
     body=subprocess.check_output(['git','show',args.ref+':'+name],cwd=ROOT)
     req.fulfill(body=body,content_type='text/html' if name.endswith('.html') else 'application/javascript' if name.endswith('.js') else 'application/json')
    else:req.continue_()
   else:req.continue_()
  ctx.route('**/*',route);ctx.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
  p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
  p.goto((args.live.rstrip('/') if args.live else f'http://127.0.0.1:{server.server_port}')+'/index.html',wait_until='networkidle');p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
  if args.shared:p.wait_for_timeout(12000)
  result=p.evaluate('''()=>{
   applyInspectionPromotions();renderLegend();refresh();renderSupplyCard();
   const leaf=[...document.querySelectorAll('#legend [data-sel]')].map(e=>e.dataset.sel);
   const other=[...document.querySelectorAll('[data-grp="other"] .leafrow')].map(el=>{
    const key=el.dataset.sel, members=DATA.filter(r=>mById[r.id]&&matchSel(pt(r.id).tags,key,r.id));
    return {key,label:el.querySelector('.nm').textContent,displayed:Number(el.querySelector('.ct2').textContent),homes:members.reduce((n,r)=>n+UW(r.id),0),
      members:members.map(r=>({id:r.id,address:r.a,weight:UW(r.id),phase:homePhase(r.id),statuses:marketMembers(r).map(m=>marketEvidence(m).status),
      coveredElsewhere:leaf.some(k=>k!==key&&!k.startsWith('F:')&&matchSel(pt(r.id).tags,k,r.id)),finished:homePhase(r.id)==='complete'}))};});
   return {rows:DATA.map(r=>({id:r.id,address:r.a,phase:homePhase(r.id),weight:UW(r.id),market:marketMembers(r).map(m=>marketEvidence(m).status),color:pinColor(r.id)})),
    finished:finishedRows(),snapshot:marketSnapshot(),columns:phaseBreakdown(),uc:ucCount(),deeds:deedCount(),sold:SOLD_DATA.length,
    custom:categoryCount('custom'),sold_off_market:categoryCount('sold_off_market'),other,otherHeader:Number(document.querySelector('[data-grp="other"] .grp-h>.ct2').textContent),
    finishedHeader:Number(document.querySelector('[data-grp="finished"] .grp-h>.ct2').textContent),finishedCounts:[...document.querySelectorAll('[data-grp="finished"] .subg-h>.ct2')].map(e=>Number(e.textContent)),
    swatches:[...document.querySelectorAll('[data-grp="finished"] .subg-h .sw')].map(e=>e.style.backgroundColor),
    merrill:marketEvidence(byId['act_715-merrill']),allston:DATA.filter(r=>(r.permits||[]).some(pm=>pm.proj==='26018730')).map(r=>({id:r.id,phase:homePhase(r.id),note:r.note})),
    colors:{tags:Object.fromEntries(Object.entries(state.tags).map(([k,v])=>[k,v.color])),groups:GROUP_C,sold:SOLD_WIN_C},
    checks:[]};}''')
  if args.checks:
   result['checks']=p.evaluate((ROOT/'tests/timeline_cases.js').read_text(),{'heights':True,'fixtures':json.loads((ROOT/'fixtures.json').read_text())})
   assert all(c['pass'] for c in result['checks']),[c for c in result['checks'] if not c['pass']]
   assert result['merrill']['status']=='active' and any(r['mls']=='50361472' for r in result['merrill']['history'])
   assert len(result['allston'])==1 and result['allston'][0]['phase']=='exterior'
   assert (result['deeds'],result['custom'],result['sold_off_market'],result['sold'])==(139,19,1,791)
   assert sum(result['finishedCounts'])==result['finishedHeader']
   colors=p.evaluate('FINISHED_COLORS')
   assert len(result['swatches'])==5
   for status,color in colors.items():
    computed=p.evaluate('(c)=>{const e=document.createElement("i");e.style.backgroundColor=c;return e.style.backgroundColor}',color)
    assert computed in result['swatches'],status
   assert all(r['color'].lower() in {c.lower() for c in colors.values()} for r in result['rows'] if r['phase']=='complete' and r['id'] in {x['pin'] for x in result['finished']})
   keys=[row['key'] for row in result['other']]
   assert 'L:off_market_single' not in keys and 'L:off_market_split' not in keys and 'L:pending' not in keys
   assert result['otherHeader']==sum(r['weight'] for r in result['rows'] if r['id'] in {m['id'] for row in result['other'] for m in row['members']})
  if args.live:
   for name in ('market_status.js','heights_market_status.data.json','inspections.json'):
    assert p.request.get(args.live.rstrip('/')+'/'+name+'?backfill=20260910').body()==(ROOT/name).read_bytes(),name
   arrivals=json.loads((ROOT/'pulls/market_backfill_20260910/arrivals.json').read_text())
   ids=['act_715-merrill',result['allston'][0]['id']]
   ids += [next(r['id'] for r in arrivals if r['runtime_phase']=='complete' and (r['status']=='no_record')==unknown) for unknown in (False,True)]
   for identifier in ids:
    p.evaluate('(id)=>{openPin(id);}',identifier)
    p.wait_for_function('(id)=>document.querySelector(".leaflet-popup-content .card")?.dataset.pid===id',arg=identifier)
    p.wait_for_timeout(300)
    text=p.locator('.leaflet-popup-content').inner_text();print('LIVE SPOT',identifier,text[:1900],flush=True)
    p.screenshot(path='/tmp/backfill-'+identifier+'.png');p.evaluate('()=>{map.closePopup();}')
  browser.close()
 server.shutdown();result['errors']=errors;assert not errors
 pathlib.Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('snapshot','columns','uc','deeds','sold','custom','sold_off_market','otherHeader','finishedHeader','finishedCounts','allston','errors')},indent=2),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--checks',action='store_true');ap.add_argument('--live');ap.add_argument('--shared',action='store_true');ap.add_argument('--ref');run(ap.parse_args())
