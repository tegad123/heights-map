"""Heights-only check that map and Overview use the same supply exclusions."""
import json,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];shared=json.load(open('/tmp/product_shared.json'));live='--live' in sys.argv
with sync_playwright() as pw:
 b=pw.chromium.launch();p=b.new_page()
 def route(r):
  if r.request.method!='GET':r.abort()
  elif 'script.google' in r.request.url:r.fulfill(json=shared)
  elif not live and r.request.url.split('?')[0].endswith('/index.html'):r.fulfill(body=(ROOT/'index.html').read_text(),content_type='text/html')
  elif not live and r.request.url.split('?')[0].endswith('/market_status.js'):r.fulfill(body=(ROOT/'market_status.js').read_text(),content_type='application/javascript')
  else:r.continue_()
 p.route('**/*',route);p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html?supply-views=20260910',wait_until='networkidle');p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready');p.evaluate('()=>{buildOverview();renderSupplyCard();renderLegend();}')
 j=p.evaluate('''()=>({map:Number(document.getElementById('sc-big').textContent),overview:Number(document.querySelector('.ovx-big').textContent),mapNote:document.getElementById('sc-foot').textContent,overviewNote:document.querySelector('.ovx-snapshot-note').textContent,snapshot:marketSnapshot(),stats:[...document.querySelectorAll('.ovx-stat')].map(e=>({label:e.querySelector('.k').textContent,value:Number(e.querySelector('.v').textContent)})),panelUC:Number(document.querySelector('[data-grp="uc"] .grp-h>.ct2').textContent),mapPhases:[...document.querySelectorAll('#sc-phases .n')].map(e=>Number(e.textContent)),overviewPhases:[...document.querySelectorAll('.ovx-pipe .dot')].map(e=>Number(e.textContent)),chart:[...document.querySelectorAll('.ovx-chart text')].filter(e=>!e.textContent.endsWith('mo')).map(e=>Number(e.textContent)),expectedCurve:[3,6,9,12,18,24].map(m=>marketSnapshot(m).available),finished:finishedRows().reduce((n,r)=>{n[r.status]=(n[r.status]||0)+1;return n;},{}),listed:listedCount(),deeds:deedCount(),queued:DATA.filter(r=>!inventoryCategory(r.id)&&r.kind==='permit'&&!isPromotedPermit(r)).length})''')
 active=p.evaluate('''()=>({counts:activeMarketCounts(),finished:Number(document.querySelector('[data-active-market="finished"] .v').textContent),construction:Number(document.querySelector('[data-active-market="construction"] .v').textContent),finishedPanel:finishedRows().filter(r=>r.status==='active').length,constructionMembers:marketRows().filter(r=>r.member!=null&&r.status==='active'&&r.phase&&r.phase!=='complete').length})''')
 assert active['finished']==active['counts']['finished']==active['finishedPanel']
 assert active['construction']==active['counts']['construction']==active['constructionMembers']
 j['activeMarket']=active
 assert j['map']==j['overview']==j['snapshot']['available'];assert j['overviewNote'] in j['mapNote'];assert j['stats'][0]['value']==j['panelUC'];assert j['mapPhases']==j['overviewPhases'];assert j['chart']==j['expectedCurve']
 print(('LIVE ' if live else '')+'PASS',json.dumps(j));Path('/tmp/supply-views-validation.json').write_text(json.dumps(j,indent=2));b.close()
