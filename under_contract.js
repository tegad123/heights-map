/* Under Contract layer for every market page.
   Reads <market>_pending.data.json. One address is not also drawn as Active or Sold. */
const UC_PAGE = document.currentScript && document.currentScript.dataset.market;
const UC_COLOR = '#d6336c';
const UC_STATUSES = ['Pending', 'Option Pending', 'Pend Cont to Show'];
const UC_FILTER = {on: true, status: 'all'};
const UC_LISTINGS = [];
const UC_KEYS = new Set();
const ucLayer = L.layerGroup();
const ucMk = {};
window.UC_KEYS = UC_KEYS;
window.UC_LISTINGS = UC_LISTINGS;
window.UC_STATE = {ready: false, market: UC_PAGE, pins: 0, error: null};

function ucKey(address) {
  let s = String(address || '').toLowerCase().split(',')[0].replace(/\b(?:houston|tx|texas|77\d{3})\b.*/, '').replace(/\b(?:unit|apt)\s*#?\s*|#/g, ' ').replace(/(\d)-?([a-f])\b/g, '$1 $2').replace(/\b(\d+)\s+(st|nd|rd|th)\b/g, '$1$2').replace(/[^a-z0-9/ ]/g, ' ');
  const aliases = {street: 'st', avenue: 'ave', lane: 'ln', drive: 'dr', road: 'rd', court: 'ct', place: 'pl', boulevard: 'blvd', east: 'e', west: 'w', north: 'n', south: 's'};
  let w = s.trim().split(/\s+/).filter(Boolean).map(x => aliases[x] || x);
  if (w.length > 2 && /^\d+$/.test(w[0]) && /^[abcdf]$/.test(w[1])) w.push(w.splice(1, 1)[0]);
  if (w.length > 3 && /^[ewns]$/.test(w[1]) && /^\d/.test(w[2])) w.push(w.splice(1, 1)[0]);
  w = w.filter((x, i) => !(i && x === w[i - 1] && ['st', 'ave', 'ln', 'dr', 'rd', 'ct', 'pl', 'blvd'].includes(x)));
  return w.join(' ');
}
window.ucClaimsAddress = function (address) {
  const key = ucKey(address);
  return UC_KEYS.has(key) || UC_KEYS.has(String(address || '').toLowerCase());
};
function ucMoney(value) {
  const n = Number(value);
  return Number.isFinite(n) ? '$' + Math.round(n).toLocaleString() : '—';
}
function ucFiltered() {
  return UC_LISTINGS.filter(row => UC_FILTER.status === 'all' || row.har_status === UC_FILTER.status);
}
function ucCardHTML(row, pop) {
  const lot = row.lot_sqft ? Number(row.lot_sqft).toLocaleString() + ' sqft lot' : 'lot size unknown';
  const sqft = row.sqft ? Number(row.sqft).toLocaleString() + ' sqft' : 'sqft unavailable';
  let html = '<div class="sx-card' + (pop ? ' sx-pop' : '') + '" style="border-left-color:' + UC_COLOR + '"' + (pop ? '' : ' data-ugo="' + esc(row.mls) + '"') + '>';
  html += '<div class="a">' + esc(row.address) + '</div>';
  html += '<div class="sx-r2">' + esc(row.har_status || 'Pending') + ' · Under Contract</div>';
  html += '<div class="sx-r1"><span class="cp">' + ucMoney(row.current_list_price) + '</span><span>List price</span><span>' + (row.dom != null ? row.dom + ' DOM' : '') + '</span><span>' + sqft + '</span><span>' + lot + '</span></div>';
  html += '<div class="sx-r2">MLS ' + esc(row.mls) + ' · ' + esc(row.product || '') + '<br>Builder: ' + esc(row.builder || 'Not supplied') + '<br>Listing agent: ' + esc(row.list_agent || 'Not supplied');
  if (row.har_url) html += '<br><a href="' + esc(row.har_url) + '" target="_blank" rel="noopener">HAR listing</a>';
  html += '</div></div>';
  return html;
}
function ensureContractTab() {
  if (document.querySelector('.tab[data-t="contract"]')) return;
  const tabs = document.getElementById('tabs');
  const sold = tabs && tabs.querySelector('[data-t="sold"]');
  if (!sold) return;
  const btn = sold.cloneNode(true);
  btn.classList.remove('on');
  btn.dataset.t = 'contract';
  btn.setAttribute('aria-label', 'Under Contract');
  const label = btn.querySelector('span');
  if (label) label.textContent = 'Contract';
  sold.after(btn);
  btn.addEventListener('click', () => switchTab('contract'));
  const overlay = document.createElement('div');
  overlay.id = 'contracttab';
  overlay.className = 'overlay';
  overlay.innerHTML = '<div class="dash" id="contractBody"></div>';
  const soldTab = document.getElementById('soldtab');
  if (soldTab) soldTab.after(overlay);
  else document.body.appendChild(overlay);
  if (!document.getElementById('uc-tab-width')) {
    const style = document.createElement('style');
    style.id = 'uc-tab-width';
    style.textContent = '@media(min-width:1024px){#tabs{width:640px;max-width:640px}}';
    document.head.appendChild(style);
  }
}
function buildContractDash() {
  const el = document.getElementById('contractBody');
  if (!el) return;
  const rows = ucFiltered().slice().sort((a, b) => Number(b.current_list_price) - Number(a.current_list_price));
  const asOf = (UC_LISTINGS[0] && UC_LISTINGS[0].as_of) || '';
  let html = '<div class="ovx-top"><span class="ovx-kicker">34DEV · UNDER CONTRACT</span><span class="ovx-live">● HAR PENDING · AS OF ' + esc(asOf) + '</span></div>';
  html += '<h2>Under Contract</h2>';
  html += '<p class="sub">New-construction homes under contract · Pending, Option Pending, and Pend Cont to Show · in-zone · lots at least 2,200 sqft. A home here is not also listed as Active or Sold. Tap a card to open its pin.</p>';
  html += '<div class="sx-tiles"><div class="sx-tile"><div class="n">' + rows.length + '</div><div class="l">UNDER CONTRACT</div></div></div>';
  if (!rows.length) html += '<div class="sx-none">' + (window.UC_STATE.error ? esc(window.UC_STATE.error) : 'No under-contract listings in this market.') + '</div>';
  else html += '<div class="sx-cards">' + rows.map(row => ucCardHTML(row)).join('') + '</div>';
  el.innerHTML = html;
  el.querySelectorAll('[data-ugo]').forEach(card => card.addEventListener('click', () => openContractPin(card.getAttribute('data-ugo'))));
}
function renderContractPins() {
  ucLayer.clearLayers();
  for (const key in ucMk) delete ucMk[key];
  if (!UC_FILTER.on) {
    if (map.hasLayer(ucLayer)) map.removeLayer(ucLayer);
    window.UC_STATE.pins = 0;
    return;
  }
  const piled = new Map();
  for (const row of ucFiltered()) {
    if (row.lat == null || row.lng == null) continue;
    const pile = row.lat.toFixed(5) + ',' + row.lng.toFixed(5);
    const n = piled.get(pile) || 0;
    piled.set(pile, n + 1);
    const lat = Number(row.lat) + n * 0.00008;
    const marker = L.circleMarker([lat, row.lng], {radius: 7, color: '#fff', weight: 1.5, fillColor: UC_COLOR, fillOpacity: 0.92});
    marker.bindPopup(() => ucCardHTML(row, true), {maxWidth: 320, minWidth: 280, autoPan: true});
    marker.on('mouseover', function () { this.setStyle({radius: 10, weight: 2}); });
    marker.on('mouseout', function () { this.setStyle({radius: 7, weight: 1.5}); });
    ucMk[row.mls] = marker;
    ucLayer.addLayer(marker);
  }
  if (!map.hasLayer(ucLayer)) ucLayer.addTo(map);
  window.UC_STATE.pins = ucLayer.getLayers().length;
}
function renderContract() {
  renderContractPins();
  const tab = document.getElementById('contracttab');
  if (tab && tab.style.display === 'block') buildContractDash();
  if (typeof renderLegend === 'function') renderLegend();
  if (typeof refresh === 'function') refresh();
  if (typeof renderHar === 'function') renderHar();
  if (typeof renderSoldAll === 'function') renderSoldAll();
}
function openContractPin(mls) {
  UC_FILTER.on = true;
  renderContractPins();
  switchTab('map');
  const marker = ucMk[mls];
  if (!marker) return;
  const small = window.matchMedia('(max-width:560px)').matches;
  if (small && typeof panel !== 'undefined' && panel) panel.classList.add('collapsed');
  setTimeout(() => {
    map.invalidateSize();
    map.setView(marker.getLatLng(), 17, {animate: false});
    setTimeout(() => marker.openPopup(), 140);
  }, 200);
}
function appendContractLegend() {
  const el = document.getElementById('legend');
  if (!el) return;
  const prior = el.querySelector('[data-uc-layer]');
  if (prior) prior.remove();
  const rows = ucFiltered();
  const byStatus = {};
  UC_LISTINGS.forEach(row => { byStatus[row.har_status] = (byStatus[row.har_status] || 0) + 1; });
  let html = '<div data-uc-layer class="grp"><div class="grp-h' + (UC_FILTER.on ? ' on' : '') + '" data-uctoggle="1"><span class="mbox' + (UC_FILTER.on ? ' on' : '') + '"></span><span class="gn">Under Contract</span><span class="ct2">' + rows.length + '</span></div><div class="grp-body">';
  for (const status of UC_STATUSES) {
    html += '<div class="leafrow' + (UC_FILTER.status === status ? ' on' : '') + '" data-ustatus="' + esc(status) + '"><span class="sw" style="background:' + UC_COLOR + '"></span><span class="nm">' + esc(status) + '</span><span class="ct2">' + (byStatus[status] || 0) + '</span></div>';
  }
  html += '<div class="pmeta" style="padding:6px 12px">HAR ' + esc((UC_LISTINGS[0] && UC_LISTINGS[0].as_of) || '') + ' · not counted as Active or Sold</div></div></div>';
  el.insertAdjacentHTML('afterbegin', html);
  const group = el.querySelector('[data-uc-layer]');
  group.querySelector('[data-uctoggle]').addEventListener('click', event => {
    event.stopPropagation();
    UC_FILTER.on = !UC_FILTER.on;
    if (UC_FILTER.on) UC_FILTER.status = 'all';
    renderContractPins();
    renderLegend();
    refresh();
  });
  group.querySelectorAll('[data-ustatus]').forEach(leaf => leaf.addEventListener('click', () => {
    const status = leaf.getAttribute('data-ustatus');
    UC_FILTER.status = UC_FILTER.status === status ? 'all' : status;
    UC_FILTER.on = true;
    renderContractPins();
    const tab = document.getElementById('contracttab');
    if (tab && tab.style.display === 'block') buildContractDash();
    renderLegend();
    refresh();
  }));
}
ensureContractTab();
const ucOriginalSwitch = switchTab;
switchTab = function (tab) {
  ucOriginalSwitch(tab);
  const contract = document.getElementById('contracttab');
  if (contract) contract.style.display = tab === 'contract' ? 'block' : 'none';
  if (tab === 'contract') buildContractDash();
};
const ucOriginalLegend = renderLegend;
renderLegend = function () {
  ucOriginalLegend();
  appendContractLegend();
};
const ucOriginalRefresh = refresh;
refresh = function () {
  ucOriginalRefresh();
  if (!UC_FILTER.on || !map.hasLayer(ucLayer)) return;
  const extra = ucLayer.getLayers().length;
  if (!extra) return;
  const shown = document.getElementById('shown');
  const total = document.getElementById('total');
  if (!shown || !total) return;
  const shownN = Number(String(shown.textContent).replace(/,/g, '')) + extra;
  const totalN = Number(String(total.textContent).replace(/,/g, '')) + UC_LISTINGS.length;
  shown.textContent = shownN.toLocaleString();
  total.textContent = totalN.toLocaleString();
};

async function loadUnderContract() {
  try {
    const response = await fetch(UC_PAGE + '_pending.data.json', {cache: 'no-store'});
    if (!response.ok) throw Error('Under Contract file missing');
    const doc = await response.json();
    if (!Array.isArray(doc.listings)) throw Error('Invalid under-contract snapshot');
    UC_LISTINGS.splice(0, UC_LISTINGS.length, ...doc.listings);
    UC_KEYS.clear();
    for (const row of UC_LISTINGS) {
      if (row.address_key) UC_KEYS.add(row.address_key);
      UC_KEYS.add(ucKey(row.address));
    }
    window.UC_STATE.ready = true;
    window.UC_STATE.error = null;
  } catch (error) {
    window.UC_STATE.error = error.message;
    console.error('Under Contract', error);
  }
  renderContractPins();
  if (typeof renderLegend === 'function') renderLegend();
  if (typeof refresh === 'function') refresh();
  if (typeof renderHar === 'function') renderHar();
  if (typeof renderSoldAll === 'function') renderSoldAll();
}
if (window.requestIdleCallback) requestIdleCallback(function () { loadUnderContract(); }, {timeout: 1500});
else setTimeout(loadUnderContract, 1);
