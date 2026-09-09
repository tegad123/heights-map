/* Independent HAR evidence layer. Never mutates DATA, tags, or supply calculations. */
const ACTIVE_VIEW = {ready:false, listings:[], byPin:new Map(), byAddress:new Map(), error:null};
function activeAddressKey(address){
  let s=String(address).toLowerCase().split(',')[0].replace(/\b(?:houston|tx|texas|77\d{3})\b.*/,'').replace(/\b(?:unit|apt)\s*#?\s*|#/g,' ').replace(/(\d)-?([a-f])\b/g,'$1 $2').replace(/\b(\d+)\s+(st|nd|rd|th)\b/g,'$1$2').replace(/[^a-z0-9/ ]/g,' ');
  const aliases={street:'st',avenue:'ave',lane:'ln',drive:'dr',road:'rd',court:'ct',place:'pl',boulevard:'blvd',east:'e',west:'w',north:'n',south:'s'};
  let w=s.trim().split(/\s+/).map(x=>aliases[x]||x);
  if(w.length>2&&/^\d+$/.test(w[0])&&/^[abcdf]$/.test(w[1]))w.push(w.splice(1,1)[0]);
  if(w.length>3&&/^[ewns]$/.test(w[1])&&/^\d/.test(w[2]))w.push(w.splice(1,1)[0]);
  w=w.filter((x,i)=>!(i&&x===w[i-1]&&['st','ave','ln','dr','rd','ct','pl','blvd'].includes(x)));
  return w.join(' ');
}
function activeMembers(r){return r._twin?[r,r._twin]:[r];}
function activeEvidence(c){
  const key=activeAddressKey(c.a), listing=ACTIVE_VIEW.byAddress.get(key);
  const sales=SOLD_DATA.filter(s=>activeAddressKey(s.a)===key).sort((a,b)=>b.cd.localeCompare(a.cd));
  return {listing,sales};
}
function activePopupFacts(r){
  let h='<section class="active-facts" style="font-size:12px;line-height:1.5;margin:12px 0;padding:10px;border:1px solid #2f9e44;border-radius:8px"><div class="lbl">Listing evidence · '+esc(ACTIVE_VIEW.asOf)+'</div>';
  for(const c of activeMembers(r)){
    const {listing,sales}=activeEvidence(c);
    const rec=RECONCILE.pending[c.id]?'Pending / Under Contract':RECONCILE.off[c.id]?'Off Market':null;
    h+='<div style="margin-top:8px"><b>'+esc(c.a)+'</b><br>';
    if(listing)h+='<strong style="color:#2f9e44">Active in HAR export</strong><br>MLS '+esc(listing.mls)+' · '+esc(listing.product)+'<br>Original list price: $'+listing.original_list_price.toLocaleString()+'<br>DOM: '+listing.dom+' days · Lot: '+listing.lot_sqft.toLocaleString()+' sq ft<br>Builder: '+esc(listing.builder||'Not supplied')+'<br>List agent: '+esc(listing.list_agent||'Not supplied');
    else if(sales.length)h+='<strong>Sold record: '+esc(sales[0].cd)+'</strong> · $'+sales[0].cp.toLocaleString()+' · MLS '+esc(sales[0].id.slice(1))+'<br>Absent from this active export; subsequent listing status unverified.';
    else h+='Not in this active export; no matching sold comp. Availability unverified.';
    if(listing&&sales.length)h+='<br>Historical sale: '+esc(sales[0].cd)+' (separate transaction).';
    if(rec)h+='<br><span class="pmeta">Prior recorded status: '+esc(rec)+'; retained for review.</span>';
    h+='</div>';
  }
  h+='<div class="pmeta" style="margin-top:8px">Original list price is not a verified current asking price. Export coverage is limited.'+(r._twin?' Construction evidence below belongs to the paired project.':'')+'</div></section>';
  return h;
}
const activeOriginalPopup=popupHTML;
popupHTML=function(r){
  const original=activeOriginalPopup(r);if(!ACTIVE_VIEW.ready)return original;
  const doc=document.createElement('div');doc.innerHTML=original;
  const card=doc.querySelector('.card');if(!card)return original;
  const llc=card.querySelector('.llc');if(llc&&/active listing/i.test(llc.textContent))llc.textContent='Property record';
  // Distinguish old market labels from inspection-certified construction.
  if(homePhase(r.id)==='market'){
    const chip=card.querySelector('.phasechip'),time=card.querySelector('.phasetime');
    if(chip)chip.textContent='COMPLETION NOT VERIFIED';
    if(time)time.textContent='Prior map stage: Active (Finished)';
  }
  card.querySelectorAll('.lbl').forEach(el=>{
    if(el.textContent==='Tags')el.textContent='Prior stored tags · may be stale';
    if(el.textContent==='Notes')el.textContent='Stored notes · historical';
    if(el.textContent==='List price')el.textContent='Prior stored list price';
    if(el.textContent==='Listed')el.textContent='Prior stored listing date';
  });
  // Legacy paired-status summaries are replaced by address-specific evidence above.
  card.querySelectorAll('.addr').forEach(el=>{if(el.style.color&&/active|pending|off market/.test(el.textContent))el.remove();});
  const anchor=card.querySelector('.phasehead')||card.querySelector('.grid');
  if(anchor)anchor.insertAdjacentHTML('beforebegin',activePopupFacts(r));else card.insertAdjacentHTML('beforeend',activePopupFacts(r));
  return doc.innerHTML;
};
const activeOriginalMatch=matchSel;
matchSel=function(tags,k,id){
  if(k.startsWith('AL:')&&inventoryCategory(id))return false;
  if(k.startsWith('AL:'))return (ACTIVE_VIEW.byPin.get(id)||[]).some(r=>k==='AL:all'||r.product===k.slice(3));
  return activeOriginalMatch(tags,k,id);
};
function renderActiveLegend(){
  const eligible=ACTIVE_VIEW.listings.filter(r=>![...ACTIVE_VIEW.byPin].some(([id,rows])=>inventoryCategory(id)&&rows.includes(r)));
  const el=document.getElementById('legend');el.querySelector('[data-active-listings]')?.remove();
  let h='<div data-active-listings class="grp"><div class="grp-h"><span class="gn">Active Listings</span><span class="ct2">'+eligible.length+'</span></div>';
  if(!ACTIVE_VIEW.ready)h+='<div class="pmeta">'+esc(ACTIVE_VIEW.error||'Loading HAR snapshot…')+'</div>';
  else {
    for(const prod of ['Single Lot','Split Lot']){
      const key='AL:'+prod,count=eligible.filter(r=>r.product===prod).length;
      h+='<button type="button" class="leafrow'+sOn(key)+'" data-active-product="'+prod+'" aria-pressed="'+activeF.has(key)+'" style="width:100%;border:0;font:inherit;color:inherit;background:transparent;text-align:left"><span class="sw" style="background:#2f9e44"></span><span class="nm">'+prod+'</span><span class="ct2">'+count+'</span></button>';
    }
    h+='<div class="pmeta" style="padding:6px 12px;font-size:10px;color:var(--muted)">HAR '+esc(ACTIVE_VIEW.asOf)+' · listing counts, paired pins may overlap</div>';
  }
  h+='</div>';el.insertAdjacentHTML('afterbegin',h);
  el.querySelectorAll('[data-active-product]').forEach(button=>button.addEventListener('click',()=>{
    const key='AL:'+button.dataset.activeProduct;activeF.has(key)?activeF.delete(key):activeF.add(key);renderLegend();refresh();
  }));
}
const activeOriginalLegend=renderLegend;
renderLegend=function(){activeOriginalLegend();renderActiveLegend();};
async function loadActiveListings(){
  try{
    const response=await fetch('heights_active.data.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);
    const data=await response.json();if(!Array.isArray(data.listings)||!data.as_of)throw Error('Invalid snapshot');
    const idx=new Map();for(const r of DATA)for(const c of activeMembers(r)){
      const key=activeAddressKey(c.a);if(!idx.has(key))idx.set(key,[]);idx.get(key).push(r.id);
    }
    const byPin=new Map(),byAddress=new Map();
    for(const listing of data.listings){
      const key=activeAddressKey(listing.address),ids=[...new Set(idx.get(key)||[])];
      if(ids.length!==1||byAddress.has(key))throw Error('Ambiguous or missing property match: '+listing.address);
      if(!byPin.has(ids[0]))byPin.set(ids[0],[]);byPin.get(ids[0]).push(listing);byAddress.set(key,listing);
    }
    Object.assign(ACTIVE_VIEW,{ready:true,asOf:data.as_of,listings:data.listings,byPin,byAddress});
  }catch(e){ACTIVE_VIEW.error='Active listings unavailable: '+e.message;console.error(ACTIVE_VIEW.error);}
  renderLegend();refresh();
}
loadActiveListings();
