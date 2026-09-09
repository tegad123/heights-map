"""Invoke market ingest, identity/history checks, and real eight-market cards."""
import argparse
import functools
import hashlib
import http.server
import json
import pathlib
import re
import subprocess
import sys
import threading
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from market_address import address_key
from market_linkage import Matcher,resolve
from deed_ingest import span
PAGES=['index','montrose','riveroaks','springbranch','springvalley','timbergrove','westu','gardenoaksoakforest']


def unit_checks():
    for a,b in [('845-A West 23rd Street','845 W 23rd St A'),('1119 East 7th 1/2 Street','1119 E 7th 1/2 St'),('1208 E 26th Street Unit#B','1208 E 26th St B'),('715 MERRILL STREET','715 Merrill St')]:assert address_key(a)==address_key(b),(a,b)
    assert address_key('1208 E 26th St A')!=address_key('1208 E 26th St B')
    assert address_key('1119 E 7th St')!=address_key('1119 E 7th 1/2 St')
    r={'id':'test','a':'1 Test St','lat':29.8,'lng':-95.4,'mls':'123'}
    matcher=Matcher([r],{'raw':[r]})
    assert matcher.match({'mls':'123','address':'1 Test Street','lat':29.8,'lng':-95.4})['method']=='mls'
    assert matcher.match({'mls':'456','address':'1 Test','lat':29.8,'lng':-95.4})['method']=='coordinate'
    assert matcher.match({'mls':'456','address':'2 Test St','lat':29.8,'lng':-95.4})['issue']=='COORDINATE_IDENTITY_CONFLICT'
    matcher=Matcher([r,dict(r,id='other',a='3 Test St')],{'raw':[r]})
    assert matcher.match({'mls':'456','address':'2 Test St','lat':29.8,'lng':-95.4})['issue']=='AMBIGUOUS_COORDINATE'
    rr=[dict(status='terminated',mls='1',dom=174),dict(status='active',mls='2',dom=8),dict(status='pending',mls='3',dom=9),dict(status='sold',mls='4',dom=10,close_date='2026-09-01'),dict(status='sold',mls='5',dom=11,close_date='2026-09-02')]
    assert resolve(rr)['current']['mls']=='5'
    print('PASS normalization, unit/fraction separation, MLS/address/proximity conflicts, status/date precedence')


