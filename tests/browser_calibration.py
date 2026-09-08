"""Exercise real market HTML, feeds, promotions, popups and counts in Chromium.
Run with the repository venv. Read-only: all shared-edit requests are intercepted.
"""
import argparse, json, pathlib, threading, http.server, functools, sys, datetime
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--baseline',action='store_true');ap.add_argument('--all-markets',action='store_true');ap.add_argument('--url');ap.add_argument('--mutant',choices=['completion','eta','exterior']);args=ap.parse_args()
    handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
    fixtures=json.loads((ROOT/'fixtures.json').read_text()); results={}; errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1000})
        def route(req):
            url=req.request.url
            if 'script.google.com' in url or 'script.googleusercontent.com' in url:
                req.fulfill(json={'points':{}});return
            if req.request.method!='GET':req.abort();return
            if args.baseline and '127.0.0.1' in url:
                name=url.split('/')[-1].split('?')[0] or 'index.html'; path=pathlib.Path('/tmp/heights-round2')/(('baseline-' if name.endswith('.html') else 'before-')+name)
                if path.exists():req.fulfill(body=path.read_bytes(),content_type='text/html' if name.endswith('.html') else 'application/json');return
            req.continue_()
        context.route('**/*',route)
        context.add_init_script("""{const RealDate=Date;const fixed=new RealDate('2026-09-08T12:00:00-05:00').getTime();window.Date=class extends RealDate{constructor(...args){super(...(args.length?args:[fixed]));}static now(){return fixed;}};}""")
        pages=sorted(ROOT.glob('*.html')) if args.all_markets else [ROOT/'index.html']
        for file in pages:
            page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            cdp=context.new_cdp_session(page);cdp.send('Runtime.enable');cdp.on('Runtime.exceptionThrown',lambda event:print('EXCEPTION',json.dumps(event),flush=True))
            page.goto((args.url.rstrip('/')+'/' if args.url else f'http://127.0.0.1:{server.server_port}/')+file.name,wait_until='networkidle',timeout=60000)
            page.wait_for_function('typeof INSP_LOADED!=="undefined" && INSP_LOADED',timeout=45000)
            if args.mutant:
                code={'completion':"const original=inspToPhase; inspToPhase=ins=>{const p=original(ins);return p==='complete'?'finishing':p;};",
                      'eta':"inspectionEta=r=>({anchor:'bucket default',target:null,months:null,complete:false,overdue:false});",
                      'exterior':"const original=inspPhase; inspPhase=(type,row)=>original(type,row)==='exterior'?'dried_in':original(type,row);"}[args.mutant]
                page.evaluate(code)
            result=page.evaluate('''fixtures=>{
              applyInspectionPromotions();applyReconcile(state.points);renderLegend();buildOverview();buildTimeline();askContext();
              const checks=fixtures.properties.map(f=>{const r=byId[f.rendered_id||f.id];if(!r)return {...f,actual:'MISSING',pass:false};
                const actual=homePhase(r.id),eta=typeof inspectionEta==='function'?inspectionEta(r):null;
                const html=popupHTML(r),expected=f.new_expected;
                let pass=f.forbidden?!f.forbidden.includes(actual):actual===expected;
                if(f.permit&&INSPECTIONS[f.permit]){const individual=inspToPhase(INSPECTIONS[f.permit]);pass=pass&&(f.forbidden?!f.forbidden.includes(individual):individual===expected);}
                if(f.eta)pass=pass&&!!eta&&eta.anchor===f.eta.anchor&&eta.target===f.eta.target&&(!('months' in f.eta)||monthsLeft(r.id)===f.eta.months);
                if(expected==='complete')pass=pass&&html.includes('COMPLETE')&&!html.includes('months to completion')&&!BUILD_PHASES.some(x=>pt(r.id).tags.includes(x));
                if(f.eta&&expected!=='complete')pass=pass&&html.includes('to completion')&&eta.anchor!=='bucket default';
                return {...f,actual,eta,months:monthsLeft(r.id),pass};});
              const counts={};for(const r of DATA){const ph=homePhase(r.id)||'no stage';counts[ph]=(counts[ph]||0)+1;}
              const candidates=DATA.filter(r=>BUILD_PHASES.some(x=>pt(r.id).tags.includes(x))).sort((a,b)=>String(a.id).localeCompare(String(b.id)));
              const sample=[];let seed=20260908;const pool=candidates.slice();while(pool.length&&sample.length<10){seed=(seed*1664525+1013904223)>>>0;const r=pool.splice(seed%pool.length,1)[0];sample.push({id:r.id,address:r.a,phase:homePhase(r.id),months:monthsLeft(r.id),eta:typeof inspectionEta==='function'?inspectionEta(r):null});}
              return {checks,counts,sample,uc:ucCount(),deed:deedCount(),phaseBreakdown:phaseBreakdown(),legend:document.getElementById('legend').innerText};
            }''',fixtures)
            if file.name=='index.html':
                page.evaluate("openPin('2131437296')");page.wait_for_timeout(500)
                page.screenshot(path=str(pathlib.Path(args.output).with_suffix('.png')))
            results[file.name]=result
            print(file.name,'fixtures',sum(x['pass'] for x in result['checks']),'/',len(result['checks']),'counts',result['counts'],flush=True)
            page.close()
        browser.close()
    server.shutdown();results['errors']=errors;pathlib.Path(args.output).write_text(json.dumps(results,indent=2)+'\n');print('page errors:',errors,flush=True)
    if not args.baseline and (errors or not all(x['pass'] for x in results['index.html']['checks'])):sys.exit(1)
if __name__=='__main__':main()
