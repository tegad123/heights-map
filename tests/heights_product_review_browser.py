"""Heights-only product/panel/phase validation; GET-only browser."""
import argparse
import collections
import functools
import http.server
import json
from pathlib import Path
import subprocess
import threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
PAGES=['index']
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass


def run(args):
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    shared=json.loads(Path(args.shared).read_text()) if args.shared else {'points':{}}
    output={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        for name in PAGES:
            ctx=browser.new_context(viewport={'width':1440,'height':1000})
            def route(req):
                if req.request.method!='GET':req.abort();return
                if 'script.google' in req.request.url:
                    req.fulfill(json=shared if name=='index' else {'points':{}});return
                if args.ref and req.request.url.split('?')[0].endswith('.html') and '127.0.0.1' in req.request.url:
                    req.fulfill(body=subprocess.check_output(['git','show',args.ref+':'+name+'.html'],cwd=ROOT),content_type='text/html');return
                req.continue_()
            ctx.route('**/*',route)
            ctx.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
            p=ctx.new_page();errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m: print('BROWSER',m.text[:180],flush=True) if 'remote load failed' in m.text else None)
            url=(args.live.rstrip('/') if args.live else f'http://127.0.0.1:{server.server_port}')+'/'+name+'.html'
            response=p.goto(url,wait_until='networkidle')
            p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
            if name=='index':
                assert p.evaluate('state.fieldEdits||{}')==shared.get('fieldEdits',{}), 'shared edits mismatch'
                p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
            result=p.evaluate('''()=>{
                renderLegend();
                const rows=DATA.map(r=>({id:r.id,address:r.a,product:prodKeyR(r)||'Unknown',weight:UW(r.id),phase:homePhase(r.id),category:inventoryCategory(r.id),twins:r._twin?[r._twin.id]:[],classified:!!r.product_classification}));
                const panel=[...document.querySelectorAll('[data-grp="uc"] .subg-h[data-col]')].map(el=>({key:el.dataset.col,label:el.querySelector('.sn').textContent,count:Number(el.querySelector('.ct2').textContent)}));
                const expected={};for(const [ty] of TYPES)expected['uc:'+ty]=ucTypeCount(ty);
                const finished=finishedRows();
                return {rows,products:rows.reduce((n,r)=>{n[r.product]=(n[r.product]||0)+r.weight;return n;},{}),
                    homes:rows.reduce((n,r)=>n+r.weight,0),uc:ucCount(),ucUnknown:ucNCCount(),panel,panelExpected:expected,
                    deeds:deedCount(),sold:typeof SOLD_DATA==='undefined'?null:SOLD_DATA.length,
                    custom:categoryCount('custom'),sold_off_market:categoryCount('sold_off_market'),
                    columns:phaseBreakdown(),finished,finishedCounts:[...document.querySelectorAll('[data-grp="finished"] .subg-h>.ct2')].map(e=>Number(e.textContent)),
                    finishedHeader:Number(document.querySelector('[data-grp="finished"] .grp-h>.ct2')?.textContent||0),
                    merrill:marketEvidence(byId['act_715-merrill']),
                    allston:DATA.filter(r=>(r.permits||[]).some(pm=>pm.proj==='26018730')).map(r=>({id:r.id,phase:homePhase(r.id)})),
                    fieldEdits:state.fieldEdits};}''')
            assert result['merrill']['status']=='active' and any(h['mls']=='50361472' for h in result['merrill']['history'])
            assert len(result['allston'])==1 and result['allston'][0]['phase']=='exterior'
            result['checks']=p.evaluate((ROOT/'tests/timeline_cases.js').read_text(),{'heights':name=='index','fixtures':json.loads((ROOT/'fixtures.json').read_text()) if name=='index' else None})
            assert all(c['pass'] for c in result['checks']),[c for c in result['checks'] if not c['pass']]
            for row in result['panel']:
                if row['key'] in result['panelExpected']:assert row['count']==result['panelExpected'][row['key']],row
            assert sum(result['panelExpected'].values())+result['ucUnknown']==result['uc']
            assert sum(result['finishedCounts'])==result['finishedHeader']
            assert p.evaluate("""()=>{const rows=finishedRows();return [...document.querySelectorAll('[data-grp="finished"] .leafrow[data-sel]')].every(el=>{const [,status,product]=el.dataset.sel.split(':');return Number(el.querySelector('.ct2').textContent)===rows.filter(r=>r.status===status&&r.product===product).length;})&&rows.every(r=>r.product===(typeKeyOf(r.pin)||'Unknown'));}""")
            if name=='index':
                assert (result['deeds'],result['sold'],result['custom'],result['sold_off_market'])==(139,791,19,1),{k:result[k] for k in ('deeds','sold','custom','sold_off_market')}
            if args.live:
                import re
                actual=p.request.get(url+'?product-check=20260910').body()
                assert re.findall(rb'<script\b[^>]*>(.*?)</script>',actual,re.S)==re.findall(rb'<script\b[^>]*>(.*?)</script>',(ROOT/(name+'.html')).read_bytes(),re.S),name
                if name=='index':
                    ids=['pmt_310-e-28th-st-77008','pmt_742-allston-st-77007']
                    for rid in ids:
                        p.evaluate('(id)=>{openPin(id);}',rid)
                        p.wait_for_function('(id)=>document.querySelector(".leaflet-popup-content .card")?.dataset.pid===id',arg=rid)
                        text=p.locator('.leaflet-popup-content').inner_text()
                        record=next(r for r in result['rows'] if r['id']==rid)
                        print('LIVE SPOT',json.dumps(record),text[:700],flush=True)
                        p.screenshot(path=str(Path(args.output).with_name('live-product-'+rid+'.png')))
                        p.evaluate('()=>{map.closePopup();}')
            result['errors']=errors;assert not errors
            output[name]=result
            print(name,json.dumps({k:result[k] for k in ('products','homes','uc','ucUnknown','deeds','sold','finishedHeader')}),flush=True)
            ctx.close()
        browser.close()
    server.shutdown()
    Path(args.output).write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--shared');ap.add_argument('--ref');ap.add_argument('--live');run(ap.parse_args())
