"""Read-only Chromium checks for all eight permit-timeline pages."""
import argparse,functools,http.server,json,pathlib,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
PAGES=['index','montrose','riveroaks','springbranch','springvalley','timbergrove','westu','gardenoaksoakforest']

def run(args):
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    results={};errors=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1000})
        def route(req):
            url=req.request.url
            if req.request.method!='GET':req.abort();return
            if 'script.google' in url:req.fulfill(json={'points':{}});return
            if args.ref and '127.0.0.1' in url and '.html' in url:
                name=url.split('/')[-1].split('?')[0]
                req.fulfill(body=subprocess.check_output(['git','show',args.ref+':'+name],cwd=ROOT),content_type='text/html');return
            req.continue_()
        ctx.route('**/*',route)
        ctx.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
        for name in PAGES:
            p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
            url=(args.live.rstrip('/') if args.live else f'http://127.0.0.1:{server.server_port}')+'/'+name+'.html'
            response=p.goto(url,wait_until='networkidle');p.wait_for_function('INSP_LOADED')
            if args.live:
                import re
                body=(ROOT/(name+'.html')).read_bytes()
                assert re.findall(rb'<script\b[^>]*>(.*?)</script>',body,re.S)==re.findall(rb'<script\b[^>]*>(.*?)</script>',response.body(),re.S)
            result=p.evaluate('''()=>{
              applyInspectionPromotions();renderLegend();buildOverview();buildTimeline();renderSupplyCard();askContext();
              return {supply:comingOnline(12).count,supplyIds:comingOnline(12).homes.map(r=>r.id),columns:phaseBreakdown(),uc:ucCount(),deed:deedCount(),sold:typeof SOLD_DATA==='undefined'?null:SOLD_DATA.length,
                rows:DATA.map(r=>({id:r.id,address:r.a,product:prodKeyR(r),phase:homePhase(r.id),weight:UW(r.id),eta:inspectionEta(r),months:monthsLeft(r.id),projects:(r.permits||[]).map(p=>p.proj)}))};
            }''')
            if args.checks:result['checks']=p.evaluate((ROOT/'tests/timeline_cases.js').read_text(),{'heights':name=='index','fixtures':json.loads((ROOT/'fixtures.json').read_text()) if name=='index' else None})
            if args.spots and name=='index':
                rough=p.evaluate("DATA.find(r=>homePhase(r.id)==='mep_roughs').permits[0].proj")
                for proj in ['26022264','26009059',rough,'26012829','26011885','25071971']:
                    identifier=p.evaluate('(proj)=>DATA.find(r=>(r.permits||[]).some(pm=>pm.proj===proj)).id',proj)
                    p.evaluate('(id)=>{openPin(id);}',identifier)
                    p.wait_for_function('(id)=>document.querySelector(".leaflet-popup-content .card")?.dataset.pid===id',arg=identifier)
                    p.wait_for_timeout(350)
                    text=p.locator('.leaflet-popup-content').inner_text();print('SPOT',proj,text[:1400],flush=True)
                    p.screenshot(path=str(pathlib.Path(args.output).with_name(('live-' if args.live else 'local-')+proj+'.png')))
                    p.evaluate('()=>{map.closePopup();}')
            results[name]=result
            print(name,json.dumps({k:result[k] for k in ['supply','columns','uc','deed','sold']}),flush=True)
            if args.checks:
                failed=[c for c in result['checks'] if not c['pass']]
                print('CHECKS',name,len(result['checks'])-len(failed),'/',len(result['checks']),'FAILURES',json.dumps(failed),flush=True)
            p.close()
        browser.close()
    server.shutdown();results['errors']=errors;pathlib.Path(args.output).write_text(json.dumps(results,indent=2)+'\n')
    print('ERRORS',errors,flush=True)
    assert not errors
    if args.checks:assert all(c['pass'] for k,r in results.items() if k!='errors' for c in r['checks'])
    return results

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--ref');ap.add_argument('--live');ap.add_argument('--checks',action='store_true');ap.add_argument('--spots',action='store_true');run(ap.parse_args())
