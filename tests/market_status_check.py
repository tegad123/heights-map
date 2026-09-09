"""Exercise market ingest idempotency and real sold/property cards; never send writes."""
import argparse
import functools
import hashlib
import http.server
import json
import pathlib
import subprocess
import sys
import threading
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(live=None):
    paths = [ROOT/'index.html', ROOT/'heights_market_status.data.json',
             *sorted((ROOT/'docs').glob('market-status-*')),
             ROOT/'pulls/dropped_market_status_2026-09-09.csv']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    command = [sys.executable, '-B', 'market_status_ingest.py', '--runtime',
               'docs/market-status-baseline-2026-09-09.json', '--apply']
    ingest = json.loads(subprocess.check_output(command, cwd=ROOT))
    assert ingest['changed_files'] == [], ingest['changed_files']
    assert all(s['added'] == s['updated'] == 0 for s in ingest['files'])
    assert ingest['accepted'] + ingest['excluded'] == ingest['rows'] == 119
    assert sum(s['classification_matches'] for s in ingest['files']) == 119
    assert before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    print('PASS: invoked --apply; zero changes; 119/119 classifications; all artifact SHA256 hashes unchanged')
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={'width': 1440, 'height': 1100})
        def route(request):
            if request.request.method != 'GET': request.abort(); return
            if 'script.google' in request.request.url: request.fulfill(json={'points': {}}); return
            request.continue_()
        context.route('**/*', route)
        context.add_init_script("{const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:['2026-09-09T12:00:00-05:00']));}static now(){return new D('2026-09-09T12:00:00-05:00').getTime();}};}")
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        base = live.rstrip('/') if live else f'http://127.0.0.1:{server.server_port}'
        page.goto(base + '/index.html?market-status-audit=20260909', wait_until='networkidle')
        page.wait_for_function('INSP_LOADED && ACTIVE_VIEW.ready')
        if live:
            for name in ['index.html', 'heights_market_status.data.json']:
                assert page.request.get(base + '/' + name + '?market-verify=20260909').body() == (ROOT/name).read_bytes(), name
            print('PASS: live HTML and market snapshot byte-identical to committed local files')
        baseline = json.loads((ROOT/'docs/market-status-baseline-2026-09-09.json').read_text())['runtime']
        current = page.evaluate('''()=>({deed:deedCount(),sold:SOLD_DATA.length,supply:comingOnline(12).count,columns:phaseBreakdown(),
          rows:DATA.map(r=>({id:r.id,phase:homePhase(r.id),eta:inspectionEta(r),weight:UW(r.id)})),
          legacyCounts:{onMarketBuilding:Object.fromEntries(TYPES.map(([ty])=>[ty,comboCount(ty,'onmkt')])),needsClarification:ucNCCount(),finishedOnMarket:listedCount()},
          soldCards:SOLD_DATA.map(r=>({id:r.id,html:soldCardHTML(r,true)}))})''')
        assert (current['deed'], current['sold'], current['supply']) == (139, 767, 144)
        assert current['columns'] == baseline['columns']
        expected = [{k:r[k] for k in ['id','phase','eta','weight']} for r in baseline['rows']]
        assert current['rows'] == expected, 'Construction/ETA/weight changed'
        assert len(current.pop('soldCards')) == 767
        assert page.evaluate("['s88173016','s26903565'].every(id=>soldCardHTML(SOLD_DATA.find(s=>s.id===id),true).includes('Building size unavailable'))")
        print('LEGACY_COUNTS', json.dumps(current['legacyCounts'], sort_keys=True))
        print('PASS: 376 property phase/ETA/weight tuples unchanged; deeds 139; sold 767; supply 144; all 767 sold cards invoked')
        spots = [('act_1207-tabor', None, ['Sold record: 2026-08-31', '949,000']),
                 ('act_902-e-25', 'complete', ['Active in HAR export', 'COMPLETE']),
                 ('act_826-ralfallen', 'complete', ['Sold record: 2026-08-26', '1,655,000', 'COMPLETE']),
                 ('pmt_1623-blount-st-77008', 'complete', ['Not in this active export', 'COMPLETE'])]
        for identifier, phase, texts in spots:
            if identifier.startswith('pmt_1623'):
                identifier = page.evaluate('DATA.find(r=>r.a.startsWith("1623 Blount")).id')
            assert page.evaluate('(id)=>homePhase(id)', identifier) == phase
            page.evaluate('(id)=>openPin(id)', identifier)
            page.wait_for_function('(id)=>document.querySelector(".leaflet-popup-content .card")?.dataset.pid===id', arg=identifier)
            content = page.locator('.leaflet-popup-content').inner_text()
            assert all(t in content for t in texts), content
            print('SPOT', identifier, 'phase', phase, 'evidence', texts)
            page.screenshot(path='/tmp/market-status-'+('live-' if live else 'local-')+identifier+'.png')
            page.evaluate('()=>{map.closePopup();}')
        assert errors == [], errors
        browser.close()
    server.shutdown()
    print('PASS: page errors []; Phase 4 remains deferred; no construction or supply mutation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live')
    parser.add_argument('--three', action='store_true')
    args = parser.parse_args()
    if args.three:
        results = []
        for number in range(1, 4):
            command = [sys.executable, '-B', str(pathlib.Path(__file__).resolve())]
            if args.live: command += ['--live', args.live]
            output = subprocess.check_output(command, cwd=ROOT)
            pathlib.Path(f'/tmp/market-check-{number}.log').write_bytes(output)
            results.append(output)
            print(f'RUN {number}: market checks PASS; SHA256 {hashlib.sha256(output).hexdigest()}', flush=True)
        assert results[0] == results[1] == results[2]
        print('PASS: all three market check outputs byte-identical')
    else:
        run(args.live)
