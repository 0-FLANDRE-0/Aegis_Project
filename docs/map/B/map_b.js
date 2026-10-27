// MAP_B: presentation state and operator command queue only. No target truth source.
function mapBObservedTrack(id){
 const t=tracks.get(Number(id));if(!t||!mapTrackVisibleA(t))return null;
 // Explicit observation/evidence whitelist. No entity/truth/object reference is copied.
 const keys=['trackId','trackUid','x','y','z','vx','vy','vz','classification','domain','classificationConfidence','classificationProbs','domainEvidence','confirmed','sensorDetected','sensorAge','sensorHits','sensorSource','memActive','reacquiring','_surfaceSensorContributorsWip13B9','_surfaceManeuverProbabilityWip13B10','_maneuverProbability','_surfaceExtentWip13B8','_surfaceExtentEstimateWip13B8','measurementSigmaM','kinematicQuality','lastUpdateSeen','ttl','isASM','_surfaceContributorsWip13B9','_surfaceMotionPriorWip13B1','_surfaceExtentWip13B1','_surfaceMotionWip13B1','trackQuality','fireControlQuality','rangeSigma','rangeSigmaM','posSigmaM','velSigmaMps','altSigmaM','azSigma','zSigma','confidence','identity','_operatorIdentity','threatStatus','engagementAuthority','_a3AuthorityReason','_a3StateRevision','_a3StateChangedStep','_lastMeasurementStep','_spyExpectedRevisitS','_lastPredictionStep','_kfStep','_kfX','_kfP','_harpoonOwnC','iffF','observationReportsC','surfaceContributorsWip13B9','surfaceMotionPriorWip13C','surfaceExtent','extent','targetSupport','bdaEvidence','identificationEvidence'];
 const out={};for(const k of keys)if(t[k]!==undefined)out[k]=structuredClone(t[k]);out.trackId=Number(id);return out;
}
function mapBNativePreview(observed,weapon,original=ACTIVE_SHIP_RUNTIME,realMode=engagementControlMode,realEmcon=emconActive){
 const ACTIVE_SHIP_RUNTIME={...original,weapons:{...original.weapons,harpoon:structuredClone(original.weapons.harpoon),vlsReleaseB2:structuredClone(original.weapons.vlsReleaseB2)},combatSystem:{...original.combatSystem,networkG:structuredClone(original.combatSystem.networkG)}};
 const tr=structuredClone(observed),tracks=new Map([[tr.trackId,tr]]),selectedLockId=tr.trackId,engagementControlMode=realMode;
 let emconActive=realEmcon;const messages=[],notify=m=>messages.push(String(m)),toggleEmcon=()=>{emconActive=!emconActive;};
 const observerC=()=>({tracks}),prepareNetworkG=r=>r.combatSystem.networkG;
 /* NATIVE_PREFLIGHT_COPIES */
 try{
  const opts={automatic:false,mode:realMode,weaponType:weapon};
  const q=vlsReleaseB2Request(weapon,opts,()=>weapon==='ESSM'?vlsReleaseEssmB1(opts):vlsReleaseStandardB1(opts));
  return q?.ok?{ok:true,reason:''}:{ok:false,reason:ACTIVE_SHIP_RUNTIME.weapons.vlsReleaseB2?.lastReject?.reason??messages.at(-1)??'RELEASE_GATE'};
 }catch(e){return {ok:false,reason:'PREVIEW_UNAVAILABLE',detail:String(e)};}
}
window.__MAP_B__=(()=>{
 const host=document.getElementById('uiDesktopA'),bar=document.getElementById('uiStatusBarA'),inv=document.getElementById('uiInventoryA');
 const labels={SM2:'SM-2MR',SM2ER:'SM-2ER',SM6:'SM-6',ESSM:'ESSM'},weapons=Object.keys(labels),byLabel=Object.fromEntries(weapons.map(k=>[labels[k],k]));
 const rows=ENVELOPE_TABLE_D.rows,altitudes=[...new Set(rows.map(r=>r.altM))].sort((a,b)=>a-b);
 const style=document.createElement('style');style.textContent=`
 #uiInventoryA{cursor:default}#uiInventoryA .map-ammo-b{background:none;color:inherit;border:1px solid transparent;border-radius:2px;padding:1px 3px;min-width:0;min-height:28px;font:inherit;position:relative}#uiInventoryA .map-ammo-b::after{content:'';position:absolute;inset:-4px 0;pointer-events:auto}#uiInventoryA .map-ammo-b:disabled{opacity:.35;cursor:default}#uiInventoryA .map-ammo-b[aria-pressed=true]{border-color:#f7d778;background:#514526}#uiInventoryA .map-ammo-b strong,#uiInventoryA .map-ammo-b span{display:block}
 .map-pane-b{position:absolute;z-index:40000;background:rgba(7,20,27,.97);border:1px solid #7a9ca5;border-radius:3px;color:#dbedf0;font:11px/1.3 monospace;padding:5px;box-sizing:border-box;max-width:calc(100vw - 8px);pointer-events:auto}.map-pane-b[hidden]{display:none}.map-pane-b button{font:11px/1.3 monospace;height:28px;min-width:36px;padding:3px 6px;color:#dbeaf0;background:#132d38;border:1px solid #47616b;position:relative}.map-pane-b button:disabled{opacity:.42}.map-pane-b button::after{content:'';position:absolute;inset:-4px 0}.map-salvo-b{display:flex;gap:8px}.map-engage-b{width:244px}.map-engage-b pre{white-space:pre-wrap;margin:3px 0}.map-engage-actions-b{display:flex;gap:8px;align-items:center;margin-top:8px}.map-engage-b .map-fire-b{height:40px;min-width:66px;background:#653021}.map-reason-b{color:#f6c896;margin:4px 0}.map-verdict-b{font-weight:bold}.map-verdict-b[data-tone=effective]{color:#82e6a1}.map-verdict-b[data-tone=warning]{color:#ffa653}.map-verdict-b[data-tone=blocked]{color:#ff7979}.map-engage-b header{font-weight:bold;margin-bottom:4px}
 `;document.head.append(style);
 const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;};
 const chooser=el('aside','map-pane-b map-salvo-b');chooser.id='mapSalvoB';chooser.hidden=true;chooser.setAttribute('aria-label','발수 선택');
 const pane=el('aside','map-pane-b map-engage-b');pane.id='mapEngagementB';pane.hidden=true;pane.setAttribute('aria-label','표적 교전');
 const title=el('header'),summary=el('pre'),verdict=el('div','map-verdict-b'),reason=el('div','map-reason-b'),buttons=el('div','map-engage-actions-b'),fire=el('button','map-fire-b','발사'),cancel=el('button','','취소');fire.id='mapFireB';fire.disabled=true;cancel.id='mapCancelB';buttons.append(fire,cancel);pane.append(title,summary,verdict,reason,buttons);host.append(chooser,pane);
 for(const e of[chooser,pane])for(const event of['pointerdown','pointermove','pointerup','click','dblclick','wheel','touchstart','touchmove','touchend','contextmenu'])e.addEventListener(event,q=>{q.stopPropagation();if(event==='contextmenu')q.preventDefault();},{passive:event.startsWith('touch')});
 let selection=null,pending=null,target=null,model=null,queue=null,lastAt=-Infinity,refreshing=false,receipts=[],revision=0;
 const metrics={draws:{MAIN:0,PIP:0},salvos:0,shots:0,lastNativePreview:null};
 const scale=()=>window.__UI_A_SETTINGS__?.scale??1;
 function visibleRect(){return WIP148_EXTERNAL_3D.active?AEGIS_VIEWPORT.threeD:AEGIS_VIEWPORT.twoD;}
 function place(e,x,y){const r=visibleRect(),s=scale(),b=e.getBoundingClientRect();e.style.left=(Math.max(r.x+3,Math.min(r.x+r.w-b.width-3,x)))/s+'px';e.style.top=(Math.max(r.y+3,Math.min(r.y+r.h-b.height-3,y)))/s+'px';}
 function availability(w){return wip14a14VlsAvailability()[w];}
 function ready(w){const a=availability(w);return typeof a==='number'?a:Number(a?.ready??a?.available??a?.count??0);}
 function repaint(){revision++;window.__PIP_A__?.invalidate();lastAt=-Infinity;refresh();}
 function highlight(){for(const e of inv.querySelectorAll('[data-weapon-b]')){const w=e.dataset.weaponB;e.setAttribute('aria-pressed',String(selection?.weapon===w));e.title=labels[w]+(selection?.weapon===w?' · '+selection.count+'발 선택':' · 발수 선택');const n=e.querySelector('span');if(n)n.textContent=labels[w]+(selection?.weapon===w?' ×'+selection.count:'');e.disabled=ready(w)<=0;}if(pending)for(const b of chooser.querySelectorAll('[data-salvo-b]'))b.disabled=ready(pending)<Number(b.dataset.salvoB);}
 function inventoryRendered(){for(const e of [...inv.children]){const name=e.querySelector('span')?.textContent,w=byLabel[name];if(!w)continue;let b=e;if(e.tagName!=='BUTTON'){b=el('button','ui-ammo-a map-ammo-b');b.type='button';while(e.firstChild)b.append(e.firstChild);e.replaceWith(b);}b.dataset.weaponB=w;b.setAttribute('aria-label',labels[w]+' 발수 선택');}highlight();}
 function clear(){selection=null;target=null;model=null;pending=null;chooser.hidden=pane.hidden=true;window.__MAP_A__?.setFiringTarget(null);highlight();repaint();}
 function countMenu(w,anchor){pending=w;chooser.replaceChildren();for(let n=1;n<=4;n++){const b=el('button','',n===1?'단발':n+'발');b.dataset.salvoB=n;b.disabled=ready(w)<n;b.title=b.disabled?'준비 탄 부족':'';b.addEventListener('click',()=>{if(ready(w)<n)return;selection={weapon:w,count:n};pending=null;chooser.hidden=true;highlight();repaint();});chooser.append(b);}chooser.hidden=false;const a=anchor.getBoundingClientRect();place(chooser,a.left,a.top-chooser.getBoundingClientRect().height-5);}
 inv.addEventListener('click',e=>{const b=e.target.closest('[data-weapon-b]');if(b){e.stopPropagation();if(b.disabled)return;if(selection?.weapon===b.dataset.weaponB){clear();return;}countMenu(b.dataset.weaponB,b);return;}if(e.target===inv)clear();else{window.__UI_A__.open('ARM');setControlDeckTabWip13C('ARM');}});
 bar.addEventListener('click',e=>{if(e.target===bar||e.target.classList.contains('ui-bar-overview-a')||e.target.classList.contains('ui-bar-command-a'))clear();});
 document.addEventListener('pointerdown',e=>{if(!chooser.hidden&&!chooser.contains(e.target)&&!inv.contains(e.target)){chooser.hidden=true;pending=null;}},{capture:true});
 function choose(o,surface='MAIN'){if(!selection||!['TRACK','NET','ESM'].includes(o.kind))return false;target={key:o.key,kind:o.kind,id:o.id,associatedTrackId:o.associatedTrackId,surface,last:{...o}};window.__MAP_A__.setFiringTarget(o.key);pane.hidden=false;repaint();return true;}
 function cancelTarget(){target=null;model=null;pane.hidden=true;window.__MAP_A__.setFiringTarget(null);repaint();}
 cancel.addEventListener('click',cancelTarget);
 function trackView(){if(!target)return null;const o=mapObservedObjectsA().find(o=>o.key===target.key);if(!o)return {...target.last,lost:true};target.last={...o};return o;}
 function dataFor(o){if(!o||o.lost)return {o,lost:true};if(o.kind==='ESM')return {o,position:false};const id=o.kind==='TRACK'?o.id:o.associatedTrackId,tr=id!=null?mapBObservedTrack(id):null;
  // A received network estimate may draw an envelope, but is never made into
  // a local fire-control track. NO_TRACK keeps the native release authority.
  const report=!tr&&o.kind==='NET'?networkPictureG(ACTIVE_SHIP_RUNTIME).find(q=>q.id===o.id):null;
  const v=report?.velocityMps,received=v?{x:o.x,y:o.y,z:o.z,vx:mpsToWorldSpeed(v.x),vy:mpsToWorldSpeed(v.y),vz:v.z}:null;
  const estimate=tr??received;if(!estimate)return {o,position:Number.isFinite(o.x)&&Number.isFinite(o.y),reason:'NO_TRACK',velocity:false};
  const s=wip118TrackStateSI(estimate),position=Number.isFinite(s.x)&&Number.isFinite(s.y),velocity=Number.isFinite(estimate.vx)&&Number.isFinite(estimate.vy);
  const own=mapOwnShipA(),dx=s.x-worldToMeters(own.x),dy=s.y-worldToMeters(own.y),rangeM=Math.hypot(dx,dy),ux=rangeM?dx/rangeM:1,uy=rangeM?dy/rangeM:0;
  const source=String(tr?.sensorSource??'NETWORK'),twoD=/^(SPQ|BRIDGE|SPS73|APS153|OFFBOARD_C)/.test(source)&&!String(tr?.sensorSource).includes('SPY');
  const altitudeKnown=!!tr&&Number.isFinite(tr.z)&&!twoD;
  return {o,tr,forecastTrack:estimate,reason:tr?null:'NO_TRACK',id:id==null?null:Number(id),position,velocity,altitudeKnown,altM:s.z,rangeKm:rangeM/1000,closingMps:-(s.vx*ux+s.vy*uy),crossMps:Math.abs(-s.vx*uy+s.vy*ux),speedMps:Math.hypot(s.vx,s.vy),headingDeg:Math.hypot(s.vx,s.vy)>0?(Math.atan2(s.vy,s.vx)*180/Math.PI+450)%360:null};
 }
 function lookup(d,w){const pool=rows.filter(r=>r.weapon===w),motions=[...new Map(pool.map(r=>[r.motion,{motion:r.motion,closing:r.targetSpeedMps,cross:r.crossSpeedMps??0}])).values()];
  const mv=motions.reduce((a,b)=>Math.hypot(d.closingMps-b.closing,d.crossMps-b.cross)<Math.hypot(d.closingMps-a.closing,d.crossMps-a.cross)?b:a),p=pool.filter(r=>r.motion===mv.motion);
  const r=d.altitudeKnown?p.reduce((a,b)=>Math.abs(b.altM-d.altM)<Math.abs(a.altM-d.altM)?b:a):p.reduce((a,b)=>b.effectiveMaxKm<a.effectiveMaxKm?b:a);
  const estimated=Math.hypot(shipNav.vx??0,shipNav.vy??0)>0||!d.altitudeKnown||d.altM!==r.altM||Math.abs(d.closingMps-mv.closing)>1e-6||Math.abs(d.crossMps-mv.cross)>1e-6;
  return {row:r,estimated,altitudeUnknown:!d.altitudeKnown};
 }
 function nativeReason(d){if(!d.tr)return {ok:false,reason:d.reason??'위치 정보 없음'};if(wip125PreSailOpen)return {ok:false,reason:'출항 전'};if(emconActive)return {ok:false,reason:'EMCON 중 — 발사 불가'};if(ready(selection.weapon)<selection.count)return {ok:false,reason:'선택 발수 대비 준비 탄 부족'};
  if(engagementControlMode==='SEMIAUTO'){const status=(wip119AutonomyState.candidateRows??[]).find(s=>s.row?.trackId===d.id);if(!status?.ready||status.row.weapon!==selection.weapon)return {ok:false,reason:'SEMIAUTO · 선택 표적/무장 추천 없음'};}
  const q=mapBNativePreview(d.tr,selection.weapon);metrics.lastNativePreview=q;return q;
 }
 function classify(range,row){if(range>row.maxRangeKm)return '사거리 밖';if((row.deadZones??[]).some(z=>range>=z.startKm&&range<=z.endKm))return '사각지대';if(range<row.effectiveMinKm)return '최소 사거리 안쪽';if(range<=row.effectiveMaxKm)return '유효';return '최대 사거리 구간';}
 function calculate(){if(!selection)return null;if(!target)return {initial:true,sets:[{row:rows.find(r=>r.weapon===selection.weapon&&r.altM===30&&r.motion==='STATIONARY'),name:'저고도',dash:[3,4],color:'#79d7ec'},{row:rows.find(r=>r.weapon===selection.weapon&&r.altM===15000&&r.motion==='STATIONARY'),name:'고고도',dash:[11,5],color:'#ead18b'}]};
  const d=dataFor(trackView());if(d.lost)return {d,verdict:'판정 불가',reason:'트랙 소실',allowed:false};if(!d.position)return {d,verdict:'판정 불가',reason:'위치 정보 없음',allowed:false,initial:true};if(!d.velocity)return {d,verdict:'판정 불가',reason:d.reason??'속도 정보 없음',allowed:false};
  const q=lookup(d,selection.weapon),v=classify(d.rangeKm,q.row),gate=nativeReason(d),belowEffective=d.rangeKm<q.row.effectiveMinKm,allowed=gate.ok&&v!=='사거리 밖';
  const profile=wip119WeaponDescriptor(selection.weapon)?.profile,th={id:d.id,tr:d.forecastTrack??d.tr,dKm:d.rangeKm,vr:d.closingMps*3.6,alt:d.altM};let prediction=null;
  if(profile){const t=hardKillKinematicInterceptEstimate(th,profile).interceptS,f=wip118FutureThreat(th,t,wip118TrackAcceleration(d.id));prediction={x:f.tr.x,y:f.tr.y,timeS:t};}
  return {d,...q,verdict:v,gate,allowed,prediction,reason:!gate.ok?gate.reason:belowEffective?'측정 유효구간 미만 · 기존 발사 관문 통과':v==='사거리 밖'?'내장 최대 사거리 초과':v==='사각지대'?'측정 실패 구간':v==='유효'?'내장 유효 구간 · 정식 VLS 관문 통과':'최대 사거리 안 · 3/5 기준 밖'};
 }
 function refresh(force=false){const now=performance.now();if(refreshing||(!force&&now-lastAt<125))return;refreshing=true;try{lastAt=now;model=calculate();highlight();if(target&&selection){pane.hidden=false;const d=model.d,o=d.o??target.last;title.textContent=o.label+' · '+(o.identity??'UNKNOWN');summary.textContent=model.reason==='트랙 소실'?'트랙 소실':o.kind==='ESM'?'방위 보고 · 위치 정보 없음':`${d.altitudeKnown?Math.round(d.altM)+'m':'고도 미상'} · ${Number.isFinite(d.speedMps)?d.speedMps.toFixed(0)+'m/s':'속도 미상'} · ${Number.isFinite(d.headingDeg)?d.headingDeg.toFixed(0)+'°':d.speedMps===0?'정지':'침로 미상'}\n${labels[selection.weapon]} ×${selection.count}${model.row?' · 표 '+model.row.altM+'m / '+model.row.motion:''}`;
   const displayed=({'사각지대':'사각지대 · 명중 확률 낮음','최대 사거리 구간':'최대 사거리 · 명중 확률 낮음','최소 사거리 안쪽':'최소 유효거리 안쪽 · 명중 확률 낮음'})[model.verdict]??model.verdict;verdict.textContent=displayed+(model.estimated?' · 추정':'')+(model.altitudeUnknown?' · 고도 미상':'');verdict.dataset.tone=!model.allowed?'blocked':model.verdict==='유효'?'effective':'warning';reason.textContent=queue?'연속 발사 중 · 남은 '+queue.remaining+'발':model.reason;fire.disabled=!model.allowed||!!queue;fire.title=fire.disabled?reason.textContent:'';positionPane();}
 }finally{refreshing=false;}}
 function currentView(){return target?.surface==='PIP'&&WIP148_EXTERNAL_3D.active?window.__PIP_A__.view():{target:'MAIN',rect:AEGIS_VIEWPORT.twoD,km:tacticalViewKm,center:{x:aircraft.x()+camOffset.x,y:aircraft.y()+camOffset.y}};}
 function positionPane(){if(!target||pane.hidden)return;const o=model?.d?.o??target.last,v=currentView(),p=Number.isFinite(o.x)?worldToScreen(o.x,o.y,v):{x:v.rect.cx,y:v.rect.cy};let x=p.x+25;const r=pane.getBoundingClientRect();if(x+r.width>visibleRect().x+visibleRect().w)x=p.x-25-r.width;place(pane,x,p.y+18);}
 function stepCommands(){if(!queue)return;if(queue.owner!==ACTIVE_SHIP_RUNTIME.entityId||simStepCounter<queue.lastStep){queue=null;repaint();return;}if(!vlsReleaseB2Snapshot().ready)return;
  const q=queue,d=dataFor(mapObservedObjectsA().find(o=>o.key===q.key)??{...q.last,lost:true});const chosen=selection;selection={weapon:q.weapon,count:1};let p;try{const evalRow=d.position&&d.velocity?lookup(d,q.weapon):null;p=d.lost?{ok:false,reason:'트랙 소실'}:!evalRow?{ok:false,reason:'관측 불충분'}:classify(d.rangeKm,evalRow.row)==='사거리 밖'?{ok:false,reason:'사거리 관문'}:nativeReason(d);}finally{selection=chosen;}
  if(!p.ok){receipts.push({step:simStepCounter,weapon:q.weapon,trackId:d.id,rejected:p.reason,remaining:q.remaining});queue=null;repaint();return;}
  // Deliberate operator FIRE command only. Existing native VLS entry/cadence/authority run again.
  selectedLockId=d.id;wip13cSelectVlsWeapon(q.weapon);
  // UI selection guard: never let a freshly rebuilt SEMIAUTO recommendation
  // substitute another weapon/track. All accepted requests still run the exact native gate.
  const nativeRequest=vlsReleaseB2Request;let substituted=false,result;
  vlsReleaseB2Request=function(w,opts,release){if(w!==q.weapon||selectedLockId!==d.id){substituted=true;return null;}return nativeRequest(w,opts,release);};
  try{result=wip13cFireSelectedVlsWeapon();}finally{vlsReleaseB2Request=nativeRequest;}
  if(substituted)result={launched:false,reason:'RECOMMENDATION_CHANGED'};
  receipts.push({step:simStepCounter,weapon:q.weapon,trackId:d.id,launched:!!result?.launched||!!result?.ok,reason:result?.reason??null});if(receipts.length>64)receipts.shift();
  const launched=!!result?.launched||!!result?.ok;if(launched){metrics.shots++;q.remaining--;q.lastStep=simStepCounter;}if(!launched||q.remaining<=0)queue=null;repaint();
 }
 fire.addEventListener('click',()=>{refresh(true);if(!model?.allowed||queue)return;metrics.salvos++;queue={...selection,remaining:selection.count,key:target.key,last:{...target.last},owner:ACTIVE_SHIP_RUNTIME.entityId,lastStep:simStepCounter};stepCommands();});
 function draw(context,view){if(!selection||!model)return;const z=mapZoom,own=mapOwnShipA(),r=view.rect,origin=worldToScreen(own.x,own.y,view),maxPx=Math.max(Math.hypot(origin.x-r.x,origin.y-r.y),Math.hypot(origin.x-r.x-r.w,origin.y-r.y-r.h),Math.hypot(origin.x-r.x-r.w,origin.y-r.y),Math.hypot(origin.x-r.x,origin.y-r.y-r.h));metrics.draws[view.target??'MAIN']++;
  const initial=()=>[{row:rows.find(q=>q.weapon===selection.weapon&&q.altM===30&&q.motion==='STATIONARY'),name:'저고도',dash:[3,4],color:'#79d7ec'},{row:rows.find(q=>q.weapon===selection.weapon&&q.altM===15000&&q.motion==='STATIONARY'),name:'고고도',dash:[11,5],color:'#ead18b'}];
  const sets=model.row?[{row:model.row,name:'표적'+(model.estimated?' · 추정':''),dash:[7,4],color:'#f4cc7c'}]:model.initial?(model.sets??initial()):[];
  context.save();context.lineWidth=1/z;context.font=`${11/z}px monospace`;
  for(const s of sets){if(!s.row)continue;const a=s.row,min=kmToWorld(a.effectiveMinKm),max=kmToWorld(a.effectiveMaxKm);context.strokeStyle=s.color;context.fillStyle=s.color+'0c';context.beginPath();context.arc(own.x,own.y,max,0,2*Math.PI);context.arc(own.x,own.y,min,0,2*Math.PI,true);context.fill('evenodd');
   for(const [km,kind]of [[a.effectiveMinKm,'최소'],[a.effectiveMaxKm,'유효'],[a.maxRangeKm,'최대']]){const radius=kmToWorld(km),px=radius*z;context.strokeStyle=s.color;context.setLineDash(kind==='최소'?[]:s.dash.map(n=>n/z));context.beginPath();context.arc(own.x,own.y,radius,0,2*Math.PI);context.stroke();context.fillStyle=s.color;const t=`${s.name} ${kind} ${km}km`;if(px<maxPx){context.fillText(t,own.x+radius+3/z,own.y+(s.name==='고고도'?-4:11)/z);}else{const y=r.y+16+(s.name==='고고도'?42:0)+(['최소','유효','최대'].indexOf(kind)*12),p=screenToWorld(r.x+r.w-8,y,view);context.textAlign='right';context.fillText('→ '+t,p.x,p.y);context.textAlign='left';}}
   if(model.row)for(const dz of a.deadZones??[]){const lo=kmToWorld(dz.startKm),hi=kmToWorld(dz.endKm);context.save();context.beginPath();context.arc(own.x,own.y,hi,0,2*Math.PI);context.arc(own.x,own.y,lo,0,2*Math.PI,true);context.clip('evenodd');context.strokeStyle='#f6b18e88';context.setLineDash([]);const left=screenToWorld(r.x,r.y,view),right=screenToWorld(r.x+r.w,r.y+r.h,view),span=right.y-left.y;for(let x=left.x-span;x<right.x+span;x+=8/z){context.beginPath();context.moveTo(x,left.y);context.lineTo(x+span,right.y);context.stroke();}context.restore();}
  }
  if(model.prediction&&model.d?.o){const p=model.prediction,o=model.d.o;context.strokeStyle='#fff0a5';context.setLineDash([4/z,3/z]);context.beginPath();context.moveTo(o.x,o.y);context.lineTo(p.x,p.y);context.stroke();context.setLineDash([]);context.strokeRect(p.x-4/z,p.y-4/z,8/z,8/z);context.fillStyle='#fff0a5';context.fillText('사통 예측 '+p.timeS.toFixed(0)+'s',p.x+7/z,p.y-7/z);}
  context.restore();
 }
 // The old quick widget is explicitly retired. ARM/SYS native controls stay intact.
 document.getElementById('wip14a14QuickEngage3D')?.remove();
 const nativeTick=simulateFixedTick;simulateFixedTick=function(dt){const result=nativeTick(dt);stepCommands();return result;};
 function frame(){refresh();positionPane();requestAnimationFrame(frame);}requestAnimationFrame(frame);inventoryRendered();
 return Object.freeze({pickObject:choose,inventoryRendered,draw,refresh,revision:()=>revision,snapshot(){return {schema:'AEGIS_MAP_B_UI_1',selection:selection?{...selection}:null,pending,target:target?{key:target.key,surface:target.surface}:null,model:model?{initial:!!model.initial,verdict:model.verdict,reason:model.reason,allowed:!!model.allowed,estimated:model.estimated,altitudeUnknown:model.altitudeUnknown,cellId:model.row?.cellId,rangeKm:model.d?.rangeKm,row:model.row?{maxRangeKm:model.row.maxRangeKm,effectiveMinKm:model.row.effectiveMinKm,effectiveMaxKm:model.row.effectiveMaxKm,deadZones:model.row.deadZones}:null,prediction:model.prediction}:null,queue:queue?{weapon:queue.weapon,remaining:queue.remaining}:null,receipts:receipts.map(q=>({...q})),metrics:structuredClone(metrics)};}});
})();
