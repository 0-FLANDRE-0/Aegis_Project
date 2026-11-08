// EMCON_B PR74 correction 2 — profile-derived global/category/equipment controls.
const EMCON_B_CATEGORY_LABEL=Object.freeze({AIR_SEARCH:'대공 레이더',SURFACE_SEARCH:'대수상 레이더',NAV:'항해 레이더',FIRE_CONTROL:'사격통제 레이더',ECM:'ECM'});
const EMCON_B_REASON_LABEL=Object.freeze({ALL_RADIATION_SILENT:'전파방사통제',CATEGORY_RADIATE:'범주 방사 허용',CATEGORY_SILENT:'범주 침묵',OVERRIDE_RADIATE:'장비 강제 방사',OVERRIDE_SILENT:'장비 강제 침묵',MASTER_SILENT:'레이더 마스터 침묵',NETWORK_SILENT:'함대 공동 침묵',EQUIPMENT_DISABLED:'기존 장비 OFF',DAMAGE:'손상',SHIP_OFFLINE:'함정 장비 정지',REGISTERED_INACTIVE:'비활성 등록',NOT_INSTALLED:'미장착'});
function emconUiOwnerB(){return (typeof fleetOwnerG==='function'?fleetOwnerG():null)??ACTIVE_SHIP_RUNTIME;}
function emconUiOwnerLabelB(r){return (r===ACTIVE_SHIP_RUNTIME?'자함':r.role==='ALLY'&&r.faction==='FRIENDLY'?'아군함':r.role==='NEUTRAL'?'중립함':'비우호 함정')+' · '+r.profileId;}
function emconUiCommandAllowedB(r){return !!r&&(r===ACTIVE_SHIP_RUNTIME||r.role==='ALLY'&&r.faction==='FRIENDLY')&&!sovHullA(r)&&shipEmitterRegistryA(r)?.physicalEmission!==false;}
function emconUiMasterSilentB(r){return r===ACTIVE_SHIP_RUNTIME?!!emconActive:!!observerC(r).emcon;}
function emconUiEcmLevelB(r){
  if(r===ACTIVE_SHIP_RUNTIME)return ownEcmLevelE();
  const e=prepareElectronicF(r);return e.auto&&(e.noiseRequested||e.deceptionRequested)?'FULL':'OFF';
}
function emconUiEcmCommandB(r,level){
  if(!['OFF','JAM','FULL'].includes(level))return {ok:false,reason:'ECM_LEVEL'};
  if(r===ACTIVE_SHIP_RUNTIME)return ownEcmCommandE(level);
  if(r.role!=='ALLY'||r.faction!=='FRIENDLY')return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  const on=level!=='OFF';return electronicCommandF(r.entityId,{auto:on,noiseRequested:on,deceptionRequested:on,autoAim:true});
}
function emconUiDetailCommandB(r,command){return emconCommandB(r?.entityId,command,'OPERATOR');}
function emconUiAllSilentB(r){return emconStateViewB(r).allRadiationSilent===true;}
function emconAllRadiationMacroB(r){
  if(!r||r!==ACTIVE_SHIP_RUNTIME&&(r.role!=='ALLY'||r.faction!=='FRIENDLY'))return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  return emconGlobalCommandB(r.entityId,!emconUiAllSilentB(r),'OPERATOR');
}
function emconUiChipSnapshotB(){
  const r=emconUiOwnerB(),registry=shipEmitterRegistryA(r),radar=EMCON_B_RADAR_CATEGORIES.filter(category=>registry?.entries?.some(q=>q.category===category)),active=radar.filter(category=>emconCategoryAllowsB(r,category)).length,
    ecm=(registry?.entries??[]).find(q=>q.category==='ECM'),decision=ecm?emconEquipmentDecisionB(r,ecm.id):null,master=emconUiMasterSilentB(r),global=emconUiAllSilentB(r),ecmCode=decision?.emissionActive?'TX':decision?.allowed?'ARMED':decision?.ecm?.requestActive?'REQ':'OFF';
  return {ownerEntityId:r.entityId,allRadiationSilent:global,masterSilent:master,activeRadarCategories:active,totalRadarCategories:radar.length,ecmCode,
    text:(global?'RF:SIL':'RF:CTL')+' R:'+active+'/'+radar.length+'\nECM:'+ecmCode,
    title:emconUiOwnerLabelB(r)+' · 전파방사통제 '+(global?'ON':'OFF')+' · RADAR MASTER '+(master?'SILENT':'ACTIVE')+' · 활성 레이더 범주 '+active+'/'+radar.length+' · ECM '+(decision?.emissionActive?'TX':decision?.allowed?'허용 · 대기':decision?.ecm?.requestActive?'요청 보존 / 미방출':'OFF')+' · 통신 링크는 별도'};
}
function emconCreatePolicyUiB(){
  const root=document.createElement('section');root.id='mapEmconPolicyB';root.className='map-emcon-policy-b';
  const owner=document.createElement('select');owner.id='mapEmconOwnerB';owner.setAttribute('aria-label','전파방사통제 조작 함정');
  const summary=document.createElement('small');summary.className='map-emcon-summary-b';const categories=document.createElement('div');categories.className='map-emcon-categories-b';
  const linkNote=document.createElement('small');linkNote.className='map-emcon-link-note-b';linkNote.textContent='통신 링크는 별도 정책이며 전파방사통제의 영향을 받지 않음';root.append(owner,summary,categories,linkNote);
  let ownerKey='',registryKey='',rows=new Map();
  owner.addEventListener('change',()=>{fleetSelectG(owner.value);ownerKey='';refresh();});
  function friendlyCommandAllowed(r){return emconUiCommandAllowedB(r);}
  function displayName(entry){return entry.system??entry.nato??entry.id.replaceAll('_',' ');}
  function rebuild(r){
    const registry=shipEmitterRegistryA(r),allowed=friendlyCommandAllowed(r);categories.replaceChildren();rows=new Map();
    for(const category of SHIP_EMITTER_CATEGORIES_A){
      const entries=(registry?.entries??[]).filter(q=>q.category===category),box=document.createElement('section');box.className='map-emcon-category-b';box.dataset.emconCategoryB=category;
      const head=document.createElement('div');head.className='map-emcon-category-head-b';const label=document.createElement('strong');label.textContent=EMCON_B_CATEGORY_LABEL[category]??category;
      const button=document.createElement('button');button.type='button';button.id='mapEmconCategoryB_'+category;button.className='ui-button-a map-emcon-toggle-b';button.disabled=!allowed||entries.length===0;button.addEventListener('click',()=>{emconCategoryToggleB(r.entityId,category,'OPERATOR');refresh();});head.append(label,button);box.append(head);
      const equipment=[];
      if(!entries.length){const empty=document.createElement('small');empty.textContent='등록 장비 없음';empty.dataset.emconEmptyB=category;box.append(empty);}
      for(const entry of entries){
        const line=document.createElement('div');line.className='map-emcon-equipment-b';line.dataset.emconEquipmentB=entry.id;const name=document.createElement('span');name.textContent=displayName(entry);name.title=entry.id;
        const toggle=document.createElement('button');toggle.type='button';toggle.id='mapEmconEquipmentB_'+entry.id.replace(/[^A-Za-z0-9_-]/g,'_');toggle.className='ui-button-a map-emcon-toggle-b';toggle.setAttribute('aria-label',displayName(entry)+' 방사 허용');toggle.addEventListener('click',()=>{emconEquipmentToggleB(r.entityId,entry.id,'OPERATOR');refresh();});
        const status=document.createElement('small');status.className='map-emcon-equipment-state-b';line.append(name,toggle,status);box.append(line);equipment.push({entry,toggle,status});
      }
      categories.append(box);rows.set(category,{button,equipment,entries});
    }
  }
  function refresh(){
    const members=typeof fleetMembersG==='function'?fleetMembersG():[ACTIVE_SHIP_RUNTIME],selected=emconUiOwnerB(),nextOwnerKey=members.map(r=>r.entityId+':'+r.profileId+':'+r.role).join('|');
    if(nextOwnerKey!==ownerKey){owner.replaceChildren();for(const r of members)owner.add(new Option(emconUiOwnerLabelB(r),r.entityId));ownerKey=nextOwnerKey;}owner.value=selected.entityId;
    const registry=shipEmitterRegistryA(selected),nextRegistryKey=selected.entityId+':'+registry?.registryId+':'+(registry?.entries?.map(q=>q.id).join('|')??'');if(nextRegistryKey!==registryKey){rebuild(selected);registryKey=nextRegistryKey;}
    const allowed=friendlyCommandAllowed(selected),global=emconUiAllSilentB(selected);let active=0,total=0;
    for(const [category,row]of rows){
      const decisions=row.entries.map(q=>emconEquipmentDecisionB(selected,q.id)),categoryOn=decisions.some(q=>q.allowed),operational=decisions.some(q=>q.operational);
      row.button.textContent=categoryOn?'ON':'OFF';row.button.setAttribute('aria-pressed',String(categoryOn));row.button.disabled=!allowed||row.entries.length===0||!operational;row.button.classList.toggle('is-active',categoryOn);
      if(EMCON_B_RADAR_CATEGORIES.includes(category)&&row.entries.length){total++;if(categoryOn)active++;}
      for(let i=0;i<row.equipment.length;i++){
        const q=row.equipment[i],decision=decisions[i],on=decision.allowed;q.toggle.textContent=on?'ON':'OFF';q.toggle.setAttribute('aria-pressed',String(on));q.toggle.classList.toggle('is-active',on);q.toggle.disabled=!allowed||!decision.operational;
        const state=category==='ECM'?(decision.emissionActive?'TX':on?'ARMED · 대기':'OFF'):(on?'ON':'OFF');q.status.textContent=state+' · '+(EMCON_B_REASON_LABEL[decision.reason]??decision.reason);if(category==='ECM')q.status.textContent+=' · 기법 '+(decision.ecm?.requestActive?'요청':'없음');
      }
    }
    const ecm=(registry?.entries??[]).find(q=>q.category==='ECM'),ecmDecision=ecm?emconEquipmentDecisionB(selected,ecm.id):null;summary.textContent='전파방사통제 '+(global?'ON':'OFF')+' · RADAR MASTER '+(emconUiMasterSilentB(selected)?'SILENT':'ACTIVE')+' · 레이더 '+active+'/'+total+' · ECM '+(ecmDecision?.emissionActive?'TX':ecmDecision?.allowed?'ARMED · 대기':ecmDecision?.ecm?.requestActive?'요청 보존 / OFF':'OFF');
  }
  function snapshot(){return {ownerEntityId:owner.value,categories:[...rows].map(([category,row])=>({category,pressed:row.button.getAttribute('aria-pressed'),disabled:row.button.disabled,equipment:row.equipment.map(q=>({id:q.entry.id,pressed:q.toggle.getAttribute('aria-pressed'),disabled:q.toggle.disabled,status:q.status.textContent}))}))};}
  if(!document.getElementById('emconBPolicyStyle')){const style=document.createElement('style');style.id='emconBPolicyStyle';style.textContent=`#mapEmconMenuE{box-sizing:border-box;width:min(350px,calc(100vw - 8px));max-width:min(350px,calc(100vw - 8px));max-height:min(76dvh,620px);overflow:auto}#mapAllRadiationE{min-height:42px!important;font-weight:800;border:2px solid #72909d}#mapAllRadiationE.is-active,.map-emcon-toggle-b.is-active{background:#197b65!important;color:#fff!important;border-color:#7fffd4!important}.map-emcon-policy-b{display:flex;flex-direction:column;gap:4px;border-top:1px solid #45606b;border-bottom:1px solid #45606b;padding:4px 0}.map-emcon-policy-b select{box-sizing:border-box;min-height:36px!important;background:#102c3b;color:#e0eef4;border:1px solid #527787;font:11px/1.3 monospace}.map-emcon-categories-b{display:flex;flex-direction:column;gap:3px}.map-emcon-category-b{display:flex;flex-direction:column;gap:2px;padding:3px;border:1px solid #38515b}.map-emcon-category-head-b{display:grid;grid-template-columns:minmax(0,1fr) minmax(72px,auto);align-items:center;gap:4px}.map-emcon-category-head-b button,.map-emcon-equipment-b button{min-height:36px!important}.map-emcon-equipment-b{display:grid;grid-template-columns:minmax(0,1fr) 72px;gap:2px 4px;align-items:center}.map-emcon-equipment-state-b{grid-column:1/-1;color:#a9c6d1!important}.map-emcon-summary-b{color:#9edfff!important}.map-emcon-link-note-b{color:#d8bd80!important}`;document.head.append(style);}
  refresh();return Object.freeze({root,refresh,snapshot});
}
window.__EMCON_B_UI__=Object.freeze({owner:()=>emconUiOwnerB().entityId,chip:emconUiChipSnapshotB,allRadiation:()=>emconAllRadiationMacroB(emconUiOwnerB()),toggleCategory:category=>emconCategoryToggleB(emconUiOwnerB().entityId,category,'OPERATOR'),toggleEquipment:id=>emconEquipmentToggleB(emconUiOwnerB().entityId,id,'OPERATOR'),memory:id=>{const r=ENGAGEMENT_RUNTIME.ships.get(String(id));if(!r)return null;const s=emconStateViewB(r);return s.allRadiationSilent?{allRadiationSilent:true,restoreMasterSilent:s.allRadiationRestoreMasterSilent}:null;}});
