// MAP_D: operator input adapter. No target truth, missile flight feedback or new firing model.
window.__MAP_D__=(()=>{
 const handles=w=>w==='HARPOON'||w==='MK45',ammoNames={HE_127_SIM:'HE',SAP_127_SIM:'SAP'};
 let mounted=false,dom={},menuCommit=null,menuWeapon=null,menuAmmo=null,hpQueue=null,gunOps=[],ownedCues=new Map(),lastOwner=null,lastEpoch=null,lastStep=-1,serial=0;
 const log=[],metrics={cue:0,preview:0,hpRequests:0,hpReleased:0,gunRequests:0,continuousStarts:0,continuousStops:0};
 const note=(action,reason,extra={})=>{log.push({step:simStepCounter,action,reason,...extra});if(log.length>64)log.shift();};
 const scale=()=>window.__UI_A_SETTINGS__?.scale??1;
 const own=()=>ACTIVE_SHIP_RUNTIME.entityId;
 const selection=()=>window.__MAP_B__?.snapshot().selection;
 const guns=()=>ACTIVE_SHIP_RUNTIME.weapons.gunMounts?[...ACTIVE_SHIP_RUNTIME.weapons.gunMounts].map(([id,g])=>({id,g})):ACTIVE_SHIP_RUNTIME.weapons.mainGun?[{id:ACTIVE_SHIP_PROFILE.weapons.mainGun.id??ACTIVE_SHIP_PROFILE.weapons.mainGun.hardpointId??'MAIN',g:ACTIVE_SHIP_RUNTIME.weapons.mainGun}]:[];
 const isSurface=o=>o?.classification==='SURFACE'||o?.domain==='SURFACE';
 const trackId=o=>o?.kind==='TRACK'?Number(o.id):o?.associatedTrackId==null?null:Number(o.associatedTrackId);
 const reasonNames={NO_TRACK:'트랙 없음',NOT_SURFACE_TRACK:'수상 표적 전용',SURFACE_IDENTITY_NOT_AUTHORIZED:'식별 권한 없음',PROTECTED_IDENTITY:'아군·중립 표적 보호',MANUAL_SURFACE_AUTHORITY_REQUIRED:'수동 교전 권한 필요',AUTOMATIC_SURFACE_ENGAGEMENT_PROHIBITED:'자동 수상 교전 금지',SURFACE_TRACK_COAST_EXPIRED:'트랙 노후',SURFACE_TRACK_NOT_CONFIRMED:'수상 트랙 미확정',SURFACE_TRACK_STATE_UNAVAILABLE:'트랙 상태 부족',TRACK_SUPPORT_BLOCKED:'트랙 지원 중지',SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE:'사거리 조건 미충족',INS_PREDICTION_BASKET_INSUFFICIENT:'INS 예측 범위 초과',TUBE_EMPTY:'탄 없음',MK141_NOT_INSTALLED:'하푼 미장착',MK141_LAUNCHER_DAMAGED:'발사기 손상',RELEASE_PENDING:'발사관 개방 중',LAUNCHER_COOLDOWN:'발사 간격 대기',SHIP_EQUIPMENT_OFFLINE:'함 장비 운용 불가',LAUNCH_GEOMETRY_UNSAFE:'발사 자세 불안전',INVALID_WAYPOINT_ROUTE:'경로 조건 미충족',ROUTE_EXCEEDS_140KM_BUDGET:'경로 사거리 초과',NOT_EDITING:'경로 편집 필요',WAYPOINT_LIMIT:'경유점 한도',WAYPOINT_TOO_CLOSE:'경유점 간격 부족',INVALID_COORDINATE:'좌표 오류',MOUNT_ENVELOPE:'포 사계 밖',MOUNT_OCCLUDED:'함 구조물 차폐',TERRAIN_MASKED:'지형 차폐',GUN_OFFLINE:'함포 운용 불가',FIRE_CONTROL_TRACK_QUALITY_INSUFFICIENT:'사통 품질 부족',SURFACE_TRACK_NOT_READY:'수상 트랙 준비 안 됨',TRACK_NOT_READY:'트랙 준비 안 됨',FEED_CYCLING:'급탄 중',MAGAZINE_EMPTY:'포탄 없음',UNKNOWN_AMMUNITION:'지원하지 않는 탄종',CURRENT_SOLUTION_REQUIRED:'사격해 필요',STALE_FIRING_SOLUTION:'사격해 노후',NO_FIRING_SOLUTION:'사격해 없음',PREVIEW_UNAVAILABLE:'관문 확인 불가'};
 const textReason=code=>reasonNames[code]??String(code??'');
 function scope(){const id=own(),epoch=ENGAGEMENT_RUNTIME.world.presentationEpoch??0;if(lastOwner!==id||lastEpoch!==epoch||simStepCounter<lastStep){hpQueue=null;gunOps=[];ownedCues.clear();}lastOwner=id;lastEpoch=epoch;lastStep=simStepCounter;}
 function ready(w){if(w==='HARPOON')return harpoonRuntimeA().tubes.filter(t=>t.loaded).length;if(w==='MK45')return guns().reduce((n,{g})=>n+Object.values(g.snapshot().magazine).reduce((a,b)=>a+b,0),0);return null;}
 function clearOwned(reason='FIRE_CONTROL_CLEARED'){
  for(const[id,c]of ownedCues){if(c.owner!==own())continue;const q=c.g.snapshot();if(q.commandTrackId===c.trackId)c.g.clear();else if(q.continuousFire.active&&q.continuousFire.trackId===c.trackId)c.g.stopContinuousFire(reason);}
  ownedCues.clear();gunOps=gunOps.filter(q=>q.owner!==own());
 }
 function selectionChanging(prev,next){if(prev?.weapon==='MK45'&&(next?.weapon!=='MK45'||next?.fireMode!==prev.fireMode))clearOwned('OPERATOR_STOP');}
 function cancelled(s){if(s?.weapon==='MK45')clearOwned('OPERATOR_STOP');}
 function cue(o){
  clearOwned('FIRE_CONTROL_COMMAND_CHANGED');const id=trackId(o),tr=id==null?null:mapBObservedTrack(id);if(!isSurface(tr))return;
  for(const{id:key,g}of guns()){const a=g.snapshot().loadedAmmoId,q=g.command(id,a);ownedCues.set(key,{g,owner:own(),trackId:id});metrics.cue++;note('GUN_CUE',q.reason??null,{mount:key,trackId:id,ok:!!q.ok});}
 }
 function chosen(s,t,o){scope();if(s?.weapon==='MK45')cue(o);}
 function applyGunAmmo(ammoId){
  // Try a known rejecting feed first, so one cycling CG feed does not partially
  // switch the other gun. The original selectAmmo decides every outcome.
  const rows=guns().sort((a,b)=>Number(!b.g.spec.ammunition[ammoId])-Number(!a.g.spec.ammunition[ammoId])||b.g.snapshot().cycleRemainingS-a.g.snapshot().cycleRemainingS);
  for(const{id,g}of rows){const q=g.selectAmmo(ammoId);if(!q.ok){note('AMMO_REJECT',q.reason,{mount:id});return q;}}
  const s=selection(),key=window.__MAP_B__?.snapshot().target?.key,o=key?mapObservedObjectsA().find(o=>o.key===key):null;if(s?.weapon==='MK45'&&o)cue(o);return {ok:true,ammoId};
 }
 function menu(w,anchor,commit){
  if(!handles(w))return false;menuWeapon=w;menuCommit=commit;const e=dom.chooser??document.getElementById('mapSalvoB');e.replaceChildren();e.classList.toggle('map-gun-menu-d',w==='MK45');
  const add=(label,attrs,fn,disabled=false)=>{const b=document.createElement('button');b.textContent=label;for(const[k,v]of Object.entries(attrs))b.dataset[k]=v;b.disabled=disabled;b.addEventListener('click',fn);e.append(b);return b;};
  if(w==='HARPOON')for(let n=1;n<=4;n++)add(n+'발',{salvoB:String(n)},()=>{if(ready(w)<n)return;menuCommit({weapon:w,count:n});},ready(w)<n);
  else{
   menuAmmo=ACTIVE_SHIP_RUNTIME.weapons.mainGun.snapshot().loadedAmmoId;
   for(const[id,label]of Object.entries(ammoNames))add(label,{ammoD:id},()=>{const q=applyGunAmmo(id);dom.menuReason.textContent=q.ok?'':textReason(q.reason);if(q.ok){menuAmmo=id;for(const b of e.querySelectorAll('[data-ammo-d]'))b.setAttribute('aria-pressed',String(b.dataset.ammoD===id));window.__MAP_B__.refresh(true);}}).setAttribute('aria-pressed',String(menuAmmo===id));
   for(const[mode,label]of [['SINGLE','단발'],['CONTINUOUS','연속']])add(label,{gunModeD:mode},()=>{menuCommit({weapon:w,count:1,ammoId:menuAmmo,fireMode:mode});});
   const r=document.createElement('small');r.className='map-menu-reason-d';e.append(r);dom.menuReason=r;
  }
  e.hidden=false;place(e,anchor.getBoundingClientRect());return true;
 }
 function place(e,a){const r=WIP148_EXTERNAL_3D.active?AEGIS_VIEWPORT.threeD:AEGIS_VIEWPORT.twoD,s=scale(),b=e.getBoundingClientRect();e.style.left=Math.max(r.x+3,Math.min(r.x+r.w-b.width-3,a.left))/s+'px';e.style.top=Math.max(r.y+3,Math.min(r.y+r.h-b.height-3,a.top-b.height-8))/s+'px';}
 function highlight(s){const h=document.querySelector('[data-weapon-b="HARPOON"]');if(h)h.querySelector('span').textContent='RGM-84';const e=document.querySelector('[data-weapon-b="MK45"]');if(e){e.querySelector('span').textContent='5in';e.title='Mk45'+(s?.weapon==='MK45'?' · '+(s.fireMode==='CONTINUOUS'?'연속':'단발'):' · 탄종/사격 방식');}}
 function gunAssessment(o){
  const id=trackId(o),tr=id==null?null:mapBObservedTrack(id),bad=reason=>({ok:false,allowed:false,tone:'blocked',reason,verdict:'사격 제한',rows:[],mountLabel:IS_BUNKER?'사계 없음':'1문'});
  if(!o||o.lost)return bad(o?.lost?'트랙 소실':'NO_TRACK');if(o.kind==='ESM'||id==null)return bad('NO_TRACK');if(!isSurface(tr))return bad('NOT_SURFACE_TRACK');
  const rows=guns().map(({id:key,g})=>{const q=g.snapshot(),sol=q.solution,desired=sol?.ok?shipGameAimWorldV1(sol.bodyAzRad,sol.bodyElevationRad):null,full=sol?.ok?{...sol,azimuthRad:desired.az,elevationRad:desired.el}:sol;
   const clearance=sol?.ok?(IS_BUNKER?bunkerGunClearance(g.spec,sol.bodyAzRad,sol.bodyElevationRad,Math.min(300,sol.rangeM)):wip13b1GunClearance(g.spec,sol.bodyAzRad,sol.bodyElevationRad,Math.min(300,sol.rangeM))):{ok:false,reason:sol?.reason??'CURRENT_SOLUTION_REQUIRED'};
   const cued=q.commandTrackId===id&&!!sol?.ok,eligible=cued&&clearance.ok,gate=eligible?g.releaseGate(id,full,{mode:'MANUAL'}):{ok:false,reason:clearance.reason},fcq=sol?.fireControlTrackQuality;
   return{id:key,g,q,eligible,clearance,gate,fcq,refusal:!gate.ok?gate.reason:(q.magazine[q.loadedAmmoId]??0)<=0?'MAGAZINE_EMPTY':q.cycleRemainingS>1e-9?'FEED_CYCLING':null,canFire:eligible&&gate.ok&&(q.magazine[q.loadedAmmoId]??0)>0&&q.cycleRemainingS<=1e-9,forward:g.installation.hardpointId===ACTIVE_SHIP_PROFILE.weapons.mainGun.hardpointId};});
  const eligible=rows.filter(r=>r.eligible),allowed=rows.some(r=>r.canFire),qualityReady=eligible.filter(r=>r.gate.ok),tone=!allowed?'blocked':qualityReady.some(r=>r.canFire&&r.fcq?.status==='FCQ_READY')?'effective':'warning',reason=allowed?null:rows.find(r=>r.eligible)?.refusal??rows[0]?.refusal??'NO_FIRING_SOLUTION';
  return {ok:allowed,allowed,tone,reason,verdict:allowed?(tone==='effective'?'사통 준비':'사통 저하'):'사격 제한',rows,mountLabel:!IS_BUNKER?'1문':eligible.length===2?'2문':eligible.length===1?(eligible[0].forward?'함수만':'함미만'):'사계 없음'};
 }
 function calculate(s,t,o){
  if(!handles(s?.weapon))return null;scope();const id=trackId(o),tr=id==null?null:mapBObservedTrack(id),d={o:o??t?.last??null,id,tr,lost:!!o?.lost,rangeKm:o&&Number.isFinite(o.x)?horizDistKm(aircraft.x(),aircraft.y(),o.x,o.y):null};
  if(s.weapon==='HARPOON'){
   const draft=harpoonRuntimeA().routeDraft,frozen=hpQueue?.routeProgram,path=draft.pointsM.length>0||!!frozen;
   if(!path&&(!o||o.lost||o.kind==='ESM'||!tr)){const reason=o?.lost?'트랙 소실':o?.kind==='ESM'?'위치 정보 없음':'NO_TRACK';return {d,initial:!o,allowed:false,tone:'blocked',verdict:'발사 제한',reason,path:false};}
   if(!path&&!isSurface(tr))return {d,allowed:false,tone:'blocked',verdict:'발사 제한',reason:'NOT_SURFACE_TRACK',path:false};
   const gate=mapDHarpoonPreview(id,{mode:engagementControlMode,...(frozen?{routeProgram:frozen}:{})});metrics.preview++;return {d,gate,allowed:!!gate.ok,tone:gate.ok?'effective':'blocked',verdict:gate.ok?'유효':'발사 제한',reason:gate.reason??null,path,initial:!o,rangeKm:gate.rangeKm};
  }
  const a=gunAssessment(o),pending=a.rows.filter(r=>r.q.pendingSingleFire.active&&r.q.pendingSingleFire.trackId===id),continuous=a.rows.filter(r=>r.q.continuousFire.active&&r.q.continuousFire.trackId===id),queued=gunOps.some(q=>q.owner===own());
  const canCancel=pending.length>0||continuous.length>0||queued,cycle=a.rows.filter(r=>r.eligible).map(r=>r.q.cycleRemainingS),cycleS=cycle.length?Math.min(...cycle):0;
  return {...a,d,initial:!o,allowed:a.allowed||canCancel,pending,continuous,queued,cycleS,holdS:pending.length?Math.max(...pending.map(r=>r.q.pendingSingleFire.remainingS)):0,timeOfFlightS:a.rows.find(r=>r.eligible)?.q.solution?.timeOfFlightS??null};
 }
 function routeToggle(){if(inputMode!=='AIM')document.getElementById('modeAimBtn').click();const value=harpoonRouteToggleE();note('ROUTE_TOGGLE',null,{editing:value});window.__MAP_B__.refresh(true);window.__PIP_A__?.invalidate();return value;}
 function appendSearchPoint(xM,yM){if(inputMode!=='AIM')document.getElementById('modeAimBtn').click();if(!harpoonRuntimeA().routeDraft.editing)harpoonRouteToggleE();const q=harpoonRouteAddE(metersToWorld(xM),metersToWorld(yM));window.__MAP_B__.refresh(true);window.__PIP_A__?.invalidate();return q;}
 function fireClick(s,t,m){
  if(!handles(s?.weapon))return false;scope();if(s.weapon==='HARPOON'){
   if(hpQueue||!m?.allowed)return true;const points=harpoonRuntimeA().routeDraft.pointsM,program=points.length?harpoonRouteProgramE(points,{x:worldToMeters(aircraft.x()),y:worldToMeters(aircraft.y())}):null;if(points.length&&!program){note('HARPOON_REJECT','INVALID_WAYPOINT_ROUTE');return true;}
   hpQueue={id:++serial,owner:own(),count:s.count,remaining:s.count,released:0,trackId:m.d?.id??null,routeProgram:program,awaiting:null,createdStep:simStepCounter};note('HARPOON_QUEUE',null,{count:s.count,trackId:hpQueue.trackId,path:!!program});
  }else{
   if(gunOps.some(q=>q.owner===own())){gunOps=[];note('GUN_QUEUE_CANCEL','OPERATOR_CANCEL');return true;}
   if(!m?.allowed)return true;gunOps.push({owner:own(),trackId:m.d.id,mode:s.fireMode,action:m.continuous?.length?'STOP':m.pending?.length?'CANCEL':'FIRE',createdStep:simStepCounter});note('GUN_QUEUE',null,{trackId:m.d.id});
  }window.__MAP_B__.refresh(true);return true;
 }
 function finishHp(reason){if(!hpQueue)return;note(reason?'HARPOON_STOP':'HARPOON_COMPLETE',reason,{released:hpQueue.released,remaining:hpQueue.remaining,id:hpQueue.id});hpQueue=null;}
 function observeHp(){if(!hpQueue?.awaiting)return;const q=hpQueue,r=harpoonRuntimeA();if(r.pending)return;const found=r.launches.find(x=>x.id!==q.awaiting.previousId&&x.tubeId===q.awaiting.tubeId&&x.releaseStep>=q.awaiting.step);if(found){q.released++;q.remaining--;metrics.hpReleased++;note('HARPOON_RELEASED',null,{id:q.id,launchId:found.id,tubeId:found.tubeId,trackId:found.memory?.trackId??null});q.awaiting=null;if(q.remaining<=0)finishHp(null);}else finishHp(r.lastResult?.replace(/^CANCELLED:/,'')??'RELEASE_CANCELLED');}
 function step(){
  scope();observeHp();if(hpQueue&&!hpQueue.awaiting){const r=harpoonRuntimeA();if(!r.pending&&r.releaseCooldownS<=0){const q=hpQueue,options={mode:engagementControlMode,...(q.routeProgram?{routeProgram:q.routeProgram}:{})},result=harpoonRequestFireA(q.trackId,null,options);metrics.hpRequests++;note('HARPOON_REQUEST',result.reason??null,{id:q.id,ok:!!result.ok,tubeId:result.tubeId});if(result.ok)q.awaiting={tubeId:result.tubeId,previousId:r.launches.at(-1)?.id??null,step:simStepCounter};else finishHp(result.reason);}}
  const ops=gunOps;gunOps=[];for(const op of ops){if(op.owner!==own())continue;
   for(const{id,g}of guns()){const q=g.snapshot();let result;if(op.action==='STOP'){if(q.continuousFire.active&&q.continuousFire.trackId===op.trackId){result=g.stopContinuousFire('OPERATOR_STOP');metrics.continuousStops++;}}
    else if(op.action==='CANCEL'){if(q.pendingSingleFire.active&&q.pendingSingleFire.trackId===op.trackId)result=g.requestFire(op.trackId,{mode:'MANUAL',ammoId:q.loadedAmmoId});}
    else{const o=mapObservedObjectsA().find(o=>trackId(o)===op.trackId&&o.kind==='TRACK'),a=gunAssessment(o),row=a.rows.find(r=>r.id===id);if(!row?.eligible){note('GUN_WITHHELD',row?.clearance.reason??a.reason,{mount:id,trackId:op.trackId});continue;}
     result=op.mode==='CONTINUOUS'?g.startContinuousFire(op.trackId,{mode:'MANUAL',ammoId:q.loadedAmmoId}):g.requestFire(op.trackId,{mode:'MANUAL',ammoId:q.loadedAmmoId});metrics.gunRequests++;if(op.mode==='CONTINUOUS'&&result.ok)metrics.continuousStarts++;
    }if(result)note('GUN_COMMAND',result.reason??null,{mount:id,trackId:op.trackId,action:op.action,ok:!!result.ok,fired:!!result.projectileId||result.fired===true,queued:!!result.queued});
   }
  }
 }
 function afterTick(){observeHp();}
 function fireState(s,m){if(!handles(s?.weapon)||!mounted)return false;const f=dom.fire;f.classList.add('map-fire-d');dom.slotDot.dataset.tone=!m||(!m.d?.o&&!m.path)?'off':m.tone??'blocked';
  if(s.weapon==='HARPOON'){f.disabled=!!hpQueue||!m?.allowed;f.textContent=hpQueue?'발사 중 '+hpQueue.released+'/'+hpQueue.count:'발사 ×'+s.count+(m?.path?' · 경로':'');}
  else{f.disabled=!m?.allowed;f.textContent=m?.queued?'요청 취소':m?.continuous?.length?'사격 중지':m?.pending?.length?'정렬 대기 '+m.holdS.toFixed(1)+'s':m?.cycleS>1e-9?m.cycleS.toFixed(1)+'s':s.fireMode==='CONTINUOUS'?'연속 사격':'발사';}
  f.title=f.disabled?textReason(m?.reason):'';return true;
 }
 function render(s,t,m,ui){
  if(!handles(s?.weapon)){if(mounted){dom.fire.classList.remove('map-fire-d');dom.routeChip.hidden=true;dom.routeActions.hidden=true;}return false;}
  if(!mounted)return false;const o=m?.d?.o??t?.last,tone=m?.tone??'blocked';if(t&&o){ui.pane.hidden=false;ui.titleText.textContent=o.label+' · '+(o.identity??'UNKNOWN');ui.tagDot.dataset.tone=tone;
   const range=Number.isFinite(m.d.rangeKm)?m.d.rangeKm.toFixed(m.d.rangeKm<10?1:0)+'km':'—';
   ui.summary.textContent=s.weapon==='HARPOON'?'RGM-84×'+s.count+' · '+(m.path?'경로':m.verdict)+' · '+(Number.isFinite(m.rangeKm)?m.rangeKm.toFixed(1)+'km':range):'5in '+[...new Set(m.rows?.filter(r=>r.eligible).map(r=>ammoNames[r.q.loadedAmmoId]))].join('/')+' · '+m.mountLabel+' · TOF'+(m.timeOfFlightS?.toFixed(0)??'—')+'s · '+range;
   ui.verdict.textContent=textReason(m.reason)||m.verdict;ui.verdict.dataset.tone=tone;ui.verdict.hidden=tone==='effective';
  }else ui.pane.hidden=true;
  dom.routeChip.hidden=s.weapon!=='HARPOON'||!!t;dom.routeActions.hidden=s.weapon!=='HARPOON'||!t;return true;
 }
 function layout(){if(!mounted)return;const s=selection(),r=harpoonRuntimeA(),z=scale(),active=harpoonRouteEditingE();dom.routeBtn.disabled=!!r.pending||!r.tubes.some(t=>t.loaded);dom.routeBtn.textContent=active?'경로 해제':'경로';dom.routeChipBtn.disabled=dom.routeBtn.disabled;dom.routeChipBtn.textContent=dom.routeBtn.textContent;
  const bar=document.getElementById('uiStatusBarA').getBoundingClientRect(),f=dom.fire.getBoundingClientRect(),c=dom.routeChip.getBoundingClientRect(),v=AEGIS_VIEWPORT.layout;dom.routeChip.style.left=Math.max(v.x+4,Math.min(v.x+v.w-c.width-4,f.x))/z+'px';dom.routeChip.style.top=Math.max(v.y+4,bar.top-c.height-14)/z+'px';
  dom.banner.hidden=!active;if(active){const view=WIP148_EXTERNAL_3D.active?window.__PIP_A__?.snapshot().visible?window.__PIP_A__.view().rect:null:AEGIS_VIEWPORT.twoD;if(view){dom.banner.style.visibility='visible';dom.banner.style.maxWidth=(view.w-8)/z+'px';dom.banner.textContent='하푼 경로 편집 중 · '+r.routeDraft.pointsM.length+'/'+HARPOON_PROFILE_A.sim.routeMaxPoints;const b=dom.banner.getBoundingClientRect();dom.banner.style.left=Math.max(view.x+4,view.cx-b.width/2)/z+'px';dom.banner.style.top=(view.y+4)/z+'px';}else dom.banner.style.visibility='hidden';}requestAnimationFrame(layout);
 }
 function draw(context,view,s,m){
  if(!handles(s?.weapon))return false;const z=mapZoom,ownship=mapOwnShipA(),limits=s.weapon==='HARPOON'?[HARPOON_PROFILE_A.sim.minLaunchRangeKm,HARPOON_PROFILE_A.sim.maxLaunchRangeKm]:guns().map(r=>r.g.spec.fireControl).length?[guns()[0].g.spec.fireControl.minRangeM/1000,guns()[0].g.spec.fireControl.maxRangeM/1000]:[0,0],color=s.weapon==='HARPOON'?'#79d7ec':'#b8d9ff';
  context.save();context.lineWidth=1/z;context.font=`${9/z}px monospace`;context.strokeStyle=context.fillStyle=color;
  for(const[km,kind]of [[limits[0],'최소'],[limits[1],'최대']]){const radius=kmToWorld(km);context.setLineDash(kind==='최소'?[]:[7/z,4/z]);context.beginPath();context.arc(ownship.x,ownship.y,radius,0,2*Math.PI);context.stroke();const center=worldToScreen(ownship.x,ownship.y,view),r=view.rect,maxPx=Math.max(Math.hypot(center.x-r.x,center.y-r.y),Math.hypot(center.x-r.x-r.w,center.y-r.y-r.h));const text=(s.weapon==='HARPOON'?'RGM-84':'5in')+' '+kind+' '+km+'km';if(radius*z<maxPx)context.fillText(text,ownship.x+radius+3/z,ownship.y+(kind==='최대'?23:11)/z);else{const p=screenToWorld(r.x+r.w-8,window.__MAP_C__.labelBase(view)+(kind==='최대'?12:0),view);context.textAlign='right';context.fillText('→ '+text,p.x,p.y);context.textAlign='left';}}
  if(s.weapon==='HARPOON'&&harpoonRuntimeA().routeDraft.pointsM.length){const p=harpoonRouteProgramE(harpoonRuntimeA().routeDraft.pointsM,{x:worldToMeters(ownship.x),y:worldToMeters(ownship.y)});if(p){const a=p.pointsM.at(-1),b=p.searchCenterM,x=metersToWorld(b.x),y=metersToWorld(b.y);context.setLineDash([3/z,3/z]);context.beginPath();context.moveTo(metersToWorld(a.x),metersToWorld(a.y));context.lineTo(x,y);context.stroke();context.setLineDash([]);context.strokeRect(x-4/z,y-4/z,8/z,8/z);context.fillText('탐색 중심',x+7/z,y-7/z);}}
  context.restore();return true;
 }
 function mount(){mounted=true;dom={chooser:document.getElementById('mapSalvoB'),fire:document.getElementById('mapFireB'),slotDot:document.querySelector('#mapFireSlotC .map-status-dot-c')};const host=document.getElementById('uiDesktopA'),pane=document.getElementById('mapEngagementB');
  const make=(tag,cls)=>{const e=document.createElement(tag);e.className=cls;return e;};dom.routeActions=make('div','map-route-actions-d');dom.routeBtn=make('button','');dom.routeBtn.id='mapRouteD';dom.routeBtn.textContent='경로';dom.routeBtn.addEventListener('click',routeToggle);dom.routeActions.append(dom.routeBtn);dom.routeActions.hidden=true;pane.append(dom.routeActions);
  dom.routeChip=make('aside','map-pane-b map-route-chip-d');dom.routeChip.id='mapRouteChipD';dom.routeChipBtn=make('button','');dom.routeChipBtn.id='mapRouteChipButtonD';dom.routeChipBtn.textContent='경로';dom.routeChipBtn.addEventListener('click',routeToggle);dom.routeChip.append(dom.routeChipBtn);dom.routeChip.hidden=true;host.append(dom.routeChip);dom.banner=make('div','map-route-banner-d');dom.banner.id='mapRouteBannerD';dom.banner.hidden=true;host.append(dom.banner);
  for(const event of['pointerdown','pointermove','pointerup','click','wheel','touchstart','touchmove','touchend','contextmenu'])dom.routeChip.addEventListener(event,e=>{e.stopPropagation();if(event==='contextmenu')e.preventDefault();},{passive:event.startsWith('touch')});
  const css=document.createElement('style');css.textContent=`#mapSalvoB.map-gun-menu-d{display:grid;grid-template-columns:repeat(2,minmax(44px,1fr));gap:8px}#mapSalvoB.map-gun-menu-d[hidden]{display:none}#mapSalvoB .map-menu-reason-d{grid-column:1/-1;font:10px/1.3 monospace;color:#ffa653;white-space:normal;max-width:200px}#mapSalvoB [aria-pressed=true]{border-color:#f7d778}.map-route-actions-d{margin-top:3px}.map-route-actions-d[hidden]{display:none}#uiDesktopA #mapEngagementB .map-route-actions-d button{height:28px;min-height:28px;min-width:36px;padding:2px 5px;font:10px/1.2 monospace}.map-route-chip-d{position:fixed;zoom:var(--ui-scale-a);padding:0;z-index:40000}.map-route-chip-d button{min-height:28px}.map-route-banner-d{position:fixed;z-index:39999;zoom:var(--ui-scale-a);font:11px/1.3 monospace;color:#ffe1ad;background:#352815e8;border:1px solid #8d6e35;padding:3px 5px;box-sizing:border-box;pointer-events:none;white-space:normal}#uiDesktopA #mapFireB.map-fire-d{font-size:10px!important}#uiDesktopA.ui-compact-a #mapFireB.map-fire-d{font-size:9px!important}`;document.head.append(css);requestAnimationFrame(layout);
  const native=simulateFixedTick;simulateFixedTick=function(dt){step();const value=native(dt);afterTick();return value;};
 }
 return Object.freeze({handles,ready,menu,highlight,selectionChanging,cancelled,chosen,calculate,render,fireState,fireClick,draw,mount,appendSearchPoint,snapshot(){const q=hpQueue;return {schema:'AEGIS_MAP_D_UI_1',queue:q?{id:q.id,count:q.count,remaining:q.remaining,released:q.released,trackId:q.trackId,path:!!q.routeProgram,routeProgram:q.routeProgram?structuredClone(q.routeProgram):null,awaiting:q.awaiting?{...q.awaiting}:null}:null,gunCommands:gunOps.map(q=>({...q})),metrics:{...metrics},log:log.map(q=>({...q})),route:{editing:harpoonRouteEditingE(),pointsM:structuredClone(harpoonRuntimeA().routeDraft.pointsM)},guns:guns().map(({id,g})=>({id,...g.snapshot()}))};}});
})();
