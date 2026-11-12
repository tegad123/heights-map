/* Sold comps and active listing pins for every market except Heights.
   Heights keeps its inline sold layer and active_listings.js. */
const HAR_PAGE = document.currentScript && document.currentScript.dataset.market;
const HAR_CSS = `
.sxc-row{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 8px;align-items:center}
.sxc-row .cl{font-family:var(--lab);font-size:9px;letter-spacing:.14em;color:var(--sub);text-transform:uppercase;width:66px;flex:0 0 auto}
.sxf{font-family:var(--lab);font-size:10px;letter-spacing:.08em;padding:5px 10px;border-radius:3px;border:1px solid var(--bd);background:transparent;color:var(--sub);cursor:pointer;text-transform:uppercase}
.sxf.on{background:var(--acc);border-color:var(--acc);color:#fff;font-weight:700}
.sxmo{font-family:var(--lab);font-size:10px;background:var(--sur2);border:1px solid var(--bd);color:var(--sub);border-radius:3px;padding:4px 6px;outline:none}
.sx-vol{border:1px solid var(--bd);border-radius:8px;padding:12px 14px 10px;background:var(--sur2);margin:0 0 14px}
.sx-volh{display:flex;justify-content:space-between;font-family:var(--lab);font-size:9px;letter-spacing:.14em;color:var(--sub);text-transform:uppercase;margin-bottom:10px}
.sx-volbars{display:flex;align-items:flex-end;gap:6px}
.sx-volcol{flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;cursor:pointer;min-width:0}
.sx-volcol .v{font-family:var(--lab);font-size:9px;color:var(--txt)}
.sx-volcol .b{width:100%;max-width:34px;background:var(--sub);border-radius:2px 2px 0 0}
.sx-volcol.on .b{background:var(--acc)}
.sx-volcol.on .m{color:var(--acc)}
.sx-volcol .m{font-family:var(--lab);font-size:8px;letter-spacing:.04em;color:var(--sub);white-space:nowrap}
.sx-tiles{display:flex;gap:10px;margin:10px 0 16px;flex-wrap:wrap}
.sx-tile{flex:1;min-width:128px;border:1px solid var(--bd);border-radius:8px;padding:12px 14px;background:var(--sur2)}
.sx-tile.tap{cursor:pointer}
.sx-tile.on{border-color:var(--acc);background:rgba(193,83,37,.10)}
.sx-tile .n{font-family:var(--disp);font-weight:700;font-size:28px;color:var(--txt);line-height:1}
.sx-tile .l{font-family:var(--lab);font-size:8.5px;color:var(--sub);letter-spacing:.12em;margin-top:5px}
.sx-bandh{display:flex;justify-content:space-between;font-family:var(--lab);font-size:9.5px;color:var(--sub);letter-spacing:.12em;margin:18px 0 10px;border-bottom:1px solid var(--bd);padding-bottom:6px;text-transform:uppercase}
.sx-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:10px}
.sx-card{border:1px solid var(--bd);border-left:3px solid var(--sub);border-radius:8px;background:var(--sur2);padding:11px 13px;cursor:pointer}
.sx-card .a{font-size:13px;font-weight:600;color:var(--txt)}
.sx-r1{display:flex;gap:9px;align-items:baseline;margin-top:5px;font-family:var(--lab);font-size:11px;color:var(--sub);flex-wrap:wrap}
.sx-r1 .cp{color:var(--fdn);font-size:14.5px;font-weight:600}
.sx-r2{margin-top:4px;font-family:var(--lab);font-size:9.5px;color:var(--sub);line-height:1.55}
.sx-presold{font-family:var(--lab);font-size:8.5px;letter-spacing:.1em;background:#d6336c;color:#fff;padding:2px 6px;border-radius:2px}
.sx-svl{font-family:var(--lab);font-size:10.5px;font-weight:600}
.sx-pop .a{font-size:14px}
.sx-none{font-family:var(--lab);font-size:11px;color:var(--sub);margin:14px 0}
`;
if (!document.getElementById('har-layer-css')) {
  const style = document.createElement('style');
  style.id = 'har-layer-css';
  style.textContent = HAR_CSS;
  document.head.appendChild(style);
}

