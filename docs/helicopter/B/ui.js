// AIR selection is UI state. Only explicit launch/queue/map commands write helo state.
const heloUiA={selectedId:null,lastUiMs:-Infinity,lastResult:''};
const HELO_LABELS_A=Object.freeze({HANGARED:'격납',QUEUED:'출격 대기',HANGAR_OPEN:'문 개방',TRAVERSE:'갑판 이동',SPREAD:'기체 전개',START:'시동',PRE_LAUNCH_CHECK:'출격 전 확인',LIFT_HOVER:'부상·호버',DEPART:'좌현 이탈·상승',TRANSIT:'이동',ARRIVED_HOVER:'목표 호버',RECOVERY:'회수 대기',LOST:'운용 불가'});
function heloSelectA(id){if(!heloInventoryA().some(q=>q.id===id))return false;heloUiA.selectedId=id;heloUiA.lastResult='지도에서 이동 위치를 누르세요';heloUpdateUiA(true);return true;}
function heloMapTapA(x,y){if(controlDeckActiveTabWip13C!=='AIR'||!heloUiA.selectedId)return;const r=heloCommandA(heloUiA.selectedId,'WAYPOINT',{x:worldToMeters(x),y:worldToMeters(y)});heloUiA.lastResult=r.ok?'이동 위치 지정 · 고도 50m':r.reason;heloUpdateUiA(true);}
function heloMountUiA(){
  const panel=document.getElementById('controlDeckPanel'),tabs=panel?.querySelector('.control-deck-tabs');if(!tabs||document.getElementById('modeAirBtn'))return;
  heloEnsureA();const tab=document.createElement('button');tab.id='modeAirBtn';tab.className='control-deck-tab';tab.dataset.tab='AIR';tab.textContent='AIR';tab.setAttribute('role','tab');tab.setAttribute('aria-controls','controlDeckAirPage');tab.setAttribute('aria-selected','false');tabs.insertBefore(tab,document.getElementById('modeDebugBtn'));
  const page=document.createElement('div');page.id='controlDeckAirPage';page.className='control-deck-page';page.dataset.page='AIR';page.hidden=true;page.setAttribute('role','tabpanel');page.setAttribute('aria-labelledby','modeAirBtn');
  page.innerHTML=`<section class="control-deck-section"><div class="control-deck-heading">항공 운용 · MH-60R</div><div id="airAircraftA"></div></section>
    <section class="control-deck-section"><div id="airSelectionA" class="control-deck-heading">기체 선택</div><div class="control-deck-grid"><button id="airLaunchA" class="wep-btn misc">이륙 요청</button><button id="airCancelA" class="wep-btn misc">대기열 취소</button><button id="airViewA" class="wep-btn misc">헬기 보기</button><button id="airShipViewA" class="wep-btn misc">모함 보기</button></div><div id="airQueueA" role="status" class="control-deck-note"></div><div id="airResultA" role="status" class="control-deck-note"></div><div class="control-deck-note">기체를 선택하고 지도에서 이동 위치 지정<br>비행 고도 50m · 갑판은 한 기씩 사용</div></section>`;
  panel.append(page);const style=document.createElement('style');style.textContent=`.control-deck-tabs{grid-template-columns:repeat(5,minmax(42px,78px))}#controlDeckAirPage.active{grid-template-columns:1.4fr 1fr;max-height:min(65dvh,370px);overflow-y:auto;min-height:0;pointer-events:auto}#airAircraftA{display:grid;gap:5px}.air-aircraft-a{padding:9px;text-align:left;line-height:1.6;background:#102c3b;border:1px solid #527787;border-radius:5px;color:#d8ecf5;font:11px monospace;white-space:pre-line;min-height:44px}.air-aircraft-a[aria-pressed="true"]{border-color:#83dce9;background:#164454}.control-deck-tab[data-tab="AIR"].active{color:#8ee6da;box-shadow:inset 0 -3px #70d8c4}#controlDeckPanel[data-active-tab="AIR"]{max-height:78dvh}@media(max-width:640px){.control-deck-tabs{grid-template-columns:repeat(5,minmax(38px,1fr))}#controlDeckAirPage.active{grid-template-columns:1fr;max-height:calc(100dvh - 135px)}#controlDeckAirPage button{min-height:44px}}`;page.append(style);
  for(const q of heloInventoryA()){const b=document.createElement('button');b.id='airHeloA'+q.slot;b.className='air-aircraft-a';b.dataset.heloId=q.id;b.setAttribute('aria-pressed','false');b.setAttribute('aria-label','H'+(q.slot+1)+' '+(q.slot===0?'좌현':'우현')+' 격납고 헬기 선택');bindPress(b,()=>heloSelectA(q.id));page.querySelector('#airAircraftA').append(b);}
  bindPress(tab,()=>{setControlDeckTabWip13C('AIR');heloUpdateUiA(true);});
  const command=action=>{const r=heloCommandA(heloUiA.selectedId,action);heloUiA.lastResult=r.ok?(action==='LAUNCH'?'출격 대기열 등록':'대기열 취소'):r.reason;heloUpdateUiA(true);};
  bindPress(document.getElementById('airLaunchA'),()=>command('LAUNCH'));bindPress(document.getElementById('airCancelA'),()=>command('CANCEL_QUEUE'));
  bindPress(document.getElementById('airViewA'),async()=>{const view=WIP148_EXTERNAL_3D;await view.open();if(!view.active||!view.ready)return;view.heloFocusA=heloUiA.selectedId;view.follow.enabled=false;view.surfaceFocus.enabled=false;view.navalFocusB=null;view.orbit.distance=42;});
  bindPress(document.getElementById('airShipViewA'),()=>{WIP148_EXTERNAL_3D.heloFocusA=null;WIP148_EXTERNAL_3D.resetCamera();});heloUpdateUiA(true);
}
function heloUpdateUiA(force=false){
  if(!document.getElementById('controlDeckAirPage'))return;if(!force&&performance.now()-heloUiA.lastUiMs<250)return;heloUiA.lastUiMs=performance.now();
  const s=heloSnapshotA(),selected=s.aircraft.find(h=>h.id===heloUiA.selectedId),host=document.getElementById('airAircraftA');
  if(!s.supported){host.textContent='이번 항공 운용은 DDG-119에서 사용할 수 있어요.';}
  for(const h of s.aircraft){const b=document.getElementById('airHeloA'+h.slot);if(!b)continue;b.setAttribute('aria-pressed',String(h===selected));
    const distance=h.distanceM==null?'목표 없음':`${(h.distanceM/1000).toFixed(2)}km · ETA≈${Math.ceil(h.etaS)}s`,phase=h.remainingS==null?'':` · ${Math.ceil(h.remainingS)}s`;
    b.textContent=`H${h.slot+1} · ${h.slot===0?'좌현':'우현'} · ${HELO_LABELS_A[h.state]}${phase}\n대기 ${h.airSpeedKt.toFixed(0)}kt · 대지 ${h.groundSpeedKt.toFixed(0)}kt · ${h.altitudeM.toFixed(0)}m · ${h.headingDeg.toFixed(0)}°\n${distance}`;
  }
  document.getElementById('airSelectionA').textContent=selected?`H${selected.slot+1} · ${HELO_LABELS_A[selected.state]}`:'기체 선택';
  document.getElementById('airLaunchA').disabled=!selected||selected.state!=='HANGARED'||wip125PreSailOpen;
  document.getElementById('airCancelA').disabled=!selected||selected.state!=='QUEUED';document.getElementById('airViewA').disabled=!selected;
  document.getElementById('airQueueA').textContent=(s.deckOwnerId?'갑판 사용 H'+(s.aircraft.find(h=>h.id===s.deckOwnerId)?.slot+1):'갑판 비어 있음')+' · 대기 '+(s.queue.map(id=>'H'+(s.aircraft.find(h=>h.id===id)?.slot+1)).join(' → ')||'없음')+(s.holdReason?' · '+s.holdReason:'');
  document.getElementById('airResultA').textContent=heloUiA.lastResult;
}
function heloDrawMapA(){
  if(!heloSupportedA())return;ctx.save();ctx.strokeStyle='#7ae6da';ctx.fillStyle='#a9fff2';ctx.lineWidth=tacticalLineWidthWorld(1,.5);ctx.font=`${tacticalFontWorldSize(10,6)}px monospace`;
  for(const h of ENGAGEMENT_RUNTIME.world.entities.helicopters?.values()??[]){
    if(!h.visible&&h.id!==heloUiA.selectedId)continue;const x=metersToWorld(h.positionM.x),y=metersToWorld(h.positionM.y),r=tacticalWorldPx(6,12,3,12);
    if(h.waypointM){const tx=metersToWorld(h.waypointM.x),ty=metersToWorld(h.waypointM.y);ctx.globalAlpha=.55;ctx.setLineDash([r,r]);ctx.beginPath();ctx.moveTo(x,y);ctx.lineTo(tx,ty);ctx.stroke();ctx.setLineDash([]);ctx.globalAlpha=1;ctx.strokeRect(tx-r,ty-r,r*2,r*2);ctx.fillText('H'+(h.slot+1)+' WP',tx+r*1.5,ty);}
    ctx.save();ctx.translate(x,y);ctx.rotate(h.headingRad);ctx.beginPath();ctx.moveTo(r*1.5,0);ctx.lineTo(-r,r*.75);ctx.lineTo(-r,-r*.75);ctx.closePath();ctx.stroke();ctx.beginPath();ctx.arc(0,0,r*.65,0,2*Math.PI);ctx.stroke();ctx.restore();ctx.fillText('H'+(h.slot+1)+' '+HELO_LABELS_A[h.state],x+r*1.8,y-r);
  }ctx.restore();
}
function heloRenderStateA(){
  const l=ACTIVE_SHIP_RUNTIME.aviation.heloLaunchA,world=ENGAGEMENT_RUNTIME.world.entities.helicopters;if(!heloSupportedA()||!l||!world)return {supported:false,doors:[],aircraft:[]};return {supported:true,doors:[...l.doors],aircraft:[...world.values()].filter(h=>h.visible).map(h=>({id:h.id,slot:h.slot,state:h.state,onboard:h.onboard,localM:{...h.localM},positionM:{...h.positionM},headingRad:h.headingRad,pitchRad:h.pitchRad,bankRad:h.bankRad,tail01:h.tail01,blades01:h.blades01,rotor01:h.rotor01,rotorAngleRad:h.rotorAngleRad}))};
}
