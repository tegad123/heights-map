/* Client-researched classifications, 2026-09-09. No construction inference.
 * Applied by exact DATA id only. Other markets use the same category display.
 */
const CLIENT_CLASSIFICATIONS = document.currentScript.dataset.market==='heights' ? {
  custom: ['pmt_1032-key-st-77009','pmt_1225-ashland-st-a-77008','pmt_1336-herkimer-st-77008','pmt_1434-herkimer-st-77008','pmt_1132-e-6th-1-2-st-77009','pmt_625-merrill-st-77009','pmt_705-e-13th-st-77008','pmt_745-e-16th-st-77008','pmt_806-peddie-st-77008','pmt_839-allston-st-77007','pmt_1314-e-28th-st-77009','pmt_734-e-7th-1-2-st-77007','pmt_918-dorothy-st-77008','pmt_930-waverly-st-77008','pmt_1602-turnpike-rd-77008','pmt_410-columbia-st-77007','pmt_715-e-12th-st-77008','pmt_826-e-27th-st-77009','2131284475'],
  sold_off_market: ['pmt_728-euclid-st-77009'],
  needs_clarification: ['pmt_1019-e-7th-st-77009','pmt_822-nashua-st-77008','pmt_1109-voight-st-77009','pmt_433-w-23rd-st-77008']
} : {};
const CLIENT_PRIOR = {};
for(const ids of Object.values(CLIENT_CLASSIFICATIONS))for(const id of ids){
  CLIENT_PRIOR[id]={category:inventoryCategory(id),tags:[...((state.points[id]||{}).tags||[])]};
}
function applyClientClassifications(){
  for(const [tag,ids] of Object.entries(CLIENT_CLASSIFICATIONS))for(const id of ids){
    if(!DATA.some(r=>r.id===id))continue;
    const point=pt(id);
    if(!point.tags.includes(tag))point.tags.push(tag);
    point.classification={source:'Client research',date:'2026-09-09',category:tag};
    if(id==='pmt_745-e-16th-st-77008')point.classification.subtype='remodel';
  }
}
// ensureTags runs after remote merge and on every legend rebuild. Preserve
// independently computed phase tags and ETAs, while restoring client labels.
const clientEnsureTags=ensureTags;
ensureTags=function(){applyClientClassifications();return clientEnsureTags();};
const clientMatchSel=matchSel;
matchSel=function(tags,key,id){
  if(key.startsWith('IC:')){
    const [,category,product]=key.split(':');
    return inventoryCategory(id)===category&&(prodKeyR(byId[id])||'Unknown')===product;
  }
  return clientMatchSel(tags,key,id);
};
const clientRenderLegend=renderLegend;
renderLegend=function(){
  clientRenderLegend();
  for(const category of ['custom','sold_off_market']){
    const root=document.querySelector('#legend > [data-grp="'+category+'"]');
    if(!root||categoryCount(category)<3)continue;
    const body=document.createElement('div');body.className='grp-body';
    for(const product of ['Single Lot','Split Lot','Common Driveway','Unknown']){
      const count=DATA.reduce((n,r)=>n+(inventoryCategory(r.id)===category&&(prodKeyR(r)||'Unknown')===product?UW(r.id):0),0);
      if(!count)continue;
      const key='IC:'+category+':'+product;
      const button=document.createElement('button');button.type='button';button.className='leafrow'+sOn(key);
      button.style.cssText='width:100%;border:0;background:transparent;color:inherit;font:inherit;text-align:left';
      button.setAttribute('aria-pressed',String(activeF.has(key)));button.dataset.categoryProduct=key;
      button.innerHTML='<span class="mbox'+sOn(key)+'"></span><span class="nm">'+esc(product)+'</span><span class="ct2">'+count+'</span>';
      button.addEventListener('click',()=>{activeF.has(key)?activeF.delete(key):activeF.add(key);renderLegend();refresh();});
      body.appendChild(button);
    }
    root.appendChild(body);
  }
};
const clientPopupHTML=popupHTML;
popupHTML=function(r){
  const html=clientPopupHTML(r),classification=(state.points[r.id]||{}).classification;
  if(!classification)return html;
  const doc=document.createElement('div');doc.innerHTML=html;
  const card=doc.querySelector('.card');
  if(card){const note=document.createElement('div');note.className='pmeta client-classification';note.textContent='Client research · '+classification.date+(classification.subtype?' · '+classification.subtype:'');card.appendChild(note);}
  return doc.innerHTML;
};
applyClientClassifications();renderLegend();refresh();buildOverview();buildTimeline();renderSupplyCard();
