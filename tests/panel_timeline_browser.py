"""Eight-market capped ETA and Heights panel validation; GET-only browser."""
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
PAGES=['index','montrose','riveroaks','springbranch','springvalley','timbergrove','westu','gardenoaksoakforest']
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
                const rows=DATA.map(r=>({id:r.id,address:r.a,product:prodKeyR(r)||'Unknown',weight:UW(r.id),phase:homePhase(r.id),category:inventoryCategory(r.id),twins:r._twin?[r._twin.id]:[],classified:!!r.product_classification,eta:inspectionEta(r)}));
                const panel=[...document.querySelectorAll('[data-grp="uc"] .subg-h[data-col]')].map(el=>({key:el.dataset.col,label:el.querySelector('.sn').textContent,count:Number(el.querySelector('.ct2').textContent)}));
                const expected={};for(const [ty] of TYPES)expected['uc:'+ty]=ucTypeCount(ty);
                const finished=finishedRows();
                return {rows,products:rows.reduce((n,r)=>{n[r.product]=(n[r.product]||0)+r.weight;return n;},{}),
                    homes:rows.reduce((n,r)=>n+r.weight,0),uc:ucCount(),ucUnknown:ucNCCount(),panel,panelExpected:expected,
                    deeds:deedCount(),sold:typeof SOLD_DATA==='undefined'?null:SOLD_DATA.length,
                    custom:categoryCount('custom'),sold_off_market:categoryCount('sold_off_market'),
                    columns:phaseBreakdown(),finished,finishedCounts:[...document.querySelectorAll('[data-grp="finished"] .subg-h>.ct2')].map(e=>Number(e.textContent)),
                    finishedHeader:Number(document.querySelector('[data-grp="finished"] .grp-h>.ct2')?.textContent||0),
                    fieldEdits:state.fieldEdits,
                    panelAudit:MARKET_PAGE==='heights'?{
                      otherHeader:+document.querySelector('[data-grp="other"] .grp-h>.ct2').textContent,
                      phaseLeafTotal:[...document.querySelectorAll('[data-grp="uc"] .leafrow[data-sel]')].filter(e=>/\|(foundation|framing|exterior|mep_roughs|insulation|interior|mep_finals)$/.test(e.dataset.sel)).reduce((n,e)=>n+Number(e.querySelector('.ct2').textContent),0),
                      soldTotal:soldFiltered().length,soldIds:soldFiltered().map(r=>r.id),
                      soldPins:DATA.filter(r=>soldInventoryPin(r.id)).map(r=>r.id),
                      overlaps:['active_single|onmkt','O:pending'].map(key=>({key,rows:DATA.filter(r=>matchSel(pt(r.id).tags,key,r.id)).map(r=>({id:r.id,phase:homePhase(r.id),weight:UW(r.id)})),parent:document.querySelector('[data-sel="'+key+'"]')?.closest('.grp').dataset.grp})),
                      other:[...document.querySelectorAll('[data-grp="other"] .leafrow')].map(e=>({key:e.dataset.sel,count:+e.querySelector('.ct2').textContent})),
                      merrill:marketEvidence(byId['act_715-merrill']),
                      northwood:DATA.filter(r=>r.a.startsWith('115 Northwood')).map(r=>({id:r.id,eta:inspectionEta(r),popup:popupHTML(r)})),
                      unphased:DATA.filter(r=>otherMarketMatch(pt(r.id).tags,'O:unphased',r.id)).map(r=>({id:r.id,weight:UW(r.id),phase:homePhase(r.id),members:marketMembers(r).map(m=>marketEvidence(m)),finished:finishedRows().filter(x=>x.pin===r.id),popup:popupHTML(r)}))
                    }:null};}''')
            result['checks']=p.evaluate((ROOT/'tests/timeline_cases.js').read_text(),{'heights':name=='index','fixtures':json.loads((ROOT/'fixtures.json').read_text()) if name=='index' else None})
            assert all(c['pass'] for c in result['checks']),[c for c in result['checks'] if not c['pass']]
            for row in result['panel']:
                if row['key'] in result['panelExpected']:assert row['count']==result['panelExpected'][row['key']],row
            assert sum(result['panelExpected'].values())+result['ucUnknown']==result['uc']
            assert sum(result['finishedCounts'])==result['finishedHeader']
            assert p.evaluate("""()=>{const rows=finishedRows();return [...document.querySelectorAll('[data-grp="finished"] .leafrow[data-sel]')].every(el=>{const [,status,product]=el.dataset.sel.split(':');return Number(el.querySelector('.ct2').textContent)===rows.filter(r=>r.status===status&&r.product===product).length;})&&rows.every(r=>r.product===(typeKeyOf(r.pin)||'Unknown'));}""")
            if name=='index':
                assert (result['deeds'],result['sold'],result['custom'],result['sold_off_market'])==(139,791,19,1),{k:result[k] for k in ('deeds','sold','custom','sold_off_market')}
            if name=='index':
                audit=result['panelAudit'];assert audit['soldTotal']==790
                assert audit['phaseLeafTotal']+result['ucUnknown']==result['uc']==225
                assert audit['otherHeader']==7
                assert [sum(r['weight'] for r in o['rows']) for o in audit['overlaps']]==[14,8]
                assert all(o['parent']=='uc' and all(r['phase'] in ('framing','mep_roughs','interior','mep_finals') for r in o['rows']) for o in audit['overlaps'])
                assert result['finishedCounts']==[34,9,19,76] and result['finishedHeader']==138
                assert audit['other']==[{'key':'L:needs_clarification','count':5},{'key':'O:unverified','count':2}]
                assert not any(r['status']=='sold' for r in result['finished'])
                assert not set(audit['soldIds']) & {s['id'] for r in result['finished'] for s in r.get('historical_sales',[])}
                assert sum(r['weight'] for r in audit['unphased'])==47
                assert sum(len(r['finished'])+sum(m['status']=='sold' for m in r['members']) for r in audit['unphased'])==47
                assert all('No permit record' in r['popup'] and r['phase'] is None for r in audit['unphased'])
                assert audit['northwood'][0]['eta']['remainingDays']==42 and 'Completion: ~6 weeks' in audit['northwood'][0]['popup'] and 'Stalled:' in audit['northwood'][0]['popup']
                assert audit['merrill']['status']=='active' and any(r['mls']=='50361472' for r in audit['merrill']['history'])
                for key in ['G:finished','F:active','O:pending','active_single|onmkt','O:unverified']:
                    selection=p.evaluate('''key=>{activeF.clear();activeF.add(key);renderLegend();refresh();return {expected:DATA.filter(r=>matchSel(pt(r.id).tags,key,r.id)).map(r=>r.id).sort(),actual:layer.getLayers().map(m=>m._rec.id).sort()};}''',key)
                    assert selection['actual']==selection['expected'],(key,selection)
                p.evaluate("()=>{activeF.clear();activeF.add('G:sold');renderSoldAll();}")
                assert p.evaluate('layer.getLayers().length')==0
                assert p.evaluate('soldLayer.getLayers().length')>0
                assert p.evaluate("marketRows().filter(r=>r.status==='sold').every(r=>soldMk[r.archive_current?.id||('s'+r.current?.mls)])")
                p.evaluate("()=>{activeF.clear();renderSoldAll();}")
                p.locator('[data-grp="finished"]').scroll_into_view_if_needed()
                p.screenshot(path=str(Path(args.output).with_suffix('.png')))
                p.locator('[data-grp="uc"] [data-sel="O:pending"]').scroll_into_view_if_needed()
                p.screenshot(path=str(Path(args.output).with_name(Path(args.output).stem+'-overlap.png')))
            if args.live:
                import re
                actual=p.request.get(url+'?product-check=20260910').body()
                assert re.findall(rb'<script\b[^>]*>(.*?)</script>',actual,re.S)==re.findall(rb'<script\b[^>]*>(.*?)</script>',(ROOT/(name+'.html')).read_bytes(),re.S),name
                if name=='index':
                    ids=[audit['northwood'][0]['id'],audit['overlaps'][0]['rows'][0]['id'],next(r['pin'] for r in result['finished'] if r['status']=='active' and not r['phase'])]
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
