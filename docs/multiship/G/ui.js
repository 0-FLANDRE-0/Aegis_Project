// Display-only controls; commands route explicitly to a friendly owner.
function mountNetworkUiG(){
  if(document.getElementById('networkControlsG'))return;
  const panel=document.getElementById('controlDeckPanel'),tabs=panel?.querySelector('.control-deck-tabs');if(!tabs)return;
  const tab=document.createElement('button');tab.id='modeFleetBtn';tab.className='control-deck-tab';tab.dataset.tab='FLEET';tab.textContent='FLEET';tab.setAttribute('role','tab');tab.setAttribute('aria-controls','controlDeckFleetPage');tab.setAttribute('aria-selected','false');tabs.insertBefore(tab,document.getElementById('modeDebugBtn'));
  const page=document.createElement('div');page.id='controlDeckFleetPage';page.className='control-deck-page';page.dataset.page='FLEET';page.hidden=true;page.setAttribute('role','tabpanel');page.setAttribute('aria-labelledby','modeFleetBtn');
  page.innerHTML=`<section class="control-deck-section"><div class="control-deck-heading">함정 조종</div>
    <div id="fleetSelectedG" role="status"></div><div class="control-deck-grid"><button id="fleetChangeG" class="wep-btn misc">함정 변경</button><button id="fleetViewG" class="wep-btn misc">선택 함정 3D 보기</button></div>
    <label>명령 속력 (kt)<input id="fleetSpeedG" type="number" min="-15" max="31" step="1" value="0"></label>
    <label>명령 타각 (°)<input id="fleetRudderG" type="number" min="-35" max="35" step="1" value="0"></label>
    <div class="control-deck-grid"><button id="fleetNavG" class="wep-btn misc">조종 적용</button><button id="fleetMidshipsG" class="wep-btn misc">타 중앙</button></div><div id="fleetNavStatusG" class="control-deck-note"></div>
    <div class="control-deck-note">속력은 가까운 기관 명령으로 반영<br>FLEET 조작은 선택 함정에 적용<br>NAV · ARM · CIC는 기존 자함 기준</div></section>
    <section class="control-deck-section"><div class="control-deck-heading">선택 함정 교전</div>
    <label>교전 관제<select id="fleetModeG"><option value="MANUAL">수동</option><option value="AUTO">자율 방어</option><option value="SEMIAUTO" hidden>반자동 (자함)</option></select></label>
    <label>현지 레이더 표적<select id="fleetTrackG"><option value="">현지 추적 없음</option></select></label>
    <div class="fleet-identity-row"><select id="fleetIdentityG" aria-label="운용자 식별"><option value="UNKNOWN">미식별</option><option value="HOSTILE">적성</option><option value="FRIEND">아군</option><option value="NEUTRAL">중립</option><option value="TRAINING_TARGET">훈련 표적</option></select><button id="fleetIdentifyG" class="wep-btn misc">식별 적용</button></div>
    <label>무장<select id="fleetWeaponG"><option value="SM2">SM-2MR</option><option value="SM2ER">SM-2ER</option><option value="SM6">SM-6</option><option value="ESSM">ESSM</option><option value="HARPOON">HARPOON</option><option value="GUN">함포</option></select></label>
    <label id="fleetGunLabelG" hidden>함포 선택<select id="fleetGunG"></select></label>
    <div class="control-deck-grid"><button id="fleetFireG" class="wep-btn missile">선택 함정 발사</button><button id="fleetEmconG" class="wep-btn misc">EMCON OFF</button></div>
    <div id="fleetInventoryG" class="control-deck-note"></div><div id="fleetResultG" class="control-deck-note" role="status"></div>
    <div class="control-deck-note">공유 트랙만으로 발사 불가 · 보호 식별 보류<br>하푼은 현지 수상 표적에 수동 발사</div></section>
    <section id="networkControlsG" class="control-deck-section"><div class="control-deck-heading">선택 함정 네트워크</div><div class="control-deck-grid"><button id="networkRadioG" class="wep-btn misc">LINK ON</button><button id="networkShareG" class="wep-btn misc">트랙 공유 ON</button><button id="networkDefenseG" class="wep-btn misc">방어 분담 ON</button></div><label>함대 공동 탐색 레이더<select id="networkEmconG"><option value="INDIVIDUAL">개별 운용</option><option value="ACTIVE">모두 탐색</option><option value="SILENT">모두 침묵</option><option value="PLAYER_SEARCH">자함만 탐색</option><option value="ALLY_SEARCH">아군함만 탐색</option></select></label><div id="networkStatusG" class="control-deck-note" role="status"></div><div class="control-deck-note">공유 정정은 전술 화면용 · 사통은 현지 추적<br>레이더 침묵 중에도 링크 송신 유지</div></section>`;
  panel.append(page);
  const style=document.createElement('style');style.textContent=`.control-deck-tabs{grid-template-columns:repeat(4,minmax(48px,78px))}.control-deck-tab[data-tab="FLEET"].active{color:#9edfff;box-shadow:inset 0 -3px #70bcff}#controlDeckPanel[data-active-tab="FLEET"]{max-height:min(78dvh,450px)}#controlDeckFleetPage.active{grid-template-columns:repeat(3,minmax(0,1fr));max-height:min(60dvh,355px);min-height:0;overflow-y:auto;pointer-events:auto}#controlDeckFleetPage label{display:block;font-size:10px}#controlDeckFleetPage input,#controlDeckFleetPage select{display:block;box-sizing:border-box;width:100%;margin:3px 0;padding:7px;min-height:34px;background:#102c3b;color:#e0eef4;border:1px solid #527787}#controlDeckFleetPage .control-deck-note{overflow-wrap:anywhere;line-height:1.6}#fleetSelectedG{font-size:11px;color:#bcecff}.fleet-identity-row{display:grid;grid-template-columns:1fr 1fr;gap:4px}@media(max-width:640px){.control-deck-tabs{grid-template-columns:repeat(4,minmax(42px,1fr))}#controlDeckFleetPage.active{grid-template-columns:1fr;max-height:calc(100dvh - 135px)}#controlDeckFleetPage input,#controlDeckFleetPage select{min-height:44px}}`;
  page.append(style);
  bindPress(tab,()=>{setControlDeckTabWip13C('FLEET');fleetUpdateUiG(true);});
  const command=c=>{const result=fleetCommandG(fleetOwnerG().entityId,c);if(!result.ok)document.getElementById('fleetResultG').textContent=result.reason;return result;};
  const number=id=>Number(document.getElementById(id).value),track=()=>number('fleetTrackG');
  bindPress(document.getElementById('fleetChangeG'),()=>{const members=fleetMembersG(),idx=members.findIndex(r=>r===fleetOwnerG());fleetSelectG(members[(idx+1)%members.length].entityId);});
  bindPress(document.getElementById('fleetViewG'),()=>fleetViewG());
  bindPress(document.getElementById('fleetNavG'),()=>command({action:'NAV',speedKt:number('fleetSpeedG'),rudderDeg:number('fleetRudderG')}));
  bindPress(document.getElementById('fleetMidshipsG'),()=>{document.getElementById('fleetRudderG').value='0';command({action:'NAV',speedKt:number('fleetSpeedG'),rudderDeg:0});});
  document.getElementById('fleetModeG').addEventListener('change',e=>command({action:'MODE',mode:e.target.value}));
  document.getElementById('fleetTrackG').addEventListener('change',()=>command({action:'TRACK',trackId:track()}));
  bindPress(document.getElementById('fleetIdentifyG'),()=>command({action:'IDENTITY',trackId:track(),identity:document.getElementById('fleetIdentityG').value}));
  document.getElementById('fleetWeaponG').addEventListener('change',()=>fleetUpdateUiG(true));
  bindPress(document.getElementById('fleetFireG'),()=>command({action:'FIRE',trackId:track(),weapon:document.getElementById('fleetWeaponG').value,...(document.getElementById('fleetWeaponG').value==='GUN'?{mountId:document.getElementById('fleetGunG').value}:{})}));
  bindPress(document.getElementById('fleetEmconG'),()=>{const r=fleetOwnerG();command({action:'EMCON',enabled:!(r===ACTIVE_SHIP_RUNTIME?emconActive:observerC(r).emcon)});});
  for(const [id,key]of [['networkRadioG','enabled'],['networkShareG','shareTracks'],['networkDefenseG','cooperativeDefense']])bindPress(document.getElementById(id),()=>{const r=fleetOwnerG(),s=networkSettingsG(r);networkCommandG(r.entityId,{[key]:!s[key]});});
  document.getElementById('networkEmconG').addEventListener('change',e=>networkCommandG(ACTIVE_SHIP_RUNTIME.entityId,{groupEmcon:e.target.value}));networkUpdateUiG();
}
function fleetUpdateUiG(force=false){
  const page=document.getElementById('controlDeckFleetPage');if(!page)return;
  if(!force&&performance.now()-(page._lastUiG??0)<250)return;page._lastUiG=performance.now();
  const snapshot=fleetSnapshotG(),q=snapshot.ships.find(r=>r.entityId===snapshot.selectedShipId),changed=page.dataset.owner!==q.entityId;page.dataset.owner=q.entityId;
  document.getElementById('fleetSelectedG').textContent=q.label;document.getElementById('fleetChangeG').disabled=snapshot.ships.length<2;
  if(changed||force){document.getElementById('fleetSpeedG').value=String(q.speedKt);document.getElementById('fleetRudderG').value=String(q.rudderDeg);}
  document.getElementById('fleetSpeedG').max=String(shipAheadLimitB(resolveShipProfile(fleetOwnerG().profileId)));
  document.getElementById('fleetNavStatusG').textContent=q.headingDeg.toFixed(0)+'° · '+q.currentSpeedKt.toFixed(1)+' kt';
  document.getElementById('fleetModeG').value=q.mode;document.getElementById('fleetEmconG').textContent='EMCON '+(q.emcon?'ON':'OFF');
  const sel=document.getElementById('fleetTrackG'),key=JSON.stringify(q.tracks.map(t=>[t.id,t.identity,t.classification]));
  if(changed||sel.dataset.key!==key){sel.replaceChildren(new window.Option('현지 표적 선택',''));for(const t of q.tracks)sel.add(new window.Option('T'+t.id+' '+t.classification+' · '+t.identity,String(t.id)));sel.dataset.key=key;}
  sel.value=q.tracks.some(t=>t.id===q.selectedTrackId)?String(q.selectedTrackId):'';
  const guns=document.getElementById('fleetGunG');if(changed||guns.dataset.key!==JSON.stringify(q.guns)){guns.replaceChildren();for(const g of q.guns)guns.add(new window.Option(g.label,g.id));guns.dataset.key=JSON.stringify(q.guns);}
  const weapon=document.getElementById('fleetWeaponG');for(const option of weapon.options)option.disabled=option.value==='GUN'?!q.guns.length:!(q.inventory[option.value]>0);
  if(weapon.selectedOptions[0]?.disabled)weapon.value=[...weapon.options].find(o=>!o.disabled)?.value??'GUN';
  document.getElementById('fleetGunLabelG').hidden=weapon.value!=='GUN';document.getElementById('fleetFireG').disabled=sel.value===''||q.mode!=='MANUAL'||weapon.selectedOptions[0]?.disabled;
  document.getElementById('fleetInventoryG').textContent=Object.entries(q.inventory).map(([k,v])=>k+' '+v).join(' · ');document.getElementById('fleetResultG').textContent=q.lastResult;
}
function networkUpdateUiG(){
  const root=document.getElementById('networkControlsG');if(!root||!ACTIVE_SHIP_RUNTIME?.combatSystem)return;
  const r=fleetOwnerG(),n=prepareNetworkG(r),s=n.settings,peers=networkConnectedPeersG(r),now=networkNowG();
  for(const [id,key,label]of [['networkRadioG','enabled','LINK'],['networkShareG','shareTracks','트랙 공유'],['networkDefenseG','cooperativeDefense','방어 분담']]){const b=document.getElementById(id);b.textContent=label+' '+(s[key]?'ON':'OFF');b.setAttribute('aria-pressed',String(s[key]));}
  const group=networkSettingsG(ACTIVE_SHIP_RUNTIME).groupEmcon;document.getElementById('networkEmconG').value=group;
  const shared=[...n.files.values()].filter(f=>![...f.sources.values()].every(q=>q.kind==='SELF')).length,assigned=[...n.leases.values()].filter(q=>q.untilS>=now).length,
    state=!s.enabled?'송수신 OFF':fleetMembersG().length<2?'아군함 없음':peers.length?'연결':'연결 대기 / 단절';
  document.getElementById('networkStatusG').textContent='LINK '+state+' · 공유 '+shared+' · 분담 '+assigned+(group!=='INDIVIDUAL'&&!peers.length?' · 개별 레이더로 복귀':'');fleetUpdateUiG();
}
function networkTrackLabelG(tr){if(!tr)return '';const n=ACTIVE_SHIP_RUNTIME.combatSystem.networkG,file=n&&[...n.files.values()].find(f=>f.localTrackId===tr.trackId);if(!file)return '';const lease=n.leases.get(tr.trackId);return ' NET 정정'+(lease&&lease.untilS>=networkNowG()?(lease.primary===ACTIVE_SHIP_RUNTIME.entityId?' · 자함 담당':' · 아군 담당'):'');}
function drawNetworkPictureG(){
  const r=ACTIVE_SHIP_RUNTIME,n=r.combatSystem.networkG;if(!n)return;const now=networkNowG();
  ctx.save();ctx.font=`${tacticalFontWorldSize(8,5)}px monospace`;ctx.lineWidth=tacticalLineWidthWorld(1.1,.45);ctx.textAlign='left';
  for(const q of networkPictureG(r)){
    if(q.localTrackId!==null||!q.positionM)continue;const x=metersToWorld(q.positionM.x),y=metersToWorld(q.positionM.y),friend=q.identity==='FRIEND',color=q.coasting?'rgba(145,165,180,.55)':friend?'rgba(90,220,245,.86)':'rgba(170,165,255,.86)',size=tacticalWorldPx(5,10,3,10);
    ctx.strokeStyle=color;ctx.fillStyle=color;ctx.setLineDash(q.coasting?[3,4]:[4,2]);ctx.strokeRect(x-size,y-size,size*2,size*2);ctx.setLineDash([]);
    const label=(friend?'ALLY':'NET '+q.id)+' '+q.ageS.toFixed(1)+'s'+(q.coasting?' COAST':' · 공유만');ctx.fillText(label,x+size+2,y-size-2);
    if(q.covariance){const rx=metersToWorld(2*Math.sqrt(q.covariance[0])),ry=metersToWorld(2*Math.sqrt(q.covariance[7]));if(rx>1&&ry>1){ctx.globalAlpha=.25;ctx.beginPath();ctx.ellipse(x,y,rx,ry,0,0,TAU);ctx.stroke();ctx.globalAlpha=1;}}
  }ctx.restore();
}