let SOLD_DATA = [];
let SOLD_METRICS = {as_of: ''};
let SOLD_COMP_POLICY = {min_lot_sqft: 2200};
let ACTIVE_LISTINGS = [];
const SOLD_WINS = ['0-30', '30-60', '60-90', '90-180', '180-365', '365+'];
const SOLD_WIN_C = {'0-30': '#c92a2a', '30-60': '#e8590c', '60-90': '#f59f00', '90-180': '#a5845c', '180-365': '#8c857a', '365+': '#68645f'};
const SOLD_BANDS = ['<600K', '600-700K', '700-800K', '800-900K', '900K-1M', '1M-1.1M', '1.1M-1.2M', '1.2M-1.3M', '1.3M-1.6M', '1.6M-1.8M', '1.8M-2M', '2M-2.2M', '2.2M+'];
const SOLD_BAND_MAX = [600000, 700000, 800000, 900000, 1000000, 1100000, 1200000, 1300000, 1600000, 1800000, 2000000, 2200000, Infinity];
const SOLD_PROD_C = {'Single Lot': '#3f6cd1', 'Split Lot': '#8e5bd0', 'Unknown': '#68645f'};
const SOLD_FILTER = {on: false, win: 'all', mo: null, band: 'all', prod: 'all', coh: 'all', sort: null};
const ACTIVE_FILTER = {on: true, prod: 'all'};
const soldById = {};
const soldLayer = L.layerGroup();
const activeLayer = L.layerGroup();
const soldMk = {};
const activeMk = {};
window.HAR_STATE = {ready: false, market: HAR_PAGE, activePins: 0, soldPins: 0, error: null};

function soldBand(cp) {
  for (let i = 0; i < SOLD_BAND_MAX.length; i++) if (cp < SOLD_BAND_MAX[i]) return SOLD_BANDS[i];
  return SOLD_BANDS[SOLD_BANDS.length - 1];
}
function soldMedian(values) {
  if (!values.length) return null;
  const sorted = values.slice().sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}