def run(live=None):
    unit_checks()
    paths=[ROOT/'heights_market_status.data.json',ROOT/'docs/linkage-repair-2026-09-09.json',ROOT/'docs/linkage-review-2026-09-09.json',ROOT/'pulls/dropped_market_status_2026-09-09.csv',*[ROOT/(p+'.html') for p in PAGES]]
    before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    command=[sys.executable,'-B','market_status_ingest.py','--runtime','docs/linkage-runtime-baseline-2026-09-09.json','--apply']
    result=json.loads(subprocess.check_output(command,cwd=ROOT))
    assert result['changed_files']==[],result['changed_files']
    assert result['input_rows']==284 and result['new_classification_matches']==165
    assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    for page in PAGES:
        old=subprocess.check_output(['git','show','2bb69f5:'+page+'.html'],cwd=ROOT).decode()
        current=(ROOT/(page+'.html')).read_text()
        for name in ['DATA','RECONCILE']:
            a,z,_=span(old,name);b,y,_=span(current,name);assert old[a:z]==current[b:y],(page,name)
        # Every original inline script must be byte-identical, covering ALL phase/timeline functions.
        assert [s for s in re.findall(r'<script\b[^>]*>(.*?)</script>',old,re.S) if s.strip()]==[s for s in re.findall(r'<script\b[^>]*>(.*?)</script>',current,re.S) if s.strip()],page
    print('PASS --apply: zero changes; 284 rows; 165/165 new lot classifications; all file hashes identical')
    print('PASS all eight DATA/RECONCILE regions and inline construction/timeline scripts byte-identical to 2bb69f5')
    baseline=json.loads((ROOT/'docs/linkage-runtime-baseline-2026-09-09.json').read_text())['runtime']
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    outputs={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1100})
        def route(req):
            if req.request.method!='GET':req.abort();return
            if 'script.google' in req.request.url:req.fulfill(json={'points':{}});return
            req.continue_()
        ctx.route('**/*',route)
        ctx.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
        base=live.rstrip('/') if live else f'http://127.0.0.1:{server.server_port}'
        for name in PAGES:
            page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(base+'/'+name+'.html?linkage=20260909',wait_until='networkidle');page.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
            if live:
                body=page.request.get(base+'/'+name+'.html?verify=linkage').text()
                assert re.findall(r'<script\b[^>]*>(.*?)</script>',body,re.S)==re.findall(r'<script\b[^>]*>(.*?)</script>',(ROOT/(name+'.html')).read_text(),re.S)
                assert 'market_status.js' in body
            current=page.evaluate('''()=>({deeds:deedCount(),sold:typeof SOLD_DATA==='undefined'?null:SOLD_DATA.length,forecast:comingOnline(12).count,snapshot:marketSnapshot(),columns:phaseBreakdown(),categories:{custom:categoryCount('custom'),sold_off_market:categoryCount('sold_off_market')},rows:DATA.map(r=>({id:r.id,phase:homePhase(r.id),eta:inspectionEta(r),weight:UW(r.id)})),complete:marketRows().filter(r=>r.phase==='complete').reduce((o,r)=>(o[r.status]=(o[r.status]||0)+1,o),{}),marketCounts:marketRows().reduce((o,r)=>(o[r.status]=(o[r.status]||0)+1,o),{})})''')
            assert page.locator('[data-market-axis]').count()==1
            assert page.locator('[data-grp="mkt"]').count()==0
            # Invoke every popup and every filter; compare each filter with its evidence rows.
            assert page.evaluate('''()=>DATA.every(r=>popupHTML(r).includes('market-facts'))''')
            assert page.evaluate('''()=>Object.keys(MARKET_LABELS).every(s=>DATA.every(p=>matchSel(pt(p.id).tags,'MS:'+s+':all',p.id)===marketRows().some(r=>r.pin===p.id&&r.status===s)))''')
            if name=='index':
                expected=[{k:r[k] for k in ['id','phase','eta','weight']} for r in baseline['rows']]
                assert current['rows']==expected,'Phase/ETA/weight changed'
                assert current['forecast']==131 and current['snapshot']==dict(construction=131,terminated=3,available=128)
                assert current['categories']==dict(custom=19,sold_off_market=1)
                assert current['deeds']==139 and current['sold']==767
                assert current['columns']==baseline['columns']
                assert current['complete']==dict(no_record=24,pending=5,sold=4,terminated=3,active=13)
                assert page.locator('#sc-big').inner_text()=='128'
                spots=[('act_715-merrill','active',['88557637','8 days','50361472','174 DOM','COMPLETE']),('act_1520-w-21st-st-unit-b','terminated',['Terminated / Expired','COMPLETE']),('act_902-e-25','active',['Active','COMPLETE']),('pmt_931-merrill-st-77009','no_record',['No Market Record','COMPLETE'])]
                for identifier,status,texts in spots:
                    assert page.evaluate('(id)=>marketEvidence(byId[id]).status',identifier)==status
                    page.evaluate('(id)=>openPin(id)',identifier)
                    page.wait_for_function('(id)=>document.querySelector(".leaflet-popup-content .card")?.dataset.pid===id',arg=identifier)
                    content=page.locator('.leaflet-popup-content').inner_text();assert all(t in content for t in texts),content
                    print('SPOT',identifier,status,json.dumps(texts))
                    page.locator('.leaflet-popup-content').screenshot(path='/tmp/linkage-'+('live-' if live else 'local-')+identifier+'.png')
                    page.evaluate('()=>{map.closePopup();}')
                # Real filter button interaction shows the Complete-and-active Merrill pin.
                page.locator('[data-market-axis] [data-market-filter="MS:active:Single Lot"]').click()
                assert page.locator('[data-market-axis] [data-market-filter="MS:active:Single Lot"]').get_attribute('aria-pressed')=='true'
                assert page.evaluate("matchSel(pt('act_715-merrill').tags,'MS:active:Single Lot','act_715-merrill')")
            else:
                assert page.locator('[data-market-axis]').inner_text().count('No market-status export supplied')==1
                assert set(current['marketCounts'])=={'no_record'}
            assert errors==[],errors
            outputs[name]={k:v for k,v in current.items() if k!='rows'}
            print('MARKET',name,json.dumps(outputs[name],sort_keys=True))
            page.close()
        if live:
            for filename in ['market_status.js','heights_market_status.data.json']:
                assert ctx.request.get(base+'/'+filename+'?verify=linkage').body()==(ROOT/filename).read_bytes()
            print('PASS live market scripts and snapshot byte-identical')
        browser.close()
    server.shutdown()
    return outputs


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--three',action='store_true');ap.add_argument('--live');args=ap.parse_args()
    results=[]
    for i in range(3 if args.three else 1):
        data=json.dumps(run(args.live),sort_keys=True);results.append(data)
        print('RUN',i+1,'SHA256',hashlib.sha256(data.encode()).hexdigest(),flush=True)
    assert len(set(results))==1
    print('PASS all runs identical')
