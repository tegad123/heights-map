"""Execute active layer filters and evidence popups; block every external write."""
import argparse,functools,http.server,json,pathlib,threading,re
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(live=None):
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    with sync_playwright() as pw:
        browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1440,'height':1100})
        def route(request):
            if request.request.method!='GET':request.abort();return
            if 'script.google' in request.request.url:request.fulfill(json={'points':{}});return
            request.continue_()
        context.route('**/*',route);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        response=page.goto((live.rstrip('/') if live else f'http://127.0.0.1:{server.server_port}')+'/index.html?active-audit=20260908',wait_until='networkidle')
        page.wait_for_function('INSP_LOADED && typeof ACTIVE_VIEW!=="undefined" && ACTIVE_VIEW.ready')
        if live:
            assert re.findall(rb'<script\b[^>]*>(.*?)</script>',response.body(),re.S)==re.findall(rb'<script\b[^>]*>(.*?)</script>',(ROOT/'index.html').read_bytes(),re.S)
            for filename in ['active_listings.js','heights_active.data.json']:
                assert page.request.get(live.rstrip('/')+'/'+filename+'?verify=20260908').body()==(ROOT/filename).read_bytes()
            print('PASS live HTML scripts, active JS and active snapshot match local files')
        before=page.evaluate('JSON.stringify({tags:state.points,data:DATA,supply:comingOnline(12).count,sold:SOLD_DATA.length,deed:deedCount()})')
        counts=page.evaluate('({active:ACTIVE_VIEW.listings.length,sold:SOLD_DATA.length,deeds:deedCount(),supply:comingOnline(12).count})')
        assert counts['active']==40 and counts['sold']==764 and counts['deeds']==139
        print('Counts',json.dumps(counts))
        for product,count in [('Single Lot',22),('Split Lot',18)]:
            control=page.locator('[data-active-product="'+product+'"]');control.click()
            result=page.evaluate('''prod=>({count:ACTIVE_VIEW.listings.filter(a=>a.product===prod).length,pins:layer.getLayers().map(m=>m._rec.id),expected:[...ACTIVE_VIEW.byPin].filter(([id,rs])=>rs.some(r=>r.product===prod)).map(([id])=>id)})''',product)
            assert result['count']==count and set(result['pins'])==set(result['expected'])
            print('PASS actual layer click',product,'listings',count,'pins',len(result['pins']))
            control.click()
        spots=[('act_1207-tabor',['Sold record: 2026-08-31','949,000','Prior recorded status: Pending / Under Contract']),('act_902-e-25',['Active in HAR export','DOM:','Original list price:','COMPLETE']),('pmt_1623-blount-st-77008',['Not in this active export','COMPLETE']),('act_1322-lawrence-street',['1322 Lawrence','1324 Lawrence','Sold record: 2026-08-28','Active in HAR export']),('act_1520-w-21st-st-unit-b',['Prior recorded status: Off Market','Active in HAR export'])]
        for identifier,expected in spots:
            if identifier=='pmt_1623-blount-st-77008':identifier=page.evaluate('DATA.find(r=>r.a.startsWith("1623 Blount")).id')
            page.evaluate('(id)=>openPin(id)',identifier)
            page.wait_for_function('(id)=>document.querySelector(".leaflet-popup-content .card")?.dataset.pid===id',arg=identifier)
            popup=page.locator('.leaflet-popup-content');text=popup.inner_text()
            assert all(x in text for x in expected),(identifier,text)
            print('POPUP',identifier,'\n'+text[:1800])
            if identifier=='act_1207-tabor':assert 'ready / on market' not in text
            page.wait_for_timeout(350)
            page.screenshot(path='/tmp/active-'+('live-' if live else 'local-')+identifier+'.png')
            page.evaluate('()=>{map.closePopup();}')
        # Exercise every source key, the all-selector branch, original selector delegation and idempotent load.
        assert page.evaluate('ACTIVE_VIEW.listings.every(r=>activeAddressKey(r.address)===r.address_key)')
        assert page.evaluate('matchSel([],"AL:all",DATA.find(r=>ACTIVE_VIEW.byPin.has(r.id)).id)')
        page.evaluate('matchSel([],"G:uc",DATA[0].id);renderActiveLegend();')
        page.evaluate('loadActiveListings()')
        after=page.evaluate('JSON.stringify({tags:state.points,data:DATA,supply:comingOnline(12).count,sold:SOLD_DATA.length,deed:deedCount()})')
        assert before==after,'Display changed underlying state'
        assert not errors,errors
        print('PASS normalization 40/40; reload leaves DATA/tags/supply/sold/deeds byte-identical; page errors []')
        browser.close()
    server.shutdown()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--live');args=ap.parse_args();run(args.live)