function soldFiltered() {
  return SOLD_DATA.filter(row => {
    if (SOLD_FILTER.mo) { if (row.mo !== SOLD_FILTER.mo) return false; }
    else if (SOLD_FILTER.win !== 'all' && row.win !== SOLD_FILTER.win) return false;
    if (SOLD_FILTER.band !== 'all' && row.band !== SOLD_FILTER.band) return false;
    if (SOLD_FILTER.prod !== 'all' && row.prod !== SOLD_FILTER.prod) return false;
    if (SOLD_FILTER.coh !== 'all' && row.coh !== SOLD_FILTER.coh) return false;
    return true;
  });
}
function activeFiltered() {
  return ACTIVE_LISTINGS.filter(row => ACTIVE_FILTER.prod === 'all' || row.product === ACTIVE_FILTER.prod);
}
function soldSvlTxt(row) {
  const pct = row.svl * 100;
  return (pct > 0 ? '+' : '') + pct.toFixed(1) + '%';
}
const soldSvlCol = value => value > 0 ? '#e03131' : '#2f9e44';
function soldCardHTML(row, pop) {
  const color = SOLD_PROD_C[row.prod] || '#8c857a';
  let html = '<div class="sx-card' + (pop ? ' sx-pop' : '') + '" style="border-left-color:' + color + '"' + (pop ? '' : ' data-sgo="' + esc(row.id) + '"') + '>';
  html += '<div class="a">' + esc(row.a) + '</div><div class="sx-r2">' + esc(row.prod || 'Unknown') + '</div>';
  html += '<div class="sx-r1"><span class="cp">$' + row.cp.toLocaleString() + '</span><span>' + (row.sq == null ? 'Building size unavailable' : row.sq.toLocaleString() + ' sqft') + '</span><span>' + (row.psf == null ? 'Price per sqft unavailable' : '$' + row.psf + '/sqft') + '</span><span>' + (row.lot ? row.lot.toLocaleString() + ' sqft lot' : 'lot size unknown') + '</span></div>';
  html += '<div class="sx-r1"><span>' + esc(row.cd) + '</span>' + (row.p ? '<span class="sx-presold">PRE-SOLD</span>' : '<span>' + (row.dom != null ? row.dom + ' DOM' : '') + '</span>');
  if (row.svl !== undefined) html += '<span class="sx-svl" style="color:' + soldSvlCol(row.svl) + '">' + soldSvlTxt(row) + ' vs list</span>';
  html += '</div>';
  const bits = [];
  if (row.sch) bits.push('Elem: ' + esc(row.sch));
  if (row.bl) bits.push('Builder: ' + esc(row.bl));
  if (row.la) bits.push('List: ' + esc(row.la));
  if (row.ba) bits.push('Sell: ' + esc(row.ba));
  bits.push('NEW CON');
  html += '<div class="sx-r2">' + bits.join(' · ') + '</div></div>';
  return html;
}
function activeCardHTML(row) {
  const color = SOLD_PROD_C[row.product] || '#8c857a';
  const ask = Number(row.current_list_price);
  let html = '<div class="sx-card sx-pop" style="border-left-color:' + color + '">';
  html += '<div class="a">' + esc(row.address) + '</div><div class="sx-r2">' + esc(row.product || 'Unknown') + ' · Active</div>';
  html += '<div class="sx-r1"><span class="cp">$' + ask.toLocaleString() + '</span><span>Current asking price</span><span>' + (row.lot_sqft ? Number(row.lot_sqft).toLocaleString() + ' sqft lot' : '') + '</span></div>';
  html += '<div class="sx-r2">MLS ' + esc(row.mls) + ' · DOM ' + row.dom + ' · Year ' + row.year_built + '<br>Original list price: $' + Number(row.original_list_price).toLocaleString();
  html += '<br>Builder: ' + esc(row.builder || 'Not supplied') + '<br>List agent: ' + esc(row.list_agent || 'Not supplied') + '</div>';
  html += '<div class="sx-r2">Asking price is the list price on ' + esc(row.as_of) + '.</div></div>';
  return html;
}
function soldChip(sel, val, label, on) {
  return '<button class="sxf' + (on ? ' on' : '') + '" data-sf="' + sel + '" data-v="' + esc(val) + '">' + label + '</button>';
}
function buildSoldDash() {
  const el = document.getElementById('soldBody');
  if (!el) return;
  const rows = soldFiltered();
  const psf = rows.map(row => row.psf).filter(Boolean);
  const svl = rows.filter(row => row.svl !== undefined).map(row => row.svl);
  const dom = rows.filter(row => row.dom != null && !row.p).map(row => row.dom);
  const medPsf = soldMedian(psf), medDom = soldMedian(dom);
  const avgSvl = svl.length ? svl.reduce((a, b) => a + b, 0) / svl.length : null;
  const floor = (SOLD_COMP_POLICY.min_lot_sqft || 2200).toLocaleString();
  let html = '<div class="ovx-top"><span class="ovx-kicker">34DEV · SOLD COMPS</span><span class="ovx-live">● HAR CLOSED SALES · AS OF ' + esc(SOLD_METRICS.as_of || '') + '</span></div>';
  html += '<h2>Sold Comps</h2>';
  html += '<p class="sub">New-construction sold comps · trailing 365 days · in-zone · lots at least ' + floor + ' sqft. Single Lot is 4,000 sqft or more. Split Lot is 2,200 to 3,999 sqft. Tap a card to open its pin.</p>';
  html += '<div class="sx-tiles">';
  html += '<div class="sx-tile"><div class="n">' + rows.length + '</div><div class="l">SOLD</div></div>';
  html += '<div class="sx-tile"><div class="n">' + (medPsf ? '$' + Math.round(medPsf) : '—') + '</div><div class="l">MEDIAN $/SQFT</div></div>';
  html += '<div class="sx-tile"><div class="n" style="color:' + (avgSvl === null ? '#f1ede6' : soldSvlCol(avgSvl)) + '">' + (avgSvl === null ? '—' : ((avgSvl > 0 ? '+' : '') + (avgSvl * 100).toFixed(1) + '%')) + '</div><div class="l">AVG SOLD VS LIST</div></div>';
  html += '<div class="sx-tile"><div class="n">' + (medDom === null ? '—' : Math.round(medDom)) + '</div><div class="l">MEDIAN DOM</div></div>';
  html += '</div>';
  html += '<div class="sxc-row"><span class="cl">Product</span>' + soldChip('prod', 'all', 'ALL', SOLD_FILTER.prod === 'all') + soldChip('prod', 'Single Lot', 'SINGLE', SOLD_FILTER.prod === 'Single Lot') + soldChip('prod', 'Split Lot', 'SPLIT', SOLD_FILTER.prod === 'Split Lot') + '</div>';
  html += '<div class="sxc-row"><span class="cl">Recency</span>' + soldChip('win', 'all', 'ALL', SOLD_FILTER.win === 'all' && !SOLD_FILTER.mo);
  for (const win of SOLD_WINS) html += soldChip('win', win, win, SOLD_FILTER.win === win && !SOLD_FILTER.mo);
  html += '</div>';
  if (!rows.length) html += '<div class="sx-none">No sales match the current filter.</div>';
  else {
    for (const band of SOLD_BANDS) {
      const group = rows.filter(row => row.band === band);
      if (!group.length) continue;
      html += '<div class="sx-bandh"><span>' + esc(band) + '</span><span>' + group.length + ' SALES</span></div>';
      html += '<div class="sx-cards">' + group.map(row => soldCardHTML(row)).join('') + '</div>';
    }
  }
  el.innerHTML = html;
  el.querySelectorAll('[data-sf]').forEach(chip => chip.addEventListener('click', () => {
    const key = chip.getAttribute('data-sf');
    SOLD_FILTER[key] = chip.getAttribute('data-v');
    if (key === 'win') SOLD_FILTER.mo = null;
    renderHar();
  }));
  el.querySelectorAll('[data-sgo]').forEach(card => card.addEventListener('click', () => openSoldPin(card.getAttribute('data-sgo'))));
}
function renderHarPins() {
  soldLayer.clearLayers();
  activeLayer.clearLayers();
  for (const key in soldMk) delete soldMk[key];
  for (const key in activeMk) delete activeMk[key];
  if (SOLD_FILTER.on) {
    const seen = new Map();
    for (const row of soldFiltered().slice().sort((a, b) => b.cd.localeCompare(a.cd))) {
      const key = row.ak || row.a.toLowerCase();
      if (seen.has(key)) { soldMk[row.id] = seen.get(key); continue; }
      const marker = L.circleMarker([row.lat, row.lng], {radius: 5, color: '#fff', weight: 1, fillColor: SOLD_WIN_C[row.win] || '#8c857a', fillOpacity: 0.85});
      marker.bindPopup(() => soldCardHTML(row, true), {maxWidth: 304, minWidth: 290, autoPan: true});
      marker.on('mouseover', function () { this.setStyle({radius: 8, weight: 1.6}); });
      marker.on('mouseout', function () { this.setStyle({radius: 5, weight: 1}); });
      soldMk[row.id] = marker;
      seen.set(key, marker);
      soldLayer.addLayer(marker);
    }
    if (!map.hasLayer(soldLayer)) soldLayer.addTo(map);
  } else if (map.hasLayer(soldLayer)) map.removeLayer(soldLayer);
  if (ACTIVE_FILTER.on) {
    for (const row of activeFiltered()) {
      const marker = L.circleMarker([row.lat, row.lng], {radius: 7, color: '#fff', weight: 1.5, fillColor: SOLD_PROD_C[row.product] || '#2f9e44', fillOpacity: 0.92});
      marker.bindPopup(() => activeCardHTML(row), {maxWidth: 304, minWidth: 290, autoPan: true});
      marker.on('mouseover', function () { this.setStyle({radius: 10, weight: 2}); });
      marker.on('mouseout', function () { this.setStyle({radius: 7, weight: 1.5}); });
      activeMk[row.mls] = marker;
      activeLayer.addLayer(marker);
    }
    if (!map.hasLayer(activeLayer)) activeLayer.addTo(map);
  } else if (map.hasLayer(activeLayer)) map.removeLayer(activeLayer);
  window.HAR_STATE.activePins = activeLayer.getLayers().length;
  window.HAR_STATE.soldPins = soldLayer.getLayers().length;
}
function renderHar() {
  SOLD_FILTER.on = activeF.has('G:sold');
  renderHarPins();
  const tab = document.getElementById('soldtab');
  if (tab && tab.style.display === 'block') buildSoldDash();
  renderLegend();
  refresh();
}
function openSoldPin(id) {
  if (!activeF.has('G:sold')) { activeF.add('G:sold'); renderHar(); }
  switchTab('map');
  const marker = soldMk[id];
  if (!marker) return;
  const small = window.matchMedia('(max-width:560px)').matches;
  if (small && panel) panel.classList.add('collapsed');
  setTimeout(() => {
    map.invalidateSize();
    map.setView(marker.getLatLng(), 17, {animate: false});
    setTimeout(() => marker.openPopup(), 140);
  }, 200);
}
function openActivePin(mls) {
  switchTab('map');
  const marker = activeMk[mls];
  if (!marker) return;
  map.setView(marker.getLatLng(), 17, {animate: false});
  setTimeout(() => marker.openPopup(), 140);
}
function appendHarLegend() {
  const el = document.getElementById('legend');
  if (!el || el.querySelector('[data-har-layers]')) return;
  const activeRows = activeFiltered();
  const byProduct = {};
  ACTIVE_LISTINGS.forEach(row => { byProduct[row.product] = (byProduct[row.product] || 0) + 1; });
  let html = '<div data-har-layers class="grp"><div class="grp-h' + (ACTIVE_FILTER.on ? ' on' : '') + '" data-atoggle="1"><span class="mbox' + (ACTIVE_FILTER.on ? ' on' : '') + '" data-atoggle="1"></span><span class="gn">Active Listings</span><span class="ct2">' + activeRows.length + '</span></div><div class="grp-body">';
  for (const product of ['Single Lot', 'Split Lot']) {
    html += '<div class="leafrow' + (ACTIVE_FILTER.prod === product ? ' on' : '') + '" data-aprod="' + product + '"><span class="sw" style="background:' + SOLD_PROD_C[product] + '"></span><span class="nm">' + product + '</span><span class="ct2">' + (byProduct[product] || 0) + '</span></div>';
  }
  html += '<div class="pmeta" style="padding:6px 12px">HAR ' + esc((ACTIVE_LISTINGS[0] && ACTIVE_LISTINGS[0].as_of) || '') + ' · blue single, purple split · current asking price is in the popup</div></div></div>';
  const soldRows = SOLD_FILTER.on ? soldFiltered() : SOLD_DATA;
  const soldByProduct = {};
  SOLD_DATA.forEach(row => { soldByProduct[row.prod] = (soldByProduct[row.prod] || 0) + 1; });
  html += '<div class="grp" data-grp="soldc"><div class="grp-h' + (SOLD_FILTER.on ? ' on' : '') + '" data-stoggle="1"><span class="mbox' + (SOLD_FILTER.on ? ' on' : '') + '" data-stoggle="1"></span><span class="gn">Sold Comps</span><span class="ct2">' + soldRows.length + '</span></div><div class="grp-body">';
  for (const product of ['Single Lot', 'Split Lot']) {
    html += '<div class="leafrow' + (SOLD_FILTER.prod === product ? ' on' : '') + '" data-sprod="' + product + '"><span class="sw" style="background:' + SOLD_PROD_C[product] + '"></span><span class="nm">' + product + '</span><span class="ct2">' + (soldByProduct[product] || 0) + '</span></div>';
  }
  html += '<div class="pmeta" style="padding:6px 12px">Trailing 365 days · lots at least ' + (SOLD_COMP_POLICY.min_lot_sqft || 2200).toLocaleString() + ' sqft. Turning this on hides construction pins.</div></div></div>';
  el.insertAdjacentHTML('afterbegin', html);
  el.querySelector('[data-atoggle]').addEventListener('click', event => {
    event.stopPropagation();
    ACTIVE_FILTER.on = !ACTIVE_FILTER.on;
    if (ACTIVE_FILTER.on) ACTIVE_FILTER.prod = 'all';
    renderHar();
  });
  el.querySelectorAll('[data-aprod]').forEach(leaf => leaf.addEventListener('click', () => {
    const product = leaf.getAttribute('data-aprod');
    ACTIVE_FILTER.prod = ACTIVE_FILTER.prod === product ? 'all' : product;
    ACTIVE_FILTER.on = true;
    renderHar();
  }));
  el.querySelector('[data-stoggle]').addEventListener('click', event => {
    event.stopPropagation();
    if (activeF.has('G:sold')) activeF.delete('G:sold');
    else { activeF.add('G:sold'); SOLD_FILTER.win = 'all'; SOLD_FILTER.prod = 'all'; }
    renderHar();
  });
  el.querySelectorAll('[data-sprod]').forEach(leaf => leaf.addEventListener('click', () => {
    const product = leaf.getAttribute('data-sprod');
    SOLD_FILTER.prod = SOLD_FILTER.prod === product ? 'all' : product;
    activeF.add('G:sold');
    renderHar();
  }));
}
const harOriginalLegend = renderLegend;
renderLegend = function () {
  harOriginalLegend();
  appendHarLegend();
};
const harOriginalRefresh = refresh;
refresh = function () {
  harOriginalRefresh();
  const soldOn = activeF.has('G:sold') && map.hasLayer(soldLayer);
  const activeOn = ACTIVE_FILTER.on && map.hasLayer(activeLayer);
  const extra = (soldOn ? soldLayer.getLayers().length : 0) + (activeOn ? activeLayer.getLayers().length : 0);
  if (!extra) return;
  const shown = document.getElementById('shown');
  const total = document.getElementById('total');
  const shownN = Number(String(shown.textContent).replace(/,/g, '')) + extra;
  const totalN = Number(String(total.textContent).replace(/,/g, '')) + (soldOn ? SOLD_DATA.length : 0) + (activeOn ? ACTIVE_LISTINGS.length : 0);
  shown.textContent = shownN.toLocaleString();
  total.textContent = totalN.toLocaleString();
};
const harOriginalSwitch = switchTab;
switchTab = function (tab) {
  harOriginalSwitch(tab);
  const sold = document.getElementById('soldtab');
  if (sold) sold.style.display = tab === 'sold' ? 'block' : 'none';
  if (tab === 'sold') buildSoldDash();
  else setTimeout(() => map.invalidateSize(), 60);
};

async function loadHarLayers() {
  try {
    const [activeRes, soldRes] = await Promise.all([
      fetch(HAR_PAGE + '_active.data.json', {cache: 'no-store'}),
      fetch(HAR_PAGE + '_sold.data.json', {cache: 'no-store'}),
    ]);
    if (!activeRes.ok || !soldRes.ok) throw Error('HAR files missing');
    const activeDoc = await activeRes.json();
    const soldDoc = await soldRes.json();
    if (!Array.isArray(activeDoc.listings) || !Array.isArray(soldDoc.comps)) throw Error('Invalid HAR snapshot');
    ACTIVE_LISTINGS = activeDoc.listings;
    SOLD_DATA = soldDoc.comps;
    SOLD_METRICS = soldDoc.metrics || {as_of: soldDoc.as_of || ''};
    SOLD_COMP_POLICY = soldDoc.policy || {min_lot_sqft: 2200};
    SOLD_DATA.forEach(row => { row.band = soldBand(row.cp); soldById[row.id] = row; });
    window.HAR_STATE.ready = true;
    window.HAR_STATE.error = null;
  } catch (error) {
    window.HAR_STATE.error = error.message;
    console.error('HAR layers', error);
  }
  renderHar();
}
loadHarLayers();
